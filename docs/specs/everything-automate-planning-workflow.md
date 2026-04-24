---
title: Everything Automate Planning Workflow
description: Codex 인세션 planning workflow의 canonical flow, 4-agent 구성, 그리고 Ralph-ready handoff를 위한 plan artifact와 agent prompt contract를 정의한다.
doc_type: spec
scope:
  - planning
  - codex
  - agents
  - prompts
  - handoff
covers:
  - docs/specs/everything-automate-plan-artifact-contract.md
  - docs/specs/everything-automate-codex-execution-model.md
  - docs/specs/everything-automate-implementation-milestones.md
  - templates/
---

# Everything Automate Planning Workflow

## Historical Note

This document is kept as design history.

It predates the current `ea-brainstorming -> ea-north-star -> ea-blueprint -> ea-planning` workflow.
Read it as an older planning draft, not as the current skill contract.

## 목적

이 문서는 `everything-automate`에서 planning을 어떻게 다룰지 고정한다.

핵심 질문은 다음과 같다.

- Codex 안에서 planning workflow는 어떤 순서로 진행되는가
- 어떤 agent들이 planning에 참여하는가
- 각 agent의 system prompt는 어떤 역할과 경계를 가져야 하는가
- planning 결과는 어떻게 Ralph-ready handoff artifact가 되는가

핵심 판단은 간단하다.

- planning은 runtime보다 먼저다
- planning은 implementation plan 생성이 아니라 execution handoff까지 포함해야 한다
- planning agent stack은 작고 선명해야 한다
- planning에는 항상 clarification phase가 있어야 한다
- 하지만 clarification phase가 항상 user interview를 의미하지는 않는다

## 기준선

현재 planning 기준선은 다음 세 레퍼런스를 섞는다.

- `claude-automate` planning
  - direct/interview mode
  - explore first, ask later
  - angel/devil 기반 확장과 검증
  - user confirmation 뒤 plan file 생성
- `superpowers`
  - brainstorming -> spec -> plan 순서
  - design approval gate
  - 옵션 비교와 recommendation discipline
- `oh-my-codex`
  - `deep-interview`
  - `ralplan`
  - execution gate
  - plan-to-ralph handoff

정리하면:

```text
claude-automate planning skeleton
  + brainstorming/spec gate
  + deep-interview readiness gate
  + ralplan-style consensus review
  = everything-automate planning
```

## 핵심 설계 원칙

### 1. planning은 implementation 전에 끝나야 한다

planning의 목적은 "생각을 좀 해보는 것"이 아니라:

- intent 정리
- scope 고정
- non-goals 명시
- decision boundaries 고정
- acceptance criteria 확정
- verification path 고정
- execution handoff 준비

를 끝내는 것이다.

### 2. planning은 broad request와 execution request를 구분해야 한다

다음 둘은 다르게 다뤄야 한다.

- vague request
  - 먼저 clarify/interview
- execution keyword가 붙은 request
  - 충분히 구체적이지 않으면 planning gate로 되돌림

즉 `ralph` 같은 execution mode는 planning gate를 우회하는 면허가 아니다.

### 3. planning은 항상 clarification gate를 거쳐야 한다

clarification gate는 planning의 기본 phase다.
다만 결과는 두 가지로 나뉜다.

- 질문 없이 통과
- one-question-at-a-time clarification 실행

즉 구조는 이렇다.

```text
preflight
  -> explore
  -> ambiguity remains?
     -> no: continue
     -> yes: clarification
```

다른 레퍼런스들이 “항상 인터뷰하는 느낌”을 주는 이유도 사실은
항상 clarification phase를 거치기 때문이다.

### 4. plan file은 실행 준비 문서여야 한다

plan은 단순한 요약이 아니다.
최종 산출물은 execution handoff artifact여야 한다.

즉 plan file은:

- 사람이 읽을 수 있어야 하고
- agent가 handoff 입력으로도 읽을 수 있어야 한다

## Primary In-Session Workflow

Codex 안에서 planning은 대체로 다음 흐름을 따른다.

```text
$brainstorming (optional, upstream)
  -> $planning
  -> clarification gate
  -> angel
  -> architect
  -> devil
  -> user approval
  -> handoff to $execute or other execution mode
```

주의:

- `$brainstorming`은 ideation/design shaping이 먼저 필요할 때 선행
- `$planning`은 기본 planning surface
- `deep-interview`/`ralplan`의 강한 readiness gate와 consensus review는 `$planning` 내부 contract로 흡수한다

