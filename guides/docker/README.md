# Docker Reference Guide

Reference documentation for Docker infrastructure in clau-doom.

## Key Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)
- [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/)
- [VizDoom Build Guide](https://github.com/Farama-Foundation/ViZDoom/blob/master/doc/Building.md)

## clau-doom Context

The entire clau-doom stack runs via Docker Compose. Each DOOM player is a separate container running VizDoom + Xvfb + noVNC + Rust agent. Supporting services (OpenSearch, MongoDB, NATS, Ollama, Dashboard) are additional containers.

## VizDoom Container Dockerfile

### doom-player Dockerfile

```dockerfile
# infra/docker/doom-player/Dockerfile

# ---- Stage 1: Build Rust agent ----
FROM rust:1.77-bookworm AS rust-builder

WORKDIR /build
COPY agent-core/ ./agent-core/
COPY proto/ ./proto/

RUN cd agent-core && \
    cargo build --release && \
    cp target/release/agent-core /build/agent-core-bin

# ---- Stage 2: Build VizDoom + Runtime ----
FROM ubuntu:24.04

# Prevent interactive prompts during build
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies for VizDoom + display
RUN apt-get update && apt-get install -y --no-install-recommends \
    # VizDoom dependencies
    cmake g++ git libboost-all-dev libsdl2-dev libfreetype-dev \
    libopenal-dev libfluidsynth-dev libmpg123-dev libsndfile1-dev \
    # Python for VizDoom glue
    python3 python3-pip python3-numpy \
    # Virtual display
    xvfb x11vnc \
    # noVNC
    novnc websockify \
    # Utilities
    wget curl net-tools procps \
    && rm -rf /var/lib/apt/lists/*

# Install VizDoom
RUN pip3 install --no-cache-dir vizdoom==1.2.3

# Install Python glue dependencies
COPY glue/requirements.txt /app/glue/requirements.txt
RUN pip3 install --no-cache-dir -r /app/glue/requirements.txt

# Copy application files
COPY glue/ /app/glue/
COPY scenarios/ /app/scenarios/
COPY --from=rust-builder /build/agent-core-bin /app/agent-core

# Copy entrypoint
COPY infra/docker/doom-player/entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Environment
ENV DISPLAY=:99
ENV AGENT_ID=unknown
ENV GENERATION=0
ENV OPENSEARCH_URL=http://opensearch:9200
ENV NATS_URL=nats://nats:4222
ENV NOVNC_PORT=6901

# Volumes
VOLUME ["/agent/config", "/agent/data"]

# Ports
EXPOSE 50051 6901

# Health check
HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
    CMD curl -f http://localhost:${NOVNC_PORT} || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
```

### Entrypoint Script

```bash
#!/bin/bash
# infra/docker/doom-player/entrypoint.sh
set -e

echo "[doom-player] Starting agent: ${AGENT_ID} (gen ${GENERATION})"

# Start virtual framebuffer
Xvfb :99 -screen 0 640x480x24 -ac +extension GLX +render -noreset &
sleep 1

# Start VNC server
x11vnc -display :99 -nopw -listen 0.0.0.0 -xkb -ncache 10 -forever -shared &
sleep 1

# Start noVNC WebSocket proxy
/usr/share/novnc/utils/novnc_proxy \
    --vnc localhost:5900 \
    --listen ${NOVNC_PORT} &
sleep 1

echo "[doom-player] Display stack ready (noVNC on port ${NOVNC_PORT})"

# Start Rust agent (manages game loop via Python glue)
exec /app/agent-core \
    --config /agent/config/agent.md \
    --data-dir /agent/data \
    --opensearch-url ${OPENSEARCH_URL} \
    --nats-url ${NATS_URL} \
    --grpc-port 50051
```

## Multi-Stage Builds

### Rust Agent (agent-core)

```dockerfile
# Stage 1: Build
FROM rust:1.77-bookworm AS builder
WORKDIR /build
COPY Cargo.toml Cargo.lock ./
COPY src/ ./src/
COPY proto/ ./proto/
RUN cargo build --release

# Stage 2: Runtime (minimal)
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates libssl3 && rm -rf /var/lib/apt/lists/*
COPY --from=builder /build/target/release/agent-core /usr/local/bin/
ENTRYPOINT ["agent-core"]
```

### Go Orchestrator

```dockerfile
# Stage 1: Build
FROM golang:1.22-bookworm AS builder
WORKDIR /build
COPY go.mod go.sum ./
RUN go mod download
COPY cmd/ ./cmd/
COPY internal/ ./internal/
COPY pkg/ ./pkg/
COPY proto/ ./proto/
RUN CGO_ENABLED=0 GOOS=linux go build -o orchestrator ./cmd/orchestrator

# Stage 2: Runtime
FROM gcr.io/distroless/static-debian12
COPY --from=builder /build/orchestrator /
ENTRYPOINT ["/orchestrator"]
```

### Dashboard (Next.js)

```dockerfile
# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Build
FROM node:18-alpine AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build

# Stage 3: Runtime
FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public
EXPOSE 3000
CMD ["node", "server.js"]
```

## Docker Compose

### Full Stack Definition

```yaml
# infra/docker-compose.yml
version: "3.8"

services:
  # ---- Game Players ----
  player-001:
    build:
      context: ../
      dockerfile: infra/docker/doom-player/Dockerfile
    container_name: player-001
    environment:
      - AGENT_ID=PLAYER_001
      - GENERATION=1
      - OPENSEARCH_URL=http://opensearch:9200
      - NATS_URL=nats://nats:4222
      - NOVNC_PORT=6901
    volumes:
      - ../volumes/agents/active/DOOM_PLAYER_001.MD:/agent/config/agent.md:ro
      - ../volumes/data/player-001:/agent/data
    ports:
      - "6901:6901"   # noVNC
      - "50051:50051"  # gRPC
    depends_on:
      opensearch:
        condition: service_healthy
      nats:
        condition: service_started
    networks:
      - clau-doom

  player-002:
    build:
      context: ../
      dockerfile: infra/docker/doom-player/Dockerfile
    container_name: player-002
    environment:
      - AGENT_ID=PLAYER_002
      - GENERATION=1
      - NOVNC_PORT=6902
    volumes:
      - ../volumes/agents/active/DOOM_PLAYER_002.MD:/agent/config/agent.md:ro
      - ../volumes/data/player-002:/agent/data
    ports:
      - "6902:6901"
      - "50052:50051"
    depends_on:
      opensearch:
        condition: service_healthy
    networks:
      - clau-doom

  # ---- Orchestrator ----
  orchestrator:
    build:
      context: ../
      dockerfile: infra/docker/orchestrator/Dockerfile
    container_name: orchestrator
    ports:
      - "8080:8080"   # REST/WebSocket API
      - "50050:50050"  # gRPC
    volumes:
      - ../volumes:/data/volumes
    environment:
      - OPENSEARCH_URL=http://opensearch:9200
      - MONGO_URL=mongodb://mongo:27017
      - NATS_URL=nats://nats:4222
    depends_on:
      opensearch:
        condition: service_healthy
      mongo:
        condition: service_healthy
    networks:
      - clau-doom

  # ---- OpenSearch ----
  opensearch:
    image: opensearchproject/opensearch:2.12.0
    container_name: opensearch
    environment:
      - discovery.type=single-node
      - plugins.security.disabled=true
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
    volumes:
      - opensearch-data:/usr/share/opensearch/data
    ports:
      - "9200:9200"
    healthcheck:
      test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health | grep -q '\"status\":\"green\"\\|\"status\":\"yellow\"'"]
      interval: 10s
      timeout: 5s
      retries: 10
    networks:
      - clau-doom

  # ---- MongoDB ----
  mongo:
    image: mongo:7.0
    container_name: mongo
    volumes:
      - mongo-data:/data/db
    ports:
      - "27017:27017"
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 10s
      timeout: 5s
      retries: 5
    networks:
      - clau-doom

  # ---- NATS ----
  nats:
    image: nats:2.10
    container_name: nats
    ports:
      - "4222:4222"   # Client
      - "8222:8222"   # Monitoring
    networks:
      - clau-doom

  # ---- Ollama ----
  ollama:
    image: ollama/ollama:latest
    container_name: ollama
    volumes:
      - ollama-data:/root/.ollama
    ports:
      - "11434:11434"
    networks:
      - clau-doom

  # ---- Dashboard ----
  dashboard:
    build:
      context: ../dashboard
      dockerfile: ../infra/docker/dashboard/Dockerfile
    container_name: dashboard
    ports:
      - "3000:3000"
    environment:
      - ORCHESTRATOR_URL=http://orchestrator:8080
      - OPENSEARCH_URL=http://opensearch:9200
    depends_on:
      - orchestrator
    networks:
      - clau-doom

volumes:
  opensearch-data:
  mongo-data:
  ollama-data:

networks:
  clau-doom:
    driver: bridge
```

## Volume Mounts

```yaml
# Agent configuration (read-only)
volumes/agents/active/DOOM_PLAYER_*.MD -> /agent/config/agent.md:ro

# Agent play data (read-write, persistent)
volumes/data/player-{SEQ}/ -> /agent/data/
  Contains: game.duckdb, local cache files

# Research documents (shared with host for Claude Code access)
volumes/research/ -> /data/volumes/research/
  Contains: RESEARCH_LOG.MD, orders/, reports/

# OpenSearch data (named volume, persistent)
opensearch-data -> /usr/share/opensearch/data

# MongoDB data (named volume, persistent)
mongo-data -> /data/db
```

## Health Checks

```yaml
# OpenSearch: Check cluster health
healthcheck:
  test: ["CMD-SHELL", "curl -s http://localhost:9200/_cluster/health"]
  interval: 10s
  timeout: 5s
  retries: 10

# MongoDB: Ping admin
healthcheck:
  test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
  interval: 10s
  timeout: 5s
  retries: 5

# Player: Check noVNC is responding
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:${NOVNC_PORT}"]
  interval: 10s
  timeout: 5s
  retries: 3

# Orchestrator: HTTP health endpoint
healthcheck:
  test: ["CMD-SHELL", "curl -f http://localhost:8080/health"]
  interval: 10s
  timeout: 5s
  retries: 5
```

## GPU Passthrough (nvidia-docker)

For GPU-accelerated rendering (optional, Linux only).

```yaml
# docker-compose.gpu.yml (override)
services:
  player-001:
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
    environment:
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=graphics,utility
```

### Prerequisites

```bash
# Install NVIDIA Container Toolkit
distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
    sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
    sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
    sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

### Usage

```bash
# Start with GPU support
docker compose -f docker-compose.yml -f docker-compose.gpu.yml up

# Without GPU (CPU-only rendering, default)
docker compose up
```

## Common Operations

```bash
# Start full stack
docker compose -f infra/docker-compose.yml up -d

# Start only infrastructure (no players)
docker compose -f infra/docker-compose.yml up -d opensearch mongo nats ollama

# Spawn additional player
docker compose -f infra/docker-compose.yml run -d \
    -e AGENT_ID=PLAYER_005 \
    -e GENERATION=3 \
    -p 6905:6901 \
    player-001

# View player logs
docker logs -f player-001

# Restart a player with new MD config
docker restart player-001

# Scale players (requires dynamic port assignment)
docker compose -f infra/docker-compose.yml up -d --scale player=8

# Stop everything
docker compose -f infra/docker-compose.yml down

# Stop and remove volumes (DESTRUCTIVE)
docker compose -f infra/docker-compose.yml down -v
```
