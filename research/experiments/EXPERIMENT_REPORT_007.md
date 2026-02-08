# EXPERIMENT_REPORT_007: Layer Ablation Study

> **Report ID**: RPT-007
> **Experiment ID**: DOE-007
> **Hypothesis**: H-011 (HYPOTHESIS_BACKLOG.md)
> **Experiment Order**: EXPERIMENT_ORDER_007.md
> **Date Analyzed**: 2026-02-08
> **Author**: research-analyst
> **Status**: COMPLETE

---

## Executive Summary

DOE-007 tested whether the action selection architecture layers (L0 reflex rules, memory dodge heuristic, strength attack modulation) have significant effects on kill_rate in defend_the_center. Five architectural configurations were compared: random, L0_only, L0_memory, L0_strength, and full_agent.

**Primary Result**: The one-way ANOVA on kill_rate is NOT significant [STAT:f=F(4,145)=1.5786] [STAT:p=0.183] [STAT:eta2=eta^2=0.0417]. The non-parametric Kruskal-Wallis test confirms non-significance [STAT:p=0.503]. **No architectural configuration significantly outperforms any other in this scenario.**

**Key Surprise**: The random agent performs comparably to all structured agents (mean kill_rate: 8.54 vs 8.25-9.08 for structured agents). This matches Scenario D from the experiment order: defend_the_center is too simple to differentiate architectures using kill_rate as the response.

**Trust Level**: MEDIUM

---

## Data Summary

### Sample

| Property | Value |
|----------|-------|
| Total episodes | 150 |
| Episodes per condition | 30 |
| Invalid/excluded | 0 |
| Seed set | [4501, 4532, ..., 5400] (identical across all 5 conditions) |
| KILLCOUNT verified | Yes (kills vary 0-3, not constant) |

### Descriptive Statistics: kill_rate (kills/min)

| Condition | n | Mean | SD | 95% CI | Min | Median | Max |
|-----------|---|------|-----|--------|-----|--------|-----|
| random | 30 | 8.54 | 5.25 | [6.66, 10.42] | 0.00 | 7.50 | 18.64 |
| L0_only | 30 | 9.08 | 2.75 | [8.09, 10.06] | 5.44 | 8.17 | 14.58 |
| L0_memory | 30 | 8.66 | 2.91 | [7.62, 9.70] | 5.30 | 7.57 | 15.56 |
| L0_strength | 30 | 8.26 | 4.16 | [6.77, 9.75] | 0.00 | 7.47 | 17.21 |
| full_agent | 30 | 6.74 | 3.97 | [5.32, 8.16] | 0.00 | 7.39 | 14.89 |

**Grand mean**: 8.25 kills/min [STAT:n=150]

### Descriptive Statistics: kills (count)

| Condition | n | Mean | SD | Min | Median | Max |
|-----------|---|------|-----|-----|--------|-----|
| random | 30 | 1.30 | 0.84 | 0 | 1 | 3 |
| L0_only | 30 | 1.30 | 0.47 | 1 | 1 | 2 |
| L0_memory | 30 | 1.27 | 0.45 | 1 | 1 | 2 |
| L0_strength | 30 | 1.20 | 0.61 | 0 | 1 | 2 |
| full_agent | 30 | 1.00 | 0.64 | 0 | 1 | 2 |

**Note**: Kill counts are very low (0-3 per episode) due to defend_the_center difficulty. The maximum kill count across ALL 150 episodes is 3.

### Descriptive Statistics: survival_time (seconds)

| Condition | n | Mean | SD | Min | Median | Max |
|-----------|---|------|-----|-----|--------|-----|
| random | 30 | 8.86 | 1.41 | 6.34 | 8.74 | 11.94 |
| L0_only | 30 | 8.61 | 1.46 | 5.83 | 8.66 | 11.26 |
| L0_memory | 30 | 8.86 | 1.45 | 6.51 | 8.69 | 11.83 |
| L0_strength | 30 | 8.65 | 1.40 | 6.51 | 8.66 | 11.83 |
| full_agent | 30 | 8.68 | 1.61 | 6.63 | 8.17 | 12.51 |

**Note**: Survival times are nearly identical across all conditions (range of means: 8.61-8.86 seconds).

### Zero-Kill Episodes

