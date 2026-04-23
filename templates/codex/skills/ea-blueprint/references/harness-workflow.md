# Harness Workflow

Use when the blueprint is about agents, prompts, hooks, state files, routing, or workflow control.

Design forces:
- Keep one clear source of truth for state.
- Make role boundaries and handoffs explicit.
- Treat routing, gates, and lifecycle as first-class design choices.

Risk hints:
- Mode confusion or mixed responsibilities.
- Broken handoff between steps or agents.
- Loops that never settle or skip needed gates.

Output focus:
- Workflow shape, state flow, and gate responsibilities.
- Routing rules and handoff notes.
- What the harness must store, ask, and check.
