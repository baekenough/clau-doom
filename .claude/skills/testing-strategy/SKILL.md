---
name: testing-strategy
description: Cross-language test patterns for Rust, Go, Python, and TypeScript including integration testing with Docker, test data management, and coverage requirements
user-invocable: false
---

# Testing Strategy for clau-doom

## Testing Philosophy

### Test Pyramid

```
       /\      E2E (few)
      /  \     - Full system integration
     /----\    - Docker Compose environment
    /      \   - Expensive, slow, but high confidence
   /--------\
  / Integration \ (some)
 /    (some)     \  - Component integration
/----------------\  - Database, gRPC, NATS
/   Unit Tests    \ (many)
/     (many)       \ - Fast, isolated
/------------------\ - High coverage
```

### Core Principles

```yaml
determinism:
  - Fixed seeds for all random operations
  - No time-dependent tests (use mock clocks)
  - Reproducible test data generation
  - Idempotent test setup/teardown

speed:
  - Unit tests: < 1s total
  - Integration tests: < 30s total
  - E2E tests: < 5min total
  - Fail fast on first error

isolation:
  - No shared state between tests
  - Clean database/filesystem per test
  - Independent parallel execution
  - Cleanup on failure

clarity:
  - Test name describes scenario
  - Clear arrange/act/assert structure
  - Minimal mocking (prefer real implementations)
  - Self-documenting test data
```

## Rust Testing Patterns

### Unit Tests with #[cfg(test)]

```rust
// src/decision/scorer.rs
pub struct Scorer {
    weights: ScoringWeights,
}

impl Scorer {
    pub fn score(&self, state: &GameState) -> f64 {
        let kill_score = state.kills as f64 * self.weights.kill;
        let health_penalty = (100.0 - state.health) * self.weights.health_penalty;
        (kill_score - health_penalty).max(0.0)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn test_weights() -> ScoringWeights {
        ScoringWeights {
            kill: 10.0,
            health_penalty: 0.5,
            ammo_efficiency: 2.0,
        }
    }

    #[test]
    fn test_score_perfect_run() {
        let scorer = Scorer { weights: test_weights() };
        let state = GameState {
            kills: 10,
            deaths: 0,
            health: 100.0,
            ammo_used: 50,
        };

        let score = scorer.score(&state);
        assert_eq!(score, 100.0); // 10 kills * 10.0, no health penalty
    }

    #[test]
    fn test_score_damaged_agent() {
        let scorer = Scorer { weights: test_weights() };
        let state = GameState {
            kills: 5,
            deaths: 0,
            health: 50.0,
            ammo_used: 30,
        };

        let score = scorer.score(&state);
        assert_eq!(score, 25.0); // 50 - (50 * 0.5)
    }

    #[test]
    fn test_score_never_negative() {
        let scorer = Scorer { weights: test_weights() };
        let state = GameState {
            kills: 0,
            deaths: 10,
            health: 0.0,
            ammo_used: 100,
        };

        let score = scorer.score(&state);
        assert!(score >= 0.0);
    }
}
```

### Property-Based Testing with proptest

```rust
// tests/property_tests.rs
use proptest::prelude::*;
use agent_core::decision::*;

// Strategy: generate valid GameState
fn game_state_strategy() -> impl Strategy<Value = GameState> {
    (0..100u32, 0..10u32, 0.0..100.0f64, 0..500u32).prop_map(
        |(kills, deaths, health, ammo)| GameState {
            kills,
            deaths,
            health,
            ammo_used: ammo,
        },
    )
}

proptest! {
    #[test]
    fn score_always_non_negative(state in game_state_strategy()) {
        let scorer = Scorer::default();
        let score = scorer.score(&state);
        prop_assert!(score >= 0.0);
    }

    #[test]
    fn decision_always_valid(state in game_state_strategy()) {
        let engine = DecisionEngine::new(ScoringWeights::default());
        let decision = engine.decide(&state);

        // Decision must be one of valid actions
        prop_assert!(decision.action_id < 10);
    }

    #[test]
    fn more_kills_means_higher_score(
        kills1 in 0..50u32,
        kills2 in 50..100u32,
    ) {
        let scorer = Scorer::default();
        let state1 = GameState { kills: kills1, ..Default::default() };
        let state2 = GameState { kills: kills2, ..Default::default() };

        prop_assert!(scorer.score(&state2) > scorer.score(&state1));
    }
}
```

### Benchmarks with criterion

