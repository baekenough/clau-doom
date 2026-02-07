# Testing Reference Guide

Comprehensive testing strategies across the clau-doom multi-language stack: Rust agent-core, Go orchestrator, Python analytics, and TypeScript dashboard.

## Key Resources

### Rust Testing
- [The Rust Programming Language - Testing](https://doc.rust-lang.org/book/ch11-00-testing.html)
- [Criterion.rs Benchmarking](https://bheisler.github.io/criterion.rs/book/)
- [proptest Property Testing](https://altsysrq.github.io/proptest-book/)
- [mockall Mocking](https://docs.rs/mockall/latest/mockall/)

### Go Testing
- [Go Testing Package](https://pkg.go.dev/testing)
- [testify Assertions](https://github.com/stretchr/testify)
- [gomock Mocking](https://github.com/golang/mock)
- [testcontainers-go](https://golang.testcontainers.org/)

### Python Testing
- [pytest Documentation](https://docs.pytest.org/)
- [hypothesis Property Testing](https://hypothesis.readthedocs.io/)
- [pytest-cov Coverage](https://pytest-cov.readthedocs.io/)
- [unittest.mock](https://docs.python.org/3/library/unittest.mock.html)

### TypeScript Testing
- [Vitest Testing Framework](https://vitest.dev/)
- [React Testing Library](https://testing-library.com/react)
- [MSW Mock Service Worker](https://mswjs.io/)
- [Testing Library User Event](https://testing-library.com/docs/user-event/intro)

## clau-doom Context

The clau-doom project requires rigorous testing across multiple languages and integration points:

### Multi-Language Stack
```
Rust agent-core     → <100ms decision latency, strategy scoring
Go orchestrator     → Agent lifecycle, generation management, gRPC API
Python analytics    → ANOVA, DOE analysis, data processing
TypeScript dashboard → Real-time visualization, WebSocket streams
```

### Performance Requirements
- **Agent decision latency**: < 100ms P99 (tested via criterion benchmarks)
- **RAG vector search**: < 100ms P99 (OpenSearch integration tests)
- **Frame processing**: < 200ms P99 (end-to-end integration tests)

### Reproducibility Requirements
- Fixed seed sets for all test scenarios
- Deterministic test data generation
- Statistical validation of test outputs
- Docker container test isolation

## Rust Testing

### Built-in Test Framework

```rust
// src/agent/decision.rs
#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_decision_basic_combat() {
        let game_state = GameState {
            health: 100.0,
            ammo: 50,
            enemy_visible: true,
            enemy_distance: 300.0,
        };

        let decision = DecisionEngine::new().decide(&game_state);

        assert_eq!(decision.action, Action::Attack);
        assert!(decision.confidence > 0.7);
    }

    #[test]
    #[should_panic(expected = "Invalid health value")]
    fn test_invalid_health() {
        let state = GameState {
            health: -10.0,
            ..Default::default()
        };
        DecisionEngine::new().decide(&state);
    }
}
```

### Integration Tests

```rust
// tests/scoring_integration.rs
use clau_doom_agent::{DecisionEngine, ScoringEngine, GameState};

#[test]
fn test_full_decision_pipeline() {
    let engine = DecisionEngine::new();
    let scorer = ScoringEngine::new();

    let states = vec![
        GameState::combat_scenario(),
        GameState::exploration_scenario(),
        GameState::retreat_scenario(),
    ];

    for state in states {
        let decision = engine.decide(&state);
        let score = scorer.score(&decision, &state);

        assert!(score >= 0.0 && score <= 1.0);
    }
}
```

### Criterion Benchmarks

```rust
// benches/decision_latency.rs
use criterion::{black_box, criterion_group, criterion_main, Criterion, BenchmarkId};
use clau_doom_agent::{DecisionEngine, GameState};

fn bench_decision_engine(c: &mut Criterion) {
    let mut group = c.benchmark_group("decision_latency");
    group.sample_size(1000);

    // P99 must be < 100ms
    group.throughput(criterion::Throughput::Elements(1));

    let engine = DecisionEngine::new();
    let state = GameState::default();

    group.bench_function("basic_decision", |b| {
        b.iter(|| {
            engine.decide(black_box(&state))
        });
    });

    group.bench_with_input(
        BenchmarkId::new("rag_search", "5_strategies"),
        &5,
        |b, &strategy_count| {
            let engine = DecisionEngine::with_strategies(strategy_count);
            b.iter(|| engine.decide_with_rag(black_box(&state)))
        },
    );

    group.finish();
}

criterion_group!(benches, bench_decision_engine);
criterion_main!(benches);
```

### Property-Based Testing with proptest

```rust
// src/scoring/mod.rs
#[cfg(test)]
mod proptests {
    use super::*;
    use proptest::prelude::*;

    proptest! {
        #[test]
        fn score_always_normalized(
            kills in 0u32..1000,
            deaths in 0u32..100,
            health in 0.0f64..100.0
        ) {
            let score = calculate_score(kills, deaths, health);
            prop_assert!(score >= 0.0 && score <= 1.0);
        }

        #[test]
        fn more_kills_better_score(
            base_kills in 1u32..100,
            deaths in 0u32..10,
            health in 50.0f64..100.0
        ) {
            let score_low = calculate_score(base_kills, deaths, health);
            let score_high = calculate_score(base_kills + 10, deaths, health);
            prop_assert!(score_high >= score_low);
        }
    }
}
```

### Mocking with mockall

```rust
use mockall::{automock, predicate::*};

#[automock]
trait OpenSearchClient {
    fn knn_search(&self, query_vector: Vec<f32>) -> Result<Vec<Strategy>>;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_decision_with_mock_opensearch() {
        let mut mock_client = MockOpenSearchClient::new();

        mock_client
            .expect_knn_search()
            .with(predicate::always())
            .times(1)
            .returning(|_| Ok(vec![Strategy::aggressive()]));

        let engine = DecisionEngine::with_client(mock_client);
        let decision = engine.decide_with_rag(&GameState::default()).unwrap();

        assert_eq!(decision.strategy_id, "aggressive");
    }
}
```

### Test Fixtures

```rust
// tests/common/mod.rs
pub struct TestFixture {
    pub game_state: GameState,
    pub expected_actions: Vec<Action>,
}

impl TestFixture {
    pub fn combat_scenario() -> Self {
        Self {
            game_state: GameState {
                health: 100.0,
                ammo: 50,
                enemy_visible: true,
                enemy_distance: 200.0,
            },
            expected_actions: vec![Action::Attack, Action::Strafe],
        }
    }

    pub fn retreat_scenario() -> Self {
        Self {
            game_state: GameState {
                health: 20.0,
                ammo: 5,
                enemy_visible: true,
                enemy_distance: 100.0,
            },
            expected_actions: vec![Action::Retreat, Action::FindHealth],
        }
    }
}

// tests/decision_scenarios.rs
mod common;
use common::TestFixture;

#[test]
fn test_all_scenarios() {
    let scenarios = vec![
        TestFixture::combat_scenario(),
        TestFixture::retreat_scenario(),
    ];

    let engine = DecisionEngine::new();

    for fixture in scenarios {
        let decision = engine.decide(&fixture.game_state);
        assert!(fixture.expected_actions.contains(&decision.action));
    }
}
```

## Go Testing

### Table-Driven Tests

```go
package orchestrator

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"
)

func TestGenerationManagement(t *testing.T) {
    tests := []struct {
        name           string
        populationSize int
        survivalRate   float64
        expectedSurvivors int
        wantErr        bool
    }{
        {
            name:           "normal_generation",
            populationSize: 50,
            survivalRate:   0.3,
            expectedSurvivors: 15,
            wantErr:        false,
        },
        {
            name:           "zero_survival",
            populationSize: 50,
            survivalRate:   0.0,
            expectedSurvivors: 0,
            wantErr:        true,
        },
        {
            name:           "full_survival",
            populationSize: 50,
            survivalRate:   1.0,
            expectedSurvivors: 50,
            wantErr:        false,
        },
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            gen := NewGeneration(tt.populationSize)
            survivors, err := gen.Select(tt.survivalRate)

            if tt.wantErr {
                require.Error(t, err)
                return
            }

            require.NoError(t, err)
            assert.Equal(t, tt.expectedSurvivors, len(survivors))
        })
    }
}
```

### Test Helpers

```go
func TestAgentLifecycle(t *testing.T) {
    t.Helper()

    ctx := context.Background()
    orch := newTestOrchestrator(t, ctx)
    defer orch.Cleanup()

    agentID := "test-agent-001"

    // Spawn
    containerID, err := orch.SpawnAgent(ctx, agentID)
    require.NoError(t, err)
    assert.NotEmpty(t, containerID)

    // Health check
    waitForHealthy(t, orch, agentID, 10*time.Second)

    // Terminate
    err = orch.TerminateAgent(ctx, agentID)
    require.NoError(t, err)
}

func newTestOrchestrator(t *testing.T, ctx context.Context) *Orchestrator {
    t.Helper()

    config := &Config{
        GRPCPort: 50051,
        NATSUrl:  "nats://localhost:4222",
    }

    orch, err := New(config)
    require.NoError(t, err)

    t.Cleanup(func() {
        _ = orch.Shutdown(context.Background())
    })

    return orch
}

func waitForHealthy(t *testing.T, orch *Orchestrator, agentID string, timeout time.Duration) {
    t.Helper()

    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()

    ticker := time.NewTicker(100 * time.Millisecond)
    defer ticker.Stop()

    for {
        select {
        case <-ctx.Done():
            t.Fatalf("agent %s did not become healthy within %v", agentID, timeout)
        case <-ticker.C:
            if orch.IsHealthy(agentID) {
                return
            }
        }
    }
}
```

### gomock for Interface Mocking

```go
//go:generate mockgen -source=agent_service.go -destination=mock_agent_service.go -package=orchestrator

func TestEvolutionWithMockAgent(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockAgent := NewMockAgentService(ctrl)

    // Expect 3 evaluation calls
    mockAgent.EXPECT().
        Evaluate(gomock.Any(), gomock.Any()).
        Return(&EvaluationResult{Score: 0.85}, nil).
        Times(3)

    orch := NewOrchestrator(WithAgentService(mockAgent))

    results, err := orch.EvaluateGeneration(context.Background(), 3)
    require.NoError(t, err)
    assert.Len(t, results, 3)
}
```

### HTTP Endpoint Testing

```go
import "net/http/httptest"

func TestHTTPStatusEndpoint(t *testing.T) {
    orch := newTestOrchestrator(t, context.Background())

    req := httptest.NewRequest("GET", "/status", nil)
    w := httptest.NewRecorder()

    orch.ServeHTTP(w, req)

    assert.Equal(t, http.StatusOK, w.Code)

    var status StatusResponse
    err := json.Unmarshal(w.Body.Bytes(), &status)
    require.NoError(t, err)
    assert.Equal(t, "running", status.State)
}
```

### Docker Integration Tests with testcontainers-go

```go
import (
    "github.com/testcontainers/testcontainers-go"
    "github.com/testcontainers/testcontainers-go/wait"
)

func TestWithRealNATS(t *testing.T) {
    ctx := context.Background()

    natsContainer, err := testcontainers.GenericContainer(ctx, testcontainers.GenericContainerRequest{
        ContainerRequest: testcontainers.ContainerRequest{
            Image:        "nats:latest",
            ExposedPorts: []string{"4222/tcp"},
            WaitingFor:   wait.ForLog("Server is ready"),
        },
        Started: true,
    })
    require.NoError(t, err)
    defer natsContainer.Terminate(ctx)

    endpoint, err := natsContainer.Endpoint(ctx, "")
    require.NoError(t, err)

    // Test with real NATS
    config := &Config{NATSUrl: fmt.Sprintf("nats://%s", endpoint)}
    orch, err := New(config)
    require.NoError(t, err)
    defer orch.Shutdown(ctx)

    // Publish event
    err = orch.PublishEvent(ctx, &Event{Type: "test"})
    assert.NoError(t, err)
}
```

### Benchmark Tests

```go
func BenchmarkAgentSpawn(b *testing.B) {
    ctx := context.Background()
    orch := setupBenchOrch(b)
    defer orch.Cleanup()

    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        agentID := fmt.Sprintf("bench-agent-%d", i)
        _, err := orch.SpawnAgent(ctx, agentID)
        if err != nil {
            b.Fatal(err)
        }
    }
}

func BenchmarkConcurrentEvaluation(b *testing.B) {
    ctx := context.Background()
    orch := setupBenchOrch(b)
    defer orch.Cleanup()

    agents := make([]string, 10)
    for i := range agents {
        agents[i] = fmt.Sprintf("agent-%d", i)
    }

    b.ResetTimer()

    for i := 0; i < b.N; i++ {
        _, err := orch.EvaluateAll(ctx, agents)
        if err != nil {
            b.Fatal(err)
        }
    }
}
```

## Python Testing

### pytest Framework

```python
# tests/conftest.py
import pytest
import duckdb
from pathlib import Path

@pytest.fixture
def test_db():
    """In-memory DuckDB for testing."""
    conn = duckdb.connect(":memory:")
    conn.execute("""
        CREATE TABLE experiments (
            run_id INTEGER,
            factor_memory DOUBLE,
            factor_strength DOUBLE,
            response_kills INTEGER,
            response_survival DOUBLE
        )
    """)
    yield conn
    conn.close()

@pytest.fixture
def sample_doe_data():
    """Fixture with known DOE results."""
    return {
        "factors": ["memory", "strength"],
        "levels": {"memory": [0.5, 0.7, 0.9], "strength": [0.3, 0.5]},
        "responses": [42, 38, 55, 48, 61, 58],  # 2x3 factorial
    }

@pytest.fixture
def known_effect_data():
    """Data with known main effect for validation."""
    # Memory effect = +10 kills per 0.2 increase (linear)
    return [
        {"memory": 0.5, "kills": 40},
        {"memory": 0.7, "kills": 50},
        {"memory": 0.9, "kills": 60},
    ] * 10  # Replicated
```

### Parametrize for Test Coverage

```python
# tests/test_anova.py
import pytest
from analysis.anova import factorial_anova, check_assumptions

@pytest.mark.parametrize("design,expected_factors", [
    ("2x3", ["memory", "strength"]),
    ("2x2x2", ["memory", "strength", "curiosity"]),
    ("3x3", ["memory", "aggression"]),
])
def test_factorial_designs(design, expected_factors, test_db):
    result = factorial_anova(test_db, design)
    assert set(result["factors"]) == set(expected_factors)

@pytest.mark.parametrize("transformation", ["log", "sqrt", "box-cox"])
def test_normality_transformations(known_skewed_data, transformation):
    transformed = apply_transformation(known_skewed_data, transformation)
    p_value = check_assumptions(transformed)["normality_p"]
    assert p_value > 0.05, f"{transformation} failed to normalize data"
```

### hypothesis for Property-Based Testing

```python
# tests/test_doe_properties.py
from hypothesis import given, strategies as st
import hypothesis.extra.numpy as npst

@given(
    memory=st.floats(min_value=0.0, max_value=1.0),
    strength=st.floats(min_value=0.0, max_value=1.0),
    kills=st.integers(min_value=0, max_value=1000)
)
def test_score_bounds(memory, strength, kills):
    """Score must always be in [0, 1] regardless of inputs."""
    score = calculate_score(memory, strength, kills)
    assert 0.0 <= score <= 1.0

@given(npst.arrays(dtype=np.float64, shape=st.integers(min_value=30, max_value=100)))
def test_anova_with_random_data(response_data):
    """ANOVA should not crash with any valid data shape."""
    result = run_anova(response_data)
    assert "F_statistic" in result
    assert "p_value" in result
    assert result["p_value"] >= 0.0
```

### unittest.mock for External Dependencies

```python
# tests/test_vizdoom_integration.py
from unittest.mock import Mock, patch
import pytest

def test_episode_execution_mocked():
    mock_game = Mock()
    mock_game.is_episode_finished.return_value = False
    mock_game.get_state.return_value = Mock(
        number=1,
        game_variables=[100.0, 50.0, 10.0]  # health, ammo, kills
    )

    with patch('vizdoom.DoomGame', return_value=mock_game):
        from agent.executor import run_episode
        result = run_episode(seed=42, steps=100)

        assert result["kills"] == 10.0
        assert mock_game.new_episode.called

@patch('duckdb.connect')
def test_data_recording(mock_connect, sample_doe_data):
    mock_conn = Mock()
    mock_connect.return_value = mock_conn

    from analysis.recorder import record_run
    record_run(run_id=1, data=sample_doe_data)

    mock_conn.execute.assert_called()
    call_args = mock_conn.execute.call_args[0][0]
    assert "INSERT INTO experiments" in call_args
```

### pytest-cov for Coverage

```python
# pytest.ini or pyproject.toml
[tool.pytest.ini_options]
addopts = """
    --cov=agent
    --cov=analysis
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
"""

# Run tests with coverage
# pytest --cov=agent --cov=analysis --cov-report=html
```

### Test Fixtures for DuckDB

```python
# tests/conftest.py
import duckdb
import pytest

@pytest.fixture
def experiment_db(tmp_path):
    """DuckDB with realistic experiment schema."""
    db_path = tmp_path / "test_experiments.duckdb"
    conn = duckdb.connect(str(db_path))

    conn.execute("""
        CREATE TABLE runs (
            run_id INTEGER PRIMARY KEY,
            experiment_id INTEGER,
            generation INTEGER,
            agent_id VARCHAR,
            seed INTEGER,
            timestamp TIMESTAMP
        )
    """)

    conn.execute("""
        CREATE TABLE episodes (
            episode_id INTEGER PRIMARY KEY,
            run_id INTEGER,
            kills INTEGER,
            deaths INTEGER,
            survival_time DOUBLE,
            damage_dealt INTEGER,
            damage_taken INTEGER,
            FOREIGN KEY (run_id) REFERENCES runs(run_id)
        )
    """)

    yield conn
    conn.close()

def test_aggregate_metrics(experiment_db):
    # Insert test data
    experiment_db.execute("""
        INSERT INTO runs VALUES (1, 42, 1, 'agent-A', 1337, NOW())
    """)
    experiment_db.execute("""
        INSERT INTO episodes VALUES
        (1, 1, 10, 2, 180.5, 500, 100),
        (2, 1, 8, 3, 150.0, 400, 120)
    """)

    # Test aggregation
    from analysis.metrics import aggregate_run_metrics
    metrics = aggregate_run_metrics(experiment_db, run_id=1)

    assert metrics["avg_kills"] == 9.0
    assert metrics["total_episodes"] == 2
```

## TypeScript Testing

### Vitest for Unit and Component Tests

```typescript
// src/lib/utils.test.ts
import { describe, it, expect } from 'vitest';
import { calculateKDRatio, formatDuration } from './utils';

describe('calculateKDRatio', () => {
  it('calculates K/D ratio correctly', () => {
    expect(calculateKDRatio(10, 2)).toBe(5.0);
    expect(calculateKDRatio(15, 3)).toBe(5.0);
  });

  it('handles zero deaths', () => {
    expect(calculateKDRatio(10, 0)).toBe(10.0);
  });

  it('handles zero kills', () => {
    expect(calculateKDRatio(0, 5)).toBe(0.0);
  });
});

describe('formatDuration', () => {
  it('formats seconds correctly', () => {
    expect(formatDuration(45)).toBe('45s');
    expect(formatDuration(125)).toBe('2m 5s');
    expect(formatDuration(3665)).toBe('1h 1m 5s');
  });
});
```

### React Testing Library

```typescript
// src/components/GenerationChart.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import userEvent from '@testing-library/user-event';
import GenerationChart from './GenerationChart';

const mockData = {
  generations: [1, 2, 3],
  avgScores: [0.45, 0.62, 0.78],
  maxScores: [0.55, 0.71, 0.89],
};

describe('GenerationChart', () => {
  it('renders chart with data', () => {
    render(<GenerationChart data={mockData} />);

    expect(screen.getByText(/Generation Progress/i)).toBeInTheDocument();
    expect(screen.getByRole('img', { name: /chart/i })).toBeInTheDocument();
  });

  it('shows tooltip on hover', async () => {
    const user = userEvent.setup();
    render(<GenerationChart data={mockData} />);

    const dataPoint = screen.getByTestId('data-point-gen-2');
    await user.hover(dataPoint);

    await waitFor(() => {
      expect(screen.getByText(/Generation 2/i)).toBeInTheDocument();
      expect(screen.getByText(/Avg: 0.62/i)).toBeInTheDocument();
    });
  });

  it('updates when data changes', () => {
    const { rerender } = render(<GenerationChart data={mockData} />);

    const updatedData = {
      ...mockData,
      generations: [1, 2, 3, 4],
      avgScores: [0.45, 0.62, 0.78, 0.85],
      maxScores: [0.55, 0.71, 0.89, 0.92],
    };

    rerender(<GenerationChart data={updatedData} />);
    expect(screen.getByTestId('data-point-gen-4')).toBeInTheDocument();
  });
});
```

### MSW for API Mocking

```typescript
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/experiment/:id/status', ({ params }) => {
    const { id } = params;
    return HttpResponse.json({
      experimentId: id,
      status: 'running',
      currentGeneration: 5,
      totalGenerations: 10,
      bestScore: 0.85,
    });
  }),

  http.get('/api/generation/:gen/agents', ({ params }) => {
    const { gen } = params;
    return HttpResponse.json({
      generation: parseInt(gen as string),
      agents: [
        { id: 'agent-1', score: 0.82, kills: 45, deaths: 12 },
        { id: 'agent-2', score: 0.75, kills: 38, deaths: 15 },
      ],
    });
  }),

  http.post('/api/experiment/start', async ({ request }) => {
    const body = await request.json();
    return HttpResponse.json({
      experimentId: 'exp-123',
      status: 'started',
    }, { status: 201 });
  }),
];

// src/mocks/browser.ts
import { setupWorker } from 'msw/browser';
import { handlers } from './handlers';

export const worker = setupWorker(...handlers);

// src/setupTests.ts
import { beforeAll, afterEach, afterAll } from 'vitest';
import { server } from './mocks/server';

beforeAll(() => server.listen());
afterEach(() => server.resetHandlers());
afterAll(() => server.close());
```

### Testing WebSocket Connections

```typescript
// src/lib/websocket.test.ts
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { WebSocketClient } from './websocket';
import { WS } from 'vitest-websocket-mock';

describe('WebSocketClient', () => {
  let server: WS;
  let client: WebSocketClient;

  beforeEach(() => {
    server = new WS('ws://localhost:8080/events');
    client = new WebSocketClient('ws://localhost:8080/events');
  });

  afterEach(() => {
    server.close();
    client.close();
  });

  it('connects and receives messages', async () => {
    await server.connected;

    const messageHandler = vi.fn();
    client.on('message', messageHandler);

    server.send(JSON.stringify({ type: 'generation', generation: 5 }));

    expect(messageHandler).toHaveBeenCalledWith(
      expect.objectContaining({ type: 'generation', generation: 5 })
    );
  });

  it('reconnects on disconnect', async () => {
    await server.connected;

    server.close();

    // Wait for reconnect
    await vi.waitFor(() => {
      expect(client.isConnected()).toBe(true);
    }, { timeout: 5000 });
  });

  it('sends events', async () => {
    await server.connected;

    client.send({ type: 'subscribe', experimentId: 'exp-123' });

    await expect(server).toReceiveMessage(
      JSON.stringify({ type: 'subscribe', experimentId: 'exp-123' })
    );
  });
});
```

### Testing Dashboard Chart Rendering

```typescript
// src/components/ExperimentDashboard.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { server } from '../mocks/server';
import { http, HttpResponse } from 'msw';
import ExperimentDashboard from './ExperimentDashboard';

describe('ExperimentDashboard', () => {
  it('loads and displays experiment data', async () => {
    render(<ExperimentDashboard experimentId="exp-123" />);

    expect(screen.getByText(/Loading.../i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText(/Experiment exp-123/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Generation 5\/10/i)).toBeInTheDocument();
    expect(screen.getByText(/Best Score: 0.85/i)).toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    server.use(
      http.get('/api/experiment/:id/status', () => {
        return HttpResponse.json(
          { error: 'Experiment not found' },
          { status: 404 }
        );
      })
    );

    render(<ExperimentDashboard experimentId="exp-999" />);

    await waitFor(() => {
      expect(screen.getByText(/Experiment not found/i)).toBeInTheDocument();
    });
  });

  it('updates in real-time via WebSocket', async () => {
    const { rerender } = render(<ExperimentDashboard experimentId="exp-123" />);

    await waitFor(() => {
      expect(screen.getByText(/Generation 5\/10/i)).toBeInTheDocument();
    });

    // Simulate WebSocket update
    // (Requires WebSocket mock integration)
  });
});
```

## Integration Testing with Docker

### Docker Compose Test Environment

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  opensearch-test:
    image: opensearchproject/opensearch:2.11.0
    environment:
      - discovery.type=single-node
      - DISABLE_SECURITY_PLUGIN=true
    ports:
      - "9201:9200"
    healthcheck:
      test: ["CMD-SHELL", "curl -f http://localhost:9200/_cluster/health || exit 1"]
      interval: 5s
      timeout: 3s
      retries: 10

  mongodb-test:
    image: mongo:7
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
    command: ["-js", "-m", "8222"]
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost:8222/healthz"]
      interval: 3s
      timeout: 2s
      retries: 10

  duckdb-test:
    image: alpine:latest
    volumes:
      - ./data/test:/data
    command: ["sleep", "infinity"]
```

### Integration Test Script

```bash
#!/bin/bash
# scripts/run-integration-tests.sh

set -e

echo "Starting test containers..."
docker compose -f docker-compose.test.yml up -d

echo "Waiting for services to be healthy..."
docker compose -f docker-compose.test.yml ps --filter "health=healthy" | grep -q opensearch-test
docker compose -f docker-compose.test.yml ps --filter "health=healthy" | grep -q mongodb-test
docker compose -f docker-compose.test.yml ps --filter "health=healthy" | grep -q nats-test

echo "Running integration tests..."

# Rust integration tests
cd agent && cargo test --features integration-tests

# Go integration tests with real containers
cd ../orchestrator && go test -tags=integration ./...

# Python integration tests
cd ../analytics && pytest tests/integration/

# TypeScript integration tests
cd ../dashboard && npm run test:integration

echo "Cleaning up test containers..."
docker compose -f docker-compose.test.yml down -v

echo "Integration tests complete!"
```

### Cross-Service Integration Test

```python
# tests/integration/test_full_pipeline.py
import pytest
import duckdb
import requests
import time
from opensearchpy import OpenSearch

@pytest.mark.integration
def test_experiment_full_pipeline(test_containers):
    """Test complete experiment pipeline across all services."""

    # 1. Start experiment via orchestrator API
    response = requests.post(
        "http://localhost:50051/api/experiment/start",
        json={
            "generations": 3,
            "populationSize": 10,
            "config": "test-config.yaml"
        }
    )
    assert response.status_code == 201
    experiment_id = response.json()["experimentId"]

    # 2. Wait for generation 1 completion
    time.sleep(10)

    # 3. Verify DuckDB has recorded episodes
    conn = duckdb.connect("data/test/experiments.duckdb")
    result = conn.execute(
        "SELECT COUNT(*) FROM episodes WHERE run_id IN (SELECT run_id FROM runs WHERE experiment_id = ?)",
        [experiment_id]
    ).fetchone()
    assert result[0] > 0, "No episodes recorded in DuckDB"

    # 4. Verify OpenSearch has strategy documents
    os_client = OpenSearch([{"host": "localhost", "port": 9201}])
    search_result = os_client.search(
        index="strategies",
        body={"query": {"match": {"experiment_id": experiment_id}}}
    )
    assert search_result["hits"]["total"]["value"] > 0

    # 5. Verify experiment status via dashboard API
    status_response = requests.get(f"http://localhost:3000/api/experiment/{experiment_id}/status")
    assert status_response.status_code == 200
    assert status_response.json()["currentGeneration"] >= 1
```

## Test Data Management

### Fixture Files Organization

```
tests/
  fixtures/
    doe_designs/
      factorial_2x3.yaml
      ccd_3factor.yaml
      taguchi_l18.yaml
    datasets/
      known_main_effect.csv       # Memory effect = +10 kills per 0.2 increase
      known_interaction.csv        # Memory × Strength interaction
      non_normal_residuals.csv     # For transformation testing
    strategies/
      aggressive_strategy.json
      defensive_strategy.json
      exploration_strategy.json
```

### Seed-Based Deterministic Data

```python
# tests/fixtures/generators.py
import numpy as np

def generate_factorial_data(seed=42, n_per_cell=30):
    """Generate 2x3 factorial data with known effects."""
    rng = np.random.default_rng(seed)

    # Memory: [0.5, 0.7, 0.9]
    # Strength: [0.3, 0.5]
    # Known effect: Memory +10 kills per 0.2, Strength +5 kills per 0.2

    data = []
    for memory in [0.5, 0.7, 0.9]:
        for strength in [0.3, 0.5]:
            base_kills = 30 + (memory - 0.5) * 50 + (strength - 0.3) * 25
            kills = rng.normal(base_kills, 5, n_per_cell)

            for k in kills:
                data.append({
                    "memory": memory,
                    "strength": strength,
                    "kills": int(k)
                })

    return data
```

### DOE Test Datasets

```yaml
# tests/fixtures/doe_designs/factorial_2x3.yaml
design_type: full_factorial
factors:
  - name: memory
    levels: [0.5, 0.7, 0.9]
  - name: strength
    levels: [0.3, 0.5]
runs: 6
replicates: 30
randomization: true
seed: 42

expected_results:
  main_effects:
    memory:
      F_statistic: 45.2
      p_value: 0.001
      effect_size: 0.18
    strength:
      F_statistic: 12.8
      p_value: 0.003
      effect_size: 0.07
  interaction:
    memory_x_strength:
      F_statistic: 2.1
      p_value: 0.15
      effect_size: 0.02
```

## Coverage Requirements

### Minimum Thresholds

| Component | Threshold | Tool |
|-----------|-----------|------|
| Rust agent-core | 80% | cargo-llvm-cov |
| Go orchestrator | 70% | go test -cover |
| Python analytics | 85% | pytest-cov |
| TypeScript dashboard | 75% | vitest coverage |

### Coverage Tools

```bash
# Rust
cargo install cargo-llvm-cov
cargo llvm-cov --html

# Go
go test -coverprofile=coverage.out ./...
go tool cover -html=coverage.out

# Python
pytest --cov=agent --cov=analysis --cov-report=html

# TypeScript
npm run test:coverage
```

### CI Integration

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test-rust:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions-rs/toolchain@v1
        with:
          toolchain: stable
      - run: cargo llvm-cov --all-features --lcov --output-path lcov.info
      - uses: codecov/codecov-action@v3
        with:
          files: lcov.info

  test-go:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-go@v4
        with:
          go-version: '1.21'
      - run: go test -race -coverprofile=coverage.out ./...
      - uses: codecov/codecov-action@v3
        with:
          files: coverage.out

  test-python:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements-dev.txt
          pytest --cov=agent --cov=analysis --cov-report=xml
      - uses: codecov/codecov-action@v3

  test-typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '18'
      - run: |
          npm ci
          npm run test:coverage
      - uses: codecov/codecov-action@v3
```

## Testing Best Practices

### Test Naming Conventions

```rust
// Rust: test_{function}_{scenario}
#[test]
fn test_decision_engine_with_low_health() { }

#[test]
fn test_scoring_calculates_normalized_values() { }
```

```go
// Go: Test{Function}_{Scenario} or table test name
func TestAgentLifecycle_SpawnAndTerminate(t *testing.T) { }

func TestScoring(t *testing.T) {
    tests := []struct {
        name string
        // ...
    }{
        {name: "perfect_run", /* ... */},
    }
}
```

```python
# Python: test_{function}_{scenario}
def test_anova_with_balanced_design():
    pass

def test_transformation_log_normalizes_skewed_data():
    pass
```

```typescript
// TypeScript: describe/it natural language
describe('GenerationChart', () => {
  it('renders chart with data', () => { });
  it('shows tooltip on hover', () => { });
});
```

### AAA Pattern (Arrange, Act, Assert)

```rust
#[test]
fn test_decision_with_enemy_nearby() {
    // Arrange
    let state = GameState {
        health: 80.0,
        enemy_distance: 150.0,
        enemy_visible: true,
        ammo: 50,
    };
    let engine = DecisionEngine::new();

    // Act
    let decision = engine.decide(&state);

    // Assert
    assert_eq!(decision.action, Action::Attack);
    assert!(decision.confidence > 0.7);
}
```

### Test Isolation

```python
import pytest

@pytest.fixture
def isolated_db(tmp_path):
    """Each test gets its own DB instance."""
    db_path = tmp_path / "test.duckdb"
    conn = duckdb.connect(str(db_path))
    yield conn
    conn.close()
    # tmp_path is cleaned up automatically

def test_insert_data(isolated_db):
    isolated_db.execute("CREATE TABLE test (id INT)")
    isolated_db.execute("INSERT INTO test VALUES (1)")
    result = isolated_db.execute("SELECT * FROM test").fetchall()
    assert len(result) == 1
```

### Flaky Test Prevention

```go
func TestConcurrentAccess(t *testing.T) {
    // Use deterministic concurrency
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    // Use sync primitives for deterministic ordering
    var wg sync.WaitGroup
    ready := make(chan struct{})

    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            <-ready  // All goroutines start together
            // Test logic
        }()
    }

    close(ready)  // Start all goroutines
    wg.Wait()
}
```

### One Assertion Per Test (Guideline)

```typescript
// Prefer focused tests
describe('calculateScore', () => {
  it('returns 0 for zero kills', () => {
    expect(calculateScore(0, 5, 50)).toBe(0);
  });

  it('returns 1 for perfect run', () => {
    expect(calculateScore(50, 0, 100)).toBe(1.0);
  });

  it('normalizes score to [0, 1] range', () => {
    const score = calculateScore(25, 10, 75);
    expect(score).toBeGreaterThanOrEqual(0);
    expect(score).toBeLessThanOrEqual(1);
  });
});

// Over multiple related assertions in one test
```
