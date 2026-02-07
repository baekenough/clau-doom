---
name: grpc-best-practices
description: gRPC and messaging patterns for Rust tonic and Go grpc-go services with NATS pub/sub and bidirectional streaming
user-invocable: false
---

# gRPC Best Practices for clau-doom Services

## Proto File Design

### Service Definitions

```protobuf
// api/proto/agent/v1/agent.proto
syntax = "proto3";
package claudoom.agent.v1;

option go_package = "github.com/clau-doom/orchestrator/pkg/proto/agent/v1";

service AgentService {
    // Unary: request single action from agent
    rpc GetAction(GetActionRequest) returns (GetActionResponse);

    // Server streaming: observe agent behavior over time
    rpc ObserveAgent(ObserveAgentRequest) returns (stream AgentObservation);

    // Client streaming: send batch of game states for evaluation
    rpc BatchEvaluate(stream GameState) returns (BatchEvaluateResponse);

    // Bidirectional: real-time agent-orchestrator communication
    rpc LiveSession(stream AgentMessage) returns (stream OrchestratorMessage);
}
```

### Message Types

```protobuf
// api/proto/agent/v1/messages.proto
syntax = "proto3";
package claudoom.agent.v1;

import "google/protobuf/timestamp.proto";

message GameState {
    string agent_id = 1;
    int32 generation_id = 2;
    int32 tick = 3;

    // Observation data
    bytes screen_buffer = 4;  // RGB24 frame
    int32 screen_width = 5;
    int32 screen_height = 6;

    // Game variables
    float health = 7;
    int32 ammo = 8;
    int32 kill_count = 9;
    int32 death_count = 10;

    // Position
    float pos_x = 11;
    float pos_y = 12;
    float angle = 13;

    google.protobuf.Timestamp timestamp = 14;
}

message Action {
    int32 action_id = 1;
    repeated bool buttons = 2;  // Button state vector

    enum ActionType {
        ACTION_TYPE_UNSPECIFIED = 0;
        ACTION_TYPE_MOVE_FORWARD = 1;
        ACTION_TYPE_MOVE_BACKWARD = 2;
        ACTION_TYPE_TURN_LEFT = 3;
        ACTION_TYPE_TURN_RIGHT = 4;
        ACTION_TYPE_ATTACK = 5;
        ACTION_TYPE_USE = 6;
    }
    ActionType type = 3;
}

message AgentScore {
    string agent_id = 1;
    int32 generation_id = 2;
    string experiment_id = 3;

    int32 kills = 4;
    int32 deaths = 5;
    float health_remaining = 6;
    float ammo_efficiency = 7;
    float exploration_coverage = 8;
    double fitness_score = 9;

    // DOE factors
    string rag_strategy = 10;
    double mutation_rate = 11;

    google.protobuf.Timestamp evaluated_at = 12;
}

message GetActionRequest {
    GameState state = 1;
}

message GetActionResponse {
    Action action = 1;
    float confidence = 2;
    int64 latency_us = 3;  // Decision latency in microseconds
}

message ObserveAgentRequest {
    string agent_id = 1;
    bool include_frames = 2;
}

message AgentObservation {
    GameState state = 1;
    Action action_taken = 2;
    float reward = 3;
}

message BatchEvaluateResponse {
    repeated AgentScore scores = 1;
    int64 total_time_ms = 2;
}
```

### Bidirectional Streaming Messages

```protobuf
message AgentMessage {
    oneof payload {
        Action action = 1;
        AgentStatus status = 2;
        AgentMetrics metrics = 3;
    }
}

message OrchestratorMessage {
    oneof payload {
        GameState state = 1;
        EpisodeControl control = 2;
        ConfigUpdate config = 3;
    }
}

message EpisodeControl {
    enum Command {
        COMMAND_UNSPECIFIED = 0;
        COMMAND_START = 1;
        COMMAND_PAUSE = 2;
        COMMAND_RESUME = 3;
        COMMAND_STOP = 4;
        COMMAND_RESET = 5;
    }
    Command command = 1;
    string reason = 2;
}
```

## Rust Tonic Implementation

### Server

