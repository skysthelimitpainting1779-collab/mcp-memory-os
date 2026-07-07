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

    print(f"\n✅ UALL integrated into '{project_name}'")
    print("\nNext steps:")
    print("  python3 uall.py /status")
    print("  python3 uall.py /task <TASK-ID>")


if __name__ == "__main__":
    bootstrap()
