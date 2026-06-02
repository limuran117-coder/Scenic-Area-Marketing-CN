#!/opt/homebrew/bin/python3.12
"""
Ontology Query Engine: 预定义查询层

封装重复查询模式，直接输出日报/分析所需格式。
依赖: ontology_store.py（底层 SQLite 操作）

查询分类:
  1. 日报查询 — 每日排名/概览/关联词分析
  2. 趋势查询 — 多景区 N 天趋势/同比环比
  3. 异常检测 — 阈值触发/波动分析
  4. 关联查询 — 跨数据源 correlation

运行: python3 ontology_query.py [daily|trend|anomaly|correlate|test]
"""

from __future__ import annotations
import json
import sys
import datetime
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ontology_store import OntologyStore
from ontology_constants import (
    SCENIC_SPOT_REVERSE,
    METRIC_TYPES,
    SOURCE_TYPES,
    resolve_spot_id,
    resolve_spot_name,
)

# ─── 查询层 ──────────────────────────────────────


class OntologyQuery:
    """
    预定义查询集合。
    每个方法返回字典列表，可直接序列化为 JSON / Markdown 表格。
    """

    def __init__(self, db_path=None):
        self.store = OntologyStore(db_path=db_path)

    # ── 日报查询 ────────────────────────────────

    def daily_ranking(self, date=None, source="douyin", metric="search_index"):
        """
        某日某数据源排名
        Return: [{name, value, change, confidence, spot_id}, ...]
        """
        with self.store:
            results = self.store.daily_ranking(source=source, date=date)
        return [
            {
                "name": r["name"],
                "spot_id": resolve_spot_id(r["name"]),
                "value": r["value"],
                "change": r.get("daily_change"),
                "confidence": r.get("confidence"),
            }
            for r in results
        ]

    def latest_snapshot_date(self) -> str | None:
        """获取最新数据日期"""
        with self.store:
            conn = self.store.conn
            cur = conn.execute("SELECT MAX(date) FROM metric_snapshots")
            row = cur.fetchone()
            return row[0] if row else None

    def daily_overview(self):
        """
        多源汇总概览 — 最新日期的所有数据源对比
        """
        with self.store:
            conn = self.store.conn
            cur = conn.execute("""
                SELECT s.name, ms.source, ms.metric_type,
                       ms.value, ms.daily_change, ms.date
                FROM metric_snapshots ms
                JOIN scenic_spots s ON ms.spot_id = s.id
                WHERE ms.date = (SELECT MAX(date) FROM metric_snapshots)
                ORDER BY s.name, ms.source, ms.metric_type
            """)
            rows = [dict(r) for r in cur.fetchall()]
        return rows

    def visitor_summary(self, days=7):
        """最近 N 天客流/收入汇总"""
        with self.store:
            conn = self.store.conn
            cur = conn.execute("""
                SELECT date, metric_type, value
                FROM metric_snapshots
                WHERE spot_id = 'movie_town'
                  AND source = 'csv'
                  AND date >= date('now', ? || ' days')
                ORDER BY date DESC, metric_type
            """, (f"-{days}",))
            return [dict(r) for r in cur.fetchall()]

    # ── 趋势查询 ────────────────────────────────

    def trend(self, spot_id_or_name, metric_type, days=7):
        """景区指标趋势"""
        spot_id = resolve_spot_id(spot_id_or_name) if spot_id_or_name in SCENIC_SPOT_REVERSE.values() else spot_id_or_name

        with self.store:
            data = self.store.trend(spot_id, metric_type, days=days)

        if not data:
            return []

        values = [d["value"] for d in data if d["value"] is not None]
        return {
            "spot_name": resolve_spot_name(spot_id),
            "spot_id": spot_id,
            "metric": metric_type,
            "metric_label": METRIC_TYPES.get(metric_type, metric_type),
            "days": len(data),
            "data": data,
            "stats": {
                "latest": values[-1] if values else None,
                "avg": round(sum(values) / len(values), 1) if values else None,
                "min": min(values) if values else None,
                "max": max(values) if values else None,
                "trend": _calc_trend(values),
            } if values else {},
        }

    # ── 异常检测 ────────────────────────────────

    def anomaly_check(self, date=None, threshold=20.0):
        """异常波动检测"""
        with self.store:
            anomalies = self.store.anomaly_detection(date=date, threshold=threshold)

        return [
            {
                "spot_name": resolve_spot_name(a["spot_id"]),
                "spot_id": a["spot_id"],
                "date": a["date"],
                "metric_type": a["metric_type"],
                "value": a["value"],
                "change": a["change"],
                "change_pct": a.get("change_pct"),
                "is_anomaly": True,
            }
            for a in anomalies
        ]

    # ── 跨源关联 ────────────────────────────────

    def cross_source_correlation(self, spot_id="movie_town", days=30):
        """跨数据源指标相关性概览"""
        with self.store:
            conn = self.store.conn
            cur = conn.execute("""
                SELECT date, source, metric_type, value
                FROM metric_snapshots
                WHERE spot_id = ?
                  AND date >= date('now', ? || ' days')
                  AND source IN ('douyin', 'xiaohongshu', 'csv')
                ORDER BY date DESC, source
            """, (spot_id, f"-{days}"))
            rows = [dict(r) for r in cur.fetchall()]

        # 按日期分组
        by_date = {}
        for r in rows:
            d = r["date"]
            if d not in by_date:
                by_date[d] = {}
            by_date[d][f"{r['source']}_{r['metric_type']}"] = r["value"]

        return {
            "spot_name": resolve_spot_name(spot_id),
            "spot_id": spot_id,
            "days_covered": len(by_date),
            "by_date": dict(sorted(by_date.items(), reverse=True)),
        }

    # ── 景区对比 ────────────────────────────────

    def competitor_comparison(self, date=None, source="douyin", metric="search_index"):
        """竞品对比"""
        ranking = self.daily_ranking(date=date, source=source, metric=metric)
        if not ranking:
            return {"date": date or "N/A", "ranking": []}

        movie_town_idx = next(
            (i for i, r in enumerate(ranking) if r["spot_id"] == "movie_town"), None
        )

        return {
            "date": ranking[0].get("date", date),
            "source": source,
            "metric": metric,
            "ranking": ranking,
            "movie_town_rank": (movie_town_idx + 1) if movie_town_idx is not None else None,
            "movie_town_value": ranking[movie_town_idx]["value"] if movie_town_idx is not None else None,
        }

    # ── 库存统计 ────────────────────────────────

    def store_stats(self):
        """数据库统计"""
        with self.store:
            conn = self.store.conn

            tables = ["scenic_spots", "metric_snapshots", "content_assets", "events"]
            stats = {}
            for t in tables:
                cur = conn.execute(f"SELECT COUNT(*) FROM {t}")
                stats[t] = cur.fetchone()[0]

            cur = conn.execute("""
                SELECT source, COUNT(*) as cnt, MAX(date) as latest_date
                FROM metric_snapshots
                GROUP BY source
                ORDER BY cnt DESC
            """)
            stats["by_source"] = [dict(r) for r in cur.fetchall()]

            cur = conn.execute("""
                SELECT spot_id, COUNT(*) as cnt,
                       MIN(date) as first_date, MAX(date) as latest_date
                FROM metric_snapshots
                GROUP BY spot_id
                ORDER BY cnt DESC
            """)
            stats["by_spot"] = [dict(r) for r in cur.fetchall()]

        return stats


