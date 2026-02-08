# EXPERIMENT_REPORT_009: Memory × Strength Factorial on defend_the_line

## Metadata
- **Experiment ID**: DOE-009
- **Hypothesis**: H-013
- **Experiment Order**: EXPERIMENT_ORDER_009.md
- **Date**: 2026-02-08

## Executive Summary

DOE-009 tested whether memory_weight and strength_weight have significant main effects or interaction on kill_rate in defend_the_line. **No significant effects were found.** This is the first real VizDoom validation of H-006/H-007/H-008, which were previously adopted from mock (synthetic) data in DOE-002. The mock-data findings do NOT replicate.

## Data Summary

| Condition | n | kills mean±SD | kill_rate mean±SD | survival mean±SD |
|-----------|---|---------------|-------------------|------------------|
| m0.1_s0.1 | 30 | 12.47±4.47 | 40.84±6.76 | 18.74±6.59 |
| m0.1_s0.5 | 30 | 14.37±4.38 | 43.69±6.81 | 20.06±6.18 |
| m0.1_s0.9 | 30 | 12.60±4.01 | 42.35±5.63 | 18.25±5.98 |
| m0.5_s0.1 | 30 | 13.03±4.57 | 41.35±6.66 | 19.26±6.75 |
| m0.5_s0.5 | 30 | 14.40±5.19 | 43.58±8.11 | 20.05±7.00 |
| m0.5_s0.9 | 30 | 14.07±3.95 | 43.97±4.05 | 19.51±5.60 |
| m0.9_s0.1 | 30 | 13.50±4.56 | 42.46±7.85 | 19.24±5.63 |
| m0.9_s0.5 | 30 | 14.07±4.52 | 43.03±6.30 | 19.86±5.96 |
| m0.9_s0.9 | 30 | 13.40±4.67 | 43.34±5.81 | 18.75±6.47 |

### Main Effect Means (kill_rate)
| memory_weight | Mean | SD | n |
|---------------|------|----|---|
| 0.1 | 42.29 | 6.46 | 90 |
| 0.5 | 42.96 | 6.53 | 90 |
| 0.9 | 42.94 | 6.65 | 90 |

| strength_weight | Mean | SD | n |
|-----------------|------|----|---|
| 0.1 | 41.55 | 7.06 | 90 |
| 0.5 | 43.43 | 7.04 | 90 |
| 0.9 | 43.22 | 5.21 | 90 |

## 2-Way ANOVA Results (kill_rate)

| Source | SS | df | F | p-value | partial η² |
|--------|----|----|---|---------|------------|
| memory_weight | 26.24 | 2 | 0.306 | 0.736 | 0.002 |
| strength_weight | 191.39 | 2 | 2.235 | 0.109 | 0.017 |
| memory × strength | 62.47 | 4 | 0.365 | 0.834 | 0.006 |
| Residual | 11177.20 | 261 | | | |

[STAT:f=F(2,261)=0.306] [STAT:p=0.736] — memory_weight: NOT SIGNIFICANT
[STAT:f=F(2,261)=2.235] [STAT:p=0.109] — strength_weight: NOT SIGNIFICANT
[STAT:f=F(4,261)=0.365] [STAT:p=0.834] — interaction: NOT SIGNIFICANT
[STAT:n=270] [STAT:eta2=partial η²<0.02 for all]

### kills (secondary)
[STAT:f=F(2,261)=0.558] [STAT:p=0.573] — memory: NS
[STAT:f=F(2,261)=1.896] [STAT:p=0.152] — strength: NS

### survival_time (secondary)
[STAT:f=F(2,261)=0.381] [STAT:p=0.683] — memory: NS
[STAT:f=F(2,261)=1.211] [STAT:p=0.299] — strength: NS

### Non-Parametric Confirmation
Kruskal-Wallis: H(8)=7.342, p=0.500. Confirms null result.

## Residual Diagnostics

| Test | Statistic | p-value | Result |
|------|-----------|---------|--------|
| Shapiro-Wilk | W=0.991 | p=0.098 | PASS |
| D'Agostino | stat=1.972 | p=0.373 | PASS |
| Levene | stat=1.400 | p=0.196 | PASS |

All assumptions satisfied. The null result is not due to diagnostic failures.

## Interpretation

### H-013: REJECTED
Neither memory_weight nor strength_weight has a significant effect on kill_rate in defend_the_line. The interaction is also non-significant. All effect sizes are negligible (partial η² < 0.02).

### Mock Data Invalidation
H-006, H-007, H-008 (adopted from DOE-002 mock data) are NOT REPLICATED with real VizDoom gameplay:
- H-006 claimed memory explains 41.5% of variance → real data shows 0.2% (η²=0.002)
- H-007 claimed strength explains 31.6% of variance → real data shows 1.7% (η²=0.017)
- H-008 claimed significant interaction → real data shows none (η²=0.006)

### Why Parameters Don't Matter
DOE-008 showed that architecture LEVEL matters (L0-only vs heuristic agents, p=0.000555), but DOE-009 shows that WITHIN the full_agent architecture, varying memory_weight and strength_weight has negligible effect. This suggests:

1. **The heuristic functions are too weak**: The memory dodge and strength attack probability modifications produce tiny behavioral changes that VizDoom gameplay noise overwhelms
2. **L0 emergency rules dominate**: The health<20 dodge-left rule fires frequently, overriding the stochastic heuristics regardless of weight settings
3. **The action space is too coarse**: With only 3 actions (TURN_LEFT, TURN_RIGHT, ATTACK), the stochastic modulation has limited room to express different strategies

### Power Analysis
With n=30/cell and observed effect sizes, statistical power for detecting the observed effects:
- memory (η²=0.002): power ≈ 0.10 — but effect is genuinely tiny
- strength (η²=0.017): power ≈ 0.50 — might reach significance with n=60/cell
- Even with doubled sample size, practical significance would be questionable (~2 kr difference)

## Trust Level: HIGH (for the null result)
- All diagnostics PASS
- n=30 per cell (adequate for detecting medium effects)
- Non-parametric confirms
- Effect sizes are tiny, not just non-significant

## Findings

### F-013: Memory Weight Has No Effect on Kill Rate (Real Data)
[STAT:f=F(2,261)=0.306] [STAT:p=0.736] [STAT:eta2=0.002] [STAT:n=270]
Trust: HIGH. Invalidates mock-based F-005 (H-006).

### F-014: Strength Weight Has Marginal-to-No Effect on Kill Rate (Real Data)
[STAT:f=F(2,261)=2.235] [STAT:p=0.109] [STAT:eta2=0.017] [STAT:n=270]
Trust: HIGH. Borderline — strength=0.1 (41.55 kr) vs strength=0.5 (43.43 kr) shows a ~2 kr trend but not significant. Invalidates mock-based F-006 (H-007).

### F-015: No Memory × Strength Interaction (Real Data)
[STAT:f=F(4,261)=0.365] [STAT:p=0.834] [STAT:eta2=0.006] [STAT:n=270]
Trust: HIGH. Invalidates mock-based F-007 (H-008).

## Recommended Next Steps

1. **Abandon memory/strength parameter tuning** — continuous parameters within FullAgentAction do not meaningfully affect performance
2. **Focus on architectural changes** — DOE-008 showed architecture LEVEL matters; design new architectures rather than tuning existing parameters
3. **Fix L0 rules for defend_the_line** — the dodge-left rule is counterproductive (DOE-008 F-010); redesign the rule set
4. **Consider larger action modifications** — instead of stochastic probability modulation, test fundamentally different strategies (e.g., positional awareness, enemy tracking, aim assist)
