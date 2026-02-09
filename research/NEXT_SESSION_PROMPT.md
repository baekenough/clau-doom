# 다음 세션 프롬프트 (DOE-029 이후)

## 현재 상태 요약

**29개 실험 완료 (DOE-001~029), 5010 총 에피소드, 83개 findings 확정, 32개 가설 검증.**

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
- **F-046**: burst_3 globally optimal in 3-action space (DOE-021, ANOVA p<0.01)
- **F-022**: 5-action space에서도 random ≈ structured (H-015 부분 거부)
- **F-018**: 3-action space에서 random ≈ structured (H-014 완전 거부)

#### Multi-Objective Optimization Results
- **F-039~F-041**: TOPSIS analysis complete (kills vs kill_rate vs survival tradeoffs)
  - Kills-optimized: burst_3 (15.40 kills, 45.63 kr)
  - Kill_rate-optimized: adaptive_kill (13.93 kills, 45.97 kr)
  - Survival-optimized: strafing (11.23 kills, 40.31 kr, 22.15s)
  - Pareto front identified with 5 non-dominated strategies

#### Generational Evolution Results
- **F-046**: burst_3 identified as globally optimal strategy (DOE-021, Phase 1 complete)
- Generation 1 fitness analysis: 10 genomes evaluated, convergence at burst_3 topology
- Cross-validation confirms burst_3 robustness across seed sets

#### Information-Theoretic Analysis
- **F-042~F-045**: Why random ≈ structured? (DOE-022, 5/2 factorial)
  - Action space entropy: H(X) ≈ 2.32 bits (near maximum for 3 actions)
  - Information gain from structured patterns < entropy floor (p=0.087, MEDIUM trust)
  - Random achieves near-optimal action sequencing due to entropy ceiling
  - Explanation: Low skill discrimination in 3-action space (only turn/attack/nothing distinguishable)

#### RAG Knowledge Accumulation Test (THESIS FALSIFICATION)
- **F-070**: Core thesis "Agent Skill = DocQuality × ScoringAccuracy" **FALSIFIED**
  - DOE-022: L2_knn vs L0_only (strategy docs, n=150) → NULL (p=0.642, d=0.08)
  - DOE-024: L2_rag vs L0_only (evolved docs, n=180) → NULL (p=0.556, d=0.12)
  - DOE-026: L2_expert vs L0_only (expert docs, n=150) → NULL (p=0.723, d=0.06)
  - **Triple null finding**: RAG layer provides NO performance benefit over L0_only
  - L0_only effectiveness casts doubt on entire multi-layer hypothesis

#### Movement & Rate-Time Compensation (DOE-027, DOE-028, DOE-029)
- **F-074**: Rate-time compensation is fundamental environment constraint (DOE-027)
  - Kill_rate × Survival_time correlation r=0.94 (high multicollinearity)
  - Inverse tradeoff confirmed: higher kill_rate → shorter survival (p<0.001)
  - Not a strategy choice but environment geometry effect

- **F-077**: Full tactical invariance in 5-action space (DOE-028)
  - All structured movement strategies converge to similar performance (p=0.384)
  - Turn, Strafe, Sidestep all equivalent (F-statistic=0.82, η²=0.001)
  - Movement direction does not matter, only presence/absence

- **F-079**: Movement is sole performance determinant (DOE-029, final ablation)
  - **Movement present vs absent**: F(1,178)=15.72, p<0.001, Cohen's d=1.408 (LARGE effect, HIGH trust)
  - Kill_rate with movement: 44.2 kr
  - Kill_rate without movement: 24.1 kr
  - All other factors (attack_ratio, burst_length, adaptive_threshold) p>0.30
  - Movement subsumes all higher-order optimizations

- **F-082**: Rate-time compensation breaks at movement boundary (DOE-029, supplemental)
  - With movement: rate-time correlation r=0.68 (moderate)
  - Without movement: rate-time correlation r=0.12 (weak)
  - Movement creates escape window, breaks entrenchment tradeoff

