---
name: deployment-ops
description: Production Docker Compose operations including health checks, restart policies, resource management, scaling, backup procedures, and troubleshooting
user-invocable: false
---

# Deployment Operations for clau-doom

## Production Docker Compose Configuration

### File Organization

The clau-doom project uses multiple compose files for different environments:

```bash
# Base service definitions
docker-compose.yml

# Production overrides (resource limits, restart policies)
docker-compose.prod.yml

# Development overrides (volume mounts, debug ports, hot reload)
docker-compose.dev.yml

# GPU support (NVIDIA runtime)
docker-compose.gpu.yml
```

### Launch Commands

```bash
# Production stack
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Development stack with hot reload
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# GPU-enabled production
docker compose -f docker-compose.yml -f docker-compose.prod.yml -f docker-compose.gpu.yml up -d

# Stop all services
docker compose down

# Stop and remove volumes (DANGEROUS for data)
docker compose down -v
```

### Environment Management

```bash
# .env file structure (root directory)
# Base configuration
NATS_VERSION=2.10
OPENSEARCH_VERSION=2.11.0
MONGODB_VERSION=7.0
OLLAMA_VERSION=latest

# Networking
ORCHESTRATOR_GRPC_PORT=50051
DASHBOARD_HTTP_PORT=3000
VIZDOOM_NOVNC_PORT=6080
NATS_CLIENT_PORT=4222

# Resource limits (overridden per environment)
ORCHESTRATOR_MEM_LIMIT=1G
VIZDOOM_MEM_LIMIT=2G
AGENT_MEM_LIMIT=512M
```

```bash
# .env.prod (production overrides)
ORCHESTRATOR_MEM_LIMIT=2G
VIZDOOM_MEM_LIMIT=4G
AGENT_MEM_LIMIT=1G
LOG_LEVEL=info
```

```bash
# .env.dev (development overrides)
ORCHESTRATOR_MEM_LIMIT=512M
VIZDOOM_MEM_LIMIT=1G
LOG_LEVEL=debug
HOT_RELOAD=true
```

### Required Variables Documentation

```bash
# Required environment variables for clau-doom stack
# Missing any of these will cause service failures

# Infrastructure
DOCKER_HOST=unix:///var/run/docker.sock  # Docker socket path
NATS_URL=nats://nats:4222                # NATS connection string

# Storage paths
OPENSEARCH_DATA_PATH=/var/lib/opensearch
MONGODB_DATA_PATH=/var/lib/mongodb
DUCKDB_DATA_PATH=/data/duckdb

# Endpoints
GRPC_ENDPOINT=orchestrator:50051
OPENSEARCH_ENDPOINT=http://opensearch:9200
MONGODB_URI=mongodb://mongodb:27017/clau-doom
```

## Health Check Patterns

### Per-Service Health Checks

```yaml
services:
  opensearch:
    image: opensearchproject/opensearch:2.11.0
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:9200/_cluster/health | grep -qE 'green|yellow'"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s  # OpenSearch takes time to initialize

  mongodb:
    image: mongo:7.0
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  nats:
    image: nats:2.10-alpine
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 5s

  ollama:
    image: ollama/ollama:latest
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s

  orchestrator:
    build:
      context: .
      dockerfile: docker/orchestrator/Dockerfile
    healthcheck:
      test: ["CMD", "grpc_health_probe", "-addr=:50051"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  agent:
    build:
      context: .
      dockerfile: docker/agent/Dockerfile
    healthcheck:
      test: ["CMD", "grpc_health_probe", "-addr=:50052"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 10s

  dashboard:
    build:
      context: .
      dockerfile: docker/dashboard/Dockerfile
    healthcheck:
      test: ["CMD", "curl", "-sf", "http://localhost:3000/api/health"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 20s

  vizdoom:
    build:
      context: .
      dockerfile: docker/vizdoom/Dockerfile
    healthcheck:
      test: ["CMD", "pgrep", "-f", "vizdoom"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 10s
```

### Configuration Parameters

