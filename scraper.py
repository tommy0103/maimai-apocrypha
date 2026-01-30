import httpx
import re
import json
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://maimai.sega.jp/"

def find_js_files(url): # filename_list
    response = httpx.get(url, follow_redirects=True)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        js_pattern = re.compile(r".*/area(-\w+)?\.js(\?.*)?$")
        found_scripts = []
        for script in soup.find_all("script"):
            src = script.get("src")
            if src:
                if js_pattern.match(src):
                    full_url = urljoin(url, src)
                    found_scripts.append(src)
                    print(full_url)
        return found_scripts
    else:
        print(f"Error: {response.status_code}")
        return []

def parse_js_logic_phase1(js_content, js_file_name):
    # 匹配 a = ['abc', 'bca', 'cab'] 字符串
    list_pattern = re.compile(r"\w+\s*=\s*\[(.*?)\]")
    list_match = list_pattern.search(js_content)
    if not list_match:
        print(f"在 {js_file_name} 文件中没找到列表定义")
        return []
    raw_content = list_match.group(1)

    items = re.findall(r"['\"](.*?)['\"]", raw_content)
    print(f"1. List items: {items}")

    # Zero.fetch.get('~/data/prismplusArea/'+a[e]+'.json'
    url_pattern = re.compile(r"Zero\.fetch\.get\(\s*['\"](.*?)['\"]\s*\+\s*.*?\+\s*['\"](.*?)['\"]")

    url_match = url_pattern.search(js_content)
    if not url_match:
        print("Found no json pattern string.")
        # todo / another logic
        return []

    prefix = url_match.group(1)
    suffix = url_match.group(2)
    print(f"2. template {prefix} {suffix}")
    
    clean_prefix = prefix.replace("~", "")
    full_urls = []
    for item in items:
        full_url = urljoin(BASE_URL, f"{clean_prefix}{item}{suffix}")
        full_urls.append(full_url)
        print(full_url)
        # full_url = f"{base_url}{clean_prefix}"
    return full_urls

# """
# 返回一个 string list，和 parse_js_logic_phase1 统一行为
# list 中只有一个元素。
# """
# def parse_js_logic_phase2(js_content, js_file_name): 
#     # 匹配 a = ['abc', 'bca', 'cab'] 字符串
#     base_url = "https://maimai.sega.jp/"

#     # Zero.fetch.get('~/data/prismplusArea/'+a[e]+'.json'
#     url_pattern = re.compile(r"Zero\.fetch\.get\(\s*['\"](.*?)['\"]\s*")

#     url_match = url_pattern.search(js_content)
#     if not url_match:
#         print("Found no json pattern string.")
#         # todo / another logic
#         return []

#     json_filename = url_match.group(1)
    
#     print(f"{json_filename}")
    
#     json_filename = json_filename.replace("~", "")
#     full_urls = [urljoin(base_url, json_filename)]
#     return full_urls

async def fetch_and_save_phase1(client, url, directory):
    try:
        filename = url.split("/")[-1]
        response = await client.get(url)

        if response.status_code == 200:
            file_path = directory / filename
            file_path.write_bytes(response.content)
            print(f"Save Successfully: {file_path}")
        else:
            print(f"Download error! code: {response.status_code}")
    except Exception as e:
        print(f"Error {url}: {e}")

# async def fetch_and_save_phase2(client, url, directory):
#     try:
#         filename = url.split("/")[-1]
#         version_name = url.split("/")[-2]
#         if version_name != 'data':
#             filename = f"{version_name}_{filename}"
#         response = await client.get(url)

#         if response.status_code == 200:
#             file_path = directory / filename
#             file_path.write_bytes(response.content)
#             print(f"Save Successfully: {file_path}")
#         else:
#             print(f"Download error! code: {response.status_code}")
#     except Exception as e:
#         print(f"Error {url}: {e}")

def get_json(url):
    response = httpx.get(url)
    if response.status_code != 200:
        print(f"Error code: {response.status_code}")
        return []
    return response.json()