# ─── 工具函数 ────────────────────────────────────


def _calc_trend(values: list[float]) -> str:
    """简单趋势判断"""
    if len(values) < 2:
        return "flat"
    half = len(values) // 2
    first_half_avg = sum(values[:half]) / half
    second_half_avg = sum(values[-half:]) / half
    diff_pct = (second_half_avg - first_half_avg) / max(first_half_avg, 1) * 100
    if diff_pct > 5:
        return "up"
    elif diff_pct < -5:
        return "down"
    return "flat"


def _format_table(headers, rows, col_widths=None):
    """简易表格格式化"""
    if not rows:
        return "无数据"
    if not col_widths:
        col_widths = [max(len(str(h)), 8) for h in headers]
        for row in rows:
            for i, v in enumerate(row):
                col_widths[i] = max(col_widths[i], len(str(v)))
    sep = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    header_row = "| " + " | ".join(h.center(w) for h, w in zip(headers, col_widths)) + " |"
    lines = [sep, header_row, sep]
    for row in rows:
        lines.append("| " + " | ".join(str(v).ljust(w) for v, w in zip(row, col_widths)) + " |")
    lines.append(sep)
    return "\n".join(lines)


# ─── CLI ─────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(description="Ontology Query Engine")
    parser.add_argument("action", nargs="?", default="test",
                        choices=["daily", "trend", "anomaly", "correlate", "visitors", "stats", "test"])
    parser.add_argument("--spot", default="movie_town", help="景区ID")
    parser.add_argument("--days", type=int, default=7, help="天数")
    parser.add_argument("--source", default="douyin", help="数据源")
    args = parser.parse_args()

    q = OntologyQuery()

    if args.action == "daily":
        result = q.daily_ranking(source=args.source)
        print(f"\n📊 {SOURCE_TYPES.get(args.source, args.source)} 最新排名:")
        rows = [[r["name"], f"{r['value']:,.0f}", f"{r.get('change') or '—'}"] for r in result]
        print(_format_table(["景区", "指数", "涨跌"], rows))

    elif args.action == "trend":
        result = q.trend(args.spot, "search_index", days=args.days)
        if result and result["data"]:
            print(f"\n📈 {result['spot_name']} · {result['metric_label']} · {result['days']}天")
            print(f"  最新: {result['stats']['latest']:,.0f}  |  均: {result['stats']['avg']:,.0f}  |  趋势: {result['stats']['trend']}")
            for d in result["data"]:
                print(f"  {d['date']}  {d['value']:>8,.0f}  ({d.get('daily_change') or '—'})")

    elif args.action == "anomaly":
        anomalies = q.anomaly_check(threshold=15.0)
        print(f"\n🚨 异常检测 ({len(anomalies)}):")
        for a in anomalies[:20]:
            print(f"  {a['spot_name']} | {a['date']} | {a['metric_type']} | {a['value']:,.0f} | 变化: {a['change']}%")

    elif args.action == "visitors":
        result = q.visitor_summary(days=args.days)
        visitors = [r for r in result if r["metric_type"] == "visitors"]
        revenues = [r for r in result if r["metric_type"] == "revenue"]
        print(f"\n🎟 电影小镇客流 ({len(visitors)}天):")
        for v in visitors[:10]:
            print(f"  {v['date']}  {v['value']:>8,.0f}")
        if revenues:
            print(f"\n💰 门票收入:")
            for r in revenues[:10]:
                print(f"  {r['date']}  {r['value']:>10,.0f}")

    elif args.action == "stats":
        stats = q.store_stats()
        print(f"\n📦 Ontology Store 统计:")
        for t in ["scenic_spots", "metric_snapshots", "content_assets", "events"]:
            print(f"  {t}: {stats[t]}")
        print(f"\n  按数据源:")
        for s in stats["by_source"]:
            print(f"    {s['source']:15s}  {s['cnt']:>5d}  最新: {s['latest_date']}")

    elif args.action == "correlate":
        result = q.cross_source_correlation(args.spot, days=args.days)
        print(f"\n🔗 {result['spot_name']} 跨源关联 ({result['days_covered']}天)")
        for date, metrics in list(result["by_date"].items())[:10]:
            print(f"  {date}:", ", ".join(f"{k}={v:,.0f}" for k, v in metrics.items()))

    elif args.action == "test":
        print("🏃 OntologyQuery 测试")
        stats = q.store_stats()
        assert stats["scenic_spots"] >= 8, f"景区不足: {stats['scenic_spots']}"
        assert stats["metric_snapshots"] > 0, "无 MetricSnapshot 数据"

        ranking = q.daily_ranking()
        assert len(ranking) > 0, "排名查询失败"

        trend = q.trend("movie_town", "search_index", days=7)
        assert trend and trend.get("data"), "趋势查询失败"

        print(f"✅ 全部通过: {stats['metric_snapshots']} snapshots, {stats['scenic_spots']} spots")
        print(f"  最新数据日期: {q.latest_snapshot_date()}")


if __name__ == "__main__":
    main()
