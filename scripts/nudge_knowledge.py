#!/usr/bin/env python3
"""
Nudge Knowledge - 任务结束前主动检查"我学到了什么"
嵌入在每个cron任务的结束流程中

触发方式：
1. 任务完成前自动调用
2. 单独运行做知识整理

检查维度：
1. 新学到的事实（竞品动态/平台规则/用户偏好）
2. 验证的假设（之前预测对了吗？）
3. 踩过的坑（哪里摔过跤？）
4. 可复用的模式（这次做得好的能复用吗？）
"""

import json
import re
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw/workspace"
MEMORY_DIR = WORKSPACE / "memory"
TODAY_FILE = MEMORY_DIR / f"{date.today().isoformat()}.md"

# 关键模式 - 识别这些内容时触发记录
PATTERNS = {
    # 用户偏好相关
    r"喜欢|偏好|要|不要|停止|不对": "user_preference",
    # 竞品动态
    r"清明上河园|万岁山|银基|方特|只有河南": "competitor_update",
    # 平台规则
    r"抖音|小红书|飞书|规则|格式": "platform_rule",
    # 预测验证
    r"预测|应该|可能|估计|涨|跌": "prediction",
    # 错误教训
    r"糗了|不对|失败|错误|问题": "lesson_learned",
    # 成功模式
    r"成功|有效|对了|很好|涨了": "success_pattern",
}

def check_current_context():
    """
    检查当前上下文是否有值得记录的新知识
    从今日记忆文件中分析
    """
    if not TODAY_FILE.exists():
        return None
    
    content = TODAY_FILE.read_text()
    
    findings = {
        "user_preference": [],
        "competitor_update": [],
        "platform_rule": [],
        "prediction": [],
        "lesson_learned": [],
        "success_pattern": []
    }
    
    lines = content.split("\n")
    
    for line in lines:
        for pattern, category in PATTERNS.items():
            if re.search(pattern, line):
                findings[category].append(line.strip())
    
    # 去重
    for k in findings:
        findings[k] = list(set(findings[k]))[:5]  # 最多保留5条
    
    return findings

def generate_knowledge_checklist(findings):
    """
    生成知识检查清单
    """
    if not findings:
        return "今日无新增知识记录"
    
    lines = ["## 📝 今日知识沉淀检查\n"]
    
    categories = [
        ("user_preference", "👤 用户偏好"),
        ("competitor_update", "🏢 竞品动态"),
        ("platform_rule", "📋 平台规则"),
        ("prediction", "🔮 预测验证"),
        ("lesson_learned", "💡 踩坑教训"),
        ("success_pattern", "✅ 成功模式")
    ]
    
    has_content = False
    for key, label in categories:
        items = findings.get(key, [])
        if items:
            has_content = True
            lines.append(f"\n### {label}\n")
            for item in items[:3]:
                lines.append(f"- [ ] {item}")
    
    if not has_content:
        return "✅ 今日无明显遗漏"
    
    return "\n".join(lines)

def ask_to_remember():
    """
    生成"要记住吗"的提醒
    """
    findings = check_current_context()
    
    if not findings:
        return None
    
    # 统计各类别数量
    counts = {k: len(v) for k, v in findings.items() if v}
    
    if not counts:
        return None
    
    total = sum(counts.values())
    
    message = f"今日发现 {total} 条潜在新知识：\n"
    for k, v in counts.items():
        message += f"- {k}: {v}条\n"
    
    message += "\n是否需要我整理沉淀到记忆系统？"
    
    return message

def main():
    """命令行调用"""
    print("🔍 知识沉淀检查...")
    
    findings = check_current_context()
    
    if findings:
        print("\n📊 发现内容：")
        for k, v in findings.items():
            if v:
                print(f"  {k}: {len(v)}条")
    
    checklist = generate_knowledge_checklist(findings)
    print("\n" + checklist)
    
    reminder = ask_to_remember()
    if reminder:
        print("\n" + "="*50)
        print(reminder)
        print("="*50)

if __name__ == "__main__":
    main()
