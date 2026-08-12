#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
cron_governor.py — Cron 自进化治理引擎（数据层，纯 Python，不引 LLM）
======================================================================
站长愿景 2026-08-12：不只手工修一次，让系统持续体检 cron、发现异常、自动提出/执行优化。

本脚本是 cron 进化的【数据层】，负责：
  --daily  每日哨兵：近 14 天异常任务清单（连续失败 / 超时撞顶 / 高错误率）
  --weekly 每周治理：深度健康报告（成功率/耗时/时段限流）+ 进化建议 JSON
  --apply  应用安全优化（禁孤儿任务 / 提高超时上限），--dry-run 先预览

安全边界（绝不自动做）：
  - 不自动改业务时段（错峰只出"建议"字段，人工决定）
  - 不自动删除任务（只建议）
  - 不自动改 prompt/message（太复杂，留给 human/LLM 决策层）
  - 只自动应用两项"零风险"项：禁用确认孤儿任务 + 提高明显偏低的超时

用法：
  python3 scripts/cron_governor.py --daily
  python3 scripts/cron_governor.py --weekly [--days 14]
  python3 scripts/cron_governor.py --apply --dry-run
  python3 scripts/cron_governor.py --apply
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone, timedelta
from pathlib import Path

DB_PATH = Path.home() / ".openclaw/state/openclaw.sqlite"
STATE_DIR = Path.home() / ".openclaw/workspace/scripts/.cron_governor"
STATE_DIR.mkdir(parents=True, exist_ok=True)

MIN_TIMEOUT = 900          # agent 任务建议最低超时(s)
RECO_TIMEOUT = 1500        # 建议超时(s)（模型限流缓冲）
WARN_CONSEC_ERR = 2        # 连续错误告警阈值
WARN_ERR_RATE = 0.4        # 14天错误率告警阈值
ORPHAN_HINT = {            # 已知应 disabled 但仍 enabled 的孤儿（job_id 前缀）
    "31080d06": "周度竞争格局报告（已并入周日洞察汇总）",
}

# 轻量探针/自检/学习类任务：timeout 小是刻意设计（快速健康检查），不参与提超时建议
LIGHT_TASKS = {
    "CDP健康探针", "Cookie健康检查", "Ontology图谱自检",
    "知识进化引擎_每周自学习", "tmp清理-每日04:00",
    "Obsidian客流数据同步", "CDP Cookie同步",
}

# 建议的 timeout 上限（业务报告类 agent 任务建议提到 RECO_TIMEOUT，但绝不砍已有更高值）
RECO_TIMEOUT = 1500


def dt(ms: int):
    return datetime.fromtimestamp(ms / 1000).astimezone()


def open_db():
    db = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    return db


def load_jobs(db):
    jobs = {}
    for r in db.execute("SELECT job_id,name,enabled,payload_kind,payload_model,"
                        "payload_timeout_seconds,schedule_expr,schedule_kind,"
                        "delete_after_run "
                        "FROM cron_jobs"):
        jobs[r["job_id"]] = dict(r)
    return jobs


def load_runs(db, days):
    since_ms = (datetime.now(timezone.utc) - timedelta(days=days)).timestamp() * 1000
    runs = defaultdict(list)
    for r in db.execute(
        "SELECT job_id,status,error,run_at_ms,duration_ms "
        "FROM cron_run_logs WHERE run_at_ms >= ?", (int(since_ms),)):
        runs[r["job_id"]].append(dict(r))
    return runs


def classify_error(err: str) -> str:
    e = (err or "")
    el = e.lower()
    if "rate" in el and "limit" in el:
        return "rate_limit"
    if "timeout" in el:
        return "timeout"
    if "exec failed" in el or "exec:" in el:
        return "exec"
    if "failover" in el:
        return "rate_limit"
    if "process" in el:
        return "process"
    if "interrupted" in el:
        return "restart"
    return "other"


def hourly_error_map(runs):
    """近 days 天 error 按小时分布（识别限流高峰）"""
    h = Counter()
    for job_runs in runs.values():
        for r in job_runs:
            if r["status"] == "error":
                h[dt(r["run_at_ms"]).hour] += 1
    return dict(sorted(h.items()))


