# Procedures — How I Do Things

_Last updated: 2026-04-17_

---

## 🎨 Communication Preferences

- **语言：** 中文为主，英文技术术语保留
- **语气：** 专业果决、数据驱动、结论先行
- **格式：** 飞书卡片优先，数据表格清晰

## 🔧 Tool Workflows

### 抖音数据采集
1. 刷新Tab1 → 运行 `douyin_index.py` → 两次验证一致性 → 发私信测试 → 发群 → 写入wiki

### 小红书采集
- 使用Chrome Tab0，在标签内导航
- 每步操作延迟2-5秒防检测
- 搜索后延迟3-8秒

### Cron任务故障排查
1. `openclaw cron list` 查看状态
2. 错误 `startsWith` → 删除重建 + isolated session
3. 错误 `Message failed` → 检查飞书群配置

## 📝 Format Preferences

### 飞书卡片
- schema: "2.0"
- header.template: orange=数据 / purple=分析 / red=预警
- body.elements: markdown格式
- 表格5列：景区 | 搜索指数 | 日环比 | 综合指数 | 日环比

### 日报格式
- 按综合指数由高到低排序
- 🔺异动标注：日环比>±20%
- 完整性和准确性优先

## ⚡ Shortcuts & Patterns

- **日报发送：** message参数固定「请查看卡片」，card参数放完整JSON
- **Cron重建：** `openclaw cron rm <id>` + `openclaw cron add`
- **Wiki同步：** 先查MEMORY.md，再查memory/YYYY-MM-DD.md，最后查wiki/
