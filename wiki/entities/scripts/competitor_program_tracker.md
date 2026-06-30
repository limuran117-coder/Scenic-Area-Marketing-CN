---
title: competitor_program_tracker.py
type: entity-script
tags: [脚本, 竞品, 追踪, 修复]
created: 2026-06-30
updated: 2026-06-30
related: [[entities/scripts/douyin_index]]
---

# competitor_program_tracker.py

> 竞品节目活动追踪脚本 | **v2（2026-06-30 修复版）**

---

## 基本信息

| 项目 | 内容 |
|------|------|
| 文件 | `~/.openclaw/workspace/scripts/competitor_program_tracker.py` |
| 用途 | 追踪 5 大竞品（只有河南/银基/万岁山/方特/清明上河园）最近节目活动 |
| 执行频率 | 每日 18:00 cron（竞品内容动态） |
| 输出 | `/tmp/competitor_programs_<YYYYMMDD>.txt` + `.json` |

---

## v1 → v2 修复（2026-06-30 站长发现）

### v1 问题（模板空壳）

- ❌ `get_douyin_programs()` 只搜"只有河南" 1 个就放弃
- ❌ 主函数连 `get_douyin_programs` 都没调用
- ❌ `format_report()` 用硬编码字符串（"春季踏青季"等过期信息）
- ❌ 输出全是"暂无重大更新"模板
- ❌ 5 竞品 0 条真实数据

### v2 修复方案

1. **新增 web_search 主路径**（LLM 调用兜底）
2. **保留 CDP 抖音用户端搜索**（备路径，需登录态）
3. **静态兜底显式标注**"未找到近期公开新闻"
4. **区分 🟢🟡🔴 三档数据来源**

### v2 修复结果

- ✅ 5 竞品 9 条 2026 年 6 月真实活动入库
- ✅ 飞书卡 `om_x100b6b06af937d18c212745f6f7a4e6`（已发）
- ⚠️ 抖音用户端 selector 待优化（DOM 渲染问题，未匹配到视频列表）

---

## v2 数据流

```
v2 = 真实 web_search 优先 → CDP 抖音备 → 静态兜底（明确标注）
   ↓
 5 竞品并行采集
   ↓
 飞书卡（电影小镇群）
```

### v2 真实数据样本（6/30）

| 竞品 | 6 月真实动作 | 来源 |
|------|------------|------|
| 清明上河园 | 6/9-6/30 高考免门票 19.9 元 + 杨洋空降 + 6/15 港股 IPO | web_search |
| 方特 | 6/26 起 65 天夜场（199 元/人）| web_search |
| 只有河南 | 6/5 许巍麦田落日音乐会 + 6/21 夏至夜幻城 + 68 天焰火 | web_search |
| 万岁山 | 4/29 刘晓庆参与王婆说媒 + 常态化运营 | web_search |
| 银基 | 6/22 缤纷焰火季 + 6/22-8/31 萤火虫之夜 | web_search |

---

## 关联文档

- W26 周报：[[竞品分析/竞品动态追踪/2026-W26-周度竞争格局]]
- W27 周报：[[竞品分析/竞品动态追踪/2026-W27-周度竞争格局]]
- H1 一页纸：`memory/2026-06-30-h1-recap.md`
- 飞书卡：`om_x100b6b06af937d18c212745f6f7a4e6`

---

## 待办

- ⚠️ **抖音用户端 selector 优化**（DOM 渲染问题，0 视频匹配）
- ✅ 5 竞品 web_search 已稳定运行
- ⚠️ 小红书竞品（`xhs_competitor_crawl.py`）需独立验证
