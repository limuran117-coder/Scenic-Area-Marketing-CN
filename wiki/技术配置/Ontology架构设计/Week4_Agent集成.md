# Week 4 · AI Agent × Ontology 集成方案（含 LLM Query Translator）

> 日期：2026-07-27 (周一) | 周期：**Week 4**（对标实现路线图.md §二 Phase 4）
> 状态：**🔵 设计阶段**（文档完成；Week 5 进入实施）
> 上接：Week 3 (2026-07-06) 数据接入管道设计（PipelineRun / 5-Stage / adapterGovernance 完成）
> 本周主题：AI Agent 如何读写 Ontology Layer（Query Handler + LLM Query Translator + Agent Context Injection）
> 当前时间：2026-07-27 20:00 (Asia/Shanghai)

---

## 一、本周目标

1. **设计** AI Agent 与 Ontology Layer 的集成架构
2. **设计** LLM Query Translator（自然语言 → Ontology Query / Function Call）
3. **设计** Agent Context Injection（Ontology → Agent Session 上下文注入）
4. **设计** Agent Write Path（Ontology Actions → Agent 执行链路）
5. **更新** ontology.json v1.5.0（新增 agentIntegration section + QueryHandler 定义）
6. **更新** weekCycle（Week 3 → Week 4）

---

## 二、现状盘点（Week 4 起点）

### 2.1 Schema 完整性（✅ 完整）

| 组件 | 状态 | 数据 |
|------|------|------|
| Object Types | ✅ 12 个 | 分布在 7 类（ScenicSpot/MetricSnapshot/ContentAsset/Event/MarketingCampaign/DecisionRule/AgentTask/TouristSegment/Region/KnowledgeBase/Creator/OntologyAdapter） |
| Link Types | ✅ 33 个 | competes_with / belongs_to / mentions 等 |
| Functions | ✅ 16 个 | Pure(6) / SideEffect(1) / FunctionBacked(2) / Aggregator(2) |
| Actions | ✅ 7 个 | lowStakes(3) / mediumStakes(2) / highStakes(2) |
| Validation Rules | ✅ 15 条 | V-001~V-015 |
| Design Decisions | ✅ 25 条 | D-001~D-025 |

### 2.2 存储层（⚠️ 部分实施）

| 组件 | 状态 | 位置 |
|------|------|------|
| SQLite Store | ⚠️ Week 6 原型跑通但 adapter 未全量接入 | `.profile/ontology/ontology_store.db` |
| JSON Git 快照 | ✅ 14 个历史文件 | `wiki/技术配置/Ontology架构设计/data/` |
| pipeline_runs 表 | ❌ 未创建（db migration 002 未实施）| Week 4 计划 |
| Function 计算列 | ❌ baselineValue/dailyVolatility/isAnomaly 未落地 | Week 4 计划 |

### 2.3 缺失的 Phase 4 组件（❌ 本周设计）

```
❌ AgentQueryHandler  — 自然语言 → Ontology 查询的接口层
❌ LLM Query Translator — LLM 驱动的大白话→结构化查询翻译器
❌ Agent Context Injection — Ontology → Agent Session 上下文注入
❌ Ontology → Agent write path — Agent 决策 → Action → Ontology 写入
❌ SOUL.md / AGENTS.md 集成点 — 尚未显式引入 ontology 对象
```

---

## 三、核心架构：Agent × Ontology 交互模型

### 3.1 交互全视图

```
┌──────────────────────────────────────────────────────────────────┐
│                        AI Agent (李涯 / OpenClaw)                  │
│  SOUL.md: "你是景区营销中心总经理"                                   │
│  AGENTS.md: "每周做 Ontology 研究"                                 │
│  MEMORY.md: 长期记忆                                               │
│                                                                   │
│  收到用户消息 → 自然语言理解 → ???                                  │
└─────────────────────┬────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │   AgentQueryHandler          │  ← Week 4 设计核心
        │   (自然语言查询接口)           │
        └─────────────────────────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
   ┌──────────┐ ┌──────────┐ ┌──────────────┐
   │ LLM Query │ │ Function │ │ Action       │
   │Translator │ │  Executor│ │ Dispatcher   │
   └────┬─────┘ └────┬─────┘ └──────┬───────┘
        │            │               │
        ▼            ▼               ▼
   ┌──────────────────────────────────────┐
   │         Ontology Layer (SQLite)        │
   │  Object Store │ Link Store │ Functions │
   └──────────────────────────────────────┘
```

