---
title: Everything Automate Provider Entry and Bootstrap Mapping
description: M3 단계에서 provider별 설치 표면, 진입 파일, bootstrap 방식, intake 연결 방식을 고정한다.
doc_type: spec
scope:
  - m3
  - providers
  - bootstrap
  - intake
  - templates
covers:
  - docs/specs/everything-automate-runtime-flow.md
  - docs/specs/everything-automate-implementation-milestones.md
  - AGENTS.md
  - templates/
---

# Everything Automate Provider Entry and Bootstrap Mapping

## 목적

이 문서는 `M3` 단계에서 다음 질문에 답한다.

- provider마다 설치는 어디서 시작되는가
- 설치가 끝난 뒤 세션은 무엇을 진입점으로 읽는가
- bootstrap은 어떤 표면에서 일어나는가
- intake는 언제 시작되는가
- 로컬 authoring 규칙과 배포용 template 규칙은 어디서 갈라지는가

핵심 판단은 간단하다.

- `M2`는 설치된 런타임 내부 흐름을 정의했다.
- `M3`는 그 흐름이 provider별로 **어디에 연결되는지**를 정의한다.

## 범위

이 문서가 다루는 것:

- provider별 install/setup surface
- provider별 runtime entry surface
- provider별 bootstrap mechanism
- provider별 skill/hook discovery 방식
- provider별 intake 시작 조건
- `templates/` 아래 source-of-truth 구조 초안

이 문서가 아직 다루지 않는 것:

- 실제 setup 스크립트 구현
- 실제 hooks/skills 코드 구현
- resume/cancel hardening
- team/subagent 확장

## M3의 핵심 판단

`everything-automate`는 세 층으로 나뉜다.

```text
authoring repo
  -> distributable templates
  -> installed runtime
```

여기서 `M3`의 책임은 이것이다.

```text
template source-of-truth
  -> provider install/setup surface
  -> installed runtime entry surface
  -> bootstrap
  -> first actionable request
  -> intake
```

즉 `M3`는 "설치 방법"과 "세션 진입 방법" 사이를 연결하는 단계다.

## 공통 규칙

모든 provider에서 다음 규칙을 유지한다.

### 1. 로컬 규칙과 배포 규칙을 섞지 않는다

- 루트 `AGENTS.md`는 authoring repo 전용이다.
- 실제 배포용 진입 파일은 앞으로 `templates/`가 source-of-truth가 된다.

### 2. 세션 시작이 곧 loop 시작은 아니다

- session start
- bootstrap
- actionable request 대기
- intake 시작

이 순서를 provider와 무관하게 유지한다.

### 3. bootstrap은 설치 이후 런타임 안에서 일어난다

- authoring repo가 직접 읽히는 것이 아니다.
- 설치된 template/plugin/runtime asset이 target runtime 안에서 활성화된다.

### 4. 공통 계약은 최대한 같게 유지한다

provider마다 설치 방식은 달라도, 최종적으로 읽게 할 계약은 최대한 같아야 한다.

공통 계약 후보:

- top-level operating guidance
- loop-state contract
- plan artifact contract
- evidence contract
- stage transition contract

### 5. intake는 항상 최소 분류부터 시작한다

`v0`의 intake 분류는 모든 provider에서 동일하게 유지한다.

```text
direct | clarify | plan
```

## 우선순위 대상

Current implementation baseline:

- Claude Code

Priority rule:

- use Claude Code as the design center
- do not block Claude-first implementation on Codex constraints
- keep Codex adaptation in mind without lowering the shared kernel early

Follow-up targets:

- Codex CLI
- OpenCode
- internal runtime (OpenCode-like)

이 우선순위는 설치/entry/bootstrap 설계를 정할 때도 그대로 적용한다.

## Provider Mapping

