# EXPERIMENT_REPORT_023: Cross-Difficulty Strategy Robustness

## Metadata

| Field | Value |
|-------|-------|
| Experiment ID | DOE-023 |
| Hypothesis | H-026 |
| Design | 3×4 full factorial |
| Factors | doom_skill (3 levels) × strategy (4 levels) |
| Episodes per cell | 30 |
| Total episodes | 360 |
| Scenario | defend_the_line.cfg |
| Seed formula | seed_i = 25001 + i × 101, i=0..29 |
| Date executed | 2026-02-09 |
| Runtime | 46.4 seconds |

## Research Question

Do strategy rankings generalize across game difficulty levels? Specifically, does the burst_3 advantage (established in DOE-008 through DOE-020) persist when doom_skill varies from Easy (1) to Nightmare (5)?

## Experimental Design

### Factor 1: doom_skill (Game Difficulty)

| Level | doom_skill | Label | Description |
|-------|-----------|-------|-------------|
| 1 | 1 | Easy | Slow enemies, low damage |
| 2 | 3 | Normal | Default difficulty |
| 3 | 5 | Nightmare | Fast enemies, high damage, respawning |

### Factor 2: Strategy (Action Selection)

| Level | Strategy | action_type | Description |
|-------|----------|-------------|-------------|
| 1 | burst_3 | burst_3 | Fire 3 consecutive shots, pattern turn |
| 2 | random | random | Uniform random action selection |
| 3 | adaptive_kill | adaptive_kill | Kill-triggered strategy switching |
| 4 | L0_only | rule_only | Pure rule-based (L0 heuristic only) |

### Design Matrix

12 conditions (3 skill × 4 strategy), 30 episodes each, fully randomized run order.

## Descriptive Statistics

### Cell Means

| Condition | n | Kills (M±SD) | Kill Rate (M±SD) | Survival (M±SD) |
|-----------|---|-------------|-------------------|-----------------|
| skill_easy_L0_only | 30 | 15.63±3.13 | 35.40±2.58 | 26.63±5.67 |
| skill_easy_adaptive_kill | 30 | 22.93±5.94 | 40.12±5.05 | 34.64±9.41 |
| skill_easy_burst_3 | 30 | 19.73±5.60 | 37.28±6.13 | 32.06±9.13 |
| skill_easy_random | 30 | 20.47±6.89 | 36.86±4.58 | 33.22±10.39 |
| skill_normal_L0_only | 30 | 9.57±2.21 | 39.20±4.59 | 14.84±3.79 |
| skill_normal_adaptive_kill | 30 | 13.43±4.74 | 46.06±5.37 | 17.61±6.35 |
| skill_normal_burst_3 | 30 | 12.17±4.31 | 41.03±6.35 | 17.84±5.68 |
| skill_normal_random | 30 | 13.73±3.81 | 44.02±6.31 | 19.07±5.77 |
| skill_nightmare_L0_only | 30 | 3.57±0.73 | 55.30±6.56 | 3.87±0.62 |
| skill_nightmare_adaptive_kill | 30 | 3.87±0.73 | 59.78±8.42 | 3.88±0.53 |
| skill_nightmare_burst_3 | 30 | 4.77±1.45 | 64.32±10.39 | 4.44±1.10 |
| skill_nightmare_random | 30 | 4.97±1.92 | 63.44±12.35 | 4.65±1.32 |

### Factor Marginals

| doom_skill | n | Kills | Kill Rate | Survival |
|-----------|---|-------|-----------|----------|
| Easy (1) | 120 | 19.69 | 37.41 | 31.64 |
| Normal (3) | 120 | 12.23 | 42.58 | 17.34 |
| Nightmare (5) | 120 | 4.29 | 60.71 | 4.21 |

