# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

## 天气查询（2026-05-23新增）

用 wttr.in 查天气，无需任何配置：
```bash
curl "wttr.in/中牟?format=%l:+%c+%t,+feels+%f,+rain+%p,+wind+%w"
curl "wttr.in/郑州?format=j1"   # JSON格式
```

**用途：** 日报中附加当日天气预报，天气直接决定主题公园客流，辅助判断客流波动原因。
- 中牟县（电影小镇所在地）每日天气
- 郑州/开封区域天气（覆盖主要客源地）

---

## 浏览器技术栈原则（2026-04-20确立，2026-04-23更新，2026-06-08清理）

**专属浏览器**：CDP端口 **18800**，所有任务统一用 `connect_over_cdp(CDP_URL)` 动态 navigate
- **权威 Tab 软规范**：`workspace/USER.md` 表格（2026-06-08 清理为单一权威）
- **本节旧的"标签0-6"列表已废弃**（与 USER.md 不一致，2026-06-08 标记废弃）
- 所有生产脚本用 `connect_over_cdp(CDP_URL)` 不依赖固定 tab 编号，**即使 Tab 乱了采集仍正常**

**定时自动任务**：一律用 Playwright 脚本，不依赖 browser-use CLI
- 抖音数据采集 → `douyin_index.py`（Playwright，脚本名是文件版，内部v11）
- 竞品动态追踪 → `competitor_program_tracker.py`（Playwright）

**browser-use 使用规则**：
- **全面禁止**：包括专属 Chrome 标签页的任何操作，一概拒绝
- **唯一例外**：临时性/没遇到过/复杂的探索任务（新平台/一次性调研），且 Playwright 脚本无法快速覆盖时，才能用
用户指定PRO模型名: MiniMax-M1（MiniMax Pro）
- 6/8 之后 M3-only 模式：默认 model = `minimax/MiniMax-M3`（M3 闪速版）
- 特定任务：用户说用 PRO/MiniMax Pro 时 → model=`minimax/MiniMax-M1`（需要先把 M1 加回 openclaw.json providers）
- ⚠️ **fallback 链已清空**（6/6 站长决策）：失败要让站长知道，不静默降级

---

## GitHub/版本控制

**已验证可用**（2026-05-30周度技能探索确认）：
```bash
gh auth status    # ✅ Logged in as limuran117-coder
```
- Remote: `limuran117-coder/Scenic-Area-Marketing-CN`
- git + gh CLI + Obsidian Git插件自动备份
- 无需额外配置，已正常运作

---

## spike工作流模式（参考·非工具）

系统技能 `spike` 已提供标准化流程（`~/.npm-global/lib/node_modules/openclaw/skills/spike/SKILL.md`）。

当需要**快速验证新数据源可行性**时，用spike代替直接写完整生产脚本：
1. 先确认具体可行性问题
2. 快速查文档确定方案
3. 建最小可运行验证物（`.tmp/openclaw-spikes/`）
4. 测一个边缘情况
5. 输出 VALIDATED / PARTIAL / INVALIDATED

适用场景：新竞品API、新的数据采集接口、替代方案A/B对比
不适合：日常已有成熟脚本的数据采集

---

## 视频帧提取（2026-06-06确认可用）

ffmpeg已安装 ✅，系统技能 `video-frames` 可用：
```bash
# 提取第一帧
~/.npm-global/lib/node_modules/openclaw/skills/video-frames/scripts/frame.sh video.mp4 --out /tmp/frame.jpg

# 提取指定时间点
~/.npm-global/lib/node_modules/openclaw/skills/video-frames/scripts/frame.sh video.mp4 --time 00:00:10 --out /tmp/frame-10s.jpg
```

**用途：** 竞品抖音/小红书视频内容分析时，提取关键帧辅助判断内容策略。按需使用，不纳入日常流程。

---

## 图表生成（2026-06-06评估，同日更新）

**diagram-maker**（系统技能）：可生成SVG/HTML/Excalidraw图表，无需任何依赖。
适用场景：季度战略报告可视化、竞品定位图、趋势图。
```bash
# 直接生成，无需安装任何工具
# 输出到指定路径即可
```
**VS** `fireworks-tech-graph`（workspace技能）：需 `rsvg-convert`（未安装），暂不使用。
**选择**：日常图表需求用 diagram-maker，它无依赖、即开即用。

## PDF处理（2026-06-06评估）

`nano-pdf` 技能可通过自然语言编辑PDF，但需安装CLI：
```bash
uv tool install nano-pdf  # 未安装
```
适用场景：处理PDF格式的文旅政策文档、提取数据。
当前状态：暂不安装，待有PDF处理需求时再评估。

## 飞书文档（2026-06-06评估）

`feishu-doc/drive/perm/wiki` 插件技能可读写飞书文档（支持表格）。
适用场景：将日报写入飞书Docx实现持久化存档（替代临时卡片）。
上线前提：需验证飞书App凭证是否已配置。
当前状态：卡片格式运行良好，暂不切换。团队有需求时试点。

