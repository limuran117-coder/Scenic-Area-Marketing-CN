# Bytebot API Skill

通过REST API调用Bytebot AI Desktop Agent执行复杂任务。

## 🚀 Railway 部署信息（2026-04-13）

| 服务 | URL |
|------|-----|
| bytebot-ui | https://bytebot-ui-production-80a2.up.railway.app |
| **bytebot-agent** | **https://bytebot-agent-production-3ecc.up.railway.app** |
| bytebot-desktop | https://bytebot-desktop-production-a79b.up.railway.app |
| Postgres | 数据库（内部服务） |

## 工具

### 创建任务

```bash
curl -X POST https://bytebot-agent-production-3ecc.up.railway.app/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "任务描述",
    "model": "claude-sonnet-4-20250514"
  }'
```

### 查询结果

```bash
curl https://bytebot-agent-production-3ecc.up.railway.app/tasks/{task_id}
```

## 已配置

- API Key: sk-zglHU9ZY0pcsrE0HbW9UwNsm6pHBrYaSW2CWYGm4H3Ws2l1x
- Agent URL: https://bytebot-agent-production-3ecc.up.railway.app

## 使用方法

1. 创建任务：`POST /tasks`
2. 查询状态：`GET /tasks/{task_id}`
3. 桌面预览：`https://bytebot-desktop-production-a79b.up.railway.app`
