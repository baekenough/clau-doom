# Stage 1: Build the Rust agent-server binary
FROM rust:1.77-bookworm AS builder

RUN apt-get update && apt-get install -y protobuf-compiler && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy dependency manifests first for layer caching
COPY agent-core/Cargo.toml agent-core/Cargo.lock ./agent-core/
COPY agent-core/build.rs ./agent-core/

# Copy proto files (needed by build.rs at compile time)
COPY proto/ ./proto/

# Create dummy sources to pre-build dependencies
RUN mkdir -p agent-core/src agent-core/benches \
    && echo "fn main() {}" > agent-core/src/main.rs \
    && echo "pub fn lib() {}" > agent-core/src/lib.rs \
    && echo "fn main() {}" > agent-core/benches/decision_cascade.rs

WORKDIR /build/agent-core
RUN cargo build --release --bin agent-server 2>/dev/null || true

# Remove dummy sources and build artifacts for the crate itself
RUN rm -rf src/ benches/ \
    && rm -f target/release/deps/agent_core* \
    && rm -f target/release/agent-server*

WORKDIR /build

# Copy real source code
COPY agent-core/src/ ./agent-core/src/

WORKDIR /build/agent-core
RUN cargo build --release --bin agent-server

# Stage 2: Minimal runtime image
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /build/agent-core/target/release/agent-server ./agent-server

# Runtime defaults (overridable via docker-compose environment)
ENV OPENSEARCH_URL=http://opensearch:9200 \
    GRPC_PORT=50051 \
    CASCADE_MODE=full_agent \
    SEED=42 \
    HEALTH_THRESHOLD=0.3 \
    DUCKDB_PATH=/app/data/agent_cache.duckdb

RUN mkdir -p /app/data

EXPOSE 50051

HEALTHCHECK --interval=10s --timeout=3s --start-period=10s --retries=3 \
    CMD nc -z localhost 50051 || exit 1

CMD ["./agent-server"]
