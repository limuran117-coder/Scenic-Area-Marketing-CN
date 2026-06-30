# 电影小镇 Ontology 架构设计研究

> 对标 Palantir Foundry/AIP Ontology Architecture
> 研究启动：2026-05-29 | 最近更新: 2026-06-29 (Week 2 Actions & Functions 标准化完成)
> 状态：Phase 1 schema 完整 + Phase 1.5 Actions/Functions 标准化完成；Phase 2 实施中
> 最新版本：ontology.json v1.3.0（11 Functions / 7 Actions / 10 Validation Rules / 20 Design Decisions）

---

## 一、Palantir Ontology 核心概念

Palantir Ontology 是一个"业务感知"语义层，位于**原始数据**和**AI Agent**之间。

```
┌──────────────────────────────────────────┐
│          AI Agents / LLM                  │ ← 自然语言推理、决策
├──────────────────────────────────────────┤
│            Ontology Layer                 │ ← 业务实体、关系、动作、函数
│  Object Types | Links | Actions | Funcs   │
├──────────────────────────────────────────┤
│     Raw Data (databases, APIs, logs)      │ ← 抖音指数、小红书、客流 CSV
└──────────────────────────────────────────┘
```

### 6 大组件

| 组件 | 描述 | 对标我们系统的什么 |
|------|------|-------------------|
| **Object Types** (对象类型) | 名词：景区、游客、活动、内容 | wiki/电影小镇/ 中的各知识板块 |
| **Properties** (属性) | 每个对象的属性（字符串/数字/枚举） | 抖音指数、客流数字、标签 |
| **Link Types** (关系) | 有向关系（many-to-many/one-to-many） | "竞品""客源地""投放渠道" |
| **Action Types** (动作) | 业务动作（审批、创建告警、调价） | 各 cron 任务的判断输出 |
| **Functions** (函数) | 可复用逻辑（计算利用率、预测峰值） | countdown.js, period.js 中的算法 |
| **Interfaces** (接口) | 多态抽象（允许不同对象类型统一处理） | 未来扩展 |

### Palantir 的关键设计原则

1. **Digital Twin** — 本体是组织现实的数字孪生，不仅是数据模型
2. **Semantic Consistency** — "游客"这个概念在所有地方含义一致
3. **AI-Readiness** — LLM 可以直接用自然语言查询和推理本体
4. **Write Governance via Actions** — 所有写操作必须经过 Action Types（防乱写）
5. **Single Source of Truth** — 本体是黄金记录，所有下游应用从同一本体读写

---

## 二、电影小镇领域 Ontology 设计

### 2.1 Object Types (核心实体)

```
ScenicSpot (景区)
  ├── 电影小镇
  ├── 只有河南
  ├── 银基动物王国
  ├── 清明上河园
  ├── 万岁山武侠城
  ├── 方特欢乐世界
  └── 其他全国景区

TouristSegment (游客群体)
  ├── 亲子家庭
  ├── Z世代年轻客群
  ├── 大学生
  ├── 周边自驾游
  └── 省外游客

MarketingCampaign (营销活动)
  ├── 节日活动
  ├── 促销优惠
  ├── 达人合作
  ├── 社媒种草
  └── 品牌联名

ContentAsset (内容资产)
  ├── 抖音视频
  ├── 小红书笔记
  ├── 微博内容
  ├── KOL/KOC 合作
  └── UGC 内容

Event (事件/动态)
  ├── 竞品新节目
  ├── 舆情事件
  ├── 政策变化
  ├── 行业趋势
  └── 节假日

MetricSnapshot (数据快照)
  ├── 抖音指数日数据
  ├── 客流周数据
  ├── 营收日数据
  └── 内容互动数据

DecisionRule (决策规则)
  ├── 内容策略规则
  ├── 投放策略规则
  ├── 预警规则
  └── 竞品应对规则

AgentTask (Agent任务)
  ├── 每日定时采集任务
  ├── 分析推理任务
  ├── 报告生成任务
  └── 知识归档任务
```

### 2.2 Link Types (关系)

```
ScenicSpot -- competes_with --> ScenicSpot          (竞品关系)
ScenicSpot -- located_in --> Region                  (地理归属)
Campaign -- targets --> TouristSegment               (目标客群)
Campaign -- uses --> ContentAsset                    (使用的素材)
ContentAsset -- mentions --> ScenicSpot              (内容提及景区)
ContentAsset -- created_by --> Creator               (创作者)
Event -- affects --> ScenicSpot                      (事件影响景区)
MetricSnapshot -- belongs_to --> ScenicSpot          (度量归属决策)
MetricSnapshot -- triggers --> DecisionRule          (数据触发规则)
DecisionRule -- produces --> AgentTask               (规则生成任务)
AgentTask -- writes_to --> KnowledgeBase             (任务输出到知识库)
```

### 2.3 Functions (核心函数) — v1.3.0 11 个

> **v1.3.0 升级：** 引入 4 类型分类（Pure / SideEffect / FunctionBacked / Aggregator）。Week 2 新增 4 个 Function（⭐）。