| Condition | Zero-kill episodes | Percentage |
|-----------|-------------------|------------|
| random | 5/30 | 16.7% |
| L0_only | 0/30 | 0.0% |
| L0_memory | 0/30 | 0.0% |
| L0_strength | 3/30 | 10.0% |
| full_agent | 6/30 | 20.0% |

**Observation**: L0_only and L0_memory achieve at least 1 kill in every episode. Full_agent has the HIGHEST zero-kill rate (20.0%), worse than random (16.7%). This paradoxical result is discussed in the Interpretation section.

---

## Primary Analysis: One-Way ANOVA on kill_rate

### ANOVA Table

| Source | SS | df | MS | F | p | eta^2 |
|--------|------|-----|-------|--------|--------|-------|
| action_strategy | 96.80 | 4 | 24.20 | 1.5786 | 0.183 | 0.0417 |
| Error | 2222.83 | 145 | 15.33 | | | |
| Total | 2319.63 | 149 | | | | |

[STAT:f=F(4,145)=1.5786] [STAT:p=0.183] [STAT:eta2=eta^2=0.0417]

### Effect Sizes

| Measure | Value | Interpretation |
|---------|-------|----------------|
| eta-squared | 0.0417 | Small |
| omega-squared | 0.0152 | Negligible-to-small |
| Cohen's f | 0.2087 | Small-to-medium |

**Conclusion**: The overall ANOVA is NOT significant at alpha=0.05. Action selection architecture does not significantly affect kill_rate in defend_the_center. [STAT:p=0.183]

---

## Residual Diagnostics

### Normality

| Test | Statistic | p | Result |
|------|-----------|---|--------|
| Anderson-Darling (overall) | A^2 = 1.8132 | < 0.05 (crit = 0.748) | **FAIL** |
| Shapiro-Wilk (overall) | W = 0.9671 | 0.0012 | **FAIL** |

| Per-Group Shapiro-Wilk | W | p | Result |
|-------------------------|------|-------|--------|
| random | 0.9449 | 0.123 | PASS |
| L0_only | 0.8971 | 0.007 | FAIL |
| L0_memory | 0.8718 | 0.002 | FAIL |
| L0_strength | 0.9287 | 0.045 | FAIL |
| full_agent | 0.8891 | 0.005 | FAIL |

**Note**: Four of five groups fail normality. The kill_rate distribution is right-skewed with zero-inflation (14/150 episodes have zero kills). This is consistent with prior experiments (DOE-005, DOE-006).

### Equal Variance

| Test | Statistic | p | Result |
|------|-----------|---|--------|
| Levene | W = 2.5862 | 0.039 | **FAIL** |
| Bartlett | chi^2 = 16.1661 | 0.003 | **FAIL** |

**Note**: The random group has much higher variance (SD=5.25) than L0_only (SD=2.75), driving the heteroscedasticity. The structured agents have more consistent behavior.

### Outliers

No observations with |studentized residual| > 3. Zero outliers detected.

### Diagnostic Summary

Both ANOVA assumptions are violated:
1. **Normality**: FAIL (kill_rate is zero-inflated and right-skewed)
2. **Equal variance**: FAIL (random SD=5.25 vs L0_only SD=2.75)

However, the non-parametric Kruskal-Wallis test (which requires neither assumption) also finds no significant differences (p=0.503). The ANOVA's non-significance is therefore robust to assumption violations.

---

## Non-Parametric Co-Primary: Kruskal-Wallis

[STAT:p=0.503]

| Statistic | Value |
|-----------|-------|
| H | 3.3397 |
| df | 4 |
| p | 0.503 |
| epsilon-squared | -0.005 (effectively zero) |

**Conclusion**: The Kruskal-Wallis test CONFIRMS the ANOVA result. No significant difference in kill_rate distribution across the five architectural conditions.

Since KW is not significant, Dunn's post-hoc test is not warranted. It was not executed.

---

## Post-Hoc: Tukey HSD Pairwise Comparisons

Although the omnibus ANOVA is non-significant, Tukey HSD was performed for completeness (exploratory). All 10 pairwise comparisons are non-significant after family-wise error correction.

