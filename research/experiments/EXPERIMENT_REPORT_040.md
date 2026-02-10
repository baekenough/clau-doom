# EXPERIMENT_REPORT_040

## Metadata
- **Experiment ID**: DOE-040
- **Hypothesis**: H-040 (HYPOTHESIS_BACKLOG.md)
- **Experiment Order**: EXPERIMENT_ORDER_040.md
- **Date**: 2026-02-10
- **Analyst**: research-analyst
- **Status**: COMPLETE

## Design Summary
- **Type**: One-way ANOVA, 3-level difficulty mapping
- **Factor**: doom_skill (1=Easy, 3=Hard, 5=Nightmare)
- **Levels**: sk1, sk3, sk5
- **Scenario**: defend_the_line_5action.cfg
- **Strategy**: random_5 (5-action random strategy)
- **Episodes per level**: 50
- **Total episodes**: 150
- **Seed set**: Fixed, identical across all levels

## Research Question
Does DOOM engine difficulty level (doom_skill) map to discriminable performance gradients?

Expected kill rates:
- sk1 (Easy): ~27 kills
- sk3 (Hard): ~15-18 kills
- sk5 (Nightmare): ~6.5 kills

## Data Summary

### sk1 (doom_skill=1, Easy)
- kills: mean=24.76, sd=6.72, median=24.00, range=[13, 36]
- survival_time: mean=42.40s, sd=10.87, median=41.21s, range=[23.91, 60.00]
- kill_rate: mean=35.14 kr, sd=4.41, median=35.38 kr, range=[24.32, 42.94]

### sk3 (doom_skill=3, Hard)
- kills: mean=17.04, sd=5.63, median=17.00, range=[8, 31]
- survival_time: mean=26.67s, sd=8.71, median=26.73s, range=[11.09, 45.17]
- kill_rate: mean=38.78 kr, sd=6.17, median=39.02 kr, range=[23.73, 51.85]

### sk5 (doom_skill=5, Nightmare)
- kills: mean=6.48, sd=2.43, median=7.00, range=[3, 12]
- survival_time: mean=6.19s, sd=2.11, median=5.90s, range=[2.71, 11.40]
- kill_rate: mean=62.49 kr, sd=8.13, median=63.26 kr, range=[37.95, 87.50]

## ANOVA Results

### Kills (Primary Response)

**One-Way ANOVA**:
- [STAT:f=F(2,147)=152.621]
- [STAT:p<0.0000000001]
- [STAT:eta2=0.6750] (large effect)
- [STAT:n=150]

**Kruskal-Wallis** (non-parametric verification):
- [STAT:H(2)=108.518]
- [STAT:p<0.0000000001]

### Survival Time (Secondary Response)

**One-Way ANOVA**:
- [STAT:f=F(2,147)=249.310]
- [STAT:p<0.0000000001]
- [STAT:eta2=0.7723] (very large effect)

## Pairwise Comparisons (Tukey HSD)

