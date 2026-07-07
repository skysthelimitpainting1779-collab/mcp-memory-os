#!/usr/bin/env python3
"""
tracer.py — Shadow Tracer v2.
Wraps any shell command, captures output, logs telemetry, and detects silent killers.
Usage: python3 .agent/tools/tracer.py "npm install"
       python3 .agent/tools/tracer.py pytest tests/ -v
"""
import subprocess
import sys
import time
import json
import os
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir, ensure_dirs

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)
LOG_DIR = AGENT / "memory" / "episodic"

# Thresholds
SLOW_THRESHOLD_SECS = 10.0
MAX_OUTPUT_BYTES    = 4096  # Truncate logged output to avoid bloating the index


def detect_anomalies(stdout: str, stderr: str, duration: float, exit_code: int) -> list[str]:
    anomalies = []
    combined = (stdout + stderr).lower()

    if not stdout.strip() and not stderr.strip() and exit_code == 0:
        anomalies.append("Zero-length output on success — may indicate a no-op.")
    if "warning" in combined or "deprecat" in combined:
        anomalies.append("Hidden warnings or deprecation notices detected in output.")
    if "error" in combined and exit_code == 0:
        anomalies.append("Word 'error' found in output despite exit code 0 — inspect carefully.")
    if duration > SLOW_THRESHOLD_SECS:
        anomalies.append(f"Performance anomaly: command took {duration:.1f}s (>{SLOW_THRESHOLD_SECS}s threshold).")
    if "segmentation fault" in combined or "core dumped" in combined:
        anomalies.append("CRITICAL: Segmentation fault or core dump detected.")

    return anomalies


def get_active_task() -> str:
    active_file = AGENT / ".active_task"
    if active_file.exists():
        return active_file.read_text().strip()
    return "general"


def trace(command: str) -> tuple[str, str, int, list[str]]:
    ensure_dirs(LOG_DIR)
    start = time.monotonic()

    process = subprocess.Popen(
        command,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=str(ROOT),
    )
    stdout, stderr = process.communicate()
    duration = time.monotonic() - start
    exit_code = process.returncode

    status = "Success" if exit_code == 0 else "Failed"
    anomalies = detect_anomalies(stdout, stderr, duration, exit_code)

    log_entry = {
        "timestamp":  datetime.datetime.utcnow().isoformat(),
        "task_id":    get_active_task(),
        "command":    command,
        "exit_code":  exit_code,
        "duration":   round(duration, 3),
        "status":     status,
        "anomalies":  anomalies,
        "output":     (stdout + stderr)[:MAX_OUTPUT_BYTES],
    }

    log_file = LOG_DIR / f"{datetime.date.today()}.jsonl"
    with open(log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

    return stdout, stderr, exit_code, anomalies


def main():
    if len(sys.argv) < 2:
        print("Usage: tracer.py <command> [args...]")
        sys.exit(1)

    command = " ".join(sys.argv[1:])
    stdout, stderr, code, alerts = trace(command)

    sys.stdout.write(stdout)
    sys.stderr.write(stderr)

    if alerts:
        print(f"\n⚠️  UALL TRACER ALERTS:", file=sys.stderr)
        for a in alerts:
            print(f"   • {a}", file=sys.stderr)

    sys.exit(code)


if __name__ == "__main__":
    main()
