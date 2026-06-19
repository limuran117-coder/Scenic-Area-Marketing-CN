"""
Ontology Query — 预定义查询引擎
对标 Palantir OSDK 的 ObjectSet 查询模式

设计原则（关注点分离 §实践 8）：
- 应用层（日报/飞书）只调用本模块的预定义查询
- 绝不直接写 SQL
- 复杂查询封装为方法名,接受简单参数
- 所有查询自动 log 到 query_log 表
"""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Literal

from ontology_store import DB_PATH, DEFAULT_CONFIDENCE


class OntologyQuery:
    """封装所有预定义 Ontology 查询"""

    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _log_query(self, name: str, qtype: str, count: int, latency_ms: int) -> None:
        """记录查询日志"""
        try:
            with self._connect() as conn:
                conn.execute(
                    """INSERT INTO query_log
                       (query_name, query_type, result_count, latency_ms)
                       VALUES (?, ?, ?, ?)""",
                    (name, qtype, count, latency_ms),
                )
        except Exception:
            pass  # 不阻塞主查询

    # ============================================
    # 抖音日报查询
    # ============================================
    def daily_douyin_ranking(self, date: str | None = None) -> list[dict]:
        """
        抖音 8 景区排名（飞书日报核心表）

        Args:
            date: YYYY-MM-DD, 默认最新一天
        Returns:
            list of {景区ID, 景区, 搜索指数, 搜索日环比, 综合指数, 综合日环比}
        """
        t0 = time.time()
        with self._connect() as conn:
            cur = conn.cursor()
            if date is None:
                # 取最新一天
                cur.execute(
                    """SELECT MAX(date) FROM metric_snapshots
                       WHERE source = 'douyin' AND metric_type = 'search_index'"""
                )
                row = cur.fetchone()
                date = row[0] if row else None

            if not date:
                return []

            cur.execute(
                """
                SELECT
                    s.id AS 景区ID,
                    s.name AS 景区,
                    s.short_name AS 简称,
                    s.is_core_competitor AS 是否核心竞品,
                    ms_search.value AS 搜索指数,
                    ms_search.daily_change AS 搜索日环比,
                    ms_comp.value AS 综合指数,
                    ms_comp.daily_change AS 综合日环比,
                    ms_search.confidence AS 置信度
                FROM scenic_spots s
                LEFT JOIN metric_snapshots ms_search
                    ON ms_search.spot_id = s.id
                    AND ms_search.source = 'douyin'
                    AND ms_search.metric_type = 'search_index'
                    AND ms_search.date = ?
                LEFT JOIN metric_snapshots ms_comp
                    ON ms_comp.spot_id = s.id
                    AND ms_comp.source = 'douyin'
                    AND ms_comp.metric_type = 'composite_index'
                    AND ms_comp.date = ?
                WHERE ms_search.value IS NOT NULL
                ORDER BY ms_search.value DESC
                """,
                (date, date),
            )
            rows = [dict(r) for r in cur.fetchall()]

        latency = int((time.time() - t0) * 1000)
        self._log_query("daily_douyin_ranking", "ranking", len(rows), latency)
        return rows

    # ============================================
    # 跨景区对比
    # ============================================
    def scenic_spot_metrics(
        self,
        spot_id: str,
        days: int = 7,
        sources: list[str] | None = None,
    ) -> dict:
        """
        单景区多日多源数据（趋势分析用）

        Returns:
            {
              "spot": {id, name, ...},
              "metrics": [
                {date, source, metric_type, value, daily_change},
                ...
              ]
            }
        """
        t0 = time.time()
        if sources is None:
            sources = ["douyin", "xiaohongshu"]

        with self._connect() as conn:
            cur = conn.cursor()
            # 景区基本信息
            cur.execute("SELECT * FROM scenic_spots WHERE id = ?", (spot_id,))
            spot_row = cur.fetchone()
            if not spot_row:
                return {"spot": None, "metrics": []}
            spot = dict(spot_row)

            # 趋势数据
            cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            placeholders = ",".join("?" for _ in sources)
            cur.execute(
                f"""
                SELECT date, source, metric_type, value, daily_change, confidence
                FROM metric_snapshots
                WHERE spot_id = ?
                  AND date >= ?
                  AND source IN ({placeholders})
                ORDER BY date DESC, source, metric_type
                """,
                (spot_id, cutoff, *sources),
            )
            metrics = [dict(r) for r in cur.fetchall()]

        latency = int((time.time() - t0) * 1000)
        self._log_query("scenic_spot_metrics", "trend", len(metrics), latency)
        return {"spot": spot, "metrics": metrics}

    # ============================================
    # 竞品对比
    # ============================================
    def competitor_comparison(
        self,
        date: str | None = None,
        source: str = "douyin",
        metric_type: str = "search_index",
    ) -> list[dict]:
        """
        电影小镇 vs 核心竞品对比
        """
        t0 = time.time()
        with self._connect() as conn:
            cur = conn.cursor()
            if not date:
                cur.execute(
                    """SELECT MAX(date) FROM metric_snapshots
                       WHERE source = ? AND metric_type = ?""",
                    (source, metric_type),
                )
                row = cur.fetchone()
                date = row[0] if row else None
            if not date:
                return []

            cur.execute(
                """
                SELECT
                    s.id, s.name, s.category,
                    ms.value, ms.daily_change, ms.confidence
                FROM scenic_spots s
                JOIN metric_snapshots ms ON ms.spot_id = s.id
                WHERE s.is_core_competitor = 1
                  AND ms.source = ?
                  AND ms.metric_type = ?
                  AND ms.date = ?
                ORDER BY ms.value DESC
                """,
                (source, metric_type, date),
            )
            rows = [dict(r) for r in cur.fetchall()]

        latency = int((time.time() - t0) * 1000)
        self._log_query("competitor_comparison", "comparison", len(rows), latency)
        return rows

    # ============================================
    # 内容资产查询
    # ============================================
    def recent_content(
        self,
        spot_id: str | None = None,
        source: str = "xiaohongshu",
        days: int = 7,
        limit: int = 20,
    ) -> list[dict]:
        """最近内容资产列表"""
        t0 = time.time()
        cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        with self._connect() as conn:
            cur = conn.cursor()
            if spot_id:
                cur.execute(
                    """SELECT * FROM content_assets
                       WHERE spot_id = ? AND source = ?
                         AND publish_date >= ?
                       ORDER BY publish_date DESC LIMIT ?""",
                    (spot_id, source, cutoff, limit),
                )
            else:
                cur.execute(
                    """SELECT * FROM content_assets
                       WHERE source = ? AND publish_date >= ?
                       ORDER BY publish_date DESC LIMIT ?""",
                    (source, cutoff, limit),
                )
            rows = [dict(r) for r in cur.fetchall()]

        latency = int((time.time() - t0) * 1000)
        self._log_query("recent_content", "content", len(rows), latency)
        return rows

    # ============================================
    # 7天内容增量
    # ============================================
    def content_growth_7d(self) -> list[dict]:
        """过去 7 天各景区内容增量（飞书日报用）"""
        t0 = time.time()
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                SELECT
                    s.id AS 景区ID,
                    s.name AS 景区,
                    ca.source AS 平台,
                    SUM(ca.notes_count) AS 内容总数,
                    COUNT(ca.id) AS 笔记条数,
                    MAX(ca.publish_date) AS 最近更新
                FROM content_assets ca
                JOIN scenic_spots s ON ca.spot_id = s.id
                WHERE ca.publish_date >= date('now', '-7 days')
                GROUP BY s.id, ca.source
                ORDER BY 内容总数 DESC
                """
            )
            rows = [dict(r) for r in cur.fetchall()]

        latency = int((time.time() - t0) * 1000)
        self._log_query("content_growth_7d", "growth", len(rows), latency)
        return rows

    # ============================================
    # 事件查询
    # ============================================
    def recent_events(
        self,
        severity: str | None = None,
        event_type: str | None = None,
        days: int = 7,
    ) -> list[dict]:
        """最近事件/动态列表"""
        t0 = time.time()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        with self._connect() as conn:
            cur = conn.cursor()
            conditions = ["occurred_at >= ?"]
            params: list = [cutoff]
            if severity:
                conditions.append("severity = ?")
                params.append(severity)
            if event_type:
                conditions.append("type = ?")
                params.append(event_type)
            where = " AND ".join(conditions)
            cur.execute(
                f"""SELECT * FROM events WHERE {where}
                    ORDER BY occurred_at DESC LIMIT 50""",
                tuple(params),
            )
            rows = [dict(r) for r in cur.fetchall()]

        latency = int((time.time() - t0) * 1000)
        self._log_query("recent_events", "events", len(rows), latency)
        return rows

    # ============================================
    # 决策规则查询
    # ============================================
    def decision_rules(self, status: str | None = None) -> list[dict]:
        """决策规则列表（验证 / 假设）"""
        t0 = time.time()
        with self._connect() as conn:
            cur = conn.cursor()
            if status:
                cur.execute(
                    "SELECT * FROM decision_rules WHERE status = ? ORDER BY authority_tier, rule_id",
                    (status,),
                )
            else:
                cur.execute(
                    "SELECT * FROM decision_rules ORDER BY status, authority_tier, rule_id"
                )
            rows = [dict(r) for r in cur.fetchall()]

        latency = int((time.time() - t0) * 1000)
        self._log_query("decision_rules", "rules", len(rows), latency)
        return rows

    # ============================================
    # 链路查询（多跳）
    # ============================================
    def metric_with_sources(self, metric_id: str) -> dict:
        """追溯一个 metric 的来源内容资产（双向引用 §实践 6）"""
        t0 = time.time()
        with self._connect() as conn:
            cur = conn.cursor()
            # 1. 主 metric
            cur.execute("SELECT * FROM metric_snapshots WHERE id = ?", (metric_id,))
            metric = cur.fetchone()
            if not metric:
                return {}
            metric = dict(metric)

            # 2. 通过 link 表找 content_assets
            cur.execute(
                """SELECT ca.* FROM content_assets ca
                   JOIN metric_content_links mcl ON mcl.content_id = ca.id
                   WHERE mcl.metric_id = ?""",
                (metric_id,),
            )
            contents = [dict(r) for r in cur.fetchall()]

            # 3. 反向：通过 metadata.content_asset_ids 找
            if not contents and metric.get("metadata"):
                try:
                    meta = json.loads(metric["metadata"])
                    content_ids = meta.get("content_asset_ids", [])
                    if content_ids:
                        placeholders = ",".join("?" for _ in content_ids)
                        cur.execute(
                            f"SELECT * FROM content_assets WHERE id IN ({placeholders})",
                            tuple(content_ids),
                        )
                        contents = [dict(r) for r in cur.fetchall()]
                except Exception:
                    pass

        latency = int((time.time() - t0) * 1000)
        self._log_query("metric_with_sources", "traversal", len(contents), latency)
        return {"metric": metric, "sources": contents}

    # ============================================
    # 健康 / 状态
    # ============================================
    def health_check(self) -> dict:
        """系统健康检查（用于心跳 / cron 监控）"""
        t0 = time.time()
        out: dict[str, Any] = {"timestamp": datetime.now().isoformat()}
        with self._connect() as conn:
            cur = conn.cursor()

            # 1. 各表行数
            tables = [
                "scenic_spots", "metric_snapshots", "content_assets",
                "events", "decision_rules", "marketing_campaigns",
            ]
            for t in tables:
                cur.execute(f"SELECT COUNT(*) FROM {t}")
                out[t] = cur.fetchone()[0]

            # 2. 最新采集时间
            cur.execute(
                "SELECT MAX(finished_at) FROM ingest_log WHERE status='success'"
            )
            out["last_successful_ingest"] = cur.fetchone()[0]

            # 3. 最近 7 天 ingest 次数
            cur.execute(
                """SELECT COUNT(*) FROM ingest_log
                   WHERE finished_at >= datetime('now', '-7 days')"""
            )
            out["ingest_count_7d"] = cur.fetchone()[0]

            # 4. 最近失败 ingest
            cur.execute(
                """SELECT adapter_name, error_message, finished_at
                   FROM ingest_log
                   WHERE status='failed'
                   ORDER BY id DESC LIMIT 3"""
            )
            out["recent_failures"] = [dict(r) for r in cur.fetchall()]

        latency = int((time.time() - t0) * 1000)
        out["query_latency_ms"] = latency
        self._log_query("health_check", "meta", 1, latency)
        return out


# ============================================
# CLI 入口
# ============================================
def main():
    import sys
    q = OntologyQuery()

    if len(sys.argv) < 2 or sys.argv[1] == "help":
        print("""
