#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
import sys

from install_common import (
    ROOT,
    iter_agent_markdown,
    iter_skill_dirs,
    load_agent_definition,
    render_agent_toml,
)


BEGIN_MARKER = "<!-- BEGIN EVERYTHING AUTOMATE CODEX -->"
END_MARKER = "<!-- END EVERYTHING AUTOMATE CODEX -->"

LEGACY_MANAGED_AGENT_FILES = (
    "advisor.toml",
    "ea-blueprint-design-reviewer.toml",
    "code-reviewer.toml",
    "ea-qa-reviewer.toml",
    "ea-blueprint-read-test.toml",
    "explorer.toml",
    "harness-reviewer.toml",
    "ea-north-star-read-test.toml",
    "plan-arch.toml",
    "plan-devil.toml",
    "qa-reviewer.toml",
    "worker.toml",
)

LEGACY_MANAGED_SKILL_DIRS = (
    "brainstorming",
    "execute",
    "issue-capture",
    "issue-pick",
    "planning",
    "qa",
    "ea-blueprint",
)


@dataclass(frozen=True)
class ProjectSpec:
    project_root: Path
    template_root: Path
    codex_root: Path
    agents_root: Path
    skills_root: Path
    state_root: Path
    backup_root: Path
    manifest_path: Path


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_spec(project_root: Path) -> ProjectSpec:
    project_root = project_root.resolve()
    codex_root = project_root / ".codex"
    state_root = project_root / ".everything-automate"
    timestamp = now_utc()

    return ProjectSpec(
        project_root=project_root,
        template_root=ROOT / "templates",
        codex_root=codex_root,
        agents_root=codex_root / "agents",
        skills_root=codex_root / "skills",
        state_root=state_root,
        backup_root=state_root / "backups" / timestamp,
        manifest_path=state_root / "install-manifest.json",
    )


def backup_path(path: Path, spec: ProjectSpec) -> Path:
    return spec.backup_root / path.relative_to(spec.project_root)


def copy_with_backup(src: Path, dst: Path, spec: ProjectSpec) -> dict[str, str | None]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    previous_backup: Path | None = None

    if dst.exists():
        previous_backup = backup_path(dst, spec)
        previous_backup.parent.mkdir(parents=True, exist_ok=True)
        if dst.is_dir():
            shutil.copytree(dst, previous_backup, dirs_exist_ok=True)
            shutil.rmtree(dst)
        else:
            shutil.copy2(dst, previous_backup)
            dst.unlink()

    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

    return {
        "target": str(dst),
        "source": str(src),
        "backup_path": str(previous_backup) if previous_backup else None,
    }


def remove_with_backup(path: Path, spec: ProjectSpec) -> dict[str, str | None]:
    previous_backup = backup_path(path, spec)
    previous_backup.parent.mkdir(parents=True, exist_ok=True)

    if path.is_dir():
        shutil.copytree(path, previous_backup, dirs_exist_ok=True)
        shutil.rmtree(path)
    else:
        shutil.copy2(path, previous_backup)
        path.unlink()

    return {
        "target": str(path),
        "backup_path": str(previous_backup),
    }


def render_agent_with_backup(agent_md: Path, dst: Path, spec: ProjectSpec) -> dict[str, str | None]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    previous_backup: Path | None = None

    if dst.exists():
        previous_backup = backup_path(dst, spec)
        previous_backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, previous_backup)
        dst.unlink()

    agent = load_agent_definition(agent_md)
    toml = render_agent_toml(
        agent.name,
        agent.description,
        agent.prompt,
        model=agent.model,
        model_reasoning_effort=agent.model_reasoning_effort,
        sandbox_mode=agent.sandbox_mode,
    )
    dst.write_text(toml, encoding="utf-8")
    return {
        "target": str(dst),
        "source": str(agent_md),
        "backup_path": str(previous_backup) if previous_backup else None,
    }


def project_agents_block(template_agents: str) -> str:
    return "\n".join(
        [
            BEGIN_MARKER,
            "",
            template_agents.rstrip(),
            "",
            END_MARKER,
            "",
        ]
    )


def strip_unmarked_template(text: str, template_text: str) -> str:
    """Remove a previous unmarked template block while keeping project text."""
    stripped = text.lstrip()
    leading = text[: len(text) - len(stripped)]
    template = template_text.strip()

    if stripped.startswith(template):
        remainder = stripped[len(template):]
        return leading + remainder.lstrip()

    return text


def join_agents_sections(before: str, block: str, after: str) -> str:
    sections = []
    if before.strip():
        sections.append(before.strip())
    sections.append(block.strip())
    if after.strip():
        sections.append(after.strip())
    return "\n\n".join(sections) + "\n"


