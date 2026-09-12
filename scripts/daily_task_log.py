#!/usr/bin/env python3
"""每日任务日志 —— 把当天所有 cron 任务的执行情况与产出，自动写入 memory/YYYY-MM-DD.md

背景：cron 任务跑在 isolated 会话里，session-memory hook 抓不到，
      导致 memory 日档出现整天空缺（任务干了活但没留痕）。
      本脚本不依赖 LLM，纯数据汇总，稳定免费。

用法: python3 daily_task_log.py [YYYY-MM-DD]
"""
import json
import os
import re
import subprocess
import sys
import datetime

WORKSPACE = os.path.expanduser('~/.openclaw/workspace')
WIKI = f'{WORKSPACE}/wiki'
MEMORY = f'{WORKSPACE}/memory'
MARKER = '## 📋 任务执行日志（自动生成）'

date = sys.argv[1] if len(sys.argv) > 1 else datetime.date.today().isoformat()
try:
    day = datetime.date.fromisoformat(date)
except ValueError:
    print(f'日期格式错误: {date}')
    sys.exit(1)

# 当天时间窗（供各扫描函数共用）
start = datetime.datetime.combine(day, datetime.time(0, 0)).timestamp()
end = start + 86400

# ---- 1) 任务执行情况 ----
OPENCLAW_BIN = os.path.expanduser('~/.npm-global/bin/openclaw')
if not os.path.exists(OPENCLAW_BIN):
    OPENCLAW_BIN = 'openclaw'
try:
    out = subprocess.run([OPENCLAW_BIN, 'cron', 'list', '--json'],
                         capture_output=True, text=True, timeout=120).stdout
    jobs = json.loads(out).get('jobs', [])
except Exception as e:
    print(f'读取 cron 列表失败: {e}')
    jobs = []

ran, failed, skipped = [], [], []
for j in jobs:
    lr = j.get('lastRunAtMs')
    if not lr:
        continue
    ts = datetime.datetime.fromtimestamp(lr / 1000)
    if ts.date() != day:
        continue
    name = j.get('name') or '?'
    st = j.get('lastRunStatus') or '-'
    err = (j.get('lastRunError') or '').strip()
    rec = (name, ts.strftime('%H:%M'), st, err)
    if st == 'ok':
        ran.append(rec)
    elif st == 'error':
        failed.append(rec)
    else:
        skipped.append(rec)

# ---- 2) 当天产出文件 ----
def changed(root, label, limit=60):
    res = []
    if not os.path.isdir(root):
        return res
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in ('.obsidian', '.git', 'archived', 'node_modules')]
        for f in files:
            if not f.endswith(('.md', '.json')):
                continue
            p = os.path.join(dirpath, f)
            try:
                mt = os.path.getmtime(p)
            except OSError:
                continue
            if start <= mt < end:
                rel = os.path.relpath(p, root)
                if rel in ('index.md', 'log.md'):
                    continue
                res.append((mt, rel))
    res.sort(reverse=True)
    return [(r[1], datetime.datetime.fromtimestamp(r[0]).strftime('%H:%M')) for r in res[:limit]]

wiki_files = changed(WIKI, 'wiki')

# ---- 3) 生成 markdown ----
lines = [MARKER, '', f'> 自动汇总于 {datetime.datetime.now():%Y-%m-%d %H:%M}｜数据源：cron 执行记录 + 文件变更扫描', '']

lines.append(f'### 执行概览（{len(ran) + len(failed) + len(skipped)} 个任务）')
lines.append('')
if ran or failed:
    lines.append('| 任务 | 时间 | 状态 | 说明 |')
    lines.append('|------|------|------|------|')
    for name, ts, st, err in sorted(ran + failed + skipped, key=lambda x: x[1]):
        mark = {'ok': '✅', 'error': '❌'}.get(st, '⏭')
        note = err[:60].replace('|', '/') if err else ''
        lines.append(f'| {name} | {ts} | {mark} {st} | {note} |')
    lines.append('')

if failed:
    lines.append('### ⚠️ 失败任务')
    lines.append('')
    for name, ts, st, err in failed:
        lines.append(f'- **{name}**（{ts}）：{err[:150] or "无错误详情"}')
    lines.append('')

if skipped:
    lines.append(f'### ⏭ 跳过（{len(skipped)} 个）：{", ".join(n for n, _, _, _ in skipped)}')
    lines.append('')

lines.append(f'### 📁 当天产出文件（{len(wiki_files)} 个 wiki 文件变更）')
lines.append('')
if wiki_files:
    for rel, ts in wiki_files[:40]:
        lines.append(f'- `{rel}`（{ts}）')
    if len(wiki_files) > 40:
        lines.append(f'- …等共 {len(wiki_files)} 个')
else:
    lines.append('- （当天无 wiki 文件变更）')
