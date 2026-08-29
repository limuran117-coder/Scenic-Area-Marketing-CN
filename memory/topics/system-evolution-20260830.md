# System Evolution Notes — 2026-08-30 压缩归档

> 从 MEMORY.md 压缩移出的历史周度细节（W33 全量 + W34 冗余项）。
> MEMORY.md 中保留的精简指针指向本节。

## 🧬 W33 记忆提炼（8/10-8/14）

**[project] 系统级重构（8/10）**：MiniMax彻底清除0残留→全deepseek | web_search searxng恢复 | Ontology双库打通（生产库465指标+图谱486实体/507关系）| 全链路采集→SQLite→图谱→NL查询闭环 | 新增cron：图谱自检(周一09:00)、知识进化引擎(周日11:00)、周度竞品周报已接图谱快照

**[project] cron治理机制（8/12）**：`scripts/cron_governor.py` 每日哨兵(10:30静默)+每周治理(周日08:15自动apply,≤1卡) | 轻量探针白名单不参与提超时 | 教训：测试新脚本前确保无发卡逻辑（8/12误发2张测试卡已撤回）

**视觉模型（8/13）**：MiniMax VLM坏key→站长否决付费阿里云→Ollama本地 qwen3-vl:8b（6.1GB免费）替代image工具截图解读。遗留：deepseek-v4-flash无视觉，三分解读/年龄分布仍"采集中"待VLM

**⚠️ 抖音指数日报cron连续失败链（8/11-8/14）**：采集脚本正常（9/9有效），LLM生成阶段超时/abort；8/14错峰07:00入低谷窗口（DeepSeek低谷00:30-08:30）——8/15观察验证，若仍失败需换模型/加超时

**[validation] 清明上河园 search_index 32万非脏数据**：抖音指数量级真实差异（全国知名vs电影小镇3千），已核实

**8/13全案迭代踩坑**：链式replace编号导致多米诺错乱→用占位符单遍替换；删卡残留div不平衡→栈扫描定位；Apple扁平化重做+dom数验证（section/table/div闭合）。**营收口径涉及收费先问站长是否额外收费**（818→去参赛费→纯门票698/560万）

**【周末市场观察cron偶发故障】**：12次中2次error，均非脚本本身，不修；failureAlert.after=2已配

**【万圣立项「与傩共舞·撕名牌大作战」最终口径（8/13）】**：傩舞非遗×撕名牌，10.8国庆后无缝隙接完胜档至10月底。**入园即参与不额外收费，收入只有门票**。副标题「傩面一戴·请神开撕」/「傩神附体·撕就对了」。**营收基准=560万**（万圣档8万客流×69.8；纯门票，中标10万→698万）。**目标体系：10月整月14-17万（力争18万冲132）| 国庆档8-10万 | 万圣档6-8万 | 全年123万**。**玩法=NPC阵营资格制**（四营：钟馗/判官/方相氏/雷神；男可撕/女授印；营主点将≤80人；千人面具共舞）。源码：`~/Desktop/傩战万圣方案/终版.html`(80K,15章,Apple扁平) + `output/...全案.html/pdf`。营收演进898→818→698→560万（删二销/去参赛费）。KPI：开档首周参与≥8,000（对标历年10月平日客流，勿用1.5万）

## 🧬 W34 冗余项（同步压缩移出）

**Graphiti 本地耗时序知识图谱落地（8/19）完整细节**：GitHub 5项目对比（AutoResearch需GPU/RAGFlow太重/Unsloth仅N卡/Milvus重复）→Graphiti唯一闭环可行。架构=DeepSeek(json_object)+Ollama bge-m3+FalkorDB+graphiti-core 0.29.3，零OpenAI依赖。本地化踩坑：macOS系统代理7897劫持Python客户端→trust_env=False；group_id=FalkorDB库名；volume挂/var/lib/falkordb/data。Ontology→Graphiti打通(sync_ontology.py)+OllamaReranker(bge-m3余弦重排)。**能力边界：只存实体间关系边(RELATES_TO)，单实体数值只产生MENTIONS边检索不到→数值型日报走Excel/CSV，Graphiti只存关系型洞察**。cron「Graphiti-Ontology同步」每周二06:30。详见 memory/2026-08-19.md（此细节与 MEMORY.md 铁律区架构段重复，压缩时移入本节）

**searxng docker代理坑（8/18）**：容器bridge网络127.0.0.1≠宿主机→代理改host.docker.internal:7897；禁用不可达引擎(google cse/wikipedia/wikidata)；否则web_search全0→依赖搜索cron连败

**竞品内容动态cron超时治理（8/20）**：6连败timeout@900s→timeout 1500(对齐兄弟任务)+schedule 0:8→7:30错峰双保险

**9月方案×德化街分析（8/22）**：8万冲9万客流(+167%)/578冲650万收入/广告190万。风险：目标跳档/平日排期错配(权重0.6458场)/广告ROI30%/年卡定价互斥。老式.xls用xlrd解析(textutil转txt提取docx)

---
*归档于 2026-08-30 周日维护（MEMORY.md 压缩）*