```rust
// benches/decision_bench.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion};
use agent_core::decision::DecisionEngine;
use agent_core::types::GameState;

fn decision_latency_benchmark(c: &mut Criterion) {
    let engine = DecisionEngine::new(ScoringWeights::default());
    let state = GameState {
        kills: 5,
        deaths: 1,
        health: 75.0,
        ammo_used: 30,
        enemy_visible: true,
        distance_to_enemy: 10.0,
    };

    c.bench_function("decision_engine_decide", |b| {
        b.iter(|| {
            let decision = engine.decide(black_box(&state));
            black_box(decision)
        })
    });
}

fn scoring_throughput_benchmark(c: &mut Criterion) {
    let scorer = Scorer::default();
    let states: Vec<GameState> = (0..1000)
        .map(|i| GameState {
            kills: i % 20,
            health: (i % 100) as f64,
            ..Default::default()
        })
        .collect();

    c.bench_function("scorer_1000_states", |b| {
        b.iter(|| {
            for state in &states {
                let score = scorer.score(black_box(state));
                black_box(score);
            }
        })
    });
}

criterion_group! {
    name = benches;
    config = Criterion::default()
        // Must meet < 100ms P99 latency requirement
        .measurement_time(std::time::Duration::from_secs(10))
        .sample_size(1000);
    targets = decision_latency_benchmark, scoring_throughput_benchmark
}
criterion_main!(benches);
```

### Integration Tests

```rust
// tests/integration_test.rs
use agent_core::grpc::AgentServiceServer;
use agent_core::storage::DuckDBStore;
use tonic::transport::Server;
use tempfile::TempDir;

#[tokio::test]
async fn test_grpc_server_decision_endpoint() {
    // Setup: temporary DuckDB
    let temp_dir = TempDir::new().unwrap();
    let db_path = temp_dir.path().join("test.db");
    let store = DuckDBStore::new(&db_path).await.unwrap();

    // Start gRPC server on random port
    let addr = "127.0.0.1:0".parse().unwrap();
    let service = AgentServiceServer::new(store);
    let server = Server::builder()
        .add_service(service.into_service())
        .serve(addr);

    let server_handle = tokio::spawn(server);

    // Wait for server ready (use health check)
    tokio::time::sleep(tokio::time::Duration::from_millis(100)).await;

    // Test: call GetAction RPC
    let mut client = AgentServiceClient::connect("http://127.0.0.1:50051")
        .await
        .unwrap();

    let request = tonic::Request::new(GetActionRequest {
        agent_id: "test-agent".to_string(),
        game_state: Some(GameStateProto {
            kills: 5,
            health: 75.0,
            ..Default::default()
        }),
    });

    let response = client.get_action(request).await.unwrap();

    // Assert: valid action returned
    assert!(response.into_inner().action_id < 10);

    // Cleanup
    server_handle.abort();
}
```

### Mocking with mockall

```rust
// src/rag/client.rs
#[cfg_attr(test, mockall::automock)]
pub trait RAGClient {
    async fn search_strategies(&self, query: &str) -> Result<Vec<Strategy>>;
}

// tests/decision_with_rag_test.rs
#[cfg(test)]
mod tests {
    use super::*;
    use mockall::predicate::*;

    #[tokio::test]
    async fn test_decision_with_rag_strategies() {
        let mut mock_rag = MockRAGClient::new();

        mock_rag
            .expect_search_strategies()
            .with(eq("aggressive combat"))
            .times(1)
            .returning(|_| {
                Ok(vec![Strategy {
                    name: "rush".to_string(),
                    weight: 0.8,
                }])
            });

        let engine = DecisionEngine::new_with_rag(mock_rag);
        let decision = engine.decide_with_context(&test_state, "aggressive combat").await;

        assert!(decision.is_ok());
    }
}
```

## Go Testing Patterns

### Table-Driven Tests

```go
// internal/orchestrator/scoring_test.go
package orchestrator

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestCalculateFitness(t *testing.T) {
    tests := []struct {
        name      string
        metrics   AgentMetrics
        expected  float64
        wantErr   bool
    }{
        {
            name: "perfect_run",
            metrics: AgentMetrics{
                Kills:        10,
                Deaths:       0,
                SurvivalTime: 300.0,
                AmmoUsed:     50,
            },
            expected: 1.0,
            wantErr:  false,
        },
        {
            name: "average_performance",
            metrics: AgentMetrics{
                Kills:        5,
                Deaths:       3,
                SurvivalTime: 150.0,
                AmmoUsed:     100,
            },
            expected: 0.45,
            wantErr:  false,
        },
        {
            name: "zero_survival",
            metrics: AgentMetrics{
                Kills:        0,
                Deaths:       10,
                SurvivalTime: 0.0,
                AmmoUsed:     0,
            },
            expected: 0.0,
            wantErr:  false,
        },
        {
            name: "invalid_negative_kills",
            metrics: AgentMetrics{
                Kills:        -5,
                Deaths:       0,
                SurvivalTime: 100.0,
                AmmoUsed:     50,
            },
            expected: 0.0,
            wantErr:  true,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result, err := CalculateFitness(tt.metrics)

            if tt.wantErr {
                assert.Error(t, err)
                return
            }

            assert.NoError(t, err)
            assert.InDelta(t, tt.expected, result, 0.01)
        })
    }
}
```

