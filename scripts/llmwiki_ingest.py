#!/opt/homebrew/bin/python3.12
"""
LLMWiki Ingest 脚本
新知识入库：读取raw文件 → 生成wiki页面 → 更新索引 → 记录日志

触发：
1. 发现新的 raw 文件时手动调用
2. 被其他脚本调用
3. cron任务中调用

使用方式：
python3 scripts/llmwiki_ingest.py <raw_file_path>
python3 scripts/llmwiki_ingest.py --scan  # 扫描所有raw文件
"""

import json
import re
import sys
from datetime import datetime, date
from pathlib import Path

WORKSPACE = Path.home() / ".openclaw/workspace"
WIKI_DIR = WORKSPACE / "wiki"
RAW_DIR = WIKI_DIR / "raw"
INDEX_FILE = WIKI_DIR / "index.md"
LOG_FILE = WIKI_DIR / "log.md"

# 分类映射
CATEGORY_MAP = {
    "景区运营": "景区运营",
    "竞品": "竞品分析",
    "营销": "营销策略",
    "数据": "数据日报",
    "技术": "技术配置",
}

def get_category(file_path):
    """根据文件路径推断分类"""
    path_str = str(file_path)
    for key, category in CATEGORY_MAP.items():
        if key in path_str:
            return category
    return "未分类"

def generate_summary(content, max_length=200):
    """生成摘要"""
    # 去掉markdown格式
    text = re.sub(r'[#*`\[\]]', '', content)
    text = re.sub(r'\n+', ' ', text)
    text = text.strip()
    
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def generate_wiki_filename(raw_file):
    """生成wiki文件名"""
    name = raw_file.stem
    # 去掉日期前缀
    name = re.sub(r'^\d{4}-\d{2}-\d{2}-', '', name)
    return f"{name}.md"

def read_file(path):
    """读取文件"""
    if path.exists():
        return path.read_text(encoding='utf-8')
    return ""

def write_file(path, content):
    """写入文件"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')

def update_index(category, filename, summary):
    """更新index.md"""
    index_content = read_file(INDEX_FILE)
    
    # 找到对应分类section
    category_header = f"## {category}"
    
    if category_header not in index_content:
        # 新增分类
        index_content += f"\n\n{category_header}\n\n| 文章 | 摘要 | Updated |\n|------|------|--------|\n"
    
    # 检查是否已存在该页面
    link = f"[[{category}/{filename}|{filename.replace('.md', '')}]]"
    if link in index_content:
        # 更新现有条目
        pass
    else:
        # 追加新条目
        today = date.today().isoformat()
        row = f"\n| [[{category}/{filename}|{filename.replace('.md', '')}]] | {summary[:50]}... | {today} |"
        
        # 找到分类表格末尾并追加
        lines = index_content.split('\n')
        for i, line in enumerate(lines):
            if line.strip() == '' and i > 0:
                # 找到空行，检查下一行是否是新的##开头
                if i+1 < len(lines) and lines[i+1].startswith('##'):
                    lines.insert(i, row)
                    break
        index_content = '\n'.join(lines)
    
    write_file(INDEX_FILE, index_content)

def append_log(operation, detail):
    """追加到log.md"""
    log_content = read_file(LOG_FILE)
    today = date.today().isoformat()
    
    log_entry = f"\n## [{today}] {operation}\n- {detail}\n"
    
    log_content += log_entry
    write_file(LOG_FILE, log_content)

def ingest_file(raw_file):
    """
    处理单个raw文件
    """
    print(f"\n📥 Ingest: {raw_file}")
    
    content = read_file(raw_file)
    if not content:
        print(f"   ⚠️ 文件为空或不存在")
        return False
    
    # 生成摘要
    summary = generate_summary(content)
    print(f"   📝 摘要: {summary[:80]}...")
    
    # 确定分类和目标路径
    category = get_category(raw_file)
    wiki_filename = generate_wiki_filename(raw_file)
    wiki_path = WIKI_DIR / category / wiki_filename
    
    # 确保分类目录存在
    wiki_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 写入wiki文件
    wiki_content = f"# {wiki_filename.replace('.md', '')}\n\n"
    wiki_content += f"> 来源：{raw_file.name} | 录入：{datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
    wiki_content += f"## 摘要\n\n{summary}\n\n"
    wiki_content += f"## 详细内容\n\n{content}\n\n"
    wiki_content += f"---\n*由 AI Agent 自动录入*\n"
    
    write_file(wiki_path, wiki_content)
    print(f"   ✅ 已生成: {wiki_path.relative_to(WIKI_DIR)}")
    
    # 更新索引
    update_index(category, wiki_filename, summary)
    print(f"   ✅ 已更新索引")
    
    # 记录日志
    append_log("ingest", f"Raw: {raw_file.relative_to(WIKI_DIR)} -> Wiki: {category}/{wiki_filename}")
    print(f"   ✅ 已记录日志")
    
    return True

def scan_raw_files():
    """
    扫描所有raw文件
    """
    print("🔍 扫描 raw 目录...")
    
    if not RAW_DIR.exists():
        print(f"   ⚠️ Raw目录不存在: {RAW_DIR}")
        return []
    
    raw_files = list(RAW_DIR.glob("**/*.md"))
    print(f"   发现 {len(raw_files)} 个 raw 文件")
    
    return raw_files

def main():
    if len(sys.argv) < 2:
        # 扫描模式
        raw_files = scan_raw_files()
        if raw_files:
            print("\n📋 找到以下 raw 文件：")
            for f in raw_files:
                print(f"   - {f.relative_to(RAW_DIR)}")
            print("\n💡 使用方法：")
            print("   python3 scripts/llmwiki_ingest.py <raw_file_path>")
            print("   python3 scripts/llmwiki_ingest.py --scan  # 扫描")
        return
    
    arg = sys.argv[1]
    
    if arg == "--scan":
        raw_files = scan_raw_files()
        for f in raw_files:
            ingest_file(f)
    else:
        raw_path = Path(arg)
        if not raw_path.is_absolute():
            raw_path = WIKI_DIR / raw_path
        ingest_file(raw_path)
    
    print("\n✅ Ingest 完成")

if __name__ == "__main__":
    main()
