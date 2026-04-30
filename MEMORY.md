# MEMORY.md - Long-Term Memory

role: 景区营销中心总经理
update_time: 2026-04-29
core_mission: 年度客流153万、营收1.2亿


**[feedback] 周度客流+W17深度分析最佳实践（04-27确认）**
> 周度报告 + 《穿越德化街》专项分析联发，成为W17报告标配
> 发送顺序：周度客流3张卡片 → 穿越德化街深度分析1张卡片
> 穿越德化街分析必须包含：核心指标/每日明细表/深度分析（场次切换/上座率分化/客流贡献/建议）
> CSV的BOM导致send_feishu_card.py报错，用rb模式strip BOM解决

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

**[feedback] 小红书灵犀后台操作规范（04-23补录自wiki SOP）**
> Wiki：wiki/技术配置/小红书灵犀后台操作流程.md
> 关键规则：
> 1. 用JS激活输入框（不能用普通click，会报not visible）
> 2. 用 `page.keyboard.type("关键词", delay=100)` 模拟真人慢速输入
> 3. **按Enter选精确匹配**（不要点击下拉词，会带后缀）
> 4. 搜索只输入主关键词，不加后缀（如只搜"万岁山"不搜"万岁山门票"）
> 5. 有两个Tab：搜索/内容，都要抓
> 6. 每个操作间隔2-3秒

**[feedback] 抖音关键词操作规范（04-23补录自wiki SOP）**
> Wiki：wiki/技术配置/抖音关键词操作流程.md
> 关键规则：
> 1. 搜索框输入关键词 → Enter或点击搜索按钮
> 2. 等3-5秒页面加载
> 3. 三类数据都要抓：关联词TOP10 + 人群画像4维度 + 关键词综合指数
> 4. 页面下午更新，08:00采的是昨日数据
> 5. 综合指数由高到低排序，环比>±20%用🔺标注

**[feedback] 竞品关键词深度分析执行规范（06-04-23确认）**
> 错误：绕过了 SOP 里的 `cdp_keyword_deep.py` 脚本和正确步骤，瞎试、数据猜的、流程全错
> 正确执行：
> 1. 打开小红书灵犀 → 在搜索框输入关键词 → 点击搜索 → 等数据加载 → 抓取（若触发品牌词拦截换核心词）
> 2. 打开抖音Tab3 → 输入关键词 → 搜索 → 等加载 → 下滑 → 点关联分析 → 等加载 → 点人群分析 → 等加载 → 抓取
> 3. 打开小红书搜索结果页 → 输入关键词 → 搜索 → 抓取爆款笔记
> 4. 打开百度 → 输入关键词 → 搜索 → 抓取百科信息
> **必须用 `cdp_keyword_deep.py` 脚本采集抖音数据，不得自行瞎试**
> **每步操作间隔5秒以上，页面完全加载后再抓取**
> **数据真实准确，禁止猜测，数据缺失标注"—"不得留空**

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
- 竞品关键词轮换（21景区：万岁山/清明上河园/只有河南✅，郑州方特✅，银基✅，清明上河园爆款拆解✅）
- Wiki架构重组（04-21确认，04-28验收完成✅）
- SOP体系完善（14个cron中8个有SOP，04-24完成13个cron全面更新）
- **图3-LLM知识层架构**（待绘制）
- **Wiki归档缺失补录**：老君山/重渡沟/龙门石窟/郑州海昌海洋公园（待站长确认方案）

---

# [reference] 权威数据

| 数据 | 来源 |
|------|------|
| 历年客流 | 桌面2023-2025年门票销售及客流统计数据表.xlsx |
| 2026每日 | ~/Desktop/2026游客量统计.csv |
| 抖音Cookie | /tmp/juLiang_cookies.json（备用CDP：18800） |
| 小红书Cookie | /tmp/xiaohongshu_cookies.json（04-23解封已验证） |
| 微博Cookie | 专属浏览器Tab6已登录（weibo.com/）04-28新增 |
| 飞书群 | 电影小镇群oc_2581.../数据推送群oc_f109... |

