# Graphiti 本地时序知识图谱（2026-08-19 落地）

## 为什么装

站长要求评估 GitHub 5 个项目（AutoResearch/RAGFlow/Unsloth/Milvus/Graphiti）哪个对本地提升最大。
结论：**Graphiti 唯一闭环可行**（其余 4 个：AutoResearch 需 GPU、RAGFlow 太重 16G 撑不住、Unsloth 仅 NVIDIA、Milvus 与 chromadb 重复）。

## 架构（零 OpenAI 依赖）

```
┌─────────────┐    ┌──────────────┐    ┌──────────────────┐
│ DeepSeek LLM │    │ Ollama bge-m3│    │ FalkorDB (Docker)│
│ (实体/关系抽取)│    │ (embedding)  │    │ (时序图存储)      │
└──────┬──────┘    └──────┬───────┘    └────────┬─────────┘
       └──────────────────┴────────────────────┘
                graphiti-core 0.29.3 (Python)
```

- **LLM**: DeepSeek `deepseek-v4-flash`（`json_object` 模式，不支持 json_schema）
- **Embedding**: Ollama `bge-m3`（1024 维，本地免费）
- **Reranker**: stub 跳过（避免下载 2G 模型；后续可升级 bge-reranker-v2-m3）
- **存储**: FalkorDB（轻量图库，~200MB 内存，比 Neo4j 省）

## 关键文件

| 文件 | 说明 |
|------|------|
| `graphiti_local.py` | 主脚本（init/add/search/test 四种模式） |
| `start_graphiti.sh` | 一键启动（幂等） |
| venv | `/tmp/graphiti-venv`（graphiti-core 0.29.3） |

## 使用

```bash
# 初始化索引
DEEPSEEK_API_KEY=xxx python graphiti_local.py init

# 写入一条业务事实
DEEPSEEK_API_KEY=xxx python graphiti_local.py add '郑州电影小镇8月16日客流9036人'

# 语义搜索
DEEPSEEK_API_KEY=xxx python graphiti_local.py search '电影小镇客流'

# 冒烟测试
DEEPSEEK_API_KEY=xxx python graphiti_local.py test
```

## 踩坑记录（重要！）

### 1. 🐛 macOS 系统代理劫持本地请求（根因）
- **症状**: httpx/requests/urllib/OpenAI SDK 请求 `localhost:11434` 全部 502；curl/nc 正常
- **根因**: macOS 系统代理 `127.0.0.1:7897`（抓站代理）被 HTTP 客户端自动读取，本地请求被代理劫持返回 502
- **排查路径**: 试遍 content-type/UA/HTTP版本/IPv6/keep-alive → 最后 `proxies={'http':None}` 立刻 200
- **修复**: `httpx.AsyncClient(trust_env=False)` 禁用系统代理
- **经验**: 本机任何 Python HTTP 客户端连 localhost 都要显式禁用代理！

### 2. Ollama 0.32.9 OpenAI 兼容层
- `/v1/embeddings` 批量请求偶发 502（encoding_format=base64 等参数不兼容）
- **解法**: 直接用原生 `/api/embed`（绕开兼容层）

### 3. graphiti-core 0.29.3 API 变化
- `add_episode(content=)` → `add_episode(episode_body=, source_description=, reference_time=)`
- `search(limit=)` → `search(query, group_ids=)`（用 config 控制数量）
- `StructuredOutputMode` 是 Literal 不是 Enum → 传 `'json_object'`

### 4. group_id 即数据库名
- `group_id='movie-town'` 会把数据写到名为 `movie-town` 的 FalkorDB graph，不是默认 `graphiti`
- 查询要对应 group_id，否则搜不到

## Reranker（8/19 已实现）

- **OllamaReranker**：复用 bge-m3 embedding 做 query-passage 余弦重排，零新模型/零内存压力
- 效果验证：查询「郑州电影小镇客流」→ 客流相关边排第 1（之前万圣节总排第 1）
- 局限：embedding 重排不是真 cross-encoder，年度目标类查询排序仍一般；未来可升级 bge-reranker-v2-m3（2GB）或 Ollama 新版本原生 /api/rerank

## Ontology 打通（8/19 已完成）

**方向**: Ontology (SQLite, 静态业务图谱) → Graphiti (FalkorDB, 动态时序图谱)

- `sync_ontology.py`: 读取 Ontology 生产库（`.profile/ontology/ontology_store.db`）的景区/关系/指标，
  写成关系型 episode 灌入 Graphiti
- 效果验证: 查询「行业对标对象」→ 返回完整竞品清单（大唐不夜城/只有河南/清明上河园/万岁山等）
- ⚠️ `--metrics` 模式数据量大（30 天×景区），16GB 机器可能超时/卡死，默认不带
- 反向（Graphiti → Ontology）暂未实现，待需求明确（如把时序洞察写回 events 表）

## 后续优化

- [x] **FalkorDB 持久化**（8/19）：volume 挂载到 `/var/lib/falkordb/data`（不是 `/data`！软链目录挂载不持久化）
- [x] **客流数据接入验证**（8/19）：写入/检索全链路 OK
- [ ] **reranker 升级**：当前 stub 跳过了 rerank，导致混合检索排序不精准（万圣节边总是排最前）。
      可升级 bge-reranker-v2-m3（sentence-transformers，~2GB）或等 Ollama 新版本原生 /api/rerank
- [ ] 与自研 Ontology（.profile/ontology）打通：Graphiti 做动态时序事实，Ontology 做静态业务图谱

## ⚠️ Graphiti 能力边界（8/19 实测）

Graphiti 抽取的是**实体间关系**（RELATES_TO 边，可语义检索）：
- ✅ 关系型叙事：`星光铁花秀是客流增长驱动因素`、`小镇举办万圣节活动` → 产生可检索的语义边
- ❌ 单实体数值：`8月15日客流10327人` → 只产生 MENTIONS 边，**检索不到**（数值型数据不适合，继续走 Excel/CSV 分析）
- ❌ 重复实体：多个 episode 讲同一实体集（如都讲郑州电影小镇客流），不会新增 RELATES_TO 边

**结论**：Graphiti 适合存“关系型洞察”（活动→客流影响、竞品关联、策略结论），不适合存逐日数值日报。
`sync_flow.py` 已改为“周洞察模式”写入关系型事实。
