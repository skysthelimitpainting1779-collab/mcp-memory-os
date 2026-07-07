---
applyTo: '**/*.py'
---
# Python File Rules (UALL)
- Wrap every subprocess/shell call: `python .agent/tools/tracer.py "<cmd>"`
- Never import from `.agent/tools/` directly — call via uall.py commands
- Add UTF-8 encoding to all file open() calls