| Parameter | Description | Recommended Value |
|-----------|-------------|-------------------|
| `interval` | Time between health checks | 10-30s (frequent for critical services) |
| `timeout` | Max time to wait for response | 5-10s |
| `retries` | Failed checks before unhealthy | 3-5 |
| `start_period` | Grace period before checks start | Service-dependent (see table below) |

### Start Period Considerations

| Service | Start Period | Reason |
|---------|-------------|--------|
| OpenSearch | 60s | Cluster initialization, shard allocation |
| MongoDB | 20s | Replica set initialization |
| Ollama | 30s | Model loading |
| Dashboard | 20s | Next.js build and server start |
| Orchestrator | 15s | gRPC server initialization |
| NATS | 5s | Lightweight, starts quickly |
| Agent | 10s | Rust binary initialization |

### Dependency Ordering

```yaml
# Startup DAG: infra → data stores → orchestrator → agents → dashboard

services:
  # Tier 1: Infrastructure (no dependencies)
  nats:
    # No depends_on

  # Tier 2: Data stores (no dependencies)
  opensearch:
    # No depends_on

  mongodb:
    # No depends_on

  ollama:
    # No depends_on

  # Tier 3: Orchestrator (depends on Tier 1+2)
  orchestrator:
    depends_on:
      nats:
        condition: service_healthy
      opensearch:
        condition: service_healthy
      mongodb:
        condition: service_healthy

  # Tier 4: Agents (depends on orchestrator)
  agent:
    depends_on:
      orchestrator:
        condition: service_healthy

  # Tier 5: Dashboard (depends on orchestrator)
  dashboard:
    depends_on:
      orchestrator:
        condition: service_healthy
```

### Startup DAG Visualization

```
nats ────────────┐
                 │
opensearch ──────┼──→ orchestrator ──→ agent
                 │            │
mongodb ─────────┘            └──→ dashboard

ollama (independent, used by Rust agent via HTTP)

vizdoom ──→ orchestrator (via gRPC)
```

## Restart Policies

### Policy Selection

```yaml
services:
  # Persistent infrastructure: restart unless manually stopped
  opensearch:
    restart: unless-stopped

  mongodb:
    restart: unless-stopped

  nats:
    restart: unless-stopped

  ollama:
    restart: unless-stopped

  # Managed services: retry on failure, stop after max attempts
  orchestrator:
    restart: on-failure:5

  dashboard:
    restart: on-failure:3

  # Agent containers: lifecycle managed by orchestrator, do not auto-restart
  agent:
    restart: "no"

  # VizDoom: restart unless stopped (game server should stay up)
  vizdoom:
    restart: unless-stopped
```

### Restart Policy Descriptions

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `no` | Never restart | Agent containers (orchestrator manages lifecycle) |
| `always` | Always restart (even on manual stop) | Not recommended for clau-doom |
| `unless-stopped` | Restart unless explicitly stopped | Persistent services (DBs, message queues) |
| `on-failure[:max]` | Restart only on non-zero exit, max retries | Application services (orchestrator, dashboard) |

### Failure Handling and Backoff

Docker Compose uses exponential backoff for restart attempts:

```
Attempt 1: Immediate restart
Attempt 2: Wait 1s, restart
Attempt 3: Wait 2s, restart
Attempt 4: Wait 4s, restart
Attempt 5: Wait 8s, restart
...
Max backoff: 1 minute
```

Monitor restart loops:

```bash
# Detect restart loops
docker compose ps --filter "status=restarting"

# View restart count
docker inspect --format='{{.RestartCount}}' <container_name>

# View last restart time
docker inspect --format='{{.State.FinishedAt}}' <container_name>
```

## Resource Management

### Memory Limits

