---
title: Codex Execute Hardening
description: Codex `execute` skill의 verify, decide, retry, progress, terminal semantics, 그리고 state/runtime 연동 gap을 검증하고 보완하기 위한 현재 M5 작업 문서.
doc_type: workflow
scope:
  - codex
  - execute
  - verification
  - retry
  - state
covers:
  - templates/codex/skills/execute/SKILL.md
  - templates/codex/skills/planning/SKILL.md
  - runtime/ea_state.py
  - runtime/ea_codex.py
  - scripts/install_global.py
---

# Codex Execute Hardening

이 문서는 현재 active 마일스톤인 `M5`를 구체화한다.

핵심 질문은 단순하다.

- `execute`가 실제로 `verify`와 `decide`를 내부 루프로 충분히 수행하는가
- `planning` handoff를 자연스럽게 소비하는가
- retry / blocker / scope drift / terminal semantics가 모호하지 않은가
- state/runtime helper가 필요한 만큼만 붙어 있는가

## 현재 전제

현재 user-facing Codex workflow는 다음과 같다.

```text
$brainstorming
  -> $planning
  -> $execute
```

그리고 `execute`는 별도 `$verify`, `$decide` surface가 아니라 아래를 내부에 포함한 skill contract다.

```text
readiness check
  -> execute
  -> verify
  -> decide
  -> fix
  -> repeat
```

즉 `M5`는 새로운 surface를 더 만드는 단계가 아니라, **이미 정의된 `execute`가 실제로 충분한지 검증하고 보완하는 단계**다.

## Hardening Focus

### 1. Handoff Consumption

검증할 것:

- `execute`가 `planning` handoff block을 충분히 소비하는가
- `approval_state`, `execution_unit`, `problem_framing`, `decision_drivers`, `recommended_direction`이 실제로 필요한 만큼 계약에 반영돼 있는가
- handoff가 얇아서 execution이 planning 결정을 다시 흔들게 되지 않는가

### 2. Readiness Gate

검증할 것:

- readiness check가 너무 약하지 않은가
- readiness failure 시 실제로 planning으로 되돌리는 경로가 선명한가
- verification steps가 약한 plan은 진입 불가로 처리되는가

### 3. Verify / Decide Loop

검증할 것:

- `verify`가 fresh evidence 기준으로 충분히 정의되어 있는가
- `decide` 결과가 실제로 다음 행동으로 이어지는가
- `pass / fail / blocked / scope_drift`의 의미가 명확한가

### 4. Retry / Escalation

검증할 것:

- bounded retry가 실제로 충분히 설명되어 있는가
- 같은 failure가 반복될 때 local retry를 멈추는 기준이 있는가
- 언제 planning으로 되돌리고, 언제 failed로 보는지 충분히 선명한가

### 5. Scope Drift

검증할 것:

- small discovered sub-work를 언제 흡수해도 되는가
- boundary-crossing work는 언제 무조건 planning으로 되돌아가야 하는가
- `execute`가 replanning으로 붕괴하지 않는가

### 6. Progress Contract

검증할 것:

- 현재 AC
- completed ACs
- blocked ACs
- failed-verification ACs
- latest evidence

위 다섯 항목이 실제로 progress contract로 충분한가

### 7. Terminal Outcomes

검증할 것:

- `complete`
- `cancelled`
- `failed`
- `suspended/interrupted`

이 네 outcome이 서로 안 섞이는가

특히 볼 것:

- `complete`에 필요한 evidence floor
- `cancelled`에서 partial-progress를 어떻게 남기는가
- `failed`와 `interrupted`의 차이

### 8. State / Runtime Gap

검증할 것:

- `runtime/ea_state.py`가 현재 `execute` 흐름과 얼마나 잘 맞는가
- 현재는 skill contract만 있고 runtime support가 덜한 부분이 무엇인가
- `runtime/ea_codex.py`가 실제 UX를 대체하지 않으면서 보조 역할을 할 수 있는가

### 9. Installed Usability

검증할 것:

- global installer로 깔린 `~/.codex/skills/execute`가 실제 사용 surface로 충분한가
- installer / doctor / manifest가 execute hardening과 충돌하지 않는가

## Current Checklist

