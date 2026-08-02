# 代码库Wiki漂移检查 SOP

> 执行 karpathy-project-wiki LINT 漂移检查 | 每周日11:00发送

---

## 执行方式

```bash
python3 ~/.openclaw/workspace/scripts/project_drift_check.py
```

## 报告格式

```json
{
  "schema": "2.0",
  "header": {
    "title": {"tag": "plain_text", "content": "🔍 代码库Wiki漂移检查 | YYYY-MM-DD"},
    "template": "blue"
  },
  "body": {
    "elements": [
      {"tag": "markdown", "content": "## 📌 一、未归档脚本\n\nscripts/ 下未在 wiki 归档的脚本..."},
      {"tag": "markdown", "content": "## 📌 二、Skills变化\n\nskills/ 数量变化..."},
      {"tag": "markdown", "content": "## 📌 三、Wiki引用有效性\n\n无效引用（如有）..."}
    ]
  }
}
```

## 无问题时

发送「✅ 代码库与Wiki同步，无漂移」到群即可。

## 发送方式

`python3 scripts/send_feishu_card.py oc_2581c03b79e4893cc3616b253d60f34e '<card_json>'`

---

*最后更新：2026-08-02*
