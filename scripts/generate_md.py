import json
import os
from pathlib import Path

# 配置路径
# DATA_FILE = Path("raw_data/7sref.json") # 假设你的 JSON 是一个包含多个区域的大列表
OUTPUT_DIR = Path("../docs/areas")

# 确保输出目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_markdown(area_file):
    # 1. 读取数据

    # area_zh_file = Path("raw_data/7sref.zh.json")
    # area_jp_file = Path("raw_data/7sref.json")
    area_jp_file = area_file
    area_zh_file = area_file.with_suffix(".zh.json")

    with open(area_zh_file, 'r', encoding='utf-8') as f:
        area_zh = json.load(f)
    with open(area_jp_file, 'r', encoding='utf-8') as f:
        area_jp = json.load(f)


    # 2. 遍历每个区域 (Area)
    # for area in areas:
    file_name = f"{area_jp['id']}.md"
    file_path = OUTPUT_DIR / file_name
        
    # 开始构建 Markdown 内容
    md_content = []
        
    # --- Frontmatter (VitePress 元数据) ---
    md_content.append("---")
    md_content.append(f"title: {area_zh.get('name', area_jp['name'])}") # 优先用中文名
    md_content.append(f"editLink: true") # 允许社区编辑
    md_content.append("---")
        
        # --- 标题与简介 ---
    md_content.append(f"\n# {area_zh.get('name', area_jp['name'])}（{area_jp.get('name', '')}）")
        
        # 双语简介 (使用引用块或折叠)
    md_content.append("::: info 区域简介")
    md_content.append(area_zh.get('area', '（暂无翻译）'))
    md_content.append(":::")
        
    md_content.append("<details class='raw-text'>")
    md_content.append("<summary>查看日语原文 (Original Text)</summary>\n")
    md_content.append(f"> {area_jp['area']}")
    md_content.append("</details>\n")

        # --- 角色介绍 (Characters) ---
    if 'characters' in area_jp:
        md_content.append("\n## 登場人物 (Characters)")
            
        # for char in area['characters']:
        chars_jp = area_jp['characters']
        chars_zh = area_zh['characters']
        for i in range(len(chars_jp)):
            char_zh = chars_zh[i]
            char_jp = chars_jp[i]
            # 假设你已经把片假名转成了英文名存在 'name_en' 或直接覆盖 'name'
            name = char_zh.get('name') 
                
            md_content.append(f"\n### {name}（{char_jp['name']}）")
                
            # 角色卡片排版
            # 这里展示台词
            if 'serif' in char_jp:
                # 假设 JSON 里有 serif_zh
                serif_zh = char_zh.get('serif', char_jp['serif']) 
                md_content.append(f"**「{serif_zh}」**\n")
                
            # 角色简介
            md_content.append(char_zh.get('summary', char_jp['summary']))
                
            # 属性列表 (用表格展示)
            md_content.append("\n| 属性 | 内容 |")
            md_content.append("| :--- | :--- |")
            # 假设 title1/item1 这种结构
            if 'title1' in char_zh: md_content.append(f"| {char_zh['title1']} | {char_zh['item1']} |")
            if 'title2' in char_zh: md_content.append(f"| {char_zh['title2']} | {char_zh['item2']} |")
            if 'title3' in char_zh: md_content.append(f"| {char_zh['title3']} | {char_zh['item3']} |")
                
            # 原文折叠
            md_content.append("\n<details class='raw-text'>")
            md_content.append(f"<summary>原文数据 ({char_jp['name']})</summary>\n")
            md_content.append(f"- **台詞**: {char_jp.get('serif', '')}")
            md_content.append(f"- **紹介**: {char_jp.get('summary', '')}")
            md_content.append("</details>\n")

        # --- 歌曲剧情 (Songs) ---
    if 'songs' in area_jp:
        md_content.append("\n## 楽曲ストーリー (Stories)")
            
        songs_jp = area_jp['songs']
        songs_zh = area_zh['songs']

        for i in range(len(songs_jp)):
            song_jp = songs_jp[i]
            song_zh = songs_zh[i]

            title = song_jp.get('songtitle', 'Unknown Song')
            artist = song_jp.get('artist', 'Unknown Artist')
                
            md_content.append(f"\n### {title}")
            md_content.append(f"*Artist: {artist}*\n")
                
                # 核心剧情文本
            story_zh = song_zh.get('songsummary', '（暂无剧情翻译）')
            story_jp = song_jp.get('songsummary', '')
                
                # 如果没剧情就跳过
            if not story_jp:
                md_content.append("> *该歌曲暂无背景故事*")
                continue

                # 正文展示
            md_content.append(story_zh)
                
                # 原文折叠
            md_content.append("\n<details class='raw-text'>")
            md_content.append("<summary>日文原文 (Japanese)</summary>\n")
            md_content.append(story_jp)
            md_content.append("</details>\n")

        # 3. 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
            
    print(f"✅ Generated: {file_name}")

# if __name__ == "__main__":
    
files =[Path("../raw_data/7sref.json"), Path("../raw_data/7sref4.json"),
        Path("../raw_data/7sref2.json"), Path("../raw_data/7sref3.json")]

for f in files:    
    generate_markdown(f)