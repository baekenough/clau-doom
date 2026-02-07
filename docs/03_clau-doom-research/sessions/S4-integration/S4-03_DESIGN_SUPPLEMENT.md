# S4-03: 연구 설계 보강 사항 문서화

> **세션**: S4 (문서 통합)
> **우선순위**: 🟠 high
> **의존성**: S2-01, S2-02, S2-03, S2-04 전체 완료
> **상태**: ⬜ 미시작 (차단됨)

---

## 목적

S2의 연구 설계 보강 결과(베이스라인, ablation, 다양성 지표, Agent Teams 워크플로)를 DOOM_ARENA_DESIGN.md에 공식 반영한다.

---

## 추가/확장할 섹션

### 1. 평가 프레임워크 섹션 (신규)

S2-01 결과 반영. 현재 "실험 구조" 섹션 뒤에 추가:

```markdown
## 평가 프레임워크

### 베이스라인 3종
- Baseline 1: Random Agent — [스펙]
- Baseline 2: Rule-Only Agent — [스펙]  
- Baseline 3: RL Agent (참조) — [수치 테이블]

### 비교 통계 방법
- [검정 방법, 효과 크기, 신뢰구간]
```

### 2. Ablation 실험 계획 섹션 (신규)

S2-02 결과 반영:

```markdown
## Ablation 실험 계획

### 핵심 가정 검증
- Ablation 1: 문서 품질 변수 조작
- Ablation 2: 스코어링 가중치 변수 조작
- Ablation 3: RAG 계층 기여도
```

### 3. 진화 다양성 모니터링 섹션 (신규)

S2-03 결과 반영:

```markdown
## 진화 다양성 모니터링

### 측정 지표 5종
- 전략 분포 엔트로피
- 행동 공간 커버리지
- QD-Score
- 전략 문서 풀 다양성
- 세대 간 변이율

### 조기 수렴 경보 조건
[테이블]
```

### 4. Agent Teams 운용 섹션 (PI 구조 내 확장)

S2-04 결과 반영. 기존 "PI 구조" 섹션 확장:

```markdown
### Agent Teams 운용

#### 세션 구조
[4세션 × 팀 × 서브 구조]

#### 파일 소유권 규칙
[매트릭스]

#### 폴백 전략
[테이블]
```

### 5. DuckDB 스키마 확장 (기존 "측정 체계" 섹션 확장)

S2-02, S2-03에서 정의한 신규 테이블/컬럼 반영:

```markdown
- generation_diversity 테이블
- generation_strategy_distribution 테이블
- experiments.ablation_condition 컬럼
- encounters.decision_level 컬럼
```

---

## 팀 구성 (Agent Teams)

| 역할 | 담당 범위 |
|------|----------|
| Lead | DESIGN.md 최종 통합, 기존 섹션과의 일관성 검수 |
| Sub-agent A | 섹션 1, 2, 3 작성 (평가/ablation/다양성) |
| Sub-agent B | 섹션 4, 5 작성 (Agent Teams/DuckDB) |

---

## 완료 기준

- [ ] 5개 신규/확장 섹션 DESIGN.md에 반영
- [ ] 기존 "실험 구조", "PI 구조", "측정 체계" 섹션과 중복/충돌 없음
- [ ] DuckDB 스키마 변경이 기존 테이블과 호환
- [ ] Lead 검수 완료
