---
title: Ralph Loop Analysis for oh-my-codex
description: Concise analysis of Ralph-related planning, execution, state, prompt, and worker mechanics in oh-my-codex.
doc_type: reference
scope:
  - ralph
  - planning
  - team runtime
  - prompts
  - state and hooks
covers:
  - references/oh-my-codex/skills/ralph/SKILL.md
  - references/oh-my-codex/skills/plan/SKILL.md
  - references/oh-my-codex/skills/ralplan/SKILL.md
  - references/oh-my-codex/skills/team/SKILL.md
  - references/oh-my-codex/skills/worker/SKILL.md
  - references/oh-my-codex/src/mcp/state-server.ts
  - references/oh-my-codex/src/cli/index.ts
  - references/oh-my-codex/src/team/runtime.ts
  - references/oh-my-codex/src/team/worker-bootstrap.ts
  - references/oh-my-codex/src/agents/native-config.ts
---

# Ralph Loop in oh-my-codex

The repo treats Ralph as a **persistent execution loop with verification**, not as a generic multi-agent umbrella. The clearest definition is in `references/oh-my-codex/skills/ralph/SKILL.md`: Ralph is a persistence loop that wraps ultrawork, keeps retrying until the task is complete, and requires architect verification before completion. The frozen contract in `references/oh-my-codex/docs/contracts/ralph-state-contract.md` makes that more explicit: Ralph is a standalone mode, session-scoped state is authoritative when present, and there is no built-in `omx team ralph ...` linked-launch path anymore.

## 1) Exact Ralph Concept

- Ralph is a **single-owner, stateful completion loop** with `iteration`, `max_iterations`, `current_phase`, `started_at`, and `completed_at` persisted through `state_write`/`state_read` (`references/oh-my-codex/skills/ralph/SKILL.md`, `references/oh-my-codex/src/mcp/state-server.ts`).
- It is **persistence-first**: the loop does not stop at a partial pass, and verification failure feeds back into fix/verify rather than exiting early (`references/oh-my-codex/docs/reference/ralph-upstream-baseline.md`, `references/oh-my-codex/skills/ralph/SKILL.md`).
- The canonical artifact trail is split between a **PRD** and a **progress ledger**. Ralph PRD mode creates `.omx/plans/prd-{slug}.md` plus `.omx/state/{scope}/ralph-progress.json` (`references/oh-my-codex/skills/ralph/SKILL.md`).
- The upstream parity docs confirm the same semantic package: persisted iteration state, terminal completion, cancel propagation, and scope preference are all tracked as explicit contract rules (`references/oh-my-codex/docs/reference/ralph-parity-matrix.md`).

## 2) Planning Flow Before Execution

The repo intentionally puts a planning gate in front of execution-heavy workflows:

- `references/oh-my-codex/skills/plan/SKILL.md` auto-detects interview vs direct planning, and its consensus mode (`ralplan`) runs Planner -> Architect -> Critic until agreement.
- `references/oh-my-codex/skills/ralplan/SKILL.md` sharpens that gate: it demands a grounded context snapshot, RALPLAN-DR summary, and sequential Architect then Critic review before any handoff.
- For interactive planning, the repo asks for user input only after the draft plan is grounded and reviewed; execution is deferred to `$ralph` or `$team` rather than performed in the planning lane (`references/oh-my-codex/skills/plan/SKILL.md`, `references/oh-my-codex/skills/ralplan/SKILL.md`).
- The practical intent is visible in the docs/index: `references/oh-my-codex/docs/agents.html` tells users to start with `deep-interview -> ralplan -> team/ralph`.

So the flow is not “Ralph first”; it is “scope and plan first, then hand off to Ralph for persistence-oriented execution.”

## 3) Loop Execution and Completion Logic

The Ralph loop itself is defined by the `skills/ralph` contract and enforced by state/runtime code:

- Start state writes `active: true`, `iteration: 1`, `max_iterations: 10`, and `current_phase: "executing"` (`references/oh-my-codex/skills/ralph/SKILL.md`).
- Each iteration updates `iteration` and phase transitions through `executing -> verifying -> fixing -> complete` as needed (`references/oh-my-codex/skills/ralph/SKILL.md`, `references/oh-my-codex/src/ralph/contract.ts`).
- Completion requires **fresh verification evidence** plus architect approval, and terminal success must write `active: false`, `current_phase: "complete"`, and `completed_at` (`references/oh-my-codex/skills/ralph/SKILL.md`, `references/oh-my-codex/src/ralph/contract.ts`).
- The state validator rejects invalid Ralph phases, rejects terminal phases with `active=true`, and auto-fills `completed_at` for terminal states (`references/oh-my-codex/src/ralph/contract.ts`, `references/oh-my-codex/src/mcp/state-server.ts`).
- Notify-hook behavior extends the loop: the session-scoped Ralph state can auto-expand `max_iterations` by 10 when the run is still progressing, while non-Ralph modes are marked complete when their max is reached (`references/oh-my-codex/src/hooks/__tests__/notify-hook-session-scope.test.ts`).
- Cancellation is terminalization, not deletion: `cancelModes` in `references/oh-my-codex/src/cli/index.ts` sets `active=false`, `current_phase="cancelled"`, and `completed_at`, and it also propagates to linked ultrawork when Ralph is linked.

## 4) Agent, Skill, and Subagent Model

The repo uses a layered model rather than one monolithic agent abstraction:

