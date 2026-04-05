---
title: claude-automate Evaluation Against Ralph Loop
description: Assessment of how references/claude-automate compares with the Ralph loop concept, including existing loop primitives, missing control surfaces, and concrete hardening recommendations.
doc_type: reference
scope:
  - ralph loop
  - claude-automate
  - harness primitives
  - completion workflows
covers:
  - references/claude-automate/
  - docs/research/ralph-loop/00-ralph-loop-concept.md
---

# claude-automate Evaluation Against Ralph Loop

## Executive Verdict

`claude-automate` is **Ralph-adjacent but not Ralph-complete**.

It already has several pieces of a completion harness: explicit planning, AC-driven execution, verification hooks, session state, specialized agents, and a wrap-up step. But those pieces are split across separate skills/hooks/agents rather than unified into a single task-scoped completion loop with durable state, explicit terminal conditions, and a cancel contract.

In Ralph terms, the repo currently has the **shape** of a loop, not the **runtime discipline** of a loop.

## 1) Does `claude-automate` already have a Ralph-like completion loop?

Partially.

The strongest evidence is the `planning` → `implement` → `wrap` flow in `README.md`, which presents a concrete harness workflow (`references/claude-automate/README.md:92-105`, `references/claude-automate/README.md:179-195`). `CLAUDE.md` also frames the system as a layered harness with commands, agents, skills, and hooks, and explicitly treats `/start-work` and `/wrap` as the basic session lifecycle (`references/claude-automate/CLAUDE.md:45-67`, `references/claude-automate/CLAUDE.md:236-244`).

But the loop is not Ralph-like in the strict sense:

- There is no single owner that persists through execution until a verified completion signal fires.
- There is no explicit completion sentinel analogous to a terminal `DONE` signal.
- There is no scoped cancel command or cancelled terminal state.
- The state model is intentionally minimal: a single `mode` string, not a task/session state object.

The current implementation is better described as a **workflow suite** than a reusable completion loop.

## 2) Which harness primitives exist or are missing?

### Existing primitives

- **Session state file**: `.claude/state/mode` is created on session start and set to `idle` (`references/claude-automate/hooks/session-start.sh:10-14`). `planning`, `implement`, and `wrap` all write to the same file (`references/claude-automate/skills/planning/SKILL.md:42-58`, `references/claude-automate/skills/implement/SKILL.md:39-49`, `references/claude-automate/skills/wrap/SKILL.md:33-45`).
- **Hook registration**: `hooks/hooks.json` wires `SessionStart`, `PreCompact`, and `Stop` hooks into the plugin runtime (`references/claude-automate/hooks/hooks.json:1-37`).
- **Pre-compact continuation hinting**: `pre-compact.sh` reads the current mode and injects a resume instruction, including the current in-progress plan path when mode is `implement` (`references/claude-automate/hooks/pre-compact.sh:10-36`).
- **Plan state and test command metadata**: plan files carry `status` and `test-command` frontmatter, which the stop hook uses as its verification source (`references/claude-automate/.claude/plans/2026-02-27-state-management.md:1-5`, `references/claude-automate/hooks/session-stop.sh:15-39`).
- **Task decomposition and delegation**: `planning` uses explore, angel, devil, and writer delegation; `implement` uses writer/writer-high with a retry policy; `verify-web-ui` uses a multi-stage orchestrator with parallel analysis agents (`references/claude-automate/skills/planning/SKILL.md:87-203`, `references/claude-automate/skills/implement/SKILL.md:63-117`, `references/claude-automate/agents/verify-web-ui-orchestrator.md:14-140`).
- **Session continuity artifact**: `context-builder` persists dated session summaries with context, decisions, incomplete work, and next steps (`references/claude-automate/agents/context-builder.md:7-16`, `references/claude-automate/agents/context-builder.md:36-87`, `references/claude-automate/agents/context-builder.md:88-151`).

### Missing or underpowered primitives

