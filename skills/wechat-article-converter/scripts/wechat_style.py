# WeChat Official Account CSS Themes
# 微信公众号样式主题集合

# ==============================================================================
# 1. 极简科技 (Tech Blue) - 默认主题
# 适合：技术教程、架构分析、行业观察
# ==============================================================================
THEME_TECH = """
/* 全局容器 */
.wechat-container {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", "Helvetica Neue", Arial, sans-serif;
    font-size: 16px;
    line-height: 1.75;
    color: #333333;
    text-align: justify;
    padding: 10px;
    letter-spacing: 0.05em;
}

/* 标题样式 */
h1 {
    font-size: 22px;
    font-weight: bold;
    color: #000000;
    margin-top: 40px;
    margin-bottom: 20px;
    text-align: center;
}

h2 {
    font-size: 18px;
    font-weight: bold;
    color: #1f2329;
    margin-top: 35px;
    margin-bottom: 15px;
    padding-left: 10px;
    border-left: 4px solid #4a90e2; /* 科技蓝 */
    line-height: 1.4;
}

h3 {
    font-size: 17px;
    font-weight: bold;
    color: #1f2329;
    margin-top: 30px;
    margin-bottom: 10px;
    padding-bottom: 5px;
    border-bottom: 1px dashed #e5e6eb;
}

/* 段落样式 */
p {
    margin-bottom: 16px;
    line-height: 1.75;
    color: #3f3f3f;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* 列表样式 */
ul, ol {
    margin-bottom: 16px;
    padding-left: 20px;
    color: #3f3f3f;
}

li {
    margin-bottom: 4px;
    line-height: 1.75;
    white-space: normal;
    word-break: keep-all;
    overflow-wrap: break-word;
}

/* 引用样式 (Obsidian Callouts) */
blockquote {
    margin: 20px 0;
    padding: 15px;
    background-color: #f7f9fc;
    border-left: 4px solid #4a90e2;
    border-radius: 4px;
    color: #555555;
    font-size: 15px;
}

/* 强调文字 */
strong {
    color: #4a90e2;
    font-weight: bold;
}

/* 链接样式 */
a {
    color: #4a90e2;
    text-decoration: none;
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: break-all;
}

/* 代码块 - 模拟 Mac 窗口风格 */
pre {
    background-color: #f6f8fa;
    padding: 15px;
    border-radius: 6px;
    overflow-x: auto;
    white-space: pre; /* Ensure horizontal scrolling works */
    margin: 20px 0;
    font-family: "JetBrains Mono", Consolas, Monaco, "Andale Mono", monospace;
    font-size: 13px;
    line-height: 1.5;
    border: 1px solid #e1e4e8;
    position: relative;
    white-space: pre;
    word-wrap: normal;
    overflow-wrap: normal;
}

/* 内联代码 */
code {
    background-color: #fff5f5;
    color: #ff502c;
    padding: 2px 4px;
    border-radius: 4px;
    font-family: "JetBrains Mono", Consolas, Monaco, monospace;
    font-size: 14px;
    margin: 0 2px;
    white-space: nowrap;
    word-break: keep-all;
}

/* 代码块内的 code 标签 - 覆盖内联代码样式 */
pre code {
    background-color: transparent !important;
    color: inherit !important;
    padding: 0 !important;
    border-radius: 0 !important;
    border: none !important;
    margin: 0 !important;
    font-size: inherit !important;
}

/* 图片 */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 20px auto;
    border-radius: 6px;
    box-shadow: 0 4px 10px rgba(0,0,0,0.05);
}

/* 图片描述 */
img + em, img + span {
    display: block;
    text-align: center;
    color: #888;
    font-size: 13px;
    margin-top: -10px;
    margin-bottom: 20px;
}

/* 表格 */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    font-size: 14px;
}

th {
    background-color: #f6f8fa;
    font-weight: bold;
    color: #333;
    padding: 10px;
    border: 1px solid #dfe2e5;
}

td {
    padding: 10px;
    border: 1px solid #dfe2e5;
    color: #555;
}

/* 分割线 */
hr {
    border: none;
    border-top: 1px solid #eee;
    margin: 40px 0;
}

/* 底部参考文献 */
.references-section {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #eee;
}

.references-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 15px;
    color: #333;
}

.reference-item {
    font-size: 13px;
    color: #888;
    margin-bottom: 5px;
    word-break: break-all;
}
"""

