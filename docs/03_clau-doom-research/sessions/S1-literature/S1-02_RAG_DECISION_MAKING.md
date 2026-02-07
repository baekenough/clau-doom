# S1-02: RAG for Decision-Making 문헌 수집

> **세션**: S1 (문헌 수집)
> **우선순위**: 🔴 critical
> **의존성**: 없음
> **상태**: ⬜ 미시작

---

## 목적

RAG를 "실시간 행동 선택"에 쓰는 것이 프로젝트의 가장 비정통적인 설계 결정이다. 현재 문헌(Reflexion, Voyager)은 self-reflection/skill library 쪽이며, 검색 기반 의사결정 자체를 다루는 선행 연구가 부족하다. 이 축을 보강하여 "RAG가 RL을 대체할 수 있는가"라는 주장의 학술적 근거를 확보한다.

---

## 수집 대상 문헌 카테고리

### A. Retrieval-Augmented Decision Making

**왜 필요한가**: clau-doom의 핵심 메커니즘 — OpenSearch kNN 검색 → Rust 스코어링 → 액션 선택 — 이 "검색으로 정책을 대체한다"는 주장의 직접적 선행 연구.

**탐색 키워드**:
- retrieval-augmented decision making
- retrieval-augmented reinforcement learning
- kNN policy / nearest neighbor policy
- episodic memory reinforcement learning

**기대 수집 논문**:
- Humphreys et al. (2022) — Large-Scale Retrieval for Reinforcement Learning
- Goyal et al. (2022) — Retrieval-Augmented Reinforcement Learning
- Blundell et al. (2016) — Model-Free Episodic Control (NEC)
- Pritzel et al. (2017) — Neural Episodic Control

**clau-doom 연결점**:
- OpenSearch kNN 검색 ≈ episodic memory의 k-nearest lookup
- 전략 문서의 success_rate ≈ episodic control의 Q-value 추정
- 윌슨 스코어 하한 ≈ 불확실성 보정된 가치 추정

---

### B. Decision Transformer / Sequence Model 기반 의사결정

**왜 필요한가**: Transformer를 의사결정에 쓰는 접근은 RL 대안으로서의 sequence modeling. clau-doom의 "경험 문서를 검색해서 의사결정"과 구조적 유사성이 있음.

**탐색 키워드**:
- Decision Transformer
- offline reinforcement learning sequence model
- in-context learning reinforcement learning

**기대 수집 논문**:
- Chen et al. (2021) — Decision Transformer
- Janner et al. (2021) — Trajectory Transformer
- Lee et al. (2024) — Supervised Pretraining Can Learn In-Context RL
- Laskin et al. (2022) — In-context RL with Algorithm Distillation

**clau-doom 연결점**:
- Decision Transformer가 "과거 trajectory를 조건으로 행동 생성" → clau-doom은 "과거 전략 문서를 검색해서 행동 선택"
- 차이: DT는 학습된 모델, clau-doom은 검색 + 스코어링 (학습 없음)

---

### C. RETRO / Retrieval-Augmented Generation 계열

**왜 필요한가**: RAG의 원류 연구. 생성이 아닌 의사결정에 RAG를 쓰는 clau-doom의 확장이 어떤 위치인지 포지셔닝 필요.

**탐색 키워드**:
- RETRO retrieval enhanced transformer
- RAG beyond generation
- retrieval augmented agent

**기대 수집 논문**:
- Borgeaud et al. (2022) — RETRO
- Lewis et al. (2020) — RAG 원논문
- RAG를 에이전트 의사결정에 적용한 최신 연구

**clau-doom 연결점**:
- RAG 원논문이 "생성 품질 향상"을 위한 것 → clau-doom은 "행동 품질 향상"으로 확장
- RETRO의 chunked retrieval ≈ clau-doom의 상황별 전략 문서 검색

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | 문헌 탐색 총괄, clau-doom과의 포지셔닝 정리 |
| Sub-agent A | 카테고리 A: Retrieval-Augmented RL 서치 |
| Sub-agent B | 카테고리 B + C: DT 계열 + RETRO 계열 서치 |

---

## 산출물 형식

```
### [논문 제목] (저자, 연도, 학회)
- **핵심 내용**: 1~2문장 요약
- **clau-doom 연결점**: 우리 프로젝트와의 관계
- **차별점**: 우리가 다르게 하는 부분
- **참고 여부**: 직접 인용 / 배경 참고 / 방법론 차용
```

---

## 완료 기준

- [ ] 카테고리 A에서 최소 3편 수집
- [ ] 카테고리 B에서 최소 2편 수집
- [ ] 카테고리 C에서 최소 2편 수집
- [ ] "RAG가 RL을 대체한다"는 주장의 학술적 포지셔닝 문장 작성
- [ ] Lead 검수 완료
