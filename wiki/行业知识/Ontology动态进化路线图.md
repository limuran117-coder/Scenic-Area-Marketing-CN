# Ontology 动态进化路线图（2026-08-19）

> 目标：把 Ontology 从"静态知识库"进化为"动态进化系统智能体"
> 日日进步、日日新：搜集 → 总结 → 归纳 → 提炼 → 进化 → 输出

## 一、现状诊断（8/19 实测）

### 表使用率：17 张表只有 9 张在用

| 状态 | 表 | 说明 |
|------|-----|------|
| ✅ 在用 | scenic_spots (13) | 景区实体 |
| ✅ 在用 | spot_relations (10) | 景区关系（**停在 6/19，手工建的**）|
| ✅ 在用 | metric_snapshots (549) | 指标快照（**停在 8/10，adapter 跑过一次**）|
| ✅ 在用 | tourist_segments (5) | 客群画像 |
| ✅ 在用 | content_assets (36) | 内容资产 |
| ✅ 在用 | regions (9) | 区域 |
| ✅ 在用 | decision_rules (4) | 决策规则（**confidence 手工定，无验证闭环**）|
| ✅ 在用 | ingest_log (55) | 采集日志 |
| ✅ 在用 | query_log (28) | 查询日志（**无反馈闭环**）|
| ⚠️ 空置 | events / marketing_campaigns / action_log | 预留但从未启用 |
| ⚠️ 空置 | event_spot_links / campaign_spot_links / metric_content_links | 预留连接表 |
| ⚠️ 空置 | v_content_growth / v_weekly_trend | 预留视图 |

### 核心问题（对照"动态进化"目标）

1. **关系静态化**：spot_relations 是 6/19 一次手工写入，不会随行业趋势更新
2. **规则无闭环**：decision_rules 的 confidence 不随验证结果变化，不会自我修正
3. **采集断档**：metric_snapshots 停在 8/10（小红书 49 天断档、抖音竞品断档）
4. **无反馈机制**：query_log 记录了查询，但没分析"哪些问题答不上来→补哪些知识"

## 二、优化方向（按优先级）

### P0：动态关系更新（adapter 已就绪，依赖数据）
- **spot_relations 自动化**：✅ `scripts/ontology/adapters/adapter_relations.py` 已写好
  - 竞争强度 = 搜索指数重叠 0.5 + 客流相关性 0.3 + 内容量对比 0.2
  - 皮尔逊相关 + 归一化重叠度
- **⚠️ 当前瓶颈：竞品数据断档**（adapter dry-run 全是 0.000）
  - movie_town 数据完整（212 天 visitors/revenue）
  - 竞品景区只有零星数据：douyin search_index 4-5 条（停 5/29-7/22）、xiaohongshu 4-6 条（停 6/18）
  - 对应：抖音竞品采集断档 19 天、小红书断档 49 天
- **数据恢复即生效**：adapter 逻辑就绪，只要竞品指标继续灌入，每周 cron 重算就能出动态竞争强度

### P1：决策规则进化闭环（下周）
- **规则验证**：每条 decision_rules 记录触发次数 + 命中率
  - 例：R-003"竞品先动预警"触发后，如果实际客流受影响 → confidence 上调
- **规则淘汰**：长期命中率 < 50% 的规则降权/标记 deprecated
- **实现**：`decision_rules` 增加 `trigger_count` / `hit_rate` / `last_triggered_at` 字段

### P2：Graphiti 双向打通（已完成单向）
- **Ontology → Graphiti**：✅ 已做（sync_ontology.py）
- **Graphiti → Ontology**：把 Graphiti 检索到的动态洞察（如"星光铁花秀驱动客流"）写回 Ontology 的 events 表
- **效果**：动态时序事实（Graphiti）与静态业务图谱（Ontology）互补

### P3：进化引擎（长期）
- **每周知识进化**：已有"知识进化引擎_每周自学习" cron，让它在进化时更新 Ontology
- **自我提问**：从 query_log 分析"回答不了的问题"→ 生成采集任务
- **行业漂移监测**：监控竞品景区是否出现新业态/新活动 → 自动更新 scenic_spots 的 competitors

## 三、未来状态（目标）

### 短期（1-2 周）
- [x] Graphiti 本地化 + reranker + Ontology 单向打通
- [ ] 竞争关系每周自动重算（P0）
- [ ] 周洞察 cron 稳定运行

### 中期（1-2 月）
- [ ] 决策规则验证闭环（P1）
- [ ] Graphiti → Ontology 反向打通（P2）
- [ ] 采集断档恢复（小红书/抖音竞品）

### 长期（季度）
- [ ] 进化引擎：自我提问 → 采集 → 归纳 → 规则更新 全闭环
- [ ] 行业漂移监测：新竞品自动识别
- [ ] **系统能自己回答"竞争对手是谁"并给出依据**，而不是死记硬背

## 四、实现原则

1. **数据驱动**：所有关系/规则更新必须来自实际数据（指标、搜索指数、客流），不手工改
2. **可验证**：每次进化记录依据（confidence 变化要有 reason）
3. **轻量优先**：16GB 机器，优先 SQLite + Python，不引入重型依赖
4. **渐进式**：先做 P0（动态关系），跑通后再做 P1（规则闭环）
