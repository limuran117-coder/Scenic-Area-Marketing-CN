# 专属浏览器 Tab 操作 SOP

> CDP端口18800，已登录状态，禁止关闭/刷新已有Tab | 2026-04-24制定

---

## CDP 连接方式

```python
from playwright.async_api import async_playwright

browser = await p.chromium.connect_over_cdp("http://127.0.0.1:18800")
ctx = browser.contexts[0]
# 先确认目标Tab
for i, pg in enumerate(ctx.pages):
    print(f"Tab{i}: {pg.url}")
```

---

## Tab0 — 小红书灵犀后台

**URL**：`https://idea.xiaohongshu.com/idea/trend/trendAnalyze`
**登录态**：✅ 已登录
**用途**：采集关键词搜索总量/关联词/上下游词/内容分析

### 操作步骤

1. CDP连接后直接用Tab0（已在此页面）
2. 输入关键词：先JS激活搜索框，再慢速输入
```python
await page.evaluate('''() => {
    const inp = document.querySelector('input.d-text');
    if (inp) { inp.focus(); }
}''')
await page.keyboard.type("关键词", delay=100)
```
3. 按Enter（不要点下拉词，会带后缀）
4. 等待6-8秒数据加载
5. 抓取：搜索总量 + 热门搜索词TOP10 + 上下游词
6. 切换「内容」Tab：用JS点击内容Tab，抓阅读总量+笔记关键词分布

### ⚠️ 注意
- React组件：不能用普通click激活输入框，必须用JS focus
- 每次操作间隔5秒以上
- 灵犀后台下午更新数据，08:00采的是昨日数据

---

## Tab1 — 抖音搜索

**URL**：`https://www.douyin.com/search/`
**登录态**：✅ 已登录
**用途**：搜索抖音内视频/用户/内容热度；竞品爆款视频发现

### 操作步骤

1. 直接用Tab1，已在此页面
2. 在搜索框输入关键词
3. 查看搜索结果（视频/用户/话题分类）
4. 抓取：爆款视频标题/点赞数/评论数

### ⚠️ 注意
- 已登录抖音账号，可以访问完整搜索结果
- 操作间隔3秒以上

---

## Tab2 — 空白页

**URL**：`chrome://new-tab-page/`
**登录态**：无（空白）
**用途**：临时导航页；行业热点采集（新浪/搜狐/36kr等免登录页面）

### 操作步骤

```python
new_pg = await ctx.new_page()  # ✅ 在同一context里创建，有登录态
await new_pg.goto("目标URL")
```

### ⚠️ 注意
- 不要在空白页上直接goto已登录的域名（会覆盖登录态）
- 新建page在当前context里才有登录态
- 用完可以关掉，不影响其他Tab

---

## Tab3 — 百度搜索

**URL**：`https://www.baidu.com/`
**登录态**：✅ 已登录（账号：李思洋912）
**用途**：竞品百度收录数据/营收/年客量/媒体报道/舆情

### 操作步骤

1. 直接用Tab3，已在百度首页
2. 输入URL参数导航：`page.goto("https://www.baidu.com/s?wd=关键词&rn=20")`
3. 抓取：搜索结果摘要/新闻/视频分类

### ⚠️ 注意
- 百度有反爬机制，每次新建URL要间隔3秒以上
- 建议直接拼接URL参数访问，减少页面操作

---

## Tab4 — 抖音指数核心页 ⭐最重要

**URL**：`https://creator.douyin.com/creator-micro/creator-count/arithmetic-index`
**登录态**：✅ 已登录（巨量账号）
**用途**：
1. **抖音指数日报**（10:30）— 直接读「我的订阅」，8个景区搜索/综合指数一览
2. **关键词深度分析**（15:00）— 搜索框输入关键词，采集关联词/人群画像/综合指数

### 操作步骤

#### 读订阅数据（日报用）
```python
# Tab4已在arithmetic-index页面
# 我的订阅显示所有景区的搜索/综合指数
text = await page.evaluate('document.body.innerText')
# 解析文本中的景区名+指数+日环比
```

#### 搜索关键词（关键词分析用）
```python
# 在Tab4搜索框输入
await page.evaluate('''() => {
    // 找搜索框并激活
    const inputs = document.querySelectorAll('input');
    for (const inp of inputs) {
        if (inp.offsetParent !== null && inp.type !== 'hidden') {
            inp.focus();
            return;
        }
    }
}''')
await page.keyboard.type("关键词", delay=100)
await page.keyboard.press("Enter")
await asyncio.sleep(5)
# 等待关联词/人群画像数据加载
```

### 「我的订阅」数据格式（固定内容）
每个订阅景区显示：
```
[景区名]
搜索指数    [数值]    日环比    [%]
综合指数    [数值]    日环比    [%]
```

### ⚠️ 注意
- 停服维护时间：每月10日01:00-07:00（页面有提示）
- 数据下午更新，08:00采集的是昨日数据
- 搜索框输入后等待5秒以上再抓取
- 不要刷新此页面，会丢失当前订阅数据

---

## Tab5 — 小红书探索页

**URL**：`https://www.xiaohongshu.com/explore`
**登录态**：✅ 已登录
**用途**：小红书爆款笔记/博主类型/内容方向

### 操作步骤

1. 直接用Tab5，已在探索页
2. 在搜索框输入关键词（慢速输入）
3. 等页面加载（3秒）
4. 抓取：爆款笔记标题/点赞/收藏/评论

### ⚠️ 注意
- 禁止点击视频类内容（自动播放会锁死DOM）
- 探索页有懒加载，滚动后新内容才出现

---

## Tab对应任务总表

| Tab | 任务 |
|-----|------|
| Tab0 | 小红书灵犀后台数据（搜索总量/关联词） |
| Tab1 | 抖音搜索（爆款视频发现） |
| Tab2 | 临时导航（行业热点/免登录页面） |
| Tab3 | 百度搜索（竞品营收/客量/媒体报道） |
| Tab4 | 抖音指数日报（我的订阅）+ 关键词深度分析（搜索框） |
| Tab5 | 小红书爆款笔记（探索页） |

---

## 通用操作规范

1. **连接CDP后先列Tab**：确认目标Tab是哪一页再操作
2. **用已有Tab不要新建空白页goto**：已有登录态的Tab直接操作，不要goto覆盖
3. **必须新建时用Tab2**：`new_pg = await ctx.new_page()` 在同一context
4. **操作间隔5秒以上**：给页面加载时间
5. **禁止刷新已登录Tab**：会丢失登录态

---

*最后更新：2026-04-24*
