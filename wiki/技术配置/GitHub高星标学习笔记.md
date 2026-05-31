# GitHub高星标项目研究笔记

> 更新：2026-05-31（W22末·周日补充）| 采集：web_search + presenc.ai + shareuhack + ecoaai + pasqualepillitteri综合 | 下期：周六00:00

---

## 一、2026年5月末 Top 25 AI Agent 框架星标排名

**数据来源：** presenc.ai/pasqualepillitteri，数据截至2026-05-24~31

| # | 项目 | ⭐ Stars | 语言 | 类型 | 备注 |
|:-:|------|:--------:|:----:|:----:|------|
| 1 | **n8n** | **187,791** | TypeScript | 工作流+Agent | 🔺 新登顶，原无代码工作流引擎+LLM节点 |
| 2 | **AutoGPT** | 184,295 | Python | 自主Agent先驱 | 历史存量高，增速放缓 |
| 3 | **LangChain** | 136,707 | Python | 基础Agent工程平台 | |
| 4 | **mattpocock/skills** | **112,551** | Shell | 🆕 Agent Skills合集 | 🔥 月增71K⭐，Skills生态最火项目 |
| 5 | **Gemini CLI** | 100,337 | TypeScript | Google终端AI Agent | |
| 6 | **browser-use** | **93,857** | Python | 浏览器自动化Agent | 🔺 1周增约8K⭐，维持高速增长 |
| 7 | **RAGFlow** | 77,200 | Python | RAG+Agent融合引擎 | |
| 8 | **TradingAgents** | 74,383 | Python | 多Agent交易框架 | 持续月增长 |
| 9 | **LobeHub** | 74,778 | TypeScript | 多Agent协作平台 | |
| 10 | **MetaGPT** | 66,673 | Python | 多Agent软件公司模拟 | |
| 11 | **Cline** | **61,755** | TypeScript | 🆕 Coding Agent IDE | 🔺 新进Top20，月增显著 |
| 12 | **AutoGen (MS)** | 58,025 | Python | 微软多Agent框架 | |
| 13 | **Flowise** | 52,810 | TypeScript | 无代码Agent构建 | |
| 14 | **CrewAI** | 51,380 | Python | 角色扮演Agent协作 | |
| 15 | **Mem0** | 52,047 | Python | 通用记忆层 | 增速放缓但稳定 |
| 16 | **LlamaIndex** | 49,399 | Python | RAG编排框架 | |
| 17 | **LiteLLM** | 46,932 | Python | LLM路由/代理 | 🔺 增长中 |
| 18 | **Aider** | 44,796 | Python | 终端Coding Agent | |
| 19 | **LocalAI** | 44,938 | Go | 本地模型引擎 | |
| 20 | **Agno (原Phidata)** | 40,118 | Python | Agent规模化部署 | |
| 21 | **Understand-Anything** | **46,328** | TypeScript | 🆕 代码知识图谱 | 🔥 月增36K⭐ |
| 22 | **ruflo** | **56,746** | TypeScript | 🆕 Claude多Agent编排 | 🔺 月增23K⭐ |
| 23 | **DSPy** | 34,408 | Python | 编程式LLM编排 | |
| 24 | **LangGraph** | 32,027 | Python | 状态化Agent编排 | |
| 25 | **semantic-kernel** | 27,902 | C# | 微软企业Agent框架 | |

### ⚡ 5月最大月度增长项目

| 项目 | 月增⭐ | 总⭐ | 说明 |
|------|:------:|:----:|------|
| **mattpocock/skills** | +71,266 | 112,551 | **月增长冠军**，Skills生态标杆 |
| **multica-ai/andrej-karpathy-skills** | +65,076 | 162,798 | Karpathy编码准则作为CLAUDE.md分发 |
| **Understand-Anything** | +36,047 | 46,328 | 代码知识图谱交互工具 |
| **codegraph** | +33,455 | 34,658 | 预索引代码知识图，减少token消耗 |
| **ruflo** | +23,037 | 56,746 | Claude多Agent swarm编排 |
| **CloakBrowser** | +21,160 | 22,694 | 防检测的Stealth Chromium |
| **agentmemory (rohitg00)** | +17,789 | 20,012 | 持久化Agent编码记忆 |
| **9router** | +11,936 | 15,293 | 免费AI编码路由代理 |
| **Pixelle-Video** | +13,102 | 20,616 | AI全自动短视频引擎 |

## 二、本周（5月第4周末，数据截至5/24-31）增长最快的项目