# ==============================================================================
# 2. 温暖治愈 (Warm Orange)
# 适合：生活随笔、情感共鸣、经验分享
# ==============================================================================
THEME_WARM = """
/* 全局容器 */
.wechat-container {
    font-family: "Optima", -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #4a4a4a;
    text-align: justify;
    padding: 10px;
    letter-spacing: 0.05em;
    background-color: #fffbf0; /* 暖色背景 */
}

h1 {
    font-size: 24px;
    font-weight: bold;
    color: #d9730d;
    margin-top: 40px;
    margin-bottom: 20px;
    text-align: center;
}

h2 {
    font-size: 20px;
    font-weight: bold;
    color: #d9730d;
    margin-top: 40px;
    margin-bottom: 20px;
    text-align: center;
    border-bottom: 2px solid #f2e3d5;
    padding-bottom: 10px;
    display: inline-block;
    min-width: 30%;
}

/* 让H2居中需要父级样式配合，但在内联CSS中较难，这里用边框装饰 */
h3 {
    font-size: 17px;
    font-weight: bold;
    color: #d9730d;
    margin-top: 30px;
    margin-bottom: 10px;
    padding-left: 10px;
    border-left: 3px solid #d9730d;
}

p {
    margin-bottom: 20px;
    color: #595959;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

strong {
    color: #d9730d;
    font-weight: bold;
    background: linear-gradient(180deg, transparent 70%, #ffe8cc 70%);
}

/* 链接样式 */
a {
    color: #d9730d;
    text-decoration: none;
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: break-all;
}

blockquote {
    margin: 20px 0;
    padding: 20px;
    background-color: #fff;
    border: 1px dashed #d9730d;
    border-radius: 8px;
    color: #8c6b4f;
}

code {
    background-color: #fff3e0;
    color: #d9730d;
    padding: 2px 5px;
    border-radius: 3px;
    font-size: 14px;
    white-space: nowrap;
    word-break: keep-all;
}

/* 代码块 */
pre {
    background-color: #2c1810;
    color: #f5e6d3;
    padding: 15px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 20px 0;
    font-family: Monaco, Menlo, Consolas, monospace;
    font-size: 13px;
    line-height: 1.6;
    white-space: pre;
    word-wrap: normal;
    overflow-wrap: normal;
}

/* 代码块内的 code 标签 - 覆盖内联代码样式 */
pre code {
    background-color: transparent !important;
    color: inherit !important;
    padding: 0 !important;
    border-radius: 0 !important;
    border: none !important;
    margin: 0 !important;
    font-size: inherit !important;
}

img {
    border-radius: 8px;
    box-shadow: 0 8px 16px rgba(217, 115, 13, 0.1);
    margin: 25px auto;
}

/* 其他基础样式复用 */
ul, ol { margin-bottom: 16px; padding-left: 20px; }
li {
    margin-bottom: 4px;
    line-height: 1.75;
    white-space: normal;
    word-break: keep-all;
    overflow-wrap: break-word;
}
table { width: 100%; border-collapse: collapse; margin: 20px 0; font-size: 14px; }
th { background-color: #fff3e0; color: #d9730d; padding: 10px; border: 1px solid #f2e3d5; }
td { padding: 10px; border: 1px solid #f2e3d5; color: #595959; }
hr { border: none; border-top: 1px dashed #d9730d; margin: 40px 0; opacity: 0.3; }
.references-section { margin-top: 40px; padding-top: 20px; border-top: 1px solid #f2e3d5; }
.references-title { font-size: 16px; font-weight: bold; margin-bottom: 15px; color: #d9730d; }
.reference-item { font-size: 13px; color: #a69080; margin-bottom: 5px; }
"""

