# MEMORY.md - Long-Term Memory

role: 景区营销中心总经理
update_time: 2026-04-22
core_mission: 年度客流153万（原132万调增）、营收1.12亿

---

# ⭐ 铁律（违反必纠）

**[feedback] 客流日报专属格式（04-20确认）**
> 格式密码：**912530**
> 5章：YTD总览→月度数据→近7日明细→穿越德化街→综合建议
> 表格限制≤5个/卡，超出拆分；先发私信→用户确认OK→再发群

**[feedback] 飞书卡片格式（04-19重大修正）**
> ⛔ 未经用户主动确认不得修改！
> `header.title.tag="plain_text"` + `header.title.content`；根级`elements[]`
> 脚本：`scripts/send_feishu_card.py <chat_id> <card_json>`

**[feedback] 数据必须读取实际值（04-14）**
禁止经验主义，先读原始数据再分析

**搜索铁律：** 只用「建业电影小镇」+7个竞品，禁止「建业华谊兄弟」

**[feedback] browser-use 全面禁止（04-20）**
所有浏览器操作走 Playwright 脚本；专属Chrome（CDP端口9222）仅手动

---

# [feedback] 最新确认（04-21止）

- 抖音指数cron：08:00→10:30（平台校准需10:00后）
- 飞书群ID：电影小镇群oc_2581.../数据推送群oc_f109...
- 小红书私信需open_id类型（非chat_id）
- 日报5列+涨跌符号+🔺异动标注
- 完整日报：表格+深度分析+竞品格局+行动建议
- 文旅热点扩展：覆盖全国不只盯竞品

---

# [project] 项目状态

## ✅ 已完成
- A+B+C多Agent架构、记忆系统整合
- 飞书卡片格式修复、案例库（5个爆款）
- 散客/渠道拆分模型、Skill-Router系统
- **环形水剧场+复古广场夏季运营方案**（04-21）
- 周度客流报告cron（周一09:00）

## ⏳ 进行中
- 抖音关键词深度数据（CDP不稳定）
- 小红书Cookie（账号封禁至04-23）
- 竞品关键词轮换（21景区：万岁山/清明上河园/只有河南✅，郑州方特🔜）
- Wiki架构重组

---

# [reference] 权威数据

| 数据 | 来源 |
|------|------|
| 历年客流 | 桌面2023-2025年门票销售及客流统计数据表.xlsx |
| 2026每日 | ~/Desktop/2026游客量统计.csv |
| 抖音Cookie | /tmp/juLiang_cookies.json（备用CDP：18800） |
| 小红书Cookie | /tmp/xiaohongshu_cookies.json（账号封禁中，04-23解封） |
| 飞书群 | 电影小镇群oc_2581.../数据推送群oc_f109... |

详细SOP索引 → wiki/SOP/
定时任务索引 → memory/topics/daily-tasks.md

---

# Promoted（2026-04-22）

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:5:5 -->
- **任务：** 整理本周优秀营销案例入库 [score=0.806]