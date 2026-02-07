---
name: nats-best-practices
description: NATS messaging patterns for Rust async-nats and Go nats.go with JetStream persistence, subject hierarchy, consumer groups, and dead letter handling
user-invocable: false
---

# NATS Best Practices for clau-doom Messaging

## Overview

NATS provides the pub/sub messaging backbone for clau-doom, enabling real-time communication between:
- Orchestrator (Go) broadcasting experiment/generation events
- Agents (Rust) publishing action/observation events
- Dashboard (Next.js) subscribing to real-time updates
- Analytics services consuming historical data via JetStream

This skill covers subject hierarchy design, JetStream persistence, consumer patterns, and dead letter handling for both Rust (async-nats) and Go (nats.go).

## Subject Hierarchy Design

### Full Subject Tree for clau-doom

```
clau-doom.                                  # Root namespace
├── agent.                                  # Agent domain
│   ├── {agent_id}.                        # Specific agent instance
│   │   ├── action                         # Action taken by agent
│   │   ├── observe                        # Observation received
│   │   ├── score                          # Score computed
│   │   ├── death                          # Agent death event
│   │   └── health                         # Health check ping
├── experiment.                             # Experiment domain
│   ├── {experiment_id}.                   # Specific experiment
│   │   ├── start                          # Experiment started
│   │   ├── run.{run_id}                   # DOE run events
│   │   ├── complete                       # Experiment completed
│   │   └── error                          # Experiment error
├── generation.                             # Generation domain
│   ├── {generation_id}.                   # Specific generation
│   │   ├── start                          # Generation started
│   │   ├── evaluate                       # Evaluation phase
│   │   ├── evolve                         # Evolution phase
│   │   ├── complete                       # Generation completed
│   │   └── agent.{agent_id}.score         # Per-agent evaluation
├── metrics.                                # Metrics domain
│   ├── agent.                             # Agent metrics
│   │   └── {agent_id}.{metric_name}       # Per-agent metric
│   ├── generation.                        # Generation metrics
│   │   └── {generation_id}.{metric_name}  # Per-generation metric
│   └── system.                            # System metrics
│       └── {service}.{metric_name}        # Per-service metric
└── system.                                 # System domain
    ├── {service}.health                   # Service health checks
    ├── {service}.error                    # Service errors
    └── control.                           # Control commands
        ├── pause                          # Pause experiment
        ├── resume                         # Resume experiment
        └── shutdown                       # Graceful shutdown
```

### Naming Conventions

```yaml
pattern: clau-doom.{domain}.{entity}.{action}

rules:
  - Use lowercase with underscores
  - Keep subject tokens short (< 20 chars)
  - Avoid unbounded cardinality (no timestamp in subject)
  - Use wildcards for subscriptions (* single token, > multiple tokens)

examples:
  - clau-doom.agent.doom-agent-A.action
  - clau-doom.experiment.DOE-042.run.3
  - clau-doom.generation.gen-005.evaluate
  - clau-doom.metrics.agent.doom-agent-B.kill_rate
  - clau-doom.system.orchestrator.health
```

### Subject Examples by Use Case

```
# Real-time agent action stream (Dashboard)
Subscribe: clau-doom.agent.*.action

# All events for a specific experiment (Analytics)
Subscribe: clau-doom.experiment.DOE-042.>

# Generation completion events (Evolution Manager)
Subscribe: clau-doom.generation.*.complete

# Agent death events (Orchestrator)
Subscribe: clau-doom.agent.*.death

# System-wide health checks (Monitoring)
Subscribe: clau-doom.system.*.health
```

## JetStream Configuration

### Stream Definitions

#### AGENT_EVENTS Stream

```json
{
  "name": "AGENT_EVENTS",
  "subjects": ["clau-doom.agent.>"],
  "retention": "limits",
  "max_age": 604800000000000,
  "max_bytes": 1073741824,
  "max_msg_size": 1048576,
  "storage": "file",
  "num_replicas": 1,
  "discard": "old",
  "duplicate_window": 120000000000
}
```

