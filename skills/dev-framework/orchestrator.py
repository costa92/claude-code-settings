#!/usr/bin/env python3
"""Dev Framework Orchestrator — 确定性状态管理

SKILL.md（决策层）调用此脚本管理所有状态变更。
LLM 不可绕过此脚本自行决定流程走向。
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

try:
    import yaml
except ImportError:
    # 降级：如果没有 pyyaml，用简单的 YAML 处理
    yaml = None

AGENT_ABBREV = {
    "triage": "TRIAGE",
    "pm": "PM",
    "ui-designer": "UI",
    "architect": "ARCH",
    "developer": "DEV",
    "reviewer": "REVIEW",
    "tester": "TESTER",
    "system": "SYSTEM",
}

PHASE_MAP = {
    "triage": "triage",
    "pm": "requirements",
    "ui-designer": "ui-design",
    "architect": "design",
    "developer": "coding",
    "reviewer": "review",
    "tester": "testing",
    "done": "done",
}

REQUIRED_ARTIFACTS = {
    "reviewer": {"file": "review-report.md", "agent_name": "Reviewer"},
    "tester": {"file": "test-report.md", "agent_name": "Tester"},
}


# === YAML 兼容层 ===

def _yaml_load(path):
    with open(path, encoding="utf-8") as f:
        if yaml:
            return yaml.safe_load(f) or {}
        else:
            return _simple_yaml_load(f.read())


def _yaml_dump(data, path):
    with open(path, "w", encoding="utf-8") as f:
        if yaml:
            yaml.dump(data, f, allow_unicode=True, default_flow_style=False)
        else:
            _simple_yaml_dump(data, f)


def _simple_yaml_load(text):
    """极简 YAML 解析（仅支持平铺 key: value 和 list）"""
    result = {}
    current_key = None
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if stripped.startswith("- ") and current_key:
            if not isinstance(result[current_key], list):
                result[current_key] = []
            val = stripped[2:].strip()
            # 尝试解析为 dict（简单的 key: value）
            if ": " in val:
                d = {}
                # 单行 dict 项
                for part in [val]:
                    k, v = part.split(": ", 1)
                    d[k.strip()] = _parse_value(v.strip())
                result[current_key].append(d)
            else:
                result[current_key].append(_parse_value(val))
        elif ": " in stripped:
            k, v = stripped.split(": ", 1)
            k = k.strip()
            v = v.strip()
            if v == "[]":
                result[k] = []
                current_key = k
            elif v == "":
                result[k] = []
                current_key = k
            else:
                result[k] = _parse_value(v)
                current_key = k
        elif stripped.endswith(":"):
            k = stripped[:-1].strip()
            result[k] = []
            current_key = k
    return result


def _parse_value(v):
    if v.startswith('"') and v.endswith('"'):
        return v[1:-1]
    if v.startswith("'") and v.endswith("'"):
        return v[1:-1]
    # 内联列表: [a, b, c]
    if v.startswith("[") and v.endswith("]"):
        inner = v[1:-1].strip()
        if not inner:
            return []
        return [_parse_value(item.strip()) for item in inner.split(",") if item.strip()]
    if v.lower() == "true":
        return True
    if v.lower() == "false":
        return False
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        pass
    return v


def _simple_yaml_dump(data, f):
    """极简 YAML 序列化"""
    for k, v in data.items():
        if isinstance(v, list):
            if not v:
                f.write(f"{k}: []\n")
            else:
                f.write(f"{k}:\n")
                for item in v:
                    if isinstance(item, dict):
                        parts = [f"{ik}: {_format_value(iv)}" for ik, iv in item.items()]
                        f.write(f"  - {{{', '.join(parts)}}}\n")
                    else:
                        f.write(f"  - {_format_value(item)}\n")
        else:
            f.write(f"{k}: {_format_value(v)}\n")


def _format_value(v):
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, str):
        if not v:
            return '""'
        if any(c in v for c in ":#{}[],&*?|->!%@`"):
            return f'"{v}"'
        return v
    return str(v)


# === 工具函数 ===

def _now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _plan_dir(project_dir):
    return os.path.join(project_dir, ".plan")


def _read_project(plan_dir):
    path = os.path.join(plan_dir, "project.yaml")
    if not os.path.exists(path):
        return {}
    return _yaml_load(path)


def _write_project(plan_dir, data):
    path = os.path.join(plan_dir, "project.yaml")
    _yaml_dump(data, path)


def _write_trace(plan_dir, agent, event, detail, message, duration=None):
    path = os.path.join(plan_dir, "trace.log")
    abbrev = AGENT_ABBREV.get(agent, agent.upper())
    dur_str = f" ({duration}s)" if duration is not None else ""
    line = f"[{_now()}] {abbrev:<8s} | {event:<10s} | {detail:<14s} | {message}{dur_str}\n"
    with open(path, "a", encoding="utf-8") as f:
        f.write(line)


def _read_last_trace(plan_dir):
    path = os.path.join(plan_dir, "trace.log")
    if not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]
    if not lines:
        return {}
    last = lines[-1]
    parts = last.split("|")
    if len(parts) >= 2:
        return {"event": parts[1].strip(), "raw": last}
    return {"raw": last}


def _agent_to_phase(agent):
    return PHASE_MAP.get(agent, agent)


def _increment_rollback(project_dir, task=None):
    pd = _plan_dir(project_dir)
    project = _read_project(pd)
    if task:
        counts = project.get("rollback_counts", {})
        if not isinstance(counts, dict):
            counts = {}
        counts[task] = counts.get(task, 0) + 1
        project["rollback_counts"] = counts
    else:
        project["rollback_count"] = project.get("rollback_count", 0) + 1
    _write_project(pd, project)


def _get_rollback_count(project_dir, task=None):
    pd = _plan_dir(project_dir)
    project = _read_project(pd)
    if task:
        counts = project.get("rollback_counts", {})
        if not isinstance(counts, dict):
            return 0
        return counts.get(task, 0)
    return project.get("rollback_count", 0)


def _output(data):
    print(json.dumps(data, ensure_ascii=False))


def _normalize_task_id(raw):
    """Task-1 / Task 1 / Task1 / task 1 → 'Task 1'"""
    m = re.match(r'[Tt]ask[- ]?(\d+)', raw.strip())
    return f"Task {m.group(1)}" if m else raw.strip()


# === 子命令 ===

def cmd_init(args):
    """初始化 .plan/ 目录 — 智能识别项目语言和框架"""
    pd = _plan_dir(args.project_dir)
    os.makedirs(os.path.join(pd, "handoff"), exist_ok=True)
    os.makedirs(os.path.join(pd, "artifacts"), exist_ok=True)

    # 智能识别项目语言和框架
    language = args.language or _detect_language(args.project_dir)
    framework = args.framework or _detect_framework(args.project_dir, language)
    has_frontend = _detect_has_frontend(args.project_dir)
    # 补充: 已知前端框架名也触发 has_frontend
    if not has_frontend and framework:
        _FRONTEND_FRAMEWORKS = {"nextjs", "next", "nuxt", "nuxtjs", "react", "vue", "svelte", "angular", "solid", "remix", "gatsby", "vite"}
        if framework.lower().replace(".", "").replace("-", "") in _FRONTEND_FRAMEWORKS:
            has_frontend = True
    has_database = _detect_has_database(args.project_dir)
    has_external_api = _detect_has_external_api(args.project_dir)
    has_api_server = _detect_has_api_server(args.project_dir, language, framework)

    project = {
        "name": os.path.basename(os.path.abspath(args.project_dir)),
        "language": language,
        "framework": framework,
        "has_frontend": has_frontend,
        "has_database": has_database,
        "has_external_api": has_external_api,
        "has_api_server": has_api_server,
        "mode": "full",
        "current_phase": "triage",
        "current_agent": "triage",
        "current_task": "",
        "rollback_count": 0,
        "history": [],
        "is_git_repo": os.path.isdir(os.path.join(args.project_dir, ".git")),
    }

    _write_project(pd, project)
    _write_trace(pd, "system", "start", "",
                 f"dev-framework 初始化，语言: {language}，框架: {framework}，前端: {has_frontend}，数据库: {has_database}，外部API: {has_external_api}，API服务: {has_api_server}")

    # 追加 .gitignore
    gitignore = os.path.join(args.project_dir, ".gitignore")
    entry = ".plan/"
    if os.path.exists(gitignore):
        with open(gitignore, encoding="utf-8") as f:
            content = f.read()
        if entry not in content.splitlines():
            with open(gitignore, "a", encoding="utf-8") as f:
                f.write(f"\n{entry}\n")
    else:
        with open(gitignore, "w", encoding="utf-8") as f:
            f.write(f"{entry}\n")

    _output({"status": "initialized", "plan_dir": pd, "language": language, "framework": framework, "is_git_repo": project["is_git_repo"]})


def _detect_language(project_dir):
    """智能检测项目语言"""
    if os.path.exists(os.path.join(project_dir, "go.mod")):
        return "go"
    if os.path.exists(os.path.join(project_dir, "pyproject.toml")) or os.path.exists(os.path.join(project_dir, "requirements.txt")) or os.path.exists(os.path.join(project_dir, "setup.py")):
        return "python"
    if os.path.exists(os.path.join(project_dir, "package.json")):
        # 先检查 tsconfig.json 存在
        if os.path.exists(os.path.join(project_dir, "tsconfig.json")):
            return "typescript"
        with open(os.path.join(project_dir, "package.json"), encoding="utf-8") as f:
            content = f.read()
        if "typescript" in content or "tsx" in content or '"tsc"' in content:
            return "typescript"
        return "javascript"
    if os.path.exists(os.path.join(project_dir, "Cargo.toml")):
        return "rust"
    if os.path.exists(os.path.join(project_dir, "pom.xml")):
        return "java"
    return ""


def _detect_framework(project_dir, language):
    """根据语言智能检测框架"""
    if language == "go":
        if os.path.exists(os.path.join(project_dir, "internal")) and os.path.exists(os.path.join(project_dir, "cmd")):
            return "gin"
        return "standard"

    if language == "python":
        if os.path.exists(os.path.join(project_dir, "manage.py")) or os.path.exists(os.path.join(project_dir, "settings.py")):
            return "django"
        if os.path.exists(os.path.join(project_dir, "app.py")) or os.path.exists(os.path.join(project_dir, "requirements.txt")):
            with open(os.path.join(project_dir, "requirements.txt"), encoding="utf-8") as f:
                if "flask" in f.read().lower():
                    return "flask"
                if "fastapi" in f.read().lower():
                    return "fastapi"
        return "standard"

    if language == "javascript" or language == "typescript":
        if os.path.exists(os.path.join(project_dir, "next.config.js")) or os.path.exists(os.path.join(project_dir, "next.config.ts")):
            return "next"
        if os.path.exists(os.path.join(project_dir, "vite.config.js")) or os.path.exists(os.path.join(project_dir, "vite.config.ts")):
            return "vite"
        if os.path.exists(os.path.join(project_dir, "webpack.config.js")):
            return "webpack"
        return "standard"

    return ""


def _detect_has_frontend(project_dir):
    """检测项目是否包含前端代码"""
    # 直接是前端项目（根目录有 package.json + 前端框架）
    pkg_path = os.path.join(project_dir, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, encoding="utf-8") as f:
                content = f.read().lower()
            if any(fw in content for fw in ["react", "vue", "svelte", "angular", "next", "nuxt", "solid-js"]):
                return True
        except (IOError, OSError):
            pass

    # 子目录有前端（如 web/, frontend/, client/）
    for subdir in ["web", "frontend", "client", "ui", "app"]:
        sub_pkg = os.path.join(project_dir, subdir, "package.json")
        if os.path.exists(sub_pkg):
            try:
                with open(sub_pkg, encoding="utf-8") as f:
                    content = f.read().lower()
                if any(fw in content for fw in ["react", "vue", "svelte", "angular", "next", "nuxt", "solid-js"]):
                    return True
            except (IOError, OSError):
                pass

    # 检测常见前端文件
    for pattern in ["src/App.tsx", "src/App.vue", "src/App.svelte", "src/main.tsx", "src/main.ts"]:
        if os.path.exists(os.path.join(project_dir, pattern)):
            return True
        # 子目录
        for subdir in ["web", "frontend", "client"]:
            if os.path.exists(os.path.join(project_dir, subdir, pattern)):
                return True

    return False


# 前端文件扩展名（用于检测 handoff 中的前端文件变更）
_FRONTEND_EXTS = {
    '.html', '.htm', '.ejs', '.hbs', '.pug',
    '.css', '.scss', '.sass', '.less', '.styl',
    '.jsx', '.tsx', '.vue', '.svelte',
}


def _has_frontend_file_changes(project_dir):
    """扫描 handoff 文件，检测是否有前端文件被创建或修改"""
    handoff_dir = os.path.join(_plan_dir(project_dir), "handoff")
    if not os.path.isdir(handoff_dir):
        return False, []

    frontend_files = []
    for fname in sorted(os.listdir(handoff_dir)):
        fpath = os.path.join(handoff_dir, fname)
        if not os.path.isfile(fpath):
            continue
        try:
            with open(fpath, encoding="utf-8") as f:
                content = f.read()
        except (IOError, OSError):
            continue
        # 提取文件路径：反引号内 或 列表项中的路径
        paths_found = set()
        # 1. 反引号包裹: `path/to/file.tsx`
        for m in re.finditer(r'`([^`]+)`', content):
            paths_found.add(m.group(1).strip())
        # 2. 列表项: - path/to/file.tsx
        for m in re.finditer(r'^[-*]\s+(\S+\.\w+)\s*$', content, re.MULTILINE):
            paths_found.add(m.group(1).strip())
        for path in paths_found:
            ext = os.path.splitext(path)[1].lower()
            if ext in _FRONTEND_EXTS:
                if path not in frontend_files:
                    frontend_files.append(path)

    return bool(frontend_files), frontend_files


def _detect_has_database(project_dir):
    """检测项目是否使用数据库"""
    # Go: 常见数据库驱动
    go_mod = os.path.join(project_dir, "go.mod")
    if os.path.exists(go_mod):
        try:
            with open(go_mod, encoding="utf-8") as f:
                content = f.read().lower()
            db_indicators = [
                "database/sql", "gorm.io", "go-redis", "mongo-driver",
                "pgx", "go-sqlite3", "sqlx", "ent", "sqlc",
            ]
            if any(ind in content for ind in db_indicators):
                return True
        except (IOError, OSError):
            pass

    # Python: 常见 ORM / 数据库库
    for req_file in ["requirements.txt", "pyproject.toml", "setup.py", "Pipfile"]:
        path = os.path.join(project_dir, req_file)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read().lower()
                db_indicators = [
                    "sqlalchemy", "django", "tortoise-orm", "peewee",
                    "pymongo", "redis", "psycopg", "mysql-connector",
                    "asyncpg", "aiosqlite", "prisma",
                ]
                if any(ind in content for ind in db_indicators):
                    return True
            except (IOError, OSError):
                pass

    # Node.js: 常见数据库库
    for pkg_dir in ["", "web", "frontend", "server", "backend", "api"]:
        pkg_path = os.path.join(project_dir, pkg_dir, "package.json") if pkg_dir else os.path.join(project_dir, "package.json")
        if os.path.exists(pkg_path):
            try:
                with open(pkg_path, encoding="utf-8") as f:
                    content = f.read().lower()
                db_indicators = [
                    "prisma", "typeorm", "sequelize", "mongoose", "knex",
                    "drizzle-orm", "mikro-orm", "pg", "mysql2", "redis",
                    "ioredis", "better-sqlite3",
                ]
                if any(ind in content for ind in db_indicators):
                    return True
            except (IOError, OSError):
                pass

    # 检测常见数据库配置文件
    db_config_files = [
        "docker-compose.yml", "docker-compose.yaml",
        "prisma/schema.prisma", "migrations",
        "alembic.ini", "alembic",
    ]
    for f in db_config_files:
        if os.path.exists(os.path.join(project_dir, f)):
            return True

    return False


def _detect_has_external_api(project_dir):
    """检测项目是否调用外部 API"""
    # Go: HTTP 客户端库
    go_mod = os.path.join(project_dir, "go.mod")
    if os.path.exists(go_mod):
        try:
            with open(go_mod, encoding="utf-8") as f:
                content = f.read().lower()
            api_indicators = ["resty", "go-retryablehttp", "grpc"]
            if any(ind in content for ind in api_indicators):
                return True
        except (IOError, OSError):
            pass

    # Python: HTTP 客户端库
    for req_file in ["requirements.txt", "pyproject.toml"]:
        path = os.path.join(project_dir, req_file)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read().lower()
                api_indicators = ["httpx", "aiohttp", "requests", "grpcio", "boto3", "stripe"]
                if any(ind in content for ind in api_indicators):
                    return True
            except (IOError, OSError):
                pass

    # Node.js: HTTP 客户端库
    pkg_path = os.path.join(project_dir, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, encoding="utf-8") as f:
                content = f.read().lower()
            api_indicators = ["axios", "got", "node-fetch", "ky", "@grpc", "stripe", "aws-sdk"]
            if any(ind in content for ind in api_indicators):
                return True
        except (IOError, OSError):
            pass

    return False


def _detect_has_api_server(project_dir, language, framework):
    """检测项目是否是 HTTP/API 服务（需要启动服务做验收测试）"""
    # 已知 Web 框架直接判定
    web_frameworks = {
        "gin", "echo", "fiber", "chi", "mux", "iris",           # Go
        "fastapi", "flask", "django", "sanic", "starlette",     # Python
        "express", "nest", "hono", "koa", "fastify",            # Node.js
        "next", "nuxt",                                         # SSR 框架
    }
    if framework in web_frameworks:
        return True

    # Go: 检测 net/http 或 Web 框架
    go_mod = os.path.join(project_dir, "go.mod")
    if os.path.exists(go_mod):
        try:
            with open(go_mod, encoding="utf-8") as f:
                content = f.read().lower()
            server_indicators = [
                "gin-gonic/gin", "labstack/echo", "gofiber/fiber",
                "go-chi/chi", "gorilla/mux", "kataras/iris",
            ]
            if any(ind in content for ind in server_indicators):
                return True
        except (IOError, OSError):
            pass
        # 检查 main.go 是否有 http.ListenAndServe
        main_go = os.path.join(project_dir, "main.go")
        if os.path.exists(main_go):
            try:
                with open(main_go, encoding="utf-8") as f:
                    content = f.read()
                if "ListenAndServe" in content or "http.Server" in content:
                    return True
            except (IOError, OSError):
                pass

    # Python: 检测 Web 框架
    for req_file in ["requirements.txt", "pyproject.toml"]:
        path = os.path.join(project_dir, req_file)
        if os.path.exists(path):
            try:
                with open(path, encoding="utf-8") as f:
                    content = f.read().lower()
                server_indicators = [
                    "fastapi", "flask", "django", "sanic",
                    "starlette", "tornado", "bottle", "aiohttp",
                ]
                if any(ind in content for ind in server_indicators):
                    return True
            except (IOError, OSError):
                pass

    # Node.js: 检测 server 框架
    pkg_path = os.path.join(project_dir, "package.json")
    if os.path.exists(pkg_path):
        try:
            with open(pkg_path, encoding="utf-8") as f:
                content = f.read().lower()
            server_indicators = [
                "express", "fastify", "koa", "hono", "@nestjs",
                "next", "nuxt",
            ]
            if any(ind in content for ind in server_indicators):
                return True
        except (IOError, OSError):
            pass

    return False


def cmd_status(args):
    """返回当前状态"""
    pd = _plan_dir(args.project_dir)
    if not os.path.exists(os.path.join(pd, "project.yaml")):
        _output({"status": "not_initialized"})
        return

    project = _read_project(pd)
    last_event = _read_last_trace(pd)

    result = {
        "current_agent": project.get("current_agent", ""),
        "current_phase": project.get("current_phase", ""),
        "current_task": project.get("current_task", ""),
        "mode": project.get("mode", "full"),
        "language": project.get("language", ""),
        "framework": project.get("framework", ""),
        "last_event": last_event,
    }

    # 计算恢复动作
    event = last_event.get("event", "")
    current_agent = project.get("current_agent", "")
    if event == "done" or current_agent == "done":
        result["resume_action"] = "completed"
        result["current_agent"] = "done"
    elif event == "blocked":
        result["resume_action"] = "await_approval"
    else:
        result["resume_action"] = f"dispatch_{current_agent}"

    # 检查 missing artifacts
    artifacts_dir = os.path.join(pd, "artifacts")
    missing_artifacts = []
    for agent_key, info in REQUIRED_ARTIFACTS.items():
        phase = PHASE_MAP.get(agent_key, "")
        # 如果当前阶段已经过了该 agent 的阶段，检查 artifact 是否存在
        artifact_path = os.path.join(artifacts_dir, info["file"])
        if not os.path.exists(artifact_path):
            missing_artifacts.append(info["file"])
    if missing_artifacts:
        result["missing_artifacts"] = missing_artifacts

    _output(result)


def cmd_handoff(args):
    """记录 Handoff: 写 handoff 文件 + trace + 更新 project.yaml"""
    pd = _plan_dir(args.project_dir)
    project = _read_project(pd)

    # full 模式下 developer/reviewer 的 handoff 必须提供 --current-task
    # 注意：tester 不在此列，因为 Tester 是全项目级测试，不绑定特定 Task
    mode = project.get("mode", "full")
    if mode == "full" and args.from_agent in ("developer", "reviewer"):
        if not args.current_task:
            _output({
                "error": f"full 模式下 {args.from_agent} 的 handoff 必须提供 --current-task",
                "hint": "请在 handoff 命令中添加 --current-task \"Task N\"",
            })
            sys.exit(1)

    # developer handoff 时验证 current_task 已通过 complete-task 标记
    if args.from_agent == "developer" and args.current_task:
        completed_tasks = project.get("completed_tasks", [])
        if not isinstance(completed_tasks, list):
            completed_tasks = []
        if args.current_task not in completed_tasks:
            _output({
                "error": f"Developer handoff 的 {args.current_task} 未通过 complete-task 标记完成",
                "hint": f"请先调用: orchestrator.py complete-task --task-id \"{args.current_task}\"",
            })
            sys.exit(1)

    # 计算序号
    handoff_dir = os.path.join(pd, "handoff")
    os.makedirs(handoff_dir, exist_ok=True)
    existing = [f for f in os.listdir(handoff_dir) if f.endswith(".md")]
    seq = len(existing) + 1

    # 写 handoff 文件
    filename = f"{seq:03d}-{args.from_agent}-to-{args.to_agent}.md"
    approval_line = "human_approved: true\n" if args.approved else ""

    # 构建文件列表部分
    files_section = ""
    if args.files_created or args.files_modified:
        files_section = "\n## 文件变更\n"
        if args.files_created:
            files_section += "\n### 新建文件\n"
            for f in args.files_created.split(","):
                f = f.strip()
                if f:
                    files_section += f"- `{f}`\n"
        if args.files_modified:
            files_section += "\n### 修改文件\n"
            for f in args.files_modified.split(","):
                f = f.strip()
                if f:
                    files_section += f"- `{f}`\n"

    content = f"""---
