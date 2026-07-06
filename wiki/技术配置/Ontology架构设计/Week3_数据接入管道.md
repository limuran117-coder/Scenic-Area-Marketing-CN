# Week 3 · 数据接入管道设计（采集→映射→存储→治理→可观测）

> 日期：2026-07-06 (周一) | 周期：**Week 3**（继 Week 1 Object/Link Types + Week 2 Actions/Functions 之后）
> 状态：**🔵 设计阶段**（document 落稿 + ontology.json v1.4.0 升级完成；脚本骨架下周一启动）
> 任务来源：实现路线图.md §二 Phase 2（Week 7 启动 — **已提前到 Week 3**）
> 上一周：Week 2 (2026-06-29) Actions & Functions 标准化
> 下一周：Week 4 (2026-07-13) AI Agent × Ontology 集成方案（含 LLM Query Translator）

---

## 一、本周定位 — 为什么是「数据接入管道」而不是继续「设计」？

### 1.1 现状盘点（截至 2026-07-06）

| 层 | 状态 | 落地物 |
|----|------|--------|
| Object Types | ✅ | ontology.json 12 OT（v1.2.0+）|
| Link Types | ✅ | ontology.json 33 LT |
| Functions | ✅ | 11 个 Function（4 类型分类） |
| Actions | ✅ | 7 个 Action（5 层治理设计） |
| 原型 SQLite | ✅ | `.profile/ontology/ontology_store.db` 163 objects |
| **Adapter** | ⚠️ 半成品 | 3 个 adapter（douyin/xhs/visitors）各做 transform，但**没有统一 governance** |
| **Ingest 可观测性** | ❌ 缺 | 缺端到端追踪、缺 dedup、缺失败告警升级 |
| **Action 治理实施** | ❌ 缺 | scripts/actions/ 目录**不存在**；5 层治理仅停在设计 |
| **Validation 实施** | ❌ 缺 | scripts/ontology/validate.py **不存在**；10 条规则无运行代码 |
| **db migration 002** | ❌ 缺 | 派生列（baselineValue/dailyVolatility/isAnomaly/tags）无 schema |

### 1.2 Week 3 必须解决的 4 个真问题

```
问题 1：3 个 adapter 各自为政
  - douyin adapter 写 /tmp 快照，xiaohongshu 写 data/ 目录，visitors 直接写 db
  - 字段映射散落各 adapter，重复实现 SCENIC_SPOT_MAP
  - 失败时无人知道，得手动 grep

问题 2：「采集→映射→存储」中间断裂
  - douyin_index.py → /tmp/crawl_data.json → adapter-douyin.py → ???
  - 没有「一个完整 pipeline run 的入口」；adapter 调一次 ingest_objects 就完事
  - 想看「昨天抖音采了多少条 / 失败几条 / 跳过几条」得自己拼 log

问题 3：Function/Action 设计有了，没实施
  - calculateBaselineValue / detectAnomaly 4 个 Function 没真实运行
  - Action 5 层治理写不出来，因为 scripts/actions/ 目录空
  - "Function-backed column" 在 db 层不存在（baselineValue 字段未加）

问题 4：Phase 3 已计划但 Phase 2 的基础设施不到位
  - 实现路线图 Phase 2（Week 7 启动）写的是 "adapter 改造 + db migration 002 + validate.py"
  - 但不先建 pipeline 框架，Phase 2 任务没法原子化推进
```

### 1.3 Week 3 的核心交付

| 交付 | 类型 | 大小估算 |
|------|------|---------|
| **adapterGovernance** section | ontology.json 设计 | 1.5KB |
| **pipelinePattern** section | ontology.json 设计 | 2KB |
| **ingestObservability** section | ontology.json 设计 | 1.5KB |
| **5 个 Pipeline Function** | ontology.json Function 定义 | 1KB |
| **5 条 Design Decision** | ontology.json D-021~D-025 | 2KB |
| **5 条 Validation Rule** | ontology.json V-011~V-015 | 2KB |
| Week3_数据接入管道.md（本文档） | 设计文档 | ~28KB |
| ontology.json v1.3.0 → v1.4.0 | JSON 升级 | +10KB |

