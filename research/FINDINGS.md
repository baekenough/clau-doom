# Findings

Research findings from clau-doom experiments. Each finding traces back through the audit chain:
HYPOTHESIS_BACKLOG -> EXPERIMENT_ORDER -> EXPERIMENT_REPORT -> FINDINGS

## Adopted Findings

### F-001: Full RAG Agent Dramatically Outperforms Random Baseline

**Hypothesis**: H-001 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Experiment Report**: RPT-001 (EXPERIMENT_REPORT_001.md)

**Evidence**:
- Welch's t-test: [STAT:t=31.26] [STAT:p_adj=0.000000] (Holm-Bonferroni corrected)
- Non-parametric confirmation: Mann-Whitney U [STAT:p_mann=0.000000]
- Effect size: [STAT:effect_size=Cohen's d=5.28] (HUGE, >3x "large" threshold)
- Mean difference: +39.80 kills [STAT:ci=95%: 37.30 to 42.30]
- Sample size: [STAT:n=70 per condition, 140 total for this comparison]

**Trust Level**: MEDIUM

**Trust Rationale**:
- Elevated from LOW despite normality failure (random condition A²=1.94, p=0.001) because:
  1. Non-parametric Mann-Whitney U confirms at p<0.001
  2. Normality failure is structurally expected (random kills bounded at 0, right-skewed)
  3. Welch's t-test is robust to unequal variance by design
  4. Effect size (d=5.28) far exceeds any practical threshold
  5. n=70 >> 30 minimum per R100
- Not HIGH because residual diagnostics did not all pass (R100 requires all-pass for HIGH)

**Interpretation**:
The full RAG cascade (L0 rules + L1 DuckDB cache + L2 OpenSearch kNN) achieves approximately 15x the kills of a random agent (42.57 vs 2.77). This validates the fundamental premise of the project: structured decision-making with RAG-augmented knowledge retrieval provides massive performance gains in the DOOM defend_the_center scenario.

**Adopted**: 2026-02-08 (Phase 0)

**Recommended Next**:
Phase 1 factorial design (DOE-002) to optimize individual RAG parameters (memory_weight, strength_weight).

---

### F-002: Full RAG Agent Outperforms Rule-Only Baseline

**Hypothesis**: H-001 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Experiment Report**: RPT-001 (EXPERIMENT_REPORT_001.md)

**Evidence**:
- Welch's t-test: [STAT:t=18.25] [STAT:p_adj=0.000000] (Holm-Bonferroni corrected)
- Non-parametric confirmation: Mann-Whitney U [STAT:p_mann=0.000000]
- Effect size: [STAT:effect_size=Cohen's d=3.09] (HUGE)
- Mean difference: +25.94 kills [STAT:ci=95%: 23.16 to 28.73]
- Sample size: [STAT:n=70 per condition, 140 total for this comparison]

**Trust Level**: MEDIUM

**Trust Rationale**:
- Both conditions (full_agent and rule_only) pass normality (A²=0.18 and 0.20, both p=0.25)
- Equal variance fails globally (Levene W=42.08) but Welch's t-test compensates
- Non-parametric confirms, effect size enormous
- Could approach HIGH for this specific pairwise comparison, but overall experiment diagnostics lower trust

**Interpretation**:
The L1+L2 layers (DuckDB cache + OpenSearch kNN) add substantial value beyond L0 rules alone. The full agent achieves 2.56x the kills of rule-only (42.57 vs 16.63). This confirms that RAG knowledge retrieval is not just overhead -- it provides actionable intelligence that significantly improves decision quality.

**Adopted**: 2026-02-08 (Phase 0)

**Recommended Next**:
DOE-003 (layer ablation, H-005) to test individual L1 and L2 contributions via 2^3 factorial.

---

### F-003: Rule Engine Provides Meaningful Structure

**Hypothesis**: H-002 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Experiment Report**: RPT-001 (EXPERIMENT_REPORT_001.md)

**Evidence**:
- Welch's t-test: [STAT:t=18.42] [STAT:p_adj=0.000000] (Holm-Bonferroni corrected)
- Non-parametric confirmation: Mann-Whitney U [STAT:p_mann=0.000000]
- Effect size: [STAT:effect_size=Cohen's d=3.11] (HUGE)
- Mean difference: +13.86 kills [STAT:ci=95%: 12.38 to 15.33]
- Sample size: [STAT:n=70 per condition, 140 total for this comparison]

**Trust Level**: MEDIUM

**Trust Rationale**:
- Same as F-001: normality violation in random condition expected, non-parametric confirms
- Effect size (d=3.11) leaves no ambiguity about practical significance

**Interpretation**:
L0 hardcoded rules alone achieve 6x the kills of random (16.63 vs 2.77). This validates that the rule-based decision layer provides a strong foundation. The L0 rules encode basic combat behaviors (target nearest enemy, fire when aligned, strafe to avoid projectiles) that are individually simple but collectively powerful.

**Adopted**: 2026-02-08 (Phase 0)

**Recommended Next**:
This finding supports the hierarchical cascade design. Future experiments should preserve L0 as the base layer and focus on optimizing L1/L2 parameters.

---

### F-004: Decision Latency Within Real-Time Bounds

**Hypothesis**: H-003 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Experiment Report**: RPT-001 (EXPERIMENT_REPORT_001.md)

**Evidence**:
- Full agent decision latency P99: 45.1ms
- Target threshold: < 100ms (R100 constraint)
- Margin: 54.9ms (55% headroom)

**Trust Level**: MEDIUM

**Trust Rationale**:
- Single scenario measurement (defend_the_center only)
- No stress testing (e.g., many simultaneous enemies, complex map geometry)
- Sufficient for Phase 0 validation, but needs confirmation under load

**Interpretation**:
The full cascade (L0->L1->L2) operates well within the 100ms P99 latency budget. The 45.1ms P99 provides 55% headroom for additional decision complexity. This confirms the architecture's feasibility for real-time gameplay without LLM calls in the loop.

**Adopted**: 2026-02-08 (Phase 0)

**Recommended Next**:
Monitor latency as agent complexity grows. Stress test in Phase 2+ with more complex scenarios.

---

### F-005: Memory Weight Has Large Main Effect on Kill Rate

**Hypothesis**: H-006 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-002 (EXPERIMENT_ORDER_002.md)
**Experiment Report**: RPT-002 (EXPERIMENT_REPORT_002.md)

**Evidence**:
- Two-way ANOVA: [STAT:f=F(1,116)=82.411] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.4154] (large effect)
- Simple effect at low Strength: +2.45 kills/min [STAT:ci=95%: 1.65-3.25] [STAT:effect_size=Cohen's d=1.55]
- Simple effect at high Strength: +3.66 kills/min [STAT:ci=95%: 2.88-4.44] [STAT:effect_size=Cohen's d=2.38]
- Sample size: [STAT:n=30 per cell, 120 factorial episodes total]
- Diagnostics: Normality PASS (A²=0.70, p=0.071), Equal variance PASS (Levene W=0.01, p=0.998), No outliers

**Trust Level**: MEDIUM

**Trust Rationale**:
- All diagnostics PASS (first experiment with fully clean residuals)
- p < 0.0001 for main effect, eta_p^2 = 0.4154 (Memory explains 41.5% of variance)
- Not HIGH because n=30 per cell < R100 HIGH threshold of n>=50 per condition
- Confirmatory study (DOE-005) at larger n would achieve HIGH

**Interpretation**:
Memory weight is the single most important parameter in the agent's decision system. Increasing memory_weight from 0.3 to 0.7 increases kill_rate by 2.45-3.66 kills/min depending on Strength level. This is scientifically coherent: higher memory weight means the agent relies more heavily on DuckDB-cached experience from past episodes, making better-informed decisions. The effect is robust across both Strength levels, confirming it is not an artifact of a single configuration.

The partial eta-squared of 0.4154 is remarkably large -- Memory alone accounts for more variance in kill_rate than all other sources combined (Strength + Interaction + Error). This positions experience retention as the primary lever for agent improvement.

**Adopted**: 2026-02-08 (Phase 0/1)

**Recommended Next**:
Test whether the linear trend continues beyond 0.7 with expanded range (DOE-005 at Memory [0.7, 0.9]). If performance plateaus or declines, the optimal is near 0.7. If it continues to rise, push further.

---

### F-006: Strength Weight Has Large Main Effect on Kill Rate

**Hypothesis**: H-007 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-002 (EXPERIMENT_ORDER_002.md)
**Experiment Report**: RPT-002 (EXPERIMENT_REPORT_002.md)

**Evidence**:
- Two-way ANOVA: [STAT:f=F(1,116)=53.685] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.3164] (large effect)
- Simple effect at low Memory: +1.75 kills/min [STAT:ci=95%: 0.95-2.54] [STAT:effect_size=Cohen's d=1.12]
- Simple effect at high Memory: +2.95 kills/min [STAT:ci=95%: 2.17-3.74] [STAT:effect_size=Cohen's d=1.90]
- Sample size: [STAT:n=30 per cell, 120 factorial episodes total]
- Diagnostics: All PASS

**Trust Level**: MEDIUM

**Trust Rationale**:
- All diagnostics PASS
- p < 0.0001, eta_p^2 = 0.3164 (Strength explains 31.6% of variance)
- Not HIGH because n=30 per cell < R100 HIGH threshold

**Interpretation**:
Strength weight is the second most important parameter, accounting for 31.6% of kill_rate variance. Higher strength_weight causes the Rust scoring function to prioritize offensive/aggressive actions, leading to more kills. The effect is consistent across both Memory levels.

The ordering Memory > Strength in effect size (0.4154 vs 0.3164) suggests that **knowing what to do** (experience) matters more than **how aggressively to act** (strength), though both are critical. An uninformed aggressive agent (low Memory, high Strength) performs worse than an informed cautious agent (high Memory, low Strength): 5.99 vs 6.70 kills/min.

**Adopted**: 2026-02-08 (Phase 0/1)

**Recommended Next**:
Expand Strength range in DOE-005 alongside Memory to test continued improvement at higher values.

---

### F-007: Memory and Strength Interact Synergistically

**Hypothesis**: H-008 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-002 (EXPERIMENT_ORDER_002.md)
**Experiment Report**: RPT-002 (EXPERIMENT_REPORT_002.md)

**Evidence**:
- Two-way ANOVA interaction: [STAT:f=F(1,116)=4.470] [STAT:p=0.0366] [STAT:eta2=partial eta2=0.0371] (small but significant)
- Interaction pattern: Memory benefit amplified at high Strength
  - Memory effect at Strength=0.3: +2.45 kills/min [STAT:effect_size=Cohen's d=1.55]
  - Memory effect at Strength=0.7: +3.66 kills/min [STAT:effect_size=Cohen's d=2.38]
  - Difference in simple effects: 1.21 kills/min (the interaction magnitude)
- Synergy confirmed by high-high vs low-low comparison:
  - High-High (0.7, 0.7) vs Low-Low (0.3, 0.3): +5.40 kills/min [STAT:ci=95%: 4.62-6.19] [STAT:effect_size=Cohen's d=3.48]
- Curvature test: NOT significant (p=0.9614, linear model adequate)
- Sample size: [STAT:n=30 per cell, 120 factorial episodes total]
- Diagnostics: All PASS

**Trust Level**: MEDIUM

**Trust Rationale**:
- Interaction is statistically significant (p=0.0366 < 0.05)
- Effect size is small (eta_p^2 = 0.0371) -- the interaction modulates but does not dominate
- Main effects are far larger (0.4154 and 0.3164), so interaction is a secondary refinement
- n=30 provides adequate power for the observed large main effects but marginal power for detecting small interactions; confirmatory study recommended

**Interpretation**:
The interaction is synergistic: experience (Memory) is more valuable when the agent acts aggressively (high Strength). This makes intuitive sense -- an agent that remembers successful strategies AND aggressively executes them outperforms the sum of either factor alone. Conversely, low Memory + low Strength is the worst combination (4.24 kills/min), while high Memory + high Strength is the best (9.65 kills/min).

The practical implication is that **Memory and Strength should be optimized jointly, not independently.** Simply maximizing one while ignoring the other leaves performance on the table. The interaction term, while small in effect size, is statistically confirmed and directionally consistent.

However, the curvature test shows no quadratic effects in the [0.3, 0.7] range. The response surface is a tilted plane -- performance increases linearly toward the high-high corner. This means:
1. The optimal point in this region is (Memory=0.7, Strength=0.7)
2. RSM would add no value in this region (no curvature to model)
3. The question is whether the trend continues beyond 0.7

**Adopted**: 2026-02-08 (Phase 0/1)

**Recommended Next**:
Design DOE-005 as a confirmatory factorial at expanded range [0.7, 0.9] to test whether the linear trend continues. Include center points at (0.8, 0.8). If curvature appears at the expanded range, then proceed to RSM. If the trend continues linearly, the optimal lies at or beyond the boundary.

---

## Tentative Findings

(None currently)

## Rejected Findings

(None currently)
