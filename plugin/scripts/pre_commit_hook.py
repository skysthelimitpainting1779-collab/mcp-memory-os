#!/usr/bin/env python3
"""
pre_commit_hook.py — Git pre-commit hook that refreshes the memory index and graph.
Install: cp .agent/tools/pre_commit_hook.py .git/hooks/pre-commit && chmod +x .git/hooks/pre-commit
"""
import subprocess
import sys
from pathlib import Path

AGENT_TOOLS = Path(__file__).resolve().parent


def run(label: str, args: list[str]) -> bool:
    print(f"  🔄 UALL Pre-Commit: {label}...")
    result = subprocess.run([sys.executable] + args, capture_output=True)
    if result.returncode != 0:
        print(f"     ⚠️  {label} returned non-zero (non-blocking): {result.stderr.decode()[:200]}")
    return result.returncode == 0


def main():
    print("🛡️  UALL Pre-Commit Hook")
    run("Refreshing memory index", [str(AGENT_TOOLS / "index_memory.py")])
    run("Syncing knowledge graph",  [str(AGENT_TOOLS / "graph_sync.py")])
    sys.exit(0)  # Never block the commit for derivative cache failures


if __name__ == "__main__":
    main()
