---
title: Execute Worker Advisor Subagents
status: approved
approval_state: approved
task_id: execute-worker-advisor-subagents-2026-04-18
plan_path: .everything-automate/plans/2026-04-18-execute-worker-advisor-subagents.md
mode: direct
execution_unit: AC
recommended_mode: execute
recommended_agents:
  - plan-arch
  - plan-devil
verification_lane: mixed
open_risks:
  - Worker escalation may become noisy if the criteria are too broad.
  - Advisor use may become too frequent if controller decision rules are weak.
  - The worker report schema may grow too wide if escalation fields are not kept minimal.
---

# Execute Worker Advisor Subagents

## Task Summary

Promote the existing `$execute` worker/advisor roles into real subagent lanes and add a clear worker-to-controller escalation loop.

The main LLM stays the controller. Workers do bounded execution work. Advisors provide high-reasoning diagnosis only when the controller decides it is needed.

## Desired Outcome

Have a follow-up change set that:

- adds a real `worker` subagent prompt
- adds a real `advisor` subagent prompt
- keeps the main LLM as the `$execute` controller
- lets the worker raise an escalation signal when continuing would require guessing
- lets the controller decide whether to retry directly, adjust instructions, call the advisor, stop, or return to `$planning`
- keeps the existing artifact model around `worker-report.json`, `advisor-handoff.json`, and `retry-packet.json`
- expands worker report fields only enough to support escalation

## In Scope

- add `templates/codex/agents/worker.md`
- add `templates/codex/agents/advisor.md`
- update `templates/codex/agents/README.md`
- update `templates/codex/AGENTS.md` agent roster
- update `templates/codex/skills/execute/SKILL.md` to say worker/advisor are subagent lanes
- define worker escalation criteria inside `$execute`
- update worker report shape in `$execute`
- update `templates/codex/skills/execute/scripts/checklist.py` if needed so worker reports can persist escalation fields
- keep existing advisor handoff and retry packet roles aligned

## Non-Goals

- add a public `$advisor` skill
- let the worker call the advisor directly
- move controller judgment into scripts
- build provider-enforced model routing
- add a full budget engine
- redesign planning or QA
- replace the existing execute checklist model

## Design Direction

Use this execution shape:

```text
[Main LLM / Controller]
- reads approved plan
- picks AC and TC
- decides direct work vs worker
   |
   v
[Worker Subagent]
- receives active AC/TC and constraints
- implements bounded work
- runs checks when possible
- reports pass, fail, blocked, or escalation_needed
   |
   v
[Main LLM / Controller]
- judges worker report
- if next step is clear: retry or continue
- if escalation is valid: build advisor handoff
- if plan boundary is broken: return to planning
   |
   v
[Advisor Subagent, only if needed]
- reads focused advisor handoff
- diagnoses the hard moment
- compares options
- recommends next steps
   |
   v
[Main LLM / Controller]
- writes retry packet
- sends bounded next instruction to worker
```

Use this ownership rule:

- the controller owns the loop
- the worker owns bounded execution attempts
- the advisor owns diagnosis and recommendation only
- scripts own artifact writing and validation only

## Worker Escalation Rule

The worker should continue only when the next action is clear and inside the approved plan.

The worker should raise escalation to the controller when:

- the same TC fails again and the next move is unclear
- the fix has multiple viable paths with tradeoffs
- the likely fix touches scope or non-goals
- the likely fix changes architecture or workflow contract
- a test failure has an unclear root cause
- continuing would mean guessing instead of executing the plan
- a risk is high enough that controller judgment is needed before changing files further

The worker must not call the advisor.

The worker can only report that advisor-style judgment may be needed.

## Worker Report Shape

Keep the existing worker report shape, but add minimal escalation fields.

Required or existing fields:

- summary
- what_tried
- candidate_next_steps
- optional files_touched
- optional checks_run
- optional failure_or_blocker

New optional escalation fields:

- escalation_needed
- escalation_type
- escalation_question
- uncertainty_reason
- risk_if_continue

`escalation_type` should use simple values such as:

- `none`
- `controller_decision`
- `advisor_candidate`
- `planning_boundary`
- `blocked`

## Advisor Handoff Shape

Advisor handoff should remain focused.

