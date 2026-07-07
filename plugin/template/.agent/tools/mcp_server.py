#!/usr/bin/env python3
"""
mcp_server.py — UALL MCP Server.
Exposes UALL tools to Claude Desktop, Cursor, and any MCP-compatible IDE.

Setup (add to your mcp_settings.json):
{
  "mcpServers": {
    "uall": {
      "command": "python3",
      "args": ["/path/to/your/project/.agent/tools/mcp_server.py"],
      "cwd": "/path/to/your/project"
    }
  }
}
"""
import subprocess
import sys
import os
from pathlib import Path

# Try importing fastmcp; give a helpful error if not installed
try:
    from mcp.server.fastmcp import FastMCP
except ImportError:
    print("FastMCP not installed. Run: pip install mcp", file=sys.stderr)
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir

ROOT  = find_project_root()
AGENT = agent_dir(ROOT)
mcp   = FastMCP("UALL")


def run_tool(script_name: str, *args: str) -> str:
    script_path = AGENT / "tools" / script_name
    if not script_path.exists():
        return f"Error: Tool {script_name} not found at {script_path}"
    cmd = [sys.executable, str(script_path)] + list(args)
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60, cwd=str(ROOT))
        out = result.stdout.strip()
        err = result.stderr.strip()
        return f"{out}\n{err}".strip() if err and result.returncode != 0 else out
    except subprocess.TimeoutExpired:
        return f"Error: {script_name} timed out after 60s"
    except Exception as e:
        return f"Error running {script_name}: {e}"


@mcp.tool()
def uall_recall(task: str, limit: int = 5) -> str:
    """Search UALL memory for context relevant to a task description."""
    return run_tool("recall.py", "--task", task, "--limit", str(limit))


@mcp.tool()
def uall_status() -> str:
    """Get UALL brain health: log count, pending skills, graduated lessons."""
    return run_tool("../../../uall.py") if (ROOT / "uall.py").exists() else "Run /status from uall.py"


@mcp.tool()
def uall_gate(action_type: str, payload: str) -> str:
    """Check if an exec/write/delete action is permitted by UALL governance."""
    return run_tool("gate.py", action_type, payload)


@mcp.tool()
def uall_checkpoint(message: str) -> str:
    """Create a git-backed checkpoint of .agent/ memory (requires prior /verify)."""
    return run_tool("recover.py", "checkpoint", message)


@mcp.tool()
def uall_recover(version: str = "") -> str:
    """Restore .agent/ to HEAD or a specific commit hash."""
    args = ["recover", "--version", version] if version else ["recover"]
    return run_tool("recover.py", *args)


@mcp.tool()
def uall_index(force: bool = False) -> str:
    """Rebuild the FTS5 memory search index (pass force=True for full rebuild)."""
    return run_tool("index_memory.py", "--force" if force else "")


@mcp.tool()
def uall_dream() -> str:
    """Run correlation mining on episodic logs to scaffold candidate lessons."""
    return run_tool("auto_dream.py")


@mcp.tool()
def uall_graduate() -> str:
    """Promote high-confidence candidate lessons and approved skills to production."""
    return run_tool("graduate.py")


@mcp.tool()
def uall_self_heal() -> str:
    """Analyze failure patterns and write self-healing hints."""
    return run_tool("self_heal.py")


@mcp.tool()
def uall_sync_graph() -> str:
    """Rebuild the temporal knowledge graph from source files."""
    return run_tool("graph_sync.py")


@mcp.tool()
def uall_enhance() -> str:
    """Detect repeated command patterns and scaffold skill proposals."""
    return run_tool("enhance.py")


@mcp.tool()
def uall_report() -> str:
    """Generate an intelligence report for the currently active task."""
    return run_tool("report.py")


@mcp.tool()
def uall_task(task_id: str, source: str = "linear") -> str:
    """Initialize task context from Linear or GitHub."""
    return run_tool("task_bridge.py", task_id, source)


