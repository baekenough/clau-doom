# EXPERIMENT_ORDER_015: Scenario Generalization

## Metadata
- **Experiment ID**: DOE-015
- **Hypothesis**: H-019
- **DOE Phase**: Phase 1 (generalization)
- **Design Type**: One-way completely randomized design (5 levels, mixed scenarios)
- **Date Ordered**: 2026-02-08

## Research Question

Does strategy performance generalize across VizDoom scenarios? Specifically, can the basic.cfg scenario (simple 1-monster environment) serve as a useful evaluation proxy for defend_the_line.cfg?

### Background

All prior experiments (DOE-001 through DOE-014) used defend_the_line.cfg as the standard evaluation scenario. This scenario features continuous enemy waves and timeout=2100 ticks (~60s). However, VizDoom provides simpler scenarios like basic.cfg that might enable faster iteration.

**basic.cfg characteristics**:
- 3 available buttons: MOVE_LEFT, MOVE_RIGHT, ATTACK
- 1 monster per episode (binary outcome: 0 or 1 kill)
- timeout=300 ticks (~8.6s)
- Fundamentally different domain from defend_the_line

### Hypothesis

**H-019: Strategy Generalization Across Scenarios**

If strategy performance rankings (e.g., burst_3 > random) hold across different scenarios, then basic.cfg can serve as a fast proxy for initial strategy screening. If rankings differ, each scenario requires independent evaluation.

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| scenario_strategy | Categorical | 5 | Strategy applied to basic.cfg or defend_the_line.cfg |

### Factor Levels

| Level | Condition Label | Scenario | Strategy | Description |
|-------|----------------|----------|----------|-------------|
| 1 | basic_random | basic.cfg | random | Uniform random over 3 actions |
| 2 | basic_burst_3 | basic.cfg | burst_3 | 3 attacks + 1 move cycle |
| 3 | basic_attack_only | basic.cfg | attack_only | 100% attack |
| 4 | dtl_burst_3 | defend_the_line.cfg | burst_3 | Reference from DOE-010 |
| 5 | dtl_random | defend_the_line.cfg | random | Reference from DOE-010 |

### Strategy Design Rationale

**basic_random, basic_burst_3, basic_attack_only**: Three strategies tested on basic.cfg to establish performance rankings in the simple scenario.

**dtl_burst_3, dtl_random**: Reference conditions from defend_the_line.cfg to enable cross-scenario comparison. Expected performance from DOE-010: burst_3 ~44.5 kr, random ~42.2 kr.

### Key Contrasts

| Contrast | Comparison | Tests |
|----------|------------|-------|
| C1 | basic_random vs basic_burst_3 | Does burst_3 outperform random on basic.cfg? |
| C2 | basic_random vs basic_attack_only | Does attack_only outperform random on basic.cfg? |
| C3 | dtl_burst_3 vs dtl_random | Replication of DOE-010 burst_3 advantage |
| C4 | basic conditions vs dtl conditions | Cross-scenario performance levels |

### Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: basic rankings match dtl rankings** | Generalization holds | Use basic.cfg for fast screening |
| **B: basic rankings differ from dtl** | Scenario-specific performance | Each scenario needs independent evaluation |
| **C: All basic conditions indistinguishable** | basic.cfg has floor/ceiling effect | Not useful for strategy evaluation |

## Design Matrix

| Run | Condition | Scenario | Strategy | Episodes | Seeds |
|-----|-----------|----------|----------|----------|-------|
| R1 | basic_random | basic.cfg | random | 30 | [16001, ..., 16942] |
| R2 | basic_burst_3 | basic.cfg | burst_3 | 30 | [16001, ..., 16942] |
| R3 | basic_attack_only | basic.cfg | attack_only | 30 | [16001, ..., 16942] |
| R4 | dtl_burst_3 | defend_the_line.cfg | burst_3 | 30 | [16001, ..., 16942] |
| R5 | dtl_random | defend_the_line.cfg | random | 30 | [16001, ..., 16942] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R2 (basic_burst_3) -> R5 (dtl_random) -> R1 (basic_random) -> R3 (basic_attack_only) -> R4 (dtl_burst_3)

## Seed Set

**Formula**: seed_i = 16001 + i x 67, i = 0, 1, ..., 29
**Range**: [16001, 16942]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[16001, 16068, 16135, 16202, 16269, 16336, 16403, 16470, 16537, 16604,
 16671, 16738, 16805, 16872, 16939, 17006, 17073, 17140, 17207, 17274,
 17341, 17408, 17475, 17542, 17609, 17676, 17743, 17810, 17877, 16942]
```

## Scenario Configuration

### basic.cfg (R1, R2, R3)
```
available_buttons = { MOVE_LEFT MOVE_RIGHT ATTACK }
available_game_variables = { KILLCOUNT }
episode_timeout = 300  # ~8.6s at 35 fps
```

### defend_the_line.cfg (R4, R5)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # ~60s at 35 fps
```

### Known Limitations

1. **Binary kills on basic.cfg**: With only 1 monster, kills are 0 or 1 per episode. This creates extreme variance in kill_rate calculations.
2. **Different timeout durations**: basic.cfg timeout is 300 ticks vs 2100 for defend_the_line. Episodes end at different times.
3. **Different action spaces**: basic.cfg uses MOVE_LEFT/MOVE_RIGHT (physical movement), defend_the_line uses TURN_LEFT/TURN_RIGHT (rotation). Strategies are not directly comparable.

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kill_rate (5 levels)
   - Response: kill_rate = (kills / survival_time) * 60
   - Factor: scenario_strategy (5 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk test on ANOVA residuals
3. **Equal variance**: Levene test across groups
4. **Independence**: Residuals vs run order plot

### If ANOVA significant (p < 0.05):
5. **Tukey HSD** all pairwise comparisons
6. **Planned contrasts** (C1-C4 as defined above)
7. **Effect sizes**: Cohen's d for pairwise, eta-squared for overall
8. **Bonferroni correction** for the 4 planned contrasts (adjusted alpha = 0.0125)

### Non-Parametric Backup
9. **Kruskal-Wallis** if normality violated

### Secondary Responses
10. Repeat analysis for kills and survival_time

### Power
- Expected power for medium effect (f=0.25) with k=5, n=30, alpha=0.05: [STAT:power=0.83]

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 16001 + i*67, i=0..29 |
| No seed collisions | YES: verified against DOE-001 through DOE-014 |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, equal variance, independence |
| Effect sizes | PLANNED: Cohen's d, eta-squared |
| Seeds identical across conditions | YES: all 5 conditions use the same 30 seeds |

## Execution Checklist

Before execution, verify:
- [ ] basic.cfg available and configured
- [ ] defend_the_line.cfg unchanged from prior experiments
- [ ] VizDoomBridge supports scenario switching between runs
- [ ] random, burst_3, attack_only action functions ready
- [ ] Seed set generated and logged
- [ ] DuckDB experiment table schema supports DOE-015 columns

## Status

**ORDERED** — Ready for execution.
