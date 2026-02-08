# EXPERIMENT_ORDER_018: Adaptive Strategies

## Metadata
- **Experiment ID**: DOE-018
- **Hypothesis**: H-022 — Adaptive state-dependent strategies outperform fixed strategies
- **DOE Phase**: Phase 1
- **Design Type**: One-way completely randomized design (5 levels)
- **Date Ordered**: 2026-02-08

## Research Question

Do strategies that adapt behavior based on game state (health, kill stagnation) outperform fixed-pattern strategies on defend_the_line?

### Background

DOE-008 through DOE-017 explored fixed-pattern strategies: burst strategies (attack-then-turn), compound actions (simultaneous operations), and random baselines. DOE-012 and DOE-017 identified burst_3 (3 attacks + 1 turn) as consistently achieving ~44-45 kr. All prior strategies used deterministic, non-adaptive patterns.

**Key Question**: Can strategies that dynamically adjust based on real-time game state (health level, recent kill history) improve performance beyond fixed patterns?

### Hypothesis

**H-022: Adaptive State-Dependent Strategies Outperform Fixed Strategies**

Adaptive strategies that modulate aggression based on health (defensive when low health, aggressive when high health) and detect kill stagnation (reset attack cycle when no kills for N ticks) should outperform fixed-pattern strategies by matching behavior to current game context.

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| action_strategy | Categorical | 5 | Action selection architecture with adaptive vs fixed patterns |

### Factor Levels

| Level | Condition Label | Description | Expected Pattern |
|-------|----------------|-------------|-----------------|
| 1 | random | Uniform random 3-action (baseline) | 33% attack rate |
| 2 | attack_only | 100% attack (baseline) | 100% attack rate |
| 3 | adaptive_kill | State-dependent: aggressive >60hp (more attacks), balanced 30-60hp, defensive <30hp (more movement), stagnation detection resets attack cycle | ~60-80% attack rate (adaptive) |
| 4 | aggressive_adaptive | Always attack unless health < 15 (nearly always attacks) | ~95% attack rate |
| 5 | burst_3 | 3 attacks + 1 move (reference strategy from DOE-012/017) | 75% attack rate |

### Strategy Design Rationale

**random** (baseline): Replication control. Expected ~43 kr based on DOE-008 through DOE-017.

**attack_only** (baseline): Pure aggression baseline. Expected ~43-44 kr based on DOE-008.

**adaptive_kill** (flagship adaptive): Adjusts behavior based on two state variables:
- Health threshold: >60hp = aggressive (higher attack rate), 30-60hp = balanced, <30hp = defensive (more movement to avoid damage)
- Stagnation detection: If no kills for 5 consecutive attacks, reset attack cycle and force a movement to reposition
- Combines health awareness with performance feedback

**aggressive_adaptive**: Tests a minimal adaptation (health < 15 triggers dodge). Almost always attacks except at critical health. This isolates whether ANY health awareness helps.

**burst_3** (reference): Replication of DOE-012/017 best performer. Anchors adaptive strategies against proven fixed pattern.

### Key Contrasts

| Contrast | Comparison | Tests |
|----------|------------|-------|
| C1 | adaptive_kill vs burst_3 | Does adaptive state awareness beat fixed burst? |
| C2 | adaptive_kill vs aggressive_adaptive | Does full state-dependent logic beat minimal adaptation? |
| C3 | aggressive_adaptive vs attack_only | Does health<15 threshold add value? |
| C4 | adaptive_kill vs random | Does adaptive intelligence beat random baseline? |

### Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: adaptive_kill > burst_3** | State awareness adds value | Phase 2 RSM on adaptive thresholds |
| **B: burst_3 >= adaptive_kill** | Fixed patterns sufficient | Optimize burst parameters instead |
| **C: aggressive_adaptive fails** | Health awareness threshold too extreme | Refine health thresholds |
| **D: All strategies similar** | Strategy doesn't matter | Scenario ceiling reached |

## Design Matrix

| Run | Condition | Description | Episodes | Seeds |
|-----|-----------|-------------|----------|-------|
| R1 | random | Uniform random 3-action | 30 | [19001, ..., 21284] |
| R2 | attack_only | 100% attack | 30 | [19001, ..., 21284] |
| R3 | adaptive_kill | State-dependent adaptive | 30 | [19001, ..., 21284] |
| R4 | aggressive_adaptive | Always attack unless hp<15 | 30 | [19001, ..., 21284] |
| R5 | burst_3 | 3 attacks + 1 move | 30 | [19001, ..., 21284] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R4 (aggressive_adaptive) -> R1 (random) -> R5 (burst_3) -> R3 (adaptive_kill) -> R2 (attack_only)

## Seed Set

**Formula**: seed_i = 19001 + i × 79, i = 0, 1, ..., 29
**Range**: [19001, 21284]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[19001, 19080, 19159, 19238, 19317, 19396, 19475, 19554, 19633, 19712,
 19791, 19870, 19949, 20028, 20107, 20186, 20265, 20344, 20423, 20502,
 20581, 20660, 20739, 20818, 20897, 20976, 21055, 21134, 21213, 21284]
```

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
8. **Bonferroni correction** for planned contrasts (alpha = 0.0125)

### Non-Parametric Backup
9. **Kruskal-Wallis** if normality violated

### Secondary Responses
10. Repeat for kills and survival_time

### Power
- Expected power for medium effect (f=0.25) with k=5, n=30, alpha=0.05: [STAT:power=0.83]
- DOE-017 observed f=0.37: [STAT:power=0.97]

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 19001 + i×79, i=0..29 |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, variance, independence |
| Effect sizes | PLANNED: Cohen's d, partial eta-squared |
| Seeds identical across conditions | YES: all 5 conditions use same 30 seeds |

## Execution Checklist

Before execution, verify:
- [ ] adaptive_kill action function implemented with health thresholds and stagnation detection
- [ ] aggressive_adaptive action function implemented with health<15 trigger
- [ ] burst_3 action function replicates DOE-012/017 pattern
- [ ] random and attack_only functions verified
- [ ] Seed set generated and logged
- [ ] DuckDB experiment table ready

## Status

**ORDERED** — Ready for execution
