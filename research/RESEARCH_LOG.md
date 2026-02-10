# Research Log

## 2026-02-10 — DOE-039/040/041: Phase 4 New Scenario Exploration and Difficulty Mapping

### Context
Phase 4 continuation: exploring new scenarios (predict_position, deadly_corridor) and completing the difficulty-performance curve with a 3-level mapping. Three experiments executed and analyzed 2026-02-10. Total episodes: 300 (cumulative: 6950).

### Hypotheses
H-042: Movement aids predict_position performance (new scenario viability test)
H-043: Performance follows monotonic gradient across doom_skill 1/3/5
H-044: Movement advantage generalizes to deadly_corridor navigation scenario

### Designs

**DOE-039** (One-Way CRD, 60 episodes):
- Factor: strategy (random_3 vs attack_raw)
- Scenario: predict_position.cfg (moving target)
- Tests: New scenario viability for agent research

**DOE-040** (One-Way CRD, 150 episodes):
- Factor: doom_skill (3 levels: sk1, sk3, sk5)
- Strategy: random_5 (optimal architecture)
- High power: n=50 per level
- Completes difficulty curve with sk3 midpoint

**DOE-041** (One-Way CRD, 90 episodes):
- Factor: strategy (random_7 vs forward_attack vs attack_only)
- Scenario: deadly_corridor.cfg (7-action space)
- Tests: Movement advantage generalization to navigation scenario

### Results

**DOE-039**: UNTRUSTED — predict_position scenario non-viable
- Welch t-test: t(29)=1.439, p=0.161 (not significant)
- Both strategies: shots_fired=0, 93-100% zero kills
- Scenario rejected for future research
- Conclusion: H-042 REJECTED, Finding F-108

**DOE-040**: HIGH — Difficulty gradient confirmed with 3-level precision
- One-way ANOVA: F(2,147)=152.621, p<1e-10, η²=0.675
- sk1=24.76, sk3=17.04, sk5=6.48 kills (linear slope=-4.57)
- Kill-rate paradox: sk5 highest rate (62.5 kr) but fewest kills (6.48)
- Kruskal-Wallis confirms: H(2)=108.518, p<1e-10
- Conclusion: H-043 SUPPORTED, Findings F-109, F-110, F-111

**DOE-041**: MEDIUM — random_7 wins on deadly_corridor
- One-way ANOVA: F(2,87)=6.879, p=0.00169, η²=0.137
- random_7: 0.500 kills, attack_only: 0.067, forward_attack: 0.167
- random_7 vs attack_only: d=0.856 (large), p=0.00240
- 73% zero-kill episodes (extremely challenging scenario)
- Conclusion: H-044 PARTIALLY SUPPORTED, Finding F-112

### Phase Status
Phase 4 continuing. Scenario viability hierarchy established:
1. defend_the_line (gold standard, 4-44 kills, excellent discrimination)
2. deadly_corridor (viable but extreme, 0-2 kills, requires advanced strategies)
3. basic.cfg (not suitable, binary kills)
4. predict_position (not viable, zero engagement)
5. defend_the_center (low discrimination, 0-3 kills)

### Next Steps
- Consider evolutionary optimization (DOE-021 GenomeAction)
- Consider multi-scenario tournament across difficulty levels
- Consider hybrid strategies for deadly_corridor

---

## 2026-02-09 — DOE-036/037/038: Phase 4 Cross-Scenario Validation

### Context
Phase 4 transition from confirmation/synthesis to cross-scenario validation and precision measurement. Three experiments designed 2026-02-09, executed and analyzed 2026-02-09, testing generalizability and boundary conditions.

### Hypotheses
H-039: Attack ratio affects strafe-aiming performance in basic.cfg
H-040: Movement benefit persists at doom_skill=5 (extreme difficulty)
H-041: Performance ceiling varies by difficulty, quantifiable at n=50

### Designs

**DOE-036** (One-Way CRD, 120 episodes):
- Factor: attack_ratio (4 levels: 20/40/60/80%)
- Scenario: basic.cfg (single monster)
- doom_skill: 5 (hard)
- Tests whether gradient exists in minimal scenario

**DOE-037** (2×2 Factorial, 120 episodes):
- Factors: movement (random_5 vs attack_raw) × difficulty (sk1 vs sk5)
- Tests movement effect persistence and compression at extreme difficulty
- Seeds: 70001 + i×167, i=0..29

**DOE-038** (One-Way CRD, 100 episodes):
- Factor: doom_skill (sk1 vs sk5)
- Strategy: random_5 baseline only
- High power: n=50 per level (highest in program)
- Precision measurement of performance ceiling

### Results

**DOE-036**: NULL — basic.cfg unsuitable for strategy research
- One-way ANOVA: F(3,116)=0.176, p=0.912, η²=0.005
- Chi-squared (binary kills): χ²(3)=0.623, p=0.8808
- All attack ratios produce identical binary outcomes (0 or 1 kill)
- Conclusion: H-039 REJECTED, Finding F-101
- Lesson: basic.cfg has only 1 monster, no continuous performance gradient possible

**DOE-037**: Movement persists but compressed at extreme difficulty
- Movement: F(1,116)=83.21, p<0.001, η²p=0.418 (MASSIVE)
- Difficulty: F(1,116)=1172.42, p<0.001, η²p=0.910 (DOMINANT)
- Interaction: F(1,116)=5.51, p=0.021, η²p=0.045 (SIGNIFICANT)
- Movement d: sk1=1.38, sk5=1.33 (both >0.9, persist)
- But performance spread compressed 3.04x at sk5 (sk1: 18.33 spread → sk5: 6.03 spread)
- Conclusion: H-040 SUPPORTED, Findings F-102, F-103, F-104

**DOE-038**: Performance ceiling 3.96x ratio, ultra-high precision
- Difficulty: F(1,98)=272.44, p=1.60e-32, η²=0.735 (DOMINANT)
- sk1: 25.98 ± 5.49 kills, sk5: 6.56 ± 2.06 kills
- Cohen's d: 4.66 (largest effect in program)
- Survival ratio: 7.27x (sk1: 29.31s, sk5: 4.03s)
- Variance compression: 2.67x (SD ratio 5.49/2.06)
- Conclusion: H-041 SUPPORTED, Findings F-105, F-106, F-107

### Cumulative Impact
- Total experiments: 38 (35 prior + 3 new)
- Total episodes: 6650 (6310 prior + 340 new)
- Total findings: 107 (F-001 through F-107)
- basic.cfg scenario ruled out for strategy research (F-101)
- Movement universality extends to doom_skill=5 (F-102)
- Performance ceiling precisely quantified: 3.96x ratio (F-105)
- Variance compression at extreme difficulty limits strategy differentiation (F-106)

### Next Steps
- Phase 4 cross-scenario validation complete
- Consider paper writing with 38 DOEs, 6650 episodes, 107 findings
- Consider adaptive/learning architectures beyond random-action baseline
- Consider multi-scenario meta-analysis across defend_the_line variants

---

## 2026-02-10 — DOE-033/034/035: Phase 3 Confirmation and Synthesis

### Context
Phase 2 (DOE-008 through DOE-032) systematically explored the defend_the_line parameter space, establishing movement dominance (F-079), action space optimization (F-087), and learning mechanism falsification (F-090/F-091). Phase 3 transitions to CONFIRMATION: testing interactions, replication, and synthesis of all findings.

### Hypotheses
H-036: Movement × action space interaction (HIGH priority)
H-037: DOE-008 exact replication (MEDIUM priority)
H-038: Best-of-breed synthesis tournament (HIGH priority)

### Designs

**DOE-033** (3×2 Factorial, 180 episodes):
- action_space (3/5/7) × movement (present/absent)
- Tests F-092 interaction hypothesis

**DOE-034** (One-way CRD, 150 episodes):
- Exact replication of DOE-008 (same seeds, same conditions)
- Tests infrastructure reproducibility

**DOE-035** (One-way CRD, 150 episodes):
- 5 best strategies at doom_skill=1 in 5-action space
- Tests absolute performance ceiling

### Results

DOE-033: H-036 SUPPORTED. Interaction F=11.38, p=2.26e-05. Movement d gradient: 3-act=0.414(NS) → 5-act=1.442 → 7-act=1.780. Stationary conditions identical (10.60 kills). Strafing, not turning, drives movement effect. Findings F-092~F-094.

DOE-034: H-037 PARTIALLY SUPPORTED. Rank order replicates perfectly (L0_strength > L0_memory > random > full_agent > L0_only). Non-parametric Kruskal-Wallis p=0.017. But ANOVA p=0.062 (marginal) and means shifted ~1-2 kills down. Findings F-095~F-096.

DOE-035: H-038 PARTIALLY SUPPORTED. F(4,145)=48.381, p=8.55e-26, η²=0.572. survival_burst ≈ ar_50 ≈ random_5 (~24-27 kills) > attack_raw (18.9) >> burst_3 (7.5). burst_3 catastrophically fails in 5-action space. Movement binary creates two performance tiers. Performance ceiling: ~27 kills at doom_skill=1. Findings F-097~F-100.

### Cumulative Impact
- Total experiments: 35
- Total episodes: 6310 (5830 + 480 new)
- Total findings: 100 (F-001 through F-100)
- Phase 3 confirms movement as the single dominant architectural decision
- Strafing mechanism identified as the driver (not turning)
- Replication validates infrastructure robustness
- Performance ceiling established at ~27 kills for random-action architectures

### Next Steps
- Consider Phase 4: adaptive/learning architectures beyond random-action
- Cross-scenario validation (scenarios beyond defend_the_line)
- Paper finalization with 100 findings and 35 DOEs

---

## 2026-02-10 — DOE-030/031/032: Three-Experiment Generalizability Push

### Context
DOE-029 concluded the defend_the_line optimization arc with a definitive finding: movement is the sole performance determinant (F-079, d=1.408). The 29-DOE program systematically eliminated all tactical optimization paths. The research now pivots to GENERALIZABILITY testing: does this conclusion hold under variation of difficulty, action space dimensionality, and learning paradigm?

