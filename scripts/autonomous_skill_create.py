#!/usr/bin/env python3
"""
Autonomous Skill Creation 脚本
自动发现重复成功任务，生成Skill模板

触发条件：
1. 同一类型任务连续成功3次
2. 用户说"把这个做成模板"
3. 复盘Agent检测到可复用工作流

工作流程：
1. 扫描任务日志
2. 识别成功模式
3. 生成Skill文件
4. 更新skill_scores.json
"""

import json
import re
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw/workspace"
SKILLS_DIR = WORKSPACE / "skills"
SKILL_SCORES = WORKSPACE / "memory/topics/feedback/skill_scores.json"
AUTO_CREATED = WORKSPACE / "memory/topics/feedback/auto_created_skills.json"

def load_skill_scores():
    """加载Skill评分"""
    if SKILL_SCORES.exists():
        return json.loads(SKILL_SCORES.read_text())
    return {}

def save_auto_created(skills):
    """保存自动创建的Skill记录"""
    AUTO_CREATED.parent.mkdir(parents=True, exist_ok=True)
    AUTO_CREATED.write_text(json.dumps(skills, ensure_ascii=False, indent=2))

def check_skill_candidates():
    """检查是否有资格自动创建Skill"""
    scores = load_skill_scores()
    candidates = []
    
    for skill_name, data in scores.items():
        history = data.get("history", [])
        if len(history) >= 3:
            # 检查最近3次是否都高分
            recent = history[-3:]
            if all(h["score"] >= 0.8 for h in recent):
                avg_score = sum(h["score"] for h in recent) / 3
                candidates.append({
                    "skill_name": skill_name,
                    "recent_scores": recent,
                    "avg_score": avg_score,
                    "success_count": len([h for h in history if h["score"] >= 0.8])
                })
    
    return candidates

def generate_skill_content(skill_name, avg_score):
    """生成Skill文件内容"""
    template = f"""# {skill_name}

> 自动生成 | 信心度: {avg_score:.0%} | 生成时间: {datetime.now().strftime('%Y-%m-%d')}

## 概述
本Skill基于连续成功经验自动生成，用于{skill_name}任务的标准化执行。

## 适用场景
- {skill_name}相关任务
- 数据分析报告生成
- 竞品对比分析

## 执行流程
1. 准备工作环境
2. 数据采集/读取
3. 数据清洗整理
4. 分析洞察提炼
5. 报告生成输出

## 成功标准
- 数据完整度 ≥ 80%
- 格式正确率 = 100%
- 用户满意度 ≥ 0.8

## 注意事项
- 使用固定Tab操作，禁止新建标签
- 注意随机延迟防反爬
- 飞书卡片使用正确格式

## 更新日志
- {datetime.now().strftime('%Y-%m-%d')}: 自动创建
"""
    return template

def create_skill(skill_name, avg_score):
    """创建Skill文件"""
    # 转换名称为文件名
    filename = re.sub(r'[^\w]', '_', skill_name)
    filepath = SKILLS_DIR / f"auto_{filename}.md"
    
    # 生成内容
    content = generate_skill_content(skill_name, avg_score)
    
    # 写入文件
    filepath.parent.mkdir(parents=True, exist_ok=True)
    filepath.write_text(content, encoding='utf-8')
    
    return filepath

def run_autonomous_creation():
    """运行自动创建流程"""
    print("=== Autonomous Skill Creation ===\n")
    
    # 1. 检查候选Skill
    candidates = check_skill_candidates()
    
    if not candidates:
        print("⏳ 没有达到自动创建阈值的Skill")
        print("条件：同一Skill连续3次评分≥0.8")
        return []
    
    print(f"🎯 发现 {len(candidates)} 个候选Skill:\n")
    
    created = []
    for c in candidates:
        print(f"  {c['skill_name']}")
        print(f"    平均分: {c['avg_score']:.2f}")
        print(f"    成功次数: {c['success_count']}")
        
        # 创建Skill
        filepath = create_skill(c["skill_name"], c["avg_score"])
        print(f"    ✅ 已创建: {filepath.name}\n")
        
        created.append({
            "skill_name": c["skill_name"],
            "avg_score": c["avg_score"],
            "filepath": str(filepath)
        })
    
    # 保存记录
    save_auto_created(created)
    
    print(f"\n✅ Autonomous Skill Creation 完成")
    print(f"   新创建 {len(created)} 个Skill")
    
    return created

if __name__ == "__main__":
    created = run_autonomous_creation()
    if created:
        print("\n📋 创建的Skill:")
        for c in created:
            print(f"  - {c['skill_name']} ({c['filepath']})")