根据GitHub Trending周榜最新数据（pasqualepillitteri, 5/24采集）：

| # | 项目 | 周增⭐ | 总⭐ | 亮点 |
|:-:|------|:------:|:----:|------|
| 1 | **openhuman** | +17,100 | 26,795 | Rust写的私人AI，完全本地化运行，GPL-3.0 |
| 2 | **codegraph** | +14,100 | 34,658 | 预索引代码知识图谱，给Claude Code/Codex用 |
| 3 | **academic-research-skills** | +11,600 | 20,268 | Claude Code学术研究Skills合集 |
| 4 | **RuView** | +6,800 | 65,107 | WiFi信号实现空间智能感知（非纯AI Agent） |
| 5 | **Understand-Anything** | ~+6,000 | 46,328 | 代码知识图谱交互式探索 |

> 注：5月13日那周的DeepSeek-TUI (+21K)、agent-skills (+11.7K)、anthropics/financial-services (+12K) 等项目的增量已基本被新项目超越，说明轮动节奏快。

### ⚡ 本周新兴项目

- **openhuman**（tinyhumansai）：Rust全栈私人AI，含Web搜索/爬虫/编码/STT/TTS/桌面萌宠，GPL-3.0，代表**本地私有AI**浪潮
- **academic-research-skills**（Imbad0202）：Claude Code学术研究全流程Skills（文献检索→论文写作→同行评审→投稿）
- **codegraph**（colbymchenry）：TypeScript实现的代码知识图MCP server，减少Claude Code 40%+ token消耗，100%本地运行
- **agentmemory**（rohitg00）：持久化编码Agent记忆，TypeScript，对标Mem0但专注编码Agent场景

## 三、对比上期（5/24）差异 & vs vs上上期（5/17）对比

### 🔺 新增高星标项目

| 项目 | ⭐ | 类型 | 为何上期遗漏 |
|------|:---:|:----:|:-----------:|
| n8n | 187K | 工作流+LLM | 归类为"工具"而非"Agent框架" |
| mattpocock/skills | 112K | Skills合集 | 月增太猛，上期未发现 |
| multica-ai/andrej-karpathy-skills | 162K | Skills+Karpathy准则 | 同上，Skills生态大爆发 |
| Cline | 61K | Coding Agent IDE | 上期只关注传统框架 |
| Understand-Anything | 46K | 代码知识图谱 | 5月才爆发 |
| codegraph | 34K | 代码知识图MCP | 同上 |
| ruflo | 56K | Claude多Agent编排 | 5月持续增长 |
| openhuman | 26K | 本地私人AI | 本周新上榜 |
| academic-research-skills | 20K | 学术Skills | 本周新上榜 |
| agentmemory | 20K | 编码Agent记忆 | 5月上线新项目 |

### 📈 星标变化显著的项目

| 项目 | 上期(5/24) | 本期(5/31) | 变化 | 趋势 |
|------|:---------:|:---------:|:----:|:----:|
| browser-use | 86,000 | 93,857 | +7,857 | 📈 高速增长 |
| CrewAI | 48,000 | 51,380 | +3,380 | 📈 稳定增长 |
| Cline | — | 61,755 | 新进 | 🔥 IDE Agent爆发 |
| Mem0 | 52,000 | 52,047 | +47 | ➡️ 趋平 |
| LangChain | 132,000 | 136,707 | +4,707 | 📈 稳健 |
| n8n | — | 187,791 | 新进 | 🔥 工作流Agent化 |
| TradingAgents | 74,383 | ~74,000+ | 略有增长 | ➡️ 持续但放缓 |

### 📊 分类维度变化

| 类别 | 领跑者 | ⭐ | 势头 |
|------|--------|:--:|:----:|
| 通用编排 | LangChain | 136K | 稳固基本盘 |
| Coding Agent | Cline | 61K | 🔥 18个月62K，增速惊人 |
| 浏览器自动化 | browser-use | 93K | ⚡ 18个月到94K，史上最快之一 |
| 可视/无代码工作流 | n8n | 187K | 🔥 Agent=工作流+LLM节点 |
| 记忆/状态化 | Letta | 22K | ➡️ niche但稳定 |
| 路由/代理 | LiteLLM | 46K | 📈 增长中 |
| Skills生态 | mattpocock/skills | 112K | 🔥🔥 本月最大亮点 |

## 🔥 新增重要发现 — 深度分析（5月31日周日补充）

