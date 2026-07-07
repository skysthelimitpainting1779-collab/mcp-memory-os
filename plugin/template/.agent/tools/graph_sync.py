#!/usr/bin/env python3
"""
graph_sync.py — Temporal Knowledge Graph builder.
Scans the project for files, classes, and imports; emits entities.md + relationships.jsonl.
Configurable via --scan-dirs (defaults to src, app, lib, tests, pages, components).
"""
import os
import json
import datetime
import subprocess
import ast
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _agent_utils import find_project_root, agent_dir, run_git

ROOT = find_project_root()
AGENT = agent_dir(ROOT)

GRAPH_ENTITIES   = AGENT / "memory" / "graph" / "entities.md"
GRAPH_RELATIONS  = AGENT / "memory" / "graph" / "relationships.jsonl"

HAS_GRAPHIFY = False
try:
    import graphify
    HAS_GRAPHIFY = True
except ImportError:
    pass

# Directories that should never be scanned
SKIP_DIRS = {".agent", ".git", "__pycache__", "node_modules", ".next",
             "dist", "build", ".vercel", "coverage", ".pytest_cache", "venv", ".venv"}

# Default scan targets — non-existent dirs are silently skipped
DEFAULT_SCAN_TARGETS = ["src", "app", "lib", "tests", "pages",
                        "components", "api", "utils", "hooks", "services"]