```yaml
# docker-compose.prod.yml
services:
  opensearch:
    deploy:
      resources:
        limits:
          memory: 4G
        reservations:
          memory: 2G
    environment:
      - "ES_JAVA_OPTS=-Xms2g -Xmx2g"  # JVM heap = 50% of container limit

  mongodb:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G

  nats:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  ollama:
    deploy:
      resources:
        limits:
          memory: 8G  # LLM models require significant RAM
        reservations:
          memory: 4G

  orchestrator:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  agent:
    deploy:
      resources:
        limits:
          memory: 512M
        reservations:
          memory: 256M

  dashboard:
    deploy:
      resources:
        limits:
          memory: 1G
        reservations:
          memory: 512M

  vizdoom:
    deploy:
      resources:
        limits:
          memory: 2G
        reservations:
          memory: 1G
```

### JVM Heap Tuning (OpenSearch)

```yaml
opensearch:
  environment:
    # Set heap to 50% of container memory limit
    # Container limit: 4G → Heap: 2G
    - "ES_JAVA_OPTS=-Xms2g -Xmx2g"
    # Disable swapping (critical for performance)
    - "bootstrap.memory_lock=true"
  ulimits:
    memlock:
      soft: -1
      hard: -1
```

### OOM Kill Monitoring

```bash
# Check if container was OOM killed
docker inspect --format='{{.State.OOMKilled}}' <container_name>

# View memory usage
docker stats --no-stream

# Continuous monitoring
docker stats

# Get top memory consumers
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" | sort -k2 -h
```

### CPU Limits

```yaml
services:
  vizdoom:
    deploy:
      resources:
        limits:
          cpus: "2.0"  # Max 2 CPU cores
        reservations:
          cpus: "1.0"  # Guaranteed 1 core

  orchestrator:
    deploy:
      resources:
        limits:
          cpus: "1.0"
        reservations:
          cpus: "0.5"

  agent:
    deploy:
      resources:
        limits:
          cpus: "0.5"  # Agents are lightweight
        reservations:
          cpus: "0.25"
```

### CPU Pinning for Latency-Sensitive Agents

```yaml
# For research experiments requiring deterministic performance
agent-primary:
  deploy:
    resources:
      limits:
        cpus: "1.0"
      reservations:
        cpus: "1.0"
        devices:
          - capabilities: [cpu]
            count: 1
  cpuset: "0"  # Pin to CPU core 0
```

### GPU Reservation

```yaml
# docker-compose.gpu.yml
services:
  vizdoom:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=0  # Use first GPU
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics

  ollama:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=1  # Use second GPU (if available)
```

### NVIDIA Runtime Configuration

```bash
# Install NVIDIA Container Toolkit
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit

# Configure Docker daemon
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker

# Verify GPU access
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi
```

### Disk Management

```yaml
volumes:
  opensearch-data:
    driver: local
    driver_opts:
      type: none
      device: /mnt/research-data/opensearch
      o: bind

  mongodb-data:
    driver: local

  nats-data:
    driver: local

  ollama-models:
    driver: local
    driver_opts:
      type: none
      device: /mnt/research-data/ollama
      o: bind
```

### DuckDB File Monitoring

```bash
#!/bin/bash
# scripts/monitor_duckdb.sh

DUCKDB_DIR=/data/duckdb
THRESHOLD_GB=50

for db in "$DUCKDB_DIR"/*.duckdb; do
  size=$(du -h "$db" | cut -f1)
  size_gb=$(du -BG "$db" | cut -f1 | sed 's/G//')

  if [ "$size_gb" -gt "$THRESHOLD_GB" ]; then
    echo "WARNING: $db exceeds ${THRESHOLD_GB}GB (current: $size)"
  fi
done
```

### Log Rotation

```yaml
services:
  orchestrator:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  vizdoom:
    logging:
      driver: "json-file"
      options:
        max-size: "50m"  # Game logs can be verbose
        max-file: "5"

  dashboard:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Data Persistence & Volumes

### Volume Definitions

```yaml
volumes:
  opensearch-data:
    driver: local

  mongodb-data:
    driver: local

  nats-data:
    driver: local

  ollama-models:
    driver: local

  dashboard-build-cache:
    driver: local

