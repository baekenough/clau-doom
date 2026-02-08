# EXPERIMENT_REPORT_005: DOE-005 Memory x Strength Expanded Range Factorial

**Experiment Order**: DOE-005 (EXPERIMENT_ORDER_005.md)
**Hypothesis**: H-009 (HYPOTHESIS_BACKLOG.md)
**Date**: 2026-02-08
**Status**: COMPLETE
**Author**: research-analyst

---

## Design Summary

- **Type**: 2^2 Full Factorial with 3 Center Points
- **Factors**: Memory (A) [0.7, 0.9], Strength (B) [0.7, 0.9], Center [0.8, 0.8]
- **Episodes**: 4 factorial cells x 30 = 120 factorial, 3 center batches x 10 = 30 center = 150 total
- **Seeds**: seed_i = 2501 + i*23, i=0..29 (identical across all factorial cells)
- **Primary Response**: kill_rate = kills / (survival_time / 60.0) [kills/min]
- **Scenario**: Defend the Center (defend_the_center.cfg)
- **Key Context**: First experiment with REAL VizDoom data after KILLCOUNT mapping bug fix. DOE-002 used erroneous data where "kills" was actually AMMO2=26 (constant). DOE-005 measures true gameplay kills.

---

## Data Validation

| Check | Status |
|-------|--------|
| Total episodes recorded | 150 (120 factorial + 30 center) -- PASS |
| Factorial cells balanced | 30 per cell -- PASS |
| Center point batches | 3 x 10 = 30 -- PASS |
| Seed integrity | All factorial cells use identical seed set [2501..3168] -- PASS |
| No duplicate episodes | PASS |
| All metrics within plausible ranges | PASS |
| Zero-kill episodes | 14/150 (9.3%) -- expected for real gameplay |

---

## Descriptive Statistics

### Cell Means (kill_rate, kills/min)

| Memory | Strength | Mean | SD | n | 95% CI |
|--------|----------|------|-----|---|--------|
| 0.7 | 0.7 | 8.03 | 3.67 | 30 | [6.66, 9.40] |
| 0.7 | 0.9 | 9.32 | 3.94 | 30 | [7.85, 10.79] |
| 0.9 | 0.7 | 7.60 | 3.43 | 30 | [6.32, 8.88] |
| 0.9 | 0.9 | 8.51 | 3.88 | 30 | [7.06, 9.96] |
| 0.8 (center) | 0.8 (center) | 7.97 | 4.78 | 30 | [6.18, 9.75] |

### Cell Means (kills, count)

| Memory | Strength | Mean | SD |
|--------|----------|------|-----|
| 0.7 | 0.7 | 1.17 | 0.59 |
| 0.7 | 0.9 | 1.30 | 0.60 |
| 0.9 | 0.7 | 1.10 | 0.55 |
| 0.9 | 0.9 | 1.23 | 0.68 |
| 0.8 (center) | 0.8 (center) | 1.13 | 0.73 |

### Cell Means (survival_time, seconds)

| Memory | Strength | Mean | SD |
|--------|----------|------|-----|
| 0.7 | 0.7 | 8.55 | 1.16 |
| 0.7 | 0.9 | 8.29 | 1.40 |
| 0.9 | 0.7 | 8.59 | 1.35 |
| 0.9 | 0.9 | 8.50 | 1.51 |
| 0.8 (center) | 0.8 (center) | 8.50 | 1.15 |

### Marginal Means (kill_rate)

| Factor | Level | Mean |
|--------|-------|------|
| Memory | 0.7 | 8.67 |
| Memory | 0.9 | 8.06 |
| Strength | 0.7 | 7.81 |
| Strength | 0.9 | 8.91 |
| Grand mean (factorial) | -- | 8.36 |
| Center point | 0.8, 0.8 | 7.97 |

---

## Primary Analysis: Two-Way ANOVA on kill_rate (Confirmatory)

### ANOVA Table (Type II Sum of Squares)