### 3.2 两条核心路径

**路径 A：Query（读）— Agent 想了解情况时**
```
用户/Agent问："本周哪个竞品最火？" 
→ AgentQueryHandler.ask(question)
→ LLM Query Translator（3阶段）
  Stage 1: 意图分类（QueryIntentClassification）
  Stage 2: 实体提取（Entity Extraction）
  Stage 3: 查询生成（Query Generation → SQL / Function Call）
→ Ontology Layer 执行
→ 结果返回 Agent → 自然语言回答
```

**路径 B：Write（写）— Agent 要改变世界时**
```
Agent 决定：发送抖音日报卡片
→ Action Dispatcher（actionGovernance 5层）
  Submission → Validation → Notification → Audit → Rollback
→ SendFeishuCard Action 执行
→ Ontology 记录 Action Log
```

---

## 四、LLM Query Translator 详细设计

### 4.1 为什么需要 Query Translator？

**现状问题：**
- Agent 想查"本周电影小镇 vs 竞品搜索指数对比"→ 需要知道查哪个表/字段
- 不同 cron 任务分散调用 `ontology_query.py` 的具体函数
- 没有统一入口，Agent 需要手动拼 SQL 或记方法名

**Query Translator 价值：**
- Agent 用自然语言表达需求，LLM 翻译为结构化查询
- 不需要 Agent 记住具体的 Function 名/SQL 语法
- 底层可以替换实现（SQLite → PostgreSQL → Neo4j），上层不变

### 4.2 Query Intent Classification（意图分类）

> **Stage 1：判断用户想做什么类型的查询**

```python
class QueryIntent(Enum):
    # 读路径（Query）
    METRIC_RANKING      # "竞品排名" / "本周最热景区"
    METRIC_TREND        # "电影小镇搜索指数走势" / "银基最近30天趋势"
    CONTENT_ANALYSIS    # "本周哪些视频爆了" / "小红书爆款分析"
    COMPETITOR_BRIEF    # "只有河南最近有什么动态"
    ALERT_REVIEW        # "最近有哪些异常"
    
    # 写路径（Action）
    SEND_CARD           # "发送日报"
    UPDATE_WIKI         # "把这个记到 wiki"
    CREATE_ALERT        # "设置一个告警"
    
    # 混合路径
    INSIGHT_SUMMARY     # "给我今日洞察" → aggregateDailyMetrics → 自然语言
```

**Prompt 模板（用于 LLM 分类）：**
```
你是一个景区营销分析助手。用户输入判断属于哪种意图：

选项：
- METRIC_RANKING：景区指标排名对比
- METRIC_TREND：某景区指标随时间变化
- CONTENT_ANALYSIS：内容资产表现分析
- COMPETITOR_BRIEF：竞品动态摘要
- ALERT_REVIEW：异常/告警查看
- SEND_CARD：发送飞书卡片
- UPDATE_WIKI：更新 wiki 知识库
- CREATE_ALERT：创建告警规则
- INSIGHT_SUMMARY：生成综合洞察报告
- UNKNOWN：无法归类

用户输入：{user_input}
```

### 4.3 Entity Extraction（实体提取）

> **Stage 2：从自然语言中提取关键实体**

```python
class ExtractedQuery:
    intent: QueryIntent
    scenic_spot_ids: list[str]          # ["ss:movie_town", "ss:only_henan"]
    metric_types: list[str]             # ["search_index", "content_index", "visitor_count"]
    date_range: tuple[str, str]         # ("2026-07-21", "2026-07-27")
    comparators: list[str]              # ["vs", "对比", "哪个更高"]
    filters: dict                       # {"isAnomaly": true, "tier": "national"}
```

