#!/usr/bin/env bash
# register-plugin-hooks.sh
# 扫描所有已启用插件的 hooks.json，自动创建 wrapper 脚本并注册到 settings.json
# 同时将新插件记录到 CLAUDE.md，并在首次安装时输出成功提示
# 作为 SessionStart hook 运行，每次启动时自检自愈，无需手动干预

set -euo pipefail

CLAUDE_DIR="${CLAUDE_CONFIG_DIR:-$HOME/.claude}"
HOOKS_DIR="$CLAUDE_DIR/hooks"
SETTINGS="$CLAUDE_DIR/settings.json"
INSTALLED="$CLAUDE_DIR/plugins/installed_plugins.json"
CLAUDE_MD="$CLAUDE_DIR/CLAUDE.md"

[[ ! -f "$INSTALLED" ]] && exit 0
[[ ! -f "$SETTINGS" ]]  && exit 0

mkdir -p "$HOOKS_DIR"

python3 - "$CLAUDE_DIR" "$HOOKS_DIR" "$SETTINGS" "$INSTALLED" "$CLAUDE_MD" <<'PYEOF'
import json, os, re, sys
from pathlib import Path

claude_dir, hooks_dir, settings_path, installed_path, claude_md_path = sys.argv[1:]
home = str(Path.home())

def expand(p):
    return p.replace("~", home)

def contract(p):
    return p.replace(home, "~")

def get_plugin_description(install_path, plugin_key):
    """从 .claude-plugin/plugin.json 或 hooks.json 读取插件描述"""
    manifest = os.path.join(install_path, ".claude-plugin", "plugin.json")
    if os.path.isfile(manifest):
        with open(manifest) as f:
            d = json.load(f)
        return d.get("description", "")
    hooks_json = os.path.join(install_path, "hooks", "hooks.json")
    if os.path.isfile(hooks_json):
        with open(hooks_json) as f:
            d = json.load(f)
        return d.get("description", "")
    return ""

def update_claude_md(claude_md_path, plugin_name, marketplace, description):
    """将新插件追加到 CLAUDE.md 的已启用插件表格中，幂等"""
    if not os.path.isfile(claude_md_path):
        return False
    with open(claude_md_path) as f:
        content = f.read()
    # 已记录则跳过
    if f"| {plugin_name} |" in content:
        return False
    new_row = f"| {plugin_name} | {marketplace} | {description} |"
    # 找到表格末尾（最后一个 | xxx | 行之后插入）
    table_pattern = r'(\| 插件 \| 来源 \| 说明 \|.*?\n(?:\|.+\|\n)+)'
    match = re.search(table_pattern, content, re.DOTALL)
    if match:
        old_table = match.group(0)
        new_table = old_table.rstrip('\n') + '\n' + new_row + '\n'
        content = content.replace(old_table, new_table)
        with open(claude_md_path, "w") as f:
            f.write(content)
        return True
    return False

with open(installed_path) as f:
    installed = json.load(f)

with open(settings_path) as f:
    settings = json.load(f)

enabled = settings.get("enabledPlugins", {})
settings_changed = False
newly_installed = []

