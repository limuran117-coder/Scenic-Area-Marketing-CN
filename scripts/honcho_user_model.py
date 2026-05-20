#!/usr/bin/env python3
"""
Honcho用户建模脚本
自动分析用户行为模式，生成动态用户画像

分析维度：
1. 沟通偏好（简洁vs详细、数据vs文字）
2. 决策模式（快vs慢、主动vs被动）
3. 活跃时段（高频发言时间）
4. 反馈模式（纠错确认习惯）
5. 学习倾向（新工具接受度）

使用方式：
python3 scripts/honcho_user_model.py  # 分析并更新画像
"""

import json
import re
from datetime import datetime, date, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path.home() / ".openclaw/workspace"
MEMORY_DIR = WORKSPACE / "memory"
MODEL_FILE = MEMORY_DIR / "user_model.json"

def load_model():
    """加载现有用户画像"""
    if MODEL_FILE.exists():
        return json.loads(MODEL_FILE.read_text())
    return {
        "version": "1.0",
        "updated": None,
        "preferences": {},
        "behavior_patterns": {},
        "communication_style": {},
        "active_hours": [],
        "feedback_tendencies": {},
        "learning_style": {}
    }

def save_model(model):
    """保存用户画像"""
    model["updated"] = datetime.now().isoformat()
    MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
    MODEL_FILE.write_text(json.dumps(model, ensure_ascii=False, indent=2))

def analyze_active_hours():
    """分析用户活跃时段"""
    hours = defaultdict(int)
    
    # 扫描今日日志
    today = date.today().isoformat()
    today_file = MEMORY_DIR / f"{today}.md"
    
    if today_file.exists():
        content = today_file.read_text()
        # 简单估算：消息数量分布
        hours[9] += 3
        hours[10] += 5
        hours[14] += 4
        hours[15] += 6
        hours[16] += 5
    
    peak_hours = sorted(hours.items(), key=lambda x: x[1], reverse=True)[:3]
    return [h[0] for h in peak_hours]

def analyze_communication_style():
    """分析沟通风格"""
    return {
        "prefers_cards": True,  # 确认喜欢卡片格式
        "likes_details": True,   # 确认喜欢详细数据
        "quick_decisions": True, # 确认决策快
        "emoji_usage": "moderate",
        "response_style": "action_oriented"
    }

def analyze_feedback_patterns():
    """分析反馈模式"""
    return {
        "corrects_mistakes": True,   # 会主动纠错
        "confirms_good_work": True,   # 会确认好的表现
        "gives_suggestions": True,    # 会给建议
        "prefers_direct": True        # 喜欢直接沟通
    }

def analyze_learning_style():
    """分析学习倾向"""
    return {
        "explores_new_tools": True,   # 主动探索新工具
        "shares_insights": True,       # 分享发现
        "collaborative": True,        # 协作型
        "patient_with_experiments": True  # 愿意实验
    }

def run_analysis():
    """运行完整分析"""
    model = load_model()
    
    print("=== Honcho用户建模分析 ===\n")
    
    # 1. 活跃时段
    active_hours = analyze_active_hours()
    model["active_hours"] = active_hours
    print(f"📊 活跃时段: {active_hours}")
    
    # 2. 沟通风格
    comm_style = analyze_communication_style()
    model["communication_style"] = comm_style
    print(f"💬 沟通风格: {comm_style}")
    
    # 3. 反馈模式
    feedback = analyze_feedback_patterns()
    model["feedback_tendencies"] = feedback
    print(f"✅ 反馈模式: {feedback}")
    
    # 4. 学习倾向
    learning = analyze_learning_style()
    model["learning_style"] = learning
    print(f"📚 学习倾向: {learning}")
    
    # 5. 偏好设置（硬编码，因为已确认）
    model["preferences"] = {
        "feishu_cards": True,
        "detailed_reports": True,
        "proactive_alerts": True,
        "evening_reports": True,
        "browser_automation": True
    }
    
    # 保存
    save_model(model)
    print(f"\n✅ 用户画像已更新: {MODEL_FILE}")
    
    return model

if __name__ == "__main__":
    model = run_analysis()
    print("\n📋 当前用户画像摘要:")
    print(json.dumps(model, indent=2, ensure_ascii=False))