from: {args.from_agent}
to: {args.to_agent}
timestamp: {_now()}
project: {project.get('name', '')}
phase: {_agent_to_phase(args.to_agent)}
{approval_line}---

## 摘要
{args.summary or ''}

## 当前 Task
{args.current_task or ''}
{files_section}"""
    with open(os.path.join(handoff_dir, filename), "w", encoding="utf-8") as f:
        f.write(content)

    # 写 trace
    _write_trace(pd, args.from_agent, "handoff",
                 f"→ {args.to_agent}", args.summary or "")

    # 更新 project.yaml
    project["current_agent"] = args.to_agent
    project["current_phase"] = _agent_to_phase(args.to_agent)
    if args.current_task:
        project["current_task"] = args.current_task
    if args.mode:
        project["mode"] = args.mode
    history = project.get("history", [])
    if not isinstance(history, list):
        history = []
    entry = {
        "from": args.from_agent,
        "to": args.to_agent,
        "timestamp": _now(),
    }
    if args.approved:
        entry["approved"] = True
    history.append(entry)
    project["history"] = history
    _write_project(pd, project)

    _output({"status": "ok", "handoff_file": filename})
    _update_state_md(args.project_dir)


def cmd_trace(args):
    """写入 trace 日志"""
    pd = _plan_dir(args.project_dir)
    duration = None
    if args.start_time:
        try:
            start = datetime.fromisoformat(args.start_time)
            duration = int((datetime.now(timezone.utc) - start).total_seconds())
        except (ValueError, TypeError):
            pass
    _write_trace(pd, args.agent, args.event,
                 args.detail or "", args.message or "", duration=duration)
    result = {"status": "ok"}
    if duration is not None:
        result["duration_sec"] = duration
    _output(result)


def cmd_next(args):
    """计算下一步（强制流程规则）— 不可被 LLM 绕过"""
    rules = {
        ("developer", "done"): "reviewer",
        ("developer", "rollback"): "_rollback",
        ("reviewer", "PASS"): "_check_tasks",
        ("reviewer", "FAIL"): "developer",
        ("tester", "PASS"): "done",
        ("tester", "done"): "done",       # alias: accept "done" as PASS
        ("tester", "FAIL"): "developer",
        ("triage", "done"): "_from_route",
        ("pm", "done"): "_pm_next",
        ("ui-designer", "done"): "architect",
        ("ui-designer", "rollback"): "pm",
        ("architect", "done"): "_await_approval",
        ("architect", "rollback"): "_architect_rollback",
    }

    key = (args.current_agent, args.conclusion)
    target = rules.get(key)

    if target is None:
        _output({"error": f"未知状态: agent={args.current_agent}, conclusion={args.conclusion}"})
        sys.exit(1)

    # Artifact 前置检查：reviewer/tester 完成时必须有对应 report 文件
    if args.current_agent in REQUIRED_ARTIFACTS:
        artifact_info = REQUIRED_ARTIFACTS[args.current_agent]
        artifact_path = os.path.join(
            _plan_dir(args.project_dir), "artifacts", artifact_info["file"]
        )
        if not os.path.exists(artifact_path):
            _output({
                "error": f"{artifact_info['agent_name']} 未生成 {artifact_info['file']}，"
                         f"不可推进流程。请确保 {artifact_info['agent_name']} Agent 已创建该文件。",
                "missing_artifact": artifact_info["file"],
                "expected_path": artifact_path,
            })
            sys.exit(1)

    if target == "_rollback":
        allowed = ["architect", "pm"]
        rollback_to = args.route_to if args.route_to in allowed else "architect"
        task = args.current_task or None
        _increment_rollback(args.project_dir, task=task)
        count = _get_rollback_count(args.project_dir, task=task)
        scope = f"（{task}）" if task else ""
        if count > 2:
            _output({
                "next_agent": "human",
                "blocked": True,
                "reason": f"回退超过 2 次{scope}（当前 {count} 次），需人工介入",
            })
            return
        _output({
            "next_agent": rollback_to,
            "reason": f"Developer 回退到 {rollback_to}{scope}（第 {count} 次回退）",
        })
        return

    if target == "_check_tasks":
        pd = _plan_dir(args.project_dir)
        project = _read_project(pd)
        current_task = args.current_task or project.get("current_task", "")
        total = args.total_tasks
        completed_tasks = project.get("completed_tasks", [])
        if not isinstance(completed_tasks, list):
            completed_tasks = []

        # Batch completion: --completed-through allows skipping ahead
        completed_through = getattr(args, 'completed_through', None)
        if completed_through is not None:
            # 校验: 1-N 中所有 Task 必须已有完成记录
            missing = []
            for i in range(1, completed_through + 1):
                task_id = f"Task {i}"
                if task_id not in completed_tasks:
                    missing.append(task_id)
            if missing:
                _output({
                    "error": f"completed-through {completed_through} 校验失败: 以下 Task 未标记完成: {', '.join(missing)}",
                    "hint": "请先对每个完成的 Task 调用 complete-task 命令",
                    "missing_tasks": missing,
                })
                sys.exit(1)

            if completed_through >= total:
                # Update project state
                pd = _plan_dir(args.project_dir)
                project = _read_project(pd)
                project["current_agent"] = "tester"
                project["current_phase"] = "testing"
                _write_project(pd, project)
                _update_state_md(args.project_dir)
                _output({
                    "next_agent": "tester",
                    "reason": f"批量审查通过（Task 1-{completed_through}），所有 {total} 个 Task 完成，进入整体测试",
                })
            else:
                next_task = f"Task {completed_through + 1}"
                pd = _plan_dir(args.project_dir)
                project = _read_project(pd)
                project["current_task"] = next_task
                _write_project(pd, project)
                _update_state_md(args.project_dir)
                _output({
                    "next_agent": "developer",
                    "next_task": next_task,
                    "reason": f"批量审查通过（至 Task {completed_through}），进入 {next_task}",
                })
            return

        if total is None:
            project["current_agent"] = "tester"
            project["current_phase"] = "testing"
            _write_project(pd, project)
            _update_state_md(args.project_dir)
            _output({"next_agent": "tester", "reason": "未提供 task 总数，进入整体测试"})
            return

        if current_task:
            # 门控：current_task 必须已通过 complete-task 标记完成
            if current_task not in completed_tasks:
                _output({
                    "error": f"{current_task} 未通过 complete-task 标记完成，不可推进到下一步。",
                    "hint": f"请先调用: orchestrator.py complete-task --project-dir {{PWD}} --task-id \"{current_task}\"",
                    "current_task": current_task,
                    "completed_tasks": completed_tasks,
                })
                sys.exit(1)
            match = re.search(r'\d+', current_task)
            if match:
                task_num = int(match.group())
                if task_num < total:
                    next_task = f"Task {task_num + 1}"
                    project["current_task"] = next_task
                    project["current_agent"] = "developer"
                    project["current_phase"] = "coding"
                    _write_project(pd, project)
                    _update_state_md(args.project_dir)
                    _output({
                        "next_agent": "developer",
                        "next_task": next_task,
                        "reason": f"{current_task} 审查通过，进入 {next_task}",
                    })
                else:
                    project["current_agent"] = "tester"
                    project["current_phase"] = "testing"
                    _write_project(pd, project)
                    _update_state_md(args.project_dir)
                    _output({
                        "next_agent": "tester",
                        "reason": f"所有 {total} 个 Task 审查通过，进入整体测试",
                    })
            else:
                project["current_agent"] = "tester"
                project["current_phase"] = "testing"
                _write_project(pd, project)
                _update_state_md(args.project_dir)
                _output({"next_agent": "tester", "reason": "无法解析 Task 编号，进入测试"})
        else:
            project["current_agent"] = "tester"
            project["current_phase"] = "testing"
            _write_project(pd, project)
            _update_state_md(args.project_dir)
            _output({"next_agent": "tester", "reason": "无 Task List，直接进入测试"})
        return

    if target == "_pm_next":
        # PM 完成后：有前端 → ui-designer，无前端 → architect
        pd = _plan_dir(args.project_dir)
        project = _read_project(pd)
        has_frontend = project.get("has_frontend", False)
        if has_frontend:
            project["current_agent"] = "ui-designer"
            project["current_phase"] = "ui-design"
            _write_project(pd, project)
            _update_state_md(args.project_dir)
            _output({
                "next_agent": "ui-designer",
                "reason": "PRD 完成，项目包含前端，进入 UI 设计",
            })
        else:
            project["current_agent"] = "architect"
            project["current_phase"] = "design"
            _write_project(pd, project)
            _update_state_md(args.project_dir)
            _output({
                "next_agent": "architect",
                "reason": "PRD 完成，进入架构设计",
            })
        return

    if target == "_architect_rollback":
        # Architect 回退：有前端时可退回 ui-designer 或 pm
        pd = _plan_dir(args.project_dir)
        project = _read_project(pd)
        has_frontend = project.get("has_frontend", False)
        rollback_to = args.route_to if args.route_to in ["pm", "ui-designer"] else ("ui-designer" if has_frontend else "pm")
        _update_state_md(args.project_dir)
        _output({
            "next_agent": rollback_to,
            "reason": f"Architect 回退到 {rollback_to}",
        })
        return

    if target == "_await_approval":
        _update_state_md(args.project_dir)
        _output({
            "next_agent": "developer",
            "blocked": True,
            "reason": "🔒 等待人工审批",
        })
        return

    if target == "_from_route":
        _update_state_md(args.project_dir)
        _output({
            "next_agent": args.route_to or "pm",
            "reason": "Triage 路由",
        })
        return

    reason_map = {
        "reviewer": f"{args.current_task or 'Task'} 完成，必须经过 Reviewer 审查",
        "developer": "Reviewer/Tester 发现问题，退回 Developer",
        "done": "所有测试通过，流程完成",
        "architect": "UI 设计完成，进入架构设计",
        "ui-designer": "PRD 完成，进入 UI 设计",
        "pm": "回退到 PM",
    }

    result = {
        "next_agent": target,
        "reason": reason_map.get(target, ""),
    }
    if target == "done":
        pd = _plan_dir(args.project_dir)
        proj = _read_project(pd)
        proj["current_agent"] = "done"
        proj["current_phase"] = "done"
        _write_project(pd, proj)
    if args.current_task:
        result["next_task"] = args.current_task
    _output(result)
    _update_state_md(args.project_dir)


def cmd_parse_tasks(args):
    """解析 design.md 中的 Task List - 优化版：支持多种格式"""
    design_path = os.path.join(args.project_dir, ".plan", "artifacts", "design.md")
    if not os.path.exists(design_path):
        _output({"error": "design.md not found", "tasks": [], "total": 0})
        return

    with open(design_path, encoding="utf-8") as f:
        content = f.read()

    tasks = []
    debug_info = [] if hasattr(args, 'debug') and args.debug else None
    parse_method = "regex_fallback"

    # YAML-first: 解析 <!-- task-meta ... --> 块
    meta_pattern = re.compile(
        r'###\s+(Task[- ]?\d+)[：:]\s*(.+?)\n'
        r'<!-- task-meta\s*\n(.*?)\n-->',
        re.DOTALL
    )
    meta_matches = meta_pattern.findall(content)
    if meta_matches:
        parse_method = "yaml_meta"
        for raw_id, name, yaml_str in meta_matches:
            tid = _normalize_task_id(raw_id)
            meta = _simple_yaml_load(yaml_str)
            # files 字段: 支持 YAML list 语法 [a, b] 或逐行 - a
            files = meta.get("files", [])
            if isinstance(files, str):
                files = [f.strip() for f in files.split(",") if f.strip()]
            elif not isinstance(files, list):
                files = []
            # deps 字段
            deps_raw = meta.get("deps", [])
            if isinstance(deps_raw, str):
                deps_raw = [d.strip() for d in deps_raw.split(",") if d.strip()]
            elif not isinstance(deps_raw, list):
                deps_raw = []
            deps = [_normalize_task_id(str(d)) for d in deps_raw] if deps_raw else []
            tasks.append({
                "id": tid, "name": name.strip(),
                "files": files,
                "deps": deps,
                "wave": int(meta.get("wave", 1)),
            })
        # 从 wave 字段构建 waves dict + parallel_groups
        waves = {}
        for t in tasks:
            w = str(t.get("wave", 1))
            waves.setdefault(w, []).append(t["id"])
        parallel_groups = [waves[k] for k in sorted(waves.keys(), key=int)]
    else:
        # Regex fallback: 原有正则逻辑
        # 支持多种 Task 标题格式
        task_pattern = re.compile(r'(?:### )?(Task[- ]?\d+)[：:]\s*(.+?)(?=\n(?:### )?(?:Task[- ]?\d+[：:]|## |$))', re.DOTALL)

        for match in task_pattern.finditer(content):
            task_id = _normalize_task_id(match.group(1))
            task_name = match.group(2).strip()
            # 清理 name：去除文件清单、依赖等元数据，只保留描述
            task_name = re.sub(
                r'\s*\*{0,2}(?:文件[清单]*|Files?|依赖|Depends|deps)\*{0,2}\s*[：:].*',
                '', task_name, flags=re.DOTALL | re.IGNORECASE
            ).strip()
            task_name = re.sub(r'\s+', ' ', task_name)

            task = {"id": task_id, "name": task_name, "files": [], "deps": []}
            section_content = match.group(0)

            # 提取文件列表（支持 文件/文件清单/Files 等标签，支持多行 - file 格式）
            file_line_match = re.search(
                r'\*{0,2}(?:文件[清单]*|Files?)\*{0,2}\s*[：:]\s*\*{0,2}\s*(.+?)(?=\n\*{0,2}(?:依赖|Depends|deps)|\n#{2,}|\Z)',
                section_content, re.DOTALL | re.IGNORECASE
            )
            if file_line_match:
                file_block = file_line_match.group(1).strip()
                # 优先提取 backtick 路径
                backtick_paths = re.findall(r'`([^`]+)`', file_block)
                if backtick_paths:
                    for p in backtick_paths:
                        clean = re.sub(r'[（(].+?[）)]', '', p).strip()
                        if clean and ('/' in clean or '.' in clean):
                            task["files"].append(clean)
                else:
                    # 提取 "- filepath" 列表项或逗号分隔
                    list_items = re.findall(r'^[-*]\s+(.+)', file_block, re.MULTILINE)
                    if list_items:
                        for item in list_items:
                            clean = re.sub(r'[（(].+?[）)]', '', item).strip().strip('`')
                            if clean and ('/' in clean or '.' in clean):
                                task["files"].append(clean)
                    elif file_block:
                        for p in re.split(r'[,，]', file_block):
                            clean = re.sub(r'[（(].+?[）)]', '', p).strip().strip('`')
                            if clean and clean.lower() not in ['无', 'none', '']:
                                task["files"].append(clean)

            # 提取依赖（strip markdown bold markers from captured value）
            dep_match = re.search(
                r'\*{0,2}(?:依赖|Depends|deps)\*{0,2}\s*[：:]\s*\*{0,2}\s*(.+?)(?:\n[-*] |\n#{2,} |\Z)',
                section_content, re.DOTALL | re.IGNORECASE
            )
            if dep_match:
                dep_text = dep_match.group(1).strip().strip('*').strip()
                if dep_text.lower() not in ["无", "none", ""]:
                    for sep in [',', '，']:
                        deps = [d.strip().strip('*').strip() for d in dep_text.split(sep) if d.strip().strip('*').strip()]
                        if len(deps) > 1:
                            task["deps"] = [_normalize_task_id(d) if re.match(r'[Tt]ask', d) else d for d in deps]
                            break
                    if not task["deps"]:
                        task_refs = re.findall(r'Task[- \s]?\d+', dep_text, re.IGNORECASE)
                        if task_refs:
                            task["deps"] = [_normalize_task_id(t.strip()) for t in task_refs]
                        else:
                            task["deps"] = [dep_text]

            tasks.append(task)

        # 更宽松的 fallback（仅在 "## Task List" section 内搜索）
        if not tasks:
            task_list_match = re.search(
                r'## Task List\s*\n(.*?)(?=\n## |\Z)', content, re.DOTALL
            )
            search_content = task_list_match.group(1) if task_list_match else ""
            if search_content:
                for i, line in enumerate(search_content.split('\n'), 1):
                    m = re.match(r'^\s*(\d+)\.\s*(.+)$', line)
                    if m:
                        tasks.append({
                            "id": f"Task {m.group(1)}",
                            "name": m.group(2).strip(),
                            "files": [], "deps": []
                        })

        # 分析并行分组：无依赖或依赖已完成的 Task 可以并行
        task_ids = [t["id"] for t in tasks]
        parallel_groups = []
        remaining = list(range(len(tasks)))
        resolved = set()

        while remaining:
            group = []
            for idx in remaining:
                deps = tasks[idx]["deps"]
                if not deps or all(d in resolved for d in deps):
                    group.append(tasks[idx]["id"])
            if not group:
                group = [tasks[remaining[0]]["id"]]
            parallel_groups.append(group)
            resolved.update(group)
            remaining = [i for i in remaining if tasks[i]["id"] not in resolved]

    # 构建 waves dict（YAML 路径已在上面构建，regex 路径从 parallel_groups 构建）
    if parse_method == "regex_fallback":
        waves = {}
        for i, group in enumerate(parallel_groups, 1):
            waves[str(i)] = group

    result = {
        "tasks": tasks, "total": len(tasks),
        "parallel_groups": parallel_groups,
        "waves": waves,
        "total_waves": len(parallel_groups),
        "parse_method": parse_method,
    }

    # 将 wave 信息写入 project.yaml
    if tasks:
        pd = _plan_dir(args.project_dir)
        project = _read_project(pd)
        project["total_waves"] = len(parallel_groups)
        if "current_wave" not in project:
            project["current_wave"] = 1
        _write_project(pd, project)
        _update_state_md(args.project_dir)

    if debug_info is not None:
        result["debug"] = {
            "design_path": design_path,
            "content_length": len(content),
            "task_count": len(tasks)
        }

    _output(result)


def cmd_approve(args):
    """记录审批通过"""
    pd = _plan_dir(args.project_dir)
    _write_trace(pd, "system", "approved", "", "用户确认设计")

    project = _read_project(pd)
    project["current_agent"] = "developer"
    project["current_phase"] = "coding"
    _write_project(pd, project)

    _output({"status": "approved"})
    _update_state_md(args.project_dir)


def cmd_parse_json(args):
    """从 Agent 输出中提取 ---JSON--- 标记包裹的 JSON"""
    text = sys.stdin.read()

    # 优先提取 ---JSON--- 标记
    m = re.search(r'---JSON---\s*(.*?)\s*---JSON---', text, re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group(1))
            _output(parsed)
            return
        except json.JSONDecodeError:
            pass

    # 降级：提取 ```json 代码块
    m = re.search(r'```json\s*(\{.*?\})\s*```', text, re.DOTALL)
    if m:
        try:
            parsed = json.loads(m.group(1))
            _output(parsed)
            return
        except json.JSONDecodeError:
            pass

    # 降级：尝试找裸 JSON 对象（支持嵌套）
    # 从每个 '{' 开始尝试 json.loads，找到包含 "status" 的有效 JSON
    for i, ch in enumerate(text):
        if ch == '{' and '"status"' in text[i:i+500]:
            # 向后搜索匹配的 '}'
            depth = 0
            for j in range(i, len(text)):
                if text[j] == '{':
                    depth += 1
                elif text[j] == '}':
                    depth -= 1
                    if depth == 0:
                        candidate = text[i:j+1]
                        try:
                            parsed = json.loads(candidate)
                            if isinstance(parsed, dict) and "status" in parsed:
                                _output(parsed)
                                return
                        except json.JSONDecodeError:
                            pass
                        break

    _output({"error": "no JSON found in agent output"})
    sys.exit(1)


# === 入口 ===

def main():
    parser = argparse.ArgumentParser(description="Dev Framework Orchestrator")
    sub = parser.add_subparsers(dest="command")

    # init
    p = sub.add_parser("init", help="初始化 .plan/ 目录")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--language", default="")
    p.add_argument("--framework", default="")

    # status
    p = sub.add_parser("status", help="返回当前状态")
    p.add_argument("--project-dir", required=True)

    # handoff
    p = sub.add_parser("handoff", help="记录 Handoff")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--from", dest="from_agent", required=True)
    p.add_argument("--to", dest="to_agent", required=True)
    p.add_argument("--summary", default="")
    p.add_argument("--mode", default="")
    p.add_argument("--current-task", default="")
    p.add_argument("--approved", action="store_true")
    p.add_argument("--files-created", default="", help="逗号分隔的新建文件列表")
    p.add_argument("--files-modified", default="", help="逗号分隔的修改文件列表")

    # trace
    p = sub.add_parser("trace", help="写入 trace 日志")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--agent", required=True)
    p.add_argument("--event", required=True)
    p.add_argument("--detail", default="")
    p.add_argument("--message", default="")
    p.add_argument("--start-time", default="", help="Agent 开始时间（ISO 格式），用于计算耗时")

    # next
    p = sub.add_parser("next", help="计算下一步（强制流程规则）")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--current-agent", required=True)
    p.add_argument("--conclusion", required=True)
    p.add_argument("--current-task", default="")
    p.add_argument("--total-tasks", type=int, default=None)
    p.add_argument("--completed-through", type=int, default=None,
                   help="批量审查通过: 标记至 Task N 全部 PASS，跳过中间的逐 Task 循环")
    p.add_argument("--route-to", default="")

    # parse-tasks
    p = sub.add_parser("parse-tasks", help="解析 design.md Task List")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--debug", action="store_true", help="输出调试信息")

    # approve
    p = sub.add_parser("approve", help="记录审批通过")
    p.add_argument("--project-dir", required=True)

    # parse-json
    sub.add_parser("parse-json", help="从 stdin 提取 JSON")

    # diagnose (新命令)
    p = sub.add_parser("diagnose", help="诊断项目状态和配置")
    p.add_argument("--project-dir", required=True)

    # validate-build
    p = sub.add_parser("validate-build", help="验证项目构建（Phase 4.5 集成验证）")
    p.add_argument("--project-dir", required=True)

    # complete-task
    p = sub.add_parser("complete-task", help="标记单个 Task 完成")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--task-id", required=True, help="Task ID, 如 'Task 1'")

    # check-conflicts
    p = sub.add_parser("check-conflicts", help="检查并行 Task 的文件冲突")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--tasks", required=True, help="逗号分隔的 Task ID, 如 'Task 2,Task 3,Task 4'")

    # extract-section
    p = sub.add_parser("extract-section", help="从 artifact 文件提取指定 section")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--file", required=True, help="artifact 文件名, 如 design.md")
    p.add_argument("--section", required=True, help="section 标题, 如 'Task 1'")

    # validate-plan
    p = sub.add_parser("validate-plan", help="验证设计方案完整性（6 维度评分）")
    p.add_argument("--project-dir", required=True)

    # resume
    p = sub.add_parser("resume", help="跨会话恢复: 分析状态并生成恢复上下文")
    p.add_argument("--project-dir", required=True)

    # decision
    p = sub.add_parser("decision", help="记录架构/技术决策")
    p.add_argument("--project-dir", required=True)
    p.add_argument("--agent", required=True, help="做决策的 Agent")
    p.add_argument("--decision", required=True, help="决策内容")
    p.add_argument("--rationale", default="", help="决策理由")

    p = sub.add_parser("detect-frontend-changes", help="检测 handoff 中是否涉及前端文件变更")
    p.add_argument("--project-dir", required=True)

    args = parser.parse_args()
    commands = {
        "init": cmd_init,
        "status": cmd_status,
        "handoff": cmd_handoff,
        "trace": cmd_trace,
        "next": cmd_next,
        "parse-tasks": cmd_parse_tasks,
        "approve": cmd_approve,
        "parse-json": cmd_parse_json,
        "diagnose": cmd_diagnose,
        "validate-build": cmd_validate_build,
        "complete-task": cmd_complete_task,
        "check-conflicts": cmd_check_conflicts,
        "detect-frontend-changes": cmd_detect_frontend_changes,
        "extract-section": cmd_extract_section,
        "resume": cmd_resume,
        "decision": cmd_decision,
        "validate-plan": cmd_validate_plan,
    }

    if args.command in commands:
        commands[args.command](args)
    else:
        parser.print_help()
        sys.exit(1)


def cmd_complete_task(args):
    """标记单个 Task 完成 — Developer 完成 Task 后必须调用"""
    pd = _plan_dir(args.project_dir)
    project = _read_project(pd)
    completed = project.get("completed_tasks", [])
    if not isinstance(completed, list):
        completed = []
    task_id = args.task_id
    if task_id not in completed:
        completed.append(task_id)
    project["completed_tasks"] = completed
    _write_project(pd, project)

    # Wave 进度追踪：同 wave 所有 task 完成 → 自动推进 current_wave
    current_wave = project.get("current_wave", 1)
    total_waves = project.get("total_waves", 0)
    if total_waves > 0:
        # 读取 design.md 获取当前 wave 的 task 列表
        design_path = os.path.join(pd, "artifacts", "design.md")
        if os.path.isfile(design_path):
            with open(design_path, encoding="utf-8") as f:
                dc = f.read()
            meta_pat = re.compile(
                r'###\s+(Task[- ]?\d+)[：:]\s*.+?\n'
                r'<!-- task-meta\s*\n(.*?)\n-->',
                re.DOTALL
            )
            wave_tasks = []
            for m in meta_pat.finditer(dc):
                tid = _normalize_task_id(m.group(1))
                meta = _simple_yaml_load(m.group(2))
                if int(meta.get("wave", 1)) == current_wave:
                    wave_tasks.append(tid)
            if wave_tasks and all(t in completed for t in wave_tasks):
                project["current_wave"] = current_wave + 1
                _write_project(pd, project)

    _write_trace(pd, "system", "task-done", task_id, f"{task_id} 标记完成")
    _output({"status": "ok", "task": task_id, "total_completed": len(completed)})
    _update_state_md(args.project_dir)


def cmd_extract_section(args):
    """从 artifact 文件提取指定 section（支持 ##/### 级别标题匹配）"""
    artifact_path = os.path.join(_plan_dir(args.project_dir), "artifacts", args.file)
    if not os.path.isfile(artifact_path):
        _output({"section": args.section, "content": "", "found": False})
        return
    try:
        with open(artifact_path, encoding="utf-8") as f:
            content = f.read()
    except (IOError, OSError, UnicodeDecodeError) as e:
        _output({"section": args.section, "content": "", "found": False, "error": str(e)})
        return
    # 先找到 section 标题，获取其 heading level（# 数量）
    heading_match = re.search(r'(#{1,3})\s+' + re.escape(args.section), content, re.IGNORECASE)
    if heading_match:
        level = len(heading_match.group(1))  # 1, 2, or 3
        # 截取到同级或更高级标题（# 数量 <= level），保留子级内容
        end_pat = r'\n#{1,' + str(level) + r'}\s'
        start_pat = r'(#{' + str(level) + r'}\s+' + re.escape(args.section) + r'.*?)'
        m = re.search(start_pat + r'(?=' + end_pat + r'|\Z)', content, re.DOTALL | re.IGNORECASE)
    else:
        m = None
    _output({
        "section": args.section,
        "content": m.group(1).strip() if m else "",
        "found": bool(m),
    })


