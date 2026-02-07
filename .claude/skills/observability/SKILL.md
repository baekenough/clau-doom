---
name: observability
description: Structured logging, Prometheus metrics exposition, OpenTelemetry tracing, health endpoints, and alerting rules for the clau-doom container stack
user-invocable: false
---

# Observability Best Practices for clau-doom

## Structured Logging

### Rust (tracing crate)

#### Subscriber Setup with JSON Formatting

```rust
// agent-core/src/main.rs
use tracing::{info, debug, warn, error, instrument};
use tracing_subscriber::{
    fmt,
    layer::SubscriberExt,
    util::SubscriberInitExt,
    EnvFilter,
};
use std::io;

fn init_logging() {
    let filter = EnvFilter::try_from_default_env()
        .unwrap_or_else(|_| EnvFilter::new("agent_core=info,rag_client=info,scoring=debug"));

    tracing_subscriber::registry()
        .with(filter)
        .with(
            fmt::layer()
                .json()
                .with_current_span(true)
                .with_span_list(true)
                .with_target(true)
                .with_thread_ids(true)
                .with_writer(io::stdout)
        )
        .init();

    info!(
        agent_id = %std::env::var("AGENT_ID").unwrap_or_default(),
        version = env!("CARGO_PKG_VERSION"),
        "Agent core initialized"
    );
}
```

#### Instrument Macro for Automatic Span Creation

```rust
// agent-core/src/decision/mod.rs
use tracing::{instrument, info_span, debug, Span};

#[instrument(
    skip(self, game_state),
    fields(
        agent_id = %self.agent_id,
        episode_id = %self.current_episode,
        generation = %self.generation,
        health = %game_state.health,
        ammo = %game_state.ammo
    )
)]
pub async fn make_decision(&self, game_state: &GameState) -> Decision {
    let _span = info_span!("decision_pipeline").entered();

    // Strategy lookup span
    let strategy = self.lookup_strategy(game_state).await;

    // Scoring span
    let decision = self.score_actions(strategy, game_state).await;

    debug!(
        decision = ?decision,
        latency_ms = %decision.latency_ms,
        "Decision made"
    );

    decision
}

#[instrument(skip(self, game_state))]
async fn lookup_strategy(&self, game_state: &GameState) -> Strategy {
    let start = std::time::Instant::now();

    let query_embedding = self.embed_game_state(game_state);
    let results = self.opensearch_client
        .knn_search(&query_embedding, k=5)
        .await;

    let latency = start.elapsed();

    debug!(
        results_count = results.len(),
        latency_ms = %latency.as_millis(),
        "Strategy lookup complete"
    );

    results.into()
}
```

#### Structured Fields in Decision Pipeline

```rust
// agent-core/src/decision/scoring.rs
use tracing::{debug_span, warn};

pub fn score_actions(
    &self,
    strategies: Vec<Strategy>,
    game_state: &GameState,
) -> ScoredAction {
    let _span = debug_span!(
        "scoring",
        strategy_count = strategies.len(),
        health = game_state.health,
        enemy_count = game_state.enemies.len()
    ).entered();

    let mut best_action = None;
    let mut best_score = f32::MIN;

    for (idx, strategy) in strategies.iter().enumerate() {
        let score = self.compute_score(strategy, game_state);

        if score > best_score {
            best_score = score;
            best_action = Some(strategy.action.clone());

            debug!(
                strategy_idx = idx,
                score = %score,
                action = ?strategy.action,
                "New best action"
            );
        }
    }

    if best_action.is_none() {
        warn!("No valid action scored, using default");
        best_action = Some(Action::default());
    }

    ScoredAction {
        action: best_action.unwrap(),
        score: best_score,
    }
}
```

#### Environment Variable Filtering

```bash
# Per-module log levels
RUST_LOG=agent_core=debug,rag_client=info,scoring=trace,hyper=warn

# Span events
RUST_LOG=agent_core[decision_pipeline]=trace

# Full trace with spans
RUST_LOG=agent_core=trace,rag_client=trace
```

### Go (zap)

#### Production vs Development Logger Config

