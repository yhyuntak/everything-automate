#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = ROOT / "templates" / "codex"
TARGET_CODEX_ROOT = ROOT / ".codex"
TARGET_SKILLS_DIR = TARGET_CODEX_ROOT / "skills"
TARGET_AGENTS_DIR = TARGET_CODEX_ROOT / "agents"
TARGET_TESTING_DIR = TARGET_CODEX_ROOT / "testing"
TARGET_RUNTIME_DIR = ROOT / ".everything-automate"

AGENT_MODELS = {
    "explorer": ("gpt-5.4-mini", "medium"),
    "angel": ("gpt-5.4", "high"),
    "architect": ("gpt-5.4", "high"),
    "devil": ("gpt-5.4", "high"),
}


def parse_frontmatter(md_path: Path) -> tuple[dict[str, str], str]:
    text = md_path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        return {}, text.strip()

    _, rest = text.split("---\n", 1)
    frontmatter_text, body = rest.split("\n---\n", 1)
    metadata: dict[str, str] = {}
    for line in frontmatter_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip()
    return metadata, body.strip()


def replace_path(dst: Path) -> None:
    if dst.is_symlink() or dst.is_file():
        dst.unlink()
    elif dst.is_dir():
        shutil.rmtree(dst)


def ensure_symlink(src: Path, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() or dst.is_symlink():
        replace_path(dst)
    dst.symlink_to(src.resolve(), target_is_directory=src.is_dir())


def render_agent_toml(name: str, description: str, prompt: str) -> str:
    model, reasoning = AGENT_MODELS.get(name, ("gpt-5.4-mini", "medium"))
    escaped_prompt = prompt.replace('"""', '\\"""')
    return "\n".join(
        [
            f'name = "{name}"',
            f'description = "{description}"',
            f'model = "{model}"',
            f'model_reasoning_effort = "{reasoning}"',
            'sandbox_mode = "read-only"',
            'developer_instructions = """',
            escaped_prompt,
            '"""',
            "",
        ]
    )


def install_skills() -> list[str]:
    skill_names: list[str] = []
    source_skills_dir = TEMPLATE_ROOT / "skills"
    TARGET_SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    for skill_dir in sorted(source_skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.exists():
            continue
        ensure_symlink(skill_dir, TARGET_SKILLS_DIR / skill_dir.name)
        skill_names.append(skill_dir.name)

    return skill_names


def install_agents() -> list[str]:
    agent_names: list[str] = []
    source_agents_dir = TEMPLATE_ROOT / "agents"
    TARGET_AGENTS_DIR.mkdir(parents=True, exist_ok=True)

    for agent_md in sorted(source_agents_dir.glob("*.md")):
        if agent_md.name == "README.md":
            continue
        metadata, body = parse_frontmatter(agent_md)
        name = metadata.get("name", agent_md.stem)
        description = metadata.get("description", f"{name} planning agent")
        toml = render_agent_toml(name, description, body)
        (TARGET_AGENTS_DIR / f"{name}.toml").write_text(toml, encoding="utf-8")
        agent_names.append(name)

    return agent_names


def install_testing_references() -> None:
    TARGET_TESTING_DIR.mkdir(parents=True, exist_ok=True)
    TARGET_RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    (TARGET_RUNTIME_DIR / "plans").mkdir(parents=True, exist_ok=True)
    ensure_symlink(TEMPLATE_ROOT / "AGENTS.md", TARGET_TESTING_DIR / "codex-template-AGENTS.md")
    ensure_symlink(TEMPLATE_ROOT / "INSTALL.md", TARGET_TESTING_DIR / "codex-template-INSTALL.md")


def write_manifest(skills: list[str], agents: list[str]) -> Path:
    manifest_path = TARGET_TESTING_DIR / "local-install-manifest.json"
    manifest = {
        "workspace_root": str(ROOT),
        "skills_dir": str(TARGET_SKILLS_DIR),
        "agents_dir": str(TARGET_AGENTS_DIR),
        "template_runtime_guidance": str(TARGET_TESTING_DIR / "codex-template-AGENTS.md"),
        "installed_skills": skills,
        "installed_agents": agents,
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
    install_testing_references()
    manifest_path = write_manifest(skills, agents)

    print("Installed project-local Codex test assets:")
    print(f"- skills: {', '.join(skills)}")
    print(f"- agents: {', '.join(agents)}")
    print(f"- manifest: {manifest_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
