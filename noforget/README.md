# No Forget · 记住每一个重要时刻

<div align="center">

![WeChat Miniprogram](https://img.shields.io/badge/WeChat-小程序-v1.0-blue?style=flat-square&logo=wechat)
![Platform](https://img.shields.io/badge/Platform-微信小程序-green?style=flat-square&logo=weixin)
![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square&logo=opensourceinitiative)
![Cloud](https://img.shields.io/badge/Cloud-腾讯云CloudBase-purple?style=flat-square&logo=serverless)
![Node](https://img.shields.io/badge/Node.js-18.15-orange?style=flat-square&logo=node.js)

**一款以「裂变传播」为核心设计目标的纪念日小程序**
**每一次打卡，都是一张博物馆级画报的诞生**

</div>

---

## ✨ 核心功能

### 🖼️ 哈苏画廊级纪念画报
- **严格比例裁切**：750:650 固定比例，绝不变形
- **拍立得质感**：纯白相框 + 物理投影悬浮感
- **四色色卡系统**：每个分类拥有专属强调色
- **双模式生成**：使用当前封面 or 上传专属背景

### ⏳ 正向计时 × 倒数未来
- **双向时间模式**：点击「累计时光」自动回拨100天
- **实时刷新**：倒计时精确到时分秒

### 🥠 浅草寺灵签盲盒
- 15条浅草寺风格灵签（大吉/吉/半吉/小吉/末吉/平）
- 盲盒抖动动画 + 震动反馈
- 每小时刷新机制

### 📅 每日黄历
- 本地农历算法 + 真实节气节日
- 百度百科「历史上的今天」
- 传统宜忌 + 现代版提示

### 💧 姨妈追踪
- 姨妈记录与预测
- 统计分析与提醒
- 云端同步

---

## 🏗️ 技术架构

### 前端
```
微信小程序 · WXML/WXSS/JS
├── pages/
│   ├── index/          # 首页纪念日列表
│   ├── add/            # 新建/编辑纪念日
│   ├── detail/         # 纪念日详情+画报生成
│   ├── almanac/        # 每日黄历+灵签
│   ├── period/         # 姨妈记录
│   └── mine/           # 个人中心
├── components/         # 卡片/主题选择器
└── utils/
    ├── countdown.js    # 核心倒计时计算
    ├── countdownStore.js # 数据存储+云同步
    ├── period.js        # 姨妈计算
    └── periodCloud.js   # 姨妈云同步
```

### 云端（CloudBase）
```
环境ID: cloud1-d5gxwed6aa4581e97
地域: ap-shanghai（上海）

云函数（Node.js 18.15）:
├── countdown-sync    # 纪念日CRUD + 云端同步
├── period-sync      # 姨妈记录CRUD
├── send-reminder    # 定时提醒推送（每天09:00）
├── get-slogan       # 每日一言
└── ai-chat          # AI闲聊

云数据库:
├── countdown-sync    # 纪念日集合（按openId隔离）
└── period-sync      # 姨妈记录集合
```

### 数据隔离
- 每个用户数据通过 `openId` 严格隔离
- 云函数调用需微信登录态验证
- 数据库读写规则：仅用户本人可访问自己的数据

---

## 🚀 快速开始

### 环境要求
- Node.js ≥ 18.15
- 微信开发者工具 ≥ 1.06+
- 腾讯云 CloudBase CLI

### 本地开发

```bash
# 克隆项目
git clone https://github.com/limuran117-coder/NO-FORGET.git
cd NO-FORGET

# 安装依赖（如需要）
npm install

# 使用微信开发者工具打开项目
# 导入路径: /path/to/NO-FORGET
# AppID: wxbc9d6a843f482a34

# 开通云开发
# 微信开发者工具 → 云开发 → 开通 → 关联环境 cloud1-d5gxwed6aa4581e97
```

### 部署云函数

```bash
# 安装 CloudBase CLI
npm install -g @cloudbase/cli

# 登录
tcb login

# 部署所有云函数
tcb fn deploy --services

# 或单独部署
tcb fn deploy countdown-sync -e cloud1-d5gxwed6aa4581e97
tcb fn deploy period-sync -e cloud1-d5gxwed6aa4581e97
tcb fn deploy send-reminder -e cloud1-d5gxwed6aa4581e97
```

### 配置

在 `cloudbaserc.json` 中确认环境ID：

```json
{
  "envId": "cloud1-d5gxwed6aa4581e97",
  "region": "ap-shanghai"
}
```

---

## 📁 项目结构

```
noforget/
├── app.js / app.json / app.wxss    # 小程序入口
├── cloud/                           # 云函数源码
│   ├── countdown-sync/              # 纪念日云函数
│   ├── period-sync/                 # 姨妈云函数
│   ├── send-reminder/              # 定时提醒
│   ├── get-slogan/                 # 每日一言
│   └── ai-chat/                   # AI闲聊
├── pages/                           # 页面
│   ├── index/                      # 首页
│   ├── add/                        # 新建/编辑
│   ├── detail/                     # 详情+画报
│   ├── almanac/                    # 黄历
│   ├── period/                     # 姨妈
│   └── mine/                       # 个人中心
├── components/                      # 组件
│   ├── card/                       # 纪念卡片
│   ├── tab-bar/                    # 底部导航
│   └── theme-picker/               # 主题选择
├── utils/                           # 工具函数
│   ├── countdown.js                # 倒计时核心算法
│   ├── countdownStore.js           # 存储+云同步
│   ├── period.js                   # 姨妈计算
│   └── icons.js                    # emoji图标库
├── cloudbaserc.json                # 云环境配置
└── project.config.json             # 项目配置
```

---

## 🧪 测试

### 测试方案
详见 `docs/测试方案-专业版.md`

### 测试模块
| 模块 | 内容 |
|------|------|
| A1-A6 | 前端UI交互测试（26个用例） |
| B1-B3 | 云函数测试（17个用例） |
| C | 数据库安全测试（10个用例） |
| D | 压力与异常测试（10个用例） |

### 通过标准
```
P0缺陷（数据丢失/隐私泄露）：0个
P1缺陷（功能失效）：<3个
P2缺陷（体验问题）：<10个
覆盖率：100%
```

---

## 🔧 开发规范

### 代码风格
- JS: ES6+，禁用 `var`
- WXSS: BEM命名，组件级样式隔离
- 异步: 全部 `async/await`，禁用回调

### Git提交规范
```
feat: 新功能
fix: Bug修复
docs: 文档更新
style: 代码格式（不影响功能）
refactor: 重构
test: 测试相关
chore: 构建/工具
```

### 云函数开发
```javascript
// 云函数模板
const cloud = require('wx-server-sdk');
cloud.init({ env: cloud.DYNAMIC_CURRENT_ENV });

exports.main = async (event, context) => {
  const { action, data } = event;
  const openId = cloud.getWXContext().OPENID;

  switch (action) {
    case 'upsert':
      return await upsertItem(openId, data);
    case 'getItems':
      return await getItems(openId);
    case 'delete':
      return await deleteItem(openId, data.itemId);
    default:
      throw new Error('Unknown action');
  }
};
```

---

## 📊 版本记录

### v1.1.x（2026-05 进行中）
- ✅ Canvas画报生成（1080×1440）
- ✅ 正向/倒数双向计时
- ✅ 姨妈追踪
- ✅ 云函数数据同步
- ✅ 每日黄历+灵签
- 🔧 防御性编程强化（iOS NaN防护）
- 🔧 UI交互完整性
- 🔧 多设备同步一致性

### v1.2（2026-06-03 体系加固）

**V4 Pro 全量评审修复（20项中完成16项）**

- ✅ **get-slogan云函数瘦身**：76MB→3MB，冷启动从8s降至<1s
- ✅ **parseDateSafe去重**：5份独立实现→1份全局模块
- ✅ **WXS替代详情页倒计时**：每秒setData 5字段→视图层零开销
- ✅ **数据导出PIN加密**：4位XOR加密保护隐私
- ✅ **数据注销**：3次确认+本地清除+云端deleteAll
- ✅ **period-sync冲突合并升级**：按updatedAt取最新版本
- ✅ **get-slogan限流**：每分类/用户60秒3次上限
- ✅ **copyTemplates缓存**：文案按周缓存，避免页面切换变化
- ✅ **env ID集中化**：硬编码移至config/constant.js
- ✅ **scope.userLocation权限删除**：未使用，降低审核风险
- ✅ **onLoad农历延迟渲染**：setTimeout 100ms，不阻塞首帧
- ✅ **periodData容量监控**：接近1MB上限告警

### v1.0（2026-04 初始版本）
- 纪念日CRUD
- 分类主题系统
- 基础倒计时

---

## 👥 团队

- **开发者**: 李涯（AI助手）
- **测试**: Codex
- **产品**: 站长

---

## 📄 License

MIT License · 2026

---

*记住每一个重要时刻 · No Forget*
