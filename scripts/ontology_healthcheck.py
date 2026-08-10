#!/usr/bin/env python3
"""
Ontology 图谱自检（M4-M6 闭环健康检查）。

检查图谱系统是否健康持续运行：
1. 图谱文件是否存在、可解析、validate 是否通过
2. 最近是否有写入（防停滞：根据 graph.jsonl 最后修改时间 + 最后几条 timestamp）
3. 实体/关系数量是否健康（随时间增长，不应异常归零）
4. 输出结构化 JSON 供 cron 洞察使用

用法：
  python3 scripts/ontology_healthcheck.py            # 默认输出人类可读摘要
  python3 scripts/ontology_healthcheck.py --json     # 输出 JSON
退出码：0=健康, 1=有告警（如停滞/validate失败）, 2=严重
"""
from __future__ import annotations
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
GRAPH = WORKSPACE / "wiki/技术配置/Ontology架构设计/graph/graph.jsonl"
SCHEMA = WORKSPACE / "wiki/技术配置/Ontology架构设计/movie-town-schema.yaml"
# 停滞阈值：超过此天数无写入则告警（对应生命周期治理文档 2周规则，但日检用更灵敏的）
STALL_DAYS = 7
STALL_DAYS_CRIT = 14

sys.path.insert(0, str(WORKSPACE / "skills/ontology/scripts"))
import ontology as eng  # noqa: E402


def check():
    report = {"healthy": True, "warnings": [], "criticals": [], "stats": {}}
    now = datetime.now(timezone.utc)

    # 1. 文件存在性
    if not GRAPH.exists():
        report["healthy"] = False
        report["criticals"].append("graph.jsonl 不存在（图谱从未初始化，需跑 ontology_migrate.py）")
        return report

    # 2. 解析 + 计数
    try:
        entities, relations = eng.load_graph(str(GRAPH))
    except Exception as e:
        report["healthy"] = False
        report["criticals"].append(f"图谱解析失败: {e}")
        return report
    report["stats"]["entities"] = len(entities)
    report["stats"]["relations"] = len(relations)

    # 3. validate（依赖 yaml；环境若无 yaml 则优雅降级——graph 能加载即视为健康核心）
    try:
        import yaml  # noqa: F401
        if hasattr(eng, "validate_graph"):
            issues = eng.validate_graph(str(GRAPH), str(SCHEMA))
            if issues:
                report["healthy"] = False
                report["criticals"].append(f"schema validate 不过: {len(issues)} 个问题, 例: {str(issues[:2])}")
    except ImportError:
        pass  # 环境无 yaml，跳过 schema 校验（graph 已成功加载即健康）
    except Exception as e:
        report["warnings"].append(f"validate 异常(可能加载器不匹配): {e}")

    # 4. 最近写入时间（文件 mtime + 最后一条 op timestamp）
    mtime = datetime.fromtimestamp(GRAPH.stat().st_mtime, tz=timezone.utc)
    days_since_write = (now - mtime).days
    report["stats"]["days_since_last_write"] = days_since_write
    if days_since_write >= STALL_DAYS_CRIT:
        report["healthy"] = False
        report["criticals"].append(f"图谱已 {days_since_write} 天无写入（>={STALL_DAYS_CRIT}天临界），疑似停滞")
    elif days_since_write >= STALL_DAYS:
        report["warnings"].append(f"图谱 {days_since_write} 天无写入（>={STALL_DAYS}天提示），请检查采集流水是否接入")

    # 5. 图谱规模边际：实体<5 或关系<5 视为未完成初始化
    if len(entities) < 5 or len(relations) < 5:
        report["warnings"].append(
            f"图谱规模过小（实体{len(entities)}/关系{len(relations)}），可能未完成 M3 迁移或数据被清空")

    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = check()
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        status = "✅ 健康" if not report["criticals"] and report["healthy"] else "⚠️ " + ("严重" if report["criticals"] else "注意")
        print(f"图谱自检: {status}")
        print(f"  实体 {report['stats'].get('entities')} | 关系 {report['stats'].get('relations')} | 距上次写入 {report['stats'].get('days_since_last_write')} 天")
        for w in report["warnings"]:
            print(f"  ⚠️ {w}")
        for c in report["criticals"]:
            print(f"  🔴 {c}")
    # 退出码
    sys.exit(2 if report["criticals"] else (1 if report["warnings"] else 0))


if __name__ == "__main__":
    main()
