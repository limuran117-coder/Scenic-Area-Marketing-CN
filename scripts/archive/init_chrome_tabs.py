#!/opt/homebrew/bin/python3.12
"""
初始化专用Chrome（3个Tab常开）
- 启动Chrome（调试端口9222）
- 打开3个Tab
- 保持窗口常开

使用方法：
1. 先杀掉现有Chrome进程（避免冲突）
2. 运行脚本
3. 在打开的Chrome中登录3个页面
4. 关闭窗口即停止，后续用采集脚本连9222端口
"""

import subprocess
import time
import sys

CHROME_PATH = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
PROFILE_DIR = "/tmp/douyin_xhs_chrome_profile"
PORT = 9222

TABS = [
    "https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator",
    "https://creator.douyin.com/creator-micro/creator-count/arithmetic-index",
    "https://www.xiaohongshu.com"
]

def kill_chrome_with_profile():
    """杀掉占用profile的Chrome进程"""
    try:
        # 杀掉使用该profile目录的Chrome
        subprocess.run(
            ["pkill", "-9", "-f", f"user-data-dir={PROFILE_DIR}"],
            capture_output=True, timeout=5
        )
        time.sleep(1)
        print("[清理] 已杀掉占用Profile的Chrome进程")
    except:
        pass

def main():
    print("=" * 50)
    print("初始化专用Chrome（3个Tab常开）")
    print("=" * 50)
    
    # 创建profile目录
    subprocess.run(["mkdir", "-p", PROFILE_DIR], check=True)
    
    # 杀掉占用端口和profile的进程
    print("[1/3] 清理残留进程...")
    kill_chrome_with_profile()
    subprocess.run(
        ["lsof", "-ti", f":{PORT}"],
        capture_output=True, timeout=5
    ).stdout and subprocess.run(
        ["xargs", "-I{}", "kill", "-9", "{}"],
        input=subprocess.run(["lsof", "-ti", f":{PORT}"], capture_output=True).stdout,
        timeout=5
    )
    time.sleep(1)
    
    # 启动Chrome
    print(f"[2/3] 启动Chrome（调试端口:{PORT}）...")
    chrome_cmd = [
        CHROME_PATH,
        f"--user-data-dir={PROFILE_DIR}",
        f"--remote-debugging-port={PORT}",
        "--no-first-run",
        "--no-default-browser-check",
        "--new-window",
    ]
    
    proc = subprocess.Popen(
        chrome_cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print(f"    Chrome PID: {proc.pid}")
    time.sleep(3)  # 等待Chrome完全启动
    
    # 用 CDP 打开3个Tab
    print("[3/3] 打开3个Tab...")
    import urllib.request
    import json
    
    for i, url in enumerate(TABS, 1):
        try:
            req = urllib.request.Request(
                f"http://127.0.0.1:{PORT}/json/new",
                method='POST'
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                new_tab = json.loads(resp.read())
                tab_id = new_tab.get('id', '')
                title = new_tab.get('title', '?')
                print(f"    Tab{i}: {url[:50]}...")
        except Exception as e:
            print(f"    Tab{i}: 打开失败 - {e}")
    
    print("")
    print("=" * 50)
    print("✅ Chrome已启动，3个Tab已打开！")
    print("=" * 50)
    print("请在Chrome窗口中登录3个页面：")
    print("  Tab1: 抖音订阅页（需登录抖音创作者账号）")
    print("  Tab2: 抖音关键词页（同上）")
    print("  Tab3: 小红书（如需登录）")
    print("")
    print(f"调试端口: {PORT}")
    print(f"Profile目录: {PROFILE_DIR}")
    print("")
    print("登录完成后关闭窗口即可")
    print("（后续采集用脚本连接端口9222，复用登录状态）")
    print("=" * 50)

if __name__ == "__main__":
    main()
