#!/usr/bin/env python3
"""
uall_bootstrap.py — Lightweight bootstrap for an existing project.
Run from inside the project root: python3 uall_bootstrap.py

Creates the .agent/ skeleton and copies the uall.py interface.
Does NOT require uall-template/ to exist — generates minimal stubs.
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()


def bootstrap() -> None:
    print("🚀 UALL Bootstrap: Initializing Agentic Intelligence Layer")
    print("=" * 56)

    # 1. Directory structure
    dirs = [
        ".agent/spec/tasks",
        ".agent/memory/episodic/archive",
        ".agent/memory/candidate_lessons",
        ".agent/memory/graduated",
        ".agent/memory/semantic",
        ".agent/memory/personal",
        ".agent/memory/graph",
        ".agent/memory/.index",
        ".agent/skills/core",
        ".agent/skills/domain",
        ".agent/skills/pending",
        ".agent/skills/audit_reports",
        ".agent/protocols",
        ".agent/tools",
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
    print(f"✅ Directory structure created ({len(dirs)} dirs)")

    # 2. Copy tools from installer source if available
    installer_root = Path(__file__).parent
    template_tools = installer_root / "plugin" / "template" / ".agent" / "tools"
    if template_tools.exists():
        for tool in template_tools.glob("*.py"):
            dst = Path(".agent/tools") / tool.name
            if not dst.exists():
                shutil.copy2(tool, dst)
        print("✅ Tools copied from template")
    else:
        print("⚠️  template not found in plugin/template — tools must be added manually")

    # 3. Core governance stub
    gov_path = Path(".agent/GOVERNANCE.md")
    if not gov_path.exists():
        gov_path.write_text(
            "# Governance & Safety Policy\n\n"
            "## Risk Tiers\n- Tier 1: Auto-Approve\n- Tier 2: Consensus\n- Tier 3: Human Review\n"
        )

    # 4. Auto-detect project type
    design_path = Path(".agent/spec/design.md")
    project_name = ROOT.name
    lines = [f"# Project Design: {project_name}\n\n## Auto-Discovery Results\n"]
    if Path("package.json").exists():
        lines.append("- Type: Node.js / JavaScript\n")
    if Path("pyproject.toml").exists() or Path("requirements.txt").exists():
        lines.append("- Type: Python\n")
    if Path("go.mod").exists():
        lines.append("- Type: Go\n")
    if Path("Cargo.toml").exists():
        lines.append("- Type: Rust\n")
    lines.append(f"- Root files: {', '.join(p.name for p in ROOT.iterdir() if p.is_file())[:200]}\n")
    design_path.write_text("".join(lines))
    print("✅ Initial design.md created")

    # 5. Git
    if not Path(".git").exists():
        subprocess.run(["git", "init"], capture_output=True)
        print("✅ Git repository initialized")

    # 6. Graphifyy integration setup
    setup_graphify()

    print(f"\n✅ UALL integrated into '{project_name}'")
    print("\nNext steps:")
    print("  python uall.py /status")
    print("  python uall.py /task <TASK-ID>")


def setup_graphify() -> None:
    print("🕸️ Checking Graphifyy integration...")
    import subprocess
    import sys

    # 1. Install/upgrade graphifyy package if needed
    try:
        import graphify
        print("✅ Graphifyy Python package is already installed.")
    except ImportError:
        print("📥 Graphifyy not found. Installing via pip...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "graphifyy"], capture_output=True)
            print("✅ Graphifyy Python package installed successfully.")
        except Exception as e:
            print(f"⚠️ Failed to install graphifyy package: {e}")
            return

    # 2. Run graphify install to update skills
    try:
        print("🔧 Running graphify install...")
        subprocess.run([sys.executable, "-m", "graphify", "install"], capture_output=True)
        print("✅ Graphifyy skills and references updated.")
    except Exception as e:
        print(f"⚠️ Failed to run graphify install: {e}")

    # 3. Setup hooks and IDE rules
    try:
        print("🔗 Installing Git hooks...")
        subprocess.run([sys.executable, "-m", "graphify", "hook", "install"], capture_output=True)
        print("💻 Registering Cursor rules...")
        subprocess.run([sys.executable, "-m", "graphify", "cursor", "install"], capture_output=True)
        print("🤖 Registering Claude Code configs...")
        subprocess.run([sys.executable, "-m", "graphify", "claude", "install"], capture_output=True)
        print("🎯 Registering Google Antigravity configs...")
        subprocess.run([sys.executable, "-m", "graphify", "antigravity", "install"], capture_output=True)
        print("✅ Graphifyy Git hooks and IDE rules configured successfully.")
    except Exception as e:
        print(f"⚠️ Failed to configure hooks/IDE rules: {e}")


if __name__ == "__main__":
    bootstrap()

