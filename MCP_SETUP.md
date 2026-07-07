# 🔌 AgentOS Model Context Protocol (MCP) Server Setup

Equip Claude Desktop, Cursor, VSCode, or any MCP-compatible IDE with **AgentOS** tools natively. By exposing the agent's memory and governance features as MCP tools, the agent can search its own database, evaluate safety policies, and auto-heal tracebacks in real-time.

---

## ⚡ Quick Prerequisites

Before connecting the server, install the Model Context Protocol SDK:

```bash
pip install mcp
```

---

## 💻 IDE Configuration Examples

### 1. Claude Desktop (macOS / Linux / Windows)
Add the following configuration to your `claude_desktop_config.json`:

* **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
* **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`
* **Linux:** `~/.config/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "agent-os": {
      "command": "python",
      "args": ["/absolute/path/to/your/project/.agent/tools/mcp_server.py"],
      "cwd": "/absolute/path/to/your/project"
    }
  }
}
```

### 2. Cursor IDE
1. Open Cursor Settings -> **Features** -> **MCP**.
2. Click **+ Add New MCP Server**.
3. Fill in the parameters:
   - **Name:** `agent-os`
   - **Type:** `command`
   - **Command:** `python .agent/tools/mcp_server.py`
4. Click **Save**.

---

## 🛠️ Available MCP Tools

Once connected, your AI assistant will gain access to the following capabilities:

| Tool Name | CLI Equivalent | Description |
| :--- | :--- | :--- |
| `uall_recall` | `/recall` | Queries FTS5 full-text index & knowledge graph context |
| `uall_status` | `/status` | Fetches agent brain health metrics, log counts, & status |
| `uall_gate` | `gate.py` | Validates command execution requests against local GOVERNANCE.md |
| `uall_checkpoint`| `/checkpoint`| Stately Git-commits verified codebase and agent brain states |
| `uall_recover` | `/recover` | Restores files and memory index to HEAD or a specific hash |
| `uall_index` | `/index` | Performs incremental rebuilt of the lexical database |
| `uall_dream` | `/dream` | Runs correlation mining on error tracebacks for new lessons |
| `uall_graduate` | `/graduate` | Promotes approved candidate skills/lessons to production rules |
| `uall_self_heal` | `/heal` | Writes failure tracebacks into active self-healing hints |
| `uall_report` | `/report` | Generates a Markdown intelligence report of completed tasks |

---

> [!NOTE]
> The MCP server dynamically checks your active working directory. If no local `.agent/` folder is present, it will fallback to the directory where the tool is running, allowing you to bootstrap UALL directly from the IDE.
