# Skill使用指南（2026-06-06重写）

## 当前架构

```
主Agent 李涯（电影小镇运营助手）
├── 8个cron日常任务（定时触发）
├── Playwright脚本（抖音/小红书数据采集）
├── 质量保障层（采集前校验 + 采集后审计）
└── 按需技能（研究/分析/可视化）
```

**核心变化（vs 旧版）：** 不再使用子Agent模式，所有任务由主Agent通过cron直接执行。

---

## 日常任务流水线

```
data-integrity-check → daily-task-template → 执行 → task-audit
     (采集前)              (标准化)                (采集后)
```

### 每个cron任务的标准流程

| 阶段 | 技能/工具 | 作用 |
|------|----------|------|
| ① 前置校验 | data-integrity-check | cookie/代理/文件是否就绪 |
| ② 数据采集/分析 | Playwright脚本 + skill-router | 按意图匹配执行方式 |
| ③ 判断层输出 | daily-task-template | 🎯💡⚠️ 三件套 |
| ④ 卡片发送 | 飞书卡片格式 | 标准schema 2.0 |
| ⑤ 结果审计 | task-audit | 送达确认+数据质量+异常标记 |

---

## 技能分类与使用

### 🔴 质量保障层（每次任务必用）

| 技能 | 时机 | 职责 |
|------|------|------|
| **data-integrity-check** | 任务执行前 | 7项A级硬检查（cookie/代理/文件） |
| **task-audit** | 任务执行后 | 7项标准审计+全局汇总 |
| **daily-task-template** | 任务编写/修改时 | 套用A/B/C类模板确保格式统一 |

### 🟡 数据采集层

| 技能/工具 | 适用场景 | 方式 |
|-----------|---------|------|
| **Playwright脚本** | 抖音指数/小红书采集 | `douyin_index.py`, `xiaohongshu_crawl.py` |
| **browser-automation技能** | 浏览器操作规范 | 技能文档指导Playwright使用 |
| **spike（系统技能）** | 新数据源验证 | `.tmp/openclaw-spikes/` 快速原型 |

### 🟢 分析洞察层

| 技能 | 适用任务 | 说明 |
|------|---------|------|
| **competitor-analyst** | 竞品关键词/内容/爆款分析 | 结构化竞品分析框架 |
| **ai-researcher** | 文旅政策/行业趋势/深度研究 | 深度调研 |
| **skill-router** | 意图识别与任务路由 | 始终激活 |

### 🔵 知识管理层

| 技能 | 用途 | 触发条件 |
|------|------|---------|
| **karpathy-wiki** | 知识库INGEST/QUERY/LINT | raw/有新文件时提示ingest |
| **karpathy-guidelines** | 编码/决策四大原则 | 重大修改前必读 |
| **llm-wiki-maintainer** | Wiki维护辅助 | 备用 |

### ⚪ 系统维护层

| 技能 | 用途 | 频率 |
|------|------|------|
| **system-metabolism** | 自动体检+修剪+报告 | 周日09:00 |
| **weather（系统技能）** | 天气查询 | 日报附加 |

---

## 浏览器使用规范

```
CDP端口：18800
连接方式：target=host（统一）
自动化：Playwright脚本（douyin_index.py等）
禁止：browser-use CLI操作专属Chrome标签页
例外：临时性/新平台的复杂探索任务可用browser-use
```

---

## 8个日常Cron任务

| 时间 | 任务 | 类型 | 核心技能 |
|------|------|------|---------|
| 10:00 | 全国景区动态 | B-分析 | competitor-analyst |
| 10:30 | 抖音指数日报 | A-采集 | Playwright脚本 |
| 14:00 | 文旅政策与资本 | B-分析 | ai-researcher |
| 15:00 | 竞品关键词深度分析 | B-分析 | competitor-analyst |
| 18:00 | 竞品内容动态 | B-分析 | competitor-analyst |
| 21:00 | 全国爆款拆解 | B-分析 | competitor-analyst |
| 22:00 | 每日复盘整合 | C-汇总 | task-audit |
| 周日09:00 | 系统代谢 | 维护 | system-metabolism |

---

## 能力边界

### 已验证可用
- Playwright数据采集 ✅
- 飞书卡片发送 ✅
- GitHub版本控制 ✅
- 天气查询 ✅
- ffmpeg视频帧提取 ✅
- Python调试（pdb/debugpy）✅
- diffs工具 ✅
- gh-issues（gh CLI可用）✅

### 按需启用
- **diagram-maker**（系统技能）：SVG/HTML图表，无依赖，即开即用。适用季度报告/竞品可视化
- fireworks-tech-graph（需rsvg-convert，未安装，用diagram-maker替代）
- nano-pdf（需 `uv tool install nano-pdf`，PDF编辑，暂不需要）
- feishu-doc（需验证飞书App凭证，可持久化存档日报，团队有需求时试点）
- model-usage（需codexbar）
- agentgo-browser（需注册云端浏览器）
- 1password CLI（已安装，需配置登录）
- healthcheck（安全审计，按需运行）

### 不适用
- Claude API相关技能（仅使用DeepSeek模型）
- React/前端设计技能（无前端项目）
- 微信小程序技能（无相关项目）

---

## 维护记录

- 2026-06-06 #2: 周度技能探索 — 评估 taskflow(不可用,开发者API) / diagram-maker(✅即开即用) / feishu-doc(需凭证验证) / nano-pdf(需安装CLI) / canvas/summarize/gog/model-usage(低价值)。新增diagram-maker为按需技能。
- 2026-06-06 #1: 周度技能探索 — 新增python-debugpy/diffs/gh-issues/1password/healthcheck评估
- 2026-06-06: 完全重写，反映当前cron+Playwright架构
- 2026-04-11: 旧版初稿（子Agent架构，已废弃）
