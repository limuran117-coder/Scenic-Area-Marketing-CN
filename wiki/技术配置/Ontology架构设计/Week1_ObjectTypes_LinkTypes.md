# Week 1 · Object Types 完整定义 + Link Types 设计

> 日期：2026-06-24 (周三) | 周期：**新周期 Week 1**（继 Week 6 原型后启动）
> 状态：**✅ ontology.json v1.2.0 升级完成**
> 任务来源：实现路线图.md §四 Phase 1 未完事项 + Week 6 发现问题

---

## 一、本周目标与完成情况

### 1.1 目标

1. **审计** ontology.json v1.1.4 已定义的 8 Object Types + 14 Link Types → 列出缺口
2. **补完** 实现路线图 §四 Phase 1 未完事项 (TouristSegment, Region, KnowledgeBase, Creator)
3. **扩充** ScenicSpot 的 tourism-specific 属性（基础设施评估 §五）
4. **新增** 8 个 Link Types 覆盖 Adapter/Function 调度、证据→规则、规则→问题、KB 引用等
5. **新增** 4 个 Interfaces (HasRegionalContext, TimeSeries, HasAuditTrail, HasPricing)
6. **建立** ID Naming Convention（解决 Week 6 发现的 only_henan/only_dream 同景区不同 ID）
7. **建立** Cardinality Matrix（显式声明所有 Link 的 N:M/1:N 关系）
8. **建立** Validation Rules 框架（6 条验证规则）

### 1.2 完成情况

| 任务 | 状态 | 增量 |
|------|------|------|
| 审计现有 schema | ✅ | 列出 4 个 Object Type 缺失、3 个 Link 缺失 |
| TouristSegment 定义 | ✅ | 新增 Object Type + 5 个实例 |
| Region 定义 | ✅ | 新增 Object Type + 6 个实例（含嵌套） |
| KnowledgeBase 定义 | ✅ | 新增 Object Type（KB scanner 待 Phase 1 之后补） |
| Creator 定义 | ✅ | 新增 Object Type（待爬虫升级） |
| ScenicSpot tourism 属性扩充 | ✅ | +aliases/province/city/peakSeasonMonths/typicalVisitDuration/ticketPriceRange/targetAgeGroups |
| MetricSnapshot 异常检测属性 | ✅ | +baselineValue/dailyVolatility/isAnomaly/tags |
| 8 个新 Link Types | ✅ | monitors/produces/evidence_for/addresses/references/created_by/located_in_region/targeted_by |
| 4 个新 Interfaces | ✅ | HasRegionalContext/TimeSeries/HasAuditTrail/HasPricing |
| 11 个 reverse-edge Link Types | ✅ | has_campaign/has_content/has_metric/triggers_sentiment/mentioned_in/uses/overridden_by/evidence_for_inverse/contains/written_by/created_by_inverse |
| ID Naming Convention | ✅ | 12 个 Object Type 命名规则 |
| Cardinality Matrix | ✅ | 33 个 Link 全部声明 cardinality |
| Validation Rules | ✅ | 6 条规则（待实现 scripts/ontology/validate.py） |
| Phase 2 启动 | 🟡 | Week 7 待实施 adapter 改造 |

---

## 二、Object Types 完整定义（v1.2.0 = 12 个）

### 2.1 12 个 Object Type 总览

| # | Object Type | 描述 | 实例数 | Link Types | Week 加入 |
|---|-------------|------|--------|-----------|----------|
| 1 | **ScenicSpot** | 景区（电影小镇+竞品） | 13 | 7 | v1.0 |
| 2 | **MetricSnapshot** | 数据快照（日级度量） | 94 | 3 (+evidence_for) | v1.0 |
| 3 | **ContentAsset** | 内容资产（笔记/视频） | 28 | 5 | v1.0 |
| 4 | **Event** | 事件/动态 | 0 | 3 (+mentioned_in) | v1.0 |
| 5 | **MarketingCampaign** | 营销活动 | 0 | 5 (+uses) | v1.0 |
| 6 | **DecisionRule** | 决策规则 | 4 | 5 | v1.0 |
| 7 | **OntologyAdapter** | Adapter 元数据 | 2 | 2 (+monitors) | v1.0 |
| 8 | **AgentTask** | 定时任务 | 14+ | 2 | v1.0 |
| 9 | **TouristSegment** ⭐ | 客群细分 | 5 | 2 (+located_in_region, +targeted_by) | **v1.2.0** |
| 10 | **Region** ⭐ | 地理区域（嵌套） | 9 | 2 (+contains) | **v1.2.0** |
| 11 | **KnowledgeBase** ⭐ | 知识库文档 | 0 | 2 (+references, +written_by) | **v1.2.0** |
| 12 | **Creator** ⭐ | 内容创作者 KOL/UGC | 0 | 1 (+created_by_inverse) | **v1.2.0** |

