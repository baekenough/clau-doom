---
name: statistical-analysis
description: Statistical analysis methods including ANOVA, residual diagnostics, post-hoc tests, and power analysis
user-invocable: false
---

# Statistical Analysis Skill

Core statistical methods for analyzing DOE experiment results: ANOVA decomposition, assumption validation, post-hoc comparisons, effect size estimation, and power analysis.

## ANOVA (Analysis of Variance)

### One-Way ANOVA

Tests whether means differ across groups defined by a single factor.

```
H0: mu_1 = mu_2 = ... = mu_k  (all group means equal)
H1: At least one mean differs

Model: Y_ij = mu + alpha_i + epsilon_ij
  where alpha_i = effect of level i
        epsilon_ij ~ N(0, sigma^2)
```

### Two-Way ANOVA

Tests main effects and interaction for two factors.

```
Model: Y_ijk = mu + alpha_i + beta_j + (alpha*beta)_ij + epsilon_ijk

alpha_i      = main effect of factor A
beta_j       = main effect of factor B
(alpha*beta) = interaction effect of A and B
```

### Multi-Factor ANOVA

For 2^k factorial designs with k factors:

```
Model (2^3 example):
Y = mu + A + B + C + AB + AC + BC + ABC + epsilon

Sources of variation:
  A, B, C           = main effects
  AB, AC, BC        = 2-factor interactions
  ABC               = 3-factor interaction
  epsilon            = residual error
```

### Sum of Squares (SS) Decomposition

```
SS_Total = SS_Model + SS_Error

SS_Total = sum((y_ij - y_bar)^2)
SS_A     = n_b * sum((y_bar_i - y_bar)^2)   for factor A
SS_Error = SS_Total - SS_A - SS_B - SS_AB - ...

For balanced designs:
  SS_A = (sum of contrast for A)^2 / (n * 2^(k-1))
```

### F-Test

```
F = MS_effect / MS_error
  = (SS_effect / df_effect) / (SS_error / df_error)

df_effect = (number of levels - 1) for main effects
df_interaction = df_A * df_B for two-factor interaction
df_error = N - total model df - 1

p-value = P(F(df_effect, df_error) > F_observed)
```

Significance threshold: p < 0.05 (standard), p < 0.01 (stringent).

### ANOVA Table Format

```
Source          |   SS    |  df  |   MS    |    F    |   p
----------------|---------|------|---------|---------|--------
A               |  45.23  |   1  |  45.23  |  12.34  | 0.002
B               |  23.11  |   1  |  23.11  |   6.30  | 0.021
C               |   8.45  |   1  |   8.45  |   2.31  | 0.145
A*B             |  31.67  |   1  |  31.67  |   8.64  | 0.008
A*C             |   2.12  |   1  |   2.12  |   0.58  | 0.456
B*C             |   5.89  |   1  |   5.89  |   1.61  | 0.220
A*B*C           |   1.23  |   1  |   1.23  |   0.34  | 0.570
Error           |  58.67  |  16  |   3.67  |         |
----------------|---------|------|---------|---------|--------
Total           | 176.37  |  23  |         |         |
```

### Interpreting Results

- Significant main effect (p < 0.05): Factor has real impact on response
- Significant interaction: Effect of one factor depends on level of another
- If interaction is significant, interpret main effects with caution (conditional on other factor levels)
- Non-significant 3-way and higher interactions can often be pooled into error

## Main Effect and Interaction Plots

### Main Effect Plot

For each factor, plot mean response at each level:

```
Factor A:
  Level -1: mean = 12.3
  Level +1: mean = 18.7
  Effect of A = 18.7 - 12.3 = 6.4

  If line is steep: large effect
  If line is flat: small/no effect
```

### Interaction Plot

Plot mean response for each combination of two factors:

```
A*B Interaction:
  A=-1, B=-1: mean = 10.2
  A=-1, B=+1: mean = 14.5
  A=+1, B=-1: mean = 16.8
  A=+1, B=+1: mean = 22.1

  Parallel lines: no interaction
  Non-parallel lines: interaction present
  Crossing lines: strong interaction
```

## Residual Diagnostics

### ANOVA Assumptions

1. **Normality**: Residuals are normally distributed
2. **Equal Variance (Homoscedasticity)**: Variance is constant across groups
3. **Independence**: Observations are independent

### Normality Tests

