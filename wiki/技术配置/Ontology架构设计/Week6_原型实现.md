# Week 6 · 最小可行 Ontology Layer 原型

> 日期：2026-06-19 | 状态：**✅ 原型跑通，163 个 Object 跨 7 张表**
> 任务来源：基础设施评估.md §三 + 实现路线图.md §四

---

## 一、原型交付物

| 文件 | 作用 | 状态 |
|------|------|------|
| `.profile/ontology/ontology_store.db` | SQLite 主存储 | ✅ 94 metric + 28 content + 13 景区 |
| `.profile/ontology/migrations/001_initial.sql` | Schema DDL | ✅ 11 表 + 4 视图 + 7 景区种子 |
| `.profile/ontology/snapshots/` | JSON Git 快照（D-006） | ✅ D-006 双轨 |
| `.profile/ontology/logs/` | 详细 ingest log | ✅ 按日分割 |
| `scripts/ontology/ontology_store.py` | SQLite CRUD 核心 | ✅ 字段映射+审计 |
| `scripts/ontology/ontology_query.py` | 预定义查询引擎 | ✅ 8 个查询方法 |
| `scripts/ontology/backfill_historical.py` | 历史 JSON 回填 | ✅ 14 文件 / +122/~11 |
| `scripts/ontology/seed_basic.py` | DecisionRule/TouristSegment/Region 种子 | ✅ 4+5+9 条 |

---

## 二、当前 db 状态（2026-06-19 20:11）

```
📈 当前 db 状态:
  scenic_spots:         13  (含 6 核心竞品 + 7 辅助景区)
  metric_snapshots:     94  (抖音/小红书 14 天历史)
  content_assets:       28  (小红书 7 天内容聚合)
  decision_rules:        4  (R-001 ~ R-004)
  tourist_segments:      5  (亲子/Z世代/大学生/省外/B端)
  regions:               9  (河南/郑州/中牟/开封/北京/...)
  spot_relations:       10  (5 个 competes_with + 5 个 located_in)
  events:                0  (待事件 adapter 接入)
  marketing_campaigns:   0  (待 campaign 接入)
  ingest_log:           14  (14 次回填全部 success)
  query_log:             5+ (各查询方法累计)
```

---

## 三、验证清单

| 验证项 | 命令 | 结果 |
|--------|------|------|
| Schema 初始化 | `python3 scripts/ontology/ontology_store.py init` | ✅ |
| 历史数据回填 | `python3 scripts/ontology/backfill_historical.py` | ✅ +122/~11 / 0 失败 |
| 抖音 8 景区排名 | `python3 scripts/ontology/ontology_query.py douyin` | ✅ 清明上河园 23.4 万居首 |
| 竞品对比 | `python3 scripts/ontology/ontology_query.py competitor` | ✅ 7 景区对比 |
| 单景区趋势 | `python3 scripts/ontology/ontology_query.py spot movie_town` | ✅ 3 天 6 条 |
| 7天内容增量 | `python3 scripts/ontology/ontology_query.py growth` | ✅ 9 条 |
| 决策规则 | `python3 scripts/ontology/ontology_query.py rules` | ✅ R-001~004 |
| Metric 双向引用溯源 | `python3 scripts/ontology/ontology_query.py metric <id>` | ✅ 1 source |
| 健康检查 | `python3 scripts/ontology/ontology_query.py health` | ✅ 0 失败 |
| 核心竞品链路 | `SELECT * FROM spot_relations WHERE source_id='movie_town'` | ✅ 5 个 competes_with |

---

## 四、原型架构（已落地的代码层）

```
┌────────────────────────────────────────────────────────┐
│  应用层 (cron / 飞书卡片 / Agent)                         │
│  → 调用 ontology_query 的 8 个预定义方法                  │
└─────────────────┬──────────────────────────────────────┘
                  │
┌─────────────────▼──────────────────────────────────────┐
│  Query Layer  ontology_query.py                       │
│  - daily_douyin_ranking() / competitor_comparison()    │
│  - scenic_spot_metrics() / content_growth_7d()         │
│  - recent_events() / decision_rules() / metric_with_sources()│
│  - health_check()                                      │
└─────────────────┬──────────────────────────────────────┘
                  │ SQL (join/group by/order by)
┌─────────────────▼──────────────────────────────────────┐
│  Store Layer  ontology_store.py                       │
│  - initialize() / ingest_objects() / write_json_snapshot()│
│  - _map_fields() (camelCase → snake_case)              │
│  - _upsert() (INSERT OR REPLACE 模式)                  │
│  - _log_ingest() (ingest_log + 日志文件)                │
└─────────────────┬──────────────────────────────────────┘
                  │ sqlite3 + migrations
┌─────────────────▼──────────────────────────────────────┐
│  .profile/ontology/ontology_store.db (SQLite)         │
│  + snapshots/*.json (Git 追踪层)                       │
│  + logs/*.log (按日 ingest log)                        │
└────────────────────────────────────────────────────────┘
                  ▲
                  │ backfill / 未来 adapter 双写
┌─────────────────┴──────────────────────────────────────┐
│  数据源 / Adapter                                       │
│  - adapter-douyin.py / adapter-xiaohongshu.py          │
│  - adapter-visitors.py / adapter-baidu.py             │
│  - backfill_historical.py (Phase 1 历史回填)            │
└────────────────────────────────────────────────────────┘
```

