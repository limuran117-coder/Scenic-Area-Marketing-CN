# MEMORY.md - Long-Term Memory
role: 景区营销中心总经理 | core_mission: 客流153万、营收1.2亿 | update: 2026-06-13

---

# ⭐ 铁律（违反必纠）

**客流日报** 密码912530 | 5章: YTD→月度→近7日→德化街→建议 | ≤5表/卡
**飞书卡片** schema=2.0走 `scripts/send_feishu_card.py` | 表格外 `

`，表内 `
`，表头可用`⚠️`
**【7/2 站长纠错】数据类报告必须用 markdown 表格**：搜索指数/综合指数/同比环比/分项分解/区域TOP5/关联词等任何多列数据，禁止用 emoji+加粗列表+内联文字罗列；必须 `| 列1 | 列2 | ... |` 格式；多个景区对比用「景区 × 指标」矩阵表；机会词/建议类清单允许用列表
**Why:** 7/2 抖音日报 8 景区数据用 🥇🥈🥉+加粗+文字描述发出去，8 行数据视觉扫描成本 > 5 秒；表格只需 1 秒纵览+对比
**How:** prompt 模板含 `| xxx |` 表格时，必须保留 markdown 表格语法；模型“按风格简化”时也算偏离铁律，必须重写
**双通道采集** 抖音脚本+CDP交替验证，任一失败走另一通道
**CDP必须用Playwright** urllib/websockets连18800会超时
**数据必须读实际值** | 搜索「建业电影小镇」禁「建业华谊兄弟」| 不限7竞品
**LLM失败不静默** 显式告警，不依赖自动fallback
**洞察驱动** 所有分析任务必须先给结论再给数据，禁止只报数字
**【6/30 站长纠错】发任何"收官/总结"卡片前必须做 2 项核对**：
  ① **CSV 末尾完整性** — 扫 CSV 末日 N 列（≥3）是否为 0；为 0 → 标"暂态"，**不写"收官"**
  ② **节假日逐日曲线** — 不能只看累计；要看逐日值，暴涨/暴跌/断崖异常必须显式标注
**Why:** 6/30 H1 收官卡片把端午累计 11,513 当结论发，没看出 6/21=782 暴跌88%；把 6/29-30=0 的暂态数据当收官值；站长当场纠错
**How:** 卡片生成前最后一步必跑 `tail -5` + 节假日逐日表两个 check；异常项进卡片必标 ⚠️
**【7/2 站长纠错】客流分析必须用 4 年均值口径**：`~/Downloads/2026游客量统计 (N).csv` 同时含 2023/2024/2025 参考行；任何同比必须三轨（2024/2025/2026）同时输出，**禁止仅比 2025**；用 4 年均值作基准判断"异常高/低"而非"涨跌";2025 是 4 年最高年（6月 2,388/5月 5,767），单一对比会失真
**Why:** 7/2 我用"2025 H1 = 671,212 vs 2026 H1 = 718,875 = +7.1%"当好消息，加 2024 后真相是 H1 剔除 2 月后 2026 实际 -51.7% vs 2024；2025 是异常大年不是常态
**How:** 月度/季度/年报类卡片必出 4 年 × 月份矩阵表 + 4 年均值列 + 2026 vs 均值列

---

# 🚨 当前系统状态（2026-06-21 · W25审视）

**模型**：minimax/MiniMax-M2.7（6/12从M3切换回来，无5h限额）
**auth配置**：openclaw.json有authProfile=minimax:default + 软链接agents→根目录auth-profiles.json ✅
**web_search**：minimax国内搜索 ✅
**代理**：7897 ✅ LISTEN | **CDP**：18800 ✅ LISTEN
**cookie保鲜**：⚠️ 灵犀后台not_logged_in×3日(6/17-19) + 抖音my-subscript采空×3日(6/17-19) | 需站长人工扫码

**今日修复（6/12）**：
- catalog.json apiKey从env变量名→真实key ✅
- 全部32个cron洞察层prompt升级 ✅
- auth软链接缺失 ✅

