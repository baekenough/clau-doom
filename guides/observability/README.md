# Observability Reference Guide

Comprehensive observability guide for the clau-doom multi-container research platform: structured logging, metrics collection, distributed tracing, and monitoring dashboards.

## Key Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| OpenTelemetry | https://opentelemetry.io | Unified observability framework |
| Prometheus | https://prometheus.io | Metrics collection and storage |
| Grafana | https://grafana.com | Visualization and dashboards |
| tracing (Rust) | https://docs.rs/tracing | Structured logging for Rust |
| zap (Go) | https://github.com/uber-go/zap | High-performance Go logging |
| structlog (Python) | https://www.structlog.org | Structured logging for Python |
| pino (TypeScript) | https://getpino.io | Fast JSON logging for Node.js |
| grpc_health_probe | https://github.com/grpc-ecosystem/grpc-health-probe | gRPC health checks |

## clau-doom Context

The clau-doom platform is a multi-container research environment requiring unified observability:

```
Stack Components:
- agent-core (Rust): Decision engine, RAG client, scoring (< 100ms latency)
- orchestrator (Go): Agent lifecycle, gRPC API, generation management
- analytics (Python): VizDoom glue, ANOVA, DOE execution
- dashboard (Next.js): Real-time spectation, research visualization

Observability Challenges:
1. Multi-language stack (Rust, Go, Python, TypeScript)
2. Distributed communication (gRPC, NATS pub/sub, WebSocket)
3. Performance-critical paths (agent decision < 100ms)
4. Research integrity (trace experiment provenance)
5. Dynamic agent spawning (container lifecycle tracking)

Requirements:
- Structured logging with consistent fields across languages
- Per-agent metrics (kills, survival, decision latency)
- Per-experiment metrics (episodes completed, run status)
- End-to-end traces (Dashboard → Orchestrator → Agent → OpenSearch)
- Real-time monitoring (Grafana dashboards)
- Health checks for all services
```

## Structured Logging

### Rust (tracing crate)

The `tracing` crate provides powerful structured, async-aware logging for Rust.

#### Basic Setup

```rust
// agent-core/src/main.rs
use tracing::{info, warn, error, debug, instrument};
use tracing_subscriber::{layer::SubscriberExt, util::SubscriberInitExt, EnvFilter};

fn init_logging() {
    tracing_subscriber::registry()
        .with(EnvFilter::from_default_env()) // RUST_LOG=info
        .with(
            tracing_subscriber::fmt::layer()
                .json() // JSON output for structured parsing
                .with_current_span(true) // Include span context
                .with_thread_ids(true)
                .with_target(true)
        )
        .init();
}
```

#### Structured Fields

```rust
use tracing::{info, instrument};

#[instrument(
    name = "agent.decision",
    skip(self, state),
    fields(
        agent_id = %self.agent_id,
        episode_id = %state.episode_id,
        generation = self.generation,
        health = state.health,
        ammo = state.ammo
    )
)]
async fn make_decision(&self, state: &GameState) -> Decision {
    let start = std::time::Instant::now();

    // RAG search for relevant strategy
    let strategy = self.rag_client.search(state).await?;

    info!(
        strategy_id = %strategy.id,
        strategy_trust = strategy.trust_score,
        "Retrieved strategy from OpenSearch"
    );

    // Apply scoring algorithm
    let decision = self.scorer.score(&state, &strategy);

    let latency_ms = start.elapsed().as_millis();

    info!(
        action = ?decision.action,
        score = decision.score,
        latency_ms = latency_ms,
        "Decision computed"
    );

    if latency_ms > 100 {
        warn!(
            latency_ms = latency_ms,
            "Decision latency exceeded 100ms threshold"
        );
    }

    Ok(decision)
}
```

#### Log Levels and Filtering

```bash
# Environment variable controls filtering
export RUST_LOG=info                           # All info and above
export RUST_LOG=agent_core=debug,scoring=trace # Per-module levels
export RUST_LOG=agent_core::rag=debug          # Specific module

# In code: conditional compilation for expensive logging
debug!(expensive_data = ?compute_debug_info(), "Debug snapshot");
```

#### JSON Output Format

```json
{
  "timestamp": "2024-12-15T10:30:42.123Z",
  "level": "INFO",
  "target": "agent_core::decision",
  "fields": {
    "message": "Decision computed",
    "agent_id": "doom-agent-A",
    "episode_id": "DOE-042-run-5-ep-15",
    "generation": 3,
    "health": 87,
    "ammo": 42,
    "action": "ATTACK",
    "score": 0.82,
    "latency_ms": 45
  },
  "span": {
    "name": "agent.decision",
    "agent_id": "doom-agent-A",
    "episode_id": "DOE-042-run-5-ep-15"
  }
}
```