for plugin_key, entries in installed.get("plugins", {}).items():
    if not enabled.get(plugin_key):
        continue

    install_path = expand(entries[0]["installPath"])
    plugin_name  = plugin_key.split("@")[0]
    marketplace  = plugin_key.split("@")[1] if "@" in plugin_key else ""

    # Path fallback: cache path → direct plugin dir → skip
    if not os.path.isdir(install_path):
        alt_path = os.path.join(claude_dir, "plugins", plugin_name)
        if os.path.isdir(alt_path):
            install_path = alt_path
        else:
            continue

    # ── 文档更新 ──────────────────────────────────────────────────────────
    desc = get_plugin_description(install_path, plugin_key)
    if update_claude_md(claude_md_path, plugin_name, marketplace, desc):
        newly_installed.append((plugin_name, marketplace, desc))

    # ── Hook 注册 ──────────────────────────────────────────────────────────
    hooks_json_path = os.path.join(install_path, "hooks", "hooks.json")
    if not os.path.isfile(hooks_json_path):
        continue

    with open(hooks_json_path) as f:
        hooks_cfg = json.load(f)

    for event, groups in hooks_cfg.get("hooks", {}).items():
        for group in groups:
            for hook in group.get("hooks", []):
                cmd = hook.get("command", "")
                m = re.search(r'\$\{?CLAUDE_PLUGIN_ROOT\}?/hooks/(\S+)', cmd)
                if not m:
                    continue
                script_name = m.group(1).strip("'\"")

                event_kebab  = re.sub(r'(?<!^)(?=[A-Z])', '-', event).lower()
                wrapper_name = f"{plugin_name}-{event_kebab}.sh"
                wrapper_path = os.path.join(hooks_dir, wrapper_name)
                wrapper_ref  = f"~/.claude/hooks/{wrapper_name}"

                existing_wrappers = os.listdir(hooks_dir)
                already_exists = any(
                    w.startswith(f"{plugin_name}-") and
                    event_kebab.replace("-","") in w.replace("-","")
                    for w in existing_wrappers
                )
                existing_cmds = [
                    h.get("command", "")
                    for g in settings.get("hooks", {}).get(event, [])
                    for h in g.get("hooks", [])
                ]
                already_registered = any(plugin_name in c for c in existing_cmds)

                if not already_exists:
                    # Detect plugin layout: cache (version dirs) vs direct
                    is_cache = "/cache/" in install_path
                    if is_cache:
                        # Cache-installed: discover latest version directory
                        version_parent = os.path.dirname(install_path)
                        version_parent_rel = contract(version_parent).replace("~", "$HOME")
                        content = f"""#!/usr/bin/env bash
# Auto-generated by register-plugin-hooks.sh
# Plugin: {plugin_key}  Event: {event}
CLAUDE_DIR="${{CLAUDE_CONFIG_DIR:-$HOME/.claude}}"
PLUGIN_DIR="{version_parent_rel}"
LATEST=$(ls -d "$PLUGIN_DIR"/*/ 2>/dev/null | sort -V | tail -1)
[[ -z "$LATEST" ]] && exit 0
export CLAUDE_PLUGIN_ROOT="${{LATEST%/}}"
exec bash "$CLAUDE_PLUGIN_ROOT/hooks/{script_name}" "$@"
"""
                    else:
                        # Direct-installed: use plugin path as-is
                        direct_rel = contract(install_path).replace("~", "$HOME")
                        content = f"""#!/usr/bin/env bash
# Auto-generated by register-plugin-hooks.sh
# Plugin: {plugin_key}  Event: {event}
CLAUDE_DIR="${{CLAUDE_CONFIG_DIR:-$HOME/.claude}}"
PLUGIN_DIR="{direct_rel}"
[[ ! -d "$PLUGIN_DIR" ]] && exit 0
export CLAUDE_PLUGIN_ROOT="$PLUGIN_DIR"
exec bash "$CLAUDE_PLUGIN_ROOT/hooks/{script_name}" "$@"
"""
                    with open(wrapper_path, "w") as wf:
                        wf.write(content)
                    os.chmod(wrapper_path, 0o755)

                if not already_registered:
                    entry = {"hooks": [{"type": "command", "command": wrapper_ref}]}
                    if hook.get("async") is not None:
                        entry["hooks"][0]["async"] = hook["async"]
                    settings.setdefault("hooks", {}).setdefault(event, []).append(entry)
                    settings_changed = True

if settings_changed:
    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)

# ── 安装成功提示 ───────────────────────────────────────────────────────────
if newly_installed:
    sep = "─" * 48
    print(f"\n┌{sep}┐")
    print(f"│{'  插件安装成功':^46}│")
    print(f"├{sep}┤")
    for name, mkt, desc in newly_installed:
        short_desc = desc[:38] + "…" if len(desc) > 38 else desc
        print(f"│  ✓ {name:<18} ({mkt})")
        if short_desc:
            print(f"│    {short_desc}")
    print(f"├{sep}┤")
    print(f"│  · CLAUDE.md 已更新{'':27}│")
    if settings_changed:
        print(f"│  · hooks 已注册，下次 session 生效{'':13}│")
    print(f"└{sep}┘")
PYEOF