# ==============================================================================
# 3. 极简黑白 (Simple Black)
# 适合：严肃评论、新闻简报、极简主义者
# ==============================================================================
THEME_SIMPLE = """
/* 全局容器 */
.wechat-container {
    font-family: "Georgia", "Times New Roman", "Songti SC", "SimSun", serif;
    font-size: 17px;
    line-height: 1.8;
    color: #222;
    text-align: justify;
    padding: 15px;
}

h1 {
    font-size: 24px;
    font-weight: 800;
    color: #000;
    margin-top: 40px;
    margin-bottom: 30px;
    line-height: 1.3;
}

h2 {
    font-size: 20px;
    font-weight: 700;
    color: #000;
    margin-top: 40px;
    margin-bottom: 20px;
    border-bottom: 3px solid #000;
    padding-bottom: 8px;
}

h3 {
    font-size: 18px;
    font-weight: 700;
    color: #000;
    margin-top: 30px;
    margin-bottom: 15px;
    background-color: #f0f0f0;
    padding: 5px 10px;
    display: inline-block;
}

p {
    margin-bottom: 20px;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

strong {
    color: #000;
    font-weight: 900;
    text-decoration: underline;
    text-decoration-thickness: 2px;
}

/* 链接样式 */
a {
    color: #000;
    text-decoration: underline;
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: break-all;
}

blockquote {
    margin: 30px 0;
    padding: 20px 30px;
    background-color: transparent;
    border-left: 4px solid #000;
    color: #666;
    font-style: italic;
}

code {
    background-color: #f0f0f0;
    color: #000;
    padding: 2px 4px;
    font-family: monospace;
    font-size: 15px;
    border: 1px solid #ddd;
    white-space: nowrap;
    word-break: keep-all;
}

/* 代码块 */
pre {
    background-color: #f8f8f8;
    color: #000;
    padding: 15px;
    border: 2px solid #000;
    margin: 25px 0;
    font-family: "Courier New", Courier, monospace;
    font-size: 13px;
    line-height: 1.5;
    white-space: pre;
    word-wrap: normal;
    overflow-wrap: normal;
    overflow-x: auto;
}

/* 代码块内的 code 标签 - 覆盖内联代码样式 */
pre code {
    background-color: transparent !important;
    color: inherit !important;
    padding: 0 !important;
    border-radius: 0 !important;
    border: none !important;
    margin: 0 !important;
    font-size: inherit !important;
}

img {
    border: 1px solid #000;
    margin: 30px auto;
    padding: 5px;
}

/* 列表 */
ul { list-style-type: square; }

/* 引用区 */
.references-section { margin-top: 50px; padding-top: 30px; border-top: 4px solid #000; }
.references-title { font-weight: 900; font-size: 18px; margin-bottom: 20px; text-transform: uppercase; }
.reference-item { font-family: monospace; font-size: 12px; margin-bottom: 8px; color: #444; }
"""

