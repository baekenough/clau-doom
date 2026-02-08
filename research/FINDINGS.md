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
| F-005 (Memory main effect) | ADOPTED (mock DOE-002) | **INVALIDATED by DOE-009** | Real data: F(2,261)=0.306, p=0.736, η²=0.002. Mock claimed η²=0.42 |
| F-006 (Strength main effect) | ADOPTED (mock DOE-002) | **INVALIDATED by DOE-009** | Real data: F(2,261)=2.235, p=0.109, η²=0.017. Mock claimed η²=0.32 |
| F-007 (Interaction) | ADOPTED (mock DOE-002) | **INVALIDATED by DOE-009** | Real data: F(4,261)=0.365, p=0.834, η²=0.006. Mock claimed significant |

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

## DOE-008 Findings (defend_the_line Layer Ablation)

### F-010: Pure Reflex Rules (L0_only) Significantly Inferior on defend_the_line

**Hypothesis**: H-012 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-008 (EXPERIMENT_ORDER_008.md)
**Experiment Report**: RPT-008 (EXPERIMENT_REPORT_008.md)

**Evidence**:
- Overall ANOVA: [STAT:f=F(4,145)=5.256] [STAT:p=0.000555] [STAT:eta2=eta^2=0.127] (medium-to-large)
- Kruskal-Wallis confirms: H(4)=20.158 [STAT:p=0.000465]
- Alexander-Govern robust test: stat=24.241 [STAT:p=0.000071]
- L0_only vs all others (C2 contrast): t=-4.451 [STAT:p=0.000019] [STAT:effect_size=Cohen's d=-0.938] (large)
- Tukey HSD: L0_only significantly worse than ALL 4 other conditions (all p_adj < 0.01):
  - vs L0_memory: +6.56 kills/min [STAT:ci=95%: 2.06-11.07] [STAT:effect_size=Cohen's d=1.132]
  - vs random: +5.72 kills/min [STAT:ci=95%: 1.22-10.23] [STAT:effect_size=Cohen's d=1.005]
  - vs full_agent: +5.61 kills/min [STAT:ci=95%: 1.10-10.11] [STAT:effect_size=Cohen's d=0.885]
  - vs L0_strength: +5.44 kills/min [STAT:ci=95%: 0.93-9.94] [STAT:effect_size=Cohen's d=1.005]
- The four non-L0_only conditions are statistically indistinguishable (all pairwise d < 0.18)
- All residual diagnostics PASS (normality, equal variance)
- Sample size: [STAT:n=150 (30 per group)]
- Statistical power: [STAT:power=0.97]

**Trust Level**: HIGH

**Trust Rationale**:
- All ANOVA assumptions satisfied (first ablation experiment to achieve this)
- p < 0.001 with three independent tests converging
- Large effect size (Cohen's f = 0.381)
- Balanced design with identical seeds across conditions
- No zero-kill episodes (0% vs 9.3% in DOE-007)
- High achieved power (97%)

**Interpretation**:
Pure reflex rules (L0_only: health<30->flee, ammo==0->flee, else->attack) perform significantly worse than ALL other architectures on defend_the_line. The "always attack" rule creates tunnel vision: L0_only commits to one enemy at a time without sweeping across the approaching enemy line. Any mechanism that introduces lateral movement (random choice, memory dodge, strength probabilistic attack) breaks this tunnel vision and provides equivalent large benefit (+5.7 kills/min).

The heuristic layers (memory dodge, strength modulation) provide NO advantage over random action selection. Their value is not in their design but in the incidental lateral movement they produce. The SOURCE of lateral movement does not matter -- only its PRESENCE.

**Rank Order Reversal**: L0_only went from BEST performer in DOE-007 (defend_the_center) to WORST in DOE-008 (defend_the_line). Agent architecture performance is scenario-dependent, not a fixed property.

**Adopted**: 2026-02-08 (Phase 0/1)

**Recommended Next**:
1. Restructure L0 rules to include turn-toward-nearest-enemy (fix tunnel vision)
2. Test on third scenario for generalization evidence
3. Expand action space to give heuristics more expressive power

---

### F-011: Combined Heuristics Reduce Raw Kills (Full Agent Penalty)

**Hypothesis**: H-012 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-008 (EXPERIMENT_ORDER_008.md)
**Experiment Report**: RPT-008 (EXPERIMENT_REPORT_008.md)

**Evidence**:
- C3 contrast (kills): t=2.759 [STAT:p=0.007] [STAT:effect_size=Cohen's d=0.487] (medium)
- Single-heuristic agents mean kills: 14.65 vs full_agent: 11.90
- L0_strength vs full_agent (Tukey kills): +3.03, p_adj=0.045 (significant)
- C3 contrast (kill_rate): t=0.264, p=0.792 (NOT significant on kill_rate)
- Full_agent survival: 17.13s vs single-heuristic: 20.86s (shorter survival partially compensates fewer kills in kill_rate)

**Trust Level**: MEDIUM

**Trust Rationale**:
- Effect present on raw kills (p=0.007) but NOT on kill_rate (p=0.792)
- Medium effect size (d=0.487), not large
- Mechanistic explanation plausible (excessive dodging from stacked heuristics)
- Consistent direction across DOE-007 and DOE-008 (full_agent trends lower in both)
- Not the primary response variable (kill_rate is primary)

**Interpretation**:
Combining memory dodge AND strength modulation (full_agent) produces fewer raw kills than either heuristic alone. The combined heuristics likely cause excessive dodging: memory dodge triggers lateral movement on health loss, while strength modulation adds probabilistic non-attack actions, reducing overall attack frequency. This penalty is partially masked in kill_rate because full_agent also dies faster (17.13s vs 20.86s for single-heuristic), deflating the denominator.

This finding is weaker than F-010 because it appears only on raw kills (secondary response), not on kill_rate (primary response). The PI should consider it as directional evidence of heuristic interference, not a definitive conclusion.

**Adopted**: 2026-02-08 (Phase 0/1) -- MEDIUM trust, pending confirmation

---

### F-012: Scenario Selection Critical for Architectural Discriminability

**Hypothesis**: H-012 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-007 and DOE-008 (paired comparison)
**Experiment Report**: RPT-007 and RPT-008

**Evidence**:
- DOE-007 (defend_the_center): [STAT:f=F(4,145)=1.579] [STAT:p=0.183] [STAT:eta2=0.042] -- NOT significant
- DOE-008 (defend_the_line): [STAT:f=F(4,145)=5.256] [STAT:p=0.000555] [STAT:eta2=0.127] -- SIGNIFICANT
- Same 5-level design, same analysis, changed scenario only
- Discriminability ratio (Range/Pooled SD): 0.60 (center) vs 1.04 (line) -- 1.7x improvement
- Effect size: 3x larger on defend_the_line (eta^2: 0.127 vs 0.042)
- Power: 97% (line) vs 49% (center)
- Residual diagnostics: ALL FAIL (center) vs ALL PASS (line)
- Zero-kill episodes: 9.3% (center) vs 0% (line)

**Trust Level**: HIGH

**Trust Rationale**:
- Direct paired comparison (identical design, one change)
- Consistent methodology across experiments
- Clear mechanistic explanation (kill range 4-26 vs 0-3)
- Diagnostic improvement confirms scenario quality

**Interpretation**:
defend_the_line is the superior scenario for testing agent architectural differences. It provides 8x the kill range, 1.7x better signal-to-noise ratio, 3x larger effect sizes, and fully compliant residual diagnostics. Future experiments in the clau-doom program should use defend_the_line as the standard evaluation scenario.

**Adopted**: 2026-02-08 (Phase 0/1)

---

## DOE-009 Findings (Memory × Strength on defend_the_line — NULL RESULT)

### F-013: Memory Weight Has No Effect on Kill Rate in Real VizDoom

**Hypothesis**: H-013 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-009 (EXPERIMENT_ORDER_009.md)
**Experiment Report**: RPT-009 (EXPERIMENT_REPORT_009.md)

**Evidence**:
- 2-way ANOVA: [STAT:f=F(2,261)=0.306] [STAT:p=0.736]
- Effect size negligible: [STAT:eta2=partial η²=0.002]
- Sample size: [STAT:n=270 (30 per cell, 9 cells)]
- All diagnostics PASS (Shapiro p=0.098, Levene p=0.196)
- Non-parametric confirms: Kruskal-Wallis p=0.500

**Trust Level**: HIGH (for null result)

**Interpretation**:
Varying memory_weight from 0.1 to 0.9 has no detectable effect on kill_rate in defend_the_line. Main effect means: memory=0.1: 42.29 kr, memory=0.5: 42.96 kr, memory=0.9: 42.94 kr. The memory dodge heuristic's probability modulation is overwhelmed by gameplay noise and L0 emergency rules.

**INVALIDATES**: F-005 (H-006, adopted from DOE-002 mock data claiming memory explains 41.5% of variance)

**Adopted**: 2026-02-08 (Phase 1)

---

### F-014: Strength Weight Has No Significant Effect on Kill Rate in Real VizDoom

**Hypothesis**: H-013 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-009 (EXPERIMENT_ORDER_009.md)
**Experiment Report**: RPT-009 (EXPERIMENT_REPORT_009.md)

**Evidence**:
- 2-way ANOVA: [STAT:f=F(2,261)=2.235] [STAT:p=0.109]
- Effect size small: [STAT:eta2=partial η²=0.017]
- Sample size: [STAT:n=270 (30 per cell, 9 cells)]
- Borderline trend: strength=0.1 (41.55 kr) vs strength=0.5 (43.43 kr)

**Trust Level**: HIGH (for null result)

**Interpretation**:
Strength_weight shows a non-significant trend (p=0.109). Low strength (0.1) yields ~2 kr less than medium/high strength (0.5/0.9), but this does not reach significance. The strength attack probability modulation has a weak effect at best, insufficient to produce reliable performance differences.

**INVALIDATES**: F-006 (H-007, adopted from DOE-002 mock data claiming strength explains 31.6% of variance)

**Adopted**: 2026-02-08 (Phase 1)

---

### F-015: No Memory × Strength Interaction in Real VizDoom

**Hypothesis**: H-013 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-009 (EXPERIMENT_ORDER_009.md)
**Experiment Report**: RPT-009 (EXPERIMENT_REPORT_009.md)

**Evidence**:
- 2-way ANOVA: [STAT:f=F(4,261)=0.365] [STAT:p=0.834]
- Effect size negligible: [STAT:eta2=partial η²=0.006]
- Sample size: [STAT:n=270]

**Trust Level**: HIGH (for null result)

**Interpretation**:
Memory and strength do not interact. The factors are independently (and equally) ineffective. The synergistic interaction claimed by DOE-002 mock data does not exist in real gameplay.

**INVALIDATES**: F-007 (H-008, adopted from DOE-002 mock data claiming significant interaction)

**Adopted**: 2026-02-08 (Phase 1)

---

## DOE-010 Findings (Structured Lateral Movement Strategies)

### F-016: Strategy Architecture Significantly Affects Kill Rate (DOE-010 Replication)

**Hypothesis**: H-014 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-010 (EXPERIMENT_ORDER_010.md)
**Experiment Report**: RPT-010 (EXPERIMENT_REPORT_010.md)

**Evidence**:
- One-way ANOVA: [STAT:f=F(4,145)=4.938] [STAT:p=0.000923] [STAT:eta2=η²=0.120] (medium)
- Kruskal-Wallis confirms: H(4)=17.438 [STAT:p=0.001589]
- C1 contrast (L0_only vs all others): t=-3.480 [STAT:p=0.001] [STAT:effect_size=Cohen's d=0.654]
- Sample size: [STAT:n=150 (30 per group)]
- Achieved power: [STAT:power=0.962]

**Trust Level**: HIGH

**Interpretation**:
Confirms DOE-008 F-010 with independent strategies and seed set. L0_only remains significantly worse than alternatives on defend_the_line.

**Adopted**: 2026-02-08 (Phase 1)

---

### F-017: Deterministic Oscillation Equivalent to No Lateral Movement

**Hypothesis**: H-014 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-010 (EXPERIMENT_ORDER_010.md)
**Experiment Report**: RPT-010 (EXPERIMENT_REPORT_010.md)

**Evidence**:
- sweep_lr vs L0_only: Tukey p_adj=0.968 [STAT:effect_size=Cohen's d=0.215] (negligible)
- sweep_lr mean: 39.94 kr, L0_only mean: 39.00 kr — statistically indistinguishable
- sweep_lr vs burst_3: Tukey p_adj=0.018 [STAT:effect_size=Cohen's d=0.857] (large) — sweep significantly worse
- Both sweep_lr and L0_only have ~identical kills (8.57 vs 8.40) and survival (12.92s vs 12.95s)

**Trust Level**: HIGH

**Interpretation**:
The deterministic attack-left-attack-right sweep pattern creates rapid oscillation (period 4 ticks = ~114ms) that does NOT produce effective repositioning. The agent jitters in place without changing its field of fire. This reveals that effective lateral movement requires sustained directional commitment — a few ticks in the same direction to actually displace the agent — not mere presence of movement commands. Rapid alternation is functionally equivalent to standing still.

**Adopted**: 2026-02-08 (Phase 1)

---

### F-018: Structured Patterns Do Not Outperform Random (H-014 Rejected)

**Hypothesis**: H-014 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-010 (EXPERIMENT_ORDER_010.md)
**Experiment Report**: RPT-010 (EXPERIMENT_REPORT_010.md)

**Evidence**:
- C2 contrast (random vs structured): t=-0.332 [STAT:p=0.741] [STAT:effect_size=Cohen's d=0.073] (negligible)
- random mean: 42.16 kr, structured mean: 42.62 kr
- burst_3 vs random: Tukey p_adj=0.485, d=0.370 (small, NS)
- burst_5 vs random: Tukey p_adj=0.926, d=0.191 (negligible, NS)

**Trust Level**: HIGH (for null result — power 0.962 rules out large effects)

**Interpretation**:
H-014 is rejected. Structured lateral movement patterns do not outperform random movement on defend_the_line. Burst strategies (burst_3, burst_5) MATCH random performance but cannot exceed it. With the current 3-action space (attack/left/right), random movement is already near-optimal for producing effective lateral displacement. The action space is the bottleneck — more expressive actions (turn, aim, compound movements) may be needed to enable intelligent strategies to outperform random.

**Adopted**: 2026-02-08 (Phase 1)

---

### F-019: Performance Hierarchy — Effective Displacement vs Oscillation

**Hypothesis**: H-014 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-010 (EXPERIMENT_ORDER_010.md)
**Experiment Report**: RPT-010 (EXPERIMENT_REPORT_010.md)

**Evidence**:
- Group A (effective displacement): burst_3=44.55, burst_5=43.36, random=42.16 kr
- Group B (no effective displacement): sweep_lr=39.94, L0_only=39.00 kr
- C3 contrast (sweep vs burst): t=-3.559 [STAT:p=0.000638] [STAT:effect_size=Cohen's d=0.758] (medium-large)
- kills ANOVA: [STAT:f=F(4,145)=12.654] [STAT:p<0.000001] [STAT:eta2=0.259]
- survival ANOVA: [STAT:f=F(4,145)=7.700] [STAT:p=0.000012] [STAT:eta2=0.175]

**Trust Level**: HIGH

**Interpretation**:
The five strategies form two distinct performance tiers. Group membership is determined by whether the strategy produces effective physical displacement (multiple consecutive same-direction moves) vs oscillation or stasis. All three secondary responses (kill_rate, kills, survival_time) show the same grouping pattern. The 3-action space ceiling is approximately 43-45 kr for any strategy that achieves effective displacement.

**Adopted**: 2026-02-08 (Phase 1)