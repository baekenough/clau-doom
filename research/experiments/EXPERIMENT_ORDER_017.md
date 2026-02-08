# EXPERIMENT_ORDER_017: Replication of Attack_only Deficit

## Metadata
- **Experiment ID**: DOE-017
- **Hypothesis**: H-021
- **DOE Phase**: Phase 1 (replication)
- **Design Type**: One-way completely randomized design (5 levels)
- **Date Ordered**: 2026-02-08

## Research Question

Do the key findings from DOE-012 and DOE-010 replicate with an independent seed set? Specifically: (1) Does attack_only produce significantly fewer kills than burst and random strategies? (2) Are burst_3 and random statistically indistinguishable?

### Background

DOE-012 established F-023: attack_only produces significantly fewer kills than all other strategies on defend_the_line (Cohen's d = 0.80-1.10). DOE-010 established F-019: random and burst_3 are statistically indistinguishable (~43 kr).

These findings have been used as references in subsequent experiments (DOE-011, DOE-013, DOE-014). Before relying on them for Phase 2 optimization, we must verify they replicate with independent seeds. If replication fails, findings may be seed-specific artifacts.

### Hypothesis

**H-021: DOE-012/DOE-010 Findings Replicate**

With a new independent seed set:
1. attack_only will produce significantly fewer kills than random, burst_1, burst_3, and burst_5 (replicates F-023)
2. random and burst_3 will be statistically indistinguishable (replicates F-019)
3. Effect sizes will be similar (d ~ 0.8-1.1 for attack_only deficit)

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| action_strategy | Categorical | 5 | Attack pattern on defend_the_line (3-action space) |

### Factor Levels

| Level | Condition Label | Description | Attack Rate |
|-------|----------------|-------------|-------------|
| 1 | random | Uniform random over 3 actions | 33% |
| 2 | burst_1 | 1 attack + 1 random turn | 50% |
| 3 | burst_3 | 3 attacks + 1 random turn | 75% |
| 4 | burst_5 | 5 attacks + 1 random turn | 83% |
| 5 | attack_only | 100% attack | 100% |

### Strategy Design Rationale

These 5 conditions replicate the DOE-010 and DOE-012 designs exactly, using identical action functions and the same scenario (defend_the_line.cfg). The ONLY change is the seed set.

**random, burst_1, burst_3, burst_5**: Four strategies spanning 33%-83% attack rate. Tests if the burst_3/random equivalence (F-019) holds.

**attack_only**: 100% attack. Tests if the attack_only deficit (F-023) replicates.

### Key Contrasts

| Contrast | Comparison | Tests Replication Of |
|----------|------------|---------------------|
| C1 | random vs burst_3 | F-019 (indistinguishable) |
| C2 | attack_only vs random | F-023 (attack_only deficit) |
| C3 | attack_only vs burst_1 | F-023 (attack_only deficit) |
| C4 | attack_only vs burst_3 | F-023 (attack_only deficit) |
| C5 | attack_only vs burst_5 | F-023 (attack_only deficit) |

### Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: All contrasts replicate** | Findings are robust | Proceed to Phase 2 with confidence |
| **B: attack_only deficit replicates, burst/random does not** | F-023 robust, F-019 seed-specific | Re-evaluate burst strategies |
| **C: No replication** | All findings seed-specific | Redo DOE-010/012 with larger n |

## Design Matrix

| Run | Condition | Strategy | Episodes | Seeds |
|-----|-----------|----------|----------|-------|
| R1 | random | random | 30 | [18001, ..., 20116] |
| R2 | burst_1 | burst_1 | 30 | [18001, ..., 20116] |
| R3 | burst_3 | burst_3 | 30 | [18001, ..., 20116] |
| R4 | burst_5 | burst_5 | 30 | [18001, ..., 20116] |
| R5 | attack_only | attack_only | 30 | [18001, ..., 20116] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R4 (burst_5) -> R2 (burst_1) -> R5 (attack_only) -> R1 (random) -> R3 (burst_3)

## Seed Set

**Formula**: seed_i = 18001 + i x 73, i = 0, 1, ..., 29
**Range**: [18001, 20116]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[18001, 18074, 18147, 18220, 18293, 18366, 18439, 18512, 18585, 18658,
 18731, 18804, 18877, 18950, 19023, 19096, 19169, 19242, 19315, 19388,
 19461, 19534, 19607, 19680, 19753, 19826, 19899, 19972, 20045, 20116]
```

### Seed Independence Verification

| Experiment | Seed Range | Overlap with [18001, 20116]? |
|-----------|------------|------------------------------|
| DOE-010 | [10001, 11248] | NO |
| DOE-012 | [13001, 14219] | NO |
| All prior experiments | Various | NO |

**Verdict**: Zero collisions. This seed set is INDEPENDENT of all prior experiments.

## Scenario Configuration

### defend_the_line.cfg (all runs)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # ~60s at 35 fps
```

**Note**: Same configuration as DOE-010 and DOE-012. No changes.

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kills (5 levels)
   - Response: kills
   - Factor: action_strategy (5 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk test on ANOVA residuals
3. **Equal variance**: Levene test across groups
4. **Independence**: Residuals vs run order plot

### If ANOVA significant (p < 0.05):
5. **Tukey HSD** all pairwise comparisons
6. **Planned contrasts** (C1-C5 as defined above):
   - C1: random vs burst_3 (expect p > 0.05)
   - C2-C5: attack_only vs others (expect p < 0.05, d ~ 0.8-1.1)
7. **Effect sizes**: Cohen's d for all pairwise comparisons
8. **Bonferroni correction** for 5 planned contrasts (adjusted alpha = 0.01)

### Replication Criteria
9. **Effect size comparison** with DOE-012:
   - DOE-012: attack_only vs burst_3, Cohen's d = 1.10
   - DOE-017: Expect Cohen's d within [0.8, 1.4] range
10. **Effect size comparison** with DOE-010:
    - DOE-010: random vs burst_3, Cohen's d = 0.12 (negligible)
    - DOE-017: Expect Cohen's d < 0.3

### Secondary Responses
11. Repeat analysis for kill_rate and survival_time

### Non-Parametric Backup
12. **Kruskal-Wallis** if normality violated

### Power
- Expected power for medium effect (f=0.25) with k=5, n=30, alpha=0.05: [STAT:power=0.83]
- Expected power for large effect (f=0.40, observed in DOE-012) with k=5, n=30, alpha=0.05: [STAT:power=0.99]

## Cross-Experiment Replication Targets

### DOE-012 Targets (kills)

| Comparison | DOE-012 Cohen's d | Expected DOE-017 Range |
|------------|------------------|----------------------|
| attack_only vs burst_1 | 0.80 | [0.6, 1.0] |
| attack_only vs burst_3 | 1.10 | [0.8, 1.4] |
| attack_only vs burst_5 | 1.02 | [0.8, 1.3] |

### DOE-010 Targets (kill_rate)

| Comparison | DOE-010 Cohen's d | Expected DOE-017 Range |
|------------|------------------|----------------------|
| random vs burst_3 | 0.12 | [-0.2, 0.4] (negligible) |

Replication is considered successful if:
1. All attack_only vs X comparisons are significant (p < 0.01 after Bonferroni)
2. Effect sizes fall within expected ranges
3. random vs burst_3 is NOT significant (p > 0.05)

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 18001 + i*73, i=0..29 |
| No seed collisions | YES: verified against all prior experiments |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, equal variance, independence |
| Effect sizes | PLANNED: Cohen's d for all pairwise comparisons |
| Seeds identical across conditions | YES: all 5 conditions use the same 30 seeds |

## Execution Checklist

Before execution, verify:
- [ ] defend_the_line.cfg unchanged from prior experiments
- [ ] All 5 action functions ready (random, burst_1, burst_3, burst_5, attack_only)
- [ ] Seed set generated and logged
- [ ] DuckDB schema supports DOE-017 columns
- [ ] No infrastructure changes since DOE-010/012

## Status

**ORDERED** — Ready for execution. This is a direct replication with independent seeds.
