---
title: Everything Automate Plan Artifact Contract
description: everything-automate v0 루프 커널이 사용하는 plan artifact의 최소 구조와 작성 규칙을 정의한다.
doc_type: spec
scope:
  - plan artifact
  - planning contract
  - acceptance criteria
covers:
  - docs/specs/everything-automate-loop-kernel-draft.md
  - docs/specs/everything-automate-implementation-milestones.md
---

# Everything Automate Plan Artifact Contract

## 목적

이 문서는 `plan` 단계의 산출물이 어떤 구조를 가져야 하는지 정의한다.

좋은 plan artifact는 다음 역할을 동시에 해야 한다.

- 사람이 읽고 이해할 수 있어야 한다.
- `execute` 단계가 바로 따라갈 수 있어야 한다.
- `verify` 단계가 무엇을 증명해야 하는지 알 수 있어야 한다.
- `decide` 단계가 완료 여부를 판단할 수 있어야 한다.

## 기본 원칙

- plan은 설명문이 아니라 실행 계약이어야 한다.
- acceptance criteria는 pass/fail 판단이 가능해야 한다.
- verification expectation이 없는 plan은 불완전하다.
- `v0`에서는 PRD-first보다 checklist-first에 가깝게 간다.
  나중에 story/PRD 구조가 필요하면 확장한다.

## v0 최소 구조

```yaml
---
title: string
task_id: string
status: draft | approved | in_progress | done | blocked | cancelled
execution_mode: single_owner
verification_policy: string
test_command: string | null
---
```

문서 본문에는 최소한 다음 섹션이 있어야 한다.

1. `Context`
2. `Goal`
3. `Non-goals`
4. `Acceptance Criteria`
5. `Verification Plan`
6. `Implementation Order`
7. `Open Questions`

## 섹션 계약

### Context

왜 이 작업을 하는지와 현재 전제를 적는다.

### Goal

이 작업이 끝났을 때 무엇이 달라지는지 한두 문장으로 적는다.

### Non-goals

이번 단계에서 하지 않을 것을 적는다.

### Acceptance Criteria

각 AC는 독립적인 work item이어야 한다.

권장 형식:

```text
- AC1. ...
  - TC: ...
- AC2. ...
  - TC: ...
```

규칙:

- 각 AC는 가능한 한 하나의 핵심 변화만 다룬다.
- 각 AC에는 하나 이상의 TC가 있어야 한다.
- TC가 정말 없다면 `(no TC)`를 명시한다.

### Verification Plan

검증은 최소한 다음을 포함해야 한다.

- 어떤 명령을 실행할지
- 어떤 결과를 pass로 볼지
- 수동 검증이 필요한지
- review가 필요한지

### Implementation Order

실행 순서를 적는다.
`v0`에서는 순차 실행이 기본이다.

### Open Questions

바로 결정되지 않은 것을 적는다.
질문이 남아 있으면 `status: approved`로 올리지 않는다.

## 상태 규칙

- `draft`
  아직 확정되지 않은 plan
- `approved`
  실행 가능
- `in_progress`
  실행 중
- `done`
  모든 AC와 verification이 통과함
- `blocked`
  외부 결정이나 해결되지 않은 문제로 진행 불가
- `cancelled`
  명시적으로 종료함

## plan과 loop-state의 관계

- `loop-state.plan_path`는 항상 현재 plan artifact를 가리켜야 한다.
- `planning`이 끝나고 `committed`로 가기 전에는 plan이 최소 `approved`여야 한다.
- `done`으로 바꾸기 전에 verification evidence가 있어야 한다.

## 금지 규칙

- goal만 있고 AC가 없는 plan
- AC는 있는데 verification이 없는 plan
- open question이 남아 있는데 `approved`인 plan
- `done`인데 evidence가 없는 plan

## 구현 판단

`v0`에서는 plan을 너무 거대하게 만들지 않는다.

필요한 것은:

- 무엇을 할지
- 무엇을 하지 않을지
- 무엇이 완료 조건인지
- 무엇으로 검증할지

이 네 가지다.
