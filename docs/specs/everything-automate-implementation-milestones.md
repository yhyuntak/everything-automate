---
title: Everything Automate Implementation Milestones
description: everything-automate 루프 커널을 v0 계약부터 어댑터 확장까지 순차적으로 구현하기 위한 단계별 마일스톤을 정의한다.
doc_type: workflow
scope:
  - implementation milestones
  - v0 kernel
  - execution flow
  - bootstrap
  - adapters
covers:
  - docs/specs/everything-automate-loop-kernel-draft.md
  - docs/specs/everything-automate-operating-principles.md
---

# Everything Automate 구현 마일스톤

이 문서는 `everything-automate`의 구현 경로를 한 단계씩 나누어 정의한다.
핵심 원칙은 간단하다.

- 한 번에 한 단계만 진행한다.
- 다음 단계는 이전 단계의 계약과 검증이 끝나야 시작한다.
- 초기는 반드시 `v0` 루프 커널 계약부터 고정하고, 그 다음에 실행 흐름과 주변 런타임 기능을 넓힌다.

## 진행 원칙

### 순서 규칙

```text
v0 kernel contracts
  -> execution flow
  -> minimal bootstrap/intake
  -> Codex in-session workflow
  -> Codex runtime and recovery
  -> Claude adaptation
  -> wider adapters
  -> later expansion
```

### 단계 완료 기준

- 각 단계는 동작하는 산출물을 하나 이상 남겨야 한다.
- 각 단계는 완료 조건이 명확해야 한다.
- 각 단계는 다음 단계로 넘어가기 전에 검증 가능해야 한다.

## 마일스톤

### M0. 범위 고정과 기준선 정리

목적: 구현 전에 문서와 범위를 고정한다.

- `everything-automate-loop-kernel-draft.md`를 기준 설계로 삼는다.
- 이 문서와 운영 원칙 문서를 현재 기준으로 만든다.
- 로컬 authoring layer와 distributable template layer를 분리한다.
- 로컬 운영 원칙은 루트 `AGENTS.md`가 담당하고, 배포 대상 런타임 자산은 앞으로 `templates/`를 source of truth로 삼는다는 규칙을 고정한다.
- `v0`에서 다루지 않을 범위를 분명히 적는다.

완료 조건:

- 구현 범위가 `v0`와 이후 확장으로 나뉜다.
- 새 기능을 추가하기 전에 지켜야 할 문서 기준이 정리된다.
- 어떤 파일이 로컬 전용이고 어떤 파일이 배포 대상인지 소유권 규칙이 정리된다.

### M1. v0 루프 커널 계약 고정

목적: 실행 흐름보다 먼저, 상태와 계약을 정의한다.

이 단계에서 고정할 것:

- `loop-state`의 최소 필드
- `plan-artifact`의 최소 구조
- `verification`의 최소 evidence 구조
- `decision-engine`의 상태 전이 규칙
- `cancel`의 종료 의미

완료 조건:

- task 단위 상태가 하나의 계약으로 표현된다.
- 계획, 검증, 결정이 같은 상태 모델을 공유한다.
- 아직 어댑터나 고급 런타임이 없어도 계약을 읽을 수 있다.

### M2. 실행 흐름 연결

목적: 계약을 실제 순서로 움직이게 만든다.

이 단계에서 연결할 것:

- `plan -> execute -> verify -> decide` inner loop
- `bootstrap -> intake -> ... -> wrap` outer flow
- 상태 전이와 검증 결과 반영

완료 조건:

- 실행 흐름이 상태 전이로 설명된다.
- 검증 결과에 따라 `continue`, `fix`, `complete`, `cancel`, `fail` 판단이 가능하다.
- 흐름이 문서가 아니라 실제 런타임 행위로 연결된다.

### M3. 최소 bootstrap / intake

목적: 작업을 시작하기 전에 최소한의 런타임 진입점을 만든다.

이 단계에서 다룰 것:

- 런타임 규칙 주입
- 작업 분류: 직접 실행, 확인 필요, 계획 필요
- task id와 실행 의도 기록
- 템플릿 레이어에서 provider별 진입 파일이 어떤 공통 계약을 읽는지 결정

완료 조건:

- 새 작업이 들어오면 처리 경로가 분류된다.
- 런타임이 어떤 계약을 사용할지 최소한으로 결정할 수 있다.
- 로컬 개발용 규칙과 배포용 진입 파일이 서로 역할을 침범하지 않는다.

### M4. Codex 인세션 workflow와 handoff

목적: Codex 사용자가 세션 안에서 밟는 canonical workflow를 먼저 고정한다.

이 단계에서 구현할 것:

- `$deep-interview`, `$ralplan`, `$ralph`, `$cancel` 같은 primary surface 정의
- planning에서 execution으로 넘어가는 handoff contract
- plan artifact에서 execution intent를 읽는 방식
- 인세션 workflow와 shared kernel의 연결 규칙

완료 조건:

- Codex의 1차 사용자 경험이 인세션 workflow로 설명된다.
- approved plan이 execution handoff로 자연스럽게 이어진다.
- `$ralph`와 `$cancel`이 어떤 의미를 가지는지 contract로 분명하다.
- 바깥 runtime은 메인 UX가 아니라 내부 구현 레이어로 위치가 정리된다.

### M5. Codex runtime과 recovery path

목적: `M4`에서 정한 인세션 workflow를 실제 state/runtime으로 받쳐준다.

이 단계에서 다룰 것:

- internal launcher/runtime glue
- handoff artifact 소비 방식
- session-scoped instructions 준비
- `runtime/ea_state.py`와 Codex runtime 연결
- Codex 기준 status / cancel / resume recovery

완료 조건:

- 인세션 workflow가 internal runtime과 연결된다.
- `cancelled`와 `failed`가 Codex path에서도 분리된다.
- resume / cancel이 file-based state 계약과 충돌하지 않는다.
- runtime primitive가 UX 레이어를 대체하지 않는다.

### M6. Claude adaptation

목적: Codex에서 먼저 굳힌 shared semantics를 Claude richer surface에 맞게 연결한다.

이 단계에서 다룰 것:

- Claude hook / subagent surface 재검토
- task metadata 전달 방식 확정
- Claude template와 shared runtime state 연결
- Codex와 다른 Claude lifecycle advantage를 별도 표면으로 격리

완료 조건:

- Claude path가 shared kernel 의미를 유지한 채 richer surface를 사용한다.
- Claude 전용 편의 기능이 core state 계약을 바꾸지 않는다.
- pause된 Claude 탐색이 실제 adapter 설계로 연결된다.

### M7. wider adapters

목적: Claude와 Codex 이후 다른 provider를 붙인다.

이 단계에서 추가할 것:

- OpenCode adapter
- internal runtime adapter
- provider별 bootstrap 차이
- tool mapping overlay

완료 조건:

- 새 provider가 붙어도 shared kernel 의미는 유지된다.
- provider 차이는 adapter 경계 바깥에 머문다.
- Codex와 Claude에서 정한 공통 상태 계약이 재사용된다.

### M8. later expansion

목적: 안정화된 커널 위에 확장 기능을 순차적으로 올린다.

이 단계에서 검토할 것:

- `subagents` 실행 모드
- `team` 런타임
- browser/reviewer evidence
- run history와 경량 메모리

완료 조건:

- 확장 기능이 커널 계약을 침범하지 않는다.
- 각 확장은 독립적으로 켜고 끌 수 있다.
- 새 기능이 들어와도 `v0`의 의미가 흐려지지 않는다.

## 단계 의존성

```text
M1 계약 고정
  -> M2 실행 흐름
  -> M3 최소 bootstrap/intake
  -> M4 Codex 인세션 workflow와 handoff
  -> M5 Codex runtime과 recovery path
  -> M6 Claude adaptation
  -> M7 wider adapters
  -> M8 later expansion
```

이 순서를 바꾸지 않는다.
특히 `adapter`, `team`, `subagents` 같은 기능은 `v0` 계약이 안정되기 전에는 앞당기지 않는다.

## 단계별 산출물

- `M1`
  상태 계약 문서, plan/evidence 스키마, 결정 규칙
- `M2`
  상태 전이표, inner loop 흐름, outer flow 연결
- `M3`
  최소 진입점, 작업 분류 규칙, 실행 의도 기록, 템플릿 진입 규칙
- `M4`
  Codex in-session workflow, handoff contract, execution intent 규칙
- `M5`
  Codex internal runtime glue, recovery path, state 연결
- `M6`
  Claude hook/subagent adaptation, task metadata path, template 연결
- `M7`
  OpenCode/internal adapters, provider bootstrap overlay
- `M8`
  확장 기능 선택지와 활성화 조건

## 구현 판단

이 프로젝트는 처음부터 큰 런타임을 만들기보다, 먼저 커널을 작게 고정하는 쪽이 맞다.

따라서 실제 구현 우선순위는 다음과 같다.

1. 상태 계약을 고정한다.
2. 실행 흐름을 연결한다.
3. 최소 진입점을 만든다.
4. Codex 인세션 workflow를 먼저 굳힌다.
5. 그 workflow를 받쳐주는 runtime과 recovery를 붙인다.
6. 그 다음 Claude adaptation을 붙인다.
7. 이후 다른 provider adapter를 붙인다.
8. 마지막에 확장을 넓힌다.