```go
// orchestrator/internal/logging/logger.go
package logging

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
    "os"
)

func NewLogger(dev bool) (*zap.Logger, error) {
    var logger *zap.Logger
    var err error

    if dev {
        config := zap.NewDevelopmentConfig()
        config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder
        logger, err = config.Build()
    } else {
        config := zap.NewProductionConfig()
        config.EncoderConfig.TimeKey = "timestamp"
        config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder
        logger, err = config.Build()
    }

    if err != nil {
        return nil, err
    }

    logger = logger.With(
        zap.String("service", "orchestrator"),
        zap.String("version", os.Getenv("VERSION")),
    )

    return logger, nil
}
```

#### Named Loggers for Components

```go
// orchestrator/internal/grpc/server.go
package grpc

import (
    "context"
    "go.uber.org/zap"
    "time"
)

type Server struct {
    logger *zap.Logger
    grpcLog *zap.Logger
    natsLog *zap.Logger
}

func NewServer(logger *zap.Logger) *Server {
    return &Server{
        logger: logger,
        grpcLog: logger.Named("grpc"),
        natsLog: logger.Named("nats"),
    }
}

func (s *Server) SpawnAgent(ctx context.Context, req *pb.SpawnRequest) (*pb.SpawnResponse, error) {
    start := time.Now()

    s.grpcLog.Info("Spawning agent",
        zap.String("agent_id", req.AgentId),
        zap.Int32("generation", req.Generation),
        zap.Strings("factors", req.Factors),
    )

    // ... spawn logic ...

    duration := time.Since(start)

    s.grpcLog.Info("Agent spawned",
        zap.String("agent_id", req.AgentId),
        zap.String("container_id", containerId),
        zap.Duration("duration", duration),
    )

    return &pb.SpawnResponse{ContainerId: containerId}, nil
}
```

#### Request ID Propagation via Context

```go
// orchestrator/internal/middleware/requestid.go
package middleware

import (
    "context"
    "github.com/google/uuid"
    "go.uber.org/zap"
)

type ctxKey string

const requestIDKey ctxKey = "request_id"

func WithRequestID(ctx context.Context) context.Context {
    requestID := uuid.New().String()
    return context.WithValue(ctx, requestIDKey, requestID)
}

func GetRequestID(ctx context.Context) string {
    if id, ok := ctx.Value(requestIDKey).(string); ok {
        return id
    }
    return ""
}

func LoggerWithRequestID(ctx context.Context, logger *zap.Logger) *zap.Logger {
    if requestID := GetRequestID(ctx); requestID != "" {
        return logger.With(zap.String("request_id", requestID))
    }
    return logger
}
```

#### Sampling for High-Volume Logs

```go
// orchestrator/internal/logging/sampled.go
package logging

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func NewSampledLogger(baseLogger *zap.Logger) *zap.Logger {
    // Sample: log first 100 of each level per second, then 1 in 100
    sampler := zapcore.NewSamplerWithOptions(
        baseLogger.Core(),
        time.Second,
        100,  // first
        100,  // thereafter
    )

    return zap.New(sampler)
}

// Use sampled logger for high-frequency operations
func (s *Server) handleEpisodeTick(tick EpisodeTick) {
    s.tickLog.Debug("Episode tick",  // tickLog is sampled
        zap.String("agent_id", tick.AgentID),
        zap.Int("frame", tick.Frame),
        zap.Float64("health", tick.Health),
    )
}
```

### Python (structlog)

#### Processor Pipeline Setup

```python
# analytics/logging_config.py
import structlog
import logging
from datetime import datetime

def setup_logging(log_level="INFO"):
    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            structlog.processors.JSONRenderer()
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, log_level),
    )
```

#### Bound Logger Pattern for Request Context

```python
# analytics/anova_runner.py
import structlog

logger = structlog.get_logger()

def run_anova_analysis(experiment_id: str, data_path: str):
    # Bind experiment context to logger
    log = logger.bind(
        experiment_id=experiment_id,
        analysis_type="anova",
        data_path=data_path
    )

    log.info("Starting ANOVA analysis")

    try:
        data = load_data(data_path)
        log.info("Data loaded", row_count=len(data))

        model = fit_anova(data)
        log.info("Model fitted",
                 factors=model.factors,
                 p_value=model.p_value)

        diagnostics = check_assumptions(model)
        log.info("Diagnostics complete",
                 normality_p=diagnostics.normality_p,
                 levene_p=diagnostics.levene_p)

        save_results(experiment_id, model, diagnostics)
        log.info("Analysis complete")

    except Exception as e:
        log.error("Analysis failed", exc_info=True)
        raise
```