def _update_state_md(project_dir):
    """从 project.yaml + handoff/ 聚合生成 .plan/STATE.md（跨会话恢复用）"""
    pd = _plan_dir(project_dir)
    project = _read_project(pd)

    current_agent = project.get("current_agent", "unknown")
    current_phase = project.get("current_phase", "unknown")
    current_task = project.get("current_task", "")
    current_wave = project.get("current_wave", 1)
    total_waves = project.get("total_waves", 0)
    completed_tasks = project.get("completed_tasks", [])
    if not isinstance(completed_tasks, list):
        completed_tasks = []
    decisions = project.get("decisions", [])
    if not isinstance(decisions, list):
        decisions = []

    # 收集累积文件（from handoffs）
    cumulative_files = {"created": [], "modified": []}
    handoff_dir = os.path.join(pd, "handoff")
    if os.path.isdir(handoff_dir):
        for fname in sorted(os.listdir(handoff_dir)):
            fpath = os.path.join(handoff_dir, fname)
            if not fname.endswith(".md") or not os.path.isfile(fpath):
                continue
            try:
                with open(fpath, encoding="utf-8") as f:
                    hcontent = f.read()
                for m in re.finditer(r'### 新建文件\n(.*?)(?=\n###|\n##|\Z)', hcontent, re.DOTALL):
                    for fm in re.findall(r'`([^`]+)`', m.group(1)):
                        if fm not in cumulative_files["created"]:
                            cumulative_files["created"].append(fm)
                for m in re.finditer(r'### 修改文件\n(.*?)(?=\n###|\n##|\Z)', hcontent, re.DOTALL):
                    for fm in re.findall(r'`([^`]+)`', m.group(1)):
                        if fm not in cumulative_files["modified"]:
                            cumulative_files["modified"].append(fm)
            except (IOError, OSError):
                continue

    # 构建 STATE.md
    lines = [
        f"# STATE — {project.get('name', 'unknown')}",
        f"\n> Auto-generated by orchestrator.py | {_now()}",
        "\n## Current Status\n",
        f"- **Agent**: {current_agent}",
        f"- **Phase**: {current_phase}",
        f"- **Task**: {current_task or 'N/A'}",
        f"- **Wave**: {current_wave}/{total_waves}" if total_waves else f"- **Wave**: N/A",
        f"- **Mode**: {project.get('mode', 'full')}",
        "\n## Progress\n",
        f"| Task | Status |",
        f"|------|--------|",
    ]

    # 尝试从 design.md 获取 task 列表
    design_path = os.path.join(pd, "artifacts", "design.md")
    all_task_ids = []
    if os.path.isfile(design_path):
        with open(design_path, encoding="utf-8") as f:
            dcontent = f.read()
        for tm in re.finditer(r'###\s+(Task[- ]?\d+)[：:]', dcontent):
            tid = _normalize_task_id(tm.group(1))
            if tid not in all_task_ids:
                all_task_ids.append(tid)

    if all_task_ids:
        for tid in all_task_ids:
            status = "done" if tid in completed_tasks else ("in_progress" if tid == current_task else "pending")
            lines.append(f"| {tid} | {status} |")
    elif completed_tasks:
        for tid in completed_tasks:
            lines.append(f"| {tid} | done |")

    # Decisions
    if decisions:
        lines.append("\n## Decisions\n")
        for d in decisions:
            agent = d.get("agent", "?")
            decision = d.get("decision", "")
            rationale = d.get("rationale", "")
            lines.append(f"- **[{agent}]** {decision}")
            if rationale:
                lines.append(f"  - _Rationale_: {rationale}")

    # Cumulative files
    if cumulative_files["created"] or cumulative_files["modified"]:
        lines.append("\n## Cumulative Files\n")
        if cumulative_files["created"]:
            lines.append("### Created")
            for f in cumulative_files["created"]:
                lines.append(f"- `{f}`")
        if cumulative_files["modified"]:
            lines.append("### Modified")
            for f in cumulative_files["modified"]:
                lines.append(f"- `{f}`")

    state_path = os.path.join(pd, "STATE.md")
    with open(state_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


def cmd_resume(args):
    """分析 project 状态并生成恢复上下文（跨会话恢复入口）"""
    pd = _plan_dir(args.project_dir)
    if not os.path.exists(os.path.join(pd, "project.yaml")):
        _output({"error": "项目未初始化，无法恢复"})
        return

    project = _read_project(pd)
    anomalies = []

    current_agent = project.get("current_agent", "")
    current_phase = project.get("current_phase", "")
    current_task = project.get("current_task", "")

    # 检查 trace 与 project.yaml 一致性
    last_event = _read_last_trace(pd)
    event = last_event.get("event", "")
    if event == "done" and current_agent != "done":
        anomalies.append("trace 显示 done 但 project.yaml current_agent 非 done")
    if event == "blocked" and current_phase != "design":
        anomalies.append(f"trace 显示 blocked 但 current_phase={current_phase}（期望 design）")

    # 检查 handoff 链连续性
    handoff_dir = os.path.join(pd, "handoff")
    if os.path.isdir(handoff_dir):
        handoffs = sorted([f for f in os.listdir(handoff_dir) if f.endswith(".md")])
        if handoffs:
            latest = handoffs[-1]
            try:
                with open(os.path.join(handoff_dir, latest), encoding="utf-8") as f:
                    hcontent = f.read()
                # 提取 to: 字段
                to_match = re.search(r'^to:\s*(.+)', hcontent, re.MULTILINE)
                if to_match:
                    handoff_to = to_match.group(1).strip()
                    if handoff_to != current_agent and current_agent != "done":
                        anomalies.append(f"最新 handoff.to={handoff_to} 但 current_agent={current_agent}")
            except (IOError, OSError):
                anomalies.append(f"无法读取最新 handoff: {latest}")

    # 检查 artifact 完整性
    artifacts_dir = os.path.join(pd, "artifacts")
    for agent_key, info in REQUIRED_ARTIFACTS.items():
        phase = PHASE_MAP.get(agent_key, "")
        phase_order = list(PHASE_MAP.values())
        if current_phase in phase_order and phase in phase_order:
            if phase_order.index(current_phase) > phase_order.index(phase):
                if not os.path.exists(os.path.join(artifacts_dir, info["file"])):
                    anomalies.append(f"已过 {phase} 阶段但缺少 {info['file']}")

    # 计算恢复动作
    if event == "done" or current_agent == "done":
        resume_action = "completed"
    elif event == "blocked":
        resume_action = "await_approval"
    else:
        resume_action = f"dispatch_{current_agent}"

    # 构建恢复上下文
    resume_context = {
        "agent": current_agent,
        "phase": current_phase,
        "task": current_task,
        "mode": project.get("mode", "full"),
        "wave": project.get("current_wave", 1),
        "total_waves": project.get("total_waves", 0),
        "completed_tasks": project.get("completed_tasks", []),
    }

    # 生成建议 prompt
    if resume_action == "completed":
        suggested_prompt = "流程已完成。如需重新开始，请删除 .plan/ 目录。"
    elif resume_action == "await_approval":
        suggested_prompt = "设计方案等待审批。请查看 .plan/artifacts/design.md 后确认。"
    else:
        suggested_prompt = f"继续 {current_agent} 阶段"
        if current_task:
            suggested_prompt += f"（当前: {current_task}）"
        suggested_prompt += "。读取最新 handoff 获取上下文。"

    # 更新 STATE.md
    _update_state_md(args.project_dir)

    _output({
        "resume_action": resume_action,
        "resume_context": resume_context,
        "anomalies": anomalies,
        "suggested_prompt": suggested_prompt,
    })


def cmd_decision(args):
    """记录架构/技术决策到 project.yaml["decisions"]"""
    pd = _plan_dir(args.project_dir)
    project = _read_project(pd)
    decisions = project.get("decisions", [])
    if not isinstance(decisions, list):
        decisions = []
    decisions.append({
        "agent": args.agent,
        "decision": args.decision,
        "rationale": args.rationale or "",
        "timestamp": _now(),
    })
    project["decisions"] = decisions
    _write_project(pd, project)
    _write_trace(pd, args.agent, "decision", "", args.decision)
    _update_state_md(args.project_dir)
    _output({"status": "ok", "total_decisions": len(decisions)})


def cmd_validate_plan(args):
    """验证设计方案完整性 — Goal-backward verification（6 维度评分，满分 100）"""
    pd = _plan_dir(args.project_dir)
    design_path = os.path.join(pd, "artifacts", "design.md")
    if not os.path.isfile(design_path):
        _output({"error": "design.md not found", "score": 0, "pass": False})
        return

    with open(design_path, encoding="utf-8") as f:
        content = f.read()

    project = _read_project(pd)
    dims = {}
    blocking = []
    warnings = []

    # 1. Section 完整性 (20 分)
    required_sections = ["技术选型", "数据模型", "API 定义", "Task List", "目录结构"]
    found = sum(1 for s in required_sections if re.search(rf'##\s+{re.escape(s)}', content))
    dims["section_completeness"] = {"score": int(found / len(required_sections) * 20), "max": 20,
                                     "missing": [s for s in required_sections if not re.search(rf'##\s+{re.escape(s)}', content)]}
    if dims["section_completeness"]["missing"]:
        blocking.append(f"缺少 section: {', '.join(dims['section_completeness']['missing'])}")

    # 2. Task 元数据完整 (20 分)
    meta_pattern = re.compile(r'###\s+(Task[- ]?\d+)[：:]\s*(.+?)\n<!-- task-meta\s*\n(.*?)\n-->', re.DOTALL)
    meta_matches = meta_pattern.findall(content)
    task_headers = re.findall(r'###\s+(Task[- ]?\d+)[：:]', content)
    total_tasks = len(task_headers)
    tasks_with_meta = len(meta_matches)
    meta_score = 0
    task_metas = []
    if total_tasks > 0:
        meta_ratio = tasks_with_meta / total_tasks
        meta_score = int(meta_ratio * 10)  # 10 分: 有 meta 块
        # 检查 files 非空 和 name
        valid_count = 0
        for raw_id, name, yaml_str in meta_matches:
            meta = _simple_yaml_load(yaml_str)
            files = meta.get("files", [])
            has_files = bool(files) and files != []
            task_metas.append({"id": _normalize_task_id(raw_id), "meta": meta, "has_files": has_files})
            if has_files and name.strip():
                valid_count += 1
        if tasks_with_meta > 0:
            meta_score += int(valid_count / tasks_with_meta * 10)
        if tasks_with_meta < total_tasks:
            warnings.append(f"{total_tasks - tasks_with_meta} 个 Task 缺少 <!-- task-meta --> 块")
    dims["task_metadata"] = {"score": meta_score, "max": 20, "tasks_total": total_tasks, "tasks_with_meta": tasks_with_meta}

    # 3. DAG 有效性 (15 分) — 依赖引用合法、无环
    dag_score = 15
    all_task_ids = {_normalize_task_id(h) for h in task_headers}
    deps_map = {}
    for tm in task_metas:
        deps_raw = tm["meta"].get("deps", [])
        if isinstance(deps_raw, str):
            deps_raw = [d.strip() for d in deps_raw.split(",") if d.strip()]
        elif not isinstance(deps_raw, list):
            deps_raw = []
        deps = [_normalize_task_id(str(d)) for d in deps_raw if str(d).strip()]
        deps_map[tm["id"]] = deps
        for d in deps:
            if d not in all_task_ids:
                blocking.append(f"{tm['id']} 依赖不存在的 {d}")
                dag_score = max(0, dag_score - 5)

    # 简单环检测（拓扑排序 - Kahn's algorithm）
    in_degree = {tid: 0 for tid in all_task_ids}
    for tid, deps in deps_map.items():
        for d in deps:
            if d in in_degree:
                in_degree[tid] += 1  # tid depends on d → incoming edge
    # Kahn's algorithm
    visited = set()
    queue = [tid for tid, deg in in_degree.items() if deg == 0]
    while queue:
        node = queue.pop(0)
        visited.add(node)
        for tid, deps in deps_map.items():
            if node in deps and tid not in visited:
                in_degree[tid] -= 1
                if in_degree[tid] == 0:
                    queue.append(tid)
    if len(visited) < len(all_task_ids):
        cycle_tasks = all_task_ids - visited
        blocking.append(f"检测到循环依赖: {', '.join(cycle_tasks)}")
        dag_score = 0
    dims["dag_validity"] = {"score": dag_score, "max": 15}

    # 4. 文件覆盖度 (15 分)
    dir_section = re.search(r'## 目录结构\s*\n```\s*\n(.*?)\n```', content, re.DOTALL)
    dir_files = set()
    if dir_section:
        for line in dir_section.group(1).splitlines():
            stripped = line.strip().strip("├─└│ ")
            if '.' in stripped and '/' not in stripped:
                dir_files.add(stripped)
            elif stripped and not stripped.endswith('/'):
                dir_files.add(stripped)
    task_files = set()
    for tm in task_metas:
        files = tm["meta"].get("files", [])
        if isinstance(files, list):
            for f in files:
                task_files.add(os.path.basename(str(f)))
    if dir_files:
        covered = dir_files & task_files
        coverage = len(covered) / len(dir_files) if dir_files else 0
        file_score = int(coverage * 15)
        uncovered = dir_files - task_files
        if uncovered:
            warnings.append(f"目录结构中 {len(uncovered)} 个文件未被 Task 覆盖")
    else:
        file_score = 8  # 无目录结构 section，给中间分
    dims["file_coverage"] = {"score": file_score, "max": 15}

    # 5. Wave 一致性 (15 分)
    wave_score = 15
    for tm in task_metas:
        wave = int(tm["meta"].get("wave", 1))
        deps = deps_map.get(tm["id"], [])
        for d in deps:
            dep_meta = next((t for t in task_metas if t["id"] == d), None)
            if dep_meta:
                dep_wave = int(dep_meta["meta"].get("wave", 1))
                if wave <= dep_wave:
                    warnings.append(f"{tm['id']} wave={wave} 但依赖 {d} wave={dep_wave}")
                    wave_score = max(0, wave_score - 5)
    dims["wave_consistency"] = {"score": wave_score, "max": 15}

    # 6. PRD 对齐 (15 分)
    prd_path = os.path.join(pd, "artifacts", "prd.md")
    prd_score = 15
    if os.path.isfile(prd_path):
        with open(prd_path, encoding="utf-8") as f:
            prd_content = f.read()
        # 提取验收标准关键词
        ac_match = re.search(r'(?:验收标准|Acceptance Criteria)(.*?)(?=\n## |\Z)', prd_content, re.DOTALL | re.IGNORECASE)
        if ac_match:
            ac_text = ac_match.group(1)
            # 提取关键词（名词短语，>= 2 个中文字符或 >= 3 个英文字符）
            keywords = re.findall(r'[\u4e00-\u9fff]{2,}|[a-zA-Z_]{3,}', ac_text)
            keywords = list(set(keywords))[:20]  # 限制数量
            task_text = "\n".join(m[1] for m in meta_matches) if meta_matches else content
            matched = sum(1 for kw in keywords if kw.lower() in task_text.lower())
            if keywords:
                prd_score = int(matched / len(keywords) * 15)
                if prd_score < 8:
                    warnings.append(f"PRD 验收标准关键词覆盖率偏低 ({matched}/{len(keywords)})")
        else:
            prd_score = 10  # 无验收标准 section
    else:
        prd_score = 10  # 无 PRD 文件
    dims["prd_alignment"] = {"score": prd_score, "max": 15}

    total_score = sum(d["score"] for d in dims.values())
    passed = total_score >= 60

    _output({
        "score": total_score,
        "max_score": 100,
        "pass": passed,
        "dimensions": dims,
        "blocking_issues": blocking,
        "warnings": warnings,
    })


def cmd_detect_frontend_changes(args):
    """检测 handoff 中是否涉及前端文件变更"""
    has_changes, files = _has_frontend_file_changes(args.project_dir)
    pd = _plan_dir(args.project_dir)
    project = _read_project(pd)
    has_frontend_flag = project.get("has_frontend", False)
    _output({
        "has_frontend": has_frontend_flag,
        "has_frontend_changes": has_changes,
        "need_browser_test": has_frontend_flag or has_changes,
        "frontend_files": files,
    })


def _run_build_cmd(cmd, cwd, label):
    """运行构建命令并返回结果"""
    try:
        proc = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=120,
        )
        return {
            "label": label,
            "command": cmd,
            "success": proc.returncode == 0,
            "stdout": proc.stdout[-2000:] if proc.stdout else "",
            "stderr": proc.stderr[-2000:] if proc.stderr else "",
        }
    except subprocess.TimeoutExpired:
        return {
            "label": label,
            "command": cmd,
            "success": False,
            "stderr": "构建超时（120s）",
        }
    except FileNotFoundError:
        return {
            "label": label,
            "command": cmd,
            "success": False,
            "stderr": f"命令不存在: {cmd.split()[0]}",
        }


