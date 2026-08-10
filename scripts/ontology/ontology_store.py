"""
Ontology Store — 电影小镇 Ontology Layer 的 SQLite 核心存储
对标 Palantir Ontology 架构

设计原则：
- 零配置（Python 内置 sqlite3）
- 双写策略（SQLite 主存储 + JSON Git 快照）
- 字段映射层（adapter ontology 字段 → db 字段）
- 审计日志（ingest/query/action）
- 关注点分离（adapter 只转换, store 只存储, query 只查询）
"""
from __future__ import annotations

import json
import os
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Iterator, Literal

# ============================================
# 路径常量（与 .profile/ontology/ 配套）
# ============================================
WORKSPACE_ROOT = Path(os.path.expanduser("~/.openclaw/workspace"))
ONTOLOGY_DIR = WORKSPACE_ROOT / ".profile" / "ontology"
DB_PATH = ONTOLOGY_DIR / "ontology_store.db"
SNAPSHOTS_DIR = ONTOLOGY_DIR / "snapshots"
LOGS_DIR = ONTOLOGY_DIR / "logs"
MIGRATIONS_DIR = ONTOLOGY_DIR / "migrations"

# 默认 confidence（与 BEST_PRACTICES.md §实践 3 对齐）
DEFAULT_CONFIDENCE: dict[str, float] = {
    "douyin": 0.9,
    "xiaohongshu": 0.5,
    "weibo": 0.7,
    "baidu": 0.6,
    "internal_csv": 0.95,
    "manual": 1.0,
}

# adapter ontology 字段 → db 列名 映射
# 对应 BEST_PRACTICES.md §实践 9：适配器 Schema 与存储 Schema 分离
FIELD_MAP: dict[str, dict[str, str]] = {
    "MetricSnapshot": {
        "scenicSpotId": "spot_id",
        "metricType": "metric_type",
        "dailyChange": "daily_change",
        "weeklyChange": "weekly_change",
        "collectedAt": "collected_at",
    },
    "ContentAsset": {
        "scenicSpotId": "spot_id",
        "platform": "source",  # adapter 用 platform，db 用 source
        "authorName": "author",
        "authorId": "author_id",
        "likeCount": "like_count",
        "commentCount": "comment_count",
        "shareCount": "share_count",
        "publishDate": "publish_date",
        "type": "content_type",  # adapter 'type' (note/video/...) → db 'content_type'
        "isViral": "is_viral",
        "derivedToMetricSnapshot": "derived_to_metric_snapshot",
    },
    "Event": {
        "scenicSpotId": "spot_id",
        "occurredAt": "occurred_at",
        "detectedAt": "detected_at",
        "expiresAt": "expires_at",
        "sourceUrl": "url",
        "relatedSpots": "related_spots",
    },
    "ScenicSpot": {
        "shortName": "short_name",
        "isCoreCompetitor": "is_core_competitor",
        "annualCapacity": "annual_capacity",
        "createdAt": "created_at",
        "updatedAt": "updated_at",
    },
    "DecisionRule": {
        "ruleId": "rule_id",
        "authorityTier": "authority_tier",
        "conflictRule": "conflict_rule",
        "lastTriggeredAt": "last_triggered_at",
        "triggerCount": "trigger_count",
    },
    "MarketingCampaign": {
        "scenicSpotId": "spot_id",
        "startDate": "start_date",
        "endDate": "end_date",
        "targetAudience": "target_audience",
        "expectedImpact": "expected_impact",
        "actualImpact": "actual_impact",
    },
    "Region": {},
    "TouristSegment": {
        "ageRange": "age_range",
        "genderSplit": "gender_split",
    },
}


