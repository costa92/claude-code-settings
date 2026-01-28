"""
Custom Pygments Style for Coffee Theme
咖啡主题专属代码高亮样式

配色方案：
- 背景: #2c1810 (深咖啡色)
- 前景: #f5e6d3 (浅米色)
- 主色调: #d4875f (温暖橙棕)
"""

from pygments.style import Style
from pygments.token import (
    Comment, Error, Generic, Keyword, Literal, Name,
    Number, Operator, String, Text, Whitespace
)


class CoffeeStyle(Style):
    """
    Coffee Latte - 咖啡拿铁配色方案
    专为 wechat-article-converter 的 coffee 主题设计
    """

    # 背景色和默认文本色
    background_color = "#2c1810"
    default_style = "#f5e6d3"

    styles = {
        # 基础
        Text:                   "#f5e6d3",      # 普通文本 - 浅米色
        Whitespace:             "#f5e6d3",      # 空白
        Error:                  "#ff6b6b",      # 错误 - 红色警告

        # 注释
        Comment:                "italic #8b7f74",   # 注释 - 暖灰色 + 斜体
        Comment.Multiline:      "italic #8b7f74",
        Comment.Preproc:        "bold #a89178",     # 预处理注释 - 稍亮
        Comment.Single:         "italic #8b7f74",
        Comment.Special:        "bold italic #9d8b7a",

        # 关键字
        Keyword:                "bold #d4875f",     # 关键字 - 主色调橙棕
        Keyword.Constant:       "bold #d4875f",
        Keyword.Declaration:    "bold #d4875f",
        Keyword.Namespace:      "bold #d4875f",
        Keyword.Pseudo:         "bold #d4875f",
        Keyword.Reserved:       "bold #d4875f",
        Keyword.Type:           "bold #c9986b",     # 类型 - 浅棕色

        # 运算符
        Operator:               "#e8b98f",          # 运算符 - 浅橙
        Operator.Word:          "bold #d4875f",     # 运算符关键字

        # 名称
        Name:                   "#f5e6d3",          # 普通名称
        Name.Attribute:         "#e6a76f",          # 属性 - 金橙色
        Name.Builtin:           "#b89968",          # 内置函数 - 金棕色
        Name.Builtin.Pseudo:    "#b89968",
        Name.Class:             "bold #e6a76f",     # 类名 - 金橙色加粗
        Name.Constant:          "#c9986b",          # 常量 - 浅棕色
        Name.Decorator:         "#d4875f",          # 装饰器 - 主色调
        Name.Entity:            "#e6a76f",
        Name.Exception:         "bold #ff9b85",     # 异常 - 浅红橙色
        Name.Function:          "#e6a76f",          # 函数名 - 金橙色
        Name.Label:             "#d4875f",
        Name.Namespace:         "#c9986b",          # 命名空间
        Name.Other:             "#f5e6d3",
        Name.Tag:               "bold #d4875f",     # 标签
        Name.Variable:          "#f5e6d3",          # 变量
        Name.Variable.Class:    "#e6a76f",
        Name.Variable.Global:   "#e6a76f",
        Name.Variable.Instance: "#f5e6d3",

        # 字面量 - 数字
        Number:                 "#c9986b",          # 数字 - 浅棕色
        Number.Bin:             "#c9986b",
        Number.Float:           "#c9986b",
        Number.Hex:             "#c9986b",
        Number.Integer:         "#c9986b",
        Number.Integer.Long:    "#c9986b",
        Number.Oct:             "#c9986b",

        # 字面量 - 字符串
        String:                 "#e6a76f",          # 字符串 - 金橙色
        String.Backtick:        "#e6a76f",
        String.Char:            "#e6a76f",
        String.Doc:             "italic #c9986b",   # 文档字符串 - 浅棕斜体
        String.Double:          "#e6a76f",
        String.Escape:          "bold #ffb394",     # 转义字符 - 亮橙
        String.Heredoc:         "#e6a76f",
        String.Interpol:        "bold #d4875f",     # 插值 - 主色调
        String.Other:           "#e6a76f",
        String.Regex:           "#f5c99e",          # 正则 - 浅金色
        String.Single:          "#e6a76f",
        String.Symbol:          "#d4875f",          # 符号 - 主色调

        # Generic (用于 diff、追踪等)
        Generic:                "#f5e6d3",
        Generic.Deleted:        "#ff6b6b",          # 删除 - 红色
        Generic.Emph:           "italic #f5e6d3",   # 强调 - 斜体
        Generic.Error:          "#ff6b6b",
        Generic.Heading:        "bold #d4875f",     # 标题 - 主色调加粗
        Generic.Inserted:       "#a8d5a3",          # 插入 - 绿色
        Generic.Output:         "#8b7f74",          # 输出 - 暖灰
        Generic.Prompt:         "bold #f5e6d3",     # 提示符
        Generic.Strong:         "bold #f5e6d3",     # 加粗
        Generic.Subheading:     "bold #e6a76f",     # 子标题
        Generic.Traceback:      "#ff9b85",          # 追踪 - 浅红橙
    }
