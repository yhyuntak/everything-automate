---
title: Everything Automate Loop State Contract
description: everything-automate v0 루프 커널이 공유하는 task-scoped 상태 모델과 필수 필드를 정의한다.
doc_type: spec
scope:
  - loop state
  - state contract
  - v0 kernel
covers:
  - docs/specs/everything-automate-loop-kernel-draft.md
  - docs/specs/everything-automate-implementation-milestones.md
---

# Everything Automate Loop State Contract

## 목적

이 문서는 `everything-automate`의 모든 실행 흐름이 공통으로 사용하는 `loop-state` 계약을 정의한다.

이 계약의 목적은 다음과 같다.

- 하나의 작업이 지금 어떤 상태인지 항상 알 수 있게 한다.
- `plan`, `execute`, `verify`, `decide`가 같은 상태 모델을 공유하게 한다.
- 중단, 재개, 취소, 완료를 모두 명시적 상태로 기록하게 한다.

`v0`에서는 하나의 작업이 하나의 `loop-state`를 가진다.

## 기본 원칙

- 상태는 반드시 `task-scoped`여야 한다.
- 상태는 사람이 읽을 수 있어야 한다.
- 상태는 런타임이 판단에 사용할 수 있을 만큼 구조화되어야 한다.
- 상태는 채팅 맥락이 아니라 파일 또는 동등한 저장 매체에 남아야 한다.

## v0 최소 필드

```yaml
run_id: string
task_id: string
provider: claude-code | opencode | codex | internal
stage: bootstrap | intake | planning | committed | executing | verifying | fixing | wrapping | complete | cancelled | failed
execution_mode: single_owner
plan_path: string | null
owner_id: string | null
iteration: number
max_iterations: number
started_at: string
updated_at: string
completed_at: string | null
terminal_reason: complete | cancelled | failed | max_iterations | superseded | null
current_phase_summary: string
verification_policy: string
```

## 필드 정의

### 식별자

- `run_id`
  한 번의 실행 인스턴스를 식별한다.
- `task_id`
  사용자의 작업 자체를 식별한다.
  같은 작업을 다시 이어서 할 수 있으므로 `run_id`와 분리한다.

### 실행 환경

- `provider`
  현재 런타임이 어떤 provider 위에서 동작하는지 기록한다.
- `execution_mode`
  `v0`에서는 `single_owner`만 허용한다.
  `team`, `subagents`는 이후 확장 단계에서만 추가한다.

### 진행 상태

- `stage`
  현재 어디에 있는지 나타내는 단일 진실원천이다.
- `iteration`
  `execute -> verify -> decide -> fixing` 반복 횟수를 센다.
- `max_iterations`
  무한 루프를 방지하는 상한이다.
- `current_phase_summary`
  사람이 빠르게 이해할 수 있도록 현재 작업 상황을 한두 문장으로 요약한다.

### 연결 정보

- `plan_path`
  현재 실행이 의존하는 plan artifact 경로다.
  `plan`이 아직 없는 초기 상태에서는 `null`일 수 있다.
- `owner_id`
  현재 실행 owner를 식별한다.
  `v0`에서는 단일 owner만 가진다.

### 시간 정보

- `started_at`
  이 실행이 시작된 시각이다.
- `updated_at`
  상태가 마지막으로 변경된 시각이다.
- `completed_at`
  `complete`, `cancelled`, `failed` 같은 terminal state에서만 채운다.

### 종료 정보

- `terminal_reason`
  terminal stage가 된 이유를 기록한다.
  non-terminal stage에서는 반드시 `null`이어야 한다.
- `verification_policy`
  어떤 종류의 검증이 요구되는지 요약한다.
  예: `test-command required`, `review + test required`

## 상태 규칙

### non-terminal stage

다음 stage는 non-terminal이다.

- `bootstrap`
- `intake`
- `planning`
- `committed`
- `executing`
- `verifying`
- `fixing`
- `wrapping`

규칙:

- `completed_at`는 `null`
- `terminal_reason`는 `null`

### terminal stage

다음 stage는 terminal이다.

- `complete`
- `cancelled`
- `failed`

규칙:

- `completed_at`는 반드시 있어야 한다.
- `terminal_reason`는 반드시 있어야 한다.
- terminal 이후에는 `stage`를 다시 non-terminal로 되돌리지 않는다.
  재실행은 새 `run_id`로 시작한다.

## v0 기본값

새 상태를 만들 때 기본값은 다음과 같다.

```yaml
stage: bootstrap
execution_mode: single_owner
plan_path: null
owner_id: null
iteration: 0
max_iterations: 10
completed_at: null
terminal_reason: null
current_phase_summary: ""
verification_policy: "unspecified"
```

## 금지 규칙

- `complete`인데 `terminal_reason`가 없는 상태
- `cancelled`인데 `completed_at`가 없는 상태
- `failed`인데 왜 실패했는지 설명이 없는 상태
- `iteration > max_iterations`인데 non-terminal로 계속 남아 있는 상태
- `plan_path`가 필요한 stage인데도 계속 `null`인 상태

## 구현 판단

`claude-automate`의 단일 `mode` 문자열은 너무 작다.
`everything-automate`는 처음부터 이 정도 수준의 구조화된 상태를 가져야 한다.

다만 `v0`에서는 과하게 복잡하게 만들지 않는다.

- task 하나
- owner 하나
- mode 하나
- 상태 파일 하나

이 최소 단위를 먼저 고정한다.
