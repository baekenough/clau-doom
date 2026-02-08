# DOOM Player Gen1 Agent Template

## Identity
- Name: doom-player-gen1
- Generation: 1
- Scenario: defend_the_center

## Parameters
- health_threshold: 0.3
- memory_weight: ${MEMORY_WEIGHT}
- strength_weight: ${STRENGTH_WEIGHT}
- curiosity_factor: ${CURIOSITY_FACTOR}

## Decision Hierarchy
- L0 (MD Rules): ENABLED
- L1 (DuckDB Cache): ${L1_ENABLED}
- L2 (OpenSearch kNN): ${L2_ENABLED}

## Decision Mode
- mode: ${DECISION_MODE}

## Scoring Weights
- similarity: 0.4
- confidence: 0.4
- recency: 0.2

## Rules

### Emergency Retreat
- condition: health < ${HEALTH_THRESHOLD}
- action: MOVE_LEFT
- priority: 100

### Attack Visible Enemy
- condition: enemies_visible >= 1
- action: ATTACK
- priority: 50

### Reposition
- condition: enemies_visible == 0
- action: MOVE_LEFT
- priority: 10
