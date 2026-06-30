# Week 2 · Actions & Functions 标准化方案

> 日期：2026-06-29 (周一) | 周期：**新周期 Week 2**（继 Week 1 Object Types + Link Types 之后）
> 状态：**✅ ontology.json v1.3.0 升级完成**
> 任务来源：实现路线图.md §五 Week 2 FDE 议程
> 上一周：Week 1 (2026-06-24) Object Types + Link Types 完整定义
> 下一周：Week 3 (2026-07-06) 数据接入管道设计（采集→映射→存储）

---

## 一、本周目标与完成情况

### 1.1 目标

1. **审计** ontology.json v1.2.0 现有 7 Functions + 5 Actions → 列出分类缺口
2. **引入** Function 4 类型分类（Pure / SideEffect / FunctionBacked / Aggregator）— 对标 Palantir Functions 概念 (2025-11)
3. **引入** Action 5 层治理（Submission / Validation / Notification / Audit / Rollback）
4. **引入** Action 3 档 Category（lowStakes / mediumStakes / highStakes）
5. **新增** 4 个 Function：calculateBaselineValue / detectAnomaly / aggregateWeeklyMetrics / enrichContentAsset
6. **新增** 2 个 Action：AdjustStrategy / OverrideRule
7. **更新** 全部现有 7 Functions（添加 type/sideEffects/idempotent/returnType/produces/usedBy 字段）
8. **更新** 全部现有 5 Actions（添加 category/functionBacked/functionImpl/produces 字段）
9. **新增** 4 条 Validation Rules：V-007~V-010（Action 业务规则层）
10. **新增** 5 条设计决策：D-016~D-020
11. **确立** Function-backed Action 模式（现代 Palantir 主推做法）

### 1.2 完成情况

| 任务 | 状态 | 增量 |
|------|------|------|
| Function 4 类型分类 | ✅ | functionTaxonomy section（4 类型 + 各自 governance/idempotent 说明）|
| Action 5 层治理 | ✅ | actionGovernance section（5 layers + 3 categories）|
| 4 个新 Function | ✅ | calculateBaselineValue / detectAnomaly / aggregateWeeklyMetrics / enrichContentAsset |
| 2 个新 Action | ✅ | AdjustStrategy / OverrideRule |
| 现有 7 Function 升级 | ✅ | 全部加 type/sideEffects/idempotent/returnType/produces/usedBy |
| 现有 5 Action 升级 | ✅ | 全部加 category/functionBacked/functionImpl/produces |
| V-007~V-010 业务规则 | ✅ | 4 条 Action 业务规则层验证 |
| D-016~D-020 设计决策 | ✅ | 5 条新决策 |
| Week 3 数据管道预备 | 🟡 | 已有 Schema，下周实施 |

---

## 二、Function 4 类型分类（v1.3.0 新增 section）

### 2.1 为什么需要分类？

Week 1 完成时 7 个 Function 全部是 read-only（计算后返回结果），缺乏对**写副作用、派生列、聚合**的显式区分。这导致：

- **无法区分 governance 强度**：calculateSearchTrend（无副作用）和 attributionScore（写 DecisionRule.attributionScore）治理需求完全不同
- **LLM 误用风险**：Agent 通过 Tool 直接调用 attributionScore 会绕过 Action 治理层
- **Function-backed 列无模式**：Week 1 schema 预留 MetricSnapshot.baselineValue 字段但无对应的"何时计算/谁计算"规范

### 2.2 4 类型定义

#### Type 1: Pure（纯计算）

| 字段 | 值 |
|------|---|
| 副作用 | ❌ 无 |
| 幂等性 | ✅ 必然幂等 |
| Governance | Low（仅审计调用次数）|
| 现有成员 | calculateSearchTrend / assessContentVacuum / predictVisitorFlow / sentimentAnalysis / competitiveAlert / enrichContentAsset |

**调用场景：** AIP/LLM Tool 的 read-only 函数、日报卡片渲染前数据准备、LLM Query Translator 内部调用。

#### Type 2: SideEffect（写副作用）

| 字段 | 值 |
|------|---|
| 副作用 | ✅ 写 Ontology |
| 幂等性 | 需显式声明（true 则可安全重试）|
| Governance | High（必须经 Action 调用，不可被 Agent 直接 invoke）|
| 现有成员 | attributionScore（写 DecisionRule.attributionScore）|

**调用场景：** 状态字段更新（DecisionRule.status）、派生属性持久化。

