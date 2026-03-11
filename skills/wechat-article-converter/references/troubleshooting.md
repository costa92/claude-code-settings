# 故障排查

### Python 引擎

**图片在微信编辑器中不显示**
- 确保图片使用外链 URL（CDN），以 `https://` 开头
- 避免使用相对路径 `./images/`

**样式在微信编辑器中丢失**
- 微信编辑器会过滤部分 CSS
- 使用内联样式代替 class
- 避免使用 `position: absolute`、`float` 等

**代码块格式错乱**
- 使用 `<pre><code>` 包裹，设置 `white-space: pre-wrap`

### Go 后端

**"command not found" 或下载失败**
- `md2wechat_backend.sh` 首次运行会自动下载二进制
- 确保有 `curl` 或 `wget`
- 网络问题可手动下载：https://github.com/geekjourneyx/md2wechat-skill/releases

**"IP not in whitelist" 错误（errcode=40164）**
- `upload_draft.py` 会自动检测此错误并**立即终止**（不会重试所有图片）
- 错误信息会直接显示当前 IP 和解决方法
- 手动检查公网 IP：`curl --noproxy '*' ifconfig.me`
- 在微信开发者平台添加 IP 白名单：mp.weixin.qq.com → 设置与开发 → 基本配置
- 注意：通过代理时，Go 后端的出口 IP 可能与 `curl ifconfig.me` 不同，以错误信息中显示的 IP 为准

**"AppID not configured" 错误**
- 设置环境变量 `WECHAT_APPID` 和 `WECHAT_SECRET`
- 或运行 `bash ${SKILL_DIR}/scripts/md2wechat_backend.sh config init`

**AI 图片生成失败**
- 检查 `IMAGE_API_KEY` 是否已设置
- 检查 `IMAGE_API_BASE` 是否正确
