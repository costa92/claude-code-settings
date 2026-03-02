# Pre-Writing Verification Checklist (ZERO TOLERANCE)

**核心原则：验证先行，绝不编造**

- 验证过的内容 → 可以写入文章
- 无法验证的内容 → 标记 "[需要验证]" 或询问用户
- 编造的内容 → 立即拒绝整篇文章

## Trusted Tools Whitelist (Skip Verification)

**Development Tools:**
- Docker, Kubernetes, Git, npm, yarn, pnpm, pip, cargo, Maven, Gradle
- Node.js, Python, Go, Rust, Java, TypeScript, Ruby

**OS & Package Managers:** apt, yum, dnf, brew, pacman, apk, snap

**Common CLI Tools:** curl, wget, ssh, scp, rsync, grep, sed, awk, tar, gzip

**When to verify anyway:**
- Niche flags or options (e.g., `docker run --gpus`)
- Version-specific features (e.g., "Docker 24.0+ only")
- Deprecated commands
- Any command you're unsure about

## Step 1: Tool/Project Research (MANDATORY for non-whitelisted tools)

1. **使用 WebSearch 查找官方文档**
   ```
   WebSearch(search_term="[tool_name] official documentation")
   WebSearch(search_term="[tool_name] GitHub repository")
   ```

2. **验证工具真实存在**
   - 检查官方网站
   - 确认 GitHub 仓库（星标数、维护状态）
   - 阅读 README 和官方文档

3. **理解实际功能**
   - 不要根据工具名称推测功能
   - 不要根据"常识"假设用法
   - 必须从官方文档确认功能

## Step 2: Command/Feature Verification (MANDATORY)

1. **命令存在性验证**
   - 在官方文档中找到该命令
   - 参数、选项与官方文档一致
   - 无法找到文档 → 该命令不存在，不要包含

2. **代码示例验证**
   - 代码是完整可运行的
   - API 用法与官方示例一致
   - 依赖版本明确标注

3. **配置文件验证**
   - 配置项在官方文档中存在
   - 值的格式正确

**Exception**: Whitelisted tools' basic commands can be trusted

## Step 3: Workflow Validation (MANDATORY)

1. **步骤完整性** - 每一步都有官方文档支持
2. **依赖关系验证** - 前置条件、版本兼容性、环境要求
3. **潜在问题标记** - 不确定 → 标记 "[需要验证]"，绝不用"合理假设"填补空白

## Step 4: Link Verification (MANDATORY)

1. **使用 WebFetch 验证链接** - 确认返回 200 状态码
2. **链接类型要求**
   - 官方文档链接（优先）
   - GitHub 官方仓库
   - 经验证的技术博客
   - 社交媒体链接（X/Twitter、微博等）→ 无法通过 WebFetch 验证时，改为纯文字引用（作者 + 平台 + 日期），不放 URL
3. **链接格式** - 使用 `**名称**: https://url`，不使用 `[[Obsidian links]]`

## Step 5: Pre-Generation Report (MANDATORY)

生成文章前，必须向用户报告验证结果：

```markdown
## 内容验证报告

### 已验证工具
- Docker (官方文档: https://docs.docker.com/)

### 受信任工具（白名单）
- Git, npm, curl

### 需要验证的内容
- [工具X] 的高级配置选项

### 处理建议
- 已验证内容将包含在文章中
- 未验证内容已标记或省略
```

## Enforcement Rules

| 情况 | 处理方式 |
|------|---------|
| 编造的命令/功能 | **拒绝整篇文章** |
| 未验证的声明 | **询问用户或省略该部分** |
| 无法验证的工作流 | **标记或移除** |
| 404 链接 | **移除或替换** |
| 有疑问的内容 | **询问用户，绝不猜测** |

## Quick Reference

生成文章前，确保：
- [ ] 所有非白名单工具已通过 WebSearch/WebFetch 验证
- [ ] 所有命令在官方文档中存在
- [ ] 所有代码示例完整可运行
- [ ] 所有链接已验证可访问（HTTP 200）
- [ ] 多步骤教程每一步都有文档支持
- [ ] 已向用户报告验证结果
- [ ] 用户确认继续或已移除未验证内容