def merge_agents_md(spec: ProjectSpec) -> dict[str, str | None]:
    src = spec.template_root / "AGENTS.md"
    dst = spec.project_root / "AGENTS.md"
    template_text = src.read_text(encoding="utf-8")
    block = project_agents_block(template_text)

    previous_backup: Path | None = None
    existing = ""

    if dst.exists():
        previous_backup = backup_path(dst, spec)
        previous_backup.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, previous_backup)
        existing = dst.read_text(encoding="utf-8")

    if BEGIN_MARKER in existing and END_MARKER in existing:
        before, rest = existing.split(BEGIN_MARKER, 1)
        _, after = rest.split(END_MARKER, 1)
        after = strip_unmarked_template(after, template_text)
        merged = join_agents_sections(before, block, after)
    elif existing.strip():
        project_text = strip_unmarked_template(existing, template_text)
        merged = join_agents_sections("", block, project_text)
    else:
        merged = block.strip() + "\n"

    dst.write_text(merged, encoding="utf-8")
    return {
        "target": str(dst),
        "source": str(src),
        "backup_path": str(previous_backup) if previous_backup else None,
    }


def install_assets(spec: ProjectSpec) -> list[dict[str, str | None]]:
    installed: list[dict[str, str | None]] = []

    agents_result = merge_agents_md(spec)
    agents_result["kind"] = "merged-file"
    installed.append(agents_result)

    for agent_md in iter_agent_markdown(spec.template_root):
        agent = load_agent_definition(agent_md)
        result = render_agent_with_backup(agent_md, spec.agents_root / f"{agent.name}.toml", spec)
        result["kind"] = "agent"
        installed.append(result)

    for skill_dir in iter_skill_dirs(spec.template_root):
        result = copy_with_backup(skill_dir, spec.skills_root / skill_dir.name, spec)
        result["kind"] = "dir"
        installed.append(result)

    return installed


def remove_legacy_managed_assets(spec: ProjectSpec) -> list[dict[str, str | None]]:
    removed: list[dict[str, str | None]] = []

    for filename in LEGACY_MANAGED_AGENT_FILES:
        path = spec.agents_root / filename
        if not path.exists():
            continue
        result = remove_with_backup(path, spec)
        result["kind"] = "legacy-agent"
        removed.append(result)

    for dirname in LEGACY_MANAGED_SKILL_DIRS:
        path = spec.skills_root / dirname
        if not path.exists():
            continue
        result = remove_with_backup(path, spec)
        result["kind"] = "legacy-skill"
        removed.append(result)

    return removed


def managed_agent_names(spec: ProjectSpec) -> set[str]:
    return {
        f"{load_agent_definition(agent_md).name}.toml"
        for agent_md in iter_agent_markdown(spec.template_root)
    }


def managed_skill_names(spec: ProjectSpec) -> set[str]:
    return {skill_dir.name for skill_dir in iter_skill_dirs(spec.template_root)}


def preserved_local_assets(spec: ProjectSpec) -> dict[str, list[str]]:
    existing_agents = {
        path.name
        for path in spec.agents_root.glob("*.toml")
        if path.is_file()
    } if spec.agents_root.exists() else set()

    existing_skills = {
        path.name
        for path in spec.skills_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").exists()
    } if spec.skills_root.exists() else set()

    return {
        "agents": sorted(
            existing_agents - managed_agent_names(spec) - set(LEGACY_MANAGED_AGENT_FILES)
        ),
        "skills": sorted(
            existing_skills - managed_skill_names(spec) - set(LEGACY_MANAGED_SKILL_DIRS)
        ),
    }


