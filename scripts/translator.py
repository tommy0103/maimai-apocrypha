import json
import os
import time
from openai import OpenAI
from pathlib import Path
from tqdm import tqdm

def translate_json(data):
    # 直接让 LLM 翻译整个 JSON
    response = client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
        {"role" : "system", "content": """
    # Role
    你是一个自动化本地化 Agent，专门负责将《maimai》的游戏数据从日文转换为中文。
    你的目标是处理不确定的新角色和新剧情，并在没有人工干预的情况下保持高质量输出。

    # Core Translation Rules (核心翻译规则)

    1. **Syntax Reconstruction (关键：语序重构)**
    - **问题**：日语常将动词放在句尾 (SOV)，且喜欢用长定语修饰名词。
    - **规则**：
        - **打破语序**：不要按照日语原文的词序逐词翻译。请先理解整句逻辑，再按中文习惯 (SVO) 重组句子。
        - **拆分长句**：如果日语的长定语导致中文通顺度下降，请将长句拆分为两个短句。
        - *Bad Example*: "从买东西回来的 Ras" (保留了日语倒装)
        - *Good Example*: "Ras 刚买完东西回来" (符合中文逻辑)

    2. **Subject Inference (关键：主语补全)**
    - **问题**：日语经常省略主语 (我/你/他)。
    - **规则**：
        - **上下文推断**：根据当前字段的 `name` (角色名) 或上一句的语境，智能补全省略的主语。
        - **避免代词滥用**：如果主语明确，直接使用名字（或“她/他”），不要生硬地保留空白或强行加“它”。
        - 在 `summary` 中，如果主语是当前角色，中文翻译时通常可以省略主语，或者在段首点明一次即可。

    3. **Name Handling (关键：人名处理)**
    - **规则**：当 `name` 字段或剧情中出现**片假名 (Katakana)** 的人名时，**不要**翻译成中文，而是将其转换为**对应的英文 (English/Romaji)**。
    - **策略**：
        - 如果是常见的英语借词名，使用标准拼写 (e.g., シフォン -> Chiffon, ソルト -> Salt)。
        - 如果是独特名字，使用最自然的英文拼写 (e.g., ラズ -> Ras, らいむ -> Lime)。
        - **禁止**出现“拉兹”、“戚风”这样的中文音译。

    4. **Dynamic Tone Adaptation (动态语气适配)**
    - **规则**：你不需要预先知道角色的性格。请**实时分析**该角色在 `serif` (台词) 和 `summary` (简介) 中的日语用词。
    - **策略**：
        - 看到「～ですわ/～ますの」 -> 翻译为**大小姐/优雅语气** (e.g., "是呢", "…哟")。
        - 看到「～マイ/～だもん/～ナノデ」等特殊句尾 -> 尝试在中文里保留这种**口癖**的韵味，或使用可爱的语气。
        - 看到大量感叹号或短句 -> 翻译为**元气/活泼语气**。

    5. **Game Terminology (通用术语)**
    - ちほー -> 区域 (Area)
    - でらっくす -> Deluxe
    - コレクション -> Collection
    - *其他专有名词如果无法确定，优先意译，或者保留原文。*

    # JSON Safety Rules
    - 仅翻译值为 **日语字符串** 的字段。
    - **绝对禁止** 修改 `id`, `youtubeID`, `img` 等元数据字段。
    - **绝对禁止** 修改 JSON 结构。

    # Output Requirement
    输出纯净的 JSON 字符串。"""},
        {
            "role": "user", 
            "content": f"""{json.dumps(data, ensure_ascii=False, indent=2)}"""
        }],
        temperature=0.3
    )

    # 代词：尽量少用“他/她/它”，在中文语境下如果主语明确，可以省略，以增加代入感。
    # 请直接把片假名译成对应的英文。

    # 解析返回的 JSON
    result_text = response.choices[0].message.content
    # 去掉可能的 markdown 代码块标记
    result_text = result_text.strip()
    if result_text.startswith("```"):
        result_text = result_text.split("```")[1]
        if result_text.startswith("json"):
            result_text = result_text[4:]
        result_text = result_text.strip()

    return json.loads(result_text)

def translate_from_to(input_file, output_file):
    # 读取 JSON
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = translate_json(data)

    # 保存
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

client = OpenAI(
    api_key=os.environ.get("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

# files = list(Path("./raw_data").rglob("*.json"))
# files = list(Path("./raw_data").rglob("7sref[1-4].json"))
files =[Path("../raw_data/7sref.json"), Path("../raw_data/7sref4.json"),
        Path("../raw_data/7sref2.json"), Path("../raw_data/7sref3.json")]
start = time.time()

# translate_from_to("input.json", "output.json")
for input_file in tqdm(files, desc="Translateing..."):
    # print(input_file.__str__())
    output_file = input_file.with_suffix(".zh.json")
    # print(input_file, output_file)
    # output_file = 
    translate_from_to(input_file, output_file)

print(f"Finished! Total: {time.time() - start:.2f}s")
