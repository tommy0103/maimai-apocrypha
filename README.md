[![License: CC BY-NC-SA 4.0](https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by-nc-sa/4.0/)

### 下载原始数据

`uv run scraper.py phase1`

`uv run scraper.py phase2`

`uv run scraper.py images --concurrency 16`

### 翻译文本

`uv run translator.py`

运行 `translator.py` 需要设置对应的 api key，并产生对应的费用。

### 生成 markdown 文件

`uv run generate_md.py`

需要先在 raw_data 目录下放置原始数据，然后使用上述命令生成 markdown 文件。

### 翻译导入

`uv import_translations.py /path/to/translation.csv --interactive`

需要先在 Feishu 中导出翻译 CSV 文件，然后使用上述命令导入。

正在构思更好的贡献翻译方式，欢迎在 issue 中交流讨论。
