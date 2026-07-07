# AGENTS.md

This project is managed by UALL (Universal Agentic Learning Layer).

## Project Status
- **Active Task**: TEST-1
- **System Version**: UALL v2.0

## Core Commands
- `/status` — Check brain health
- `/recall <desc>` — Search project memory
- `/task <id>` — Initialize task context
- `/verify` — Run security & quality gates
- `/checkpoint` — Persist verified state

## Operational Rules
1. **Trace Everything**: Run all shell commands via `python3 .agent/tools/tracer.py "<cmd>"`.
2. **Verify First**: Never `/checkpoint` without a successful `/verify`.
3. **Memory First**: Always `/recall` before starting a new task.

## Tech Stack
- Python detected
