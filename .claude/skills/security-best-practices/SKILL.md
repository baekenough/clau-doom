---
name: security-best-practices
description: Security patterns for mTLS between services, JWT authentication for dashboard, container hardening, Docker secrets management, and network isolation
user-invocable: false
---

# Security Best Practices for clau-doom

## mTLS Between Services

### Certificate Generation

```bash
# Self-signed CA for development
# Directory structure: certs/{ca,server,client}/

mkdir -p certs/{ca,server,client}

# Generate CA private key and certificate
openssl genrsa -out certs/ca/ca-key.pem 4096
openssl req -new -x509 -days 3650 -key certs/ca/ca-key.pem \
  -out certs/ca/ca-cert.pem \
  -subj "/C=US/ST=CA/L=SF/O=clau-doom/CN=clau-doom-ca"

# Generate server private key and CSR
openssl genrsa -out certs/server/server-key.pem 4096
openssl req -new -key certs/server/server-key.pem \
  -out certs/server/server.csr \
  -subj "/C=US/ST=CA/L=SF/O=clau-doom/CN=orchestrator"

# Sign server certificate with CA
openssl x509 -req -days 365 \
  -in certs/server/server.csr \
  -CA certs/ca/ca-cert.pem \
  -CAkey certs/ca/ca-key.pem \
  -CAcreateserial \
  -out certs/server/server-cert.pem

# Generate client private key and CSR
openssl genrsa -out certs/client/client-key.pem 4096
openssl req -new -key certs/client/client-key.pem \
  -out certs/client/client.csr \
  -subj "/C=US/ST=CA/L=SF/O=clau-doom/CN=agent-client"

# Sign client certificate with CA
openssl x509 -req -days 365 \
  -in certs/client/client.csr \
  -CA certs/ca/ca-cert.pem \
  -CAkey certs/ca/ca-key.pem \
  -CAcreateserial \
  -out certs/client/client-cert.pem

# Set permissions (read-only for keys)
chmod 400 certs/*/.*-key.pem
chmod 444 certs/*/.*-cert.pem
```

### Rust tonic TLS (Server)

```rust
// agent-core/src/grpc_server.rs
use tonic::transport::{Server, ServerTlsConfig, Identity};
use std::fs;

pub async fn run_grpc_server() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "[::1]:50051".parse()?;

    // Load server certificate and key
    let cert = fs::read_to_string("certs/server/server-cert.pem")?;
    let key = fs::read_to_string("certs/server/server-key.pem")?;
    let server_identity = Identity::from_pem(cert, key);

    // Load CA certificate for client verification
    let ca_cert = fs::read_to_string("certs/ca/ca-cert.pem")?;

    let tls_config = ServerTlsConfig::new()
        .identity(server_identity)
        .client_ca_root(tonic::transport::Certificate::from_pem(ca_cert));

    Server::builder()
        .tls_config(tls_config)?
        .add_service(agent_service)
        .serve(addr)
        .await?;

    Ok(())
}
```

### Rust tonic TLS (Client)

```rust
// agent-core/src/grpc_client.rs
use tonic::transport::{Channel, ClientTlsConfig, Identity};
use std::fs;

pub async fn create_grpc_client() -> Result<Channel, Box<dyn std::error::Error>> {
    // Load client certificate and key
    let cert = fs::read_to_string("certs/client/client-cert.pem")?;
    let key = fs::read_to_string("certs/client/client-key.pem")?;
    let client_identity = Identity::from_pem(cert, key);

    // Load CA certificate for server verification
    let ca_cert = fs::read_to_string("certs/ca/ca-cert.pem")?;

    let tls_config = ClientTlsConfig::new()
        .identity(client_identity)
        .ca_certificate(tonic::transport::Certificate::from_pem(ca_cert))
        .domain_name("orchestrator");

    let channel = Channel::from_static("https://orchestrator:50051")
        .tls_config(tls_config)?
        .connect()
        .await?;

    Ok(channel)
}
```

### Go grpc-go TLS (Server)

