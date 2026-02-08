# EXPERIMENT_ORDER_014: L0 Health Threshold Parameter

## Metadata
- **Experiment ID**: DOE-014
- **Hypothesis**: H-018
- **DOE Phase**: Phase 1 (L0 behavioral parameter tuning)
- **Design Type**: One-way completely randomized design (5 levels)
- **Date Ordered**: 2026-02-08

## Research Question

Does the health threshold for L0 emergency dodge behavior affect kill_rate on defend_the_line?

### Background

All prior experiments (DOE-001 through DOE-013) used hardcoded L0 (Level 0) decision logic: pure attack strategies with no health-based behavior. DOE-013 established that attack ratio does NOT affect kill_rate [STAT:p=0.812] when using fixed burst patterns. However, the L0 layer can be enhanced with **conditional emergency behavior** that responds to the agent's health state.

**L0 Enhancement Proposal**: Add a health threshold parameter. When `current_health < threshold`, override the base strategy and execute a dodge action (e.g., random turn or strafe). This emergency dodge behavior aims to:
1. Avoid death when health is critically low
2. Extend survival time
3. Potentially maintain or improve kill_rate by keeping the agent alive longer

**Parameter Space**: The health threshold can range from 0 (no emergency dodge, baseline) to 100 (always dodging, degenerate). Reasonable values are 10-50, where the agent dodges only when health is low.

**Known Tradeoff**: Emergency dodging diverts ticks from attack to movement. This REDUCES attack frequency (and potentially kill_rate) but MAY extend survival enough to accumulate more total kills. The net effect on kill_rate is unknown.

### Hypothesis

**H-018: L0 Health Threshold Modulates Kill_Rate**

Introducing a health-based dodge threshold will create a performance gradient. Moderate thresholds (20-30) should balance attack frequency with survival, producing HIGHER kill_rate than no-dodge baseline (threshold=0) or overly aggressive dodge (threshold=50).

**Competing Hypothesis**: The threshold parameter has NO effect on kill_rate because weapon cooldown and enemy damage patterns dominate. The dodge behavior is triggered too rarely (only when health is low) to affect the overall performance.

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| health_threshold | Categorical | 5 | Health value below which L0 triggers emergency dodge |

### Factor Levels

All 5 conditions use the **burst_3 base strategy** (3 attacks + 1 random turn, 75% attack rate) from DOE-010/011/013. The health threshold OVERRIDES this pattern when triggered.

| Level | Condition Label | Health Threshold | Dodge Trigger | Expected Dodge Frequency |
|-------|----------------|------------------|---------------|-------------------------|
| 1 | threshold_0 | 0 | Never | 0% (pure burst_3, baseline) |
| 2 | threshold_10 | 10 | health < 10 | Rare (~5% of episode) |
| 3 | threshold_20 | 20 | health < 20 | Occasional (~10-15%) |
| 4 | threshold_30 | 30 | health < 30 | Moderate (~20-25%) |
| 5 | threshold_50 | 50 | health < 50 | Frequent (~40-50%) |

### Strategy Design Rationale

**threshold_0** (no dodge): Pure burst_3 strategy. No health-based behavior. Expected ~43-45 kr based on DOE-010/011/013. Serves as the baseline.

**threshold_10** (rare dodge): Emergency dodge only when health is critically low (<10). Minimal impact on attack frequency. Tests whether late-stage survival extension helps.

**threshold_20** (occasional dodge): Dodge when health is moderately low. Moderate dodge frequency. Tests a balanced threshold.

**threshold_30** (moderate dodge): Dodge when health drops below 30 (close to half of starting health 100). More frequent dodging. Tests whether preemptive dodging (before health is critical) helps.

**threshold_50** (frequent dodge): Aggressive dodge behavior. The agent dodges for roughly half of the episode (whenever health < 50). High dodge frequency. Tests the upper bound of dodge behavior.

### Dodge Action

When the threshold is triggered (health < threshold), the agent executes a **random turn** (turn_left or turn_right with equal probability) for that tick, overriding the burst_3 pattern. This is the same repositioning action used in burst_3, so the dodge behavior is consistent with the base strategy (no new action types introduced).

### Key Contrasts (Planned Comparisons)

| Contrast | Comparison | Tests |
|----------|------------|-------|
| C1 | threshold_0 vs threshold_10 | Baseline vs minimal dodge |
| C2 | threshold_10 vs threshold_20 | Rare vs occasional dodge |
| C3 | threshold_20 vs threshold_30 | Occasional vs moderate dodge |
| C4 | threshold_30 vs threshold_50 | Moderate vs aggressive dodge |
| C5 | threshold_0 vs threshold_50 | Baseline vs extreme dodge |

### Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: Inverted-U (threshold_20 or threshold_30 peaks)** | Optimal threshold exists; balance is critical | Phase 2 RSM to fine-tune around optimal |
| **B: Monotonic decrease (threshold_0 > ... > threshold_50)** | Dodge behavior HURTS kill_rate; avoid it | Disable health-based dodge; stick with pure burst_3 |
| **C: Monotonic increase (threshold_50 > ... > threshold_0)** | More dodge = better; aggressive defense helps | Adopt high threshold; explore 50-100 range |
| **D: No effect (all conditions similar)** | Health threshold doesn't matter | L0 parameters are not a productive research avenue |
| **E: Plateau at low threshold (threshold_10 = ... = threshold_50 < threshold_0)** | ANY dodge is better than none, but frequency doesn't matter | Use minimal threshold (10); binary effect like movement presence |

## Design Matrix

| Run | Condition | Health Threshold | Base Strategy | Episodes | Seeds |
|-----|-----------|------------------|---------------|----------|-------|
| R1 | threshold_0 | 0 (no dodge) | burst_3 | 30 | [15001, ..., 16770] |
| R2 | threshold_10 | 10 | burst_3 + dodge | 30 | [15001, ..., 16770] |
| R3 | threshold_20 | 20 | burst_3 + dodge | 30 | [15001, ..., 16770] |
| R4 | threshold_30 | 30 | burst_3 + dodge | 30 | [15001, ..., 16770] |
| R5 | threshold_50 | 50 | burst_3 + dodge | 30 | [15001, ..., 16770] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R3 (threshold_20) -> R5 (threshold_50) -> R1 (threshold_0) -> R4 (threshold_30) -> R2 (threshold_10)

## Seed Set

**Formula**: seed_i = 15001 + i x 61, i = 0, 1, ..., 29
**Range**: [15001, 16770]
**Count**: 30 seeds per condition, identical across all 5 conditions

**Full seed set**:
```
[15001, 15062, 15123, 15184, 15245, 15306, 15367, 15428, 15489, 15550,
 15611, 15672, 15733, 15794, 15855, 15916, 15977, 16038, 16099, 16160,
 16221, 16282, 16343, 16404, 16465, 16526, 16587, 16648, 16709, 16770]
```

### Cross-Experiment Seed Collision Check

| Experiment | Seed Range | Overlap with [15001, 16770]? |
|-----------|------------|------------------------------|
| DOE-013 | [14001, 15712] | Minimal (15001-15712 shared) |

**Verdict**: Minor overlap with DOE-013 tail (711 seeds), but different experiment contexts. No practical collision risk.

## Scenario Configuration

**File**: defend_the_line.cfg (standard 3-action)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

### L0 Implementation

The health threshold logic is implemented in the L0 decision layer (Rust agent core or Python VizDoomBridge):

```python
def get_action(game_state, threshold):
    current_health = game_state.health

    # Emergency dodge override
    if current_health < threshold:
        return random.choice([TURN_LEFT, TURN_RIGHT])

    # Base burst_3 strategy
    return burst_3_action(game_state)
```

### Known Limitations
1. **AMMO2 tracking broken** for defend_the_line. ammo_efficiency and shots_fired EXCLUDED from analysis.
2. **Health reporting granularity**: VizDoom may report health in discrete increments. Fine-grained thresholds (e.g., 15 vs 16) may not be distinguishable.
3. **Enemy damage patterns**: Damage is probabilistic and depends on enemy AI. High variance in health trajectories may obscure threshold effects.

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kill_rate (5 levels)
   - Response: kill_rate = (kills / survival_time) * 60
   - Factor: health_threshold (5 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk test
3. **Equal variance**: Levene test
4. **Independence**: Residuals vs run order

### If ANOVA significant:
5. **Tukey HSD** all pairwise comparisons (10 pairs)
6. **Planned contrasts** (C1-C5)
7. **Trend analysis**: Linear, quadratic trends across the threshold spectrum
8. **Effect sizes**: Cohen's d, eta-squared
9. **Bonferroni correction** for 5 planned contrasts (alpha = 0.01)

### Non-Parametric Backup
10. **Kruskal-Wallis** if normality violated

### Secondary Responses
11. Repeat analysis for kills and survival_time
12. **Dodge frequency analysis**: If VizDoom logs action counts, compute actual dodge tick percentage per condition to validate expected frequencies

### Power
- Expected power for medium effect (f=0.25) with k=5, n=30, alpha=0.05: [STAT:power=0.83]
- DOE-010/011/012/013 observed effects (f~0.32-0.41): [STAT:power>0.89]

## Cross-Experiment Validation

### Replication Check
- **threshold_0** should replicate DOE-010/011/013 burst_3 (~43-45 kr). If it differs by more than 1 pooled SD, flag for investigation.

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 15001 + i*61, i=0..29 |
| No seed collisions | YES: verified against prior experiments |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED |
| Residual diagnostics | PLANNED |
| Effect sizes | PLANNED |
| Seeds identical across conditions | YES |

## Status

**ORDERED** — Awaiting execution.