**关键约束：** SideEffect Function 永远不应被 Agent 通过 tool_use 直接调用。Agent 必须通过 Action → Function 链路才能触发 SideEffect。

#### Type 3: FunctionBacked（派生列函数）⭐ 现代 Palantir 主推

| 字段 | 值 |
|------|---|
| 副作用 | ❌ 默认无（计算时）；可派生为 SideEffect 模式持久化 |
| 幂等性 | ✅ true |
| Governance | Medium（持久化派生列时走 SideEffect 模式）|
| 现有成员 | calculateBaselineValue / detectAnomaly |

**调用场景：** MetricSnapshot.baselineValue 派生（14天滚动均值）、MetricSnapshot.isAnomaly 派生（|value-baseline|/baseline>0.3）、ScenicSpot.currentRank 派生。

**关键模式（参考 Palantir Function-backed column）：**
```
┌─────────────────────────────────────────────────────┐
│ MetricSnapshot (v1.3.0)                              │
│   ├── id: ms:douyin:movie_town:2026-06-29:search    │
│   ├── value: 876543                                  │
│   ├── baselineValue: ← calculateBaselineValue()    │
│   ├── dailyVolatility: ← calculateBaselineValue()  │
│   └── isAnomaly: ← detectAnomaly()                  │
│                                                       │
│ 每次 ON-READ：重新计算（不存库）                      │
│ 每次 ON-WRITE：固化派生值（存库，Function becomes SideEffect）│
└─────────────────────────────────────────────────────┘
```

#### Type 4: Aggregator（聚合函数）

| 字段 | 值 |
|------|---|
| 副作用 | ❌ 无 |
| 幂等性 | ✅ true |
| Governance | Low（不写入 Ontology）|
| 现有成员 | generateDailyInsight / aggregateWeeklyMetrics |

**调用场景：** 周报聚合（7 天 MetricSnapshot → 1 个 WeeklyReport）、日复盘聚合（30+ 卡片 → 1 个 insight 列表）。

### 2.3 Function 分类矩阵

| Function | v1.2.0 type | v1.3.0 type | sideEffects | idempotent | returnType | 关键变化 |
|----------|-------------|-------------|-------------|------------|------------|---------|
| calculateSearchTrend | (无) | **Pure** | F | T | TrendLine[] | 加 type/sideEffects/returnType |
| assessContentVacuum | (无) | **Pure** | F | T | VacuumAssessment | 同上 |
| predictVisitorFlow | (无) | **Pure** | F | T | Prediction | 同上 |
| sentimentAnalysis | (无) | **Pure** | F | T | SentimentReport | 同上 |
| attributionScore | (无) | **SideEffect** | T | T | AttributionResult | **类型升级**：从 Pure → SideEffect |
| competitiveAlert | (无) | **Pure** | F | T | AlertList | 加 type/sideEffects |
| generateDailyInsight | (无) | **Aggregator** | F | T | InsightCards | **类型升级**：从 Pure → Aggregator |
| calculateBaselineValue | (无) | **FunctionBacked** ⭐ | F | T | number | **本周新增** |
| detectAnomaly | (无) | **FunctionBacked** ⭐ | F | T | AnomalyDetection | **本周新增** |
| aggregateWeeklyMetrics | (无) | **Aggregator** ⭐ | F | T | WeeklyMetrics | **本周新增** |
| enrichContentAsset | (无) | **Pure** ⭐ | F | T | EnrichedAsset | **本周新增** |

---

## 三、Action 5 层治理（v1.3.0 新增 section）

### 3.1 为什么需要治理层？

**当前痛点（v1.2.0 Actions）：**
- 仅 `requiresApproval` / `auditLog` / `rateLimit` 三字段
- 无 preCondition（业务规则前置校验）
- 无 rollback 机制
- Action 输出物（产生什么 Object）无显式声明 → 无法做 produces 链接

**Palantir Action Type 治理（2025 业界标准）：**所有 Action 必须经完整治理链，确保"所有写操作可追溯、可回滚"。

### 3.2 5 层治理详解

#### Layer 1: Submission（入参校验）

**目的：** 拦截格式/必填/枚举/外键错误。

**规则：**
- 必填字段缺失 → 拒绝（HTTP 400 类语义）
- 枚举值不在 enum 列表 → 拒绝
- 外键引用不存在的 Object ID → 拒绝

**实施位置：** `scripts/ontology/validate.py::validate_action_params(action_name, params)`

#### Layer 2: Validation（业务规则校验）

**目的：** 在 Schema 验证（V-001~V-006）之上加业务规则（V-007~V-010）。

