#!/usr/bin/env python3
"""
uall_master_installer.py — UALL Master Installer v2.0
Deploys the framework to a target project directory.
Does NOT run chmod 555 on tools (that blocked re-runs in v1).
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

SOURCE_DIR = Path(__file__).parent / "template"


def deploy(target_dir: Path) -> None:
    print(f"🚀 UALL MASTER INSTALLER: Deploying to '{target_dir}'...")
    target_dir.mkdir(parents=True, exist_ok=True)

    if not SOURCE_DIR.exists():
        print(f"❌ uall-template not found at {SOURCE_DIR}")
        print("   Run this from the UALL development root.")
        sys.exit(1)

    # Deploy framework
    items = [".agent", "uall.py", ".cursorrules", ".clinerules", "README.md"]
    for item in items:
        src = SOURCE_DIR / item
        dst = target_dir / item
        if not src.exists():
            continue
        if src.is_dir():
            if dst.exists():
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)
        print(f"  [+] {item}")

    print("✅ Framework core deployed.")

    # Git init if needed
    if not (target_dir / ".git").exists():
        print("🐙 Initializing Git...")
        subprocess.run(["git", "init"], cwd=target_dir, capture_output=True)

    # Initial domain scan
    print("🔍 Initial domain scan...")
    subprocess.run(
        [sys.executable, str(target_dir / ".agent" / "tools" / "graph_sync.py")],
        cwd=target_dir, capture_output=True
    )

    # Initial memory index
    print("🧠 Building search index...")
    subprocess.run(
        [sys.executable, str(target_dir / ".agent" / "tools" / "index_memory.py")],
        cwd=target_dir, capture_output=True
    )

    # NOTE: We do NOT chmod 555 tools — that breaks re-runs and updates.
    # Kernel integrity is enforced via security_v2.py --sign instead.

    print("\n🏁 UALL DEPLOYMENT COMPLETE.")
    print("─" * 40)
    print("Next steps:")
    print(f"  cd {target_dir}")
    print("  python3 uall.py /status")
    print("  python3 uall.py /task <TASK-ID>")
    print("  python3 .agent/tools/security_v2.py --sign  # lock kernel hashes")
    print("─" * 40)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    deploy(target)
