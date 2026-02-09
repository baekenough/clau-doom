# EXPERIMENT_ORDER_028: Temporal Attack Pattern Study (Burst Cycle)

## Metadata
- **DOE ID**: DOE-028
- **Hypothesis**: H-031
- **Design Type**: OFAT (5 levels)
- **Phase**: 1 (Structural Investigation)
- **Date Ordered**: 2026-02-09
- **Budget**: 150 episodes
- **Cumulative Episodes**: 4890

## Hypothesis

**H-031**: Temporal grouping of attacks (burst cycling) affects kill performance independently of attack ratio, since concentrated attacks target the same enemy while dispersed attacks waste shots after movement changes aim direction.

### Rationale

DOE-027 showed total kills are invariant to attack ratio (F-071, p=0.717) due to rate-time compensation (F-074). However, DOE-025 showed survival_burst (structured burst-3 at ~40% attack) achieved highest kills among 5-action strategies (F-063, 18.07 kills). F-075 concluded the survival-first paradox was a strategy STRUCTURE artifact. DOE-028 isolates the STRUCTURE variable by fixing attack ratio at 50% across all conditions and varying only the temporal grouping pattern.

### Mechanistic Prediction

Burst cycling creates "focused attack windows" where multiple consecutive attacks target the same enemy, increasing kill probability. Random interleaving wastes attacks because movement between attack ticks changes aim direction, potentially targeting a different enemy or no enemy.

## Scenario

- **Config**: defend_the_line_5action.cfg
- **Action Space**: 5 actions (TURN_LEFT=0, TURN_RIGHT=1, MOVE_LEFT=2, MOVE_RIGHT=3, ATTACK=4)
- **Episode Length**: Default (timeout at ~90s or death)

## Factor

| Factor | Type | Description |
|--------|------|-------------|
| burst_pattern | Categorical, 5 levels | Temporal grouping of attack/move actions |

### Levels

| Level | Code | Pattern | Attack Ratio |
|-------|------|---------|-------------|
| 1 | `random_50` | p(attack)=0.5 each tick, random | 50% (expected) |
| 2 | `cycle_2` | Attack 2 ticks, Move 2 ticks, repeat | 50% (exact) |
| 3 | `cycle_3` | Attack 3 ticks, Move 3 ticks, repeat | 50% (exact) |
| 4 | `cycle_5` | Attack 5 ticks, Move 5 ticks, repeat | 50% (exact) |
| 5 | `cycle_10` | Attack 10 ticks, Move 10 ticks, repeat | 50% (exact) |

### Movement Selection During Move Phase

During the move phase of each cycle, the agent selects uniformly at random from TURN_LEFT(0), TURN_RIGHT(1), MOVE_LEFT(2), MOVE_RIGHT(3). This matches the DOE-027 ar_* baseline behavior.

### Health Override

All conditions: if health < 20, force movement (random from 0-3). If ammo == 0, force movement. Same as DOE-027 AttackRatioAction.

## Design Matrix

| Run | Condition | Burst Length | Episodes | Seeds |
|-----|-----------|-------------|----------|-------|
| R1 | random_50 | N/A (random) | 30 | 48001+i×131 |
| R2 | cycle_2 | 2 | 30 | 48001+i×131 |
| R3 | cycle_3 | 3 | 30 | 48001+i×131 |
| R4 | cycle_5 | 5 | 30 | 48001+i×131 |
| R5 | cycle_10 | 10 | 30 | 48001+i×131 |

### Seed Set (n=30)

Formula: seed_i = 48001 + i × 131, for i = 0, 1, ..., 29

```
[48001, 48132, 48263, 48394, 48525, 48656, 48787, 48918, 49049, 49180,
 49311, 49442, 49573, 49704, 49835, 49966, 50097, 50228, 50359, 50490,
 50621, 50752, 50883, 51014, 51145, 51276, 51407, 51538, 51669, 51800]
```

All conditions use the SAME seed set for paired comparison.

## Randomized Run Order

R3, R5, R1, R4, R2

## Planned Contrasts

| Contrast | Comparison | Purpose |
|----------|-----------|---------|
| C1 | random_50 vs mean(all cycles) | Structure vs no-structure effect |
| C2 | Linear trend (cycle_2 → cycle_10) | Optimal burst length |
| C3 | cycle_3 vs cycle_5 | Bracket the optimum |
| C4 | random_50 vs cycle_3 | Direct replication of DOE-025 finding |

## Outcome Scenarios

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| A: Structure significant, cycles > random | Temporal grouping matters for kills | Optimize burst length via RSM |
| B: Structure significant, random > cycles | Randomness provides beneficial exploration | Investigate stochastic advantage |
| C: No structure effect, cycle length matters | Burst length matters but not vs random | Test continuous burst length gradient |
| D: Null result (no differences) | Temporal structure irrelevant at 50% ratio | Research program summary/paper |

## Analysis Plan

1. One-way ANOVA: kills ~ burst_pattern (5 levels)
2. Residual diagnostics: normality (Anderson-Darling), equal variance (Levene), independence
3. Planned contrasts C1-C4
4. Kruskal-Wallis non-parametric confirmation
5. Effect sizes (partial eta-squared, Cohen's d for pairwise)
6. Tukey HSD if overall F significant
7. Secondary ANOVAs: survival_time, kill_rate

## Execution Instructions for doe_executor

- Use BurstCycleAction class for cycle_* conditions
- Use AttackRatioAction(attack_ratio=0.5) for random_50 condition
- Record all metrics to DuckDB experiments table with experiment_id='DOE-028'
- Run all 150 episodes (5 conditions × 30 episodes)
