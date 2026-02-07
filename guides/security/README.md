# Security Reference Guide

Reference documentation for security in the clau-doom multi-service research platform.

## Key Resources

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Docker Security Best Practices](https://docs.docker.com/engine/security/)
- [CIS Docker Benchmark](https://www.cisecurity.org/benchmark/docker)
- [gRPC Authentication Guide](https://grpc.io/docs/guides/auth/)
- [Let's Encrypt Documentation](https://letsencrypt.org/docs/)
- [JWT.io](https://jwt.io/)
- [NATS Security](https://docs.nats.io/running-a-nats-service/configuration/securing_nats)
- [MongoDB Security Checklist](https://www.mongodb.com/docs/manual/administration/security-checklist/)
- [OpenSearch Security](https://opensearch.org/docs/latest/security/)

## clau-doom Context

The clau-doom research platform consists of multiple services communicating via gRPC and NATS:
- **Orchestrator** (Go): Manages agent lifecycle, exposes gRPC API
- **Agents** (Rust): Decision engines, communicate via gRPC to orchestrator
- **Dashboard** (Next.js): Web UI, consumes orchestrator API, serves noVNC streams
- **VizDoom** (Python glue): Game environment, embedded in agent containers
- **OpenSearch**: RAG vector search backend
- **MongoDB**: Knowledge catalog
- **NATS**: Pub/sub message bus for agent coordination

Security concerns:
1. Inter-service communication (gRPC, NATS) should use mTLS
2. Dashboard API requires authentication (JWT)
3. Containers should run with minimal privileges
4. Secrets (DB passwords, JWT keys) must not be in version control
5. Container images should be scanned for vulnerabilities
6. Research data should be protected from unauthorized access

## mTLS Between Services

### Certificate Generation

#### Self-Signed Certificates (Development)

```bash
#!/bin/bash
# scripts/security/generate-dev-certs.sh

set -e

CERT_DIR="./secrets/certs"
mkdir -p "$CERT_DIR"

# Generate CA key and certificate
openssl req -x509 -newkey rsa:4096 -days 365 -nodes \
    -keyout "$CERT_DIR/ca-key.pem" \
    -out "$CERT_DIR/ca-cert.pem" \
    -subj "/C=US/ST=State/L=City/O=clau-doom-dev/OU=Research/CN=clau-doom-ca"

echo "CA certificate generated"

# Function to generate service certificate
generate_service_cert() {
    local service=$1
    local san=$2

    # Generate private key
    openssl genrsa -out "$CERT_DIR/${service}-key.pem" 4096

    # Generate CSR
    openssl req -new -key "$CERT_DIR/${service}-key.pem" \
        -out "$CERT_DIR/${service}.csr" \
        -subj "/C=US/ST=State/L=City/O=clau-doom-dev/OU=${service}/CN=${service}"

    # Create SAN config
    cat > "$CERT_DIR/${service}-ext.cnf" <<EOF
subjectAltName = ${san}
EOF

    # Sign with CA
    openssl x509 -req -in "$CERT_DIR/${service}.csr" \
        -CA "$CERT_DIR/ca-cert.pem" -CAkey "$CERT_DIR/ca-key.pem" \
        -CAcreateserial -out "$CERT_DIR/${service}-cert.pem" \
        -days 365 -extfile "$CERT_DIR/${service}-ext.cnf"

    echo "Certificate generated for $service"
}

# Generate certificates for each service
generate_service_cert "orchestrator" "DNS:orchestrator,DNS:localhost,IP:127.0.0.1"
generate_service_cert "opensearch" "DNS:opensearch,DNS:localhost"
generate_service_cert "mongo" "DNS:mongo,DNS:localhost"
generate_service_cert "nats" "DNS:nats,DNS:localhost"

# Generate client certificates for agents
for i in {1..8}; do
    generate_service_cert "player-$(printf '%03d' $i)" "DNS:player-$(printf '%03d' $i),DNS:localhost"
done

echo "All certificates generated in $CERT_DIR"
```

#### CA-Signed Certificates (Production)

```bash
#!/bin/bash
# scripts/security/generate-prod-certs.sh

set -e

# Use Let's Encrypt for public-facing services (Dashboard)
certbot certonly --standalone -d dashboard.clau-doom.example.com

# For internal services, use organizational CA
CERT_DIR="./secrets/certs/prod"
CA_CERT="/path/to/org/ca-cert.pem"
CA_KEY="/path/to/org/ca-key.pem"

mkdir -p "$CERT_DIR"

generate_service_cert() {
    local service=$1
    local san=$2

    openssl genrsa -out "$CERT_DIR/${service}-key.pem" 4096
    openssl req -new -key "$CERT_DIR/${service}-key.pem" \
        -out "$CERT_DIR/${service}.csr" \
        -subj "/C=US/ST=State/L=City/O=clau-doom/OU=${service}/CN=${service}.internal.clau-doom.example.com"

    cat > "$CERT_DIR/${service}-ext.cnf" <<EOF
subjectAltName = ${san}
extendedKeyUsage = serverAuth,clientAuth
EOF

    openssl x509 -req -in "$CERT_DIR/${service}.csr" \
        -CA "$CA_CERT" -CAkey "$CA_KEY" \
        -CAcreateserial -out "$CERT_DIR/${service}-cert.pem" \
        -days 365 -extfile "$CERT_DIR/${service}-ext.cnf"
}

generate_service_cert "orchestrator" "DNS:orchestrator.internal.clau-doom.example.com"
generate_service_cert "opensearch" "DNS:opensearch.internal.clau-doom.example.com"
# ... etc
```

### TLS Configuration for gRPC (Rust tonic)

```rust
// agent-core/src/grpc/client.rs

use tonic::transport::{Certificate, Channel, ClientTlsConfig, Identity};
use std::fs;

pub async fn create_secure_channel(endpoint: &str) -> Result<Channel, Box<dyn std::error::Error>> {
    // Load CA certificate
    let ca_cert = fs::read_to_string("/secrets/certs/ca-cert.pem")?;
    let ca = Certificate::from_pem(ca_cert);

    // Load client certificate and key
    let client_cert = fs::read_to_string("/secrets/certs/player-001-cert.pem")?;
    let client_key = fs::read_to_string("/secrets/certs/player-001-key.pem")?;
    let client_identity = Identity::from_pem(client_cert, client_key);

    let tls_config = ClientTlsConfig::new()
        .ca_certificate(ca)
        .identity(client_identity)
        .domain_name("orchestrator");

    let channel = Channel::from_shared(endpoint.to_string())?
        .tls_config(tls_config)?
        .connect()
        .await?;

    Ok(channel)
}
```

### TLS Configuration for gRPC (Go grpc-go)

```go
// orchestrator/internal/grpc/server.go

package grpc

import (
    "crypto/tls"
    "crypto/x509"
    "fmt"
    "os"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials"
)

func NewSecureServer() (*grpc.Server, error) {
    // Load server certificate and key
    cert, err := tls.LoadX509KeyPair(
        "/secrets/certs/orchestrator-cert.pem",
        "/secrets/certs/orchestrator-key.pem",
    )
    if err != nil {
        return nil, fmt.Errorf("load server cert: %w", err)
    }

    // Load CA certificate for client verification
    caCert, err := os.ReadFile("/secrets/certs/ca-cert.pem")
    if err != nil {
        return nil, fmt.Errorf("read CA cert: %w", err)
    }

    certPool := x509.NewCertPool()
    if !certPool.AppendCertsFromPEM(caCert) {
        return nil, fmt.Errorf("append CA cert")
    }

    tlsConfig := &tls.Config{
        Certificates: []tls.Certificate{cert},
        ClientAuth:   tls.RequireAndVerifyClientCert,
        ClientCAs:    certPool,
        MinVersion:   tls.VersionTLS13,
    }

    creds := credentials.NewTLS(tlsConfig)
    server := grpc.NewServer(grpc.Creds(creds))

    return server, nil
}
```

### TLS Configuration for NATS

```bash
# secrets/nats-server.conf

port: 4222

tls {
  cert_file: "/secrets/certs/nats-cert.pem"
  key_file: "/secrets/certs/nats-key.pem"
  ca_file: "/secrets/certs/ca-cert.pem"
  verify: true
  timeout: 2
}

authorization {
  token: "$NATS_AUTH_TOKEN"
}
```

```yaml
# docker-compose.yml (NATS with TLS)
services:
  nats:
    image: nats:2.10
    volumes:
      - ./secrets/certs:/secrets/certs:ro
      - ./secrets/nats-server.conf:/etc/nats/nats-server.conf:ro
    secrets:
      - nats-auth-token
    environment:
      - NATS_AUTH_TOKEN_FILE=/run/secrets/nats-auth-token
    command: ["-c", "/etc/nats/nats-server.conf"]
```

### TLS Configuration for MongoDB

```yaml
# docker-compose.yml (MongoDB with TLS)
services:
  mongo:
    image: mongo:7.0
    command:
      - "--tlsMode"
      - "requireTLS"
      - "--tlsCertificateKeyFile"
      - "/secrets/certs/mongo.pem"
      - "--tlsCAFile"
      - "/secrets/certs/ca-cert.pem"
    volumes:
      - ./secrets/certs:/secrets/certs:ro
      - mongo-data:/data/db
    secrets:
      - mongo-root-password
    environment:
      - MONGO_INITDB_ROOT_USERNAME=admin
      - MONGO_INITDB_ROOT_PASSWORD_FILE=/run/secrets/mongo-root-password
```

### TLS Configuration for OpenSearch

```yaml
# docker-compose.yml (OpenSearch with TLS)
services:
  opensearch:
    image: opensearchproject/opensearch:2.12.0
    environment:
      - plugins.security.ssl.transport.pemcert_filepath=/secrets/certs/opensearch-cert.pem
      - plugins.security.ssl.transport.pemkey_filepath=/secrets/certs/opensearch-key.pem
      - plugins.security.ssl.transport.pemtrustedcas_filepath=/secrets/certs/ca-cert.pem
      - plugins.security.ssl.http.enabled=true
      - plugins.security.ssl.http.pemcert_filepath=/secrets/certs/opensearch-cert.pem
      - plugins.security.ssl.http.pemkey_filepath=/secrets/certs/opensearch-key.pem
      - plugins.security.ssl.http.pemtrustedcas_filepath=/secrets/certs/ca-cert.pem
    volumes:
      - ./secrets/certs:/secrets/certs:ro
      - opensearch-data:/usr/share/opensearch/data
    secrets:
      - opensearch-admin-password
```

### Certificate Rotation

```bash
#!/bin/bash
# scripts/security/rotate-certs.sh

set -e

CERT_DIR="./secrets/certs"
BACKUP_DIR="./secrets/certs.backup.$(date +%Y%m%d)"

# Backup existing certificates
cp -r "$CERT_DIR" "$BACKUP_DIR"

# Generate new certificates
./scripts/security/generate-dev-certs.sh

# Rolling restart services (zero downtime)
for service in orchestrator player-001 player-002 opensearch mongo nats; do
    echo "Rotating certificates for $service..."
    docker compose restart $service
    sleep 5
done

echo "Certificate rotation complete. Backups in $BACKUP_DIR"
```

### Docker Secrets for Certificate Storage

```yaml
# docker-compose.yml
secrets:
  ca-cert:
    file: ./secrets/certs/ca-cert.pem
  orchestrator-cert:
    file: ./secrets/certs/orchestrator-cert.pem
  orchestrator-key:
    file: ./secrets/certs/orchestrator-key.pem
  player-001-cert:
    file: ./secrets/certs/player-001-cert.pem
  player-001-key:
    file: ./secrets/certs/player-001-key.pem

services:
  orchestrator:
    secrets:
      - ca-cert
      - orchestrator-cert
      - orchestrator-key

  player-001:
    secrets:
      - ca-cert
      - player-001-cert
      - player-001-key
```

## API Authentication

### JWT for Dashboard API

#### Token Generation and Validation

```go
// orchestrator/internal/auth/jwt.go

package auth

import (
    "fmt"
    "os"
    "time"

    "github.com/golang-jwt/jwt/v5"
)

type Claims struct {
    UserID       string   `json:"user_id"`
    Roles        []string `json:"roles"`
    ExperimentAccess []string `json:"experiment_access"`
    jwt.RegisteredClaims
}

func GenerateToken(userID string, roles []string, experiments []string) (string, error) {
    signingKey := []byte(os.Getenv("JWT_SIGNING_KEY"))

    claims := &Claims{
        UserID:       userID,
        Roles:        roles,
        ExperimentAccess: experiments,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            Issuer:    "clau-doom-orchestrator",
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(signingKey)
}

func ValidateToken(tokenString string) (*Claims, error) {
    signingKey := []byte(os.Getenv("JWT_SIGNING_KEY"))

    token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return signingKey, nil
    })

    if err != nil {
        return nil, err
    }

    if claims, ok := token.Claims.(*Claims); ok && token.Valid {
        return claims, nil
    }

    return nil, fmt.Errorf("invalid token")
}
```

#### gRPC Middleware (Go)

```go
// orchestrator/internal/grpc/middleware/auth.go

package middleware

import (
    "context"
    "strings"

    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/metadata"
    "google.golang.org/grpc/status"

    "clau-doom/internal/auth"
)

func AuthInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    // Extract metadata
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "missing metadata")
    }

    // Get authorization header
    authHeaders := md.Get("authorization")
    if len(authHeaders) == 0 {
        return nil, status.Error(codes.Unauthenticated, "missing authorization header")
    }

    // Extract token
    authHeader := authHeaders[0]
    if !strings.HasPrefix(authHeader, "Bearer ") {
        return nil, status.Error(codes.Unauthenticated, "invalid authorization header format")
    }

    token := strings.TrimPrefix(authHeader, "Bearer ")

    // Validate token
    claims, err := auth.ValidateToken(token)
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, "invalid token")
    }

    // Add claims to context
    ctx = context.WithValue(ctx, "claims", claims)

    return handler(ctx, req)
}
```

#### Next.js API Route Protection

```typescript
// dashboard/src/middleware.ts

import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';
import * as jose from 'jose';

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value;

  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  try {
    const secret = new TextEncoder().encode(process.env.JWT_SIGNING_KEY);
    const { payload } = await jose.jwtVerify(token, secret);

    // Check experiment access for /api/experiments/* routes
    if (request.nextUrl.pathname.startsWith('/api/experiments/')) {
      const experimentId = request.nextUrl.pathname.split('/')[3];
      const experimentAccess = payload.experiment_access as string[];

      if (!experimentAccess.includes(experimentId) && !payload.roles?.includes('admin')) {
        return NextResponse.json({ error: 'Forbidden' }, { status: 403 });
      }
    }

    return NextResponse.next();
  } catch (error) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: ['/api/:path*', '/dashboard/:path*'],
};
```

### API Key for Service-to-Service (Internal)

#### Key Generation and Storage

```bash
#!/bin/bash
# scripts/security/generate-api-key.sh

SERVICE_NAME=$1

if [ -z "$SERVICE_NAME" ]; then
    echo "Usage: $0 <service-name>"
    exit 1
fi

API_KEY=$(openssl rand -hex 32)

echo "$API_KEY" > "./secrets/api-keys/${SERVICE_NAME}.key"
chmod 600 "./secrets/api-keys/${SERVICE_NAME}.key"

echo "API key generated for $SERVICE_NAME"
echo "Key: $API_KEY"
```

#### Key Validation Middleware

```go
// orchestrator/internal/grpc/middleware/apikey.go

package middleware

import (
    "context"
    "os"
    "strings"

    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/metadata"
    "google.golang.org/grpc/status"
)

func APIKeyInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "missing metadata")
    }

    apiKeys := md.Get("x-api-key")
    if len(apiKeys) == 0 {
        return nil, status.Error(codes.Unauthenticated, "missing api key")
    }

    providedKey := apiKeys[0]
    expectedKey := os.Getenv("INTERNAL_API_KEY")

    if !strings.EqualFold(providedKey, expectedKey) {
        return nil, status.Error(codes.Unauthenticated, "invalid api key")
    }

    return handler(ctx, req)
}
```

#### Key Rotation

```bash
#!/bin/bash
# scripts/security/rotate-api-keys.sh

set -e

# Generate new keys
for service in orchestrator agent-001 agent-002; do
    ./scripts/security/generate-api-key.sh "$service"
done

# Update environment variables in docker-compose
docker compose restart orchestrator player-001 player-002

echo "API key rotation complete"
```

## Container Hardening

### Non-Root User in Dockerfiles

```dockerfile
# docker/orchestrator/Dockerfile
FROM golang:1.22-bookworm AS builder
WORKDIR /build
COPY . .
RUN CGO_ENABLED=0 go build -o orchestrator ./cmd/orchestrator

FROM gcr.io/distroless/static-debian12

# distroless images use non-root user by default (uid 65532)
COPY --from=builder /build/orchestrator /orchestrator

USER 65532:65532

ENTRYPOINT ["/orchestrator"]
```

```dockerfile
# docker/vizdoom/Dockerfile
FROM ubuntu:22.04

# Create non-root user
RUN groupadd -r doomuser && useradd -r -g doomuser -u 1001 doomuser

# Install dependencies
RUN apt-get update && apt-get install -y \
    python3 xvfb x11vnc novnc \
    && rm -rf /var/lib/apt/lists/*

# Copy application
COPY --chown=doomuser:doomuser ./app /app

# Switch to non-root user
USER doomuser

ENTRYPOINT ["/app/entrypoint.sh"]
```

### Read-Only Filesystem

```yaml
# docker-compose.yml
services:
  orchestrator:
    read_only: true
    tmpfs:
      - /tmp:size=100M,mode=1777
    volumes:
      - orchestrator-data:/data  # writable volume for persistent data
```

### Drop Capabilities

```yaml
# docker-compose.yml
services:
  orchestrator:
    cap_drop:
      - ALL
    cap_add:
      - NET_BIND_SERVICE  # only if binding to ports < 1024
    security_opt:
      - no-new-privileges:true
```

### Minimal Base Images

```dockerfile
# Use distroless for Go
FROM gcr.io/distroless/static-debian12

# Use alpine for Rust (if musl-libc compatible)
FROM alpine:3.19
RUN apk add --no-cache ca-certificates

# Multi-stage to exclude build tools
FROM rust:1.83-bookworm AS builder
RUN cargo build --release

FROM debian:bookworm-slim
COPY --from=builder /build/target/release/agent-core /usr/local/bin/
```

### Image Scanning

```yaml
# .github/workflows/security-scan.yml
name: Security Scan

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  trivy-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build images
        run: docker compose build

      - name: Run Trivy vulnerability scanner
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: 'clau-doom-orchestrator:latest'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Upload Trivy results to GitHub Security
        uses: github/codeql-action/upload-sarif@v3
        with:
          sarif_file: 'trivy-results.sarif'
```

```bash
# scripts/security/scan-images.sh
#!/bin/bash

set -e

echo "Scanning Docker images with Trivy..."

for image in orchestrator dashboard vizdoom; do
    echo "Scanning clau-doom-${image}..."
    trivy image --severity HIGH,CRITICAL "clau-doom-${image}:latest"
done

echo "Scanning with Grype..."
grype dir:. --scope all-layers
```

## Secrets Management

### Docker Secrets

```yaml
# docker-compose.yml
secrets:
  mongo-root-password:
    file: ./secrets/mongo-root-password.txt
  opensearch-admin-password:
    file: ./secrets/opensearch-admin-password.txt
  jwt-signing-key:
    file: ./secrets/jwt-signing-key.txt
  nats-auth-token:
    file: ./secrets/nats-auth-token.txt

services:
  mongo:
    secrets:
      - mongo-root-password
    environment:
      - MONGO_INITDB_ROOT_PASSWORD_FILE=/run/secrets/mongo-root-password

  orchestrator:
    secrets:
      - jwt-signing-key
      - nats-auth-token
```

### Environment Variable Handling

```bash
# .env.example (checked into git)
ORCHESTRATOR_PORT=50050
DASHBOARD_PORT=3000
# Secrets should be in .env (gitignored)
# JWT_SIGNING_KEY=<generate-with-openssl-rand-hex-32>
# MONGO_ROOT_PASSWORD=<strong-password>
# OPENSEARCH_ADMIN_PASSWORD=<strong-password>
# NATS_AUTH_TOKEN=<generate-with-openssl-rand-hex-32>
```

```bash
# .gitignore
.env
secrets/*.txt
secrets/*.key
secrets/*.pem
!secrets/README.md
```

### Secret Rotation Procedures

```bash
#!/bin/bash
# scripts/security/rotate-secrets.sh

set -e

rotate_mongo_password() {
    NEW_PASSWORD=$(openssl rand -base64 32)
    echo "$NEW_PASSWORD" > ./secrets/mongo-root-password.txt

    # Update MongoDB password
    docker compose exec mongo mongosh --eval "
        db.getSiblingDB('admin').changeUserPassword('admin', '$NEW_PASSWORD')
    "

    # Restart dependent services
    docker compose restart orchestrator
}

rotate_jwt_key() {
    NEW_KEY=$(openssl rand -hex 32)
    echo "$NEW_KEY" > ./secrets/jwt-signing-key.txt

    # Restart orchestrator to pick up new key
    docker compose restart orchestrator

    echo "WARNING: Existing JWT tokens are now invalid"
}

rotate_nats_token() {
    NEW_TOKEN=$(openssl rand -hex 32)
    echo "$NEW_TOKEN" > ./secrets/nats-auth-token.txt

    # Restart NATS and all services
    docker compose restart nats orchestrator player-001 player-002
}

echo "1. Rotate MongoDB password"
echo "2. Rotate JWT signing key"
echo "3. Rotate NATS auth token"
echo "4. Rotate all"
read -p "Select option: " option

case $option in
    1) rotate_mongo_password ;;
    2) rotate_jwt_key ;;
    3) rotate_nats_token ;;
    4) rotate_mongo_password && rotate_jwt_key && rotate_nats_token ;;
    *) echo "Invalid option" ;;
esac
```

## Network Isolation

### Docker Network Segmentation

```yaml
# docker-compose.yml
networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
  agent:
    driver: bridge

services:
  dashboard:
    networks:
      - frontend
    ports:
      - "3000:3000"  # exposed to host

  orchestrator:
    networks:
      - frontend
      - backend
      - agent
    ports:
      - "50050:50050"  # gRPC for agents

  opensearch:
    networks:
      - backend  # no external access

  mongo:
    networks:
      - backend  # no external access

  nats:
    networks:
      - agent  # only agents and orchestrator

  player-001:
    networks:
      - agent
    ports:
      - "6901:6901"  # noVNC for debugging only
```

### Port Exposure Minimization

```yaml
# Production: minimize exposed ports
services:
  dashboard:
    ports:
      - "127.0.0.1:3000:3000"  # only localhost

  orchestrator:
    # no ports exposed, accessed via reverse proxy

  opensearch:
    # no ports exposed

  mongo:
    # no ports exposed
```

### Internal DNS Resolution

```yaml
services:
  orchestrator:
    environment:
      - OPENSEARCH_URL=https://opensearch:9200  # service name
      - MONGO_URL=mongodb://mongo:27017
      - NATS_URL=nats://nats:4222
```

## Input Validation

### gRPC Message Validation (protoc-gen-validate)

```protobuf
// proto/orchestrator.proto
syntax = "proto3";

import "validate/validate.proto";

message CreateExperimentRequest {
  string name = 1 [(validate.rules).string = {
    min_len: 1,
    max_len: 100,
    pattern: "^[a-zA-Z0-9_-]+$"
  }];

  string description = 2 [(validate.rules).string.max_len = 1000];

  repeated string agent_ids = 3 [(validate.rules).repeated = {
    min_items: 1,
    max_items: 100,
    items: {
      string: {
        pattern: "^PLAYER_[0-9]{3}$"
      }
    }
  }];

  int32 episode_count = 4 [(validate.rules).int32 = {
    gt: 0,
    lte: 1000
  }];
}
```

### Dashboard Input Sanitization

```typescript
// dashboard/src/lib/validation.ts

import { z } from 'zod';

export const experimentSchema = z.object({
  name: z.string().min(1).max(100).regex(/^[a-zA-Z0-9_-]+$/),
  description: z.string().max(1000),
  agentIds: z.array(z.string().regex(/^PLAYER_[0-9]{3}$/)).min(1).max(100),
  episodeCount: z.number().int().positive().max(1000),
});

export function validateExperimentInput(input: unknown) {
  return experimentSchema.parse(input);
}
```

### SQL Injection Prevention (DuckDB)

```rust
// agent-core/src/db/duckdb.rs

use duckdb::{params, Connection};

pub fn record_episode(conn: &Connection, episode_id: &str, kills: i32, survival_time: f64) -> Result<()> {
    // Use parameterized query
    conn.execute(
        "INSERT INTO episodes (episode_id, kills, survival_time) VALUES (?, ?, ?)",
        params![episode_id, kills, survival_time],
    )?;

    Ok(())
}
```

### NoSQL Injection Prevention (MongoDB)

```go
// orchestrator/internal/db/mongo.go

import (
    "go.mongodb.org/mongo-driver/bson"
    "go.mongodb.org/mongo-driver/bson/primitive"
)

func FindExperimentByID(ctx context.Context, experimentID string) (*Experiment, error) {
    // Validate and convert to ObjectID
    objID, err := primitive.ObjectIDFromHex(experimentID)
    if err != nil {
        return nil, fmt.Errorf("invalid experiment ID: %w", err)
    }

    // Use strongly-typed BSON filter
    filter := bson.M{"_id": objID}

    var experiment Experiment
    err = collection.FindOne(ctx, filter).Decode(&experiment)
    if err != nil {
        return nil, err
    }

    return &experiment, nil
}
```

## Security Scanning

### Container Image Scanning in CI

```yaml
# .github/workflows/ci.yml
name: CI

on: [push, pull_request]

jobs:
  security-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build images
        run: docker compose build

      - name: Scan with Trivy
        run: |
          docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
            aquasec/trivy image --severity HIGH,CRITICAL \
            clau-doom-orchestrator:latest

      - name: Scan with Grype
        uses: anchore/scan-action@v3
        with:
          image: "clau-doom-orchestrator:latest"
          fail-build: true
          severity-cutoff: high
```

### Dependency Vulnerability Scanning

```bash
# scripts/security/scan-dependencies.sh
#!/bin/bash

set -e

echo "Scanning Rust dependencies..."
cargo audit --file agent-core/Cargo.lock

echo "Scanning Go dependencies..."
(cd orchestrator && govulncheck ./...)

echo "Scanning Python dependencies..."
(cd analytics && pip-audit)

echo "Scanning Node.js dependencies..."
(cd dashboard && npm audit --audit-level=high)
```

### SAST Tools by Language

```yaml
# .github/workflows/sast.yml
name: SAST

on: [push, pull_request]

jobs:
  rust-clippy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - run: cargo clippy --all-targets -- -D warnings

  go-gosec:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: securego/gosec@master
        with:
          args: ./orchestrator/...

  typescript-eslint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: cd dashboard && npm ci && npm run lint
```

## Incident Response

### Log-Based Forensics

```yaml
# docker-compose.yml
services:
  orchestrator:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"
        labels: "service,version"
```

```bash
# scripts/security/collect-logs.sh
#!/bin/bash

INCIDENT_DATE=$(date +%Y%m%d_%H%M%S)
LOG_DIR="./incidents/${INCIDENT_DATE}"

mkdir -p "$LOG_DIR"

# Collect container logs
for service in orchestrator player-001 opensearch mongo nats; do
    docker compose logs --no-color "$service" > "$LOG_DIR/${service}.log"
done

# Collect system logs
journalctl --since "1 hour ago" > "$LOG_DIR/system.log"

# Archive
tar -czf "./incidents/${INCIDENT_DATE}.tar.gz" "$LOG_DIR"

echo "Logs collected in ./incidents/${INCIDENT_DATE}.tar.gz"
```

### Container Isolation Procedures

```bash
# scripts/security/isolate-container.sh
#!/bin/bash

CONTAINER=$1

if [ -z "$CONTAINER" ]; then
    echo "Usage: $0 <container-name>"
    exit 1
fi

echo "Isolating container: $CONTAINER"

# Disconnect from all networks
for network in $(docker inspect "$CONTAINER" --format '{{range .NetworkSettings.Networks}}{{.NetworkID}} {{end}}'); do
    docker network disconnect "$network" "$CONTAINER"
done

# Create forensics snapshot
docker commit "$CONTAINER" "forensics-${CONTAINER}-$(date +%Y%m%d_%H%M%S)"

# Stop container
docker stop "$CONTAINER"

echo "Container isolated. Forensics image created."
```

### Credential Revocation

```bash
# scripts/security/revoke-credentials.sh
#!/bin/bash

USER_ID=$1

if [ -z "$USER_ID" ]; then
    echo "Usage: $0 <user-id>"
    exit 1
fi

# Rotate JWT signing key (invalidates all tokens)
./scripts/security/rotate-secrets.sh 2

# Remove user from database
docker compose exec mongo mongosh clau-doom --eval "
    db.users.updateOne(
        {user_id: '$USER_ID'},
        {\$set: {revoked: true, revoked_at: new Date()}}
    )
"

echo "Credentials revoked for user: $USER_ID"
```

### Recovery Procedures

```bash
# scripts/security/recover.sh
#!/bin/bash

echo "Initiating recovery..."

# 1. Rotate all secrets
./scripts/security/rotate-secrets.sh 4

# 2. Rebuild all images from scratch
docker compose build --no-cache

# 3. Recreate all containers
docker compose down -v
docker compose up -d

# 4. Verify services
docker compose ps
docker compose logs --tail=50

echo "Recovery complete. Review logs for errors."
```
