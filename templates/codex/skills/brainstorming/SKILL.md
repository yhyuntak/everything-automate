---
name: brainstorming
description: Help shape an idea, feature, design direction, or document direction before deciding what to do next.
argument-hint: "<idea, feature, design question, doc idea, or vague request>"
---

# brainstorming

Use this when the user needs help thinking, not just help planning execution.

## Purpose

`brainstorming` is a thinking skill.

Its job is to:

- make a fuzzy idea clearer
- help the user say what they really want
- narrow a broad thought into a direction
- compare a few realistic directions when useful
- recommend one direction when that helps
- end with a useful next step

That next step may be:

- stop here
- keep brainstorming
- move to `$planning`

`brainstorming` does **not** have to end in planning.

## Use When

Use `brainstorming` when the user wants help with any of these:

- shaping a raw idea
- turning a backlog item into something clearer
- thinking through a feature direction
- thinking through a design direction
- thinking through a document direction
- sorting out a vague request before deciding whether execution even makes sense

## Do Not Use When

Do **not** use `brainstorming` when:

- the request is already clear enough for `$planning`
- the user already wants a file-based execution plan
- the user already has an approved plan and wants implementation
- the task is only to review finished work

## Core Rule

`brainstorming` is not implementation.
It is not execution planning.
It is not a hidden version of `$planning`.

Its job is to help the user think clearly enough to choose a direction.

## Routing

Start by routing the request into one of 4 lanes.

### 1. `idea shaping`

Use this when the user has a broad idea, a vague direction, or an early thought that is still hard to name clearly.

### 2. `feature shaping`

Use this when the user has a backlog item, feature idea, or product change that needs clearer scope and value.

### 3. `design shaping`

Use this when the user is thinking about code design, technical structure, architecture direction, or testing direction.

### 4. `doc shaping`

Use this when the user is thinking about a document, note, guide, spec, README, or other writing direction.

## Interaction Style

`brainstorming` is interactive by default.

- Ask one strong question at a time.
- Do not dump a long checklist on the user.
- Use simple English.
- Reflect back what became clearer before asking the next question.
- Stop asking once the direction is clear enough.

If repo context matters, look first before asking the user for facts that the repo can tell you.

## Lane Goals

Do not force one fixed interview script.
Instead, use questions that help reveal the right things for the current lane.

### `idea shaping`

Try to reveal:

- why this idea matters
- what change the user wants to see
- what still feels blurry
- what kind of direction feels promising

### `feature shaping`

Try to reveal:

- who the feature is for
- what value it should create
- what the smallest useful version is
- what should stay out of scope for now

### `design shaping`

Try to reveal:

- what technical problem needs a direction
- what constraints already exist
- what must not break
- what kind of test strategy makes sense

### `doc shaping`

Try to reveal:

- who the document is for
- what the reader should understand or do after reading
- what kind of document this is
- what structure would make it easiest to use

## Default Flow

```text
request
  -> quick route
  -> pick the lane
  -> ask the strongest next question
  -> reflect back what became clearer
  -> ask again only if needed
  -> narrow the direction
  -> recommend or synthesize
  -> choose next step
     -> stop
     -> keep brainstorming
     -> move to $planning
```

## Rules

- Do not implement during brainstorming.
- Do not turn brainstorming into hidden planning.
- Do not force the user into `$planning` if they only want thought cleanup.
- Do not use one rigid question list for every lane.
- Do not force one rigid output template for every brainstorm.
- Ask about the reason behind the request before pushing too fast into how to build it.
- Keep the result useful, but not over-structured.

## Output Modes

End in the form that best fits the discussion.

Allowed output modes include:

- `idea brief`
- `feature direction note`
- `design direction note`
- `doc direction note`
- `option comparison`
- `recommended direction`
- `planning handoff note`

Do not force the same shape every time.

No matter which mode you use, the result should make these clear enough:

- what the user is trying to do
- what direction now looks strongest
- what is still open, if anything
- what the next step should be

## When To Move To `$planning`

Move to `$planning` only when the user now wants execution planning.

That usually means:

- the direction is clear enough
- scope is clear enough
- the user wants real implementation planning
- a file-based plan would now help more than another thinking pass

## Completion

`brainstorming` is complete when:

- the user can see the direction more clearly
- the conversation has produced a useful thinking result
- the next step is clear
- the user can either stop, continue brainstorming, or move to `$planning`