### TypeScript (pino)

#### Base Logger with Serializers

```typescript
// dashboard/lib/logger.ts
import pino from 'pino';

const redactPaths = [
  'req.headers.authorization',
  'req.headers.cookie',
  'res.headers["set-cookie"]',
];

export const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  redact: {
    paths: redactPaths,
    remove: true,
  },
  serializers: {
    req: (req) => ({
      method: req.method,
      url: req.url,
      headers: req.headers,
      remoteAddress: req.socket.remoteAddress,
    }),
    res: (res) => ({
      statusCode: res.statusCode,
      headers: res.getHeaders(),
    }),
    err: pino.stdSerializers.err,
  },
  formatters: {
    level: (label) => ({ level: label }),
  },
});
```

#### Child Loggers per Request

```typescript
// dashboard/app/api/agents/route.ts
import { logger } from '@/lib/logger';
import { randomUUID } from 'crypto';

export async function GET(request: Request) {
  const requestId = randomUUID();
  const reqLogger = logger.child({ requestId });

  reqLogger.info({ req: request }, 'Fetching agents');

  try {
    const agents = await fetchAgents();

    reqLogger.info(
      { agentCount: agents.length },
      'Agents fetched successfully'
    );

    return Response.json(agents);
  } catch (error) {
    reqLogger.error({ err: error }, 'Failed to fetch agents');
    return Response.json({ error: 'Internal server error' }, { status: 500 });
  }
}
```

#### WebSocket Connection Logging

```typescript
// dashboard/lib/websocket-server.ts
import { WebSocketServer } from 'ws';
import { logger } from './logger';

const wss = new WebSocketServer({ port: 3001 });

wss.on('connection', (ws, req) => {
  const connectionId = randomUUID();
  const wsLogger = logger.child({
    connectionId,
    remoteAddress: req.socket.remoteAddress,
  });

  wsLogger.info('WebSocket connection established');

  ws.on('message', (data) => {
    wsLogger.debug({ messageSize: data.length }, 'Message received');
  });

  ws.on('close', (code, reason) => {
    wsLogger.info({ code, reason: reason.toString() }, 'Connection closed');
  });

  ws.on('error', (error) => {
    wsLogger.error({ err: error }, 'WebSocket error');
  });
});
```

## Prometheus Metrics

### Naming Convention

Pattern: `clau_doom_{component}_{metric}_{unit}`

Components:
- `agent` - Agent containers (Rust)
- `orchestrator` - Orchestrator service (Go)
- `dashboard` - Dashboard frontend (TypeScript)
- `opensearch` - OpenSearch queries
- `nats` - NATS messaging
- `mongodb` - MongoDB operations

### Key Metrics Definition

#### Agent Metrics

```promql
# Decision latency histogram
clau_doom_agent_decision_latency_seconds

# Total kills counter
clau_doom_agent_kills_total

# Episodes completed
clau_doom_agent_episodes_completed_total

# Current health gauge
clau_doom_agent_health

# Ammo remaining gauge
clau_doom_agent_ammo
```

#### Orchestrator Metrics

```promql
# Generation duration
clau_doom_orchestrator_generation_duration_seconds

# Active agents gauge
clau_doom_orchestrator_active_agents

# Container operations
clau_doom_orchestrator_container_operations_total

# gRPC request duration
clau_doom_orchestrator_grpc_request_duration_seconds
```

#### OpenSearch Metrics

```promql
# Query latency
clau_doom_opensearch_query_latency_seconds

# Query count
clau_doom_opensearch_queries_total

# Document hits
clau_doom_opensearch_document_hits
```

#### NATS Metrics

```promql
# Messages published
clau_doom_nats_messages_published_total

# Consumer pending messages
clau_doom_nats_consumer_pending_messages

# Message processing latency
clau_doom_nats_message_processing_seconds
```

#### MongoDB Metrics

```promql
# Operations total
clau_doom_mongodb_operations_total

# Operation latency
clau_doom_mongodb_operation_latency_seconds

# Connection pool size
clau_doom_mongodb_connection_pool_size
```

### Rust Exposition

#### Prometheus Crate Setup

