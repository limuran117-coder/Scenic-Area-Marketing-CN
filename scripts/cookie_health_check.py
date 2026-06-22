#!/opt/homebrew/bin/python3.12
"""
Cookie 健康检查脚本（2026-06-22 W26 新增）
- 验证 /tmp/juLiang_cookies.json + /tmp/xiaohongshu_cookies.json 是否新鲜+有效
- 验证 CDP 18800 端口可达
- 验证 7897 代理（如果存在）可达
- 验证关键域名 Cookie 是否携带 (douyin.com / xiaohongshu.com)

用法:
  python3 scripts/cookie_health_check.py          # 完整探测
  python3 scripts/cookie_health_check.py --quiet  # 只在异常时输出

退出码:
  0 = 全部健康
  1 = 任一异常（建议立即人工干预）
"""
import argparse
import json
import os
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

import urllib.request
import urllib.error

COOKIE_FILES = {
    "douyin": "/tmp/juLiang_cookies.json",
    "xiaohongshu": "/tmp/xiaohongshu_cookies.json",
}
CDP_PORT = 18800
PROXY_PORT = 7897
FRESHNESS_HOURS = 6  # cookie 文件超过 6h 未更新视为陈旧

# 关键域名（用于探测 Cookie 有效性）
TEST_DOMAINS = {
    "douyin": "https://creator.douyin.com/creator-micro/creator-count/my-subscript",
    "xiaohongshu": "https://idea.xiaohongshu.com/idea/welcome/index",
}


def check_file_fresh(path: str) -> dict:
    """检查 cookie 文件存在性 + 新鲜度"""
    p = Path(path)
    if not p.exists():
        return {"ok": False, "reason": f"文件不存在: {path}"}
    stat = p.stat()
    age_hours = (time.time() - stat.st_mtime) / 3600
    return {
        "ok": True,
        "path": path,
        "size_kb": round(stat.st_size / 1024, 1),
        "age_hours": round(age_hours, 2),
        "fresh": age_hours < FRESHNESS_HOURS,
        "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
    }


def check_cdp(port: int) -> dict:
    """检查 CDP 端口可达"""
    import socket
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=3) as s:
            return {"ok": True, "port": port, "status": "LISTEN"}
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        return {"ok": False, "port": port, "error": str(e)}


def check_proxy(port: int) -> dict:
    """检查代理端口可达 + 能访问外部"""
    import socket
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=2) as s:
            proxy_ok = True
    except Exception as e:
        return {"ok": False, "port": port, "status": "代理进程不存在", "error": str(e)}
    # 代理进程存在，测是否能联通外网
    try:
        proxy_url = f"http://127.0.0.1:{port}"
        req = urllib.request.Request("https://www.baidu.com")
        proxy_handler = urllib.request.ProxyHandler({"http": proxy_url, "https": proxy_url})
        opener = urllib.request.build_opener(proxy_handler)
        opener.open(req, timeout=8).read(100)
        return {"ok": True, "port": port, "external": "可达"}
    except Exception as e:
        return {"ok": False, "port": port, "status": "进程在但外网不通", "error": str(e)}


def check_cookie_valid(cookie_path: str, test_url: str) -> dict:
    """用 cookie 文件访问关键域名，验证 session 有效"""
    try:
        with open(cookie_path) as f:
            cookies = json.load(f)
        # 解析成 Cookie 头
        cookie_pairs = []
        if isinstance(cookies, list):
            for c in cookies:
                if isinstance(c, dict):
                    name = c.get("name")
                    value = c.get("value")
                    if name and value:
                        cookie_pairs.append(f"{name}={value}")
        elif isinstance(cookies, dict):
            for name, value in cookies.items():
                cookie_pairs.append(f"{name}={value}")
        cookie_header = "; ".join(cookie_pairs)
        # 构造请求
        req = urllib.request.Request(test_url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Cookie": cookie_header,
        })
        try:
            resp = urllib.request.urlopen(req, timeout=10)
            # 看是否有重定向到登录页
            final_url = resp.geturl()
            body_snippet = resp.read(2000).decode("utf-8", errors="replace")
            login_keywords = ["登录", "login", "扫码", "请先登录", "passport"]
            is_login_page = any(kw in body_snippet for kw in login_keywords)
            return {
                "ok": not is_login_page,
                "url": test_url,
                "final_url": final_url,
                "login_page_detected": is_login_page,
                "cookies_count": len(cookie_pairs),
            }
        except urllib.error.HTTPError as e:
            return {"ok": False, "url": test_url, "http_error": e.code, "reason": str(e)}
    except Exception as e:
        return {"ok": False, "url": test_url, "error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--quiet", action="store_true", help="只在异常时输出")
    args = parser.parse_args()

    issues = []
    report = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"), "checks": {}}

    # 1. Cookie 文件新鲜度
    for name, path in COOKIE_FILES.items():
        r = check_file_fresh(path)
        report["checks"][f"file_{name}"] = r
        if not r.get("ok"):
            issues.append(f"❌ {name} cookie 文件: {r.get('reason')}")
        elif not r.get("fresh"):
            issues.append(f"⚠️ {name} cookie 陈旧 ({r.get('age_hours')}h 前回写，阈值 {FRESHNESS_HOURS}h)")

    # 2. CDP
    cdp = check_cdp(CDP_PORT)
    report["checks"]["cdp_18800"] = cdp
    if not cdp["ok"]:
        issues.append(f"❌ CDP {CDP_PORT}: {cdp.get('error')}")

    # 3. Proxy (可选，7897 经常挂但不影响 CDP 采集)
    proxy = check_proxy(PROXY_PORT)
    report["checks"]["proxy_7897"] = proxy
    if not proxy["ok"]:
        # 代理挂不一定是问题（不一定需要），但要提醒
        report["proxy_warning"] = f"⚠️ 代理 7897: {proxy.get('status', proxy.get('error'))}（如脚本走 CDP 直连则无影响）"

    # 4. Cookie 有效性
    for name, url in TEST_DOMAINS.items():
        cookie_path = COOKIE_FILES[name]
        if not Path(cookie_path).exists():
            continue
        r = check_cookie_valid(cookie_path, url)
        report["checks"][f"cookie_valid_{name}"] = r
        if r.get("login_page_detected"):
            issues.append(f"🚨 {name} cookie 已失效（跳转到登录页）")

    # 输出
    if not args.quiet or issues:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        print()
        if issues:
            print("⚠️ 健康问题：")
            for i in issues:
                print(f"  {i}")
            if report.get("proxy_warning"):
                print(f"  {report['proxy_warning']}")
            return 1
        else:
            print("✅ 全部 Cookie/CDP 健康")
            return 0
    else:
        return 0


if __name__ == "__main__":
    sys.exit(main())