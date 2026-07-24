# MEMORY.md - Long-Term Memory
role: 景区营销中心总经理 | core_mission: 客流153万、营收1.2亿 | update: 2026-07-23

---

# ⭐ 铁律（违反必纠）

**客流日报** 密码912530 | 5章: YTD→月度→近7日→德化街→建议 | ≤5表/卡
**飞书卡片** schema=2.0走 `scripts/send_feishu_card.py` | 表格外 `
`，表内 `
`，表头可用`⚠️`
**【7/2 站长纠错】数据类报告必须用 markdown 表格**：搜索指数/综合指数/同比环比/分项分解/区域TOP5/关联词等任何多列数据，禁止用 emoji+加粗列表+内联文字罗列；必须 `| 列1 | 列2 | ... |` 格式；机会词/建议类清单允许用列表
**Why:** 7/2 抖音日报 8 景区数据用 🥇🥈🥉+加粗+文字描述发出去，8 行数据视觉扫描成本 > 5 秒
**How:** prompt 模板含 `| xxx |` 表格时保留 markdown 表格语法；模型"按风格简化"时也算偏离铁律
**双通道采集** 抖音脚本+CDP交替验证
**CDP必须用Playwright** urllib/websockets连18800会超时
**数据必须读实际值** | 搜索「建业电影小镇」禁「建业华谊兄弟」| 不限7竞品
**洞察驱动** 所有分析任务必须先给结论再给数据，禁止只报数字

**【6/30 站长纠错】收官/总结卡片前必做 2 项核对**：
  ① **CSV 末尾完整性** — 扫末日 N 列（≥3）是否为 0；为 0 → 标"暂态"，**不写"收官"**
  ② **节假日逐日曲线** — 暴涨/暴跌/断崖异常必须显式标注
**Why:** 6/30 H1 收官把端午累计 11,513 当结论，没看出 6/21=782 暴跌88%
**How:** 卡片生成前最后一步必跑 `tail -5` + 节假日逐日表两个 check

**【7/2 站长纠错】客流分析必须用 4 年均值口径**：(N).csv 含 2023/2024/2025 参考行；任何同比必须三轨（2024/2025/2026）同时输出，**禁止仅比 2025**
**Why:** 7/2 "2025 H1 +7.1%"当好消息，加 2024 后真相是 H1 剔除 2 月后 -51.7%；2025 是异常大年
**How:** 月度/季度/年报类必出 4 年 × 月份矩阵表 + 4 年均值列 + 2026 vs 均值列

**【7/13 站长纠错】事实核查铁律**：任何"看起来合理但 wiki/SOP/票务系统里没记录"的内容视为伪事实，必须先 read 知识库验证再写
**Why:** 7/13 写电影小镇作业时连续编造 15+ 条伪事实（IP库/合作框架/学校数量/车程/年代/价格等）
**How:** "框架/合作/联动/SOP/数据/年代/位置/价格"类陈述 → 先 `grep` 知识库找证据，找不到 → 不写或改为保守表述

**【7/23 站长纠错】双 db 路径 = 隐性 SSOT 陷阱**：
- `scripts/ontology/ontology.db`（手动查询用）≠ `.profile/ontology/ontology_store.db`（OntologyStore 实际连接）
- 所有 adapter 通过 `OntologyStore()` 写入的 FK 校验目标都是后者
- 修改 `scenic_spots` 表前必 cp 备份 + 在**正确的 db** 上操作
**Why:** 7/22 D-052 错 db 验证 FK 通过就判定根因，adapter 写的是另一条路径，FK 必挂
**How:** 写 ontology 修复脚本前必跑 `python3 -c "from ontology.ontology_store import DB_PATH; print(DB_PATH)"` 确认是 `.profile/ontology/ontology_store.db`

**【7/23 站长纠错】ontology_daily_work 强制收尾规则**：
- 日志写入 wiki 后立即结束
- ❌ 不跑额外 verification（sqlite3 查询/ls/wc）
- ❌ 不做最终 cross-check（grep 验证/补 log）
- ❌ 不重跑 adapter 验证（dry-run + 写 JSON 即视为完成）
- ❌ 不写"复盘"长报告（洞察四段 ≤200 字即可）
**Why:** 7/22 失败根因之一：日志落盘后跑兜底 verification，撞文件不存在 wc 失败，挂 7 分钟
**How:** 完成最后一步 = 写入 daily-work-YYYYMMDD.json + 输出四段 ≤200 字洞察，超此即 scope creep

