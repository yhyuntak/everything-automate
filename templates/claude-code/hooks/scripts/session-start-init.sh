#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/ea-lib.sh"

ea_require_state_tool

if ! ea_have_init_context; then
  ea_noop "session start init skipped: missing EA_TASK_ID or EA_PLAN_PATH"
fi

TASK_ID="$(ea_task_id)"
STATE_FILE="$(ea_state_file "${TASK_ID}")"

if [[ -f "${STATE_FILE}" ]]; then
  ea_log "session start init skipped: state already exists for ${TASK_ID}"
  exit 0
fi

"${EA_STATE_TOOL}" init \
  --state-root "$(ea_state_root)" \
  --provider claude-code \
  --task-id "${TASK_ID}" \
  --plan-path "${EA_PLAN_PATH}" \
  --stage "${EA_INITIAL_STAGE:-planning}" \
  --execution-mode "${EA_EXECUTION_MODE:-single_owner}" \
  --owner-id "${EA_OWNER_ID:-claude-code}" \
  --summary "${EA_INITIAL_SUMMARY:-session initialized}"
