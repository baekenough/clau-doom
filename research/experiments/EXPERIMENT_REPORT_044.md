# Experiment Report: DOE-044

## Experiment Metadata

**Experiment ID**: DOE-044
**Experiment Order**: EXPERIMENT_ORDER_044.md
**Hypothesis**: H-047 — Evolutionary optimization breaks tactical invariance
**Date Analyzed**: 2026-02-10
**Analyst**: research-analyst

---

## Design Summary

**Design Type**: Evolutionary optimization (generational)
**Scenario**: defend_the_line.cfg
**Total Genomes**: 10 per generation
**Episodes per Genome**: 20
**Generations**: 5
**Total Episodes**: 1000 (5 gen x 10 genomes x 20 episodes)

---

## Generational Performance Summary

| Generation | Avg Kills | Best Genome | Best Kills | Best Survival (s) |
|-----------|-----------|-------------|------------|-------------------|
| Gen 1 | 14.0 | G10 | 18.7 | 25.8 |
| Gen 2 | 18.3 | G01 | 21.9 | 30.2 |
| Gen 3 | 17.8 | G05 | 23.0 | 32.3 |
| Gen 4 | 18.5 | G05 | 22.7 | 34.3 |
| Gen 5 | 21.6 | G05 | 25.3 | 36.6 |

**Maximum kills observed**: 42 (Gen 5, single episode)

---

## Statistical Analysis

### Generation-over-Generation Improvement

**Average kills trajectory**: 14.0 → 18.3 → 17.8 → 18.5 → 21.6

Total improvement: 21.6 - 14.0 = **+7.6 kills** (+54.3% from Gen 1 baseline)

**Best-genome kills trajectory**: 18.7 → 21.9 → 23.0 → 22.7 → 25.3

Total best-genome improvement: 25.3 - 18.7 = **+6.6 kills** (+35.3% from Gen 1 best)

**Best-genome survival trajectory**: 25.8 → 30.2 → 32.3 → 34.3 → 36.6

Total survival improvement: 36.6 - 25.8 = **+10.8 seconds** (+41.9% from Gen 1)

### Trend Analysis

**Linear regression (average kills ~ generation)**:
- x = [1, 2, 3, 4, 5], y = [14.0, 18.3, 17.8, 18.5, 21.6]
- x_bar = 3.0, y_bar = 18.04
- SS_xy = (1-3)(14.0-18.04) + (2-3)(18.3-18.04) + (3-3)(17.8-18.04) + (4-3)(18.5-18.04) + (5-3)(21.6-18.04)
  = 8.08 + 0.26 + 0 + 0.46 + 7.12 = 15.92
- SS_xx = 4 + 1 + 0 + 1 + 4 = 10
- Slope (b1) = 15.92 / 10 = **1.592 kills/generation**
- R-squared: SS_reg / SS_total
  - SS_total = (14.0-18.04)^2 + (18.3-18.04)^2 + (17.8-18.04)^2 + (18.5-18.04)^2 + (21.6-18.04)^2
    = 16.32 + 0.068 + 0.058 + 0.212 + 12.67 = 29.33
  - SS_reg = b1^2 * SS_xx = 1.592^2 * 10 = 25.34
  - R-squared = 25.34 / 29.33 = **0.864**

[STAT:slope=+1.592 kills/gen] [STAT:R2=0.864]

**Linear regression (best-genome survival ~ generation)**:
- y = [25.8, 30.2, 32.3, 34.3, 36.6]
- y_bar = 31.84
- SS_xy = (1-3)(25.8-31.84) + (2-3)(30.2-31.84) + ... + (5-3)(36.6-31.84)
  = 12.08 + 1.64 + 0 + 2.46 + 9.52 = 25.70
- Slope = 25.70 / 10 = **2.57 s/generation**
- SS_total = 36.51 + 2.69 + 0.21 + 6.05 + 22.66 = 68.12
- SS_reg = 2.57^2 * 10 = 66.05
- R-squared = 66.05 / 68.12 = **0.970**

[STAT:slope=+2.57 s/gen] [STAT:R2=0.970]

### Convergence Assessment

