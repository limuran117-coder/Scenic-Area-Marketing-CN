# System Evolution Notes — 2026-09-13 压缩归档

> 从 MEMORY.md 压缩移出的 W31-W37 历史细节（主要为 W35-W37 周度细节）。
> MEMORY.md 保留的精简指针指向本节。源：memory/2026-08-30.md ~ 2026-09-12.md。

## 🧬 W35 细节（8/24-8/30）

**8/24 站长重点（二期北地块）**：片场 vs 幻城核心主张；《织女北上》被否→换《大喇叭》；8/28 V6 评审 4 处待处理（壹章"国资入主更名"硬伤/竞品表漏清明上河园/未交代时间轴/夏季隐藏式空调）。

**8/25 周客流脚本观测**：weekly_visitor_report.py E4/E5 硬编码 6 月静态字符串（行 690-712），周报行动建议与 8 月实际（+43% 复苏）矛盾。9/1 用 (19) 重跑输出已正确（本周 4,428/天 vs 上周 6,910 vs 去年 7,815），未再复现 → 假设关闭（见 MEMORY 过期声明）。

**8/27-8/28 情歌夜验证**：周六情歌夜常设化立项。

**8/30 周日维护**：MEMORY.md 压缩（192行/24KB → 161行/20KB），归档 W33 全量 + W34 冗余项 → `system-evolution-20260830.md`。

**W35 知识进化引擎（08-30 07:30）**：结论库 已验证 909 / 待验证 186 / 已推翻 222；新增决策规则 2（R09 客流双峰、R10 清园资本代差）；15 条待验证候选无干净数据支持→全部保持待验证。

**W35 cron 每周治理（08-30）**：25/32 正常（78%），限流高峰 7:00+8:00（贡献 25 次错误）；建议错峰 3 个清早任务 + 提升 2 个 timeout；需人工核查营销日历/文旅营销案例。

## 🧬 W36 细节（8/31-9/6）

**8/31 营销日历 W37**：暑期末班→开学过渡周；9/5 情歌夜常设化 DAY1；验证器 2 条 warning 为误报。

**8/31 Ontology 图谱自检**：⚠️ warning（退出码 1），图谱健康但 11 天无写入；实体 513 | 关系 526。

**9/1 月度复盘 SSOT**：8 月日均 4,598=6 月 3.2 倍；YTD 至 8/17=853,180=69.4%；🚨 CSV(18) 只到 8/17，黄金两周不可归因。

**9/1 站长确认新数据 + 列解析纠错（重要教训）**：站长告知 (19).csv 为最新（08:41 上传）；我上午**解析列错位一天**（误报至 8/29），站长指出后深查，正确映射 **idx2=1/1**（锚点：2025元旦 8,034 / 8/15=10,327 / 8/16=9,036 三重验证）→ 修正为至 8/30（周日 3,612）。YTD 932,551（75.8%）/ 闸机 969,779 / 收入 74.89M。8/22（周六）9,706 为 8 月下旬峰值。→ 已固化为 MEMORY 铁律「CSV 列解析锚点三重验证」。

**9/1 dashboard 脚本清理**：dashboard.py(17) / build_dashboard.py(Desktop+(2)) 硬编码旧文件名，均无 cron 引用 → 移入 scripts/archive/；同步更新 3 处清单。

**9/3 新招法**：方特森林中秋夜案例（提前 3 周抢注中秋夜游搜索词）。

**W36 GitHub 学习（9/5，OptMem）**：VictorTaelin/OptMem（1.5K⭐，426-token prompt+单文件零依赖 Python，全量 LOG 只追加+摘要可重建缓存）→ P2 借鉴「LOG 只追加+摘要只是可重建缓存」治理 MEMORY.md 超限。

**9/6 周度记忆提炼（W37）**：MEMORY.md 增量 6 处；已验证「8 月黄金两周断档」= 解析列偏移+CSV 未及时更新（非真断档）。