Configuration explanation:
- `max_age`: 7 days (604800s = 7d × 24h × 3600s)
- `max_bytes`: 1GB total storage
- `max_msg_size`: 1MB per message
- `storage`: file (persistent across restarts)
- `discard`: old (FIFO when limits reached)
- `duplicate_window`: 2 minutes for deduplication

#### EXPERIMENT_EVENTS Stream

```json
{
  "name": "EXPERIMENT_EVENTS",
  "subjects": ["clau-doom.experiment.>"],
  "retention": "limits",
  "max_age": 2592000000000000,
  "storage": "file",
  "num_replicas": 1,
  "discard": "old"
}
```

Configuration:
- `max_age`: 30 days (retain experiment history longer)
- No `max_bytes` limit (experiments generate fewer events)

#### METRICS Stream

```json
{
  "name": "METRICS",
  "subjects": ["clau-doom.metrics.>"],
  "retention": "limits",
  "max_age": 86400000000000,
  "max_bytes": 536870912,
  "storage": "file",
  "discard": "old"
}
```

Configuration:
- `max_age`: 24 hours (metrics are high-frequency)
- `max_bytes`: 512MB
- `discard`: old (rolling window)

### Creating Streams in Go

```go
import "github.com/nats-io/nats.go"

func createStreams(js nats.JetStreamContext) error {
    // AGENT_EVENTS stream
    _, err := js.AddStream(&nats.StreamConfig{
        Name:     "AGENT_EVENTS",
        Subjects: []string{"clau-doom.agent.>"},
        Storage:  nats.FileStorage,
        MaxAge:   7 * 24 * time.Hour,
        MaxBytes: 1 * 1024 * 1024 * 1024, // 1GB
    })
    if err != nil {
        return fmt.Errorf("create AGENT_EVENTS stream: %w", err)
    }

    // EXPERIMENT_EVENTS stream
    _, err = js.AddStream(&nats.StreamConfig{
        Name:     "EXPERIMENT_EVENTS",
        Subjects: []string{"clau-doom.experiment.>"},
        Storage:  nats.FileStorage,
        MaxAge:   30 * 24 * time.Hour,
    })
    if err != nil {
        return fmt.Errorf("create EXPERIMENT_EVENTS stream: %w", err)
    }

    // METRICS stream
    _, err = js.AddStream(&nats.StreamConfig{
        Name:     "METRICS",
        Subjects: []string{"clau-doom.metrics.>"},
        Storage:  nats.FileStorage,
        MaxAge:   24 * time.Hour,
        MaxBytes: 512 * 1024 * 1024, // 512MB
        Discard:  nats.DiscardOld,
    })
    if err != nil {
        return fmt.Errorf("create METRICS stream: %w", err)
    }

    return nil
}
```

## Consumer Patterns

### Durable Push Consumer (Dashboard Real-time Updates)

```go
// Dashboard WebSocket bridge subscribes to all agent actions
func (b *DashboardBridge) subscribeAgentActions() error {
    _, err := b.js.Subscribe(
        "clau-doom.agent.*.action",
        func(msg *nats.Msg) {
            // Forward to all connected WebSocket clients
            b.broadcastToClients(msg.Data)
            msg.Ack() // Acknowledge immediately (best-effort delivery)
        },
        nats.Durable("dashboard-actions"), // Survives restarts
        nats.DeliverNew(),                // Only new messages
        nats.AckExplicit(),               // Manual acknowledgment
    )
    return err
}
```

### Pull Consumer (Analytics Batch Processing)