**Week 4 才动手实施**：scripts/ontology/pipeline.py（orchestrator）、scripts/actions/wrapper.py（Action wrapper）、scripts/ontology/validate.py（V-001~V-015 全量）

---

## 二、Week 3 核心架构 — Pipeline as a First-Class Concept

### 2.1 设计哲学

> **数据接入不是「adapter 调一次 store」，而是「一个完整 pipeline run 的可观测生命周期」**。
>
> 对标 Palantir Foundry 的 **Data Connection Sync** 概念：
> - 一个 sync 包含 source → extract → transform → load → audit 5 阶段
> - 每个阶段有 status / duration / records / errors
> - 任何阶段失败都有 retry 策略 + 告警
> - 全链路有 runId 串联，可通过 runId 看到完整 trace

### 2.2 Pipeline 5 阶段（**新概念**）

```
┌─────────────────────────────────────────────────────────────────┐
│                Ontology Ingest Pipeline (Week 3 新概念)          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Stage 1: EXTRACT       Stage 2: TRANSFORM   Stage 3: LOAD     │
│  ┌──────────┐          ┌──────────┐         ┌──────────┐        │
│  │ 采集原始  │  ──→     │ 映射到    │  ──→    │ 写入      │       │
│  │ 数据      │          │ Ontology │         │ Ontology │        │
│  │          │          │ Object   │         │ Layer    │        │
│  └──────────┘          └──────────┘         └──────────┘        │
│   douyin_index.py       adapter-douyin      ingest_objects()    │
│   xhs_crawl.py          adapter-xhs         SQLite + JSON       │
│   visitor CSV           adapter-visitors    snapshot            │
│   baidu_search          adapter-baidu                            │
│                                                                  │
│  Stage 4: VALIDATE      Stage 5: AUDIT                            │
│  ┌──────────┐          ┌──────────┐                              │
│  │ V-001~015 │  ──→    │ 写入      │                              │
│  │ 规则验证   │         │ ingest_log│                              │
│  │          │          │ + alert   │                              │
│  └──────────┘          └──────────┘                              │
│   validate.py            pipeline_run_log                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
              runId 串联 5 阶段（pipeline_runs 表）
              失败可重试（按 stage 分别 retry）
              告警按 failureAlert.cooldownMs 分级
```

### 2.3 Pipeline Run 实体（核心新概念）

每个 pipeline run（一次完整的采集→入库过程）产生一条 **PipelineRun** object：

```json
{
  "schema": "PipelineRun",
  "id": "run::adapter-douyin::2026-07-06T18:30:00",
  "adapterName": "adapter-douyin",
  "triggeredBy": "cron:抖音指数日报_1030",
  "startedAt": "2026-07-06T18:30:00",
  "finishedAt": "2026-07-06T18:31:23",
  "status": "success",
  "stages": {
    "extract":   {"status": "success", "recordsRead": 8, "durationMs": 4521},
    "transform": {"status": "success", "recordsMapped": 8, "recordsSkipped": 0, "durationMs": 312},
    "load":      {"status": "success", "recordsAdded": 6, "recordsUpdated": 2, "durationMs": 145},
    "validate":  {"status": "success", "rulesChecked": 10, "rulesFailed": 0, "durationMs": 67},
    "audit":     {"status": "success", "loggedTo": "ingest_log", "durationMs": 23}
  },
  "errors": [],
  "warnings": [
    {"stage": "transform", "code": "spot_id_unmapped", "message": "spot '清明上河园' not in SCENIC_SPOT_MAP, defaulted to 'qingming_river'"}
  ]
}
```

**关键设计点**：
- `id` 用 runId 命名（不是 UUID，因为同 adapter 同时间戳 = 同 run，可幂等 upsert）
- `stages` 是嵌套对象，5 个 stage 各自有独立 status/duration/records
- `warnings` 不阻塞成功，但写到 run record 让 dashboard 可视化
- `errors` 任一为非空 → `status="failed"`，触发 failureAlert

### 2.4 adapterGovernance — 4 个治理轴

