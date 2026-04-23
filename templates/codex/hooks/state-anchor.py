#!/usr/bin/env python3
"""Inject a short workflow anchor from the single workspace active state file."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


MAX_SECTION_CHARS = 900
ACTIVE_RELATIVE_PATH = Path(".everything-automate") / "state" / "active.md"


def read_stdin_json() -> dict:
    raw = sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return data if isinstance(data, dict) else {}


def section(markdown: str, name: str) -> str:
    pattern = re.compile(
        rf"^## {re.escape(name)}\s*\n(?P<body>.*?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(markdown)
    if not match:
        return ""
    body = match.group("body").strip()
    if len(body) <= MAX_SECTION_CHARS:
        return body
    return body[:MAX_SECTION_CHARS].rstrip() + "\n..."


def frontmatter_value(markdown: str, key: str) -> str:
    if not markdown.startswith("---"):
        return ""
    end = markdown.find("\n---", 3)
    if end == -1:
        return ""
    for line in markdown[3:end].splitlines():
        if ":" not in line:
            continue
        raw_key, raw_value = line.split(":", 1)
        if raw_key.strip() == key:
            return raw_value.strip().strip('"')
    return ""


def build_north_star_anchor(markdown: str, stage: str) -> str:
    anchor_message = section(markdown, "Anchor Message")
    north_star = section(markdown, "North Star Draft")
    decision_filter = section(markdown, "Decision Filter")

    parts = [
        "North Star mode is active.",
        f"Stage: {stage}.",
    ]
    if anchor_message:
        parts.extend(["", "Anchor:", anchor_message])
    if north_star:
        parts.extend(["", "Current North Star:", north_star])
    if decision_filter:
        parts.extend(["", "Decision Filter:", decision_filter])
    parts.extend(
        [
            "",
            "Before answering, classify the user's new message as Goal Material, Spec Seed, or Parking Lot.",
            "If the message may redirect the current North Star, challenge it as likely drift before updating the goal.",
            "Do not accept side tasks as Goal Material unless the user explicitly chooses to replace the North Star.",
            "Stay inside the current North Star unless the user explicitly changes it.",
            "Use request_user_input only for clear choices, classification, boundary confirmation, scope cuts, ambiguity choice, or lock/refine confirmation.",
        ]
    )
    return "\n".join(parts).strip()


def build_blueprint_anchor(markdown: str, stage: str) -> str:
    anchor_message = section(markdown, "Anchor Message")
    source_goal = section(markdown, "Source Goal")
    target_and_scope = section(markdown, "Target And Scope")
    current_state = section(markdown, "Current State")
    design_pressure = section(markdown, "Design Pressure")
    proposed_design = section(markdown, "Proposed Design")
    open_questions = section(markdown, "Open Questions And Decisions")
    handoff_notes = section(markdown, "Handoff Notes")

    parts = [
        "Blueprint mode is active.",
        f"Stage: {stage}.",
    ]
    if anchor_message:
        parts.extend(["", "Anchor:", anchor_message])
    if source_goal:
        parts.extend(["", "Source Goal:", source_goal])
    if target_and_scope:
        parts.extend(["", "Target And Scope:", target_and_scope])
    if current_state:
        parts.extend(["", "Current State:", current_state])
    if design_pressure:
        parts.extend(["", "Design Pressure:", design_pressure])
    if proposed_design:
        parts.extend(["", "Proposed Design:", proposed_design])
    if open_questions:
        parts.extend(["", "Open Questions And Decisions:", open_questions])
    if handoff_notes:
        parts.extend(["", "Handoff Notes:", handoff_notes])
    parts.extend(
        [
            "",
            "Stay inside the active blueprint boundary.",
            "Classify new ideas as Blueprint Design Material, Open Question, Handoff Note, or Parking Lot before following them.",
            "Do not turn blueprint work into execution planning unless the user explicitly asks to move stages.",
        ]
    )
    return "\n".join(parts).strip()


def build_anchor(markdown: str) -> str:
    mode = frontmatter_value(markdown, "mode")
    stage = frontmatter_value(markdown, "stage") or "unknown"
    if mode == "north-star":
        return build_north_star_anchor(markdown, stage)
    if mode == "blueprint":
        return build_blueprint_anchor(markdown, stage)
    return ""


def main() -> int:
    payload = read_stdin_json()
    cwd = payload.get("cwd")
    if not isinstance(cwd, str) or not cwd.strip():
        print("{}")
        return 0

    active = Path(cwd) / ACTIVE_RELATIVE_PATH
    if not active.is_file():
        print("{}")
        return 0

    markdown = active.read_text(encoding="utf-8")
    status = frontmatter_value(markdown, "status")
    if status not in {"active", "locked"}:
        print("{}")
        return 0

    anchor = build_anchor(markdown)
    if not anchor:
        print("{}")
        return 0

    output = {
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": anchor,
        }
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
