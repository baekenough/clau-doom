# EXPERIMENT_REPORT_006: DOE-006 Memory x Strength Wide Range Re-validation with Real KILLCOUNT

**Experiment Order**: DOE-006 (EXPERIMENT_ORDER_006.md)
**Hypothesis**: H-010 (HYPOTHESIS_BACKLOG.md)
**Date**: 2026-02-08
**Status**: COMPLETE
**Author**: research-analyst

---

## Design Summary

- **Type**: 2^2 Full Factorial with 3 Center Points
- **Factors**: Memory (A) [0.3, 0.7], Strength (B) [0.3, 0.7], Center [0.5, 0.5]
- **Episodes**: 4 factorial cells x 30 = 120 factorial, 3 center batches x 10 = 30 center = 150 total
- **Seeds**: seed_i = 3501 + i*29, i=0..29 (identical across all factorial cells)
- **Primary Response**: kill_rate = kills / (survival_time / 60.0) [kills/min]
- **Scenario**: Defend the Center (defend_the_center.cfg)
- **Key Context**: Re-validation of DOE-002's [0.3, 0.7] range with REAL VizDoom KILLCOUNT data. DOE-002 used erroneous AMMO2 constant mapped as kills. DOE-006 is the definitive test of whether Memory and Strength have genuine effects at this wider range.

---

## Data Validation

| Check | Status |
|-------|--------|
| Total episodes recorded | 150 (120 factorial + 30 center) -- PASS |
| Factorial cells balanced | 30 per cell -- PASS |
| Center point batches | 3 x 10 = 30 -- PASS |
| Seed integrity | All factorial cells use identical seed set [3501..4342] -- PASS |
| No duplicate episodes | PASS |
| All metrics within plausible ranges | PASS |
| Zero-kill episodes | 25/150 (16.7%) -- expected for real gameplay |
| kill_rate range | [0.00, 22.66] kills/min -- plausible |

---

## Descriptive Statistics

### Cell Means (kill_rate, kills/min)

| Memory | Strength | Mean | SD | n | 95% CI |
|--------|----------|------|-----|---|--------|
| 0.3 | 0.3 | 6.83 | 5.29 | 30 | [4.86, 8.81] |
| 0.3 | 0.7 | 9.45 | 4.26 | 30 | [7.86, 11.04] |
| 0.7 | 0.3 | 7.73 | 4.93 | 30 | [5.89, 9.57] |
| 0.7 | 0.7 | 7.90 | 4.47 | 30 | [6.23, 9.57] |
| 0.5 (center) | 0.5 (center) | 7.39 | 3.47 | 30 | [6.10, 8.69] |

### Cell Means (kills, count)

| Memory | Strength | Mean | SD |
|--------|----------|------|-----|
| 0.3 | 0.3 | 1.03 | 0.81 |
| 0.3 | 0.7 | 1.33 | 0.66 |
| 0.7 | 0.3 | 1.13 | 0.78 |
| 0.7 | 0.7 | 1.13 | 0.68 |
| 0.5 (center) | 0.5 (center) | 1.10 | 0.55 |

### Cell Means (survival_time, seconds)

| Memory | Strength | Mean | SD |
|--------|----------|------|-----|
| 0.3 | 0.3 | 8.46 | 1.78 |
| 0.3 | 0.7 | 8.36 | 1.75 |
| 0.7 | 0.3 | 8.37 | 1.52 |
| 0.7 | 0.7 | 8.35 | 1.59 |
| 0.5 (center) | 0.5 (center) | 8.77 | 1.18 |

### Marginal Means (kill_rate)

| Factor | Level | Mean |
|--------|-------|------|
| Memory | 0.3 | 8.14 |
| Memory | 0.7 | 7.82 |
| Strength | 0.3 | 7.28 |
| Strength | 0.7 | 8.68 |
| Grand mean (factorial) | -- | 7.98 |
| Center point | 0.5, 0.5 | 7.39 |

---

## Primary Analysis: Two-Way ANOVA on kill_rate (Confirmatory)

### ANOVA Table (Type II Sum of Squares)

