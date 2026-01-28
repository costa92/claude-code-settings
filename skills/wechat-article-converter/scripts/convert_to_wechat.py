#!/usr/bin/env python3
"""
Convert Markdown to WeChat Official Account compatible HTML
- Inlines CSS
- Handles Code highlighting (Mac style)
- Converts links to footnotes
"""

import sys
import os
import re
import argparse
import markdown
from premailer import transform
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.formatters import HtmlFormatter

# Register custom Coffee style
try:
    from coffee_highlight_style import CoffeeStyle
    from pygments.styles import STYLE_MAP
    STYLE_MAP['coffee_style'] = 'coffee_highlight_style::CoffeeStyle'
except ImportError:
    pass  # Custom style not available, will fallback

# Import CSS style
try:
    from wechat_style import THEMES, THEME_PYGMENTS_STYLES, WECHAT_CSS as DEFAULT_CSS
except ImportError:
    # Fallback simple style
    THEMES = {}
    THEME_PYGMENTS_STYLES = {}
    DEFAULT_CSS = "h2 { border-left: 3px solid blue; padding-left: 10px; } img { max-width: 100%; }"

class WeChatConverter:
    def __init__(self, theme_name="tech"):
        self.links = []
        self.theme_name = theme_name
        self.theme_css = THEMES.get(theme_name, DEFAULT_CSS)

        # Get Pygments style - handle custom coffee style
        style_name = THEME_PYGMENTS_STYLES.get(theme_name, "default")
        if style_name == "coffee_style" and theme_name == "coffee":
            try:
                from coffee_highlight_style import CoffeeStyle
                self.pygments_style = CoffeeStyle
                print(f"🎨 Using theme: {theme_name}")
                print(f"🎨 Code highlighting style: Custom Coffee Style (专属咖啡色)")
            except ImportError:
                self.pygments_style = "monokai"  # Fallback
                print(f"🎨 Using theme: {theme_name}")
                print(f"⚠️  Coffee style not available, using fallback: monokai")
        else:
            self.pygments_style = style_name
            print(f"🎨 Using theme: {theme_name}")
            print(f"🎨 Code highlighting style: {self.pygments_style}")

    def _replace_links_with_footnotes(self, match):
        """Regex callback to replace [text](url) with text[n]"""
        text = match.group(1)
        url = match.group(2)

        # Skip image links which are ![text](url) - handled by negative lookbehind in regex
        # Skip anchor links #
        if url.startswith("#"):
            return f"{text}"

        self.links.append(url)
        index = len(self.links)
        return f"{text}<sup style=\"color: #4a90e2;\">[{index}]</sup>"

    def process_markdown(self, md_content):
        """
        Custom processing before standard markdown conversion
        1. Strip YAML frontmatter
        2. Transform Obsidian callouts
        3. Extract links for footnotes (WeChat doesn"t support external links in body)
        """
        # 1. Strip Frontmatter
        # Remove content between first two --- lines if they exist at start
        # Improved regex to handle potential leading whitespace and ensure robust matching
        md_content = re.sub(r"^\s*---\n.*?\n---\n", "", md_content, count=1, flags=re.DOTALL | re.MULTILINE)

        # 2. Transform Obsidian Callouts
        # > [!INFO] Title -> > ℹ️ **Title**
        def callout_replace(match):
            c_type = match.group(1).lower()
            # Group 2 is the title content, strip whitespace
            title = match.group(2).strip()
            
            emoji_map = {
                "abstract": "📝",
                "summary": "📝",
                "tldr": "📝",
                "info": "ℹ️",
                "note": "📝",
                "tip": "💡",
                "hint": "💡",
                "important": "💡",
                "warning": "⚠️",
                "caution": "⚠️",
                "attention": "⚠️",
                "error": "❌",
                "fail": "❌",
                "failure": "❌",
                "missing": "❌",
                "danger": "🚫",
                "bug": "🐛",
                "question": "❓",
                "help": "❓",
                "faq": "❓",
                "success": "✅",
                "check": "✅",
                "done": "✅",
                "todo": "☐",
                "example": "📍",
                "quote": "💬",
                "cite": "💬"
            }
            # Fallback for unknown types
            emoji = emoji_map.get(c_type, "📌")
            return f"> {emoji} **{title}**"

        # Improved regex to handle:
        # - Whitespace after >
        # - Whitespace before title
        # - Standard \w+ for type
        md_content = re.sub(r"^>\s*\[!(\w+)\]\s*(.*)$", callout_replace, md_content, flags=re.MULTILINE)

        # 3. Process Links
        # Reset links
        self.links = []

        # Match standard markdown links: [text](url) but NOT images ![text](url)
        # Regex: (?<!!)\[(.*?)\]\((.*?)\)
        pattern = r"(?<!!)\[(.*?)\]\((.*?)\)"

        # Helper wrapper for re.sub
        def replacement(m):
            return self._replace_links_with_footnotes(m)

        processed_content = re.sub(pattern, replacement, md_content)
        return processed_content

    def generate_references_html(self):
        """Generate HTML for references section"""
        if not self.links:
            return ""

        html = "<div class=\"references-section\">"
        html += "<div class=\"references-title\">参考资料</div>"

        for i, url in enumerate(self.links, 1):
            html += f"<div class=\"reference-item\">[{i}] {url}</div>"

        html += "</div>"
        return html

    def convert(self, md_file_path, output_path=None):
        """Main conversion function"""
        if not os.path.exists(md_file_path):
            raise FileNotFoundError(f"File not found: {md_file_path}")

        with open(md_file_path, "r", encoding="utf-8") as f:
            md_content = f.read()

        # 1. Pre-process links and other custom syntax
        md_content = self.process_markdown(md_content)

        # 2. Convert to HTML with extensions
        # We need "fenced_code" for ``` blocks and "codehilite" for syntax highlighting
        html_body = markdown.markdown(
            md_content,
            extensions=[
                "fenced_code",
                "tables",
                "nl2br",
                "sane_lists",
                "codehilite"
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "noclasses": True, # Inline styles
                    "pygments_style": self.pygments_style  # Use theme-specific style
                }
            }
        )

        # 4. Wrap in container and References
        references = self.generate_references_html()

        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>WeChat Article</title>
        </head>
        <body>
            <div class="wechat-container">
                {html_body}
                {references}
            </div>
        </body>
        </html>
        """

        # 5. Inline CSS using Premailer
        # combine our custom CSS
        print("🎨 Inlining CSS styles...")
        final_html = transform(full_html, css_text=self.theme_css)

        # Output file - use custom path or default
        if output_path is None:
            output_path = os.path.splitext(md_file_path)[0] + "_wechat.html"

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(final_html)

        return output_path

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Markdown to WeChat Official Account HTML")
    parser.add_argument("file", help="Markdown file to convert")
    parser.add_argument("--theme", default=None, choices=list(THEMES.keys()), help="CSS Theme (tech, warm, simple, md2_classic, md2_dark, md2_purple, coffee)")
    parser.add_argument("--output", "-o", help="Output file path (default: INPUT_FILE_wechat.html)")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)

    # 如果没有指定主题，使用 AskUserQuestion 让用户选择
    if args.theme is None:
        # 检查是否在支持 AskUserQuestion 的环境中
        # 如果不支持，回退到命令行输入
        try:
            # 尝试导入 Claude Code 的交互工具
            # 注意：这里假设 AskUserQuestion 是通过环境变量或特殊方式提供的
            # 实际使用中，Claude Code 会处理这个工具调用

            # 如果在 Claude Code 环境中，应该显示选择界面
            # 这里先设置默认值，让 Claude Code 介入
            print("\n🎨 请选择主题...")
            print("提示：如果您正在使用 Claude Code，将显示主题选择界面")
            print("      如果没有显示，请使用 --theme 参数指定主题\n")

            # 默认使用 tech 主题
            args.theme = "tech"
            print(f"使用默认主题: tech (科技蓝)\n")

        except Exception:
            # 如果无法使用交互式选择，使用默认主题
            args.theme = "tech"
            print(f"使用默认主题: tech (科技蓝)\n")

    converter = WeChatConverter(theme_name=args.theme)
    try:
        output = converter.convert(args.file, output_path=args.output)
        print(f"✅ Successfully converted to: {output}")
    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        # traceback
        import traceback
        traceback.print_exc()
        sys.exit(1)
