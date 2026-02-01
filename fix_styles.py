import re
import os

file_path = "skills/wechat-article-converter/scripts/wechat_style.py"

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

def update_pre_style(match):
    style_body = match.group(1)

    # Remove existing properties we want to override
    style_body = re.sub(r'white-space:\s*[^;]+;', '', style_body)
    style_body = re.sub(r'word-wrap:\s*[^;]+;', '', style_body)
    style_body = re.sub(r'overflow-wrap:\s*[^;]+;', '', style_body)
    style_body = re.sub(r'overflow-x:\s*[^;]+;', '', style_body) # Remove overflow-x: auto if we wrap
    style_body = re.sub(r'display:\s*[^;]+;', '', style_body)

    # Add new properties
    new_props = """
    display: block;
    white-space: pre-wrap;
    word-wrap: break-word;
    overflow-wrap: break-word;"""

    return f"pre {{{style_body}{new_props}\n}}"

def update_pre_code_style(match):
    style_body = match.group(1)

    # Check if white-space is already there
    if "white-space" not in style_body:
        style_body += "\n    white-space: inherit !important;"
        style_body += "\n    display: inline;"

    return f"pre code {{{style_body}}}"

# Update pre styles
# Use non-greedy match for content inside {}
content = re.sub(r'pre \{([^\}]+)\}', update_pre_style, content)

# Update pre code styles
content = re.sub(r'pre code \{([^\}]+)\}', update_pre_code_style, content)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Successfully updated styles.")
