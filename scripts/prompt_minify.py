#!/usr/bin/env python3
"""
prompt_minify.py — Caveman-style prompt compression for cron task dispatch.
Cuts 50-65% of prompt tokens by removing filler phrases, merging redundant
instructions, and stripping polite boilerplate.

Usage:
    python3 prompt_minify.py < prompt.txt         # read from stdin
    python3 prompt_minify.py -f prompt.txt         # read from file
    python3 prompt_minify.py "raw prompt text"     # inline string

Based on the Caveman (66.5K⭐) principle: "why use many token when few do trick"
https://github.com/JuliusBrussee/caveman
"""

import re
import sys


# === RULES (ordered: most aggressive first) ===

REMOVE_LINES = [
    # Polite/boilerplate openers
    r"^(当然|好的|没问题|收到|明白了|开始吧|我来帮你|让我来).*[。！]",
    r"^(Sure|OK|Got it|Let me|I'll |Here['´]s|Certainly|Of course|Absolutely).*",
    r"^(I'd be happy to|I can help|Let me help|I will|I'm here to).*",
    r"^(Please|Kindly|Feel free to|Don't hesitate).*",

    # Redundant prompt instructions
    r"^(请|麻烦)(按照|根据|参考|遵循|使用).*$",
    r"^(使用|用|通过).*工具[，。]",
    r"^(严格按照|务必|一定|必须|切记).*",
    r"^⚠.*retry.*mechanism.*$",
    r"^(If|When).*(encounter|meet|face).*(error|timeout|fail).*wait.*retry.*$",
    r"^.*(重试机制|遇到.*超时|等待.*秒后自动重试|最多重试).*$",

    # Generic ceremony (pattern: "Do X. The goal is to Y.")
    r"^目的是.*$",
    r"^目标是为.*$",
    r"^本文将.*$",
    r"^本报告.*$",

    # Footer ceremony
    r"^(如果您有|有任何|如有|欢迎).*(问题|建议|反馈|联系).*$",
    r"^(Thank|Thanks|Thx).*$",
    r"^(如有疑问|欢迎随时).*$",
    r"^.*(祝您|祝工作).*$",
]

REMOVE_PATTERNS = [
    # Filler adjectives
    (r"\b(comprehensive|detailed|thorough|careful|robust|extensive|in-depth)\b", ""),
    # Weasel words
    (r"\b(essentially|basically|actually|simply|literally|virtually|practically)\b", ""),
    # Redundant qualifiers
    (r"\b(it['´]s worth noting that|it should be noted that|it is important to|it['´]s important to|keep in mind that|as you know|as mentioned|as we discussed)\b", ""),
    # Self-referential
    (r"\b(in my opinion|from my perspective|I think|I believe|I would say|I suggest)\b", "建议"),
    # Politeness padding
    (r"\b(please|kindly|graciously)\b", ""),
]

SHORTEN = [
    (r"为了提高|为了提升|为了增强|为了优化", "→"),
    (r"数据必须是当天|数据必须是.*最新", "取今日数据"),
    (r"确保.*正确|保证.*准确|确认为", "→"),
    (r"北极星目标[：:]\s*提升\s*有效到园客流\s*\+\s*提升\s*散客占比\s*\+\s*提升\s*种草转化效率", "目标:客流↑·散客↑·种草↑"),
    (r"发送方式（重要）[：:]\s*使用\s*send_feishu_card\.py\s*发送", "通道:send_feishu_card.py"),
    (r"完成标记（务必执行）[：:]\s*卡片发送成功后", "标记卡片发送完成"),
    (r"构造.*schema.*2\.0.*卡片.*header.*tag.*plain_text.*body.*elements.*markdown", ""),
    (r"保存.*/tmp/report_card\.json.*后运行|保存 JSON 到 /tmp/report_card\.json", "卡片JSON→/tmp/report_card.json"),
    (r"表格在 markdown 中用.*管道符.*不加任何代码块", ""),
    (r"不得额外添加.*列", ""),
    (r"表头必须含.*异动.*列", ""),
    (r"每行数据必须写异动简评", ""),
    (r"（重要）", "·"),
    (r"（务必执行）", "·"),
]


def compress(text: str) -> str:
    """Apply minification rules. Returns compressed text."""
    lines = text.splitlines()

    # Pass 1: remove full lines matching REMOVE_LINES
    cleaned = []
    for line in lines:
        skip = False
        for pattern in REMOVE_LINES:
            if re.match(pattern, line.strip(), re.IGNORECASE):
                skip = True
                break
        if not skip:
            cleaned.append(line)
    text = "\n".join(cleaned)

    # Pass 2: apply regex substitutions (REMOVE_PATTERNS)
    for pattern, replacement in REMOVE_PATTERNS:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Pass 3: SHORTEN patterns
    for pattern, replacement in SHORTEN:
        text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

    # Pass 4: collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = text.strip()

    return text


def main():
    raw = ""
    if len(sys.argv) >= 3 and sys.argv[1] == "-f":
        with open(sys.argv[2], "r", encoding="utf-8") as f:
            raw = f.read()
    elif len(sys.argv) >= 2 and not sys.argv[1].startswith("-"):
        raw = sys.argv[1]
    else:
        raw = sys.stdin.read()

    compressed = compress(raw)
    orig_chars = len(raw)
    new_chars = len(compressed)
    saved = orig_chars - new_chars
    pct = (saved / orig_chars * 100) if orig_chars else 0

    # Stats on stderr so stdout is clean for piping
    print(f"📊 {orig_chars}ch → {new_chars}ch | 节省 {saved}ch ({pct:.0f}%)", file=sys.stderr)
    print(compressed)


if __name__ == "__main__":
    main()
