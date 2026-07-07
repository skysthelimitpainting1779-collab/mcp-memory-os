#!/usr/bin/env python3
"""
uall_master_installer.py — UALL Master Installer v2.0
Deploys the framework to a target project directory.
Does NOT run chmod 555 on tools (that blocked re-runs in v1).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).parent / "plugin" / "template"


def post_deploy_patch(target_dir: Path) -> None:
    """
    Rewrite IDE instruction files (.cursorrules, .clinerules, CLAUDE.md,
    AGENTS.md) so they reference the *actual* target project path and
    project name rather than the template's hardcoded mcp-memory-os values.
    """
    abs_path = str(target_dir.resolve())
    project_name = target_dir.resolve().name

    # ── .cursorrules ────────────────────────────────────────────────────────
    cursorrules = target_dir / ".cursorrules"
    cursorrules.write_text(
        f"# Cursor Rules for UALL & {project_name}\n\n"
        f"- **SOPs & Profile:** At startup, read `.agent/AGENTS.md` to load active profile guidelines and commands.\n"
        f"- **Memory Retrieval:** Always run `python uall.py /recall \"<task_keywords>\"` at the start of a session or task to retrieve memory context.\n"
        f"- **Workspace Specs:** Refer to `.agent/spec/design.md` for codebase design and `.agent/spec/tasks/` for active ticket instructions.\n"
        f"- **Local Playbook:** Consult `.agent/PLAYBOOK.md` to check graduated coding lessons and avoid repeating past errors.\n"
        f"- **Safety Gate:** Before writing files, verify the action via `python .agent/tools/gate.py write <file_path>` and respect boundaries in `.agent/GOVERNANCE.md`.\n"
        f"- **Traced Execution:** Execute all terminal commands wrapped in `python .agent/tools/tracer.py \"<command>\"` to capture episodic metrics.\n"
        f"- **Git Checkpoints:** Run `python uall.py /checkpoint \"<message>\"` only after `/verify` pass.\n",
        encoding="utf-8",
    )

    # ── .clinerules ─────────────────────────────────────────────────────────
    clinerules = target_dir / ".clinerules"
    clinerules.write_text(
        f"# Roo Code / Cline Rules for UALL & {project_name}\n\n"
        "<system_instructions>\n"
        f"You are an agent operating within a UALL-enabled repository: {project_name}.\n\n"
        "1. **Active SOP Rules**: At startup, read `.agent/AGENTS.md` to load active profile guidelines and commands.\n"
        "2. **Memory Retrieval**: Your first action for any task MUST be to run `python uall.py /recall \"<task_keywords>\"` to fetch grounded context.\n"
        "3. **Workspace Specs**: Reference `.agent/spec/design.md` for design and `.agent/spec/tasks/` for active ticket instructions.\n"
        "4. **Local Playbook**: Consult `.agent/PLAYBOOK.md` to check graduated coding lessons and avoid repeating past errors.\n"
        "5. **Safety Gate**: Before writing files, verify the action via `python .agent/tools/gate.py write <file_path>` and respect boundaries in `.agent/GOVERNANCE.md`.\n"
        "6. **Command Tracing**: Execute all terminal commands wrapped in `python .agent/tools/tracer.py \"<command>\"` to capture episodic metrics.\n"
        "7. **Git Checkpoints**: Persist milestones with `python uall.py /checkpoint \"<message>\"` (only after `/verify` pass).\n"
        "</system_instructions>\n",
        encoding="utf-8",
    )

    # ── .agent/AGENTS.md — replace {PROJECT_NAME} placeholder ──────────────
    agents_md = target_dir / ".agent" / "AGENTS.md"
    if agents_md.exists():
        content = agents_md.read_text(encoding="utf-8")
        content = content.replace("{PROJECT_NAME}", project_name)
        agents_md.write_text(content, encoding="utf-8")

    print(f"   [OK] IDE instruction files patched for '{project_name}' ({abs_path})")


def deploy(target_dir: Path) -> None:
    print(f"🚀 UALL MASTER INSTALLER: Deploying to '{target_dir}'...")
    target_dir.mkdir(parents=True, exist_ok=True)

    if not SOURCE_DIR.exists():
        print(f"❌ uall-template not found at {SOURCE_DIR}")
        print("   Run this from the UALL development root.")
        sys.exit(1)

    # Deploy framework
    items = [".agent", "uall.py", ".cursorrules", ".clinerules", "README.md"]
    for item in items:
        src = SOURCE_DIR / item
        dst = target_dir / item
        if not src.exists():
            continue
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        print(f"  [+] {item}")

    print("✅ Framework core deployed.")

    # Patch IDE rules files with correct project path/name
    post_deploy_patch(target_dir)

    # Git init if needed
    if not (target_dir / ".git").exists():
        print("🐙 Initializing Git...")
        subprocess.run(["git", "init"], cwd=target_dir, capture_output=True)

    # Graphifyy Git hooks and IDE rules setup
    print("🕸️  Configuring Graphifyy integration...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "graphifyy"], cwd=target_dir, capture_output=True)
        subprocess.run([sys.executable, "-m", "graphify", "install"], cwd=target_dir, capture_output=True)
        subprocess.run([sys.executable, "-m", "graphify", "hook", "install"], cwd=target_dir, capture_output=True)
        subprocess.run([sys.executable, "-m", "graphify", "cursor", "install"], cwd=target_dir, capture_output=True)
        subprocess.run([sys.executable, "-m", "graphify", "claude", "install"], cwd=target_dir, capture_output=True)
        subprocess.run([sys.executable, "-m", "graphify", "antigravity", "install"], cwd=target_dir, capture_output=True)
        print("   ✅ Hooks, Cursor, Claude, and Antigravity registered.")
    except Exception as e:
        print(f"   ⚠️ Graphifyy configuration warning: {e}")

    # Initial domain scan
    print("🔍 Initial domain scan...")
    subprocess.run(
        [sys.executable, str(target_dir / ".agent" / "tools" / "graph_sync.py")],
        cwd=target_dir, capture_output=True
    )

    # Initial memory index
    print("🧠 Building search index...")
    subprocess.run(
        [sys.executable, str(target_dir / ".agent" / "tools" / "index_memory.py")],
        cwd=target_dir, capture_output=True
    )

    # NOTE: We do NOT chmod 555 tools — that breaks re-runs and updates.
    # Kernel integrity is enforced via security_v2.py --sign instead.

    print("\n🏁 UALL DEPLOYMENT COMPLETE.")
    print("─" * 40)
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  python3 uall.py /status")
    print("  python3 uall.py /task <TASK-ID>")
    print("  python3 .agent/tools/security_v2.py --sign  # lock kernel hashes")
    print("─" * 40)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    deploy(target)

