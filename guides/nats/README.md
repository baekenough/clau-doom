# NATS Reference Guide

Reference documentation for NATS messaging in the clau-doom distributed agent system.

## Key Resources

- [NATS Documentation](https://docs.nats.io/)
- [NATS by Example](https://natsbyexample.com/)
- [JetStream Documentation](https://docs.nats.io/nats-concepts/jetstream)
- [nats.go (Go client)](https://github.com/nats-io/nats.go)
- [async-nats (Rust client)](https://github.com/nats-io/nats.rs)
- [NATS CLI](https://github.com/nats-io/natscli)

## clau-doom Context

NATS serves as the pub/sub messaging backbone connecting:
- **Orchestrator (Go)**: Experiment lifecycle management, generation evolution
- **Agents (Rust)**: Decision engines running episodes, sending metrics
- **Dashboard (Next.js)**: Real-time spectation via WebSocket bridge
- **Analytics**: Offline data processing, experiment retrospection

### Message Flow Architecture

```
Dashboard (WebSocket)
        │
        ↓
Orchestrator (Go) ←─ NATS Core ─→ Analytics Pipeline
        │              │
        │         JetStream
        │         (persistence)
        │              │
        └──────────────┴─────→ Agents (Rust)
                               doom-agent-A
                               doom-agent-B
                               doom-agent-C
```

### Communication Patterns

| Pattern | Transport | Use Case |
|---------|-----------|----------|
| Agent events | NATS Core | Real-time dashboard updates (action, observe, death) |
| Experiment logs | JetStream | Durable storage for replay and analytics |
| Metrics | JetStream | Time-series agent performance data |
| Control commands | NATS Core | Orchestrator → Agent commands (pause, reset, config) |

## Subject Hierarchy Design

NATS subject hierarchy follows the convention: `clau-doom.{domain}.{action}.{id}`

### Agent Events

```
clau-doom.agent.{agent_id}.action        # Action taken by agent
clau-doom.agent.{agent_id}.observe       # Observation received
clau-doom.agent.{agent_id}.score         # Episode score computed
clau-doom.agent.{agent_id}.death         # Agent died
clau-doom.agent.{agent_id}.ragquery      # RAG query executed
clau-doom.agent.{agent_id}.error         # Error occurred
```

**Example messages:**
```json
// clau-doom.agent.doom-agent-A.action
{
  "agent_id": "doom-agent-A",
  "generation": 5,
  "episode": 42,
  "tick": 1280,
  "action": "ATTACK",
  "confidence": 0.85,
  "latency_us": 87000
}

// clau-doom.agent.doom-agent-B.death
{
  "agent_id": "doom-agent-B",
  "generation": 5,
  "episode": 43,
  "tick": 2345,
  "survival_time_s": 195.0,
  "kills": 12,
  "cause": "IMP_FIREBALL"
}
```

### Experiment Events

```
clau-doom.experiment.{exp_id}.start      # Experiment started
clau-doom.experiment.{exp_id}.run        # Run within experiment started
clau-doom.experiment.{exp_id}.complete   # Experiment completed
clau-doom.experiment.{exp_id}.error      # Experiment error
```

**Example:**
```json
// clau-doom.experiment.DOE-042.start
{
  "experiment_id": "DOE-042",
  "design_type": "2x3_factorial",
  "factors": {
    "memory": [0.5, 0.7, 0.9],
    "strength": [0.3, 0.5]
  },
  "runs": 6,
  "episodes_per_run": 30,
  "seed_set": [42, 1337, 2023, ...]
}
```

### Generation Events

```
clau-doom.generation.{gen_id}.start      # Generation started
clau-doom.generation.{gen_id}.evaluate   # Agent evaluation in generation
clau-doom.generation.{gen_id}.evolve     # Evolution algorithm running
clau-doom.generation.{gen_id}.complete   # Generation completed
```

**Example:**
```json
// clau-doom.generation.gen-05.complete
{
  "generation_id": 5,
  "experiment_id": "DOE-042",
  "population_size": 50,
  "best_fitness": 0.87,
  "avg_fitness": 0.64,
  "mutations": 12,
  "crossovers": 25,
  "duration_s": 3600
}
```

### Metrics

```
clau-doom.metrics.agent.{agent_id}       # Agent-specific metrics
clau-doom.metrics.generation.{gen_id}    # Generation-level metrics
clau-doom.metrics.experiment.{exp_id}    # Experiment-level metrics
clau-doom.metrics.system.{service}       # System health metrics
```

**Example:**
```json
// clau-doom.metrics.agent.doom-agent-A
{
  "agent_id": "doom-agent-A",
  "timestamp": "2026-02-07T10:30:00Z",
  "kills": 42,
  "deaths": 3,
  "health_avg": 65.0,
  "ammo_efficiency": 0.78,
  "decision_latency_p99_us": 95000,
  "rag_queries": 1200
}
```

### System Events

```
clau-doom.system.orchestrator.ready      # Orchestrator ready
clau-doom.system.orchestrator.shutdown   # Graceful shutdown
clau-doom.system.agent.{agent_id}.ready  # Agent ready
clau-doom.system.vizdoom.health          # VizDoom container health
clau-doom.system.opensearch.health       # OpenSearch health
clau-doom.system.mongodb.health          # MongoDB health
```

### Control Commands

```
clau-doom.control.experiment.pause       # Pause experiment
clau-doom.control.experiment.resume      # Resume experiment
clau-doom.control.agent.{agent_id}.reset # Reset specific agent
clau-doom.control.agent.*.config         # Config update (wildcard)
```

## Core NATS (Pub/Sub)

### Go Client (nats.go)

#### Connect

```go
import "github.com/nats-io/nats.go"

func ConnectNATS(url string) (*nats.Conn, error) {
    nc, err := nats.Connect(url,
        nats.Name("clau-doom-orchestrator"),
        nats.MaxReconnects(-1),
        nats.ReconnectWait(time.Second),
        nats.DisconnectErrHandler(func(_ *nats.Conn, err error) {
            log.Printf("NATS disconnected: %v", err)
        }),
        nats.ReconnectHandler(func(nc *nats.Conn) {
            log.Printf("NATS reconnected to %s", nc.ConnectedUrl())
        }),
    )
    if err != nil {
        return nil, fmt.Errorf("connect to NATS at %s: %w", url, err)
    }

    log.Printf("Connected to NATS at %s", nc.ConnectedUrl())
    return nc, nil
}
```

#### Publish

```go
// Simple publish (fire and forget)
func (o *Orchestrator) PublishAgentDeath(agentID string, death AgentDeath) error {
    subject := fmt.Sprintf("clau-doom.agent.%s.death", agentID)
    data, err := json.Marshal(death)
    if err != nil {
        return fmt.Errorf("marshal death: %w", err)
    }

    if err := o.nc.Publish(subject, data); err != nil {
        return fmt.Errorf("publish to %s: %w", subject, err)
    }

    return nil
}

// Publish with flush (ensure delivered before returning)
func (o *Orchestrator) PublishExperimentStart(exp Experiment) error {
    subject := fmt.Sprintf("clau-doom.experiment.%s.start", exp.ID)
    data, err := json.Marshal(exp)
    if err != nil {
        return fmt.Errorf("marshal experiment: %w", err)
    }

    if err := o.nc.Publish(subject, data); err != nil {
        return fmt.Errorf("publish to %s: %w", subject, err)
    }

    // Wait for server acknowledgment
    if err := o.nc.Flush(); err != nil {
        return fmt.Errorf("flush: %w", err)
    }

    return nil
}
```

#### Subscribe

```go
// Simple subscription
func (o *Orchestrator) SubscribeToAgentEvents(agentID string) error {
    subject := fmt.Sprintf("clau-doom.agent.%s.>", agentID)

    sub, err := o.nc.Subscribe(subject, func(msg *nats.Msg) {
        log.Printf("Agent event: %s - %s", msg.Subject, string(msg.Data))
        o.handleAgentEvent(msg.Subject, msg.Data)
    })
    if err != nil {
        return fmt.Errorf("subscribe to %s: %w", subject, err)
    }

    o.subscriptions[agentID] = sub
    return nil
}

// Queue subscription (load balancing across multiple orchestrators)
func (o *Orchestrator) SubscribeToControlCommands() error {
    _, err := o.nc.QueueSubscribe(
        "clau-doom.control.>",
        "orchestrators", // Queue group
        func(msg *nats.Msg) {
            o.handleControlCommand(msg.Subject, msg.Data)
        },
    )
    return err
}
```

#### Drain and Cleanup

```go
func (o *Orchestrator) Shutdown() error {
    // Drain all subscriptions (process in-flight messages)
    for agentID, sub := range o.subscriptions {
        if err := sub.Drain(); err != nil {
            log.Printf("drain subscription for %s: %v", agentID, err)
        }
    }

    // Drain connection (flush outbound messages)
    if err := o.nc.Drain(); err != nil {
        return fmt.Errorf("drain connection: %w", err)
    }

    return nil
}
```

### Rust Client (async-nats)

#### Connect

```rust
use async_nats;
use tokio;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = async_nats::connect("nats://localhost:4222").await?;
    tracing::info!("Connected to NATS at {}", client.connection_state());

    Ok(())
}

// With options
async fn connect_with_options() -> Result<async_nats::Client, async_nats::ConnectError> {
    let client = async_nats::ConnectOptions::new()
        .name("doom-agent-A")
        .max_reconnects(None) // Infinite reconnects
        .reconnect_delay_callback(|attempts| {
            std::cmp::min(std::time::Duration::from_secs(attempts as u64),
                          std::time::Duration::from_secs(8))
        })
        .disconnect_callback(|| {
            tracing::warn!("NATS disconnected");
        })
        .reconnect_callback(|| {
            tracing::info!("NATS reconnected");
        })
        .connect("nats://localhost:4222")
        .await?;

    Ok(client)
}
```

#### Publish

```rust
use async_nats;
use serde_json;

pub struct AgentPublisher {
    client: async_nats::Client,
    agent_id: String,
}

impl AgentPublisher {
    pub async fn publish_action(&self, action: &Action, tick: u32) -> Result<()> {
        let subject = format!("clau-doom.agent.{}.action", self.agent_id);
        let payload = serde_json::to_vec(&ActionEvent {
            agent_id: self.agent_id.clone(),
            tick,
            action: action.clone(),
            confidence: 0.85,
        })?;

        self.client.publish(subject, payload.into()).await?;
        Ok(())
    }

    pub async fn publish_death(&self, death: &DeathEvent) -> Result<()> {
        let subject = format!("clau-doom.agent.{}.death", self.agent_id);
        let payload = serde_json::to_vec(death)?;

        self.client.publish(subject, payload.into()).await?;
        self.client.flush().await?; // Ensure delivery
        Ok(())
    }
}
```

#### Subscribe

```rust
use async_nats::Subscriber;
use futures::StreamExt;

pub async fn subscribe_to_control_commands(
    client: &async_nats::Client,
    agent_id: &str,
) -> Result<()> {
    let subject = format!("clau-doom.control.agent.{}", agent_id);
    let mut subscriber = client.subscribe(subject.clone()).await?;

    tracing::info!("Subscribed to {}", subject);

    tokio::spawn(async move {
        while let Some(msg) = subscriber.next().await {
            match handle_control_command(&msg.payload).await {
                Ok(_) => tracing::info!("Handled control command"),
                Err(e) => tracing::error!("Failed to handle command: {}", e),
            }
        }
    });

    Ok(())
}

async fn handle_control_command(payload: &[u8]) -> Result<()> {
    let cmd: ControlCommand = serde_json::from_slice(payload)?;
    match cmd {
        ControlCommand::Reset => reset_agent().await,
        ControlCommand::UpdateConfig(config) => update_config(config).await,
        ControlCommand::Pause => pause_agent().await,
    }
}
```

### Request-Reply Pattern

Useful for synchronous queries where a response is needed.

#### Go Client (Request)

```go
// Request agent status with timeout
func (o *Orchestrator) GetAgentStatus(agentID string) (*AgentStatus, error) {
    subject := fmt.Sprintf("clau-doom.agent.%s.status", agentID)

    msg, err := o.nc.Request(subject, nil, 2*time.Second)
    if err != nil {
        return nil, fmt.Errorf("request agent status: %w", err)
    }

    var status AgentStatus
    if err := json.Unmarshal(msg.Data, &status); err != nil {
        return nil, fmt.Errorf("unmarshal status: %w", err)
    }

    return &status, nil
}
```

#### Rust Client (Reply)

```rust
pub async fn handle_status_requests(client: &async_nats::Client) -> Result<()> {
    let mut subscriber = client.subscribe("clau-doom.agent.*.status").await?;

    tokio::spawn(async move {
        while let Some(msg) = subscriber.next().await {
            let status = get_current_status().await;
            let payload = serde_json::to_vec(&status).unwrap();

            if let Some(reply_to) = msg.reply {
                let _ = client.publish(reply_to, payload.into()).await;
            }
        }
    });

    Ok(())
}
```

### Wildcard Subscriptions

| Wildcard | Matches | Example |
|----------|---------|---------|
| `*` | Single token | `clau-doom.agent.*.action` matches `clau-doom.agent.doom-agent-A.action` |
| `>` | One or more tokens | `clau-doom.agent.>` matches all agent subjects |

```go
// Subscribe to all agent deaths
nc.Subscribe("clau-doom.agent.*.death", func(msg *nats.Msg) {
    handleAgentDeath(msg.Data)
})

// Subscribe to all experiment events
nc.Subscribe("clau-doom.experiment.>", func(msg *nats.Msg) {
    handleExperimentEvent(msg.Subject, msg.Data)
})
```

## JetStream (Persistence)

JetStream adds persistence, delivery guarantees, and replay capabilities on top of core NATS.

### Stream Configuration

```go
import "github.com/nats-io/nats.go"

func CreateStreams(nc *nats.Conn) error {
    js, err := nc.JetStream()
    if err != nil {
        return fmt.Errorf("init JetStream: %w", err)
    }

    // AGENT_EVENTS stream
    _, err = js.AddStream(&nats.StreamConfig{
        Name:        "AGENT_EVENTS",
        Subjects:    []string{"clau-doom.agent.>"},
        Storage:     nats.FileStorage,
        Retention:   nats.LimitsPolicy,
        MaxAge:      7 * 24 * time.Hour, // 7 days
        MaxBytes:    100 * 1024 * 1024 * 1024, // 100 GB
        Replicas:    1,
        Description: "Agent action, observation, and death events",
    })
    if err != nil {
        return fmt.Errorf("create AGENT_EVENTS stream: %w", err)
    }

    // EXPERIMENT_EVENTS stream
    _, err = js.AddStream(&nats.StreamConfig{
        Name:        "EXPERIMENT_EVENTS",
        Subjects:    []string{"clau-doom.experiment.>", "clau-doom.generation.>"},
        Storage:     nats.FileStorage,
        Retention:   nats.InterestPolicy, // Delete after all consumers ack
        MaxAge:      30 * 24 * time.Hour, // 30 days
        Replicas:    1,
        Description: "Experiment and generation lifecycle events",
    })
    if err != nil {
        return fmt.Errorf("create EXPERIMENT_EVENTS stream: %w", err)
    }

    // METRICS stream
    _, err = js.AddStream(&nats.StreamConfig{
        Name:        "METRICS",
        Subjects:    []string{"clau-doom.metrics.>"},
        Storage:     nats.FileStorage,
        Retention:   nats.LimitsPolicy,
        MaxAge:      14 * 24 * time.Hour, // 14 days
        Replicas:    1,
        Description: "Agent and system performance metrics",
    })
    if err != nil {
        return fmt.Errorf("create METRICS stream: %w", err)
    }

    return nil
}
```

### Consumer Types

#### Push Consumer

Server pushes messages to the consumer.

```go
// Push consumer for real-time dashboard updates
func (b *WebSocketBridge) StartPushConsumer(expID string) error {
    js, _ := b.nc.JetStream()

    subject := fmt.Sprintf("clau-doom.experiment.%s.>", expID)

    _, err := js.Subscribe(subject, func(msg *nats.Msg) {
        // Forward to WebSocket clients
        b.broadcastToClients(msg.Subject, msg.Data)
        msg.Ack()
    },
        nats.DeliverNew(),
        nats.ManualAck(),
    )

    return err
}
```

#### Pull Consumer

Consumer pulls messages on demand (better for batch processing).

```go
// Pull consumer for analytics processing
func (a *AnalyticsProcessor) StartPullConsumer() error {
    js, _ := a.nc.JetStream()

    // Create durable consumer
    _, err := js.AddConsumer("AGENT_EVENTS", &nats.ConsumerConfig{
        Durable:       "analytics-processor",
        FilterSubject: "clau-doom.agent.*.death",
        AckPolicy:     nats.AckExplicitPolicy,
        AckWait:       30 * time.Second,
        MaxDeliver:    3,
    })
    if err != nil {
        return fmt.Errorf("create consumer: %w", err)
    }

    sub, err := js.PullSubscribe("clau-doom.agent.*.death", "analytics-processor")
    if err != nil {
        return fmt.Errorf("pull subscribe: %w", err)
    }

    go func() {
        for {
            msgs, err := sub.Fetch(10, nats.MaxWait(5*time.Second))
            if err != nil {
                if err == nats.ErrTimeout {
                    continue
                }
                log.Printf("fetch error: %v", err)
                continue
            }

            for _, msg := range msgs {
                if err := a.processDeathEvent(msg.Data); err != nil {
                    log.Printf("process death: %v", err)
                    msg.Nak()
                } else {
                    msg.Ack()
                }
            }
        }
    }()

    return nil
}
```

### Durable Consumers

Durable consumers track their progress, allowing resume after restart.

```go
func CreateDurableConsumer(js nats.JetStreamContext, stream, consumerName string) error {
    _, err := js.AddConsumer(stream, &nats.ConsumerConfig{
        Durable:        consumerName,
        FilterSubject:  "clau-doom.experiment.*.complete",
        AckPolicy:      nats.AckExplicitPolicy,
        AckWait:        60 * time.Second,
        MaxDeliver:     5,
        DeliverPolicy:  nats.DeliverAllPolicy, // Replay all messages on first start
        ReplayPolicy:   nats.ReplayInstantPolicy,
    })
    return err
}
```

### Consumer Acknowledgment

| Ack Type | Meaning | Use Case |
|----------|---------|----------|
| `Ack()` | Success, delete message | Message processed successfully |
| `Nak()` | Failure, redeliver immediately | Temporary failure, retry now |
| `NakWithDelay(d)` | Failure, redeliver after delay | Rate limit, backoff |
| `InProgress()` | Still processing, extend ack wait | Long-running processing |
| `Term()` | Permanent failure, do not redeliver | Invalid message, skip |

```go
_, err := js.Subscribe("clau-doom.experiment.*.complete", func(msg *nats.Msg) {
    var exp ExperimentComplete
    if err := json.Unmarshal(msg.Data, &exp); err != nil {
        log.Printf("invalid message: %v", err)
        msg.Term() // Poison message, do not retry
        return
    }

    if err := analytics.ProcessExperiment(exp); err != nil {
        if errors.Is(err, ErrRateLimited) {
            msg.NakWithDelay(10 * time.Second) // Backoff
        } else {
            msg.Nak() // Retry immediately
        }
        return
    }

    msg.Ack() // Success
},
    nats.Durable("analytics-processor"),
    nats.ManualAck(),
    nats.AckWait(30*time.Second),
)
```

### Replay Policies

| Policy | Behavior | Use Case |
|--------|----------|----------|
| `ReplayInstantPolicy` | Deliver as fast as possible | Real-time processing |
| `ReplayOriginalPolicy` | Deliver at original publish rate | Time-sensitive replay |

## Dead Letter Handling

### Max Deliveries Configuration

```go
_, err := js.AddConsumer("AGENT_EVENTS", &nats.ConsumerConfig{
    Durable:       "death-processor",
    FilterSubject: "clau-doom.agent.*.death",
    AckPolicy:     nats.AckExplicitPolicy,
    MaxDeliver:    3, // Attempt delivery 3 times
    AckWait:       30 * time.Second,
})
```

### Dead Letter Subject Pattern

When a message exceeds `MaxDeliver`, manually move to dead letter queue:

```go
func (p *Processor) handleMessage(msg *nats.Msg) {
    meta, err := msg.Metadata()
    if err != nil {
        log.Printf("get metadata: %v", err)
        return
    }

    if meta.NumDelivered >= 3 {
        // Move to dead letter queue
        subject := "clau-doom.dlq.agent.death"
        if err := p.nc.Publish(subject, msg.Data); err != nil {
            log.Printf("publish to DLQ: %v", err)
        }
        msg.Term() // Permanent failure
        return
    }

    // Process normally
    if err := p.process(msg.Data); err != nil {
        msg.Nak()
    } else {
        msg.Ack()
    }
}
```

### Monitoring Unprocessed Messages

```bash
# Check consumer lag
nats consumer info AGENT_EVENTS analytics-processor

# Output shows:
# Num Pending: 1234 messages
# Num Redelivered: 56 messages
```

## Go nats.go Advanced Patterns

### Structured Message Encoding

```go
// JSON encoding
type GenerationComplete struct {
    GenerationID int     `json:"generation_id"`
    BestFitness  float64 `json:"best_fitness"`
    Duration     int     `json:"duration_s"`
}

func (o *Orchestrator) PublishGenerationComplete(gen GenerationComplete) error {
    subject := fmt.Sprintf("clau-doom.generation.gen-%02d.complete", gen.GenerationID)
    data, err := json.Marshal(gen)
    if err != nil {
        return err
    }

    return o.js.Publish(subject, data)
}

// Protobuf encoding (more efficient)
import pb "github.com/clau-doom/orchestrator/pkg/proto/events"

func (o *Orchestrator) PublishAgentAction(action *pb.AgentAction) error {
    subject := fmt.Sprintf("clau-doom.agent.%s.action", action.AgentId)
    data, err := proto.Marshal(action)
    if err != nil {
        return err
    }

    return o.js.Publish(subject, data)
}
```

### Connection Options

```go
nc, err := nats.Connect("nats://localhost:4222",
    nats.Name("clau-doom-orchestrator"),
    nats.MaxReconnects(-1), // Infinite reconnects
    nats.ReconnectWait(time.Second),
    nats.ReconnectBufSize(8*1024*1024), // 8MB buffer
    nats.DisconnectErrHandler(func(_ *nats.Conn, err error) {
        log.Printf("NATS disconnected: %v", err)
    }),
    nats.ReconnectHandler(func(nc *nats.Conn) {
        log.Printf("NATS reconnected to %s", nc.ConnectedUrl())
    }),
    nats.ClosedHandler(func(_ *nats.Conn) {
        log.Printf("NATS connection closed")
    }),
    nats.ErrorHandler(func(_ *nats.Conn, _ *nats.Subscription, err error) {
        log.Printf("NATS error: %v", err)
    }),
)
```

### Error Handlers and Disconnect Callbacks

```go
type OrchestratorNATS struct {
    nc          *nats.Conn
    connected   atomic.Bool
    reconnectCh chan struct{}
}

func NewOrchestratorNATS(url string) (*OrchestratorNATS, error) {
    o := &OrchestratorNATS{
        reconnectCh: make(chan struct{}, 1),
    }
    o.connected.Store(false)

    nc, err := nats.Connect(url,
        nats.DisconnectErrHandler(func(_ *nats.Conn, err error) {
            o.connected.Store(false)
            log.Printf("NATS disconnected: %v", err)
        }),
        nats.ReconnectHandler(func(nc *nats.Conn) {
            o.connected.Store(true)
            log.Printf("NATS reconnected")
            select {
            case o.reconnectCh <- struct{}{}:
            default:
            }
        }),
    )
    if err != nil {
        return nil, err
    }

    o.nc = nc
    o.connected.Store(true)
    return o, nil
}
```

### Graceful Drain on Shutdown

```go
func (o *Orchestrator) Shutdown(ctx context.Context) error {
    log.Println("Draining NATS subscriptions...")

    // Drain all subscriptions
    for _, sub := range o.subscriptions {
        if err := sub.Drain(); err != nil {
            log.Printf("drain subscription: %v", err)
        }
    }

    // Drain connection (flush pending publishes)
    done := make(chan struct{})
    go func() {
        if err := o.nc.Drain(); err != nil {
            log.Printf("drain connection: %v", err)
        }
        close(done)
    }()

    select {
    case <-done:
        log.Println("NATS drained successfully")
        return nil
    case <-ctx.Done():
        o.nc.Close() // Force close
        return ctx.Err()
    }
}
```

## Rust async-nats Patterns

### Tokio Integration

```rust
use async_nats;
use tokio;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let client = async_nats::connect("nats://localhost:4222").await?;

    // Spawn subscriber task
    let sub_handle = tokio::spawn(async move {
        let mut subscriber = client.subscribe("clau-doom.agent.*.action").await?;
        while let Some(msg) = subscriber.next().await {
            process_message(msg).await;
        }
        Ok::<_, async_nats::Error>(())
    });

    // Spawn publisher task
    let pub_handle = tokio::spawn(async move {
        loop {
            let action = generate_action().await;
            client.publish("clau-doom.agent.doom-agent-A.action", action.into()).await?;
            tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;
        }
    });

    tokio::try_join!(sub_handle, pub_handle)?;
    Ok(())
}
```

### Publish with Headers

```rust
use async_nats::HeaderMap;

pub async fn publish_with_metadata(
    client: &async_nats::Client,
    subject: String,
    payload: Vec<u8>,
) -> Result<()> {
    let mut headers = HeaderMap::new();
    headers.insert("agent-id", "doom-agent-A");
    headers.insert("generation", "5");
    headers.insert("experiment", "DOE-042");

    client.publish_with_headers(subject, headers, payload.into()).await?;
    Ok(())
}
```

### Subscribe with Message Processing Loops

```rust
use futures::StreamExt;

pub async fn subscribe_and_process(client: &async_nats::Client) -> Result<()> {
    let mut subscriber = client.subscribe("clau-doom.agent.>".to_string()).await?;

    while let Some(msg) = subscriber.next().await {
        let subject = &msg.subject;
        let payload = &msg.payload;

        match parse_event(subject, payload) {
            Ok(event) => {
                if let Err(e) = handle_event(event).await {
                    tracing::error!("handle event: {}", e);
                }
            }
            Err(e) => {
                tracing::warn!("parse event: {}", e);
            }
        }
    }

    Ok(())
}
```

### Connection Resilience

```rust
use async_nats::{ConnectOptions, ServerAddr};
use std::time::Duration;

pub async fn connect_resilient() -> Result<async_nats::Client> {
    let client = ConnectOptions::new()
        .name("doom-agent-A")
        .max_reconnects(None) // Infinite
        .reconnect_delay_callback(|attempts| {
            let delay = std::cmp::min(
                Duration::from_secs(2u64.pow(attempts as u32)),
                Duration::from_secs(60),
            );
            tracing::info!("Reconnect attempt {} in {:?}", attempts, delay);
            delay
        })
        .disconnect_callback(|| {
            tracing::warn!("NATS disconnected, will reconnect");
        })
        .reconnect_callback(|| {
            tracing::info!("NATS reconnected successfully");
        })
        .connect("nats://localhost:4222")
        .await?;

    Ok(client)
}
```

## Monitoring & Operations

### NATS Monitoring Endpoint

```bash
# Access monitoring HTTP endpoint (default: localhost:8222)
curl http://localhost:8222/varz    # Server variables
curl http://localhost:8222/connz   # Connection info
curl http://localhost:8222/subsz   # Subscription info
curl http://localhost:8222/routez  # Route info
curl http://localhost:8222/jsz     # JetStream info
```

### NATS CLI Tool Usage

```bash
# Publish message
nats pub clau-doom.agent.doom-agent-A.action '{"action":"ATTACK","confidence":0.85}'

# Subscribe to subject
nats sub "clau-doom.agent.>"

# Stream operations
nats stream ls                                    # List streams
nats stream info AGENT_EVENTS                     # Stream details
nats stream view AGENT_EVENTS                     # View messages

# Consumer operations
nats consumer ls AGENT_EVENTS                     # List consumers
nats consumer info AGENT_EVENTS analytics-processor  # Consumer details
nats consumer next AGENT_EVENTS analytics-processor 10  # Pull 10 messages

# Message inspection
nats stream get AGENT_EVENTS 1234                 # Get specific message by seq
```

### Docker Health Check for NATS

```yaml
# docker-compose.yml
services:
  nats:
    image: nats:2.10
    command: ["--jetstream", "--http_port", "8222"]
    ports:
      - "4222:4222"  # Client connections
      - "8222:8222"  # Monitoring
    healthcheck:
      test: ["CMD", "wget", "--spider", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
```

### Metrics to Track

| Metric | Source | Alert Threshold | Meaning |
|--------|--------|----------------|---------|
| `msg/sec` | `/varz` | > 10,000 | Message throughput |
| `pending` | `/subsz` | > 1,000 per sub | Consumer lag |
| `redeliveries` | Consumer info | > 100 | Processing failures |
| `slow_consumers` | `/varz` | > 0 | Consumers not keeping up |
| `reconnects` | Client logs | > 10/hour | Connection instability |
| `stream_bytes` | `/jsz` | > 80% max | Storage approaching limit |

```go
// Example: Prometheus exporter for NATS metrics
import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/nats-io/nats.go"
)

var (
    natsMessagesPublished = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "clau_doom_nats_messages_published_total",
            Help: "Total NATS messages published",
        },
        []string{"subject"},
    )

    natsConsumerLag = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "clau_doom_nats_consumer_lag",
            Help: "NATS consumer pending messages",
        },
        []string{"stream", "consumer"},
    )
)

func collectMetrics(js nats.JetStreamContext) {
    ticker := time.NewTicker(15 * time.Second)
    for range ticker.C {
        consumers, _ := js.Consumers("AGENT_EVENTS")
        for consumer := range consumers {
            info, _ := js.ConsumerInfo("AGENT_EVENTS", consumer.Name)
            natsConsumerLag.WithLabelValues("AGENT_EVENTS", consumer.Name).
                Set(float64(info.NumPending))
        }
    }
}
```

## Best Practices Summary

1. **Subject Hierarchy**: Use consistent naming (`clau-doom.{domain}.{action}.{id}`)
2. **Durability**: Use JetStream for events that need replay or persistence
3. **Consumer Types**: Push for real-time, pull for batch processing
4. **Acknowledgment**: Always use manual ack for JetStream consumers
5. **Error Handling**: Set `MaxDeliver` and handle dead letters
6. **Graceful Shutdown**: Always drain subscriptions and connections
7. **Monitoring**: Track consumer lag, redeliveries, and connection health
8. **Wildcards**: Use `*` for single level, `>` for multi-level subscriptions
9. **Reconnection**: Configure infinite reconnects with exponential backoff
10. **Message Size**: Keep messages small (<1MB), use references for large data
