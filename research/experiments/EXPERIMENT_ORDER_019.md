# EXPERIMENT_ORDER_019: Cross-Validation

## Metadata
- **Experiment ID**: DOE-019
- **Hypothesis**: H-023 — Top strategies maintain ranking in cross-validation with independent seeds
- **DOE Phase**: Phase 1
- **Design Type**: One-way completely randomized design (5 levels)
- **Date Ordered**: 2026-02-08

## Research Question

Do the best-performing strategies from DOE-008 through DOE-018 maintain their ranking when tested with fresh, independent seeds?

### Background

After 11 experiments (DOE-008 through DOE-018), several strategies have emerged as top performers:
- **burst_3**: Best kills strategy in DOE-012, 013, 017 (~44-45 kr)
- **l0_only**: Worst performer in DOE-008, 010 (~39 kr)
- **adaptive_kill**: Best adaptive strategy in DOE-018 (~46 kr)
- **random**: Consistent baseline across all experiments (~42-43 kr)
- **attack_only**: Pure aggression baseline (~43-44 kr)

All prior experiments used different seed sets. H-023 tests whether strategy rankings REPLICATE across independent seed sets, which is critical for establishing trust in findings.

### Hypothesis

**H-023: Top Strategies Maintain Ranking in Cross-Validation**

The performance ranking observed across DOE-008 through DOE-018 will replicate when tested with a fresh seed set. Specifically:
- burst_3 will remain top-tier (kill_rate ~44-45)
- l0_only will remain worst-tier (kill_rate ~38-40)
- adaptive_kill will match top-tier performance (kill_rate ~45-46)
- random will remain mid-tier baseline (kill_rate ~42-43)

If rankings replicate, this confirms that seed set choice does not drive results, increasing trust in all prior findings.

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| action_strategy | Categorical | 5 | Best, worst, and baseline strategies from prior campaign |

### Factor Levels

| Level | Condition Label | Description | Expected kill_rate |
|-------|----------------|-------------|-------------------|
| 1 | random | Baseline from all prior experiments | ~42-43 |
| 2 | attack_only | Pure aggression baseline | ~43-44 |
| 3 | burst_3 | Best kills strategy (DOE-012, 013, 017) | ~44-45 |
| 4 | l0_only | Worst strategy (DOE-008, 010) | ~38-40 |
| 5 | adaptive_kill | Best adaptive strategy (DOE-018) | ~45-46 |

### Strategy Selection Rationale

**random**: Universal baseline across all 11 prior experiments. Anchors cross-validation.

**attack_only**: Pure aggression baseline. Tested in DOE-008, 009, 018.

**burst_3**: Top kills performer in DOE-012 (14.97 kills), DOE-013 (14.80 kills), DOE-017 (14.97 kills). Consistent ~44-45 kr across experiments.

**l0_only**: Consistently worst performer in DOE-008 (F-010: 39.31 kr) and DOE-010 (F-016: 38.63 kr). Tests whether "tunnel vision" strategy replicates as worst.

**adaptive_kill**: DOE-018 winner (F-032: 46.18 kr). Tests whether state-dependent adaptation replicates top-tier performance.

### Key Contrasts

| Contrast | Comparison | Tests |
|----------|------------|-------|
| C1 | burst_3 vs l0_only | Best vs worst replication |
| C2 | adaptive_kill vs burst_3 | Adaptive vs fixed best replication |
| C3 | adaptive_kill vs random | Adaptive vs baseline |
| C4 | l0_only vs random | Worst vs baseline separation |

### Expected Outcomes

| Outcome | Interpretation | Trust Level |
|---------|---------------|-------------|
| **A: Rankings replicate** | Strategies are robust to seed choice | HIGH trust in all findings |
| **B: Rankings shift slightly** | Some seed dependence exists | MEDIUM trust, need larger n |
| **C: Rankings scramble** | Results are seed-dependent | LOW trust, fundamental issue |

## Design Matrix

| Run | Condition | Description | Episodes | Seeds |
|-----|-----------|-------------|----------|-------|
| R1 | random | Uniform random 3-action | 30 | [20001, ..., 22404] |
| R2 | attack_only | 100% attack | 30 | [20001, ..., 22404] |
| R3 | burst_3 | 3 attacks + 1 move | 30 | [20001, ..., 22404] |
| R4 | l0_only | Attack-only at action index 0 (tunnel vision) | 30 | [20001, ..., 22404] |
| R5 | adaptive_kill | State-dependent adaptive | 30 | [20001, ..., 22404] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R2 (attack_only) -> R4 (l0_only) -> R1 (random) -> R3 (burst_3) -> R5 (adaptive_kill)

## Seed Set

**Formula**: seed_i = 20001 + i × 83, i = 0, 1, ..., 29
**Range**: [20001, 22404]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[20001, 20084, 20167, 20250, 20333, 20416, 20499, 20582, 20665, 20748,
 20831, 20914, 20997, 21080, 21163, 21246, 21329, 21412, 21495, 21578,
 21661, 21744, 21827, 21910, 21993, 22076, 22159, 22242, 22325, 22404]
```

### Cross-Experiment Seed Collision Check

This seed set ([20001, 22404]) is COMPLETELY INDEPENDENT from all prior experiments:
- DOE-008: [6001, 7074]
- DOE-010: [10001, 11248]
- DOE-011: [12001, 13364]
- DOE-012: [14001, 15364]
- DOE-017: [17001, 18364]
- DOE-018: [19001, 21284]

**Verdict**: Zero collisions. True cross-validation.

## Scenario Configuration

**Scenario**: defend_the_line.cfg (3-action space)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kill_rate (5 levels)
   - Response: kill_rate = (kills / survival_time) * 60
   - Factor: action_strategy (5 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk or Anderson-Darling test
3. **Equal variance**: Levene test
4. **Independence**: Residuals vs run order

### If ANOVA significant (p < 0.05):
5. **Tukey HSD** all pairwise comparisons
6. **Planned contrasts** (C1-C4)
7. **Effect sizes**: Cohen's d and partial eta-squared
8. **Bonferroni correction** for contrasts (alpha = 0.0125)

### Cross-Experiment Comparison
9. **Compare to prior experiments**:
   - burst_3 DOE-019 vs DOE-012/017
   - l0_only DOE-019 vs DOE-008/010
   - adaptive_kill DOE-019 vs DOE-018
   - random DOE-019 vs all prior experiments

### Non-Parametric Backup
10. **Kruskal-Wallis** if normality violated

### Secondary Responses
11. Repeat for kills and survival_time

### Power
- Expected power for medium effect (f=0.25) with k=5, n=30, alpha=0.05: [STAT:power=0.83]
- Prior experiments observed f=0.30-0.37: [STAT:power>0.90]

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 20001 + i×83, i=0..29 |
| No seed collisions | YES: verified against all prior experiments |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, variance, independence |
| Effect sizes | PLANNED: Cohen's d, partial eta-squared |
| Seeds identical across conditions | YES: all 5 conditions use same 30 seeds |

## Execution Checklist

Before execution, verify:
- [ ] All 5 action functions implemented and tested
- [ ] l0_only function replicates DOE-008/010 implementation
- [ ] burst_3 function replicates DOE-012/017 implementation
- [ ] adaptive_kill function replicates DOE-018 implementation
- [ ] Seed set generated and logged
- [ ] DuckDB experiment table ready

## Status

**ORDERED** — Ready for execution