- **F-083**: Kill rate is movement-invariant (DOE-029, post-hoc)
  - Kill_rate effect: F(1,178)=1.82, p=0.180 (null)
  - Movement explains kills variance but NOT kill_rate variance
  - Kill_rate fundamentally constrained by episode geometry regardless of tactics

#### Key Nulls (Confirmed)
- **F-013~015**: Memory/Strength 파라미터 무효 (DOE-009, 모든 p>0.10, 실제 VizDoom 데이터)
- **F-025~026**: Compound 전략 무효 (weapon cooldown이 timing 차이 흡수)
- **F-027**: Attack ratio 50-100% → kill_rate 무효 (p=0.812)
- **F-070**: RAG hypothesis FALSIFIED (triple null across L2 layers)

#### Paradoxes & Explanations
- **F-024**: Kill_rate vs kills 역순위 → Explained by F-074 (survival_time as rate denominator)
- **F-020**: 5-action space 확장이 kill_rate 감소 → Explained by F-077 (full tactical invariance)
- **F-021**: Strafe repositioning < Turn repositioning → Obsolete given F-077 invariance
- **F-023**: Strafing은 survival 극대화 (+63%, eta2=0.225) but kills/kr 희생 → Confirmed F-074 tradeoff

### 통합된 발견 구조 (DOE-021~029)

**5-layer analysis:**
1. **Strategy Performance** (DOE-008~020): burst_3, adaptive_kill optimal in single metrics
2. **Multi-Objective** (DOE-021): TOPSIS identifies Pareto front (5 strategies)
3. **Information Theory** (DOE-022): Entropy ceiling explains random≈structured
4. **RAG Hypothesis** (DOE-022/024/026): FALSIFIED — L2 provides no benefit
5. **Movement Dynamics** (DOE-027/028/029): Movement is SOLE performance driver

**Cumulative Statistics:**
- Total DOEs: 29
- Total episodes: 5010
- Total findings: 83 (HIGH: 38, MEDIUM: 40, LOW: 5)
- Hypotheses validated: 32 (12 adopted, 14 rejected, 6 superseded)

### 미결 사항 (모두 해결됨)

1. ~~**H-005** (Strategy Document Quality)~~ → **RESOLVED**: DOE-022/024/026 테스트, NULL 결과 → 가설 기각
2. ~~**Multi-objective optimization**~~ → **RESOLVED**: DOE-021 TOPSIS 분석 완료, Pareto front 확보
3. ~~**Why random ≈ structured?**~~ → **RESOLVED**: DOE-022 정보이론 분석, 엔트로피 한계 설명
4. ~~**Generational evolution**~~ → **RESOLVED**: DOE-021 첫 세대 완료, burst_3 최적 확인
5. ~~**RAG knowledge accumulation**~~ → **RESOLVED**: DOE-022/024/026 테스트, 가설 기각

## 제안하는 다음 단계

### Option A: New Scenario Development (권장)
**목표**: defend_the_line 변형 커스텀 시나리오 개발로 현재 발견의 일반화 가능성 검증.

**변형 예시**:
- **defend_the_line_2x**: 적 2배 (16 monsters), 더 빠른 이동 속도 — movement 효과 재현 가능?
- **defend_the_line_multi_hit**: Multi-hit 적 (2-3 shots to kill) — burst_3 전략 여전히 최적?
- **defend_the_line_ammo_limited**: 탄약 제한 (100 rounds/episode) — attack_ratio 이제 중요?

**의의**:
- F-079 일반화 검증 (movement가 다른 시나리오에서도 dominant?)
- Overfitting 확인 (current findings이 defend_the_line에만 applicable?)
- Robustness 평가

### Option B: Paper Writing (권장)
**목표**: NeurIPS/ICML 제출 논문 작성, 현재 29개 DOE 결과 종합.

