#!/usr/bin/env python3
"""
enhance.py — Gap analysis: detect repeated manual patterns in episodic logs
and scaffold skill proposals for them.
"""
import json
import glob
import sys
import datetime
import hashlib
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir, ensure_dirs

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)
CANDIDATE_SKILLS = AGENT / "skills" / "pending"


def stable_id(seed: str) -> str:
    return hashlib.sha1(seed.encode()).hexdigest()[:8].upper()


def load_commands() -> list[str]:
    cmds = []
    for log_file in sorted((AGENT / "memory" / "episodic").glob("*.jsonl")):
        with open(log_file) as f:
            for line in f:
                try:
                    data = json.loads(line.strip())
                    if data.get("status") == "Success" and data.get("command"):
                        cmds.append(data["command"][:120])
                except (json.JSONDecodeError, KeyError):
                    pass
    return cmds


def detect_gaps(commands: list[str]) -> list[dict]:
    """Find command patterns repeated ≥3 times that don't have a skill yet."""
    # Normalize: strip args, keep binary+first-arg as pattern key
    patterns = []
    for cmd in commands:
        parts = cmd.strip().split()
        key = " ".join(parts[:2]) if len(parts) >= 2 else parts[0] if parts else ""
        if key:
            patterns.append(key)

    counts = Counter(patterns)
    existing_skills = {p.stem for p in (AGENT / "skills" / "domain").glob("*.md")}
    existing_pending = {p.stem for p in CANDIDATE_SKILLS.glob("*.md")}

    gaps = []
    for pattern, count in counts.most_common(10):
        if count < 3:
            break
        skill_name = pattern.replace(" ", "_").replace("/", "-")
        if skill_name in existing_skills or skill_name in existing_pending:
            continue
        gaps.append({
            "name": skill_name,
            "pattern": pattern,
            "count": count,
            "reason": f"Command pattern `{pattern}` repeated {count}× in episodic logs without a skill.",
            "proposed_procedure": (
                f"1. Recall context: `/recall \"{pattern}\"`\n"
                f"2. Execute via tracer: `python3 .agent/tools/tracer.py \"{pattern} <args>\"`\n"
                f"3. Verify output and run `/verify`\n"
                f"4. Checkpoint on success: `/checkpoint \"Applied {skill_name}\"`"
            ),
        })
    return gaps


def scaffold_skill(proposal: dict) -> Path:
    ensure_dirs(CANDIDATE_SKILLS)
    name = proposal["name"]
    path = CANDIDATE_SKILLS / f"{name}.md"
    if path.exists():
        return path  # Don't overwrite existing proposal

    content = (
        f"---\n"
        f"id: SKILL-{stable_id(name)}\n"
        f"name: {name}\n"
        f"created: {datetime.date.today().isoformat()}\n"
        f"confidence: 0.0\n"
        f"---\n\n"
        f"# Skill: {name}\n\n"
        f"## Reason for Evolution\n{proposal['reason']}\n\n"
        f"## Trigger\nWhen `{proposal['pattern']}` needs to be applied consistently.\n\n"
        f"## Procedure\n{proposal['proposed_procedure']}\n\n"
        f"## Verification\n- Run `/verify` after execution.\n"
        f"- Success criteria: exit code 0, no anomalies in tracer log.\n"
    )
    path.write_text(content)
    return path


def main():
    print("🧠 UALL Enhancer: Scanning for capability gaps...")
    commands = load_commands()
    if not commands:
        print("  No successful commands in episodic logs yet.")
        return

    gaps = detect_gaps(commands)
    if not gaps:
        print("  ✅ No new gaps detected — all repeated patterns have skills.")
        return

    for gap in gaps:
        path = scaffold_skill(gap)
        print(f"  ✨ Scaffolded: {path.name}  (pattern: `{gap['pattern']}` ×{gap['count']})")

    print(f"\n  {len(gaps)} skill proposal(s) written to {CANDIDATE_SKILLS}")
    print("  Run `/audit` then `/graduate` to activate them.")


if __name__ == "__main__":
    main()
