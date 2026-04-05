---
title: Ralph Loop Concept Synthesis
description: Precise cross-repo definition of Ralph loop, its minimal lifecycle, required harness primitives, implementation surfaces, and project design implications.
doc_type: reference
scope:
  - ralph loop
  - persistence loops
  - verification and cancellation
  - agent orchestration
covers:
  - references/oh-my-openagent/
  - references/oh-my-claudecode/
  - references/oh-my-codex/
  - references/superpowers/
---

# Ralph Loop Concept Synthesis

## Working Definition

Ralph loop is a task-scoped persistence loop for agentic execution: it keeps one owner on one task until the task is genuinely complete, then stops only after a completion signal is verified or an explicit terminal condition fires. Across the repos, the common contract is not "keep trying" in the abstract; it is "continue work, preserve state, verify fresh evidence, and only then exit." The direct loop surfaces all enforce some combination of completion detection, retries, state persistence, and cancelability (`references/oh-my-openagent/docs/reference/features.md:476-496`, `references/oh-my-openagent/src/hooks/ralph-loop/AGENTS.md:7-18`, `references/oh-my-claudecode/skills/ralph/SKILL.md:11-13`, `references/oh-my-codex/skills/ralph/SKILL.md:11-13`).

## Minimal Lifecycle

The minimal portable lifecycle is:

1. `plan` - establish the smallest acceptable task shape and success criteria before execution. Some repos do this explicitly with PRD/planning gates (`references/oh-my-claudecode/skills/ralplan/SKILL.md:39-58`, `references/oh-my-claudecode/skills/autopilot/SKILL.md:40-52`, `references/superpowers/skills/writing-plans/SKILL.md:10-18`), while `oh-my-openagent` can start from task text and defer richer scoping to the loop itself (`references/oh-my-openagent/src/features/builtin-commands/templates/ralph-loop.ts:24-29`).
2. `execute` - do real work continuously, usually with parallel subagents or background work when available (`references/oh-my-openagent/src/hooks/ralph-loop/AGENTS.md:12-18`, `references/oh-my-claudecode/skills/autopilot/SKILL.md:53-57`, `references/oh-my-codex/skills/ralph/SKILL.md:57-77`).
3. `verify` - run fresh evidence, not just intuition. Verification must include the command that proves completion and then reading its output (`references/oh-my-claudecode/skills/ralph/SKILL.md:71-80`, `references/oh-my-codex/skills/ralph/SKILL.md:71-89`, `references/superpowers/skills/verification-before-completion/SKILL.md:16-38`).
4. `fix` - if verification fails or the completion signal is not yet justified, repair the gap and re-run the same checks (`references/oh-my-openagent/src/hooks/ralph-loop/AGENTS.md:14-17`, `references/oh-my-claudecode/skills/ralph/SKILL.md:107-115`, `references/oh-my-codex/skills/ralph/SKILL.md:86-91`).
5. `repeat` - continue the loop until the task is complete, the reviewer approves, or a maximum iteration bound is hit (`references/oh-my-openagent/docs/reference/features.md:491-496`, `references/oh-my-claudecode/skills/ralph/SKILL.md:88-115`, `references/oh-my-codex/skills/ralph/SKILL.md:88-91`).
6. `stop` - terminate on completion, cancel, or bounded failure; do not silently drift into a partial finish (`references/oh-my-openagent/docs/reference/features.md:494-538`, `references/oh-my-claudecode/skills/ralph/SKILL.md:113-115`, `references/oh-my-codex/docs/contracts/ralph-cancel-contract.md:8-18`).

In short: plan enough to know what "done" means, execute continuously, verify with fresh evidence, fix what failed, and stop only at an explicit terminal condition.

## Required Harness Primitives

The repos converge on a small set of harness primitives that make Ralph loop work:

