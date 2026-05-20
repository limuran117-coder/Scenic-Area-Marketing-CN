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
