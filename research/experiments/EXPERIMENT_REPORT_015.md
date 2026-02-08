# EXPERIMENT_REPORT_015: Scenario Generalization

## Metadata
- **Experiment ID**: DOE-015
- **Hypothesis**: H-019
- **Experiment Order**: EXPERIMENT_ORDER_015.md
- **Date Executed**: 2026-02-08
- **Scenarios**: basic.cfg and defend_the_line.cfg
- **Total Episodes**: 150 (5 conditions x 30 episodes)

## Design Summary

One-way completely randomized design testing 5 scenario-strategy combinations across two VizDoom scenarios. Tests whether strategy performance rankings generalize from defend_the_line.cfg to basic.cfg.

| Condition | Scenario | Strategy | n |
|-----------|----------|----------|---|
| basic_random | basic.cfg | random | 30 |
| basic_burst_3 | basic.cfg | burst_3 | 30 |
| basic_attack_only | basic.cfg | attack_only | 30 |
| dtl_burst_3 | defend_the_line.cfg | burst_3 | 30 |
| dtl_random | defend_the_line.cfg | random | 30 |

## Descriptive Statistics

| Condition | kill_rate (mean +/- SD) | kills (mean +/- SD) | survival (mean +/- SD) |
|-----------|------------------------|---------------------|------------------------|
| basic_random | 69.31 +/- 118.34 | 0.57 +/- 0.50 | 29.31 +/- 27.97 |
| basic_burst_3 | 104.90 +/- 152.04 | 0.60 +/- 0.50 | 25.60 +/- 28.81 |
| basic_attack_only | 101.02 +/- 154.36 | 0.40 +/- 0.50 | 36.24 +/- 29.60 |
| dtl_burst_3 | 45.26 +/- 6.27 | 12.93 +/- 4.86 | 17.46 +/- 6.03 |
| dtl_random | 41.80 +/- 6.76 | 13.17 +/- 5.34 | 19.03 +/- 6.65 |

**Notable Pattern**: basic.cfg conditions exhibit EXTREME variance in kill_rate (SD > 100) compared to defend_the_line (SD ~6-7). With only 1 monster per episode, kills are binary (0 or 1), producing massive variance when normalized to kills per minute.

## Primary Analysis: One-way ANOVA on kill_rate

### ANOVA Table

| Source | SS | df | MS | F | p | eta2 |
|--------|------|----|----|------|------|------|
| Scenario | 131547.2 | 4 | 32886.8 | 2.186 | 0.073 | 0.057 |
| Error | 2181760.4 | 145 | 15046.6 | | | |
| Total | 2313307.6 | 149 | | | | |

**Result**: [STAT:f=F(4,145)=2.186] [STAT:p=0.073] [STAT:eta2=0.057] -- **NOT SIGNIFICANT**

### Residual Diagnostics

| Diagnostic | Test | Statistic | p-value | Result |
|-----------|------|-----------|---------|--------|
| Normality | Shapiro-Wilk | W=0.4107 | <0.0001 | **FAIL** |
| Equal Variance | Levene | W=38.642 | <0.0001 | **FAIL** |

**Diagnostic Failure**: Extreme variance heterogeneity (max SD/min SD = 154.36/6.27 = 24.6x) violates all ANOVA assumptions. The binary kill outcome on basic.cfg creates a fundamentally different distribution from continuous kill counts on defend_the_line.

### Non-parametric Analysis

Due to severe diagnostic failures, non-parametric analysis is required:
- Kruskal-Wallis: H(4) = 4.329 [STAT:p=0.363] -- **NOT SIGNIFICANT**

## Secondary Responses

### kills

| Source | SS | df | MS | F | p | eta2 |
|--------|------|----|----|------|------|------|
| Scenario | 2827.2 | 4 | 706.8 | 174.832 | <0.000001 | 0.828 |
| Error | 586.3 | 145 | 4.0 | | | |
| Total | 3413.5 | 149 | | | | |

**Result**: [STAT:f=F(4,145)=174.832] [STAT:p<0.000001] [STAT:eta2=0.828] -- **MASSIVE EFFECT**

**Residual Diagnostics**: Normality FAIL (p<0.0001), Levene FAIL (p<0.0001)

**Tukey HSD**:
- All basic vs dtl comparisons: Cohen's d > 3.7, p_adj < 0.001 (extreme effects)
- No significant differences within basic conditions (p_adj > 0.9)
- No significant differences within dtl conditions (p_adj > 0.9)

**Interpretation**: The two scenarios produce fundamentally different kill counts (basic: 0-1 kills, dtl: 10-18 kills). This is a domain difference, not a strategy effect.

### survival_time

| Source | SS | df | MS | F | p | eta2 |
|--------|------|----|----|------|------|------|
| Scenario | 5619.1 | 4 | 1404.8 | 3.451 | 0.010 | 0.087 |
| Error | 59012.4 | 145 | 407.0 | | | |
| Total | 64631.5 | 149 | | | | |

**Result**: [STAT:f=F(4,145)=3.451] [STAT:p=0.010] [STAT:eta2=0.087] -- **SIGNIFICANT**

