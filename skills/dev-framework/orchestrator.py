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

    project = {
        "name": os.path.basename(os.path.abspath(args.project_dir)),
        "language": language,
        "framework": framework,
        "has_frontend": has_frontend,
        "mode": "full",
        "current_phase": "triage",
        "current_agent": "triage",
        "current_task": "",
        "rollback_count": 0,
        "history": [],
    }

    _write_project(pd, project)
    _write_trace(pd, "system", "start", "",
                 f"dev-framework 初始化，语言: {language}，框架: {framework}，前端: {has_frontend}")

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

    _output({"status": "initialized", "plan_dir": pd, "language": language, "framework": framework})


def _detect_language(project_dir):
    """智能检测项目语言"""
    if os.path.exists(os.path.join(project_dir, "go.mod")):
        return "go"
    if os.path.exists(os.path.join(project_dir, "pyproject.toml")) or os.path.exists(os.path.join(project_dir, "requirements.txt")) or os.path.exists(os.path.join(project_dir, "setup.py")):
        return "python"
    if os.path.exists(os.path.join(project_dir, "package.json")):
        with open(os.path.join(project_dir, "package.json"), encoding="utf-8") as f:
            content = f.read()
        if "typescript" in content or "tsx" in content:
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
    if event == "done":
        result["resume_action"] = "completed"
        # 状态一致性修复：trace 显示 done 时覆写 current_agent
        result["current_agent"] = "done"
    elif event == "blocked":
        result["resume_action"] = "await_approval"
    elif event == "handoff":
        result["resume_action"] = f"dispatch_{project.get('current_agent', '')}"
    else:
        result["resume_action"] = f"dispatch_{project.get('current_agent', '')}"

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

    # full 模式下 developer/reviewer/tester 的 handoff 必须提供 --current-task
    mode = project.get("mode", "full")
    if mode == "full" and args.from_agent in ("developer", "reviewer", "tester"):
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
                _output({
                    "next_agent": "tester",
                    "reason": f"批量审查通过（Task 1-{completed_through}），所有 {total} 个 Task 完成，进入整体测试",
                })
            else:
                next_task = f"Task {completed_through + 1}"
                _output({
                    "next_agent": "developer",
                    "next_task": next_task,
                    "reason": f"批量审查通过（至 Task {completed_through}），进入 {next_task}",
                })
            return

        if total is None:
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
                    _output({
                        "next_agent": "developer",
                        "next_task": next_task,
                        "reason": f"{current_task} 审查通过，进入 {next_task}",
                    })
                else:
                    _output({
                        "next_agent": "tester",
                        "reason": f"所有 {total} 个 Task 审查通过，进入整体测试",
                    })
            else:
                _output({"next_agent": "tester", "reason": "无法解析 Task 编号，进入测试"})
        else:
            _output({"next_agent": "tester", "reason": "无 Task List，直接进入测试"})
        return

    if target == "_pm_next":
        # PM 完成后：有前端 → ui-designer，无前端 → architect
        pd = _plan_dir(args.project_dir)
        project = _read_project(pd)
        has_frontend = project.get("has_frontend", False)
        if has_frontend:
            _output({
                "next_agent": "ui-designer",
                "reason": "PRD 完成，项目包含前端，进入 UI 设计",
            })
        else:
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
        _output({
            "next_agent": rollback_to,
            "reason": f"Architect 回退到 {rollback_to}",
        })
        return

    if target == "_await_approval":
        _output({
            "next_agent": "developer",
            "blocked": True,
            "reason": "🔒 等待人工审批",
        })
        return

    if target == "_from_route":
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

    # 支持多种 Task 标题格式：
    # - ### Task 1: ...
    # - ### Task 1：... (中文冒号)
    # - Task 1: ... (没有 ###)
    task_pattern = re.compile(r'(?:### )?(Task \d+)[：:]\s*(.+?)(?=\n(?:### )?(?:Task \d+[：:]|## |$))', re.DOTALL)

    for match in task_pattern.finditer(content):
        task_id = match.group(1)
        task_name = match.group(2).strip()

        # 移除任务名称中多余的换行
        task_name = re.sub(r'\s+', ' ', task_name)

        task = {
            "id": task_id,
            "name": task_name,
            "files": [],
            "deps": []
        }

        # 提取文件列表 - 支持多种格式：
        # - 文件: internal/...
        # - 文件: internal/...
        # - - 文件: internal/...
        section_content = match.group(0)

        # 寻找 "文件" 或 "依赖" 段落
        for line in section_content.split('\n'):
            line = line.strip()

            # 匹配文件行：- `file/path` 或 - file/path
            if re.match(r'^-+\s*`?[^-`]+`?\s*$', line) and not any(kw in line.lower() for kw in ['依赖', 'depend', 'task']):
                file_path = line.lstrip('- ').strip().strip('`')
                if file_path and not file_path.lower() in ['无', 'none']:
                    task["files"].append(file_path)

        # 提取依赖：支持中文"依赖"和英文"deps"
        dep_match = re.search(r'(?:依赖|Depends|deps)\s*[：:]\s*(.+?)(?:\n- |\n## |$)', section_content, re.DOTALL | re.IGNORECASE)
        if dep_match:
            dep_text = dep_match.group(1).strip()
            if dep_text not in ["无", "none", ""]:
                # 支持逗号、空格分隔
                for sep in [',', '，', ' ']:
                    deps = [d.strip() for d in dep_text.split(sep) if d.strip()]
                    if len(deps) > 1:
                        task["deps"] = deps
                        break
                if not task["deps"]:
                    task["deps"] = [dep_text]

        tasks.append(task)

    # 如果没有找到任务，尝试更宽松的格式
    if not tasks:
        # 尝试找编号列表
        for i, line in enumerate(content.split('\n'), 1):
            m = re.match(r'^\s*(\d+)\.\s*(.+)$', line)
            if m:
                tasks.append({
                    "id": f"Task {m.group(1)}",
                    "name": m.group(2).strip(),
                    "files": [],
                    "deps": []
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
            # 依赖为空或全部已解决 → 可加入当前批次
            if not deps or all(d in resolved for d in deps):
                group.append(tasks[idx]["id"])
        if not group:
            # 防止死循环（循环依赖）
            group = [tasks[remaining[0]]["id"]]
        parallel_groups.append(group)
        resolved.update(group)
        remaining = [i for i in remaining if tasks[i]["id"] not in resolved]

    result = {"tasks": tasks, "total": len(tasks), "parallel_groups": parallel_groups}

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
    _write_trace(pd, "system", "task-done", task_id, f"{task_id} 标记完成")
    _output({"status": "ok", "task": task_id, "total_completed": len(completed)})


def cmd_check_conflicts(args):
    """分析并行 Task 批次中的文件冲突"""
    design_path = os.path.join(args.project_dir, ".plan", "artifacts", "design.md")
    if not os.path.exists(design_path):
        _output({"error": "design.md not found"})
        sys.exit(1)

    with open(design_path, encoding="utf-8") as f:
        content = f.read()

    # 解析每个 Task 的文件列表
    task_files = {}
    task_pattern = re.compile(
        r'(?:### )?(Task \d+)[：:]\s*(.+?)(?=\n(?:### )?(?:Task \d+[：:]|## |$))',
        re.DOTALL
    )
    for match in task_pattern.finditer(content):
        task_id = match.group(1)
        section = match.group(0)
        file_match = re.search(r'(?:文件|files?)\s*[：:]\s*(.+?)(?:\n- |\n##|\n###|$)',
                               section, re.IGNORECASE)
        if file_match:
            raw = file_match.group(1).strip().strip('`')
            files = [f.strip().strip('`') for f in re.split(r'[,，]', raw) if f.strip()]
            task_files[task_id] = files

    # 解析要检查的 Task IDs
    check_tasks = [t.strip() for t in args.tasks.split(",") if t.strip()]

    # 检测冲突
    file_to_tasks = {}
    for tid in check_tasks:
        for f in task_files.get(tid, []):
            norm = f.split("/")[-1]  # 用文件名做近似匹配
            file_to_tasks.setdefault(norm, []).append(tid)

    conflicts = {f: tasks for f, tasks in file_to_tasks.items() if len(tasks) > 1}

    result = {
        "tasks_checked": check_tasks,
        "conflicts": conflicts,
        "has_conflicts": bool(conflicts),
    }
    if conflicts:
        result["recommendation"] = "存在文件冲突，建议将冲突 Task 改为串行执行，或合并到同一 Agent"
    _output(result)


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


if __name__ == "__main__":
    main()
