---
title: Ralph Loop in oh-my-claudecode
description: Evidence-based analysis of the Ralph persistence loop, its planning gate, hook/state runtime, and reuse tradeoffs in the oh-my-claudecode reference repo.
doc_type: reference
scope:
  - ralph
  - ralplan
  - hooks
  - state
  - agent orchestration
covers:
  - references/oh-my-claudecode/skills/ralph/SKILL.md
  - references/oh-my-claudecode/skills/ralplan/SKILL.md
  - references/oh-my-claudecode/skills/plan/SKILL.md
  - references/oh-my-claudecode/scripts/persistent-mode.mjs
  - references/oh-my-claudecode/scripts/keyword-detector.mjs
  - references/oh-my-claudecode/hooks/hooks.json
---

# Ralph Loop Analysis

## 1) Exact Ralph Concept

Ralph is not just “keep trying.” In this repo it is a **PRD-driven persistence loop** that keeps working until **all user stories in `prd.json` pass and are reviewer-verified**, while wrapping ultrawork-style parallel execution with session persistence and mandatory verification before completion ([`skills/ralph/SKILL.md`](../../../references/oh-my-claudecode/skills/ralph/SKILL.md)).

The skill makes that concrete:
- If no PRD exists, it auto-generates a scaffold and then **refines generic acceptance criteria into task-specific ones** before any implementation starts ([`skills/ralph/SKILL.md`](../../../references/oh-my-claudecode/skills/ralph/SKILL.md)).
- It selects the next incomplete story, implements it, verifies each criterion with fresh evidence, marks `passes: true`, and records progress in `progress.txt` ([`skills/ralph/SKILL.md`](../../../references/oh-my-claudecode/skills/ralph/SKILL.md)).
- It treats completion as conditional on reviewer verification, then an optional deslop pass, then post-deslop regression checks, and only after that calls `/oh-my-claudecode:cancel` ([`skills/ralph/SKILL.md`](../../../references/oh-my-claudecode/skills/ralph/SKILL.md)).

## 2) Planning Flow Before Execution

There are two planning surfaces before Ralph execution:

1. **`ralplan` / `plan` consensus gate** for vague execution requests.
   - `ralplan` redirects underspecified `ralph`/`autopilot`/`team` prompts into a Planner -> Architect -> Critic loop ([`skills/ralplan/SKILL.md`](../../../references/oh-my-claudecode/skills/ralplan/SKILL.md), [`skills/plan/SKILL.md`](../../../references/oh-my-claudecode/skills/plan/SKILL.md)).
   - The plan must include a compact RALPLAN-DR summary, and in deliberate mode also a pre-mortem and expanded test plan ([`skills/plan/SKILL.md`](../../../references/oh-my-claudecode/skills/plan/SKILL.md)).
   - On approval, the plan handoff explicitly transitions to `team` or `ralph`; it does not implement directly in the planning agent ([`skills/plan/SKILL.md`](../../../references/oh-my-claudecode/skills/plan/SKILL.md)).

2. **Ralph’s own PRD setup** for direct execution.
   - Ralph auto-scaffolds `prd.json` if missing, but the skill requires replacing generic acceptance criteria with concrete story-level criteria before implementation ([`skills/ralph/SKILL.md`](../../../references/oh-my-claudecode/skills/ralph/SKILL.md)).
   - That makes planning part of the execution loop, not a separate optional step.

Net: `ralplan` is the pre-execution gate for ambiguous requests; `ralph` is the execution loop that still forces story-level planning when it starts without a usable PRD.

## 3) Loop Execution and Completion Logic

The runtime loop is enforced by the stop hook, not just by the skill prompt.

- `hooks.json` wires `Stop` to `persistent-mode.cjs`, so when Claude stops, the hook checks whether Ralph is still active and blocks the turn if work is incomplete ([`hooks/hooks.json`](../../../references/oh-my-claudecode/hooks/hooks.json)).
- `persistent-mode.mjs` reads session-scoped or legacy state files, checks whether the Ralph state is active, and if so increments `iteration`, writes the updated state back, and emits a blocking reason like `[RALPH LOOP - ITERATION X/Y] Work is NOT done` ([`scripts/persistent-mode.mjs`](../../../references/oh-my-claudecode/scripts/persistent-mode.mjs)).
- If the loop reaches `max_iterations`, it either extends the limit by 10 or disables itself at a hard ceiling, so the loop is bounded rather than infinite ([`scripts/persistent-mode.mjs`](../../../references/oh-my-claudecode/scripts/persistent-mode.mjs)).
- Ralph completion is not “I think it’s done.” The skill requires reviewer verification, then a mandatory deslop pass unless opted out, then rerun of build/test/lint checks, and only then a clean exit via `/oh-my-claudecode:cancel` ([`skills/ralph/SKILL.md`](../../../references/oh-my-claudecode/skills/ralph/SKILL.md)).

