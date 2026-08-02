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

*最后更新：2026-08-02*

---

## 🆕 2026-06-30 H1 收官更新

### **6 轮 Obsidian 同步总计（11:08-15:50）**

| 轮次 | 时间 | 文件数 |
|------|------|--------|
| 1 | 11:08-11:25 | 7 |
| 2 | 11:25-11:31 | 32 |
| 3 | 11:35-11:42 | 47 |
| 4 | 13:18-13:45 | 16 |
| 5 | 15:08-15:50 | 8 |
| 6 | 15:14-15:50 | 22 |
| **总计** | — | **142 个文件** |

### **6/30 Wiki 质量**

- 总文件 329 → 142 已 6/30 更新（43%）
- 6 月新生成/更新 95%+
- 双向链接 95%+
- P0 行动截止 7/2 18:00

### **6/30 站长纠错 6 次**

1. 端午累计掩盖初六 782
2. CSV 6/29-30=0 误标收官
3. 客流档案漏 W24-W27
4. 穿越德化街漏更新
5. 自媒体+运营规划漏更新
6. 全量扫描漏 22 个文件

### 关联文档

- 6 轮同步记录：`wiki/log.md`
- H1 一页纸：`memory/2026-06-30-h1-recap.md`
- 索引入口：`wiki/index.md`
