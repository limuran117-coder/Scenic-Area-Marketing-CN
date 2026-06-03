# No Forget · 记住每一个重要时刻

<div align="center">

![WeChat Miniprogram](https://img.shields.io/badge/WeChat-小程序-blue?style=flat-square&logo=wechat)
![Platform](https://img.shields.io/badge/Platform-微信小程序-green?style=flat-square)
![Cloud](https://img.shields.io/badge/Cloud-腾讯云CloudBase-purple?style=flat-square&logo=serverless)

**纪念日倒数 · 姨妈追踪 · 画报生成**

</div>

---

## ✨ 当前功能

| 模块 | 状态 | 说明 |
|------|------|------|
| 🎂 纪念日管理 | ✅ | CRUD + 10分类系统 + 双向倒计时/正向累计 |
| 🖼️ 纪念画报 | ✅ | Canvas生成+照片裁切+双模式（封面/上传） |
| 💧 姨妈追踪 | ✅ | 记录+预测算法+月历+每日症状+云端同步 |
| 🔔 微信提醒 | ✅ | 订阅消息推送（姨妈+纪念日） |
| 🤖 AI聊天 | ✅ | MiniMax模型客服助手 |
| 🥠 灵签/黄历 | ❌ | 子包代码不在此仓库（独立subpackages目录） |
| 🌐 多主题 | ⏸️ | 主题框架已预留，仅`apple`风格 |

---

## 🏗️ 实际代码结构

```
noforget/
├── app.js / app.json          # 小程序入口（含页面注册+tabBar）
├── cloud/                     # 云函数（5个）
│   ├── countdown-sync/        # 纪念日数据CRUD
│   ├── period-sync/           # 姨妈数据CRUD
│   ├── send-reminder/         # 定时提醒（9:00触达）
│   ├── get-slogan/            # AI随机文案（混元大模型+本地池）
│   └── ai-chat/               # MiniMax API客服
├── pages/                     # 页面（5个）
│   ├── index/                 # 首页 - 纪念日列表（JS only）
│   ├── detail/                # 详情+画报生成（JS+WXML+WXS）
│   ├── mine/                  # 个人中心（JS+WXML）
│   ├── period/                # 姨妈追踪+统计+设置（JS only）
│   └── reminder/              # 提醒设置（JS only）
├── utils/                     # 工具模块（6个）
│   ├── countdown.js           # 倒计时核心算法
│   ├── copyTemplates.js       # 分类文案模板
│   ├── date-utils.js          # 日期解析统一模块
│   ├── period.js              # 姨妈预测算法
│   ├── periodCloud.js         # 姨妈云同步
│   └── subscribe-helper.js    # 订阅消息助手
├── config/
│   └── constant.js            # 全局常量（env ID/模板ID/周期配置）
├── docs/
│   └── 修复报告-20260601.md    # V4 Pro全量评审报告
└── cloudbaserc.json           # 云环境配置
```

> ⚠️ 注意：WXML/WXSS 文件目前仅 detail 和 mine 页面齐全，index/period/reminder 仅有 JS 逻辑。该项目为后端逻辑主导的开发模式。

---

## ☁️ 云函数一览

| 函数 | 作用 | 调用方式 |
|------|------|---------|
| `countdown-sync` | 纪念日增删改查+云端同步 | 前端读写 | 
| `period-sync` | 姨妈数据云端存取+注销 | 前端读写 |
| `send-reminder` | 每日9:00推送姨妈+纪念日提醒 | 定时触发器 |
| `get-slogan` | 随机走心文案（混元AI/本地池双源） | 前端加载时调用 |
| `ai-chat` | MiniMax模型客服（用户问答） | 用户触发 |

### 数据库

| 集合 | 用途 | 安全规则 |
|------|------|---------|
| `countdownItems` | 纪念日数据 | `_openid` 隔离 |
| `periodData` | 姨妈数据（单文档/用户） | `_openid` 隔离 |
| `ai_chat_logs` | AI对话记录 | 仅新增 |

---

## 🚀 部署

### 环境要求
- 微信开发者工具
- 腾讯云 CloudBase CLI
- Node.js ≥ 18.15

### 云函数部署
```bash
tcb login
tcb fn deploy countdown-sync -e cloud1-d5gxwed6aa4581e97
tcb fn deploy period-sync -e cloud1-d5gxwed6aa4581e97
tcb fn deploy send-reminder -e cloud1-d5gxwed6aa4581e97
tcb fn deploy get-slogan -e cloud1-d5gxwed6aa4581e97
tcb fn deploy ai-chat -e cloud1-d5gxwed6aa4581e97
```

---

## 🔧 开发规范

| 规则 | 标准 |
|------|------|
| JS | ES6+，`const`/`let`，禁用`var` |
| 异步 | 全部 `async/await`，禁用回调 |
| 云函数 | switch(action) + openid隔离 |
| 安全 | `_openid` 字段自动隔离 |
| 注释 | 修复标注 `✅ P0#1 / ✅ P1#2` 格式 |

---

## 📊 版本记录

### v1.2（2026-06-03 体系加固）
V4 Pro 全量评审，20 项中完成 16 项：

**性能**
- get-slogan 云函数瘦身：76MB→3MB，冷启动 8s→<1s
- WXS 替代详情页每秒 setData：CPU 开销降 95%
- onLoad 农历延迟渲染：首帧不阻塞

**安全**
- 数据导出 PIN 码加密（4 位 XOR）
- 数据注销：三次确认 + 本地清除 + 云端 deleteAll（2 云函数同步支持）

**健壮性**
- parseDateSafe 去重：5 份独立实现→1 份全局 date-utils.js
- period-sync 冲突合并：按 `updatedAt` 取最新版本
- copyTemplates 缓存：文案按周固定，不再页面切换乱跳
- get-slogan 限流：每分类/用户 60 秒 3 次上限
- periodData 容量监控：接近 1MB 告警

**工程**
- env ID 集中化：硬编码移至 config/constant.js（2 处→1 处）
- scope.userLocation 权限删除（未使用，降低审核风险）

### v1.1（2026-05）
- Canvas 画报生成（1080×1440）
- 正向/倒数双向计时
- 姨妈追踪系统（预测+云同步）
- 微信订阅消息提醒
- 防御性编程强化（iOS NaN 防护）

### v1.0（2026-04 初始）
- 纪念日 CRUD
- 分类主题系统（10 分类）
- 基础倒计时

---

## 📄 License

MIT License · 2026

---

*记住每一个重要时刻 · No Forget*