| 轴 | 控制点 | 失败行为 |
|----|--------|---------|
| **Schema 契约** | adapter 输出必须遵循 ontology.json schema 字段 | hard fail（拒绝写入）|
| **Idempotency** | 同一 source+date+metricType 重跑 = 同结果 | 无副作用，count 为 updated |
| **Field Validation** | V-001~V-006 schema 规则 + V-007~V-015 业务规则 | hard fail |
| **Rate Limit** | 同一 adapter 1h 内最多 12 次 run（保守） | 跳过并 warning |

### 2.5 失败处理 3 档

```
Hard Fail（status=failed，触发告警）
  - Schema 字段缺失
  - V-001 ID 命名违反
  - V-002 Cardinality 冲突
  - V-004 Region link 缺失
  - V-008 Action cardinality 冲突
  - V-009 highStakes 缺少 approval

Soft Warning（status=success，但 warnings[] 增加）
  - 重复 ID（已有同 id object）
  - source confidence < 0.5（数据不可信）
  - dailyVolatility > 50%（数据异常大，需人工复核）
  - spot_id_unmapped（用 fuzzy match 兜底）

Silent Skip（status=success，不入 warnings）
  - 同一 runId 重跑（幂等）
  - rate limit 触发的跳过
```

---

## 三、Adapter Pipeline Pattern（v1.4.0 新增 section）

### 3.1 4 个统一约定

#### Convention 1: 入口函数签名标准化

```python
def run_pipeline(
    *,
    adapter_name: str,
    triggered_by: str = "manual",
    input_path: Optional[Path] = None,
    dry_run: bool = False,
) -> PipelineRun:
    """所有 adapter 必须实现这个签名"""
```

#### Convention 2: 阶段产物显式返回

```python
class PipelineRun:
    extract_output: list[dict]   # 原始数据
    transform_output: list[dict] # Ontology objects
    load_result: IngestResult    # store.ingest_objects 返回值
    validation_result: ValidationResult
```

#### Convention 3: 全链路 runId 传递

```python
run_id = f"run::{adapter_name}::{datetime.now().isoformat()}"
# 5 个 stage 共享 run_id（写入 log + pipeline_runs 表 + 告警 context）
```

#### Convention 4: 失败 → 告警 → 升级（escalation）

```python
def escalate(run: PipelineRun):
    if run.status == "failed":
        if run.adapter_governance.tier == "critical":
            send_feishu_alert(channel="电影小镇群", ...)
        elif run.adapter_governance.tier == "important":
            send_feishu_alert(channel="personal_DM", ...)
        else:
            log_warning_only(run)
```

### 3.2 现有 3 个 adapter 的改造矩阵

| Adapter | 现状 | Week 4 改造点 | 优先级 |
|---------|------|--------------|--------|
| adapter-douyin | ✅ active（250 行）| 改入口签名为 run_pipeline；加 stage 计时；warnings 上报 | P0 |
| adapter-xiaohongshu | ⚠️ active 但**爬虫待补**（427 行）| 同上 + 反向 contributes_to link 实施 | P0 |
| adapter-visitors | ⚠️ **planned**（185 行）| 完整重写：补 run_pipeline + CSV SSOT 解析 + revenue metric type | P0 |
| adapter-baidu | ❌ **planned** | 完整新建：百度指数 → MetricSnapshot | P1 |

---

## 四、ingestObservability — 端到端可观测性

### 4.1 4 层可观测性

```
Layer 1: 实时日志（每个 stage 写 stdout + 文件 log）
Layer 2: 持久化记录（ingest_log 表 + pipeline_runs 表）
Layer 3: 健康检查（每日 00:30 cron：健康率 < 95% 告警）
Layer 4: 趋势指标（每周日：各 adapter 成功率、平均 records、p95 latency）
```

### 4.2 健康指标公式

| 指标 | 公式 | 阈值 |
|------|------|------|
| Adapter 健康率 | success_runs / total_runs (7d) | < 95% 告警 |
| Adapter 时延 | p95 stage duration | > 60s 告警 |
| 数据完整度 | records_mapped / records_read | < 90% 告警 |
| 异常检测命中率 | anomalies_detected / total_snapshots | 1-3% 正常 |

### 4.3 失败重试策略