### Hypotheses
H-033: Movement x difficulty interaction (HIGH priority)
H-034: Action space dilution gradient (MEDIUM priority)
H-035: L1 sequential cache learning (MEDIUM priority)

### Designs

**DOE-030** (2x5 Factorial, 300 episodes):
- Factors: movement (present/absent) x doom_skill (1-5)
- Tests whether F-079 (movement dominance) generalizes across all 5 difficulty levels
- Extends DOE-023's difficulty investigation with the precise movement contrast
- Seeds: 53001 + i*139, i=0..29

**DOE-031** (One-Way ANOVA, 4 levels, 120 episodes):
- Factor: action_space (3, 5, 7, 9 actions)
- Tests random strategy dilution across increasing action dimensionality
- Requires creation of 7-action and 9-action .cfg files
- Seeds: 57101 + i*149, i=0..29

**DOE-032** (2x2 Factorial with Repeated Measures, 400 episodes):
- Factors: l1_cache (on/off) x sequence_mode (sequential/independent)
- Tests whether L1 experiential learning succeeds where L2 document-based RAG failed
- Novel measurement: learning slope across 10-episode sequences
- Seeds: 61501 + k*151 + i*13, k=0..9, i=0..9

### Result
PENDING (experiments ordered but not yet executed)

### Research Strategy Rationale
Three experiments target distinct generalizability dimensions:
1. **Environmental** (difficulty): Does the finding hold under harder/easier conditions?
2. **Architectural** (action space): Does the finding hold with more/fewer degrees of freedom?
3. **Temporal** (learning): Can the system improve with sequential experience?

These form a comprehensive generalizability package for the paper. If F-079 holds across all three dimensions, it represents a strong negative result about tactical optimization in simple FPS environments. If any dimension breaks the pattern, it identifies the boundary conditions of the finding.

### Budget
DOE-030: 300 episodes (cumulative: 5310)
DOE-031: 120 episodes (cumulative: 5430)
DOE-032: 400 episodes (cumulative: 5830)
Total new: 820 episodes

---

## 2026-02-09 — DOE-029: Emergency Health Override Effect (SIGNIFICANT)

### Context
DOE-025~028 all included health<20 emergency override as untested confound. Additionally, pure_attack (always attack, no movement) was never tested in 5-action space. DOE-029 uses 2×2 factorial to isolate both effects.

### Hypothesis
H-032: Emergency health override improves survival and kills.
Priority: High
Rationale: Confound removal + pure_attack baseline in 5-action space.

### Design
DOE type: 2² Full Factorial
Factor A: action_pattern (random_50 vs pure_attack)
Factor B: health_override (enabled vs disabled)
Sample size: 30 episodes per cell, 120 total
Seeds: 49001 + i × 137, i=0..29

### Result
Pattern (A): [STAT:f=F(1,116)=58.402] [STAT:p<0.001] [STAT:eta2=0.332] [STAT:effect_size=d=1.408] — MASSIVE
Override (B): [STAT:f=F(1,116)=0.784] [STAT:p=0.378] [STAT:eta2=0.004] — NULL
Interaction: [STAT:f=F(1,116)=0.987] [STAT:p=0.322] — NULL
Kill rate: pattern p=0.180 — NOT SIGNIFICANT (kill efficiency same for both)
Kruskal-Wallis confirms: H(3)=50.802 [STAT:p<0.001]
Conclusion: H-032 PARTIALLY SUPPORTED. F-079~F-083 adopted.
Trust: HIGH

### Key Discoveries
1. **Movement is the SOLE determinant (F-079)**: d=1.408, largest effect in 29-DOE program
2. **Override irrelevant (F-080)**: Health-based dodge adds nothing
3. **Rate-time compensation breaks at movement boundary (F-082)**: Survival +60%, kr only -3%
4. **Kill rate invariant to movement (F-083)**: Movement doesn't reduce killing efficiency
5. **Research program narrative complete**: Only movement matters; everything else is noise

### Next Steps
Research program has reached definitive conclusion. 29 DOEs, 5010 episodes, 83 findings. Paper writing recommended.

---

## 2026-02-09 — DOE-028: Temporal Attack Pattern Study (NULL)

### Context
DOE-027 showed kills are invariant to attack RATIO (F-071) due to rate-time compensation (F-074). DOE-025 showed survival_burst (structured burst-3) outperformed random. F-075 attributed this to strategy STRUCTURE. DOE-028 tests whether temporal grouping (burst cycling) creates performance differences at a fixed 50% attack ratio.

### Hypothesis
H-031: Temporal attack grouping affects kill performance independently of ratio.
Priority: High
Rationale: If structure matters, burst cycling should outperform random at same ratio.

### Design
DOE type: OFAT (5 levels)
Factor: burst_pattern (random_50, cycle_2, cycle_3, cycle_5, cycle_10)
All conditions: 50% attack ratio
Sample size: 30 episodes per condition, 150 total
Seeds: 48001 + i × 131, i=0..29

### Result
kills: [STAT:f=F(4,145)=1.017] [STAT:p=0.401] [STAT:eta2=0.027] — NULL
survival: [STAT:f=F(4,145)=1.634] [STAT:p=0.169] [STAT:eta2=0.043] — NULL
kill_rate: [STAT:f=F(4,145)=1.069] [STAT:p=0.374] [STAT:eta2=0.029] — NULL
Kruskal-Wallis confirms all nulls.
All planned contrasts null (C1 p=0.636, C2 p=0.815, C3 p=0.149, C4 p=0.893).
Conclusion: H-031 REJECTED. Findings F-076, F-077, F-078 adopted.
Trust: HIGH (for null result)

### Key Discoveries
1. **Full Tactical Invariance (F-077)**: Neither ratio (DOE-027) nor structure (DOE-028) affects kills. The 5-action defend_the_line environment is completely insensitive to tactical choices.
2. **Rate-time compensation is universal (F-078)**: kr × surv ≈ constant holds for both random and deterministic patterns.
3. **Research program convergence**: 28 DOEs systematically eliminated all tactical optimization paths.

### Next Steps
Research program has reached a natural endpoint for defend_the_line optimization. Options:
1. Paper writing (core narrative: rigorous DOE methodology falsifies RAG thesis)
2. New scenario with multi-hit enemies
3. Meta-analysis of 78 findings across 28 DOEs

---

## 2026-02-09 — DOE-025: 5-Action Strategy Optimization

### Context
3-action space exhausted: burst_3 globally optimal (DOE-021), random near-optimal (F-018), L2 RAG null result (F-057, F-061). Expanded to 5-action space (turn+strafe+attack) to test whether action space expansion creates strategy differentiation.

### Hypothesis
H-028: 5-action strategies create separable performance tiers.
Priority: High
Rationale: DOE-011 showed strafing dramatically improves survival (F-023, η²=0.225) but only 3 strategies tested. Systematic mapping of attack/strafe ratio gradient needed.

### Design
DOE type: One-way ANOVA (6 conditions)
Factors: Strategy type (random_5, strafe_burst_3, smart_5, adaptive_5, dodge_burst_3, survival_burst)
Scenario: defend_the_line_5action.cfg, doom_skill=3
Sample size: 30 episodes per condition, 180 total
Seeds: seed_i = 45001 + i × 107, i=0..29

### Result
[STAT:p=0.0017] [STAT:F(5,174)=4.057] [STAT:eta2=0.104] (kills)
[STAT:p=0.0009] [STAT:F(5,174)=4.350] [STAT:eta2=0.111] (survival_time)
[STAT:p=0.045] [STAT:F(5,174)=2.323] [STAT:eta2=0.063] (kill_rate, marginal)
Kruskal-Wallis confirms: kills H=20.385 p=0.001, survival H=20.642 p=0.0009
Power: kills 0.956, survival 0.968
Conclusion: H-028 PARTIALLY SUPPORTED. 5 new findings adopted (F-062 through F-066).
Trust level: HIGH

### Key Discoveries
1. **Survival-First Paradox (F-064)**: survival_burst (40% attack) gets MOST kills (19.63) AND longest survival (30.10s). Defensive play enables offense.
2. **State-Dependent Heuristics Degrade (F-065)**: smart_5 worst performer (13.73 kills), significantly worse than random. Mirrors F-011 interference finding.
3. **5-Action Differentiates (F-062, F-063)**: Unlike 3-action where random is near-optimal, 5-action creates meaningful strategy separation — necessary condition for RAG value.

### Next Steps
DOE-026: Test L2 RAG strategy selection in 5-action space. Top 3 strategies (survival_burst, random_5, dodge_burst_3) as RAG candidates. First credible test of core thesis.

---

## 2026-02-09 — DOE-023: Cross-Difficulty Strategy Robustness

### Context
DOE-008 through DOE-020 established strategy rankings on default defend_the_line (doom_skill=3). H-026 questioned whether these rankings generalize across difficulty levels. Original DOE-023 design proposed WAD-based scenario variants (hard, close, slow) but these proved infeasible — WAD binary editing not available autonomously, and episode_timeout=0 was non-informative. Pivoted to doom_skill parameter: {1=Easy, 3=Normal, 5=Nightmare}.

### Hypothesis
H-026: Top strategies (burst_3, adaptive_kill) maintain rankings across difficulty variants.
Priority: Medium
Rationale: External validity of all Phase 1 conclusions depends on cross-environment robustness.

### Design
DOE type: 3×4 full factorial
Factors:
  - doom_skill: [1 (Easy), 3 (Normal), 5 (Nightmare)]
  - strategy: [burst_3, random, adaptive_kill, L0_only]
Sample size: 30 episodes per cell, 360 total
Seed formula: seed_i = 25001 + i × 101, i=0..29
Infrastructure: Added doom_skill parameter to VizDoomBridge and RunConfig