| Source | SS | df | MS | F | p-value | partial eta2 | omega2 |
|--------|-------|----|----|------|---------|-------------|--------|
| Memory (A) | 11.369 | 1 | 11.369 | 0.814 | 0.3689 | 0.0070 | -0.0015 |
| Strength (B) | 36.224 | 1 | 36.224 | 2.593 | 0.1101 | 0.0219 | 0.0132 |
| Memory x Strength (AxB) | 1.100 | 1 | 1.100 | 0.079 | 0.7795 | 0.0007 | -0.0076 |
| Residual | 1620.693 | 116 | 13.972 | | | | |
| **Total** | **1669.386** | **119** | | | | | |

**Memory (A)**: [STAT:f=F(1,116)=0.814] [STAT:p=0.3689] [STAT:eta2=partial eta2=0.0070] -- NOT significant

**Strength (B)**: [STAT:f=F(1,116)=2.593] [STAT:p=0.1101] [STAT:eta2=partial eta2=0.0219] -- NOT significant

**Memory x Strength (AxB)**: [STAT:f=F(1,116)=0.079] [STAT:p=0.7795] [STAT:eta2=partial eta2=0.0007] -- NOT significant

[STAT:n=120 factorial episodes (30 per cell)]

### Summary

**No factor or interaction reaches statistical significance at alpha=0.05.** In the [0.7, 0.9] range, neither Memory nor Strength has a detectable effect on kill_rate. The effects observed in DOE-002's [0.3, 0.7] range have effectively vanished at this higher operating range.

---

## Secondary Analyses (Exploratory)

### ANOVA on kills (count)

| Source | SS | df | F | p-value | partial eta2 |
|--------|-------|----|----|---------|-------------|
| Memory (A) | 0.133 | 1 | 0.364 | 0.5477 | 0.0031 |
| Strength (B) | 0.533 | 1 | 1.455 | 0.2303 | 0.0124 |
| AxB | 0.000 | 1 | 0.000 | 1.0000 | 0.0000 |
| Residual | 42.533 | 116 | | | |

No significant effects on kill count.

### ANOVA on survival_time (seconds)

| Source | SS | df | F | p-value | partial eta2 |
|--------|-------|----|----|---------|-------------|
| Memory (A) | 0.460 | 1 | 0.248 | 0.6196 | 0.0021 |
| Strength (B) | 0.921 | 1 | 0.496 | 0.4825 | 0.0043 |
| AxB | 0.192 | 1 | 0.103 | 0.7483 | 0.0009 |
| Residual | 215.308 | 116 | | | |

No significant effects on survival time.

### Consistency Across Responses

All three response variables (kill_rate, kills, survival_time) show the same pattern: no significant main effects or interactions in the [0.7, 0.9] range. This consistency strengthens the conclusion that the factor effects have plateaued.

---

## Residual Diagnostics

### Normality

**Shapiro-Wilk Test**:
- W = 0.9149, p = 0.000001
- Result: **FAIL** (p < 0.05)

**Anderson-Darling Test**:
- A2 = 4.263
- Rejects normality at all significance levels (1%, 2.5%, 5%, 10%, 15%)
- Result: **FAIL**

**Q-Q Plot Correlation**: r = 0.9524 (below 0.97 threshold)

**Root Cause**: The kill_rate distribution has 14/150 (9.3%) zero values (episodes with 0 kills produce kill_rate=0), creating a zero-inflated, right-skewed distribution. This is a structural feature of real VizDoom gameplay data, not a data quality issue. Per-group skewness ranges from -0.56 to +1.27, with excess kurtosis up to 3.88.

### Equal Variance

**Levene's Test**: F = 0.226, p = 0.8779 -- **PASS**

**Bartlett's Test**: T = 0.668, p = 0.8808 -- **PASS**

Variance is homogeneous across all four factorial cells. This is a strong result.

### Outliers

- Max |studentized residual|: 3.376
- Outliers (|r| > 3): 1 observation
- Result: **MARGINAL** (1 outlier at boundary, not extreme)

### Independence

- All factorial cells used identical seed set [2501..3168]
- Execution followed randomized run order
- No time-dependent confounds within VizDoom simulation
- Result: **PASS**

