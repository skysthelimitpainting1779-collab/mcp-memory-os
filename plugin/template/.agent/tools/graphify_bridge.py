#!/usr/bin/env python3
"""
graphify_bridge.py — Bridge wrapper for the graphifyy library.
"""
import sys
import subprocess
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root

ROOT = find_project_root()


def run_graphify(*args: str) -> str:
    cmd = [sys.executable, "-m", "graphify"] + list(args)
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT))
        out = res.stdout.strip()
        err = res.stderr.strip()
        if res.returncode != 0:
            return f"❌ Graphifyy Error:\n{out}\n{err}".strip()
        return out
    except Exception as e:
        return f"❌ Execution error: {e}"


def load_graph_data():
    import json
    path = ROOT / "graphify-out" / "graph.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def get_node(label: str) -> str:
    data = load_graph_data()
    if not data:
        return "Error: graph.json not found. Run /graphify first."
    label_lower = label.lower()
    for n in data.get("nodes", []):
        nid = str(n.get("id", ""))
        nlabel = str(n.get("label", ""))
        if label_lower in nid.lower() or label_lower in nlabel.lower():
            lines = [
                f"Node: {nlabel}",
                f"  ID: {nid}",
                f"  Source: {n.get('source_file', '')} {n.get('source_location', '')}",
                f"  Type: {n.get('file_type', '')}",
                f"  Community: {n.get('community_name') or n.get('community', '')}"
            ]
            return "\n".join(lines)
    return f"No node matching '{label}' found."


def get_neighbors(label: str) -> str:
    data = load_graph_data()
    if not data:
        return "Error: graph.json not found. Run /graphify first."
    label_lower = label.lower()
    target_id = None
    target_label = None
    for n in data.get("nodes", []):
        nid = str(n.get("id", ""))
        nlabel = str(n.get("label", ""))
        if label_lower in nid.lower() or label_lower in nlabel.lower():
            target_id = nid
            target_label = nlabel
            break
            
    if not target_id:
        return f"No node matching '{label}' found."
        
    lines = [f"Neighbors of {target_label}:"]
    for link in (data.get("links") or data.get("edges") or []):
        src = str(link.get("source", ""))
        tgt = str(link.get("target", ""))
        rel = link.get("relation", "")
        conf = link.get("confidence", "")
        if src == target_id:
            nb_label = next((n.get("label", tgt) for n in data.get("nodes", []) if n.get("id") == tgt), tgt)
            lines.append(f"  --> {nb_label} [{rel}] [{conf}]")
        elif tgt == target_id:
            nb_label = next((n.get("label", src) for n in data.get("nodes", []) if n.get("id") == src), src)
            lines.append(f"  <-- {nb_label} [{rel}] [{conf}]")
    return "\n".join(lines)


def get_community(community_id: int) -> str:
    data = load_graph_data()
    if not data:
        return "Error: graph.json not found. Run /graphify first."
    lines = []
    comm_name = None
    nodes_in_comm = []
    for n in data.get("nodes", []):
        cid = n.get("community")
        if cid is not None and int(cid) == community_id:
            nodes_in_comm.append(n)
            if not comm_name:
                comm_name = n.get("community_name")
                
    if not nodes_in_comm:
        return f"Community {community_id} not found or empty."
        
    lines.append(f"Community {community_id} ({comm_name or 'unnamed'}) ({len(nodes_in_comm)} nodes):")
    for n in nodes_in_comm:
        lines.append(f"  {n.get('label', n.get('id'))} [{n.get('source_file', '')}]")
    return "\n".join(lines)


def god_nodes(top_n: int = 10) -> str:
    data = load_graph_data()
    if not data:
        return "Error: graph.json not found. Run /graphify first."
    from collections import Counter
    degrees = Counter()
    for link in (data.get("links") or data.get("edges") or []):
        degrees[link.get("source")] += 1
        degrees[link.get("target")] += 1
        
    top = degrees.most_common(top_n)
    lines = ["God nodes (most connected):"]
    for i, (nid, deg) in enumerate(top, 1):
        nlabel = next((n.get("label", nid) for n in data.get("nodes", []) if n.get("id") == nid), nid)
        lines.append(f"  {i}. {nlabel} - {deg} edges")
    return "\n".join(lines)


def graph_stats() -> str:
    data = load_graph_data()
    if not data:
        return "Error: graph.json not found. Run /graphify first."
    nodes = len(data.get("nodes", []))
    edges = len(data.get("links") or data.get("edges") or [])
    comms = len(set(n.get("community") for n in data.get("nodes", []) if n.get("community") is not None))
    return f"Nodes: {nodes}\nEdges: {edges}\nCommunities: {comms}"


def main():
    parser = argparse.ArgumentParser(description="Graphifyy Bridge")
    parser.add_argument("--query", type=str, help="BFS query on the codebase graph")
    parser.add_argument("--affected", type=str, help="Impact analysis for a node/symbol")
    parser.add_argument("--tree", action="store_true", help="Generate interactive collapsible D3 tree")
    parser.add_argument("--callflow", action="store_true", help="Export call-flow graph HTML")
    parser.add_argument("--extract", action="store_true", help="Run full code extraction")
    
    # Exposing serve.py-equivalent query commands
    parser.add_argument("--node", type=str, help="Get node details")
    parser.add_argument("--neighbors", type=str, help="Get node neighbors")
    parser.add_argument("--community", type=int, help="Get nodes in community ID")
    parser.add_argument("--gods", type=int, nargs="?", const=10, help="Get top God nodes")
    parser.add_argument("--stats", action="store_true", help="Get graph statistics")
    parser.add_argument("--explain", type=str, help="Explain node concept")
    parser.add_argument("--path", type=str, nargs=2, metavar=("SRC", "TGT"), help="Get shortest path between two concepts")
    
    args, unknown = parser.parse_known_args()

    if args.extract:
        print("🔍 Extracting codebase structure via Graphifyy...")
        print(run_graphify("extract", ".", "--no-cluster"))
    elif args.query:
        print(run_graphify("query", args.query))
    elif args.affected:
        print(run_graphify("affected", args.affected))
    elif args.tree:
        print("🌳 Generating collapsible graph tree...")
        print(run_graphify("tree"))
    elif args.callflow:
        print("🗺️ Exporting callflow mapping...")
        print(run_graphify("export", "callflow-html"))
    elif args.node:
        print(get_node(args.node))
    elif args.neighbors:
        print(get_neighbors(args.neighbors))
    elif args.community is not None:
        print(get_community(args.community))
    elif args.gods is not None:
        print(god_nodes(args.gods))
    elif args.stats:
        print(graph_stats())
    elif args.explain:
        print(run_graphify("explain", args.explain))
    elif args.path:
        print(run_graphify("path", args.path[0], args.path[1]))
    else:
        # Default fallback
        print("🔍 Extracting codebase structure via Graphifyy...")
        print(run_graphify("extract", ".", "--no-cluster"))


if __name__ == "__main__":
    main()
