---
title: Codex Execute Hardening
description: Current execute and QA hardening summary.
doc_type: guide
status: support
scope:
  - codex
  - execute
  - qa
  - verification
covers:
  - templates/codex/skills/execute/SKILL.md
  - templates/codex/skills/qa/SKILL.md
  - runtime/ea_progress.py
---

# Codex Execute Hardening

Status: support.

The old M5 working-note body was removed.
It had useful history, but it mixed older milestone language with current behavior.

Current source of truth:

- `templates/codex/skills/execute/SKILL.md`
- `templates/codex/skills/qa/SKILL.md`
- `templates/codex/agents/worker.md`
- `templates/codex/agents/advisor.md`
- `templates/codex/agents/code-reviewer.md`
- `templates/codex/agents/harness-reviewer.md`

Current hardening focus:

- `$execute` follows an approved plan AC-by-AC.
- `$execute` anchors work in TCs and records checklist progress.
- `worker` and `advisor` are support lanes; the main LLM remains controller.
- `$execute` builds a QA handoff instead of going straight to commit.
- `$qa` routes to `code-reviewer`, `harness-reviewer`, or both when needed.
