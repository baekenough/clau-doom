# EXPERIMENT_ORDER_011: Expanded Action Space (5-Action) Strategy Differentiation

## Metadata
- **Experiment ID**: DOE-011
- **Hypothesis**: H-015
- **DOE Phase**: Phase 1 (architecture exploration)
- **Design Type**: One-way completely randomized design (5 levels)
- **Date Ordered**: 2026-02-08

## Research Question

Does expanding the action space from 3 actions (turn_left, turn_right, attack) to 5 actions (turn_left, turn_right, move_left, move_right, attack) enable meaningful strategy differentiation on defend_the_line?

### Background

DOE-010 established a critical finding (F-018, F-019): with the default 3-action space in defend_the_line.cfg, random action selection performs as well as ANY structured strategy (~43 kr). Burst strategies match random; sweep oscillation matches L0_only (~39 kr). The 3-action space appears to be the ceiling.

**Critical Discovery**: The actions labeled MOVE_LEFT/MOVE_RIGHT in VizDoomBridge code are actually mapped to TURN_LEFT/TURN_RIGHT in the defend_the_line.cfg. The scenario has always been a turn-only, zero-physical-movement environment. This means:

- L0_only "tunnel vision" = agent never turns to face enemies at different positions on the line
- "Random lateral movement" = random turning = scanning the enemy line randomly
- sweep_lr oscillation = rapid alternating turn direction = view jitters without scanning
- burst strategies = concentrated fire then turn = acquire-fire-acquire cycle

**Implication**: defend_the_line has NO physical movement buttons. The agent is stationary and can only rotate and fire. Adding MOVE_LEFT/MOVE_RIGHT (true strafing) to the action space would:

1. Give the agent the ability to physically dodge incoming fire (currently impossible)
2. Create a fundamentally richer strategy space with two independent degrees of freedom (aim direction via turning, position via strafing)
3. Enable intelligent strategies that separate aiming from dodging, potentially differentiating from random

### Hypothesis

**H-015: Expanded Action Space (Turn+Strafe) Enables Strategy Differentiation**

With only 3 actions (turn_left, turn_right, attack), random selection achieves ~43 kr because turning is inherently a scanning mechanism where random is near-optimal. With 5 actions (add move_left, move_right for strafing), random wastes ~40% of ticks on strafing instead of attack/turn. Intelligent strategies that coordinate aiming (turn), dodging (strafe), and attack timing can outperform random in the expanded space.

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| action_strategy | Categorical | 5 | Action selection architecture in 3- or 5-action space |

### Factor Levels

| Level | Condition Label | Action Space | Description | Expected Attack Rate |
|-------|----------------|-------------|-------------|---------------------|
| 1 | random_3 | 3-action | Uniform random over {turn_left, turn_right, attack} | 33% |
| 2 | random_5 | 5-action | Uniform random over {turn_left, turn_right, move_left, move_right, attack} | 20% |
| 3 | turn_burst_3 | 3-action | 3 attacks then 1 random turn (DOE-010 burst_3 replication) | 75% |
| 4 | strafe_burst_3 | 5-action | 3 attacks then 1 random strafe (move_left or move_right) | 75% |
| 5 | smart_5 | 5-action | Coordinated: turn to scan, attack on sight, strafe to dodge between kills | ~60% (adaptive) |

### Strategy Design Rationale

**random_3** (3-action, 33% attack): Replication control from DOE-010. Expected ~43 kr based on F-019 Group A performance. Serves as the proven baseline for the existing action space.

**random_5** (5-action, 20% attack): Direct test of action space dilution. With 5 equal-probability actions, only 20% of ticks are attacks (vs 33% for random_3). The remaining 40% is split between turning (useful for aiming) and strafing (useful for dodging but not aiming). If random_5 performs worse than random_3, it confirms that the extra actions are wasted under random selection. The performance DROP from random_3 to random_5 quantifies the "dilution tax" of expanding the action space.

