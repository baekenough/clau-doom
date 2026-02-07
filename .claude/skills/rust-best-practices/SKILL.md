---
name: rust-best-practices
description: Idiomatic Rust patterns for agent-core development including ownership, async tokio, tonic gRPC, and performance optimization
user-invocable: false
---

# Rust Best Practices for clau-doom Agent Core

## Ownership and Borrowing Patterns

### Prefer Borrowing Over Cloning

```rust
// WRONG: unnecessary clone
fn process_state(state: GameState) -> Decision {
    let cloned = state.clone();
    analyze(&cloned)
}

// CORRECT: borrow when possible
fn process_state(state: &GameState) -> Decision {
    analyze(state)
}
```

### Use Cow for Conditional Ownership

```rust
use std::borrow::Cow;

fn normalize_action<'a>(action: &'a str) -> Cow<'a, str> {
    if action.contains(' ') {
        Cow::Owned(action.replace(' ', "_"))
    } else {
        Cow::Borrowed(action)
    }
}
```

### Builder Pattern for Complex Structs

```rust
pub struct AgentConfig {
    model_path: PathBuf,
    max_latency_ms: u64,
    rag_endpoint: String,
}

pub struct AgentConfigBuilder {
    model_path: Option<PathBuf>,
    max_latency_ms: u64,
    rag_endpoint: Option<String>,
}

impl AgentConfigBuilder {
    pub fn new() -> Self {
        Self {
            model_path: None,
            max_latency_ms: 100,
            rag_endpoint: None,
        }
    }

    pub fn model_path(mut self, path: impl Into<PathBuf>) -> Self {
        self.model_path = Some(path.into());
        self
    }

    pub fn max_latency_ms(mut self, ms: u64) -> Self {
        self.max_latency_ms = ms;
        self
    }

    pub fn build(self) -> Result<AgentConfig, AgentConfigError> {
        Ok(AgentConfig {
            model_path: self.model_path.ok_or(AgentConfigError::MissingModelPath)?,
            max_latency_ms: self.max_latency_ms,
            rag_endpoint: self.rag_endpoint.unwrap_or_else(|| "http://localhost:50051".into()),
        })
    }
}
```

## Error Handling

### Use thiserror for Library Errors

```rust
use thiserror::Error;

#[derive(Error, Debug)]
pub enum AgentCoreError {
    #[error("decision timeout: took {elapsed_ms}ms, limit {limit_ms}ms")]
    DecisionTimeout { elapsed_ms: u64, limit_ms: u64 },

    #[error("RAG query failed: {0}")]
    RagQueryFailed(#[from] tonic::Status),

    #[error("invalid game state: {reason}")]
    InvalidGameState { reason: String },

    #[error("scoring error: {0}")]
    ScoringError(#[from] ScoringError),
}
```

### Use anyhow for Application/Binary Errors

```rust
use anyhow::{Context, Result, bail};

async fn run_agent(config_path: &Path) -> Result<()> {
    let config = AgentConfig::load(config_path)
        .context("failed to load agent configuration")?;

    let agent = AgentCore::new(config)
        .await
        .context("failed to initialize agent core")?;

    if agent.model_version() < MIN_VERSION {
        bail!("model version {} is below minimum {}", agent.model_version(), MIN_VERSION);
    }

    agent.run().await.context("agent runtime error")
}
```

### Result Type Aliases

```rust
// In lib.rs - library-specific Result
pub type Result<T> = std::result::Result<T, AgentCoreError>;

// In decision engine module
pub fn decide(state: &GameState) -> Result<Action> {
    // Uses AgentCoreError automatically
}
```

## Async with Tokio

### Runtime Configuration

```rust
#[tokio::main]
async fn main() -> anyhow::Result<()> {
    // For the agent-core binary
    let runtime = tokio::runtime::Builder::new_multi_thread()
        .worker_threads(4)
        .enable_all()
        .build()?;

    runtime.block_on(run())
}
```

### Task Spawning and Channels

```rust
use tokio::sync::{mpsc, oneshot};

struct DecisionRequest {
    state: GameState,
    respond_to: oneshot::Sender<Decision>,
}

async fn decision_loop(mut rx: mpsc::Receiver<DecisionRequest>) {
    while let Some(req) = rx.recv().await {
        let decision = compute_decision(&req.state).await;
        let _ = req.respond_to.send(decision);
    }
}

async fn request_decision(
    tx: &mpsc::Sender<DecisionRequest>,
    state: GameState,
) -> Result<Decision> {
    let (respond_to, rx) = oneshot::channel();
    tx.send(DecisionRequest { state, respond_to })
        .await
        .map_err(|_| AgentCoreError::ChannelClosed)?;

    tokio::time::timeout(Duration::from_millis(100), rx)
        .await
        .map_err(|_| AgentCoreError::DecisionTimeout {
            elapsed_ms: 100,
            limit_ms: 100,
        })?
        .map_err(|_| AgentCoreError::ChannelClosed)
}
```

### Select for Multiple Futures

```rust
use tokio::select;

async fn agent_main_loop(
    mut game_rx: mpsc::Receiver<GameState>,
    mut shutdown_rx: oneshot::Receiver<()>,
) {
    loop {
        select! {
            Some(state) = game_rx.recv() => {
                handle_game_state(state).await;
            }
            _ = &mut shutdown_rx => {
                tracing::info!("shutdown signal received");
                break;
            }
        }
    }
}
```

## Tonic gRPC

### Service Definition (from .proto)

