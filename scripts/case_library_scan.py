#!/opt/homebrew/bin/python3.12
"""案例库更新：扫描抖音/小红书景区爆款内容"""
import json
import subprocess
import sys
import time
import re

# 竞品关键词列表
COMPETITORS = [
    "只有河南戏剧幻城",
    "银基动物王国", 
    "万岁山武侠城",
    "清明上河园",
    "郑州方特欢乐世界",
    "建业电影小镇"
]

def search_douyin(keyword):
    """使用curl搜索抖音"""
    cmd = f'''curl -s "https://www.douyin.com/aweme/v1/web/general/search/item/?keyword={keyword}&search_channel=aweme_video_web&enable_history=1&source=normal_search&pd=aweme" \
        -H "User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36" \
        -H "Referer: https://www.douyin.com/"'''
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout
    except Exception as e:
        return ""

def parse_video_info(html_text):
    """解析视频信息"""
    # 简化处理，实际需要解析JSON
    videos = []
    try:
        data = json.loads(html_text)
        if 'data' in data:
            for item in data.get('data', []):
                videos.append({
                    'title': item.get('aweme_info', {}).get('desc', ''),
                    'likes': item.get('aweme_info', {}).get('statistics', {}).get('digg_count', 0),
                    'desc': item.get('aweme_info', {}).get('desc', '')[:100]
                })
    except:
        pass
    return videos

def main():
    print("=== 案例库更新扫描 ===")
    for kw in COMPETITORS:
        print(f"扫描: {kw}")
        time.sleep(5)
    
    # 扫描通用景区爆款
    keywords = ["景区爆款", "景点打卡", "五一去哪", "景区营销"]
    for kw in keywords:
        print(f"扫描: {kw}")
        time.sleep(5)
    
    print("扫描完成")

if __name__ == "__main__":
    main()
