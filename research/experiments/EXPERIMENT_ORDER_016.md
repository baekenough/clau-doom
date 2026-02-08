# EXPERIMENT_ORDER_016: Deadly Corridor Feasibility

## Metadata
- **Experiment ID**: DOE-016
- **Hypothesis**: H-020
- **DOE Phase**: Phase 1 (scenario exploration)
- **Design Type**: One-way completely randomized design (5 levels)
- **Date Ordered**: 2026-02-08

## Research Question

Can simple heuristic agents achieve meaningful kill counts on deadly_corridor.cfg? This scenario features a narrow corridor with multiple enemies requiring forward navigation and combat. If simple agents perform above floor levels, deadly_corridor could serve as a navigation-focused evaluation scenario.

### Background

All prior experiments used defend_the_line.cfg where the agent is stationary and only rotates to aim. deadly_corridor.cfg introduces a fundamentally different challenge: the agent must navigate forward through a corridor of enemies. This requires coordinated movement and combat, potentially beyond the capabilities of simple heuristic strategies.

**deadly_corridor.cfg characteristics**:
- 7 available buttons: MOVE_LEFT, MOVE_RIGHT, ATTACK, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT
- Multiple enemies distributed along a corridor
- timeout=2100 ticks (~60s)
- skill=5 (highest difficulty)
- Requires forward navigation to engage enemies

### Hypothesis

**H-020: Simple Agents Can Function on deadly_corridor**

If at least one simple heuristic strategy (e.g., forward_attack cycling) achieves meaningful kill counts (>3 kills per episode on average), then deadly_corridor can be used for navigation-focused agent evaluation. If all strategies produce floor effects (~0 kills), the scenario is too complex for current agent architecture.

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| action_strategy | Categorical | 5 | Action selection heuristic for deadly_corridor |

### Factor Levels

| Level | Condition Label | Description | Expected Attack Rate |
|-------|----------------|-------------|---------------------|
| 1 | dc_random_7 | Uniform random over 7 actions | 14% |
| 2 | dc_forward_attack | 3 attacks + 1 move_forward cycle | 75% |
| 3 | dc_burst_3_turn | 3 attacks + 1 random turn | 75% |
| 4 | dc_attack_only | 100% attack | 100% |
| 5 | dc_adaptive | State-dependent: forward if health>50, attack if enemy visible | ~50% |

### Strategy Design Rationale

**dc_random_7**: Baseline random selection over all 7 actions. With 14% attack rate, this should underperform attack-focused strategies.

**dc_forward_attack**: Simple navigation strategy. Cycle of 3 attacks followed by 1 move_forward to progress through corridor. Tests if forward movement enables engagement.

**dc_burst_3_turn**: Adapted burst strategy from defend_the_line experiments. 3 attacks + 1 random turn. Tests if rotation-based aiming works without navigation.

**dc_attack_only**: Pure attack strategy. Agent stands still and fires continuously. Tests if corridor enemies approach the agent.

**dc_adaptive**: Conditional logic based on game state. Move forward when healthy, attack when enemy detected. Requires state awareness.

### Key Contrasts

| Contrast | Comparison | Tests |
|----------|------------|-------|
| C1 | dc_forward_attack vs dc_attack_only | Value of forward navigation |
| C2 | dc_forward_attack vs dc_burst_3_turn | Forward movement vs turning |
| C3 | dc_random_7 vs dc_adaptive | Random vs state-dependent selection |
| C4 | All conditions vs floor (0 kills) | Any strategy above floor? |

### Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: dc_forward_attack >> dc_attack_only** | Navigation is essential | Develop navigation-focused agents |
| **B: All strategies ~0 kills** | Floor effect, scenario too hard | Retire deadly_corridor from pipeline |
| **C: dc_adaptive >> all others** | State-dependent logic needed | Focus on adaptive strategies |

## Design Matrix

| Run | Condition | Strategy | Episodes | Seeds |
|-----|-----------|----------|----------|-------|
| R1 | dc_random_7 | random_7 | 30 | [17001, ..., 19056] |
| R2 | dc_forward_attack | forward_attack | 30 | [17001, ..., 19056] |
| R3 | dc_burst_3_turn | burst_3_turn | 30 | [17001, ..., 19056] |
| R4 | dc_attack_only | attack_only | 30 | [17001, ..., 19056] |
| R5 | dc_adaptive | adaptive | 30 | [17001, ..., 19056] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R3 (dc_burst_3_turn) -> R1 (dc_random_7) -> R5 (dc_adaptive) -> R2 (dc_forward_attack) -> R4 (dc_attack_only)

## Seed Set

**Formula**: seed_i = 17001 + i x 71, i = 0, 1, ..., 29
**Range**: [17001, 19056]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[17001, 17072, 17143, 17214, 17285, 17356, 17427, 17498, 17569, 17640,
 17711, 17782, 17853, 17924, 17995, 18066, 18137, 18208, 18279, 18350,
 18421, 18492, 18563, 18634, 18705, 18776, 18847, 18918, 18989, 19056]
```

## Scenario Configuration

### deadly_corridor.cfg (all runs)
```
available_buttons = { MOVE_LEFT MOVE_RIGHT ATTACK MOVE_FORWARD MOVE_BACKWARD TURN_LEFT TURN_RIGHT }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # ~60s at 35 fps
doom_skill_level = 5  # Nightmare difficulty
```

### Known Limitations

1. **Navigation complexity**: Requires coordinated forward movement and combat, potentially beyond heuristic capability.
2. **Narrow corridor**: Limited maneuvering space may reduce survival time.
3. **High difficulty**: skill=5 means enemies deal maximum damage.
4. **7-action space**: Larger action space dilutes random attack rate to 14% (vs 33% for 3-action defend_the_line).

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kill_rate (5 levels)
   - Response: kill_rate = (kills / survival_time) * 60
   - Factor: action_strategy (5 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk test on ANOVA residuals
3. **Equal variance**: Levene test across groups
4. **Independence**: Residuals vs run order plot

### If ANOVA significant (p < 0.05):
5. **Tukey HSD** all pairwise comparisons
6. **Planned contrasts** (C1-C4 as defined above)
7. **Effect sizes**: Cohen's d for pairwise, eta-squared for overall

### Non-Parametric Backup
8. **Kruskal-Wallis** if normality violated

### Floor Effect Test
9. **One-sample t-test** vs hypothetical mean of 0 kills for each condition

### Secondary Responses
10. Repeat analysis for kills and survival_time

## Infrastructure Prerequisites

Before execution, verify:
- [ ] deadly_corridor.cfg available and configured
- [ ] VizDoomBridge supports 7-action mode
- [ ] All 5 action functions implemented (random_7, forward_attack, burst_3_turn, attack_only, adaptive)
- [ ] Adaptive strategy has access to game state (health, enemy visibility)
- [ ] Seed set generated and logged

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 17001 + i*71, i=0..29 |
| No seed collisions | YES: verified against DOE-001 through DOE-015 |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, equal variance, independence |
| Effect sizes | PLANNED: Cohen's d, eta-squared |
| Seeds identical across conditions | YES: all 5 conditions use the same 30 seeds |

## Execution Checklist

Before execution, verify:
- [ ] deadly_corridor.cfg configured with skill=5
- [ ] VizDoomBridge supports 7-action space
- [ ] forward_attack action function implemented
- [ ] adaptive strategy has game state access
- [ ] All other strategies ready for 7-action space
- [ ] DuckDB schema supports DOE-016 columns

## Status

**ORDERED** — Ready for execution.
