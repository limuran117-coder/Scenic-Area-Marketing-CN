# Bytebot Skill

通过Bytebot AI Desktop Agent执行浏览器自动化任务。

## 配置

**Bytebot API地址**: http://localhost:9991

**支持的模型**: claude-sonnet-4-20250514

## 工具

### Bash(bytebot:*)

调用Bytebot REST API创建和管理任务。

## 使用方法

### 创建任务

```bash
curl -X POST http://localhost:9991/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "description": "你的任务描述",
    "model": "claude-sonnet-4-20250514"
  }'
```

### 查询任务状态

```bash
curl http://localhost:9991/tasks/{task_id}
```

### 获取任务结果

```bash
curl http://localhost:9991/tasks/{task_id}/messages
```

## 示例任务

- "打开抖音创作者平台并搜索关键词XXX"
- "截取当前桌面截图"
- "打开浏览器访问指定URL并获取页面内容"

## 状态

- API: http://localhost:9991
- UI: http://localhost:9992
- Desktop VNC: http://localhost:9990/vnc
