# Claude Code Hooks

This directory holds Claude Code-specific hook assets for bootstrap, suspension, and runtime recovery glue.

Current M4 surfaces:

- `hooks.json`
  sample Claude Code hook configuration
- `scripts/session-start-init.sh`
  initialize task-scoped loop state when `EA_TASK_ID` and `EA_PLAN_PATH` are available
- `scripts/stop-suspend.sh`
  suspend the current task conservatively on `Stop`
- `scripts/cancel-current.sh`
  explicit cancellation helper
- `scripts/resume-check.sh`
  inspect resumability for the current task

Hook code belongs here rather than in the repo root so distributable behavior stays inside the template layer.
