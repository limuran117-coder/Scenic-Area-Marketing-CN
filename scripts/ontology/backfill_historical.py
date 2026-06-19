"""
回填历史 JSON 数据到 SQLite Ontology Store
对标 Phase 1 启动期：把现有 wiki/技术配置/Ontology架构设计/data/ 中的 JSON
全部导入 .profile/ontology/ontology_store.db

执行：python scripts/ontology/backfill_historical.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# 路径：scripts/ontology/ 上两级是 workspace
WORKSPACE = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(WORKSPACE / "scripts" / "ontology"))

from ontology_store import OntologyStore  # noqa: E402

DATA_DIR = WORKSPACE / "wiki" / "技术配置" / "Ontology架构设计" / "data"


def list_json_files() -> list[Path]:
    """列出 data/ 下所有 JSON"""
    if not DATA_DIR.exists():
        return []
    return sorted(DATA_DIR.glob("*.json"))


def backfill():
    store = OntologyStore()
    if not store.db_path.exists():
        store.initialize()
        print("✅ initialized store")

    files = list_json_files()
    print(f"📂 找到 {len(files)} 个 JSON 文件")
    if not files:
        print("⚠️ 没有 JSON 文件可回填")
        return

    total_added = 0
    total_updated = 0
    failed = 0

    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"  ❌ {f.name}: JSON parse failed: {e}")
            failed += 1
            continue

        schema = data.get("objectType")
        objects = data.get("objects", [])
        if not schema or not objects:
            print(f"  ⚠️ {f.name}: empty schema or objects, skip")
            continue

        # adapter_name 从 sourceAdapter 字段提取
        adapter = data.get("sourceAdapter", "backfill")

        result = store.ingest_objects(
            adapter_name=adapter,
            schema=schema,
            objects=objects,
            source_file=str(f),
        )

        status_icon = "✅" if result.status == "success" else "❌"
        print(
            f"  {status_icon} {f.name} ({schema}): "
            f"+{result.records_added} ~{result.records_updated} "
            f"status={result.status}"
        )

        total_added += result.records_added
        total_updated += result.records_updated
        if result.status == "failed":
            failed += 1

    print()
    print(f"📊 回填完成: +{total_added} (新增) / ~{total_updated} (更新) / {failed} 失败")
    print()
    print("📈 当前统计:")
    for k, v in store.stats().items():
        if v > 0:
            print(f"  {k}: {v}")


if __name__ == "__main__":
    backfill()
