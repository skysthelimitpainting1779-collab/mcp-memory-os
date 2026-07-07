## graphify

This project has a knowledge graph at graphify-out/ with god nodes, community structure, and cross-file relationships.

Rules:
- For codebase questions, first run `graphify query "<question>"` when graphify-out/graph.json exists. Use `graphify path "<A>" "<B>"` for relationships and `graphify explain "<concept>"` for focused concepts. These return a scoped subgraph, usually much smaller than GRAPH_REPORT.md or raw grep output.
- If graphify-out/wiki/index.md exists, use it for broad navigation instead of raw source browsing.
- Read graphify-out/GRAPH_REPORT.md only for broad architecture review or when query/path/explain do not surface enough context.
- After modifying code, run `graphify update .` to keep the graph current (AST-only, no API cost).

## UALL & mcp-memory-os Rules
- At startup, read [.agent/AGENTS.md](file:///c:/Users/Johnny%20Cage/Projects/mcp-memory-os/.agent/AGENTS.md) to load active profile guidelines and commands.
- Run `python uall.py /recall "<keywords>"` before starting code edits to retrieve memory context.
- Reference [.agent/spec/design.md](file:///c:/Users/Johnny%20Cage/Projects/mcp-memory-os/.agent/spec/design.md) for architecture design and `.agent/spec/tasks/` for task scope.
- Check [.agent/PLAYBOOK.md](file:///c:/Users/Johnny%20Cage/Projects/mcp-memory-os/.agent/PLAYBOOK.md) for graduated codebase lessons.
- Respect file permissions in [.agent/GOVERNANCE.md](file:///c:/Users/Johnny%20Cage/Projects/mcp-memory-os/.agent/GOVERNANCE.md) and check `python .agent/tools/gate.py write <file_path>` before writing files.
- Run all terminal commands via `python .agent/tools/tracer.py "<command>"`.
- Commit progress via `python uall.py /checkpoint "<message>"` (requires a passing `/verify` first).
