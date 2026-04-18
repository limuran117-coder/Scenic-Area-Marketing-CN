#!/usr/bin/env python3
"""
Periodic Nudge 脚本
主动检查被忽略的上下文/规则冲突/遗忘知识，主动提醒用户

触发方式：
1. 被每日复盘Agent调用（主要）
2. 被其他cron任务调用做上下文检查
3. 可以单独运行做全面检查

检查维度：
1. 上下文遗忘 - 重要上下文是否被遗忘
2. 规则冲突 - 不同文件间的规则是否有矛盾
3. 知识流失 - 近期学到的重要知识是否被沉淀
"""

import json
import re
from datetime import datetime, timedelta, date
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw/workspace"
MEMORY_DIR = WORKSPACE / "memory"
WIKI_DIR = WORKSPACE / "wiki"
NUDGE_FILE = MEMORY_DIR / "topics" / "nudge_pending.json"
LAST_CONTEXT_FILE = MEMORY_DIR / "topics" / "last_context.json"

# 重要上下文关键词（这些内容被提到但可能未被使用）
IMPORTANT_KEYWORDS = [
    "目标", "KPI", "客流", "营收", "竞品", "策略",
    "清明上河园", "万岁山", "银基", "方特",
    "年度", "月度", "周度",
    "转化率", "曝光", "搜索指数", "综合指数"
]

def load_json(path, default):
    """加载JSON文件，不存在则返回默认值"""
    if path and path.exists():
        try:
            return json.loads(path.read_text())
        except:
            return default
    return default

def save_json(path, data):
    """保存JSON文件"""
    if path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2))

def check_context_forgetting():
    """
    检查上下文遗忘
    思路：如果某些重要关键词在对话中被提到，但最近的记忆文件中没有相关记录，说明可能被忽略了
    """
    issues = []
    
    # 读取今日记忆文件
    today = date.today().isoformat()
    today_memory = MEMORY_DIR / f"{today}.md"
    
    if not today_memory.exists():
        return issues
    
    content = today_memory.read_text()
    
    # 检查重要关键词是否被提到
    mentioned = []
    for kw in IMPORTANT_KEYWORDS:
        if kw in content:
            mentioned.append(kw)
    
    # 检查这些关键词是否被遗忘（在记忆中没有后续跟踪）
    # 简化：如果一个关键词被提到但后续没有行动项，说明可能被忽略
    # 这里只是标记，由人工判断
    
    return issues

def check_rule_conflicts():
    """
    检查规则冲突
    扫描memory/topics/下的规则，看是否有矛盾
    """
    issues = []
    topics_dir = MEMORY_DIR / "topics"
    
    if not topics_dir.exists():
        return issues
    
    # 收集所有规则
    rules = []
    for f in topics_dir.glob("*.md"):
        if f.name.startswith("20"):
            continue  # 跳过日志文件
        
        content = f.read_text()
        
        # 提取 #rule/xxx 标签
        rule_tags = re.findall(r'#rule/(\w+)', content)
        for tag in rule_tags:
            rules.append({"tag": tag, "file": f.name})
    
    # 检查同一标签的规则是否有矛盾
    rule_dict = {}
    for r in rules:
        tag = r["tag"]
        if tag not in rule_dict:
            rule_dict[tag] = []
        rule_dict[tag].append(r["file"])
    
    for tag, files in rule_dict.items():
        if len(set(files)) > 1:  # 同一规则出现在不同文件
            issues.append({
                "type": "rule_conflict",
                "rule": tag,
                "files": list(set(files)),
                "suggestion": f"规则 #{tag} 在多个文件中有定义，请确认以哪个为准"
            })
    
    return issues

def check_knowledge_drain():
    """
    检查知识流失
    思路：Dream整合的内容是否有被遗忘的
    """
    issues = []
    
    # 读取最近的Dream记录
    dreams_dir = MEMORY_DIR / ".dreams"
    if not dreams_dir.exists():
        return issues
    
    # 找最近的dream文件
    dream_files = sorted(dreams_dir.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)
    
    if not dream_files:
        return issues
    
    # 检查是否有重要洞察未被执行
    try:
        recent_dreams = []
        for f in dream_files[:3]:  # 只看最近3个
            data = json.loads(f.read_text())
            recent_dreams.extend(data.get("insights", []) if isinstance(data, dict) else [])
        
        # 简化：只是标记有dream记录
        if recent_dreams:
            issues.append({
                "type": "knowledge_check",
                "message": f"近期有 {len(recent_dreams)} 条洞察待跟踪",
                "suggestion": "确认这些洞察是否已转化为行动"
            })
    except:
        pass
    
    return issues

