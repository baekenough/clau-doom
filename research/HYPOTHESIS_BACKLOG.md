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
**Status**: Queued (Phase 1, planned as DOE-003 layer ablation or DOE-004 doc quality)
**Date Added**: 2026-02-07

## Queued Hypotheses

## Completed Hypotheses

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

## Rejected Hypotheses

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
