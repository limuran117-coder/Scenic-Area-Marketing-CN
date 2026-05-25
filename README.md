# 🏗️ 建业电影小镇 AI 智能化营销系统
# JIANYE MOVIE TOWN AI-POWERED MARKETING SYSTEM

> **景区营销中心 × OpenClaw Agent × 数据驱动决策**  
> 一个由 AI Agent 全自动运行的景区数字化营销系统  
> An AI-agent-driven, fully automated digital marketing system for scenic tourism

---

## 📋 目录 | TABLE OF CONTENTS

- [🇨🇳 中文版](#-中文版)
- [🇬🇧 English Version](#-english-version)

---

## 🇨🇳 中文版

### 一、系统概述

建业电影小镇 AI 智能化营销系统是一套基于 OpenClaw Agent 框架、DeepSeek-V4 大模型驱动的全自动景区营销数据系统。系统实现从**数据采集 → 智能分析 → 决策建议 → 自动推送 → 知识沉淀**的完整闭环，无需人工干预。

**核心理念：** 让 AI 替代人工完成日常数据监测、竞品追踪、报告生成和知识管理，将营销团队从繁琐的日常工作中解放出来，专注于策略决策与内容创意。

### 二、系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                        🧠 AI AGENT 核心                           │
│              OpenClaw Runtime + DeepSeek-V4-Flash                 │
│          23个cron定时任务 | 飞书API推送 | CDP浏览器操控             │
└──────────────────────────────────────────────────────────────────┘
         ↙               ↘               ↘                ↘
┌─────────────┐ ┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
│  📊 数据采集   │ │  📱 内容洞察分析  │ │  ⚡ 自动执行   │ │  🗄️ 知识沉淀  │
├─────────────┤ ├─────────────────┤ ├─────────────┤ ├─────────────┤
│抖音指数日报    │ │文旅情报日报       │ │飞书卡片推送    │ │Obsidian Wiki │
│小红书日报      │ │竞品爆款拆解       │ │23个cron     │ │20竞品深度档案 │
│客流CSV同步     │ │竞品关键词分析     │ │CDP Cookie轮换│ │案例库10公式   │
│CDP浏览器采集   │ │竞品内容动态       │ │营销日历      │ │22个SOP       │
└─────────────┘ └─────────────────┘ └─────────────┘ └─────────────┘
```

#### 2.1 数据采集层

| 模块 | 频率 | 数据源 | 技术实现 |
|------|:----:|--------|----------|
| 抖音指数日报 | 每日10:30 | 抖音创作者平台·我的订阅页 | `douyin_index_v9.py` Playwright脚本 + CDP浏览器双通道 |
| 小红书日报 | 每日10:00 | 小红书灵犀后台 + 搜索结果页 | CDP浏览器直连 + Cookie自动轮换 |
| 文旅情报日报 | 每日13:00 | 百度搜索 + 微博热搜 + 行业新闻 | `web_search` 工具 + 多源聚合 |
| 客流数据同步 | 自动检测 | 桌面CSV文件 | `sync_obsidian_daily.py` CSV解析 + 增量更新 |

> **技术亮点：** 抖音指数采集采用 **Playwright脚本 + CDP浏览器双通道** 降级机制——脚本首选项，CDP人工采集为兜底，确保数据采集零中断。

#### 2.2 内容洞察层

**专有的决策判断框架**：每份日报/周报输出均包含以下结构化判断层：

| 判断维度 | 说明 | 示例 |
|----------|------|------|
| 🎯 **影响等级** | 高/中/低/噪音 | 高 — 竞品重大营销动作 |
| 💡 **建议动作** | 跟风/借势/警惕/忽略 | 跟风 — 立即启动同类型活动 |
| ⏰ **执行窗口** | 今天/本周/不紧急 | 今天 — 热搜窗口仅48小时 |
| ⚠️ **不做代价** | 错过会损失什么 | 错过夏季夜经济峰值期 |

**决策简报格式**（D序列）：
```
D<序号> | 1句标题
├─ 简单理解：一句话解释
├─ 做错风险：不执行的后果
├─ 推荐+理由：具体建议 + 置信度评分
└─ 利弊：收益 vs 成本
```

#### 2.3 自动执行层

系统运行在 Mac Mini 上，通过 OpenClaw 的 cron 调度引擎执行 23 个定时任务，日均 API 调用约 20 万 tokens。

| 时段 | 任务 | 执行说明 |
|:----:|------|---------|
| 08:00 | CDP Cookie同步 | 从专属浏览器提取抖音/小红书/微博Cookie |
| 08:00 | 营销日历(周一) | 生成本周内容排期+竞品预警+节假日借势 |
| 10:00 | 小红书日报 | 品牌五维数据+竞品关键词+官方账号分析 |
| 10:30 | 抖音指数日报 | 8景区搜索/综合指数+日环比+异动标注 |
| 13:00 | 文旅情报日报 | 竞品动态+政策资本+舆情预警+决策判断 |
| 15:00 | 竞品爆款拆解 | 抖音热搜+小红书爆款+微博热点深度拆解 |
| 16:00 | 竞品关键词深度分析 | 轮换制深度分析（已完成14/21个景区） |
| 18:00 | 竞品内容动态 | 竞品最新节目/活动/营销动作追踪 |
| 20:00 | 案例库更新 | 全国景区案例库周度更新 |
| 21:00 | 营销效果归因 | 归因模型追踪 |
| 22:00 | 每日复盘整合 | 全任务执行回顾+学习闭环 |
| 周二9:30 | 周度客流洞察 | 客流对比+渠道拆分+营收分析 |
| 周日 | 竞争格局报告 | 格局变化+准确率复盘+规则更新 |

所有日报通过 `send_feishu_card.py` 以飞书 interactive 卡片格式推送至电影小镇飞书群。

#### 2.4 知识沉淀层

基于 Obsidian 的知识管理系统（karpathy-wiki 模式），实现 **概念层 + 实体层 + 来源层** 三层知识抽象：

```
wiki/
├── 电影小镇/                  ← 核心业务层
│   ├── 基础档案.md             - 景区基本信息/年度目标(153万/1.2亿)
│   ├── 战略框架.md             - SWOT分析/渠道策略
│   ├── 历史数据/               - 2023-2026客流/营收/规律洞察
│   │   ├── 数据.md              ✅ YTD 656,067 (42.9%)
│   │   └── 规律洞察.md         - 三峰值 + 德化街悖论
│   ├── 演出节目/               - 穿越德化街六年数据
│   ├── 运营方法/               - 抖音/小红书运营SOP
│   └── 运营规划/               - 夏季方案/节假日排期
│
├── 竞品分析/                  ← 竞品追踪层
│   ├── 竞品深度档案/           - 20个全国景区深度分析
│   ├── 追踪数据/              - 抖音/小红书日常追踪
│   ├── 抖音指数追踪.md         - 8景区连续日环比
│   └── 关键词池状态.md         - 断点续做机制
│
├── 全国景区案例库/             ← 知识资产层
│   ├── index.md               - 10条爆款公式索引
│   ├── 第22周更新记录          - 20个入库案例
│   └── *(按周归档的拆解案例)*
│
├── SOP/                       ← 操作手册层
│   ├── 抖音指数日报.md          - 日报生成SOP
│   ├── 竞品深度分析流程.md       - 四平台采集SOP
│   ├── 每日任务总览.md          - 所有cron任务索引
│   └── *(共22个SOP文件)*
│
├── concepts/                  ← 概念层(知识抽象)
│   └── 演艺景区/内容爆款规律/平台算法...
├── entities/                  ← 实体层(具体对象)
│   └── 建业电影小镇/万岁山/清明上河园...
├── sources/                   ← 来源层(数据溯源)
│   └── 穿越德化街数据分析/抖音指数追踪...
└── AI系统搭建全景展示.md       ← 分享文稿
```

### 三、核心优势

#### 3.1 真正的「数据驱动」
不是人工看数据后凭经验拍脑袋，而是 AI 自主完成**数据采集 → 解读 → 决策建议**的全链路。每份报告都附带置信度评分，让决策有据可依。

#### 3.2 24/7 全自动运行
23个 cron 任务从早 8 点到晚 10 点自动执行，节假日无休。日均产生 6-8 份结构化决策简报，全部自动推送到飞书群。

#### 3.3 知识持续沉淀
每篇分析报告、每个竞品档案、每份决策判断都会被自动归档到 Obsidian Wiki，形成可检索、可复用的景区营销知识资产。

#### 3.4 人性化判断框架
AI 不只是一个"报告生成器"，它内置了业务判断逻辑——影响等级、建议动作、执行窗口、不做代价——让建议可执行、可衡量。

#### 3.5 容错降级机制
数据采集采用**双通道设计**（Playwright 脚本 + CDP 浏览器直连），任一通道失效自动降级，确保日报不中断。

### 四、当前效果

| 指标 | 数值 |
|------|:----:|
| 🎯 年度客流目标 | **153万**（截止5/17完成**65.6万 / 42.9%**） |
| 📊 每日追踪景区 | **8个**（建业电影小镇+7核心竞品） |
| 📁 竞品深度档案 | **20个**全国景区全覆盖 |
| 📝 爆款案例库 | **10条爆款公式 + 20个真实案例** |
| 📋 SOP规范 | **22个**标准化操作手册 |
| ⏰ 自动化任务 | **23个**cron定时任务 |
| 🔄 连续运行天数 | **30+天**无人工干预 |
| 📈 竞争格局预测准确率 | **W21达80%**（连续4周提升: 60%→65%→70%→80%） |

### 五、技术栈

| 层级 | 技术/工具 |
|------|-----------|
| AI框架 | OpenClaw Runtime + Agent Skills |
| 大模型 | DeepSeek-V4-Flash |
| 数据采集 | Python Playwright + CDP Protocol |
| 推送渠道 | 飞书Bot API (interactive card, schema 2.0) |
| 知识管理 | Obsidian Wiki (karpathy-wiki模式) |
| 任务调度 | OpenClaw cron (23个isolated session) |
| 运行环境 | macOS 26.4 on Mac Mini (ARM64) |
| 版本控制 | Git + GitHub |

### 六、使用方式

系统完全自动化运行，无需人工操作。如需查看状态，可：

1. **查看飞书群** → 电影小镇群（oc_2581...）每日自动推送所有日报
2. **打开 Obsidian** → 查看竞品档案/案例库/历史数据
3. **GitHub 仓库** → `Scenic-Area-Marketing-CN` 查看代码和Wiki

---

## 🇬🇧 English Version

### 1. System Overview

Jianye Movie Town AI-Powered Marketing System is a fully automated scenic marketing data system built on OpenClaw Agent framework and driven by DeepSeek-V4 LLM. The system achieves a complete closed loop of **Data Collection → Intelligent Analysis → Decision Recommendations → Automated Delivery → Knowledge Archiving** — entirely without human intervention.

**Core Philosophy:** Replace manual daily data monitoring, competitor tracking, report generation, and knowledge management with AI agents, freeing the marketing team to focus on strategic decisions and content creation.

### 2. System Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                      🧠 AI AGENT CORE                             │
│           OpenClaw Runtime + DeepSeek-V4-Flash                    │
│        23 cron tasks | Feishu Bot API | CDP Browser Control       │
└──────────────────────────────────────────────────────────────────┘
         ↙               ↘               ↘                ↘
┌─────────────┐ ┌─────────────────┐ ┌─────────────┐ ┌─────────────┐
│  📊 DATA     │ │  📱 CONTENT     │ │  ⚡ EXECUTION│ │  🗄️ KNOWLEDGE│
│  COLLECTION  │ │  INSIGHT        │ │  LAYER      │ │  LAYER      │
├─────────────┤ ├─────────────────┤ ├─────────────┤ ├─────────────┤
│Douyin Index  │ │Travel Intel     │ │Feishu Card  │ │Obsidian Wiki│
│Xiaohongshu   │ │Competitor Hits  │ │Push (23 cron)│ │20 Profiles   │
│Passenger CSV │ │Keyword Analysis │ │Cookie Mgmt  │ │10 Formulas   │
│CDP Browser   │ │Content Tracking │ │Calendar     │ │22 SOPs       │
└─────────────┘ └─────────────────┘ └─────────────┘ └─────────────┘
```

**Key System Features:**

| Feature | Implementation | Benefit |
|---------|---------------|---------|
| **Dual-Channel Data Collection** | Playwright script + CDP direct browser access | Zero downtime on data collection |
| **Decision Framework** | Impact level/Action/Window/Risk per report | Executable, measurable recommendations |
| **Knowledge Graph** | 3-layer abstraction (concepts→entities→sources) | Searchable, reusable marketing asset |
| **Graceful Degradation** | Auto-fallback between script/CDP/estimation | Uninterrupted daily reports |
| **Competitive Intelligence** | 20 deep-profile archives + daily tracking | Full market landscape awareness |

### 3. Current Results

| Metric | Value |
|--------|:-----:|
| 🎯 Annual Visitor Target | **1.53M** (656K achieved / 42.9% as of May 17) |
| 📊 Daily Tracked Venues | **8** (Movie Town + 7 core competitors) |
| 📁 Competitor Profiles | **20** national scenic spots covered |
| 📝 Case Library | **10 viral formulas + 20 real cases** |
| 📋 SOP Documents | **22** standardized operation manuals |
| ⏰ Automated Tasks | **23** cron jobs |
| 🔄 Days Running | **30+ days** without human intervention |
| 📈 Weekly Accuracy Rate | **W21: 80%** (4 consecutive weeks improving: 60%→65%→70%→80%) |

### 4. Technology Stack

| Layer | Technology |
|-------|-----------|
| AI Framework | OpenClaw Runtime + Agent Skills |
| LLM | DeepSeek-V4-Flash |
| Data Collection | Python Playwright + CDP Protocol |
| Push Channel | Feishu Bot API (interactive card, schema 2.0) |
| Knowledge Mgmt | Obsidian Wiki (karpathy-wiki pattern) |
| Task Scheduler | OpenClaw cron (23 isolated sessions) |
| Runtime | macOS 26.4 on Mac Mini (ARM64) |
| Version Control | Git + GitHub |

---

*由 AI Agent 自动维护 · Automatically maintained by AI Agent*  
*最后更新 · Last updated: 2026-05-25*  
*景区营销中心 · Scenic Marketing Center*
