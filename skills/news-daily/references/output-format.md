# Markdown Output Format

This document defines the standard markdown output format for AI Daily news.

**重要要求**：
1. **全部翻译成中文** - 所有英文内容必须翻译成中文
2. **保留原链接** - 每条新闻必须附上原文链接作为备注

---

## Template

```markdown
# AI Daily · {年}年{月}月{日}日

> {一句话核心摘要}

## 核心摘要

{3-5条核心要点，每条一句话}

## {分类名称}

### {中文标题}

{详细摘要，翻译成中文}

**关键信息**: {相关标签}

📎 原文链接: [{来源名称}]({原始URL})

---

数据来源: {来源列表}
生成时间: {YYYY-MM-DD HH:MM}
```

---

## Complete Example

```markdown
# AI Daily · 2026年1月19日

> OpenAI 在 ChatGPT 引入广告，HN 热议 AI 编程对 COBOL 开发者的影响，ArXiv 发布 HPV 疫苗 AI 代理系统研究

## 核心摘要

- OpenAI 开始在 ChatGPT 中植入广告以缓解资金压力
- GPT-5.2 Pro 独立完成了一个 45 年未解决的数论猜想证明
- 哈工大团队开源人形机器人项目，获小米、商汤投资
- Hacker News 热议：AI 编程工具对 COBOL 开发者的影响
- ArXiv 发布 HPV 疫苗接种 AI 代理系统设计论文

## 产品动态

### ChatGPT 引入广告系统

OpenAI 开始在 ChatGPT 中引入广告功能。这一决定的背后是公司持续增长的运营成本压力。广告将以非侵入式方式呈现，但这一举动引发了用户对产品体验变化的担忧。

**关键信息**: OpenAI, ChatGPT, 广告, 商业化

📎 原文链接: [量子位](https://www.qbitai.com/2026/01/370285.html)

### GPT-5.2 Pro 完成数论猜想证明

OpenAI 的 GPT-5.2 Pro 模型独立完成了一个 45 年未解决的数论猜想证明。数学家陶哲轩验证后表示该证明"没有犯任何错误"。这标志着 AI 在数学推理能力上的重大突破。

**关键信息**: GPT-5.2, 数学证明, 陶哲轩, 推理能力

📎 原文链接: [量子位](https://www.qbitai.com/2026/01/370328.html)

## 研究论文

### HPV 疫苗接种 AI 代理系统设计

研究人员开发了一个双重用途的 AI 代理系统，用于解决日本 HPV 疫苗接种犹豫问题。该系统包含：整合学术论文、政府资源的向量数据库；使用 ReAct 架构的检索增强生成聊天机器人；以及自动报告生成系统。

**关键信息**: AI 代理, HPV 疫苗, RAG, 公共卫生

📎 原文链接: [ArXiv](https://arxiv.org/abs/2601.10718)

### 大语言模型中的可信度认知-情感特征

研究分析了指令调优的 LLM 如何编码感知可信度。结果显示，信任信号与公平性、确定性和自我责任评估维度关联最强——这些是人类在线信任形成的核心维度。

**关键信息**: LLM, 可信度, 认知心理学, 网络信任

📎 原文链接: [ArXiv](https://arxiv.org/abs/2601.10719)

## 技术社区

### COBOL 开发者如何看待 AI 编程工具

Hacker News 热帖讨论了 AI 编程工具对 COBOL/大型机开发者的影响。有观点认为，真正运行经济的大量代码几乎未受 AI 编程代理的触及，这可能是安全也可能是机遇。

**关键信息**: COBOL, 大型机, AI 编程, 就业影响

📎 原文链接: [Hacker News](https://news.ycombinator.com/item?id=46678550)

### 维基百科 AI 清理项目

维基百科发起 WikiProject AI Cleanup 项目，旨在识别和清理 AI 生成的低质量内容。该项目反映了社区对 AI 生成内容质量控制的关注。

**关键信息**: 维基百科, 内容审核, AI 生成内容, 质量控制

📎 原文链接: [Hacker News](https://news.ycombinator.com/item?id=46677106)

## 融资并购

### 哈工大人形机器人项目获投资

哈工大系团队成立不到一年，推出全栈开源 3m/s 人形机器人原型机，获得小米、商汤等公司投资。项目开源了硬件图纸、算法和避坑指南。

**关键信息**: 人形机器人, 开源, 哈工大, 小米, 商汤

📎 原文链接: [量子位](https://www.qbitai.com/2026/01/370355.html)

## 关键词

#OpenAI #ChatGPT #GPT-5 #人形机器人 #ArXiv #HackerNews #COBOL #HPV #LLM可信度

---

数据来源: 量子位, ArXiv AI, Hacker News AI
生成时间: 2026-01-19 22:00
```

---

## Category Names

Use these Chinese category names:

| Category | Chinese Name | Icon |
|----------|--------------|------|
| Model Releases | 模型发布 | 🤖 |
| Product Updates | 产品动态 | 💼 |
| Research | 研究论文 | 📚 |
| Tools & Frameworks | 工具框架 | 🛠️ |
| Funding & M&A | 融资并购 | 💰 |
| Industry Events | 行业事件 | 🏆 |

---

## Output Guidelines

1. **Title format**: `# AI Daily · {年}年{月}月{日}日`
2. **Language**: 全部内容必须翻译成中文
3. **Summary**: 3-5 bullet points, one sentence each (中文)
4. **Categories**: Use Chinese category names (模型发布、产品动态、研究论文、工具框架、融资并购、行业事件、技术社区)
5. **Original Links**: 每条新闻必须附上原文链接，格式：`📎 原文链接: [来源名称](URL)`
6. **Keywords**: 5-10 hashtags, 中英文混合
7. **Footer**: 列出所有数据来源和生成时间

## Link Format Examples

```markdown
📎 原文链接: [smol.ai](https://news.smol.ai/issues/26-01-19/)
📎 原文链接: [Import AI](https://importai.substack.com/p/import-ai-440)
📎 原文链接: [量子位](https://www.qbitai.com/2026/01/370285.html)
📎 原文链接: [ArXiv](https://arxiv.org/abs/2601.10718)
📎 原文链接: [Hacker News](https://news.ycombinator.com/item?id=46678550)
📎 原文链接: [Last Week in AI](https://lastweekin.ai/p/last-week-in-ai-332)
📎 原文链接: [Ahead of AI](https://magazine.sebastianraschka.com/p/...)
```