**规则：**
- V-007: DecisionRule.status 变更为 verified 必须 triggerCount > 0
- V-008: Action 写入前检查 cardinality 冲突（不破坏已有反向链）
- V-009: highStakes Action 必须有 requiresApproval=true + 人工批准记录
- V-010: Action 输出必须可被 produces link 回溯到 Ontology Object

**实施位置：** `scripts/ontology/validate.py::validate_action_business_rules(action_name, params, object_targets)`

#### Layer 3: Notification（执行前后通知）

**目的：** 风险沟通。

| Category | 通知策略 |
|----------|---------|
| lowStakes | 执行后异步通知（飞书群 + log） |
| mediumStakes | 执行前确认 + 执行后通知 |
| highStakes | 执行前必须人工批准 (requiresApproval=true) |

**实施位置：** `scripts/actions/notifier.py::notify(action_name, status, payload)`

#### Layer 4: Audit（审计日志）

**目的：** 全留痕。

**规则：**
- 所有 Action 写入 `action_log` 表（SQLite）：action_name, params, status, executed_at, executor, rollback_target
- 每条 Action 必须可追溯到 callingTasks
- 可追溯到相关 evidence_for / addresses links

**实施位置：** `action_log` 表（Week 6 原型已建）+ HasAuditTrail interface（Week 1 引入）

#### Layer 5: Rollback（回滚）

**目的：** 误操作可恢复。

| Action 类型 | 回滚策略 |
|------------|---------|
| 幂等 Action | 自动可重试（不需要 rollback）|
| 非幂等 SideEffect | 记录 pre_state 快照，rollback 时回写 |
| Function-backed Action | 重新计算即可（无副作用可回滚）|
| human-approved Action | rollback 必须二次人工批准 |

**实施位置：** `scripts/actions/rollback.py::rollback(action_log_id)`

### 3.3 Action 3 档 Category

| Category | 治理强度 | 现有成员 | 触发示例 |
|----------|---------|---------|---------|
| **lowStakes** | no approval / async notify / idempotent | SendFeishuCard / UpdateWiki / ScheduleOntologyResearch | 日报发送、wiki 写入 |
| **mediumStakes** | no approval / sync notify / rollback required | CreateAlert / AdjustStrategy | 预警推送、策略调整建议 |
| **highStakes** | approval required / audit critical / manual rollback | UpdateDecisionRule / OverrideRule | 规则状态变更、规则暂停 |

### 3.4 Action 升级矩阵

| Action | v1.2.0 | v1.3.0 变化 |
|--------|--------|------------|
| SendFeishuCard | lowStakes (隐式) | **+category/functionBacked/functionImpl 显式声明** |
| UpdateWiki | lowStakes (隐式) | **+category/functionBacked/functionImpl** |
| CreateAlert | mediumStakes (隐式) | **+category 显式 + dependsOn (detectAnomaly/competitiveAlert)** |
| UpdateDecisionRule | highStakes (隐式) | **+category + preCondition (V-007)** |
| ScheduleOntologyResearch | lowStakes (隐式) | **+category/functionBacked/functionImpl** |
| AdjustStrategy | (无) | **本周新增** mediumStakes functionBacked |
| OverrideRule | (无) | **本周新增** highStakes — Week 1 schema overridden_by link 首次启用 |

---

## 四、Function-backed Action 模式 ⭐ 核心模式

### 4.1 模式定义

**Function-backed Action = Action 治理层 + Function 业务逻辑层的组合。**

```
┌────────────────────────────────────────────────────────────┐
│ Action: AdjustStrategy (mediumStakes)                       │
│   ├── Governance: Submission/Validation/Notification/Audit/Rollback │
│   ├── functionBacked: true                                  │
│   ├── functionImpl: scripts/actions/adjust_strategy.py     │
│   └── 调用链:                                              │
│         ┌─────────────────────────────────────────┐       │
│         │ assessContentVacuum (Pure)              │       │
│         │ competitiveAlert (Pure)                │       │
│         │ enrichContentAsset (Pure)              │       │
│         └─────────────────────────────────────────┘       │
│           ↓ 聚合 → AdjustStrategy 建议                     │
│           ↓ produces: MarketingCampaign (suggestion)       │
└────────────────────────────────────────────────────────────┘
```

**现代 Palantir 主流做法（2025-11 CSDN 翻译）：** "用于复杂的本体编辑操作（例如一个函数触发多个对象更新）作为 '函数支持的动作 (function-backed action)'"。

### 4.2 Function-backed vs 普通 Action 区别

