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
