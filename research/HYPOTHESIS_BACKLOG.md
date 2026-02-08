# Hypothesis Backlog

## Active Hypotheses

### H-004: Memory Weight Optimization [MEDIUM PRIORITY]
**Statement**: Optimal memory_weight exists between 0.3-0.9 for maximizing kill_rate in the full RAG agent.
**Rationale**: DOE-002 reported large Memory effect (eta_p^2=0.4154, BUT with INVALID AMMO2 data). DOE-005 confirmed performance plateau at [0.7, 0.9] with real kills data. The [0.3, 0.7] range has NOT been tested with real KILLCOUNT data -- DOE-006 will address this.
**Status**: Partially addressed. DOE-005 rejected H-009 (no effect at [0.7, 0.9]). DOE-006 will test [0.3, 0.7] with real data.
**Date Added**: 2026-02-07
**Date Updated**: 2026-02-08

### H-005: Strategy Document Quality Matters [MEDIUM PRIORITY]
**Statement**: Higher quality strategy documents (higher confidence_tier) lead to better agent performance.
**Rationale**: Validates the RAG curation pipeline importance. If document quality does not matter, the refinement pipeline is unnecessary overhead.
**Status**: Queued (Phase 1, planned as DOE-003 layer ablation or DOE-004 doc quality)
**Date Added**: 2026-02-07

### H-010: Memory and Strength Have Significant Effects in the [0.3, 0.7] Range with Real KILLCOUNT Data [HIGH PRIORITY]
**Statement**: Memory weight and strength weight have significant main effects on kill_rate in the [0.3, 0.7] range when measured with correct VizDoom KILLCOUNT (real kills, not AMMO2 bug).
**Rationale**: DOE-002 reported large effects (Memory eta2=0.42, Strength eta2=0.32) but used INVALID data (AMMO2 mapped as kills). DOE-005 found no effects at [0.7, 0.9] with REAL data. The [0.3, 0.7] range may reveal effects masked by the performance plateau if wider separation between factor levels produces genuinely different agent behaviors. This is a critical re-validation experiment.
**Status**: Experiment ordered (DOE-006)
**Date Added**: 2026-02-08
**Linked Experiment**: DOE-006

## Queued Hypotheses

## Completed Hypotheses

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

### H-006: Memory Weight Main Effect [ADOPTED - MEDIUM TRUST]
**Statement**: Memory weight has a significant main effect on kill_rate.
**Evidence**: RPT-002, F-005
- [STAT:f=F(1,116)=82.411] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.4154]
- Memory explains 41.5% of kill_rate variance (dominant factor)
- Simple effects: +2.45 kills/min (at low Strength), +3.66 kills/min (at high Strength)
- All diagnostics PASS
**Trust**: MEDIUM (n=30 per cell < R100 HIGH threshold of n>=50)
**Date Adopted**: 2026-02-08

### H-007: Strength Weight Main Effect [ADOPTED - MEDIUM TRUST]
**Statement**: Strength weight has a significant main effect on kill_rate.
**Evidence**: RPT-002, F-006
- [STAT:f=F(1,116)=53.685] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.3164]
- Strength explains 31.6% of kill_rate variance
- Simple effects: +1.75 kills/min (at low Memory), +2.95 kills/min (at high Memory)
- All diagnostics PASS
**Trust**: MEDIUM (n=30 per cell < R100 HIGH threshold of n>=50)
**Date Adopted**: 2026-02-08

### H-008: Memory-Strength Interaction [ADOPTED - MEDIUM TRUST]
**Statement**: Memory weight and strength weight interact to affect kill_rate (non-additive effect).
**Evidence**: RPT-002, F-007
- [STAT:f=F(1,116)=4.470] [STAT:p=0.0366] [STAT:eta2=partial eta2=0.0371]
- Interaction is synergistic: Memory benefit amplified at high Strength
- High-High vs Low-Low: +5.40 kills/min [STAT:effect_size=Cohen's d=3.48]
- Curvature test NOT significant (p=0.9614): linear model adequate in [0.3, 0.7]
- All diagnostics PASS
**Trust**: MEDIUM (interaction effect small, confirmatory study recommended)
**Date Adopted**: 2026-02-08

## Rejected Hypotheses

### H-009: Memory-Strength Trend Continues Beyond 0.7 [REJECTED]
**Statement**: Increasing memory_weight and strength_weight beyond 0.7 (toward 0.9) continues to improve kill_rate without diminishing returns.
**Evidence**: RPT-005, F-008
- Memory: [STAT:f=F(1,116)=0.814] [STAT:p=0.3689] [STAT:eta2=partial eta2=0.0070] -- negligible
- Strength: [STAT:f=F(1,116)=2.593] [STAT:p=0.1101] [STAT:eta2=partial eta2=0.0219] -- small, non-significant
- No curvature: [STAT:p=0.6242]
- Performance plateau at ~8.4 kills/min across all conditions in [0.7, 0.9]
**Trust**: MEDIUM (non-parametric verification confirms, normality violation mitigated)
**Date Rejected**: 2026-02-08
