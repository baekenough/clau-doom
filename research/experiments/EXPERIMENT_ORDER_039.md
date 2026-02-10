# EXPERIMENT_ORDER_039: predict_position.cfg Movement Strategy Contrast

## Hypothesis
H-042: Movement-based agents (random action selection including turns) outperform stationary attack-only agents in predict_position.cfg, a moving-target scenario.

## Research Question
Does turning ability enhance performance in scenarios with moving enemies? predict_position.cfg features a single enemy that moves unpredictably. Unlike defend_the_line (where enemies approach in roughly predictable lines), predict_position tests whether agents must adjust aim by rotating. If random_5 (includes turns) outperforms attack_raw (never turns), then aiming at moving targets requires active rotation.

## Design
- **Type**: One-Way CRD (two levels)
- **Factor**: Action Strategy
- **Scenario**: predict_position.cfg (3 actions available: TURN_LEFT, TURN_RIGHT, ATTACK)
- **num_actions**: 3
- **doom_skill**: 3 (moderate difficulty)
- **Episodes per condition**: 30
- **Total episodes**: 60

## Conditions
| Run | Condition | Strategy | Description |
|-----|-----------|----------|-------------|
| R1 | random | random_3 | Random selection from 3 actions (includes turns) |
| R2 | attack_raw | attack_raw | Always attacks, never turns |

## Seed Set
Formula: seed_i = 85001 + i × 181, i = 0..29
Set: [85001, 85182, 85363, 85544, 85725, 85906, 86087, 86268, 86449, 86630, 86811, 86992, 87173, 87354, 87535, 87716, 87897, 88078, 88259, 88440, 88621, 88802, 88983, 89164, 89345, 89526, 89707, 89888, 90069, 90250]

## Analysis Plan
1. Two-sample Welch's t-test on kills (primary metric)
2. Mann-Whitney U test as non-parametric backup
3. Effect size: Cohen's d
4. 95% CI for the performance difference
5. Survival time and ammo efficiency as secondary metrics
6. Summary statistics: mean, sd, min, max, median for both conditions

## Expected Outcome
- If random_3 > attack_raw: turning ability critical for tracking moving enemies (d > 0.5 expected)
- If random_3 ≈ attack_raw: attack_raw sufficient despite moving target (moving enemy eventually enters crosshair)
- Result informs whether movement strategies generalize beyond defend_the_line

## Linked Hypotheses
- H-079: Movement enables superior performance (defend_the_line baseline)
- H-102: Random action selection outperforms specialized strategies
- This experiment: cross-scenario validation of movement advantage

## Execution Notes
- Use VizDoom predict_position scenario
- doom_skill = 3 (consistent with DOE-030 intermediate difficulty)
- Record: kills, survival_time, ammo_efficiency, shots_fired
- DuckDB table: experiments.DOE_039
- Random seed consumption: 60 seeds total (30 per condition × 2 conditions)
