#!/usr/bin/env python3
"""
export_insights.py — Sanitize and export high-confidence graduated lessons
for cross-repo / cross-team sharing.
"""
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)

GRADUATED_JSONL = AGENT / "memory" / "graduated" / "LESSONS.jsonl"
EXPORT_FILE     = ROOT / "uall_shared_insights.jsonl"
SCORE_THRESHOLD = 0.85


def sanitize(text: str | None) -> str:
    if not text:
        return ""
    # Remove filesystem paths
    text = re.sub(r"(/[a-zA-Z0-9._\-]+)+", "[PATH]", text)
    # Remove IP addresses
    text = re.sub(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", "[IP]", text)
    # Remove anything that looks like a secret (key=value with >12-char value)
    text = re.sub(r"\b\w+=([\w/+]{12,})\b", r"\1=[REDACTED]", text)
    return text


def export() -> None:
    print("🌍 UALL Federated Export: Sanitizing insights...")

    if not GRADUATED_JSONL.exists():
        print("  No graduated lessons to export.")
        return

    shared_count = 0
    with open(GRADUATED_JSONL) as f_in, open(EXPORT_FILE, "w") as f_out:
        for line in f_in:
            try:
                lesson = json.loads(line)
            except json.JSONDecodeError:
                continue

            confidence = float(lesson.get("confidence", 0))
            if confidence < SCORE_THRESHOLD:
                continue

            sanitized = {
                "id":         lesson.get("id"),
                "title":      sanitize(lesson.get("title", "")),
                "topic":      lesson.get("topic", "general"),
                "confidence": confidence,
                "insight":    sanitize(lesson.get("insight", "General architectural pattern.")),
                "tags":       lesson.get("tags", []),
            }
            f_out.write(json.dumps(sanitized) + "\n")
            shared_count += 1

    print(f"✅ Exported {shared_count} sanitized insights → {EXPORT_FILE}")
    print(f"   Threshold: confidence ≥ {SCORE_THRESHOLD}")


if __name__ == "__main__":
    export()