详细SOP索引 → wiki/SOP/
定时任务索引 → memory/topics/daily-tasks.md

---

# Promoted（2026-04-22）

<!-- openclaw-memory-promotion:memory:memory/2026-04-16.md:5:5 -->
- **任务：** 整理本周优秀营销案例入库 [score=0.806]
---

# [feedback] announce模式导致群里收到过程性消息（2026-04-26修复）

**问题现象：** cron announce模式把agent完整文字输出推到群里，包含"Now I have enough context"等思考过程，不是飞书卡片

**原因：** announce是额外兜底投递，即使agent正确走send_card()，announce仍会再推一遍完整输出

**修复：** 直接编辑cron/jobs.json，把6个cron的announce改为none
- 文旅活动热点追踪/小红书日报/行业热点采集/竞品关键词深度分析/竞品爆款拆解/每日复盘整合
- SOP本身没错，announce是多余的路

**预防：** 新建cron任务时，delivery.mode一律设none，不走announce

---

# [feedback] 飞书卡片换行修复（04-26确认）
> 卡片markdown内容中\n未正确解析为换行，需在后续卡片中用`<br/>`替代`\n`
> 已在文旅热点追踪日报中触发该问题

---

# [insight] 五一前关键洞察（04-25-26综合）

**5·19中国旅游日（广州主会场，洛阳入选5城倒计时）**
> 5城倒计时=开封/郑州/洛阳相关景区受益，电影小镇需提前备战
> 惠民补贴超10亿元/南航51.9万套福利机票/179趟旅游专列
> 五一建议提前预备应急预案（大客流应对）

**竞品动态：**
- 银基动物王国：听劝标题（避坑攻略7.7万赞/12.7万藏）+ 稀缺体验（酋长表演/烟花秀/飞鹰）+ 优速通痛点营销 + 性价比对比
- 只有红楼梦：情绪悬念文案（「你睡了吗」11.3万赞）+ 决策辅助（「三大剧场选哪个」1.2万赞）+ 百度负面风险（「不建议去只有红楼梦」）

**落地建议汇总：** 借鉴听劝标题/稀缺体验公式/优速通痛点营销/性价比对比/决策辅助内容/情绪悬念文案/双城联票策略

**[feedback] 飞书卡片`<br/>`换行（04-26确认）**
> markdown内容中\n未正确解析为换行，需用`<br/>`替代

**[project] 做图规范SOP（04-28建立）**
> wiki/做图规范.md：字号梯度/颜色规范/区块尺寸/检查清单/工具链
> 五一期间低压力窗口期适合完成图3-LLM知识层架构

**[reference] 微博已登录（04-28）**
> 专属浏览器Tab6：weibo.com（热搜，文旅舆情+竞品动态）

---

## 📅 本周执行摘要（2026-04-20 ~ 2026-04-28）

**重大进展：** SOP体系✅/announce修复✅/飞书卡片换行修复✅/系统架构图2张✅/微博Tab6✅/五一排期录入wiki✅

**竞品关键词轮换：** 万岁山/清明上河园/只有河南/郑州方特/银基动物王国 5个已完成✅

**技术债务：** 抖音关键词CDP不稳定（长期）| Wiki归档缺失4个（待站长确认）| 图3待绘制

**五一双节点：** 5·19旅游日（洛阳入选5城）+ 五一假期，竞品联合动作密集，电影小镇需备应急预案

## Promoted From Short-Term Memory (2026-04-28)

