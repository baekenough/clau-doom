# Experiment Report: DOE-042

## Experiment Metadata

**Experiment ID**: DOE-042
**Experiment Order**: EXPERIMENT_ORDER_042.md
**Hypothesis**: H-045 — Strategy rankings shift at intermediate difficulty (doom_skill=3)
**Date Analyzed**: 2026-02-10
**Analyst**: research-analyst

---

## Design Summary

**Design Type**: One-way completely randomized design (CRD), 5 levels
**Scenario**: defend_the_line.cfg (doom_skill=3)
**Total Episodes**: 150 (30 per strategy)
**Response Variable**: kills (primary)

### Factor

| Factor | Type | Levels |
|--------|------|--------|
| action_strategy | Categorical | random_5, dodge_burst_3, ar_50, survival_burst, attack_raw |

---

## Descriptive Statistics

### kills (primary response)

| Strategy | n | Mean | SD |
|----------|---|------|-----|
| random_5 | 30 | 19.10 | 5.66 |
| dodge_burst_3 | 30 | 18.20 | 7.43 |
| ar_50 | 30 | 17.03 | 5.62 |
| survival_burst | 30 | 16.40 | 7.05 |
| attack_raw | 30 | 10.60 | 3.05 |

### survival_time (seconds)

| Strategy | n | Mean | SD |
|----------|---|------|-----|
| random_5 | 30 | 28.22 | 9.55 |
| dodge_burst_3 | 30 | 28.17 | 12.42 |
| ar_50 | 30 | 26.16 | 9.79 |
| survival_burst | 30 | 26.11 | 12.25 |
| attack_raw | 30 | 14.77 | 4.72 |

Grand Mean (kills): 16.266

---

## Statistical Analysis

### One-Way ANOVA (kills)

**Computation (manual from summary statistics):**

SS_between = sum(n_i * (mean_i - grand_mean)^2)
= 30 * [(19.10 - 16.266)^2 + (18.20 - 16.266)^2 + (17.03 - 16.266)^2 + (16.40 - 16.266)^2 + (10.60 - 16.266)^2]
= 30 * [8.028 + 3.743 + 0.584 + 0.018 + 32.112]
= 30 * 44.484 = **1334.52**

SS_within = sum((n_i - 1) * sd_i^2)
= 29 * [32.036 + 55.205 + 31.584 + 49.703 + 9.303]
= 29 * 177.830 = **5157.07**

| Source | SS | df | MS | F | p-value | eta-squared |
|--------|------|-----|--------|--------|---------|-------------|
| Strategy | 1334.52 | 4 | 333.63 | 9.381 | < 0.001 | 0.206 |
| Error | 5157.07 | 145 | 35.566 | | | |
| Total | 6491.59 | 149 | | | | |

[STAT:f=F(4,145)=9.381] [STAT:p<0.001] [STAT:eta2=eta-squared=0.206]

**p-value estimation**: F(4,145) = 9.381 is far beyond the critical value F_0.001(4,145) ~ 4.85. Thus p < 0.0001.

### Effect Size

- eta-squared = 0.206 (large effect; >0.14 threshold)
- The strategy factor accounts for approximately 20.6% of total variance in kills.

### Post-Hoc Pairwise Interpretation

The effect is predominantly driven by **attack_raw** (mean=10.60) being far below all other strategies (means 16.40-19.10). The top four strategies are relatively clustered within a 2.7-kill range.

Estimated Tukey HSD critical difference (approximate):
q_0.05(5,145) ~ 3.93, SE = sqrt(MS_within / n) = sqrt(35.566/30) = 1.089
HSD = 3.93 * 1.089 = 4.28

Pairwise differences vs attack_raw:
- random_5 - attack_raw = 8.50 > 4.28 (significant)
- dodge_burst_3 - attack_raw = 7.60 > 4.28 (significant)
- ar_50 - attack_raw = 6.43 > 4.28 (significant)
- survival_burst - attack_raw = 5.80 > 4.28 (significant)

Pairwise among top 4:
- random_5 - survival_burst = 2.70 < 4.28 (not significant)
- random_5 - ar_50 = 2.07 < 4.28 (not significant)
- random_5 - dodge_burst_3 = 0.90 < 4.28 (not significant)
- dodge_burst_3 - survival_burst = 1.80 < 4.28 (not significant)

---

## Residual Diagnostics

### Normality Assessment
SD ratios across groups range from 3.05 to 7.43. The large SD differences suggest potential non-normality, but with n=30 per group, ANOVA is robust to moderate departures (Central Limit Theorem). Assessment: **MARGINAL** — recommend non-parametric verification.

### Equal Variance (Homoscedasticity)
SD ratio (max/min) = 7.43 / 3.05 = 2.44. This exceeds the 2:1 rule-of-thumb for concern. attack_raw has notably lower variance (SD=3.05) compared to dodge_burst_3 (SD=7.43). Assessment: **CAUTION** — variance heterogeneity detected. Welch ANOVA recommended as robustness check.

### Independence
Assuming randomized seed assignment across conditions. No run-order effects expected. Assessment: **PASS**

---

## Findings

**F-010 Extension**: attack_raw (pure attack, no movement) is significantly worse than all movement-inclusive strategies at doom_skill=3 [STAT:p<0.001] [STAT:f=F(4,145)=9.381] [STAT:eta2=eta-squared=0.206].

**F-045a**: The four movement-inclusive strategies (random_5, dodge_burst_3, ar_50, survival_burst) are statistically indistinguishable at doom_skill=3, with all pairwise differences below the Tukey HSD threshold.

**F-045b**: Strategy rankings at doom_skill=3 broadly replicate doom_skill=1 patterns: movement is the critical discriminator, not specific tactical design.

Sample size: [STAT:n=150 (30 per condition)]

---

## Trust Level: MEDIUM

**Rationale**:
- Significant result (p < 0.001) with large effect size (eta-squared = 0.206)
- Variance heterogeneity (SD ratio 2.44) reduces trust from HIGH to MEDIUM
- Welch ANOVA and/or Kruskal-Wallis confirmation recommended
- n=30 per group provides adequate power for this effect size

---

## Conclusion

At intermediate difficulty (doom_skill=3), the dominant finding replicates earlier results: movement is essential. attack_raw (no movement) performs dramatically worse than all strategies incorporating lateral movement. Among the four movement strategies, no significant differentiation exists, confirming the "tactical invariance" pattern — at this difficulty level, *how* you move matters less than *that* you move.

## Recommended Next Steps

1. Confirm with Welch ANOVA to address variance heterogeneity
2. Compare doom_skill=3 rankings directly with doom_skill=1 rankings (DOE-045 addresses this)
3. Investigate why attack_raw variance is so much lower (floor/ceiling effect?)
4. Consider doom_skill=5 to test if strategy differentiation emerges under extreme pressure
