# Scenic-Area-Marketing-CN
## AI-Powered Scenic Tourism Marketing System - Build by OpenClaw Agent

---

## 📋 TABLE OF CONTENTS

- [🇬🇧 ENGLISH](#-english-version)
- [🇨🇳 中文版](#-中文版)

---

# 🇬🇧 ENGLISH VERSION

## 1. WHAT IS THIS PROJECT?

**Scenic-Area-Marketing-CN** is a production-grade, fully automated scenic marketing intelligence system built on the [OpenClaw AI Agent framework](https://github.com/openclaw/openclaw). It runs 24/7 on a Mac Mini, autonomously collecting data from 8+ platforms, generating structured competitive intelligence reports, pushing decision-grade insights to Feishu (飞书) group chats, and archiving everything into an Obsidian knowledge graph.

The system serves **Jianye Movie Town (建业电影小镇)**, a cultural-tourism scenic spot in Zhengzhou, Henan, China, with an annual visitor target of 1.53 million and revenue target of ¥120 million for 2026.

This is **not** a demo or prototype. It has been running continuously for 30+ days without human intervention, producing **6-8 actionable decision briefs daily**.

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
**Source:** Douyin Creator Platform (抖音创作者平台) - subscription page
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

1. 清明上河园 (Qingming Riverside Landscape Garden) - #1 by search volume
2. 万岁山武侠城 (Wansui Mountain Martial Arts City) - #2
3. 银基动物王国 (Yinji Animal Kingdom) - #3 (亲子旺季 surge)
4. 郑州方特欢乐世界 (Zhengzhou Fantawild) - student pricing threat
5. 郑州海昌海洋公园 (Zhengzhou Haichang Ocean Park) - price war
6. 只有河南戏剧幻城 (Only Henan·Drama City) - 50%+ surge
7. 只有红楼梦戏剧幻城 (Only Dream of Red Mansions) - growth leader
8. **建业电影小镇 (Jianye Movie Town)** - baseline

### 3.2 Xiaohongshu Daily Report (小红书日报)

**Schedule:** Daily 10:00 CST
**Source:** Xiaohongshu Lingxi Backend (小红书灵犀) + Search Page + Official Account Profile

| Feature | Detail |
|---------|--------|
| **Official Account** | 98K followers, 2,196 notes, profile ID: `5fbb4f740000000001000410` |
| **Brand Metrics** | Audience Assets, Search Volume, Click Index, Reading Penetration Rate |
| **Competitor Keywords** | 7 competitors + self brand - weekly comparison |
| **Xiaohongshu Trend Data** | Search totals, YoY/DoD change, Interest rankings |
| **Viral Notes** | Top UGC notes with like/collect/comment counts |

### 3.3 Travel Intel Daily Report (文旅情报日报)

**Schedule:** Daily 13:00 CST
**Source:** Baidu Search + Weibo Trending + Industry News
**Scope:** National - NOT limited to 7 core competitors (expanded May 25)

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
**Scope:** National - actively discovers new competitors

**Deconstruction Framework:**
```
Case: [Title]
├─ 📊 Data Snapshot (likes/views/engagement)
├─ 🔍 Strategy Analysis (angle/emotion/format)
├─ 🎯 Replicability Assessment (confidence score)
└─ 💡 Movie Town Adaptation (concrete action plan)
```

**Recent Cases Analyzed:**
- "Li Bai Poetry Duel at West Lake" - 356M views, NPC random-poetry model → replicable
- "Red Rose Dress for Waterfall" - Chongdugou scenic makeover → 22K likes
- "520 Marriage Registration" at Wansui Mountain - civic ceremony in scenic spot
- "Korean Brand Copies Hanfu" - Weibo #15 trending → cultural IP defense

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

**Data Source:** `~/Desktop/2026游客量统计.csv` - daily passenger count spreadsheet

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
| **Annual Target** | **1,530,000** | - | - | - | - |

**Data Quality Status:** ⚠️ CSV last updated May 17, now 8 days stale - pending internal data sync

---

### 3.8 Passenger Flow Data Collection & Analysis Pipeline

#### Data Sources

| Source | Format | Location | Update Frequency |
|--------|--------|----------|-----------------|
| Primary: Daily spreadsheeet | `2026游客量统计.csv` (wide-format, 368 cols) | `~/Desktop/` | Irregular (internal dept) |
| Historical reference | `2023-2025年门票销售及客流统计数据表.xlsx` | `~/Desktop/` | Annual |
| Fallback: Feishu Bitable | `电影小镇-2026年数量统计` | Feishu multi-dim table | Daily (when CSV stale) |

#### CSV Structure & Parsing

The CSV is a complex wide-format spreadsheet (not a clean row-per-day format). The parser (`sync_obsidian_daily.py`) handles:

```
Row Layout:
  Row  0: 2023年参考 - 368 daily values (for YoY comparison)
  Row  1: 2024年参考 - 368 daily values
  Row  2: 2025年参考 - 32 values (partial year)
  Row  3: 天气备注 - Weather notes per day
  Rows 4-11: 门票细分 - Ticket breakdown by channel
  Row 12: 门票人数合计 - Total tickets sold (primary metric)
  Row 13: 门票收入金额 - Ticket revenue (¥)
  Row 14: 闸机入园人次 - Turnstile entry count (actual visitors)
  Rows 16-23: 预定数据 - Pre-sale data (evening/morning shifts)
  Row 25-28: 穿越德化街 - Show performance data
```

Column mapping: Column index 2 = January 1, column 3 = January 2, etc. (sequential days from Jan 1).

#### Analysis Pipeline

```
CSV file detected → Python parser reads wide format
  → Extract: Total tickets (Row 12), Turnstile (Row 14), Weather (Row 3)
  → Build: {date: {tickets, turnstile, weather}} dictionary
  → Calculate: Daily avg, WoW change, YoY comparison, YTD cumulative
  → Compare: vs annual target (1,530,000), monthly benchmarks
  → Output: Structured data → Feishu card (weekly report)
            → Memory log (daily append)
            → Obsidian Wiki (data.md update)
```

#### Sync Architecture

```
~/Desktop/2026游客量统计.csv
  │
  ├──→ scripts/sync_obsidian_daily.py  (auto-detects changes)
  │       │
  │       ├──→ workspace wiki/电影小镇/历史数据/2026年/数据.md
  │       │       (auto-updates last-updated timestamp)
  │       │
  │       └──→ Obsidian Vault (同步目标)
  │               (mirrors workspace wiki to user's Obsidian)
  │
  └──→ Agent weekly passenger insight task (周二 9:30)
          Reads CSV → generates 5-chapter card
          → pushes to Feishu group
          → logs to memory
```

#### Key Metrics & Derived Analysis

| Metric | Calculation | Used For |
|--------|------------|----------|
| Daily total | Row 12, col N | Base data point |
| Daily avg (month) | Monthly total ÷ days | Capacity planning |
| YTD completion | Cumulative ÷ 1,530,000 | Target tracking |
| WoW change | (This week - last week) ÷ last week | Trend detection |
| YoY change | (2026 - 2023/2024) ÷ baseline | Growth analysis |
| Channel breakdown | Rows 4-11 / total | Channel efficiency |
| Turnstile-to-ticket | Row 14 ÷ Row 12 | Redemption rate |

#### Current Data Status

| Metric | Value |
|--------|-------|
| Last CSV update | **2026-05-17** |
| Data age | **8 days stale** (⚠️) |
| YTD total | **656,067** |
| Target completion | **42.9%** |
| Days with data | **135 days** (Jan 1 - May 17) |
| Max single day | **33,411** (May 3, Labor Day) |

---

### 3.9 穿越德化街 (Chuanyue Dehua Street) Thematic Analysis

#### What Is 穿越德化街?

穿越德化街 is the **flagship indoor theatrical performance** at Jianye Movie Town - a time-travel immersive show set in 1930s Dehua Street, Zhengzhou. The venue underwent expansion in late 2024:

- **Before expansion (2023):** 450 seats per show
- **After expansion (2025+):** 1,140 seats per show (253% increase)
- **Expansion impact:** Oct-Nov 2024 closed for construction; Dec 2024 pressure-test only

#### Data Collection Method

The show data lives in the same passenger CSV (Rows 25-28):

| CSV Row | Data | Unit |
|---------|------|------|
| Row 25 | Date label | String ("1月1日") |
| Row 26 | Performances (场次) | Count |
| Row 27 | Seat inventory (库存) | Seats (1,140 per show) |
| Row 28 | Tickets sold (售卖) | Tickets |
| *(Derived)* | Occupancy rate (上座率) | Sold ÷ Inventory |

#### Key Analytical Dimensions

**1. Performance Cadence**
- Regular days: 1 show/day (1,140 seats)
- Peak weekends: 2-3 shows/day
- Holiday peaks: 5-6 shows/day (Labor Day 2026: 23 shows in 5 days)

**2. Occupancy Rate Tracking**

```
Occupancy = Tickets Sold ÷ (Performances × 1,140)

Thresholds:
  🔴 Below 40% → Under-performing, review pricing/content
  🟡 40-65%    → Normal range
  🟢 65-85%    → Good utilization
  💎 Above 85% → Capacity constraint, consider adding shows
```

**3. Conversion Rate (The Critical Metric)**

```
Conversion Rate = Show Audience ÷ Park Visitors

Historical:
  2023: 18.0% (baseline, pre-expansion)
  2024: 16.2% (dipped, pre-expansion)
  2025: 35.2% 🚀 (doubled post-expansion - product improvement)
  2026 YTD: 27.0% (tracking - Q1 low due to off-season)
```

**4. Ticket Mix (套票 vs 加购)**

| Metric | 2023 | 2024 | 2025 | 2026 Q1 |
|--------|:----:|:----:|:----:|:-------:|
| Package ticket % (套票) | 72.5% | 60.7% | 77.6% | 49.5% |
| Add-on ticket % (加购) | 27.5% | 39.3% | 22.4% | **50.5%** |
| Unit price (package) | - | - | ¥101.59 | - |
| Unit price (add-on) | - | - | ¥52.80 | - |

⚠️ **Key 2026 Q1 Signal:** Add-on share exceeded 50% for the first time - indicates packaging strategy shift or self-selection effect. Needs monitoring.

#### 2026 Q2 Update (from CSV, May 2025)

| Month | Days | Shows | Audience |
|:-----:|:----:|:-----:|:--------:|
| April | 30 | 52 | 37,581 |
| May (to 17th) | 17 | 47 | 33,565 |
| **Q2 Total** | **47** | **99** | **71,146** |

**May Labor Day Peak (May 1-4):** 5-6 shows/day, 92-93% occupancy - near capacity.

#### Data Update Workflow

```
CSV Rows 25-28 parsed → sync_obsidian_daily.py
  → Extracts: date, shows, inventory, sold
  → Calculates: occupancy %, conversion %, trend
  → Updates:
      wiki/电影小镇/演出节目/穿越德化街.md
      wiki/sources/穿越德化街数据分析.md
  → Weekly report: included in passenger insight card
```

---

### 3.10 Revenue Data Analysis

#### Data Sources

| Source | Data | Update |
|--------|------|--------|
| Passenger CSV Row 13 | 门票收入金额 (Ticket revenue) | Per CSV sync |
| 2023-2025年门票销售及客流统计数据表.xlsx | Historical revenue | Annual |
| 穿越德化街 Excel | 演出收入 (Show revenue) | As available |

#### Revenue Model Breakdown (Movie Town)

```
Total Revenue = Ticket Revenue + Non-Ticket Revenue
                     │                  │
                     ▼                  ▼
               × Daily Visitors    Dining, Shopping,
               × Average Ticket     Accommodation,
                 Price (ATP)        Photo, Experiences
```

**Revenue Channels (Ticket):**

| Channel | Description | Data Source |
|---------|-------------|-------------|
| Online individual | 线上散客 (mini-program, Douyin, Meituan) | CSV Rows 9-10 |
| Offline window | 窗口散客 (walk-up at gate) | CSV Row 10 |
| Travel agency | 旅行社 (group tours) | CSV Row 8 |
| Corporate client | 大客户 (corporate events) | CSV Row 7 |
| Study tours | 研学 (educational groups) | CSV Row 6 |

#### 穿越德化街 Revenue

| Year | Show Revenue | Note |
|:----:|:------------:|------|
| 2023 | ¥3,139万 | Pre-expansion baseline |
| 2024 | ¥2,675万 | Pre-expansion, -14.8% |
| 2025 | **¥4,266万** | 🚀 Post-expansion, +35.9% |
| 2026 Q1 | ¥632万 | Tracking |

#### Revenue Analysis Capabilities

| Analysis | Method | Output |
|----------|--------|--------|
| ATP (Avg Ticket Price) | Revenue ÷ Visitors | Pricing strategy input |
| Channel mix | Each channel ÷ total | Channel optimization |
| Non-ticket revenue share | (Total - Ticket) ÷ Total | Ancillary revenue tracking |
| Show revenue contribution | Show revenue ÷ Total | Product efficiency |

---

Every report, insight, and recommendation in this system follows a structured decision framework designed for real-world marketing execution.

### 4.1 Standard Judgment Layer

Every daily report contains this exact judgment structure:

| Dimension | Values | Description | Example |
|-----------|--------|-------------|---------|
| 🎯 **Impact Level** | 🔴高/🟡中/🟢低/📡噪音 | How much does this affect Movie Town? | 🔴高 - competitor 50%+ surge |
| 💡 **Action** | 跟风/借势/警惕/忽略 | What should the team do? | 跟风 - replicate the format |
| ⏰ **Window** | 今天/本周/不紧急 | When must action happen? | 今天 - trending window closes in 48h |
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
| "或许可以考虑" | Definitive suggestion: "推荐:..." |
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
│   ├── 演艺景区.md       - Performance venue characteristics
│   ├── 内容爆款规律.md    - Viral content patterns
│   ├── 景区营销漏斗.md    - Marketing funnel model
│   ├── 情绪营销.md       - Emotional marketing framework
│   ├── 平台算法规则.md    - Douyin/Xiaohongshu algorithm notes
│   └── ... (12 concept files)
│
├── entities/         ← Concrete objects & actors
│   ├── 建业电影小镇.md    - Movie Town profile
│   ├── 万岁山武侠城.md    - Competitor: Wansui Mountain
│   ├── 清明上河园.md      - Competitor: Qingming Garden
│   ├── 抖音平台.md        - Platform entity
│   ├── 小红书平台.md      - Platform entity
│   └── ... (12 entity files)
│
├── sources/          ← Data provenance & analysis
│   ├── 穿越德化街数据分析.md - Thematic data analysis
│   ├── 抖音指数追踪日报.md  - Daily tracking archive
│   ├── 竞品深度档案.md     - Profile sources
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
├── 基础档案.md            - Basic info, targets, annual goals
├── 战略框架.md            - SWOT, competitive positioning
├── 人群画像.md            - Douyin & Xiaohongshu audience profiles
├── 历史数据/              - Historical records (2023-2026)
│   ├── 2023年/数据.md
│   ├── 2024年/数据.md
│   ├── 2025年/数据.md
│   └── 数据.md (2026, updated to May 17)
├── 演出节目/
│   └── 穿越德化街.md      - 6-year show data + Q2 update
├── 运营方法/              - Operation SOPs
│   ├── 抖音运营方法.md
│   └── 小红书运营方法.md
└── 运营规划/              - Seasonal plans
    └── 环形水剧场与复古广场夏季运营方案.md
```

### 5.3 Competitor Intelligence Layer

```
COMPETITOR INTELLIGENCE (wiki/竞品分析/)
│
├── 竞品深度档案/          - 20 deep-profile reports
│   ├── 郑州方特欢乐世界深度分析.md
│   ├── 银基动物王国深度分析.md
│   ├── 清明上河园深度分析.md
│   ├── 大唐不夜城深度分析.md
│   ├── 阿那亚深度分析.md
│   └── ... (20 files, all completed)
│
├── 竞品动态追踪/          - Daily activity log (Apr 20-27)
├── 追踪数据/
│   ├── 抖音指数追踪.md
│   └── 小红书爆款追踪.md
│
└── 关键词池状态.md        - Checkpoint system for rotation
```

### 5.4 Viral Case Library (全国景区案例库)

```
CASE LIBRARY (wiki/全国景区案例库/)
│
├── index.md             - 10 viral formulas index
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
  /tmp/juLiang_cookies.json       - Douyin (proxied via 127.0.0.1:7897)
  /tmp/xiaohongshu_cookies.json   - Xiaohongshu (proxied)
  /tmp/weibo_cookies.json         - Weibo
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

## 7.5 TOOLS & OPERATIONAL ECOSYSTEM

Beyond the core modules, the system includes a rich ecosystem of supporting tools, operational mechanisms, and quality assurance processes.

---

### 7.5.1 Scripts Ecosystem (45+ Python Scripts)

The system includes a comprehensive Python scripts library that handles everything from data collection to card delivery.

| Script | Purpose | Type | Key Feature |
|--------|---------|:----:|-------------|
| `douyin_index_v9.py` | Douyin Index data collection | 📊 Data | Dual-channel (Playwright + CDP) |
| `competitor_keyword_v8.py` | Competitor keyword deep analysis | 📊 Data | 4-platform aggregation |
| `cdp_cookie_hub.py` | Cookie extraction from CDP browser | 🔧 Ops | Cross-platform (Douyin/XHS/Weibo) |
| `cdp_keyword_deep.py` | Deep keyword analysis via CDP | 📊 Data | Auto-rotate between Tab 2/4 |
| `cdp_collect.py` | General CDP data collector | 📊 Data | Tab-aware targeting |
| `xiaohongshu_crawl.py` | Xiaohongshu data collection | 📊 Data | Anti-ratelimit handling |
| `xhs_competitor_crawl.py` | XHS competitor page scraping | 📊 Data | Multi-keyword queue |
| `send_feishu_card.py` | Feishu interactive card sender | 📨 Push | schema 2.0 validation |
| `sync_obsidian_daily.py` | Obsidian Wiki sync agent | 🔄 Sync | CSV→Wiki→Vault pipeline |
| `query_passenger.py` | Passenger CSV query helper | 📊 Data | Date-range filtering |
| `self_check.py` | System self-diagnosis | 🔧 Ops | 8-point health checklist |
| `cdp_restore_tabs.py` | CDP browser tab recovery | 🔧 Ops | Auto-restore on crash |
| `case_library_scan.py` | Case library audit & repair | 🔄 Sync | Broken link detection |
| `industry_news_browser.py` | Travel intel news collector | 📊 Data | Multi-source aggregation |
| `llmwiki_ingest.py` | Wiki knowledge ingestion | 🔄 Sync | karpathy-wiki pattern |
| `build_xhs_card.py` | XHS report card builder | 🎨 Card | Visual spec compliant |
| `build_dashboard.py` | Dashboard HTML generator | 🎨 Card | Static page export |
| `validate_data.py` | Data integrity validator | ✅ QA | Staleness & completeness |
| `project_drift_check.py` | Project drift detection | ✅ QA | Content vs. reality mismatch |
| `wiki_drift_check.py` | Wiki drift detection | ✅ QA | Cross-reference validation |

> **Total: 45+ active scripts** (archived/legacy excluded)

---

### 7.5.2 Feishu Card System

All reports are delivered as Feishu interactive cards (not plain text). The card system has its own design specification, validation script, and fault recovery.

#### Card Architecture

```
{
  "schema": "2.0",                          // Required for rendering
  "header": {
    "title": {
      "tag": "plain_text",                   // NOT "lark_md"
      "content": "📊 抖音指数日报 | 2026-05-25"
    },
    "template": "blue"                       // Optional color accent
  },
  "body": {
    "elements": [                            // NOT root-level elements[]
      {
        "tag": "markdown",
        "content": "| 景区 | 搜索指数 | ... |"  // Tables inside markdown
      }
    ]
  }
}
```

#### Design Rules (Hard Constraints)

| Rule | Reason | Established |
|------|--------|------------|
| `header.title.tag` must be `"plain_text"` | `"lark_md"` causes rendering glitch | 2026-04-19 |
| Content goes in `body.elements[]`, **not** root `elements[]` | Schema compliance | 2026-04-19 |
| Tables inside markdown elements with `\|` pipe syntax | Feishu MD renderer | 2026-04-19 |
| Line breaks use `<br/>` not `\n` | Feishu ignores `\n` | 2026-04-10 |
| Must use `send_feishu_card.py`, not default message tool | `msg_type:"post"` doesn't render tables | 2026-05-25 |

#### Visual Spec

```
Section separator: ━━━━━━━━━━━━━━━━━━━━━━━━
Emoji hierarchy:   📌 → 🔍 → ⚠️ → 💡
Bold for emphasis: **text**
Code blocks:       `monospace text`
Decision output:   D<number> | <one-line title>
```

#### Card Sending Flow

```python
# send_feishu_card.py (key logic)

# 1. Validate card structure
validate_card(card)  → checks schema/header/elements

# 2. Get Feishu tenant token
token = get_token()  # client_credentials grant

# 3. Send with correct msg_type
payload = {
    "receive_id": chat_id,
    "msg_type": "interactive",  # NOT "post"
    "content": json.dumps(card, ensure_ascii=False)
}

# 4. Auto-retry on token expiry
if result.code in (99991663, 19001):
    token = refresh_token()
    retry()
```

#### Failure History & Recovery

| Date | Failure | Root Cause | Fix |
|:----:|---------|------------|-----|
| 05-25 | W22 marketing calendar shown as plain text | Agent used default `message` tool (msg_type: "post") instead of send_feishu_card.py | Updated all 9 cron jobs to enforce card script |
| 04-27 | Card table not rendering | `header.title.tag` was `"lark_md"` | Changed to `"plain_text"` |
| 04-19 | Elements in root instead of `body.elements[]` | Agent misread schema spec | Added validation in send_feishu_card.py |

---

### 7.5.3 Error Handling & Recovery

The system uses a **multi-layer fallback strategy** to ensure uninterrupted daily operations:

```
Layer 1: Primary Script
  └─ douyin_index_v9.py runs → [success?]
       ├─ Yes → parse + use data
       └─ No  → fall to Layer 2

Layer 2: CDP Direct Extraction
  └─ CDP browser navigates to target page → [success?]
       ├─ Yes → parse + use data
       └─ No  → fall to Layer 3

Layer 3: Trend Inference
  └─ Estimate from recent history + known patterns
       → mark as "estimated" (lower confidence)
```

#### Known Error Patterns & Responses

| Error Pattern | Trigger | Response | Recovery |
|-------------|---------|----------|----------|
| 503 Service Busy | DeepSeek API overload | Auto-retry at next cron cycle | No action needed (provider) |
| Cookie Expired | Douyin/XHS session timeout | CDP browser fallback; next sync cycle | Re-login via QR code |
| 667-char Truncation | Douyin SPA page partial render | Auto-switch to CDP extraction | Script update pending |
| Tool Execution Timeout | CDP browser busy/heavy load | Agent retries with 30s timeout | Monitor, no manual fix |
| Edit Failed | Wiki file write conflict | Agent retries with new content | Rare, auto-resolves |

#### Failure Alert Chain

Alert configuration per cron job (example):
```json
{
  "failureAlert": {
    "after": 2,              // Alert after 2 consecutive failures
    "channel": "feishu",
    "to": "oc_f109bcfd1bc7e166fd0ae077f70247cf",
    "cooldownMs": 60000       // 1 hour between alerts
  }
}
```

---

### 7.5.4 Agent Skill Ecosystem

The agent's capabilities are extensible through OpenClaw's Skills system. Skills are loaded from ClawHub (community registry) or custom-written.

#### Installed Skills Inventory

| Skill | Purpose | Installed | Type |
|-------|---------|:---------:|:----:|
| `wechat-mini-program-builder` | WeChat mini-program rapid dev | ✅ | 📱 Dev |
| `mini-program-dev` | Mini-program code templates & API | ✅ | 📱 Dev |
| `wechat-miniprogram-skill` | Mini-program beginner→expert guide | ✅ | 📱 Dev |
| `miniprogram-development` | General mini-program dev | ✅ | 📱 Dev |
| `frontend-design-3` | Frontend design specification | ✅ | 🎨 UI |
| `react-best-practices` | React best practices | ✅ | 💻 Code |
| `typescript-skills` | TypeScript skill set | ✅ | 💻 Code |
| `karpathy-coding-guidelines` | Karpathy coding principles | ✅ | 💻 Code |
| `debug-pro` | Systematic debugging | ✅ | 🔧 Dev |
| `api-tester` | HTTP request testing (GET/POST/PUT/DELETE) | ✅ | 🔧 Dev |
| `browser-automation` | Browser automation via natural language | ✅ | 🤖 Auto |
| `karpathy-guidelines` | General LLM coding wisdom | ✅ | 💻 Code |

**Total skills available: 59** (system + workspace + installed)

#### How Skills Work

```
Skill = SKILL.md (YAML frontmatter + Markdown instructions)
  → Agent reads skill at load time
  → Matches skill description against user request
  → Activates relevant skills
  → Filters by environment/config

Priority: Workspace > Local > Bundled
```

#### ClawHub Integration

- **Registry**: 13,729 community-built skills (as of Feb 2026)
- **Installer**: `clawhub install <skill-slug> --dir ~/.openclaw/workspace/skills`
- **Security**: VirusTotal integration for published skills

---

### 7.5.5 Memory & Learning System

The agent maintains both **episodic memory** (daily logs) and **semantic memory** (curated rules), plus a **feedback loop** for continuous improvement.

#### Memory Architecture

```
EPISODIC MEMORY (Raw logs)
memory/
├── YYYY-MM-DD.md        ← Daily execution records
├── YYYY-MM-DD.md.bak    ← Archived (when compacted)

SEMANTIC MEMORY (Curated)
MEMORY.md                ← Long-term rules (max 100 lines)
├── 铁律 (Ironclad rules)    — Violation must-correct
├── 关键洞察 (Key insights)  — Reusable patterns
├── [reference]              — System pointers (Feishu groups, file paths)
├── [project]                — Active project status
└── [feedback]               — Confirmed corrections/confirmations

STATE (Machine-readable)
memory/heartbeat-state.json   ← Heartbeat check tracking
memory/topics/               ← Topic-specific knowledge
  ├── feedback/               ← User corrections & confirmations
  ├── projects/               ← Long-running project state
  └── daily-tasks.md          ← Task roster
```

#### Feedback Loop

```
User says "不要" / "不对" / "停止"
  → Agent records correction in memory/topics/feedback/
  → Updates MEMORY.md rules if pattern confirmed
  → Adjusts future behavior

User says "对" / "很好" / "就这样"
  → Agent records confirmation (success pattern)
  → Reinforces existing rule
  → No change needed
```

#### Entry Format

```markdown
**规则：** [Brief rule description]
**Why:** [Why this rule exists]
**How to apply:** [When/where to apply]
```

#### Memory Categories

| Type | Purpose | Example |
|------|---------|--------|
| `[user]` | User role/preferences/goals | `user: 站长偏好详细数据报告` |
| `[feedback]` | Work guidance (correction+confirmation) | `feedback: 达人必须绑定转化链路` |
| `[project]` | Project status/targets | `project: 当前在优化多Agent系统` |
| `[reference]` | External system pointers | `reference: 飞书群 oc_xxx` |

#### Behavioral Rules (Examples from MEMORY.md)

| Rule | Type | Established |
|------|:----:|:-----------:|
| Weekly passenger report moved to Tuesday | 铁律 | 2026-05-25 |
| Feishu cards must use `send_feishu_card.py` | 铁律 | 2026-05-25 |
| Search scope: unlimited national (not 21 fixed) | 铁律 | 2026-05-25 |
| Data must be read from actual files, never guessing | 铁律 | 2026-04-22 |
| browser-use is banned (use Playwright scripts) | 铁律 | 2026-04-20 |
| Cron delivery mode: none (no redundant announce) | 铁律 | 2026-04-10 |

---

### 7.5.6 System Health & Operations

#### Daily Health Checks

The system self-diagnoses every 30 minutes via heartbeat:

```
Checklist:
  □ Cron jobs ran successfully (check lastError)
  □ CDP browser online (port 18800)
  □ Cookie files fresh (not expired)
  □ Passenger CSV not stale (last update < 14 days)
  □ Feishu Bot token valid
  □ Disk space adequate (< 90% usage)
  □ No orphan session files (> 100 = cleanup needed)
  □ Skills & plugins loaded without errors
```

#### Weekly Maintenance (Sundays 10:00-14:00)

| Task | Time | Description |
|------|:----:|-------------|
| Wiki Health Check | 10:00 | Verify all wiki links, fix broken refs |
| Codebase Drift Check | 10:00 | Detect workspace vs wiki content drift |
| Orphan Session Cleanup | 11:00 | Archive/deleted unused .jsonl transcript files |
| Skill Exploration | 14:00 | Discover new ClawHub skills, update skillset |
| Weekly Evolution Review | Weekly | System upgrade, memory consolidation, SOP audit |

#### CDP Browser Operations

| Property | Detail |
|----------|--------|
| **Port** | 18800 (dedicated instance) |
| **Target** | `host` (Mac Mini) |
| **Tab 0** | Xiaohongshu Lingxi Backend (trend/trendAnalyze) |
| **Tab 1** | Baidu Search |
| **Tab 2** | Douyin Subscription Page (my-subscript) |
| **Tab 3** | Douyin iframe |
| **Tab 4** | Douyin Keyword Page (arithmetic-index) |
| **Tab 5** | Douyin iframe |
| **Tab 6** | Xiaohongshu Explore Page (explore) |
| **Cookie Storage** | `/tmp/juLiang_cookies.json` (Douyin) |
| | `/tmp/xiaohongshu_cookies.json` (XHS) |
| | `/tmp/weibo_cookies.json` (Weibo) |
| **Proxy** | 127.0.0.1:7897 (for Douyin) |
| **Recovery**| `cdp_restore_tabs.py` on tab crash |

#### Cookie Rotation Strategy

```
Cron: 每日 08:05 (cdp_cookie_hub.py)
  → Connect to CDP browser (port 18800)
  → Navigate each platform tab
  → Extract cookies via document.cookie
  → Save to /tmp/<platform>_cookies.json
  → (Fallback: stale cookies still work for ~24h)
```

#### Data Quality Gates

| Gate | Check | Action on Failure |
|:----:|-------|-------------------|
| ✅ | Script returns all 8 venues | Partial data → switch to CDP |
| ✅ | Cookie age < 24h | Stale → CDP fallback, flag for refresh |
| ✅ | CSV last update < 2 weeks | Stale → flag in weekly report, request sync |
| ✅ | Feishu card delivery confirmed | Fail → retry with token refresh |
| ✅ | Wiki write succeeds | Conflict → retry with unique content |

---

### 7.5.7 Weekly Evolution System

Every Sunday, the system undergoes a structured evolution cycle:

| Phase | Action | Output |
|:-----:|--------|--------|
| 🧹 **Cleanup** | Archive orphan sessions, compact memory | Clean state |
| 📚 **Ingest** | Process new wiki content (raw/ → knowledge layer) | Updated wiki |
| 🔍 **Audit** | Check prediction accuracy, error patterns | Accuracy report |
| 🧠 **Learn** | Update decision rules based on validation results | Rule updates |
| 🚀 **Explore** | Search ClawHub for new useful skills | Skill updates |
| 📝 **Commit** | Git commit & push Wiki updates | GitHub sync |

---

### 7.5.8 Cost & Resource Management

| Resource | Usage | Management Strategy |
|----------|:-----:|-------------------|
| **API Tokens** | ~200K tokens/day (DeepSeek-V4-Flash) | Single model to max context window; isolated sessions prevent state bloat |
| **Disk** | 81Gi available / 228Gi total | Weekly orphan cleanup; Ollama models removed (reclaimed 26Gi) |
| **CDP Browser** | 6 permanent tabs | Tab-specific targeting prevents resource waste |
| **Cron Sessions** | 23 isolated sessions | Ephemeral (deleted after run); 30s-600s timeout per task |
| **Feishu API** | ~30 calls/day | Token caching reduces auth requests |

---

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
- **Weekly accuracy**: Improved from 60% (W18) to **80% (W21)** - 4 consecutive weeks of improvement
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
- `scripts/` - Python automation scripts (45+ files)
- `wiki/` - Knowledge base (150+ markdown files)
- `PROGRAMMER_AGENT.md` - Dedicated coding agent

### Give Feedback
The system includes a feedback loop mechanism. Corrections are recorded in `memory/topics/feedback/` and influence future behavior.

---

*Built by AI, for humans. Running since April 2026.*
*Automatically deployed & maintained by OpenClaw AI Agent.*
*Last system update: 2026-05-25*

---

## 11. FUTURE ROADMAP

The system is under active development. The following capabilities are planned or in progress:

### Phase 2: Data Depth Expansion (Q2 2026)

| Feature | Status | Description |
|---------|:------:|-------------|
| 🔴 **Viral Video Auto-Deconstruction** | 🟡 Planning | Automated scraping of Douyin trending videos → AI analysis → replicability assessment → Feishu card. Currently manual-selection. Target: fully automated daily pipeline. |
| 🔴 **Passenger Flow Real-Time Dashboard** | 🟡 Planning | Replace stale-CSV dependency with real-time API from park ticketing system. Auto-detect anomalies (daily deviation > 20%). |
| 🟣 **Revenue Tracking Module** | 🔴 Research | Integrate revenue data from ticketing system + show system. Automated ATP calculation, revenue mix analysis, non-ticket revenue tracking. |
| 🟣 **Competitor Pricing Monitor** | 🔴 Research |  Daily auto-check of competitor ticket prices (Douyin团购, Meituan, official mini-program). Alert on price changes > 10%. |

### Phase 3: Intelligence Upgrades (Q3 2026)

| Feature | Status | Description |
|---------|:------:|-------------|
| 🟢 **Weekly Prediction Accuracy** | ✅ Active | Already implemented (W21: 80%). Continuous improvement via learning loop. |
| 🟣 **Sentiment Analysis on UGC** | 🔴 Research | Auto-analyze sentiment trends on Xiaohongshu/Douyin comments. Early warning for negative sentiment spikes. |
| 🟣 **Automated Content Generation** | 🔴 Research | Generate draft content (short videos scripts, Xiaohongshu posts) based on trending formats. Human review before publishing. |
| 🟣 **Multi-Agent Collaboration** | 🟡 Planning | Specialized sub-agents: Competitor Agent, Content Agent, Passenger Agent, Review Agent - working in parallel under coordinator. |

### Phase 4: Open Platform (Q4 2026+)

| Feature | Status | Description |
|---------|:------:|-------------|
| 🟣 **Public API Layer** | 🔴 Research | Expose anonymized competitive intelligence data via API for other scenic spots. |
| 🟣 **Template Marketplace** | 🔴 Idea | Shareable SOP templates, decision frameworks, and report card templates. |
| 🟣 **Cross-Scene Benchmarking** | 🔴 Idea | Compare Movie Town metrics against national averages (seasonally adjusted). |
| 🟣 **WeChat Mini-Program Extension** | 🟡 In Dev | ChatWiki mini-program (holographic knowledge graph + AI ingestion center) - currently in active development. |

### Legend

| Icon | Meaning |
|:----:|---------|
| 🟢 | **Active** - deployed and running |
| 🟡 | **Planning** - design/spec in progress |
| 🔴 | **Research** - feasibility study |
| 💡 | **Idea** - concept, no active work |

---

# 🇨🇳 中文版

## 一、项目简介

**Scenic-Area-Marketing-CN** 是一个基于 [OpenClaw AI Agent框架](https://github.com/openclaw/openclaw) 构建的生产级全自动景区营销情报系统。系统 24/7 运行在 Mac Mini 上,自主完成从多平台数据采集、结构化竞争情报分析、决策级报告生成、飞书群推送,到 Obsidian 知识图谱归档的完整闭环。

系统服务于**建业电影小镇**--位于河南郑州的文化旅游景区,2026年度目标客流153万人次、营收1.2亿元。

这不是一个演示版或原型。系统已**连续无人工干预运行30+天**,日均产出 **6-8份可执行决策简报**。

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

**时间:** 每日10:30
**来源:** 抖音创作者平台·我的订阅页
**脚本:** `scripts/douyin_index_v9.py`

| 特性 | 详情 |
|------|------|
| **数据范围** | 8个景区:电影小镇+7核心竞品 |
| **指标** | 搜索指数 + 综合指数 + 日环比 |
| **采集** | 双通道:Playwright脚本 → CDP浏览器直连(自动降级) |
| **输出** | 排名表 + 异动标注(🔺🔻) |
| **降级机制** | 脚本返回空/截断数据时,自动切换CDP提取 |

**8个常规定义竞品(固定不变):**

| 排名 | 景区 | 日均搜索指数 | 特点 |
|:---:|------|:----------:|------|
| 🥇 | 清明上河园 | 31.5万 | IP联动(杨洋/雨霖铃) |
| 🥈 | 万岁山武侠城 | 5.5万 | 情绪价值内容/IP势能 |
| 🥉 | 银基动物王国 | 9.4万 | 亲子旺季启动 |
| 4 | 郑州方特欢乐世界 | 1.1万 | 学生低价促销 |
| 5 | 郑州海昌海洋公园 | 5,557 | 价格战 |
| 6 | 只有河南戏剧幻城 | 5,162 | 50%+暴涨 |
| 7 | 只有红楼梦戏剧幻城 | 3,509 | 增速领先 |
| - | **建业电影小镇** | **8,448** | **基准** |

### 3.2 小红书日报

**时间:** 每日10:00
**来源:** 小红书灵犀后台 + 搜索页 + 官方账号

| 特性 | 数据 |
|------|------|
| 官方账号 | 9.8万粉丝 / 2196篇笔记 |
| 品牌五维 | 人群资产+44.64%, 搜索量+22.9%, **阅读渗透率↓57.93%** |
| 决策输出 | 520方向正确 → 跟风提炼至618/端午 |
| 竞品覆盖 | 清上河园/万岁山/银基/只有河南/方特 |

### 3.3 文旅情报日报

**时间:** 每日13:00
**范围:** **全国范围**(5月25日起扩展,不限7个核心竞品)

**覆盖维度:**
- 🏛️ **政策资本**:政府旅游政策/补贴/监管变化
- 🏟️ **竞品活动**:新节目/活动/定价/IP合作
- 🌐 **行业趋势**:暑期旅游/体验经济/出行模式
- ⚠️ **风险预警**:安全事故/监管执法/负面舆情

**今日(5月25日)示例:**
- 河南省文旅发展大会刚闭幕(5.22-23安阳),发布300项惠民措施
- 5·19中国旅游日惠民补贴窗口5月31日关闭
- 文旅部第二批强制消费典型案例涉及河南新乡/洛阳

### 3.4 竞品爆款拆解

**时间:** 每日15:00
**来源:** 抖音热搜/小红书爆款/微博热搜
**范围:** **全国范围主动发现**

**拆解框架:**
```
案例: [标题]
├─ 📊 数据快照 (点赞/播放/互动)
├─ 🔍 策略分析 (角度/情绪/格式)
├─ 🎯 可复制性评估 (置信度评分)
└─ 💡 电影小镇适配建议 (具体行动)
```

**近期案例:**
- 李白西湖对诗 → 356万播放,NPC随机对诗模式 → 可复制
- 重渡沟瀑布玫瑰裙 → 2.2万赞,场景改造+话题矩阵
- 万岁山520景区领证 → 前26对赠年卡 → 建议七夕档落地
- 韩国品牌抄袭汉服 → 微博第15位 → 国潮汉服日策划

### 3.5 竞品关键词深度分析

**时间:** 每日16:00
**方法:** 轮换制 + 断点续做(`/tmp/daily_task_state.json`)

**四平台采集清单:**

| 平台 | 采集数据 | 工具 |
|------|---------|------|
| 🎵 抖音指数 | 搜索指数/综合指数/关联词TOP10/人群画像 | `cdp_keyword_deep.py` |
| 📕 小红书灵犀 | 搜索量/热搜词/上下游词 | CDP + JS注入 |
| 📕 小红书搜索页 | 爆款笔记TOP10/标签/热搜问题 | CDP浏览器 |
| 🌐 百度搜索 | 营收/客流量/票价/媒体报道 | CDP浏览器 |

**当前进度:已完成14/21个核心景区**(截至5月25日)

### 3.6 周度竞争格局报告(含准确率复盘)

**时间:** 周日10:00

系统每周计算自身预测准确率:

| 周次 | 准确率 | 趋势 |
|:----:|:------:|:----:|
| W18 | 60% | 基准 |
| W19 | 65% | +5pp |
| W20 | 70% | +5pp |
| **W21** | **80%** | **+10pp** |

**W21错误模式分析:**
- 执行层脱节:2次(建议已出但执行未跟上)
- 数据源断裂:1次(CSV断档8天)
- 信号误判:0次(持续改善)

---

### 3.7 客流数据采集与分析流水线

#### 数据源

| 来源 | 格式 | 位置 | 更新频率 |
|------|------|------|---------|
| 主要:每日客流表 | `2026游客量统计.csv`(宽表,368列) | `~/Desktop/` | 不定期(内部部门) |
| 历史参考 | `2023-2025年门票销售及客流统计数据表.xlsx` | `~/Desktop/` | 年度 |
| 降级:飞书多维表格 | `电影小镇-2026年数量统计` | 飞书多维表 | 每日(CSV断档时)|

#### CSV结构与解析

CSV是复杂的宽表格式(非标准的行-天结构),解析脚本 `sync_obsidian_daily.py` 处理方式:

```
行布局:
  Row  0: 2023年参考 - 368个日值(用于同比)
  Row  1: 2024年参考 - 368个日值
  Row  2: 2025年参考 - 32个值(部分年份)
  Row  3: 天气备注 - 每日天气
  Rows 4-11: 门票细分 - 各渠道拆分
  Row 12: 门票人数合计 - 主要指标
  Row 13: 门票收入金额 - 门票收入(元)
  Row 14: 闸机入园人次 - 实际入园
  Rows 16-23: 预定数据 - 晨更/夕更
  Row 25-28: 穿越德化街 - 演出数据
```

列映射:列索引2=1月1日,列3=1月2日,以此类推(从1月1日起的连续天)。

#### 数据分析流水线

```
检测到CSV文件 → Python解析宽表
  → 提取:门票合计(Row12)、闸机入园(Row14)、天气(Row3)
  → 构建:{日期: {门票, 闸机, 天气}} 字典
  → 计算:日均、周环比、同比、YTD累计
  → 对比:年度目标(153万)、月度基准
  → 输出:结构化数据 → 飞书卡片(周报)
            → 记忆追加(每日)
            → Obsidian Wiki(数据.md更新)
```

#### 同步架构

```
~/Desktop/2026游客量统计.csv
  │
  ├──→ scripts/sync_obsidian_daily.py(自动检测变更)
  │       │
  │       ├──→ workspace wiki/电影小镇/历史数据/2026年/数据.md
  │       │      (自动更新时间戳)
  │       │
  │       └──→ Obsidian Vault(同步目标)
  │              (镜像workspace wiki至用户Obsidian)
  │
  └──→ Agent周度客流洞察任务(周二9:30)
          读取CSV → 生成5章卡片
          → 推送至飞书群
          → 记录至memory
```

#### 核心指标与派生分析

| 指标 | 计算方式 | 用途 |
|------|---------|------|
| 日总量 | Row 12, 第N列 | 基础数据点 |
| 月日均 | 月度合计 ÷ 天数 | 容量规划 |
| YTD完成率 | 累计 ÷ 1,530,000 | 目标追踪 |
| 周环比 | (本周-上周)÷上周 | 趋势检测 |
| 同比 | (2026-2023/2024)÷基准 | 增长分析 |
| 渠道占比 | Rows 4-11 ÷ 合计 | 渠道效率 |
| 闸机转化率 | Row 14 ÷ Row 12 | 核销率 |

#### 当前数据状态

| 指标 | 数值 |
|------|------|
| CSV最后更新 | **2026-05-17** |
| 数据断档 | **8天**(⚠️ 需内部同步) |
| YTD合计 | **656,067** |
| 目标完成率 | **42.9%** |
| 有数据天数 | **135天**(1月1日-5月17日) |
| 单日最高 | **33,411**(5月3日,五一) |

---

### 3.8 穿越德化街主题演出数据分析

#### 穿越德化街是什么?

穿越德化街是建业电影小镇的**旗舰室内剧场演出**--一场设定在1930年代郑州德化街的穿越沉浸式大秀。剧场于2024年底完成扩建:

- **扩建前(2023):** 每场450座
- **扩建后(2025+):** 每场1,140座(+253%)
- **扩建影响:** 2024年10-11月闭园施工,12月仅压力测试

#### 数据采集方式

演出数据同样存储在客流CSV中(Rows 25-28):

| CSV行 | 数据 | 单位 |
|-------|------|------|
| Row 25 | 日期标签 | 字符串("1月1日")|
| Row 26 | 场次 | 计数 |
| Row 27 | 库存(座位总量) | 座位数(每场1,140) |
| Row 28 | 售卖(售出门票) | 张数 |
| *(派生)* | 上座率 | 售卖÷库存 |

#### 关键分析维度

**1. 演出节奏**
- 平日:1场/天(1,140座)
- 高峰周末:2-3场/天
- 节假日峰值:5-6场/天(2026五一5天23场)

**2. 上座率追踪**

```
上座率 = 售出门票 ÷ (场次 × 1,140)

阈值:
  🔴 低于40% → 表现不佳,需检查定价/内容
  🟡 40-65%  → 正常范围
  🟢 65-85%  → 良好利用
  💎 高于85% → 容量瓶颈,考虑加场
```

**3. 转化率(核心指标)**

```
转化率 = 观演人次 ÷ 入园人次

历史数据:
  2023: 18.0%(基准,扩建前)
  2024: 16.2%(下降,扩建前)
  2025: 35.2% 🚀(翻倍,扩建后--产品力提升)
  2026 YTD: 27.0%(追踪中--Q1淡季低频)
```

**4. 票种结构(套票 vs 加购)**

| 指标 | 2023 | 2024 | 2025 | 2026 Q1 |
|------|:----:|:----:|:----:|:-------:|
| 套票占比 | 72.5% | 60.7% | 77.6% | 49.5% |
| 加购占比 | 27.5% | 39.3% | 22.4% | **50.5%** |
| 套票单价 | - | - | ¥101.59 | - |
| 加购单价 | - | - | ¥52.80 | - |

⚠️ **2026 Q1关键信号:** 加购占比首次超过50%--可能表明打包策略转变或客群自选效应。需持续监测。

#### 2026 Q2更新(来自CSV,截至5月17日)

| 月份 | 天数 | 场次 | 观演人次 |
|:----:|:----:|:----:|:--------:|
| 4月 | 30 | 52 | 37,581 |
| 5月(至17日)| 17 | 47 | 33,565 |
| **Q2合计** | **47** | **99** | **71,146** |

**五一峰值(5月1日-4日):** 5-6场/天,92-93%上座率--接近容量上限。

#### 数据更新工作流

```
CSV Rows 25-28 解析 → sync_obsidian_daily.py
  → 提取:日期、场次、库存、售卖
  → 计算:上座率、转化率、趋势
  → 更新:
      wiki/电影小镇/演出节目/穿越德化街.md
      wiki/sources/穿越德化街数据分析.md
  → 周报:纳入客流洞察卡片
```

---

### 3.9 营收数据分析

#### 数据源

| 来源 | 数据 | 更新 |
|------|------|------|
| 客流CSV Row 13 | 门票收入金额 | 随CSV同步 |
| 2023-2025年门票销售及客流统计表.xlsx | 历史营收 | 年度 |
| 穿越德化街Excel | 演出收入 | 按需获取 |

#### 营收模型(电影小镇)

```
总营收 = 门票收入 + 非门票收入
            │           │
            ▼           ▼
     × 日客流    餐饮、购物、住宿、
     × 平均票价  旅拍、体验项目
```

**门票收入渠道:**

| 渠道 | 说明 | 数据源 |
|------|------|--------|
| 线上散客 | 小程序/抖音/美团 | CSV Rows 9-10 |
| 窗口散客 | 现场购票 | CSV Row 10 |
| 旅行社 | 团队游 | CSV Row 8 |
| 大客户 | 企业活动 | CSV Row 7 |
| 研学 | 教育团体 | CSV Row 6 |

#### 穿越德化街营收

| 年份 | 演出收入 | 说明 |
|:----:|:--------:|------|
| 2023 | ¥3,139万 | 扩建前基准 |
| 2024 | ¥2,675万 | 扩建前,-14.8% |
| 2025 | **¥4,266万** | 🚀 扩建后,+35.9% |
| 2026 Q1 | ¥632万 | 追踪中 |

#### 营收分析能力

| 分析 | 方法 | 输出 |
|------|------|------|
| 平均票价(ATP) | 收入÷客流 | 定价策略输入 |
| 渠道占比 | 各渠道÷合计 | 渠道优化 |
| 非门票收入占比 | (总-门票)÷总 | 辅助收入追踪 |
| 演出收入贡献 | 演出收入÷总营收 | 产品效率 |

### 4.1 标准判断层

| 维度 | 取值 | 说明 |
|------|------|------|
| 🎯 **影响等级** | 🔴高/🟡中/🟢低/📡噪音 | 对电影小镇的实际影响程度 |
| 💡 **建议动作** | 跟风/借势/警惕/忽略 | 团队应该做什么 |
| ⏰ **执行窗口** | 今天/本周/不紧急 | 必须在什么时间前行动 |
| ⚠️ **不做代价** | 明确的损失陈述 | 不做的后果量化 |

### 4.2 决策简报格式(D序列)

```
D<序号> | <一句话标题>
├─ 简单理解:一句话解释
├─ 做错风险:不执行的后果
├─ 推荐+理由:具体建议 + 置信度评分
└─ 利弊:收益 vs 成本/精力
```

### 4.3 禁止用语(2026-05-19强制执行)

| ❌ 禁止 | ✅ 替换为 |
|---------|----------|
| "值得关注" | "本周必须执行" 或 具体优先级 |
| "仅供参考" | 具体建议+置信度 |
| "或许可以考虑" | "推荐:..." |
| "需要进一步分析" | 明确判断 或 明确"信息不足" |

---

## 五、知识管理(Obsidian Wiki)

### 5.1 三层知识抽象

```
KNOWLEDGE LAYER (wiki/)
│
├── concepts/         ← 抽象模式与理论
│   ├── 演艺景区.md        - 演艺景区特征
│   ├── 内容爆款规律.md    - 爆款内容模式
│   ├── 景区营销漏斗.md    - 漏斗模型
│   ├── 情绪营销.md       - 情绪营销框架
│   ├── 平台算法规则.md    - 抖音/小红书算法
│   └── ... (共12个概念文件)
│
├── entities/         ← 具体对象
│   ├── 建业电影小镇.md    - 自身档案
│   ├── 万岁山武侠城.md    - 竞品
│   ├── 清明上河园.md      - 竞品
│   ├── 抖音平台.md        - 平台实体
│   ├── 小红书平台.md      - 平台实体
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
├── 基础档案.md        - 基本信息/年度目标(153万/1.2亿)
├── 战略框架.md        - SWOT/竞争定位
├── 人群画像.md        - 抖音/小红书用户画像
├── 历史数据/          - 2023-2026历年客流
│   ├── 数据.md        - ✅ YTD 656,067 / 42.9%
│   ├── 规律洞察.md    - 春节/暑期/国庆三峰值
│   └── 2023年/2024年/2025年/
├── 演出节目/
│   └── 穿越德化街.md  - 6年数据 + Q2更新
│                       (240场/177,076人次/转化率27.0%)
├── 运营方法/          - 抖音/小红书运营SOP
└── 运营规划/          - 夏季运营方案
```

### 5.3 竞品情报层

```
COMPETITOR INTELLIGENCE (wiki/竞品分析/)
├── 竞品深度档案/      - 20个全国景区深度分析
│   ├── 郑州方特欢乐世界深度分析.md
│   ├── 银基动物王国深度分析.md
│   ├── 清明上河园深度分析.md
│   ├── 大唐不夜城深度分析.md
│   ├── 阿那亚深度分析.md
│   └── ... (20个文件,全部完成)
│
├── 竞品动态追踪/      - 每日动态日志 (4月20-27日)
├── 追踪数据/
│   ├── 抖音指数追踪.md
│   └── 小红书爆款追踪.md
│
└── 关键词池状态.md    - 断点续做检查点
```

### 5.4 全国景区案例库

```
CASE LIBRARY (wiki/全国景区案例库/)
├── index.md          - 10条爆款公式索引
└── 20+ 按周归档案例
    ├── 大唐不夜城夜游标杆-2026W17.md
    ├── 万岁山武侠城标杆-2026W17.md
    ├── 打铁花跨景区爆款现象-2026W17.md
    ├── 乌镇住宿早茶客46%复购率-2026W22.md
    └── ...
```

**10条爆款公式(W22更新):**

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

### 6.1 为什么用OpenClaw Agent(而非自建)

| 选项 | 评估 | 结论 |
|------|------|------|
| OpenClaw + Agent Skills | ✅ **选择** | 25+模型供应商、cron调度、技能生态、本地优先 |
| 纯Python脚本 | ❌ 放弃 | 无Agent推理能力,无法自主决策 |
| 付费SaaS | ❌ 放弃 | 昂贵,无法定制决策框架,数据锁定 |

### 6.2 为什么用Verlet物理引擎(而非d3-force)

微信小程序不支持npm d3-force(ES模块+DOM依赖),图谱可视化使用**手写Verlet积分**物理引擎:

```javascript
const kRepulsion = 700;    // 库仑排斥力
const kSpring = 0.04;      // 胡克弹簧张力
const lLength = 120;        // 理想弹簧长度
const gravity = 0.02;       // 中心引力
const friction = 0.85;      // 阻尼衰减
```

性能:50个节点下稳定60fps。

### 6.3 为什么用双通道(脚本+CDP)采集

抖音创作者平台使用重度客户端渲染(SPA),Playwright脚本有时返回空数据或截断数据。CDP浏览器直连作为可靠降级通道:

```
Script → [成功?] → 解析使用
         ↓
      [失败?]  → CDP直连提取 → 解析使用
                  ↓
               [失败?] → 基于近期数据推断趋势
```

### 6.4 为什么必须用send_feishu_card.py

飞书默认message tool发送`msg_type: "post"`(富文本),**不渲染表格**。card脚本发送`msg_type: "interactive"` + `schema: "2.0"`:

```python
payload = {
    "receive_id": chat_id,
    "msg_type": "interactive",
    "content": json.dumps(card, ensure_ascii=False)
}
```

---

## 六点五、工具与运维生态

除核心模块外，系统还包含丰富的支持工具、运维机制和质量保障流程。

---

### 6.5.1 脚本生态（45+个Python脚本）

| 脚本 | 用途 | 类型 | 特点 |
|------|------|:----:|------|
| `douyin_index_v9.py` | 抖音指数采集 | 📊 数据 | 双通道(Playwright+CDP) |
| `competitor_keyword_v8.py` | 竞品关键词深度分析 | 📊 数据 | 四平台聚合 |
| `cdp_cookie_hub.py` | CDP浏览器Cookie提取 | 🔧 运维 | 跨平台(抖音/小红书/微博) |
| `cdp_keyword_deep.py` | CDP深度关键词分析 | 📊 数据 | Tab2/4自动切换 |
| `cdp_collect.py` | 通用CDP数据采集 | 📊 数据 | Tab感知定位 |
| `xiaohongshu_crawl.py` | 小红书数据采集 | 📊 数据 | 反限流处理 |
| `xhs_competitor_crawl.py` | 小红书竞品页面抓取 | 📊 数据 | 多关键词队列 |
| `send_feishu_card.py` | 飞书交互卡片发送 | 📨 推送 | schema 2.0验证 |
| `sync_obsidian_daily.py` | Obsidian Wiki同步 | 🔄 同步 | CSV→Wiki→Vault流水线 |
| `query_passenger.py` | 客流CSV查询助手 | 📊 数据 | 日期范围筛选 |
| `self_check.py` | 系统自检诊断 | 🔧 运维 | 8项健康检查清单 |
| `cdp_restore_tabs.py` | CDP浏览器Tab恢复 | 🔧 运维 | 崩溃自动恢复 |
| `case_library_scan.py` | 案例库审计修复 | 🔄 同步 | 断链检测 |
| `industry_news_browser.py` | 文旅情报新闻采集 | 📊 数据 | 多源聚合 |
| `llmwiki_ingest.py` | Wiki知识接入 | 🔄 同步 | karpathy-wiki模式 |
| `validate_data.py` | 数据完整性验证 | ✅ 质控 | 过时&完整性检查 |
| `wiki_drift_check.py` | Wiki漂移检测 | ✅ 质控 | 交叉引用验证 |

> **总计：45+个活跃脚本**（不含已归档/遗留脚本）

---

### 6.5.2 飞书卡片系统

所有报告以飞书交互卡片（interactive card）形式推送，非纯文本。卡片系统拥有独立的设计规范、验证脚本和故障恢复机制。

#### 卡片架构

```json
{
  "schema": "2.0",                          // 必须
  "header": {
    "title": {
      "tag": "plain_text",                   // 非"lark_md"
      "content": "📊 抖音指数日报 | 2026-05-25"
    },
    "template": "blue"
  },
  "body": {
    "elements": [
      {
        "tag": "markdown",
        "content": "| 景区 | 搜索指数 | ... |"
      }
    ]
  }
}
```

#### 设计规则（硬约束）

| 规则 | 原因 | 建立时间 |
|------|------|---------|
| `header.title.tag`必须为`"plain_text"` | `"lark_md"`导致渲染异常 | 2026-04-19 |
| 内容放在`body.elements[]`，非根级`elements[]` | Schema合规 | 2026-04-19 |
| 表格用`\|`管道符放在markdown元素内 | 飞书MD解析器 | 2026-04-19 |
| 换行用`<br/>`不用`\n` | 飞书忽略`\n` | 2026-04-10 |
| 必须用`send_feishu_card.py`，非默认message tool | `msg_type:"post"`不渲染表格 | 2026-05-25 |

#### 视觉规范

```
章节分隔符：━━━━━━━━━━━━━━━━━━━━━━━━
Emoji层级：  📌 → 🔍 → ⚠️ → 💡
加粗强调：   **文字**
等宽代码：   `等宽文字`
决策输出：   D<序号> | <一行标题>
```

#### 发送流程

```python
# 1. 验证卡片结构
validate_card(card)  → 检查schema/header/elements

# 2. 获取飞书tenant token
token = get_token()  # client_credentials授权

# 3. 以正确msg_type发送
payload = {
    "receive_id": chat_id,
    "msg_type": "interactive",  # 非"post"
    "content": json.dumps(card, ensure_ascii=False)
}

# 4. Token过期自动重试
if result.code in (99991663, 19001):
    token = refresh_token()
    retry()
```

#### 故障记录与恢复

| 日期 | 故障 | 根因 | 修复 |
|:----:|------|------|------|
| 05-25 | W22营销日历显示为纯文本 | Agent用了默认message tool(msg_type:"post") | 9个cron任务统一为send_feishu_card.py |
| 04-27 | 卡片表格不渲染 | `header.title.tag`为`"lark_md"` | 改为`"plain_text"` |
| 04-19 | elements在根级而非`body.elements[]` | Agent误解schema | 在send_feishu_card.py中增加验证 |

---

### 6.5.3 错误处理与恢复

系统使用**多层降级策略**保障每日运行不间断：

```
第一层：主脚本
  └─ douyin_index_v9.py运行 → [成功?]
       ├─ 是 → 解析+使用
       └─ 否 → 降级至第二层

第二层：CDP直连提取
  └─ CDP浏览器导航至目标页 → [成功?]
       ├─ 是 → 解析+使用
       └─ 否 → 降级至第三层

第三层：趋势推断
  └─ 基于近期数据+已知模式估算
       → 标记为"估算"（低置信度）
```

#### 已知错误模式及响应

| 错误模式 | 触发条件 | 响应 | 恢复方式 |
|---------|---------|------|---------|
| 503服务繁忙 | DeepSeek API过载 | 下一cron周期自动重试 | 无需操作（服务商） |
| Cookie过期 | 抖音/小红书登录超时 | CDP浏览器降级；下一同步周期 | 扫码重新登录 |
| 667字符截断 | 抖音SPA页面部分渲染 | 自动切换CDP提取 | 等待脚本更新 |
| 工具执行超时 | CDP浏览器繁忙/负载高 | Agent以30s超时重试 | 监控，无需手修 |
| 编辑失败 | Wiki文件写入冲突 | Agent重试新内容 | 极少发生，自动恢复 |

#### 故障告警链

cron任务的告警配置示例：
```json
{
  "failureAlert": {
    "after": 2,              // 连续2次失败后告警
    "channel": "feishu",
    "to": "oc_f109bcfd1bc7e166fd0ae077f70247cf",
    "cooldownMs": 60000       // 告警间隔1小时
  }
}
```

---

### 6.5.4 Agent技能生态

Agent的能力通过OpenClaw的Skills系统可扩展。技能来源：ClawHub（社区仓库）+ 自定义编写。

#### 已安装技能清单

| 技能 | 用途 | 类型 |
|------|------|:----:|
| `wechat-mini-program-builder` | 微信小程序快速搭建 | 📱 开发 |
| `mini-program-dev` | 小程序代码模板&API | 📱 开发 |
| `wechat-miniprogram-skill` | 小程序从入门到精通指南 | 📱 开发 |
| `miniprogram-development` | 通用小程序开发 | 📱 开发 |
| `frontend-design-3` | 前端设计规范 | 🎨 UI |
| `react-best-practices` | React最佳实践 | 💻 代码 |
| `typescript-skills` | TypeScript技能集 | 💻 代码 |
| `karpathy-coding-guidelines` | Karpathy编码准则 | 💻 代码 |
| `debug-pro` | 系统化调试 | 🔧 开发 |
| `api-tester` | HTTP请求测试(GET/POST/PUT/DELETE) | 🔧 开发 |
| `browser-automation` | 自然语言浏览器自动化 | 🤖 自动化 |
| `karpathy-guidelines` | LLM编程通用智慧 | 💻 代码 |

**可用技能总数：59**（系统内置 + 工作区 + 已安装）

---

### 6.5.5 记忆与学习系统

Agent维护两种记忆：**情景记忆**（日常日志）和**语义记忆**（精炼规则），以及**反馈闭环**实现持续改进。

#### 记忆架构

```
情景记忆（原始日志）
memory/
├── YYYY-MM-DD.md        ← 每日执行记录

语义记忆（精炼）
MEMORY.md                ← 长期规则（最长100行）
├── 铁律（不可违反）
├── 关键洞察（可复用模式）
├── [reference]（系统指针）
├── [project]（项目状态）
└── [feedback]（纠错/确认）

状态（机器可读）
memory/heartbeat-state.json
memory/topics/
  ├── feedback/          ← 用户纠错&确认
  └── projects/          ← 长运行项目状态
```

#### 反馈闭环

```
用户说"不要"/"不对"/"停止"
  → Agent记录纠错至memory/topics/feedback/
  → 如模式确认则更新MEMORY.md规则
  → 调整后续行为

用户说"对"/"很好"/"就这样"
  → Agent记录确认（成功模式）
  → 强化已有规则
  → 无需变更
```

#### 记忆分类

| 类型 | 用途 | 示例 |
|------|------|------|
| `[user]` | 用户角色/偏好/目标 | `user: 站长偏好详细数据报告` |
| `[feedback]` | 工作指导（纠错+确认） | `feedback: 达人必须绑定转化链路` |
| `[project]` | 项目状态/目标 | `project: 当前在优化多Agent系统` |
| `[reference]` | 外部系统指针 | `reference: 飞书群 oc_xxx` |

---

### 6.5.6 系统健康与运维

#### 每日健康检查（每30分钟心跳检测）

```
检查清单：
  □ cron任务正常运行（检查lastError）
  □ CDP浏览器在线（端口18800）
  □ Cookie文件未过期
  □ 客流CSV未过时（更新<14天）
  □ 飞书Bot Token有效
  □ 磁盘空间充足（<90%）
  □ 无orphan会话文件（>100需清理）
  □ Skills&Plugins加载无错误
```

#### 每周维护（周日10:00-14:00）

| 任务 | 时间 | 说明 |
|------|:----:|------|
| Wiki健康检查 | 10:00 | 验证所有Wiki链接，修复断链 |
| 代码漂移检查 | 10:00 | 检测workspace与Wiki内容漂移 |
| Orphan会话清理 | 11:00 | 归档/删除未使用的.jsonl文件 |
| 技能探索 | 14:00 | 发现ClawHub新技能，更新技能集 |
| 周度演进评审 | 每周 | 系统升级、记忆整理、SOP审计 |

#### CDP浏览器运维

| 属性 | 详情 |
|------|------|
| **端口** | 18800 |
| **目标** | `host`（Mac Mini） |
| **Tab 0** | 小红书灵犀后台 |
| **Tab 1** | 百度搜索 |
| **Tab 2** | 抖音订阅页 |
| **Tab 3** | 抖音iframe |
| **Tab 4** | 抖音关键词页 |
| **Tab 5** | 抖音iframe |
| **Tab 6** | 小红书探索页 |
| **Cookie存储** | `/tmp/juLiang_cookies.json`（抖音） |
| | `/tmp/xiaohongshu_cookies.json`（小红书） |
| | `/tmp/weibo_cookies.json`（微博） |
| **代理** | 127.0.0.1:7897（抖音专用） |
| **恢复** | `cdp_restore_tabs.py` Tab崩溃恢复 |

#### 数据质量门控

| 门控 | 检查项 | 失败处理 |
|:----:|--------|---------|
| ✅ | 脚本返回全部8个景区 | 部分数据→切换CDP |
| ✅ | Cookie时效<24h | 过期→CDP降级，标记需刷新 |
| ✅ | CSV更新<2周 | 过期→周报标记，请求同步 |
| ✅ | 飞书卡片送达确认 | 失败→Token刷新重试 |
| ✅ | Wiki写入成功 | 冲突→唯一内容重试 |

---

### 6.5.7 周度演进系统

每周日，系统执行结构化演进周期：

| 阶段 | 行动 | 产出 |
|:----:|------|------|
| 🧹 **清理** | 归档orphan会话、压缩记忆 | 干净状态 |
| 📚 **接入** | 处理新Wiki内容（raw/→知识层） | 更新Wiki |
| 🔍 **审计** | 检查预测准确率、错误模式 | 准确率报告 |
| 🧠 **学习** | 基于验证结果更新决策规则 | 规则更新 |
| 🚀 **探索** | 搜索ClawHub新技能 | 技能更新 |
| 📝 **提交** | Git commit & push Wiki更新 | GitHub同步 |

---

### 6.5.8 成本与资源管理

| 资源 | 用量 | 管理策略 |
|------|:----:|---------|
| **API Token** | ~20万token/天 | 单一模型最大化上下文窗口；isolated session防止状态膨胀 |
| **磁盘** | 81Gi可用/228Gi总 | 每周orphan清理；已删除Ollama模型（回收26Gi） |
| **CDP浏览器** | 6个永久Tab | Tab级精确定位防止资源浪费 |
| **Cron会话** | 23个isolated session | 临时性（运行后删除）；每任务30s-600s超时 |
| **飞书API** | ~30次调用/天 | Token缓存减少认证请求 |

---

### 7.1 运营指标

| 指标 | 数值 |
|------|------|
| **连续运行天数** | 30+天 |
| **日均产出决策简报** | 6-8份 |
| **日均消耗API token** | ~20万(DeepSeek-V4-Flash) |
| **已推送飞书卡片** | 180+张 |
| **活跃cron任务** | 23个 |
| **允许模型** | deepseek/deepseek-v4-flash(唯一) |

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

- **搜索指数回升**:电影小镇搜索指数W21环比**+24.51%**(品牌修复信号)
- **竞品排名**:从第7升至**第4位**
- **预测准确率**:从W18的60%持续提升至**W21的80%**
- **内容真空检测**:成功识别"搜索涨·综合跌"背离模式(5月22日验证)

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
- `scripts/` - Python自动化脚本(45+文件)
- `wiki/` - 知识库(150+ Markdown文件)

### 反馈机制
系统包含反馈闭环。纠错记录在 `memory/topics/feedback/` 并影响后续行为。

---

## 十、未来规划

系统正在持续演进中，以下功能已在规划或开发中：

### Phase 2：数据深度扩展（2026 Q2）

| 功能 | 状态 | 说明 |
|------|:----:|------|
| 🔴 **爆款视频自动拆解** | 🟡 规划中 | 自动爬取抖音热门视频 → AI分析 → 可复制性评估 → 飞书卡片。当前为手动选择，目标：全自动每日流水线。 |
| 🔴 **客流实时看板** | 🟡 规划中 | 替换stale CSV依赖，接入园区票务系统实时API。自动检测异常（日偏差>20%）。 |
| 🟣 **营收追踪模块** | 🔴 研究中 | 整合票务+演出系统营收数据。自动ATP计算、营收结构分析、非门票收入追踪。 |
| 🟣 **竞品定价监控** | 🔴 研究中 | 每日自动检查竞品票价（抖音团购/美团/官方小程序）。价格变动>10%即时告警。 |

### Phase 3：智能升级（2026 Q3）

| 功能 | 状态 | 说明 |
|------|:----:|------|
| 🟢 **周度预测准确率** | ✅ 已运行 | 已实现（W21: 80%）。通过学习闭环持续改进。 |
| 🟣 **UGC情感分析** | 🔴 研究中 | 自动分析小红书/抖音评论情感趋势。负面情绪飙升早期预警。 |
| 🟣 **自动内容生成** | 🔴 研究中 | 基于热门格式生成内容草稿（短视频脚本/小红书笔记）。人工审核后发布。 |
| 🟣 **多Agent协作** | 🟡 规划中 | 专业化子Agent：竞品Agent/内容Agent/客流Agent/复盘Agent——在协调者下并行工作。 |

### Phase 4：开放平台（2026 Q4+）

| 功能 | 状态 | 说明 |
|------|:----:|------|
| 🟣 **公共API层** | 🔴 研究中 | 对外暴露匿名化竞品情报数据API，供其他景区参考。 |
| 🟣 **模板市场** | 💡 构想 | 可分享的SOP模板、决策框架、报告卡片模板。 |
| 🟣 **跨场景对标** | 💡 构想 | 电影小镇指标与全国均值对比（季节性调整）。 |
| 🟣 **微信小程序延展** | 🟡 开发中 | ChatWiki小程序（全息知识图谱 + AI析构中心）—— 开发进行中。 |

### 状态说明

| 图标 | 含义 |
|:----:|------|
| 🟢 | **已上线** — 正在运行 |
| 🟡 | **规划中** — 设计/方案进行中 |
| 🔴 | **研究中** — 可行性验证 |
| 💡 | **构想** — 概念阶段 |

---

*由AI构建，服务于人。2026年4月启动运行。*  
*由OpenClaw AI Agent自动部署与维护。*  
*最后系统更新：2026-05-25*
