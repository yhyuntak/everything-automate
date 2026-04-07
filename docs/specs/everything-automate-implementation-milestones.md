---
title: Everything Automate Implementation Milestones
description: everything-automate를 내가 이해하고 실제로 쓸 수 있는 흐름으로 다시 세우기 위한 단계별 마일스톤 문서.
doc_type: workflow
scope:
  - implementation milestones
  - user-facing flow
  - codex
  - brainstorming
  - planning
  - execute
  - qa
covers:
  - docs/specs/everything-automate-operating-principles.md
  - docs/specs/everything-automate-planning-workflow.md
  - docs/specs/everything-automate-codex-execute-hardening.md
---

# Everything Automate 구현 마일스톤

이 문서는 `everything-automate`를 다시 단순하게 잡기 위한 현재 기준 문서다.

이번 재정리의 핵심은 이것이다.

- 남의 Ralph loop를 닮았는지가 기준이 아니다.
- 내가 이해할 수 있고 실제로 쓰고 싶은 흐름이 기준이다.
- 먼저 사용자 플로우를 고정한다.
- state, progress, installer 같은 것은 뒤의 숨겨진 지원층으로 둔다.

## 가장 중요한 흐름

현재 기준의 메인 플로우는 이것이다.

```text
$brainstorming
  -> $planning
  -> $execute
  -> $qa
  -> commit
```

각 단계의 뜻은 단순하다.

- `$brainstorming`
  아이디어를 작업 가능한 방향으로 좁힌다.
- `$planning`
  파일 기반 plan을 만든다.
- `$execute`
  AC 단위로 구현하고, 가능한 경우 테스트를 먼저 쓰고 검증하며 진행한다.
- `$qa`
  plan대로 잘 되었는지, 코드 품질과 위험은 괜찮은지, commit해도 되는지 다시 본다.
- `commit`
  최종 검증이 끝난 뒤 남긴다.

## 숨겨진 지원층

아래 요소들은 필요하지만 메인 플로우의 중심은 아니다.

```text
hidden support
  -> state
  -> progress
  -> recovery
  -> installer
```

이것들은 사용자가 먼저 이해해야 할 대상이 아니다.
메인 플로우를 돕는 내부 지원층이다.

## 진행 원칙

### 1. 사용자 플로우를 먼저 고정한다

구현보다 먼저, 사람이 어떻게 쓰는지부터 분명해야 한다.

### 2. 쉬운 말로 쓴다

어려운 말은 줄인다.
중학생이 읽어도 흐름을 따라갈 수 있어야 한다.

### 3. 테스트는 뒤가 아니라 실행의 중심이다

`$execute`는 "코드 먼저 짜고 나중에 테스트"를 기본으로 하지 않는다.
프로젝트 성격에 따라 다르지만, 가능한 경우 테스트를 먼저 쓰는 쪽을 기본으로 본다.

### 4. 단계 이름보다 단계 안의 행동이 더 중요하다

`brainstorming`, `planning`, `execute`, `qa`라는 이름만 있는 것은 부족하다.
각 단계에서 실제로 무엇을 하는지가 보여야 한다.

### 5. state와 runtime은 나중에 붙인다

state와 runtime support는 필요하지만, 그것이 메인 플로우를 설명하는 자리를 차지하면 안 된다.

## 현재 상태

현재 구현 상태는 이렇게 본다.

```text
M0 완료
M1 다음 작업
그 뒤 단계는 아직 재설계 대상
```

이미 있는 것:

- Codex global installer v0
- `brainstorming`, `planning`, `execute` skill 초안
- state/progress helper 초안

하지만 이것들은 아직 최종 구조가 아니다.
지금부터는 **마일스톤 자체를 다시 잡고, 각 skill을 위에서부터 다시 설계**한다.

## 마일스톤

### M0. 리셋과 기준선 고정

목적: 무엇을 만들고 싶은지 다시 고정한다.

이 단계에서 하는 일:

- 메인 플로우를 `brainstorming -> planning -> execute -> qa -> commit`으로 고정
- state/runtime/installer를 숨겨진 지원층으로 내림
- 쉬운 영어와 쉬운 설명을 기본 원칙으로 고정
- 이 저장소에서 지금 하지 않을 것을 분명히 적음

완료 조건:

- 메인 플로우가 한 장으로 설명된다.
- 각 단계의 큰 목적이 분명하다.
- 내부 지원층이 메인 UX를 밀어내지 않는다.

### M1. `$brainstorming` 재설계

목적: 아이디어를 내가 이해할 수 있는 말로 정리하고, 다음 단계로 넘길 수 있는 짧은 brief를 만든다.

이 단계에서 하는 일:

- 왜 이 작업을 하고 싶은지 먼저 묻는 흐름 정리
- 아이디어, backlog item, feature request를 작업 방향으로 좁히는 규칙 정리
- 너무 빠르게 구현이나 상세 설계로 내려가지 않게 경계 정리
- output brief 형식 재정의
- 언제 멈추고, 언제 `$planning`으로 넘기는지 기준 정리

완료 조건:

- `$brainstorming`의 질문 순서와 종료 기준이 단순하게 설명된다.
- output brief가 다음 단계로 넘기기 충분하다.
- 사용자가 "왜 이 방향을 추천받았는지" 이해할 수 있다.

