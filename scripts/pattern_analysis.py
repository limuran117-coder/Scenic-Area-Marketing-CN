#!/usr/bin/env python3
"""
pattern_analysis.py — 景区运营模式提取引擎
知识输入 → 模式提取 → 建议输出

功能：
  1. 读取 CSV（天气/客流/穿越德化街上座率）
  2. 计算周模式（同比/环比/天气相关性/散客占比趋势）
  3. 输出结构化 JSON（insights/patterns/alerts）
  4. 追加到 knowledge_base.json（积累历史模式）
  5. 触发 P0 预警（如有）

用法:
  python3 pattern_analysis.py                    # 分析最近7天
  python3 pattern_analysis.py --weeks 4          # 分析最近4周
  python3 pattern_analysis.py --date 2026-06-07  # 指定日期
"""
import sys, os, json, re
from datetime import datetime, timedelta
from pathlib import Path

# ── 路径配置 ───────────────────────────────────────────────────────────────
CSV_PATH  = Path.home() / "Desktop" / "2026游客量统计.csv"
WIKI_DATA = Path(__file__).parent.parent / "wiki" / "电影小镇" / "历史数据"
KB_FILE   = Path(__file__).parent.parent / "wiki" / "电影小镇" / "知识沉淀" / "patterns_knowledge_base.json"
WEEK_REPORT_DIR = WIKI_DATA

os.makedirs(KB_FILE.parent, exist_ok=True)

# ── 工具函数 ───────────────────────────────────────────────────────────────
def parse_csv(path):
    """解析宽格式 CSV。

    列结构：
      col 0 = 行类型（门票/市场/线上/窗口/2023年参考...）
      col 1 = 子类型（日期/研学/线上散客/大客户期票...）
      col 2 = 1月1日 的值/日期
      col 3 = 1月2日 的值/日期
      ...
      col 184 = 7月1日 的值（col2 + 182）

    dates 来自：row where col0="门票" and col1="日期" → col2..col183 是日期字符串列表
    """
    rows = {}   # {(type, subtype): [val_day1, val_day2, ...]}

    with open(path, encoding="utf-8-sig") as f:
        for raw in f:
            parts = [p.strip() for p in raw.split(",")]
            if not parts or not parts[0]:
                continue
            row_type = parts[0]
            row_sub  = parts[1] if len(parts) > 1 else ""
            vals = parts[2:]   # 各天的数据，从1月1日开始
            rows[(row_type, row_sub)] = vals

    # 日期行
    dates = rows.get(("门票", "日期"), [])
    if not dates or "日" not in str(dates[0]):
        raise ValueError("CSV 里找不到'门票, 日期'行（日期从第3列开始）")

    return rows, dates  # dates[i] = "M月D日"，vals[i] = 该天的数据


def get_val(rows, row_type, row_sub, date_index):
    """取指定行在 date_index 这天的值"""
    vals = rows.get((row_type, row_sub), [])
    if date_index >= len(vals):
        return None
    raw = vals[date_index].strip()
    if raw in ("", None, "#DIV/0!", "—"):
        return None
    try:
        return float(raw.replace("%","").replace(",",""))
    except:
        return raw


def date_label_to_index(dates, month, day):
    """'6月1日' → 在 dates 里的索引"""
    target = f"{month}月{day}日"
    try:
        return dates.index(target)
    except ValueError:
        return -1


