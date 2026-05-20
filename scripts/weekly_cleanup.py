#!/usr/bin/env python3
"""
周度清理脚本 - 清理workspace下的无用文件
"""
import os
import shutil
from pathlib import Path

WORKSPACE = Path("/Users/tianjinzhan/.openclaw/workspace")

def find_useless_files():
    """找出可以清理的无用文件"""
    useless = []
    
    # 1. 空的 .md 文件（只有标题没有内容）
    for md in WORKSPACE.rglob("*.md"):
        if md.name.startswith("Untitled"):
            try:
                if md.stat().st_size == 0:
                    useless.append(("空文件", md))
            except:
                pass
    
    # 2. 临时文件
    temp_patterns = ["*.tmp", "*.bak", "*~", ".DS_Store"]
    for pat in temp_patterns:
        for f in WORKSPACE.rglob(pat):
            useless.append(("临时文件", f))
    
    # 3. 404 stub 文件（空或只有标题）
    for md in WORKSPACE.rglob("*.md"):
        if "404" in md.name or "stub" in md.name.lower():
            try:
                content = md.read_text(errors="ignore")
                if len(content) < 100:
                    useless.append(("stub文件", md))
            except:
                pass
    
    # 4. 分离的日期文件夹（只有一个文件且无用）
    for d in WORKSPACE.iterdir():
        if d.is_dir() and d.name.startswith("0"):
            files = list(d.rglob("*"))
            if len(files) == 0:
                useless.append(("空目录", d))
    
    return useless

def cleanup(files):
    """删除文件"""
    deleted = []
    for kind, path in files:
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            deleted.append((kind, str(path)))
        except Exception as e:
            print(f"  删除失败: {path} - {e}")
    return deleted

def main():
    print("## 周度清理 | workspace无用文件检查")
    
    useless = find_useless_files()
    
    if not useless:
        print("✅ 未发现需要清理的文件")
        return
    
    print(f"⚠️ 发现 {len(useless)} 个可清理项:")
    for kind, path in useless:
        print(f"  - [{kind}] {path}")
    
    # 预览模式：只报告不删除
    print("\n（预览模式，只报告不删除）")
    print(f"如需执行删除，去掉脚本里的注释")

if __name__ == "__main__":
    main()
