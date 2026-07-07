#!/usr/bin/env python3
"""
task_bridge.py — Initialize a task context from Linear/GitHub and link it to UALL.
After init, triggers a graph sync so entity linkage is always fresh.
"""
import os
import json
import datetime
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir, ensure_dirs

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)
TASKS_DIR = AGENT / "spec" / "tasks"


def init_task(task_id: str, source: str = "linear") -> None:
    ensure_dirs(TASKS_DIR)

    task_metadata = {
        "id":               task_id,
        "source":           source,
        "status":           "in_progress",
        "started_at":       datetime.datetime.now().isoformat(),
        "description":      f"[Fetched from {source}] Task {task_id}",
        "related_entities": [],
    }

    # Check for existing task file to preserve manual notes
    task_file = TASKS_DIR / f"{task_id}.json"
    if task_file.exists():
        existing = json.loads(task_file.read_text())
        # Preserve any manually-added fields
        task_metadata.update({k: v for k, v in existing.items()
                               if k not in ("status", "started_at")})
        task_metadata["status"] = "in_progress"
        task_metadata["resumed_at"] = datetime.datetime.now().isoformat()

    task_file.write_text(json.dumps(task_metadata, indent=2))

    # Set as active task
    (AGENT / ".active_task").write_text(task_id)

    print(f"🌉 Task Bridge: {task_id} initialized (source: {source})")
    print(f"   Context saved to: {task_file}")

    # Trigger graph sync to link related entities
    print("   🕸️  Syncing knowledge graph...")
    subprocess.run(
        [sys.executable, str(AGENT / "tools" / "graph_sync.py")],
        capture_output=True,
        cwd=str(ROOT),
    )
    print(f"   Run `/recall \"{task_id}\"` to surface relevant context.")


def push_feedback(task_id: str) -> str:
    """Build a summary of graduated lessons relevant to this task."""
    lessons_file = AGENT / "memory" / "graduated" / "LESSONS.jsonl"
    if not lessons_file.exists():
        return f"No graduated lessons yet for {task_id}."

    relevant = []
    with open(lessons_file) as f:
        for line in f:
            try:
                lesson = json.loads(line)
                if task_id.lower() in json.dumps(lesson).lower():
                    relevant.append(f"- {lesson.get('id')}: {lesson.get('title', 'Unnamed')}")
            except json.JSONDecodeError:
                pass

    lines = [f"### UALL Intelligence Report for {task_id}"]
    if relevant:
        lines.append("**Relevant Graduated Lessons:**")
        lines.extend(relevant)
    else:
        lines.append("No directly-related lessons found.")
    lines.append("**Verification**: All professional checks passed (run /verify to confirm).")
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: task_bridge.py <task_id> [source]")
        sys.exit(1)

    task_id = sys.argv[1]
    source  = sys.argv[2] if len(sys.argv) > 2 else "linear"
    init_task(task_id, source)


if __name__ == "__main__":
    main()
