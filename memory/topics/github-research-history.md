# GitHub 高星标调研历史

**目的**：每周 W 编号追踪 GitHub 上与本系统痛点强相关的项目，存档避免重复调研。
**索引**：[project] MEMORY.md 仅保留最新一期（W29 claude-mem），历史详情见本文件。

---

## W29 (2026-07-04) — thedotmack/claude-mem ⭐ 推荐
- **Stars**: 85.7K（OpenClaw 原生支持）
- **痛点对位**: MEMORY.md 100/25KB 限制 + 32 cron 记忆碎片 + 冷启动 token 高 + 跨任务知识无法复用
- **行动**: W29 本周 spike `curl -fsSL https://install.cmem.ai/openclaw.sh | bash`
- **预期**: 冷启动 token 降 60%+，可替代 MEMORY.md 持久层
- **状态**: 🆕 待 spike

## W28 (2026-06-27) — ChromeDevTools/chrome-devtools-mcp
- **Stars**: 44.1K（Google 官方）
- **价值**: MCP 协议封装思路（CLI + MCP 双入口）
- **行动**: H2 评估脚本 MCP 化试点；W28-W29 spike「采集脚本出错时自动截屏诊断」
- **状态**: ⏸️ 中期话题，无紧迫性

## W27 (2026-06-24) — affaan-m/everything-claude-code (ECC) ⭐ 自纠错
- **Stars**: 220,792（最初 W26 漏掉，W27 自我纠错补入）
- **价值**: Skills 生态「操作系统层」标准化（7 大 harness 跨平台）
- **借鉴 4 点**:
  1. Memory Persistence Hooks
  2. Verification Loops (checkpoint + pass@k)
  3. Continuous Learning（自动提取爆款规律）
  4. 跨平台 plugin 结构
- **状态**: 📋 评估中，W27 已写入 self-improving-agent-3.0.10

## W26 (2026-06-20) — rohitg00/agentmemory
- **Stars**: ~18K（2026-05-27 首版）
- **价值**: BM25+向量混合检索+LLM 自动压缩，token 消耗降 92%
- **状态**: ⏸️ 等 v1.0 稳定；与 W29 claude-mem 功能重合，claude-mem 更优

## 同期关注
- anthropics/knowledge-work-plugins 21,864（Anthropic 官方，Skill 三层结构可能成为行业事实标准）
- Understand-Anything 67K（反驳 W26「知识图谱赛道见顶」判断）