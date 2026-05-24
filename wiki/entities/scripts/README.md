# Scripts 索引

> 所有脚本索引 | 最后更新：2026-05-24（漂移检查后同步）

---

## 核心运营脚本

| 脚本 | 用途 | 执行频率 |
|------|------|---------|
| `douyin_index_v9.py` | 抖音指数数据采集（8大景区排名） | 每日10:30 cron |
| `xiaohongshu_crawl.py` | 小红书数据采集（备用） | 备用/待解封 |
| `xhs_competitor_crawl.py` | 小红书竞品数据采集 | 每日10:00 cron |
| `send_feishu_card.py` | 飞书卡片发送（统一入口） | 所有飞书任务 |
| `industry_news_browser.py` | 行业热点采集（文章正文版） | 每日14:00 cron |
| `industry_news_rss.py` | 行业热点RSS采集 | 备用采集 |
| `competitor_keyword_v8.py` | 竞品关键词分析（v8最终版） | 每日15:00 cron |
| `cdp_keyword_deep.py` | 关键词深度CDP采集 | 每日15:00 cron调用 |
| `build_xhs_card.py` | 小红书报告卡片构建 | 供小红书日报使用 |
| `build_dashboard.py` | 数据可视化看板 | 按需 |
| `send_wenhua_tracking.py` | 文旅热点追踪卡片 | 每日12:00 cron |
| `send_industry_news.py` | 行业热点发送 | 每日14:00 cron |
| `send_case_lib_update.py` | 案例库更新发送 | 每周五09:00 cron |
| `send_marketing_case_qyshy.py` | 营销案例发送（清明上河园） | 按需 |
| `send_w16_report.py` | W16周报发送 | 按需 |
| `case_library_scan.py` | 案例库扫描 | 每周五09:00 cron |
| `competitor_program_tracker.py` | 竞品节目动态追踪 | 按需 |
| `sync_obsidian_daily.py` | Obsidian每日同步 | 每日05:00 cron |
| `wiki_drift_check.py` | Wiki漂移检测 | 每周日11:00 cron |
| `project_drift_check.py` | 项目漂移检测 | 每周日11:00 cron |
| `cdp_cookie_hub.py` | CDP Cookie总控（批量同步Cookie） | 每日08:05 cron |
| `competitor_keyword_debug.py` | 竞品关键词调试 | 调试用 |
| `competitor_keyword_index.py` | 竞品关键词指数页采集 | 按需 |
| `autonomous_skill_create.py` | 自动发现重复任务生成Skill | 按需 |
| `confirm_action.py` | 高风险操作确认 | 被各脚本调用 |
| `nudge_knowledge.py` | 任务结束前检查"学到的知识" | cron任务尾部嵌入 |
| `periodic_nudge.py` | 主动检查被忽略上下文/规则冲突 | 后台定期 |
| `query_passenger.py` | 客流数据查询（Excel） | 日报引用 |
| `self_check.py` | 任务完成后自动评估打分 | cron任务尾部 |
| `validate_data.py` | 采集数据异常检测 | 按需 |

## 技术支撑脚本

| 脚本 | 用途 |
|------|------|
| `cdp_collect.py` | CDP基础采集框架 |
| `cdp_collector.py` | CDP采集器 |
| `cdp_douyin.py` | 抖音CDP采集 |
| `cdp_restore_tabs.py` | 浏览器标签页恢复 |
| `init_chrome_tabs.py` | 浏览器标签页初始化 |
| `llmwiki_ingest.py` | Wiki知识库摄入 |
| `llmwiki_lint.py` | Wiki语法检查 |
| `llmwiki_query.py` | Wiki知识库查询 |
| `dashboard.py` | 基础仪表盘 |

## 废弃脚本（已移入 scripts/archive/）

| 脚本 | 替代 | 状态 |
|------|------|:----:|
| `scripts/archive/douyin_browser_final.py` | douyin_index_v9.py | ✅ 已归档 |
| `scripts/archive/competitor_keyword_v2_to_v7.py` | competitor_keyword_v8.py | ✅ 已归档 |
| `scripts/archive/competitor_keyword_debug2.py` | competitor_keyword_debug.py | ✅ 已归档 |
| `scripts/archive/send_wenhua_tracking_20260421.py` | send_wenhua_tracking.py | ✅ 已归档 |
| `scripts/archive/test_card_send.py` | send_feishu_card.py | ✅ 已归档 |
| `scripts/archive/batch_insert_feishu.py` | — | ✅ 已归档（一次性迁移） |
| `scripts/archive/batch_insert_policy.py` | — | ✅ 已归档（一次性迁移） |
| `scripts/archive/batch_insert_price.py` | — | ✅ 已归档（一次性迁移） |
| `scripts/archive/batch_insert_refund.py` | — | ✅ 已归档（一次性迁移） |
| `scripts/archive/insert_all_feishu.py` | — | ✅ 已归档（一次性迁移） |
| `scripts/archive/insert_feishu_records.py` | — | ✅ 已归档（一次性迁移） |
| `scripts/archive/insert_price_fixed.py` | — | ✅ 已归档（一次性迁移） |
| `scripts/archive/honcho_user_model.py` | — | ✅ 已归档（实验性） |
| `scripts/archive/ollama_vision.py` | — | ✅ 已归档（本地测试） |
| `scripts/archive/weekly_cleanup.py` | — | ✅ 已归档（手动执行） |

---

## 归档路径说明

废弃脚本统一移入 `scripts/archive/`，需回滚时直接移回 `scripts/` 根目录即可。

---

*本索引最后更新：2026-05-24*
