# Agent Roles

| Role       | Responsibilities |
| :--------- | :--------------- |
| Architect  | Design decisions, ADRs, spec updates |
| Developer  | Feature implementation, tests |
| SRE        | Deployments, monitoring, incident response |
| Auditor    | Skill review via `/audit`, security sign-off |

## SOP Quick Reference

1. `/task <id>` — Link to Linear/GitHub ticket
2. `/recall "<description>"` — Surface relevant memory
3. Execute via `python3 .agent/tools/tracer.py "<cmd>"` — Capture telemetry
4. `/dream` — Mine patterns from logs
5. `/verify` — Run semgrep + ruff + pytest
6. `/checkpoint "<msg>"` — Persist verified state
7. `/report` — Generate PR/Linear summary
