# ADR-001: Ontology 架构融合路径

> 决策日期：2026-08-10 | 状态：**已采纳** | 决策者：站长（长期工程，不限时）
> 关联：`memory/topics/ontology-progress.md` · `MEMORY.md`（7/23 双db铁律）

---

## 背景

站长拍板：**将整个系统建成 ontology 架构的系统**（长期不限时工程）。

现状存在**双 ontology 体系并存**（13:44 核查）：

| 维度 | A. 业务版 `scripts/ontology/` | B. 通用 skill 版 `skills/ontology/` |
|------|-------------------------------|--------------------------------------|
| 存储 | SQLite `.profile/ontology/ontology_store.db` | JSONL `memory/ontology/graph.jsonl` |
| 领域 | 景区营销专属（SCENIC_SPOT_MAP 10景、metric_snapshots、tourist_segments、content_assets） | 通用（Person/Project/Task/Document/Event…） |
| 关系层 | ❌ 无（仅单表 upsert+快照） | ✅ create_relation/get_related(带方向) |
| 验证 | 基础 upsert | ✅ validate_graph（DFS 循环检测）+ schema merge/append |
| 真实数据 | 生产库 100+ 条 | 空 |
| 智能层 | W5 规划未实现 | 无 |

**各自局限**：A 有真实领域数据但缺"图谱/关系/验证"能力；B 有完整图谱引擎+验证但无景区领域数据。

**关键事实**：生产库最后写入 7/22（停 18 天）；两个 ontology cron 均 disabled；A 的 W5(QueryHandler/LLM Translator/ActionDispatcher) 未实现。

## 决策

**采用"图谱引擎融合"架构**：以 B（通用 ontology skill）的**图谱引擎 + schema 验证**作为系统骨架，叠加 A 的**景区营销领域模型**，接回 A 的生产数据，最终加 LLM 智能层。

具体：
1. **保留 A 的 SQLite 生产库**作为领域事实存储（不破坏现有数据），B 的图谱作为**关联/推断层**，两者通过 entity ID 对齐。
2. **扩展 B 的 schema**，新增景区领域 type：`ScenicSpot`、`MetricSnapshot`、`TouristSegment`、`ContentAsset`、`MarketingCampaign` 及 domain relation（如 `competes_with`、`has_metric`、`targets_segment`）。
3. **建设智能层**（原 W5 规划，落地）：QueryHandler（自然语言→图谱查询）+ LLM Translator（中文问句→结构化 query）。
4. **接入日常流水**：恢复/新建 ontology cron，使每个采集任务写入图谱。

## 理由

- **复用成熟引擎**：B 的 validate_graph/relation/schema 已实现且可验证，避免重复造轮子。
- **不破坏真实数据**：A 的生产库 100+ 条是不可再生事实，保留 SQLite 底座。
- **领域化优于通用**：schema 引擎通用，但 type 须领域化才有业务价值。
- **渐进落地**：分里程碑推进，每步可验证，符合长期工程定位。

## 影响/风险

- **双存储一致性**：SQLite 与 JSONL 需同一 entity ID 规约，否则脱节 → 用 `SCENIC_SPOT_MAP` 等常量做 ID 单源。
- **空壳残留**：`scripts/ontology.db`、`scripts/ontology/ontology_store.db` 0字节空壳应清理（防混淆）。
- **工程量大**：智能层需 LLM 集成 + 测试，放在后期里程碑。

## 里程碑路线图

| M | 内容 | 验收 |
|---|------|------|
| M1 | 本 ADR + 架构定稿 | 路径固化 |
| M2 | 景区领域 schema（type+relation+constraint） | schema 文件可验证 |
| M3 | 迁移生产数据到图谱（保留 SQLite） | 数据对齐，无丢失 |
| M4 | 关系查询/图谱遍历层 | 能答"谁在竞争"等关系问题 |
| M5 | LLM 智能层 | 自然语言→图谱 query |
| M6 | 接入日常流水 cron | 采集任务持续写入图谱 |

## 决策记录

- 2026-08-10 13:44 站长拍板"做成 ontology 架构"，不限时，不局限理解，可搜资料。