```
Stage 1 (extract) 失败 → 重试 3 次，间隔 30s → 仍失败 → 告警
Stage 2 (transform) 失败 → 不重试（schema 错误重试无意义）→ 告警
Stage 3 (load) 失败 → 重试 3 次（可能是 db lock）→ 仍失败 → 告警
Stage 4 (validate) 失败 → 不重试 → 告警
Stage 5 (audit) 失败 → 不影响 status（log 即可）
```

---

## 五、5 个新 Function（Function Pipeline 编排）

### F-012: orchestratePipeline（type=Aggregator）
**职责：** 接收 1 个 PipelineRun 配置 + 调 5 个 stage 函数，组装为完整 run
**输入：** PipelineRunConfig{adapter, input_path, triggered_by, dry_run}
**输出：** PipelineRun object（含完整 stages 状态）
**usedBy：** 所有 cron adapter 调用点

### F-013: validateAdapterSchema（type=Pure）
**职责：** 检查 adapter 输出 objects 是否符合 ontology.json schema 字段定义
**输入：** schema name + objects list
**输出：** ValidationResult{passed, errors[], warnings[]}
**usedBy：** orchestratePipeline 的 stage 4

### F-014: enrichWithProvenance（type=SideEffect）
**职责：** 给所有写入的 objects 加 ingestRunId / ingestedAt / ingestSource 三个字段（**新 requirement**）
**输入：** objects list + run_id
**输出：** 增强后的 objects（in-place mutate）
**usedBy：** store.ingest_objects 前置 hook

### F-015: calculateAdapterHealthScore（type=Pure）
**职责：** 计算 adapter 健康率（过去 7 天）
**输入：** adapter_name + days
**输出：** {healthRate, p95Latency, avgRecords, alertLevel}
**usedBy：** Cookie 健康检查 cron / 每日复盘 cron

### F-016: detectPipelineAnomaly（type=FunctionBacked）
**职责：** 检测 pipeline run 异常（如 records_read 突降到 0、stage 4 频繁失败）
**输入：** adapter_name + lookback_days
**输出：** {isAnomaly, anomalyType, confidence}
**usedBy：** heartbeat / 周日系统升级

---

## 六、5 条 Validation Rule（V-011~V-015）

### V-011: Adapter Schema 字段必填
**规则：** adapter 输出的每个 object 必须包含 ontology.json 该 schema 定义的 required 字段
**实施：** scripts/ontology/validate.py::validate_adapter_schema（Week 4）
**类型：** schema 层
**失败行为：** hard fail（拒绝写入）

### V-012: ingestRunId 必填（provenance 追溯）
**规则：** 所有通过 adapter 写入的 objects 必须有 ingestRunId 字段，指向 PipelineRun.id
**实施：** validate.py::validate_provenance
**类型：** provenance 层
**失败行为：** hard fail

### V-013: Adapter 输出 confidence 必填
**规则：** MetricSnapshot / ContentAsset 的 confidence 字段必填，值在 [0, 1]
**实施：** validate.py::validate_confidence（Week 1 已有逻辑升级）
**类型：** schema 层
**失败行为：** hard fail

### V-014: PipelineRun.status 与 stages 状态一致性
**规则：** PipelineRun.status == 'success' ⇔ 所有 stages.status == 'success'
**实施：** validate.py::validate_run_status_consistency
**类型：** pipeline 层
**失败行为：** hard fail（pipeline_run 表写入前）

### V-015: 高频 Adapter 必须有 health 探针
**规则：** 凡 cron 每小时 ≥ 1 次调用的 adapter，必须有 health 探针 + failureAlert 配置
**实施：** scripts/ontology/health_probe.py（Week 4）
**类型：** governance 层
**失败行为：** soft warning（首次），hard fail（3 次后）

---

## 七、5 条 Design Decision（D-021~D-025）

### D-021: Pipeline as First-Class Concept
**决策：** 引入 PipelineRun 实体作为「一次完整采集→入库」的 first-class 对象
**理由：** 当前 adapter 调一次 ingest_objects 是一次「半事务」，无 retry、无 stage 隔离、无端到端追踪。PipelineRun 把整条链变成可观测的 run
**参考：** Palantir Data Connection Sync 的 run concept
**替代：** 维持现状（adapter + ingest_log 散乱）— 失败时排查成本高
**代价：** 多一张表 + 多一个 Function；值得