| 函数 | 类型 | 输入 | 输出 | 当前存在 |
|------|------|------|------|---------|
| `calculateSearchTrend()` | Pure | 景区ID, 日期范围 | 搜索指数趋势 | ✅ douyin_index.py |
| `predictVisitorFlow()` | Pure | 历史客流, 节假日日历 | 峰值预测 | ✅ period.js (算法模式) |
| `assessContentVacuum()` | Pure | 搜索指数, 综合指数 | 内容缺口判定 | ✅ MEMORY.md 铁律 |
| `sentimentAnalysis()` | Pure | 舆情文本 | 正面/负面/情感分 | ✅ 舆情监控 |
| `competitiveAlert()` | Pure | 竞品动态 | 预警等级 | ✅ 竞品动态 |
| `enrichContentAsset()` ⭐ | Pure | ContentAsset + 上下文 | 富化语义 | ⚠️ Week 4 实施 |
| `calculateBaselineValue()` ⭐ | FunctionBacked | 景区ID, 指标类型, 14天 | 基线值 | ⚠️ Week 3 实施 |
| `detectAnomaly()` ⭐ | FunctionBacked | MetricSnapshot, 阈值 | 异常检测 | ⚠️ Week 3 实施 |
| `attributionScore()` | **SideEffect** | 营销动作, 客流变化 | 归因置信度 + 写库 | ✅ 营销归因 |
| `generateDailyInsight()` | Aggregator | 今日所有 Object | 洞察卡片 | ✅ 每日复盘 |
| `aggregateWeeklyMetrics()` ⭐ | Aggregator | 景区ID, ISO week | 周度聚合 | ⚠️ Week 5 实施 |

**关键约束（D-016）：** SideEffect Function（attributionScore）必须经 Action 调用，不可被 Agent 直接 invoke。

### 2.4 Action Types (业务动作) — v1.3.0 7 个

> **v1.3.0 升级：** 引入 5 层治理（Submission/Validation/Notification/Audit/Rollback）+ 3 档 category（lowStakes/mediumStakes/highStakes）+ Function-backed Action 模式。Week 2 新增 2 个 Action（⭐）。

| 动作 | Category | Function-backed | 触发条件 | 效果 | 当前 |
|------|----------|----------------|---------|------|------|
| `SendFeishuCard` | lowStakes | ✅ | 日报/分析完成 | 发送卡片到群 | ✅ send_feishu_card.py |
| `UpdateWiki` | lowStakes | ✅ | 新洞察产生 | 写入行业知识库 | ✅ wiki/ |
| `ScheduleOntologyResearch` | lowStakes | ✅ | 每周 cron 触发 | 写 Wiki 设计文档 | ✅ 已运行 |
| `CreateAlert` | mediumStakes | ❌ | 舆情/竞品重大变化 | 飞书私信告警 | ⚠️ 部分自动化 |
| `AdjustStrategy` ⭐ | mediumStakes | ✅ | 数据驱动 | 推送策略建议 | ❌ Week 4 实施 |
| `UpdateDecisionRule` | **highStakes** | ❌ | 规则验证通过/失败 | 更新规则状态（需批准）| ❌ Week 4 实施 |
| `OverrideRule` ⭐ | **highStakes** | ❌ | 紧急情况暂停规则 | 覆盖规则（需批准，到期恢复）| ❌ Week 4 实施 |

**关键治理（D-017~D-019）：**
- **lowStakes** (3 个)：no approval / async notify / idempotent
- **mediumStakes** (2 个)：no approval / sync notify / rollback required
- **highStakes** (2 个)：requires approval / audit critical / manual rollback

---

## 三、当前系统与 Ontology 架构的差距分析

### 当前架构（碎片化）

```
data sources → 独立脚本 → 飞书卡片 / wiki 文件
                    ↕ (无统一数据模型)
               cron 调度器（分散管理）
                    ↕ (无实体关联)
               memory + wiki（知识库）
```

### 目标架构（Ontology-driven）

```
data sources → Ingestion Pipeline → Ontology Layer → AI Agents
                                        ↕
                                  Knowledge Graph
                                        ↕
                                  Decision Engine
                                        ↕
                                  Action Dispatcher
```

### 差距清单

| 维度 | 当前 | 目标 | 差距 |
|------|------|------|------|
| 数据模型 | 无统一模型，数据散落在 JSON/CSV/Storage | Object Types 统一建模 | 🔴 高 |
| 关系管理 | 隐式（在代码中 hardcode "竞品"关系） | Link Types 显式声明 | 🔴 高 |
| 动作治理 | 每个 cron 直接写文件/发卡片 | Action Types 统一管控 | 🟡 中 |
| 函数复用 | 函数分散在多个 JS 工具库中 | Ontology Functions 中心化 | 🟡 中 |
| 知识图谱 | wiki 是平面 markdown 文件 | 图结构知识库 | 🔴 高 |
| AI-Ready | AI 通过 prompt 感知业务上下文 | AI 直接查询 ontology | 🟡 中 |
| 版本控制 | 数据无版本 | Time Travel & Audit | 🟡 中 |
| **Action 治理** | **每个 cron 直接写文件/发卡片** | **Action Types 5 层治理 (Submission/Validation/Notification/Audit/Rollback)** | **🟡 中** | 🆕 Week 2 升级 |
| **Function 类型化** | **无分类** | **4 类型 (Pure/SideEffect/FunctionBacked/Aggregator)** | **🟡 中** | 🆕 Week 2 升级 |

