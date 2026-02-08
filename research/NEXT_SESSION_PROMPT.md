# 다음 세션 프롬프트 (DOE-020 이후)

## 현재 상태 요약

20개 실험(DOE-001~020) 완료, 38개 findings 확정, 24개 가설 검증.

### 핵심 발견

#### Scenario & Architecture
- **F-012**: defend_the_line이 표준 평가 시나리오 (높은 discriminability, 4-26 kills/episode)
- **F-010, F-034**: L0_only 일관되게 최악 (3개 독립 실험에서 확인, d=0.83-1.48)
- **F-029**: basic.cfg 사용 불가 (1 monster, floor effect)
- **F-030**: deadly_corridor 사용 불가 (97%+ zero kills, 너무 어려움)

#### Strategy Performance
- **F-036**: burst_3 = kills 최적 (15.40 kills/episode)
- **F-032**: adaptive_kill = kill_rate 최적 (46.18 kr)
- **F-035**: adaptive_kill, burst_3, random 형성 top tier (43.4-46.6 kr, 통계적으로 동등)
- **F-022**: 5-action space에서도 random ≈ structured (H-015 부분 거부)
- **F-018**: 3-action space에서 random ≈ structured (H-014 완전 거부)

#### Key Nulls
- **F-013~015**: Memory/Strength 파라미터 무효 (DOE-009, 모든 p>0.10, 실제 VizDoom 데이터)
- **F-025~026**: Compound 전략 무효 (weapon cooldown이 timing 차이 흡수)
- **F-027**: Attack ratio 50-100% → kill_rate 무효 (p=0.812)

#### Paradoxes
- **F-024**: Kill_rate vs kills 역순위 (생존시간이 rate denominator로 작용)
- **F-020**: 5-action space 확장이 kill_rate 감소 (3.18 kr deficit)
- **F-021**: Strafe repositioning < Turn repositioning (aim 방향 변경이 핵심)
- **F-023**: Strafing은 survival 극대화 (+63%, eta2=0.225) but kills/kr 희생

#### Negative Results
- **F-037**: compound_attack_turn ≈ attack_only (10.73 vs 10.70, d=0.01, 이점 없음)
- **F-028**: Health threshold=0 최적 (dodge 규칙 disable이 최선)

### 미결 사항

1. **H-005** (Strategy Document Quality) — 아직 테스트 안됨 (OpenSearch L2 layer 실제 효과 검증)
2. **Multi-objective optimization** 필요 (kills vs kill_rate vs survival 트레이드오프, F-024/F-038)
3. **Why random ≈ structured?** — Information-theoretic 분석 필요 (3-action space의 entropy 한계)
4. **Generational evolution** 미시작
5. **RAG knowledge accumulation** 미시작 (L2 layer 실제 가동 테스트)

## 제안하는 다음 단계

### Option A: Multi-Objective Optimization (TOPSIS/AHP)
**목표**: kills vs kill_rate vs survival_time 트레이드오프 정량화.

**방법**: TOPSIS 기반 multi-criteria decision analysis.

**데이터**: DOE-020 best-of-breed 결과 활용.
- burst_3: kills=15.40, kr=45.63, survival=20.34s
- adaptive_kill: kills=13.93, kr=45.97, survival=18.23s
- random: kills=12.23, kr=42.31, survival=17.44s

**산출물**: User-defined 가중치(kill_rate, kills, survival_time) 기반 최적 전략 선택.

**의미**: Single-metric 최적화에서 multi-objective 최적화로 전환. Pareto front 구축.

### Option B: Generational Evolution 시작
**목표**: 현재 best-of-breed 기반 진화 알고리즘 첫 generation 설계.

**기반 전략**: burst_3 (kills 최적), adaptive_kill (kr 최적).

**진화 메커니즘**:
- Crossover: 전략 조합 (예: burst_3 패턴 + adaptive_kill 조건 분기)
- Mutation: 파라미터 변이 (burst length, attack ratio, adaptive threshold)
- Selection: TOPSIS 기반 fitness 평가

