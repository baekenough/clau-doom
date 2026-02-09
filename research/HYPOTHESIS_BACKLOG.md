# Hypothesis Backlog

## Active Hypotheses

### H-011: Action Selection Architecture Has Significant Effect on Kill Rate [CLOSED -- Scenario D confirmed, superseded by H-012]
**Statement**: Action selection architecture (L0 rules, memory heuristic, strength heuristic) has a significant effect on kill_rate performance in defend_the_center. Specifically, the layer ablation study tests whether the memory dodge heuristic and/or strength attack probability modulation provide measurable improvement over bare L0 reflex rules.
**Rationale**: DOE-005 and DOE-006 both found NO significant effect of memory_weight and strength_weight on kill_rate, closing the Memory-Strength optimization thread. This raises a fundamental question: do these heuristic layers contribute anything at all? An ablation study (DOE-007) isolates each layer's contribution.
**Status**: CLOSED — Scenario D confirmed (defend_the_center too simple). Superseded by H-012 (defend_the_line replication).
**Date Added**: 2026-02-08
**Date Analyzed**: 2026-02-08
**Date Closed**: 2026-02-08
**Linked Experiment**: DOE-007
**Result Summary**: One-way ANOVA NOT significant [STAT:f=F(4,145)=1.579] [STAT:p=0.183] [STAT:eta2=0.042]. Kruskal-Wallis also non-significant (p=0.503). No architectural configuration significantly outperforms any other. Random agent performs comparably to all structured agents. Full_agent (combined heuristics) is paradoxically the WORST performer (mean=6.74 vs L0_only mean=9.08, d=0.685 medium). Scenario D: defend_the_center lacks discriminability.

### H-005: Strategy Document Quality Matters [MEDIUM PRIORITY]
**Statement**: Higher quality strategy documents (higher confidence_tier) lead to better agent performance.
**Rationale**: Validates the RAG curation pipeline importance. If document quality does not matter, the refinement pipeline is unnecessary overhead.
**Status**: Experiment ordered (DOE-022: L2 RAG Pipeline Activation)
**Date Added**: 2026-02-07
**Update 2026-02-09**: DOE-022 (L2 RAG Pipeline Activation) will directly test this hypothesis by comparing L0_L1_L2_good vs L0_L1_L2_random conditions.


### H-015: Expanded Action Space (Turn+Strafe) Enables Strategy Differentiation [PARTIALLY REJECTED]
**Statement**: When both turning (aim) and strafing (dodge) actions are available in defend_the_line, structured strategies will outperform random selection, unlike with the turn-only 3-action space where random is near-optimal.
**Rationale**: With only 3 actions (turn_left, turn_right, attack), random selection achieves ~43 kr because turning is inherently a scanning mechanism where random is near-optimal (F-018). With 5 actions (add move_left, move_right for strafing), random wastes ~40% of ticks on movement instead of attack/turn, while intelligent strategies can separate aiming (turn) from dodging (strafe) and attack timing. The extra degrees of freedom should create separable performance tiers.
**Critical Context**: The "MOVE_LEFT/MOVE_RIGHT" in VizDoomBridge code are actually TURN_LEFT/TURN_RIGHT in defend_the_line.cfg. Adding true MOVE_LEFT/MOVE_RIGHT buttons creates a 5-action space with two independent degrees of freedom (rotation and translation).
**Status**: Partially Rejected (DOE-011)
**Evidence**: EXPERIMENT_REPORT_011.md, F-020 through F-024
**Result**: Action space expansion creates inter-space differentiation (3-action vs 5-action, C4: p=0.003) but NOT intra-space differentiation (smart_5 vs random_5, C3: p=0.213). Strafing hurts kill_rate (C2: p=0.003) but dramatically improves survival (F-023, eta2=0.225).
**Trust**: HIGH for significant findings, MEDIUM for null findings
**Date**: 2026-02-08
**Date Added**: 2026-02-08
**Linked Experiment**: DOE-011
**Key Contrasts**:
- C1: random_3 vs random_5 (dilution effect of action space expansion)
- C2: turn_burst_3 vs strafe_burst_3 (value of dodging vs turning between bursts)
- C3: random_5 vs smart_5 (strategy differentiation in expanded space)
- C4: random_3 vs smart_5 (cross-space best-vs-best comparison)
- C5: 5-action group vs 3-action group (overall action space effect)

