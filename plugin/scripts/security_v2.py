#!/usr/bin/env python3
"""
security_v2.py — Kernel integrity verification.
  --sign    : Hash the protected tools (run once by a human after setup)
  --verify  : Check that hashes still match (run before /checkpoint)
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)
INTEGRITY_DB = AGENT / "protocols" / ".integrity.json"

PROTECTED_FILES = [
    ".agent/tools/gate.py",
    ".agent/tools/recover.py",
    ".agent/tools/security_v2.py",
    ".agent/GOVERNANCE.md",
]


def sha256(file_path: Path) -> str:
    hasher = hashlib.sha256()
    hasher.update(file_path.read_bytes())
    return hasher.hexdigest()


def sign_tools() -> None:
    manifest = {}
    missing = []
    for rel_path in PROTECTED_FILES:
        abs_path = ROOT / rel_path
        if abs_path.exists():
            manifest[rel_path] = sha256(abs_path)
        else:
            missing.append(rel_path)

    if missing:
        print(f"⚠️  Some protected files not found (skipped):")
        for m in missing:
            print(f"   {m}")

    INTEGRITY_DB.parent.mkdir(parents=True, exist_ok=True)
    INTEGRITY_DB.write_text(json.dumps(manifest, indent=2))
    print(f"🛡️  Signed {len(manifest)} kernel files → {INTEGRITY_DB}")


def verify_integrity() -> bool:
    if not INTEGRITY_DB.exists():
        print("  ⏭  No integrity manifest found — run `--sign` to create one.")
        return True  # First-run case, don't block

    try:
        manifest = json.loads(INTEGRITY_DB.read_text())
    except (json.JSONDecodeError, OSError) as e:
        print(f"  ❌ Integrity DB unreadable: {e}")
        return False

    all_ok = True
    for rel_path, expected_hash in manifest.items():
        abs_path = ROOT / rel_path
        if not abs_path.exists():
            print(f"  ❌ MISSING: {rel_path}")
            all_ok = False
            continue
        current = sha256(abs_path)
        if current != expected_hash:
            print(f"  🚨 TAMPERED: {rel_path}")
            all_ok = False
        else:
            print(f"  ✅ {rel_path}")

    return all_ok


def main():
    if len(sys.argv) < 2:
        print("Usage: security_v2.py --sign | --verify")
        sys.exit(1)

    flag = sys.argv[1]
    if flag == "--sign":
        sign_tools()
    elif flag == "--verify":
        ok = verify_integrity()
        if not ok:
            print("\n🚨 SECURITY ALERT: Kernel tamper detected. Do NOT /checkpoint.")
            sys.exit(1)
        else:
            print("\n✅ All kernel files verified.")
    else:
        print(f"Unknown flag: {flag}")
        sys.exit(1)


if __name__ == "__main__":
    main()
