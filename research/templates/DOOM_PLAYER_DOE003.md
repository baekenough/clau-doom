# DOOM Player: DOE-003 Layer Ablation

## Decision Mode
configurable_layers

## Parameters
- memory_weight: 0.5
- strength_weight: 0.5
- health_threshold: 0.3
- attack_priority: nearest_enemy

## Decision Hierarchy
- L0 (MD Rules): ${L0_ENABLED}
- L1 (DuckDB Cache): ${L1_ENABLED}
- L2 (OpenSearch RAG): ${L2_ENABLED}

## Purpose
Configurable agent for DOE-003 ablation study. Each decision level can be independently enabled or disabled per experimental condition. This template supports the full 2^3 factorial design (8 conditions) for H-005 (layer removal ablation).

## Variable Injection

The research-doe-runner agent injects layer ON/OFF settings per condition:

```
DOE-003 Run 1 (Full Stack: L0+L1+L2):
  ${L0_ENABLED} → true
  ${L1_ENABLED} → true
  ${L2_ENABLED} → true

DOE-003 Run 2 (L0 + L1 Only):
  ${L0_ENABLED} → true
  ${L1_ENABLED} → true
  ${L2_ENABLED} → false

DOE-003 Run 3 (L0 Only):
  ${L0_ENABLED} → true
  ${L1_ENABLED} → false
  ${L2_ENABLED} → false

DOE-003 Run 4 (L2 Only):
  ${L0_ENABLED} → false
  ${L1_ENABLED} → false
  ${L2_ENABLED} → true

DOE-003 Run 5 (L0 + L2):
  ${L0_ENABLED} → true
  ${L1_ENABLED} → false
  ${L2_ENABLED} → true

DOE-003 Run 6 (L1 + L2):
  ${L0_ENABLED} → false
  ${L1_ENABLED} → true
  ${L2_ENABLED} → true

DOE-003 Run 7 (L1 Only):
  ${L0_ENABLED} → false
  ${L1_ENABLED} → true
  ${L2_ENABLED} → false

DOE-003 Run 8 (All Layers OFF — degenerate floor):
  ${L0_ENABLED} → false
  ${L1_ENABLED} → false
  ${L2_ENABLED} → false
```

## Decision Flow

```
1. Observe game state (health, ammo, enemies_visible, position)

2. If L0_ENABLED:
     Check emergency MD rules (health < threshold → retreat)
     if triggered:
       → execute emergency action
       → DONE (skip L1, L2)

3. If L1_ENABLED:
     Query DuckDB cache for similar past situations
     cache_strategy = top_strategy_from_cache()
   else:
     cache_strategy = null

4. If L2_ENABLED:
     Query OpenSearch kNN for strategy documents
     rag_strategy = rust_scoring(opensearch_knn(state, k=5))
   else:
     rag_strategy = null

5. Blend available strategies:
   if cache_strategy and rag_strategy:
     final = memory_weight * cache + (1 - memory_weight) * rag
   elif cache_strategy only:
     final = cache_strategy
   elif rag_strategy only:
     final = rag_strategy
   elif no strategies available (all layers OFF):
     final = default_action (MOVE_FORWARD)

6. Execute action
   execute(final.select_action())
```

## Degenerate Floor Condition (All Layers OFF)

When L0, L1, and L2 are all disabled:
- No emergency rules
- No cache retrieval
- No RAG retrieval
- Agent defaults to `MOVE_FORWARD` every tick

This condition represents the absolute floor: no decision-making structure at all. Expected performance: worse than Random Agent (which at least tries ATTACK occasionally). This condition validates that the measurement system is working — if All OFF performs well, the experiment setup is broken.

## Expected Metrics by Condition

| Condition | L0 | L1 | L2 | Expected kill_rate | Interpretation |
|-----------|----|----|----|--------------------|----------------|
| Full Stack | ✓ | ✓ | ✓ | 0.50 | Best performance |
| L0+L1 | ✓ | ✓ | ✗ | 0.35 | No RAG retrieval |
| L0 Only | ✓ | ✗ | ✗ | 0.30 | Rule-Only baseline |
| L2 Only | ✗ | ✗ | ✓ | 0.25 | RAG without rules |
| L0+L2 | ✓ | ✗ | ✓ | 0.45 | No cache, RAG only |
| L1+L2 | ✗ | ✓ | ✓ | 0.40 | No emergency rules |
| L1 Only | ✗ | ✓ | ✗ | 0.20 | Cache without RAG |
| All OFF | ✗ | ✗ | ✗ | 0.05 | Degenerate floor |

These are rough predictions. ANOVA will reveal actual main effects and interactions.

## Hypothesis Testing (DOE-003)

This template tests **H-005**: Each decision layer independently adds measurable value.

**ANOVA Model**:
```
kill_rate ~ L0 + L1 + L2 + L0:L1 + L0:L2 + L1:L2 + L0:L1:L2 + error
```

**Expected Findings**:
- L0 main effect: significant (emergency rules prevent early death)
- L1 main effect: significant (cache provides situational recall)
- L2 main effect: significant (RAG provides strategic guidance)
- Interactions: L0×L2 interaction likely significant (rules + RAG synergy)

**Decision Gate**:
If Full Stack ≈ L0 Only (no significant difference, p > 0.10), STOP further ablations (H-003, H-004) and investigate why RAG is not adding value.

## Notes

- All conditions use the same seeds per replicate (controlled randomization)
- memory_weight and strength_weight are fixed at 0.5 for this ablation (not varied)
- DOE-003 is the most fundamental ablation — run FIRST before H-003 and H-004
- If L2 (OpenSearch RAG) is not significant, document quality ablation (H-003) becomes less meaningful
