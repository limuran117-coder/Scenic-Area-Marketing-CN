# Claude Code 集成 Skill

通过OpenClaw调用Claude Code执行复杂任务。

## 配置

环境变量：
```bash
export ANTHROPIC_API_KEY=sk-zglHU9ZY0pcsrE0HbW9UwNsm6pHBrYaSW2CWYGm4H3Ws2l1x
```

## 使用方法

### 方式1：通过sessions_spawn启动Claude Code子Agent

```javascript
sessions_spawn({
  task: "执行任务描述",
  runtime: "subagent",
  mode: "run"
})
```

### 方式2：通过exec调用Claude Code CLI

```bash
export ANTHROPIC_API_KEY=sk-zglHU9ZY0pcsrE0HbW9UwNsm6pHBrYaSW2CWYGm4H3Ws2l1x
claude -p "你的任务描述" --output-format stream 2>/dev/null
```

### 方式3：使用已安装的APEX Stack框架

已安装的增强框架：
- `apex-stack-claude-code` - APEX认知框架
- `agent-swarm-ex` - 多Agent编排
- `browser-agent` - 浏览器自动化

## 适用场景

- 复杂代码生成和调试
- 多步骤自动化任务
- 需要强推理能力的任务
- 代码审查和重构

## 状态

- Claude Code CLI: 已安装 v2.1.101
- API Key: 已配置
- 子Agent支持: sessions_spawn可用
