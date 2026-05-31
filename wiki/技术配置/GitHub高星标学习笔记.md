# GitHub高星标项目研究笔记

> 更新：2026-05-31（W22末）| 采集：web_search + presenc.ai + shareuhack综合 | 下期：周六00:00

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

- **openhuman**（tinyhumansai）：Rust全栈私人AI，含Web搜索/爬虫/编码/STT/TTS/桌面萌宠 — "personal super-intelligence"，GPL-3.0协议，代表了**本地私有AI**浪潮
- **academic-research-skills**（Imbad0202）：Claude Code的学术研究全流程Skills（文献检索→论文写作→同行评审→投稿），博士群体推动
- **codegraph**（colbymchenry）：TypeScript实现的代码知识图MCP server，减少Claude Code 40%+ token消耗，100%本地运行
- **agentmemory**（rohitg00）：持久化编码Agent记忆，TypeScript，对标Mem0但专注编码Agent场景

## 三、对比上期（5/24）的差异

### 🔺 新增高星标项目（上期未收录）

| 项目 | ⭐ | 类型 | 为何上期遗漏 |
|------|:---:|:----:|:-----------:|
| n8n | 187K | 工作流+LLM | 归类为"工具"而非"Agent框架"，presenc.ai才把它算入 |
| mattpocock/skills | 112K | Skills合集 | 月增太猛，上期未发现 |
| multica-ai/andrej-karpathy-skills | 162K | Skills+Karpathy准则 | 同上，Skills生态大爆发 |
| Cline | 61K | Coding Agent IDE | 上期只关注到了传统框架 |
| Understand-Anything | 46K | 代码知识图谱 | 新兴项目，5月才爆发 |
| codegraph | 34K | 代码知识图MCP | 同上 |
| ruflo | 56K | Claude多Agent编排 |  |
| openhuman | 26K | 本地私人AI | 本周新上榜 |
| academic-research-skills | 20K | 学术Skills | 本周新上榜 |
| agentmemory | 20K | 编码Agent记忆 | 5月上线的新项目 |

### 📈 星标变化显著的项目（上期→本期）

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

**根据presenc.ai的分类法，Agent框架已分化为四大类别：**

| 类别 | 领跑者 | ⭐ | 势头 |
|------|--------|:--:|:----:|
| 通用编排 | LangChain | 136K | 稳固基本盘 |
| Coding Agent | Cline | 61K | 🔥 18个月62K，增速惊人 |
| 浏览器自动化 | browser-use | 93K | ⚡ 18个月到94K，史上最快之一 |
| 可视/无代码工作流 | n8n | 187K | 🔥 Agent实际=工作流+LLM节点 |
| 记忆/状态化 | Letta | 22K | ➡️ niche但稳定 |
| 路由/代理 | LiteLLM | 46K | 📈 增长中 |
| Skills生态 | mattpocock/skills | 112K | 🔥🔥 本月最大亮点 |

## 四、与当前系统对比分析

### 🔗 直接可借鉴的项目（新增/更新）

| 项目 | 相关度 | 借鉴内容 |
|------|:------:|---------|
| **mattpocock/skills (112K⭐)** | ⭐⭐⭐⭐⭐ | Skills作为独立项目分发模式 → 本站的SKILL.md+SOP体系可以独立打包成文旅Agent Skill包 |
| **codegraph (34K⭐)** | ⭐⭐⭐⭐⭐ | 代码知识图MCP server → 可为本项目搭建景区专有知识图（政策文件、历史数据），减少日报执行时的token消耗 |
| **agentmemory (20K⭐)** | ⭐⭐⭐⭐ | 编码Agent持久记忆 → 与当前MEMORY.md+memory/架构互补，尤其适合跨session的状态保持 |
| **academic-research-skills (20K⭐)** | ⭐⭐⭐⭐ | 专用领域Skills → 验证了**垂直场景Agent Skill包**模式可行，文旅Agent也可以有自己的Skill包 |
| **openhuman (26K⭐)** | ⭐⭐⭐ | 全栈本地AI → 提醒我们可探索本地推理（Ollama+本地知识库）作为云端备选方案 |
| **Understand-Anything (46K⭐)** | ⭐⭐⭐ | 代码知识图谱交互 → 可用于景区数据可视化和内部管理知识库构建 |
| **ruflo (56K⭐)** | ⭐⭐⭐ | Claude多Agent swarm → A+B+C架构的潜在升级参考 |