```rust
// agent-core/src/metrics/mod.rs
use lazy_static::lazy_static;
use prometheus::{
    Registry, Histogram, Counter, Gauge,
    HistogramOpts, Opts, register_histogram_with_registry,
    register_counter_with_registry, register_gauge_with_registry,
};
use std::sync::Arc;

lazy_static! {
    pub static ref REGISTRY: Registry = Registry::new();

    pub static ref DECISION_LATENCY: Histogram = register_histogram_with_registry!(
        HistogramOpts::new(
            "clau_doom_agent_decision_latency_seconds",
            "Agent decision pipeline latency"
        ).buckets(vec![0.01, 0.025, 0.05, 0.1, 0.25]),
        REGISTRY
    ).unwrap();

    pub static ref KILLS_TOTAL: Counter = register_counter_with_registry!(
        Opts::new(
            "clau_doom_agent_kills_total",
            "Total kills by agent"
        ).const_labels([
            ("service", "agent-core"),
        ].into_iter().collect()),
        REGISTRY
    ).unwrap();

    pub static ref EPISODES_COMPLETED: Counter = register_counter_with_registry!(
        Opts::new(
            "clau_doom_agent_episodes_completed_total",
            "Total episodes completed"
        ),
        REGISTRY
    ).unwrap();

    pub static ref CURRENT_HEALTH: Gauge = register_gauge_with_registry!(
        Opts::new(
            "clau_doom_agent_health",
            "Current agent health"
        ),
        REGISTRY
    ).unwrap();
}
```

#### Histogram Observation in Decision Pipeline

```rust
// agent-core/src/decision/mod.rs
use crate::metrics::{DECISION_LATENCY, KILLS_TOTAL, CURRENT_HEALTH};

pub async fn make_decision(&self, game_state: &GameState) -> Decision {
    let timer = DECISION_LATENCY.start_timer();

    let decision = self.compute_decision(game_state).await;

    timer.observe_duration();

    // Update health gauge
    CURRENT_HEALTH.set(game_state.health as f64);

    // Increment kill counter if action resulted in kill
    if decision.resulted_in_kill {
        KILLS_TOTAL.inc();
    }

    decision
}
```

#### Metrics HTTP Endpoint

```rust
// agent-core/src/metrics/server.rs
use hyper::{Body, Request, Response, Server, Method, StatusCode};
use hyper::service::{make_service_fn, service_fn};
use prometheus::{Encoder, TextEncoder};
use std::convert::Infallible;
use std::net::SocketAddr;
use crate::metrics::REGISTRY;

async fn serve_metrics(_req: Request<Body>) -> Result<Response<Body>, Infallible> {
    if _req.method() != Method::GET || _req.uri().path() != "/metrics" {
        return Ok(Response::builder()
            .status(StatusCode::NOT_FOUND)
            .body(Body::from("Not Found"))
            .unwrap());
    }

    let encoder = TextEncoder::new();
    let metric_families = REGISTRY.gather();
    let mut buffer = vec![];

    encoder.encode(&metric_families, &mut buffer).unwrap();

    Ok(Response::builder()
        .status(StatusCode::OK)
        .header("Content-Type", encoder.format_type())
        .body(Body::from(buffer))
        .unwrap())
}

pub async fn start_metrics_server(addr: SocketAddr) {
    let make_svc = make_service_fn(|_conn| async {
        Ok::<_, Infallible>(service_fn(serve_metrics))
    });

    let server = Server::bind(&addr).serve(make_svc);

    tracing::info!("Metrics server listening on {}", addr);

    if let Err(e) = server.await {
        tracing::error!("Metrics server error: {}", e);
    }
}
```

### Go Exposition

#### Promauto for Metric Registration

```go
// orchestrator/internal/metrics/metrics.go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    GenerationDuration = promauto.NewHistogram(prometheus.HistogramOpts{
        Name: "clau_doom_orchestrator_generation_duration_seconds",
        Help: "Duration of generation execution",
        Buckets: prometheus.DefBuckets,
    })

    ActiveAgents = promauto.NewGauge(prometheus.GaugeOpts{
        Name: "clau_doom_orchestrator_active_agents",
        Help: "Number of currently active agent containers",
    })

    ContainerOperations = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "clau_doom_orchestrator_container_operations_total",
        Help: "Total container operations",
    }, []string{"operation", "status"})

    GRPCRequestDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Name: "clau_doom_orchestrator_grpc_request_duration_seconds",
        Help: "gRPC request duration",
        Buckets: []float64{0.001, 0.005, 0.01, 0.05, 0.1, 0.5, 1.0},
    }, []string{"method"})
)
```

