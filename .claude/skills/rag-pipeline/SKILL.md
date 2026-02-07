---
name: rag-pipeline
description: RAG pipeline for strategy document lifecycle, embedding, indexing, retrieval, and quality scoring
user-invocable: false
---

# RAG Pipeline Skill

Retrieval-Augmented Generation pipeline for managing strategy documents that encode learned game behaviors. Covers the full document lifecycle from creation through embedding, indexing, retrieval, quality scoring, and retirement.

## Document Lifecycle

```
[Create] Strategy document authored by agent or derived from experiment
    |
    v
[Embed] Generate vector embedding via Ollama
    |
    v
[Index] Store in OpenSearch with kNN field
    |
    v
[Retrieve] At game time: situation -> embed -> kNN search -> rank
    |
    v
[Score] Track retrieval frequency, success correlation
    |
    v
[Retire] Remove low-quality documents that hurt performance
```

### Lifecycle States

| State | Description |
|-------|------------|
| DRAFT | Created but not yet embedded/indexed |
| ACTIVE | Embedded, indexed, available for retrieval |
| UNDER_REVIEW | Flagged for quality review |
| DEPRECATED | Soft-deleted, not returned in searches |
| RETIRED | Permanently removed from index |

## Strategy Document Format

```yaml
---
doc_id: STR-GEN005-003
title: "Corridor Ambush with Shotgun"
context: "narrow_corridor enemy_approaching ammo_shotgun_available health_above_50"
strategy: |
  When in a narrow corridor with an approaching enemy and shotgun ammo available:
  1. Position at corner for ambush advantage
  2. Wait until enemy is within 3 tiles
  3. Fire shotgun (high damage at close range in corridors)
  4. If enemy survives, retreat to next cover point
  5. Do not chase - let them come to the next ambush point
expected_outcome: "High kill probability (>80%) with minimal damage taken"
source_agent: Agent_3
generation: GEN-005
tags:
  - combat
  - ambush
  - shotgun
  - corridor
created_at: 2026-02-07T14:30:00Z
quality_score: 0.0
retrieval_count: 0
success_count: 0
---
```

### Document Fields

| Field | Type | Description |
|-------|------|-------------|
| doc_id | string | Unique identifier: STR-{gen}-{seq} |
| title | string | Human-readable strategy name |
| context | string | Space-separated context tags for matching |
| strategy | string | Detailed tactical instructions |
| expected_outcome | string | What should happen if strategy works |
| source_agent | string | Agent that originated this strategy |
| generation | string | Generation when strategy was created |
| tags | list | Categorical tags for filtering |
| quality_score | float | Computed quality metric [0.0, 1.0] |
| retrieval_count | int | Times this document was retrieved |
| success_count | int | Times retrieval correlated with good outcome |

## Embedding with Ollama

### Model Selection

```yaml
embedding:
  provider: ollama
  model: nomic-embed-text    # 768 dimensions, good for short documents
  alternative: mxbai-embed-large  # 1024 dimensions, higher quality
  batch_size: 32
  normalize: true
```

### Embedding Process

```
1. Concatenate document fields for embedding:
   embed_text = f"{title}\n{context}\n{strategy}\n{expected_outcome}"

2. Call Ollama API:
   POST http://localhost:11434/api/embeddings
   {
     "model": "nomic-embed-text",
     "prompt": embed_text
   }

3. Response contains vector of 768 floats

4. Normalize vector to unit length:
   vector = vector / norm(vector)
```

### Batch Embedding

For bulk operations (new generation, re-indexing):

```python
def batch_embed(documents, batch_size=32):
    results = []
    for batch in chunks(documents, batch_size):
        texts = [doc.embed_text for doc in batch]
        embeddings = ollama_batch_embed(texts)
        results.extend(zip(batch, embeddings))
    return results
```

### Embedding Refresh

Re-embed documents when:
- Embedding model is upgraded
- Document content is modified
- Periodic refresh (every 10 generations)

## OpenSearch kNN Search Configuration

### Index Mapping

```json
{
  "settings": {
    "index": {
      "knn": true,
      "knn.algo_param.ef_search": 100,
      "number_of_shards": 1,
      "number_of_replicas": 0
    }
  },
  "mappings": {
    "properties": {
      "doc_id": { "type": "keyword" },
      "title": { "type": "text" },
      "context": { "type": "text" },
      "strategy": { "type": "text" },
      "expected_outcome": { "type": "text" },
      "source_agent": { "type": "keyword" },
      "generation": { "type": "keyword" },
      "tags": { "type": "keyword" },
      "quality_score": { "type": "float" },
      "retrieval_count": { "type": "integer" },
      "success_count": { "type": "integer" },
      "status": { "type": "keyword" },
      "created_at": { "type": "date" },
      "embedding": {
        "type": "knn_vector",
        "dimension": 768,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib",
          "parameters": {
            "ef_construction": 256,
            "m": 16
          }
        }
      }
    }
  }
}
```

### Search Query

