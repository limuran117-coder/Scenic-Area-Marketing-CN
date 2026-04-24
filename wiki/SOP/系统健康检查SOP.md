# 系统健康检查SOP

> 建立时间：2026-04-22
> 适用范围：每日监控 / 周日全面检查 / 故障排查

---

## 每日检查清单（快速，5分钟）

### 1. Cron任务状态

```bash
openclaw tasks 2>&1 | grep -E "error|warn|timeout" | head -20
```

关注：
- `lastRunStatus: error` 的任务
- `consecutiveErrors: >0` 的任务
- 超时任务（`timeout` in lastError）

### 2. Feishu卡片发送验证

检查最近3个任务的日志：
```bash
openclaw tasks --filter my-tasks 2>&1 | tail -10
```

**验证方法**：去飞书群看对应时间是否有卡片发出。

### 3. 专属浏览器状态

```python
browser(action="tabs", profile="openclaw", target="host")
```

确认5个Tab都在，不足5个则补充打开。

---

## 周日全面检查（30分钟）

### 4. Cron健康全表

列出所有任务：
```bash
openclaw cron list 2>&1
```

关注：
- `lastRunStatus: error` → 查明原因
- `lastDurationMs` 异常高（>900s）→ 性能问题
- `lastRunAtMs` 距离现在超过1.5个执行周期 → 漏运行

### 5. Session堆积检查

```bash
openclaw sessions list --active-minutes 60 2>&1 | wc -l
```

超过50个活跃session需关注，可能导致OOM。

### 6. Memory状态

```bash
openclaw status 2>&1 | grep Memory
```

`dirty: true` 意味着有未刷回磁盘的记忆块。

### 7. Gateway进程

```bash
openclaw gateway status 2>&1
```

确认：
- Gateway reachable
- pid 与上次一致
- 无 restart 记录

---

## 已知系统限制（不可改）

### 限制1：isolated session 硬超时 120秒

**现象**：karpathy-wiki LINT / karpathy-project-wiki LINT 任务，payload timeoutSeconds=3600 仍会在120秒后超时。

**原因**：karpathy-wiki skill 本身的多轮agent迭代对72个文件扫描超出120秒。

**当前缓解**：timeoutSeconds 设为3600，由skill内部超时控制进度。

**如果仍然超时**：考虑将 LINT 任务改为直接运行Python脚本（wiki_drift_check.py）而非调用skill。

### 限制2：专属Browser与站长Chrome互斥

专属Browser（18800端口）和站长日常Chrome无法同时以remote debugging模式运行。

**当前方案**：站长Chrome正常使用，专属Browser由Gateway管理，两套并行。

---

## 故障决策树

```
任务失败 → 看 lastError 内容
├─ "timeout" → 查 payload.timeoutSeconds 是否够用，或任务本身是否太重
├─ "no route" → 查 delivery.mode 是否为 announce+last，且飞书channel未配置
├─ "Message failed" → 查 Python 脚本 send_feishu_card.py 是否正常
└─ "python error" → 查对应脚本的输出日志
```

---

## 关键配置文件位置

| 用途 | 路径 |
|------|------|
| Cron任务定义 | `~/.openclaw/gateway/jobs.json` |
| Cron执行状态 | `~/.openclaw/gateway/jobs-state.json` |
| Session存储 | `~/.openclaw/agents/main/sessions/sessions.json` |
| 专属Browser数据 | `~/.openclaw/browser/openclaw/user-data` |
| 每日任务断点 | `/tmp/daily_task_state.json` |

---

## 本次修复记录（2026-04-22）

### 修复1：announce -> last 静默失败
- **问题**：16个cron任务配置了 `announce -> last`，飞书channel无路由，导致每次执行完都会留下 `lastRunStatus: error` 记录
- **修复**：全部改为 `delivery.mode: none`（这些任务内部用Python脚本发飞书卡片，不需要外层announce）
- **受影响任务**：抖音指数日报/文旅营销案例/文旅活动热点追踪/行业热点采集/竞品关键词深度分析/竞品爆款拆解/每日复盘整合/案例库更新/auto-memory-dream/Obsidian Wiki同步/五一提醒/周度技能探索/周度清理/周日系统升级

### 修复2：超时任务timeout升级
- **问题**：Wiki健康检查/代码库Wiki漂移检查 120秒硬超时
- **修复**：timeoutSeconds 1800 → 3600
- **注意**：可能是skill本身超时导致，持续观察

### 修复3：153万年度目标更新
- **问题**：年度客流目标从132万调增至153万（2026-04-22确认）
- **修复**：已更新 MEMORY.md / USER.md / Wiki客流页 / 基础档案 / SOP周报 / 穿越德化街 等8个文件
- **新完成度**：YTD 511,141 / 1,530,000 = 33.4%（时间进度37.5%，滞后4.1pp）

### 文档4：Browser SOP建立
- 新建 `wiki/SOP/专属浏览器维护SOP.md`
- 记录5个Tab位/启动命令/故障排查/登录维护

---

## 待执行任务（2026-04-22）

### 穿越德化街数据深度分析
- **来源**：《穿越德化街》数据分析-4.16v4(1).xlsx（桌面）
- **内容**：历年德化街客流/转化率/收入数据
- **关键背景**：
  - 2024-10-07前：正常运营
  - 2024-10-08至年底：扩建施工，无数据
  - 2024-12月：压力测试期（12/28-30有0.1元加购活动），数据不完整
  - **2025-01-01起：扩建完成，正式运营**
- **分析要求**：
  1. 更新 `wiki/电影小镇/演出节目/穿越德化街.md` 中的数据部分
  2. 重新计算转化率（观演人次/入园人次）
  3. 更新扩建后的新运营数据
  4. 修正数据解读（特别注明扩建期数据缺失）

---

## 附：抖音订阅页采集失败复盘（2026-04-24）

### 失败现象
抖音指数日报（订阅页Tab1）只抓到5个竞品，缺失万岁山/清明上河园/只有河南。

### 根因（三层）

| 层次 | 问题 | 为什么没发现 |
|------|------|-------------|
| **脚本层** | `douyin_index_v9.py` 没有滚动逻辑，订阅页懒加载，首屏外数据不渲染 | 开发时只测了首屏，没有模拟真实用户场景 |
| **SOP层** | SOP只写"等5秒刷新"，没写"滚动触发懒加载" | SOP基于成功路径总结，没有覆盖动态页面行为 |
| **验证层** | 采集后没有校验是否所有8个景区都有数据，直接假设成功 | 缺乏数据完整性校验意识 |

### 修复措施

1. **脚本修复**：`douyin_index_v9.py` 已加入 `scroll_to_load_all()` 函数，滚动至页面底部触发懒加载，刷新后重新滚动
2. **SOP更新**：订阅页操作步骤增加"滚动到页面底部"
3. **验证机制**：采集后校验8个景区是否全部有数据（`len(competitors) == 8`），缺失则重试或告警

### 预防检查清单（每次修改采集脚本后必做）

- [ ] 页面是懒加载吗？→ 是的话必须加滚动
- [ ] 采集后数据完整性校验了吗？（8个景区都抓到？）
- [ ] 单独跑了全流程验证了吗？（不是只看日志）
