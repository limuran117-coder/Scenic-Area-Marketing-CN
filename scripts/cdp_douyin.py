#!/opt/homebrew/bin/python3.12
"""
CDP采集脚本（纯标准库，无外部依赖）
通过Chrome远程调试端口连接已有Chrome窗口

使用前提：
Chrome需要带 --remote-debugging-port=9222 启动
启动命令：
open -a "Google Chrome" --args --remote-debugging-port=9222 --user-data-dir=$HOME/Library/Application\ Support/Google\ Chrome

采集完成后浏览器窗口保持打开（不关闭）
"""

import json
import urllib.request
import urllib.error
import time
import re
import sys
import os

CDP_HOST = "127.0.0.1"
CDP_PORT = 9222
BASE_URL = f"http://{CDP_HOST}:{CDP_PORT}"

TARGET_TAB_PATTERN = "creator.douyin.com/creator-micro/creator-count/my-subscript"

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

def parse_number(text):
    match = re.search(r'([\d,]+)', text)
    if match:
        return int(match.group(1).replace(',', ''))
    return 0

def parse_page_text(text, spot_name):
    data = {"name": spot_name, "search": 0, "synth": 0, "search_trend": "", "synth_trend": ""}
    if spot_name not in text:
        return data
    
    lines = text.split('\n')
    for i, line in enumerate(lines):
        if spot_name not in line:
            continue
        for j in range(i+1, min(i+20, len(lines))):
            current = lines[j].strip()
            
            if '搜索指数' in current:
                for k in range(j+1, min(j+5, len(lines))):
                    val = lines[k].strip()
                    if '有异动' in val:
                        continue
                    n = parse_number(val)
                    if n > 0:
                        data["search"] = n
                        break
            
            if '综合指数' in current:
                for k in range(j+1, min(j+5, len(lines))):
                    val = lines[k].strip()
                    if '有异动' in val:
                        continue
                    n = parse_number(val)
                    if n > 0:
                        data["synth"] = n
                        break
            
            if '日环比' in current:
                trend = lines[j+1].strip() if j+1 < len(lines) else ''
                if '%' in trend:
                    if data["search"] > 0 and data["synth"] == 0:
                        data["search_trend"] = trend
                    elif data["search"] > 0 and data["synth"] > 0:
                        data["synth_trend"] = trend
    return data

def cdp_ws_send_recv(ws_url, commands):
    """通过WebSocket发送CDP命令并接收响应"""
    import http.client
    import urllib.parse
    
    # 解析WebSocket URL
    parsed = urllib.parse.urlparse(ws_url)
    host_port = parsed.netloc.split(':')
    host = host_port[0]
    port = int(host_port[1]) if len(host_port) > 1 else 443
    
    # 升级到WebSocket
    conn = http.client.HTTPConnection(host, port)
    path = parsed.path
    if parsed.query:
        path += '?' + parsed.query
    
    # WebSocket握手
    key = "SmF2YVNjcmlwdA=="
    headers = {
        "Upgrade": "websocket",
        "Connection": "Upgrade",
        "Sec-WebSocket-Key": key,
        "Sec-WebSocket-Version": "13"
    }
    conn.request("GET", path, headers=headers)
    resp = conn.getresponse()
    
    if resp.status != 101:
        print(f"WebSocket握手失败: {resp.status}")
        conn.close()
        return []
    
    # 接收所有响应
    results = []
    import struct
    
    while True:
        try:
            data = conn.sock.recv(4096)
            if not data:
                break
            # 解析WebSocket帧（简化处理）
            # 实际使用时用 websocket 库更可靠
            break
        except:
            break
    
    conn.close()
    return results

