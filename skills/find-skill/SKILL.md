---
name: find-skill
description: 查找并验证已安装的 skills 与 agents 是否正常加载。当用户询问「有哪些 skill」「某个 skill 是否存在」「验证 skill 配置」时使用。
---

# find-skill

列出当前所有可用 skills 与 agents，并验证其加载状态。

## 使用方式

运行以下命令检查配置状态：

```bash
# 列出所有 skill
ls ~/.claude/skills/

# 列出所有 agent
ls ~/.claude/agents/

# 检查插件注册
cat ~/.claude/plugins/installed_plugins.json
```

输出结果后，告知用户各 skill 是否正常加载。