```go
// orchestrator/internal/grpc/server.go
package grpc

import (
    "crypto/tls"
    "crypto/x509"
    "os"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials"
)

func NewServer() (*grpc.Server, error) {
    // Load server certificate and key
    serverCert, err := tls.LoadX509KeyPair(
        "certs/server/server-cert.pem",
        "certs/server/server-key.pem",
    )
    if err != nil {
        return nil, err
    }

    // Load CA certificate for client verification
    caCert, err := os.ReadFile("certs/ca/ca-cert.pem")
    if err != nil {
        return nil, err
    }
    certPool := x509.NewCertPool()
    certPool.AppendCertsFromPEM(caCert)

    tlsConfig := &tls.Config{
        Certificates: []tls.Certificate{serverCert},
        ClientAuth:   tls.RequireAndVerifyClientCert,
        ClientCAs:    certPool,
    }

    creds := credentials.NewTLS(tlsConfig)
    opts := []grpc.ServerOption{
        grpc.Creds(creds),
    }

    return grpc.NewServer(opts...), nil
}
```

### Go grpc-go TLS (Client)

```go
// orchestrator/internal/grpc/client.go
package grpc

import (
    "crypto/tls"
    "crypto/x509"
    "os"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials"
)

func NewClient(addr string) (*grpc.ClientConn, error) {
    // Load client certificate and key
    clientCert, err := tls.LoadX509KeyPair(
        "certs/client/client-cert.pem",
        "certs/client/client-key.pem",
    )
    if err != nil {
        return nil, err
    }

    // Load CA certificate for server verification
    caCert, err := os.ReadFile("certs/ca/ca-cert.pem")
    if err != nil {
        return nil, err
    }
    certPool := x509.NewCertPool()
    certPool.AppendCertsFromPEM(caCert)

    tlsConfig := &tls.Config{
        Certificates: []tls.Certificate{clientCert},
        RootCAs:      certPool,
        ServerName:   "orchestrator",
    }

    creds := credentials.NewTLS(tlsConfig)
    opts := []grpc.DialOption{
        grpc.WithTransportCredentials(creds),
    }

    return grpc.Dial(addr, opts...)
}
```

### NATS TLS Configuration

```conf
# nats-server.conf
tls {
  cert_file: "/certs/server/server-cert.pem"
  key_file:  "/certs/server/server-key.pem"
  ca_file:   "/certs/ca/ca-cert.pem"
  verify:    true
}
```

### MongoDB TLS Configuration

```yaml
# mongod.conf
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /certs/server/mongodb.pem
    CAFile: /certs/ca/ca-cert.pem
    allowConnectionsWithoutCertificates: false
```

MongoDB client connection URI:

```
mongodb://mongodb:27017/?tls=true&tlsCAFile=/certs/ca/ca-cert.pem&tlsCertificateKeyFile=/certs/client/client.pem
```

### OpenSearch TLS Configuration

```yaml
# opensearch.yml
plugins.security.ssl.transport.pemcert_filepath: certs/server/server-cert.pem
plugins.security.ssl.transport.pemkey_filepath: certs/server/server-key.pem
plugins.security.ssl.transport.pemtrustedcas_filepath: certs/ca/ca-cert.pem
plugins.security.ssl.transport.enforce_hostname_verification: true

plugins.security.ssl.http.enabled: true
plugins.security.ssl.http.pemcert_filepath: certs/server/server-cert.pem
plugins.security.ssl.http.pemkey_filepath: certs/server/server-key.pem
plugins.security.ssl.http.pemtrustedcas_filepath: certs/ca/ca-cert.pem
```

### Certificate Rotation with File Watching

