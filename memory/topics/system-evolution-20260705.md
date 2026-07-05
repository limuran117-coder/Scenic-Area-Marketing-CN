# System Evolution Log W26-W27 (2026-06-20 → 2026-07-05)

**来源**：MEMORY.md 7/5 首次压缩（288→160 行），拆出历史细节存档
**备份**：/tmp/memory_backup_20260705.md（288 行 / 24KB 原始全量）

---

## W26 (2026-06-20~26) 关键发现

### GitHub 高星标学习 W26
**项目：** rohitg00/agentmemory (~18K stars, 2026-05-27 首版)
**它解决了什么：** AI Agent 跨会话/跨工具的共享长期记忆层（BM25+向量混合检索+LLM自动压缩），token 消耗较 Agent 内置记忆降 92%
**我们怎么用：** 解决 MEMORY.md 100行/25KB 限制 + 多 Agent 记忆碎片化。短期 spike 验证单 Agent 接入能否降 M3 5h 撞限频率
**不跟进的代价：** MEMORY.md 持续线性膨胀，6 个月后必然撞限丢失关键规则；多 Agent 冷启动 token 成本居高不下
**注：** v0.9.17，3 周迭代 7 次，等 v1.0 稳定再 production。TypeScript 实现需 Node v22+ (✅已有)

### Ontology Week 1 (2026-06-24) · Object Types + Link Types 完整定义
- ontology.json v1.2.0 升级 — Object Types 8→12, Link Types 14→33, Interfaces 3→7
- Phase 1 未完事项全部补完 — TouristSegment/Region/KnowledgeBase/Creator 4 个 OT 定义完成
- D-011 ID Naming Convention — `<scope>:<type>:<value>` 三段式 + aliases 机制（根因解决 only_henan/only_dream 双 ID 问题）
- D-012 Cardinality Matrix — 33 个 Link 全声明基数（M:N/N:1/1:N/N:M）；解决双向引用歧义
- D-013 KnowledgeBase 反向引用 — wiki markdown `[[objectId]]` 语法待 scanner 解析
- D-014 Inverse Link 显式声明 — aggregated_from ↔ contributes_to 必须双向一致
- D-015 Validation Rules 框架 — V-001~V-006 6 条规则，Week 2 实施 validate.py
- AgentO 覆盖率 12/14 (86%) — 仅 Resource（多 Agent 协作时）未建模
- ScenicSpot 扩充 Tourism 属性 — +aliases/province/city/peakSeasonMonths/typicalVisitDuration/ticketPriceRange/targetAgeGroups
- MetricSnapshot 扩充异常检测属性 — +baselineValue/dailyVolatility/isAnomaly/tags
- 文档：`Week1_ObjectTypes_LinkTypes.md`（21.7KB）+ `ontology.json` v1.2.0（35.5KB）

### W25 关键发现（6/21 系统进化审视）
- SOP 三件套 0/31 全齐首次发现 — When/RedFlag/Verify 覆盖率 6%/0%/10%；YAML 28/31（90%）优秀但三件套严重缺
- SOP 升级连续 3 周跳票（W23→W24→W25）— 站长需 A/B/C 三选一：A 集中突击 / B 拆分 3 天 / C 降级 H2 不做
- 基础设施断链双发 — 灵犀 not_logged_in×3日 + 抖音 my-subscript 采空×3日
- 6/8 cron 时间冲突已修（竞品 14:00→14:30；周日 9:00→9:30）
- 业务执行层脱节第 8 天 — 6/15 预警的毕业生免票+海魂衫+80 年代夜游 2.0+品牌主标识 全部未落地
- R08 执行闭环连续 5 周跳票 — 端午窗口失守已确认
- W26 新建议：`scripts/cookie_health_check.py` + cron `0 9 * * 1-5` 早于日报 2 小时发现 Cookie/账号失效

### 6/24 重要修复（3 个 cron 错同时落地）
- Cron 时间表重排（6/24 09:00-09:25 完成）：业务日报全部挪白天，间隔硬规则 ≥2h，复盘挪 23:30/23:35，Cookie 挪凌晨 00:30（周二-周六），删除已 disabled 的 Memory Dreaming
- 复盘 cron 回退单步（方案 A #2 拆分版有契约不一致 bug）：22:00 生成「业务数据」不是飞书卡片，22:05 投递必 400；6/24 已回退为「单步生成+投递」+ disable 投递 cron（736e87e1）
- prompt 修容错：「which cron && cron --version」macOS 无 cron 必失败，prompt 加容错说明
- 大文件 edit 改 write：ontology.json 35.5KB，edit 工具超时；prompt 改为 read→parse→write 流程
- `/tmp/daily_recap_<YYYY-MM-DD>.json` 旧产物（6/22-6/24 拆分版）结构是业务数据，新版本必须含 `header.title.content` + `body.elements[]`