**今日修复（7/2）**：
- [feedback] **Cookie健康检查不再发飞书群告警**（站长明确要求）—— cron `dee74616-...` prompt 已改：exit 1 时只写 `/tmp/cookie_health_latest.json` + stdout，不再调 `send_feishu_card.py`；告警由 cron failureAlert 兜底（连续 2 次 error → 个人 DM `ou_f308d672765ecf1be73a75eb5e5f0f48`，不刷群）
- [project] **/tmp/cookie_health_latest.json** 已建档为「Cookie健康检查产物」SSOT — 后续日报 prompt 可直接读这个文件判断前置依赖是否健康，无需再独立探测
- [feedback] **Why:** 最近 7 天连发 5 次告警卡（06/23、06/25、06/26、06/27、07/01）+ 7/2 脚本崩溃也走告警路径刷群，站长嫌告警卡片刷屏
- [feedback] **How:** 任何告警类任务必须问「发群 vs 发 DM vs 静默」；6h 陈旧阈值过严可后续放宽（待站长确认）

**W25关键发现（6/21系统进化审视）**：
- [project] **SOP三件套 0/31 全齐首次发现** — When/RedFlag/Verify 覆盖率 6%/0%/10%；YAML 28/31（90%）优秀但三件套严重缺
- [project] **SOP升级连续3周跳票（W23→W24→W25）** — 站长需A/B/C三选一：A集中突击/B拆分3天/C降级H2不做
- [project] **基础设施断链双发** — 灵犀not_logged_in×3日 + 抖音my-subscript采空×3日；需站长人工恢复
- [project] **6/8 cron时间冲突已修**（竞品内容动态14:00→14:30；周日系统代谢9:00→9:30）
- [project] **业务执行层脱节第8天** — 6/15预警的毕业生免票+海魂衫+80年代夜游2.0+品牌主标识 全部未落地
- [project] **R08执行闭环连续5周跳票** — 端午窗口失守已确认
- [project] **W26新建议**：`scripts/cookie_health_check.py` + cron `0 9 * * 1-5` 早于日报2小时发现Cookie/账号失效

**🆕 6/30 H1 收官日报·站长当场纠错**（[feedback]）：
- [feedback] **端午3天 4,099 / 6,632 / 782**——我只看累计 11,513，掩盖了 6/21(初六)暴跌 88% 的断崖；正常 U 型曲线应初五初六持平或缓降
- [feedback] **CSV 6/29=0、6/30=0**——我把"暂态数据"当 H1 收官值 716,409 发出去，事实 H1 未收官；卡片标题应标"暂态"，等周二/Wed Excel 更新
- [feedback] **铁律新增 2 条**（已写入上方铁律区）：① 发收官卡片前必扫 CSV 末日 N 列完整性 ② 节假日数据必看逐日曲线不能只看累计
- [project] **已发修正卡 v2**（om_x100b6b06400b20bcc25b9d26883bf66）—— 显式标注"暂态"+端午异常曲线

**🆕 6/24 重要修复**（3 个 cron 错同时落地）：
- [project] **Cron 时间表重排**（6/24 09:00-09:25 完成）：业务日报全部挪白天，间隔硬规则 ≥2h，复盘挪 23:30/23:35，Cookie 挪凌晨 00:30（周二-周六），删除已 disabled 的 Memory Dreaming
- [project] **复盘 cron 回退单步**（方案 A #2 拆分版有契约不一致 bug）：22:00 生成「业务数据」不是飞书卡片，22:05 投递必 400；6/24 已回退为「单步生成+投递」+ disable 投递 cron（736e87e1）
- [feedback] **prompt 修容错**：「which cron && cron --version」macOS 无 cron 必失败，prompt 加容错说明
- [feedback] **大文件 edit 改 write**：ontology.json 35.5KB，edit 工具超时；prompt 改为 read→parse→write 流程
- [reference] `/tmp/daily_recap_<YYYY-MM-DD>.json` 旧产物（6/22-6/24 拆分版）结构是业务数据，新版本必须含 `header.title.content` + `body.elements[]`

---

# 🔍 关键洞察（持续有效）

