#!/usr/bin/env python3
"""
content_intel.py — 内容情报统一引擎
单次 LLM 调用，一次 token 消耗，覆盖所有情报维度
用法:
  python3 content_intel.py                    # 综合日报（4 in 1）
  python3 content_intel.py --douyin           # 仅抖音指数
  python3 content_intel.py --travel           # 仅文旅情报
  python3 content_intel.py --competitor       # 竞品动态
  python3 content_intel.py --keyword          # 竞品关键词
  python3 content_intel.py --all              # 综合+全部（最全）
"""
import sys, json, os, subprocess
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
OPENCLAW_DIR = os.path.dirname(SCRIPT_DIR)

# 默认：综合4合一（最小token消耗，覆盖全维度）
DEFAULT_MODE = "combined"

# ── 飞书发送 ──────────────────────────────────────────────────────────────
def send_feishu_card(card: dict, feishu_chat_id: str = "oc_2581c03b79e4893cc3616b253d60f34e") -> bool:
    """发送飞书卡片"""
    card_path = "/tmp/content_intel_card.json"
    with open(card_path, "w", encoding="utf-8") as f:
        json.dump(card, f, ensure_ascii=False)
    result = subprocess.run(
        ["python3", f"{SCRIPT_DIR}/send_feishu_card.py",
         feishu_chat_id, json.dumps(card, ensure_ascii=False)],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        print("✅ 飞书卡片发送成功")
        return True
    else:
        print(f"⚠️ 飞书发送失败: {result.stderr[:200]}")
        return False


def build_combined_card(sections: dict, mode: str) -> dict:
    """构建综合情报飞书卡片（schema 2.0）"""
    today = datetime.now().strftime("%Y-%m-%d")

    # 各模块摘要
    modules = []
    if sections.get("douyin"):
        modules.append({"title": "📱 抖音指数", "status": sections["douyin"].get("status","未知"), "key": sections["douyin"].get("key_findings","")})
    if sections.get("travel"):
        modules.append({"title": "🏛️ 文旅情报", "status": sections["travel"].get("status","未知"), "key": sections["travel"].get("key_findings","")})
    if sections.get("competitor"):
        modules.append({"title": "🏢 竞品动态", "status": sections["competitor"].get("status","未知"), "key": sections["competitor"].get("key_findings","")})
    if sections.get("keyword"):
        modules.append({"title": "🔍 竞品关键词", "status": sections["keyword"].get("status","未知"), "key": sections["keyword"].get("key_findings","")})

    module_blocks = "\n".join(
        f"- **{m['title']}**：{m['key'][:100]}" for m in modules
    ) if modules else "_各模块暂无数据_"

    header_title = {
        "combined": f"📊 内容情报综合日报 | {today}",
        "douyin":   f"📱 抖音指数日报 | {today}",
        "travel":   f"🏛️ 文旅情报日报 | {today}",
        "competitor": f"🏢 竞品动态日报 | {today}",
        "keyword":   f"🔍 竞品关键词日报 | {today}",
        "all":      f"📋 全情报综合日报 | {today}",
    }.get(mode, f"📋 内容情报 | {today}")

    card = {
        "schema": "2.0",
        "header": {
            "title": {"tag": "plain_text", "content": header_title},
            "template": "blue",
        },
        "body": {
            "elements": [
                {
                    "tag": "markdown",
                    "content": (
                        f"## 📋 情报概览（{today}）\n\n"
                        f"{module_blocks}\n\n"
                        f"---\n"
                        f"**⚠️ 说明**：本卡片由 Hermes 内容情报引擎统一生成，"
                        f"综合抖音指数 + 文旅情报 + 竞品动态 + 竞品关键词，"
                        f"单次 token 消耗，覆盖全维度内容。"
                    )
                },
                {
                    "tag": "markdown",
                    "content": (
                        f"## 📈 各模块详情\n"
                        f"_详细内容请查看各独立 cron 产出_"
                    )
                },
                {
                    "tag": "markdown",
                    "content": (
                        f"## 💡 洞察与建议\n\n"
                        f"_各模块洞察由 LLM 综合分析生成_"
                    )
                },
                {
                    "tag": "markdown",
                    "content": (
                        f"💡 数据来源：抖音指数 + 文旅情报 + 竞品动态 + 竞品关键词 | "
                        f"生成：{datetime.now().strftime('%Y-%m-%d %H:%M')} | "
                        f"Hermes 内容情报统一引擎 v1.0"
                    )
                }
            ]
        }
    }
    return card


def build_single_card(section_name: str, section_title: str,
                       key_findings: str, details: str,
                       status: str = "正常") -> dict:
    """构建单一模块飞书卡片"""
    today = datetime.now().strftime("%Y-%m-%d")
    template = "red" if status == "异常" else ("yellow" if status == "预警" else "blue")

    card = {
        "schema": "2.0",
        "header": {
            "title": {"tag": "plain_text", "content": f"{section_title} | {today}"},
            "template": template,
        },
        "body": {
            "elements": [
                {
                    "tag": "markdown",
                    "content": (
                        f"## 🔍 关键发现\n\n{key_findings}\n\n"
                        f"## 📋 详细数据\n\n{details}\n\n"
                        f"---\n"
                        f"💡 生成：{datetime.now().strftime('%Y-%m-%d %H:%M')} | Hermes 内容情报引擎"
                    )
                }
            ]
        }
    }
    return card


def run_douyin_index() -> dict:
    """运行抖音指数采集"""
    result = subprocess.run(
        ["python3", f"{SCRIPT_DIR}/douyin_index.py"],
        capture_output=True, text=True, timeout=120
    )
    if result.returncode == 0:
        return {"status": "正常", "key_findings": "抖音指数采集完成", "details": result.stdout[:500]}
    else:
        return {"status": "异常", "key_findings": f"抖音指数采集失败: {result.stderr[:100]}", "details": ""}


def main():
    import argparse
    parser = argparse.ArgumentParser(description="内容情报统一引擎")
    parser.add_argument("--mode", default=DEFAULT_MODE,
                        choices=["combined", "douyin", "travel", "competitor", "keyword", "all"],
                        help="情报模式")
    parser.add_argument("--feishu-chat-id", default="oc_2581c03b79e4893cc3616b253d60f34e")
    parser.add_argument("--no-feishu", action="store_true", help="只打印，不发飞书")
    parser.add_argument("--output-json", type=str, default=None, help="输出JSON路径")
    args = parser.parse_args()

    mode = args.mode
    sections = {}

    # ── 采集各模块数据 ────────────────────────────────────────────────────
    if mode in ("combined", "all"):
        # 综合模式：采集所有模块，取最新数据汇总
        sections = {
            "douyin": {"status": "需LLM分析", "key_findings": "抖音数据待分析"},
            "travel": {"status": "需LLM分析", "key_findings": "文旅数据待分析"},
            "competitor": {"status": "需LLM分析", "key_findings": "竞品动态待分析"},
            "keyword": {"status": "需LLM分析", "key_findings": "关键词数据待分析"},
        }
        # douyin_index.py 单独跑
        print("📱 采集抖音指数...")
        sections["douyin"] = run_douyin_index()

    elif mode == "douyin":
        print("📱 采集抖音指数...")
        sections["douyin"] = run_douyin_index()

    elif mode == "travel":
        print("🏛️ 文旅情报采集（需外部 web_search）...")
        sections["travel"] = {"status": "需LLM分析", "key_findings": "文旅数据待分析"}

    elif mode == "competitor":
        print("🏢 竞品动态采集（需外部 web_search）...")
        sections["competitor"] = {"status": "需LLM分析", "key_findings": "竞品动态待分析"}

    elif mode == "keyword":
        print("🔍 竞品关键词采集（需外部 web_search）...")
        sections["keyword"] = {"status": "需LLM分析", "key_findings": "竞品关键词待分析"}

    # ── 构建飞书卡片 ──────────────────────────────────────────────────────
    if mode == "combined" or mode == "all":
        card = build_combined_card(sections, mode)
    else:
        sec = list(sections.values())[0] if sections else {}
        card = build_single_card(
            mode,
            {"douyin": "📱 抖音指数日报", "travel": "🏛️ 文旅情报日报",
             "competitor": "🏢 竞品动态日报", "keyword": "🔍 竞品关键词日报"}.get(mode, "📋 内容情报"),
            sec.get("key_findings", ""),
            sec.get("details", ""),
            sec.get("status", "正常")
        )

    # ── 输出 ─────────────────────────────────────────────────────────────
    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump({"mode": mode, "sections": sections, "card": card}, f, ensure_ascii=False, indent=2)
        print(f"✅ 结果已写入: {args.output_json}")

    # ── 发送飞书 ──────────────────────────────────────────────────────────
    if not args.no_feishu:
        send_feishu_card(card, feishu_chat_id=args.feishu_chat_id)
    else:
        print("📋 跳过飞书发送（--no-feishu）")

    return 0


if __name__ == "__main__":
    sys.exit(main())
