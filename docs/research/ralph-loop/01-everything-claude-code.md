---
title: Ralph Loop Analysis for Everything Claude Code
description: Concise analysis of how the Ralph loop is defined, orchestrated, and supported in references/everything-claude-code, including planning, execution, hooks, prompts, and harness tradeoffs.
doc_type: reference
scope:
  - autonomous loops
  - agent orchestration
  - hooks
  - memory
covers:
  - references/everything-claude-code/skills/autonomous-loops/SKILL.md
  - references/everything-claude-code/skills/continuous-agent-loop/SKILL.md
  - references/everything-claude-code/agents/loop-operator.md
  - references/everything-claude-code/skills/autonomous-agent-harness/SKILL.md
  - references/everything-claude-code/skills/agent-harness-construction/SKILL.md
  - references/everything-claude-code/skills/continuous-learning-v2/SKILL.md
  - references/everything-claude-code/skills/continuous-learning-v2/hooks/observe.sh
  - references/everything-claude-code/skills/continuous-learning-v2/config.json
  - references/everything-claude-code/AGENTS.md
  - references/everything-claude-code/agents/planner.md
  - references/everything-claude-code/contexts/dev.md
  - references/everything-claude-code/contexts/research.md
  - references/everything-claude-code/contexts/review.md
---

# Ralph Loop in Everything Claude Code

This report only uses files under `references/everything-claude-code`.

## 1. What "Ralph loop" means here

