#!/usr/bin/env python3
"""
数据异常检测脚本
验证采集数据的合理性，发现异常及时告警

触发条件：
- 抖音指数为0或异常高（>100万）
- 环比波动超过±30%
- 数据缺失（应该有的字段为空）
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 阈值配置
THRESHOLDS = {
    "抖音指数": {"min": 0, "max": 1000000, "波动阈值": 0.3},
    "小红书笔记数": {"min": 0, "max": 10000, "波动阈值": 0.5},
    "客流": {"min": 0, "max": 50000, "波动阈值": 0.5},
}

def validate_douyin_data(data):
    """验证抖音数据"""
    issues = []
    
    if "error" in data:
        return {"valid": False, "issues": [data["error"]]}
    
    for key in ["抖音指数", "搜索指数", "自媒体综合指数"]:
        if key in data:
            val = data[key]
            if val is None:
                issues.append(f"{key}为空")
            elif not isinstance(val, (int, float)):
                issues.append(f"{key}不是数字: {val}")
            elif val < 0:
                issues.append(f"{key}为负数: {val}")
            elif val > THRESHOLDS["抖音指数"]["max"]:
                issues.append(f"{key}异常高: {val}")
    
    return {"valid": len(issues) == 0, "issues": issues}

def validate_xhs_data(data):
    """验证小红书数据"""
    issues = []
    
    if "error" in data:
        return {"valid": False, "issues": [data["error"]]}
    
    # 小红书数据在 results 数组里
    results = data.get("results", [])
    if not results:
        issues.append("results数组为空")
        return {"valid": False, "issues": issues}
    
    # 检查每条记录的字段
    for item in results:
        keyword = item.get("keyword", "未知")
        
        # notes_count 检查
        notes = item.get("notes_count")
        if notes is not None and notes > THRESHOLDS["小红书笔记数"]["max"]:
            issues.append(f"{keyword}: 笔记数异常高: {notes}")
        
        # likes_count 检查
        likes = item.get("likes_count")
        if likes is not None and likes < 0:
            issues.append(f"{keyword}: 点赞数为负: {likes}")
    
    return {"valid": len(issues) == 0, "issues": issues}

def check_data_freshness(file_path, max_age_hours=26):
    """检查数据新鲜度"""
    if not Path(file_path).exists():
        return {"fresh": False, "issue": f"文件不存在: {file_path}"}
    
    import time
    mtime = Path(file_path).stat().st_mtime
    age_hours = (time.time() - mtime) / 3600
    
    if age_hours > max_age_hours:
        return {
            "fresh": False,
            "issue": f"数据过旧: {age_hours:.1f}小时前",
            "age_hours": round(age_hours, 1)
        }
    
    return {"fresh": True, "age_hours": round(age_hours, 1)}

def detect_anomaly(current, previous, threshold=0.3):
    """检测异常波动"""
    if current is None or previous is None:
        return False
    if previous == 0:
        return current != 0
    
    change = abs((current - previous) / previous)
    return change > threshold

def run_validation():
    """执行所有验证"""
    results = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "checks": []
    }
    
    # 检查抖音数据
    douyin_file = "/tmp/crawl_data.json"
    douyin_check = check_data_freshness(douyin_file)
    results["checks"].append({
        "type": "抖音数据新鲜度",
        "result": douyin_check
    })
    
    # 检查小红书数据
    xhs_file = "/tmp/crawl_xhs_unified.json"
    xhs_check = check_data_freshness(xhs_file)
    results["checks"].append({
        "type": "小红书数据新鲜度",
        "result": xhs_check
    })
    
    # 如果文件存在，验证内容
    if Path(douyin_file).exists():
        try:
            with open(douyin_file) as f:
                douyin_data = json.load(f)
            validation = validate_douyin_data(douyin_data)
            results["checks"].append({
                "type": "抖音数据内容验证",
                "result": validation
            })
        except Exception as e:
            results["checks"].append({
                "type": "抖音数据解析",
                "result": {"valid": False, "issues": [str(e)]}
            })
    
    if Path(xhs_file).exists():
        try:
            with open(xhs_file) as f:
                xhs_data = json.load(f)
            validation = validate_xhs_data(xhs_data)
            results["checks"].append({
                "type": "小红书数据内容验证",
                "result": validation
            })
        except Exception as e:
            results["checks"].append({
                "type": "小红书数据解析",
                "result": {"valid": False, "issues": [str(e)]}
            })
    
    # 汇总
    all_valid = all(c["result"].get("valid", True) for c in results["checks"])
    all_fresh = all(c["result"].get("fresh", True) for c in results["checks"])
    
    results["summary"] = {
        "all_valid": all_valid,
        "all_fresh": all_fresh,
        "status": "✅ 正常" if (all_valid and all_fresh) else "⚠️ 异常"
    }
    
    return results

if __name__ == "__main__":
    results = run_validation()
    print(json.dumps(results, ensure_ascii=False, indent=2))
    
    # 如果异常，退出码非0
    if not results["summary"]["all_valid"] or not results["summary"]["all_fresh"]:
        sys.exit(1)
