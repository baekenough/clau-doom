---
name: docker-best-practices
description: Docker patterns for VizDoom containers with Xvfb and noVNC, multi-service compose, GPU support, and development workflows
user-invocable: false
---

# Docker Best Practices for clau-doom Infrastructure

## VizDoom Container

### Base Image with Xvfb and noVNC

```dockerfile
# docker/vizdoom/Dockerfile
FROM ubuntu:22.04 AS vizdoom-base

ENV DEBIAN_FRONTEND=noninteractive

# System dependencies for VizDoom + display
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv \
    xvfb \
    x11vnc \
    novnc websockify \
    libboost-all-dev \
    libsdl2-dev \
    cmake g++ git \
    && rm -rf /var/lib/apt/lists/*

# VizDoom
RUN pip3 install --no-cache-dir vizdoom==1.2.0

# noVNC setup
ENV DISPLAY=:99
ENV VNC_PORT=5900
ENV NOVNC_PORT=6080

# Entrypoint script
COPY docker/vizdoom/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5900 6080

ENTRYPOINT ["/entrypoint.sh"]
```

### Entrypoint Script

```bash
#!/bin/bash
# docker/vizdoom/entrypoint.sh

# Start Xvfb (virtual framebuffer)
Xvfb :99 -screen 0 640x480x24 -ac +extension GLX +render -noreset &
sleep 1

# Start VNC server
x11vnc -display :99 -nopw -forever -shared -rfbport ${VNC_PORT} &
sleep 1

# Start noVNC WebSocket proxy
/usr/share/novnc/utils/novnc_proxy \
    --vnc localhost:${VNC_PORT} \
    --listen ${NOVNC_PORT} &

# Run the actual command
exec "$@"
```

### Agent Container (Rust)

```dockerfile
# docker/agent/Dockerfile
FROM rust:1.83-bookworm AS builder

WORKDIR /build
COPY agent-core/ .
RUN cargo build --release --workspace

FROM debian:bookworm-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /build/target/release/agent-core /usr/local/bin/agent-core
COPY --from=builder /build/target/release/scoring /usr/local/bin/scoring

ENV RUST_LOG=info
ENTRYPOINT ["agent-core"]
```

## Multi-Stage Builds

### Go Orchestrator

```dockerfile
# docker/orchestrator/Dockerfile
FROM golang:1.23-bookworm AS builder

WORKDIR /build
COPY orchestrator/go.mod orchestrator/go.sum ./
RUN go mod download

COPY orchestrator/ .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /clau-doom ./cmd/clau-doom

FROM gcr.io/distroless/static-debian12

COPY --from=builder /clau-doom /clau-doom
ENTRYPOINT ["/clau-doom"]
```

### Dashboard (Next.js)

```dockerfile
# docker/dashboard/Dockerfile
FROM node:22-slim AS deps
WORKDIR /app
COPY dashboard/package.json dashboard/pnpm-lock.yaml ./
RUN corepack enable && pnpm install --frozen-lockfile

FROM node:22-slim AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY dashboard/ .
RUN corepack enable && pnpm build

FROM node:22-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static

EXPOSE 3000
CMD ["node", "server.js"]
```

## Docker Compose

### Service Definitions

```yaml
# docker-compose.yml
services:
  orchestrator:
    build:
      context: .
      dockerfile: docker/orchestrator/Dockerfile
    ports:
      - "50051:50051"   # gRPC
      - "9090:9090"     # metrics
    environment:
      - NATS_URL=nats://nats:4222
      - DOCKER_HOST=unix:///var/run/docker.sock
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./config:/config:ro
    depends_on:
      nats:
        condition: service_healthy
      duckdb-init:
        condition: service_completed_successfully
    healthcheck:
      test: ["CMD", "grpc_health_probe", "-addr=:50051"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - clau-doom-net

  vizdoom:
    build:
      context: .
      dockerfile: docker/vizdoom/Dockerfile
    command: python3 /app/game_server.py
    ports:
      - "6080:6080"     # noVNC
    volumes:
      - ./scenarios:/scenarios:ro
      - ./analytics:/app:ro
    environment:
      - GRPC_ENDPOINT=orchestrator:50051
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:6080"]
      interval: 15s
      timeout: 5s
      retries: 3
    networks:
      - clau-doom-net

  dashboard:
    build:
      context: .
      dockerfile: docker/dashboard/Dockerfile
    ports:
      - "3000:3000"
    environment:
      - GRPC_ENDPOINT=orchestrator:50051
      - NEXT_PUBLIC_WS_URL=ws://localhost:3000
      - NEXT_PUBLIC_VNC_URL=ws://localhost:6080
    depends_on:
      orchestrator:
        condition: service_healthy
    networks:
      - clau-doom-net

  nats:
    image: nats:2.10-alpine
    ports:
      - "4222:4222"     # client
      - "8222:8222"     # monitoring
    command: ["--jetstream", "--store_dir=/data"]
    volumes:
      - nats-data:/data
    healthcheck:
      test: ["CMD", "nats-server", "--signal", "ldm"]
      interval: 10s
      timeout: 5s
      retries: 3
    networks:
      - clau-doom-net

  duckdb-init:
    image: python:3.12-slim
    command: python3 /scripts/init_db.py
    volumes:
      - ./scripts:/scripts:ro
      - duckdb-data:/data
    networks:
      - clau-doom-net

networks:
  clau-doom-net:
    driver: bridge

volumes:
  nats-data:
  duckdb-data:
```

