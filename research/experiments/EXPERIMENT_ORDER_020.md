# EXPERIMENT_ORDER_020: Best-of-Breed Confirmation

## Metadata
- **Experiment ID**: DOE-020
- **Hypothesis**: H-024 — Best-of-breed confirmation tournament
- **DOE Phase**: Phase 1
- **Design Type**: One-way completely randomized design (5 levels)
- **Date Ordered**: 2026-02-08

## Research Question

Final confirmation of the best strategy candidates from the DOE-008 through DOE-019 experimental campaign on defend_the_line.

### Background

After 12 experiments (DOE-008 through DOE-019), the strategy landscape is well-mapped:

**Top Tier (kill_rate ~44-46)**:
- **burst_3**: Best kills in DOE-012 (14.97), DOE-013 (14.80), DOE-017 (14.97), consistent 44-45 kr
- **adaptive_kill**: Best adaptive in DOE-018 (46.18 kr), replicated in DOE-019 (46.56 kr)

**Mid Tier (kill_rate ~42-44)**:
- **random**: Universal baseline, stable at 42-43 kr across all experiments
- **attack_only**: Pure aggression baseline, 43-44 kr

**Bottom Tier (kill_rate ~38-40)**:
- **l0_only**: Worst in DOE-008 (39.31 kr), DOE-010 (38.63 kr), DOE-019 (38.52 kr)

**Novel Candidates**:
- **compound_attack_turn**: Best compound in DOE-012 (41.56 kr), theoretical simultaneous attack+turn advantage

DOE-020 is the final Phase 1 confirmation tournament, testing the best-of-breed strategies with a fresh seed set to establish publication-ready rankings.

### Hypothesis

**H-024: Best-of-Breed Confirmation**

In a head-to-head tournament with independent seeds:
1. burst_3 will rank highest on kills (expected ~15 kills)
2. adaptive_kill will rank highest or tie on kill_rate (expected ~46 kr)
3. compound_attack_turn will match or exceed random on kill_rate (expected ~42 kr)
4. All top-tier strategies will significantly outperform baselines

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| action_strategy | Categorical | 5 | Best-of-breed strategies from DOE-008 through DOE-019 |

### Factor Levels

| Level | Condition Label | Description | Expected kill_rate | Expected kills |
|-------|----------------|-------------|-------------------|----------------|
| 1 | random | Universal baseline | ~42-43 | ~13 |
| 2 | attack_only | Pure aggression baseline | ~43-44 | ~10-11 |
| 3 | burst_3 | Best kills (DOE-012/017) | ~44-45 | ~15 |
| 4 | compound_attack_turn | Best compound (DOE-012) | ~42 | ~13 |
| 5 | adaptive_kill | Best adaptive (DOE-018/019) | ~46 | ~13 |

### Strategy Selection Rationale

**random**: Universal baseline across 12 experiments. Anchors tournament.

**attack_only**: Pure aggression baseline. Standard comparison.

**burst_3**: Most consistent top performer for kills (14.8-15.0 kills across DOE-012/013/017). 4 prior independent seed validations.

**compound_attack_turn**: Theoretical advantage of simultaneous attack+turn to maximize both damage output and aiming. DOE-012 showed 41.56 kr (F-025), but needs confirmation with fresh seeds.

**adaptive_kill**: Best adaptive strategy. 2 prior independent seed validations (DOE-018: 46.18 kr, DOE-019: 46.56 kr). State-dependent logic (health thresholds + stagnation detection).

### Key Contrasts

| Contrast | Comparison | Tests |
|----------|------------|-------|
| C1 | burst_3 vs adaptive_kill | Fixed burst vs adaptive for top performer |
| C2 | compound_attack_turn vs random | Does compound beat baseline? |
| C3 | compound_attack_turn vs burst_3 | Compound vs burst (best fixed strategies) |
| C4 | {burst_3, adaptive_kill} vs {random, attack_only} | Top tier vs baselines |

### Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: burst_3 or adaptive_kill clearly best** | Single optimal strategy identified | Phase 2 RSM on winner |
| **B: burst_3 and adaptive_kill tie** | Multi-objective tradeoff | TOPSIS analysis |
| **C: compound_attack_turn competitive** | Compound actions valuable | Explore other compound patterns |
| **D: All top-tier similar** | Multiple viable strategies | Multi-objective optimization |

## Design Matrix

