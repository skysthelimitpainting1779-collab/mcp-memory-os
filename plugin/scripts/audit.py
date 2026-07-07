#!/usr/bin/env python3
"""
audit.py — Adversarial skill reviewer. Scores pending skills and writes audit reports.
"""
import sys
import os
import json
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir, ensure_dirs

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)
PENDING_DIR  = AGENT / "skills" / "pending"
REPORTS_DIR  = AGENT / "skills" / "audit_reports"

# Deductions
CHECKS = [
    (r"chmod|chown|GOVERNANCE\.md", 0.6, "CRITICAL: Skill modifies governance kernel."),
    (r"import uall_framework",       0.3, "WARNING: Introduces framework dependency (violates decoupling)."),
    (r"shell=True",                  0.2, "WARNING: Uses shell=True in subprocess call."),
    (r"Check the output",            0.2, "FAIL: Circular verification phrase detected."),
]

REQUIRED_SECTIONS = ["Verification", "Procedure", "Trigger"]


def audit_skill(skill_file: Path) -> dict:
    content = skill_file.read_text()
    findings = []
    score = 1.0

    for pattern, penalty, message in CHECKS:
        if re.search(pattern, content, re.IGNORECASE):
            findings.append(message)
            score -= penalty

    for section in REQUIRED_SECTIONS:
        if f"## {section}" not in content:
            findings.append(f"FAIL: Missing required section '## {section}'.")
            score -= 0.2

    score = round(max(0.0, score), 2)
    status = "APPROVED" if score >= 0.6 else "REJECTED"

    return {
        "skill": skill_file.name,
        "status": status,
        "score": score,
        "findings": findings,
    }


def main():
    ensure_dirs(REPORTS_DIR)
    if not PENDING_DIR.exists():
        print("  No pending skills to audit.")
        return

    pending = list(PENDING_DIR.glob("*.md"))
    if not pending:
        print("  No pending skills found.")
        return

    for skill_file in pending:
        report = audit_skill(skill_file)
        report_path = REPORTS_DIR / skill_file.name.replace(".md", "_report.json")
        report_path.write_text(json.dumps(report, indent=2))

        icon = "✅" if report["status"] == "APPROVED" else "❌"
        print(f"  {icon} {skill_file.name}: {report['status']} (score {report['score']})")
        for finding in report.get("findings", []):
            print(f"     • {finding}")

    print(f"\n  Audit reports written to {REPORTS_DIR}")
    print("  Run `/graduate` to promote APPROVED skills.")


if __name__ == "__main__":
    main()