- Persistent mode state with iteration, phase, ownership, and timestamps. `oh-my-codex` freezes this as `.omx/state/{scope}/ralph-state.json` with `active`, `iteration`, `max_iterations`, `current_phase`, `started_at`, and `completed_at` fields (`references/oh-my-codex/docs/contracts/ralph-state-contract.md:5-22`), while `oh-my-openagent` uses `.sisyphus/ralph-loop.local.md` with session id, prompt, iteration count, max iterations, completion promise, and ultrawork flag (`references/oh-my-openagent/src/hooks/ralph-loop/AGENTS.md:36-41`).
- A completion sentinel plus detector. `oh-my-openagent` terminates on `<promise>DONE</promise>` (`references/oh-my-openagent/src/hooks/ralph-loop/AGENTS.md:14-17`, `references/oh-my-openagent/src/features/builtin-commands/templates/ralph-loop.ts:5-8`), while `oh-my-codex` and `oh-my-claudecode` pair that idea with reviewer approval and fresh verification evidence (`references/oh-my-codex/skills/ralph/SKILL.md:71-80`, `references/oh-my-claudecode/skills/ralph/SKILL.md:78-115`).
- A continuation mechanism. The loop must be able to inject another prompt or re-dispatch the task when the agent stops early or verification is not yet satisfied (`references/oh-my-openagent/src/hooks/ralph-loop/AGENTS.md:14-17`, `references/oh-my-openagent/src/features/builtin-commands/templates/ralph-loop.ts:5-8`).
- A cancellation path that terminalizes state cleanly. `oh-my-openagent` exposes `/cancel-ralph` and `/stop-continuation` (`references/oh-my-openagent/docs/reference/features.md:494-538`), and `oh-my-codex` requires scoped cancellation that sets `active=false`, `current_phase='cancelled'`, and `completed_at` without touching unrelated sessions (`references/oh-my-codex/docs/contracts/ralph-cancel-contract.md:8-18`).
- Fresh verification commands and evidence gating. All direct Ralph surfaces require a real command run, reading output, and only then claiming completion (`references/oh-my-claudecode/skills/ralph/SKILL.md:71-80`, `references/oh-my-codex/skills/ralph/SKILL.md:71-89`, `references/superpowers/skills/verification-before-completion/SKILL.md:10-38`).
- Planning and artifact storage for non-trivial tasks. `oh-my-claudecode` front-loads PRD/planning gates through `ralplan` and `autopilot` (`references/oh-my-claudecode/skills/ralplan/SKILL.md:39-58`, `references/oh-my-claudecode/skills/autopilot/SKILL.md:40-72`), and `oh-my-codex` persists canonical PRD/progress artifacts (`references/oh-my-codex/skills/ralph/SKILL.md:45-56`, `references/oh-my-codex/docs/contracts/ralph-state-contract.md:82-89`).
- Parallel or background worker support for execution and verification. `oh-my-claudecode` and `oh-my-codex` both explicitly use parallel delegation and background ops for long-running work (`references/oh-my-claudecode/skills/ralph/SKILL.md:32-41`, `references/oh-my-codex/skills/ralph/SKILL.md:33-41`, `references/superpowers/skills/subagent-driven-development/SKILL.md:8-12`).

## Direct vs Indirect Implementations

| Repo | Classification | Why |
|---|---|---|
| `references/oh-my-openagent/` | Direct | It ships `/ralph-loop`, `/ulw-loop`, cancel commands, a loop hook, a completion detector, and prompt injection that actually runs the cycle (`references/oh-my-openagent/docs/reference/features.md:476-538`, `references/oh-my-openagent/src/hooks/ralph-loop/AGENTS.md:7-18`). |
| `references/oh-my-claudecode/` | Direct | It has a dedicated `ralph` skill and treats Ralph as a first-class execution mode with persistence, verification, deslop cleanup, and cancel-to-exit semantics (`references/oh-my-claudecode/skills/ralph/SKILL.md:12-14`, `references/oh-my-claudecode/README.md:180-189`). |
| `references/oh-my-codex/` | Direct | It has a dedicated `ralph` skill plus CLI/runtime/state contracts that define the loop, its phases, PRD/progress artifacts, and scoped cancellation (`references/oh-my-codex/skills/ralph/SKILL.md:10-13`, `references/oh-my-codex/src/cli/ralph.ts:11-23`, `references/oh-my-codex/docs/contracts/ralph-state-contract.md:1-29`). |
| `references/superpowers/` | Indirect | It does not define a Ralph runtime, but it supplies the enabling pieces: planning, task decomposition, subagent execution, and evidence-before-claims verification (`references/superpowers/skills/writing-plans/SKILL.md:10-18`, `references/superpowers/skills/executing-plans/SKILL.md:18-37`, `references/superpowers/skills/subagent-driven-development/SKILL.md:8-13`, `references/superpowers/skills/verification-before-completion/SKILL.md:10-38`). |

## Reusable Design Implications For This Project

1. Treat Ralph as a state machine, not a vibe. The minimum useful contract is explicit phase tracking, ownership, iteration count, and a terminal cancel/completion path (`references/oh-my-codex/docs/contracts/ralph-state-contract.md:5-22`, `references/oh-my-openagent/src/hooks/ralph-loop/AGENTS.md:36-41`).
2. Separate planning from execution. The strongest patterns front-load plan/spec generation when scope is unclear, then let Ralph handle the persistent execution loop (`references/oh-my-claudecode/skills/ralplan/SKILL.md:64-75`, `references/oh-my-claudecode/skills/autopilot/SKILL.md:40-73`, `references/superpowers/skills/writing-plans/SKILL.md:21-43`).
3. Make verification mandatory and fresh. A loop is incomplete unless the harness can prove it with a newly run command and readable output, not agent self-report (`references/superpowers/skills/verification-before-completion/SKILL.md:16-38`, `references/oh-my-codex/skills/ralph/SKILL.md:71-89`).
4. Keep cancellation scoped. Cancel should end the active loop cleanly without mutating unrelated sessions or hidden state (`references/oh-my-codex/docs/contracts/ralph-cancel-contract.md:8-18`, `references/oh-my-openagent/docs/reference/features.md:534-538`).
5. Prefer explicit completion signals plus bounded retries. `oh-my-openagent` uses a sentinel and iteration ceiling; `oh-my-claudecode` and `oh-my-codex` add reviewer approval and post-verification cleanup. That combination is the portable core worth reusing here (`references/oh-my-openagent/src/features/builtin-commands/templates/ralph-loop.ts:18-29`, `references/oh-my-claudecode/skills/ralph/SKILL.md:93-115`, `references/oh-my-codex/skills/ralph/SKILL.md:76-91`).

## Bottom Line

Ralph loop is best understood as a bounded, stateful, evidence-gated completion loop: plan enough to define done, execute continuously, verify with fresh output, fix what fails, repeat until complete, and stop only on verified success, explicit cancel, or a documented failure bound.
