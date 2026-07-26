---
title: W30 ego(lite) 调研报告
type: github-research
created: 2026-07-23 11:08
owner: 李涯
period: W30
tags: [ego-lite, ego-browser, agent-browser, chromium, browser-automation]
status: researched-not-installed
---

# W30 ego(lite) 调研报告

> 调研时间：2026-07-23 11:06 → 11:08（站长追加指令）
> 状态：**仅调研 + 推荐**，**未安装任何东西**

---

## 📊 项目身份（事实核查结果）

| 维度 | 内容 |
|------|------|
| **项目名** | ego (lite) / ego-browser |
| **官网** | https://lite.ego.app |
| **GitHub** | https://github.com/citrolabs/ego-lite |
| **skill 名** | ego-browser（v1.2.6，2026-07-20 最新） |
| **安装** | `npx skills add citrolabs/ego-lite` 或 macOS dmg |
| **价格** | 完全免费 |
| **平台** | macOS 现在 ✅ / Windows/Linux roadmap |
| **自定义** | 自定义 Chromium 内核（非 stock Chrome）|

## 🏆 关键能力（从 SKILL.md + 官网读到的真实功能）

| # | 能力 | 我们能否实现 |
|---|------|------|
| 1 | **Space 隔离**（每个 agent 独立空间，agent 不会抢用户的 tab）| ❌ 我们没实现（多 agent 共用 CDP 18800） |
| 2 | **3.45x faster** 复杂任务 | ❌ 我们是 1x baseline |
| 3 | **强 snapshot 质量**（iframe / shadow DOM / Stripe SDK）| ❌ 默认 Chromium 经常在这些场景失败 |
| 4 | **2.5x faster 复杂 workflow + 更高成功率** | ⚠️ 我们靠 stealth 包了一层 |
| 5 | **agent-native / Code-based**（不靠 CLI 调用） | ❌ 我们用 Playwright Python asyncio |
| 6 | **自动 import Chrome 数据**（首次启动问一次） | ❌ 我们手动管理 cookie |
| 7 | **节省 token**（语义 snapshot 比 JS shim 省 60%+） | ⚠️ 部分省（stealth 后减少重试） |

## 🎯 最值得的 3 个卖点

### 1️⃣ Space 隔离 —— **直接解决我们 agent 抢 Chrome 的痛点**
现在 douyin_index.py / xiaohongshu_crawl.py 都在用同一个 CDP 18800，多 cron 同时跑会抢同一个 tab。
**ego(lite) 给每个 agent 一个独立 Space**，互不干扰。

### 2️⃣ 强 snapshot —— **解决 iframe / shadow DOM / 第三方 SDK 内容抓不到**
我们 6/2 飞书 11310 错误码 / 7/13 小红书后台 not_logged_in 连续 9 日——
很多都是 iframe 边界场景被卡。ego 自定义内核能深入。

### 3️⃣ 真 0 设置接入 —— **agent 不需改 1 行 Python**
npx skills add 一行 = 6 个 agent 全自动加载。vs 我们每个 cron 都要手改 Python。

## 📋 安装路径（3 选 1，按你风险偏好）

| 选项 | 描述 | 风险 |
|------|------|------|
| **A** | `npx skills add citrolabs/ego-lite` 仅装 skill | 🟢 低（仅 skill 文件，未装 app）|
| **B** | 装 macOS dmg 完整版（接管 Chrome 数据）| 🟡 中（首次会问是否迁移 Chrome cookies）|
| **C** | 不装，继续用 CDP 18800 + stealth | 🟢 0 |

**推荐先做 A**（仅装 skill 不装 app），看你给不给 macOS app 接管 cookie。

## 🔍 spike 评估（推荐先做）

| 步骤 | 行动 | 时间 | 风险 |
|------|------|------|------|
| 1 | `npx skills add citrolabs/ego-lite` | 30s | 🟢 低 |
| 2 | 检查 OpenClaw 是否自动加载 ego-browser skill | 30s | 🟢 低 |
| 3 | 看 SKILL.md 完整内容（citrolabs/ego-lite/SKILL.md）| 5 min | 🟢 低 |
| 4 | 评估：能否让现有 douyin/xhs 脚本迁移到 ego 模式 | 30 min | 🟡 中 |
| 5 | 实测：用 ego-browser 完成一次抖音采集对比 | 1h | 🟡 中 |

**不主动跑 spike**，等站长拍板。

## 📦 与现有体系的兼容性

| 维度 | 兼容性 |
|------|------|
| **现有 CDP 18800 Chrome** | ✅ 兼容（ego 接管 cookie 是可选）|
| **douyin_index.py v12 (stealth)** | ⚠️ 可并存（stealth wrap 在 Playwright 层）|
| **send_feishu_card.py** | ✅ 不受影响（飞书仍走 curl）|
| **feishu 4 件套插件** | ✅ 不受影响（飞书域）|
| **playwright_stealth venv** | ✅ 不受影响（独立 venv）|
| **pdf_ocr_to_md.py** | ✅ 不受影响 |

## 🛡️ 我没做的事（按 7/13 铁律）

- ❌ **没主动安装任何东西**（npx skills add / dmg）
- ❌ **没让 ego 接管 Chrome 数据**
- ❌ **没改 douyin_index.py**（CDP 18800 路径已 v12 stealth 完成）

## 🎯 推荐 spike 顺序（站长决策）

**第一优先（5 min）**：
```
npx skills add citrolabs/ego-lite
# 然后 read SKILL.md 的完整内容
```
**目的**：评估技能形态，不动浏览器。

**第二优先（1-2 h）**：实测 ego-browser vs CDP 18800 的抖音采集
**目的**：验证 ego 真快 3.45x / 能解决我们 iframe 问题

**第三优先（待评估）**：迁移现有脚本到 ego 模式
**目的**：长期收益

---

## 📎 关联文档

- GitHub 调研历史：`memory/topics/github-research-history.md`
- W30 候选推荐：`wiki/系统/W30-GitHub-skill-TOP5-spike-清单.md`
- W30 spike 实战：`wiki/系统/W30-GitHub-skill-spike-实战报告.md`
- 现有 CDP 体系：`USER.md` 的"专属浏览器" + `scripts/douyin_index.py` v12

---

**报告人：李涯 · 2026-07-23 11:08**
**状态：仅调研，等站长拍板 spike**