def extract_week_data(all_rows, dates, monday, sunday):
    """从 all_rows 提取指定周(Mon-Sun)的数据"""
    year = monday.year
    result = {}

    for day_offset in range(7):
        d = monday + timedelta(days=day_offset)
        idx = date_label_to_index(dates, d.month, d.day)
        if idx < 0:
            continue

        date_str = d.strftime("%Y-%m-%d")
        dow = ["周一","周二","周三","周四","周五","周六","周日"][day_offset]

        entry = {
            "date": date_str,
            "dow": dow,
            "date_index": idx,
        }

        # 各指标
        entry["门票人数合计"] = get_val(all_rows, "门票人数合计", "", idx)
        entry["门票收入金额"] = get_val(all_rows, "门票收入金额", "", idx)
        entry["闸机入园人次"] = get_val(all_rows, "闸机入园人次", "", idx)
        entry["天气备注"] = get_val(all_rows, "天气备注", "", idx) or "正常天"

        # 散客 = 线上 + 窗口
        sk_total = 0
        for row_type, row_sub in [("线上", "线上散客"), ("窗口", "线下散客")]:
            v = get_val(all_rows, row_type, row_sub, idx)
            if isinstance(v, (int, float)):
                sk_total += v
        entry["散客合计"] = sk_total
        # 渠道 = 合计 - 散客（无法精确拆分的渠道合计）
        total_pax = entry.get("门票人数合计", 0) or 0
        entry["渠道合计"] = max(0, total_pax - sk_total)

        # 散客占比
        total = entry["门票人数合计"]
        if total and total > 0:
            entry["散客占比"] = (sk_total / total) * 100
        else:
            entry["散客占比"] = None

        # 穿越德化街
        entry["德化街_场次"] = get_val(all_rows, "场次", "《穿越德化街》", idx)
        entry["德化街_上座率"] = get_val(all_rows, "上座率", "《穿越德化街》", idx)
        entry["德化街_售卖"] = get_val(all_rows, "售卖", "《穿越德化街》", idx)

        result[date_str] = entry

    return result


def get_week_dates(anchor=None):
    """返回最近完整周的日期区间 (Mon-Sun)"""
    if anchor is None:
        anchor = datetime.now()
    days_since_sunday = (anchor.weekday() + 1) % 7
    sunday = anchor - timedelta(days=days_since_sunday)
    monday = sunday - timedelta(days=6)
    return monday, sunday


def calc_weather_impact(week_data):
    """计算天气-客流相关性"""
    normal_days = []
    rain_days = []
    for d, v in week_data.items():
        weather = str(v.get("天气备注","正常天"))
        total = v.get("门票人数合计")
        if total is None:
            continue
        if "雨" in weather or "雪" in weather or "冰" in weather:
            rain_days.append(total)
        else:
            normal_days.append(total)

    avg_normal = sum(normal_days)/len(normal_days) if normal_days else 0
    avg_rain = sum(rain_days)/len(rain_days) if rain_days else 0
    impact = (avg_normal - avg_rain) / avg_normal if avg_normal else 0

    return {
        "normal_avg": round(avg_normal),
        "rain_avg": round(avg_rain),
        "impact_pct": round(impact*100, 1),
        "normal_days": len(normal_days),
        "rain_days": len(rain_days),
    }


def calc_week_stats(week_data, prev_week_data):
    """计算本周统计"""
    totals = [v["门票人数合计"] for v in week_data.values() if v.get("门票人数合计")]
    revenues = [v["门票收入金额"] for v in week_data.values() if v.get("门票收入金额")]
    gate_in = [v["闸机入园人次"] for v in week_data.values() if v.get("闸机入园人次")]
    sjt_sessions = [v["德化街_场次"] for v in week_data.values() if v.get("德化街_场次")]
    sjt_occ = [v["德化街_上座率"] for v in week_data.values() if v.get("德化街_上座率")]

    # 散客/渠道合计（已由 extract_week_data 计算好）
    sk_total = sum(v.get("散客合计", 0) or 0 for v in week_data.values())
    qd_total = sum(v.get("渠道合计", 0) or 0 for v in week_data.values())

    total_pax = sum(totals) if totals else 0
    prev_total = sum(v["门票人数合计"] for v in prev_week_data.values() if v.get("门票人数合计")) if prev_week_data else 0

    week_total_revenue = sum(revenues) if revenues else 0
    avg_daily = total_pax / len(totals) if totals else 0

    # 散客占比趋势
    sk_ratio = sk_total / total_pax if total_pax else 0

    # 穿越德化街上座率
    sjt_avg_occ = sum(sjt_occ)/len(sjt_occ) if sjt_occ else 0

    return {
        "week_total_pax": int(total_pax),
        "week_total_revenue": int(week_total_revenue),
        "avg_daily_pax": int(avg_daily),
        "wow_change_pct": round((total_pax - prev_total) / prev_total * 100, 1) if prev_total else 0,
        "sk_ratio": round(sk_ratio*100, 1),
        "sk_total": int(sk_total),
        "qd_total": int(qd_total),
        "gate_in": int(sum(gate_in)) if gate_in else 0,
        "sjt_avg_occ": round(sjt_avg_occ, 1),
        "sjt_sessions": len([s for s in sjt_sessions if s]),
    }


