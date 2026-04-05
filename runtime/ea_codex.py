#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shlex
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


DEFAULT_RUNTIME_ROOT = ".everything-automate/codex"
DEFAULT_STATE_ROOT = ".everything-automate/state"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def fail(message: str, *, code: int = 1) -> None:
    print(message, file=sys.stderr)
    raise SystemExit(code)


def dump_json(data: Any) -> None:
    print(json.dumps(data, indent=2, sort_keys=True))


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def default_guidance_file() -> Path:
    return repo_root() / "templates" / "codex" / "AGENTS.md"


def parse_workspace_root(raw: str) -> Path:
    return Path(raw).expanduser().resolve()


def relativize(path: Path, base: Path) -> str:
    try:
        return str(path.relative_to(base))
    except ValueError:
        return str(path)


def runtime_root(workspace_root: Path) -> Path:
    return workspace_root / DEFAULT_RUNTIME_ROOT


def state_root(workspace_root: Path) -> Path:
    return workspace_root / DEFAULT_STATE_ROOT


def task_root(workspace_root: Path, task_id: str) -> Path:
    return runtime_root(workspace_root) / "tasks" / task_id


def handoff_file(workspace_root: Path, task_id: str) -> Path:
    return task_root(workspace_root, task_id) / "handoff.json"


def current_run_file(workspace_root: Path, task_id: str) -> Path:
    return task_root(workspace_root, task_id) / "current-run.json"


def run_root(workspace_root: Path, task_id: str, run_id: str) -> Path:
    return task_root(workspace_root, task_id) / "runs" / run_id


