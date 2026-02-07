---
name: go-best-practices
description: Idiomatic Go patterns for orchestrator service including concurrency, gRPC, CLI with cobra, and Docker SDK integration
user-invocable: false
---

# Go Best Practices for clau-doom Orchestrator

## Concurrency Patterns

### Goroutines and Channels

```go
// Fan-out: distribute work across multiple goroutines
func runGeneration(ctx context.Context, agents []Agent, game *vizdoom.Game) []Result {
    results := make(chan Result, len(agents))

    for _, agent := range agents {
        go func(a Agent) {
            result, err := evaluateAgent(ctx, a, game)
            if err != nil {
                results <- Result{AgentID: a.ID, Error: err}
                return
            }
            results <- result
        }(agent)
    }

    var collected []Result
    for range agents {
        collected = append(collected, <-results)
    }
    return collected
}
```

### Context Propagation

```go
func (o *Orchestrator) RunExperiment(ctx context.Context, config ExperimentConfig) error {
    ctx, cancel := context.WithTimeout(ctx, config.MaxDuration)
    defer cancel()

    for gen := 0; gen < config.Generations; gen++ {
        select {
        case <-ctx.Done():
            return fmt.Errorf("experiment cancelled at generation %d: %w", gen, ctx.Err())
        default:
            if err := o.runGeneration(ctx, gen); err != nil {
                return fmt.Errorf("generation %d failed: %w", gen, err)
            }
        }
    }
    return nil
}
```

### Sync Primitives

```go
// Use sync.Map for concurrent read-heavy agent registry
type AgentRegistry struct {
    agents sync.Map // map[AgentID]*AgentState
}

func (r *AgentRegistry) Get(id AgentID) (*AgentState, bool) {
    val, ok := r.agents.Load(id)
    if !ok {
        return nil, false
    }
    return val.(*AgentState), true
}

// Use sync.WaitGroup for waiting on parallel evaluation
func (o *Orchestrator) evaluateAll(ctx context.Context, agents []Agent) error {
    var wg sync.WaitGroup
    errCh := make(chan error, len(agents))

    for _, a := range agents {
        wg.Add(1)
        go func(agent Agent) {
            defer wg.Done()
            if err := o.evaluate(ctx, agent); err != nil {
                errCh <- fmt.Errorf("agent %s: %w", agent.ID, err)
            }
        }(a)
    }

    wg.Wait()
    close(errCh)

    var errs []error
    for err := range errCh {
        errs = append(errs, err)
    }
    return errors.Join(errs...)
}
```

### errgroup for Structured Concurrency

```go
import "golang.org/x/sync/errgroup"

func (o *Orchestrator) startServices(ctx context.Context) error {
    g, ctx := errgroup.WithContext(ctx)

    g.Go(func() error {
        return o.grpcServer.Serve(ctx)
    })

    g.Go(func() error {
        return o.natsSubscriber.Run(ctx)
    })

    g.Go(func() error {
        return o.metricsServer.ListenAndServe()
    })

    return g.Wait()
}
```

## Error Handling

### Wrapping with Context

```go
func (o *Orchestrator) LoadConfig(path string) (*Config, error) {
    data, err := os.ReadFile(path)
    if err != nil {
        return nil, fmt.Errorf("reading config file %s: %w", path, err)
    }

    var config Config
    if err := yaml.Unmarshal(data, &config); err != nil {
        return nil, fmt.Errorf("parsing config YAML: %w", err)
    }

    if err := config.Validate(); err != nil {
        return nil, fmt.Errorf("invalid config: %w", err)
    }

    return &config, nil
}
```

### Sentinel Errors

```go
var (
    ErrAgentNotFound    = errors.New("agent not found")
    ErrGenerationFull   = errors.New("generation at capacity")
    ErrExperimentDone   = errors.New("experiment completed")
    ErrShutdownRequested = errors.New("shutdown requested")
)

func (o *Orchestrator) GetAgent(id AgentID) (*Agent, error) {
    agent, ok := o.registry.Get(id)
    if !ok {
        return nil, fmt.Errorf("agent %s: %w", id, ErrAgentNotFound)
    }
    return agent, nil
}

// Caller checks with errors.Is
if errors.Is(err, ErrAgentNotFound) {
    // handle missing agent
}
```

## gRPC Server

### Proto Service Definition

