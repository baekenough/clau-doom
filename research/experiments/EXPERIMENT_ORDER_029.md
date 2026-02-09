# EXPERIMENT_ORDER_029: Emergency Health Override Effect (2² Factorial)

## Metadata
- **DOE ID**: DOE-029
- **Hypothesis**: H-032
- **Design Type**: 2² Full Factorial
- **Phase**: 1 (State-Dependence Investigation)
- **Date Ordered**: 2026-02-09
- **Budget**: 120 episodes
- **Cumulative Episodes**: 5010

## Hypothesis

**H-032**: Emergency health override (force dodge when health < 20) improves survival and total kills in the 5-action defend_the_line environment.

### Rationale

All strategies tested in DOE-025 through DOE-028 included a common health<20 emergency override. This confound has never been isolated. DOE-028 showed full tactical invariance (F-077) when the override is present. Does the override ITSELF contribute to performance, or is it irrelevant like all other tactical choices?

Additionally, pure_attack (100% attack, no movement) has never been tested in the 5-action space. DOE-008 showed L0_only (always attack) was WORST in 3-action space. Does this replicate in 5-action space?

## Factors

| Factor | Levels | Description |
|--------|--------|-------------|
| action_pattern | random_50, pure_attack | Base action selection strategy |
| health_override | enabled, disabled | Health<20 emergency dodge |

### Factor Levels

**action_pattern**:
- `random_50`: p(attack)=0.5, else random movement (0-3). Same as DOE-028 baseline.
- `pure_attack`: Always action 4 (ATTACK). No movement.

**health_override**:
- `enabled`: If health < 20 OR ammo == 0, force random movement (0-3).
- `disabled`: No override. Action pattern determines all actions regardless of health/ammo.

## Design Matrix

| Run | action_pattern | health_override | Code | Episodes | Seeds |
|-----|---------------|----------------|------|----------|-------|
| R1 | random_50 | enabled | rand50_ovr | 30 | 49001+i×137 |
| R2 | random_50 | disabled | rand50_raw | 30 | 49001+i×137 |
| R3 | pure_attack | enabled | attack_ovr | 30 | 49001+i×137 |
| R4 | pure_attack | disabled | attack_raw | 30 | 49001+i×137 |

### Seed Set (n=30)

Formula: seed_i = 49001 + i × 137, for i = 0, 1, ..., 29

```
[49001, 49138, 49275, 49412, 49549, 49686, 49823, 49960, 50097, 50234,
 50371, 50508, 50645, 50782, 50919, 51056, 51193, 51330, 51467, 51604,
 51741, 51878, 52015, 52152, 52289, 52426, 52563, 52700, 52837, 52974]
```

### Randomized Run Order

R3, R1, R4, R2

## Planned Contrasts

| Contrast | Comparison | Purpose |
|----------|-----------|---------|
| Main A | random_50 vs pure_attack (averaged over override) | Movement value in 5-action space |
| Main B | override_on vs override_off (averaged over pattern) | Override value |
| A×B | Interaction | Does override matter more for one pattern? |
| C1 | rand50_ovr vs rand50_raw | Override effect for random strategy |
| C2 | attack_ovr vs attack_raw | Override effect for pure attack |
| C3 | attack_raw vs rand50_raw | Movement value without override |

## Outcome Scenarios

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| A: Override significant, pattern significant, no interaction | Both matter independently | Optimize health threshold |
| B: Override significant, pattern null | State-dependence matters, movement doesn't | State-dependent strategies are the key |
| C: Override null, pattern significant | Movement matters, state-dependence doesn't | Confirms DOE-008 F-010 in 5-action |
| D: Both null | Full invariance extends to state-dependence | Research program complete |
| E: Significant interaction | Override matters for one pattern only | Investigate mechanism |

## Analysis Plan

1. 2×2 ANOVA: kills ~ action_pattern * health_override
2. Residual diagnostics
3. Planned contrasts C1-C3
4. Kruskal-Wallis and Mann-Whitney non-parametric confirmation
5. Effect sizes (partial eta-squared, Cohen's d)
6. Secondary ANOVAs: survival_time, kill_rate

## Execution Instructions

- rand50_ovr: AttackRatioAction(0.5) — existing, has health override built in
- rand50_raw: AttackRatioAction(0.5) variant with override disabled
- attack_ovr: PureAttackAction with health override
- attack_raw: PureAttackAction without health override
- Record to DuckDB with experiment_id='DOE-029'
