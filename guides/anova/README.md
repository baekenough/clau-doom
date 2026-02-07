# ANOVA Reference Guide

Reference documentation for Analysis of Variance in clau-doom experiments.

## Key Resources

- Montgomery, D.C. (2017). *Design and Analysis of Experiments*, Ch. 3-5, 13-14. Wiley.
- NIST/SEMATECH e-Handbook: https://www.itl.nist.gov/div898/handbook/prc/section4/prc43.htm
- statsmodels ANOVA: https://www.statsmodels.org/stable/anova.html

## clau-doom Context

ANOVA is the primary analysis method for DOE experiments. After running a factorial or fractional factorial design, ANOVA decomposes total variation into components attributable to each factor, interaction, and error.

## ANOVA Table

### One-Way ANOVA

```
Source     | SS          | df      | MS          | F           | p-value
-----------|-------------|---------|-------------|-------------|--------
Treatment  | SS_treat    | a - 1   | SS_treat/df | MS_treat/MSE| P(F > f)
Error      | SS_error    | N - a   | SS_error/df |             |
Total      | SS_total    | N - 1   |             |             |
```

Where: a = number of treatment levels, N = total observations.

### Two-Way ANOVA with Interaction

```
Source     | SS          | df          | MS          | F           | p-value
-----------|-------------|-------------|-------------|-------------|--------
Factor A   | SS_A        | a - 1       | SS_A/df_A   | MS_A/MSE    | P(F > f)
Factor B   | SS_B        | b - 1       | SS_B/df_B   | MS_B/MSE    | P(F > f)
A x B      | SS_AB       | (a-1)(b-1)  | SS_AB/df_AB | MS_AB/MSE   | P(F > f)
Error      | SS_E        | ab(n-1)     | SS_E/df_E   |             |
Total      | SS_T        | abn - 1     |             |             |
```

Where: a = levels of A, b = levels of B, n = replicates per cell.

### Three-Factor ANOVA (2^3 Factorial)

```
Source     | SS    | df | MS   | F     | p-value
-----------|-------|--  |------|-------|--------
A          | SS_A  | 1  | MS_A | F_A   | p_A
B          | SS_B  | 1  | MS_B | F_B   | p_B
C          | SS_C  | 1  | MS_C | F_C   | p_C
A x B      | SS_AB | 1  | MS_AB| F_AB  | p_AB
A x C      | SS_AC | 1  | MS_AC| F_AC  | p_AC
B x C      | SS_BC | 1  | MS_BC| F_BC  | p_BC
A x B x C  | SS_ABC| 1  | MS_ABC|F_ABC | p_ABC
Error      | SS_E  |8(n-1)|MS_E|       |
Total      | SS_T  |8n-1|      |       |
```

## Sum of Squares Decomposition

### Fundamental Identity

```
SS_total = SS_treatment + SS_error

For factorial:
SS_total = SS_A + SS_B + SS_AB + SS_error

For blocked factorial:
SS_total = SS_A + SS_B + SS_AB + SS_block + SS_error
```

### Computation

```
SS_total = sum((y_ij - y_bar)^2)

SS_A = bn * sum((y_bar_i. - y_bar)^2)      # Factor A
SS_B = an * sum((y_bar_.j - y_bar)^2)      # Factor B
SS_AB = SS_total - SS_A - SS_B - SS_error   # Interaction (by subtraction)

SS_error = sum(sum((y_ijk - y_bar_ij)^2))   # Within-cell variation
```

## F-test

### Hypothesis

```
H0: All treatment means are equal (mu_1 = mu_2 = ... = mu_a)
H1: At least one mean differs
```

### Test Statistic

```
F = MS_treatment / MS_error

Where:
  MS_treatment = SS_treatment / df_treatment
  MS_error = SS_error / df_error

F follows F-distribution with (df_treatment, df_error) degrees of freedom.
```

### Decision Rule

