---
title: Everything Automate Runtime Flow
description: everything-automate v0 루프 커널의 inner loop와 outer flow를 실제 런타임 순서로 연결하고, 각 단계의 입력, 출력, 상태 변화를 정의한다.
doc_type: workflow
scope:
  - runtime flow
  - inner loop
  - outer flow
  - m2
covers:
  - docs/specs/everything-automate-loop-state-contract.md
  - docs/specs/everything-automate-plan-artifact-contract.md
  - docs/specs/everything-automate-evidence-contract.md
  - docs/specs/everything-automate-stage-transition-contract.md
  - docs/specs/everything-automate-implementation-milestones.md
---

# Everything Automate Runtime Flow

## 목적

이 문서는 `M1`에서 고정한 계약 문서들을 실제 런타임 순서로 연결한다.

핵심 질문은 이것이다.

- 어떤 단계가 먼저 시작되는가
- 각 단계는 무엇을 입력으로 받는가
- 각 단계는 무엇을 출력으로 남기는가
- 다음 단계는 어떤 조건에서 시작되는가

즉 이 문서는 계약 자체가 아니라, 계약들이 실제로 어떻게 움직이는지를 설명하는 `M2` 문서다.

중요한 전제:

- 이 문서는 설치된 결과물이 **타깃 런타임 안에서** 어떻게 동작하는지 설명한다.
- `everything-automate` authoring repo가 직접 세션에 읽히는 모델을 전제로 하지 않는다.
- 실제 동작은 나중에 `templates/`를 통해 배포된 산출물이 각 provider 환경에 설치된 뒤 시작된다.
- provider별 realization은 다를 수 있다. 현재 `v0` 구현 경로에서는 Codex가 인세션 workflow를 1차 UX로 두고, 그 아래에 runtime support 레이어를 두는 모델을 사용한다.

## 큰 구조

## 런타임 층 구분

`everything-automate`는 세 층으로 나눠서 이해한다.

### 1. authoring layer

이 저장소 자체다.

하는 일:

- 공통 커널 설계
- 문서 작성
- 템플릿 생성
- 패키징과 검증

### 2. distributable template layer

나중에 `templates/` 아래에 놓일 배포용 원본이다.

하는 일:

- provider별 `AGENTS.md` / `CLAUDE.md`
- provider별 hooks / plugin / skills / commands
- 설치 가능한 runtime assets 정의

### 3. installed runtime layer

사용자의 Claude Code, OpenCode, Codex, 사내 런타임 안에 실제로 설치된 결과물이다.

하는 일:

- session start
- bootstrap
- actionable request intake
- loop 실행

이 문서의 주된 관심사는 3번이다.

`everything-automate`의 런타임은 두 층으로 본다.

### 1. outer flow

```text
bootstrap
  -> intake
  -> plan
  -> commit
  -> execute
  -> verify
  -> decide
  -> wrap
```

### 2. inner loop

```text
plan -> execute -> verify -> decide
```

이 둘의 관계는 다음과 같다.

- `outer flow`는 세션 운영 순서다.
- `inner loop`는 문제 해결의 핵심 반복이다.
- `fixing`은 `decide`가 다시 `execute`로 되돌리는 루프 동작으로 이해한다.

## 핵심 상호작용

```text
authoring repo
  -> template build/package
  -> install/setup in target runtime
  -> session start in installed runtime
  -> bootstrap
  -> wait for actionable user request
  -> intake classification
  -> plan artifact
  -> committed state
  -> execution
  -> evidence
  -> decision
  -> wrap or loop
```

`M2`의 본문은 이 전체 중에서 `session start in installed runtime` 이후를 상세히 다룬다.

```text
session start in installed runtime
  -> bootstrap
  -> wait for actionable user request
  -> intake classification
  -> plan artifact
  -> committed state
  -> execution
  -> evidence
  -> decision
  -> wrap or loop
```

짧게 쓰면:

```text
actionable user request
  -> intake classification
  -> plan artifact
  -> committed state
  -> execution
  -> evidence
  -> decision
  -> wrap or loop
```

