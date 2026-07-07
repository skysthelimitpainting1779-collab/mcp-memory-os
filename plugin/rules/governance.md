# Governance & Safety Policy

## Risk Tiers

| Tier | Impact | Approval Required |
| :--- | :--- | :--- |
| **Tier 1** | Low (Docs, Tests, Local Fixes) | Auto-Approve |
| **Tier 2** | Medium (Network, New Skills, Memory Promotion) | Agent Consensus / Logged |
| **Tier 3** | High (Production Config, Security, Kernel Files) | Human Review Required |

## Protected Files (Tier 3 — No Agent Writes)
- `.agent/GOVERNANCE.md`
- `.agent/tools/gate.py`
- `.agent/tools/recover.py`
- `.agent/tools/security_v2.py`
- `.agent/protocols/hook_patterns.json`
- `.agent/protocols/semgrep_rules.yaml`

## Operational Boundaries
- No external network calls unless the governance tier explicitly allows it.
- No deletion of episodic logs without archival to `.agent/memory/episodic/archive/`.
- All shell commands MUST be wrapped in `tracer.py` during task execution.
- The `/checkpoint` command requires a prior `/verify` pass in the same session.

## Capability Tags
Explicitly grant these in this file to allow Tier-3 operations:
- `CAPABILITY: BASH_FULL_CONTROL` — enables unrestricted shell_exec via gate.py
