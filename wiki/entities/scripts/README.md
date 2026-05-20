# Scripts 索引

> 所有运营脚本索引 | 最后更新：2026-04-26

---

## 核心运营脚本

| 脚本 | 用途 | 执行频率 |
|------|------|---------|
| [[douyin_index_v9]] | 抖音指数数据采集（8大景区排名） | 每日10:30 cron |
| [[xhs_competitor_crawl]] | 小红书竞品数据采集 | 每日10:00 cron |
| [[query_passenger]] | 客流数据查询（Excel） | 按需/日报引用 |
| [[send_feishu_card]] | 飞书卡片发送（统一入口） | 所有飞书任务 |
| [[industry_news_browser]] | 行业热点采集（文章正文版） | 每日14:00 cron |
| [[industry_news_rss]] | 行业热点RSS采集 | 备用采集 |
| [[competitor_keyword_v8]] | 竞品关键词分析 | 每日15:00 cron |
| [[wiki_drift_check]] | Wiki漂移检查 | 每周日cron |
| [[build_xhs_card]] | 小红书报告卡片构建 | 供小红书日报使用 |
| [[send_wenhua_tracking]] | 文旅热点追踪卡片 | 每日12:00 cron |
| [[send_industry_news]] | 行业热点发送 | 每日14:00 cron |
| [[case_library_scan]] | 案例库扫描 | 每周五09:00 cron |
| [[xiaohongshu_crawl]] | 小红书数据原始采集 | 备用/对比 |
| [[sync_obsidian_daily]] | Obsidian每日同步 | 每日05:00 cron |
| [[self_check]] | 系统自检 | 按需 |
| [[llmwiki_ingest]] | Wiki知识库摄入 | 按需 |
| [[llmwiki_lint]] | Wiki语法检查 | Wiki维护 |

---

## 技术支撑脚本

| 脚本 | 用途 |
|------|------|
| [[competitor_keyword_debug]] | 竞品关键词调试（各版本） |
| [[cdp_collect]] / [[cdp_douyin]] | CDP浏览器采集 |
| [[cdp_keyword_deep]] | 关键词深度CDP采集 |
| [[competitor_program_tracker]] | 竞品节目动态追踪 |
| [[init_chrome_tabs]] | 浏览器标签页初始化 |
| ~~[[{old}]~~（已删除）]] | 周期性提醒 |
| [[project_drift_check]] | 项目漂移检查（2026-05-17创建） |
| [[wiki_drift_check]] | Wiki漂移检查（2026-05-17创建） |

---

## 数据管理脚本

| 脚本 | 用途 |
|------|------|
| [[build_dashboard]] | 数据可视化看板 |
| [[dashboard]] | 基础仪表盘 |

---

## 实验/废弃脚本

| 脚本 | 状态 |
|------|------|
| douyin_browser_final.py | 废弃（v9已替代） |
| competitor_keyword_v2-v7.py | 废弃（v8已替代） |
| send_wenhua_tracking_20260421.py | 旧版（保留参考） |
| test_card_send.py | 测试用 |
| competitor_keyword_debug2.py | 调试用（debug替代） |

---

## 废弃脚本清理建议（2026-05-17）

以下废弃文件建议移入 `scripts/archive/` 减少目录杂乱：
- `douyin_browser_final.py`
- `competitor_keyword_v2.py` ~ `v7.py`（共6个）
- `test_card_send.py`
- `send_wenhua_tracking_20260421.py`

---

*本索引最后更新：2026-05-17*
