#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=/dev/null
source "${SCRIPT_DIR}/ea-lib.sh"

ea_require_state_tool

if ! ea_have_task_context; then
  ea_noop "cancel skipped: missing EA_TASK_ID"
fi

TASK_ID="$(ea_task_id)"
STATE_FILE="$(ea_state_file "${TASK_ID}")"

if [[ ! -f "${STATE_FILE}" ]]; then
  ea_noop "cancel skipped: no state file for ${TASK_ID}"
fi

"${EA_STATE_TOOL}" cancel "${STATE_FILE}" \
  --cancelled-by "${EA_CANCELLED_BY:-user}" \
  --summary "${EA_CANCEL_SUMMARY:-cancelled from Claude helper script}" \
  --preserve-artifact plan \
  --preserve-artifact evidence
