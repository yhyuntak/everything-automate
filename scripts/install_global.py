#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from bisect import bisect_right
import os
import shutil
import re
import tomllib
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


LEGACY_MANAGED_AGENT_FILES = (
    "advisor.toml",
    "code-reviewer.toml",
    "ea-qa-reviewer.toml",
    "explorer.toml",
    "harness-reviewer.toml",
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
)

CONFIG_FEATURE_KEYS = (
    "multi_agent",
    "codex_hooks",
    "default_mode_request_user_input",
)

FEATURES_HEADER_RE = re.compile(
    r"^\s*\[\s*(?:features|\"features\"|'features')\s*\]\s*(?:#.*)?$"
)
FEATURES_ARRAY_HEADER_RE = re.compile(
    r"^\s*\[\[\s*(?:features|\"features\"|'features')\s*\]\]\s*(?:#.*)?$"
)
FEATURES_TOP_LEVEL_ASSIGNMENT_RE = re.compile(
    r"^\s*(?:features|\"features\"|'features')\s*="
)
FEATURES_ROOT_DOTTED_ASSIGNMENT_RE = re.compile(
    r"^\s*(?:features|\"features\"|'features')\s*\."
)
CONFIG_FEATURE_KEY_RE = r"(?:multi_agent|codex_hooks|default_mode_request_user_input)"
CONFIG_ASSIGNMENT_RE = re.compile(
    r"^\s*(?P<key>(?:'[^']+'|\"[^\"]+\"|[A-Za-z0-9_-]+(?:\.[A-Za-z0-9_-]+)*))\s*=\s*(?P<value>.*)$"
)
MANAGED_CONFIG_FEATURE_RE = re.compile(
    rf"^\s*(?:(?P<quoted>['\"](?P<quoted_key>{CONFIG_FEATURE_KEY_RE})['\"])|(?P<bare>{CONFIG_FEATURE_KEY_RE}))\s*=\s*(?P<value>.*)$"
)
CANONICAL_CONFIG_FEATURE_RE = re.compile(
    rf"^\s*(?P<key>{CONFIG_FEATURE_KEY_RE})\s*=\s*true\s*(?:#.*)?$"
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


def codex_config_path(spec: ProviderSpec) -> Path:
    return spec.install_root / "config.toml"


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

    if dst.exists() or dst.is_symlink():
        backup_path = spec.backup_root / dst.relative_to(spec.install_root)
        backup_existing_path(dst, backup_path)
        remove_existing_path(dst)

    if src.is_dir():
        shutil.copytree(src, dst)
    else:
        shutil.copy2(src, dst)

    return {
        "target": str(dst),
        "source": str(src),
        "backup_path": str(backup_path) if backup_path else None,
    }


def remove_with_backup(path: Path, spec: ProviderSpec) -> dict[str, str | None]:
    backup_path = spec.backup_root / path.relative_to(spec.install_root)
    backup_existing_path(path, backup_path)
    remove_existing_path(path)

    return {
        "target": str(path),
        "backup_path": str(backup_path),
    }


def render_agent_with_backup(agent_md: Path, dst: Path, spec: ProviderSpec) -> dict[str, str | None]:
    dst.parent.mkdir(parents=True, exist_ok=True)
    backup_path: Path | None = None

    if dst.exists() or dst.is_symlink():
        backup_path = spec.backup_root / dst.relative_to(spec.install_root)
        backup_existing_path(dst, backup_path)
        remove_existing_path(dst)

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


def backup_existing_path(path: Path, backup_path: Path) -> None:
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    remove_existing_path(backup_path)

    if path.is_symlink():
        backup_path.symlink_to(os.readlink(path), target_is_directory=path.is_dir())
        return

    if path.is_dir():
        shutil.copytree(path, backup_path, dirs_exist_ok=True)
        return

    shutil.copy2(path, backup_path)


def remove_existing_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def write_manifest(
    spec: ProviderSpec,
    *,
    status: str,
    installed_assets: list[dict[str, str | None]],
    removed_legacy_assets: list[dict[str, str | None]] | None = None,
    missing_assets: list[str] | None = None,
    failed_asset: str | None = None,
    error: str | None = None,
) -> None:
    spec.manifest_path.parent.mkdir(parents=True, exist_ok=True)
    if spec.manifest_path.is_symlink():
        remove_existing_path(spec.manifest_path)
    manifest = {
        "tool": "everything-automate",
        "provider": spec.name,
        "status": status,
        "install_root": str(spec.install_root),
        "backup_root": str(spec.backup_root),
        "manifest_path": str(spec.manifest_path),
        "written_at": now_utc(),
        "installed_assets": installed_assets,
        "removed_legacy_assets": removed_legacy_assets or [],
        "missing_assets": missing_assets or [],
        "failed_asset": failed_asset,
        "error": error,
    }
    spec.manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def codex_asset_targets(spec: ProviderSpec) -> list[tuple[str, Path, Path]]:
    assets: list[tuple[str, Path, Path]] = [
        ("file", spec.template_root / "AGENTS.md", spec.install_root / "AGENTS.md"),
    ]

    hooks_json = spec.template_root / "hooks.json"
    if hooks_json.exists():
        assets.append(("file", hooks_json, spec.install_root / "hooks.json"))

    hooks_dir = spec.template_root / "hooks"
    if hooks_dir.exists():
        assets.append(("dir", hooks_dir, spec.install_root / "hooks"))

    for agent_md in iter_agent_markdown(spec.template_root):
        agent = load_agent_definition(agent_md)
        assets.append(("agent", agent_md, spec.agents_root / f"{agent.name}.toml"))

    for skill_dir in iter_skill_dirs(spec.template_root):
        assets.append(("dir", skill_dir, spec.skills_root / skill_dir.name))

    return assets


def bootstrap_asset_targets(spec: ProviderSpec) -> list[tuple[str, Path, Path]]:
    return [
        ("file", spec.template_root / "AGENTS.md", spec.install_root / "AGENTS.md"),
        ("dir", spec.template_root / "skills" / "ea-setup", spec.skills_root / "ea-setup"),
        ("dir", spec.template_root / "skills" / "ea-doctor", spec.skills_root / "ea-doctor"),
    ]


def remove_legacy_managed_assets(spec: ProviderSpec) -> list[dict[str, str | None]]:
    removed: list[dict[str, str | None]] = []

    for filename in LEGACY_MANAGED_AGENT_FILES:
        path = spec.agents_root / filename
        if not path.exists() and not path.is_symlink():
            continue
        result = remove_with_backup(path, spec)
        result["kind"] = "legacy-agent"
        removed.append(result)

    for dirname in LEGACY_MANAGED_SKILL_DIRS:
        path = spec.skills_root / dirname
        if not path.exists() and not path.is_symlink():
            continue
        result = remove_with_backup(path, spec)
        result["kind"] = "legacy-skill"
        removed.append(result)

    return removed


def render_config_features_block(newline: str) -> str:
    return "".join(
        [
            "[features]",
            newline,
            *[f"{key} = true{newline}" for key in CONFIG_FEATURE_KEYS],
        ]
    )


def build_line_offsets(lines: list[str]) -> list[int]:
    offsets: list[int] = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)
    return offsets


