---
title: Result First TC Policy And Planning Gates
status: approved
approval_state: approved
task_id: result-first-tc-policy-and-planning-gates-2026-04-19
plan_path: .everything-automate/plans/2026-04-19-result-first-tc-policy-and-planning-gates.md
mode: direct
execution_unit: AC
recommended_mode: execute
recommended_agents:
  - plan-arch
  - plan-devil
verification_lane: mixed
open_risks:
  - Planning skill text may become too heavy if the TC policy is written as a long testing guide.
  - TC type routing may become too detailed and slow down small plans.
  - Plan reviewer gates may add overhead unless tiny low-risk exceptions are clear.
---

# Result First TC Policy And Planning Gates

## Task Summary

Add a clear TC writing policy to the Codex template.

The policy should make `$planning` responsible for creating result-first TCs, while `$execute` stays responsible for running the TC checklist and reporting when a TC is not executable.

## Desired Outcome

After this work:

- `$planning` explains how to write good TCs, not only that TCs are required
- TC writing defaults to result-first checks
- TDD is treated as useful but not mandatory
- code TCs prefer a classicist style: run real internal code paths where practical, and mock or fake external boundaries
- UI work has clear TC routing for component, browser, Playwright, and manual visual checks
- non-code work has clear TC routing for docs, config, runtime/state, and prompt/skill scenarios
- `plan-arch` and `plan-devil` become default gates for non-trivial plans
- `$execute` clearly returns to `$planning` when TC quality is too weak or unclear

## In Scope

- update `templates/codex/skills/planning/SKILL.md`
- update `templates/codex/skills/execute/SKILL.md`
- update `templates/codex/agents/plan-arch.md`
- update `templates/codex/agents/plan-devil.md`
- inspect `templates/codex/AGENTS.md`; edit only if it contradicts the new TC policy
- inspect `templates/codex/skills/README.md`; edit only if its skill summary contradicts the new TC policy
- keep `.everything-automate/decisions/DEC-008-result-first-tc-policy-lives-in-planning.md` as the durable decision note

## Non-Goals

- add a new `tc-strategist` agent now
- enforce TDD for every task
- require Playwright for every UI change
- build new test tooling or scripts
- change execute checklist storage format unless a wording update reveals a real mismatch
- redesign `$qa`
- rewrite the whole planning skill

## Design Direction

Keep the policy short inside `$planning`.

Use this split:

```text
[$planning]
   |
   v
[Write result-first AC/TC]
   |
   v
[Use plan-arch and plan-devil for non-trivial plans]
   |
   v
[Approved handoff]
   |
   v
[$execute runs TC checklist]
   |
   +---- TC unclear or too weak ----> [Return to planning]
   |
   v
[$qa]
```

The planning skill should carry the core TC rules directly because it writes the TCs. It may point to compact examples or a short routing guide, but it should not become a long testing textbook.

## Test Strategy

Use `mixed`.

Verification should include:

- doc read-through of changed skills and agents
- search checks for old contradictory wording
- scenario checks that planning, execute, plan-arch, and plan-devil each have the right responsibility
- no Python compile check unless execution touches Python files

The scenario checks are text-level walkthroughs, not new automation.

Required scenarios:

- Planning UI scenario:
  A plan for a UI form change should route TC choices to component, browser, or manual visual checks based on risk, without requiring Playwright for every UI change.
- Planning code scenario:
  A plan for a CLI/runtime change should prefer checking output, files, state, or errors instead of private method calls.
- Execute weak TC scenario:
  If a TC only says "check it works" or only checks an internal call with no user-visible result, `$execute` should return to `$planning` instead of inventing a better TC.
- Reviewer gate scenario:
  A skill/workflow change should use `plan-arch` and `plan-devil` by default, while a tiny typo or link fix may skip them.

## Task

Implement the result-first TC policy and planning reviewer gate.

### AC1. Preserve The Accepted Decision

The durable decision note records the chosen workflow policy.

- TC: `.everything-automate/decisions/DEC-008-result-first-tc-policy-lives-in-planning.md` exists with `status: accepted`.
- TC: The decision says TC policy lives in `$planning`.
- TC: The decision says TDD is not mandatory.
- TC: The decision says code TCs default to result-first or classicist checks.
- TC: The decision says `plan-arch` and `plan-devil` are default gates for non-trivial plans.

### AC2. Add TC Writing Policy To Planning

`$planning` explains how to write TCs, not only that TCs are required.

- TC: `templates/codex/skills/planning/SKILL.md` defines a TC as evidence that an AC is done.
- TC: The planning skill says TCs should be result-first by default.
- TC: The planning skill says TDD is useful but not mandatory.
- TC: The planning skill includes a compact TC routing guide for code, UI, docs, config, runtime/state, and prompt/skill work.
- TC: The planning skill explains UI/browser checks and when Playwright-style checks fit.
- TC: The planning skill says `$execute` must be able to run or perform each TC without guessing.
- TC: A UI scenario can be walked through from the final planning text and produces component/browser/manual TC choices without making Playwright mandatory.
- TC: A code scenario can be walked through from the final planning text and produces result checks instead of private method or call-order checks.