```go
// Analytics service pulls messages in batches for processing
func (a *AnalyticsService) processExperimentBatch(expID string) error {
    subject := fmt.Sprintf("clau-doom.experiment.%s.>", expID)

    // Create pull consumer
    sub, err := a.js.PullSubscribe(
        subject,
        "analytics-batch",
        nats.ManualAck(),
    )
    if err != nil {
        return fmt.Errorf("pull subscribe: %w", err)
    }

    // Fetch messages in batches
    for {
        msgs, err := sub.Fetch(100, nats.MaxWait(5*time.Second))
        if err == nats.ErrTimeout {
            break // No more messages
        }
        if err != nil {
            return fmt.Errorf("fetch messages: %w", err)
        }

        for _, msg := range msgs {
            if err := a.processMessage(msg); err != nil {
                msg.Nak() // Requeue on failure
                continue
            }
            msg.Ack()
        }
    }

    return nil
}
```

### Consumer Acknowledgment Patterns

```go
// Ack: Message processed successfully
msg.Ack()

// Nak: Failed, requeue for retry
msg.Nak()

// NakWithDelay: Failed, retry after delay (exponential backoff)
msg.NakWithDelay(5 * time.Second)

// InProgress: Processing ongoing, extend AckWait
msg.InProgress()

// Term: Permanent failure, don't retry (dead letter)
msg.Term()
```

### Filtered Consumer (Specific Agent Events)

```go
// Subscribe to events for a specific agent
func (m *Monitoring) monitorAgent(agentID string) error {
    subject := fmt.Sprintf("clau-doom.agent.%s.>", agentID)

    _, err := m.js.Subscribe(
        subject,
        func(msg *nats.Msg) {
            m.handleAgentEvent(agentID, msg)
            msg.Ack()
        },
        nats.Durable(fmt.Sprintf("monitor-%s", agentID)),
        nats.DeliverNew(),
    )
    return err
}
```

## Replay and Message Recovery

### Replay from Timestamp (Experiment Re-analysis)

```go
// Replay all events from a specific timestamp
func (a *AnalyticsService) replayExperiment(expID string, startTime time.Time) error {
    subject := fmt.Sprintf("clau-doom.experiment.%s.>", expID)

    sub, err := a.js.Subscribe(
        subject,
        func(msg *nats.Msg) {
            a.processMessage(msg)
            msg.Ack()
        },
        nats.Durable("replay-analytics"),
        nats.DeliverByStartTime(startTime), // Replay from timestamp
        nats.ReplayInstant(),               // Fast replay
    )
    if err != nil {
        return fmt.Errorf("replay subscribe: %w", err)
    }

    defer sub.Unsubscribe()
    return nil
}
```

### Deliver by Start Sequence (Missed Messages)

```go
// Resume from a specific sequence number
func (s *Service) resumeFromSequence(seq uint64) error {
    sub, err := s.js.Subscribe(
        "clau-doom.generation.*.complete",
        s.handleMessage,
        nats.Durable("generation-handler"),
        nats.DeliverByStartSequence(seq), // Resume from sequence
    )
    return err
}
```

## Go nats.go Patterns

### Connection Management

```go
import "github.com/nats-io/nats.go"

type NATSClient struct {
    nc *nats.Conn
    js nats.JetStreamContext
}

func NewNATSClient(url string) (*NATSClient, error) {
    nc, err := nats.Connect(url,
        nats.Name("clau-doom-orchestrator"),
        nats.MaxReconnects(-1),              // Infinite reconnects
        nats.ReconnectWait(time.Second),     // Wait between reconnects
        nats.ReconnectBufSize(8*1024*1024),  // 8MB buffer during disconnect
        nats.ErrorHandler(func(c *nats.Conn, s *nats.Subscription, err error) {
            log.Error("NATS error", zap.Error(err))
        }),
        nats.DisconnectErrHandler(func(c *nats.Conn, err error) {
            log.Warn("NATS disconnected", zap.Error(err))
        }),
        nats.ReconnectHandler(func(c *nats.Conn) {
            log.Info("NATS reconnected")
        }),
    )
    if err != nil {
        return nil, fmt.Errorf("connect to NATS: %w", err)
    }

    js, err := nc.JetStream(
        nats.PublishAsyncMaxPending(256), // Buffer for async publishes
    )
    if err != nil {
        return nil, fmt.Errorf("init JetStream: %w", err)
    }

    return &NATSClient{nc: nc, js: js}, nil
}

func (c *NATSClient) Close() {
    c.nc.Drain() // Graceful shutdown
}
```

