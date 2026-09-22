# Graphiti 运维说明（2026-09-22 更新）

## ⚠️ 2026-09-22 复发：FalkorDB 容器停摆（本次 cron run 内修复）

### 症状
- cron `cfb095fc` 09:14 触发时 `sync_ontology.py` 直接崩：`redis.exceptions.ConnectionError: Error 61 connecting to localhost:6379. Connection refused`
- 根因：容器 `graphiti-falkordb` 状态 `Exited (255) 2 days ago`（Docker Desktop 无开机自启 → 宿主机重启后容器不再拉起）
- 数据无损：volume `graphiti-data` 挂载点在 `/var/lib/falkordb/data`，检查后 171 节点 / 452 边 / 157 Episodic 全在

### 修复（本次已执行）
```bash
docker start graphiti-falkordb   # 4 秒后 6379 恢复 LISTEN
```

### 关键认知：数据在图 `movie-town`，不是 `graphiti`
- `graphiti_local.py:154` 写的是 `database="graphiti"`，但 graphiti_core 会按 **group_id 克隆 driver**（`falkordb_driver.py:331 clone()`），而三个脚本的 `GROUP_ID = "movie-town"`
- 所以真实数据落在 FalkorDB graph **`movie-town`**；graph `graphiti` 是空的历史遗留（`GRAPH.LIST` 里两个都在，查 `graphiti` 恒返 0 节点，别被误导）
- 核对图规模：`docker exec graphiti-falkordb redis-cli GRAPH.QUERY movie-town "MATCH (n) RETURN count(n)"`

### 2026-09-22 同步结果
- sync_ontology：18 条 episode（13 景区 + 10 关系，4 批）
- sync_flow --weeks 2：2 条周洞察（W36: 12226 人 / 日均 1747；W37: 22275 人 / 日均 3182，数据源 `~/Downloads/2026游客量统计 (21).csv`，304 天有效数据）
- 检索「行业对标对象」✅ 命中竞品关系

### 仍待站长处理（isolated run 改不了 cron payload）
- cron payload 未调用 `start_graphiti.sh`；建议要么让 Docker Desktop 开机自启，要么在 payload 首行加 `docker start graphiti-falkordb`
- 历史脏实体仍在：「只有红楼梦戏剧幻城」应为「只有河南·戏剧幻城」；「郑州电影小镇以建业电影小镇为行业对标对象」自指错误

---

# Graphiti 运维说明（2026-09-08 更新）

## ✅ 2026-09-08 修复：venv 移至持久位置（.venv）

### 问题（第二次复发）
- `/tmp/graphiti-venv` 又被 /tmp 清理删除（首次 8/24，二次 9/8）；`/tmp/ds_key.txt` 也不存在
- **同步任务 9/8 06:30 执行时环境全挂**（venv 无、key 无、Docker daemon 未启动）

### 修复动作（9/8 cron run 内完成）
1. **venv 建到持久位置**：`/opt/homebrew/bin/python3.12 -m venv ~/.openclaw/workspace/scripts/graphiti_local/.venv`
   - 依赖：清华镜像装 `graphiti-core==0.29.3` + `httpx` + `falkordb==1.7.1`（0.29.3 不自带 httpx/falkordb，必须手动补）
2. **符号链接兼容旧路径**：`ln -sfn ~/.openclaw/workspace/scripts/graphiti_local/.venv /tmp/graphiti-venv`
   - cron payload 里的 `/tmp/graphiti-venv/bin/python` 继续可用；即使 /tmp 再被清，重建链接即可（venv 本体已持久）
3. **Docker/FalkorDB 未随开机自启**：`open -a Docker` 后 `docker start graphiti-falkordb`（数据在 volume `graphiti-data`，无损）
4. DEEPSEEK_API_KEY 走环境变量注入（✅ 9/8 实测可用），不再依赖 key 文件

### 2026-09-08 同步结果（本次）
- sync_ontology：18 条 episode（13 景区 + 10 关系，4 批）；sync_flow --weeks 2：2 条周洞察（W34: 48372人 / W35: 30999人，数据源 Downloads 2026游客量统计 (19).csv）
- 检索「行业对标对象」✅ 返回竞品清单（清明上河园/大唐不夜城等，含已知脏实体）

