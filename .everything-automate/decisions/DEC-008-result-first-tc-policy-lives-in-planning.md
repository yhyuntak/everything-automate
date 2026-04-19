---
title: Result First TC Policy Lives In Planning
status: accepted
date: 2026-04-19
decision_id: DEC-008
---

## Context

The workflow already requires `Task -> AC -> TC`, and `$execute` works through TCs as a checklist.

What was missing was a clear rule for how `$planning` should write good TCs. Without that rule, `$execute` can receive weak or unclear TCs and start guessing.

## Decision

TC writing policy belongs in `$planning`.

TCs should be result-first by default:

- a TC is evidence that an AC is done
- TDD is not mandatory
- use test-first when it is useful and practical
- use check-first or verify-after when that fits the work better
- code TCs should prefer real internal code paths and mock or fake external boundaries
- UI work should include browser checks such as Playwright when browser behavior, responsive layout, or user flow risk matters
- `$execute` should run the TC checklist and return to `$planning` when a TC is unclear, too weak, or mismatched with the AC

For non-trivial plans, `plan-arch` and `plan-devil` should be default planning gates. They may be skipped only for tiny low-risk work where scope, TCs, test strategy, and handoff are already obvious.

## Consequences

- `$planning` becomes responsible for TC quality, not only TC presence
- `$execute` should not silently redesign weak TCs during implementation
- code testing defaults toward behavior/result checks instead of internal interaction checks
- UI plans can route TCs to component checks, browser checks, or manual visual checks
- planning reviewers need stronger responsibility for TC fit and execution readiness

## Related Plans Or Files

- .everything-automate/plans/2026-04-19-result-first-tc-policy-and-planning-gates.md
- templates/codex/skills/planning/SKILL.md
- templates/codex/skills/execute/SKILL.md
- templates/codex/agents/plan-arch.md
- templates/codex/agents/plan-devil.md