### Publishing with Headers

```go
func (p *Publisher) PublishAgentAction(agentID string, action *Action) error {
    subject := fmt.Sprintf("clau-doom.agent.%s.action", agentID)

    data, err := json.Marshal(action)
    if err != nil {
        return fmt.Errorf("marshal action: %w", err)
    }

    msg := &nats.Msg{
        Subject: subject,
        Data:    data,
        Header: nats.Header{
            "trace-id":     []string{action.TraceID},
            "source-agent": []string{agentID},
            "timestamp":    []string{time.Now().UTC().Format(time.RFC3339Nano)},
        },
    }

    _, err = p.js.PublishMsg(msg)
    return err
}
```

### JetStream Publish with Ack Confirmation

```go
func (p *Publisher) PublishExperimentComplete(expID string, results *Results) error {
    subject := fmt.Sprintf("clau-doom.experiment.%s.complete", expID)

    data, err := json.Marshal(results)
    if err != nil {
        return fmt.Errorf("marshal results: %w", err)
    }

    // Synchronous publish (wait for ack)
    ack, err := p.js.Publish(subject, data)
    if err != nil {
        return fmt.Errorf("publish: %w", err)
    }

    log.Info("published experiment complete",
        zap.String("experiment_id", expID),
        zap.Uint64("stream_seq", ack.Sequence),
    )

    return nil
}
```

### QueueSubscribe for Load-Balanced Processing

```go
// Multiple workers subscribe to same subject with queue group
func (w *Worker) startWorkers(count int) error {
    for i := 0; i < count; i++ {
        _, err := w.nc.QueueSubscribe(
            "clau-doom.generation.*.evaluate",
            "eval-workers", // Queue group name
            func(msg *nats.Msg) {
                w.handleEvaluation(msg)
            },
        )
        if err != nil {
            return fmt.Errorf("start worker %d: %w", i, err)
        }
    }
    return nil
}
```

### Request-Reply Pattern (Agent Health Check)

```go
// Orchestrator requests agent health
func (o *Orchestrator) checkAgentHealth(agentID string) (*HealthStatus, error) {
    subject := fmt.Sprintf("clau-doom.agent.%s.health", agentID)

    msg, err := o.nc.Request(subject, nil, 2*time.Second)
    if err == nats.ErrTimeout {
        return nil, fmt.Errorf("agent %s did not respond", agentID)
    }
    if err != nil {
        return nil, fmt.Errorf("request health: %w", err)
    }

    var status HealthStatus
    if err := json.Unmarshal(msg.Data, &status); err != nil {
        return nil, fmt.Errorf("unmarshal health: %w", err)
    }

    return &status, nil
}

// Agent responds to health checks
func (a *Agent) handleHealthChecks() error {
    _, err := a.nc.Subscribe(
        fmt.Sprintf("clau-doom.agent.%s.health", a.id),
        func(msg *nats.Msg) {
            status := HealthStatus{
                AgentID: a.id,
                Healthy: a.isHealthy(),
                Uptime:  time.Since(a.startTime),
            }
            data, _ := json.Marshal(status)
            msg.Respond(data)
        },
    )
    return err
}
```

## Rust async-nats Patterns

### Connection Setup

```rust
use async_nats::{Client, ConnectOptions};
use tokio::time::Duration;

pub async fn connect_nats(url: &str) -> Result<Client> {
    let client = ConnectOptions::new()
        .name("clau-doom-agent")
        .max_reconnects(None) // Infinite
        .reconnect_delay_callback(|attempts| {
            let delay = std::cmp::min(attempts * 100, 5000);
            Duration::from_millis(delay as u64)
        })
        .connect(url)
        .await
        .map_err(|e| AgentError::NatsConnect(e.to_string()))?;

    tracing::info!("connected to NATS at {}", url);
    Ok(client)
}
```

