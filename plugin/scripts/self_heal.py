#!/usr/bin/env python3
"""
self_heal.py — Analyze episodic logs for repeating failures and write active hints.
Hints below threshold stay "proposed"; above threshold become "active".
"""
import json
import glob
import sys
import datetime
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)

EPISODIC_DIR       = AGENT / "memory" / "episodic"
HINTS_PATH         = AGENT / "protocols" / "self_healing_hints.md"
FAILURE_THRESHOLD  = 2   # occurrences before a hint becomes "active"
MAX_HINTS          = 10  # cap to avoid hint sprawl


def load_failure_signals() -> list[tuple[str, str]]:
    """Return list of (reason, command) tuples from all episodic logs."""
    signals = []
    for log_file in sorted(EPISODIC_DIR.glob("*.jsonl")):
        with open(log_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    anomalies = data.get("anomalies", [])
                    status    = data.get("status", "")
                    command   = data.get("command", "")[:80]
                    if status == "Failed":
                        signals.append((f"Exit failure: {command}", command))
                    for a in anomalies:
                        signals.append((a, command))
                except json.JSONDecodeError:
                    continue
    return signals


def self_heal() -> None:
    print("🩹 UALL Self-Healing Analysis...")
    HINTS_PATH.parent.mkdir(parents=True, exist_ok=True)

    signals = load_failure_signals()
    if not signals:
        HINTS_PATH.write_text(
            "# Self-Healing Hints\n\n## Active Hints\nNo active hints — system healthy.\n"
        )
        print("  ✅ No failures detected. System healthy.")
        return

    counts = Counter(reason for reason, _ in signals)
    command_map = {reason: cmd for reason, cmd in signals}

    active_hints   = []
    proposed_hints = []

    for reason, count in counts.most_common(MAX_HINTS):
        cmd = command_map.get(reason, "unknown")
        entry = (
            f"- **Issue** ({count}×): {reason}\n"
            f"  **Context**: `{cmd}`\n"
            f"  **Rule**: Investigate prerequisites before retrying this pattern.\n"
        )
        if count >= FAILURE_THRESHOLD:
            active_hints.append(entry)
        else:
            proposed_hints.append(entry)

    lines = [
        f"# Self-Healing Hints",
        f"*Updated: {datetime.datetime.now().isoformat()[:16]}*\n",
    ]

    if active_hints:
        lines.append("## Active Hints")
        lines.append(
            "*These patterns exceeded the failure threshold and are surfaced on every `/recall`.*\n"
        )
        lines.extend(active_hints)

    if proposed_hints:
        lines.append("\n## Proposed Hints (below threshold)")
        lines.extend(proposed_hints)

    HINTS_PATH.write_text("\n".join(lines) + "\n")

    print(f"  ⚠️  {len(active_hints)} active hint(s), {len(proposed_hints)} proposed.")
    if active_hints:
        print("  These hints will be surfaced automatically during /recall.")


if __name__ == "__main__":
    self_heal()
