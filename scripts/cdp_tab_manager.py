#!/opt/homebrew/bin/python3.12
"""
CDP Tab 连接管理器
功能：根据 URL 模式在已有浏览器 Tab 中找到目标 Tab 并连接，
      找不到则新建，挂在 about:blank 上备用。
      所有脚本统一通过这个函数获取 Page，避免重复创建 Tab。

用法：
  from cdp_tab_manager import get_tab
  page = await get_tab(cdp_url, "douyin_index")  # 获取抖音指数 Tab
  page = await get_tab(cdp_url, "xhs_lingxi")    # 获取小红书灵犀 Tab
  page = await get_tab(cdp_url, "douyin_search")  # 获取抖音搜索 Tab
  page = await get_tab(cdp_url, "xhs_explore")    # 获取小红书探索 Tab
  page = await get_tab(cdp_url, "blank")         # 获取空白备用 Tab
"""
import asyncio
from playwright.async_api import async_playwright

# 固定 Tab URL 映射表（精确匹配优先，模糊匹配兜底）
TAB_TARGETS = {
    # 抖音系
    "douyin_index": {
        "urls": [
            "creator.douyin.com/creator-micro/creator-count/my-subscript",
            "creator.douyin.com/creator-micro/creator-count/arithmetic-index",
        ],
        "label": "抖音指数",
    },
    "douyin_search": {
        "urls": [
            "www.douyin.com/search/",
        ],
        "label": "抖音搜索",
    },
    # 小红书系
    "xhs_lingxi": {
        "urls": [
            "idea.xiaohongshu.com",
        ],
        "label": "小红书灵犀",
    },
    "xhs_explore": {
        "urls": [
            "www.xiaohongshu.com/explore",
        ],
        "label": "小红书探索",
    },
    "xhs_search": {
        "urls": [
            "www.xiaohongshu.com/search_result",
        ],
        "label": "小红书搜索",
    },
    # 通用备用
    "blank": {
        "urls": ["about:blank"],
        "label": "空白页",
    },
}


def _url_matches(url: str, patterns: list) -> bool:
    """判断当前 Tab URL 是否匹配目标 URL 模式列表"""
    for p in patterns:
        if p in url or url.startswith(p):
            return True
    return False


def _find_target_page(pages, tab_key: str) -> tuple:
    """在已有 pages 中找匹配的 Tab，返回 (Page, is_existing)"""
    targets = TAB_TARGETS.get(tab_key, {})
    patterns = targets.get("urls", [])
    label = targets.get("label", tab_key)

    for page in pages:
        try:
            u = page.url
            if u and _url_matches(u, patterns):
                return page, True
        except Exception:
            continue

    return None, False


async def get_tab(cdp_url: str, tab_key: str, timeout_ms: int = 8000) -> object:
    """
    获取指定用途的 CDP Page。

    策略：
      1. 遍历所有已有 Tab，找 URL 匹配的 → 复用
      2. 找不到则创建新 Tab，导航到 about:blank
      3. 返回 Page 对象，脚本直接使用 page.goto / page.locator ...

    Args:
        cdp_url:   "http://127.0.0.1:18800"
        tab_key:   TAB_TARGETS 中的键名，如 "douyin_index"、"xhs_lingxi"
        timeout_ms: 连接超时

    Returns:
        Page 对象（playwright.async_api.Page）
    """
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(cdp_url, timeout=timeout_ms)

        # 收集所有 Tab（去重）
        all_pages = []
        for ctx in browser.contexts:
            for pg in ctx.pages:
                try:
                    u = pg.url
                    if u and not u.startswith("chrome://"):
                        all_pages.append(pg)
                except Exception:
                    continue

        # 策略1：找已有匹配 Tab
        target_page, is_existing = _find_target_page(all_pages, tab_key)
        if target_page is not None:
            await target_page.bring_to_front()
            label = TAB_TARGETS.get(tab_key, {}).get("label", tab_key)
            print(f"[✓] 复用已有 Tab（{label}）: {target_page.url[:60]}")
            await browser.close()
            return target_page

        # 策略2：找「空白备用 Tab」复用
        if tab_key != "blank":
            blank_page, _ = _find_target_page(all_pages, "blank")
            if blank_page:
                await blank_page.bring_to_front()
                print(f"[+] 复用空白 Tab: {blank_page.url}")
                await browser.close()
                return blank_page

        # 策略3：创建新 Tab
        for ctx in browser.contexts:
            new_tab = await ctx.new_page()
            print(f"[+] 新建 Tab（{TAB_TARGETS.get(tab_key, {}).get('label', tab_key)}）")
            await browser.close()
            return new_tab

        #兜底
        raise RuntimeError(f"无法获取 Tab '{tab_key}'：无可用 context")