| 维度 | 普通 Action | Function-backed Action |
|------|------------|----------------------|
| 实现位置 | Action 自身含完整逻辑 | Action 调用 N 个 Function 组合 |
| 复用度 | 低（每次重写） | 高（Function 可被其他 Action 复用）|
| 测试性 | 需 mock 整个 Action | 可独立测每个 Function |
| OSDK 友好度 | 中 | 高（Function 可独立导出为 OSDK method）|

### 4.3 我们 7 个 Action 的 Function-backed 状态

| Action | functionBacked | 实际逻辑分布 |
|--------|---------------|------------|
| SendFeishuCard | ✅ true | 调 send_feishu_card.py（薄包装）|
| UpdateWiki | ✅ true | 调 update_wiki.py（git commit 包装）|
| ScheduleOntologyResearch | ✅ true | 调 schedule_research.py（cron 触发包装）|
| AdjustStrategy | ✅ true | 调 assessContentVacuum + competitiveAlert + enrichContentAsset |
| CreateAlert | ❌ false | 独立逻辑（飞书私信 + 频控）|
| UpdateDecisionRule | ❌ false | 独立逻辑（状态机）|
| OverrideRule | ❌ false | 独立逻辑（紧急状态切换）|

**观察：** lowStakes Action 普遍 functionBacked（轻量包装），highStakes Action 普遍非 functionBacked（独立逻辑，治理链不与业务耦合）。

---

## 五、4 个新 Function 详细设计

### 5.1 calculateBaselineValue（FunctionBacked）⭐

**用途：** 计算 MetricSnapshot 的 14 天滚动均值基线。

**输入：**
```json
{
  "scenicSpotId": "ss:movie_town",
  "metricType": "search_index",   // or "composite_index" / "visitor_count"
  "lookbackDays": 14
}
```

**输出：** `baselineValue: float`

**计算逻辑：**
```python
def calculateBaselineValue(scenicSpotId, metricType, lookbackDays=14):
    """返回 14 天滚动均值（用于异常检测 baseline）"""
    end = today
    start = end - timedelta(days=lookbackDays)
    snapshots = ontology_query.metric_snapshots(
        scenic_spot_id=scenicSpotId,
        metric_type=metricType,
        date_range=(start, end)
    )
    values = [s.value for s in snapshots if s.value is not None]
    if not values:
        return None
    return sum(values) / len(values)
```

**与 Week 1 schema 关系：**
- Week 1 在 MetricSnapshot 中预留 `baselineValue: number?` 字段
- 本 Function 计算该字段的值
- 调用模式：on-write (MetricSnapshot 写入时) 或 on-read (查询时即时算)

### 5.2 detectAnomaly（FunctionBacked）⭐

**用途：** 基于 baseline 检测异常。

**输入：**
```json
{
  "metricSnapshot": "ms:douyin:movie_town:2026-06-29:search_index",
  "threshold": 0.3
}
```

**输出：**
```json
{
  "isAnomaly": true,
  "deviation": 0.42,
  "severity": "high"
}
```

**计算逻辑：**
```python
def detectAnomaly(snapshot, threshold=0.3):
    baseline = calculateBaselineValue(
        snapshot.scenic_spot_id, snapshot.metric_type, lookbackDays=14
    )
    if baseline is None or baseline == 0:
        return {"isAnomaly": False, "deviation": 0, "severity": "low"}
    deviation = abs(snapshot.value - baseline) / baseline
    is_anomaly = deviation > threshold
    severity = "high" if deviation > 0.5 else "medium" if deviation > 0.3 else "low"
    return {
        "isAnomaly": is_anomaly,
        "deviation": round(deviation, 3),
        "severity": severity
    }
```

**与 Action 联动：** severity=high 时触发 CreateAlert（mediumStakes Action）。

### 5.3 aggregateWeeklyMetrics（Aggregator）⭐

**用途：** 周度竞争格局报告基础。

**输入：**
```json
{
  "scenicSpotId": "ss:movie_town",
  "week": "2026-W26",
  "metrics": ["search_index", "composite_index", "visitor_count"]
}
```

**输出：**
```json
{
  "scenicSpotId": "ss:movie_town",
  "week": "2026-W26",
  "searchIndex_avg": 920000,
  "compositeIndex_avg": 1050000,
  "visitorTotal": 28500,
  "top3Content": ["ca:xiaohongshu:abc", ...],
  "anomalies": ["ms:douyin:movie_town:2026-06-25:search_index"]
}
```