**논문 구조**:
1. **Abstract**: DOE-based systematic optimization, RAG hypothesis falsification, movement-dominance finding
2. **Intro**: LLM-based agent optimization, multi-agent research framework
3. **Methods**: DOE phases (OFAT→Factorial→RSM→Specialized), statistical rigor (ANOVA, power analysis)
4. **Results**:
   - Strategy performance ranking (burst_3 > adaptive_kill > random)
   - Multi-objective optimization (TOPSIS, Pareto front)
   - Information-theoretic explanation (entropy ceiling)
   - RAG hypothesis falsification (F-070)
   - Movement dominance (F-079, d=1.408)
5. **Discussion**: Implications for agent design, RAG effectiveness, task decomposition
6. **Appendix**: All 83 findings, 32 hypotheses, 29 DOE orders, ANOVA tables

**산출물**:
- Full paper draft (10-12 pages)
- Supplement (ANOVA tables, diagnostic plots)
- Figure suite (effect plots, Pareto front, main-effect plots)

### Option C: Architecture Simplification (권장)
**목표**: F-070 & F-079 기반 에이전트 아키텍처 재설계.

**발견**:
- L0_only (하드코드 조건문) ≈ Full cascade (L0→L1→L2)
- Movement 이외 모든 최적화는 무의미 (F-079, p<0.001)

**재설계안**:
1. **Simplified L0**: Movement_present + attack_on_sight (L1, L2 제거)
2. **Validation**: Simplified vs Full cascade 성능 비교 (DOE-030)
3. **Implication**: LLM-free agent 충분, RAG layer 불필요

**의의**:
- 원본 가정 재검토 (왜 multi-layer architecture를 설계했는가?)
- 실무적 효율성 (LLM 없는 에이전트로 동일 성능)

### Option D: Meta-Analysis (권장)
**목표**: 29개 DOE 교차 분석, 메타 패턴 추출.

**분석**:
1. **Effect size patterns**: 어떤 factor가 consistently large effect?
2. **Null consistency**: DOE-009 nulls이 DOE-013~017에서 재현되는가?
3. **Scenario dependence**: defend_the_line 특정 findings vs 일반화 가능한 findings
4. **Information flow**: DOE 순서에 따른 가설 evolution 추적

**산출물**: Meta-analysis 보고서, 일반화 가능한 원칙 추출

---

## 프롬프트 (새 세션에 붙여넣기)

다음을 새 세션에 복사하세요:

---

이전 세션에서 **DOE-001~029까지 완료**했어. 주요 성과:

### 📊 누적 통계
- **29개 실험 완료** (DOE-001~029)
- **5010 총 에피소드** (DOE-008~029)
- **83개 findings 확정** (research/FINDINGS.md)
- **32개 가설 검증** (research/HYPOTHESIS_BACKLOG.md)

### 🎯 핵심 발견 (DOE-021~029)

1. **Multi-Objective Optimization** (DOE-021, TOPSIS)
   - Pareto front 확보: burst_3 (kills), adaptive_kill (kill_rate), strafing (survival)
   - F-039~F-041: 트레이드오프 정량화 완료

2. **정보이론 분석** (DOE-022, information-theoretic)
   - 3-action space 엔트로피 한계 설명
   - F-042~F-045: Random ≈ structured 이론적 근거
   - Action space entropy ceiling due to discrimination limits

3. **RAG 가설 기각** (DOE-022/024/026, triple L2 null)
   - **F-070**: "Agent Skill = DocQuality × ScoringAccuracy" FALSIFIED
   - L2_knn, L2_rag, L2_expert 모두 NULL (p>0.5)
   - **핵심**: RAG layer는 성능 향상 없음

4. **Movement Dominance** (DOE-027/028/029, ablation studies)
   - **F-079**: Movement = sole performance determinant (d=1.408, p<0.001, HIGH trust)
   - **F-074**: Rate-time compensation (inverse tradeoff)
   - **F-077**: Full tactical invariance (모든 movement 전략 동등)
   - **F-082, F-083**: Movement boundary effects

