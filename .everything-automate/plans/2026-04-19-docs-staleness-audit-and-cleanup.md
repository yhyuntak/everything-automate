---
title: Docs Staleness Audit And Cleanup
status: approved
approval_state: approved
task_id: docs-staleness-audit-and-cleanup-2026-04-19
plan_path: .everything-automate/plans/2026-04-19-docs-staleness-audit-and-cleanup.md
mode: direct
execution_unit: AC
recommended_mode: execute
verification_lane: docs-only
open_risks:
  - Some older specs are useful historical context, so deleting or rewriting too much may erase why the current shape exists.
  - Provider templates for Claude, OpenCode, and internal runtime are not active, so they need clear status labels without pretending they are finished.
  - The docs may drift again unless the source-of-truth order is made explicit and checked during future doc updates.
---

# Docs Staleness Audit And Cleanup

## Task Summary

Audit the whole Everything Automate repo for stale project and documentation surfaces, then clean them up so a future session can quickly tell what is current, what is historical, and what is paused.

## Desired Outcome

After the cleanup, the repo should make this clear:

- the current implementation path is Codex-first
- the active user flow is `$brainstorming -> $planning -> $execute -> $qa -> commit`
- backlog intake uses `$issue-capture` and `$issue-pick`
- stable workflow contract lives in `templates/codex/AGENTS.md` and `templates/codex/skills/*/SKILL.md`
- root docs and indexes point to the current source of truth
- old Ralph loop research is removed from current docs, with only a tombstone index left
- Claude, OpenCode, and internal templates are reduced to inactive markers
- old plans and decision notes stay as history unless they conflict with current accepted decisions

## In Scope

- audit all tracked Markdown docs outside `references/`
- audit current template surfaces under `templates/`
- audit runtime and installer docs for stale command or asset lists
- classify docs into current, support/reference, historical, paused/scaffold, or cleanup-needed
- update root README and docs indexes as needed
- delete stale bodies or reduce them to short tombstones
- update stale provider-template wording that still depends on an old Claude-first baseline
- update stale milestone wording where it contradicts the current Codex-first state
- add a lightweight stale-doc check checklist for future changes

## Non-Goals

- rewrite old research notes into current specs
- implement new runtime behavior
- redesign the workflow skills
- finish Claude, OpenCode, or internal runtime adapters
- change global installer behavior unless the audit finds a direct docs/code mismatch
- commit or push

## Relevant Accepted Decisions

This cleanup should respect:

- `DEC-004`: stable workflow contract lives in Codex AGENTS and skills
- `DEC-005`: QA routes specialist reviewers
- `DEC-006`: GitHub backlog intake uses capture and pick skills
- `DEC-007`: execute uses worker escalation and advisor subagents

No new decision note is required before execution.

Create a new decision note only if the cleanup settles a long-lived documentation policy that is broader than this one task.

## Current Findings

The first audit pass found these stale or risky areas.

### Current But Recently Drifted

- `README.md`
  had lagged behind the installed skill list and did not mention `$qa`, `$issue-capture`, or `$issue-pick`.
- `docs/README.md`
  read like only a research index, even though it is now the main docs index.
- `AGENTS.md`
  missed `runtime/ea_progress.py` in the runtime overview and syntax-check command.
- `docs/specs/everything-automate-implementation-milestones.md`
  still described the project as if M1 was next, even though M1-M4 now have usable drafts.

These have already been partly refreshed in the current working tree.
Execution should review and finish that refresh.

### Likely Cleanup Needed

- `docs/specs/everything-automate-planning-workflow.md`
  still talks about "Ralph-ready handoff", a 4-agent planning model, and old agent names such as angel/architect/devil. The current planning skill uses a simpler Codex-first shape with `explorer`, `plan-arch`, and `plan-devil`.
- `docs/specs/everything-automate-runtime-flow.md`
  still presents an older provider-neutral M1/M2 runtime sequence with `commit` as a stage before execute. It needs either a historical banner or a current alignment pass.