def scan_multiline_string_end(
    text: str, start_offset: int, quote_char: str
) -> int | None:
    delimiter = quote_char * 3
    pos = start_offset + 3
    escape_next = False

    while pos < len(text):
        char = text[pos]
        if quote_char == '"' and escape_next:
            escape_next = False
            pos += 1
            continue

        if quote_char == '"' and char == "\\":
            escape_next = True
            pos += 1
            continue

        if char == quote_char and text.startswith(delimiter, pos):
            return pos + 3

        pos += 1

    return None


def scan_array_end(text: str, start_offset: int) -> int | None:
    pos = start_offset + 1
    depth = 1
    mode: str | None = None
    escape_next = False
    comment = False

    while pos < len(text):
        char = text[pos]

        if comment:
            if char in "\r\n":
                comment = False
            pos += 1
            continue

        if mode is None:
            if char == "#":
                comment = True
            elif char == "[":
                depth += 1
            elif char == "]":
                depth -= 1
                if depth == 0:
                    return pos + 1
            elif char == '"':
                if text.startswith('"""', pos):
                    mode = "basic_multiline"
                    pos += 3
                    escape_next = False
                    continue
                mode = "basic"
            elif char == "'":
                if text.startswith("'''", pos):
                    mode = "literal_multiline"
                    pos += 3
                    continue
                mode = "literal"
            pos += 1
            continue

        if mode == "basic":
            if escape_next:
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == '"':
                mode = None
            pos += 1
            continue

        if mode == "literal":
            if char == "'":
                mode = None
            pos += 1
            continue

        if mode == "basic_multiline":
            if escape_next:
                escape_next = False
            elif char == "\\":
                escape_next = True
            elif char == '"' and text.startswith('"""', pos):
                mode = None
                pos += 3
                continue
            pos += 1
            continue

        if mode == "literal_multiline":
            if char == "'" and text.startswith("'''", pos):
                mode = None
                pos += 3
                continue
            pos += 1
            continue

    return None


