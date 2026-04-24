# Dependency Patterns

Use these questions when deciding milestone order:

- does milestone B need the artifact from milestone A?
- would doing this later force redesign of earlier work?
- does this milestone reduce ambiguity for later brainstorming and planning?
- is this milestone only polish and therefore safe to push later?

Common dependency patterns:

- investigation -> document -> frontend
- north star -> roadmap -> brainstorming -> planning
- schema decision -> implementation design -> execution

Record dependencies simply.

Good:

- `guide document v1` depends on `investigation summary`

Weak:

- `docs work should probably happen first because it feels better`
