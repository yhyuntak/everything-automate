# Codex Agents

This directory holds the narrow agent prompts for the Codex template.

Current planning roster:

- `explorer.md`
- `plan-arch.md`
- `plan-devil.md`

Current execute agents:

- `worker.md`
- `advisor.md`

Current QA review lanes:

- `code-reviewer.md`
- `harness-reviewer.md`

Compatibility prompt still installed:

- `qa-reviewer.md`

`qa-reviewer.md` is kept for older broad QA routing.
New `$qa` routing should prefer `code-reviewer` and `harness-reviewer`.

These agents support the current in-session workflow and are intentionally narrow in scope.