### Publishing Agent Actions

```rust
use async_nats::HeaderMap;
use serde_json;

pub async fn publish_action(
    client: &Client,
    agent_id: &str,
    action: &Action,
) -> Result<()> {
    let subject = format!("clau-doom.agent.{}.action", agent_id);
    let data = serde_json::to_vec(action)?;

    let mut headers = HeaderMap::new();
    headers.insert("trace-id", action.trace_id.as_str());
    headers.insert("timestamp", chrono::Utc::now().to_rfc3339().as_str());

    client.publish_with_headers(subject, headers, data.into())
        .await
        .map_err(|e| AgentError::NatsPublish(e.to_string()))?;

    Ok(())
}
```

### JetStream Publishing

```rust
use async_nats::jetstream;

pub async fn publish_agent_score(
    js: &jetstream::Context,
    agent_id: &str,
    score: &AgentScore,
) -> Result<()> {
    let subject = format!("clau-doom.generation.{}.agent.{}.score",
                          score.generation_id, agent_id);
    let data = serde_json::to_vec(score)?;

    let ack = js.publish(subject, data.into())
        .await
        .map_err(|e| AgentError::JetStreamPublish(e.to_string()))?;

    tracing::debug!(
        "published agent score, stream_seq={}",
        ack.await?.sequence
    );

    Ok(())
}
```

### Subscribing and Processing

```rust
use tokio_stream::StreamExt;

pub async fn subscribe_control_commands(
    client: &Client,
    agent_id: &str,
) -> Result<()> {
    let subject = "clau-doom.system.control.>";
    let mut subscriber = client.subscribe(subject.to_string())
        .await
        .map_err(|e| AgentError::NatsSubscribe(e.to_string()))?;

    tracing::info!("subscribed to control commands");

    while let Some(msg) = subscriber.next().await {
        match msg.subject.as_str() {
            "clau-doom.system.control.pause" => {
                tracing::info!("pausing agent");
                // Handle pause
            }
            "clau-doom.system.control.resume" => {
                tracing::info!("resuming agent");
                // Handle resume
            }
            "clau-doom.system.control.shutdown" => {
                tracing::info!("shutting down agent");
                break;
            }
            _ => {}
        }
    }

    Ok(())
}
```

### Message Acknowledgment

```rust
use async_nats::jetstream;

pub async fn process_observations(
    js: &jetstream::Context,
    agent_id: &str,
) -> Result<()> {
    let subject = format!("clau-doom.agent.{}.observe", agent_id);

    let consumer = js.get_consumer_from_stream("AGENT_EVENTS", "agent-observer")
        .await?;

    let mut messages = consumer.messages().await?;

    while let Some(msg) = messages.next().await {
        let msg = msg?;

        match process_observation(&msg.payload).await {
            Ok(_) => {
                msg.ack().await?;
            }
            Err(e) if e.is_retriable() => {
                msg.ack_with(jetstream::AckKind::Nak(Some(Duration::from_secs(5))))
                    .await?;
            }
            Err(_) => {
                msg.ack_with(jetstream::AckKind::Term)
                    .await?;
            }
        }
    }

    Ok(())
}
```

### Graceful Shutdown with Drain

```rust
pub async fn shutdown_gracefully(client: Client) -> Result<()> {
    tracing::info!("draining NATS connection");

    client.drain()
        .await
        .map_err(|e| AgentError::NatsDrain(e.to_string()))?;

    tracing::info!("NATS connection drained");
    Ok(())
}
```

## Dead Letter Handling

### Max Deliveries Configuration

```go
// Create consumer with max delivery attempts
_, err := js.AddConsumer("AGENT_EVENTS", &nats.ConsumerConfig{
    Durable:       "action-processor",
    AckPolicy:     nats.AckExplicitPolicy,
    MaxDeliver:    5,  // Max 5 delivery attempts
    AckWait:       30 * time.Second,
    DeliverPolicy: nats.DeliverNewPolicy,
})
```