### Development Override

```yaml
# docker-compose.dev.yml
services:
  orchestrator:
    build:
      target: builder  # Use builder stage for dev tools
    volumes:
      - ./orchestrator:/build:cached
    command: ["go", "run", "./cmd/clau-doom"]

  dashboard:
    build:
      target: deps
    volumes:
      - ./dashboard:/app:cached
      - /app/node_modules
    command: ["pnpm", "dev"]
    environment:
      - NEXT_TELEMETRY_DISABLED=1

  vizdoom:
    volumes:
      - ./analytics:/app:cached
      - ./scenarios:/scenarios:cached
```

## GPU Support

### NVIDIA Docker Configuration

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
      - NVIDIA_VISIBLE_DEVICES=all
      - NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics
```

### GPU-Enabled VizDoom Dockerfile

```dockerfile
# docker/vizdoom/Dockerfile.gpu
FROM nvidia/cuda:12.4.0-runtime-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV NVIDIA_VISIBLE_DEVICES=all
ENV NVIDIA_DRIVER_CAPABILITIES=compute,utility,graphics

RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip \
    xvfb x11vnc novnc websockify \
    libgl1-mesa-glx libglu1-mesa \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install --no-cache-dir vizdoom==1.2.0

# Same entrypoint as base image
COPY docker/vizdoom/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

## Development Workflow

### Hot Reload Setup

```bash
# Start development environment
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Rebuild single service
docker compose build orchestrator

# View logs for specific service
docker compose logs -f vizdoom

# Shell into running container
docker compose exec orchestrator bash
```

### Volume Mounts for Development

```yaml
# Key principle: mount source code, not build artifacts
volumes:
  # Source code: cached for performance
  - ./orchestrator:/build:cached
  # Exclude build artifacts from mount
  - /build/target
  # Read-only for configs
  - ./config:/config:ro
```

## Health Checks

### gRPC Health Check

```yaml
healthcheck:
  test: ["CMD", "grpc_health_probe", "-addr=:50051"]
  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 15s
```

### HTTP Health Check

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
  interval: 10s
  timeout: 5s
  retries: 3
```

### Custom Health Script

```bash
#!/bin/bash
# docker/vizdoom/healthcheck.sh

# Check Xvfb is running
pgrep Xvfb > /dev/null || exit 1

# Check VNC server
pgrep x11vnc > /dev/null || exit 1

# Check noVNC proxy
curl -sf http://localhost:6080 > /dev/null || exit 1

exit 0
```

## Resource Limits and Monitoring

### Per-Service Limits

```yaml
services:
  vizdoom:
    deploy:
      resources:
        limits:
          cpus: "2.0"
          memory: 2G
        reservations:
          cpus: "1.0"
          memory: 1G

  orchestrator:
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 1G

  agent:  # spawned dynamically
    deploy:
      resources:
        limits:
          cpus: "0.5"
          memory: 512M
```

### Container Labels for Monitoring

```yaml
labels:
  - "clau-doom.service=orchestrator"
  - "clau-doom.version=${VERSION}"
  - "prometheus.io/scrape=true"
  - "prometheus.io/port=9090"
```

## Best Practices Summary

1. Always use multi-stage builds to minimize image size
2. Pin base image versions for reproducibility
3. Use health checks on all services with proper `start_period`
4. Mount Docker socket read-only when orchestrator needs container management
5. Use named volumes for persistent data (DuckDB, NATS JetStream)
6. Define resource limits for all services to prevent runaway containers
7. Use `.dockerignore` to exclude build artifacts, `.git`, and `node_modules`
8. Tag images with git SHA for traceability
9. Use `depends_on` with `condition` for proper startup ordering
10. Keep development and production configurations separate with compose overrides
