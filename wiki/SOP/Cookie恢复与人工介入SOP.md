# Cookie 健康异常恢复 SOP（2026-06-22 W26 新增）

> **触发条件**：Cookie 健康检查 cron（每日 09:00，ID `dee74616-8d05-4c57-b17b-1f8e17c31352`）检测到异常并推送飞书告警卡片到电影小镇群 `oc_2581c03b79e4893cc3616b253d60f34e`。
> **目标**：把"发现 cookie 失效 → 恢复采集"的 MTTR 从小时级降到分钟级。

---

## 📊 异常分类与恢复动作（4 类）

### 类型 1：Cookie 文件陈旧（> 6h 未更新）

**告警样本**：
```
⚠️ douyin cookie 陈旧 (7.3h 前回写，阈值 6h)
```

**根因**：CDP Cookie 同步 cron 失败 / Chrome 未登录 / 浏览器被关闭

**站长动作（30s 内）**：
```bash
# 强制重新同步（直接读 Chrome 当前登录态写到 /tmp）
python3 ~/.openclaw/workspace/scripts/cdp_cookie_hub.py
```
- 若返回 ok → 看是否生成新的 mtime
- 若仍失败 → 跳到类型 2（登录态失效）

---

### 类型 2：Cookie 跳登录页（最常见）

**告警样本**：
```
🚨 douyin cookie 已失效（跳转到登录页）
```

**根因**：抖音/小红书 token 过期 / 浏览器 session 被踢出

**站长动作（2min）**：
1. **打开专属 Chrome**（CDP 18800）
2. 访问告警中的域名（`creator.douyin.com` 或 `idea.xiaohongshu.com`）
3. **扫码登录**（手机端飞书/抖音/小红书都行）
4. 登录成功后，回到终端跑：
   ```bash
   python3 ~/.openclaw/workspace/scripts/cdp_cookie_hub.py
   ```
5. 验证：
   ```bash
   python3 ~/.openclaw/workspace/scripts/cookie_health_check.py --quiet
   ```
   - exit 0 = 恢复成功
   - exit 1 = 仍异常，看新告警

---

### 类型 3：CDP 18800 断

**告警样本**：
```
❌ CDP 18800: [Errno 61] Connection refused
```

**根因**：Chrome 进程退出 / 18800 端口被占用 / 系统重启

**站长动作（1min）**：
1. 检查 Chrome 是否在运行：
   ```bash
   lsof -nP -iTCP:18800 -sTCP:LISTEN
   ```
   - 无输出 → Chrome 没起
   - 有输出但 cron 报错 → 端口冲突

2. **方案 A：Chrome 没起**
   - 启动 Chrome，开启远程调试：
     ```bash
     /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=18800 --user-data-dir=~/.openclaw/chrome-profile-18800
     ```
   - 等 3 秒，访问 `chrome://inspect/#devices` 确认 CDP 在线

3. **方案 B：端口冲突**
   - 看谁占用：`lsof -nP -iTCP:18800`
   - kill 占用进程后重启 Chrome

4. 验证：
   ```bash
   python3 ~/.openclaw/workspace/scripts/cookie_health_check.py --quiet
   ```

---

### 类型 4：Proxy 7897 死

**告警样本**：
```
⚠️ 代理 7897: 代理进程不存在（如脚本走 CDP 直连则无影响）
```

**根因**：ClashX/Surge 等代理客户端被关闭 / 系统重启后未自动启动

**站长动作（10s）**：
1. 启动代理客户端（推荐 ClashX Pro 或 Surge）
2. 确认 7897 端口 LISTEN：
   ```bash
   lsof -nP -iTCP:7897 -sTCP:LISTEN
   ```
3. **判断是否必须修**：
   - 如果抖音/小红书采集脚本**走 CDP 18800 直连 Chrome**（当前架构）→ 代理死**不影响采集**，可以延后修
   - 如果有脚本**走代理链路**（curl/wget/requests）→ 必须立即修

---

---

## 📞 何时需要人工介入更深

| 情况 | 建议 |
|---|---|
| 同一类异常**连续 3 天**发生 | 说明根因没解决（可能是 Chrome 配置漂移/账号被风控），需要排查 Chrome profile |
| 抖音/小红书账号**被风控**（扫码后立即被踢） | 切换账号 / 降低采集频率 / 联系平台 |
| Chrome 反复崩溃 | 看 `chrome-profile-18800/` 是否过大（> 500MB 清一下） |
| Proxy 7897 反复死 | 系统启动加代理客户端自启（System Settings → Login Items） |

---

## 🔗 相关 cron / 脚本

| 名称 | 路径 / ID | 作用 |
|---|---|---|
| Cookie 健康检查 | cron `dee74616` 09:00 / `scripts/cookie_health_check.py` | 探测异常 + 推飞书 |
| CDP Cookie 同步 | cron `d47fc152` 08:05 / `scripts/cdp_cookie_hub.py` | 把 Chrome cookie 写到 /tmp |
| CDP 健康探针 | cron `3eacd6bb` 08:30 | 验证 Chrome 18800 在线 |

---

## 📈 失效模式统计（每周回顾）

每次异常恢复后，在 `wiki/SOP/Cookie失效案例/` 记录：
- 日期 / 时间
- 类型（1-4）
- 根因
- 恢复时长（从告警到 exit 0）
- 是否影响日报

> 一个月后基于历史失效模式决定是否调整 cron 频率或加新保护。

---

## 📝 历史变更

- 2026-06-22 创建（W26 新增，配套 `cookie_health_check.py` 上线）
---

## 🆕 2026-06-30 H1 收官更新

### **6/30 状态（需介入）**

- ⚠️ **小红书灵犀后台 not_logged_in 连续 3+ 日**（6/17-6/19 起）
- 6/30 采集 `xiaohongshu_建业电影小镇.json` 返回 `search_box_not_found`

### **6/30 行动（站长）**

1. 打开 `https://idea.xiaongshu.com/idea/welcome/index` 扫码登录
2. 等待 cookie 同步到 `/tmp/xiaohongshu_cookies.json`
3. 重跑 `xiaohongshu_crawl.py`

### **6/30 系统恢复状态**

- ✅ 抖音 cookie 健康（6/30 08:34 同步）
- ⚠️ 小红书 cookie 待恢复
- ✅ CDP 18800 LISTEN
- ✅ 代理 7897 LISTEN

### 关联文档

- 灵犀可用性：`wiki/行业知识/小红书灵犀数据可用性状态表.md`
- 脚本实体：`entities/scripts/xiaohongshu_crawl.md`
- 飞书配置：`wiki/技术配置/飞书配置.md`
- H1 一页纸：`memory/2026-06-30-h1-recap.md`
