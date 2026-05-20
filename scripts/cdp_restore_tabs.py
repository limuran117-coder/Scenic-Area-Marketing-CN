#!/usr/bin/env python3
"""
CDP浏览器标签页自动恢复脚本
每次启动时检查7个固定标签页是否存在，缺失则自动恢复
"""
import json, urllib.request, asyncio, websockets

CDP_PORT = 18800
TABS = [
    ("Tab0", "https://idea.xiaohongshu.com/idea/welcome/index"),
    ("Tab1", "https://www.douyin.com/search/"),
    ("Tab2", "about:blank"),
    ("Tab3", "https://www.baidu.com/s?wd="),
    ("Tab4", "https://creator.douyin.com/creator-micro/creator-count/my-subscript"),
    ("Tab5", "https://www.xiaohongshu.com/explore"),
    ("Tab6", "https://weibo.com/"),
]

async def restore():
    try:
        req = urllib.request.Request(f'http://127.0.0.1:{CDP_PORT}/json/list')
        resp = urllib.request.urlopen(req, timeout=3)
        existing = [t.get('url','') for t in json.loads(resp.read().decode()) if t.get('type')=='page']
    except Exception as e:
        print(f"连接CDP失败: {e}")
        return False

    restored = 0
    for label, url in TABS:
        url_base = url.split('?')[0]
        if url_base not in [e.split('?')[0] for e in existing]:
            try:
                req = urllib.request.Request(f'http://127.0.0.1:{CDP_PORT}/json/new', method='PUT')
                resp = urllib.request.urlopen(req, timeout=3)
                tab = json.loads(resp.read().decode())
                ws_url = tab['webSocketDebuggerUrl']
                async with websockets.connect(ws_url) as ws:
                    cmd = json.dumps({"id": 1, "method": "Page.navigate", "params": {"url": url}})
                    await ws.send(cmd)
                    await asyncio.wait_for(ws.recv(), timeout=5)
                restored += 1
                print(f"恢复: {label} -> {url[:40]}")
            except Exception:
                pass

    if restored == 0:
        print(f"全部 {len(TABS)} 个标签页正常")
    else:
        print(f"已恢复 {restored} 个标签页")
    return True

if __name__ == "__main__":
    asyncio.run(restore())