def detect_anomalies(week_data):
    """检测异常日"""
    totals = {d: v["门票人数合计"] for d, v in week_data.items() if v.get("门票人数合计")}
    if not totals:
        return []

    avg = sum(totals.values()) / len(totals)
    anomalies = []

    for d, v in totals.items():
        change = (v - avg) / avg * 100 if avg else 0
        weather = week_data[d].get("天气备注", "")
        is_holiday = False  # 需要节假日数据，这里简化

        if abs(change) > 40:  # 偏离均值 40% 以上
            if change > 0:
                label = "🔺暴涨"
            else:
                label = "🔻骤降"

            entry = {
                "date": d,
                "pax": int(v),
                "deviation_pct": round(change, 1),
                "weather": weather,
                "label": label,
                "reason": [],
            }

            if "雨" in weather or "雪" in weather:
                entry["reason"].append("天气异常")
            if change > 50 and v > avg * 1.5:
                entry["reason"].append("疑似节假日/活动")
            if change < -40 and v < avg * 0.6:
                entry["reason"].append("疑似闭园/恶劣天气")

            anomalies.append(entry)

    return anomalies


def compare_with_history(week_data, kb_data):
    """对比历史同期（从知识库读取去年同一周数据）"""
    # 从 W23 报告已知 6/1-6/7 的历史数据
    # 这里用知识库里的 pattern
    historical = kb_data.get("historical_6月初", {})

    if not historical:
        # 从 wiki 历史报告里读（后备）
        historical = {
            "2023": {"pax": 22198, "note": "端午6/22-24不干扰"},
            "2024": {"pax": 15806, "note": "端午6/8-10不干扰"},
            "2025": {"pax": 28687, "note": "含端午尾巴6/1=16929"},
            "2025_adj": {"pax": 13771, "note": "剔除端午尾巴"},
        }

    return historical