- `docs/specs/everything-automate-codex-execution-model.md`
  still describes M4/M5 in older terms and should be checked against the current `$execute -> $qa` model.
- `docs/specs/everything-automate-codex-execute-hardening.md`
  is useful, but it is a working note. It should say clearly whether it is active, partially completed, or superseded by newer plans.
- `templates/opencode/*`, `templates/internal/*`
  still say work will happen after the Claude Code baseline is stable. That is stale because the active implementation order is now Codex-first.
- `templates/claude-code/INSTALL.md`
  says it will become an install guide and has skeletal status. That may be fine, but it should be labeled as paused/scaffold rather than current setup guidance.

### Remove Or Tombstone

- `docs/research/ralph-loop/*`
  old research reports should be deleted from current docs, leaving only a tombstone index.
- `.everything-automate/plans/*`
  are execution history. Do not rewrite old plans unless an index needs better status wording.
- `.everything-automate/decisions/*`
  are accepted decision notes. Update or supersede only when a decision is actually changing.

## Design Direction

Use a simple document hierarchy:

```text
[Current Source Of Truth]
   |
   +--> templates/codex/AGENTS.md
   +--> templates/codex/skills/*/SKILL.md
   +--> scripts/install_global.py
   |
   v
[Current Explanation]
   |
   +--> README.md
   +--> docs/README.md
   +--> templates/codex/INSTALL.md
   +--> templates/codex/skills/README.md
   +--> templates/codex/agents/README.md
   |
   v
[Support Contracts]
   |
   +--> runtime/README.md
   +--> selected docs/specs/*
   +--> .everything-automate/decisions/*
   |
   v
[History / Paused Work]
       +--> docs/research/* tombstones
       +--> old specs reduced to tombstones
       +--> inactive Claude/OpenCode/internal markers
       +--> old plans
```

Use this status vocabulary in docs:

- `current`
  describes the active Codex-first setup or workflow.
- `support`
  explains runtime, installer, or lower-level contracts that support the current flow.
- `inactive`
  marks provider surfaces with no current implementation.
- `removed`
  means the old content was deleted. A short tombstone may remain to prevent broken links.
- `superseded`
  marks a doc whose main guidance has been replaced by a newer source.

Prefer deleting stale bodies.
Leave a short tombstone only when the path is still useful.

## Test Strategy

Use `docs-only`.

Verification should include:

- run `git diff --check`
- run `rg` checks for known stale phrases
- run `python3 scripts/install_global.py doctor --provider codex --codex-home <tmp-dir>` after setup in a temp home when install docs or install asset lists change
- re-read `README.md`, `docs/README.md`, and `templates/codex/INSTALL.md` as a new user would
- check that `docs/README.md` points readers to current docs before historical docs
- check that inactive provider templates do not imply they are current
- check that old research content is deleted or reduced to tombstones

## Task

### AC1. Build A Full Staleness Inventory

The cleanup should start with a repo-wide inventory, not hand-picked fixes.

#### TC1

List every tracked Markdown file outside `references/` and classify it as:

- current
- support
- historical
- paused
- scaffold
- superseded
- needs-update

#### TC2

Record the inventory in a new or existing docs index file so future sessions can reuse it.

#### TC3

For each `needs-update` file, name the current source of truth it should align with.

### AC2. Lock The Current Source-Of-Truth Order

The docs should stop making future sessions guess which file wins when two docs disagree.

#### TC1

`README.md` and `docs/README.md` clearly say that current Codex workflow contract lives in:

- `templates/codex/AGENTS.md`
- `templates/codex/skills/*/SKILL.md`

#### TC2

`templates/README.md` explains that provider templates translate current contracts into provider-specific surfaces, and that inactive provider templates may be scaffolded or paused.

#### TC3

No current index presents old Ralph research as the active operating model.

### AC3. Update Current Codex-Facing Docs

The docs that a user sees first should match the current installed assets and workflow.

