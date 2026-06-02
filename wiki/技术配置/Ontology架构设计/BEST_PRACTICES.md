# Ontology 架构设计 · 最佳实践参考

> 从 Palantir OSDK、JSON-LD、Knowledge Graph 等领域研究中提炼
> 最后更新: 2026-05-31

---

## 实践 1：Adapter as Generated Code（对标 Palantir OSDK）

**来源：** [Palantir Ontology SDK 文档](https://www.palantir.com/docs/foundry/ontology-sdk/overview/)

**核心思想：**
Palantir OSDK 为每个 Ontology Object Type 自动生成类型安全的代码绑定（Python/TypeScript/Java）。
我们的 adapter 模式与此对齐：每个数据源对应一个专用 adapter，负责将原始数据转换为类型安全的 Ontology 对象。

**映射关系：**
| Palantir OSDK | 我们的实现 |
|:---|:---|
| Object Type 生成代码 | adapter 生成 MetricSnapshot/ContentAsset |
| `loadSingleRestaurant(pk)` | `build_metric_object(scenic_spot_id, ...)` |
| Type-safe properties | ontology.json 中定义的 property types |
| Paginated queries | 按日期分文件存储（metric_snapshots_{date}.json） |
| Granular governance | confidence 字段 + audit log |

**启示：**
- ✅ 每个 adapter 应使用 ontology.json 中的 property names 作为字段名
- ✅ 未来可考虑从 ontology.json 自动生成 Python dataclass（类似 OSDK 代码生成）
- ⚠️ 当前 SCENIC_SPOT_MAP 在两个 adapter 中重复，应提取为共享模块

---

## 实践 2：JSON Schema 优于 OWL/RDF（轻量级操作型本体）

**来源：** [JSON-LD 规范](https://json-ld.org/) & 实际工程经验

**核心思想：**
对于运营决策系统这类操作型本体（Operational Ontology），不需要完整的 OWL/RDF 语义层。
JSON Schema + 显式 linkTypes 足以满足 80% 的查询/推理需求，且开发效率提升 3-5x。

**对比：**
| 维度 | OWL/RDF | JSON Schema (我们的选择) |
|:---|:---|:---|
| 语义表达能力 | 完整（subClassOf, equivalentClass, etc） | 基础（ObjectType + property types） |
| 开发成本 | 高（需 Protege/RDFlib/SPARQL） | 低（任何语言都能读） |
| 团队学习曲线 | 陡峭 | 平缓 |
| 查询效率 | 需 SPARQL 引擎 | 原生 JSON 遍历/过滤 |
| 适用场景 | 学术研究/企业知识图谱 | 运营决策/数据管道 |

**启示：**
- ✅ 当前 ontology.json 的 property types + linkTypes 设计已充分
- 🔮 如需跨系统互操作，future step 是添加 JSON-LD `@context` 支持（非当前阶段必需）
- ⚠️ 不要过早引入 RDF/OWL 复杂性

---

## 实践 3：渐进式数据丰富（Incremental Metadata Enrichment）

**来源：** Palantir OSDK 的设计哲学 & 实际 adapter 开发经验

**核心思想：**
Ontology 不是一次性设计好的，而是随着数据源的接入逐步丰富。
每个 adapter 不仅转换数据，还应该为数据附加元数据（置信度、来源、采集时间）。

**我们在 ontology.json 中的体现：**
```json
"MetricSnapshot": {
  "confidence": { "type": "number", "description": "数据置信度 0-1" },
  "collectedAt": { "type": "datetime" }
}
```

**置信度分层策略（adapter 实现中）：**
| 数据源 | 默认置信度 | 理由 |
|:---|:---|:---|
| 抖音指数（douyin） | 0.9 | 官方 API，精确数值 |
| 小红书（xiaohongshu） | 0.3-0.7 | 爬虫提取，content_length 估算 |
| 百度指数（future） | 0.6 | 第三方估算 |
| 内部客流 CSV | 0.95 | 票务系统，精确计数 |

**启示：**
- ✅ 当前 adapter 已实现 confidence 分层
- 🔮 未来可在查询时按 confidence 加权聚合
- 🔮 ContentAsset（小红书笔记详情）需等爬虫升级后启用

---

## 实践 4：本体驱动决策闭环（Ontology → Decision Rules → Actions）

**来源：** Palantir Foundry Ontology + Actions 模式

**核心思想：**
Ontology 的终极价值不在存储，而在驱动决策。
Palantir 的 Actions 层允许基于 Ontology 对象触发操作（发送通知、更新数据、启动工作流）。

**我们的映射（已内置于 ontology.json）：**
```
MetricSnapshot → DecisionRule.evaluate() → Action.SendFeishuCard
ContentAsset → DecisionRule.evaluate() → Action.UpdateWiki
Event → DecisionRule.evaluate() → Action.CreateAlert
```

**当前规则验证状态：**
| Rule ID | 名称 | 状态 | 验证次数 |
|:---|:---|:---|:---|
| R-001 | 内容真空窗口 | verified ✅ | 持续验证中 |
| R-002 | 双节点浪费 | verified ✅ | 2次 |
| R-003 | 竞品先动预警 | hypothesis 🔬 | 待验证 |
| R-004 | 模型晚高峰规避 | verified ✅ | 连续观察 |

**启示：**
- ✅ 当前 4 条规则已覆盖核心运营场景
- 🔮 每季度应 review 规则状态，升级 hypothesis → verified
- 🔮 未来可添加自动触发阈值（当前为人工判断）

---

## 实践 5：共享常量提取（Centralized Ontology Constants）

**来源：** adapter 开发实践发现

**核心思想：**
SCENIC_SPOT_MAP 在多 adapter 中重复，应抽取为共享模块，避免分散维护。

**当前问题：**
- `adapter-douyin.py` 和 `adapter-xiaohongshu.py` 各自维护 SCENIC_SPOT_MAP
- 新增景区需同时更新两个文件

**建议方案（后续迭代）：**
```python
# scripts/ontology_constants.py
SCENIC_SPOT_MAP = { ... }
CONFIDENCE_BY_SOURCE = { "douyin": 0.9, "xiaohongshu": 0.7 }
```

**启示：**
- 🏗️ 下次 adapter 开发（adapter-visitors.py / adapter-baidu.py）时应先创建共享常量模块
- ✅ 当前 2 个 adapter 重复量尚可接受，暂不重构

---

## 实践 6：双向映射模式（Bidirectional Object Mapping）

**来源：** AgentO (Agentic AI Ontology) 的关系建模 & Palantir OSDK ObjectSet

**核心思想：**
当两个 Ontology Object 之间存在因果关系时（一个聚合自多个），应同时在两个方向上建立引用：
- **正向引用** (MetricSnapshot → ContentAsset[]): 记录快照由哪些内容资产聚合生成
- **反向引用** (ContentAsset → MetricSnapshot): 记录单个内容资产贡献了哪个快照

**AgentO 的启发：**
```
Team → hasAgentMember → Agent
Agent → hasTask → Task
Task → hasAssociatedTask → WorkflowStep (反向)
```
AgentO 中的每条关系都是双向可遍历的，这对审计和溯因至关重要。

**我们的实现（adapter-xiaohongshu.py 中）：**
```python
# 正向：MetricSnapshot.metadata.content_asset_ids = ["xhs::movie_town::2026-05-31::note_0", ...]
# 反向：ContentAsset.derivedFromMetricSnapshotId = "movie_town::2026-05-31::content_count::xhs"
```

**设计原则：**
- ✅ 每条 Link 都应有明确的 sourceTypes → targetTypes 方向
- ✅ 聚合关系 (N:1) 需 2 条 Link：正向聚合 + 反向贡献
- ✅ 双向引用使查询无需全表扫描
- ⚠️ 维护成本增加：更新内容时需同步两侧

**在 ontology.json 中的体现：**
```json
{
  "aggregated_from": { "sourceTypes": ["MetricSnapshot"], "targetTypes": ["ContentAsset"] },
  "contributes_to": { "sourceTypes": ["ContentAsset"], "targetTypes": ["MetricSnapshot"] }
}
```

---

## 实践 7：操作型本体 vs 知识型本体（Operational vs Knowledge Ontology）

**来源：** [Agentic AI Ontology (AgentO)](https://github.com/agentic-patterns/agentic-ai-onto) & Lior Limonad 的 Agent Design 文章

**核心思想：**
现代 AI Agent 的本体设计有两类：
- **知识型本体** (Knowledge Ontology): OWL/RDF，用于学术研究、跨系统互操作
- **操作型本体** (Operational Ontology): 轻量级 JSON Schema，驱动实际决策和动作

**AgentO 的 14 个核心类：**
| 类 | 说明 | 我们的映射 |
|:---|:---|:---|
| Agent | AI 智能体 | IDENTITY.md (李涯) |
| Task | 具体任务 | AgentTask (cron jobs) |
| Goal | 目标 | customer: 153万客流目标 |
| Capability | 能力 | Functions (calculateSearchTrend, etc) |
| Constraint | 约束 | DecisionRule[] + AuthorityHierarchy |
| KnowledgeBase | 知识库 | wiki/ 目录体系 |
| Memory | 记忆 | MEMORY.md + memory/*.md |
| Tool | 工具 | Actions (SendFeishuCard, etc) |
| WorkflowPattern | 工作流模板 | cron 调度配置 |
| Environment | 运行环境 | macOS + CDP 浏览器 |

**启示：**
- ✅ 我们已有 10/14 核心类映射，操作型本体设计充分
- 🔮 AgentO 的 `Resource` 和 `Team` 类可作为未来多 Agent 协作的参考
- ⚠️ 不要追求知识型本体的完整性——操作型本体够用即可

---

## 实践 8：查询层与共享常量 — 关注点分离（Concern Separation）

**来源：** Day 4 重构实践（2026-06-02）

**核心思想：**
Ontology 系统应严格分层，每层职责单一：
```
数据采集层 (crawler)
    ↓
适配层 (adapter-*.py) — 原始数据 → Ontology Object
    ↓
存储层 (ontology_store.py) — SQLite CRUD
    ↓
查询层 (ontology_query.py) — 预定义查询 + 格式化输出
    ↓
应用层 (日报/飞书/Canvas) — 消费查询结果
```

**分层要点：**
- `ontology_constants.py`: **单一事实来源**，所有 adapter 和 query 统一引用，消除 SCENIC_SPOT_MAP 多头维护
- `ontology_query.py`: 封装 `JOIN + GROUP BY + ORDER BY` 等重复 SQL 模式，应用层不直接写 SQL
- adapter 只负责转换，不负责查询；query 只负责查询，不负责写入

**为什么分层：**
- 修改 SPOT_MAP 加景区：只改 `ontology_constants.py` 一处
- 日报需要新统计维度：只改 `ontology_query.py`，不影响 adapter
- 换存储引擎（SQLite→PostgreSQL）：只影响 `ontology_store.py`，query 层通过 store 接口访问

**启示：**
- ✅ Day 4 已验证：adapter-{douyin,xiaohongshu,visitors}.py 全部改用 `from ontology_constants import ...`
- 🔮 未来可考虑：`ontology_query.py` 的 `daily_overview()` 方法直接替代日报中硬编码的查询逻辑

---

## 总结

这 8 条实践从 Palantir OSDK 文档、AgentO 语义模型、JSON-LD 规范和实际开发中发现提炼而来。核心原则：
1. **轻量优于完整**：JSON Schema 而非 OWL，操作型本体够用就好
2. **适配器模式**：每个数据源独立 adapter，对标 Palantir OSDK
3. **渐进式丰富**：本体随数据接入逐步生长
4. **决策驱动**：本体终极目标是触发 Actions，而非纯存储
5. **共享优于重复**：常量尽早提取，避免分散维护
6. **双向映射**：聚合关系建立正反两个方向的引用，支持高效溯因
7. **操作型定位**：对标 AgentO 的 10 个核心类，不追求知识型本体的完整性
8. **关注点分离**：adapter → store → query 三层，每层职责单一、互不越界

_文档维护：Ontology架构研究 每周深化任务