### Test Helpers

```go
// internal/orchestrator/testutil/helpers.go
package testutil

import (
    "context"
    "testing"
    "time"
    "github.com/stretchr/testify/require"
)

// NewTestOrchestrator creates an orchestrator for testing
func NewTestOrchestrator(t *testing.T) *Orchestrator {
    t.Helper()

    config := &Config{
        GRPCPort:      getRandomPort(),
        NATSUrl:       "nats://localhost:4222",
        DockerNetwork: "test-network",
    }

    orch, err := New(config)
    require.NoError(t, err, "failed to create test orchestrator")

    t.Cleanup(func() {
        ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
        defer cancel()
        _ = orch.Shutdown(ctx)
    })

    return orch
}

// CreateTestAgent creates a test agent with default configuration
func CreateTestAgent(t *testing.T, id string) *Agent {
    t.Helper()

    return &Agent{
        ID:         AgentID(id),
        Generation: 0,
        Genome: Genome{
            Memory:    0.5,
            Strength:  0.5,
            Curiosity: 0.5,
        },
        CreatedAt: time.Now(),
    }
}
```

### Interface Mocking with gomock

```go
// Generate mocks:
//go:generate mockgen -source=container_manager.go -destination=mock_container_manager.go -package=orchestrator

// internal/orchestrator/orchestrator_test.go
func TestSpawnAgentContainers(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockContainer := NewMockContainerManager(ctrl)

    // Expect SpawnAgent called 3 times
    mockContainer.EXPECT().
        SpawnAgent(gomock.Any(), gomock.Any(), gomock.Any()).
        DoAndReturn(func(ctx context.Context, id string, config AgentConfig) (string, error) {
            return fmt.Sprintf("container-%s", id), nil
        }).
        Times(3)

    orch := &Orchestrator{containerMgr: mockContainer}

    agents := []Agent{
        {ID: "agent-1"},
        {ID: "agent-2"},
        {ID: "agent-3"},
    }

    err := orch.spawnAgents(context.Background(), agents)
    require.NoError(t, err)
}
```

### Integration Tests with Build Tags

```go
//go:build integration
// +build integration

// tests/integration/nats_test.go
package integration

import (
    "context"
    "testing"
    "time"

    "github.com/nats-io/nats.go"
    "github.com/stretchr/testify/require"
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

func TestNATSPubSub(t *testing.T) {
    ctx := context.Background()

    // Start NATS container
    req := testcontainers.ContainerRequest{
        Image:        "nats:latest",
        ExposedPorts: []string{"4222/tcp"},
        WaitingFor:   wait.ForListeningPort("4222/tcp"),
    }

    natsContainer, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: req,
        Started:          true,
    })
    require.NoError(t, err)
    defer natsContainer.Terminate(ctx)

    // Get NATS endpoint
    endpoint, err := natsContainer.Endpoint(ctx, "")
    require.NoError(t, err)

    // Connect to NATS
    nc, err := nats.Connect(fmt.Sprintf("nats://%s", endpoint))
    require.NoError(t, err)
    defer nc.Close()

    // Test pub/sub
    received := make(chan string, 1)
    _, err = nc.Subscribe("test.events", func(msg *nats.Msg) {
        received <- string(msg.Data)
    })
    require.NoError(t, err)

    err = nc.Publish("test.events", []byte("hello"))
    require.NoError(t, err)

    select {
    case msg := <-received:
        require.Equal(t, "hello", msg)
    case <-time.After(2 * time.Second):
        t.Fatal("timeout waiting for message")
    }
}
```

### gRPC Testing with bufconn

```go
// internal/grpc/server_test.go
package grpc

import (
    "context"
    "net"
    "testing"

    "github.com/stretchr/testify/require"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"
    "google.golang.org/grpc/test/bufconn"

    pb "clau-doom/pkg/proto"
)

const bufSize = 1024 * 1024

var lis *bufconn.Listener

func bufDialer(context.Context, string) (net.Conn, error) {
    return lis.Dial()
}

func TestOrchestratorServer_StartExperiment(t *testing.T) {
    lis = bufconn.Listen(bufSize)
    s := grpc.NewServer()

    orch := NewTestOrchestrator(t)
    pb.RegisterOrchestratorServiceServer(s, &orchestratorServer{orchestrator: orch})

    go func() {
        if err := s.Serve(lis); err != nil {
            t.Logf("Server exited with error: %v", err)
        }
    }()
    defer s.Stop()

    // Create client
    ctx := context.Background()
    conn, err := grpc.DialContext(ctx, "bufnet",
        grpc.WithContextDialer(bufDialer),
        grpc.WithTransportCredentials(insecure.NewCredentials()))
    require.NoError(t, err)
    defer conn.Close()

    client := pb.NewOrchestratorServiceClient(conn)

    // Test StartExperiment
    resp, err := client.StartExperiment(ctx, &pb.StartExperimentRequest{
        Config: &pb.ExperimentConfig{
            Generations:    10,
            PopulationSize: 50,
        },
    })

    require.NoError(t, err)
    require.NotEmpty(t, resp.ExperimentId)
}
```

