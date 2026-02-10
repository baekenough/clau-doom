# EXPERIMENT_ORDER_037: Extreme Difficulty Movement Contrast

## Hypothesis
H-040: The movement performance benefit (F-079, F-086) persists at doom_skill=5 (Nightmare difficulty), and the effect size remains large (d > 0.8).

## Research Question
DOE-030 found VizDoom difficulty degeneracy (skill 2=3=4) and showed movement benefit is universally positive (d>0.9 at all tested difficulties). But doom_skill=5 was only tested with n=30. Does the movement effect hold under the HARDEST conditions with sufficient power?

## Design
- **Type**: 2×2 Full Factorial (CRD)
- **Factor A**: movement (present=random_5, absent=attack_raw)
- **Factor B**: doom_skill (1=Easiest, 5=Nightmare)
- **Episodes per cell**: 30
- **Total episodes**: 120
- **Scenario**: defend_the_line_5action.cfg

## Conditions
| Cell | Movement | doom_skill | Strategy |
|------|----------|------------|----------|
| A1B1 | Present | 1 | random_5 |
| A1B2 | Present | 5 | random_5 |
| A2B1 | Absent | 1 | attack_raw |
| A2B2 | Absent | 5 | attack_raw |

## Seed Set
Formula: seed_i = 77001 + i × 173, i = 0..29
Set: [77001, 77174, 77347, 77520, 77693, 77866, 78039, 78212, 78385, 78558, 78731, 78904, 79077, 79250, 79423, 79596, 79769, 79942, 80115, 80288, 80461, 80634, 80807, 80980, 81153, 81326, 81499, 81672, 81845, 82018]

## Analysis Plan
1. Two-way ANOVA: movement × doom_skill on kills
2. Main effects: movement (F-079 replication), doom_skill (F-052 replication)
3. Interaction: Does movement benefit change with difficulty?
4. Effect sizes: partial η² for all effects
5. Pairwise: Cohen's d for movement effect at each difficulty level
6. Compare to DOE-030 findings (F-084, F-085, F-086)

## Expected Outcome
Based on DOE-030:
- Movement main effect: SIGNIFICANT (strong, d > 0.9)
- doom_skill main effect: SIGNIFICANT (large, η² > 0.3)
- Interaction: POSSIBLE — movement benefit may compress at skill=5

## Linked Findings
- F-079: Movement sole determinant (d=1.408)
- F-084: Movement × difficulty interaction (p=0.002)
- F-085: VizDoom difficulty degeneracy (skill 2=3=4)
- F-086: Movement universally beneficial (d>0.9)

## Execution Notes
- Use VizDoom defend_the_line with 5-action set
- doom_skill conditions: 1 (minimum difficulty) and 5 (Nightmare)
- Strategy A1: random_5 (random movement + random attack)
- Strategy A2: attack_raw (attack-only, no movement)
- Record: kills, survival_time, ammo_efficiency, shots_fired
- DuckDB table: experiments.DOE_037
- Random seed consumption: 120 seeds total (30 per cell × 4 cells)