```protobuf
// api/proto/orchestrator.proto
syntax = "proto3";
package claudoom.orchestrator.v1;

service OrchestratorService {
    rpc StartExperiment(StartExperimentRequest) returns (StartExperimentResponse);
    rpc GetGenerationStatus(GetGenerationStatusRequest) returns (GenerationStatus);
    rpc StreamEvents(StreamEventsRequest) returns (stream ExperimentEvent);
    rpc ControlAgent(stream AgentCommand) returns (stream AgentResponse);
}
```

### Server Implementation

```go
type orchestratorServer struct {
    pb.UnimplementedOrchestratorServiceServer
    orchestrator *Orchestrator
}

func (s *orchestratorServer) StartExperiment(
    ctx context.Context,
    req *pb.StartExperimentRequest,
) (*pb.StartExperimentResponse, error) {
    config, err := configFromProto(req.Config)
    if err != nil {
        return nil, status.Errorf(codes.InvalidArgument, "invalid config: %v", err)
    }

    expID, err := s.orchestrator.Start(ctx, config)
    if err != nil {
        return nil, status.Errorf(codes.Internal, "failed to start: %v", err)
    }

    return &pb.StartExperimentResponse{ExperimentId: string(expID)}, nil
}

func (s *orchestratorServer) StreamEvents(
    req *pb.StreamEventsRequest,
    stream pb.OrchestratorService_StreamEventsServer,
) error {
    ch := s.orchestrator.Subscribe(req.ExperimentId)
    defer s.orchestrator.Unsubscribe(ch)

    for {
        select {
        case event, ok := <-ch:
            if !ok {
                return nil
            }
            if err := stream.Send(eventToProto(event)); err != nil {
                return err
            }
        case <-stream.Context().Done():
            return stream.Context().Err()
        }
    }
}
```

### gRPC Server Startup

```go
func NewGRPCServer(orch *Orchestrator, port int) (*grpc.Server, net.Listener, error) {
    lis, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
    if err != nil {
        return nil, nil, fmt.Errorf("listen on port %d: %w", port, err)
    }

    srv := grpc.NewServer(
        grpc.UnaryInterceptor(grpc_middleware.ChainUnaryServer(
            grpc_recovery.UnaryServerInterceptor(),
            grpc_zap.UnaryServerInterceptor(logger),
        )),
        grpc.StreamInterceptor(grpc_middleware.ChainStreamServer(
            grpc_recovery.StreamServerInterceptor(),
            grpc_zap.StreamServerInterceptor(logger),
        )),
    )

    pb.RegisterOrchestratorServiceServer(srv, &orchestratorServer{orchestrator: orch})
    reflection.Register(srv)

    return srv, lis, nil
}
```

## CLI with Cobra

### Command Structure

```go
// cmd/clau-doom/main.go
func main() {
    rootCmd := &cobra.Command{
        Use:   "clau-doom",
        Short: "Evolutionary AI agent experimentation platform",
    }

    rootCmd.AddCommand(
        newRunCmd(),
        newStatusCmd(),
        newAgentCmd(),
        newAnalyzeCmd(),
    )

    if err := rootCmd.Execute(); err != nil {
        os.Exit(1)
    }
}
```

### Run Command

```go
func newRunCmd() *cobra.Command {
    var configPath string
    var generations int
    var populationSize int

    cmd := &cobra.Command{
        Use:   "run",
        Short: "Run an evolution experiment",
        RunE: func(cmd *cobra.Command, args []string) error {
            config, err := loadConfig(configPath)
            if err != nil {
                return err
            }
            config.Generations = generations
            config.PopulationSize = populationSize

            orch, err := orchestrator.New(config)
            if err != nil {
                return fmt.Errorf("creating orchestrator: %w", err)
            }

            return orch.Run(cmd.Context())
        },
    }

    cmd.Flags().StringVarP(&configPath, "config", "c", "config.yaml", "configuration file path")
    cmd.Flags().IntVarP(&generations, "generations", "g", 100, "number of generations")
    cmd.Flags().IntVarP(&populationSize, "population", "p", 50, "population size per generation")

    return cmd
}
```

### Viper Configuration

```go
func loadConfig(path string) (*Config, error) {
    v := viper.New()
    v.SetConfigFile(path)
    v.SetEnvPrefix("CLAU_DOOM")
    v.AutomaticEnv()
    v.SetEnvKeyReplacer(strings.NewReplacer(".", "_"))

    // Defaults
    v.SetDefault("grpc.port", 50051)
    v.SetDefault("nats.url", "nats://localhost:4222")
    v.SetDefault("docker.network", "clau-doom-net")

    if err := v.ReadInConfig(); err != nil {
        return nil, fmt.Errorf("reading config: %w", err)
    }

    var config Config
    if err := v.Unmarshal(&config); err != nil {
        return nil, fmt.Errorf("unmarshaling config: %w", err)
    }

    return &config, nil
}
```