#### Example: Logging Decision Engine Calls

```rust
use tracing::{info, instrument, Span};

#[instrument(skip(self))]
async fn execute_episode(&self, seed: u32) -> EpisodeResult {
    let episode_span = Span::current();
    episode_span.record("seed", seed);
    episode_span.record("agent_id", &self.agent_id);

    info!(seed = seed, "Episode started");

    let mut total_latency_ms = 0u64;
    let mut decision_count = 0u32;

    loop {
        let state = self.game.get_state();

        let start = std::time::Instant::now();
        let decision = self.make_decision(&state).await?;
        let latency_ms = start.elapsed().as_millis() as u64;

        total_latency_ms += latency_ms;
        decision_count += 1;

        if self.game.is_episode_finished() {
            break;
        }
    }

    let avg_latency_ms = total_latency_ms / decision_count as u64;

    info!(
        seed = seed,
        decision_count = decision_count,
        avg_latency_ms = avg_latency_ms,
        kills = result.kills,
        survival_time_s = result.survival_time,
        "Episode completed"
    );

    Ok(result)
}
```

### Go (zap)

Uber's `zap` provides high-performance structured logging for Go.

#### Logger Initialization

```go
// orchestrator/internal/logging/logger.go
package logging

import (
    "go.uber.org/zap"
    "go.uber.org/zap/zapcore"
)

func NewProduction() (*zap.Logger, error) {
    config := zap.NewProductionConfig()
    config.EncoderConfig.TimeKey = "timestamp"
    config.EncoderConfig.EncodeTime = zapcore.ISO8601TimeEncoder

    return config.Build()
}

func NewDevelopment() (*zap.Logger, error) {
    config := zap.NewDevelopmentConfig()
    config.EncoderConfig.EncodeLevel = zapcore.CapitalColorLevelEncoder

    return config.Build()
}
```

#### Structured Fields

```go
import "go.uber.org/zap"

func (o *Orchestrator) SpawnAgent(ctx context.Context, req *pb.SpawnAgentRequest) error {
    logger := o.logger.With(
        zap.String("agent_id", req.AgentId),
        zap.Int32("generation", req.Generation),
        zap.String("experiment_id", req.ExperimentId),
    )

    logger.Info("Spawning agent container")

    start := time.Now()

    containerID, err := o.docker.CreateContainer(ctx, req)
    if err != nil {
        logger.Error("Failed to create container",
            zap.Error(err),
            zap.Duration("elapsed", time.Since(start)),
        )
        return err
    }

    logger.Info("Agent container spawned successfully",
        zap.String("container_id", containerID),
        zap.Duration("spawn_duration", time.Since(start)),
    )

    return nil
}
```

#### Log Levels and Sampling

```go
// High-volume logs with sampling (1 in 100)
sampledLogger := logger.WithOptions(zap.WrapCore(func(core zapcore.Core) zapcore.Core {
    return zapcore.NewSamplerWithOptions(
        core,
        time.Second,    // interval
        100,            // first
        100,            // thereafter
    )
}))

sampledLogger.Debug("High-frequency event")
```

#### Context-Aware Logging

```go
import (
    "context"
    "go.uber.org/zap"
)

// Attach logger to context
func WithLogger(ctx context.Context, logger *zap.Logger) context.Context {
    return context.WithValue(ctx, loggerKey, logger)
}

// Extract logger from context
func FromContext(ctx context.Context) *zap.Logger {
    if logger, ok := ctx.Value(loggerKey).(*zap.Logger); ok {
        return logger
    }
    return zap.L() // fallback to global logger
}

// Usage in handlers
func (s *Server) ExecuteExperiment(ctx context.Context, req *pb.ExperimentRequest) (*pb.ExperimentResponse, error) {
    logger := FromContext(ctx).With(
        zap.String("experiment_id", req.ExperimentId),
        zap.Int32("total_runs", req.TotalRuns),
    )

    logger.Info("Experiment execution started")
    defer logger.Info("Experiment execution completed")

    // ... execution logic
}
```

#### Example: Logging Orchestrator Lifecycle Events