```rust
// agent-core/src/tls_watcher.rs
use notify::{Watcher, RecursiveMode, Event};
use std::sync::Arc;
use tokio::sync::RwLock;

pub struct TlsWatcher {
    cert_path: String,
    key_path: String,
    current_identity: Arc<RwLock<Identity>>,
}

impl TlsWatcher {
    pub fn new(cert_path: String, key_path: String) -> Self {
        let initial_cert = fs::read_to_string(&cert_path).unwrap();
        let initial_key = fs::read_to_string(&key_path).unwrap();
        let identity = Identity::from_pem(initial_cert, initial_key);

        TlsWatcher {
            cert_path,
            key_path,
            current_identity: Arc::new(RwLock::new(identity)),
        }
    }

    pub async fn watch(&self) -> Result<(), Box<dyn std::error::Error>> {
        let (tx, mut rx) = tokio::sync::mpsc::channel(10);
        let mut watcher = notify::recommended_watcher(move |res: Result<Event, _>| {
            if let Ok(event) = res {
                let _ = tx.blocking_send(event);
            }
        })?;

        watcher.watch(&self.cert_path.as_ref(), RecursiveMode::NonRecursive)?;
        watcher.watch(&self.key_path.as_ref(), RecursiveMode::NonRecursive)?;

        while let Some(_event) = rx.recv().await {
            // Reload certificates
            let cert = fs::read_to_string(&self.cert_path)?;
            let key = fs::read_to_string(&self.key_path)?;
            let new_identity = Identity::from_pem(cert, key);

            let mut identity = self.current_identity.write().await;
            *identity = new_identity;

            tracing::info!("TLS certificates reloaded");
        }

        Ok(())
    }

    pub fn get_identity(&self) -> Arc<RwLock<Identity>> {
        self.current_identity.clone()
    }
}
```

## JWT Authentication (Dashboard API)

### Token Structure

```
Header:
{
  "alg": "HS256",
  "typ": "JWT"
}

Claims:
{
  "sub": "user-id",
  "exp": 1735689600,
  "iat": 1735603200,
  "roles": ["admin", "researcher"],
  "experiment_access": ["DOE-042", "DOE-043"]
}
```

### Go Token Generation

```go
// orchestrator/internal/auth/jwt.go
package auth

import (
    "time"
    "github.com/golang-jwt/jwt/v5"
)

type Claims struct {
    Sub             string   `json:"sub"`
    Roles           []string `json:"roles"`
    ExperimentAccess []string `json:"experiment_access"`
    jwt.RegisteredClaims
}

var signingKey = []byte("your-secret-key-from-env")

func GenerateToken(userID string, roles []string, experiments []string) (string, error) {
    claims := &Claims{
        Sub:   userID,
        Roles: roles,
        ExperimentAccess: experiments,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(24 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString(signingKey)
}

func ValidateToken(tokenString string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
        return signingKey, nil
    })

    if err != nil {
        return nil, err
    }

    if claims, ok := token.Claims.(*Claims); ok && token.Valid {
        return claims, nil
    }

    return nil, jwt.ErrSignatureInvalid
}
```

### Go gRPC Interceptor

```go
// orchestrator/internal/auth/interceptor.go
package auth

import (
    "context"
    "strings"

    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/metadata"
    "google.golang.org/grpc/status"
)

func UnaryAuthInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    // Extract token from metadata
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return nil, status.Error(codes.Unauthenticated, "missing metadata")
    }

    auth := md.Get("authorization")
    if len(auth) == 0 {
        return nil, status.Error(codes.Unauthenticated, "missing authorization header")
    }

    tokenString := strings.TrimPrefix(auth[0], "Bearer ")
    claims, err := ValidateToken(tokenString)
    if err != nil {
        return nil, status.Error(codes.Unauthenticated, "invalid token")
    }

    // Add claims to context
    ctx = context.WithValue(ctx, "claims", claims)

    return handler(ctx, req)
}

func StreamAuthInterceptor(srv interface{}, ss grpc.ServerStream, info *grpc.StreamServerInfo, handler grpc.StreamHandler) error {
    // Similar to UnaryAuthInterceptor
    return handler(srv, ss)
}
```

### Next.js API Route Middleware

```typescript
// dashboard/src/middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { jwtVerify } from 'jose';

const JWT_SECRET = new TextEncoder().encode(
  process.env.JWT_SECRET || 'your-secret-key'
);

export async function middleware(request: NextRequest) {
  const token = request.cookies.get('auth-token')?.value;

  if (!token) {
    return NextResponse.redirect(new URL('/login', request.url));
  }

  try {
    const { payload } = await jwtVerify(token, JWT_SECRET);

    // Check role-based access
    const path = request.nextUrl.pathname;
    if (path.startsWith('/admin') && !payload.roles?.includes('admin')) {
      return NextResponse.redirect(new URL('/unauthorized', request.url));
    }

    return NextResponse.next();
  } catch (error) {
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: ['/dashboard/:path*', '/api/:path*', '/admin/:path*'],
};
```