### W24 关键发现（2026-06-14）
1. SOP 升级连续 2 周跳票（小红书日报/文旅/案例库 3 个 SOP 四件套未补）→ 建议改策略：由各 cron 自己顺便执行
2. 3 个过时 SOP 连续 3 周「待废弃」零行动（竞品深度分析流程/决策简报格式标准/每日任务总览）→ 需站长直接介入
3. Cron 时间冲突仍未修（竞品内容动态 14:30 vs 竞品关键词 15:00）
4. R08 执行闭环连续 4 周未解决，本质是「执行层意愿」问题降级为 P2
5. 系统健康分 6.9/10 不变，主要受 SOP 跳票和 Cron 冲突拖累

---

## W27 (2026-06-27~07-03) 关键发现

### GitHub 高星标学习 W27 — 自纠错版
**项目：** affaan-m/everything-claude-code（ECC）| Stars: 220,792（gh API 直查 6/24 08:03 UTC）
**它解决了什么：** Skills 生态「操作系统层」标准化 —— 跨 Claude Code/Codex/Cursor/OpenCode/Gemini/Zed/Copilot 7 大 harness 的可移植 Skills+Agents+Hooks+Memory+Verification 全栈工具链
**我们怎么用：** 借鉴 4 大核心组件到本系统 SKILL.md 体系（仅 7 个 vs ECC 268 个）：
1. Memory Persistence Hooks → 解决冷启动全量 read MEMORY.md 的痛点
2. Verification Loops（checkpoint vs continuous + pass@k grader）→ 给日报加「自检→告警→重跑」环节
3. Continuous Learning → 从历史日报自动提取爆款规律
4. 跨平台 plugin 结构（.claude-plugin/.cursor-plugin/.gemini-plugin/...）→ 未来切换 Agent 工具零迁移成本
**不跟进的代价：** SKILL.md 继续维持 7 个手写 Skill，跟不上 Skills 生态指数级扩张；日报缺失验证环，格式漂移只能等站长人肉发现
**注：** W26 上期笔记判断错误（漏掉 ECC 22 万星；漏掉 Understand-Anything 67K 反证），W27 已自纠错。同期 anthropics/knowledge-work-plugins 21,864（Anthropic 官方）也需关注。

### GitHub 高星标学习 W28 (2026-06-27)
**项目：** ChromeDevTools/chrome-devtools-mcp（44.1K stars，日增 400，Google Chrome DevTools 团队官方）
**它解决了什么：** 第一个为 AI Coding Agent 设计的浏览器控制协议——通过 MCP server 把 Chrome DevTools 能力（screenshot/console/network/trace）以工具形式暴露给 LLM agent
**我们怎么用：**
- ❌ 不能直接接管抖音/小红书采集（只支持 Google Chrome）
- ✅ 借鉴 3 点：(1) MCP 协议封装思路 → 把本系统的「采集→处理→投递」链抽象为 MCP 工具；(2) Puppeteer 自动等待策略 → 减少 30% time.sleep；(3) CLI + MCP 双入口 → 脚本同时包装为 MCP 工具供其他 agent 调用
**不跟进的代价：** MCP 已是 AI Agent 工具调用事实标准（Anthropic 4 月推 → 6 月 Google 接入 → 8 月预计 Cursor/Copilot 跟进）。本系统 56 个脚本全是 CLI/Python 调用，无 MCP 入口，1-2 年后其他 agent 想调用「采集抖音指数/读飞书群」时找不到接口。短期抖音/小红书采集脚本仍能稳定跑，MCP 化是 H2 重构话题，W28 无紧迫性
**行动：** W28-W29 spike「采集脚本出错时自动截屏诊断」流程 | H2 评估脚本 MCP 化试点

