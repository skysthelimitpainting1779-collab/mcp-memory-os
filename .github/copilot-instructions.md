# GitHub Copilot Instructions — mcp-memory-os

## Project Context
<!-- Fill in: what this project does, key constraints -->

## UALL Agent Rules

- Run `python uall.py /recall "<task>"` before starting any task
- Read `.agent/spec/design.md` and the active `.agent/spec/tasks/*.json`
- Check `.agent/PLAYBOOK.md` for codebase-specific lessons
- Wrap shell commands: `python .agent/tools/tracer.py "<cmd>"`
- Gate writes to restricted files: `python .agent/tools/gate.py write <path>`
- Checkpoint only after `/verify` passes: `python uall.py /checkpoint "<msg>"`

## Graphify
- Architecture questions: `graphify query "<question>"`
- Call paths: `graphify path "<A>" "<B>"`
- After edits: `graphify update .`
