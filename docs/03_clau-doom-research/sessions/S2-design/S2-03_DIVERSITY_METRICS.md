# S2-03: 진화 수렴/다양성 측정 지표 설계

> **세션**: S2 (연구 설계 보강)
> **우선순위**: 🟠 high
> **의존성**: 없음 (S1-01 QD 문헌 있으면 유리)
> **상태**: ⬜ 미시작

---

## 목적

세대 진화가 조기 수렴(premature convergence)하는지, 전략 다양성이 유지되는지를 측정하는 지표가 없다. QD 문헌을 참조하여 clau-doom에 적합한 다양성 지표를 설계하고, DuckDB 스키마에 매핑한다.

---

## 설계할 지표

### 1. 전략 분포 엔트로피

**정의**: 세대 내 에이전트들의 play_style, weapon_preference 등 전략 파라미터 분포의 Shannon 엔트로피

**수식**: H = -Σ p(x) log₂ p(x)

**측정 대상**:
- play_style 분포 (aggressive, balanced, defensive, …)
- retreat_threshold 분포 (연속값 → 구간 이산화)
- 자주 사용하는 전략 문서 Top-10의 다양성

**해석**: 엔트로피 감소 = 수렴 진행 중, 엔트로피 유지/증가 = 다양성 유지

---

### 2. 행동 공간 커버리지 (Behavioral Coverage)

**정의**: 전체 가능한 상황-행동 조합 중 세대 내 에이전트들이 실제로 사용한 비율

**측정 방법**:
- situation_tags × decision.tactic 조합을 그리드화
- 세대 내 전체 교전에서 관찰된 (상황, 행동) 셀 수 / 전체 셀 수

**해석**: 커버리지 감소 = 행동 패턴 단순화, 특정 전략에 고착

---

### 3. QD-Score (Quality-Diversity Score)

**정의**: MAP-Elites에서 차용. 행동 공간의 각 셀에서 최고 성과의 합.

**수식**: QD-Score = Σ (occupied cells) best_fitness(cell)

**clau-doom 적용**:
- 셀 = (situation_tag 조합) → 이산화된 상황 공간
- fitness = encounter_success_rate
- QD-Score 증가 = 다양한 상황에서 골고루 잘하는 세대

---

### 4. 전략 문서 풀 다양성

**정의**: OpenSearch 내 전략 문서들의 임베딩 공간에서의 분산

**측정 방법**:
- 전체 문서 임베딩의 평균 쌍별 코사인 거리
- 또는 임베딩의 주성분 분석(PCA) 후 설명된 분산 비율

**해석**: 평균 거리 감소 = 문서들이 비슷해지고 있음 (다양성 손실)

---

### 5. 세대 간 변이율

**정의**: 세대 N과 N+1 사이 MD 파일의 변경 비율

**측정 방법**:
- Strategy Profile 파라미터의 변화량
- Learned Rules의 추가/삭제/수정 수
- 부모-자식 간 전략 문서 코사인 유사도

**해석**: 변이율이 0에 수렴하면 진화 정체

---

## DuckDB 스키마 매핑

```sql
-- 세대별 다양성 지표 테이블
CREATE TABLE generation_diversity (
    generation_id INT,
    strategy_entropy FLOAT,
    behavioral_coverage FLOAT,
    qd_score FLOAT,
    doc_pool_avg_distance FLOAT,
    mutation_rate FLOAT,
    num_agents INT,
    num_unique_strategies INT,
    measured_at TIMESTAMP
);

-- 세대별 전략 분포 상세
CREATE TABLE generation_strategy_distribution (
    generation_id INT,
    parameter_name VARCHAR,   -- 'play_style', 'retreat_threshold', etc.
    parameter_value VARCHAR,  -- 이산화된 값
    count INT,
    proportion FLOAT
);
```

---

## 조기 수렴 경보 조건

| 지표 | 경보 조건 | 대응 |
|------|----------|------|
| 전략 엔트로피 | 3세대 연속 감소 | exploration 비율 증가 (30% → 50%) |
| 행동 커버리지 | 이전 세대 대비 20% 이상 감소 | 새로운 상황 탐색 실험 강제 |
| QD-Score | 정체 (5세대 동안 < 5% 증가) | 변이 강도 증가 |
| 세대 간 변이율 | < 5% | 교차 연산 다양화, 외부 전략 주입 |

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | 지표 설계 총괄, DuckDB 스키마 검수 |
| Sub-agent A | QD 문헌에서 지표 추출 (S1-01 결과 참조) |
| Sub-agent B | DuckDB 스키마 매핑 + 경보 조건 설계 |

---

## 완료 기준

- [ ] 5개 지표 각각의 정의, 수식, 측정 방법 확정
- [ ] DuckDB 스키마 확장 SQL 작성
- [ ] 조기 수렴 경보 조건 테이블 완성
- [ ] 대시보드 Evolution 탭에 표시할 차트 스펙 정의
- [ ] Lead 검수 완료
