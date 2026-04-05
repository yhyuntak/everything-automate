---
title: Superpowers Ralph-Adjacent Mechanisms
description: Analysis of planning, execution, verification, subagent, and bootstrap mechanisms in the superpowers reference repo as Ralph-like workflow analogues.
doc_type: reference
scope:
  - planning-to-execution loops
  - subagent orchestration
  - verification gates
  - plugin and hook bootstrap
covers:
  - references/superpowers/
  - references/superpowers/skills/
  - references/superpowers/hooks/
  - references/superpowers/.opencode/
---

# Superpowers Ralph-Adjacent Mechanisms

This repo does **not** name a `Ralph` system explicitly. A repo-wide search for `Ralph` under `references/superpowers` returned no matches, so the right reading is analogy rather than direct implementation. The relevant question is whether the repo contains a reusable plan-execute-verify harness. It does.

## 1. Explicit Ralph vs analogy only

There is no `Ralph` identifier, command, skill, or config surface in the tree. Instead, the repo exposes a layered workflow that looks Ralph-like in shape: bootstrap the agent, force design first, write a concrete plan, execute task-by-task, and require verification before declaring completion. The core narrative is summarized in [`references/superpowers/README.md`](../../../references/superpowers/README.md), which describes the sequence from brainstorming to planning to subagent-driven execution and review.

## 2. Planning flow

Planning starts in [`references/superpowers/skills/brainstorming/SKILL.md`](../../../references/superpowers/skills/brainstorming/SKILL.md). It hard-gates implementation until a design is written and approved, then explicitly transitions to `writing-plans`. The checklist is structured as a staged funnel: explore context, ask one question at a time, propose approaches, present design sections, write a spec, self-review it, and only then invoke planning.

The plan-writing surface is [`references/superpowers/skills/writing-plans/SKILL.md`](../../../references/superpowers/skills/writing-plans/SKILL.md). It turns an approved spec into a task list with exact files, bite-sized steps, and explicit test commands. The plan header itself requires a goal, architecture, tech stack, and checkbox tasks, which makes the output machine-readable enough for later automation.

The flow is reinforced by [`references/superpowers/skills/using-git-worktrees/SKILL.md`](../../../references/superpowers/skills/using-git-worktrees/SKILL.md), which requires isolated worktrees and a clean baseline before implementation. That makes planning a setup for controlled execution, not just a document.

## 3. Execution and verification loop

There are two execution modes. [`references/superpowers/skills/executing-plans/SKILL.md`](../../../references/superpowers/skills/executing-plans/SKILL.md) is the sequential mode: load the plan, review it critically, execute tasks in order, stop on blockers, then finish with the branch-completion workflow. [`references/superpowers/skills/subagent-driven-development/SKILL.md`](../../../references/superpowers/skills/subagent-driven-development/SKILL.md) is the tighter loop: dispatch a fresh implementer subagent per task, then run spec compliance review, then code-quality review, and re-review until both pass.

Verification is not an afterthought. [`references/superpowers/skills/verification-before-completion/SKILL.md`](../../../references/superpowers/skills/verification-before-completion/SKILL.md) requires fresh evidence before any completion claim, and [`references/superpowers/skills/test-driven-development/SKILL.md`](../../../references/superpowers/skills/test-driven-development/SKILL.md) enforces red-green-refactor at the code level. [`references/superpowers/skills/requesting-code-review/SKILL.md`](../../../references/superpowers/skills/requesting-code-review/SKILL.md) adds a review gate after each task in subagent-driven mode, while [`references/superpowers/skills/receiving-code-review/SKILL.md`](../../../references/superpowers/skills/receiving-code-review/SKILL.md) insists on technical verification before accepting feedback.

Net effect: the repo treats execution as a closed loop of task, test, review, rework, and only then progression. That is the closest analogue to a Ralph-style harness in the tree.

## 4. Skill and subagent model

The skills layer is the main abstraction. [`references/superpowers/README.md`](../../../references/superpowers/README.md) says the agent checks for relevant skills before any task and treats them as mandatory workflows. [`references/superpowers/skills/using-superpowers/SKILL.md`](../../../references/superpowers/skills/using-superpowers/SKILL.md) is the bootstrap guardrail: it requires skill invocation before any response, defines skill priority, and maps how different harnesses access skills.

