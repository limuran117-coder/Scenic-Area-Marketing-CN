---
title: xiaohongshu_crawl.py
type: entity-script
tags: [脚本, 小红书, 灵犀, 采集]
created: 2026-06-30
updated: 2026-06-30
related: [[entities/scripts/douyin_index]]
---

# xiaohongshu_crawl.py

> 小红书灵犀数据采集脚本

---

## 基本信息

| 项目 | 内容 |
|------|------|
| 文件 | `~/.openclaw/workspace/scripts/xiaohongshu_crawl.py` |
| 用途 | 小红书关键词搜索采集 |
| 执行频率 | 按需 |
| 输出 | `/tmp/xiaohongshu_<关键词>.json` |

---

## 当前状态（2026-06-30）

### ⚠️ 登录态问题

- 灵犀后台 `idea.xiaohongshu.com/idea/welcome/index` **not_logged_in 连续 3+ 日**（6/17-6/19 起）
- 6/30 采集 `xiaohongshu_建业电影小镇.json` 返回 `search_box_not_found` 错误
- **需站长人工扫码登录**

### 6/30 验证结果

| 测试项 | 结果 |
|--------|------|
| CDP 连接 | ✅ 成功 |
| explore 页加载 | ✅ 成功 |
| 搜索框 | ❌ 未找到（未登录） |
| 数据采集 | ❌ 失败 |

---

## Cookie 健康度

- **文件**：`/tmp/xiaohongshu_cookies.json`（4.5KB，6/30 08:05 写过）
- **代理**：127.0.0.1:7897 ✅ LISTEN

---

## 恢复步骤

1. 站长打开 `https://idea.xiaohongshu.com/idea/welcome/index`
2. 扫码登录（账号：建业电影小镇官方 ID:530883）
3. 等待 cookie 同步回 `/tmp/xiaohongshu_cookies.json`
4. 重新跑 `xiaohongshu_crawl.py`

---

## 关联文档

- 灵犀数据可用性：`wiki/行业知识/小红书灵犀数据可用性状态表.md`
- 灵犀深度探索：`wiki/行业知识/小红书灵犀深度探索报告.md`
- Cookie 恢复 SOP：`wiki/SOP/Cookie恢复与人工介入SOP.md`