**双节点浪费（已固化）** 520有效→端午竞品先动电影小镇零预热→窗口关闭无动作。H1执行闭环未实施。

**内容真空窗口** 搜索涨+综合指数涨→内容供给追不上需求，端午后同步下降（不是背离是真实萎缩）

**票根互认** H6窗口期，6月内必须决策，W22公式变体

**6月开局崩盘** 日均1,187 vs 5月4,395（-73%），端午是H1唯一翻身机会

**端午后竞品格局**：只有河南麦田音乐会(6/5-6/6)高威胁 | 万岁山王婆说媒单一爆款押注风险显现

---

# 📊 关键数据指针

| 来源 | 路径 |
|------|------|
| 历年客流 | ~/Desktop/2023-2025年门票销售及客流统计数据表.xlsx |
| 内部运营数据（SSOT） | `wiki/sources/建业电影小镇阶段性数据表.md`（年度/Q1/德化街模拟/2026KPI/排期模型，2026-06-27更新）|
| 2026每日 | ~~~/Desktop/2026游客量统计.csv（已弃用，截至6/9）~~ → **SSOT: ~/Downloads/2026游客量统计 (N).csv + ~/Downloads/电影小镇-2026年数量统计.dbt(N).xlsx**（每周二更新，最新至6/21）|
| 抖音Cookie | /tmp/juLiang_cookies.json |
| 小红书Cookie | /tmp/xiaohongshu_cookies.json |
| Cookie健康检查产物 | **/tmp/cookie_health_latest.json**（cron `Cookie健康检查` 每日 00:30 跑 `scripts/cookie_health_check.py` 写入，6 项 check + issues；7/2 起不再发飞书群告警，由 cron failureAlert 个人 DM 兜底）|
| 飞书群 | 电影小镇 oc_2581c03b79e4893cc3616b253d60f34e |
| SOP | wiki/SOP/ |
| 核心脚本 | ~/.openclaw/workspace/scripts/ |

---

# [project] 项目状态

**结论索引系统**（2026-06-13上线）：所有洞察任务前置读 `wiki/行业知识/结论索引.md`，矛盾必须显式标注，不允许静默覆盖。
**系统进化审视**（2026-06-13升级）：每周迭代记录→每月准确率报告→每季淘汰检查，三层进化闭环。
**Ontology**：Week 6目标（最小可行Ontology Layer），当前暂停推进（优先级下调）
**系统瘦身**（2026-06-13）：disable 6个冗余任务，清理21个prompt冗余重试逻辑，结论索引+矛盾检查落地
**爆款公式库**：14条公式+52案例，W24新增票根经济/万岁山商业模型
**漂移双跑**：每周一/三/五 cron执行
**GitHub调研**：Agent Zero Annotate Mode — 网页元素自主发现，UI改版自适应。browser-use(97K)趋稳印证基础自动化赛道见顶，下一代方向是"自主发现并操作"而非"执行预设指令"。
- 项目名：agent0ai/agent-zero
- 它解决了什么：Annotate Mode把网页变成可编程操作面，Agent点哪操作哪，无需预设DOM选择器
- 我们怎么用：竞品抖音/小红书后台UI改版时自动恢复采集，无需人工修复脚本
- 不跟进的代价：平台每次UI改版，我们的Playwright脚本需人工介入，竞品系统更快恢复

**GitHub调研 W28（2026-06-27）**：
- 项目名：**ChromeDevTools/chrome-devtools-mcp**（44.1K stars，日增 400，Google Chrome DevTools 团队官方）
- 它解决了什么：**第一个为 AI Coding Agent 设计的浏览器控制协议**——通过 MCP server 把 Chrome DevTools 能力（screenshot/console/network/trace）以工具形式暴露给 LLM agent，填补"AI 想要操控浏览器但不想写代码"的空白
- 我们怎么用：❌ 不能直接接管抖音/小红书采集（只支持 Google Chrome）；✅ 借鉴 3 点：(1) MCP 协议封装思路 → 把本系统的"采集→处理→投递"链抽象为 MCP 工具；(2) Puppeteer 自动等待策略 → 减少 30% time.sleep；(3) CLI + MCP 双入口 → 脚本同时包装为 MCP 工具供其他 agent 调用
- 不跟进的代价：**MCP 已是 AI Agent 工具调用事实标准**（Anthropic 4 月推 → 6 月 Google 接入 → 8 月预计 Cursor/Copilot 跟进）。本系统 56 个脚本全是 CLI/Python 调用，无 MCP 入口，1-2 年后其他 agent 想调用"采集抖音指数/读飞书群"时找不到接口，架构层可能要重写。**但短期抖音/小红书采集脚本仍能稳定跑，MCP 化是 H2 重构话题，W28 无紧迫性**
- 行动：W28-W29 spike "采集脚本出错时自动截屏诊断" 流程 | H2 评估脚本 MCP 化试点

