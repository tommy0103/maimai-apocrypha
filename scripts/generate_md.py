import argparse
import html
import json
import logging
from pathlib import Path

DEFAULT_OUTPUT_DIR = Path("../docs/areas")

def safe_html_text(text):
    if not text:
        return ""
    text = str(text)
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    escaped = html.escape(text)
    return escaped.replace('\n', '<br>')


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def format_attr_value(value) -> str:
    value = "" if value is None else str(value)
    if '"' in value:
        escaped = html.escape(value, quote=False).replace('"', "&quot;")
        return escaped
    escaped = html.escape(value, quote=False).replace("'", "&#39;")
    return escaped


def is_missing(value) -> bool:
    if value is None:
        return True
    if isinstance(value, str) and value.strip() == "":
        return True
    return False


def deep_merge(base, overlay):
    if is_missing(overlay):
        return base
    if isinstance(base, dict) and isinstance(overlay, dict):
        merged = dict(base)
        for key, value in overlay.items():
            if key in base:
                merged[key] = deep_merge(base[key], value)
            else:
                merged[key] = value
        return merged
    if isinstance(base, list) and isinstance(overlay, list):
        merged = []
        max_len = max(len(base), len(overlay))
        for i in range(max_len):
            if i < len(base) and i < len(overlay):
                merged.append(deep_merge(base[i], overlay[i]))
            elif i < len(overlay):
                merged.append(overlay[i])
            else:
                merged.append(base[i])
        return merged
    return overlay


def get_list_item(items, index, fallback):
    if isinstance(items, list) and index < len(items):
        return items[index]
    return fallback