# ==============================================================================
# 4. MD2 Classic (Green)
# 适合：经典风格、清新阅读、文档说明
# ==============================================================================
THEME_MD2_CLASSIC = """
/* 全局容器 */
.wechat-container {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #3f3f3f;
    text-align: justify;
    padding: 10px;
}

/* 标题 */
h1 {
    font-size: 22px;
    font-weight: bold;
    color: #42b983;
    margin: 40px 0 20px 0;
    text-align: center;
}

h2 {
    font-size: 18px;
    font-weight: bold;
    color: #42b983;
    margin: 35px 0 15px 0;
    border-bottom: 1px solid #eaecef;
    padding-bottom: 10px;
}

h3 {
    font-size: 16px;
    font-weight: bold;
    color: #42b983;
    margin: 30px 0 10px 0;
}

/* 段落与列表 */
p {
    margin-bottom: 16px;
    line-height: 1.8;
    color: #3f3f3f;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

ul, ol {
    margin-bottom: 16px;
    padding-left: 20px;
}

li {
    margin-bottom: 4px;
    line-height: 1.75;
    white-space: normal;
    word-break: keep-all;
    overflow-wrap: break-word;
}

/* 引用 */
blockquote {
    border-left: 4px solid #42b983;
    background-color: #f8fcf9;
    padding: 15px;
    margin: 20px 0;
    color: #555;
    border-radius: 4px;
}

/* 代码 */
pre {
    background-color: #f6f8fa;
    padding: 15px;
    border-radius: 6px;
    overflow-x: auto;
    margin: 20px 0;
    font-family: "JetBrains Mono", Consolas, monospace;
    font-size: 13px;
    border: 1px solid #e1e4e8;
    white-space: pre;
    word-wrap: normal;
    overflow-wrap: normal;
}

code {
    background-color: #f6f8fa;
    color: #476582;
    padding: 2px 4px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 14px;
    margin: 0 2px;
    white-space: nowrap;
    word-break: keep-all;
}

/* 代码块内的 code 标签 - 覆盖内联代码样式 */
pre code {
    background-color: transparent !important;
    color: inherit !important;
    padding: 0 !important;
    border-radius: 0 !important;
    border: none !important;
    margin: 0 !important;
    font-size: inherit !important;
}

/* 强调 */
strong {
    color: #42b983;
    font-weight: bold;
}

/* 链接样式 */
a {
    color: #42b983;
    text-decoration: none;
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: break-all;
}

/* 图片 */
img {
    max-width: 100%;
    border-radius: 6px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    margin: 20px auto;
    display: block;
}

/* 底部引用 */
.references-section {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #eaecef;
}
.references-title {
    font-weight: bold;
    color: #42b983;
    margin-bottom: 10px;
}
.reference-item {
    font-size: 12px;
    color: #999;
}
"""

# ==============================================================================
# 5. MD2 Dark (Terminal)
# 适合：极客、终端风格、高对比度
# ==============================================================================
THEME_MD2_DARK = """
/* 全局容器 */
.wechat-container {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #333;
    text-align: justify;
    padding: 10px;
}

/* 标题 */
h1 {
    font-size: 24px;
    font-weight: 800;
    color: #2c3e50;
    margin: 40px 0 20px 0;
    text-align: center;
}

h2 {
    font-size: 20px;
    font-weight: bold;
    color: #2c3e50;
    margin: 35px 0 15px 0;
    padding-left: 10px;
    border-left: 5px solid #2c3e50;
}

h3 {
    font-size: 17px;
    font-weight: bold;
    color: #2c3e50;
    margin: 30px 0 10px 0;
}

/* 段落 */
p {
    margin-bottom: 16px;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* 引用 */
blockquote {
    background-color: #f3f5f7;
    border-left: 5px solid #2c3e50;
    padding: 15px;
    margin: 20px 0;
    color: #666;
    border-radius: 0 4px 4px 0;
}

/* 代码 - Terminal Style */
pre {
    background-color: #282c34;
    color: #abb2bf;
    padding: 20px;
    border-radius: 6px;
    overflow-x: auto;
    white-space: pre; /* Ensure horizontal scrolling works */
    margin: 20px 0;
    font-family: Consolas, Monaco, monospace;
    font-size: 13px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    position: relative;
    white-space: pre;
    word-wrap: normal;
    overflow-wrap: normal;
}

code {
    background-color: #f3f4f4;
    color: #c7254e;
    padding: 2px 4px;
    border-radius: 3px;
    font-family: monospace;
    font-size: 14px;
    white-space: nowrap;
    word-break: keep-all;
}

/* 代码块内的 code 标签 - 覆盖内联代码样式 */
pre code {
    background-color: transparent !important;
    color: inherit !important;
    padding: 0 !important;
    border-radius: 0 !important;
    border: none !important;
    margin: 0 !important;
    font-size: inherit !important;
}

/* 强调 */
strong {
    color: #2c3e50;
    font-weight: 900;
}

/* 链接样式 */
a {
    color: #2c3e50;
    text-decoration: none;
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: break-all;
}

/* 图片 */
img {
    max-width: 100%;
    border-radius: 6px;
    border: 1px solid #eee;
    margin: 20px auto;
    display: block;
}

/* 引用区 */
.references-section {
    margin-top: 40px;
    border-top: 2px solid #2c3e50;
    padding-top: 20px;
}
.references-title {
    font-weight: bold;
    color: #2c3e50;
}
.reference-item {
    font-size: 12px;
    color: #777;
}
"""

