#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


SCHEMA_VERSION = 1
DEFAULT_STATE_ROOT = ".everything-automate/state"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fail(message: str, *, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def dump_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def parse_state_root(raw: str) -> Path:
    return Path(raw).expanduser().resolve()


def progress_file(state_root: Path, task_id: str) -> Path:
    return state_root / "tasks" / task_id / "execute-progress.json"


def state_file(state_root: Path, task_id: str) -> Path:
    return state_root / "tasks" / task_id / "loop-state.json"


def qa_handoff_file(state_root: Path, task_id: str) -> Path:
    return state_root / "tasks" / task_id / "qa-handoff.json"


def read_json(path: Path, *, required: bool) -> dict[str, Any]:
    if not path.exists():
        if required:
            fail(f"json file not found: {path}")
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"json file is not valid JSON: {path} ({exc})")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_stdin_json() -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        fail("stdin JSON payload required")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"stdin payload is not valid JSON ({exc})")
    if not isinstance(payload, dict):
        fail("stdin JSON payload must be an object")
    return payload


def require_string_field(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"stdin field '{key}' must be a non-empty string")
    return value.strip()


def optional_string_field(payload: dict[str, Any], key: str) -> str | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        fail(f"stdin field '{key}' must be a non-empty string when present")
    return value.strip()


def require_string_list_field(payload: dict[str, Any], key: str, *, allow_empty: bool = False) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list):
        fail(f"stdin field '{key}' must be a list")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            fail(f"stdin field '{key}' must contain only non-empty strings")
        normalized.append(item.strip())
    if not allow_empty and not normalized:
        fail(f"stdin field '{key}' must not be empty")
    return normalized


def build_handoff(*, task_id: str, progress: dict[str, Any], state: dict[str, Any], extra: dict[str, Any]) -> dict[str, Any]:
    task_summary = require_string_field(extra, "task_summary")
    desired_outcome = require_string_field(extra, "desired_outcome")
    scope = require_string_list_field(extra, "scope")
    non_goals = require_string_list_field(extra, "non_goals")
    plan_summary = require_string_field(extra, "plan_summary")
    changed_files = require_string_list_field(extra, "changed_files", allow_empty=True)
    diff_summary = optional_string_field(extra, "diff_summary")
    if not changed_files and not diff_summary:
        fail("stdin must include changed_files or diff_summary")
    test_results = require_string_list_field(extra, "test_results")
    behavior_goal = require_string_field(extra, "behavior_goal")
    llm_reads = require_string_list_field(extra, "llm_reads")
    llm_owned_decisions = require_string_list_field(extra, "llm_owned_decisions")
    script_owned_validation = require_string_list_field(extra, "script_owned_validation")
    contract_changes = require_string_list_field(extra, "contract_changes")
    open_risks = require_string_list_field(extra, "open_risks", allow_empty=True)

    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": task_id,
        "run_id": progress.get("run_id") or state.get("run_id"),
        "task_summary": task_summary,
        "desired_outcome": desired_outcome,
        "scope": scope,
        "non_goals": non_goals,
        "plan_summary": plan_summary,
        "changed_files": changed_files,
        "diff_summary": diff_summary,
        "test_results": test_results,
        "behavior_goal": behavior_goal,
        "llm_reads": llm_reads,
        "llm_owned_decisions": llm_owned_decisions,
        "script_owned_validation": script_owned_validation,
        "contract_changes": contract_changes,
        "open_risks": open_risks,
        "progress_summary": {
            "current_ac": progress.get("current_ac"),
            "current_tc": progress.get("current_tc"),
            "completed_acs": progress.get("completed_acs", []),
            "blocked_acs": progress.get("blocked_acs", []),
            "failed_verification_acs": progress.get("failed_verification_acs", []),
            "latest_evidence": progress.get("latest_evidence"),
        },
        "state_summary": {
            "stage": state.get("stage"),
            "terminal_reason": state.get("terminal_reason"),
        } if state else None,
        "updated_at": utc_now(),
        "writer": "qa/scripts/build_handoff.py",
    }


def build_handoff_cmd(args: argparse.Namespace) -> None:
    state_root = parse_state_root(args.state_root)
    progress = read_json(progress_file(state_root, args.task_id), required=True)
    state = read_json(state_file(state_root, args.task_id), required=False)
    extra = read_stdin_json()
    payload = build_handoff(task_id=args.task_id, progress=progress, state=state, extra=extra)
    target = qa_handoff_file(state_root, args.task_id)
    write_json(target, payload)
    dump_json({"ok": True, "qa_handoff_file": str(target), "task_id": args.task_id})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Build the installed QA review packet.")
    parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    parser.add_argument("--task-id", required=True)
    parser.set_defaults(func=build_handoff_cmd)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