def assignment_span_end(
    lines: list[str], text: str, line_offsets: list[int], start_index: int
) -> int:
    match = CONFIG_ASSIGNMENT_RE.match(lines[start_index])
    if not match:
        return start_index + 1

    value = match.group("value")
    start_offset = line_offsets[start_index] + match.start("value")

    if value.startswith('"""'):
        end_offset = scan_multiline_string_end(text, start_offset, '"')
    elif value.startswith("'''"):
        end_offset = scan_multiline_string_end(text, start_offset, "'")
    elif value.startswith("["):
        end_offset = scan_array_end(text, start_offset)
    else:
        return start_index + 1

    if end_offset is None:
        raise RuntimeError(
            "config.toml has an unterminated multiline array or triple-quoted string "
            "inside the managed [features] block; refusing to patch it"
        )

    return bisect_right(line_offsets, end_offset - 1)


def find_features_block_bounds_from(
    lines: list[str], start_index: int = 0
) -> tuple[int | None, int | None]:
    header_index: int | None = None
    for index in range(start_index, len(lines)):
        line = lines[index]
        if FEATURES_HEADER_RE.match(line):
            header_index = index
            break

    if header_index is None:
        return None, None

    text = "".join(lines)
    line_offsets = build_line_offsets(lines)
    end_index = len(lines)
    index = header_index + 1
    while index < len(lines):
        stripped = lines[index].lstrip()
        if stripped.startswith("[") and not stripped.startswith("#"):
            end_index = index
            break
        index = assignment_span_end(lines, text, line_offsets, index)

    return header_index, end_index


def find_features_block_bounds(lines: list[str]) -> tuple[int | None, int | None]:
    return find_features_block_bounds_from(lines)


