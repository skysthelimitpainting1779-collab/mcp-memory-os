#!/usr/bin/env python3
"""
gate.py — Behavioral Gatekeeper v4.
Checks exec commands and write paths against governance tiers.
No longer blocks pipe/redirect syntax — those are legitimate shell constructs.
"""
import sys
import shlex
import json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)

# Binaries that are categorically Tier-3 and need human review
TIER3_BINARIES = {"rm", "chmod", "chown", "dd", "mkfs", "fdisk", "shutdown", "reboot"}

# Binaries that are Tier-2 (network-capable or destructive if misused)
TIER2_BINARIES = {"curl", "wget", "nc", "ncat", "ssh", "scp", "rsync", "docker", "kubectl"}

# Protected paths within .agent/ — only tools themselves may write here
PROTECTED_KERNEL_PATHS = {
    ".agent/tools",
    ".agent/protocols",
    ".agent/GOVERNANCE.md",
    ".agent/skills/core",
}


def classify_exec(command: str) -> tuple[bool, str, int]:
    """
    Returns (allowed, message, tier).
    Tier 1 = auto-approve, Tier 2 = log + warn, Tier 3 = block.
    """
    try:
        parts = shlex.split(command)
    except ValueError:
        return False, "Malformed command (unbalanced quotes).", 3

    if not parts:
        return True, "Empty command — trivially safe.", 1

    binary = Path(parts[0]).name  # Handle full paths like /usr/bin/rm

    if binary in TIER3_BINARIES:
        # Special case: `rm` of a purely local relative path without -rf is Tier 2
        if binary == "rm":
            flags = [p for p in parts[1:] if p.startswith("-")]
            targets = [p for p in parts[1:] if not p.startswith("-")]
            is_recursive = any("r" in f.lower() or "f" in f for f in flags)
            is_absolute = any(t.startswith("/") or t.startswith("..") for t in targets)
            if not is_recursive and not is_absolute:
                return True, "Local non-recursive rm approved (Tier 2).", 2
        return False, f"Tier-3 binary '{binary}' requires human sign-off (GOVERNANCE.md).", 3

    if binary in TIER2_BINARIES:
        return True, f"Network-capable binary '{binary}' — logged for review (Tier 2).", 2

    return True, "Safe behavior predicted (Tier 1).", 1


def classify_write(path_str: str) -> tuple[bool, str, int]:
    """Check if a file write is permitted."""
    norm = str(Path(path_str))
    for protected in PROTECTED_KERNEL_PATHS:
        if norm.startswith(protected):
            return False, f"Direct kernel write to '{path_str}' prohibited (Tier 3).", 3
    if norm.startswith(".agent/memory/"):
        return True, "Memory write approved (Tier 1).", 1
    return True, "Write approved (Tier 1).", 1


def main():
    if len(sys.argv) < 3:
        print("Usage: gate.py <exec|write|delete> <payload>")
        sys.exit(1)

    action_type = sys.argv[1].lower()
    payload = sys.argv[2]

    if action_type == "exec":
        allowed, msg, tier = classify_exec(payload)
    elif action_type in ("write", "delete"):
        allowed, msg, tier = classify_write(payload)
    else:
        print(f"❌ Unknown action type: {action_type}")
        sys.exit(1)

    tier_emoji = {1: "✅", 2: "⚠️ ", 3: "❌"}[tier]
    print(f"{tier_emoji} Tier {tier} | {msg}")

    # Emit structured JSON for programmatic callers
    result = {"allowed": allowed, "message": msg, "tier": tier, "action": action_type, "payload": payload}
    print(json.dumps(result))

    sys.exit(0 if allowed else 1)


if __name__ == "__main__":
    main()
