# S3-03: OpenSearch kNN 검색 레이턴시 검증

> **세션**: S3 (기술 검증)
> **우선순위**: 🟠 high
> **의존성**: 없음
> **상태**: ⬜ 미시작

---

## 목적

설계 문서에서 "OpenSearch kNN 검색 ~20ms, Level 2 전체 < 100ms"를 주장하고 있다. 실제 전략 문서 1000개 기준으로 이 수치가 달성 가능한지 실측한다.

---

## 검증 항목

### 1. OpenSearch 컨테이너 기본 동작

- [ ] Docker Compose로 OpenSearch 단일 노드 기동
- [ ] 인덱스 생성 (kNN 벡터 필드 포함)
- [ ] 문서 색인 / 검색 기본 동작

### 2. kNN 벡터 검색 레이턴시

**테스트 조건**:

| 변수 | 값 |
|------|-----|
| 문서 수 | 100, 500, 1000, 5000 |
| 벡터 차원 | 384 (MiniLM), 768 (larger model) |
| Top-K | 5, 10, 20 |
| kNN 알고리즘 | HNSW (기본) |
| HNSW 파라미터 | ef_search: 100, 256, 512 |

**측정**: 각 조합에서 100회 검색의 p50, p90, p99 레이턴시

### 3. 전략 문서 구조 색인

실제 설계의 전략 문서 구조로 테스트:

```json
{
  "doc_id": "tactic_test_001",
  "agent_id": "PLAYER_001",
  "generation": 1,
  "situation_embedding": [/* 384 or 768 dims */],
  "situation_tags": ["narrow_corridor", "multi_enemy"],
  "decision": { "tactic": "retreat_and_funnel", "weapon": "shotgun" },
  "quality": { "success_rate": 0.84, "sample_size": 47, "confidence_tier": "high" }
}
```

### 4. 하이브리드 검색

kNN + 필터(generation, confidence_tier) 조합 검색의 레이턴시 추가 측정

---

## 성능 기준

| 항목 | 통과 기준 | 목표 |
|------|----------|------|
| 1000 문서 kNN p50 | < 50ms | < 20ms |
| 1000 문서 kNN p99 | < 100ms | < 50ms |
| 5000 문서 kNN p50 | < 100ms | < 50ms |
| 하이브리드 검색 p50 | < 100ms | < 50ms |

**통과 기준 미달 시**: HNSW 파라미터 튜닝, 또는 DuckDB Level 1 캐시 의존도를 높이는 방향으로 아키텍처 조정

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | 벤치마크 설계, 결과 분석 |
| Sub-agent A | OpenSearch 컨테이너 구성 + 인덱스 설계 |
| Sub-agent B | 더미 전략 문서 생성 + 벤치마크 실행 |

---

## 완료 기준

- [ ] OpenSearch 컨테이너 기동 + kNN 인덱스 생성
- [ ] 문서 수 × 차원 × Top-K 조합 레이턴시 테이블
- [ ] 하이브리드 검색 레이턴시 측정
- [ ] 통과/미달 판정 + 미달 시 대응 방안
- [ ] Lead 검수 완료