**Anderson-Darling Test**:
```
H0: Residuals follow normal distribution
H1: Residuals do not follow normal distribution

A^2 = -N - (1/N) * sum((2i-1) * [ln(F(z_i)) + ln(1 - F(z_(N+1-i)))])

Reject H0 if A^2 > critical value (depends on N)
p < 0.05 → evidence against normality
```

**Shapiro-Wilk Test**:
```
W = (sum(a_i * x_(i))^2) / (sum((x_i - x_bar)^2))

Range: 0 to 1 (1 = perfectly normal)
p < 0.05 → evidence against normality
```

Preferred for small samples (N < 50). Anderson-Darling preferred for larger samples.

### Normal Probability Plot (Q-Q Plot)

```
1. Order residuals: e_(1) <= e_(2) <= ... <= e_(N)
2. Compute expected quantiles: z_i = Phi^-1((i - 0.375)/(N + 0.25))
3. Plot e_(i) vs z_i
4. Points should fall on straight line if normal
```

### Equal Variance Tests

**Levene's Test** (robust to non-normality):
```
H0: sigma_1^2 = sigma_2^2 = ... = sigma_k^2
Test statistic uses absolute deviations from group medians
p < 0.05 → evidence of unequal variances
```

**Bartlett's Test** (assumes normality):
```
H0: All group variances are equal
More powerful than Levene if normality holds
Sensitive to non-normality (use Levene instead if unsure)
```

### Independence Assessment

**Run Order Plot**:
```
Plot residuals vs run order
Look for: trends, cycles, shifts
Pattern present → time-related systematic effect
```

**Durbin-Watson Test**:
```
d = sum((e_t - e_{t-1})^2) / sum(e_t^2)

d near 2: no autocorrelation
d near 0: positive autocorrelation
d near 4: negative autocorrelation
```

### Residual Plots Summary

| Plot | Purpose | Warning Sign |
|------|---------|-------------|
| Residuals vs Fitted | Equal variance | Funnel/fan shape |
| Normal Q-Q | Normality | S-curve or outliers |
| Residuals vs Run Order | Independence | Trend or pattern |
| Residuals vs Factor | Factor-specific issues | Non-random pattern |

## Post-Hoc Tests

When ANOVA is significant, determine which specific groups differ.

### Tukey HSD (Honestly Significant Difference)

```
HSD = q_alpha * sqrt(MS_error / n)

q_alpha = studentized range statistic at alpha, k groups, df_error
n = observations per group (balanced design)

Groups differ if: |mean_i - mean_j| > HSD
```

Properties:
- Controls family-wise error rate at alpha
- All pairwise comparisons simultaneously
- Requires balanced design (equal n per group)
- Use Tukey-Kramer for unbalanced designs

### Bonferroni Correction

```
Adjusted alpha = alpha / m
where m = number of pairwise comparisons = k(k-1)/2

Compare each p-value against adjusted alpha
More conservative than Tukey for many comparisons
```

Use when:
- Small number of planned comparisons
- Unbalanced designs
- Non-parametric tests

## Effect Sizes

### Partial Eta-Squared

```
partial_eta^2 = SS_effect / (SS_effect + SS_error)
```

| Value | Interpretation |
|-------|---------------|
| 0.01  | Small |
| 0.06  | Medium |
| 0.14  | Large |

### Cohen's d

```
d = (mean_1 - mean_2) / s_pooled

s_pooled = sqrt(((n1-1)*s1^2 + (n2-1)*s2^2) / (n1+n2-2))
```

| d | Interpretation |
|---|---------------|
| 0.2 | Small |
| 0.5 | Medium |
| 0.8 | Large |

### Omega-Squared

Less biased than eta-squared, especially for small samples:

```
omega^2 = (SS_effect - df_effect * MS_error) / (SS_total + MS_error)
```

Preferred for reporting in publications.

## Power Analysis

### Power Definition

```
Power = 1 - beta = P(reject H0 | H0 is false)

beta = P(Type II error) = P(fail to reject H0 | H0 is false)

Target: Power >= 0.80 (standard), >= 0.90 (stringent)
```

### Sample Size Determination

For one-way ANOVA:
```
N_per_group = (z_alpha/2 + z_beta)^2 * 2 * sigma^2 / delta^2

delta = minimum detectable difference
sigma = within-group standard deviation
```

For factorial designs:
```
Replicates needed per design point:
n = 2 * (z_alpha/2 + z_beta)^2 * sigma^2 / (delta^2 / 4)

(divide delta by 4 because factorial effects are differences of averages)
```

### Retrospective Power