#### gRPC Interceptor for Request Metrics

```go
// orchestrator/internal/grpc/interceptor.go
package grpc

import (
    "context"
    "time"
    "google.golang.org/grpc"
    "orchestrator/internal/metrics"
)

func UnaryServerInterceptor() grpc.UnaryServerInterceptor {
    return func(
        ctx context.Context,
        req interface{},
        info *grpc.UnaryServerInfo,
        handler grpc.UnaryHandler,
    ) (interface{}, error) {
        start := time.Now()

        resp, err := handler(ctx, req)

        duration := time.Since(start).Seconds()
        metrics.GRPCRequestDuration.WithLabelValues(info.FullMethod).Observe(duration)

        return resp, err
    }
}
```

#### Promhttp Handler for /metrics Endpoint

```go
// orchestrator/cmd/clau-doom/main.go
package main

import (
    "github.com/prometheus/client_golang/prometheus/promhttp"
    "net/http"
)

func startMetricsServer() {
    http.Handle("/metrics", promhttp.Handler())
    http.ListenAndServe(":9090", nil)
}

func main() {
    // Start metrics server
    go startMetricsServer()

    // ... rest of application ...
}
```

### Docker Compose Integration

#### Prometheus Container

```yaml
# docker-compose.yml
services:
  prometheus:
    image: prom/prometheus:v2.45.0
    ports:
      - "9091:9090"
    volumes:
      - ./docker/prometheus/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus-data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'
    networks:
      - clau-doom-net

volumes:
  prometheus-data:
```

#### Prometheus Scrape Configuration

```yaml
# docker/prometheus/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'orchestrator'
    static_configs:
      - targets: ['orchestrator:9090']
        labels:
          service: 'orchestrator'

  - job_name: 'agents'
    docker_sd_configs:
      - host: unix:///var/run/docker.sock
        refresh_interval: 30s
    relabel_configs:
      - source_labels: [__meta_docker_container_label_clau_doom_service]
        regex: agent
        action: keep
      - source_labels: [__meta_docker_container_label_clau_doom_agent_id]
        target_label: agent_id
      - source_labels: [__address__]
        target_label: __address__
        replacement: $1:9091

  - job_name: 'dashboard'
    static_configs:
      - targets: ['dashboard:9092']
        labels:
          service: 'dashboard'
```

#### Service Discovery via Docker Labels

```yaml
# docker-compose.yml (agent service)
services:
  agent:
    labels:
      - "clau-doom.service=agent"
      - "clau-doom.agent_id=${AGENT_ID}"
      - "prometheus.io/scrape=true"
      - "prometheus.io/port=9091"
      - "prometheus.io/path=/metrics"
```

## OpenTelemetry Traces

### Trace Context Propagation

#### W3C TraceContext Format

```
traceparent: 00-{trace-id}-{span-id}-{trace-flags}
tracestate: {vendor-specific-state}
```

#### gRPC Metadata Propagation

```go
// orchestrator/internal/grpc/tracing.go
package grpc

import (
    "context"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/propagation"
    "google.golang.org/grpc/metadata"
)

func InjectTraceContext(ctx context.Context) context.Context {
    md := metadata.MD{}
    otel.GetTextMapPropagator().Inject(ctx, &MetadataCarrier{md: &md})
    return metadata.NewOutgoingContext(ctx, md)
}

func ExtractTraceContext(ctx context.Context) context.Context {
    md, ok := metadata.FromIncomingContext(ctx)
    if !ok {
        return ctx
    }
    return otel.GetTextMapPropagator().Extract(ctx, &MetadataCarrier{md: &md})
}

type MetadataCarrier struct {
    md *metadata.MD
}

func (c *MetadataCarrier) Get(key string) string {
    values := c.md.Get(key)
    if len(values) == 0 {
        return ""
    }
    return values[0]
}

func (c *MetadataCarrier) Set(key, value string) {
    c.md.Set(key, value)
}

func (c *MetadataCarrier) Keys() []string {
    keys := make([]string, 0, len(*c.md))
    for k := range *c.md {
        keys = append(keys, k)
    }
    return keys
}
```

#### NATS Message Header Propagation

