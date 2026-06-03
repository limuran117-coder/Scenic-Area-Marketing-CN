---
title: Wiki Schema
type: schema
tags: [wiki, conventions]
created: 2026-04-25
updated: 2026-04-25
---

# Wiki Schema — 建业电影小镇知识库编写规范

> 基于 karpathy-wiki 模式 | 每次更新后同步 log.md

---

## 核心理念

- **纯添加，不修改，不删除**：`raw/` 文件永远不可变
- **知识分层**：业务执行层（电影小镇/竞品分析/…）≠ 知识抽象层（concepts/entities/sources/）
- **链接驱动**：通过 [[wikilinks]] 建立概念间关系，形成知识图谱

---

## 目录结构

```
wiki/
├── raw/               # 不可变源文档（原始报告/截图/粘贴内容）
├── index.md          # 内容总目录
├── log.md            # 追加式操作日志
├── overview.md       # 全域知识总览（从所有sources合成）
├── schema.md         # 本文件：编写规范
├── concepts/         # 概念页（景区类型、内容类型、平台规则…）
├── entities/         # 实体页（景区、平台、品牌…）
├── sources/          # 每个raw源文档的摘要页
└── queries/          # 有价值的问答结果归档
```

---

## 页面类型（type）

| type | 用途 | 示例 |
|------|------|------|
| `concept` | 抽象概念 | 演艺景区、季节性客流规律、内容爆款规律 |
| `entity` | 具体实体 | 建业电影小镇、万岁山武侠城、抖音平台 |
| `source` | 原始文档摘要 | 2026-04月抖音指数日报合集、穿越德化街数据分析 |
| `query` | 问答归档 | 竞品对比分析结论、如何提升平日客流 |
| `overview` | 领域总览 | 文旅景区营销知识总览 |
| `schema` | 规范文档 | 本文件 |

---

## 页面格式（YAML frontmatter）

```yaml
---
title: Page Title
type: concept | entity | source | query | overview | schema
tags: [tag1, tag2, tag3]
created: YYYY-MM-DD
updated: YYYY-MM-DD
sources: [raw/filename.md]      # 仅 source 页必填
related: [[entities/xxx]]       # 主要关联（可选）
---
```

---

## Wikilink 规范

- 页面间链接：`[[pagename]]` 或 `[[pagename|显示文本]]`
- 同一目录下：`[[pagename]]`
- 不同目录下：`[[directory/pagename]]`
- 外部链接：使用标准 markdown `[text](url)` 格式

---

## 命令规则

| 操作 | 触发条件 | 动作 |
|------|----------|------|
| **INGEST** | raw/ 有新文件 | 读取 → 写 sources/ → 更新概念/实体页 → 更新 index.md → 追加 log.md |
| **QUERY** | 用户问知识库相关问题 | 读 index.md → 读相关页 → 综合回答 → 有价值则归档到 queries/ |
| **LINT** | 用户说"lint"/"健康检查"/raw有新文件 | 扫描所有页 → 检查矛盾/孤立页/过时内容 → 修复或报告 |
| **日常更新** | cron/手动任务执行 | 更新对应业务层文件 → 不碰 knowledge 层 |

---

## 知识层 vs 业务层 分工

| 层级 | 内容 | 维护方式 |
|------|------|----------|
| **知识层** | concepts/ entities/ sources/ queries/ overview/ schema/ | INGEST/LINT 时更新 |
| **业务层** | 电影小镇/ 竞品分析/ 全国景区案例库/ 行业知识/ SOP/ 技术配置/ | cron 任务直接写入 |

**关键原则**：知识层从业务层提炼，但业务层不依赖知识层。知识层可完全重建，业务层不变。

---

## 命名规范

- 页面标题：使用中文，无特殊字符
- 文件名：`kebab-case` 或中文全拼
- tags：全小写，复数
- 更新时：只改 `updated`，不改 `created`

---

## 质量标准

- 每个 concept/entity 页：1-2 句摘要开头
- 每个 source 页：列出关键数据点（数字/结论）
- 矛盾处理：保留最新/最权威，不删除旧结论（加脚注说明）
- 孤立页检查：每个页至少有一个 inbound link

---

*本文件由 AI Agent 维护 | 修改需遵循 karpathy-wiki 规范*
