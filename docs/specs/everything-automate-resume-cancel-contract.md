---
title: Everything Automate Resume and Cancel Contract
description: M4 단계에서 중단 후 재개와 명시적 취소를 안전하게 처리하기 위한 공통 계약을 정의한다.
doc_type: spec
scope:
  - m4
  - resume
  - cancel
  - loop state
  - recovery
covers:
  - docs/specs/everything-automate-loop-state-contract.md
  - docs/specs/everything-automate-stage-transition-contract.md
  - docs/specs/everything-automate-runtime-flow.md
  - docs/specs/everything-automate-provider-entry-bootstrap-mapping.md
---

# Everything Automate Resume and Cancel Contract

## 목적

이 문서는 `M4`에서 다음 질문에 답한다.

- 중간에 멈춘 작업은 무엇을 근거로 다시 이어지는가
- 사용자가 멈추라고 했을 때 어떤 상태로 끝나는가
- `failed`와 `cancelled`는 어떻게 다르게 기록되는가
- 진행 중이던 evidence와 산출물은 무엇을 남기고 무엇을 정리하는가

핵심 판단은 이거다.

- `resume`은 편의 기능이 아니라 loop 연속성 계약이다.
- `cancel`은 실패의 별칭이 아니라 명시적 terminal state다.

## 현재 구현 기준

`M4`의 공통 계약은 provider-neutral하게 유지한다.

Claude Code는 richer reference surface를 제공하지만,
현재 작업 환경과 구현 속도를 고려하면 실제 구현 순서는 Codex 쪽을 먼저 보는 것이 더 현실적이다.

따라서 현재 문서는:

- 상태 의미는 provider-neutral하게 유지
- Claude 탐색 결과는 문서로 보존
- 실제 다음 구현은 Codex path를 먼저 본다
- Codex에서는 인세션 workflow를 1차 UX로 두고, runtime support 레이어가 그 아래를 받친다

라는 전제를 둔다.

## 범위

이 문서가 다루는 것:

- resume eligibility
- cancel semantics
- terminal reason 구분
- partial artifact preservation
- re-entry rules

이 문서가 아직 다루지 않는 것:

- provider별 resume 구현 코드
- background team runtime 복구
- subagent tree 복원

## 핵심 원칙

### 1. resume는 같은 task를 이어가는 것이다

resume는 새 run을 시작하는 것이 아니라,
기존 task/run의 상태를 읽고 같은 execution intent를 이어가는 것이다.

### 2. cancel은 명시적 종료다

`cancelled`는 `failed`와 다르다.

- `failed`: 완료를 시도했지만 종료 조건상 실패
- `cancelled`: 사용자가 의도적으로 중단

### 3. evidence는 가능한 한 버리지 않는다

중간에 실패했거나 취소됐더라도, 이미 수집된 evidence는 후속 판단 가치가 있으면 남긴다.

### 4. resume는 불명확한 상태에서 시작하지 않는다

resume를 하려면 최소한 아래가 식별 가능해야 한다.

- 어떤 task인지
- 어떤 plan을 따르는지
- 마지막 안정 stage가 무엇이었는지
- 마지막 evidence가 무엇인지

### 5. wrapping 없이 complete는 없다

resume/cancel이 들어와도 이 원칙은 그대로다.

- `complete`는 `wrapping` 이후에만 가능
- `cancelled`는 wrap 없이도 terminal state가 될 수 있다
- 하지만 cancel summary는 남겨야 한다

## Resume Eligibility

resume가 가능한 최소 조건:

```text
1. task_id가 존재
2. run_id 또는 last_active_run 식별 가능
3. plan_path가 존재
4. 마지막 stage가 terminal이 아님
5. 상태 파일이 손상되지 않았음
```

resume를 막아야 하는 경우:

```text
- state file corrupted
- plan artifact missing
- terminal state already reached
- superseded run exists
```

## Resume State Model

resume를 위해 loop-state에 필요한 최소 추가 의미는 다음과 같다.

- `last_stable_stage`
- `resume_from_stage`
- `suspended_at`
- `resume_count`
- `superseded_by`

`v0`에서는 기존 loop-state에 별도 필드를 전부 추가하지 않아도 된다.
하지만 최소한 이 의미는 표현 가능해야 한다.

## Resume Rules

### 1. stage별 resume 원칙

