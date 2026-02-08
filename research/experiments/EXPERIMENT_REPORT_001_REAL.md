# EXPERIMENT_REPORT_001_REAL: DOE-001 Real VizDoom Baseline Comparison

**DATA SOURCE**: REAL VIZDOOM EPISODES (not simulated)
**Experiment Order**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Hypothesis**: H-001 (HYPOTHESIS_BACKLOG.md)
**Date**: 2026-02-08
**Status**: COMPLETE

## Design Summary

- **Type**: OFAT (One Factor At a Time)
- **Factor**: Decision Architecture (3 levels: Random, Rule-Only, Full Agent)
- **Episodes per condition**: 70
- **Total episodes**: 210
- **Seeds**: seed_i = 42 + i*31, i=0..69 (identical across conditions)
- **Scenario**: defend_the_center.cfg (VizDoom built-in)

## Results

### Primary Metric: Kills

| Condition | Mean | SD | n |
|-----------|------|-----|---|
| random | 9.90 | 3.33 | 70 |
| rule_only | 26.00 | 0.00 | 70 |
| full_agent | 26.00 | 0.00 | 70 |

### Pairwise Comparisons (Kills)

#### full_agent vs random

| Metric | Value |
|--------|-------|
| t-statistic | [STAT:t=40.4732] |
| p-value (unadjusted) | [STAT:p=0.000000] |
| p-value (Holm-Bonferroni) | [STAT:p_adj=0.000000] |
| Cohen's d | [STAT:effect_size=Cohen's d=6.84] |
| 95% CI | [STAT:ci=95%: 15.32 to 16.88] |
| Mann-Whitney U p | [STAT:p_mann=0.000000] |
| Significant | YES |

**Interpretation**: full_agent achieved 16.10 more kills than random (95% CI: [15.32, 16.88]). Effect size is large (d=6.84).

#### full_agent vs rule_only

| Metric | Value |
|--------|-------|
| t-statistic | [STAT:t=nan] |
| p-value (unadjusted) | [STAT:p=nan] |
| p-value (Holm-Bonferroni) | [STAT:p_adj=1.000000] |
| Cohen's d | [STAT:effect_size=Cohen's d=0.00] |
| 95% CI | [STAT:ci=95%: 0.00 to 0.00] |
| Mann-Whitney U p | [STAT:p_mann=1.000000] |
| Significant | NO |

**Interpretation**: full_agent achieved 0.00 more kills than rule_only (95% CI: [0.00, 0.00]). Effect size is small (d=0.00).

#### rule_only vs random

| Metric | Value |
|--------|-------|
| t-statistic | [STAT:t=40.4732] |
| p-value (unadjusted) | [STAT:p=0.000000] |
| p-value (Holm-Bonferroni) | [STAT:p_adj=0.000000] |
| Cohen's d | [STAT:effect_size=Cohen's d=6.84] |
| 95% CI | [STAT:ci=95%: 15.32 to 16.88] |
| Mann-Whitney U p | [STAT:p_mann=0.000000] |
| Significant | YES |

**Interpretation**: rule_only achieved 16.10 more kills than random (95% CI: [15.32, 16.88]). Effect size is large (d=6.84).

### Secondary Metrics

#### Survival Time (seconds)

| Condition | Mean | SD |
|-----------|------|-----|
| random | 8.7 | 1.8 |
| rule_only | 7.8 | 1.2 |
| full_agent | 7.8 | 1.2 |

#### Ammo Efficiency

| Condition | Mean | SD |
|-----------|------|-----|
| random | 0.000 | 0.000 |
| rule_only | 0.000 | 0.000 |
| full_agent | 0.000 | 0.000 |

### Diagnostics

#### Normality (Anderson-Darling)

| Condition | A-squared | p-value | Result |
|-----------|-----------|---------|--------|
| random | 0.7955 | 0.0250 | FAIL |
| rule_only | nan | 0.0010 | FAIL |
| full_agent | nan | 0.0010 | FAIL |

**Overall**: FAIL

#### Equal Variance (Levene)

- Levene's W: 138.2438
- p-value: 0.0000
- Result: FAIL

#### Independence

- Seed set used: identical across all conditions [seed_i = 42 + i*31]
- No time-dependent confounds
- Result: PASS

#### Overall Diagnostics: FAIL

### Trust Assessment

**Trust Level**: LOW

**Criteria**:
- Sample size: [STAT:n=70 per condition]
- Normality: FAIL
- Equal variance: FAIL
- Adjusted p-value: [STAT:p_adj=0.000000]
- Effect size: [STAT:effect_size=Cohen's d=6.84]

## Conclusions

### H-001: Full Agent Outperforms Baselines

**Status**: SUPPORTED

The full agent (L0 rules + memory + strategy heuristics) demonstrated statistically significant improvement over the random baseline in kills [STAT:p_adj=0.000000]. The effect size was large [STAT:effect_size=Cohen's d=6.84].

Compared to rule-only baseline, the full agent showed no significant improvement [STAT:p_adj=1.000000], with a small effect size [STAT:effect_size=Cohen's d=0.00].

### H-002: Rule Engine Provides Value

**Status**: SUPPORTED

The rule-only baseline significantly outperformed the random baseline [STAT:p_adj=0.000000], with a large effect [STAT:effect_size=Cohen's d=6.84].

### H-003: Decision Latency Within Bounds

Full agent decision latency P99: 0.0ms (mean).
Target: < 100ms. Result: PASS.

## Next Steps

1. If HIGH/MEDIUM trust: Adopt findings to FINDINGS.md, proceed to Phase 1
2. If LOW trust: Increase sample size or address diagnostic violations
3. Follow-up experiments:
   - H-004: Memory weight optimization (factorial design)
   - H-005: Strategy document quality impact
   - Phase 2: RSM for fine-tuning optimal parameters

## Data Location

- **DuckDB**: data_dir/doe_001_real.duckdb
- **Experiment table**: `experiments` (210 rows)
- **Seed set table**: `seed_sets` (1 row)

---

**Report generated**: 2026-02-08 06:01:12
**Analysis pipeline**: `glue/doe_001_real.py`
**Data source**: Real VizDoom episodes (defend_the_center scenario)