def build_report(days):
    db = open_db()
    jobs = load_jobs(db)
    runs = load_runs(db, days)
    hourly = hourly_error_map(runs)

    report = {
        "generated_at": datetime.now().astimezone().strftime("%Y-%m-%d %H:%M"),
        "window_days": days,
        "task_count": len(jobs),
        "hourly_errors": hourly,
        "peak_hours": [h for h, c in hourly.items() if c >= 5],
        "daily_records": sum(len(v) for v in runs.values()),
        "tasks": [],
        "recommendations": [],
    }

    for jid, job in jobs.items():
        if not job["enabled"]:
            continue
        jruns = [r for r in runs.get(jid, []) if r["status"] in ("ok", "error")]
        total = len(jruns)
        errs = [r for r in jruns if r["status"] == "error"]
        nerr = len(errs)
        nok = total - nerr

        # 连续错误
        consec = 0
        for r in sorted(runs.get(jid, []), key=lambda x: x["run_at_ms"], reverse=True):
            if r["status"] == "error":
                consec += 1
            else:
                break

        # 错误分类
        err_types = Counter(classify_error(r["error"]) for r in errs)
        # timeout 撞顶计数（duration 接近 timeout）
        timeout_sec = job["payload_timeout_seconds"]
        timeout_hits = sum(
            1 for r in errs if timeout_sec
            and r["duration_ms"] and r["duration_ms"] >= timeout_sec * 1000 * 0.95
        )

        err_rate = nerr / total if total else 0
        avg_dur = int(sum(r["duration_ms"] or 0 for r in jruns) / total) if total else 0

        is_agent = job["payload_kind"] == "agentTurn"
        is_light = job["name"] in LIGHT_TASKS
        is_onetime = bool(job.get("delete_after_run"))
        t = {
            "job_id": jid,
            "name": job["name"],
            "schedule": job["schedule_expr"],
            "kind": job["payload_kind"],
            "timeout": timeout_sec,
            "runs": total,
            "ok": nok,
            "error": nerr,
            "error_rate": round(err_rate, 2),
            "consecutive_errors": consec,
            "avg_duration_ms": avg_dur,
            "error_types": dict(err_types),
            "timeout_hits": timeout_hits,
            "issues": [],
        }

        # 规则引擎：识别问题 + 建议（只读部分）
        if consec >= WARN_CONSEC_ERR:
            t["issues"].append(f"连续{consec}次失败")
            t.setdefault("suggestions", []).append(
                "人工查看：是否是模型限流（若 timeout/rate_limit 类）或是脚本问题（若 exec 类）")
        if err_rate >= WARN_ERR_RATE and total >= 3:
            t["issues"].append(f"近{days}天错误率{err_rate:.0%}")
        if timeout_hits >= 2:
            t["issues"].append(f"{timeout_hits}次撞超时顶")
            t.setdefault("suggestions", []).append(
                f"建议提高 timeout {timeout_sec}→{max(timeout_sec + 300, RECO_TIMEOUT)}")
        if is_agent and not is_light and not is_onetime and \
                (not timeout_sec or timeout_sec < MIN_TIMEOUT):
            t.setdefault("suggestions", []).append(
                f"timeout 偏低或未设 ({timeout_sec})，建议 ≥{MIN_TIMEOUT}")
        if t.get("issues"):
            report["tasks"].append(t)

        # 生成可自动应用的优化（业务 agent 任务才提超时，轻量探针/一次性任务排除）
        if is_agent and not is_light and not is_onetime and \
                (not timeout_sec or timeout_sec < MIN_TIMEOUT):
            report["recommendations"].append({
                "type": "bump_timeout", "job": jid, "name": job["name"],
                "from": timeout_sec, "to": RECO_TIMEOUT,
            })

    # 孤儿任务检测
    for jid, job in jobs.items():
        if job["enabled"] and jid.startswith(tuple(ORPHAN_HINT)):
            report["recommendations"].append({
                "type": "disable_orphan", "job": jid, "name": job["name"],
                "reason": ORPHAN_HINT[next(k for k in ORPHAN_HINT if jid.startswith(k))],
            })

    # 错峰建议（只读，不自动应用）
    peak = report["peak_hours"]
    if peak:
        for t in (x for x in report["tasks"] if x["error_rate"] >= WARN_ERR_RATE):
            from_hour = t["schedule"].split() if t["schedule"] else []
            if from_hour and from_hour[1].lstrip("*/").isdigit():
                h = int(from_hour[1].lstrip("*/"))
                if h in peak:
                    t.setdefault("suggestions", []).append(
                        f"⚠️ 任务时段 {h}:00 撞限流高峰 {peak}，可人工考虑错峰")
    db.close()
    return report


