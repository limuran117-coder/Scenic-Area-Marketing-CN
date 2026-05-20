#!/usr/bin/env python3
"""
电影小镇运营数据看板 v2
更新：2026-05-15
"""
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import json, os, http.server, socketserver, webbrowser
from datetime import datetime

PORT = 8888
OUTPUT_DIR = "/tmp/movie_town_dashboard"
VISITOR_CSV = os.path.expanduser("~/Desktop/2026游客量统计.csv")
ANNUAL_TARGET = 1530000
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ========== DATA ==========
def load_visitor():
    if not os.path.exists(VISITOR_CSV):
        return None, None
    df = pd.read_csv(VISITOR_CSV)
    df['日期'] = pd.to_datetime(df['日期'])
    df = df.sort_values('日期').reset_index(drop=True)
    df['累计'] = df['合计'].cumsum()
    df['周'] = df['日期'].dt.isocalendar().week
    ytd = df[df['日期'].dt.year == 2026]['合计'].sum()
    return df, {'ytd': ytd, 'progress': ytd / ANNUAL_TARGET * 100}

# ========== CHARTS ==========
def chart_daily(df):
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=('每日客流', '累计客流'),
                        vertical_spacing=0.12)
    fig.add_trace(go.Bar(x=df['日期'], y=df['合计'],
                         name='日客流', marker_color='#3498db'), row=1, col=1)
    fig.add_trace(go.Scatter(x=df['日期'], y=df['累计'],
                             name='累计', line=dict(color='#e74c3c', width=2),
                             fill='tozeroy', fillcolor='rgba(231,76,60,0.1)'),
                  row=2, col=1)
    fig.add_hline(y=ANNUAL_TARGET, line_dash="dash", line_color="green",
                  annotation_text="目标 153万", row=2, col=1)
    fig.update_layout(height=600, title_text="日客流趋势", template='plotly_white')
    fig.write_html(OUTPUT_DIR + "/daily_trend.html")

def chart_weekly(df):
    weekly = df.groupby('周').agg({'合计': 'sum'}).reset_index()
    fig = px.bar(weekly, x='周', y='合计', title='周度客流',
                 color='合计', color_continuous_scale='Blues')
    fig.update_layout(template='plotly_white')
    fig.write_html(OUTPUT_DIR + "/weekly_trend.html")

def chart_douyin():
    spots = ['清明上河园','万岁山','银基动物王国','海昌海洋公园','只有河南','方特','电影小镇','只有红楼梦']
    scores = [192213, 33354, 21229, 16657, 5599, 3796, 2392, 1713]
    colors = ['#e74c3c' if s > 50000 else '#f39c12' if s > 5000 else '#2ecc71' for s in scores]
    fig = go.Figure(go.Bar(x=spots, y=scores, marker_color=colors,
                           text=[f'{s:,}' for s in scores], textposition='outside'))
    fig.update_layout(title='8大景区抖音搜索指数', template='plotly_white',
                      height=500, xaxis_tickangle=-30)
    fig.add_annotation(x=6, y=2392, text='电影小镇', showarrow=True, arrowhead=2)
    fig.write_html(OUTPUT_DIR + "/douyin_rank.html")

# ========== HTML ==========
def build_index(df, stats):
    latest = df.iloc[-1] if len(df) > 0 else None
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    cards = ""
    if stats:
        cards = (
            '<div style="display:flex;gap:20px;flex-wrap:wrap;padding:20px;font-family:sans-serif;">'
            '<div style="background:#2c3e50;color:white;padding:20px;border-radius:10px;flex:1;min-width:200px;">'
            '<div style="font-size:14px;opacity:0.8;">年度累计客流</div>'
            '<div style="font-size:36px;font-weight:bold;">' + str(stats['ytd']) + '</div>'
            '<div style="font-size:14px;">目标 ' + str(ANNUAL_TARGET) + ' | 进度 ' + str(round(stats['progress'],1)) + '%</div></div>'
        )
        if latest is not None:
            date_str = latest['日期'].strftime('%m-%d')
            cards += (
                '<div style="background:#27ae60;color:white;padding:20px;border-radius:10px;flex:1;min-width:200px;">'
                '<div style="font-size:14px;opacity:0.8;">最新日客流 (' + date_str + ')</div>'
                '<div style="font-size:36px;font-weight:bold;">' + str(latest['合计']) + '</div>'
                '<div style="font-size:14px;">累计天数: ' + str(len(df)) + '天</div></div>'
            )
        cards += '</div>'
    
    html = (
        '<!DOCTYPE html><html><head><meta charset="utf-8">'
        '<title>电影小镇运营看板</title>'
        '<meta http-equiv="refresh" content="300">'
        '<style>'
        'body{margin:0;background:#f5f6fa;font-family:-apple-system,BlinkMacSystemFont,sans-serif}'
        '.header{background:linear-gradient(135deg,#2c3e50,#3498db);color:#fff;padding:30px;text-align:center}'
        '.header h1{margin:0;font-size:28px}'
        '.header p{margin:5px 0 0;opacity:.8;font-size:14px}'
        '.nav{display:flex;justify-content:center;gap:15px;padding:15px;background:#fff;border-bottom:1px solid #ddd}'
        '.nav a{color:#3498db;text-decoration:none;font-size:14px;padding:8px 16px;border-radius:20px}'
        '.nav a:hover{background:#3498db;color:#fff}'
        'iframe{width:100%;height:700px;border:none}'
        '</style>'
        '<script>'
        'setInterval(function(){'
        'var f=document.getElementsByTagName("iframe");'
        'for(var i=0;i<f.length;i++){f[i].contentWindow.location.reload()}'
        '},300000);'
        '</script>'
        '</head><body>'
        '<div class="header"><h1>🎬 建业电影小镇 · 运营数据看板</h1>'
        '<p>年度目标 ' + str(ANNUAL_TARGET) + ' | 数据：客流CSV + 抖音指数</p></div>'
        + cards +
        '<div class="nav">'
        '<a href="daily_trend.html" target="main">📊 日客流</a>'
        '<a href="weekly_trend.html" target="main">📈 周度</a>'
        '<a href="douyin_rank.html" target="main">🎯 抖音指数</a>'
        '</div>'
        '<iframe name="main" src="daily_trend.html"></iframe>'
        '<p style="text-align:center;color:#999;font-size:12px;padding:10px;">更新: ' + now + '</p>'
        '</body></html>'
    )
    with open(OUTPUT_DIR + "/index.html", 'w') as f:
        f.write(html)

# ========== MAIN ==========
if __name__ == "__main__":
    from plotly.subplots import make_subplots
    
    print("📊 加载数据...")
    result = load_visitor()
    df, stats = result if result[0] is not None else (None, None)
    
    if df is not None:
        print("   读取", len(df), "天数据, 年度累计", stats['ytd'])
        chart_daily(df)
        chart_weekly(df)
    
    chart_douyin()
    build_index(df, stats)
    print("✅ 看板HTML已生成")
    
    # 启动服务器
    os.chdir(OUTPUT_DIR)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print("\n🌐 访问看板: http://localhost:" + str(PORT))
        webbrowser.open("http://localhost:" + str(PORT))
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 服务已停止")
