# EvoMap/evolver 研究报告

> GitHub: EvoMap/evolver | Stars: 7.1k | 语言: Node.js | GPL-3.0

---

## 一、核心定位

基于GEP（Gene Expression Programming）协议的AI Agent自进化引擎。

**一句话概括**：把零散的prompt调优变成可审计、可复用的进化资产（Gene/Capsule）。

**与OpenClaw关系**：README明确提到OpenClaw集成 — "OpenClaw会识别Evolver向stdout输出的sessions_spawn(...)协议，无需安装hooks"

---

## 二、核心概念

### 2.1 Gene（基因）
经验迭代的最小单位。紧凑的代码/提示片段，可被激活和复用。

### 2.2 Capsule（胶囊）
多个Gene的组合，形成更完整的技能单元。

### 2.3 EvolutionEvent（进化事件）
完整审计链 — 记录每次进化的触发信号、选择依据、执行结果。

---

## 三、工作流程

```
memory/目录扫描 → Gene/Capsule匹配 → GEP提示词生成 → EvolutionEvent记录
```

### 三种运行模式
| 模式 | 命令 | 行为 |
|------|------|------|
| 单次 | `evolver` | 生成提示词，输出到stdout，退出 |
| 审查 | `evolver --review` | 暂停等待人工确认后再应用 |
| 循环 | `evolver --loop` | 守护进程循环，带自适应休眠 |

---

## 四、与OpenClaw集成

### 4.1 安装方式
```bash
# 安装
npm install -g @evomap/evolver

# OpenClaw workspace内克隆
cd ~/.openclaw/workspace
git clone https://github.com/EvoMap/evolver.git
cd evolver && npm install
```

### 4.2 OpenClaw原生识别
- OpenClaw会识别stdout中的`sessions_spawn(...)`协议
- 无需额外安装hooks
- evolver输出纯文本，OpenClaw自动解释并触发后续动作

### 4.3 与autonomy-kit对比

| 维度 | EvoMap/evolver | autonomy-kit |
|------|----------------|--------------|
| 核心理念 | Gene进化 | 自驱任务 |
| 审计链 | EvolutionEvent | 无明确审计 |
| 触发方式 | memory/扫描 | 任务队列 |
| 产出 | GEP提示词 | 执行动作 |
| OpenClaw集成 | 原生支持 | 已有skill |

---

## 五、学术背景

论文：《从程序化技能到策略基因：面向经验驱动的测试时进化》
arXiv: 2604.15097

45个科学代码场景，4590次对照实验结论：
- Gene表示 > 散落prompt文档（更紧凑、更稳定）
- gene-evolved系统将配对基座模型从9.1%→18.57%

---

## 六、可落地借鉴

### 6.1 低成本：引入进化审计意识
不需要装evolver，只需要在daily notes中增加"进化事件"格式：
```markdown
## 进化事件
- 日期：YYYY-MM-DD
- 触发：什么问题/信号
- 选择：为什么选这个方案
- 结果：执行效果
```

### 6.2 中成本：集成Evolver
```bash
cd ~/.openclaw/workspace
git clone https://github.com/EvoMap/evolver.git
cd evolver && npm install
```
在cron任务中调用evolver作为进化引擎。

### 6.3 高成本：Gene/Capsule知识沉淀
将每次任务执行的精华提炼为Gene存入知识库，供后续任务复用。

---

## 七、注意事项

1. **EvoMap声明**：2026年3月出现了一个与Evolver高度相似的系统（指Hermes Agent），EvoMap从MIT转为GPL-3.0以保护项目完整性
2. **Evolver vs Hermes**：两者都做自进化，但架构不同；我们已在用hermes-agent
3. **源码可见**：Evolver最新版本从完全开源转为源码可见，但npm包仍可用

---

*研究日期：2026-04-30*