| Strategy | n | Kills | Kill Rate | Survival |
|----------|---|-------|-----------|----------|
| L0_only | 90 | 9.59 | 43.30 | 15.11 |
| burst_3 | 90 | 12.22 | 47.54 | 18.11 |
| random | 90 | 13.06 | 48.11 | 18.98 |
| adaptive_kill | 90 | 13.41 | 48.65 | 18.71 |

## ANOVA Results

### Response: kills

| Source | SS | df | F | p | partial η² |
|--------|------|-----|---------|---------|-----------|
| doom_skill | 14233.96 | 2 | 446.73 | 7.77e-97 | 0.720 |
| strategy | 805.41 | 3 | 16.85 | 3.04e-10 | 0.127 |
| doom_skill × strategy | 387.80 | 6 | 4.06 | 6.02e-04 | 0.065 |
| Residual | 5544.10 | 348 | | | |

[STAT:f=F(2,348)=446.73] [STAT:p=7.77e-97] [STAT:eta2=partial η²=0.720] (doom_skill)
[STAT:f=F(3,348)=16.85] [STAT:p=3.04e-10] [STAT:eta2=partial η²=0.127] (strategy)
[STAT:f=F(6,348)=4.06] [STAT:p=6.02e-04] [STAT:eta2=partial η²=0.065] (interaction)
[STAT:n=360] [STAT:power=very high given massive effects]

### Response: kill_rate

| Source | SS | df | F | p | partial η² |
|--------|------|-----|---------|---------|-----------|
| doom_skill | 35911.93 | 2 | 362.04 | 9.45e-86 | 0.675 |
| strategy | 1610.52 | 3 | 10.82 | 8.14e-07 | 0.085 |
| doom_skill × strategy | 1097.31 | 6 | 3.69 | 1.45e-03 | 0.060 |
| Residual | 17259.72 | 348 | | | |

### Response: survival_time

| Source | SS | df | F | p | partial η² |
|--------|------|-----|---------|---------|-----------|
| doom_skill | 45159.00 | 2 | 621.53 | 1.38e-115 | 0.781 |
| strategy | 856.02 | 3 | 7.85 | 4.38e-05 | 0.063 |
| doom_skill × strategy | 548.15 | 6 | 2.51 | 2.14e-02 | 0.042 |
| Residual | 12642.42 | 348 | | | |

## Residual Diagnostics

### kills

| Test | Statistic | p-value | Verdict |
|------|-----------|---------|---------|
| Shapiro-Wilk | W=0.9643 | <0.001 | FAIL (mild non-normality) |
| D'Agostino-Pearson | 25.52 | <0.001 | FAIL |
| Levene | 14.98 | <0.001 | FAIL (heteroscedasticity) |
| Skewness | 0.44 | — | Moderate positive |
| Kurtosis | 1.48 | — | Leptokurtic |

### kill_rate

| Test | Statistic | p-value | Verdict |
|------|-----------|---------|---------|
| Shapiro-Wilk | W=0.9879 | 0.004 | FAIL (slight) |
| D'Agostino-Pearson | 8.26 | 0.016 | FAIL (marginal) |
| Levene | 7.82 | <0.001 | FAIL |
| Skewness | 0.09 | — | Negligible |
| Kurtosis | 0.92 | — | Slight leptokurtic |

### Robustness Assessment

Residual assumptions violated due to heteroscedasticity across doom_skill levels (Easy has much larger variance than Nightmare). However:
- **Large balanced design** (n=30/cell) provides robustness via CLT
- **Kruskal-Wallis confirms**: doom_skill H=274.10 (p=3.01e-60), strategy H=11.33 (p=0.010)
- **All effects confirmed by both parametric and non-parametric tests**
- **Trust level**: MEDIUM-HIGH (assumptions violated but effects are overwhelmingly large)

## Post-Hoc Comparisons (Tukey HSD)

### doom_skill marginal (kills)