### sk1 vs sk3
- Mean difference: +7.72 kills
- [STAT:p<0.000001]
- [STAT:effect_size=Cohen's d=1.258] (large)

### sk1 vs sk5
- Mean difference: +18.28 kills
- [STAT:p<0.000001]
- [STAT:effect_size=Cohen's d=3.653] (very large)

### sk3 vs sk5
- Mean difference: +10.56 kills
- [STAT:p<0.000001]
- [STAT:effect_size=Cohen's d=2.462] (very large)

**Conclusion**: ALL pairwise differences are highly significant. Difficulty levels produce clearly discriminable performance gradients.

## Linear Trend Analysis

**Regression on doom_skill level**:
- Slope: -4.570 kills per difficulty step
- [STAT:r=-0.8183]
- [STAT:R2=0.6696]
- [STAT:p<0.0000000001]

**Interpretation**: Strong negative linear relationship. Each 2-step increase in doom_skill reduces kills by ~9.1 on average.

## Residual Diagnostics

### Normality Test
- Anderson-Darling: [STAT:A2=1.064] vs critical (5%)=0.748
- **Result**: FAIL (p<0.05)
- Residuals deviate from normality

### Equal Variance Test
- Levene test: [STAT:F=18.914], [STAT:p<0.000001]
- **Result**: FAIL
- Variance heterogeneity detected (sk1 has larger variance than sk5)

### Interpretation
- ANOVA assumptions violated (non-normality + unequal variance)
- However: Kruskal-Wallis confirms ANOVA results (p<0.0000000001)
- Effect sizes are enormous (eta2=0.675, Cohen's d up to 3.65)
- Conclusion: ANOVA results are ROBUST despite assumption violations

## Trust Level Assessment

**Trust Level**: HIGH

**Rationale**:
1. **Highly significant results**: p < 0.0000000001 (far below α=0.05)
2. **Very large effect sizes**: eta2=0.675, Cohen's d ranging 1.26–3.65
3. **Robust to assumptions**: Kruskal-Wallis confirms parametric results
4. **Large sample size**: [STAT:n=150] (50 per level)
5. **Convergence**: Parametric and non-parametric tests agree

Despite residual diagnostic failures, the effect is so large and consistent that findings are trustworthy.

## Key Findings

### F-040: DOOM Difficulty Mapping Confirmed
**Statement**: DOOM engine difficulty level (doom_skill) produces strong, discriminable performance gradients.

**Evidence**:
- [STAT:f=F(2,147)=152.621]
- [STAT:p<0.0000000001]
- [STAT:eta2=0.6750]
- [STAT:n=150]
- All pairwise comparisons significant (p<0.000001)

**Observed vs Expected**:
- sk1 (Easy): 24.76 kills (expected ~27) — slightly lower
- sk3 (Hard): 17.04 kills (expected 15-18) — matches expectation
- sk5 (Nightmare): 6.48 kills (expected ~6.5) — perfect match

**Interpretation**: Difficulty scaling works as expected. sk1 slightly underperforms (possibly due to random_5 strategy not exploiting easy enemies optimally), but overall gradient is strong and linear.

### F-041: Survival Time Inversely Proportional to Difficulty
**Statement**: Higher difficulty drastically reduces survival time.

**Evidence**:
- [STAT:f=F(2,147)=249.310]
- [STAT:p<0.0000000001]
- [STAT:eta2=0.7723]

**Survival by difficulty**:
- sk1: 42.40s (71% of max 60s)
- sk3: 26.67s (44% of max)
- sk5: 6.19s (10% of max)

**Interpretation**: Nightmare difficulty is LETHAL. Agents survive only 6s on average. This creates a kill-rate paradox: sk5 has highest kill_rate (62.5 kr) because agents die so quickly, but lowest total kills (6.48).

### F-042: Kill-Rate Paradox Under Time Pressure
**Statement**: Higher difficulty increases kill_rate (kills/minute) but decreases total kills.

**Evidence**:
- sk1: 35.14 kr, 24.76 kills, 42.40s survival
- sk3: 38.78 kr, 17.04 kills, 26.67s survival
- sk5: 62.49 kr, 6.48 kills, 6.19s survival

**Interpretation**: Kill-rate increases with difficulty because agents are under extreme time pressure (must kill before dying). However, total kills decrease because survival time collapses. This suggests kill_rate is NOT a pure performance metric — it conflates lethality with time scarcity.

## Recommendations

### For Future Experiments
1. **Use doom_skill for controlled difficulty variation**: Confirmed as reliable discriminator
2. **Report both kills and survival_time**: They tell complementary stories
3. **Interpret kill_rate cautiously**: High kill_rate can indicate desperation (short survival) rather than dominance

### For DOE Phase Progression
- Difficulty mapping validated: can use doom_skill as a blocking variable or covariate
- Recommended difficulty for agent optimization: **sk3 (Hard)** — balances discrimination (17 kills ± 5.6) with reasonable survival (27s), avoiding floor/ceiling effects

### For Agent Strategy Development
- sk1 (Easy): agents can afford to explore, optimize long-term strategy
- sk3 (Hard): balanced challenge, good for testing robustness
- sk5 (Nightmare): survival-critical, tests extreme decision-making under pressure

## Next Steps

1. **Adopt F-040, F-041, F-042 to FINDINGS.md** (HIGH trust)
2. **Update DOE_CATALOG.md**: Add difficulty mapping as validated blocking variable
3. **Plan DOE-041**: Test agent strategies across difficulty levels (sk1, sk3, sk5) to see if optimal strategy changes with difficulty
4. **Investigate variance heterogeneity**: Why does sk1 have higher variance (sd=6.72) than sk5 (sd=2.43)? Possible explanation: sk1 allows more strategic variation, sk5 forces convergent survival tactics

## Audit Trail
- **Hypothesis**: H-040 (HYPOTHESIS_BACKLOG.md)
- **Experiment Order**: EXPERIMENT_ORDER_040.md
- **Experiment Report**: EXPERIMENT_REPORT_040.md (this document)
- **Next**: Update FINDINGS.md with F-040, F-041, F-042
- **Phase**: 3 (Multi-factor optimization and validation)
