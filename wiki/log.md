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