### 待站长处理
- ⏳ cron job `cfb095fc` payload 仍写 `export DEEPSEEK_API_KEY=$(cat /tmp/ds_key.txt)`（已失效但无害，key 走环境变量）——isolated run 无法自改 payload，需主 session 用 `openclaw cron edit` 清理；建议同时把 venv 路径改为 `.venv` 持久路径（当前靠符号链接兜底）
- Docker Desktop 未配置开机自启 → cron 若在重启后触发需先拉起 Docker（start_graphiti.sh 已覆盖此逻辑，可考虑让 cron 先调它）

---

# Graphiti 运维说明（2026-08-25 更新）

## ⚠️ 2026-08-25 关键修复记录

### 问题 1：/tmp/graphiti-venv 被 /tmp 清理破坏（8/24 00:00）
- **症状**：`ModuleNotFoundError: No module named 'graphiti_core'`；venv 只剩 bin/ 目录，site-packages 里 graphiti_core 只剩空目录（0 个 .py 文件、无 __init__.py、RECORD 丢失）
- **根因**：macOS /tmp 定期清理（8/24 00:00）删掉了 venv 内部文件；`pyvenv.cfg` 也丢了，venv python 退化到系统 site-packages
- **修复**：`rm -rf /tmp/graphiti-venv` 后用 `/opt/homebrew/bin/python3.12 -m venv` 重建，再装依赖：
  ```bash
  /tmp/graphiti-venv/bin/python -m pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple "graphiti-core==0.29.3" "httpx" "falkordb==1.7.1"
  ```
  - ⚠️ 注意：清华镜像快（PyPI 直连会卡死），装 graphiti-core 后必须**手动补装 httpx 和 falkordb**（0.29.3 的依赖里没有它们，只有 dev extra 里有）

### 问题 2：/tmp/ds_key.txt 不存在
- **症状**：`cat: /tmp/ds_key.txt: No such file or directory`
- **根因**：key 文件也被 /tmp 清理删了
- **修复**：**DEEPSEEK_API_KEY 已在环境变量中**（agent 运行时自动注入），无需 key 文件。直接用环境变量：
  ```bash
  cd ~/.openclaw/workspace/scripts/graphiti_local && /tmp/graphiti-venv/bin/python sync_ontology.py
  ```

### 问题 3：cron payload 过时
- cron job `cfb095fc` 的 message 里还写着 `export DEEPSEEK_API_KEY=$(cat /tmp/ds_key.txt)` —— 该写法已失效
- **下次 cron 触发时**：忽略 key 文件步骤，直接用环境变量 + venv python 跑（本说明就是给下次 cron 的 agent 看的）
- ⚠️ isolated cron run 里 cron update 被限制（只能操作自身 job），需站长在主 session 手动更新 payload 或等下次自然触发时自愈

## 正确运行方式（2026-08-25 起）

```bash
# 1. Ontology 同步（13 景区 + 10 竞品关系 → 18 条 episode）
cd ~/.openclaw/workspace/scripts/graphiti_local && /tmp/graphiti-venv/bin/python sync_ontology.py

# 2. 客流周洞察（最近 2 周）
cd ~/.openclaw/workspace/scripts/graphiti_local && /tmp/graphiti-venv/bin/python sync_flow.py --weeks 2

# 3. 验证竞品关系
cd ~/.openclaw/workspace/scripts/graphiti_local && /tmp/graphiti-venv/bin/python graphiti_local.py search '行业对标对象'
```

## 2026-08-25 同步结果（本次）
- sync_ontology：18 条 episode 写入（13 景区 + 10 关系，4 批）
- sync_flow：2 条周洞察（W32: 32880人 / W33: 33642人）
- 图节点 63 → 68，边 174
- 检索「行业对标对象」✅ 返回竞品清单；「竞争对手」✅ 返回方特/万岁山/银基/清明上河园/只有河南
- 已知数据瑕疵（历史遗留，非本次引入）：实体名「只有红楼梦戏剧幻城」应为「只有河南·戏剧幻城」（LLM 抽取错误）；「郑州电影小镇以建业电影小镇为行业对标对象」自指错误

## 建议（待站长决策）
1. **venv 挪到持久位置**（如 `~/.openclaw/workspace/scripts/graphiti_local/.venv`），避免 /tmp 清理再次破坏 —— 但需更新 cron payload 中的路径
2. cron payload 移除 `/tmp/ds_key.txt` 引用
3. 图里「只有红楼梦戏剧幻城」脏实体可手动清理（FalkorDB graph.QUERY 删除或重建该节点）
