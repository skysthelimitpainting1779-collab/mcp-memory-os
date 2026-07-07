#!/usr/bin/env python3
"""
graduate.py — Promote high-confidence candidate lessons and approved skills.
Also updates PLAYBOOK.md and triggers an auto-checkpoint.
"""
import os
import json
import re
import datetime
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir

ROOT = find_project_root()
AGENT = agent_dir(ROOT)

CANDIDATE_DIR   = AGENT / "memory" / "candidate_lessons"
PENDING_SKILLS  = AGENT / "skills" / "pending"
DOMAIN_SKILLS   = AGENT / "skills" / "domain"
REPORTS_DIR     = AGENT / "skills" / "audit_reports"
GRADUATED_MD    = AGENT / "memory" / "graduated" / "LESSONS.md"
GRADUATED_JSONL = AGENT / "memory" / "graduated" / "LESSONS.jsonl"
PLAYBOOK_MD     = AGENT / "PLAYBOOK.md"

CONFIDENCE_THRESHOLD = 0.75  # Lowered from 0.8 for better throughput


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Robust YAML frontmatter parser — does not crash on missing keys."""
    match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
    if not match:
        return {}, content
    yaml_text = match.group(1)
    body = match.group(2)
    metadata = {}
    for line in yaml_text.splitlines():
        if ":" in line:
            key, _, val = line.partition(":")
            metadata[key.strip()] = val.strip()
    return metadata, body


def load_graduated_ids() -> set[str]:
    """Return set of already-graduated IDs to avoid duplicates."""
    if not GRADUATED_JSONL.exists():
        return set()
    ids = set()
    with open(GRADUATED_JSONL) as f:
        for line in f:
            try:
                ids.add(json.loads(line).get("id", ""))
            except json.JSONDecodeError:
                pass
    return ids


def run_checkpoint(msg: str) -> None:
    try:
        subprocess.run(
            [sys.executable, str(AGENT / "tools" / "recover.py"), "checkpoint", msg],
            check=True,
            cwd=str(ROOT),
        )
    except subprocess.CalledProcessError as e:
        print(f"  ⚠️  Checkpoint failed: {e}")


def graduate_lessons() -> int:
    """Promote candidate lessons meeting the confidence threshold."""
    if not CANDIDATE_DIR.exists():
        return 0

    already_graduated = load_graduated_ids()
    promoted = 0

    for md_file in sorted(CANDIDATE_DIR.glob("*.md")):
        content = md_file.read_text()
        meta, body = parse_frontmatter(content)

        lesson_id = meta.get("id", md_file.stem)

        # Skip already-graduated lessons
        if lesson_id in already_graduated:
            continue

        try:
            confidence = float(meta.get("confidence", 0))
        except ValueError:
            confidence = 0.0

        if confidence < CONFIDENCE_THRESHOLD:
            print(f"  ⏭  Skipped {md_file.name} (confidence {confidence:.2f} < {CONFIDENCE_THRESHOLD})")
            continue

        now = datetime.datetime.now().isoformat()

        # Append to LESSONS.jsonl
        with open(GRADUATED_JSONL, "a") as jf:
            jf.write(json.dumps({
                "id": lesson_id,
                "title": meta.get("title", md_file.stem),
                "topic": meta.get("topic", "general"),
                "confidence": confidence,
                "graduated_at": now,
                "source_file": md_file.name,
            }) + "\n")

        # Append to LESSONS.md
        with open(GRADUATED_MD, "a") as mf:
            mf.write(f"\n## {lesson_id}: {md_file.stem}\n")
            mf.write(f"*Graduated: {now[:10]} | Confidence: {confidence}*\n\n")
            mf.write(body.strip() + "\n")

        promoted += 1
        print(f"  🎓 Graduated: {md_file.name} (confidence {confidence:.2f})")

    return promoted


def graduate_skills() -> int:
    """Promote adversarially-approved pending skills to domain/."""
    if not PENDING_SKILLS.exists():
        return 0

    promoted = 0
    DOMAIN_SKILLS.mkdir(parents=True, exist_ok=True)

    for skill_file in PENDING_SKILLS.glob("*.md"):
        report_path = REPORTS_DIR / skill_file.name.replace(".md", "_report.json")
        if not report_path.exists():
            print(f"  ⏭  Skipped {skill_file.name} — no audit report found (run /audit first)")
            continue
        try:
            report = json.loads(report_path.read_text())
        except (json.JSONDecodeError, OSError):
            print(f"  ⚠️  Corrupt audit report for {skill_file.name}")
            continue
        if report.get("status") != "APPROVED":
            print(f"  ❌ Skill REJECTED: {skill_file.name} (score {report.get('score')})")
            if report.get("findings"):
                for f in report["findings"]:
                    print(f"     • {f}")
            continue
        dest = DOMAIN_SKILLS / skill_file.name
        skill_file.rename(dest)
        print(f"  ✅ Skill promoted to domain/: {skill_file.name}")
        promoted += 1

    return promoted


def rebuild_playbook() -> None:
    """Regenerate PLAYBOOK.md from graduated lessons + core principles."""
    core_principles = """# Operational Playbook

*Auto-generated from graduated lessons. Do not edit manually — update lessons instead.*

## Core Principles

1. **Be Portable**: All context must reside within `.agent/`. Never hardcode absolute paths.
2. **Be Explicit**: Document assumptions in the spec/. Run `/recall` before every task.
3. **Be Safe**: Every high-impact action must pass `/verify` before `/checkpoint`.
4. **Be Traceable**: Wrap all shell commands with `tracer.py` to catch silent killers.
5. **Be Iterative**: `/dream` → `/graduate` is the feedback loop. Run it nightly.

## Graduated Lessons

"""
    graduated_content = ""
    if GRADUATED_MD.exists():
        raw = GRADUATED_MD.read_text()
        # Strip the auto-header if it already exists to avoid doubling
        body = re.sub(r"^# Temporal.*?\n\n", "", raw, flags=re.DOTALL).strip()
        graduated_content = body

    PLAYBOOK_MD.write_text(core_principles + graduated_content + "\n")
    print(f"  📖 Playbook rebuilt: {PLAYBOOK_MD}")


def graduate():
    print("🎓 UALL Graduation Pipeline starting...")

    lessons = graduate_lessons()
    skills  = graduate_skills()
    total   = lessons + skills

    if total > 0:
        rebuild_playbook()
        run_checkpoint(f"Graduate: +{lessons} lessons, +{skills} skills")
        print(f"\n✅ Graduation complete. Promoted {total} asset(s).")
    else:
        print("\n  Nothing new to graduate.")


if __name__ == "__main__":
    graduate()