**调用方：** weekly_competitive_landscape_report（周日 09:00 cron）+ monthly_strategy_review

### 5.4 enrichContentAsset（Pure）⭐

**用途：** 内容资产语义富化（LLM 辅助 + Entity Linking）。

**输入：**
```json
{
  "contentAsset": "ca:xiaohongshu:abc123",
  "context": ["scenicSpot", "creator", "relatedMetrics"]
}
```

**输出：**
```json
{
  "enriched": {
    "sentimentScore": 0.82,
    "mentionedSpots": ["ss:movie_town"],
    "topKeywords": ["沉浸式", "夜景", "必打卡"],
    "relatedMetrics": ["ms:douyin:movie_town:2026-06-28:composite_index"],
    "confidence": 0.78
  }
}
```

**与 Action 联动：** AdjustStrategy 调用 enrichContentAsset 获取内容资产语义信息，组装成"是否复用此内容/类似内容投放到哪个客群"的建议。

---

## 六、2 个新 Action 详细设计

### 6.1 AdjustStrategy（mediumStakes，Function-backed）⭐

**用途：** 调整营销策略——向李涯推送建议（不直接执行）。

**为什么是 mediumStakes：**
- 推送建议而非直接执行（无 Ontology 写操作）
- 但频次高可能造成信息过载（rateLimit: 3/day）
- confidence < 0.7 时不发

**输入：**
```json
{
  "targetScenicSpotId": "ss:movie_town",
  "adjustmentType": "content",  // "price" | "channel" | "timing" | "content"
  "evidence": ["ms:douyin:movie_town:2026-06-28:composite_index", "dr:R-001"],
  "confidence": 0.85
}
```

**输出：** `MarketingCampaign (suggestion)` via produces link

**Function 调用链：**
```
AdjustStrategy Action
  ↓ calls
assessContentVacuum (Pure) → 检测内容缺口
competitiveAlert (Pure) → 评估竞品异动
enrichContentAsset (Pure) → 提取相似内容资产
  ↓ aggregate
{suggestion: {type, content, timing, targetSegment, confidence}}
  ↓
SendFeishuCard (lowStakes) → 推到飞书群 + 私信李涯
```

### 6.2 OverrideRule（highStakes，非 Function-backed）⭐

**用途：** 人工覆盖决策规则（紧急情况暂停某条规则）。

**为什么是 highStakes：**
- 决策规则是 Ontology 核心 governance 机制
- 暂停错误规则会误导后续自动化
- 必须 requiresApproval=true + 二次 rollback 批准

**输入：**
```json
{
  "ruleId": "dr:R-003",
  "reason": "R-003 在端午窗口误报 5 次，需排查算法",
  "overrideUntil": "2026-07-06T00:00:00+08:00",
  "approver": "李涯"
}
```

**输出：** `DecisionRule.overridden_by link`（Week 1 schema 预留）

**治理链：**
```
Submission → 校验 ruleId 存在 + reason 非空 + overrideUntil 是未来时间
Validation (V-009) → 校验 approver == '李涯'（hard-coded 防止误操作）
Notification → 飞书私信李涯请求批准
Audit → 写入 action_log + DecisionRule.overridden_by link
Rollback → overrideUntil 到期自动恢复（无需人工）
```

**Week 1 link type 首次实战：** Week 1 schema 设计了 `overridden_by` link（Cardinality N:M，directional true），本周 OverrideRule Action 首次创建该 link 实例。

---

## 七、对标 Palantir 的设计映射更新

| Palantir 组件 | v1.2.0 实现 | v1.3.0 增强 |
|---------------|------------|------------|
| Object Types | 12 个 | (无变化)|
| Properties | 6-12 个/OT | (无变化)|
| Link Types | 33 个 | (无变化)|
| **Action Types** | 5 个 / 1 层治理 (auditLog only) | **7 个 / 5 层治理 (Submission/Validation/Notification/Audit/Rollback) / 3 档 Category** ⭐ |
| **Functions** | 7 个 / 无分类 | **11 个 / 4 类型分类 (Pure/SideEffect/FunctionBacked/Aggregator) / Function-backed column 模式** ⭐ |
| Interfaces | 7 个 | (无变化)|
| Object Set Queries | 8 个预定义查询 | (无变化，Week 4 LLM Translator 深化)|
| **Function-backed Action** | (无) | **AdjustStrategy/SendFeishuCard/UpdateWiki 等 4 个 Action 启用该模式** ⭐ |
| OSDK 代码生成 | 暂未实现 | (Week 4 评估)|
| Action Type Governance | 1 层 (auditLog) | **5 层 (Submission~Rollback)** ⭐ |
| **Function Type System** | 无类型 | **4 类型（Pure/SideEffect/FunctionBacked/Aggregator）** ⭐ |