---

## 五、关键技术决策（Week 6 新增）

### D-007：模块布局采用 scripts/ontology/ 子包
**决策：** ontology 相关代码放 `scripts/ontology/` 子包而非散落 scripts/ 根。
**理由：**
1. 关注点内聚（store/query/seed/CLI 集中）
2. 共享同一份 FIELD_MAP 和路径常量
3. 后续添加 ontology_actions.py / ontology_agents.py 时不污染根目录
**结构：**
```
scripts/ontology/
├── __init__.py             # 公开 API（OntologyStore 等）
├── ontology_store.py       # SQLite CRUD 核心
├── ontology_query.py       # 预定义查询
├── backfill_historical.py  # Phase 1 历史数据回填
├── seed_basic.py           # DecisionRule/Region/TouristSegment 种子
└── (未来) ontology_actions.py / ontology_agents.py
```

### D-008：字段映射集中在 FIELD_MAP 常量（不是 SQL 视图）
**决策：** adapter ontology 字段（camelCase）→ db 列名（snake_case）通过 Python `FIELD_MAP` 字典映射，**不**在 SQL 视图里做。
**理由：**
1. adapter 字段命名遵循 ontology.json（camelCase 来自 OSDK 风格）
2. db 列名遵循 SQLite 惯例（snake_case）
3. 视图层做字段映射会让 SQL 维护成本翻倍（应用层要 SELECT as 别名）
4. Python 字典版本控制、单元测试都更简单
**示例：**
```python
FIELD_MAP["ContentAsset"] = {
    "scenicSpotId": "spot_id",
    "publishDate": "publish_date",
    "platform": "source",  # adapter 字段命名遵循 ontology.json
    ...
}
```

### D-009：JSON 适配字段单独处理（metrics.notes_count / date→publish_date）
**决策：** ContentAsset 的 `metrics.notes_count` 和 `date→publish_date` 映射在 `_map_fields()` 中特殊处理。
**理由：**
1. adapter JSON 中 `metrics` 是嵌套 dict，db 中是平铺列
2. adapter JSON 中 `date` 是"快照日期"，db 中 `publish_date` 是"内容发布日期"，但当前数据语义相同
**注意：** 未来若 adapter 输出真实的内容发布日期（vs 聚合快照日期），需要拆分为两个字段。

### D-010：原型采用"先全量回填，后续增量"策略
**决策：** Week 6 不改造 adapter，而是先 backfill 14 个历史 JSON，验证链路。
**理由：**
1. 最小风险 — 不动生产 cron 脚本
2. 快速验证 — 30 分钟内跑通全链路
3. 数据验证 — 用历史数据测试 query 正确性
4. 后续改造：Week 7+ 让 adapter 直接调 `store.ingest_objects()` 替代 JSON 输出

---

## 六、Week 6 发现的问题与待办

| # | 问题 | 优先级 | 建议解决时机 |
|---|------|--------|------------|
| 1 | adapter 中 `only_henan` 和 `only_dream` 是同一景区 | 🟡 中 | Week 7: 统一 ID 命名规范 |
| 2 | 部分历史数据 confidence 异常 (1.0 或缺失) | 🟢 低 | Week 7: backfill 时统一默认值 |
| 3 | 4 个 adapter (douyin/xhs/visitors/baidu) 仍输出 JSON，未调 store | 🟡 中 | Week 7-8: 逐步迁移 |
| 4 | metric_snapshots 缺 events / campaigns 接入 | 🟢 低 | Phase 2 后续 |
| 5 | ontology_query 没支持 LLM 自然语言→查询 转换 | 🟡 中 | Phase 4 (Week 4 of next cycle) |
| 6 | 没有自动 ingest cron (Phase 3 Actions 还没接) | 🟡 中 | Week 7-8 |

---

## 七、下一步（Week 7+ 计划）

### Week 7: Adapter 改造（最小破坏）
- [ ] `adapter-douyin.py`：保留 JSON 输出 + 新增 `store.ingest_objects()` 双写调用
- [ ] `adapter-xiaohongshu.py`：同上
- [ ] 验证：cron 跑完后 SQLite 行数 +1/天
- [ ] 跑健康检查 cron：每天 8:00 自检

### Week 8: Actions 接入（Phase 3）
- [ ] `ontology_actions.py` 模块：SendFeishuCard → Action Log
- [ ] 飞书日报调用 `query.daily_douyin_ranking()` 替代手写 SQL
- [ ] `action_log` 表自动记录

### 未来 (Week 4 of next cycle)
- [ ] LLM Query Translator：自然语言 → ontology_query 方法调用
- [ ] Agent prompt 注入 ontology 上下文
- [ ] 反向：Agent 决策 → ontology 写回

---

## 八、关键收获

1. **SQLite 完全够用** — 14 个 JSON / 122 条记录 不到 100KB 查询毫秒级
2. **关注点分离大法有效** — adapter/store/query 三层边界清晰，bug 都集中在边界（字段映射）
3. **Git 快照层 (D-006) 真香** — 失败重跑 backfill 0 风险，回滚一行命令
4. **Migrations 模式** — 未来 schema 演进可版本管理
5. **审计日志在 30 行代码内** — ingest_log + 日志文件 双写零负担

---

_本文档由 Ontology架构研究_每周深化 cron 生成（Week 6 原型实现）_
_下次更新：Week 7 Adapter 接入_
