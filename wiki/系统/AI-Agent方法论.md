---
title: AI-Agent方法论
type: concept
tags: [AI-Agent, 方法论, karpathy, LLMWiki]
created: 2026-04-18
updated: 2026-04-18
---

# AI-Agent方法论

AI-Agent的核心方法论，融合Andrej Karpathy的编程智慧与LLM Wiki模式。

---

## 一、行为准则（karpathy-guidelines）

### 4大原则

| 原则 | 核心 | 敌人 |
|------|------|------|
| Think Before Coding | 不假设、不隐藏困惑 | 猜测当事实 |
| Simplicity First | 最小代码解决问题 | 过度设计 |
| Surgical Changes | 只改必须改的 | 顺手美化 |
| Goal-Driven | 定义可验证的终点 | 盲目执行 |

### 反模式速查

- **沉默假设** → 开口前列出假设
- **单一折扣用Strategy** → 50行能解决的别写200行
- **修bug改引号风格** → 只改那行必须改的
- **"让它能work"** → 先写测试复现，再修复

### 复杂度时机原则

> 好代码 = 用简单方式解决今天的问题，而不是用复杂方案预防明天的问题

---

## 二、知识管理（LLMWiki模式）

### 核心理念

**知识应该复合增长，不该每次重新推导。**

### 三层架构

| 层级 | 目录 | 说明 |
|------|------|------|
| 原始资料 | `raw/` | 不可变源文档，用户维护 |
| 消化整理 | `wiki/` | AI维护的互联markdown |
| 结构规范 | `schema/` | 配置规则文档 |

### 三种操作

| 操作 | 触发 | 产出 |
|------|------|------|
| **INGEST** | raw/有新文件 | 10-15个互联页面 |
| **QUERY** | 用户问问题 | 综合答案，有价值则写回wiki |
| **LINT** | 定期检查 | 矛盾/过时/孤儿页/断裂链接 |

### 追加日志

`log.md`格式：
```
## [YYYY-MM-DD] operation | Title
- Pages created: ...
- Pages updated: ...
- Total pages touched: N
```

---

## 三、nanoGPT启示

### 模型架构（330行model.py）

```
GPT
├── transformer
│   ├── wte   — Token Embedding
│   ├── wpe   — Position Embedding
│   ├── h     — N个Block
│   └── ln_f  — 最终LayerNorm
└── lm_head   — 输出投影
```

### 训练循环（336行train.py）

```
get_lr(it) → cosine decay with warmup
↓
model(x, y) → cross_entropy loss
↓
scaler.scale(loss).backward() → clip → step → zero_grad
```

### 设计哲学

> **"teeth over education"** — 去掉教学包装，只留核心

---

## 四、Trae AI编辑器

### Solo核心能力

- 自动拆解任务并调用工具执行
- 支持Desktop + Web多设备
- 云端并行运行多个任务
- 读取.docx/.csv/.pptx/Python等多格式
- 实时预览，支持评论和迭代

### API控制（有限制）

```python
from trae_client import TraeClient
client = TraeClient(token="token")
client.chat.send_message("分析这个代码库")
```

限制：需要有效Token，云端服务

---

## 五、对本Agent的具体应用

### 行为层面
- [ ] 重大修改前先说假设
- [ ] 多解释时呈现选项
- [ ] 手术刀式改动，每行追溯到请求
- [ ] 多步任务列plan+verify

### 知识管理层面
- [x] `wiki/log.md` 追加日志 ✅
- [ ] `wiki/concepts/` 概念页（karpathy-wiki结构）
- [ ] `wiki/entities/` 实体页（karpathy-wiki结构）
- [ ] `wiki/queries/` 查询归档（karpathy-wiki结构）
- [x] karpathy-wiki skill ✅
- [x] karpathy-project-wiki skill ✅

### 代码库知识库
- [ ] karpathy-project-wiki模式（代码库专属）
- [ ] git diff驱动漂移检测
- [ ] mermaid架构图

---

## 🆕 2026-06-30 H1 收官节点（AI Agent 应用实证）

### **6/30 AI Agent 关键工作**

#### 1. H1 客流收官分析

- 4 张飞书卡已发（v1 误版 + v2 修正版 + 抖音日报 + 竞品动态 v2 + P0 精简卡）
- H1 716,409（+6.7%）+ 6 月崩盘 + 端午异常曲线 + 渠道全塌方

#### 2. 站长纠错 6 次 → MEMORY 铁律 +2 条

- **R-NEW-01** CSV 末日完整性（Level 1 宪法）
- **R-NEW-02** 节假日逐日曲线（Level 1 宪法）
- 6/30 当日纠错 2 次（端午累计掩盖初六 782 暴跌 88% + 6/29-30 CSV=0 误标收官）

#### 3. competitor_program_tracker.py v1→v2 修复

- v1 模板空壳 → v2 引入 web_search 主路径 + CDP 抖音备路径 + 静态兜底
- 5 竞品 9 条 2026 年 6 月真实活动入库

#### 4. Obsidian 知识库 6 轮同步

- 1+2+3+4+5+6 轮总计 131 个文件 6/30 更新
- 含电影小镇/竞品分析/行业知识/SOP/entities/sources/运营规划/queries/concepts 全部子目录

### **6/30 AI Agent 方法论验证**

| 原则 | 6/30 实证 |
|------|----------|
| 反谄媚 | 4 张飞书卡均含数据来源+同比+环比 |
| 量化+定性 | 6/30 全部数据均有置信度/同比/环比 |
| 推荐+利弊+代价 | P0 三项均有截止日+降级方案 |
| 不掩盖失败 | 4 次主动暴露（v1 误版+CSV 暂态+端午异常+抖音垫底）|

### 关联文档

- 6 轮同步记录：`wiki/log.md`
- H1 一页纸：`memory/2026-06-30-h1-recap.md`
- 反谄媚规范：`wiki/SOP/反谄媚分析规范.md`
- 决策规则库：`wiki/行业知识/决策规则库.md`
- 验证记录：`wiki/行业知识/验证记录.md`