### Client-Side Auth Context

```typescript
// dashboard/src/contexts/AuthContext.tsx
'use client';

import { createContext, useContext, useEffect, useState } from 'react';

interface User {
  id: string;
  roles: string[];
  experimentAccess: string[];
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  const login = async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    setUser(data.user);
  };

  const logout = async () => {
    await fetch('/api/auth/logout', { method: 'POST' });
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
};
```

### Refresh Token Pattern

```go
// orchestrator/internal/auth/refresh.go
package auth

import "time"

func GenerateTokenPair(userID string, roles []string, experiments []string) (accessToken, refreshToken string, err error) {
    // Short-lived access token (15 minutes)
    accessClaims := &Claims{
        Sub:   userID,
        Roles: roles,
        ExperimentAccess: experiments,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(15 * time.Minute)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
        },
    }
    accessToken, err = jwt.NewWithClaims(jwt.SigningMethodHS256, accessClaims).SignedString(signingKey)
    if err != nil {
        return "", "", err
    }

    // Long-lived refresh token (7 days)
    refreshClaims := &Claims{
        Sub: userID,
        RegisteredClaims: jwt.RegisteredClaims{
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(7 * 24 * time.Hour)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
        },
    }
    refreshToken, err = jwt.NewWithClaims(jwt.SigningMethodHS256, refreshClaims).SignedString(signingKey)
    if err != nil {
        return "", "", err
    }

    return accessToken, refreshToken, nil
}
```

## Container Hardening

### Non-Root User Pattern

```dockerfile
# docker/agent/Dockerfile
FROM rust:1.83-bookworm AS builder

WORKDIR /build
COPY agent-core/ .
RUN cargo build --release --workspace

FROM debian:bookworm-slim AS runtime

# Create non-root user
RUN groupadd -r agent && useradd -r -g agent -u 1001 agent

RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder --chown=agent:agent /build/target/release/agent-core /usr/local/bin/agent-core

# Switch to non-root user
USER agent

ENV RUST_LOG=info
ENTRYPOINT ["agent-core"]
```

### Distroless Base Image

```dockerfile
# docker/orchestrator/Dockerfile
FROM golang:1.23-bookworm AS builder

WORKDIR /build
COPY orchestrator/ .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /clau-doom ./cmd/clau-doom

FROM gcr.io/distroless/static-debian12:nonroot

# Copy binary with correct ownership
COPY --from=builder --chown=nonroot:nonroot /clau-doom /clau-doom

# distroless/static:nonroot already runs as UID 65532
ENTRYPOINT ["/clau-doom"]
```

### Alpine Hardening

```dockerfile
# docker/vizdoom/Dockerfile
FROM alpine:3.19

# Create non-root user
RUN addgroup -g 1001 vizdoom && \
    adduser -D -u 1001 -G vizdoom vizdoom

# Install dependencies
RUN apk add --no-cache \
    python3 py3-pip \
    xvfb x11vnc novnc

# Install VizDoom as non-root
USER vizdoom
RUN pip3 install --user --no-cache-dir vizdoom==1.2.0

COPY --chown=vizdoom:vizdoom docker/vizdoom/entrypoint.sh /entrypoint.sh
RUN chmod 500 /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
```

### Docker Compose Hardening

```yaml
# docker-compose.yml (security-focused)
services:
  orchestrator:
    build:
      context: .
      dockerfile: docker/orchestrator/Dockerfile
    read_only: true
    cap_drop:
      - ALL
    security_opt:
      - no-new-privileges:true
    pids_limit: 100
    tmpfs:
      - /tmp:size=64M,mode=1777

  vizdoom:
    build:
      context: .
      dockerfile: docker/vizdoom/Dockerfile
    read_only: false  # Needs write for /tmp/.X11-unix
    cap_drop:
      - ALL
    cap_add:
      - SETGID
      - SETUID
    security_opt:
      - no-new-privileges:true
    pids_limit: 200
    tmpfs:
      - /tmp:size=256M,mode=1777
```

