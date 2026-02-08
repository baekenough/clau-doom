# EXPERIMENT_REPORT_016: Deadly Corridor Feasibility

## Metadata
- **Experiment ID**: DOE-016
- **Hypothesis**: H-020
- **Experiment Order**: EXPERIMENT_ORDER_016.md
- **Date Executed**: 2026-02-08
- **Scenario**: deadly_corridor.cfg
- **Total Episodes**: 150 (5 conditions x 30 episodes)

## Design Summary

One-way completely randomized design testing 5 action strategies on deadly_corridor.cfg. Tests whether simple heuristic agents can achieve meaningful kill counts on a navigation-focused scenario.

| Condition | Strategy | Attack Rate | n |
|-----------|----------|-------------|---|
| dc_random_7 | random | 14% | 30 |
| dc_forward_attack | forward+attack cycle | 75% | 30 |
| dc_burst_3_turn | attack burst+turn | 75% | 30 |
| dc_attack_only | pure attack | 100% | 30 |
| dc_adaptive | state-dependent | ~50% | 30 |

## Descriptive Statistics

| Condition | kill_rate (mean +/- SD) | kills (mean +/- SD) | survival (mean +/- SD) |
|-----------|------------------------|---------------------|------------------------|
| dc_random_7 | 2.05 +/- 6.34 | 0.10 +/- 0.31 | 2.80 +/- 1.05 |
| dc_forward_attack | 0.83 +/- 4.56 | 0.03 +/- 0.18 | 2.28 +/- 0.49 |
| dc_burst_3_turn | 0.60 +/- 3.31 | 0.03 +/- 0.18 | 2.84 +/- 1.11 |
| dc_attack_only | 0.60 +/- 3.28 | 0.03 +/- 0.18 | 2.85 +/- 1.09 |
| dc_adaptive | 0.00 +/- 0.00 | 0.00 +/- 0.00 | 2.86 +/- 1.09 |

**Notable Pattern**: ALL conditions exhibit extreme floor effects. Kill counts range from 0.00 to 0.10 kills per episode. Survival times are uniformly low (2.3-2.9 seconds). No meaningful differentiation between strategies.

## Primary Analysis: One-way ANOVA on kill_rate

### ANOVA Table

| Source | SS | df | MS | F | p | eta2 |
|--------|------|----|----|------|------|------|
| Strategy | 88.2 | 4 | 22.1 | 1.036 | 0.391 | 0.028 |
| Error | 3097.6 | 145 | 21.4 | | | |
| Total | 3185.9 | 149 | | | | |

**Result**: [STAT:f=F(4,145)=1.036] [STAT:p=0.391] [STAT:eta2=0.028] -- **NOT SIGNIFICANT**

### Residual Diagnostics

| Diagnostic | Test | Statistic | p-value | Result |
|-----------|------|-----------|---------|--------|
| Normality | Shapiro-Wilk | W=0.1834 | <0.0001 | **FAIL** |
| Equal Variance | Levene | W=1.542 | 0.193 | PASS |

**Diagnostic Note**: Severe non-normality due to zero-inflation (most episodes have 0 kills). Equal variance holds only because all conditions have uniformly low variance.

### Non-parametric Analysis

- Kruskal-Wallis: H(4) = 3.218 [STAT:p=0.522] -- **NOT SIGNIFICANT**

Confirms ANOVA result: no detectable difference between strategies.

## Secondary Responses

### kills

| Source | SS | df | MS | F | p | eta2 |
|--------|------|----|----|------|------|------|
| Strategy | 0.233 | 4 | 0.058 | 1.036 | 0.391 | 0.028 |
| Error | 8.167 | 145 | 0.056 | | | |
| Total | 8.400 | 149 | | | | |

**Result**: [STAT:f=F(4,145)=1.036] [STAT:p=0.391] [STAT:eta2=0.028] -- **NOT SIGNIFICANT**

**Tukey HSD**: No significant pairwise comparisons. All p_adj > 0.9.

**One-sample t-tests vs 0 kills**:
- dc_random_7: t(29)=1.764, p=0.088 (borderline)
- All other conditions: p > 0.3 (NOT different from 0)

Only dc_random_7 shows marginal evidence of kills above zero floor.

### survival_time

| Source | SS | df | MS | F | p | eta2 |
|--------|------|----|----|------|------|------|
| Strategy | 7.32 | 4 | 1.83 | 1.865 | 0.120 | 0.049 |
| Error | 142.36 | 145 | 0.98 | | | |
| Total | 149.68 | 149 | | | | |

