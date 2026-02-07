# Deployment Reference Guide

Reference documentation for deployment and operations in clau-doom.

## Key Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Docker Production Guide](https://docs.docker.com/config/containers/start-containers-automatically/)
- [systemd Service Management](https://www.freedesktop.org/software/systemd/man/systemd.service.html)
- [MongoDB Backup Tools](https://www.mongodb.com/docs/database-tools/mongodump/)
- [OpenSearch Snapshot API](https://opensearch.org/docs/latest/tuning-your-cluster/availability-and-recovery/snapshots/index/)

## clau-doom Context

All services in clau-doom run via Docker Compose. Research workloads require reliable data persistence (DuckDB files, OpenSearch indices, MongoDB collections) and robust recovery mechanisms. This guide covers production configuration, health monitoring, backup strategies, and operational procedures for running long-duration experiments.

## Docker Compose Production Configuration

### Production Compose File Structure

```yaml
# docker-compose.prod.yml
version: "3.8"

services:
  orchestrator:
    image: clau-doom/orchestrator:${VERSION}
    container_name: orchestrator
    restart: unless-stopped
    environment:
      - OPENSEARCH_URL=${OPENSEARCH_URL}
      - MONGO_URL=${MONGO_URL}
      - NATS_URL=${NATS_URL}
      - LOG_LEVEL=${LOG_LEVEL:-info}
    env_file:
      - .env.prod
    ports:
      - "${ORCHESTRATOR_HTTP_PORT:-8080}:8080"
      - "${ORCHESTRATOR_GRPC_PORT:-50050}:50050"
    volumes:
      - ./volumes:/data/volumes:rw
      - ./config/orchestrator.yaml:/config/orchestrator.yaml:ro
    depends_on:
      opensearch:
        condition: service_healthy
      mongo:
        condition: service_healthy
      nats:
        condition: service_started
    networks:
      - clau-doom-internal
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G
        reservations:
          cpus: "0.5"
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  opensearch:
    image: opensearchproject/opensearch:2.12.0
    container_name: opensearch
    restart: unless-stopped
    environment:
      - discovery.type=single-node
      - plugins.security.disabled=true
      - "OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g"
      - bootstrap.memory_lock=true
    ulimits:
      memlock:
        soft: -1
        hard: -1
      nofile:
        soft: 65536
        hard: 65536
    volumes:
      - opensearch-data:/usr/share/opensearch/data
      - ./config/opensearch.yml:/usr/share/opensearch/config/opensearch.yml:ro
    ports:
      - "9200:9200"
    networks:
      - clau-doom-internal
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 4G
        reservations:
          cpus: "1.0"
          memory: 2G
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health | grep -q '\"status\":\"green\"\\|\"status\":\"yellow\"'"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s

  mongo:
    image: mongo:7.0
    container_name: mongo
    restart: unless-stopped
    volumes:
      - mongo-data:/data/db
      - ./backups/mongo:/backups:rw
    ports:
      - "27017:27017"
    networks:
      - clau-doom-internal
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 20s
    command: ["mongod", "--wiredTigerCacheSizeGB", "0.5"]

  nats:
    image: nats:2.10-alpine
    container_name: nats
    restart: unless-stopped
    command: ["--jetstream", "--store_dir=/data", "--max_memory=512M", "--max_file_store=2G"]
    volumes:
      - nats-data:/data
    ports:
      - "4222:4222"
      - "8222:8222"
    networks:
      - clau-doom-internal
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
    healthcheck:
      test: ["CMD", "nats-server", "--signal", "ldm"]
      interval: 10s
      timeout: 5s
      retries: 3

  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    restart: unless-stopped
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - clau-doom-internal
    deploy:
      resources:
        limits:
          cpus: "4.0"
          memory: 4G
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 60s

  dashboard:
    image: clau-doom/dashboard:${VERSION}
    container_name: dashboard
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - ORCHESTRATOR_URL=http://orchestrator:8080
      - OPENSEARCH_URL=http://opensearch:9200
      - NODE_ENV=production
    depends_on:
      orchestrator:
        condition: service_healthy
    networks:
      - clau-doom-internal
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/"]
      interval: 15s
      timeout: 5s
      retries: 3

  player:
    image: clau-doom/doom-player:${VERSION}
    restart: on-failure
    environment:
      - AGENT_ID=${AGENT_ID}
      - GENERATION=${GENERATION}
      - OPENSEARCH_URL=http://opensearch:9200
      - NATS_URL=nats://nats:4222
    volumes:
      - ./volumes/agents/active/${AGENT_MD_FILE}:/agent/config/agent.md:ro
      - ./volumes/data/${AGENT_ID}:/agent/data:rw
    depends_on:
      opensearch:
        condition: service_healthy
      nats:
        condition: service_started
    networks:
      - clau-doom-internal
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3
        window: 120s
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:${NOVNC_PORT}"]
      interval: 15s
      timeout: 5s
      retries: 3
      start_period: 20s

volumes:
  opensearch-data:
    driver: local
  mongo-data:
    driver: local
  nats-data:
    driver: local
  ollama-data:
    driver: local

networks:
  clau-doom-internal:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

### Environment Variable Management

```bash
# .env.prod
VERSION=1.0.0

# Service URLs (internal network)
OPENSEARCH_URL=http://opensearch:9200
MONGO_URL=mongodb://mongo:27017
NATS_URL=nats://nats:4222

# Ports (external access)
ORCHESTRATOR_HTTP_PORT=8080
ORCHESTRATOR_GRPC_PORT=50050

# Logging
LOG_LEVEL=info

# Agent configuration (for dynamically spawned players)
AGENT_ID=PLAYER_001
GENERATION=1
AGENT_MD_FILE=DOOM_PLAYER_001.MD
NOVNC_PORT=6901
```

### Override File for Secrets

```yaml
# docker-compose.override.yml (not tracked in git)
version: "3.8"

services:
  orchestrator:
    environment:
      - CLAUDE_API_KEY=${CLAUDE_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
```

### Service Startup Order and Dependencies

```yaml
# Dependency chain
depends_on:
  opensearch:
    condition: service_healthy  # Wait for cluster health
  mongo:
    condition: service_healthy  # Wait for ping success
  nats:
    condition: service_started  # Start immediately after container starts

# Startup sequence:
# 1. opensearch, mongo, nats (parallel)
# 2. orchestrator (after opensearch + mongo healthy)
# 3. dashboard (after orchestrator healthy)
# 4. player containers (after opensearch + nats ready)
```

### Network Configuration

```yaml
networks:
  clau-doom-internal:
    driver: bridge
    internal: false  # Set to true to prevent external access
    ipam:
      driver: default
      config:
        - subnet: 172.20.0.0/16
          gateway: 172.20.0.1

# Isolated network for sensitive services
networks:
  clau-doom-backend:
    driver: bridge
    internal: true  # No external internet access
```

## Health Checks

### OpenSearch Health Check

```yaml
healthcheck:
  test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health | grep -q '\"status\":\"green\"\\|\"status\":\"yellow\"'"]
  interval: 30s
  timeout: 10s
  retries: 5
  start_period: 60s
```

```bash
# Manual health check
curl -s http://localhost:9200/_cluster/health?pretty

# Expected output
{
  "cluster_name": "opensearch-cluster",
  "status": "green",
  "number_of_nodes": 1,
  "active_primary_shards": 5,
  "active_shards": 5
}
```

### MongoDB Health Check

```yaml
healthcheck:
  test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
  interval: 15s
  timeout: 5s
  retries: 3
  start_period: 20s
```

```bash
# Manual health check
docker exec mongo mongosh --eval "db.adminCommand('ping')"

# Expected: { ok: 1 }
```

### NATS Health Check

```yaml
healthcheck:
  test: ["CMD", "nats-server", "--signal", "ldm"]
  interval: 10s
  timeout: 5s
  retries: 3
```

```bash
# Manual health check via monitoring endpoint
curl http://localhost:8222/healthz

# Expected: ok
```

### Ollama Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:11434/api/tags"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 60s
```

```bash
# Manual health check
curl http://localhost:11434/api/tags

# Expected: JSON list of loaded models
```

### VizDoom Player Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:6901"]
  interval: 15s
  timeout: 5s
  retries: 3
  start_period: 20s
```

```bash
# Custom health script (inside container)
#!/bin/bash
# /app/healthcheck.sh

# Check Xvfb process
pgrep Xvfb > /dev/null || exit 1

# Check VNC server
pgrep x11vnc > /dev/null || exit 1

# Check noVNC proxy
curl -sf http://localhost:${NOVNC_PORT} > /dev/null || exit 1

# Check agent-core process
pgrep agent-core > /dev/null || exit 1

exit 0
```

### Dashboard Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/"]
  interval: 15s
  timeout: 5s
  retries: 3
```

### Orchestrator Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
  interval: 15s
  timeout: 5s
  retries: 3
  start_period: 30s
```

### Agent gRPC Health Check

```yaml
healthcheck:
  test: ["CMD", "grpc_health_probe", "-addr=:50051"]
  interval: 10s
  timeout: 5s
  retries: 3
```

## Restart Policies

### Persistent Services (unless-stopped)

```yaml
# Restart unless manually stopped by user
restart: unless-stopped

# Use for:
# - orchestrator
# - opensearch
# - mongo
# - nats
# - ollama
# - dashboard
```

### Transient Services (on-failure)

```yaml
# Restart only on failure, with limits
restart: on-failure

# Use for:
# - player containers (may exit intentionally after experiment)
```

### Advanced Restart Configuration

```yaml
deploy:
  restart_policy:
    condition: on-failure  # only | on-failure | any
    delay: 5s              # delay between restarts
    max_attempts: 3        # maximum restart attempts
    window: 120s           # time window to evaluate attempts
```

### Backoff Configuration

```yaml
# Example: exponential backoff for player restarts
# Attempt 1: wait 5s
# Attempt 2: wait 10s
# Attempt 3: wait 20s
# Max attempts: 3 within 120s window

deploy:
  restart_policy:
    condition: on-failure
    delay: 5s
    max_attempts: 3
    window: 120s
```

## Resource Limits

### Memory Limits Per Service

```yaml
services:
  opensearch:
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 4G
        reservations:
          cpus: "1.0"
          memory: 2G
    environment:
      - "OPENSEARCH_JAVA_OPTS=-Xms2g -Xmx2g"  # Heap size matches limit

  mongo:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G
    command: ["mongod", "--wiredTigerCacheSizeGB", "0.5"]

  nats:
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
    command: ["--max_memory=512M", "--max_file_store=2G"]

  ollama:
    deploy:
      resources:
        limits:
          cpus: "4.0"
          memory: 4G
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]

  orchestrator:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G
        reservations:
          cpus: "0.5"
          memory: 512M

  dashboard:
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M

  player:
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
```

### CPU Limits for Agent Containers

```yaml
# Prevent runaway agent processes
player:
  deploy:
    resources:
      limits:
        cpus: "0.5"  # 50% of one CPU core
        memory: 512M
      reservations:
        cpus: "0.25"
        memory: 256M
```

### GPU Reservation for Ollama

```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1  # Reserve 1 GPU
            capabilities: [gpu]
  environment:
    - NVIDIA_VISIBLE_DEVICES=all
```

### Recommended Values for Research Workloads

| Service | Memory Limit | CPU Limit | Rationale |
|---------|--------------|-----------|-----------|
| OpenSearch | 4GB | 2.0 | Vector search + aggregations for RAG |
| MongoDB | 1GB | 1.0 | Knowledge catalog storage |
| NATS | 512MB | 0.5 | Lightweight message broker |
| Ollama | 4GB + GPU | 4.0 | Model inference (embedding generation) |
| Orchestrator | 1GB | 1.0 | Lifecycle management, gRPC server |
| Dashboard | 512MB | 0.5 | Next.js frontend |
| Player (each) | 512MB | 0.5 | VizDoom + agent-core + Xvfb |

## Data Persistence

### Named Volumes

```yaml
volumes:
  opensearch-data:
    driver: local
    driver_opts:
      type: none
      device: /mnt/research/opensearch
      o: bind

  mongo-data:
    driver: local
    driver_opts:
      type: none
      device: /mnt/research/mongo
      o: bind

  nats-data:
    driver: local

  ollama-data:
    driver: local
```

### Volume Mount Patterns

```yaml
# Agent configuration (read-only)
volumes:
  - ./volumes/agents/active/${AGENT_MD_FILE}:/agent/config/agent.md:ro

# Agent play data (read-write, persistent)
volumes:
  - ./volumes/data/${AGENT_ID}:/agent/data:rw

# Research documents (shared with host)
volumes:
  - ./volumes/research:/data/research:rw

# Config files (read-only)
volumes:
  - ./config/orchestrator.yaml:/config/orchestrator.yaml:ro
```

### Data Directory Structure

```
/mnt/research/
├── opensearch/          # OpenSearch indices
│   └── nodes/
│       └── 0/
│           └── indices/
├── mongo/               # MongoDB collections
│   ├── collection-0--*.wt
│   └── WiredTiger
├── nats/                # NATS JetStream
│   └── jetstream/
├── ollama/              # Ollama models
│   └── models/
└── volumes/             # Host-mounted volumes
    ├── agents/
    │   ├── active/      # Active agent MD files
    │   └── archive/     # Retired agents
    ├── data/            # Per-agent DuckDB files
    │   ├── PLAYER_001/
    │   │   └── game.duckdb
    │   └── PLAYER_002/
    └── research/        # Research documents
        ├── RESEARCH_LOG.md
        ├── orders/
        └── reports/
```

## Backup & Restore

### MongoDB Backup

```bash
# Backup with mongodump
docker exec mongo mongodump \
    --out=/backups/$(date +%Y%m%d_%H%M%S) \
    --gzip

# Restore from backup
docker exec mongo mongorestore \
    --gzip \
    /backups/20240115_120000
```

```bash
# Automated backup script
#!/bin/bash
# /scripts/backup-mongo.sh

BACKUP_DIR=/mnt/research/backups/mongo
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

# Create backup
docker exec mongo mongodump \
    --out=/backups/${DATE} \
    --gzip

# Copy to host (if not using bind mount)
docker cp mongo:/backups/${DATE} ${BACKUP_DIR}/

# Remove old backups
find ${BACKUP_DIR} -type d -mtime +${RETENTION_DAYS} -exec rm -rf {} +

echo "Backup complete: ${BACKUP_DIR}/${DATE}"
```

### OpenSearch Snapshot

```bash
# Register snapshot repository
curl -X PUT "localhost:9200/_snapshot/research_backup" \
    -H 'Content-Type: application/json' \
    -d '{
  "type": "fs",
  "settings": {
    "location": "/usr/share/opensearch/backups",
    "compress": true
  }
}'

# Create snapshot
curl -X PUT "localhost:9200/_snapshot/research_backup/snapshot_$(date +%Y%m%d_%H%M%S)?wait_for_completion=true"

# List snapshots
curl -X GET "localhost:9200/_snapshot/research_backup/_all?pretty"

# Restore snapshot
curl -X POST "localhost:9200/_snapshot/research_backup/snapshot_20240115_120000/_restore"
```

### DuckDB Backup

```bash
# DuckDB is a single file, simple file copy
#!/bin/bash
# /scripts/backup-duckdb.sh

BACKUP_DIR=/mnt/research/backups/duckdb
DATE=$(date +%Y%m%d_%H%M%S)

for player in $(ls volumes/data/); do
    if [ -f "volumes/data/${player}/game.duckdb" ]; then
        mkdir -p ${BACKUP_DIR}/${DATE}
        cp volumes/data/${player}/game.duckdb \
            ${BACKUP_DIR}/${DATE}/${player}_game.duckdb
    fi
done

echo "DuckDB backup complete: ${BACKUP_DIR}/${DATE}"
```

### Volume Backup (Generic)

```bash
# Backup named volume using temporary container
docker run --rm \
    -v opensearch-data:/data \
    -v /mnt/research/backups/opensearch:/backup \
    alpine tar czf /backup/opensearch_$(date +%Y%m%d_%H%M%S).tar.gz -C /data .

# Restore named volume
docker run --rm \
    -v opensearch-data:/data \
    -v /mnt/research/backups/opensearch:/backup \
    alpine sh -c "cd /data && tar xzf /backup/opensearch_20240115_120000.tar.gz"
```

### Automated Backup Scheduling

```bash
# crontab -e

# MongoDB daily at 2 AM
0 2 * * * /scripts/backup-mongo.sh

# DuckDB daily at 3 AM
0 3 * * * /scripts/backup-duckdb.sh

# OpenSearch weekly on Sunday at 4 AM
0 4 * * 0 /scripts/backup-opensearch.sh
```

## Scaling

### Horizontal Scaling of Agent Containers

```bash
# Scale to 8 player instances
docker compose up -d --scale player=8

# Requires dynamic port assignment
docker compose -f docker-compose.yml \
    -f docker-compose.scale.yml \
    up -d --scale player=8
```

```yaml
# docker-compose.scale.yml
services:
  player:
    ports:
      - "6901-6908:6901"  # Port range for 8 instances
      - "50051-50058:50051"
```

### NATS Queue Groups for Load Distribution

```yaml
# In agent-core config
nats:
  url: nats://nats:4222
  queue_group: agent_pool  # All agents in same queue group

# NATS distributes messages round-robin across queue group members
# Enables horizontal scaling of agent processing
```

### OpenSearch Node Addition

```yaml
# docker-compose.opensearch-cluster.yml
services:
  opensearch-1:
    image: opensearchproject/opensearch:2.12.0
    environment:
      - cluster.name=opensearch-cluster
      - node.name=opensearch-1
      - discovery.seed_hosts=opensearch-1,opensearch-2,opensearch-3
      - cluster.initial_cluster_manager_nodes=opensearch-1,opensearch-2,opensearch-3
    volumes:
      - opensearch-data-1:/usr/share/opensearch/data
    networks:
      - clau-doom-internal

  opensearch-2:
    image: opensearchproject/opensearch:2.12.0
    environment:
      - cluster.name=opensearch-cluster
      - node.name=opensearch-2
      - discovery.seed_hosts=opensearch-1,opensearch-2,opensearch-3
    volumes:
      - opensearch-data-2:/usr/share/opensearch/data
    networks:
      - clau-doom-internal

  opensearch-3:
    image: opensearchproject/opensearch:2.12.0
    environment:
      - cluster.name=opensearch-cluster
      - node.name=opensearch-3
      - discovery.seed_hosts=opensearch-1,opensearch-2,opensearch-3
    volumes:
      - opensearch-data-3:/usr/share/opensearch/data
    networks:
      - clau-doom-internal
```

### Scaling Considerations for DOE Parallelism

```yaml
# For parallel DOE execution (R009)
# Spawn 4 parallel player instances (max per R009)

# Example: 2x3 factorial design, parallel execution
# Run 1-3: instances 1-3 (parallel)
# Run 4-6: instances 1-3 (reused after completion)

# Resource requirements:
# - 4 player containers: 4 * 512MB = 2GB RAM
# - OpenSearch: 4GB RAM (handle parallel writes)
# - MongoDB: 1GB RAM
# - Total: ~8GB RAM for parallel DOE execution
```

## Operational Procedures

### Starting the Full Stack

```bash
# Production environment
docker compose -f docker-compose.prod.yml up -d

# Wait for all health checks to pass
docker compose -f docker-compose.prod.yml ps

# Check logs for errors
docker compose -f docker-compose.prod.yml logs -f
```

### Stopping Gracefully

```bash
# Stop all services (containers remain)
docker compose -f docker-compose.prod.yml stop

# Stop and remove containers (volumes persist)
docker compose -f docker-compose.prod.yml down

# Stop, remove containers and volumes (DESTRUCTIVE)
docker compose -f docker-compose.prod.yml down -v
```

### Viewing Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f orchestrator

# Last 100 lines
docker compose logs --tail=100 opensearch

# Since timestamp
docker compose logs --since 2024-01-15T12:00:00 mongo

# Filter by level (requires structured logging)
docker compose logs mongo | grep ERROR
```

### Entering Containers for Debugging

```bash
# Shell into running container
docker compose exec orchestrator /bin/sh

# Execute one-off command
docker compose exec mongo mongosh --eval "db.stats()"

# Run new container with same image (for debugging)
docker compose run --rm player /bin/bash
```

### Updating Individual Services Without Downtime

```bash
# Pull new image
docker compose pull orchestrator

# Recreate only orchestrator (zero downtime with health checks)
docker compose up -d --no-deps orchestrator

# Verify health
docker compose ps orchestrator
```

### Rolling Out New Agent Images

```bash
# Build new agent image with version tag
docker build -t clau-doom/doom-player:1.1.0 -f docker/doom-player/Dockerfile .

# Update .env.prod
VERSION=1.1.0

# Stop players gracefully (finish current episode)
docker compose stop player-001 player-002

# Start with new image
docker compose up -d player-001 player-002

# Verify
docker compose ps | grep player
```

## Troubleshooting

### Common Startup Failures

```bash
# OpenSearch fails to start
# Symptom: "max virtual memory areas vm.max_map_count is too low"
# Fix:
sudo sysctl -w vm.max_map_count=262144
echo "vm.max_map_count=262144" | sudo tee -a /etc/sysctl.conf

# MongoDB fails to start
# Symptom: "WiredTiger error: Permission denied"
# Fix: Check volume permissions
sudo chown -R 999:999 /mnt/research/mongo

# NATS fails to start
# Symptom: "jetstream disabled"
# Fix: Ensure --jetstream flag in command
docker compose logs nats | grep jetstream
```

### Port Conflicts

```bash
# Check if port is already in use
sudo lsof -i :9200
sudo netstat -tuln | grep 9200

# Kill conflicting process
sudo kill -9 $(lsof -t -i:9200)

# Or change port in .env.prod
OPENSEARCH_PORT=9201
```

### Volume Permission Issues

```bash
# Fix volume permissions
# OpenSearch requires UID 1000
sudo chown -R 1000:1000 /mnt/research/opensearch

# MongoDB requires UID 999
sudo chown -R 999:999 /mnt/research/mongo

# Generic fix (match container user)
docker compose exec opensearch id  # Check UID
sudo chown -R <UID>:<GID> /path/to/volume
```

### Out-of-Memory Kills

```bash
# Check for OOM kills
docker inspect orchestrator | grep -i oom

# Increase memory limit in compose file
deploy:
  resources:
    limits:
      memory: 2G

# Monitor memory usage
docker stats
```

### Network Connectivity Between Services

```bash
# Check if services can reach each other
docker compose exec orchestrator ping opensearch
docker compose exec dashboard curl http://orchestrator:8080/health

# Check DNS resolution
docker compose exec orchestrator nslookup opensearch

# Check network configuration
docker network inspect clau-doom_clau-doom-internal

# Verify service names match in environment variables
docker compose exec orchestrator env | grep URL
```

### Player Container Crashes

```bash
# Check player logs
docker compose logs player-001 | tail -50

# Common issues:
# 1. Xvfb failed to start
# Fix: Ensure DISPLAY=:99 is set, check Xvfb process

# 2. Agent MD file missing
# Fix: Ensure volume mount path is correct
docker compose exec player-001 ls -la /agent/config/

# 3. DuckDB permission denied
# Fix: Ensure /agent/data is writable
docker compose exec player-001 touch /agent/data/test.txt
```