| Comparison | Mean Diff | p_adj | 95% CI | Reject |
|------------|-----------|-------|--------|--------|
| L0_memory vs L0_only | +0.42 | 0.994 | [-2.38, 3.21] | No |
| L0_memory vs L0_strength | -0.41 | 0.995 | [-3.20, 2.39] | No |
| L0_memory vs full_agent | -1.92 | 0.320 | [-4.72, 0.87] | No |
| L0_memory vs random | -0.12 | 1.000 | [-2.91, 2.67] | No |
| L0_only vs L0_strength | -0.82 | 0.927 | [-3.61, 1.97] | No |
| L0_only vs full_agent | -2.34 | 0.146 | [-5.13, 0.45] | No |
| L0_only vs random | -0.54 | 0.984 | [-3.33, 2.26] | No |
| L0_strength vs full_agent | -1.52 | 0.562 | [-4.31, 1.27] | No |
| L0_strength vs random | +0.28 | 0.999 | [-2.51, 3.08] | No |
| full_agent vs random | +1.80 | 0.387 | [-0.99, 4.60] | No |

### Cohen's d for All Pairwise Comparisons

| Comparison | Mean Diff | Cohen's d | Interpretation |
|------------|-----------|-----------|----------------|
| random vs L0_only | -0.54 | -0.128 | Negligible |
| random vs L0_memory | -0.12 | -0.029 | Negligible |
| random vs L0_strength | +0.28 | +0.060 | Negligible |
| random vs full_agent | +1.80 | +0.388 | Small |
| L0_only vs L0_memory | +0.42 | +0.147 | Negligible |
| L0_only vs L0_strength | +0.82 | +0.233 | Small |
| **L0_only vs full_agent** | **+2.34** | **+0.685** | **Medium** |
| L0_memory vs L0_strength | +0.41 | +0.113 | Negligible |
| **L0_memory vs full_agent** | **+1.92** | **+0.553** | **Medium** |
| L0_strength vs full_agent | +1.52 | +0.374 | Small |

**Notable**: L0_only and L0_memory each outperform full_agent by medium effect sizes (d=0.685 and d=0.553). While not statistically significant after Tukey correction, this directional pattern is noteworthy -- the full pipeline (L0 + memory + strength) performs WORSE than L0 alone or L0 + memory alone.

---

## Planned Contrasts

### C1: random vs all others (structured vs unstructured)

[STAT:f=F(1,145)=0.199] [STAT:p=0.656]

**Result**: NOT significant. Random performance is NOT different from the average of all structured approaches. This is a fundamental finding: in defend_the_center with real KILLCOUNT data, random action selection achieves comparable kill_rate to structured decision-making.

### C2: L0_only vs {L0_memory, L0_strength, full_agent} (bare rules vs augmented)

[STAT:f=F(1,145)=2.085] [STAT:p=0.151]

**Result**: NOT significant. Adding heuristic layers (memory, strength, or both) to L0 rules does not improve performance.

### C3: {L0_memory, L0_strength} vs full_agent (single heuristic vs combined)

[STAT:f=F(1,145)=3.870] [STAT:p=0.051]

**Result**: Borderline significant (p=0.051). Single-heuristic configurations perform BETTER than the full combined pipeline. The contrast is in the direction of single-heuristic superiority: L0_memory (8.66) and L0_strength (8.26) both outperform full_agent (6.74).

### C4: L0_memory vs L0_strength (memory vs strength heuristic)

[STAT:f=F(1,145)=0.161] [STAT:p=0.689]

**Result**: NOT significant. The two heuristic layers produce indistinguishable kill_rate outcomes.

---

## Secondary Responses (Exploratory)

### kills (count per episode)

[STAT:f=F(4,145)=1.251] [STAT:p=0.292] [STAT:eta2=0.033]
Kruskal-Wallis: H=4.317, p=0.365

NOT significant. Kill counts are very low (0-3) and do not differ across conditions.

### survival_time (seconds)

[STAT:f=F(4,145)=0.199] [STAT:p=0.938] [STAT:eta2=0.006]
Kruskal-Wallis: H=0.995, p=0.910

NOT significant. All agents survive approximately 8.6-8.9 seconds. Survival does not differentiate architectures.

### ammo_efficiency (hits/shots)

[STAT:f=F(4,145)=1.468] [STAT:p=0.215] [STAT:eta2=0.039]
Kruskal-Wallis: H=2.680, p=0.613

NOT significant. All agents have similarly poor ammo efficiency (5.6%-7.6%).

### damage_dealt (HP)

