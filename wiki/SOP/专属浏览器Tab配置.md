# 专属浏览器 Tab 配置 SOP

> 已登录的 CDP 浏览器（端口 18800）标签页分配 | 2026-04-24 确认

---

## ⚠️ 核心原则

**禁止关闭任何已登录的 Tab。**
**禁止刷新页面（会丢失登录态）。**

---

## 当前 Tab 分配（已确认）

| Tab | URL | 用途 | 登录态 |
|-----|-----|------|--------|
| **Tab0** | `https://idea.xiaohongshu.com/idea/trend/trendAnalyze` | 小红书灵犀后台：搜索总量/关联词/灵犀趋势 | ✅ 已登录 |
| **Tab1** | `https://www.douyin.com/search/` | 抖音搜索页：可搜索关键词看抖音内视频/用户/内容热度 | ✅ 已登录 |
| **Tab2** | `chrome://new-tab-page/` | 空白页，可新建目标页 | — |
| **Tab3** | `https://www.baidu.com/` | 百度搜索（空白页，待用） | ✅ 已登录 |
| **Tab4** | `https://creator.douyin.com/creator-micro/creator-count/arithmetic-index` | **抖音指数核心页**：左侧有搜索框「请输入您想查询的关键词」+「我的订阅」（所有景区搜索/综合指数）；**这就是抖音指数日报+关键词深度分析的主页** | ✅ 已登录 |
| **Tab5** | `https://www.xiaohongshu.com/explore` | 小红书探索页：笔记搜索/爆款内容 | ✅ 已登录 |

---

## CDP 连接方式

```python
from playwright.async_api import async_playwright

CDP = "http://127.0.0.1:18800"

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP)
        # 列出所有已有Tab
        for ctx in browser.contexts:
            for i, pg in enumerate(ctx.pages):
                try:
                    print(f"Tab{i}: {pg.url}")
                except:
                    pass
```

---

## 脚本对应关系

| 任务 | 应使用的 Tab |
|------|------------|
| 抖音指数日报 | Tab4：直接读取「我的订阅」数据（所有景区搜索/综合指数） |
| 抖音关键词深度分析 | Tab4：在搜索框输入关键词，查询关联词/人群画像/综合指数 |
| 小红书灵犀数据 | Tab0 |
| 小红书笔记搜索 | Tab5（探索页） |
| 百度搜索 | Tab3 |
| 行业热点采集（新浪/搜狐） | Tab2（空白页） |

---

## 操作规范

1. **先列 Tab**：CDP 连接后先 `print(pg.url)` 确认目标 Tab 是哪个
2. **用已有 Tab**：操作 Tab0/Tab3/Tab4/Tab5，不要新建
3. **必须新建时**：用 Tab2（空白页），在同一个 context 里
4. **不要 `goto()` 空白页**：已有登录态的 Tab 直接 `goto()` 会丢失状态

---

## ❌ 禁止事项

- 关闭已登录的 Tab
- 刷新已登录页面（会丢失登录态，需重新扫码）
- 在已登录 Tab 上 `goto()` 其他 URL（会覆盖当前页面）
- 新建 Tab 后不指定 URL 就导航

---

*最后更新：2026-04-24*