def generate_insights(week_stats, weather_impact, anomalies, week_id, week_dates):
    """生成结构化洞察（按 insight-template 格式）"""
    insights = []
    monday_str = week_dates[0].strftime("%m/%d") if isinstance(week_dates[0], datetime) else str(week_dates[0])
    sunday_str = week_dates[1].strftime("%m/%d") if isinstance(week_dates[1], datetime) else str(week_dates[1])

    # Insight 1: 客流趋势
    wow = week_stats["wow_change_pct"]
    if wow < -10:
        level = "P0" if wow < -20 else "P1"
        insights.append({
            "level": level,
            "title": f"W{week_id} 客流环比{wow}%（{'结构性下滑' if wow < -20 else '短期波动'}）",
            "data_fact": f"本周客流 {week_stats['week_total_pax']} 人，日均 {week_stats['avg_daily_pax']} 人，环比 {'减少' if wow < 0 else '增加'} {abs(wow)}pp",
            "business_meaning": "同比/环比出现显著变化，需要判断是外部因素（天气/节假日/竞品）还是内部因素（节目/定价/营销）",
            "causal_analysis": "需对照：①天气记录 ②节假日日历 ③竞品动态 ④近期营销动作",
            "action": "核实根因，如为结构性下滑，需本周内启动营销应对",
            "archive_path": f"concepts/客流趋势/{monday_str}-{sunday_str}.md"
        })

    # Insight 2: 天气影响
    if weather_impact["rain_days"] > 0 and weather_impact["impact_pct"] > 0:
        insights.append({
            "level": "P2",
            "title": f"雨天 vs 晴天客流差异 {weather_impact['impact_pct']}%",
            "data_fact": f"正常天日均 {weather_impact['normal_avg']} 人，雨天 {weather_impact['rain_avg']} 人（{weather_impact['normal_days']} 正常天 / {weather_impact['rain_days']} 雨天）",
            "business_meaning": "雨天客流下降约 40% 是正常季节性现象，但可通过室内演出/雨天专项产品对冲",
            "causal_analysis": "雨天→出行意愿↓，但室内剧场《穿越德化街》不受影响",
            "action": "建议下雨天加强室内剧场推广，德化街上座率应有逆势表现",
            "archive_path": "concepts/天气客流关系.md"
        })

    # Insight 3: 散客占比
    sk_ratio = week_stats["sk_ratio"]
    if sk_ratio < 70:
        insights.append({
            "level": "P1",
            "title": f"散客占比跌破 70%（当前 {sk_ratio}%）",
            "data_fact": f"本周散客 {week_stats['sk_total']} 人（{sk_ratio}%），渠道 {week_stats['qd_total']} 人",
            "business_meaning": "散客占比低于 70% 表明对渠道（旅行社/研学）依赖度过高，散客是利润更高、更稳定的客群",
            "causal_analysis": "可能原因：①研学季结束 ②暑期散客还未启动 ③渠道正在补货",
            "action": "关注下周一散客占比是否回升，若持续低于 70%，需启动散客专项营销",
            "archive_path": "concepts/散客渠道结构.md"
        })
    elif sk_ratio > 80:
        insights.append({
            "level": "P2",
            "title": f"散客占比健康（{sk_ratio}%）",
            "data_fact": f"散客 {week_stats['sk_total']} 人，占比 {sk_ratio}%，高于 80% 健康线",
            "business_meaning": "散客基本盘稳固，是营收质量良好的信号",
            "causal_analysis": "高散客占比通常意味着自然流量强，品牌认知度高",
            "action": "保持当前内容营销力度，重点维护抖音/小红书种草",
            "archive_path": "concepts/散客渠道结构.md"
        })

    # Insight 4: 穿越德化街
    sjt_occ = week_stats["sjt_avg_occ"]
    if sjt_occ > 0:
        if sjt_occ < 50:
            insights.append({
                "level": "P1",
                "title": f"《穿越德化街》上座率偏低（{sjt_occ}%）",
                "data_fact": f"本周场均上座率 {sjt_occ}%，{week_stats['sjt_sessions']} 场",
                "business_meaning": "上座率低于 50% 意味着产能浪费，场均成本不变但收入不足",
                "causal_analysis": "工作日白天场次通常上座率低，建议核查是否排了过多工作日白场",
                "action": "评估是否减少工作日白场，增加周末/夜场，或推出学生票/低价体验票拉动工作日上座",
                "archive_path": "entities/穿越德化街.md"
            })
        elif sjt_occ > 80:
            insights.append({
                "level": "P2",
                "title": f"《穿越德化街》上座率优秀（{sjt_occ}%）",
                "data_fact": f"本周场均上座率 {sjt_occ}%，{week_stats['sjt_sessions']} 场",
                "business_meaning": "高上座率说明产品力强，可考虑提升票价或增加场次",
                "causal_analysis": "高上座率常与周末/节假日重叠，说明定价和产品匹配度好",
                "action": "追踪高上座率日的共同特征（天气？节假日？营销活动？）",
                "archive_path": "entities/穿越德化街.md"
            })

    # Insight 5: 异常日洞察
    if anomalies:
        for a in anomalies[:2]:  # 最多2个
            insights.append({
                "level": "P0" if abs(a["deviation_pct"]) > 50 else "P1",
                "title": f"{a['label']} {a['date']} 客流偏离均值 {a['deviation_pct']}%",
                "data_fact": f"{a['date']} 客流 {a['pax']} 人，偏离周均值 {a['deviation_pct']}%，天气：{a['weather']}，可能原因：{'/'.join(a['reason']) if a['reason'] else '待查'}",
                "business_meaning": f"{'需立即核实' if abs(a['deviation_pct']) > 50 else '需关注'}：{a['date']} 出现显著偏离",
                "causal_analysis": "天气/节假日/临时活动/数据误差均可能，需交叉核实",
                "action": f"核实 {a['date']} 是否有特殊事件（天气/节假日/竞品/内部活动），如有数据错误需更正 CSV",
                "archive_path": f"concepts/异常日分析/{a['date']}.md"
            })

    return insights