⭐ = 本周新增

### 2.2 ScenicSpot 扩充（Tourism Ontology 参考属性）

来源：基础设施评估.md §五（TOIR/Dublin Core 启发）

```json
"ScenicSpot": {
  // ... v1.0 字段保留
  "aliases": ["only_dream"],              // ⭐ Week 1 补：解决 only_henan/only_dream 双 ID 问题
  "province": "河南",                     // ⭐ Week 1 补：冗余于 Region 但便于查询
  "city": "郑州",                         // ⭐ Week 1 补：同上
  "peakSeasonMonths": [4, 5, 10],         // ⭐ Tourism Ontology: 旺季月份
  "typicalVisitDuration": 6,              // ⭐ Tourism Ontology: 典型游览时长（小时）
  "ticketPriceRange": "80-150",           // ⭐ Tourism Ontology: 票价区间
  "targetAgeGroups": ["儿童", "青年", "中年"]  // ⭐ Tourism Ontology: 目标年龄段
}
```

### 2.3 MetricSnapshot 异常检测属性

```json
"MetricSnapshot": {
  // ... v1.0 字段保留
  "baselineValue": 950000,               // ⭐ Week 1 补：14天滚动均值
  "dailyVolatility": 0.08,               // ⭐ Week 1 补：7天滚动标准差/均值
  "isAnomaly": false,                    // ⭐ Week 1 补：异常标记
  "tags": ["端午窗口", "5月峰值"]         // ⭐ Week 1 补：业务标签
}
```

**异常检测规则（Week 2 Functions 设计时实现）：**
```
anomaly = abs(value - baselineValue) / baselineValue > 0.3
```

### 2.4 新 Object Type 详细设计

#### TouristSegment（Week 1 新增）

| 字段 | 类型 | 说明 |
|------|------|------|
| id | string PK | ts:<name_slug> |
| name | string | 客群名 |
| ageRange | string | "18-25" |
| genderSplit | object | {"male": 0.4, "female": 0.6} |
| primaryRegionIds | array[Region] | 主要客源地 |
| characteristics | object | {preferredCategories, avgSpending, groupSize} |

**5 个种子实例**（Week 6 已 seed）：亲子家庭 / Z世代 / 大学生 / 省外游客 / B端团建

#### Region（Week 1 新增 + Week 6 seed 已存在）

**嵌套层级：** country → province → city → district

```json
[
  {"id": "rg:province:河南", "level": "province"},
  {"id": "rg:city:郑州", "parentRegionId": "rg:province:河南"},
  {"id": "rg:district:中牟", "parentRegionId": "rg:city:郑州", "aliases": ["中牟县"]}
]
```

**关键设计：** `aliases` 字段解决「中牟 vs 中牟县」等同义区域查询歧义（Week 1 与 ScenicSpot.aliases 思路一致）

#### KnowledgeBase（Week 1 新增，Phase 1 后扫描器实现）

**设计动机：** wiki/ 目录树是隐式知识图谱，但缺乏结构化索引 → 无法支持 KB ↔ Ontology 双向引用。

**Phase 1 后实现 KB scanner：**
```python
# 伪代码
for md_file in walk('wiki/'):
    kb = KnowledgeBase(
        id=f"kb:{path_slug}",
        path=md_file.relative_path,
        checksum=sha256(md_file.content),
        tags=parse_frontmatter(md_file).get('tags', [])
    )
    # 解析 [[objectId]] 语法生成 references link
    for ref in parse_md_links(md_file.content, pattern=r'\[\[([a-z_]+:[a-z_0-9]+)\]\]'):
        kb.references.append(ref)
```

