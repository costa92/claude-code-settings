import sys
import os

file_path = "/Users/costalong/.claude/skills/article-generator/scripts/generate_and_upload_images.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# 1. Add argument
new_lines = []
arg_added = False
for line in lines:
    new_lines.append(line)
    if not arg_added and 'parser.add_argument("--process-file"' in line:
        new_lines.append('    parser.add_argument("--wechat", action="store_true", help="生成微信公众号兼容的 HTML")\n')
        arg_added = True

# 2. Add logic at end of main
final_lines = []
logic_added = False
for i, line in enumerate(new_lines):
    if not logic_added and line.strip() == 'if __name__ == "__main__":':
        # Insert logic before this
        logic_code = [
            '\n',
            '    # WeChat 转换逻辑\n',
            '    if args.wechat:\n',
            '        target_file = None\n',
            '        if args.process_file:\n',
            '            target_file = args.process_file\n',
            '        elif args.output:\n',
            '            target_file = args.output\n',
            '\n',
            '        if target_file and os.path.exists(target_file):\n',
            '            print(f"\n🚀 正在转换为微信公众号格式: {target_file}")\n',
            '            convert_script = os.path.join(SCRIPT_DIR, "convert_to_wechat.py")\n',
            '            try:\n',
            '                subprocess.run(["python3", convert_script, target_file], check=True)\n',
            '            except subprocess.CalledProcessError as e:\n',
            '                print(f"❌ 微信格式转换失败: {e}")\n',
            '            except Exception as e:\n',
            '                print(f"❌ 微信格式转换发生错误: {e}")\n',
            '        else:\n',
            '            print("\n⚠️  --wechat 参数需要有效的 Markdown 文件 (通过 --process-file 或 --output 指定)")\n'
        ]
        final_lines.extend(logic_code)
        logic_added = True
    final_lines.append(line)

with open(file_path, 'w') as f:
    f.writelines(final_lines)
print("Updated generate_and_upload_images.py")
