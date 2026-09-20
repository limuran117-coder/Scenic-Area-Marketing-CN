#!/usr/bin/env python3
"""wiki_rev.py — wiki 修订/回滚最小工具（页级 diff + 一键回退）

背景：workspace 根即 Obsidian vault，`wiki/` 已在 git 跟踪，但改动大量淹没在
Obsidian Git 插件的批量自动提交（"vault backup: <时间>"）里 —— 版本存在，
却无法按文件定位"哪次任务改了什么"，也没有回退程序。本脚本只补这两件事。

用法:
  wiki_rev.py mark <label>              写前锚点：把当前 wiki 状态固化为可回退点
  wiki_rev.py save <label>              写后固化：提交本次改动并附语义消息
  wiki_rev.py log <file> [-n N]         只看该文件的有效提交（过滤 vault backup 噪音）
  wiki_rev.py rollback <file> [--to REF] [--yes]
                                        单文件回退；默认丢弃未提交改动（即"刚写坏了，退回去"）
                                        --to REF 从指定提交恢复该文件
  wiki_rev.py guard <file>              写前守卫：该文件若有未提交改动则警告（防覆盖他人改动）
  wiki_rev.py status                    高危文件未提交改动概览

安全约束（硬性）:
  - rollback 默认 dry-run（只显示 diff），必须 --yes 才真正恢复
  - 只回滚指定文件，绝不 git reset --hard / git clean
  - 恢复前自动备份原内容到 /tmp/wiki_rev_backup/

退出码: 0 成功 / 1 参数或仓库错误 / 2 需要 --yes 确认 / 3 无改动
"""
import argparse
import os
import shutil
import subprocess
import sys
from datetime import datetime

# ---- 并发追加类高危文件（多任务写同一文件，最容易锚点漂移 / 相互覆盖）----
HIGH_RISK = [
    "wiki/行业知识/结论索引.md",
    "wiki/电影小镇/营销归因日志.md",
    "wiki/电影小镇/历史数据/index.md",
    "wiki/技术配置/GitHub高星标学习笔记.md",
    "MEMORY.md",
]

BACKUP_DIR = "/tmp/wiki_rev_backup"
NOISE_PREFIXES = ("vault backup", "vault-backup")


# 本工具是 vault 级修订层：workspace 根即 Obsidian vault，
# 固化范围与 Obsidian Git 的 vault backup 一致（全仓，受 .gitignore 约束）。
STAGE = ["-A", "."]


def stage_all(root):
    git("add", *STAGE, cwd=root, check=False)


def repo_root() -> str:
    here = os.path.dirname(os.path.abspath(__file__))
    out = subprocess.run(
        ["git", *GIT_BASE, "rev-parse", "--show-toplevel"],
        cwd=here, capture_output=True, text=True,
    )
    if out.returncode != 0:
        die("不在 git 仓库内；本工具依赖 workspace 的 git 修订历史。")
    return out.stdout.strip()


# 必须关掉 quotepath，否则中文路径被转义成八进制，guard/rollback 会匹配不到文件
GIT_BASE = ["-c", "core.quotepath=false"]


def git(*args, cwd=None, check=True):
    out = subprocess.run(["git", *GIT_BASE, *args], cwd=cwd, capture_output=True, text=True)
    if check and out.returncode != 0:
        msg = (out.stderr or out.stdout).strip()
        die(f"git {' '.join(args)} 失败:\n{msg}")
    return out


def die(msg: str, code: int = 1):
    print(f"❌ {msg}", file=sys.stderr)
    sys.exit(code)


def rel(path: str, root: str) -> str:
    """把用户给的路径规范化成仓库相对路径。"""
    p = os.path.abspath(path) if not os.path.isabs(path) else path
    if not p.startswith(root):
        p = os.path.join(root, path.lstrip("/"))
    return os.path.relpath(p, root)


def dirty_paths(root: str):
    out = git("status", "--porcelain", cwd=root)
    files = []
    for line in out.stdout.splitlines():
        if len(line) > 3:
            files.append(line[3:].strip().strip('"'))
    return files


def cmd_mark(args, root):
    """写前锚点：把*当前*状态固化。若本来就有未提交改动，一并固化 —— 这正是可回退点的定义。"""
    files = dirty_paths(root)
    label = f"锚点 {args.label}" if args.label else "锚点"
    stage_all(root)
    if not files:
        print(f"ℹ️  工作区已干净，无需锚点（HEAD = {git('rev-parse', '--short', 'HEAD', cwd=root).stdout.strip()}）")
        sys.exit(3)
    msg = f"{label}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    git("commit", "-m", msg, "--no-verify", cwd=root)
    sha = git("rev-parse", "--short", "HEAD", cwd=root).stdout.strip()
    print(f"✅ 锚点已建 {sha} — {msg}")
    print(f"   含 {len(files)} 个文件改动（回退到此处 = `wiki_rev.py rollback <file> --to {sha}`）")