---

## 成本追踪（2026-06-06评估）

`model-usage` 技能需要 `codexbar`（未安装）。
当前token成本未追踪，如果日后消耗显著增长可安装brew cask `steipete/tap/codexbar` 启用。

---

## Python调试（2026-06-06新增）

系统技能 `python-debugpy` 提供Python调试工具链：
```bash
# 快速断点调试（无需安装）
python3 -m pdb path/to/script.py

# 异常后自动进入调试
python3 -m pdb -c continue path/to/script.py

# 远程调试（需先 pip install debugpy）
python3 -m debugpy --listen 127.0.0.1:5678 --wait-for-client path/to/script.py
```

**用途：** Playwright脚本（douyin_index.py等）出问题时快速定位bug。
- `pdb` 无需额外安装，python3自带
- `debugpy` 需要 `pip install debugpy`（按需安装）
- 调试完毕后清理断点：`rg -n 'breakpoint\(|pdb\.set_trace' --type py`

---

## 1Password密钥管理（2026-06-06评估）

1Password CLI (`op`) 已安装（`/opt/homebrew/bin/op`）但未配置登录。
可用于集中管理cookie/API key等敏感凭证，当前cookie存放在 `/tmp/` 下已满足需求。
如果日后新增需要API key的外部服务，可配置1Password统一管理。

---

## 系统安全审计（2026-06-06评估）

`healthcheck` 技能提供系统安全审计（SSH/防火墙/备份/磁盘加密等）。
当前 `system-metabolism` 已覆盖常规维护，healthcheck更偏安全加固。按需使用。

---

## diff/issue工具（2026-06-06评估）

- `diffs` 工具：生成可分享的diff视图（URL/PNG/PDF），代码修改时可替代手动摘要
- `gh-issues` 技能：GitHub Issues自动化（筛选→修复→PR），可用于脚本维护的bug追踪
- gh CLI已可用，必要时两个工具可直接使用，无需额外配置

---

## 周度技能探索 #3（2026-06-06 10:51 真实spike）

**已 spike 验证的工具/能力：**

| 能力 | 验证结论 | 行动 |
|------|----------|------|
| `@steipete/summarize`（npm） | ✅ **装上**（25s）但需 `OPENAI_API_KEY` 或 `OPENROUTER_API_KEY`，当前无 | **PARTIAL** — 等站长提供 key；装好后可替代人工读公众号文章/竞品新闻 |
| `oracle`（第二模型审查） | ❌ 同上，需 OpenAI API key，不兼容 deepseek | **暂搁置** — 没有可用 API key |
| `blogwatcher`（RSS监控） | ⚠️ brew 无包，需 go 装 | **暂不装** — 已有 `industry_news_rss.py` 覆盖该能力 |
| `mcporter`（MCP CLI） | ❌ 未装，使用场景与当前 chrome CDP 18800 重复 | **跳过** |
| `feishu-doc`（飞书云文档写入） | ⚠️ 凭证未验证 | **暂缓** — 卡片格式已稳定 |
| 现有 lint/drift 双跑 | ✅ 已确认可执行，发现 22 个脚本URL/版本漂移 | **新增 cron** — 每周一/三/五跑 `wiki_drift_check.py` + `project_drift_check.py`，把 stale 提前 1 周发现 |

**修正已存在的文档漂移（本次确认 → 已修）：**
- ~~`scripts/douyin_index.py` 文件**已不存在**~~ ✅ 2026-06-06 已修复：`scripts/douyin_index_v9.py` → `scripts/douyin_index.py`（内部 v11）
- ✅ `wiki/entities/scripts/README.md` 同步更新为新名（44 个文件 / 87 处替换）
- ✅ `wiki/entities/scripts/douyin_index.md` 文档重命名 + 内容更新为 v11
- ✅ 4 个 SVG 数据流图（data-pipeline, system-architecture 中英文版）已更新
- ✅ `wiki/SOP/抖音指数日报.md` 标记 v10 → v11
- ✅ `IDENTITY.md` 第 24 行 fixer bug 修复（"原 douyin_index_v9.py 已重命名"）
- ✅ `ai-pipeline-diagrams.html` 8:00 触发脚本名更新

**WIKI lint 真实数据（重扫后修正，2026-06-06 16:26）：**
- 用 `last_update` 字段重扫 0 个真 stale 文档（TOOLS.md 之前 37-38 天为误报）
- 实际漂移：0 处已知（除 2 处历史梦境快照引用的 `weather_auto.py`，那是历史）
- 下次 `wiki_drift_check` 跑完应推送到 `wiki/lint-result.json` 并附飞书提醒

---

## 配置追踪（2026-06-06）