def get_tabs():
    """获取所有Chrome Tab"""
    try:
        req = urllib.request.Request(f"{BASE_URL}/json", headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        print(f"[错误] 无法连接到Chrome调试端口: {e}")
        print(f"[提示] 请确保Chrome已启动并开启调试：")
        print(f"       open -a 'Google Chrome' --args --remote-debugging-port={CDP_PORT}")
        return []

def find_target_tab(tabs, url_pattern):
    """查找匹配的Tab"""
    for tab in tabs:
        if url_pattern in tab.get('url', ''):
            return tab
    return None

def activate_tab(tab_id):
    """激活指定Tab"""
    try:
        req = urllib.request.Request(
            f"{BASE_URL}/json/activate/{tab_id}",
            method='POST',
            headers={"Content-Length": "0"}
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            return True
    except Exception as e:
        print(f"[警告] 激活Tab失败: {e}")
        return False

def send_cdp_command(ws_url, method, params=None, cmd_id=1):
    """通过CDP WebSocket发送命令"""
    try:
        import http.client
        import urllib.parse
        import threading
        import queue
        
        parsed = urllib.parse.urlparse(ws_url)
        host_port = parsed.netloc.split(':')
        host = host_port[0]
        port = int(host_port[1]) if len(host_port) > 1 else 443
        
        result_queue = queue.Queue()
        
        def ws_communicate():
            try:
                conn = http.client.HTTPSConnection(host, port, timeout=10)
                path = parsed.path
                if parsed.query:
                    path += '?' + parsed.query
                
                key = "dGhlIHNhbXBsZSBub25jZQ=="
                headers = {
                    "Upgrade": "websocket",
                    "Connection": "Upgrade",
                    "Sec-WebSocket-Key": key,
                    "Sec-WebSocket-Version": "13",
                    "Origin": f"http://{host}:{port}"
                }
                conn.request("GET", path, headers=headers)
                resp = conn.getresponse()
                
                if resp.status != 101:
                    result_queue.put(None)
                    conn.close()
                    return
                
                # 发送CDP命令
                cmd = json.dumps({"id": cmd_id, "method": method, "params": params or {}})
                
                # WebSocket帧 - 文本帧
                payload = cmd.encode('utf-8')
                frame = bytearray()
                frame.append(0x81)  # FIN + 文本帧
                if len(payload) < 126:
                    frame.append(len(payload))
                elif len(payload) < 65536:
                    frame.append(0x7E)
                    frame.extend(struct.pack(">H", len(payload)))
                else:
                    frame.append(0x7F)
                    frame.extend(struct.pack(">Q", len(payload)))
                frame.extend(payload)
                
                conn.sock.sendall(bytes(frame))
                
                # 接收响应
                data = b''
                while True:
                    try:
                        chunk = conn.sock.recv(8192)
                        if not chunk:
                            break
                        data += chunk
                        # 简单检查：找到结果就停止
                        if b'"result"' in data or b'"error"' in data:
                            break
                    except:
                        break
                
                conn.close()
                
                # 解析结果
                if data:
                    text = data.decode('utf-8', errors='ignore')
                    # 找JSON对象
                    start = text.find('{')
                    end = text.rfind('}') + 1
                    if start >= 0 and end > start:
                        result = json.loads(text[start:end])
                        result_queue.put(result)
                        return
                
                result_queue.put(None)
            except Exception as e:
                result_queue.put(None)
        
        t = threading.Thread(target=ws_communicate)
        t.daemon = True
        t.start()
        t.join(timeout=12)
        
        if not result_queue.empty():
            return result_queue.get()
        return None
        
    except Exception as e:
        print(f"[错误] CDP通信失败: {e}")
        return None

import struct

def collect_from_page(ws_url, page_text=None):
    """从页面收集文本（通过Runtime.evaluate）"""
    # 注入一个脚本返回页面文本
    result = send_cdp_command(ws_url, "Runtime.evaluate", {
        "expression": "document.body ? document.body.innerText : ''",
        "returnByValue": True
    }, cmd_id=1)
    
    if result and 'result' in result and 'result' in result['result']:
        return result['result']['result']['value']
    return page_text or ""

def collect_douyin_data():
    """采集抖音指数数据"""
    print("\n" + "=" * 50)
    print("CDP 抖音指数采集")
    print(f"Chrome调试端口: {BASE_URL}")
    print("=" * 50)
    
    # 获取Tab列表
    tabs = get_tabs()
    if not tabs:
        print("[错误] 无法获取Chrome Tab列表")
        return None
    
    print(f"\n当前打开的Tab数量: {len(tabs)}")
    
    # 找到抖音订阅Tab
    target_tab = find_target_tab(tabs, TARGET_TAB_PATTERN)
    
    if not target_tab:
        print(f"[错误] 未找到抖音订阅Tab（{TARGET_TAB_PATTERN}）")
        print("请手动打开：https://creator.douyin.com/creator-micro/creator-count/my-subscript")
        return None
    
    print(f"\n[Tab] 找到目标Tab: {target_tab.get('title', '?')}")
    
    # 激活Tab
    activate_tab(target_tab['id'])
    
    # 获取CDP WebSocket
    ws_url = target_tab.get('webSocketDebuggerUrl')
    if not ws_url:
        print("[错误] 无法获取WebSocket URL")
        return None
    
    # 刷新页面
    print("[Tab] 刷新页面...")
    send_cdp_command(ws_url, "Page.navigate", {"url": TARGET_TAB_PATTERN.replace("creator-micro/creator-count/", "")})
    time.sleep(5)  # 等待页面加载
    
    # 采集页面文本
    print("[采集] 获取页面文本...")
    page_text = collect_from_page(ws_url)
    
    if not page_text:
        print("[错误] 无法获取页面内容")
        return None
    
    # 解析数据
    today = time.strftime("%Y-%m-%d")
    result = {
        "date": today,
        "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "competitors": [],
        "data_url": TARGET_TAB_PATTERN
    }
    
    print("\n[解析] 解析景区数据...")
    for spot in SCENIC_SPOTS:
        spot_data = parse_page_text(page_text, spot)
        if spot_data["search"] > 0 or spot_data["synth"] > 0:
            result["competitors"].append(spot_data)
            print(f"  ✅ {spot}: 搜索={spot_data['search']}, 综合={spot_data['synth']}")
        else:
            print(f"  ⚠️  {spot}: 未找到数据")
    
    return result

if __name__ == "__main__":
    result = collect_douyin_data()
    if result:
        output_file = "/tmp/crawl_data.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 数据已保存: {output_file}")
        print(f"   采集时间: {result['crawled_at']}")
        print(f"   有效景区数据: {len(result['competitors'])}/8")
    else:
        print("\n❌ 采集失败")
        sys.exit(1)
