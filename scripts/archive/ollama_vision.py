#!/usr/bin/env python3
"""
Ollama Vision 图片分析脚本
调用本地 llama3.2-vision:11b 模型分析图片

用法:
  python3 ollama_vision.py <图片路径> [prompt]
  python3 ollama_vision.py /path/to/image.png "详细描述这张图"
"""
import urllib.request
import urllib.error
import json
import base64
import sys
import os
import time

MODEL = "llama3.2-vision:11b"
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
DEFAULT_PROMPT = "请详细描述这张图片里的所有文字和数据内容，用中文回答。"
OUTPUT_FILE = "/tmp/ollama_vision_result.txt"

def analyze_image(image_path, prompt=DEFAULT_PROMPT, max_retries=3):
    """分析图片，返回文本描述"""
    if not os.path.exists(image_path):
        return f"错误：图片文件不存在: {image_path}"
    
    with open(image_path, "rb") as f:
        img_b64 = base64.b64encode(f.read()).decode("utf-8")
    
    payload = json.dumps({
        "model": MODEL,
        "prompt": prompt,
        "images": [img_b64],
        "stream": False
    }).encode("utf-8")
    
    req = urllib.request.Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            print(f"[尝试 {attempt}/{max_retries}] 正在分析图片...", file=sys.stderr)
            with urllib.request.urlopen(req, timeout=180) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return result.get("response", "无响应")
        except Exception as e:
            last_error = str(e)
            print(f"[尝试 {attempt}] 失败: {last_error}", file=sys.stderr)
            if attempt < max_retries:
                time.sleep(5)
    
    return f"错误：多次尝试后失败。最后错误: {last_error}"

def main():
    if len(sys.argv) < 2:
        print("用法: python3 ollama_vision.py <图片路径> [prompt]")
        print("默认prompt: 请详细描述这张图片里的所有文字和数据内容，用中文回答。")
        sys.exit(1)
    
    image_path = sys.argv[1]
    prompt = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_PROMPT
    
    # 确保Ollama服务在运行
    try:
        urllib.request.urlopen("http://127.0.0.1:11434/api/tags", timeout=5)
    except:
        print("错误: Ollama服务未运行，请先执行: ollama serve", file=sys.stderr)
        sys.exit(1)
    
    result = analyze_image(image_path, prompt)
    
    # 保存到文件
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(result)
    
    print(result)
    print(f"\n[结果已保存到: {OUTPUT_FILE}]")

if __name__ == "__main__":
    main()