| 配置项 | 当前值 | 来源 |
|--------|--------|------|
| Gateway | 18789（localhost LISTEN ✅） | `lsof -i :18789 -sTCP:LISTEN` |
| CDP 端口 | 18800（localhost LISTEN ✅） | `lsof -i :18800 -sTCP:LISTEN` |
| 抓站代理 | 7897 ✅ **LISTEN**（2026-06-08 09:21 实测修正）| `python3 ~/.hermes/hermes-agent/openclaw-watch/bin/chain_health.py` |
| 抖音 Cookie | ✅ 存在（1.2h 前回写，2026-06-08 09:21 实测） | 同上 |
| 小红书 Cookie | ✅ 存在（1.2h 前回写） | 同上 |
| OpenClaw cron 存储 | `~/.openclaw/state/openclaw.sqlite`（不是 jobs.json） | `lsof -i :18789 -sTCP:LISTEN -t \| xargs -I {} lsof -p {} \| grep openclaw.sqlite` |
| jobs.json 状态 | 不存在磁盘上，OpenClaw 启动时从 SQLite 重建 | `ls ~/.openclaw/cron/jobs.json` |
| jobs.json.migrated | 6/2 06:51 归档版本（35 任务，已不反映现役 28 任务） | `ls -la ~/.openclaw/cron/` |
| **14:00 cron 冲突** | ~~`竞品内容动态` 0 14 * * 1-5 与 `竞品关键词深度分析` 同分钟~~ ✅ **2026-06-08 已修**：竞品内容动态 改为 `30 14 * * 1-5`（用 `openclaw cron edit --cron "30 14 * * 1-5" <id>`） | `openclaw cron list` |
| **周日 9:00 cron 冲突** | ~~`系统代谢` 0 9 * * 0 与 `周日系统升级+GitHub推送` 同分钟~~ ✅ **2026-06-08 已修**：系统代谢 改为 `30 9 * * 0`（让升级任务先跑） | `openclaw cron list` |
| Python | 3.12.13（homebrew） | `python3 --version` |
| Node | v25.8.2 | system |
| uv | `/Users/tianjinzhan/.local/bin/uv` | PATH |
| gh | `/opt/homebrew/bin/gh`（已登录 limuran117-coder） | `gh auth status` |
| ffmpeg | 已安装 | brew |
| `openai` Python 包 | ❌ 未装 | `python3 -c "import openai"` |
| `feedparser` Python 包 | ❌ 未装（industry_news_rss.py 需要） | pip |
| @steipete/summarize | ✅ 已装 0.14.1 | `npm install -g` |



## 周度技能探索 #4（2026-06-06 23:18 cron 真实spike）

**扫描范围（步骤 1 完成）：**
- `scripts/`：56 个脚本
- `~/.npm-global/lib/node_modules/openclaw/skills/`：58 个系统技能
- 已装 CLI（PATH）：`gh` `/usr/bin/curl` `jq` `ffmpeg` `summarize`（@steipete/summarize 0.14.1）
- 未装但可 brew 装：`peekaboo 3.3.0`（steipete/tap）、`remindctl`、`openhue`、`imsg`、`goplaces`（需 `GOOGLE_PLACES_API_KEY`）、`gogcli`（需 OAuth）

**LLM 评估（步骤 2）：挑 2 个最值得试点的工具**

| 工具 | 验证结论 | 行动 |
|------|----------|------|
| `peekaboo 3.3.0`（macOS UI 自动化） | ⚠️ 当前用 Playwright + CDP 18800 跑浏览器，能覆盖 90% 站长场景；peekaboo 唯一独特价值是驱动**原生 Mac 应用**（Mail.app / 备忘录 / 系统设置 / 文件对话框），但景区运营场景几乎用不到 | **暂不装** — 边际收益低，brew install 等待 30s 不值得。`/usr/sbin/screencapture` 已原生可用，本周没有 `peekaboo capture` 的真实需求。**触发安装条件**：未来需要把"系统级弹窗"或"非浏览器 app"截图/操作纳入日报自动化时再装 |
| `imsg`（iMessage/SMS CLI） | ⚠️ 飞书群 `oc_2581c03b79e4893cc3616b253d60f34e` 已是站长主沟通渠道，iMessage 仅在老板个人沟通时用。CLI 价值：cron 把日报**降级推送**到 iMessage 作为飞书群的 backup | **暂不装** — 飞书卡片稳定运行，iMessage 推送是 nice-to-have 不是 must-have。**触发安装条件**：当站长要求"飞书不在线时也确保收到日报"时再装 |

**结论**：本周没有"必须立刻装"的工具。`TOOLS.md` 已记录这两个候选项的触发安装条件，避免后续重复评估。

**已完成漂移/质量基线（沿用 #3 评估）：**
- `wiki_drift_check.py` + `project_drift_check.py`：每周一/三/五 cron 已配
- `self_check.py`：每次 isolated 任务完成后自动评分
- WIKI lint 0 处真 stale
