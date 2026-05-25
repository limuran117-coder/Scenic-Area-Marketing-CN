#!/opt/homebrew/bin/python3.12
"""
LLMWiki Query 脚本
查询知识库，并将结果存回wiki

使用方式：
python3 scripts/llmwiki_query.py <search_term>
python3 scripts/llmwiki_query.py --list  # 列出所有页面
python3 scripts/llmwiki_query.py --read <page_name>  # 读取指定页面
"""

import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw/workspace"
WIKI_DIR = WORKSPACE / "wiki"
INDEX_FILE = WIKI_DIR / "index.md"

def read_file(path):
    if path.exists():
        return path.read_text(encoding='utf-8')
    return ""

def search_in_wiki(query):
    """
    在wiki中搜索内容
    """
    results = []
    query_lower = query.lower()
    
    # 搜索所有md文件
    for md_file in WIKI_DIR.glob("**/*.md"):
        if md_file.name in ["index.md"]:
            continue
        
        content = read_file(md_file)
        
        if query_lower in content.lower():
            # 找到匹配
            rel_path = str(md_file.relative_to(WIKI_DIR))
            
            # 提取上下文
            lines = content.split('\n')
            matches = []
            for i, line in enumerate(lines):
                if query_lower in line.lower():
                    matches.append((i, line.strip()))
            
            results.append({
                "file": rel_path,
                "matches": matches[:3],  # 最多3处匹配
                "preview": content[:200]
            })
    
    return results

def list_all_pages():
    """列出所有wiki页面"""
    pages = []
    
    for md_file in WIKI_DIR.glob("**/*.md"):
        if md_file.name in ["index.md", "log.md"]:
            continue
        if 'schema' in str(md_file) or 'orphans' in str(md_file):
            continue
        
        rel_path = str(md_file.relative_to(WIKI_DIR))
        content = read_file(md_file)
        
        # 提取标题（第一个#开头的内容）
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        title = title_match.group(1) if title_match else md_file.stem
        
        # 提取摘要
        summary = content[:150].replace('\n', ' ')
        
        pages.append({
            "path": rel_path,
            "title": title,
            "summary": summary[:100]
        })
    
    return pages

def save_query_result(query, result, wiki_path=None):
    """
    将查询结果保存到wiki
    """
    if not result:
        return None
    
    # 生成文件名
    safe_query = re.sub(r'[^\w]', '_', query)[:30]
    filename = f"探索记录_{safe_query}.md"
    
    if wiki_path is None:
        wiki_path = WIKI_DIR / "数据日报" / filename
    else:
        wiki_path = WIKI_DIR / wiki_path
    
    wiki_path.parent.mkdir(parents=True, exist_ok=True)
    
    content = f"# 探索：{query}\n\n"
    content += f"> 探索时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    content += f"## 探索结果\n\n"
    
    for item in result:
        content += f"### 📄 {item['file']}\n\n"
        for line_no, line in item['matches']:
            content += f"- 行{line_no+1}: {line}\n"
        content += "\n"
    
    content += f"---\n*自动生成*\n"
    
    wiki_path.write_text(content, encoding='utf-8')
    print(f"💾 已保存探索记录: {wiki_path.relative_to(WIKI_DIR)}")
    
    return wiki_path

def main():
    if len(sys.argv) < 2:
        print("LLMWiki Query")
        print("=" * 50)
        print("使用方式：")
        print("  python3 scripts/llmwiki_query.py <搜索词>")
        print("  python3 scripts/llmwiki_query.py --list")
        print("  python3 scripts/llmwiki_query.py --read <页面名>")
        return
    
    arg = sys.argv[1]
    
    if arg == "--list":
        pages = list_all_pages()
        print(f"\n📚 Wiki页面列表（共 {len(pages)} 个）\n")
        for p in pages:
            print(f"📄 {p['title']}")
            print(f"   {p['path']}")
            print(f"   {p['summary'][:60]}...\n")
    
    elif arg == "--read":
        if len(sys.argv) < 3:
            print("请指定页面名")
            return
        page_name = sys.argv[2]
        # 查找页面
        for md_file in WIKI_DIR.glob(f"**/{page_name}*"):
            if md_file.is_file():
                print(f"\n📄 {md_file.relative_to(WIKI_DIR)}\n")
                print(read_file(md_file))
                return
        print(f"未找到页面: {page_name}")
    
    else:
        query = arg
        print(f"\n🔍 搜索: {query}")
        results = search_in_wiki(query)
        
        if results:
            print(f"\n✅ 找到 {len(results)} 个相关页面\n")
            for r in results:
                print(f"📄 {r['file']}")
                for line_no, line in r['matches']:
                    print(f"   行{line_no+1}: {line[:80]}")
                print()
            
            # 保存结果
            save = input("是否保存到wiki？(y/n): ")
            if save.lower() == 'y':
                save_query_result(query, results)
        else:
            print("未找到相关内容")

if __name__ == "__main__":
    main()
