---
title: Everything Automate Stage Transition Contract
description: everything-automate v0 루프 커널의 stage 전이 규칙과 decide 단계의 판단 계약을 정의한다.
doc_type: spec
scope:
  - stage transition
  - decision engine
  - v0 kernel
covers:
  - docs/specs/everything-automate-loop-kernel-draft.md
  - docs/specs/everything-automate-loop-state-contract.md
  - docs/specs/everything-automate-plan-artifact-contract.md
  - docs/specs/everything-automate-evidence-contract.md
---

# Everything Automate Stage Transition Contract

## 목적

이 문서는 `everything-automate`의 `stage`가 언제 어떻게 바뀌는지 정의한다.

핵심은 다음 두 가지다.

- stage 전이는 명시적으로만 일어난다.
- `decide`는 항상 다음 행동을 고른다.
  멈춘 척하고 부분 완료로 남아 있지 않는다.

## v0 stage 목록

```text
bootstrap
intake
planning
committed
executing
verifying
fixing
wrapping
complete
cancelled
failed
```

## 기본 전이표

| 현재 stage | 허용되는 다음 stage | 의미 |
| --- | --- | --- |
| `bootstrap` | `intake`, `failed` | 런타임 준비 후 작업 접수로 이동 |
| `intake` | `planning`, `committed`, `cancelled`, `failed` | 계획 필요 여부를 판단 |
| `planning` | `committed`, `cancelled`, `failed` | 실행 가능한 계획을 만든다 |
| `committed` | `executing`, `cancelled`, `failed` | 실행 계약을 잠근다 |
| `executing` | `verifying`, `fixing`, `cancelled`, `failed` | 작업 수행 후 검증으로 가거나 바로 수정으로 들어갈 수 있다 |
| `verifying` | `decide`, `fixing`, `cancelled`, `failed` | evidence를 평가한다 |
| `fixing` | `executing`, `cancelled`, `failed` | 실패 원인을 보완하고 다시 실행한다 |
| `wrapping` | `complete`, `failed` | 종료 정리 후 완료 또는 종료 실패 |
| `complete` | 없음 | terminal |
| `cancelled` | 없음 | terminal |
| `failed` | 없음 | terminal |

## decide 단계의 의미

`decide`는 실제 저장 stage가 아니라 판단 엔진의 역할로 본다.

즉 흐름은 이렇게 이해한다.

```text
execute -> verify -> decide
```

그리고 `decide` 결과는 다음 중 하나다.

- `fixing`
- `wrapping`
- `cancelled`
- `failed`

`complete`는 `wrapping` 이후에만 간다.

## v0 판단 규칙

### 1. `continue as fixing`

다음 경우 `fixing`으로 간다.

- evidence가 `fail`
- required evidence가 부족함
- plan의 AC가 아직 모두 충족되지 않음
- reviewer/manual verification이 아직 끝나지 않음

이 경우:

- `iteration`을 1 증가시킨다.
- `current_phase_summary`에 왜 fixing으로 갔는지 남긴다.

### 2. `continue as execute`

`fixing`에서 수정이 끝나면 다시 `executing`으로 간다.

### 3. `wrap`

다음 조건이 모두 맞으면 `wrapping`으로 간다.

- plan의 AC가 모두 충족됨
- required evidence가 모두 `pass`
- terminal blocker가 없음
- user-confirm-required 정책이 있다면 그 조건도 충족됨

### 4. `cancel`

명시적 사용자 취소 또는 시스템 취소 규칙이 발동하면 `cancelled`로 간다.

이 경우:

- `terminal_reason = cancelled`
- `completed_at`를 기록
- 이후 재개는 새 `run_id`로만 한다

### 5. `fail`

다음 경우 `failed`로 간다.

- bootstrap/intake/planning 자체가 진행 불가
- `iteration >= max_iterations`이고 더 진행할 합리적 근거가 없음
- 필수 plan/evidence/state가 깨져서 안전하게 진행할 수 없음

이 경우:

- `terminal_reason = failed` 또는 `max_iterations`
- 실패 원인을 `current_phase_summary`에 남긴다

## v0 상세 규칙

### bootstrap

- 성공하면 `intake`
- provider 감지나 필수 초기화에 실패하면 `failed`

### intake

- 바로 실행 가능한 요청이면 `committed`
- 계획이 필요한 요청이면 `planning`
- 사용자 취소면 `cancelled`

### planning

- usable plan artifact가 만들어지면 `committed`
- 질문 미해결 또는 외부 결정 대기면 `failed` 또는 이후 확장에서는 `blocked` 후보

### committed

- owner, plan_path, verification_policy가 정해지면 `executing`

### executing

- 작업이 끝나면 `verifying`
- 중간 실패가 분명하면 `fixing`

### verifying

- pass면 `wrapping`
- fail 또는 insufficient evidence면 `fixing`

### wrapping

- 정리 성공 시 `complete`
- 정리 단계 실패 시 `failed`

## 금지 전이

- `bootstrap -> executing`
- `intake -> complete`
- `planning -> complete`
- `executing -> complete`
- `verifying -> complete`
- terminal stage에서 다른 stage로 이동

이 금지 전이를 막는 이유는, 완료 전에 반드시 `wrap`과 terminalization을 거치게 하기 위해서다.

## 구현 판단

`v0`에서는 전이 규칙을 단순하게 유지한다.

- `blocked` 같은 중간 상태는 나중에 추가할 수 있다.
- `decide`는 일단 별도 저장 stage가 아니라 규칙 엔진 역할로 둔다.
- `complete`는 반드시 `wrapping` 뒤에만 나온다.

이 단순함이 중요한 이유는, 처음부터 너무 많은 상태를 넣으면 provider adapter보다 먼저 상태 모델이 흔들리기 때문이다.
