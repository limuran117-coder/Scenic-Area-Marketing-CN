#!/usr/bin/env python3
"""
Ontology 动态关系更新 adapter（P0 进化）
========================================
根据实际指标数据（metric_snapshots）动态重算景区间竞争强度，
取代 6/19 手工写死的 spot_relations。

核心逻辑：
  竞争强度 = f(搜索指数重叠度, 客流相关性, 内容量对比)
  - 搜索指数重叠：两景区搜索指数接近 → 竞争强（游客在两者间选择）
  - 客流相关性：两景区客流趋势同向波动 → 竞争强（同一客源池）
  - 内容量对比：内容产出接近 → 竞争强

用法：
  python adapter_relations.py          # 重算并更新 spot_relations
  python adapter_relations.py --dry    # 只打印将要的更新，不写库
"""
import json
import os
import sqlite3
import sys
from datetime import datetime, timedelta

DB_PATH = os.path.expanduser("~/.openclaw/workspace/.profile/ontology/ontology_store.db")

def connect():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(f"Ontology 生产库不存在: {DB_PATH}")
    return sqlite3.connect(DB_PATH)

def get_spots(conn):
    return {sid: name for sid, name, *_ in conn.execute("SELECT id, name FROM scenic_spots").fetchall()}

def get_metric_series(conn, spot_id, metric_type, days=30):
    """取某景区最近 N 天某指标序列 {date: value}"""
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    rows = conn.execute(
        """SELECT date, value FROM metric_snapshots
           WHERE spot_id=? AND metric_type=? AND date>=? AND value IS NOT NULL
           ORDER BY date""",
        (spot_id, metric_type, cutoff),
    ).fetchall()
    return {d: v for d, v in rows}

def search_index_series(conn, spot_id, days=30):
    """搜索指数序列（douyin source）"""
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    rows = conn.execute(
        """SELECT date, value FROM metric_snapshots
           WHERE spot_id=? AND source='douyin' AND metric_type='search_index' AND date>=? AND value IS NOT NULL
           ORDER BY date""",
        (spot_id, cutoff),
    ).fetchall()
    return {d: v for d, v in rows}

def pearson(a, b):
    """皮尔逊相关系数（两序列同日期交集）"""
    common = [d for d in a if d in b]
    if len(common) < 3:
        return 0.0
    xs = [a[d] for d in common]
    ys = [b[d] for d in common]
    n = len(xs)
    mx, my = sum(xs)/n, sum(ys)/n
    cov = sum((x-mx)*(y-my) for x, y in zip(xs, ys))
    vx = sum((x-mx)**2 for x in xs)
    vy = sum((y-my)**2 for y in ys)
    if vx == 0 or vy == 0:
        return 0.0
    return cov / (vx ** 0.5 * vy ** 0.5)

def overlap_ratio(a, b):
    """搜索指数重叠度：两序列值接近程度（0-1）
    支持少数据点（1-2 天），直接比较归一化值
    """
    common = [d for d in a if d in b]
    if not common:
        return 0.0
    xs = [a[d] for d in common]
    ys = [b[d] for d in common]
    xmax, ymax = max(xs), max(ys)
    if xmax == 0 or ymax == 0:
        return 0.0
    # 归一化到 [0,1] 后算平均绝对差，越小越重叠
    diffs = [abs(x/xmax - y/ymax) for x, y in zip(xs, ys)]
    return max(0.0, 1.0 - sum(diffs)/len(diffs))

def compute_competition(conn, spot_a, spot_b, days=30):
    """计算两个景区的竞争强度（0-1）
    搜索指数重叠 0.5 + 客流相关性 0.3 + 内容量对比 0.2
    任一维度无数据则跳过该维度并重新归一化权重
    """
    # 搜索指数重叠（权重 0.5）
    sa = search_index_series(conn, spot_a, days)
    sb = search_index_series(conn, spot_b, days)
    overlap = overlap_ratio(sa, sb) if sa and sb else None

    # 客流相关性（权重 0.3）
    va = get_metric_series(conn, spot_a, "visitors", days)
    vb = get_metric_series(conn, spot_b, "visitors", days)
    corr = pearson(va, vb) if va and vb else None

    # 内容量对比（权重 0.2）
    ca = get_metric_series(conn, spot_a, "content_count", days)
    cb = get_metric_series(conn, spot_b, "content_count", days)
    content_sim = overlap_ratio(ca, cb) if ca and cb else None

    # 收集可用维度并重新归一化权重
    dims = []
    if overlap is not None:
        dims.append(("overlap", overlap, 0.5))
    if corr is not None:
        dims.append(("corr", max(0, corr), 0.3))
    if content_sim is not None:
        dims.append(("content", content_sim, 0.2))
    if not dims:
        return 0.0
    total_w = sum(w for _, _, w in dims)
    score = sum(v * w for _, v, w in dims) / total_w
    return round(score, 3)

def main():
    dry = "--dry" in sys.argv
    conn = connect()
    spots = get_spots(conn)
    print(f"📊 景区: {len(spots)} 个")
    print(f"{'':4}计算竞争强度（30 天窗口）...")

    updates = []
    for a in spots:
        for b in spots:
            if a >= b:
                continue
            score = compute_competition(conn, a, b)
            updates.append((a, b, score))

    print(f"\n{'源景区':<12} {'目标景区':<12} {'竞争强度':<8} {'变化'}")
    print("-" * 50)
    for a, b, score in sorted(updates, key=lambda x: -x[2])[:15]:
        old = conn.execute(
            "SELECT confidence FROM spot_relations WHERE source_id=? AND target_id=? AND relation_type='competes_with'",
            (a, b),
        ).fetchone()
        old_val = old[0] if old else None
        delta = f"{score - old_val:+.3f}" if old_val is not None else "新增"
        print(f"{spots[a]:<12} {spots[b]:<12} {score:<8.3f} {delta}")

    if dry:
        print("\n[dry-run] 未写入")
        return

    # 更新 spot_relations
    updated = 0
    for a, b, score in updates:
        if score < 0.1:
            continue  # 太弱不建关系
        exists = conn.execute(
            "SELECT 1 FROM spot_relations WHERE source_id=? AND target_id=? AND relation_type='competes_with'",
            (a, b),
        ).fetchone()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if exists:
            conn.execute(
                """UPDATE spot_relations SET confidence=?, updated_at=?
                   WHERE source_id=? AND target_id=? AND relation_type='competes_with'""",
                (score, now, a, b),
            )
        else:
            conn.execute(
                """INSERT INTO spot_relations (source_id, target_id, relation_type, confidence, updated_at)
                   VALUES (?, ?, 'competes_with', ?, ?)""",
                (a, b, score, now),
            )
        updated += 1
    conn.commit()
    print(f"\n✅ 已更新 {updated} 条竞争关系（动态重算）")

if __name__ == "__main__":
    main()
