# P-02: Will GPT-4 Run DOOM?

## 서지 정보

| 항목 | 내용 |
|------|------|
| 저자 | Adrian de Wynter |
| 발표 | IEEE Transactions on Games, 2024 |
| 소속 | University of York (Microsoft 겸직) |
| arXiv | [2403.05468](https://arxiv.org/abs/2403.05468) |
| IEEE | [10.1109/TG.2024.3497321](https://ieeexplore.ieee.org/document/10752360/) |
| GitHub | [adewynter/Doom](https://github.com/adewynter/Doom) |
| 프로젝트 페이지 | [adewynter.github.io/Doom](https://adewynter.github.io/Doom) |

---

## 핵심 아이디어

GPT-4(V)가 Doom(E1M1: Hangar)을 zero-shot으로 플레이할 수 있는지 실험. 스크린샷을 텍스트 설명으로 변환한 뒤 GPT-4에게 행동을 결정하게 하는 Vision+Agent 파이프라인 구성.

---

## 아키텍처

```
VizDoom 엔진 (C, Matplotlib)
    │ 스크린샷
    ▼
Vision 컴포넌트 (GPT-4V)
    │ 구조화된 게임 상태 텍스트 설명
    ▼
Agent 컴포넌트 (GPT-4)
    │ 행동 결정 + 이전 히스토리
    ▼
Manager 레이어 (Python)
    │ 키스트로크 커맨드로 변환
    ▼
VizDoom 엔진 (액션 실행)
```

---

## 주요 발견

### 할 수 있는 것
- 문 조작 (열기/통과)
- 적 전투 (발견 시 사격)
- 기본 경로 탐색 (pathing)
- 워크스루 지시문을 컨텍스트로 제공하면 성능 향상

### 할 수 없는 것 (핵심 한계)

| 한계 | 설명 | clau-doom 해결 방식 |
|------|------|---------------------|
| **적 망각** | 좀비가 시야에서 사라지면 존재 자체를 잊어버림 | OpenSearch에 적 위치/상태 기록, 지속적 상황 인식 |
| **벽 끼임** | 모서리에 끼여 빠져나오지 못하고 사망 | Rust 룰엔진에 stuck detection + 회피 기동 하드코딩 |
| **산성 풀 망각** | 산성 풀에 빠져도 데미지 원인을 잊어버림 | DuckDB에 환경 위험 기록, Level 0 룰로 즉시 대응 |
| **학습 불가** | 50-60회 실행에서도 동일 실수 반복 | 에피소드 회고 → MD 업데이트 → 전략 문서 축적 |
| **환각** | 행동을 수행했다고 거짓 보고 | 실시간 판단에 LLM 호출 없음 (RAG+Rust) |
| **입력 크기 제한** | 긴 히스토리 유지 불가 | RAG로 관련 경험만 선택적 검색 |

### 프롬프팅 전략 비교

- 단일 모델 호출 < 다중 모델 호출 (Vision+Agent 분리)
- 워크스루 제공 시 성능 향상 → 외부 지식의 중요성 입증

---

## clau-doom과의 관계

### 이 논문이 증명한 것 (우리에게 유리한 증거)

1. **LLM이 FPS를 이해할 수 있다** — zero-shot으로도 기본 행동 가능
2. **외부 지식이 성능을 높인다** — 워크스루 제공 효과 → RAG의 가치 입증
3. **메모리 없이는 한계가 명확하다** — 경험 축적의 필요성 입증

### clau-doom이 이 연구의 모든 한계를 해결하는 방식

```
GPT-4 Doom 한계          → clau-doom 해결
─────────────────────────────────────────
메모리 없음              → OpenSearch + DuckDB + MD
학습 없음                → 에피소드 회고 + 세대 진화
단일 에이전트             → 멀티 에이전트 + 지식 공유
실시간 LLM 호출 (느림)    → RAG + Rust (100ms 이내)
환각 문제                → 실시간에서 LLM 제거
히스토리 크기 제한        → 벡터 검색으로 관련 경험만 검색
```

### 벤치마크 활용

이 논문의 E1M1 실험 설정을 clau-doom의 초기 베이스라인으로 활용 가능:
- 동일 맵(E1M1: Hangar)에서 시작
- GPT-4 zero-shot 성과를 기준점으로 설정
- clau-doom 세대별 성과 향상을 비교

---

## 기술적 참고사항

- VizDoom Python 바인딩 + Matplotlib으로 렌더링 관리
- 스크린샷 → 텍스트 변환에 GPT-4V 사용 (clau-doom은 직접 게임 상태 API 사용 예정)
- 키스트로크 커맨드 매핑 체계가 잘 정리되어 있음

---

## 주요 인용 메모

- "GPT-4 forgets about the zombie and just keeps going"
- "it is quite worrisome how easy it was for the model to accurately shoot something without second-guessing the instructions"
- E1M1 마지막 방까지 도달한 것은 50-60회 중 단 1회

---

## 프로젝트 적용 체크리스트

- [x] E1M1을 초기 실험 맵으로 선정 근거
- [x] zero-shot 베이스라인 비교 기준 확보
- [ ] GPT-4 Doom의 행동 로그 공개 여부 확인 → 구체적 비교 데이터 확보
- [ ] Vision 컴포넌트 vs 직접 API 상태 추출 성능 비교 실험 설계
