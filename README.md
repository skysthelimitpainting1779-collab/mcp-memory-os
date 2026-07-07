# 🧠 AgentOS — The Portable Memory, Security & Self-Healing Layer for AI Agents

[![GitHub license](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org)
[![Agent Compatibility](https://img.shields.io/badge/agents-Cursor%20%7C%20Claude%20%7C%20Custom-orange)](https://github.com)

**Stop building stateless agents.** Turn Cursor, Claude Desktop, and custom agent scripts into production-grade developers. **AgentOS** (powered by UALL) is a lightweight, zero-dependency engine you can drop into any repository to instantly equip your AI developer with long-term memory, execution guardrails, and self-healing loops.

```
                  ┌────────────────────────────────────────┐
                  │          AI AGENT (Cursor/Claude)      │
                  └──────────────────┬─────────────────────┘
                                     │ (MCP / CLI)
                  ┌──────────────────▼─────────────────────┐
                  │                AgentOS                 │
                  └──────┬───────────┬──────────────┬──────┘
                         │           │              │
           ┌─────────────▼─────┐┌────▼────────┐┌────▼─────────────┐
           │   HYBRID MEMORY   ││ GOVERNANCE  ││   SELF-HEALING   │
           │ SQLite FTS5 + Graph││ Policy Gate ││ Log Correlation │
           └───────────────────┘└─────────────┘└──────────────────┘
```

---

## ⚡ The Value Proposition

| Feature | Standard AI Agent | AgentOS-Empowered Agent |
| :--- | :--- | :--- |
| **Context Retention** | Single-session, forgets past file paths & fixes | Hybrid FTS5 + Entity Relationship Knowledge Graph |
| **Execution Safety** | Runs arbitrary commands blindly (dangerous) | Pre-command gatekeeper matching your security policy |
| **Continuous Learning**| Repeats identical errors and loops infinitely | Failure correlation mining + active self-healing hints |
| **State Tracking** | Manual git commits (or none) | Auto-verified Git checkpoints after successful quality gates |

---

## 🛠️ The Agentic Loop

AgentOS organizes the agent's behavior into a structured, continuous reinforcement loop:

```mermaid
graph TD
    A["Initialize Context (/task)"] --> B["Memory Recall (/recall)"]
    B --> C["Shadow-Trace Commands (tracer.py)"]
    C --> D["Auto-Heal on Failures (self_heal.py)"]
    D --> E["Mine Logs for Lessons (/dream)"]
    E --> F["Evaluate & Evolve Skills (/graduate)"]
    F --> G["Run Quality & Lint Gates (/verify)"]
    G --> H["Git-Checkpoint State (/checkpoint)"]
    H --> A
```

---

## 🚀 Installation & Setup

### 1. Install the Antigravity Plugin (CLI/IDE Orchestration)
If you are developing inside Google Antigravity (or an Antigravity-supported CLI/IDE), install the plugin to expose the global MCP Server and execution hook policies:

* **Locate the plugin folder:** Ensure the `plugin/` directory in this repository is accessible.
* **Copy to your global plugin directory:**
  * **macOS / Linux:** Copy the `plugin/` directory to `~/.gemini/config/plugins/uall-plugin/`
  * **Windows:** Copy the `plugin/` directory to `C:\Users\<username>\.gemini\config\plugins\uall-plugin\` (e.g., `C:\Users\Johnny Cage\.gemini\config\plugins\uall-plugin\`)
* **Restart the Agent:** Restart your Antigravity CLI or reload your IDE window to register the new plugin configurations.

Once installed:
* Global pre-command safety checks defined in `hooks.json` will intercept commands.
* The global `uall-server` MCP toolset becomes available.

---

### 2. Bootstrap your Project (Deploying the Template)
To run AgentOS inside any codebase workspace:

* **Option A: Run the MCP Server Tool (Easiest)**
  If you have the Antigravity plugin installed and connected, your agent can bootstrap the project directly by calling the `uall_bootstrap` tool. Just tell your agent:
  > *"Please bootstrap this project with AgentOS"*
* **Option B: Run the Bootstrap Script**
  Copy `uall_bootstrap.py` and `uall.py` to your target project root and run:
  ```bash
  python uall_bootstrap.py
  ```
  This creates the local `.agent/` directory skeleton, generates configuration stubs, and initializes Git.
* **Option C: Deploy via Master Installer (Optional)**
  Deploy the full pre-configured template package to a target directory:
  ```bash
  python uall_master_installer.py /path/to/target/project
  ```

---

### 3. Setup the IDE Integration (MCP Server)
AgentOS exposes a local Model Context Protocol (MCP) server so Cursor, Claude Desktop, or VSCode can access its tools natively. 

Add this to your IDE's MCP settings:
```json
{
  "mcpServers": {
    "agent-os": {
      "command": "python",
      "args": [".agent/tools/mcp_server.py"],
      "cwd": "."
    }
  }
}
```
*(For detailed setup and configurations, see [MCP_SETUP.md](file:///C:/Users/Johnny%20Cage/Projects/UALL-Antigravity/MCP_SETUP.md))*

---

## 📋 Daily Workflow Guide

Once set up, run commands via `uall.py` inside your project root to manage your AI agent:

### 1. Initialize Task Context
Before the agent starts, link the workspace to a specific task ticket (e.g. Jira, Linear, or GitHub issues):
```bash
python uall.py /task TASK-101
```

### 2. Recall Project Memory
Have the agent search semantic history, entity relations, and active failure-avoidance hints before writing code:
```bash
python uall.py /recall "JWT auth verification logic"
```

### 3. Shadow-Trace Commands
Wrap every shell command (like compiling, linting, or package installations) using `tracer.py` so AgentOS can log metrics, track files, and intercept errors:
```bash
python .agent/tools/tracer.py "npm install"
```

### 4. Auto-Heal Failures
If commands fail, run healing to analyze episodic tracebacks and auto-generate context-aware active hints:
```bash
python uall.py /heal
```

### 5. Run Quality & Security Gates
Validate your code changes before committing. This runs Semgrep security checks, Ruff formatting rules, and Pytest suites:
```bash
python uall.py /verify
```

### 6. Git-Checkpoint verified State
Once `/verify` returns `VALID`, unlock and save your current progress with a Git-signed checkpoint commit:
```bash
python uall.py /checkpoint "Initial auth implementation"
```
*(If an agent breaks your code, roll back instantly using `python uall.py /recover`)*

---

## 📦 Architecture & Directory Layout

AgentOS operates entirely locally within a portable `.agent/` directory:

```
.agent/
├── GOVERNANCE.md          # Security policy, risk tiers, & capability grants
├── PLAYBOOK.md            # Auto-generated knowledge-base from graduated lessons
├── AGENTS.md              # Role definitions & standard operating procedures
├── memory/
│   ├── episodic/          # Per-day JSONL event logs captured during commands
│   ├── candidate_lessons/ # Proposed learnings awaiting graduation
│   ├── graduated/         # LESSONS.md + LESSONS.jsonl (the source of truth)
│   ├── graph/             # entities.md + relationships.jsonl knowledge graph
│   └── .index/            # SQLite FTS5 search index database
├── skills/
│   ├── core/              # Built-in system instructions
│   ├── domain/            # Graduated project-specific skills
│   └── pending/           # Staged skills awaiting human review
├── protocols/
│   ├── semgrep_rules.yaml # Static security & structural checks
│   ├── hook_patterns.json # Event-driven pre/post tool hooks
│   └── self_healing_hints.md # Dynamic hints built from command failures
└── tools/                 # Python engine scripts (verify, recall, self_heal, etc.)
```

---

## 💎 Key Features

### 🧠 1. Hybrid Semantic & Graph Memory
Standard search is not enough. AgentOS combines **SQLite FTS5 full-text indexing** with an **Entity-Relationship Knowledge Graph** to trace code dependencies, previous refactorings, and file mappings.
* `/recall <query>` queries both lexical indices and code relationships to construct a hyper-relevant context.

### 🛡️ 2. Pre-Command Governance
Protect your environment. When your agent attempts to execute a terminal command (e.g., `git`, `docker`, `rm`), the AgentOS pre-tool hook interceptor validates the command against [.agent/GOVERNANCE.md](file:///C:/Users/Johnny%20Cage/Projects/UALL-Antigravity/.agent/GOVERNANCE.md).
* Auto-approves safe commands (Tier 1).
* Prompts or logs medium-risk activities (Tier 2).
* Blocks high-risk or unauthorized commands (Tier 3) until approved.

### 🩹 3. Self-Healing Failures
When a task fails, `tracer.py` captures the traceback and exit code. `self_heal.py` correlates recurring failures to write active hints in [protocols/self_healing_hints.md](file:///C:/Users/Johnny%20Cage/Projects/UALL-Antigravity/.agent/protocols/self_healing_hints.md), which are automatically injected into the agent's context next time it attempts a similar command.

### 💾 4. Verified Checkpoint & Recovery
Never let an agent break your code.
* `/verify` runs Semgrep rules, Ruff checks, and pytest suites.
* On success, it unlocks `/checkpoint "<msg>"` which creates a Git-signed snapshot of the code and agent memory.
* If the agent goes off the rails, `/recover` instantly rolls back the codebase and brain state to the last verified checkpoint.

---

> [!IMPORTANT]
> **AgentOS** is completely open-source, local-first, and contains no external API dependencies. All memory, database indices, and event logs are stored directly in your codebase's `.agent/` folder.

---

## 🌟 Support & Contributions

Give us a star ⭐ if this project helps you build better agents! Contributions, bug reports, and suggestions are welcome.
