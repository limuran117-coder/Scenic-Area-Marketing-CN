#!/usr/bin/env python3
"""
Ontology → Graphiti 打通：把自研 Ontology（静态业务图谱）的关键事实灌入 Graphiti（时序图谱）

方向: Ontology (SQLite) → Graphiti (FalkorDB)
价值: Graphiti 检索时获得业务上下文（竞品关系、景区定位、指标趋势），能回答
      "电影小镇的主要竞争对手是谁" / "8月客流趋势如何" 等跨库问题

用法:
  python sync_ontology.py             # 同步核心事实（景区+竞争关系，推荐）
  python sync_ontology.py --metrics   # 同步最近 30 天指标快照（⚠️ 数据量大，16GB 机器慎用）
  python sync_ontology.py --all       # 全量同步
"""
import asyncio
import glob
import os
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from graphiti_local import build_client

GROUP_ID = "movie-town"
ONTOLOGY_DB = os.path.expanduser("~/.openclaw/workspace/.profile/ontology/ontology_store.db")

def connect():
    if not os.path.exists(ONTOLOGY_DB):
        raise FileNotFoundError(f"Ontology 生产库不存在: {ONTOLOGY_DB}")
    return sqlite3.connect(ONTOLOGY_DB)

def get_spots(conn):
    """景区实体"""
    cur = conn.execute("SELECT id, name, category, tier FROM scenic_spots")
    return cur.fetchall()

def get_relations(conn):
    """景区间关系"""
    cur = conn.execute(
        "SELECT source_id, target_id, relation_type, confidence FROM spot_relations"
    )
    return cur.fetchall()

def get_latest_metrics(conn, days=30):
    """最近 N 天指标快照（游客量）"""
    cutoff = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    cur = conn.execute(
        """SELECT spot_id, date, metric_type, value
           FROM metric_snapshots
           WHERE date >= ? AND metric_type IN ('visitors','revenue')
           ORDER BY date""",
        (cutoff,),
    )
    return cur.fetchall()

def build_episodes(spots, relations, metrics, include_metrics=False):
    """构建 episode 列表"""
    episodes = []

    # 1. 景区定位（关系型）
    spot_names = {sid: name for sid, name, cat, t in spots}
    for sid, name, cat, t in spots:
        if not t:
            continue
        body = f"{name}是位于郑州的{cat}类景区，是郑州电影小镇的行业对标对象。"
        episodes.append({
            "name": f"景区-{sid}",
            "body": body,
            "date": datetime.now().strftime("%Y-%m-%d"),
        })

    # 2. 竞争关系（核心关系型事实）
    rel_labels = {"competes_with": "主要竞争对手", "located_in": "位于", "supplier_of": "供应商"}
    for sid, tid, rtype, weight in relations:
        if sid not in spot_names or tid not in spot_names:
            continue
        src, tgt = spot_names[sid], spot_names[tid]
        label = rel_labels.get(rtype, rtype)
        body = f"{src}与{tgt}存在{label}关系，置信度{weight:.2f}。"
        episodes.append({
            "name": f"关系-{sid}-{rtype}-{tid}",
            "body": body,
            "date": datetime.now().strftime("%Y-%m-%d"),
        })

    # 3. 指标趋势（可选，关系型）
    if include_metrics:
        by_spot = {}
        for spot_id, date, mtype, value in metrics:
            by_spot.setdefault(spot_id, []).append((date, mtype, value))
        for sid, rows in by_spot.items():
            if sid not in spot_names:
                continue
            visitors = [(d, v) for d, m, v in rows if m == "visitors"]
            if not visitors:
                continue
            latest_d, latest_v = visitors[-1]
            if len(visitors) >= 2:
                prev_v = visitors[-2][1]
                if prev_v > 0:
                    delta = (latest_v - prev_v) / prev_v * 100
                    trend = f"较上一记录{prev_v:.0f}人{'增长' if delta >= 0 else '下降'}{abs(delta):.1f}%"
                else:
                    trend = ""
            else:
                trend = ""
            body = (
                f"{spot_names[sid]}在{latest_d}的游客量为{latest_v:.0f}人，{trend}。"
                f"该数据反映其市场热度，与郑州电影小镇竞争格局相关。"
            )
            episodes.append({
                "name": f"指标-{sid}-{latest_d}",
                "body": body,
                "date": latest_d,
            })

    return episodes

async def sync(include_metrics=False):
    print(f"📄 Ontology 生产库: {ONTOLOGY_DB}")
    conn = connect()
    spots = get_spots(conn)
    relations = get_relations(conn)
    metrics = get_latest_metrics(conn, 30) if include_metrics else []
    print(f"📊 读取: {len(spots)} 景区, {len(relations)} 关系, {len(metrics)} 指标")

    episodes = build_episodes(spots, relations, metrics, include_metrics)
    print(f"📝 准备写入 {len(episodes)} 条 episode")
    for ep in episodes[:5]:
        print(f"  - {ep['name']}: {ep['body'][:50]}...")
    if len(episodes) > 5:
        print(f"  ... 等 {len(episodes)-5} 条")

    g = build_client()
    # 分批写入，避免单次调用过多导致进程被 kill（每条需 DeepSeek 抽取 + embedding）
    batch_size = 5
    for i in range(0, len(episodes), batch_size):
        batch = episodes[i:i + batch_size]
        print(f"  ▶ 批次 {i//batch_size + 1}/{(len(episodes) + batch_size - 1)//batch_size} ({len(batch)} 条)...")
        for ep in batch:
            ref_time = datetime.strptime(ep["date"], "%Y-%m-%d").replace(tzinfo=timezone.utc)
            await g.add_episode(
                name=ep["name"],
                episode_body=ep["body"],
                source_description="Ontology 业务图谱同步",
                reference_time=ref_time,
                group_id=GROUP_ID,
            )
        print(f"  ✅ 批次完成")
    print(f"\n🎉 同步完成！共 {len(episodes)} 条")

if __name__ == "__main__":
    include_metrics = "--metrics" in sys.argv or "--all" in sys.argv
    asyncio.run(sync(include_metrics))