Ontology Query 预定义查询：
  python ontology_query.py douyin              # 抖音8景区排名
  python ontology_query.py spot <id>           # 单景区趋势
  python ontology_query.py competitor          # 竞品对比
  python ontology_query.py content [spot_id]   # 最近内容
  python ontology_query.py growth              # 7天内容增量
  python ontology_query.py events              # 最近事件
  python ontology_query.py rules              # 决策规则
  python ontology_query.py health              # 健康检查
  python ontology_query.py metric <id>         # metric 溯源
        """)
        return

    cmd = sys.argv[1]
    if cmd == "douyin":
        rows = q.daily_douyin_ranking()
        for r in rows:
            print(f"  {r['景区']:20s} 搜索={r['搜索指数']:>10} "
                  f"({r['搜索日环比']:+.1f}%) 综合={r['综合指数']}")
    elif cmd == "spot":
        if len(sys.argv) < 3:
            print("usage: spot <spot_id>")
            return
        result = q.scenic_spot_metrics(sys.argv[2])
        print(f"景区: {result['spot']['name'] if result['spot'] else 'N/A'}")
        for m in result['metrics'][:10]:
            print(f"  [{m['date']}] {m['source']}/{m['metric_type']}: {m['value']}")
    elif cmd == "competitor":
        for r in q.competitor_comparison():
            print(f"  {r['name']:20s} {r['value']:>10}")
    elif cmd == "content":
        spot = sys.argv[2] if len(sys.argv) > 2 else None
        for r in q.recent_content(spot_id=spot)[:5]:
            print(f"  [{r['publish_date']}] {r['source']}/{r['title'][:40]}")
    elif cmd == "growth":
        for r in q.content_growth_7d():
            print(f"  {r['景区']:20s} {r['平台']:12s} 内容总数={r['内容总数']}")
    elif cmd == "events":
        for r in q.recent_events()[:5]:
            print(f"  [{r['severity']}] {r['title'][:50]}")
    elif cmd == "rules":
        for r in q.decision_rules():
            print(f"  [{r['status']:12s}] {r['rule_id']:8s} {r['name']}")
    elif cmd == "health":
        import json
        print(json.dumps(q.health_check(), ensure_ascii=False, indent=2))
    elif cmd == "metric":
        if len(sys.argv) < 3:
            print("usage: metric <metric_id>")
            return
        result = q.metric_with_sources(sys.argv[2])
        if result.get("metric"):
            print(f"metric: {result['metric']['id']} value={result['metric']['value']}")
            print(f"sources: {len(result.get('sources', []))} 个内容资产")
            for s in result.get("sources", [])[:3]:
                print(f"  - {s.get('title', '?')[:50]}")
    else:
        print(f"unknown: {cmd}")


if __name__ == "__main__":
    main()
