#!/opt/homebrew/bin/python3.12
"""
CDP浏览器标签页自动恢复脚本 (WebSocket 版，2026-09-11 重写)

历史问题：
  1) Playwright connect_over_cdp 在 Chrome 152 上 <ws preparing> 挂起超时
  2) HTTP PUT /json/new 在 Chrome 152 上直接挂死（即使 about:blank）

现方案：直接用 CDP WebSocket 调 Target.createTarget —— 创建标签页不等待
页面加载完成，立即返回，稳定可靠。纯 websockets 库，无 Playwright 依赖。
"""
import asyncio
import json
import urllib.request

CDP_PORT = 18800
BASE = f"http://127.0.0.1:{CDP_PORT}"

TABS = [
    ("Tab0", "https://idea.xiaohongshu.com/idea/welcome/index"),
    ("Tab1", "https://www.douyin.com/search/"),
    ("Tab2", "about:blank"),
    ("Tab3", "https://www.baidu.com/s?wd="),
    ("Tab4", "https://creator.douyin.com/creator-micro/creator-count/my-subscript"),
    ("Tab5", "https://www.xiaohongshu.com/explore"),
    ("Tab6", "https://weibo.com/"),
]

_opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def _version():
    with _opener.open(BASE + "/json/version", timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


def _list():
    with _opener.open(BASE + "/json/list", timeout=15) as r:
        return json.loads(r.read().decode("utf-8", "replace"))


async def restore():
    import websockets

    try:
        ver = _version()
    except Exception as e:
        print(f"[❌] CDP 端口 {CDP_PORT} 不可达: {e}")
        return False

    ws_url = ver.get("webSocketDebuggerUrl")
    if not ws_url:
        print("[❌] 未拿到 webSocketDebuggerUrl")
        return False

    try:
        targets = _list()
    except Exception as e:
        print(f"[❌] 无法读取标签列表: {e}")
        return False

    pages = [t for t in targets if t.get("type") == "page"]
    existing = [(t.get("url") or "").split("?")[0] for t in pages
                if (t.get("url") or "") != "about:blank"]
    has_blank = any((t.get("url") or "") == "about:blank" for t in targets)
    print(f"当前浏览器有 {len(pages)} 个页面标签")

    try:
        async with websockets.connect(ws_url, open_timeout=15, max_size=None) as ws:
            msg_id = 0

            async def send(method, params=None):
                nonlocal msg_id
                msg_id += 1
                await ws.send(json.dumps({"id": msg_id, "method": method,
                                          "params": params or {}}))
                while True:
                    raw = await asyncio.wait_for(ws.recv(), timeout=20)
                    data = json.loads(raw)
                    if data.get("id") == msg_id:
                        return data

            restored, failed = 0, 0
            for label, target in TABS:
                base = target.split("?")[0]
                if base == "about:blank":
                    if has_blank:
                        continue
                elif base in existing:
                    continue

                try:
                    resp = await send("Target.createTarget", {"url": target})
                    if resp.get("result", {}).get("targetId"):
                        restored += 1
                        has_blank = has_blank or base == "about:blank"
                        print(f"恢复: {label} -> {target[:50]}")
                    else:
                        failed += 1
                        print(f"恢复 {label} 失败: {resp.get('error')}")
                except Exception as e:
                    failed += 1
                    print(f"恢复 {label} 失败: {e}")

    except Exception as e:
        print(f"[❌] CDP WebSocket 连接失败: {e}")
        return False

    if restored == 0 and failed == 0:
        print(f"✅ 全部 {len(TABS)} 个标签页正常")
    elif failed == 0:
        print(f"✅ 已恢复 {restored} 个标签页")
    else:
        print(f"⚠️ 已恢复 {restored} 个，失败 {failed} 个")
    return failed == 0


if __name__ == "__main__":
    ok = asyncio.run(restore())
    raise SystemExit(0 if ok else 1)