### GitHub 高星标学习 W29 (2026-07-04)
**项目：** thedotmack/claude-mem（85.7K stars，2025-08-31 首版，OpenClaw 原生支持）
**它解决了什么：** 填补「AI Agent 持久记忆层操作系统」的空白——自动捕获会话→LLM 压缩摘要→SQLite+ChromaDB 索引→MCP 注入新会话；专门为 OpenClaw/Claude Code 设计，提供一键安装和 8 个 MCP search tool
**我们怎么用：** 直接对位本系统 7 大痛点——① MEMORY.md 100 行/25KB 限制 ② 28 个 cron 各自维护 memory 目录 ③ 飞书卡片格式漂移靠人肉发现 ④ LLM 失败时冷启动 token 居高不下 ⑤ 6/22 结论索引事故 1.7KB 丢失教训 ⑥ 跨任务知识无法复用 ⑦ 无 MCP 接口对外暴露能力
**行动：** **W29 本周 spike** 一键安装 → 验证 8 个 MCP search tool → 成功则 W29-W30 把 32 个 cron 接入 worker service
**预期效果：** 冷启动 token 降 60%+

### Ontology Week 2 (2026-06-29 新周期) · Actions & Functions 标准化
- ontology.json v1.3.0 升级 — Functions 7→11, Actions 5→7, Validation 6→10, Decisions 15→20
- D-016 Function 4 类型分类 — Pure / SideEffect / FunctionBacked / Aggregator。**治理可分级**的关键：SideEffect Function 必须经 Action 调用，Agent Tool 不暴露 attributionScore
- D-017 Action 5 层治理 — Submission→Validation→Notification→Audit→Rollback 缺一不可
- D-018 Function-backed Action 模式 — Action 治理层 + Function 业务逻辑层组合（现代 Palantir 主推）
- D-019 Action Category 3 档 — lowStakes(no approval) / mediumStakes(sync notify+rollback) / highStakes(requires approval)
- D-020 V-007~V-010 业务规则层 — Schema 验证(V-001~V-006)≠ 业务验证(V-007~V-010)
- Week 2 新增 4 Function — calculateBaselineValue / detectAnomaly (FunctionBacked) / aggregateWeeklyMetrics (Aggregator) / enrichContentAsset (Pure)
- Week 2 新增 2 Action — AdjustStrategy (mediumStakes functionBacked) / OverrideRule (highStakes，首次启用 Week 1 schema overridden_by link)
- 文档：`Week2_Actions_Functions.md`（24.7KB，16 节）+ `ontology.json` v1.3.0（83.7KB，read+write 流程）

### Week 3 重点
- scripts/ontology/validate.py V-001~V-010 全量实施
- calculateBaselineValue/detectAnomaly 写入 MetricSnapshot 派生列
- scripts/actions/ 目录创建（function_impl + action_wrapper 拆分）

### Ontology 原型 Week 6 完成 (2026-06-19)
- SQLite 163 objects / 7 表
- scripts/ontology/ 子包上线：store/query/backfill/seed 4 模块
- 14 个历史 JSON 全部回填，0 失败（+122 新增/~11 更新）
- 8 个预定义查询方法 + 健康检查已就位
- 完整记录见 `wiki/技术配置/Ontology架构设计/Week6_原型实现.md`

### Ontology 关键设计决策（Week 6 → Week 1 → Week 2）
- D-007: scripts/ontology/ 子包布局（关注点内聚）
- D-008: FIELD_MAP 字段映射（camelCase ontology → snake_case db）
- D-009: 嵌套字段 metrics.notes_count / date→publish_date 在 _map_fields 特殊处理
- D-010: 「先全量回填，后续增量」策略（不动生产 cron）

### scripts/ontology/dedup 迁移（2026-07-03）
- migrations/20260703_dedup_scenic_spots.py 上线
- snapshots/ontology_store.pre_dedup_20260703.db（241KB）保留
- 解决 ScenicSpot 多 ID 重复

### 7/2 站长纠错：数据类报告必须用 markdown 表格
- 抖音日报 8 景区数据用 🥇🥈🥉+加粗+文字描述发出去，视觉扫描成本 > 5 秒
- 强制：搜索指数/综合指数/同比环比/分项分解/区域 TOP5/关联词等任何多列数据必须 markdown 表格
- 已写入铁律区

### 7/2 站长纠错：客流分析必须用 4 年均值口径
- 单一 2025 对比会失真（2025 是异常大年）
- 任何同比必须三轨（2024/2025/2026）同时输出
- 已写入铁律区

---

## 历史已结项（W26 之前）
DeepSeek→M3 切换 | 5/27 系统重构 | M3-only 配置 | DDG 修复 | 14+15 点 cron 冲突修复 | SOP 路径漂移修复 | auth 配置修复 | 洞察驱动 prompt 升级(6/12) | catalog.json key 注入(6/12) | 系统瘦身+结论索引(6/13)