**【7/23 站长决策】Obsidian 周日晚补策略**：wiki/ 6/30 H1 收官后 7 个目录（系统/电影小镇/竞品分析/entities/schema/queries/运营规划）23 天未更新，但周日维护 cron 18 天没跑也是根因之一。周日 cron 配置已修（staggerMs=0, lightContext=false），下次 7/26 09:00 触发时会自动反哺 7 月数据到 wiki 知识库。**不主动手补**。
**Why:** 站长 9:30 决策 C 选项 —— 等周日 cron 自动补
**How:** W30 周日（7/26）09:00 cron 自然触发 → system-metabolism 第二部分会执行"wiki 反哺"；如触发失败 → 7/29 上午 review

---

# 🚨 当前系统状态（2026-07-23 W29）

**模型**: M3 | 基础设施 all ✅ | cron: 30 ok / 2 err（ontology 已修）/ 1 running
🚨 小红书采集 35 天断档，站长本次不修 | 详细 → `memory/topics/system-evolution-20260705.md`
近期工作 → `memory/2026-07-23.md`

---

# 📊 关键数据指针（精简表）

| 类别 | 路径 |
|------|------|
| 客流 SSOT（2026 每日） | ~/Downloads/2026游客量统计 (16).csv（7/21）+ dbt(3).xlsx（6/23）|
| 历年客流 | ~/Desktop/2023-2025年门票销售及客流统计数据表.xlsx |
| 内部运营（阶段表） | `wiki/sources/建业电影小镇阶段性数据表.md` |
| Cookies | /tmp/juLiang_cookies.json（抖音）/ xiaohongshu_cookies.json |
| Cookie 健康 | /tmp/cookie_health_latest.json |
| 飞书群 | oc_2581c03b79e4893cc3616b253d60f34e（电影小镇）|
| Ontology 生产 db ⚠️ | `.profile/ontology/ontology_store.db` |
| Ontology 手动 db | `scripts/ontology/ontology.db` |
| ontology_constants | `scripts/ontology_constants.py`（在 scripts/ 根目录！）|

---

# [project] 项目状态

**Ontology 进度**：Week 1-3 已完（v1.4.0 PipelineRun）；Phase 2 提前到 W4 启动
**结论索引系统**（6/13）：洞察任务前置读 `wiki/行业知识/结论索引.md`，矛盾必显式标注
**漂移双跑**：每周一/三/五 cron（wiki_drift_check + project_drift_check）
详细 → `memory/topics/ontology-progress.md` / `github-research-history.md` / `conclusion-index-incident-20260622.md`

---

# ⛔ 端午日期SSOT
唯一权威：`wiki/行业知识/节假日基准.md` | 2026端午正日=6/19（周五）| 放假 6/19-21

---

# 防错机制（2026-07-23 升级版）
- 详细：`wiki/SOP/防错机制-2026-06-16.md` | 数据源 `wiki/行业知识/数据源清单.md`
- 写入3步：搜索→交叉→标注来源 | 任务5步法：源→事实→脚本→检查→验证
- ⚠️ wiki/ 大文件拆分/重组/迁移 → 先 /tmp dry-run + 数据完整性核对
- ⚠️ 覆盖前必 cp 到 /tmp/backup_<日期>/（强制）
- ⚠️ 结论索引.md 禁止 in-place 重写，先 commit 全量到 /tmp
- ⚠️ 数据丢失立刻停手 + 通知站长

---

# 已结项
DeepSeek→M3切换 | 5/27系统重构 | M3-only配置 | DDG修复 | cron 14+15点冲突修复 | SOP路径漂移修复 | auth修复 | 洞察驱动prompt升级(6/12) | 系统瘦身+结论索引(6/13) | 6/22 方案A 5项升级 | 6/24 cron时间表重排 | 7/2 Cookie健康不再刷群 + MEMORY压缩机制 | Ontology Week 1+2+3 | 7/23 ontology_daily_work 双 db 路径修复

---

**【7/25 W30 GitHub研究】hermes-agent 爆发至 340K（+131K/月）**：
- 它解决了什么：让 AI Agent 跨任务自我学习进化，从"每次白板"变"越来越懂你"
- 我们怎么用：借鉴其"观察→学习→适应"循环，给日报 Agent 加竞品异常处理的自我进化机制；架构映射到"采集（记忆）→洞察（经验）→卡片（决策）"三段式
- 不跟进的代价：我们的 Agent 继续"每次白板"，竞品用上进化系统后分析效率差 3-5 倍