def cmd_validate_build(args):
    """验证项目构建 — Phase 4.5 集成验证"""
    pd = _plan_dir(args.project_dir)
    project = _read_project(pd)
    language = project.get("language", "") or _detect_language(args.project_dir)
    has_frontend = project.get("has_frontend", False)

    results = []

    # 后端编译验证
    if language == "go":
        results.append(_run_build_cmd("go build ./...", args.project_dir, "Go 编译"))
    elif language == "python":
        # 查找 Python 包目录
        pkg_dirs = []
        for item in os.listdir(args.project_dir):
            item_path = os.path.join(args.project_dir, item)
            if os.path.isdir(item_path) and os.path.exists(os.path.join(item_path, "__init__.py")):
                pkg_dirs.append(item)
        if pkg_dirs:
            for pkg in pkg_dirs:
                results.append(_run_build_cmd(
                    f"python3 -m compileall -q {pkg}", args.project_dir, f"Python 编译 ({pkg})"
                ))
        else:
            results.append(_run_build_cmd(
                "python3 -m compileall -q .", args.project_dir, "Python 编译"
            ))
    elif language in ("typescript", "javascript"):
        if os.path.exists(os.path.join(args.project_dir, "tsconfig.json")):
            results.append(_run_build_cmd("npx tsc --noEmit", args.project_dir, "TypeScript 类型检查"))

    # 前端构建验证
    if has_frontend:
        frontend_dirs = ["web", "frontend", "client"]
        found_frontend = False
        for subdir in frontend_dirs:
            sub_path = os.path.join(args.project_dir, subdir)
            if os.path.exists(os.path.join(sub_path, "package.json")):
                results.append(_run_build_cmd("npm run build", sub_path, f"前端构建 ({subdir}/)"))
                found_frontend = True
                break
        # 根目录就是前端项目
        if not found_frontend and os.path.exists(os.path.join(args.project_dir, "package.json")):
            results.append(_run_build_cmd("npm run build", args.project_dir, "前端构建 (root)"))

    if not results:
        _output({"success": True, "results": [], "message": "无需构建验证（未检测到构建目标）"})
        return

    success = all(r["success"] for r in results)
    _output({"success": success, "results": results})
    if not success:
        sys.exit(1)