async def download_jsons(dir_name, json_urls, fetch_and_save):
    save_dir = Path(dir_name)
    save_dir.mkdir(exist_ok=True)

    async with httpx.AsyncClient() as client:
        tasks = []
        for json_url in json_urls:
            tasks.append(fetch_and_save(client, json_url, save_dir))
        await asyncio.gather(*tasks)

# result:
# https://maimai.sega.jp/data/{版本名}Area/{id}.json 
# dx area = area not dxArea

def build_unified_index(version_names):
    url = urljoin(BASE_URL, "./data/")
    # dx to do
    all_areas = []
    for version_name in version_names:
        site_url = urljoin(url, f"./{version_name}Area/index.json")
        items = get_json(site_url)       
        for item in items:
            clean_item = {
                "id": item["id"],
                "text": item["text"],
                "version": version_name
            }
            all_areas.append(clean_item)
            print(clean_item)

    output_file = Path("index/area_index.json")
    output_file.write_text(
        json.dumps(all_areas, ensure_ascii=False, indent=2), 
        encoding="utf-8"
    )
    return all_areas

def fetch_begin_page():
    url = "https://maimai.sega.jp/area/hapifes/story/"
    response = httpx.get(url)
    print(response.text)

async def fetch_data_phase1():
    version_list = ["", "./prismplus/", "./prism/", "./buddiesplus/", "./buddies/"]
    area_url = urljoin(BASE_URL, "./area/")
    version_urls = [urljoin(area_url, version) for version in version_list]
    for version_url in version_urls:
        print(version_url)
        js_filenames = find_js_files(version_url)
        if js_filenames == []:
            print("No any js files. Maybe there are some mistakes.")
            continue
        for js_filename in js_filenames:
            full_url = urljoin(version_url, js_filename)
            print(js_filename, full_url)
            js_content = httpx.get(full_url).text
            print(js_content)
            json_urls = parse_js_logic_phase1(js_content, js_filename)
            await download_jsons("raw_data", json_urls, fetch_and_save_phase1)

async def fetch_data_phase2():
    # version_site_list = ["./festivalplus/", "./festival/", "./universeplus/", "./universe-unit/", "./splashplus/", "./splash/", "./dxplus/", "./dx/"]
    version_name_list = ["festivalplus", "festival", "universeplus", "universe", "splashplus", "splash"]
    # base_url = "https://maimai.sega.jp/area/"
    # version_urls = [urljoin(base_url, version) for version in version_site_list]
    all_areas = build_unified_index(version_name_list)
    json_urls = []
    for area in all_areas:
        json_urls.append(f"https://maimai.sega.jp/data/{area["version"]}Area/{area["id"]}.json")
    await download_jsons("raw_data", json_urls, fetch_and_save_phase1)

# result:
# https://maimai.sega.jp/data/{版本名}Area/{id}.json 
# dx area = area not dxArea

def proof_phase2():
    # version_name_list = ["festivalplus", "festival", "universeplus", "universe", "splashplus", "splash", "dxplus", "dx"]
    # version_list = ["./festivalplus/", "./festival/", "./universeplus/", "./universe-unit/", "./splashplus/", "./splash/", "./dxplus/", "./dx/"]
    # base_url = "https://maimai.sega.jp/area/"

    url = "https://maimai.sega.jp/lib/site.js"
    response = httpx.get(url)
    # print(response.text)
    json_pattern = re.compile(r"t='(.*?)'\s*\+\s*this\.areaId\+\s*'(\.json)'")
    result = json_pattern.findall(response.text)
    print(result)

    # version_urls = [urljoin(base_url, version) for version in version_list]
    # for version_url in version_urls:
        # '~/data/universeArea/'+this.areaId+'.json'
        

# proof_phase2()

# fetch_begin_page()
# asyncio.run(fetch_data_phase1())
asyncio.run(fetch_data_phase2())