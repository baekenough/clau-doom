# Go Expert Agent Memory

## Project Structure
- Module: `github.com/sangyi/clau-doom` (go 1.22)
- CLI binary: `cmd/clau-doom/main.go` (cobra-based)
- Internal packages: `internal/experiment/`, `internal/config/`
- Build output: `build/` (gitignored)
- Proto files: `proto/agent.proto`, `proto/orchestrator.proto`

## Key Dependencies
- github.com/spf13/cobra v1.10.2 (CLI framework)
- github.com/spf13/pflag v1.0.9 (flag parsing, cobra dep)

## CLI Commands Implemented
- `clau-doom version` - prints version
- `clau-doom status` - shows system status
- `clau-doom init` - creates volume directories
- `clau-doom doe list` - lists available experiments
- `clau-doom doe run DOE-001` - runs DOE-001 (dry-run mode)
- `clau-doom doe status <id>` - placeholder

## DOE-001 Configuration
- 3 conditions: random, rule_only, full_agent
- 70 episodes per condition (configurable via --episodes-per-condition)
- Seed formula: seed_i = 42 + i * 31
- Factor: DECISION_MODE

## Patterns
- Build to `build/` directory, never project root
- Use context.Context for all long-running operations
- Runner continues on condition error (logs and moves to next)
- Seed sets are deterministic and shared across conditions