```json
{
  "size": 5,
  "query": {
    "bool": {
      "must": [
        {
          "knn": {
            "embedding": {
              "vector": [0.12, -0.34, ...],
              "k": 10
            }
          }
        }
      ],
      "filter": [
        { "term": { "status": "ACTIVE" } },
        { "range": { "quality_score": { "gte": 0.3 } } }
      ]
    }
  },
  "_source": ["doc_id", "title", "context", "strategy", "expected_outcome", "quality_score"]
}
```

## Quality Scoring

### Score Components

```
quality_score = w1 * retrieval_success_rate
              + w2 * recency_score
              + w3 * author_performance
              + w4 * peer_rating

Weights:
  w1 = 0.40  (success rate most important)
  w2 = 0.20  (newer strategies may be more relevant)
  w3 = 0.25  (high-performing agents produce better strategies)
  w4 = 0.15  (peer evaluation from other agents)
```

### Retrieval Success Rate

```
success_rate = success_count / retrieval_count  (if retrieval_count > 5)
             = 0.5 (default if insufficient data)

Success defined as:
  - Agent survived the encounter
  - Kill was achieved within 50 ticks of retrieval
  - Damage taken was below threshold
```

### Recency Score

```
recency = exp(-lambda * generations_since_creation)

lambda = 0.05 (slow decay)

Gen 0:  1.00
Gen 10: 0.61
Gen 20: 0.37
Gen 50: 0.08
```

### Author Performance

```
author_score = topsis_score of source_agent in most recent generation

If source_agent no longer exists: use average of current generation
```

### Quality Threshold Actions

| Score Range | Action |
|-------------|--------|
| 0.8 - 1.0  | Priority retrieval, increased weight |
| 0.5 - 0.8  | Normal retrieval |
| 0.3 - 0.5  | Under review, reduced weight |
| 0.0 - 0.3  | Deprecated, excluded from search |

## Retrieval at Game Time

### Situation Encoding

During gameplay, encode current situation as context:

```
situation = encode_situation(
  location_type="corridor",
  enemy_nearby=True,
  enemy_distance=5,
  enemy_type="imp",
  health=65,
  ammo_shotgun=12,
  ammo_pistol=30,
  armor=20,
  items_visible=["health_pack", "shotgun_shells"],
  recent_events=["took_damage", "killed_enemy"]
)

# Output: "corridor enemy_nearby_5 enemy_imp health_medium ammo_shotgun_high ammo_pistol_high armor_low items_health items_ammo recent_damage recent_kill"
```

### Retrieval Flow

```
1. Encode current situation as text
2. Embed situation text via Ollama
3. kNN search in OpenSearch (k=5)
4. Filter by quality_score >= 0.3
5. Re-rank by composite score:
     composite = 0.6 * knn_similarity + 0.4 * quality_score
6. Return top strategy
7. Increment retrieval_count for returned document
```

### Retrieval Latency Budget

```
Target: < 100ms total

Breakdown:
  Embedding:  ~30ms  (Ollama local)
  kNN search: ~20ms  (OpenSearch)
  Re-ranking: ~5ms   (in-memory)
  Overhead:   ~15ms  (network, parsing)
  Budget:     ~30ms  (margin)
```

### Fallback Strategy

If no documents match (kNN similarity < 0.5):
1. Use default behavior encoded in agent base config
2. Log the unmatched situation for future strategy creation
3. After game: analyze unmatched situations, create new strategies

## Document Retirement

### Retirement Criteria

Document is retired when:
```
1. quality_score < 0.1 for 3+ consecutive scoring cycles
2. retrieval_count > 20 AND success_rate < 0.15
3. source_agent has been replaced for 10+ generations
4. Strategy contradicts current best practices (manual flag)
```

### Retirement Process

```
1. Set status = DEPRECATED (soft delete, excluded from search)
2. Keep in index for 5 more generations (can be restored)
3. After 5 generations with no retrieval: status = RETIRED
4. Archive document to DuckDB archive table
5. Remove from OpenSearch index
```

### Archival

```sql
INSERT INTO strategy_archive (
  doc_id, title, context, strategy,
  source_agent, generation,
  final_quality_score, total_retrievals, total_successes,
  created_at, retired_at, retirement_reason
)
SELECT *, NOW(), 'low_quality' FROM strategy_documents WHERE doc_id = ?;
```

## Monitoring

### Pipeline Health Metrics

```yaml
metrics:
  index_size: 150          # total active documents
  avg_quality_score: 0.62  # mean quality across active docs
  retrieval_latency_p50: 45ms
  retrieval_latency_p99: 95ms
  cache_hit_rate: 0.35     # similar situations reuse recent results
  unmatched_rate: 0.08     # situations with no good match
  deprecated_this_gen: 3   # documents deprecated this generation
  created_this_gen: 5      # new documents this generation
```

### Alerts

- unmatched_rate > 0.20: Need more diverse strategies
- avg_quality_score < 0.40: Strategy pool degrading
- retrieval_latency_p99 > 200ms: Performance issue
- index_size > 1000: Consider pruning old strategies
