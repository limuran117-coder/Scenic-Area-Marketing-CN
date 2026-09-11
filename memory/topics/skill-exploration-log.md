# 周度技能探索日志

## 2026-06-06 探索

### 背景
- 第3次周度探索（前两次：5/24技能分配、5/30验证GitHub）
- 上次大规模Skill更新：6月5日新增4个技能（daily-task-template, data-integrity-check, task-audit, system-metabolism）
- SKILL-USAGE-GUIDE.md 严重过时（2026-04-11），描述已不存在的子Agent架构

### 本次评估的技能

| 技能 | 位置 | 判断力 | 采集力 | 沉淀力 | 评估 |
|------|------|--------|--------|--------|------|
| spike | 系统技能 | 🟢 高 | 🟡 中 | ⚪ 低 | ✅ 已记录在TOOLS.md，无需新建Skill |
| taskflow | 系统技能 | ⚪ 低 | 🟡 中 | ⚪ 低 | ❌ 太重，cron+task-audit已满足编排需求 |
| model-usage | 系统技能 | 🟡 中 | ⚪ 低 | 🟢 高 | ⏸️ 需brew安装codexbar，暂不优先 |
| healthcheck | 系统技能 | ⚪ 低 | ⚪ 低 | ⚪ 低 | ❌ 侧重SSH/防火墙安全，非运营运维核心 |
| fireworks-tech-graph | .agents | 🟡 中 | ⚪ 低 | 🟡 中 | ⏸️ 需rsvg-convert，季度报告可能有用 |
| video-frames | 系统技能 | ⚪ 低 | 🟡 中 | ⚪ 低 | 🔧 ffmpeg已安装，按需使用即可 |

### 关键发现

1. **SKILL-USAGE-GUIDE.md 严重过时** ⚠️
   - 日期：2026-04-11
   - 引用不存在的技能：browser-agent, ai-web-automation, elite-longterm-memory, neural-memory, jpeng-knowledge-graph-memory, deepresearchwork, market-research-agent
   - 描述不存在的子Agent架构：douyin-agent, xiaohongshu-agent, competitor-agent, review-agent
   - 需要完全重写

2. **skills-catalog.md 同样过时**
   - 统计30个Skill → 实际workspace只有24个
   - Agent-Skill分配表全是历史遗留

3. **当前实际情况**
   - 主Agent通过cron直接执行8个日常任务
   - 数据采集：Playwright脚本（douyin_index.py, xiaohongshu_crawl.py）
   - 质量保证：data-integrity-check（前）+ task-audit（后）
   - 标准化：daily-task-template
   - 维护：system-metabolism（周日）
   - 路由：skill-router（意图识别）
   - 规范：karpathy-guidelines, karpathy-wiki

4. **无需新增技能** - 当前技能栈已满足运营需求，6月5日新增的4个技能填补了最后的缺口

### 执行动作

- [x] 更新 TOOLS.md（video-frames可用性 + spike模式确认）
- [x] 重写 SKILL-USAGE-GUIDE.md（反映当前架构）
- [x] 更新 skills-catalog.md（反映实际Skill清单）
- [x] 创建本日志文件

### 下次探索关注点
- 验证 system-metabolism 周日首次运行效果
- 评估是否需要 cost tracking（如果token消耗显著增长）
- 评估data-integrity-check在实际运行中的拦截率

---

## 2026-09-12 探索（第 12 次）

> ⚠️ 注：任务配置指向 `~/.openclaw/workspace/TOOLS.md`，但该文件**已不存在**（本地 notes 已并入 AGENTS.md，2026-06 起）。本日志为周度探索的权威归档位置。

### 环境快照（exec 实测，非 LLM 推断）
- `scripts/`：**105 个**（含 `__pycache__` / `archive/`）
- 系统技能（openclaw/skills）：**52 个**
- workspace 技能：**38 个**
- 核心 CLI 全部在位：`gh` `/opt/homebrew/bin/gh`、`curl` `/usr/bin/curl`、`jq` `/usr/bin/jq`、`ffmpeg` `/opt/homebrew/bin/ffmpeg` ✅

### 与上次（2026-06-06）的差异
- 系统技能 58 → **52**（清减 6 个）
- scripts 56 → **105**（含归档子目录，实际生产脚本仍 ~40+）
- 无缺失 CLI，无新增依赖缺口

### 本次评估（1-2 个候选）
| 候选 | 位置 | 判断力 | 采集力 | 沉淀力 | 评估 |
|------|------|--------|--------|--------|------|
| `codegraph__codegraph_explore` | MCP 工具（已挂载） | 🟢 高 | 🟢 高 | 🟡 中 | ✅ **已可直接用**，无需安装。改脚本前先探索调用链，替代 grep/read 循环，省 token |
| `notion` / `obsidian` | 系统技能 | 🟡 中 | 🟡 中 | 🟢 高 | ⏸️ wiki 已走 karpathy-wiki + GitHub 链路，Notion 无落地场景，暂不引入 |

### 结论
- **无需新增技能**。当前链路（douyin_index v11 / xiaohongshu_crawl / feishu 卡片 / karpathy-wiki / cron 治理）稳定。
- 唯一可立刻受益的是 `codegraph_explore`——**零成本**（已挂载），改代码前先探索，减少 Read/Grep 往返。
- 上线前提：无。

### 遗留问题
- 任务 prompt 中的 `TOOLS.md` 路径已失效，建议下次治理时把 cron message 改为写 `memory/topics/skill-exploration-log.md`。
