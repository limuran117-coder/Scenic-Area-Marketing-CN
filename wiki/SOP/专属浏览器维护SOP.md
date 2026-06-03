# 专属浏览器维护SOP

> 适用版本：OpenClaw v2026.4.20+
> 维护者：AI助手 + 站长协同
> 最近更新：2026-04-22

---

## 核心概念

专属浏览器 = OpenClaw Gateway管理的Chrome实例（profile: openclaw）
- 端口：18800（CDP）
- 有独立Cookie存储，与站长日常Chrome隔离
- **站长不会关闭自己的Chrome**，因此Browser MCP一直可用

---

## 启动专属浏览器

### 方式A：OpenClaw自动启动（推荐）

```bash
openclaw browser start
```
Gateway自动启动Chrome with remote debugging。

### 方式B：手动启动（Gateway重启后）

```bash
# 查找Chrome
which "Google Chrome"

# 启动专属Chrome（18800端口）
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome \
  --remote-debugging-port=18800 \
  --user-data-dir="$HOME/.openclaw/browser/openclaw/user-data"
```

### 验证启动成功

```bash
curl -s http://127.0.0.1:18800/json/version
```

---

## 5个专属Tab位（已登录）

| Tab序号 | 用途 | 标题 | targetId |
|---------|------|------|----------|
| Tab0 | 百度搜索 | 百度一下，你就知道 | F8F91A65FA31E941412C277FB523EAAD |
| Tab1 | 抖音订阅页 | 抖音创作者中心 | 068C1DC031579CE3302C93057DBDE499 |
| Tab3 | 抖音关键词 | 抖音创作者中心 | 644318A4DF1B58F75659DD93CD0E91E4 |
| Tab4 | 小红书灵犀 | 趋势分析 - 小红书灵犀 | 8C06181FE90B33BB283BEB46146DFC25 |
| Tab5 | 小红书探索 | 小红书 - 你的生活兴趣社区 | 979670A566A0F434E489BC3C461583C2 |

> ⚠️ 每次重启后 targetId 会变化，以tabs命令查到的为准。

---

## 打开/关闭标签页

### 查看当前所有Tab

```python
browser(action="tabs", profile="openclaw", target="host")
```

### 打开新Tab

```python
browser(action="open", profile="openclaw", target="host",
        url="https://creator.douyin.com/creator-micro/creator-count/arithmetic-index")
```

### 关闭Tab

```python
browser(action="close", profile="openclaw", target="host",
        targetId="<targetId>")
```

### 关闭自动生成的iframe标签

每次用 `browser.open()` 打开抖音相关URL时，会自动生成summon.bytedance.com iframe，**立即关闭**：

```python
browser(action="close", targetId="<iframe_targetId>")
```

判断方法：`tabs`返回结果中 `type: "iframe"` 的都是，需要关闭。

---

## 登录状态维护

专属浏览器使用独立profile，**每次重启后需要重新登录**：

需要登录的平台：
1. 抖音创作者后台（Tab1/Tab3）：https://creator.douyin.com
2. 小红书（Tab5）：https://www.xiaohongshu.com
3. 小红书灵犀（Tab4）：https://idea.xiaohongshu.com

### 登录后保存状态

登录后正常关闭浏览器即可，下次启动时Cookie保留。

---

## 故障排查

### 症状：browser工具连接失败

```
Error: Could not connect to Chrome. Check if Chrome is running.
Cause: Could not find DevToolsActivePort...
```

**解决步骤：**

1. 检查端口是否在监听：
```bash
curl -s http://127.0.0.1:18800/json/version
```

2. 如果没有输出 → Chrome未启动 → 执行「启动专属浏览器」

3. 如果有输出但工具仍报错 → Gateway未正确attach
   → 重启Gateway：`openclaw gateway restart`

4. 如果Chrome启动但端口不对
   → 检查是否有多个Chrome实例：`pgrep -fl "Chrome"`
   → 杀死所有Chrome重新启动

### 症状：Tab打开但内容空白

Cookie过期，需要重新登录该平台。

### 症状：操作时Chrome无响应

可能是页面加载超时，等5秒后重试。如果持续无响应，关闭并重新打开对应Tab。

---

## 浏览器技术栈原则（2026-04-20确立）

**定时自动任务**：一律用 Playwright 脚本，不依赖 browser-use CLI
- 抖音数据采集 → `douyin_index_v9.py`（Playwright）
- 竞品动态追踪 → `competitor_program_tracker.py`（Playwright）

**browser-use 使用规则**：
- **全面禁止**：包括专属 Chrome 标签页的任何操作，一概拒绝
- **唯一例外**：临时性/没遇到过/复杂的探索任务（新平台/一次性调研），且 Playwright 脚本无法快速覆盖时，才能用

---

## OpenClaw版本更新后的注意事项

v2026.4.20 更新后：
- Browser MCP 的 `DevToolsActivePort` 报错更明确
- 专属浏览器配置（user-data-dir）不会因更新丢失
- Gateway 重启会自动重建 browser MCP 连接

**不需要重新配置**，只需确认Chrome进程在运行即可。