| Comparison | Mean Diff | p-adj | Significant |
|------------|-----------|-------|-------------|
| Easy vs Normal | +7.47 | <0.001 | YES |
| Easy vs Nightmare | +15.40 | <0.001 | YES |
| Normal vs Nightmare | +7.93 | <0.001 | YES |

All doom_skill levels significantly different from each other.

### Strategy marginal (kills)

| Comparison | Mean Diff | p-adj | Significant |
|------------|-----------|-------|-------------|
| adaptive_kill vs L0_only | +3.82 | 0.004 | YES |
| random vs L0_only | +3.47 | 0.012 | YES |
| burst_3 vs L0_only | +2.63 | 0.090 | NO (marginal) |
| adaptive_kill vs burst_3 | +1.19 | 0.714 | NO |
| random vs burst_3 | +0.83 | 0.880 | NO |
| adaptive_kill vs random | +0.36 | 0.989 | NO |

### Simple Effects: Strategy within each doom_skill level (kills)

| doom_skill | F(3,116) | p | η² | Strategy Ranking |
|-----------|----------|---------|------|-----------------|
| Easy (1) | 8.90 | 0.000023 | 0.187 | adaptive > random > burst_3 > L0_only |
| Normal (3) | 7.16 | 0.000188 | 0.156 | random > adaptive > burst_3 > L0_only |
| Nightmare (5) | 8.08 | 0.000062 | 0.173 | random > burst_3 > adaptive > L0_only |

### Tukey HSD within Easy (kills)

| Comparison | Mean Diff | p-adj | Significant |
|------------|-----------|-------|-------------|
| adaptive_kill vs L0_only | +7.30 | <0.001 | YES |
| random vs L0_only | +4.83 | 0.006 | YES |
| burst_3 vs L0_only | +4.10 | 0.026 | YES |
| adaptive_kill vs burst_3 | +3.20 | 0.122 | NO |
| adaptive_kill vs random | +2.47 | 0.320 | NO |
| burst_3 vs random | -0.73 | 0.957 | NO |

### Tukey HSD within Normal (kills)

| Comparison | Mean Diff | p-adj | Significant |
|------------|-----------|-------|-------------|
| random vs L0_only | +4.17 | <0.001 | YES |
| adaptive_kill vs L0_only | +3.87 | 0.001 | YES |
| burst_3 vs L0_only | +2.60 | 0.052 | NO (marginal) |
| random vs burst_3 | +1.57 | 0.404 | NO |
| adaptive_kill vs burst_3 | +1.27 | 0.588 | NO |
| random vs adaptive_kill | +0.30 | 0.991 | NO |

### Tukey HSD within Nightmare (kills)

| Comparison | Mean Diff | p-adj | Significant |
|------------|-----------|-------|-------------|
| random vs L0_only | +1.40 | <0.001 | YES |
| burst_3 vs L0_only | +1.20 | 0.003 | YES |
| random vs adaptive_kill | +1.10 | 0.008 | YES |
| burst_3 vs adaptive_kill | +0.90 | 0.044 | YES |
| adaptive_kill vs L0_only | +0.30 | 0.812 | NO |
| random vs burst_3 | +0.20 | 0.935 | NO |

## Key Interaction Pattern

### Strategy Ranking Changes Across Difficulty

| Rank | Easy | Normal | Nightmare |
|------|------|--------|-----------|
| 1st | adaptive_kill (22.9) | random (13.7) | random (5.0) |
| 2nd | random (20.5) | adaptive_kill (13.4) | burst_3 (4.8) |
| 3rd | burst_3 (19.7) | burst_3 (12.2) | adaptive_kill (3.9) |
| 4th | L0_only (15.6) | L0_only (9.6) | L0_only (3.6) |

### Effect Compression

| doom_skill | Best−Worst Spread | Relative Effect |
|-----------|-------------------|-----------------|
| Easy (1) | 7.30 kills | 47% of Easy L0 baseline |
| Normal (3) | 4.17 kills | 44% of Normal L0 baseline |
| Nightmare (5) | 1.40 kills | 39% of Nightmare L0 baseline |