def cmd_save(args, root):
    """写后固化：语义化提交，让该文件的改动可被单独定位。"""
    files = dirty_paths(root)
    if not files:
        print("ℹ️  无未提交改动，跳过。")
        sys.exit(3)
    git("add", "-A", ".", cwd=root, check=False)
    msg = args.label or f"wiki 修订: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    git("commit", "-m", msg, "--no-verify", cwd=root)
    sha = git("rev-parse", "--short", "HEAD", cwd=root).stdout.strip()
    print(f"✅ 已固化 {sha} — {msg}")
    for f in files[:10]:
        print(f"   · {f}")


def cmd_log(args, root):
    f = rel(args.file, root)
    n = args.number
    out = git("log", "--pretty=%h|%ad|%s", "--date=format:%m-%d %H:%M",
              "-n", str(n * 4), "--", f, cwd=root)
    rows = [l for l in out.stdout.splitlines() if "|" in l]
    meaningful = [r for r in rows if not r.split("|", 2)[2].strip().lower().startswith(NOISE_PREFIXES)]
    print(f"=== {f} 有效提交（已滤除 vault backup 噪音）===")
    if not meaningful:
        print("  ⚠️  无任务级提交 —— 该文件的全部改动都埋在自动备份里，无法按提交定位。")
    for r in meaningful[:n]:
        sha, when, subj = r.split("|", 2)
        print(f"  {sha}  {when}  {subj}")
    noise = len(rows) - len(meaningful)
    if noise:
        print(f"  （另滤除 {noise} 条 vault backup）")


def cmd_guard(args, root):
    f = rel(args.file, root)
    dirty = dirty_paths(root)
    if f in dirty:
        print(f"⚠️  {f} 有未提交改动 —— 直接写入会覆盖掉它。")
        print(f"   先保存：`wiki_rev.py save \"<说明>\"`，或看 diff：`git diff -- {f}`")
        sys.exit(2)
    print(f"✅ {f} 无未提交改动，可安全写入。")


def cmd_status(args, root):
    dirty = set(dirty_paths(root))
    print("=== 高危文件未提交改动 ===")
    hit = False
    for f in HIGH_RISK:
        if f in dirty:
            hit = True
            print(f"  🔴 {f}")
    if not hit:
        print("  ✅ 全部干净")
    print(f"\n=== 工作区未提交改动 {len(dirty)} 项 ===")
    for f in sorted(dirty)[:15]:
        print(f"  · {f}")


def cmd_rollback(args, root):
    f = rel(args.file, root)
    if not os.path.exists(os.path.join(root, f)):
        # 仍允许：可能是恢复到"文件被删除前"的版本
        print(f"⚠️  {f} 当前不存在，将从历史恢复。")

    ref = args.to
    if ref:
        diff = git("diff", f"{ref}..HEAD", "--", f, cwd=root, check=False)
        head = git("rev-parse", "--short", ref, cwd=root, check=False).stdout.strip()
        print(f"=== 将 {f} 恢复到 {head}（{ref}）===")
    else:
        diff = git("diff", "--", f, cwd=root, check=False)
        print(f"=== 将丢弃 {f} 的未提交改动（恢复到 HEAD）===")

    body = diff.stdout.strip()
    if not body:
        print("ℹ️  无差异，无需回滚。")
        sys.exit(3)

    # 截断展示，避免刷屏
    lines = body.splitlines()
    print("\n".join(lines[:120]))
    if len(lines) > 120:
        print(f"... （diff 共 {len(lines)} 行，已截断）")

    if not args.yes:
        print(f"\n⚠️  这是预览。确认执行请追加 --yes")
        sys.exit(2)

    # 备份当前内容
    os.makedirs(BACKUP_DIR, exist_ok=True)
    src = os.path.join(root, f)
    if os.path.exists(src):
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        dst = os.path.join(BACKUP_DIR, f"{stamp}__{os.path.basename(f)}")
        shutil.copy2(src, dst)
        print(f"💾 已备份当前内容 → {dst}")

    if ref:
        git("checkout", ref, "--", f, cwd=root)
    else:
        git("checkout", "--", f, cwd=root)
    print(f"✅ 已回滚 {f}")
    print(f"   如需撤回本次回滚：`cp '{os.path.join(BACKUP_DIR, dst) if os.path.exists(src) else ''}' {f}`")


def main():
    ap = argparse.ArgumentParser(prog="wiki_rev.py", description="wiki 修订/回滚最小工具")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("mark", help="写前锚点"); p.add_argument("label", nargs="?", default="")
    p = sub.add_parser("save", help="写后固化"); p.add_argument("label", nargs="?", default="")
    p = sub.add_parser("log", help="看单文件有效提交"); p.add_argument("file"); p.add_argument("-n", "--number", type=int, default=8)
    p = sub.add_parser("guard", help="写前守卫"); p.add_argument("file")
    sub.add_parser("status", help="高危文件概览")
    p = sub.add_parser("rollback", help="单文件回退")
    p.add_argument("file"); p.add_argument("--to", default=None); p.add_argument("--yes", action="store_true")

    args = ap.parse_args()
    root = repo_root()
    {"mark": cmd_mark, "save": cmd_save, "log": cmd_log,
     "guard": cmd_guard, "status": cmd_status, "rollback": cmd_rollback}[args.cmd](args, root)


if __name__ == "__main__":
    main()
