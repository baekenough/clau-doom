---
name: opensearch-management
description: OpenSearch index management for kNN strategy documents including schema, bulk operations, and monitoring
user-invocable: false
---

# OpenSearch Management Skill

Management of OpenSearch indices for the strategy document RAG pipeline. Covers index creation, schema design, bulk operations, performance tuning, lifecycle management, and monitoring.

## Index Creation with kNN Field Mapping

### Strategy Index

```json
PUT /strategy-documents
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
      "title": {
        "type": "text",
        "analyzer": "standard"
      },
      "context": {
        "type": "text",
        "analyzer": "standard",
        "fields": {
          "keyword": { "type": "keyword" }
        }
      },
      "strategy": {
        "type": "text",
        "analyzer": "standard"
      },
      "expected_outcome": {
        "type": "text"
      },
      "source_agent": {
        "type": "keyword"
      },
      "generation": {
        "type": "keyword"
      },
      "tags": {
        "type": "keyword"
      },
      "quality_score": {
        "type": "float"
      },
      "retrieval_count": {
        "type": "integer"
      },
      "success_count": {
        "type": "integer"
      },
      "status": {
        "type": "keyword"
      },
      "created_at": {
        "type": "date"
      },
      "updated_at": {
        "type": "date"
      },
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

### kNN Parameters

| Parameter | Value | Description |
|-----------|-------|-------------|
| dimension | 768 | Matches nomic-embed-text output |
| space_type | cosinesimil | Cosine similarity for normalized vectors |
| engine | nmslib | Fast approximate nearest neighbor |
| ef_construction | 256 | Build-time accuracy (higher = more accurate, slower build) |
| m | 16 | Number of bi-directional links (higher = more memory, better recall) |
| ef_search | 100 | Query-time accuracy (higher = more accurate, slower query) |

### Alternative: Lucene Engine

For smaller indices (< 10K documents):

```json
{
  "type": "knn_vector",
  "dimension": 768,
  "method": {
    "name": "hnsw",
    "space_type": "cosinesimil",
    "engine": "lucene",
    "parameters": {
      "ef_construction": 128,
      "m": 16
    }
  }
}
```

Lucene advantages: no native library dependency, easier setup.
nmslib advantages: faster for larger indices, better throughput.

## Strategy Document Schema

### Core Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| doc_id | keyword | Yes | Unique ID: STR-{gen}-{seq} |
| title | text | Yes | Strategy name |
| context | text | Yes | Situation context tags |
| strategy | text | Yes | Tactical instructions |
| expected_outcome | text | Yes | Expected result |
| source_agent | keyword | Yes | Originating agent |
| generation | keyword | Yes | Originating generation |
| tags | keyword[] | Yes | Category tags |
| embedding | knn_vector | Yes | 768-dim vector |

### Metadata Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| quality_score | float | No | Quality metric [0, 1] |
| retrieval_count | integer | No | Times retrieved |
| success_count | integer | No | Successful retrievals |
| status | keyword | Yes | ACTIVE, DEPRECATED, RETIRED |
| created_at | date | Yes | Creation timestamp |
| updated_at | date | No | Last update timestamp |

### Computed Fields (at query time)

```
success_rate = success_count / retrieval_count
recency_score = exp(-0.05 * (current_gen - generation))
composite_score = 0.4 * success_rate + 0.2 * recency + 0.25 * author_perf + 0.15 * peer_rating
```

## Bulk Indexing Operations

### Bulk Index API

```
POST /_bulk
{"index": {"_index": "strategy-documents", "_id": "STR-GEN005-001"}}
{"doc_id": "STR-GEN005-001", "title": "...", "context": "...", "strategy": "...", "embedding": [...], "status": "ACTIVE", "created_at": "2026-02-07T14:30:00Z"}
{"index": {"_index": "strategy-documents", "_id": "STR-GEN005-002"}}
{"doc_id": "STR-GEN005-002", "title": "...", "context": "...", "strategy": "...", "embedding": [...], "status": "ACTIVE", "created_at": "2026-02-07T14:30:00Z"}
```

### Bulk Operation Guidelines

| Operation | Batch Size | Refresh |
|-----------|-----------|---------|
| Initial load | 100 | After all batches |
| Generation update | 20-50 | After batch |
| Quality score update | 50 | After batch |
| Status updates | 100 | After batch |

### Bulk Update (quality scores)

```
POST /_bulk
{"update": {"_index": "strategy-documents", "_id": "STR-GEN005-001"}}
{"doc": {"quality_score": 0.75, "retrieval_count": 15, "success_count": 11, "updated_at": "2026-02-07T15:00:00Z"}}
{"update": {"_index": "strategy-documents", "_id": "STR-GEN005-002"}}
{"doc": {"quality_score": 0.42, "retrieval_count": 20, "success_count": 7, "updated_at": "2026-02-07T15:00:00Z"}}
```

### Error Handling

```
After bulk operation, check response:
- "errors": true → some operations failed
- Check individual item statuses
- Retry failed items (max 3 retries)
- Log permanent failures for manual review
```

## Performance Tuning

### Index Settings

```json
{
  "index": {
    "refresh_interval": "5s",
    "number_of_replicas": 0,
    "translog": {
      "flush_threshold_size": "512mb",
      "sync_interval": "30s"
    }
  }
}
```

### Tuning for Batch Ingestion

Before bulk load:
```json
PUT /strategy-documents/_settings
{
  "index": {
    "refresh_interval": "-1",
    "number_of_replicas": 0
  }
}
```

After bulk load:
```json
PUT /strategy-documents/_settings
{
  "index": {
    "refresh_interval": "5s"
  }
}

