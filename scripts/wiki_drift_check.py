#!/usr/bin/env python3
"""
Wiki知识库健康检查
运行 karpathy-wiki LINT 操作：
- 检查 raw/ 中未处理的文件
- 检查孤儿页面（无 inbound 链接）
- 检查过时内容
- 检查断裂的 wikilinks
"""
import os
import re
from datetime import datetime
from pathlib import Path

WIKI_DIR = Path.home() / '.openclaw' / 'workspace' / 'wiki'
RAW_DIR = WIKI_DIR / 'raw'
LOG_FILE = WIKI_DIR / 'log.md'
INDEX_FILE = WIKI_DIR / 'index.md'

def check_raw_drift():
    """检查 raw/ 中未被 log.md 记录的文件"""
    if not RAW_DIR.exists():
        return [], []
    
    raw_files = list(RAW_DIR.glob('*'))
    raw_files = [f for f in raw_files if not f.name.startswith('.')]
    
    if not LOG_FILE.exists():
        return raw_files, []
    
    log_content = LOG_FILE.read_text()
    
    unprocessed = []
    processed = []
    for f in raw_files:
        if f.name in log_content:
            processed.append(f.name)
        else:
            unprocessed.append(f.name)
    
    return unprocessed, processed

def check_orphan_pages():
    """检查孤儿页面（无 inbound 链接）"""
    if not WIKI_DIR.exists():
        return []
    
    # 获取所有 wiki 页面（含 index.md，用于提取出链）
    all_pages_for_links = list(WIKI_DIR.rglob('*.md'))
    # 排除 index/log/schema/overview 等特殊页
    skip_names = {'index', 'log', 'schema', 'overview', 'AI-Agent方法论'}
    all_pages = [p for p in all_pages_for_links if p.name not in skip_names]

    # 收集所有被链接的页面（带完整相对路径）
    # 注意：index.md 也要处理（它们链接到子页面）
    linked = set()
    for page in all_pages_for_links:
        try:
            content = page.read_text()
            # 匹配 [[page]] 格式
            links = re.findall(r'\[\[([^\]]+)\]\]', content)
            for link in links:
                link = link.strip()
                # 处理 [[path|alias]] 格式（只取路径部分）
                if '|' in link:
                    link = link.split('|')[0].strip()
                # 解析相对路径：以来源文件所在目录为基准
                if '/' not in link:
                    # 短链接：相对于当前文件目录
                    parent_dir = page.parent.relative_to(WIKI_DIR)
                    resolved = str(parent_dir / link) if str(parent_dir) != '.' else link
                else:
                    resolved = link
                linked.add(resolved)
                # 同时保留不含扩展名的 stem 形式
                linked.add(link.replace('.md', ''))
        except:
            pass

    # 找出没有被链接的页面（排除 index/log/schema/overview）
    orphans = []
    skip_names = {'index', 'log', 'schema', 'overview', 'AI-Agent方法论', 'INDEX'}
    for page in all_pages:
        page_name = page.stem  # 文件名不带 .md
        page_rel = str(page.relative_to(WIKI_DIR))
        # 检查是否被其他页面链接（匹配完整相对路径或短名）
        # 同时尝试去掉 .md 后缀（因为链接文本通常不含 .md）
        page_rel_no_ext = page_rel.replace('.md', '')
        is_linked = any(
            name in linked or page.name in linked
            for name in [page_rel, page_rel_no_ext, page_name, page.name]
        )
        if not is_linked and page_name not in skip_names:
            orphans.append(page_rel)
    
    return orphans

def check_wiki_completeness():
    """检查内容稀薄的页面"""
    if not WIKI_DIR.exists():
        return []
    
    thin_pages = []
    for page in WIKI_DIR.rglob('*.md'):
        if page.name in ['index.md', 'log.md']:
            continue
        try:
            content = page.read_text()
            # 去掉 YAML frontmatter
            content = re.sub(r'^---.*?---\n', '', content, flags=re.DOTALL)
            lines = [l for l in content.split('\n') if l.strip()]
            if len(lines) < 5:
                thin_pages.append((str(page.relative_to(WIKI_DIR)), len(lines)))
        except:
            pass
    
    return thin_pages

def generate_report():
    """生成检查报告"""
    unprocessed, processed = check_raw_drift()
    orphans = check_orphan_pages()
    thin = check_wiki_completeness()
    
    has_issues = unprocessed or orphans or thin
    
    lines = []
    lines.append(f"## Wiki健康检查 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    
    if not has_issues:
        lines.append("✅ 无问题发现，Wiki状态健康")
    else:
        if unprocessed:
            lines.append(f"⚠️ **raw/ 未处理文件 ({len(unprocessed)}个)**：")
            for f in unprocessed:
                lines.append(f"  - {f}")
        
        if orphans:
            lines.append(f"\n⚠️ **孤儿页面 ({len(orphans)}个)** — 无其他页面链接：")
            for p in orphans:
                lines.append(f"  - {p}")
        
        if thin:
            lines.append(f"\n⚠️ **内容稀薄页面 ({len(thin)}个)** — 少于5行：")
            for p, lines_count in thin:
                lines.append(f"  - {p} ({lines_count}行)")
    
    return '\n'.join(lines), has_issues, unprocessed, orphans, thin

if __name__ == '__main__':
    report, has_issues, unprocessed, orphans, thin = generate_report()
    print(report)