```go
// orchestrator/internal/nats/publisher.go
package nats

import (
    "context"
    "github.com/nats-io/nats.go"
    "go.opentelemetry.io/otel"
)

func PublishWithTrace(ctx context.Context, nc *nats.Conn, subject string, data []byte) error {
    msg := nats.NewMsg(subject)
    msg.Data = data

    // Inject trace context into NATS headers
    carrier := &NATSHeaderCarrier{header: &msg.Header}
    otel.GetTextMapPropagator().Inject(ctx, carrier)

    return nc.PublishMsg(msg)
}

type NATSHeaderCarrier struct {
    header *nats.Header
}

func (c *NATSHeaderCarrier) Get(key string) string {
    return c.header.Get(key)
}

func (c *NATSHeaderCarrier) Set(key, value string) {
    c.header.Set(key, value)
}

func (c *NATSHeaderCarrier) Keys() []string {
    keys := make([]string, 0, len(*c.header))
    for k := range *c.header {
        keys = append(keys, k)
    }
    return keys
}
```

### Rust OpenTelemetry Setup

```rust
// agent-core/src/tracing.rs
use opentelemetry::{global, sdk::trace as sdktrace, trace::TracerProvider};
use opentelemetry_otlp::WithExportConfig;
use tracing_opentelemetry::OpenTelemetryLayer;
use tracing_subscriber::{layer::SubscriberExt, Registry};

pub fn init_tracing() -> anyhow::Result<()> {
    let otlp_exporter = opentelemetry_otlp::new_exporter()
        .tonic()
        .with_endpoint("http://otel-collector:4317");

    let tracer = opentelemetry_otlp::new_pipeline()
        .tracing()
        .with_exporter(otlp_exporter)
        .with_trace_config(
            sdktrace::config()
                .with_resource(opentelemetry::sdk::Resource::new(vec![
                    opentelemetry::KeyValue::new("service.name", "agent-core"),
                    opentelemetry::KeyValue::new("service.version", env!("CARGO_PKG_VERSION")),
                ]))
        )
        .install_batch(opentelemetry::runtime::Tokio)?;

    let telemetry_layer = OpenTelemetryLayer::new(tracer);

    let subscriber = Registry::default()
        .with(tracing_subscriber::EnvFilter::from_default_env())
        .with(telemetry_layer);

    tracing::subscriber::set_global_default(subscriber)?;

    Ok(())
}
```

### Go OpenTelemetry Setup

```go
// orchestrator/internal/telemetry/telemetry.go
package telemetry

import (
    "context"
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/exporters/otlp/otlptrace/otlptracegrpc"
    "go.opentelemetry.io/otel/sdk/resource"
    sdktrace "go.opentelemetry.io/otel/sdk/trace"
    semconv "go.opentelemetry.io/otel/semconv/v1.17.0"
)

func InitTracer(ctx context.Context, serviceName, version string) (*sdktrace.TracerProvider, error) {
    exporter, err := otlptracegrpc.New(ctx,
        otlptracegrpc.WithEndpoint("otel-collector:4317"),
        otlptracegrpc.WithInsecure(),
    )
    if err != nil {
        return nil, err
    }

    res, err := resource.Merge(
        resource.Default(),
        resource.NewWithAttributes(
            semconv.SchemaURL,
            semconv.ServiceName(serviceName),
            semconv.ServiceVersion(version),
        ),
    )
    if err != nil {
        return nil, err
    }

    tp := sdktrace.NewTracerProvider(
        sdktrace.WithBatcher(exporter),
        sdktrace.WithResource(res),
        sdktrace.WithSampler(sdktrace.ParentBased(
            sdktrace.TraceIDRatioBased(0.1), // Sample 10%
        )),
    )

    otel.SetTracerProvider(tp)
    otel.SetTextMapPropagator(propagation.NewCompositeTextMapPropagator(
        propagation.TraceContext{},
        propagation.Baggage{},
    ))

    return tp, nil
}
```

### Sampling Configuration

```go
// Development: trace everything
sdktrace.WithSampler(sdktrace.AlwaysSample())

// Production: 10% sampling
sdktrace.WithSampler(sdktrace.ParentBased(
    sdktrace.TraceIDRatioBased(0.1),
))

// Adaptive: high sampling for errors
sdktrace.WithSampler(sdktrace.ParentBased(
    &AdaptiveSampler{
        baseRate: 0.1,
        errorRate: 1.0,
    },
))
```