## Python Testing Patterns

### pytest Framework

```python
# tests/conftest.py
import pytest
import duckdb
from pathlib import Path

@pytest.fixture(scope="session")
def test_data_dir():
    """Shared test data directory"""
    return Path(__file__).parent / "testdata"

@pytest.fixture(scope="function")
def duckdb_conn():
    """In-memory DuckDB connection for each test"""
    conn = duckdb.connect(":memory:")

    # Setup schema
    conn.execute("""
        CREATE TABLE experiments (
            run_id INTEGER,
            agent_id VARCHAR,
            kills INTEGER,
            deaths INTEGER,
            survival_time REAL,
            seed INTEGER
        )
    """)

    yield conn
    conn.close()

@pytest.fixture(scope="function")
def experiment_data(duckdb_conn):
    """Insert test experiment data"""
    data = [
        (1, "agent-A", 10, 2, 180.5, 42),
        (1, "agent-A", 8, 3, 165.0, 1337),
        (1, "agent-B", 5, 5, 120.0, 42),
        (1, "agent-B", 7, 4, 140.5, 1337),
    ]

    duckdb_conn.executemany(
        "INSERT INTO experiments VALUES (?, ?, ?, ?, ?, ?)",
        data
    )

    return duckdb_conn

@pytest.fixture
def vizdoom_mock():
    """Mock VizDoom game instance"""
    from unittest.mock import Mock

    game = Mock()
    game.get_state.return_value = Mock(
        number=1,
        game_variables=[100.0, 50, 10]  # health, ammo, kills
    )
    game.is_episode_finished.return_value = False
    game.make_action.return_value = 0.5

    return game
```

### Parametrized Tests

```python
# tests/test_anova.py
import pytest
import pandas as pd
from analytics.anova import run_factorial_anova

@pytest.mark.parametrize("memory,strength,expected_kills", [
    (0.5, 0.3, 5.0),
    (0.7, 0.3, 8.0),
    (0.9, 0.3, 12.0),
    (0.5, 0.5, 7.0),
    (0.7, 0.5, 11.0),
    (0.9, 0.5, 15.0),
])
def test_factorial_design_cells(memory, strength, expected_kills, duckdb_conn):
    """Test each cell of 2x3 factorial design"""
    # Insert test data for this cell
    duckdb_conn.execute("""
        INSERT INTO experiments (run_id, agent_id, kills, memory, strength)
        VALUES (?, ?, ?, ?, ?)
    """, [1, f"agent-{memory}-{strength}", expected_kills, memory, strength])

    # Query and verify
    result = duckdb_conn.execute("""
        SELECT AVG(kills) as avg_kills
        FROM experiments
        WHERE memory = ? AND strength = ?
    """, [memory, strength]).fetchone()

    assert result[0] == pytest.approx(expected_kills, rel=0.1)

@pytest.mark.parametrize("alpha,expected_significant", [
    (0.05, ["Memory", "Strength"]),
    (0.01, ["Memory"]),  # Only memory significant at stricter alpha
])
def test_anova_significance_levels(alpha, expected_significant, experiment_data):
    """Test ANOVA with different significance levels"""
    result = run_factorial_anova(
        experiment_data,
        factors=["Memory", "Strength"],
        response="kills",
        alpha=alpha
    )

    significant = [f for f, p in result.p_values.items() if p < alpha]
    assert set(significant) == set(expected_significant)
```

### Statistical Testing with Known Results

