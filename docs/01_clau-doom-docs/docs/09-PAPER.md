# 09 — 논문 구조

← [08-DASHBOARD](08-DASHBOARD.md) · [인덱스](../DOOM_ARENA_CLAUDE.md) · 다음 → [10-INFRA](10-INFRA.md)

---

## 대상 학회/저널

- 1차 타겟: NeurIPS / ICML (AI + 게임 에이전트 트랙)
- 2차 타겟: AAAI, IEEE Transactions on Games
- 산업공학 교차: IISE Transactions, Journal of Quality Technology (DOE 관점)

## 논문 제목 (후보)

- "clau-doom: Design of Experiments Meets LLM Agent Evolution in First-Person Shooters"
- "From OFAT to Factorial: Systematic Experimentation for Multi-Agent LLM Strategy Optimization"
- "LLM as Principal Investigator: Autonomous Experimental Design for Game-Playing Agent Swarms"

## 핵심 기여점 (Contribution)

1. **DOE + LLM 에이전트 최초 결합** — RL 없이 RAG + 산업공학 DOE로 에이전트 행동 최적화. 기존 LLM 에이전트 연구가 ad-hoc 실험에 의존한 것과 대비.

2. **LLM-as-PI 프레임워크** — LLM이 실험 대상이 아니라 실험을 설계/제어하는 PI 역할. DOE 설계, ANOVA 해석, 단계 전환까지 자율 수행.

3. **품질공학 기반 진화** — 단순 적합도(fitness) 대신 SPC/Cpk/SN비/TOPSIS로 다기준 부모 선택. 강건하고 안정적인 전략으로의 수렴.

4. **FPS 도메인의 체계적 실험** — 대부분 기존 연구가 Minecraft/텍스트 게임. FPS의 실시간성 + RAG 계층 분리가 고유 도전.

5. **재현 가능한 실험 프로토콜** — DOE 매트릭스, 시드 고정, 블록 설계로 완전한 재현성. 기존 LLM 에이전트 논문의 재현성 문제 해결.

## Research Questions

```
RQ1: DOE가 OFAT 대비 파라미터 탐색을 얼마나 가속하는가?
  - 학습 곡선 비교: Phase 0(OFAT) vs Phase 1(요인배치) 기울기
  - 동일 에피소드 수에서 발견한 유의 변수 개수 비교
  - 교호작용 발견율: OFAT = 0% vs DOE = ?%

RQ2: 품질공학 기반 부모 선택이 평균 기반 대비 우수한가?
  - A/B: 평균 kill rate 선택 vs TOPSIS 선택 vs SN비 선택
  - 세대별 성과 추이 + 분산 추이 비교
  - Cpk 수렴 속도 비교

RQ3: LLM-as-PI가 DOE 단계를 적절히 전환하는가?
  - PI의 Phase 전환 판단 vs 사후 최적 전환 시점 비교
  - PI가 설계한 매트릭스의 효율(D-efficiency) 평가
  - 인간 통계 전문가의 설계와 비교 (가능하면)

RQ4: FMEA 기반 가설 생성이 ad-hoc 대비 효과적인가?
  - RPN 상위 실패 모드 대상 실험의 채택률 vs 랜덤 가설 채택률
  - 세대별 RPN 총합 감소 추이

RQ5: 멀티 에이전트 간 지식 공유가 개별 학습 대비 유리한가?
  - 격리(NATS 차단) 에이전트 군 vs 공유 에이전트 군 비교
  - 전략 다양성(PCA 분산) 추이 비교
```

## Ablation Study 계획

```
각 구성요소의 기여를 격리하여 측정:

  - DOE off:     OFAT만 사용, 나머지 동일
  - SPC off:     관리도 모니터링 없이 진화
  - FMEA off:    랜덤 가설 순서, 우선순위 없음
  - TOPSIS off:  평균 kill rate만으로 부모 선택
  - RAG off:     룰엔진만 사용 (OpenSearch 비활성)
  - Share off:   NATS 차단, 개별 학습만
  - PI off:      고정 실험 스케줄, LLM PI 판단 없음

→ 7개 ablation × 5 세대 × 30 에피소드 = 논문 핵심 테이블
```

## 관련 연구

### 직접 관련 논문

1. **"Will GPT-4 Run DOOM?"** (de Wynter, 2024, IEEE Transactions on Games) — GPT-4가 스크린샷 텍스트 설명으로 Doom을 zero-shot 플레이. 메모리/학습 없음.

2. **Reflexion** (Shinn et al., NeurIPS 2023) — 가중치 업데이트 없이 언어적 피드백으로 에이전트 강화. 가장 가까운 선행 연구. 차이: 단일 에이전트 → 우리는 멀티 + 진화.

3. **Voyager** (Wang et al., NeurIPS 2023) — Minecraft에서 자동 커리큘럼 + 스킬 라이브러리. 스킬 라이브러리 ≈ 우리의 OpenSearch 전략 문서 풀. 차이: 코드 기반 스킬 → 우리는 문서 RAG 검색.

4. **RL-GPT** (Liu et al., NeurIPS 2024 Oral) — LLM+RL 2레벨 계층. 우리의 RAG+LLM 분리와 구조적 유사. 차이: RL 사용 → 우리는 RAG 대체.

5. **Agent-Pro** (Zhang et al., 2024) — 정책 수준 반성/최적화로 자가 진화.

6. **S-Agents** (2024) — 오픈 엔디드 환경에서 자기 조직화 에이전트.

### DOE / 품질공학 관련

7. **Taguchi Methods** (Taguchi, 1986) — 강건 설계, SN비, 직교배열.

8. **Response Surface Methodology** (Box & Wilson, 1951; Myers et al., 2016).

9. **Montgomery, "Design and Analysis of Experiments"** — DOE 표준 교과서.

10. **AutoML / Neural Architecture Search** — 하이퍼파라미터 최적화에 DOE 적용 선례. 우리와의 차이: NAS는 모델 구조, 우리는 에이전트 전략.

### 서베이

- "A Survey on Large Language Model-Based Game Agents" — LLM 게임 에이전트 6대 구성요소.
- BAAI-Agents/GPA-LM — LLM 기반 게임 에이전트 논문 큐레이션.

### 우리 프로젝트의 고유 포지셔닝

1. RL 없이 RAG + 경험 문서로 행동 개선 — verbal RL의 극단적 확장
2. 멀티 에이전트 간 지식 공유 + 자연선택 — 집단 진화
3. LLM을 PI로서 실험을 자율 설계/제어 — 기존 연구에서 거의 미탐색
4. FPS 도메인 적용 — 대부분 기존 연구는 Minecraft/텍스트 게임
5. 산업공학 DOE/품질공학의 AI 에이전트 연구 교차 적용 — 새로운 방법론 융합
