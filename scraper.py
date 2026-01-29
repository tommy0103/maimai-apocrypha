import httpx
import re
import asyncio
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def find_js_files(base_url): # filename_list
    response = httpx.get(base_url, follow_redirects=True)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        js_pattern = re.compile(r".*/area(-\w+)?\.js(\?.*)?$")
        found_scripts = []
        for script in soup.find_all("script"):
            src = script.get("src")
            if src:
                if js_pattern.match(src):
                    full_url = urljoin(base_url, src)
                    found_scripts.append(src)
                    print(full_url)
        return found_scripts
    else:
        print(f"Error: {response.status_code}")
        return []

def parse_js_logic(js_content, js_file_name, base_url):
    # 匹配 a = ['abc', 'bca', 'cab'] 字符串
    base_url = "https://maimai.sega.jp/"
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
        full_url = urljoin(base_url, f"{clean_prefix}{item}{suffix}")
        full_urls.append(full_url)
        print(full_url)
        # full_url = f"{base_url}{clean_prefix}"
    return full_urls

async def fetch_and_save(client, url, directory):
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

async def download_jsons(json_urls):
    save_dir = Path("raw_data")
    save_dir.mkdir(exist_ok=True)

    async with httpx.AsyncClient() as client:
        tasks = []
        for json_url in json_urls:
            tasks.append(fetch_and_save(client, json_url, save_dir))
        await asyncio.gather(*tasks)

def fetch_begin_page():
    base_url = "https://maimai.sega.jp/area/"
    response = httpx.get(base_url)
    print(response.text)

async def fetch_data():
    version_list1 = ["", "./prismplus/", "./prism/", "./buddiesplus/", "./buddies/"]
    base_url = "https://maimai.sega.jp/area/"
    version_urls = [urljoin(base_url, version) for version in version_list1]
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
            json_urls = parse_js_logic(js_content, js_filename, version_url)
            await download_jsons(json_urls)

fetch_begin_page()
asyncio.run(fetch_data())