```python
# tests/test_statistical_analysis.py
import numpy as np
from scipy import stats
from analytics.anova import run_anova, check_residuals

def test_anova_known_dataset():
    """Test ANOVA with dataset with known F-statistic and p-value"""
    # Dataset from Montgomery, Design and Analysis of Experiments, p. 76
    data = pd.DataFrame({
        'temperature': [150, 150, 150, 170, 170, 170, 190, 190, 190],
        'yield': [28, 25, 27, 36, 32, 34, 18, 19, 23],
    })

    result = run_anova(data, factor='temperature', response='yield')

    # Expected values from textbook
    assert result['F_statistic'] == pytest.approx(39.0, rel=0.01)
    assert result['p_value'] < 0.001
    assert result['df_between'] == 2
    assert result['df_within'] == 6

def test_residual_diagnostics_normal_data():
    """Test residual diagnostics on known normal residuals"""
    # Generate normal residuals
    np.random.seed(42)
    residuals = np.random.normal(0, 1, 100)

    diagnostics = check_residuals(residuals)

    # Anderson-Darling test should not reject normality
    assert diagnostics['normality_p'] > 0.05

    # Variance should be close to 1.0
    assert np.var(residuals) == pytest.approx(1.0, abs=0.2)

def test_power_analysis():
    """Test statistical power calculation"""
    from analytics.power import calculate_power

    # Small effect size (Cohen's d = 0.3) with n=30
    power = calculate_power(effect_size=0.3, n=30, alpha=0.05)
    assert power == pytest.approx(0.47, abs=0.05)

    # Large effect size (Cohen's d = 0.8) with n=30
    power = calculate_power(effect_size=0.8, n=30, alpha=0.05)
    assert power == pytest.approx(0.93, abs=0.05)
```

### hypothesis for Property-Based Testing

```python
# tests/test_properties.py
from hypothesis import given, strategies as st, settings
from analytics.scoring import calculate_fitness

@given(
    kills=st.integers(min_value=0, max_value=100),
    deaths=st.integers(min_value=0, max_value=50),
    survival_time=st.floats(min_value=0.0, max_value=600.0, allow_nan=False),
)
@settings(max_examples=200, deadline=None)
def test_fitness_always_in_range(kills, deaths, survival_time):
    """Fitness score must always be between 0.0 and 1.0"""
    fitness = calculate_fitness(kills, deaths, survival_time)

    assert 0.0 <= fitness <= 1.0
    assert not np.isnan(fitness)

@given(
    kills1=st.integers(min_value=0, max_value=50),
    kills2=st.integers(min_value=50, max_value=100),
)
def test_more_kills_higher_fitness(kills1, kills2):
    """More kills should always result in higher fitness (all else equal)"""
    fitness1 = calculate_fitness(kills1, deaths=5, survival_time=100.0)
    fitness2 = calculate_fitness(kills2, deaths=5, survival_time=100.0)

    assert fitness2 > fitness1
```

### Mocking with unittest.mock

```python
# tests/test_vizdoom_integration.py
from unittest.mock import Mock, patch, call
import pytest
from agent.executor import run_episode

def test_run_episode_with_mock_vizdoom():
    """Test episode execution with mocked VizDoom"""
    with patch('vizdoom.DoomGame') as MockGame:
        mock_game = MockGame.return_value
        mock_game.get_state.return_value = Mock(
            number=1,
            game_variables=[100.0, 50, 0]  # health, ammo, kills
        )
        mock_game.is_episode_finished.return_value = False
        mock_game.get_available_buttons_size.return_value = 5

        # Run episode
        result = run_episode(
            game=mock_game,
            agent_config={'memory': 0.7, 'strength': 0.5},
            seed=42,
            max_steps=100
        )

        # Verify game methods called
        mock_game.init.assert_called_once()
        mock_game.new_episode.assert_called_once()
        assert mock_game.make_action.call_count > 0

        # Verify result structure
        assert 'kills' in result
        assert 'survival_time' in result
        assert result['seed'] == 42
```

## TypeScript Testing Patterns

### vitest with describe/it/expect

```typescript
// src/components/ExperimentDashboard.test.ts
import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ExperimentDashboard } from './ExperimentDashboard';
import { mockExperimentData } from '../testdata/experiments';

describe('ExperimentDashboard', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders experiment summary correctly', () => {
    render(<ExperimentDashboard experimentId="DOE-042" />);

    expect(screen.getByText('DOE-042')).toBeInTheDocument();
    expect(screen.getByText('2x3 Factorial Design')).toBeInTheDocument();
  });

  it('displays generation progress', async () => {
    const { container } = render(<ExperimentDashboard experimentId="DOE-042" />);

    await waitFor(() => {
      const progressBar = container.querySelector('[role="progressbar"]');
      expect(progressBar).toHaveAttribute('aria-valuenow', '5');
      expect(progressBar).toHaveAttribute('aria-valuemax', '10');
    });
  });

  it('handles start experiment action', async () => {
    const user = userEvent.setup();
    const onStart = vi.fn();

    render(<ExperimentDashboard experimentId="DOE-042" onStart={onStart} />);

    const startButton = screen.getByRole('button', { name: /start/i });
    await user.click(startButton);

    expect(onStart).toHaveBeenCalledOnce();
    expect(onStart).toHaveBeenCalledWith('DOE-042');
  });
});
```

