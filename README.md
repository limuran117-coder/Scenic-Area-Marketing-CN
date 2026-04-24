# 🎬 Scenic Area Marketing Agent

> An AI-powered marketing operations agent for scenic area management, featuring multi-platform data monitoring, competitor analysis, and passenger flow insights.

[English](#features) | [中文说明](#中文说明) | [核心能力](#核心能力) | [技术架构](#技术架构)

---

## 重大更新 2026-04-24

### 日报SOP全面标准化（13个任务全部专属SOP）

**根因修复**：cron isolated session 不自动加载 wiki，导致 SOP 规则无法落地。

**修复方案**：每个 cron prompt 第一步强制读对应 SOP 文件。

新建专属 SOP 文件：
- `wiki/SOP/抖音指数日报.md` — 订阅页Tab2 + 关键词页Tab4，4板块格式
- `wiki/SOP/小红书日报.md` — 灵犀后台 + 关键词笔记搜索Tab6
- `wiki/SOP/竞品爆款拆解.md` — 四平台深度拆解，触发条件 + 落地建议
- `wiki/SOP/竞品内容动态.md` — 8大竞品追踪，3板块格式
- `wiki/SOP/每日复盘整合.md` — 任务执行/数据发现/问题/改进建议
- `wiki/SOP/案例库更新.md` — 仅写 wiki，不发群
- `wiki/SOP/Wiki健康检查.md` — karpathy-wiki LINT
- `wiki/SOP/代码库Wiki漂移检查.md` — karpathy-project-wiki LINT

**静默执行规范**：所有 announce 投群任务，禁止输出操作日志到群里，只发关键发现。

**行业热点采集升级 v5**：改用新浪旅游/搜狐旅游（无需登录），提取真实正文摘要 + 自动生成影响判断。

---

## 重大更新 2026-04-22

### 年度目标调增：132万→153万
- YTD 51.1万，完成度33.4%（时间进度37.5%，滞后4.1pp）
- 散客/渠道结构：散客占85%+，渠道为淡季补充

### 穿越德化街深度分析完成（数据里程碑）
基于《穿越德化街》数据分析-4.16v4(1).xlsx全部5个子表格：
- **扩建分界线：2025-01-01正式运营**，2024年10-12月扩建施工，数据不可比
- **2025年质变：** 入园133.8万(-15%)但转化率35.2%(+17.2pp)，观演47.1万(+65.8%)，演出收入4266万(+35.9%)
- **客单价：** 套票101.59元 / 德化街39.54元 / 加购52.80元
- **六大洞察：** 扩建悖论 / 平日>大假 / 国庆入园崩-41% / ⚠️2026Q1加购占比超50%预警 / 8月vs10月差异逻辑 / 受众画像
- **文档：** `wiki/电影小镇/演出节目/穿越德化街.md`

### 抖音指数日报数据Bug修复
- **问题：** 脚本读取昨日缓存（平台每天只更新一次）
- **修复：** 添加数据日期检测，非今日则`page.reload()`等待8秒再读取
- **脚本：** `scripts/douyin_index_v9.py`

### 系统健康检查SOP建立
- **每日检查（5分钟）：** cron状态 / 飞书卡片验证 / 专属浏览器5Tab
- **周日全面检查（30分钟）：** 全表cron / session堆积 / memory脏块 / gateway进程
- **故障决策树：** timeout→no route→message failed→python error四类分流
- **文档：** `wiki/SOP/系统健康检查SOP.md`

### 专属浏览器维护SOP建立
- 5个Tab位：Tab0百度 / Tab1抖音订阅 / Tab3抖音关键词 / Tab4小红书灵犀 / Tab5小红书探索
- 启动命令：`openclaw browser start`（或手动`--remote-debugging-port=18800`）
- 每次重启后需重新登录各平台（Cookie独立配置）
- **文档：** `wiki/SOP/专属浏览器维护SOP.md`

### Feishu Cron投递路由全面修复
- 16个cron任务`announce->last`静默失败 → 改为`delivery.mode:none`
- 3个任务保留显式Feishu配置（双重保障）

---

## 重大更新 2026-04-20

### 竞品深度分析SOP正式建立
四平台标准化采集流程，浏览器操作规范大幅更新：

| 平台 | 正确操作 | 关键突破 |
|------|---------|---------|
| 百度搜索 | `browser.open()` 新Tab直开URL | 绕过人机验证 ✅ |
| 抖音指数 | CDP已有直连Tab搜索 | 5/10停服维护 ⚠️ |
| 小红书灵犀 | `page.evaluate()` DOM注入文字 | React组件type无效问题解决 ✅ |
| 小红书搜索 | `browser.open()` 直开搜索结果页 | 绕过Explore视频锁死DOM ✅ |

**文档位置：** `wiki/SOP/竞品深度分析流程.md` · `wiki/技术配置/浏览器操作规范.md`

### 万岁山武侠城深度分析（今日完成）
首次四平台全量数据采集：
- 百度：12.7亿营收/2452万游客/日均2700场演出/100元三日票
- 抖音指数：搜索7.3万（同比-38%）
- 小红书灵犀：武侠兴趣榜9904排第4（+54位）
- 小红书搜索：爆款笔记TOP1获8077赞

### W17周案例库更新
- 大唐不夜城/老君山景区案例归档
- 文旅小镇运营模式专题建立

### 客流规律洞察报告
2023-2026年历史数据分析：
- 春节7天日均3.2万/散客占93-95%
- 2026年YTD完成度38.7%，超进度5.4个百分点
- 雨雪天气可导致客流下降50-80%

---

## Features

### 📊 Daily Automated Reports
| Report | Time | Content |
|--------|------|---------|
| Douyin Index Daily | 08:00 | 8 scenic areas ranked by search & synthesis index |
| Travel Hotspots | 10:00 | Nationwide travel industry trends |
| Competitor Case Studies | 12:00 | 爆款 Content analysis across scenic areas |
| Industry Trends | 14:00 | Tourism sector news & policies |
| Weekly Passenger Insights | Mon 09:00 | 散客/渠道 Structure + monthly progress |

### 🔍 Core Capabilities
- **Douyin Platform Monitoring** — Real-time index tracking for 8 competitor scenic areas
- **Xiaohongshu Analytics** — 灵犀后台 data (search volume, 笔记 insights, crowd profiling)
- **Passenger Flow Analysis** — 散客 vs 渠道 Structure, historical comparison, weather correlation
- **Competitor Deep Dive** — 竞品深度分析 SOP: 4 platforms × standard flow
- **Case Library** — Nationwide scenic area marketing case studies (updated weekly)
- **Browser Automation** — CDP-based multi-platform data collection (2026-04-20 stabilized)

### 🎯 Marketing Intelligence
- **Content Strategy** — UGC/KOL trends, POV/互动挑战 formats, 攻略爆款公式
- **Crowd Profiling** — Demographic insights from Douyin + Xiaohongshu
- **舆情 Monitoring** — Sentiment tracking and crisis alerts
- **Seasonal Patterns** — Spring Festival/Summer/National Day peak analysis
- **Competitive Pricing** — 竞品定价策略监控（e.g. 万岁山100元三日通票）

---

## Tech Stack

| Component | Technology |
|-----------|------------|
| AI Agent | OpenClaw + MiniMax-M2.7 |
| Knowledge Base | Obsidian Vault + LLMWiki |
| Browser Automation | CDP (Chrome DevTools Protocol) — stabilized 2026-04-20 |
| Data Sources | Douyin Creator Hub · Xiaohongshu 灵犀 · Feishu Bitable · Baidu |
| Scheduled Tasks | Cron (automated jobs) |
| Memory System | Multi-tier: daily logs → weekly dreaming → long-term MEMORY.md |

---

## Repository Structure

```
wiki/
├── 电影小镇/                        # 景区核心数据
│   ├── 基础档案.md                  # 年度目标/配置
│   ├── 历史数据/
│   │   ├── 规律洞察.md              # 散客/渠道/季节性规律 (2026-04-20更新)
│   │   ├── 2026年/数据.md
│   │   └── ...
│   └── 运营方法/
│       ├── 抖音运营方法.md
│       └── 小红书运营方法.md
├── 竞品分析/                        # 7大竞品数据追踪
│   ├── index.md
│   ├── 万岁山武侠城深度分析.md      # 四平台全量采集 (2026-04-20新建)
│   ├── 清明上河园深度分析.md
│   └── 竞品动态追踪/
├── 全国景区案例库/                    # 爆款案例（按周归档）
│   ├── 大唐不夜城案例-2026W17.md   # 2026-04-20新建
│   ├── 老君山景区案例-2026W17.md   # 2026-04-20新建
│   ├── 万岁山武侠城标杆.md
│   └── 文旅小镇运营模式专题.md      # 2026-04-20新建
├── SOP/                             # 标准化操作流程
│   ├── 竞品深度分析流程.md         # 四平台SOP (2026-04-20新建)
│   ├── 飞书卡片视觉规范.md
│   ├── 周度客流营收洞察报告.md
│   └── 文旅活动热点追踪日报.md
└── 技术配置/                         # Browser/CDP/Skills配置
    ├── 浏览器操作规范.md            # 大幅更新 (2026-04-20)
    └── 搜索关键词规范.md

scripts/                             # 自动化脚本
├── douyin_index_v9.py               # 抖音指数采集
├── xiaohongshu_crawl.py             # 小红书数据采集
└── send_feishu_card.py              # 飞书卡片发送

memory/
└── YYYY-MM-DD.md                    # 每日会话日志
```

---

## 竞品深度分析 · 标准流程

### 四平台数据采集（详见 wiki/SOP/竞品深度分析流程.md）

```
1. 百度   → browser.open() 新Tab直开  https://www.baidu.com/s?wd={关键词}
2. 抖音   → CDP已有Tab搜索关键词
3. 灵犀   → page.evaluate() DOM注入文字 → 等2秒 → evaluate找选项.click()
4. 小红书 → browser.open() 新Tab直开  https://www.xiaohongshu.com/search_result?keyword={关键词}
```

### 报告标准格式

每个竞品深度分析必须包含7大模块：
1. 核心数据快照表（四平台汇总）
2. 百度数据（运营/财务/媒体报道）
3. 抖音指数分析（搜索+综合指数）
4. 小红书灵犀数据（搜索量+上下游词）
5. 小红书内容分析（爆款TOP10+热搜问题）
6. 内容营销规律总结（爆款公式/用户决策路径）
7. 对电影小镇的深度借鉴

---

## Data Architecture

```
┌─────────────────────────────────────────┐
│  Data Sources (Daily Auto-Sync)         │
│  • Douyin Creator Hub → 抖音指数        │
│  • Xiaohongshu 灵犀 → 搜索/内容/人群    │
│  • Baidu Search → 运营/媒体报道          │
│  • Feishu Bitable → 客流数据            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│  Obsidian Wiki Knowledge Base (42+ notes)│
│  • 竞品深度分析 SOP (2026-04-20)        │
│  • Browser操作规范 (updated 2026-04-20)│
│  • 客流规律洞察 (updated 2026-04-20)    │
│  • W17案例库 (大唐不夜城/老君山)         │
└────────────────┬────────────────────────┘
                 │ AI Agent Processing
                 ▼
┌─────────────────────────────────────────┐
│  Feishu Group Delivery                 │
│  • 08:00 抖音指数日报                  │
│  • 10:00 文旅热点追踪                  │
│  • Mon 09:00 周度客流洞察             │
│  • 15:00 竞品深度分析报告              │
└─────────────────────────────────────────┘
```

---

## 中文说明

本仓库是**建业电影小镇**景区营销中心的AI运营助手，基于OpenClaw框架构建。

### 2026-04-20重大进展
- **浏览器操作规范化** — 4平台采集流程全部跑通，不再绕弯子
- **竞品深度分析SOP建立** — 万岁山武侠城为标杆，流程固化为标准操作
- **案例库W17更新** — 大唐不夜城/老君山/文旅小镇模式

### 核心功能
- **抖音指数监测** — 每日08:00追踪8大竞品景区排名
- **小红书运营** — 灵犀后台替代爬虫，获取搜索/内容/人群数据
- **竞品深度分析** — 四平台标准化采集（百度/抖音/灵犀/小红书）
- **客流营收分析** — 散客/渠道结构拆分，历年同期对比
- **案例库积累** — 全国景区爆款营销案例学习（按周归档）

### 8大竞品关键词
建业电影小镇 · 万岁山武侠城 · 清明上河园 · 只有河南戏剧幻城 · 郑州方特欢乐世界 · 郑州海昌海洋公园 · 郑州银基动物王国 · 只有红楼梦戏剧幻城

---

## License

MIT License

---

> Built with [OpenClaw](https://github.com/openclaw/openclaw) · Powered by [MiniMax](https://minimax.io/)