#### Creator（Week 1 新增，待爬虫升级）

**触发条件：** xiaohongshu_crawl.py 支持单条笔记详情爬取后启用。

**当前状态：** schema 定义完成，instance 0，dataSource 标注 "爬虫待升级"。

---

## 三、Link Types 完整定义（v1.2.0 = 33 个）

### 3.1 按功能分组

**关系类（15 个）：**
- belongs_to, has_campaign, has_content, has_metric（景区-数据 4 件套）
- competes_with（竞品 M:N）
- mentions, triggers_sentiment, promotes, uses（内容相关 4 件套）
- targets, targeted_by（客群相关 2 件套，双向）
- located_in, located_in_region, contains（地理相关 3 件套）
- affected_by_*, mentioned_in（事件相关 2 件套）
- created_by, created_by_inverse（创作者相关）

**调度类（5 个）：**
- transforms_to（Adapter→Object）
- monitors（Adapter→景区/指标，本周新增）
- produces（Function→Object，本周新增）
- triggers_action（Rule→Action）
- triggered_by（Agent→Event/Rule）

**证据/知识类（5 个）：**
- aggregated_from, contributes_to（双向聚合）
- based_on_metric（Rule→Metric）
- evidence_for（Metric/Event→Rule，本周新增）
- references（KB→Object，本周新增）

**治理类（3 个）：**
- addresses（Rule→Problem，本周新增）
- overridden_by（Rule→Rule）
- writes_to, written_by（Agent/KB 双向）

### 3.2 Cardinality Matrix（Week 1 新增）

**33 个 Link 的基数完整声明（schema/cardinalityMatrix.definitions）：**

| Link | Source | Target | Cardinality | Directional |
|------|--------|--------|------------|-------------|
| competes_with | ScenicSpot | ScenicSpot | M:N | false |
| belongs_to | MetricSnapshot/Campaign/Asset | ScenicSpot | N:1 | true |
| has_campaign | ScenicSpot | MarketingCampaign | 1:N | true |
| has_content | ScenicSpot | ContentAsset | 1:N | true |
| has_metric | ScenicSpot | MetricSnapshot | 1:N | true |
| transforms_to | OntologyAdapter | MetricSnapshot/ContentAsset | 1:N | true |
| monitors ⭐ | OntologyAdapter | ScenicSpot/MetricSnapshot | 1:N | true |
| mentions | ContentAsset | ScenicSpot | N:M | false |
| triggers_sentiment | ContentAsset | Event | 1:N | true |
| promotes | MarketingCampaign | ContentAsset | 1:N | true |
| uses | MarketingCampaign | ContentAsset | N:M | true |
| targets | Campaign/Asset | TouristSegment | N:M | false |
| targeted_by ⭐ | Campaign/Asset | TouristSegment | N:M | true |
| located_in | ScenicSpot/Region | Region | N:1 | true |
| located_in_region ⭐ | TouristSegment | Region | N:M | false |
| contains ⭐ | Region | Region | 1:N | true |
| affects | Event | ScenicSpot | M:N | true |
| mentioned_in ⭐ | Event | ContentAsset/KB | N:M | false |
| created_by ⭐ | ContentAsset | Creator | N:1 | true |
| created_by_inverse ⭐ | Creator | ContentAsset | 1:N | true |
| produces ⭐ | Function (logical) | MetricSnapshot/Asset/Event | 1:N | true |
| triggers_action | DecisionRule | AgentTask/Event | 1:N | true |
| triggered_by | AgentTask | Event/Rule | N:M | false |
| aggregated_from | MetricSnapshot | ContentAsset | M:N | true (↔) |
| contributes_to | ContentAsset | MetricSnapshot | N:M | true (↔) |
| based_on_metric | DecisionRule | MetricSnapshot | N:M | false |
| evidence_for ⭐ | MetricSnapshot/Event | DecisionRule | N:M | false |
| evidence_for_inverse ⭐ | DecisionRule | MetricSnapshot/Event | N:M | true |
| references ⭐ | KnowledgeBase | Object | N:M | true |
| addresses ⭐ | DecisionRule | Event | N:M | false |
| overridden_by ⭐ | DecisionRule | DecisionRule | N:M | true |
| writes_to | AgentTask | KnowledgeBase | 1:N | true |
| written_by ⭐ | KnowledgeBase | AgentTask/Creator | N:M | true |

