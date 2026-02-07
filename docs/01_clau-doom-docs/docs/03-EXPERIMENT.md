# 03 — 실험 구조

← [02-AGENT](02-AGENT.md) · [인덱스](../DOOM_ARENA_CLAUDE.md) · 다음 → [04-DOE](04-DOE.md)

---

## 과학적 실험 사이클

```
가설 수립 → DOE 설계 → 병렬 실행 → 측정 → ANOVA/회귀 분석 → 지식화
    ↑                                                        │
    └── SPC 이상 감지 / FMEA 우선순위 / 메타 분석 ←────────────┘
```

## 가설 소스

1. Claude Code (코치) — 에피소드 회고, 세대 간 비교에서 도출
2. 에이전트 자가 분석 — DuckDB 집계에서 패턴 발견
3. 에이전트 간 관찰 — NATS 구독으로 다른 에이전트의 노하우 비교
4. SPC 이상 신호 — 관리도에서 이탈 패턴 감지 시 원인 가설 자동 생성
5. FMEA — RPN 높은 실패 모드에 대한 개선 가설

## 실험 실행 정책

기존 (Phase 0):
- 한 번에 하나의 변수만 변경 (OFAT)
- A/B 방식: 짝수 에피소드는 control, 홀수는 treatment
- 동일 시드로 control/treatment 대조 (맵 노이즈 제거)
- 최소 표본 수 충족 전까지 결론 내리지 않음

확장 (Phase 1+):
- DOE 매트릭스에 따라 다변수 동시 변경 허용
- 요인배치/직교배열의 변수 격리는 통계적으로 보장됨
- 블록 설계로 교란 변수(맵, 난이도) 통제
- 동일 시드 세트로 모든 Run 실행 (재현성)
- 중심점 추가로 곡률 검정
- 잔차 분석으로 모델 가정(정규성, 등분산성, 독립성) 검증 필수

## 측정 체계 (DuckDB)

에피소드 단위 + 교전 단위 이중 기록:

```sql
-- 기존
experiments: experiment_id, episode_id, variant, seed, 
  metrics(survival_time, kills, damage_taken, ammo_efficiency, 
          exploration_coverage, encounter_success_rate)
encounters: situation_snapshot, strategy_used, weapon_used, 
  rag_query_result, outcome, duration_ms

-- DOE 확장
doe_runs: experiment_id, run_id, design_type, factor_levels(JSON),
  block, replicate, center_point(bool)
doe_results: run_id, episode_id, response_values(JSON)
spc_observations: generation, agent_id, metric, value, 
  x_bar, r_value, ucl, lcl, signal_type
fmea_log: generation, failure_mode, occurrence, severity, 
  detection, rpn, corrective_action
capability: generation, agent_id, metric, cp, cpk, pp, ppk
```

## 결론 분기

- **채택**: ANOVA에서 유의(p < α) + 효과 크기 실용적 의미 있음 + 잔차 가정 충족 → MD 기본 전략 변경, 새 전략 문서 색인, NATS 노하우 발행
- **기각**: 유의하지 않음 또는 효과 크기 미미 → 기존 유지, 실패 기록 저장, 파워 분석으로 표본 부족 여부 확인
- **후속 실험**: 유의한 교호작용 발견 → RSM으로 정밀 최적화
- **모델 부적합**: 잔차 가정 위반 → 변환(Box-Cox) 또는 비모수 검정 전환

## 메타 실험

세대가 쌓이면 "어떤 종류의 실험이 효과적이었나"도 분석:
- DOE 유형별 채택률 비교 (OFAT vs 요인배치 vs 타구치 vs RSM)
- 변수 카테고리별 효과 크기 분포
- exploitation vs exploration 밸런스를 실험 포트폴리오 자체에 적용
- 학습 곡선 phase별 기울기 변화 → DOE 전환 효과 정량화

## PI 구조: Cowork(연구) + Claude Code(실행)

### 역할 분리

```
Cowork (Opus 4.6) = PI (연구 책임자)
  - 연구 방향 결정, 가설 수립
  - DOE 매트릭스 설계 (설계 유형, 인자/수준, 블록, 반복 수 결정)
  - 결과 해석: ANOVA, 효과도, 잔차 진단
  - SPC 관리도 해석, FMEA 우선순위 결정
  - TOPSIS/AHP 가중치 조정
  - 세대 진화 전략 결정
  - DOE 단계 전환 판단 (Phase 0→1→2→3)
  - 메타 실험 전략 조정
  - 출력: EXPERIMENT_ORDER.MD (DOE 매트릭스 포함)

Claude Code = 연구원 (실험 실행자, Sub-agents 활용)
  - DOE 매트릭스를 에이전트별 조건으로 분해
  - Sub-agent 병렬 배분 및 실행 조율
  - DuckDB 쿼리 실행, ANOVA 테이블 산출
  - 에이전트 MD 수정 (실험 변수 주입)
  - docker compose로 에이전트 재시작
  - OpenSearch 색인 작업
  - SPC 관리도 데이터 갱신
  - 출력: EXPERIMENT_REPORT_{ID}.MD (ANOVA 결과, 효과도, 잔차 진단 포함)
```