```go
func (o *Orchestrator) RunGeneration(ctx context.Context, gen int32) error {
    logger := o.logger.With(
        zap.Int32("generation", gen),
        zap.Int32("population_size", o.config.PopulationSize),
    )

    logger.Info("Generation started")

    // Spawn population
    spawnStart := time.Now()
    agents := make([]*Agent, o.config.PopulationSize)

    for i := int32(0); i < o.config.PopulationSize; i++ {
        agent, err := o.SpawnAgent(ctx, &pb.SpawnAgentRequest{
            AgentId:      fmt.Sprintf("gen-%d-agent-%d", gen, i),
            Generation:   gen,
            ExperimentId: o.currentExperiment,
        })
        if err != nil {
            logger.Error("Failed to spawn agent",
                zap.Int32("agent_index", i),
                zap.Error(err),
            )
            return err
        }
        agents[i] = agent
    }

    logger.Info("Population spawned",
        zap.Int("agent_count", len(agents)),
        zap.Duration("spawn_duration", time.Since(spawnStart)),
    )

    // Execute episodes
    execStart := time.Now()
    results := o.executePopulation(ctx, agents)

    logger.Info("Population execution completed",
        zap.Int("results_count", len(results)),
        zap.Duration("execution_duration", time.Since(execStart)),
    )

    // Compute fitness
    fitness := o.computeFitness(results)

    logger.Info("Generation completed",
        zap.Float64("best_fitness", fitness.Best),
        zap.Float64("mean_fitness", fitness.Mean),
        zap.Float64("worst_fitness", fitness.Worst),
        zap.Duration("total_duration", time.Since(spawnStart)),
    )

    return nil
}
```

### Python (structlog)

`structlog` provides structured logging with a flexible processor pipeline.

#### Processor Pipeline Configuration

```python
# analytics/logging_config.py
import structlog
from structlog.processors import JSONRenderer, TimeStamper, add_log_level

def configure_logging():
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            add_log_level,
            TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )

# Call during initialization
configure_logging()
logger = structlog.get_logger()
```

#### Bound Loggers with Context

```python
import structlog

logger = structlog.get_logger()

def run_anova(experiment_id: str, data_path: str):
    # Bind context for all logs in this function
    log = logger.bind(
        experiment_id=experiment_id,
        data_path=data_path,
        analysis_type="factorial_anova"
    )

    log.info("ANOVA analysis started")

    # Load data
    import pandas as pd
    df = pd.read_csv(data_path)
    log.info("Data loaded", row_count=len(df), column_count=len(df.columns))

    # Run ANOVA
    import statsmodels.api as sm
    from statsmodels.formula.api import ols

    model = ols('kill_efficiency ~ C(memory) * C(strength)', data=df).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    # Extract results
    for factor, row in anova_table.iterrows():
        log.info("ANOVA result",
            factor=factor,
            f_statistic=float(row['F']),
            p_value=float(row['PR(>F)']),
            significant=(row['PR(>F)'] < 0.05)
        )

    log.info("ANOVA analysis completed")
```

#### Integration with stdlib Logging

```python
import logging
import structlog

# Bridge stdlib logging to structlog
structlog.configure(
    logger_factory=structlog.stdlib.LoggerFactory(),
)

# Now stdlib logging calls also go through structlog
logging.info("This will be structured", extra={"key": "value"})
```

#### Example: Logging ANOVA Execution with Parameters

```python
import structlog
import pandas as pd
from typing import Dict, Any

logger = structlog.get_logger()

def execute_doe_analysis(
    experiment_id: str,
    design_matrix: pd.DataFrame,
    response_var: str,
    factors: list[str],
    alpha: float = 0.05
) -> Dict[str, Any]:
    log = logger.bind(
        experiment_id=experiment_id,
        response_var=response_var,
        factors=factors,
        alpha=alpha,
        sample_size=len(design_matrix)
    )

    log.info("DOE analysis started")

    # Build formula
    formula = f"{response_var} ~ " + " * ".join([f"C({f})" for f in factors])
    log.debug("ANOVA formula built", formula=formula)

    # Fit model
    import statsmodels.api as sm
    from statsmodels.formula.api import ols

    model = ols(formula, data=design_matrix).fit()
    anova_table = sm.stats.anova_lm(model, typ=2)

    # Residual diagnostics
    from scipy import stats
    residuals = model.resid

    # Normality test
    _, normality_p = stats.shapiro(residuals)
    log.info("Residual normality test",
        test="shapiro-wilk",
        p_value=normality_p,
        assumption_met=(normality_p > alpha)
    )

    # Results
    results = {}
    for factor, row in anova_table.iterrows():
        p_value = float(row['PR(>F)'])
        significant = p_value < alpha

        results[factor] = {
            'f_statistic': float(row['F']),
            'p_value': p_value,
            'significant': significant
        }

        log.info("Factor effect",
            factor=factor,
            f_statistic=float(row['F']),
            p_value=p_value,
            significant=significant
        )

    log.info("DOE analysis completed",
        significant_factors=sum(1 for r in results.values() if r['significant'])
    )

    return results
```

