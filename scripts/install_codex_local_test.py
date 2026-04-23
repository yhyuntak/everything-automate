#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from install_common import (
    ROOT,
    ensure_symlink,
    iter_agent_markdown,
    iter_skill_dirs,
    load_agent_definition,
    render_agent_toml,
)


TEMPLATE_ROOT = ROOT / "templates" / "codex"
TARGET_CODEX_ROOT = ROOT / ".codex"
TARGET_SKILLS_DIR = TARGET_CODEX_ROOT / "skills"
TARGET_AGENTS_DIR = TARGET_CODEX_ROOT / "agents"
TARGET_HOOKS_DIR = TARGET_CODEX_ROOT / "hooks"
TARGET_TESTING_DIR = TARGET_CODEX_ROOT / "testing"
TARGET_RUNTIME_DIR = ROOT / ".everything-automate"


def install_skills() -> list[str]:
    skill_names: list[str] = []
    TARGET_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    for skill_dir in iter_skill_dirs(TEMPLATE_ROOT):
        ensure_symlink(skill_dir, TARGET_SKILLS_DIR / skill_dir.name)
        skill_names.append(skill_dir.name)

    return skill_names


def install_agents() -> list[str]:
    agent_names: list[str] = []
    TARGET_AGENTS_DIR.mkdir(parents=True, exist_ok=True)

    for agent_md in iter_agent_markdown(TEMPLATE_ROOT):
        agent = load_agent_definition(agent_md)
        toml = render_agent_toml(
            agent.name,
            agent.description,
            agent.prompt,
            model=agent.model,
            model_reasoning_effort=agent.model_reasoning_effort,
            sandbox_mode=agent.sandbox_mode,
        )
        (TARGET_AGENTS_DIR / f"{agent.name}.toml").write_text(toml, encoding="utf-8")
        agent_names.append(agent.name)

    return agent_names


def install_hooks() -> list[str]:
    installed: list[str] = []
    hooks_json = TEMPLATE_ROOT / "hooks.json"
    if hooks_json.exists():
        ensure_symlink(hooks_json, TARGET_CODEX_ROOT / "hooks.json")
        installed.append("hooks.json")

    hooks_dir = TEMPLATE_ROOT / "hooks"
    if hooks_dir.exists():
        ensure_symlink(hooks_dir, TARGET_HOOKS_DIR)
        installed.append("hooks/")

    return installed


def install_testing_references() -> None:
    TARGET_TESTING_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    (TARGET_RUNTIME_DIR / "plans").mkdir(parents=True, exist_ok=True)
    ensure_symlink(TEMPLATE_ROOT / "AGENTS.md", TARGET_TESTING_DIR / "codex-template-AGENTS.md")
    ensure_symlink(TEMPLATE_ROOT / "INSTALL.md", TARGET_TESTING_DIR / "codex-template-INSTALL.md")


def write_manifest(skills: list[str], agents: list[str], hooks: list[str]) -> Path:
    manifest_path = TARGET_TESTING_DIR / "local-install-manifest.json"
    manifest = {
        "workspace_root": str(ROOT),
        "skills_dir": str(TARGET_SKILLS_DIR),
        "agents_dir": str(TARGET_AGENTS_DIR),
        "template_runtime_guidance": str(TARGET_TESTING_DIR / "codex-template-AGENTS.md"),
        "installed_skills": skills,
        "installed_agents": agents,
        "installed_hooks": hooks,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return manifest_path


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install the Codex template into project-local .codex/ for testing."
    )
    parser.parse_args()

    skills = install_skills()
    agents = install_agents()
    hooks = install_hooks()
    install_testing_references()
    manifest_path = write_manifest(skills, agents, hooks)

    print("Installed project-local Codex test assets:")
    print(f"- skills: {', '.join(skills)}")
    print(f"- agents: {', '.join(agents)}")
    print(f"- hooks: {', '.join(hooks) if hooks else '(none)'}")
    print(f"- manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