### M2. `$planning` 재설계

목적: brief를 plan 파일로 바꾸고, 구현 전에 test strategy까지 같이 고정한다.

이 단계에서 하는 일:

- plan 파일 구조를 다시 정의
- AC를 더 읽기 쉽게 정리
- test strategy를 planning의 필수 항목으로 올림
- 프로젝트 종류에 따라 어떤 테스트가 맞는지 정하는 규칙 정리
  - no-test change
  - unit-first
  - integration-first
  - service verification
  - web E2E
- handoff를 `$execute`가 이해하기 쉽게 단순화

완료 조건:

- `$planning` 결과가 plan 파일로 남는다.
- AC와 test strategy가 plan 안에 같이 있다.
- `$execute`가 읽어야 할 입력이 단순하고 분명하다.

### M3. `$execute` 재설계

목적: 구현 단계를 블랙박스가 아니라, AC 단위의 반복 가능한 작업 흐름으로 만든다.

이 단계에서 하는 일:

- `$execute`의 실제 작업 순서를 다시 정의
- 가능한 경우 test-first 또는 test-with-code 흐름을 기본으로 둠
- AC 하나를 고르고, 테스트를 쓰고, 실패를 보고, 구현하고, 다시 확인하는 흐름 정리
- project type에 따라 어떤 verify를 먼저 돌릴지 읽는 규칙 정리
- 너무 많은 state 용어 없이도 이해 가능한 실행 설명으로 바꿈

기본 흐름:

```text
pick AC
  -> choose test lane
  -> write or update test first if it makes sense
  -> run targeted test and see current failure
  -> implement
  -> rerun targeted test
  -> run broader verify if needed
  -> move to next AC
```

완료 조건:

- `$execute`를 읽으면 실제로 어떤 순서로 일하는지 보인다.
- 테스트가 실행의 중심에 있다.
- verify와 decide가 내부에서 어떻게 쓰이는지 쉬운 말로 설명된다.

### M4. `$qa` 설계

목적: commit 전에 한 번 더 전체를 보는 최종 검증 단계를 만든다.

이 단계에서 하는 일:

- `$qa`를 새 user-facing 단계로 정의
- plan과 실제 결과가 맞는지 확인하는 규칙 정리
- 코드 품질, 보안, 구조, 위험, 누락을 보는 check 정리
- 필요한 경우 reviewer-style agent나 skill을 어디까지 쓸지 결정
- commit 전에 무엇이 통과되어야 하는지 commit gate 정의

완료 조건:

- `$qa`가 무엇을 보는 단계인지 분명하다.
- `$execute` 안의 AC 검증과 `$qa`의 최종 검증이 구분된다.
- commit 전 기준이 문서로 남는다.

### M5. 숨겨진 지원층 정리

목적: 이제서야 state, progress, recovery, installer를 메인 플로우에 맞춰 다시 정리한다.

이 단계에서 하는 일:

- `ea_state.py`, `ea_progress.py`, `ea_codex.py`의 역할을 다시 점검
- 메인 플로우를 해치지 않는 범위에서만 지원층을 남김
- progress와 terminal summary가 진짜 필요한지, 필요하면 어디까지 필요한지 다시 판단
- installer도 user-facing skill 흐름을 돕는 범위로만 유지

완료 조건:

- 내부 지원층이 메인 플로우와 충돌하지 않는다.
- state/runtime이 과하게 앞에 나오지 않는다.
- 필요한 지원만 남기고 과한 부분은 제거하거나 뒤로 민다.

### M6. 설치와 사용 마무리

목적: 실제로 설치해서 쓸 수 있게 정리한다.

이 단계에서 하는 일:

- global Codex setup 흐름을 현재 플로우 기준으로 다시 점검
- 설치 후 어떤 skill이 보이고, 어떤 순서로 쓰는지 안내문 정리
- doctor, backup, manifest 같은 도구 설명을 메인 플로우에 맞게 다듬음

완료 조건:

- 처음 보는 사람도 설치 후 무엇을 먼저 해야 할지 안다.
- 설치 문서가 현재 메인 플로우와 맞는다.

## 단계 의존성

```text
M0 reset
  -> M1 brainstorming
  -> M2 planning
  -> M3 execute
  -> M4 qa
  -> M5 hidden support
  -> M6 install polish
```

이 순서를 크게 바꾸지 않는다.
특히 `state`, `progress`, `recovery`는 다시 뒤로 민다.

## 지금 당장 할 일

현재 바로 다음 작업은 이것이다.

1. `$brainstorming`을 다시 설계한다.
2. 그 다음 `$planning`을 다시 설계한다.
3. 그 다음 `$execute`를 다시 설계한다.
4. 그 뒤에 `$qa`를 만든다.
5. 마지막에 내부 지원층을 다시 정리한다.

## 기억해야 할 한 줄

이 프로젝트는 남의 Ralph loop를 닮게 만드는 것이 목표가 아니다.

이 프로젝트의 목표는:

**내가 이해할 수 있고, 실제로 계속 쓰고 싶은 작업 흐름을 만드는 것**이다.
