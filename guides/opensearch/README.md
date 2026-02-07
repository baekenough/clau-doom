# OpenSearch Reference Guide

Reference documentation for OpenSearch integration in clau-doom.

## Key Resources

- [OpenSearch Documentation](https://opensearch.org/docs/latest/)
- [k-NN Plugin](https://opensearch.org/docs/latest/search-plugins/knn/index/)
- [OpenSearch REST API](https://opensearch.org/docs/latest/api-reference/)
- [Performance Tuning](https://opensearch.org/docs/latest/tuning-your-cluster/)

## clau-doom Context

OpenSearch serves as the RAG (Retrieval-Augmented Generation) knowledge base for agent strategy documents. Agents query OpenSearch using k-nearest-neighbor (kNN) vector search to find relevant strategies for their current game situation. The decision must complete within 100ms including network round-trip.

Key operations:
- **Index creation** with kNN settings for vector fields
- **Bulk indexing** of strategy documents from research curation
- **kNN search** at game time for strategy retrieval (< 100ms budget)
- **Document lifecycle**: creation, validation, promotion, retirement

## Index Creation with kNN Settings

### Strategy Index

```json
PUT /strategies
{
  "settings": {
    "index": {
      "knn": true,
      "knn.algo_param.ef_search": 100,
      "number_of_shards": 1,
      "number_of_replicas": 0,
      "refresh_interval": "5s"
    }
  },
  "mappings": {
    "properties": {
      "doc_id": {
        "type": "keyword"
      },
      "agent_id": {
        "type": "keyword"
      },
      "generation": {
        "type": "integer"
      },
      "situation_embedding": {
        "type": "knn_vector",
        "dimension": 384,
        "method": {
          "name": "hnsw",
          "space_type": "cosinesimil",
          "engine": "nmslib",
          "parameters": {
            "ef_construction": 256,
            "m": 16
          }
        }
      },
      "situation_tags": {
        "type": "keyword"
      },
      "decision": {
        "properties": {
          "tactic": { "type": "keyword" },
          "weapon": { "type": "keyword" },
          "parameters": { "type": "object", "enabled": false }
        }
      },
      "quality": {
        "properties": {
          "success_rate": { "type": "float" },
          "sample_size": { "type": "integer" },
          "last_validated": { "type": "date" },
          "confidence_tier": { "type": "keyword" },
          "trust_score": { "type": "float" }
        }
      },
      "metadata": {
        "properties": {
          "created_at": { "type": "date" },
          "source_experiment": { "type": "keyword" },
          "retired": { "type": "boolean" }
        }
      }
    }
  }
}
```

### Field Mapping Details

| Field | Type | Purpose |
|-------|------|---------|
| `situation_embedding` | `knn_vector` | 384-dim embedding for similarity search |
| `dimension` | 384 | Matches Ollama embedding model output |
| `space_type` | `cosinesimil` | Cosine similarity for normalized vectors |
| `engine` | `nmslib` | Fastest engine for approximate kNN |
| `m` | 16 | HNSW graph connections (higher = more accurate, more memory) |
| `ef_construction` | 256 | Build-time quality (higher = better index, slower build) |

## Strategy Document Schema

```json
{
  "doc_id": "tactic_007_042",
  "agent_id": "PLAYER_007",
  "generation": 3,
  "situation_embedding": [0.12, -0.34, 0.56, ...],
  "situation_tags": ["narrow_corridor", "multi_enemy", "low_health"],
  "decision": {
    "tactic": "retreat_and_funnel",
    "weapon": "shotgun",
    "parameters": {
      "retreat_distance": 200,
      "funnel_width": 50
    }
  },
  "quality": {
    "success_rate": 0.84,
    "sample_size": 47,
    "last_validated": "2026-02-07T10:30:00Z",
    "confidence_tier": "high",
    "trust_score": 0.82
  },
  "metadata": {
    "created_at": "2026-02-05T08:00:00Z",
    "source_experiment": "EXP-021",
    "retired": false
  }
}
```

### Trust Score Computation

```
trust_score = wilson_lower_bound(successes, total_uses, z=1.96)

Tiers:
  trust_score >= 0.70: "high"    (proven strategy)
  trust_score >= 0.40: "medium"  (promising, needs more data)
  trust_score <  0.40: "low"     (unproven, exploratory)
```

## Bulk Indexing API

### Single Document

```json
POST /strategies/_doc/tactic_007_042
{
  "doc_id": "tactic_007_042",
  "agent_id": "PLAYER_007",
  "generation": 3,
  "situation_embedding": [0.12, -0.34, ...],
  "situation_tags": ["narrow_corridor", "multi_enemy"],
  "decision": {
    "tactic": "retreat_and_funnel",
    "weapon": "shotgun"
  },
  "quality": {
    "success_rate": 0.84,
    "sample_size": 47,
    "last_validated": "2026-02-07T10:30:00Z",
    "confidence_tier": "high",
    "trust_score": 0.82
  },
  "metadata": {
    "created_at": "2026-02-07T10:30:00Z",
    "source_experiment": "EXP-021",
    "retired": false
  }
}
```

### Bulk Indexing

```json
POST /_bulk
{"index": {"_index": "strategies", "_id": "tactic_007_042"}}
{"doc_id": "tactic_007_042", "agent_id": "PLAYER_007", "generation": 3, "situation_embedding": [0.12, -0.34, ...], "situation_tags": ["narrow_corridor"], "decision": {"tactic": "retreat_and_funnel", "weapon": "shotgun"}, "quality": {"success_rate": 0.84, "sample_size": 47, "trust_score": 0.82}, "metadata": {"created_at": "2026-02-07T10:30:00Z", "retired": false}}
{"index": {"_index": "strategies", "_id": "tactic_007_043"}}
{"doc_id": "tactic_007_043", "agent_id": "PLAYER_007", "generation": 3, "situation_embedding": [0.45, 0.12, ...], "situation_tags": ["open_area", "single_enemy"], "decision": {"tactic": "direct_engage", "weapon": "chaingun"}, "quality": {"success_rate": 0.91, "sample_size": 33, "trust_score": 0.78}, "metadata": {"created_at": "2026-02-07T10:35:00Z", "retired": false}}
```

### Bulk Indexing Best Practices

- Batch size: 500-1000 documents per request
- Disable refresh during bulk: `PUT /strategies/_settings {"index.refresh_interval": "-1"}`
- Re-enable after bulk: `PUT /strategies/_settings {"index.refresh_interval": "5s"}`
- Force merge after large bulk: `POST /strategies/_forcemerge?max_num_segments=1`

## kNN Search Query

### Basic kNN Query

```json
POST /strategies/_search
{
  "size": 5,
  "query": {
    "knn": {
      "situation_embedding": {
        "vector": [0.15, -0.30, 0.52, ...],
        "k": 5
      }
    }
  }
}
```

### Filtered kNN Query

Combine vector search with filters for more relevant results.

```json
POST /strategies/_search
{
  "size": 5,
  "query": {
    "bool": {
      "must": [
        {
          "knn": {
            "situation_embedding": {
              "vector": [0.15, -0.30, 0.52, ...],
              "k": 10
            }
          }
        }
      ],
      "filter": [
        { "term": { "metadata.retired": false } },
        { "range": { "quality.trust_score": { "gte": 0.3 } } }
      ]
    }
  },
  "_source": ["doc_id", "decision", "quality", "situation_tags"]
}
```

### Search Response

```json
{
  "hits": {
    "total": { "value": 5, "relation": "eq" },
    "max_score": 0.92,
    "hits": [
      {
        "_id": "tactic_007_042",
        "_score": 0.92,
        "_source": {
          "doc_id": "tactic_007_042",
          "decision": {
            "tactic": "retreat_and_funnel",
            "weapon": "shotgun"
          },
          "quality": {
            "success_rate": 0.84,
            "sample_size": 47,
            "trust_score": 0.82
          },
          "situation_tags": ["narrow_corridor", "multi_enemy"]
        }
      }
    ]
  }
}
```

### Rust Client Query (from agent-core)

```rust
async fn query_strategies(
    client: &reqwest::Client,
    embedding: &[f32; 384],
    k: usize,
) -> Result<Vec<StrategyDoc>> {
    let body = serde_json::json!({
        "size": k,
        "query": {
            "bool": {
                "must": [{
                    "knn": {
                        "situation_embedding": {
                            "vector": embedding,
                            "k": k * 2  // Over-fetch for post-filtering
                        }
                    }
                }],
                "filter": [
                    { "term": { "metadata.retired": false } },
                    { "range": { "quality.trust_score": { "gte": 0.3 } } }
                ]
            }
        },
        "_source": ["doc_id", "decision", "quality", "situation_tags",
                     "situation_embedding"]
    });

    let resp = client
        .post("http://opensearch:9200/strategies/_search")
        .json(&body)
        .timeout(Duration::from_millis(80))
        .send()
        .await?;

    parse_hits(resp).await
}
```

## Performance Tuning

### Index Settings

```json
PUT /strategies/_settings
{
  "index": {
    "refresh_interval": "5s",
    "number_of_replicas": 0,
    "translog.durability": "async",
    "translog.sync_interval": "10s"
  }
}
```

| Setting | Value | Reason |
|---------|-------|--------|
| `refresh_interval` | `5s` | Balance between search freshness and indexing speed |
| `number_of_replicas` | `0` | Single node, no replication needed |
| `translog.durability` | `async` | Better write performance for research workload |

### kNN Parameters

| Parameter | Value | Impact |
|-----------|-------|--------|
| `ef_search` | 100 | Runtime quality (higher = more accurate, slower) |
| `ef_construction` | 256 | Index build quality |
| `m` | 16 | Graph connections (16 balances speed/quality) |

### Merge Policy

```json
PUT /strategies/_settings
{
  "index": {
    "merge.policy.max_merged_segment": "1gb",
    "merge.policy.segments_per_tier": 10
  }
}
```

After large bulk operations, force merge to optimize search:
```
POST /strategies/_forcemerge?max_num_segments=1
```

## Monitoring Endpoints

### Cluster Health

```
GET /_cluster/health

Response:
{
  "cluster_name": "docker-cluster",
  "status": "green",    // green/yellow/red
  "number_of_nodes": 1,
  "active_shards": 1,
  "unassigned_shards": 0
}
```

### Index Stats

```
GET /strategies/_stats

Key metrics:
  - docs.count: Total strategy documents
  - store.size_in_bytes: Index size on disk
  - indexing.index_total: Total indexing operations
  - search.query_total: Total search queries
  - search.query_time_in_millis: Cumulative search time
```

### Search Performance

```
GET /strategies/_stats/search

Monitor:
  - query_time_in_millis / query_total = avg query latency
  - Target: < 50ms average (leaves budget for network + scoring)
```

### Node Stats

```
GET /_nodes/stats

Key metrics:
  - jvm.mem.heap_used_percent: Should be < 75%
  - os.cpu.percent: CPU usage
  - fs.total.available_in_bytes: Disk space
```

## Document Lifecycle

```
1. Creation (research-rag-curator):
   - Generate embedding from situation features via Ollama
   - Index with initial quality (success_rate=0.5, sample_size=0, trust_score=0)

2. Validation (game play):
   - Each time strategy is used: increment sample_size
   - Track success/failure: update success_rate
   - Recompute trust_score via Wilson score

3. Promotion:
   - trust_score >= 0.70: Mark as "high" confidence
   - Frequently retrieved and successful docs get priority

4. Retirement:
   - trust_score drops below 0.20 after 50+ uses
   - Set metadata.retired = true (excluded from search via filter)
   - Keep in index for historical analysis

5. Generation Evolution:
   - Copy high-trust docs to next generation's pool
   - Reset sample_size for copied docs (new validation cycle)
   - Merge similar docs to reduce index bloat
```

## Embedding Model

```
Model: Ollama (nomic-embed-text or similar)
Dimension: 384
Input: Concatenated situation features as text
Output: Float32 vector [384]

Feature text template:
  "health:{h} ammo:{a} enemies:{n} distance:{d} area:{type} weapon:{w}"

Embedding is generated:
  - At index time by research-rag-curator
  - At query time by Rust agent (pre-computed or via Ollama API)
```