### Overall Diagnostics: PARTIAL FAIL (normality violated)

The normality assumption is violated. However:
1. Equal variance holds strongly (Levene p = 0.88)
2. Sample sizes are equal and adequate (n=30)
3. ANOVA is robust to moderate non-normality with equal variances and balanced designs (Lindman, 1974)

To validate conclusions, non-parametric alternatives were applied (see below).

---

## Non-Parametric Verification

Given the normality violation, all primary conclusions were verified with distribution-free methods.

### Kruskal-Wallis Tests

| Response | H statistic | p-value | Conclusion |
|----------|-------------|---------|------------|
| kill_rate | 4.428 | 0.2188 | Not significant |
| kills | 1.473 | 0.6885 | Not significant |
| survival_time | 1.906 | 0.5921 | Not significant |

### Aligned Rank Transform (ART) ANOVA

The ART procedure aligns data by removing other effects, then ranks the aligned data, providing a robust nonparametric factorial ANOVA:

| Effect | F | p-value | Conclusion |
|--------|------|---------|------------|
| Memory (A) | 0.105 | 0.7463 | Not significant |
| Strength (B) | 3.265 | 0.0733 | Not significant (borderline) |
| AxB Interaction | 0.000 | 0.9875 | Not significant |

### Robustness Assessment

Both parametric (ANOVA) and non-parametric (Kruskal-Wallis, ART ANOVA) methods agree: no significant effects exist. The Strength effect shows a borderline trend in ART ANOVA (p=0.073) consistent with the parametric ANOVA (p=0.110). This convergence confirms the primary conclusion is robust to the normality violation.

---

## Curvature Test (Critical for Phase Transition)

### Comparison: Factorial Average vs Center Point Mean

| Metric | Value |
|--------|-------|
| Average of 4 factorial cell means | 8.364 kills/min |
| Center point mean (0.8, 0.8) | 7.966 kills/min |
| Curvature (center - factorial avg) | -0.398 kills/min |
| Curvature F-test: F(1,145) | 0.241 |
| Curvature p-value | 0.6242 |
| Welch t-test (factorial vs center) | t = 0.425, p = 0.673 |
| Mann-Whitney U (factorial vs center) | U = 2047.5, p = 0.246 |

**Conclusion**: [STAT:p=0.6242] -- **NO CURVATURE DETECTED**. The linear model is adequate in the [0.7, 0.9] range. However, since the linear effects themselves are non-significant, this means the response surface is essentially FLAT (plateau) in this region.

---

## Effect Sizes

### Partial Eta-Squared (ANOVA effects)

| Effect | partial eta2 | omega2 | Interpretation |
|--------|-------------|--------|---------------|
| Memory | 0.0070 | -0.0015 | Negligible |
| Strength | 0.0219 | 0.0132 | Small |
| Interaction | 0.0007 | -0.0076 | Negligible |

Note: Negative omega-squared values indicate the effect is indistinguishable from zero (estimated variance component is zero or negative).

### Cohen's d (Pairwise Comparisons)

| Comparison | d | Interpretation |
|-----------|------|---------------|
| (0.7,0.9) vs (0.7,0.7) | +0.339 | Small |
| (0.9,0.7) vs (0.7,0.7) | -0.119 | Negligible |
| (0.9,0.9) vs (0.7,0.7) | +0.128 | Negligible |
| (0.9,0.7) vs (0.7,0.9) | -0.464 | Small |
| (0.9,0.9) vs (0.7,0.9) | -0.206 | Small |
| (0.9,0.9) vs (0.9,0.7) | +0.248 | Small |

### Main Effect Cohen's d