### TypeScript (pino)

`pino` is a fast JSON logger for Node.js with low overhead.

#### Logger Creation with Serializers

```typescript
// dashboard/lib/logger.ts
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',

  serializers: {
    req: pino.stdSerializers.req,
    res: pino.stdSerializers.res,
    err: pino.stdSerializers.err,
  },

  formatters: {
    level: (label) => {
      return { level: label.toUpperCase() };
    },
  },

  timestamp: pino.stdTimeFunctions.isoTime,
});

export default logger;
```

#### Child Loggers for Request Context

```typescript
import logger from '@/lib/logger';
import { NextRequest, NextResponse } from 'next/server';

export async function GET(req: NextRequest) {
  const requestId = crypto.randomUUID();

  // Create child logger with request context
  const log = logger.child({
    requestId,
    method: req.method,
    url: req.url,
  });

  log.info('API request received');

  try {
    const result = await processRequest(req);

    log.info('API request completed', {
      status: 200,
      responseSize: JSON.stringify(result).length,
    });

    return NextResponse.json(result);
  } catch (error) {
    log.error({ err: error }, 'API request failed');
    return NextResponse.json({ error: 'Internal error' }, { status: 500 });
  }
}
```

#### Log Level Management

```typescript
// Dynamic log level adjustment
logger.level = 'debug';

// Per-module log levels
const dbLogger = logger.child({ module: 'database' });
dbLogger.level = 'trace';

const wsLogger = logger.child({ module: 'websocket' });
wsLogger.level = 'info';
```

#### Example: Logging WebSocket Connections and Dashboard Events

```typescript
import logger from '@/lib/logger';
import { WebSocket } from 'ws';

export class DashboardWebSocketServer {
  private clients = new Map<string, WebSocket>();

  handleConnection(ws: WebSocket, connectionId: string) {
    const log = logger.child({
      connectionId,
      module: 'websocket',
    });

    log.info('WebSocket connection established');

    this.clients.set(connectionId, ws);

    ws.on('message', (data) => {
      try {
        const message = JSON.parse(data.toString());

        log.debug('WebSocket message received', {
          messageType: message.type,
          payloadSize: data.length,
        });

        this.handleMessage(connectionId, message);
      } catch (error) {
        log.error({ err: error }, 'Failed to parse WebSocket message');
      }
    });

    ws.on('close', (code, reason) => {
      log.info('WebSocket connection closed', {
        code,
        reason: reason.toString(),
        duration: Date.now() - connectionStart,
      });

      this.clients.delete(connectionId);
    });

    ws.on('error', (error) => {
      log.error({ err: error }, 'WebSocket error');
    });
  }

  broadcastExperimentProgress(experimentId: string, progress: number) {
    const log = logger.child({
      experimentId,
      module: 'websocket',
      event: 'experiment_progress',
    });

    const message = JSON.stringify({
      type: 'experiment_progress',
      experimentId,
      progress,
      timestamp: new Date().toISOString(),
    });

    let sentCount = 0;

    this.clients.forEach((ws, connectionId) => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(message);
        sentCount++;
      }
    });

    log.debug('Broadcast sent', {
      clientCount: sentCount,
      messageSize: message.length,
    });
  }
}
```

## Prometheus Metrics

### Metric Types

| Type | Purpose | Example |
|------|---------|---------|
| Counter | Monotonically increasing value | `agent_kills_total` |
| Gauge | Value that can go up or down | `agent_survival_time_seconds` |
| Histogram | Distribution of values | `agent_decision_latency_seconds` |
| Summary | Similar to histogram, client-side quantiles | `opensearch_query_duration_seconds` |

### Naming Conventions

```
clau_doom_{component}_{metric}_{unit}

Examples:
- clau_doom_agent_decision_latency_seconds
- clau_doom_agent_kills_total
- clau_doom_experiment_episodes_completed
- clau_doom_opensearch_query_latency_seconds
- clau_doom_generation_fitness_score
```

### Rust: prometheus crate

