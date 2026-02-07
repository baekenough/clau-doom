# DOOM Player: Random Baseline

## Decision Mode
random_action

## Parameters
- action_space: [MOVE_LEFT, MOVE_RIGHT, ATTACK]
- selection: uniform_random

## Decision Hierarchy
- L0 (MD Rules): DISABLED
- L1 (DuckDB Cache): DISABLED
- L2 (OpenSearch RAG): DISABLED

## Purpose
Floor baseline for DOE-001. All actions selected uniformly at random with equal probability (1/3 per action). No learning, no strategy, no memory. Expected performance: very low kill_rate, short survival_time. This baseline represents the absolute minimum capability — any structured agent should outperform this decisively.

**Action Space Note**: Aligned with DOE-001 scenario specification (Defend the Center: 3 discrete actions). See EXPERIMENT_ORDER_001.md, Section: Scenario.

## Implementation
```
Each tick:
  action = random.choice([MOVE_LEFT, MOVE_RIGHT, ATTACK])
```

No context, no state, no history. Pure stochastic behavior.

## Expected Metrics
- kill_rate: ~0.05 (occasional lucky hits)
- survival_time: ~500 ticks (dies quickly due to random movement into danger)
- damage_dealt: ~50 (random firing, mostly misses)
- ammo_efficiency: ~0.02 kills/ammo (extremely wasteful)
- map_coverage: ~10% (random walk, likely gets stuck)

## Comparison Value
The delta between any agent and this baseline quantifies the value of ANY decision-making structure. If Full Agent ~ Random Agent, the architecture is fundamentally broken.