Strategy effect shrinks from 7.30 kills at Easy to 1.40 kills at Nightmare — effect compression ratio of 5.2×.

### adaptive_kill Environment Sensitivity

adaptive_kill shows the most dramatic ranking change:
- Easy: BEST (rank 1, 22.9 kills)
- Normal: 2nd (rank 2, 13.4 kills)
- Nightmare: 3rd (rank 3, 3.9 kills, NOT significantly different from L0_only)

Mechanism: adaptive_kill's kill-triggered switching requires kills to trigger adaptation. At Nightmare difficulty, survival time is only ~3.9 seconds — insufficient time for the adaptive mechanism to observe kills and switch strategies. The agent dies before adaptation can occur.

### Kill Rate Paradox

Kill_rate INCREASES with difficulty: Easy 37.4/min → Normal 42.6/min → Nightmare 60.7/min.
This is because survival_time drops faster than kills. At Nightmare, agents die very quickly but kill efficiently in the brief time alive. Kill_rate is an unreliable metric for cross-difficulty comparison.

## Findings

### F-052: doom_skill Is the Dominant Factor

doom_skill explains 72% of variance in kills [STAT:eta2=partial η²=0.720], 68% in kill_rate, and 78% in survival_time. Game difficulty overwhelms all strategy differences. [STAT:f=F(2,348)=446.73] [STAT:p=7.77e-97]

### F-053: Significant Strategy × Difficulty Interaction

Strategy ranking changes across difficulty levels [STAT:f=F(6,348)=4.06] [STAT:p=6.02e-04] [STAT:eta2=partial η²=0.065]. adaptive_kill drops from rank 1 (Easy) to rank 3 (Nightmare). random is the most robust strategy.

### F-054: Effect Compression Under Difficulty

Strategy effect shrinks from 7.30 kills at Easy to 1.40 kills at Nightmare (5.2× compression). Higher difficulty compresses all agents toward a low-performance floor, reducing strategy differentiation.

### F-055: adaptive_kill Is Environment-Sensitive

adaptive_kill requires sufficient survival time for its kill-triggered switching to activate. At Nightmare (survival ~3.9s), it degrades to L0_only-level performance (not significantly different, p=0.812).

### F-056: L0_only Universally Worst Across All Difficulty Levels

L0_only ranks last in all 3 difficulty conditions, extending the DOE-008 finding (F-010) to a broader range of game environments. Strategy effect is significant within every difficulty level (all simple-effects p<0.001).

## H-026 Disposition

**PARTIALLY SUPPORTED**

- L0_only consistently worst: CONFIRMED across all difficulty levels
- burst_3 maintains ranking: NOT CONFIRMED — burst_3 drops from rank 2 (DOE-008 Normal) to rank 3 (Easy), but rises to rank 2 at Nightmare. Its ranking is unstable.
- Strategy rankings generalize: PARTIALLY — the L0_only deficit generalizes, but the ordering among non-L0 strategies changes significantly with difficulty
- Key insight: Strategy rankings are difficulty-dependent, not universal

## Trust Level

**MEDIUM-HIGH**

- Massive sample size (360 episodes, 30/cell)
- All effects confirmed by both parametric ANOVA and non-parametric Kruskal-Wallis
- Residual assumption violations (non-normality, heteroscedasticity) mitigated by large balanced design
- Interaction effect confirmed with clear mechanistic explanation (adaptive_kill time dependency)
- Downgraded from HIGH due to residual violations

## Recommendations

1. **For deployment**: Use random or burst_3 as they are most robust across difficulty levels
2. **For Easy environments**: adaptive_kill provides best raw performance
3. **For harsh environments**: Avoid adaptive strategies that require observation time; simple reactive strategies (random, burst_3) are more robust
4. **Next experiment**: Consider testing adaptive strategies with faster switching thresholds to improve Nightmare performance
