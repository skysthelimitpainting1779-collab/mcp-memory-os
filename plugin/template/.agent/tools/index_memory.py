#!/usr/bin/env python3
"""
index_memory.py — Build / incrementally refresh the SQLite FTS5 memory index.

Strategy:
- On first run: full build.
- On subsequent runs: only re-index files whose mtime is newer than the DB mtime.
  Pass --force to always do a full rebuild.
"""
import sqlite3
import os
import json
import glob
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir, ensure_dirs

ROOT = find_project_root()
AGENT = agent_dir(ROOT)
DB_PATH = AGENT / "memory" / ".index" / "memory.db"


def get_db_mtime() -> float:
    """Return the mtime of the DB, or 0 if it doesn't exist yet."""
    return DB_PATH.stat().st_mtime if DB_PATH.exists() else 0.0


def init_db(conn: sqlite3.Connection) -> None:
    cursor = conn.cursor()
    cursor.execute("""
        CREATE VIRTUAL TABLE IF NOT EXISTS memory_fts USING fts5(
            content_id UNINDEXED,
            type,
            body,
            metadata UNINDEXED
        )
    """)
    # Track indexed files for incremental updates
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS index_state (
            path TEXT PRIMARY KEY,
            mtime REAL NOT NULL
        )
    """)
    conn.commit()


def clear_file_from_index(conn: sqlite3.Connection, path: str) -> None:
    conn.execute("DELETE FROM memory_fts WHERE content_id = ?", (path,))
    conn.execute("DELETE FROM index_state WHERE path = ?", (path,))


def index_file(conn: sqlite3.Connection, path: str, content_type: str,
               force: bool = False) -> bool:
    """Index a single file if it has changed. Returns True if indexed."""
    if not os.path.exists(path):
        return False
    mtime = os.path.getmtime(path)
    if not force:
        row = conn.execute(
            "SELECT mtime FROM index_state WHERE path = ?", (path,)
        ).fetchone()
        if row and row[0] >= mtime:
            return False  # Up to date

    clear_file_from_index(conn, path)
    content = open(path).read()
    conn.execute(
        "INSERT INTO memory_fts (content_id, type, body, metadata) VALUES (?, ?, ?, ?)",
        (path, content_type, content, json.dumps({"path": path}))
    )
    conn.execute(
        "INSERT OR REPLACE INTO index_state (path, mtime) VALUES (?, ?)",
        (path, mtime)
    )
    return True


def index_episodic_logs(conn: sqlite3.Connection, force: bool = False) -> int:
    """Index JSONL log files line-by-line. Each line → one FTS entry."""
    log_files = glob.glob(str(AGENT / "memory" / "episodic" / "*.jsonl"))
    total = 0
    for log_file in log_files:
        mtime = os.path.getmtime(log_file)
        if not force:
            row = conn.execute(
                "SELECT mtime FROM index_state WHERE path = ?", (log_file,)
            ).fetchone()
            if row and row[0] >= mtime:
                continue
        # Re-index this file fully
        conn.execute("DELETE FROM memory_fts WHERE content_id = ?", (log_file,))
        with open(log_file) as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    body = " ".join(filter(None, [
                        data.get("action", ""),
                        data.get("outcome", ""),
                        data.get("thought", ""),
                        data.get("command", ""),
                        str(data.get("status", "")),
                        " ".join(data.get("anomalies", [])),
                    ]))
                    conn.execute(
                        "INSERT INTO memory_fts (content_id, type, body, metadata) VALUES (?, ?, ?, ?)",
                        (log_file, "episodic", body, line)
                    )
                    total += 1
                except json.JSONDecodeError:
                    continue
        conn.execute(
            "INSERT OR REPLACE INTO index_state (path, mtime) VALUES (?, ?)",
            (log_file, mtime)
        )
    return total


def index_graph_entities(conn: sqlite3.Connection, force: bool = False) -> int:
    """Index entities.md block by block. Each block -> one FTS entry."""
    entities_path = AGENT / "memory" / "graph" / "entities.md"
    if not entities_path.exists():
        return 0
    mtime = entities_path.stat().st_mtime
    if not force:
        row = conn.execute(
            "SELECT mtime FROM index_state WHERE path = ?", (str(entities_path),)
        ).fetchone()
        if row and row[0] >= mtime:
            return 0
            
    conn.execute("DELETE FROM memory_fts WHERE content_id = ?", (str(entities_path),))
    content = entities_path.read_text(encoding="utf-8")
    
    blocks = content.split("---")
    total = 0
    for block in blocks:
        block = block.strip()
        if not block or block.startswith("#"):
            continue
        try:
            data = json.loads(block)
            body = " ".join(filter(None, [
                data.get("name", ""),
                data.get("type", ""),
                data.get("source_file", ""),
                data.get("source_location", ""),
            ]))
            conn.execute(
                "INSERT INTO memory_fts (content_id, type, body, metadata) VALUES (?, ?, ?, ?)",
                (str(entities_path), "graph_entity", body, json.dumps(data))
            )
            total += 1
        except json.JSONDecodeError:
            continue
            
    conn.execute(
        "INSERT OR REPLACE INTO index_state (path, mtime) VALUES (?, ?)",
        (str(entities_path), mtime)
    )
    return total



def remove_stale_entries(conn: sqlite3.Connection) -> int:
    """Remove index entries for files that no longer exist."""
    rows = conn.execute("SELECT path FROM index_state").fetchall()
    removed = 0
    for (path,) in rows:
        if not os.path.exists(path):
            clear_file_from_index(conn, path)
            removed += 1
    return removed


def main():
    parser = argparse.ArgumentParser(description="UALL Memory Indexer")
    parser.add_argument("--force", action="store_true", help="Full rebuild, ignore cache")
    args = parser.parse_args()

    ensure_dirs(DB_PATH.parent)
    conn = sqlite3.connect(DB_PATH)
    init_db(conn)

    if args.force:
        print("⚡ Forcing full index rebuild...")
        conn.execute("DELETE FROM memory_fts")
        conn.execute("DELETE FROM index_state")
        conn.commit()

    indexed = 0
    sources = [
        (str(AGENT / "PLAYBOOK.md"),                         "playbook"),
        (str(AGENT / "GOVERNANCE.md"),                       "governance"),
        (str(AGENT / "memory" / "graduated" / "LESSONS.md"), "lesson"),
        (str(AGENT / "spec" / "design.md"),                  "design"),
    ]
    for path, ctype in sources:
        if index_file(conn, path, ctype, force=args.force):
            print(f"  ✔ indexed {ctype}: {Path(path).name}")
            indexed += 1

    # Index all candidate lessons
    for path in glob.glob(str(AGENT / "memory" / "candidate_lessons" / "*.md")):
        if index_file(conn, path, "candidate", force=args.force):
            indexed += 1

    # Index all graduated skills
    for path in glob.glob(str(AGENT / "skills" / "domain" / "*.md")):
        if index_file(conn, path, "skill", force=args.force):
            indexed += 1

    # Index episodic logs
    log_total = index_episodic_logs(conn, force=args.force)
    if log_total:
        print(f"  ✔ indexed {log_total} episodic log entries")

    # Index graph entities
    graph_total = index_graph_entities(conn, force=args.force)
    if graph_total:
        print(f"  ✔ indexed {graph_total} graph entities")

    # Prune stale entries
    removed = remove_stale_entries(conn)
    if removed:
        print(f"  🗑  removed {removed} stale entries")

    conn.commit()
    conn.close()

    if indexed or log_total or graph_total or removed:
        print(f"\n✅ Index updated: +{indexed} files, +{log_total} logs, +{graph_total} entities, -{removed} stale")
    else:
        print("✅ Index already up to date.")


if __name__ == "__main__":
    main()
