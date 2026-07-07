# Code Review Style Guide — mcp-memory-os

## UALL Safety Constraints
- Flag any direct writes to `.agent/tools/` without a `gate.py` call
- Flag any shell commands not wrapped in `tracer.py`
- Flag any git commits not preceded by a `/verify` run
- Flag hardcoded secrets or API keys

## Project Standards
<!-- Fill in: language style, test coverage requirements, etc. -->
