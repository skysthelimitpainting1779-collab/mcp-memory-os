#!/usr/bin/env python3
"""
auto_dream.py — Correlation mining: detect command sequences that precede failures
and scaffold candidate lessons. Uses stable SHA-based IDs, not session-volatile hash().
"""
import glob
import json
import os
import collections
import hashlib
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir, ensure_dirs

ROOT = find_project_root()
AGENT = agent_dir(ROOT)
CANDIDATE_DIR = AGENT / "memory" / "candidate_lessons"
EPISODIC_DIR = AGENT / "memory" / "episodic"


def stable_id(seed: str) -> str:
    """Generate a deterministic short ID from a string."""
    return hashlib.sha1(seed.encode()).hexdigest()[:8].upper()


def load_events() -> list[dict]:
    events = []
    for log_file in sorted(EPISODIC_DIR.glob("*.jsonl")):
        with open(log_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    events.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return events


def mine_failure_sequences(events: list[dict]) -> collections.Counter:
    """Find (cmd_n-1, cmd_n) pairs where cmd_n resulted in failure or anomaly."""
    sequences = []
    for i in range(1, len(events)):
        prev = events[i - 1]
        curr = events[i]
        is_failure = curr.get("status") == "Failed" or bool(curr.get("anomalies"))
        if is_failure:
            sequences.append((
                prev.get("command", "unknown")[:60],
                curr.get("command", "unknown")[:60],
                curr.get("status", "Unknown"),
                curr.get("anomalies", [None])[0] if curr.get("anomalies") else None,
            ))
    return collections.Counter(sequences)


def scaffold_lesson(cmd1: str, cmd2: str, status: str, anomaly: str | None, count: int) -> Path:
    seed = f"{cmd1}|{cmd2}"
    lesson_id = f"CL-DREAM-{stable_id(seed)}"
    path = CANDIDATE_DIR / f"{lesson_id}.md"

    # Don't overwrite an existing lesson — just update its count in metadata
    if path.exists():
        content = path.read_text()
        # bump the seen-count comment
        content = content.replace(
            "<!-- dream-count:", f"<!-- updated: {datetime.date.today()} | dream-count:"
        )
        path.write_text(content)
        return path

    detail = f"anomaly: {anomaly}" if anomaly else f"exit status: {status}"
    content = (
        f"---\n"
        f"id: {lesson_id}\n"
        f"topic: stability\n"
        f"confidence: 0.75\n"
        f"created: {datetime.date.today().isoformat()}\n"
        f"---\n\n"
        f"# Candidate Lesson: Caution before `{cmd2[:40]}`\n\n"
        f"**Pattern detected {count}× in episodic logs.**\n\n"
        f"Running `{cmd1}` immediately before `{cmd2}` correlates with failure "
        f"({detail}). Investigate side effects or missing prerequisites before "
        f"combining these commands.\n\n"
        f"<!-- dream-count: {count} -->\n"
    )
    path.write_text(content)
    return path


def dream():
    print("🌙 UALL Dream Engine: Mining failure correlations...")
    ensure_dirs(CANDIDATE_DIR)

    events = load_events()
    if len(events) < 2:
        print("  Not enough episodic data yet (need ≥ 2 events). Log more tasks first.")
        return

    counts = mine_failure_sequences(events)
    if not counts:
        print("  ✅ No failure sequences detected. System healthy.")
        return

    scaffolded = 0
    for (cmd1, cmd2, status, anomaly), count in counts.most_common():
        if count >= 2:
            path = scaffold_lesson(cmd1, cmd2, status, anomaly, count)
            print(f"  ⚠️  Sequence → failure ({count}×): {cmd1[:30]} → {cmd2[:30]}")
            print(f"     Scaffolded: {path.name}")
            scaffolded += 1

    if scaffolded:
        print(f"\n✨ {scaffolded} candidate lesson(s) written to {CANDIDATE_DIR}")
        print("   Run `/graduate` to promote high-confidence lessons to the Playbook.")
    else:
        print("  No patterns exceeded the threshold of 2 occurrences.")


if __name__ == "__main__":
    dream()