## Planning Modes

planning은 네 가지 모드를 가진다.

| Mode | 언제 쓰나 | 핵심 동작 |
| --- | --- | --- |
| `direct` | 요청이 이미 구체적일 때 | clarification gate는 통과하되 user interview 없이 draft로 넘어갈 가능성이 높음 |
| `interview` | broad/vague request일 때 | clarification gate가 열리고 one-question-at-a-time clarification lane이 먼저 수행됨 |
| `consensus` | high-risk / high-impact request일 때 | architect -> devil 순차 검토 |
| `review` | 기존 plan을 점검할 때 | plan 재작성 없이 검토 중심 |

추천 기준:

- file/symbol/behavior가 명확하면 `direct`
- vague verbs, broad goal, multiple unknowns면 `interview`
- auth/security/migration/public API breakage면 `consensus`

## Canonical Planning Flow

### Step 1. Mode Detection

입력:

- user request
- conversation history
- codebase specificity

출력:

- `direct | interview | consensus | review`

규칙:

- broad request는 `interview`
- high-risk request는 `consensus`
- 단순하고 구체적인 task는 `direct`

### Step 2. Preflight Context Intake

planning을 시작하기 전에 최소 context snapshot을 만든다.

최소 필드:

- task statement
- desired outcome
- known facts
- constraints
- unknowns
- likely touchpoints

이 단계 목적:

- 바로 질문부터 던지지 않기
- 현재 알고 있는 것과 모르는 것을 분리하기

### Step 3. Explore

사용자에게 물어보기 전에 먼저 코드베이스 사실을 찾는다.

탐색 목표:

- 수정 후보 파일
- 기존 패턴
- 관련 dependency
- impact scope

원칙:

- codebase facts는 explore가 먼저 확인
- user preference만 사용자에게 묻는다

### Step 4. Clarification Gate

이 단계는 planning에서 항상 존재한다.

판정 질문:

- intent가 충분히 선명한가
- desired outcome이 충분히 선명한가
- non-goals가 충분히 보이는가
- decision boundaries가 충분히 보이는가

핵심 ambiguity가 남아 있으면 clarification lane을 연다.

### Step 5. Clarification Lane if Needed

`interview` mode일 때 수행한다.

반드시 먼저 확정할 항목:

- intent
- desired outcome
- scope
- non-goals
- decision boundaries

후순위:

- implementation detail
- optimization preference

원칙:

- 한 번에 한 질문
- 같은 thread를 깊게 판다
- scope보다 먼저 why와 boundary를 본다

### Step 6. Problem Framing

draft plan 전에 아래를 고정한다.

- problem statement
- why now
- success definition
- non-goals
- decision boundaries
- decision drivers
- viable options
- recommended direction

효과:

- task list가 너무 일찍 떨어지는 걸 막는다
- architect review 품질이 올라간다
- 나중에 “왜 이 방향이었는지”가 남는다

### Step 7. Draft Plan

초기 plan draft를 만든다.

포함 요소:

- requirements summary
- AC list
- verification plan
- implementation order
- risk list
- open questions

### Step 8. Angel Expansion

draft를 확장한다.

Angel의 역할:

- 빠진 work item 찾기
- edge case 찾기
- AC 누락 찾기
- verification 빈틈 찾기

주의:

- Angel은 설계를 확정하지 않는다
- Angel은 가능성을 넓힌다

### Step 9. Architect Review

설계 선택과 execution shape를 점검한다.

Architect의 역할:

- 현재 plan의 구조적 타당성 검토
- meaningful alternative 1개 이상 제시
- tradeoff tension 명시
- 왜 이 방향이 execution-ready인지 검토

이 단계에서 ADR 수준의 결정이 생긴다.

### Step 10. Devil Validation

마지막으로 냉정하게 공격한다.

Devil의 역할:

- vague AC 공격
- untestable verification 공격
- risk mitigation 부족 지적
- plan-handoff mismatch 지적
- scope creep 지적

원칙:

- Devil은 호의적 요약자가 아니다
- reject / iterate 판단을 분명히 해야 한다

### Step 11. Plan Self-Check

마지막 revise 이후, approval 전에 planning agent가 빠르게 self-check를 돈다.

확인할 것:

