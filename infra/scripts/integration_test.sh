#!/usr/bin/env bash
# Integration test runner for the gRPC pipeline.
# Checks service health, seeds OpenSearch if needed, runs pytest.
#
# Environment variables:
#   GRPC_HOST       - gRPC server host (default: localhost)
#   GRPC_PORT       - gRPC server port (default: 50052)
#   OPENSEARCH_URL  - OpenSearch base URL (default: http://localhost:9200)

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
GRPC_HOST="${GRPC_HOST:-localhost}"
GRPC_PORT="${GRPC_PORT:-50052}"
OPENSEARCH_URL="${OPENSEARCH_URL:-http://localhost:9200}"

echo "[integration] Testing gRPC pipeline..."
echo "[integration] gRPC: ${GRPC_HOST}:${GRPC_PORT}"
echo "[integration] OpenSearch: ${OPENSEARCH_URL}"

# Phase 1: Wait for OpenSearch
echo "[integration] Waiting for OpenSearch..."
for i in $(seq 1 30); do
    if curl -sf "${OPENSEARCH_URL}/_cluster/health" > /dev/null 2>&1; then
        echo "[integration] OpenSearch healthy"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "[integration] ERROR: OpenSearch not healthy after 150s"
        exit 1
    fi
    sleep 5
done

# Phase 2: Seed strategies if needed
echo "[integration] Checking strategy documents..."
DOC_COUNT=$(curl -sf "${OPENSEARCH_URL}/strategies/_count" 2>/dev/null \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('count',0))" 2>/dev/null \
    || echo "0")

if [ "$DOC_COUNT" -eq 0 ]; then
    echo "[integration] No strategies found, running seed script..."
    if [ -f "$PROJECT_ROOT/infra/scripts/setup_opensearch.sh" ]; then
        OPENSEARCH_URL="$OPENSEARCH_URL" bash "$PROJECT_ROOT/infra/scripts/setup_opensearch.sh" || true
    else
        echo "[integration] WARNING: setup_opensearch.sh not found, skipping seed"
    fi
fi
echo "[integration] Strategies: $DOC_COUNT documents"

# Phase 3: Wait for gRPC server
echo "[integration] Waiting for gRPC server..."
for i in $(seq 1 30); do
    if python3 -c "
from glue.grpc_client import check_grpc_health
import sys
sys.exit(0 if check_grpc_health('${GRPC_HOST}', ${GRPC_PORT}, 2.0) else 1)
" 2>/dev/null; then
        echo "[integration] gRPC server healthy"
        break
    fi
    if [ "$i" -eq 30 ]; then
        echo "[integration] ERROR: gRPC server not reachable after 150s"
        exit 1
    fi
    sleep 5
done

# Phase 4: Run integration tests
echo "[integration] Running integration tests..."
cd "$PROJECT_ROOT"
GRPC_HOST="$GRPC_HOST" GRPC_PORT="$GRPC_PORT" \
    python3 -m pytest glue/tests/test_grpc_integration.py -v --tb=short

echo "[integration] All tests passed!"
