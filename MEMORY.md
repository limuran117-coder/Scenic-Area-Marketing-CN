# MEMORY.md - Long-Term Memory
role: 景区营销中心总经理 | core_mission: 客流153万、营收1.2亿 | update: 2026-07-26

---

# ⭐ 铁律（违反必纠）

**客流日报** 密码912530 | 5章: YTD→月度→近7日→德化街→建议 | ≤5表/卡
**飞书卡片** schema=2.0走 `scripts/send_feishu_card.py` | 表格外 `
`，表内 `
`，表头可用`⚠️`
**【7/2 站长纠错】数据类报告必须用 markdown 表格**：搜索指数/综合指数/同比环比/分项分解/区域TOP5/关联词等任何多列数据，禁止用 emoji+加粗列表+内联文字罗列；必须 `| 列1 | 列2 | ... |` 格式
**双通道采集** 抖音脚本+CDP交替验证
**CDP必须用Playwright** urllib/websockets连18800会超时
**数据必须读实际值** | 搜索「建业电影小镇」禁「建业华谊兄弟」
**洞察驱动** 所有分析任务必须先给结论再给数据，禁止只报数字

**【6/30 站长纠错】收官/总结卡片前必做 2 项核对**：
  ① **CSV 末尾完整性** — 扫末日 N 列（≥3）是否为 0；为 0 → 标"暂态"，**不写"收官"**
  ② **节假日逐日曲线** — 暴涨/暴跌/断崖异常必须显式标注
**Why:** 6/30 H1 收官把端午累计 11,513 当结论，没看出 6/21=782 暴跌88%
**How:** 卡片生成前最后一步必跑 `tail -5` + 节假日逐日表两个 check

**【7/2 站长纠错】客流分析必须用 4 年均值口径**：任何同比必须三轨（2024/2025/2026）同时输出，**禁止仅比 2025**
**Why:** 2025 是异常大年（剔除2月后H1 -51.7%）
**How:** 月度/季度/年报类必出 4 年×月份矩阵表 + 4年均值列

**【7/13 站长纠错】事实核查铁律**：wiki/SOP/票务系统里没记录的内容视为伪事实，必须先 read 知识库验证
**【7/23 站长纠错】双 db 路径陷阱**：`scripts/ontology/ontology.db` ≠ `.profile/ontology/ontology_store.db`（生产db）；写修复脚本前必先确认 DB_PATH
**【7/23 站长纠错】ontology_daily_work 强制收尾**：日志写入 wiki 后立即结束，不跑 verification/cross-check
**【7/25 站长决策】景区更名**：建业电影小镇 → 郑州电影小镇（双轨采集，新名优先）；历史档案保留旧名

---

# 🚨 当前系统状态（2026-07-26 W30）

**模型**: M3 | 基础设施 all ✅ | cron: 30 ok / 3 err（小红书日报+竞品关键词+周二客流深度报告）
🚨 小红书采集 42 天断档（站长决策不修）| 近期工作 → `memory/2026-07-23.md`

---

# 📊 关键数据指针

| 类别 | 路径 |
|------|------|
| 客流 SSOT（2026） | ~/Downloads/2026游客量统计 (16).csv（7/21）+ dbt(3).xlsx（6/23）|
| 历年客流 | ~/Desktop/2023-2025年门票销售及客流统计数据表.xlsx |
| 内部运营 | `wiki/sources/建业电影小镇阶段性数据表.md` |
| Cookies | /tmp/juLiang_cookies.json（抖音）/ xiaohongshu_cookies.json |
| Ontology 生产 db ⚠️ | `.profile/ontology/ontology_store.db` |

---

# [project] 项目状态

**Ontology 进度**：Week 1-3 已完（v1.4.0 PipelineRun）；Phase 2 W4 启动
**结论索引系统**：洞察任务前置读 `wiki/行业知识/结论索引.md`
**漂移双跑**：每周一/三/五 cron（wiki_drift_check + project_drift_check）
详细 → `memory/topics/ontology-progress.md`

---

# ⛔ 端午日期SSOT
唯一权威：`wiki/行业知识/节假日基准.md` | 2026端午正日=6/19（周五）| 放假 6/19-21

---

# 防错机制
- 详细：`wiki/SOP/防错机制-2026-06-16.md`
- 写入3步：搜索→交叉→标注来源 | 任务5步法：源→事实→脚本→检查→验证
- ⚠️ wiki/ 大文件迁移 → 先 /tmp dry-run + 数据完整性核对
- ⚠️ 覆盖前必 cp 备份
- ⚠️ 结论索引.md 禁止 in-place 重写

---

# 已结项
DeepSeek→M3切换 | 5/27系统重构 | M3-only配置 | DDG修复 | cron冲突修复 | SOP路径漂移修复 | 洞察驱动prompt升级(6/12) | 系统瘦身+结论索引(6/13) | 6/22 方案A升级 | 6/24 cron时间表重排 | 7/2 Cookie健康+MEMORY压缩 | Ontology Week 1+2+3 | 7/23 双db路径修复 | 7/25 景区更名执行

---

# 🗜️ 7/26 周维护压缩记录
- MEMORY.md: 125行→99行 / 12KB→6KB
- hermes-agent 研究 → `memory/topics/github-research-20260725.md`
- 更名铁律细节压缩（原12行→精简版）
