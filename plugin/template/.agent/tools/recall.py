#!/usr/bin/env python3
"""
recall.py — Hybrid memory search: FTS5 lexical + graph relationships + self-healing hints.
Usage: python3 .agent/tools/recall.py --task "description" [--limit N] [--detail]
"""
import sqlite3
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir

ROOT = find_project_root()
AGENT = agent_dir(ROOT)
DB_PATH = AGENT / "memory" / ".index" / "memory.db"


def search_lexical(query: str, limit: int = 5) -> list:
    if not DB_PATH.exists():
        return []
    conn = sqlite3.connect(DB_PATH)
    try:
        cursor = conn.cursor()
        # Use FTS5 MATCH with highlight for better snippet quality
        sql = """
            SELECT content_id, type, snippet(memory_fts, 2, '[', ']', '...', 32), rank
            FROM memory_fts
            WHERE memory_fts MATCH ?
            ORDER BY rank
            LIMIT ?
        """
        cursor.execute(sql, (query, limit))
        return cursor.fetchall()
    except sqlite3.OperationalError:
        return []
    finally:
        conn.close()


def get_self_healing_hints() -> str | None:
    hints_path = AGENT / "protocols" / "self_healing_hints.md"
    if not hints_path.exists():
        return None
    content = hints_path.read_text()
    # Only surface hints that have been activated (contain "## Active Hints")
    if "## Active Hints" in content and "No active hints" not in content:
        return content
    # Also surface pending proposals so agent sees them
    if "PENDING CONSENSUS" in content:
        return content
    return None


def get_graph_context(task_query: str) -> list[str]:
    graph_json_path = ROOT / "graphify-out" / "graph.json"
    HAS_GRAPHIFY = False
    try:
        import graphify
        HAS_GRAPHIFY = True
    except ImportError:
        pass

    if HAS_GRAPHIFY and graph_json_path.exists():
        import subprocess
        cmd = [sys.executable, "-m", "graphify", "query", task_query, "--budget", "1000"]
        try:
            res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
            if res.returncode == 0:
                lines = res.stdout.strip().splitlines()
                paths = []
                for line in lines:
                    line = line.strip()
                    if line.startswith("EDGE "):
                        clean = line.replace("EDGE ", "").split("[")[0].strip()
                        paths.append(clean)
                if paths:
                    return paths[:8]
        except Exception:
            pass

    graph_rel_path = AGENT / "memory" / "graph" / "relationships.jsonl"
    if not graph_rel_path.exists():
        return []
    tokens = set(task_query.lower().split())
    related = []
    seen = set()
    with open(graph_rel_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rel = json.loads(line)
                subj = rel.get("subject_id", "").lower()
                obj = rel.get("object_id", "").lower()
                pred = rel.get("predicate", "")
                if any(t in subj or t in obj for t in tokens):
                    entry = f"{rel['subject_id']} ─[{pred}]→ {rel['object_id']}"
                    if entry not in seen:
                        seen.add(entry)
                        related.append(entry)
            except json.JSONDecodeError:
                continue
    return related[:8]


def get_active_task_context() -> str | None:
    active_file = AGENT / ".active_task"
    if not active_file.exists():
        return None
    task_id = active_file.read_text().strip()
    task_file = AGENT / "spec" / "tasks" / f"{task_id}.json"
    if task_file.exists():
        try:
            data = json.loads(task_file.read_text())
            return f"Task {task_id}: {data.get('description', 'No description')}"
        except Exception:
            pass
    return f"Active Task: {task_id}"


def main():
    parser = argparse.ArgumentParser(description="UALL Recall — Hybrid Memory Search")
    parser.add_argument("--task", type=str, required=True, help="Task description or keywords")
    parser.add_argument("--detail", action="store_true", help="Show full body (300 chars vs 150)")
    parser.add_argument("--limit", type=int, default=5, help="Max results from FTS index")
    args = parser.parse_args()

    print(f"🧠 UALL Recall: '{args.task}'")
    print("─" * 50)

    # 1. Active task context
    task_ctx = get_active_task_context()
    if task_ctx:
        print(f"\n📌 [ACTIVE TASK]\n  {task_ctx}")

    # 2. Self-Healing hints — surfaces FIRST so agent can't miss them
    hints = get_self_healing_hints()
    if hints:
        print("\n⚠️  [CRITICAL SELF-HEALING HINTS — READ BEFORE PROCEEDING]")
        print(hints)
        print("─" * 50)

    # 3. Graph context — structural knowledge
    graph = get_graph_context(args.task)
    if graph:
        print("\n🕸️  [GRAPH RELATIONSHIPS]")
        for g in graph:
            print(f"  {g}")

    # 4. FTS5 lexical search
    results = search_lexical(args.task, args.limit)
    if results:
        print(f"\n📚 [TOP {len(results)} MEMORIES]")
        snippet_len = 300 if args.detail else 150
        for cid, ctype, body, rank in results:
            print(f"\n  ── {ctype.upper()} [{Path(cid).name}] ──")
            print(f"  {body[:snippet_len]}{'...' if len(body) > snippet_len else ''}")
    else:
        # Fallback: show playbook excerpt
        playbook = AGENT / "PLAYBOOK.md"
        if playbook.exists():
            print("\n📖 [PLAYBOOK FALLBACK — no index matches]")
            print(playbook.read_text()[:600])
        else:
            print("\n  No memories found. Run `/index` to build the search index.")

    print("\n─" * 50)


if __name__ == "__main__":
    main()
