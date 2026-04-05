---
title: Ralph Loop in oh-my-openagent
description: Concise reference analysis of how oh-my-openagent defines, plans, runs, and verifies the Ralph Loop and related orchestration machinery.
doc_type: reference
scope:
  - ralph-loop
  - orchestration
  - planning
  - hooks
  - agents
covers:
  - references/oh-my-openagent/README.md
  - references/oh-my-openagent/docs/guide/orchestration.md
  - references/oh-my-openagent/src/hooks/ralph-loop/
  - references/oh-my-openagent/src/hooks/start-work/
  - references/oh-my-openagent/src/agents/
  - references/oh-my-openagent/src/features/builtin-commands/
---

# Ralph Loop in `oh-my-openagent`

## 1) Exact Ralph Loop concept in this repo

In this repo, Ralph Loop is not just a prompt pattern. It is a named builtin command plus a stateful hook subsystem that keeps re-injecting work until the task is done. The README frames it as a “self-referential loop” that “doesn’t stop until 100% done” and ties it directly to `/ulw-loop` ([README.md:151](../../../references/oh-my-openagent/README.md#L151-L151)). The command surface is explicit: `ralph-loop` and `ulw-loop` are builtin commands, with `ulw-loop` described as an ultrawork loop that continues until verified completion ([commands.ts:39-60](../../../references/oh-my-openagent/src/features/builtin-commands/commands.ts#L39-L60)).

The loop has two modes:

- `ralph-loop`: regular self-referential completion loop with a configurable max iteration count and a completion promise tag ([ralph-loop.ts:1-29](../../../references/oh-my-openagent/src/features/builtin-commands/templates/ralph-loop.ts#L1-L29)).
- `ulw-loop`: ultrawork mode, where the system requires Oracle verification before the loop can end and there is no iteration limit ([ralph-loop.ts:31-57](../../../references/oh-my-openagent/src/features/builtin-commands/templates/ralph-loop.ts#L31-L57)).

So the repo’s “Ralph loop” concept is: prompt the agent to keep working, persist loop state in a file, detect completion tags in the transcript, and auto-inject follow-up prompts until the loop is truly finished.

## 2) Planning flow before execution

The repo draws a hard line between planning and execution. The orchestration guide says the precise path is `@plan` then `/start-work`, with Prometheus planning and Atlas executing ([orchestration.md:7-25](../../../references/oh-my-openagent/docs/guide/orchestration.md#L7-L25)). Prometheus is read-only except for `.sisyphus/` markdown files, and its interview flow explicitly alternates between user questions, exploration, Metis gap analysis, and Momus review before the plan is finalized ([orchestration.md:79-163](../../../references/oh-my-openagent/docs/guide/orchestration.md#L79-L163)).

The Prometheus planner is assembled from modular prompt sections in `PROMETHEUS_SYSTEM_PROMPT`, and its permissions intentionally allow edit/bash/webfetch/question while still relying on a `prometheus-md-only` hook to keep writes constrained to plan files ([system-prompt.ts:15-32](../../../references/oh-my-openagent/src/agents/prometheus/system-prompt.ts#L15-L32)). The planner command surface is materialized through the builtin command layer, which routes `start-work` to Atlas and uses a dedicated `START_WORK_TEMPLATE` ([commands.ts:75-90](../../../references/oh-my-openagent/src/features/builtin-commands/commands.ts#L75-L90), [start-work.ts:1-44](../../../references/oh-my-openagent/src/features/builtin-commands/templates/start-work.ts#L1-L44)).

Before execution, `start-work` requires a Prometheus plan in `.sisyphus/plans/`, loads or creates `.sisyphus/boulder.json`, and forces the plan to be read before any task delegation happens ([start-work.ts:14-45](../../../references/oh-my-openagent/src/features/builtin-commands/templates/start-work.ts#L14-L45)). The template also requires the plan to be broken into concrete implementation-level subtasks before work starts ([start-work.ts:93-112](../../../references/oh-my-openagent/src/features/builtin-commands/templates/start-work.ts#L93-L112)).

## 3) Loop execution and completion logic

The runtime implementation lives in `src/hooks/ralph-loop/`. `createRalphLoopHook()` wires together state control, session recovery, transcript inspection, and event handling ([ralph-loop-hook.ts:40-89](../../../references/oh-my-openagent/src/hooks/ralph-loop/ralph-loop-hook.ts#L40-L89)). `startLoop()` persists state and, when needed, snapshots the current message count so later idle events can judge whether progress actually moved ([ralph-loop-hook.ts:68-85](../../../references/oh-my-openagent/src/hooks/ralph-loop/ralph-loop-hook.ts#L68-L85), [loop-state-controller.ts:21-65](../../../references/oh-my-openagent/src/hooks/ralph-loop/loop-state-controller.ts#L21-L65)).

The state file is a frontmatter-backed record with `active`, `iteration`, `completion_promise`, `ultrawork`, `verification_pending`, `strategy`, and session metadata ([storage.ts:1-80](../../../references/oh-my-openagent/src/hooks/ralph-loop/storage.ts#L1-L80), [types.ts:1-19](../../../references/oh-my-openagent/src/hooks/ralph-loop/types.ts#L1-L19)). On each transcript completion signal, the completion handler either:

- clears the loop and emits a success toast for normal Ralph Loop completion, or
- for ultrawork, transitions into a verification phase, rewrites the completion promise to `ULTRAWORK_VERIFICATION_PROMISE`, injects a new continuation prompt, and tells the user Oracle verification is required ([completion-handler.ts:13-65](../../../references/oh-my-openagent/src/hooks/ralph-loop/completion-handler.ts#L13-L65), [loop-state-controller.ts:120-175](../../../references/oh-my-openagent/src/hooks/ralph-loop/loop-state-controller.ts#L120-L175)).

The continuation prompt is itself stateful: it prefixes the next turn with `ultrawork` when needed, distinguishes normal continuation from verification-failure recovery, and explicitly tells the agent to keep going until the prompt tag is emitted ([continuation-prompt-builder.ts:8-76](../../../references/oh-my-openagent/src/hooks/ralph-loop/continuation-prompt-builder.ts#L8-L76)). The injector preserves the prior agent/model/tool context so the next prompt continues in the same runtime shape instead of starting fresh ([continuation-prompt-injector.ts:20-83](../../../references/oh-my-openagent/src/hooks/ralph-loop/continuation-prompt-injector.ts#L20-L83)).

The key completion rule is therefore:

`task work -> emit <promise>... -> detect it in transcript -> maybe require Oracle -> re-inject continuation or clear state`

That is enforced by code, not just by instruction text.

## 4) Agent / skill / subagent model

The repo uses a category-first delegation model rather than hard-coding every subagent by model name. The README says Sisyphus delegates by category, not model, and that the category maps to the right model automatically ([README.md:179-190](../../../references/oh-my-openagent/README.md#L179-L190)). Atlas’s agent metadata reinforces that it is the orchestrator that “complete[s] ALL tasks in a todo list until fully done” and delegates by `task()` ([atlas/agent.ts:1-10,101-142](../../../references/oh-my-openagent/src/agents/atlas/agent.ts#L1-L10), [atlas/agent.ts:101-142](../../../references/oh-my-openagent/src/agents/atlas/agent.ts#L101-L142)).

The built-in agent layering is:

- Sisyphus: main orchestrator, intent gate, delegation, verification, task tracking ([sisyphus/default.ts:169-184](../../../references/oh-my-openagent/src/agents/sisyphus/default.ts#L169-L184), [sisyphus/gpt-5-4.ts:109-123](../../../references/oh-my-openagent/src/agents/sisyphus/gpt-5-4.ts#L109-L123)).
- Sisyphus-Junior: focused executor; cannot delegate; must verify before completion ([sisyphus-junior/default.ts:22-47](../../../references/oh-my-openagent/src/agents/sisyphus-junior/default.ts#L22-L47)).
- Prometheus: read-only planner for interview-driven plan creation ([system-prompt.ts:22-32](../../../references/oh-my-openagent/src/agents/prometheus/system-prompt.ts#L22-L32), [orchestration.md:81-116](../../../references/oh-my-openagent/docs/guide/orchestration.md#L81-L116)).

Skills are not an afterthought. Both Sisyphus prompts explicitly tell the agent to load relevant skills immediately when there is any plausible domain overlap ([sisyphus/gpt-5-4.ts:136-145](../../../references/oh-my-openagent/src/agents/sisyphus/gpt-5-4.ts#L136-L145), [sisyphus/gpt-5-4.ts:355-378](../../../references/oh-my-openagent/src/agents/sisyphus/gpt-5-4.ts#L355-L378)). The agent configuration layer also materializes `sisyphus-junior` and `prometheus`, and can demote the built-in `plan` agent to Prometheus semantics when configured ([agent-config-handler.ts:149-259](../../../references/oh-my-openagent/src/plugin-handlers/agent-config-handler.ts#L149-L259)).

## 5) Hooks / state / runtime mechanisms

The hook system is the real enforcement layer. `createHooks()` composes core hooks, continuation hooks, and skill hooks into a single runtime bundle ([create-hooks.ts:25-80](../../../references/oh-my-openagent/src/create-hooks.ts#L25-L80)). The continuation group includes `todo-continuation-enforcer`, `stop-continuation-guard`, compaction hooks, and the Atlas hook itself ([create-continuation-hooks.ts:1-84](../../../references/oh-my-openagent/src/plugin/hooks/create-continuation-hooks.ts#L1-L84)).

Important runtime state files and in-memory state:

- `.sisyphus/boulder.json` tracks the active plan, session IDs, plan name, and optional worktree path ([boulder-state/storage.ts:14-65](../../../references/oh-my-openagent/src/features/boulder-state/storage.ts#L14-L65), [boulder-state/types.ts:1-23](../../../references/oh-my-openagent/src/features/boulder-state/types.ts#L1-L23)).
- `session-state.ts` tracks the current agent per session and registered agent names for routing and display ([state.ts:1-65](../../../references/oh-my-openagent/src/features/claude-code-session-state/state.ts#L1-L65)).
- `stop-continuation-guard` can halt the loop and clear continuation markers, and it also cancels descendant background tasks ([hook.ts:1-76](../../../references/oh-my-openagent/src/hooks/stop-continuation-guard/hook.ts#L1-L76)).
- `todo-continuation-enforcer` marks a session as recovering, cancels countdowns, and resumes on later events ([index.ts:1-40](../../../references/oh-my-openagent/src/hooks/todo-continuation-enforcer/index.ts#L1-L40), [handler.ts:1-55](../../../references/oh-my-openagent/src/hooks/todo-continuation-enforcer/handler.ts#L1-L55)).

The `start-work` hook is the main runtime bridge from command text to active orchestration. It recognizes the command by template marker, chooses Atlas if registered, resolves worktree state, and injects the session/context block that the execution agent will consume ([start-work-hook.ts:66-152](../../../references/oh-my-openagent/src/hooks/start-work/start-work-hook.ts#L66-L152)).

## 6) System-prompt or command-template surfaces

This repo exposes the harness mostly through prompt templates:

- `RALPH_LOOP_TEMPLATE` defines the basic self-referential contract, completion promise, and exit conditions ([ralph-loop.ts:1-29](../../../references/oh-my-openagent/src/features/builtin-commands/templates/ralph-loop.ts#L1-L29)).
- `ULW_LOOP_TEMPLATE` upgrades that contract to require Oracle verification before the loop can stop ([ralph-loop.ts:31-57](../../../references/oh-my-openagent/src/features/builtin-commands/templates/ralph-loop.ts#L31-L57)).
- `START_WORK_TEMPLATE` defines the plan-selection, `boulder.json`, and task-breakdown rules for execution ([start-work.ts:1-128](../../../references/oh-my-openagent/src/features/builtin-commands/templates/start-work.ts#L1-L128)).
- `Sisyphus` prompts enforce intent gating, exploration, delegation, verification, and task completion contracts ([sisyphus/default.ts:169-479](../../../references/oh-my-openagent/src/agents/sisyphus/default.ts#L169-L479), [sisyphus/gpt-5-4.ts:272-353](../../../references/oh-my-openagent/src/agents/sisyphus/gpt-5-4.ts#L272-L353)).
- `Sisyphus-Junior` prompts are narrower and more execution-focused, with verification gating and stronger anti-optimism rules ([sisyphus-junior/default.ts:22-47](../../../references/oh-my-openagent/src/agents/sisyphus-junior/default.ts#L22-L47), [sisyphus-junior/gemini.ts:23-165](../../../references/oh-my-openagent/src/agents/sisyphus-junior/gemini.ts#L23-L165)).

Prometheus’s system prompt is assembled from modular sections and model-specific variants, which makes the planner easier to tune than a single monolithic prompt ([system-prompt.ts:1-85](../../../references/oh-my-openagent/src/agents/prometheus/system-prompt.ts#L1-L85)).

## 7) Notable strengths and gaps for a reusable agent harness

Strengths:

- Clear separation of planning and execution, with distinct planner, conductor, and executor roles ([orchestration.md:29-75](../../../references/oh-my-openagent/docs/guide/orchestration.md#L29-L75)).
- State-backed continuation, so the harness can resume instead of hoping the model remembers context ([boulder-state/storage.ts:18-65](../../../references/oh-my-openagent/src/features/boulder-state/storage.ts#L18-L65), [ralph-loop/storage.ts:1-80](../../../references/oh-my-openagent/src/hooks/ralph-loop/storage.ts#L1-L80)).
- Model-specific prompts and category-based routing, which makes the harness adaptable across providers ([atlas/agent.ts:7-10](../../../references/oh-my-openagent/src/agents/atlas/agent.ts#L7-L10), [sisyphus/gpt-5-4.ts:13-21](../../../references/oh-my-openagent/src/agents/sisyphus/gpt-5-4.ts#L13-L21)).
- Verification is built into both prompts and runtime hooks, instead of being left to user judgment ([completion-handler.ts:25-64](../../../references/oh-my-openagent/src/hooks/ralph-loop/completion-handler.ts#L25-L64), [sisyphus-junior/default.ts:31-40](../../../references/oh-my-openagent/src/agents/sisyphus-junior/default.ts#L31-L40)).

Gaps / tradeoffs:

- The harness is powerful but fragmented. Ralph Loop behavior is spread across builtin commands, state storage, continuation prompts, and event handlers, so understanding it requires reading several files together rather than one obvious entry point ([commands.ts:39-60](../../../references/oh-my-openagent/src/features/builtin-commands/commands.ts#L39-L60), [ralph-loop-hook.ts:40-89](../../../references/oh-my-openagent/src/hooks/ralph-loop/ralph-loop-hook.ts#L40-L89)).
- Completion is still tag-based and transcript-driven (`<promise>...` plus Oracle text inspection), which is flexible but less structured than a dedicated machine-readable completion protocol ([ralph-loop.ts:5-8](../../../references/oh-my-openagent/src/features/builtin-commands/templates/ralph-loop.ts#L5-L8), [continuation-prompt-builder.ts:21-46](../../../references/oh-my-openagent/src/hooks/ralph-loop/continuation-prompt-builder.ts#L21-L46)).
- Several invariants depend on prompt discipline plus hook behavior working together; if a command surface or transcript shape changes, the loop can degrade in subtle ways rather than failing at a single obvious boundary ([start-work.ts:85-128](../../../references/oh-my-openagent/src/features/builtin-commands/templates/start-work.ts#L85-L128), [continuation-prompt-injector.ts:35-83](../../../references/oh-my-openagent/src/hooks/ralph-loop/continuation-prompt-injector.ts#L35-L83)).

Bottom line: this is a strong reusable harness design if you want prompt-driven orchestration with persistent state and verification gates. It is less attractive if you want a single, small, formal loop engine; the system works because many pieces agree on the same conventions.