**提取示例：**
```
用户输入："本周电影小镇和只有河南的抖音搜索指数对比"
→ intent: METRIC_RANKING
→ scenic_spot_ids: ["ss:movie_town", "ss:only_henan"]  # 来自 SCENIC_SPOT_MAP 反查
→ metric_types: ["search_index"]
→ date_range: ("2026-07-21", "2026-07-27")           # 本周 = 最近7天
→ comparators: ["对比"]

用户输入："最近30天哪些景区有异常？"
→ intent: ALERT_REVIEW
→ scenic_spot_ids: []                                    # 空 = 全部景区
→ metric_types: []
→ date_range: ("2026-06-27", "2026-07-27")             # 最近30天
→ filters: {"isAnomaly": true}
```

### 4.4 Query Generation（查询生成）

> **Stage 3：将结构化查询翻译为执行指令**

```python
def translate(extracted: ExtractedQuery) -> QueryInstruction:
    """生成可执行指令（SQL 或 Function Call）"""
    
    if extracted.intent == METRIC_RANKING:
        return FunctionCall(
            function="aggregateWeeklyMetrics",  # F-011，Aggregator 类型
            params={
                "scenic_spot_ids": extracted.scenic_spot_ids,
                "metric_types": extracted.metric_types,
                "date_range": extracted.date_range,
                "group_by": "scenic_spot",
                "order_by": extracted.metric_types[0] if extracted.metric_types else "composite_index",
                "order": "desc"
            }
        )
    
    elif extracted.intent == METRIC_TREND:
        return FunctionCall(
            function="calculateSearchTrend",  # F-001，Pure 类型
            params={
                "scenic_spot_id": extracted.scenic_spot_ids[0],
                "metric_type": extracted.metric_types[0],
                "start_date": extracted.date_range[0],
                "end_date": extracted.date_range[1]
            }
        )
    
    elif extracted.intent == ALERT_REVIEW:
        return SQLQuery(
            sql="""SELECT * FROM metric_snapshots 
                    WHERE is_anomaly = 1 
                    AND date BETWEEN ? AND ?
                    ORDER BY date DESC""",
            params=[extracted.date_range[0], extracted.date_range[1]]
        )
```

### 4.5 Query Translator 实现决策

**D-026：Query Translator 采用 3-Stage LLM Chain（而非单次 prompt）**
- Stage 1（意图分类）：轻量 prompt，fast model 可完成
- Stage 2（实体提取）：需要 ontology schema context，必须用主力 model
- Stage 3（查询生成）：确定性规则 + 少量 LLM 判断
- **理由**：避免单次 prompt 过长导致 schema 信息被截断；分类/提取/生成可独立测试

**D-027：Query Translator 输出给 Agent 的格式**
- 优先返回 Function Call（可解释、可追溯）
- 次选返回 SQL 结果（仅在 Function 无法覆盖时）
- **理由**：Function Call 有显式的 Function 名 + 参数，Agent 更容易理解"查了什么"

**D-028：Query Translator 的 fallback 策略**
- LLM 无法分类 → 返回 UNKNOWN → Agent 追问用户
- 实体提取失败（spot_id 无法映射）→ 用 fuzzy match → 最接近的 1 个景区
- 查询执行失败 → 返回错误 + 建议修正方案
- **理由**：fail gracefully，不阻塞 Agent 对话

---

## 五、AgentContextInjection：Ontology → Agent 上下文注入

### 5.1 注入时机与方式

| 时机 | 内容 | 注入量 | 方式 |
|------|------|--------|------|
| **Session 启动** | Object Types schema（简化版）| ~2KB | 系统 prompt 拼接 |
| **对话过程中** | 当前查询相关的 MetricSnapshot | ~500B | Function 返回结果内联 |
| **决策前** | 相关 DecisionRule + 历史 Action | ~1KB | Agent 主动 request |
| **报告生成** | 全部 MetricSnapshot（本周）| ~5KB | 批量查询 |

### 5.2 Session 启动时的 Schema 注入

**注入位置：** `SOUL.md` 或 `AGENTS.md` 末尾追加

