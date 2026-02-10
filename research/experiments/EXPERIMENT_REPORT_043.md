# Experiment Report: DOE-043

## Experiment Metadata

**Experiment ID**: DOE-043
**Experiment Order**: EXPERIMENT_ORDER_043.md
**Hypothesis**: H-046 — Hybrid strategies outperform random_7 on deadly_corridor
**Date Analyzed**: 2026-02-10
**Analyst**: research-analyst

---

## Design Summary

**Design Type**: One-way completely randomized design (CRD), 5 levels
**Scenario**: deadly_corridor.cfg (7-action space)
**Total Episodes**: 150 (30 per strategy)
**Response Variable**: kills (primary, zero-inflated)

### Factor

| Factor | Type | Levels |
|--------|------|--------|
| action_strategy | Categorical | random_7, burst_advance_7, forward_biased_7, strafe_dodge_7, adaptive_aggression_7 |

---

## Descriptive Statistics

### kills (primary response)

| Strategy | n | Mean | SD | Zero-kill % |
|----------|---|------|-----|-------------|
| random_7 | 30 | 0.47 | 0.63 | ~53% |
| burst_advance_7 | 30 | 0.30 | 0.53 | ~70% |
| forward_biased_7 | 30 | 0.20 | 0.48 | ~80% |
| strafe_dodge_7 | 30 | 0.13 | 0.35 | ~87% |
| adaptive_aggression_7 | 30 | 0.10 | 0.31 | ~90% |

### survival_time (seconds)

| Strategy | n | Mean | SD |
|----------|---|------|-----|
| random_7 | 30 | 6.34 | 4.58 |
| strafe_dodge_7 | 30 | 3.98 | 1.33 |
| forward_biased_7 | 30 | 3.62 | 1.12 |
| adaptive_aggression_7 | 30 | 3.53 | 1.00 |
| burst_advance_7 | 30 | 3.41 | 0.90 |

Grand Mean (kills): 0.240

---

## Statistical Analysis

### One-Way ANOVA (kills)

**Computation (manual from summary statistics):**

SS_between = sum(n_i * (mean_i - grand_mean)^2)
= 30 * [(0.47 - 0.24)^2 + (0.30 - 0.24)^2 + (0.20 - 0.24)^2 + (0.13 - 0.24)^2 + (0.10 - 0.24)^2]
= 30 * [0.0529 + 0.0036 + 0.0016 + 0.0121 + 0.0196]
= 30 * 0.0898 = **2.694**

SS_within = sum((n_i - 1) * sd_i^2)
= 29 * [0.3969 + 0.2809 + 0.2304 + 0.1225 + 0.0961]
= 29 * 1.1268 = **32.677**

| Source | SS | df | MS | F | p-value | eta-squared |
|--------|------|-----|--------|--------|---------|-------------|
| Strategy | 2.694 | 4 | 0.6735 | 2.989 | ~0.021 | 0.076 |
| Error | 32.677 | 145 | 0.22536 | | | |
| Total | 35.371 | 149 | | | | |

[STAT:f=F(4,145)=2.989] [STAT:p=0.021] [STAT:eta2=eta-squared=0.076]

**p-value estimation**: F_0.05(4,145) ~ 2.43, F_0.01(4,145) ~ 3.44. Our F=2.989 falls between these, so 0.01 < p < 0.05, approximately p ~ 0.021.

### Effect Size

- eta-squared = 0.076 (medium effect; between 0.06 and 0.14)
- The strategy factor accounts for approximately 7.6% of total variance in kills.

### Critical Caveat: Zero-Inflation and Non-Normality

This data is severely zero-inflated. All strategies have majority zero-kill episodes (53-90%). The ANOVA assumptions of normality and continuous response are violated. The parametric ANOVA result should be interpreted with extreme caution.

### Non-Parametric Alternative: Kruskal-Wallis Consideration

Given the zero-inflated count data:
- Kruskal-Wallis H test is the appropriate primary analysis
- Most observations are 0 or 1, creating many tied ranks
- With heavily tied ranks, even Kruskal-Wallis has reduced power
- A permutation test or Poisson/negative binomial regression would be more appropriate for this data structure

### Survival Time Analysis (Secondary)

Random_7 survives notably longer (mean=6.34s, SD=4.58) vs all hybrid strategies (3.41-3.98s). This suggests random_7's advantage in kills may be partially attributable to longer survival enabling more kill opportunities. The high SD of random_7 survival (4.58 vs 0.90-1.33 for hybrids) suggests highly variable performance — some episodes achieve extended survival while others die quickly.

---

## Residual Diagnostics

### Normality Assessment
**FAIL** — Data is discrete count data (0, 1, 2) with massive zero-inflation (53-90%). Residuals cannot be normally distributed. Shapiro-Wilk would reject normality (p < 0.001).

### Equal Variance (Homoscedasticity)
SD ratio (max/min) = 0.63 / 0.31 = 2.03. Borderline by 2:1 rule. More critically, the variance is intrinsically tied to the mean (count data property). Assessment: **FAIL** (mean-variance coupling).

### Independence
Assuming randomized seed assignment. Assessment: **PASS**

---

## Findings

**H-046 REJECTED**: Hybrid strategies do NOT outperform random_7 on deadly_corridor. In fact, random_7 achieves the highest mean kills (0.47) while all engineered strategies perform worse (0.10-0.30).

**F-046a**: On deadly_corridor, random_7 outperforms all four hybrid strategies in both kills and survival time. This extends the "random is competitive" finding to the deadly_corridor scenario.

**F-046b**: deadly_corridor produces extremely low kill counts (0-2 range) with heavy zero-inflation, making it a poor discriminating scenario for strategy comparison. Similar to defend_the_center, the scenario imposes a low ceiling on measurable performance.

**F-046c**: Hybrid strategies (burst_advance_7, forward_biased_7, strafe_dodge_7, adaptive_aggression_7) produce lower survival times than random_7, suggesting that deterministic movement patterns are more easily exploited by enemies in corridor environments.

[STAT:n=150 (30 per condition)]

---

## Trust Level: LOW

**Rationale**:
- Parametric ANOVA marginally significant (p ~ 0.021), but assumptions severely violated
- Zero-inflated count data: normality assumption fails
- Small effect size (eta-squared = 0.076)
- Mean-variance coupling invalidates homoscedasticity assumption
- Non-parametric or GLM analysis needed for valid inference
- deadly_corridor provides minimal discrimination (0-2 kill range)
- Trust cannot exceed LOW until proper count-data model applied

---

## Conclusion

deadly_corridor proves to be an extremely challenging scenario where all strategies achieve near-zero kills. The hypothesis that hybrid strategies outperform random_7 is rejected — random_7 actually performs best, likely because random movement is harder for enemies to predict in the constrained corridor environment. The scenario has a severe floor effect similar to defend_the_center, producing insufficient variance for meaningful strategy discrimination. Proper analysis requires zero-inflated Poisson regression or similar count-data models.

## Recommended Next Steps

1. Re-analyze with zero-inflated Poisson (ZIP) or negative binomial regression
2. Consider survival_time as primary DV instead of kills (more continuous, more variance)
3. Classify deadly_corridor as a non-discriminating scenario alongside defend_the_center
4. Focus future experiments on defend_the_line (proven discrimination) or doom_skill-modulated scenarios
5. If deadly_corridor is retained, increase episodes to n=100+ per condition for adequate power with count data
