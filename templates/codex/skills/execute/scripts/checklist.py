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


def task_dir(state_root: Path, task_id: str) -> Path:
    return state_root / "tasks" / task_id


def worker_report_file(state_root: Path, task_id: str) -> Path:
    return task_dir(state_root, task_id) / "worker-report.json"


def advisor_handoff_file(state_root: Path, task_id: str) -> Path:
    return task_dir(state_root, task_id) / "advisor-handoff.json"


def retry_packet_file(state_root: Path, task_id: str) -> Path:
    return task_dir(state_root, task_id) / "retry-packet.json"


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"json file not found: {path}")
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        fail(f"json file is not valid JSON: {path} ({exc})")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_stdin_json(*, required: bool) -> dict[str, Any]:
    raw = sys.stdin.read().strip()
    if not raw:
        if required:
            fail("stdin JSON payload required")
        return {}
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        fail(f"stdin payload is not valid JSON ({exc})")
    if not isinstance(payload, dict):
        fail("stdin JSON payload must be an object")
    return payload


def write_progress(path: Path, payload: dict[str, Any]) -> None:
    payload["updated_at"] = utc_now()
    payload.setdefault("schema_version", SCHEMA_VERSION)
    payload.setdefault("writer", "execute/scripts/checklist.py")
    write_json(path, payload)


def require_progress(state_root: Path, task_id: str) -> dict[str, Any]:
    return read_json(progress_file(state_root, task_id))


def find_ac(progress: dict[str, Any], ac_id: str) -> dict[str, Any]:
    for ac in progress.get("acs", []):
        if ac.get("ac_id") == ac_id:
            return ac
    fail(f"ac not found in progress: {ac_id}")


def find_tc(ac: dict[str, Any], tc_id: str) -> dict[str, Any]:
    for tc in ac.get("tcs", []):
        if tc.get("tc_id") == tc_id:
            return tc
    fail(f"tc not found in AC {ac.get('ac_id')}: {tc_id}")


def ac_ref(ac: dict[str, Any]) -> dict[str, Any]:
    return {"ac_id": ac["ac_id"], "title": ac["title"]}


def tc_ref(tc: dict[str, Any]) -> dict[str, Any]:
    return {"tc_id": tc["tc_id"], "title": tc["title"], "type": tc.get("type", "automated")}


def checklist_from_payload(payload: dict[str, Any]) -> list[dict[str, Any]]:
    acs = payload.get("acs", [])
    if not isinstance(acs, list):
        fail("payload field 'acs' must be a list")
    normalized: list[dict[str, Any]] = []
    for ac in acs:
        if not isinstance(ac, dict):
            fail("each AC must be an object")
        ac_id = ac.get("ac_id")
        title = ac.get("title")
        if not ac_id or not title:
            fail("each AC must include ac_id and title")
        tcs_raw = ac.get("tcs", [])
        if not isinstance(tcs_raw, list):
            fail(f"AC {ac_id} field 'tcs' must be a list")
        tcs: list[dict[str, Any]] = []
        for tc in tcs_raw:
            if not isinstance(tc, dict):
                fail(f"AC {ac_id} includes a non-object TC")
            tc_id = tc.get("tc_id")
            tc_title = tc.get("title")
            if not tc_id or not tc_title:
                fail(f"each TC in AC {ac_id} must include tc_id and title")
            tcs.append(
                {
                    "tc_id": tc_id,
                    "title": tc_title,
                    "type": tc.get("type", "automated"),
                    "status": tc.get("status", "pending"),
                    "latest_check": tc.get("latest_check"),
                }
            )
        normalized.append(
            {
                "ac_id": ac_id,
                "title": title,
                "status": ac.get("status", "pending"),
                "retry_count": ac.get("retry_count", 0),
                "latest_evidence": ac.get("latest_evidence"),
                "tcs": tcs,
            }
        )
    return normalized