**turn_burst_3** (3-action, 75% attack): Replication of DOE-010's burst_3 strategy. Expected ~44 kr based on DOE-010 results. This anchors the 3-action space performance and validates cross-experiment comparability under the modified cfg.

**strafe_burst_3** (5-action, 75% attack): Identical burst pattern to turn_burst_3, but the single repositioning move between burst windows is a strafe (move_left or move_right) instead of a turn. This isolates the value of dodging vs turning between attack bursts. If strafe_burst_3 outperforms turn_burst_3, strafing provides survival benefit. If they are equivalent, physical movement adds no value in this scenario.

**smart_5** (5-action, ~60% attack): The flagship test condition. A coordinated strategy that exploits both degrees of freedom:
- **Aiming phase**: Turn toward nearest enemy cluster (1-2 ticks of turning)
- **Attack phase**: Fire at current target (3 ticks)
- **Dodge phase**: Strafe left or right (1 tick) to avoid incoming fire
- **Cycle**: aim-attack-dodge repeats
- The key innovation is that turning is used ONLY for aiming (not dodging) and strafing is used ONLY for dodging (not aiming). This separation of concerns should be impossible to achieve with random action selection.

### Key Contrasts (Planned Comparisons)

| Contrast | Comparison | Tests |
|----------|------------|-------|
| C1 | random_3 vs random_5 | Action space dilution effect |
| C2 | turn_burst_3 vs strafe_burst_3 | Value of strafing vs turning between bursts |
| C3 | random_5 vs smart_5 | Strategy differentiation in 5-action space |
| C4 | random_3 vs smart_5 | Cross-space comparison (best of each) |
| C5 | {random_5, strafe_burst_3, smart_5} vs {random_3, turn_burst_3} | 5-action overall vs 3-action overall |

### Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: smart_5 > random_5 > random_3** | Expanded space + intelligent strategy = optimal | Phase 2 RSM on smart_5 parameters |
| **B: smart_5 > random_3 > random_5** | Intelligence overcomes dilution; raw randomness does not | Focus on strategy refinement, not action space |
| **C: random_3 >= smart_5 > random_5** | Expanded space hurts, even with intelligence | 3-action space is sufficient; optimize within it |
| **D: All conditions similar** | Neither action space nor strategy matters | Scenario ceiling reached; pivot to different scenario |
| **E: strafe_burst_3 > turn_burst_3 >> random_5** | Dodging is valuable, but only with concentrated fire | Develop dodge-during-pause strategies |

## Design Matrix

| Run | Condition | Action Space | Strategy | Episodes | Seeds |
|-----|-----------|-------------|----------|----------|-------|
| R1 | random_3 | 3-action (standard cfg) | random | 30 | [12001, ..., 13364] |
| R2 | random_5 | 5-action (modified cfg) | random | 30 | [12001, ..., 13364] |
| R3 | turn_burst_3 | 3-action (standard cfg) | burst_3 | 30 | [12001, ..., 13364] |
| R4 | strafe_burst_3 | 5-action (modified cfg) | strafe_burst_3 | 30 | [12001, ..., 13364] |
| R5 | smart_5 | 5-action (modified cfg) | smart_5 | 30 | [12001, ..., 13364] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R3 (turn_burst_3) -> R5 (smart_5) -> R1 (random_3) -> R4 (strafe_burst_3) -> R2 (random_5)

## Seed Set

**Formula**: seed_i = 12001 + i x 47, i = 0, 1, ..., 29
**Range**: [12001, 13364]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[12001, 12048, 12095, 12142, 12189, 12236, 12283, 12330, 12377, 12424,
 12471, 12518, 12565, 12612, 12659, 12706, 12753, 12800, 12847, 12894,
 12941, 12988, 13035, 13082, 13129, 13176, 13223, 13270, 13317, 13364]