In the prompt contract, the continuation signal is explicit: the skill tells the model that “the boulder never stops,” meaning the iteration continues until verified completion ([`skills/ralph/SKILL.md`](../../../references/oh-my-claudecode/skills/ralph/SKILL.md)).

## 4) Agent / Skill / Subagent Model

The repo’s harness is layered:

- `CLAUDE.md` defines the orchestration vocabulary, agent catalog, and model routing rules, including `haiku` for quick lookups, `sonnet` for standard work, and `opus` for architecture/deep analysis ([`CLAUDE.md`](../../../references/oh-my-claudecode/CLAUDE.md)).
- `skills/AGENTS.md` lists the execution modes and the reusable skill categories, showing that Ralph is a skill-level orchestration wrapper rather than a new primitive agent type ([`skills/AGENTS.md`](../../../references/oh-my-claudecode/skills/AGENTS.md)).
- `ultrawork` is the parallel execution layer Ralph composes on top of; it routes independent work to `executor` subagents with explicit model tiers and does not itself provide persistence ([`skills/ultrawork/SKILL.md`](../../../references/oh-my-claudecode/skills/ultrawork/SKILL.md)).
- `team` is the newer coordinated-agent surface; it stages `team-plan -> team-prd -> team-exec -> team-verify -> team-fix`, with explicit specialist routing and a documented `linked_ralph` composition path ([`skills/team/SKILL.md`](../../../references/oh-my-claudecode/skills/team/SKILL.md)).

Ralph therefore behaves like a policy wrapper over existing skills and subagents:
- it delegates work to ultrawork/executor-style agents,
- it uses reviewer agents for verification,
- and it relies on skill-level prompts plus state files for persistence and completion.

## 5) Hooks, State, and Runtime Mechanisms

The runtime contract is mostly file-and-hook driven:

