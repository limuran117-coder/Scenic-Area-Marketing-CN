# 2026-06-19 · Ontology Week 6 原型实现

## 任务
执行 Ontology 架构每周深化研究 — Week 6 主题：最小可行 Ontology Layer 原型

## 完成情况
- ✅ 创建 `.profile/ontology/` 目录 + SQLite schema (001_initial.sql)
- ✅ 实现 `scripts/ontology/ontology_store.py` — SQLite CRUD + 字段映射 + ingest_log
- ✅ 实现 `scripts/ontology/ontology_query.py` — 8 个预定义查询方法
- ✅ 实现 `scripts/ontology/backfill_historical.py` — 14 个历史 JSON 回填
- ✅ 实现 `scripts/ontology/seed_basic.py` — DecisionRule/TouristSegment/Region 种子
- ✅ 数据验证：163 objects 跨 7 表，0 失败
- ✅ 8 个查询全部跑通 (抖音排名/竞品对比/趋势/内容增量/决策规则/链路溯源/健康检查)
- ✅ 输出文档：`Week6_原型实现.md`
- ✅ 推送架构转折到 MEMORY.md project 区

## 关键设计决策 (4 条)
- **D-007** scripts/ontology/ 子包布局（关注点内聚）
- **D-008** FIELD_MAP 字段映射（camelCase ontology → snake_case db）
- **D-009** 嵌套字段特殊处理（metrics.notes_count, date→publish_date）
- **D-010** "先全量回填，后续增量" 策略（最小破坏原则）

## 数据状态
- scenic_spots: 13 (6 核心 + 7 辅助)
- metric_snapshots: 94 (抖音/小红书 14 天历史)
- content_assets: 28 (小红书 7 天内容聚合)
- decision_rules: 4 (R-001~R-004)
- tourist_segments: 5 (亲子/Z世代/大学生/省外/B端)
- regions: 9 (河南/郑州/中牟/开封/...)
- spot_relations: 10 (5 competes_with + 5 located_in)

## 发现的问题
- adapter 中 `only_henan` 和 `only_dream` 是同一景区（ID 命名不一致）→ Week 7 统一
- 4 个 adapter 仍输出 JSON，未直接调 store.ingest_objects() → Week 7-8 改造
- 飞书日报仍用硬编码 SQL → Week 8 替换为 ontology_query

## Token 守则执行
- 全程无重复跑 backfill（一次成功，未重试）
- 全程无 LLM 调 LLM 问配额
- 全程无 chrome CDP 重连调试（设计完成一次跑通）
