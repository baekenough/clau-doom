# Arch-Documenter Agent Memory

## Project Scaffolding (2026-02-07)

### Directory Structure Reference
- Rust agent-core: `agent-core/src/{strategy,rag,game}/mod.rs`
- Go CLI + orchestrator: `cmd/{clau-doom,orchestrator}/main.go`
- Python glue: `glue/vizdoom_bridge.py`
- Proto definitions: `proto/{agent,orchestrator}.proto`
- Volumes: `volumes/{agents/{templates,active},data,research}`
- `volumes/research` is a symlink to `../../research`

### .gitignore Pattern
- Volumes runtime data is ignored: `volumes/data/`, `volumes/opensearch/`, `volumes/mongo/`, `volumes/nats/`, `volumes/agents/active/`
- Templates directory IS tracked: `volumes/agents/templates/`
- .gitkeep files used for empty directories

### Proto Messages
- agent.proto: GameState (health, ammo, kills, enemies_visible, position, angle, episode_time, is_dead), Action (action_type enum, decision_level, latency_ms), AgentService (Tick, StreamTick)
- orchestrator.proto: SpawnAgent, StopAgent, RunExperiment, GetExperimentStatus

### Build Validation
- `cargo check` validates Rust (takes ~90s first time due to duckdb bundled build)
- `go build ./cmd/...` validates Go
- Reference docs: `docs/01_clau-doom-docs/docs/10-INFRA.md` (repo structure), `02-AGENT.md` (agent types)