- `hooks.json` wires `UserPromptSubmit`, `SessionStart`, `PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `SubagentStart`, `SubagentStop`, `PreCompact`, `Stop`, and `SessionEnd` into small hook scripts ([`hooks/hooks.json`](../../../references/oh-my-claudecode/hooks/hooks.json)).
- `keyword-detector.mjs` activates mode state on prompt submission, injects `[MAGIC KEYWORD: RALPH]` and the loaded skill content, and auto-creates `ralph-state.json` with `iteration`, `max_iterations`, `prompt`, `session_id`, and `linked_ultrawork` fields ([`scripts/keyword-detector.mjs`](../../../references/oh-my-claudecode/scripts/keyword-detector.mjs)).
- The same detector links Ralph and Team state when both are present, so cancellation and lifecycle can cascade across modes ([`scripts/keyword-detector.mjs`](../../../references/oh-my-claudecode/scripts/keyword-detector.mjs), [`skills/team/SKILL.md`](../../../references/oh-my-claudecode/skills/team/SKILL.md)).
- `session-start.mjs` restores active Ralph context on new sessions and falls back to legacy state only when session-scoped state is unavailable ([`scripts/session-start.mjs`](../../../references/oh-my-claudecode/scripts/session-start.mjs)).
- `post-tool-use-failure.mjs` stores the last tool error and retry count, which `persistent-mode.mjs` can turn into retry guidance on the next stop cycle ([`scripts/post-tool-use-failure.mjs`](../../../references/oh-my-claudecode/scripts/post-tool-use-failure.mjs), [`scripts/persistent-mode.mjs`](../../../references/oh-my-claudecode/scripts/persistent-mode.mjs)).
- `context-guard-stop.mjs` can block a stop when context is too full, but it explicitly avoids deadlocking context-limit or user-abort stops ([`scripts/context-guard-stop.mjs`](../../../references/oh-my-claudecode/scripts/context-guard-stop.mjs)).
- `verify-deliverables.mjs` is advisory only, so deliverable enforcement exists, but it is not a hard blocker ([`scripts/verify-deliverables.mjs`](../../../references/oh-my-claudecode/scripts/verify-deliverables.mjs)).

State is session-aware in the newer path, but the repo still carries legacy fallbacks under `.omc/state/*.json`, which is a compatibility strength and a consistency risk ([`skills/cancel/SKILL.md`](../../../references/oh-my-claudecode/skills/cancel/SKILL.md), [`scripts/keyword-detector.mjs`](../../../references/oh-my-claudecode/scripts/keyword-detector.mjs)).

## 6) Prompt and System-Instruction Surfaces

Three layers shape what the model sees:

- `CLAUDE.md` is the top-level operating contract: delegate work, verify outcomes, use the lightest-weight path, and rely on hooks/state for orchestration ([`CLAUDE.md`](../../../references/oh-my-claudecode/CLAUDE.md)).
- Skill frontmatter and bodies encode mode-specific policy, including Ralph’s PRD loop, planning gate behavior, and cancel requirements ([`skills/ralph/SKILL.md`](../../../references/oh-my-claudecode/skills/ralph/SKILL.md), [`skills/ralplan/SKILL.md`](../../../references/oh-my-claudecode/skills/ralplan/SKILL.md)).
- `keyword-detector.mjs` turns prompts into structured mode entries by injecting skill text or explicit `Skill(...)` instructions, so the user-facing phrase and the underlying orchestration contract stay aligned ([`scripts/keyword-detector.mjs`](../../../references/oh-my-claudecode/scripts/keyword-detector.mjs)).

That means the “system instruction surface” is distributed, not centralized: repo docs, skill markdown, and hook-generated context all contribute.

## 7) Strengths and Gaps for a Reusable Agent Harness

**Strengths**
- Clear separation of concerns: keyword detection, skill policy, state persistence, stop enforcement, and reviewer cleanup are split across files ([`hooks/hooks.json`](../../../references/oh-my-claudecode/hooks/hooks.json), [`scripts/persistent-mode.mjs`](../../../references/oh-my-claudecode/scripts/persistent-mode.mjs)).
- Session-aware state prevents most cross-session bleed and supports resume ([`scripts/session-start.mjs`](../../../references/oh-my-claudecode/scripts/session-start.mjs), [`skills/cancel/SKILL.md`](../../../references/oh-my-claudecode/skills/cancel/SKILL.md)).
- Ralph composes well with ultrawork and team, so the harness can scale from single-threaded persistence to parallel execution without changing the basic contract ([`skills/ultrawork/SKILL.md`](../../../references/oh-my-claudecode/skills/ultrawork/SKILL.md), [`skills/team/SKILL.md`](../../../references/oh-my-claudecode/skills/team/SKILL.md)).
- The completion path is unusually strict: story-level acceptance criteria, reviewer verification, deslop, regression rerun, then cancel ([`skills/ralph/SKILL.md`](../../../references/oh-my-claudecode/skills/ralph/SKILL.md)).

**Gaps**
- The harness is still heavily prompt- and convention-driven; there is no single typed “Ralph state machine” API exposed to callers.
- Several flows keep legacy fallback paths, which improves compatibility but makes state semantics harder to reason about across sessions ([`skills/cancel/SKILL.md`](../../../references/oh-my-claudecode/skills/cancel/SKILL.md)).
- Some enforcement is advisory rather than hard blocking, especially deliverable verification, so completion still depends on the model obeying policy ([`scripts/verify-deliverables.mjs`](../../../references/oh-my-claudecode/scripts/verify-deliverables.mjs)).
- Ralph’s loop bounds are heuristic (`max_iterations` with extension and hard ceiling), which is practical but not strongly task-adaptive ([`scripts/persistent-mode.mjs`](../../../references/oh-my-claudecode/scripts/persistent-mode.mjs)).

## Bottom Line

Ralph in this repo is best understood as a **verified persistence wrapper**: planning is forced into concrete stories, execution is repeated until reviewer-checked completion, and stop hooks/state files keep the model from exiting early. That makes it a strong reusable harness for “must finish” work, but it remains a convention-heavy system whose guarantees depend on prompt discipline, hook reliability, and consistent state cleanup.
