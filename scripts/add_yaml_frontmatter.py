#!/usr/bin/env python3
"""
add_yaml_frontmatter.py — 给周报/Memory 等 wiki 文件加 Dataview YAML frontmatter

功能：
  1. 给周报文件（W{YY}期-YYYYMMDD.md）加 frontmatter
  2. 给 memory/deep/ 日报加 frontmatter
  3. 写入到文件（不改原内容）

用法：
  python3 add_yaml_frontmatter.py [--dry-run] [--file <path>] [--dir <path>]
"""
import sys, re, os, argparse
from datetime import datetime
from pathlib import Path


# ── 周报 frontmatter ───────────────────────────────────────────────────────
def week_report_frontmatter(path: str) -> dict:
    """从 W23期-20260609.md 这样的文件名提取信息"""
    fname = os.path.basename(path)
    # W23期-20260609.md
    m = re.match(r'W(\d+)期-(\d{4})(\d{2})(\d{2})\.md', fname)
    if not m:
        return {}

    week_num = int(m.group(1))
    year, month, day = int(m.group(2)), int(m.group(3)), int(m.group(4))
    date_str = f"{year}-{month:02d}-{day:02d}"
    # 周范围：取该日期所在的完整周（周一~周日）
    anchor = datetime(year, month, day)
    days_since_sunday = (anchor.weekday() + 1) % 7
    sunday = anchor - __import__('datetime').timedelta(days=days_since_sunday)
    monday = sunday - __import__('datetime').timedelta(days=6)
    week_range = f"{monday.strftime('%Y-%m-%d')} ~ {sunday.strftime('%Y-%m-%d')}"

    return {
        "week": f"W{week_num}",
        "week_num": week_num,
        "report_date": date_str,
        "week_range": week_range,
        "type": "weekly-report",
        "tags": ["周报", "客流洞察"],
        "dataview": "weekly-insights",
    }


# ── Memory deep 日报 frontmatter ─────────────────────────────────────────────
def memory_deep_frontmatter(path: str, content: str = "") -> dict:
    """从 memory/deep/2026-04-19.md 提取"""
    fname = os.path.basename(path)
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})\.md', fname)
    if not m:
        return {}
    date_str = f"{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return {
        "date": date_str,
        "type": "daily-memory",
        "tags": ["日常记录"],
        "dataview": "daily-log",
    }


# ── 知识沉淀文件 frontmatter ────────────────────────────────────────────────
def insight_frontmatter(path: str, content: str = "") -> dict:
    """从路径提取洞察类型"""
    fname = os.path.basename(path)
    if "pattern" in fname.lower():
        return {"type": "pattern-analysis", "tags": ["模式分析"], "dataview": "patterns"}
    if "异常" in fname or "预警" in fname:
        return {"type": "anomaly-alert", "tags": ["异常预警"], "dataview": "alerts"}
    return {}


# ── 写 frontmatter ─────────────────────────────────────────────────────────
def add_frontmatter(path: str, fm: dict) -> str:
    """生成带 YAML frontmatter 的文件内容"""
    lines = []
    lines.append("---")
    for k, v in fm.items():
        if isinstance(v, list):
            lines.append(f"{k}:")
            for item in v:
                lines.append(f"  - {item}")
        else:
            lines.append(f"{k}: {v}")
    lines.append("---")
    lines.append("")  # 空行分隔
    return "\n".join(lines)


def add_yaml_frontmatter(path: Path, dry_run: bool = False) -> bool:
    """处理单个文件，返回是否成功"""
    path = Path(path)
    if not path.exists():
        print(f"  ⚠️ 不存在: {path}", file=sys.stderr)
        return False

    # 识别类型
    fname = path.name
    parent = path.parent.name  # 父目录名
    content = path.read_text(encoding="utf-8") if path.stat().st_size < 100_000 else ""

    if re.match(r'W\d+期-\d{8}\.md', fname):
        fm = week_report_frontmatter(str(path))
    elif parent == "deep" and re.match(r'\d{4}-\d{2}-\d{2}\.md', fname):
        fm = memory_deep_frontmatter(str(path), content)
    else:
        fm = insight_frontmatter(str(path), content)

    if not fm:
        return False  # 不需要处理

    # 检查是否已有 frontmatter
    if content.startswith("---"):
        # 已有 frontmatter，跳过
        print(f"  ⏭️ 已有 frontmatter，跳过: {fname}")
        return True

    new_content = add_frontmatter(str(path), fm) + content

    if dry_run:
        print(f"  🔍 [dry-run] 会写入 frontmatter: {fname}")
        print(new_content[:300])
        print("  ...")
    else:
        path.write_text(new_content, encoding="utf-8")
        print(f"  ✅ 已添加 frontmatter: {fname}")

    return True


def main():
    parser = argparse.ArgumentParser(description="给 wiki 文件加 Dataview YAML frontmatter")
    parser.add_argument("--dry-run", action="store_true", help="只显示不写入")
    parser.add_argument("--file", type=str, help="处理单个文件")
    parser.add_argument("--dir", type=str, help="处理目录下所有 .md 文件")
    args = parser.parse_args()

    wiki_base = Path.home() / ".openclaw" / "workspace" / "wiki"

    if args.file:
        results = [add_yaml_frontmatter(Path(args.file), args.dry_run)]
    elif args.dir:
        base = Path(args.dir)
        files = sorted(base.rglob("*.md"))
        results = [add_yaml_frontmatter(f, args.dry_run) for f in files]
    else:
        # 默认处理：周报 + memory/deep + 知识沉淀
        print("=== 处理周报 ===")
        r1 = [add_yaml_frontmatter(f, args.dry_run) for f in sorted(wiki_base.glob("**/W*期-*.md"))]
        print(f"\n=== 处理 memory/deep 日报 ===")
        r2 = [add_yaml_frontmatter(f, args.dry_run) for f in sorted((wiki_base / "memory" / "deep").glob("*.md"))]
        print(f"\n=== 处理 patterns_knowledge_base ===")
        kb_path = wiki_base / "电影小镇" / "知识沉淀" / "patterns_knowledge_base.json"
        # JSON 文件不需要 frontmatter，跳过
        print("  ⏭️ 跳过 JSON 文件")
        results = r1 + r2
        print(f"\n完成：{sum(results)}/{len(results)} 个文件处理成功")

    return 0


if __name__ == "__main__":
    sys.exit(main())
