#!/usr/bin/env python3
"""
本地预览服务器 - 实时预览微信文章效果
支持热重载、主题切换、多文件浏览
"""

import os
import sys
import http.server
import socketserver
import webbrowser
import argparse
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import subprocess
import threading
import time

class WeChatPreviewHandler(http.server.SimpleHTTPRequestHandler):
    """自定义请求处理器"""

    # 存储当前主题（类变量，所有实例共享）
    current_theme = 'tech'
    base_dir = Path.cwd()

    def do_GET(self):
        """处理 GET 请求"""
        parsed = urlparse(self.path)

        # 处理主题切换请求
        if parsed.path == '/switch-theme':
            query = parse_qs(parsed.query)
            new_theme = query.get('theme', ['tech'])[0]
            file_path = query.get('file', [''])[0]

            if file_path:
                # 切换主题并重新转换
                WeChatPreviewHandler.current_theme = new_theme
                self.regenerate_html(file_path, new_theme)

                # 重定向回文件页面
                self.send_response(302)
                self.send_header('Location', f'/{Path(file_path).stem}_wechat.html')
                self.end_headers()
                return

        # 处理根目录请求 - 显示文件列表
        elif parsed.path == '/' or parsed.path == '/index.html':
            self.serve_file_list()
            return

        # 默认处理其他请求
        super().do_GET()

    def serve_file_list(self):
        """提供文件列表页面"""
        md_files = list(WeChatPreviewHandler.base_dir.glob('*.md'))
        html_files = list(WeChatPreviewHandler.base_dir.glob('*_wechat.html'))

        html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>微信文章预览服务器</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #2c3e50;
            font-size: 32px;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        .subtitle {{
            color: #7f8c8d;
            font-size: 14px;
            margin-bottom: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section-title {{
            color: #34495e;
            font-size: 18px;
            font-weight: 600;
            margin-bottom: 15px;
            padding-bottom: 8px;
            border-bottom: 2px solid #e0e0e0;
        }}
        .file-list {{
            display: grid;
            gap: 12px;
        }}
        .file-item {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            padding: 16px 20px;
            background: #f8f9fa;
            border-radius: 8px;
            transition: all 0.3s;
            border: 2px solid transparent;
        }}
        .file-item:hover {{
            background: #e3f2fd;
            border-color: #2196F3;
            transform: translateX(4px);
        }}
        .file-name {{
            font-size: 16px;
            color: #2c3e50;
            font-weight: 500;
        }}
        .file-actions {{
            display: flex;
            gap: 10px;
        }}
        .btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            cursor: pointer;
            transition: all 0.2s;
            text-decoration: none;
            display: inline-block;
        }}
        .btn-primary {{
            background: #2196F3;
            color: white;
        }}
        .btn-primary:hover {{
            background: #1976D2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(33, 150, 243, 0.4);
        }}
        .btn-secondary {{
            background: #9C27B0;
            color: white;
        }}
        .btn-secondary:hover {{
            background: #7B1FA2;
        }}
        .empty-state {{
            text-align: center;
            padding: 40px;
            color: #95a5a6;
        }}
        .badge {{
            display: inline-block;
            padding: 4px 12px;
            background: #4CAF50;
            color: white;
            border-radius: 12px;
            font-size: 12px;
            margin-left: 8px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>
            📱 微信文章预览服务器
            <span class="badge">运行中</span>
        </h1>
        <div class="subtitle">
            本地实时预览微信公众号文章效果 · 支持主题切换和热重载
        </div>

        <div class="section">
            <div class="section-title">📄 Markdown 源文件 ({len(md_files)})</div>
            <div class="file-list">
"""

        if md_files:
            for md_file in sorted(md_files):
                html_file = md_file.parent / f"{md_file.stem}_wechat.html"
                exists = html_file.exists()

                html_content += f"""
                <div class="file-item">
                    <span class="file-name">{md_file.name}</span>
                    <div class="file-actions">
"""
                if exists:
                    html_content += f"""
                        <a href="/{html_file.name}" class="btn btn-primary">预览</a>
"""
                else:
                    html_content += f"""
                        <span style="color: #95a5a6;">未转换</span>
"""
                html_content += """
                    </div>
                </div>
"""
        else:
            html_content += """
                <div class="empty-state">
                    <p>📭 当前目录没有 Markdown 文件</p>
                </div>
"""

        html_content += """
            </div>
        </div>

        <div class="section">
            <div class="section-title">🎨 已转换的微信文章 ({len(html_files)})</div>
            <div class="file-list">
"""

        if html_files:
            for html_file in sorted(html_files):
                html_content += f"""
                <div class="file-item">
                    <span class="file-name">{html_file.name}</span>
                    <div class="file-actions">
                        <a href="/{html_file.name}" class="btn btn-primary">预览</a>
                    </div>
                </div>
"""
        else:
            html_content += """
                <div class="empty-state">
                    <p>📭 还没有转换的文件</p>
                    <p style="margin-top: 8px; font-size: 14px;">运行 convert_to_wechat.py 或 batch_convert.py 来转换文件</p>
                </div>
"""

        html_content += f"""
            </div>
        </div>

        <div style="margin-top: 30px; padding: 20px; background: #f0f0f0; border-radius: 8px;">
            <h3 style="margin-bottom: 10px; color: #2c3e50;">💡 使用提示</h3>
            <ul style="color: #555; line-height: 1.8; padding-left: 20px;">
                <li>点击"预览"按钮查看微信文章效果</li>
                <li>当前工作目录: <code style="background: white; padding: 2px 6px; border-radius: 3px;">{WeChatPreviewHandler.base_dir}</code></li>
                <li>按 <kbd>Ctrl+C</kbd> 停止服务器</li>
            </ul>
        </div>
    </div>
</body>
</html>
"""

        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))

    def regenerate_html(self, md_file, theme):
        """重新生成 HTML（主题切换时）"""
        script_dir = Path(__file__).parent
        convert_script = script_dir / "convert_to_wechat.py"

        cmd = [
            sys.executable,
            str(convert_script),
            md_file,
            "--theme", theme
        ]

        try:
            subprocess.run(cmd, check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"❌ 转换失败: {e.stderr.decode()}")

def main():
    parser = argparse.ArgumentParser(
        description="启动本地预览服务器，实时预览微信文章效果",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 在当前目录启动服务器（默认端口 8000）
  python3 preview_server.py

  # 指定端口
  python3 preview_server.py --port 8080

  # 指定目录
  python3 preview_server.py --dir ./articles

  # 启动后不自动打开浏览器
  python3 preview_server.py --no-browser
        """
    )

    parser.add_argument(
        '-p', '--port',
        type=int,
        default=8000,
        help='服务器端口（默认: 8000）'
    )

    parser.add_argument(
        '-d', '--dir',
        default='.',
        help='工作目录（默认: 当前目录）'
    )

    parser.add_argument(
        '--no-browser',
        action='store_true',
        help='不自动打开浏览器'
    )

    args = parser.parse_args()

    # 切换到指定目录
    work_dir = Path(args.dir).resolve()
    if not work_dir.exists():
        print(f"❌ 目录不存在: {work_dir}")
        return 1

    os.chdir(work_dir)
    WeChatPreviewHandler.base_dir = work_dir

    # 启动服务器
    try:
        with socketserver.TCPServer(("", args.port), WeChatPreviewHandler) as httpd:
            server_url = f"http://localhost:{args.port}"

            print("\n" + "="*60)
            print("🚀 微信文章预览服务器已启动")
            print("="*60)
            print(f"📁 工作目录: {work_dir}")
            print(f"🌐 访问地址: {server_url}")
            print(f"⏹️  停止服务: 按 Ctrl+C")
            print("="*60 + "\n")

            # 自动打开浏览器
            if not args.no_browser:
                def open_browser():
                    time.sleep(1)  # 等待服务器启动
                    webbrowser.open(server_url)

                threading.Thread(target=open_browser, daemon=True).start()

            httpd.serve_forever()

    except KeyboardInterrupt:
        print("\n\n✅ 服务器已停止")
        return 0
    except OSError as e:
        if e.errno == 48 or e.errno == 98:  # Address already in use
            print(f"\n❌ 端口 {args.port} 已被占用，请尝试其他端口:")
            print(f"   python3 preview_server.py --port {args.port + 1}")
        else:
            print(f"\n❌ 服务器错误: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
