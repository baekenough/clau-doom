# EXPERIMENT_ORDER_031: Action Space Granularity Threshold (One-Way, 4 Levels)

## Metadata
- **DOE ID**: DOE-031
- **Hypothesis**: H-034
- **Design Type**: One-Way ANOVA (4 levels)
- **Phase**: 2 (Generalizability Testing)
- **Date Ordered**: 2026-02-10
- **Budget**: 120 episodes
- **Cumulative Episodes**: 5430

## Hypothesis

**H-034**: Tactical invariance (F-077) breaks down in larger action spaces (7+ actions). As action dimensionality increases, random action selection becomes increasingly suboptimal because the probability of choosing a useful action (ATTACK) decreases from 33% (3-action) to 20% (5-action) to 14% (7-action) to 11% (9-action), creating exploitable performance gaps that structured strategies can capture.

### Rationale

Across DOE-008 through DOE-029, we tested 3-action and 5-action spaces. Key findings:
- 3-action space: tactical invariance (random equivalent to structured, F-035)
- 5-action space: full tactical invariance for movement strategies (F-077), but movement vs no-movement separates (F-079)
- 7-action space (deadly_corridor, DOE-016): complete floor effect (all zero kills, F-030) -- but this was a SCENARIO limitation, not action space

The untested question: does increasing action dimensionality on defend_the_line (where we KNOW strategies can separate) create stronger differentiation? With 7 actions, a random agent attacks only 14% of ticks; with 9 actions, only 11%. If structured agents maintain 50% attack while using extra actions for survival, the gap should widen.

### Specific Predictions

1. Kill performance gradient: 3-action > 5-action > 7-action > 9-action for RANDOM strategy (dilution effect)
2. Kill performance: structured strategies resist dilution because they maintain attack frequency
3. Tactical invariance threshold: at some action count, random becomes significantly worse than structured

### Research Value

- Identifies the action space dimensionality threshold where strategy matters
- Extends F-077 (tactical invariance) to its boundary conditions
- Informs the paper's scope claims about when RAG/strategy becomes relevant

## Factors

| Factor | Levels | Type | Description |
|--------|--------|------|-------------|
| action_space | 4 | Fixed | Number of available actions |

### Factor Levels

**action_space** (4 levels):

1. **3-action** (defend_the_line.cfg): TURN_LEFT(0), TURN_RIGHT(1), ATTACK(2)
   - Random p(attack) = 33%
   - Strategy: random_3 (uniform random)

2. **5-action** (defend_the_line_5action.cfg): MOVE_LEFT(0), MOVE_RIGHT(1), TURN_LEFT(2), TURN_RIGHT(3), ATTACK(4)
   - Random p(attack) = 20%
   - Strategy: random_5 (uniform random)

3. **7-action** (defend_the_line_7action.cfg -- requires creation): MOVE_LEFT(0), MOVE_RIGHT(1), TURN_LEFT(2), TURN_RIGHT(3), ATTACK(4), MOVE_FORWARD(5), MOVE_BACKWARD(6)
   - Random p(attack) = 14%
   - Strategy: random_7 (uniform random)

4. **9-action** (defend_the_line_9action.cfg -- requires creation): MOVE_LEFT(0), MOVE_RIGHT(1), TURN_LEFT(2), TURN_RIGHT(3), ATTACK(4), MOVE_FORWARD(5), MOVE_BACKWARD(6), SPEED(7), TURN180(8)
   - Random p(attack) = 11%
   - Strategy: random_9 (uniform random)

### Infrastructure Note

7-action and 9-action configs need to be created by adding buttons to the defend_the_line scenario. VizDoom supports all these buttons natively (MOVE_FORWARD, MOVE_BACKWARD, SPEED, TURN180 are standard VizDoom buttons). The doe-runner must create the .cfg files before execution. See Execution Instructions below.

### Design Decision: Random-Only

This experiment tests ONLY random strategies at each action space level. Rationale:
- We want to measure the DILUTION effect of larger action spaces
- Random is the baseline that captures pure action space effects without strategy confounds
- If random performance degrades monotonically, it proves the dilution mechanism
- A follow-up DOE can then test structured vs random at the threshold action space

## Response Variables

| Variable | Metric | Direction |
|----------|--------|-----------|
| kills | Total enemies killed per episode | Maximize |
| survival_time | Ticks alive before death or timeout | Maximize |
| kill_rate | kills / (survival_time / 35) | Maximize |

## Design Matrix

| Run | action_space | Scenario Config | Strategy | p(attack) | Episodes | Seeds |
|-----|-------------|-----------------|----------|-----------|----------|-------|
| R1 | 3-action | defend_the_line.cfg | random_3 | 0.333 | 30 | 57101+i*149 |
| R2 | 5-action | defend_the_line_5action.cfg | random_5 | 0.200 | 30 | 57101+i*149 |
| R3 | 7-action | defend_the_line_7action.cfg | random_7 | 0.143 | 30 | 57101+i*149 |
| R4 | 9-action | defend_the_line_9action.cfg | random_9 | 0.111 | 30 | 57101+i*149 |

