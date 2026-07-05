# Ontology Layer 进展

## Week 6 原型 (2026-06-19) — 最小可行
- SQLite 163 objects / 7 表
- scripts/ontology/ 子包：store/query/backfill/seed 4 模块
- 14 个历史 JSON 全部回填，0 失败（+122 新增/~11 更新）
- 8 个预定义查询方法 + 健康检查已就位

## Week 1 (2026-06-24) — Object Types + Link Types 完整定义
- ontology.json v1.2.0（35.5KB）— Object Types 8→12, Link Types 14→33, Interfaces 3→7
- Phase 1 补完 4 个 OT：TouristSegment / Region / KnowledgeBase / Creator
- AgentO 覆盖率 12/14 (86%)

### Week 1 设计决策
- **D-011** ID Naming Convention — `<scope>:<type>:<value>` 三段式 + aliases 机制
- **D-012** Cardinality Matrix — 33 个 Link 全声明基数
- **D-013** KnowledgeBase 反向引用 — wiki markdown `[[objectId]]` 语法
- **D-014** Inverse Link 显式声明 — aggregated_from ↔ contributes_to 必须双向一致
- **D-015** Validation Rules 框架 — V-001~V-006 6 条规则

### Week 1 字段扩充
- ScenicSpot +aliases/province/city/peakSeasonMonths/typicalVisitDuration/ticketPriceRange/targetAgeGroups
- MetricSnapshot +baselineValue/dailyVolatility/isAnomaly/tags

## Week 2 (2026-06-29) — Actions & Functions 标准化
- ontology.json v1.3.0（83.7KB）— Functions 7→11, Actions 5→7, Validation 6→10, Decisions 15→20
- Week 2 新增 4 Function: calculateBaselineValue / detectAnomaly (FunctionBacked) / aggregateWeeklyMetrics (Aggregator) / enrichContentAsset (Pure)
- Week 2 新增 2 Action: AdjustStrategy (mediumStakes functionBacked) / OverrideRule (highStakes)

### Week 2 设计决策
- **D-016** Function 4 类型分类 — Pure / SideEffect / FunctionBacked / Aggregator
- **D-017** Action 5 层治理 — Submission→Validation→Notification→Audit→Rollback
- **D-018** Function-backed Action 模式 — Action 治理层 + Function 业务逻辑层组合
- **D-019** Action Category 3 档 — lowStakes / mediumStakes / highStakes
- **D-020** V-007~V-010 业务规则层 — Schema 验证 ≠ 业务验证

## Week 3 (计划)
- scripts/ontology/validate.py V-001~V-010 全量实施
- calculateBaselineValue/detectAnomaly 写入 MetricSnapshot 派生列
- scripts/actions/ 目录创建（function_impl + action_wrapper 拆分）

## 历史设计决策（Week 6）
- **D-007** scripts/ontology/ 子包布局（关注点内聚）
- **D-008** FIELD_MAP 字段映射（camelCase → snake_case）
- **D-009** 嵌套字段 metrics.notes_count / date→publish_date 在 _map_fields 特殊处理
- **D-010** 「先全量回填，后续增量」策略（不动生产 cron）

## dedup 迁移 (2026-07-03)
- migrations/20260703_dedup_scenic_spots.py 上线
- snapshots/ontology_store.pre_dedup_20260703.db（241KB）保留