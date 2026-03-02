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
import socket
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

def is_port_in_use(port):
    """检测端口是否被占用"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(("127.0.0.1", port))
            return False
        except socket.error:
            return True

class WeChatConverter:
    def __init__(self, theme_name="tech", preview_mode=True):
        self.links = []
        self.theme_name = theme_name
        self.theme_css = THEMES.get(theme_name, DEFAULT_CSS)
        self.preview_mode = preview_mode  # Enable WeChat-style preview wrapper
        self.frontmatter_title = None  # Will be extracted from YAML frontmatter

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

    def _normalize_code_blocks(self, md_content):
        """
        Normalize indentation of fenced code blocks to the nearest 4-space boundary.
        This ensures that code blocks nested in lists are preserved (not dedented to 0),
        while satisfying the parser's requirement for 4-space indentation levels.
        """
        import math
        lines = md_content.split('\n')
        new_lines = []
        in_block = False
        block_indent_len = 0
        fence_char = ""
        fence_length = 0
        indent_delta = 0

        for line in lines:
            if not in_block:
                # Detect start of code block
                # Match: start of line, optional whitespace group, fence (``` or ~~~), optional info
                match = re.match(r'^([ \t]*)(`{3,}|~{3,})(.*)$', line)
                if match:
                    current_indent = match.group(1)
                    fence_part = match.group(2)
                    info_part = match.group(3)

                    indent_len = len(current_indent)

                    # Calculate target indentation (nearest multiple of 4)
                    if indent_len % 4 == 0:
                        target_indent = indent_len
                    else:
                        target_indent = math.ceil(indent_len / 4) * 4

                    indent_delta = target_indent - indent_len

                    in_block = True
                    block_indent_len = indent_len
                    fence_char = fence_part[0]
                    fence_length = len(fence_part)

                    # Output opening fence with adjusted indentation
                    new_lines.append(" " * target_indent + fence_part + info_part)
                else:
                    new_lines.append(line)
            else:
                # Inside block
                # Check for closing fence
                m_close = re.match(r'^([ \t]*)([`~]+)[ \t]*$', line)
                is_closing = False

                if m_close:
                    captured_indent = m_close.group(1)
                    captured_fence = m_close.group(2)
                    if captured_fence.startswith(fence_char) and len(captured_fence) >= fence_length:
                        is_closing = True

                if is_closing:
                    in_block = False
                    # Output closing fence with adjusted indentation
                    # We use the same delta as the opening fence to keep it aligned
                    # Alternatively, calculate fresh based on its own indent, but alignment to opener is safer
                    # However, if user wrote mismatched indentation, we should probably respect the structure relative to start
                    # Simpler: just indent by block_indent_len + delta (which is target_indent)
                    # But the closing fence might be indented differently in source?
                    # Let's assume closing fence matches opening fence intent.

                    # If we use the original line's content and add delta:
                    if len(line.strip()) == 0:
                         new_lines.append("")
                    else:
                         new_lines.append(" " * indent_delta + line)
                else:
                    # Content line
                    # Add delta spaces
                    if len(line.strip()) == 0:
                        new_lines.append("")
                    else:
                        new_lines.append(" " * indent_delta + line)

        return '\n'.join(new_lines)

    def process_markdown(self, md_content):
        """
        Custom processing before standard markdown conversion
        1. Strip YAML frontmatter (but extract title first)
        2. Transform Obsidian callouts
        3. Extract links for footnotes (WeChat doesn"t support external links in body)
        """
        # 1. Extract title from YAML frontmatter before stripping
        self.frontmatter_title = None
        yaml_match = re.match(r'^\s*---\n(.*?)\n---\n', md_content, re.DOTALL | re.MULTILINE)
        if yaml_match:
            yaml_content = yaml_match.group(1)
            # Try to extract title from YAML
            title_match = re.search(r'^title:\s*["\']?(.*?)["\']?\s*$', yaml_content, re.MULTILINE)
            if title_match:
                self.frontmatter_title = title_match.group(1).strip()

        # Strip Frontmatter
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

        # 2.5 Process Reference Links (Best Effort)
        # Extract definitions: [id]: url
        ref_links = {}
        def extract_refs(match):
            ref_id = match.group(1).lower()
            url = match.group(2)
            ref_links[ref_id] = url
            return ""  # Remove definition from output

        # Regex: Start of line, [id]: url (handling optional title/junk at end of line)
        md_content = re.sub(r'^\s*\[([^\]]+)\]:\s*(\S+).*$', extract_refs, md_content, flags=re.MULTILINE)

        # Replace usages: [text][id] or [text][]
        def replace_refs(match):
            text = match.group(1)
            ref_id = match.group(2).lower()
            if not ref_id:  # Case [text][] -> id is text
                ref_id = text.lower()

            if ref_id in ref_links:
                return f"[{text}]({ref_links[ref_id]})"
            return match.group(0)

        md_content = re.sub(r'\[([^\]]+)\]\[([^\]]*)\]', replace_refs, md_content)

        # 3. Process Links
        # Reset links
        self.links = []

        # Match standard markdown links: [text](url) but NOT images ![text](url)
        # Improved Regex to handle balanced parentheses in URLs (e.g. Wikipedia links)
        # Pattern: (?<!!)\[([^\]]+)\]\(([^)]+(?:\([^)]+\)[^)]*)*)\)
        pattern = r'(?<!!)\[([^\]]+)\]\(([^)]+(?:\([^)]+\)[^)]*)*)\)'

        # Helper wrapper for re.sub
        def replacement(m):
            return self._replace_links_with_footnotes(m)

        processed_content = re.sub(pattern, replacement, md_content)

        # 4. Fix indented code blocks
        # Smartly dedent fenced code blocks to ensure they render correctly (especially in lists)
        processed_content = self._normalize_code_blocks(processed_content)

        return processed_content

    def generate_references_html(self):
        """Generate HTML for references section"""
        if not self.links:
            return ""

        html = "<div class=\"references-section\">"

        # Add decoration for Coffee theme (disabled - WeChat compatibility)
        title_prefix = ""
        # if self.theme_name == "coffee":
        #      title_prefix = '<span style="color: #d4875f; margin-right: 8px;">✦</span>'

        html += f"<div class=\"references-title\">{title_prefix}参考资料</div>"

        # Use ul/li for better semantic structure and compatibility
        html += "<ul style=\"list-style: none; padding-left: 0; margin: 0;\">"
        for i, url in enumerate(self.links, 1):
            html += f"<li class=\"reference-item\" style=\"margin-bottom: 5px;\">[{i}] {url}</li>"
        html += "</ul>"

        html += "</div>"
        return html

    def _get_current_time(self):
        """Get current time in WeChat format"""
        from datetime import datetime
        now = datetime.now()
        return now.strftime("%Y年%m月%d日 %H:%M")

    def _extract_title(self, html_content):
        """Extract title from HTML content (first h1 tag) or frontmatter"""
        import re

        # First, try to use title from frontmatter
        if hasattr(self, 'frontmatter_title') and self.frontmatter_title:
            return self.frontmatter_title

        # Try to extract title from first h1 tag
        h1_match = re.search(r'<h1[^>]*>(.*?)</h1>', html_content, re.DOTALL)
        if h1_match:
            # Remove HTML tags from title
            title = re.sub(r'<[^>]+>', '', h1_match.group(1))
            return title.strip()

        return "微信公众号文章"

    def _remove_first_h1(self, html_content):
        """Remove the first h1 tag from HTML content (to avoid duplication in preview mode)"""
        import re
        # Remove first h1 tag only
        return re.sub(r'<h1[^>]*>.*?</h1>', '', html_content, count=1, flags=re.DOTALL)

    def _fix_list_item_breaks(self, html_content):
        """Fix list item line breaks for WeChat editor compatibility

        Key strategy from md2wechat.cn:
        - Wrap colon+content in <section><span> to prevent breaks
        - Structure: <strong>Title:</strong><section><span>content</span></section>
        """
        import re

        # Step 1: Remove newlines inside <strong> tags (removed code tag processing to fix code blocks)
        html_content = re.sub(
            r'(<strong[^>]*>)(.*?)(</strong>)',
            lambda m: m.group(1) + re.sub(r'\s+', ' ', m.group(2)).strip() + m.group(3),
            html_content,
            flags=re.DOTALL
        )

        # Removed the code tag whitespace collapsing block that was destroying code block formatting

        # Step 2: Move separator INSIDE <strong> and wrap content in <section><span>
        # Pattern: <strong>Title</strong>: content -> <strong>Title:</strong><section><span>content</span></section>
        def transform_list_item(match):
            li_attrs = match.group(1)
            strong_open = match.group(2)  # <strong...>
            title = match.group(3)
            strong_close = match.group(4)  # </strong>
            separator = match.group(5)  # : or -
            content = match.group(6).strip()

            # Build: <li><strong>Title:</strong><section><span>content</span></section></li>
            return f'<li{li_attrs}>{strong_open}{title}{separator}{strong_close}<section><span>{content}</span></section></li>'

        # Transform: <li><strong>Title</strong>: content</li>
        html_content = re.sub(
            r'<li([^>]*)>(<strong[^>]*>)(.*?)(</strong>)\s*([:\-：－])\s*(.*?)</li>',
            transform_list_item,
            html_content,
            flags=re.DOTALL
        )

        # Step 3: Apply remaining nbsp fixes
        html_content = re.sub(r'(</code>)\s+和\s+', r'\1&nbsp;和&nbsp;', html_content)
        html_content = re.sub(r'(</code>)\s+and\s+', r'\1&nbsp;and&nbsp;', html_content)
        html_content = re.sub(r'(github\.com/[^\s<]+)\s+-\s+', r'\1&nbsp;-&nbsp;', html_content)
        html_content = re.sub(
            r'(Action|action|仓库|平台|工具|库),\s+(支持|包含|提供)',
            r'\1,&nbsp;\2',
            html_content
        )

        return html_content

    def _fix_table_alignment(self, html_content):
        """Fix table header alignment for WeChat editor compatibility

        Premailer may convert text-align:center to align="left" in <th> tags.
        This function ensures table headers are center-aligned.
        """
        import re

        # Fix <th> tags: change align="left" to align="center"
        html_content = re.sub(
            r'(<th[^>]*\s)align="left"',
            r'\1align="center"',
            html_content
        )

        # Also ensure text-align:center is in style attribute
        html_content = re.sub(
            r'(<th[^>]*style="[^"]*?)text-align:\s*left',
            r'\1text-align:center',
            html_content
        )

        return html_content

    @staticmethod
    def _replace_spaces_in_text_nodes(html_str):
        """Replace all space characters with &nbsp; in HTML text nodes only.

        Walks through the HTML string character by character:
        - Inside HTML tags (<...>): spaces are preserved as-is (for attributes)
        - Outside HTML tags (text nodes): spaces are replaced with &nbsp;

        This ensures WeChat's editor cannot collapse any spaces in code blocks,
        regardless of how Pygments tokenizes the code (whitespace-only spans,
        bare text spaces, trailing spaces in keyword spans, etc.)
        """
        result = []
        in_tag = False
        for ch in html_str:
            if ch == '<':
                in_tag = True
                result.append(ch)
            elif ch == '>':
                in_tag = False
                result.append(ch)
            elif ch == ' ' and not in_tag:
                result.append('&nbsp;')
            else:
                result.append(ch)
        return ''.join(result)

    def _preserve_code_indentation(self, html_content):
        """Preserve code block indentation and line breaks for WeChat compatibility

        WeChat editor has major issues with code blocks:
        1. Collapses spaces (both in text nodes and stripped <span> tags)
        2. Removes newlines, causing all code to appear on one line

        This function fixes all issues by:
        - Replacing ALL spaces in text nodes with &nbsp; entities
        - Converting newlines (\\n) to <br> tags for explicit line breaks
        """
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(html_content, 'html.parser')

        # Find all code blocks
        for pre_tag in soup.find_all('pre'):
            code_tag = pre_tag.find('code')
            if not code_tag:
                continue

            # Get the HTML content inside <code> tag
            code_html = str(code_tag)

            # Step 1: Replace whitespace-only spans with &nbsp; entities
            # Pygments wraps some spaces in <span style="color: #BBB"> </span>
            # Remove these spans entirely, replacing with &nbsp;
            code_html = re.sub(
                r'<span[^>]*>([ \t]+)</span>',
                lambda m: '&nbsp;' * len(m.group(1)),
                code_html
            )

            # Step 2: Replace ALL remaining spaces in text nodes with &nbsp;
            # This handles bare text spaces (e.g., "</span> OpenAI" after keywords)
            # and trailing spaces inside spans (e.g., "<span>import </span>")
            code_html = self._replace_spaces_in_text_nodes(code_html)

            # Step 3: Split into lines and join with <br> for explicit line breaks
            lines = code_html.split('\n')
            new_code_html = '<br>'.join(lines)

            # Replace the old code tag with the new one
            new_soup = BeautifulSoup(new_code_html, 'html.parser')
            code_tag.replace_with(new_soup)

        return str(soup)

    def post_process_html(self, html_body):
        """
        Process HTML content after markdown conversion but before inlining CSS
        Used for adding decorative elements that CSS pseudo-elements can't handle
        """
        # Coffee Theme Decorations
        if self.theme_name == "coffee":
            # Add H1 decoration: ◈ (disabled - WeChat compatibility)
            # decoration_h1 = '<div style="display: block; color: #d4875f; font-size: 14px; margin-top: 10px; text-align: center;">◈</div>'
            # html_body = re.sub(r'(</h1>)', f'{decoration_h1}\\1', html_body)

            # Add H2 decoration: ✦ prefix (disabled - WeChat compatibility)
            # decoration_h2 = '<span style="color: #d4875f; margin-right: 8px; font-size: 16px;">✦</span>'
            # html_body = re.sub(r'(<h2>)', f'\\1{decoration_h2}', html_body)

            # Add HR decoration: ◈ (WeChat-compatible: hr + negative margin overlay)
            decoration_hr = '<hr style="border: none; border-top: 1px solid #e8ddd0; margin: 35px 0 0 0;"><p style="text-align: center; margin-top: -10px; margin-bottom: 35px; font-size: 12px; line-height: 1;"><span style="background-color: #faf9f5; padding: 0 15px; color: #d4875f;">◈</span></p>'
            html_body = re.sub(r'<hr\s*/?>', decoration_hr, html_body)

        return html_body

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
        # NOTE: Removed "nl2br" to avoid extra line breaks in WeChat editor
        html_body = markdown.markdown(
            md_content,
            extensions=[
                "fenced_code",
                "tables",
                "nl2br",
                # "nl2br", # Disabled to prevent unexpected line breaks in lists
                "sane_lists",
                "codehilite",
                "extra"
            ],
            extension_configs={
                "codehilite": {
                    "css_class": "highlight",
                    "noclasses": True, # Inline styles
                    "pygments_style": self.pygments_style  # Use theme-specific style
                }
            }
        )

        # 3. Fix list item line breaks for WeChat compatibility
        html_body = self._fix_list_item_breaks(html_body)

        # 3. Post-process HTML (Theme specific decorations)
        html_body = self.post_process_html(html_body)

        # 4. Wrap in container and References
        references = self.generate_references_html()

        # Extract article title from html_body (first h1 tag)
        article_title = self._extract_title(html_body)

        # Generate HTML with or without preview wrapper
        if self.preview_mode:
            # Remove first h1 from content (will be displayed separately in title section)
            html_body_without_title = self._remove_first_h1(html_body)
            # Add viewport and styling for better WeChat-like preview
            full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <meta name="format-detection" content="telephone=no">
    <title>{article_title} - 微信公众号文章预览</title>
    <style>
        /* Body styling - simulate WeChat article page */
        body {{
            margin: 0;
            padding: 0;
            background-color: #f5f5f5;
            font-family: -apple-system-font, BlinkMacSystemFont, "Helvetica Neue", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei UI", "Microsoft YaHei", Arial, sans-serif;
        }}

        /* WeChat article wrapper */
        #wechat-article-wrapper {{
            max-width: 677px;
            margin: 0 auto;
            background-color: #ffffff;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
            min-height: 100vh;
        }}

        /* Top bar - simulate WeChat header */
        .wechat-header {{
            padding: 16px;
            border-bottom: 1px solid #ebebeb;
            background-color: #ffffff;
        }}

        .wechat-account {{
            font-size: 16px;
            color: #576b95;
            font-weight: 500;
            margin-bottom: 4px;
        }}

        .wechat-time {{
            font-size: 13px;
            color: #888888;
        }}

        /* Article title */
        .article-title {{
            padding: 20px 16px 16px 16px;
            border-bottom: 1px solid #ebebeb;
            background-color: #ffffff;
        }}

        .article-title h1 {{
            margin: 0;
            font-size: 24px;
            font-weight: bold;
            color: #000000;
            line-height: 1.4;
            word-break: break-word;
        }}

        /* Article content area */
        .wechat-content {{
            padding: 20px 16px;
        }}

        /* Bottom actions - simulate WeChat footer */
        .wechat-footer {{
            padding: 16px;
            border-top: 1px solid #ebebeb;
            text-align: center;
            color: #888888;
            font-size: 14px;
        }}

        /* Copy button */
        .copy-button {{
            display: inline-block;
            margin-top: 12px;
            padding: 8px 24px;
            background-color: #07c160;
            color: #ffffff;
            border: none;
            border-radius: 4px;
            font-size: 14px;
            cursor: pointer;
            transition: background-color 0.3s;
        }}

        .copy-button:hover {{
            background-color: #06ad56;
        }}

        .copy-button:active {{
            background-color: #059a4c;
        }}

        /* Print styles */
        @media print {{
            body {{
                background-color: #ffffff;
            }}
            #wechat-article-wrapper {{
                box-shadow: none;
            }}
            .wechat-header,
            .wechat-footer {{
                display: none;
            }}
        }}
    </style>
</head>
<body>
    <div id="wechat-article-wrapper">
        <!-- WeChat-style Header -->
        <div class="wechat-header">
            <div class="wechat-account">微信公众号文章预览</div>
            <div class="wechat-time">{self._get_current_time()}</div>
        </div>

        <!-- Article Title -->
        <div class="article-title">
            <h1>{article_title}</h1>
        </div>

        <!-- Article Content -->
        <div class="wechat-content">
            <div class="wechat-container" id="article-content">
                {html_body_without_title}
                {references}
            </div>
        </div>

        <!-- WeChat-style Footer -->
        <div class="wechat-footer">
            <div>预览模式 · 可直接复制内容到微信编辑器</div>
            <button class="copy-button" onclick="copyArticle()">📋 复制文章内容</button>
        </div>
    </div>

    <script>
    function copyArticle() {{
        const content = document.getElementById('article-content');
        const range = document.createRange();
        range.selectNode(content);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);

        try {{
            document.execCommand('copy');
            const btn = event.target;
            const originalText = btn.textContent;
            btn.textContent = '✅ 已复制';
            btn.style.backgroundColor = '#888888';
            setTimeout(() => {{
                btn.textContent = originalText;
                btn.style.backgroundColor = '#07c160';
            }}, 2000);
        }} catch (err) {{
            alert('复制失败，请手动选择内容复制');
        }}

        selection.removeAllRanges();
    }}
    </script>
</body>
</html>"""
        else:
            # Simple HTML without preview wrapper (for direct copy to WeChat)
            full_html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信公众号文章</title>
</head>
<body>
    <div class="wechat-container">
        {html_body}
        {references}
    </div>
</body>
</html>"""

        # 5. Inline CSS using Premailer
        # combine our custom CSS
        print("🎨 Inlining CSS styles...")
        # Use Premailer with CSS validation warnings suppressed
        # We use CSS3 properties that are valid but not in CSS 2.1 spec
        from premailer import Premailer
        import logging

        p = Premailer(
            html=full_html,
            css_text=self.theme_css,
            cssutils_logging_level=logging.CRITICAL,  # Suppress CSS warnings
            strip_important=False  # Keep !important declarations
        )
        final_html = p.transform()

        # 6. Preserve code block indentation and line breaks for WeChat compatibility
        # Must be done after premailer to ensure modifications persist
        final_html = self._preserve_code_indentation(final_html)

        # 7. Fix list item line breaks again (after premailer processing)
        # Premailer might normalize some HTML, so we apply the fix again
        final_html = self._fix_list_item_breaks(final_html)

        # 8. Fix table header alignment (premailer may override text-align)
        final_html = self._fix_table_alignment(final_html)

        # Output file - use custom path or default
        if output_path is None:
            # Get absolute path of input file
            abs_input_path = os.path.abspath(md_file_path)
            output_path = os.path.splitext(abs_input_path)[0] + "_wechat.html"
        else:
            # Ensure output path is absolute
            output_path = os.path.abspath(output_path)

        # Ensure output directory exists
        output_dir = os.path.dirname(output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)

        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(final_html)

            # Verify file was created
            if not os.path.exists(output_path):
                raise FileNotFoundError(f"Failed to create output file: {output_path}")

        except PermissionError:
            raise PermissionError(f"Permission denied when writing to: {output_path}")
        except Exception as e:
            raise Exception(f"Failed to write output file: {e}")

        return output_path

def interactive_theme_selection():
    """交互式主题选择（命令行版本）"""
    # 定义主题分组
    recommended_themes = {
        "1": ("coffee", "☕ Coffee (咖啡拿铁) - 专业优雅，温暖咖啡色系"),
        "2": ("tech", "💙 Tech (科技蓝) - 清爽专业，技术文章默认"),
        "3": ("warm", "🧡 Warm (温暖橙) - 温暖治愈，生活随笔适用"),
    }

    md2_themes = {
        "1": ("md2_purple", "💜 MD2 Purple (优雅紫) - Material Design 现代风"),
        "2": ("md2_classic", "💚 MD2 Classic (经典绿) - VuePress 清新风格"),
        "3": ("md2_dark", "🖤 MD2 Dark (终端黑) - 极客风格高对比度"),
    }

    simple_theme = ("simple", "⚫ Simple (极简黑白) - 聚焦内容，最轻量")

    # 第一步：显示推荐主题
    while True:
        print("\n" + "="*60)
        print("🎨 请选择微信公众号文章主题")
        print("="*60)
        print("\n📌 推荐主题（适合 95% 使用场景）：\n")

        for key, (name, desc) in recommended_themes.items():
            print(f"  {key}. {desc}")

        print(f"\n  4. 🔍 查看更多主题 (MD2 系列)...")
        print(f"  0. ⚫ Simple - 极简黑白主题")

        choice = input("\n👉 请输入选项 (0-4，直接回车使用 Tech): ").strip()

        # 直接回车使用默认主题
        if choice == "":
            print("\n✅ 已选择默认主题: Tech (科技蓝)")
            return "tech"

        # 选择推荐主题
        if choice in recommended_themes:
            theme_name, theme_desc = recommended_themes[choice]
            print(f"\n✅ 已选择: {theme_desc}")
            return theme_name

        # 选择 Simple 主题
        if choice == "0":
            print(f"\n✅ 已选择: {simple_theme[1]}")
            return simple_theme[0]

        # 查看更多主题
        if choice == "4":
            # 第二步：显示 MD2 主题
            while True:
                print("\n" + "="*60)
                print("🎨 更多主题 (MD2 系列)")
                print("="*60)
                print()

                for key, (name, desc) in md2_themes.items():
                    print(f"  {key}. {desc}")

                print(f"\n  0. ⬅️  返回推荐主题")

                md2_choice = input("\n👉 请输入选项 (0-3): ").strip()

                # 返回推荐主题
                if md2_choice == "0":
                    break  # 跳出内层循环，回到推荐主题

                # 选择 MD2 主题
                if md2_choice in md2_themes:
                    theme_name, theme_desc = md2_themes[md2_choice]
                    print(f"\n✅ 已选择: {theme_desc}")
                    return theme_name

                print("\n❌ 无效选项，请重新选择")

        else:
            print("\n❌ 无效选项，请重新选择")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert Markdown to WeChat Official Account HTML")
    parser.add_argument("file", help="Markdown file to convert")
    parser.add_argument("--theme", default=None, choices=list(THEMES.keys()), help="CSS Theme (tech, warm, simple, md2_classic, md2_dark, md2_purple, coffee)")
    parser.add_argument("--output", "-o", help="Output file path (default: INPUT_FILE_wechat.html)")
    parser.add_argument("--preview", action="store_true", help="转换完成后自动启动预览服务器")
    parser.add_argument("--port", type=int, default=8000, help="预览服务器端口 (默认: 8000)")
    parser.add_argument("--no-preview-mode", action="store_true", help="禁用微信预览模式，生成纯净 HTML（用于直接复制）")

    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"❌ File not found: {args.file}")
        sys.exit(1)

    # 如果没有指定主题，提供交互式选择
    if args.theme is None:
        args.theme = interactive_theme_selection()

    # 创建转换器，默认启用预览模式
    preview_mode = not args.no_preview_mode
    converter = WeChatConverter(theme_name=args.theme, preview_mode=preview_mode)
    try:
        output = converter.convert(args.file, output_path=args.output)

        # 获取文件大小
        file_size = os.path.getsize(output)
        file_size_kb = file_size / 1024

        print("\n" + "="*60)
        print(f"✅ 转换成功！")
        print("="*60)
        print(f"📄 输出文件: {output}")
        print(f"📊 文件大小: {file_size_kb:.1f} KB")
        print(f"🎨 使用主题: {args.theme}")
        print(f"🎭 预览模式: {'启用' if preview_mode else '禁用'}")

        # 验证文件确实存在并可读取
        print(f"\n🔍 验证输出文件...")
        if os.path.exists(output):
            # 再次检查文件大小，确保文件真实写入
            actual_size = os.path.getsize(output)
            if actual_size == file_size:
                print(f"✅ 文件已确认创建: {os.path.dirname(output)}")
                print(f"✅ 文件路径: {output}")

                # 测试文件可读性
                try:
                    with open(output, 'r', encoding='utf-8') as f:
                        f.read(100)  # 读取前 100 字符测试
                    print(f"✅ 文件可读性: 正常")
                except Exception as e:
                    print(f"⚠️  警告: 文件无法读取 - {e}")
            else:
                print(f"⚠️  警告: 文件大小不匹配（期望: {file_size}, 实际: {actual_size}）")
        else:
            print(f"❌ 错误: 文件未创建")
            print(f"   期望路径: {output}")
            print(f"   目录存在: {os.path.exists(os.path.dirname(output))}")
            print(f"   目录内容: {os.listdir(os.path.dirname(output))[:10]}")
            sys.exit(1)

        print("="*60 + "\n")

        # 如果启用了 --preview，智能启动预览服务器
        if args.preview:
            import subprocess
            from pathlib import Path

            # 获取输出文件所在目录
            output_dir = os.path.dirname(os.path.abspath(output))
            script_dir = os.path.dirname(__file__)
            preview_script = os.path.join(script_dir, "preview_server.py")

            # 检测端口是否已被占用
            if is_port_in_use(args.port):
                print("\n" + "="*60)
                print(f"✅ 预览服务器已在运行中 (端口 {args.port})")
                print("="*60)
                print(f"🌐 访问地址: http://localhost:{args.port}")
                print("💡 提示: 刷新浏览器即可查看新转换的文件")
                print("="*60 + "\n")
            else:
                # 端口未被占用，启动新服务器
                print("\n🚀 启动预览服务器...")
                print("="*60)

                try:
                    subprocess.run([
                        sys.executable,
                        preview_script,
                        "--port", str(args.port),
                        "--dir", output_dir
                    ], check=True)
                except KeyboardInterrupt:
                    print("\n✅ 预览服务器已停止")
                except Exception as e:
                    print(f"\n⚠️  预览服务器启动失败: {e}")
                    print(f"💡 提示: 你可以手动运行: python3 {preview_script} --dir {output_dir}")

    except Exception as e:
        print(f"❌ Conversion failed: {e}")
        # traceback
        import traceback
        traceback.print_exc()
        sys.exit(1)
