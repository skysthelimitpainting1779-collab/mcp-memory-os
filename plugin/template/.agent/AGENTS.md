# 👥 {PROJECT_NAME} Roles & SOP Guidelines

This project utilizes **mcp-memory-os** (powered by UALL) to maintain structural integrity, long-term memory, and codebase safety.

---

## 🤖 Active Agent Profile
- **System Version:** mcp-memory-os v2.0
- **Operational Mode:** Local-first, git-backed learning loop

---

## 📋 Core Agent Commands

Use these commands via the `uall.py` interface inside the project:
* `/status` — Verify the health of the agent's memory index and active task.
* `/task <id>` — Link the workspace to a specific task identifier (e.g., Jira, Linear, or GitHub issues).
* `/recall <desc>` — Query past lessons, context, and structural codebase mappings.
* `/graphify [<args>]` — Parse codebase structure, run BFS/DFS graph queries, or export visualizations via Graphifyy.
* `/verify` — Run security scans (Semgrep), code linter (Ruff), and test suites (pytest).
* `/checkpoint "<msg>"` — Commit current progress to Git (unlocked only after a successful `/verify`).

---

## 📂 Workspace Instruction Files

These files contain project-specific context the agent must consult before starting any task:

| File | Purpose |
|------|---------|
| `.agent/spec/design.md` | Architecture design, tech decisions, system constraints |
| `.agent/spec/tasks/<TASK-ID>.json` | Active ticket scope, requirements, and acceptance criteria |
| `.agent/PLAYBOOK.md` | Graduated codebase-specific lessons; rules for writing code *here* |
| `.agent/GOVERNANCE.md` | File write permissions, command risk tiers, security rules |

---

## 🛡️ Operational Guidelines

To ensure consistency, safety, and learning, the agent must adhere to the following rules:

1. **Memory First:** Always run `/recall` before starting a new task or editing complex code blocks to pull historical context.
2. **Consult Specs:** Read `.agent/spec/design.md` and the active `.agent/spec/tasks/<id>.json` before writing code.
3. **Check Playbook:** Check `.agent/PLAYBOOK.md` before touching any domain-specific logic.
4. **Command Tracing:** Execute any command-line tools (e.g., `npm install`, `pytest`, `cargo build`) wrapped in `tracer.py`:
   ```bash
   python .agent/tools/tracer.py "<command>"
   ```
   This captures the command telemetry and logs execution metrics into the episodic brain.
5. **Verify Before Checkpoint:** Never attempt to checkpoint the repository state without a successful `/verify` pass.
6. **No Kernel Modification:** Do not modify core files in `.agent/tools/` or `.agent/GOVERNANCE.md` without human override approval.