**对标差异（v1.2.0 → v1.3.0）：**
- ✅ Action Type Governance：1 层 → 5 层
- ✅ Functions：纯计算 → 4 类型分类 + Function-backed column 模式
- ⏳ OSDK 代码生成：仍待 Phase 2 后实施（Week 4 评估）
- ⏳ 多租户/RBAC：单 Agent 系统不需要

---

## 八、Tourism Ontology Function 设计参考

### 8.1 TOIR + Dublin Core 启示

**TOIR (Tourism Ontology for Information Retrieval) 关注的运营函数：**
- 客流预测（predictVisitorFlow）✅ 已有
- 季节性调整（peakSeasonFactor）⚠️ Week 3+ 考虑加入
- 客群偏好聚类（segmentPreference）⚠️ Phase 2+ 评估

**Dublin Core 启示的元数据：**
- dcterms:temporal → MetricSnapshot.collectedAt（已有）
- dcterms:spatial → ScenicSpot.located_in（已有）
- dcterms:audience → ContentAsset.targets → TouristSegment（已有）

### 8.2 文旅运营核心 Functions 缺什么？

| 现有 | 缺失 | 优先级 |
|------|------|--------|
| calculateSearchTrend | peakSeasonFactor（季节因子）| P1 |
| predictVisitorFlow | weatherImpactScore（天气影响分）| P1 |
| sentimentAnalysis | competitorBenchmark（竞品对标）| P2 |
| detectAnomaly | sentimentDriftDetection（舆情漂移）| P2 |

**Week 3 计划：** 评估 peakSeasonFactor 与 weatherImpactScore 是否需要新增为 Function（依赖天气 API + 历年客流数据已就位）。

---

## 九、Agent × Action 调用约束（Week 2 新增 governance）

### 9.1 Agent 调用 Action 的 3 条规则

1. **Agent 可直接调用 Pure Function**（calculateSearchTrend / assessContentVacuum / sentimentAnalysis 等）— 通过 LLM Tool 暴露
2. **Agent 调用 SideEffect Function 必须经 Action** — Agent 不允许直接 invoke attributionScore
3. **Agent 调用 highStakes Action 必须经人工批准** — UpdateDecisionRule / OverrideRule 始终需要人批

### 9.2 Function Tool 暴露矩阵

| Function | 暴露给 Agent Tool | 治理 |
|----------|-----------------|------|
| calculateSearchTrend | ✅ | Pure, safe |
| assessContentVacuum | ✅ | Pure, safe |
| predictVisitorFlow | ✅ | Pure, safe |
| sentimentAnalysis | ✅ | Pure, safe |
| competitiveAlert | ✅ | Pure, safe (但结果可能触发 CreateAlert) |
| enrichContentAsset | ✅ | Pure, safe |
| generateDailyInsight | ✅ | Aggregator, safe |
| aggregateWeeklyMetrics | ✅ | Aggregator, safe |
| **calculateBaselineValue** | ✅ | FunctionBacked, safe |
| **detectAnomaly** | ✅ | FunctionBacked, safe |
| **attributionScore** | ❌ | SideEffect — 必须经 UpdateDecisionRule Action |

---

## 十、失败模式与降级策略

### 10.1 Function 失败模式

| 模式 | 触发条件 | 降级策略 |
|------|---------|---------|
| **数据不足** | 输入 ObjectSet 为空 | 返回 None + log warning，不抛异常 |
| **类型不匹配** | scenicSpotId 格式错误 | 抛 ValidationError (V-001) |
| **基数冲突** | 试图破坏 N:1 关系 | 抛 ValidationError (V-002/V-008) |
| **依赖 Function 失败** | calculateBaselineValue 失败 → detectAnomaly 失败 | detectAnomaly 跳过，isAnomaly=None |

### 10.2 Action 失败模式

| 模式 | 触发条件 | 降级策略 |
|------|---------|---------|
| **审计日志写失败** | SQLite 写失败 | 阻塞 Action（不写入 Ontology）|
| **回滚目标不存在** | rollback_target 找不到 | 抛异常 + 飞书紧急告警（CreateAlert high severity）|
| **并发写入冲突** | 同时两个 Action 写同一 Object | SQLite 事务串行化 |
| **Function 调用超时** | LLM 调用 > 30s | 返回部分结果 + 标注 incomplete |

