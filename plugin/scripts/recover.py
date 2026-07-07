#!/usr/bin/env python3
"""
recover.py — Git-native checkpoint & recovery for .agent/ memory state.
"""
import subprocess
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir, run_git

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)
AGENT_REL = ".agent"


def checkpoint(message: str) -> None:
    print(f"💾 Creating UALL Checkpoint: {message}")

    run_git(["add", AGENT_REL], cwd=ROOT)

    status = run_git(["status", "--porcelain", AGENT_REL], cwd=ROOT)
    if not status:
        print("  No changes in .agent/ to checkpoint.")
        return

    result = run_git(["commit", "-m", f"UALL Checkpoint: {message}"], cwd=ROOT)
    if result is not None:
        print(f"  ✅ Checkpoint saved: {message}")
    else:
        print("  ⚠️  Commit failed — check git config (user.email / user.name may be unset).")


def recover(version: str | None = None) -> None:
    target = version or "HEAD"
    print(f"🚨 Recovering .agent/ to: {target}")
    run_git(["checkout", target, "--", AGENT_REL], cwd=ROOT)
    print(f"  ✅ .agent/ restored to {target}")
    print("  🔄 Re-indexing memory...")
    subprocess.run(
        [sys.executable, str(AGENT / "tools" / "index_memory.py")],
        check=False,
        cwd=str(ROOT),
    )


def list_history(n: int = 10) -> None:
    print(f"📜 UALL Memory History (Last {n}):")
    logs = run_git(["log", f"-n{n}", "--oneline", "--", AGENT_REL], cwd=ROOT)
    if logs:
        print(logs)
    else:
        print("  No UALL checkpoints found. Run /checkpoint after your first task.")


def main():
    parser = argparse.ArgumentParser(description="UALL Recovery Tool")
    sub = parser.add_subparsers(dest="command")

    cp = sub.add_parser("checkpoint", help="Save .agent/ state to git")
    cp.add_argument("message", nargs="?", default="Manual checkpoint")

    rec = sub.add_parser("recover", help="Restore .agent/ from git")
    rec.add_argument("--version", help="Commit hash (defaults to HEAD)")

    hist = sub.add_parser("history", help="List recent UALL checkpoints")
    hist.add_argument("--count", type=int, default=10)

    args = parser.parse_args()

    if args.command == "checkpoint":
        checkpoint(args.message)
    elif args.command == "recover":
        recover(getattr(args, "version", None))
    elif args.command == "history":
        list_history(getattr(args, "count", 10))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