### H-014: Structured Lateral Movement Outperforms Random [REJECTED]
**Statement**: Structured lateral movement patterns (sweep, burst-fire) produce higher kill_rate than random lateral movement on defend_the_line.
**Rationale**: DOE-008 showed ANY lateral movement helps equally (~38 kr), but all tested strategies used reactive/probabilistic movement. Deterministic patterns (sweep, burst) may provide better enemy line coverage or more efficient attack windows.
**Evidence**: RPT-010, F-016, F-017, F-018, F-019
- Overall ANOVA: [STAT:f=F(4,145)=4.938] [STAT:p=0.000923] [STAT:eta2=0.120]
- C2 contrast (random vs structured): t=-0.332 [STAT:p=0.741] [STAT:effect_size=Cohen's d=0.073] — NOT significant
- Burst strategies MATCH random but do not exceed it
- sweep_lr ≡ L0_only (Tukey p=0.968) — oscillation is not movement
- Kruskal-Wallis confirms: H(4)=17.438 [STAT:p=0.001589]
**Trust**: HIGH (for rejection — all diagnostics pass, power 0.962, non-parametric confirms)
**Date Added**: 2026-02-08
**Linked Experiment**: DOE-010
**Key Findings**: F-016 (replication), F-017 (oscillation≡stasis), F-018 (H-014 rejected), F-019 (displacement hierarchy)

### H-025: Generational Evolution Discovers Superior Strategies [PARTIALLY REJECTED]
**Statement**: Evolutionary optimization using TOPSIS-based fitness with crossover and mutation can discover agent configurations that outperform the current best individual strategies (burst_3, adaptive_kill) within 5 generations.
**Rationale**: DOE-020 identified burst_3 and adaptive_kill as Pareto-optimal. Evolution can explore the space between and beyond these strategies by combining their genomes through crossover and mutation. If the performance convergence zone (F-045) is a true ceiling, evolution will confirm this by converging to existing optima. If room exists above the zone, evolution may find it.
**Status**: Outcome D confirmed — Convergence at Gen 2, burst_3 is globally optimal in 3-action space
**Evidence**: RPT-021, F-046, F-047, F-048
**Trust**: HIGH
**Date Added**: 2026-02-09
**Date Resolved**: 2026-02-09
**Linked Experiment**: DOE-021
**Key Findings**: F-046 (convergence, global optimality), F-047 (turn_direction penalty d=1.17), F-048 (adaptive switching null)


## Queued Hypotheses

## Completed Hypotheses

### H-026: Top Strategies Generalize Across Scenario Variants [PARTIALLY SUPPORTED]
**Statement**: burst_3 and adaptive_kill maintain their relative performance rankings when tested across scenario perturbations (increased difficulty, closer engagement, longer episodes) on defend_the_line.
**Evidence**: RPT-023, F-052, F-053, F-054, F-055, F-056
- doom_skill is dominant factor [STAT:f=F(2,348)=446.73] [STAT:p=7.77e-97] [STAT:eta2=0.720]
- Significant interaction [STAT:f=F(6,348)=4.06] [STAT:p=6.02e-04]
- L0_only consistently worst: CONFIRMED across all difficulty levels
- Strategy rankings change with difficulty: adaptive_kill drops from rank 1 (Easy) to rank 3 (Nightmare)
- burst_3 ranking unstable: rank 3 on Easy, rank 3 on Normal, rank 2 on Nightmare
- Effect compression: strategy spread shrinks 5.2× from Easy to Nightmare
**Trust**: MEDIUM-HIGH (residual violations mitigated by n=30/cell balanced design)
**Date Completed**: 2026-02-09

### H-012: defend_the_line Scenario Reveals Architectural Differences [ADOPTED - HIGH TRUST]
**Statement**: The defend_the_line scenario, with its higher kill ceiling (4-26 kills/episode vs 0-3) and more varied gameplay, will reveal statistically significant performance differences between action architecture levels that the simpler defend_the_center scenario (DOE-007) could not detect.
**Evidence**: RPT-008, F-010, F-011
- Overall ANOVA: [STAT:f=F(4,145)=5.256] [STAT:p=0.000555] [STAT:eta2=0.127]
- Kruskal-Wallis confirms: H(4)=20.158 [STAT:p=0.000465]
- All residual diagnostics PASS (normality, equal variance)
- L0_only significantly WORSE than all others (d=0.89-1.13, all p_adj < 0.01)
- Rank order REVERSAL from DOE-007: L0_only went from BEST to WORST
- Heuristic layers provide no advantage over random lateral movement
- Achieved power: [STAT:power=0.97]
**Trust**: HIGH (all diagnostics pass, p < 0.001, large effect size, three tests converge)
**Date Added**: 2026-02-08
**Date Adopted**: 2026-02-08
**Linked Experiment**: DOE-008
**Key Findings**: F-010 (L0_only deficit), F-011 (full_agent kills penalty)

### H-001: RAG System Outperforms Baselines [ADOPTED - MEDIUM TRUST]
**Statement**: Full RAG agent (L0+L1+L2) achieves significantly higher kill_rate than random and rule-only baselines in defend_the_center.
**Evidence**: RPT-001, F-001, F-002
- Full vs Random: [STAT:p_adj=0.000000] [STAT:effect_size=Cohen's d=5.28]
- Full vs Rule-Only: [STAT:p_adj=0.000000] [STAT:effect_size=Cohen's d=3.09]
- Non-parametric (Mann-Whitney U) confirms both at p<0.001
**Trust**: MEDIUM (normality violation in random condition expected and compensated by non-parametric test)
**Date Adopted**: 2026-02-08

### H-002: Rule Engine Provides Meaningful Structure [ADOPTED - MEDIUM TRUST]
**Statement**: Rule-only baseline significantly outperforms random baseline.
**Evidence**: RPT-001, F-003
- Rule-Only vs Random: [STAT:p_adj=0.000000] [STAT:effect_size=Cohen's d=3.11]
- Non-parametric (Mann-Whitney U) confirms at p<0.001
**Trust**: MEDIUM
**Date Adopted**: 2026-02-08

### H-003: Decision Latency Within Bounds [ADOPTED - MEDIUM TRUST]
**Statement**: Full cascade decision latency P99 < 100ms.
**Evidence**: RPT-001, F-004
- P99 latency: 45.1ms (target: <100ms, 55% headroom)
**Trust**: MEDIUM (single scenario, no stress testing)
**Date Adopted**: 2026-02-08

### H-006: Memory Weight Main Effect [ADOPTED - MEDIUM TRUST] [INVALIDATED by DOE-009]
**Statement**: Memory weight has a significant main effect on kill_rate.
**Evidence**: RPT-002, F-005
- [STAT:f=F(1,116)=82.411] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.4154]
- Memory explains 41.5% of kill_rate variance (dominant factor)
- Simple effects: +2.45 kills/min (at low Strength), +3.66 kills/min (at high Strength)
- All diagnostics PASS
**Trust**: MEDIUM (n=30 per cell < R100 HIGH threshold of n>=50)
**Date Adopted**: 2026-02-08
**[INVALIDATED by DOE-009]**: Real VizDoom data shows no significant effect (F(2,261)=0.306, p=0.736, η²=0.002). Mock data effect was fabricated. See F-013.

### H-007: Strength Weight Main Effect [ADOPTED - MEDIUM TRUST] [INVALIDATED by DOE-009]
**Statement**: Strength weight has a significant main effect on kill_rate.
**Evidence**: RPT-002, F-006
- [STAT:f=F(1,116)=53.685] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.3164]
- Strength explains 31.6% of kill_rate variance
- Simple effects: +1.75 kills/min (at low Memory), +2.95 kills/min (at high Memory)
- All diagnostics PASS
**Trust**: MEDIUM (n=30 per cell < R100 HIGH threshold of n>=50)
**Date Adopted**: 2026-02-08
**[INVALIDATED by DOE-009]**: Real VizDoom data shows no significant effect (F(2,261)=2.235, p=0.109, η²=0.017). Mock data effect was fabricated. See F-014.

### H-008: Memory-Strength Interaction [ADOPTED - MEDIUM TRUST] [INVALIDATED by DOE-009]
**Statement**: Memory weight and strength weight interact to affect kill_rate (non-additive effect).
**Evidence**: RPT-002, F-007
- [STAT:f=F(1,116)=4.470] [STAT:p=0.0366] [STAT:eta2=partial eta2=0.0371]
- Interaction is synergistic: Memory benefit amplified at high Strength
- High-High vs Low-Low: +5.40 kills/min [STAT:effect_size=Cohen's d=3.48]
- Curvature test NOT significant (p=0.9614): linear model adequate in [0.3, 0.7]
- All diagnostics PASS
**Trust**: MEDIUM (interaction effect small, confirmatory study recommended)
**Date Adopted**: 2026-02-08
**[INVALIDATED by DOE-009]**: Real VizDoom data shows no significant interaction (F(4,261)=0.365, p=0.834, η²=0.006). Mock data effect was fabricated. See F-015.

## Completed Hypotheses

### H-016: Compound Simultaneous Actions Outperform Sequential [REJECTED]
**Statement**: Compound simultaneous actions (attack+turn or attack+move on same tick) will outperform sequential actions on defend_the_line.
**Evidence**: RPT-012, F-025, F-026
- Compound strategies produce IDENTICAL results to each other (F-025, p=1.000)
- Compound strategies significantly WORSE than burst_3 (F-026, p<0.000001, eta2=0.262)
- VizDoom weapon cooldown absorbs timing differences
- Compound group: 36.58 kr vs burst_3: 44.54 kr (+18% deficit)
**Trust**: HIGH (all diagnostics pass, large effect sizes, mechanistic explanation clear)
**Date Rejected**: 2026-02-08
**Linked Experiment**: DOE-012

### H-017: Higher Attack Ratio → Higher Kill Rate [REJECTED]
**Statement**: Increasing attack ratio from 50% (burst strategies) to 100% (attack_only) will increase kill_rate.
**Evidence**: RPT-013, F-027
- kill_rate: F(4,145)=0.395, p=0.812 — NOT significant
- kills: F(4,145)=9.056, p<0.000001 — SIGNIFICANT (attack_only FEWER kills)
- survival_time: F(4,145)=6.621, p=0.000073 — SIGNIFICANT (attack_only SHORTER survival)
- attack_only produces 9.57 kills vs burst_3 13.7-14.5 kills (d=0.80-1.07)
**Trust**: HIGH (kill_rate null confirmed, kills/survival effects significant)
**Date Rejected**: 2026-02-08
**Linked Experiment**: DOE-013

### H-018: L0 Health Threshold Modulates Kill Rate [ADOPTED]
**Statement**: L0 health dodge threshold (0, 25, 50, 75, 100) modulates kill_rate on defend_the_line.
**Evidence**: RPT-014, F-028
- F(4,145)=3.860, p=0.005, eta2=0.096
- Monotonic trend: threshold_0 (46.3 kr) > threshold_50 (40.0 kr)
- C1 contrast (threshold_0 vs others): p=0.002, d=0.628
**Trust**: MEDIUM (monotonic trend clear, slight non-monotonicity at threshold_75)
**Date Adopted**: 2026-02-08
**Linked Experiment**: DOE-014

### H-019: Strategy Performance Generalizes Across Scenarios [REJECTED]
**Statement**: Strategy performance rankings on defend_the_line generalize to basic.cfg.
**Evidence**: RPT-015, F-029
- F(4,145)=174.832, p<0.000001, eta2=0.828 — HUGE effect
- basic.cfg: 1 monster, floor effect (83-93% zero kills)
- defend_the_line: 8+ monsters, kills [4,26]
- Rankings DO NOT REPLICATE across scenarios
**Trust**: HIGH (largest effect size in project, non-parametric confirms)
**Date Rejected**: 2026-02-08
**Linked Experiment**: DOE-015

### H-020: Simple Agents Function on Deadly_Corridor [REJECTED]
**Statement**: Simple agents (random, L0_only, burst_3, etc.) can achieve >0 kills on deadly_corridor.
**Evidence**: RPT-016, F-030
- F(4,145)=0.695, p=0.596 — NOT significant
- All strategies: mean kills ≈ 0.00-0.03 (floor effect)
- All strategies: survival ≈ 2-3 seconds
- 97-100% zero-kill episodes
**Trust**: HIGH (for null result — complete floor effect, no signal)
**Date Rejected**: 2026-02-08
**Linked Experiment**: DOE-016

### H-021: Replication of Attack_Only Deficit [ADOPTED]
**Statement**: attack_only produces fewer total kills than burst_3 with independent seed set (replication of F-027).
**Evidence**: RPT-017, F-031
- F(4,145)=4.726, p=0.001, eta2=0.115
- attack_only: 10.13 kills vs burst_3: 13.70 kills, p_adj=0.043, d=0.66
- Independent seed set (14001-15364) confirms finding
**Trust**: HIGH (replicates F-027 with different seeds)
**Date Adopted**: 2026-02-08
**Linked Experiment**: DOE-017

### H-022: Adaptive Strategies Outperform Fixed [PARTIALLY ADOPTED]
**Statement**: State-dependent adaptive strategies outperform fixed burst patterns.
**Evidence**: RPT-018, F-032, F-033
- adaptive_kill: 46.18 kr (highest kill_rate), matches burst_3 on kills (13.7 vs 14.5, NS)
- aggressive_adaptive: 40.65 kr (FAILS — too little movement)
- State-dependent logic viable if properly designed
**Trust**: MEDIUM (Levene violation, but non-parametric confirms)
**Date Adopted**: 2026-02-08
**Linked Experiment**: DOE-018

### H-023: Top Strategies Maintain Ranking in Cross-Validation [ADOPTED]
**Statement**: Top-performing strategies from DOE-008/010/018 maintain rankings in independent cross-validation.
**Evidence**: RPT-019, F-034, F-035
- L0_only worst performer across 3 experiments (38.52 kr, d=0.83-1.48)
- adaptive_kill, burst_3, random form top tier (43.4-46.6 kr, all NS pairwise)
- Replicated across 3 independent seed sets
**Trust**: HIGH (3x replication with independent seeds)
**Date Adopted**: 2026-02-08
**Linked Experiment**: DOE-019

### H-024: Best-of-Breed Confirmation [ADOPTED]
**Statement**: Best-of-breed comparison confirms optimal strategy for total kills and kill_rate.
**Evidence**: RPT-020, F-036, F-037, F-038
- burst_3: highest kills (15.40), beats attack_only/compound (d=0.95-1.00)
- compound_attack_turn ≈ attack_only (10.73 vs 10.70, d=0.01, NO advantage)
- Multi-objective selection needed (no single strategy dominates both metrics)
**Trust**: MEDIUM (consistent replication pattern across DOE-010/017/019/020)
**Date Adopted**: 2026-02-08
**Linked Experiment**: DOE-020

## Rejected Hypotheses

### H-027: L2 RAG Meta-Strategy Selection Outperforms Fixed Strategies [REJECTED]
**Statement**: L2 RAG meta-strategy selection, which queries OpenSearch to dynamically choose between L1 strategies based on game-state context, outperforms fixed single-strategy baselines across difficulty levels.
**Evidence**: DOE-024, RPT-024, F-057
**Reason**: decision_mode NOT significant for kills (p=0.3925, η²=0.009), survival (p=0.9314), or kill_rate main effect (p=0.4117). All planned contrasts ns. Cohen's d < 0.12 (negligible).
**Trust**: HIGH (n=360, non-parametric confirms)
**Date Rejected**: 2026-02-09

### H-025: L2 kNN Strategy Retrieval Provides Performance Improvement [REJECTED]
**Statement**: Adding L2 OpenSearch strategy document retrieval to the L0+L1 architecture will improve kill performance.
**Evidence**: DOE-022, EXPERIMENT_REPORT_022.md, F-049, F-050, F-051
**Result**: L2 RAG significantly DEGRADES performance (kills: 14.73→9.57, p<0.001, d=1.641). Document quality has zero effect (d=0.000). Tactic-to-action mapping too coarse.
**Trust**: HIGH
**Date Rejected**: 2026-02-09
**Linked Experiment**: DOE-022

### H-013: Memory and Strength Weights Have Significant Effects on defend_the_line [REJECTED]
**Statement**: memory_weight and strength_weight have significant main effects and/or interaction on kill_rate when tested with real VizDoom gameplay on defend_the_line scenario.
**Rationale**: H-006/H-007/H-008 were adopted from DOE-002 mock (synthetic) data. DOE-008 confirmed defend_the_line discriminates architectures (F-012). Now we test whether the continuous parameters (memory_weight, strength_weight) also show significant effects on this scenario.
**Evidence**: RPT-009, F-013, F-014, F-015
- memory_weight: [STAT:f=F(2,261)=0.306] [STAT:p=0.736] [STAT:eta2=0.002] — NOT significant
- strength_weight: [STAT:f=F(2,261)=2.235] [STAT:p=0.109] [STAT:eta2=0.017] — NOT significant
- interaction: [STAT:f=F(4,261)=0.365] [STAT:p=0.834] [STAT:eta2=0.006] — NOT significant
- All diagnostics PASS. Non-parametric confirms (Kruskal-Wallis p=0.500).
- DOE-002 mock findings (H-006, H-007, H-008) NOT replicated with real data.
**Trust**: HIGH (for null result — all diagnostics pass, n=270, non-parametric confirms)
**Date Added**: 2026-02-08
**Date Rejected**: 2026-02-08
**Linked Experiment**: DOE-009
**Key Design**: 3x3 full factorial, memory_weight [0.1, 0.5, 0.9] x strength_weight [0.1, 0.5, 0.9], 30 episodes/cell, 270 total.

### H-010: Memory and Strength Have Significant Effects in [0.3, 0.7] with Real KILLCOUNT [REJECTED]
**Statement**: Memory weight and strength weight have significant main effects on kill_rate in the [0.3, 0.7] range when measured with correct VizDoom KILLCOUNT.
**Evidence**: DOE-006 (pending formal RPT-006)
- DOE-006 confirmed ALL factors non-significant in [0.3, 0.7] with real KILLCOUNT data
- DOE-002's large effects (Memory eta2=0.42, Strength eta2=0.32) were entirely measurement artifacts of the AMMO2 bug
- Combined with DOE-005's null result at [0.7, 0.9]: Memory_weight and strength_weight have NO detectable effect on kill_rate at ANY tested range [0.3, 0.9]
**Trust**: MEDIUM (consistent null across two independent experiments with different seed sets)
**Date Rejected**: 2026-02-08
**Linked Experiment**: DOE-006

### H-004: Memory Weight Optimization [CLOSED — Superseded]
**Statement**: Optimal memory_weight exists between 0.3-0.9 for maximizing kill_rate in the full RAG agent.
**Evidence**: DOE-005 (RPT-005, F-008), DOE-006
- DOE-005: No effect at [0.7, 0.9], all p > 0.10
- DOE-006: No effect at [0.3, 0.7], all p > 0.10
- No evidence of optimal memory_weight at any tested value
**Status**: CLOSED. Superseded by DOE-005 and DOE-006 null results. The entire Memory-Strength optimization thread is closed.
**Date Added**: 2026-02-07
**Date Closed**: 2026-02-08

### H-009: Memory-Strength Trend Continues Beyond 0.7 [REJECTED]
**Statement**: Increasing memory_weight and strength_weight beyond 0.7 (toward 0.9) continues to improve kill_rate without diminishing returns.
**Evidence**: RPT-005, F-008
- Memory: [STAT:f=F(1,116)=0.814] [STAT:p=0.3689] [STAT:eta2=partial eta2=0.0070] -- negligible
- Strength: [STAT:f=F(1,116)=2.593] [STAT:p=0.1101] [STAT:eta2=partial eta2=0.0219] -- small, non-significant
- No curvature: [STAT:p=0.6242]
- Performance plateau at ~8.4 kills/min across all conditions in [0.7, 0.9]
**Trust**: MEDIUM (non-parametric verification confirms, normality violation mitigated)
**Date Rejected**: 2026-02-08