```
If F > F_critical(alpha, df1, df2): Reject H0 (factor is significant)
Equivalently: If p-value < alpha: Reject H0

clau-doom default: alpha = 0.05
Screening phase: alpha = 0.10 (more liberal for factor discovery)
```

## Residual Diagnostics

Residuals: e_ij = y_ij - y_hat_ij (observed - fitted)

### Assumption Checks (ALL REQUIRED)

| Assumption | Diagnostic | Test |
|------------|-----------|------|
| Normality | Normal probability plot, histogram | Anderson-Darling |
| Equal variance | Residuals vs fitted plot | Levene test |
| Independence | Residuals vs run order | Durbin-Watson |

### Normal Probability Plot

Plot ordered residuals against expected normal quantiles. Points should fall approximately on a straight line.

```
Procedure:
1. Sort residuals: e_(1) <= e_(2) <= ... <= e_(n)
2. Compute quantiles: q_i = Phi_inverse((i - 0.375) / (n + 0.25))
3. Plot: (q_i, e_(i))
4. Assess linearity (deviations indicate non-normality)
```

### Residuals vs Fitted Values

Plot residuals (y-axis) against fitted values (x-axis). Look for:
- **Funnel shape**: Variance increases with mean (need transformation)
- **Curved pattern**: Model misspecification (need higher-order terms)
- **Random scatter**: Assumptions satisfied

### Residuals vs Run Order

Plot residuals in the order experiments were conducted. Look for:
- **Trend**: Time-related systematic effect
- **Cycling**: Periodic disturbance
- **Random scatter**: Independence satisfied

## Normality Testing

### Anderson-Darling Test

```
H0: Data comes from a normal distribution
H1: Data does not come from a normal distribution

Test statistic: A^2 = -n - (1/n) * sum((2i-1) * [ln(F(y_i)) + ln(1-F(y_(n+1-i)))])

Decision:
  p-value >= 0.05: Fail to reject H0 (normality assumed)
  p-value < 0.05: Reject H0 (non-normality detected, consider transformation)
```

### Levene Test for Equal Variance

```
H0: All group variances are equal
H1: At least one group variance differs

Procedure:
1. Compute z_ij = |y_ij - median_i| (deviations from group medians)
2. Perform one-way ANOVA on z_ij values

Decision:
  p-value >= 0.05: Equal variance assumption holds
  p-value < 0.05: Unequal variance (consider Welch ANOVA or transformation)
```

## Post-hoc Comparisons

### Tukey HSD (Honestly Significant Difference)

After a significant F-test, identify which specific pairs of means differ.

```
HSD = q_alpha(a, df_error) * sqrt(MS_error / n)

Where:
  q = studentized range statistic
  a = number of treatment levels
  n = observations per treatment

Compare |y_bar_i - y_bar_j| to HSD:
  If |diff| > HSD: Pair is significantly different
  If |diff| <= HSD: No significant difference
```

### Confidence Intervals for Differences

```
(y_bar_i - y_bar_j) +/- q_alpha(a, df_error) * sqrt(MS_error / n)

If interval excludes 0: Significant difference
```

## Effect Size

### Partial Eta-Squared

```
partial_eta^2 = SS_effect / (SS_effect + SS_error)

Interpretation:
  Small:  partial_eta^2 ~ 0.01
  Medium: partial_eta^2 ~ 0.06
  Large:  partial_eta^2 ~ 0.14
```

### Cohen's f

```
f = sqrt(partial_eta^2 / (1 - partial_eta^2))

Interpretation:
  Small:  f ~ 0.10
  Medium: f ~ 0.25
  Large:  f ~ 0.40
```

### clau-doom Practical Significance

```
Even if p < 0.05, check practical significance:
  - Effect of 0.5 kills/episode: Statistically significant but trivially small
  - Effect of 3.0 kills/episode: Both statistically and practically significant

PI decision rule: Factor must have BOTH statistical significance (p < 0.05)
AND practical significance (effect > 1.0 kills/episode or partial_eta^2 > 0.06).
```

