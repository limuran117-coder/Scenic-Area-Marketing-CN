# MEMORY.md - Long-Term Memory
role: 景区营销中心总经理 | core_mission: 客流153万、营收1.2亿 | update: 2026-07-26 W30

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
**【7/29 站长纠错】禁止发卡自检循环**：每个 isolated session 全程最多发 1 张卡片到电影小镇群；飞书 API code=0 即视为成功，**禁止看 response.content 再判断**；禁止任何 layout A/B test 刷屏
  - 7/28 19:37 实证事故：竞品关键词深度分析 isolated session 03fb2625 飞书 API 返回老格式占位图，agent 自检循环发了 17 张「Test 1-5/测试/调试/Split/Full E5」+ 2 张原版重渡沟 + 1 张续图 = 20 张刷屏
  - 防错：cron 9bf47f42 prompt 已加【发卡铁律】硬约束（每个 session 最多 1 张 + code=0 即视为成功 + 禁止 test/debug 字样）
  - 监控：cron 7ae9127b 飞书发消息审计（每天 23:55 扫群消息，异常推 ou_f308d672 私聊）
**【7/25 站长决策】景区更名**：建业电影小镇 → 郑州电影小镇（双轨采集，新名优先）；历史档案保留旧名
**【7/23 重要教训】v9误判**：我说"movietown-ai-system-v9完整版不存在"是错的——该文件真实存在于Desktop，13天前生成，150KB/2481行。**所有"XX不存在/找不到"的判断，必须先查workspace全路径+Desktop，不能草率结论**
**【7/23 spike结论】ego-lite**：装了app+v12 stealth脚本，但 ego-browser不能替代CDP18800（已登录采集场景不适配）；feishu-mcp-server与现有4件套冗余；PaddleOCR可用（PDF/PPT/图片中文识别）；crawl4ai默认headless不适合已登录dashboard
**【7/23 v12 stealth】douyin_index.py v12**：stealth wrap在全局作用域调用，graceful degrade（无venv时回退v11）；原v11备份在`/tmp/wiki_remedy_20260723/`

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
**SOP质量系统**：W30进化审视新增 SOP质量升级计划（wiki/技术配置/）；当前34个SOP，2个优先修复：防错机制补When字段 + 竞品分析SOP合并
详细 → `memory/topics/ontology-progress.md`
**郑州电影小镇易主**（7/23 港交所公告）：建业30亿出售只有河南+电影小镇，国资（中信资本旗下信宸资本）90%控股，民企主导正式终结 → 运营策略需重新评估

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
DeepSeek→M3切换 | 5/27系统重构 | M3-only配置 | DDG修复 | cron冲突修复 | SOP路径漂移修复 | 洞察驱动prompt升级(6/12) | 系统瘦身+结论索引(6/13) | 6/22 方案A升级 | 6/24 cron时间表重排 | 7/2 Cookie健康+MEMORY压缩 | Ontology Week 1+2+3 | 7/23 双db路径修复 | 7/25 景区更名执行 | W30 v9误判纠正+stealth集成+PaddleOCR | 7/26 MEMORY二次压缩+w30维护

---

---
**[W31 2026-08-01] GitHub高星标学习：Skills 3.0 — 质量门时代（已落地 24/24）**
- **项目名**：addyosmani/agent-skills（Google工程总监出品，81K⭐ MIT，updatedAt=2026-08-01）
- **它解决了什么**：AI写代码走"最短路径"跳测试跳规格，agent-skills把Google工程纪律编码成强制quality gate（测试覆盖率/类型检查/Lint通过才放行），让AI从"能跑"进化到"可合并PR"
- **安装位置**：`~/.openclaw/skills/`（OpenClaw 系统级目录，24 个全装入）
- **装法**：`npx skills add addyosmani/agent-skills -a openclaw -g -y --dangerously-accept-openclaw-risks`
- **OpenClaw 状态**：全部 `ready` + `openclaw-managed` 标签（验证：`openclaw skills list` 见 24 行）

**24 skill 触发矩阵（按场景分组）：**

| 场景 | 优先 skill | 备注 |
|------|-----------|------|
| 新需求模糊/一句话任务 | `interview-me` | 一问一答到 95% 信心，**7/23 站长纠错"静默填洞"事故的对症药** |
| 任务超 1 文件/感觉大 | `incremental-implementation` | 防一次性大改（agent-skills 元方法论） |
| 写新代码/改脚本前 | `spec-driven-development` | spec 先行，禁止裸奔 |
| cron 失败/采集异常 | `debugging-and-error-recovery` | 系统化根因，禁止猜 3 次（替代当前乱试模式） |
| 改 cron 脚本提交前 | `code-review-and-quality` | 五维 review（correctness/readability/architecture/security/performance） |
| 修 bug/改行为 | `test-driven-development` | 红绿重构强制，TDD 落地 |
| 找"哪个 skill 适用当前任务" | `using-agent-skills` | 元 skill，路由到其他 skill |
| 新项目/大改造 | `context-engineering` + `planning-and-task-breakdown` | 上下文+任务拆分 |
| 想法还模糊 | `idea-refine` | 发散→收敛 |
| 高风险决策（生产/不可逆） | `doubt-driven-development` | 对抗式 review，**验证比自信便宜** |
| 设计 API/模块边界 | `api-and-interface-design` | 稳定接口 |
| 改 web UI/前端 | `frontend-ui-engineering` | 生产级 UI |
| Git 提交/打 tag/分支冲突 | `git-workflow-and-versioning` | semver/changelog |
| 加日志/指标/追踪 | `observability-and-instrumentation` | 生产可见性 |
| 性能慢/N+1 查询 | `performance-optimization` | profile 先于优化 |
| 删旧系统/迁移用户 | `deprecation-and-migration` | sunset 流程 |
| 写 ADR/记录决策 | `documentation-and-adrs` | 决策可追溯 |
| 准备上线 | `shipping-and-launch` | 部署前 checklist |
| 用第三方库/框架 | `source-driven-development` | 官方文档优先 |
| CI/CD 配置 | `ci-cd-and-automation` | 质量门流水线 |
| 安全/输入校验/认证 | `security-and-hardening` | 漏洞防护 |
| 浏览器测试/DevTools MCP | `browser-testing-with-devtools` | 需 chrome-devtools MCP |
| 代码太复杂想简化 | `code-simplification` | 行为不变下提升可读性 |

**我们怎么用**：
- 触发符合 description 时**自动激活**（agent-skills 设计如此）
- 关键场景：日报发布前自动用 `code-review-and-quality` 五维 review schema 2.0 + 数据来源标注
- **不跟进的代价**：日报质量靠AI自觉，无自动化校验；竞品用quality gate后报告稳定性远超我们

**安装命令（重装/更新用）**：
```bash
# 重装全部 24 个
npx skills add addyosmani/agent-skills -a openclaw -g -y --dangerously-accept-openclaw-risks

# 卸指定 skill
npx skills remove <name> -a openclaw -g

# 验证安装
openclaw skills list | grep openclaw-managed
```

**TOOLS.md 同步触发矩阵**：见 TOOLS.md "Skill 3.0 触发矩阵"段
