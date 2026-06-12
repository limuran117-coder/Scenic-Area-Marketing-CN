# 系统演化日志（2026-06-12归档）

## 模型切换历史
- 6/6：DeepSeek余额不足 → 切换MiniMax M3
- 6/8：切换M3-only（删DeepSeek/M1/M2.1），openclaw.json -33%
- 6/12：全面切回 M2.7（当前状态）

## 重大故障记录
- 5/25-6/9：DeepSeek余额耗尽导致持续失败
- 6/9：M3 5h限额100%触顶，14:00任务全部失败
- 6/10-6/11：小红书explore页改版导致4连失败
- 6/12：auth store空条目+软链接缺失导致isolated session auth失败

## 根因教训
- lsof状态抖动误报7897代理断连（6/6-6/9）
- DDG插件死（web_search）连续4天爆款拆解降级（6/8-6/11）
- isolated session不继承shell env变量
- catalog.json apiKey是env变量名不是真实key

## SOP路径漂移（5/27重构后遗症）
4个cron prompt写SOP/xxx.md，实际路径wiki/SOP/xxx.md → 已修

## 修复方法
- auth问题：authProfile="minimax:default" + 软链接agents→根目录auth-profiles.json
- DDG：改web_search provider为minimax
- catalog.json：直接写入真实key
- cron tz：补Asia/Shanghai

---
*来源：MEMORY.md系统演化章节，完整时间线在memory/YYYY-MM-DD.md*