def check_skill_nudge():
    """
    检查是否有较少使用的技能可以推荐给用户
    思路：读取 skill-usage.md，如果某些高频技能长期未触发，提醒用户
    """
    issues = []
    usage_file = MEMORY_DIR / 'skill-usage.md'
    
    if not usage_file.exists():
        # 第一次运行，推荐所有核心技能
        issues.append({
            'type': 'skill_reminder',
            'message': '你可以用自然语言指挥我执行各种任务',
            'suggestion': '试试说"抖音今天怎么样"或"竞品分析"或"周报"',
            'skills': ['抖音指数日报', '竞品关键词深度分析', '周度客流营收洞察', '文旅热点追踪']
        })
        return issues
    
    content = usage_file.read_text()
    # 检查最近一次使用记录
    import re
    entries = re.findall(r'## (\d{4}-\d{2}-\d{2})', content)
    if not entries:
        return issues
    
    last_date = entries[0] if entries else None
    if last_date:
        from datetime import datetime
        try:
            last = datetime.strptime(last_date, '%Y-%m-%d').date()
            days_ago = (date.today() - last).days
            if days_ago > 3:
                issues.append({
                    'type': 'skill_reminder',
                    'message': f'你已经{days_ago}天没有触发日常任务了',
                    'suggestion': '需要我运行"抖音日报"或"竞品分析"吗？直接说就行',
                    'skills': ['抖音指数日报', '竞品关键词深度分析', '小红书日报']
                })
        except:
            pass
    
    return issues

def check_pending_nudge():
    """
    检查是否有待处理的nudge
    """
    return load_json(NUDGE_FILE, [])

def generate_nudge_message(all_issues):
    """
    生成nudge提醒消息
    """
    if not all_issues:
        return None
    
    messages = []
    for issue in all_issues:
        if issue["type"] == "rule_conflict":
            messages.append(f"⚠️ **规则冲突**：{issue['suggestion']}")
        elif issue["type"] == "knowledge_check":
            messages.append(f"💡 **{issue['message']}**：{issue['suggestion']}")
        elif issue["type"] == "context_forget":
            messages.append(f"🔔 **{issue['suggestion']}**")
        elif issue["type"] == "skill_reminder":
            messages.append(f"🎯 **{issue['message']}**：{issue['suggestion']}")
    
    if messages:
        return "\n\n".join(messages)
    return None

def run_full_check():
    """
    运行全面检查
    """
    all_issues = []
    
    # 1. 检查上下文遗忘
    context_issues = check_context_forgetting()
    all_issues.extend(context_issues)
    
    # 2. 检查规则冲突
    rule_issues = check_rule_conflicts()
    all_issues.extend(rule_issues)
    
    # 3. 检查知识流失
    knowledge_issues = check_knowledge_drain()
    all_issues.extend(knowledge_issues)
    
    # 4. 检查待处理nudge
    pending = check_pending_nudge()
    all_issues.extend(pending)
    
    # 5. 检查技能提醒（较少使用的技能）
    skill_issues = check_skill_nudge()
    all_issues.extend(skill_issues)
    
    # 保存待处理nudge
    if all_issues:
        save_json(NUDGE_FILE, all_issues)
    
    # 生成消息
    message = generate_nudge_message(all_issues)
    
    return {
        "issues_count": len(all_issues),
        "issues": all_issues,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }

def add_nudge(nudge_type, content, suggestion):
    """
    添加一个nudge项
    """
    pending = load_json(NUDGE_FILE, [])
    pending.append({
        "type": nudge_type,
        "content": content,
        "suggestion": suggestion,
        "created": datetime.now().isoformat()
    })
    save_json(NUDGE_FILE, pending)
    return pending

def main():
    """命令行调用"""
    result = run_full_check()
    
    print(f"检查完成：发现 {result['issues_count']} 个问题")
    
    if result["message"]:
        print("\n" + "="*50)
        print(result["message"])
        print("="*50)
    else:
        print("✅ 无需提醒")

if __name__ == "__main__":
    main()