services:
  opensearch:
    volumes:
      - opensearch-data:/usr/share/opensearch/data

  mongodb:
    volumes:
      - mongodb-data:/data/db

  nats:
    volumes:
      - nats-data:/data

  ollama:
    volumes:
      - ollama-models:/root/.ollama

  # Agent DuckDB files: bind mount per agent
  agent-A:
    volumes:
      - ./data/agent-A:/data

  agent-B:
    volumes:
      - ./data/agent-B:/data

  dashboard:
    volumes:
      - dashboard-build-cache:/app/.next/cache
```

### Volume Backup

```bash
#!/bin/bash
# scripts/backup_volume.sh

VOLUME_NAME=$1
BACKUP_DIR=${2:-./backups}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/${VOLUME_NAME}_${TIMESTAMP}.tar.gz"

mkdir -p "$BACKUP_DIR"

docker run --rm \
  -v "$VOLUME_NAME:/data:ro" \
  -v "$(pwd)/$BACKUP_DIR:/backup" \
  alpine \
  tar czf "/backup/$(basename $BACKUP_FILE)" -C /data .

echo "Backup created: $BACKUP_FILE"
```

### Scheduled Backup Script

```bash
#!/bin/bash
# scripts/scheduled_backup.sh

set -e

BACKUP_DIR=/mnt/backup/clau-doom
RETENTION_DAYS=30

echo "[$(date)] Starting scheduled backup"

# Backup all named volumes
for volume in opensearch-data mongodb-data nats-data ollama-models; do
  echo "Backing up $volume..."
  ./scripts/backup_volume.sh "$volume" "$BACKUP_DIR"
done

