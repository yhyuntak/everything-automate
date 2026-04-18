---
title: Execute Uses Worker Escalation And Advisor Subagents
status: accepted
date: 2026-04-18
decision_id: DEC-007
---

## Context

The execute workflow already uses `controller`, `worker`, and `advisor` as roles, plus worker/advisor artifact files.

That was useful, but it left an unclear gap: `worker` and `advisor` were not real subagent prompts, and the worker did not have a clear way to say that controller or advisor judgment was needed.

## Decision

`$execute` should keep the main LLM as the controller, but `worker` and `advisor` should become real subagent lanes.

The worker should not call the advisor directly.

The worker may raise an escalation signal to the controller when continuing would require guessing, widening scope, or making a design judgment.

The controller decides whether to:

- retry directly
- adjust worker instructions
- call the advisor
- stop as blocked
- return to `$planning`

The advisor is a high-reasoning subagent used only for hard execution moments.

## Consequences

- worker/advisor are no longer only loose role names in `$execute`
- worker reports need explicit escalation fields
- advisor handoff should be built from controller judgment plus worker escalation context
- controller ownership stays intact because workers still do not call advisors directly
- execute can support a more organic loop without turning scripts into the workflow controller

## Related Plans Or Files

- .everything-automate/plans/2026-04-18-execute-worker-advisor-subagents.md
- .everything-automate/plans/2026-04-11-codex-execute-advisor-runtime-policy.md
- templates/codex/skills/execute/SKILL.md
- templates/codex/skills/execute/scripts/checklist.py
- templates/codex/agents/worker.md
- templates/codex/agents/advisor.md
