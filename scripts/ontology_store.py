#!/opt/homebrew/bin/python3.12
"""
Ontology Store: SQLite 本地数据库

功能：
1. 建表（完整 Schema：6 张数据表 + 3 张元数据表 + 2 个视图）
2. 写入（ingest_spots, ingest_metric_snapshots, ingest_content_assets）
3. 查询（daily_ranking, trend, competitor_comparison, anomaly_detection）
4. 审计（ingest_log 记录每次 adapter 执行）

数据库路径: .profile/ontology/ontology_store.db
运行: python3 ontology_store.py [init|status|query|test]

设计原则:
  - 零外部依赖（仅 Python 3.12+ 标准库 sqlite3）
  - 所有 ID 使用语义化前缀（ss_, ms_, ca_, ev_, mc_）
  - JSON 字段存 TEXT，Python 侧序列化/反序列化
  - 索引覆盖所有常用查询路径
"""

import json
import os
import sys
import datetime
import sqlite3
from pathlib import Path

# ─── 常量 ────────────────────────────────────────

DB_DIR = Path.home() / ".profile" / "ontology"
DB_PATH = DB_DIR / "ontology_store.db"

SCHEMA_VERSION = "1.0.0"

# ─── Schema DDL ──────────────────────────────────

DDL_STATEMENTS = [
    # ========================
    # 1. 核心数据表
    # ========================

    # 1.1 景区实体
    """
    CREATE TABLE IF NOT EXISTS scenic_spots (
        id          TEXT PRIMARY KEY,
        name        TEXT NOT NULL,
        short_name  TEXT,
        category    TEXT,
        city        TEXT,
        province    TEXT,
        tier        TEXT DEFAULT 'secondary',
        annual_capacity REAL,
        is_core_competitor INTEGER DEFAULT 0,
        competitors TEXT,
        tags        TEXT,
        created_at  TEXT DEFAULT (datetime('now')),
        updated_at  TEXT DEFAULT (datetime('now'))
    )
    """,

    # 1.2 指标快照（核心写入表）
    """
    CREATE TABLE IF NOT EXISTS metric_snapshots (
        id             TEXT PRIMARY KEY,
        spot_id        TEXT NOT NULL REFERENCES scenic_spots(id),
        source         TEXT NOT NULL,
        date           TEXT NOT NULL,
        metric_type    TEXT NOT NULL,
        value          REAL NOT NULL,
        daily_change   REAL,
        weekly_change  REAL,
        confidence     REAL DEFAULT 0.5,
        raw_data       TEXT,
        metadata_json  TEXT,
        ingested_at    TEXT DEFAULT (datetime('now'))
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ms_spot_date ON metric_snapshots(spot_id, date)",
    "CREATE INDEX IF NOT EXISTS idx_ms_source_date ON metric_snapshots(source, date)",
    "CREATE INDEX IF NOT EXISTS idx_ms_metric_type ON metric_snapshots(metric_type)",

    # 1.3 内容资产
    """
    CREATE TABLE IF NOT EXISTS content_assets (
        id              TEXT PRIMARY KEY,
        source          TEXT NOT NULL,
        external_id     TEXT,
        spot_id         TEXT REFERENCES scenic_spots(id),
        title           TEXT,
        description     TEXT,
        url             TEXT,
        author          TEXT,
        like_count      INTEGER DEFAULT 0,
        comment_count   INTEGER DEFAULT 0,
        share_count     INTEGER DEFAULT 0,
        view_count      INTEGER DEFAULT 0,
        publish_date    TEXT,
        content_type    TEXT,
        sentiment       TEXT,
        is_viral        INTEGER DEFAULT 0,
        tags            TEXT,
        raw_data        TEXT,
        derived_from_metric_id TEXT,
        ingested_at     TEXT DEFAULT (datetime('now'))
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_ca_spot ON content_assets(spot_id)",
    "CREATE INDEX IF NOT EXISTS idx_ca_source ON content_assets(source)",
    "CREATE INDEX IF NOT EXISTS idx_ca_date ON content_assets(publish_date)",

    # 1.4 事件
    """
    CREATE TABLE IF NOT EXISTS events (
        id              TEXT PRIMARY KEY,
        type            TEXT NOT NULL,
        title           TEXT NOT NULL,
        description     TEXT,
        severity        TEXT DEFAULT 'low',
        date            TEXT NOT NULL,
        related_spots   TEXT,
        source_url      TEXT,
        raw_data        TEXT,
        ingested_at     TEXT DEFAULT (datetime('now'))
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_events_date ON events(date)",
    "CREATE INDEX IF NOT EXISTS idx_events_type ON events(type)",

    # 1.5 营销活动
    """
    CREATE TABLE IF NOT EXISTS marketing_campaigns (
        id              TEXT PRIMARY KEY,
        name            TEXT NOT NULL,
        spot_id         TEXT REFERENCES scenic_spots(id),
        start_date      TEXT,
        end_date        TEXT,
        budget          REAL,
        channels        TEXT,
        kpis            TEXT,
        status          TEXT DEFAULT 'planned',
        notes           TEXT,
        created_at      TEXT DEFAULT (datetime('now')),
        updated_at      TEXT DEFAULT (datetime('now'))
    )
    """,

    # 1.6 决策规则
    """
    CREATE TABLE IF NOT EXISTS decision_rules (
        id              TEXT PRIMARY KEY,
        rule_id         TEXT NOT NULL,
        name            TEXT NOT NULL,
        category        TEXT,
        condition       TEXT,
        action          TEXT,
        authority_tier  INTEGER,
        conflict_rule   TEXT,
        confidence      REAL DEFAULT 0.5,
        status          TEXT DEFAULT 'hypothesis',
        source          TEXT,
        last_triggered_at TEXT,
        trigger_count   INTEGER DEFAULT 0
    )
    """,

    # ========================
    # 2. 关系表
    # ========================

    """
    CREATE TABLE IF NOT EXISTS spot_relations (
        source_id      TEXT NOT NULL REFERENCES scenic_spots(id),
        target_id      TEXT NOT NULL REFERENCES scenic_spots(id),
        relation_type  TEXT NOT NULL,
        confidence     REAL DEFAULT 0.8,
        updated_at     TEXT DEFAULT (datetime('now')),
        PRIMARY KEY (source_id, target_id, relation_type)
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS event_spot_links (
        event_id       TEXT NOT NULL REFERENCES events(id),
        spot_id        TEXT NOT NULL REFERENCES scenic_spots(id),
        relevance      REAL DEFAULT 1.0,
        PRIMARY KEY (event_id, spot_id)
    )
    """,

    # ========================
    # 3. 审计与元数据
    # ========================

    """
    CREATE TABLE IF NOT EXISTS ingest_log (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        adapter_name   TEXT NOT NULL,
        status         TEXT NOT NULL,
        source_file    TEXT,
        records_added  INTEGER DEFAULT 0,
        records_updated INTEGER DEFAULT 0,
        error_message  TEXT,
        summary_json   TEXT,
        started_at     TEXT,
        finished_at    TEXT
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS query_log (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        query_text     TEXT NOT NULL,
        query_type     TEXT,
        result_count   INTEGER,
        latency_ms     INTEGER,
        queried_at     TEXT DEFAULT (datetime('now'))
    )
    """,

    """
    CREATE TABLE IF NOT EXISTS action_log (
        id             INTEGER PRIMARY KEY AUTOINCREMENT,
        action_type    TEXT NOT NULL,
        target         TEXT,
        payload_summary TEXT,
        status         TEXT,
        error_message  TEXT,
        created_at     TEXT DEFAULT (datetime('now'))
    )
    """,

    # ========================
    # 4. 视图
    # ========================

    """
    CREATE VIEW IF NOT EXISTS v_douyin_ranking AS
    SELECT s.name AS scenic_name,
           ms.value AS search_index,
           ms.daily_change AS search_daily_change,
           (SELECT ms2.value FROM metric_snapshots ms2
            WHERE ms2.spot_id = ms.spot_id AND ms2.date = ms.date
              AND ms2.source = 'douyin' AND ms2.metric_type = 'composite_index'
            LIMIT 1) AS composite_index,
           (SELECT ms2.daily_change FROM metric_snapshots ms2
            WHERE ms2.spot_id = ms.spot_id AND ms2.date = ms.date
              AND ms2.source = 'douyin' AND ms2.metric_type = 'composite_index'
            LIMIT 1) AS composite_daily_change
    FROM metric_snapshots ms
    JOIN scenic_spots s ON ms.spot_id = s.id
    WHERE ms.source = 'douyin'
      AND ms.metric_type = 'search_index'
      AND ms.date = (SELECT MAX(date) FROM metric_snapshots WHERE source = 'douyin')
    ORDER BY ms.value DESC
    """,

    """
    CREATE VIEW IF NOT EXISTS v_weekly_trend AS
    SELECT s.name AS scenic_name,
           ms.metric_type AS metric,
           ms.date AS date,
           ms.value AS value,
           ms.source AS source
    FROM metric_snapshots ms
    JOIN scenic_spots s ON ms.spot_id = s.id
    WHERE ms.date >= date('now', '-7 days')
    ORDER BY s.name, ms.metric_type, ms.date
    """,
]


# ─── 核心 Store 类 ───────────────────────────────

class OntologyStore:
    """Ontology Store: SQLite 数据库管理器"""

    def __init__(self, db_path=None):
        self.db_path = db_path or str(DB_PATH)
        self.conn = None

    def connect(self):
        """建立数据库连接（自动创建目录）"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        return self

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def __enter__(self):
        return self.connect()

    def __exit__(self, *args):
        self.close()

    # ── 初始化 ──

    def init_schema(self):
        """建表（幂等：IF NOT EXISTS）"""
        cursor = self.conn.cursor()
        for stmt in DDL_STATEMENTS:
            try:
                cursor.execute(stmt)
            except sqlite3.OperationalError as e:
                print(f"[⚠️] DDL 警告: {str(e)[:100]}")
        self.conn.commit()
        # 写入 schema 版本
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS _schema_version (
                version TEXT PRIMARY KEY,
                applied_at TEXT DEFAULT (datetime('now'))
            )
        """)
        cursor.execute(
            "INSERT OR REPLACE INTO _schema_version(version, applied_at) VALUES (?, datetime('now'))",
            (SCHEMA_VERSION,)
        )
        self.conn.commit()
        return self

    # ── 景区写入 ──

    def ingest_scenic_spots(self, spots: list[dict]) -> int:
        """批量插入/更新景区"""
        count = 0
        for spot in spots:
            self.conn.execute("""
                INSERT OR REPLACE INTO scenic_spots
                    (id, name, short_name, category, city, province, tier,
                     annual_capacity, is_core_competitor, competitors, tags,
                     updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                spot.get("id"),
                spot.get("name"),
                spot.get("short_name"),
                spot.get("category"),
                spot.get("city"),
                spot.get("province"),
                spot.get("tier", "secondary"),
                spot.get("annual_capacity"),
                1 if spot.get("is_core_competitor") else 0,
                json.dumps(spot.get("competitors", []), ensure_ascii=False),
                json.dumps(spot.get("tags", []), ensure_ascii=False),
            ))
            count += 1
        self.conn.commit()
        return count

    # ── 指标快照写入 ──

    def ingest_metric_snapshots(self, objects: list[dict], adapter_name: str = "unknown") -> int:
        """
        批量插入 MetricSnapshot 对象（幂等：INSERT OR REPLACE）
        
        输入: adapter 输出的 ontology objects 列表（仅 MetricSnapshot schema）
        返回: 插入行数
        """
        count = 0
        for obj in objects:
            if obj.get("schema") != "MetricSnapshot":
                continue
            self.conn.execute("""
                INSERT OR REPLACE INTO metric_snapshots
                    (id, spot_id, source, date, metric_type, value,
                     daily_change, weekly_change, confidence,
                     raw_data, metadata_json, ingested_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                obj.get("id"),
                obj.get("scenicSpotId"),
                obj.get("source"),
                obj.get("date"),
                obj.get("metricType"),
                obj.get("value"),
                obj.get("dailyChange"),
                obj.get("weeklyChange"),
                obj.get("confidence", 0.5),
                json.dumps(obj, ensure_ascii=False),
                json.dumps(obj.get("metadata"), ensure_ascii=False) if obj.get("metadata") else None,
            ))
            count += 1
        self.conn.commit()

        # 记录 ingest log
        if count > 0:
            date_str = objects[0].get("date", "") if objects else ""
            self._log_ingest(adapter_name, "success", records_added=count,
                             summary={"date": date_str, "object_type": "MetricSnapshot"})

        return count

    # ── 内容资产写入 ──

    def ingest_content_assets(self, objects: list[dict], adapter_name: str = "unknown") -> int:
        """批量插入 ContentAsset 对象"""
        count = 0
        for obj in objects:
            if obj.get("schema") != "ContentAsset":
                continue
            # spot_id 解析: 优先 mentions[0] → 回退 scenicSpotId 顶层字段 (D-019)
            mentions = obj.get("mentions", [])
            spot_id = mentions[0] if mentions else obj.get("scenicSpotId")

            self.conn.execute("""
                INSERT OR REPLACE INTO content_assets
                    (id, source, external_id, spot_id, title, description,
                     url, author, like_count, comment_count, share_count,
                     view_count, publish_date, content_type, sentiment,
                     is_viral, tags, raw_data, derived_from_metric_id, ingested_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
            """, (
                obj.get("id"),
                obj.get("platform") or obj.get("source"),  # 兼容 adapter 的 source 字段（D-018）
                obj.get("externalId"),
                spot_id,
                obj.get("title"),
                obj.get("description"),
                obj.get("url"),
                obj.get("authorName"),
                obj.get("likes", 0),
                obj.get("comments", 0),
                obj.get("shares", 0),
                obj.get("views", 0),
                obj.get("publishDate"),
                obj.get("type"),
                obj.get("sentiment"),
                1 if obj.get("isViral") else 0,
                json.dumps(obj.get("tags", []), ensure_ascii=False),
                json.dumps(obj, ensure_ascii=False),
                obj.get("derivedFromMetricSnapshotId"),
            ))
            count += 1
        self.conn.commit()

        if count > 0:
            self._log_ingest(adapter_name, "success", records_added=count,
                             summary={"object_type": "ContentAsset"})

        return count

    # ── 审计日志 ──

    def _log_ingest(self, adapter_name, status, source_file=None, records_added=0,
                    records_updated=0, error_message=None, summary=None):
        """内部：写入 ingest 日志"""
        self.conn.execute("""
            INSERT INTO ingest_log
                (adapter_name, status, source_file, records_added,
                 records_updated, error_message, summary_json,
                 started_at, finished_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'), datetime('now'))
        """, (
            adapter_name, status, source_file, records_added,
            records_updated, error_message,
            json.dumps(summary, ensure_ascii=False) if summary else None,
        ))
        self.conn.commit()

    # ── 查询函数 ──

    def daily_ranking(self, source="douyin", date=None):
        """某数据源某日期景区排名"""
        if date is None:
            cursor = self.conn.execute(
                "SELECT MAX(date) FROM metric_snapshots WHERE source = ?", (source,)
            )
            row = cursor.fetchone()
            date = row[0] if row else None

        if not date:
            return []

        cursor = self.conn.execute("""
            SELECT s.name, ms.value, ms.daily_change, ms.confidence
            FROM metric_snapshots ms
            JOIN scenic_spots s ON ms.spot_id = s.id
            WHERE ms.source = ? AND ms.date = ? AND ms.metric_type = 'search_index'
            ORDER BY ms.value DESC
        """, (source, date))
        return [dict(row) for row in cursor.fetchall()]

    def trend(self, spot_id, metric_type, days=7):
        """某景区某指标近 N 天趋势"""
        cursor = self.conn.execute("""
            SELECT date, value, daily_change
            FROM metric_snapshots
            WHERE spot_id = ? AND metric_type = ?
              AND date >= date('now', ? || ' days')
            ORDER BY date ASC
        """, (spot_id, metric_type, f"-{days}"))
        return [dict(row) for row in cursor.fetchall()]

    def anomaly_detection(self, date=None, threshold=20.0):
        """检测异常波动（日环比绝对值 > threshold%）"""
        if date is None:
            cursor = self.conn.execute("SELECT MAX(date) FROM metric_snapshots")
            row = cursor.fetchone()
            date = row[0] if row else None

        if not date:
            return []

        cursor = self.conn.execute("""
            SELECT s.name, ms.source, ms.metric_type, ms.value, ms.daily_change
            FROM metric_snapshots ms
            JOIN scenic_spots s ON ms.spot_id = s.id
            WHERE ms.date = ? AND ABS(ms.daily_change) > ?
            ORDER BY ABS(ms.daily_change) DESC
        """, (date, threshold))
        return [dict(row) for row in cursor.fetchall()]

    def stats(self):
        """数据库统计"""
        tables = ["scenic_spots", "metric_snapshots", "content_assets",
                   "events", "marketing_campaigns", "decision_rules"]
        result = {"schema_version": SCHEMA_VERSION, "db_path": self.db_path, "tables": {}}
        for t in tables:
            cursor = self.conn.execute(f"SELECT COUNT(*) FROM {t}")
            result["tables"][t] = cursor.fetchone()[0]

        # 最近一次 ingest
        cursor = self.conn.execute(
            "SELECT adapter_name, status, records_added, finished_at FROM ingest_log ORDER BY id DESC LIMIT 5"
        )
        result["recent_ingests"] = [dict(row) for row in cursor.fetchall()]

        return result


# ─── 种子数据：景区 ───────────────────────────────

SEED_SCENIC_SPOTS = [
    {
        "id": "movie_town", "name": "建业电影小镇", "short_name": "电影小镇",
        "category": "theme_park", "city": "郑州", "province": "河南",
        "tier": "primary", "annual_capacity": 123,
        "is_core_competitor": False,
        "competitors": ["only_henan", "yinji", "wansui_mountain", "qingming_riverside", "fangte"],
        "tags": ["沉浸式", "民国风", "电影文化"]
    },
    {
        "id": "only_henan", "name": "只有河南·戏剧幻城", "short_name": "只有河南",
        "category": "cultural_town", "city": "郑州", "province": "河南",
        "tier": "primary", "annual_capacity": None,
        "is_core_competitor": True,
        "competitors": ["movie_town", "qingming_riverside"],
        "tags": ["戏剧", "沉浸式", "文化IP"]
    },
    {
        "id": "wansui_mountain", "name": "万岁山武侠城", "short_name": "万岁山",
        "category": "theme_park", "city": "开封", "province": "河南",
        "tier": "national", "annual_capacity": None,
        "is_core_competitor": True,
        "competitors": ["movie_town", "qingming_riverside"],
        "tags": ["武侠", "实景演出", "性价比"]
    },
    {
        "id": "qingming_riverside", "name": "清明上河园", "short_name": "清园",
        "category": "historical", "city": "开封", "province": "河南",
        "tier": "national", "annual_capacity": None,
        "is_core_competitor": True,
        "competitors": ["movie_town", "wansui_mountain", "only_henan"],
        "tags": ["宋代文化", "实景演出", "5A景区"]
    },
    {
        "id": "fangte", "name": "郑州方特欢乐世界", "short_name": "方特",
        "category": "theme_park", "city": "郑州", "province": "河南",
        "tier": "secondary", "annual_capacity": None,
        "is_core_competitor": False,
        "competitors": ["movie_town", "yinji", "haichang"],
        "tags": ["游乐设施", "亲子", "连锁品牌"]
    },
    {
        "id": "yinji", "name": "郑州银基动物王国", "short_name": "银基",
        "category": "theme_park", "city": "郑州", "province": "河南",
        "tier": "secondary", "annual_capacity": None,
        "is_core_competitor": True,
        "competitors": ["movie_town", "fangte", "haichang"],
        "tags": ["动物主题", "亲子", "度假区"]
    },
    {
        "id": "haichang", "name": "郑州海昌海洋公园", "short_name": "海昌",
        "category": "theme_park", "city": "郑州", "province": "河南",
        "tier": "secondary", "annual_capacity": None,
        "is_core_competitor": False,
        "competitors": ["movie_town", "yinji", "fangte"],
        "tags": ["海洋主题", "亲子", "连锁品牌"]
    },
    {
        "id": "only_dream", "name": "只有红楼梦·戏剧幻城", "short_name": "只有红楼梦",
        "category": "cultural_town", "city": "廊坊", "province": "河北",
        "tier": "national", "annual_capacity": None,
        "is_core_competitor": False,
        "competitors": ["only_henan", "qingming_riverside"],
        "tags": ["红楼梦IP", "戏剧", "沉浸式"]
    },
]


# ─── 命令行入口 ──────────────────────────────────

def cmd_init():
    """初始化：建表 + 种子数据"""
    store = OntologyStore()
    with store:
        store.init_schema()
        n = store.ingest_scenic_spots(SEED_SCENIC_SPOTS)
        print(f"[✅] Schema 初始化完成 (v{SCHEMA_VERSION})")
        print(f"[✅] 种子数据: {n} 个景区已写入")
    # 显示文件大小
    size = os.path.getsize(DB_PATH)
    print(f"[📁] 数据库: {DB_PATH} ({size:,} bytes)")


def cmd_status():
    """查看数据库状态"""
    if not DB_PATH.exists():
        print(f"[⚠️] 数据库不存在: {DB_PATH}")
        print(f"[💡] 运行: python3 ontology_store.py init")
        return

    store = OntologyStore()
    with store:
        stats = store.stats()

    print(f"\n{'='*50}")
    print(f"  Ontology Store 状态")
    print(f"{'='*50}")
    print(f"  版本: {stats['schema_version']}")
    print(f"  路径: {stats['db_path']}")
    print(f"  大小: {os.path.getsize(DB_PATH):,} bytes")
    print(f"\n  数据表:")
    for table, count in stats["tables"].items():
        print(f"    {table}: {count} 行")
    print(f"\n  最近 Ingest:")
    for log in stats.get("recent_ingests", []):
        print(f"    [{log['status']}] {log['adapter_name']}: +{log['records_added']} @ {log['finished_at']}")
    print()


def cmd_query_test():
    """查询功能自测"""
    store = OntologyStore()
    with store:
        ranking = store.daily_ranking("douyin")
        print(f"[📊] 抖音排名 (top 3):")
        for i, r in enumerate(ranking[:3]):
            print(f"  {i+1}. {r['name']}: {r['value']} ({r['daily_change']:+.1f}%)")

        anomalies = store.anomaly_detection()
        if anomalies:
            print(f"\n[⚠️] 异常检测:")
            for a in anomalies:
                print(f"  {a['name']} {a['metric_type']}: {a['daily_change']:+.1f}%")
        else:
            print(f"\n[✅] 无异常波动")

        trend = store.trend("movie_town", "search_index", days=7)
        if trend:
            print(f"\n[📈] 电影小镇 搜索指数 近7天趋势:")
            for t in trend:
                bar = "█" * max(1, int(t['value'] / 100))
                print(f"  {t['date']}: {t['value']:>6.0f} {bar}")
        else:
            print(f"\n[📈] 暂无趋势数据")


# ─── main ────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("用法: python3 ontology_store.py [init|status|query|test]")
        print("  init   - 初始化数据库（建表 + 种子数据）")
        print("  status - 查看数据库状态")
        print("  query  - 查询功能自测")
        print("  test   - 同 query")
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == "init":
        cmd_init()
    elif cmd == "status":
        cmd_status()
    elif cmd in ("query", "test"):
        cmd_query_test()
    else:
        print(f"[❌] 未知命令: {cmd}")
        sys.exit(1)


if __name__ == "__main__":
    main()
