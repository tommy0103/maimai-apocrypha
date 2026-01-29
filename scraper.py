import httpx
import re
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
    list_pattern = re.compile(r"\w+\s*=\s*\[(.*?)\]")
    list_match = list_pattern.search(js_content)
    if not list_match:
        print(f"在 {js_file_name} 文件中没找到列表定义")
        return []
    raw_content = list_match.group(1)

    items = re.findall(r"['\"](.*?)['\"]", raw_content)
    print(f"1. List items: {items}")

def fetch_data():
    base_url = "https://maimai.sega.jp/area/"
    js_filenames = find_js_files(base_url)
    if js_filenames == []:
        print("No any js files. Maybe there are some mistakes.")
        return
    for js_filename in js_filenames:
        full_url = urljoin(base_url, js_filename)
        print(js_filename, full_url)
        js_content = httpx.get(full_url).text
        print(js_content)
        parse_js_logic(js_content, js_filename, base_url)
        # 5. 提取数据（比如所有的 <h1> 标签）
        # title = soup.find("h1").text
        # print(f"找到标题啦: {title}")
    # elif response.status_code == 301:
        # target_location = response.headers.get("Location");
        # print(target_location);

fetch_data()