### D-022: 5-Stage Pipeline 标准化
**决策：** 所有 adapter 强制走 extract → transform → load → validate → audit 5 阶段
**理由：** 让 agent/dashboard 可假设所有 adapter 都有这 5 个 stage，方便通用监控/告警
**不强制：** extract stage 内部实现（douyin 可能用 CDP，xhs 用 batch json，visitors 用 csv）— 只要求入参与出参统一
**代价：** adapter 重构（Week 4 1 天工作量）

### D-023: PipelineRun 写入 SQLite（不写入 JSON snapshot）
**决策：** PipelineRun 仅写入 SQLite pipeline_runs 表，不写 JSON snapshot
**理由：** PipelineRun 是运行时产物，不是 ontology 业务对象（区别于 MetricSnapshot/ContentAsset）
**例外：** 失败 PipelineRun 不入快照，避免 git 噪声
**代价：** PipelineRun 历史仅在 SQLite 可见（7 天滚动保留，cron 自动清理）

### D-024: failureAlert 三档分级（adapter tier）
**决策：** adapter 按业务重要性分 3 档：critical（抖音/客流）/ important（小红书/百度）/ optional（手工录入）
**理由：** critical 失败必须告警到飞书群；important 告警到个人 DM；optional 仅 log
**实施：** v1.4.0 adapterGovernance.tier 字段
**代价：** 站长未来 1 次配置（每个 adapter 选 tier）

### D-025: 幂等性 = runId 不重复
**决策：** 同一 adapter 同分钟（minute 精度）只允许 1 个 runId
**理由：** cron 重入时（如网络抖动导致上 1 次未完成又触发）不重复写入
**实施：** PipelineRun.id 命名 = `run::{adapter_name}::{YYYY-MM-DDTHH:MM}`，minute 级
**代价：** 高频 adapter（cookie 健康 00:30 这种）需要迁到 second 精度 → 改 cron 表达式或用 `run::xxx::{sec}` 后缀
**触发改造条件：** 当真实出现 cron 重入导致重复 run 时再升级

---

## 八、Week 3 vs Week 4 切分（避免 scope creep）

### Week 3 完成（本次 🔵 设计阶段）
- ✅ ontology.json v1.4.0 升级（adapterGovernance / pipelinePattern / ingestObservability 3 个 section）
- ✅ 5 个 Function 设计（F-012~F-016）
- ✅ 5 条 Validation Rule 设计（V-011~V-015）
- ✅ 5 条 Design Decision 决策（D-021~D-025）
- ✅ PipelineRun entity schema 设计
- ✅ 5-stage pipeline 架构定稿

### Week 4 启动（**下周一 7/13**）
- ⏳ scripts/ontology/pipeline.py — orchestrator 实施（F-012）
- ⏳ scripts/ontology/validate.py — V-001~V-015 全量
- ⏳ scripts/actions/wrapper.py — Action 治理层（5 层）实施
- ⏳ adapter-douyin / adapter-xiaohongshu / adapter-visitors 改造为 run_pipeline 入口
- ⏳ db migration 002 — pipeline_runs 表 + metric_snapshots 派生列
- ⏳ calculateBaselineValue / detectAnomaly 实施

---

## 九、与已有 Best Practice 的对齐

### 9.1 对齐 BEST_PRACTICES.md §实践 9：适配器 Schema 与存储 Schema 分离
✅ Week 3 延续：adapter 输出 ontology schema（camelCase）→ store 转换 snake_case → db 存储
✅ 新增：adapter 输出必须加 ingestRunId（D-022 + V-012 provenance 追溯）

### 9.2 对齐 D-008：FIELD_MAP 集中管理
✅ Week 3 延续：所有 adapter 共用 scripts/ontology/ontology_constants.py 的 SCENIC_SPOT_MAP
✅ 新增：SCENIC_SPOT_MAP 升级为带 tier/metadata 的 schema（adapter-tier 字段）

