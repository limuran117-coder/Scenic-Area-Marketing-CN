#!/opt/homebrew/bin/python3.12
"""
CDP轻量采集脚本
通过Chrome调试端口连接已有Chrome窗口，刷新页面并采集数据
窗口常开，不产生daemon进程

用法：
1. 首次：手动打开Chrome：Google\ Chrome --remote-debugging-port=9222 --user-data-dir=$HOME/Library/Application\ Support/Google/Chrome/DevToolsActivePort
2. 手动设置3个tab：抖音订阅页、抖音关键词页、小红书
3. 每日采集：python3 cdp_collector.py
"""

import json
import datetime
import time
import re
import sys
import os

# CDP连接配置
CDP_PORT = 9222
CDP_URL = f"http://127.0.0.1:{CDP_PORT}/json"

# 采集目标URL
TAB1_URL = "https://creator.douyin.com/creator-micro/creator-count/my-subscript?source=creator"  # 抖音订阅
TAB2_URL = "https://creator.douyin.com/creator-micro/creator-count/arithmetic-index"  # 抖音关键词

def parse_number(text):
    """从文本中解析数字"""
    match = re.search(r'([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0

def parse_page_text(text, spot_name):
    """从页面文本中解析指定景区的数据"""
    data = {
        "name": spot_name,
        "search": 0,
        "synth": 0,
        "search_trend": "",
        "synth_trend": ""
    }
    
    if spot_name not in text:
        return data
    
    lines = text.split('\n')
    
    for i, line in enumerate(lines):
        if spot_name not in line:
            continue
        
        for j in range(i+1, min(i+20, len(lines))):
            current = lines[j].strip()
            
            # 搜索指数
            if '搜索指数' in current:
                for k in range(j+1, min(j+5, len(lines))):
                    val = lines[k].strip()
                    if '有异动' in val:
                        continue
                    n = parse_number(val)
                    if n > 0:
                        data["search"] = n
                        break
            
            # 综合指数
            if '综合指数' in current:
                for k in range(j+1, min(j+5, len(lines))):
                    val = lines[k].strip()
                    if '有异动' in val:
                        continue
                    n = parse_number(val)
                    if n > 0:
                        data["synth"] = n
                        break
            
            # 日环比
            if '日环比' in current:
                trend = lines[j+1].strip() if j+1 < len(lines) else ''
                if '%' in trend:
                    if data["search"] > 0 and data["synth"] == 0:
                        data["search_trend"] = trend
                    elif data["search"] > 0 and data["synth"] > 0:
                        data["synth_trend"] = trend
    
    return data

def get_chrome_tabs():
    """获取Chrome已打开的Tab"""
    import urllib.request
    import urllib.error
    
    try:
        with urllib.request.urlopen(CDP_URL, timeout=5) as resp:
            tabs = json.loads(resp.read())
        return tabs
    except Exception as e:
        print(f"[错误] 无法连接到Chrome调试端口: {e}")
        print(f"[提示] 请确保Chrome已启动：Google Chrome --remote-debugging-port={CDP_PORT}")
        return []

def activate_or_create_tab(tab_url, tabs):
    """激活已有Tab或创建新Tab"""
    import urllib.request
    import urllib.error
    
    # 查找已存在的Tab
    for tab in tabs:
        if tab.get('url', '').startswith(tab_url.split('?')[0]):
            # 找到匹配的Tab，激活它
            try:
                req = urllib.request.Request(
                    f"http://127.0.0.1:{CDP_PORT}/json/activate/{tab['id']}",
                    method='POST'
                )
                with urllib.request.urlopen(req, timeout=5) as resp:
                    print(f"  [Tab] 已激活已有Tab: {tab_url}")
                    return tab
            except Exception as e:
                print(f"  [Tab] 激活失败: {e}")
    
    # 没找到，创建新Tab
    try:
        req = urllib.request.Request(
            f"http://127.0.0.1:{CDP_PORT}/json/new",
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            new_tab = json.loads(resp.read())
            # 导航到目标URL
            import websocket
            ws_url = new_tab.get('webSocketDebuggerUrl')
            if ws_url:
                ws = websocket.create_connection(ws_url, timeout=10)
                # 发送Page.navigate命令
                navigate_cmd = json.dumps({
                    "id": 1,
                    "method": "Page.navigate",
                    "params": {"url": tab_url}
                })
                ws.send(navigate_cmd)
                ws.close()
            print(f"  [Tab] 已创建新Tab: {tab_url}")
            return new_tab
    except Exception as e:
        print(f"  [Tab] 创建失败: {e}")
        return None

def refresh_and_collect(tab_url, spot_keywords):
    """刷新Tab并采集数据"""
    import urllib.request
    import websocket
    import json
    
    tabs = get_chrome_tabs()
    if not tabs:
        return None
    
    # 找到目标Tab
    target_tab = None
    for tab in tabs:
        if tab_url.split('?')[0] in tab.get('url', ''):
            target_tab = tab
            break
    
    if not target_tab:
        print(f"  [错误] 未找到Tab: {tab_url}")
        return None
    
    ws_url = target_tab.get('webSocketDebuggerUrl')
    if not ws_url:
        print(f"  [错误] 无法获取WebSocket URL")
        return None
    
    try:
        # 连接CDP
        ws = websocket.create_connection(ws_url, timeout=15)
        
        # 刷新页面
        refresh_cmd = json.dumps({
            "id": 1,
            "method": "Page.navigate",
            "params": {"url": tab_url}
        })
        ws.send(refresh_cmd)
        time.sleep(5)  # 等待页面加载
        
        # 等待networkidle
        idle_cmd = json.dumps({
            "id": 2,
            "method": "Network.enable"
        })
        ws.send(idle_cmd)
        time.sleep(3)
        
        # 获取页面文本
        content_cmd = json.dumps({
            "id": 3,
            "method": "Runtime.evaluate",
            "params": {"expression": "document.body.innerText"}
        })
        ws.send(content_cmd)
        
        result = ws.recv()
        ws.close()
        
        # 解析结果
        if result:
            try:
                data = json.loads(result)
                if 'result' in data and 'result' in data['result']:
                    return data['result']['result']['value']
            except:
                pass
        return None
        
    except Exception as e:
        print(f"  [错误] CDP采集失败: {e}")
        return None

def main():
    print("=" * 50)
    print("CDP轻量采集")
    print(f"连接端口: {CDP_PORT}")
    print("=" * 50)
    
    # 检查Chrome连接
    tabs = get_chrome_tabs()
    if not tabs:
        sys.exit(1)
    
    print(f"当前打开的Tab数: {len(tabs)}")
    for t in tabs[:5]:
        print(f"  - {t.get('title', '?')[:50]} | {t.get('url', '?')[:60]}")
    
    print("\n[1/2] 采集抖音订阅页数据...")
    
    # 采集抖音订阅页
    SCENIC_SPOTS = [
        "建业电影小镇",
        "万岁山武侠城",
        "清明上河园",
        "只有河南戏剧幻城",
        "郑州方特欢乐世界",
        "郑州海昌海洋公园",
        "郑州银基动物王国",
        "只有红楼梦戏剧幻城"
    ]
    
    # 这里简化处理，实际使用时需要通过 CDP 采集
    print("  [提示] 请通过 browser-use 工具操作已打开的Chrome窗口")
    print("  CDP脚本待完整实现（需要websocket-client库）")

if __name__ == "__main__":
    main()