**설계**: Gen 1 → 10 genomes, 30 episodes/genome, TOPSIS fitness → Gen 2 선택.

**산출물**: Gen 1 최적 genome, 진화 가능성 검증.

### Option C: Information-Theoretic Analysis
**목표**: 왜 random ≈ structured인지 이론적 분석.

**방법**: Shannon entropy, mutual information, information gain 계산.
- 3-action space entropy: H(X) = -Σp(x)log₂p(x)
- Random의 최대 entropy vs structured pattern entropy
- Action sequence information content 분석

**분석 대상**:
- random vs burst_3 action sequence 비교
- Turn action의 information gain (적 탐지, aim 조정)
- Attack action의 information gain (kill 획득)

**의미**: 3-action space에서 random이 near-optimal인 이유를 정보이론으로 설명.

### Option D: RAG Pipeline 가동 (L2 Layer 검증)
**목표**: defend_the_line 에피소드 데이터로 strategy document 생성 → OpenSearch 인덱싱 → L2 layer 실제 가동.

**단계**:
1. DOE-020 에피소드 데이터 → strategy document 자동 생성 (LLM 기반)
2. OpenSearch kNN 인덱싱 (vector embeddings via Ollama)
3. L2_knn 전략 구현 (OpenSearch query → strategy selection)
4. DOE-021: L2_knn vs burst_3 vs random 비교

**검증**: H-005 테스트 — document quality가 성능에 영향을 주는가?

**의미**: 전체 L0→L1→L2 cascade 실제 가동, RAG 효과 검증.

### Option E: New Scenario Development
**목표**: defend_the_line 변형 커스텀 시나리오 개발, 기존 전략 robustness 검증.

**변형 예시**:
- defend_the_line_hard: 적 2배 (16 monsters), 더 빠른 이동 속도
- defend_the_line_weapons: 다른 무기 (shotgun, chaingun)
- defend_the_line_narrow: 좁은 복도 (lateral movement 더 중요)

**검증**: 현재 top tier (burst_3, adaptive_kill, random)가 새 시나리오에서도 유효한가?

**의미**: Scenario generalization, overfitting 여부 확인.

## 프롬프트

아래를 새 세션에 붙여넣으세요:

---

이전 세션에서 DOE-001~020까지 완료했어. 주요 성과:

1. **38개 findings 확정** (research/FINDINGS.md)
   - defend_the_line = 표준 시나리오 (F-012)
   - L0_only 최악, burst_3 kills 최적, adaptive_kill kr 최적 (F-010, F-034, F-036, F-032)
   - Memory/Strength 파라미터 무효 (F-013~015)
   - Random ≈ structured in 3-action space (F-018)

2. **24개 가설 검증** (research/HYPOTHESIS_BACKLOG.md)
   - 12개 adopted, 8개 rejected, 4개 closed/superseded

3. **커밋 완료**:
   - c44bc27 (DOE-008, 첫 significant result)
   - 87ea59d (DOE-012~020)
   - 전체 히스토리는 `git log --oneline --graph` 참고

4. **주요 발견**:
   - compound 전략 무효 (F-025~026)
   - 5-action space 확장 = kill_rate 감소 (F-020)
   - Strafing = survival 극대화 but kr 희생 (F-023)
   - Kill_rate vs kills 역순위 (F-024)

다음으로 **[Option A/B/C/D/E 중 선택]**을 진행하자.

**Option A**: TOPSIS multi-objective optimization (kills/kr/survival 트레이드오프)
**Option B**: Generational evolution (burst_3/adaptive_kill 기반 첫 generation)
**Option C**: Information-theoretic analysis (왜 random ≈ structured?)
**Option D**: RAG pipeline 가동 (L2 layer 실제 검증, H-005)
**Option E**: New scenario development (robustness 검증)

