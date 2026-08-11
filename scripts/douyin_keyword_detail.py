#!/opt/homebrew/bin/python3.12
"""
抖音指数·关键词详情增强采集脚本 v4
混合采集策略：
  textContent 解析 → 搜索指数/综合指数（Tab1）
  innerText 解析  → 关联词/地域/性别（Tab2/3）
  截图+AI 读图    → 三分解读/折线图/关联词图谱/年龄/兴趣

采集维度：
  1. 关键词搜索指数（同比/环比/平均值）
  2. 关键词综合指数（同比/环比/平均值）
  3. 综合指数三分解读（内容分/搜索分/传播分 增长率）→ 截图读
  4. 趋势折线图（每日数值）→ 截图读
  5. 搜索关联词 TOP 20（关联度分值）→ innerText 直接读
  6. 地域分布 TOP 34（省份/占比/TGI）→ innerText 直接读
  7. 年龄分布 + 性别分布 + 兴趣分布 → 截图读

输出：/tmp/douyin_keyword_detail.json
截图：/tmp/douyin_kw_{keyword}_tab{1,2,3}.png（供AI解读图表数据）

⚠️ 2026-08-11：目标关键词由「建业电影小镇」改为「电影小镇」（与订阅页新增订阅一致，日报主目标口径）。
旧名「建业电影小镇」关键词详情不再单独采，如需历史同比可在运行时临时改 KEYWORDS。

数据来源: https://creator.douyin.com/creator-micro/creator-count/arithmetic-index
"""
import asyncio, json, re, datetime, time, os
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:18800"
OUTPUT_JSON = "/tmp/douyin_keyword_detail.json"
LOCK = "/tmp/douyin_kw_detail.lock"
KEYWORDS = [
    "电影小镇", "万岁山武侠城", "清明上河园", "只有河南戏剧幻城",
    "郑州方特欢乐世界", "郑州海昌海洋公园", "郑州银基动物王国", "只有红楼梦戏剧幻城",
]


def parse_kw_index(text: str) -> dict:
    """从 textContent 解析：搜索指数 + 综合指数（三分解读在canvas→截图读）"""
    out = {"search_idx": {}, "synth_idx": {}, "synth_detail_note": "三分解读见tab1截图AI解读"}
    pairs = re.findall(r'同比\s*([+-]?[\d.]+%)\｜环比\s*([+-]?[\d.]+%)平均值\s*([\d,]+)', text)
    if len(pairs) >= 1:
        p = pairs[0]
        out["search_idx"] = {"同比": p[0], "环比": p[1], "平均值": p[2].replace(',', '')}
    if len(pairs) >= 2:
        p = pairs[-1]
        out["synth_idx"] = {"同比": p[0], "环比": p[1], "平均值": p[2].replace(',', '')}
    return out


def parse_guanlian(text: str) -> dict:
    """从 innerText 解析搜索关联词 TOP 20

    innerText 结构（Tab2）：
      搜索关联词 / 内容关联词
      搜索
      建业电影小镇的人也都在搜电影小镇，其中海魂衫最近搜索飙升
      关联词图谱
      ...
      关联词排名
      按关联度  按涨幅
      电影小镇 100    ← 分值(3位) 下1行是排名 1
      1
      德化街    40    ← 分值(2位) 下1行是排名 2
      2
      ...
      20
      大管家    5     ← 分值(1位)

    解析策略：
      · 扫描「关联词排名」标记之后
      · 中文词(2-10字) → 同行数字分析：
        - 2-3位：分值，i+2是排名(1位) → 跳3行
        - 1位数字：若i+2是2-3位→分值，i+2是排名 → 跳3行
        - 1位数字且i+2非分值→分值本身(如5) → 跳2行
    """
    out = {"search_related": [], "content_related_note": "见tab2截图AI解读"}
    lines = text.split('\n')

    start_idx = 0
    for i, line in enumerate(lines):
        if '关联词排名' in line:
            start_idx = i + 1
            break
    if start_idx == 0:
        return out

    i = start_idx
    while i < len(lines) and len(out["search_related"]) < 20:
        word = lines[i].strip()
        if not re.match(r'^[\u4e00-\u9fff]{2,10}$', word):
            i += 1
            continue

        n1_raw = re.sub(r'[^\d]', '', lines[i+1].strip()) if i+1 < len(lines) else ''
        n1_len = len(n1_raw)

        if n1_len >= 2:
            # 2-3位：分值，i+2是排名(1位) → 跳3行
            out["search_related"].append({"word": word, "score": int(n1_raw)})
            i += 3
        elif n1_len == 1:
            # 1位：可能是分值也可能是排名
            if i + 2 < len(lines):
                n2_raw = re.sub(r'[^\d]', '', lines[i+2].strip())
                if len(n2_raw) >= 2:
                    # i+1是排名(1位)，i+2是分值 → 跳3行
                    out["search_related"].append({"word": word, "score": int(n2_raw)})
                    i += 3
                    continue
            # i+1是分值本身（如分值<10）→ 跳2行
            out["search_related"].append({"word": word, "score": int(n1_raw)})
            i += 2
        else:
            i += 1

    return out


