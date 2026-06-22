#!/opt/homebrew/bin/python3.12
"""
爆款案例归档脚本（2026-06-22 W26 新增，方案 A #5）
- 接收集成爆款拆解结果，自动写入 wiki/全国景区案例库/
- 命名规范：<景区或品牌>-<主题>-<ISO 周号>.md
- 头部固定格式（与现有 W24 案例对齐）

用法:
  python3 scripts/archive_case.py --title "万岁山主客共创" \\
    --date 2026-06-22 --source "腾讯新闻" --action "即兴互动节目" \\
    --data "2025春节7天72万人次" --tags "#情景剧 #互动挑战" \\
    --body-file /tmp/case_body.md
"""
import argparse
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path("/Users/tianjinzhan/.openclaw/workspace")
CASE_DIR = ROOT / "wiki" / "全国景区案例库"
INDEX_FILE = CASE_DIR / "index.md"


def get_iso_week(date_str: str) -> str:
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    iso = dt.isocalendar()
    return f"{iso[0]}W{iso[1]:02d}"


def sanitize_title(title: str) -> str:
    safe = re.sub(r'[\s\\/:*?"<>|]+', '-', title)
    return safe.strip('-')


def build_template(title, date, source, action, data, tags, body):
    week = get_iso_week(date)
    return f"""# {title}

## 案例概述
- **来源：** {source}
- **核心动作：** {action}
- **关键数据：** {data}
- **发现日期：** {date}（{week}）
- **标签：** {tags}

---

{body}

---

## 元数据（自动生成）
- **归档工具：** `scripts/archive_case.py`
- **Week：** {week}
"""


def update_index(title, date, tags, filename):
    if not INDEX_FILE.exists():
        return
    content = INDEX_FILE.read_text(encoding="utf-8")
    week = get_iso_week(date)
    section_header = f"## 第{week[4:]}周新增"
    new_row = f"| {title} | 见文件 | 见文件 | {tags} | [[{filename[:-3]}]] |\n"
    if section_header not in content:
        appendix = f"\n\n{section_header}（{date} 实时归档）\n\n| 案例名 | 来源 | 数据 | 标签 | 详情 |\n|--------|------|------|------|------|\n{new_row}"
        INDEX_FILE.write_text(content + appendix, encoding="utf-8")
    else:
        idx = content.find(section_header)
        section_end = content.find("\n## ", idx + 1)
        if section_end < 0:
            section_end = len(content)
        content = content[:section_end] + new_row + content[section_end:]
        INDEX_FILE.write_text(content, encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--title", required=True)
    parser.add_argument("--date", required=True)
    parser.add_argument("--source", required=True)
    parser.add_argument("--action", required=True)
    parser.add_argument("--data", required=True)
    parser.add_argument("--tags", default="#爆款")
    parser.add_argument("--body-file")
    parser.add_argument("--no-index", action="store_true")
    args = parser.parse_args()

    if args.body_file:
        body = Path(args.body_file).read_text(encoding="utf-8")
    elif not sys.stdin.isatty():
        body = sys.stdin.read()
    else:
        body = "\n## 案例详情\n待补充。\n"

    week = get_iso_week(args.date)
    safe_title = sanitize_title(args.title)
    filename = f"{safe_title}-{week}.md"
    fpath = CASE_DIR / filename

    if fpath.exists():
        print(f"⚠️ 文件已存在（不覆盖）: {fpath}")
        sys.exit(0)

    content = build_template(args.title, args.date, args.source, args.action, args.data, args.tags, body)
    fpath.write_text(content, encoding="utf-8")
    print(f"✅ 已写入: {fpath} ({len(content)} 字节)")

    if not args.no_index:
        try:
            update_index(args.title, args.date, args.tags, filename)
            print(f"✅ index.md 已追加")
        except Exception as e:
            print(f"⚠️ index.md 更新失败: {e}")


if __name__ == "__main__":
    main()