#!/usr/bin/env python3
"""
UALL v2.0 — Universal Agentic Learning Layer
Central command router with enhanced error handling and consistency checks.
Drop this file and .agent/ into any project root and run:

  python3 uall.py /status
  python3 uall.py /recall "describe task here"
  python3 uall.py /task TASK-123
"""
import sys
import os
import subprocess
from pathlib import Path

# ─── Resolve project root (where this file lives) ────────────────────────────
ROOT = Path(__file__).resolve().parent
AGENT_DIR = ROOT / ".agent"
TOOLS_DIR = AGENT_DIR / "tools"


def run_script(script_name: str, *args) -> str:
    """Run a .agent/tools script in the project root context with error handling."""
    script_path = TOOLS_DIR / script_name
    if not script_path.exists():
        return f"❌ Tool not found: {script_path}"
    
    cmd = [sys.executable, str(script_path)] + list(args)
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=300)
        output = res.stdout.strip()
        if res.returncode != 0:
            err = res.stderr.strip()
            return f"{output}\n{err}".strip() if err else output
        return output
    except subprocess.TimeoutExpired:
        return f"❌ Tool timeout: {script_name} exceeded 5 minutes"
    except Exception as e:
        return f"❌ Tool execution error: {str(e)}"


def handle_command(cmd_input: str) -> None:
    """Route commands to appropriate tools with consistency checks."""
    parts = cmd_input.strip().split(" ", 1)
    cmd = parts[0].lower()
    args = parts[1].strip() if len(parts) > 1 else ""

    # Commands that map directly to tool scripts
    TOOL_MAP = {
        "/recall":     ("recall.py",        ["--task", args] if args else ["--task", "general"]),
        "/verify":     ("verify.py",         []),
        "/dream":      ("auto_dream.py",     []),
        "/graduate":   ("graduate.py",       []),
        "/heal":       ("self_heal.py",      []),
        "/enhance":    ("enhance.py",        []),
        "/audit":      ("audit.py",          []),
        "/sync":       ("graph_sync.py",     []),
        "/report":     ("report.py",         []),
        "/export":     ("export_insights.py",[]),
        "/task":       ("task_bridge.py",    [args, "linear"] if args else []),
        "/checkpoint": ("recover.py",        ["checkpoint", args or "Manual checkpoint"]),
        "/recover":    ("recover.py",        ["recover"] + (["--version", args] if args else [])),
        "/history":    ("recover.py",        ["history"]),
        "/index":      ("index_memory.py",   []),
        "/sign":       ("security_v2.py",    ["--sign"]),
        "/integrity":  ("security_v2.py",    ["--verify"]),
        "/graphify":   ("graphify_bridge.py", []),
        "/standard":   ("agent_standard.py",  []),
        "/proactive":  ("proactive.py",       []),
    }

    # /checkpoint requires prior /verify
    if cmd == "/checkpoint":
        verified_flag = AGENT_DIR / ".verified"
        if not verified_flag.exists():
            print("❌ ACTION BLOCKED: Run `/verify` first to unlock /checkpoint.")
            return
        print(run_script("recover.py", "checkpoint", args or "Manual checkpoint"))
        if verified_flag.exists():
            verified_flag.unlink()
        return

    if cmd == "/status":
        _print_status()
        return

    if cmd == "/help":
        _print_help()
        return

    if cmd in TOOL_MAP:
        script, s_args = TOOL_MAP[cmd]
        # Filter out empty string args
        clean_args = [a for a in s_args if a != ""]
        print(run_script(script, *clean_args))
    else:
        print(f"Unknown command: '{cmd}'. Run `python3 uall.py /help` for commands.")


def _print_status() -> None:
    """Print brain health and system status."""
    episodic_dir = AGENT_DIR / "memory" / "episodic"
    pending_dir = AGENT_DIR / "skills" / "pending"
    candidate_dir = AGENT_DIR / "memory" / "candidate_lessons"
    graduated_jsonl = AGENT_DIR / "memory" / "graduated" / "LESSONS.jsonl"
    db_path = AGENT_DIR / "memory" / ".index" / "memory.db"

    log_count = len(list(episodic_dir.glob("*.jsonl"))) if episodic_dir.exists() else 0
    pending_count = len(list(pending_dir.glob("*.md"))) if pending_dir.exists() else 0
    candidate_count = len(list(candidate_dir.glob("*.md"))) if candidate_dir.exists() else 0

    graduated_count = 0
    if graduated_jsonl.exists():
        with open(graduated_jsonl) as f:
            graduated_count = sum(1 for line in f if line.strip())

    active_task = "none"
    active_task_file = AGENT_DIR / ".active_task"
    if active_task_file.exists():
        active_task = active_task_file.read_text().strip()

    index_status = "✅ built" if db_path.exists() else "⚠️  missing (run /index)"
    verified = "✅ unlocked" if (AGENT_DIR / ".verified").exists() else "🔒 locked"

    print("=" * 60)
    print("📊 UALL v2.0 Status")
    print("=" * 60)
    print(f"  Project Root  : {ROOT}")
    print(f"  Active Task   : {active_task}")
    print(f"  Episodic Logs : {log_count} files")
    print(f"  Candidates    : {candidate_count} pending review")
    print(f"  Graduated     : {graduated_count} lessons")
    print(f"  Pending Skills: {pending_count}")
    print(f"  Memory Index  : {index_status}")
    print(f"  Checkpoint    : {verified}")
    print("=" * 60)


def _print_help() -> None:
    """Print command reference."""
    help_text = """
UALL v2.0 Commands
─────────────────────────────────────────────────────────────
/status              Brain health & counters
/recall <task>       Hybrid memory search (FTS5 + graph + hints)
/task <id>           Initialize task context from Linear/GitHub
/verify              Run semgrep + ruff + pytest; unlocks /checkpoint
/checkpoint <msg>    Git-commit .agent/ state (requires /verify)
/recover [hash]      Restore .agent/ to HEAD or a specific commit
/history             Show recent UALL checkpoints
/dream               Correlation mining → candidate lessons
/graduate            Promote approved candidates to playbook
/heal                Analyze failures → self-healing hints
/enhance             Scaffold new skills from episodic patterns
/audit               Adversarial review of pending skills
/sync                Rebuild temporal knowledge graph (v2.0)
/graphify            Deep codebase mapping via tree-sitter (Graphifyy)
/standard            Sync project state to AGENTS.md standard
/proactive           Autonomous task seeking and execution
/index               Rebuild FTS5 memory search index (v2.0)
/report              Generate intelligence report for active task
/export              Sanitize & export insights for cross-repo sharing
/sign                Lock security tools (human-run once)
/integrity           Verify kernel files haven't been tampered with
/help                Show this message
─────────────────────────────────────────────────────────────
"""
    print(help_text)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        _print_help()
    else:
        handle_command(" ".join(sys.argv[1:]))