POST /strategy-documents/_forcemerge?max_num_segments=1
```

### kNN Tuning

| Scenario | ef_search | Latency | Recall |
|----------|-----------|---------|--------|
| Low latency | 50 | ~10ms | ~90% |
| Balanced | 100 | ~20ms | ~95% |
| High accuracy | 200 | ~40ms | ~98% |

Increase ef_search if relevant documents are being missed.

### Memory Requirements

```
kNN memory estimate:
  vectors = num_docs * dimension * 4 bytes (float32)
  graph = num_docs * m * 2 * 4 bytes (HNSW graph)

Example (1000 documents, 768 dim, m=16):
  vectors = 1000 * 768 * 4 = 3.07 MB
  graph = 1000 * 16 * 2 * 4 = 0.13 MB
  total ~ 3.2 MB (very manageable)
```

## Index Lifecycle Management

### Index Rotation

For long-running experiments, rotate indices by generation range:

```
strategy-documents-gen001-010  (generations 1-10)
strategy-documents-gen011-020  (generations 11-20)
strategy-documents-current     (active generation, alias)
```

### Alias Management

```json
POST /_aliases
{
  "actions": [
    { "remove": { "index": "strategy-documents-gen001-010", "alias": "strategy-documents-current" } },
    { "add": { "index": "strategy-documents-gen011-020", "alias": "strategy-documents-current" } }
  ]
}
```

### Retention Policy

| Age (generations) | Action |
|-------------------|--------|
| 0-10 | Active, full search |
| 11-20 | Active, reduced weight |
| 21-50 | Archive search only |
| 51+ | Delete from OpenSearch, keep in DuckDB |

### Reindex Operation

When schema changes:

```json
POST /_reindex
{
  "source": { "index": "strategy-documents-v1" },
  "dest": { "index": "strategy-documents-v2" }
}
```

## Monitoring and Health Checks

### Cluster Health

```
GET /_cluster/health
```

Expected: status = "green" (or "yellow" with 0 replicas)

### Index Stats

```
GET /strategy-documents/_stats
```

Key metrics:
- docs.count: total documents
- store.size_in_bytes: index disk usage
- search.query_total: total queries
- search.query_time_in_millis: total query time
- indexing.index_total: total indexing operations

### kNN Stats

```
GET /_plugins/_knn/stats
```

Key metrics:
- circuit_breaker_triggered: memory limit hit
- total_load_time: time spent loading kNN indices
- knn_query_requests: number of kNN queries
- cache_capacity_reached: kNN graph cache full

### Health Check Script

```bash
#!/bin/bash
# OpenSearch health check

OPENSEARCH_URL="http://localhost:9200"

# Cluster health
curl -s "$OPENSEARCH_URL/_cluster/health" | jq '.status'

# Index exists and has documents
curl -s "$OPENSEARCH_URL/strategy-documents/_count" | jq '.count'

# kNN plugin loaded
curl -s "$OPENSEARCH_URL/_plugins/_knn/stats" | jq '.nodes | to_entries[0].value.knn_query_requests'

# Search latency test
time curl -s -X POST "$OPENSEARCH_URL/strategy-documents/_search" \
  -H 'Content-Type: application/json' \
  -d '{"size": 1, "query": {"match_all": {}}}' > /dev/null
```

### Alerting Thresholds

| Metric | Warning | Critical |
|--------|---------|----------|
| Cluster status | yellow | red |
| Query latency p99 | > 100ms | > 500ms |
| Index size | > 10000 docs | > 50000 docs |
| Circuit breaker | 1 trigger | 3+ triggers |
| Disk usage | > 80% | > 95% |

## Docker Compose Integration

```yaml
opensearch:
  image: opensearchproject/opensearch:2.11.0
  container_name: clau-doom-opensearch
  environment:
    - discovery.type=single-node
    - DISABLE_SECURITY_PLUGIN=true
    - OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m
    - plugins.ml_commons.only_run_on_ml_node=false
  ports:
    - "9200:9200"
    - "9600:9600"
  volumes:
    - opensearch-data:/usr/share/opensearch/data
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
    interval: 30s
    timeout: 10s
    retries: 5
```
