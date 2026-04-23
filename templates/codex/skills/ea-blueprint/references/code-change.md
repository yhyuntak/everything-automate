# Code Change

Use when the blueprint is mainly about app code, scripts, hooks, tests, config, or data shape changes.

Design forces:
- Keep existing boundaries clear.
- Prefer the smallest safe change to the current system shape.
- Check data flow, control flow, and testability before adding abstractions.

Risk hints:
- Hidden coupling across files or layers.
- Over-refactoring before the real shape is clear.
- Migration or compatibility risk when state or schema changes.

Output focus:
- What modules, boundaries, or interfaces should change.
- What must stay stable.
- Which tradeoffs matter for implementation.
- Execution-Shape Sufficiency: the design is clear enough on components, boundaries, ownership, flows, and decisions that planning can slice the work without inventing the core shape. Do not ask for TC slices, file edit order, worker assignment, or verification command details.