⭐ = 本周新增或补充双向

### 3.3 关键 Link Type 设计动机（Week 1 新增部分）

#### monitors（Adapter→ScenicSpot/MetricSnapshot）
**动机：** 当前 OntologyAdapter.instances 只声明"产出类型"，不声明"监控范围"。monitors link 把 adapter 与景区/指标显式绑定：
```json
{
  "adapter-douyin" monitors [movie_town, only_henan, ..., qingming],
  "adapter-douyin" monitors [ms:douyin:movie_town:2026-06-24:search_index, ...]
}
```
**用途：** Cron 失败诊断 — adapter-douyin 连续失败 → 检查其 monitors 的 MetricSnapshot 是否漏采。

#### produces（Function→Object）
**动机：** 当前 Function 与输出 Object 之间无显式 link。Function 不存为独立 Object Type（无 schema），但 produces 关系让 Function 的输出可追溯：
```json
{
  "Function:calculateSearchTrend" produces [ms:douyin:movie_town:2026-06-24:search_index, ...]
}
```
**与 Palantir 对齐：** Palantir Functions 是 pipeline 中的可调用节点，produces 关系是函数签名 → 输出的对应。

#### evidence_for（Metric/Event→DecisionRule）
**动机：** 当前 based_on_metric 是 DecisionRule→Metric 的反向视角（"规则基于哪些指标"）。evidence_for 提供 Metric→DecisionRule 视角（"哪些指标支持这条规则"），支持：
- 规则验证：列出所有 evidence_for 链接的 metric
- 规则废弃：metrics 失事后自动建议规则降级
- 证据溯因：从 metric 反查所有支持的规则

#### addresses（DecisionRule→Event）
**动机：** 决策闭环关键 link。Event（问题/异动）→ DecisionRule（应对规则）→ AgentTask（执行动作）的 3 跳链路中，addresses 是第一步。
**用途：** 解决问题"竞品先动预警"链路中 Event 与 R-003 规则的对应关系不清问题。

#### references（KnowledgeBase→Object）
**动机：** Wiki ↔ Ontology 双向链接。当前 wiki markdown 中的 `[[objectId]]` 语法未被解析，文档与业务对象之间无结构化关联。
**Week 1 设计：** KnowledgeBase.path 字段 + references link 让 KB scanner 解析 markdown 链接自动生成 Ontology 引用。

---

## 四、ID Naming Convention（Week 1 新增）

### 4.1 设计动机

Week 6 发现问题：adapter-douyin.py 中 only_henan 和 only_dream 是同一景区（"只有河南·戏剧幻城"），但使用不同 ID，导致 scenic_spots 表出现重复记录。

### 4.2 命名规范

**通用规则：** `<scope>:<type>:<value>` 三段式，scope 统一为 `ss`/`ms`/`ca`/`ev`/`mc`/`dr`/`ts`/`rg`/`kb`/`cr`/`adapter`/`at`

| Object Type | ID 模式 | 示例 |
|-------------|---------|------|
| ScenicSpot | `ss:<lowercase_name>` | `ss:movie_town`, `ss:only_henan` |
| MetricSnapshot | `ms:<source>:<spot_id>:<date>:<metric_type>` | `ms:douyin:movie_town:2026-06-24:search_index` |
| ContentAsset | `ca:<source>:<external_id>` | `ca:xiaohongshu:65a1b2c3d4e5f` |
| Event | `ev:<type>:<date>:<seq>` | `ev:competitor_activity:2026-06-19:001` |
| MarketingCampaign | `mc:<name_slug>` | `mc:dragon_boat_2026` |
| DecisionRule | `dr:<rule_id>` | `dr:R-001` |
| TouristSegment | `ts:<name_slug>` | `ts:parent_family` |
| Region | `rg:<level>:<name_slug>` | `rg:city:zhengzhou`, `rg:district:zhongmu` |
| KnowledgeBase | `kb:<path_slug>` | `kb:tech:ontology:ontology_json` |
| Creator | `cr:<platform>:<author_id>` | `cr:xiaohongshu:5a8b9c0d` |
| OntologyAdapter | `adapter-<name>` | `adapter-douyin` |
| AgentTask | `at:<cron_job_id>` | `at:douyin_daily_1030` |

