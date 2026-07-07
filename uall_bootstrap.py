#!/usr/bin/env python3
"""
uall_bootstrap.py — Lightweight bootstrap for an existing project.
Run from inside the project root: python uall_bootstrap.py

Creates the .agent/ skeleton, generates all IDE instruction files,
and configures Graphifyy. Does NOT require uall-template/ to exist.
"""
import importlib.util
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()


def bootstrap() -> None:
    print("UALL Bootstrap v3.0: Initializing Agentic Intelligence Layer")
    print("=" * 60)

    project_name = ROOT.name

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
    print(f"[OK] Directory structure created ({len(dirs)} dirs)")

    # 2. Copy tools from installer source if available
    installer_root = Path(__file__).parent
    template_tools = installer_root / "plugin" / "template" / ".agent" / "tools"
    if template_tools.exists():
        for tool in template_tools.glob("*.py"):
            dst = Path(".agent/tools") / tool.name
            if not dst.exists():
                shutil.copy2(tool, dst)
        print("[OK] Tools copied from template")
    else:
        print("[WARN] plugin/template not found — tools must be added manually")

    # 3. Core governance stub
    gov_path = Path(".agent/GOVERNANCE.md")
    if not gov_path.exists():
        gov_path.write_text(
            "# Governance & Safety Policy\n\n"
            "## Risk Tiers\n"
            "- Tier 1 (Auto-Approve): Read-only, comments, docs\n"
            "- Tier 2 (Consensus): Code changes, new files, config edits\n"
            "- Tier 3 (Human Review): Deleting files, modifying .agent/tools/, secrets\n",
            encoding="utf-8"
        )
        print("[OK] GOVERNANCE.md created")

    # 4. Auto-detect project type and write canonical Google design doc format
    design_path = Path(".agent/spec/design.md")
    project_name = ROOT.name
    from datetime import date
    stack_lines = []
    if Path("package.json").exists():
        stack_lines.append("- Runtime: Node.js / JavaScript")
    if Path("pyproject.toml").exists() or Path("requirements.txt").exists():
        stack_lines.append("- Runtime: Python")
    if Path("go.mod").exists():
        stack_lines.append("- Runtime: Go")
    if Path("Cargo.toml").exists():
        stack_lines.append("- Runtime: Rust")
    if not stack_lines:
        stack_lines.append("- Runtime: (fill in)")
    stack_block = "\n".join(stack_lines)

    design_path.write_text(
        f"# Design Doc: {project_name}\n\n"
        "| Field | Value |\n"
        "|-------|-------|\n"
        "| **Status** | DRAFT — ACTION REQUIRED: fill in all (fill in) sections |\n"
        f"| **Authors** | (fill in) |\n"
        f"| **Last Updated** | {date.today()} |\n\n"
        "---\n\n"
        "## Context & Scope\n"
        "<!-- Succinct objective background. What landscape is this being built in? "
        "What is actually being built? Assume some prior knowledge. -->\n"
        "(fill in)\n\n"
        "## Goals\n"
        "<!-- Bullet list of what the system MUST achieve. "
        "Focus on technical outcomes, not implementation steps. -->\n"
        "- (fill in)\n\n"
        "## Non-Goals\n"
        "<!-- Things that COULD reasonably be goals but are explicitly NOT. "
        "Example: 'ACID compliance', 'sub-10ms latency'. NOT negated goals like 'must not crash'. -->\n"
        "- (fill in)\n\n"
        "## The Actual Design\n\n"
        "### Overview\n"
        "<!-- High-level description of the proposed solution. -->\n"
        "(fill in)\n\n"
        "### System Context\n"
        "<!-- How does this system fit into the larger technical landscape? "
        "Add a diagram if helpful (ASCII or Mermaid). -->\n"
        "(fill in)\n\n"
        "### Stack & Key Components\n"
        f"{stack_block}\n"
        "- Framework: (fill in)\n"
        "- Database: (fill in)\n"
        "- Key libraries: (fill in)\n\n"
        "### APIs & Interfaces\n"
        "<!-- Sketch the key APIs. Don't copy-paste full schemas — focus on design-relevant parts. -->\n"
        "(fill in)\n\n"
        "### Data Storage\n"
        "<!-- How and in what form is data stored? Focus on design trade-offs. -->\n"
        "(fill in)\n\n"
        "## Alternatives Considered\n"
        "<!-- IMPORTANT: This is one of the most valuable sections. "
        "List alternative designs and explain WHY they were rejected. "
        "Show the trade-offs that led to the chosen design. -->\n"
        "| Alternative | Why Rejected |\n"
        "|-------------|--------------|\n"
        "| (fill in) | (fill in) |\n\n"
        "## Cross-Cutting Concerns\n"
        "<!-- Security, privacy, observability, scalability. Short sections each. -->\n"
        "- **Security:** (fill in)\n"
        "- **Privacy:** (fill in)\n"
        "- **Observability:** (fill in)\n"
        "- **Scalability:** (fill in)\n\n"
        "## Do Not Touch\n"
        "<!-- Files that must never be modified without explicit human approval. -->\n"
        "- `.agent/tools/` — UALL kernel, gate-protected\n"
        "- `.agent/GOVERNANCE.md` — requires human approval\n\n"
        "## Test & Verify\n"
        "```bash\n"
        "python uall.py /verify\n"
        "```\n\n"
        "## Open Questions\n"
        "<!-- Unresolved design questions. Remove when resolved or move to an Amendment. -->\n"
        "- (fill in)\n",
        encoding="utf-8"
    )
    print("[OK] design.md created (canonical Google design doc format — ACTION REQUIRED: fill in)")

    # 5. Git init if needed
    if not Path(".git").exists():
        subprocess.run(["git", "init"], capture_output=True)
        print("[OK] Git repository initialized")

    # 6. Update .gitignore with UALL-specific entries
    _update_gitignore(ROOT)

    # 7. Graphifyy: detect, install if missing, wire IDE integrations
    setup_graphify()

    # 8. Generate ALL IDE instruction files via master installer
    _call_generate_ide_files(ROOT)

    print(f"\n[OK] UALL integrated into '{project_name}'")
    print("\nNext steps:")
    print("  python uall.py /status")
    print("  Fill in: .agent/spec/design.md  <-- ACTION REQUIRED")
    print("  python uall.py /task <TASK-ID>")