In this repo, "Ralph loop" is shorthand for the RFC-driven DAG orchestration described in [`skills/autonomous-loops/SKILL.md`](../../../references/everything-claude-code/skills/autonomous-loops/SKILL.md#6-ralphinho--rfc-driven-dag-orchestration). It is not presented as a single daemon or command. It is a multi-pass pipeline that:

- decomposes an RFC/PRD into dependency-aware work units
- runs each DAG layer sequentially by dependency, with parallel work inside a layer
- pushes each unit through a tiered quality pipeline
- lands changes through a merge queue that can evict and re-feed conflict context

The canonical wrapper skill has moved to [`skills/continuous-agent-loop/SKILL.md`](../../../references/everything-claude-code/skills/continuous-agent-loop/SKILL.md), which says `autonomous-loops` is superseded but still compatible for one release. That makes "Ralph" a named subpattern inside the broader loop taxonomy rather than the top-level abstraction.

## 2. Planning flow before execution

Planning is explicit and front-loaded. The Ralph section starts with AI decomposition of an RFC into `WorkUnit` objects with `deps`, `acceptance`, and `tier` fields, then uses the dependency DAG to decide layer order ([`skills/autonomous-loops/SKILL.md`](../../../references/everything-claude-code/skills/autonomous-loops/SKILL.md#rfc-decomposition)). The decomposition rules are practical:

- prefer fewer, cohesive units
- minimize file overlap
- keep tests with implementation
- only encode real dependencies

That is reinforced by repo-wide instructions in [`AGENTS.md`](../../../references/everything-claude-code/AGENTS.md): `Plan Before Execute`, `planner` for complex features, and a development workflow that starts with planning before TDD and review. The dedicated [`agents/planner.md`](../../../references/everything-claude-code/agents/planner.md) makes the plan artifact explicit: requirements, architecture review, step breakdown, implementation order, testing strategy, and risks.

The research context also supports the same pattern: [`contexts/research.md`](../../../references/everything-claude-code/contexts/research.md) says to read widely, form a hypothesis, verify with evidence, and not write code until understanding is clear.

## 3. Loop execution and completion logic

Ralph execution is pass-limited and gate-driven. The architecture explicitly says "RALPH LOOP (up to 3 passes)" in [`skills/autonomous-loops/SKILL.md`](../../../references/everything-claude-code/skills/autonomous-loops/SKILL.md#architecture-overview). Inside that envelope:

- each DAG layer runs in dependency order
- each unit gets its own worktree
- depth varies by tier
- stages are separate agent processes with separate context windows

The tier model is the main completion throttle:

- `trivial`: implement -> test
- `small`: implement -> test -> code-review
- `medium`: research -> plan -> implement -> test -> PRD-review + code-review -> review-fix
- `large`: same as medium plus final-review

Completion is not "loop until success forever." It is "land or evict." The merge queue rebases onto `main`, runs build/tests, then either fast-forwards, deletes the branch, or evicts the unit with conflict/test context ([`skills/autonomous-loops/SKILL.md`](../../../references/everything-claude-code/skills/autonomous-loops/SKILL.md#merge-queue-with-eviction)). Evicted work is reintroduced with the captured context so the next pass can fix the real failure instead of retrying blindly.

At the safety layer, [`agents/loop-operator.md`](../../../references/everything-claude-code/agents/loop-operator.md) adds explicit stop conditions: track checkpoints, detect retry storms, pause on repeated failure, and resume only after verification passes. It escalates when there is no progress across two checkpoints, identical failures repeat, cost drifts, or merge conflicts block queue advancement.

## 4. Agent, skill, and subagent model

The repo is strongly agent-centric. [`AGENTS.md`](../../../references/everything-claude-code/AGENTS.md) frames the system as 38 specialized agents and recommends proactive delegation: planner for complex work, tdd-guide for implementation, code-reviewer after code changes, security-reviewer before commits, and loop-operator for autonomous loops.

Ralph uses that separation more aggressively than the simpler loops. The pipeline assigns distinct model roles per stage: research, plan, implement, test, PRD review, code review, review fix, and final review all run in separate agent processes, with the reviewer never reviewing its own code ([`skills/autonomous-loops/SKILL.md`](../../../references/everything-claude-code/skills/autonomous-loops/SKILL.md#separate-context-windows-author-bias-elimination)). That is the main anti-bias mechanism.

The broader harness documents the runtime layer underneath this:

- [`skills/autonomous-agent-harness/SKILL.md`](../../../references/everything-claude-code/skills/autonomous-agent-harness/SKILL.md) maps crons, dispatch, memory, computer use, and task queues onto Claude Code
- [`skills/agent-harness-construction/SKILL.md`](../../../references/everything-claude-code/skills/agent-harness-construction/SKILL.md) says agent quality depends on action space, observation quality, recovery quality, and context budget

Taken together, the repo treats "agent" as a narrow, stage-specific worker, "skill" as a reusable workflow surface, and "subagent" as a deliberately isolated execution context for a single phase or unit.

## 5. Hooks, state, and runtime mechanisms

The runtime substrate is mostly hook- and memory-driven rather than loop-engine-driven. The most concrete mechanism is [`skills/continuous-learning-v2/hooks/observe.sh`](../../../references/everything-claude-code/skills/continuous-learning-v2/hooks/observe.sh), which:

- reads hook JSON from stdin
- detects project context from `cwd` and git root
- skips automated sessions, subagents, observer loops, and disabled runs
- writes observations to project-scoped `observations.jsonl`
- purges old observation files periodically

The matching skill doc [`skills/continuous-learning-v2/SKILL.md`](../../../references/everything-claude-code/skills/continuous-learning-v2/SKILL.md) makes the state model explicit: project-scoped instincts, global instincts, evolved commands/skills/agents, and project hashing via git remote or repo path. Its `config.json` keeps the background observer off by default, which is a good sign that the learning loop is designed to be opt-in rather than always-on.

[`skills/autonomous-agent-harness/SKILL.md`](../../../references/everything-claude-code/skills/autonomous-agent-harness/SKILL.md) adds the other runtime pieces: persistent memory, scheduled tasks, remote dispatch, computer use, and a persistent task queue in memory files. For reusable harness work, this matters because Ralph is not just a control loop; it is expected to survive session boundaries and feed future sessions with durable state.

## 6. System-prompt and instruction surfaces

The repo splits instructions across several surfaces instead of stuffing everything into one prompt:

- global operating policy in [`AGENTS.md`](../../../references/everything-claude-code/AGENTS.md)
- role-specific prompts in agent files like [`agents/planner.md`](../../../references/everything-claude-code/agents/planner.md) and [`agents/loop-operator.md`](../../../references/everything-claude-code/agents/loop-operator.md)
- mode-specific context files in [`contexts/dev.md`](../../../references/everything-claude-code/contexts/dev.md), [`contexts/research.md`](../../../references/everything-claude-code/contexts/research.md), and [`contexts/review.md`](../../../references/everything-claude-code/contexts/review.md)
- workflow guidance in skill frontmatter and skill bodies, especially [`skills/autonomous-loops/SKILL.md`](../../../references/everything-claude-code/skills/autonomous-loops/SKILL.md) and [`skills/continuous-agent-loop/SKILL.md`](../../../references/everything-claude-code/skills/continuous-agent-loop/SKILL.md)
- deterministic enforcement in hooks such as [`skills/continuous-learning-v2/hooks/observe.sh`](../../../references/everything-claude-code/skills/continuous-learning-v2/hooks/observe.sh)

That layering is deliberate. [`skills/agent-harness-construction/SKILL.md`](../../../references/everything-claude-code/skills/agent-harness-construction/SKILL.md) explicitly recommends keeping the system prompt minimal and invariant, moving larger guidance into skills, and using deterministic outputs with explicit stop conditions.

## 7. Strengths and gaps for a reusable agent harness

### Strengths

- Clear separation of concerns: plan, implement, test, review, and merge are distinct stages with different agents and models.
- Strong recovery story: evictions preserve conflict/test context, and loop-operator defines when to stop or narrow scope.
- Good state story: project-scoped observation, project hashing, memory files, and durable task queues support long-running work.
- Good prompt architecture: the repo uses layered instruction surfaces instead of one giant system prompt.

### Gaps

- The Ralph pipeline is described well, but the repo does not show a concrete runnable implementation for the DAG planner, merge queue, or SQLite state store in the files reviewed here.
- The work-unit schema is only illustrative; there is no enforced contract or schema file in this slice of the repo.
- The loop selection guidance is clear, but budget policy is still mostly advisory. There is no single authoritative place that formalizes max-runs, max-cost, or escalation thresholds across all loop types.
- Observation hooks are concrete, but the learning loop is mostly about passive capture and promotion; there is less evidence here of a fully closed-loop harness that automatically decides next actions from state.

## Bottom line

If you want a reusable agent harness, this repo gives you the right design shape: explicit decomposition, tiered execution, isolated contexts, durable state, and deterministic hooks. The main thing it lacks, in the files reviewed here, is a fully implemented Ralph runtime that turns the design into a single executable orchestration engine.
