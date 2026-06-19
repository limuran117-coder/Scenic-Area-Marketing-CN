# MEMORY.md - Long-Term Memory
role: 景区营销中心总经理 | core_mission: 客流153万、营收1.2亿 | update: 2026-06-13

---

# ⭐ 铁律（违反必纠）

**客流日报** 密码912530 | 5章: YTD→月度→近7日→德化街→建议 | ≤5表/卡
**飞书卡片** schema=2.0走 `scripts/send_feishu_card.py` | 表格外 `

`，表内 `
`，表头可用`⚠️`
**双通道采集** 抖音脚本+CDP交替验证，任一失败走另一通道
**CDP必须用Playwright** urllib/websockets连18800会超时
**数据必须读实际值** | 搜索「建业电影小镇」禁「建业华谊兄弟」| 不限7竞品
**LLM失败不静默** 显式告警，不依赖自动fallback
**洞察驱动** 所有分析任务必须先给结论再给数据，禁止只报数字

---

# 🚨 当前系统状态（2026-06-12）

**模型**：minimax/MiniMax-M2.7（6/12从M3切换回来，无5h限额）
**auth配置**：openclaw.json有authProfile=minimax:default + 软链接agents→根目录auth-profiles.json ✅
**web_search**：minimax国内搜索 ✅
**代理**：7897 ✅ LISTEN | **CDP**：18800 ✅ LISTEN
**cookie保鲜**：抖音20:28 / 小红书10:45 ✅

**今日修复（6/12）**：
- catalog.json apiKey从env变量名→真实key ✅
- 全部32个cron洞察层prompt升级 ✅
- auth软链接缺失 ✅

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
| 2026每日 | ~/Desktop/2026游客量统计.csv（每周二更新，最新至6/9）|
| 抖音Cookie | /tmp/juLiang_cookies.json |
| 小红书Cookie | /tmp/xiaohongshu_cookies.json |
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

**防错机制（2026-06-16制定）**
- 详细规则：`wiki/SOP/防错机制-2026-06-16.md`
- 数据源 SSOT：`wiki/行业知识/数据源清单.md`
- 节假日 SSOT：`wiki/行业知识/节假日基准.md`
- 写入前3步验证：搜索→交叉→标注来源
- 任务5步法：数据源→事实→脚本→检查→验证
- 临时脚本<30行可用heredoc；>=30行/复用脚本必须write文件

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

# W26 (2026-06-20) GitHub高星标学习 — 关键发现

**项目：** rohitg00/agentmemory (~18K stars, 2026-05-27 首版)
**它解决了什么：** AI Agent 跨会话/跨工具的共享长期记忆层（BM25+向量混合检索+LLM自动压缩），token 消耗较 Agent 内置记忆降 92%
**我们怎么用：** 解决 MEMORY.md 100行/25KB 限制 + 多 Agent（主对话/抖音日报/竞品分析）记忆碎片化问题。短期 spike 验证单 Agent 接入能否降 M3 5h 撞限频率
**不跟进的代价：** MEMORY.md 持续线性膨胀，6 个月后必然撞限丢失关键规则；多 Agent 冷启动 token 成本居高不下；竞品若用同类工具，跨任务知识复用效率比我们高 1-2 个量级

**注：** 当前 v0.9.17，3 周迭代 7 次，等 v1.0 稳定再 production。TypeScript 实现需 Node v22+ (✅已有)
