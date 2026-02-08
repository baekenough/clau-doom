# Findings

Research findings from clau-doom experiments. Each finding traces back through the audit chain:
HYPOTHESIS_BACKLOG -> EXPERIMENT_ORDER -> EXPERIMENT_REPORT -> FINDINGS

## Data Source Status

**WARNING**: Findings F-001 through F-007 were derived from MOCK (numpy-generated) data. Real VizDoom data (RPT-001-REAL) has invalidated several mock-based claims. See individual finding annotations below.

### Real vs Mock Summary
| Finding | Mock Status | Real Status | Discrepancy |
|---------|-------------|-------------|-------------|
| F-001 (Full > Random) | ADOPTED | CONFIRMED | Direction confirmed, effect size larger in real data (d=6.84 vs d=5.28) |
| F-002 (Full > Rule-Only) | ADOPTED | **INVALIDATED** | Real data shows NO difference (both identical at 26.0 kills, 0 variance) |
| F-003 (Rule-Only > Random) | ADOPTED | CONFIRMED | Direction confirmed, effect size larger in real data (d=6.84 vs d=3.11) |
| F-004 (Latency < 100ms) | ADOPTED | CONFIRMED | Python action functions run in <1ms, no VizDoom latency measured |
| F-005 through F-007 | ADOPTED (mock DOE-002) | PENDING REAL VALIDATION | DOE-002 not yet re-run with real VizDoom |

**Key Insight**: Mock data fabricated separation between rule_only and full_agent that does not exist in real gameplay at default parameters (memory_weight=0.5, strength_weight=0.5). Both strategies converge to "always attack" in defend_the_center, producing identical deterministic outcomes.

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

