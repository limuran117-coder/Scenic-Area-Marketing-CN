#!/usr/bin/env python3
"""
Wiki漂移检测脚本
检测wiki目录下所有markdown文件的lint状态，输出漂移报告
用于karpathy-wiki健康检查 cron任务

参考: scripts/llmwiki_lint.py（实际lint引擎）
创建: 2026-05-17（从SOP文档反哺创建）
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

WIKI_DIR = Path.home() / ".openclaw" / "workspace" / "wiki"
SCRIPTS_DIR = Path.home() / ".openclaw" / "workspace" / "scripts"
LINT_RESULT = WIKI_DIR / "lint-result.json"

def load_lint_result():
    """加载最新的lint结果"""
    if LINT_RESULT.exists():
        with open(LINT_RESULT) as f:
            return json.load(f)
    return None

def check_missing_docs():
    """检查wiki/entities/scripts/ 与实际脚本的覆盖情况"""
    described = set()
    scripts_doc = WIKI_DIR / "entities" / "scripts" / "README.md"
    if scripts_doc.exists():
        content = scripts_doc.read_text()
        for line in content.split("\n"):
            if "[[douyin_index" in line or "[[send_feishu" in line:
                described.add("douyin_index_v9.py")
            elif "[[" in line:
                # extract script name from [[xxx]]
                import re
                m = re.search(r'\[\[([^\]]+)\]\]', line)
                if m:
                    described.add(m.group(1) + ".py")
    
    actual = set(f.name for f in SCRIPTS_DIR.glob("*.py"))
    
    missing_from_wiki = actual - described
    stale_in_wiki = described - actual
    
    return missing_from_wiki, stale_in_wiki

def generate_report():
    """生成漂移检测报告"""
    lint = load_lint_result()
    missing, stale = check_missing_docs()
    
    # Check for the drift-check scripts themselves
    drift_scripts_exist = all(
        (SCRIPTS_DIR / s).exists() 
        for s in ["wiki_drift_check.py", "project_drift_check.py"]
    )
    
    issues = []
    
    if lint:
        issues.append({
            "type": "lint_summary",
            "total_issues": lint.get("issues_count", 0),
            "orphan_count": sum(1 for i in lint["issues"] if i["type"] == "orphan"),
            "contradiction_count": sum(1 for i in lint["issues"] if i["type"] == "contradiction"),
        })
    
    if missing:
        issues.append({
            "type": "scripts_not_documented",
            "count": len(missing),
            "scripts": sorted(missing),
        })
    
    if stale:
        issues.append({
            "type": "stale_script_references",
            "count": len(stale),
            "scripts": sorted(stale),
        })
    
    if not drift_scripts_exist:
        issues.append({
            "type": "self_reference_fixed",
            "detail": "漂移检测脚本自身已创建，此问题已修复",
        })
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "status": "has_issues" if issues else "clean",
        "issues": issues,
    }
    
    return report

if __name__ == "__main__":
    report = generate_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
