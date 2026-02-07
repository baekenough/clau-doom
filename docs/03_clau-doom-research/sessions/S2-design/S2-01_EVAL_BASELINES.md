# S2-01: 평가 베이스라인 정의

> **세션**: S2 (연구 설계 보강)
> **우선순위**: 🔴 critical
> **의존성**: 없음 (S1-04 결과 있으면 유리)
> **상태**: ⬜ 미시작

---

## 목적

현재 설계에 kill rate, survival time 등 메트릭은 있지만 "무엇과 비교하는가"가 빠져 있다. 실험 설계 진입 전에 3종 베이스라인을 정의하여, clau-doom 에이전트의 성과를 객관적으로 평가할 기준을 확보한다.

---

## 정의할 베이스라인 3종

### Baseline 1: Random Agent

**정의**: 매 틱마다 가능한 액션 중 균일 랜덤 선택

**목적**: 하한선. 어떤 전략이든 랜덤보다는 나아야 한다.

**구현 복잡도**: 최소. Rust에서 rand::random()으로 액션 선택.

**측정 항목**: survival_time, kills, damage_taken, exploration_coverage

**예상 수치**: VizDoom basic 시나리오에서 극히 낮은 성과

---

### Baseline 2: Rule-Only Agent (RAG 없이 MD 룰만)

**정의**: DOOM_PLAYER.MD의 Learned Rules만 사용, OpenSearch 검색 없음. 의사결정 계층에서 Level 0만 활성화.

**목적**: RAG 검색의 순수 기여분 측정. Rule-Only vs Full Agent의 차이 = RAG의 가치.

**구현 복잡도**: 중간. 기존 에이전트에서 RAG 호출만 비활성화.

**측정 항목**: 동일 메트릭 + RAG 호출 없음 확인

**설계 포인트**:
- 동일 MD 파일 사용 (Learned Rules 섹션만 활성)
- 동일 시드, 동일 시나리오
- MD 룰의 커버리지(매칭률)도 함께 기록

---

### Baseline 3: RL Agent (외부 참조)

**정의**: VizDoom Competition 수상작 또는 공개된 DRL 에이전트의 보고 성능 수치 참조

**목적**: 기존 SOTA와의 비교. "RAG가 RL을 대체할 수 있는가"에 대한 답.

**구현 복잡도**: 직접 구현하지 않음 (문헌 수치 참조). 가능하면 공개 코드로 재현.

**데이터 소스**: S1-04(Doom RL 베이스라인 문헌)에서 추출

**주의**: 시나리오/조건이 다르면 직접 비교 불가. 동일 시나리오에서의 수치만 사용.

---

## 측정 프레임워크

### 공통 메트릭 (모든 베이스라인 동일 기준)

| 메트릭 | 설명 | 단위 |
|--------|------|------|
| survival_time | 에피소드 내 생존 시간 | 초 (게임 틱 → 초 변환) |
| kills | 에피소드 내 처치 수 | 정수 |
| damage_taken | 에피소드 내 누적 피해량 | HP |
| ammo_efficiency | 발사 대비 명중률 | 비율 (0~1) |
| exploration_coverage | 맵 탐색 커버리지 | 비율 (0~1) |
| encounter_success_rate | 교전 승리율 | 비율 (0~1) |

### 비교 방법

- 동일 시나리오, 동일 시드 세트에서 최소 30 에피소드
- Welch's t-test 또는 Mann-Whitney U (비정규 분포 시)
- 효과 크기 (Cohen's d) 보고
- 95% 신뢰구간 함께 보고

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | 베이스라인 설계 총괄, 비교 방법 확정 |
| Sub-agent A | Baseline 1, 2 스펙 정의 + 구현 방안 |
| Sub-agent B | Baseline 3 — S1-04 결과 참조하여 RL 수치 정리 |

---

## 완료 기준

- [ ] Baseline 1 (Random) 스펙 확정
- [ ] Baseline 2 (Rule-Only) 스펙 확정 + RAG 비활성화 방법 정의
- [ ] Baseline 3 (RL) 참조 수치 테이블 (시나리오별)
- [ ] 비교 통계 방법 확정 (검정, 효과 크기, 신뢰구간)
- [ ] DuckDB experiments 테이블에 baseline_type 컬럼 추가 스펙
- [ ] Lead 검수 완료
