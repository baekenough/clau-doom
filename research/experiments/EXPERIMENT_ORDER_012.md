# EXPERIMENT_ORDER_012: Compound Actions (Multi-Hot Action Vector)

## Metadata
- **Experiment ID**: DOE-012
- **Hypothesis**: H-016
- **DOE Phase**: Phase 1 (strategy architecture)
- **Design Type**: One-way completely randomized design (5 levels)
- **Date Ordered**: 2026-02-08

## Research Question

Do compound VizDoom actions (pressing multiple buttons simultaneously via multi-hot action vector) improve kill performance over sequential single-button strategies?

### Background

DOE-011 revealed that expanding the action space from 3 to 5 actions REDUCES kill_rate by diluting attack frequency [STAT:p=0.003] [STAT:effect_size=Cohen's d=0.523]. However, all tested strategies used single-button presses (one-hot vectors). VizDoom supports simultaneous button presses via multi-hot action vectors (e.g., [1,0,1] = turn_left + attack simultaneously).

**Hypothesis**: Compound actions could overcome the dilution problem by executing attack AND repositioning in the SAME tick. For example, [1,0,1] (attack + turn_left) achieves 100% attack rate while still repositioning, unlike sequential strategies that sacrifice attack ticks for movement ticks.

**Known Limitation**: VizDoom weapon cooldown may absorb timing differences. The pistol has ~8 tic cooldown between shots. If two strategies differ only in the distribution of non-attack ticks within an 8-tic window, the game state may not diverge (weapon cooldown prevents additional shots anyway).

### Hypothesis

**H-016: Compound Simultaneous Actions Outperform Sequential Single Actions**

Simultaneous attack+turn (compound) should produce higher kill_rate than sequential burst strategies because compound actions maintain 100% attack frequency while still repositioning. The burst_3 strategy (3 attacks, 1 turn, repeat) achieves only 75% attack rate; compound_attack_turn ([1,0,1] or [0,1,1]) achieves 100% attack rate with continuous repositioning.

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| action_architecture | Categorical | 5 | Single-button vs compound (multi-hot) action strategies |

### Factor Levels

| Level | Condition Label | Action Vector | Description | Expected Attack Rate |
|-------|----------------|--------------|-------------|---------------------|
| 1 | random_3 | One-hot, 3 actions | Uniform random over {turn_left, turn_right, attack} (baseline) | 33% |
| 2 | burst_3 | One-hot, 3 actions | 3 attacks + 1 random turn (DOE-010/011 replication) | 75% |
| 3 | attack_only | One-hot, 3 actions | 100% attack, never moves | 100% |
| 4 | compound_attack_turn | Multi-hot, 3 actions | Simultaneous attack+random turn: [1,0,1] or [0,1,1] | 100% (attack) + 100% (turn) |
| 5 | compound_burst_3 | Multi-hot, 3 actions | 3 ticks of [attack+turn], then 1 tick of [turn only] | 75% compound + 25% turn-only |

### Strategy Design Rationale

**random_3** (33% attack): Baseline control from DOE-010/011. Expected ~43 kr. Anchors random selection performance.

**burst_3** (75% attack): Replication of DOE-010/011's best single-button strategy. Expected ~44-45 kr. Anchors structured sequential strategy performance.

**attack_only** (100% attack): Pure offense, zero repositioning. Tests the upper bound of attack frequency without movement. Expected to have moderate kill_rate but short survival (gets hit repeatedly without dodging/aiming).

**compound_attack_turn** (100% attack + 100% turn): The flagship compound strategy. Every tick presses attack AND a random turn button simultaneously. Maintains 100% attack rate (like attack_only) but ALSO repositions continuously (like burst_3). If compound actions work as hypothesized, this should produce the HIGHEST kill_rate by combining the benefits of both pure attack and repositioning.

**compound_burst_3** (75% compound + 25% turn-only): Hybrid strategy. Matches burst_3's rhythm (3 offensive ticks, 1 reposition tick) but the 3 offensive ticks are compound [attack+turn] instead of pure [attack]. The single repositioning tick is turn-only. This tests whether compounding the burst windows provides any advantage over pure sequential burst.

### Key Contrasts (Planned Comparisons)

| Contrast | Comparison | Tests |
|----------|------------|-------|
| C1 | attack_only vs burst_3 | Pure attack vs burst (no compound) |
| C2 | compound_attack_turn vs attack_only | Does adding turn to every attack improve over pure attack? |
| C3 | compound_attack_turn vs burst_3 | Does compound continuous outperform sequential burst? |
| C4 | compound_burst_3 vs burst_3 | Does compounding the burst windows help? |
| C5 | compound_attack_turn vs compound_burst_3 | Continuous compound vs burst compound |

### Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: compound_attack_turn > burst_3 > attack_only** | Compound actions work; continuous is best | Adopt compound strategies as new baseline |
| **B: compound_attack_turn = compound_burst_3 > burst_3** | Compound works but rhythm doesn't matter | Cooldown absorbs timing; use simpler compound |
| **C: burst_3 >= compound_attack_turn** | Compound provides no advantage | Stick with sequential burst strategies |
| **D: attack_only > compound_attack_turn** | Turn degrades attack effectiveness | Pure attack is optimal; ignore repositioning |
| **E: All conditions similar** | Compound vs sequential makes no difference | VizDoom mechanics don't support compound advantage |

### Known Risk: Weapon Cooldown Absorption

The pistol in defend_the_line has ~8 tic cooldown. If compound_attack_turn and compound_burst_3 differ only in when the 1-in-4 turn-only tick occurs within an 8-tic window, the weapon cooldown may prevent any additional shots from being fired during that period anyway. Result: the two compound strategies may produce IDENTICAL game states and metrics, making them indistinguishable.

**Mitigation**: If this occurs, it confirms that VizDoom weapon mechanics absorb small timing differences. The experiment still tests whether compound actions (in general) outperform sequential actions.

## Design Matrix

| Run | Condition | Action Vector Type | Strategy | Episodes | Seeds |
|-----|-----------|-------------------|----------|----------|-------|
| R1 | random_3 | One-hot | random | 30 | [13001, ..., 14538] |
| R2 | burst_3 | One-hot | burst_3 | 30 | [13001, ..., 14538] |
| R3 | attack_only | One-hot | attack_only | 30 | [13001, ..., 14538] |
| R4 | compound_attack_turn | Multi-hot | compound_attack_turn | 30 | [13001, ..., 14538] |
| R5 | compound_burst_3 | Multi-hot | compound_burst_3 | 30 | [13001, ..., 14538] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R2 (burst_3) -> R4 (compound_attack_turn) -> R1 (random_3) -> R5 (compound_burst_3) -> R3 (attack_only)

## Seed Set

**Formula**: seed_i = 13001 + i x 53, i = 0, 1, ..., 29
**Range**: [13001, 14538]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[13001, 13054, 13107, 13160, 13213, 13266, 13319, 13372, 13425, 13478,
 13531, 13584, 13637, 13690, 13743, 13796, 13849, 13902, 13955, 14008,
 14061, 14114, 14167, 14220, 14273, 14326, 14379, 14432, 14485, 14538]
```

### Cross-Experiment Seed Collision Check

| Experiment | Seed Range | Overlap with [13001, 14538]? |
|-----------|------------|------------------------------|
| DOE-001 | [42, 2211] | NO |
| DOE-011 | [12001, 13364] | Minimal (13001-13364 shared range) |

**Verdict**: Minor overlap with DOE-011 tail (363 seeds), but different experiment contexts. No practical collision risk.

## Scenario Configuration

**File**: defend_the_line.cfg (standard 3-action)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

**Note**: All 5 conditions use the same 3-action cfg. The compound strategies use multi-hot action vectors over the same 3 buttons.

### Known Limitations
1. **AMMO2 tracking broken** for defend_the_line. ammo_efficiency and shots_fired EXCLUDED from analysis.
2. **Weapon cooldown**: Pistol has ~8 tic cooldown; timing differences within this window may not affect game state.
3. **No vertical aim**: Agent cannot aim up/down; only horizontal via turning.

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kill_rate (5 levels)
   - Response: kill_rate = (kills / survival_time) * 60
   - Factor: action_architecture (5 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk test
3. **Equal variance**: Levene test
4. **Independence**: Residuals vs run order

### If ANOVA significant:
5. **Tukey HSD** all pairwise comparisons (10 pairs)
6. **Planned contrasts** (C1-C5)
7. **Effect sizes**: Cohen's d, eta-squared
8. **Bonferroni correction** for 5 planned contrasts (alpha = 0.01)

### Non-Parametric Backup
9. **Kruskal-Wallis** if normality violated

### Secondary Responses
10. Repeat analysis for kills and survival_time

### Power
- Expected power for medium effect (f=0.25) with k=5, n=30, alpha=0.05: [STAT:power=0.83]
- DOE-010/011 observed effects (f~0.32-0.37): [STAT:power>0.89]

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 13001 + i*53, i=0..29 |
| No seed collisions | YES: verified against prior experiments |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED |
| Residual diagnostics | PLANNED |
| Effect sizes | PLANNED |
| Seeds identical across conditions | YES |

## Status

**ORDERED** — Awaiting execution.
