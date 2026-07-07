# mcp-memory-os

## Stack & Setup
<!-- Fill in: stack, test command, dev server command -->
- Test: `python uall.py /verify`
- Status: `python uall.py /status`

## Agent Rules

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

## Graphify Knowledge Graph
- Query: `graphify query "<question>"`
- Path tracing: `graphify path "<A>" "<B>"`
- After edits: `graphify update .`
