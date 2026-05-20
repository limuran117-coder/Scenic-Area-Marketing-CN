#!/usr/bin/env python3
"""
代码库漂移检测脚本
检测 scripts/ SOP/ wiki/ 三者之间的不一致
重点关注：脚本已改但知识文档没跟上
用于karpathy-project-wiki漂移检查 cron任务

创建: 2026-05-17（从SOP文档反哺创建）
"""

import json
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw" / "workspace"
SCRIPTS_DIR = WORKSPACE / "scripts"
WIKI_DIR = WORKSPACE / "wiki"
SOP_DIR = WIKI_DIR / "SOP"

def check_script_versions():
    """检查脚本内部版本号与文件名的一致性"""
    drifts = []
    for f in sorted(SCRIPTS_DIR.glob("*.py")):
        content = f.read_text()
        lines = content.split("\n")
        header = "\n".join(lines[:15])  # look in first 15 lines
        
        # Check for version mismatch
        v_match = re.search(r"v(\d+)", f.stem)
        header_match = re.search(r"[Vv](\d+)", header)
        
        if v_match and header_match:
            file_v = int(v_match.group(1))
            header_v = int(header_match.group(1))
            if file_v != header_v:
                drifts.append({
                    "file": f.name,
                    "file_version": file_v,
                    "header_version": header_v,
                    "type": "version_mismatch",
                })
        
        # Check for URL changes vs documented URLs
        url_match = re.findall(r'creator\.douyin\.com/[^\s"\']+', content)
        if url_match:
            documented_urls_file = WIKI_DIR / "技术配置" / "脚本清单.md"
            if documented_urls_file.exists():
                doc_content = documented_urls_file.read_text()
                for url in url_match:
                    if url not in doc_content:
                        drifts.append({
                            "file": f.name,
                            "url": url,
                            "type": "url_changed_not_documented",
                        })
    
    return drifts

def check_sop_vs_scripts():
    """检查SOP引用的脚本文件是否存在"""
    drifts = []
    for sop_file in sorted(SOP_DIR.glob("*.md")):
        content = sop_file.read_text()
        # Find plain script references: standalone xxx.py or xxx.sh
        # Filter out: path references, Chinese text anomalies, markdown links
        refs = re.findall(r'(?<![\w/]) ([a-zA-Z_]\w*\.py)\b', content)
        refs += re.findall(r'(?<![\w/]) ([a-zA-Z_]\w*\.sh)\b', content)
        unique_refs = set(ref.strip() for ref in refs if ref.strip())
        
        # Also check for path-containing references with valid filenames
        path_refs = re.findall(r'scripts/([a-zA-Z_]\w*\.py)', content)
        unique_refs.update(path_refs)
        
        for ref in sorted(unique_refs):
            ref_path = SCRIPTS_DIR / ref
            if not ref_path.exists():
                drifts.append({
                    "sop": sop_file.name,
                    "referenced_script": ref,
                    "type": "broken_script_reference",
                })
    
    return drifts

def check_documented_vs_actual_scripts():
    """检查脚本清单与实际脚本的一致性"""
    inventory_files = [
        WIKI_DIR / "技术配置" / "脚本清单.md",
        WIKI_DIR / "entities" / "scripts" / "README.md",
    ]
    
    actual = sorted(f.name for f in SCRIPTS_DIR.glob("*.py"))
    drifts = []
    
    for inv_file in inventory_files:
        if not inv_file.exists():
            continue
        content = inv_file.read_text()
        # Extract script names mentioned
        mentioned = set(re.findall(r'([\w]+\.py)', content))
        
        actual_set = set(actual)
        missing_from_doc = actual_set - mentioned
        stale_refs = mentioned - actual_set
        
        if missing_from_doc:
            drifts.append({
                "inventory": str(inv_file.relative_to(WORKSPACE)),
                "missing_count": len(missing_from_doc),
                "missing": sorted(missing_from_doc),
                "type": "scripts_not_in_inventory",
            })
        if stale_refs:
            drifts.append({
                "inventory": str(inv_file.relative_to(WORKSPACE)),
                "stale_count": len(stale_refs),
                "stale": sorted(stale_refs),
                "type": "stale_references_in_inventory",
            })
    
    return drifts

def check_raw_unprocessed():
    """检查raw/目录是否有未处理文件"""
    raw_dir = WORKSPACE / "raw"
    if not raw_dir.exists():
        return [{"type": "raw_dir_missing", "detail": "raw/目录已不存在，可能是被清理了"}]
    
    log_file = WIKI_DIR / "log.md"
    if not log_file.exists():
        return [{"type": "log_missing", "detail": "wiki/log.md 不存在，无法判断漂移状态"}]
    
    log_content = log_file.read_text()
    unprocessed = []
    
    for f in sorted(raw_dir.rglob("*")):
        if f.is_file() and not f.name.startswith("."):
            basename = f.name
            if basename not in log_content and str(f.relative_to(raw_dir)).replace("/", "") not in log_content:
                unprocessed.append(str(f.relative_to(WORKSPACE)))
    
    return unprocessed

def generate_report():
    """生成完整的漂移检测报告"""
    report = {
        "timestamp": datetime.now().isoformat(),
        "schema": "2.0",
        "drift_categories": [],
    }
    
    # Category 1: Script version mismatches
    version_drifts = check_script_versions()
    if version_drifts:
        report["drift_categories"].append({
            "category": "脚本版本不一致",
            "severity": "中",
            "items": version_drifts,
        })
    
    # Category 2: SOP references broken scripts
    sop_drifts = check_sop_vs_scripts()
    if sop_drifts:
        report["drift_categories"].append({
            "category": "SOP引用的脚本不存在",
            "severity": "高",
            "items": sop_drifts,
        })
    
    # Category 3: Inventory drift
    inventory_drifts = check_documented_vs_actual_scripts()
    if inventory_drifts:
        report["drift_categories"].append({
            "category": "脚本清单与实际不符",
            "severity": "中",
            "items": inventory_drifts,
        })
    
    # Category 4: Raw unprocessed
    raw_issues = check_raw_unprocessed()
    if raw_issues:
        report["drift_categories"].append({
            "category": "raw/目录状态异常",
            "severity": "低",
            "items": raw_issues,
        })
    
    report["total_drifts"] = sum(len(c["items"]) for c in report["drift_categories"])
    report["status"] = "clean" if report["total_drifts"] == 0 else "has_drifts"
    
    return report

if __name__ == "__main__":
    report = generate_report()
    print(json.dumps(report, ensure_ascii=False, indent=2))