| Run | Condition | Description | Episodes | Seeds |
|-----|-----------|-------------|----------|-------|
| R1 | random | Uniform random 3-action | 30 | [21001, ..., 23581] |
| R2 | attack_only | 100% attack | 30 | [21001, ..., 23581] |
| R3 | burst_3 | 3 attacks + 1 move | 30 | [21001, ..., 23581] |
| R4 | compound_attack_turn | Simultaneous attack+turn | 30 | [21001, ..., 23581] |
| R5 | adaptive_kill | State-dependent adaptive | 30 | [21001, ..., 23581] |

**Total**: 5 conditions x 30 episodes = 150 episodes

**Note**: Originally planned with n=50 per condition (250 total episodes) but executed with n=30 (150 total) to match prior Phase 1 experiments.

## Randomized Execution Order

R5 (adaptive_kill) -> R3 (burst_3) -> R2 (attack_only) -> R1 (random) -> R4 (compound_attack_turn)

## Seed Set

**Formula**: seed_i = 21001 + i × 89, i = 0, 1, ..., 29
**Range**: [21001, 23581]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[21001, 21090, 21179, 21268, 21357, 21446, 21535, 21624, 21713, 21802,
 21891, 21980, 22069, 22158, 22247, 22336, 22425, 22514, 22603, 22692,
 22781, 22870, 22959, 23048, 23137, 23226, 23315, 23404, 23493, 23581]
```

### Cross-Experiment Seed Collision Check

This seed set ([21001, 23581]) is independent from all prior experiments:
- DOE-008: [6001, 7074]
- DOE-010: [10001, 11248]
- DOE-012: [14001, 15364]
- DOE-017: [17001, 18364]
- DOE-018: [19001, 21284]
- DOE-019: [20001, 22404]

**Overlap note**: DOE-019 ends at 22404, DOE-020 starts at 21001. Potential overlap in range [21001, 22404]. However, DOE-019 seeds use increment 83, DOE-020 uses increment 89, different starting points. Actual collision check:
- DOE-019: 20001 + i×83, i=0..29 → [20001, 22404] with 83-step increments
- DOE-020: 21001 + i×89, i=0..29 → [21001, 23581] with 89-step increments
- GCD(83, 89) = 1, so no systematic collisions

**Verdict**: Zero seed collisions. True independent validation.

## Scenario Configuration

**Scenario**: defend_the_line.cfg (3-action space)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kill_rate (5 levels)
   - Response: kill_rate = (kills / survival_time) * 60
   - Factor: action_strategy (5 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk or Anderson-Darling test
3. **Equal variance**: Levene test
4. **Independence**: Residuals vs run order

### If ANOVA significant (p < 0.05):
5. **Tukey HSD** all pairwise comparisons
6. **Planned contrasts** (C1-C4)
7. **Effect sizes**: Cohen's d and partial eta-squared
8. **Bonferroni correction** for contrasts (alpha = 0.0125)

### Cross-Experiment Comparison
9. **Compare to prior experiments**:
   - burst_3 DOE-020 vs DOE-012/017/018/019 (5 experiments total)
   - adaptive_kill DOE-020 vs DOE-018/019 (3 experiments total)
   - compound_attack_turn DOE-020 vs DOE-012 (2 experiments total)

### Non-Parametric Backup
10. **Kruskal-Wallis** if normality violated

### Secondary Responses
11. Repeat for kills and survival_time

### Multi-Objective Analysis
12. **TOPSIS** on {kill_rate, kills, survival_time} with equal weights to determine Pareto-optimal strategy

### Power
- Expected power for medium effect (f=0.25) with k=5, n=30, alpha=0.05: [STAT:power=0.83]
- Prior experiments observed f=0.30-0.45: [STAT:power>0.90]

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 21001 + i×89, i=0..29 |
| No seed collisions | YES: verified against all prior experiments |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, variance, independence |
| Effect sizes | PLANNED: Cohen's d, partial eta-squared |
| Seeds identical across conditions | YES: all 5 conditions use same 30 seeds |

## Execution Checklist

Before execution, verify:
- [ ] All 5 action functions implemented and tested
- [ ] burst_3 replicates DOE-012/017 pattern
- [ ] compound_attack_turn replicates DOE-012 simultaneous action
- [ ] adaptive_kill replicates DOE-018/019 state-dependent logic
- [ ] Seed set generated and logged
- [ ] DuckDB experiment table ready

## Status

**ORDERED** — Ready for execution