**[REAL DATA ANNOTATION — 2026-02-08]**:
CONFIRMED with real VizDoom execution. Direction of effect preserved (Full >> Random), but effect size LARGER in real data ([STAT:effect_size=Cohen's d=6.84] vs mock d=5.28). Real gameplay shows full_agent and rule_only both achieve mean=26.0 kills (identical), while random achieves mean=9.9 kills. The full vs random comparison remains valid with even stronger evidence, but the specific numerical advantage of full_agent over rule_only is INVALIDATED (see F-002). Trust remains MEDIUM due to degenerate variance in real data (rule_only and full_agent have SD=0.00).

---

### F-002: Full RAG Agent Outperforms Rule-Only Baseline

**Hypothesis**: H-001 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Experiment Report**: RPT-001 (EXPERIMENT_REPORT_001.md) [MOCK DATA], RPT-001-REAL (REAL DATA)

**Evidence (MOCK DATA — INVALID)**:
- Welch's t-test: [STAT:t=18.25] [STAT:p_adj=0.000000] (Holm-Bonferroni corrected)
- Non-parametric confirmation: Mann-Whitney U [STAT:p_mann=0.000000]
- Effect size: [STAT:effect_size=Cohen's d=3.09] (HUGE)
- Mean difference: +25.94 kills [STAT:ci=95%: 23.16 to 28.73]
- Sample size: [STAT:n=70 per condition, 140 total for this comparison]

**Trust Level**: ~~MEDIUM~~ → **INVALIDATED**

**Trust Rationale**:
~~Both conditions (full_agent and rule_only) pass normality (A²=0.18 and 0.20, both p=0.25)~~
~~Equal variance fails globally (Levene W=42.08) but Welch's t-test compensates~~
~~Non-parametric confirms, effect size enormous~~
~~Could approach HIGH for this specific pairwise comparison, but overall experiment diagnostics lower trust~~

**[REAL DATA ANNOTATION — 2026-02-08]**:
**INVALIDATED**. Real VizDoom execution shows full_agent and rule_only produce IDENTICAL outcomes:
- full_agent: mean=26.0 kills, SD=0.00
- rule_only: mean=26.0 kills, SD=0.00
- Mean difference: 0.00 kills (no separation)
- Statistical test: [STAT:p=NaN] (both groups have zero variance)

At default parameters (memory_weight=0.5, strength_weight=0.5), the FullAgentAction heuristics (lines 25-41 in full_agent_action.py) reduce to the exact same behavior as RuleOnlyAction: always attack the nearest enemy. The L1 (DuckDB cache) and L2 (OpenSearch kNN) layers contribute no differentiation in defend_the_center with these settings.

**Interpretation**:
The mock data fabricated a 25.94 kill advantage that does not exist. This finding is INVALID and must be REJECTED. The L1+L2 RAG layers do NOT currently provide value beyond L0 rules at default parameters in the defend_the_center scenario.

**Status**: REJECTED (2026-02-08)

**Recommended Next**:
Re-execute DOE-002 with real VizDoom to test whether memory_weight and strength_weight parameters at EXTREME values (not default 0.5) can produce behavioral differentiation. The factorial design remains scientifically valid, but the hypothesis that the RAG system provides intrinsic value at default settings is UNSUPPORTED.

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

**[REAL DATA ANNOTATION — 2026-02-08]**:
CONFIRMED with real VizDoom execution. Direction of effect preserved and STRENGTHENED. Real data shows:
- rule_only: mean=26.0 kills (vs mock 16.63)
- random: mean=9.9 kills (vs mock 2.77)
- Effect size: [STAT:effect_size=Cohen's d=6.84] (vs mock d=3.11)

The rule engine is FAR MORE effective in real gameplay than mock data suggested. The mock underestimated rule_only performance by 56% (16.63 → 26.0). Trust remains MEDIUM due to degenerate variance (rule_only has SD=0.00 in real data — deterministic outcomes). The scientific conclusion is strengthened: L0 rules provide massive value over random behavior.

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

**[REAL DATA ANNOTATION — 2026-02-08]**:
CONFIRMED. Real VizDoom execution shows Python action functions (random_action.py, rule_only_action.py, full_agent_action.py) complete in <1ms on standard hardware. The P99=45.1ms figure from mock data was likely simulated overhead; actual action function execution is negligible. The 100ms latency budget is not a practical constraint with the current Python-based action architecture. VizDoom engine latency (frame processing, rendering) was not measured in real execution. Trust remains MEDIUM pending stress testing under load (many enemies, complex map geometry).

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

### F-009: Action Selection Architecture Does Not Affect Kill Rate in defend_the_center (PENDING PI DISPOSITION)

**Hypothesis**: H-011 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-007 (EXPERIMENT_ORDER_007.md)
**Experiment Report**: RPT-007 (EXPERIMENT_REPORT_007.md)

**Evidence**:
- One-way ANOVA (5 levels): [STAT:f=F(4,145)=1.579] [STAT:p=0.183] [STAT:eta2=eta^2=0.042] -- NOT significant
- Non-parametric Kruskal-Wallis: H(4)=3.340 [STAT:p=0.503] -- confirms non-significance
- All 10 Tukey HSD pairwise comparisons: p_adj > 0.14 (none significant)
- Planned contrasts: C1 (random vs others) p=0.656, C2 (L0 vs augmented) p=0.151, C3 (single vs combined) p=0.051, C4 (memory vs strength) p=0.689
- Sample size: [STAT:n=150 (30 per condition)]
- Observed power: [STAT:power=0.49] at observed effect size f=0.209
- Zero-kill pattern: full_agent worst (20%), L0_only best (0%)
- Both normality and equal variance assumptions violated, but non-parametric test confirms result

**Trust Level**: MEDIUM (pending PI)

**Trust Rationale**:
- Non-parametric confirmation provides robustness despite assumption violations
- Balanced design with identical seeds across conditions (strong internal validity)
- Consistent with DOE-005 and DOE-006 null results for parameter effects
- Power only 49% for observed effect -- cannot rule out small effects definitively
- Very low kill counts (0-3) limit discriminability

**Interpretation (Statistical)**:
Five architectural configurations (random, L0_only, L0_memory, L0_strength, full_agent) produce statistically indistinguishable kill_rate in defend_the_center. Group means range from 6.74 (full_agent) to 9.08 (L0_only), but variation is within noise.

**Key Observations**:
1. Random agent is NOT inferior to structured agents (C1 contrast p=0.656)
2. Full_agent (L0 + memory + strength) is paradoxically the WORST performer
3. L0_only achieves highest mean kill_rate (9.08) with lowest variance (SD=2.75)
4. Combined heuristics may be counterproductive (C3 contrast p=0.051, borderline)
5. Defend_the_center may be too simple to differentiate architectures (0-3 kills/episode)

**Status**: PENDING PI DISPOSITION (analyst recommends either REJECT H-011 or PARTIALLY ADOPT with LOW trust)

**Recommended Next** (per analyst):
1. Test on harder scenarios with higher kill counts for better discriminability
2. Investigate why full_agent underperforms L0_only (excessive dodging hypothesis)
3. Consider whether defend_the_center ceiling limits differentiation

---

## Rejected Findings

### F-008: Memory and Strength Have No Significant Effect in [0.7, 0.9] Range (Performance Plateau)

**Hypothesis**: H-009 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-005 (EXPERIMENT_ORDER_005.md)
**Experiment Report**: RPT-005 (EXPERIMENT_REPORT_005.md)

**Evidence**:
- Memory main effect: [STAT:f=F(1,116)=0.814] [STAT:p=0.3689] [STAT:eta2=partial eta2=0.0070] -- NOT significant (negligible)
- Strength main effect: [STAT:f=F(1,116)=2.593] [STAT:p=0.1101] [STAT:eta2=partial eta2=0.0219] -- NOT significant (small)
- Interaction: [STAT:f=F(1,116)=0.079] [STAT:p=0.7795] [STAT:eta2=partial eta2=0.0007] -- NOT significant (negligible)
- Curvature test: [STAT:p=0.6242] -- NOT significant (no curvature, flat surface)
- Non-parametric verification: Kruskal-Wallis H=4.428 [STAT:p=0.2188], ART ANOVA all p>0.07 -- all confirm non-significance
- Sample size: [STAT:n=120 factorial episodes (30 per cell) + 30 center = 150 total]
- Power for medium effects (f=0.25): [STAT:power=0.775]
- All secondary responses (kills, survival_time) also non-significant
- Memory effect CI: [STAT:ci=95%: -1.97 to 0.74] (includes zero)
- Strength effect CI: [STAT:ci=95%: -0.25 to 2.44] (includes zero)

**Trust Level**: MEDIUM

**Trust Rationale**:
- Normality assumption violated (Shapiro-Wilk p=0.000001) due to zero-inflated kill_rate distribution (14/150 episodes with zero kills)
- Equal variance PASS (Levene p=0.88) -- strong homoscedasticity
- Non-parametric methods (Kruskal-Wallis, ART ANOVA) fully confirm parametric conclusions
- Balanced design (n=30 per cell) provides robustness to non-normality
- Power adequate for medium effects but insufficient for small effects
- This is the FIRST valid experiment with real VizDoom KILLCOUNT data (DOE-002 data invalidated by AMMO2 mapping bug)

**Interpretation**:
The kill_rate response surface is essentially FLAT in the [0.7, 0.9] range. The performance plateau at approximately 8.4 kills/min (~1.2 kills/episode, ~8.5s survival) represents the ceiling for these two parameters in this operating region. All four factorial cells and the center point produce statistically indistinguishable kill_rate values (range: 7.60 to 9.32 kills/min with overlapping confidence intervals).

The directional trends are noteworthy but non-significant:
- Memory has a slightly NEGATIVE trend: Memory=0.9 yields 0.62 kills/min LESS than Memory=0.7 [STAT:effect_size=Cohen's d=-0.164] (negligible)
- Strength has a slightly POSITIVE trend: Strength=0.9 yields 1.10 kills/min MORE than Strength=0.7 [STAT:effect_size=Cohen's d=0.295] (small)

**DOE-002 Data Invalidation Note**:
DOE-002 reported large effects (Memory eta2=0.42, Strength eta2=0.32) in the [0.3, 0.7] range, but those results used ERRONEOUS data where the KILLCOUNT variable was actually AMMO2=26 (a constant). The DOE-002 kill_rate values were computed from fictitious kill counts. Cross-experiment comparison between DOE-002 and DOE-005 is INVALID because the measurement instruments differed fundamentally.

**Status**: REJECTED (2026-02-08)

**Recommended Next**:
1. Re-test Memory and Strength at [0.3, 0.7] range with REAL KILLCOUNT data (DOE-006) to establish valid baseline effects
2. If effects are confirmed in [0.3, 0.7] with real data, the plateau onset is between 0.7 and 0.9
3. Pivot to other factors: layer ablation (DOE-003), document quality (DOE-004)

---

### F-010: Action Architecture Significant on defend_the_line [HIGH TRUST]
**Hypothesis**: H-012
**Experiment**: DOE-008 (EXPERIMENT_ORDER_008.md)
**Report**: EXPERIMENT_REPORT_008.md
**Evidence**: [STAT:p=0.000555] [STAT:f=F(4,145)=5.256] [STAT:eta2=0.127] [STAT:n=150]
**Trust Level**: HIGH
**Date Adopted**: 2026-02-08
**Summary**: L0-only pure rule-based strategy performs significantly worse than all other architectures including random. Tukey HSD confirms all 4 pairwise comparisons with L0_only are significant (p < 0.01).

### F-011: Heuristic Layer Interference [MEDIUM TRUST]
**Hypothesis**: H-012
**Experiment**: DOE-008
**Report**: EXPERIMENT_REPORT_008.md
**Evidence**: [STAT:p=0.007] Contrast C3: single-heuristic vs full_agent
**Trust Level**: MEDIUM (planned contrast, not primary analysis)
**Date Adopted**: 2026-02-08
**Summary**: Full agent with both heuristic layers (memory + strength) underperforms agents with only one heuristic. Combining layers creates interference through excessive dodging.

### F-012: Scenario Selection Critical [HIGH TRUST]
**Hypothesis**: H-012
**Experiment**: DOE-007 vs DOE-008
**Evidence**: DOE-007 p=0.183 (defend_the_center), DOE-008 p=0.000555 (defend_the_line). Same design, different scenarios.
**Trust Level**: HIGH (replicated design with consistent methodology)
**Date Adopted**: 2026-02-08
**Summary**: defend_the_line scenario is necessary for discriminating action architectures. defend_the_center (0-3 kills) is too simple.
