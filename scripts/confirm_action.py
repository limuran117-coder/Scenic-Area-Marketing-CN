#!/usr/bin/env python3
"""
重要操作确认脚本
在执行高风险操作前请求用户确认

使用场景：
- 对外发送消息（发群、发邮件）
- 修改数据（更新Excel、删除文件）
- 关键决策建议（促销、降价）
- 异常数据处理

用户确认方式：
- 飞书消息回复"确认"/"同意"
- 或者在对话中明确表达同意
"""

import json
import sys
from datetime import datetime

# 高风险操作类型
HIGH_RISK_ACTIONS = [
    "send_group",      # 发群消息
    "send_external",   # 对外发送
    "delete_data",     # 删除数据
    "price_change",    # 价格变动
    "promotion",       # 促销活动
    "cancel_order",    # 取消订单
]

def create_confirm_request(action_type, details):
    """创建确认请求"""
    confirm_request = {
        "action": action_type,
        "details": details,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "user_confirmed": None,
        "user_response": None
    }
    return confirm_request

def save_confirm_request(request, filepath="/tmp/pending_confirm.json"):
    """保存确认请求到文件"""
    with open(filepath, "w") as f:
        json.dump(request, f, ensure_ascii=False, indent=2)

def load_confirm_request(filepath="/tmp/pending_confirm.json"):
    """加载确认请求"""
    if not filepath.exists():
        return None
    with open(filepath) as f:
        return json.load(f)

def is_high_risk(action_type):
    """判断是否高风险操作"""
    return action_type in HIGH_RISK_ACTIONS

def format_confirm_message(request):
    """格式化确认消息"""
    action = request["action"]
    details = request["details"]
    
    messages = {
        "send_group": f"⚠️ 确认发群\n\n内容：{details.get('content', '')[:100]}...",
        "send_external": f"⚠️ 对外发送\n\n内容：{details.get('content', '')[:100]}...",
        "delete_data": f"⚠️ 删除数据\n\n确认删除：{details.get('target', '')}",
        "price_change": f"⚠️ 价格变动\n\n调整：{details.get('change', '')}",
        "promotion": f"⚠️ 促销活动\n\n内容：{details.get('content', '')[:100]}...",
    }
    
    return messages.get(action, f"⚠️ 确认操作\n\n{json.dumps(details, ensure_ascii=False)[:100]}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        action = sys.argv[1]
        
        if action == "check":
            # 检查是否有待确认的操作
            request = load_confirm_request()
            if request and request["status"] == "pending":
                print("有待确认操作:")
                print(json.dumps(request, ensure_ascii=False, indent=2))
                print(f"\n消息预览:\n{format_confirm_message(request)}")
            else:
                print("没有待确认的操作")
        
        elif action == "clear":
            # 清除待确认操作
            Path("/tmp/pending_confirm.json").unlink(missing_ok=True)
            print("已清除待确认操作")
        
        elif action == "request":
            if len(sys.argv) > 2:
                action_type = sys.argv[2]
                details = json.loads(sys.argv[3]) if len(sys.argv) > 3 else {}
                
                if is_high_risk(action_type):
                    request = create_confirm_request(action_type, details)
                    save_confirm_request(request)
                    print(f"已创建确认请求:")
                    print(format_confirm_message(request))
                else:
                    print(f"操作 {action_type} 不是高风险，直接执行")
            else:
                print("用法: confirm.py request <action_type> <details_json>")
    
    else:
        print("高风险操作确认工具")
        print("用法:")
        print("  confirm.py check      - 检查待确认操作")
        print("  confirm.py clear      - 清除待确认操作")
        print("  confirm.py request <type> <details> - 创建确认请求")
        print(f"\n高风险操作类型: {HIGH_RISK_ACTIONS}")
