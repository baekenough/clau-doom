# EXPERIMENT_REPORT_001: DOE-001 Baseline Comparison

**Experiment Order**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Hypothesis**: H-001 (HYPOTHESIS_BACKLOG.md)
**Date**: 2026-02-08
**Status**: COMPLETE

## Design Summary

- **Type**: OFAT (One Factor At a Time)
- **Factor**: Decision Architecture (3 levels: Random, Rule-Only, Full RAG)
- **Episodes per condition**: 70
- **Total episodes**: 210
- **Seeds**: seed_i = 42 + i*31, i=0..69 (identical across conditions)

## Results

### Primary Metric: Kills

| Condition | Mean | SD | n |
|-----------|------|-----|---|
| random | 2.77 | 2.41 | 70 |
| rule_only | 16.63 | 5.81 | 70 |
| full_agent | 42.57 | 10.37 | 70 |

### Pairwise Comparisons (Kills)

#### full_agent vs random

| Metric | Value |
|--------|-------|
| t-statistic | [STAT:t=31.2641] |
| p-value (unadjusted) | [STAT:p=0.000000] |
| p-value (Holm-Bonferroni) | [STAT:p_adj=0.000000] |
| Cohen's d | [STAT:effect_size=Cohen's d=5.28] |
| 95% CI | [STAT:ci=95%: 37.30 to 42.30] |
| Mann-Whitney U p | [STAT:p_mann=0.000000] |
| Significant | YES |

**Interpretation**: Full agent achieved 39.80 more kills than random baseline (95% CI: [37.30, 42.30]). Effect size is large (d=5.28).

#### full_agent vs rule_only

| Metric | Value |
|--------|-------|
| t-statistic | [STAT:t=18.2544] |
| p-value (unadjusted) | [STAT:p=0.000000] |
| p-value (Holm-Bonferroni) | [STAT:p_adj=0.000000] |
| Cohen's d | [STAT:effect_size=Cohen's d=3.09] |
| 95% CI | [STAT:ci=95%: 23.16 to 28.73] |
| Mann-Whitney U p | [STAT:p_mann=0.000000] |
| Significant | YES |

**Interpretation**: Full agent achieved 25.94 more kills than rule-only baseline (95% CI: [23.16, 28.73]). Effect size is large (d=3.09).

#### rule_only vs random

| Metric | Value |
|--------|-------|
| t-statistic | [STAT:t=18.4227] |
| p-value (unadjusted) | [STAT:p=0.000000] |
| p-value (Holm-Bonferroni) | [STAT:p_adj=0.000000] |
| Cohen's d | [STAT:effect_size=Cohen's d=3.11] |
| 95% CI | [STAT:ci=95%: 12.38 to 15.33] |
| Mann-Whitney U p | [STAT:p_mann=0.000000] |
| Significant | YES |

**Interpretation**: Rule-only achieved 13.86 more kills than random baseline (95% CI: [12.38, 15.33]). Effect size is large (d=3.11).

### Secondary Metrics

#### Survival Time (seconds)

| Condition | Mean | SD |
|-----------|------|-----|
| random | 55.9 | 18.5 |
| rule_only | 113.9 | 27.7 |
| full_agent | 171.9 | 36.9 |

#### Ammo Efficiency

| Condition | Mean | SD |
|-----------|------|-----|
| random | 0.147 | 0.057 |
| rule_only | 0.344 | 0.115 |
| full_agent | 0.593 | 0.138 |

### Diagnostics

#### Normality (Anderson-Darling)

| Condition | A² statistic | p-value | Result |
|-----------|-------------|---------|--------|
| random | 1.9388 | 0.0010 | FAIL |
| rule_only | 0.1974 | 0.2500 | PASS |
| full_agent | 0.1806 | 0.2500 | PASS |

**Overall**: FAIL

#### Equal Variance (Levene)

- Levene's W: 42.0766
- p-value: 0.0000
- Result: FAIL

#### Independence

- Seed set used: identical across all conditions [seed_i = 42 + i*31]
- No time-dependent confounds
- Result: PASS

#### Overall Diagnostics: PARTIAL

### Trust Assessment

**Trust Level**: LOW

**Criteria**:
- Sample size: [STAT:n=70 per condition]
- Normality: FAIL
- Equal variance: FAIL
- Adjusted p-value: [STAT:p_adj=0.000000]
- Effect size: [STAT:effect_size=Cohen's d=5.28]

## Conclusions

### H-001: Full RAG Agent Outperforms Baselines

**Status**: SUPPORTED

The full RAG agent (L0+L1+L2 cascade) demonstrated statistically significant improvement over the random baseline in kill rate [STAT:p_adj=0.000000]. The effect size was large [STAT:effect_size=Cohen's d=5.28].

Compared to rule-only baseline, the full agent showed significant improvement [STAT:p_adj=0.000000], with a large effect size [STAT:effect_size=Cohen's d=3.09].

### H-002: Rule Engine Provides Value

**Status**: SUPPORTED

The rule-only baseline significantly outperformed the random baseline [STAT:p_adj=0.000000], with a large effect [STAT:effect_size=Cohen's d=3.11]. This validates that L0 rules provide meaningful structure.

### H-003: Decision Latency Within Bounds

**Status**: SUPPORTED

Full agent decision latency P99: 45.1ms (mean across all episodes).
Target: < 100ms. Result: PASS.

## Next Steps

1. **If HIGH/MEDIUM trust**: Adopt findings to FINDINGS.md, proceed to Phase 1 parameter optimization
2. **If LOW trust**: Increase sample size or address diagnostic violations
3. **Follow-up experiments**:
   - H-004: Memory weight optimization (factorial design)
   - H-005: Strategy document quality impact
   - Phase 2: RSM for fine-tuning optimal parameters

## Data Location

- **DuckDB**: `volumes/data/doe_001.duckdb`
- **Experiment table**: `experiments` (210 rows)
- **Seed set table**: `seed_sets` (1 row)

---

**Report generated**: 2026-02-08 09:34:00
**Analysis pipeline**: `glue/doe_001_execute.py`