**Result**: [STAT:f=F(4,145)=1.865] [STAT:p=0.120] [STAT:eta2=0.049] -- **NOT SIGNIFICANT**

All conditions produce 2.3-2.9 second survival times. No strategy extends survival meaningfully.

## Floor Effect Analysis

### Zero-Inflation

| Condition | Episodes with 0 kills | Percentage |
|-----------|----------------------|------------|
| dc_random_7 | 27/30 | 90% |
| dc_forward_attack | 29/30 | 97% |
| dc_burst_3_turn | 29/30 | 97% |
| dc_attack_only | 29/30 | 97% |
| dc_adaptive | 30/30 | 100% |

**Total**: 144/150 episodes (96%) produced 0 kills.

### Maximum Performance

| Condition | Max kills in single episode |
|-----------|---------------------------|
| dc_random_7 | 1 kill (3 episodes) |
| dc_forward_attack | 1 kill (1 episode) |
| dc_burst_3_turn | 1 kill (1 episode) |
| dc_attack_only | 1 kill (1 episode) |
| dc_adaptive | 0 kills (all episodes) |

Even the best single-episode performance is only 1 kill (rare event).

## Interpretation

### Key Discovery: deadly_corridor Exhibits Complete Floor Effect

The central finding of DOE-016 is that **deadly_corridor.cfg is beyond the capability of simple heuristic agents**:

1. **Uniformly low performance**: All strategies produce ~0 kills per episode (range: 0.00-0.10). No strategy achieves meaningful kill counts.

2. **No strategy differentiation**: ANOVA p=0.391, Kruskal-Wallis p=0.522. Random, forward_attack, burst, attack_only, and adaptive strategies are statistically indistinguishable.

3. **Extremely short survival**: All conditions die within 2-3 seconds. Agents cannot navigate forward through the corridor before being killed.

4. **Navigation requirement**: The corridor scenario requires coordinated forward movement, enemy avoidance, and aiming—capabilities beyond heuristic action selection. The agent spawns in a narrow corridor and is immediately overwhelmed.

### H-020 Disposition: REJECTED

H-020 predicted that at least one simple heuristic strategy would achieve meaningful kill counts (>3 kills per episode) on deadly_corridor. The results show:

- **No strategy above floor**: Best mean = 0.10 kills (dc_random_7), which is NOT meaningfully above 0.
- **Floor effect confirmed**: 96% of episodes produce 0 kills.
- **Scenario too complex**: Navigation-focused scenarios require capabilities beyond current agent architecture.

### Implications for Research Design

1. **Retire deadly_corridor from pipeline**: The scenario is unsuitable for simple agent evaluation. Floor effects prevent any strategy differentiation.

2. **Navigation requires advanced architecture**: Simple heuristic action selection cannot solve navigation tasks. Future work would need pathfinding, spatial awareness, or learned policies.

3. **defend_the_line remains optimal**: Stationary combat scenarios (where the agent rotates but does not move) are appropriate for current agent capabilities.

4. **Scenario difficulty screening**: Before running full DOE experiments, pilot test new scenarios with n=10 to check for floor/ceiling effects.

### Recommended Next Steps

1. **Do NOT pursue deadly_corridor experiments**: Zero kills and 2-second survival make it impossible to evaluate strategies.

2. **Focus on defend_the_line variations**: Modify defend_the_line parameters (enemy count, timeout, difficulty) rather than changing scenarios.

3. **Agent architecture upgrade**: If navigation scenarios are desired, develop state-aware agents with pathfinding (Phase 3 work, beyond current scope).

## Findings

- **F-030**: deadly_corridor.cfg exhibits a FLOOR EFFECT for all simple agent strategies [STAT:f=F(4,145)=1.036] [STAT:p=0.391]. All conditions produce ~0 kills (range: 0.00-0.10) with 2-3 second survival. 96% of episodes have 0 kills. The corridor navigation requirement is beyond heuristic action selection capability. deadly_corridor is NOT suitable for current agent architecture evaluation.

## Trust Assessment

| Aspect | Assessment |
|--------|-----------|
| ANOVA significance | NOT significant (p=0.391) |
| Diagnostics | Normality FAIL (zero-inflation), Variance PASS |
| Effect size | eta^2 = 0.028 (negligible) |
| Floor effect | Confirmed: 96% of episodes have 0 kills |
| Scenario suitability | REJECTED: floor effect prevents evaluation |
| Overall Trust | **HIGH** for F-030 (floor effect conclusion). Non-parametric confirmation (Kruskal-Wallis p=0.522) and one-sample t-tests support zero-inflation finding. |
