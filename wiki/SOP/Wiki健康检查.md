# Wiki健康检查 SOP

> 执行 karpathy-wiki LINT 健康检查，发送Wiki状态报告 | 每周日10:00发送

---

## 执行方式

```bash
python3 ~/.openclaw/workspace/scripts/wiki_drift_check.py
```

## 报告格式

```json
{
  "schema": "2.0",
  "header": {
    "title": {"tag": "plain_text", "content": "🩺 Wiki健康检查 | YYYY-MM-DD"},
    "template": "green"
  },
  "body": {
    "elements": [
      {"tag": "markdown", "content": "## 📌 一、健康状态\n\n✅/⚠️ 整体评估..."},
      {"tag": "markdown", "content": "## 📌 二、孤儿页面\n\n（无 inbound 链接的页面）..."},
      {"tag": "markdown", "content": "## 📌 三、内容稀薄页面\n\n（<5行的页面）..."},
      {"tag": "markdown", "content": "## 📌 四、建议\n\n修复建议..."}
    ]
  }
}
```

## 无问题时的简化格式

发送「✅ Wiki状态健康，上周无漂移」到群即可。

## 发送方式

`python3 scripts/send_feishu_card.py oc_2581c03b79e4893cc3616b253d60f34e '<card_json>'`

---

*最后更新：2026-06-07*