여기서 각 문서의 역할은 다음과 같다.

- `loop-state`
  지금 어디까지 왔는지 기록
- `plan-artifact`
  무엇을 해야 하는지 정의
- `evidence`
  무엇이 증명되었는지 기록
- `stage-transition`
  다음에 무엇을 해야 하는지 결정

## 설치 세션과 실행 세션 구분

혼동을 막기 위해 `M2`에서는 세션을 두 종류로 나눠서 본다.

### 1. install/setup session

설치용 세션이다.

하는 일:

- provider에 맞는 template 또는 plugin 선택
- target runtime에 파일/설정 반영
- 필요한 setup command 실행
- hooks, skills, entry file, config 연결

이 세션의 결과는 "설치된 runtime assets"다.
즉 아직 loop가 돈 것이 아니라, loop가 돌 준비가 끝난 상태다.

### 2. runtime session

실제 사용자가 대화하는 세션이다.

하는 일:

- session start
- bootstrap
- actionable request 대기
- intake 이후 loop 실행

이 세션에서부터 비로소 `plan -> execute -> verify -> decide` 커널이 의미를 가진다.

짧게 요약하면:

```text
install/setup session
  -> runtime session
  -> loop execution
```

중요:

- `bootstrap`은 install/setup session이 아니라 runtime session에서 일어난다.
- install/setup은 provider별로 다를 수 있다.
- bootstrap 이후의 공통 흐름은 최대한 provider와 무관하게 맞춘다.

## 현재 Codex realization

현재 `v0` 구현 순서에서는 Codex를 다음처럼 현실화한다.

```text
inside Codex
  -> workflow surfaces
  -> approved plan
  -> task handoff

under the hood
  -> runtime preparation
  -> execute
  -> verify
  -> decide
  -> wrap
```

중요:

- 이 분리는 커널 의미를 바꾸는 것이 아니다.
- Codex에서 인세션 workflow와 runtime support를 나누는 provider-specific realization이다.
- 현재 `M4`는 이 Codex realization의 in-session workflow와 handoff를 먼저 고정하는 단계다.

## 단계별 흐름

### 1. bootstrap

목적:

- 설치된 템플릿/플러그인이 타깃 런타임 세션 안에서 자신을 활성화한다.

입력:

- provider 정보
- 현재 작업 디렉터리
- 설치된 runtime assets
- provider별 entry surface

출력:

- 초기 `loop-state`
- provider capability
- 기본 경로 결정
- 공통 계약을 읽을 준비가 된 런타임

상태 변화:

- `stage = bootstrap`
- 성공 시 `intake`
- 실패 시 `failed`

`v0`에서는 bootstrap을 최소화한다.
필수 provider 감지, 공통 계약 로드 준비, 상태 저장 위치 결정만 한다.

중요:

- bootstrap은 authoring repo가 직접 수행하는 단계가 아니다.
- bootstrap은 설치된 결과물이 타깃 런타임 안에서 수행하는 단계다.

### 2. intake

목적:

- 들어온 요청을 처리 가능한 형태로 분류한다.

입력:

- 사용자 요청
- 현재 provider capability
- 기존에 이어지는 `task_id`가 있는지 여부

출력:

- `task_id`
- 처리 경로
  - 바로 실행 가능
  - clarification 필요
  - planning 필요

상태 변화:

- `stage = intake`
- planning 필요면 `planning`
- 이미 plan이 충분하면 `committed`
- 취소되면 `cancelled`

`v0`에서는 분류를 단순하게 유지한다.
기본 분류는 `direct | clarify | plan`이다.

### 3. plan

목적:

- 실행 가능한 plan artifact를 만든다.

입력:

- 사용자 요청
- intake 분류 결과
- 필요한 경우 코드베이스 탐색 결과

출력:

- `plan-artifact`
- AC
- verification plan
- open questions 해소 결과

상태 변화:

