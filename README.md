# clau-doom

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Rust](https://img.shields.io/badge/Rust-stable-orange.svg)](https://www.rust-lang.org/)
[![Go](https://img.shields.io/badge/Go-1.21+-00ADD8.svg)](https://golang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docs.docker.com/compose/)
[![Status](https://img.shields.io/badge/Status-Phase%202%20In%20Progress-green.svg)]()

**Can LLM-orchestrated multi-agent systems systematically optimize game-playing AI -- without ever calling an LLM during gameplay?**

clau-doom investigates this question using DOOM (VizDoom) as the experimental platform. Agents make decisions through a multi-level cascade of hardcoded rules, cached experience, and vector-searched strategy documents. LLM reasoning (Claude Code CLI) is used exclusively *between* episodes for retrospection, experiment design, and generational evolution -- never during the gameplay loop.

The research applies industrial quality engineering methodology: Design of Experiments (DOE) with ANOVA-based analysis, fixed seed sets for reproducibility, and a formal audit trail from hypothesis to finding.

[Korean version / 한국어 버전](README_ko.md)

---

## Table of Contents

- [Architecture](#architecture)
- [Decision Hierarchy](#decision-hierarchy)
- [Research Methodology](#research-methodology)
- [Research Status](#research-status)
- [Key Findings](#key-findings)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Commands](#commands)
- [Contributing](#contributing)
- [Citation](#citation)
- [License](#license)

---

## Architecture

```
                          HOST (macOS / Linux)
    ┌──────────────────────────────────────────────────────────┐
    │                                                          │
    │   Claude Code CLI (Orchestrator)                         │
    │   ┌────────────────────────────────────────────────┐     │
    │   │  18 Sub-agents  |  32 Skills  |  20 Rules      │     │
    │   │                                                │     │
    │   │  research-pi ──> DOE Design                    │     │
    │   │  research-analyst ──> ANOVA / Statistics        │     │
    │   │  research-doe-runner ──> Experiment Execution   │     │
    │   │  research-evolution-mgr ──> Generational Evo    │     │
    │   └────────────────────────────────────────────────┘     │
    │          |                                               │
    │          | (between episodes only)                       │
    │          v                                               │
    │   ┌──────────────────── Docker Compose ──────────────┐   │
    │   │                                                  │   │
    │   │  ┌──────────┐   gRPC    ┌────────────┐           │   │
    │   │  │ VizDoom  │ <------> │ Agent Core │           │   │
    │   │  │ + Xvfb   │          │   (Rust)   │           │   │
    │   │  │ + noVNC   │          │  < 100ms   │           │   │
    │   │  └──────────┘          └──────┬─────┘           │   │
    │   │       |                       |                  │   │
    │   │       |  Python Glue          |                  │   │
    │   │       |  (DOE executor,       |                  │   │
    │   │       |   episode runner)     |                  │   │
    │   │       |                       v                  │   │
    │   │       |            ┌──────────────────┐          │   │
    │   │       |            │   OpenSearch     │          │   │
    │   │       |            │   (kNN RAG)      │          │   │
    │   │       |            └──────────────────┘          │   │
    │   │       |                                          │   │
    │   │       v            ┌──────────────────┐          │   │
    │   │  ┌─────────┐      │      NATS        │          │   │
    │   │  │ DuckDB  │      │   (messaging)    │          │   │
    │   │  │ (logs)  │      └──────────────────┘          │   │
    │   │  └─────────┘                                    │   │
    │   └──────────────────────────────────────────────────┘   │
    └──────────────────────────────────────────────────────────┘
```

The system separates **real-time decision-making** (Rust, sub-100ms) from **offline reasoning** (Claude Code CLI, seconds to minutes). During gameplay, no LLM is invoked. Between episodes, the LLM orchestrator analyzes performance, designs experiments, and evolves agent strategies.

---

## Decision Hierarchy

The agent core uses a four-level decision cascade, where each level adds latency but increases decision quality:

| Level | Engine | Latency | Description |
|-------|--------|---------|-------------|
| L0 | Rust (hardcoded) | < 1ms | Reflex rules: health-based retreat, ammo management, target nearest |
| L1 | DuckDB (SQL) | < 10ms | Per-agent play history, frequently accessed patterns |
| L2 | OpenSearch (kNN) | < 100ms | Strategy document retrieval, cross-agent know-how search |
| L3 | Claude Code CLI | seconds | Episode retrospection, DOE design, evolution (async, offline only) |

**No real-time LLM calls during gameplay.** The core research claim is that agent skill equals `Document Quality x Scoring Accuracy` -- improvement comes from refining RAG documents and optimizing Rust decision weights, not from in-loop LLM inference.

---

## Research Methodology

### Design of Experiments (DOE)

All optimization follows industrial DOE methodology rather than ad-hoc hyperparameter tuning:

- **Phase 0 (OFAT)**: One-factor-at-a-time screening to identify candidate factors
- **Phase 1 (Factorial)**: Full/fractional factorial designs to quantify main effects and interactions
- **Phase 2 (RSM)**: Response Surface Methodology (CCD/BBD) to find optimal regions
- **Phase 3 (Split-Plot)**: Complex constrained designs for multi-objective optimization

### Statistical Rigor

Every experimental claim carries formal statistical evidence:

- ANOVA with residual diagnostics (normality, equal variance, independence)
- Effect sizes (partial eta-squared, Cohen's d) for practical significance
- Fixed seed sets shared between control and treatment conditions
- Trust score framework: HIGH (p<0.01, n>=50, clean diagnostics), MEDIUM (p<0.05, n>=30), LOW (exploratory), UNTRUSTED (anecdotal)
- Complete audit trail: `Hypothesis -> Experiment Order -> Report -> Finding`

### Quality Engineering Integration

- **SPC**: Statistical Process Control charts for cross-generation anomaly detection
- **FMEA**: Failure Mode and Effects Analysis for experiment prioritization
- **TOPSIS**: Multi-criteria decision making for strategy selection when trade-offs exist

---

## Research Status

**Phase 1 complete. Phase 2 in progress.**

### Experiment Summary

| Experiment | Scenario | Key Result | Status |
|------------|----------|------------|--------|
| DOE-001 | defend_the_center | Full agent >> Random (d=5.28) | Complete |
| DOE-002 | defend_the_center | Mock data -- Memory/Strength effects invalidated | Invalidated |
| DOE-003~004 | -- | Infrastructure validation, KILLCOUNT bug found | Complete |
| DOE-005~006 | defend_the_center | Zero variance, factor injection failure | Complete |
| DOE-007 | defend_the_center | Cannot discriminate architectures (kills 0-3) | Complete |
| DOE-008 | defend_the_line | **First significant result** -- architecture matters (p=0.0006) | Complete |
| DOE-009 | defend_the_line | Memory/Strength confirmed null (p=0.736) | Complete |
| DOE-010 | defend_the_line | Structured patterns do not beat random in 3-action space | Complete |
| DOE-011 | defend_the_line | 5-action space creates rate-vs-total tradeoff | Complete |
| DOE-012~020 | defend_the_line | Systematic strategy exploration (9 experiments) | Complete |
| DOE-021~023 | defend_the_line | Generational evolution design | Ordered |

**Totals**: 20 experiments executed, 3420+ episodes, 45 findings (38 adopted, 7 invalidated).

### Phase Progression

```
Phase 0 (Screening)     [=============================] Complete
Phase 1 (Main Effects)  [=============================] Complete
Phase 2 (Optimization)  [====                         ] In Progress
Phase 3 (Evolution)     [                             ] Planned
```

---

## Key Findings

Selected findings from 45 total (see `research/FINDINGS.md` for full details):

1. **F-010**: Pure reflex rules (L0_only) are significantly inferior on defend_the_line. Any mechanism introducing lateral movement breaks tunnel vision (p=0.000019, d=0.94). *Trust: HIGH.*

2. **F-012**: Scenario selection is critical. defend_the_line provides 8x the kill range and 3x larger effect sizes compared to defend_the_center. *Trust: HIGH.*

3. **F-013~F-015**: Memory and strength weight parameters have NO effect on kill_rate in real VizDoom gameplay (p=0.736). Prior mock data findings invalidated. *Trust: HIGH.*

4. **F-024**: Kill rate and total kills are inversely ranked across strategies -- single-metric optimization is insufficient. *Trust: HIGH.*

5. **F-039**: burst_3 (3 attacks + 1 turn) is Pareto-optimal by TOPSIS analysis (C_i=0.974), ranking first across all weight schemes. *Trust: HIGH.*

6. **F-045**: Three equalization forces (weapon cooldown, stochastic displacement, enemy uniformity) create a performance convergence zone at 42-46 kills/min for all viable strategies. *Trust: MEDIUM.*

---

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Rust (stable toolchain)
- Go 1.22+
- Python 3.11+
- Make

### Setup

```bash
# Clone the repository
git clone https://github.com/baekenough/clau-doom.git
cd clau-doom

# Build all components (Rust agent core, Go orchestrator)
make build

# Install Python dependencies (VizDoom glue)
cd glue && pip install -r requirements.txt && cd ..

# Build and start the Docker stack
make docker-build
make docker-up

# Verify services are running
# VizDoom + noVNC: http://localhost:6901
# OpenSearch:      http://localhost:9200
# NATS Monitor:    http://localhost:8222
```

### Running an Experiment

Experiments are designed using the DOE methodology and executed through the Python glue layer:

```bash
# Run an experiment inside Docker (example: DOE-020 best-of-breed)
docker exec clau-doom-player python3 -m glue.doe_executor --experiment DOE-020

# View results in DuckDB
docker exec clau-doom-player python3 -c "
import duckdb
con = duckdb.connect('/app/data/doe020.duckdb', read_only=True)
print(con.execute('SELECT condition, COUNT(*), AVG(kills), AVG(kill_rate) FROM experiments GROUP BY condition').fetchdf())
"
```

### Stopping the Stack

```bash
make docker-down
```

---

## Project Structure

```
clau-doom/
├── agent-core/              # Rust decision engine (gRPC server)
│   ├── src/
│   │   ├── main.rs          # Agent server entry point
│   │   ├── lib.rs           # Library entry point
│   │   ├── cascade.rs       # L0/L1/L2 decision cascade logic
│   │   ├── cache/           # Cache module
│   │   ├── game/            # Game state module
│   │   ├── grpc/            # gRPC server module
│   │   ├── rag/             # RAG client module
│   │   └── strategy/        # Strategy module
│   ├── benches/             # Decision latency benchmarks
│   └── Cargo.toml
├── cmd/                     # Go CLI and orchestrator
│   ├── clau-doom/           # Main CLI binary
│   └── orchestrator/        # Agent lifecycle manager
├── glue/                    # Python VizDoom binding + DOE executor
│   ├── action_functions.py  # 21 strategy class implementations
│   ├── doe_executor.py      # DOE experiment execution engine
│   └── tests/               # Python test suite
├── proto/                   # gRPC protocol definitions
│   ├── agent.proto          # Agent decision service
│   └── orchestrator.proto   # Lifecycle management service
├── infra/                   # Docker infrastructure
│   ├── docker-compose.yml   # Service definitions
│   └── docker/              # Dockerfiles per service
├── research/                # Research documentation
│   ├── experiments/         # 23 experiment orders, 19 reports
│   ├── analyses/            # TOPSIS, information theory
│   ├── FINDINGS.md          # 45 research findings
│   ├── HYPOTHESIS_BACKLOG.md
│   ├── RESEARCH_LOG.md
│   ├── DOE_CATALOG.md
│   ├── SPC_STATUS.md
│   └── FMEA_REGISTRY.md
├── docs/                    # Literature review, design documents
├── guides/                  # Reference docs (18 topics)
├── .claude/                 # Claude Code agent definitions
│   ├── agents/              # 18 sub-agent definitions
│   ├── skills/              # 32 skill definitions
│   └── rules/               # 20 project rules (R000-R102)
├── Makefile
└── go.mod
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| Agent Core | Rust + Tokio + Tonic | gRPC decision engine, < 100ms P99 |
| Orchestrator | Go + Cobra | Agent lifecycle, CLI, gRPC client |
| Game Glue | Python + VizDoom | Scenario execution, DOE runner |
| RAG Search | OpenSearch 2.17 | kNN vector search for strategy docs |
| Local DB | DuckDB | Per-experiment play logs, SQL analytics |
| Messaging | NATS | Agent pub/sub broadcast |
| Game Engine | VizDoom + Xvfb + noVNC | DOOM scenarios, headless rendering |
| AI Reasoning | Claude Code CLI | Experiment design, analysis, evolution |
| Infra | Docker Compose | Full stack orchestration |

### Container Stack

| Container | Port | Purpose |
|-----------|------|---------|
| doom-player | 6901 (noVNC), 5900 (VNC) | VizDoom game environment |
| agent-core | 50052 | Rust gRPC decision engine |
| opensearch | 9200 | RAG vector search |
| nats | 4222, 8222 | Messaging, monitoring |

---

## Commands

```bash
make build          # Build Rust agent core + Go orchestrator
make test           # Run all test suites (Rust, Go, Python)
make proto-gen      # Regenerate gRPC code from .proto definitions
make docker-build   # Build Docker images
make docker-up      # Start Docker Compose stack
make docker-down    # Stop Docker Compose stack
make bench          # Run Rust decision cascade benchmarks
make clean          # Remove build artifacts
```

---

## Contributing

Contributions are welcome. Please follow these guidelines:

1. **Branch strategy**: Create feature branches from `main` (`feature/*`, `experiment/*`, `docs/*`).
2. **Commit convention**: Use `type(scope): subject` format (e.g., `feat(agent-core): add L2 cache fallback`, `exp(research): DOE-024 compound strategy exploration`).
3. **Experiment integrity**: All experiments must use fixed seed sets, include ANOVA with residual diagnostics, and follow the audit trail (Hypothesis -> Order -> Report -> Finding). See `research/` for examples.
4. **Testing**: Run `make test` before submitting a pull request.
5. **Statistical claims**: Include evidence markers (`[STAT:p=...]`, `[STAT:ci=...]`) for all quantitative claims.

---

## Citation

If you use clau-doom in your research, please cite:

```bibtex
@misc{clau-doom2026,
  title     = {clau-doom: Systematic Optimization of Game-Playing AI
               through RAG, DOE, and Generational Evolution},
  author    = {Yi, Sang},
  year      = {2026},
  url       = {https://github.com/baekenough/clau-doom},
  note      = {Work in progress. Target venues: NeurIPS, ICML.}
}
```

### Research Contributions

1. **RAG-based skill accumulation** without real-time LLM inference
2. **DOE-driven systematic optimization** replacing ad-hoc hyperparameter tuning
3. **Quality engineering for generational evolution** (SPC, FMEA, TOPSIS)
4. **Reproducible multi-agent research framework** with full audit trail

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
