---
name: llm-wiki-maintainer
description: "使用 Karpathy LLM Wiki 模式维护知识库。当用户提到'加入 wiki'、'编译知识'、'更新知识库'、'写入 wiki'时触发。维护 ~/.openclaw/workspace/wiki/ 目录，使用 Obsidian 打开。"
---

# LLM Wiki 知识库维护

## 核心原则

> "The LLM writes and maintains the wiki; the human reads and asks questions."
> "Wiki before RAG" — 文档少于 100 篇时，直接读 wiki 比向量检索更高效。

## 目录结构

```
~/.openclaw/workspace/
├── wiki/              # 知识库主目录（Obsidian Vault）
│   ├── index.md       # 全局索引
│   ├── log.md         # 操作日志（append-only）
│   ├── raw/           # 原始资料（不再修改）
│   └── <topic>/       # 按主题的知识文章
│       └── <article>.md
└── raw/               # 主动收集的原始资料
    └── <topic>/
```

## Topic 分类

- `景区运营` — 景区基础档案、客流数据、运营流程
- `竞品分析` — 竞品数据、对比分析、策略洞察
- `营销策略` — 推广方案、活动策划、内容策略
- `数据日报` — 抖音/小红书日报汇总
- `技术配置` — 脚本、工具、自动化配置

## 三种操作

### 1. Ingest（摄入）

收到需要保存的信息时：
1. 判断 topic → 存入 `raw/<topic>/YYYY-MM-DD-title.md`
2. 编译 → 更新或新建 `wiki/<topic>/<article>.md`
3. 级联更新 → 检查相关 article 是否受影响
4. 更新 `wiki/index.md` 索引
5. 追加 `wiki/log.md` 日志

### 2. Query（查询）

回答用户问题时：
1. 读 `wiki/index.md` 定位相关 article
2. 读 article → 综合回答
3. 引用时用相对链接：`[文章名](../<topic>/<article>.md)`

### 3. Lint（检查）

定期检查：
- index.md 中的条目是否都有对应文件
- article 之间的内部链接是否有效
- raw 引用是否指向存在文件

## 文章格式

```markdown
# 标题

> 本文由 AI Agent 编译 | 首次建立：YYYY-MM-DD | 持续更新

## 标题结构

| 字段 | 内容 |
|------|------|
|      |      |

---

## 相关资源

- [[../../raw/<topic>/<file>.md|Raw: 标题]]

## Updated
YYYY-MM-DD
```

## 强制规则

- **Writeback is mandatory** — 每一个重要决策必须写回 wiki
- **Raw is immutable** — raw/ 下的文件不再修改，只增
- **Log is append-only** — log.md 只追加，不修改历史
- **Compillation before RAG** — 先查 wiki/，再考虑向量检索