| 마지막 상태 | resume 동작 |
| --- | --- |
| `planning` | plan을 다시 읽고 planning부터 재진입 |
| `committed` | 실행 전 잠금 상태 확인 후 `executing` 진입 |
| `executing` | 실행 결과가 불명확하면 `verifying` 또는 `executing` 재진입 |
| `verifying` | verification을 다시 수행 |
| `fixing` | fixing 원인을 읽고 `executing` 재진입 |
| `wrapping` | wrap을 다시 수행하거나 terminal summary 재생성 |

### 2. resume는 보수적으로 한다

모호하면 이전 진행을 낙관적으로 이어가지 않는다.

예:

- `executing` 중 중단됐지만 실제 변경 반영 여부가 불명확함
- 이 경우 "끝났을 것"이라고 가정하지 않고 verify부터 다시 들어간다

### 3. resume는 superseded run을 만들 수 있다

같은 task를 새 방향으로 다시 시작해야 하면:

- 기존 run은 `superseded`
- 새 run은 새로운 `run_id`
- task linkage는 유지

## Cancel Contract

cancel은 아래를 명확히 기록해야 한다.

- 누가 취소했는지
- 언제 취소했는지
- 어떤 task/run을 취소했는지
- 이미 남겨진 evidence와 artifact를 어떻게 다뤘는지

최소 결과:

```text
stage = cancelled
terminal_reason = cancelled
```

추가로 남길 것:

- cancel summary
- last stable stage
- preserved artifacts 목록

## Cancel Rules

### 1. cancel은 가능한 빨리 terminalize한다

사용자 취소가 들어오면:

- 새 작업을 시작하지 않는다
- 남은 loop를 억지로 마치지 않는다
- 현재 상태를 정리하고 `cancelled`로 종료한다

### 2. cancel은 evidence를 지우지 않는다

이미 수집된 evidence는 기본적으로 남긴다.

예외:

- 민감 정보
- 임시 캐시
- provider-specific disposable runtime state

### 3. cancel은 실패로 바꾸지 않는다

사용자가 멈췄다는 사실을 숨기기 위해 `failed`로 기록하면 안 된다.

### 4. cancel 이후 resume 정책은 명시적이어야 한다

기본 규칙:

- `cancelled` run은 자동 resume 대상이 아니다
- 사용자가 명시적으로 다시 시작해야 한다

## Artifact Preservation

`M4` 기준 기본 보존 정책:

보존:

- plan artifact
- evidence records
- final known loop-state
- cancel or failure summary

정리 가능:

- transient bootstrap cache
- provider-specific temporary session glue
- disposable hook scratch files

원칙:

- 판단 근거는 남긴다
- 재생성 가능한 임시물은 정리할 수 있다

## Resume vs Cancel vs Fail

```text
interrupted but recoverable
  -> suspended / resumable

explicit user stop
  -> cancelled

loop exhausted or unrecoverable
  -> failed
```

핵심 차이:

- `resume`은 상태
- `cancelled`와 `failed`는 terminal outcome

## Claude 기준선과 Codex 적응 메모

### Claude Code

- hook/runtime 기반 중단 정보를 이용하기 쉽다
- cancel은 hook/command surface와 연결될 가능성이 높다
- resume는 hook state + template state를 함께 읽는 방향이 자연스럽다

### Codex CLI

- `AGENTS.md`와 인세션 workflow surface가 중심이 된다
- resume는 local state 파일과 plan/evidence 파일을 읽는 방식이 자연스럽다
- Claude처럼 풍부한 hook surface를 전제하지 않는다
- runtime helper는 상태와 recovery를 받치는 내부 레이어로 두는 편이 자연스럽다

이 차이 때문에 현재는 Codex 인세션 workflow를 먼저 고정하고,
그 다음 단계에서 recovery/runtime 보조층을 붙이는 순서가 맞다.

## M4 산출물

이 단계에서 최소로 남겨야 할 것:

- resume/cancel contract 문서
- 상태 복구 조건
- terminal reason 구분 규칙
- artifact preservation 규칙

이 단계가 끝나면 다음 구현은 더 구체화될 수 있다.

- cancel 기록 파일
- resume lookup 방식
- provider별 state adapter

## 핵심 결론

`M4`의 목적은 단순히 "다시 시작할 수 있게 한다"가 아니다.

정확한 목적은 이거다.

```text
do not lose loop meaning across interruption
do not confuse cancel with fail
do not lose evidence needed for later judgment
```

즉 `M4`는 persistence의 품질을 올리는 단계다.