- `stage = planning`
- usable plan이 생기면 `committed`
- 풀리지 않는 질문이 남으면 `failed` 또는 이후 확장에서는 `blocked`

중요 규칙:

- `approved` 상태의 plan이 생기기 전에는 실행으로 넘어가지 않는다.
- `plan_path`가 이 단계 끝에서 고정된다.

### 4. commit

목적:

- 실행 계약을 잠근다.

입력:

- approved plan
- execution mode
- owner 정보

출력:

- committed loop-state
- 실행 시작에 필요한 최소 컨텍스트

상태 변화:

- `stage = committed`
- `execution_mode = single_owner`
- `owner_id` 설정
- `plan_path` 설정
- 이후 `executing`

이 단계가 필요한 이유는, planning과 실행을 명확히 분리하기 위해서다.
`commit`이 있어야 "생각 중인 plan"과 "실제로 돌리기로 한 plan"이 나뉜다.

### 5. execute

목적:

- plan artifact에 적힌 작업을 실제로 수행한다.

입력:

- committed loop-state
- approved plan

출력:

- 코드/문서/구성 변경
- 실행 로그
- 다음 검증에 필요한 변경 결과

상태 변화:

- `stage = executing`
- 작업 단위가 끝나면 `verifying`
- 즉시 수정이 필요하면 `fixing`

`v0`에서는 한 명의 owner가 plan의 implementation order를 순차적으로 따른다.

### 6. verify

목적:

- 완료 주장 대신 fresh evidence를 남긴다.

입력:

- 실행 결과
- verification plan

출력:

- evidence records
- pass/fail/unknown 판정 재료

상태 변화:

- `stage = verifying`
- evidence가 충분하면 `decide`
- evidence가 실패하거나 부족하면 `fixing`

중요 규칙:

- verification은 증거를 남기지 않으면 없는 것으로 본다.
- `unknown`만 있는 경우 완료로 갈 수 없다.

### 7. decide

목적:

- evidence와 plan 상태를 보고 다음 행동을 고른다.

입력:

- loop-state
- plan-artifact
- evidence

출력:

- 다음 stage 결정
- terminal 여부 결정

판단 결과:

- `fixing`
- `wrapping`
- `cancelled`
- `failed`

중요 규칙:

- `decide`는 별도 저장 stage라기보다 판단 엔진이다.
- pass라고 바로 `complete`로 가지 않는다.
- 반드시 `wrap`을 거쳐 terminal state로 간다.

### 8. wrap

목적:

- 작업 종료를 정리 가능한 상태로 만든다.

입력:

- 완료 또는 종료 직전 상태
- evidence
- plan 결과

출력:

- 최종 요약
- persistence artifact
- 종료된 loop-state

상태 변화:

- `stage = wrapping`
- 정리 성공 시 `complete`
- 정리 실패 시 `failed`

`wrap`은 단순한 메시지 출력이 아니다.
나중에 다시 볼 수 있는 종료 기록을 남기는 단계다.

## fixing 루프

`fixing`은 outer flow의 큰 단계가 아니라 inner loop 재진입 지점이다.

흐름은 이렇게 본다.

```text
execute
  -> verify
  -> decide
     -> fixing
     -> execute
     -> verify
     -> decide
```

상태 규칙:

- `fixing`으로 갈 때 `iteration += 1`
- `iteration >= max_iterations`이면 `failed` 후보가 된다
- `fixing`의 목적은 실패 원인을 없애는 것이지, 새 범위를 추가하는 것이 아니다

## v0 대표 시나리오

### 시나리오 A. 정상 완료

```text
session start
  -> bootstrap
  -> actionable request
  -> intake
  -> planning
  -> committed
  -> executing
  -> verifying
  -> decide(pass)
  -> wrapping
  -> complete
```

### 시나리오 B. 검증 실패 후 수정

```text
session start
  -> bootstrap
  -> actionable request
  -> intake
  -> planning
  -> committed
  -> executing
  -> verifying
  -> decide(fixing)
  -> fixing
  -> executing
  -> verifying
  -> decide(pass)
  -> wrapping
  -> complete
```

