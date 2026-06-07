# Skills 探索笔记

> 记录新发现/测试的技能，每周更新
> 最后更新：2026-06-07

---

## 2026-W16 探索记录

### 1. agent-swarm（多智能体集群编排）✅ 已深入研究

**定位：** 多智能体团队指挥官，适合复杂任务拆解并行执行

**核心能力：**
- 9种专业角色（pm/researcher/coder/writer/designer/analyst/reviewer/assistant/automator）
- 支持并行+串行混合编排
- 经验记忆积累机制
- 模型成本优化分配

**适用场景：**
- 竞品深度调研（并行抓取多个竞品）
- 多维度日报生成（数据+文案+图表分工）
- 复杂项目规划与审核链路

**关键语法：**
```javascript
sessions_spawn({
  task: "具体任务",
  agentId: "researcher", // 指定角色
  label: "task-name",
  runTimeoutSeconds: 300
})
```

**注意：** 该技能需要子Agent配置，当前主要用 sessions_spawn 做并行调研

---

### 2. knowledge-graph-memory（知识图谱记忆）✅ 已深入研究

**定位：** 结构化长期记忆，支持概念漂移检测和时间推理

**核心能力：**
- 知识图谱：节点（概念）+ 边（关系）
- 概念漂移检测：ADWIN/DDM/统计方法
- 时间推理：事件追踪、时间范围查询
- 记忆整合：短时→长时自动晋升

**适用场景：**
- 建立景区运营知识图谱（竞品/用户/内容关系）
- 长期跟踪概念变化（如竞品热度趋势）
- 复杂知识结构化存储

**关键API：**
```javascript
const kg = new KnowledgeGraph();
kg.addConcept('电影小镇', { category: '景区' });
kg.link('电影小镇', '建业', 'owns');
kg.getRelated('电影小镇');
```

**注意：** 是JS库，需要Node环境；更适合知识库构建而非日常日报

---

---

## 2026-W17 探索记录（2026-04-25）

### 3. deep-research（深度研究框架）✅ 已研究

**定位：** 系统性深度调研方法论，适合竞品分析、政策研究、市场调查

**核心价值：** 将零散的 web_search + web_fetch 串联成标准化流程，避免调研浅尝辄止

**4阶段流程：**
1. **Initial Investigation** — 广撒网，定义研究范围，识别关键术语
2. **Deep Dive** — 定向抓取，交叉验证，挖掘一手来源
3. **Synthesis & Validation** — 模式识别，事实核查，评估偏差
4. **Report Generation** — 结构化报告，含置信度、矛盾点、待验证问题

**对我工作的适用场景：**
- 竞品深度调研（不只是抓数据，要验证事实）
- 文旅政策研究（多源交叉验证）
- 行业趋势分析（信源分级+时间衰减判断）

**研究质量标准（关键）：**
- 信源多样性：学术+行业+一手都要有
- 时效性评估：fast-changing topic要优先新信息
- 权威性判断：同行评审>机构>匿名

**研究迭代循环：** Cycle1泛查→Cycle2定向→Cycle3验证→Cycle4报告

**输出模板结构：** Executive Summary / Research Questions / Methodology / Key Findings / Supporting Evidence / Contradictions / Limitations / Further Research

**现有工具支撑：** web_search + web_fetch + browser + read/write + memory_search

**注意：** 这是一套方法论，不是独立工具。需要主动调用其框架意识来执行调研任务。

---

### 4. agentic-workflow-automation（工作流自动化蓝图）✅ 已研究

**定位：** 将多步骤任务生成可复用的自动化蓝图，导出给 n8n 等平台执行

**核心价值：** 把「日报生成」这类固定流程固化成蓝图，一键触发自动执行

**核心概念：**
- **trigger**：触发条件（cron时间触发/Webhook/文件变化）
- **steps[]**：有序步骤列表，每步单一日标
- **step类型**：http / llm / db / task 等
- **fallback**：失败行为（retry重试 / skip跳过 / stop停止）

**关键工具：** `scripts/generate_workflow_blueprint.py` — 输入workflow名+trigger+steps，输出确定性JSON/markdown蓝图

**对我工作的适用场景：**
- **抖音日报自动化** → cron触发 → 数据采集(Playwright) → LLM分析 → 飞书推送
- **竞品动态追踪** → 定时触发 → 多源数据采集 → 聚合分析 → 推送
- **每日复盘整合** → 定时触发 → 汇总各定时任务输出 → 生成综合日报

**工作流设计原则：**
- 每步单一职责
- 明确声明step类型和fallback
- 顺序要显式声明

**输出格式：** JSON（给n8n用）或 Markdown（给文档用）

**注意：** 脚本 `generate_workflow_blueprint.py` 需要确认是否已部署在 workspace 内。

---

## 后续探索计划

- [ ] gemini-computer-use（Gemini浏览器控制）
- [ ] apex-stack-claude-code（APEX认知框架）
- [ ] skill-router（技能路由自动匹配）
- [ ] elite-longterm-memory（精英长期记忆）

---

*由 AI Agent 维护 | 随周度探索更新*