#### TC1

`README.md` includes the current workflow, support skills, installed assets, and verification commands.

#### TC2

`templates/codex/INSTALL.md` matches what `scripts/install_global.py setup --provider codex` actually installs.

#### TC3

`templates/codex/agents/README.md` matches the current agent files and explains the status of `qa-reviewer.md`.

#### TC4

`runtime/README.md` mentions the current helper files and does not present runtime helpers as the primary user workflow.

### AC4. Remove Stale Historical And Provider Docs

Older docs should not keep stale bodies in current docs.

#### TC1

Ralph research report bodies are deleted, with only a tombstone index left.

#### TC2

Older provider-neutral specs that are no longer active source-of-truth are reduced to short tombstones.

#### TC3

Claude, OpenCode, and internal template docs are reduced to short inactive markers.

#### TC4

Inactive provider docs use consistent `inactive` wording.

### AC5. Clean Or Clarify Stale Milestone And Working Notes

Milestone docs should show what is done, what is active, and what is only historical.

#### TC1

`docs/specs/everything-automate-implementation-milestones.md` reflects the current M1-M6 status.

#### TC2

`docs/specs/everything-automate-codex-execute-hardening.md` clearly says whether it is active, partially completed, or historical.

#### TC3

`docs/specs/everything-automate-planning-workflow.md` no longer conflicts silently with the current planning skill and agent roster.

#### TC4

If a spec body is stale, it is removed or reduced to a tombstone.

### AC6. Add A Future Drift Check

The repo should make it easier to avoid this problem next time.

#### TC1

Add a short docs maintenance checklist to a current doc such as `docs/README.md`, `AGENTS.md`, or a new `docs/docs-maintenance.md`.

#### TC2

The checklist includes checking:

- root README
- docs index
- Codex install docs
- skill roster
- agent roster
- installer output
- accepted decisions

#### TC3

The checklist includes simple `rg` patterns for stale words such as:

- `Claude Code baseline`
- `will become`
- `Ralph-ready`
- old agent names when used as current planning agents

### AC7. Verify The Cleanup

The final cleanup should be checked like a docs change, not guessed.

#### TC1

`git diff --check` passes.

#### TC2

Stale-phrase searches are reviewed and either fixed or intentionally left in historical docs.

#### TC3

Temp Codex setup and doctor pass if install docs or installer-facing lists changed:

```bash
python3 scripts/install_global.py setup --provider codex --codex-home /tmp/everything-automate-docs-cleanup-codex-home
python3 scripts/install_global.py doctor --provider codex --codex-home /tmp/everything-automate-docs-cleanup-codex-home
```

#### TC4

The final report names any intentionally stale historical docs that remain.

## Execution Order

1. Finish the inventory and classify every Markdown surface.
2. Lock source-of-truth order in top-level docs.
3. Update current Codex-facing docs.
4. Remove stale historical bodies and reduce inactive provider docs.
5. Clean milestone and active working-note status.
6. Add a future drift checklist.
7. Run verification and report intentionally retained historical wording.

## Open Risks

- Some deleted research may need to be recovered from git history if future work wants it.
- If provider-template docs are made too terse, later Claude/OpenCode work may need to restart from current Codex contracts.
- A broad cleanup can become noisy. Keep each edit tied to a clear stale-doc finding.
- If current source-of-truth order is not explicit, the same drift will come back.

## Execute Handoff

- `task_id`: `docs-staleness-audit-and-cleanup-2026-04-19`
- `plan_path`: `.everything-automate/plans/2026-04-19-docs-staleness-audit-and-cleanup.md`
- `approval_state`: `approved`
- `execution_unit`: `AC`
- `test_strategy`: `docs-only`
- `open_risks`:
  - remove stale history while preserving path tombstones where useful
  - avoid pretending inactive provider templates are complete
  - keep cleanup scoped to docs/project surfaces unless a direct mismatch requires a small installer-facing change
