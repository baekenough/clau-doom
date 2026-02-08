#!/usr/bin/env bash
# Run a DOE experiment inside the doom-player Docker container.
#
# Usage:
#   ./infra/scripts/run_experiment.sh DOE-005
#   ./infra/scripts/run_experiment.sh DOE-005 --dry-run
#
# Environment variables:
#   COMPOSE_FILE  - docker-compose file (default: infra/docker-compose.yml)

set -euo pipefail

# ============================================================================
# Configuration
# ============================================================================

COMPOSE_FILE="${COMPOSE_FILE:-infra/docker-compose.yml}"
DRY_RUN=false

# ============================================================================
# Argument Parsing
# ============================================================================

if [ $# -lt 1 ]; then
  echo "Usage: $0 EXPERIMENT_ID [--dry-run]" >&2
  echo "Example: $0 DOE-005" >&2
  exit 1
fi

EXPERIMENT_ID="$1"
shift

# Parse optional flags
while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run)
      DRY_RUN=true
      shift
      ;;
    *)
      echo "Unknown option: $1" >&2
      exit 1
      ;;
  esac
done

# ============================================================================
# Project Root Detection
# ============================================================================

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

cd "$PROJECT_ROOT"

echo "[experiment] Project root: $PROJECT_ROOT"

# ============================================================================
# Pre-flight Checks
# ============================================================================

echo "[experiment] Running pre-flight checks..."

# Check docker-compose.yml exists
if [ ! -f "$COMPOSE_FILE" ]; then
  echo "[experiment] ERROR: Compose file not found: $COMPOSE_FILE" >&2
  exit 1
fi
echo "[experiment] ✓ Compose file found: $COMPOSE_FILE"

# Check glue directory exists
if [ ! -d "glue" ]; then
  echo "[experiment] ERROR: glue/ directory not found" >&2
  exit 1
fi
echo "[experiment] ✓ glue/ directory found"

# Extract experiment number from ID (e.g., DOE-005 → 005)
if [[ ! "$EXPERIMENT_ID" =~ ^DOE-([0-9]{3})$ ]]; then
  echo "[experiment] ERROR: Invalid experiment ID format: $EXPERIMENT_ID" >&2
  echo "[experiment] Expected format: DOE-XXX (e.g., DOE-005)" >&2
  exit 1
fi

EXPERIMENT_NUM="${BASH_REMATCH[1]}"
echo "[experiment] Experiment number: $EXPERIMENT_NUM"

# Check experiment order file exists
ORDER_FILE="research/experiments/EXPERIMENT_ORDER_${EXPERIMENT_NUM}.md"
if [ ! -f "$ORDER_FILE" ]; then
  echo "[experiment] ERROR: Experiment order file not found: $ORDER_FILE" >&2
  exit 1
fi
echo "[experiment] ✓ Experiment order file found: $ORDER_FILE"

# Check for execution script - prefer reusable executor over per-experiment scripts
EXEC_MODE=""
EXEC_SCRIPT=""

if [ -f "glue/doe_executor.py" ]; then
  EXEC_MODE="reusable"
  echo "[experiment] ✓ Reusable DOE executor found: glue/doe_executor.py"
else
  # Fall back to per-experiment scripts (legacy)
  for candidate in "glue/doe_${EXPERIMENT_NUM}_execute.py" "glue/doe_${EXPERIMENT_NUM}_real.py"; do
    if [ -f "$candidate" ]; then
      EXEC_SCRIPT="$candidate"
      EXEC_MODE="legacy"
      break
    fi
  done

  if [ "$EXEC_MODE" = "legacy" ]; then
    echo "[experiment] ✓ Legacy execution script found: $EXEC_SCRIPT"
  else
    EXEC_MODE="none"
    echo "[experiment] WARNING: No execution script found" >&2
    echo "[experiment] Expected: glue/doe_executor.py or glue/doe_${EXPERIMENT_NUM}_execute.py" >&2
    # Not a fatal error - user might want to run manually
  fi
fi

# ============================================================================
# Dry-run Mode
# ============================================================================

if [ "$DRY_RUN" = true ]; then
  echo ""
  echo "[experiment] DRY-RUN MODE - Actions that would be performed:"
  echo ""
  echo "1. Start doom-player container:"
  echo "   docker compose -f $COMPOSE_FILE up -d doom-player"
  echo ""
  echo "2. Wait for container health check"
  echo ""
  if [ "$EXEC_MODE" = "reusable" ]; then
    echo "3. Execute experiment script (reusable executor):"
    echo "   docker compose -f $COMPOSE_FILE exec doom-player \\"
    echo "       python3 -m glue.doe_executor --experiment $EXPERIMENT_ID"
  elif [ "$EXEC_MODE" = "legacy" ]; then
    echo "3. Execute experiment script (legacy):"
    echo "   docker compose -f $COMPOSE_FILE exec doom-player \\"
    echo "       python3 /app/$EXEC_SCRIPT"
  else
    echo "3. No execution script found - manual execution required"
  fi
  echo ""
  echo "4. Results would be written to:"
  echo "   - DuckDB: volumes/data/clau-doom.duckdb"
  echo "   - Reports: research/experiments/"
  echo ""
  exit 0