### Image Scanning in CI

```yaml
# .github/workflows/security.yml
name: Security Scan

on:
  push:
    branches: [main, develop]
  pull_request:

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Build images
        run: |
          docker compose build

      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: clau-doom-orchestrator:latest
          format: 'sarif'
          output: 'trivy-results.sarif'
          severity: 'CRITICAL,HIGH'

      - name: Upload Trivy results
        uses: github/codeql-action/upload-sarif@v2
        with:
          sarif_file: 'trivy-results.sarif'

      - name: Run Grype scan
        uses: anchore/scan-action@v3
        with:
          image: clau-doom-orchestrator:latest
          fail-build: true
          severity-cutoff: high
```

## Secrets Management

### Docker Secrets Creation

```bash
# Create secrets from files
docker secret create mongodb_password /path/to/mongodb_password.txt

# Create secrets from stdin
echo "supersecret" | docker secret create jwt_signing_key -

# Create secrets from environment (in deployment script)
echo "$JWT_SIGNING_KEY" | docker secret create jwt_signing_key -
```

### Docker Compose with Secrets

```yaml
# docker-compose.yml
services:
  orchestrator:
    secrets:
      - jwt_signing_key
      - nats_auth_token
    environment:
      - JWT_SECRET_FILE=/run/secrets/jwt_signing_key
      - NATS_TOKEN_FILE=/run/secrets/nats_auth_token

  mongodb:
    secrets:
      - mongodb_password
    environment:
      - MONGO_INITDB_ROOT_PASSWORD_FILE=/run/secrets/mongodb_password

secrets:
  jwt_signing_key:
    file: ./secrets/jwt_signing_key.txt
  mongodb_password:
    file: ./secrets/mongodb_password.txt
  nats_auth_token:
    file: ./secrets/nats_auth_token.txt
```

### Reading Secrets in Application

```go
// orchestrator/internal/config/secrets.go
package config

import (
    "os"
    "strings"
)

func ReadSecret(envVar string) (string, error) {
    // Try file-based secret first
    secretFile := os.Getenv(envVar + "_FILE")
    if secretFile != "" {
        content, err := os.ReadFile(secretFile)
        if err != nil {
            return "", err
        }
        return strings.TrimSpace(string(content)), nil
    }

    // Fallback to environment variable
    return os.Getenv(envVar), nil
}

// Usage:
// jwtSecret, err := ReadSecret("JWT_SECRET")
```

### Environment Variable Safety

```yaml
# .env.example (committed to git)
NATS_URL=nats://nats:4222
GRPC_PORT=50051
LOG_LEVEL=info

# NEVER PUT SECRETS IN .env.example
# Use Docker secrets or external secret manager
```

```gitignore
# .gitignore
.env
.env.local
secrets/
certs/
```

### Secrets Validation

```go
// orchestrator/cmd/clau-doom/main.go
package main

import (
    "log"
    "os"
)

func validateSecrets() {
    required := []string{
        "JWT_SECRET",
        "MONGODB_PASSWORD",
        "OPENSEARCH_PASSWORD",
        "NATS_AUTH_TOKEN",
    }

    missing := []string{}
    for _, secret := range required {
        if _, err := config.ReadSecret(secret); err != nil {
            missing = append(missing, secret)
        }
    }

    if len(missing) > 0 {
        log.Fatalf("Missing required secrets: %v", missing)
    }
}
```

## Network Isolation

### Network Segmentation

```yaml
# docker-compose.yml
services:
  dashboard:
    networks:
      - frontend
      - backend

  orchestrator:
    networks:
      - backend
      - agent-net
    ports:
      - "50051:50051"  # Exposed for dashboard

  vizdoom:
    networks:
      - agent-net
    ports:
      - "6080:6080"  # noVNC WebSocket

  nats:
    networks:
      - backend  # Internal only

  mongodb:
    networks:
      - backend  # Internal only

  opensearch:
    networks:
      - backend  # Internal only

networks:
  frontend:
    driver: bridge
  backend:
    driver: bridge
    internal: true  # No external access
  agent-net:
    driver: bridge
    internal: true
```

