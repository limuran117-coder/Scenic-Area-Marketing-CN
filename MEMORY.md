# MEMORY.md - Long-Term Memory
role: 景区营销中心总经理 | core_mission: 客流153万、营收1.2亿 | update: 2026-08-02 W32

---

# ⭐ 铁律（违反必纠）

**客流日报** 密码912530 | 5章: YTD→月度→近7日→德化街→建议 | ≤5表/卡
**飞书卡片** schema=2.0走 `scripts/send_feishu_card.py` | 表格外 `
`，表内 `
`，表头可用`⚠️` | **单卡markdown表≤5张**（超限ErrCode11310，8/13踩坑）| header.title须`{tag:plain_text,content}` | 表内不加粗/不用`>`引用（8/13实测）
**【7/2 站长纠错】数据类报告必须用 markdown 表格**：搜索指数/综合指数/同比环比/分项分解/区域TOP5/关联词等任何多列数据，禁止用 emoji+加粗列表+内联文字罗列；必须 `| 列1 | 列2 | ... |` 格式
**双通道采集** 抖音脚本+CDP交替验证
**CDP必须用Playwright** urllib/websockets连18800会超时
**数据必须读实际值** | 搜索「建业电影小镇」禁「建业华谊兄弟」
**洞察驱动** 所有分析任务必须先给结论再给数据，禁止只报数字

**【6/30 站长纠错】收官/总结卡片前必做 2 项核对**（Why: 6/30 H1 收官没看出 6/21=782 暴跌88%）：
  ① **CSV 末尾完整性** — 扫末日 N 列（≥3）是否为 0；为 0 → 标"暂态"，**不写"收官"**
  ② **节假日逐日曲线** — 暴涨/暴跌/断崖异常必须显式标注
  → How: 卡片生成前最后一步必跑 `tail -5` + 节假日逐日表两个 check

**【7/2 站长纠错】客流分析必须用 4 年均值口径**：同比必须三轨（2024/2025/2026）同时输出，**禁止仅比 2025**（Why: 2025 是异常大年，剔除2月后H1 -51.7%）→ How: 月度/季度/年报类必出 4 年×月份矩阵表 + 4年均值列

**【7/13 站长纠错】事实核查铁律**：wiki/SOP/票务系统里没记录的内容视为伪事实，必须先 read 知识库验证
**【7/23 站长纠错】双 db 路径陷阱**：`scripts/ontology/ontology.db` ≠ `.profile/ontology/ontology_store.db`（生产db）；写修复脚本前必先确认 DB_PATH
**【7/23 站长纠错】ontology_daily_work 强制收尾**：日志写入 wiki 后立即结束，不跑 verification/cross-check
**【8/6 站长纠错】剧情化包装不能编造事实**
- **Why**: 任何方案中具体年份/具体事件/具体人物/具体年代物件必须 wiki 知识库可查证，不能用修辞手法包装虚构细节
- **How**:
  - 戏剧外壳（剧本杀/对话/场景）可以保留，但具体细节必须有事实锚点
  - 资产方向可以用（如"80 年代怀旧"），具体年份必须可查证
  - "具体年份/年代物件/历史场景" 三类是事实核查重点
  - 战略/汇报方案写作前先 grep wiki/，把数据点列出来再动笔

**【7/29 站长纠错】禁止发卡自检循环**：每个 isolated session 全程最多发 1 张卡片到电影小镇群；飞书 API code=0 即视为成功，**禁止看 response.content 再判断**
  - 实证事故：7/28 竞品关键词 isolated session 03fb2625 自检循环发了 20 张刷屏
  - 防错：cron 9bf47f42 prompt 已加【发卡铁律】硬约束 + cron 7ae9127b 飞书发消息审计
**【7/25 站长决策】景区更名**：建业电影小镇 → 郑州电影小镇（双轨采集，新名优先）；历史档案保留旧名
**【7/25 易主确认】**：7/23港交所公告，建业30亿出售电影小镇+只有河南，国资（中信资本旗下信宸资本）90%控股，运营策略需重新评估
**【7/23 重要教训】v9误判**：所有"XX不存在/找不到"的判断，必须先查workspace全路径+Desktop，不能草率结论
**【7/23 spike结论】ego-lite不能替代CDP18800** | PaddleOCR可用 | crawl4ai默认headless不适合已登录dashboard

---

# 🚨 当前系统状态（2026-08-02 W32）

**模型**: M3 | 基础设施 all ✅ | cron: 30 ok / 3 err（小红书日报+竞品关键词+周二客流深度报告）
🚨 小红书采集 49 天断档（站长决策不修）| 近期工作 → `memory/2026-08-01.md`
✅ **image工具MiniMax残留已清除(8/13)**：`service-env/ai.openclaw.gateway.env` 删2行MINIMAX key + managed keys精简，gateway已restart(17809→81071)，进程/launchctl/shell全无MINIMAX。⚠️残留仅存于历史会话进程内存，新会话即干净；deepseek-v4-flash无视觉能力，截图解读仍需可用的VLM模型（待定）

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

**Ontology 进度**：W1-4 已完（v1.5.0发布，Agent集成架构确定）；W5实施：QueryHandler+LLM Translator+ActionDispatcher+Schema注入
**漂移双跑**：每周一/三/五 cron（wiki_drift_check + project_drift_check）；W32 drift: 22 issues（4 orphan raw + scripts_not_in_inventory：competitor_keyword_v8.py已归档需更新inventory）
**SOP质量系统**：W30进化审视，2个优先修复（防错机制补When字段 + 竞品分析SOP合并）
**郑州电影小镇易主**（7/23 港交所公告）：建业30亿出售，国资（中信资本旗下信宸资本）90%控股 → 运营策略需重新评估

---

# ⛔ 端午日期SSOT
唯一权威：`wiki/行业知识/节假日基准.md` | 2026端午正日=6/19（周五）| 放假 6/19-21

---

# 防错机制
- 详细：`wiki/SOP/防错机制-2026-06-16.md` | 写入3步：搜索→交叉→标注来源 | 任务5步法：源→事实→脚本→检查→验证
- ⚠️ wiki/ 大文件迁移 → 先 /tmp dry-run + 数据完整性核对 | ⚠️ 覆盖前必 cp 备份 | ⚠️ 结论索引.md 禁止 in-place 重写

---

# 已结项
DeepSeek→M3切换 | 5/27系统重构 | M3-only配置 | DDG修复 | cron冲突修复 | SOP路径漂移修复 | 6/12洞察驱动 | 6/13系统瘦身+结论索引 | 6/22方案A升级 | 6/24 cron时间表重排 | 7/2 Cookie健康+MEMORY压缩 | Ontology W1+2+3 | 7/23双db路径修复+stealth | 7/25景区更名执行 | 7/26 MEMORY二次压缩+w30维护 | **W31 MEMORY瘦身+skill3.0落地+quality gate部署**
详细履历 → `memory/topics/system-evolution-20260802.md`

---

# 📌 W32 重要发现（2026-08-02）

**【8月是年度最关键单月】**：历史最高单月绝对量，完成153万目标唯一量级窗口。7月散客占比87.9%（近春节高点），但日均仅1,699人（5月的38.7%），6月崩盘后遗症延续。

**【7/18周六3,145人】**：暑期最高单日，但原因待查（散客/团队/活动？）。

**【W32 系统审视】结论索引739条（已验证635/待验证102）| 本周新增67条 | 准确率100% | Q3淘汰检查：0条超期 | SOP质量：6个0/4分需补When触发条件**

**【周末市场观察cron偶发故障】**：12次中2次error，均非脚本本身，不修；failureAlert.after=2已配
