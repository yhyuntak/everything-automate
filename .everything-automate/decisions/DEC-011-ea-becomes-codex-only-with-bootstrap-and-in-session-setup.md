---
title: Everything Automate Becomes Codex-Only With Bootstrap And In-Session Setup
status: accepted
date: 2026-04-24
decision_id: DEC-011
---

## Context

The repository still carries a broader multi-provider shape in its folders, docs, and some runtime surfaces.

At the same time, the active product direction is narrower:

- Everything Automate should be a Codex-only project
- setup should feel native inside the Codex session
- the first-user install flow should be easy to follow from the README

The current global install story is still too script-first.
That makes the setup UX harder to explain and harder to evolve around the in-session workflow.

## Decision

Treat Everything Automate as a Codex-only project.

Adopt this install model:

- a small bootstrap step makes the minimum setup surface available globally
- the real setup flow happens inside Codex through `$ea-setup`
- `$ea-setup` should end by running `$ea-doctor`

Do not mix this decision with a large repo relayout in the same first change.

The accepted migration shape is:

- v1
  - update the user-facing install contract
  - add bootstrap, `ea-setup`, and `ea-doctor`
  - keep large internal file moves out of scope
- later
  - flatten the remaining Codex source layout further when the new install flow is stable

## Consequences

- User-facing docs should stop describing EA as a provider-neutral or multi-provider product.
- Setup UX should move from script-first to bootstrap-plus-skill-first.
- Existing low-level install scripts can stay, but as support tools under the new setup flow.
- Large file moves, provider directory cleanup, and runtime helper relayout should be handled in later work so the first migration stays smaller and safer.

## Related Plans Or Files

- README.md
- templates/INSTALL.md
- scripts/install_global.py
- .everything-automate/plans/2026-04-24-codex-only-bootstrap-setup-v1.md
