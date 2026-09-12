---
title: Memory 结构说明
type: index
tags: [memory, 结构说明]
created: 2026-09-12
updated: 2026-09-12
---

# memory/ 结构说明

> 2026-09-12 整理：本目录是 OpenClaw 的**记忆层**，与 `wiki/`（知识库层）分工明确。

## 目录组织

| 位置 | 内容 | 说明 |
|------|------|------|
| `20XX-XX-XX.md` | **日档**（约 138 个） | 每日工作记录、决策、发现 |
| `20XX-XX-XX-<后缀>.md` | 专题日档 | 如 `-summary`（汇总）、`-anomaly`（异常） |
| `topics/` | **主题笔记**（26 个） | 跨日期的专题沉淀 |
| `dreaming/` | **梦境日记**（101 个） | 系统自主反思产物 |
| `personas/` | 人格设定（2 个） | — |
| `dream-log.md` | 梦境总日志 | — |
| `procedures.md` | 流程记录 | — |
| `skill-usage.md` | 技能使用统计 | — |
| `index.json` / `user_model.json` | 结构化索引 | 供程序读取（Obsidian 中已排除） |
| `palace/` | **向量库**（ChromaDB） | 语义检索用，已在 Obsidian 中排除显示 |
| `dreaming/` | 梦境日记（deep/light/rem 三层） | Memory Dreaming 自动生成，与 `DREAMS.md` 对应 |


## 与其他层的关系

- **本层（memory/）**：过程与记忆 —— 什么时候发生了什么
- **wiki/ 层**：结论与知识 —— 沉淀后的可复用内容（独立 vault 呈现）
- **顶层文件**：`MEMORY.md`（长期记忆）、`AGENTS.md`（行为规范）、`DREAMS.md`（反思）、`SOUL.md`/`USER.md`/`IDENTITY.md`（人格）

> 💡 数据/CSV 等原始文件已移至 `raw/data/`，不再混放在日档目录。
