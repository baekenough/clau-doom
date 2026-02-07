# S1-01: 진화/집단지능 문헌 수집

> **세션**: S1 (문헌 수집)
> **우선순위**: 🔴 critical
> **의존성**: 없음
> **상태**: ⬜ 미시작

---

## 목적

프로젝트의 핵심 기여 중 하나인 "멀티 에이전트 간 지식 공유 + 자연선택"을 뒷받침할 선행 연구를 수집한다. 현재 관련 연구 섹션에 이 축의 문헌이 전무하여 진화 메커니즘 설계의 이론적 근거가 부족한 상태.

---

## 수집 대상 문헌 카테고리

### A. Quality-Diversity / MAP-Elites 계열

**왜 필요한가**: clau-doom의 세대 진화에서 교차/변이 알고리즘의 이론적 근거. 전략 다양성을 유지하면서 성과를 높이는 방법론.

**탐색 키워드**:
- Quality-Diversity optimization
- MAP-Elites
- behavioral diversity preservation
- novelty search + fitness

**기대 수집 논문**:
- Mouret & Clune (2015) — MAP-Elites 원논문
- Cully et al. (2015) — 로봇 적응에 QD 적용
- Fontaine & Nikolaidis (2023) — Differentiable QD
- 최신 QD + LLM 조합 연구 (있다면)

**clau-doom 연결점**:
- 세대 진화 시 엘리트 보존 + 변이의 밸런스 → QD의 archive 메커니즘
- 전략 분포 다양성 측정 → QD-score 활용 가능
- 조기 수렴 방지 → novelty bonus 적용 여부

---

### B. LLM 기반 진화 최적화

**왜 필요한가**: clau-doom의 MD 파일 교차/변이가 본질적으로 "텍스트를 진화시키는" 행위. LLM 출력을 교차/변이하는 기존 접근과 직접 비교 필요.

**탐색 키워드**:
- EvoPrompting
- FunSearch
- LLM evolutionary optimization
- prompt evolution

**기대 수집 논문**:
- Chen et al. (2023) — EvoPrompting: Language Models for Code-Level Neural Architecture Search
- Romera-Paredes et al. (Nature, 2024) — FunSearch: Mathematical discoveries from program search with LLMs
- Lehman et al. (2023) — Evolution through Large Models
- Meyerson et al. (2023) — Language Model Crossover

**clau-doom 연결점**:
- MD 파일 교차 ≈ EvoPrompting의 프롬프트 교차
- 전략 문서의 변이 ≈ FunSearch의 프로그램 변이
- "Evolution through Large Models" 프레임워크와의 직접 비교

---

### C. 멀티 에이전트 협업/경쟁 학습

**왜 필요한가**: 에이전트 간 NATS를 통한 지식 공유와 자연선택의 효과를 논하려면 비교 기준이 필요.

**탐색 키워드**:
- multi-agent reinforcement learning knowledge sharing
- emergent behavior multi-agent
- cooperative multi-agent learning
- population-based training

**기대 수집 논문**:
- Baker et al. (2019) — OpenAI hide-and-seek emergent behavior
- Jaderberg et al. (2019) — Population-Based Training (PBT)
- MARL 서베이 (최신)
- 지식 공유/distillation 관련 MARL 연구

**clau-doom 연결점**:
- NATS pub/sub 노하우 공유 ≈ PBT의 hyperparameter 전파
- 세대 진화 ≈ PBT의 population-level selection
- 에이전트 간 전략 문서 공유 ≈ knowledge distillation

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | 문헌 탐색 총괄, 중복 제거, clau-doom 연결점 검수 |
| Sub-agent A | 카테고리 A: QD/MAP-Elites 서치 |
| Sub-agent B | 카테고리 B: LLM 진화 최적화 서치 |
| Sub-agent C | 카테고리 C: MARL 협업/경쟁 서치 |

---

## 산출물 형식

각 논문에 대해:

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
- [ ] 카테고리 B에서 최소 3편 수집
- [ ] 카테고리 C에서 최소 2편 수집
- [ ] 각 논문의 clau-doom 연결점 기술 완료
- [ ] Lead 검수 완료