```rust
// agent-core/src/metrics.rs
use prometheus::{
    register_histogram_vec, register_counter_vec, register_gauge_vec,
    HistogramVec, CounterVec, GaugeVec, Encoder, TextEncoder,
};
use lazy_static::lazy_static;

lazy_static! {
    pub static ref DECISION_LATENCY: HistogramVec = register_histogram_vec!(
        "clau_doom_agent_decision_latency_seconds",
        "Agent decision latency in seconds",
        &["agent_id", "generation"],
        vec![0.001, 0.005, 0.010, 0.025, 0.050, 0.100, 0.250, 0.500, 1.0]
    ).unwrap();

    pub static ref KILLS_TOTAL: CounterVec = register_counter_vec!(
        "clau_doom_agent_kills_total",
        "Total kills by agent",
        &["agent_id", "generation", "experiment_id"]
    ).unwrap();

    pub static ref SURVIVAL_TIME: GaugeVec = register_gauge_vec!(
        "clau_doom_agent_survival_time_seconds",
        "Agent survival time in current episode",
        &["agent_id", "generation"]
    ).unwrap();

    pub static ref OPENSEARCH_LATENCY: HistogramVec = register_histogram_vec!(
        "clau_doom_opensearch_query_latency_seconds",
        "OpenSearch kNN query latency",
        &["agent_id", "index"],
        vec![0.001, 0.005, 0.010, 0.025, 0.050, 0.100, 0.250]
    ).unwrap();
}

// Usage in code
impl Agent {
    async fn make_decision(&self, state: &GameState) -> Decision {
        let timer = DECISION_LATENCY
            .with_label_values(&[&self.agent_id, &self.generation.to_string()])
            .start_timer();

        let decision = self.compute_decision(state).await;

        timer.observe_duration(); // Records latency

        decision
    }

    fn record_kill(&self) {
        KILLS_TOTAL
            .with_label_values(&[
                &self.agent_id,
                &self.generation.to_string(),
                &self.experiment_id,
            ])
            .inc();
    }
}

// Metrics endpoint (Axum)
use axum::{routing::get, Router};

async fn metrics_handler() -> String {
    let encoder = TextEncoder::new();
    let metric_families = prometheus::gather();
    encoder.encode_to_string(&metric_families).unwrap()
}

pub fn metrics_router() -> Router {
    Router::new().route("/metrics", get(metrics_handler))
}
```

### Go: promhttp and promauto

```go
// orchestrator/internal/metrics/metrics.go
package metrics

import (
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    EpisodesCompleted = promauto.NewCounterVec(
        prometheus.CounterOpts{
            Name: "clau_doom_experiment_episodes_completed",
            Help: "Total episodes completed by experiment",
        },
        []string{"experiment_id", "run_id"},
    )

    GenerationFitness = promauto.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "clau_doom_generation_fitness_score",
            Help: "Best fitness score for generation",
        },
        []string{"experiment_id", "generation"},
    )

    ContainerSpawnDuration = promauto.NewHistogram(
        prometheus.HistogramOpts{
            Name: "clau_doom_container_spawn_duration_seconds",
            Help: "Container spawn duration",
            Buckets: prometheus.DefBuckets,
        },
    )
)

// Usage
func (o *Orchestrator) ExecuteRun(ctx context.Context, runID string) error {
    for i := 0; i < episodesPerRun; i++ {
        err := o.executeEpisode(ctx, runID, i)
        if err != nil {
            return err
        }

        EpisodesCompleted.WithLabelValues(o.experimentID, runID).Inc()
    }
    return nil
}

// Expose metrics endpoint
import "github.com/prometheus/client_golang/prometheus/promhttp"

http.Handle("/metrics", promhttp.Handler())
```

### Python: prometheus_client

```python
# analytics/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server

anova_executions = Counter(
    'clau_doom_anova_executions_total',
    'Total ANOVA executions',
    ['experiment_id', 'design_type']
)

anova_duration = Histogram(
    'clau_doom_anova_duration_seconds',
    'ANOVA execution duration',
    ['experiment_id']
)

significant_factors = Gauge(
    'clau_doom_significant_factors',
    'Number of significant factors found',
    ['experiment_id']
)

# Usage
from prometheus_client import start_http_server

def run_anova(experiment_id: str, design_type: str):
    with anova_duration.labels(experiment_id).time():
        results = perform_anova(...)

    sig_count = sum(1 for r in results.values() if r['significant'])
    significant_factors.labels(experiment_id).set(sig_count)

    anova_executions.labels(experiment_id, design_type).inc()

# Start metrics server
start_http_server(8000)
```

### Key Metrics to Track

