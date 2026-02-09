# EXPERIMENT_ORDER_027: Attack Ratio Gradient Sweep in 5-Action Space

## Metadata

| Field | Value |
|-------|-------|
| Experiment ID | DOE-027 |
| Hypothesis | H-030 |
| Design | One-way ANOVA (7 levels) |
| Factor | attack_ratio (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8) |
| Episodes per level | 30 |
| Total episodes | 210 |
| Scenario | defend_the_line_5action.cfg |
| Seed formula | seed_i = 47001 + i × 127, i=0..29 |

## Hypothesis

H-030: The relationship between attack frequency and total kills is non-monotonic in the 5-action space. An optimal attack ratio exists below 50%, consistent with the survival-first paradox (F-064) where survival_burst (40% attack) paradoxically achieves the highest kills.

## Research Question

What is the optimal attack-to-movement ratio for maximizing kills in the 5-action defend_the_line scenario? Is the survival-first paradox (F-064) a robust phenomenon with a clear optimum, or an artifact of discrete strategy comparison?

## Background

DOE-025 compared 6 discrete strategies in the 5-action space and found:
- survival_burst (40% attack): 17.57 kills — BEST
- random_5 (~50% implicit attack): 17.20 kills
- dodge_burst_3 (~60% attack): 17.17 kills
- adaptive_dodge (state-dependent): 16.57 kills
- full_aggressive_5 (70% attack): 15.93 kills — WORST non-adaptive

This suggests a paradoxical inverse relationship between attack frequency and kills. DOE-027 maps the full gradient with a single parametric strategy to isolate the attack ratio variable cleanly.

## Experimental Design

### Factor: attack_ratio

| Level | attack_ratio | Description | Condition Label |
|-------|-------------|-------------|-----------------|
| 1 | 0.20 | 20% attack, 80% movement | ar_20 |
| 2 | 0.30 | 30% attack, 70% movement | ar_30 |
| 3 | 0.40 | 40% attack, 60% movement | ar_40 |
| 4 | 0.50 | 50% attack, 50% movement | ar_50 |
| 5 | 0.60 | 60% attack, 40% movement | ar_60 |
| 6 | 0.70 | 70% attack, 30% movement | ar_70 |
| 7 | 0.80 | 80% attack, 20% movement | ar_80 |

### Strategy Implementation

AttackRatioAction: On each tick, with probability = attack_ratio, choose ATTACK (action 4); otherwise, choose uniformly from {TURN_LEFT(0), TURN_RIGHT(1), MOVE_LEFT(2), MOVE_RIGHT(3)}.

This provides a clean parametric gradient where ONLY the attack probability varies. Movement is always uniform random across the 4 non-attack actions.

### Design Matrix

7 conditions × 30 episodes = 210 episodes total.

### Seed Set

Formula: seed_i = 47001 + i × 127, i = 0..29
All 7 conditions use the IDENTICAL seed set for fair comparison.

### Randomized Run Order

R5, R2, R7, R1, R4, R6, R3 (pre-randomized)

## Statistical Analysis Plan

### Primary Analysis

One-way ANOVA with 7 levels on:
- kills (primary response)
- survival_time (secondary)
- kill_rate (derived: kills / survival_time × 60)

### Planned Contrasts

| Contrast | Test | Description |
|----------|------|-------------|
| C1 | Linear trend | Is there a monotonic linear trend? |
| C2 | Quadratic trend | Is there a peak (inverted U-shape)? |
| C3 | ar_40 vs ar_50 | Does the F-064 paradox replicate? |
| C4 | ar_20 vs ar_80 | Extreme endpoints comparison |

### Post-Hoc

Tukey HSD for all pairwise comparisons if overall ANOVA is significant.

### Residual Diagnostics

- Normality: Anderson-Darling
- Equal variance: Levene's test
- Independence: Run order plot

### Power

With n=30 per group and 7 groups, power > 0.80 for medium effect (f=0.25) at α=0.05.

## Outcome Scenarios

| Scenario | Description | Implication |
|----------|-------------|-------------|
| A: Inverted U | Peak at ar_30-40, decline at higher ratios | Confirms survival-first paradox, optimal ratio identified |
| B: Monotonic decrease | Higher attack = fewer kills linearly | Survival is strictly dominant, movement > attack |
| C: Flat/Null | No significant effect of attack_ratio | Strategy selection irrelevant, confirming 5-action near-ceiling |
| D: Monotonic increase | Higher attack = more kills | Rejects survival-first paradox, more attack is better |

## Execution Instructions

1. Implement AttackRatioAction class in action_functions.py
2. Add DOE-027 config to doe_executor.py
3. Execute: `python3 -m glue.doe_executor --experiment DOE-027`
4. Analyze with one-way ANOVA + trend contrasts
