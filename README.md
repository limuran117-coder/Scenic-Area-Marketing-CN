# Scenic-Area-Marketing-CN
## AI-Powered Scenic Tourism Marketing System — Build by OpenClaw Agent

---

## 📋 TABLE OF CONTENTS

- [🇬🇧 ENGLISH](#-english-version)
- [🇨🇳 中文版](#-中文版)

---

# 🇬🇧 ENGLISH VERSION

## 1. WHAT IS THIS PROJECT?

**Scenic-Area-Marketing-CN** is a production-grade, fully automated scenic marketing intelligence system built on the [OpenClaw AI Agent framework](https://github.com/openclaw/openclaw). It runs 24/7 on a Mac Mini, autonomously collecting data from 8+ platforms, generating structured competitive intelligence reports, pushing decision-grade insights to Feishu (飞书) group chats, and archiving everything into an Obsidian knowledge graph.

The system serves **Jianye Movie Town (建业电影小镇)**, a cultural-tourism scenic spot in Zhengzhou, Henan, China, with an annual visitor target of 1.53 million and revenue target of ¥120 million for 2026.

This is **not** a demo or prototype. It has been running continuously for 30+ days without human intervention, producing **6–8 actionable decision briefs daily**.

---

## 2. SYSTEM ARCHITECTURE

### 2.1 High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              🧠 AI AGENT CORE                                       │
│              OpenClaw Runtime · DeepSeek-V4-Flash · 23 Cron Tasks                    │
│                   Web Search · Memory · CDP Browser · Feishu API                     │
└─────────────────────────────────────────────────────────────────────────────────────┘
          │                             │                           │
          ▼                             ▼                           ▼
┌─────────────────────┐ ┌─────────────────────────────┐ ┌─────────────────────────┐
│    📊 DATA LAYER     │ │    🧠 INTELLIGENCE LAYER     │ │    ⚡ EXECUTION LAYER    │
├─────────────────────┤ ├─────────────────────────────┤ ├─────────────────────────┤
│ Douyin Index Tracker │ │ Decision Framework Engine    │ │ Feishu Card Pusher      │
│ Xiaohongshu Monitor  │ │ Competitive Intel Analysis   │ │ (send_feishu_card.py)   │
│ Weibo Hot Search     │ │ Trend & Anomaly Detection   │ │ Cron Job Scheduler      │
│ Baidu Search         │ │ Viral Content Deconstruction │ │ Cookie Rotation Manager  │
│ Passenger CSV Reader │ │ Weekly Pattern Forecasting   │ │ CDP Browser Control     │
│ CDP Cookie Manager   │ │ Learning Loop & Validation   │ │ Health Monitor          │
└─────────────────────┘ └─────────────────────────────┘ └─────────────────────────┘
          │                             │                           │
          └─────────────────────────────┼───────────────────────────┘
                                        ▼
                         ┌─────────────────────────────┐
                         │    📚 KNOWLEDGE LAYER        │
                         ├─────────────────────────────┤
                         │ Obsidian Wiki (3-Layer Abstraction) │
                         │  → Concepts / Entities / Sources     │
                         │  → 20 Competitor Profiles           │
                         │  → 10 Viral Formulas / 22 SOPs       │
                         │  → Historical Data (2023-2026)       │
                         └─────────────────────────────┘
```

### 2.2 Detailed System Flow

```
 ┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌────────────┐
 │ 08:00    │───▶│ 10:00-10:30  │───▶│ 13:00-16:00   │───▶│ 18:00-22:00│
 │ Cookie   │    │ Douyin + XHS │    │ Intel + Hit   │    │ Review +   │
 │ Sync     │    │ Daily Report │    │ Deep Analysis │    │ Archive    │
 └──────────┘    └──────────────┘    └───────────────┘    └────────────┘
      │                │                    │                   │
      ▼                ▼                    ▼                   ▼
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌────────────┐
│ 3 Cookie  │    │ Parsed Data +│    │ Decision      │    │ Memory +   │
│ Files     │    │ Decision     │    │ Briefs (D1-D4)│    │ Wiki +     │
│ (JuLiang, │    │ Layer        │    │ + Risk Alert  │    │ GitHub     │
│ XHS, Weibo)│   │ Output       │    │               │    │ Commit     │
 └──────────┘    └──────────────┘    └───────────────┘    └────────────┘
                      │                    │
                      ▼                    ▼
               ┌──────────────────────────────┐
               │     Feishu Group Chat        │
               │  (oc_2581c03b79e4893cc36...) │
               │  Interactive Card via        │
               │  send_feishu_card.py         │
               └──────────────────────────────┘
```

### 2.3 Data Flow (How a Daily Report Is Born)

```
1. Cron triggers isolated Agent session
       │
2. Agent reads task description & SOP from Wiki
       │
3. Agent invokes Python scripts → collects raw data
   (Playwright → CDP Browser → parse → validate)
       │
4. Agent analyzes data using DeepSeek-V4
   → applies Decision Framework
   → generates structured judgment layer
       │
5. Agent constructs Feishu interactive card JSON
   (schema: "2.0", elements[].tag: "markdown")
       │
6. Agent calls send_feishu_card.py → pushes to group
       │
7. Agent logs summary to memory/YYYY-MM-DD.md
   → optionally updates Wiki knowledge base
```

---

## 3. CORE MODULES IN DETAIL

### 3.1 Douyin Index Daily Report (抖音指数日报)

**Schedule:** Daily 10:30 CST
**Source:** Douyin Creator Platform (抖音创作者平台) — subscription page
**Script:** `scripts/douyin_index_v9.py`

| Feature | Detail |
|---------|--------|
| **Data Coverage** | 8 venues: Jianye Movie Town + 7 core competitors |
| **Metrics** | Search Index (搜索指数) + Composite Index (综合指数) + Daily % Change |
| **Collection** | Dual-channel: Playwright script → CDP direct browser (auto-fallback) |
| **Output** | Ranked table with 8 venues, anomaly markers (🔺🔻) |
| **Fallback** | If script returns incomplete data (667-char truncation bug), agent auto-switches to CDP extraction |
| **Real-World Case** | May 22: script truncated → agent used CDP → report delivered on time |

**Competitor Tracking Set (Fixed):**

1. 清明上河园 (Qingming Riverside Landscape Garden) — #1 by search volume
2. 万岁山武侠城 (Wansui Mountain Martial Arts City) — #2
3. 银基动物王国 (Yinji Animal Kingdom) — #3 (亲子旺季 surge)
4. 郑州方特欢乐世界 (Zhengzhou Fantawild) — student pricing threat
5. 郑州海昌海洋公园 (Zhengzhou Haichang Ocean Park) — price war
6. 只有河南戏剧幻城 (Only Henan·Drama City) — 50%+ surge
7. 只有红楼梦戏剧幻城 (Only Dream of Red Mansions) — growth leader
8. **建业电影小镇 (Jianye Movie Town)** — baseline

### 3.2 Xiaohongshu Daily Report (小红书日报)

**Schedule:** Daily 10:00 CST
**Source:** Xiaohongshu Lingxi Backend (小红书灵犀) + Search Page + Official Account Profile

| Feature | Detail |
|---------|--------|
| **Official Account** | 98K followers, 2,196 notes, profile ID: `5fbb4f740000000001000410` |
| **Brand Metrics** | Audience Assets, Search Volume, Click Index, Reading Penetration Rate |
| **Competitor Keywords** | 7 competitors + self brand — weekly comparison |
| **Xiaohongshu Trend Data** | Search totals, YoY/DoD change, Interest rankings |
| **Viral Notes** | Top UGC notes with like/collect/comment counts |

### 3.3 Travel Intel Daily Report (文旅情报日报)

**Schedule:** Daily 13:00 CST
**Source:** Baidu Search + Weibo Trending + Industry News
**Scope:** National — NOT limited to 7 core competitors (expanded May 25)

**Coverage Dimensions:**
- 🏛️ **Policy & Capital:** Government tourism initiatives, subsidies, regulatory changes
- 🏟️ **Competitor Activity:** New shows, events, pricing changes, IP collaborations
- 🌐 **Industry Trends:** Summer tourism, experience economy, national travel patterns
- ⚠️ **Risk Alerts:** Safety incidents, regulatory enforcement, negative PR

**Recent Examples (May 25):**
- Henan Provincial Tourism Development Conference just concluded (5.22-23) with 300+ summer initiatives
- 5·19 China Tourism Day subsidy window closing May 31
- Ministry of Culture spot-slap on 5A downgrade threats (Shaolin Temple case)

### 3.4 Competitor Viral Hit Deconstruction (竞品爆款拆解)

**Schedule:** Daily 15:00 CST
**Source:** Douyin Trending · Xiaohongshu Viral · Weibo Hot Search
**Scope:** National — actively discovers new competitors

**Deconstruction Framework:**
```
Case: [Title]
├─ 📊 Data Snapshot (likes/views/engagement)
├─ 🔍 Strategy Analysis (angle/emotion/format)
├─ 🎯 Replicability Assessment (confidence score)
└─ 💡 Movie Town Adaptation (concrete action plan)
```

**Recent Cases Analyzed:**
- "Li Bai Poetry Duel at West Lake" — 356M views, NPC random-poetry model → replicable
- "Red Rose Dress for Waterfall" — Chongdugou scenic makeover → 22K likes
- "520 Marriage Registration" at Wansui Mountain — civic ceremony in scenic spot
- "Korean Brand Copies Hanfu" — Weibo #15 trending → cultural IP defense

### 3.5 Competitor Keyword Deep Analysis (竞品关键词深度分析)

**Schedule:** Daily 16:00 CST
**Source:** Douyin Index Keyword Page + Xiaohongshu Lingxi + Baidu Search
**Method:** Rotation mechanism with checkpoint resume (`/tmp/daily_task_state.json`)

**4-Platform Collection Manifest:**

| Platform | Data Collected | Tool |
|----------|---------------|------|
| 🎵 Douyin Index | Search Index, Composite Index, Related Keywords TOP10, Audience Portrait | `cdp_keyword_deep.py` |
| 📕 Xiaohongshu Lingxi | Search Volume, Hot Terms, Upstream/Downstream Keywords | CDP + JS Injection |
| 📕 XHS Search Page | Viral Notes TOP10, Tags, Hot Questions | CDP Browser |
| 🌐 Baidu Search | Revenue, Visitor Count, Ticket Price, Media Coverage | CDP Browser |

**Progress: 14/21 core competitors completed** (as of May 25)

### 3.6 Weekly Accurate Rate Evaluation (周度竞争格局报告)

**Schedule:** Sundays 10:00 CST

Each week, the system calculates its own prediction accuracy across all decision outputs:

| Week | Accuracy | Trend |
|:----:|:--------:|:-----:|
| W18 | 60% | Baseline |
| W19 | 65% | +5pp |
| W20 | 70% | +5pp |
| **W21** | **80%** | **+10pp** |

**Error Pattern Analysis (W21):**
- Execution-layer disconnection: 2 errors (insights identified but execution not triggered)
- Data source breakage: 1 error (CSV missing 8 days)
- Signal misinterpretation: 0 errors (improving)

### 3.7 Weekly Passenger Flow Insight (周度客流洞察)

**Schedule:** Tuesday 9:30 CST (moved from Monday because Monday data is stale)

**Data Source:** `~/Desktop/2026游客量统计.csv` — daily passenger count spreadsheet

**Report Structure (5 chapters, max 5 tables per card):**
1. YTD Summary (年度累计 vs target)
2. Monthly Breakdown (月度拆解)
3. Last 7 Days Detail (近7日明细)
4. 穿越德化街 Thematic Analysis (穿越德化街专项)
5. Actionable Recommendations (建议)

**Key Metrics (as of May 17):**

| Month | Visitors | Days | Daily Avg | YTD Cumulative | Target Completion |
|:----:|:--------:|:----:|:---------:|:--------------:|:-----------------:|
| Jan | 56,571 | 29 | 1,950 | 56,571 | 3.7% |
| Feb | 307,169 | 28 | 10,970 | 363,740 | 23.8% |
| Mar | 80,285 | 31 | 2,589 | 444,025 | 29.0% |
| Apr | 93,295 | 30 | 3,109 | 537,320 | 35.1% |
| May (to 17th) | 118,747 | 17 | 6,985 | 656,067 | **42.9%** |
| **Annual Target** | **1,530,000** | — | — | — | — |

**Data Quality Status:** ⚠️ CSV last updated May 17, now 8 days stale — pending internal data sync

---

## 4. DECISION FRAMEWORK

Every report, insight, and recommendation in this system follows a structured decision framework designed for real-world marketing execution.

### 4.1 Standard Judgment Layer

Every daily report contains this exact judgment structure:

| Dimension | Values | Description | Example |
|-----------|--------|-------------|---------|
| 🎯 **Impact Level** | 🔴高/🟡中/🟢低/📡噪音 | How much does this affect Movie Town? | 🔴高 — competitor 50%+ surge |
| 💡 **Action** | 跟风/借势/警惕/忽略 | What should the team do? | 跟风 — replicate the format |
| ⏰ **Window** | 今天/本周/不紧急 | When must action happen? | 今天 — trending window closes in 48h |
| ⚠️ **Cost of Inaction** | Specific loss statement | What is lost by doing nothing? | Missed summer peak season |

### 4.2 Decision Brief Format (D-Series)

```
D<number> | <one-line title>
├─ 简单理解: plain-English explanation
├─ 做错风险: consequence of not acting
├─ 推荐+理由: specific suggestion + confidence score
└─ 利弊: trade-offs (benefit vs cost/effort)
```

### 4.3 Forbidden Vocabulary (2026-05-19 Mandate)

The agent is strictly prohibited from using these vague phrases:

| ❌ Banned | ✅ Replace With |
|-----------|----------------|
| "值得关注" | "本周必须执行" or specific priority |
| "仅供参考" | Concrete recommendation with confidence |
| "或许可以考虑" | Definitive suggestion: "推荐：..." |
| "需要进一步分析" | Clear judgment or explicit "信息不足" |

### 4.4 Learning Loop (每周复盘)

Every Sunday, the system:
1. Calculates prediction accuracy from the past week
2. Analyzes error patterns: data gaps / logic bias / platform changes
3. Updates decision rules in Wiki
4. Validates → marks rules as 🟢 (verified) or 🔴 (expired)

---

## 5. KNOWLEDGE MANAGEMENT SYSTEM (WIKI)

### 5.1 Wiki Architecture (karpathy-wiki 模式)

The wiki follows a three-layer knowledge abstraction model:

```
KNOWLEDGE LAYER (wiki/)
│
├── concepts/         ← Abstract patterns & theories
│   ├── 演艺景区.md       — Performance venue characteristics
│   ├── 内容爆款规律.md    — Viral content patterns
│   ├── 景区营销漏斗.md    — Marketing funnel model
│   ├── 情绪营销.md       — Emotional marketing framework
│   ├── 平台算法规则.md    — Douyin/Xiaohongshu algorithm notes
│   └── ... (12 concept files)
│
├── entities/         ← Concrete objects & actors
│   ├── 建业电影小镇.md    — Movie Town profile
│   ├── 万岁山武侠城.md    — Competitor: Wansui Mountain
│   ├── 清明上河园.md      — Competitor: Qingming Garden
│   ├── 抖音平台.md        — Platform entity
│   ├── 小红书平台.md      — Platform entity
│   └── ... (12 entity files)
│
├── sources/          ← Data provenance & analysis
│   ├── 穿越德化街数据分析.md — Thematic data analysis
│   ├── 抖音指数追踪日报.md  — Daily tracking archive
│   ├── 竞品深度档案.md     — Profile sources
│   └── ... (8 source files)
│
└── queries/          ← Archived decision Q&A
    ├── 抖音与小红书平台差异.md
    ├── 知识层与业务层关系.md
    └── ... (5 query files)
```

### 5.2 Business Layer (电影小镇/)

```
BUSINESS LAYER (wiki/电影小镇/)
│
├── 基础档案.md            — Basic info, targets, annual goals
├── 战略框架.md            — SWOT, competitive positioning
├── 人群画像.md            — Douyin & Xiaohongshu audience profiles
├── 历史数据/              — Historical records (2023-2026)
│   ├── 2023年/数据.md
│   ├── 2024年/数据.md
│   ├── 2025年/数据.md
│   └── 数据.md (2026, updated to May 17)
├── 演出节目/
│   └── 穿越德化街.md      — 6-year show data + Q2 update
├── 运营方法/              — Operation SOPs
│   ├── 抖音运营方法.md
│   └── 小红书运营方法.md
└── 运营规划/              — Seasonal plans
    └── 环形水剧场与复古广场夏季运营方案.md
```

### 5.3 Competitor Intelligence Layer

```
COMPETITOR INTELLIGENCE (wiki/竞品分析/)
│
├── 竞品深度档案/          — 20 deep-profile reports
│   ├── 郑州方特欢乐世界深度分析.md
│   ├── 银基动物王国深度分析.md
│   ├── 清明上河园深度分析.md
│   ├── 大唐不夜城深度分析.md
│   ├── 阿那亚深度分析.md
│   └── ... (20 files, all completed)
│
├── 竞品动态追踪/          — Daily activity log (Apr 20-27)
├── 追踪数据/
│   ├── 抖音指数追踪.md
│   └── 小红书爆款追踪.md
│
└── 关键词池状态.md        — Checkpoint system for rotation
```

### 5.4 Viral Case Library (全国景区案例库)

```
CASE LIBRARY (wiki/全国景区案例库/)
│
├── index.md             — 10 viral formulas index
└── (20+ weekly case files)
    ├── 大唐不夜城夜游标杆-2026W17.md
    ├── 万岁山武侠城标杆-2026W17.md
    ├── 打铁花跨景区爆款现象-2026W17.md
    ├── 乌镇住宿早茶客46%复购率-2026W22.md
    ├── NPC体系化运营青岩古镇银票系统-2026W22.md
    └── ...
```

**10 Viral Formulas (as of W22):**

| # | Formula | Example Cases |
|---|---------|--------------|
| 1 | Emotional Teaser + Reality Reveal | Wansui Mountain, Tang Dynasty Street |
| 2 | Intangible Heritage × Scenic Reality | Iron Flower, Song Dynasty Performance |
| 3 | Local KOC Matrix Distribution | Multi-angle coverage strategy |
| 4 | Interactive NPC Surprise Encounters | Poetry Duel, Marriage Registration |
| 5 | Seasonal Limited-Edition Transformation | Summer Night Market, Cherry Blossom |
| 6 | Reverse Operation: Quiet ≠ Boring | Only Henan "Non-Noisy" Concert |
| 7 | Spirituality Economy × Emotional Bonding | First-snow Wishes, Sunset Photography |
| 8 | Space Cultural Remake | Waterfall Rose Dress, Cliff Coffee |
| 9 | Festival IP Long-term Operation | Qingming Festival series, Dragon Boat |
| 10 | Audience Co-creation UGC Campaign | "My Hidden Spot" Contest |

### 5.5 SOP Library (22 Documents)

| # | SOP File | Purpose |
|:-:|----------|---------|
| 1 | 抖音指数日报.md | Daily Douyin report generation flow |
| 2 | 小红书日报.md | Daily XHS report generation flow |
| 3 | 文旅活动热点追踪日报.md | Travel intel daily report |
| 4 | 竞品爆款拆解.md | Viral hit deconstruction standard |
| 5 | 竞品关键词深度分析流程.md | Keyword deep analysis step-by-step |
| 6 | 竞品内容动态.md | Competitor content tracking |
| 7 | 竞品深度分析流程.md | 4-platform deep analysis SOP |
| 8 | 竞品深度档案标准格式.md | Profile archive format spec |
| 9 | 周度客流营收洞察报告.md | Weekly passenger insight report |
| 10 | 每日复盘整合.md | Daily review integration |
| 11 | 每日任务总览.md | All tasks roster |
| 12 | 案例库更新.md | Case library update flow |
| 13 | 系统健康检查SOP.md | System health checklist |
| 14 | 专属浏览器维护SOP.md | CDP browser maintenance |
| 15 | 飞书卡片视觉规范.md | Feishu card visual spec |
| 16 | 飞书卡片故障复盘.md | Card failure postmortem |
| 17 | 反馈纠错.md | Feedback & correction |
| 18 | 日报模板.md | Report template |
| 19 | Wiki健康检查.md | Wiki health check |
| 20 | 代码库Wiki漂移检查.md | Wiki drift detection |
| 21 | 决策简报格式标准.md | Decision brief format |
| 22 | 反谄媚分析规范.md | Anti-sycophancy analysis norm |

---

## 6. SYSTEM MEMORY & STATE

### 6.1 Memory Architecture

```
memory/                          ← Agent's episodic memory
├── YYYY-MM-DD.md               ← Daily logs (cron execution records)
├── topics/feedback/            ← Correction/confirmation feedback
├── topics/projects/            ← Long-running project state
├── heartbeat-state.json        ← Heartbeat check tracking
└── daily_task_state.json       ← Task rotation checkpoint

MEMORY.md                        ← Long-term curated memory (100 lines max)
PROGRAMMER_AGENT.md              ← Dedicated coding agent identity
AGENTS.md                        ← Agent behavioral guidelines
SOUL.md                          ← Agent personality & working standards
TOOLS.md                         ← Local tool configuration
USER.md                          ← User profile & preferences
```

### 6.2 Key System Rules (Ironclad Rules in MEMORY.md)

| Rule | Purpose | Established |
|------|---------|------------|
| Feishu cards must use `send_feishu_card.py` | Tables won't render via default message tool | 2026-05-25 |
| Weekly passenger report moved to Tuesday | Monday data is stale | 2025-05-25 |
| Obsidian sync: value-add only | Don't re-sync unchanged content | 2025-05-25 |
| Search scope: unlimited national | Any relevant competitor qualifies | 2025-05-25 |
| Data must be read from actual files | Never use experience/heuristics | 2025-04-22 |
| browser-use is banned entirely | All automation via Playwright scripts | 2025-04-20 |
| Cron delivery: mode=none | No redundant push notifications | 2025-04-10 |
| Card line breaks: use `<br/>` | Feishu doesn't parse `\n` | 2025-04-10 |

### 6.3 Task State Checkpoint

The system uses `/tmp/daily_task_state.json` for task rotation persistence:

```json
{
  "竞品关键词": {
    "done": ["万岁山武侠城", "清明上河园", "只有河南", "郑州方特", "银基", ...],
    "current": "郑州海昌海洋公园"
  },
  "文旅案例": {
    "done": ["万岁山", "银基", "大唐不夜城", ...],
    "current": "轮换中"
  }
}
```

### 6.4 CDP Browser Setup

```
Port: 18800 (dedicated browser instance)

Tab Assignments:
  Tab 0: Xiaohongshu Lingxi Backend (idea.xiaohongshu.com/trend/trendAnalyze)
  Tab 1: Baidu Search
  Tab 2: Douyin Subscription Page (creator.douyin.com/my-subscript)
  Tab 3: Douyin iframe
  Tab 4: Douyin Keyword Page (creator.douyin.com/arithmetic-index)
  Tab 5: Douyin iframe
  Tab 6: Xiaohongshu Explore Page (xiaohongshu.com/explore)

Cookies stored at:
  /tmp/juLiang_cookies.json       — Douyin (proxied via 127.0.0.1:7897)
  /tmp/xiaohongshu_cookies.json   — Xiaohongshu (proxied)
  /tmp/weibo_cookies.json         — Weibo
```

---

## 7. KEY ARCHITECTURAL DECISIONS & TRADE-OFFS

### 7.1 Why OpenClaw + DeepSeek (Not Custom-Built)

| Option | Considered | Verdict |
|--------|-----------|---------|
| OpenClaw + Agent Skills | ✅ **Chosen** | 25+ model providers, cron scheduling, skills ecosystem, local-first |
| Custom Python scripts only | ❌ Rejected | No agent reasoning or autonomous decision-making |
| Paid SaaS (e.g. Similarweb) | ❌ Rejected | Expensive, no custom decision framework, data locked-in |

### 7.2 Why Verlet Physics (Not d3-force for Canvas)

WeChat Mini-Programs cannot run npm d3-force directly (ES module + DOM dependency). The graph visualization uses a **hand-rolled Verlet integration** physics engine:

```javascript
const kRepulsion = 700;    // Coulomb-like repulsion
const kSpring = 0.04;      // Hooke's spring tension
const lLength = 120;        // Ideal spring length
const gravity = 0.02;       // Center gravity
const friction = 0.85;      // Velocity damping
```

Performance: 60fps on modern devices with 50+ nodes.

### 7.3 Why Douyin Script + CDP Dual-Channel

The Douyin Creator Platform uses heavy client-side rendering (SPA). The Playwright script sometimes returns empty or truncated data. The CDP direct browser channel serves as a reliable fallback:

```
Script → [success?] → Parse & use data
         ↓
      [fail?]  → CDP direct extraction → Parse & use data
                  ↓
               [fail?] → Trend inference from recent history
```

### 7.4 Why send_feishu_card.py (Not Direct message tool)

Feishu's default message tool sends `msg_type: "post"` (rich text), which **does not render tables**. The card script sends `msg_type: "interactive"` with proper `schema: "2.0"` format:

```python
# send_feishu_card.py
payload = {
    "receive_id": chat_id,
    "msg_type": "interactive",
    "content": json.dumps(card, ensure_ascii=False)
}
# card format:
{
    "schema": "2.0",
    "header": {"title": {"tag": "plain_text", "content": "..."}},
    "body": {"elements": [{"tag": "markdown", "content": "| table | data |"}]}
}
```

---

## 8. RESULTS & EFFECTIVENESS

### 8.1 Operational Metrics

| Metric | Value |
|--------|-------|
| **Uptime** | 30+ days continuous |
| **Daily reports generated** | 6-8 decision briefs |
| **Daily API tokens consumed** | ~200K (DeepSeek-V4-Flash) |
| **Feishu cards pushed** | 180+ cards to date |
| **Automated cron tasks** | 23 active |
| **Models allowed** | deepseek/deepseek-v4-flash (single) |

### 8.2 Knowledge Assets Accumulated

| Asset Type | Count | Details |
|------------|:-----:|---------|
| Competitor deep profiles | **20** | Full 4-platform analysis |
| Viral case studies | **20+** | Weekly updated |
| Viral formulas | **10** | Identified patterns |
| SOP documents | **22** | Standardized procedures |
| Historical records | **4 years** | 2023-2026 passenger data |
| Wiki files | **150+** | Markdown documents |

### 8.3 Business Impact

- **Search Index recovery**: Movie Town search index rose **+24.51%** in W21 (brand trauma recovery signal)
- **Competitive ranking**: Moved from 7th to **4th** among 8 tracked venues
- **Weekly accuracy**: Improved from 60% (W18) to **80% (W21)** — 4 consecutive weeks of improvement
- **Content vacuum detection**: Algorithm successfully identified "search up / composite down" divergence pattern (content supply gap), confirmed May 22

---

## 9. TECHNOLOGY STACK

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **AI Framework** | OpenClaw v2026.5.20 | Agent runtime, cron, tools |
| **LLM** | DeepSeek-V4-Flash | Reasoning, analysis, generation |
| **Data Collection** | Python 3.12 + Playwright + CDP | Web scraping, browser automation |
| **Push Channel** | Feishu Bot API (interactive card) | Report delivery to group chat |
| **Knowledge Base** | Obsidian + karpathy-wiki | Structured wiki with 3-layer abstraction |
| **Operating System** | macOS 26.4 (Darwin 25.4.0) ARM64 | Host environment |
| **Hardware** | Mac Mini (2024) | 24/7 local runtime |
| **Node.js** | v25.8.2 | OpenClaw runtime |
| **Skills Registry** | ClawHub (13,729 available skills) | Extensible agent capabilities |
| **Version Control** | Git + GitHub | Code & wiki repository |

---

## 10. HOW TO NAVIGATE

### Open Obsidian Wiki
Open the `wiki/` directory in Obsidian. Start at `wiki/index.md`.

### View Daily Reports
All reports auto-push to Feishu group chat. Summary logs are in `memory/YYYY-MM-DD.md`.

### Explore the Code
- `scripts/` — Python automation scripts (45+ files)
- `wiki/` — Knowledge base (150+ markdown files)
- `PROGRAMMER_AGENT.md` — Dedicated coding agent

### Give Feedback
The system includes a feedback loop mechanism. Corrections are recorded in `memory/topics/feedback/` and influence future behavior.

---

*Built by AI, for humans. Running since April 2026.*  
*Automatically deployed & maintained by OpenClaw AI Agent.*  
*Last system update: 2026-05-25*

---

# 🇨🇳 中文版

## 一、项目简介

**Scenic-Area-Marketing-CN** 是一个基于 [OpenClaw AI Agent框架](https://github.com/openclaw/openclaw) 构建的生产级全自动景区营销情报系统。系统 24/7 运行在 Mac Mini 上，自主完成从多平台数据采集、结构化竞争情报分析、决策级报告生成、飞书群推送，到 Obsidian 知识图谱归档的完整闭环。

系统服务于**建业电影小镇**——位于河南郑州的文化旅游景区，2026年度目标客流153万人次、营收1.2亿元。

这不是一个演示版或原型。系统已**连续无人工干预运行30+天**，日均产出 **6-8份可执行决策简报**。

---

## 二、系统架构

### 2.1 高维架构

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                              🧠 AI AGENT 核心                                       │
│              OpenClaw Runtime · DeepSeek-V4-Flash · 23个cron任务                     │
│                   Web搜索 · 记忆系统 · CDP浏览器 · 飞书API                          │
└─────────────────────────────────────────────────────────────────────────────────────┘
          │                             │                           │
          ▼                             ▼                           ▼
┌─────────────────────┐ ┌─────────────────────────────┐ ┌─────────────────────────┐
│    📊 数据层         │ │    🧠 智能分析层              │ │    ⚡ 执行层            │
├─────────────────────┤ ├─────────────────────────────┤ ├─────────────────────────┤
│ 抖音指数追踪         │ │ 决策判断引擎                  │ │ 飞书卡片推送            │
│ 小红书监测           │ │ 竞品情报分析                  │ │ (send_feishu_card.py)   │
│ 微博热搜             │ │ 趋势&异动检测                 │ │ Cron任务调度器           │
│ 百度搜索             │ │ 爆款拆解框架                  │ │ Cookie轮换管理器        │
│ 客流CSV读取          │ │ 周度预测&复盘                 │ │ CDP浏览器控制           │
│ CDP Cookie管理       │ │ 学习闭环&验证                 │ │ 健康监控                │
└─────────────────────┘ └─────────────────────────────┘ └─────────────────────────┘
          │                             │                           │
          └─────────────────────────────┼───────────────────────────┘
                                        ▼
                         ┌─────────────────────────────┐
                         │    📚 知识层                 │
                         ├─────────────────────────────┤
                         │ Obsidian Wiki (三层抽象)      │
                         │  → 概念/实体/来源             │
                         │  → 20个竞品深度档案            │
                         │  → 10条爆款公式/22个SOP       │
                         │  → 历史数据 (2023-2026)       │
                         └─────────────────────────────┘
```

### 2.2 完整数据流

```
 ┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌────────────┐
 │ 08:00    │───▶│ 10:00-10:30  │───▶│ 13:00-16:00   │───▶│ 18:00-22:00│
 │ Cookie   │    │ 抖音+小红书   │    │ 情报+爆款     │    │ 复盘+     │
 │ 同步     │    │ 日报         │    │ 深度分析      │    │ 归档      │
 └──────────┘    └──────────────┘    └───────────────┘    └────────────┘
      │                │                    │                   │
      ▼                ▼                    ▼                   ▼
┌──────────┐    ┌──────────────┐    ┌───────────────┐    ┌────────────┐
│ 3个Cookie │    │ 解析数据+    │    │ 决策简报      │    │ 记忆+Wiki  │
│ 文件      │    │ 决策层输出   │    │ (D1-D4)       │    │ +GitHub    │
│ (抖音/小红 │    │              │    │ +风险预警     │    │ 提交       │
│ 书/微博)  │    │              │    │               │    │            │
 └──────────┘    └──────────────┘    └───────────────┘    └────────────┘
                      │                    │
                      ▼                    ▼
               ┌──────────────────────────────┐
               │       飞书群聊               │
               │  (oc_2581c03b79e4893cc36...) │
               │  通过send_feishu_card.py      │
               │  发送interactive卡片          │
               └──────────────────────────────┘
```

### 2.3 一份日报的诞生过程

```
1. Cron触发隔离Agent session
       │
2. Agent读取任务描述及Wiki中的SOP
       │
3. Agent调用Python脚本 → 采集原始数据
   (Playwright → CDP浏览器 → 解析 → 验证)
       │
4. Agent用DeepSeek-V4分析数据
   → 应用决策判断框架
   → 生成结构化决策层
       │
5. Agent构造飞书交互卡片JSON
   (schema: "2.0", elements[].tag: "markdown")
       │
6. Agent调用send_feishu_card.py → 推送至群
       │
7. Agent记录执行摘要至memory/YYYY-MM-DD.md
   → 可选更新Wiki知识库
```

---

## 三、核心功能详解

### 3.1 抖音指数日报

**时间：** 每日10:30
**来源：** 抖音创作者平台·我的订阅页
**脚本：** `scripts/douyin_index_v9.py`

| 特性 | 详情 |
|------|------|
| **数据范围** | 8个景区：电影小镇+7核心竞品 |
| **指标** | 搜索指数 + 综合指数 + 日环比 |
| **采集** | 双通道：Playwright脚本 → CDP浏览器直连（自动降级） |
| **输出** | 排名表 + 异动标注(🔺🔻) |
| **降级机制** | 脚本返回空/截断数据时，自动切换CDP提取 |

**8个常规定义竞品（固定不变）：**

| 排名 | 景区 | 日均搜索指数 | 特点 |
|:---:|------|:----------:|------|
| 🥇 | 清明上河园 | 31.5万 | IP联动（杨洋/雨霖铃） |
| 🥈 | 万岁山武侠城 | 5.5万 | 情绪价值内容/IP势能 |
| 🥉 | 银基动物王国 | 9.4万 | 亲子旺季启动 |
| 4 | 郑州方特欢乐世界 | 1.1万 | 学生低价促销 |
| 5 | 郑州海昌海洋公园 | 5,557 | 价格战 |
| 6 | 只有河南戏剧幻城 | 5,162 | 50%+暴涨 |
| 7 | 只有红楼梦戏剧幻城 | 3,509 | 增速领先 |
| — | **建业电影小镇** | **8,448** | **基准** |

### 3.2 小红书日报

**时间：** 每日10:00
**来源：** 小红书灵犀后台 + 搜索页 + 官方账号

| 特性 | 数据 |
|------|------|
| 官方账号 | 9.8万粉丝 / 2196篇笔记 |
| 品牌五维 | 人群资产+44.64%, 搜索量+22.9%, **阅读渗透率↓57.93%** |
| 决策输出 | 520方向正确 → 跟风提炼至618/端午 |
| 竞品覆盖 | 清上河园/万岁山/银基/只有河南/方特 |

### 3.3 文旅情报日报

**时间：** 每日13:00
**范围：** **全国范围**（5月25日起扩展，不限7个核心竞品）

**覆盖维度：**
- 🏛️ **政策资本**：政府旅游政策/补贴/监管变化
- 🏟️ **竞品活动**：新节目/活动/定价/IP合作
- 🌐 **行业趋势**：暑期旅游/体验经济/出行模式
- ⚠️ **风险预警**：安全事故/监管执法/负面舆情

**今日(5月25日)示例：**
- 河南省文旅发展大会刚闭幕（5.22-23安阳），发布300项惠民措施
- 5·19中国旅游日惠民补贴窗口5月31日关闭
- 文旅部第二批强制消费典型案例涉及河南新乡/洛阳

### 3.4 竞品爆款拆解

**时间：** 每日15:00
**来源：** 抖音热搜/小红书爆款/微博热搜
**范围：** **全国范围主动发现**

**拆解框架：**
```
案例: [标题]
├─ 📊 数据快照 (点赞/播放/互动)
├─ 🔍 策略分析 (角度/情绪/格式)
├─ 🎯 可复制性评估 (置信度评分)
└─ 💡 电影小镇适配建议 (具体行动)
```

**近期案例：**
- 李白西湖对诗 → 356万播放，NPC随机对诗模式 → 可复制
- 重渡沟瀑布玫瑰裙 → 2.2万赞，场景改造+话题矩阵
- 万岁山520景区领证 → 前26对赠年卡 → 建议七夕档落地
- 韩国品牌抄袭汉服 → 微博第15位 → 国潮汉服日策划

### 3.5 竞品关键词深度分析

**时间：** 每日16:00
**方法：** 轮换制 + 断点续做（`/tmp/daily_task_state.json`）

**四平台采集清单：**

| 平台 | 采集数据 | 工具 |
|------|---------|------|
| 🎵 抖音指数 | 搜索指数/综合指数/关联词TOP10/人群画像 | `cdp_keyword_deep.py` |
| 📕 小红书灵犀 | 搜索量/热搜词/上下游词 | CDP + JS注入 |
| 📕 小红书搜索页 | 爆款笔记TOP10/标签/热搜问题 | CDP浏览器 |
| 🌐 百度搜索 | 营收/客流量/票价/媒体报道 | CDP浏览器 |

**当前进度：已完成14/21个核心景区**（截至5月25日）

### 3.6 周度竞争格局报告（含准确率复盘）

**时间：** 周日10:00

系统每周计算自身预测准确率：

| 周次 | 准确率 | 趋势 |
|:----:|:------:|:----:|
| W18 | 60% | 基准 |
| W19 | 65% | +5pp |
| W20 | 70% | +5pp |
| **W21** | **80%** | **+10pp** |

**W21错误模式分析：**
- 执行层脱节：2次（建议已出但执行未跟上）
- 数据源断裂：1次（CSV断档8天）
- 信号误判：0次（持续改善）

---

## 四、决策判断框架

### 4.1 标准判断层

| 维度 | 取值 | 说明 |
|------|------|------|
| 🎯 **影响等级** | 🔴高/🟡中/🟢低/📡噪音 | 对电影小镇的实际影响程度 |
| 💡 **建议动作** | 跟风/借势/警惕/忽略 | 团队应该做什么 |
| ⏰ **执行窗口** | 今天/本周/不紧急 | 必须在什么时间前行动 |
| ⚠️ **不做代价** | 明确的损失陈述 | 不做的后果量化 |

### 4.2 决策简报格式（D序列）

```
D<序号> | <一句话标题>
├─ 简单理解：一句话解释
├─ 做错风险：不执行的后果
├─ 推荐+理由：具体建议 + 置信度评分
└─ 利弊：收益 vs 成本/精力
```

### 4.3 禁止用语（2026-05-19强制执行）

| ❌ 禁止 | ✅ 替换为 |
|---------|----------|
| "值得关注" | "本周必须执行" 或 具体优先级 |
| "仅供参考" | 具体建议+置信度 |
| "或许可以考虑" | "推荐：..." |
| "需要进一步分析" | 明确判断 或 明确"信息不足" |

---

## 五、知识管理（Obsidian Wiki）

### 5.1 三层知识抽象

```
KNOWLEDGE LAYER (wiki/)
│
├── concepts/         ← 抽象模式与理论
│   ├── 演艺景区.md        — 演艺景区特征
│   ├── 内容爆款规律.md    — 爆款内容模式
│   ├── 景区营销漏斗.md    — 漏斗模型
│   ├── 情绪营销.md       — 情绪营销框架
│   ├── 平台算法规则.md    — 抖音/小红书算法
│   └── ... (共12个概念文件)
│
├── entities/         ← 具体对象
│   ├── 建业电影小镇.md    — 自身档案
│   ├── 万岁山武侠城.md    — 竞品
│   ├── 清明上河园.md      — 竞品
│   ├── 抖音平台.md        — 平台实体
│   ├── 小红书平台.md      — 平台实体
│   └── ... (共12个实体文件)
│
├── sources/          ← 数据溯源
│   ├── 穿越德化街数据分析.md
│   ├── 抖音指数追踪日报.md
│   ├── 竞品深度档案.md
│   └── ... (共8个来源文件)
│
└── queries/          ← 决策问答归档
    ├── 抖音与小红书平台差异.md
    ├── 知识层与业务层关系.md
    └── ... (共5个问答文件)
```

### 5.2 电影小镇核心业务层

```
BUSINESS LAYER (wiki/电影小镇/)
├── 基础档案.md        — 基本信息/年度目标(153万/1.2亿)
├── 战略框架.md        — SWOT/竞争定位
├── 人群画像.md        — 抖音/小红书用户画像
├── 历史数据/          — 2023-2026历年客流
│   ├── 数据.md        — ✅ YTD 656,067 / 42.9%
│   ├── 规律洞察.md    — 春节/暑期/国庆三峰值
│   └── 2023年/2024年/2025年/
├── 演出节目/
│   └── 穿越德化街.md  — 6年数据 + Q2更新
│                       (240场/177,076人次/转化率27.0%)
├── 运营方法/          — 抖音/小红书运营SOP
└── 运营规划/          — 夏季运营方案
```

### 5.3 竞品情报层

```
COMPETITOR INTELLIGENCE (wiki/竞品分析/)
├── 竞品深度档案/      — 20个全国景区深度分析
│   ├── 郑州方特欢乐世界深度分析.md
│   ├── 银基动物王国深度分析.md
│   ├── 清明上河园深度分析.md
│   ├── 大唐不夜城深度分析.md
│   ├── 阿那亚深度分析.md
│   └── ... (20个文件，全部完成)
│
├── 竞品动态追踪/      — 每日动态日志 (4月20-27日)
├── 追踪数据/
│   ├── 抖音指数追踪.md
│   └── 小红书爆款追踪.md
│
└── 关键词池状态.md    — 断点续做检查点
```

### 5.4 全国景区案例库

```
CASE LIBRARY (wiki/全国景区案例库/)
├── index.md          — 10条爆款公式索引
└── 20+ 按周归档案例
    ├── 大唐不夜城夜游标杆-2026W17.md
    ├── 万岁山武侠城标杆-2026W17.md
    ├── 打铁花跨景区爆款现象-2026W17.md
    ├── 乌镇住宿早茶客46%复购率-2026W22.md
    └── ...
```

**10条爆款公式（W22更新）：**

| # | 公式 | 案例 |
|---|------|------|
| 1 | 情绪悬念+反转曝光 | 万岁山/大唐不夜城 |
| 2 | 非遗x实景融合 | 打铁花/大宋演出 |
| 3 | 本地KOC矩阵分发 | 多角度覆盖策略 |
| 4 | NPC随机惊喜互动 | 对诗/领证/情景剧 |
| 5 | 季节限定场景改造 | 夏日夜市/樱花季 |
| 6 | 反向操作·安静≠无聊 | 只有河南"不躁"音乐会 |
| 7 | 情绪经济x情感绑定 | 初雪许愿/日落摄影 |
| 8 | 空间文化再造 | 瀑布玫瑰裙/悬崖咖啡 |
| 9 | 节庆IP长期运营 | 清明系列/端午 |
| 10 | 用户共创UGC话题 | "我的隐藏打卡点" |

---

## 六、关键架构决策

### 6.1 为什么用OpenClaw Agent（而非自建）

| 选项 | 评估 | 结论 |
|------|------|------|
| OpenClaw + Agent Skills | ✅ **选择** | 25+模型供应商、cron调度、技能生态、本地优先 |
| 纯Python脚本 | ❌ 放弃 | 无Agent推理能力，无法自主决策 |
| 付费SaaS | ❌ 放弃 | 昂贵，无法定制决策框架，数据锁定 |

### 6.2 为什么用Verlet物理引擎（而非d3-force）

微信小程序不支持npm d3-force（ES模块+DOM依赖），图谱可视化使用**手写Verlet积分**物理引擎：

```javascript
const kRepulsion = 700;    // 库仑排斥力
const kSpring = 0.04;      // 胡克弹簧张力
const lLength = 120;        // 理想弹簧长度
const gravity = 0.02;       // 中心引力
const friction = 0.85;      // 阻尼衰减
```

性能：50个节点下稳定60fps。

### 6.3 为什么用双通道（脚本+CDP）采集

抖音创作者平台使用重度客户端渲染（SPA），Playwright脚本有时返回空数据或截断数据。CDP浏览器直连作为可靠降级通道：

```
Script → [成功?] → 解析使用
         ↓
      [失败?]  → CDP直连提取 → 解析使用
                  ↓
               [失败?] → 基于近期数据推断趋势
```

### 6.4 为什么必须用send_feishu_card.py

飞书默认message tool发送`msg_type: "post"`（富文本），**不渲染表格**。card脚本发送`msg_type: "interactive"` + `schema: "2.0"`：

```python
payload = {
    "receive_id": chat_id,
    "msg_type": "interactive",
    "content": json.dumps(card, ensure_ascii=False)
}
```

---

## 七、效果数据

### 7.1 运营指标

| 指标 | 数值 |
|------|------|
| **连续运行天数** | 30+天 |
| **日均产出决策简报** | 6-8份 |
| **日均消耗API token** | ~20万（DeepSeek-V4-Flash） |
| **已推送飞书卡片** | 180+张 |
| **活跃cron任务** | 23个 |
| **允许模型** | deepseek/deepseek-v4-flash（唯一） |

### 7.2 知识资产积累

| 资产类型 | 数量 | 说明 |
|---------|:----:|------|
| 竞品深度档案 | **20个** | 四平台全量分析 |
| 爆款案例 | **20+个** | 每周更新 |
| 爆款公式 | **10条** | 已验证的模式 |
| SOP规范 | **22个** | 标准化操作手册 |
| 历史数据 | **4年** | 2023-2026年客流 |
| Wiki文件 | **150+篇** | Markdown文档 |

### 7.3 业务影响

- **搜索指数回升**：电影小镇搜索指数W21环比**+24.51%**（品牌修复信号）
- **竞品排名**：从第7升至**第4位**
- **预测准确率**：从W18的60%持续提升至**W21的80%**
- **内容真空检测**：成功识别"搜索涨·综合跌"背离模式（5月22日验证）

---

## 八、技术栈

| 层级 | 技术 | 用途 |
|------|------|------|
| **AI框架** | OpenClaw v2026.5.20 | Agent运行时/cron/工具 |
| **大模型** | DeepSeek-V4-Flash | 推理/分析/生成 |
| **数据采集** | Python 3.12 + Playwright + CDP | 网页抓取/浏览器自动化 |
| **推送渠道** | 飞书Bot API (interactive card) | 报告推送至群聊 |
| **知识库** | Obsidian + karpathy-wiki | 三层抽象结构化Wiki |
| **操作系统** | macOS 26.4 (Darwin 25.4.0) ARM64 | 宿主机环境 |
| **硬件** | Mac Mini (2024) | 24/7本地运行 |
| **Node.js** | v25.8.2 | OpenClaw运行时 |
| **技能仓库** | ClawHub (13,729个可用技能) | 可扩展的Agent能力 |
| **版本控制** | Git + GitHub | 代码与Wiki仓库 |

---

## 九、快速导航

### 打开Obsidian Wiki
在Obsidian中打开 `wiki/` 目录。从 `wiki/index.md` 开始浏览。

### 查看每日报告
所有报告自动推送至飞书群。执行摘要记录在 `memory/YYYY-MM-DD.md`。

### 浏览代码
- `scripts/` — Python自动化脚本（45+文件）
- `wiki/` — 知识库（150+ Markdown文件）

### 反馈机制
系统包含反馈闭环。纠错记录在 `memory/topics/feedback/` 并影响后续行为。

---

*由AI构建，服务于人。2026年4月启动运行。*  
*由OpenClaw AI Agent自动部署与维护。*  
*最后系统更新：2026-05-25*
