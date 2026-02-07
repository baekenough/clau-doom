# DOOM Player: Generation 1 (Full RAG)

## Decision Mode
full_rag

## Parameters
- memory_weight: ${MEMORY_WEIGHT}
- strength_weight: ${STRENGTH_WEIGHT}
- health_threshold: 0.3
- attack_priority: nearest_enemy
- retreat_distance: 100

## Decision Hierarchy
- L0 (MD Rules): ENABLED
- L1 (DuckDB Cache): ENABLED
- L2 (OpenSearch RAG): ENABLED

## OpenSearch Config
- index: strategies
- k: 5
- similarity: cosine

## DuckDB Cache Config
- table: episode_history
- lookback: last_100_episodes
- similarity: situational_match

## Purpose
Full RAG agent for DOE-001 (condition 3), DOE-002, DOE-005. This configuration activates all three decision levels:
- **Level 0 (MD Rules)**: Emergency reflexes (health < threshold → retreat)
- **Level 1 (DuckDB Cache)**: Recent episode memory (what worked in similar situations)
- **Level 2 (OpenSearch kNN)**: Strategy document retrieval (semantic search for situation-appropriate tactics)

Parameters are injected per experiment condition via MD variable substitution.

## Variable Injection

The research-doe-runner agent injects factor values into this template:

```
DOE-002 Run 1 (Memory=0.3, Strength=0.3):
  ${MEMORY_WEIGHT} → 0.3
  ${STRENGTH_WEIGHT} → 0.3

DOE-002 Run 2 (Memory=0.3, Strength=0.7):
  ${MEMORY_WEIGHT} → 0.3
  ${STRENGTH_WEIGHT} → 0.7

DOE-002 Center Point (Memory=0.5, Strength=0.5):
  ${MEMORY_WEIGHT} → 0.5
  ${STRENGTH_WEIGHT} → 0.5
```

## Decision Flow

```
1. Observe game state (health, ammo, enemies_visible, position)

2. Level 0 (MD Rules): Check emergency conditions
   if health < health_threshold:
     → immediate_retreat()
     → DONE (skip L1, L2)

3. Level 1 (DuckDB Cache): Query recent episodes
   situations = query_similar_situations(current_state)
   cache_strategy = top_strategy_from(situations)

4. Level 2 (OpenSearch RAG): Query strategy documents
   documents = opensearch_knn(current_state, k=5)
   rag_strategy = rust_scoring(documents, weights=[similarity, confidence, recency])

5. Blend: Combine cache + RAG strategies
   final_strategy = memory_weight * cache_strategy + (1 - memory_weight) * rag_strategy

6. Execute action
   action = final_strategy.select_action()
   execute(action)
```

## Rust Scoring (Level 2)

OpenSearch returns top-k documents. Rust agent scores each using:

```
score = 0.4 * similarity + 0.4 * confidence + 0.2 * recency

similarity  = cosine(current_state_embedding, document_embedding)
confidence  = wilson_score(wins, total_uses) from document metadata
recency     = exp(-age_in_episodes / 100)
```

Best scoring document is selected for execution.

## Expected Metrics

Baseline expectations (before evolution):
- kill_rate: ~0.50 (significantly better than Rule-Only ~0.30)
- survival_time: ~3500 ticks (adaptive retreat based on experience)
- damage_dealt: ~700 (focused attacks + learned positioning)
- ammo_efficiency: ~0.25 kills/ammo (learned conservation)
- map_coverage: ~50% (exploration guided by RAG strategies)

These metrics should improve across generations as:
1. Strategy documents accumulate successful patterns
2. DuckDB cache refines situational recall
3. Evolution optimizes memory_weight and strength_weight

## Comparison Value

The delta between Full RAG (this template) and Rule-Only (L0 only) quantifies the core contribution of RAG experience accumulation. This is the primary claim of the clau-doom research.

If Full RAG ≈ Rule-Only (no significant difference), the RAG pipeline does not add value, and the research direction fails validation.
