#!/usr/bin/env bash
# Setup OpenSearch strategies index with kNN mapping and seed documents.
# Idempotent: safe to run multiple times.

set -euo pipefail

OPENSEARCH_URL="${OPENSEARCH_URL:-http://localhost:9200}"
INDEX_NAME="strategies"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "[setup_opensearch] OpenSearch URL: $OPENSEARCH_URL"

# --- Phase 1: Wait for OpenSearch to be healthy ---
echo "[setup_opensearch] Waiting for OpenSearch cluster health..."
MAX_RETRIES=30
RETRY_INTERVAL=5
for i in $(seq 1 $MAX_RETRIES); do
    STATUS=$(curl -sf "$OPENSEARCH_URL/_cluster/health" 2>/dev/null \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('status',''))" 2>/dev/null \
        || echo "")
    if [ "$STATUS" = "green" ] || [ "$STATUS" = "yellow" ]; then
        echo "[setup_opensearch] Cluster is healthy (status: $STATUS)"
        break
    fi
    if [ "$i" -eq "$MAX_RETRIES" ]; then
        echo "[setup_opensearch] ERROR: OpenSearch not healthy after $((MAX_RETRIES * RETRY_INTERVAL))s"
        exit 1
    fi
    echo "[setup_opensearch] Waiting... ($i/$MAX_RETRIES)"
    sleep "$RETRY_INTERVAL"
done

# --- Phase 2: Create index (idempotent) ---
INDEX_EXISTS=$(curl -sf -o /dev/null -w "%{http_code}" "$OPENSEARCH_URL/$INDEX_NAME" 2>/dev/null || echo "000")
if [ "$INDEX_EXISTS" = "200" ]; then
    echo "[setup_opensearch] Index '$INDEX_NAME' already exists, skipping creation."
else
    echo "[setup_opensearch] Creating index '$INDEX_NAME' with kNN mapping..."
    HTTP_CODE=$(curl -sf -o /tmp/opensearch_create_response.json -w "%{http_code}" \
        -X PUT "$OPENSEARCH_URL/$INDEX_NAME" \
        -H "Content-Type: application/json" \
        -d '{
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
      "doc_id": { "type": "keyword" },
      "agent_id": { "type": "keyword" },
      "generation": { "type": "integer" },
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
      "situation_tags": { "type": "keyword" },
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
}')

    if [ "$HTTP_CODE" = "200" ]; then
        echo "[setup_opensearch] Index '$INDEX_NAME' created successfully."
    else
        echo "[setup_opensearch] ERROR: Failed to create index (HTTP $HTTP_CODE)"
        cat /tmp/opensearch_create_response.json 2>/dev/null
        exit 1
    fi
fi

# --- Phase 3: Seed strategy documents ---
echo "[setup_opensearch] Seeding strategy documents..."
SEED_SCRIPT="$PROJECT_ROOT/glue/data/seed_to_opensearch.py"
if [ -f "$SEED_SCRIPT" ]; then
    OPENSEARCH_URL="$OPENSEARCH_URL" python3 "$SEED_SCRIPT"
else
    echo "[setup_opensearch] WARNING: Seed script not found at $SEED_SCRIPT"
    echo "[setup_opensearch] Skipping document seeding."
fi

echo "[setup_opensearch] Setup complete."