def _update_gitignore(root: Path) -> None:
    """Add UALL-specific entries to .gitignore without clobbering existing ones."""
    gi = root / ".gitignore"
    existing = gi.read_text(encoding="utf-8") if gi.exists() else ""
    entries = [
        ("# UALL — ephemeral memory (never commit raw episodic logs)", ""),
        (".agent/memory/episodic/", ".agent/memory/episodic/"),
        (".agent/memory/.index/", ".agent/memory/.index/"),
        (".agent/.verified", ".agent/.verified"),
        ("# Graphifyy build artifacts", ""),
        ("graphify-out/", "graphify-out/"),
        ("*.graphify.tmp", "*.graphify.tmp"),
    ]
    to_add = []
    for comment, pattern in entries:
        check = pattern if pattern else comment
        if check and check not in existing:
            to_add.append(comment if not pattern else pattern)
    if to_add:
        with gi.open("a", encoding="utf-8") as f:
            f.write("\n" + "\n".join(to_add) + "\n")
        print("[OK] .gitignore updated with UALL entries")


def _call_generate_ide_files(root: Path) -> None:
    """Import _generate_ide_files from master installer and run it."""
    installer_py = Path(__file__).parent / "uall_master_installer.py"
    if not installer_py.exists():
        print("[WARN] uall_master_installer.py not found — IDE files not generated")
        return
    try:
        spec = importlib.util.spec_from_file_location("uall_installer", installer_py)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        mod._generate_ide_files(root)
    except Exception as e:
        print(f"[WARN] IDE file generation failed: {e}")


def setup_graphify() -> None:
    """Install graphify only if not present; prefer uv over pip. Then wire IDE integrations."""
    print("Checking Graphifyy integration...")

    # 1. Check if already installed
    try:
        from importlib.metadata import version as _pkg_ver
        ver = _pkg_ver("graphifyy")
        print(f"   [OK] graphifyy {ver} already installed — skipping install")
    except Exception:
        print("   [..] graphifyy not found — installing...")
        import shutil as _shutil
        if _shutil.which("uv"):
            cmd = ["uv", "pip", "install", "graphifyy"]
            installer = "uv"
        else:
            cmd = [sys.executable, "-m", "pip", "install", "graphifyy"]
            installer = "pip"
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"   [OK] graphifyy installed via {installer}")
        else:
            print(f"   [WARN] graphifyy install failed: {result.stderr[:200]}")
            return

    # 2. Run graphify install (updates skills/references)
    try:
        subprocess.run(
            [sys.executable, "-m", "graphify", "install"],
            capture_output=True, text=True
        )
        print("   [OK] graphify skills updated")
    except Exception as e:
        print(f"   [WARN] graphify install failed: {e}")

    # 3. Wire graphify IDE integrations BEFORE _generate_ide_files appends UALL content
    for subcmd, label in [
        (["hook", "install"], "git hooks"),
        (["cursor", "install"], "Cursor"),
        (["claude", "install"], "Claude"),
        (["antigravity", "install"], "Antigravity"),
    ]:
        try:
            subprocess.run(
                [sys.executable, "-m", "graphify"] + subcmd,
                capture_output=True, text=True
            )
        except Exception:
            pass
    print("   [OK] Graphifyy IDE integrations configured")


if __name__ == "__main__":
    bootstrap()
