"""
_agent_utils.py  —  UALL shared helpers
Every tool imports from here instead of reimplementing path resolution.
"""
from __future__ import annotations
import os
import subprocess
from pathlib import Path


def find_project_root(start: Path | None = None) -> Path:
    """Walk up from `start` (default: cwd) until we find .agent/ directory."""
    here = Path(start or Path.cwd()).resolve()
    for candidate in [here, *here.parents]:
        if (candidate / ".agent").is_dir():
            return candidate
    # Fallback: use cwd (allows bootstrapping into a new project)
    return here


def agent_dir(root: Path | None = None) -> Path:
    return find_project_root(root) / ".agent"


def tools_dir(root: Path | None = None) -> Path:
    return agent_dir(root) / "tools"


def run_git(args: list[str], cwd: Path | None = None) -> str | None:
    """Run a git command. Returns stdout or None on error."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            check=True,
            cwd=str(cwd or find_project_root()),
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"  git error: {e.stderr.strip()}")
        return None


def ensure_dirs(*paths: Path) -> None:
    for p in paths:
        p.mkdir(parents=True, exist_ok=True)
