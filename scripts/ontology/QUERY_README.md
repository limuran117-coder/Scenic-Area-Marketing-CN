# ontology_query.py · 实战示例

> 闭环 D-29 决策（D-32 完成）。覆盖 9 个公开方法的最小调用形态，复制即可用。

**位置**: `scripts/ontology/ontology_query.py`
**DB**: `~/.openclaw/workspace/.profile/ontology/ontology_store.db`（SSOT）
**调用**: CLI / Python API 两种

---

## 0. 初始化（Python API）

```python
from pathlib import Path
import sys
sys.path.insert(0, str(Path.home() / ".openclaw/workspace/scripts/ontology"))
from ontology_query import OntologyQuery

q = OntologyQuery()
```

---

## 1. 抖音 8 景区排名（飞书日报核心表）

```python
rank = q.daily_douyin_ranking()           # 默认最新一天
rank = q.daily_douyin_ranking("2026-06-19")  # 指定日期
# → [{景区ID, 景区, 简称, 是否核心竞品, 搜索指数, 搜索日环比, 综合指数, 综合日环比, 置信度}, ...]
# 排序：搜索指数 DESC
```

**CLI**: `python ontology_query.py douyin [YYYY-MM-DD]`
**真实输出（D-32）**: 清明上河园 233577 / 万岁山 40510 / 建业电影小镇 2295（+7.5%）

---

## 2. 单景区多日多源趋势

```python
trends = q.scenic_spot_metrics(
    "jianye_film_town",      # spot_id
    days=7,                   # 最近 7 天
    sources=["douyin", "xiaohongshu"],  # 默认
)
# → {"spot": {...}, "metrics": [{date, source, metric_type, value, daily_change}, ...]}
```

**CLI**: `python ontology_query.py spot jianye_film_town`
**用途**: 趋势图、环比分析、日报单景区板块

---

## 3. 竞品对比（核心 5 家）

```python
cmp = q.competitor_comparison(
    date="2026-06-19",
    include_self=True,        # 是否包含自身
)
# → [{景区, 搜索指数, 综合指数, ...}, ...]
```

**CLI**: `python ontology_query.py competitor`

---

## 4. 最近内容资产

```python
content = q.recent_content(
    spot_id="jianye_film_town",   # 可选, None=全部
    limit=10,
)
# → [{id, title, source, url, published_at, engagement, ...}, ...]
```

**CLI**: `python ontology_query.py content [spot_id]`

---

## 5. 7 天内容增量（选题发现）

```python
growth = q.content_growth_7d()    # 各景区 7 天新增内容数
# → [{景区, source, count_7d, count_prev_7d, growth_pct}, ...]
```

**CLI**: `python ontology_query.py growth`

---

## 6. 最近事件

```python
events = q.recent_events(days=30)
# → [{date, type, spot_id, description, ...}, ...]
```

**CLI**: `python ontology_query.py events [days]`

---

## 7. 决策规则查询

```python
rules = q.decision_rules()                   # 全部
rules = q.decision_rules(status="verified") # 仅已验证
# → [{id, name, status, statement, source_pattern, ...}, ...]
```

**CLI**: `python ontology_query.py rules`（D-32 实测: 4 条，3 verified + 1 hypothesis）

---

## 8. 单条 metric 溯源

```python
m = q.metric_with_sources("metric_uuid_here")
# → {id, spot_id, source, date, metric_type, value, raw_data, ...}
```

**CLI**: `python ontology_query.py metric <id>`

---

## 9. 健康检查（每日 cron 前置）

```python
health = q.health_check()
# → {scenic_spots, metric_snapshots, content_assets,
#    last_successful_ingest, ingest_count_7d, recent_failures, ...}
```

**CLI**: `python ontology_query.py health`

**D-32 实测**:
- `last_successful_ingest`: 2026-06-19T20:10:43（12 天无新 ingest ⚠️）
- `ingest_count_7d`: 0
- 根因：8 个 adapter 未工程化（D-031 决策）

---

## 实战案例：日报生成最小骨架

```python
from ontology_query import OntologyQuery

q = OntologyQuery()

# 1. 健康检查
h = q.health_check()
if h["recent_failures"]:
    print(f"⚠️ {len(h['recent_failures'])} failures")

# 2. 抖音排名（日报主表）
rank = q.daily_douyin_ranking()

# 3. 自身趋势
self_trends = q.scenic_spot_metrics("jianye_film_town", days=7)

# 4. 内容增量
growth = q.content_growth_7d()

# 5. 决策规则验证
rules = q.decision_rules(status="verified")

# → 拼成飞书卡片
```

---

## 已知约束（D-32 当前状态）

| 维度 | 现状 |
|------|------|
| 数据时效 | 12 天无新 ingest（last=6/19） |
| scenic_spots | 13（5 处 SSOT 重复未修） |
| metricSnapshots | 94 全是 6/19 backfill |
| contentAssets | 28 |
| decision_rules | 4（3 verified + 1 hypothesis） |

> 数据时效问题需要 Phase 4 启动 adapter 链工程化（不属于 query 层）
