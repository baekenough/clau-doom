# Python Expert Agent Memory

## Project: clau-doom

### gRPC Integration (Phase 6)
- Proto stubs generated with `grpc_tools.protoc` into `glue/proto/`
- Generated `agent_pb2_grpc.py` needs import fix: `import agent_pb2` -> `from glue.proto import agent_pb2`
- GrpcActionClient implements ActionFn protocol via `__call__(self, state: GameState) -> int`
- ActionType mapping: proto {MOVE_LEFT=1, MOVE_RIGHT=2, ATTACK=7} -> VizDoom {0, 1, 2}
- Dynamic decision_level: episode_runner uses `hasattr(action_fn, 'last_decision_level')` duck typing
- Dependencies in `.venv`: grpcio, grpcio-tools, protobuf

### Environment
- Python venv at `/Users/sangyi/workspace/research/clau-doom/.venv/`
- macOS uses externally-managed Python; must use `.venv/bin/python3` for pip installs
- Run commands with full venv path: `.venv/bin/python3 -m pip install ...`

### Key Files
- `glue/vizdoom_bridge.py` - GameState dataclass, VizDoom wrapper, action constants
- `glue/episode_runner.py` - EpisodeRunner, EpisodeResult, ActionFn protocol
- `glue/grpc_client.py` - GrpcActionClient, check_grpc_health
- `glue/proto/` - Generated proto stubs (agent_pb2.py, agent_pb2_grpc.py)
- `proto/agent.proto` - Source proto definition
