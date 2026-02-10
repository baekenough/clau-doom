# EXPERIMENT_ORDER_041: deadly_corridor.cfg 7-Action Strategy Comparison

## Hypothesis
H-044: Movement-based strategies (random_7, forward_attack) outperform stationary strategies (attack_only) in deadly_corridor.cfg, a navigation-heavy scenario requiring corridor traversal combined with combat.

## Research Question
Does the movement advantage (established in defend_the_line via F-079, F-102) generalize to navigation-intensive scenarios? deadly_corridor.cfg is the most complex standard VizDoom scenario: agents must navigate a corridor while dodging projectiles and eliminating enemies. All 7 possible actions are relevant (MOVE_LEFT, MOVE_RIGHT, ATTACK, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT). This tests whether random_7 (full action diversity) and forward_attack (goal-directed movement) outperform attack_only (no movement, pure positioning).

## Design
- **Type**: One-Way CRD (three levels)
- **Factor**: Action Strategy
- **Scenario**: deadly_corridor.cfg (7 actions available)
- **num_actions**: 7
- **doom_skill**: 3 (moderate difficulty for corridor navigation)
- **Episodes per condition**: 30
- **Total episodes**: 90

## Conditions
| Run | Condition | Strategy | Description |
|-----|-----------|----------|-------------|
| R1 | random_7 | random_7 | Random selection from all 7 actions |
| R2 | forward_attack | forward_attack | Move forward (goal-directed) + attack (hybrid) |
| R3 | attack_only | attack_only | Attack only (no movement) |

## Seed Set
Formula: seed_i = 93001 + i × 193, i = 0..29
Set: [93001, 93194, 93387, 93580, 93773, 93966, 94159, 94352, 94545, 94738, 94931, 95124, 95317, 95510, 95703, 95896, 96089, 96282, 96475, 96668, 96861, 97054, 97247, 97440, 97633, 97826, 98019, 98212, 98405, 98598]

## Analysis Plan
1. One-way ANOVA on kills (primary metric)
2. Kruskal-Wallis test as non-parametric backup (if residuals non-normal)
3. Tukey HSD pairwise comparisons with 95% family-wise CI
4. Effect sizes: partial η² for overall model, Cohen's d for pairwise comparisons
5. Residual diagnostics: normality (Anderson-Darling), equal variance (Levene)
6. Survival time analysis (secondary metric: corridor traversal efficiency)
7. Summary statistics: mean, sd, min, max, median for each condition

## Expected Outcome
- forward_attack expected to excel: goal-directed movement (forward) directly solves corridor navigation problem
- random_7 expected intermediate: includes forward/backward movement among other actions (lower forward probability)
- attack_only expected worst: stationary positioning ineffective in corridor environment
- If forward_attack >> attack_only: movement strategy matters critically for navigation scenarios
- If random_7 ≈ forward_attack: random exploration sufficient even in structured navigation task

## Linked Hypotheses and Findings
- H-079: Movement enables superior performance (defend_the_line baseline)
- F-102: Random action selection with movement outperforms attack_only
- This experiment: cross-scenario validation of movement advantage in navigation-heavy scenario
- This extends F-079/F-102 beyond positional combat to environment navigation

## Execution Notes
- Use VizDoom deadly_corridor scenario
- doom_skill = 3 (moderate difficulty for corridor navigation)
- Record: kills, survival_time, ammo_efficiency, shots_fired, corridor_progress
- DuckDB table: experiments.DOE_041
- Random seed consumption: 90 seeds total (30 per condition × 3 conditions)
- Note: deadly_corridor may show different dynamics than defend_the_line due to navigation requirements and confined space
