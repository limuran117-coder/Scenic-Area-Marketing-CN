#!/opt/homebrew/bin/python3.12
"""
Day 25 探针: XHR 拦截 (方式C)
- 拦截 page.on('request', ...) 抓所有 XHR/fetch
- 找包含 search_index / info_index 的 API 路径
- 抓 payload / response 验证是否含原始数据

Day 24 决策 D-025:
  - 方式A (innerText) 永久失败
  - 方式B (SVG) 永久失败
  - 方式C (XHR) 是最后可行路径 — 如失败则冻结 baidu 项目
"""
import asyncio, json
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:18800"
KEYWORD = "清明上河园"
# 百度指数常见 API 路径 (Day 6 文档 + 经验)
TARGET_PATH_HINTS = ["search", "index", "trend", "api/index", "v2/index", "word"]

xhr_log = []  # 收集所有 XHR 请求


async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        ctx = browser.contexts[0] if browser.contexts else await browser.new_context()
        page = await ctx.new_page()

        # ── 拦截 XHR 请求 ─────────────────────────────
        def on_request(req):
            rtype = req.resource_type
            url = req.url
            if rtype in ("xhr", "fetch"):
                xhr_log.append({
                    "type": rtype,
                    "method": req.method,
                    "url": url,
                    "headers": dict(req.headers),
                    "post_data": req.post_data,
                })

        def on_response(resp):
            url = resp.url
            rtype = resp.request.resource_type
            if rtype in ("xhr", "fetch"):
                # 标记 response 状态码
                for item in reversed(xhr_log):
                    if item["url"] == url and "status" not in item:
                        item["status"] = resp.status
                        try:
                            body = resp.body()
                            item["body_len"] = len(body)
                            # 尝试解码为 UTF-8 文本（前 2000 字节）
                            try:
                                item["body_preview"] = body[:2000].decode("utf-8", errors="replace")
                            except Exception:
                                item["body_preview"] = "(binary)"
                        except Exception as e:
                            item["body_error"] = str(e)
                        break

        page.on("request", on_request)
        page.on("response", on_response)

        try:
            # ── 阶段 1: 直接 goto hash URL (Day 23 已验证这是登录态恢复方式) ──
            print(f"📡 stage 1: 直接 goto hash URL (Day 23 验证方式)")
            await page.goto(
                f"https://index.baidu.com/v2/main/index.html#/trend/{KEYWORD}",
                wait_until="networkidle",
                timeout=30000,
            )
            t1_title = await page.title()
            t1_url = page.url
            print(f"  title={t1_title!r}  url={t1_url}")

            # ── 阶段 2: 等 8s 让数据 fetch + 渲染 ──
            n_before = len(xhr_log)
            print(f"⏳ stage 2: 等待 8s (XHR 起点={n_before})")
            await page.wait_for_timeout(8000)
            n_after = len(xhr_log)
            print(f"  XHR 触发: {n_after - n_before} 个 (累计 {n_after})")

            # ── 阶段 3: 多等 5s + 模拟滚动 + 鼠标移动 (触发懒加载) ──
            print(f"⏳ stage 3: 模拟滚动 + 等待 5s")
            try:
                await page.mouse.move(500, 500)
                await page.evaluate("window.scrollTo(0, 200)")
                await page.wait_for_timeout(2000)
                await page.evaluate("window.scrollTo(0, 0)")
            except Exception:
                pass
            await page.wait_for_timeout(5000)
            n_final = len(xhr_log)
            print(f"  XHR 总数: {n_final}")

            # ── 阶段 4: 还要看下 body_text 是不是真的 0 ──
            text_len = await page.evaluate("document.body.innerText.length")
            body_text_sample = await page.evaluate(
                "document.body.innerText.slice(0, 500)"
            )

            # ── 阶段 5: 筛选 XHR ──
            api_hits = [
                x for x in xhr_log
                if any(h in x["url"].lower() for h in TARGET_PATH_HINTS)
            ]
            all_xhr = list(xhr_log)

            # 找含"指数"等关键词的 response body
            data_hits = []
            for x in xhr_log:
                preview = x.get("body_preview", "")
                if any(k in preview for k in ["search", "index", "trend", "data", "result"]):
                    data_hits.append({
                        "url": x["url"],
                        "status": x.get("status"),
                        "body_len": x.get("body_len"),
                        "body_preview": preview[:600],
                    })

            report = {
                "stage1": {"title": t1_title, "url": t1_url, "xhr_count": n_before},
                "stage2": {"xhr_after_8s": n_after, "xhr_during_8s_wait": n_after - n_before},
                "stage3": {"xhr_final": n_final, "xhr_during_scroll": n_final - n_after},
                "dom_check": {
                    "body_text_len": text_len,
                    "body_text_sample": body_text_sample,
                },
                "xhr_summary": {
                    "total": len(all_xhr),
                    "api_keyword_hits": len(api_hits),
                    "data_keyword_hits": len(data_hits),
                },
                "api_hits_url_list": [x["url"] for x in api_hits[:30]],
                "data_hits": data_hits[:5],  # 最多 5 个, 避免输出过大
                "all_xhr_url_list": [x["url"] for x in all_xhr[:50]],
            }
            print("=" * 60)
            print(json.dumps(report, ensure_ascii=False, indent=2))
            print("=" * 60)

            # ── 决策输出 ──
            print()
            print("=" * 60)
            print("📋 决策建议 (自动分析):")
            if len(data_hits) >= 1:
                print(f"  ✅ 方式C 可行: 找到 {len(data_hits)} 个含数据的 XHR 响应")
                print(f"  → 建议 Day 26: 解析 data_hits[0] 提取 search_index")
            elif len(api_hits) >= 3:
                print(f"  🟡 方式C 部分可行: {len(api_hits)} 个 API 路径, 但未在 response body 中找到目标数据")
                print(f"  → 建议 Day 26: 抓包 body 看是否加密, 检查 api_hits_url_list")
            else:
                print(f"  ❌ 方式C 不可行: 仅 {len(all_xhr)} 个 XHR, 没有命中指数 API")
                print(f"  → 建议: 冻结 baidu adapter, 转向 visitors CSV 零值修复")
            print("=" * 60)
            # ── 如果 XHR 极少, 进一步诊断: 登录态? ──
            if n_final <= 5:
                print()
                print("🟡 深度诊断: XHR 极少, 可能登录态失效")
                try:
                    cookies = await ctx.cookies()
                    baidu_cookies = [c for c in cookies if "baidu.com" in c.get("domain", "")]
                    print(f"  baidu.com 域 cookie 数: {len(baidu_cookies)}")
                    for c in baidu_cookies[:5]:
                        print(f"    {c['name']} = {c['value'][:30]}... (expires={c.get('expires', -1)})")
                except Exception as e:
                    print(f"  cookie 读失败: {e}")

        finally:
            await page.close()


asyncio.run(main())