<!-- openclaw-memory-promotion:memory:memory/2026-04-20.md:9:12 -->
- **数据**（2026-04-20）: | 景区 | 搜索指数 | 搜索日环比 | 综合指数 | 综合日环比 | |------|---------|---------|---------|---------| | 清明上河园 | 230,452 | 📈 29.98% | 78,888 | 📈 29.85% | [score=0.879 recalls=0 avg=0.620 source=memory/2026-04-20.md:9-12]
<!-- openclaw-memory-promotion:memory:memory/2026-04-20.md:13:16 -->
- | 万岁山武侠城 | 54,510 | 📉 -2.63% | 24,610 | 📉 -7.77% | | 郑州银基动物王国 | 30,929 | 📈 2.31% | 9,514 | 📈 2.51% | | 郑州方特欢乐世界 | 11,033 | 📈 32.45% | 3,558 | 📈 34.82% | | **建业电影小镇** 🔺 | 6,477 | 📈 12.78% | 2,816 | 📈 12.01% | [score=0.879 recalls=0 avg=0.620 source=memory/2026-04-20.md:13-16]
<!-- openclaw-memory-promotion:memory:memory/2026-04-20.md:17:19 -->
- | 郑州海昌海洋公园 | 5,136 | 📈 11.12% | 1,851 | 📈 9.66% | | 只有河南戏剧幻城 | 3,617 | 📈 15.04% | 1,598 | 📉 -9.51% | | 只有红楼梦戏剧幻城 | 2,766 | 📈 9.76% | 1,054 | 📉 -2.59% | [score=0.879 recalls=0 avg=0.620 source=memory/2026-04-20.md:17-19]
<!-- openclaw-memory-promotion:memory:memory/2026-04-20.md:21:21 -->
- **建业电影小镇亮点**: 搜索+12.78%，综合+12.01%，双指标保持正增长，增速跑赢银基 [score=0.879 recalls=0 avg=0.620 source=memory/2026-04-20.md:21-21]

---

**[fix] 案例库更新cron错误（06-04-30修复）**
> 根因：SOP脚本用了 `cat > /tmp/xxx.py << 'PYEOF'` heredoc，触发exec安全拦截
> 修复：编辑cron/jobs.json，移除SOP中的heredoc，改用直接python执行

**[fix] 每日复盘整合cron错误（06-04-30修复）**
> 根因：edit工具找不到SOP文件中精确匹配的oldText
> 修复：编辑cron/jobs.json，简化cron message指令，禁止edit工具修改wiki

**[fix] Swap压力告警（06-04-30记录）**
> Swap使用率89.7%（4590M/5120M），主因Ollama 26GB模型blob
> 建议：考虑限制Ollama模型按需加载，非长期驻留

---

# 🌟 GitHub高星项目研究（06-04-30）

**[CowAgent] 43.9k⭐** — 飞书+Skills+MCP多Agent
- 架构：bridge/channel层支持飞书/钉钉/企微/微信/QQ等10+接入
- Skills系统：SKILL.md格式，metadata.cow.always/requires.bins/requires.env
- Skill Hub：skills.cowagent.ai 社区市场，支持clawhub安装
- MCP集成：完整MCP工具注册体系
- 记忆系统：长期记忆+知识库双轨，支持Ollama/DeepSeek/Claude/Gemini多模型
- 与当前系统对比：Skills格式高度相似（SKILL.md+description+metadata），MCP接入方式可比拟

**[EvoMap/evolver] 7.1k⭐** — GEP自进化引擎
- Genes/Capsules/Events三层进化机制
- 支持A2A（Agent to Agent）协议
- MCP工具注册
- 审计日志：可追踪每个skill的创建/演化过程
- 与autonomy-kit对比：进化逻辑更系统化，有审计链条

**[lobehub/lobehub] 75.9k⭐** — 多Agent协作平台
- Agent团队设计：多个Agent协同工作，有角色分工
- 与当前A+B+C架构可对照参考
- lobe-chat支持多模型切换（OpenAI/Claude/Gemini/DeepSeek）

**[neural-memory] 发现本地已有安装** ⚠️
- 内核通过spreading activation做记忆关联（不是向量检索）
- 20种突触类型：BEFORE/AFTER/CAUSED_BY/LEADS_TO/IS_A/HAS_PROPERTY等
- Hebbian学习+记忆衰减+矛盾检测
- 可作为MEMORY.md的增强层而非替代