以下项目在初版笔记（5月24/31日初版）中未收录或信息不完整，本周日补充调研后发现极具价值。

### 发现一：Caveman（65,181⭐）— Token效率革命

**仓库：** JuliusBrussee/caveman | **语言：** JavaScript | **上线：** 2026-04-04

2026年4-5月最爆发的项目，**45行JS实现prompt极简化压缩**，将冗长的prompt压缩为极简的"原始人语"：

> 示例：`"I would like you to carefully review the following Python code and provide a comprehensive analysis of its security vulnerabilities with specific line references"`
> → `"review py code. find vulns. line numbers."`

**效果：平均减token 65%**，代码审查类任务从2,847→998 tokens。对技术性任务（代码审查、debug、shell命令）几乎没有质量损失，但对创意写作类任务有损失。

**对本系统的直接价值：** ⭐⭐⭐⭐⭐
- 日报/分析类任务的prompt可直接应用类似压缩策略
- 日报生成占token消耗大头，65% reduction = 直接节省65% API费用
- 实现思路极其简单（45行JS），可作为独立skill集成

### 发现二：MemPalace（52,880⭐）— 新一代记忆系统王者

**仓库：** MemPalace/mempalace | **语言：** Python | **上线：** 2026年

在MTEB Memory Benchmark上全面超越Mem0的新记忆系统：

| 指标 | MemPalace | Mem0 | LangMem | Chroma RAG |
|:-----|:---------:|:----:|:-------:|:----------:|
| Recall@5 | **93.2%** | 87.1% | 81.4% | 79.8% |
| Precision@5 | **91.8%** | 84.3% | 78.9% | 82.1% |
| 延迟(ms) | 47 | 8 | 212 | 463 |
| 每session内存 | **2.1MB** | 4.8MB | 8.3MB | 3.2MB |

**架构亮点：** 三级记忆体系（工作记忆/情节记忆/语义记忆）+ MCP原生集成。值得本系统memory架构升级时参考。

### 发现三：Claude+Obsidian（5,591⭐）— Wiki模式验证

Karpathy LLM Wiki模式在Obsidian中的实现。Claude对话自动丰富持久知识库。
**与本系统wiki体系思路完全一致**，验证了我们当前的wiki架构方向正确。

### 发现四：OpenSquilla（1,964⭐）— 推理效率优化

优化Agent内部推理循环结构，等token预算下任务完成率提高22%。
**提示：token效率不仅仅是prompt压缩，内部推理结构同样有优化空间。**

---

## 四、与当前系统对比分析

### 🔗 直接可借鉴的项目

| 项目 | 相关度 | 借鉴内容 |
|------|:------:|---------|
| **Caveman (65K⭐)** | ⭐⭐⭐⭐⭐ | Token压缩 → 日报prompt应用压缩策略，节省65% API费用 |
| **mattpocock/skills (112K⭐)** | ⭐⭐⭐⭐⭐ | Skills独立分发模式 → SKILL.md+SOP体系独立为文旅Agent Skill包 |
| **codegraph (34K⭐)** | ⭐⭐⭐⭐⭐ | 代码知识图MCP → 搭建景区专有知识图（政策/历史/客流/竞品） |
| **MemPalace (52K⭐)** | ⭐⭐⭐⭐ | 多级记忆体系 → 升级MEMORY.md架构参考（三位一体记忆） |
| **agentmemory (20K⭐)** | ⭐⭐⭐⭐ | 编码Agent持久记忆 → 跨session状态保持 |
| **academic-research-skills (20K⭐)** | ⭐⭐⭐⭐ | 垂直领域Skills → 验证文旅Agent Skill包模式可行 |
| **Claude+Obsidian (5.5K⭐)** | ⭐⭐⭐⭐ | Wiki模式 → 验证当前wiki架构方向正确 |
| **openhuman (26K⭐)** | ⭐⭐⭐ | 全栈本地AI → Ollama+本地知识库备选方案 |
| **OpenSquilla (1.9K⭐)** | ⭐⭐⭐ | 推理效率优化 → 可研究内部推理循环优化 |
| **Understand-Anything (46K⭐)** | ⭐⭐⭐ | 知识图谱交互 → 景区数据可视化 |
| **ruflo (56K⭐)** | ⭐⭐⭐ | Claude多Agent swarm → A+B+C架构升级参考 |

### 🆚 本系统已覆盖的能力 → 再加强