### 4.3 别名策略

**新规则：** 同一景区只能有 1 个 primary ID，alias 用 ScenicSpot.aliases 数组保留。

**示例：**
```json
{
  "id": "ss:only_henan",
  "name": "只有河南·戏剧幻城",
  "aliases": ["only_dream", "只有河南"],
  "shortName": "只有河南"
}
```

**查询层 alias 解析（Week 7 实施）：**
```python
def resolve_spot_id(spot_id_or_alias: str) -> str:
    """Returns primary ID, looking up aliases if needed"""
    # First try primary
    if spot := db.scenic_spots.get(spot_id_or_alias):
        return spot.id
    # Then try aliases
    for s in db.scenic_spots.find():
        if spot_id_or_alias in (s.aliases or []):
            return s.id
    return spot_id_or_alias  # unchanged if not found
```

---

## 五、Interfaces 完整定义（v1.2.0 = 7 个）

### 5.1 7 个 Interface 总览

| Interface | Object Types | 用途 | Week 加入 |
|-----------|--------------|------|----------|
| HasDailyMetric | ScenicSpot | 统一每日趋势查询 | v1.0 |
| HasContent | ScenicSpot, Campaign | 内容资产聚合查询 | v1.0 |
| DecisionSupport | DecisionRule, Event, AgentTask | 决策上下文拉取 | v1.0 |
| **HasRegionalContext** ⭐ | ScenicSpot, Event, TouristSegment, Creator | 区域维度查询 | **v1.2.0** |
| **TimeSeries** ⭐ | MetricSnapshot, Event, ContentAsset, AgentTask | 时序数据抽象 | **v1.2.0** |
| **HasAuditTrail** ⭐ | DecisionRule, AgentTask, Adapter, KB | 审计追溯 | **v1.2.0** |
| **HasPricing** ⭐ | ScenicSpot, MarketingCampaign | 价格维度查询 | **v1.2.0** |

### 5.2 关键 Interface 设计动机

#### TimeSeries（v1.2.0）
**动机：** 趋势查询"过去 7 天 MetricSnapshot"和"过去 7 天 Event"和"过去 7 天 ContentAsset"都涉及 7 天窗口，但当前查询层要写 3 个不同的 SQL。

**设计：** TimeSeries 接口定义 requiredProperties: `id + (collectedAt|occurredAt|publishDate|lastRunAt)` 任一时间字段，查询层 UNION 抽象为统一 `query_recent(7d, types=[MetricSnapshot, Event, ContentAsset])` 方法。

#### HasAuditTrail（v1.2.0）
**动机：** DecisionRule 状态变更、AgentTask 失败、Adapter 异常、KnowledgeBase 更新都需要审计。SQLite 中已有 ingest_log + action_log + query_log 三表，HasAuditTrail interface 把这三表统一暴露给所有需要审计的对象。

**Week 2+ 实现：** `ontology_query.py::audit_trail(object_id) -> List[AuditEvent]` 跨表查询。

---

## 六、Validation Rules 框架（v1.2.0 = 6 条）

### 6.1 6 条规则

| ID | 名称 | 实施位置 | 优先级 |
|----|------|---------|--------|
| **V-001** | ID 必须遵循 idNamingConvention | scripts/ontology/validate.py | P0 |
| **V-002** | Link Type 实例化时检查 cardinality | ontology_store.py::validate_link_cardinality() | P0 |
| **V-003** | Inverse link 双向一致 (aggregated_from ↔ contributes_to) | ontology_store.py::validate_inverse_links() | P0 |
| **V-004** | ScenicSpot 的 located_in 必须指向 Region 对象 | ontology_store.py::validate_region_link() | P1 |
| **V-005** | confidence 字段值必须在 [0, 1] 区间 | ontology_store.py::validate_confidence_range() | P1 |
| **V-006** | DecisionRule.status == 'verified' 必须有 triggerCount > 0 | ontology_store.py::validate_verified_rule() | P2 |