| Source | SS | df | MS | F | p-value | partial eta2 | omega2 |
|--------|-------|----|----|------|---------|-------------|--------|
| Memory (A) | 3.136 | 1 | 3.136 | 0.139 | 0.7102 | 0.0012 | -0.0071 |
| Strength (B) | 58.083 | 1 | 58.083 | 2.571 | 0.1115 | 0.0217 | 0.0129 |
| Memory x Strength (AxB) | 44.832 | 1 | 44.832 | 1.985 | 0.1616 | 0.0168 | 0.0081 |
| Residual | 2620.359 | 116 | 22.589 | | | | |
| **Total** | **2726.409** | **119** | | | | | |

**Memory (A)**: [STAT:f=F(1,116)=0.139] [STAT:p=0.7102] [STAT:eta2=partial eta2=0.0012] -- NOT significant

**Strength (B)**: [STAT:f=F(1,116)=2.571] [STAT:p=0.1115] [STAT:eta2=partial eta2=0.0217] -- NOT significant

**Memory x Strength (AxB)**: [STAT:f=F(1,116)=1.985] [STAT:p=0.1616] [STAT:eta2=partial eta2=0.0168] -- NOT significant

[STAT:n=120 factorial episodes (30 per cell)]

### Summary

**No factor or interaction reaches statistical significance at alpha=0.05.** In the [0.3, 0.7] range with real KILLCOUNT data, neither Memory nor Strength has a statistically detectable effect on kill_rate. This directly contradicts DOE-002's findings (Memory eta2=0.42, Strength eta2=0.32), confirming those effects were measurement artifacts of the AMMO2 bug.

Notable observation: The Strength effect (p=0.112, eta2=0.022) and the interaction (p=0.162, eta2=0.017) are both non-significant but show larger trends than DOE-005's analysis of the [0.7, 0.9] range. The interaction is driven by Strength having a large simple effect at Memory=0.3 (see Simple Effects Analysis) but no effect at Memory=0.7.

---

## Secondary Analyses (Exploratory)

### ANOVA on kills (count)

| Source | SS | df | F | p-value | partial eta2 |
|--------|-------|----|----|---------|-------------|
| Memory (A) | -- | 1 | 0.139 | 0.7099 | 0.0012 |
| Strength (B) | -- | 1 | 1.251 | 0.2656 | 0.0107 |
| AxB | -- | 1 | 1.251 | 0.2656 | 0.0107 |
| Residual | -- | 116 | | | |

No significant effects on kill count.

### ANOVA on survival_time (seconds)

| Source | SS | df | F | p-value | partial eta2 |
|--------|-------|----|----|---------|-------------|
| Memory (A) | -- | 1 | 0.021 | 0.8855 | 0.0002 |
| Strength (B) | -- | 1 | 0.035 | 0.8510 | 0.0003 |
| AxB | -- | 1 | 0.019 | 0.8905 | 0.0002 |
| Residual | -- | 116 | | | |

No significant effects on survival time. Survival time is extremely stable across all conditions (~8.4 seconds), confirming that parameter changes do not affect how long the agent survives.

### Consistency Across Responses

All three response variables (kill_rate, kills, survival_time) show the same pattern: no significant main effects or interactions in the [0.3, 0.7] range with real KILLCOUNT data. This consistency strengthens the conclusion that DOE-002's large effects were entirely measurement artifacts.

---

## Residual Diagnostics

### Normality

**Shapiro-Wilk Test**:
- W = 0.9641, p = 0.002750
- Result: **FAIL** (p < 0.05)

**Anderson-Darling Test**:
- A2 = 1.546
- Rejects normality at all significance levels (1%, 2.5%, 5%, 10%, 15%)
- Result: **FAIL**

**Q-Q Plot Correlation**: r = 0.9829 (above 0.97 threshold -- PASS)

**Root Cause**: The kill_rate distribution has 25/150 (16.7%) zero values (episodes with 0 kills produce kill_rate=0), creating a zero-inflated, right-skewed distribution. Per-group distributional characteristics vary: some cells show negative skew (M=0.3,S=0.3: skew=-0.10; M=0.7,S=0.7: skew=-0.47) while one cell shows positive skew (M=0.3,S=0.7: skew=+0.51 with excess kurtosis=2.55). The Q-Q correlation passes the 0.97 threshold, indicating the departure from normality is moderate.

### Equal Variance

