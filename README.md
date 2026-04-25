# 🎬 Scenic Area Marketing Agent

> AI驱动的景区全域营销运营系统 | 数据驱动 × 知识沉淀 × 流程自动化

**[English](#english) | [中文说明](#中文说明)**

---

# English

## What This Project Does

An AI-powered autonomous agent that manages the entire marketing operations for **Jianye Film Town** (建业电影小镇) — a performing arts-themed scenic area in Zhengzhou, China — covering Douyin, Xiaohongshu, competitor monitoring, passenger flow analysis, and daily automated reporting.

**Annual Goal (2026)**: 1.53 million visitors · ¥112M revenue

---

## Why This Project Exists

Most scenic area marketing teams operate reactively: they post content, manually check data, and learn from past campaigns with no systematic knowledge retention.

This project is different. It runs **proactively**, 24/7, with:

- **Scheduled automation** — Every critical task fires on time without human intervention
- **Knowledge compounding** — Every insight is stored and linked, not forgotten
- **Data-driven decisions** — Daily metrics inform strategy, not gut feelings
- **Competitor intelligence** — 8 competitors tracked daily with standardized deep-dive reports

---

## Core Advantages

### 1. karpathy-wiki Knowledge Graph

Unlike traditional wikis that accumulate documents you never read, this system is structured as a **compounding knowledge base** (karpathy-wiki standard):

```
knowledge layer (abstract) ← business layer (raw data)
```

| Layer | Purpose | Example |
|-------|---------|---------|
| `concepts/` | Why things work | 「情绪营销公式」— why suspense hooks go viral |
| `entities/` | What things are | 「万岁山武侠城」— competitor profile |
| `sources/` | Source summaries | 「穿越德化街数据分析」— key data points |
| `queries/` | Valuable Q&A | 「抖音vs小红书差异」— when to use which platform |

**Weekly INGEST**: Every Sunday, new insights are distilled into the knowledge layer, so the system gets smarter over time.

### 2. SOP-Driven Execution

Every task has a dedicated SOP that survives session restarts. When a cron job fires, it reads the SOP first and executes precisely — no deviation, no forgotten steps.

**13 Standardized SOPs**:
- 抖音指数日报 (Douyin Index Daily)
- 小红书日报 (Xiaohongshu Daily)
- 竞品关键词深度分析 (Competitor Keyword Deep Dive)
- 竞品内容动态 (Competitor Content Tracking)
- 全国爆款拆解 (Nationwide Viral Content Analysis)
- 文旅热点追踪 (Travel Industry Hotspots)
- 每日复盘整合 (Daily Review)
- 周度客流洞察 (Weekly Passenger Insights)
- 客流数据Wiki同步 (Passenger Data Sync)
- 案例库更新 (Case Library Update)
- Wiki健康检查 (Wiki LINT)
- 代码库漂移检查 (Codebase Drift Check)
- 系统健康检查 (System Health Check)

### 3. Multi-Platform Data Collection

**Douyin (抖音)**
- Search Index — tracks 8 competitors daily
- Synthesis Index — content热度 + interaction + search
- Keyword Deep Dive —关联词TOP10 + 人群画像
- Automated collection via Playwright + CDP browser

**Xiaohongshu (小红书)**
- 灵犀后台 — brand search volume, related terms, content trends
- Note tracking — new posts, engagement metrics
- Crowd profiling — age/gender/geography

### 4. Competitor Intelligence System

**8 Core Competitors Tracked**:
- 万岁山武侠城 (Wanshu Mountain)
- 清明上河园 (Qingming Riverside Park)
- 只有河南 (Only Henan)
- 银基动物王国 (Yinji Animal Kingdom)
- 郑州方特欢乐世界 (Zhengzhou Fantawild)
- 郑州海昌海洋公园 (Zhengzhou Haichang Ocean Park)
- 只有红楼梦 (Only Dream of Red Mansions)
- 大唐不夜城 (Tang Dynasty Night City)

**21 keyword pool** for nationwide trend monitoring.

Each competitor deep-dive covers: Douyin index · Xiaohongshu data · Baidu search · crowd profiling · content strategy · actionable insights.

### 5. Data-Driven Passenger Flow Management

**Passenger flow data architecture**:
- Daily CSV sync → Wiki → Feishu card
- 散客 vs 渠道 split analysis
- Historical comparison (2023–2026)
- Weather correlation
- Seasonal peak modeling (春节/暑期/国庆)

---

## Automated Reports Schedule

| Time | Report | Channel |
|------|--------|---------|
| 08:00 | Douyin Index Daily | Feishu Group |
| 10:00 | Xiaohongshu Daily | Feishu Group |
| 10:00 | Travel Industry Hotspots | Feishu Group |
| 15:00 | Competitor Keyword Deep Dive | DM |
| 18:00 | Competitor Content Tracking | Feishu Group |
| 21:00 | Nationwide Viral Content Analysis | Feishu Group |
| 22:00 | Daily Review & Integration | DM |
| Mon 09:00 | Weekly Passenger Insights | Feishu Group |

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| AI Agent | OpenClaw + MiniMax-M2.7 |
| Knowledge Base | Obsidian Vault + karpathy-wiki |
| Browser Automation | CDP (Chrome DevTools Protocol) |
| Data Collection | Playwright + custom scripts |
| Instant Messaging | Feishu (Lark) Bot API |
| Scheduled Tasks | Cron (OpenClaw built-in) |
| Memory System | Multi-tier: daily logs → weekly dreaming → long-term MEMORY.md |
| Code Repository | GitHub (auto-sync on Sundays) |

---

## Repository Structure

```
.
├── wiki/                          # Knowledge base (Obsidian-compatible)
│   ├── concepts/                  # 11 knowledge concepts
│   ├── entities/                  # 10 entities (scenic areas + platforms)
│   ├── sources/                   # 5 source document summaries
│   ├── queries/                   # 4 valuable Q&A archives
│   ├── 电影小镇/                  # Core business data (untouched)
│   ├── 竞品分析/                  # Daily competitor tracking
│   ├── 全国景区案例库/             # Weekly case studies
│   ├── 行业知识/                  # Industry knowledge
│   ├── SOP/                       # 13 standardized SOPs
│   └── 技术配置/                  # Browser + script configs
├── scripts/                       # Automation scripts
│   ├── douyin_index_v9.py        # Douyin index collection
│   ├── xiaohongshu_crawl.py      # Xiaohongshu collection
│   └── send_feishu_card.py       # Feishu card sender
├── memory/                        # AI memory & session logs
├── README.md                      # This file
└── LICENSE                        # MIT
```

---

## karpathy-wiki Knowledge Layer (Detailed)

The knowledge layer is the system's "brain" — separate from the business execution layer:

**concepts/** — Abstract principles
- 演艺景区 (Performing Arts Scenic Areas)
- 内容爆款规律 (Viral Content Patterns)
- 情绪营销 (Emotional Marketing)
- 季节性客流规律 (Seasonal Passenger Flow Patterns)
- 景区营销漏斗 (Marketing Funnel)
- 景区抖音运营 (Douyin Operations for Scenic Areas)
- 景区小红书运营 (Xiaohongshu Operations for Scenic Areas)
- 内容发布节奏 (Content Publishing Cadence)
- ROI分析 (ROI Analysis)
- 景区类型 (Scenic Area Types)
- 平台算法规则 (Platform Algorithm Rules)

**entities/** — Concrete entities
- 建业电影小镇 (Jianye Film Town)
- 7 竞品 (7 competitors)
- 抖音平台 (Douyin platform)
- 小红书平台 (Xiaohongshu platform)

**sources/** — Source document summaries
- 穿越德化街数据分析 (Through Dehua Street Data Analysis)
- 抖音指数追踪日报 (Douyin Index Daily Report)
- 竞品深度档案 (Competitor Deep Dive Archives)
- 客流营收历年分析 (Passenger Flow & Revenue Historical Analysis)

**queries/** — Valuable Q&A archives
- Wiki重组决策 (Wiki Restructuring Decision)
- 知识层与业务层关系 (Knowledge Layer vs Business Layer)
- 抖音与小红书平台差异 (Douyin vs Xiaohongshu Platform Differences)
- 旧目录与知识层重叠分析 (Old Directory vs Knowledge Layer Overlap Analysis)

---

## Competitive Advantages Summary

| Advantage | Detail |
|-----------|--------|
| **Autonomous Operation** | 13 cron jobs run daily without human intervention |
| **Knowledge Compounding** | karpathy-wiki ensures insights accumulate and compound |
| **Data-Driven** | All decisions backed by real-time platform data |
| **Standardized SOPs** | Every task has a precise, version-controlled playbook |
| **Multi-Platform** | Douyin + Xiaohongshu + Baidu + Feishu integrated |
| **Competitor Intelligence** | 8 competitors × 21 keywords, tracked daily |
| **Weekly INGEST** | Every Sunday, knowledge layer is refreshed and synced to GitHub |
| **Historical Depth** | 2023–2026 passenger flow data + performing arts analysis |

---

---

# 中文说明

## 这个项目做什么

**建业电影小镇 AI 营销运营系统** — 一个覆盖抖音、小红书、竞品监控、客流分析、日报自动化的全链路AI运营助手。

**年度目标（2026年）**：客流153万 · 营收1.12亿

---

## 核心优势

### 1. karpathy-wiki 知识图谱

传统 Wiki 积累文档但无人阅读，本系统按 karpathy-wiki 标准构建**可化合的知识库**：

```
知识抽象层（concept/entity/source/query）← 业务执行层（每日数据/报告）
```

| 层级 | 作用 | 示例 |
|------|------|------|
| `concepts/` | 为什么 | 「情绪营销公式」— 情绪悬念为什么能爆 |
| `entities/` | 是什么 | 「万岁山武侠城」— 竞品完整画像 |
| `sources/` | 源文档摘要 | 「穿越德化街数据分析」— 关键数据提炼 |
| `queries/` | 有价值的问答 | 「抖音vs小红书差异」— 什么场景用哪个平台 |

**每周 INGEST**：每周日将新知识提炼到知识层，系统越用越聪明。

### 2. SOP 驱动执行

每个任务都有专属 SOP，cron 触发时先读 SOP 再执行，精确无误。

**13 个标准化 SOP**：
- 抖音指数日报 · 小红书日报 · 竞品关键词深度分析 · 竞品内容动态
- 全国爆款拆解 · 文旅热点追踪 · 每日复盘整合 · 周度客流洞察
- 客流数据Wiki同步 · 案例库更新 · Wiki健康检查 · 代码库漂移检查 · 系统健康检查

### 3. 多平台数据采集

**抖音**：搜索指数/综合指数/关联词TOP10/人群画像（CDP浏览器+Playwright）
**小红书**：灵犀后台/笔记追踪/收藏数/互动总量（五维度日报格式）

### 4. 竞品智能系统

**8个核心竞品**：万岁山/清明上河园/只有河南/银基动物王国/郑州方特/郑州海昌/只有红楼梦/大唐不夜城
**21个关键词池**：覆盖全国热点景区
**四平台深度分析**：百度/抖音/灵犀/小红书搜索

### 5. 客流数据驱动决策

- 每日CSV同步Wiki → 飞书卡片
- 散客/渠道拆分模型
- 历年对比（2023-2026）
- 天气相关性
- 季节峰值模型（春节/暑期/国庆）

---

## 自动化报告排期

| 时间 | 报告 | 发送渠道 |
|------|------|---------|
| 08:00 | 抖音指数日报 | 飞书群 |
| 10:00 | 小红书日报 | 飞书群 |
| 10:00 | 全国文旅热点 | 飞书群 |
| 15:00 | 竞品关键词深度 | 私信 |
| 18:00 | 竞品内容动态 | 飞书群 |
| 21:00 | 全国爆款拆解 | 飞书群 |
| 22:00 | 每日复盘整合 | 私信 |
| 周一09:00 | 周度客流洞察 | 飞书群 |

---

## 核心竞品关键词（8个）

建业电影小镇 · 万岁山武侠城 · 清明上河园 · 只有河南戏剧幻城 · 郑州方特欢乐世界 · 郑州海昌海洋公园 · 银基动物王国 · 只有红楼梦戏剧幻城

---

## 技术栈

| 组件 | 技术 |
|------|------|
| AI Agent | OpenClaw + MiniMax-M2.7 |
| 知识库 | Obsidian Vault + karpathy-wiki |
| 浏览器自动化 | CDP (Chrome DevTools Protocol) |
| 数据采集 | Playwright + 自定义脚本 |
| 消息推送 | 飞书 Bot API |
| 定时任务 | Cron (OpenClaw 内置) |
| 记忆系统 | 多层：每日日志 → 周度梦境 → 长期记忆MEMORY.md |
| 代码仓库 | GitHub（每周日自动同步） |

---

## 数据架构

```
数据来源
├── 抖音创作服务平台（搜索/综合指数）
├── 小红书灵犀后台（搜索/内容/趋势）
├── 百度搜索（运营/媒体报道）
├── 桌面CSV（每日客流）
└── 飞书多维表格（协同）

       ↓ AI Agent 处理

知识沉淀
├── concepts/（提炼概念）
├── entities/（实体画像）
├── sources/（数据摘要）
└── queries/（问答归档）

       ↓ 飞书推送

报告输出
├── 抖音指数日报（08:00）
├── 小红书日报（10:00）
├── 文旅热点（10:00）
├── 竞品内容动态（18:00）
├── 全国爆款拆解（21:00）
└── 周度客流洞察（周一09:00）
```

---

## Wiki 知识层详情

**concepts/（11个概念）**
演艺景区 · 内容爆款规律 · 情绪营销 · 季节性客流规律 · 景区营销漏斗 · 景区抖音运营 · 景区小红书运营 · 内容发布节奏 · ROI分析 · 景区类型 · 平台算法规则

**entities/（10个实体）**
电影小镇 + 7个竞品 + 抖音平台 + 小红书平台

**sources/（5个源文档摘要）**
穿越德化街数据分析 · 抖音指数追踪日报 · 竞品深度档案 · 客流营收历年分析 · Wiki重组记录

**queries/（4个问答归档）**
Wiki重组决策 · 知识层与业务层关系 · 抖音与小红书平台差异 · 旧目录重叠分析

---

## 竞争优势总结

| 优势 | 说明 |
|------|------|
| **全自动化运营** | 13个cron任务全天候自动执行，无需人工干预 |
| **知识化合** | karpathy-wiki确保洞察积累而非遗忘 |
| **数据驱动决策** | 所有策略基于实时平台数据，非经验主义 |
| **标准化SOP** | 每个任务都有精确的版本控制操作手册 |
| **多平台整合** | 抖音+小红书+百度+飞书一体化 |
| **竞品智能** | 8竞品×21关键词，每日追踪 |
| **每周INGEST** | 每周日知识层刷新并同步GitHub |
| **历史深度** | 2023-2026客流数据+演出分析 |

---

## License

MIT License

---

> Built with [OpenClaw](https://github.com/openclaw/openclaw) · Powered by [MiniMax](https://minimax.io/) · 景区营销中心 AI Agent