파일 위치:
- `research/INTERIM_REPORT_DOE001_020.md` — 중간 보고서
- `research/FINDINGS.md` — 전체 38개 findings
- `research/HYPOTHESIS_BACKLOG.md` — 가설 현황
- `research/RESEARCH_LOG.md` — 연구 로그
- `research/DOE_CATALOG.md` — DOE 카탈로그
- `research/experiments/` — 실험 문서 (ORDER + REPORT)
- `.claude/rules/` — 프로젝트 규칙 (R000-R102)
- `CLAUDE.md` — 프로젝트 엔트리포인트

---

## 추가 정보

### 실험 히스토리 요약
| DOE | Hypothesis | Result | Key Finding |
|-----|-----------|--------|-------------|
| DOE-001 | H-001 (RAG > baselines) | MEDIUM trust | Full ≈ Rule >> Random (F-001~004) |
| DOE-002 | H-006~008 (Memory/Strength) | INVALIDATED | Mock data, AMMO2 bug |
| DOE-005 | H-009 (Plateau) | NULL | [0.7,0.9] plateau (F-008) |
| DOE-006 | H-010 (Re-validation) | NULL | [0.3,0.7] null (confirming F-008) |
| DOE-007 | H-011 (Ablation) | NULL | defend_the_center too simple |
| DOE-008 | H-012 (defend_the_line) | HIGH trust | L0_only worst (F-010), scenario matters (F-012) |
| DOE-009 | H-013 (Memory/Strength real data) | NULL | All p>0.10 (F-013~015) |
| DOE-010 | H-014 (Structured movement) | REJECTED | Random ≈ burst (F-018) |
| DOE-011 | H-015 (5-action expansion) | PARTIAL | Space expansion hurts kr (F-020~024) |
| DOE-012 | H-016 (Compound actions) | REJECTED | Compound worse (F-025~026) |
| DOE-013 | H-017 (Attack ratio) | REJECTED | Ratio doesn't affect kr (F-027) |
| DOE-014 | H-018 (Health threshold) | ADOPTED | Threshold=0 best (F-028) |
| DOE-015 | H-019 (Scenario generalization) | REJECTED | basic.cfg unusable (F-029) |
| DOE-016 | H-020 (deadly_corridor) | REJECTED | Complete floor effect (F-030) |
| DOE-017 | H-021 (attack_only replication) | ADOPTED | Independent seeds confirm (F-031) |
| DOE-018 | H-022 (Adaptive strategies) | PARTIAL | adaptive_kill wins kr (F-032~033) |
| DOE-019 | H-023 (Cross-validation) | ADOPTED | L0_only worst 3x (F-034~035) |
| DOE-020 | H-024 (Best-of-breed) | ADOPTED | burst_3 kills, multi-obj needed (F-036~038) |

### 통계적 신뢰도 현황
- HIGH trust: 16 findings (F-010, F-012, F-013~015, F-016~019, F-021, F-023, F-029~030, F-034~035, F-037)
- MEDIUM trust: 16 findings (F-001~004, F-005~007 INVALIDATED, F-008 rejected, F-011, F-020, F-022, F-027~028, F-032, F-036, F-038)
- LOW trust: 0 findings (all elevated or rejected)

### 현재 에이전트 아키텍처
```
Level 0 (L0): Hardcoded reflex rules (health<30→flee, attack nearest)
Level 1 (L1): DuckDB episode cache (memory dodge heuristic)
Level 2 (L2): OpenSearch kNN strategy documents (NOT TESTED YET)
```

**L0-L1 검증 완료**, **L2 미검증** (H-005 pending).

### 기술 스택
- VizDoom 1.2.4 (Docker, Xvfb headless)
- Rust: 에이전트 코어 (L0-L1-L2 cascade)
- Python: VizDoom bridge (action_functions.py)
- R: 통계 분석 (ANOVA, diagnostics)
- Go: Orchestrator (experiment lifecycle)
- DuckDB: 에피소드 데이터
- OpenSearch: RAG kNN (L2, pending)

### 문제 사항
- AMMO2 broken for defend_the_line (shots_fired/ammo_efficiency 사용 불가)
- 3-action space entropy 한계 (random ≈ structured)
- Multi-objective 트레이드오프 미해결 (kills vs kr vs survival)