- placeholder 없음?
- AC는 testable 한가?
- verification steps는 concrete 한가?
- implementation order는 AC와 맞물리는가?
- handoff block은 완전한가?
- 문서 내부 모순은 없는가?

### Step 12. User Approval

사용자에게 최종 plan을 보여준다.

여기서 확인할 것:

- 이대로 진행
- 수정 필요
- execution mode 선택

추천 execution mode:

- `execute`
- `team` (future)
- other execution mode (future)

### Step 13. Execution Handoff

승인된 plan을 execution-ready artifact로 잠근다.

여기서 고정할 것:

- `task_id`
- `plan_path`
- `approval_state`
- `execution_unit`
- recommended execution mode
- acceptance criteria
- verification commands
- non-goals
- decision boundaries
- unresolved risk notes

즉 이 단계가 끝나야 `$execute` 같은 execution surface로 넘길 수 있다.

## Agent Roster

planning에 참여하는 기본 agent는 4개만 둔다.

```text
explorer
angel
architect
devil
```

이유:

- 충분히 강한 planning loop를 만들 수 있음
- 역할이 겹치지 않음
- 늘리면 orchestration cost가 커짐

## Agent Responsibilities

### 1. explorer

역할:

- 코드베이스 사실 확인
- 영향 범위 파악
- 기존 패턴/관례 찾기

하지 말 것:

- 설계 결정
- 요구사항 확정
- 구현 제안의 강한 결론화

### 2. angel

역할:

- 빠진 관점 확장
- edge case 추가
- AC와 TC의 누락 보완

하지 말 것:

- 최종 구조 선택
- 비판적 reject 판단

### 3. architect

역할:

- plan의 구조적 soundness 검토
- 대안 비교
- tradeoff 문서화
- execution lane 제안

하지 말 것:

- nitpick 중심 리뷰
- 단순 completeness checker 역할

### 4. devil

역할:

- ambiguity 공격
- untestable plan 공격
- risk/verification mismatch 공격
- reject / iterate 판단

하지 말 것:

- 새로운 대안만 무한히 추가
- 설계 ownership을 가져가기

## Agent System Prompt Contract

각 agent는 긴 프롬프트보다 역할 경계가 분명해야 한다.

### explorer system prompt contract

핵심 목적:

- planning에 필요한 코드베이스 사실만 빠르게 수집

반드시 지킬 것:

- 추측보다 evidence
- file/symbol/path 중심
- planning 판단에 필요한 범위만 조사
- recommendation보다 findings 우선

출력 형식:

- relevant files
- current pattern
- likely touchpoints
- open unknowns

### angel system prompt contract

핵심 목적:

- 현재 plan draft에서 빠진 가능성과 edge case를 찾기

반드시 지킬 것:

- 현재 draft를 전제로 확장
- AC, TC, risk, edge case 관점에서 gap 찾기
- scope를 무한정 넓히지 않기

출력 형식:

- missing work items
- missing validation points
- edge cases
- optional improvements

### architect system prompt contract

핵심 목적:

- plan을 execution-ready 구조로 만들기

반드시 지킬 것:

- favored option 하나만 밀지 말고 meaningful alternative를 제시
- tradeoff tension을 명확히 쓰기
- 왜 이 방향이 handoff-ready인지 설명
- 필요하면 ADR 관점으로 정리

출력 형식:

- recommended approach
- alternatives considered
- tradeoffs
- execution recommendation
- architecture risks

### devil system prompt contract

핵심 목적:

- plan이 실제 execution에서 깨질 지점을 공격적으로 찾기

반드시 지킬 것:

- vague AC를 허용하지 않기
- untestable verification을 허용하지 않기
- non-goals/decision boundaries 누락을 공격하기
- reject / iterate / approve를 분명히 하기

출력 형식:

- verdict: `approve | iterate | reject`
- critical gaps
- ambiguous points
- verification failures
- required revisions

## Reference Comparison

### Compared to `claude-automate` planning

공통점:

- `direct / interview` mode detection
- explore first, ask later
- angel/devil를 통한 확장과 검증
- user confirmation 뒤 plan을 잠그는 discipline

차이점:

- `claude-automate`는 implementation plan 생성이 중심이다
- `everything-automate`는 execution handoff artifact 생성이 중심이다
- `everything-automate`는 `architect`를 planning core에 넣는다
- `everything-automate`는 non-goals / decision boundaries / handoff block을 더 강하게 강제한다
- `everything-automate`는 planning을 execution gate로 본다
- `everything-automate`는 clarification gate와 self-check를 명시적으로 둔다

