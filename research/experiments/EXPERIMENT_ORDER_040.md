# EXPERIMENT_ORDER_040: Medium Difficulty Performance Mapping

## Hypothesis
H-043: Performance follows a monotonic gradient across doom_skill levels, with doom_skill=3 producing intermediate performance between the established sk1 benchmark (mean≈27 kills from F-098) and sk5 benchmark (mean≈6.5 kills from DOE-038).

## Research Question
What is the shape of the difficulty-performance curve? DOE-038 established the endpoints: easy (doom_skill=1, ~27 kills) and nightmare (doom_skill=5, ~6.5 kills). Adding a middle point (doom_skill=3) from DOE-030 completes the mapping and tests whether the relationship is linear or shows diminishing/accelerating returns. This enables predictive modeling of agent performance at any difficulty level.

## Design
- **Type**: One-Way CRD (three levels)
- **Factor**: doom_skill (1, 3, 5)
- **Strategy**: random_5 (movement-inclusive optimal architecture)
- **Scenario**: defend_the_line_5action.cfg
- **num_actions**: 5
- **Episodes per condition**: 50
- **Total episodes**: 150

## Conditions
| Run | Condition | doom_skill | Strategy | Expected Kills |
|-----|-----------|------------|----------|----------------|
| R1 | easy | 1 | random_5 | ~27 (from F-098) |
| R2 | medium | 3 | random_5 | ~15-18 (interpolated) |
| R3 | nightmare | 5 | random_5 | ~6.5 (from DOE-038) |

## Seed Set
Formula: seed_i = 89001 + i × 191, i = 0..49
Set: [89001, 89192, 89383, 89574, 89765, 89956, 90147, 90338, 90529, 90720, 90911, 91102, 91293, 91484, 91675, 91866, 92057, 92248, 92439, 92630, 92821, 93012, 93203, 93394, 93585, 93776, 93967, 94158, 94349, 94540, 94731, 94922, 95113, 95304, 95495, 95686, 95877, 96068, 96259, 96450, 96641, 96832, 97023, 97214, 97405, 97596, 97787, 97978, 98169, 98360]

## Analysis Plan
1. One-way ANOVA on kills (primary metric)
2. Kruskal-Wallis test as non-parametric backup
3. Tukey HSD pairwise comparisons with 95% family-wise CI
4. Trend analysis: linear vs quadratic contrast
5. Effect sizes: partial η² for overall model, Cohen's d for pairwise comparisons
6. Residual diagnostics: normality (Anderson-Darling), equal variance (Levene)
7. Summary statistics: mean, sd, min, max, median for each condition

## Expected Outcome
- Strong main effect expected (η² > 0.60 based on DOE-038 and F-052)
- Linear trend likely: if (easy - medium) ≈ (medium - nightmare), relationship is linear
- If nonlinear: investigate diminishing returns at easier difficulties or accelerating returns at harder difficulties
- This establishes the performance envelope for random_5 architecture across full difficulty range

## Linked Findings
- F-052: doom_skill explains 72% variance (DOE-030)
- F-054: 5.2× performance compression from easy to nightmare
- F-098: Performance ceiling ~27 kills at doom_skill=1
- This experiment completes the difficulty curve with n=50 power per point

## Execution Notes
- Use VizDoom defend_the_line with 5-action set
- doom_skill conditions: 1 (minimum), 3 (medium), 5 (Nightmare/maximum)
- Strategy: random_5 (optimal from F-079, F-086, F-102)
- High power design: n=50 per condition for precise difficulty gradient estimation
- Record: kills, survival_time, ammo_efficiency, shots_fired
- DuckDB table: experiments.DOE_040
- Random seed consumption: 150 seeds total (50 per condition × 3 conditions)
