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

## 浏览器技术栈原则（2026-04-20确立，2026-04-23更新）

**专属浏览器**：CDP端口 **18800**，所有任务统一用 `target=host`
- 标签0：小红书灵犀 https://idea.xiaohongshu.com/idea/trend/trendAnalyze
- 标签1：百度
- 标签2：抖音订阅页 https://creator.douyin.com/creator-micro/creator-count/my-subscript
- 标签3：抖音iframe
- 标签4：抖音关键词页 https://creator.douyin.com/creator-micro/creator-count/arithmetic-index
- 标签5：抖音iframe
- 标签6：小红书探索页 https://www.xiaohongshu.com/explore

**定时自动任务**：一律用 Playwright 脚本，不依赖 browser-use CLI
- 抖音数据采集 → `douyin_index_v9.py`（Playwright）
- 竞品动态追踪 → `competitor_program_tracker.py`（Playwright）

**browser-use 使用规则**：
- **全面禁止**：包括专属 Chrome 标签页的任何操作，一概拒绝
- **唯一例外**：临时性/没遇到过/复杂的探索任务（新平台/一次性调研），且 Playwright 脚本无法快速覆盖时，才能用
用户指定PRO模型名: deepseek-v4-pro
用法:
- 默认: deepseek/deepseek-v4-flash（闪速版）
- 特定任务: 用户说用PRO/v4pro时 → model="deepseek/deepseek-v4-pro"

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

当需要**快速验证新数据源可行性**时，用spike代替直接写完整生产脚本：
1. 先确认具体可行性问题
2. 快速查文档确定方案
3. 建最小可运行验证物（`.tmp/openclaw-spikes/`）
4. 测一个边缘情况
5. 输出 VALIDATED / PARTIAL / INVALIDATED

适用场景：新竞品API、新的数据采集接口、替代方案A/B对比
不适合：日常已有成熟脚本的数据采集