```markdown
## 当前 Ontology 上下文（自动注入，勿手动修改）

### Object Types
- ScenicSpot（景区）: ss:<name>。属性：name, category, tier, province, city
- MetricSnapshot（日级数据）: ms:<source>:<spot>:<date>:<type>。属性：value, dailyChange, baselineValue, isAnomaly
- ContentAsset（内容）: ca:<source>:<id>。属性：platform, engagement, postedAt
- Event（事件）: ev:<type>:<date>:<seq>
- DecisionRule（规则）: dr:<id>。属性：status, priority
- MarketingCampaign（活动）: mc:<slug>

### Link Types
- competes_with：景区竞品关系
- belongs_to：数据归属景区
- mentions：内容提及景区

### Functions（可用自然语言调用）
- calculateSearchTrend(scenicSpotId, startDate, endDate) → 趋势数据
- detectAnomaly(metricSnapshotId) → 异常判定
- aggregateWeeklyMetrics(scenicSpotIds, metricTypes, week) → 排名数据
- assessContentVacuum(searchIndex, compositeIndex) → 内容缺口判定
```

**注入逻辑（Session Startup Hook）：**
```python
def inject_ontology_context(agent_session):
    schema_summary = load_ontology_schema_summary()  # 约2KB精简版
    agent_session.system_prompt += "\n\n" + schema_summary
```

### 5.3 Query 时的动态注入

**当 Agent 查询时，QueryHandler 返回结构化结果，Agent 自动获得上下文：**

```python
# 示例：Agent 问"本周竞品排名"
result = query_handler.ask("本周电影小镇和主要竞品的抖音指数排名")

# result 返回给 Agent 的格式（自然语言 + 结构化）
{
    "answer": "本周（7/21-7/27）抖音搜索指数排名：1.只有河南 8,234（↑12%）；2.银基动物王国 7,891（↑5%）；3.电影小镇 6,234（↓2%）",
    "structured": {
        "rankings": [
            {"scenic_spot": "ss:only_henan", "name": "只有河南", "search_index": 8234, "change": "+12%"},
            {"scenic_spot": "ss:yanji_animal", "name": "银基动物王国", "search_index": 7891, "change": "+5%"},
            {"scenic_spot": "ss:movie_town", "name": "电影小镇", "search_index": 6234, "change": "-2%"}
        ],
        "query_metadata": {
            "function_used": "aggregateWeeklyMetrics",
            "date_range": ("2026-07-21", "2026-07-27"),
            "confidence": 0.95
        }
    }
}
```

---

## 六、Agent Write Path：Ontology Actions → Agent 执行链路

### 6.1 现状问题

```
Agent（李涯）想："发送今日日报卡片"
→ 目前：直接调用 send_feishu_card.py（绕过 Ontology Action 治理）
→ 问题：无 audit trail、无 approval 记录、无可观测性
```

### 6.2 目标：Action 治理接入 Agent

```
Agent 决定：发送日报
→ Action Dispatcher
  → Submission：验证请求格式
  → Validation：检查 SendFeishuCard 约束（lowStakes: no approval）
  → Notification：发送飞书卡片（functionBacked: True）
  → Audit：写入 action_log（action_type, triggered_by, status, duration）
  → 完成，返回结果给 Agent
→ Agent 继续下一步
```

### 6.3 Action 分类的 Agent 感知

```python
class ActionClassification:
    LOW_STAKES = ["SendFeishuCard", "UpdateWiki", "ScheduleOntologyResearch"]
    MEDIUM_STAKES = ["CreateAlert", "AdjustStrategy"]
    HIGH_STAKES = ["UpdateDecisionRule", "OverrideRule"]

# Agent 的决策提示（当 Agent 说"我要XXX"时）
AGENT_ACTION_GUIDANCE = """
你触发了以下 Action，请注意：
- lowStakes（{LOW_STAKES}）：直接执行，不需要批准
- mediumStakes（{MEDIUM_STAKES}）：执行后通知站长
- highStakes（{HIGH_STAKES}）：执行前必须获得站长明确批准
"""
```

### 6.4 设计决策

