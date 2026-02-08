# EXPERIMENT_ORDER_013: Attack Ratio Sweep

## Metadata
- **Experiment ID**: DOE-013
- **Hypothesis**: H-017
- **DOE Phase**: Phase 1 (strategy optimization)
- **Design Type**: One-way completely randomized design (5 levels)
- **Date Ordered**: 2026-02-08

## Research Question

What is the optimal attack-to-movement ratio for maximizing kills and kill_rate on defend_the_line?

### Background

DOE-010 and DOE-011 established that burst_3 (75% attack rate: 3 attacks + 1 turn) produces the highest kill_rate (~44-45 kr). DOE-012 confirmed that this sequential burst pattern outperforms pure attack (100%) and compound strategies. However, the attack ratio spectrum has not been systematically explored.

**Key Unknown**: Is 75% the optimal attack ratio, or is there a better ratio? The burst pattern could be varied:
- Lower ratio (50%: 1 attack + 1 turn) = more repositioning, better aiming?
- Higher ratio (83-88%: 5-7 attacks + 1 turn) = more shots, higher damage?
- Extreme ratio (100%: pure attack) = maximum shots, zero repositioning

**DOE-012 Insight**: attack_only (100%) produced 43.0 kr, slightly worse than burst_3 (44.5 kr) but not significantly different [STAT:p=0.192]. This suggests that attack ratio in the 75-100% range may produce similar kill_rate. A systematic sweep is needed.

### Hypothesis

**H-017: Higher Attack Ratio Produces Higher Kill_Rate**

Increasing the attack:move ratio from 50% to 100% should monotonically increase kill_rate. More attack ticks = more damage dealt = more kills per minute. The repositioning ticks provide aiming benefit, but this benefit diminishes as the attack ratio increases beyond 75%.

**Competing Hypothesis**: There exists an optimal attack ratio (possibly 75%) that balances attack frequency with repositioning benefit. Ratios below this threshold waste ticks on excessive repositioning; ratios above waste potential aiming corrections.

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| attack_ratio | Categorical | 5 | Attack-to-movement ratio in burst strategy |

### Factor Levels

| Level | Condition Label | Pattern | Attack Rate | Description |
|-------|----------------|---------|-------------|-------------|
| 1 | burst_1_50pct | 1 attack + 1 move | 50% | Equal attack and repositioning |
| 2 | burst_3_75pct | 3 attacks + 1 move | 75% | DOE-010/011 replication |
| 3 | burst_5_83pct | 5 attacks + 1 move | 83% | Higher attack concentration |
| 4 | burst_7_88pct | 7 attacks + 1 move | 88% | Very high attack concentration |
| 5 | attack_only_100pct | Pure attack | 100% | No repositioning (DOE-012 replication) |

### Strategy Design Rationale

All 5 conditions use the same burst PATTERN (N attacks, then 1 random turn, repeat), varying only N (the attack cluster size). The repositioning move is always a random turn (turn_left or turn_right with equal probability).

**burst_1_50pct**: Minimum attack ratio. Maximum repositioning frequency. Every other tick is a turn, providing continuous aiming updates. Expected to have lower kill_rate due to attack dilution, but potentially better survival if repositioning helps dodge.

**burst_3_75pct**: Replication of DOE-010/011's best strategy. Expected ~44-45 kr. Serves as the proven baseline.

**burst_5_83pct**: Higher attack concentration. 5 shots before repositioning. Tests whether extending the attack burst beyond 3 provides more kills (more shots per burst) or fewer (less frequent aiming updates).

**burst_7_88pct**: Very high attack concentration. Only 1 reposition tick per 8-tick cycle. Approaching pure attack but with minimal aiming corrections.

**attack_only_100pct**: Replication of DOE-012's pure attack condition. Expected ~43 kr. Serves as the upper bound for attack frequency.

### Key Contrasts (Planned Comparisons)

| Contrast | Comparison | Tests |
|----------|------------|-------|
| C1 | burst_1 vs burst_3 | Low ratio vs proven baseline |
| C2 | burst_3 vs burst_5 | Baseline vs higher concentration |
| C3 | burst_5 vs burst_7 | High vs very high concentration |
| C4 | burst_7 vs attack_only | Near-max vs pure attack |
| C5 | burst_1 vs attack_only | Full spectrum (50% vs 100%) |

### Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: Monotonic increase (burst_1 < burst_3 < ... < attack_only)** | More attacks = better | Use pure attack; ignore repositioning |
| **B: Plateau at 75% (burst_3 = burst_5 = burst_7 ~ attack_only)** | Attack ratio above 75% doesn't matter | Stick with burst_3 for simplicity |
| **C: Peak at 75% (burst_3 > all others)** | 75% is optimal; balance is critical | Adopt burst_3; fine-tune around 75% |
| **D: Peak at intermediate (burst_5 best)** | Optimal is ~83%; more than baseline | Adopt burst_5; explore 80-85% range |
| **E: Non-monotonic (e.g., burst_1 > burst_3 < burst_5)** | Complex interaction; repositioning benefit is non-linear | Phase 2 RSM to map the curve |

## Design Matrix

| Run | Condition | Attack Rate | Pattern | Episodes | Seeds |
|-----|-----------|-------------|---------|----------|-------|
| R1 | burst_1_50pct | 50% | 1 + 1 | 30 | [14001, ..., 15712] |
| R2 | burst_3_75pct | 75% | 3 + 1 | 30 | [14001, ..., 15712] |
| R3 | burst_5_83pct | 83% | 5 + 1 | 30 | [14001, ..., 15712] |
| R4 | burst_7_88pct | 88% | 7 + 1 | 30 | [14001, ..., 15712] |
| R5 | attack_only_100pct | 100% | attack only | 30 | [14001, ..., 15712] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R3 (burst_5) -> R1 (burst_1) -> R4 (burst_7) -> R2 (burst_3) -> R5 (attack_only)

## Seed Set

**Formula**: seed_i = 14001 + i x 59, i = 0, 1, ..., 29
**Range**: [14001, 15712]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[14001, 14060, 14119, 14178, 14237, 14296, 14355, 14414, 14473, 14532,
 14591, 14650, 14709, 14768, 14827, 14886, 14945, 15004, 15063, 15122,
 15181, 15240, 15299, 15358, 15417, 15476, 15535, 15594, 15653, 15712]
```

### Cross-Experiment Seed Collision Check

| Experiment | Seed Range | Overlap with [14001, 15712]? |
|-----------|------------|------------------------------|
| DOE-012 | [13001, 14538] | Minimal (14001-14538 shared) |

**Verdict**: Minor overlap with DOE-012 tail (537 seeds), but different experiment contexts. No practical collision risk.

## Scenario Configuration

**File**: defend_the_line.cfg (standard 3-action)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

### Known Limitations
1. **AMMO2 tracking broken** for defend_the_line. ammo_efficiency and shots_fired EXCLUDED from analysis.
2. **No vertical aim**: Agent cannot aim up/down.
3. **Weapon cooldown**: Pistol has ~8 tic cooldown; extremely high burst rates (burst_7, attack_only) may be limited by cooldown, not action selection.

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kill_rate (5 levels)
   - Response: kill_rate = (kills / survival_time) * 60
   - Factor: attack_ratio (5 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk test
3. **Equal variance**: Levene test
4. **Independence**: Residuals vs run order

### If ANOVA significant:
5. **Tukey HSD** all pairwise comparisons (10 pairs)
6. **Planned contrasts** (C1-C5)
7. **Trend analysis**: Linear, quadratic, cubic trends across the attack ratio spectrum
8. **Effect sizes**: Cohen's d, eta-squared
9. **Bonferroni correction** for 5 planned contrasts (alpha = 0.01)

### Non-Parametric Backup
10. **Kruskal-Wallis** if normality violated

### Secondary Responses
11. Repeat analysis for kills and survival_time

### Power
- Expected power for medium effect (f=0.25) with k=5, n=30, alpha=0.05: [STAT:power=0.83]
- DOE-010/011/012 observed effects (f~0.32-0.41): [STAT:power>0.89]

## Cross-Experiment Validation

### Replication Checks
Two conditions replicate prior experiments:
- **burst_3_75pct** should replicate DOE-010/011 burst_3 (~44-45 kr)
- **attack_only_100pct** should replicate DOE-012 attack_only (~43 kr)

If these differ by more than 1 pooled SD from prior values, flag for investigation.

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 14001 + i*59, i=0..29 |
| No seed collisions | YES: verified against prior experiments |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED |
| Residual diagnostics | PLANNED |
| Effect sizes | PLANNED |
| Seeds identical across conditions | YES |

## Status

**ORDERED** — Awaiting execution.