### Dead Letter Subject

```
Dead letter subjects follow pattern:
  clau-doom.deadletter.{original_subject}

Example:
  Original: clau-doom.agent.doom-agent-A.action
  DLQ:      clau-doom.deadletter.agent.doom-agent-A.action
```

### Dead Letter Consumer

```go
// Monitor dead letter queue for alerts
func (m *Monitoring) monitorDeadLetters() error {
    _, err := m.nc.Subscribe(
        "clau-doom.deadletter.>",
        func(msg *nats.Msg) {
            m.alertDeadLetter(msg)
        },
    )
    return err
}

func (m *Monitoring) alertDeadLetter(msg *nats.Msg) {
    log.Error("dead letter detected",
        zap.String("subject", msg.Subject),
        zap.Int("attempts", getDeliveryCount(msg)),
        zap.ByteString("payload", msg.Data),
    )

    // Send alert to monitoring system
    m.sendAlert(Alert{
        Level:   "error",
        Message: fmt.Sprintf("dead letter on %s", msg.Subject),
        Data:    string(msg.Data),
    })
}
```

### Retry Strategy with Exponential Backoff

```go
func (p *Processor) handleMessage(msg *nats.Msg) {
    attempts := getDeliveryCount(msg)

    if err := p.process(msg.Data); err != nil {
        if attempts >= 5 {
            // Max attempts reached, send to DLQ
            p.sendToDeadLetter(msg)
            msg.Term()
            return
        }

        // Exponential backoff: 1s, 2s, 4s, 8s, 16s
        delay := time.Duration(1<<uint(attempts-1)) * time.Second
        msg.NakWithDelay(delay)
        return
    }

    msg.Ack()
}

func getDeliveryCount(msg *nats.Msg) int {
    meta, _ := msg.Metadata()
    return int(meta.NumDelivered)
}
```

### Monitoring Unprocessed Messages

```go
// Check for messages stuck in consumers
func (m *Monitoring) checkConsumerLag() error {
    info, err := m.js.ConsumerInfo("AGENT_EVENTS", "action-processor")
    if err != nil {
        return fmt.Errorf("get consumer info: %w", err)
    }

    lag := info.NumPending + info.NumAckPending

    if lag > 10000 {
        m.alertHighLag("action-processor", lag)
    }

    return nil
}
```

## Message Schemas

### AgentActionEvent

```json
{
  "agent_id": "doom-agent-A",
  "episode_id": "ep-12345",
  "action": {
    "action_id": 3,
    "buttons": [true, false, false, true, false],
    "action_type": "ATTACK"
  },
  "timestamp": "2024-12-15T10:30:00.123456Z"
}
```

### ExperimentEvent

```json
{
  "experiment_id": "DOE-042",
  "phase": "execution",
  "status": "in_progress",
  "metadata": {
    "run_id": 3,
    "factors": {
      "memory": 0.7,
      "strength": 0.5
    },
    "episodes_completed": 15,
    "episodes_total": 30
  },
  "timestamp": "2024-12-15T10:30:00Z"
}
```

### MetricEvent

```json
{
  "agent_id": "doom-agent-A",
  "metric_name": "kill_rate",
  "value": 42.5,
  "timestamp": "2024-12-15T10:30:00Z"
}
```

### Standard Envelope

```json
{
  "type": "agent.action",
  "version": "1.0",
  "payload": {
    "agent_id": "doom-agent-A",
    "action": "..."
  },
  "trace_id": "trace-abc-123",
  "timestamp": "2024-12-15T10:30:00.123456Z"
}
```

## Monitoring and Operations

### NATS Server Monitoring Endpoint

```bash
# Access monitoring endpoint
curl http://localhost:8222/varz     # Server info
curl http://localhost:8222/connz    # Connections
curl http://localhost:8222/routez   # Routes
curl http://localhost:8222/subsz    # Subscriptions
curl http://localhost:8222/jsz      # JetStream info
```