---

## 四、落地路线图

### Phase 1：核心 Ontology 搭建（2周）
- [ ] 用 JSON 定义全部 Object Types（景区、活动、游客等）
- [ ] 定义 Link Types
- [ ] 将现有数据源映射到对象
- [ ] 创建 ontology.json 作为单一事实源

### Phase 2：数据接入管道（2周）
- [ ] 抖音指数脚本输出改为 Ontology Object 格式
- [ ] 小红书采集脚本输出改为 Ontology Object
- [ ] 客流 CSV 解析为 Ontology Object
- [ ] Agent cron 任务输出写入 Ontology

### Phase 3：Actions & Functions 标准化（1周，✅ Week 2 完成 schema）
- [x] Functions 4 类型分类（D-016，✅ schema 完成）
- [x] Action 5 层治理（D-017，✅ schema 完成）
- [x] Function-backed Action 模式（D-018，✅ schema 完成）
- [x] Action Category 3 档（D-019，✅ schema 完成）
- [ ] 全部 SendFeishuCard 调用改为 Action Type wrapper（Week 3 实施）
- [ ] 全部决策逻辑抽为 Functions（部分已有，Week 3+ 补全）
- [ ] scripts/actions/ 目录创建（Week 3）
- [ ] scripts/ontology/validate.py V-001~V-010 实施（Week 3）

### Phase 4：AI Agent 接入 Ontology（2周）
- [ ] Agent 通过 Ontology SDK 读取业务对象
- [ ] Agent 动作通过 Actions 执行
- [ ] 自然语言查询 Ontology 链路打通

### Phase 5：持续迭代（∞）
- [ ] 每季度审计 Ontology 漂移
- [ ] 新增 Object Types 与 Links
- [ ] 优化 Functions 准确性

---

## 五、对标 Palantir 的关键设计决策

### 5.1 我们不做 Palantir 的哪些？

| Palantir 功能 | 我们 | 原因 |
|-------------|------|------|
| 多租户/复杂 RBAC | ❌ 不需要 | 单用户系统 |
| 大数据湖 (PB级) | ❌ 不需要 | 数据量小 |
| 实时流处理 | ❌ 不需要 | 日级批量 |
| Workshop/Quiver UI | ❌ 不需要 | 飞书卡片够用 |

### 5.2 我们要做的核心

1. **Ontology as JSON Schema** — 不用 OWL/RDF（太重），用轻量 JSON 定义
2. **Object Types 对应 wiki 目录** — 每个 Object Type 对应一个 wiki 文件夹
3. **Links 对应 wiki 引用** — 跨页面链接显式声明
4. **Actions 对应 cron 任务** — 每个 cron 的 payload 改写为 Action 格式
5. **Functions 对应 utils/*.js** — 核心算法统一注册
6. **Storage: SQLite** — 核心存储用 SQLite（见 基础设施评估.md D-005）
7. **Git Snapshots: JSON** — adapter 双写 JSON 文件进 Git 历史（见 D-006）

---

## 六、下一步

1. 审阅本文档，确认 Object Types 和 Link Types 完整
2. 确定 Phase 1 启动的具体 Object Type（建议从 ScenicSpot + MetricSnapshot 开始）
3. 设计 ontology.json Schema
4. 启动定时研究任务，每周深化

---

## 🆕 2026-06-30 H1 收官节点

### **H1 收官数据写入 Ontology 计划**

| Object Type | 数据 | 状态 |
|------------|------|------|
| ScenicSpot | 建业电影小镇 | ✅ 已有 |
| MetricSnapshot | H1=716,409 / 6月日均=1,428 / 端午=11,513 | 🔶 待写入 |
| Region | 河南（46.16% TGI=634）| 🔶 待写入 |
| ContentAsset | 5/15 启幕「回到小时候」/ 6/13 暑期季 | 🔶 待写入 |
| Action | P0 三项（毕业生免票/夜游 2.0/抖音日更）| 🔶 待写入 |
| Decision | 应急 MVP 7/2 18:00 触发 | 🔶 待写入 |

### **Week 3 实施路径**

- Day 1（7/1）：validate.py V-001~V-010 全量
- Day 2（7/2）：calculateBaselineValue + detectAnomaly 写入
- Day 3（7/3）：scripts/actions/ 目录创建
- Day 4（7/4）：P0-2 夜游 2.0 启动 → Action 治理
- Day 5（7/5）：P0-1 毕业生免票数据回填

### 关联文档

- 实现路线图：`wiki/技术配置/Ontology架构设计/实现路线图.md`
- ontology.json v1.3.0
- Week 2 Actions & Functions：`wiki/技术配置/Ontology架构设计/Week2_Actions_Functions.md`
- H1 一页纸：`memory/2026-06-30-h1-recap.md`
