# gRPC Reference Guide

## Key Resources

- [gRPC Official Documentation](https://grpc.io/docs/)
- [Protocol Buffers v3 Language Guide](https://protobuf.dev/programming-guides/proto3/)
- [Tonic (Rust gRPC)](https://github.com/hyperium/tonic)
- [grpc-go (Go gRPC)](https://github.com/grpc/grpc-go)
- [Buf CLI](https://buf.build/docs/)
- [gRPC Status Codes](https://grpc.github.io/grpc/core/md_doc_statuscodes.html)

## clau-doom Context

gRPC provides the communication backbone for clau-doom's distributed architecture:

```
Dashboard (Next.js)
    │
    └─ WebSocket ───> Orchestrator (Go)
                          │
                          ├─ gRPC ──> Agent-Core (Rust)
                          ├─ gRPC ──> Agent-Core (Rust)
                          └─ gRPC ──> Agent-Core (Rust)
                          │
                          └─ NATS pub/sub (real-time events)
```

**Service Responsibilities:**

| Service | Language | Role | Port |
|---------|----------|------|------|
| `AgentService` | Rust (tonic) | Decision engine, RAG queries, scoring | 50052+ |
| `OrchestratorService` | Go (grpc-go) | Experiment lifecycle, generation mgmt | 50051 |
| `HealthService` | Both | Standard gRPC health checking | same |

**Communication Patterns:**

- **Unary RPC**: Single action request (low latency < 100ms)
- **Server Streaming**: Observation/monitoring agents over time
- **Bidirectional Streaming**: Live game sessions (agent ↔ orchestrator)
- **NATS**: Ephemeral event broadcast (dashboard updates)
- **NATS JetStream**: Durable event storage (analytics replay)

## Proto3 Design Patterns

### Service Definition Conventions

**Verb-Noun Method Naming:**

```protobuf
// api/proto/agent/v1/agent.proto
syntax = "proto3";
package claudoom.agent.v1;

option go_package = "github.com/clau-doom/orchestrator/pkg/proto/agent/v1";

service AgentService {
    // Unary: request single action
    rpc GetAction(GetActionRequest) returns (GetActionResponse);

    // Server streaming: observe agent behavior
    rpc ObserveAgent(ObserveAgentRequest) returns (stream AgentObservation);

    // Client streaming: batch evaluation
    rpc BatchEvaluate(stream GameState) returns (BatchEvaluateResponse);

    // Bidirectional: live session
    rpc LiveSession(stream AgentMessage) returns (stream OrchestratorMessage);
}
```

**Naming Conventions:**

- Methods: `VerbNoun` (GetAction, StartExperiment, StreamEvents)
- Request messages: `{MethodName}Request`
- Response messages: `{MethodName}Response`
- Streaming items: descriptive nouns (AgentObservation, GameState)

### Message Design

**Field Numbering:**

```protobuf
message GameState {
    // Core fields: 1-15 (most frequently used)
    string agent_id = 1;
    int32 generation_id = 2;
    int32 tick = 3;

    // Observation data: 16-31
    bytes screen_buffer = 16;
    int32 screen_width = 17;
    int32 screen_height = 18;

    // Game variables: 32-47
    float health = 32;
    int32 ammo = 33;
    int32 kill_count = 34;

    // Metadata: 48+
    google.protobuf.Timestamp timestamp = 48;
}
```

**Best Practices:**

- Reserve 1-15 for frequently accessed fields (efficient encoding)
- Group related fields together (16-31, 32-47)
- Never reuse field numbers (breaks backward compatibility)
- Use `reserved` for removed fields

**Oneofs (Tagged Unions):**

```protobuf
message AgentMessage {
    oneof payload {
        Action action = 1;
        AgentStatus status = 2;
        AgentMetrics metrics = 3;
        ErrorReport error = 4;
    }
}
```

**Enums:**

```protobuf
enum ActionType {
    ACTION_TYPE_UNSPECIFIED = 0;  // Always have zero value
    ACTION_TYPE_MOVE_FORWARD = 1;
    ACTION_TYPE_MOVE_BACKWARD = 2;
    ACTION_TYPE_TURN_LEFT = 3;
    ACTION_TYPE_TURN_RIGHT = 4;
    ACTION_TYPE_ATTACK = 5;
    ACTION_TYPE_USE = 6;
}
```

### Streaming Patterns

**Unary (Request-Response):**

```
Client ──GetAction(state)──> Server
Client <──Action──────────── Server
```

Use for: Single action requests, fast decisions (< 100ms)

**Server Streaming:**

```
Client ──ObserveAgent(agent_id)──> Server
Client <──observation stream────── Server
Client <──observation stream────── Server
Client <──observation stream────── Server
```

Use for: Monitoring agents, real-time metrics, event streams

**Client Streaming:**

```
Client ──state 1──> Server
Client ──state 2──> Server
Client ──state 3──> Server
Client <──response─ Server
```

Use for: Batch processing, bulk uploads

**Bidirectional Streaming:**

```
Client ──state 1──> Server
Client <──action 1─ Server
Client ──state 2──> Server
Client <──action 2─ Server
Client <──metrics── Server
```

Use for: Live game sessions, real-time interaction

### Proto File Organization

```
api/proto/
├── agent/
│   └── v1/
│       ├── agent.proto          # Service definition
│       ├── messages.proto       # Message types
│       └── enums.proto          # Shared enums
├── orchestrator/
│   └── v1/
│       ├── orchestrator.proto   # Service definition
│       ├── experiment.proto     # Experiment messages
│       └── generation.proto     # Generation messages
└── common/
    └── v1/
        ├── health.proto         # Health check
        └── errors.proto         # Error types
```

**Import Paths:**

```protobuf
// In orchestrator/v1/orchestrator.proto
syntax = "proto3";
package claudoom.orchestrator.v1;

import "google/protobuf/timestamp.proto";
import "google/protobuf/empty.proto";
import "agent/v1/messages.proto";  // Cross-service import
import "common/v1/health.proto";
```

**Package Naming:**

- Pattern: `{project}.{service}.{version}`
- Example: `claudoom.agent.v1`
- Go package: `github.com/clau-doom/orchestrator/pkg/proto/agent/v1`

## Buf Tooling

### buf.yaml Configuration

```yaml
# /Users/sangyi/workspace/research/clau-doom/buf.yaml
version: v1
name: buf.build/clau-doom/api
deps:
  - buf.build/googleapis/googleapis
lint:
  use:
    - DEFAULT
    - COMMENTS
  except:
    - PACKAGE_VERSION_SUFFIX  # Allow v1, v2, etc.
  enum_zero_value_suffix: _UNSPECIFIED
  rpc_allow_same_request_response: false
  rpc_allow_google_protobuf_empty_requests: true
  rpc_allow_google_protobuf_empty_responses: true
breaking:
  use:
    - FILE
  except:
    - EXTENSION_MESSAGE_NO_DELETE  # Allow message extension removal during dev
```

### buf.gen.yaml for Code Generation

```yaml
# /Users/sangyi/workspace/research/clau-doom/buf.gen.yaml
version: v1
managed:
  enabled: true
  go_package_prefix:
    default: github.com/clau-doom/orchestrator/pkg/proto
plugins:
  # Go code generation
  - plugin: buf.build/protocolbuffers/go:v1.31.0
    out: orchestrator/pkg/proto
    opt:
      - paths=source_relative

  # Go gRPC code generation
  - plugin: buf.build/grpc/go:v1.3.0
    out: orchestrator/pkg/proto
    opt:
      - paths=source_relative
      - require_unimplemented_servers=false

  # Rust code generation (via prost)
  - plugin: buf.build/community/neoeinstein-prost:v0.2.3
    out: agent-core/src/proto

  # Rust gRPC code generation (via tonic)
  - plugin: buf.build/community/neoeinstein-tonic:v0.3.0
    out: agent-core/src/proto
```

### Linting Rules

```bash
# Run lint
buf lint

# Common violations:
# - ENUM_ZERO_VALUE_SUFFIX: Enum zero value must end with _UNSPECIFIED
# - FIELD_LOWER_SNAKE_CASE: Field names must be lower_snake_case
# - PACKAGE_DEFINED: Every .proto must define a package
# - PACKAGE_DIRECTORY_MATCH: Package must match directory structure
# - RPC_REQUEST_STANDARD_NAME: Request message should be {Method}Request
```

**Fix Example:**

```protobuf
// WRONG
enum Status {
    UNKNOWN = 0;  // Should be STATUS_UNSPECIFIED
    ACTIVE = 1;
}

// CORRECT
enum Status {
    STATUS_UNSPECIFIED = 0;
    STATUS_ACTIVE = 1;
    STATUS_COMPLETED = 2;
}
```

### Breaking Change Detection

```bash
# Compare against main branch
buf breaking --against '.git#branch=main'

# Breaking changes buf catches:
# - Field number changes
# - Field type changes
# - Service/method removal
# - Message/field removal
# - Enum value removal
```

### buf build and buf push

```bash
# Build (compile and validate)
buf build

# Generate code
buf generate

# Push to Buf Schema Registry (optional)
buf push --tag v1.0.0
```

## Rust Tonic Patterns

### Server Implementation

```rust
use tonic::{transport::Server, Request, Response, Status};
use agent::agent_service_server::{AgentService, AgentServiceServer};

pub struct AgentServiceImpl {
    decision_engine: Arc<DecisionEngine>,
    rag_client: Arc<RagClient>,
}

#[tonic::async_trait]
impl AgentService for AgentServiceImpl {
    async fn get_action(
        &self,
        request: Request<GetActionRequest>,
    ) -> Result<Response<GetActionResponse>, Status> {
        let state = request.into_inner()
            .state
            .ok_or_else(|| Status::invalid_argument("missing game state"))?;

        // Decision latency must be < 100ms (P99)
        let start = std::time::Instant::now();

        let action = self.decision_engine
            .decide(&state.into())
            .await
            .map_err(|e| Status::internal(format!("decision failed: {e}")))?;

        let latency_us = start.elapsed().as_micros() as i64;

        if latency_us > 100_000 {
            tracing::warn!("decision latency exceeded 100ms: {}us", latency_us);
        }

        Ok(Response::new(GetActionResponse {
            action: Some(action.into()),
            confidence: 0.85,
            latency_us,
        }))
    }
}
```

### Client Creation and Connection Management

```rust
use agent::agent_service_client::AgentServiceClient;
use tonic::transport::{Channel, Endpoint};

pub struct AgentClient {
    client: AgentServiceClient<Channel>,
}

impl AgentClient {
    pub async fn connect(addr: &str) -> Result<Self, Box<dyn std::error::Error>> {
        let channel = Endpoint::from_shared(addr.to_string())?
            .connect_timeout(Duration::from_secs(5))
            .timeout(Duration::from_millis(200))  // Per-request timeout
            .tcp_keepalive(Some(Duration::from_secs(30)))
            .http2_keep_alive_interval(Duration::from_secs(30))
            .keep_alive_while_idle(true)
            .connect()
            .await?;

        Ok(Self {
            client: AgentServiceClient::new(channel)
                .max_decoding_message_size(10 * 1024 * 1024)  // 10MB for screen buffers
                .max_encoding_message_size(2 * 1024 * 1024),   // 2MB
        })
    }

    pub async fn get_action(&mut self, state: GameState) -> Result<Action, Status> {
        let request = GetActionRequest {
            state: Some(state.into()),
        };

        let response = self.client
            .get_action(request)
            .await?;

        response.into_inner()
            .action
            .ok_or_else(|| Status::internal("empty action response"))
    }
}
```

### Interceptors for Logging and Auth

```rust
use tonic::service::Interceptor;

#[derive(Clone)]
pub struct LoggingInterceptor;

impl Interceptor for LoggingInterceptor {
    fn call(&mut self, mut req: tonic::Request<()>) -> Result<tonic::Request<()>, Status> {
        let path = req.uri().path().to_string();
        tracing::info!("gRPC request: {}", path);

        req.extensions_mut().insert(RequestStart(Instant::now()));
        Ok(req)
    }
}

// Use interceptor
Server::builder()
    .layer(tower::ServiceBuilder::new()
        .layer(tonic::service::interceptor(LoggingInterceptor)))
    .add_service(AgentServiceServer::new(service))
    .serve(addr)
    .await?;
```

### Streaming: Response with tokio mpsc Channel

```rust
use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;

type ObserveStream = ReceiverStream<Result<AgentObservation, Status>>;

#[tonic::async_trait]
impl AgentService for AgentServiceImpl {
    type ObserveAgentStream = ObserveStream;

    async fn observe_agent(
        &self,
        request: Request<ObserveAgentRequest>,
    ) -> Result<Response<Self::ObserveAgentStream>, Status> {
        let agent_id = request.into_inner().agent_id;
        let (tx, rx) = mpsc::channel(128);

        let engine = self.decision_engine.clone();
        tokio::spawn(async move {
            let mut observer = engine.observe(&agent_id).await;

            while let Some(obs) = observer.next().await {
                if tx.send(Ok(obs.into())).await.is_err() {
                    // Client disconnected
                    break;
                }
            }
        });

        Ok(Response::new(ReceiverStream::new(rx)))
    }
}
```

### Error Mapping to tonic::Status

```rust
use thiserror::Error;

#[derive(Debug, Error)]
pub enum AgentCoreError {
    #[error("decision timeout after {ms}ms")]
    DecisionTimeout { ms: u64 },

    #[error("invalid game state: {reason}")]
    InvalidGameState { reason: String },

    #[error("RAG query failed: {0}")]
    RagQueryFailed(String),

    #[error("agent not found: {agent_id}")]
    AgentNotFound { agent_id: String },
}

impl From<AgentCoreError> for tonic::Status {
    fn from(err: AgentCoreError) -> Self {
        match err {
            AgentCoreError::DecisionTimeout { .. } =>
                Status::deadline_exceeded(err.to_string()),

            AgentCoreError::InvalidGameState { .. } =>
                Status::invalid_argument(err.to_string()),

            AgentCoreError::RagQueryFailed(msg) =>
                Status::unavailable(format!("RAG service: {}", msg)),

            AgentCoreError::AgentNotFound { .. } =>
                Status::not_found(err.to_string()),

            _ => Status::internal(err.to_string()),
        }
    }
}
```

### Health Checking (tonic-health crate)

```rust
use tonic_health::server::health_reporter;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "[::]:50052".parse()?;

    let (mut health_reporter, health_service) = health_reporter();

    // Set serving status
    health_reporter
        .set_serving::<AgentServiceServer<AgentServiceImpl>>()
        .await;

    let agent_service = AgentServiceImpl::new().await?;

    Server::builder()
        .add_service(health_service)
        .add_service(AgentServiceServer::new(agent_service))
        .serve(addr)
        .await?;

    Ok(())
}
```

### Reflection for grpcurl Compatibility

```rust
use tonic_reflection::server::Builder as ReflectionBuilder;

let reflection_service = ReflectionBuilder::configure()
    .register_encoded_file_descriptor_set(agent::FILE_DESCRIPTOR_SET)
    .build()?;

Server::builder()
    .add_service(reflection_service)
    .add_service(AgentServiceServer::new(service))
    .serve(addr)
    .await?;
```

Test with grpcurl:

```bash
grpcurl -plaintext localhost:50052 list
grpcurl -plaintext localhost:50052 list claudoom.agent.v1.AgentService
grpcurl -plaintext -d '{"agent_id": "agent-A"}' \
    localhost:50052 \
    claudoom.agent.v1.AgentService/ObserveAgent
```

### Graceful Shutdown

```rust
use tokio::signal;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let (tx, rx) = tokio::sync::oneshot::channel::<()>();

    tokio::spawn(async move {
        signal::ctrl_c().await.expect("failed to listen for ctrl-c");
        tracing::info!("received shutdown signal");
        let _ = tx.send(());
    });

    Server::builder()
        .add_service(AgentServiceServer::new(service))
        .serve_with_shutdown(addr, async {
            rx.await.ok();
        })
        .await?;

    tracing::info!("server gracefully stopped");
    Ok(())
}
```

## Go grpc-go Patterns

### Server Setup

```go
package main

import (
    "context"
    "log"
    "net"

    pb "github.com/clau-doom/orchestrator/pkg/proto/orchestrator/v1"
    "google.golang.org/grpc"
    "google.golang.org/grpc/health"
    healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

type orchestratorServer struct {
    pb.UnimplementedOrchestratorServiceServer
    orch *Orchestrator
}

func (s *orchestratorServer) StartExperiment(
    ctx context.Context,
    req *pb.StartExperimentRequest,
) (*pb.StartExperimentResponse, error) {
    expID, err := s.orch.StartExperiment(ctx, req.GetConfig())
    if err != nil {
        return nil, status.Errorf(codes.Internal, "start experiment: %v", err)
    }

    return &pb.StartExperimentResponse{
        ExperimentId: expID,
    }, nil
}

func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("failed to listen: %v", err)
    }

    grpcServer := grpc.NewServer(
        grpc.MaxRecvMsgSize(10*1024*1024), // 10MB
        grpc.MaxSendMsgSize(10*1024*1024),
    )

    // Register services
    pb.RegisterOrchestratorServiceServer(grpcServer, &orchestratorServer{
        orch: NewOrchestrator(),
    })

    // Register health service
    healthServer := health.NewServer()
    healthpb.RegisterHealthServer(grpcServer, healthServer)
    healthServer.SetServingStatus(
        "claudoom.orchestrator.v1.OrchestratorService",
        healthpb.HealthCheckResponse_SERVING,
    )

    log.Printf("Orchestrator gRPC server listening on :50051")
    if err := grpcServer.Serve(lis); err != nil {
        log.Fatalf("failed to serve: %v", err)
    }
}
```

### Client Connection

```go
import (
    "context"
    "time"

    pb "github.com/clau-doom/orchestrator/pkg/proto/agent/v1"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    grpc_retry "github.com/grpc-ecosystem/go-grpc-middleware/retry"
)

type AgentClient struct {
    conn   *grpc.ClientConn
    client pb.AgentServiceClient
}

func NewAgentClient(addr string) (*AgentClient, error) {
    conn, err := grpc.NewClient(
        addr,
        grpc.WithTransportCredentials(insecure.NewCredentials()),
        grpc.WithDefaultCallOptions(
            grpc.MaxCallRecvMsgSize(10*1024*1024),
        ),
        grpc.WithUnaryInterceptor(
            grpc_retry.UnaryClientInterceptor(
                grpc_retry.WithMax(3),
                grpc_retry.WithBackoff(grpc_retry.BackoffLinear(100*time.Millisecond)),
                grpc_retry.WithCodes(codes.Unavailable, codes.DeadlineExceeded),
            ),
        ),
    )
    if err != nil {
        return nil, fmt.Errorf("dial agent at %s: %w", addr, err)
    }

    return &AgentClient{
        conn:   conn,
        client: pb.NewAgentServiceClient(conn),
    }, nil
}

func (c *AgentClient) Close() error {
    return c.conn.Close()
}
```

### Interceptors (Unary, Stream)

```go
import (
    "context"
    "time"

    "go.uber.org/zap"
    "google.golang.org/grpc"
)

func loggingUnaryInterceptor(logger *zap.Logger) grpc.UnaryServerInterceptor {
    return func(
        ctx context.Context,
        req interface{},
        info *grpc.UnaryServerInfo,
        handler grpc.UnaryHandler,
    ) (interface{}, error) {
        start := time.Now()
        resp, err := handler(ctx, req)
        duration := time.Since(start)

        level := zap.InfoLevel
        if err != nil {
            level = zap.ErrorLevel
        }

        logger.Log(level, "gRPC call",
            zap.String("method", info.FullMethod),
            zap.Duration("duration", duration),
            zap.Error(err),
        )

        return resp, err
    }
}

func loggingStreamInterceptor(logger *zap.Logger) grpc.StreamServerInterceptor {
    return func(
        srv interface{},
        ss grpc.ServerStream,
        info *grpc.StreamServerInfo,
        handler grpc.StreamHandler,
    ) error {
        start := time.Now()
        err := handler(srv, ss)
        duration := time.Since(start)

        logger.Info("gRPC stream",
            zap.String("method", info.FullMethod),
            zap.Duration("duration", duration),
            zap.Error(err),
        )

        return err
    }
}

// Use interceptors
grpcServer := grpc.NewServer(
    grpc.ChainUnaryInterceptor(
        loggingUnaryInterceptor(logger),
        // Add more interceptors here
    ),
    grpc.ChainStreamInterceptor(
        loggingStreamInterceptor(logger),
    ),
)
```

### Server-Side Streaming Implementation

```go
func (s *orchestratorServer) StreamEvents(
    req *pb.StreamEventsRequest,
    stream pb.OrchestratorService_StreamEventsServer,
) error {
    expID := req.GetExperimentId()

    // Subscribe to experiment events
    eventCh := s.orch.Subscribe(expID)
    defer s.orch.Unsubscribe(expID, eventCh)

    for {
        select {
        case event, ok := <-eventCh:
            if !ok {
                return nil  // Channel closed, experiment complete
            }

            if err := stream.Send(eventToProto(event)); err != nil {
                return status.Errorf(codes.Internal, "send event: %v", err)
            }

        case <-stream.Context().Done():
            return stream.Context().Err()
        }
    }
}
```

### Bidirectional Streaming for Live Sessions

```go
func (c *AgentClient) LiveSession(ctx context.Context) error {
    stream, err := c.client.LiveSession(ctx)
    if err != nil {
        return fmt.Errorf("open live session: %w", err)
    }

    // Send goroutine
    go func() {
        for {
            select {
            case state := <-c.stateCh:
                if err := stream.Send(&pb.OrchestratorMessage{
                    Payload: &pb.OrchestratorMessage_State{State: state},
                }); err != nil {
                    return
                }
            case <-ctx.Done():
                stream.CloseSend()
                return
            }
        }
    }()

    // Receive loop
    for {
        msg, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return fmt.Errorf("recv from agent: %w", err)
        }

        switch payload := msg.Payload.(type) {
        case *pb.AgentMessage_Action:
            c.actionCh <- payload.Action
        case *pb.AgentMessage_Metrics:
            c.metricsCh <- payload.Metrics
        }
    }
}
```

### Error Handling with status.Errorf

```go
import (
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"
)

func (s *orchestratorServer) GetExperimentStatus(
    ctx context.Context,
    req *pb.GetExperimentStatusRequest,
) (*pb.GetExperimentStatusResponse, error) {
    expID := req.GetExperimentId()

    exp, err := s.orch.GetExperiment(expID)
    if errors.Is(err, ErrExperimentNotFound) {
        return nil, status.Errorf(codes.NotFound, "experiment %s not found", expID)
    }
    if err != nil {
        return nil, status.Errorf(codes.Internal, "get experiment: %v", err)
    }

    if exp.Status == ExperimentStatusRunning && exp.ResourcesExhausted {
        return nil, status.Errorf(codes.ResourceExhausted, "experiment at capacity")
    }

    return &pb.GetExperimentStatusResponse{
        Status: exp.Status,
        Generation: exp.CurrentGeneration,
    }, nil
}
```

### Health Checking (grpc_health_v1)

```go
import (
    "google.golang.org/grpc/health"
    healthpb "google.golang.org/grpc/health/grpc_health_v1"
)

healthServer := health.NewServer()
healthpb.RegisterHealthServer(grpcServer, healthServer)

// Set service status
healthServer.SetServingStatus(
    "claudoom.orchestrator.v1.OrchestratorService",
    healthpb.HealthCheckResponse_SERVING,
)

// Update status dynamically
if orchestratorOverloaded {
    healthServer.SetServingStatus(
        "claudoom.orchestrator.v1.OrchestratorService",
        healthpb.HealthCheckResponse_NOT_SERVING,
    )
}
```

### Graceful Stop with Signal Handling

```go
import (
    "os"
    "os/signal"
    "syscall"
)

func main() {
    grpcServer := grpc.NewServer()
    pb.RegisterOrchestratorServiceServer(grpcServer, &orchestratorServer{})

    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatalf("listen: %v", err)
    }

    // Handle shutdown signals
    sigCh := make(chan os.Signal, 1)
    signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)

    go func() {
        <-sigCh
        log.Println("received shutdown signal, stopping gracefully...")
        grpcServer.GracefulStop()
    }()

    log.Println("starting gRPC server on :50051")
    if err := grpcServer.Serve(lis); err != nil {
        log.Fatalf("serve: %v", err)
    }
}
```

## clau-doom Service Definitions

### AgentService

```protobuf
service AgentService {
    // Unary: Request single action (< 100ms latency target)
    rpc GetAction(GetActionRequest) returns (GetActionResponse);

    // Server streaming: Observe agent behavior over time
    rpc ObserveAgent(ObserveAgentRequest) returns (stream AgentObservation);

    // Bidirectional: Live game session (real-time interaction)
    rpc LiveSession(stream AgentMessage) returns (stream OrchestratorMessage);
}
```

### OrchestratorService

```protobuf
service OrchestratorService {
    // Start new DOE experiment
    rpc StartExperiment(StartExperimentRequest) returns (StartExperimentResponse);

    // Get experiment status
    rpc GetExperimentStatus(GetExperimentStatusRequest) returns (GetExperimentStatusResponse);

    // Server streaming: Subscribe to experiment events
    rpc StreamEvents(StreamEventsRequest) returns (stream ExperimentEvent);

    // Control experiment lifecycle
    rpc PauseExperiment(PauseExperimentRequest) returns (PauseExperimentResponse);
    rpc ResumeExperiment(ResumeExperimentRequest) returns (ResumeExperimentResponse);
    rpc StopExperiment(StopExperimentRequest) returns (StopExperimentResponse);
}
```

### HealthService

```protobuf
// Standard gRPC health checking protocol
service Health {
    rpc Check(HealthCheckRequest) returns (HealthCheckResponse);
    rpc Watch(HealthCheckRequest) returns (stream HealthCheckResponse);
}
```

## Testing

### Go: bufconn for In-Process Testing

```go
import (
    "context"
    "testing"

    "google.golang.org/grpc"
    "google.golang.org/grpc/test/bufconn"
)

const bufSize = 1024 * 1024

func setupTestServer(t *testing.T) (*grpc.ClientConn, func()) {
    lis := bufconn.Listen(bufSize)

    grpcServer := grpc.NewServer()
    pb.RegisterOrchestratorServiceServer(grpcServer, &orchestratorServer{
        orch: NewMockOrchestrator(),
    })

    go func() {
        if err := grpcServer.Serve(lis); err != nil {
            t.Errorf("server exited with error: %v", err)
        }
    }()

    conn, err := grpc.NewClient(
        "passthrough://bufconn",
        grpc.WithContextDialer(func(context.Context, string) (net.Conn, error) {
            return lis.Dial()
        }),
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    if err != nil {
        t.Fatalf("dial bufconn: %v", err)
    }

    cleanup := func() {
        conn.Close()
        grpcServer.Stop()
        lis.Close()
    }

    return conn, cleanup
}

func TestStartExperiment(t *testing.T) {
    conn, cleanup := setupTestServer(t)
    defer cleanup()

    client := pb.NewOrchestratorServiceClient(conn)

    resp, err := client.StartExperiment(context.Background(), &pb.StartExperimentRequest{
        Config: &pb.ExperimentConfig{
            DesignType: "factorial",
            Factors: 3,
        },
    })

    if err != nil {
        t.Fatalf("start experiment: %v", err)
    }

    if resp.GetExperimentId() == "" {
        t.Error("expected non-empty experiment ID")
    }
}
```

### Rust: tonic Test Helpers

```rust
#[cfg(test)]
mod tests {
    use super::*;
    use tonic::transport::Server;

    #[tokio::test]
    async fn test_get_action() {
        let service = AgentServiceImpl::new_mock();
        let addr = "[::1]:0".parse().unwrap();

        let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
        let addr = listener.local_addr().unwrap();

        tokio::spawn(async move {
            Server::builder()
                .add_service(AgentServiceServer::new(service))
                .serve_with_incoming(tokio_stream::wrappers::TcpListenerStream::new(listener))
                .await
                .unwrap();
        });

        let mut client = AgentServiceClient::connect(format!("http://{}", addr))
            .await
            .unwrap();

        let response = client
            .get_action(GetActionRequest {
                state: Some(mock_game_state()),
            })
            .await
            .unwrap();

        assert!(response.into_inner().action.is_some());
    }
}
```

### grpcurl for Manual Testing

```bash
# List services
grpcurl -plaintext localhost:50052 list

# List methods
grpcurl -plaintext localhost:50052 list claudoom.agent.v1.AgentService

# Call GetAction
grpcurl -plaintext \
    -d '{"state": {"agent_id": "agent-A", "tick": 100, "health": 100.0}}' \
    localhost:50052 \
    claudoom.agent.v1.AgentService/GetAction

# Server streaming (ObserveAgent)
grpcurl -plaintext \
    -d '{"agent_id": "agent-A", "include_frames": false}' \
    localhost:50052 \
    claudoom.agent.v1.AgentService/ObserveAgent

# Health check
grpcurl -plaintext \
    -d '{"service": "claudoom.agent.v1.AgentService"}' \
    localhost:50052 \
    grpc.health.v1.Health/Check
```

### Load Testing with ghz

```bash
# Install ghz
go install github.com/bojand/ghz/cmd/ghz@latest

# Load test GetAction
ghz --insecure \
    --proto api/proto/agent/v1/agent.proto \
    --call claudoom.agent.v1.AgentService/GetAction \
    -d '{"state": {"agent_id": "agent-A", "tick": 100, "health": 100.0}}' \
    -c 10 \
    -n 1000 \
    localhost:50052

# Expected output:
# Summary:
#   Count:        1000
#   Total:        2.15 s
#   Slowest:      25.3 ms
#   Fastest:      1.2 ms
#   Average:      8.5 ms
#   Requests/sec: 465
```

## Performance

### Connection Pooling

```rust
// Rust: tonic uses HTTP/2 multiplexing (single connection)
let channel = Endpoint::from_shared("http://localhost:50052")?
    .connect()
    .await?;

// Multiple concurrent requests on same channel
let mut client = AgentServiceClient::new(channel.clone());
```

```go
// Go: grpc-go also uses HTTP/2 multiplexing
conn, err := grpc.NewClient("localhost:50052")
client := pb.NewAgentServiceClient(conn)

// Multiple goroutines can use the same client concurrently
```

### Keepalive Configuration

```rust
// Rust tonic keepalive
let channel = Endpoint::from_shared("http://localhost:50052")?
    .tcp_keepalive(Some(Duration::from_secs(30)))
    .http2_keep_alive_interval(Duration::from_secs(30))
    .keep_alive_while_idle(true)
    .connect()
    .await?;
```

```go
// Go grpc-go keepalive
conn, err := grpc.NewClient(
    "localhost:50052",
    grpc.WithKeepaliveParams(keepalive.ClientParameters{
        Time:                30 * time.Second,
        Timeout:             10 * time.Second,
        PermitWithoutStream: true,
    }),
)
```

### Max Message Size Tuning

```rust
// Rust: set max message size
let client = AgentServiceClient::new(channel)
    .max_decoding_message_size(10 * 1024 * 1024)  // 10MB
    .max_encoding_message_size(2 * 1024 * 1024);   // 2MB
```

```go
// Go: set max message size
grpcServer := grpc.NewServer(
    grpc.MaxRecvMsgSize(10*1024*1024),
    grpc.MaxSendMsgSize(10*1024*1024),
)
```

### Compression (gzip)

```rust
// Rust: enable compression
use tonic::codec::CompressionEncoding;

let client = AgentServiceClient::new(channel)
    .send_compressed(CompressionEncoding::Gzip)
    .accept_compressed(CompressionEncoding::Gzip);
```

```go
// Go: enable compression
import "google.golang.org/grpc/encoding/gzip"

conn, err := grpc.NewClient(
    "localhost:50052",
    grpc.WithDefaultCallOptions(grpc.UseCompressor(gzip.Name)),
)
```

**When to Use Compression:**

- Large message payloads (> 1KB)
- Screen buffers (RGB24 frames)
- Batch operations

**When NOT to Use:**

- Small messages (< 1KB overhead > savings)
- Low-latency requirements (compression adds latency)
- Already compressed data (images, protobuf is already efficient)
