---
title: 贡献翻译
editLink: true
---

# 贡献翻译

可以通过 GitHub 帐号提交对应 `*.zh.json` 文件的 PR。

如果你没有 GitHub 账号，也可以通过表单参与翻译。填写后，我会定期导出并合并到站点里。

表单链接：[https://hcnvswz2ngt8.feishu.cn/share/base/form/shrcngEBZAylqG0nmsziM53spg6](https://hcnvswz2ngt8.feishu.cn/share/base/form/shrcngEBZAylqG0nmsziM53spg6)

可以直接填写表单，也可以通过表单上传 csv 文件。

## 表单字段

请在表单中填写以下字段：

- `area_id`：区域 ID，例如 `skystreet6`
- `path`：字段路径，例如 `characters[0].summary`
- `text`：译文内容

可翻译字段范围：

- `name`
- `comment`
- `area`
- `characters[i].name`
- `characters[i].summary`
- `characters[i].serif`
- `songs[i].songsummary`

## CSV 模板

你也可以下载模板 CSV，离线填写后再提交：

- [translation_template.csv](/translation_template.csv)

示例行：

```
area_id,path,text,note
skystreet6,characters[0].summary,这里是译文,可选备注
```
