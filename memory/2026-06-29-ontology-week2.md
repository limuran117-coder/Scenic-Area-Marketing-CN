# 2026-06-29 (周一) · Ontology Week 2 · Actions & Functions 标准化

## 任务
执行 Ontology 架构每周深化研究 — Week 2 主题：Actions & Functions 标准化方案
（继 Week 1 2026-06-24 Object Types + Link Types 之后，新周期 Week 2 启动）

## 完成情况

### 1. ontology.json v1.2.0 → v1.3.0 升级 ✅

**Schema 元数据：**
- version: 1.2.0 → 1.3.0
- updatedAt: 2026-06-24 → 2026-06-29
- 新增 3 个结构 section：functionTaxonomy / actionGovernance / designDecisions

**Functions: 7 → 11 (+4)**
- ⭐ calculateBaselineValue (FunctionBacked) — Week 1 预留 baselineValue 字段配套
- ⭐ detectAnomaly (FunctionBacked) — 异常检测，基于 calculateBaselineValue
- ⭐ aggregateWeeklyMetrics (Aggregator) — 周报聚合基础
- ⭐ enrichContentAsset (Pure) — LLM 辅助 + Entity Linking
- 全部 11 个 Function 加 type/sideEffects/idempotent/returnType/produces/usedBy 字段
- attributionScore 类型升级 Pure → SideEffect（写库语义）

**Actions: 5 → 7 (+2)**
- ⭐ AdjustStrategy (mediumStakes, functionBacked) — 调 3 个 Function 组合建议
- ⭐ OverrideRule (highStakes, 非 functionBacked) — 首次启用 Week 1 schema overridden_by link
- 全部 7 个 Action 加 category/functionBacked/functionImpl/produces 字段

**Validation Rules: 6 → 10 (+4)**
- V-007 DecisionRule.status 变更为 verified 必须 triggerCount > 0
- V-008 Action 写入前检查 cardinality 冲突
- V-009 highStakes Action 必须有 requiresApproval=true + 人工批准
- V-010 Action 输出必须可被 produces link 回溯

**设计决策: 15 → 20 (+5)**
- D-016 Function 4 类型分类
- D-017 Action 5 层治理
- D-018 Function-backed Action 模式
- D-019 Action Category 3 档
- D-020 V-007~V-010 业务规则层

### 2. 关键设计决策 (5 条新增)

- **D-016** Function 4 类型分类（Pure/SideEffect/FunctionBacked/Aggregator）— 治理可分级，避免 Agent 误用 SideEffect Function
- **D-017** Action 5 层治理（Submission/Validation/Notification/Audit/Rollback）— Palantir 业界标准
- **D-018** Function-backed Action 模式（Action 治理层 + Function 业务逻辑层组合）— 现代 Palantir 主推
- **D-019** Action Category 3 档（lowStakes/mediumStakes/highStakes）— 让 cron 任务显式选择风险等级
- **D-020** V-007~V-010 业务规则层（Schema 验证 ≠ 业务验证）— 两层验证互补

### 3. 输出文档 ✅

- `wiki/技术配置/Ontology架构设计/Week2_Actions_Functions.md`（24.7KB，16 节）
- `wiki/技术配置/Ontology架构设计/ontology.json` v1.3.0（83.7KB，**完整 read+write 流程**）
- `wiki/技术配置/Ontology架构设计/实现路线图.md` 更新（Week 2 标记完成，D-016~D-020 加入决策记录）
- `wiki/技术配置/Ontology架构设计/电影小镇-Ontology架构设计.md` 更新（Phase 1.5 status + 11 Function/7 Action 表）

### 4. 关键技术对标

**Palantir Function-backed Action（2025-11 业界标准）：**
- 参考：CSDN 翻译《Palantir-Functions 概念》[原文](https://blog.csdn.net/czhcc/article/details/154636416)
- "用于复杂的本体编辑操作（例如一个函数触发多个对象更新）作为 '函数支持的动作 (function-backed action)'"
- 我们 AdjustStrategy Action 调 assessContentVacuum + competitiveAlert + enrichContentAsset 3 个 Function → 完全对标

**Action Type Governance：**
- Palantir 标准：所有写操作必须经治理链
- 我们的 5 层：Submission(入参) → Validation(业务) → Notification(通知) → Audit(留痕) → Rollback(回滚)

**Action 风险等级：**
- lowStakes (3 个): SendFeishuCard / UpdateWiki / ScheduleOntologyResearch — 无副作用、可重试
- mediumStakes (2 个): CreateAlert / AdjustStrategy — 推送/建议，需 rollback
- highStakes (2 个): UpdateDecisionRule / OverrideRule — 改 ontology 核心，需人批

## 关键洞察

1. **Function 必带 type 标签** — 4 类型让 governance 可分级。Agent Tool 暴露矩阵明确：10 个 Function 暴露给 Agent，attributionScore (SideEffect) 不暴露。
2. **Action 必带 5 层治理** — Submission/Validation/Notification/Audit/Rollback 不能跳层。任意层失败 → Action 不执行 + 写 action_log + 飞书群通知。
3. **Function-backed 是现代 Palantir 主推** — Action 拆为"治理层 wrapper + Function 业务逻辑"，比"一个 Action 100 行"易测、复用、OSDK 友好。
4. **Schema 验证 ≠ 业务验证** — V-001~V-006 保 ontology 一致性，V-007~V-010 保业务正确性。两层互补缺一不可。
5. **高风险 Action 必须 requiresApproval** — UpdateDecisionRule/OverrideRule 不能让 Agent 自主决定，business 上线前必有人批。

## 发现的问题

| # | 问题 | 优先级 | 解决时机 |
|---|------|--------|----------|
| 1 | calculateBaselineValue / detectAnomaly 待实现（仅 schema） | 🔴 高 | Week 3 数据管道 |
| 2 | AdjustStrategy Action 调 3 个 Function 链路未实现 | 🔴 高 | Week 4 Agent × Ontology 集成 |
| 3 | OverrideRule Action 待实现 | 🟡 中 | Week 4（highStakes 需人工批准链路） |
| 4 | scripts/ontology/validate.py 未升级到 V-007~V-010 | 🔴 高 | Week 3 adapter 改造 |
| 5 | scripts/actions/ 目录不存在 | 🟡 中 | Week 3 创建 |
| 6 | rollback.py 尚未实现 | 🟡 中 | Week 4 |
| 7 | action_log 表已建但未接 governance chain | 🟡 中 | Week 3 |

## Token 守则执行

- 0 次重复跑（单次 audit + 单次 patch + 单次 consistency check）
- 0 次重试（设计文档 + ontology.json 一次到位）
- 0 次 LLM 调 LLM 问配额
- 2 次 web_search（Palantir Functions 概念 + function-backed action 模式）
- 1 次 web_fetch（CSDN Palantir-Functions 概念文章）
- 0 次 edit 工具改 ontology.json（用 Python 脚本 read+write 整文件，遵守"大文件约束"）

## 下一步

Week 3 主题：**数据接入管道设计（采集→映射→存储）**
- 实施 scripts/ontology/validate.py（V-001~V-010）
- Function calculateBaselineValue() + detectAnomaly() 写入 MetricSnapshot 派生列
- db migration 002 schema 扩展
- scripts/actions/ 目录创建
- adapter 改造按 D-011/D-015/D-016/D-020 实施