```yaml
Agent Performance:
  - clau_doom_agent_decision_latency_seconds (Histogram)
    labels: [agent_id, generation]
  - clau_doom_agent_kills_total (Counter)
    labels: [agent_id, generation, experiment_id]
  - clau_doom_agent_survival_time_seconds (Gauge)
    labels: [agent_id, generation]
  - clau_doom_agent_damage_dealt_total (Counter)
    labels: [agent_id, generation]

Experiment Execution:
  - clau_doom_experiment_episodes_completed (Counter)
    labels: [experiment_id, run_id]
  - clau_doom_experiment_run_duration_seconds (Histogram)
    labels: [experiment_id, run_id]

Evolution:
  - clau_doom_generation_fitness_score (Gauge)
    labels: [experiment_id, generation, metric_type]
    metric_type: [best, mean, worst]

Infrastructure:
  - clau_doom_opensearch_query_latency_seconds (Histogram)
    labels: [agent_id, index]
  - clau_doom_nats_messages_published_total (Counter)
    labels: [subject]
  - clau_doom_duckdb_query_duration_seconds (Histogram)
    labels: [query_type]
  - clau_doom_container_restarts_total (Counter)
    labels: [service, reason]
```

## OpenTelemetry Traces

### Trace Context Propagation Across gRPC

```rust
// agent-core/src/tracing.rs
use opentelemetry::{global, sdk::propagation::TraceContextPropagator};
use tonic::metadata::MetadataMap;

pub fn init_tracing() {
    global::set_text_map_propagator(TraceContextPropagator::new());

    let tracer = opentelemetry_jaeger::new_agent_pipeline()
        .with_service_name("agent-core")
        .install_simple()
        .unwrap();

    tracing_subscriber::registry()
        .with(tracing_opentelemetry::layer().with_tracer(tracer))
        .init();
}

// Extract trace context from gRPC metadata
use opentelemetry::propagation::Extractor;

struct MetadataExtractor<'a>(&'a MetadataMap);

impl<'a> Extractor for MetadataExtractor<'a> {
    fn get(&self, key: &str) -> Option<&str> {
        self.0.get(key).and_then(|v| v.to_str().ok())
    }

    fn keys(&self) -> Vec<&str> {
        self.0.keys().map(|k| k.as_str()).collect()
    }
}

// In gRPC handler
async fn handle_request(
    request: tonic::Request<SpawnRequest>
) -> Result<tonic::Response<SpawnResponse>, tonic::Status> {
    let parent_cx = global::get_text_map_propagator(|prop| {
        prop.extract(&MetadataExtractor(request.metadata()))
    });

    let span = tracing::info_span!("agent.spawn");
    let _guard = span.entered();

    // Trace is now connected to parent
    process_spawn(request.into_inner()).await
}
```

### Span Creation for Rust and Go

```rust
// Rust: async instrumentation
#[tracing::instrument(
    name = "rag.search",
    skip(self, query),
    fields(
        agent_id = %self.agent_id,
        query_vector_dim = query.len()
    )
)]
async fn search_opensearch(&self, query: &[f32]) -> Result<Strategy> {
    let response = self.client.search(query).await?;
    tracing::info!(
        results_count = response.hits.len(),
        top_score = response.hits.first().map(|h| h.score)
    );
    Ok(response.into())
}
```

```go
// Go: manual span creation
import (
    "go.opentelemetry.io/otel"
    "go.opentelemetry.io/otel/attribute"
    "go.opentelemetry.io/otel/trace"
)

func (o *Orchestrator) SpawnAgent(ctx context.Context, req *pb.SpawnRequest) error {
    tracer := otel.Tracer("orchestrator")
    ctx, span := tracer.Start(ctx, "orchestrator.spawn_agent",
        trace.WithAttributes(
            attribute.String("agent_id", req.AgentId),
            attribute.Int("generation", int(req.Generation)),
        ),
    )
    defer span.End()

    containerID, err := o.docker.CreateContainer(ctx, req)
    if err != nil {
        span.RecordError(err)
        return err
    }

    span.SetAttributes(attribute.String("container_id", containerID))
    return nil
}
```

### Trace ID Injection into NATS Messages

```go
import (
    "go.opentelemetry.io/otel/propagation"
)

func (o *Orchestrator) PublishEvent(ctx context.Context, subject string, data []byte) error {
    // Create NATS message
    msg := nats.NewMsg(subject)
    msg.Data = data

    // Inject trace context into headers
    propagator := otel.GetTextMapPropagator()
    propagator.Inject(ctx, &NATSHeaderCarrier{msg.Header})

    return o.nats.PublishMsg(msg)
}

// Carrier for NATS headers
type NATSHeaderCarrier struct {
    header nats.Header
}

func (c *NATSHeaderCarrier) Get(key string) string {
    return c.header.Get(key)
}

func (c *NATSHeaderCarrier) Set(key, value string) {
    c.header.Set(key, value)
}

func (c *NATSHeaderCarrier) Keys() []string {
    keys := make([]string, 0, len(c.header))
    for k := range c.header {
        keys = append(keys, k)
    }
    return keys
}
```