def build_feishu_card(week_data: dict, week_stats: dict,
                       weather_impact: dict, insights: list,
                       week_label: str, week_id: str) -> dict:
    """生成飞书交互卡片 JSON（schema 2.0）"""
    from datetime import datetime

    wow = week_stats["wow_change_pct"]
    wow_emoji = "📈" if wow >= 0 else "📉"
    wow_color = "blue" if wow >= 0 else "orange"

    sjt_occ = week_stats.get("sjt_avg_occ", 0) or 0
    sjt_emoji = "🟢" if sjt_occ >= 60 else ("🟡" if sjt_occ >= 40 else "🔴")

    sk_ratio = week_stats.get("sk_ratio", 0) or 0
    sk_emoji = "🟢" if sk_ratio >= 70 else ("🟡" if sk_ratio >= 50 else "🔴")

    revenue_w = week_stats.get("week_total_revenue", 0) or 0

    # 洞察摘要
    p0s = [i for i in insights if i.get("level") == "P0"]
    p1s = [i for i in insights if i.get("level") == "P1"]
    p2s = [i for i in insights if i.get("level") == "P2"]

    p0_block = ""
    if p0s:
        p0_block = "## 🔴 P0 预警（需立即处理）\n"
        for p in p0s:
            p0_block += f"- **{p['title']}**：{p['action']}\n"

    insight_lines = []
    for i in (p0s + p1s + p2s):
        flag = "🔴" if i["level"] == "P0" else ("🟡" if i["level"] == "P1" else "🟢")
        insight_lines.append(f"{flag}[{i['level']}] **{i['title']}**：{i['action']}")

    insight_block = "\n".join(insight_lines) if insight_lines else "_本周无显著异常_"

    # 天气数据
    wi = weather_impact
    weather_block = (
        f"雨天日均 **{wi['rain_avg']:,}人**（{wi['rain_days']}天）"
        f" vs 正常天 **{wi['normal_avg']:,}人**（{wi['normal_days']}天）"
        f" → 雨天影响 **{wi['impact_pct']}%**"
        if wi.get("rain_days", 0) > 0
        else f"本周无雨天数据（{wi['normal_days']}个正常天，日均 **{wi['normal_avg']:,}人**）"
    )

    # 每日明细表
    day_lines = ["| 日期 | 星期 | 客流 | 散客 | 渠道 | 天气 |",
                 "|------|------|------|------|------|------|"]
    for d, v in sorted(week_data.items()):
        total = int(v.get("门票人数合计", 0) or 0)
        sk = int(v.get("散客合计", 0) or 0)
        qd = int(v.get("渠道合计", 0) or 0)
        weather = str(v.get("天气备注", "正常天") or "正常天")[:6]
        dow = v.get("dow", d[5:])
        day_lines.append(f"| {d[5:]} | {dow} | {total:,} | {sk:,} | {qd:,} | {weather} |")

    day_table = "\n".join(day_lines)

    header_tag = "red" if p0s else ("yellow" if p1s else "blue")

    # note 元素的正确格式：content 字段直接放 plain_text
    card = {
        "schema": "2.0",
        "header": {
            "title": {"tag": "plain_text", "content": f"📊 {week_id} 客流模式分析 | {week_label}"},
            "template": header_tag,
        },
        "body": {
            "elements": [
                {
                    "tag": "markdown",
                    "content": (
                        "## 📈 核心指标\n"
                        f"| 指标 | 数值 | 状态 |\n"
                        f"|------|------|------|\n"
                        f"| 周合计客流 | **{week_stats['week_total_pax']:,}人** | {wow_emoji} 环比 {wow:+.1f}% |\n"
                        f"| 日均客流 | **{week_stats['avg_daily_pax']:,}人** | — |\n"
                        f"| 散客占比 | **{sk_ratio:.1f}%** | {sk_emoji} {'健康' if sk_ratio >= 70 else '偏低'} |\n"
                        f"| 渠道客流 | **{week_stats.get('qd_total',0):,}人** | — |\n"
                        f"| 闸机入园 | **{week_stats.get('gate_in',0):,}人次** | — |\n"
                        f"| 门票收入 | **¥{revenue_w:,}** | — |\n"
                        f"| 德化街上座率 | **{sjt_occ:.1f}%** | {sjt_emoji} {'优秀' if sjt_occ>=80 else ('良好' if sjt_occ>=50 else '偏低')} |\n"
                    )
                },
                {
                    "tag": "markdown",
                    "content": (
                        f"## 🌤️ 天气-客流关系\n{weather_block}\n\n"
                        f"## 📅 每日明细\n{day_table}"
                    )
                },
                {
                    "tag": "markdown",
                    "content": (
                        f"## 🔍 本周洞察（共 {len(insights)} 条，P0:{len(p0s)}/P1:{len(p1s)}/P2:{len(p2s)}）\n{insight_block}\n\n"
                        f"{p0_block}"
                    )
                },
                {
                    "tag": "markdown",
                    "content": f"💡 数据来源：Desktop/2026游客量统计.csv | 生成：{datetime.now().strftime('%Y-%m-%d %H:%M')} | Hermes 景区模式分析引擎"
                }
            ]
        }
    }
    return card


