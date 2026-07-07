# Conventions — mcp-memory-os

## UALL Workflow
- Run `python uall.py /recall "<task>"` before starting any task
- Read `.agent/spec/design.md` and the active `.agent/spec/tasks/*.json`
- Check `.agent/PLAYBOOK.md` for codebase-specific lessons
- Wrap shell commands: `python .agent/tools/tracer.py "<cmd>"`
- Gate writes to restricted files: `python .agent/tools/gate.py write <path>`
- Checkpoint only after `/verify` passes: `python uall.py /checkpoint "<msg>"`

## Graphify
- `graphify query "<question>"` before editing complex modules
- `graphify update .` after each editing session

## Stack
<!-- Fill in: language, framework, test runner, linter -->