It should include:

- open_question
- recent_attempts
- candidate_options
- optional relevant_files
- optional failing_check
- optional worker_report_ref
- optional escalation_question
- optional uncertainty_reason
- optional risk_if_continue

Do not pass the full transcript to the advisor.

## Test Strategy

The lane is `mixed`.

Verification should include:

- re-read execute skill text for clear controller, worker, and advisor ownership
- re-read worker/advisor prompts for correct boundaries
- run `python3 -m py_compile templates/codex/skills/execute/scripts/checklist.py` if the helper changes
- run helper smoke tests if worker-report or advisor-handoff persistence changes
- confirm AGENTS and agents README list the new subagents
- confirm no text says workers may call advisors directly

## Task

### AC1. Add Real Worker And Advisor Subagents

The existing worker/advisor roles must become real agent prompts.

#### TC1

`templates/codex/agents/worker.md` exists and describes bounded implementation execution.

#### TC2

`templates/codex/agents/advisor.md` exists and describes high-reasoning diagnosis and recommendation for hard execution moments.

#### TC3

The agent roster in `templates/codex/AGENTS.md` and `templates/codex/agents/README.md` lists both subagents.

### AC2. Define Worker Escalation Behavior

The worker must know when to continue and when to report uncertainty to the controller.

#### TC1

The worker prompt defines continue criteria.

#### TC2

The worker prompt defines escalation criteria.

#### TC3

The worker prompt says the worker must not call the advisor directly.

### AC3. Update `$execute` Around Subagent Lanes

The execute skill must stop treating worker/advisor as loose role names only.

#### TC1

`templates/codex/skills/execute/SKILL.md` says `worker` and `advisor` are subagent lanes used by the controller.

#### TC2

The core flow shows worker escalation to controller before advisor use.

#### TC3

The controller decision rules say how to handle worker escalation:

- continue
- retry
- call advisor
- blocked
- return to planning

### AC4. Extend Worker Report And Advisor Handoff Artifacts

The durable artifacts must support the new escalation loop without becoming transcript dumps.

#### TC1

The worker report shape includes minimal escalation fields.

#### TC2

The advisor handoff shape can include worker escalation context.

#### TC3

If helper changes are needed, `checklist.py` validates the new fields without making them mandatory for every worker report.

### AC5. Preserve Controller Ownership

The new subagents must not take over the execute loop.

#### TC1

The docs clearly say the controller owns advisor calls.

#### TC2

The docs clearly say the worker can request escalation but cannot call the advisor.

#### TC3

The docs clearly say the controller makes the final retry, stop, or planning-return decision.

### AC6. Verify The New Loop

The final implementation must prove that the new subagent loop is clear and safe.

#### TC1

Changed Python helpers pass `py_compile` when any Python helper changes.

#### TC2

Helper smoke tests pass if artifact persistence changes.

#### TC3

A read-through of the final docs shows this flow clearly:

```text
controller -> worker -> worker escalation -> controller -> advisor if needed -> controller -> worker retry
```

## Execution Order

1. Add worker and advisor agent prompts.
2. Update AGENTS and agents README roster.
3. Rewrite execute skill role language around subagent lanes.
4. Add worker escalation criteria and controller decision rules.
5. Update artifact field descriptions and helper validation if needed.
6. Verify helper syntax and smoke tests if Python changes.
7. Re-read docs for simple English and ownership clarity.

## Open Risks

- If worker escalation is too broad, the controller may be interrupted too often.
- If worker escalation is too narrow, the worker may keep guessing instead of asking for judgment.
- If advisor output is too broad, retry packets may become vague.
- If helper fields become mandatory too quickly, normal worker reports may become too heavy.

## Execute Handoff

- `task_id`: `execute-worker-advisor-subagents-2026-04-18`
- `plan_path`: `.everything-automate/plans/2026-04-18-execute-worker-advisor-subagents.md`
- `approval_state`: `approved`
- `execution_unit`: `AC`
- `test_strategy`: `mixed`
- `open_risks`:
  - Worker escalation may become noisy if the criteria are too broad.
  - Advisor use may become too frequent if controller decision rules are weak.
  - The worker report schema may grow too wide if escalation fields are not kept minimal.
