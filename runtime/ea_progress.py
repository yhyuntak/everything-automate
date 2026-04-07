#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_STATE_ROOT = ".everything-automate/state"
SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fail(message: str, *, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def dump_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def parse_state_root(raw: str) -> Path:
    return Path(raw).expanduser().resolve()


@dataclass
class ProgressLocation:
    root: Path
    task_dir: Path
    progress_file: Path
    terminal_summary_file: Path
    state_file: Path


def progress_location(state_root: Path, task_id: str) -> ProgressLocation:
    task_dir = state_root / "tasks" / task_id
    return ProgressLocation(
        root=state_root,
        task_dir=task_dir,
        progress_file=task_dir / "execute-progress.json",
        terminal_summary_file=task_dir / "terminal-summary.json",
        state_file=task_dir / "loop-state.json",
    )


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"json file not found: {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"json file is not valid JSON: {path} ({exc})")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def ensure_progress_exists(location: ProgressLocation) -> dict[str, Any]:
    return read_json(location.progress_file)


def init_progress(args: argparse.Namespace) -> None:
    state_root = parse_state_root(args.state_root)
    location = progress_location(state_root, args.task_id)
    if location.progress_file.exists() and not args.force:
        fail(f"progress file already exists: {location.progress_file}")

    now = utc_now()
    payload = {
        "schema_version": SCHEMA_VERSION,
        "task_id": args.task_id,
        "run_id": args.run_id,
        "plan_path": args.plan_path,
        "status": args.status,
        "current_ac": None,
        "completed_acs": [],
        "blocked_acs": [],
        "failed_verification_acs": [],
        "acs": [],
        "latest_evidence": None,
        "best_resume_point": "select first AC",
        "updated_at": now,
        "writer": "ea_progress.py",
    }
    write_json(location.progress_file, payload)
    dump_json(
        {
            "ok": True,
            "progress_file": str(location.progress_file),
            "task_id": args.task_id,
            "run_id": args.run_id,
        }
    )


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


def validate_snapshot(payload: dict[str, Any], *, task_id: str) -> dict[str, Any]:
    payload = dict(payload)
    if payload.get("task_id") and payload["task_id"] != task_id:
        fail("snapshot task_id does not match target task")
    payload["task_id"] = task_id
    payload.setdefault("schema_version", SCHEMA_VERSION)
    payload["updated_at"] = utc_now()
    payload.setdefault("writer", "ea_progress.py")
    return payload


def write_snapshot_cmd(args: argparse.Namespace) -> None:
    state_root = parse_state_root(args.state_root)
    location = progress_location(state_root, args.task_id)
    ensure_progress_exists(location)
    payload = validate_snapshot(read_stdin_json(), task_id=args.task_id)
    write_json(location.progress_file, payload)
    dump_json({"ok": True, "progress_file": str(location.progress_file), "task_id": args.task_id})


def build_terminal_summary(
    *,
    progress: dict[str, Any],
    state: dict[str, Any],
    outcome: str,
    summary: str | None,
) -> dict[str, Any]:
    current_ac = progress.get("current_ac")
    completed_acs = progress.get("completed_acs", [])
    latest_evidence = progress.get("latest_evidence")
    payload: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "task_id": progress.get("task_id") or state.get("task_id"),
        "run_id": progress.get("run_id") or state.get("run_id"),
        "outcome": outcome,
        "completed_acs": completed_acs,
        "current_ac": current_ac,
        "latest_evidence": latest_evidence,
        "terminal_reason": state.get("terminal_reason"),
        "updated_at": utc_now(),
        "writer": "ea_progress.py",
    }
    if summary:
        payload["summary"] = summary

    if outcome == "complete":
        payload["remaining_open_risks"] = []
        payload.setdefault("summary", "Run completed with required ACs and fresh evidence.")
    elif outcome == "cancelled":
        payload["remaining_work"] = [
            ac.get("ac_id")
            for ac in progress.get("acs", [])
            if ac.get("status") not in {"passed"}
        ]
        payload.setdefault("summary", "Run cancelled before completion.")
    elif outcome == "failed":
        payload["failed_ac"] = current_ac
        payload["failure_reason"] = state.get("terminal_reason") or "failed"
        payload.setdefault("summary", "Run failed before valid completion.")
    elif outcome in {"suspended", "interrupted"}:
        payload["best_resume_point"] = progress.get("best_resume_point")
        payload.setdefault("summary", "Run stopped before terminal completion.")
    else:
        fail(f"unsupported terminal outcome: {outcome}")

    return payload


def write_terminal_summary_cmd(args: argparse.Namespace) -> None:
    state_root = parse_state_root(args.state_root)
    location = progress_location(state_root, args.task_id)
    progress = ensure_progress_exists(location)
    state = read_json(location.state_file)
    payload = build_terminal_summary(
        progress=progress,
        state=state,
        outcome=args.outcome,
        summary=args.summary,
    )
    write_json(location.terminal_summary_file, payload)
    dump_json(
        {
            "ok": True,
            "task_id": args.task_id,
            "terminal_summary_file": str(location.terminal_summary_file),
            "outcome": args.outcome,
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage everything-automate execution progress artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create an execute-progress file")
    init_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    init_parser.add_argument("--task-id", required=True)
    init_parser.add_argument("--run-id", required=True)
    init_parser.add_argument("--plan-path", required=True)
    init_parser.add_argument("--status", default="pending")
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=init_progress)

    snapshot_parser = subparsers.add_parser("write-snapshot", help="replace execute-progress.json with a full snapshot from stdin")
    snapshot_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    snapshot_parser.add_argument("--task-id", required=True)
    snapshot_parser.set_defaults(func=write_snapshot_cmd)

    terminal_parser = subparsers.add_parser("write-terminal-summary", help="derive and write terminal-summary.json")
    terminal_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    terminal_parser.add_argument("--task-id", required=True)
    terminal_parser.add_argument("--outcome", required=True, choices=["complete", "cancelled", "failed", "suspended", "interrupted"])
    terminal_parser.add_argument("--summary")
    terminal_parser.set_defaults(func=write_terminal_summary_cmd)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