def write_manifest(
    spec: ProjectSpec,
    *,
    status: str,
    installed_assets: list[dict[str, str | None]],
    removed_legacy_assets: list[dict[str, str | None]] | None = None,
    preserved_assets: dict[str, list[str]] | None = None,
    failed_asset: str | None = None,
    error: str | None = None,
) -> None:
    spec.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "tool": "everything-automate",
        "provider": "codex",
        "scope": "project",
        "status": status,
        "project_root": str(spec.project_root),
        "template_root": str(spec.template_root),
        "backup_root": str(spec.backup_root),
        "manifest_path": str(spec.manifest_path),
        "written_at": now_utc(),
        "installed_assets": installed_assets,
        "removed_legacy_assets": removed_legacy_assets or [],
        "preserved_local_assets": preserved_assets or {"agents": [], "skills": []},
        "failed_asset": failed_asset,
        "error": error,
    }
    spec.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def run_setup(spec: ProjectSpec) -> int:
    spec.codex_root.mkdir(parents=True, exist_ok=True)
    spec.state_root.mkdir(parents=True, exist_ok=True)

    installed_assets: list[dict[str, str | None]] = []
    removed_legacy_assets: list[dict[str, str | None]] = []
    failed_asset: str | None = None

    try:
        installed_assets = install_assets(spec)
        removed_legacy_assets = remove_legacy_managed_assets(spec)
        preserved_assets = preserved_local_assets(spec)
    except Exception as exc:  # pragma: no cover - failure path exercised by manual setup
        write_manifest(
            spec,
            status="failed",
            installed_assets=installed_assets,
            removed_legacy_assets=removed_legacy_assets,
            preserved_assets=preserved_local_assets(spec),
            failed_asset=failed_asset,
            error=str(exc),
        )
        print("everything-automate project setup failed.", file=sys.stderr)
        print(f"- project root: {spec.project_root}", file=sys.stderr)
        print(f"- error: {exc}", file=sys.stderr)
        print(f"- backup root: {spec.backup_root}", file=sys.stderr)
        print(f"- manifest: {spec.manifest_path}", file=sys.stderr)
        return 1

    write_manifest(
        spec,
        status="ok",
        installed_assets=installed_assets,
        removed_legacy_assets=removed_legacy_assets,
        preserved_assets=preserved_assets,
    )

    print("Installed everything-automate project Codex setup.")
    print(f"- project root: {spec.project_root}")
    print(f"- backup root: {spec.backup_root}")
    print(f"- manifest: {spec.manifest_path}")
    print("- installed assets:")
    for asset in installed_assets:
        print(f"  - {asset['target']}")
    if removed_legacy_assets:
        print("- removed legacy managed assets:")
        for asset in removed_legacy_assets:
            print(f"  - {asset['target']}")
    if preserved_assets["agents"] or preserved_assets["skills"]:
        print("- preserved local assets:")
        for agent in preserved_assets["agents"]:
            print(f"  - agent: {agent}")
        for skill in preserved_assets["skills"]:
            print(f"  - skill: {skill}")
    return 0


def run_doctor(spec: ProjectSpec) -> int:
    expected = [
        spec.project_root / "AGENTS.md",
        spec.agents_root,
        spec.skills_root,
    ]

    missing = [str(path) for path in expected if not path.exists()]
    has_markers = False
    agents_md = spec.project_root / "AGENTS.md"
    if agents_md.exists():
        text = agents_md.read_text(encoding="utf-8")
        has_markers = BEGIN_MARKER in text and END_MARKER in text
        if not has_markers:
            missing.append(f"{agents_md} markers")

    manifest_path = spec.manifest_path if spec.manifest_path.exists() else None
    latest_status = "unknown"
    if manifest_path:
        manifest = json.loads(spec.manifest_path.read_text(encoding="utf-8"))
        latest_status = manifest.get("status", "unknown")

    print("everything-automate project doctor")
    print(f"- project root: {spec.project_root}")
    print(f"- AGENTS.md managed block: {'yes' if has_markers else 'no'}")
    print(f"- agents dir: {spec.agents_root if spec.agents_root.exists() else '(missing)'}")
    print(f"- skills dir: {spec.skills_root if spec.skills_root.exists() else '(missing)'}")
    print(f"- latest manifest path: {manifest_path if manifest_path else '(none)'}")
    print(f"- latest manifest status: {latest_status}")

    legacy_assets = [
        *(spec.agents_root / filename for filename in LEGACY_MANAGED_AGENT_FILES),
        *(spec.skills_root / dirname for dirname in LEGACY_MANAGED_SKILL_DIRS),
    ]
    found_legacy = [str(path) for path in legacy_assets if path.exists()]

    if missing:
        print("- missing:")
        for item in missing:
            print(f"  - {item}")
        return 1

    if found_legacy:
        print("- legacy managed assets still present:")
        for item in found_legacy:
            print(f"  - {item}")
        return 1

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install the flat Codex Everything Automate runtime into a project root."
    )
    parser.add_argument(
        "command",
        choices=("setup", "doctor"),
        help="Project installer command to run.",
    )
    parser.add_argument(
        "--provider",
        default="codex",
        choices=("codex",),
        help="Compatibility flag; only codex is supported.",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="Target project root. Defaults to the current directory.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.provider != "codex":
        raise ValueError(f"Unsupported provider: {args.provider}")

    spec = build_spec(args.project_root)
    if args.command == "setup":
        return run_setup(spec)
    return run_doctor(spec)


if __name__ == "__main__":
    raise SystemExit(main())
