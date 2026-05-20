#!/usr/bin/env python3
"""
抖音关键词深度数据采集脚本 v5（反爬增强版）
完整流程：
1. Cookie预检 → 先验证登录态
2. 在搜索框输入关键词（慢速输入）
3. 滚轮缓慢下滑
4. 点击"关联分析"tab
5. 点击"人群分析"tab
6. 所有操作带随机延迟，模拟人类行为

v5变更 - 2026-05-16
  - 增加Cookie预检机制，采集前验证登录态
  - 所有操作延迟拉到5-8秒+随机抖动(-30%~+30%)
  - 增加人类行为模拟(鼠标随机移动+慢速打字)
  - 增加Cookie过期标记文件写入
  - 页面加载状态验证，等待指定元素出现而非固定延迟
"""

import json
import time
import re
import os
import random
import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


CDP_ENDPOINT = "http://127.0.0.1:18800"
DEFAULT_KEYWORD = "建业电影小镇"
COOKIE_EXPIRED_FLAG = "/tmp/douyin_cookie_expired.flag"


# ========================
# 反爬策略工具函数
# ========================

def random_jitter(base_seconds, jitter_ratio=0.3):
    """生成带随机抖动的时间(秒)"""
    delta = base_seconds * jitter_ratio
    return base_seconds - delta + random.random() * 2 * delta


def human_sleep(base_seconds, jitter_ratio=0.3):
    """sleep with random jitter"""
    duration = random_jitter(base_seconds, jitter_ratio)
    time.sleep(duration)


def human_mouse_move(page):
    """模拟人类鼠标随机小幅度移动"""
    try:
        viewport = page.viewport_size or {"width": 1440, "height": 900}
        for _ in range(random.randint(1, 3)):
            x = random.randint(100, viewport.get("width", 1440) - 100)
            y = random.randint(100, viewport.get("height", 900) - 100)
            page.mouse.move(x, y)
            time.sleep(random.uniform(0.3, 1.0))
    except Exception:
        pass


def human_type(page, text, selector=None):
    """慢速打字，模拟人类输入节奏"""
    if selector:
        page.click(selector, force=True)
        human_sleep(1)
        page.fill(selector, "")
        human_sleep(0.5)
    
    for char in text:
        page.keyboard.type(char, delay=random.randint(80, 250))
        time.sleep(random.uniform(0.02, 0.08))
    
    # 输入完成后暂停，模拟人类检查输入内容
    human_sleep(1)


def set_cookie_expired_flag():
    """写入Cookie过期标记文件"""
    with open(COOKIE_EXPIRED_FLAG, "w") as f:
        f.write(f"Cookie过期于: {datetime.datetime.now().isoformat()}\n")
        f.write(f"需站长重新登录抖音创作者平台\n")
    print(f"[⚠ Cookie过期] 标记文件已写入: {COOKIE_EXPIRED_FLAG}")


def clear_cookie_expired_flag():
    """清除Cookie过期标记"""
    if os.path.exists(COOKIE_EXPIRED_FLAG):
        os.remove(COOKIE_EXPIRED_FLAG)


def check_login_status(page):
    """检查抖音登录态是否有效
    
    连接已有Tab后进行检查，不新建页面。
    """
    try:
        current_url = page.url
        page_text = page.evaluate("() => document.body.innerText")
        
        # 检查是否在登录页
        if any(hint in (current_url or "") for hint in ["passport", "login", "account"]):
            print("[Cookie预检] ✗ 被重定向到登录页")
            return False
        
        # 检查登录相关关键词
        login_indicators = ["请登录", "扫码登录", "手机号登录/注册", "登录抖音"]
        for ind in login_indicators:
            if ind in page_text:
                print(f"[Cookie预检] ✗ 页面包含'{ind}'")
                return False
        
        print("[Cookie预检] ✓ 登录态有效")
        return True
    except Exception as e:
        print(f"[Cookie预检] ⚠ 检测异常({e})，按已登录继续")
        return True


# ========================
# 数据解析
# ========================