```rust
use tonic::{transport::Server, Request, Response, Status};
use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;

pub struct AgentServiceImpl {
    decision_engine: Arc<DecisionEngine>,
}

#[tonic::async_trait]
impl AgentService for AgentServiceImpl {
    async fn get_action(
        &self,
        request: Request<GetActionRequest>,
    ) -> Result<Response<GetActionResponse>, Status> {
        let state = request.into_inner().state
            .ok_or_else(|| Status::invalid_argument("missing game state"))?;

        let start = std::time::Instant::now();
        let action = self.decision_engine
            .decide(&state.into())
            .await
            .map_err(|e| Status::internal(format!("decision failed: {e}")))?;

        let latency_us = start.elapsed().as_micros() as i64;

        Ok(Response::new(GetActionResponse {
            action: Some(action.into()),
            confidence: 0.85,
            latency_us,
        }))
    }

    type ObserveAgentStream = ReceiverStream<Result<AgentObservation, Status>>;

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
                    break;
                }
            }
        });

        Ok(Response::new(ReceiverStream::new(rx)))
    }

    type LiveSessionStream = ReceiverStream<Result<OrchestratorMessage, Status>>;

    async fn live_session(
        &self,
        request: Request<tonic::Streaming<AgentMessage>>,
    ) -> Result<Response<Self::LiveSessionStream>, Status> {
        let mut inbound = request.into_inner();
        let (tx, rx) = mpsc::channel(128);

        let engine = self.decision_engine.clone();
        tokio::spawn(async move {
            while let Some(msg) = inbound.message().await.unwrap_or(None) {
                match msg.payload {
                    Some(agent_message::Payload::Action(action)) => {
                        // Process action, send next state
                        let next_state = engine.step(action.into()).await;
                        let _ = tx.send(Ok(OrchestratorMessage {
                            payload: Some(orchestrator_message::Payload::State(next_state.into())),
                        })).await;
                    }
                    _ => {}
                }
            }
        });

        Ok(Response::new(ReceiverStream::new(rx)))
    }
}
```

### Tonic Server Startup

```rust
#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::init();

    let addr = "[::]:50052".parse()?;
    let service = AgentServiceImpl {
        decision_engine: Arc::new(DecisionEngine::new().await?),
    };

    let (mut health_reporter, health_service) = tonic_health::server::health_reporter();
    health_reporter
        .set_serving::<AgentServiceServer<AgentServiceImpl>>()
        .await;

    tracing::info!("Agent gRPC server listening on {}", addr);

    Server::builder()
        .add_service(health_service)
        .add_service(AgentServiceServer::new(service))
        .serve(addr)
        .await?;

    Ok(())
}
```

### Tonic Client

```rust
use agent::agent_service_client::AgentServiceClient;

pub struct AgentClient {
    client: AgentServiceClient<tonic::transport::Channel>,
}

impl AgentClient {
    pub async fn connect(endpoint: &str) -> Result<Self> {
        let channel = tonic::transport::Channel::from_shared(endpoint.to_string())?
            .connect_timeout(Duration::from_secs(5))
            .timeout(Duration::from_millis(200))
            .connect()
            .await?;

        Ok(Self {
            client: AgentServiceClient::new(channel),
        })
    }

    pub async fn get_action(&mut self, state: GameState) -> Result<Action> {
        let request = GetActionRequest {
            state: Some(state.into()),
        };

        let response = self.client
            .get_action(request)
            .await
            .map_err(|s| AgentCoreError::GrpcError(s.to_string()))?;

        response.into_inner().action
            .ok_or(AgentCoreError::EmptyResponse)
            .map(Into::into)
    }
}
```

## Go grpc-go Implementation

### Server

