# GitHub高星标项目研究笔记

> 更新：2026-05-24（W22）| 采集：web_search综合 | 下期：周六00:00

---

## 一、2026年5月 Top 20 AI Agent 框架星标排名

| # | 项目 | ⭐ Stars (2026-05) | 语言 | 定位 |
|:-:|------|:-----------------:|:----:|------|
| 1 | AutoGPT | 183K | Python | 自主Agent框架先驱 |
| 2 | Langflow | 147K | Python | 可视化Agent构建器 |
| 3 | Dify | 136K | TypeScript | 企业级Agent工作流平台 |
| 4 | LangChain | 132K | Python | 基础Agent工程平台 |
| 5 | Gemini CLI | 100K | TypeScript | Google终端AI Agent |
| 6 | Browser-use | 86K | Python | 浏览器自动化Agent框架 |
| 7 | RAGFlow | 77K | Python | RAG+Agent融合引擎 |
| 8 | **LobeHub** | **75K** | TypeScript | 多Agent协作平台 |
| 9 | **MetaGPT** | **67K** | Python | 软件公司模拟多Agent |
| 10 | OpenBB | 65K | Python | 金融AI Agent平台 |
| 11 | **AutoGen (MS)** | **57K** | Python | 微软多Agent对话框架 |
| 12 | AI-Agents-Beginners | 56K | Jupyter | MS 12课Agent教程 |
| 13 | Mem0 | 52K | Python | Agent通用记忆层 |
| 14 | Flowise | 52K | TypeScript | 无代码Agent构建 |
| 15 | **CrewAI** | **48K** | Python | 角色扮演Agent协作 |
| 16 | LocalAI | 45K | Go | 本地模型运行引擎 |
| 17 | Cherry Studio | 43K | TypeScript | AI生产力工作室 |
| 18 | Agno (原Phidata) | 39K | Python | Agent规模化部署 |
| 19 | MindsDB | 39K | Python | AI分析查询引擎 |
| 20 | ToolJet | 38K | JavaScript | 内部工具+Agent |

## 二、本周（5月第4周）增长最快的项目

| # | 项目 | 周增⭐ | 总⭐ | 亮点 |
|:-:|------|:------:|:----:|------|
| 1 | DeepSeek-TUI | +21,752 | 26K | Rust实现的DS终端编码Agent |
| 2 | anthropics/financial-services | +12,088 | 21K | Anthropic官方金融服务Agent |
| 3 | addyosmani/agent-skills | +11,725 | 40K | Google Engineer的Agent Skills合集 |
| 4 | TradingAgents | +7,259 | 74K | 多Agent对冲基金交易系统 |
| 5 | pi-mono (badlogic) | 43.9K | — | AI Agent工具包：CLI+TUI+Web+统一LLM |

### ⚡ 本周新兴项目（周增TOP）

- **DeepSeek-TUI**（Hmbown）: Rust写的DeepSeek终端编程Agent，一周暴增2.1万⭐
- **agent-skills**（addyosmani）: Google工程师整理的Agent Skills集合，持续月增长
- **pi-mono**（badlogic）: 统一Agent工具包，含CLI/TUI/Web/LLM统一接口/Slack/GPU部署

## 三、与当前系统对比分析

### 🔗 直接可借鉴的项目

| 项目 | 相关度 | 借鉴内容 |
|------|:------:|---------|
| **Agent Skills (addyosmani)** | ⭐⭐⭐⭐⭐ | Skills编写规范、最佳实践合集 → 可直接参考其SKILL.md模式 |
| **Mem0** | ⭐⭐⭐⭐ | 通用记忆层方案 → 对标当前MEMORY.md+memory/架构 |
| **CrewAI** | ⭐⭐⭐⭐ | 多Agent角色分工 → 可用作A+B+C架构的优化参考 |
| **LobeHub** | ⭐⭐⭐ | 多Agent协作平台UI → Agent团队可视化 |
| **pi-mono** | ⭐⭐⭐ | 统一工具包思路 → 统一LLM API抽象 |

### 🆚 本系统已覆盖的能力

- Skills系统：SKILL.md格式 ✅（与CowAgent/agent-skills模式一致）
- 多Agent协作：A+B+C架构 ✅（对应CrewAI/AutoGen模式）
- 记忆系统：MEMORY.md+memory/ ✅（对标Mem0/neural-memory）
- 浏览器自动化：CDP+Playwright ✅（对应Browser-use）

### 🆕 新增发现 — 值得尝试

1. **Mem0（52K⭐）**：独立记忆层API，可作为当前memory系统的增强补充
2. **agent-skills（40K⭐）**：社区Skills标准，参考优化当前SOP体系
3. **pi-mono的LLM统一API**：统一Anthropic/OpenAI/Google接口，降低切换成本

## 四、趋势判断

| 趋势 | 表现 | 对本系统影响 |
|------|------|:----------:|
| **Skills标准化** | agent-skills月增长→Skills成为Agent生态标准 | ✅ 当前模式符合趋势 |
| **记忆层独立** | Mem0 52K⭐→记忆从框架剥离为独立组件 | ⚠️ 可优化memory架构 |
| **无代码Agent** | Langflow/Dify/Flowise占据Top5三席 | ❌ 暂无需跟进 |
| **垂直Agent** | TradingAgents/金融/医疗专用Agent快速增长 | ✅ 文旅Agent方向正确 |
| **本地推理** | LocalAI 45K⭐→本地模型回归 | ⚠️ 可探索本地LLM |

---

**关联文件：**
- MEMORY.md → 记忆系统架构
- wiki/SOP/ → 当前SOP体系
- identity.md → 技能编写参考
- 4月份存档：`memory/dreaming/light/2026-04-30.md`
