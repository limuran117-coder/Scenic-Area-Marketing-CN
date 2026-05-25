#!/opt/homebrew/bin/python3.12
"""
LLMWiki Lint 脚本
定期检查知识库：矛盾点、过时信息、孤儿页面、缺失概念

触发：每周日系统升级时自动运行
或：手动调用 python3 scripts/llmwiki_lint.py
"""

import json
import re
from datetime import datetime, timedelta, date
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw/workspace"
WIKI_DIR = WORKSPACE / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"
RAW_DIR = WIKI_DIR / "raw"
ORPHANS_DIR = WIKI_DIR / "orphans"

# 矛盾关键词（互相矛盾的概念）
CONTRADICTION_PAIRS = [
    ("抖音", "小红书"),  # 两个平台不同策略
    ("搜索指数", "综合指数"),  # 不同指标
]

def read_file(path):
    """读取文件内容"""
    if path.exists():
        return path.read_text(encoding='utf-8')
    return ""

def get_all_markdown_files():
    """获取所有markdown文件"""
    files = []
    for ext in ["*.md", "**/*.md"]:
        files.extend(WIKI_DIR.glob(ext))
    return [f for f in files if f.name not in ["index.md", "log.md"]]

def check_staleness():
    """
    检查过时信息
    超过30天未更新的档案页
    """
    issues = []
    cutoff = date.today() - timedelta(days=30)
    
    # 扫描所有wiki子目录的md文件
    for md_file in get_all_markdown_files():
        if md_file.is_file():
            content = read_file(md_file)
            
            # 检查是否有更新时间标记
            update_match = re.search(r'最后更新：(\d{4}-\d{2}-\d{2})', content)
            if update_match:
                update_date = datetime.strptime(update_match.group(1), "%Y-%m-%d").date()
                if update_date < cutoff:
                    issues.append({
                        "type": "stale",
                        "file": str(md_file.relative_to(WIKI_DIR)),
                        "last_update": update_match.group(1),
                        "days_old": (date.today() - update_date).days,
                        "suggestion": f"该档案超过30天未更新，建议核实是否有过期信息"
                    })
    
    return issues

def check_orphan_pages():
    """
    检查孤儿页面
    index.md 中未引用的页面
    """
    issues = []
    
    index_content = read_file(INDEX_FILE)
    
    # 提取index中引用的所有文件
    referenced = re.findall(r'\[\[([^\]|]+)\]\]', index_content)
    
    # 获取所有实际文件
    all_files = [str(f.relative_to(WIKI_DIR)) for f in get_all_markdown_files()]
    
    # 找未被引用的文件
    for f in all_files:
        f_normalized = f.replace('\\', '/')
        # 去除 .md 后缀后再比对（index中[[xxx]]引用不带扩展名）
        f_stem = f_normalized.rsplit('.md', 1)[0] if f_normalized.endswith('.md') else f_normalized
        # 同时处理 [[wiki/xxx]] 和 [[xxx]] 两种引用格式
        f_stem_with_wiki = 'wiki/' + f_stem
        if f_stem in referenced or f_stem_with_wiki in referenced or f_normalized in referenced:
            continue
        # 排除 schema 和 orphans 目录
        if not f.startswith('schema/') and not f.startswith('orphans/'):
                issues.append({
                    "type": "orphan",
                    "file": f,
                    "suggestion": "该页面在 index.md 中未被引用，可能需要补充索引"
                })
    
    return issues

def check_contradictions():
    """
    检查矛盾点
    同一概念在不同页面的描述是否有冲突
    """
    issues = []
    
    # 简化版：检查关键指标的表述一致性
    # 如"年度目标132万"是否在多个地方一致
    
    files = get_all_markdown_files()
    targets = {}
    
    for f in files:
        content = read_file(f)
        # 查找年度目标
        goal_match = re.search(r'年度.*?(\d+)\s*万', content)
        if goal_match:
            goal = goal_match.group(1)
            if goal in targets:
                # 发现同一个目标在不同文件
                issues.append({
                    "type": "contradiction",
                    "concept": "年度目标",
                    "files": [targets[goal], str(f.relative_to(WIKI_DIR))],
                    "values": [goal],
                    "suggestion": "年度目标在多个文件中存在，需确认最新值"
                })
            else:
                targets[goal] = str(f.relative_to(WIKI_DIR))
    
    return issues

def check_missing_concepts():
    """
    检查缺失概念
    应该有的主题但 wiki 中没有
    """
    concepts = [
        ("抖音指数", "数据日报"),
        ("小红书", "营销策略"),
        ("竞品", "竞品分析"),
        ("客流", "景区运营"),
        ("营收", "景区运营"),
    ]
    
    issues = []
    all_content = ""
    for f in get_all_markdown_files():
        all_content += read_file(f)
    
    for concept, expected_category in concepts:
        if concept not in all_content:
            issues.append({
                "type": "missing",
                "concept": concept,
                "suggestion": f"缺少「{concept}」相关页面，建议在{expected_category}目录补充"
            })
    
    return issues

def move_to_orphans(file_path):
    """将孤儿页面移动到orphans目录"""
    src = WIKI_DIR / file_path
    dst = ORPHANS_DIR / file_path
    
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding='utf-8'), encoding='utf-8')
        src.unlink()
        return True
    return False

def run_lint():
    """
    运行完整 lint 检查
    """
    print("🔍 LLMWiki Lint 检查...")
    print("=" * 50)
    
    all_issues = []
    
    # 1. 检查过时信息
    print("\n📋 检查过时信息...")
    stale_issues = check_staleness()
    all_issues.extend(stale_issues)
    print(f"   发现 {len(stale_issues)} 个过时页面")
    
    # 2. 检查孤儿页面
    print("\n📋 检查孤儿页面...")
    orphan_issues = check_orphan_pages()
    all_issues.extend(orphan_issues)
    print(f"   发现 {len(orphan_issues)} 个孤儿页面")
    
    # 3. 检查矛盾点
    print("\n📋 检查矛盾点...")
    contradiction_issues = check_contradictions()
    all_issues.extend(contradiction_issues)
    print(f"   发现 {len(contradiction_issues)} 个矛盾点")
    
    # 4. 检查缺失概念
    print("\n📋 检查缺失概念...")
    missing_issues = check_missing_concepts()
    all_issues.extend(missing_issues)
    print(f"   发现 {len(missing_issues)} 个缺失概念")
    
    # 输出汇总
    print("\n" + "=" * 50)
    print(f"📊 检查完成：共发现 {len(all_issues)} 个问题\n")
    
    if all_issues:
        print("### 问题汇总\n")
        for i, issue in enumerate(all_issues, 1):
            print(f"{i}. [{issue['type']}] {issue.get('file', issue.get('concept', 'N/A'))}")
            print(f"   💡 {issue['suggestion']}\n")
    
    return all_issues

def main():
    issues = run_lint()
    
    # 保存结果
    result_file = WIKI_DIR / "lint-result.json"
    result_file.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "issues_count": len(issues),
        "issues": issues
    }, ensure_ascii=False, indent=2))
    
    print(f"\n📄 结果已保存: {result_file}")

if __name__ == "__main__":
    main()