### Connecting Traces: Dashboard → Orchestrator → Agent → OpenSearch

```
User clicks "Start Experiment" in Dashboard (trace_id: abc123)
    │
    ├─ Dashboard sends gRPC ExecuteExperiment (propagates trace_id)
    │       │
    │       └─ Orchestrator receives request (extracts trace_id)
    │               │
    │               ├─ Orchestrator spawns agent containers
    │               │       │
    │               │       └─ Agent receives config via gRPC (trace_id in metadata)
    │               │               │
    │               │               └─ Agent queries OpenSearch (trace_id in HTTP headers)
    │               │
    │               └─ Orchestrator publishes progress to NATS (trace_id in message headers)
    │                       │
    │                       └─ Dashboard subscribes to updates (receives trace_id)
    │
    └─ All spans linked by trace_id: abc123
```

### Sampling Strategies

```yaml
# Development: always sample
sampling:
  type: always_on

# Production: probabilistic sampling
sampling:
  type: probabilistic
  rate: 0.1  # 10% of traces

# Research: sample decision-critical paths
sampling:
  type: parent_based
  root:
    type: always_on  # Always sample user-initiated traces
  remote_parent_sampled:
    type: always_on
  remote_parent_not_sampled:
    type: probabilistic
    rate: 0.01
```

## Grafana Dashboards

### Agent Performance Dashboard

```json
{
  "dashboard": {
    "title": "Agent Performance",
    "panels": [
      {
        "title": "Decision Latency (P50, P95, P99)",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, rate(clau_doom_agent_decision_latency_seconds_bucket[5m]))",
            "legendFormat": "P50 - {{agent_id}}"
          },
          {
            "expr": "histogram_quantile(0.95, rate(clau_doom_agent_decision_latency_seconds_bucket[5m]))",
            "legendFormat": "P95 - {{agent_id}}"
          },
          {
            "expr": "histogram_quantile(0.99, rate(clau_doom_agent_decision_latency_seconds_bucket[5m]))",
            "legendFormat": "P99 - {{agent_id}}"
          }
        ]
      },
      {
        "title": "Kills per Minute",
        "targets": [
          {
            "expr": "rate(clau_doom_agent_kills_total[1m]) * 60",
            "legendFormat": "{{agent_id}}"
          }
        ]
      },
      {
        "title": "Survival Time",
        "targets": [
          {
            "expr": "clau_doom_agent_survival_time_seconds",
            "legendFormat": "{{agent_id}}"
          }
        ]
      }
    ]
  }
}
```

### Experiment Progress Dashboard

```json
{
  "dashboard": {
    "title": "Experiment Progress",
    "panels": [
      {
        "title": "Episodes Completed",
        "targets": [
          {
            "expr": "sum by (experiment_id) (clau_doom_experiment_episodes_completed)",
            "legendFormat": "{{experiment_id}}"
          }
        ]
      },
      {
        "title": "Run Duration Distribution",
        "targets": [
          {
            "expr": "histogram_quantile(0.50, sum by (le) (rate(clau_doom_experiment_run_duration_seconds_bucket[10m])))",
            "legendFormat": "P50"
          }
        ]
      },
      {
        "title": "Fitness Score Progression",
        "targets": [
          {
            "expr": "clau_doom_generation_fitness_score{metric_type=\"best\"}",
            "legendFormat": "Gen {{generation}} Best"
          }
        ]
      }
    ]
  }
}
```

### System Health Dashboard

```json
{
  "dashboard": {
    "title": "System Health",
    "panels": [
      {
        "title": "Container CPU Usage",
        "targets": [
          {
            "expr": "rate(container_cpu_usage_seconds_total{name=~\"doom-.*\"}[5m]) * 100",
            "legendFormat": "{{name}}"
          }
        ]
      },
      {
        "title": "Container Memory Usage",
        "targets": [
          {
            "expr": "container_memory_usage_bytes{name=~\"doom-.*\"} / 1024 / 1024",
            "legendFormat": "{{name}} (MB)"
          }
        ]
      },
      {
        "title": "NATS Message Throughput",
        "targets": [
          {
            "expr": "rate(clau_doom_nats_messages_published_total[1m]) * 60",
            "legendFormat": "{{subject}}"
          }
        ]
      },
      {
        "title": "OpenSearch Query Latency",
        "targets": [
          {
            "expr": "histogram_quantile(0.95, rate(clau_doom_opensearch_query_latency_seconds_bucket[5m]))",
            "legendFormat": "P95 - {{index}}"
          }
        ]
      }
    ]
  }
}
```