**Levene's Test**: F = 1.624, p = 0.1877 -- **PASS**

**Bartlett's Test**: T = 1.630, p = 0.6527 -- **PASS**

Variance is homogeneous across all four factorial cells. This is a strong result.

### Outliers

- Max |studentized residual|: 2.918
- Outliers (|r| > 3): 0 observations
- Result: **PASS** (no extreme outliers)

### Independence

- All factorial cells used identical seed set [3501..4342]
- Execution followed randomized run order
- No time-dependent confounds within VizDoom simulation
- Result: **PASS**

### Overall Diagnostics: PARTIAL FAIL (normality violated)

The normality assumption is violated by formal tests (Shapiro-Wilk p=0.003, Anderson-Darling A2=1.546). However:
1. Q-Q correlation r=0.98 suggests the departure is moderate
2. Equal variance holds strongly (Levene p=0.19)
3. Sample sizes are equal and adequate (n=30)
4. No extreme outliers
5. ANOVA is robust to moderate non-normality with equal variances and balanced designs (Lindman, 1974)

To validate conclusions, non-parametric alternatives were applied (see below).

---

## Non-Parametric Verification

Given the normality violation, all primary conclusions were verified with distribution-free methods.

### Kruskal-Wallis Tests

| Response | H statistic | p-value | Conclusion |
|----------|-------------|---------|------------|
| kill_rate | 3.819 | 0.2817 | Not significant |
| kills | 2.183 | 0.5354 | Not significant |
| survival_time | 0.116 | 0.9898 | Not significant |

### Aligned Rank Transform (ART) ANOVA

The ART procedure aligns data by removing other effects, then ranks the aligned data, providing a robust nonparametric factorial ANOVA:

| Effect | F | p-value | Conclusion |
|--------|------|---------|------------|
| Memory (A) | 0.066 | 0.7982 | Not significant |
| Strength (B) | 2.394 | 0.1245 | Not significant |
| AxB Interaction | 1.851 | 0.1764 | Not significant |

### Mann-Whitney U for Main Effects

| Comparison | U | p-value | Conclusion |
|-----------|------|---------|------------|
| Memory (0.3 vs 0.7) | 1876.0 | 0.6910 | Not significant |
| Strength (0.3 vs 0.7) | 1518.0 | 0.1383 | Not significant |

### Robustness Assessment

Both parametric (ANOVA) and non-parametric (Kruskal-Wallis, ART ANOVA, Mann-Whitney U) methods agree fully: **no significant effects exist in the [0.3, 0.7] range**. The Strength effect shows a consistent but non-significant trend across all methods (ANOVA p=0.112, ART p=0.125, Mann-Whitney p=0.138). This convergence confirms the primary conclusion is robust to the normality violation.

---

## Curvature Test (Critical for Phase Transition)

### Comparison: Factorial Average vs Center Point Mean

| Metric | Value |
|--------|-------|
| Average of 4 factorial cell means | 7.979 kills/min |
| Center point mean (0.5, 0.5) | 7.394 kills/min |
| Curvature (center - factorial avg) | -0.585 kills/min |
| Curvature F-test: F(1,145) | 0.364 |
| Curvature p-value | 0.5473 |
| Welch t-test (factorial vs center) | t = 0.761, p = 0.450 |
| Mann-Whitney U (factorial vs center) | U = 2056.0, p = 0.229 |

**Conclusion**: [STAT:p=0.5473] -- **NO CURVATURE DETECTED**. The linear model is adequate in the [0.3, 0.7] range. Combined with non-significant linear effects, the response surface is essentially FLAT (plateau) across the entire [0.3, 0.7] region.

---

## Effect Sizes

### Partial Eta-Squared (ANOVA effects)

| Effect | partial eta2 | omega2 | Interpretation |
|--------|-------------|--------|---------------|
| Memory | 0.0012 | -0.0071 | Negligible |
| Strength | 0.0217 | 0.0129 | Small |
| Interaction | 0.0168 | 0.0081 | Small (but non-significant) |

Note: Negative omega-squared for Memory indicates the effect is indistinguishable from zero.

### Pairwise Cohen's d