def parse_renqun(text: str) -> dict:
    """从 innerText 解析：地域 + 性别（年龄/兴趣→截图）"""
    out = {"region": [], "age_note": "见tab3截图AI解读",
           "gender": [], "interest_note": "见tab3截图AI解读"}
    lines = text.split('\n')

    # 省份地域（格式：排名  省份  占比%  TGI）
    i = 0
    while i < len(lines):
        if re.match(r'^\d+$', lines[i].strip()) and i+3 < len(lines):
            prov = lines[i+1].strip()
            pct = lines[i+2].strip()
            tgi = lines[i+3].strip()
            if re.match(r'^[\u4e00-\u9fff]', prov) and '%' in pct:
                out["region"].append({
                    "province": prov,
                    "pct": re.sub(r'[^\d.]', '', pct),
                    "tgi": re.sub(r'[^\d.]', '', tgi)
                })
                i += 4
                continue
        i += 1

    gender_blocks = re.findall(
        r'(男性|女性)\s+占比\s+(\d+(?:\.\d+)?%)\s+TGI\s+(\d+(?:\.\d+)?)', text)
    if gender_blocks:
        out["gender"] = [{"gender": m[0], "pct": m[1], "tgi": m[2]} for m in gender_blocks]

    return out


async def capture_all_tabs(page, keyword: str) -> dict:
    """切换三个 tab 各截一张图（供 AI 解读图表数据）"""
    screenshots = {}
    try:
        # Tab 1: 关键词指数（三分解读柱图 + 折线图）
        try:
            await page.locator('text=关键词指数').first.click()
        except Exception:
            pass  # Tab 已激活
        await asyncio.sleep(3)
        p1 = f"/tmp/douyin_kw_{keyword}_tab1.png"
        await page.screenshot(path=p1, full_page=True)
        screenshots["tab1_keyword_idx"] = p1

        # Tab 2: 关联分析（关联词图谱 + 热度趋势）
        await page.locator('text=关联分析').first.click()
        await asyncio.sleep(3)
        await page.evaluate('window.scrollBy(0, 600)')
        await asyncio.sleep(1)
        p2 = f"/tmp/douyin_kw_{keyword}_tab2.png"
        await page.screenshot(path=p2, full_page=True)
        screenshots["tab2_guanlian"] = p2

        # Tab 3: 人群分析（年龄柱图 + 兴趣柱图 + 地图）
        await page.locator('text=人群分析').first.click()
        await asyncio.sleep(3)
        p3 = f"/tmp/douyin_kw_{keyword}_tab3.png"
        await page.screenshot(path=p3, full_page=True)
        screenshots["tab3_renqun"] = p3

    except Exception as e:
        screenshots["error"] = str(e)[:80]
    return screenshots