```go
type orchestratorServer struct {
    pb.UnimplementedOrchestratorServiceServer
    orch *Orchestrator
}

func (s *orchestratorServer) StreamEvents(
    req *pb.StreamEventsRequest,
    stream pb.OrchestratorService_StreamEventsServer,
) error {
    expID := req.GetExperimentId()
    ch := s.orch.Subscribe(expID)
    defer s.orch.Unsubscribe(expID, ch)

    for {
        select {
        case event, ok := <-ch:
            if !ok {
                return nil
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

### Go gRPC Client (calling Rust agent)

```go
func NewAgentClient(addr string) (*AgentClient, error) {
    conn, err := grpc.NewClient(addr,
        grpc.WithTransportCredentials(insecure.NewCredentials()),
        grpc.WithDefaultCallOptions(
            grpc.MaxCallRecvMsgSize(10*1024*1024), // 10MB for screen buffers
        ),
        grpc.WithUnaryInterceptor(grpc_retry.UnaryClientInterceptor(
            grpc_retry.WithMax(3),
            grpc_retry.WithBackoff(grpc_retry.BackoffLinear(100*time.Millisecond)),
        )),
    )
    if err != nil {
        return nil, fmt.Errorf("dial agent at %s: %w", addr, err)
    }

    return &AgentClient{
        conn:   conn,
        client: pb.NewAgentServiceClient(conn),
    }, nil
}