def generate_markdown(area_file: Path, output_dir: Path, lang: str | None):
    area_jp_file = area_file
    area_jp = load_json(area_jp_file)

    area_local = area_jp
    if lang:
        area_local_file = area_file.with_suffix(f".{lang}.json")
        if area_local_file.exists():
            area_local = deep_merge(area_jp, load_json(area_local_file))
        else:
            logging.warning("No translation file found: %s", area_local_file)


    # 2. 遍历每个区域 (Area)
    # for area in areas:
    file_name = f"{area_jp['id']}.md"
    file_path = output_dir / file_name
        
    # 开始构建 Markdown 内容
    md_content = []
        
    # --- Frontmatter (VitePress 元数据) ---
    md_content.append("---")
    md_content.append(f"title: {area_local.get('name', area_jp['name'])}") # 优先用译名
    md_content.append(f"editLink: true") # 允许社区编辑
    md_content.append("---")
        
        # --- 标题与简介 ---
    md_content.append(f"\n# {area_local.get('name', area_jp['name'])}（{area_jp.get('name', '')}）")
    
    area_story_jp = area_jp.get('area', area_jp.get('comment', ''))
    area_story_zh = area_local.get('area', area_local.get('comment', ''))

        # 双语简介 (使用引用块或折叠)
    md_content.append("::: info 区域简介")
    md_content.append(area_story_zh)
    md_content.append(":::")
        
    md_content.append("<details class='raw-text'>")
    md_content.append("<summary>查看日语原文 (Original Text)</summary>\n")
    md_content.append(f"> {area_story_jp}")
    md_content.append("</details>\n")

    soukanzu_url = f"/src/images/{area_jp['id']}/soukanzu.png"
    
    # 使用 HTML 居中显示大图，视觉效果更好
    md_content.append(f"""
<div style="text-align: center; margin: 20px 0;">
  <img src="{soukanzu_url}" alt="相关图" style="max-width: 100%; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
  <p style="font-size: 0.8em; color: #666;">区域人物相关图</p>
</div>
""")

        # --- 角色介绍 (Characters) ---
    if 'characters' in area_jp:
        md_content.append("\n## 登場人物 (Characters)")
            
        # for char in area['characters']:
        chars_jp = area_jp['characters']
        chars_local = area_local.get('characters', [])
        for i in range(len(chars_jp)):
            char_jp = chars_jp[i]
            char_local = get_list_item(chars_local, i, char_jp)
            # 假设你已经把片假名转成了英文名存在 'name_en' 或直接覆盖 'name'
            name = char_local.get('name', '')
                
            # md_content.append(f"\n### {name}（{char_jp['name']}）")
                
            # # 角色卡片排版
            # # 这里展示台词
            # if 'serif' in char_jp:
            #     # 假设 JSON 里有 serif_zh
            #     serif_zh = char_zh.get('serif', char_jp['serif']) 
            #     md_content.append(f"**「{serif_zh}」**\n")
                
            # # 角色简介
            # md_content.append(char_zh.get('summary', char_jp['summary']))
                
            # # 属性列表 (用表格展示)
            # md_content.append("\n| 属性 | 内容 |")
            # md_content.append("| :--- | :--- |")
            # # 假设 title1/item1 这种结构
            # if 'title1' in char_zh: md_content.append(f"| {char_zh['title1']} | {char_zh['item1']} |")
            # if 'title2' in char_zh: md_content.append(f"| {char_zh['title2']} | {char_zh['item2']} |")
            # if 'title3' in char_zh: md_content.append(f"| {char_zh['title3']} | {char_zh['item3']} |")
                
            # # 原文折叠
            # md_content.append("\n<details class='raw-text'>")
            # md_content.append(f"<summary>原文数据 ({char_jp['name']})</summary>\n")
            # md_content.append(f"- **台詞**: {char_jp.get('serif', '')}")
            # md_content.append(f"- **紹介**: {char_jp.get('summary', '')}")
            # md_content.append("</details>\n")

            # 路径规则: /images/{area_id}/{img_filename}.png
            # 注意：这里直接用 JSON 里的 "01", "02" 拼接
            img_filename = char_jp.get('img', '')
            img_url = f"/src/images/{area_jp['id']}/{img_filename}.png"

            serif_jp = safe_html_text(char_jp.get('serif', ''))
            serif_zh = safe_html_text(char_local.get('serif', '...'))
            summary_jp = safe_html_text(char_jp.get('summary', ''))
            summary_zh = safe_html_text(char_local.get('summary', '...'))
            
            stats_items = []
            for i in range(1, 4):
                t_key = f'title{i}'
                i_key = f'item{i}'

                title = char_local.get(t_key)
                val = char_local.get(i_key)

                if title and val:
                    t_safe = safe_html_text(title)
                    v_safe = safe_html_text(val)
                    stats_items.append(f'<span style="white-space: nowrap;"><span style="opacity: 0.6; margin-right: 4px;">{t_safe}:</span><b>{v_safe}</b></span>')
            
            if stats_items:
                stats_html = f"""
<div style="display: flex; flex-wrap: wrap; gap: 15px; font-size: 0.9em; margin: 10px 0; padding: 8px 12px; background: var(--vp-c-bg-alt); border-radius: 6px;">
{''.join(stats_items)}
</div>
"""
            else:
                stats_html = ""

            # 使用 Flexbox 布局：左边头像(120px)，右边文字
            card_html = f"""\
<div style="display: flex; gap: 20px; align-items: flex-start; margin-bottom: 40px; padding: 15px; background: var(--vp-c-bg-soft); border-radius: 12px;">
<div style="flex-shrink: 0; width: 120px;">
<img src="{img_url}" alt="{name}" style="width: 100%; border-radius: 8px; object-fit: cover;">
</div>
<div style="flex-grow: 1;">
<h3 style="margin-top: 0;">{name}</h3>
<p><b>「{serif_zh}」</b></p>
{stats_html}
<p>{summary_zh}</p>    
<details class="raw-text" style="margin-top: 10px; border: 1px solid var(--vp-c-divider); padding: 8px; border-radius: 4px;">
<summary style="cursor: pointer; opacity: 0.7;">查看原文数据</summary>
<div style="font-size: 0.9em; margin-top: 8px; color: var(--vp-c-text-2);">
<p><b>台詞:</b> {serif_jp}</p>
<p><b>紹介:</b> {summary_jp}</p>
</div>
</details>
</div>
</div>
"""
            md_content.append(card_html)

        # --- 歌曲剧情 (Songs) ---
    if 'songs' in area_jp:
        md_content.append("\n## 楽曲ストーリー (Stories)")
            
        songs_jp = area_jp['songs']
        songs_local = area_local.get('songs', [])

        for i in range(len(songs_jp)):
            song_jp = songs_jp[i]
            song_local = get_list_item(songs_local, i, song_jp)

            title = song_jp.get('songtitle', 'Unknown Song')
            artist = song_jp.get('artist', 'Unknown Artist')
            title_attr = format_attr_value(title)
    
                # 核心剧情文本
            story_zh = safe_html_text(song_local.get('songsummary', '（暂无剧情翻译）'))
            story_jp = safe_html_text(song_jp.get('songsummary', ''))
                
                # 如果没剧情就跳过
            # if not story_jp:
            #     md_content.append("> *该歌曲暂无背景故事*")
            #     continue

            thumb_filename = song_jp.get('thumbnail', '')
            jacket_url = f"/src/images/{area_jp['id']}/{thumb_filename}.png"
            
            # md_content.append(f"### {title}")
            # md_content.append(f'<Badge type="info" text="{artist}" />\n')
            
            # # 歌曲封面通常不需要太复杂布局，直接放出来就行
            # # 限制一下宽度防止太巨大
            # md_content.append(f'<img src="{jacket_url}" alt="{title}" style="width: 200px; border-radius: 6px; margin: 10px 0;">\n')
            
            # md_content.append(f"\n{story_zh}\n")

            # #     # 正文展示
            # # md_content.append(story_zh)
                
            # #     # 原文折叠
            # md_content.append("\n<details class='raw-text'>")
            # md_content.append("<summary>日文原文 (Japanese)</summary>\n")
            # md_content.append(story_jp)
            # md_content.append("</details>\n")

            song_html = f"""
<div style="display: flex; gap: 20px; align-items: flex-start; margin-bottom: 40px; padding: 20px; background: var(--vp-c-bg-soft); border-radius: 12px; border: 1px solid var(--vp-c-divider);">
    
<div style="flex-shrink: 0; width: 140px;">
<img src="{jacket_url}" alt="{title_attr}" style="width: 100%; border-radius: 6px; box-shadow: 0 8px 16px rgba(0,0,0,0.15); aspect-ratio: 1/1; object-fit: cover;">
</div>
    
<div style="flex-grow: 1;">
<div style="display: flex; flex-wrap: wrap; align-items: center; gap: 10px; margin-bottom: 12px;">
<h3 style="margin: 0; border: none; font-size: 1.3em;">{title}</h3>
<Badge type="tip" text="{artist}" style="vertical-align: middle;" />
</div>
        
<div style="opacity: 0.9; line-height: 1.7;">
{story_zh}
</div>
        
<details class="raw-text" style="margin-top: 15px; border-top: 1px dashed var(--vp-c-divider); padding-top: 10px;">
<summary style="cursor: pointer; opacity: 0.6; font-size: 0.85em;">查看日语原文</summary>
<div style="font-size: 0.9em; margin-top: 8px; color: var(--vp-c-text-2);">
{story_jp}
</div>
</details>
</div>
</div>
"""
            md_content.append(song_html)

        # 3. 写入文件
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(md_content))
            
    print(f"✅ Generated: {file_name}")

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate VitePress markdown from area JSON.")
    parser.add_argument("--data-dir", default="../raw_data")
    parser.add_argument("--output-dir", default=str(DEFAULT_OUTPUT_DIR))
    parser.add_argument("--lang", default=None, help="Translation suffix, e.g. zh")
    parser.add_argument("--log-level", default="INFO")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    logging.basicConfig(level=args.log_level, format="%(levelname)s: %(message)s")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    files = list(Path(args.data_dir).rglob("*.json"))
    for f in files:
        if args.lang and f.name.endswith(f".{args.lang}.json"):
            continue
        if not args.lang and ".zh" in f.name:
            continue
        generate_markdown(f, output_dir, args.lang)


if __name__ == "__main__":
    main()
    