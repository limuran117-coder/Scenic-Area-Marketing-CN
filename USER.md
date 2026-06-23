# USER.md - 关于站长

- **Name:** 站长
- **称呼:** 站长
- **Timezone:** Asia/Shanghai (GMT+8)
- **Notes:** 建业电影小镇景区运营负责人

## Context

站长负责建业电影小镇的景区营销与运营工作，核心目标是：
- 年度客流目标：153万（2026-04-22调增，原132万）
- 年度营收目标：1.2亿

**日常自动化任务（2026-04-23更新）：**
- 抖音指数日报（10:30）
- 全国景区动态（10:00）
- 文旅政策与资本（14:00）
- 竞品关键词深度分析（15:00）
- 竞品内容动态（18:00）
- 全国爆款拆解（21:00）
- 每日复盘整合（22:00）

**核心文件：**
- 抖音指数脚本：`~/.openclaw/workspace/scripts/douyin_index.py`（内部v11）
- 抖音Cookie：`/tmp/juLiang_cookies.json`（代理 127.0.0.1:7897 — ✅ 2026-06-08 09:21 实测：代理在 LISTEN，cookie 文件正常回写。采集链健康。）
- 抖音数据订阅页：https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator
- 小红书采集脚本：`~/.openclaw/workspace/scripts/xiaohongshu_crawl.py`
- 小红书Cookie：`/tmp/xiaohongshu_cookies.json`（代理 127.0.0.1:7897 — ✅ 同上，2026-06-08 实测健康）
- 小红书灵犀后台：https://idea.xiaohongshu.com/idea/welcome/index（账号：建业电影小镇官方ID:530883）
- 历年客流数据（2023-2025）：`~/Desktop/2023-2025年门票销售及客流统计数据表.xlsx`（**唯一权威来源，禁止混用其他数据**）
- 2026年客流数据（⚠️ **2026-06-23 SSOT 迁移**）：
  - **新位置（永久）**：`~/Downloads/2026游客量统计 (N).csv` + `~/Downloads/电影小镇-2026年数量统计.dbt(N).xlsx`
  - 旧位置 `~/Desktop/2026游客量统计.csv` **已弃用**（截至6/9）
  - **更新频率**：每周二更新一次（最新 6/21）
  - **未来所有客流数据都在 ~/Downloads/**（站长 6/23 确认）
- 飞书群：oc_2581c03b79e4893cc3616b253d60f34e（电影小镇群）

**专属浏览器（CDP端口18800）**：所有任务用 `connect_over_cdp(CDP_URL)` 动态 navigate，**生产脚本不依赖固定 tab 编号**

#### 软规范 Tab 参考（2026-06-08 清理，USER.md 为权威）
> ⚠️ **重要**：以下 Tab 编号是参考性软规范，**仅供人工维护 Chrome 标签时参考**。
> 实际所有采集脚本（douyin_index.py / xiaohongshu_crawl.py 等）都用 `connect_over_cdp(CDP_URL)` 动态 navigate，**不依赖固定 tab 编号**。
>
> **灵犀保活 6/9 已移除**（`openclaw cron remove 8535705a`）：站长判定 `*/45 * * * *` 高频保活浪费 token 且与高峰任务抢资源。如需保活，手动访问灵犀后台或偶发任务时触发。
> 即使 Tab 编号乱了，**生产任务仍能正常跑**。

| Tab | 用途 | URL |
|-----|------|-----|
| Tab0 | 小红书灵犀后台 | https://idea.xiaohongshu.com/idea/welcome/index |
| Tab1 | 抖音搜索页 | https://www.douyin.com/search/ |
| Tab2 | 空白页（可新建临时） | about:blank |
| Tab3 | 百度搜索 | https://www.baidu.com/ |
| Tab4 | 抖音指数核心页（搜索框+我的订阅） | https://creator.douyin.com/creator-micro/creator-count/my-subscript |
| Tab5 | 小红书探索页（搜索入口） | https://www.xiaohongshu.com/explore?channel_type=web_user_page |
| Tab6 | 微博热搜 | https://weibo.com/ ✅已登录 |

**已知历史包袱**（无需立即处理）：
- TOOLS.md 旧版有第二套 Tab 定义（与本规范不同）—— 2026-06-08 标记为废弃参考
- `init_chrome_tabs.py` 和 `cdp_restore_tabs.py` 是孤儿脚本——已移到 `archive/`（2026-06-08）
- 实际 Chrome 14+ 个 tab 经常累积（service worker / blob / 临时任务）——不影响生产任务，可定期人工清理

---

_随着交流深入，持续更新_