### AC3. Keep Execute As TC Runner, Not TC Designer

`$execute` stays focused on running the checklist and reporting TC gaps.

- TC: `templates/codex/skills/execute/SKILL.md` still says execute works from the approved `Task -> AC -> TC` checklist.
- TC: The execute skill says TDD is not mandatory and keeps the earliest useful verification loop rule.
- TC: The execute skill says unclear, too weak, mismatched, or non-executable TCs should return to `$planning` instead of being silently redesigned.
- TC: The execute TC type list is aligned with planning. If new types are added, keep the list small and easy to use.
- TC: A weak TC scenario can be walked through from the final execute text and clearly stops or returns to `$planning`.

### AC4. Make Plan Reviewers Default Gates For Non-Trivial Plans

Planning reviewers help protect TC quality and execution readiness.

- TC: `templates/codex/skills/planning/SKILL.md` says `plan-arch` and `plan-devil` are default for non-trivial plans.
- TC: The planning skill names tiny low-risk work as the main skip case.
- TC: The planning skill gives examples of non-trivial plans, such as workflow, runtime/state, skill/agent, UI behavior, or multi-file behavior changes.
- TC: The planning skill gives examples of tiny low-risk exceptions, such as typo fixes, link fixes, or narrow copy edits.
- TC: `templates/codex/agents/plan-arch.md` checks TC routing, test-strategy fit, UI/browser fit, and execute readiness.
- TC: `templates/codex/agents/plan-devil.md` attacks weak TCs, implementation-first TCs, over-testing, under-testing, and handoff gaps.
- TC: The updated wording does not imply every tiny typo or link fix needs both reviewers.
- TC: The old "if needed" reviewer wording is replaced or bounded so it does not conflict with the new default-gate rule.

### AC5. Keep Top-Level Template Guidance Aligned

Top-level guidance does not contradict the new TC policy.

- TC: `templates/codex/AGENTS.md` does not describe TDD as mandatory.
- TC: `templates/codex/AGENTS.md` keeps `$planning` as the source of `Task -> AC -> TC`.
- TC: `templates/codex/AGENTS.md` is inspected and edited only if it contradicts the new TC policy.
- TC: `templates/codex/skills/README.md` is inspected and edited only if it contradicts the new TC policy.
- TC: Any edited README or top-level guidance keeps the same stage order: `$brainstorming -> $planning -> $execute -> $qa`.
- TC: The wording uses simple English and does not introduce heavy testing jargon without explanation.

## Execution Order

1. Update `$planning` with the TC writing policy and reviewer gate.
2. Update `$execute` with the boundary rule for weak or unclear TCs.
3. Update `plan-arch` and `plan-devil` reviewer prompts.
4. Inspect `AGENTS.md` and skill README, then update only if needed for alignment.
5. Run the mixed verification checks, including read-through, search, and scenario checks.

## Open Risks

- The planning skill could become too long. Keep the new policy concise.
- TC types could become too many. Prefer a small list with routing examples.
- Review gates could slow tiny work. Keep the tiny low-risk exception explicit.
- UI TC guidance could over-require Playwright. Say when browser checks matter instead of making them universal.

Mitigation checks:

- the added planning policy should be compact and should not rewrite unrelated sections
- the TC type list should stay small, with extra routing handled as examples
- reviewer gate wording should include both non-trivial examples and tiny low-risk exceptions
- UI wording should keep Playwright conditional

## Execute Handoff

- `task_id`: `result-first-tc-policy-and-planning-gates-2026-04-19`
- `plan_path`: `.everything-automate/plans/2026-04-19-result-first-tc-policy-and-planning-gates.md`
- `approval_state`: `approved`
- `execution_unit`: `AC`
- `test_strategy`: `mixed`
- `open_risks`:
  - Planning skill text may become too heavy if the TC policy is written as a long testing guide.
  - TC type routing may become too detailed and slow down small plans.
  - Plan reviewer gates may add overhead unless tiny low-risk exceptions are clear.
- `approval_note`: Approved by user request `$execute` on 2026-04-20.
- `verification_commands`:
  - `rg -n "TDD|test-first|result-first|Playwright|plan-arch|plan-devil|if needed|not required for every plan" templates/codex/skills templates/codex/agents templates/codex/AGENTS.md`
  - `sed -n '170,280p' templates/codex/skills/planning/SKILL.md`
  - `sed -n '300,335p' templates/codex/skills/execute/SKILL.md`
  - `sed -n '1,70p' templates/codex/agents/plan-arch.md`
  - `sed -n '1,70p' templates/codex/agents/plan-devil.md`
- `scenario_checks`:
  - UI form change routes to component/browser/manual checks without requiring Playwright for every UI task.
  - CLI/runtime change routes to output, file, state, or error checks instead of private call checks.
  - Weak TC returns to `$planning` instead of being silently rewritten by `$execute`.
  - Non-trivial workflow/skill/runtime/UI change uses plan reviewers by default; tiny typo/link/copy fixes may skip them.
