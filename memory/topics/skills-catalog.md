# 已安装Skill目录（2026-06-06更新）

## 位置
- 系统技能：`~/.npm-global/lib/node_modules/openclaw/skills/`（50+个，含天气/GitHub/飞书/视频帧等）
- 工作区技能：`~/.openclaw/workspace/skills/`（24个，景区运营专用）

## 工作区技能清单

### 🔴 核心运营（6个，每日使用）
| 技能 | 用途 | 状态 |
|------|------|------|
| **data-integrity-check** | 数据采集前校验cookie/代理/文件 | ✅ 6/5新增 |
| **task-audit** | 任务完成后审计卡片送达+数据正确性 | ✅ 6/5新增 |
| **daily-task-template** | 标准化cron任务模板（A/B/C类） | ✅ 6/5新增 |
| **skill-router** | 意图识别→技能匹配 | ✅ 激活 |
| **competitor-analyst** | 竞品分析框架 | ✅ 激活 |
| **ai-researcher** | 深度研究助手 | ✅ 激活 |

### 🟡 规范与知识（5个）
| 技能 | 用途 | 状态 |
|------|------|------|
| **karpathy-guidelines** | 四大原则（Think/Surgical/Simple/Goal） | ✅ 日常引用 |
| **karpathy-wiki** | 知识库INGEST/QUERY/LINT | ✅ 按需使用 |
| **karpathy-coding-guidelines** | 代码层面规范 | ✅ 写脚本时引用 |
| **llm-wiki-maintainer** | Wiki维护辅助 | 🔧 备用 |
| **react-best-practices** | React规范 | ⚪ 不适用 |

### 🟢 维护与自动化（3个）
| 技能 | 用途 | 状态 |
|------|------|------|
| **system-metabolism** | 周日自动体检+修剪 | ✅ 6/5新增 |
| **agent-automation-scripter** | 自动化脚本模板 | 🔧 备用 |
| **api-tester** | API测试 | 🔧 按需 |

### 🔵 采集工具（3个）
| 技能 | 用途 | 状态 |
|------|------|------|
| **xiaohongshu-crawler** | 小红书内容爬取 | ✅ 激活 |
| **browser-automation** | 浏览器自动化指南 | ✅ Playwright为主 |
| **agentgo-browser** | 云端浏览器（备用） | ⏸️ 未启用 |

### ⚪ 其他（7个）
| 技能 | 用途 | 状态 |
|------|------|------|
| **agent-spawner** | Agent生成器 | 🔧 备用 |
| **ai-web-automation** | AI网页自动化 | ⚪ 已不适用 |
| **claude-api-cost-optimizer** | Claude成本优化 | ⚪ 非Claude模型 |
| **claude-code-claude-api-builder** | Claude API集成 | ⚪ 非Claude模型 |
| **frontend-design-3** | 前端设计 | ⚪ 不适用 |
| **huashu-design** | HTML原型设计 | ⚪ 不适用 |
| **wechat-miniprogram-skill** | 微信小程序 | ⚪ 不适用 |

## 系统技能精选（按需调用）

| 技能 | 用途 | 触发场景 |
|------|------|---------|
| **weather** | wttr.in天气查询 | 日报附加天气 |
| **github** | GitHub CLI操作 | 代码推送 |
| **feishu-doc/drive/wiki** | 飞书文档操作 | 飞书内容管理 |
| **video-frames** | ffmpeg视频帧提取 | 竞品视频分析 |
| **spike** | 快速原型验证 | 新数据源评估 |
| **diagram-maker** | SVG图表生成 | 季度报告可视化 |
| **gh-issues** | GitHub Issue管理 | 项目管理 |

## 当前架构（2026-06现状）

```
主Agent（李涯/佛龛）
├── 8个cron日常任务（抖音指数/竞品分析/复盘等）
├── 数据采集：Playwright脚本（douyin_index_v9.py等）
├── 质量保证：data-integrity-check → task-audit
├── 标准化：daily-task-template
├── 维护：system-metabolism（周日09:00）
└── 路由：skill-router
```

**已淘汰的旧架构：** 子Agent模式（douyin-agent/xiaohongshu-agent等）已不再使用，所有任务由主Agent通过cron直接执行。