### 9.3 对齐 D-006：JSON Git 快照层
✅ Week 3 调整：**PipelineRun 不入 Git 快照**（D-023 决策），仅业务对象入快照
✅ 理由：PipelineRun 是运行时产物，写入 git 噪声大；业务对象才有追溯价值

### 9.4 对齐 D-003 / D-017：Action 5 层治理
⏳ Week 3 仅完成设计，Week 4 实施
⏳ Action wrapper 第一次被 adapter 实际调用是 Week 4

### 9.5 对齐 D-018：Function-backed Action 模式
⏳ Week 3 仅在 F-012 orchestratePipeline 中体现 Function 编排
⏳ Week 4 Action 治理层才会全面使用 Function-backed 模式

---

## 十、对标 Palantir Foundry

### 10.1 我们的对应物

| Palantir Foundry 概念 | 我们的实现 | 状态 |
|------------------------|-----------|------|
| Data Connection | adapter-* | ✅ 3 个 active |
| Sync Run | **PipelineRun**（Week 3 新增）| 🔵 设计中 |
| Sync Schedule | cron job + triggeredBy | ✅ |
| Sync Status (SUCCESS/FAILED/RUNNING) | PipelineRun.status | 🔵 |
| Sync Stage (extract/transform/load) | 5 stages | 🔵 |
| Sync Audit Log | ingest_log + pipeline_runs | ⚠️ 部分 |
| Sync Failure Alert | failureAlert 字段 | ⏳ Week 4 |
| Source Schema Validation | V-011 | 🔵 Week 3 设计 |
| Object Type Schema | ontology.json v1.4.0 | ✅ |
| Function-backed column | F-014 enrichWithProvenance | 🔵 Week 3 设计 |

### 10.2 我们比 Palantir 简化的部分

| Palantir 概念 | 我们的简化 | 理由 |
|---------------|-----------|------|
| Branch-based Development (Code Repositories + Branches) | 单一 ontology.json 主分支 | 单人维护，无需 branching |
| Multi-source Schema Inference | 手动 adapter 写 transform | 数据源少（5 个），不值得自动化 |
| Real-time Stream Processing | 每日 batch 即可 | 景区数据非高频（< 200 条/天）|
| 复杂 Transformation Functions (Data Lineage Graph) | 简单 Python transform | 不需要 lineage 可视化 |

### 10.3 我们多出的部分（独特价值）

| 我们的概念 | Palantir 是否有 |
|-----------|----------------|
| adapter-tier 分级告警 | ❌（Palantir 假设所有 source 同等重要）|
| WIKI 集成（adapter 也可写 wiki 笔记）| ❌ |
| 与飞书群组告警链路 | ❌ |
| 中文场景 OCR 字段处理 | ❌ |

---

## 十一、未决问题（Week 4 解决）

### Q1: PipelineRun 表与 ingest_log 表的关系？
**当前思考：** PipelineRun 是「一次完整 run」，ingest_log 是「一条 object 写入记录」。一对多。
**Week 4 待做：** 在 ingest_log 表加 run_id 列（FK → pipeline_runs.id）

### Q2: 5 stage 是不是太重了？3 stage 够不够？
**当前思考：** 5 stage 是 Palantir 标准；我们减到 4 stage 也不损失可观测性
**Week 4 验证：** 实施后看 dashboard 体验

### Q3: adapter 的 dry_run 模式要不要做？
**当前思考：** Yes，cron 在异常后想手动跑一遍验证
**Week 4 实施：** run_pipeline(..., dry_run=True) 时跳过 load stage

### Q4: 跨 adapter 的级联告警怎么处理？
**场景：** adapter-douyin 失败 → 衍生出 adapter-visitors 的「今天 vs 昨天」对照失真 → visitors adapter 也需要触发告警
**Week 4 决策：** 不做级联告警（复杂度太高），仅单 adapter 独立告警

### Q5: PipelineRun 7 天滚动清理是 cron 还是 SQLite auto-vacuum？
**Week 4 决策：** 加 cron `pipeline_run_cleanup`（每日 03:00 跑），删 7 天前的 record
**依据：** auto-vacuum 不可控（依赖 SQLite 配置）；cron 显式更可审计

---

## 十二、对电影小镇业务的具体应用（7 月下半月即将发生）

