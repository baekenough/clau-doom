# S1-03: LLM-as-Scientist 문헌 수집

> **세션**: S1 (문헌 수집)
> **우선순위**: 🟡 medium
> **의존성**: 없음
> **상태**: ⬜ 미시작

---

## 목적

"LLM을 PI로서 실험을 자율 설계/제어"가 고유 기여점으로 제시되어 있으나, 이 방향의 선행 연구 조사가 없다. LLM이 과학적 탐구를 수행하는 기존 연구와 비교하여 clau-doom의 PI 구조가 어디가 새로운지를 명확히 한다.

---

## 수집 대상 문헌 카테고리

### A. LLM-as-Scientist / Autonomous Research

**탐색 키워드**:
- AI scientist autonomous research
- LLM hypothesis generation
- automated scientific discovery
- LLM experiment design

**기대 수집 논문**:
- Lu et al. (2024) — The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery (Sakana AI)
- Boiko et al. (2023) — Autonomous chemical research with large language models
- Yang et al. (2024) — LLM-based hypothesis generation

**clau-doom 연결점**:
- AI Scientist가 "가설 → 실험 → 논문" 전체 파이프라인 자동화 → clau-doom의 Opus PI도 유사하지만 도메인이 게임 AI
- 차이: AI Scientist는 단발성, clau-doom의 PI는 세대를 걸쳐 누적적 연구 수행
- 차이: clau-doom은 PI(Opus)와 실행자(Claude Code)를 분리, AI Scientist는 단일 모델

---

### B. Hypothesis Search / Automated Experimentation

**탐색 키워드**:
- hypothesis search LLM
- automated experimentation AI
- self-improving AI systems

**기대 수집 논문**:
- FunSearch (Romera-Paredes et al., 2024) — 이미 S1-01과 중복, 여기서는 "탐색 전략" 측면에서 분석
- 자율 실험 설계 관련 최신 연구

**clau-doom 연결점**:
- Opus PI의 메타 실험("어떤 종류의 실험이 효과적인가") ≈ hypothesis search의 search strategy
- exploitation vs exploration 밸런스 제어

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | 문헌 탐색 총괄 |
| Sub-agent A | 카테고리 A: LLM-as-Scientist 서치 |
| Sub-agent B | 카테고리 B: Hypothesis Search 서치 |

---

## 완료 기준

- [ ] 카테고리 A에서 최소 2편 수집
- [ ] 카테고리 B에서 최소 1편 수집
- [ ] clau-doom PI 구조의 고유성 주장 문장 작성
- [ ] Lead 검수 완료
