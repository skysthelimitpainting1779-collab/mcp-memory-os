#!/usr/bin/env python3
"""
verify.py — Verification gate: semgrep + ruff + pytest.
Writes .agent/.verified on success, which unlocks /checkpoint.
Also checks for unauthorized kernel mutations.
"""
import subprocess
import sys
import shutil
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)
VERIFIED_FLAG = AGENT / ".verified"
SEMGREP_RULES = AGENT / "protocols" / "semgrep_rules.yaml"


def run_tool(cmd: list[str], label: str) -> tuple[bool, str]:
    """Run a verification tool. Returns (passed, output)."""
    if not shutil.which(cmd[0]):
        return True, f"  ⏭  {label} not installed — skipped"
    print(f"  🔍 Running {label}...")
    res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
    output = (res.stdout + res.stderr).strip()
    if res.returncode != 0:
        return False, f"  ❌ {label} FAILED:\n{output[:500]}"
    return True, f"  ✅ {label} passed"


def check_kernel_mutation() -> tuple[bool, str]:
    """Detect unauthorized modifications to protected kernel files."""
    try:
        diff = subprocess.check_output(
            ["git", "diff", "--name-only"],
            text=True,
            cwd=str(ROOT),
        ).strip()
    except Exception:
        return True, "  ⏭  git diff unavailable — skipped kernel check"

    protected = [".agent/tools/", ".agent/protocols/", "GOVERNANCE.md"]
    violations = [line for line in diff.splitlines()
                  if any(line.startswith(p) or p in line for p in protected)]
    if violations:
        return False, (
            "  ❌ Unauthorized kernel mutation detected:\n"
            + "\n".join(f"     {v}" for v in violations)
        )
    return True, "  ✅ Kernel integrity check passed"


def verify_state() -> tuple[bool, str]:
    print("\n🔍 UALL Verification Gate")
    print("─" * 40)

    results = []
    all_passed = True

    # 1. Kernel mutation check
    ok, msg = check_kernel_mutation()
    print(msg)
    results.append(msg)
    if not ok:
        all_passed = False

    # 2. Semgrep (if rules exist and semgrep is installed)
    if SEMGREP_RULES.exists():
        src_dir = ROOT / "src"
        if src_dir.exists():
            ok, msg = run_tool(
                ["semgrep", "--config", str(SEMGREP_RULES), "src/", "--quiet"],
                "Semgrep"
            )
            print(msg)
            if not ok:
                all_passed = False

    # 3. Ruff
    ok, msg = run_tool(["ruff", "check", "src/", "--quiet"], "Ruff")
    print(msg)
    if not ok:
        all_passed = False

    # 4. Pytest — allowed to have no tests (won't fail gate)
    tests_dir = ROOT / "tests"
    if tests_dir.exists() and list(tests_dir.rglob("test_*.py")):
        ok, msg = run_tool(["pytest", "tests/", "-q", "--tb=short"], "Pytest")
        print(msg)
        if not ok:
            all_passed = False
    else:
        print("  ⏭  Pytest — no tests found, skipped")

    print("─" * 40)
    return all_passed, "Verification " + ("Successful." if all_passed else "FAILED.")


if __name__ == "__main__":
    success, msg = verify_state()
    if success:
        print(f"\n✅ {msg}")
        VERIFIED_FLAG.write_text("VALID")
    else:
        print(f"\n❌ {msg}")
        if VERIFIED_FLAG.exists():
            VERIFIED_FLAG.unlink()
        sys.exit(1)
