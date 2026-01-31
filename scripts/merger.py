import json
import hashlib
import os

# 模拟 LLM 调用
def call_llm_translate(text):
    print(f"  [LLM] Translating: {text[:10]}...")
    return f"(中) {text}" # 伪代码返回

def get_hash(text):
    if not text: return ""
    return hashlib.md5(str(text).encode()).hexdigest()

# --- 核心：通用字段合并器 ---
def merge_field(obj_key, raw_obj, db_obj, field_name_raw, field_name_zh):
    """
    检查 raw_obj[field_name_raw] 的哈希。
    如果变了 -> 调用 LLM -> 更新 db_obj[field_name_zh]
    如果没变 -> 保留 db_obj[field_name_zh]
    """
    raw_text = raw_obj.get(field_name_raw, "")
    current_hash = get_hash(raw_text)
    hash_key = f"{field_name_raw}_hash" 
    
    if (field_name_zh not in db_obj) or (db_obj.get(hash_key) != current_hash):
        if raw_text:
            db_obj[field_name_zh] = call_llm_translate(raw_text)
        else:
            db_obj[field_name_zh] = ""
            
        db_obj[hash_key] = current_hash
        db_obj[f"{field_name_raw}_ja"] = raw_text # 存一份日文原文在库里方便对照
    else:
        pass

# --- 核心：列表合并器 ---
def merge_list(raw_list, db_list, anchor_key, fields_to_translate):
    """
    raw_list: 爬虫爬到的新列表
    db_list: 数据库里现有的列表
    anchor_key: 用来对齐的字段 (如 'name' 或 'songtitle')
    fields_to_translate: 需要翻译的字段映射 { 'summary': 'summary_zh', 'serif': 'serif_zh' }
    """
    db_map = {item.get(anchor_key): item for item in db_list if item.get(anchor_key)}
    
    new_db_list = []
    
    for raw_item in raw_list:
        anchor_val = raw_item.get(anchor_key)
        if not anchor_val: continue
        
        if anchor_val in db_map:
            db_item = db_map[anchor_val]
        else:
            db_item = {anchor_key: anchor_val} # 新建
            
        for k, v in raw_item.items():
            if k not in fields_to_translate and k != anchor_key:
                db_item[k] = v
        
        for raw_field, zh_field in fields_to_translate.items():
            merge_field(anchor_val, raw_item, db_item, raw_field, zh_field)
            
        new_db_list.append(db_item)
        
    return new_db_list

# --- 主流程 ---
def run_merger(raw_data_path, db_data_path):
    # 读取
    with open(raw_data_path, 'r') as f: 
        raw_root = json.load(f)
    
    if os.path.exists(db_data_path):
        with open(db_data_path, 'r') as f: 
            db_root = json.load(f)
    else:
        db_root = {"id": raw_root['id']}

    print(f"Processing {raw_root['name']}...")

    # 1. 处理根目录字段
    merge_field("root", raw_root, db_root, "name", "name_zh")
    merge_field("root", raw_root, db_root, "area", "area_zh")
    
    # 复制其他根元数据 (youtubeID 等)
    db_root["youtubeID"] = raw_root.get("youtubeID")

    # 2. 处理 Characters 列表
    #    告诉合并器：用 'name' 做 ID，翻译 'summary' 和 'serif'
    db_root['characters'] = merge_list(
        raw_list=raw_root.get('characters', []),
        db_list=db_root.get('characters', []),
        anchor_key='name',
        fields_to_translate={
            'summary': 'summary_zh',
            'serif': 'serif_zh',
            # 甚至 title 也可以翻译
            'title1': 'title1_zh', 
            'item1': 'item1_zh',
            'title2': 'title2_zh',
            'item2': 'item2_zh',
            'title3': 'title3_zh',
            'item3': 'item3_zh'
        }
    )

    # 3. 处理 Songs 列表
    #    告诉合并器：用 'songtitle' 做 ID，翻译 'songsummary'
    db_root['songs'] = merge_list(
        raw_list=raw_root.get('songs', []),
        db_list=db_root.get('songs', []),
        anchor_key='songtitle',
        fields_to_translate={
            'songsummary': 'songsummary_zh'
        }
    )

    # 保存
    with open(db_data_path, 'w', encoding='utf-8') as f:
        json.dump(db_root, f, ensure_ascii=False, indent=2)
    print("Done.")

# 测试运行
# run_merger("raw_data/7sref2.json", "data/7sref2.json")