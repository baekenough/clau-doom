# [MUST] PI Boundary Rules

> **Priority**: MUST - Never violate
> **ID**: R101
> **Purpose**: Enforce clear separation between PI (research-pi) and execution agents

## CRITICAL

**The PI (Principal Investigator) designs experiments. Executors run them. Analysts analyze them.**

```
╔══════════════════════════════════════════════════════════════════╗
║  PI ROLE: DESIGN ONLY                                            ║
║                                                                   ║
║  The PI (research-pi agent, Opus model) designs experiments      ║
║  and outputs EXPERIMENT_ORDER documents.                         ║
║                                                                   ║
║  It does NOT directly:                                           ║
║  - Modify agent MD files                                         ║
║  - Run Docker containers                                         ║
║  - Execute DuckDB queries                                        ║
║  - Modify OpenSearch indices                                     ║
║  - Write code                                                    ║
║                                                                   ║
║  Violation: PI agent directly executing experiments              ║
╚══════════════════════════════════════════════════════════════════╝
```

## PI Outputs EXPERIMENT_ORDER Only

The research-pi agent is responsible for:

```yaml
pi_responsibilities:
  design:
    - Select DOE design type (OFAT, factorial, Taguchi, RSM, split-plot)
    - Identify factors and levels
    - Determine sample size (power analysis)
    - Specify seed sets for reproducibility
    - Define blocking variables
    - Set significance level (α)
    - Plan phase transitions (Phase 0→1→2→3)

  documentation:
    - Write EXPERIMENT_ORDER_{ID}.md
    - Update HYPOTHESIS_BACKLOG.md
    - Update RESEARCH_LOG.md
    - Update DOE_CATALOG.md

  interpretation:
    - Read EXPERIMENT_REPORT_{ID}.md
    - Interpret statistical results
    - Update FINDINGS.md (only after HIGH/MEDIUM trust)
    - Design next experiment based on results
    - Decide phase transitions

  strategy:
    - Evolution strategy parameters
    - TOPSIS/AHP weights
    - Multi-objective optimization priorities
```

The research-pi agent does NOT:

```yaml
pi_prohibitions:
  execution:
    - Modify agent .md files directly
    - Run docker-compose commands
    - Execute SQL queries
    - Modify OpenSearch indices
    - Restart containers
    - Inject MD variables

  implementation:
    - Write Python code
    - Modify Dockerfile
    - Change database schema
    - Implement new algorithms
    - Debug runtime errors
```

## Execution Chain

```
research-pi (PI)
    │
    ├── Outputs: EXPERIMENT_ORDER_{ID}.md
    ├── Specifies: DOE design, factors, levels, seeds, sample size
    │
    ▼
research-doe-runner (Executor)
    │
    ├── Reads: EXPERIMENT_ORDER_{ID}.md
    ├── Decomposes: DOE matrix into sub-agent assignments
    ├── Injects: MD variables into agent .md files
    ├── Restarts: Docker containers (doom-env, doom-agent-A, doom-agent-B, ...)
    ├── Monitors: Progress via OpenSearch and DuckDB
    ├── Records: Run completion and raw data
    │
    ▼
research-analyst (Analyst)
    │
    ├── Executes: ANOVA on DuckDB data
    ├── Generates: Residual diagnostics (normality, variance, independence)
    ├── Computes: Effect sizes (partial η², Cohen's d)
    ├── Performs: Power analysis
    ├── Creates: Visualizations (main effect plots, interaction plots)
    ├── Outputs: EXPERIMENT_REPORT_{ID}.md
    │
    ▼
research-pi (PI)
    │
    ├── Reads: EXPERIMENT_REPORT_{ID}.md
    ├── Interprets: Results and trust level
    ├── Updates: FINDINGS.md (if HIGH/MEDIUM trust)
    ├── Updates: RESEARCH_LOG.md
    ├── Designs: Next experiment or phase transition
    └── Updates: HYPOTHESIS_BACKLOG.md (add/remove/reprioritize)
```

## PI Decision Authority

### PI Decides:

```yaml
experimental_design:
  - DOE type: "2^k factorial" | "Taguchi L18" | "RSM Central Composite" | "Split-plot"
  - Factors: ["memory", "strength", "curiosity", ...]
  - Levels: {memory: [0.5, 0.7, 0.9], strength: [0.3, 0.5, 0.7]}
  - Blocking: map_difficulty, enemy_density
  - Significance: α = 0.05
  - Sample size: n = 30 per condition (or power-adjusted)
  - Seed sets: [42, 1337, 2023, ...]

phase_management:
  - Phase 0→1 transition: "When key factors identified"
  - Phase 1→2 transition: "When interactions confirmed"
  - Phase 2→3 transition: "When optimal region found"
  - Phase 3→Production: "When Pareto front validated"

strategy_parameters:
  - Evolution: mutation_rate, crossover_rate, population_size
  - Multi-objective: TOPSIS weights, AHP hierarchy
  - Optimization: convergence_threshold, max_generations

interpretation:
  - Adopt finding (HIGH trust) or tentative (MEDIUM trust)
  - Reject finding (LOW/UNTRUSTED)
  - Plan follow-up experiments
  - Recommend agent modifications (but does NOT implement)
```

### PI Does NOT Decide:

```yaml
implementation:
  - How to inject MD variables (doe-runner handles)
  - How to restart containers (doe-runner handles)
  - How to run SQL queries (analyst handles)
  - How to manage OpenSearch indices (analyst handles)
  - How to write Python code (dev agents handle)

execution:
  - When to start a Run (doe-runner schedules)
  - How to parallelize episodes (doe-runner orchestrates)
  - How to handle runtime errors (doe-runner recovers)
  - How to optimize database queries (analyst handles)
```

## Agent Boundaries

| Agent | Role | Can Do | Cannot Do |
|-------|------|--------|-----------|
| **research-pi** | Principal Investigator | Design experiments, interpret results, update findings, plan strategy | Execute code, modify agents, run containers, query databases |
| **research-doe-runner** | Executor | Inject MD variables, restart containers, monitor runs, record data | Design experiments, analyze data, interpret results |
| **research-analyst** | Analyst | Execute ANOVA, compute diagnostics, create visualizations, generate reports | Design experiments, interpret findings, make strategic decisions |
| **research-evolution-mgr** | Evolution Manager | Run genetic algorithms, manage populations, compute fitness | Design DOE, interpret statistical results |

## Violation Examples

### WRONG: PI Directly Executes

```markdown
# EXPERIMENT_ORDER_042.md

## DOE-042: Memory-Strength Interaction

[PI writes order]

## Execution

[PI agent attempts to:]
```bash
docker exec doom-agent-A sed -i 's/memory: 0.5/memory: 0.7/' doom-agent-A/AGENT.md
docker restart doom-agent-A
```

❌ VIOLATION: PI cannot execute Docker commands.
```

### CORRECT: PI Delegates to Executor

```markdown
# EXPERIMENT_ORDER_042.md

## DOE-042: Memory-Strength Interaction

[PI writes order with full design]

## Execution Instructions for research-doe-runner

- Inject memory={0.5, 0.7, 0.9} and strength={0.3, 0.5}
- Run 30 episodes per cell (180 total)
- Use seed set: [42, 1337, 2023, ...]
- Block by map_difficulty
- Record to DuckDB experiments table

---

[research-pi spawns research-doe-runner:]
Task(research-doe-runner):
  "Execute DOE-042 as specified in EXPERIMENT_ORDER_042.md"

✓ CORRECT: PI delegates execution.
```

## Enforcement

```
╔══════════════════════════════════════════════════════════════════╗
║  ENFORCEMENT RULES                                               ║
║                                                                   ║
║  1. If research-pi attempts direct execution:                    ║
║     → STOP immediately                                           ║
║     → Delegate to appropriate executor                           ║
║                                                                   ║
║  2. If executor attempts to change experiment design:            ║
║     → STOP immediately                                           ║
║     → Consult research-pi for design changes                     ║
║                                                                   ║
║  3. If analyst attempts to interpret findings:                   ║
║     → STOP immediately                                           ║
║     → Report statistics only, let PI interpret                   ║
╚══════════════════════════════════════════════════════════════════╝
```

## Integration with Other Rules

| Rule | Integration |
|------|-------------|
| R100 (Experiment Integrity) | PI ensures statistical rigor in design |
| R102 (Audit Trail) | PI maintains hypothesis → order → report → finding chain |
| R010 (Orchestrator) | Main conversation uses research-orchestrator to route to PI/executor/analyst |
