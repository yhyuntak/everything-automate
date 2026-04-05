---
title: Everything Automate Claude M4 Pause Notes
description: Claude Code 기준으로 M4를 탐색하며 확인한 사실과, 현재 시점에서 Codex 우선 구현으로 전환하기로 한 이유를 기록한다.
doc_type: decision
scope:
  - claude code
  - m4
  - pause notes
  - implementation order
covers:
  - templates/claude-code/
  - runtime/ea_state.py
  - docs/specs/everything-automate-resume-cancel-contract.md
---

# Everything Automate Claude M4 Pause Notes

## 왜 이 문서를 남기나

Claude Code 기준으로 `M4`를 바로 구현하려다가, 현재 작업 환경이 Codex이고 Claude의 subagent/task metadata 연결 방식까지 정확히 확인해야 해서 생각 비용이 급격히 커졌다.

이 문서는 다음 두 가지를 위해 남긴다.

- Claude 쪽에서 어디까지 확인했는지 잊지 않기 위해
- 지금 시점에서는 Codex 우선 구현으로 전환한다는 결정을 명확히 남기기 위해

## 현재 결정

핵심 결정은 이거다.

```text
semantic reference
  -> Claude Code

practical implementation order for now
  -> Codex first
  -> Claude later
```

즉 의미 설계는 여전히 Claude Code가 더 자연스러운 참고점이지만,
지금 실제 구현 순서는 Codex에서 먼저 굴려보는 쪽이 더 현실적이다.

## Claude에서 확인한 것

### 1. Claude는 hook surface가 풍부하다

레퍼런스와 공식 문서 기준으로 다음 같은 이벤트 표면이 있다.

- `SessionStart`
- `Stop`
- `TaskCreated`
- `SubagentStart`
- `SessionEnd`

이 때문에 `resume/cancel` 같은 lifecycle 의미를 Claude에서는 비교적 자연스럽게 훅에 연결할 수 있다.

### 2. SessionStart/Stop 기반 M4 연결 초안은 만들었다

현재 template 쪽에 실험적으로 추가된 것:

- `templates/claude-code/hooks/hooks.json`
- `templates/claude-code/hooks/scripts/session-start-init.sh`
- `templates/claude-code/hooks/scripts/stop-suspend.sh`
- `templates/claude-code/hooks/scripts/cancel-current.sh`
- `templates/claude-code/hooks/scripts/resume-check.sh`

이 초안은 다음 의미만 검증했다.

- `SessionStart`에서 state init 가능
- `Stop`에서 conservative suspend 가능
- 명시적 helper로 cancel/resume-check 가능

### 3. 그러나 task metadata 전달 방식이 아직 불명확하다

지금까지 확인한 가장 큰 문제는 이것이다.

- subagent spawn 시점에 per-subagent env를 직접 넣는 공식 표면은 아직 분명하지 않다
- `TaskCreated`, `SubagentStart`, `additionalContext`, session env 파일 같은 우회 표면은 보이지만
- "task-bound session에 `task_id`와 `plan_path`를 가장 자연스럽게 전달하는 canonical path"는 아직 미정이다

즉 Claude 쪽은 hook는 강하지만, task metadata injection 경로를 더 정확히 조사해야 한다.

## 왜 여기서 멈추나

문제는 현재 작업 환경이 Codex라는 점이다.

Claude 쪽을 계속 파면 다음 주제들이 한꺼번에 열린다.

- subagent spawn semantics
- task metadata injection
- additionalContext vs env vs task file
- native subagent surface와 everything-automate state의 연결 방식

이건 지금 시점에서 `M4`를 빨리 끝내기보다,
Claude에 맞는 이상적인 모델을 더 깊게 설계하는 쪽으로 흘러가기 쉽다.

반면 지금 작업하는 환경은 Codex이므로,
"현재 내가 쓰는 곳에서 먼저 runtime primitive를 어떻게 굴릴까"를 보는 편이 더 빠르게 산출물을 만든다.

## 현재 Claude 구현물의 위치

현재 Claude 쪽 변경은 "버릴 것"이 아니라 "pause된 탐색 산출물"로 본다.

의미:

- 완성본으로 간주하지 않는다
- 후속 Claude 조사 때 다시 참고한다
- 지금은 Codex 구현을 막는 기준선으로 사용하지 않는다

## 이후 돌아왔을 때 다시 확인할 질문

Claude M4로 다시 돌아오면 아래 질문부터 확인한다.

1. `TaskCreated`에서 task metadata를 어디까지 안정적으로 얻을 수 있는가
2. `SubagentStart`에서 metadata를 어떤 표면으로 넘기는 것이 가장 자연스러운가
3. `additionalContext`만으로 충분한가, 아니면 task-context file이 필요한가
4. `Stop`이 실제로 어떤 종료 경계를 안정적으로 포착하는가
5. cancel은 명시적 helper로 둘지, hook/command hybrid로 둘지

## 지금부터의 구현 원칙

당분간은 이렇게 간다.

```text
shared runtime semantics
  -> already started

Codex implementation path
  -> next

Claude implementation path
  -> paused, documented, revisit later
```

중요:

- 이 결정은 "Claude를 버린다"는 뜻이 아니다
- 지금은 구현 순서만 Codex 우선으로 바꾸는 것이다

## 한 줄 결론

Claude Code는 여전히 더 풍부한 reference surface지만,
현재 단계에서는 그 풍부함 때문에 오히려 구현 논점이 너무 많이 열린다.

그래서 지금은 Claude M4 탐색을 기록으로 남기고,
실제 next step은 Codex 쪽 구현으로 옮기는 것이 맞다.