## 🧬 W37 细节（9/6 系统维护 + 9/7-9/12）

**9/6 系统维护发现**：
- 🔴 cron_governor.py 哨兵 schema 断裂（9/4 起）：硬编码 SELECT 含 payload_model/delete_after_run 旧列，9 月 DB 迁移后 schema 变更 → 哨兵空转、对 cron 漂移盲视。修复方向：查新版 cron_jobs 真实列后改 SELECT；DB_PATH=~/.openclaw/state/openclaw.sqlite live 迁移库不可盲改。
- 🟠 git push 失败：github.com 经 127.0.0.1:7897 SSL_ERROR_SYSCALL（curl code 000），commit 本地落待推。
- 🟡 memory/2026-09-04.md 与 2026-09-05.md 日档缺失；feishu_audit total_ai_messages=0 待核。
- 9/6 周治理：修复 governor schema 漂移（job_json/receipts 迁移）+ auto 应用 1 项 timeout 提升；92.9% 成功率。

**9/7 图谱自检 critical**：graph.jsonl 18 天无写入（最后 8/19），根因=上游断粮（小红书每日采集 cron 未挂 + adapter-douyin 停摆）非故障。

**9/8 周二客流深度报告**：⚠️ `/tmp/xlsxenv` 虚拟环境丢失（macOS /tmp 重启清空）→ 已重建（pandas/openpyxl/requests）。教训：/tmp 非持久，脚本 PYTHON 硬编码该路径。

**9/8 周度客流洞察**：无新周数据，SSOT 仍 (19) 至 8/30，8/31-9/7 空窗 8 天；W35(8/24-30) 30,999 门票 vs W34 48,372=↓36%。

**9/8-9/9 心跳轮系统告警**：
- 9/5 Gateway 重启更新错误（managed-service-handoff-failed）→ 根因=版本升级后 6 插件未同步+未重启。修复命令（未代执行，需站长手跑）：`openclaw plugins update @openclaw/{lobster,memory-lancedb,openshell-sandbox,searxng-plugin,tokenjuice,voice-call}@2026.9.1` + `openclaw gateway restart`。
- 次要：2 workspace skill 缺 description（仅警告）；AGENTS.md 26.8KB 超限截断 29%（已知）。

**9/10 文旅营销案例 cron error**：`Inline API key for provider "deepseek" is temporarily disabled after a provider auth/billing failure`（约 6 分钟后可重试）——本周唯一 LLM 层故障，非持久。

**9/11 CDP 三层故障 + cdp_restore_tabs 重写**：Chrome 152 上 Playwright `connect_over_cdp` 握手 stall；`PUT /json/new` 挂死整个 CDP HTTP 服务（约 45s 自愈）→ 重写 `cdp_restore_tabs.py` 为 CDP WebSocket + `Target.createTarget`（websockets 16.0，无 Playwright），7 标签恢复在位。

**9/11 searxng 外部检索链断档**：全查询归零，根因=baidu 引擎 CAPTCHA 查封；仅 360 可取存量无时间过滤结果 → 舆情/竞品内容动态/爆款拆解三链路进入「存量证据块+如实上报」模式。

**9/12 wiki 大治理（站长发起）**：18→16 顶层目录重组、补齐 10 个末级目录索引（全库导航 100% 覆盖）、结论索引.md 由 530KB 流水账拆为分册+索引层（写入契约=任务只追加自己分册）、固化治理规则 R1-R7 写入 `wiki/schema/rules.md`。

**W37 GitHub 学习（9/12）**：`lennney/stop-that-shit` + `Leonxlnx/unlazy` + `Spielewoy/autoprompt-skill` 三仓库同月爆发=「纪律层」新赛道；`tigerless-labs/agent-memory` 与 OptMem 同源收敛 → P0=把 Token 守则硬规则升级为可执行前置检查脚本。

**9/1 月度复盘 SSOT 口径**：见上 9/1 段（已合并）。