## Docker SDK

### Container Management

```go
import (
    "github.com/docker/docker/api/types/container"
    "github.com/docker/docker/client"
)

func (m *ContainerManager) SpawnAgent(ctx context.Context, agentID string, config AgentContainerConfig) (string, error) {
    resp, err := m.client.ContainerCreate(ctx,
        &container.Config{
            Image: config.Image,
            Env: []string{
                fmt.Sprintf("AGENT_ID=%s", agentID),
                fmt.Sprintf("GRPC_ENDPOINT=%s", config.GRPCEndpoint),
            },
            Labels: map[string]string{
                "clau-doom.agent-id":    agentID,
                "clau-doom.generation":  fmt.Sprint(config.Generation),
                "clau-doom.experiment":  config.ExperimentID,
            },
        },
        &container.HostConfig{
            NetworkMode: container.NetworkMode(m.network),
            Resources: container.Resources{
                Memory:   config.MemoryLimit,
                NanoCPUs: config.CPULimit,
            },
        },
        nil, nil,
        fmt.Sprintf("agent-%s", agentID),
    )
    if err != nil {
        return "", fmt.Errorf("creating container for agent %s: %w", agentID, err)
    }

    if err := m.client.ContainerStart(ctx, resp.ID, container.StartOptions{}); err != nil {
        return "", fmt.Errorf("starting container %s: %w", resp.ID, err)
    }

    return resp.ID, nil
}
```

### Cleanup

```go
func (m *ContainerManager) CleanupGeneration(ctx context.Context, generation int) error {
    filters := filters.NewArgs()
    filters.Add("label", fmt.Sprintf("clau-doom.generation=%d", generation))

    containers, err := m.client.ContainerList(ctx, container.ListOptions{Filters: filters})
    if err != nil {
        return fmt.Errorf("listing generation %d containers: %w", generation, err)
    }

    var errs []error
    for _, c := range containers {
        timeout := 10
        if err := m.client.ContainerStop(ctx, c.ID, container.StopOptions{Timeout: &timeout}); err != nil {
            errs = append(errs, fmt.Errorf("stopping %s: %w", c.ID[:12], err))
            continue
        }
        if err := m.client.ContainerRemove(ctx, c.ID, container.RemoveOptions{}); err != nil {
            errs = append(errs, fmt.Errorf("removing %s: %w", c.ID[:12], err))
        }
    }

    return errors.Join(errs...)
}
```

## Testing

### Table-Driven Tests

```go
func TestScoreCalculation(t *testing.T) {
    tests := []struct {
        name     string
        kills    int
        deaths   int
        health   float64
        expected float64
    }{
        {"perfect_run", 10, 0, 100.0, 1.0},
        {"even_kd", 5, 5, 50.0, 0.5},
        {"no_kills", 0, 3, 10.0, 0.05},
    }

    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := calculateScore(tt.kills, tt.deaths, tt.health)
            assert.InDelta(t, tt.expected, result, 0.01)
        })
    }
}
```

### Mock with gomock

```go
//go:generate mockgen -source=agent_service.go -destination=mock_agent_service.go -package=orchestrator

func TestOrchestratorEvaluation(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockAgent := NewMockAgentService(ctrl)
    mockAgent.EXPECT().
        GetAction(gomock.Any(), gomock.Any()).
        Return(&pb.ActionProto{ActionId: 1}, nil).
        Times(3)

    orch := NewOrchestrator(WithAgentService(mockAgent))
    err := orch.evaluate(context.Background(), testAgent)
    require.NoError(t, err)
}
```

## Project Layout

```
orchestrator/
  cmd/
    clau-doom/        # main binary
      main.go
  internal/
    orchestrator/     # core orchestration logic
      orchestrator.go
      generation.go
      evolution.go
    container/        # Docker container management
      manager.go
      health.go
    grpc/             # gRPC server implementation
      server.go
      handlers.go
    nats/             # NATS pub/sub
      publisher.go
      subscriber.go
    config/           # configuration
      config.go
      validate.go
  pkg/
    api/              # shared API types
      types.go
    proto/            # generated protobuf
      orchestrator.pb.go
  api/
    proto/            # protobuf definitions
      orchestrator.proto
      agent.proto
  go.mod
  go.sum
```
