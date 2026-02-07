# S2-02: 핵심 가정 검증 계획 (Ablation 설계)

> **세션**: S2 (연구 설계 보강)
> **우선순위**: 🟠 high
> **의존성**: 없음
> **상태**: ⬜ 미시작

---

## 목적

프로젝트의 핵심 가정 **"에이전트 실력 = OpenSearch 문서 품질 × Rust 스코어링 정확도"**를 검증할 수 있는 ablation 실험을 설계한다. 이 가정이 검증되지 않으면 전체 피드백 루프의 근거가 흔들린다.

---

## Ablation 실험 설계

### Ablation 1: 문서 품질 변수 조작

**가설**: 전략 문서의 품질이 높을수록 에이전트 성과가 향상된다.

**조작 방법**:
- **High Quality**: 정상 운영 (LLM이 정제한 전략 문서)
- **Degraded Quality**: 문서의 situation_tags를 랜덤 셔플하여 의미적 정합성 파괴
- **No Documents**: OpenSearch를 비우고 Level 0 룰만으로 플레이 (= Baseline 2)

**측정**: 동일 시드, 동일 시나리오에서 3조건 비교

**예상 결과**: High > Degraded > No Documents 순서로 성과 하락

**검증 실패 시 의미**: 문서 품질이 성과와 무관하면, RAG 파이프라인 전체 재설계 필요

---

### Ablation 2: 스코어링 가중치 변수 조작

**가설**: Rust 스코어링의 가중치(유사도 0.4, 신뢰도 0.4, 최신성 0.2)가 성과에 영향을 미친다.

**조작 방법**:
- **Optimized**: 현재 가중치 (0.4, 0.4, 0.2)
- **Similarity Only**: (1.0, 0.0, 0.0) — 유사도만
- **Confidence Only**: (0.0, 1.0, 0.0) — 신뢰도만
- **Random Score**: kNN Top-K에서 랜덤 선택

**측정**: 동일 문서 풀, 동일 시드에서 4조건 비교

**예상 결과**: Optimized > 단일 가중치 > Random 순서

**검증 실패 시 의미**: 가중치 조합이 무의미하면 스코어링 단순화 가능 (복잡도 감소)

---

### Ablation 3: RAG 계층 기여도

**가설**: 의사결정 계층의 각 레벨이 독립적으로 성과에 기여한다.

**조작 방법**:
- **Full Stack**: Level 0 + 1 + 2 (MD 룰 + DuckDB + OpenSearch)
- **Level 0 Only**: MD 하드코딩 룰만
- **Level 0 + 1**: MD 룰 + DuckDB 캐시
- **Level 2 Only**: OpenSearch kNN만 (MD 룰 무시)

**측정**: 각 조건에서 룰 매칭률, RAG 호출률, 평균 응답 시간도 함께 기록

**예상 결과**: Full Stack > Level 0+1 > Level 0 Only, Level 2 Only의 위치는 미지수

---

## 실험 실행 정책 (기존 설계와 일관)

- 시드 고정, 변수 격리
- 조건당 최소 30 에피소드
- 교전 단위 기록 필수 (어떤 교전에서 어떤 계층이 사용되었는지)
- p < 0.05 유의 수준

---

## DuckDB 스키마 확장 필요사항

```sql
-- ablation 실험용 컬럼 추가
ALTER TABLE experiments ADD COLUMN ablation_condition VARCHAR;
-- 'full', 'degraded_docs', 'no_docs', 'sim_only', 'conf_only', 'random_score',
-- 'level0_only', 'level01', 'level2_only'

ALTER TABLE encounters ADD COLUMN decision_level INT;
-- 0: MD rule, 1: DuckDB cache, 2: OpenSearch kNN
```

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | ablation 전체 설계, 조건 간 직교성 확인 |
| Sub-agent A | Ablation 1: 문서 품질 조작 방법 상세화 |
| Sub-agent B | Ablation 2: 스코어링 가중치 조합 + Ablation 3 설계 |

---

## 완료 기준

- [ ] Ablation 1, 2, 3 각각의 조작/측정/분석 방법 확정
- [ ] DuckDB 스키마 확장 스펙 작성
- [ ] 실험 실행 순서 (어떤 ablation을 먼저 할지) 결정
- [ ] 검증 실패 시 대응 계획 기술
- [ ] Lead 검수 완료