**GitHub调研 W29（2026-07-04）**：
- 项目名：**thedotmack/claude-mem**（85.7K stars，2025-08-31 首版，OpenClaw 原生支持）
- 它解决了什么：填补"AI Agent 持久记忆层操作系统"的空白——自动捕获会话→LLM 压缩摘要→SQLite+ChromaDB 索引→MCP 注入新会话；专门为 OpenClaw/Claude Code 设计，提供 `curl install.cmem.ai/openclaw.sh` 一键安装和 8 个 MCP search tool（search_observations/search_sessions/get_recent_context/timeline 等）。**对比 W26 agentmemory(24K) 是 DIY 集成，claude-mem 是开箱即用的产品级方案**
- 我们怎么用：直接对位本系统 7 大痛点——① MEMORY.md 100 行/25KB 限制 ② 28 个 cron 各自维护 memory 目录 ③ 飞书卡片格式漂移靠人肉发现 ④ LLM 失败时冷启动 token 居高不下 ⑤ 6/22 结论索引事故 1.7KB 丢失教训 ⑥ 跨任务知识无法复用 ⑦ 无 MCP 接口对外暴露能力。**W29-W30 spike 安装 + 验证，32 个 cron 接入 worker service 后预计冷启动 token 降 60%+**
- 不跟进的代价：MEMORY.md 2-3 个月后必然撞限丢失关键规则（6/22 已是先例）；冷启动 token 持续浪费致 M3 5h 限额反复触及；竞品用 claude-mem 后跨任务知识复用效率比我们高 1-2 个量级；错过 MCP-first 红利
- 行动：**W29 本周 spike** `curl -fsSL https://install.cmem.ai/openclaw.sh | bash` → 验证 8 个 MCP search tool → 成功则 W29-W30 把 32 个 cron 接入 worker service

**⚠️ W24关键发现（2026-06-14）**：
1. SOP升级连续2周跳票（小红书日报/文旅/案例库3个SOP四件套未补）→ 建议改策略：由各cron自己顺便执行
2. 3个过时SOP连续3周"待废弃"零行动（竞品深度分析流程/决策简报格式标准/每日任务总览）→ 需站长直接介入
3. Cron时间冲突仍未修（竞品内容动态14:30 vs 竞品关键词15:00）
4. R08执行闭环连续4周未解决，本质是"执行层意愿"问题降级为P2
5. 系统健康分6.9/10不变，主要受SOP跳票和Cron冲突拖累

---

# ✅ 已结项（存档参考）
DeepSeek→M3切换 | 5/27系统重构 | M3-only配置 | DDG修复 | 14+15点cron冲突修复 | SOP路径漂移修复 | auth配置修复 | 洞察驱动prompt升级(6/12) | catalog.json key注入(6/12) | 系统瘦身+结论索引(6/13)

---

# 📝 历史归档
详细客流数据 → memory/topics/visitors-20260609.md
系统演化记录 → memory/topics/system-evolution-20260612.md
每日日志 → memory/YYYY-MM-DD.md（按日期）
---

**日期基准（2026-06-15确认）**
- `Downloads/电影小镇-2026年数量统计(2).xlsx` col154=6月1日
- serial基准46174=col154（Excel日期serial，非1900起源，文件内serial=46174对应6月1日）
- ~~**2026端午=6月3日**（周二）~~ **【已废弃，正确=6月19日，见上方SSOT】**

