# UALL MCP Server Setup

Connect UALL tools directly to Claude Desktop, Cursor, or any MCP-compatible IDE.

## Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "uall": {
      "command": "python3",
      "args": ["/absolute/path/to/your/project/.agent/tools/mcp_server.py"],
      "cwd": "/absolute/path/to/your/project"
    }
  }
}
```

## Prerequisites

```bash
pip install mcp
```

## Available MCP Tools

| Tool | Description |
| :--- | :--- |
| `uall_recall` | Hybrid FTS + graph memory search |
| `uall_task` | Initialize task context from Linear/GitHub |
| `uall_gate` | Check governance approval for an action |
| `uall_checkpoint` | Git-commit .agent/ state |
| `uall_recover` | Restore .agent/ to HEAD or a commit |
| `uall_index` | Rebuild the FTS5 search index |
| `uall_dream` | Mine failure correlations |
| `uall_graduate` | Promote candidates to Playbook |
| `uall_self_heal` | Write self-healing hints from failures |
| `uall_sync_graph` | Rebuild knowledge graph |
| `uall_enhance` | Scaffold skill proposals |
| `uall_report` | Generate task intelligence report |
