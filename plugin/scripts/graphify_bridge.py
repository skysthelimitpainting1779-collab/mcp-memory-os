#!/usr/bin/env python3
"""
graphify_bridge.py — Bridge wrapper for the graphifyy library.
"""
import sys
import subprocess
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root

ROOT = find_project_root()


def run_graphify(*args: str) -> str:
    cmd = [sys.executable, "-m", "graphify"] + list(args)
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        out = res.stdout.strip()
        err = res.stderr.strip()
        if res.returncode != 0:
            return f"❌ Graphifyy Error:\n{out}\n{err}".strip()
        return out
    except Exception as e:
        return f"❌ Execution error: {e}"


def main():
    parser = argparse.ArgumentParser(description="Graphifyy Bridge")
    parser.add_argument("--query", type=str, help="BFS query on the codebase graph")
    parser.add_argument("--affected", type=str, help="Impact analysis for a node/symbol")
    parser.add_argument("--tree", action="store_true", help="Generate interactive collapsible D3 tree")
    parser.add_argument("--callflow", action="store_true", help="Export call-flow graph HTML")
    parser.add_argument("--extract", action="store_true", help="Run full code extraction")
    
    args, unknown = parser.parse_known_args()

    # If no flags are provided, default to full extraction
    if not (args.query or args.affected or args.tree or args.callflow or args.extract):
        print("🔍 Extracting codebase structure via Graphifyy...")
        print(run_graphify("extract", ".", "--no-cluster"))
        return

    if args.extract:
        print("🔍 Extracting codebase structure via Graphifyy...")
        print(run_graphify("extract", ".", "--no-cluster"))
    elif args.query:
        print(run_graphify("query", args.query))
    elif args.affected:
        print(run_graphify("affected", args.affected))
    elif args.tree:
        print("🌳 Generating collapsible graph tree...")
        print(run_graphify("tree"))
    elif args.callflow:
        print("🗺️ Exporting callflow mapping...")
        print(run_graphify("export", "callflow-html"))


if __name__ == "__main__":
    main()