## Health Endpoints

### gRPC Health Check

```go
// orchestrator/internal/grpc/health.go
package grpc

import (
    "context"
    "google.golang.org/grpc/health"
    "google.golang.org/grpc/health/grpc_health_v1"
)

func RegisterHealthServer(s *grpc.Server, checker *health.Server) {
    grpc_health_v1.RegisterHealthServer(s, checker)

    // Set serving status
    checker.SetServingStatus("", grpc_health_v1.HealthCheckResponse_SERVING)
}

// Docker Compose healthcheck
// healthcheck:
//   test: ["CMD", "grpc_health_probe", "-addr=:50051"]
//   interval: 10s
//   timeout: 5s
//   retries: 3
```

### HTTP Health Endpoints

```go
// orchestrator/internal/http/health.go
package http

import (
    "encoding/json"
    "net/http"
)

type HealthResponse struct {
    Status       string            `json:"status"`
    Dependencies map[string]string `json:"dependencies"`
}

func (s *Server) handleHealthz(w http.ResponseWriter, r *http.Request) {
    // Liveness: just check if process is running
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(map[string]string{"status": "ok"})
}

func (s *Server) handleReadyz(w http.ResponseWriter, r *http.Request) {
    // Readiness: check dependencies
    deps := map[string]string{}

    if err := s.natsClient.Ping(); err != nil {
        deps["nats"] = "unhealthy"
        w.WriteHeader(http.StatusServiceUnavailable)
    } else {
        deps["nats"] = "healthy"
    }

    if err := s.mongoClient.Ping(r.Context()); err != nil {
        deps["mongodb"] = "unhealthy"
        w.WriteHeader(http.StatusServiceUnavailable)
    } else {
        deps["mongodb"] = "healthy"
    }

    status := "ready"
    for _, health := range deps {
        if health != "healthy" {
            status = "not_ready"
            break
        }
    }

    if status == "ready" {
        w.WriteHeader(http.StatusOK)
    }

    json.NewEncoder(w).Encode(HealthResponse{
        Status:       status,
        Dependencies: deps,
    })
}
```

### Docker Compose Health Check Configuration

```yaml
# docker-compose.yml
services:
  orchestrator:
    healthcheck:
      test: ["CMD", "grpc_health_probe", "-addr=:50051"]
      interval: 10s
      timeout: 5s
      retries: 3
      start_period: 15s

  dashboard:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/api/health"]
      interval: 10s
      timeout: 5s
      retries: 3

  nats:
    healthcheck:
      test: ["CMD", "nats-server", "--signal", "ldm"]
      interval: 10s
      timeout: 5s
      retries: 3

  vizdoom:
    healthcheck:
      test: ["CMD", "/healthcheck.sh"]
      interval: 15s
      timeout: 5s
      retries: 3
```

## Grafana Dashboards

### Agent Performance Dashboard

```json
{
  "title": "Agent Performance",
  "panels": [
    {
      "title": "Decision Latency Heatmap",
      "type": "heatmap",
      "targets": [
        {
          "expr": "rate(clau_doom_agent_decision_latency_seconds_bucket[5m])"
        }
      ]
    },
    {
      "title": "Kill Rate Over Time",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(clau_doom_agent_kills_total[1m])",
          "legendFormat": "{{agent_id}} - Gen {{generation}}"
        }
      ]
    },
    {
      "title": "Survival Time Distribution",
      "type": "histogram",
      "targets": [
        {
          "expr": "clau_doom_agent_survival_seconds_bucket"
        }
      ]
    }
  ]
}
```

### System Health Dashboard

```json
{
  "title": "System Health",
  "panels": [
    {
      "title": "Container CPU Usage",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(container_cpu_usage_seconds_total{name=~\"clau-doom.*\"}[5m]) * 100"
        }
      ]
    },
    {
      "title": "NATS Message Throughput",
      "type": "graph",
      "targets": [
        {
          "expr": "rate(clau_doom_nats_messages_published_total[1m])",
          "legendFormat": "{{subject}}"
        }
      ]
    },
    {
      "title": "OpenSearch Query Latency",
      "type": "graph",
      "targets": [
        {
          "expr": "histogram_quantile(0.95, rate(clau_doom_opensearch_query_latency_seconds_bucket[5m]))"
        }
      ]
    }
  ]
}
```