### 10.3 governance 链中断处理

**5 层治理链不允许跳过任何一层。** 任意层失败 → Action 不执行 → 写 action_log 记录原因 → 飞书群通知。

---

## 十一、Validation Rules 完整列表（v1.3.0 = 10 条）

| ID | 名称 | 层级 | 触发 |
|----|------|------|------|
| V-001 | ID 必须遵循 idNamingConvention | Schema | 写入时 |
| V-002 | Link Type 实例化时检查 cardinality | Schema | 写入时 |
| V-003 | Inverse link 双向一致 (aggregated_from ↔ contributes_to) | Schema | 写入时 |
| V-004 | ScenicSpot 的 located_in 必须指向 Region 对象 | Schema | 写入时 |
| V-005 | confidence 字段值必须在 [0, 1] 区间 | Schema | 写入时 |
| V-006 | DecisionRule.status == 'verified' 必须有 triggerCount > 0 | Schema | 写入时 |
| **V-007** ⭐ | **DecisionRule.status 变更为 verified 必须 triggerCount > 0** | **Action Business** | **Action:UpdateDecisionRule** |
| **V-008** ⭐ | **Action 写入前检查 cardinality 冲突** | **Action Business** | **所有 Action** |
| **V-009** ⭐ | **highStakes Action 必须有 requiresApproval=true + 人工批准记录** | **Action Business** | **Action:UpdateDecisionRule / OverrideRule** |
| **V-010** ⭐ | **Action 输出必须可被 produces link 回溯到 Ontology Object** | **Action Business** | **所有 Action** |

**两层验证互补：**
- **Schema 层（V-001~V-006）**：保证 ontology 一致性（ID/cardinality/双向链）
- **Action Business 层（V-007~V-010）**：保证业务正确性（状态机前置/审批/可追溯）

---

## 十二、关键设计决策（Week 2 新增 5 条）

### D-016：Function 4 类型分类
**决策：** 引入 Pure / SideEffect / FunctionBacked / Aggregator 4 类型标签。
**理由：**
1. Week 1 时 7 个 Function 全部 read-only，缺少对写副作用/派生列/聚合的显式区分
2. governance 必须按 type 分级：SideEffect Function 必须经 Action 调用，不可被 Agent 直接 invoke
3. FunctionBacked 是现代 Palantir 主推模式（参考 2025-11 CSDN Functions 概念翻译）
**实施：** ontology.json §functionTaxonomy；所有 Function 显式声明 type/sideEffects/idempotent/returnType 字段。

### D-017：Action 5 层治理
**决策：** 所有 Action 必须经 Submission/Validation/Notification/Audit/Rollback 5 层。
**理由：**
1. Palantir Action Type 治理是确保"所有写操作可追溯、可回滚"的核心
2. 当前 5 个 Action 仅有 auditLog 一层，缺 preCondition/rollback 机制
3. 治理层与业务逻辑分离，让 Action 复用更安全
**实施：** ontology.json §actionGovernance；Week 2+ scripts/ontology/validate.py 升级到 V-007~V-010。

### D-018：Function-backed Action 模式
**决策：** 所有 Action 显式声明 functionBacked + functionImpl 字段。
**理由：**
1. 现代 Palantir 主推：Action 治理层 + Function 业务逻辑层组合
2. AdjustStrategy 调 3 个 Pure Function 组合成建议，比"一个 Action 含 100 行逻辑"更易测
3. OSDK 自动生成时，Function 可独立导出为 method，Action 仅是 wrapper
**实施：** ontology.json actions.*.functionBacked + functionImpl；Week 3+ scripts/actions/ 拆分为 function_impl.py + action_wrapper.py。

### D-019：Action Category 3 档
**决策：** lowStakes / mediumStakes / highStakes 3 档 category。
**理由：**
1. 不同 Action 风险/成本差异巨大
2. governance 字段（requiresApproval/rateLimit/preCondition）按 category 默认值自动填充
3. Cron 任务设计时显式选择 category，提醒工程师该 Action 的风险等级
**实施：** ontology.json actions.*.category；Week 3+ cron 任务元数据加 category 字段。

### D-020：V-007~V-010 业务规则层
**决策：** 引入 4 条 Action 业务规则层验证。
**理由：**
1. Schema 层（V-001~V-006）只能保 ontology 一致性，无法保业务正确性
2. V-007 保证 DecisionRule 状态机不会乱跳（verified 必须有证据）
3. V-008 保证 Action 不会破坏已有反向链
4. V-009/V-010 保证高风险 Action 必有人批 + 可追溯
**实施：** scripts/ontology/validate.py 升级；Week 3+ adapter 升级后接入 V-007~V-010。

