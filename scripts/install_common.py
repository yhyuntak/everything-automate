#!/usr/bin/env python3

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil


ROOT = Path(__file__).resolve().parents[1]
TEMPLATES_ROOT = ROOT / "templates"

@dataclass(frozen=True)
class AgentDefinition:
    name: str
    description: str
    prompt: str
    model: str
    model_reasoning_effort: str


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


def render_agent_toml(
    name: str,
    description: str,
    prompt: str,
    *,
    model: str,
    model_reasoning_effort: str,
) -> str:
    escaped_prompt = prompt.replace('"""', '\\"""')
    return "\n".join(
        [
            f'name = "{name}"',
            f'description = "{description}"',
            f'model = "{model}"',
            f'model_reasoning_effort = "{model_reasoning_effort}"',
            'sandbox_mode = "read-only"',
            'developer_instructions = """',
            escaped_prompt,
            '"""',
            "",
        ]
    )


def load_agent_definition(agent_md: Path) -> AgentDefinition:
    metadata, body = parse_frontmatter(agent_md)
    name = metadata.get("name", agent_md.stem)
    description = metadata.get("description", f"{name} planning agent")
    model = metadata.get("model", "gpt-5.4-mini")
    model_reasoning_effort = metadata.get("model_reasoning_effort", "medium")
    return AgentDefinition(
        name=name,
        description=description,
        prompt=body,
        model=model,
        model_reasoning_effort=model_reasoning_effort,
    )


def iter_skill_dirs(provider_root: Path) -> list[Path]:
    skills_dir = provider_root / "skills"
    result: list[Path] = []
    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not (skill_dir / "SKILL.md").exists():
            continue
        result.append(skill_dir)
    return result


def iter_agent_markdown(provider_root: Path) -> list[Path]:
    agents_dir = provider_root / "agents"
    return [
        path
        for path in sorted(agents_dir.glob("*.md"))
        if path.name != "README.md"
    ]
