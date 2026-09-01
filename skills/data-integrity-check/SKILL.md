---
name: "data-integrity-check"
description: "数据采集前完整性校验：cookie/excel/代理/文件，防5/26三联失败"
---

# 数据完整性校验

## 背景

2026-05-26 发生「三联失败」：抖音 cookie 过期(401)、小红书文件被移动、代理断连——三个不同的根因在同一天集中爆发，完全没有事前检查机制。每次失败后需要手动排查重试。

## 前置校验清单（任何数据采集任务前必跑）

### A级：硬依赖（不过则跳过任务）

| # | 检查项 | 命令 | 通过条件 |
|---|--------|------|---------|
| 1 | 抖音Cookie | `python3 -c "import json; f=open('/tmp/juLiang_cookies.json'); d=json.load(f); print('ok' if d else 'empty')"` | 文件存在且非空 |
| 2 | 小红书Cookie | `python3 -c "import json; f=open('/tmp/xiaohongshu_cookies.json'); d=json.load(f); print('ok' if d else 'empty')"` | 文件存在且非空 |
| 3 | 代理连通性 | `curl -s -o /dev/null -w '%{http_code}' --max-time 5 --socks5 127.0.0.1:7897 http://httpbin.org/ip` | 返回 200 |
| 4 | 抖音脚本存在 | `test -f ~/.openclaw/workspace/scripts/douyin_index.py` | 返回 0 |
| 5 | 小红书脚本存在 | `test -f ~/.openclaw/workspace/scripts/xiaohongshu_crawl.py` | 返回 0 |
| 6 | 客流Excel存在 | `test -f ~/Desktop/2026年电影小镇实际客流.xlsx` | 返回 0 |
| 7 | 历年客流存在 | `test -f ~/Desktop/2023-2025年门票销售及客流统计数据表.xlsx` | 返回 0 |

### B级：软依赖（警告但继续）

| # | 检查项 | 命令 | 通过条件 |
|---|--------|------|---------|
| 8 | 磁盘空间 | `df -h ~ \| tail -1 \| awk '{print \$5}' \| sed 's/%//'` | <90% |
| 9 | 网络连通性 | `curl -s -o /dev/null -w '%{http_code}' --max-time 5 https://api.deepseek.com` | 返回 200 或 401（服务活着） |
| 10 | 飞书连接 | `curl -s -o /dev/null -w '%{http_code}' --max-time 5 https://open.feishu.cn` | 返回 200 |

## 执行流程

```
┌──────────────────────┐
│   收到任务执行指令     │
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│  A级检查（全部通过？）│ ← 否 → 跳过任务，报告具体哪个出问题
└──────────┬───────────┘
           ↓ 是
┌──────────────────────┐
│  B级检查（有警告？）  │ ← 是 → 记录到日志，继续执行
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│     执行任务          │
└──────────────────────┘
```

## 快速执行脚本

```bash
# 一键检查所有A级依赖
python3 -c "
import json, os

checks = {
    '抖音Cookie': os.path.isfile('/tmp/juLiang_cookies.json') and os.path.getsize('/tmp/juLiang_cookies.json') > 10,
    '小红书Cookie': os.path.isfile('/tmp/xiaohongshu_cookies.json') and os.path.getsize('/tmp/xiaohongshu_cookies.json') > 10,
    '抖音脚本': os.path.isfile(os.path.expanduser('~/.openclaw/workspace/scripts/douyin_index.py')),
    '小红书脚本': os.path.isfile(os.path.expanduser('~/.openclaw/workspace/scripts/xiaohongshu_crawl.py')),
    '客流Excel': os.path.isfile(os.path.expanduser('~/Desktop/2026年电影小镇实际客流.xlsx')),
}

for name, ok in checks.items():
    print(f'{\"✅\" if ok else \"❌\"} {name}')

print(f'结论: {\"ALL PASS\" if all(checks.values()) else \"FAIL: \" + \", \".join(k for k,v in checks.items() if not v)}')
"
```

```bash
# 检查代理
curl -s --max-time 5 --socks5 127.0.0.1:7897 http://httpbin.org/ip
```

## 失败处理规则

| 失败等级 | 处理方式 |
|---------|---------|
| A级1项失败 | 跳过任务，在报告中标注具体失败项 |
| A级≥2项失败 | 跳过任务，推送到电影小镇群提醒 |
| B级失败 | 记录日志，继续执行 |
| 连续失败≥3次 | 推送到电影小镇群 |

## 记录格式

每次校验结果追加到 `memory/topics/data-integrity-log.md`：

```
| 日期 | 任务 | A级通过 | B级通过 | 失败项 |
|------|------|--------|--------|--------|
| 6/5 | 抖音指数 | ✅ 7/7 | ✅ 3/3 | 无 |
```

## 客流 SSOT 新版本校验（每周二更新 / 站长告知新版时）

数据更新后（或站长说"XX.csv 是最新"）必做，防旧版误导报告：

1. **定位最新版**（禁裸 `find`，文件名含 `()`）：
   ```bash
   python3 -c "import glob,os; fs=[f for f in glob.glob(os.path.expanduser('~/Downloads/2026游客量统计*.csv'))]; print(max(fs, key=os.path.getmtime))"
   ```
2. **宽表解析**（SSOT 是宽表，无 `日期`/`合计` 列；`dashboard.py` 的 schema 假设已过时）：
   - 门票人数合计=第13行 / 门票收入金额=第14行 / 闸机入园人次=第15行 / 售卖=第31行（德化街演出票，非客流）
   - 日期 = 列索引 - 2（第3列 = 1/1）；YTD = 第3列起数值求和
3. **尾3日全 0 → 标「暂缺/暂态」**，不写"收官"（6/30 铁律）；例：数据至8/29、8/30-31为0 → "8/30-31暂缺"
4. **更新 MEMORY.md 关键数据指针**：版本号 (N)、截止日、YTD 门票/闸机/收入三项