- `references/oh-my-codex/AGENTS.md` and `templates/AGENTS.md` are the top-level orchestration contract; role prompts under `prompts/*.md` are narrower execution surfaces that must follow AGENTS authority.
- `references/oh-my-codex/docs/shared/agent-tiers.md` separates `role`, `tier`, and `posture`, which is the repo’s core routing vocabulary for agent work.
- `references/oh-my-codex/skills/ralph/SKILL.md` treats ultrawork as the parallelism layer and Ralph as persistence plus verification on top.
- `references/oh-my-codex/skills/team/SKILL.md` is the tmux-based durable worker model: it explicitly says native Codex subagents complement team/ralph execution, but do not replace the team runtime’s stateful coordination contract.
- `references/oh-my-codex/skills/worker/SKILL.md` is the worker-side protocol: ACK the leader, claim tasks, transition task status, and use mailbox/task state as the source of truth.

This gives the repo three distinct execution surfaces:

1. native subagents for bounded in-session fanout,
2. Ralph for persistent single-owner completion,
3. Team for durable tmux workers and shared task state.

## 5) Hooks, State, and Runtime Mechanisms

The runtime is state-driven and observable rather than ad hoc:

- `references/oh-my-codex/src/mcp/state-server.ts` provides `state_read`, `state_write`, `state_clear`, `state_list_active`, and `state_get_status`, and it validates Ralph state before persisting it.
- `references/oh-my-codex/src/cli/index.ts` handles session cleanup, mode cancellation, and hook emission. It also launches background helpers such as notify fallback and hook-derived watchers.
- The Ralph state contract in `references/oh-my-codex/docs/contracts/ralph-state-contract.md` establishes session-scoped authority, root fallback compatibility, and safe cross-session migration rules.
- `references/oh-my-codex/docs/hooks-extension.md` shows the hook model is additive: plugins can read/write scoped state, but team workers skip side effects by default.
- The team runtime is more elaborate: `references/oh-my-codex/src/team/runtime.ts`, `references/oh-my-codex/src/team/runtime-cli.ts`, `references/oh-my-codex/src/team/mcp-comm.ts`, and `references/oh-my-codex/src/team/worker-bootstrap.ts` coordinate task state, mailbox dispatch, worktree setup, and worker instructions.
- `references/oh-my-codex/src/team/state-root.ts` and `references/oh-my-codex/src/team/orchestrator.ts` define the canonical state root and the team phase machine.

The result is a harness that can be inspected from files alone: state files, mailbox files, task JSON, and runtime metadata all exist as first-class artifacts.

## 6) Prompt and System-Instruction Surfaces

The prompt surface is split across authored prompts, generated config, and bootstrap overlays:

- `references/oh-my-codex/src/config/generator.ts` injects top-level `developer_instructions` saying AGENTS.md is the orchestration brain and that skills/prompt surfaces sit under that authority.
- `references/oh-my-codex/src/agents/native-config.ts` composes role prompts with posture overlays, model-class overlays, and an exact `gpt-5.4-mini` overlay. That is a concrete seam for prompt adaptation.
- `references/oh-my-codex/src/team/worker-bootstrap.ts` composes worker runtime instructions by combining the project AGENTS content, role prompt content, and worker overlay, while avoiding direct mutation of source AGENTS files.
- `references/oh-my-codex/prompts/planner.md`, `references/oh-my-codex/prompts/executor.md`, and `references/oh-my-codex/prompts/verifier.md` are canonical XML-tagged role surfaces with distinct behavioral contracts.
- `references/oh-my-codex/AGENTS.md` and `references/oh-my-codex/templates/AGENTS.md` enforce the higher-level routing policy: delegate only when it materially improves quality, and use `executor` outside team mode.

The net effect is that prompt behavior is not a single file; it is a stack: AGENTS authority -> generated developer instructions -> role prompt -> runtime overlay -> worker overlay.

## 7) Strengths and Gaps for a Reusable Agent Harness

### Strengths

- Clear persistence semantics: Ralph state is explicit, validated, and terminalized in code rather than implied by chat behavior.
- Strong inspection surface: `state`, `mailbox`, `task`, and `HUD` files make the runtime observable without reverse-engineering a live session.
- Good separation of concerns: planning, execution, verification, and worker bootstrap are split across distinct files and skills.
- Model/prompt control is explicit: the repo can route by role, tier, posture, and even exact resolved model for mini-specific prompt adaptation (`references/oh-my-codex/src/agents/native-config.ts`).
- Team bootstrap is careful about workspace safety: worker overlays are applied without mutating the source AGENTS contract (`references/oh-my-codex/src/team/worker-bootstrap.ts`).

### Gaps

- The policy surface is spread across many files, so drift is a real risk: `AGENTS.md`, `templates/AGENTS.md`, `prompts/*.md`, `docs/contracts/*`, and generated config all carry overlapping rules.
- Ralph, team, ultrawork, and autopilot are adjacent but not unified. That helps specialization, but it raises the cognitive cost of building a truly reusable harness.
- Some behavior is documented in tests and reference docs rather than centralized in one implementation path, especially around session scope and completion semantics.
- The repo has intentionally deprecated the old linked `team ralph` path, which is cleaner architecturally, but it also means downstream workflows must now explicitly choose whether they want team execution or a separate Ralph follow-up.

### Bottom line

This repo already has most of the pieces needed for a reusable agent harness: explicit state, explicit prompts, explicit worker protocols, and explicit verification. The main limitation is not missing machinery; it is **contract dispersion**. The more reusable the harness becomes, the more important it is to keep the planning gate, Ralph contract, team runtime, and prompt-generation rules synchronized.
