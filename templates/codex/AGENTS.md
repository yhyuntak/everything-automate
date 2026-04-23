# Everything Automate for Codex CLI

This file is the top-level runtime guidance entry for the Codex template.

## Positioning

Codex CLI is the current `v0` implementation path.
The primary user workflow should stay inside the Codex session.
Runtime helpers and state tools exist to support that workflow, not replace it.

## Runtime Model

```text
inside Codex
  -> $ea-brainstorming
  -> $ea-north-star
  -> $ea-blueprint
  -> $ea-planning
  -> $ea-execute
  -> $ea-qa

under the hood
  -> handoff
  -> state/runtime preparation
  -> execution/recovery support
```

## Core Expectations

- `AGENTS.md` is the top-level operating contract
- setup installs the guidance, agent prompts, and skills Codex needs
- in-session workflow is the primary UX
- durable execution is not assumed to be native to Codex
- runtime helpers are internal support surfaces for state, instructions, and recovery
- the kernel discipline remains:

```text
plan -> ea-execute -> verify -> decide
```

## Language Rule

Use simple English by default.

- prefer common words over abstract framework words
- write so non-native English speakers can follow quickly
- keep important terms stable, but explain them in simple words around them
- use the same rule in skill text, setup text, and direct user-facing explanations
- prefer easier words over harder professional English
- English terms are allowed, but do not overuse them
- if a simpler word works, use the simpler word
- do not stack many English terms in one short paragraph

If a middle-school-level reader cannot follow the wording, it is too hard.

## Request Clarity Rule

Before doing heavy work, make the user's request clear enough to act on safely.

A request is clear when you can tell:

- the wanted outcome
- the current workflow stage
- the allowed scope
- the important non-goals
- the check for done

If any of these are missing and the next action is risky, ask one short question before acting.

If the next action is low-risk, state the assumption briefly and proceed.

Prefer turning a vague prompt into a sharper working request over giving a generic answer.

Do not guess silently when a wrong guess could change scope, edit files, create issues, commit, push, change data shape, or move workflow stage.

## Think Before Coding Rule

Do not assume.
Do not hide confusion.
Surface tradeoffs.

Before implementing:

- state your assumptions explicitly
- if several interpretations are possible, present them instead of silently choosing one
- if a simpler approach exists, say so
- push back when the current direction appears needlessly complex or risky
- if something is unclear, stop, name what is unclear, and ask

## Anti-Overengineering Rule

Prefer the smallest design that solves the current problem well.

Do not start with broad architecture, heavy abstractions, large schemas, many categories, or hard words unless the task clearly needs them.

Do not add speculative work:

- no features beyond what was asked
- no abstractions for one-use code
- no flexibility or configurability that was not requested
- no error handling for impossible scenarios
- if a large change can be much smaller, simplify it before moving on

Build in thin layers:

- solve the immediate use case first
- keep names and data shapes simple
- add structure only when a real need appears
- explain tradeoffs in plain words

Avoid making the work look more complex than it is.

## Surgical Change Rule

Touch only what the task requires.
Clean up only the mess created by your own change.

When editing existing code:

- do not improve adjacent code, comments, or formatting just because you noticed it
- do not refactor things that are not broken
- match the existing local style, even if you would choose a different style elsewhere
- if you notice unrelated dead code, mention it instead of deleting it

When your change creates unused code:

- remove imports, variables, functions, files, and docs that your change made unused
- do not remove pre-existing dead code unless the user asked for that cleanup

Every changed line should connect directly to the user's request.

## Goal-Driven Execution Rule

Define success criteria.
Loop until verified.

Turn implementation requests into verifiable goals:

- "add validation" means define invalid inputs, check them, then make the check pass
- "fix the bug" means reproduce or describe the failure, then verify the fix
- "refactor X" means know what behavior must stay the same and run a check before and after when possible

For multi-step tasks, use a short plan where each step has a check:

```text
1. [Step] -> verify: [check]
2. [Step] -> verify: [check]
3. [Step] -> verify: [check]
```

Strong success criteria let the agent loop independently.
Weak criteria such as "make it work" require clarification.

## Rigor Tradeoff Rule

These rules bias toward caution over speed.
For trivial tasks, such as a typo or an obvious one-line edit, use judgment and keep the process light.
The goal is to reduce costly mistakes on non-trivial work, not to slow down simple work.

## Communication Rule

Put the answer first.

- start with the main conclusion or state change
- do not hide the answer inside a long setup paragraph
- if the user mainly needs a status update, lead with:
  - what finished
  - what changed
  - what is still left

Keep the answer cleanly structured.

- prefer short sections or short paragraphs over one long block
- group content into clear chunks when helpful:
  - conclusion
  - key changes
  - checks
  - next step
- do not mix every detail into one paragraph
- do not flood the main answer with too many file paths

## Flow Chart Rule

When a process or workflow needs to be explained, prefer a real ASCII flow chart.

Good:

```text
[Start]
   |
   v
[Read Plan]
   |
   v
[Pick AC]
   |
   +---- blocked ----> [Stop and Report]
   |
   v
[Pick TC]
   |
   v
[Run Check]
   |
   v
[Implement]
   |
   v
[Check Again]
   |
   +---- fail ----> [Fix and Retry]
   |
   v
[Next]
```

Do not treat this as a flow chart:

```text
plan -> ea-execute -> verify -> decide
```

That is only a short chain, not a real flow chart.

## Current Status

Primary in-session workflow surface:

- `$ea-brainstorming`
- `$ea-north-star`
- `$ea-blueprint`
- `$ea-planning`
- `$ea-execute`
- `$ea-qa`

Current internal support surface in this source repo:

- `runtime/ea_codex.py`
- `templates/codex/overlays/ea-codex.sh`

These helpers are not the intended primary user workflow.
`ea-codex.sh` is an authoring-time wrapper around `runtime/ea_codex.py`.
The current global setup does not install that wrapper into `~/.codex/`.

Current agent roster:

Planning agents:
- `ea-explorer`
- `ea-plan-arch`
- `ea-plan-devil`

Execute agents:
- `ea-worker`
- `ea-advisor`

QA review agents:
- `ea-code-reviewer`
- `ea-harness-reviewer`

Docs agents:
- `ea-docs-worker`

Current note:

- `$ea-brainstorming` is the idea-shaping surface before ea-planning.
- `$ea-north-star` is the goal-lock surface when the target is fuzzy and drift risk is high.
- `$ea-blueprint` is the design-spec surface after North Star and before ea-planning.
- `$ea-planning` is the execution planning surface after direction is clear enough.
- `$ea-execute` is the TC-first execution surface after an approved ea-planning handoff and before `$ea-qa`.
- Calling `$ea-execute` is an explicit request to use the `ea-worker` subagent for implementation work; the main LLM stays the controller.
- `$ea-execute` normally continues into `$ea-qa` before `commit` when the work is ready for review.
- `$ea-qa` is the final review-and-judgment gate before `commit`.
- support skills such as `ea-docs`, `ea-issue-capture`, and `ea-issue-pick` may feed docs or backlog work into the main workflow, but they are not main workflow stages.
- hidden runtime/state helpers may support the flow, but they are not the main user workflow.