### 12.1 抖音指数日报（10:30 cron）
- **改造前：** douyin_index.py → /tmp/crawl_data.json → adapter-douyin.py → 散落写入
- **改造后：** douyin_index.py → run_pipeline(adapter_name='adapter-douyin') → PipelineRun 完整记录 → 失败自动告警
- **增益：** 「上周抖音日报失败几次」「adapter 平均 records」「p95 时延」变成 dashboard 数字

### 12.2 小红书内容动态（10:00 cron）
- **改造前：** 爬虫偶尔 not_logged_in → adapter 不知道 → 当日无 ContentAsset 写入 → 无告警
- **改造后：** run_pipeline.extract stage 失败 → 立即告警到飞书群（adapter-tier=important → 个人 DM）
- **增益：** 7/2 灵犀 not_logged_in × 3 日的事故**当天就能发现**

### 12.3 客流数据（每周二更新）
- **改造前：** adapter-visitors 还是 planned 状态，没有真正运行
- **改造后：** 每周二 09:30 自动跑 adapter-visitors → 写入 MetricSnapshot(visitors) + MetricSnapshot(revenue)
- **增益：** calculateBaselineValue 写入 14 天均值 → detectAnomaly 自动标 6 月崩盘日均 1,428

### 12.4 竞品爆款拆解（15:00 cron）
- **改造前：** 拆解结果写到 wiki 笔记，无 Ontology 接入
- **改造后：** 拆解结果 → ContentAsset + DecisionRule（爆款公式 R-005 等）
- **增益：** 14 条爆款公式 + 52 案例变成可 query 的 ontology 对象

---

## 十三、与 SOUL.md「karpathy-guidelines」的对照

| Karpathy 原则 | Week 3 应用 |
|--------------|------------|
| **Think Before Coding** | Week 3 仅设计不写代码；Week 4 才动手。避免过早抽象 |
| **Simplicity First** | 5 stage 不增不减；PipelineRun 是单表不是多表；不为「未来分布式」过度设计 |
| **Surgical Changes** | 本次只动 ontology.json v1.3.0 → v1.4.0（additive，不修改已有 Object/Link Type）|
| **Goal-Driven** | Week 3 的 goal 是「让 adapter 失败可观测」，所有设计都为这个目标服务 |

---

## 十四、与 MEMORY.md 的写入联动

### 14.1 本周关键洞察（待写入）

```
[project] Ontology Week 3 完成：数据接入管道设计落地
  - 引入 PipelineRun 实体作为「一次完整采集→入库」first-class 对象
  - 5-Stage Pipeline 标准化（extract/transform/load/validate/audit）
  - adapter-tier 三档分级（critical/important/optional）
  - 设计决策 D-021~D-025 + Validation V-011~V-015 + Function F-012~F-016
  - ontology.json v1.4.0 升级（adapterGovernance/pipelinePattern/ingestObservability 三 section）
  - Week 4 才动手实施：scripts/ontology/pipeline.py + validate.py + actions/wrapper.py
```

### 14.2 Phase 2 提前触发
实现路线图 Phase 2 标的是 Week 7（adapter 改造 + db migration 002 + validate.py），但 Week 3 的设计已经把 Phase 2 的工作分解完了。
**实际节奏：** Phase 2 实施 = Week 4（7/13）— 比原计划 Week 7 提前 3 周。

---

## 十五、相关文档索引

| 文档 | 关联 |
|------|------|
| `Week1_ObjectTypes_LinkTypes.md` | 上游：Object/Link Type 是 pipeline transform 的目标 schema |
| `Week2_Actions_Functions.md` | 上游：Function F-012~F-016 复用 Week 2 的 4 类型分类 |
| `实现路线图.md` | 下游：Week 3 完成后追加记录 + Phase 2 启动标记 |
| `基础设施评估.md` | 上游：D-005 SQLite + D-006 JSON 双写 |
| `本地接入方案.md` | 上游：adapter 入口签名 |
| `BEST_PRACTICES.md` | 上游：§实践 9 schema 分离 |

---

**Week 3 完结。下周 Week 4：脚本实施（pipeline.py + validate.py + actions/wrapper.py + 3 adapter 改造 + db migration 002）。**