# Repository Guidelines

## Project Structure & Module Organization

- `templates/`: source of truth for distributable runtime assets. Codex lives under `templates/codex/`.
- `scripts/`: setup and install helpers such as `install_global.py` and local test installers.
- `runtime/`: shared runtime helpers and state tools, including `ea_state.py` and `ea_codex.py`.
- `docs/`: research notes, specs, milestones, and design decisions. Start with `docs/README.md`.
- `references/`: external reference projects used for research only. Do not treat them as editable source.
- `.everything-automate/`: local working artifacts such as generated plans and state.

## Build, Test, and Development Commands

- `python3 scripts/install_global.py setup --provider codex`
  Install the current Codex template into `~/.codex`.
- `python3 scripts/install_global.py doctor --provider codex`
  Check whether managed global assets are installed and readable.
- `python3 scripts/install_codex_local_test.py`
  Materialize repo-local Codex skills and agents for local testing.
- `python3 -m py_compile scripts/install_global.py scripts/install_common.py runtime/ea_state.py runtime/ea_codex.py`
  Fast syntax check for the current Python entry points.
- `git status --short`
  Confirm intended file scope before commit.

## Coding Style & Naming Conventions

- Use ASCII by default.
- Prefer short, plain English. Write for non-native English speakers.
- Python: follow standard style, 4-space indentation, clear function names, no clever abstractions.
- Markdown: keep sections short, use stable headings, and update related indexes when adding docs.
- Template assets should live under `templates/`; repo-local helpers should not become the only shipped behavior.

## Testing Guidelines

- There is no formal test suite yet; use targeted verification.
- For Python changes, run `py_compile`.
- For installer changes, run both `setup` and `doctor` against a temp root before touching `~/.codex`.
- For docs and skills, re-read the rendered flow and check linked indexes such as `docs/README.md`.

## Commit & Pull Request Guidelines

- Follow the repo’s existing commit style: `feat: ...`, `docs: ...`, `chore: ...`.
- Keep commits scoped to one change area when possible.
- PRs should explain:
  - what changed
  - why it changed
  - how it was verified
- Include file paths or commands where useful, for example `templates/codex/skills/planning/SKILL.md` or `python3 scripts/install_global.py doctor --provider codex`.