### 6.2 验证层架构（Week 2+ 实施）

```
validate_ontology.py (CLI)
├── load_schema(ontology.json)
├── for each object in db:
│   ├── validate_id_format(obj.id)              # V-001
│   ├── validate_required_properties(obj)       # (未来 V-007)
│   ├── for each link in obj.links:
│   │   ├── validate_cardinality(link)          # V-002
│   │   ├── validate_inverse_consistency(link)  # V-003
│   │   └── validate_link_target_exists(link)   # V-004
│   └── validate_value_ranges(obj)              # V-005/V-006
└── return List[ValidationError]
```

### 6.3 与 Adapter 集成（Week 7 实施）

adapter 写入 SQLite 之前调用 `validate.py`：
- V-001 失败 → 警告 + 自动修复（添加 alias）
- V-002/V-003 失败 → 拒绝写入，返回错误给 cron
- V-004/V-005/V-006 失败 → 警告但允许写入（业务问题，不阻断采集）

---

## 七、对标 Palantir Ontology 的设计映射

| Palantir 组件 | 我们的实现 | v1.2.0 增强 |
|---------------|----------|-------------|
| Object Types | 12 个（含 4 个 Week 1 新增） | +TouristSegment/Region/KnowledgeBase/Creator |
| Properties | 每个 OT 6-12 个属性 | ScenicSpot +7 tourism 属性，MetricSnapshot +4 异常检测属性 |
| Link Types | 33 个（M:N/N:1/1:N 全覆盖） | Week 1 新增 8 个 + 补 11 个 reverse-edge |
| Action Types | 5 个 | （Week 2 深化） |
| Functions | 7 个 | （Week 2 深化） |
| Interfaces | 7 个 | Week 1 新增 4 个 |
| Object Set Queries | ontology_query.py 8 个预定义查询 | （Week 2 深化 + LLM Query Translator） |
| Action Type Governance | governance 字段 | （Week 3 数据接入深化） |
| OSDK 代码生成 | 暂未实现（待 Phase 2 后） | （Week 4 评估） |

---

## 八、Tourism Ontology 设计模式应用

### 8.1 TOIR（Tourism Ontology for Information Retrieval）参考

TOIR 启发我们增加的 ScenicSpot 属性（v1.2.0）：
| TOIR 属性 | 我们的实现 | 数据源 |
|----------|----------|--------|
| peak_season | peakSeasonMonths | 历年客流 CSV + 节假日基准.md |
| typical_visit_duration | typicalVisitDuration | 行业报告 + 用户调研 |
| ticket_price | ticketPriceRange | 票务系统 |
| target_age | targetAgeGroups | 抖音人群画像 |

### 8.2 Dublin Core 参考

Dublin Core Terms（DCMI）启发 ContentAsset / Event 的元数据：
| DCMI 元素 | 我们的映射 |
|----------|----------|
| dcterms:title | ContentAsset.title / Event.title |
| dcterms:date | ContentAsset.publishDate / Event.occurredAt |
| dcterms:creator | ContentAsset.authorName → Creator 引用 |
| dcterms:source | ContentAsset.source (platform enum) |
| dcterms:type | ContentAsset.type (video/note/post) |

### 8.3 AgentO（Agentic AI Ontology）核心类映射