**D-029：Agent 的 Action 执行通过 Action Dispatcher（不允许绕过）**
- 所有 Agent 触发的写操作必须走 actionGovernance 5层
- Action Dispatcher 是唯一出口，不允许直接调用 `send_feishu_card.py`
- **理由**：Action 是 Ontology 写操作的唯一治理点；绕过 = 失去 audit trail
- **过渡方案**：短期内 `send_feishu_card.py` 同时保留（向后兼容），但所有新调用走 Dispatcher

**D-030：Query Handler 优先返回 Function Call 而非原始 SQL**
- Function Call = 可解释、可追溯的语义单元
- SQL = 底层实现细节，不应暴露给 Agent prompt
- **理由**：Agent 看到 `aggregateWeeklyMetrics(...)` 远比看到 `SELECT ... FROM metric_snapshots WHERE ...` 更容易理解

**D-031：Session 启动时注入 Ontology Schema 简化版（约2KB）**
- 不注入完整 100KB ontology.json
- 只注入 Object Type 名称、ID 格式、核心属性、可用 Function 列表
- **理由**：Token 限制 + Schema 细节 Agent 用到时再查

---

## 七、Week 4 Schema 新增：agentIntegration Section

### 7.1 新增 Section（v1.5.0）

```json
{
  "agentIntegration": {
    "version": "1.0",
    "addedAt": "2026-07-27",
    "addedBy": "Week4_Agent集成.md",
    "description": "AI Agent 与 Ontology Layer 的集成方案（Query Handler + LLM Query Translator + Agent Context Injection）",
    
    "queryHandler": {
      "description": "自然语言查询的统一入口",
      "className": "AgentQueryHandler",
      "location": "scripts/ontology/query_handler.py",
      "methods": {
        "ask(question: str) -> QueryResult": "主查询方法，3-stage LLM translation",
        "get_context_for(ontology_object_id: str) -> dict": "获取特定对象的完整上下文",
        "list_recent_alerts(days: int = 7) -> list[Alert]": "快速查询近期异常"
      }
    },
    
    "llmQueryTranslator": {
      "description": "3-Stage LLM Chain：将自然语言翻译为 Ontology 查询",
      "stage1": {
        "name": "QueryIntentClassification",
        "model": "fast（mini/maxflash）",
        "prompt_template": "见 §4.2",
        "output": "QueryIntent enum"
      },
      "stage2": {
        "name": "EntityExtraction",
        "model": "主力 model",
        "prompt_includes": ["ontology_schema_summary", "scenic_spot_map", "metric_type_list"],
        "output": "ExtractedQuery"
      },
      "stage3": {
        "name": "QueryGeneration",
        "model": "确定性规则 + 轻量 LLM",
        "output": "FunctionCall | SQLQuery"
      }
    },
    
    "contextInjection": {
      "session_startup": {
        "description": "Session 启动时注入简化 Schema",
        "location": "SOUL.md / AGENTS.md 末尾追加",
        "size_limit": "2KB",
        "content_type": "简化 Object Types + Link Types + Function 列表"
      },
      "query_time": {
        "description": "查询结果内联返回（structured + 自然语言 answer）",
        "structured_format": "FunctionCall 返回值 + query_metadata"
      },
      "decision_time": {
        "description": "Agent 决策前主动拉取相关 DecisionRule + Action History",
        "trigger": "Agent 说'要调整策略'/'要设置告警'时"
      }
    },
    
    "actionIntegration": {
      "description": "Agent Write Path：所有写操作走 Action Dispatcher",
      "dispatcher_class": "ActionDispatcher",
      "location": "scripts/actions/dispatcher.py",
      "rules": {
        "LOW_STAKES": "直接执行，audit only",
        "MEDIUM_STAKES": "执行后通知站长",
        "HIGH_STAKES": "执行前必须批准"
      },
      "forbidden_paths": [
        "直接调用 send_feishu_card.py（必须经 ActionDispatcher）",
        "直接写 wiki 文件（必须经 UpdateWiki Action）"
      ]
    }
  }
}
```

### 7.2 新增 Design Decisions（D-026~D-031）