# ============================================
# Dataclasses
# ============================================
@dataclass
class IngestResult:
    """Adapter 输出统一结构"""
    status: Literal["success", "partial", "failed"]
    records_added: int = 0
    records_updated: int = 0
    error_message: str = ""
    started_at: str = ""
    finished_at: str = ""

    def to_dict(self) -> dict:
        return {
            "status": self.status,
            "records_added": self.records_added,
            "records_updated": self.records_updated,
            "error_message": self.error_message,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


# ============================================
# Core Store
# ============================================
class OntologyStore:
    """
    电影小镇 Ontology SQLite Store

    使用示例:
        store = OntologyStore()
        store.initialize()  # 首次启动时建表
        result = store.ingest_objects("adapter-douyin", schema, objects)
    """

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._ensure_dirs()

    def _ensure_dirs(self) -> None:
        """确保所有必要目录存在"""
        for d in (ONTOLOGY_DIR, SNAPSHOTS_DIR, LOGS_DIR, MIGRATIONS_DIR):
            d.mkdir(parents=True, exist_ok=True)

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """SQLite 连接上下文（自动 commit/rollback/close）"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def initialize(self) -> None:
        """应用所有 migrations，建库 + 种子数据"""
        self._ensure_dirs()
        with self._connect() as conn:
            migration_files = sorted(MIGRATIONS_DIR.glob("*.sql"))
            cur = conn.cursor()
            for mf in migration_files:
                sql = mf.read_text(encoding="utf-8")
                cur.executescript(sql)
        return None

    # ============================================
    # 字段映射（adapter → db）
    # ============================================
    def _map_fields(self, schema: str, obj: dict) -> dict:
        """将 adapter ontology 字段（camelCase）映射为 db 列名（snake_case）"""
        mapping = FIELD_MAP.get(schema, {})
        out = {}
        for k, v in obj.items():
            db_key = mapping.get(k, k)
            out[db_key] = v

        # 特殊处理：ContentAsset 的 date → publish_date
        if schema == "ContentAsset" and "date" in out and "publish_date" not in out:
            out["publish_date"] = out["date"]

        # 特殊处理：metrics.notes_count → notes_count 列
        if schema == "ContentAsset" and "metrics" in out:
            metrics = out["metrics"]
            if isinstance(metrics, dict):
                if "notes_count" in metrics and not out.get("notes_count"):
                    out["notes_count"] = metrics["notes_count"]

        return out

    def _serialize_json_fields(self, row: dict) -> dict:
        """dict/list 字段序列化为 JSON 字符串（写入 db 前）"""
        json_fields = {"tags", "competitors", "raw_data", "metadata",
                       "metrics", "channels", "target_audience", "kpis",
                       "related_spots", "aliases", "characteristics",
                       "gender_split"}
        for f in json_fields:
            if f in row and row[f] is not None and not isinstance(row[f], str):
                row[f] = json.dumps(row[f], ensure_ascii=False)
        return row

    # ============================================
    # Ingest 入口
    # ============================================
    def ingest_objects(
        self,
        adapter_name: str,
        schema: str,
        objects: list[dict],
        source_file: str = "",
    ) -> IngestResult:
        """
        主入口：接收 adapter 输出的 objects，写入对应表
        """
        started_at = datetime.now().isoformat()
        result = IngestResult(status="success", started_at=started_at)

        if not objects:
            result.status = "partial"
            result.error_message = "empty objects list"
            self._log_ingest(adapter_name, result, source_file)
            return result

        table = self._schema_to_table(schema)
        if not table:
            result.status = "failed"
            result.error_message = f"unknown schema: {schema}"
            self._log_ingest(adapter_name, result, source_file)
            return result

        added = 0
        updated = 0
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                for obj in objects:
                    row = self._map_fields(schema, obj)
                    row = self._serialize_json_fields(row)
                    row = self._fill_defaults(row, schema)
                    if self._upsert(cur, table, row, schema):
                        added += 1
                    else:
                        updated += 1
            result.records_added = added
            result.records_updated = updated
            result.finished_at = datetime.now().isoformat()
            # M6: 同步图谱（FAIL-OPEN，绝不影响 SQLite 主流程）
            try:
                from ontology_graph_sync import sync_to_graph
                synced, err = sync_to_graph(schema, objects)
                if err:
                    result.error_message = f"{result.error_message or ''} {err}".strip()
            except Exception as _e:  # 任何导入/运行异常都忽略
                pass
        except Exception as e:
            result.status = "failed"
            result.error_message = str(e)[:500]
            result.finished_at = datetime.now().isoformat()
        finally:
            self._log_ingest(adapter_name, result, source_file)
        return result

    def _fill_defaults(self, row: dict, schema: str) -> dict:
        """补齐默认字段"""
        if schema == "MetricSnapshot":
            row.setdefault("confidence", DEFAULT_CONFIDENCE.get(row.get("source", ""), 0.5))
            row.setdefault("ingested_at", datetime.now().isoformat())
        elif schema == "ContentAsset":
            row.setdefault("ingested_at", datetime.now().isoformat())
        elif schema == "Event":
            row.setdefault("detected_at", datetime.now().isoformat())
            row.setdefault("ingested_at", datetime.now().isoformat())
        return row

    def _schema_to_table(self, schema: str) -> str | None:
        """schema → db 表名"""
        return {
            "ScenicSpot": "scenic_spots",
            "MetricSnapshot": "metric_snapshots",
            "ContentAsset": "content_assets",
            "Event": "events",
            "MarketingCampaign": "marketing_campaigns",
            "DecisionRule": "decision_rules",
            "TouristSegment": "tourist_segments",
            "Region": "regions",
        }.get(schema)

    def _upsert(
        self,
        cur: sqlite3.Cursor,
        table: str,
        row: dict,
        schema: str,
    ) -> bool:
        """
        插入或更新；返回 True=新插入, False=更新
        """
        if not row.get("id"):
            row["id"] = f"{table}_{uuid.uuid4().hex[:8]}"

        # 过滤掉 db 表不存在的列（adapter 可能有冗余字段如 schema/version/createdAt）
        cur.execute(f"PRAGMA table_info({table})")
        valid_cols = {r[1] for r in cur.fetchall()}
        row = {k: v for k, v in row.items() if k in valid_cols}

        cur.execute(f"SELECT id FROM {table} WHERE id = ?", (row["id"],))
        exists = cur.fetchone() is not None

        if exists:
            cols = [k for k in row.keys() if k != "id"]
            set_clause = ", ".join(f"{c} = ?" for c in cols)
            values = [row[c] for c in cols] + [row["id"]]
            cur.execute(
                f"UPDATE {table} SET {set_clause} WHERE id = ?",
                values,
            )
            return False

        cols = list(row.keys())
        placeholders = ", ".join("?" for _ in cols)
        values = [row[c] for c in cols]
        cur.execute(
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({placeholders})",
            values,
        )
        return True

    def _log_ingest(
        self,
        adapter_name: str,
        result: IngestResult,
        source_file: str,
    ) -> None:
        """写入 ingest_log + 详细 log 文件"""
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.execute(
                    """INSERT INTO ingest_log
                       (adapter_name, status, source_file, records_added,
                        records_updated, error_message, started_at, finished_at)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (
                        adapter_name,
                        result.status,
                        source_file,
                        result.records_added,
                        result.records_updated,
                        result.error_message,
                        result.started_at,
                        result.finished_at,
                    ),
                )
        except Exception as e:
            print(f"[OntologyStore] failed to log ingest: {e}", flush=True)

        log_file = LOGS_DIR / f"{datetime.now().strftime('%Y-%m-%d')}-ingest.log"
        try:
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(
                    f"[{datetime.now().isoformat()}] {adapter_name} "
                    f"status={result.status} added={result.records_added} "
                    f"updated={result.records_updated} err={result.error_message}\n"
                )
        except Exception as e:
            print(f"[OntologyStore] failed to write log file: {e}", flush=True)

    # ============================================
    # JSON Snapshot（Git 追溯用）
    # ============================================
    def write_json_snapshot(
        self,
        schema: str,
        objects: list[dict],
        date: str | None = None,
    ) -> Path:
        """写 JSON 快照到 snapshots/ 目录（adapter 双写模式）"""
        date = date or datetime.now().strftime("%Y-%m-%d")
        snapshot = {
            "objectType": schema,
            "date": date,
            "generatedAt": datetime.now().isoformat(),
            "ontologyVersion": "1.1.4",
            "objects": objects,
        }
        source = objects[0].get("source", "unknown") if objects else "unknown"
        fname = f"{schema.lower()}_{source}_{date}.json"
        path = SNAPSHOTS_DIR / fname
        path.write_text(
            json.dumps(snapshot, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return path

    # ============================================
    # 读 API（简单查询用；复杂查询用 ontology_query.py）
    # ============================================
    def get(self, table: str, id: str) -> dict | None:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT * FROM {table} WHERE id = ?", (id,))
            row = cur.fetchone()
            return dict(row) if row else None

    def count(self, table: str, where: str = "1=1", params: tuple = ()) -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(f"SELECT COUNT(*) FROM {table} WHERE {where}", params)
            return cur.fetchone()[0]

    def list_recent_ingests(self, limit: int = 20) -> list[dict]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT * FROM ingest_log ORDER BY id DESC LIMIT ?",
                (limit,),
            )
            return [dict(r) for r in cur.fetchall()]

    def stats(self) -> dict:
        """快速统计各表行数"""
        tables = [
            "scenic_spots", "metric_snapshots", "content_assets",
            "events", "marketing_campaigns", "decision_rules",
            "tourist_segments", "regions",
            "spot_relations", "event_spot_links", "metric_content_links",
        ]
        return {t: self.count(t) for t in tables}


# ============================================
# CLI 入口
# ============================================
def main():
    import sys
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python ontology_store.py init        # 建表 + 种子数据")
        print("  python ontology_store.py stats       # 统计行数")
        print("  python ontology_store.py recent      # 最近 ingest 记录")
        return

    cmd = sys.argv[1]
    store = OntologyStore()
    if cmd == "init":
        store.initialize()
        print(f"✅ initialized: {DB_PATH}")
        print("   stats:", store.stats())
    elif cmd == "stats":
        try:
            print(store.stats())
        except Exception as e:
            print(f"❌ store not initialized: {e}")
            print("   run: python ontology_store.py init")
    elif cmd == "recent":
        for r in store.list_recent_ingests(20):
            print(f"  [{r['id']}] {r['adapter_name']} {r['status']} "
                  f"+{r['records_added']}/~{r['records_updated']} "
                  f"at {r['finished_at']}")
    else:
        print(f"unknown command: {cmd}")


if __name__ == "__main__":
    main()
