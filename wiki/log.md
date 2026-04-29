# Wiki Log

> 追加式操作记录 | `grep "^## \[" wiki/log.md | tail -20` 查看最近20条

---

## [2026-04-18] skill_install | 安装karpathy-guidelines
- 安装来源：multica-ai/andrej-karpathy-skills
- 安装路径：~/.openclaw/workspace/skills/karpathy-guidelines/SKILL.md
- 同步内容：4大原则 + 反模式速查表 + 本项目应用指南
- 状态：✅ 生效中

## [2026-04-18] skill_install | 安装karpathy-wiki + karpathy-project-wiki
- 安装来源：toolboxmd/karpathy-wiki
- 安装路径：~/.openclaw/workspace/skills/karpathy-wiki/ + karpathy-project-wiki/
- 包含：SKILL.md + hooks.json + references/operations.md + scripts/check-wiki-drift.sh
- 差异：karpathy-wiki=通用知识库，karpathy-project-wiki=代码库专属（git diff驱动）
- 状态：✅ 生效中

## [2026-04-18] system | karpathy三Skill自动运行机制建立
- 新增cron：每周日10:00 Wiki健康检查（LINT）→ 发飞书卡片
- 新增cron：每周日11:00 代码库Wiki漂移检查（LINT）→ 发飞书卡片
- 新增脚本：scripts/wiki_drift_check.py（karpathy-wiki LINT）
- 新增脚本：scripts/project_drift_check.py（karpathy-project-wiki LINT）
- cron IDs：Wiki健康检查(2e204ea4) / 代码库漂移(7d92440d)
- 首次LINT结果：33个孤儿页 + 28个未归档脚本
- 状态：✅ 自动运行已激活

## [2026-04-18] wiki_structure | 建立Wiki追加结构
- 新增目录：concepts/ / entities/ / queries/ / raw/
- 新增文件：wiki/log.md（追加式操作记录）
- 参考：toolboxmd/karpathy-wiki 架构
- 状态：✅ 完成

## [2026-04-19] 数据同步 | 电影小镇2026年客流数据Wiki同步
- 数据来源：~/Desktop/2026游客量统计.csv（唯一权威来源）
- 同步内容：电影小镇/历史数据/2026年/数据.md
- 数据截止：04-12
- 月度汇总：01月56,571(+29天) / 02月307,169(+28天) / 03月80,285(+31天) / 04月51,153(+12天)
- YTD：495,178人次/100天/完成度37%
- 状态：✅ 完成

## [2026-04-19] 故障复盘 | 飞书卡片发送故障
- 现象：卡片发送后表格渲染异常，内容不完整
- 根因：OpenClaw card参数与飞书API不兼容 + 分段方式错误
- 解决：改用Python直调API，修正markdown分段方式
- 新增：`wiki/SOP/飞书卡片故障复盘.md`
- 状态：✅ 已解决

## [2026-04-21] 数据同步 | 电影小镇2026年客流数据Wiki同步
- 数据来源：~/Desktop/2026游客量统计.csv（唯一权威来源）
- 同步内容：电影小镇/历史数据/2026年/数据.md
- 数据截止：04-19（后续日期均为0，待更新）
- YTD：502,571人次/111天/完成度38%
- 状态：✅ 无需更新（已同步）

## [2026-04-20] 数据同步 | 电影小镇2026年客流数据Wiki同步
- 数据来源：~/Desktop/2026游客量统计.csv（唯一权威来源）
- 同步内容：电影小镇/历史数据/2026年/数据.md
- 数据截止：04-12
- YTD：484,133人次/99天/完成度37%
- 状态：✅ 完成
## [2026-04-22] 数据同步 | 电影小镇2026年客流数据Wiki同步
- 数据来源：~/Desktop/2026游客量统计.csv（唯一权威来源）
- 同步内容：电影小镇/历史数据/2026年/数据.md
- 数据截止：04-19（CSV中04-20起均为0，待更新）
- YTD：511,141人次/107天/完成度38.7%
- 状态：✅ 无需更新（已同步至最新有效数据）

## [2026-04-22] 系统全面检查+修复
- 20个cron任务检查：3个timeout错误，16个announce->last路由失败
- 修复1：16个cron delivery.mode改为none（announce静默失败）
- 修复2：超时任务timeoutSeconds 1200→3600
- 修复3：153万年度目标全面同步（8个wiki文件）
- 新建SOP：wiki/SOP/系统健康检查SOP.md（每日/周日检查清单）
- 新建SOP：wiki/SOP/专属浏览器维护SOP.md（5个Tab位/启动命令）
- 新建SOP：wiki/SOP/每日任务总览.md（cron任务索引/断点续做）
- 新建技术配置：wiki/技术配置/脚本清单.md（5个脚本索引）
- 新建技术配置：wiki/技术配置/飞书配置.md（Bot配置/卡片规范）
- 新建竞品：wiki/竞品分析/关键词池状态.md（21景区关键词池）
- 状态：✅ 完成

