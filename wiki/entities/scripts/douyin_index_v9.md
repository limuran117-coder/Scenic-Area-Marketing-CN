# douyin_index_v9.py

> 抖音指数数据采集脚本 | v9（最新）

---

## 基本信息

| 项目 | 内容 |
|------|------|
| 文件 | `~/.openclaw/workspace/scripts/douyin_index_v9.py` |
| 用途 | 采集8大竞品景区的抖音指数数据（搜索指数/综合指数/关联词/人群画像） |
| 执行频率 | 每日10:30 cron |
| 输出 | `/tmp/crawl_data.json` |

---

## 数据指标

- **搜索指数**：潜在游客主动搜索热度
- **综合指数**：全网曝光综合热度
- **关联词TOP10**：用户搜索前的关联行为
- **人群画像**：年龄/性别/地域分布

---

## 景区覆盖

1. 建业电影小镇
2. 万岁山武侠城
3. 清明上河园
4. 只有河南戏剧幻城
5. 郑州方特欢乐世界
6. 郑州海昌海洋公园
7. 郑州银基动物王国
8. 只有红楼梦戏剧幻城

---

## 技术细节

- **技术栈**：Playwright + CDP 浏览器自动化
- **Cookie存储**：`/tmp/juLiang_cookies.json`（代理：127.0.0.1:7897）
- **数据订阅页**：https://creator.douyin.com/creator-micro/creator-count/my-subscript
- **注意事项**：页面下午更新，08:00采的是昨日数据

---

## 调用方式

```bash
python3 ~/.openclaw/workspace/scripts/douyin_index_v9.py
```

---

*最后更新：2026-04-26*
