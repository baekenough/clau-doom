# EXPERIMENT_REPORT_008: Action Architecture Ablation on defend_the_line

## Metadata
- **Experiment ID**: DOE-008
- **Hypothesis**: H-012
- **Experiment Order**: EXPERIMENT_ORDER_008.md
- **Date**: 2026-02-08

## Executive Summary

DOE-008 is the first experiment in the clau-doom program to produce statistically significant results. The defend_the_line scenario successfully discriminates between action architectures. L0-only (pure rule-based) performs significantly worse than all other architectures including random.

## Data Summary

| Condition | n | kills mean+/-SD | kill_rate mean+/-SD | survival mean+/-SD |
|-----------|---|-----------------|---------------------|--------------------|
| random | 30 | 14.30+/-4.37 | 42.51+/-6.42 | 20.46+/-6.41 |
| L0_only | 30 | 9.37+/-2.92 | 36.78+/-4.87 | 15.42+/-4.91 |
| L0_memory | 30 | 14.37+/-4.44 | 43.35+/-6.59 | 20.21+/-6.68 |
| L0_strength | 30 | 14.93+/-5.11 | 42.22+/-5.90 | 21.51+/-7.98 |
| full_agent | 30 | 11.90+/-3.77 | 42.39+/-7.51 | 17.13+/-5.62 |

## ANOVA Results

### kill_rate (Primary)
[STAT:f=F(4,145)=5.256] [STAT:p=0.000555] [STAT:eta2=0.127] [STAT:n=150]
Result: SIGNIFICANT

### kills (Secondary)
[STAT:f=F(4,145)=9.275] [STAT:p=0.000001] [STAT:eta2=0.204]
Result: HIGHLY SIGNIFICANT

### survival_time (Secondary)
[STAT:f=F(4,145)=4.799] [STAT:p=0.001153]
Result: SIGNIFICANT

### Non-Parametric Confirmation
Kruskal-Wallis: H(4)=20.158, p=0.000465. Confirms parametric results.

## Residual Diagnostics

| Test | Statistic | p-value | Result |
|------|-----------|---------|--------|
| Shapiro-Wilk | W=0.996 | p=0.931 | PASS |
| D'Agostino | stat=1.763 | p=0.414 | PASS |
| Levene | stat=1.558 | p=0.189 | PASS |

All assumptions satisfied.

## Tukey HSD Post-Hoc (kill_rate)

| Comparison | Mean Diff | p-adj | Reject |
|-----------|-----------|-------|--------|
| L0_memory vs L0_only | +6.56 | 0.0009 | Yes |
| L0_strength vs L0_only | +5.44 | 0.0095 | Yes |
| full_agent vs L0_only | +5.61 | 0.0068 | Yes |
| random vs L0_only | +5.72 | 0.0053 | Yes |
| All other pairs | <1.13 | >0.95 | No |

L0_only differs from ALL others. Remaining four are indistinguishable.

## Planned Contrasts (kills)

| Contrast | t | p | Sig |
|----------|---|---|-----|
| C1: random vs structured | 1.767 | 0.079 | No |
| C2: rule_only vs heuristic | -4.856 | <0.0001 | Yes |
| C3: single-heuristic vs full | 2.759 | 0.007 | Yes |
| C4: memory vs strength | -0.458 | 0.649 | No |

## Interpretation

L0-only performs worst because dodge-left rule at health<20 wastes time. Random performs well due to unpredictable movement. Full agent underperforms single-heuristic agents due to heuristic layer interference (excessive dodging from stacked rules).

## DOE-007 vs DOE-008 Comparison

| Metric | DOE-007 (center) | DOE-008 (line) |
|--------|-------------------|----------------|
| Kills range | 0-3 | 4-26 |
| F-stat | 1.579 | 5.256 |
| p-value | 0.183 | 0.000555 |
| eta2 | 0.042 | 0.127 |
| Diagnostics | FAIL | ALL PASS |

H-012 CONFIRMED.

## Trust Level: HIGH

## Findings
- F-010: L0-only significantly worse than all others [STAT:p=0.000555]
- F-011: Full agent underperforms single-heuristic agents [STAT:p=0.007]
- F-012: Scenario selection critical for discriminability

## Next Steps
1. DOE-009: Vary heuristic weights individually on defend_the_line
2. Investigate full_agent interference mechanism
3. Fix L0 rules for defend_the_line
4. Standardize on defend_the_line