def find_features_block_ranges(lines: list[str]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    search_index = 0

    while True:
        header_index, end_index = find_features_block_bounds_from(lines, search_index)
        if header_index is None or end_index is None:
            break
        ranges.append((header_index, end_index))
        search_index = end_index

    return ranges


def inspect_config_features(text: str) -> dict[str, object]:
    values: dict[str, object | None] = {key: None for key in CONFIG_FEATURE_KEYS}

    try:
        parsed = tomllib.loads(text) if text else {}
    except tomllib.TOMLDecodeError as exc:
        return {
            "parse_error": str(exc),
            "has_features_block": False,
            "values": values,
        }

    features = parsed.get("features")
    if not isinstance(features, dict):
        return {
            "parse_error": None,
            "has_features_block": False,
            "values": values,
        }

    for key in CONFIG_FEATURE_KEYS:
        values[key] = features.get(key)

    return {
        "parse_error": None,
        "has_features_block": True,
        "values": values,
    }


def inspect_config_feature_lines(text: str) -> dict[str, object]:
    lines = text.splitlines(keepends=True)
    block_ranges = find_features_block_ranges(lines)
    canonical_counts: dict[str, int] = {key: 0 for key in CONFIG_FEATURE_KEYS}
    managed_counts: dict[str, int] = {key: 0 for key in CONFIG_FEATURE_KEYS}

    if not block_ranges:
        return {
            "has_features_block": False,
            "feature_block_count": 0,
            "canonical_counts": canonical_counts,
            "managed_counts": managed_counts,
        }

    for header_index, end_index in block_ranges:
        for line in lines[header_index + 1 : end_index]:
            match = MANAGED_CONFIG_FEATURE_RE.match(line)
            if not match:
                continue
            key = match.group("quoted_key") or match.group("bare")
            if key is None:
                continue
            managed_counts[key] += 1
            if CANONICAL_CONFIG_FEATURE_RE.match(line):
                canonical_counts[key] += 1

    return {
        "has_features_block": True,
        "feature_block_count": len(block_ranges),
        "canonical_counts": canonical_counts,
        "managed_counts": managed_counts,
    }


def build_config_features_text(existing_text: str) -> str:
    newline = "\r\n" if "\r\n" in existing_text else "\n"
    if not existing_text:
        return render_config_features_block(newline)

    lines = existing_text.splitlines(keepends=True)
    text = "".join(lines)
    line_offsets = build_line_offsets(lines)
    config_state = inspect_config_feature_lines(existing_text)
    canonical_counts = config_state["canonical_counts"]
    managed_counts = config_state["managed_counts"]
    already_ok = (
        bool(config_state["has_features_block"])
        and config_state["feature_block_count"] == 1
        and all(
            canonical_counts[key] == 1 and managed_counts[key] == 1
            for key in CONFIG_FEATURE_KEYS
        )
    )
    if already_ok:
        return existing_text

    features_block = render_config_features_block(newline)
    block_ranges = find_features_block_ranges(lines)

    if not block_ranges:
        prefix = existing_text
        if prefix and not prefix.endswith(("\n", "\r")):
            prefix += newline
        return prefix + features_block

    preserved_lines: list[str] = []
    for header_index, end_index in block_ranges:
        index = header_index + 1
        while index < end_index:
            span_end = assignment_span_end(lines, text, line_offsets, index)
            line = lines[index]
            if MANAGED_CONFIG_FEATURE_RE.match(line):
                index = span_end
                continue
            preserved_lines.extend(lines[index:span_end])
            index = span_end

    rebuilt_lines = [
        *lines[:block_ranges[0][0]],
        lines[block_ranges[0][0]],
        *[f"{key} = true{newline}" for key in CONFIG_FEATURE_KEYS],
        *preserved_lines,
    ]
    cursor = block_ranges[0][1]
    for header_index, end_index in block_ranges[1:]:
        rebuilt_lines.extend(lines[cursor:header_index])
        cursor = end_index
    rebuilt_lines.extend(lines[cursor:])
    return "".join(rebuilt_lines)


def has_conflicting_top_level_features_definition(existing_text: str) -> bool:
    if not existing_text:
        return False

    lines = existing_text.splitlines(keepends=True)
    if find_features_block_ranges(lines):
        return False

    for line in lines:
        stripped = line.lstrip()
        if not stripped or stripped.startswith("#"):
            continue
        if FEATURES_ARRAY_HEADER_RE.match(line):
            return True
        if FEATURES_TOP_LEVEL_ASSIGNMENT_RE.match(line):
            return True
        if FEATURES_ROOT_DOTTED_ASSIGNMENT_RE.match(line):
            return True
        if stripped.startswith("["):
            break

    return False


def validate_config_toml(text: str) -> None:
    try:
        tomllib.loads(text)
    except tomllib.TOMLDecodeError as exc:
        raise RuntimeError(f"config.toml is invalid TOML after setup: {exc}") from exc


def run_bootstrap(spec: ProviderSpec) -> int:
    installed_assets: list[dict[str, str | None]] = []
    bootstrap_assets = bootstrap_asset_targets(spec)
    failed_asset = bootstrap_assets[0][2]

    try:
        for asset_kind, src, dst in bootstrap_assets:
            failed_asset = dst
            if asset_kind == "agent":
                result = render_agent_with_backup(src, dst, spec)
            else:
                result = copy_with_backup(src, dst, spec)
            result["kind"] = asset_kind
            installed_assets.append(result)
    except Exception as exc:  # pragma: no cover - failure path exercised manually
        write_manifest(
            spec,
            status="bootstrap-failed",
            installed_assets=installed_assets,
            failed_asset=str(failed_asset),
            error=str(exc),
        )
        print("everything-automate bootstrap failed.", file=sys.stderr)
        print(f"- failed asset: {failed_asset}", file=sys.stderr)
        print(f"- error: {exc}", file=sys.stderr)
        if installed_assets:
            print("- installed so far:", file=sys.stderr)
            for asset in installed_assets:
                print(f"  - {asset['target']}", file=sys.stderr)
        print(f"- manifest: {spec.manifest_path}", file=sys.stderr)
        return 1

    write_manifest(
        spec,
        status="bootstrap",
        installed_assets=installed_assets,
    )

    print("Installed Everything Automate bootstrap surface.")
    print(f"- install root: {spec.install_root}")
    print(f"- manifest: {spec.manifest_path}")
    print("- installed assets:")
    for asset in installed_assets:
        print(f"  - {asset['target']}")
    return 0


def ensure_codex_config_features(spec: ProviderSpec) -> dict[str, str | None]:
    config_path = codex_config_path(spec)
    config_path.parent.mkdir(parents=True, exist_ok=True)

    existing_text = ""
    if config_path.exists():
        existing_text = config_path.read_text(encoding="utf-8")
    if has_conflicting_top_level_features_definition(existing_text):
        raise RuntimeError(
            "config.toml already defines top-level `features` data or root `features.*` "
            "assignments but has no explicit [features] table to patch; refusing to append "
            "a new block"
        )

    updated_text = build_config_features_text(existing_text)
    validate_config_toml(updated_text)
    backup_path: Path | None = None

    if updated_text == existing_text:
        return {
            "target": str(config_path),
            "source": str(config_path),
            "backup_path": None,
        }

    if config_path.exists() or config_path.is_symlink():
        backup_path = spec.backup_root / config_path.relative_to(spec.install_root)
        backup_existing_path(config_path, backup_path)
        remove_existing_path(config_path)

    config_path.write_text(updated_text, encoding="utf-8")
    return {
        "target": str(config_path),
        "source": str(config_path),
        "backup_path": str(backup_path) if backup_path else None,
    }


def run_setup(spec: ProviderSpec) -> int:
    installed_assets: list[dict[str, str | None]] = []
    removed_legacy_assets: list[dict[str, str | None]] = []
    failed_asset = codex_config_path(spec)

    try:
        config_result = ensure_codex_config_features(spec)
        config_result["kind"] = "config"
        installed_assets.append(config_result)

        full_assets = codex_asset_targets(spec)
        for asset_kind, src, dst in full_assets:
            failed_asset = dst
            if asset_kind == "agent":
                result = render_agent_with_backup(src, dst, spec)
            else:
                result = copy_with_backup(src, dst, spec)
            result["kind"] = asset_kind
            installed_assets.append(result)
        removed_legacy_assets = remove_legacy_managed_assets(spec)
    except Exception as exc:  # pragma: no cover - failure path exercised by manual setup
        write_manifest(
            spec,
            status="failed",
            installed_assets=installed_assets,
            removed_legacy_assets=removed_legacy_assets,
            failed_asset=str(failed_asset),
            error=str(exc),
        )
        print("everything-automate setup failed.", file=sys.stderr)
        print(f"- failed asset: {failed_asset}", file=sys.stderr)
        print(f"- error: {exc}", file=sys.stderr)
        if installed_assets:
            print("- installed so far:", file=sys.stderr)
            for asset in installed_assets:
                print(f"  - {asset['target']}", file=sys.stderr)
        print(f"- backup root: {spec.backup_root}", file=sys.stderr)
        print(f"- manifest: {spec.manifest_path}", file=sys.stderr)
        return 1

    write_manifest(
        spec,
        status="ok",
        installed_assets=installed_assets,
        removed_legacy_assets=removed_legacy_assets,
    )

    print("Installed Everything Automate full Codex setup.")
    print(f"- install root: {spec.install_root}")
    print(f"- backup root: {spec.backup_root}")
    print(f"- manifest: {spec.manifest_path}")
    print("- installed assets:")
    for asset in installed_assets:
        print(f"  - {asset['target']}")
    if removed_legacy_assets:
        print("- removed legacy managed assets:")
        for asset in removed_legacy_assets:
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

    manifest_path = (
        spec.manifest_path
        if spec.manifest_path.exists() or spec.manifest_path.is_symlink()
        else None
    )
    latest_status = "unknown"
    manifest_parse_error: str | None = None
    if manifest_path:
        try:
            manifest = json.loads(spec.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            latest_status = "invalid"
            manifest_parse_error = str(exc)
        else:
            latest_status = manifest.get("status", "unknown")

    config_path = codex_config_path(spec)
    config_text = ""
    config_read_error: str | None = None
    if config_path.exists():
        try:
            config_text = config_path.read_text(encoding="utf-8")
        except OSError as exc:
            config_read_error = str(exc)
    config_state = None
    config_values: dict[str, object | None] = {key: None for key in CONFIG_FEATURE_KEYS}
    config_parse_error: str | None = None
    config_conflict = False
    has_features_block = False
    if config_read_error is None:
        try:
            config_conflict = has_conflicting_top_level_features_definition(config_text)
        except RuntimeError as exc:
            config_parse_error = str(exc)

        try:
            config_state = inspect_config_feature_lines(config_text)
            has_features_block = bool(config_state["has_features_block"])
        except RuntimeError as exc:
            config_parse_error = str(exc)

        if config_parse_error is None:
            parsed_state = inspect_config_features(config_text)
            config_values = parsed_state["values"]
            config_parse_error = parsed_state["parse_error"]
            if config_state is None:
                has_features_block = bool(parsed_state["has_features_block"])

    config_complete = (
        config_read_error is None
        and config_parse_error is None
        and not config_conflict
        and has_features_block
        and all(config_values[key] is True for key in CONFIG_FEATURE_KEYS)
    )
    legacy_assets = [
        *(spec.agents_root / filename for filename in LEGACY_MANAGED_AGENT_FILES),
        *(spec.skills_root / dirname for dirname in LEGACY_MANAGED_SKILL_DIRS),
    ]
    found_legacy = [
        str(path) for path in legacy_assets if path.exists() or path.is_symlink()
    ]
    ready = (
        not missing_assets
        and config_complete
        and not found_legacy
        and manifest_parse_error is None
    )

    print("everything-automate doctor")
    print(f"- target: {spec.name}")
    print(f"- managed install root: {spec.install_root}")
    print(f"- managed assets found: {len(found_assets)}")
    print(f"- missing assets: {len(missing_assets)}")
    print(f"- latest manifest path: {manifest_path if manifest_path else '(none)'}")
    print(f"- latest manifest status: {latest_status}")
    if manifest_parse_error is not None:
        print(f"- latest manifest parse error: {manifest_parse_error}")
    print(f"- ready: {'yes' if ready else 'no'}")

    if found_assets:
        print("- found:")
        for asset in found_assets:
            print(f"  - {asset}")

    print(f"- managed config path: {config_path}")
    print(f"- required config feature flags present: {'yes' if config_complete else 'no'}")
    if config_read_error is not None:
        print(f"- config TOML: unreadable ({config_read_error})")
    elif config_parse_error is not None:
        print(f"- config TOML: invalid ({config_parse_error})")
    elif config_conflict:
        print(
            "- config feature flags: conflict (top-level features data or root "
            "features.* assignments without an explicit [features] table)"
        )
    elif config_state is not None and has_features_block:
        print("- config feature flags:")
        for key in CONFIG_FEATURE_KEYS:
            value = config_values[key]
            if value is True:
                status = "true"
            elif value is None:
                status = "missing"
            elif isinstance(value, bool):
                status = "false"
            else:
                status = f"wrong type ({type(value).__name__})"
            print(f"  - {key}: {status}")
    else:
        print("- config feature flags: missing [features] block")

    if found_legacy:
        print("- legacy managed assets still present:")
        for asset in found_legacy:
            print(f"  - {asset}")
        return 1

    if missing_assets:
        print("- missing:")
        for asset in missing_assets:
            print(f"  - {asset}")
        return 1

    if not config_complete or manifest_parse_error is not None:
        return 1

    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Manage the Codex Everything Automate runtime."
    )
    parser.add_argument(
        "command",
        choices=("bootstrap", "setup", "doctor"),
        help="Installer command to run.",
    )
    parser.add_argument(
        "--provider",
        default="codex",
        choices=("codex",),
        help="Compatibility flag; only codex is supported.",
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
    if args.command == "bootstrap":
        return run_bootstrap(spec)
    if args.command == "setup":
        return run_setup(spec)
    return run_doctor(spec)


if __name__ == "__main__":
    raise SystemExit(main())