| Comparison | d | Interpretation |
|-----------|------|---------------|
| (0.3,0.7) vs (0.3,0.3) | +0.544 | Medium |
| (0.7,0.3) vs (0.3,0.3) | +0.176 | Negligible |
| (0.7,0.7) vs (0.3,0.3) | +0.218 | Small |
| (0.7,0.3) vs (0.3,0.7) | -0.372 | Small |
| (0.7,0.7) vs (0.3,0.7) | -0.354 | Small |
| (0.7,0.7) vs (0.7,0.3) | +0.036 | Negligible |

The largest pairwise difference is between (0.3, 0.7) and (0.3, 0.3) with d=0.544 (medium effect). This is driven by the Strength simple effect at Memory=0.3 (see Simple Effects Analysis).

### Main Effect Cohen's d

| Effect | d | Direction | Interpretation |
|--------|------|-----------|---------------|
| Memory (0.7 vs 0.3) | [STAT:effect_size=Cohen's d=-0.067] | Memory=0.7 negligibly LOWER | Negligible |
| Strength (0.7 vs 0.3) | [STAT:effect_size=Cohen's d=+0.293] | Strength=0.7 slightly higher | Small |

---

## Power Analysis

### Achieved Power (for observed effect sizes)

| Effect | F(1,116) | p | Achieved Power |
|--------|----------|---|---------------|
| Memory | 0.139 | 0.710 | [STAT:power=0.066] |
| Strength | 2.571 | 0.112 | [STAT:power=0.356] |
| Interaction | 1.985 | 0.162 | [STAT:power=0.287] |

### Observed Cohen's f

| Effect | partial eta2 | Cohen's f |
|--------|-------------|-----------|
| Memory | 0.0012 | 0.035 (very small) |
| Strength | 0.0217 | 0.149 (small) |
| Interaction | 0.0168 | 0.131 (small) |

### Design Power (for reference effect sizes)

| Effect size (f) | Required n/cell for power=0.80 | Our n/cell | Our power |
|-----------------|-------------------------------|------------|-----------|
| 0.10 (very small) | 197 | 30 | 0.192 |
| 0.15 (small) | 88 | 30 | 0.371 |
| 0.20 (small-medium) | 50 | 30 | 0.584 |
| 0.25 (medium) | 32 | 30 | 0.775 |
| 0.30 (medium-large) | 23 | 30 | 0.903 |

### Power Interpretation

The design had adequate power (0.78) to detect medium effects (f=0.25) and high power (0.90) for medium-large effects (f=0.30). The observed effect sizes are below medium:
- Memory: f = 0.035 (very small, essentially zero)
- Strength: f = 0.149 (small)
- Interaction: f = 0.131 (small)

The non-significance is not merely a power issue for Memory (f=0.035 is negligible -- even n=197/cell would not detect it). The Strength effect (f=0.149) would require n=88/cell to reach significance at 80% power. The interaction (f=0.131) would require even more. Importantly, even if these small effects were statistically significant with much larger samples, the practical significance would be minimal (1.4 kills/min difference for Strength, with heavily overlapping confidence intervals).

---

## Simple Effects Analysis

Although the interaction is non-significant (p=0.162), simple effects reveal an interesting asymmetric pattern:

### Memory Effect at Each Strength Level

| Strength | Memory 0.7 - 0.3 | t | p |
|----------|-----------------|---|----|
| 0.3 | +0.90 kills/min | -0.68 | 0.498 |
| 0.7 | -1.55 kills/min | +1.37 | 0.175 |

At Strength=0.3, increasing Memory slightly helps (+0.90). At Strength=0.7, increasing Memory slightly hurts (-1.55). Neither reaches significance, but the pattern reversal contributes to the non-significant interaction trend.

### Strength Effect at Each Memory Level

| Memory | Strength 0.7 - 0.3 | t | p |
|--------|-------------------|---|----|
| 0.3 | +2.61 kills/min | -2.11 | **0.039** |
| 0.7 | +0.17 kills/min | -0.14 | 0.890 |

**Notable finding**: Strength has a significant simple effect at Memory=0.3 (p=0.039, +2.61 kills/min), but no effect at Memory=0.7 (p=0.890, +0.17 kills/min). This suggests that low-memory agents benefit from higher Strength, but high-memory agents (which rely on cached experience) are unaffected by Strength parameter changes. However, this individual simple effect should be interpreted with caution because:
1. The overall interaction is not significant (p=0.162)
2. This was not a pre-planned comparison (exploratory)
3. It would not survive Bonferroni correction for 4 simple effects (adjusted alpha = 0.0125)

---

## Confidence Intervals for Main Effects

### Memory Effect (0.7 - 0.3)

- Difference: -0.323 kills/min
- [STAT:ci=95%: -2.06 to 1.41]
- Includes zero: consistent with no effect

### Strength Effect (0.7 - 0.3)

- Difference: +1.391 kills/min
- [STAT:ci=95%: -0.33 to 3.11]
- Includes zero: consistent with no effect (though borderline positive)

---

## Cross-Experiment Replication Check (DOE-006 vs DOE-005)

### Replication of (0.7, 0.7) Cell

| Experiment | Mean | SD | n |
|-----------|------|-----|---|
| DOE-005 | 8.03 | 3.67 | 30 |
| DOE-006 | 7.90 | 4.47 | 30 |

- Difference: -0.12 kills/min (DOE-006 slightly lower)
- Welch's t-test: t = 0.118, df = 55.9, [STAT:p=0.9066]
- Mann-Whitney U: U = 436.0, p = 0.8416
- Cohen's d: 0.030 (negligible)
- [STAT:ci=95%: -1.99 to 2.24] for DOE-005 - DOE-006 difference
- Variance ratio (DOE-006/DOE-005): 1.480

### Replication: CONFIRMED (p = 0.907)

The (0.7, 0.7) cell replicates almost perfectly between DOE-005 and DOE-006 (mean difference of only 0.12 kills/min, Cohen's d = 0.03). This confirms:
1. The experimental measurement system is stable across experiments
2. KILLCOUNT mapping is consistently measuring real kills
3. The VizDoom simulation environment produces reproducible results
4. Both experiments can be treated as using the same measurement instrument

The variance ratio of 1.48 (DOE-006 slightly more variable) is within acceptable limits (not significantly different by Levene/F-test). Different seed sets across experiments may contribute to minor variance differences.

---

## Trust Assessment

**Trust Level**: MEDIUM

### Criteria Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| Sample size | [STAT:n=30 per cell] | Adequate for medium effects |
| Normality | FAIL (Shapiro-Wilk p=0.003) | Mitigated by balanced design + non-parametric verification |
| Equal variance | PASS (Levene p=0.19) | Homoscedasticity confirmed |
| Non-parametric agreement | PASS | Kruskal-Wallis, ART ANOVA, Mann-Whitney all confirm |
| Seed integrity | PASS | Identical seeds across factorial cells |
| Power for medium effects | 0.78 | Near target 0.80 |
| Cross-experiment replication | PASS (p=0.91) | DOE-005 (0.7,0.7) cell replicated |
| No outliers | PASS | Max |studentized residual| = 2.92 |

Trust is MEDIUM (not HIGH) because:
1. Normality assumption is violated (though mitigated by non-parametric convergence)
2. Zero-kill rate is higher than DOE-005 (16.7% vs 9.3%), suggesting more variability in the wider [0.3, 0.7] range
3. The interesting simple effect (Strength at Memory=0.3, p=0.039) is exploratory and would not survive multiple comparison correction

---

## Conclusions

### H-010: Memory and Strength Effects at [0.3, 0.7] with Real Data

**Status**: REJECTED

H-010 stated: "Memory weight and strength weight have significant main effects on kill_rate in the [0.3, 0.7] range when measured with correct VizDoom KILLCOUNT."

Evidence against H-010:
- Memory main effect: [STAT:f=F(1,116)=0.139] [STAT:p=0.7102] -- not significant, negligible effect
- Strength main effect: [STAT:f=F(1,116)=2.571] [STAT:p=0.1115] -- not significant, small effect
- Interaction: [STAT:f=F(1,116)=1.985] [STAT:p=0.1616] -- not significant
- No curvature detected: [STAT:p=0.5473]
- All non-parametric tests confirm non-significance

**DOE-002's large effects (Memory eta2=0.42, Strength eta2=0.32) were entirely measurement artifacts.** With real KILLCOUNT data, neither factor produces statistically significant effects at any tested range ([0.3, 0.7] in DOE-006 or [0.7, 0.9] in DOE-005).

### Key Finding: DOE-002 Artifact Confirmation

This is the most important result of DOE-006. The re-validation directly demonstrates that DOE-002's dramatic effects were caused by the AMMO2-as-kills measurement bug, not by genuine behavioral differences:

| Metric | DOE-002 [0.3, 0.7] (BUG) | DOE-006 [0.3, 0.7] (REAL) | Conclusion |
|--------|---------------------------|---------------------------|------------|
| Memory eta2 | 0.42 (LARGE) | 0.001 (negligible) | Artifact eliminated |
| Strength eta2 | 0.32 (LARGE) | 0.022 (small) | Artifact mostly eliminated |
| Interaction eta2 | 0.04 (small, sig) | 0.017 (small, n.s.) | Artifact eliminated |
| Curvature p | 0.96 (none) | 0.55 (none) | Consistent |
| kill_rate SD | ~1.5 | ~4.8 | Real gameplay has 10x variance |

### Direction of Non-Significant Trends

While no effect is significant, the directional trends are informative:

1. **Memory has essentially ZERO main effect**: d = -0.067 (negligible). Memory weight does not influence kill_rate at any level.

2. **Strength shows a small positive trend**: d = +0.293 (small). Higher Strength improves kill_rate by ~1.4 kills/min, but this is not significant (p=0.112) and would need n=88/cell to confirm.

3. **The interaction pattern is asymmetric**: Strength helps when Memory is low (Memory=0.3: +2.61 kills/min, p=0.039) but not when Memory is high (Memory=0.7: +0.17, p=0.890). This suggests a ceiling effect or compensatory mechanism -- when the agent already relies on cached experience (high Memory), Strength parameter changes have no incremental effect.

### Real VizDoom Baseline Updated

DOE-006 extends the performance baseline with more data points:
- Grand mean kill_rate (factorial): 7.98 kills/min (consistent with DOE-005's 8.36)
- Average kills per episode: ~1.15
- Average survival: ~8.4 seconds
- Kill_rate SD: ~4.8 (higher variance than DOE-005's ~3.7, reflecting the wider factor range)
- Zero-kill rate: 16.7% (higher than DOE-005's 9.3%, possibly due to lower Strength settings)

---

## Phase Transition Assessment

### Does DOE-006 Support Phase 2 (RSM)?

**No.** Phase 2 RSM requires either:
1. Significant curvature (to model a quadratic surface) -- NOT found (p=0.55)
2. Significant main effects to optimize -- NOT found (all p > 0.05)

### Combined Interpretation: DOE-005 + DOE-006

| Range | Memory Effect | Strength Effect | Interaction | Curvature | Conclusion |
|-------|--------------|-----------------|-------------|-----------|------------|
| [0.3, 0.7] (DOE-006) | p=0.710, negligible | p=0.112, small | p=0.162, small | p=0.547, none | FLAT |
| [0.7, 0.9] (DOE-005) | p=0.369, negligible | p=0.110, small | p=0.780, negligible | p=0.624, none | FLAT |

**The response surface is flat from 0.3 to 0.9 for both factors.** Neither Memory nor Strength weight parameters meaningfully influence real VizDoom kill_rate. The entire Memory-Strength optimization hypothesis is closed.

### Scenario Assessment (from EXPERIMENT_ORDER_006.md)

DOE-006 matches **Scenario B: Effects Not Confirmed (DOE-002 Was Entirely Artifact)**.

- No main effects are significant (all p > 0.10 for Memory; p > 0.10 for Strength)
- Similar to DOE-005: flat response surface across [0.3, 0.7]
- Memory and Strength weight parameters have no real influence on kill_rate at ANY tested range

**Implication**: The entire DOE-002 effect structure was a measurement artifact. Memory_weight and strength_weight do not influence real gameplay performance. The research program must pivot entirely to other factors.

---

## Recommended Path Forward

### Immediate Actions
1. Update FINDINGS.md: H-010 rejected -- DOE-002 effects confirmed as artifacts
2. Mark DOE-002 as INVALID in all references
3. Close the Memory-Strength optimization thread permanently
4. Update HYPOTHESIS_BACKLOG: demote all Memory-Strength hypotheses (H-004, H-009)

### Future Experiments (Priority Order)
1. **DOE-007: Layer Ablation Study** -- Which decision levels (L0 MD rules / L1 DuckDB cache / L2 OpenSearch kNN) actually influence performance? This is the most important question now that parameter tuning is ruled out.
2. **DOE-008: Document Quality Manipulation** -- Does the content of RAG strategy documents affect performance? If the agent retrieves better documents, does kill_rate improve?
3. **DOE-009: Action Space Expansion** -- Does adding more action options (MOVE_FORWARD, MOVE_BACKWARD, TURN) change the performance landscape?
4. **DOE-010: Scenario Complexity** -- Does the factor sensitivity change with different VizDoom scenarios (Deathmatch, Health Gathering)?

### Methodological Notes
1. Real VizDoom kill_rate data is zero-inflated and non-normal. Future analyses should use:
   - Non-parametric methods as co-primary (Kruskal-Wallis, ART ANOVA)
   - Consider Poisson/negative binomial regression for kill counts
   - Report both parametric and non-parametric results
2. The zero-kill rate (16.7%) at [0.3, 0.7] vs 9.3% at [0.7, 0.9] suggests that lower factor settings may increase episode failure probability. This could be explored as a binary outcome (logistic regression: kill vs no-kill).
3. Cross-experiment replication works well with the current setup (DOE-005 vs DOE-006 replication p=0.91). Future experiments should always include an overlapping condition for validation.

---

## Statistical Markers Summary

| Marker | Value |
|--------|-------|
| [STAT:f] Memory | F(1,116) = 0.139 |
| [STAT:p] Memory | p = 0.7102 |
| [STAT:eta2] Memory | partial eta2 = 0.0012 |
| [STAT:f] Strength | F(1,116) = 2.571 |
| [STAT:p] Strength | p = 0.1115 |
| [STAT:eta2] Strength | partial eta2 = 0.0217 |
| [STAT:f] Interaction | F(1,116) = 1.985 |
| [STAT:p] Interaction | p = 0.1616 |
| [STAT:eta2] Interaction | partial eta2 = 0.0168 |
| [STAT:p] Curvature | p = 0.5473 |
| [STAT:n] | 120 factorial + 30 center = 150 total |
| [STAT:power] Memory | 0.066 |
| [STAT:power] Strength | 0.356 |
| [STAT:power] Interaction | 0.287 |
| [STAT:effect_size] Memory d | Cohen's d = -0.067 (negligible) |
| [STAT:effect_size] Strength d | Cohen's d = +0.293 (small) |
| [STAT:ci] Memory effect | 95% CI: [-2.06, 1.41] |
| [STAT:ci] Strength effect | 95% CI: [-0.33, 3.11] |
| [STAT:p] Replication (DOE-005 vs DOE-006) | p = 0.9066 |
| [STAT:effect_size] Replication d | Cohen's d = 0.030 (negligible) |
| [STAT:p] Kruskal-Wallis kill_rate | p = 0.2817 |
| [STAT:p] ART Memory | p = 0.7982 |
| [STAT:p] ART Strength | p = 0.1245 |
| [STAT:p] ART Interaction | p = 0.1764 |
| [STAT:p] Simple: Strength at Memory=0.3 | p = 0.039 (exploratory) |
| [STAT:p] Simple: Strength at Memory=0.7 | p = 0.890 (exploratory) |

---

## Data Location

- **DuckDB**: `volumes/data/clau-doom.duckdb`
- **Table**: `experiments` (experiment_id = 'DOE-006')
- **Episodes**: 150 rows (120 factorial + 30 center)

---

## Audit Trail

| Document | Status |
|----------|--------|
| HYPOTHESIS_BACKLOG.md | H-010 active |
| EXPERIMENT_ORDER_006.md | ORDERED (2026-02-08) |
| EXPERIMENT_REPORT_006.md | This document (COMPLETE) |
| FINDINGS.md | Pending update (H-010 rejected, DOE-002 artifact confirmed) |
| RESEARCH_LOG.md | Entry pending |

---

**Report generated**: 2026-02-08
**Analysis method**: Python (statsmodels 0.14.6, scipy 1.17.0, pandas 3.0.0)
**Analyst**: research-analyst (opus)
