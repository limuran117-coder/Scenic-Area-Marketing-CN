# Wiki Log

> 追加式操作记录 | `grep "^## \[" wiki/log.md | tail -20` 查看最近20条

---

## [2026-04-18] skill_install | 安装karpathy-guidelines
- 安装来源：multica-ai/andrej-karpathy-skills
- 安装路径：~/.openclaw/workspace/skills/karpathy-guidelines/SKILL.md
- 同步内容：4大原则 + 反模式速查表 + 本项目应用指南
- 状态：✅ 生效中

## [2026-04-18] skill_install | 安装karpathy-wiki + karpathy-project-wiki
- 安装来源：toolboxmd/karpathy-wiki
- 安装路径：~/.openclaw/workspace/skills/karpathy-wiki/ + karpathy-project-wiki/
- 包含：SKILL.md + hooks.json + references/operations.md + scripts/check-wiki-drift.sh
- 差异：karpathy-wiki=通用知识库，karpathy-project-wiki=代码库专属（git diff驱动）
- 状态：✅ 生效中

## [2026-04-18] wiki_structure | 建立Wiki追加结构
- 新增目录：concepts/ / entities/ / queries/ / raw/
- 新增文件：wiki/log.md（追加式操作记录）
- 参考：toolboxmd/karpathy-wiki 架构
- 状态：✅ 完成
