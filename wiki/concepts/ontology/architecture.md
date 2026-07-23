# Ontology 架构（D-053 双 db 路径知识沉淀）

> ⚠️ **关键 SSOT 陷阱** —— 7/22 22:33 ontology_daily_work 失败 + 7/23 凌晨 8:25 修复实证
> Last update: 2026-07-23 W29 | Owner: 李涯

## 一、为什么本文件存在

7/22 晚 ontology_daily_work 跑了 7 分多钟，**最后挂在 FK constraint failed**，但已经在 wiki log 写好了完整诊断。**真实根因**是双 db 路径混淆 —— 之前所有"在 ontology.db 上验证通过"的判断都是错觉。本文件把这次事故的根因、修复方案、防错规则沉淀下来，避免反复踩坑。

## 二、双 db 路径真相

| 路径 | 大小 | 用途 | 谁写入 |
|------|------|------|---------|
| `scripts/ontology/ontology.db` | 192 KB | **手动查询**、adapter 配套回填历史 | 人工 seed_basic.py / backfill_historical.py |
| `.profile/ontology/ontology_store.db` | 253 KB | **生产 db**，所有 adapter 实际写入目标 | ontology_store.py `OntologyStore()` |

### 验证命令（写代码前必跑）

```python
python3 -c "from ontology.ontology_store import DB_PATH; print(DB_PATH)"
# 输出必须是: /Users/tianjinzhan/.openclaw/workspace/.profile/ontology/ontology_store.db
```

⚠️ **DB_PATH 在 ontology_store.py 第 29 行**：
```python
DB_PATH = ONTOLOGY_DIR / "ontology_store.db"
ONTOLOGY_DIR = WORKSPACE_ROOT / ".profile" / "ontology"
```

⚠️ **ontology_constants.py 不在 ontology/ 子目录**！它在 `scripts/ontology_constants.py`（scripts/ 根目录）。adapter 直接 `from ontology_constants import ...`。

## 三、典型错误模式 + 防御

### ❌ 错误：在 scripts/ontology/ontology.db 上验证 FK 通过就以为全 OK

```bash
# 错的做法
sqlite3 scripts/ontology/ontology.db "SELECT id FROM scenic_spots WHERE id='only_dream'"
# → 看起来有（手动 seed 的），但生产 db 缺这个 ID，adapter 写时必挂
```

### ✅ 正确：在生产 db 上验证

```bash
sqlite3 .profile/ontology/ontology_store.db "SELECT id FROM scenic_spots WHERE id='only_dream'"
# → 这才是 OntologyStore 实际看到的表
```

### 操作前 3 步必做

1. **`cp .profile/ontology/ontology_store.db /tmp/ontology_store_backup_<日期>.db`**（强制）
2. **`DB_PATH` 确认**：`python3 -c "from ontology.ontology_store import DB_PATH; print(DB_PATH)"`
3. **`PRAGMA foreign_keys`**：用 `OntologyStore()` 走 API；不要直接 sqlite3 操作（FK 设置会丢）

## 四、D-053 修复实证（7/22 22:33 → 7/23 08:25）

### 现象
- ingestion pipeline dry-run + 写 JSON ✅
- 但最后一行 `[⚠️] SQLite 写入失败: FOREIGN KEY constraint failed`
- 实际根因：adapter 输出 8 个 spot_id（含 `only_dream`），生产 db scenic_spots 只有 7 个景区

### 调查路径
1. **看 adapter 输出** → `metric_snapshots_20260722.json` 16 条记录，8 spot_id
2. **核查 `.profile/ontology/ontology_store.db scenic_spots`** → 缺 `only_dream`
3. **核查 `scripts/ontology/ontology.db scenic_spots`** → 看起来有（误导！实际错误归类成"只有河南"）
4. **修生产 db**：INSERT `only_dream`（江苏盐城，国家级，cultural_town），与 `only_henan` 明确分离
5. **回滚手动 db**：从 backup 恢复原始状态（避免连锁污染）
6. **重跑 adapter → 16 条全写入** ✅

### 备份 vs 修复结果

```bash
/tmp/ontology_backup_20260723.db         # scripts/ontology/ontology.db（手动 db）
/tmp/ontology_store_backup_20260723.db  # .profile/ontology/ontology_store.db（生产 db）
```

## 五、ontology_daily_work 强制收尾规则（7/23 加固）

**日志写入 wiki 后立即结束**，不允许扫尾 verification：

| ❌ 不要 | ✅ 要做 |
|--------|--------|
| 跑 sqlite3 查询验证 | dry-run + 写 JSON 即视为完成 |
| 做 grep cross-check | 写入 daily-work-YYYYMMDD.json 即停 |
| 重跑 adapter 验证 | 输出四段 ≤200 字洞察即停 |
| 写"复盘"长报告 | 详情写入 wiki 即可 |
| 假设 ontology_constants.py 在 ontology/ 子目录 | 先 `ls` 确认 |

## 六、相关文件清单

| 文件 | 路径 | 备注 |
|------|------|------|
| OntologyStore 代码 | `scripts/ontology/ontology_store.py` | DB_PATH 在第 29 行 |
| adapter-douyin | `scripts/adapter-douyin.py` | write_to_sqlite() 走 OntologyStore() |
| ingest_pipeline.sh | `scripts/ingest_pipeline.sh` | 双 cd scripts/ 路径坑已修复 |
| ontology_constants | `scripts/ontology_constants.py` | 在 scripts/ 根目录，不在 ontology/ 子目录 |
| 日志目录 | `wiki/技术配置/Ontology架构设计/data/logs/` | daily-work-YYYYMMDD.json |
| MEMORY 铁律 | `MEMORY.md` | 7/23 双 db 路径铁律 + 强制收尾规则 |

## 七、关联记录

- `data/logs/daily-work-20260722.json`（D-052 触发，问题误判）
- `data/logs/daily-work-20260723.json`（D-053 修复，根因定位）
- `memory/topics/ontology-progress.md`（Week 1-3 进度）
- `MEMORY.md`（铁律区第 26-32 行）