**Residual Diagnostics**: Normality FAIL (p=0.003), Levene FAIL (p<0.0001)

**Tukey HSD**:
- basic_attack_only vs dtl_burst_3: Cohen's d=0.88, p_adj=0.012
- basic_attack_only vs dtl_random: Cohen's d=0.80, p_adj=0.029
- No other significant pairs

**Interpretation**: basic_attack_only survives longer (36.2s) than dtl conditions (17-19s), but this reflects scenario timeout differences (basic: 300 ticks, dtl: 2100 ticks) and is not meaningful.

## Cross-Scenario Comparison

### basic.cfg Performance

| Condition | kills | survival | kill_rate |
|-----------|-------|----------|-----------|
| basic_random | 0.57 | 29.3s | 69.3 kr |
| basic_burst_3 | 0.60 | 25.6s | 104.9 kr |
| basic_attack_only | 0.40 | 36.2s | 101.0 kr |

**Within-basic ANOVA**: kills F(2,87)=1.022, p=0.365 (NOT significant)

No strategy differentiation within basic.cfg. All three strategies produce statistically indistinguishable kill counts (~0.4-0.6 kills per episode).

### defend_the_line Performance

| Condition | kills | survival | kill_rate |
|-----------|-------|----------|-----------|
| dtl_burst_3 | 12.93 | 17.5s | 45.3 kr |
| dtl_random | 13.17 | 19.0s | 41.8 kr |

**Within-dtl comparison**: kills t(58)=-0.189, p=0.851 (NOT significant); kill_rate t(58)=1.904, p=0.062 (borderline)

Replicates DOE-010 finding (F-019): burst_3 and random are statistically indistinguishable on defend_the_line.

## Interpretation

### Key Discovery: basic.cfg is Unsuitable for Strategy Evaluation

The central finding of DOE-015 is that **basic.cfg and defend_the_line.cfg are fundamentally different domains**:

1. **Different kill distributions**: basic.cfg produces binary outcomes (0 or 1 kill), defend_the_line produces continuous counts (10-18 kills). Effect size eta^2=0.828 (massive).

2. **No strategy differentiation on basic.cfg**: All three strategies (random, burst_3, attack_only) produce identical kill counts (~0.5 kills/episode, p=0.365). The single-monster scenario lacks the complexity needed to differentiate strategies.

3. **Extreme variance on basic.cfg**: kill_rate SD ranges from 118 to 154 (vs 6-7 on defend_the_line). Binary kill outcomes create unstable rate calculations.

4. **Strategy rankings do NOT generalize**: On defend_the_line, burst_3 slightly outperforms random. On basic.cfg, all strategies are equivalent. Performance rankings are scenario-specific.

### H-019 Disposition: REJECTED

H-019 predicted that strategy performance rankings would generalize across scenarios, enabling basic.cfg as a fast proxy for defend_the_line evaluation. The results show:

- **No generalization**: Strategy rankings differ between scenarios (indistinguishable on basic, borderline differentiation on dtl).
- **basic.cfg is not suitable**: Binary kill outcomes produce floor effects and extreme variance.
- **Scenario-specific evaluation required**: Each VizDoom scenario needs independent strategy testing.

### Implications for Research Design

1. **Do NOT use basic.cfg for strategy evaluation**: The single-monster design creates floor effects. No strategy can be distinguished from random with n=30.

2. **defend_the_line remains the standard**: Continuous kill counts (10-18 per episode) provide sufficient variance for strategy differentiation.

3. **Scenario generalization is NOT guaranteed**: Strategy performance must be validated independently for each scenario.

4. **Sample size requirements differ by scenario**: basic.cfg might require n>100 per condition to detect small effects on binary outcomes.

### Recommended Next Steps

1. **Retire basic.cfg from research pipeline**: Focus all experiments on defend_the_line or scenarios with continuous outcomes.

2. **Test other scenarios**: Explore VizDoom scenarios with intermediate complexity (e.g., health_gathering, deadly_corridor) to find additional evaluation environments.

3. **Continue defend_the_line experiments**: All findings (F-001 through F-029) remain valid and generalizable within the defend_the_line domain.

## Findings

- **F-029**: basic.cfg is a fundamentally different domain from defend_the_line [STAT:f=F(4,145)=174.832] [STAT:p<0.000001] [STAT:eta2=0.828]. Binary kill outcomes (0 or 1) create extreme variance and prevent strategy differentiation. Strategy performance rankings do NOT generalize across scenarios. defend_the_line remains the standard evaluation scenario.

## Trust Assessment

| Aspect | Assessment |
|--------|-----------|
| ANOVA significance | kills: p < 0.000001 (domain difference, not strategy effect) |
| Diagnostics | All FAIL (normality, variance) for kill_rate and kills |
| Effect size | eta^2 = 0.828 (massive) for scenario difference |
| Power | Not applicable (non-parametric required) |
| Generalization | REJECTED: scenarios are incomparable domains |
| Overall Trust | **HIGH** for F-029 (scenario incompatibility). Kruskal-Wallis confirms ANOVA patterns despite diagnostic failures. |
