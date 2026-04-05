#!/usr/bin/env bash

set -euo pipefail

EA_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
EA_REPO_ROOT="$(cd "${EA_SCRIPT_DIR}/../../../.." && pwd)"
EA_STATE_TOOL="${EA_STATE_TOOL:-${EA_REPO_ROOT}/runtime/ea_state.py}"

ea_state_root() {
  if [[ -n "${EA_STATE_ROOT:-}" ]]; then
    printf '%s\n' "${EA_STATE_ROOT}"
  else
    printf '%s\n' "${PWD}/.everything-automate/state"
  fi
}

ea_task_id() {
  printf '%s\n' "${EA_TASK_ID:-}"
}

ea_state_file() {
  local task_id="$1"
  printf '%s/tasks/%s/loop-state.json\n' "$(ea_state_root)" "${task_id}"
}

ea_have_task_context() {
  [[ -n "${EA_TASK_ID:-}" ]]
}

ea_have_init_context() {
  [[ -n "${EA_TASK_ID:-}" && -n "${EA_PLAN_PATH:-}" ]]
}

ea_log() {
  printf '[ea-claude] %s\n' "$*" >&2
}

ea_noop() {
  ea_log "$*"
  exit 0
}

ea_require_state_tool() {
  [[ -x "${EA_STATE_TOOL}" ]] || ea_noop "state tool unavailable: ${EA_STATE_TOOL}"
}
