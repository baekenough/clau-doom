# Rust Expert Memory

## Project Structure
- Workspace root: `/Users/sangyi/workspace/research/clau-doom/agent-core/`
- Single crate (not workspace yet), may expand to workspace with scoring/rag-client crates
- Proto definitions at `../proto/agent.proto` - has 8 action types, but defend_the_center scenario uses only 3 (MoveLeft, MoveRight, Attack)
- Proto package: `clau_doom.agent` -> Rust module: `clau_doom::agent`
- Benchmark scaffold at `benches/decision_cascade.rs`
- Binary: `agent-server` at `src/main.rs`

## Architecture Decisions
- GameState has `tick: u32` field, now also in proto (field 11)
- Proto `cascade_mode` (field 12) allows per-request DOE condition override
- Proto Action has `confidence` (field 4) and `rule_matched` (field 5)
- Action enum uses `Hash` derive for use in HashSet (needed by cascade random mode tests)
- RuleEngine sorts rules by priority descending on add - O(n log n) per add but rules are few
- DecisionCascade uses xorshift64 for deterministic random mode (seed reproducibility for DOE)
- RagClient fields prefixed with `_` when unused (scaffold phase) to avoid warnings
- Decision level 255 used for both random and fallback - distinguish via rule_matched field
- AgentServer uses Arc<Mutex<DecisionCascade>> for thread-safe gRPC handler access
- Per-request cascade_mode creates a temporary DecisionCascade (DOE flexibility)
- StreamTick returns Unimplemented for now

## gRPC Server
- Proto action type mapping: internal MoveLeft(0)->proto MOVE_LEFT(1), MoveRight(1)->MOVE_RIGHT(2), Attack(2)->ATTACK(7)
- build.rs uses tonic-build with build_server(true), build_client(false)
- futures-core dependency needed for BoxStream type in StreamTick
- Env vars: OPENSEARCH_URL, GRPC_PORT(50051), CASCADE_MODE, SEED(42), HEALTH_THRESHOLD(0.3), DUCKDB_PATH

## Key Patterns
- `make_state()` test helper consolidates GameState construction
- All latency measured with `std::time::Instant` and stored as nanoseconds
- L0 latency target: < 1ms (1_000_000 ns)
- Full cascade latency target: < 100ms (100_000_000 ns)
- Confidence = 1.0 for deterministic L0 rules, 0.0 for random/fallback
- proto module exposed via `pub mod proto { tonic::include_proto!(...) }` inside grpc/mod.rs

## Dependencies
- serde + serde_json for serialization
- tokio for async (rag client, gRPC server)
- duckdb with bundled feature
- reqwest with json feature (for OpenSearch HTTP)
- tonic + prost for gRPC
- tonic-build in build-dependencies
- futures-core for BoxStream
- criterion for benchmarks
- tracing + tracing-subscriber for structured logging

## Test Results (Phase 1 Complete)
- 33 tests, all passing
- game: 6 tests (action round-trip, health fraction, low health/ammo)
- strategy: 10 tests (rule matching, priority, compound conditions, enable/disable)
- rag: 4 tests (scoring weights, client enable/disable)
- cascade: 10 tests (random mode, rule-only, full-rag fallback, latency, determinism)
- grpc: 3 tests (action mapping, state conversion, cascade mode parsing)

## Next Steps (TODO)
- L1 DuckDB cache implementation in cascade
- L2 OpenSearch kNN actual HTTP queries
- Benchmark with real cascade (update benches/decision_cascade.rs)
- Scoring crate extraction if complexity warrants it
- StreamTick implementation (streaming RPC)

## Build Notes
- protoc must be installed (`brew install protobuf` on macOS)
- duckdb bundled feature compiles from source (slow first build)
- cargo check/test run from agent-core/ directory
