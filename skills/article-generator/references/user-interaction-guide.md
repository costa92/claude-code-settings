# User Interaction Guidelines

## MANDATORY: Use AskUserQuestion for All User Decisions

When generating articles, you MUST use the `AskUserQuestion` tool to collect user requirements and preferences.

**Core Principle: Gradual Progressive Interaction**

- Ask ONE question at a time
- Wait for user response before proceeding
- Each question should have 2-4 clear options with descriptions
- Adjust follow-up questions based on previous answers
- NEVER ask all questions in a single text message

## When to Use AskUserQuestion

1. **Initial Requirements Gathering** - Topic, audience, length, images
2. **Ambiguous Content Decisions** - Multiple approaches, uncertain details
3. **Image Generation Workflow** - Style, format, quantity
4. **Error Handling and Retries** - Timeout, upload errors, verification failures

## Progressive Interaction Flow

**Step 1: Topic Clarification**
```
Question: "您想写什么主题的技术文章？"
Options:
  - 工具使用教程（如：Docker入门、Git进阶）
  - 技术原理解析（如：React渲染机制、HTTP/3协议）
  - 实战项目分享（如：构建博客系统、API设计）
  - 其他（自定义输入）
```

**Step 2: Audience Selection** (after Step 1)
```
Question: "目标读者是？"
Options:
  - 初学者（需要详细步骤）
  - 开发者（需要代码示例）
  - 架构师（需要设计思路）
```

**Step 3: Content Depth** (adjusted based on Step 2)
```
Question: "期望的文章深度？"
Options:
  - 快速入门（500-1000字）
  - 实战教程（2000-3000字，推荐）
  - 深度解析（4000+字）
```

**Step 4: Image Requirements** (after Step 3)
```
Question: "是否需要生成配图？"
Options:
  - 是 - 封面 + 节奏图（推荐）
  - 仅占位符（稍后添加）
  - 纯文字文章
```

**Step 5: Additional Information** (optional, based on topic complexity)
```
Question: "您可以提供以下哪些补充信息？"
Options:
  - 官方文档链接
  - 真实配置文件示例
  - 个人使用经验
  - 无额外信息（仅基于公开资料）
multiSelect: true
```

## Question Template Examples

### Target Audience Selection
```javascript
AskUserQuestion({
  questions: [{
    header: "受众定位",
    question: "这篇文章的目标读者是？",
    options: [
      { label: "初学者", description: "需要详细的基础知识和步骤说明" },
      { label: "开发者", description: "需要代码示例和最佳实践" },
      { label: "架构师", description: "需要设计思路和性能分析" }
    ],
    multiSelect: false
  }]
})
```

### Image Generation Decision
```javascript
AskUserQuestion({
  questions: [{
    header: "配图方式",
    question: "如何处理文章配图？",
    options: [
      { label: "立即生成（封面 + 节奏图）", description: "自动生成并上传到CDN，一步完成" },
      { label: "仅占位符（稍后添加）", description: "文章中使用HTML注释占位，可后续批量生成" },
      { label: "纯文字文章", description: "不需要配图" }
    ],
    multiSelect: false
  }]
})
```

### Error Recovery
```javascript
AskUserQuestion({
  questions: [{
    header: "失败处理",
    question: "图片生成超时，如何处理？",
    options: [
      { label: "使用现有图片", description: "跳过失败的图片，使用已有资源" },
      { label: "重试生成", description: "调整超时时间或更换提示词后重试" },
      { label: "容错模式", description: "继续生成其他图片，忽略单个失败" }
    ],
    multiSelect: false
  }]
})
```

## Best Practices

1. **Clear Option Labels** — "快速入门（500-1000字）" not "短文章"
2. **Helpful Descriptions** — "完整代码示例和实践步骤" not "包含代码"
3. **2-4 options per question** — Never 5+
4. **Short Headers** — "受众定位" (4 chars) not "请选择目标受众群体"
5. **Contextual Follow-ups** — Adjust next question based on previous answer
6. **ONE question at a time** — Each focuses on ONE decision point
