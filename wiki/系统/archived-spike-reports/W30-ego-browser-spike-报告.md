---
title: W30 ego-browser + crawl4ai 双 spike 报告
type: github-research + spike
created: 2026-07-23 11:15
owner: 李涯
period: W30
tags: [ego-browser, ego-lite, crawl4ai, agent-browser, spike]
status: skill-installed + crawl4ai-verified
---

# W30 ego-browser + crawl4ai 双 spike 报告

> 站长指令："A, 然后 crawl4ai"  
> 实测时间：2026-07-23 11:11 → 11:15  
> 状态：**ego-browser skill 已装** ✅ + **crawl4ai spike 验证通过** ✅

---

## ✅ Spike #1 — ego-browser skill（已装）

### 安装路径

由于 `npx skills add` 默认进入交互式 TUI（让你从 47 个 agent 里选），我直接 **从 GitHub raw 下载到 `~/.openclaw/workspace/skills/ego-browser/`**：

```bash
mkdir -p ~/.openclaw/workspace/skills/ego-browser/references
curl https://raw.githubusercontent.com/citrolabs/ego-lite/main/skills/ego-browser/SKILL.md > .../SKILL.md
curl https://raw.githubusercontent.com/citrolabs/ego-lite/main/skills/ego-browser/references/install.md > .../references/install.md
```

### OpenClaw 识别情况

```text
ego-browser ✓ Ready
Source: openclaw-workspace
Path: ~/.openclaw/workspace/skills/ego-browser/SKILL.md
Visible to model: yes
Available as command: yes
```

🎉 **skill 已就位** —— 但**实际命令 `ego-browser` 来源于 macOS app**（未装）。

### 我没做的事（你拍板）

| ❌ 没做 | 原因 |
|---------|------|
| 没装 ego-lite.dmg | 首次会接管 Chrome cookie 数据 |
| 没试 `/ego-browser follow ...` | 无 macOS app，不能跑命令 |
| 没改 douyin_index.py 接入 ego | skill 不带 cli，需要 app |

### 何时它真生效

如果你装 macOS app（dmg 下载），**OpenClaw 会自动识别 `ego-browser` 命令**即可用。

---

## ✅ Spike #2 — crawl4ai 实战验证通过

### 安装

```bash
uv pip install --python /tmp/spike_venv/bin/python3 crawl4ai==0.9.2
/tmp/spike_venv/bin/python3 -m playwright install chromium  # 93.5 MiB 下载
```

### 验证步骤

| 步骤 | 命令 | 结果 |
|------|------|------|
| 库 import | `import crawl4ai` | ✅ |
| 抓 example.com | `AsyncWebCrawler().arun("https://example.com")` | ✅ Status 200，markdown 122 chars |
| 抓抖音 my-subscript | `AsyncWebCrawler().arun("https://creator.douyin.com/...")` | ✅ Status 200，"加载中..." (因为无 cookie)|

### crawl4ai 真实数据

| 项 | 值 |
|----|---|
| GitHub | unclecode/crawl4ai |
| ⭐ Stars | **74,230** |
| 最新版 | v0.9.2 (2026-07-15 发布) |
| 平台 | Python 3.10+ |
| 安装 | `pip install crawl4ai` + `crawl4ai-setup` |
| API 风格 | async (`AsyncWebCrawler`) |
| 输出 | LLM-ready markdown |

### 我们场景的潜在价值

| 维度 | 我们现状 | crawl4ai 优势 |
|------|---------|--------------|
| 抖音日报 | douyin_index.py 硬编码 selector + regex | 通用 markdown 提取 |
| 小红书日报 | xiaohongshu_crawl.py 类似 | 同上 |
| 周度竞争格局报告 | weekly_visitor_report.py | 同上 |
| 飞书 wiki 同步 | curl 模拟 | 可抓飞书 wiki HTML 转 markdown |
| 政府文旅政策 PDF | 手工 grep | crawl4ai 支持 PDF/含表格 |

### ⚠️ 关键限制（实测发现）

1. **crawl4ai 默认 headless**（强反爬需要手动配置 stealth）
2. **无 cookie 抓不登录内容**（抖音"加载中..."）—— 跟我们的方案一样
3. **需要单独装 chromium**（93 MB）
4. **不是 CDP 模式** —— 不与我们 CDP 18800 Chrome 兼容

## ❌ crawl4ai 当前阶段**不推荐 spike 集成**

理由：
- 我们 CDN 18800 Chrome + stealth wrap 已经能跑出 8 景区数据
- crawl4ai 默认 headless 反而抓不到我们需要的"已登录 dashboard"
- 集成需要重构 douyin_index.py 主逻辑（5+ 小时）
- 收益有限

**建议**：crawl4ai 适合 LLM 抓公开网页（文档、政策、新闻、案例库），**不适合我们当前的"已登录 dashboard 抓取"**。

**真要用 crawl4ai 替代某个东西** → 应该是**信息源采集**（如自动同步飞书 wiki 到本地知识库），不是采集脚本。

---

## 📦 已实际成果

| 成果 | 路径 | 状态 |
|------|------|------|
| ego-browser SKILL.md | `~/.openclaw/workspace/skills/ego-browser/SKILL.md` (18.9KB) | ✅ |
| ego-browser install.md ref | `~/.openclaw/workspace/skills/ego-browser/references/install.md` | ✅ |
| OpenClaw 识别 ego-browser | `openclaw skills info ego-browser` | ✅ Ready |
| crawl4ai 0.9.2 + chromium | `/tmp/spike_venv/` (在 venv 跑) | ✅ |
| crawl4ai 抖音实测 | "加载中..." (无 cookie 预期行为) | ✅ |

---

## 🎯 推荐行动

| 选项 | 描述 | 时间 |
|------|------|------|
| A. 不动 | 保持现状（技能已装，crawl4ai 已 spike，无副作用）| 0 |
| B. 装 ego-lite.dmg | macOS app 接管 Chrome cookies，**接管前先跟你确认** | 5 min + 安装 |
| C. 试用 crawl4ai 做 wiki 同步 | 写小脚本自动同步飞书 wiki 到本地知识库 | 1-2 h |

## 🛡️ 我做的事 / 没做的事

| ✅ 做了 | ❌ 没做 |
|--------|--------|
| ego-browser skill 文件下载到 OpenClaw 加载目录 | 装 macOS app |
| OpenClaw 验证 skill 识别 | 跑 `/ego-browser follow ...` |
| crawl4ai 装上 + 跑 example.com 验证 API | 改 douyin/xhs 脚本 |
| 抖音 my-subscript 实测（确认预期行为）| 让它接管 CDP 18800 |

---

**报告人：李涯 · 2026-07-23 11:15**
**ego-browser skill 真装上 + crawl4ai spike 实跑验证**