# ==============================================================================
# 6. MD2 Purple (Elegant)
# 适合：优雅、现代、设计感
# ==============================================================================
THEME_MD2_PURPLE = """
/* 全局容器 */
.wechat-container {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #444;
    text-align: justify;
    padding: 10px;
}

/* 标题 */
h1 {
    font-size: 22px;
    font-weight: bold;
    color: #7b16ff;
    margin: 40px 0 20px 0;
    text-align: center;
    text-shadow: 0 2px 4px rgba(123, 22, 255, 0.1);
}

h2 {
    font-size: 18px;
    font-weight: bold;
    color: #7b16ff;
    margin: 35px 0 15px 0;
    background: linear-gradient(to right, rgba(123, 22, 255, 0.1), transparent);
    padding: 5px 10px;
    border-radius: 4px;
}

h3 {
    font-size: 16px;
    font-weight: bold;
    color: #7b16ff;
    margin: 30px 0 10px 0;
    padding-left: 8px;
    border-left: 3px solid #7b16ff;
}

/* 段落 */
p {
    margin-bottom: 16px;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* 引用 */
blockquote {
    background-color: #f8f4ff;
    border: 1px solid #e0d4fc;
    border-left: 4px solid #7b16ff;
    padding: 15px;
    margin: 20px 0;
    color: #666;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(123, 22, 255, 0.05);
}

/* 代码 */
pre {
    background-color: #2a2a2a;
    color: #f8f8f2;
    padding: 15px;
    border-radius: 6px;
    overflow-x: auto;
    white-space: pre; /* Ensure horizontal scrolling works */
    margin: 20px 0;
    font-family: Consolas, monospace;
    font-size: 13px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    white-space: pre;
    word-wrap: normal;
    overflow-wrap: normal;
}

code {
    background-color: #f0e6ff;
    color: #7b16ff;
    padding: 2px 4px;
    border-radius: 4px;
    font-family: monospace;
    font-size: 14px;
    white-space: nowrap;
    word-break: keep-all;
}

/* 代码块内的 code 标签 - 覆盖内联代码样式 */
pre code {
    background-color: transparent !important;
    color: inherit !important;
    padding: 0 !important;
    border-radius: 0 !important;
    border: none !important;
    margin: 0 !important;
    font-size: inherit !important;
}

/* 强调 */
strong {
    color: #7b16ff;
    font-weight: bold;
}

/* 链接样式 */
a {
    color: #7b16ff;
    text-decoration: none;
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: break-all;
}

/* 图片 */
img {
    max-width: 100%;
    border-radius: 8px;
    box-shadow: 0 8px 20px rgba(123, 22, 255, 0.15);
    margin: 25px auto;
    display: block;
}

/* 引用区 */
.references-section {
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px dashed #7b16ff;
}
.references-title {
    font-weight: bold;
    color: #7b16ff;
}
.reference-item {
    font-size: 12px;
    color: #888;
}
"""