fi

# ============================================================================
# Start Services
# ============================================================================

echo ""
echo "[experiment] Starting doom-player container..."

docker compose -f "$COMPOSE_FILE" up -d doom-player

# ============================================================================
# Wait for Container Health
# ============================================================================

echo "[experiment] Waiting for doom-player to be healthy..."

MAX_WAIT=60
ELAPSED=0
INTERVAL=2

while [ $ELAPSED -lt $MAX_WAIT ]; do
  # Check if container is running
  if ! docker compose -f "$COMPOSE_FILE" ps doom-player --format json | grep -q "running"; then
    echo "[experiment] ERROR: doom-player container is not running" >&2
    docker compose -f "$COMPOSE_FILE" logs --tail=50 doom-player
    exit 1
  fi

  # Check if Xvfb is running (simple health check)
  if docker compose -f "$COMPOSE_FILE" exec -T doom-player pgrep -x Xvfb > /dev/null 2>&1; then
    echo "[experiment] ✓ doom-player is healthy"
    break
  fi

  sleep $INTERVAL
  ELAPSED=$((ELAPSED + INTERVAL))
  echo -n "."
done

echo ""

if [ $ELAPSED -ge $MAX_WAIT ]; then
  echo "[experiment] ERROR: doom-player failed to become healthy after ${MAX_WAIT}s" >&2
  docker compose -f "$COMPOSE_FILE" logs --tail=100 doom-player
  exit 1
fi

# ============================================================================
# Execute Experiment
# ============================================================================

echo ""
echo "[experiment] ============================================"
echo "[experiment] Executing experiment: $EXPERIMENT_ID"
echo "[experiment] ============================================"
echo ""

if [ "$EXEC_MODE" = "reusable" ]; then
  # Run the reusable DOE executor
  echo "[experiment] Running: python3 -m glue.doe_executor --experiment $EXPERIMENT_ID"
  echo ""

  # Note: The glue/ directory is mounted at /app/glue (read-only)
  # Execute as module so imports work correctly
  docker compose -f "$COMPOSE_FILE" exec doom-player \
    python3 -m glue.doe_executor --experiment "$EXPERIMENT_ID"

  EXIT_CODE=$?

elif [ "$EXEC_MODE" = "legacy" ]; then
  # Run the legacy per-experiment script
  echo "[experiment] Running (legacy): python3 /app/$EXEC_SCRIPT"
  echo ""

  # Note: The glue/ directory is mounted at /app/glue (read-only)
  # Execute the script inside the container
  docker compose -f "$COMPOSE_FILE" exec doom-player \
    python3 "/app/$EXEC_SCRIPT"

  EXIT_CODE=$?

else
  # No execution script found - provide manual instructions
  echo "[experiment] No execution script found for $EXPERIMENT_ID"
  echo "[experiment] To execute manually, run:"
  echo ""
  echo "  docker compose -f $COMPOSE_FILE exec doom-player bash"
  echo ""
  echo "Then inside the container:"
  echo "  cd /app/glue"
  echo "  python3 -m glue.doe_executor --experiment $EXPERIMENT_ID"
  echo ""
  exit 1
fi

# ============================================================================
# Report Results
# ============================================================================

echo ""

if [ $EXIT_CODE -eq 0 ]; then
  echo "[experiment] ============================================"
  echo "[experiment] Experiment $EXPERIMENT_ID completed successfully"
  echo "[experiment] ============================================"
  echo ""
  echo "[experiment] Results locations:"
  echo "[experiment]   - DuckDB: volumes/data/clau-doom.duckdb"
  echo "[experiment]   - Order:  $ORDER_FILE"
  echo ""
  echo "[experiment] To view results:"
  echo "[experiment]   duckdb volumes/data/clau-doom.duckdb 'SELECT * FROM episodes ORDER BY episode_id DESC LIMIT 10;'"
  echo ""
else
  echo "[experiment] ============================================"
  echo "[experiment] Experiment $EXPERIMENT_ID FAILED (exit code: $EXIT_CODE)"
  echo "[experiment] ============================================"
  echo ""
  echo "[experiment] Check logs:"
  echo "[experiment]   docker compose -f $COMPOSE_FILE logs doom-player"
  echo ""
  exit $EXIT_CODE
fi