# Backup DuckDB files
echo "Backing up DuckDB files..."
tar czf "$BACKUP_DIR/duckdb_$(date +%Y%m%d_%H%M%S).tar.gz" data/*/play_logs.duckdb

# Clean old backups
find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete

echo "[$(date)] Backup complete"
```

### Backup Verification

```bash
#!/bin/bash
# scripts/verify_backup.sh

BACKUP_FILE=$1

# Extract to temp directory
TEMP_DIR=$(mktemp -d)
tar xzf "$BACKUP_FILE" -C "$TEMP_DIR"

# Check extracted files
if [ -z "$(ls -A $TEMP_DIR)" ]; then
  echo "ERROR: Backup is empty"
  exit 1
fi

echo "Backup verified: $BACKUP_FILE"
echo "Contents:"
ls -lh "$TEMP_DIR"

# Cleanup
rm -rf "$TEMP_DIR"
```

## Backup & Restore Procedures

### MongoDB Backup

```bash
#!/bin/bash
# scripts/backup_mongodb.sh

MONGODB_URI="mongodb://localhost:27017"
BACKUP_DIR=/mnt/backup/mongodb
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
ARCHIVE_FILE="$BACKUP_DIR/mongo_${TIMESTAMP}.archive.gz"

mkdir -p "$BACKUP_DIR"

docker compose exec -T mongodb \
  mongodump \
  --uri="$MONGODB_URI" \
  --archive \
  --gzip \
  > "$ARCHIVE_FILE"

echo "MongoDB backup created: $ARCHIVE_FILE"
```

### MongoDB Restore

```bash
#!/bin/bash
# scripts/restore_mongodb.sh

ARCHIVE_FILE=$1
MONGODB_URI="mongodb://localhost:27017"

if [ ! -f "$ARCHIVE_FILE" ]; then
  echo "ERROR: Archive file not found: $ARCHIVE_FILE"
  exit 1
fi

echo "WARNING: This will overwrite the current database"
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Restore cancelled"
  exit 0
fi

docker compose exec -T mongodb \
  mongorestore \
  --uri="$MONGODB_URI" \
  --archive \
  --gzip \
  --drop \
  < "$ARCHIVE_FILE"

echo "MongoDB restore complete"
```

### OpenSearch Snapshot

```bash
# Register snapshot repository (once)
curl -X PUT "localhost:9200/_snapshot/backup" -H 'Content-Type: application/json' -d'
{
  "type": "fs",
  "settings": {
    "location": "/mnt/backup/opensearch",
    "compress": true
  }
}'

# Create snapshot
SNAPSHOT_NAME="snapshot_$(date +%Y%m%d_%H%M%S)"
curl -X PUT "localhost:9200/_snapshot/backup/$SNAPSHOT_NAME?wait_for_completion=true"

# List snapshots
curl -X GET "localhost:9200/_snapshot/backup/_all"

# Restore snapshot
curl -X POST "localhost:9200/_snapshot/backup/$SNAPSHOT_NAME/_restore" -H 'Content-Type: application/json' -d'
{
  "indices": "*",
  "ignore_unavailable": true,
  "include_global_state": false
}'
```

### DuckDB Backup

```bash
#!/bin/bash
# scripts/backup_duckdb.sh

AGENT_ID=$1
DUCKDB_FILE="data/${AGENT_ID}/play_logs.duckdb"
BACKUP_DIR=/mnt/backup/duckdb/${AGENT_ID}
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$BACKUP_DIR"

# Stop writes (checkpoint WAL)
docker compose exec agent-${AGENT_ID} \
  duckdb "$DUCKDB_FILE" -c "CHECKPOINT;"

# Copy file
cp "$DUCKDB_FILE" "$BACKUP_DIR/play_logs_${TIMESTAMP}.duckdb"

echo "DuckDB backup created: $BACKUP_DIR/play_logs_${TIMESTAMP}.duckdb"
```

### Full Stack Backup Script

```bash
#!/bin/bash
# scripts/full_backup.sh

set -e

BACKUP_ROOT=/mnt/backup/clau-doom
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="$BACKUP_ROOT/$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

echo "[$(date)] Starting full stack backup to $BACKUP_DIR"

# MongoDB
echo "Backing up MongoDB..."
./scripts/backup_mongodb.sh "$BACKUP_DIR/mongodb.archive.gz"

# OpenSearch (via snapshot API)
echo "Creating OpenSearch snapshot..."
curl -X PUT "localhost:9200/_snapshot/backup/snapshot_${TIMESTAMP}?wait_for_completion=true"

# DuckDB files
echo "Backing up DuckDB files..."
for agent_dir in data/agent-*; do
  agent_id=$(basename "$agent_dir" | sed 's/agent-//')
  ./scripts/backup_duckdb.sh "$agent_id" "$BACKUP_DIR/duckdb"
done

# Named volumes
echo "Backing up named volumes..."
for volume in nats-data ollama-models; do
  ./scripts/backup_volume.sh "$volume" "$BACKUP_DIR/volumes"
done

# Verification
echo "Verifying backups..."
for file in "$BACKUP_DIR"/**/*.{tar.gz,archive.gz,duckdb}; do
  [ -f "$file" ] && ./scripts/verify_backup.sh "$file"
done

