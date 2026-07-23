---
title: W30 GitHub Skill 候选推荐
type: github-research
created: 2026-07-23 10:42
owner: 李涯
period: W30 (2026-07-20 → 2026-07-26)
tags: [github-trending, MCP, skill-ecosystem, W30]
---

# W30 GitHub Skill 候选推荐（不安装，只报告）

> 调研时间：2026-07-23 10:40
> 范围：4 个关键词搜索 + 5 个候选项目 deep-read
> 状态：仅 5 候选项目 spike 评估；**未安装任何 skill**，等站长决策

---

## 📊 候选清单（按对位我们价值排序）

### 🥇 第 1 名：`hankeyyh/feishu-mcp-server` ⭐⭐⭐

| 维度 | 内容 |
|------|------|
| **定位** | 飞书文档/知识库 MCP server（npm 包 `feishu-mcp-server`） |
| **发布** | 2026-06-08，npm 全局安装 |
| **核心能力** | 读飞书知识库 / 写飞书云文档 / 集成 MCP 协议 |
| **痛点对位** | **直接对位** —— 我们每天推 12+ 飞书卡片，wiki 知识库 6/30 后未与飞书同步 |
| **预期价值** | - 飞书卡片失败率 -50%（标准化协议代替 curl 模拟）<br>- wiki/飞书知识库双向同步成为可能<br>- 飞书 wiki 升级时不再撞 API 错误码（6/2 已撞过 11310）|
| **风险** | 飞书未出官方 MCP（社区贡献），项目较新，stars 不高 |
| **建议行动** | **W30-W31 spike 安装验证**（与 W29 claude-mem 并行，互不干扰） |
| **前置条件** | 飞书 App 凭证（feishu-doc 插件已有，需扩展 chat.document 权限） |

### 🥈 第 2 名：`VoltAgent/awesome-agent-skills` ⭐⭐

| 维度 | 内容 |
|------|------|
| **定位** | "skill marketplace"，收录 Anthropic / Google Labs / Stripe / Sentry / Cloudflare 官方 skill |
| **规模** | 1,497 stars / 371 commits / 6 个月持续维护 |
| **核心能力** | 包含 brand-guidelines / pdf / docx / xlsx / pptx 等通用 skill |
| **痛点对位** | 我们 60 eligible skill 大多通用，缺**品牌一致性 + 报告自动化** |
| **预期价值** | - 飞书卡片品牌一致性升级（brand-guidelines skill）<br>- PDF 报告生成标准化（对比我们 `25_deep_report.py`）<br>- skill 生态覆盖率 +30% |
| **建议行动** | W30 周日浏览目录，挑选 3-5 个对位我们场景的试装 |

### 🥉 第 3 名：`anthropics/skills`（Anthropic 官方） ⭐

| 维度 | 内容 |
|------|------|
| **定位** | Anthropic 官方 skill 库（agentskills.io 标准） |
| **规模** | 1,400+ stars（6 月正式发布） |
| **建议** | 与 voltagent 同步调研；优先看 brand-guidelines + pdf |

### ⚪ 候选但**不推荐**（已排除）

| 项目 | 排除原因 |
|------|----------|
| `Batman0506/openclaw-sec-skills` | 网络安全专题，与景区运营无关 |
| `rfdiosuao/AgentSkill` | 飞书+OpenClaw 通用工具箱，无景区针对性 |
| `EgoAlpha/awesome-DeepAgent-skills` | awesome 索引类（不是真 skill） |
| `YangsonHung/awesome-agent-skills` | 同上 |
| `junminhong/awesome-agent-skills` | 同上 |
| `github-mcp-server`（官方） | 我们已有 gh CLI，已认证（limuran117-coder）+ gh-issues skill 覆盖 |

---

## 🎯 痛点 → skill 对位矩阵

| 我们的痛点 | 对位候选 | 优先级 |
|----------|---------|--------|
| **飞书卡片推送脆性**（API 升级/错误码） | 🥇 `hankeyyh/feishu-mcp-server` | 立即 spike |
| **飞书 wiki/云文档双向同步缺失** | 🥇 `hankeyyh/feishu-mcp-server` | 立即 spike |
| **MEMORY.md 100/25KB 限制** | （已计划）`thedotmack/claude-mem` W29 | W31 后执行 |
| **PDF 报告生成标准化**（月报/复盘） | 🥈 `awesome-agent-skills` 中的 pdf skill | W30 周末 |
| **飞书卡片品牌一致性**（颜色/字体） | 🥈 brand-guidelines skill | W30 周末 |
| **数据源 → 知识库反哺自动化** | ❌ 暂无对位 | 内部实现 |
| **周末 cron 调度漂移** | ❌ 暂无对位 | 内部修复（已修）|

---

## 🛠️ 风险与依赖

### 高风险（需站长决策）
1. **🎯 `feishu-mcp-server` 安装**：需评估是否替代 `scripts/send_feishu_card.py`
   - **风险**：现有 12+ cron 飞书卡片全依赖该脚本，全替换风险大
   - **方案**：先**并行**（不替换），验证后再迁移
2. **`anthropics/skills` 安装对 OpenClaw 兼容性**：官方文档说 "Claude Code 标准"，需要 OpenClaw 实现兼容层
3. **`awesome-agent-skills` 中的 brand-guidelines**：跟现有飞书卡片 schema=2.0 冲突时如何处理

### 低风险（可自主 spike）
1. 浏览 `awesome-agent-skills` 找 3-5 个对位我们场景的 skill 试装
2. 用 `anthropics/skills` 的 pdf skill 替代 `25_deep_report.py`

---

## 📋 行动优先级（等站长决策）

| 优先级 | 行动 | 时间 | 风险 |
|--------|------|------|------|
| 🟢 **立即** | 浏览 `awesome-agent-skills` 目录，挑 3-5 个 spike 候选 | 30 min | 0 |
| 🟢 **W30 末** | spike `brand-guidelines` skill，测试对飞书卡片兼容性 | 2-3h | 低 |
| 🟡 **W31** | spike `feishu-mcp-server`（需站长飞书 App 凭证扩展）| 1 天 | 中（需凭证） |
| 🟡 **W32** | spike `anthropics/skills` 官方 pdf/docx/xlsx，验证 vs 现有脚本 | 1-2 天 | 中（迁移风险） |
| 🔴 **W33+** | claude-mem（已评估）| TBD | TBD |

---

## 📎 关联文档

- 完整调研历史：`memory/topics/github-research-history.md`
- MEMORY 7/23 备忘：`MEMORY.md`（W29 claude-mem 决策）
- W30 周日维护：`wiki/系统/W29-知识库脱节补救计划.md`

---

**报告人：李涯 · 2026-07-23 10:42**
