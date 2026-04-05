---
title: Everything Automate Evidence Contract
description: everything-automate v0 루프 커널이 완료 판단에 사용하는 verification evidence 구조와 기록 규칙을 정의한다.
doc_type: spec
scope:
  - evidence
  - verification
  - completion criteria
covers:
  - docs/specs/everything-automate-loop-kernel-draft.md
  - docs/specs/everything-automate-implementation-milestones.md
---

# Everything Automate Evidence Contract

## 목적

이 문서는 `verify` 단계가 남겨야 하는 evidence의 최소 구조를 정의한다.

핵심 원칙은 단순하다.

- 완료는 주장으로 결정하지 않는다.
- 완료는 fresh evidence로 결정한다.

## 기본 원칙

- evidence는 가능하면 실행 직후 기록한다.
- evidence는 사람이 읽을 수 있어야 한다.
- evidence는 런타임이 pass/fail 판단에 사용할 수 있어야 한다.
- evidence가 없으면 `complete`로 갈 수 없다.

## v0 evidence record

```yaml
- kind: test | lint | build | review | browser | manual
  name: string
  command: string
  artifact_path: string | null
  status: pass | fail | unknown
  summary: string
  captured_at: string
```

## 필드 정의

- `kind`
  어떤 종류의 검증인지 나타낸다.
- `name`
  사람이 빠르게 식별할 수 있는 이름이다.
- `command`
  어떤 명령이나 절차로 검증했는지 적는다.
  수동 검증이면 `manual:<description>` 형식도 허용한다.
- `artifact_path`
  로그, 스크린샷, JSON 결과 등 관련 artifact 경로다.
- `status`
  `pass`, `fail`, `unknown` 중 하나다.
- `summary`
  핵심 결과를 짧게 적는다.
- `captured_at`
  evidence를 기록한 시각이다.

## v0 최소 요구사항

`complete`로 가기 전에 최소 하나 이상의 evidence가 있어야 한다.

권장 최소 조합:

- 자동 검증이 가능한 경우
  `test` 또는 `build` evidence 1개 이상
- 자동 검증이 불충분한 경우
  `manual` 또는 `review` evidence 추가

## evidence 저장 규칙

- evidence는 plan 또는 별도 evidence 파일과 연결되어야 한다.
- `loop-state`는 evidence 전체를 직접 담지 않아도 되지만, evidence가 어디 있는지는 추적 가능해야 한다.
- 같은 명령을 다시 실행했다면 이전 evidence를 덮어쓰기보다 새 기록을 추가한다.

## pass/fail 해석 규칙

### `pass`

- 실행 결과가 명시적으로 성공했고
- 요약이 그 성공 이유를 설명하며
- 필요하면 artifact가 연결됨

### `fail`

- 실행 결과가 명시적으로 실패했거나
- reviewer/manual verification이 미완료 또는 부적합하다고 판단함

### `unknown`

- 아직 해석되지 않았거나
- 명령은 실행했지만 결과 판단이 끝나지 않았거나
- evidence는 모였지만 review가 필요함

`unknown` 상태의 evidence만 있는 경우 `decide`는 `complete`를 선택할 수 없다.

## 금지 규칙

- 명령은 실행했지만 기록이 없는 검증
- `summary` 없이 상태만 적은 evidence
- stale output을 fresh evidence처럼 사용하는 것
- 실패했는데 artifact를 남길 수 있었음에도 아무것도 남기지 않는 것

## 구현 판단

`claude-automate`의 stop hook처럼 검증 명령을 돌리는 습관은 유지하되, 결과를 버리면 안 된다.

`everything-automate`에서는 evidence를 반드시 남겨야 한다.

- 무엇을 실행했는지
- 결과가 어땠는지
- 왜 pass/fail인지

이 세 가지가 없으면 나중에 `decide`를 다시 평가할 수 없다.
