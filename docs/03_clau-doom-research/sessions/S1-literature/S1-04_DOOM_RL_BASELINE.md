# S1-04: Doom RL 베이스라인 문헌 수집

> **세션**: S1 (문헌 수집)
> **우선순위**: 🟡 medium
> **의존성**: 없음
> **상태**: ⬜ 미시작

---

## 목적

"RAG가 RL을 대체한다"는 주장을 하려면 기존 RL 에이전트의 성능 수준을 알아야 한다. VizDoom Competition 수상작과 DRL 기반 Doom AI 문헌을 수집하여, 나중에 clau-doom 에이전트의 성능 비교 기준점을 확보한다.

---

## 수집 대상 문헌 카테고리

### A. VizDoom Competition 수상작

**탐색 키워드**:
- VizDoom competition winner
- VizDoom AI competition
- visual doom AI competition results

**기대 수집 자료**:
- VizDoom 2016~2018 Competition 수상 팀 기술 보고서
- Lample & Chaplot (2017) — Playing FPS Games with Deep Reinforcement Learning (AAAI)
- Dosovitskiy & Koltun (2017) — Learning to Act by Predicting the Future

**clau-doom 연결점**:
- 이 논문들의 kill rate, survival time 등이 정량적 베이스라인
- 학습에 필요한 에피소드 수 / 시간 대비 clau-doom의 학습 효율 비교 가능

---

### B. DRL 기반 FPS AI

**탐색 키워드**:
- deep reinforcement learning FPS
- doom reinforcement learning
- first-person shooter AI deep learning

**기대 수집 논문**:
- Kempka et al. (2016) — VizDoom: A Doom-based AI Research Platform
- Wu & Tian (2017) — Training Agent for FPS Game with Actor-Critic Curriculum Learning
- 최신 VizDoom DRL 연구

**clau-doom 연결점**:
- VizDoom 플랫폼의 standard scenario별 RL 성능 수치 확보
- 같은 시나리오에서 clau-doom을 테스트하면 직접 비교 가능
- 학습 곡선 (에피소드 vs 성능) 비교 → RAG 기반 학습 효율 주장 근거

---

### C. "Will GPT-4 Run DOOM?" 후속/관련 연구

**탐색 키워드**:
- LLM game playing FPS
- GPT Doom
- language model video game

**기대 수집 논문**:
- de Wynter (2024) — 이미 수집됨, 여기서는 후속 연구 및 반응 조사
- LLM + FPS 조합의 최신 시도

**clau-doom 연결점**:
- de Wynter의 zero-shot 접근 대비 clau-doom의 RAG + 경험 축적이 얼마나 개선되는지
- "LLM만으로는 한계, 구조적 보완이 필요하다"는 논점 강화

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | 문헌 탐색 총괄, 정량 수치 추출 |
| Sub-agent A | 카테고리 A: VizDoom Competition 서치 |
| Sub-agent B | 카테고리 B + C: DRL FPS + LLM FPS 서치 |

---

## 특별 요구 사항

이 태스크는 **정량적 수치 추출**이 핵심이다. 각 논문에서 다음을 반드시 기록:

```
### [논문 제목]
- **시나리오**: 어떤 VizDoom 시나리오에서 테스트했는가
- **성능 수치**: kill rate, survival time, score 등
- **학습 조건**: 에피소드 수, 학습 시간, 하드웨어
- **모델 구조**: 네트워크 아키텍처 요약
```

이 수치들이 S2-01(평가 베이스라인 정의)에서 직접 활용됨.

---

## 완료 기준

- [ ] VizDoom Competition 수상작 최소 2편 수집 + 성능 수치 추출
- [ ] DRL 기반 Doom AI 최소 2편 수집 + 성능 수치 추출
- [ ] standard scenario별 베이스라인 수치 테이블 작성
- [ ] Lead 검수 완료
