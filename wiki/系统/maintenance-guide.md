# 维护手册

> 新成员上手指南 + 例行维护项 | 2026-04-28

---

## 一、新成员上手流程

### 1. 环境准备（约30分钟）

**必需工具：**
- Node.js 18+（运行 OpenClaw）
- Python 3.10+（运行 Playwright 采集脚本）
- Git（代码管理）
- Obsidian（Wiki 管理，推荐）
- Chrome（专属浏览器，需保持登录态）

**安装步骤：**
```bash
# 1. 克隆仓库
git clone git@github.com:limuran117-coder/Scenic-Area-Marketing-CN.git
cd Scenic-Area-Marketing-CN

# 2. 安装 OpenClaw
npm install -g openclaw

# 3. 初始化配置
openclaw init

# 4. 验证运行
openclaw status
```

### 2. 配置检查（约10分钟）

**确认以下文件存在且配置正确：**
- `USER.md` — 核心用户配置（飞书群ID、Cookie路径等）
- `MEMORY.md` — 长期记忆（只读，不修改）
- `IDENTITY.md` — Agent身份定义
- `TOOLS.md` — 本地工具备注

**确认以下服务在线：**
- CDP 浏览器（`127.0.0.1:18800`）
- 飞书群机器人（测试发送消息）
- 抖音 Cookie（`/tmp/juLiang_cookies.json`）
- 小红书 Cookie（`/tmp/xiaohongshu_cookies.json`）

### 3. 验证自动化链路（约10分钟）

按顺序触发测试：
```bash
# 1. 测试抖音指数采集
python scripts/douyin_index_v9.py

# 2. 测试飞书卡片发送
python scripts/send_feishu_card.py <chat_id> test

# 3. 测试 cron 任务
openclaw tasks list
```

### 4. 理解 Wiki 结构（约20分钟）

必读文件（按顺序）：
1. `wiki/SOP/抖音指数日报.md` — 核心日报流程
2. `wiki/电影小镇/演出节目/穿越德化街.md` — 核心业务数据
3. `wiki/竞品分析/竞品动态追踪/index.md` — 竞品监控体系
4. `docs/ai-analysis-spec.md` — AI分析逻辑
5. `docs/目录结构说明.md` — 整体结构

---

## 二、每月例行维护项

### 每周
- [ ] 检查 cron 任务执行状态（`openclaw tasks list`）
- [ ] 确认日报/周报正常发出（飞书群消息记录）
- [ ] INGEST 提炼周日执行（自动触发，检查输出）

### 每月
- [ ] 更新竞品关键词列表（如有新增景区/关店/改名）
- [ ] 检查抖音/小红书 Cookie 有效性（提前7天续期）
- [ ] 清理 `wiki/.obsidian/` 本地缓存（不影响 Wiki 内容）
- [ ] 检查 GitHub 仓库大小（`git status`），确认无异常大文件
- [ ] 备份 MEMORY.md（重要！）

### 每季度
- [ ] 更新年度客流目标（如有调整）
- [ ] 竞品深度分析更新（8个竞品轮换）
- [ ] Wiki LINT 检查（`scripts/wiki_drift_check.py`）
- [ ] 知识层概念清理（删除过时/重复概念）

---

## 三、常见问题排查

### 抖音数据采集失败
```
症状：搜索指数为0或报错
排查：
1. 检查 CDP 连接：curl http://127.0.0.1:18800
2. 检查 Cookie 有效期：/tmp/juLiang_cookies.json
3. 重启专属浏览器：openclaw browser stop && openclaw browser start
4. 手动访问抖音创作平台确认登录态
```

### 飞书卡片发送失败
```
症状：脚本执行成功但群里收不到
排查：
1. 检查 chat_id 是否正确（不是 open_id）
2. 检查 Bot 权限（是否有发消息权限）
3. 检查卡片格式（markdown 是否合规）
4. 查看飞书后台日志
```

### Cron 任务不触发
```
症状：定时任务没有执行
排查：
1. 检查任务状态：openclaw tasks list
2. 检查上次执行时间
3. 检查 failureAlert 是否触发（连续失败2次会告警）
4. 查看日志：openclaw logs
```

### Wiki 内容丢失/冲突
```
症状：Wiki 文件消失或 Git 冲突
排查：
1. 不要慌：Wiki 全部在 Git 里，Git pull 恢复
2. 避免多人同时编辑同一文件
3. 每次提交写清楚修改内容
```

---

## 四、权限管理规则

### Wiki 编辑权限
- 所有成员可读
- 修改前先告知团队（避免冲突）
- 每次修改在 Git commit 写清楚改了什么
- 核心文件（`MEMORY.md`、`USER.md`）修改前确认必要性

### 代码库修改
- 不直接 push 到 main 分支
- 通过 commit + PR 流程
- 脚本修改前在本地测试
- 重要配置修改（如飞书群ID）需双重确认

### 敏感信息
- Cookie/Token 不进 Git（已在 .gitignore）
- 密码/密钥只留在本地配置文件
- 飞书群 ID 等半敏感信息进 Git（前缀过滤）

---

## 五、紧急联系人

| 场景 | 处理方式 |
|------|---------|
| 自动化全部停摆 | 检查 OpenClaw Gateway：`openclaw gateway restart` |
| CDP 连接失败 | 重启专属浏览器 Chrome |
| 飞书 Bot 无响应 | 检查飞书开放平台应用状态 |
| 关键数据丢失 | Git 历史恢复：`git log` → `git checkout <commit>` |

---

*由 AI Agent 维护 | 2026-04-28 新建*