@mcp.tool()
def uall_bootstrap() -> str:
    """Bootstrap the current workspace with the mcp-memory-os structure, Git hooks, and IDE rules."""
    plugin_root = Path(__file__).resolve().parent.parent
    template_dir = plugin_root / "template"
    if not template_dir.exists():
        return f"Error: Template directory not found at {template_dir}"
    
    target_dir = Path.cwd()
    import shutil
    try:
        items = [".agent", "uall.py", ".cursorrules", ".clinerules", "README.md"]
        deployed = []
        for item in items:
            src = template_dir / item
            dst = target_dir / item
            if not src.exists():
                continue
            if src.is_dir():
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            deployed.append(item)
        
        # Git init if needed
        import subprocess
        git_init_msg = ""
        if not (target_dir / ".git").exists():
            res = subprocess.run(["git", "init"], cwd=str(target_dir), capture_output=True, text=True)
            if res.returncode == 0:
                git_init_msg = " [git initialized]"
            else:
                git_init_msg = f" [git init failed: {res.stderr.strip()}]"
        
        # Install graphifyy package if missing, upgrade skill, and install hooks/IDE rules
        graphify_msg = ""
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "graphifyy"], cwd=str(target_dir), capture_output=True)
            subprocess.run([sys.executable, "-m", "graphify", "install"], cwd=str(target_dir), capture_output=True)
            subprocess.run([sys.executable, "-m", "graphify", "hook", "install"], cwd=str(target_dir), capture_output=True)
            subprocess.run([sys.executable, "-m", "graphify", "cursor", "install"], cwd=str(target_dir), capture_output=True)
            subprocess.run([sys.executable, "-m", "graphify", "claude", "install"], cwd=str(target_dir), capture_output=True)
            subprocess.run([sys.executable, "-m", "graphify", "antigravity", "install"], cwd=str(target_dir), capture_output=True)
            graphify_msg = " [Graphifyy package, Git hooks, and IDE rules successfully configured]"
        except Exception as ge:
            graphify_msg = f" [Graphifyy config failed: {ge}]"
            
        # Initial memory index
        index_script = target_dir / ".agent" / "tools" / "index_memory.py"
        if index_script.exists():
            subprocess.run([sys.executable, str(index_script)], cwd=str(target_dir), capture_output=True)
        
        return f"Success: Bootstrapped project at {target_dir} with {', '.join(deployed)}{git_init_msg}{graphify_msg}."
    except Exception as e:
        return f"Error bootstrapping project: {e}"



@mcp.tool()
def uall_graphify(action: str = "extract", query: str = "") -> str:
    """Run Graphifyy structural codebase operations.
    
    action: "extract" (headless AST mapping), "query" (BFS graph traversal),
            "affected" (impact analysis), "tree" (D3 collapsible tree HTML),
            "callflow" (Mermaid call-flow HTML)
    query: the search phrase or symbol name for query/affected actions.
    """
    args = []
    if action == "extract":
        args = ["--extract"]
    elif action == "query":
        if not query:
            return "Error: query parameter required for query action."
        args = ["--query", query]
    elif action == "affected":
        if not query:
            return "Error: query parameter required for affected action."
        args = ["--affected", query]
    elif action == "tree":
        args = ["--tree"]
    elif action == "callflow":
        args = ["--callflow"]
    else:
        return f"Error: unknown action: {action}"
        
    return run_tool("graphify_bridge.py", *args)


@mcp.tool()
def uall_graph_node(label: str) -> str:
    """Get full details for a specific graph node by label or ID."""
    return run_tool("graphify_bridge.py", "--node", label)


@mcp.tool()
def uall_graph_neighbors(label: str) -> str:
    """Get all direct neighbors of a graph node with edge details."""
    return run_tool("graphify_bridge.py", "--neighbors", label)


@mcp.tool()
def uall_graph_community(community_id: int) -> str:
    """Get all nodes in a specific community by community ID."""
    return run_tool("graphify_bridge.py", "--community", str(community_id))


@mcp.tool()
def uall_graph_gods(top_n: int = 10) -> str:
    """Return the most connected nodes (core abstractions) in the graph."""
    return run_tool("graphify_bridge.py", "--gods", str(top_n))


@mcp.tool()
def uall_graph_stats() -> str:
    """Return summary statistics of the codebase knowledge graph."""
    return run_tool("graphify_bridge.py", "--stats")


@mcp.tool()
def uall_graph_explain(label: str) -> str:
    """Return a plain-language explanation of a concept node using Graphifyy."""
    return run_tool("graphify_bridge.py", "--explain", label)


@mcp.tool()
def uall_graph_path(source: str, target: str) -> str:
    """Find the shortest path between two concepts in the knowledge graph."""
    return run_tool("graphify_bridge.py", "--path", source, target)


if __name__ == "__main__":
    mcp.run()