# Create manifest
cat > "$BACKUP_DIR/MANIFEST.txt" <<EOF
Backup Timestamp: $TIMESTAMP
Created: $(date)
Components:
  - MongoDB: mongodb.archive.gz
  - OpenSearch: snapshot_${TIMESTAMP}
  - DuckDB: duckdb/*.duckdb
  - Volumes: volumes/*.tar.gz
EOF

echo "[$(date)] Full backup complete: $BACKUP_DIR"
```

### Retention Policy

```bash
#!/bin/bash
# scripts/cleanup_backups.sh

BACKUP_ROOT=/mnt/backup/clau-doom

# Keep 7 daily backups
find "$BACKUP_ROOT" -maxdepth 1 -type d -mtime +7 -name "202*" -exec rm -rf {} \;

# Keep 4 weekly backups (older than 7 days, keep one per week)
# Implementation depends on naming convention
```

## Scaling

### Agent Scaling

```bash
# Scale agent containers to 4 instances
docker compose up --scale agent=4 -d

# Verify scaling
docker compose ps agent

# Scale down
docker compose up --scale agent=1 -d
```

### NATS Queue Groups for Load Distribution

```yaml
# Agent subscribes to queue group
# orchestrator/internal/nats/subscriber.go
sub, err := nc.QueueSubscribe("doom.episode", "agents", func(msg *nats.Msg) {
  // Process episode
})

# Multiple agent containers automatically distribute work
# NATS ensures only one agent in "agents" group receives each message
```

### Orchestrator Container Pool Management

```yaml
# orchestrator configuration
orchestrator:
  environment:
    - AGENT_POOL_MIN=2
    - AGENT_POOL_MAX=10
    - AGENT_SCALE_THRESHOLD=0.8  # Scale up when 80% busy
```

### Research Experiment Scaling

```bash
# Run DOE experiment with 4 parallel agents
# Each agent processes a subset of experimental runs

# Scale up for experiment
docker compose up --scale agent=4 -d

# Run experiment (orchestrator distributes work via NATS)
docker compose exec orchestrator \
  /clau-doom run-experiment --doe-id=DOE-042

# Scale down after completion
docker compose up --scale agent=2 -d
```

### Generation-Based Scaling

```bash
#!/bin/bash
# scripts/generation_scale.sh

GENERATION=$1

if [ "$GENERATION" -le 3 ]; then
  # Early generations: high exploration
  AGENT_COUNT=6
elif [ "$GENERATION" -le 7 ]; then
  # Mid generations: balanced
  AGENT_COUNT=4
else
  # Late generations: fine-tuning
  AGENT_COUNT=2
fi

echo "Scaling to $AGENT_COUNT agents for generation $GENERATION"
docker compose up --scale agent=$AGENT_COUNT -d
```

## Operational Procedures

### Starting the Stack

```bash
#!/bin/bash
# scripts/start_stack.sh

set -e

echo "Starting clau-doom research stack..."

# Start production stack
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Wait for all services to be healthy
echo "Waiting for services to become healthy..."
timeout 120 bash -c '
  while [ $(docker compose ps --filter "health=healthy" --format json | jq -s "length") -lt 7 ]; do
    sleep 5
  done
'

# Verify health
echo "Service health status:"
docker compose ps --format "table {{.Name}}\t{{.Status}}"

# Smoke tests
echo "Running smoke tests..."
./scripts/smoke_test.sh

echo "Stack is ready!"
```

### Health Check Verification After Startup

```bash
#!/bin/bash
# scripts/verify_health.sh

SERVICES=(opensearch mongodb nats ollama orchestrator dashboard vizdoom)

for service in "${SERVICES[@]}"; do
  health=$(docker compose ps --filter "name=$service" --format "{{.Status}}" | grep -o "healthy")

  if [ "$health" != "healthy" ]; then
    echo "ERROR: $service is not healthy"
    docker compose logs --tail=50 "$service"
    exit 1
  fi

  echo "✓ $service is healthy"
done

echo "All services healthy"
```

### Smoke Test Checklist

```bash
#!/bin/bash
# scripts/smoke_test.sh

set -e

echo "Running smoke tests..."

# Test orchestrator gRPC
grpcurl -plaintext localhost:50051 list || exit 1
echo "✓ Orchestrator gRPC responding"

# Test OpenSearch
curl -sf http://localhost:9200/_cluster/health || exit 1
echo "✓ OpenSearch cluster healthy"

# Test MongoDB
docker compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" || exit 1
echo "✓ MongoDB responding"

# Test NATS
curl -sf http://localhost:8222/varz || exit 1
echo "✓ NATS responding"

# Test Dashboard
curl -sf http://localhost:3000/api/health || exit 1
echo "✓ Dashboard responding"

# Test noVNC
curl -sf http://localhost:6080 || exit 1
echo "✓ noVNC web viewer responding"

echo "All smoke tests passed"
```

### Graceful Shutdown

```bash
#!/bin/bash
# scripts/graceful_shutdown.sh

set -e

echo "Initiating graceful shutdown..."

# Stop accepting new work (signal orchestrator)
docker compose exec orchestrator kill -SIGTERM 1

# Wait for in-flight episodes to complete
echo "Waiting for active episodes to complete (max 5 minutes)..."
sleep 300

# Checkpoint DuckDB files
echo "Checkpointing DuckDB files..."
for agent_dir in data/agent-*; do
  duckdb_file="$agent_dir/play_logs.duckdb"
  docker compose exec agent duckdb "$duckdb_file" -c "CHECKPOINT;"
done

# Stop services gracefully
echo "Stopping services..."
docker compose down --timeout 30

echo "Graceful shutdown complete"
```

### Data Flush Verification Before Shutdown

```bash
#!/bin/bash
# Verify all data is flushed before shutdown

# OpenSearch: force merge and flush
curl -X POST "localhost:9200/_flush/synced"

# MongoDB: flush to disk
docker compose exec mongodb mongosh --eval "db.adminCommand({fsync: 1})"

# NATS: checkpoint JetStream
docker compose exec nats nats stream ls

echo "All data flushed"
```

### Agent Drain Procedure

```bash
# Mark agent as draining (stops accepting new work)
docker compose exec orchestrator \
  /clau-doom agent drain --agent-id=agent-A

# Wait for current episode to finish
docker compose exec orchestrator \
  /clau-doom agent wait --agent-id=agent-A

# Stop agent container
docker compose stop agent-A
```

### Log Management

```bash
# View logs for specific service
docker compose logs -f --tail=100 orchestrator

# View logs with timestamps
docker compose logs -f --timestamps vizdoom

# Filter logs by level (if JSON logging)
docker compose logs orchestrator | jq 'select(.level=="error")'

# Search logs for pattern
docker compose logs --no-color orchestrator | grep "episode complete"
```

### JSON Log Parsing with jq

```bash
# Extract error messages
docker compose logs orchestrator 2>&1 | jq -r 'select(.level=="error") | .msg'

# Count errors by type
docker compose logs orchestrator 2>&1 | jq -r 'select(.level=="error") | .error_type' | sort | uniq -c

# Get latency statistics
docker compose logs orchestrator 2>&1 | jq -r '.latency_ms' | awk '{sum+=$1; count++} END {print "Avg:", sum/count, "ms"}'
```

### Log Aggregation to File

```bash
#!/bin/bash
# scripts/aggregate_logs.sh

LOG_DIR=/var/log/clau-doom
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

mkdir -p "$LOG_DIR"

for service in orchestrator agent dashboard vizdoom; do
  docker compose logs --no-color --timestamps "$service" > "$LOG_DIR/${service}_${TIMESTAMP}.log"
done

echo "Logs aggregated to $LOG_DIR"
```

### Service Updates

```bash
# Update single service (zero-downtime for stateless services)
docker compose build orchestrator
docker compose up -d --no-deps orchestrator

# Verify update
docker compose ps orchestrator

# Rollback if needed
docker compose down orchestrator
docker compose up -d orchestrator
```

### Zero-Downtime Update for Dashboard

```bash
# Build new image
docker compose build dashboard

# Start new container alongside old
docker compose up -d --scale dashboard=2 --no-recreate

# Verify new container is healthy
sleep 10
NEW_CONTAINER=$(docker compose ps dashboard --format json | jq -r '.[1].Name')
docker inspect --format='{{.State.Health.Status}}' "$NEW_CONTAINER"

# Stop old container
OLD_CONTAINER=$(docker compose ps dashboard --format json | jq -r '.[0].Name')
docker stop "$OLD_CONTAINER"

# Scale down to 1
docker compose up -d --scale dashboard=1
```

### Agent Image Update Procedure

```bash
#!/bin/bash
# scripts/update_agent_image.sh

set -e

# Build new agent image
docker compose build agent

# Tag with version
VERSION=$(git rev-parse --short HEAD)
docker tag clau-doom-agent:latest clau-doom-agent:$VERSION

# Orchestrator will pull new image for new agent containers
# Existing agents continue running until completed

echo "Agent image updated to $VERSION"
echo "New agents will use updated image"
```

## Troubleshooting

### Common Issues

#### Port Conflicts

```bash
# Check what's using a port
netstat -tlnp | grep 50051
lsof -i :50051

# Find Docker containers using port
docker ps --filter "publish=50051"

# Change port in docker-compose.yml
ports:
  - "50052:50051"  # Map to different host port
```

#### Volume Permissions

```bash
# Check volume ownership
docker run --rm -v opensearch-data:/data alpine ls -la /data

# Fix permissions
docker run --rm -v opensearch-data:/data alpine chown -R 1000:1000 /data

# For bind mounts
sudo chown -R $(id -u):$(id -g) ./data/agent-A
```

#### OOM Kills

```bash
# Check if container was OOM killed
docker inspect --format='{{.State.OOMKilled}}' clau-doom-orchestrator

# View OOM events
journalctl -u docker.service | grep -i oom

# Increase memory limit
# In docker-compose.prod.yml
deploy:
  resources:
    limits:
      memory: 2G  # Increase from 1G
```

#### Network Connectivity

```bash
# Test container-to-container connectivity
docker compose exec orchestrator ping mongodb

# DNS resolution test
docker compose exec orchestrator nslookup opensearch

# Port reachability test
docker compose exec orchestrator nc -zv nats 4222

# Network inspection
docker network inspect clau-doom_clau-doom-net
```

### Diagnostic Commands

```bash
# Service status
docker compose ps

# Resource usage (real-time)
docker stats

# Resource usage (snapshot)
docker stats --no-stream

# Get top memory consumers
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}" | sort -k2 -hr | head -5

# Get top CPU consumers
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}" | sort -k2 -nr | head -5

# Shell access to container
docker compose exec orchestrator sh

# Run command in container
docker compose exec mongodb mongosh

# Inspect container configuration
docker inspect clau-doom-orchestrator | jq '.[0].Config'

# View real-time events
docker compose events

# View events since timestamp
docker compose events --since "2024-01-01T00:00:00"
```

## Anti-Patterns to Avoid

### No Health Checks (Silent Failures)

**Wrong:**
```yaml
orchestrator:
  image: clau-doom-orchestrator
  # No healthcheck
```

**Correct:**
```yaml
orchestrator:
  image: clau-doom-orchestrator
  healthcheck:
    test: ["CMD", "grpc_health_probe", "-addr=:50051"]
    interval: 10s
    timeout: 5s
    retries: 3
```

### No Resource Limits (Runaway Containers)

**Wrong:**
```yaml
vizdoom:
  image: clau-doom-vizdoom
  # No resource limits
```

**Correct:**
```yaml
vizdoom:
  image: clau-doom-vizdoom
  deploy:
    resources:
      limits:
        cpus: "2.0"
        memory: 2G
```

### Using restart: always for Managed Containers

**Wrong:**
```yaml
agent:
  restart: always  # Interferes with orchestrator lifecycle management
```

**Correct:**
```yaml
agent:
  restart: "no"  # Orchestrator manages agent lifecycle
```

### No Backup Strategy for Persistent Data

**Wrong:**
```yaml
# No backup, no retention policy
mongodb:
  volumes:
    - mongodb-data:/data/db
```

**Correct:**
```yaml
mongodb:
  volumes:
    - mongodb-data:/data/db

# + Scheduled backup script (cron)
# + Retention policy (7 daily, 4 weekly)
# + Verification after backup
```

### Exposing Debug Ports in Production

**Wrong:**
```yaml
# docker-compose.yml (used in production)
orchestrator:
  ports:
    - "2345:2345"  # Delve debugger port exposed
```

**Correct:**
```yaml
# docker-compose.yml (production)
orchestrator:
  # No debug ports

# docker-compose.dev.yml (development only)
orchestrator:
  ports:
    - "2345:2345"  # Debug port only in dev
```

### Not Monitoring Disk Usage for Volumes

**Wrong:**
```yaml
# No monitoring, volumes grow unbounded
volumes:
  duckdb-data:
  opensearch-data:
```

**Correct:**
```bash
# Add monitoring script
#!/bin/bash
# scripts/monitor_volumes.sh

docker volume ls --format "{{.Name}}" | while read vol; do
  size=$(docker run --rm -v $vol:/data alpine du -sh /data | cut -f1)
  echo "$vol: $size"
done
```