[STAT:f=F(4,145)=1.251] [STAT:p=0.292] [STAT:eta2=0.033]
Kruskal-Wallis: H=4.317, p=0.365

NOT significant. Damage dealt tracks kills proportionally (each kill = 100 HP damage).

**Summary**: ALL secondary responses are non-significant. No metric differentiates the five architectural configurations.

---

## Power Analysis

| Property | Value |
|----------|-------|
| Observed Cohen's f | 0.2087 |
| Observed power | 0.4932 [STAT:power=0.49] |
| Power for small effect (f=0.10) | 0.134 |
| Power for medium effect (f=0.25) | 0.668 |
| Power for large effect (f=0.40) | 0.983 |
| MDE at power=0.80 | f = 0.287 |

**Interpretation**: The study had 49% power at the observed effect size, which is underpowered. However, the observed effect size (f=0.209, eta^2=0.042) represents a small effect that is not practically meaningful. Even if a larger sample detected statistical significance, the actual performance differences (1-2 kills/min) are within normal episode-to-episode variance.

The minimum detectable effect at 80% power is f=0.287. To detect the observed effect (f=0.209) at 80% power with k=5 groups would require approximately n=55 per group (275 total episodes).

**However**: The Kruskal-Wallis test (p=0.503) with its more lenient assumptions also finds no effect, suggesting the true effect is likely smaller than the parametric estimate.

---

## Cross-Experiment Comparisons

### DOE-007 full_agent vs DOE-005

| Property | DOE-007 full_agent | DOE-005 (all conditions) |
|----------|--------------------|--------------------------|
| Mean kill_rate | 6.74 | 8.28 |
| SD | 3.97 | 3.96 |
| n | 30 | 150 |
| t-test | t = -1.955 | p = 0.052 |
| Cohen's d | -0.391 | Small |

DOE-007 full_agent trends lower than DOE-005 grand mean (6.74 vs 8.28), but the difference is borderline non-significant (p=0.052). The DOE-007 full_agent uses default parameters (memory_weight=0.5, strength_weight=0.5), while DOE-005 tested the [0.7, 0.9] range. This lower performance at default parameters is consistent with the (now-rejected) hypothesis that parameter values matter, though neither DOE-005 nor DOE-006 found significant parametric effects.

### DOE-007 full_agent vs DOE-006

| Property | DOE-007 full_agent | DOE-006 (all conditions) |
|----------|--------------------|--------------------------|
| Mean kill_rate | 6.74 | 7.86 |
| SD | 3.97 | 4.55 |
| n | 30 | 150 |
| t-test | t = -1.263 | p = 0.208 |
| Cohen's d | -0.253 | Small |

Not significantly different from DOE-006 grand mean.

### DOE-001 Random Baseline

DOE-001 random condition data was not available in the database for direct comparison (DOE-001 used different condition labeling). This comparison is deferred.

---

## Trust Level Assessment

**Trust Level: MEDIUM**

### Trust Justification

**Strengths**:
- Balanced design (n=30 per condition, 150 total) [STAT:n=150]
- Identical seed set across all 5 conditions (strong internal validity)
- KILLCOUNT verified as real kills (not AMMO2 bug)
- Both parametric and non-parametric tests agree on non-significance
- No outliers detected
- Results consistent with DOE-005 and DOE-006 null findings

**Weaknesses**:
- Normality assumption violated (Anderson-Darling p<0.05, Shapiro-Wilk p=0.001)
- Equal variance assumption violated (Levene p=0.039)
- Observed power only 49% for the detected effect size
- Very low kill counts (0-3 per episode) limit discriminability
- Defend_the_center scenario may be too simple for architectural differentiation

**Why Not HIGH**: Both ANOVA assumptions are violated. The observed power is below 80%. While the non-parametric test confirms the null result, the study cannot definitively rule out a small-to-medium effect.

**Why Not LOW**: The non-parametric confirmation, balanced design, identical seeds, and consistency with prior experiments provide robust evidence. The null finding is supported by two independent test approaches and is directionally consistent with DOE-005/006 findings of parameter insensitivity.

---

## Interpretation (Statistical Only)

### Overall Pattern

The data match **Scenario D** from the experiment order: all five architectural configurations produce statistically indistinguishable kill_rate performance. The group means range from 6.74 (full_agent) to 9.08 (L0_only), but this variation is within the noise level of the high-variance kill_rate metric.

