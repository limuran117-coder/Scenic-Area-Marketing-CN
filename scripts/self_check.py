#!/usr/bin/env python3
"""
自检脚本 - 任务完成后自动评估打分
触发：每次isolated任务完成后，由cron/agent调用

评估维度：
1. 内容完整度 - 数据是否齐全，有无遗漏字段
2. 数据准确度 - 与已知数据的偏差
3. 格式正确度 - 飞书卡片是否合规
4. 时效性 - 是否在合理时间内完成

输出：
- score.json - 本次评分
- skill_score.json - 各Skill历史评分（用于self-improvement）
- auto_feedback.json - 捕捉到的问题（无需用户反馈）
"""

import json
import sys
import os
from datetime import datetime, date
from pathlib import Path

MEMORY_DIR = Path.home() / ".openclaw/workspace/memory/topics/feedback"
SKILL_SCORE_FILE = MEMORY_DIR / "skill_scores.json"
AUTO_FEEDBACK_FILE = MEMORY_DIR / "auto_feedback.json"

TASK_TYPES = {
    "douyin": {
        "name": "抖音指数日报",
        "expected_fields": ["search", "synth", "trends", "competitors"],
        "min_data_points": 8
    },
    "xiaohongshu": {
        "name": "小红书日报",
        "expected_fields": ["notes", "likes", "engagement"],
        "min_data_points": 5
    },
    "competitor": {
        "name": "竞品分析",
        "expected_fields": ["name", "search", "synth", "trend"],
        "min_data_points": 6
    },
    "passenger": {
        "name": "客流分析",
        "expected_fields": ["date", "passengers", "revenue", "target_gap"],
        "min_data_points": 1
    }
}

def load_json(path, default):
    """加载JSON文件，不存在则返回默认值"""
    if path.exists():
        return json.loads(path.read_text())
    return default

def save_json(path, data):
    """保存JSON文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def calculate_completeness(task_type, data):
    """计算内容完整度"""
    if task_type not in TASK_TYPES:
        return 0.5
    
    expected = TASK_TYPES[task_type]["expected_fields"]
    found = sum(1 for f in expected if f in data and data[f] is not None)
    return found / len(expected) if expected else 0

def calculate_accuracy(task_type, data):
    """计算数据准确度（与历史数据偏差）"""
    # 简化版：检查数据是否在合理范围内
    if task_type == "douyin":
        # 搜索指数合理范围：0 ~ 500万
        search = data.get("search", 0)
        if 0 <= search <= 5000000:
            return 1.0
        return 0.0
    
    if task_type == "passenger":
        # 单日客流合理范围：0 ~ 5万
        passengers = data.get("passengers", 0)
        if 0 <= passengers <= 50000:
            return 1.0
        return 0.0
    
    return 0.8  # 默认

def calculate_format_score(card_valid, table_format):
    """计算格式正确度"""
    score = 0.0
    if card_valid:
        score += 0.5
    if table_format:
        score += 0.5
    return score

def update_skill_score(skill_name, score_delta):
    """更新Skill评分（用于self-improvement）"""
    scores = load_json(SKILL_SCORE_FILE, {})
    
    if skill_name not in scores:
        scores[skill_name] = {"total": 0, "count": 0, "history": []}
    
    scores[skill_name]["total"] += score_delta
    scores[skill_name]["count"] += 1
    
    # 保留最近20次记录
    scores[skill_name]["history"].append({
        "score": score_delta,
        "timestamp": datetime.now().isoformat()
    })
    scores[skill_name]["history"] = scores[skill_name]["history"][-20:]
    
    save_json(SKILL_SCORE_FILE, scores)
    return scores[skill_name]

def record_auto_feedback(task_type, score, issues, suggestions):
    """记录自动捕捉的反馈"""
    feedback = load_json(AUTO_FEEDBACK_FILE, [])
    
    feedback.append({
        "type": "auto",
        "task_type": task_type,
        "score": score,
        "issues": issues,
        "suggestions": suggestions,
        "timestamp": datetime.now().isoformat(),
        "date": date.today().isoformat()
    })
    
    # 只保留最近100条
    feedback = feedback[-100:]
    
    save_json(AUTO_FEEDBACK_FILE, feedback)
    return feedback

def self_check(task_type, data, card_valid=True, table_format=True):
    """
    主自检函数
    
    Args:
        task_type: 任务类型 (douyin/xiaohongshu/competitor/passenger)
        data: 任务数据字典
        card_valid: 飞书卡片是否有效
        table_format: 表格格式是否正确
    
    Returns:
        dict: 评分结果和建议
    """
    completeness = calculate_completeness(task_type, data)
    accuracy = calculate_accuracy(task_type, data)
    format_score = calculate_format_score(card_valid, table_format)
    
    # 综合评分（权重：完整度40%，准确度40%，格式20%）
    total_score = completeness * 0.4 + accuracy * 0.4 + format_score * 0.2
    
    issues = []
    suggestions = []
    
    if completeness < 1.0:
        issues.append(f"内容完整度不足: {completeness:.0%}")
        suggestions.append("补充缺失字段")
    
    if accuracy < 1.0:
        issues.append(f"数据准确度存疑: {accuracy:.0%}")
        suggestions.append("核实数据来源")
    
    if not card_valid:
        issues.append("飞书卡片格式错误")
        suggestions.append("检查schema 2.0格式")
    
    if not table_format:
        issues.append("表格格式错误")
        suggestions.append("使用columns:[字符串]格式")
    
    # 更新Skill评分
    skill_name = TASK_TYPES.get(task_type, {}).get("name", task_type)
    update_skill_score(skill_name, total_score)
    
    # 记录自动反馈
    if issues:
        record_auto_feedback(task_type, total_score, issues, suggestions)
    
    return {
        "task_type": task_type,
        "scores": {
            "completeness": completeness,
            "accuracy": accuracy,
            "format": format_score,
            "total": total_score
        },
        "issues": issues,
        "suggestions": suggestions,
        "timestamp": datetime.now().isoformat()
    }

def main():
    """命令行调用"""
    if len(sys.argv) < 3:
        print("Usage: self_check.py <task_type> <json_data>")
        print("Example: self_check.py douyin '{\"search\": 4414, \"synth\": 1782}'")
        sys.exit(1)
    
    task_type = sys.argv[1]
    data = json.loads(sys.argv[2])
    
    result = self_check(task_type, data)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 输出建议（供agent读取）
    if result["suggestions"]:
        print("\n💡 改进建议:")
        for s in result["suggestions"]:
            print(f"  - {s}")

if __name__ == "__main__":
    main()