- [x] `planning -> execute` handoff example 하나를 실제로 읽어 본다.
- [x] readiness failure 예시를 하나 만든다.
- [x] verify / decide 분기 예시를 문서화한다.
- [x] retry bound와 escalation example을 만든다.
- [x] scope drift in-bound / out-of-bound 예시를 만든다.
- [ ] partial-progress summary example을 만든다.
- [ ] `complete / cancelled / failed / interrupted` summary example을 만든다.
- [ ] `ea_state.py`와 `execute` contract의 gap을 정리한다.
- [ ] global install된 skill 기준으로 사용성을 다시 본다.

## Ordered Work Checklist

`M5`는 아래 순서대로 진행한다.

### 1. Entry and Branch Semantics

- [x] `planning -> execute` handoff example read-through
- [x] readiness failure example
- [ ] `verify / decide` branch examples
- [ ] retry bound / escalation example
- [ ] scope drift in-bound / out-of-bound example

이 단계를 먼저 하는 이유:

- `execute`가 어디서 시작 가능하고
- 어떤 경우에 pass / fail / blocked / scope_drift를 내는지
- 언제 planning으로 되돌아가야 하는지

를 먼저 잠가야 progress/state 설계가 덜 흔들린다.

### 2. Progress and Terminal Artifacts

- [ ] partial-progress summary example
- [ ] `complete / cancelled / failed / interrupted` summary examples
- [ ] AC-level progress를 별도 artifact로 둘지 `ea_state.py`로 흡수할지 결정

이 단계의 목표:

- `execute`가 중간 상태와 끝난 상태를 어떤 모양으로 남기는지 고정
- progress artifact와 run-level state의 경계를 분명히 하기

### 3. State / Runtime Fit

- [ ] `ea_state.py`와 `execute` contract의 gap 정리
- [ ] `runtime/ea_codex.py`가 보조 역할로 충분한지 점검

이 단계의 목표:

- 지금 runtime helper가 과한지 부족한지 판단
- 필요한 support만 남기고 user-facing UX와 분리 유지

### 4. Installed Usability

- [ ] global install된 skill 기준으로 사용성 다시 보기

이 단계의 목표:

- 문서상 contract가 아니라 실제 설치된 Codex skill surface로도 납득되는지 확인

## Validation Notes

### Reference Cross-Check Summary

레퍼런스 기준으로 보면 현재 `M5` 방향은 정당하다.

- strong execution entry gate는 공통 패턴이다.
  - approved/validated plan 없이 execution으로 바로 들어가는 쪽이 아니라,
    readiness를 먼저 확인하는 쪽이 더 일반적이다.
- run-level state와 AC/story/progress 기록을 분리하는 패턴도 흔하다.
  - 즉 큰 상태와 세부 진행상황을 같은 파일 하나에 모두 넣지 않는 쪽이 자연스럽다.
- `execute` 내부에 `verify / decide`를 포함하는 구조 자체는 문제 없다.
  - 다만 이 경우에는 분기 규칙과 terminal summary를 더 선명하게 써야 한다.

현재 결론:

```text
M5 direction
  -> justified

remaining open questions
  -> verify / decide branch examples
  -> progress artifact vs ea_state.py expansion
  -> terminal summary shape
```

### Example 1. `global-codex-setup-v0` handoff read-through

읽은 artifact:

- `.everything-automate/plans/2026-04-06-global-codex-setup-v0.md`

관찰 결과:

- handoff block 자체는 존재한다.
- `task_id`, `plan_path`, `approval_state`, `execution_unit`, `recommended_mode`, `recommended_agents`, `verification_lane`, `open_risks`가 모두 있다.
- `problem_framing`, `decision_drivers`, `viable_options`, `recommended_direction`도 문서 본문에 존재한다.
- 하지만 현재 `approval_state`는 `draft`다.

현재 판단:

- 이 artifact는 `planning -> execute` 경계의 예시로는 충분하다.
- 하지만 현재 상태로는 `execute`가 실제 진입을 허용하면 안 된다.
- 즉 `M5` 관점의 첫 readiness rule은 이미 분명하다.

```text
approval_state != approved
  -> execute must refuse entry
  -> return to planning / approval
```

의미:

- `execute`는 handoff block의 존재만 확인하면 안 된다.
- `approval_state`와 explicit approval을 같이 확인해야 한다.
- `planning` 산출물은 draft와 approved를 같은 형식으로 공유할 수 있지만, `execute`는 그 차이를 엄격하게 봐야 한다.

### Example 2. Readiness Failure on Draft Handoff

상황:

- handoff block은 존재한다.
- acceptance criteria와 verification steps도 존재한다.
- 하지만 `approval_state: draft`다.

기대 동작:

```text
execute status: refused
reason: approval_state is draft
missing readiness:
  - explicit approval
next action:
  - return to $planning
```

현재 판단:

- `execute`는 이 상황에서 코드를 만지거나 AC를 선택하면 안 된다.
- handoff completeness와 execution readiness는 같은 개념이 아니다.
- `M5`에서 `execute`는 "handoff exists"가 아니라 "approved and executable"을 entry gate로 써야 한다.

### Example 3. `pass`

상황:

- current AC: global installer에 `setup`과 `doctor` surface를 추가한다.
- fresh evidence:
  - `python3 -m py_compile scripts/install_common.py scripts/install_global.py`
  - temp install root에서 `setup` 성공
  - temp install root에서 `doctor` 성공

기대 동작:

```text
decide: pass
reason: current AC is satisfied and fresh evidence proves it
next action: mark the AC complete and move on
```

현재 판단:

- `pass`는 단순히 코드가 있어 보인다는 뜻이 아니다.
- 현재 AC를 증명하는 fresh evidence가 있어야 한다.

### Example 4. `fail`

상황:

- current AC: doctor가 missing managed asset을 올바르게 보고한다.
- fresh evidence:
  - command는 실행되지만
  - missing manifest path에서 crash한다.

기대 동작:

```text
decide: fail
reason: current AC is still the right target, but fresh evidence shows it is not satisfied
next action: fix and re-verify within retry bounds
```

현재 판단:

- `fail`은 local retry가 여전히 합리적인 경우다.
- 아직 blocker나 replanning으로 넘기기 전의 상태다.

### Example 5. `blocked`

상황:

- current AC: 실제 global Codex 환경에서 installed skill usability를 검증한다.
- local evidence:
  - 설치된 파일은 있다.
  - 하지만 필요한 외부 환경, 권한, 또는 dependency가 현재 세션에는 없다.

기대 동작:

```text
decide: blocked
reason: valid continuation depends on an external prerequisite that local fixing cannot supply
next action: stop the current run and report the blocker clearly
```

현재 판단:

- v0에서는 `blocked`가 나오면 현재 run을 멈추는 쪽으로 본다.
- 다른 AC로 건너뛰는 multi-lane executor로 보지 않는다.

### Example 6. `scope_drift`

상황:

- current AC: `approval_state != approved` refusal semantics를 고정한다.
- discovered work:
  - refusal 문구를 같은 section에서 조금 더 명확히 다듬는 일
  - planning approval semantics 전체를 다시 설계하는 일

기대 동작:

```text
small wording fix
  -> scope_drift in-bound
  -> absorb into current AC

planning approval redesign
  -> scope_drift out-of-bound
  -> stop and return to $planning
```

현재 판단:

- `scope_drift`는 발견된 일이 있다는 사실만으로 바로 planning 복귀를 뜻하지 않는다.
- 같은 AC를 끝내기 위한 작은 enabling work는 흡수 가능하다.
- boundary-crossing work만 planning으로 되돌린다.

### Example 7. Retry / Escalation

상황:

- current AC: doctor가 missing managed asset을 올바르게 보고한다.
- first retry 후에도 같은 failure
- second retry 후에도 같은 failure
- third retry 후에도 materially new approach 없이 같은 failure

기대 동작:

```text
decide: failed
reason: bounded retry exhausted without a materially new path to success
next action: stop local retry and report whether replanning or external unblock is needed
```

현재 판단:

- local retry는 무한루프가 아니다.
- 같은 실패를 반복하는데 접근 자체가 바뀌지 않았다면 `failed` 또는 replanning으로 넘어가야 한다.
- 반대로 evidence가 plan 자체의 부족함을 보여주면 `failed`보다 `$planning` 복귀가 더 맞을 수 있다.