async def crawl_one_keyword(browser, keyword: str) -> dict:
    result = {"keyword": keyword, "success": False, "error": None,
              "kw_index": {}, "guanlian": {}, "renqun": {}, "screenshots": {}}
    try:
        # 策略1：找已有 arithmetic-index Tab
        target = None
        for ctx in browser.contexts:
            for pg in ctx.pages:
                try:
                    u = pg.url
                    if u and "arithmetic-index" in u:
                        target = pg
                        print(f"  → 复用 arithmetic-index Tab: {u[:60]}")
                        break
                except: pass
                if target: break
            if target: break

        # 策略2：找空白备用 Tab
        if not target:
            for ctx in browser.contexts:
                for pg in ctx.pages:
                    try:
                        if "about:blank" in (pg.url or ""):
                            target = pg
                            print(f"  → 复用空白 Tab")
                            break
                    except: pass
                    if target: break
                if target: break

        # 策略3：新建 Tab
        if not target:
            for ctx in browser.contexts:
                target = await ctx.new_page()
                print(f"  → 新建 Tab")
                break

        if not target:
            result["error"] = "no_tab"; return result
        page = target

        await page.goto(
            "https://creator.douyin.com/creator-micro/creator-count/arithmetic-index",
            timeout=20000, wait_until="networkidle")
        await asyncio.sleep(3)
        sb = page.locator('input[placeholder*="关键词"]').first
        await sb.click(); await sb.fill(keyword)
        await page.keyboard.press("Enter")
        await asyncio.sleep(7)

        # Tab 1: textContent → 搜索/综合指数
        tc = await page.evaluate('() => document.body.textContent || ""')
        result["kw_index"] = parse_kw_index(tc)

        # 三个 tab 截图（供 AI 解读图表）
        result["screenshots"] = await capture_all_tabs(page, keyword)

        # Tab 2: innerText → 关联词（需 scroll 触发列表渲染）
        try:
            await page.locator('text=关联分析').first.click()
            await asyncio.sleep(4)
            await page.evaluate('window.scrollBy(0, 600)')
            await asyncio.sleep(2)
            t2 = await page.inner_text('body')
            result["guanlian"] = parse_guanlian(t2)
        except Exception as e:
            result["guanlian"] = {"error": str(e)[:60]}

        # Tab 3: innerText → 地域 + 性别
        try:
            await page.locator('text=人群分析').first.click()
            await asyncio.sleep(4)
            t3 = await page.inner_text('body')
            result["renqun"] = parse_renqun(t3)
        except Exception as e:
            result["renqun"] = {"error": str(e)[:60]}

        result["success"] = True
        r = result["renqun"]
        print(f"  ✓ {keyword}: "
              f"搜索={bool(result['kw_index'].get('search_idx'))} "
              f"综合={bool(result['kw_index'].get('synth_idx'))} "
              f"关联词={len(result['guanlian'].get('search_related',[]))}个 "
              f"地域={len(r.get('region',[]))}省 "
              f"性别={len(r.get('gender',[]))}")
        return result

    except Exception as e:
        result["error"] = str(e)[:100]
        print(f"  ✗ {keyword}: {e}"); return result


async def crawl():
    try:
        os.open(LOCK, os.O_CREAT | os.O_EXCL)
    except FileExistsError:
        age = time.time() - os.path.getmtime(LOCK)
        if age > 180:
            os.remove(LOCK)
            os.open(LOCK, os.O_CREAT | os.O_EXCL)
        else:
            print(f"[⏳] 已有实例({age:.0f}s)，跳过"); return None
    except: pass

    from playwright.async_api import async_playwright
    out = {"date": datetime.date.today().isoformat(),
           "crawled_at": datetime.datetime.now().isoformat(),
           "version": "v4-hybrid-final", "results": []}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.connect_over_cdp(CDP_URL, timeout=8000)
            for kw in KEYWORDS:
                r = await crawl_one_keyword(browser, kw)
                out["results"].append(r)
                await asyncio.sleep(5)
            await browser.close()
    except Exception as e:
        out["error"] = str(e)
    finally:
        try: os.remove(LOCK)
        except: pass

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    ok = sum(1 for r in out["results"] if r["success"])
    print(f"\n完成 {ok}/{len(KEYWORDS)}"); print(f"→ {OUTPUT_JSON}")
    return out


if __name__ == "__main__":
    print(f"=== 抖音关键词详情 [{time.strftime('%Y-%m-%d %H:%M')}] ===")
    asyncio.run(crawl())