### Seed Set (n=30, shared across all runs)

Formula: seed_i = 57101 + i * 149, for i = 0, 1, ..., 29

```
[57101, 57250, 57399, 57548, 57697, 57846, 57995, 58144, 58293, 58442,
 58591, 58740, 58889, 59038, 59187, 59336, 59485, 59634, 59783, 59932,
 60081, 60230, 60379, 60528, 60677, 60826, 60975, 61124, 61273, 61422]
```

Maximum seed: 61422

### Randomized Run Order

R3, R1, R4, R2

## Analysis Plan

### Primary Analysis

One-way ANOVA: action_space (4 levels)

| Source | df |
|--------|-----|
| action_space | 3 |
| Error | 116 |
| Total | 119 |

### Planned Contrasts

| ID | Contrast | Tests |
|----|----------|-------|
| C1 | Linear trend (3 vs 5 vs 7 vs 9) | Monotonic dilution with action space size |
| C2 | 3-action vs 5-action | Replicate DOE-011 dilution finding (F-020) |
| C3 | 5-action vs 7-action | First novel comparison: does adding forward/backward matter? |
| C4 | 7-action vs 9-action | Speed/turn180 effect |
| C5 | 3-action vs {7+9}-action | Large vs small action space |

### Trend Analysis

- Linear, quadratic, and cubic polynomial contrasts for action_space
- Test: is the kills vs action_space relationship strictly linear (dilution proportional to 1/N_actions)?

### Predicted Kill Rate

If kills are invariant to action space (like kill_rate was in DOE-027):
- 3-action: ~43 kr (from F-035)
- 5-action: ~28 kr (predicted from DOE-025 random_5)
- 7-action: ~20 kr (predicted by dilution: kr_3 * (1/7) / (1/3))
- 9-action: ~15 kr (predicted by dilution: kr_3 * (1/9) / (1/3))

If kills DECREASE with action space, the effect is true dilution beyond rate-time compensation.

### Diagnostics

- Normality: Anderson-Darling on residuals
- Equal variance: Levene test (variance may differ by action space)
- Non-parametric fallback: Kruskal-Wallis

## Power Analysis

- Alpha = 0.05
- Expected effect: Based on DOE-011, 3-action vs 5-action showed d=0.55 (C1, p=0.003)
- With n=30 per group, 4 groups (N=120):
  - Power for detecting d=0.55 between adjacent levels: approximately 0.65
  - Power for detecting overall ANOVA effect (eta2=0.10): approximately 0.80
  - Power for linear trend across all 4 levels: approximately 0.90
- Adequate for trend detection; marginal for pairwise comparisons

## Execution Instructions for research-doe-runner

### Pre-Execution: Create New Config Files

Before running this experiment, create two new VizDoom config files:

**defend_the_line_7action.cfg**:
Copy defend_the_line_5action.cfg and add:
```
available_buttons = { MOVE_LEFT MOVE_RIGHT TURN_LEFT TURN_RIGHT ATTACK MOVE_FORWARD MOVE_BACKWARD }
```

**defend_the_line_9action.cfg**:
Copy defend_the_line_5action.cfg and add:
```
available_buttons = { MOVE_LEFT MOVE_RIGHT TURN_LEFT TURN_RIGHT ATTACK MOVE_FORWARD MOVE_BACKWARD SPEED TURN180 }
```

Place both in the VizDoom scenarios directory alongside existing .cfg files.

### Execution Steps

1. Create 7-action and 9-action .cfg files (see above)
2. For each run, use appropriate scenario config and num_actions parameter
3. All strategies: uniform random over available actions
4. Use doom_skill=3 (default) for all runs
5. No health override
6. 30 episodes per condition, same seed set for all runs
7. Follow randomized run order: R3, R1, R4, R2
8. Record kills, survival_time (ticks), compute kill_rate

### Implementation Note for Random Action Functions

For 7-action: `action = random.randint(0, 6)`
For 9-action: `action = random.randint(0, 8)`

The random function must uniformly sample from all available actions.

## Expected Outcomes

| Outcome | Probability | Implication |
|---------|------------|-------------|
| A: Monotonic decrease in kills, linear with 1/N_actions | 50% | Pure dilution effect; larger spaces punish random agents proportionally |
| B: Kills plateau after 5 actions (7-action = 5-action) | 25% | Extra movement dimensions (forward/backward) are functionally irrelevant in defend_the_line |
| C: Non-monotonic (7-action worse than expected, 9-action similar to 7) | 15% | SPEED/TURN180 provide some compensatory benefit |
| D: No effect (kills same across all action spaces) | 10% | Action space size is noise; environment determines kills regardless |

## Cross-References

- F-020: 3-action vs 5-action differentiation (DOE-011)
- F-035: 3-action ceiling ~43 kr (DOE-019, 3x replicated)
- F-062: 5-action strategies separate into tiers (DOE-025)
- F-077: Full tactical invariance in 5-action space (DOE-028)
- F-079: Movement is sole determinant (DOE-029)
- F-030: Deadly corridor floor effect at 7-action (DOE-016) -- scenario limitation