## Power Analysis

### Given: alpha, effect size, n -> compute 1-beta

```
Parameters:
  alpha: Significance level (typically 0.05)
  delta: True difference in means
  sigma: Standard deviation (estimated from prior data)
  n: Sample size per group
  k: Number of groups

Noncentrality parameter:
  lambda = n * sum(tau_i^2) / sigma^2

Power = P(F > F_critical | lambda)
  = 1 - beta
```

### Sample Size Determination

```
Given desired power (1-beta = 0.80), alpha = 0.05, and estimated effect size:

For one-way ANOVA with k groups:
  n = (z_alpha/2 + z_beta)^2 * 2 * sigma^2 / delta^2  (per group, approximate)

clau-doom usage:
  - After Phase 0 OFAT, estimate sigma from episode variance
  - Determine minimum episodes per DOE run for 80% power
  - If power < 0.80 with 30 episodes: increase to 50
  - PI reviews power analysis before committing to DOE matrix
```

### Power Curve

```
Plot: Power (y-axis) vs Effect Size (x-axis) for different sample sizes

Useful for:
  - Justifying sample sizes to reviewers (paper)
  - Deciding whether non-significant results are due to small effect or small n
  - PI planning how many episodes per run
```

## Box-Cox Transformation

When residuals violate normality or equal variance, transform the response.

```
y_transformed = (y^lambda - 1) / lambda    if lambda != 0
              = ln(y)                       if lambda = 0

Common lambda values:
  lambda = -1:   1/y  (reciprocal)
  lambda = -0.5: 1/sqrt(y)
  lambda = 0:    ln(y)
  lambda = 0.5:  sqrt(y)
  lambda = 1:    y (no transform)
  lambda = 2:    y^2

Procedure:
1. Fit model, check residual diagnostics
2. If non-normal or heteroscedastic: compute Box-Cox profile
3. Find lambda that maximizes log-likelihood
4. Transform response, refit model
5. Re-check diagnostics
```

## Non-parametric Alternative: Kruskal-Wallis

When ANOVA assumptions cannot be satisfied even after transformation.

```
H0: All k populations have identical distributions
H1: At least one population differs

Test statistic:
  H = (12 / (N(N+1))) * sum(R_i^2 / n_i) - 3(N+1)

Where:
  R_i = sum of ranks for group i
  n_i = sample size of group i
  N = total sample size

H ~ chi-squared with k-1 degrees of freedom

Decision:
  p-value < alpha: Reject H0 (groups differ)

Post-hoc: Dunn test with Bonferroni correction for pairwise comparisons.
```

### When to Use Kruskal-Wallis in clau-doom

```
Use when:
  - Anderson-Darling rejects normality (p < 0.05) AND Box-Cox fails
  - Small sample sizes (< 10 episodes per run)
  - Ordinal response variable (rank-based metrics)
  - Severe outliers that resist transformation

Report both parametric (ANOVA) and non-parametric results in paper
for robustness of conclusions.
```

## clau-doom ANOVA Workflow

```
1. Run DOE matrix (factorial, fractional, CCD, etc.)
2. Collect response data (kill_rate, survival_time, etc.)
3. Fit linear model: response ~ factor_A * factor_B * ...
4. Generate ANOVA table (Type II SS for unbalanced, Type III for interaction focus)
5. Check residual diagnostics:
   a. Normal probability plot + Anderson-Darling
   b. Residuals vs fitted + Levene test
   c. Residuals vs run order + Durbin-Watson
6. If assumptions violated:
   a. Try Box-Cox transformation
   b. If still violated: Kruskal-Wallis
7. Report significant factors (p < 0.05) with effect sizes
8. Run Tukey HSD for pairwise comparisons
9. Compute power for non-significant factors
10. PI interprets: practical significance + next experiment design
```
