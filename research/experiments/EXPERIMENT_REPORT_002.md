# EXPERIMENT_REPORT_002: DOE-002 Memory x Strength Factorial

**Experiment Order**: DOE-002 (EXPERIMENT_ORDER_002.md)
**Hypotheses**: H-006, H-007, H-008 (HYPOTHESIS_BACKLOG.md)
**Date**: 2026-02-08
**Status**: COMPLETE

## Design Summary

- **Type**: 2^2 Full Factorial with 3 Center Points
- **Factors**: Memory (A) [0.3, 0.7], Strength (B) [0.3, 0.7], Center [0.5, 0.5]
- **Episodes**: 4 factorial cells x 30 = 120, 3 center point batches x 10 = 30, Total = 150
- **Seeds**: seed_i = 1337 + i*17, i=0..29 (identical across all factorial cells)
- **Primary Response**: kill_rate = kills / (survival_time / 60.0)

## Results

### Cell Means (kill_rate, kills/min)

| Memory | Strength | Mean | SD | n |
|--------|----------|------|-----|---|
| 0.3 | 0.3 | 4.24 | 1.58 | 30 |
| 0.3 | 0.7 | 5.99 | 1.55 | 30 |
| 0.7 | 0.3 | 6.70 | 1.58 | 30 |
| 0.7 | 0.7 | 9.65 | 1.53 | 30 |
| 0.5 (center) | 0.5 (center) | 6.67 | 1.59 | 30 |

### Two-Way ANOVA (Type III Sum of Squares)

| Source | SS | df | MS | F | p-value | partial eta2 |
|--------|-----|----|----|---|---------|-------------|
| Memory (A) | 200.661 | 1 | 200.661 | 82.411 | 0.0000 | 0.4154 |
| Strength (B) | 130.717 | 1 | 130.717 | 53.685 | 0.0000 | 0.3164 |
| Memory*Strength (AxB) | 10.884 | 1 | 10.884 | 4.470 | 0.0366 | 0.0371 |
| Residual | 282.446 | 116 | 2.435 | | | |

**Memory (A)**: [STAT:f=F(1,116)=82.411] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.4154] (large effect)

**Strength (B)**: [STAT:f=F(1,116)=53.685] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.3164] (large effect)

**Memory x Strength (AxB)**: [STAT:f=F(1,116)=4.470] [STAT:p=0.0366] [STAT:eta2=partial eta2=0.0371] (small effect) -- significant

[STAT:n=120 factorial episodes + 30 center = 150 total]

### Curvature Test

| Property | Value |
|----------|-------|
| Factorial grand mean | 6.646 |
| Center point mean | 6.669 |
| Difference | -0.023 |
| t-statistic | -0.048 |
| p-value | 0.9614 |
| Conclusion | Linear model adequate |

### Pairwise Comparisons (Cohen's d)

| Comparison | Cohen's d | Mean Diff | 95% CI | Size |
|-----------|-----------|-----------|---------|------|
| Memory effect (low Strength) | [STAT:effect_size=Cohen's d=1.55] | +2.45 | [1.65, 3.25] | large |
| Memory effect (high Strength) | [STAT:effect_size=Cohen's d=2.38] | +3.66 | [2.88, 4.44] | large |
| Strength effect (low Memory) | [STAT:effect_size=Cohen's d=1.12] | +1.75 | [0.95, 2.54] | large |
| Strength effect (high Memory) | [STAT:effect_size=Cohen's d=1.90] | +2.95 | [2.17, 3.74] | large |
| High-High vs Low-Low | [STAT:effect_size=Cohen's d=3.48] | +5.40 | [STAT:ci=95%: 4.62-6.19] | large |

### Diagnostics

#### Normality (Anderson-Darling on residuals)

- A2 statistic: 0.6973
- p-value: 0.0707
- Result: PASS

#### Equal Variance (Levene across 4 factorial cells)

- Levene's W: 0.0125
- p-value: 0.9981
- Result: PASS

#### Outliers (studentized residuals)

- Outliers (|r| > 3): 0
- Result: PASS (no outliers)

#### Independence

- Seed set used: identical across all factorial cells [seed_i = 1337 + i*17]
- No time-dependent confounds (simulated data)
- Result: PASS

#### Overall Diagnostics: PASS

### Trust Assessment

**Trust Level**: MEDIUM

**Criteria**:
- Sample size: [STAT:n=30 per cell]
- Normality: PASS
- Equal variance: PASS
- Primary factor (Memory) p-value: [STAT:p=0.0000]
- Primary effect size: [STAT:eta2=partial eta2=0.4154]

## Conclusions

### H-006: Memory Main Effect on Kill Efficiency

**Status**: SUPPORTED

Memory has a statistically significant main effect on kill_rate [STAT:f=F(1,116)=82.411] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.4154].

At low Strength (0.3), increasing Memory from 0.3 to 0.7 changes kill_rate by +2.45 kills/min [STAT:ci=95%: 1.65-3.25] [STAT:effect_size=Cohen's d=1.55].

At high Strength (0.7), increasing Memory from 0.3 to 0.7 changes kill_rate by +3.66 kills/min [STAT:ci=95%: 2.88-4.44] [STAT:effect_size=Cohen's d=2.38].

### H-007: Strength Main Effect on Kill Efficiency

**Status**: SUPPORTED

Strength has a statistically significant main effect on kill_rate [STAT:f=F(1,116)=53.685] [STAT:p=0.0000] [STAT:eta2=partial eta2=0.3164].

At low Memory (0.3), increasing Strength from 0.3 to 0.7 changes kill_rate by +1.75 kills/min [STAT:ci=95%: 0.95-2.54] [STAT:effect_size=Cohen's d=1.12].

At high Memory (0.7), increasing Strength from 0.3 to 0.7 changes kill_rate by +2.95 kills/min [STAT:ci=95%: 2.17-3.74] [STAT:effect_size=Cohen's d=1.90].

### H-008: Memory x Strength Interaction (Exploratory)

**Status**: SUPPORTED

The interaction between Memory and Strength is significant [STAT:f=F(1,116)=4.470] [STAT:p=0.0366] [STAT:eta2=partial eta2=0.0371].

The interaction is statistically significant, confirming synergy.

The high-high configuration (Memory=0.7, Strength=0.7) outperforms the low-low (Memory=0.3, Strength=0.3) by +5.40 kills/min [STAT:ci=95%: 4.62-6.19] [STAT:effect_size=Cohen's d=3.48].

## Phase Transition Assessment

**Recommend Phase 2 (RSM)**: At least one factor significant with medium+ effect, and interaction suggestive. Design DOE-003 as Central Composite Design around optimal region.

## Next Steps

1. Adopt Memory and Strength findings to FINDINGS.md
2. Design DOE-003 as CCD augmenting DOE-002 factorial points
3. Optimize Memory-Strength combination via response surface

## Data Location

- **DuckDB**: `volumes/data/doe_002.duckdb`
- **Experiment table**: `experiments` (150 rows)
- **Analysis pipeline**: `glue/doe_002_execute.py`

## Audit Trail

| Document | Status |
|----------|--------|
| HYPOTHESIS_BACKLOG.md | H-006, H-007, H-008 defined |
| EXPERIMENT_ORDER_002.md | ORDERED (2026-02-07) |
| EXPERIMENT_REPORT_002.md | This document (COMPLETE) |
| FINDINGS.md | Updated with F-002 |
| RESEARCH_LOG.md | Entry added |

---

**Report generated**: 2026-02-08 09:49:51
**Analysis pipeline**: `glue/doe_002_execute.py`
