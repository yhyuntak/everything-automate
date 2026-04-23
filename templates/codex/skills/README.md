# Codex Skills

This directory holds distributable skills for the Codex template.

Current active in-session workflow surface:

- `ea-brainstorming/`
- `ea-north-star/`
- `ea-blueprint/`
- `ea-planning/`
- `ea-execute/`
- `ea-qa/`

`ea-brainstorming/` is upstream ideation and design shaping.
`ea-north-star/` locks a fuzzy target into one clear shared goal.
`ea-blueprint/` turns a locked North Star into a buildable design spec.
`ea-planning/` is downstream execution planning.
`ea-execute/` is downstream TC-first execution after an approved ea-planning handoff and before `$ea-qa`.
`ea-qa/` is the final cold-review gate before commit.

Support skills:

- `ea-docs/`
- `ea-issue-capture/`
- `ea-issue-pick/`

`ea-docs/` sets up, checks, and maintains an LLM Wiki docs structure for project work.
`ea-issue-capture/` creates a real backlog GitHub issue in `yhyuntak/everything-automate` from another project session.
`ea-issue-pick/` reads one open backlog issue and turns it into input for `$ea-brainstorming`.

Installed helper scripts live under the skill that uses them.

- `ea-execute/scripts/`
- `ea-qa/scripts/`

Workflow hooks live under:

- `templates/codex/hooks.json`
- `templates/codex/hooks/`
