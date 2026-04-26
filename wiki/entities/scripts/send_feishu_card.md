# send_feishu_card.py

> 飞书卡片发送统一入口脚本

---

## 基本信息

| 项目 | 内容 |
|------|------|
| 文件 | `~/.openclaw/workspace/scripts/send_feishu_card.py` |
| 用途 | 统一发送所有飞书卡片的入口 |
| 调用方式 | Python函数 `send_card(chat_id, card)` |

---

## 格式规范（2026-04-19确认）

```json
{
  "schema": "2.0",
  "header": {
    "title": {"tag": "plain_text", "content": "标题"},
    "template": "orange"
  },
  "body": {
    "elements": [
      {"tag": "markdown", "content": "内容"}
    ]
  }
}
```

---

## 关键规则

| 规则 | 说明 |
|------|------|
| header.title | 必须是 `{"tag": "plain_text", "content": "..."}` |
| 内容位置 | 放在 `body.elements[]`，不是根级 |
| 表格格式 | 表头+表格行放同一 element，不能拆分 |
| 验证 | 发送前调用 `validate_card()` 检查格式 |

---

## 调用示例

```python
from send_feishu_card import send_card

card = {
  "schema": "2.0",
  "header": {"title": {"tag": "plain_text", "content": "标题"}, "template": "orange"},
  "body": {"elements": [{"tag": "markdown", "content": "内容"}]}
}

# 发送私信
send_card("ou_f308d672765ecf1be73a75eb5e5f0f48", card)

# 发送群
send_card("oc_2581c03b79e4893cc3616b253d60f34e", card)
```

---

## 飞书群ID

| 群 | ID |
|------|------|
| 电影小镇群 | `oc_2581c03b79e4893cc3616b253d60f34e` |
| 数据推送群 | `oc_f109bcfd1bc7e166fd0ae077f70247cf` |

---

*最后更新：2026-04-26*