## [2026-04-22] 穿越德化街深度分析
- 数据来源：《穿越德化街》数据分析-4.16v4(1).xlsx（桌面，唯一权威）
- 扩建分界线：2024-10-07起扩建，10/11月停演，2025-01-01正式运营
- 2025年质变：入园133.8万(-15%)/转化率35.2%(+17.2pp)/观演47.1万(+65.8%)/收入4266万(+35.9%)
- 客单价：套票101.59元/德化街39.54元/加购52.80元
- 六大洞察：扩建悖论/平日>大假/国庆入园崩-41%/⚠️2026Q1加购占比50.5%预警/8月vs10月差异/受众画像
- 更新的文件：wiki/电影小镇/演出节目/穿越德化街.md
- 状态：✅ 完成

## [2026-04-22] 抖音指数日报Bug修复
- 问题：脚本读取昨日缓存，平台每天只更新一次
- 修复：douyin_index_v9.py添加数据日期检测，非今日则page.reload()等待8秒
- 更新的文件：scripts/douyin_index_v9.py
- 状态：✅ 完成

## [2026-04-22] 只有河南暴涨溯源分析
- 爆款：@铁铁铁锤「只有河南你睡了吗」11.3万赞（情绪悬念文案）
- 规律：情绪类内容/小达人出圈（2.3万粉出11万赞爆款）
- 爆款类型：TOP1情绪悬念/TOP2攻略型/TOP3情绪共鸣
- GitHub同步：README.md更新（2026-04-22提交：ff71282）
- 状态：✅ 完成
## [2026-04-23] Obsidian Wiki客流同步

- **cron ID：** 7af8d42f-4441-4640-950f-96bfa1f79b80
- **执行时间：** 2026-04-23 05:00（GMT+8）
- **数据源：** 桌面CSV文件（飞书已同步）
- **同步范围：** 更新至2026-04-19
- **Wiki文件：** wiki/电影小镇/历史数据/2026年/数据.md
- **数据状态：** 4月20日后数据均为0（尚未录入）
- **状态：** ✅ 完成
## [2026-04-25] 周度技能探索 W17
- 探索技能：deep-research + agentic-workflow-automation
- deep-research：4阶段调研方法论（泛查→定向→验证→报告），适合竞品调研和政策研究
- agentic-workflow-automation：生成可复用自动化蓝图（n8n），可用于日报自动化
- 记录位置：wiki/技术配置/Skills探索笔记.md
- 状态：✅ 完成

## [2026-04-25] wiki_reorg | karpathy-wiki知识层重组启动
- **重组目标**：按 karpathy-wiki 标准建立纯知识抽象层（concepts/entities/sources/）
- **业务层不动**：电影小镇/竞品分析/全国景区案例库/行业知识/SOP/技术配置/ 原封不动
- **安全机制**：纯添加不修改不删除，raw/文件永不可变
### 新建文件
- `wiki/schema.md`：wiki编写规范（页面类型/命名/link约定/分层原则）
- `wiki/overview.md`：全域知识总览（三层体系+关键实体+核心概念+数据资产）
### 新建概念页（concepts/）
- `concepts/演艺景区.md`：产品即内容，口碑驱动，扩建悖论
- `concepts/内容爆款规律.md`：情绪悬念>攻略型>情绪共鸣，小达人出圈
- `concepts/季节性客流规律.md`：三峰值+德化街悖论
- `concepts/景区抖音运营.md`：搜索指数/综合指数/关键词策略
- `concepts/景区小红书运营.md`：灵犀后台三大模块
### 新建实体页（entities/）
- `entities/建业电影小镇.md`：年度153万/1.2亿，拳头《穿越德化街》
- `entities/万岁山武侠城.md`：50亿+播放，王婆说媒/麻将比赛
- `entities/只有河南.md`：11.3万赞情绪悬念爆款
- `entities/清明上河园.md`：搜索指数39.9万，同比+549%
- `entities/银基动物王国.md`：亲子乐园，Live图品牌定位
- `entities/郑州方特欢乐世界.md`：POV跳楼机1.1万赞
- `entities/大唐不夜城.md`：夜游标杆，情绪悬念+本地达人矩阵
- `entities/抖音平台.md`：搜索指数/综合指数/7个竞品关键词
- `entities/小红书平台.md`：灵犀后台/种草逻辑
### 下一步
- sources/ 归档页（将四月日报/报告摘要入sources/）
- 旧目录清理/合并（待定）
- 状态：**进行中**