### Notable Observations

1. **Random is not inferior**: The random agent (mean=8.54) performs comparably to L0_only (9.08), L0_memory (8.66), and L0_strength (8.26). Only full_agent (6.74) appears lower, but not significantly so. The contrast C1 (random vs all others) is not significant (p=0.656).

2. **Full_agent is the WORST performer**: Paradoxically, the most complex architecture (full_agent = L0 + memory + strength) achieves the lowest mean kill_rate (6.74) and the highest zero-kill rate (20.0%). The contrast C3 (single heuristic vs combined, p=0.051) approaches significance in the direction of REMOVING the combined heuristics improving performance.

3. **L0_only is the BEST performer**: The simplest structured agent (L0_only = pure reflex rules) achieves the highest mean kill_rate (9.08) with the lowest variance (SD=2.75) and zero zero-kill episodes.

4. **Heuristic layers appear counterproductive**: Adding memory dodge (L0_memory) or strength modulation (L0_strength) to L0 rules does not improve kill_rate. Adding BOTH (full_agent) appears to REDUCE kill_rate, though not significantly.

5. **Zero-kill pattern is informative**: L0_only and L0_memory never have zero-kill episodes (0/30), while full_agent has the most (6/30 = 20%). This suggests the combined heuristics occasionally produce suboptimal action sequences (e.g., dodging instead of attacking when an enemy is in the crosshair).

### Consistency with Prior Experiments

This result is consistent with the cumulative evidence:
- DOE-005: No memory/strength parameter effect at [0.7, 0.9]
- DOE-006: No memory/strength parameter effect at [0.3, 0.7]
- DOE-007: No architectural layer effect at all

Together, these three experiments establish that in defend_the_center with the current implementation, **neither the parameters nor the architecture of the heuristic layers contributes to kill_rate performance**. The L0 reflex rules account for all structured behavior, and even random action selection achieves comparable results.

---

## Statistical Markers Summary

| Marker | Value |
|--------|-------|
| [STAT:f] | F(4,145) = 1.5786 |
| [STAT:p] | p = 0.183 |
| [STAT:eta2] | eta^2 = 0.0417 (small) |
| [STAT:n] | n = 150 (30 per group) |
| [STAT:power] | observed power = 0.49 |
| [STAT:effect_size] | Cohen's f = 0.209 (small-to-medium) |
| Kruskal-Wallis | H(4) = 3.340, p = 0.503 |
| C1 (random vs others) | F(1,145) = 0.199, p = 0.656 |
| C2 (L0 vs augmented) | F(1,145) = 2.085, p = 0.151 |
| C3 (single vs combined) | F(1,145) = 3.870, p = 0.051 |
| C4 (memory vs strength) | F(1,145) = 0.161, p = 0.689 |

---

## Recommendations for PI

1. **H-011 Disposition**: The overall ANOVA is not significant. However, the marginal C3 contrast (p=0.051) and the directional pattern (full_agent < L0_only by d=0.685) warrant nuanced interpretation. The PI should decide whether to:
   - REJECT H-011 outright (no significant overall effect)
   - PARTIALLY ADOPT with LOW trust (specific layer contributions are detectable directionally but not statistically)

2. **Scenario Complexity**: The defend_the_center scenario produces only 0-3 kills per episode. This floor/ceiling compression makes it very difficult to detect architectural differences. Testing on scenarios with higher kill counts (e.g., defend_the_line, basic, simpler_basic) would provide better discriminability.

3. **Full Agent Performance Paradox**: The full_agent's worst-in-class performance (mean=6.74, 20% zero-kill rate) suggests the combined memory+strength heuristics may be HARMFUL. The PI should consider investigating whether the heuristics introduce excessive dodging that reduces attack opportunities.

4. **Audit Trail**: All findings trace to H-011 -> DOE-007 -> RPT-007.

---

## Audit Trail

| Document | ID | Status |
|----------|----|--------|
| Hypothesis | H-011 | Active (pending PI disposition) |
| Experiment Order | EXPERIMENT_ORDER_007.md | COMPLETED |
| Experiment Report | This document (RPT-007) | COMPLETE |
| Findings | Pending PI interpretation | |
| Research Log | Entry logged 2026-02-08 | |