```rust
// Generated by tonic-build from agent.proto
// Server implementation
#[tonic::async_trait]
impl AgentService for AgentServer {
    async fn get_action(
        &self,
        request: Request<GameStateProto>,
    ) -> Result<Response<ActionProto>, Status> {
        let state: GameState = request.into_inner().try_into()
            .map_err(|e| Status::invalid_argument(format!("{e}")))?;

        let action = self.decision_engine.decide(&state)
            .await
            .map_err(|e| Status::internal(format!("{e}")))?;

        Ok(Response::new(action.into()))
    }

    type ObserveStream = ReceiverStream<Result<ObservationProto, Status>>;

    async fn observe(
        &self,
        request: Request<ObserveRequest>,
    ) -> Result<Response<Self::ObserveStream>, Status> {
        let (tx, rx) = mpsc::channel(128);
        let agent_id = request.into_inner().agent_id;

        tokio::spawn(async move {
            // Stream observations
        });

        Ok(Response::new(ReceiverStream::new(rx)))
    }
}
```

### Client with Retry

```rust
use tonic::transport::Channel;
use backoff::ExponentialBackoff;

async fn connect_with_retry(endpoint: &str) -> Result<AgentServiceClient<Channel>> {
    let backoff = ExponentialBackoff {
        max_elapsed_time: Some(Duration::from_secs(30)),
        ..Default::default()
    };

    backoff::future::retry(backoff, || async {
        AgentServiceClient::connect(endpoint.to_string())
            .await
            .map_err(backoff::Error::transient)
    })
    .await
    .context("failed to connect to agent service")
}
```

## Performance Patterns

### Zero-Cost Abstractions

```rust
// Use newtypes for type safety with zero runtime cost
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct AgentId(u32);

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct GenerationId(u32);

// Compile-time checked, same runtime cost as u32
fn get_agent_score(agent: AgentId, gen: GenerationId) -> f64 {
    // ...
}
```

### Avoid Unnecessary Allocations

```rust
// WRONG: allocates a Vec just to iterate
fn sum_scores(agents: &[Agent]) -> f64 {
    let scores: Vec<f64> = agents.iter().map(|a| a.score).collect();
    scores.iter().sum()
}

// CORRECT: iterator chain, zero allocation
fn sum_scores(agents: &[Agent]) -> f64 {
    agents.iter().map(|a| a.score).sum()
}
```

### Pre-allocate When Size Is Known

```rust
fn collect_actions(states: &[GameState]) -> Vec<Action> {
    let mut actions = Vec::with_capacity(states.len());
    for state in states {
        actions.push(decide(state));
    }
    actions
}
```

### Use SmallVec for Small Collections

```rust
use smallvec::SmallVec;

// Stack-allocated for <= 8 elements, heap for more
type ActionHistory = SmallVec<[Action; 8]>;
```

## Testing

### Unit Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_decision_basic_state() {
        let state = GameState::default();
        let decision = decide_sync(&state);
        assert!(matches!(decision, Action::MoveForward | Action::TurnLeft | Action::TurnRight));
    }

    #[tokio::test]
    async fn test_decision_engine_timeout() {
        let engine = DecisionEngine::new(DecisionConfig {
            max_latency_ms: 1, // impossibly short
            ..Default::default()
        });

        let result = engine.decide(&GameState::default()).await;
        assert!(matches!(result, Err(AgentCoreError::DecisionTimeout { .. })));
    }
}
```

### Integration Tests

```rust
// tests/integration/grpc_test.rs
#[tokio::test]
async fn test_agent_service_end_to_end() {
    let server = spawn_test_server().await;
    let mut client = AgentServiceClient::connect(server.addr()).await.unwrap();

    let response = client
        .get_action(GameStateProto::default())
        .await
        .unwrap();

    assert!(response.into_inner().action_id > 0);
}
```

### Benchmarks with Criterion

```rust
// benches/decision_bench.rs
use criterion::{criterion_group, criterion_main, Criterion};

fn bench_decision(c: &mut Criterion) {
    let state = GameState::sample();
    let engine = DecisionEngine::new_sync(Default::default());

    c.bench_function("decide_basic_state", |b| {
        b.iter(|| engine.decide_sync(criterion::black_box(&state)))
    });
}

criterion_group!(benches, bench_decision);
criterion_main!(benches);
```

## Project Structure

```
agent-core/
  Cargo.toml           # workspace root
  crates/
    agent-core/        # main decision engine
      src/
        lib.rs
        decision.rs
        state.rs
        error.rs
    scoring/           # fitness scoring
      src/
        lib.rs
        fitness.rs
        metrics.rs
    rag-client/        # RAG service client
      src/
        lib.rs
        client.rs
        embedding.rs
  proto/               # shared protobuf definitions
    agent.proto
    scoring.proto
  benches/
    decision_bench.rs
```

### Workspace Cargo.toml

```toml
[workspace]
members = ["crates/*"]
resolver = "2"

[workspace.dependencies]
tokio = { version = "1", features = ["full"] }
tonic = "0.12"
prost = "0.13"
thiserror = "2"
anyhow = "1"
tracing = "0.1"
tracing-subscriber = "0.3"
serde = { version = "1", features = ["derive"] }
```

## Unsafe Guidelines

- Minimize: use safe abstractions first, only use unsafe when measured performance gain justifies it
- Document every unsafe block with a `// SAFETY:` comment explaining the invariant
- Encapsulate unsafe code behind safe public APIs
- Test unsafe code with Miri (`cargo +nightly miri test`)
- Never use unsafe for convenience, only for performance-critical paths with benchmarks proving the need