def apply_changes(changes, dry_run):
    """应用安全优化。只处理白名单类：bump_timeout / disable_orphan"""
    applied = []
    db = sqlite3.connect(DB_PATH)
    cur = db.cursor()
    for c in changes:
        if c["type"] == "bump_timeout":
            newto = max(c.get("to", RECO_TIMEOUT), c.get("from") or 0)
            desc = f"提高超时 {c['name']}: {c['from']}→{newto}s"
            if not dry_run:
                cur.execute(
                    "UPDATE cron_jobs SET payload_timeout_seconds=?, updated_at=? "
                    "WHERE job_id=?",
                    (newto, int(datetime.now().timestamp() * 1000), c["job"]))
            applied.append(desc)
        elif c["type"] == "disable_orphan":
            desc = f"禁用孤儿任务 {c['name']}: {c['reason']}"
            if not dry_run:
                cur.execute(
                    "UPDATE cron_jobs SET enabled=0, updated_at=? WHERE job_id=?",
                    (int(datetime.now().timestamp() * 1000), c["job"]))
            applied.append(desc)
    if not dry_run:
        db.commit()
    db.close()
    return applied


def main():
    ap = argparse.ArgumentParser(description="Cron 自进化治理引擎")
    ap.add_argument("--daily", action="store_true")
    ap.add_argument("--weekly", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--days", type=int, default=14)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    days = args.days
    rep = build_report(days)

    if args.apply or args.dry_run:
        applied = apply_changes(rep["recommendations"], args.dry_run)
        rep["applied"] = applied
        rep["mode"] = "dry-run" if args.dry_run else "applied"
        if args.json:
            print(json.dumps(rep, ensure_ascii=False, indent=2))
            return
        print(f"=== Cron 治理 {'预览(dry-run)' if args.dry_run else '已应用'} ===")
        for a in applied:
            print(f"  ✅ {a}")
        if not applied:
            print("  无待应用项")
        return

    # 写状态文件供 cron/LLM 参考
    out = STATE_DIR / f"report_{days}d.json"
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")

    if args.json:
        print(json.dumps(rep, ensure_ascii=False, indent=2))
        return

    peak = "+".join(f"{h}:00" for h in rep["peak_hours"]) or "无"
    print(f"=== Cron 治理报告（近{days}天 {datetime.now().strftime('%m-%d %H:%M')}）===")
    print(f"任务数: {rep['task_count']} | 运行记录: {rep['daily_records']} | 限流高峰: {peak}")
    if not rep["tasks"]:
        print("\n✅ 无异常任务，系统健康")
        return
    print(f"\n⚠️ 异常任务 {len(rep['tasks'])} 个:")
    for t in rep["tasks"]:
        print(f"\n- {t['name']} ({t['job_id'][:8]}) [{t['schedule']}]")
        print(f"   成功率 {t['ok']}/{t['runs']} (err {t['error_rate']:.0%}) 连续err={t['consecutive_errors']} "
              f"均值{t['avg_duration_ms']//1000}s")
        for i in t["issues"]:
            print(f"   ✗ {i}")
        for s in t.get("suggestions", []):
            print(f"   → {s}")
    print(f"\n自动优化建议 {len(rep['recommendations'])} 项:")
    for r in rep["recommendations"]:
        if r["type"] == "bump_timeout":
            print(f"   [timeout] {r['name']}: {r['from']}→{r['to']}s")
        elif r["type"] == "disable_orphan":
            print(f"   [禁用孤儿] {r['name']}: {r['reason']}")
    print(f"\n状态文件: {out}")


if __name__ == "__main__":
    main()