func (c *AgentClient) GetAction(ctx context.Context, state *pb.GameState) (*pb.Action, error) {
    ctx, cancel := context.WithTimeout(ctx, 200*time.Millisecond)
    defer cancel()

    resp, err := c.client.GetAction(ctx, &pb.GetActionRequest{State: state})
    if err != nil {
        return nil, fmt.Errorf("get action: %w", err)
    }
    return resp.GetAction(), nil
}
```

### Middleware (Interceptors)

```go
func loggingInterceptor(
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
```

## Bidirectional Streaming

### Agent-Orchestrator Live Session

```
Orchestrator (Go)                        Agent (Rust)
     |                                       |
     |-- GameState (initial) -->             |
     |                                       |
     |               <-- Action -------------|
     |                                       |
     |-- GameState (next) -->                |
     |                                       |
     |               <-- Action -------------|
     |               <-- Metrics ------------|
     |                                       |
     |-- EpisodeControl(STOP) -->            |
     |                                       |
```

### Go Client for Bidirectional Stream

```go
func (c *AgentClient) LiveSession(ctx context.Context) error {
    stream, err := c.client.LiveSession(ctx)
    if err != nil {
        return fmt.Errorf("open live session: %w", err)
    }

    // Send goroutine
    go func() {
        for state := range c.stateCh {
            if err := stream.Send(&pb.OrchestratorMessage{
                Payload: &pb.OrchestratorMessage_State{State: state},
            }); err != nil {
                return
            }
        }
        stream.CloseSend()
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

## NATS Pub/Sub

### Subject Hierarchy

```
clau-doom.                          # root
  experiment.                       # experiment events
    {exp_id}.                       # specific experiment
      started                       # experiment started
      completed                     # experiment completed
      generation.                   # generation events
        {gen_id}.                   # specific generation
          started                   # generation started
          completed                 # generation completed
          agent.                    # agent events
            {agent_id}.             # specific agent
              evaluated             # agent evaluation complete
              error                 # agent error
  metrics.                          # metrics stream
    agent.{agent_id}                # per-agent metrics
    generation.{gen_id}             # per-generation metrics
  control.                          # control commands
    pause                           # pause experiment
    resume                          # resume experiment
    shutdown                        # graceful shutdown
```

### NATS Publisher (Go)

```go
import "github.com/nats-io/nats.go"

type EventPublisher struct {
    nc *nats.Conn
    js nats.JetStreamContext
}

func NewEventPublisher(url string) (*EventPublisher, error) {
    nc, err := nats.Connect(url,
        nats.MaxReconnects(-1),
        nats.ReconnectWait(time.Second),
    )
    if err != nil {
        return nil, fmt.Errorf("connect to NATS: %w", err)
    }

    js, err := nc.JetStream()
    if err != nil {
        return nil, fmt.Errorf("init JetStream: %w", err)
    }

    // Create stream for experiment events
    _, err = js.AddStream(&nats.StreamConfig{
        Name:     "EXPERIMENTS",
        Subjects: []string{"clau-doom.experiment.>"},
        Storage:  nats.FileStorage,
        MaxAge:   24 * time.Hour,
    })
    if err != nil {
        return nil, fmt.Errorf("create stream: %w", err)
    }

    return &EventPublisher{nc: nc, js: js}, nil
}

func (p *EventPublisher) PublishGenerationComplete(
    expID string,
    genID int,
    summary *GenerationSummary,
) error {
    subject := fmt.Sprintf("clau-doom.experiment.%s.generation.%d.completed", expID, genID)
    data, err := json.Marshal(summary)
    if err != nil {
        return fmt.Errorf("marshal summary: %w", err)
    }

    _, err = p.js.Publish(subject, data)
    return err
}
```

### NATS Subscriber (Dashboard WebSocket Bridge)

```go
func (b *WebSocketBridge) subscribeToEvents(expID string) error {
    subject := fmt.Sprintf("clau-doom.experiment.%s.>", expID)

    sub, err := b.js.Subscribe(subject, func(msg *nats.Msg) {
        // Forward to all connected WebSocket clients
        b.broadcast(msg.Subject, msg.Data)
    }, nats.DeliverNew())

    if err != nil {
        return fmt.Errorf("subscribe to %s: %w", subject, err)
    }

    b.subscriptions = append(b.subscriptions, sub)
    return nil
}
```

### JetStream Persistence

```go
// Durable consumer for analytics processing
_, err := js.Subscribe(
    "clau-doom.experiment.*.generation.*.completed",
    func(msg *nats.Msg) {
        var summary GenerationSummary
        if err := json.Unmarshal(msg.Data, &summary); err != nil {
            msg.Nak()
            return
        }

        if err := analytics.ProcessGeneration(summary); err != nil {
            msg.NakWithDelay(5 * time.Second)
            return
        }

        msg.Ack()
    },
    nats.Durable("analytics-processor"),
    nats.ManualAck(),
    nats.AckWait(30*time.Second),
)
```

## Error Handling Across Services

### gRPC Status Codes

| Situation | Code | Example |
|-----------|------|---------|
| Invalid input | `INVALID_ARGUMENT` | Bad game state format |
| Agent not found | `NOT_FOUND` | Unknown agent ID |
| Decision timeout | `DEADLINE_EXCEEDED` | >100ms decision |
| Engine failure | `INTERNAL` | Scoring computation error |
| Experiment full | `RESOURCE_EXHAUSTED` | Generation at capacity |
| Not ready | `UNAVAILABLE` | Agent still initializing |

### Error Propagation

```rust
// Rust: convert domain errors to gRPC status
impl From<AgentCoreError> for tonic::Status {
    fn from(err: AgentCoreError) -> Self {
        match err {
            AgentCoreError::DecisionTimeout { .. } =>
                Status::deadline_exceeded(err.to_string()),
            AgentCoreError::InvalidGameState { .. } =>
                Status::invalid_argument(err.to_string()),
            AgentCoreError::RagQueryFailed(s) =>
                Status::unavailable(format!("RAG service: {s}")),
            _ => Status::internal(err.to_string()),
        }
    }
}
```

## Health Checking

### gRPC Health Protocol

```rust
// Rust: tonic-health
use tonic_health::server::health_reporter;

let (mut reporter, service) = health_reporter();
reporter.set_serving::<AgentServiceServer<AgentServiceImpl>>().await;

Server::builder()
    .add_service(service)
    .add_service(AgentServiceServer::new(agent_service))
    .serve(addr)
    .await?;
```

```go
// Go: grpc-health
import "google.golang.org/grpc/health"
import healthpb "google.golang.org/grpc/health/grpc_health_v1"

healthServer := health.NewServer()
healthpb.RegisterHealthServer(grpcServer, healthServer)
healthServer.SetServingStatus("claudoom.orchestrator.v1.OrchestratorService", healthpb.HealthCheckResponse_SERVING)
```

## Graceful Shutdown

```go
func (s *Server) GracefulShutdown(ctx context.Context) error {
    // Stop accepting new connections
    s.grpcServer.GracefulStop()

    // Drain NATS subscriptions
    for _, sub := range s.subscriptions {
        if err := sub.Drain(); err != nil {
            s.logger.Warn("drain subscription", zap.Error(err))
        }
    }

    // Close NATS connection
    s.natsConn.Close()

    // Wait for in-flight requests
    select {
    case <-ctx.Done():
        s.grpcServer.Stop() // Force stop
        return ctx.Err()
    case <-s.done:
        return nil
    }
}
```