def require_string(payload: dict[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        fail(f"payload field '{key}' must be a non-empty string")
    return value.strip()


def require_string_list(payload: dict[str, Any], key: str) -> list[str]:
    value = payload.get(key)
    if not isinstance(value, list) or not value:
        fail(f"payload field '{key}' must be a non-empty list")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            fail(f"payload field '{key}' must contain only non-empty strings")
        normalized.append(item.strip())
    return normalized


def optional_string_list(payload: dict[str, Any], key: str) -> list[str] | None:
    value = payload.get(key)
    if value is None:
        return None
    if not isinstance(value, list):
        fail(f"payload field '{key}' must be a list when present")
    normalized: list[str] = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            fail(f"payload field '{key}' must contain only non-empty strings")
        normalized.append(item.strip())
    return normalized


def require_live_context(
    *,
    progress: dict[str, Any],
    ac_id: str | None,
    tc_id: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    current_ac_raw = progress.get("current_ac")
    if not isinstance(current_ac_raw, dict):
        fail("live current_ac not found in progress")

    current_ac_id = current_ac_raw.get("ac_id")
    if not isinstance(current_ac_id, str) or not current_ac_id.strip():
        fail("live current_ac is missing ac_id")

    ac = find_ac(progress, current_ac_id)
    if ac_id and ac_id != current_ac_id:
        fail(f"ac_id does not match live current_ac: {ac_id}")

    current_tc_raw = progress.get("current_tc")
    if current_tc_raw is None:
        if tc_id:
            fail("live current_tc not found in progress")
        return ac_ref(ac), None

    if not isinstance(current_tc_raw, dict):
        fail("live current_tc is not a valid object")

    current_tc_id = current_tc_raw.get("tc_id")
    if not isinstance(current_tc_id, str) or not current_tc_id.strip():
        fail("live current_tc is missing tc_id")

    tc = find_tc(ac, current_tc_id)
    if tc_id and tc_id != current_tc_id:
        fail(f"tc_id does not match live current_tc: {tc_id}")

    return ac_ref(ac), tc_ref(tc)


def write_packet(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload["updated_at"] = utc_now()
    payload.setdefault("schema_version", SCHEMA_VERSION)
    payload.setdefault("writer", "execute/scripts/checklist.py")
    write_json(path, payload)


def execute_start_cmd(args: argparse.Namespace) -> None:
    path = progress_file(parse_state_root(args.state_root), args.task_id)
    if path.exists() and not args.force:
        fail(f"progress file already exists: {path}")
    payload = read_stdin_json(required=False)
    progress = {
        "schema_version": SCHEMA_VERSION,
        "task_id": args.task_id,
        "run_id": args.run_id,
        "plan_path": args.plan_path,
        "status": "in_progress",
        "current_ac": None,
        "current_tc": None,
        "completed_acs": [],
        "blocked_acs": [],
        "failed_verification_acs": [],
        "acs": checklist_from_payload(payload) if payload else [],
        "latest_evidence": None,
        "best_resume_point": "pick first AC",
        "updated_at": utc_now(),
        "writer": "execute/scripts/checklist.py",
    }
    write_json(path, progress)
    dump_json({"ok": True, "progress_file": str(path), "task_id": args.task_id})


def ac_start_cmd(args: argparse.Namespace) -> None:
    path = progress_file(parse_state_root(args.state_root), args.task_id)
    progress = read_json(path)
    ac = find_ac(progress, args.ac_id)
    ac["status"] = "in_progress"
    progress["status"] = "in_progress"
    progress["current_ac"] = {"ac_id": ac["ac_id"], "title": ac["title"]}
    progress["current_tc"] = None
    progress["best_resume_point"] = f"resume AC {ac['ac_id']}"
    write_progress(path, progress)
    dump_json({"ok": True, "task_id": args.task_id, "ac_id": args.ac_id})


def tc_start_cmd(args: argparse.Namespace) -> None:
    path = progress_file(parse_state_root(args.state_root), args.task_id)
    progress = read_json(path)
    ac = find_ac(progress, args.ac_id)
    tc = find_tc(ac, args.tc_id)
    ac["status"] = "in_progress"
    tc["status"] = "in_progress"
    tc["type"] = args.tc_type
    progress["current_ac"] = {"ac_id": ac["ac_id"], "title": ac["title"]}
    progress["current_tc"] = {"tc_id": tc["tc_id"], "title": tc["title"], "type": tc["type"]}
    progress["best_resume_point"] = f"resume TC {tc['tc_id']} in AC {ac['ac_id']}"
    write_progress(path, progress)
    dump_json({"ok": True, "task_id": args.task_id, "ac_id": args.ac_id, "tc_id": args.tc_id})


def tc_result_cmd(args: argparse.Namespace) -> None:
    path = progress_file(parse_state_root(args.state_root), args.task_id)
    progress = read_json(path)
    ac = find_ac(progress, args.ac_id)
    tc = find_tc(ac, args.tc_id)
    tc["status"] = args.result
    latest_check = {
        "tc_id": args.tc_id,
        "kind": args.tc_type or tc.get("type", "automated"),
        "result": args.result,
    }
    if args.summary:
        latest_check["summary"] = args.summary
    tc["latest_check"] = latest_check
    progress["latest_evidence"] = latest_check
    ac["latest_evidence"] = latest_check
    blocked = progress.setdefault("blocked_acs", [])
    failed = progress.setdefault("failed_verification_acs", [])
    if args.result == "blocked":
        if args.ac_id not in blocked:
            blocked.append(args.ac_id)
        if args.ac_id in failed:
            failed.remove(args.ac_id)
    elif args.result == "fail":
        if args.ac_id not in failed:
            failed.append(args.ac_id)
        if args.ac_id in blocked:
            blocked.remove(args.ac_id)
        ac["retry_count"] = int(ac.get("retry_count", 0)) + 1
    elif args.result == "pass":
        if args.ac_id in blocked:
            blocked.remove(args.ac_id)
        if args.ac_id in failed:
            failed.remove(args.ac_id)
    write_progress(path, progress)
    dump_json(
        {
            "ok": True,
            "task_id": args.task_id,
            "ac_id": args.ac_id,
            "tc_id": args.tc_id,
            "result": args.result,
        }
    )


def ac_complete_cmd(args: argparse.Namespace) -> None:
    path = progress_file(parse_state_root(args.state_root), args.task_id)
    progress = read_json(path)
    ac = find_ac(progress, args.ac_id)
    ac["status"] = "passed"
    completed = progress.setdefault("completed_acs", [])
    if args.ac_id not in completed:
        completed.append(args.ac_id)
    if progress.get("current_ac", {}).get("ac_id") == args.ac_id:
        progress["current_ac"] = None
        progress["current_tc"] = None
    progress["best_resume_point"] = "pick next AC"
    write_progress(path, progress)
    dump_json({"ok": True, "task_id": args.task_id, "ac_id": args.ac_id})


def worker_report_cmd(args: argparse.Namespace) -> None:
    state_root = parse_state_root(args.state_root)
    payload = read_stdin_json(required=True)
    progress = require_progress(state_root, args.task_id)
    current_ac, current_tc = require_live_context(
        progress=progress,
        ac_id=args.ac_id,
        tc_id=args.tc_id,
    )
    packet = {
        "kind": "worker_report",
        "task_id": args.task_id,
        "current_ac": current_ac,
        "current_tc": current_tc,
        "summary": require_string(payload, "summary"),
        "what_tried": require_string_list(payload, "what_tried"),
        "candidate_next_steps": require_string_list(payload, "candidate_next_steps"),
    }
    files_touched = optional_string_list(payload, "files_touched")
    if files_touched is not None:
        packet["files_touched"] = files_touched
    checks_run = optional_string_list(payload, "checks_run")
    if checks_run is not None:
        packet["checks_run"] = checks_run
    failure_or_blocker = payload.get("failure_or_blocker")
    if failure_or_blocker is not None:
        if not isinstance(failure_or_blocker, str) or not failure_or_blocker.strip():
            fail("payload field 'failure_or_blocker' must be a non-empty string when present")
        packet["failure_or_blocker"] = failure_or_blocker.strip()
    path = worker_report_file(state_root, args.task_id)
    write_packet(path, packet)
    dump_json({"ok": True, "task_id": args.task_id, "worker_report_file": str(path)})


def advisor_handoff_cmd(args: argparse.Namespace) -> None:
    state_root = parse_state_root(args.state_root)
    payload = read_stdin_json(required=True)
    progress = require_progress(state_root, args.task_id)
    current_ac, current_tc = require_live_context(
        progress=progress,
        ac_id=args.ac_id,
        tc_id=args.tc_id,
    )
    packet = {
        "kind": "advisor_handoff",
        "task_id": args.task_id,
        "current_ac": current_ac,
        "current_tc": current_tc,
        "open_question": require_string(payload, "open_question"),
        "recent_attempts": require_string_list(payload, "recent_attempts"),
        "candidate_options": require_string_list(payload, "candidate_options"),
    }
    relevant_files = optional_string_list(payload, "relevant_files")
    if relevant_files is not None:
        packet["relevant_files"] = relevant_files
    failing_check = payload.get("failing_check")
    if failing_check is not None:
        if not isinstance(failing_check, str) or not failing_check.strip():
            fail("payload field 'failing_check' must be a non-empty string when present")
        packet["failing_check"] = failing_check.strip()
    worker_report_ref = payload.get("worker_report_ref")
    if worker_report_ref is not None:
        if not isinstance(worker_report_ref, str) or not worker_report_ref.strip():
            fail("payload field 'worker_report_ref' must be a non-empty string when present")
        packet["worker_report_ref"] = worker_report_ref.strip()
    path = advisor_handoff_file(state_root, args.task_id)
    write_packet(path, packet)
    dump_json({"ok": True, "task_id": args.task_id, "advisor_handoff_file": str(path)})


def retry_packet_cmd(args: argparse.Namespace) -> None:
    state_root = parse_state_root(args.state_root)
    payload = read_stdin_json(required=True)
    progress = require_progress(state_root, args.task_id)
    current_ac, current_tc = require_live_context(
        progress=progress,
        ac_id=args.ac_id,
        tc_id=args.tc_id,
    )
    packet = {
        "kind": "retry_packet",
        "task_id": args.task_id,
        "current_ac": current_ac,
        "current_tc": current_tc,
        "controller_decision": require_string(payload, "controller_decision"),
        "recommended_path": require_string(payload, "recommended_path"),
        "next_steps": require_string_list(payload, "next_steps"),
    }
    advisor_summary = payload.get("advisor_summary")
    if advisor_summary is not None:
        if not isinstance(advisor_summary, str) or not advisor_summary.strip():
            fail("payload field 'advisor_summary' must be a non-empty string when present")
        packet["advisor_summary"] = advisor_summary.strip()
    risks_to_watch = optional_string_list(payload, "risks_to_watch")
    if risks_to_watch is not None:
        packet["risks_to_watch"] = risks_to_watch
    advisor_handoff_ref = payload.get("advisor_handoff_ref")
    if advisor_handoff_ref is not None:
        if not isinstance(advisor_handoff_ref, str) or not advisor_handoff_ref.strip():
            fail("payload field 'advisor_handoff_ref' must be a non-empty string when present")
        packet["advisor_handoff_ref"] = advisor_handoff_ref.strip()
    path = retry_packet_file(state_root, args.task_id)
    write_packet(path, packet)
    dump_json({"ok": True, "task_id": args.task_id, "retry_packet_file": str(path)})


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage the installed execute checklist artifact.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start_parser = subparsers.add_parser("execute-start", help="create a live checklist from stdin JSON")
    start_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    start_parser.add_argument("--task-id", required=True)
    start_parser.add_argument("--plan-path")
    start_parser.add_argument("--run-id")
    start_parser.add_argument("--force", action="store_true")
    start_parser.set_defaults(func=execute_start_cmd)

    ac_start_parser = subparsers.add_parser("ac-start", help="mark an AC as in progress")
    ac_start_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    ac_start_parser.add_argument("--task-id", required=True)
    ac_start_parser.add_argument("--ac-id", required=True)
    ac_start_parser.set_defaults(func=ac_start_cmd)

    tc_start_parser = subparsers.add_parser("tc-start", help="mark a TC as in progress")
    tc_start_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    tc_start_parser.add_argument("--task-id", required=True)
    tc_start_parser.add_argument("--ac-id", required=True)
    tc_start_parser.add_argument("--tc-id", required=True)
    tc_start_parser.add_argument("--tc-type", default="automated")
    tc_start_parser.set_defaults(func=tc_start_cmd)

    tc_result_parser = subparsers.add_parser("tc-result", help="record the result of a TC")
    tc_result_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    tc_result_parser.add_argument("--task-id", required=True)
    tc_result_parser.add_argument("--ac-id", required=True)
    tc_result_parser.add_argument("--tc-id", required=True)
    tc_result_parser.add_argument("--result", required=True, choices=["pass", "fail", "blocked"])
    tc_result_parser.add_argument("--tc-type")
    tc_result_parser.add_argument("--summary")
    tc_result_parser.set_defaults(func=tc_result_cmd)

    ac_complete_parser = subparsers.add_parser("ac-complete", help="mark an AC as complete")
    ac_complete_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    ac_complete_parser.add_argument("--task-id", required=True)
    ac_complete_parser.add_argument("--ac-id", required=True)
    ac_complete_parser.set_defaults(func=ac_complete_cmd)

    worker_report_parser = subparsers.add_parser("worker-report", help="write the latest durable worker report from stdin JSON")
    worker_report_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    worker_report_parser.add_argument("--task-id", required=True)
    worker_report_parser.add_argument("--ac-id")
    worker_report_parser.add_argument("--tc-id")
    worker_report_parser.set_defaults(func=worker_report_cmd)

    advisor_handoff_parser = subparsers.add_parser("advisor-handoff", help="write the latest advisor handoff from stdin JSON")
    advisor_handoff_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    advisor_handoff_parser.add_argument("--task-id", required=True)
    advisor_handoff_parser.add_argument("--ac-id")
    advisor_handoff_parser.add_argument("--tc-id")
    advisor_handoff_parser.set_defaults(func=advisor_handoff_cmd)

    retry_packet_parser = subparsers.add_parser("retry-packet", help="write the latest controller retry packet from stdin JSON")
    retry_packet_parser.add_argument("--state-root", default=DEFAULT_STATE_ROOT)
    retry_packet_parser.add_argument("--task-id", required=True)
    retry_packet_parser.add_argument("--ac-id")
    retry_packet_parser.add_argument("--tc-id")
    retry_packet_parser.set_defaults(func=retry_packet_cmd)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