### 🆚 本系统已覆盖的能力 → 再加强

| 能力 | 现状 | 对标项目 | 优化方向 |
|------|:----:|:---------:|:---------|
| Skills体系 | ✅ 有SKILL.md | agent-skills / mattpocock | 参考Skills独立分发/版本管理 |
| 多Agent协作 | ✅ A+B+C | CrewAI / ruflo | 评估是否引入swarm模式 |
| 记忆系统 | ✅ MEMORY.md+memory/ | Mem0 / agentmemory / Letta | 引入持久化嵌入索引 |
| 浏览器自动化 | ✅ Playwright+CDP | browser-use | 已验证充分 |
| 代码知识图 | ❌ 空白 | codegraph / Understand-Anything | 🆕 **最大优化空间** |

### 🆕 新增发现 — 值得尝试（较上期更新）

1. **Skills方向**不再只是agent-skills独大，mattpocock/skills (112K) + academic-research-skills (20K) 验证了**垂直Skill包独立分发模式**可行 → 可将文旅Agent的skill体系打包为独立repo或文件包
2. **代码知识图谱**是全新赛道 — codegraph和Understand-Anything的爆发说明**预索引上下文**是降低token消耗的关键手段 → 为本系统搭建景区运营知识图，提高日报/分析效率
3. **agentmemory** + **Letta** — 记忆层独立化趋势更明确，可探索将当前memory架构升级为嵌入索引+语义检索
4. **Cline** (61K) 作为IDE Coding Agent的崛起 — 提醒可关注IDE端Agent（Cursor/Cline）作为未来Agent交互入口

## 五、趋势判断（更新至2026年5月末）

| 趋势 | 表现指标 | 对本系统影响 |
|------|---------|:-----------:|
| **Skills生态大爆发** | mattpocock/skills月增71K + academic-research-skills周增11K | ✅ 当前SKILL.md模式正确，可进一步独立化、版本化 |
| **代码知识图谱标准化** | codegraph(34K)+Understand-Anything(46K)+多项目模仿 | 🆕 **最高优先级探索**，直接提升日报/分析效率 |
| **Agent记忆层独立** | agentmemory(20K)+Letta(22K)+Mem0(52K) | ⚠️ 可升级memory架构为嵌入索引 |
| **Agent生态框架化** | n8n(187K)登顶·工作流=Agent | ✅ 方向正确，但无需切换底层框架 |
| **本地私有AI回归** | openhuman(26K)·全栈本地·GPL-3.0 | ⚠️ 可备选探索，非当前刚需 |
| **Coding Agent IDE化** | Cline(61K,18个月)+Aider(44K) | ℹ️ 远期影响，暂不调整 |
| **无代码Agent构建** | n8n+Flowise+Dify占Top5三席 | ❌ 暂无需跟进，当前脚本化方案更适配报表需求 |
| **垂直Agent Skill包** | 学术Skills+金融Skills+Karpathy Skills均已出现 | ✅ **文旅垂直Skill包具有先发机会** |

### 🎯 对电影小镇Agent架构的核心启示

1. **短期内（可执行）：** 搭建景区运营**知识图**（codegraph模式）——将政策文件、历史数据、客流数据、竞品数据预索引，日报中的搜索/读取操作可直接query语义索引，减少token消耗50%+
2. **中期内（可规划）：** 将当前SKILL.md+SOP体系独立为**文旅Agent Skill包**——包括抖音指数分析、竞品追踪、客流分析、日报生成等垂直技能，独立版本管理
3. **长期（可探索）：** 引入**agentmemory**或升级记忆架构为嵌入向量检索，实现跨session的上下文连续性和长期知识自动累积

---

**关联文件：**
- MEMORY.md → 记忆系统架构
- wiki/SOP/ → 当前SOP体系，可升级为独立Skill包
- wiki/技术配置/ → 相关技术参考
- 上期记录：本文档前身（2026-05-24版本）