| Provider | Install / Setup Surface | Runtime Entry Surface | Bootstrap Mechanism | Skill / Hook Discovery | Intake Trigger | M3 판단 |
| --- | --- | --- | --- | --- | --- | --- |
| Claude Code | plugin marketplace, local plugin install, setup command | `CLAUDE.md`, plugin metadata, hooks config | setup 이후 plugin + hook runtime이 세션 규칙과 skills를 활성화 | plugin-defined skills, hook files, Claude-native config | session start 후 첫 actionable request | current implementation baseline |
| OpenCode | `opencode.json` plugin 등록, project/global config, restart | plugin file, project `AGENTS.md` 또는 bootstrap text injection | plugin transform/config hook이 bootstrap text와 skill paths를 주입 | plugin config hook, skills path registration, native skill tool | session start 후 첫 actionable request | follow-up target |
| internal runtime | 사내 설치 방식에 맞는 plugin/config 등록 | OpenCode-like entry surface 또는 별도 internal entry doc | internal adapter가 OpenCode-compatible bootstrap을 우선 사용 | internal plugin loader 또는 shared skill discovery | session start 후 첫 actionable request | follow-up target |
| Codex CLI | setup command, install docs, generated config | `AGENTS.md`, local skills, generated overlays | setup으로 생성된 guidance + skill/runtime overlays가 Codex session에 붙음 | skills directory, `AGENTS.md`, generated runtime markers | session start 후 첫 actionable request | follow-up adaptation target |

## Provider별 해석

### Claude Code

레퍼런스에서 반복해서 보인 패턴:

- marketplace/plugin install
- `/setup` 또는 동등한 setup command
- `CLAUDE.md` + hooks + plugin metadata

`everything-automate`가 가져갈 핵심:

- Claude Code용 배포물은 `CLAUDE.md`가 top-level guidance entry여야 한다.
- setup은 hooks, skills, config를 런타임에 연결하는 단계여야 한다.
- bootstrap은 세션 시작 후 hook/plugin 표면에서 수행된다.

가져가지 않을 것:

- provider 고유의 세세한 hook 구현을 공통 커널 안으로 끌고 들어오지 않는다.

### OpenCode

레퍼런스에서 반복해서 보인 패턴:

- plugin 등록
- plugin auto-install 또는 restart 후 활성화
- config hook으로 skills path 등록
- message/system transform으로 bootstrap context 주입

`everything-automate`가 가져갈 핵심:

- OpenCode용 배포물은 plugin 중심이 자연스럽다.
- bootstrap text injection과 skill path registration을 분리해서 본다.
- OpenCode의 native skill surface와 충돌하지 않게 설계한다.
- 다만 초기 구현 기준은 Claude Code에 두고, OpenCode는 그 다음 적응 레이어로 둔다.

가져가지 않을 것:

- bootstrap 문구를 provider 특화 표현에 과도하게 묶지 않는다.

### internal runtime

현재 판단:

- 사내 런타임은 OpenCode-like라고 가정한다.
- 따라서 Claude 기준선이 선 뒤에 OpenCode adapter를 기반으로 internal overlay를 얹는 방식이 맞다.

의미:

- internal 전용 커널을 새로 만들지 않는다.
- OpenCode template를 기반으로 필요한 차이만 얹는다.

### Codex CLI

레퍼런스에서 반복해서 보인 패턴:

- `AGENTS.md`가 top-level operating contract
- skills directory
- setup command로 generated config / overlays 반영

`everything-automate`가 가져갈 핵심:

- Codex는 `AGENTS.md` 중심 guidance entry가 자연스럽다.
- setup은 skill discovery와 runtime overlay 반영을 담당한다.
- Codex는 Claude Code 구현이 선 뒤에 적응시켜야 할 후속 target로 둔다.

의미:

- Claude Code와 최대한 비슷한 커널 의미를 유지하되, Codex 제약은 뒤에서 overlay와 degrade path로 처리한다.
- Claude/OpenCode에서 가능한 표면이 Codex에 없더라도, 먼저 Claude 기준 의미를 구현하고 나중에 Codex 대체 경로를 찾는다.

## Template Source-of-Truth 초안

`M3` 단계에서 고정할 최소 구조는 다음과 같다.

