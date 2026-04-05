#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PLAN_SLUG="${1:-ralph-implementation-v0}"
PLAN_PATH="$ROOT/.everything-automate/plans/$(date +%F)-${PLAN_SLUG}.md"
PROMPT_PATH="$ROOT/.everything-automate/testing/codex-planning-test-prompt.md"
LAST_MESSAGE_PATH="$ROOT/.everything-automate/testing/codex-planning-last-message.md"

mkdir -p "$(dirname "$PLAN_PATH")" "$(dirname "$PROMPT_PATH")"

python3 "$ROOT/scripts/install_codex_local_test.py" >/dev/null

cat >"$PROMPT_PATH" <<EOF
Use the project-local skills installed under ./.codex/skills and the project-local agents installed under ./.codex/agents.

For this test, treat ./templates/codex/AGENTS.md as the runtime guidance reference.

Invoke \$planning for this repository and create an execution-ready plan artifact at:
$PLAN_PATH

The plan is for implementing the Ralph loop in this repository.

Do not implement code. Planning only.

The plan must include:
- requirements summary
- desired outcome
- in-scope
- non-goals
- decision boundaries
- acceptance criteria
- verification steps
- implementation order
- risks and mitigations
- execution handoff block

The execution handoff block must include:
- task_id
- plan_path
- recommended_mode
- recommended_agents
- verification_lane
- open_risks
EOF

codex exec \
  --cd "$ROOT" \
  --dangerously-bypass-approvals-and-sandbox \
  -o "$LAST_MESSAGE_PATH" \
  - <"$PROMPT_PATH"

printf 'Planning test completed.\n'
printf 'Plan path: %s\n' "$PLAN_PATH"
printf 'Last message: %s\n' "$LAST_MESSAGE_PATH"
