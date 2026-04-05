#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4


STAGES = {
    "bootstrap",
    "intake",
    "planning",
    "committed",
    "executing",
    "verifying",
    "fixing",
    "wrapping",
    "complete",
    "cancelled",
    "failed",
}

TERMINAL_STAGES = {"complete", "cancelled", "failed"}
DEFAULT_STATE_ROOT = ".everything-automate/state"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fail(message: str, *, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def dump_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def ensure_stage(stage: str) -> str:
    if stage not in STAGES:
        fail(f"unsupported stage: {stage}")
    return stage


def is_terminal(state: dict[str, Any]) -> bool:
    return state["stage"] in TERMINAL_STAGES or state.get("terminal_reason") is not None


def suggested_resume_stage(stage: str) -> str | None:
    mapping = {
        "bootstrap": "intake",
        "intake": "planning",
        "planning": "planning",
        "committed": "executing",
        "executing": "verifying",
        "verifying": "verifying",
        "fixing": "executing",
        "wrapping": "wrapping",
    }
    return mapping.get(stage)


@dataclass
class StateLocation:
    root: Path
    task_dir: Path
    state_file: Path
    events_dir: Path


def state_location(state_root: Path, task_id: str) -> StateLocation:
    task_dir = state_root / "tasks" / task_id
    return StateLocation(
        root=state_root,
        task_dir=task_dir,
        state_file=task_dir / "loop-state.json",
        events_dir=task_dir / "events",
    )


def read_state(state_file: Path) -> dict[str, Any]:
    if not state_file.exists():
        fail(f"state file not found: {state_file}")
    try:
        return json.loads(state_file.read_text())
    except json.JSONDecodeError as exc:
        fail(f"state file is not valid JSON: {state_file} ({exc})")


def write_state(location: StateLocation, state: dict[str, Any]) -> None:
    location.task_dir.mkdir(parents=True, exist_ok=True)
    location.events_dir.mkdir(parents=True, exist_ok=True)
    location.state_file.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def write_event(location: StateLocation, prefix: str, payload: dict[str, Any]) -> Path:
    location.events_dir.mkdir(parents=True, exist_ok=True)
    timestamp = payload["recorded_at"].replace(":", "-")
    event_path = location.events_dir / f"{prefix}-{timestamp}.json"
    event_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return event_path


def parse_state_root(raw: str) -> Path:
    return Path(raw).expanduser().resolve()


def init_state(args: argparse.Namespace) -> None:
    stage = ensure_stage(args.stage)
    if stage in TERMINAL_STAGES:
        fail("init stage cannot be terminal")

    state_root = parse_state_root(args.state_root)
    location = state_location(state_root, args.task_id)
    if location.state_file.exists() and not args.force:
        fail(f"state file already exists: {location.state_file}")

    now = utc_now()
    state = {
        "completed_at": None,
        "current_phase_summary": args.summary or "",
        "execution_mode": args.execution_mode,
        "iteration": args.iteration,
        "last_stable_stage": stage,
        "max_iterations": args.max_iterations,
        "owner_id": args.owner_id or "",
        "plan_path": args.plan_path,
        "provider": args.provider,
        "resume_count": 0,
        "resume_from_stage": None,
        "run_id": args.run_id or str(uuid4()),
        "stage": stage,
        "started_at": now,
        "suspended_at": None,
        "superseded_by": None,
        "task_id": args.task_id,
        "terminal_reason": None,
        "updated_at": now,
        "verification_policy": args.verification_policy,
    }
    write_state(location, state)
    dump_json({"ok": True, "state_file": str(location.state_file), "task_id": args.task_id, "run_id": state["run_id"]})


def set_stage(args: argparse.Namespace) -> None:
    new_stage = ensure_stage(args.stage)
    state_file = Path(args.state_file).expanduser().resolve()
    state = read_state(state_file)
    if is_terminal(state):
        fail("cannot set stage on a terminal run")

    now = utc_now()
    state["stage"] = new_stage
    state["updated_at"] = now
    state["resume_from_stage"] = None
    state["suspended_at"] = None
    if new_stage not in TERMINAL_STAGES:
        state["last_stable_stage"] = new_stage
    if args.summary:
        state["current_phase_summary"] = args.summary
    location = state_location(state_file.parents[2], state["task_id"])
    write_state(location, state)
    dump_json({"ok": True, "stage": new_stage, "state_file": str(state_file)})


def suspend_state(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).expanduser().resolve()
    state = read_state(state_file)
    if is_terminal(state):
        fail("cannot suspend a terminal run")

    now = utc_now()
    current_stage = state["stage"]
    resume_stage = ensure_stage(args.resume_from_stage) if args.resume_from_stage else suggested_resume_stage(current_stage)
    state["last_stable_stage"] = current_stage
    state["resume_from_stage"] = resume_stage
    state["suspended_at"] = now
    state["updated_at"] = now
    if args.summary:
        state["current_phase_summary"] = args.summary

    location = state_location(state_file.parents[2], state["task_id"])
    write_state(location, state)
    dump_json(
        {
            "ok": True,
            "resume_from_stage": resume_stage,
            "state_file": str(state_file),
            "suspended_at": now,
        }
    )


def resume_check(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).expanduser().resolve()
    try:
        state = read_state(state_file)
    except SystemExit:
        dump_json({"ok": False, "resumable": False, "reason": "state_unreadable"})
        raise

    if not state.get("task_id"):
        dump_json({"ok": False, "resumable": False, "reason": "missing_task_id"})
        return
    if not state.get("plan_path"):
        dump_json({"ok": False, "resumable": False, "reason": "missing_plan_path"})
        return
    if is_terminal(state):
        dump_json(
            {
                "ok": True,
                "resumable": False,
                "reason": "terminal_state",
                "stage": state["stage"],
                "terminal_reason": state.get("terminal_reason"),
            }
        )
        return
    if state.get("superseded_by"):
        dump_json({"ok": True, "resumable": False, "reason": "superseded", "superseded_by": state["superseded_by"]})
        return

    stage = state["stage"]
    suggested = state.get("resume_from_stage") or suggested_resume_stage(stage)
    dump_json(
        {
            "ok": True,
            "resumable": True,
            "reason": "eligible",
            "state_file": str(state_file),
            "task_id": state["task_id"],
            "run_id": state["run_id"],
            "last_stable_stage": state.get("last_stable_stage"),
            "resume_from_stage": suggested,
            "stage": stage,
        }
    )


def cancel_state(args: argparse.Namespace) -> None:
    state_file = Path(args.state_file).expanduser().resolve()
    state = read_state(state_file)
    if is_terminal(state):
        fail("cannot cancel a terminal run")

    now = utc_now()
    previous_stage = state["stage"]
    state["completed_at"] = now
    state["last_stable_stage"] = previous_stage
    state["resume_from_stage"] = None
    state["stage"] = "cancelled"
    state["suspended_at"] = None
    state["terminal_reason"] = "cancelled"
    state["updated_at"] = now

    location = state_location(state_file.parents[2], state["task_id"])
    write_state(location, state)

    cancel_record = {
        "cancelled_by": args.cancelled_by,
        "preserved_artifacts": args.preserve_artifact or [],
        "recorded_at": now,
        "run_id": state["run_id"],
        "summary": args.summary or "",
        "task_id": state["task_id"],
        "terminal_reason": "cancelled",
        "was_stage": previous_stage,
    }
    event_path = write_event(location, "cancel", cancel_record)
    dump_json(
        {
            "ok": True,
            "cancel_record": str(event_path),
            "stage": state["stage"],
            "state_file": str(state_file),
            "terminal_reason": state["terminal_reason"],
        }
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage everything-automate file-based loop state.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="create a new loop-state file")
    init_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    init_parser.add_argument("--provider", choices=["claude-code", "codex", "opencode", "internal"], required=True)
    init_parser.add_argument("--task-id", required=True)
    init_parser.add_argument("--plan-path", required=True)
    init_parser.add_argument("--stage", default="planning")
    init_parser.add_argument("--execution-mode", default="single_owner", choices=["single_owner", "team", "subagents"])
    init_parser.add_argument("--owner-id")
    init_parser.add_argument("--run-id")
    init_parser.add_argument("--summary")
    init_parser.add_argument("--verification-policy", default="fresh_evidence_required")
    init_parser.add_argument("--max-iterations", default=10, type=int)
    init_parser.add_argument("--iteration", default=0, type=int)
    init_parser.add_argument("--force", action="store_true")
    init_parser.set_defaults(func=init_state)

    set_stage_parser = subparsers.add_parser("set-stage", help="update the current non-terminal stage")
    set_stage_parser.add_argument("state_file")
    set_stage_parser.add_argument("--stage", required=True)
    set_stage_parser.add_argument("--summary")
    set_stage_parser.set_defaults(func=set_stage)

    suspend_parser = subparsers.add_parser("suspend", help="mark a run as suspended and resumable")
    suspend_parser.add_argument("state_file")
    suspend_parser.add_argument("--resume-from-stage")
    suspend_parser.add_argument("--summary")
    suspend_parser.set_defaults(func=suspend_state)

    resume_parser = subparsers.add_parser("resume-check", help="report whether a run is resumable")
    resume_parser.add_argument("state_file")
    resume_parser.set_defaults(func=resume_check)

    cancel_parser = subparsers.add_parser("cancel", help="mark a run as cancelled and write a cancel record")
    cancel_parser.add_argument("state_file")
    cancel_parser.add_argument("--cancelled-by", required=True)
    cancel_parser.add_argument("--summary")
    cancel_parser.add_argument("--preserve-artifact", action="append")
    cancel_parser.set_defaults(func=cancel_state)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