def cmd_diagnose(args):
    """诊断项目状态 — 全面验证流程一致性"""
    pd = _plan_dir(args.project_dir)
    result = {
        "project_dir": args.project_dir,
        "status": "ok",
        "issues": [],
        "warnings": [],
        "suggestions": [],
    }

    # 检查项目语言识别
    detected_lang = _detect_language(args.project_dir)
    detected_fw = _detect_framework(args.project_dir, detected_lang)
    result["detected"] = {
        "language": detected_lang,
        "framework": detected_fw,
    }

    if not os.path.exists(pd):
        result["issues"].append(".plan/ 目录不存在，项目未初始化")
        result["status"] = "error"
        _output(result)
        return

    # 检查 project.yaml
    project_path = os.path.join(pd, "project.yaml")
    if not os.path.exists(project_path):
        result["issues"].append(".plan/project.yaml 不存在")
        result["status"] = "error"
        _output(result)
        return

    project = _read_project(pd)
    result["project"] = {
        "current_agent": project.get("current_agent", ""),
        "current_phase": project.get("current_phase", ""),
        "current_task": project.get("current_task", ""),
        "mode": project.get("mode", ""),
    }

    if not project.get("language") and detected_lang:
        result["suggestions"].append(f"建议设置语言为: {detected_lang}")

    # 1. trace/project.yaml 状态一致性
    last_event = _read_last_trace(pd)
    event = last_event.get("event", "")
    current_agent = project.get("current_agent", "")
    if event == "done" and current_agent != "done":
        result["issues"].append(
            f"状态不一致: trace 显示 done，但 project.yaml current_agent={current_agent}"
        )

    # 2. 按阶段检查预期 artifact
    artifacts_dir = os.path.join(pd, "artifacts")
    phase_order = ["triage", "requirements", "ui-design", "design", "coding", "review", "testing", "done"]
    current_phase = project.get("current_phase", "")
    if current_phase in phase_order:
        phase_idx = phase_order.index(current_phase)
        # review 阶段之后应有 review-report.md
        if phase_idx > phase_order.index("review"):
            if not os.path.exists(os.path.join(artifacts_dir, "review-report.md")):
                result["warnings"].append("当前阶段已过 review，但 review-report.md 不存在")
        # testing 阶段之后应有 test-report.md
        if phase_idx > phase_order.index("testing"):
            if not os.path.exists(os.path.join(artifacts_dir, "test-report.md")):
                result["warnings"].append("当前阶段已过 testing，但 test-report.md 不存在")

    if os.path.exists(artifacts_dir):
        result["artifacts"] = os.listdir(artifacts_dir)
    else:
        result["issues"].append(".plan/artifacts/ 目录不存在")

    # 3. completed_tasks 与 current_task 一致性
    completed_tasks = project.get("completed_tasks", [])
    if not isinstance(completed_tasks, list):
        completed_tasks = []
    current_task = project.get("current_task", "")
    result["completed_tasks"] = completed_tasks
    if current_task and current_agent in ("reviewer", "tester"):
        if current_task not in completed_tasks:
            result["warnings"].append(
                f"current_task={current_task} 未在 completed_tasks 中，可能导致 next 命令失败"
            )

    # 4. handoff 文件完整性
    handoff_dir = os.path.join(pd, "handoff")
    if os.path.exists(handoff_dir):
        handoffs = sorted([f for f in os.listdir(handoff_dir) if f.endswith(".md")])
        result["handoff_count"] = len(handoffs)
        # 检查最新 handoff 是否包含 current_task
        if handoffs and project.get("mode") == "full" and current_agent in ("developer", "reviewer", "tester"):
            latest_handoff = os.path.join(handoff_dir, handoffs[-1])
            with open(latest_handoff, encoding="utf-8") as f:
                hf_content = f.read()
            if "## 当前 Task" in hf_content:
                task_section = hf_content.split("## 当前 Task")[1].split("##")[0].strip()
                if not task_section:
                    result["warnings"].append(f"最新 handoff ({handoffs[-1]}) 的 '当前 Task' 为空")
    else:
        result["issues"].append(".plan/handoff/ 目录不存在")

    # 汇总状态
    if result["issues"]:
        result["status"] = "error"
    elif result["warnings"]:
        result["status"] = "warning"

    _output(result)