# ==============================================================================
# 7. Coffee Latte (Editorial)
# 适合：专业评论、深度分析、编辑精选
# ==============================================================================
THEME_COFFEE = """
/* 全局容器 */
.wechat-container {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    font-size: 16px;
    line-height: 1.8;
    color: #4a413d;
    text-align: left;
    padding: 10px;
    background-color: #faf9f5;
}

/* 标题样式 */
h1 {
    font-size: 24px;
    font-weight: bold;
    color: #2c1810;
    margin: 40px 0 20px 0;
    text-align: center;
    position: relative;
    padding-bottom: 15px;
    line-height: 1.3;
}

/* Pseudo-elements removed as they don't work with inline styles
   Logic moved to python script
*/

h2 {
    font-size: 20px;
    font-weight: bold;
    color: #2c1810;
    margin: 35px 0 15px 0;
    padding: 12px 20px;
    background-color: #fff5eb;
    border-left: 4px solid #d4875f;
    border-radius: 4px;
    position: relative;
    text-align: left;
}

/* Pseudo-elements removed as they don't work with inline styles
   Logic moved to python script
*/

h3 {
    font-size: 17px;
    font-weight: bold;
    color: #d4875f;
    margin: 30px 0 10px 0;
    padding-left: 10px;
    border-left: 3px solid #d4875f;
    text-align: left;
}

/* 段落样式 */
p {
    margin-bottom: 18px;
    line-height: 1.8;
    color: #4a413d;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* 列表样式 */
ul, ol {
    margin-bottom: 16px;
    padding-left: 15px;
    color: #4a413d;
}

li {
    margin-bottom: 4px;
    line-height: 1.75;
    word-break: keep-all;
    word-wrap: break-word;
    white-space: normal;
    overflow-wrap: break-word;
}

/* 引用样式 */
blockquote {
    margin: 25px 0;
    padding: 18px 20px;
    background-color: #e8f4f8;
    border-left: 4px solid #5b9fb5;
    border-radius: 6px;
    color: #4a413d;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
}

/* 强调文字 */
strong {
    color: #d4875f;
    font-weight: bold;
    background-color: rgba(212, 135, 95, 0.1);
}

/* 链接样式 */
a {
    color: #d4875f;
    text-decoration: none;
    word-wrap: break-word;
    overflow-wrap: break-word;
    word-break: break-all;
}

/* 代码块 */
pre {
    background-color: #2c1810;
    color: #f5e6d3;
    padding: 15px;
    border-radius: 8px;
    margin: 20px 0;
    font-family: Monaco, Menlo, Consolas, monospace;
    font-size: 13px;
    line-height: 1.6;
    box-shadow: 0 4px 12px rgba(44, 24, 16, 0.3);
<<<<<<< HEAD
    white-space: pre;
    word-wrap: normal;
    overflow-wrap: normal;
||||||| 5c93349
    white-space: pre;
=======
    white-space: pre; /* Ensure horizontal scrolling works */
    overflow-x: auto;
>>>>>>> 1f5691301a511fa7d29796457c349af229d2f904
    display: block;
}

/* 内联代码 */
code {
    background-color: #fff5eb;
    color: #d4875f;
    padding: 1px 2px;
    border-radius: 2px;
    font-family: Monaco, Menlo, Consolas, monospace;
    font-size: 14px;
    margin: 0;
    border: 1px solid #ffe8d6;
    display: inline;
    white-space: nowrap;
    word-break: keep-all;
}

/* 代码块内的 code 标签 - 覆盖内联代码样式 */
pre code {
    background-color: transparent !important;
    color: inherit !important;
    padding: 0 !important;
    border-radius: 0 !important;
    border: none !important;
    margin: 0 !important;
    font-size: inherit !important;
}

/* 图片 */
img {
    max-width: 100%;
    height: auto;
    display: block;
    margin: 25px auto;
    border-radius: 8px;
    box-shadow: 0 6px 16px rgba(0, 0, 0, 0.08);
    border: 1px solid #f0e6d8;
}

/* 图片描述 */
img + em, img + span {
    display: block;
    text-align: center;
    color: #8b7f74;
    font-size: 13px;
    margin-top: -15px;
    margin-bottom: 20px;
    font-style: italic;
}

/* 表格 - 微信编辑器优化版 */
table {
    width: 100%;
    border-collapse: collapse;
    margin: 25px 0;
    font-size: 14px;
    border: 2px solid #d4875f;
    background-color: #fff;
    table-layout: auto;
}

th {
    background-color: #fff5eb;
    font-weight: bold;
    color: #2c1810;
    padding: 12px 10px;
    border: 1px solid #d4875f;
    text-align: center;
    vertical-align: middle;
    line-height: 1.5;
    white-space: normal;
    word-break: keep-all;
    min-width: 80px;
}

td {
    padding: 10px;
    border: 1px solid #e8d5c4;
    color: #4a413d;
    background-color: #fff;
    text-align: left;
    vertical-align: top;
    line-height: 1.6;
    white-space: normal;
    word-break: normal;
    word-wrap: break-word;
    overflow-wrap: break-word;
}

/* 特殊处理：只对包含代码的第一列允许断词 */
td:first-child {
    font-weight: 600;
    color: #2c1810;
    word-break: break-word;
}

tr:nth-child(even) td {
    background-color: #faf9f5;
}

/* Pseudo-elements removed as they don't work with inline styles
   Logic moved to python script
*/

/* 分割线 */
hr {
    border: none;
    border-top: 2px solid #f0e6d8;
    margin: 40px 0;
    position: relative;
}

/* Pseudo-elements removed as they don't work with inline styles
   Logic moved to python script
*/

/* 底部参考文献 */
.references-section {
    margin-top: 50px;
    padding-top: 25px;
    border-top: 2px solid #f0e6d8;
    background-color: #fff5eb;
    padding: 25px 15px 15px 15px;
    border-radius: 8px;
}

.references-title {
    font-size: 16px;
    font-weight: bold;
    margin-bottom: 15px;
    color: #2c1810;
    position: relative;
    padding-left: 15px;
    text-align: left;
}

/* Pseudo-elements removed as they don't work with inline styles
   Logic moved to python script
*/

.reference-item {
    font-size: 13px;
    color: #8b7f74;
    margin-bottom: 8px;
    word-break: break-all;
    padding-left: 15px;
}
"""