### nats CLI Commands for Debugging

```bash
# List streams
nats stream ls

# Stream info
nats stream info AGENT_EVENTS

# List consumers
nats consumer ls AGENT_EVENTS

# Consumer info
nats consumer info AGENT_EVENTS action-processor

# Publish test message
nats pub clau-doom.agent.test.action '{"agent_id":"test"}'

# Subscribe to subject
nats sub 'clau-doom.agent.*.action'

# View messages in stream
nats stream view AGENT_EVENTS

# Purge stream
nats stream purge AGENT_EVENTS --force
```

### Consumer Lag Monitoring

```go
func (m *Metrics) recordConsumerLag(streamName, consumerName string) error {
    info, err := m.js.ConsumerInfo(streamName, consumerName)
    if err != nil {
        return err
    }

    lag := info.NumPending + info.NumAckPending

    m.gauges["consumer_lag"].With(prometheus.Labels{
        "stream":   streamName,
        "consumer": consumerName,
    }).Set(float64(lag))

    return nil
}
```

### Subject Message Rate Tracking

```go
func (m *Metrics) trackPublishRate(subject string) {
    m.counters["messages_published"].With(prometheus.Labels{
        "subject": subject,
    }).Inc()
}
```

### Docker Health Check for NATS

```dockerfile
# docker-compose.yml
services:
  nats:
    image: nats:latest
    healthcheck:
      test: ["CMD", "wget", "--spider", "-q", "http://localhost:8222/healthz"]
      interval: 10s
      timeout: 5s
      retries: 3
```

## Anti-Patterns to Avoid

### Unbounded Subject Cardinality

```
# BAD: Timestamp in subject creates unlimited unique subjects
clau-doom.agent.doom-agent-A.action.2024-12-15T10:30:00

# GOOD: Timestamp in message body
clau-doom.agent.doom-agent-A.action
  with payload: { "timestamp": "2024-12-15T10:30:00", ... }
```

### Missing Acknowledgments

```go
// BAD: No acknowledgment, causes redelivery storms
_, err := js.Subscribe("subject", func(msg *nats.Msg) {
    process(msg.Data) // Missing msg.Ack()
})

// GOOD: Always acknowledge
_, err := js.Subscribe("subject", func(msg *nats.Msg) {
    if err := process(msg.Data); err != nil {
        msg.Nak()
        return
    }
    msg.Ack()
})
```

### Synchronous Processing in Message Handlers

```go
// BAD: Blocking handler prevents message processing
_, err := nc.Subscribe("subject", func(msg *nats.Msg) {
    heavyComputation() // Blocks other messages
})

// GOOD: Async processing
_, err := nc.Subscribe("subject", func(msg *nats.Msg) {
    go heavyComputation()
})
```

### Large Messages Without Chunking

```
# BAD: Publishing 10MB message directly
nats pub subject huge_data.bin

# GOOD: Chunk messages or use object store
# Split into chunks: chunk-1, chunk-2, ...
# Or use JetStream Object Store for large blobs
```

## Integration Example: Full Workflow

```
1. Agent publishes action
   [Rust async-nats] → clau-doom.agent.doom-agent-A.action

2. Dashboard subscribes to actions
   [Go nats.go] ← clau-doom.agent.*.action (durable consumer)

3. JetStream persists to AGENT_EVENTS stream
   [NATS Server] stores to file

4. Analytics pulls batch for processing
   [Go nats.go] ← pull consumer on AGENT_EVENTS

5. Orchestrator publishes experiment complete
   [Go nats.go] → clau-doom.experiment.DOE-042.complete

6. Multiple services react to completion
   [Evolution Mgr] ← clau-doom.experiment.*.complete
   [Dashboard] ← clau-doom.experiment.*.complete
   [Analytics] ← clau-doom.experiment.*.complete
```

This pattern ensures:
- Real-time updates to dashboard
- Historical data for analytics
- Decoupled services via pub/sub
- Resilience via JetStream persistence
- Load balancing via queue groups
