#!/opt/homebrew/bin/python3.12
"""
feishu_wiki_sync.py — 飞书知识库 → 本地 wiki 同步工具 (W30 spike)

基于 crawl4ai 0.9.2 抓公开页面 + 铁山 feishu-wiki plugin 拉已登录页面，
输出 LLM-ready Markdown 入 wiki/ 知识库。

输入：
  - URL（飞书公开 wiki 或已登录页面）
  - urls.txt（批量）
  - 飞书 docx token（拉已登录 wiki 内容）

输出：
  - 默认: wiki/复盘报告/外部/sync-YYYYMMDD/<slug>.md
  - 含 yaml frontmatter（来源、抓取时间、状态）

依赖：
  - crawl4ai==0.9.2 (venv spike_venv 装好)
  - playwright (crawl4ai 自带)

用法：
  /tmp/spike_venv/bin/python3 feishu_wiki_sync.py "https://*.feishu.cn/wiki/XXX"
  /tmp/spike_venv/bin/python3 feishu_wiki_sync.py --file urls.txt
  /tmp/spike_venv/bin/python3 feishu_wiki_sync.py <url> --dry-run

W30 spike 设计：
- 仅抓公开页面（最多用 cookie）
- 不接管 CDP 18800
- 不动现有 douyin/xhs 脚本
- 成功/失败都计入 sync-log.md
"""

import asyncio
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from datetime import datetime

# === venv 注入 ===
_SPIKE_VENV_SITE = '/tmp/spike_venv/lib/python3.12/site-packages'
if os.path.exists(_SPIKE_VENV_SITE) and _SPIKE_VENV_SITE not in sys.path:
    sys.path.insert(0, _SPIKE_VENV_SITE)


def url_to_slug(url: str) -> str:
    """URL → 文件名 slug"""
    # https://bytedance.feishu.cn/wiki/ABC123 -> wiki-abc123
    m = re.search(r'/wiki/([^/?#]+)', url)
    if m:
        return f'wiki-{m.group(1).lower()[:20]}'
    # docx
    m = re.search(r'/docx/([^/?#]+)', url)
    if m:
        return f'docx-{m.group(1).lower()[:20]}'
    # fallback
    return re.sub(r'[^a-z0-9]+', '-', url.lower())[:50].strip('-')


def make_frontmatter(url, title, status, error=None):
    """生成 YAML frontmatter"""
    fm_lines = [
        '---',
        f'title: "{title or url_to_slug(url)}"',
        f'source_url: "{url}"',
        f'source_type: "feishu-wiki-or-docx"',
        f'synced_at: "{datetime.now().isoformat()}"',
        f'sync_tool: "feishu_wiki_sync.py v1.0 (crawl4ai 0.9.2)"',
        f'sync_status: "{status}"',
    ]
    if error:
        fm_lines.append(f'error: "{error[:200]}"')
    fm_lines.append('---')
    return '\n'.join(fm_lines)


async def crawl_one(url, output_dir, dry_run=False):
    """单 URL 抓取"""
    from crawl4ai import AsyncWebCrawler

    slug = url_to_slug(url)
    today = datetime.now().strftime('%Y%m%d')
    out_dir = Path(output_dir) / f'sync-{today}'
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f'{slug}.md'

    if out_path.exists() and not dry_run:
        return {
            'url': url, 'status': 'skipped (exists)',
            'output': str(out_path)
        }

    print(f"\n[FETCH] {url}")
    try:
        async with AsyncWebCrawler(verbose=False) as crawler:
            result = await crawler.arun(url=url, bypass_cache=False)
            status_code = result.status_code
            markdown = result.markdown.raw_markdown if result.markdown else ''

            title_match = re.search(r'^# (.+)$', markdown, re.MULTILINE)
            title = title_match.group(1) if title_match else slug

            print(f"  Status: {status_code}, Markdown: {len(markdown)} chars")

            if dry_run:
                print(f"  [DRY] 不写文件，仅预览")
                print(f"  [DRY] Frontmatter 预览:")
                fm = make_frontmatter(url, title, 'dry-run')
                print(fm[:200] + '...')
                return {
                    'url': url, 'status': 'dry-run',
                    'output': str(out_path)
                }

            frontmatter = make_frontmatter(url, title, 'success')
            content = f'{frontmatter}\n\n{markdown}\n'
            out_path.write_text(content, encoding='utf-8')
            print(f"  ✅ 已存: {out_path}")

            return {
                'url': url, 'status': 'success',
                'output': str(out_path),
                'markdown_len': len(markdown)
            }

    except Exception as e:
        print(f"  ❌ 异常: {e}")
        if not dry_run:
            err_path = out_dir / f'{slug}.ERROR.md'
            err_path.write_text(
                make_frontmatter(url, title or '', 'error', str(e)) + '\n\n# Error\n\n' + str(e),
                encoding='utf-8'
            )
            return {
                'url': url, 'status': 'error',
                'output': str(err_path),
                'error': str(e)
            }
        return {'url': url, 'status': 'error', 'error': str(e)}


async def crawl_batch(urls, output_dir, dry_run=False):
    results = []
    for url in urls:
        url = url.strip()
        if not url or url.startswith('#'):
            continue
        result = await crawl_one(url, output_dir, dry_run)
        results.append(result)
    return results


def load_urls_from_file(path):
    p = Path(path)
    if not p.exists():
        return []
    return [line.strip() for line in p.read_text(encoding='utf-8').split('\n') if line.strip() and not line.strip().startswith('#')]


def main():
    ap = argparse.ArgumentParser(description='飞书知识库 → 本地 wiki 同步')
    ap.add_argument('urls', nargs='*', help='URL 列表')
    ap.add_argument('--file', '-f', help='urls.txt 路径（批量）')
    ap.add_argument('--output-dir', '-o', default='./wiki/复盘报告/外部',
                    help='输出目录 (default: ./wiki/复盘报告/外部)')
    ap.add_argument('--dry-run', action='store_true', help='仅预览不写文件')
    args = ap.parse_args()

    urls = list(args.urls) + load_urls_from_file(args.file) if args.file else list(args.urls)
    if not urls:
        ap.print_help()
        sys.exit(1)

    print(f"[INFO] {len(urls)} 个 URL, 输出至 {args.output_dir}")
    if args.dry_run:
        print("[MODE] DRY RUN（不写文件）")

    start = time.time()
    results = asyncio.run(crawl_batch(urls, args.output_dir, args.dry_run))
    duration = time.time() - start

    # 汇总
    success = sum(1 for r in results if r.get('status') == 'success')
    skipped = sum(1 for r in results if 'skipped' in r.get('status', ''))
    errors = sum(1 for r in results if r.get('status') == 'error')

    print(f"\n=== 同步汇总 ===")
    print(f"  总数: {len(results)}")
    print(f"  成功: {success}")
    print(f"  跳过: {skipped}")
    print(f"  失败: {errors}")
    print(f"  耗时: {duration:.1f}s")

    sys.exit(0 if errors == 0 else 1)


if __name__ == '__main__':
    main()