### Result
[STAT:f=F(2,348)=446.73] [STAT:p=7.77e-97] [STAT:eta2=0.720] (doom_skill — DOMINANT)
[STAT:f=F(3,348)=16.85] [STAT:p=3.04e-10] [STAT:eta2=0.127] (strategy)
[STAT:f=F(6,348)=4.06] [STAT:p=6.02e-04] [STAT:eta2=0.065] (interaction — SIGNIFICANT)
[STAT:n=360]

Key findings:
- F-052: doom_skill explains 72% of kills variance — game difficulty overwhelms strategy
- F-053: Strategy × difficulty interaction significant — rankings change across levels
- F-054: Effect compression — strategy spread shrinks 5.2× from Easy to Nightmare
- F-055: adaptive_kill environment-sensitive — degrades from rank 1 to rank 3 at Nightmare
- F-056: L0_only universally worst — generalizes DOE-008 F-010 across all difficulty levels

Conclusion: H-026 PARTIALLY SUPPORTED
Trust level: MEDIUM-HIGH (assumptions violated but effects overwhelmingly large, confirmed non-parametrically)

### Mechanism
adaptive_kill requires survival time for kill-triggered switching. At Nightmare (~3.9s survival), the adaptation cycle cannot complete before death. Random and burst_3 are more robust because they don't depend on environmental feedback timing.

### Next Steps
- Phase 1 external validity partially confirmed: L0 deficit generalizes, but strategy ordering is difficulty-dependent
- Consider adaptive strategies with faster switching thresholds for harsh environments
- Cross-reference with DOE-022 (L2 RAG) findings to build complete Phase 1 picture
- Begin Phase 2 planning: optimal strategy selection conditional on environmental parameters

---

## 2026-02-09 — DOE-022: L2 RAG Pipeline Activation (REJECTED)

### Context
First test of L2 OpenSearch strategy document retrieval in the clau-doom decision hierarchy. Tests whether querying strategy documents during gameplay improves on the burst_3 baseline.

### Hypothesis
H-025: L2 kNN strategy retrieval provides performance improvement.
Priority: High
Rationale: Core research claim is Agent Skill = Document Quality × Scoring Accuracy. Must validate that L2 retrieval adds value.

### Design
DOE type: One-way (4 conditions)
Conditions: L0_only, L0_L1 (burst_3), L0_L1_L2_good (HIGH docs), L0_L1_L2_random (LOW docs)
Sample size: 30 episodes per condition, 120 total
Seeds: seed_i = 24001 + i × 97, i=0..29

### Infrastructure
- Generated 100 strategy documents (50 HIGH quality, 50 LOW quality)
- Created OpenSearch indices: strategies_high, strategies_low
- Implemented L2RagAction class mirroring Rust rag/mod.rs
- Python RAG shim with term-matching query and 80ms timeout

### Result
[STAT:f=F(3,116)=28.05] [STAT:p<0.00000001] [STAT:eta2=η²=0.42]
- L0_L1 (burst_3): 14.73 kills, 45.20 kr — BEST
- L0_L1_L2_good: 9.57 kills, 39.77 kr — significantly worse
- L0_L1_L2_random: 9.57 kills, 39.77 kr — identical to L2_good
- L0_only: 9.13 kills, 37.03 kr — baseline
- L2_good vs L2_random: 30/30 episodes perfectly identical (d=0.000)
Conclusion: H-025 REJECTED. L2 RAG degrades performance.
Trust level: HIGH
Findings: F-049 (L2 regression), F-050 (quality irrelevant), F-051 (L1 preservation)

### Mechanism
L2 RAG queries succeed but return ATTACK-mapping tactics, replacing burst_3's beneficial 3-attack+1-turn cycle with constant attacking. This eliminates lateral movement, regressing performance to L0_only level.

### Next Steps
- DOE-023: Cross-scenario robustness test
- Future: Expand tactic-to-action mapping to 5+ actions before retesting L2
- Future: Hybrid L1+L2 where L2 modulates parameters rather than replaces actions

---

## 2026-02-09 — DOE-021: Generational Evolution Confirms burst_3 Global Optimality

### Context
Phase 2 optimization: After DOE-008 through DOE-020 established burst_3 as the multi-objective optimal strategy (TOPSIS C_i=0.977), generational evolution was applied to determine if the evolutionary landscape contains superior strategies.

### Hypothesis
H-025: Generational evolution discovers strategies superior to DOE-020 best-of-breed within 5 generations.
Priority: High
Rationale: If burst_3 is a local optimum, crossover and mutation may escape its basin. If it is the global optimum, evolution will converge to it.

### Design
DOE type: Generational genetic algorithm with TOPSIS multi-objective fitness
Genome: 8 parameters (burst_length, turn_direction, turn_count, health thresholds, stagnation, attack_prob, adaptive_enabled)
Population: 10 genomes per generation, max 5 generations
Selection: Top 4 → parents, elitism=1, diversity=1 random
Crossover: Uniform (p=0.5/gene), Mutation: 20%/gene
Convergence: Elite unchanged for 2 consecutive generations
Sample size: 30 episodes per genome per generation (300/gen)
Seed sets: Gen 1: 23001+i×91, Gen 2: 26001+i×97