| Effect | d | Direction | Interpretation |
|--------|------|-----------|---------------|
| Memory (0.9 vs 0.7) | [STAT:effect_size=Cohen's d=-0.164] | Memory=0.9 slightly WORSE | Negligible |
| Strength (0.9 vs 0.7) | [STAT:effect_size=Cohen's d=0.295] | Strength=0.9 slightly better | Small |

---

## Power Analysis

### Achieved Power (for observed effect sizes)

| Effect | F(1,116) | p | Achieved Power |
|--------|----------|---|---------------|
| Memory | 0.814 | 0.369 | [STAT:power=0.145] |
| Strength | 2.593 | 0.110 | [STAT:power=0.359] |
| Interaction | 0.079 | 0.779 | [STAT:power=0.059] |

### Design Power (for reference effect sizes)

| Effect size (f) | Required n/cell for power=0.80 | Our n/cell | Our power |
|-----------------|-------------------------------|------------|-----------|
| 0.15 (small) | 88 | 30 | ~0.30 |
| 0.20 (small-medium) | 50 | 30 | ~0.50 |
| 0.25 (medium) | 32 | 30 | 0.775 |
| 0.30 (medium-large) | 23 | 30 | ~0.90 |

### Power Interpretation

The design had adequate power (0.78) to detect medium effects (f=0.25) and high power (0.90) for medium-large effects (f=0.30). The observed effect sizes are much smaller than medium:
- Memory: f = 0.084 (very small)
- Strength: f = 0.150 (small)
- Interaction: f = 0.026 (negligible)

The non-significance is not merely a power issue -- the true effects in the [0.7, 0.9] range are genuinely small. Even with n=88 per cell (352 total), only the Strength effect might reach significance, and the practical significance would remain minimal (1.1 kills/min difference with overlapping confidence intervals).

---

## Simple Effects Analysis

Although the interaction is non-significant, simple effects are reported for completeness:

### Memory Effect at Each Strength Level

| Strength | Memory 0.9 - 0.7 | t | p |
|----------|-----------------|---|----|
| 0.7 | -0.42 kills/min | 0.46 | 0.646 |
| 0.9 | -0.81 kills/min | 0.80 | 0.428 |

### Strength Effect at Each Memory Level

| Memory | Strength 0.9 - 0.7 | t | p |
|--------|-------------------|---|----|
| 0.7 | +1.29 kills/min | -1.31 | 0.195 |
| 0.9 | +0.91 kills/min | -0.96 | 0.342 |

Strength consistently shows a positive trend (higher Strength improves kill_rate by ~1 kill/min) while Memory shows a slightly negative trend (higher Memory marginally decreases kill_rate). Neither reaches significance.

---

## Confidence Intervals for Main Effects

### Memory Effect (0.9 - 0.7)

- Difference: -0.616 kills/min
- [STAT:ci=95%: -1.97 to 0.74]
- Includes zero: consistent with no effect

### Strength Effect (0.9 - 0.7)

- Difference: +1.099 kills/min
- [STAT:ci=95%: -0.25 to 2.44]
- Includes zero: consistent with no effect (though borderline)

---

## Cross-Experiment Comparison with DOE-002

### Replication Check: (0.7, 0.7) Cell

| Experiment | Mean | SD | n |
|-----------|------|-----|---|
| DOE-002 | 9.65 | 1.53 | 30 |
| DOE-005 | 8.03 | 3.67 | 30 |

- Welch's t-test: t = -2.23, df = 38.8, [STAT:p=0.0313]
- Cohen's d: -0.577 (medium)
- Mean difference: -1.62 kills/min [STAT:ci=95%: -3.09 to -0.15]

**Replication: FAILED** (p = 0.031 < 0.05)

### Interpretation of Replication Failure

The replication failure is EXPECTED and EXPLAINED by a critical context difference:

1. **DOE-002 used ERRONEOUS data**: A KILLCOUNT mapping bug meant DOE-002's "kills" variable was actually AMMO2=26 (a constant). The kill_rate values in DOE-002 were computed from fictitious kill counts, not real gameplay kills.

2. **DOE-005 uses REAL data**: After the KILLCOUNT bug fix, DOE-005 records true VizDoom kills. Real gameplay has much higher variance (SD=3.67 vs 1.53) and lower mean kill_rate.

3. **The 5.76x variance ratio** (DOE-005 vs DOE-002) confirms the data generation mechanism fundamentally changed.

**Conclusion**: Cross-experiment comparison between DOE-002 and DOE-005 is INVALID because the measurement instruments differed. DOE-002 results should be treated as baseline characterization under erroneous conditions. DOE-005 is the first valid experiment with real kills data.

---

## Trust Assessment

**Trust Level**: MEDIUM

### Criteria Assessment

| Criterion | Status | Notes |
|-----------|--------|-------|
| Sample size | [STAT:n=30 per cell] | Adequate for medium effects |
| Normality | FAIL | Mitigated by balanced design + non-parametric verification |
| Equal variance | PASS (p=0.88) | Strong homoscedasticity |
| Non-parametric agreement | PASS | Kruskal-Wallis and ART ANOVA confirm all findings |
| Seed integrity | PASS | Identical seeds across factorial cells |
| Power for medium effects | 0.78 | Near target 0.80 |
| Cross-experiment replication | N/A | Invalid comparison due to DOE-002 data bug |

Trust is MEDIUM (not HIGH) because:
1. Normality assumption is violated (though mitigated)
2. DOE-002 cross-validation is impossible due to measurement change
3. This is the FIRST experiment with real kills data -- no prior benchmark

---

## Conclusions

### H-009: Continued Improvement at [0.7, 0.9] Range

**Status**: REJECTED

H-009 stated: "Increasing memory_weight and strength_weight beyond 0.7 (toward 0.9) continues to improve kill_rate without diminishing returns."

Evidence against H-009:
- Memory main effect: [STAT:f=F(1,116)=0.814] [STAT:p=0.3689] -- not significant
- Strength main effect: [STAT:f=F(1,116)=2.593] [STAT:p=0.1101] -- not significant
- No curvature detected: [STAT:p=0.6242]
- All non-parametric tests confirm non-significance

The kill_rate response surface is essentially FLAT in the [0.7, 0.9] range. Increasing Memory or Strength beyond 0.7 provides no statistically significant improvement.

### Direction of Non-Significant Trends

While no effect is significant, the directional trends are noteworthy:

1. **Memory has a slightly NEGATIVE trend**: Memory=0.9 yields 0.62 kills/min LESS than Memory=0.7. Higher memory reliance may introduce noise into decision-making at extreme values.

2. **Strength has a slightly POSITIVE trend**: Strength=0.9 yields 1.10 kills/min MORE than Strength=0.7. This is the largest effect observed but still non-significant (p=0.11).

3. **No interaction**: The Memory x Strength interaction is essentially zero (p=0.78).

### Real VizDoom Baseline Established

DOE-005 establishes the first valid performance baseline with real VizDoom kills:
- Grand mean kill_rate: 8.36 kills/min across all conditions
- Average kills per episode: ~1.2
- Average survival: ~8.5 seconds
- Kill_rate SD: ~3.7 (high variance typical of real gameplay)
- Zero-kill rate: ~9% of episodes

---

## Phase Transition Assessment

### Does DOE-005 Support Phase 2 (RSM)?

**No.** Phase 2 RSM requires either:
1. Significant curvature (to model a quadratic surface) -- NOT found (p=0.62)
2. Significant main effects to optimize -- NOT found (all p > 0.05)

### Recommended Path Forward

This experiment matches **Scenario C from EXPERIMENT_ORDER_005.md**: Performance Plateau.

1. **Performance has plateaued** in the [0.7, 0.9] range for both Memory and Strength
2. The optimal Memory-Strength configuration cannot be precisely determined from this range because all configurations perform similarly
3. **Practical recommendation**: Any value in [0.7, 0.9] for both Memory and Strength produces equivalent kill_rate (~8.4 kills/min). Adopt Memory=0.7, Strength=0.7 as the default (simplest configuration that achieves plateau performance)
4. **Pivot to other factors**: The Memory-Strength optimization space is exhausted. Focus on:
   - H-005: Document quality effects (RAG content improvement)
   - DOE-003 / Layer ablation: Which decision levels (L0/L1/L2) contribute most
   - New factors: weapon selection strategy, spatial awareness, retreat timing

---

## Comparison with DOE-002 (Contextual)

| Metric | DOE-002 [0.3, 0.7] | DOE-005 [0.7, 0.9] | Note |
|--------|---------------------|---------------------|------|
| Memory effect | eta2=0.42 (LARGE) | eta2=0.007 (negligible) | Effect disappeared |
| Strength effect | eta2=0.32 (LARGE) | eta2=0.022 (small) | Effect nearly gone |
| Interaction | eta2=0.04 (small, sig) | eta2=0.001 (zero) | No interaction |
| Curvature | p=0.96 (none) | p=0.62 (none) | Flat in both ranges |

**CRITICAL CAVEAT**: DOE-002 used erroneous kill data (AMMO2 constant mapped as kills). The large effects in DOE-002 may be artifacts of the measurement bug. DOE-005 is the first experiment measuring real kills. The contrast above is provided for documentation completeness but should NOT be interpreted as evidence of diminishing returns between the [0.3, 0.7] and [0.7, 0.9] ranges, because the two experiments measured fundamentally different things.

---

## Recommendations

### Immediate Actions
1. Update FINDINGS.md: H-009 rejected -- no improvement in [0.7, 0.9] range
2. Adopt Memory=0.7, Strength=0.7 as default agent configuration
3. Close the Memory-Strength optimization thread (performance plateau reached)

### Future Experiments
1. **DOE-006**: Repeat DOE-002's [0.3, 0.7] range with REAL kills data to establish valid baseline effects
2. **DOE-007**: Layer ablation study (L0 vs L0+L1 vs L0+L1+L2) -- which decision levels matter
3. **DOE-008**: Document quality manipulation -- does RAG content improvement affect performance

### Methodological Notes
1. Real VizDoom kill_rate data is zero-inflated and non-normal. Future analyses should plan for non-parametric methods as primary or use generalized linear models (Poisson regression for kill counts).
2. Sample size of n=30 per cell provides adequate power for medium effects but not for the small effects observed here. If small effects are scientifically important, increase to n=80-100 per cell.
3. All future cross-experiment comparisons must use DOE-005 as the post-bugfix baseline, not DOE-002.

---

## Statistical Markers Summary

| Marker | Value |
|--------|-------|
| [STAT:f] Memory | F(1,116) = 0.814 |
| [STAT:p] Memory | p = 0.3689 |
| [STAT:eta2] Memory | partial eta2 = 0.0070 |
| [STAT:f] Strength | F(1,116) = 2.593 |
| [STAT:p] Strength | p = 0.1101 |
| [STAT:eta2] Strength | partial eta2 = 0.0219 |
| [STAT:f] Interaction | F(1,116) = 0.079 |
| [STAT:p] Interaction | p = 0.7795 |
| [STAT:eta2] Interaction | partial eta2 = 0.0007 |
| [STAT:p] Curvature | p = 0.6242 |
| [STAT:n] | 120 factorial + 30 center = 150 total |
| [STAT:power] Memory | 0.145 |
| [STAT:power] Strength | 0.359 |
| [STAT:power] Interaction | 0.059 |
| [STAT:effect_size] Memory d | Cohen's d = -0.164 (negligible) |
| [STAT:effect_size] Strength d | Cohen's d = 0.295 (small) |
| [STAT:ci] Memory effect | 95% CI: [-1.97, 0.74] |
| [STAT:ci] Strength effect | 95% CI: [-0.25, 2.44] |

---

## Data Location

- **DuckDB**: `volumes/data/clau-doom.duckdb`
- **Table**: `experiments` (experiment_id = 'DOE-005')
- **Episodes**: 150 rows (120 factorial + 30 center)

---

## Audit Trail

| Document | Status |
|----------|--------|
| HYPOTHESIS_BACKLOG.md | H-009 active |
| EXPERIMENT_ORDER_005.md | ORDERED (2026-02-08) |
| EXPERIMENT_REPORT_005.md | This document (COMPLETE) |
| FINDINGS.md | Pending update (H-009 rejected) |
| RESEARCH_LOG.md | Entry pending |

---

**Report generated**: 2026-02-08
**Analysis method**: Python (statsmodels 0.14.6, scipy 1.17.0, pandas 3.0.0)
**Analyst**: research-analyst (opus)
