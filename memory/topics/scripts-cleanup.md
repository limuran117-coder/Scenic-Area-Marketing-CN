# 脚本清理记录

## 清理日期
2026-04-11

## 清理内容
移至 .trash/ 目录（可恢复）：

### 旧版本脚本
- douyin_browser_v2.py ~ v8.py (7个)
- douyin_debug.py, douyin_debug2.py
- douyin_screenshot.py
- douyin_js_extract.py
- douyin_connect_v2.py
- xiaohongshu_login.py, xiaohongshu_test.py

## 保留脚本
| 脚本 | 用途 |
|------|------|
| douyin_browser_final.py | 抖音浏览器采集 |
| douyin_index.py | 抖音指数查询 |
| xiaohongshu_crawl.py | 小红书采集 |
| query_passenger.py | 客流查询 |
| validate_data.py | 数据验证 |
| confirm_action.py | 操作确认 |

## 恢复方法
```bash
mv scripts/.trash/<filename> scripts/
```