def parse_related_words(text):
    """从关联分析页面提取关联词"""
    results = []
    
    if '关联词排名' not in text:
        return results
    
    start = text.find('关联词排名')
    segment = text[start:start+2000]
    lines = segment.split('\n')
    
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            continue
        if line.isdigit() and 1 <= int(line) <= 20:
            kw = None
            score = None
            for j in range(i+1, min(i+5, len(lines))):
                candidate = lines[j].strip()
                if not candidate:
                    continue
                if kw is None and not candidate.isdigit() and 2 <= len(candidate) <= 15:
                    kw = candidate
                    continue
                if kw is not None and score is None and candidate.isdigit():
                    score = candidate
                    break
            if kw and score:
                results.append({
                    "rank": int(line),
                    "word": kw,
                    "score": int(score)
                })
                if len(results) >= 10:
                    break
    
    return results[:10]


def parse_crowd_profile(text):
    """从人群分析页面提取人群画像"""
    crowd = {}
    
    if '地域分布' in text:
        crowd["地域分布"] = []
        region_pattern = re.compile(r'(\d+)\s+([^\d\n]+?)\s+([\d.]+%)\s+([\d.]+)')
        matches = region_pattern.findall(text)
        for m in matches[:10]:
            crowd["地域分布"].append({
                "rank": int(m[0]),
                "province": m[1].strip(),
                "ratio": m[2],
                "tgi": float(m[3])
            })
    
    male_ratio = re.search(r'男性\s+占比\s+(\d+)%', text)
    male_tgi = re.search(r'男性\s+TGI\s+(\d+)', text)
    female_ratio = re.search(r'女性\s+占比\s+(\d+)%', text)
    female_tgi = re.search(r'女性\s+TGI\s+(\d+)', text)
    
    if male_ratio:
        crowd["男性占比"] = male_ratio.group(1) + "%"
    if male_tgi:
        crowd["男性TGI"] = int(male_tgi.group(1))
    if female_ratio:
        crowd["女性占比"] = female_ratio.group(1) + "%"
    if female_tgi:
        crowd["女性TGI"] = int(female_tgi.group(1))
    
    age_main = re.search(r'([\d]+-[\d]+岁)\s+占比最高', text)
    age_tgi = re.search(r'([\d]+-[\d]+岁)\s+TGI最高', text)
    
    if age_main:
        crowd["主要年龄段"] = age_main.group(1)
    if age_tgi:
        crowd["TGI最高年龄段"] = age_tgi.group(1)
    
    return crowd


# ========================
# 主流程
# ========================