### React Testing Library

```typescript
// src/components/AgentCard.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { AgentCard } from './AgentCard';

describe('AgentCard', () => {
  const mockAgent = {
    id: 'agent-A',
    generation: 5,
    fitness: 0.82,
    genome: {
      memory: 0.7,
      strength: 0.5,
      curiosity: 0.6,
    },
  };

  it('displays agent information', () => {
    render(<AgentCard agent={mockAgent} />);

    expect(screen.getByText('agent-A')).toBeInTheDocument();
    expect(screen.getByText('Generation 5')).toBeInTheDocument();
    expect(screen.getByText('Fitness: 0.82')).toBeInTheDocument();
  });

  it('shows genome parameters on expand', async () => {
    const user = userEvent.setup();
    render(<AgentCard agent={mockAgent} />);

    const expandButton = screen.getByRole('button', { name: /expand/i });
    await user.click(expandButton);

    await waitFor(() => {
      expect(screen.getByText('Memory: 0.7')).toBeInTheDocument();
      expect(screen.getByText('Strength: 0.5')).toBeInTheDocument();
      expect(screen.getByText('Curiosity: 0.6')).toBeInTheDocument();
    });
  });
});
```

### MSW (Mock Service Worker)

```typescript
// src/mocks/handlers.ts
import { rest } from 'msw';

export const handlers = [
  rest.get('/api/experiments/:id', (req, res, ctx) => {
    const { id } = req.params;

    return res(
      ctx.status(200),
      ctx.json({
        id,
        status: 'running',
        generation: 5,
        totalGenerations: 10,
        agents: [
          { id: 'agent-A', fitness: 0.82 },
          { id: 'agent-B', fitness: 0.75 },
        ],
      })
    );
  }),

  rest.post('/api/experiments/:id/start', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({ message: 'Experiment started' })
    );
  }),

  rest.ws('/api/events', (req, res, ctx) => {
    // WebSocket mock
    return res(
      ctx.data({
        type: 'GENERATION_COMPLETE',
        generation: 6,
        bestFitness: 0.85,
      })
    );
  }),
];

// src/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';

export const server = setupServer(...handlers);
```

### Test Setup with MSW

```typescript
// src/setupTests.ts
import { beforeAll, afterEach, afterAll } from 'vitest';
import { server } from './mocks/server';

beforeAll(() => server.listen({ onUnhandledRequest: 'error' }));
afterEach(() => server.resetHandlers());
afterAll(() => server.close());

// src/components/ExperimentList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { server } from '../mocks/server';
import { rest } from 'msw';
import { ExperimentList } from './ExperimentList';

describe('ExperimentList with API', () => {
  it('fetches and displays experiments', async () => {
    render(<ExperimentList />);

    await waitFor(() => {
      expect(screen.getByText('DOE-042')).toBeInTheDocument();
      expect(screen.getByText('Generation 5/10')).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    server.use(
      rest.get('/api/experiments/:id', (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: 'Server error' }));
      })
    );

    render(<ExperimentList />);

    await waitFor(() => {
      expect(screen.getByText(/error loading experiments/i)).toBeInTheDocument();
    });
  });
});
```

## Integration Testing with Docker

### docker-compose.test.yml

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  opensearch-test:
    image: opensearchproject/opensearch:2.11.0
    environment:
      - discovery.type=single-node
      - plugins.security.disabled=true
      - "OPENSEARCH_JAVA_OPTS=-Xms512m -Xmx512m"
    ports:
      - "9201:9200"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 10

  mongodb-test:
    image: mongo:7.0
    ports:
      - "27018:27017"
    healthcheck:
      test: ["CMD", "mongosh", "--eval", "db.adminCommand('ping')"]
      interval: 5s
      timeout: 3s
      retries: 10

  nats-test:
    image: nats:latest
    ports:
      - "4223:4222"
    healthcheck:
      test: ["CMD", "nats", "rtt"]
      interval: 3s
      timeout: 2s
      retries: 10

  duckdb-test:
    build:
      context: .
      dockerfile: Dockerfile.duckdb-test
    volumes:
      - ./testdata:/testdata
    command: ["sleep", "infinity"]
```

### Service Health Check Script

```bash
#!/bin/bash
# scripts/wait-for-services.sh

set -e

wait_for_service() {
    local service=$1
    local max_attempts=30
    local attempt=0

    echo "Waiting for $service..."

    while [ $attempt -lt $max_attempts ]; do
        if docker-compose -f docker-compose.test.yml ps $service | grep -q "healthy"; then
            echo "$service is ready"
            return 0
        fi

        attempt=$((attempt + 1))
        sleep 1
    done

    echo "Timeout waiting for $service"
    return 1
}