- **Persistent task state**: there is no state object with task identity, iteration count, current phase, ownership, timestamps, or max-iteration bounds. The state-management plan explicitly chose a simple string mode and left plan lookup to `grep` (`references/claude-automate/.claude/plans/2026-02-27-state-management.md:32-36`).
- **Terminal completion signal**: nothing equivalent to a reusable completion sentinel exists. `wrap` finishes by normal cleanup and commit, not by validating a canonical done signal (`references/claude-automate/skills/wrap/SKILL.md:78-102`).
- **Scoped cancel path**: there is no `/cancel` command, no cancel hook contract, and no cancelled state transition. The `Stop` hook is a test gate, not a cancellation API (`references/claude-automate/hooks/session-stop.sh:9-39`).
- **Reusable continuation primitive**: `pre-compact.sh` can resume from mode, but it cannot re-dispatch a task, restore iteration count, or recover a completed/failed terminal state (`references/claude-automate/hooks/pre-compact.sh:10-36`).
- **Evidence retention contract**: verification exists, but the runtime often suppresses the actual output. The writer agent requires visible evidence, yet `session-stop.sh` redirects the test command output to `/dev/null` (`references/claude-automate/agents/writer.md:79-85`, `references/claude-automate/hooks/session-stop.sh:25-31`).

## 3) Planning / execution / verification / cancel structure

### Planning

`planning` is the most Ralph-like piece in the repo from a control-flow perspective. It has:

- automatic mode detection
- interview mode for vague requests
- brain reading
- codebase exploration
- AC/TC extraction
- angel expansion
- devil validation
- user confirmation
- plan file creation

That is a real pre-execution gate, not just a prompt stub (`references/claude-automate/skills/planning/SKILL.md:22-203`).

### Execution

`implement` is a bounded TDD loop over plan ACs. It loads or resumes a plan, writes `implement` into mode state, delegates brain updates, iterates ACs, escalates retries, and marks ACs done (`references/claude-automate/skills/implement/SKILL.md:39-117`).

This is strong execution structure, but it is still **plan-centric** rather than **task-loop-centric**:

- execution is driven by plan ACs
- continuation depends on the presence of incomplete ACs
- the loop ends when ACs are checked and plan status becomes `done`

That makes it a good implementation harness, but not a general completion loop runtime.

### Verification

Verification is present in three places:

- `implement` requires TDD for ACs with TCs and retries on red/green failure (`references/claude-automate/skills/implement/SKILL.md:73-99`).
- `wrap` checks that in-progress plans are complete, asks for confirmation when they are not, and can hand off to `doc-sync-checker` (`references/claude-automate/skills/wrap/SKILL.md:33-74`).
- `session-stop.sh` runs the plan’s `test-command` on stop and fails the hook if the command fails (`references/claude-automate/hooks/session-stop.sh:15-39`).

The weak point is not the existence of verification; it is the lack of a single reusable verification contract that always captures fresh evidence and preserves it as loop state.

### Cancel

Cancel is the clearest gap.

There is no explicit cancel surface in the command set or skill set. The closest thing is the `Stop` hook’s infinite-loop guard and test validation, but that is a stop-time guardrail, not a user-initiated terminal cancel path (`references/claude-automate/hooks/session-stop.sh:9-13`, `references/claude-automate/hooks/session-stop.sh:15-39`).

If Ralph is expected to stop cleanly on completion or explicit cancel, `claude-automate` currently only covers the completion-adjacent path.

## 4) Hooks, state, agents, prompts, and workflow surfaces

### Hooks

The repo has the right hook surfaces:

- `SessionStart` initializes state (`references/claude-automate/hooks/hooks.json:4-14`, `references/claude-automate/hooks/session-start.sh:10-14`)
- `PreCompact` injects a resume message (`references/claude-automate/hooks/hooks.json:15-25`, `references/claude-automate/hooks/pre-compact.sh:16-36`)
- `Stop` validates tests before exit (`references/claude-automate/hooks/hooks.json:26-36`, `references/claude-automate/hooks/session-stop.sh:15-39`)

That is a useful substrate, but the hooks are not yet unified around a shared state contract.

### State

The active state is intentionally tiny:

- `mode` is set to `idle`, `planning`, or `implement` (`references/claude-automate/.claude/plans/2026-02-27-state-management.md:17-21`, `references/claude-automate/.claude/plans/2026-02-27-state-management.md:54-58`)
- the plan path is derived by scanning files rather than storing it in state (`references/claude-automate/.claude/plans/2026-02-27-state-management.md:34-36`)

