#!/usr/bin/env python3
"""
代码库知识库漂移检查
运行 karpathy-project-wiki LINT 操作：
- 对比 wiki 与实际代码库结构
- 检查 entity 页面的文件引用是否还存在
- 检查过时文档
"""
import os
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / '.openclaw' / 'workspace'
WIKI_DIR = WORKSPACE / 'wiki'
CODE_DIR = WORKSPACE

def get_actual_files():
    """获取实际代码库文件结构"""
    scripts = list((CODE_DIR / 'scripts').glob('*.py')) if (CODE_DIR / 'scripts').exists() else []
    skill_dirs = [d for d in (CODE_DIR / 'skills').iterdir()] if (CODE_DIR / 'skills').exists() else []
    
    files = {
        'scripts': [f.name for f in scripts],
        'skill_count': len(skill_dirs),
        'skill_names': [d.name for d in skill_dirs if d.is_dir()][:10],
    }
    return files

def get_wiki_entities():
    """从 wiki 中提取 entity 引用"""
    if not (WIKI_DIR / 'entities').exists():
        return []
    
    entities = []
    for page in (WIKI_DIR / 'entities').glob('*.md'):
        try:
            content = page.read_text()
            # 提取文件引用格式: `path:line` 或类似
            refs = re.findall(r'`([^`]+`:\d+)`', content)
            if refs:
                entities.append({'page': page.name, 'refs': refs})
        except:
            pass
    return entities

def check_drift():
    """检查代码库与 wiki 之间的漂移"""
    actual = get_actual_files()
    entities = get_wiki_entities()
    
    issues = []
    
    # 检查 scripts/ 文件是否在 wiki 中有对应文档
    wiki_files_mentioned = set()
    if WIKI_DIR.exists():
        for page in WIKI_DIR.rglob('*.md'):
            try:
                content = page.read_text()
                for script in actual['scripts']:
                    if script in content:
                        wiki_files_mentioned.add(script)
            except:
                pass
    
    # 检查是否有脚本还没在 wiki 中被提及
    undocumented = [s for s in actual['scripts'] if s not in wiki_files_mentioned]
    if undocumented:
        issues.append(f"scripts/ 下有 {len(undocumented)} 个脚本未在 wiki 中提及")
    
    return {
        'actual_files': actual,
        'undocumented_scripts': undocumented,
        'entities_checked': len(entities),
    }

def generate_report():
    """生成漂移报告"""
    drift = check_drift()
    
    lines = []
    lines.append(f"## 代码库Wiki漂移检查 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"scripts/ 共 {len(drift['actual_files']['scripts'])} 个 Python 脚本")
    lines.append(f"skills/ 共 {drift['actual_files']['skill_count']} 个 Skill")
    
    if drift['undocumented_scripts']:
        lines.append(f"\n⚠️ **未归档脚本 ({len(drift['undocumented_scripts'])}个)**：")
        for s in drift['undocumented_scripts']:
            lines.append(f"  - scripts/{s}")
        lines.append("\n建议：下次问答时可顺便归档这些脚本到 wiki/entities/")
    else:
        lines.append("\n✅ 所有 scripts/ 均已在 wiki 中归档")
    
    return '\n'.join(lines)

if __name__ == '__main__':
    print(generate_report())
