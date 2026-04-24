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


def build_milestone_anchor(markdown: str, stage: str) -> str:
    anchor_message = section(markdown, "Anchor Message")
    parent_goal = section(markdown, "Parent Goal")
    milestone_list = section(markdown, "Milestone List")
    current_milestone = section(markdown, "Current Milestone Recommendation")
    ordering_logic = section(markdown, "Ordering Logic")

    parts = [
        "Milestone mode is active.",
        f"Stage: {stage}.",
    ]
    if anchor_message:
        parts.extend(["", "Anchor:", anchor_message])
    if parent_goal:
        parts.extend(["", "Parent Goal:", parent_goal])
    if current_milestone:
        parts.extend(["", "Current Milestone Recommendation:", current_milestone])
    if milestone_list:
        parts.extend(["", "Milestone List:", milestone_list])
    if ordering_logic:
        parts.extend(["", "Ordering Logic:", ordering_logic])
    parts.extend(
        [
            "",
            "Stay inside the active milestone boundary.",
            "Classify new ideas as Milestone Material, Ordering Question, Dependency Note, or Parking Lot before following them.",
            "Keep milestones output-first and make the current milestone recommendation explicit.",
        ]
    )
    return "\n".join(parts).strip()


def build_brainstorming_anchor(markdown: str, stage: str) -> str:
    anchor_message = section(markdown, "Anchor Message")
    source_milestone = section(markdown, "Source Milestone")
    boundary = section(markdown, "Boundary")
    codebase_context = section(markdown, "Codebase Context")
    senior_scan = section(markdown, "Senior Engineer Scan")
    current_design = section(markdown, "Current Design Direction")
    decisions = section(markdown, "Decisions")
    open_questions = section(markdown, "Open Questions")
    parking_lot = section(markdown, "Parking Lot")
    planning_handoff = section(markdown, "Planning Handoff")

    parts = [
        "Brainstorming mode is active.",
        f"Stage: {stage}.",
    ]
    if anchor_message:
        parts.extend(["", "Anchor:", anchor_message])
    if source_milestone:
        parts.extend(["", "Source Milestone:", source_milestone])
    if boundary:
        parts.extend(["", "Boundary:", boundary])
    if codebase_context:
        parts.extend(["", "Codebase Context:", codebase_context])
    if senior_scan:
        parts.extend(["", "Senior Engineer Scan:", senior_scan])
    if current_design:
        parts.extend(["", "Current Design Direction:", current_design])
    if decisions:
        parts.extend(["", "Decisions:", decisions])
    if open_questions:
        parts.extend(["", "Open Questions:", open_questions])
    if parking_lot:
        parts.extend(["", "Parking Lot:", parking_lot])
    if planning_handoff:
        parts.extend(["", "Planning Handoff:", planning_handoff])
    parts.extend(
        [
            "",
            "Stay inside the chosen code milestone boundary.",
            "Classify new ideas as Code Design Material, Learning Question, Decision, Open Question, or Parking Lot before following them.",
            "Do not implement or write an execution plan in brainstorming mode.",
            "If the user asks for implementation planning, first make sure the integrated design note is accepted and archived.",
        ]
    )
    return "\n".join(parts).strip()


def build_anchor(markdown: str) -> str:
    mode = frontmatter_value(markdown, "mode")
    stage = frontmatter_value(markdown, "stage") or "unknown"
    if mode == "brainstorming":
        return build_brainstorming_anchor(markdown, stage)
    if mode == "north-star":
        return build_north_star_anchor(markdown, stage)
    if mode == "milestone":
        return build_milestone_anchor(markdown, stage)
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
