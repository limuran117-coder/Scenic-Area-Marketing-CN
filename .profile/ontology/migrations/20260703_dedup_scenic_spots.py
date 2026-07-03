"""
D-033: scenic_spots SSOT 去重迁移 (修订版 2)
=============================================
解决 D-29 决策遗留的「5 处重复 spot」问题。

策略: 每个重复组保留「数据更多」的那个 ID (canonical) 作为 winner,
     loser's FK 行重定向到 winner; 遇 UNIQUE 冲突时, winner 的行胜出 (loser 行删除).

合并映射 (基于 2026-07-03 22:30 实测):
  wansui_mountain  (10 metrics, 3 content) ← wansuishan            (loser, 仅 2 spot_relations)
  only_henan       (14 metrics, 4 content) ← only_dream            (loser, 10 metrics 有 6 行 UNIQUE 冲突)
  fangte           (13 metrics, 4 content) ← fangte_joy            (loser, 1 spot_rel)
  haichang         ( 8 metrics, 2 content) ← 海昌海洋公园           (loser, 2 metrics 不冲突)
  yinji            (13 metrics, 4 content) ← yinji_animal_kingdom  (loser, 2 spot_relations)

冲突解决: winner 的 existing row wins, loser 的 collision rows 被删除
         (loser 是更老/更不权威的别名; winner 是已积累数据的主 ID)

⚠️  本迁移是「破坏性」的: 删除 loser 行 + 部分 loser metrics. 跑前请先 snapshot。
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

ONTOLOGY_DIR = Path.home() / ".openclaw" / "workspace" / ".profile" / "ontology"
DB_PATH = ONTOLOGY_DIR / "ontology_store.db"

# (winner_id, loser_id, label) — winner 必须有数据
MERGES = [
    ("wansui_mountain", "wansuishan",          "万岁山武侠城"),
    ("only_henan",      "only_dream",          "只有河南·戏剧幻城"),
    ("fangte",          "fangte_joy",          "方特欢乐世界"),
    ("haichang",        "海昌海洋公园",         "海昌海洋公园"),
    ("yinji",           "yinji_animal_kingdom","银基动物王国"),
]


def dry_run(conn: sqlite3.Connection) -> dict:
    """报告: 每个 loser 的 FK 影响范围 + 预期 UNIQUE 冲突 (不写)"""
    cur = conn.cursor()
    report = {}
    for winner, loser, label in MERGES:
        info = {"label": label, "fk_impact": {}, "unique_collisions": 0, "mergeable_metrics": 0}
        # FK counts on loser side
        for tbl, col in [
            ("metric_snapshots", "spot_id"),
            ("content_assets", "spot_id"),
        ]:
            n = cur.execute(f"SELECT count(*) FROM {tbl} WHERE {col}=?", (loser,)).fetchone()[0]
            info["fk_impact"][f"{tbl}.{col}"] = n
        info["fk_impact"]["spot_relations_src"] = cur.execute(
            "SELECT count(*) FROM spot_relations WHERE source_id=?", (loser,)
        ).fetchone()[0]
        info["fk_impact"]["spot_relations_tgt"] = cur.execute(
            "SELECT count(*) FROM spot_relations WHERE target_id=?", (loser,)
        ).fetchone()[0]
        info["fk_impact"]["event_spot_links"] = cur.execute(
            "SELECT count(*) FROM event_spot_links WHERE spot_id=?", (loser,)
        ).fetchone()[0]
        info["fk_impact"]["campaign_spot_links"] = cur.execute(
            "SELECT count(*) FROM campaign_spot_links WHERE spot_id=?", (loser,)
        ).fetchone()[0]
        # UNIQUE collisions: how many loser metric_snapshots rows would clash with winner's existing rows
        n_total = info["fk_impact"]["metric_snapshots.spot_id"]
        n_collide = cur.execute("""
            SELECT count(*) FROM metric_snapshots l
            WHERE l.spot_id=? AND EXISTS (
              SELECT 1 FROM metric_snapshots w WHERE w.spot_id=?
                AND w.source=l.source AND w.date=l.date AND w.metric_type=l.metric_type
            )
        """, (loser, winner)).fetchone()[0]
        info["unique_collisions"] = n_collide
        info["mergeable_metrics"] = n_total - n_collide
        report[loser] = info
    return report


def apply(conn: sqlite3.Connection) -> dict:
    """执行迁移. 返回 summary stats."""
    cur = conn.cursor()
    summary = {}
    for winner, loser, _label in MERGES:
        st = {"mergeable": 0, "dropped_collision": 0, "spot_relations_merged": 0}
        # 1) metric_snapshots: 先记录 collide 数, 再删 collide, 再 UPDATE 剩余
        n_collide = cur.execute("""
            SELECT count(*) FROM metric_snapshots l
            WHERE l.spot_id=? AND EXISTS (
              SELECT 1 FROM metric_snapshots w WHERE w.spot_id=?
                AND w.source=l.source AND w.date=l.date AND w.metric_type=l.metric_type
            )
        """, (loser, winner)).fetchone()[0]
        st["dropped_collision"] = n_collide
        if n_collide:
            cur.execute("""
                DELETE FROM metric_snapshots WHERE spot_id=? AND EXISTS (
                  SELECT 1 FROM metric_snapshots w WHERE w.spot_id=?
                    AND w.source=metric_snapshots.source
                    AND w.date=metric_snapshots.date
                    AND w.metric_type=metric_snapshots.metric_type
                )
            """, (loser, winner))
        n_total = cur.execute(
            "SELECT count(*) FROM metric_snapshots WHERE spot_id=?", (loser,)
        ).fetchone()[0]
        st["mergeable"] = n_total
        cur.execute("UPDATE metric_snapshots SET spot_id=? WHERE spot_id=?", (winner, loser))
        # 2) content_assets
        cur.execute("UPDATE content_assets SET spot_id=? WHERE spot_id=?", (winner, loser))
        # 3) spot_relations: 计数 + UPDATE
        st["spot_relations_merged"] = cur.execute(
            "SELECT count(*) FROM spot_relations WHERE source_id=? OR target_id=?", (loser, loser)
        ).fetchone()[0]
        cur.execute("UPDATE spot_relations SET source_id=? WHERE source_id=?", (winner, loser))
        cur.execute("UPDATE spot_relations SET target_id=? WHERE target_id=?", (winner, loser))
        # 4) event_spot_links / campaign_spot_links
        cur.execute("UPDATE event_spot_links SET spot_id=? WHERE spot_id=?", (winner, loser))
        cur.execute("UPDATE campaign_spot_links SET spot_id=? WHERE spot_id=?", (winner, loser))
        # 5) 删除 loser scenic_spots 行
        cur.execute("DELETE FROM scenic_spots WHERE id=?", (loser,))
        summary[loser] = st
    conn.commit()
    return summary


def main() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else "dry"
    if mode not in ("dry", "apply"):
        print("usage: 20260703_dedup_scenic_spots.py [dry|apply]")
        return 2

    conn = sqlite3.connect(str(DB_PATH))
    report = dry_run(conn)
    print("=== 迁移影响报告 (dry) ===")
    total_collisions = 0
    for loser, info in report.items():
        print(f"\n  loser={loser}  →  winner ({info['label']})")
        for tbl, n in info["fk_impact"].items():
            print(f"    {tbl:35s} = {n}")
        print(f"    {'-> unique_collisions (to drop)':35s} = {info['unique_collisions']}")
        print(f"    {'-> mergeable_metrics (re-point)':35s} = {info['mergeable_metrics']}")
        total_collisions += info["unique_collisions"]

    print(f"\n>>> total UNIQUE collision rows to drop: {total_collisions}")

    if mode == "apply":
        print("\n>>> APPLY (commit)")
        summary = apply(conn)
        cur = conn.cursor()
        n_total = cur.execute("SELECT count(*) FROM scenic_spots").fetchone()[0]
        n_dup = cur.execute(
            "SELECT count(*) FROM (SELECT name, count(*) c FROM scenic_spots GROUP BY name HAVING c>1)"
        ).fetchone()[0]
        n_metric = cur.execute("SELECT count(*) FROM metric_snapshots").fetchone()[0]
        print(f"\n>>> AFTER: scenic_spots={n_total} (was 13, -5 losers)  duplicate_groups={n_dup}")
        print(f"           metric_snapshots={n_metric} (was 94, -{total_collisions} collisions dropped)")
        for loser, st in summary.items():
            print(f"    {loser}: mergeable={st['mergeable']} dropped_collision={st['dropped_collision']} relations={st['spot_relations_merged']}")
    else:
        print("\n(dry-run; no changes written; pass 'apply' to commit)")
    conn.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