| ID | 决策 | 摘要 |
|----|------|------|
| D-026 | 3-Stage LLM Chain | Query Translator 分3阶段（分类/提取/生成），避免单次 prompt 过长 |
| D-027 | Function Call 优先 | 返回 Function Call 而非原始 SQL，提高 Agent 可解释性 |
| D-028 | Fail Gracefully | 翻译/执行失败返回友好错误 + 建议，不阻塞对话 |
| D-029 | 禁止 Action 绕过 | Agent 所有写操作走 Action Dispatcher，不允许绕过治理层 |
| D-030 | Schema 简化注入 | Session 启动仅注入约2KB Schema 摘要，不注入完整 ontology.json |
| D-031 | Query→FunctionCall 映射 | 5种 QueryIntent → 具体 Function 调用的确定性映射规则 |

---

## 八、Week 4 新增设计：QueryIntent → Function Call 映射表

> 这是 D-027/D-030 的具体化——让 QueryTranslator 的 Stage 3 有确定性规则可循

| QueryIntent | 调用的 Function | 参数来源 |
|-------------|----------------|---------|
| METRIC_RANKING | aggregateWeeklyMetrics (F-011) | scenic_spot_ids, metric_types, date_range |
| METRIC_TREND | calculateSearchTrend (F-001) | scenic_spot_id, date_range |
| CONTENT_ANALYSIS | enrichContentAsset (F-010) + raw query | scenic_spot_id, platform, date_range |
| COMPETITOR_BRIEF | competitiveAlert (F-006) + raw query | scenic_spot_id, lookback_days |
| ALERT_REVIEW | detectAnomaly (F-009) + raw query | scenic_spot_id, threshold |
| INSIGHT_SUMMARY | generateDailyInsight (F-008) | date, scenic_spot_ids |

**SQL 作为 Fallback（当没有合适 Function 时）：**
```python
FALLBACK_SQL = {
    "total_visitors_this_week": """
        SELECT SUM(value) FROM metric_snapshots 
        WHERE scenic_spot_id = 'ss:movie_town' 
        AND metric_type = 'visitor_count'
        AND date BETWEEN ? AND ?""",
    "anomaly_count": """
        SELECT COUNT(*) FROM metric_snapshots 
        WHERE is_anomaly = 1 AND date >= ?"""
}
```

---

## 九、对标 Palantir：AIP Ontology Agent Integration

### 9.1 我们的对应物

| Palantir AIP 概念 | 我们的实现 | 状态 |
|-------------------|-----------|------|
| Ontology SDK | AgentQueryHandler | 🔵 Week 4 设计 |
| LLM-powered Object Search | LLM Query Translator | 🔵 Week 4 设计 |
| Object Type Schema → Agent Context | SOUL.md Schema Injection | 🔵 Week 4 设计 |
| Action Execution via Ontology | ActionDispatcher | ⚠️ Week 3 设计，待实施 |
| Agent Decision Logging | action_log | ⚠️ Week 3 设计，待实施 |
| Palantir Copilot（自然语言查 Ontology）| 我们的 QueryHandler.ask() | 🔵 Week 4 设计 |

### 9.2 我们的独特价值（Palantir 没有的）

| 我们的能力 | Palantir 是否支持 |
|-----------|------------------|
| 中文自然语言查询 | ❌（Palantir 英文为主）|
| 飞书卡片作为 Action 输出 | ❌（Palantir Workshop UI）|
| 景区营销垂直场景优化 | ❌（通用平台）|
| 小红书/抖音/客流多模态数据 | ❌（结构化企业数据为主）|

---

## 十、与已有设计的对齐

### 10.1 对齐 Week 3 数据接入管道（PipelineRun）

✅ QueryTranslator 的 Stage 2 Entity Extraction 需要访问 `adapterGovernance.tier` 信息（判断 critical adapter）
✅ ALERT_REVIEW 查询需要 pipeline_runs 表（adapter 健康率 → 告警来源）
✅ Week 3 的 F-016 detectPipelineAnomaly 可以被 QueryHandler 直接调用

### 10.2 对齐 Week 2 Actions & Functions（functionTaxonomy）