def send_feishu_card(card: dict, feishu_chat_id: str = "oc_2581c03b79e4893cc3616b253d60f34e") -> bool:
    """发送飞书卡片"""
    import subprocess, json as _json
    card_path = "/tmp/pattern_analysis_card.json"
    with open(card_path, "w", encoding="utf-8") as f:
        _json.dump(card, f, ensure_ascii=False)
    result = subprocess.run(
        ["python3", "/Users/tianjinzhan/.openclaw/workspace/scripts/send_feishu_card.py",
         feishu_chat_id, _json.dumps(card, ensure_ascii=False)],
        capture_output=True, text=True, timeout=30
    )
    if result.returncode == 0:
        print(f"  ✅ 飞书卡片已发送")
        return True
    else:
        print(f"  ⚠️ 飞书卡片发送失败: {result.stderr[:200]}")
        return False


def detect_p0_alerts(insights):
    """返回所有 P0 洞察（需立即处理的）"""
    return [i for i in insights if i.get("level") == "P0"]


def load_knowledge_base():
    """加载历史知识库"""
    if KB_FILE.exists():
        with open(KB_FILE) as f:
            return json.load(f)
    return {"patterns": [], "insights": [], "alerts": [], "historical_6月初": {}}


def save_knowledge_base(kb):
    """保存知识库"""
    with open(KB_FILE, "w", encoding="utf-8") as f:
        json.dump(kb, f, ensure_ascii=False, indent=2)


