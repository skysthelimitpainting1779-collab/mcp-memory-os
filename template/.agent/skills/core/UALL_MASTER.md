# Skill: UALL V4 Operational Mastery
## Trigger
When an agent needs to persist changes to the repository or verify the integrity of the professional-scoped brain.

## Procedure
1. **Recall**: Run `/recall` to fetch domain-specific constraints.
2. **Execute**: Perform the task via `tracer.py` to ensure anomaly capture.
3. **Verify**: Run `/verify`. This triggers:
   - **Semgrep**: Checks for decoupling violations and unsafe patterns.
   - **Ruff**: Ensures code matches professional styling/quality.
   - **Pytest**: Verifies functional correctness.
4. **Checkpoint**: Run `/checkpoint "<message>"` to persist the verified state.

## Verification
- **Success Criteria**: `/verify` returns `VALID`.
- **Integrity**: Check `.agent/protocols/.integrity.json` to ensure no kernel tampering.