### Initial State Gap Observation

읽은 구현:

- `runtime/ea_state.py`

관찰 결과:

- 현재 state는 `stage`, `iteration`, `resume_from_stage`, `terminal_reason` 같은 run-level 필드에는 강하다.
- 하지만 `execute` contract가 요구하는 AC-level progress는 아직 담지 않는다.
- 특히 아래 항목은 state에 직접 존재하지 않는다.
  - `current_ac`
  - `completed_acs`
  - `blocked_acs`
  - `failed_verification_acs`
  - `latest_evidence`

현재 판단:

- 이건 즉시 state 스키마를 늘려야 한다는 뜻은 아니다.
- 다만 `M5`가 끝나기 전에는 아래 둘 중 하나를 정해야 한다.

```text
option A
  -> execute progress는 별도 progress artifact로 남긴다

option B
  -> ea_state.py에 AC-level progress 필드를 추가한다
```

- 현재 `ea_state.py`만으로는 `execute` progress contract를 완전히 충족한다고 보기 어렵다.

### Reference Cross-Check

레퍼런스와 비교했을 때 현재 `M5` 방향은 대체로 정당하다.

#### 1. Strong execution entry gate는 레퍼런스에도 있다

- `oh-my-codex`는 `$ralph`가 항상 approved plan을 전제로 둔다.
  - `references/oh-my-codex/README.md`
  - `references/oh-my-codex/skills/ralplan/SKILL.md`
- `oh-my-claudecode`도 consensus approval 이후에만 execution skill로 handoff 한다.
  - `references/oh-my-claudecode/skills/plan/SKILL.md`
- `oh-my-openagent`도 `Prometheus` plan 이후 `/start-work`로 execution을 연다.
  - `references/oh-my-openagent/README.md`
  - `references/oh-my-openagent/docs/guide/orchestration.md`
- `superpowers`도 plan 작성 뒤 execution choice를 열고, spec/review gate를 별도로 둔다.
  - `references/superpowers/skills/writing-plans/SKILL.md`
  - `references/superpowers/docs/testing.md`

즉:

```text
approved / validated plan 없이 execution 진입 금지
```

이건 우리만의 과한 가정이 아니라 공통 패턴에 가깝다.

#### 2. run-level state와 progress ledger를 분리하는 패턴도 실제로 있다

- `oh-my-codex`
  - mode state: `ralph-state.json`
  - progress ledger: `ralph-progress.json`
  - 참조:
    - `references/oh-my-codex/docs/contracts/ralph-state-contract.md`
    - `references/oh-my-codex/skills/ralph-init/SKILL.md`
- `claude-automate`
  - mode state는 `.claude/state/mode`
  - AC progress는 plan file checkbox/status에 남긴다
  - 참조:
    - `references/claude-automate/skills/implement/SKILL.md`
    - `references/claude-automate/skills/planning/refs/plan-file.md`
- `oh-my-claudecode`
  - mode/session state와 별도 plan/handoff/state lifecycle이 분리돼 있다
  - 참조:
    - `references/oh-my-claudecode/docs/HOOKS.md`
    - `references/oh-my-claudecode/skills/plan/SKILL.md`

즉:

```text
run-level state
!=
unit-of-work progress ledger
```

이 분리는 레퍼런스들과도 어긋나지 않는다.

#### 3. 현재 우리 `execute`는 방향은 맞지만 review/verification rigor는 더 약하다

- `superpowers`는 execution 후 spec compliance review와 code quality review를 분리한다.
- `oh-my-claudecode`는 verify/fix loop와 reviewer floor가 더 강하다.
- `oh-my-openagent`는 planner/executor separation과 completion verification이 더 두껍다.

현재 판단:

- `execute` 내부에 `verify`와 `decide`를 포함한 구조 자체는 괜찮다.
- 다만 `M5`에서는 최소한 분기 예시와 summary contract를 더 선명하게 만들어야 한다.

## Expected Outputs

이 단계에서 남겨야 할 산출물:

- `execute` contract의 수정점
- gap list
- example-based validation notes
- runtime support가 더 필요한 부분과 필요하지 않은 부분의 분리

## Out of Scope

- Claude adaptation
- internal service adapter
- team / subagents mode
- browser/reviewer expansion