# ── 主逻辑 ─────────────────────────────────────────────────────────────────
def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--weeks", type=int, default=1, help="分析最近N周")
    parser.add_argument("--date", type=str, default=None, help="指定周日（YYYY-MM-DD）")
    parser.add_argument("--output-json", type=str, default=None, help="输出JSON路径")
    parser.add_argument("--feishu", action="store_true", help="生成并发送飞书卡片")
    parser.add_argument("--feishu-chat-id", type=str,
                        default="oc_2581c03b79e4893cc3616b253d60f34e",
                        help="飞书群ID")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args()

    if not CSV_PATH.exists():
        print(f"❌ CSV 不存在: {CSV_PATH}", file=sys.stderr)
        print("请确认 Desktop/2026游客量统计.csv 存在", file=sys.stderr)
        sys.exit(1)

    rows, dates = parse_csv(CSV_PATH)

    # 加载知识库
    kb = load_knowledge_base()

    # 分析最近 N 周
    anchor = datetime.strptime(args.date, "%Y-%m-%d") if args.date else datetime.now()
    monday, sunday = get_week_dates(anchor)

    all_results = {}

    for w in range(args.weeks):
        w_monday = monday - timedelta(weeks=w)
        w_sunday = sunday - timedelta(weeks=w)
        w_monday_prev = w_monday - timedelta(weeks=1)
        w_sunday_prev = w_sunday - timedelta(weeks=1)

        week_data = extract_week_data(rows, dates, w_monday, w_sunday)
        prev_week_data = extract_week_data(rows, dates, w_monday_prev, w_sunday_prev)

        if not week_data:
            print(f"⚠️ W around {w_monday.strftime('%m/%d')} 无数据，跳过", file=sys.stderr)
            continue

        week_id = w_monday.isocalendar()[1]
        year = w_monday.year

        weather_impact = calc_weather_impact(week_data)
        week_stats = calc_week_stats(week_data, prev_week_data)
        anomalies = detect_anomalies(week_data)
        historical = compare_with_history(week_data, kb)
        insights = generate_insights(week_stats, weather_impact, anomalies, week_id, [w_monday, w_sunday])

        # 当前周的当年 YTD
        ytd = kb.get("ytd", 0) + week_stats["week_total_pax"]

        result = {
            "week_id": f"W{week_id}",
            "week_label": f"{w_monday.strftime('%Y-%m-%d')} ~ {w_sunday.strftime('%Y-%m-%d')}",
            "year": year,
            "stats": week_stats,
            "weather_impact": weather_impact,
            "anomalies": anomalies,
            "historical": historical,
            "insights": insights,
            "p0_alerts": detect_p0_alerts(insights),
            "ytd_pax": ytd,
            "generated_at": datetime.now().isoformat(),
        }

        key = f"W{week_id}_{w_monday.strftime('%Y%m%d')}"
        all_results[key] = result

        if args.verbose:
            print(f"\n{'='*60}")
            print(f"  {key} | {w_monday.strftime('%m/%d')} - {w_sunday.strftime('%m/%d')}")
            print(f"{'='*60}")
            print(f"  客流: {week_stats['week_total_pax']:,} 人 | 日均 {week_stats['avg_daily_pax']:,}")
            print(f"  环比: {week_stats['wow_change_pct']:+.1f}% | 散客占比: {week_stats['sk_ratio']:.1f}%")
            print(f"  天气影响: 雨天-{weather_impact['rain_days']}天/正常-{weather_impact['normal_days']}天 → {weather_impact['impact_pct']}%差异")
            print(f"  德化街上座率: {week_stats['sjt_avg_occ']}%")
            print(f"  洞察 ({len(insights)}条):")
            for i in insights:
                print(f"    [{i['level']}] {i['title']}")
            if result["p0_alerts"]:
                print(f"  🔴 P0 预警: {len(result['p0_alerts'])} 条！")

        # 追加到知识库
        kb["patterns"].append({
            "week": key,
            "stats": week_stats,
            "weather_impact": weather_impact,
            "ytd": ytd,
        })
        kb["insights"].extend([{"week": key, **i} for i in insights])

    # 保存知识库
    cumulative_ytd = kb.get("ytd", 0)
    for r in all_results.values():
        cumulative_ytd += r["stats"]["week_total_pax"]
    kb["ytd"] = cumulative_ytd
    save_knowledge_base(kb)

    # ── 飞书卡片（--feishu）─────────────────────────────────────────────────
    if args.feishu and all_results:
        print(f"\n📤 正在发送飞书卡片...")
        # 单周发卡片（多周只发最新的一周）
        latest_key = sorted(all_results.keys())[-1]
        latest = all_results[latest_key]
        # 重建 week_data 用于卡片
        w_label = latest["week_label"]
        w_id = latest["week_id"]
        # 重新从 CSV 提取本周数据给卡片
        anchor2 = datetime.strptime(args.date or datetime.now().strftime("%Y-%m-%d"), "%Y-%m-%d")
        _, sun2 = get_week_dates(anchor2)
        w_m_prev = sun2 - timedelta(days=6) - timedelta(weeks=len(all_results)-1)
        w_s_prev = sun2 - timedelta(weeks=len(all_results)-1)
        wd = extract_week_data(rows, dates, w_m_prev, w_s_prev)

        card = build_feishu_card(
            week_data=wd,
            week_stats=latest["stats"],
            weather_impact=latest["weather_impact"],
            insights=latest["insights"],
            week_label=w_label,
            week_id=w_id,
        )
        send_feishu_card(card, feishu_chat_id=args.feishu_chat_id)

    # 输出
    if args.output_json:
        with open(args.output_json, "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        print(f"\n✅ 结果已写入: {args.output_json}")
    elif len(all_results) == 1:
        # 单周：打印摘要
        k = list(all_results.keys())[0]
        r = all_results[k]
        print(f"\n{'='*60}")
        print(f"  📊 {r['week_label']} 客流分析")
        print(f"{'='*60}")
        s = r['stats']
        print(f"  本周客流: {s['week_total_pax']:,} 人 | 日均 {s['avg_daily_pax']:,} 人")
        print(f"  环比变化: {s['wow_change_pct']:+.1f}%")
        print(f"  散客占比: {s['sk_ratio']:.1f}%（{'健康' if s['sk_ratio'] > 70 else '⚠️偏低'}）")
        print(f"  德化街上座率: {s['sjt_avg_occ']}%")
        print(f"  天气影响: 雨天均 {r['weather_impact']['rain_avg']} 人 vs 正常天 {r['weather_impact']['normal_avg']} 人")
        print()
        print(f"  🔍 洞察 ({len(r['insights'])}条):")
        for i in r['insights']:
            flag = "🔴" if i['level'] == "P0" else ("🟡" if i['level'] == "P1" else "🟢")
            print(f"    {flag}[{i['level']}] {i['title']}")
            print(f"           数据: {i['data_fact']}")
            print(f"           建议: {i['action']}")
        if r['p0_alerts']:
            print(f"\n  🔴 P0 预警 {len(r['p0_alerts'])} 条 — 需立即处理！")
            for a in r['p0_alerts']:
                print(f"    → {a['title']}")
    else:
        # 多周：打印摘要
        print(f"\n📊 分析了 {len(all_results)} 周:")
        for k, r in sorted(all_results.items()):
            s = r['stats']
            print(f"  {r['week_label']}: {s['week_total_pax']:,}人 | 环比{s['wow_change_pct']:+.1f}% | 散客{s['sk_ratio']:.1f}% | 德化街{s['sjt_avg_occ']:.1f}%")

    # P0 告警
    all_p0 = [i for r in all_results.values() for i in r.get("p0_alerts", [])]
    if all_p0:
        print(f"\n🔴 共 {len(all_p0)} 条 P0 预警:")
        for a in all_p0:
            print(f"  → {a['title']}")

    return 0 if not all_p0 else 1


if __name__ == "__main__":
    sys.exit(main())
