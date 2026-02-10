# EXPERIMENT_ORDER_036: basic.cfg Attack Ratio Gradient

## Hypothesis
H-039: In the basic.cfg scenario (strafe-aiming, no turning), attack ratio affects kill performance differently than in defend_the_line because MOVE_LEFT/MOVE_RIGHT serve dual purpose as both evasion AND aiming.

## Research Question
Does the attack ratio → kills relationship from defend_the_line (F-071: kills invariant to attack ratio) hold in a scenario where movement IS aiming?

## Design
- **Type**: One-Way CRD (Completely Randomized Design)
- **Factor**: attack_ratio (4 levels: 20%, 40%, 60%, 80%)
- **Episodes per condition**: 30
- **Total episodes**: 120
- **Scenario**: basic.cfg (3-action: MOVE_LEFT, MOVE_RIGHT, ATTACK)
- **doom_skill**: 5 (basic.cfg default)

## Conditions
| Condition | Attack % | Move % | Action Type |
|-----------|----------|--------|-------------|
| ar_20 | 20% | 80% | ar_20 |
| ar_40 | 40% | 60% | ar_40 |
| ar_60 | 60% | 40% | ar_60 |
| ar_80 | 80% | 20% | ar_80 |

## Seed Set
Formula: seed_i = 73001 + i × 167, i = 0..29
Set: [73001, 73168, 73335, 73502, 73669, 73836, 74003, 74170, 74337, 74504, 74671, 74838, 75005, 75172, 75339, 75506, 75673, 75840, 76007, 76174, 76341, 76508, 76675, 76842, 77009, 77176, 77343, 77510, 77677, 77844]

## Analysis Plan
1. One-way ANOVA on kills (primary) and survival_time (secondary)
2. Residual diagnostics (normality, equal variance, independence)
3. Effect size: partial η², Cohen's d for pairwise
4. Compare gradient shape to defend_the_line F-071 (invariance)
5. If significant: identify optimal attack ratio for strafe-aiming
6. If null: confirms F-071 extends across scenarios

## Expected Outcome
If basic.cfg strafe-aiming changes the relationship:
- Lower attack ratios → more movement → better aiming → more kills
- Expect ar_20 or ar_40 to outperform ar_80

If invariance extends:
- All attack ratios produce similar kill counts
- Confirms F-071 is a universal property of random-action architectures

## Linked Findings
- F-071: Attack ratio invariance for kills (defend_the_line)
- F-074: Rate-time compensation mechanism
- F-077: Full tactical invariance

## Execution Notes
- Use VizDoom basic.cfg environment
- Map: default basic.cfg map (not defend_the_line)
- Record: kills, survival_time, ammo_efficiency, shots_fired
- DuckDB table: experiments.DOE_036
- Random seed consumption: 120 seeds total (30 per condition × 4 conditions)