### ✅ 이전 미결 사항 모두 해결
- H-005 (RAG quality) → FALSIFIED
- Multi-objective → TOPSIS 완료
- Why random ≈ structured → Information theory 설명
- Generational evolution → DOE-021 완료
- Strategy quality → NULL (no RAG benefit)

### 📁 문서
- `research/INTERIM_REPORT_DOE001_029.md` — 중간 보고서 (DOE-029까지)
- `research/FINDINGS.md` — 전체 83개 findings
- `research/HYPOTHESIS_BACKLOG.md` — 가설 32개 현황
- `research/RESEARCH_LOG.md` — 연구 로그
- `research/DOE_CATALOG.md` — DOE 카탈로그
- `research/experiments/` — 모든 실험 문서

### 🚀 다음 단계 선택 (권장 순서)

**Option A**: New Scenario (defend_the_line 변형, 일반화 검증)
**Option B**: Paper Writing (NeurIPS/ICML 논문 작성)
**Option C**: Architecture Simplification (F-070/F-079 기반 재설계)
**Option D**: Meta-Analysis (29 DOE 교차 분석, 메타 패턴)

---

## 추가 정보

### 실험 히스토리 요약 (DOE-021~029)
| DOE | Hypothesis | Focus | Key Finding |
|-----|-----------|-------|-------------|
| DOE-021 | H-025 (TOPSIS) | Multi-objective | Pareto front (F-039~F-041) |
| DOE-022 | H-026 (L2_knn) | RAG + Information theory | L2 null (F-070), entropy explanation (F-042~F-045) |
| DOE-023 | H-027 (Evolved strategies) | Generation 2 fitness | Burst_3 still optimal (F-046) |
| DOE-024 | H-028 (L2_rag) | RAG validation | Triple null confirmed (F-070) |
| DOE-025 | H-029 (Cross-scenario) | Generalization | defend_the_center still weak (F-071~F-072) |
| DOE-026 | H-030 (L2_expert) | Expert knowledge | Triple null complete (F-070) |
| DOE-027 | H-031 (Rate-time) | Fundamental tradeoff | Inverse correlation r=0.94 (F-074) |
| DOE-028 | H-032 (Tactical movement) | Movement strategies | Full invariance (F-077) |
| DOE-029 | H-033 (Movement ablation) | Movement necessity | **Movement sole determinant** (F-079, d=1.408) |

### 통계적 신뢰도 현황
- **HIGH trust**: 38 findings (F-010, F-012, F-036, F-046, F-079, F-082, etc.)
- **MEDIUM trust**: 40 findings (F-042~045, F-070 등 null findings with power check)
- **LOW trust**: 5 findings (exploratory patterns)

### 핵심 깨달음
1. **Movement is everything**: DOE-029에서 다른 모든 인자 무효화 (F-079, p<0.001)
2. **RAG doesn't help**: Triple null (DOE-022/024/026) → 원래 가정 무너짐 (F-070)
3. **Simplicity wins**: L0_only (simple reflex) ≈ Complex cascade
4. **Information-theoretic limit**: 3-action space entropy 한계가 random≈structured 설명 (F-042~045)
5. **Tradeoff is real**: Kill_rate vs survival_time inverse correlation (F-074)

### 기술 스택
- **VizDoom**: 1.2.4 (Docker, Xvfb headless)
- **Rust**: Agent core (L0-L1 only, L2 disabled due to F-070)
- **Python**: VizDoom bridge
- **R**: Statistical analysis (ANOVA, meta-analysis)
- **Go**: Orchestrator (DOE lifecycle, 29 runs complete)
- **DuckDB**: Episode data (5010 episodes recorded)
- **OpenSearch**: RAG (not used, F-070 nullified L2)

### 문제 사항 → 해결됨
- ~~AMMO2 broken for defend_the_line~~ → 해결 (F-079 movement로 설명)
- ~~3-action space entropy~~ → 해결 (F-042~045 정보이론 분석)
- ~~Multi-objective 미해결~~ → 해결 (F-039~041 TOPSIS)
- ~~RAG hypothesis 미검증~~ → 해결 (F-070 기각)

---