### 소통 인터페이스 = MD 파일

```
volumes/research/
├── RESEARCH_LOG.MD              # Cowork 작성, 누적 연구 일지
├── HYPOTHESIS_BACKLOG.MD        # Cowork 관리, 가설 큐
├── FINDINGS.MD                  # Cowork 작성, 확정된 발견 누적
├── DOE_CATALOG.MD               # 실험 설계 유형별 카탈로그 및 적용 기록
├── SPC_STATUS.MD                # 관리도 현황, 이상 신호 이력
├── FMEA_REGISTRY.MD             # 실패 모드 등록부, RPN 추이
├── orders/
│   └── EXPERIMENT_ORDER_021.MD  # Cowork → Claude Code (DOE 매트릭스 포함)
└── reports/
    └── EXPERIMENT_REPORT_021.MD # Claude Code → Cowork (ANOVA, 효과도, 잔차)
```

### Opus가 제어하는 실험 변수

- 유의 수준: α = 0.05 (기본), 스크리닝은 α = 0.10 허용
- 최소 표본: 30 에피소드/Run (기본), 파워 분석(1-β ≥ 0.80)으로 동적 조정
- DOE 설계 유형: OFAT / 요인배치 / 부분요인 / 타구치 / RSM-CCD 중 선택
- 블록 변수: 맵 난이도, 적 밀도 등 교란 변수 지정
- 중심점 수: 곡률 검정용 (기본 3~5회)
- 동시 실험: DOE 매트릭스 단위로 관리 (에이전트당 1개 → Run당 1개)
- 조기 중단: 중간 분석에서 주효과 |effect| > 3σ이면 해당 인자 확정
- exploration 비율: 전체 실험의 30%는 기존과 크게 다른 전략 시도
- SPC 관리한계: 세대 3 이후 기선 확립, 이후 자동 모니터링
- FMEA 갱신 주기: 매 세대 종료 시
- TOPSIS 가중치: 세대 전략 방향에 따라 동적 조정

### 실험 지시서 확장 포맷 (DOE 매트릭스)

```markdown
# EXPERIMENT_ORDER_021 — DOE Factorial

## 실험 유형: 2³ 완전요인배치
## 목적: retreat_threshold × ammo_conservation × exploration_priority 교호작용 분석

## 설계 매트릭스
| Run | retreat_threshold | ammo_conservation | exploration_priority | Agent   | Seed Set          |
|-----|-------------------|-------------------|----------------------|---------|-------------------|
| 1   | 0.30 (-)          | low (-)           | low (-)              | P_001   | [42,77,113,256,389] |
| 2   | 0.45 (+)          | low (-)           | low (-)              | P_002   | [42,77,113,256,389] |
| 3   | 0.30 (-)          | high (+)          | low (-)              | P_003   | [42,77,113,256,389] |
| 4   | 0.45 (+)          | high (+)          | low (-)              | P_004   | [42,77,113,256,389] |
| 5   | 0.30 (-)          | low (-)           | high (+)             | P_005   | [42,77,113,256,389] |
| 6   | 0.45 (+)          | low (-)           | high (+)             | P_006   | [42,77,113,256,389] |
| 7   | 0.30 (-)          | high (+)          | high (+)             | P_007   | [42,77,113,256,389] |
| 8   | 0.45 (+)          | high (+)          | high (+)             | P_008   | [42,77,113,256,389] |

## 블록 설계
- 블록 변수: 맵 난이도 (easy/hard)
- 각 Run은 easy 블록 15ep + hard 블록 15ep = 30 에피소드

## 반복(Replication)
- 각 Run 최소 30 에피소드 (시드 5개 × 6 반복)
- 중심점(center point) 추가: retreat=0.375, ammo=mid, explore=mid → P_009에서 10ep

## 반응변수(Response)
- 1차: kill_rate (kills/episode)
- 2차: survival_time, damage_taken, ammo_efficiency

## 분석 계획
- ANOVA (α = 0.05)
- 주효과도(main effect plot) + 교호작용도(interaction plot)
- 잔차 분석: 정규성(Anderson-Darling), 등분산성(Levene), 독립성(run order plot)
- 유의한 교호작용 발견 시 → Phase 2 RSM 후속 실험 설계

## 실행 배분 (Sub-agent 병렬화)
- Sub-agent α: Run 1, 2 (P_001, P_002)
- Sub-agent β: Run 3, 4 (P_003, P_004)
- Sub-agent γ: Run 5, 6 (P_005, P_006)
- Sub-agent δ: Run 7, 8 + 중심점 (P_007, P_008, P_009)

## 조기 중단
- 15 에피소드 시점 중간 분석
- 주효과 중 하나라도 |effect| > 3σ이면 해당 인자 유의 확정, 나머지 집중
```