✅ ActionDispatcher 复用 Week 2 的 5 层治理（Submission→Validation→Notification→Audit→Rollback）
✅ LOW/MEDIUM/HIGH 档位复用 Week 2 的 `action.category` 定义
✅ Function 类型（Pure/SideEffect/FunctionBacked/Aggregator）影响 QueryTranslator 的 fallback 策略

### 10.3 对齐 Week 1 Object Types

✅ Entity Extraction 的 scenic_spot 映射复用 `idNamingConvention.ScenicSpot` 规则
✅ QueryIntent METRIC_RANKING 的 metric_types 来自 `MetricSnapshot.properties.metricType` 枚举

### 10.4 对齐 D-006（JSON Git 快照层）

✅ Agent 写入 Action 产生的 object → 走 adapter 双写路径（SQLite + JSON Git）
✅ Action 结果（飞书卡片内容）→ 不入 Git 快照（与 PipelineRun 同样逻辑）

---

## 十一、未决问题（Week 5 解决）

### Q1: LLM Query Translator 用哪个 model？
**当前思考：** Stage 1（意图分类）用 fast model（M3 flash）；Stage 2（实体提取）用主力 model
**Week 5 实施时决策**

### Q2: QueryHandler 是独立 service 还是内嵌 Agent session？
**当前思考：** 内嵌在 OpenClaw Agent 中（scripts/ontology/query_handler.py 作为 tool），不需要独立 service
**理由：** 我们的查询 QPS < 10次/天，独立 service 过度设计

### Q3: SOUL.md Schema Injection 是手动还是自动？
**当前思考：** Session 启动时自动注入（OpenClaw hooks），不需要手动维护
**Week 5 实施：** 写一个 `scripts/ontology/inject_schema.py`，在 Agent session 启动时调用

### Q4: Agent 可以直接写新的 Object Instance 吗？
**场景：** Agent 说"帮我新增一个竞品景区：xxx"
**当前思考：** 可以，但需要走 Action 治理（CreateScenicSpot 是 highStakes → 需批准）
**Week 5 实施：** ActionDispatcher 增加 `CreateScenicSpot` / `UpdateMetricSnapshot` 等原子操作

---

## 十二、Week 4 vs Week 5 切分

### Week 4 完成（本次 🔵 设计阶段）
- ✅ Agent × Ontology 交互全视图
- ✅ LLM Query Translator 3-Stage 设计（QueryIntentClassification / EntityExtraction / QueryGeneration）
- ✅ AgentContextInjection 注入时机与方式（Session Startup / Query Time / Decision Time）
- ✅ Action Integration Write Path（D-029）
- ✅ QueryIntent → Function Call 映射表（D-030/D-031）
- ✅ ontology.json v1.5.0 新增 agentIntegration section
- ✅ 6 条新 Design Decision（D-026~D-031）

### Week 5 启动（8/3 周一）
- ⏳ scripts/ontology/query_handler.py — AgentQueryHandler 实施
- ⏳ scripts/ontology/llm_translator.py — LLM Query Translator 3-Stage 实施
- ⏳ scripts/ontology/inject_schema.py — SOUL.md Session 启动注入脚本
- ⏳ scripts/actions/dispatcher.py — Action Dispatcher（复用 Week 3 设计）
- ⏳ SOUL.md 末尾追加 Ontology Schema 简化版
- ⏳ 第一个真实 Query 测试："本周竞品排名" → 返回结构化结果

---

## 十三、Week 4 的关键交付物

```
交付物                          | 文件位置
-------------------------------|----------------------------------
Week4_Agent集成.md（本文档）      | wiki/技术配置/Ontology架构设计/
ontology.json v1.5.0           | wiki/技术配置/Ontology架构设计/
  └ agentIntegration section  |  新增 3KB
  └ designDecisions D-026~031 |  新增 6 条
  └ weekCycle 更新             |  Week 3 → Week 4
memory/2026-07-27.md          |  写入本週关键洞察
```

---

**Week 4 设计完结。下周 Week 5：实施 QueryHandler + LLM Translator + Schema 注入脚本。**