def state_file_for_task(workspace_root: Path, task_id: str) -> Path:
    return state_root(workspace_root) / "tasks" / task_id / "loop-state.json"


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        fail(f"json file not found: {path}")
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as exc:
        fail(f"json file is not valid JSON: {path} ({exc})")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    ensure_parent(path)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def call_state_tool(arguments: list[str]) -> dict[str, Any]:
    state_tool = repo_root() / "runtime" / "ea_state.py"
    result = subprocess.run(
        [sys.executable, str(state_tool), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        message = result.stderr.strip() or result.stdout.strip() or "ea_state.py failed"
        fail(message, code=result.returncode)
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"ea_state.py returned invalid JSON ({exc})")


def ensure_plan_exists(plan_path: Path) -> Path:
    resolved = plan_path.expanduser().resolve()
    if not resolved.exists():
        fail(f"plan path not found: {resolved}")
    return resolved


def assert_startable(workspace_root: Path, task_id: str, *, force: bool) -> None:
    state_file = state_file_for_task(workspace_root, task_id)
    if not state_file.exists():
        return
    if not force:
        fail(
            "state file already exists for this task. "
            "Use status/resume/cancel or pass --force to start a new run."
        )


def build_handoff_payload(
    *,
    workspace_root: Path,
    task_id: str,
    plan_path: Path,
    mode: str,
    execution_mode: str,
) -> dict[str, Any]:
    now = utc_now()
    return {
        "created_at": now,
        "desired_mode": mode,
        "execution_intent": "durable_completion_loop" if mode == "ralph" else "standard_execution",
        "execution_mode": execution_mode,
        "plan_path": relativize(plan_path, workspace_root),
        "provider": "codex",
        "task_id": task_id,
        "updated_at": now,
        "workspace_root": str(workspace_root),
    }


def render_instructions(
    *,
    workspace_root: Path,
    task_id: str,
    run_id: str,
    plan_path: Path,
    mode: str,
    action: str,
    guidance_file: Path,
    resume_from_stage: str | None = None,
) -> str:
    guidance_text = guidance_file.read_text().strip()
    lines = [
        "# Everything Automate Codex Runtime Instructions",
        "",
        "## Run Metadata",
        f"- task_id: {task_id}",
        f"- run_id: {run_id}",
        f"- provider: codex",
        f"- mode: {mode}",
        f"- action: {action}",
        f"- workspace_root: {workspace_root}",
        f"- plan_path: {plan_path}",
    ]
    if resume_from_stage:
        lines.append(f"- resume_from_stage: {resume_from_stage}")

    lines.extend(
        [
            "",
            "## Top-Level Guidance",
            "",
            guidance_text,
            "",
            "## Execution Contract",
            "",
            "Follow the approved plan before widening scope.",
            "Read the referenced plan file before making changes.",
            "Use the kernel discipline: plan -> execute -> verify -> decide.",
            "Do not claim completion without fresh verification evidence.",
            "If verification fails, fix and loop.",
        ]
    )

    if mode == "ralph":
        lines.extend(
            [
                "Treat this as a durable completion loop.",
                "Do not stop after a first implementation pass if verification is still incomplete.",
                "Keep iterating until the task is verified complete or an explicit stop condition is reached.",
            ]
        )
    else:
        lines.append("Treat this as a task-bound execution session for the approved plan.")

    if action == "resume":
        lines.extend(
            [
                "",
                "## Resume Guidance",
                "",
                "This run is resuming an interrupted task.",
                "Resume conservatively from the suggested stage rather than assuming prior work is complete.",
            ]
        )

    return "\n".join(lines) + "\n"


def build_codex_exec_command(
    *,
    workspace_root: Path,
    prompt_file: Path,
    model: str | None,
    profile: str | None,
    sandbox: str | None,
) -> list[str]:
    command = ["codex", "exec", "-C", str(workspace_root), "--skip-git-repo-check"]
    if model:
        command.extend(["-m", model])
    if profile:
        command.extend(["-p", profile])
    if sandbox:
        command.extend(["-s", sandbox])
    command.extend(["-", "<", str(prompt_file)])
    return command


def build_launch_script(
    *,
    workspace_root: Path,
    state_file: Path,
    prompt_file: Path,
    start_stage: str,
    action: str,
    model: str | None,
    profile: str | None,
    sandbox: str | None,
) -> str:
    state_tool = repo_root() / "runtime" / "ea_state.py"
    shell_parts = ["codex", "exec", "-C", str(workspace_root), "--skip-git-repo-check"]
    if model:
        shell_parts.extend(["-m", model])
    if profile:
        shell_parts.extend(["-p", profile])
    if sandbox:
        shell_parts.extend(["-s", sandbox])
    codex_command = " ".join(shlex.quote(part) for part in shell_parts)
    summary = f"codex {action} launched via everything-automate"
    state_command = " ".join(
        shlex.quote(part)
        for part in [
            sys.executable,
            str(state_tool),
            "set-stage",
            str(state_file),
            "--stage",
            start_stage,
            "--summary",
            summary,
        ]
    )
    return "\n".join(
        [
            "#!/usr/bin/env bash",
            "set -euo pipefail",
            "",
            state_command,
            f"{codex_command} - < {shlex.quote(str(prompt_file))}",
            "",
        ]
    )


def maybe_launch(
    *,
    workspace_root: Path,
    state_file: Path,
    prompt_file: Path,
    action: str,
    stage: str,
    model: str | None,
    profile: str | None,
    sandbox: str | None,
) -> int:
    summary = f"codex {action} launched via everything-automate"
    call_state_tool(["set-stage", str(state_file), "--stage", stage, "--summary", summary])
    command = ["codex", "exec", "-C", str(workspace_root), "--skip-git-repo-check"]
    if model:
        command.extend(["-m", model])
    if profile:
        command.extend(["-p", profile])
    if sandbox:
        command.extend(["-s", sandbox])
    command.append("-")
    prompt_text = prompt_file.read_text()
    result = subprocess.run(command, input=prompt_text, text=True, check=False)
    return result.returncode


def prepare_run(
    *,
    workspace_root: Path,
    task_id: str,
    plan_path: Path,
    mode: str,
    execution_mode: str,
    force: bool,
    launch: bool,
    model: str | None,
    profile: str | None,
    sandbox: str | None,
) -> None:
    guidance_file = default_guidance_file()
    if not guidance_file.exists():
        fail(f"guidance file not found: {guidance_file}")

    plan_path = ensure_plan_exists(plan_path)
    assert_startable(workspace_root, task_id, force=force)

    handoff = build_handoff_payload(
        workspace_root=workspace_root,
        task_id=task_id,
        plan_path=plan_path,
        mode=mode,
        execution_mode=execution_mode,
    )
    handoff_path = handoff_file(workspace_root, task_id)
    write_json(handoff_path, handoff)

    init_args = [
        "init",
        "--state-root",
        str(state_root(workspace_root)),
        "--provider",
        "codex",
        "--task-id",
        task_id,
        "--plan-path",
        str(plan_path),
        "--stage",
        "committed",
        "--execution-mode",
        execution_mode,
        "--summary",
        f"prepared for codex {mode}",
    ]
    if force:
        init_args.append("--force")
    init_result = call_state_tool(init_args)

    run_id = init_result["run_id"]
    state_file = Path(init_result["state_file"])
    action = "start" if mode == "start" else "ralph"
    run_dir = run_root(workspace_root, task_id, run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    instructions_file = run_dir / f"{action}-instructions.md"
    launch_script = run_dir / f"{action}-launch.sh"

    instructions_file.write_text(
        render_instructions(
            workspace_root=workspace_root,
            task_id=task_id,
            run_id=run_id,
            plan_path=plan_path,
            mode=mode,
            action=action,
            guidance_file=guidance_file,
        )
    )
    launch_script.write_text(
        build_launch_script(
            workspace_root=workspace_root,
            state_file=state_file,
            prompt_file=instructions_file,
            start_stage="executing",
            action=action,
            model=model,
            profile=profile,
            sandbox=sandbox,
        )
    )
    launch_script.chmod(0o755)

    write_json(
        current_run_file(workspace_root, task_id),
        {
            "last_action": action,
            "launch_script": str(launch_script),
            "prepared_at": utc_now(),
            "prompt_file": str(instructions_file),
            "run_id": run_id,
            "state_file": str(state_file),
            "task_id": task_id,
        },
    )

    dump_json(
        {
            "action": action,
            "handoff_file": str(handoff_path),
            "launch_command": " ".join(
                build_codex_exec_command(
                    workspace_root=workspace_root,
                    prompt_file=instructions_file,
                    model=model,
                    profile=profile,
                    sandbox=sandbox,
                )
            ),
            "launch_script": str(launch_script),
            "mode": mode,
            "ok": True,
            "prompt_file": str(instructions_file),
            "run_id": run_id,
            "state_file": str(state_file),
            "task_id": task_id,
        }
    )

    if launch:
        raise SystemExit(
            maybe_launch(
                workspace_root=workspace_root,
                state_file=state_file,
                prompt_file=instructions_file,
                action=action,
                stage="executing",
                model=model,
                profile=profile,
                sandbox=sandbox,
            )
        )


def show_status(*, workspace_root: Path, task_id: str) -> None:
    task_dir = task_root(workspace_root, task_id)
    state_file = state_file_for_task(workspace_root, task_id)
    payload: dict[str, Any] = {
        "current_run_file": str(current_run_file(workspace_root, task_id)),
        "handoff_file": str(handoff_file(workspace_root, task_id)),
        "ok": True,
        "state_file": str(state_file),
        "task_dir": str(task_dir),
        "task_id": task_id,
    }
    if handoff_file(workspace_root, task_id).exists():
        payload["handoff"] = read_json(handoff_file(workspace_root, task_id))
    if current_run_file(workspace_root, task_id).exists():
        payload["current_run"] = read_json(current_run_file(workspace_root, task_id))
    if state_file.exists():
        payload["state"] = read_json(state_file)
        payload["resume_check"] = call_state_tool(["resume-check", str(state_file)])
    dump_json(payload)


def cancel_run(*, workspace_root: Path, task_id: str, summary: str | None) -> None:
    state_file = state_file_for_task(workspace_root, task_id)
    if not state_file.exists():
        fail(f"state file not found for task: {task_id}")
    args = [
        "cancel",
        str(state_file),
        "--cancelled-by",
        "user",
        "--preserve-artifact",
        "plan",
        "--preserve-artifact",
        "evidence",
    ]
    if summary:
        args.extend(["--summary", summary])
    dump_json(call_state_tool(args))


def resume_run(
    *,
    workspace_root: Path,
    task_id: str,
    launch: bool,
    model: str | None,
    profile: str | None,
    sandbox: str | None,
) -> None:
    guidance_file = default_guidance_file()
    if not guidance_file.exists():
        fail(f"guidance file not found: {guidance_file}")

    state_file = state_file_for_task(workspace_root, task_id)
    if not state_file.exists():
        fail(f"state file not found for task: {task_id}")

    resume_info = call_state_tool(["resume-check", str(state_file)])
    if not resume_info.get("resumable"):
        fail(f"task is not resumable: {resume_info.get('reason')}")

    state = read_json(state_file)
    run_id = state["run_id"]
    plan_path = Path(state["plan_path"]).expanduser()
    if not plan_path.is_absolute():
        plan_path = (workspace_root / plan_path).resolve()
    mode = "start"
    handoff_path = handoff_file(workspace_root, task_id)
    if handoff_path.exists():
        mode = read_json(handoff_path).get("desired_mode", "start")

    run_dir = run_root(workspace_root, task_id, run_id)
    run_dir.mkdir(parents=True, exist_ok=True)
    instructions_file = run_dir / "resume-instructions.md"
    launch_script = run_dir / "resume-launch.sh"

    instructions_file.write_text(
        render_instructions(
            workspace_root=workspace_root,
            task_id=task_id,
            run_id=run_id,
            plan_path=plan_path,
            mode=mode,
            action="resume",
            guidance_file=guidance_file,
            resume_from_stage=resume_info["resume_from_stage"],
        )
    )
    launch_script.write_text(
        build_launch_script(
            workspace_root=workspace_root,
            state_file=state_file,
            prompt_file=instructions_file,
            start_stage=resume_info["resume_from_stage"],
            action="resume",
            model=model,
            profile=profile,
            sandbox=sandbox,
        )
    )
    launch_script.chmod(0o755)

    write_json(
        current_run_file(workspace_root, task_id),
        {
            "last_action": "resume",
            "launch_script": str(launch_script),
            "prepared_at": utc_now(),
            "prompt_file": str(instructions_file),
            "run_id": run_id,
            "state_file": str(state_file),
            "task_id": task_id,
        },
    )

    dump_json(
        {
            "action": "resume",
            "launch_command": " ".join(
                build_codex_exec_command(
                    workspace_root=workspace_root,
                    prompt_file=instructions_file,
                    model=model,
                    profile=profile,
                    sandbox=sandbox,
                )
            ),
            "launch_script": str(launch_script),
            "ok": True,
            "prompt_file": str(instructions_file),
            "resume_from_stage": resume_info["resume_from_stage"],
            "run_id": run_id,
            "state_file": str(state_file),
            "task_id": task_id,
        }
    )

    if launch:
        raise SystemExit(
            maybe_launch(
                workspace_root=workspace_root,
                state_file=state_file,
                prompt_file=instructions_file,
                action="resume",
                stage=resume_info["resume_from_stage"],
                model=model,
                profile=profile,
                sandbox=sandbox,
            )
        )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare and operate the Codex execution path for everything-automate.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_runtime_flags(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("--workspace-root", default=".")
        subparser.add_argument("--model")
        subparser.add_argument("--profile")
        subparser.add_argument("--sandbox")
        subparser.add_argument("--launch", action="store_true")

    start_parser = subparsers.add_parser("start", help="prepare a standard Codex execution run")
    start_parser.add_argument("--task-id", required=True)
    start_parser.add_argument("--plan-path", required=True)
    start_parser.add_argument("--force", action="store_true")
    add_common_runtime_flags(start_parser)

    ralph_parser = subparsers.add_parser("ralph", help="prepare a durable Ralph-style Codex execution run")
    ralph_parser.add_argument("--task-id", required=True)
    ralph_parser.add_argument("--plan-path", required=True)
    ralph_parser.add_argument("--force", action="store_true")
    add_common_runtime_flags(ralph_parser)

    status_parser = subparsers.add_parser("status", help="show Codex runtime status for a task")
    status_parser.add_argument("--workspace-root", default=".")
    status_parser.add_argument("--task-id", required=True)

    cancel_parser = subparsers.add_parser("cancel", help="cancel the active run for a task")
    cancel_parser.add_argument("--workspace-root", default=".")
    cancel_parser.add_argument("--task-id", required=True)
    cancel_parser.add_argument("--summary")

    resume_parser = subparsers.add_parser("resume", help="prepare a resumable Codex run")
    resume_parser.add_argument("--workspace-root", default=".")
    resume_parser.add_argument("--task-id", required=True)
    resume_parser.add_argument("--model")
    resume_parser.add_argument("--profile")
    resume_parser.add_argument("--sandbox")
    resume_parser.add_argument("--launch", action="store_true")

    return parser


def main() -> None:
    args = build_parser().parse_args()
    workspace_root = parse_workspace_root(getattr(args, "workspace_root", "."))

    if args.command == "start":
        prepare_run(
            workspace_root=workspace_root,
            task_id=args.task_id,
            plan_path=Path(args.plan_path),
            mode="start",
            execution_mode="single_owner",
            force=args.force,
            launch=args.launch,
            model=args.model,
            profile=args.profile,
            sandbox=args.sandbox,
        )
        return

    if args.command == "ralph":
        prepare_run(
            workspace_root=workspace_root,
            task_id=args.task_id,
            plan_path=Path(args.plan_path),
            mode="ralph",
            execution_mode="single_owner",
            force=args.force,
            launch=args.launch,
            model=args.model,
            profile=args.profile,
            sandbox=args.sandbox,
        )
        return

    if args.command == "status":
        show_status(workspace_root=workspace_root, task_id=args.task_id)
        return

    if args.command == "cancel":
        cancel_run(workspace_root=workspace_root, task_id=args.task_id, summary=args.summary)
        return

    if args.command == "resume":
        resume_run(
            workspace_root=workspace_root,
            task_id=args.task_id,
            launch=args.launch,
            model=args.model,
            profile=args.profile,
            sandbox=args.sandbox,
        )
        return

    fail(f"unsupported command: {args.command}")


if __name__ == "__main__":
    main()