def cmd_check_conflicts(args):
    """检查并行 Task 的文件冲突（全路径匹配 + 目录级软冲突检测）"""
    pd = _plan_dir(args.project_dir)
    design_path = os.path.join(pd, "artifacts", "design.md")
    if not os.path.isfile(design_path):
        _output({"error": "design.md not found", "has_conflicts": False, "conflicts": [], "soft_conflicts": []})
        return

    with open(design_path, encoding="utf-8") as f:
        content = f.read()

    requested = [t.strip() for t in args.tasks.split(",") if t.strip()]

    # 解析每个 Task 的文件列表（YAML-first, 与 parse-tasks 一致）
    task_files = {}
    meta_pattern = re.compile(
        r'###\s+(Task[- ]?\d+)[：:]\s*.+?\n'
        r'<!-- task-meta\s*\n(.*?)\n-->',
        re.DOTALL
    )
    meta_matches = meta_pattern.findall(content)
    if meta_matches:
        for raw_id, yaml_str in meta_matches:
            tid = _normalize_task_id(raw_id)
            meta = _simple_yaml_load(yaml_str)
            files = meta.get("files", [])
            if isinstance(files, str):
                files = [f.strip() for f in files.split(",") if f.strip()]
            elif not isinstance(files, list):
                files = []
            task_files[tid] = [str(f) for f in files]
    else:
        # Regex fallback: 旧格式
        for tid_raw in requested:
            tid = _normalize_task_id(tid_raw)
            pattern = rf'(?:### )?{re.escape(tid)}[：:]\s*(.+?)(?=\n(?:### )?Task[- ]?\d+[：:]|\n## |\Z)'
            m = re.search(pattern, content, re.DOTALL)
            if m:
                section = m.group(0)
                file_match = re.search(
                    r'\*{0,2}(?:文件|files?)\*{0,2}\s*[：:]\s*(.+)',
                    section, re.IGNORECASE
                )
                if file_match:
                    files_text = file_match.group(1).strip()
                    backtick = re.findall(r'`([^`]+)`', files_text)
                    if backtick:
                        task_files[tid] = [f.strip() for f in backtick]
                    else:
                        task_files[tid] = [f.strip() for f in re.split(r'[,，]', files_text) if f.strip()]

    # 硬冲突检测：完全相同的文件路径
    conflicts = []
    req_ids = [_normalize_task_id(t) for t in requested]
    checked = set()
    for i, t1 in enumerate(req_ids):
        for t2 in req_ids[i + 1:]:
            pair = tuple(sorted([t1, t2]))
            if pair in checked:
                continue
            checked.add(pair)
            f1 = set(task_files.get(t1, []))
            f2 = set(task_files.get(t2, []))
            overlap = f1 & f2
            if overlap:
                conflicts.append({
                    "tasks": list(pair),
                    "files": sorted(overlap),
                })

    # 软冲突检测：目录级重叠
    soft_conflicts = []
    dir_to_tasks = {}
    for tid in req_ids:
        for f in task_files.get(tid, []):
            d = os.path.dirname(f) or "."
            dir_to_tasks.setdefault(d, set()).add(tid)
    for d, tids in dir_to_tasks.items():
        if len(tids) > 1:
            pair_key = tuple(sorted(tids))
            # 排除已经是硬冲突的
            if not any(tuple(sorted(c["tasks"])) == pair_key for c in conflicts):
                soft_conflicts.append({
                    "directory": d,
                    "tasks": sorted(tids),
                })

    _output({
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts,
        "soft_conflicts": soft_conflicts,
        "task_files": task_files,
    })


if __name__ == "__main__":
    main()