### Port Exposure Minimization

```yaml
# Only expose what's necessary
services:
  dashboard:
    ports:
      - "3000:3000"  # Public

  vizdoom:
    ports:
      - "6080:6080"  # Public (noVNC)

  orchestrator:
    # No exposed ports - accessed via internal network only
    expose:
      - "50051"  # Accessible only within backend network

  nats:
    # No exposed ports - internal only
    expose:
      - "4222"

  mongodb:
    # No exposed ports - internal only
    expose:
      - "27017"

  opensearch:
    # No exposed ports - internal only
    expose:
      - "9200"
```

### Service-to-Service DNS Resolution

```go
// orchestrator/internal/config/config.go
package config

type Config struct {
    NATSUrl        string // "nats://nats:4222"
    MongoDBUrl     string // "mongodb://mongodb:27017"
    OpenSearchUrl  string // "https://opensearch:9200"
}

// Services resolve each other by name within Docker network
```

### Firewall Rules (Host-Level)

```bash
# Only allow dashboard and noVNC ports externally
# All other services internal only

sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH
sudo ufw allow 22/tcp

# Allow dashboard
sudo ufw allow 3000/tcp

# Allow noVNC
sudo ufw allow 6080/tcp

# Deny all other ports
sudo ufw enable
```

## Input Validation

### gRPC Validation with protoc-gen-validate

```protobuf
// orchestrator/proto/agent.proto
syntax = "proto3";

import "validate/validate.proto";

message StartExperimentRequest {
  string experiment_id = 1 [(validate.rules).string = {
    pattern: "^DOE-[0-9]{3}$",
    min_len: 7,
    max_len: 7
  }];

  int32 episode_count = 2 [(validate.rules).int32 = {
    gte: 1,
    lte: 1000
  }];

  repeated Factor factors = 3 [(validate.rules).repeated = {
    min_items: 1,
    max_items: 10
  }];
}

message Factor {
  string name = 1 [(validate.rules).string = {
    min_len: 1,
    max_len: 50,
    pattern: "^[a-z_]+$"
  }];

  double value = 2 [(validate.rules).double = {
    gte: 0.0,
    lte: 1.0
  }];
}
```

### Server-Side Validation Interceptor

```go
// orchestrator/internal/grpc/validator.go
package grpc

import (
    "context"
    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

type validator interface {
    Validate() error
}

func ValidationInterceptor(ctx context.Context, req interface{}, info *grpc.UnaryServerInfo, handler grpc.UnaryHandler) (interface{}, error) {
    if v, ok := req.(validator); ok {
        if err := v.Validate(); err != nil {
            return nil, status.Error(codes.InvalidArgument, err.Error())
        }
    }
    return handler(ctx, req)
}
```

### Dashboard Input Validation with Zod

```typescript
// dashboard/src/lib/validators.ts
import { z } from 'zod';

export const experimentSchema = z.object({
  experimentId: z.string().regex(/^DOE-[0-9]{3}$/),
  episodeCount: z.number().int().min(1).max(1000),
  factors: z.array(
    z.object({
      name: z.string().min(1).max(50).regex(/^[a-z_]+$/),
      value: z.number().min(0).max(1),
    })
  ).min(1).max(10),
});

export type ExperimentInput = z.infer<typeof experimentSchema>;
```

### XSS Prevention

```typescript
// dashboard/src/components/ExperimentLog.tsx
import DOMPurify from 'isomorphic-dompurify';

export function ExperimentLog({ log }: { log: string }) {
  // React auto-escapes by default, but for rich content:
  const sanitized = DOMPurify.sanitize(log, {
    ALLOWED_TAGS: ['b', 'i', 'em', 'strong', 'code', 'pre'],
    ALLOWED_ATTR: [],
  });

  return <div dangerouslySetInnerHTML={{ __html: sanitized }} />;
}
```

### CSRF Protection