## [2026-04-25] wiki_reorg_phase2 | 第二阶段完成：sources归档+新增概念/实体
### 新增概念页（concepts/）
- `concepts/景区营销漏斗.md`：五层漏斗（曝光→兴趣→搜索→决策→到院）
- `concepts/内容发布节奏.md`：每日节奏/节假日节奏/爆款时间窗口
- `concepts/ROI分析.md`：内容ROI/获客ROI/转化ROI，扩建案例
- `concepts/景区类型.md`：五大类型分类（演艺/主题乐园/文旅小镇/古镇/自然）
- `concepts/平台算法规则.md`：抖音流量池机制/小红书推荐权重
- `concepts/情绪营销.md`：情绪类型与传播力（悬念/焦虑/共鸣/反转/怀旧）
### 新增实体页（entities/）
- `entities/只有红楼梦戏剧幻城.md`：只有河南姐妹篇，红楼梦IP
### 新建sources归档（sources/）
- `sources/穿越德化街数据分析.md`：三年数据+扩建对比+六大洞察
- `sources/抖音指数追踪日报.md`：7个竞品+我方，搜索/综合指数
- `sources/竞品深度档案.md`：21个关键词池，7个核心竞品状态
- `sources/客流营收历年分析.md`：历年客流+2026目标+YTD完成度
### index.md更新
- 概念页：从5个增至11个
- 实体页：从9个增至10个
- sources归档：从0增至4个
### 状态：✅ 第二阶段完成

## [2026-04-25] wiki_reorg_phase3 | 第三阶段完成：queries归档+去重分析+INGEST记录
### 新增queries归档（queries/）
- `queries/2026-04-25-Wiki重组决策.md`：重组背景/决策/安全机制/执行结果
- `queries/知识层与业务层关系.md`：两层分离原则/依赖关系/实际例子
- `queries/抖音与小红书平台差异.md`：核心差异/内容策略/发布节奏/协同策略
- `queries/旧目录与知识层重叠分析.md`：重叠分析结论/不是冗余是分层
### 新增sources归档（sources/）
- `sources/2026-04-25Wiki重组.md`：karpathy-wiki重组全记录（INGEST记录）
### 去重分析结论
- 行业知识/景区类型/ vs concepts/景区类型.md：不是冗余，是业务层详细+知识层摘要
- 竞品分析/ vs sources/：不是冗余，是业务层数据+知识层说明
- entities/ vs 竞品分析/：不是冗余，是实体摘要+详细分析
- 结论：**无完全重复文件，无需删除**
### index.md更新
- queries归档：从0增至4个
- sources归档：从4增至5个
### 知识层最终规模
- concepts/: 11个 ✅
- entities/: 10个 ✅
- sources/: 5个 ✅
- queries/: 4个 ✅
### 状态：✅ 重组完成

## [2026-04-27] 每日客流数据同步
- **action**: INGEST
- **source**: 飞书Bitable「电影小镇-2026年数量统计」(124条记录)
- **output**: wiki/knowledge/2026年每日客流数据.md
- **data**: 2026年1-4月每日客流(截至4/19)
  - 1月: 46,466人次(26天)
  - 2月: 234,621人次(25天，含春节黄金周)
  - 3月: 124,331人次(31天)
  - 4月: 62,028人次(19天)
  - 合计: 467,446人次
- **说明**: 飞书多维表格为每日明细数据，与阶段性数据表(xlsx)口径可能存在差异
- **状态**: ✅ 完成

## [2026-04-26] Obsidian Wiki客流同步
- **action**: INGEST
- **source**: wiki/raw/建业电影小镇阶段性数据表.xlsx
- **output**: wiki/knowledge/建业电影小镇阶段性数据表.md
- **data**: 年度(2023-2025)+Q1(2026)+平日大假+2025激励+2026目标排期
- **card**: 已发送飞书群 oc_2581c03b79e4893cc3616b253d60f34e

## [2026-04-26] 核心运营脚本归档
- **action**: INGEST
- **scope**: scripts/ 目录 → wiki/entities/scripts/
- **索引文件**: wiki/entities/scripts/README.md（1902字节，22个脚本条目）
- **单页归档**: douyin_index_v9.md / send_feishu_card.md / query_passenger.md
- **原因**: 漂移检查报警46个脚本未归档，建立索引防失控
- **状态**: ✅ 完成
## [2026-04-28] 每日客流数据同步 | W17数据(04/20-04/26)同步至wiki：2026年/数据.md更新(截止04-26,YTD 525,533,完成度34.3%)；建业电影小镇实体文件同步更新

## [2026-04-30] 每日客流数据同步 | 无新增数据
- **action**: CHECK
- **scope**: ~/Desktop/2026游客量统计.csv
- **finding**: CSV截止04-26，最后修改04-27（无新增数据）
- **04-27~04-30**: 均为空记录（合计=0）
- **Wiki状态**: 上次04-28同步已是最新（YTD 525,533，完成度34.3%）
- **状态**: ✅ 无需操作