### Dashboard JSON Provisioning

```yaml
# docker/grafana/provisioning/dashboards/dashboard.yml
apiVersion: 1

providers:
  - name: 'clau-doom'
    orgId: 1
    folder: 'Research'
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /etc/grafana/provisioning/dashboards
```

```yaml
# docker-compose.yml
services:
  grafana:
    image: grafana/grafana:10.2.0
    ports:
      - "3001:3000"
    volumes:
      - ./docker/grafana/provisioning:/etc/grafana/provisioning
      - grafana-data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
```

## Docker Health Checks

### Health Check Patterns

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

  opensearch:
    healthcheck:
      test: ["CMD-SHELL", "curl -sf http://localhost:9200/_cluster/health | grep -q '\"status\":\"green\\|yellow\"'"]
      interval: 30s
      timeout: 10s
      retries: 5
```

### Custom Health Endpoints

```rust
// agent-core health endpoint
use axum::{routing::get, Json, Router};
use serde_json::json;

async fn health_handler() -> Json<serde_json::Value> {
    Json(json!({
        "status": "healthy",
        "timestamp": chrono::Utc::now().to_rfc3339(),
    }))
}

async fn readiness_handler() -> Result<Json<serde_json::Value>, StatusCode> {
    // Check dependencies
    if opensearch_client.ping().await.is_ok()
        && duckdb_connection.execute("SELECT 1").is_ok() {
        Ok(Json(json!({ "status": "ready" })))
    } else {
        Err(StatusCode::SERVICE_UNAVAILABLE)
    }
}

pub fn health_router() -> Router {
    Router::new()
        .route("/healthz", get(health_handler))
        .route("/readyz", get(readiness_handler))
}
```

```go
// Go orchestrator health endpoint
func (s *Server) Health(ctx context.Context, req *pb.HealthRequest) (*pb.HealthResponse, error) {
    return &pb.HealthResponse{
        Status: pb.HealthStatus_SERVING,
    }, nil
}
```

### Dependency Ordering with Health Checks

```yaml
services:
  orchestrator:
    depends_on:
      nats:
        condition: service_healthy
      opensearch:
        condition: service_healthy
      duckdb-init:
        condition: service_completed_successfully

  agent:
    depends_on:
      orchestrator:
        condition: service_healthy
```

## Alerting Rules

### Prometheus Alert Rules

```yaml
# docker/prometheus/alerts.yml
groups:
  - name: clau_doom_alerts
    interval: 30s
    rules:
      - alert: AgentDecisionLatencyHigh
        expr: histogram_quantile(0.99, rate(clau_doom_agent_decision_latency_seconds_bucket[5m])) > 0.100
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "Agent {{ $labels.agent_id }} decision latency > 100ms"
          description: "P99 latency is {{ $value }}s"

      - alert: ContainerRestartingFrequently
        expr: rate(clau_doom_container_restarts_total[15m]) > 0.2
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Container {{ $labels.service }} restarting frequently"
          description: "Restart rate: {{ $value }}/min"

      - alert: OpenSearchQueryLatencyHigh
        expr: histogram_quantile(0.95, rate(clau_doom_opensearch_query_latency_seconds_bucket[5m])) > 0.200
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "OpenSearch query latency > 200ms"
          description: "P95 latency is {{ $value }}s for index {{ $labels.index }}"

      - alert: NATSConsumerPendingHigh
        expr: nats_consumer_num_pending > 1000
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "NATS consumer has {{ $value }} pending messages"

      - alert: DuckDBDiskUsageHigh
        expr: (disk_used_bytes / disk_total_bytes) > 0.80
        for: 10m
        labels:
          severity: warning
        annotations:
          summary: "DuckDB disk usage > 80%"
          description: "{{ $value | humanizePercentage }} disk used"
```

### Integration with Alertmanager

```yaml
# docker/alertmanager/config.yml
global:
  resolve_timeout: 5m

route:
  receiver: 'default'
  group_by: ['alertname', 'severity']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 12h

receivers:
  - name: 'default'
    webhook_configs:
      - url: 'http://dashboard:3000/api/alerts'
```

This observability guide provides comprehensive patterns for monitoring the clau-doom multi-container research platform. All metrics, logs, and traces follow consistent naming and structured formats for unified analysis.
