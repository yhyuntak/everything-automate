---
name: planning
description: Ralph-ready planning workflow with direct/interview/consensus/review modes.
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
- produce testable acceptance criteria
- prepare a clean future execution handoff

## Interaction Policy

Planning should be interactive only at two boundaries:

1. ambiguity resolution
2. final approval

Everything else should run as a procedural planning pipeline.

```text
interactive
  -> clarification when needed
  -> final approval

non-interactive
  -> explorer
  -> draft
  -> angel
  -> architect
  -> devil
  -> revise
```

## Default Flow

```text
mode detection
  -> preflight context intake
  -> clarification if needed
  -> explorer
  -> draft plan
  -> angel expansion
  -> revise
  -> architect review
  -> revise
  -> devil validation
  -> revise
  -> user approval
  -> execution handoff
```

## Modes

| Mode | Trigger | Behavior |
| --- | --- | --- |
| `direct` | request already concrete | skip interview, draft immediately |
| `interview` | broad or vague request | run a clarification step first |
| `consensus` | risky, high-impact, or architecture-heavy work | require architect then devil review |
| `review` | existing plan needs evaluation | review without rewriting from scratch |

## Rules

- Explore codebase facts before asking the user about them.
- Ask one question at a time when clarification is needed.
- Do not implement during planning.
- Do not hand off to execution until non-goals and decision boundaries are explicit.
- Keep the final plan small enough to execute, but concrete enough to verify.
- Do not keep asking the user for intermediate confirmation once ambiguity is low enough.
- Run the planning stages in order and absorb each stage result into the draft before moving on.

## Orchestration Contract

Planning is a staged orchestration workflow, not a single draft-and-dump step.

```text
request
  -> mode detection
  -> preflight
  -> clarification if needed
  -> explorer
  -> draft
  -> angel
  -> revise
  -> architect
  -> revise
  -> devil
  -> revise
  -> approval
  -> handoff
```

Stage rules:

- `explorer` runs before the first draft when codebase grounding matters.
- `angel` expands the first real draft.
- `architect` reviews the revised draft for structure and execution shape.
- `devil` gives the final critical verdict on the revised draft.
- Each subagent result must be reflected in the draft before the next stage begins.
- `devil` may return `approve`, `iterate`, or `reject`.

Verdict handling:

```text
devil approve
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

- `clarification`
  - clarified task statement
  - desired outcome
  - in-scope
  - non-goals
  - decision boundaries
- `explorer`
  - relevant files
  - current pattern
  - likely touchpoints
  - open unknowns
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
