#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""飞书卡片表格上限拆分：每卡≤3张表。输出 A/B/C 三卡"""
import json, datetime, re

parts = json.load(open("/tmp/report_parts.json"))
p1, p2, p3 = parts["p1"], parts["p2"], parts["p3"]
today = datetime.date(2026, 8, 27).strftime("%m-%d")

# ---- 拆分 p2 的 4 个子表（子表4 含 region+gender 两张表，再拆）----
p2seg = re.split(r'(?=\*\*子表 )', p2)  # [标题, 子表1, 子表2, 子表3, 子表4]
title2 = p2seg[0]
s1 = p2seg[1]  # 子表1
s2 = p2seg[2]  # 子表2
s3 = p2seg[3]  # 子表3
s4 = p2seg[4]  # 子表4 (region + gender)
# 拆子表4 为 region 段 + gender 段
s4sp = re.split(r'(?=\n\n\| 性别)', s4)  # 在 gender 表前断开
s4_region = s4sp[0]   # 含 region 表 + 说明行
s4_gender = s4sp[1] if len(s4sp) > 1 else s4  # gender 表

p4 = (
f"**第四部分：竞品格局分析**（{today}）\n\n"
"**📊 头部格局**\n"
"- 清明上河园搜索 486,305（综合 168,649）断层第一，杨洋IP+《茶会》+资本叙事持续压制\n"
"- 银基动物王国 49,061 搜索（综合 15,022）双环比↑4.5%+，暑期产品词锁心智，是暑期夜游正面威胁\n"
"- 🔥 只有河南异动：搜索↑21.81%/综合↑18.34%（全场唯一高增长），王潮歌IP+夜幻城+68天焰火大会进入转化高峰\n"
"- 只有红楼梦综合↑10.13%：IP+复购护城河成型，京津冀客群虹吸延续\n\n"
"**😐 中游震荡**\n"
"- 万岁山搜索↓5.77%：王婆换人+NPC整治后单一爆款押注风险暴露\n"
"- 海昌↑7-8%：雨天免费重玩+海洋日公益，与电影小镇客群错位非直接威胁\n\n"
"**🔮 电影小镇自身**\n"
"- 双指数日环比转正（搜索+0.44%/综合+0.79%）：连续多日下滑后首次企稳微升，但同比仍双位数下行（搜索-12.35%/综合-17.85%），绝对值处 9 景区中游\n"
)

p5 = (
"**第五部分：行动建议**\n\n"
"**① 抓「海魂衫/海魂」双词 TOP3 飙升**（关联度49/48，第2/3位）：连续多日稳居关联词顶层但停留品牌词层未转种草词。今日发 1 条抖音+1 条小红书 80 年代海魂衫内容，绑定免费入园权益，把流量词变转化漏斗\n\n"
"**② 把「夜场」关联词(27)升级为 80 年代夜游 IP**：对标只有河南夜幻城+银基暑期夜场双压制，本周内出一版「80年代夜游 3 小时动线」（怀旧市集+老电影放映+年代金曲）\n\n"
"**③ 借「打铁花」做非遗怀旧嫁接**：万岁山打铁花(42)是短视频爆款，做「80年代怀旧市集+非遗打铁花」跨时代场景\n\n"
"**④ 只有河南异动≠跟风从众**：其+21.81%是王潮歌IP私域转化，客群(31-40中年+女性59%)与其麦田音乐会不同源，建议「借势观察」不硬刚，聚焦 80 年代差异化\n"
)

judge = (
"**判断层**\n"
"- 🎯 **影响等级**：中（双指数企稳微升，但同比仍下行、绝对值中游）\n"
"- 💡 **建议动作**：跟风（海魂衫/夜场/打铁花）＋ 警惕（银基暑期夜场 6/22 临近）\n"
"- ⏰ **执行窗口**：今天（海魂衫/夜场内容）、本周（80年代夜游升级）\n"
"- ⚠️ **不做的代价**：海魂衫流量词继续闲置 → 双指数再陷下滑，散客拉新窗口被银基/只有河南双夜游虹吸\n"
)

def mk_card(title, elements_list):
    elements = []
    for i, b in enumerate(elements_list):
        elements.append({"tag": "markdown", "content": b})
        if i != len(elements_list) - 1:
            elements.append({"tag": "hr"})
    return {
        "schema": "2.0",
        "header": {"template": "turquoise",
                   "title": {"tag": "plain_text", "content": title}},
        "body": {"elements": elements}
    }

def cnt_tables(s):
    t = 0; in_t = False
    for ln in s.split('\n'):
        if ln.strip().startswith('|'):
            if not in_t: t += 1; in_t = True
        else: in_t = False
    return t

# Card A: part1(1) + 子表1(1) + 子表2(1) = 3 tables
cardA = mk_card(f"📊 抖音指数日报 {today} · ① 数据一览与基础指标", [p1, s1, s2])
# Card B: 子表3(1) + 子表4region(1) + 子表4gender(1) = 3 tables
cardB = mk_card(f"📊 抖音指数日报 {today} · ② 关联词与人群画像", [s3, s4_region, s4_gender])
# Card C: part3(2) + 格局 + 行动 + 判断 = 2 tables
cardC = mk_card(f"📊 抖音指数日报 {today} · ③ 竞品对比与行动", [p3, p4, p5, judge])

for name, c, chk in [("A", cardA, [p1, s1, s2]), ("B", cardB, [s3, s4_region, s4_gender]), ("C", cardC, [p3])]:
    print(f"Card {name}: tables={sum(cnt_tables(x) for x in chk)}")

json.dump(cardA, open("/tmp/report_card_A.json", "w"), ensure_ascii=False)
json.dump(cardB, open("/tmp/report_card_B.json", "w"), ensure_ascii=False)
json.dump(cardC, open("/tmp/report_card_C.json", "w"), ensure_ascii=False)
print("✅ done")