参考 AgentO 的 14 个核心类（[GitHub](https://github.com/agentic-patterns/agentic-ai-onto)），我们的实现覆盖度：

| AgentO 类 | 我们的映射 | 状态 |
|----------|----------|------|
| Agent | IDENTITY.md (李涯) | ✅ 已有 |
| Task | AgentTask | ✅ v1.0 |
| Goal | customer: 153万 + 1.2亿 | ✅ 已有（MEMORY.md） |
| Capability | Functions | ✅ v1.0 |
| Constraint | DecisionRule[] + AuthorityHierarchy | ✅ v1.0 |
| KnowledgeBase | KnowledgeBase ⭐ | ✅ **v1.2.0** |
| Memory | MEMORY.md + memory/*.md | ✅ 已有 |
| Tool | Actions | ✅ v1.0 |
| WorkflowPattern | cron 调度配置 | ✅ 已有 |
| Environment | macOS + CDP 浏览器 | ✅ 已有 |
| Resource | （未单独建模）| ⚠️ Week 5+ 评估 |
| Team | （单 Agent 无需）| N/A |
| WorkflowStep | AgentTask.consecutiveErrors 等元数据 | ✅ v1.0 |
| Outcome | Event / MetricSnapshot | ✅ v1.0 |

**覆盖率：12/14 (86%)**，缺失 Resource（多 Agent 协作时引入）。

---

## 九、JSON-LD @context 未来扩展性

### 9.1 当前状态（D-001 决策）

ontology.json 当前是 **纯 JSON Schema**，不引入 OWL/RDF（基础设施评估 §2.4 决策）。

### 9.2 JSON-LD 轻量引入方案（Week 4+ 评估）

如需跨系统互操作（如对接外部 API），可添加 @context 字段使对象可被标准工具理解：

```json
{
  "@context": {
    "ontology": "https://movietown.cn/ontology/v1.2.0#",
    "xsd": "http://www.w3.org/2001/XMLSchema#"
  },
  "@type": "ontology:MetricSnapshot",
  "ontology:scenicSpotId": { "@id": "ontology:ScenicSpot/ss:movie_town" },
  "ontology:value": { "@value": 876543, "@type": "xsd:integer" }
}
```

**当前结论：** 不引入。理由同基础设施评估 D-001。

---

## 十、关键设计决策（Week 1 新增 5 条）

### D-011：建立 ID Naming Convention 解决 Week 6 双 ID 问题
**决策：** 引入 `<scope>:<type>:<value>` 三段式 ID 命名 + 别名机制。
**理由：**
1. Week 6 发现的 only_henan/only_dream 双 ID 问题必须根治
2. 三段式 ID 自带 type 信息，避免命名冲突（如 ev: 与 mc: 不会撞）
3. aliases 数组保留历史 ID，查询层透明映射
**触发条件：** Week 7 adapter 改造时统一应用。

### D-012：Cardinality Matrix 显式声明
**决策：** 所有 33 个 Link Types 必须显式声明 cardinality（M:N/N:1/1:N/N:M）。
**理由：**
1. Week 6 双向引用歧义（aggregated_from ↔ contributes_to）需要 cardinality 标注
2. SQLite schema 设计时需要明确 UNIQUE/PRIMARY KEY 约束
3. 未来 GraphQL API 自动生成时需要 cardinality
**实施：** ontology.json §cardinalityMatrix；Week 2+ ontology_store.py::validate_link_cardinality() 校验。

### D-013：KnowledgeBase 作为 wiki 目录结构化索引
**决策：** KnowledgeBase Object Type 索引 wiki/ 目录树，references link 反向引用业务对象。
**理由：**
1. 当前 wiki markdown 是隐式知识图谱，文档间无结构化关联
2. `[[objectId]]` 语法未被解析，文档与 Ontology 无双向链接
3. KB scanner 解析 markdown 自动生成 references link，零人工成本
**触发实施：** Phase 1 之后（Week 5+）。

### D-014：Inverse Link 显式声明
**决策：** 双向引用关系（如 aggregated_from ↔ contributes_to）必须显式声明 inverseLink 字段。
**理由：**
1. 双向引用必须双向一致，否则审计和溯因困难
2. V-003 validation rule 强制 inverse 一致性
3. 未来 GraphQL 自动生成时 inverse 是必要 metadata
**实施：** ontology.json §cardinalityMatrix.definitions[*].inverseLink。

### D-015：Validation Rules 作为 Adapter 写入前 gate
**决策：** 所有 adapter 写入 SQLite 之前必须通过 V-001/V-002/V-003 校验。
**理由：**
1. P0 校验失败 = 阻断采集（ID 格式/双向一致）
2. P1 校验失败 = 警告但允许（业务问题不阻断）
3. 校验逻辑集中在 scripts/ontology/validate.py，adapter 不重复实现
**触发实施：** Week 7 adapter 改造。

---

## 十一、Week 1 发现的问题

| # | 问题 | 优先级 | 建议解决时机 |
|---|------|--------|------------|
| 1 | **only_henan/only_dream 双 ID 需 alias 迁移** | 🔴 高 | Week 7 adapter 改造 + db migration 002 |
| 2 | **KnowledgeBase scanner 未实现**（KB 节点全空） | 🟡 中 | Phase 1 后（Week 5+） |
| 3 | **Creator 节点全空**（爬虫未升级） | 🟡 中 | xiaohongshu_crawl.py 升级后（Phase 2） |
| 4 | **Validation rules 全部"待实现"** | 🔴 高 | Week 2 实施 ontology_validate.py |
| 5 | **ScenicSpot.aliases 字段未迁移现有 13 个景区** | 🟡 中 | Week 7 migration 002 |
| 6 | **Region 嵌套层级只在 6 个种子**（应有完整省/市/区树） | 🟢 低 | Week 5+ 引入行政区划数据 |
| 7 | **MetricSnapshot.baselineValue/dailyVolatility 未填值** | 🟡 中 | Week 2 Function: calculateBaselineValue() |

---

## 十二、下一步（Week 2+ 计划）

### Week 2：Actions & Functions 标准化方案
- [ ] 实施 `scripts/ontology/validate.py`（V-001 ~ V-006）
- [ ] Function: `calculateBaselineValue()` 写入 MetricSnapshot.baselineValue
- [ ] Function: `detectAnomaly()` 写入 MetricSnapshot.isAnomaly
- [ ] Action: `SendFeishuCard` 增加 ontology_query 上下文注入
- [ ] adapter 改造调用 validate.py

### Week 3：数据接入管道设计（采集→映射→存储）
- [ ] adapter 改造按 D-008/D-011/D-015 实施
- [ ] db migration 002：scenic_spots 加 aliases/province/city 列
- [ ] metric_snapshots 加 baselineValue/dailyVolatility/isAnomaly/tags 列
- [ ] KnowledgeBase scanner 原型

### Week 4：AI Agent × Ontology 集成（含 LLM Query Translator）
- [ ] 自然语言 → ontology_query 方法映射
- [ ] Agent system prompt 注入 ontology 上下文
- [ ] 反向：Agent 决策 → ontology 写回

### Week 5：基础设施深度评估
- [ ] Resource Object Type 评估（多 Agent 协作）
- [ ] JSON-LD @context 二次评估
- [ ] Region 完整层级数据接入

### Week 6：原型 v2（含 KB scanner）
- [ ] KnowledgeBase scanner 完整实施
- [ ] Creator 实例填充（待爬虫升级）
- [ ] inverse link 自动同步机制

---

## 十三、关键收获

1. **Schema 演进必须有版本号 + 验证规则** — v1.1.4 → v1.2.0 跨 19 天多次修改无验证，Cardinality/ID 一致性需 validate.py 自动检查
2. **Inverse Link 必须显式声明** — Week 6 双向引用歧义是重大教训
3. **Tourism Ontology 属性不必一次到位** — peakSeasonMonths 等可后续通过 Function 派生，无需初始 schema 覆盖
4. **ID Naming Convention 是基础设施** — 没规范 = 多源数据无法合并
5. **KnowledgeBase 反向引用是 wiki 升级关键** — 让 markdown 成为 Ontology 的客户端而非独立系统

---

## 十四、参考资源

- [Palantir Foundry Ontology 文档](https://www.palantir.com/docs/foundry/ontology/overview/)
- [AgentO (Agentic AI Ontology)](https://github.com/agentic-patterns/agentic-ai-onto)
- [JSON-LD 1.1 规范](https://www.w3.org/TR/json-ld11/)
- [TOIR (Tourism Ontology for Information Retrieval)](https://link.springer.com/chapter/10.1007/11590019_4)
- [Dublin Core Metadata Terms](https://www.dublincore.org/specifications/dublin-core/dcmi-terms/)
- [《哥谭神话-工程篇》02.Palantir的Ontology层](https://blog.csdn.net/hyde_jiang/article/details/159885417)
- [《Palantir Ontology 技术深度解析》](https://blog.csdn.net/hrZUVu/article/details/150510328)

---

_本文档由 Ontology架构研究_每周深化 cron 生成（Week 1 Object Types + Link Types 设计）_
_下次更新：Week 2 Actions & Functions 标准化_
