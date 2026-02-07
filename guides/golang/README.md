# Go Reference Guide

Reference documentation for Go development in clau-doom orchestrator.

## Key Resources

- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Standard Go Project Layout](https://github.com/golang-standards/project-layout)
- [gRPC-Go](https://grpc.io/docs/languages/go/)
- [Cobra CLI](https://cobra.dev/)

## clau-doom Context

The orchestrator is written in Go for agent lifecycle management, generation control, and CLI tooling. It communicates with Rust agents via gRPC and manages Docker containers.

Project layout:
```
cmd/
├── clau-doom/          # CLI entry point (cobra)
└── orchestrator/       # gRPC server entry point
internal/
├── agent/              # Agent lifecycle management
├── generation/         # Generation evolution logic
├── doe/                # DOE run coordination
├── spc/                # SPC data collection
└── docker/             # Docker SDK wrapper
pkg/
├── proto/              # Generated gRPC stubs
└── config/             # Shared configuration types
```

## Concurrency Patterns

### Goroutines and Channels

Use goroutines for parallel agent monitoring and channels for coordination.

```go
// Monitor multiple agents concurrently.
func (o *Orchestrator) MonitorAgents(ctx context.Context, agents []Agent) <-chan AgentStatus {
    statusCh := make(chan AgentStatus, len(agents))

    for _, agent := range agents {
        go func(a Agent) {
            for {
                select {
                case <-ctx.Done():
                    return
                case <-time.After(1 * time.Second):
                    status, err := a.GetStatus(ctx)
                    if err != nil {
                        statusCh <- AgentStatus{ID: a.ID, Error: err}
                        continue
                    }
                    statusCh <- status
                }
            }
        }(agent)
    }

    return statusCh
}
```

### Context for Cancellation

Pass context through all operations for graceful shutdown and timeout control.

```go
// DOE run with timeout and cancellation.
func (r *DOERunner) ExecuteRun(ctx context.Context, run DOERun) (*RunResult, error) {
    ctx, cancel := context.WithTimeout(ctx, 30*time.Minute)
    defer cancel()

    // Spawn agent container
    containerID, err := r.docker.SpawnAgent(ctx, run.AgentConfig)
    if err != nil {
        return nil, fmt.Errorf("spawn agent for run %d: %w", run.ID, err)
    }
    defer r.docker.StopAgent(ctx, containerID)

    // Wait for episodes to complete
    results, err := r.collectEpisodes(ctx, containerID, run.MinEpisodes)
    if err != nil {
        return nil, fmt.Errorf("collect episodes for run %d: %w", run.ID, err)
    }

    return &RunResult{RunID: run.ID, Episodes: results}, nil
}
```

### Worker Pool for Parallel DOE Runs

```go
// Execute DOE matrix runs in parallel with bounded concurrency.
func (r *DOERunner) ExecuteMatrix(ctx context.Context, matrix []DOERun, workers int) ([]RunResult, error) {
    var (
        wg      sync.WaitGroup
        mu      sync.Mutex
        results []RunResult
        errs    []error
    )

    sem := make(chan struct{}, workers) // Limit concurrency

    for _, run := range matrix {
        wg.Add(1)
        go func(run DOERun) {
            defer wg.Done()
            sem <- struct{}{}        // Acquire
            defer func() { <-sem }() // Release

            result, err := r.ExecuteRun(ctx, run)
            mu.Lock()
            defer mu.Unlock()
            if err != nil {
                errs = append(errs, err)
                return
            }
            results = append(results, *result)
        }(run)
    }

    wg.Wait()
    if len(errs) > 0 {
        return results, fmt.Errorf("%d runs failed: %v", len(errs), errs[0])
    }
    return results, nil
}
```

## gRPC Server (grpc-go)

### Service Definition

```protobuf
// proto/orchestrator.proto
service OrchestratorService {
    rpc RegisterAgent(RegisterRequest) returns (RegisterReply);
    rpc ReportEpisode(EpisodeReport) returns (Ack);
    rpc StreamStates(StreamRequest) returns (stream StateUpdate);
    rpc TriggerEvolution(EvolutionRequest) returns (EvolutionReply);
}
```

### Server Implementation

```go
type orchestratorServer struct {
    pb.UnimplementedOrchestratorServiceServer
    agents     map[string]*AgentInfo
    mu         sync.RWMutex
    generation *GenerationManager
}

func (s *orchestratorServer) RegisterAgent(
    ctx context.Context, req *pb.RegisterRequest,
) (*pb.RegisterReply, error) {
    s.mu.Lock()
    defer s.mu.Unlock()

    s.agents[req.AgentId] = &AgentInfo{
        ID:         req.AgentId,
        Generation: req.Generation,
        Address:    req.Address,
        Status:     AgentReady,
    }

    return &pb.RegisterReply{Accepted: true}, nil
}
```

## CLI with Cobra

```go
// cmd/clau-doom/main.go
var rootCmd = &cobra.Command{
    Use:   "clau-doom",
    Short: "LLM multi-agent DOOM research orchestrator",
}

var spawnCmd = &cobra.Command{
    Use:   "spawn [count]",
    Short: "Spawn N agent containers",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        count, _ := strconv.Atoi(args[0])
        return orchestrator.SpawnAgents(cmd.Context(), count)
    },
}

var doeStatusCmd = &cobra.Command{
    Use:   "doe status",
    Short: "Show current DOE experiment progress",
    RunE: func(cmd *cobra.Command, args []string) error {
        return orchestrator.ShowDOEStatus(cmd.Context())
    },
}

func init() {
    rootCmd.AddCommand(spawnCmd, doeStatusCmd, evolveCmd, watchCmd, spcCmd, fmeaCmd)
}
```

## Docker SDK

```go
import (
    "github.com/docker/docker/client"
    "github.com/docker/docker/api/types/container"
)

// SpawnAgent creates a VizDoom player container with agent configuration.
func (d *DockerManager) SpawnAgent(ctx context.Context, config AgentConfig) (string, error) {
    resp, err := d.client.ContainerCreate(ctx,
        &container.Config{
            Image: "clau-doom/player:latest",
            Env: []string{
                fmt.Sprintf("AGENT_ID=%s", config.AgentID),
                fmt.Sprintf("GENERATION=%d", config.Generation),
                fmt.Sprintf("OPENSEARCH_URL=%s", d.opensearchURL),
            },
        },
        &container.HostConfig{
            Binds: []string{
                fmt.Sprintf("%s:/agent/config.md:ro", config.MDPath),
                fmt.Sprintf("%s:/agent/data", config.DataDir),
            },
            NetworkMode: "clau-doom_default",
        },
        nil, nil, fmt.Sprintf("player-%s", config.AgentID),
    )
    if err != nil {
        return "", fmt.Errorf("create container: %w", err)
    }

    if err := d.client.ContainerStart(ctx, resp.ID, container.StartOptions{}); err != nil {
        return "", fmt.Errorf("start container: %w", err)
    }

    return resp.ID, nil
}
```

## Error Wrapping

Use `fmt.Errorf` with `%w` for wrappable errors and `errors.Is`/`errors.As` for checking.

```go
func (o *Orchestrator) LoadGeneration(ctx context.Context, genID int) error {
    agents, err := o.store.GetAgentsByGeneration(ctx, genID)
    if err != nil {
        return fmt.Errorf("load generation %d: %w", genID, err)
    }

    for _, agent := range agents {
        if err := o.validateAgent(agent); err != nil {
            return fmt.Errorf("validate agent %s: %w", agent.ID, err)
        }
    }

    return nil
}

// Caller can inspect specific error types:
if errors.Is(err, ErrAgentNotFound) {
    // handle missing agent
}
```

## Testing Patterns

```go
// Table-driven tests
func TestScoreCalculation(t *testing.T) {
    tests := []struct {
        name     string
        kills    int
        health   float32
        time     int
        expected float64
    }{
        {"high_kills_low_health", 10, 20.0, 300, 8.5},
        {"zero_kills", 0, 100.0, 600, 1.0},
        {"balanced", 5, 50.0, 450, 5.2},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            got := CalculateScore(tt.kills, tt.health, tt.time)
            if math.Abs(got-tt.expected) > 0.1 {
                t.Errorf("CalculateScore() = %v, want %v", got, tt.expected)
            }
        })
    }
}

// Test with context timeout
func TestDOERunnerTimeout(t *testing.T) {
    ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
    defer cancel()

    runner := NewDOERunner(mockDocker, mockStore)
    _, err := runner.ExecuteRun(ctx, slowRun)
    if !errors.Is(err, context.DeadlineExceeded) {
        t.Errorf("expected deadline exceeded, got: %v", err)
    }
}
```

## Module Dependencies

| Module | Purpose |
|--------|---------|
| `google.golang.org/grpc` | gRPC framework |
| `google.golang.org/protobuf` | Protocol Buffers |
| `github.com/spf13/cobra` | CLI framework |
| `github.com/docker/docker` | Docker SDK |
| `github.com/nats-io/nats.go` | NATS messaging |
| `go.uber.org/zap` | Structured logging |
