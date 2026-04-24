---
title: Codex-Only Bootstrap And In-Session Setup v1
task_id: codex-only-bootstrap-setup-v1-2026-04-24
status: approved
approval_state: approved
plan_path: .everything-automate/plans/2026-04-24-codex-only-bootstrap-setup-v1.md
mode: direct
execution_mode: single_owner
execution_unit: AC
recommended_mode: execute
recommended_agents:
  - ea-worker
verification_policy: docs-and-temp-home-install-checks
verification_lane: mixed
open_risks:
  - If v1 mixes new setup flow with large file moves, the change can become too broad and hard to verify.
  - README now describes bootstrap, `ea-setup`, and `ea-doctor`, but those surfaces do not exist yet.
  - Keeping old `setup --provider codex` paths beside new bootstrap paths can confuse users during the transition.
  - Some docs and runtime notes still describe provider-neutral or multi-provider design and may drift if not narrowed deliberately.
test_command: python3 scripts/install_global.py bootstrap --codex-home <tmp-dir> && python3 scripts/install_global.py setup --codex-home <tmp-dir> && python3 scripts/install_global.py doctor --codex-home <tmp-dir>
---

# Requirements Summary

- Make the repository and setup story clearly Codex-only.
- Use the new README install flow as the user-facing contract:
  - clone the repo
  - run bootstrap
  - open Codex
  - run `$ea-setup`
  - let `$ea-setup` run `$ea-doctor`
- Keep v1 smaller by avoiding a large source-tree relayout in the same change.

# Desired Outcome

After this work:

- A first-time user can follow the README install flow and reach a ready EA Codex setup.
- A bootstrap command installs only the minimum global setup surface.
- `$ea-setup` exists as a support skill and drives the real install or repair flow.
- `$ea-doctor` exists as a support skill and reports whether EA is ready.
- User-facing docs consistently describe EA as Codex-only.
- Existing low-level install logic is still reusable under the new setup model.

# In Scope

- Define and implement a bootstrap install command for Codex-only EA setup.
- Add `ea-setup` as a support skill.
- Add `ea-doctor` as a support skill.
- Reframe the installer so bootstrap, full setup, and doctor each have a clear role.
- Update user-facing and directly adjacent install docs to match the new flow.
- Narrow the install language from provider-focused wording to Codex-only wording where needed for this flow.

# Non-Goals

- Do not do a full `templates/codex/` to `templates/` source relayout in v1.
- Do not remove every historical provider-neutral or multi-provider note in one pass.
- Do not redesign runtime state tools beyond what the new setup flow needs.
- Do not expand setup to clone the EA repo automatically.
- Do not build a broad package-manager-like system.

# Design Direction

Keep the first change in two layers.

Layer 1: user-facing contract

- README is the main install guide
- bootstrap is the first outside-Codex step
- `ea-setup` is the real in-session setup surface
- `ea-doctor` is the read-only health check surface

Layer 2: low-level support

- `scripts/install_global.py` stays as the deterministic installer tool
- it should expose separate commands for:
  - bootstrap
  - full setup
  - doctor

Keep the v1 repo shape stable enough to avoid large path churn.
The project should present as Codex-only in docs and setup UX first.
Further flattening can follow after the new setup model is working.

# Test Strategy

Strategy: `mixed`

Use docs and temp-home verification:

- Re-read README and install docs for one clear first-user flow.
- Run bootstrap into a temp Codex home and confirm it installs only the minimum setup surface.
- Confirm bootstrap makes `$ea-setup` and `$ea-doctor` available in the installed skills area.
- Run full setup into a temp Codex home and confirm the expected EA global assets are installed.
- Run doctor into the same temp Codex home and confirm it reports a ready state.
- Re-run setup and doctor where useful to confirm the new flow does not break the current config guarantees.

# Task

## AC1: Docs Lock One Codex-Only Install Story

README and directly adjacent install docs describe one setup model instead of competing script-first and provider-first stories.

### TC1.1

Read `README.md`.

Expected evidence:

- It describes EA as a Codex-only project.
- It explains the first-user flow as `bootstrap -> $ea-setup -> $ea-doctor`.
- It makes clear that bootstrap is only the minimum setup surface.

### TC1.2

Read `templates/codex/INSTALL.md`.

Expected evidence:

- It aligns with the README install flow.
- It explains how bootstrap, full setup, and doctor differ.
- It avoids unnecessary provider wording for the user-facing flow.

## AC2: Bootstrap Installs Only The Minimum Setup Surface

A bootstrap command exists and installs only the minimum global assets needed to continue setup inside Codex.

### TC2.1

Run bootstrap into an empty temp Codex home.

Expected evidence:

- The install succeeds.
- The installed skill set includes `ea-setup`.
- The installed skill set includes `ea-doctor`.
- The install does not materialize the full EA runtime surface yet.

### TC2.2

Inspect the bootstrap install manifest or file set.

Expected evidence:

- Only the minimum setup assets are treated as bootstrap-managed.
- Full workflow skills, agents, and hooks are not all installed by bootstrap.

## AC3: `$ea-setup` Orchestrates Full Install Or Repair

`$ea-setup` exists as a support skill and tells the agent to inspect the environment, run the deterministic full setup path when safe, then run `$ea-doctor`.

### TC3.1

Read the installed source skill for `ea-setup`.

Expected evidence:

- It describes install, update, and repair as setup responsibilities.
- It tells the agent to inspect the current EA source and Codex home state before changing anything.
- It ends by calling or instructing the use of `$ea-doctor`.

### TC3.2

Run the full setup path into a temp Codex home after bootstrap.

Expected evidence:

- The full EA runtime assets are installed.
- Required EA config guarantees are still applied.
- The flow is compatible with the existing install manifest and backup behavior.

## AC4: `$ea-doctor` Reports Ready State Clearly

`$ea-doctor` exists as a support skill and the low-level doctor command can support its checks.

### TC4.1

Read the installed source skill for `ea-doctor`.

Expected evidence:

- It is read-only.
- It checks the expected global assets and required config state.
- It reports what is missing or broken instead of installing anything.

### TC4.2

Run doctor against a temp Codex home after successful full setup.

Expected evidence:

- Doctor reports a ready state.
- Doctor still fails clearly when required assets or config guarantees are missing.

## AC5: Existing Installer Entry Points Are Reframed Under The New Setup Model

The low-level installer supports the new setup flow without pretending to be the main user-facing story.

### TC5.1

Inspect `scripts/install_global.py` help surface and related docs.

Expected evidence:

- Bootstrap, full setup, and doctor have clearly different roles.
- The new setup flow does not require the user-facing docs to lead with `setup --provider codex`.

### TC5.2

Search directly touched docs and scripts for the old provider-first user story.

Expected evidence:

- New or updated user-facing install text leads with the Codex-only flow.
- Any remaining provider wording is limited to internal or historical surfaces that are out of scope for this v1 change.

## Execute Handoff

Use `$ea-execute` after approval.

Start with AC1 so docs and command roles match before implementation spreads.

Recommended execution order:

1. AC1 docs alignment
2. AC2 bootstrap command
3. AC3 `ea-setup`
4. AC4 `ea-doctor`
5. AC5 installer help and remaining wording alignment

Keep the first version smaller:

- no large source-tree move
- no multi-provider cleanup campaign
- no broader runtime redesign
