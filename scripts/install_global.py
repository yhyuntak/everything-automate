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
    ensure_symlink,
    iter_agent_markdown,
    iter_skill_dirs,
    load_agent_definition,
    render_agent_toml,
)


@dataclass(frozen=True)
class ProviderSpec:
    name: str
    template_root: Path
    install_root: Path
    backup_root: Path
    manifest_path: Path
    agents_root: Path
    skills_root: Path


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def build_codex_spec(codex_home: Path) -> ProviderSpec:
    return ProviderSpec(
        name="codex",
        template_root=ROOT / "templates" / "codex",
        install_root=codex_home,
        backup_root=codex_home / "backups" / now_utc(),
        manifest_path=codex_home / "everything-automate" / "install-manifest.json",
        agents_root=codex_home / "agents",
        skills_root=codex_home / "skills",
    )


def copy_with_backup(src: Path, dst: Path, spec: ProviderSpec) -> dict[str, str | None]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    backup_path: Path | None = None

    if dst.exists():
        backup_path = spec.backup_root / dst.relative_to(spec.install_root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        if dst.is_dir():
            shutil.copytree(dst, backup_path, dirs_exist_ok=True)
            shutil.rmtree(dst)
        else:
            shutil.copy2(dst, backup_path)
            dst.unlink()

    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

    return {
        "target": str(dst),
        "source": str(src),
        "backup_path": str(backup_path) if backup_path else None,
    }


def render_agent_with_backup(agent_md: Path, dst: Path, spec: ProviderSpec) -> dict[str, str | None]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    backup_path: Path | None = None

    if dst.exists():
        backup_path = spec.backup_root / dst.relative_to(spec.install_root)
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(dst, backup_path)
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
        "backup_path": str(backup_path) if backup_path else None,
    }


def write_manifest(
    spec: ProviderSpec,
    *,
    status: str,
    installed_assets: list[dict[str, str | None]],
    missing_assets: list[str] | None = None,
    failed_asset: str | None = None,
    error: str | None = None,
) -> None:
    spec.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest = {
        "tool": "everything-automate",
        "provider": spec.name,
        "status": status,
        "install_root": str(spec.install_root),
        "backup_root": str(spec.backup_root),
        "manifest_path": str(spec.manifest_path),
        "written_at": now_utc(),
        "installed_assets": installed_assets,
        "missing_assets": missing_assets or [],
        "failed_asset": failed_asset,
        "error": error,
    }
    spec.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def codex_asset_targets(spec: ProviderSpec) -> list[tuple[str, Path, Path]]:
    assets: list[tuple[str, Path, Path]] = [
        ("file", spec.template_root / "AGENTS.md", spec.install_root / "AGENTS.md"),
    ]

    for agent_md in iter_agent_markdown(spec.template_root):
        agent = load_agent_definition(agent_md)
        assets.append(("agent", agent_md, spec.agents_root / f"{agent.name}.toml"))

    for skill_dir in iter_skill_dirs(spec.template_root):
        assets.append(("dir", skill_dir, spec.skills_root / skill_dir.name))

    return assets


def run_setup(spec: ProviderSpec) -> int:
    installed_assets: list[dict[str, str | None]] = []
    spec.install_root.mkdir(parents=True, exist_ok=True)

    try:
        for asset_kind, src, dst in codex_asset_targets(spec):
            if asset_kind == "agent":
                result = render_agent_with_backup(src, dst, spec)
            else:
                result = copy_with_backup(src, dst, spec)
            result["kind"] = asset_kind
            installed_assets.append(result)
    except Exception as exc:  # pragma: no cover - failure path exercised by manual setup
        write_manifest(
            spec,
            status="failed",
            installed_assets=installed_assets,
            failed_asset=str(dst),
            error=str(exc),
        )
        print("everything-automate setup failed.", file=sys.stderr)
        print(f"- failed asset: {dst}", file=sys.stderr)
        print(f"- error: {exc}", file=sys.stderr)
        if installed_assets:
            print("- installed so far:", file=sys.stderr)
            for asset in installed_assets:
                print(f"  - {asset['target']}", file=sys.stderr)
        print(f"- backup root: {spec.backup_root}", file=sys.stderr)
        print(f"- manifest: {spec.manifest_path}", file=sys.stderr)
        return 1

    write_manifest(spec, status="ok", installed_assets=installed_assets)

    print("Installed everything-automate global Codex setup.")
    print(f"- install root: {spec.install_root}")
    print(f"- backup root: {spec.backup_root}")
    print(f"- manifest: {spec.manifest_path}")
    print("- installed assets:")
    for asset in installed_assets:
        print(f"  - {asset['target']}")
    return 0


def run_doctor(spec: ProviderSpec) -> int:
    expected_assets = codex_asset_targets(spec)
    found_assets: list[str] = []
    missing_assets: list[str] = []

    for _, _, dst in expected_assets:
        if dst.exists():
            found_assets.append(str(dst))
        else:
            missing_assets.append(str(dst))

    manifest_path = spec.manifest_path if spec.manifest_path.exists() else None
    latest_status = "unknown"
    if manifest_path:
        manifest = json.loads(spec.manifest_path.read_text(encoding="utf-8"))
        latest_status = manifest.get("status", "unknown")

    print("everything-automate doctor")
    print(f"- provider: {spec.name}")
    print(f"- managed install root: {spec.install_root}")
    print(f"- managed assets found: {len(found_assets)}")
    print(f"- missing assets: {len(missing_assets)}")
    print(f"- latest manifest path: {manifest_path if manifest_path else '(none)'}")
    print(f"- latest manifest status: {latest_status}")

    if found_assets:
        print("- found:")
        for asset in found_assets:
            print(f"  - {asset}")

    if missing_assets:
        print("- missing:")
        for asset in missing_assets:
            print(f"  - {asset}")
        return 1

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Install everything-automate templates into a provider global root."
    )
    parser.add_argument(
        "command",
        choices=("setup", "doctor"),
        help="Installer command to run.",
    )
    parser.add_argument(
        "--provider",
        default="codex",
        choices=("codex",),
        help="Provider adapter/spec to materialize.",
    )
    parser.add_argument(
        "--codex-home",
        type=Path,
        default=Path.home() / ".codex",
        help="Override the target Codex global root for testing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.provider != "codex":
        raise ValueError(f"Unsupported provider: {args.provider}")

    spec = build_codex_spec(args.codex_home)
    if args.command == "setup":
        return run_setup(spec)
    return run_doctor(spec)


if __name__ == "__main__":
    raise SystemExit(main())