### Dashboard Provisioning

```yaml
# docker/grafana/provisioning/dashboards/dashboard.yml
apiVersion: 1

providers:
  - name: 'clau-doom'
    orgId: 1
    folder: 'clau-doom'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/dashboards
```

```yaml
# docker/grafana/provisioning/datasources/prometheus.yml
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
```

## Alerting Rules

```yaml
# docker/prometheus/alerts.yml
groups:
  - name: agent_performance
    interval: 30s
    rules:
      - alert: HighDecisionLatency
        expr: histogram_quantile(0.99, rate(clau_doom_agent_decision_latency_seconds_bucket[5m])) > 0.1
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Agent decision latency too high"
          description: "P99 latency is {{ $value }}s (threshold: 0.1s)"

      - alert: ContainerRestartLoop
        expr: rate(container_last_seen{name=~"clau-doom.*"}[10m]) > 0.3
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "Container restarting frequently"
          description: "{{ $labels.name }} has restarted {{ $value }} times in 10 minutes"

  - name: system_health
    interval: 30s
    rules:
      - alert: OpenSearchSlowQueries
        expr: histogram_quantile(0.95, rate(clau_doom_opensearch_query_latency_seconds_bucket[5m])) > 0.2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "OpenSearch queries are slow"
          description: "P95 query latency is {{ $value }}s"

      - alert: NATSConsumerBacklog
        expr: clau_doom_nats_consumer_pending_messages > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "NATS consumer has backlog"
          description: "{{ $labels.consumer }} has {{ $value }} pending messages"

      - alert: HighMemoryUsage
        expr: (container_memory_usage_bytes / container_spec_memory_limit_bytes) * 100 > 85
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Container memory usage high"
          description: "{{ $labels.name }} using {{ $value }}% of memory limit"

      - alert: NoEpisodesCompleted
        expr: rate(clau_doom_agent_episodes_completed_total[30m]) == 0
        for: 30m
        labels:
          severity: critical
        annotations:
          summary: "No episodes completed"
          description: "Agent {{ $labels.agent_id }} has not completed any episodes in 30 minutes"
```

## Anti-Patterns to Avoid

### 1. Logging Sensitive Data

```rust
// WRONG: Logging credentials
tracing::info!(api_key = %api_key, "Connecting to OpenSearch");

// CORRECT: Redact or omit
tracing::info!(endpoint = %endpoint, "Connecting to OpenSearch");
```

### 2. High-Cardinality Labels

```rust
// WRONG: episode_id as label (potentially millions of unique values)
let counter = register_counter!(
    "episodes_total",
    "agent_id" => agent_id,
    "episode_id" => episode_id  // BAD: unbounded cardinality
);

// CORRECT: Use labels with bounded cardinality
let counter = register_counter!(
    "episodes_total",
    "agent_id" => agent_id,
    "generation" => generation.to_string()
);
// episode_id goes in structured logs, not metrics
```

### 3. Missing Log Levels

```python
# WRONG: Everything at INFO
logger.info("Starting analysis")
logger.info("Data loaded")
logger.info("Intermediate calculation: x=42")  # Too verbose
logger.info("Analysis complete")

# CORRECT: Appropriate levels
logger.info("Starting analysis")
logger.debug("Data loaded: %d rows", len(data))
logger.debug("Intermediate calculation: x=%d", x)
logger.info("Analysis complete")
```

### 4. Not Correlating Logs/Metrics/Traces

```go
// WRONG: No correlation between logs, metrics, traces
logger.Info("Request received")
metrics.RequestCount.Inc()
// No trace context propagation

// CORRECT: Shared identifiers
ctx = WithRequestID(ctx)
logger := logger.With(zap.String("request_id", GetRequestID(ctx)))
logger.Info("Request received")
metrics.RequestCount.Inc()
span := tracer.Start(ctx, "handle_request")
defer span.End()
```

### 5. Health Checks That Mask Problems

```go
// WRONG: Always return healthy
func handleHealthz(w http.ResponseWriter, r *http.Request) {
    w.WriteHeader(http.StatusOK)  // Even if dependencies are down
}

// CORRECT: Check actual health
func handleReadyz(w http.ResponseWriter, r *http.Request) {
    if err := checkDependencies(); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        return
    }
    w.WriteHeader(http.StatusOK)
}
```
