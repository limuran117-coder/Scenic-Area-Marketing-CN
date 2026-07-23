# GitHub 高星标调研历史

> 每周 W 编号追踪 GitHub 上与本系统痛点强相关的项目，存档避免重复调研。
> 索引：[project] MEMORY.md 仅保留最新两期（W28 claude-mem + W29 飞书 MCP/awesome-agent-skills），历史详情见本文件。

---

## W30 (2026-07-23) — 飞书 MCP + awesome-agent-skills ⭐⭐ NEW

### 🔥 第一优先：`hankeyyh/feishu-mcp-server` ⭐⭐⭐
- **npm package**: `feishu-mcp-server`
- **发布日期**: 2026-06-08（4 个 commits 重写过）
- **痛点对位**: 我们每天推 12+ 飞书卡片，所有写入路径都依赖 `scripts/send_feishu_card.py` + curl 模拟。
  - 当前痛点: 飞书 API 升级时容易断（Feishu 6/2 升级撞过 11310 错误码限制）
  - 当前痛点: 飞书 wiki / 知识库联动缺失（v9 报告里手动维护月度复盘索引）
- **价值**: 标准化 MCP 协议封装飞书知识库/云文档读写，未来可以 **AI 直接从飞书读 + 写**，减少脚本依赖
- **行动**:
  - W30-W31 spike 安装 → 验证 3 个核心场景 (1) 读飞书知识库 wiki (2) 写飞书卡片 (3) 反向同步本地 wiki
  - **前置条件**: 飞书 App 凭证（feishu-doc 插件已有 credentials，但需扩展 chat:document）
- **风险**: 飞书官方未出 mecp server（社区贡献），需评估 stars / 维护频率
- **预期**: 减少 50% 飞书卡片失败次数 + 站长能直接 AI 同步飞书 wiki

### 🔥 第二优先：`VoltAgent/awesome-agent-skills` ⭐⭐
- **Stars: 1,497 (badge 显示)**, 371 commits, 6 个月持续维护
- **痛点对位**: 我们 60 个 eligible skill 里很多是**通用型**（content-strategy/diagram-maker），缺**景区营销专用** skill
- **价值**: 这是"skill marketplace"，收录 Anthropic/Google Labs/Stripe/Sentry/Cloudflare 官方 skill
- **包含目录**: Anthropic 官方 pdf / docx / xlsx / pptx / brand-guidelines 等
- **行动**:
  - W30 浏览 → 挑选 3-5 个**对位我们场景**的 skill 试装
  - 重点关注: brand-guidelines skill（我们做飞书卡片需要品牌一致性）
  - 关注: pdf/docx skill（站长给 PPT 报告时已用过 `25_deep_report.py`，有官方版可对比）
- **预期**: 我们现有 skill 生态 +30% 场景覆盖

### 第三优先：`anthropics/skills` (官方) ⭐
- **Stars: 1,400+**（Anthropic 官方）
- **价值**: 官方指导文档样板，含 brand-guidelines / pdf / docx 标准实现
- **优先级**: 比 voltagent/awesome 第一层（因为更稳定，更贴近 Anthropic OpenAI 兼容层）
- **行动**: 与 VoltAgent 同步调研，优先看 brand-guidelines

---

## W29 (2026-07-04) — thedotmack/claude-mem
- **Stars**: 85.7K（OpenClaw 原生支持）
- **痛点对位**: MEMORY.md 100/25KB 限制 + 32 cron 记忆碎片 + 冷启动 token 高 + 跨任务知识无法复用
- **行动**: W29 本周 spike `curl -fsSL https://install.cmem.ai/openclaw.sh | bash`
- **状态**: 🆕 待 spike（9 月份 M3 token 限额改善后执行）

## W28 (2026-06-27) — ChromeDevTools/chrome-devtools-mcp
- 44.1K（Google 官方）
- 状态: ⏸️ 中期话题

## W27 (2026-06-24) — affaan-m/everything-claude-code (ECC)
- 220,792 stars
- 状态: 📋 评估中

## W26 (2026-06-20) — rohitg00/agentmemory
- ~18K (2026-05-27)
- 状态: ⏸️ 等 v1.0，与 W29 claude-mem 功能重合

---