# Theme Registry
THEMES = {
    "tech": THEME_TECH,
    "warm": THEME_WARM,
    "simple": THEME_SIMPLE,
    "md2_classic": THEME_MD2_CLASSIC,
    "md2_dark": THEME_MD2_DARK,
    "md2_purple": THEME_MD2_PURPLE,
    "coffee": THEME_COFFEE
}

# Pygments style mapping for each theme
# Available styles: default, monokai, vim, fruity, native, paraiso-dark, paraiso-light, etc.
# Run `python -c "from pygments.styles import get_all_styles; print(list(get_all_styles()))"` to see all
#
# Custom styles:
# - coffee: Custom coffee theme style defined in coffee_highlight_style.py
THEME_PYGMENTS_STYLES = {
    "tech": "default",          # 蓝色主题 - 默认清爽样式
    "warm": "autumn",           # 橙色主题 - 温暖的秋天样式
    "simple": "bw",             # 黑白主题 - 纯黑白样式
    "md2_classic": "friendly",  # 绿色主题 - 友好清新样式
    "md2_dark": "monokai",      # 暗黑主题 - Monokai 经典暗色
    "md2_purple": "material",   # 紫色主题 - Material 现代紫色系
    "coffee": "coffee_style"    # 咖啡主题 - 专属咖啡色代码高亮
}

# 默认样式 (向后兼容)
WECHAT_CSS = THEME_TECH