한 줄 요약:

```text
claude-automate planning
  -> 좋은 implementation-plan generator

everything-automate planning
  -> canonical pre-execution contract
```

### Compared to `superpowers`

공통점:

- planning 전에 ideation/design shaping이 필요할 수 있다는 점
- user approval gate를 강하게 둔다는 점
- implementation 전에 spec/plan을 먼저 확정한다는 점

차이점:

- `superpowers`는 `brainstorming -> writing-plans`로 더 upstream/downstream 분리가 강하다
- `everything-automate`는 `brainstorming`을 별도 active skill로 두되, planning 자체는 execution-handoff 중심으로 더 압축한다
- `superpowers`는 2-3 approaches 제시와 spec 문서화 ceremony가 더 강하다
- `everything-automate`는 agent-orchestrated plan hardening이 더 강하다
- `superpowers`의 spec self-review discipline은 우리 planning의 self-check 단계로 흡수할 수 있다

한 줄 요약:

```text
superpowers
  -> design/spec discipline first

everything-automate planning
  -> execution-ready plan hardening first
```

### Compared to `oh-my-codex` `deep-interview` / `ralplan`

공통점:

- intent-first clarification
- non-goals / decision boundaries의 중요성
- execution 전에 readiness gate를 둔다는 점
- architecture-heavy 작업에는 stronger review를 붙인다는 점

차이점:

- `oh-my-codex deep-interview`는 별도 skill이며 ambiguity gating이 더 무겁다
- `everything-automate`는 그 강한 readiness gate를 `$planning` 내부 contract로 흡수한다
- `ralplan`은 `ralph/team` handoff를 전제로 한 consensus launcher에 가깝다
- `everything-automate`는 현재 `$execute` handoff를 중심으로 더 단순한 canonical planning contract를 만든다
- `oh-my-codex`는 정량적 ambiguity scoring이 강하지만, `everything-automate`는 당장은 lighter gate로 유지한다

한 줄 요약:

```text
oh-my-codex
  -> stronger explicit interview/consensus ceremony

everything-automate planning
  -> lighter single planning surface with absorbed readiness rules
```

## What Changes from Claude-Automate

`claude-automate` planning에서 유지할 것:

- direct/interview mode
- explore first
- angel/devil
- user confirmation
- plan file discipline

`everything-automate`에서 추가할 것:

- brainstorming/spec gate
- deep-interview readiness gate
- architect review
- clarification gate
- problem framing
- decision drivers / viable options / recommendation
- self-check
- execution handoff block
- non-goals / decision boundaries 강제
- execute-ready execution recommendation

즉 차이는 이거다.

```text
claude-automate planning
  -> implementation plan 중심

everything-automate planning
  -> execution handoff 중심
```

## Plan Artifact Requirements

planning의 최종 산출물은 최소한 아래를 가져야 한다.

- requirements summary
- desired outcome
- in-scope
- non-goals
- decision boundaries
- problem framing
- decision drivers
- viable options
- recommended direction
- acceptance criteria
- verification steps
- implementation order
- risks and mitigations
- handoff block

### Handoff Block

planning 종료 시 plan file에는 아래 execution handoff 정보가 있어야 한다.

- `task_id`
- `plan_path`
- `approval_state`
- `execution_unit`
- `recommended_mode`
- `recommended_agents`
- `verification_lane`
- `open_risks`

이 block이 있어야 later execution surface가 plan을 읽고 실행을 시작할 수 있다.

## Recommended Initial UX

초기 Codex UX는 이렇게 가는 게 좋다.

```text
vague request
  -> $brainstorming or clarification lane
  -> $planning
  -> architect/devil review
  -> approval
  -> $execute

clear request
  -> $planning --direct
  -> architect/devil review
  -> approval
  -> $execute
```

즉 `$execute`는 planning을 대체하지 않고,
planning이 끝난 뒤 handoff를 받아야 한다.

## 한 줄 결론

`everything-automate` planning의 목표는 단순한 plan 작성이 아니다.

정확한 목표는 이것이다.

```text
turn vague intent into an execution-ready handoff artifact
```

그리고 이를 위해 planning stack은 다음 네 agent면 충분하다.

```text
explorer
angel
architect
devil
```