That is sufficient for mode recovery, but too weak for a reusable loop harness.

### Agents

The agent set is a real strength:

- `writer` is an execution-only modifier with explicit verification discipline (`references/claude-automate/agents/writer.md:1-21`, `references/claude-automate/agents/writer.md:79-100`)
- `test-planner` separates scenario design from execution (`references/claude-automate/agents/test-planner.md:1-52`)
- `verify-web-ui-orchestrator` composes sequential and parallel stages and keeps browser access out of the orchestrator context (`references/claude-automate/agents/verify-web-ui-orchestrator.md:14-20`, `references/claude-automate/agents/verify-web-ui-orchestrator.md:43-140`)
- `verify-web-ui` is a pure executor that collects evidence and writes `summary.json` plus artifacts (`references/claude-automate/agents/verify-web-ui.md:16-20`, `references/claude-automate/agents/verify-web-ui.md:61-132`)
- `context-builder` captures session continuity after the fact (`references/claude-automate/agents/context-builder.md:7-16`)

### Prompts

The prompts are generally disciplined:

- `planning` has a concrete step list and explicit progress notifications (`references/claude-automate/skills/planning/SKILL.md:22-40`)
- `implement` has retry policy, AC checkbox updates, and a completion prompt (`references/claude-automate/skills/implement/SKILL.md:25-117`)
- `wrap` has a terminal step order and confirmation gates (`references/claude-automate/skills/wrap/SKILL.md:24-102`)

The missing piece is that these prompts do not share a common loop protocol. Each skill owns its own local semantics.

### Workflow surfaces

The published workflow surfaces are coherent:

- `README.md` lists `/start-work`, `/planning`, `/implement`, `/wrap`, `/angel`, `/devil`, `/verify-web-ui`, and supporting utilities (`references/claude-automate/README.md:92-105`, `references/claude-automate/README.md:179-195`)
- `CLAUDE.md` defines the layered architecture, naming conventions, and working style (`references/claude-automate/CLAUDE.md:45-67`, `references/claude-automate/CLAUDE.md:79-104`, `references/claude-automate/CLAUDE.md:236-260`)
- the only directly visible command file in the `.claude/commands/` surface is a one-line `test-hook` stub (`references/claude-automate/.claude/commands/test-hook.md:1-1`)

That last point matters: the repo’s docs describe a broad command surface, but the inspected command implementation surface is very thin compared to the promise.

## 5) Strengths, gaps, and direct recommendations

### Strengths

- Strong separation of planning, execution, verification, and wrap-up.
- Good use of specialized agents instead of overloading the main context.
- A real hook pipeline already exists, which is the right place to anchor a reusable harness.
- The `verify-web-ui` stack demonstrates that the repo already understands multi-stage orchestration, evidence collection, and parallel analysis.

### Gaps

- No single task-scoped state machine.
- No explicit cancel/terminal-state contract.
- No reusable completion sentinel.
- Verification evidence is inconsistently surfaced.
- The current mode model is too small to support iteration-aware persistence.
- The repo still looks like a set of well-written tools, not one continuously running completion harness.

### Direct recommendations

1. Replace the single `mode` string with a loop state record that includes `task_id`, `phase`, `iteration`, `max_iterations`, `started_at`, `completed_at`, and `terminal_reason`.
2. Add a first-class cancel path that writes a terminal cancelled state and cleanly disables further continuation.
3. Make the verification contract explicit and durable: command, output, artifact path, and pass/fail result should be stored together.
4. Move continuation responsibility into one reusable loop primitive instead of duplicating resume logic in hooks and skills.
5. Keep the current planning/implement/wrap skills, but make them consumers of a shared loop state machine rather than the source of truth.
6. Use `verify-web-ui` as the model for stage separation and evidence capture, but do not rely on its domain-specific pipeline as the general harness abstraction.

## Bottom Line

`claude-automate` already contains many of the right pieces for a Ralph-capable harness, especially planning discipline, delegated execution, and verification surfaces. What it lacks is the small set of runtime primitives that make the loop reusable: persistent task state, explicit completion/cancel terminals, and a single continuation protocol.

In other words: the repo is a promising harness foundation, but it still needs a real completion loop kernel before it can be called Ralph-capable.
