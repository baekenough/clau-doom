# EXPERIMENT_ORDER_038: High-Power Difficulty Performance Mapping

## Hypothesis
H-041: The performance ceiling at doom_skill=1 (~27 kills, F-098) drops substantially at doom_skill=5, and the magnitude of this drop can be precisely estimated with n=50 per condition.

## Research Question
What is the precise performance ceiling at each extreme difficulty level? DOE-030 tested 5 difficulty levels with n=30 each, but focused on the movement contrast. DOE-038 tests ONLY the optimal configuration (random_5 with movement) at extreme difficulties with higher power (n=50) for precise ceiling estimation.

## Design
- **Type**: One-Way CRD (two levels)
- **Factor**: doom_skill (1=Easiest, 5=Nightmare)
- **Strategy**: random_5 (the movement-inclusive standard)
- **Episodes per condition**: 50
- **Total episodes**: 100
- **Scenario**: defend_the_line_5action.cfg

## Conditions
| Condition | doom_skill | Strategy | Expected Kills |
|-----------|------------|----------|----------------|
| easy | 1 | random_5 | ~27 (F-098) |
| nightmare | 5 | random_5 | ~5-10 (estimated from DOE-030) |

## Seed Set
Formula: seed_i = 81001 + i × 179, i = 0..49
Set: [81001, 81180, 81359, 81538, 81717, 81896, 82075, 82254, 82433, 82612, 82791, 82970, 83149, 83328, 83507, 83686, 83865, 84044, 84223, 84402, 84581, 84760, 84939, 85118, 85297, 85476, 85655, 85834, 86013, 86192, 86371, 86550, 86729, 86908, 87087, 87266, 87445, 87624, 87803, 87982, 88161, 88340, 88519, 88698, 88877, 89056, 89235, 89414, 89593, 89772]

## Analysis Plan
1. Two-sample t-test on kills (primary metric)
2. Welch's t-test (unequal variances expected)
3. Effect size: Cohen's d
4. 95% CI for the difficulty gap
5. Survival time comparison (secondary)
6. Kill rate comparison (kills/minute)
7. Summary statistics: mean, sd, min, max, median for both conditions

## Expected Outcome
- Large effect expected (d > 2.0 based on DOE-030 doom_skill effect η²=0.72)
- Precise ceiling estimates: easy ~27±5, nightmare ~5-10±3
- This completes the performance envelope for the random-action architecture

## Linked Findings
- F-052: doom_skill explains 72% variance
- F-054: 5.2× effect compression from easy to nightmare
- F-098: Performance ceiling ~27 kills at doom_skill=1

## Execution Notes
- Use VizDoom defend_the_line with 5-action set
- doom_skill conditions: 1 (minimum difficulty) and 5 (Nightmare/maximum)
- Strategy: random_5 (optimal random architecture from F-079, F-086)
- High power design: n=50 per condition to precisely estimate ceiling difference
- Record: kills, survival_time, ammo_efficiency, shots_fired
- DuckDB table: experiments.DOE_038
- Random seed consumption: 100 seeds total (50 per condition × 2 conditions)
