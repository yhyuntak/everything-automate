---
title: Everything Automate Codex Execution Model
description: Codex에서는 인세션 skill workflow를 1차 사용자 표면으로 두고, 바깥 runtime/launcher는 그 흐름을 받쳐주는 내부 구현 레이어로 본다.
doc_type: spec
scope:
  - codex
  - workflow
  - planning
  - ralph loop
  - execution model
covers:
  - templates/codex/
  - runtime/ea_state.py
  - docs/specs/everything-automate-runtime-flow.md
  - docs/specs/everything-automate-implementation-milestones.md
---

# Everything Automate Codex Execution Model

## 목적

이 문서는 Codex 기준 `everything-automate`의 실제 운영 모델을 고정한다.

핵심 질문은 이것이다.

- 사용자는 Codex 안에서 어떤 workflow를 밟는가
- `deep-interview`, `ralplan`, `ralph`, `cancel` 같은 표면은 어떻게 보이는가
- 바깥 runtime/launcher는 어디까지가 내부 구현 레이어인가
- handoff와 recovery는 어떤 층에서 처리되는가

핵심 판단은 간단하다.

- Codex의 1차 사용자 경험은 인세션 workflow여야 한다.
- 바깥 runtime/launcher는 사용자가 직접 조작하는 메인 UX가 아니라 내부 구현 레이어에 가깝다.
- 따라서 `v0`에서는 먼저 Codex 안에서의 skill workflow와 handoff 계약을 고정한다.

## 현재 Codex 운영 모델

현재 기준 운영 모델은 다음과 같다.

```text
inside Codex
  -> $deep-interview
  -> $ralplan
  -> $ralph
  -> $cancel

under the hood
  -> handoff artifact
  -> state/runtime preparation
  -> durable execution support
  -> recovery / cancel bookkeeping
```

짧게 말하면:

- 사용자는 안에서 workflow를 밟는다
- 바깥 runtime은 그 workflow를 받쳐주는 구현 레이어다

## 왜 이렇게 나누나

이 분리는 Codex의 현재 제약 때문이다.

### 1. 사용자 경험은 in-session이어야 한다

Codex 세션 안에서는 다음이 자연스럽다.

- 요구사항 명확화
- 계획 수립
- plan artifact 작성
- task와 verification 기준 정리
- Ralph 같은 실행 모드 진입
- 명시적 취소나 상태 확인

즉 day-to-day workflow는 Codex 안에서 skill처럼 느껴져야 한다.

### 2. 하지만 내부적으로는 runtime 보조층이 필요하다

반면 다음 문제는 Codex 안에서만 처리하기 어렵다.

- long-running background lifecycle
- reliable cancel / resume semantics
- session-scoped runtime assembly
- explicit state recovery

그래서 state와 runtime glue는 별도 내부 레이어가 받쳐줘야 한다.
중요한 점은, 이 레이어가 곧바로 사용자 메인 표면일 필요는 없다는 것이다.

## Codex에서 하지 않을 것

`v0`에서는 다음을 기본 모델로 삼지 않는다.

- 사용자에게 바깥 launcher command를 메인 UX처럼 강요하는 구조
- Codex 안에서 다시 Codex를 깊게 중첩해서 돌리는 구조
- Codex native background session을 신뢰하는 구조
- `AGENTS.md`만으로 cancel / resume lifecycle까지 해결하려는 구조

즉 사용자에게 보이는 것은 인세션 skill workflow이고,
runtime control은 내부 구현 레이어가 맡는 모델을 기본으로 둔다.

## Handoff Model

planning이 끝나면 실행으로 넘어가기 전에 handoff artifact가 필요하다.

최소 handoff에는 다음이 들어간다.

- `task_id`
- `plan_path`
- execution intent
- provider = `codex`
- desired mode
  - `start`
  - `ralph`

흐름은 다음과 같다.

```text
in-session workflow
  -> approved plan
  -> execution mode chosen
  -> handoff metadata fixed
  -> internal runtime path starts
```

## In-Session Workflow Surface

`v0`에서 먼저 고정해야 할 표면은 바깥 command가 아니라 인세션 workflow다.

- `$deep-interview`
- `$ralplan`
- `$ralph`
- `$cancel`

각 surface의 역할:

- `deep-interview`
  요구사항과 경계를 명확히 한다.
- `ralplan`
  실행 가능한 plan artifact를 만든다.
- `ralph`
  approved plan을 completion loop로 넘긴다.
- `cancel`
  active execution intent를 중단한다.

이 문서 기준으로는 이것이 1차 UX다.

## Internal Runtime Responsibilities

바깥 runtime/launcher는 다음 일을 맡는다.

```text
1. task handoff metadata 읽기
2. runtime state root 준비
3. instructions / guidance assembly
4. ea_state.py 호출
5. Codex launch or wrapped execution
6. status / cancel / resume surfaces 제공
```

중요:

- 이 레이어는 planning을 대신하지 않는다.
- 이 레이어는 사용자가 직접 주로 다루는 command surface일 필요가 없다.
- 이 레이어의 역할은 loop runtime과 recovery를 안정화하는 것이다.

## Runtime Assembly

Codex 쪽 runtime assembly는 다음 세 요소로 본다.

- top-level `AGENTS.md`
- session-scoped runtime instructions
- file-based loop state

즉 Codex는 풍부한 hook보다,
instructions assembly와 state file을 더 강하게 활용하는 쪽으로 설계한다.

## Runtime Flow 연결

Codex 기준으로 `M2`의 공통 흐름은 다음처럼 현실화된다.

```text
inside Codex
  -> clarify / plan / ralph / cancel

under the hood
  -> handoff
  -> bootstrap/runtime preparation
  -> execute
  -> verify
  -> decide
  -> wrap
```

여기서 중요한 점:

- planning은 여전히 커널의 일부다
- Ralph 같은 execution intent도 사용자에게는 인세션 workflow로 보여야 한다
- 그 아래에서 handoff와 runtime preparation이 분리될 수 있다
- 이 분리는 provider-specific realization이지, 커널 의미 변경은 아니다

## Claude와의 관계

이 문서는 Claude 의미를 버리자는 문서가 아니다.

정확한 관계는 다음과 같다.

```text
semantic richness reference
  -> Claude Code

practical v0 implementation path
  -> Codex execution model first
```

즉 Claude는 더 풍부한 reference surface를 제공하지만,
현재 구현 순서는 Codex 인세션 workflow를 먼저 굳히는 쪽으로 간다.

## 마일스톤 영향

이 운영 모델을 받아들이면 다음이 바뀐다.

- `M4`는 Codex 인세션 workflow와 handoff contract 정의가 된다
- `M5`는 그 workflow를 받쳐주는 internal runtime / recovery path 구현이 된다
- Claude는 그 다음 단계에서 같은 의미를 richer surface에 맞게 적응한다

## 한 줄 결론

`v0`의 Codex 모델은 이것이다.

```text
primary UX inside Codex
  -> runtime support underneath
```

이 기준을 먼저 고정해야 인세션 workflow, handoff, runtime 보조층의 역할이 서로 섞이지 않는다.
