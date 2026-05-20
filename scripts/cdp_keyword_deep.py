#!/usr/bin/env python3
"""
抖音关键词深度数据采集脚本 v4（最终版）
完整流程已验证：
1. 刷新页面
2. 在搜索框输入关键词
3. 滚轮下滑
4. 点击"关联分析"tab (force=True)
5. 点击"人群分析"tab (force=True)
"""

import json
import time
import re
from playwright.sync_api import sync_playwright

CDP_ENDPOINT = "http://127.0.0.1:18800"
DEFAULT_KEYWORD = "建业电影小镇"

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
        # 匹配排名数字
        if line.isdigit() and 1 <= int(line) <= 20:
            # 找关键词和热度
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
    
    # 地域分布
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
    
    # 性别分布
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
    
    # 年龄分布（简化）
    age_main = re.search(r'([\d]+-[\d]+岁)\s+占比最高', text)
    age_tgi = re.search(r'([\d]+-[\d]+岁)\s+TGI最高', text)
    
    if age_main:
        crowd["主要年龄段"] = age_main.group(1)
    if age_tgi:
        crowd["TGI最高年龄段"] = age_tgi.group(1)
    
    return crowd

def collect_keyword_deep(keyword=DEFAULT_KEYWORD):
    """采集关键词深度数据"""
    result = {
        "keyword": keyword,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "success": False,
        "related_words": [],
        "crowd_profile": {},
        "error": None
    }

    # CDP连接重试机制：最多尝试5次，每次间隔3秒
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
                print(f"[CDP] 3秒后重试...")
                time.sleep(3)
            else:
                result["error"] = f"CDP连接5次失败: {e}"
                return result

    try:
        context = browser.contexts[0]

        # 找到关键词Tab
        page = None
        for pg in context.pages:
            if 'arithmetic-index' in pg.url:
                page = pg
                break

        if not page:
            result["error"] = "未找到关键词Tab（arithmetic-index）"
            return result

        print(f"→ 使用现有关键词Tab")

        # 1. 在保留Tab内导航到关键词分析页
        page.goto(
            f"https://creator.douyin.com/creator-micro/creator-count/arithmetic-index/analysis"
            f"?keyword={keyword}&tab=related&appName=aweme&source=creator"
        )
        time.sleep(6)
        print(f"  ✓ 关键词页加载: {keyword}")

        # 2. 滚轮下滑，加载完整数据
        for i in range(3):
            page.mouse.wheel(0, 800)
            time.sleep(1)
        page.mouse.wheel(0, -300)
        time.sleep(2)
        print("  ✓ 滚轮下滑")

        # 4. 点击关联分析tab (force=True避免被遮挡)
        page.click('text=关联分析', force=True, timeout=5000)
        time.sleep(4)
        text1 = page.evaluate('document.body.innerText')
        result["related_words"] = parse_related_words(text1)
        print(f"  ✓ 关联词: {len(result['related_words'])} 条")

        # 5. 点击人群分析tab
        page.click('text=人群分析', force=True, timeout=5000)
        time.sleep(4)
        text2 = page.evaluate('document.body.innerText')
        result["crowd_profile"] = parse_crowd_profile(text2)
        print(f"  ✓ 人群画像: {len(result['crowd_profile'].get('地域分布', []))} 条地域")

        result["success"] = True
        if p is not None:
            p.stop()

    except Exception as e:
        result["error"] = str(e)
        print(f"  ✗ 错误: {e}")
        try:
            if p is not None:
                p.stop()
        except:
            pass

    return result

if __name__ == "__main__":
    import sys
    keyword = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_KEYWORD
    
    print(f"=== 采集关键词深度数据: {keyword} ===")
    data = collect_keyword_deep(keyword)
    
    print(f"\n成功: {data['success']}")
    
    if data['related_words']:
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
    
    # 保存
    output = f"/tmp/keyword_deep_{keyword.replace(' ', '_')}.json"
    with open(output, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"\n已保存: {output}")
