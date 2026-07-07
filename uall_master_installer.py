#!/usr/bin/env python3
"""
uall_master_installer.py — UALL Master Installer v3.0
Deploys the framework to a target project directory.

v3.0 changes:
  - Single source of truth: one function generates ALL IDE instruction files
  - Covers 15 IDEs: Cursor, Claude Code, Cline, Devin, Windsurf, Copilot,
    Copilot-granular, VS Code, Aider, OpenHands, Gemini CLI, Gemini Code Assist,
    Antigravity, Eve (if detected), CLI/headless
  - Smart graphify detection: checks installed version before running pip/uv
  - Correct install order: graphify IDE installs FIRST, UALL patch SECOND
    (so we append to graphify's content, not overwrite it)
  - Creates PLAYBOOK.md and proper design.md template stubs
  - Does NOT run chmod 555 on tools (that broke re-runs in v1)
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).parent / "plugin" / "template"

# ─────────────────────────────────────────────────────────────────────────────
# UALL startup block — the single source of truth for what every IDE is told
# ─────────────────────────────────────────────────────────────────────────────
UALL_STARTUP_STEPS = """\
UALL STARTUP SEQUENCE — run these steps before writing ANY code:
1. python uall.py /recall "<describe your task in 3-5 words>"
2. Read: .agent/spec/design.md  (architecture & stack constraints)
3. Read active task: .agent/spec/tasks/<task-id>.json  (run /task <id> to set)
4. Check: .agent/PLAYBOOK.md  (graduated lessons for THIS codebase)
DURING WORK:
- Wrap every shell command:  python .agent/tools/tracer.py "<cmd>"
- Before writing .agent/ files: python .agent/tools/gate.py write <path>
- Respect: .agent/GOVERNANCE.md  (risk tiers, restricted files)
BEFORE COMMITTING:
- python uall.py /verify  (lint + security + tests must pass)
- python uall.py /checkpoint "<message>"  (only after green /verify)
"""

UALL_RULES_BRIEF = """\
- Run `python uall.py /recall "<task>"` before starting any task
- Read `.agent/spec/design.md` and the active `.agent/spec/tasks/*.json`
- Check `.agent/PLAYBOOK.md` for codebase-specific lessons
- Wrap shell commands: `python .agent/tools/tracer.py "<cmd>"`
- Gate writes to restricted files: `python .agent/tools/gate.py write <path>`
- Checkpoint only after `/verify` passes: `python uall.py /checkpoint "<msg>"`
"""


def _ensure_graphify(target_dir: Path) -> bool:
    """Install graphify only if not already present. Prefers uv over pip."""
    try:
        from importlib.metadata import version as pkg_version
        ver = pkg_version("graphifyy")
        print(f"   [OK] graphifyy {ver} already installed — skipping install")
        return True
    except Exception:
        pass

    print("   [..] graphifyy not found — installing...")
    if shutil.which("uv"):
        cmd = ["uv", "pip", "install", "graphifyy"]
        installer = "uv"
    else:
        cmd = [sys.executable, "-m", "pip", "install", "graphifyy"]
        installer = "pip"

    result = subprocess.run(cmd, capture_output=True, text=True, cwd=target_dir)
    if result.returncode == 0:
        print(f"   [OK] graphifyy installed via {installer}")
        return True
    print(f"   [WARN] graphifyy install failed via {installer}: {result.stderr[:200]}")
    return False


def _run_graphify_ide_installs(target_dir: Path) -> None:
    """Run graphify IDE integrations FIRST so our patch can append on top."""
    try:
        from importlib.metadata import version as pkg_version
        installed = pkg_version("graphifyy")
        # Check if skill update needed (graphify install updates skills)
        result = subprocess.run(
            [sys.executable, "-m", "graphify", "install"],
            capture_output=True, text=True, cwd=target_dir
        )
        print(f"   [OK] graphify install (skills updated)")
    except Exception:
        pass

    for subcmd, label in [
        (["hook", "install"], "git hooks"),
        (["cursor", "install"], "Cursor rules"),
        (["claude", "install"], "Claude/CLAUDE.md"),
        (["antigravity", "install"], "Antigravity rules"),
    ]:
        try:
            subprocess.run(
                [sys.executable, "-m", "graphify"] + subcmd,
                capture_output=True, text=True, cwd=target_dir
            )
            print(f"   [OK] graphify {' '.join(subcmd)} ({label})")
        except Exception as e:
            print(f"   [WARN] graphify {' '.join(subcmd)} failed: {e}")


def _generate_ide_files(target_dir: Path) -> None:
    """
    Single source of truth: generate/patch ALL IDE instruction files.
    Must be called AFTER graphify IDE installs so we append, not overwrite.
    """
    p = target_dir.resolve()
    project_name = p.name

    def write(rel: str, content: str, mode: str = "w") -> None:
        """Write or append to an IDE instruction file."""
        f = target_dir / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        if mode == "a" and f.exists():
            existing = f.read_text(encoding="utf-8")
            if "UALL STARTUP" in existing or "uall.py /recall" in existing:
                return  # Already patched — don't duplicate
            f.write_text(existing.rstrip() + "\n\n" + content, encoding="utf-8")
        else:
            f.write_text(content, encoding="utf-8")

    def write_json(rel: str, data: dict) -> None:
        """Merge UALL keys into an existing JSON file or create it."""
        f = target_dir / rel
        f.parent.mkdir(parents=True, exist_ok=True)
        existing = {}
        if f.exists():
            try:
                existing = json.loads(f.read_text(encoding="utf-8"))
            except Exception:
                pass
        existing.update(data)
        f.write_text(json.dumps(existing, indent=2), encoding="utf-8")

    # ── 1. Cursor ─────────────────────────────────────────────────────────────
    write(".cursorrules",
        f"# Cursor Rules — {project_name} (UALL v3)\n\n"
        f"{UALL_STARTUP_STEPS}\n"
        "# Graphify graph queries\n"
        "- For architecture questions: `graphify query \"<question>\"`\n"
        "- For call paths: `graphify path \"<A>\" \"<B>\"`\n"
        "- After editing code: `graphify update .`\n",
        mode="w"
    )

    # ── 2. Claude Code / Claude Desktop ───────────────────────────────────────
    # graphify claude install already wrote CLAUDE.md — append our block
    write("CLAUDE.md",
        f"## UALL Memory & Safety ({project_name})\n\n"
        f"{UALL_STARTUP_STEPS}",
        mode="a"
    )

    # ── 3. Cline / Roo Code ───────────────────────────────────────────────────
    write(".clinerules",
        f"# Cline / Roo Code Rules — {project_name} (UALL v3)\n\n"
        "<system_instructions>\n"
        f"You are operating in UALL-enabled repo: {project_name}.\n\n"
        f"{UALL_STARTUP_STEPS}"
        "</system_instructions>\n",
        mode="w"
    )

    # ── 4. Windsurf ───────────────────────────────────────────────────────────
    write(".windsurfrules",
        f"# Windsurf Rules — {project_name} (UALL v3)\n\n"
        f"{UALL_STARTUP_STEPS}\n"
        "# Graphify\n"
        "- Query the knowledge graph: `graphify query \"<question>\"`\n"
        "- After edits: `graphify update .`\n",
        mode="w"
    )

    # ── 5. Gemini CLI ─────────────────────────────────────────────────────────
    write("GEMINI.md",
        f"# {project_name}\n\n"
        "## Stack & Setup\n"
        "<!-- Fill in: stack, test command, dev server command -->\n"
        "- Test: `python uall.py /verify`\n"
        "- Status: `python uall.py /status`\n\n"
        f"## Agent Rules\n\n"
        f"{UALL_STARTUP_STEPS}\n"
        "## Graphify Knowledge Graph\n"
        "- Query: `graphify query \"<question>\"`\n"
        "- Path tracing: `graphify path \"<A>\" \"<B>\"`\n"
        "- After edits: `graphify update .`\n",
        mode="w"
    )

    # ── 6. Gemini Code Assist ─────────────────────────────────────────────────
    write(".gemini/styleguide.md",
        f"# Code Review Style Guide — {project_name}\n\n"
        "## UALL Safety Constraints\n"
        "- Flag any direct writes to `.agent/tools/` without a `gate.py` call\n"
        "- Flag any shell commands not wrapped in `tracer.py`\n"
        "- Flag any git commits not preceded by a `/verify` run\n"
        "- Flag hardcoded secrets or API keys\n\n"
        "## Project Standards\n"
        "<!-- Fill in: language style, test coverage requirements, etc. -->\n",
        mode="w"
    )
    write_json(".gemini/settings.json", {
        "ignore_patterns": [
            ".agent/memory/**",
            "graphify-out/**",
            "**/__pycache__/**",
            "**/.pytest_cache/**"
        ]
    })

    # ── 7. Antigravity ────────────────────────────────────────────────────────
    # graphify antigravity install already wrote .agents/rules/graphify.md
    # We write a separate UALL rules file alongside it
    write(".agents/rules/uall.md",
        "---\n"
        "trigger: always_on\n"
        f"description: UALL memory retrieval, safety gates, and verification workflow for {project_name}.\n"
        "---\n\n"
        f"## UALL — {project_name}\n\n"
        f"{UALL_STARTUP_STEPS}",
        mode="w"
    )
    # .agents/AGENTS.md — Antigravity project entry point
    write(".agents/AGENTS.md",
        f"# {project_name} — Agent Profile\n\n"
        "This project uses **mcp-memory-os (UALL v3)** for persistent memory,\n"
        "structured knowledge graphs (Graphifyy), and governed execution.\n\n"
        "## Roles\n"
        "- **AI Agent:** Implements features, fixes bugs, writes tests\n"
        "- **Human:** Reviews checkpoints, approves Tier-3 actions, fills spec files\n\n"
        f"## Required Startup\n\n"
        f"{UALL_STARTUP_STEPS}\n"
        "## Key Files\n"
        "| File | Purpose |\n"
        "|------|---------|\n"
        "| `.agent/spec/design.md` | Architecture, stack, constraints |\n"
        "| `.agent/spec/tasks/<id>.json` | Active ticket scope |\n"
        "| `.agent/PLAYBOOK.md` | Graduated codebase lessons |\n"
        "| `.agent/GOVERNANCE.md` | Risk tiers, restricted files |\n"
        "| `graphify-out/graph.json` | Live code knowledge graph |\n",
        mode="w"
    )

    # ── 8. GitHub Copilot (base) ──────────────────────────────────────────────
    write(".github/copilot-instructions.md",
        f"# GitHub Copilot Instructions — {project_name}\n\n"
        "## Project Context\n"
        "<!-- Fill in: what this project does, key constraints -->\n\n"
        f"## UALL Agent Rules\n\n"
        f"{UALL_RULES_BRIEF}\n"
        "## Graphify\n"
        "- Architecture questions: `graphify query \"<question>\"`\n"
        "- Call paths: `graphify path \"<A>\" \"<B>\"`\n"
        "- After edits: `graphify update .`\n",
        mode="w"
    )

    # ── 9. GitHub Copilot (granular — Python files) ───────────────────────────
    write(".github/instructions/uall-python.instructions.md",
        "---\n"
        "applyTo: '**/*.py'\n"
        "---\n"
        "# Python File Rules (UALL)\n"
        "- Wrap every subprocess/shell call: `python .agent/tools/tracer.py \"<cmd>\"`\n"
        "- Never import from `.agent/tools/` directly — call via uall.py commands\n"
        "- Add UTF-8 encoding to all file open() calls\n",
        mode="w"
    )

    # ── 10. GitHub Copilot (granular — kernel protection) ─────────────────────
    write(".github/instructions/uall-kernel.instructions.md",
        "---\n"
        "applyTo: '.agent/tools/**'\n"
        "---\n"
        "# UALL Kernel Protection\n"
        "STOP. You are editing the UALL kernel (.agent/tools/).\n"
        "Run this first: `python .agent/tools/gate.py write <file_path>`\n"
        "If gate.py returns DENY, do NOT proceed without human approval.\n",
        mode="w"
    )

    # ── 11. VS Code workspace settings ────────────────────────────────────────
    write_json(".vscode/settings.json", {
        "chat.instructionsFilesLocations": {
            ".github/instructions": True
        },
        "github.copilot.chat.codeGeneration.useInstructionFiles": True
    })

    # ── 12. Aider ─────────────────────────────────────────────────────────────
    write("CONVENTIONS.md",
        f"# Conventions — {project_name}\n\n"
        "## UALL Workflow\n"
        f"{UALL_RULES_BRIEF}\n"
        "## Graphify\n"
        "- `graphify query \"<question>\"` before editing complex modules\n"
        "- `graphify update .` after each editing session\n\n"
        "## Stack\n"
        "<!-- Fill in: language, framework, test runner, linter -->\n",
        mode="w"
    )
    write(".aider.conf.yml",
        "# Aider configuration — UALL\n"
        "read:\n"
        "  - CONVENTIONS.md\n"
        "  - .agent/spec/design.md\n"
        "  - .agent/PLAYBOOK.md\n",
        mode="w"
    )

    # ── 13. OpenHands / OpenDevin ─────────────────────────────────────────────
    write(".openhands/microagents/uall.md",
        "---\n"
        "name: uall\n"
        "type: repo\n"
        "agent: CodeActAgent\n"
        "trigger: always\n"
        "---\n\n"
        f"# UALL Memory & Safety — {project_name}\n\n"
        f"{UALL_STARTUP_STEPS}",
        mode="w"
    )

    # ── 14. Devin — fix root AGENTS.md to have project context block at top ───
    root_agents = target_dir / "AGENTS.md"
    if root_agents.exists():
        existing = root_agents.read_text(encoding="utf-8")
        if "## Project Context" not in existing:
            project_block = (
                f"# {project_name}\n\n"
                "## Project Context\n"
                "<!-- Fill in: what this project does, key URLs, team conventions -->\n\n"
                "## Setup\n"
                "```bash\n"
                "python uall.py /status    # verify memory index\n"
                "python uall.py /verify    # lint + security + tests\n"
                "```\n\n"
                "## Never Modify\n"
                "- `.agent/tools/` (UALL kernel — use gate.py)\n"
                "- `.agent/GOVERNANCE.md` (requires human approval)\n\n"
                "---\n\n"
            )
            root_agents.write_text(project_block + existing, encoding="utf-8")

    # ── 15. .agent/AGENTS.md — replace {PROJECT_NAME} placeholder ─────────────
    agent_agents = target_dir / ".agent" / "AGENTS.md"
    if agent_agents.exists():
        content = agent_agents.read_text(encoding="utf-8")
        content = content.replace("{PROJECT_NAME}", project_name)
        agent_agents.write_text(content, encoding="utf-8")

    # ── 16. PLAYBOOK.md stub ──────────────────────────────────────────────────
    playbook = target_dir / ".agent" / "PLAYBOOK.md"
    if not playbook.exists():
        playbook.write_text(
            f"# Playbook — {project_name}\n\n"
            "> Auto-generated stub. Lessons are compiled here via `/dream` + `/graduate`.\n\n"
            "## Graduated Lessons\n"
            "_No lessons yet. Run `python uall.py /dream` after each sprint._\n\n"
            "## Known Footguns\n"
            "_None yet._\n\n"
            "## Architecture Decisions Made\n"
            "_None recorded yet._\n",
            encoding="utf-8"
        )

    # ── 17. design.md — replace stub scan dump with real fillable template ─────
    design = target_dir / ".agent" / "spec" / "design.md"
    if design.exists():
        content = design.read_text(encoding="utf-8")
        # Check if it's still the auto-scan stub
        if "Auto-Discovery Results" in content:
            # Preserve the auto-detected stack info
            design.write_text(
                f"# Project Design — {project_name}\n\n"
                "> ACTION REQUIRED: Fill in the sections below before running agent tasks.\n"
                "> An agent reading an unfilled spec will have no useful context.\n\n"
                "## Purpose\n"
                "<!-- What does this project do? What problem does it solve? -->\n\n"
                "## Stack\n"
                + "\n".join(
                    line for line in content.splitlines()
                    if line.startswith("- Type:") or line.startswith("- Root")
                ) + "\n"
                "<!-- Add: framework versions, databases, key libraries -->\n\n"
                "## Key Modules\n"
                "<!-- List main entry points, services, or packages -->\n\n"
                "## Architecture Decisions\n"
                "<!-- Why key tech choices were made -->\n\n"
                "## Do Not Touch\n"
                "- `.agent/tools/` — UALL kernel, gate-protected\n"
                "- `.agent/GOVERNANCE.md` — requires human approval\n\n"
                "## Test Command\n"
                "```bash\n"
                "python uall.py /verify\n"
                "```\n",
                encoding="utf-8"
            )

    # ── 18. Eve skill (only if Eve project detected) ──────────────────────────
    is_eve = (target_dir / ".eve").exists() or (target_dir / "agent" / "channels" / "eve.ts").exists()
    if is_eve:
        write(".eve/skills/uall-memory.md",
            f"# UALL Memory & Safety Skill\n\n"
            "You are operating inside a UALL-governed project.\n\n"
            f"{UALL_STARTUP_STEPS}",
            mode="w"
        )
        print("   [OK] Eve UALL skill generated (.eve/skills/uall-memory.md)")

    print(f"   [OK] All IDE instruction files generated for '{project_name}'")


def deploy(target_dir: Path) -> None:
    print(f"UALL MASTER INSTALLER v3.0: Deploying to '{target_dir}'...")
    target_dir.mkdir(parents=True, exist_ok=True)

    if not SOURCE_DIR.exists():
        print(f"[ERR] uall-template not found at {SOURCE_DIR}")
        print("      Run this from the UALL development root.")
        sys.exit(1)

    # ── Step 1: Deploy framework core ─────────────────────────────────────────
    items = [".agent", "uall.py", "README.md"]
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
    print("[OK] Framework core deployed.")

    # ── Step 2: Git init if needed ────────────────────────────────────────────
    if not (target_dir / ".git").exists():
        print("[..] Initializing Git...")
        subprocess.run(["git", "init"], cwd=target_dir, capture_output=True)

    # ── Step 3: Install graphify (smart — checks before running pip/uv) ───────
    print("[..] Checking Graphifyy...")
    has_graphify = _ensure_graphify(target_dir)

    # ── Step 4: Run graphify IDE integrations FIRST ───────────────────────────
    # (so our patch in step 5 can append on top, not get overwritten)
    if has_graphify:
        print("[..] Configuring Graphifyy IDE integrations...")
        _run_graphify_ide_installs(target_dir)

    # ── Step 5: Generate ALL IDE instruction files (single source of truth) ───
    print("[..] Generating IDE instruction files...")
    _generate_ide_files(target_dir)

    # ── Step 6: Initial graph scan ────────────────────────────────────────────
    print("[..] Initial domain scan...")
    subprocess.run(
        [sys.executable, str(target_dir / ".agent" / "tools" / "graph_sync.py")],
        cwd=target_dir, capture_output=True
    )

    # ── Step 7: Initial memory index ─────────────────────────────────────────
    print("[..] Building search index...")
    subprocess.run(
        [sys.executable, str(target_dir / ".agent" / "tools" / "index_memory.py")],
        cwd=target_dir, capture_output=True
    )

    # NOTE: We do NOT chmod 555 tools — that breaks re-runs and updates.
    # Kernel integrity is enforced via security_v2.py --sign instead.

    print("\nUALL DEPLOYMENT COMPLETE.")
    print("-" * 40)
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  python uall.py /status")
    print("  python uall.py /task <TASK-ID>")
    print("  Fill in: .agent/spec/design.md  <-- ACTION REQUIRED")
    print("  python .agent/tools/security_v2.py --sign  # lock kernel hashes")
    print("-" * 40)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    deploy(target)
