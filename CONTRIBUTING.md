# Contributing to mcp-memory-os

Thank you for your interest in contributing to **mcp-memory-os**! Contributions from the developer community help make this a more robust and capable agentic tool.

---

## 📋 Ways to Contribute

1. **Reporting Bugs:** Create an issue describing the bug, including steps to reproduce, agent environment details, and tracelogs from `.agent/memory/episodic/`.
2. **Feature Requests:** Open an issue proposing new capabilities (e.g. support for new IDE configurations, new verification rules, or hooks).
3. **Submitting Pull Requests:** We welcome fixes, documentation updates, and new features.

---

## 🛠️ Local Development & Testing

To set up a local workspace for developing or testing mcp-memory-os:

1. **Fork and Clone** this repository.
2. **Create a local virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt  # If any
   pip install mcp ruff pytest semgrep
   ```
3. **Execute local verification:**
   Make sure all code matches linting and verification gates before staging commits:
   ```bash
   python uall.py /verify
   ```

---

## 📥 Submitting a PR

1. **Keep it DRY:** Ensure your changes do not introduce file duplication. The core template files are stored exclusively inside `plugin/template/`.
2. **Follow style guidelines:** Ensure `ruff check` passes.
3. **Write tests:** If you add new logic to tools in `plugin/template/.agent/tools/`, include a test in a local test suite if possible.
4. **Link tickets:** Use `/task <ID>` or reference issue numbers in your commit messages.

We review pull requests regularly. Thank you for contributing!