### 시나리오 C. 사용자 취소

```text
session start
  -> bootstrap
  -> actionable request
  -> intake
  -> planning
  -> committed
  -> executing
  -> decide(cancel)
  -> cancelled
```

### 시나리오 D. 반복 한도 초과

```text
session start
  -> bootstrap
  -> actionable request
  -> intake
  -> planning
  -> committed
  -> executing
  -> verifying
  -> decide(fixing)
  -> fixing
  -> executing
  -> verifying
  -> decide(fixing)
  -> ...
  -> failed(max_iterations)
```

### 시나리오 E. planning 생략 가능한 단순 작업

```text
session start
  -> bootstrap
  -> actionable request
  -> intake
  -> committed
  -> executing
  -> verifying
  -> decide(pass)
  -> wrapping
  -> complete
```

## 단계별 입출력 요약

| 단계 | 핵심 입력 | 핵심 출력 |
| --- | --- | --- |
| `bootstrap` | provider, workspace | 초기 state, capability |
| `intake` | request | task id, 처리 경로 |
| `plan` | request, context | approved plan |
| `commit` | plan, owner | committed state |
| `execute` | plan, state | work result |
| `verify` | work result | evidence |
| `decide` | state, plan, evidence | next action |
| `wrap` | final state candidate | terminal summary |

## 설치와 런타임 연결 메모

이 문서는 설치 절차 자체를 상세히 정의하지 않는다.
다만 `M2` 단계에서 잊지 않기 위해 provider별 설치/초기화 패턴을 메모로 남긴다.

상세 설치 절차는 별도 세션이나 이후 문서에서 다뤄도 된다.
여기서는 "설치가 먼저 있고, 그다음 설치된 런타임에서 bootstrap이 시작된다"는 사실만 고정한다.

### Claude Code 계열 참고 패턴

- plugin marketplace 또는 동등한 설치 표면 사용
- setup 명령으로 hooks / skills / config 반영
- 세션 시작 시 `CLAUDE.md`와 hook runtime이 bootstrap 수행

레퍼런스:

- `oh-my-claudecode`
- `superpowers`

### OpenCode 계열 참고 패턴

- plugin 또는 config 등록
- plugin transform / config hook으로 bootstrap text와 skills 경로 주입
- 설치된 plugin이 session bootstrap 수행

레퍼런스:

- `superpowers`
- `oh-my-openagent`

### Codex 계열 참고 패턴

- setup 명령 또는 install 문서 기반 설정
- `AGENTS.md` / skills / generated config 반영
- 설치된 산출물이 Codex 세션 안에서 bootstrap 수행

레퍼런스:

- `oh-my-codex`
- `superpowers`

### 이 메모의 의미

핵심은 설치 방식 자체보다 다음 사실이다.

- provider마다 설치 표면은 다르다
- 하지만 설치된 뒤 런타임이 읽는 공통 계약은 최대한 같아야 한다
- 구체적인 provider entry/bootstrap mapping은 `M3`에서 정의한다

## M2의 핵심 판단

`M1`이 "무엇이 존재해야 하는가"를 정했다면,
`M2`는 "그것들이 어떤 순서로 움직이는가"를 정한다.

이 단계에서 중요한 것은 기능을 늘리는 것이 아니다.
오히려 다음을 명확히 하는 것이다.

- 어떤 단계가 stage를 바꾸는가
- 어떤 단계가 evidence를 만든다
- 어떤 단계가 terminal state를 만든다
- 어떤 경우에 다시 loop로 들어간다

## 다음 단계와의 경계

이 문서가 끝나면 `M2`는 충분하다.
다음 `M3`에서 다룰 것은 이 흐름을 실제 provider 진입점에 어떻게 연결할지다.

즉 `M2`는 설치된 런타임 내부의 흐름을 정의하고,
`M3`는 provider별 setup, entry file, bootstrap 방식, intake trigger를 정의한다.
