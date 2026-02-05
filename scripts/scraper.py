import argparse
import asyncio
import hashlib
import json
import logging
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urljoin

import httpx
from bs4 import BeautifulSoup

BASE_URL = "https://maimai.sega.jp/"


@dataclass(frozen=True)
class ScraperConfig:
    base_url: str = BASE_URL
    raw_data_dir: Path = Path("../raw_data")
    images_dir: Path = Path("../docs/src/images")
    concurrency: int = 32
    area_index_path: Path = Path("../docs/public/area_index.json")
    only_new: bool = False


class AreaScraper:
    def __init__(self, config: ScraperConfig) -> None:
        self.config = config
        self.semaphore = asyncio.Semaphore(config.concurrency)

    def _hash_key(self, path: Path, base_dir: Path) -> str:
        try:
            return str(path.relative_to(base_dir))
        except ValueError:
            return str(path)

    def _hash_bytes(self, data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    def _hash_file(self, path: Path) -> str:
        return self._hash_bytes(path.read_bytes())

    def _load_hashes(self, path: Path) -> dict[str, str]:
        if not path.exists():
            return {}
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            logging.warning("Hash file is invalid JSON: %s", path)
            return {}
        if not isinstance(data, dict):
            logging.warning("Hash file is not an object: %s", path)
            return {}
        return {str(k): str(v) for k, v in data.items()}

    def _save_hashes(self, path: Path, hashes: dict[str, str]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(dict(sorted(hashes.items())), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def _get_cached_hash(self, hashes: dict[str, str], key: str, path: Path) -> str | None:
        cached = hashes.get(key)
        if cached is None and path.exists():
            cached = self._hash_file(path)
            hashes[key] = cached
        return cached

    def _log_update_list(self, updated_files: list[Path]) -> None:
        if not updated_files:
            logging.info("No files updated.")
            return
        logging.info("Updated files:")
        for path in sorted(set(updated_files), key=lambda p: str(p)):
            logging.info("  %s | updated", path)

    def find_js_files(self, url: str) -> list[str]:
        response = httpx.get(url, follow_redirects=True)
        if response.status_code != 200:
            logging.error("Fetch failed: %s (status=%s)", url, response.status_code)
            return []

        soup = BeautifulSoup(response.text, "html.parser")
        js_pattern = re.compile(r".*/area(-\w+)?\.js(\?.*)?$")
        found_scripts: list[str] = []
        for script in soup.find_all("script"):
            src = script.get("src")
            if src and js_pattern.match(src):
                full_url = urljoin(url, src)
                found_scripts.append(src)
                logging.info("Found script: %s", full_url)
        return found_scripts

    def parse_area_json_urls(self, js_content: str, js_file_name: str) -> tuple[str, list[str]]:
        list_pattern = re.compile(r"\w+\s*=\s*\[(.*?)\]")
        list_match = list_pattern.search(js_content)
        if not list_match:
            logging.warning("No list definition in %s", js_file_name)
            return ("unknown", [])
        raw_content = list_match.group(1)
        items = re.findall(r"['\"](.*?)['\"]", raw_content)
        logging.info("List items: %s", items)

        url_pattern = re.compile(
            r"Zero\.fetch\.get\(\s*['\"](.*?)['\"]\s*\+\s*.*?\+\s*['\"](.*?)['\"]"
        )
        url_match = url_pattern.search(js_content)
        if not url_match:
            logging.warning("No json pattern string found in %s", js_file_name)
            return ("unknown", [])

        prefix = url_match.group(1)
        suffix = url_match.group(2)
        logging.info("Template: %s %s", prefix, suffix)

        clean_prefix = prefix.replace("~", "")
        full_urls = [
            urljoin(self.config.base_url, f"{clean_prefix}{item}{suffix}")
            for item in items
        ]
        for url in full_urls:
            logging.info("JSON URL: %s", url)
        version_match = re.search(r"/data/([^/]+)Area/", clean_prefix)
        version_name = version_match.group(1) if version_match else "unknown"
        return (version_name, full_urls)

    async def fetch_and_save_json(
        self,
        client: httpx.AsyncClient,
        url: str,
        directory: Path,
    ) -> None:
        try:
            filename = url.split("/")[-1]
            response = await client.get(url)
            if response.status_code == 200:
                file_path = directory / filename
                file_path.write_bytes(response.content)
                logging.info("Saved: %s", file_path)
            else:
                logging.error("Download error: %s (status=%s)", url, response.status_code)
        except Exception as exc:
            logging.exception("Error fetching %s: %s", url, exc)

    async def fetch_bytes(self, client: httpx.AsyncClient, url: str) -> bytes | None:
        try:
            response = await client.get(url)
            if response.status_code == 200:
                return response.content
            logging.error("Download error: %s (status=%s)", url, response.status_code)
        except Exception as exc:
            logging.exception("Error fetching %s: %s", url, exc)
        return None

    def get_json(self, url: str) -> list[dict]:
        response = httpx.get(url)
        if response.status_code != 200:
            logging.error("Fetch JSON failed: %s (status=%s)", url, response.status_code)
            return []
        return response.json()

    async def get_image(self, client: httpx.AsyncClient, url: str) -> bytes | None:
        response = await client.get(url)
        if response.status_code != 200:
            logging.error("Image fetch failed: %s (status=%s)", url, response.status_code)
            return None
        return response.content

    async def download_image(
        self,
        client: httpx.AsyncClient,
        output_path: Path,
        url: str,
        hashes: dict[str, str],
        base_dir: Path,
    ) -> None:
        async with self.semaphore:
            img_data = await self.get_image(client, url)
            if img_data:
                key = self._hash_key(output_path, base_dir)
                new_hash = self._hash_bytes(img_data)
                existing_hash = self._get_cached_hash(hashes, key, output_path)
                if existing_hash == new_hash:
                    logging.info("Unchanged: %s", output_path)
                    return
                output_path.write_bytes(img_data)
                hashes[key] = new_hash
                logging.info("Saved: %s", output_path)
            else:
                logging.error("Image download error: %s", url)

    async def download_jsons(self, json_urls: list[str]) -> list[Path]:
        save_dir = self.config.raw_data_dir
        save_dir.mkdir(exist_ok=True)
        hashes_path = save_dir / ".hashes.json"
        hashes = self._load_hashes(hashes_path)
        hashes_dirty = False
        if self.config.only_new:
            pending_urls = []
            for json_url in json_urls:
                filename = json_url.split("/")[-1]
                file_path = save_dir / filename
                if file_path.exists():
                    logging.info("Skip existing: %s", file_path)
                    continue
                pending_urls.append(json_url)
            json_urls = pending_urls
            if json_urls:
                new_files = [save_dir / url.split("/")[-1] for url in json_urls]
                logging.info("New json files (%s):", len(new_files))
                for file_path in new_files:
                    logging.info("  %s", file_path)
            else:
                logging.info("No new json files to download.")
        if not json_urls:
            return []
        async with httpx.AsyncClient() as client:
            tasks = [self.fetch_bytes(client, json_url) for json_url in json_urls]
            results = await asyncio.gather(*tasks)

        updated_files: list[Path] = []
        for json_url, content in zip(json_urls, results, strict=False):
            if content is None:
                continue
            filename = json_url.split("/")[-1]
            file_path = save_dir / filename
            if self.config.only_new and file_path.exists():
                logging.info("Skip existing: %s", file_path)
                continue
            key = self._hash_key(file_path, save_dir)
            new_hash = self._hash_bytes(content)
            existing_hash = self._get_cached_hash(hashes, key, file_path)
            if not self.config.only_new and existing_hash == new_hash:
                logging.info("Unchanged: %s", file_path)
                continue
            file_path.write_bytes(content)
            hashes[key] = new_hash
            hashes_dirty = True
            updated_files.append(file_path)
            logging.info("Saved: %s", file_path)

        if hashes_dirty:
            self._save_hashes(hashes_path, hashes)
        return updated_files

    def build_unified_index(self, version_names: list[str], *, write_output: bool = True) -> list[dict]:
        url = urljoin(self.config.base_url, "./data/")
        all_areas: list[dict] = []
        for version_name in version_names:
            site_url = urljoin(url, f"./{version_name}Area/index.json")
            items = self.get_json(site_url)
            for item in items:
                clean_item = {
                    "id": item["id"],
                    "text": item["text"],
                    "version": version_name,
                }
                all_areas.append(clean_item)
                logging.info("Index item: %s", clean_item)

        if write_output:
            output_file = self.config.raw_data_dir / "area_index.json"
            output_file.write_text(
                json.dumps(all_areas, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
        return all_areas

    def merge_area_index(self, entries: list[dict]) -> bool:
        index_path = self.config.area_index_path
        index_path.parent.mkdir(parents=True, exist_ok=True)
        if index_path.exists():
            existing = json.loads(index_path.read_text(encoding="utf-8"))
        else:
            existing = []
        merged = {}
        for item in existing + entries:
            if not isinstance(item, dict):
                continue
            area_id = item.get("id")
            version = item.get("version")
            if not area_id or not version:
                continue
            merged[f"{area_id}:{version}"] = { # A key designed to merge
                "id": area_id,
                "text": item.get("text", ""),
                "version": version,
            }
        merged_list = sorted(merged.values(), key=lambda x: (x["id"], x["version"]))
        new_content = json.dumps(merged_list, ensure_ascii=False, indent=2)
        if index_path.exists():
            current = index_path.read_text(encoding="utf-8")
            if current == new_content:
                return False
        index_path.write_text(new_content, encoding="utf-8")
        return True

    def build_phase1_index_entries(
        self,
        version_name: str,
        json_sources: list[Path | str],
    ) -> list[dict]:
        entries: list[dict] = []
        for source in json_sources:
            if isinstance(source, Path):
                file_path = source
            else:
                filename = source.split("/")[-1]
                file_path = self.config.raw_data_dir / filename
            if not file_path.exists():
                continue
            area = json.loads(file_path.read_text(encoding="utf-8"))
            area_id = area.get("id", "")
            area_name = area.get("name", "")
            if not area_id:
                continue
            entries.append(
                {
                    "id": area_id,
                    "text": area_name,
                    "version": version_name,
                }
            )
        return entries

    def fetch_begin_page(self) -> None:
        url = "https://maimai.sega.jp/area/hapifes/story/"
        response = httpx.get(url)
        logging.info("Begin page length: %s", len(response.text))

    async def fetch_data_phase1(self) -> None:
        version_list = ["", "./prismplus/", "./prism/", "./buddiesplus/", "./buddies/"]
        area_url = urljoin(self.config.base_url, "./area/")
        version_urls = [urljoin(area_url, version) for version in version_list]
        updated_files: list[Path] = []
        for version_url in version_urls:
            logging.info("Scanning: %s", version_url)
            js_filenames = self.find_js_files(version_url)
            if not js_filenames:
                logging.warning("No JS files found: %s", version_url)
                continue
            for js_filename in js_filenames:
                full_url = urljoin(version_url, js_filename)
                logging.info("Fetching script: %s", full_url)
                js_content = httpx.get(full_url).text
                version_name, json_urls = self.parse_area_json_urls(js_content, js_filename)
                updated_jsons = await self.download_jsons(json_urls)
                updated_files.extend(updated_jsons)
                if updated_jsons:
                    entries = self.build_phase1_index_entries(version_name, updated_jsons)
                    if entries:
                        if self.merge_area_index(entries):
                            updated_files.append(self.config.area_index_path)
        if not self.config.only_new:
            self._log_update_list(updated_files)

    async def fetch_data_phase2(self) -> None:
        version_name_list = [
            "festivalplus",
            "festival",
            "universeplus",
            "universe",
            "splashplus",
            "splash",
        ]
        updated_files: list[Path] = []
        all_areas = self.build_unified_index(
            version_name_list,
            write_output=not self.config.only_new,
        )
        if self.config.only_new:
            new_entries = [
                area
                for area in all_areas
                if not (self.config.raw_data_dir / f"{area['id']}.json").exists()
            ]
            if new_entries:
                if self.merge_area_index(new_entries):
                    updated_files.append(self.config.area_index_path)
            json_urls = [
                f"https://maimai.sega.jp/data/{area['version']}Area/{area['id']}.json"
                for area in new_entries
            ]
            updated_files.extend(await self.download_jsons(json_urls))
            return

        if self.merge_area_index(all_areas):
            updated_files.append(self.config.area_index_path)
        json_urls = [
            f"https://maimai.sega.jp/data/{area['version']}Area/{area['id']}.json"
            for area in all_areas
        ]
        updated_files.extend(await self.download_jsons(json_urls))
        self._log_update_list(updated_files)

    async def fetch_images(self) -> None:
        base_dir = self.config.images_dir
        hashes_path = base_dir / ".hashes.json"
        hashes = self._load_hashes(hashes_path)
        urls: list[tuple[Path, str]] = []
        for json_file in self.config.raw_data_dir.rglob("*.json"):
            area = json.loads(json_file.read_text(encoding="utf-8"))
            area_id = area["id"]
            logging.info("Area: %s", area_id)
            area_dir = base_dir / area_id
            area_dir.mkdir(parents=True, exist_ok=True)

            area_url = urljoin(self.config.base_url, f"./storage/area/region/{area_id}/")
            urls.append((area_dir / "soukanzu.png", urljoin(area_url, "./pc/soukanzu.png")))

            for char in area.get("characters", []):
                img_url = urljoin(area_url, f"./icon/{char['img']}.png")
                output_dir = area_dir / f"{char['img']}.png"
                urls.append((output_dir, img_url))

            for song in area.get("songs", []):
                thumbnail = song["thumbnail"]
                img_url = urljoin(area_url, f"./jacket/{thumbnail}.png")
                output_dir = area_dir / f"{thumbnail}.png"
                urls.append((output_dir, img_url))

        async with httpx.AsyncClient() as client:
            tasks = [
                self.download_image(client, path, url, hashes, base_dir)
                for (path, url) in urls
            ]
            await asyncio.gather(*tasks)
        self._save_hashes(hashes_path, hashes)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="maimai area data scraper")
    parser.add_argument(
        "task",
        choices=["phase1", "phase2", "images", "begin"],
        help="Which task to run",
    )
    parser.add_argument("--raw-data-dir", default="../raw_data")
    parser.add_argument("--images-dir", default="../docs/src/images")
    parser.add_argument("--concurrency", type=int, default=32)
    parser.add_argument("--log-level", default="INFO")
    parser.add_argument(
        "--only-new",
        action="store_true",
        help="Only download new json files; do not overwrite existing ones",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(levelname)s: %(message)s")
    # logging.getLogger().setLevel(logging.WARNING)

    config = ScraperConfig(
        raw_data_dir=Path(args.raw_data_dir),
        images_dir=Path(args.images_dir),
        concurrency=args.concurrency,
        only_new=args.only_new,
    )
    scraper = AreaScraper(config)

    if args.task == "begin":
        scraper.fetch_begin_page()
        return

    if args.task == "phase1":
        asyncio.run(scraper.fetch_data_phase1())
        return

    if args.task == "phase2":
        asyncio.run(scraper.fetch_data_phase2())
        return

    if args.task == "images":
        asyncio.run(scraper.fetch_images())
        return


if __name__ == "__main__":
    main()
# import httpx
# import re
# import json
# import asyncio
# from pathlib import Path
# from bs4 import BeautifulSoup
# from urllib.parse import urljoin

# semaphore = asyncio.Semaphore(32)
# BASE_URL = "https://maimai.sega.jp/"

# def find_js_files(url): # filename_list
#     response = httpx.get(url, follow_redirects=True)
#     if response.status_code == 200:
#         soup = BeautifulSoup(response.text, "html.parser")
#         js_pattern = re.compile(r".*/area(-\w+)?\.js(\?.*)?$")
#         found_scripts = []
#         for script in soup.find_all("script"):
#             src = script.get("src")
#             if src:
#                 if js_pattern.match(src):
#                     full_url = urljoin(url, src)
#                     found_scripts.append(src)
#                     print(full_url)
#         return found_scripts
#     else:
#         print(f"Error: {response.status_code}")
#         return []

# def parse_js_logic_phase1(js_content, js_file_name):
#     # 匹配 a = ['abc', 'bca', 'cab'] 字符串
#     list_pattern = re.compile(r"\w+\s*=\s*\[(.*?)\]")
#     list_match = list_pattern.search(js_content)
#     if not list_match:
#         print(f"在 {js_file_name} 文件中没找到列表定义")
#         return []
#     raw_content = list_match.group(1)

#     items = re.findall(r"['\"](.*?)['\"]", raw_content)
#     print(f"1. List items: {items}")

#     # Zero.fetch.get('~/data/prismplusArea/'+a[e]+'.json'
#     url_pattern = re.compile(r"Zero\.fetch\.get\(\s*['\"](.*?)['\"]\s*\+\s*.*?\+\s*['\"](.*?)['\"]")

#     url_match = url_pattern.search(js_content)
#     if not url_match:
#         print("Found no json pattern string.")
#         # todo / another logic
#         return []

#     prefix = url_match.group(1)
#     suffix = url_match.group(2)
#     print(f"2. template {prefix} {suffix}")
    
#     clean_prefix = prefix.replace("~", "")
#     full_urls = []
#     for item in items:
#         full_url = urljoin(BASE_URL, f"{clean_prefix}{item}{suffix}")
#         full_urls.append(full_url)
#         print(full_url)
#         # full_url = f"{base_url}{clean_prefix}"
#     return full_urls

# async def fetch_and_save_phase1(client, url, directory):
#     try:
#         filename = url.split("/")[-1]
#         response = await client.get(url)

#         if response.status_code == 200:
#             file_path = directory / filename
#             file_path.write_bytes(response.content)
#             print(f"Save Successfully: {file_path}")
#         else:
#             print(f"Download error! code: {response.status_code}")
#     except Exception as e:
#         print(f"Error {url}: {e}")

# def get_json(url):
#     response = httpx.get(url)
#     if response.status_code != 200:
#         print(f"Error code: {response.status_code}")
#         return []
#     return response.json()

# async def get_image(client, url):
#     response = await client.get(url)
#     if response.status_code != 200:
#         print(f"Error code: {response.status_code}")
#         return None
#     return response.content

# async def download_image(client, dir, url):
#     async with semaphore: 
#         img_data = await get_image(client, url)
#         if img_data:
#             with open(dir, "wb") as f:
#                 f.write(img_data)
#         else:
#             print(f"Error! {url}", url)

# async def download_jsons(dir_name, json_urls, fetch_and_save):
#     save_dir = Path(dir_name)
#     save_dir.mkdir(exist_ok=True)

#     async with httpx.AsyncClient() as client:
#         tasks = []
#         for json_url in json_urls:
#             tasks.append(fetch_and_save(client, json_url, save_dir))
#         await asyncio.gather(*tasks)

# # result:
# # https://maimai.sega.jp/data/{版本名}Area/{id}.json 
# # dx area = area not dxArea

# def build_unified_index(version_names):
#     url = urljoin(BASE_URL, "./data/")
#     # dx to do
#     all_areas = []
#     for version_name in version_names:
#         site_url = urljoin(url, f"./{version_name}Area/index.json")
#         items = get_json(site_url)       
#         for item in items:
#             clean_item = {
#                 "id": item["id"],
#                 "text": item["text"],
#                 "version": version_name
#             }
#             all_areas.append(clean_item)
#             print(clean_item)

#     output_file = Path("../raw_data/area_index.json")
#     output_file.write_text(
#         json.dumps(all_areas, ensure_ascii=False, indent=2), 
#         encoding="utf-8"
#     )
#     return all_areas

# def fetch_begin_page():
#     url = "https://maimai.sega.jp/area/hapifes/story/"
#     response = httpx.get(url)
#     print(response.text)

# async def fetch_data_phase1():
#     version_list = ["", "./prismplus/", "./prism/", "./buddiesplus/", "./buddies/"]
#     area_url = urljoin(BASE_URL, "./area/")
#     version_urls = [urljoin(area_url, version) for version in version_list]
#     for version_url in version_urls:
#         print(version_url)
#         js_filenames = find_js_files(version_url)
#         if js_filenames == []:
#             print("No any js files. Maybe there are some mistakes.")
#             continue
#         for js_filename in js_filenames:
#             full_url = urljoin(version_url, js_filename)
#             print(js_filename, full_url)
#             js_content = httpx.get(full_url).text
#             print(js_content)
#             json_urls = parse_js_logic_phase1(js_content, js_filename)
#             await download_jsons("../raw_data", json_urls, fetch_and_save_phase1)

# async def fetch_data_phase2():
#     # version_site_list = ["./festivalplus/", "./festival/", "./universeplus/", "./universe-unit/", "./splashplus/", "./splash/", "./dxplus/", "./dx/"]
#     version_name_list = ["festivalplus", "festival", "universeplus", "universe", "splashplus", "splash"]
#     # base_url = "https://maimai.sega.jp/area/"
#     # version_urls = [urljoin(base_url, version) for version in version_site_list]
#     all_areas = build_unified_index(version_name_list)
#     json_urls = []
#     for area in all_areas:
#         json_urls.append(f"https://maimai.sega.jp/data/{area["version"]}Area/{area["id"]}.json")
#     await download_jsons("../raw_data", json_urls, fetch_and_save_phase1)

# async def fetch_img():
#     base_dir = Path("../docs/src/images")
#     urls = []
#     for json_file in Path("../raw_data").rglob("*.json"):
#         with open(json_file, "r", encoding="utf-8") as f:
#             area = json.load(f)
#         area_id = area['id']
#         print(area_id)
#         area_dir = base_dir / area_id

#         area_dir.mkdir(parents=True, exist_ok=True)
#         area_url = urljoin(BASE_URL, f"./storage/area/region/{area_id}/")
#         print(area_url)
#         urls.append((area_dir / 'soukanzu.png', urljoin(area_url, "./pc/soukanzu.png")))
#         # download_image(area_dir / 'soukanzu.png', urljoin(area_url, "./pc/soukanzu.png"))

#         # https://maimai.sega.jp/storage/area/region/
#         for char in area['characters']:
#             img_url = urljoin(area_url, f"./icon/{char['img']}.png")
#             output_dir = area_dir / f"{char['img']}.png"
#             urls.append((output_dir, img_url))
#             # download_image(output_dir, img_url)
            
#         for song in area['songs']:
#             thumbnail = song['thumbnail']
#             img_url = urljoin(area_url, f"./jacket/{thumbnail}.png")
#             output_dir = area_dir / f"{thumbnail}.png"
#             urls.append((output_dir, img_url))
#             # download_image(output_dir, img_url)
    
#     async with httpx.AsyncClient() as client:
#         tasks = [
#             download_image(client, dir, url)
#             for (dir, url) in urls
#         ]
#         await asyncio.gather(*tasks)

# # result:
# # https://maimai.sega.jp/data/{版本名}Area/{id}.json 
# # dx area = area not dxArea

# # def proof_phase2():
# #     # version_name_list = ["festivalplus", "festival", "universeplus", "universe", "splashplus", "splash", "dxplus", "dx"]
# #     # version_list = ["./festivalplus/", "./festival/", "./universeplus/", "./universe-unit/", "./splashplus/", "./splash/", "./dxplus/", "./dx/"]
# #     # base_url = "https://maimai.sega.jp/area/"

# #     url = "https://maimai.sega.jp/lib/site.js"
# #     response = httpx.get(url)
# #     # print(response.text)
# #     json_pattern = re.compile(r"t='(.*?)'\s*\+\s*this\.areaId\+\s*'(\.json)'")
# #     result = json_pattern.findall(response.text)
# #     print(result)

# #     # version_urls = [urljoin(base_url, version) for version in version_list]
# #     # for version_url in version_urls:
# #         # '~/data/universeArea/'+this.areaId+'.json'
        

# # proof_phase2()

# # fetch_begin_page()
# # asyncio.run(fetch_data_phase1())
# # asyncio.run(fetch_data_phase2())
# asyncio.run(fetch_img())