After experiment, calculate achieved power:
```
Given: observed effect size, N, alpha
Compute: power for detecting that effect

If power < 0.80: insufficient evidence, need more replicates
If power > 0.80: adequate sensitivity
```

### Power Curve

Plot power vs effect size for given N and alpha:
```
For each effect_size in range:
  power = 1 - P(F < F_critical | non-centrality = N*effect^2/sigma^2)
```

Use to determine: minimum detectable effect for current design.

## Box-Cox Transformation

When normality assumption is violated, transform the response:

```
y_transformed = (y^lambda - 1) / lambda    if lambda != 0
              = ln(y)                        if lambda = 0
```

Common transformations:

| lambda | Transformation |
|--------|---------------|
| -1 | Reciprocal (1/y) |
| -0.5 | Reciprocal square root |
| 0 | Natural log |
| 0.5 | Square root |
| 1 | No transformation |
| 2 | Square |

Procedure:
1. Fit ANOVA with untransformed data
2. Check residual diagnostics
3. If normality violated, find optimal lambda via maximum likelihood
4. Re-fit ANOVA with transformed response
5. Re-check diagnostics

## Non-Parametric Alternatives

### Kruskal-Wallis Test

Non-parametric alternative to one-way ANOVA.

```
H0: All group distributions are identical
H1: At least one group differs

Test statistic:
H = (12/(N(N+1))) * sum(R_i^2/n_i) - 3(N+1)

R_i = sum of ranks in group i
n_i = number of observations in group i
N = total observations
```

Use when:
- Normality assumption severely violated
- Box-Cox transformation insufficient
- Ordinal response variable
- Small sample sizes with non-normal data

Post-hoc: Dunn's test with Bonferroni correction.

## Analysis Workflow

```
1. Compute ANOVA table
   |
2. Check p-values for all effects
   |
3. Residual diagnostics
   |-- Normality (Anderson-Darling / Shapiro-Wilk)
   |-- Equal variance (Levene)
   |-- Independence (run order plot)
   |
4. If assumptions violated:
   |-- Try Box-Cox transformation
   |-- If still violated: Kruskal-Wallis
   |
5. If assumptions hold:
   |-- Post-hoc tests (Tukey HSD)
   |-- Effect sizes (partial eta^2, omega^2)
   |-- Power analysis
   |
6. Generate EXPERIMENT_REPORT
   |-- ANOVA table
   |-- Significant effects
   |-- Effect sizes
   |-- Residual diagnostic plots (described)
   |-- Power achieved
   |-- Recommendations for next experiment
```

## DuckDB Integration

### ANOVA Computation in SQL

```sql
-- Group means
SELECT factor_a, AVG(response) as group_mean, COUNT(*) as n
FROM experiment_runs
WHERE experiment_id = ?
GROUP BY factor_a;

-- Grand mean
SELECT AVG(response) as grand_mean FROM experiment_runs WHERE experiment_id = ?;

-- SS computation
SELECT
  SUM(n * (group_mean - grand_mean)^2) as SS_between,
  SUM((response - group_mean)^2) as SS_within
FROM ...;
```

For complex ANOVA (multi-factor with interactions): use Python statsmodels or R via Bash, reading data from DuckDB.

## Reporting Format

EXPERIMENT_REPORT structure:

```markdown
# Experiment Report: EXP-001

## Design Summary
- Type: 2^3 Full Factorial
- Factors: retreat_threshold, ammo_conservation, exploration_priority
- Replicates: 3 per design point
- Total runs: 33 (including center points)

## ANOVA Results
[ANOVA table]

## Significant Effects
- Factor A (retreat_threshold): F(1,16) = 12.34, p = 0.002, partial eta^2 = 0.44
- Interaction A*B: F(1,16) = 8.64, p = 0.008, partial eta^2 = 0.35

## Residual Diagnostics
- Normality: Anderson-Darling A^2 = 0.34, p = 0.48 (PASS)
- Equal variance: Levene F = 1.23, p = 0.31 (PASS)
- Independence: No pattern in run order plot (PASS)

## Effect Sizes
[Table of effects with omega-squared]

## Power Analysis
- Achieved power: 0.87 for observed effect size
- Minimum detectable effect: 0.5 sigma at 80% power

## Recommendations
- retreat_threshold and ammo_conservation are significant and interact
- exploration_priority is not significant (can be dropped)
- Center point curvature test: F = 3.45, p = 0.07 (marginal)
- Recommend: augment to RSM if curvature becomes significant with more data
```