---

## 十三、Week 2 发现的问题

| # | 问题 | 优先级 | 解决时机 |
|---|------|--------|----------|
| 1 | calculateBaselineValue / detectAnomaly 待实现（仅 schema 定义）| 🔴 高 | Week 3 数据管道 + 派生列写入 |
| 2 | AdjustStrategy Action 调 3 个 Function 链路未实现 | 🔴 高 | Week 4 Agent × Ontology 集成时 |
| 3 | OverrideRule Action 待实现 | 🟡 中 | Week 4（highStakes 需人工批准链路）|
| 4 | scripts/ontology/validate.py 未升级到 V-007~V-010 | 🔴 高 | Week 3 adapter 改造 |
| 5 | scripts/actions/ 目录不存在（function_impl + action_wrapper 拆分的目录结构）| 🟡 中 | Week 3 创建 |
| 6 | rollback.py 尚未实现（仅 schema 描述）| 🟡 中 | Week 4 实现 |
| 7 | action_log 表已建但未接 governance chain | 🟡 中 | Week 3 adapter 改造时接 |
| 8 | peakSeasonFactor / weatherImpactScore 等 tourism function 待评估 | 🟢 低 | Week 5+ |

---

## 十四、下一步（Week 3+ 计划）

### Week 3：数据接入管道设计（采集→映射→存储）
- [ ] scripts/ontology/validate.py 升级到 V-001~V-010
- [ ] Function calculateBaselineValue() 写入 MetricSnapshot.baselineValue
- [ ] Function detectAnomaly() 写入 MetricSnapshot.isAnomaly
- [ ] Action AdjustStrategy / OverrideRule 脚本骨架（Week 4 完善）
- [ ] scripts/actions/ 目录创建（function_impl + action_wrapper 拆分）
- [ ] db migration 002 扩展 MetricSnapshot 字段

### Week 4：AI Agent × Ontology 集成
- [ ] Function Tool 暴露矩阵实施（10 个 Function 暴露给 Agent）
- [ ] Agent system prompt 注入 ontology 上下文
- [ ] OverrideRule 人工批准链路（飞书审批回调）
- [ ] rollback.py 完整实施

### Week 5：基础设施深度评估
- [ ] OSDK 代码生成评估（Python 版）
- [ ] peakSeasonFactor / weatherImpactScore Function 设计
- [ ] KB scanner 与 ActionGovernance 集成评估

### Week 6：原型 v2
- [ ] KnowledgeBase scanner 完整实施
- [ ] action_log 全量审计追溯 demo
- [ ] Week 1+2 schema 全部导入 SQLite

---

## 十五、关键收获

1. **Function 必须有 type 标签** — Pure/SideEffect/FunctionBacked/Aggregator 让 governance 可分级，避免 Agent 误用 SideEffect Function
2. **Action 必须有 5 层治理** — Submission/Validation/Notification/Audit/Rollback 是 Palantir 业界标准，week 2 一次性补齐
3. **Function-backed 是现代 Palantir 主推** — Action 治理层 + Function 业务逻辑层组合，比"一个 Action 100 行"更易测、复用、OSDK 友好
4. **高风险 Action 必须 requiresApproval** — UpdateDecisionRule/OverrideRule 不能让 Agent 自主决定，business 上线前必有人批
5. **Schema 验证 ≠ 业务验证** — V-001~V-006 保 ontology 一致性，V-007~V-010 保业务正确性，两层验证互补

---

## 十六、参考资源

- [Palantir-Functions 概念 (CSDN 翻译 2025-11)](https://blog.csdn.net/czhcc/article/details/154636416) — Function 概念 + Function-backed action 模式
- [Palantir Foundry Ontology 文档](https://www.palantir.com/docs/foundry/ontology/overview/) — 6 大组件 + Action Type governance
- [Palantir AIP Functions](https://www.palantir.com/docs/foundry/functions/overview/) — Functions vs Actions 区分
- [AgentO (Agentic AI Ontology)](https://github.com/agentic-patterns/agentic-ai-onto) — Agent 与 Ontology 集成模式
- [TOIR (Tourism Ontology for Information Retrieval)](https://link.springer.com/chapter/10.1007/11590019_4)
- [Dublin Core Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)

---

_本文档由 Ontology架构研究_每周深化 cron 生成（Week 2 Actions & Functions 标准化）_
_下次更新：Week 3 数据接入管道设计_