| 能力 | 现状 | 对标项目 | 优化方向 |
|------|:----:|:---------:|:---------|
| Skills体系 | ✅ 有SKILL.md | agent-skills / mattpocock | 参考Skills独立分发/版本管理 |
| Token效率 | ❌ 未系统优化 | **Caveman** | 🆕 **新增最高优先级：** 引入prompt压缩策略 |
| 多Agent协作 | ✅ A+B+C | CrewAI / ruflo | 评估是否引入swarm模式 |
| 记忆系统 | ✅ MEMORY.md+memory/ | **MemPalace** / Mem0 | 🆕 **升级为三级记忆体系参考MemPalace** |
| 浏览器自动化 | ✅ Playwright+CDP | browser-use | 已验证充分 |
| 代码知识图 | ❌ 空白 | codegraph / Understand-Anything | 🆕 **最大架构优化空间** |
| Wiki知识库 | ✅ 有wiki/ | Claude+Obsidian | 验证方向正确，可强化自动循环 |

### 🆕 新增发现 — 值得尝试（较上期更新）

1. **Caveman（65K⭐）— Token压缩** — 最简单的降本手段。日报生成前先做prompt极简压缩，预计降50-65% token消耗。实现成本极低（参考其45行JS），收益立即见效
2. **Skills垂直化验证** — mattpocock/skills（112K）+ academic-research-skills（20K）+ 金融Skills（28K）+ Karpathy Skills（162K）全面爆发 → 文旅垂直Skill包有先发机会
3. **代码知识图谱是全新赛道** — codegraph和Understand-Anything爆发说明**预索引上下文**是降低token消耗的关键手段
4. **记忆层新竞品** — MemPalace（52K）定位超越Mem0，叠加agentmemory（20K）+ Letta（22K），记忆层独立化趋势更明确
5. **Cline（61K）** — IDE Coding Agent崛起 → 可关注IDE端Agent（Cursor/Cline）作为未来交互入口

## 五、趋势判断（更新至2026年5月末）

| 趋势 | 表现指标 | 对本系统影响 |
|------|---------|:-----------:|
| **Token效率革命** | Caveman(65K)+OpenSquilla+codegraph | 🆕 **最高优先级行动项**，直接降API成本50%+ |
| **Skills生态大爆发** | mattpocock/skills月增71K + academic-research-skills周增11K | ✅ SKILL.md模式正确，可进一步独立化版本化 |
| **代码知识图谱标准化** | codegraph(34K)+Understand-Anything(46K) | 🆕 **高优先级探索**，直接提升日报/分析效率 |
| **Agent记忆层独立** | MemPalace(52K,新王)+Mem0(52K)+Letta(22K)+agentmemory(20K) | ⚠️ 可升级memory架构为嵌入索引+三级记忆 |
| **Agent生态框架化** | n8n(187K)登顶·工作流=Agent | ✅ 方向正确，但无需切换底层框架 |
| **本地私有AI回归** | openhuman(26K)·全栈本地·GPL-3.0 | ⚠️ 可备选探索，非当前刚需 |
| **Coding Agent IDE化** | Cline(61K,18个月)+Aider(44K) | ℹ️ 远期影响，暂不调整 |
| **无代码Agent构建** | n8n+Flowise+Dify占Top5三席 | ❌ 暂无需跟进，脚本化方案更适配报表需求 |
| **垂直Agent Skill包** | 学术+金融+Karpathy Skills均已出现 | ✅ **文旅垂直Skill包具有先发机会** |

### 🎯 对电影小镇Agent架构的核心启示

1. **立即执行：** 引入**prompt压缩策略**（Caveman模式），在日报生成前压缩prompt，预计减少50-65% token消耗，对应API费用立减
2. **短期（本周内可执行）：** 搭建景区运营**知识图**（codegraph模式）——政策文件、历史客流、竞品数据预索引，日报中的搜索/读取操作直接query语义索引
3. **中期（可规划）：** 升级memory架构为**三级记忆体系**（MemPalace模式）——工作记忆/情节记忆/语义记忆
4. **长期（可探索）：** 将SKILL.md+SOP体系独立为**文旅Agent Skill包**——包括抖音指数分析、竞品追踪、客流分析、日报生成等垂直技能，独立版本管理

---

**关联文件：**
- MEMORY.md → 记忆系统架构
- wiki/SOP/ → 当前SOP体系，可升级为独立Skill包
- wiki/技术配置/ → 相关技术参考
- 上期记录：本文档前身（2026-05-24版本）