```typescript
// dashboard/src/middleware.ts (add CSRF token)
import { NextRequest, NextResponse } from 'next/server';
import { randomBytes } from 'crypto';

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // Generate CSRF token if not present
  if (!request.cookies.get('csrf-token')) {
    const csrfToken = randomBytes(32).toString('hex');
    response.cookies.set('csrf-token', csrfToken, {
      httpOnly: true,
      secure: true,
      sameSite: 'strict',
    });
  }

  return response;
}
```

### Database Query Safety

```python
# analytics/data_processing.py
import duckdb

def query_episodes_safe(experiment_id: str, min_score: float):
    conn = duckdb.connect('data/experiments.duckdb')

    # SAFE: Parameterized query
    result = conn.execute("""
        SELECT episode_id, score, metrics
        FROM episodes
        WHERE experiment_id = $1 AND score >= $2
    """, [experiment_id, min_score]).fetchall()

    return result

# UNSAFE: String interpolation (NEVER DO THIS)
def query_episodes_unsafe(experiment_id: str):
    conn = duckdb.connect('data/experiments.duckdb')

    # UNSAFE: SQL injection vulnerability
    result = conn.execute(f"""
        SELECT * FROM episodes WHERE experiment_id = '{experiment_id}'
    """).fetchall()

    return result
```

```go
// orchestrator/internal/db/queries.go
package db

import "github.com/mongodb/mongo-go-driver/bson"

// SAFE: MongoDB query with sanitized input
func FindDocumentsByExperiment(experimentID string) ([]Document, error) {
    filter := bson.M{"experiment_id": experimentID}

    cursor, err := collection.Find(ctx, filter)
    // ...
}

// UNSAFE: Building query from user input (DON'T DO THIS)
func UnsafeQuery(userInput map[string]interface{}) error {
    // User could inject "$where" or other operators
    cursor, err := collection.Find(ctx, userInput)
    // ...
}
```

## Dependency Scanning

### Rust Cargo Audit

```yaml
# .github/workflows/security.yml
jobs:
  cargo-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions-rust-lang/audit@v1
        with:
          denyWarnings: true
```

### Go Govulncheck

```yaml
jobs:
  govulncheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v4
        with:
          go-version: '1.23'
      - run: go install golang.org/x/vuln/cmd/govulncheck@latest
      - run: govulncheck ./...
```

### Python Safety

```yaml
jobs:
  python-safety:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v4
        with:
          python-version: '3.12'
      - run: pip install safety
      - run: safety check --json
```

### TypeScript npm Audit

```yaml
jobs:
  npm-audit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - run: npm audit --audit-level=high
```

## Anti-Patterns to Avoid

1. **Hardcoded Credentials**

```go
// WRONG
const jwtSecret = "supersecret123"  // Hardcoded secret

// CORRECT
jwtSecret, err := config.ReadSecret("JWT_SECRET")
```

2. **Running Containers as Root**

```dockerfile
# WRONG
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y myapp
CMD ["/usr/bin/myapp"]

# CORRECT
FROM ubuntu:22.04
RUN groupadd -r myapp && useradd -r -g myapp myapp
RUN apt-get update && apt-get install -y myapp
USER myapp
CMD ["/usr/bin/myapp"]
```

3. **Exposing All Ports**

```yaml
# WRONG
services:
  mongodb:
    ports:
      - "27017:27017"  # Exposed to host

# CORRECT
services:
  mongodb:
    expose:
      - "27017"  # Internal network only
```

4. **Using latest Tag**

```dockerfile
# WRONG
FROM node:latest  # Version drift, reproducibility issues

# CORRECT
FROM node:22.11.0-slim  # Pinned version
```

5. **Disabling TLS for Convenience**

```go
// WRONG
conn, err := grpc.Dial(addr, grpc.WithInsecure())

// CORRECT
creds := credentials.NewTLS(tlsConfig)
conn, err := grpc.Dial(addr, grpc.WithTransportCredentials(creds))
```

6. **Storing Secrets in Environment Variables**

```yaml
# WRONG (visible in docker inspect)
environment:
  - JWT_SECRET=supersecret123

# CORRECT (Docker secrets)
secrets:
  - jwt_secret
environment:
  - JWT_SECRET_FILE=/run/secrets/jwt_secret
```
