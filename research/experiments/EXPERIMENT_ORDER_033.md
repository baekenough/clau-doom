# EXPERIMENT_ORDER_033: Action Space × Movement Interaction

## Metadata

- **DOE ID**: DOE-033
- **Hypothesis**: H-036
- **Design Type**: 3×2 Full Factorial
- **Phase**: 3 (Confirmation)
- **Date Ordered**: 2026-02-10
- **Budget**: 180 episodes
- **Cumulative Episodes**: 5490

## Hypothesis

**H-036**: The interaction between action space size and movement availability creates significant performance differences. Movement benefit (measured as Cohen's d for kills) is larger in 5-action and 7-action spaces compared to 3-action space, because in larger action spaces, movement actions represent true directional control (strafe left/right), whereas in 3-action space, movement is limited to turn-only actions.

### Rationale

Phase 2 established two independent findings:
1. **F-079** (DOE-029): Movement is the sole determinant of performance at default difficulty (d=1.408)
2. **F-087** (DOE-031): Action space exhibits non-monotonic relationship with kills (5-action ≈ 7-action > 3-action >> 9-action)

However, these experiments tested movement and action space in isolation. An interaction is theoretically plausible: the efficacy of movement depends on action space design. Specifically, 5-action and 7-action spaces include true strafing (MOVE_LEFT, MOVE_RIGHT), whereas 3-action space includes only rotation (TURN_LEFT, TURN_RIGHT). True strafing may be qualitatively more effective for evasion than rotation alone.

This experiment tests whether the movement advantage is AMPLIFIED in action spaces with true strafing, or whether movement dominates uniformly regardless of action space design.

### Research Value

- Tests the SCOPE of F-079 (movement dominance). Is it universal or action-space-dependent?
- Informs action space design decisions in Phase 4 (synthesis experiments)
- Provides interaction term for the paper's generalizability claims
- Tests whether movement operationalization matters

## Factors

| Factor | Levels | Type | Description |
|--------|--------|------|-------------|
| action_space | 3, 5, 7 | Fixed | Number of discrete actions available |
| movement | present, absent | Fixed | Whether movement-type actions are enabled |

### Factor Levels

**action_space** (3 levels):
- 3-action: TURN_LEFT(0), TURN_RIGHT(1), ATTACK(2)
- 5-action: MOVE_LEFT(0), MOVE_RIGHT(1), TURN_LEFT(2), TURN_RIGHT(3), ATTACK(4)
- 7-action: MOVE_LEFT(0), MOVE_RIGHT(1), MOVE_BACKWARD(2), TURN_LEFT(3), TURN_RIGHT(4), ATTACK(5), ATTACK_MELEE(6)

**movement** (2 levels):
- present: Agent randomly selects movement or attack (p_attack=0.5 for 3-action/5-action; mixed strategy for 7-action with movement actions enabled)
- absent: Agent performs attack-only behavior (action 2 for 3-action, action 4 for 5-action, action 5 for 7-action)

### Operationalization by Condition

| Condition | action_space | movement | Action Type | Strategy |
|-----------|-------------|----------|------------|----------|
| 3act_move | 3 | present | random_basic | Random 50% TURN left/right, 50% ATTACK |
| 3act_stat | 3 | absent | attack_only | Always ATTACK(2) |
| 5act_move | 5 | present | ar_50 | Random 50% movement (MOVE_LEFT/RIGHT), 50% ATTACK |
| 5act_stat | 5 | absent | attack_raw | Always ATTACK(4) from 5-action space |
| 7act_move | 7 | present | ar_50 | Random 50% movement (MOVE_LEFT/RIGHT/BACKWARD), 50% ATTACK(5) |
| 7act_stat | 7 | absent | attack_raw | Always ATTACK(5) from 7-action space |

## Response Variables

| Variable | Metric | Direction |
|----------|--------|-----------|
| kills | Total enemies killed per episode | Maximize |
| survival_time | Ticks alive before death or timeout | Maximize |
| kill_rate | kills / (survival_time / 35) | Maximize |

## Design Matrix

| Run | action_space | movement | Condition | Config | Episodes | Seeds |
|-----|-------------|----------|-----------|--------|----------|-------|
| R01 | 3 | present | 3act_move | defend_the_line_3action.cfg | 30 | 65001+i*157 |
| R02 | 3 | absent | 3act_stat | defend_the_line_3action.cfg | 30 | 65001+i*157 |
| R03 | 5 | present | 5act_move | defend_the_line_5action.cfg | 30 | 65001+i*157 |
| R04 | 5 | absent | 5act_stat | defend_the_line_5action.cfg | 30 | 65001+i*157 |
| R05 | 7 | present | 7act_move | defend_the_line_7action.cfg | 30 | 65001+i*157 |
| R06 | 7 | absent | 7act_stat | defend_the_line_7action.cfg | 30 | 65001+i*157 |

### Seed Set (n=30, shared across all runs)

Formula: seed_i = 65001 + i * 157, for i = 0, 1, ..., 29

```
[65001, 65158, 65315, 65472, 65629, 65786, 65943, 66100, 66257, 66414,
 66571, 66728, 66885, 67042, 67199, 67356, 67513, 67670, 67827, 67984,
 68141, 68298, 68455, 68612, 68769, 68926, 69083, 69240, 69397, 69554]
```

Maximum seed: 69554

### Randomized Run Order

R04, R01, R06, R02, R05, R03

## Analysis Plan

### Primary Analysis

Two-way ANOVA: kills ~ action_space × movement

| Source | df |
|--------|-----|
| action_space (A) | 2 |
| movement (B) | 1 |
| A × B (interaction) | 2 |
| Error | 174 |
| Total | 179 |

Key tests:
1. **Main effect of action_space**: Replication of F-087 (5 ≈ 7 > 3)
2. **Main effect of movement**: Replication of F-079 (movement dominance)
3. **Interaction A × B**: Does movement benefit vary by action space?

### Planned Contrasts

| ID | Contrast | Tests |
|----|----------|-------|
| C1 | Movement present vs absent (collapsed across action_space) | Overall movement effect |
| C2 | 3-action vs (5-action, 7-action) | Discrimination between low and high action spaces |
| C3 | 5-action vs 7-action | Discrimination between optimal action spaces |
| C4 | Movement × [3-action vs (5, 7)] | Does movement benefit differ in 3-action? |
| C5 | Movement × [5-action vs 7-action] | Are 5-action and 7-action equivalent with movement? |

### Diagnostics

- Normality: Anderson-Darling on residuals
- Equal variance: Levene test
- Independence: Run order plot
- Non-parametric fallback: Kruskal-Wallis per action_space level

### Effect Size Metrics

- Partial eta-squared (η²) for each ANOVA term
- Cohen's d for movement effect AT EACH action_space level separately
- Comparison of d values across action spaces: does movement benefit amplify in larger action spaces?

## Power Analysis

- Alpha = 0.05
- From DOE-029: movement effect d = 1.408 (massive)
- From DOE-031: action_space effect η² ≈ 0.15
- With n=30 per cell (6 cells, N=180):
  - Power for movement main effect (d=1.4): > 0.99
  - Power for action_space main effect (η²=0.15): > 0.95
  - Power for interaction (expected small): approximately 0.75

## Execution Instructions for research-doe-runner

1. Use scenario defend_the_line (all difficulties kept at default doom_skill=3)
2. For 3-action runs: use defend_the_line_3action.cfg
3. For 5-action runs: use defend_the_line_5action.cfg
4. For 7-action runs: use defend_the_line_7action.cfg
5. For "present" movement: use ar_50 action function (random 50% movement, 50% attack from available actions)
6. For "absent" movement: use attack_only action function (always attack, suppress movement actions)
7. No health or doom_skill overrides
8. Record kills, survival_time (ticks), compute kill_rate = kills / (survival_time / 35)
9. 30 episodes per cell, all cells use same seed set
10. Follow randomized run order: R04, R01, R06, R02, R05, R03

## Expected Outcomes

| Outcome | Probability | Implication |
|---------|------------|-------------|
| A: No interaction, movement dominates across all action spaces | 50% | F-079 is universal; action space operationalization is secondary |
| B: Interaction significant, movement d increases with action space (3 < 5 ≈ 7) | 35% | Movement benefit is amplified by strafing availability |
| C: Action space effect disappears (3 ≈ 5 ≈ 7) | 10% | F-087 was difficulty or strategy-specific artifact |
| D: 3-action outperforms 5-action/7-action | 5% | Simpler action spaces reduce exploration overhead |

## Cross-References

- F-079: Movement sole determinant (DOE-029, d=1.408)
- F-087: Non-monotonic action space curve, 5 ≈ 7 > 3 >> 9 (DOE-031)
- F-084: Movement × difficulty non-monotonic interaction (DOE-030)
- F-082: Rate-time compensation breaks at movement boundary (DOE-029)