```text
templates/
  claude-code/
    CLAUDE.md
    INSTALL.md
    hooks/
    skills/
    plugin/

  opencode/
    AGENTS.md
    INSTALL.md
    plugin/
    skills/

  internal/
    AGENTS.md
    INSTALL.md
    adapter/
    skills/

  codex/
    AGENTS.md
    INSTALL.md
    skills/
    overlays/
```

중요:

- 이 구조는 source-of-truth 초안이다.
- 실제 구현은 이후 단계에서 최소한부터 생성한다.
- `AGENTS.md`와 `CLAUDE.md`는 같은 내용을 복붙하는 파일이 아니라, 같은 공통 계약을 provider surface에 맞게 표현한 진입 파일이어야 한다.

## Entry Surface 규칙

### top-level guidance entry

provider마다 top-level guidance entry가 하나는 있어야 한다.

- Claude Code: `CLAUDE.md`
- OpenCode: `AGENTS.md` 또는 plugin-injected bootstrap contract
- internal: internal entry doc 또는 OpenCode-compatible entry
- Codex: `AGENTS.md`

규칙:

- top-level guidance entry는 "이 세션이 무엇을 따르는가"를 정의한다.
- plan/verify/decide 같은 공통 커널 규칙을 provider 표현으로 압축한다.
- install guide나 긴 설계 문서를 직접 대체하지 않는다.

### install guide

각 provider template는 최소 하나의 `INSTALL.md`를 가진다.

역할:

- 설치 절차
- setup command
- verify 방법
- uninstall/update 메모

즉 `M2`에서 메모로만 남겨둔 설치 방법을, `M3` 이후에는 provider별 `INSTALL.md`로 구체화할 수 있어야 한다.

### skills and hooks

규칙:

- skill 내용은 가능한 한 공통화한다.
- hook/plugin 코드는 provider-specific 표면으로 분리한다.
- provider-specific 연결은 template 안에서 처리하고, 커널 계약 자체는 바꾸지 않는다.

## Bootstrap Contract at M3

`M3`에서 bootstrap이 반드시 해내야 하는 최소 일은 다음과 같다.

```text
1. provider identity 파악
2. top-level guidance entry 활성화
3. skill / hook / plugin assets 연결
4. shared contract location 파악
5. runtime state root 결정
6. actionable request를 받을 준비 완료
```

여기서 중요한 점:

- 아직 loop를 시작하지 않는다.
- bootstrap의 완료 조건은 "실행 준비 완료"다.

## Intake Contract at M3

`M3`에서 intake가 반드시 해내야 하는 최소 일은 다음과 같다.

```text
1. actionable request 여부 판단
2. 기존 run/task 이어받기 여부 확인
3. direct | clarify | plan 분류
4. task id와 execution intent 기록
```

추가 규칙:

- 일반 대화는 intake를 강제로 시작하지 않는다.
- 첫 actionable request가 들어왔을 때만 실제 loop 진입 후보가 된다.

## M3 산출물

이 단계에서 실제로 남겨야 할 것은 다음이다.

- provider entry/bootstrap mapping 문서
- provider별 template source-of-truth 구조 초안
- provider별 `INSTALL.md` 필요성 정의
- top-level guidance entry 규칙

이 단계가 끝나면 다음 단계에서 실제 파일 생성이 가능해진다.

## M3 이후 바로 이어질 구현

`M3`가 끝나면 다음 작업은 훨씬 구체적이 된다.

- `templates/` 디렉터리 실제 생성
- provider별 `INSTALL.md` 초안 작성
- provider별 top-level entry file 초안 생성
- minimal bootstrap assets 생성
- minimal intake 기록 방식 생성

즉 `M3`는 마지막 순수 설계 단계라기보다,
실제 template 구현 직전의 연결 단계다.

## 핵심 결론

`M3`의 핵심은 "provider별로 다르게 설치되더라도, 설치된 뒤에는 같은 커널 흐름으로 진입하게 만든다"는 데 있다.

짧게 쓰면:

```text
different install surfaces
  -> provider-specific entry
  -> provider-specific bootstrap
  -> shared intake contract
  -> shared kernel flow
```

이 문서가 고정되면, 이후 구현은 "어디에 무엇을 둘지"를 다시 논쟁하지 않고 진행할 수 있다.