---

---

**⛔ 端午日期SSOT（2026-06-16清理）**
- 唯一权威：`wiki/行业知识/节假日基准.md`
- **2026端午正日=6月19日（周五）**
- 放假：6/19-6/21
- 蓄水期：6/1-6/14
- 旧记录「端午=6/3」是CSV header错误标注，已废弃
- 任何端午相关分析一律读 SSOT，不查 MEMORY/CSV

---

**防错机制（2026-06-16制定，2026-06-22 强化）**
- 详细规则：`wiki/SOP/防错机制-2026-06-16.md`
- 数据源 SSOT：`wiki/行业知识/数据源清单.md`
- 节假日 SSOT：`wiki/行业知识/节假日基准.md`
- 写入前3步验证：搜索→交叉→标注来源
- 任务5步法：数据源→事实→脚本→检查→验证
- 临时脚本<30行可用heredoc；>=30行/复用脚本必须write文件
- ⚠️ **2026-06-22 事故补充规则**（**违反必究**，优先级最高）：
  - **任何对 wiki/ 大文件的"拆分/重组/迁移"操作必须先在 /tmp 做完整 dry-run + 数据完整性核对**
  - **操作前必须 grep 全文件结构**（不要假设 ## section 语义），确认所有数据归属
  - **覆盖前必须 cp 到 /tmp/backup_<日期>/**（这不是可选项，是强制项）
  - **结论索引.md 不允许任何形式的 in-place 重写**——必须先 commit 全量到 /tmp，再分段处理
  - **数据丢失立刻停止所有写入动作 + 通知站长**，不接受「先做完再总结」

---

**🚨 2026-06-22 结论索引事故（永久记录 + 8:57 完整恢复）**
- **事故**：08:41 拆分脚本误把"## 2026-06-16 防错机制上线"伪章节里的 200+ 条数据当元数据跳过，74KB → 1.7KB
- **8:57 发现 git 已启用**（6/6 wiki 漂移修复时建的），从 commit `ea541a3 vault backup: 2026-06-21 12:26:45` **完整恢复 128KB / 299 行 / 200+ 条结论** —— **数据零损失** ✅
- **根因（已修复）**：①拆分脚本误判文件结构 ②操作前未 /tmp 备份 ③任务 5 步法跳过「检查+验证」 ④脚本 60+ 行未 write 文件
- **保留**：`/tmp/backup_20260622/` 残骸（1.7KB 主文件 + 4 个错误子文件）—— 可清理
- **站长决策**（6/22 08:48）：接受损失 → **被 git 救回**
- **教训**：**再急也要先备份**；**任何"重组"操作都用 git 检查点 + apply_patch 不直接 write**

---

**🆕 2026-06-22 08:57 升级：方案 A 5 项全部完成（08:36 → 09:15，39 分钟）**
- **#1（08:58 完成）**：git 已启用，6/21 完整 backup 已恢复，事故结论已写入 MEMORY.md
- **#2（09:01 完成）**：复盘 cron prompt 拆分（生成 + 投递两步）
- **#3（09:01 完成）**：Cookie 恢复 SOP 文档
- **#4（09:15 完成）**：周日 5 cron 合并为 2 个（5 → 2 = -60% LLM 调用）
- **#5（09:08 完成）**：竞品爆款拆解 cron 加同步入库爆款公式库（archive_case.py + cron 加固）

---

**🚨 2026-06-22 15:15 heartbeat 规则强化（避免 token 浪费）**
- 之前错误：10 次 heartbeat 每次都回 "系统健康" → 浪费 ~9 次 LLM token
- **新规则**：收到 `[OpenClaw heartbeat poll]` 标记的消息 → **只回 `NO_REPLY`（单行）**，不解释
- 收到人问的真问题 → 正常回答
- SOUL.md 规则同步强化
- **预期效果**：每天省 ~10-15 次 LLM 调用 × 30-60s × token 成本

---

**🏗️ Ontology Layer 原型完成（2026-06-19 Week 6 重大里程碑）**
- [project] **Week 6 最小可行 Ontology Layer 已跑通** — SQLite 163 objects / 7 表
- [project] `scripts/ontology/` 子包上线：store/query/backfill/seed 4 模块
- [project] 14 个历史 JSON 全部回填，0 失败（+122 新增/~11 更新）
- [project] 8 个预定义查询方法 + 健康检查已就位
- [project] 完整记录见 `wiki/技术配置/Ontology架构设计/Week6_原型实现.md`
- [feedback] **adapter 双写时机：Week 7 改造 4 个 adapter，最小破坏**
- [reference] `ontology_query.py douyin` 可直接替代手写飞书日报 SQL

**Week 6 关键设计决策：**
- D-007: scripts/ontology/ 子包布局（关注点内聚）
- D-008: FIELD_MAP 字段映射（camelCase ontology → snake_case db）
- D-009: 嵌套字段 metrics.notes_count / date→publish_date 在 _map_fields 特殊处理
- D-010: "先全量回填，后续增量" 策略（不动生产 cron）

---

**🏗️ Ontology Week 1 (2026-06-24 新周期) · Object Types + Link Types 完整定义**
- [project] **ontology.json v1.2.0 升级** — Object Types 8→12, Link Types 14→33, Interfaces 3→7
- [project] **Phase 1 未完事项全部补完** — TouristSegment/Region/KnowledgeBase/Creator 4 个 OT 定义完成
- [feedback] **D-011 ID Naming Convention** — `<scope>:<type>:<value>` 三段式 + aliases 机制；**根因解决 Week 6 发现的 only_henan/only_dream 双 ID 问题**
- [feedback] **D-012 Cardinality Matrix** — 33 个 Link 全声明基数（M:N/N:1/1:N/N:M）；解决双向引用歧义
- [feedback] **D-013 KnowledgeBase 反向引用** — wiki markdown `[[objectId]]` 语法待 scanner 解析
- [feedback] **D-014 Inverse Link 显式声明** — aggregated_from ↔ contributes_to 必须双向一致
- [feedback] **D-015 Validation Rules 框架** — V-001~V-006 6 条规则，Week 2 实施 validate.py
- [project] **AgentO 覆盖率 12/14 (86%)** — 仅 Resource（多 Agent 协作时）未建模
- [project] **ScenicSpot 扩充 Tourism 属性** — +aliases/province/city/peakSeasonMonths/typicalVisitDuration/ticketPriceRange/targetAgeGroups
- [project] **MetricSnapshot 扩充异常检测属性** — +baselineValue/dailyVolatility/isAnomaly/tags
- [project] **Week 1 文档**：`Week1_ObjectTypes_LinkTypes.md`（21.7KB，14 节）+ `ontology.json` v1.2.0（35.5KB）+ 实现路线图更新

**Week 7 重点：** adapter 改造（D-008/D-011/D-015 集成）+ db migration 002（aliases/baselineValue 列扩展）+ only_henan/only_dream 双 ID 合并

---

**🏗️ Ontology Week 2 (2026-06-29 新周期) · Actions & Functions 标准化**
- [project] **ontology.json v1.3.0 升级** — Functions 7→11, Actions 5→7, Validation 6→10, Decisions 15→20
- [feedback] **D-016 Function 4 类型分类** — Pure / SideEffect / FunctionBacked / Aggregator。**治理可分级**的关键：SideEffect Function 必须经 Action 调用，**Agent Tool 不暴露 attributionScore** (避免越权写库)
- [feedback] **D-017 Action 5 层治理** — Submission→Validation→Notification→Audit→Rollback 缺一不可。任意层失败 → Action 不执行 + 写 action_log + 飞书群通知
- [feedback] **D-018 Function-backed Action 模式** — Action 治理层 + Function 业务逻辑层组合（现代 Palantir 主推）。AdjustStrategy 调 3 个 Pure Function 组合建议，比"Action 100 行"易测、复用、OSDK 友好
- [feedback] **D-019 Action Category 3 档** — lowStakes(no approval) / mediumStakes(sync notify+rollback) / highStakes(requires approval)。让 cron 任务显式选择风险等级
- [feedback] **D-020 V-007~V-010 业务规则层** — Schema 验证(V-001~V-006)≠ 业务验证(V-007~V-010)，两层互补
- [project] **Week 2 新增 4 Function** — calculateBaselineValue / detectAnomaly (FunctionBacked，配套 Week 1 派生列) / aggregateWeeklyMetrics (Aggregator) / enrichContentAsset (Pure)
- [project] **Week 2 新增 2 Action** — AdjustStrategy (mediumStakes functionBacked) / OverrideRule (highStakes，首次启用 Week 1 schema overridden_by link)
- [project] **Week 2 文档**：`Week2_Actions_Functions.md`（24.7KB，16 节）+ `ontology.json` v1.3.0（83.7KB，read+write 流程）+ 实现路线图 + 电影小镇-Ontology架构设计 同步更新
- [reference] Palantir Function-backed Action 模式参考：[CSDN 翻译 2025-11](https://blog.csdn.net/czhcc/article/details/154636416)

**Week 3 重点：** scripts/ontology/validate.py V-001~V-010 全量实施 + calculateBaselineValue/detectAnomaly 写入 MetricSnapshot 派生列 + scripts/actions/ 目录创建（function_impl + action_wrapper 拆分）

---

# W26 (2026-06-20) GitHub高星标学习 — 关键发现

**项目：** rohitg00/agentmemory (~18K stars, 2026-05-27 首版)
**它解决了什么：** AI Agent 跨会话/跨工具的共享长期记忆层（BM25+向量混合检索+LLM自动压缩），token 消耗较 Agent 内置记忆降 92%
**我们怎么用：** 解决 MEMORY.md 100行/25KB 限制 + 多 Agent（主对话/抖音日报/竞品分析）记忆碎片化问题。短期 spike 验证单 Agent 接入能否降 M3 5h 撞限频率
**不跟进的代价：** MEMORY.md 持续线性膨胀，6 个月后必然撞限丢失关键规则；多 Agent 冷启动 token 成本居高不下；竞品若用同类工具，跨任务知识复用效率比我们高 1-2 个量级

**注：** 当前 v0.9.17，3 周迭代 7 次，等 v1.0 稳定再 production。TypeScript 实现需 Node v22+ (✅已有)

---

# W27 (2026-06-24) GitHub高星标学习 — 关键发现（自纠错版）

**项目：** affaan-m/everything-claude-code（ECC）| Stars: 220,792（gh API 直查 6/24 08:03 UTC）
**它解决了什么：** Skills 生态"操作系统层"标准化 —— 跨 Claude Code/Codex/Cursor/OpenCode/Gemini/Zed/Copilot 7 大 harness 的可移植 Skills+Agents+Hooks+Memory+Verification 全栈工具链，把单点配置经验沉淀为可复用基线
**我们怎么用：** 借鉴 4 大核心组件到本系统 SKILL.md 体系（仅 7 个 vs ECC 268 个）：
1. **Memory Persistence Hooks** → 解决每次冷启动全量 read MEMORY.md 的痛点（降低 M3 5h 限额撞限频率）
2. **Verification Loops**（checkpoint vs continuous + pass@k grader）→ 给日报加"自检→告警→重跑"环节
3. **Continuous Learning** → 从历史日报自动提取爆款规律，替代站长手写公式
4. **跨平台 plugin 结构**（.claude-plugin/.cursor-plugin/.gemini-plugin/...）→ 未来切换 Agent 工具零迁移成本
**不跟进的代价：** SKILL.md 继续维持 7 个手写 Skill，跟不上 Skills 生态指数级扩张；竞品若用 ECC Continuous Learning 提取爆款规律效率比我们高 10-100 倍；日报缺失验证环，格式漂移只能等站长人肉发现

**注：** W26 上期笔记判断错误（"Skills 双雄并立"漏掉 ECC 22万星；"知识图谱赛道见顶"被 Understand-Anything 67K 反证），W27 已自纠错。**同期 anthropics/knowledge-work-plugins 21,864（Anthropic 官方）也需关注**——其 Skill 三层结构（plugin.json + mcp.json + commands/ + skills/）可能成为行业事实标准。
