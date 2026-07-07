# mcp-memory-os — Agent Profile

This project uses **mcp-memory-os (UALL v3)** for persistent memory,
structured knowledge graphs (Graphifyy), and governed execution.

## Roles
- **AI Agent:** Implements features, fixes bugs, writes tests
- **Human:** Reviews checkpoints, approves Tier-3 actions, fills spec files

## Required Startup

UALL STARTUP SEQUENCE — run these steps before writing ANY code:
1. python uall.py /recall "<describe your task in 3-5 words>"
2. Read: .agent/spec/design.md  (architecture & stack constraints)
3. Read active task: .agent/spec/tasks/<task-id>.json  (run /task <id> to set)
4. Check: .agent/PLAYBOOK.md  (graduated lessons for THIS codebase)
DURING WORK:
- Wrap every shell command:  python .agent/tools/tracer.py "<cmd>"
- Before writing .agent/ files: python .agent/tools/gate.py write <path>
- Respect: .agent/GOVERNANCE.md  (risk tiers, restricted files)
BEFORE COMMITTING:
- python uall.py /verify  (lint + security + tests must pass)
- python uall.py /checkpoint "<message>"  (only after green /verify)

## Key Files
| File | Purpose |
|------|---------|
| `.agent/spec/design.md` | Architecture, stack, constraints |
| `.agent/spec/tasks/<id>.json` | Active ticket scope |
| `.agent/PLAYBOOK.md` | Graduated codebase lessons |
| `.agent/GOVERNANCE.md` | Risk tiers, restricted files |
| `graphify-out/graph.json` | Live code knowledge graph |