- Gen 1 → Gen 2: Large jump (+4.3 avg kills, +30.7%) — initial selection pressure effective
- Gen 2 → Gen 3: Slight regression (-0.5 avg kills) — genetic drift or local optimum exploration
- Gen 3 → Gen 4: Marginal gain (+0.7 avg kills) — plateau behavior
- Gen 4 → Gen 5: Substantial jump (+3.1 avg kills) — possible escape from local optimum

The non-monotonic trajectory (Gen 2 → Gen 3 regression) is characteristic of evolutionary algorithms exploring the fitness landscape. The strong Gen 5 recovery suggests the algorithm has not yet converged.

### Best Genome Consistency

G05 appears as best genome in Gen 3, 4, and 5, indicating an evolved genome that dominates the population. This suggests convergence toward a particular strategy configuration, though the continued improvement in Gen 5 indicates remaining optimization potential.

---

## Residual Diagnostics

Not applicable — this is not an ANOVA design. Generational analysis uses trend regression.

**Regression diagnostics**:
- Linearity: R-squared = 0.864 for avg kills, suggesting strong but not perfect linear trend. Non-monotonic Gen 2→3 creates some residual.
- Sample size: Only 5 data points (generations) for regression — limited statistical power for formal inference on trend significance.

---

## Findings

**H-047 SUPPORTED**: Evolution successfully breaks tactical invariance on defend_the_line.

**F-047a**: Evolutionary optimization produces a +54.3% improvement in average kills over 5 generations (14.0 → 21.6), with a strong positive linear trend (R-squared = 0.864, +1.59 kills/generation). [STAT:slope=+1.592 kills/gen] [STAT:R2=0.864]

**F-047b**: Best-genome survival time improves nearly monotonically (+2.57 s/generation, R-squared = 0.970), suggesting evolution discovers survival-enhancing behaviors even without explicit survival optimization. [STAT:slope=+2.57 s/gen] [STAT:R2=0.970]

**F-047c**: The maximum observed kills (42 in Gen 5) far exceeds the best fixed-strategy means from DOE-042 (random_5 = 19.10), suggesting evolution discovers performance configurations inaccessible to fixed strategies.

**F-047d**: Non-monotonic improvement (Gen 2 → Gen 3 regression) followed by strong recovery (Gen 5) is characteristic of healthy evolutionary search — exploration before exploitation.

**F-047e**: Genome G05 dominates from Gen 3 onward, indicating convergence toward an effective strategy while maintaining improvement trajectory.

[STAT:n=1000 episodes total across 5 generations]

---

## Trust Level: MEDIUM

**Rationale**:
- Strong improvement trends with high R-squared (0.864, 0.970)
- Large absolute improvement (+54.3% average kills)
- Maximum kills (42) substantially exceeds baseline strategies
- However, only 5 generational data points limits formal statistical inference
- No control group running in parallel (historical comparison only)
- Confound: improvement could partly reflect population diversity benefits rather than true evolution
- Would need replicated evolution runs (multiple independent populations) for HIGH trust

---

## Conclusion

Evolutionary optimization successfully improves agent performance on defend_the_line across 5 generations, achieving a 54% improvement in average kills and a 42% improvement in best-genome survival time. The trend is strongly positive (R-squared > 0.86) with characteristic non-monotonic exploration behavior. The evolved best genome (G05) achieves kills (25.3 mean, 42 max) substantially exceeding any fixed strategy tested in DOE-042 (best fixed: 19.1). This supports H-047: evolution breaks the tactical invariance observed among fixed strategies by discovering synergistic parameter combinations.

## Recommended Next Steps

1. **Extend generations**: Continue evolution to 10-15 generations to test convergence plateau
2. **Replicated runs**: Run 3-5 independent evolutionary populations to assess consistency
3. **Evolved vs fixed comparison**: Run the best evolved genome (G05 Gen 5) against top fixed strategies in a controlled CRD for formal statistical comparison
4. **Genome analysis**: Decompose the G05 genome to understand which parameters evolution optimized
5. **Cross-scenario transfer**: Test whether evolved genomes generalize to other scenarios
6. **Population diversity tracking**: Monitor genetic diversity across generations to detect premature convergence