wait_for_service opensearch-test
wait_for_service mongodb-test
wait_for_service nats-test

echo "All services ready"
```

### Integration Test Runner

```python
# tests/integration/conftest.py
import pytest
import subprocess
import time
import os

@pytest.fixture(scope="session", autouse=True)
def docker_services():
    """Start Docker services for integration tests"""
    # Check if running in CI (services may already be running)
    if os.getenv("CI"):
        yield
        return

    # Start services
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.test.yml", "up", "-d"],
        check=True
    )

    # Wait for health checks
    subprocess.run(
        ["./scripts/wait-for-services.sh"],
        check=True
    )

    yield

    # Cleanup
    subprocess.run(
        ["docker-compose", "-f", "docker-compose.test.yml", "down", "-v"],
        check=True
    )
```

### GitHub Actions CI Configuration

```yaml
# .github/workflows/test.yml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      opensearch:
        image: opensearchproject/opensearch:2.11.0
        env:
          discovery.type: single-node
          plugins.security.disabled: true
        ports:
          - 9200:9200
        options: >-
          --health-cmd "curl -f http://localhost:9200/_cluster/health"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10

      mongodb:
        image: mongo:7.0
        ports:
          - 27017:27017
        options: >-
          --health-cmd "mongosh --eval 'db.adminCommand(\"ping\")'"
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10

      nats:
        image: nats:latest
        ports:
          - 4222:4222

    steps:
      - uses: actions/checkout@v3

      - name: Run Rust tests
        run: |
          cd agent-core
          cargo test --all-features

      - name: Run Go tests
        run: |
          cd orchestrator
          go test -v -race -coverprofile=coverage.out ./...

      - name: Run Python tests
        run: |
          cd analytics
          pytest --cov=analytics --cov-report=xml

      - name: Run TypeScript tests
        run: |
          cd dashboard
          npm test -- --coverage
```

## Test Data Management

### Directory Structure

```
testdata/
├── agent/
│   ├── decision_engine/
│   │   ├── normal_gameplay.json
│   │   ├── emergency_low_health.json
│   │   └── enemy_encounter.json
│   └── rag/
│       ├── strategy_docs.json
│       └── mock_embeddings.npy
├── experiments/
│   ├── DOE-021/
│   │   ├── design.yaml
│   │   ├── raw_data.csv
│   │   └── expected_anova.json
│   ├── DOE-022/
│   │   └── ...
│   └── golden/
│       ├── factorial_2x3_report.md
│       └── ccd_3factor_report.md
├── anova/
│   ├── known_f_statistic.csv
│   ├── heterogeneous_variance.csv
│   └── non_normal_residuals.csv
└── seeds/
    ├── generation_001.txt
    ├── generation_002.txt
    └── ...
```

### Seed-Based Test Data Generation

```python
# testdata/generate_doe_data.py
import numpy as np
import pandas as pd

def generate_factorial_data(
    factors: dict[str, list[float]],
    effects: dict[str, float],
    interaction_effect: float,
    n_replicates: int,
    seed: int,
) -> pd.DataFrame:
    """
    Generate test data for factorial design with known effects.

    Args:
        factors: {'memory': [0.5, 0.7, 0.9], 'strength': [0.3, 0.5]}
        effects: {'memory': 10.0, 'strength': 5.0}  # Effect sizes
        interaction_effect: 3.0
        n_replicates: 30
        seed: 42

    Returns:
        DataFrame with columns: memory, strength, kills
    """
    np.random.seed(seed)

    rows = []
    for memory in factors['memory']:
        for strength in factors['strength']:
            # Calculate true mean with interaction
            mean_kills = (
                50.0 +  # baseline
                effects['memory'] * memory +
                effects['strength'] * strength +
                interaction_effect * memory * strength
            )

            # Add noise
            kills = np.random.normal(mean_kills, 2.0, n_replicates)

            for k in kills:
                rows.append({
                    'memory': memory,
                    'strength': strength,
                    'kills': max(0, int(k))  # Kills can't be negative
                })

    return pd.DataFrame(rows)

# Generate and save
if __name__ == "__main__":
    data = generate_factorial_data(
        factors={'memory': [0.5, 0.7, 0.9], 'strength': [0.3, 0.5]},
        effects={'memory': 10.0, 'strength': 5.0},
        interaction_effect=3.0,
        n_replicates=30,
        seed=42,
    )

    data.to_csv('testdata/experiments/DOE-021/raw_data.csv', index=False)
```

### Golden File Testing

```python
# tests/test_report_generation.py
import pytest
from pathlib import Path
from analytics.reporting import generate_anova_report