```

### Cross-Experiment Seed Collision Check

| Experiment | Seed Range | Formula | Overlap with [12001, 13364]? |
|-----------|------------|---------|------------------------------|
| DOE-001 | [42, 2211] | 42 + i*31, i=0..69 | NO |
| DOE-002 | [1337, 1830] | 1337 + i*17, i=0..29 | NO |
| DOE-005 | [2501, 3168] | 2501 + i*23, i=0..29 | NO |
| DOE-006 | [3501, 4342] | 3501 + i*29, i=0..29 | NO |
| DOE-007 | [4501, 5400] | 4501 + i*31, i=0..29 | NO |
| DOE-008 | [6001, 7074] | 6001 + i*37, i=0..29 | NO |
| DOE-009 | [8001, 9190] | 8001 + i*41, i=0..29 | NO |
| DOE-010 | [10001, 11248] | 10001 + i*43, i=0..29 | NO |

**Verdict**: Zero collisions with all prior experiments.

## Scenario Configuration

### Standard defend_the_line.cfg (for 3-action conditions: R1, R3)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

### Modified defend_the_line_5action.cfg (for 5-action conditions: R2, R4, R5)
```
available_buttons = { TURN_LEFT TURN_RIGHT MOVE_LEFT MOVE_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

**IMPORTANT**: The modified cfg must be created before execution. Only the `available_buttons` line changes. All other scenario parameters (map, enemies, spawn, timeout, rewards) remain identical to ensure controlled comparison.

### Known Limitations
1. **AMMO2 tracking broken** for defend_the_line (enemy ammo drops increase AMMO2). ammo_efficiency and shots_fired are EXCLUDED from analysis.
2. **No aim control**: Agent cannot aim up/down; only horizontal aiming via turning. Enemies on defend_the_line are at a fixed elevation.
3. **Movement physics**: Strafing speed and turning speed may differ, affecting relative displacement per tick. This is a VizDoom engine property, not controllable.
4. **smart_5 implementation complexity**: The aim-attack-dodge cycle requires enemy position awareness from game state. If the VizDoom API does not expose enemy positions, the strategy may need to use a simpler heuristic (e.g., turn if no recent kill, strafe periodically).

## Infrastructure Prerequisites

Before execution, the following changes are required:

### 1. Modified Config File
Create `defend_the_line_5action.cfg` with MOVE_LEFT and MOVE_RIGHT added to available_buttons. Copy from standard defend_the_line.cfg and add two buttons.

### 2. VizDoomBridge Update
The Python VizDoomBridge must support NUM_ACTIONS=5 for the 5-action conditions. Currently it supports NUM_ACTIONS=3. The bridge should:
- Accept NUM_ACTIONS as a parameter (or detect from cfg)
- Map action index 0-4 to the 5 buttons in order
- Handle both 3-action and 5-action scenarios in the same session (R1/R3 use 3-action, R2/R4/R5 use 5-action)

### 3. New Strategy Functions
Four new action functions are needed (random_3 and burst_3 already exist from DOE-010):

**random_5**: Identical to random_3 but with range 0-4 instead of 0-2.

**strafe_burst_3**: Like burst_3, but the repositioning move after each burst selects from {move_left, move_right} (action indices 2 or 3) instead of {turn_left, turn_right} (indices 0 or 1).

**smart_5**: The coordinated strategy requires state tracking:
```python
class Smart5Action:
    def __init__(self):
        self.phase = "attack"     # attack, turn, dodge
        self.attack_count = 0
        self.turn_count = 0
        self.last_kills = 0

    def get_action(self, game_state):
        current_kills = game_state.killcount

        if self.phase == "attack":
            self.attack_count += 1
            if self.attack_count >= 3:
                # After 3 attacks, check if we got a kill
                if current_kills > self.last_kills:
                    # Got a kill — dodge to avoid return fire
                    self.phase = "dodge"
                    self.last_kills = current_kills
                else:
                    # No kill — turn to find enemy
                    self.phase = "turn"
                self.attack_count = 0
            return ATTACK  # action index 4

        elif self.phase == "turn":
            self.turn_count += 1
            if self.turn_count >= 2:
                self.phase = "attack"
                self.turn_count = 0
            return random.choice([TURN_LEFT, TURN_RIGHT])  # index 0 or 1

        elif self.phase == "dodge":
            self.phase = "attack"
            return random.choice([MOVE_LEFT, MOVE_RIGHT])  # index 2 or 3
```

### 4. Execution Note: Cfg Switching
Runs R1 and R3 use the standard 3-action cfg. Runs R2, R4, R5 use the 5-action cfg. The doe-runner must switch between cfgs between runs. This can be done by:
- Passing the cfg filename as a parameter to VizDoomBridge
- Or having two separate scenario configurations and switching at run boundary

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kill_rate (5 levels)
   - Response: kill_rate = (kills / survival_time) * 60 (kills per minute)
   - Factor: action_strategy (5 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk test on ANOVA residuals
3. **Equal variance**: Levene test across groups
4. **Independence**: Residuals vs run order plot

### If ANOVA significant (p < 0.05):
5. **Tukey HSD** all pairwise comparisons (10 pairs)
6. **Planned contrasts** (C1-C5 as defined above):
   - C1: random_3 vs random_5 (dilution effect)
   - C2: turn_burst_3 vs strafe_burst_3 (strafe value)
   - C3: random_5 vs smart_5 (strategy differentiation in 5-action)
   - C4: random_3 vs smart_5 (cross-space best-vs-best)
   - C5: 5-action group vs 3-action group (overall space effect)
7. **Effect sizes**: Cohen's d for pairwise, eta-squared for overall
8. **Bonferroni correction** for the 5 planned contrasts (adjusted alpha = 0.01)

### Non-Parametric Backup
9. **Kruskal-Wallis** if normality violated, followed by Dunn's test with Bonferroni correction

### Secondary Responses
10. Repeat analysis for kills and survival_time as secondary responses

### Power
- Expected power for medium effect (f=0.25) with k=5, n=30, alpha=0.05: [STAT:power=0.83]
- Expected power for large effect (f=0.40) with k=5, n=30, alpha=0.05: [STAT:power=0.99]
- DOE-010 observed effect (f=0.37): [STAT:power=0.97]
- DOE-011 anticipates LARGER effects due to the dilution tax on random_5, so power should be excellent

## Cross-Experiment Validation

### Replication Checks
Two conditions replicate DOE-010 strategies on the same action space:
- **random_3** should replicate DOE-010's random condition (~42 kr, SD~6.7)
- **turn_burst_3** should replicate DOE-010's burst_3 condition (~44 kr, SD~6.4)

If these differ by more than 1 pooled SD from DOE-010 values, the experiment should be flagged for investigation before proceeding with the novel conditions.

### Cross-Experiment Contrast
If both replication checks pass, the DOE-011 novel conditions (random_5, strafe_burst_3, smart_5) can be interpreted against the established DOE-010 baseline with higher confidence.

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 12001 + i*47, i=0..29 |
| No seed collisions | YES: verified against DOE-001 through DOE-010 |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, equal variance, independence |
| Effect sizes | PLANNED: Cohen's d (pairwise), eta-squared (overall) |
| Non-parametric backup | PLANNED: Kruskal-Wallis if normality violated |
| Seeds identical across conditions | YES: all 5 conditions use the same 30 seeds |

## Execution Checklist

Before execution, verify:
- [ ] defend_the_line_5action.cfg created and tested
- [ ] VizDoomBridge supports 5-action mode (NUM_ACTIONS=5)
- [ ] random_5 action function implemented and tested
- [ ] strafe_burst_3 action function implemented and tested
- [ ] smart_5 action function implemented and tested
- [ ] random_3 action function loads correct 3-action cfg
- [ ] turn_burst_3 action function loads correct 3-action cfg
- [ ] Cfg switching between runs verified (3-action vs 5-action)
- [ ] Seed set generated and logged
- [ ] DuckDB experiment table schema supports DOE-011 columns

## Status

**ORDERED** — Awaiting infrastructure changes (modified cfg, VizDoomBridge update, new action functions) before execution.