The subagent model is explicit in [`references/superpowers/skills/subagent-driven-development/SKILL.md`](../../../references/superpowers/skills/subagent-driven-development/SKILL.md). It defines a fresh subagent per task, isolated context, and a strict reviewer ladder. [`references/superpowers/skills/dispatching-parallel-agents/SKILL.md`](../../../references/superpowers/skills/dispatching-parallel-agents/SKILL.md) extends that into parallel independent domains. The repo also ships role-specific prompt templates under [`references/superpowers/skills/subagent-driven-development/`](../../../references/superpowers/skills/subagent-driven-development/) and [`references/superpowers/skills/brainstorming/spec-document-reviewer-prompt.md`](../../../references/superpowers/skills/brainstorming/spec-document-reviewer-prompt.md).

This is not a generic agent pool. It is a role-based system: brainstormer, planner, implementer, spec reviewer, code reviewer, finisher.

## 5. Hooks, plugin, and runtime integration

The repo supports multiple harnesses rather than one runtime. For Claude-family shells, [`references/superpowers/CLAUDE.md`](../../../references/superpowers/CLAUDE.md) is the top-level policy document. For Gemini, [`references/superpowers/GEMINI.md`](../../../references/superpowers/GEMINI.md) points directly at `using-superpowers` plus Gemini tool mapping. The package metadata in [`references/superpowers/package.json`](../../../references/superpowers/package.json) points OpenCode at `.opencode/plugins/superpowers.js`.

The OpenCode plugin in [`references/superpowers/.opencode/plugins/superpowers.js`](../../../references/superpowers/.opencode/plugins/superpowers.js) has two key runtime hooks: a `config` hook that adds the skills directory to discovery, and an `experimental.chat.messages.transform` hook that injects bootstrap text into the first user message. The OpenCode install doc in [`references/superpowers/.opencode/INSTALL.md`](../../../references/superpowers/.opencode/INSTALL.md) and the public guide in [`references/superpowers/docs/README.opencode.md`](../../../references/superpowers/docs/README.opencode.md) both describe that plugin flow.

There is also a generic hook path for Claude-like environments in [`references/superpowers/hooks/hooks.json`](../../../references/superpowers/hooks/hooks.json) and [`references/superpowers/hooks/session-start`](../../../references/superpowers/hooks/session-start). That hook injects the `using-superpowers` skill content on session start and even warns about legacy skill locations, which makes bootstrap stateful rather than passive.

## 6. System-prompt and bootstrap surfaces

Bootstrap happens in more than one place. The OpenCode plugin injects an “EXTREMELY_IMPORTANT” block into the first user message, embedding the `using-superpowers` content plus tool-mapping guidance. The Claude hook injects similar context at session start through `additionalContext` / `hookSpecificOutput`. Meanwhile, [`references/superpowers/README.md`](../../../references/superpowers/README.md), [`references/superpowers/docs/README.codex.md`](../../../references/superpowers/docs/README.codex.md), and [`references/superpowers/docs/README.opencode.md`](../../../references/superpowers/docs/README.opencode.md) all describe platform-specific installation paths so the bootstrap can actually land.

The important design choice is that bootstrapping is treated as a runtime concern, not just documentation. The agent is expected to start sessions already primed to use the skill system, with harness-specific tool substitutions where needed.

## 7. Strengths and gaps for a reusable agent harness

Strengths:
- Clear phase separation: design, plan, execute, verify, finish.
- Strong anti-drift gates: no implementation before design approval, no completion claims without fresh verification.
- Subagent isolation is first-class, not improvised.
- Harness adaptation is explicit across Claude, OpenCode, Gemini, and Codex.
- The system is mostly dependency-light and skill-driven, which makes it portable.

Gaps:
- No explicit `Ralph` abstraction or canonical entrypoint; the pattern is distributed across skills and docs.
- The same workflow is described in several places, so the source of truth is fragmented.
- OpenCode gets the richest runtime integration; Codex and other platforms rely more on manual install and skill discovery conventions.
- The OpenCode guide and plugin are already slightly out of sync on the hook name (`experimental.chat.system.transform` in docs vs `experimental.chat.messages.transform` in code), which is a maintenance risk for harness adapters.
- The repo is strong on process but weaker on a single orchestration API that another harness could call directly.

Bottom line: this repo is best understood as a Ralph-like workflow substrate, not a Ralph implementation. Its real value is the combination of bootstrap hooks, skill-gated planning, task-level execution loops, and mandatory verification.