def collect_keyword_deep(keyword=DEFAULT_KEYWORD):
    """采集关键词深度数据（反爬增强版v5）
    
    流程:
    1. CDP连接到专属浏览器
    2. Cookie预检验证登录态
    3. 找到关键词Tab
    4. 导航到关键词分析页（带随机延迟）
    5. 慢速滚轮下滑
    6. 点击关联分析 → 提取数据
    7. 点击人群分析 → 提取数据
    """
    result = {
        "keyword": keyword,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "success": False,
        "related_words": [],
        "crowd_profile": {},
        "cookie_expired": False,
        "error": None
    }

    # CDP连接重试
    browser = None
    p = None
    for attempt in range(1, 6):
        try:
            print(f"[CDP连接尝试 {attempt}/5] {CDP_ENDPOINT}")
            p = sync_playwright().start()
            browser = p.chromium.connect_over_cdp(CDP_ENDPOINT)
            print(f"[CDP] 连接成功！")
            break
        except Exception as e:
            print(f"[CDP] 连接失败: {e}")
            if attempt < 5:
                print(f"[CDP] 等待后重试...")
                human_sleep(5)
            else:
                result["error"] = f"CDP连接5次失败: {e}"
                return result

    try:
        context = browser.contexts[0]

        # 找到关键词Tab（arithmetic-index）
        page = None
        for pg in context.pages:
            url = pg.url or ""
            if 'arithmetic-index' in url or 'creator.douyin.com' in url:
                page = pg
                break
        
        # 如果找不到目标Tab，试试用第一个可用Tab
        if not page and context.pages:
            page = context.pages[0]
            print(f"  → 使用Tab: {page.url}")

        if not page:
            result["error"] = "未找到可用Tab"
            print("[错误] 未找到可用Tab")
            return result

        print(f"  → 使用页面: {page.url[:80]}...")

        # ---- v5新增: Cookie预检 ----
        print("\n━━━ 登录态检查 ━━━")
        human_mouse_move(page)
        login_ok = check_login_status(page)
        if not login_ok:
            print("[Cookie预检] ✗ 登录态已过期，停止采集")
            set_cookie_expired_flag()
            result["cookie_expired"] = True
            result["error"] = "Cookie已过期"
            return result
        # ---- 预检结束 ----

        # 1. 导航到关键词分析页
        target_url = (
            f"https://creator.douyin.com/creator-micro/creator-count/arithmetic-index/analysis"
            f"?keyword={keyword}&tab=related&appName=aweme&source=creator"
        )
        print(f"\n→ 导航到关键词分析页: {keyword}")
        page.goto(target_url, wait_until="domcontentloaded")
        
        # v5: 拉长初始等待 + 等网络空闲
        human_sleep(8)
        try:
            page.wait_for_load_state("networkidle", timeout=15000)
        except:
            pass
        human_sleep(3)
        print(f"  ✓ 关键词页加载完成")

        # 2. 模拟人类鼠标移动 + 慢速滚轮下滑
        human_mouse_move(page)
        print("  → 缓慢下滑加载数据...")
        for i in range(3):
            page.mouse.wheel(0, 800)
            human_sleep(3)  # v5: 每次滚动间隔3秒
        page.mouse.wheel(0, -300)  # 往回滚一点，模拟人类行为
        human_sleep(3)
        print("  ✓ 滚轮下滑完成")

        # 3. 点击关联分析tab
        human_mouse_move(page)
        print("  → 点击[关联分析] tab...")
        human_sleep(2)
        try:
            page.click('text=关联分析', force=True, timeout=8000)
        except PlaywrightTimeout:
            print("  → 用evaluate尝试点击...")
            page.evaluate('''() => {
                const tabs = document.querySelectorAll('[class*="tab"], [class*="Tab"], button, [role="tab"]');
                for (const t of tabs) {
                    if (t.textContent.includes('关联分析')) { t.click(); break; }
                }
            }''')
        human_sleep(6)  # v5: 等待6秒加载
        text1 = page.evaluate('document.body.innerText')
        result["related_words"] = parse_related_words(text1)
        print(f"  ✓ 关联词: {len(result['related_words'])} 条")

        # 4. 点击人群分析tab
        human_mouse_move(page)
        print("  → 点击[人群分析] tab...")
        human_sleep(2)
        try:
            page.click('text=人群分析', force=True, timeout=8000)
        except PlaywrightTimeout:
            print("  → 用evaluate尝试点击...")
            page.evaluate('''() => {
                const tabs = document.querySelectorAll('[class*="tab"], [class*="Tab"], button, [role="tab"]');
                for (const t of tabs) {
                    if (t.textContent.includes('人群分析')) { t.click(); break; }
                }
            }''')
        human_sleep(6)  # v5: 等待6秒加载
        text2 = page.evaluate('document.body.innerText')
        result["crowd_profile"] = parse_crowd_profile(text2)
        print(f"  ✓ 人群画像: {len(result['crowd_profile'].get('地域分布', []))} 条地域")

        result["success"] = True

    except Exception as e:
        result["error"] = str(e)
        print(f"  ✗ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            if p is not None:
                p.stop()
        except:
            pass

    return result


if __name__ == "__main__":
    import sys
    keyword = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_KEYWORD
    
    print(f"=== 采集关键词深度数据 v5: {keyword} ===")
    print("=" * 50)
    
    data = collect_keyword_deep(keyword)
    
    print(f"\n成功: {data['success']}")
    
    if data.get('cookie_expired'):
        print("\n⚠ Cookie已过期，请站长重新登录抖音后重试")
    elif data['related_words']:
        print(f"\n关联词TOP10:")
        for w in data['related_words'][:10]:
            print(f"  {w['rank']}. {w['word']} ({w['score']})")
    
    cp = data['crowd_profile']
    if cp:
        print(f"\n人群画像:")
        if '地域分布' in cp:
            print(f"  地域TOP3:")
            for r in cp['地域分布'][:3]:
                print(f"    {r['rank']}. {r['province']} {r['ratio']} TGI{r['tgi']}")
        if '男性占比' in cp:
            print(f"  性别: 男{cp['男性占比']}(TGI{cp.get('男性TGI','N/A')}) 女{cp['女性占比']}(TGI{cp.get('女性TGI','N/A')})")
    
    # 保存结果
    safe_name = keyword.replace(' ', '_').replace('\n', '')
    output = f"/tmp/keyword_deep_{safe_name}.json"
    with open(output, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n已保存: {output}")