def test_factorial_report_matches_golden(experiment_data):
    """Test that generated report matches golden file"""
    report = generate_anova_report(
        experiment_data,
        experiment_id="DOE-021",
        design_type="2x3 Factorial"
    )

    golden_path = Path("testdata/experiments/golden/factorial_2x3_report.md")
    golden_content = golden_path.read_text()

    # Compare (ignore timestamps and run IDs)
    report_normalized = normalize_report(report)
    golden_normalized = normalize_report(golden_content)

    assert report_normalized == golden_normalized

def normalize_report(content: str) -> str:
    """Remove dynamic fields for comparison"""
    import re

    # Remove timestamps
    content = re.sub(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}', 'TIMESTAMP', content)

    # Remove run IDs
    content = re.sub(r'Run ID: \d+', 'Run ID: XXX', content)

    return content
```

## Coverage Requirements

### Rust: cargo-llvm-cov

```toml
# Cargo.toml
[dev-dependencies]
cargo-llvm-cov = "0.6"

# Run coverage
# cargo llvm-cov --html --open
```

### Go: Built-in Coverage

```bash
# Run tests with coverage
go test -coverprofile=coverage.out ./...

# View coverage report
go tool cover -html=coverage.out

# Enforce minimum coverage in CI
go test -coverprofile=coverage.out ./...
go tool cover -func=coverage.out | grep total | awk '{if ($3+0 < 75.0) exit 1}'
```

### Python: pytest-cov

```ini
# pytest.ini
[pytest]
addopts =
    --cov=analytics
    --cov-report=term-missing
    --cov-report=html
    --cov-fail-under=85
```

### TypeScript: vitest

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'lcov'],
      lines: 70,
      functions: 70,
      branches: 70,
      statements: 70,
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.test.ts',
        '**/*.test.tsx',
      ],
    },
  },
});
```

## Anti-Patterns to Avoid

### ❌ Testing Implementation Details

```typescript
// BAD: Testing internal state
it('sets loading state correctly', () => {
  const component = render(<ExperimentList />);
  expect(component.instance().state.loading).toBe(true);
});

// GOOD: Testing observable behavior
it('shows loading spinner while fetching', async () => {
  render(<ExperimentList />);
  expect(screen.getByRole('progressbar')).toBeInTheDocument();

  await waitFor(() => {
    expect(screen.queryByRole('progressbar')).not.toBeInTheDocument();
  });
});
```

### ❌ Flaky Tests with Timing

```python
# BAD: Time-dependent test
def test_experiment_duration():
    start = time.time()
    run_experiment()
    duration = time.time() - start
    assert duration < 5.0  # Flaky on slow CI

# GOOD: Mock time or measure operations
def test_experiment_completes():
    with patch('time.time', side_effect=[0.0, 10.0, 20.0]):
        result = run_experiment()
        assert result.duration == 20.0
```

### ❌ Shared Mutable State

```go
// BAD: Global state shared between tests
var testDB *sql.DB

func TestQuery1(t *testing.T) {
    testDB.Exec("INSERT INTO users ...")  // Affects other tests
}

// GOOD: Fresh database per test
func TestQuery1(t *testing.T) {
    db := newTestDB(t)  // Clean database
    defer db.Close()

    db.Exec("INSERT INTO users ...")
}
```

### ❌ Testing Framework Code

```rust
// BAD: Testing that HashMap works
#[test]
fn test_hashmap_insertion() {
    let mut map = HashMap::new();
    map.insert("key", "value");
    assert_eq!(map.get("key"), Some(&"value"));
}

// GOOD: Testing business logic
#[test]
fn test_agent_registry_tracks_active_agents() {
    let mut registry = AgentRegistry::new();
    registry.register(Agent::new("agent-1"));

    assert_eq!(registry.active_count(), 1);
    assert!(registry.is_active("agent-1"));
}
```

### ❌ Ignoring Test Failures in CI

```yaml
# BAD: Continue on test failure
- name: Run tests
  run: cargo test || true  # DON'T DO THIS

# GOOD: Fail fast
- name: Run tests
  run: cargo test
```

## Summary

| Language | Framework | Key Patterns | Coverage Target |
|----------|-----------|--------------|-----------------|
| Rust | cargo test, proptest, criterion | Unit, property, benchmarks, integration | 80% |
| Go | testing, testify, gomock | Table-driven, interfaces, bufconn | 75% |
| Python | pytest, hypothesis | Fixtures, parametrize, mocking | 85% |
| TypeScript | vitest, RTL, MSW | Components, API mocks, user events | 70% |

All tests must be:
- **Deterministic** (fixed seeds, no time dependencies)
- **Fast** (unit < 1s, integration < 30s)
- **Isolated** (no shared state)
- **Clear** (descriptive names, obvious assertions)