lines.append('')

block = '\n'.join(lines)

# ---- 3.5) 系统变更扫描（写入 openclaw vault 的 CHANGELOG）----
def system_changes():
    """扫描 OpenClaw 系统层的当日变更：技能/扩展/配置/插件/重启"""
    res = []
    targets = [
        (os.path.expanduser('~/.openclaw/skills'), '技能'),
        (os.path.expanduser('~/.openclaw/extensions'), '扩展'),
        (os.path.expanduser('~/.openclaw/skill-workshop'), '技能工坊'),
        (os.path.expanduser('~/.openclaw/plugins'), '插件'),
    ]
    for root, label in targets:
        if not os.path.isdir(root):
            continue
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d != 'node_modules']
            for f in files:
                if not f.endswith(('.md', '.json')):
                    continue
                p = os.path.join(dirpath, f)
                try:
                    mt = os.path.getmtime(p)
                except OSError:
                    continue
                if start <= mt < end:
                    res.append((mt, label, os.path.relpath(p, os.path.expanduser('~/.openclaw'))))
    # 配置文件
    for p, label in [(os.path.expanduser('~/.openclaw/openclaw.json'), '配置')]:
        if os.path.exists(p) and start <= os.path.getmtime(p) < end:
            res.append((os.path.getmtime(p), label, os.path.basename(p)))
    # gateway 重启
    restart_log = os.path.expanduser('~/.openclaw/logs/gateway-restart.log')
    restarts = []
    if os.path.exists(restart_log):
        for line in open(restart_log, encoding='utf-8', errors='replace'):
            if day.isoformat() in line:
                restarts.append(line.strip()[:120])
    res.sort(reverse=True)
    return res, restarts


sys_changes, restarts = system_changes()
changelog = os.path.expanduser('~/.openclaw/CHANGELOG.md')
if not os.path.exists(changelog):
    open(changelog, 'w', encoding='utf-8').write(
        '# OpenClaw 系统变更日志\n\n'
        '> 自动记录（每日任务日志脚本扫描）：技能 / 扩展 / 插件 / 配置 / gateway 重启\n'
        '> 由 cron「每日任务日志」每天 22:30 维护，人工补充请直接在此追加。\n\n')

cl = [f'## {date}', '']
if restarts:
    cl.append('### 🔄 gateway 重启')
    cl.append('')
    for r in restarts[:10]:
        cl.append(f'- `{r}`')
    cl.append('')
if sys_changes:
    cl.append(f'### 变更文件（{len(sys_changes)} 个）')
    cl.append('')
    cl.append('| 时间 | 类型 | 文件 |')
    cl.append('|------|------|------|')
    for mt, label, rel in sys_changes[:30]:
        cl.append(f'| {datetime.datetime.fromtimestamp(mt):%H:%M} | {label} | `{rel}` |')
    cl.append('')
if not restarts and not sys_changes:
    cl.append('- （当天无系统层变更）')
    cl.append('')
entry = '\n'.join(cl)

if date not in open(changelog, encoding='utf-8').read():
    with open(changelog, 'a', encoding='utf-8') as f:
        f.write(entry + '\n')
    print(f'✅ 已追加系统变更到 CHANGELOG.md（{len(sys_changes)} 个文件变更 / {len(restarts)} 次重启）')
else:
    # 替换当天区块
    txt = open(changelog, encoding='utf-8').read()
    head = txt.split(f'## {date}')[0].rstrip()
    rest = txt.split(f'## {date}', 1)[1]
    nxt = rest.find('\n## ')
    tail = rest[nxt:] if nxt != -1 else ''
    open(changelog, 'w', encoding='utf-8').write(f'{head}\n\n{entry}\n{tail}')
    print(f'✅ 已更新 CHANGELOG.md 当天区块（{len(sys_changes)} 个文件变更 / {len(restarts)} 次重启）')

# ---- 4) 写入日档 ----
os.makedirs(MEMORY, exist_ok=True)
daily = f'{MEMORY}/{date}.md'
existing = ''
if os.path.exists(daily):
    existing = open(daily, encoding='utf-8').read()

if MARKER in existing:
    # 替换旧的自动区块（保留人工内容）
    head = existing.split(MARKER)[0].rstrip()
    new = f'{head}\n\n{block}' if head else block
else:
    new = (existing.rstrip() + '\n\n' + block) if existing.strip() else f'# {date}\n\n{block}'

open(daily, 'w', encoding='utf-8').write(new)
print(f'✅ 已写入 {daily}')
print(f'   任务 {len(ran)} 成功 / {len(failed)} 失败 / {len(skipped)} 跳过｜产出 {len(wiki_files)} 个文件')
if failed:
    print(f'   ⚠️ 失败: {[n for n, _, _, _ in failed]}')
