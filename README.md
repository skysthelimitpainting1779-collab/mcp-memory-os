# UALL — Universal Agentic Learning Layer

A portable AI agent operating system. Drop `.agent/` and `uall.py` into any project and your agent gains memory, governance, and continuous learning.

## Quick Start

```bash
# In any project
python3 uall.py /status          # Check brain health
python3 uall.py /task TASK-123   # Initialize task context
python3 uall.py /recall "jwt auth pattern"  # Search memory
```

## The Learning Loop

```
/task → /recall → [execute via tracer.py] → /dream → /graduate → /checkpoint
```

1. **`/task <id>`** — Link work to a Linear/GitHub ticket
2. **`/recall "<desc>"`** — Surface relevant memory (FTS + graph + hints)
3. **`tracer.py "<cmd>"`** — Wrap every shell command for telemetry
4. **`/dream`** — Mine failure correlations from logs → candidate lessons
5. **`/enhance`** → **`/audit`** → **`/graduate`** — Evolve agent skills
6. **`/verify`** — Run semgrep + ruff + pytest → unlock `/checkpoint`
7. **`/checkpoint "<msg>"`** — Git-commit the brain state
8. **`/report`** — Generate PR/Linear intelligence summary

## Structure

```
.agent/
├── GOVERNANCE.md          # Risk tiers + capability grants
├── PLAYBOOK.md            # Auto-generated from graduated lessons
├── AGENTS.md              # Role definitions + SOP
├── memory/
│   ├── episodic/          # Per-day JSONL event logs
│   ├── candidate_lessons/ # Proposed learnings (awaiting graduation)
│   ├── graduated/         # LESSONS.md + LESSONS.jsonl (source of truth)
│   ├── graph/             # entities.md + relationships.jsonl
│   └── .index/            # SQLite FTS5 search index
├── skills/
│   ├── core/              # Framework skills (UALL_MASTER.md)
│   ├── domain/            # Graduated project-specific skills
│   └── pending/           # Awaiting /audit approval
├── protocols/
│   ├── semgrep_rules.yaml # Security + decoupling checks
│   ├── hook_patterns.json # Pre/post-tool hooks
│   └── self_healing_hints.md  # Active failure-avoidance hints
├── spec/
│   ├── design.md          # Auto-generated domain knowledge
│   └── tasks/             # Per-task context JSON files
└── tools/                 # All UALL executables
    ├── _agent_utils.py    # Shared path helpers (import me!)
    ├── recall.py          # Hybrid FTS+graph memory search
    ├── auto_dream.py      # Failure correlation mining
    ├── graduate.py        # Candidate → Playbook promotion
    ├── index_memory.py    # Incremental FTS5 index builder
    ├── graph_sync.py      # Temporal knowledge graph
    ├── tracer.py          # Command shadow tracer
    ├── verify.py          # Semgrep + Ruff + Pytest gate
    ├── recover.py         # Git checkpoint & recovery
    ├── gate.py            # Behavioral gatekeeper
    ├── task_bridge.py     # Linear/GitHub task linkage
    ├── self_heal.py       # Failure pattern → active hints
    ├── enhance.py         # Pattern → skill scaffolder
    ├── audit.py           # Adversarial skill reviewer
    ├── report.py          # Intelligence report generator
    ├── export_insights.py # Sanitized cross-repo export
    ├── security_v2.py     # Kernel integrity signing/verify
    ├── mcp_server.py      # MCP server for IDE integration
    └── pre_commit_hook.py # Git hook for auto-indexing
```

## MCP / IDE Integration

See `MCP_SETUP.md` for Claude Desktop / Cursor setup.
