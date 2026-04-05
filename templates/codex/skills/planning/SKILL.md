---
name: planning
description: Execution-ready planning workflow with clarification gate, staged agent review, and explicit handoff to later execution.
argument-hint: "[--direct|--consensus|--review] <task or spec>"
---

# planning

Turn a user request into an execution-ready plan artifact.

## Purpose

Planning is not implementation.
Its job is to:

- clarify intent
- lock scope
- define non-goals and decision boundaries
- frame the problem before task decomposition
- compare viable directions when design choice matters
- produce testable acceptance criteria
- prepare a clean future execution handoff

## Interaction Policy

Planning is interactive only at two boundaries:

1. clarification when unresolved ambiguity remains after preflight and exploration
2. final approval

Everything else should run as a procedural planning pipeline.

```text
interactive
  -> clarification gate when needed
  -> final approval

non-interactive
  -> preflight
  -> explore
  -> problem framing
  -> draft
  -> angel
  -> architect
  -> devil
  -> self-check
  -> revise
```

## Default Flow

```text
mode detection
  -> preflight context intake
  -> explore
  -> clarification gate
  -> problem framing
  -> draft plan
  -> angel expansion
  -> revise
  -> architect review
  -> revise
  -> devil validation
  -> revise
  -> plan self-check
  -> user approval
  -> execution handoff
```

## Modes

| Mode | Trigger | Behavior |
| --- | --- | --- |
| `direct` | request already concrete | still runs clarification gate, but may pass without user questions |
| `interview` | broad or vague request | clarification gate is expected to open and resolve ambiguity first |
| `consensus` | risky, high-impact, or architecture-heavy work | require architect then devil review and strengthen decision rationale |
| `review` | existing plan needs evaluation | review without rewriting from scratch unless critical gaps require it |

## Rules

- Planning always runs a clarification phase.
  - This does **not** mean it always asks the user questions.
  - It means it always checks whether ambiguity remains after preflight and exploration.
- Explore codebase facts before asking the user about them.
- Ask one question at a time only when clarification is still needed.
- Do not implement during planning.
- Do not decompose into implementation order until problem framing is stable enough.
- Do not hand off to execution until non-goals and decision boundaries are explicit.
- Keep the final plan small enough to execute, but concrete enough to verify.
- Do not keep asking the user for intermediate confirmation once ambiguity is low enough.
- Run the planning stages in order and absorb each stage result into the draft before moving on.
- Prefer lightweight planning by default, but strengthen rigor for high-risk work rather than adding ceremony everywhere.

## Orchestration Contract

Planning is a staged orchestration workflow, not a single draft-and-dump step.

```text
request
  -> mode detection
  -> preflight
  -> explore
  -> clarification gate
  -> problem framing
  -> draft
  -> angel
  -> revise
  -> architect
  -> revise
  -> devil
  -> revise
  -> self-check
  -> approval
  -> handoff
```

Stage rules:

- `preflight` runs before any user questioning.
- `explore` runs before the first draft when codebase grounding matters.
- `clarification gate` decides whether user interaction is still necessary after preflight and exploration.
- `problem framing` locks intent, outcome, scope boundaries, and decision context before task decomposition.
- `angel` expands the first real draft.
- `architect` reviews the revised draft for structure and execution shape.
- `devil` gives the final critical verdict on the revised draft.
- `self-check` runs after the final revise pass and before user approval.
- Each stage result must be reflected in the draft before the next stage begins.
- `devil` may return `approve`, `iterate`, or `reject`.

Verdict handling:

```text
devil approve
  -> self-check
  -> user approval

devil iterate
  -> revise draft
  -> re-run only the stages still needed

devil reject
  -> go back to draft or clarification depending on the failure
```

## Required Output

The plan artifact must include:

- requirements summary
- desired outcome
- in-scope
- non-goals
- decision boundaries
- problem framing
- decision drivers
- viable options
- recommended direction
- acceptance criteria
- verification steps
- implementation order
- risks and mitigations
- execution handoff block

## Plan Artifact Path

During local Everything Automate development, write plan artifacts to:

- `.everything-automate/plans/{YYYY-MM-DD}-{slug}.md`

If a caller already provides a plan path, use that path instead of inventing a new one.

## Handoff Block

Every approved plan must end with a handoff block containing:

- `task_id`
- `plan_path`
- `approval_state`
- `execution_unit`
- `recommended_mode`
- `recommended_agents`
- `verification_lane`
- `open_risks`

## Agent Usage

- `explorer`
  collect codebase facts, patterns, and touchpoints before the draft
- `angel`
  expand missing work items, edge cases, and verification gaps after the draft
- `architect`
  validate structure, alternatives, and execution shape after angel revisions
- `devil`
  attack ambiguity, weak verification, and hidden risk after architect revisions

## Stage Outputs

- `preflight`
  - task statement
  - desired outcome
  - known facts
  - constraints
  - unknowns
  - likely touchpoints
- `clarification`
  - clarified task statement or confirmation that no user interview was required
  - desired outcome
  - in-scope
  - non-goals
  - decision boundaries
- `explorer`
  - relevant files
  - current pattern
  - likely touchpoints
  - open unknowns
- `problem framing`
  - problem statement
  - why now
  - success definition
  - decision drivers
  - viable options
  - recommended direction
- `angel`
  - missing work items
  - missing validation points
  - edge cases
  - optional improvements
- `architect`
  - recommended approach
  - alternatives considered
  - tradeoffs
  - execution recommendation
  - architecture risks
- `devil`
  - verdict: `approve | iterate | reject`
  - critical gaps
  - ambiguous points
  - verification failures
  - required revisions
- `self-check`
  - placeholder scan
  - AC/testability check
  - handoff completeness check
  - implementation-order sanity check
  - unresolved contradiction check

## Mode Selection Guidance

- If the request names files, symbols, or concrete behavior, prefer `direct`.
- If the request uses vague verbs like "improve", "refactor", or "make it better", prefer `interview`.
- If the request touches auth, security, migration, public API breakage, or other high-risk areas, prefer `consensus`.

## Completion

Planning is complete only when:

- the plan is execution-ready
- user approval is explicit when needed
- the handoff block is present
- the plan can be handed off to later execution work without reopening basic scope questions
- all required subagent review stages have been incorporated into the final draft
- problem framing is explicit enough that task decomposition is not guessing at intent
- decision drivers and recommended direction are visible when design choice mattered
- self-check passed with no blocking placeholder, contradiction, or handoff gap