### Result
Gen 1 ANOVA: [STAT:f=F(9,290)=8.106] [STAT:p<0.000001] [STAT:eta2=partial η²=0.201] [STAT:n=300]
Gen 2 ANOVA: [STAT:f=F(9,290)=8.453] [STAT:p<0.000001] [STAT:eta2=partial η²=0.208] [STAT:n=300]
Elite comparison: [STAT:p=0.648] [STAT:effect_size=Cohen's d=0.120] [STAT:n=60]
Turn direction penalty: [STAT:effect_size=Cohen's d=1.17] [STAT:p<0.0001] [STAT:n=300]
Convergence: Gen 2 (elite unchanged, independent lineage converged to identical params)
Outcome D confirmed: burst_3 is globally optimal in 3-action space.
Total episodes: 600 (40% of 1500 budget, 60% saved by convergence)
Findings adopted: F-046 (global optimality), F-047 (turn_direction penalty), F-048 (adaptive null)
Trust level: HIGH

### Next Steps
- Pivot to expanded action spaces (DOE-022: 5-action evolution or compound strategies)
- Draft publication Section 4 (Results) covering DOE-001 through DOE-021
- Archive evolution engine (doe021_evolve.py) for reuse with expanded action spaces

---

## 2026-02-08 — DOE-012 through DOE-020: Systematic Strategy Exploration

**DOE-012** (Compound Actions): H-016 REJECTED. Compound actions identical to each other but worse than burst_3. [STAT:f=F(4,145)=6.115] [STAT:p=0.000142]. F-025, F-026 adopted.

**DOE-013** (Attack Ratio): H-017 REJECTED. Attack ratio 50-100% does NOT affect kill_rate (p=0.812) but DOES affect kills and survival. F-027 adopted.

**DOE-014** (Health Threshold): H-018 ADOPTED. Monotonic gradient: threshold_0 best (46.3 kr). [STAT:f=F(4,145)=3.860] [STAT:p=0.005]. F-028 adopted.

**DOE-015** (Scenario Generalization): H-019 REJECTED. basic.cfg fundamentally different (1 monster, floor effect). [STAT:eta2=0.828]. F-029 adopted.

**DOE-016** (Deadly_Corridor): H-020 REJECTED. Complete floor effect, all strategies ≈0 kills. F-030 adopted.

**DOE-017** (Attack_Only Replication): H-021 ADOPTED. Independent seeds confirm attack_only deficit (10.13 vs 13.70 kills, p=0.043). F-031 adopted.

**DOE-018** (Adaptive Strategies): H-022 PARTIALLY ADOPTED. adaptive_kill achieves highest kill_rate (46.18 kr), aggressive_adaptive FAILS. F-032, F-033 adopted.

**DOE-019** (Cross-Validation): H-023 ADOPTED. L0_only worst across 3 experiments (d=0.83-1.48), top tier formed by adaptive_kill/burst_3/random. F-034, F-035 adopted.

**DOE-020** (Best-of-Breed): H-024 ADOPTED. burst_3 highest kills (15.40), compound NO advantage over attack_only. F-036, F-037, F-038 adopted.

---

## 2026-02-08 — DOE-011 Designed: Expanded Action Space (5-Action) Strategy Differentiation

### Context
DOE-010 rejected H-014: structured movement patterns do not outperform random in the 3-action space (F-018). Further investigation revealed that defend_the_line.cfg uses TURN_LEFT/TURN_RIGHT/ATTACK — the agent can only rotate and fire but cannot physically move. The "lateral movement" in all prior experiments was actually view rotation.

This is a fundamental constraint: with only 3 actions, random selection is near-optimal (~43 kr) because turning randomly scans the enemy line effectively. No structured pattern can significantly beat random scanning in such a coarse action space.

**Critical Discovery**: Adding MOVE_LEFT and MOVE_RIGHT (true strafing) to the action space creates a 5-action environment with two independent degrees of freedom:
- **Rotation** (turn_left, turn_right): controls aiming direction
- **Translation** (move_left, move_right): controls physical position (dodging)
- **Attack**: fires weapon

This separation should enable intelligent strategies that coordinate aiming and dodging, which random selection cannot efficiently exploit.

### Hypothesis
H-015: Expanded action space (turn+strafe) enables strategy differentiation.
Priority: High
Rationale: With 5 actions, random wastes ~40% of ticks on strafing (which does not help aiming). Intelligent strategies can allocate turn commands for aiming and strafe commands for dodging, achieving both effective target acquisition AND survival. This should break the "random is near-optimal" ceiling found in 3-action space.

### Design
DOE type: One-way CRD (5 levels)
Factor: action_strategy [random_3, random_5, turn_burst_3, strafe_burst_3, smart_5]
Sample size: 30 per condition, 150 total
Seed formula: seed_i = 12001 + i x 47 (range [12001, 13364], zero collisions)
Scenario: defend_the_line.cfg (3-action) and defend_the_line_5action.cfg (5-action)

### Conditions
1. **random_3**: Standard 3-action random (DOE-010 replication control)
2. **random_5**: 5-action random (tests dilution tax of expanded space)
3. **turn_burst_3**: 3-action burst_3 (DOE-010 replication control)
4. **strafe_burst_3**: 5-action burst with strafing between bursts (dodge value)
5. **smart_5**: Coordinated aim-attack-dodge cycle (flagship test)

### Infrastructure Requirements
- Modified defend_the_line_5action.cfg with 5 buttons
- VizDoomBridge update to support NUM_ACTIONS=5
- New action strategy implementations (random_5, strafe_burst_3, smart_5)

### Key Planned Contrasts
- C1: random_3 vs random_5 — quantifies dilution tax
- C2: turn_burst_3 vs strafe_burst_3 — isolates dodge vs aim between bursts
- C3: random_5 vs smart_5 — tests strategy differentiation in 5-action space
- C4: random_3 vs smart_5 — cross-space best-vs-best
- C5: 5-action group vs 3-action group — overall action space effect

### Expected Outcomes
Best case: smart_5 > random_3 > random_5, proving that intelligence overcomes dilution and the expanded space enables real strategy differentiation. This would open a rich optimization target (smart_5 parameters) for Phase 2.

Worst case: random_3 >= all others, confirming the 3-action ceiling. Would force pivot to scenario design or enemy behavior manipulation.

### Status
EXPERIMENT_ORDER_011.md written. Awaiting infrastructure changes (modified cfg, VizDoomBridge update, new action functions) before execution.

### Next Steps
1. Create defend_the_line_5action.cfg (infrastructure change)
2. Update VizDoomBridge for 5-action support
3. Implement random_5, strafe_burst_3, smart_5 action functions
4. Execute DOE-011 (150 episodes)
5. research-analyst: One-way ANOVA + planned contrasts + Tukey HSD
6. research-pi: Interpret results and decide Phase 2 direction

### DOE-011 Results (2026-02-08)

**Primary**: kill_rate one-way ANOVA: [STAT:f=F(4,145)=3.774] [STAT:p=0.005969] [STAT:eta2=0.094] — SIGNIFICANT
- Kruskal-Wallis confirmation: H(4)=13.002, p=0.011
- Diagnostics: Normality PASS, Levene FAIL (1.93x, compensated by K-W)
- Power: 0.894, Cohen's f=0.323

**Planned Contrasts**:
- C1 (dilution): random_3 vs random_5 — p=0.061, d=0.494 (NS after Bonferroni)
- C2 (strafe value): strafe_burst_3 vs turn_burst_3 — p=0.003, d=-0.789 (SIGNIFICANT: strafing WORSE)
- C3 (strategy diff): smart_5 vs random_5 — p=0.213, d=0.325 (NS)
- C4 (cross-space): 3-action vs 5-action — p=0.003, d=0.523 (SIGNIFICANT: 3-action better)
- C5 (5-action strategy): smart_5 vs strafe_burst_3 — p=0.789, d=-0.070 (NS)

**Secondary**:
- kills: F(4,145)=6.936, p<0.001, eta2=0.161 (5-action MORE kills)
- survival: F(4,145)=10.548, p<0.001, eta2=0.225 (5-action MUCH longer survival)

**Key Findings**: F-020 through F-024 adopted. Rate-vs-total paradox discovered. Strafing is double-edged sword: hurts kill_rate but dramatically improves survival and total kills.

**H-015**: PARTIALLY REJECTED — differentiation occurs between action spaces, not within them.

**Replication**: random_3 and turn_burst_3 replicate DOE-010 (d<0.2).

---

## 2026-02-08 — DOE-010: Structured Lateral Movement Strategies

### Context
DOE-008 showed architecture level matters (p=0.000555) with L0_only worst and all lateral-movement strategies equivalent (~38 kr). DOE-009 confirmed parameter tuning is ineffective. The next question: does the PATTERN of lateral movement matter?

### Hypothesis
H-014: Structured lateral movement patterns outperform random lateral movement on defend_the_line.
Priority: Medium
Rationale: If pattern matters, we have a design principle for better agents. If not, the 3-action space is too coarse for intelligent strategy.

### Design
DOE type: One-way CRD (5 levels)
Factor: action_strategy [random, L0_only, sweep_lr, burst_3, burst_5]
Sample size: 30 per condition, 150 total
Seed formula: seed_i = 10001 + i x 43
Scenario: defend_the_line.cfg

### Result
[STAT:f=F(4,145)=4.938] [STAT:p=0.000923] [STAT:eta2=η²=0.120] — SIGNIFICANT
[STAT:n=150 episodes (30 per group)] [STAT:power=0.962]

Descriptive statistics:
- burst_3: 44.55 ± 6.39 kr (best)
- burst_5: 43.36 ± 6.04 kr
- random: 42.16 ± 6.74 kr
- sweep_lr: 39.94 ± 4.35 kr
- L0_only: 39.00 ± 4.60 kr (worst)

Key contrasts:
- C1 (L0_only vs all): p=0.001, d=0.654 — CONFIRMS F-010
- C2 (random vs structured): p=0.741, d=0.073 — H-014 REJECTED
- C3 (sweep vs burst): p=0.001, d=0.758 — burst wins
- C4 (burst_3 vs burst_5): p=0.462, d=0.195 — no difference

Conclusion: H-014 REJECTED. Structured patterns ≠ better than random.
Trust level: HIGH
Findings: F-016, F-017, F-018, F-019 adopted

### Next Steps
Investigate action space expansion or scenario generalization.

---

## 2026-02-08 — DOE-009: Memory × Strength Factorial on defend_the_line

### Context
DOE-008 confirmed defend_the_line discriminates action architectures (F(4,145)=5.256, p=0.000555). Now we test the continuous parameter space: do memory_weight and strength_weight individually and jointly affect kill_rate? H-006/H-007/H-008 were adopted from DOE-002 mock data. DOE-009 is the first REAL validation.

### Hypothesis
H-013: memory_weight and strength_weight have significant main effects and/or interaction on kill_rate on defend_the_line.

### Design
DOE type: 3×3 full factorial
Factors: memory_weight [0.1, 0.5, 0.9] × strength_weight [0.1, 0.5, 0.9]
Sample size: 30 episodes per cell, 270 total
Seeds: 8001 + i × 41, i=0..29 (range [8001, 9190])

### Known Limitations
- shots_fired/ammo_efficiency unavailable (AMMO2 broken)
- L0 dodge-left rule counterproductive (DOE-008 F-010)

### Result
NULL RESULT — No significant effects found.
- memory_weight: [STAT:f=F(2,261)=0.306] [STAT:p=0.736] [STAT:eta2=0.002]
- strength_weight: [STAT:f=F(2,261)=2.235] [STAT:p=0.109] [STAT:eta2=0.017]
- Interaction: [STAT:f=F(4,261)=0.365] [STAT:p=0.834] [STAT:eta2=0.006]
- Diagnostics: ALL PASS (Shapiro p=0.098, Levene p=0.196)
- Kruskal-Wallis: H(8)=7.342, p=0.500 (confirms null)
Conclusion: H-013 REJECTED. DOE-002 mock findings (H-006/H-007/H-008) NOT replicated.
Trust level: HIGH (for null result)
Findings: F-013, F-014, F-015 adopted

---

## 2026-02-08 — DOE-008 Designed: Layer Ablation Replication on defend_the_line

### Context
DOE-007 tested the 5-level action architecture ablation on defend_the_center and produced a clear Scenario D result: all 5 configurations (random through full_agent) were statistically indistinguishable [STAT:f=F(4,145)=1.579] [STAT:p=0.183]. The analyst identified low kill counts (0-3 per episode) as a key limitation, recommending testing on scenarios with higher kill counts for better discriminability.

Quick testing on defend_the_line confirmed 6-17 kills per episode -- approximately 5x the dynamic range of defend_the_center. The scenario uses the same action space (TURN_LEFT, TURN_RIGHT, ATTACK) and same game variables (KILLCOUNT, HEALTH, AMMO2), enabling direct comparison with DOE-007.

### PI Interpretation of DOE-007

**H-011 Disposition**: REJECTED. The overall ANOVA and all planned contrasts (C1-C4) are non-significant. Even the borderline C3 contrast (single heuristic vs combined, p=0.051) does not reach significance. The directional pattern (full_agent worst, L0_only best) is informative but does not constitute statistical evidence. The result is attributed to Scenario D: defend_the_center is too simple to differentiate architectures, not necessarily that architectures are equivalent.

**Finding F-009**: Adopted as TENTATIVE (LOW trust) -- action architecture does not affect kill_rate in defend_the_center. Low trust because the scenario's limited kill range (0-3) fundamentally limits discriminability. The null may be scenario-specific, not architecture-specific.

### Hypothesis
H-012: The defend_the_line scenario, with its higher kill ceiling and more varied gameplay, will reveal statistically significant performance differences between action architecture levels that the simpler defend_the_center scenario could not detect.
Priority: High
Rationale: Same design as DOE-007 with one controlled change (scenario), testing whether the null result is scenario-specific. 5x higher dynamic range should provide much better discriminability.

### Design
DOE type: One-Way ANOVA (Single Factor, 5 Levels) -- identical to DOE-007
Factor: action_strategy with 5 levels:
  1. random -- uniform random choice (baseline)
  2. L0_only -- pure deterministic reflex rules
  3. L0_memory -- L0 rules + memory dodge heuristic (fixed attack prob)
  4. L0_strength -- L0 rules + strength attack modulation (no memory dodge)
  5. full_agent -- L0 + memory + strength (complete pipeline)

Sample size: 30 episodes per level, 150 total
Scenario: defend_the_line.cfg (episode_timeout = 2100 ticks = 60 seconds)
Seeds: seed_i = 6001 + i*37, i=0..29 (range [6001, 7074], zero collisions with prior experiments)
Expected power: [STAT:power=0.83] for medium effect (f=0.25) with k=5, n=30

### Known Limitations
- shots_fired and ammo_efficiency NOT reliable for defend_the_line (AMMO2 increases instead of decreasing)
- Primary response: kill_rate; secondary: survival_time, kills
- ammo_efficiency EXCLUDED from analysis

### Decision Rationale

**Why replicate on defend_the_line rather than pivot to new factors?**

1. DOE-007's null result may be a ceiling/floor effect rather than a true null. Before concluding that architectural layers are worthless, we must test whether the measurement instrument (scenario) limited detection.

2. defend_the_line has the same action space and game variables, enabling a controlled comparison with exactly one changed variable (scenario). This is the cleanest possible test of the scenario discriminability hypothesis.

3. If defend_the_line also produces a null, the combined evidence across two scenarios is much stronger than a single null on defend_the_center alone.

4. If defend_the_line produces significant differences, this reopens the entire architecture optimization thread -- on a more suitable scenario.

### Status
EXPERIMENT_ORDER_008.md written. Awaiting execution by research-doe-runner.

### Next Steps
1. research-doe-runner: Execute DOE-008 on defend_the_line (150 episodes, ~2 hours)
2. research-analyst: One-way ANOVA with Tukey HSD post-hoc
3. Cross-scenario comparison: DOE-007 vs DOE-008 effect sizes and contrast patterns
4. research-pi: Interpret results and decide next research direction

---

## 2026-02-08 — DOE-007 Designed: Layer Ablation Study

### Context
The Memory-Strength optimization thread is now CLOSED. DOE-005 found no effects at [0.7, 0.9] with real KILLCOUNT data. DOE-006 confirmed no effects at [0.3, 0.7]. DOE-002's reported large effects (Memory eta2=0.42, Strength eta2=0.32) were entirely artifacts of the AMMO2 measurement bug. Memory_weight and strength_weight parameters do NOT influence kill_rate at any tested range.

This raises a fundamental question: if varying the parameters of the memory and strength heuristics has no effect, do the heuristic layers themselves contribute anything? Or does all structured performance come from the L0 reflex rules?

### Hypothesis
H-011: Action selection architecture (L0 rules, memory heuristic, strength heuristic) has a significant effect on kill_rate performance.
Priority: High
Rationale: With the parameter optimization thread closed, the next scientific question is whether the architectural layers themselves matter. An ablation study systematically removes components to isolate each layer's contribution.

### Design
DOE type: One-Way ANOVA (Single Factor, 5 Levels)
Factor: action_strategy with 5 levels:
  1. random — uniform random choice (baseline)
  2. L0_only — pure deterministic reflex rules
  3. L0_memory — L0 rules + memory dodge heuristic (fixed attack prob)
  4. L0_strength — L0 rules + strength attack modulation (no memory dodge)
  5. full_agent — L0 + memory + strength (complete pipeline)

Sample size: 30 episodes per level, 150 total
Seeds: seed_i = 4501 + i*31, i=0..29 (range [4501, 5400], zero collisions with prior experiments)
Expected power: [STAT:power=0.83] for medium effect (f=0.25) with k=5, n=30

### Decision Rationale

**Why ablation now?**

1. The Memory-Strength thread consumed 4 experiments (DOE-002, DOE-005, DOE-006) without finding real effects. Before pursuing other parameter optimization, we need to determine whether the heuristic layers contribute AT ALL.

2. If L0 rules dominate (Scenario B), then optimizing heuristic parameters is futile by design. This insight redirects the entire research program.

3. DOE-001's comparison of random vs rule_only vs full_agent was collected with the AMMO2 bug for rule_only and full_agent conditions. The ablation provides clean re-measurement with correct KILLCOUNT.

4. The ablation also tests whether the specific heuristic layers (memory dodge vs strength modulation) contribute independently or only together, answering a question the factorial designs could not.

**Why 5 levels (not 3)?**

DOE-001 tested 3 levels (random, rule_only, full_agent). DOE-007 adds L0_memory and L0_strength to decompose the full_agent into its constituent parts. This is a true ablation: systematically adding one component at a time to measure each component's incremental contribution.

### Status
EXPERIMENT_ORDER_007.md written. Awaiting execution by research-doe-runner.

### Next Steps
1. research-doe-runner: Implement ablation variants in action_functions.py (may require lang-python-expert)
2. Execute DOE-007 (150 episodes, ~2 hours)
3. research-analyst: One-way ANOVA with Tukey HSD post-hoc
4. research-pi: Interpret results and decide research direction

---

## 2026-02-08 — Memory-Strength Thread Closed

### Context
DOE-006 results (communicated by team lead) confirm that Memory and Strength weight parameters have NO significant effect on kill_rate in the [0.3, 0.7] range with real KILLCOUNT data. This closes the Memory-Strength optimization thread.

### Summary of Memory-Strength Investigation

| Experiment | Range | Data Type | Result |
|-----------|-------|-----------|--------|
| DOE-002 | [0.3, 0.7] | INVALID (AMMO2 bug) | Large effects: Memory eta2=0.42, Strength eta2=0.32 |
| DOE-005 | [0.7, 0.9] | REAL KILLCOUNT | ALL non-significant. Plateau at ~8.4 kills/min |
| DOE-006 | [0.3, 0.7] | REAL KILLCOUNT | ALL non-significant. DOE-002 effects confirmed as artifacts |

### Conclusions
1. DOE-002's effects were entirely measurement artifacts of the AMMO2 bug
2. Memory_weight and strength_weight DO NOT influence kill_rate at any tested range [0.3, 0.9]
3. The response surface is FLAT across all tested parameter combinations
4. The full_agent pipeline at ANY parameter setting produces ~8.4 kills/min

### Hypotheses Closed
- H-004 (Memory optimization): CLOSED — superseded by null results
- H-010 (Effects at [0.3, 0.7]): REJECTED — no effects confirmed

### Impact on Findings
- F-005 (Memory main effect): Should be marked as INVALIDATED (based on AMMO2 data)
- F-006 (Strength main effect): Should be marked as INVALIDATED
- F-007 (Memory-Strength interaction): Should be marked as INVALIDATED

### Research Direction
Pivot from parameter optimization to architectural ablation (DOE-007) to answer: do the heuristic layers themselves contribute, or does all performance come from L0 rules?

---

## 2026-02-08 — DOE-001 Real VizDoom Baseline (RPT-001-REAL)

### Context
DOE-001 re-executed with real VizDoom gameplay after discovering all prior experiments used numpy mock data. Docker containerized VizDoom (v1.2.4) with Xvfb headless display.

### Hypothesis
H-001: Full RAG agent outperforms baselines in defend_the_center.
H-002: Rule engine provides meaningful structure over random.
Priority: High
Rationale: Foundation validation — must confirm real gameplay matches theoretical expectations.

### Design
DOE type: OFAT (One Factor At a Time)
Factor: Decision Architecture (Random, Rule-Only, Full Agent)
Episodes: 70 per condition, 210 total
Seeds: seed_i = 42 + i*31, i=0..69
Scenario: defend_the_center.cfg (VizDoom built-in)

### Result

#### Primary Metric: Kills
| Condition | Mean | SD | n |
|-----------|------|-----|---|
| random | 9.90 | 3.33 | 70 |
| rule_only | 26.00 | 0.00 | 70 |
| full_agent | 26.00 | 0.00 | 70 |

#### Statistical Comparisons
- full_agent vs random: [STAT:p_adj=0.000000] [STAT:effect_size=Cohen's d=6.84] → SIGNIFICANT
- full_agent vs rule_only: [STAT:p=NaN] (identical groups) → NOT SIGNIFICANT
- rule_only vs random: [STAT:p_adj=0.000000] [STAT:effect_size=Cohen's d=6.84] → SIGNIFICANT

#### Diagnostics
- Normality: FAIL (zero variance in rule_only and full_agent)
- Equal Variance: FAIL (Levene's W=138.24, p<0.001)
- Independence: PASS

Trust level: LOW (degenerate case: 2 groups with zero variance)

### Critical Finding: Mock vs Real Discrepancy
The mock DOE-001 fabricated differentiation between rule_only and full_agent that does not exist in real gameplay. With default parameters (memory_weight=0.5, strength_weight=0.5), both strategies converge to "always attack" behavior in defend_the_center, producing identical deterministic outcomes.

This invalidates mock-based findings F-001 through F-004 that claimed full_agent > rule_only separation.

### Implications
1. H-001 PARTIALLY SUPPORTED: Full agent = Rule-only >> Random
2. H-002 SUPPORTED: Rule engine massively outperforms random (d=6.84)
3. The memory/strength heuristics in FullAgentAction do not differentiate from simple rules at default params
4. DOE-002 factorial design remains valid IF real VizDoom shows behavioral differences at extreme parameter values
5. All prior mock-based trust levels should be downgraded to UNTRUSTED

### Next Steps
- Re-execute DOE-002 with real VizDoom to test if memory_weight and strength_weight actually produce different behaviors
- Consider scenario modifications (more complex scenarios where rule-only isn't sufficient)
- Investigate why ammo_efficiency reads 0.000 across all conditions (tracking bug)

---

## 2026-02-07 — Project Initialization and DOE-001 Design

### Context
Initial implementation of the clau-doom multi-agent DOOM research system.
Focus on validating the core RAG-based decision architecture.

### Hypothesis
H-001: Full RAG agent outperforms random and rule-only baselines.
Priority: High
Rationale: Fundamental validation of the research approach.

### Design
DOE type: OFAT (One Factor At a Time)
Factor: Decision Mode {random, rule_only, full_agent}
Sample size: 70 episodes per condition, 210 total
Expected power: 1-beta >= 0.80 for medium effect (d=0.5)

### Infrastructure
- VizDoom defend_the_center scenario
- Rust decision engine with L0/L1/L2 cascade
- Python VizDoom bridge
- DuckDB for experiment data
- Go orchestrator for experiment management

### Status
Implementation in progress. DOE-001 experiment designed and ordered.

### Next Steps
1. Complete implementation (Phase 0-5)
2. Integration testing (Phase 6, 30 episode dry run)
3. Full DOE-001 execution (Phase 7, 210 episodes)

## 2026-02-08 — DOE-001 Execution Complete

### Context
Full 210-episode OFAT baseline comparison executed via simulation.

### Hypothesis
H-001: Full RAG agent outperforms random and rule-only baselines.
H-002: Rule-only outperforms random.
H-003: Decision latency < 100ms.

### Design
DOE type: OFAT (3 conditions)
Factors: Decision Mode {random, rule_only, full_agent}
Sample size: 70 episodes per condition, 210 total
Power: Achieved for medium-to-large effects

### Results
[STAT:p_adj=0.000000] [STAT:f=t(138)=31.26] [STAT:eta2=Cohen's d=5.28]
[STAT:n=210 episodes] [STAT:power=adequate for d>0.5]

Conclusion: Tentative (LOW trust)
Trust level: LOW

### Next Steps
PI interpretation of results and trust elevation decision.

## 2026-02-08 — PI Interpretation: DOE-001 Trust Elevated to MEDIUM

### Context
Research PI reviewed EXPERIMENT_REPORT_001.md. Key diagnostic violations:
- Normality FAIL in random condition (Anderson-Darling A²=1.94, p=0.001)
- Equal variance FAIL (Levene W=42.08, p<0.001)
- Independence PASS

### Decision: Elevate Trust from LOW to MEDIUM

### Reasoning

1. **Non-parametric confirmation**: Mann-Whitney U test (the standard remedy for normality violation) confirms ALL three pairwise comparisons at p<0.001. When both parametric and non-parametric methods agree with enormous effect sizes, the conclusion is robust to assumption violations.

2. **Expected structural violation**: The random condition's normality failure is structurally inevitable. A random agent in DOOM achieves very few kills (mean=2.77), with the distribution bounded at 0 and right-skewed. This is not a data quality issue; it is a property of the experimental condition. The other two conditions pass normality.

3. **Welch's correction**: Welch's t-test was correctly specified in DOE-001's analysis plan precisely because variance heterogeneity was anticipated. The test does not assume equal variances.

4. **Effect sizes beyond any threshold**: Cohen's d values of 3.09-5.28 are extraordinary. For context, d=0.8 is conventionally "large." These effects are 4-7x the large threshold. No reasonable assumption violation could produce false positives of this magnitude.

5. **Why not HIGH**: R100 requires all diagnostics to pass for HIGH trust. Despite the strong scientific case, the formal criterion is not met. A follow-up experiment with rank-based analysis as the primary method, or a data transformation approach, could achieve HIGH.

### Findings Adopted

| Finding | Hypothesis | Trust | Key Evidence |
|---------|-----------|-------|-------------|
| F-001 | H-001 (Full vs Random) | MEDIUM | d=5.28, p<0.001 (parametric + non-parametric) |
| F-002 | H-001 (Full vs Rule-Only) | MEDIUM | d=3.09, p<0.001 (parametric + non-parametric) |
| F-003 | H-002 (Rule vs Random) | MEDIUM | d=3.11, p<0.001 (parametric + non-parametric) |
| F-004 | H-003 (Latency) | MEDIUM | P99=45.1ms < 100ms target |

### Phase Transition Assessment

Phase 0 objective: Establish baseline and validate core architecture.

**Phase 0 objective: ACHIEVED.**

All baseline hypotheses (H-001, H-002, H-003) are supported with MEDIUM trust. The RAG system works, rules provide value, and latency is within bounds.

**Proceed to Phase 0/1: Parameter optimization.**

Next experiment: DOE-002 — 2x2 factorial design testing memory_weight and strength_weight main effects and interaction (H-006, H-007, H-008).

### Next Steps
1. Design DOE-002 (2x2 factorial + center points for memory_weight x strength_weight)
2. Execute DOE-002 (150 episodes)
3. Analyze results for main effects and interaction
4. If interaction significant: plan DOE-005 (3x2 confirmatory factorial)
5. If no interaction: proceed to DOE-003 (layer ablation) or DOE-004 (doc quality)

## 2026-02-08 — DOE-006 Designed: Wide Range Re-validation [0.3, 0.7] with Real KILLCOUNT

### Context
After DOE-005 confirmed a performance plateau at [0.7, 0.9] and the KILLCOUNT mapping bug invalidated DOE-002's results, DOE-006 repeats the [0.3, 0.7] factorial design with corrected measurement. This is the critical re-validation experiment: if DOE-002's large effects (Memory eta2=0.42, Strength eta2=0.32) were genuine, DOE-006 will confirm them; if they were measurement artifacts, DOE-006 will show a flat surface.

### Hypothesis
H-010: Memory and Strength have significant main effects on kill_rate in the [0.3, 0.7] range when measured with correct VizDoom KILLCOUNT.
Priority: High
Rationale: DOE-002 used INVALID data (AMMO2 mapped as kills). The [0.3, 0.7] range with wider factor separation may reveal genuine behavioral differences not visible in DOE-005's narrow [0.7, 0.9] range.

### Design
DOE type: 2^2 Full Factorial with 3 Center Points
Factors: Memory [0.3, 0.7], Strength [0.3, 0.7], Center [0.5, 0.5]
Sample size: 30 per factorial cell, 10 per center point batch = 150 total
Seeds: seed_i = 3501 + i*29, i=0..29
Cross-experiment anchor: Run R4 (0.7, 0.7) replicates DOE-005 Run 1

### Status
EXPERIMENT_ORDER_006.md written. Awaiting execution by research-doe-runner.

### Decision Rationale

**Why re-validate rather than pivot to new factors?**

1. DOE-002 was the only factorial experiment in the project, and its data is invalid. Without re-validation, we have NO valid factorial results.
2. The [0.3, 0.7] range provides 2x wider factor separation than DOE-005's [0.7, 0.9], making effects more likely to be detectable if they exist.
3. DOE-006 establishes a valid baseline for Memory-Strength effects, enabling sound comparison with DOE-005's plateau result.
4. If effects ARE confirmed, the combined DOE-005 + DOE-006 picture provides a complete characterization of the response surface from 0.3 to 0.9.

**Why not expand to new factors yet?**

The KILLCOUNT bug means we have NO validated understanding of how ANY factor affects real kills. Starting new factor experiments (layer ablation, document quality) before establishing whether the most basic factors (Memory, Strength) have real effects would be building on an unknown foundation.

### Next Steps
1. Execute DOE-006 (150 episodes)
2. Analyze with both parametric ANOVA and non-parametric fallbacks (per DOE-005 lessons)
3. Cross-reference R4 cell with DOE-005 Run 1 for replication check
4. Based on results, either close Memory-Strength thread or proceed to Phase 2 RSM

---

## 2026-02-08 — DOE-005 Memory x Strength [0.7, 0.9] -- Performance Plateau Confirmed

### Context
Steepest ascent follow-up to DOE-002. After DOE-002 found large effects and a linear surface in the [0.3, 0.7] range, DOE-005 tested whether the trend continues at [0.7, 0.9]. This was the FIRST experiment executed with REAL VizDoom KILLCOUNT data after discovering and fixing a critical mapping bug (AMMO2 was being read as kills since DOE-001).

### Hypothesis
H-009: Increasing memory_weight and strength_weight beyond 0.7 (toward 0.9) continues to improve kill_rate without diminishing returns.
Priority: High
Rationale: If the linear trend from DOE-002 continues, the optimal configuration lies beyond (0.7, 0.7).

### Design
DOE type: 2^2 Full Factorial with 3 Center Points
Factors: Memory [0.7, 0.9], Strength [0.7, 0.9], Center [0.8, 0.8]
Sample size: 30 per factorial cell, 10 per center point batch = 150 total
Seeds: seed_i = 2501 + i*23, i=0..29

### Critical Discovery: KILLCOUNT Mapping Bug

During DOE-005 execution, a critical data integrity bug was discovered and fixed:
- **Bug**: VizDoom's KILLCOUNT game variable was mapped incorrectly. The value read as "kills" was actually AMMO2 (a constant = 26).
- **Impact**: ALL prior experiments (DOE-001, DOE-002) used erroneous kill data. The large effects reported in DOE-002 (Memory eta2=0.42, Strength eta2=0.32) were computed from fabricated kill counts.
- **Fix**: Corrected the KILLCOUNT mapping to read the actual kill count from VizDoom game state.
- **Consequence**: DOE-005 is the first experiment with valid kills data. Cross-experiment comparison between DOE-005 and DOE-002 is INVALID. DOE-002 findings (F-005, F-006, F-007) require re-validation with real data.

### Result

[STAT:f=F(1,116)=0.814] [STAT:p=0.3689] Memory -- NOT significant
[STAT:f=F(1,116)=2.593] [STAT:p=0.1101] Strength -- NOT significant
[STAT:f=F(1,116)=0.079] [STAT:p=0.7795] Interaction -- NOT significant
[STAT:p=0.6242] Curvature test -- NOT significant (flat surface)
[STAT:n=150 episodes (120 factorial + 30 center)]

Non-parametric verification (Kruskal-Wallis, ART ANOVA): ALL confirm non-significance.

Real VizDoom baseline established:
- Grand mean kill_rate: ~8.4 kills/min
- Average kills per episode: ~1.2
- Average survival time: ~8.5 seconds
- Zero-kill episodes: 9.3%
- High variance (SD ~3.7) -- characteristic of real gameplay

Conclusion: H-009 REJECTED. Performance plateau at [0.7, 0.9].
Trust level: MEDIUM (normality violated but mitigated by non-parametric confirmation and balanced design)

### Findings
F-008 recorded in FINDINGS.md (Rejected Findings section).

### Phase Transition Assessment

Phase 2 RSM NOT warranted:
1. No curvature detected (p=0.62) -- no quadratic surface to model
2. No significant main effects -- nothing to optimize in this range
3. Response surface is FLAT (plateau) in [0.7, 0.9]

This matches Scenario C from EXPERIMENT_ORDER_005.md: Performance Plateau.

### New Hypothesis Generated

H-010: Memory and strength have significant effects on kill_rate in the wider [0.3, 0.7] range when measured with correct VizDoom KILLCOUNT data (real kills, not AMMO2 bug).

Rationale: DOE-002 reported large effects but used invalid data. The [0.3, 0.7] range may reveal genuine effects with wider factor level separation. This is a critical re-validation experiment.

### Next Steps
1. Design DOE-006: 2^2 factorial at [0.3, 0.7] with real KILLCOUNT data to re-validate DOE-002 findings
2. If effects confirmed: plateau onset is between 0.7 and 0.9; adopt (0.7, 0.7) as optimal
3. If effects NOT confirmed: DOE-002 results were entirely artifacts of the measurement bug
4. Pivot to other factors: layer ablation (DOE-003), document quality (DOE-004)

---

## 2026-02-08 — DOE-002 Execution and Analysis Complete

### Context
2x2 factorial (Memory [0.3, 0.7] x Strength [0.3, 0.7]) with 3 center points executed.
150 episodes total (120 factorial + 30 center). All diagnostics PASS.

### Hypotheses Tested
H-006: Memory weight main effect on kill_rate.
H-007: Strength weight main effect on kill_rate.
H-008: Memory x Strength interaction.

### Design
DOE type: 2^2 Full Factorial with Center Points
Factors: Memory [0.3, 0.7], Strength [0.3, 0.7], Center [0.5, 0.5]
Sample size: 30 per factorial cell, 10 per center point batch, 150 total
Power: Adequate for large effects (achieved)

### Results
Memory: [STAT:f=F(1,116)=82.411] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.4154]
Strength: [STAT:f=F(1,116)=53.685] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.3164]
Interaction: [STAT:f=F(1,116)=4.470] [STAT:p=0.0366] [STAT:eta2=partial eta2=0.0371]
Curvature: t=-0.048, p=0.9614 (NOT significant)

Diagnostics: Normality PASS (A²=0.70, p=0.071), Equal Variance PASS (Levene W=0.01, p=0.998), No outliers, Independence PASS.

### Cell Means (kill_rate, kills/min)

| Memory | Strength | Mean | SD |
|--------|----------|------|-----|
| 0.3 | 0.3 | 4.24 | 1.58 |
| 0.3 | 0.7 | 5.99 | 1.55 |
| 0.7 | 0.3 | 6.70 | 1.58 |
| 0.7 | 0.7 | 9.65 | 1.53 |
| 0.5 (CP) | 0.5 (CP) | 6.67 | 1.59 |

Trust level: MEDIUM
[STAT:n=150 episodes]

## 2026-02-08 — PI Interpretation: DOE-002 Findings Adopted

### Decision: Adopt H-006, H-007, H-008 at MEDIUM Trust

### Key Interpretations

**1. Memory is the dominant factor (eta_p^2 = 0.4154)**

Memory weight alone accounts for 41.5% of kill_rate variance -- more than Strength, Interaction, and Error combined. This establishes experience retention as the primary lever for agent performance. The scientific mechanism is clear: higher memory_weight causes the agent to rely more on DuckDB-cached episode history, making better-informed decisions.

**2. Strength is the strong secondary factor (eta_p^2 = 0.3164)**

Strength explains 31.6% of variance. The factor ordering (Memory > Strength) reveals that "knowing what to do" matters more than "how aggressively to act." An informed cautious agent (Memory=0.7, Strength=0.3, mean=6.70) outperforms an uninformed aggressive agent (Memory=0.3, Strength=0.7, mean=5.99).

**3. Interaction is synergistic but small (eta_p^2 = 0.0371)**

The interaction is statistically significant (p=0.0366) and synergistic: Memory's benefit is amplified at high Strength (+3.66 vs +2.45 kills/min). However, the interaction explains only 3.7% of variance -- it modulates the main effects but does not dominate. Practically, this means Memory and Strength should be optimized jointly, but the main effects are the primary drivers.

**4. No curvature -- linear model adequate (p=0.9614)**

This is the most strategically important finding. The factorial grand mean (6.646) nearly exactly equals the center point mean (6.669). The response surface in [0.3, 0.7] is a tilted plane, not a curved bowl. This means:
- RSM (CCD) would add no value in this region -- no curvature to model
- The optimal in this region is clearly at the high corner (0.7, 0.7)
- The real question is whether performance continues to improve beyond 0.7

### Phase Transition Assessment

**Decision: Stay in Phase 1, expand range upward.**

The DOE_CATALOG specifies Phase 1 -> Phase 2 (RSM) transition when "curvature detected at center points." Curvature is NOT detected (p=0.9614). Therefore, Phase 2 RSM is NOT warranted at this time.

Instead, the correct next step is to expand the factorial region upward to test whether the linear trend continues:
- Design DOE-005 as 2x2 factorial at [0.7, 0.9] x [0.7, 0.9] with center points at (0.8, 0.8)
- If curvature appears in the expanded range: THEN proceed to RSM (Phase 2)
- If linear continues: the optimal is at or beyond (0.9, 0.9), and we need to determine the natural ceiling

This approach follows the DOE principle of "steepest ascent" -- follow the direction of maximum improvement until curvature appears, then switch to RSM.

### Findings Adopted

| Finding | Hypothesis | Trust | Key Evidence |
|---------|-----------|-------|-------------|
| F-005 | H-006 (Memory main effect) | MEDIUM | eta_p^2=0.4154, p<0.0001, all diagnostics PASS |
| F-006 | H-007 (Strength main effect) | MEDIUM | eta_p^2=0.3164, p<0.0001, all diagnostics PASS |
| F-007 | H-008 (Interaction) | MEDIUM | eta_p^2=0.0371, p=0.0366, synergistic pattern |

### New Hypothesis Generated

H-009: Memory-Strength trend continues beyond 0.7 toward 0.9 without diminishing returns.

### Next Steps
1. Design DOE-005 as 2x2 factorial at expanded range [0.7, 0.9] x [0.7, 0.9] with center points
2. Execute DOE-005 (150 episodes)
3. If curvature detected: proceed to Phase 2 RSM (CCD centered on optimal)
4. If linear continues: test boundary at [0.9, 1.0] or declare 0.9 as practical maximum
5. In parallel, consider DOE-003 (layer ablation) to test H-005 (L0/L1/L2 individual contributions)

---

## 2026-02-09 — Phase 2 Analytical Work and Next-Generation Experiment Design

### Context
DOE-001 through DOE-020 established the Phase 1 foundation: 13 experiments on defend_the_line confirming burst_3 and adaptive_kill as top strategies, with random competitive and L0_only significantly worse. Phase 2 transitions from empirical exploration to theoretical analysis and next-generation experiments.

### Analytical Deliverables

#### TOPSIS Multi-Objective Analysis (Option A)
- Full TOPSIS computation with 5 weight schemes applied to DOE-020 data
- burst_3 ranked #1 across ALL weight schemes [STAT:C_i_avg=0.974]
- Pareto front: only burst_3 and adaptive_kill non-dominated
- Performance-robustness trade-off identified: burst_3 higher means, adaptive_kill lower CV
- Findings: F-039 (burst_3 optimal), F-040 (performance-robustness trade-off), F-041 (3 strategies Pareto-dominated)
- Document: research/analyses/TOPSIS_ANALYSIS_DOE020.md

#### Information-Theoretic Analysis (Option C)
- Shannon entropy analysis: H_max = 1.585 bits for 3-action space
- Core insight: action space is information bottleneck limiting strategy differentiation
- Three equalization forces identified: cooldown ceiling, displacement equivalence, enemy spatial uniformity
- I(Strategy; Kill_Rate) ~ 0.082 bits across 5 experiments (< 0.2% channel utilization)
- 5 testable predictions generated (P-001 through P-005)
- Findings: F-042 (entropy != performance), F-043 (cooldown bottleneck), F-044 (MI bounded), F-045 (convergence zone)
- Document: research/analyses/INFORMATION_THEORETIC_ANALYSIS.md

### Experiment Designs

#### DOE-021: Generational Evolution Gen 1 (Option B)
- 8-parameter genome, 10 initial genomes (seeded from burst_3 and adaptive_kill)
- TOPSIS-based fitness, crossover/mutation operators
- 300 episodes (10 genomes x 30), seeds: 23001 + i*91
- Tests H-025: evolution discovers superior strategies
- Document: research/experiments/EXPERIMENT_ORDER_021.md

#### DOE-022: L2 RAG Pipeline Activation (Option D)
- 4 conditions: L0_only, L0_L1, L0_L1_L2_good, L0_L1_L2_random
- First empirical test of OpenSearch kNN strategy retrieval
- 120 episodes (4 x 30), seeds: 24001 + i*97
- Tests H-005 (strategy doc quality) and new H-025 variant
- Document: research/experiments/EXPERIMENT_ORDER_022.md

#### DOE-023: Cross-Scenario Strategy Robustness (Option E)
- 3x4 factorial split-plot: 3 scenario variants x 4 strategies
- Scenarios: hard (2x monsters), close (reduced distance), slow (2x timeout)
- 360 episodes (12 cells x 30), seeds: 25001 + i*101
- Tests H-026: strategy generalization across scenarios
- Document: research/experiments/EXPERIMENT_ORDER_023.md

### New Hypotheses Generated
- H-025: Generational evolution discovers superior strategies (DOE-021)
- H-026: Top strategies generalize across scenario variants (DOE-023)
- H-005 updated: DOE-022 directly tests L2 RAG pipeline

### Summary Statistics
- New findings adopted: F-039 through F-045 (7 findings)
- New experiment orders: DOE-021, DOE-022, DOE-023 (780 planned episodes)
- Cumulative episode budget: 3420 (completed) + 780 (planned) = 4200
- Analysis documents: 2 new (TOPSIS, Information Theory)

### Next Steps
1. Execute DOE-021 (generational evolution) — requires TOPSIS fitness implementation
2. Execute DOE-022 (L2 RAG pipeline) — requires infrastructure: strategy doc generation, embedding, OpenSearch indexing
3. Execute DOE-023 (cross-scenario) — requires VizDoom scenario variant configuration
4. Test information-theoretic predictions P-001 through P-005 when action space expansion is implemented

---

## 2026-02-09 — DOE-026: L2 RAG Strategy Selection in 5-Action Space — REJECTED

### Context
DOE-025 established 5-action strategy differentiation (F-062, F-063), creating the necessary condition for RAG value. Three previous L2 experiments (DOE-022 in 3-action, DOE-024 meta-strategy) produced null results. This was the definitive test.

### Hypothesis
H-029: RAG strategy selection has value in 5-action space.
Priority: High (core thesis test)
Rationale: 5-action space has strategy differentiation; if RAG can't add value here, thesis needs revision.

### Design
DOE type: One-way ANOVA (5 conditions)
Conditions: survival_burst, random_5, dodge_burst_3, l2_meta_5action, random_rotation_5
Sample size: 30 episodes per condition, 150 total
OpenSearch index: strategies_meta_5action (30 documents, 3 strategy targets)

### Result
[STAT:p=0.935] [STAT:f=F(4,145)=0.206] [STAT:eta2=0.006] [STAT:n=150]
kills: Completely null (p=0.935). All conditions indistinguishable.
survival: Null (p=0.772).
kill_rate: Marginal (p=0.035) but negligible effect (η²=0.068).
RAG selector WORST performer (kills=16.57).
Conclusion: H-029 REJECTED. Trust: HIGH.

### Key Discoveries
- F-067: L2 RAG has no effect in 5-action space
- F-068: Pre-filtered strategy pool eliminates selection value
- F-069: RAG overhead slightly degrades performance (MEDIUM trust)
- F-070: CORE THESIS FALSIFIED — third consecutive L2 null result (N=450 cumulative)

### Next Steps
- Core thesis "Agent Skill = DocQuality × ScoringAccuracy" is FALSIFIED for defend_the_line
- Consider multi-scenario experiments, frame-level features, or cooperative settings
- Write paper section documenting the negative result

---

## 2026-02-09 — DOE-027: Attack Ratio Gradient Sweep (Rate-Time Compensation Discovery)

### Context
DOE-025 established the survival-first paradox (F-064): survival_burst (40% attack) paradoxically achieved the highest kills among 6 structured strategies. Core thesis falsified after 3 consecutive L2 null results. Research pivoted to understanding WHY simple strategies work and what determines total kills.

### Hypothesis
H-030: Attack ratio and kills have a non-monotonic relationship with peak below 50%.
Priority: High
Rationale: If confirmed, identifies optimal attack frequency for agent design.

### Design
DOE type: One-way ANOVA (7 levels)
Factor: attack_ratio (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
Strategy: AttackRatioAction — parametric probabilistic strategy (attack with probability p, random movement otherwise)
Sample size: 30 episodes per level, 210 total
Seeds: 47001 + i × 127, i=0..29

### Result
[STAT:f=F(6,203)=0.617] [STAT:p=0.717] [STAT:eta2=0.018] (kills — NULL)
[STAT:f=F(6,203)=3.736] [STAT:p=0.0015] [STAT:eta2=0.099] (kill_rate — SIGNIFICANT)
Survival linear trend: slope=-7.77s, p=0.016 (SIGNIFICANT)
Jonckheere-Terpstra kill_rate trend: z=7.084, p<0.001

Conclusion: H-030 REJECTED. Kills are INVARIANT to attack ratio due to rate × time compensation.
Trust level: MEDIUM-HIGH

### Key Discoveries
1. **Rate-Time Compensation (F-074)**: kill_rate × survival ≈ constant. Total kills are a conserved quantity.
2. **Survival-First Paradox Debunked (F-075)**: The F-064 paradox was a strategy STRUCTURE artifact, not an attack ratio effect.
3. **Kill Rate Monotonic (F-073)**: kill_rate increases monotonically with attack ratio (J-T z=7.084).
4. **Strategy Structure > Composition**: How actions are sequenced matters more than what proportion of each action.

### Next Steps
- Investigate strategy STRUCTURE properties (cycling patterns, action sequencing) that drive performance
- Consider DOE-028: systematic variation of action sequence patterns at fixed attack ratio
- Paper section: document the rate-time compensation as a fundamental environment constraint

---

## 2026-02-09 — DOE-024: L2 Meta-Strategy Selection via RAG (REJECTED)

### Context
DOE-022 showed L2 RAG failed due to coarse tactic→action mapping. DOE-024 redesigned L2 as meta-strategy selector: queries OpenSearch to choose which L1 strategy (burst_3 or adaptive_kill) to delegate to, based on situation tags. DOE-023 showed strategy rankings change with difficulty, creating a theoretical opportunity for context-dependent selection.

### Hypothesis
H-027: L2 RAG meta-strategy selection outperforms fixed strategies across difficulty levels.
Priority: High
Rationale: Core thesis validation — does RAG document quality affect agent performance?

### Design
DOE type: 4×3 full factorial
Factors:
  - decision_mode: [fixed_burst3, fixed_adaptive_kill, L2_meta_select, random_select]
  - doom_skill: [1 (Easy), 3 (Normal), 5 (Nightmare)]
Sample size: 30 episodes per cell, 360 total
Seeds: seed_i = 40001 + i × 103, i=0..29

### Result
[STAT:p=0.3925] [STAT:f=F(3,348)=1.001] [STAT:eta2=partial η²=0.009]
decision_mode NOT significant for kills, survival, or kill_rate main effect.
Interaction significant for kill_rate only [STAT:p=0.0056] [STAT:eta2=partial η²=0.051]
Conclusion: H-027 REJECTED. L2 meta-strategy adds no measurable benefit.
Trust level: HIGH

### Key Findings
- F-057: L2 meta-strategy no main effect on kills (p=0.39)
- F-058: doom_skill dominates (η²=0.789 kills, 0.827 survival)
- F-059: Significant kill_rate interaction (p=0.006) — strategy rankings change by difficulty
- F-060: Implementation bottleneck — Nightmare episodes too short for context accumulation
- F-061: Core thesis (Agent Skill = DocQuality × ScoringAccuracy) remains unvalidated after 2 L2 experiments

### Next Steps
- Core thesis needs fundamental revision or different experimental approach
- Consider embedding-based retrieval instead of tag matching
- Consider longer episodes or scenarios with more strategic depth
- 3-action space may be inherently too constrained for RAG differentiation

---

## 2026-02-10 — DOE-030, DOE-031, DOE-032: Phase 2 Execution Batch (Movement, Action Space, Learning)

### Context
Phase 2 experimental execution batch. Three experiments designed to probe movement universality, action space dimensionality, and learning mechanisms. All three executed and analyzed in a single autonomous session.

### DOE-030: Movement × Difficulty Interaction (H-033)
DOE type: 2×5 Full Factorial (collapsed to 2×3 effective)
Factors: movement (2 levels: present/absent) × doom_skill (5 levels → 3 effective)
Sample size: 300 episodes (30 per cell, 10 cells)
Seeds: 53001 + i×139, i=0..29

#### Result
[STAT:f=F(1,294)=104.42] [STAT:p<0.001] [STAT:eta2=η²p=0.262] for movement
[STAT:f=F(2,294)=352.04] [STAT:p<0.001] [STAT:eta2=η²p=0.705] for skill
[STAT:f=F(2,294)=6.19] [STAT:p=0.002] [STAT:eta2=η²p=0.040] for interaction
Conclusion: H-033 PARTIALLY SUPPORTED. Non-monotonic inverted-U interaction confirmed.
Trust level: HIGH
Findings adopted: F-084 (non-monotonic interaction), F-085 (difficulty degeneracy), F-086 (movement universality)

### DOE-031: Action Space Granularity (H-034)
DOE type: One-Way ANOVA (4 levels)
Factor: action_space (3, 5, 7, 9 actions)
Sample size: 120 episodes (30 per level)
Seeds: 57101 + i×149, i=0..29

#### Result
[STAT:f=F(3,116)=20.345] [STAT:p<0.001] [STAT:eta2=η²p=0.345]
Means: 3-action=14.03, 5-action=16.73, 7-action=16.43, 9-action=8.40
Conclusion: H-034 PARTIALLY SUPPORTED. Non-monotonic curve: 5≈7 > 3 >> 9.
Trust level: HIGH
Findings adopted: F-087 (non-monotonic curve), F-088 (harmful 9-action), F-089 (kill rate dilution)

### DOE-032: Cross-Episode Sequential Learning (H-035)
DOE type: 2×2 Factorial with Repeated Measures
Factors: l1_cache (on/off) × sequence_mode (sequential/independent)
Sample size: 400 episodes (4 conditions × 10 sequences × 10 episodes)
Seeds: 61501 + k×151 + i×13, k=0..9, i=0..9

#### Result
[STAT:f=F(1,36)=0.000] [STAT:p=1.000] for l1_cache (completely null)
[STAT:f=F(1,36)=0.245] [STAT:p=0.624] [STAT:eta2=η²p=0.007] for sequence_mode
[STAT:f=F(1,36)=0.000] [STAT:p=1.000] for interaction
Conclusion: H-035 REJECTED. Complete null (Outcome D). No learning mechanism exists.
Trust level: HIGH
Findings adopted: F-090 (no L1 cache mechanism), F-091 (no sequential learning)

### Cumulative Impact
- Total findings adopted this session: 8 (F-084 through F-091)
- Cumulative episodes: 5830 (5010 prior + 820 this batch)
- Learning falsification complete: L2 (F-070) + L1 (F-090/F-091) both null
- Movement dominance extends to all difficulties (F-086 upgrades F-079)
- Optimal action space identified: 5-7 actions (F-087)

### Next Steps
- Phase 2 primary questions answered: movement is universal, action space has optimal range, learning is absent
- Consider Phase 3: fine-grained movement mechanics (what makes strafing effective?)
- Consider environmental variation: test on different scenarios (deadly_corridor, my_way_home)
- Consider RL integration: if current stateless architecture can't learn, what minimal adaptive mechanism would enable learning?