class TemporalGraphEngine:
    def __init__(self, root: Path, scan_dirs: list[str]):
        self.root = root
        self.scan_dirs = scan_dirs
        self.entities: dict[str, dict] = {}
        self.relations: list[dict] = []

    def get_git_metadata(self, file_path: Path) -> tuple[str, str]:
        try:
            out = run_git(["log", "-1", "--format=%H|%ai", "--", str(file_path)], cwd=self.root)
            if out:
                commit_hash, _, timestamp = out.partition("|")
                return commit_hash, timestamp
        except Exception:
            pass
        return "untracked", datetime.datetime.now().isoformat()

    def ent_id(self, path: Path) -> str:
        rel = path.relative_to(self.root)
        return "ENT-" + str(rel).replace(os.sep, "-").replace("/", "-")

    def scan_file(self, file_path: Path) -> None:
        ent_id = self.ent_id(file_path)
        commit, ts = self.get_git_metadata(file_path)
        entity = {
            "id": ent_id,
            "type": "file",
            "name": str(file_path.relative_to(self.root)),
            "last_commit": commit,
            "updated_at": ts,
            "ext": file_path.suffix,
        }
        self.entities[ent_id] = entity

        if file_path.suffix == ".py":
            self._parse_python(file_path, ent_id)
        elif file_path.suffix in (".ts", ".tsx", ".js", ".jsx"):
            self._parse_js_imports(file_path, ent_id)

    def _parse_python(self, file_path: Path, parent_id: str) -> None:
        try:
            tree = ast.parse(file_path.read_text(errors="replace"))
        except SyntaxError:
            return

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_id = f"{parent_id}-{node.name}"
                self.entities[class_id] = {
                    "id": class_id,
                    "type": "class",
                    "name": node.name,
                    "parent": parent_id,
                }
                self.relations.append({
                    "subject_id": class_id,
                    "predicate": "defined_in",
                    "object_id": parent_id,
                })
            elif isinstance(node, ast.FunctionDef) and not isinstance(
                getattr(node, "parent_node", None), ast.ClassDef
            ):
                fn_id = f"{parent_id}-fn-{node.name}"
                self.entities[fn_id] = {
                    "id": fn_id,
                    "type": "function",
                    "name": node.name,
                    "parent": parent_id,
                }
            elif isinstance(node, ast.ImportFrom) and node.module:
                target_id = "ENT-" + node.module.replace(".", "-")
                self.relations.append({
                    "subject_id": parent_id,
                    "predicate": "imports",
                    "object_id": target_id,
                })

    def _parse_js_imports(self, file_path: Path, parent_id: str) -> None:
        """Simple regex-free import extraction for TS/JS files."""
        try:
            text = file_path.read_text(errors="replace")
        except OSError:
            return
        for line in text.splitlines():
            line = line.strip()
            if line.startswith("import ") and " from " in line:
                _, _, module = line.partition(" from ")
                module = module.strip().strip("'\"").strip(";")
                if module and not module.startswith("."):
                    target_id = "ENT-npm-" + module.split("/")[0].lstrip("@")
                else:
                    target_id = "ENT-" + module.replace("/", "-").lstrip(".")
                self.relations.append({
                    "subject_id": parent_id,
                    "predicate": "imports",
                    "object_id": target_id,
                })

    def sync(self) -> None:
        scanned = 0
        use_fallback = True

        if HAS_GRAPHIFY:
            print("🚀 Graphifyy detected! Running deep AST/semantic extraction...")
            try:
                cmd = [sys.executable, "-m", "graphify", "extract", ".", "--no-cluster"]
                subprocess.run(cmd, capture_output=True, text=True, cwd=str(self.root))
                
                graph_json_path = self.root / "graphify-out" / "graph.json"
                if graph_json_path.exists():
                    with open(graph_json_path, encoding="utf-8") as f:
                        data = json.load(f)
                    
                    self.entities.clear()
                    self.relations.clear()
                    
                    for node in data.get("nodes", []):
                        node_id = node.get("id")
                        if not node_id:
                            continue
                        self.entities[node_id] = {
                            "id": node_id,
                            "type": node.get("file_type", "symbol"),
                            "name": node.get("label", ""),
                            "source_file": node.get("source_file", ""),
                            "source_location": node.get("source_location", ""),
                        }
                        
                    for edge in data.get("edges", []):
                        self.relations.append({
                            "subject_id": edge.get("source", ""),
                            "predicate": edge.get("relation", "connects"),
                            "object_id": edge.get("target", ""),
                        })
                    
                    scanned = len(set(node.get("source_file") for node in data.get("nodes", []) if node.get("source_file")))
                    use_fallback = False
                    print("✅ Graphifyy extraction parsed successfully.")
                else:
                    print("⚠️  Graphifyy output graph.json not found. Falling back to local scanner...")
            except Exception as e:
                print(f"⚠️  Graphifyy extraction failed: {e}. Falling back to local scanner...")

        if use_fallback:
            for target in self.scan_dirs:
                target_path = self.root / target
                if not target_path.exists():
                    continue
                for fpath in target_path.rglob("*"):
                    if fpath.is_file() and not any(skip in fpath.parts for skip in SKIP_DIRS):
                        self.scan_file(fpath)
                        scanned += 1

        # Write entities
        GRAPH_ENTITIES.parent.mkdir(parents=True, exist_ok=True)
        with open(GRAPH_ENTITIES, "w", encoding="utf-8") as f:
            f.write("# Temporal Knowledge Graph: Entities\n\n")
            for eid, data in self.entities.items():
                f.write(f"---\n{json.dumps(data, indent=2)}\n---\n\n")

        # Write relationships (deduplicated)
        seen = set()
        unique_rels = []
        for rel in self.relations:
            key = (rel["subject_id"], rel["predicate"], rel["object_id"])
            if key not in seen:
                seen.add(key)
                unique_rels.append(rel)

        with open(GRAPH_RELATIONS, "w", encoding="utf-8") as f:
            for rel in unique_rels:
                f.write(json.dumps(rel) + "\n")

        print(f"✅ Graph Sync complete.")
        print(f"   {len(self.entities)} entities | {len(unique_rels)} relationships | {scanned} files scanned")
        if use_fallback:
            print(f"   Scan roots: {[d for d in self.scan_dirs if (self.root / d).exists()]}")
        else:
            print(f"   Scan source: parsed from Graphifyy graph.json")


def main():
    parser = argparse.ArgumentParser(description="UALL Temporal Graph Sync")
    parser.add_argument(
        "--scan-dirs",
        nargs="+",
        default=DEFAULT_SCAN_TARGETS,
        help="Directories to scan (relative to project root)",
    )
    args = parser.parse_args()

    print(f"🕸️  UALL Graph Sync: {ROOT}")
    engine = TemporalGraphEngine(ROOT, args.scan_dirs)
    engine.sync()


if __name__ == "__main__":
    main()
