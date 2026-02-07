---
name: doe-execution
description: DOE experiment execution including matrix decomposition, MD variable injection, and container management
user-invocable: false
---

# DOE Execution Skill

Handles the operational execution of designed experiments: matrix decomposition into parallel sub-agent assignments, variable injection into agent Markdown files, Docker container lifecycle, and data collection.

## DOE Matrix Decomposition

### Parallel Assignment Strategy

Claude Code Task tool supports max 4 parallel sub-agents. Decompose the DOE matrix into batches of 4:

```
DOE matrix: 11 design points * 3 seeds = 33 runs

Batch 1: Runs 1-4   → 4 parallel containers
Batch 2: Runs 5-8   → 4 parallel containers
Batch 3: Runs 9-12  → 4 parallel containers
...
Batch 9: Runs 33    → 1 container (remainder)
```

Assignment algorithm:
1. Sort runs by expected duration (longest first for load balancing)
2. Assign to 4 slots using greedy bin-packing
3. Each slot maps to one player container (player_001 through player_004)
4. Track assignment in DuckDB `run_assignments` table

### Batch Scheduling

```
for each batch in batches:
  1. Inject MD variables for all 4 runs
  2. Restart all 4 containers simultaneously
  3. Monitor until all 4 complete or timeout
  4. Collect results from all 4
  5. Validate data completeness
  6. Proceed to next batch
```

Inter-batch gap: minimum 10 seconds for container cleanup.

## MD Variable Injection

### Target Files

Agent behavior is controlled by Markdown (.md) configuration files. DOE factors map to specific fields in these files.

```
Injection targets:
  agents/player_XXX/config.md
    - retreat_threshold: float [0.0, 1.0]
    - ammo_conservation: float [0.0, 1.0]
    - exploration_priority: float [0.0, 1.0]
    - aggression_level: float [0.0, 1.0]
    - health_caution: float [0.0, 1.0]
```

### Injection Process

1. Read current agent config.md
2. Parse YAML frontmatter or parameter section
3. Replace factor values with experimental levels
4. Write modified config.md
5. Verify write was successful (read-back check)

```python
# Pseudocode for MD injection
def inject_factors(agent_dir, factor_values, run_id):
    config_path = f"{agent_dir}/config.md"
    config = read_md(config_path)

    for factor_name, factor_value in factor_values.items():
        config = set_parameter(config, factor_name, factor_value)

    config = set_parameter(config, "run_id", run_id)
    config = set_parameter(config, "seed", get_seed_for_run(run_id))

    write_md(config_path, config)
    verify_md(config_path, factor_values)
```

### Rollback on Failure

If injection fails or container fails to start:
1. Restore original config.md from backup
2. Log failure with factor values and error
3. Mark run as FAILED in DuckDB
4. Continue with remaining runs in batch

Always create backup before injection:
```bash
cp config.md config.md.bak.{run_id}
```

## Seed Set Management

### Fixed Seeds for Reproducibility

Each experiment uses a fixed set of seeds. Seeds are assigned per replicate, not per design point.

```yaml
seed_sets:
  replicate_1: 42
  replicate_2: 137
  replicate_3: 256
  replicate_4: 789    # spare
  replicate_5: 1024   # spare
```

### Seed Injection

Seeds control:
- Game map random generation
- Enemy spawn patterns
- Item placement
- Agent decision noise (if stochastic)

Seed is injected alongside factor values:
```yaml
run_config:
  run_id: EXP001-R03-S2
  experiment_id: EXP-001
  design_point: 3
  replicate: 2
  seed: 137
  factors:
    retreat_threshold: 0.60
    ammo_conservation: 0.30
    exploration_priority: 0.20
```

### Seed Validation

Before starting a run, verify:
- Seed has not been used for this design point in this experiment
- Seed is in the approved seed set
- Seed is recorded in run_assignments table

## Container Restart Workflow

### Standard Restart Sequence

```bash
# 1. Stop container gracefully (allow current tick to finish)
docker compose stop player_001

# 2. Inject new MD variables (while container is stopped)
inject_factors(agent_dir="./agents/player_001", ...)

# 3. Start container with clean state
docker compose up -d player_001

# 4. Verify container is healthy
docker compose ps player_001  # should show "running"

# 5. Wait for game initialization
sleep 5  # allow game engine to initialize

# 6. Verify agent is connected to game server
docker compose logs --tail=10 player_001 | grep "Connected"
```

### Batch Restart (4 containers)

```bash
# Stop all 4
docker compose stop player_001 player_002 player_003 player_004

# Inject all 4 (can be parallel since different files)
for i in 1 2 3 4; do
  inject_factors(agent_dir="./agents/player_00${i}", ...)
done

# Start all 4
docker compose up -d player_001 player_002 player_003 player_004

# Health check all 4
for i in 1 2 3 4; do
  verify_health("player_00${i}")
done
```

### Container Health Checks

| Check | Method | Timeout |
|-------|--------|---------|
| Container running | `docker compose ps` | 30s |
| Process alive | `docker compose top` | 10s |
| Game connected | Log grep for "Connected" | 60s |
| First tick received | Log grep for "tick" | 120s |

If any check fails: stop container, log error, mark run as FAILED.

## Progress Monitoring

### Real-time Monitoring

Monitor each running container for:
- Game ticks processed (progress indicator)
- Kill count (performance metric)
- Death events (survival metric)
- Ammo usage (efficiency metric)
- Error messages (health indicator)

```bash
# Monitor logs for progress
docker compose logs -f --tail=0 player_001 | while read line; do
  parse_and_record(line)
done
```

### Progress Recording to DuckDB

```sql
INSERT INTO run_progress (
  run_id, timestamp, game_tick,
  kills, deaths, ammo_used, health_remaining,
  exploration_pct, status
) VALUES (?, NOW(), ?, ?, ?, ?, ?, ?, 'running');
```

### Completion Detection

A run is complete when:
- Game engine signals "map complete" or "game over"
- Maximum tick count reached (configurable, default 10000)
- Agent dies and no respawn configured
- Timeout reached (configurable, default 600s)

### Early Stopping Criteria

Stop a run early if:
- Agent stuck in loop (same position for 100+ ticks)
- Container memory exceeds limit (OOM imminent)
- Error rate exceeds threshold (10+ errors per minute)
- Game server disconnection

Log early stop reason in DuckDB.

## Data Collection to DuckDB

### Run Completion Data

After each run completes:

```sql
INSERT INTO experiment_runs (
  run_id, experiment_id, design_point, replicate, seed,
  factor_values,  -- JSON blob
  start_time, end_time, duration_seconds,
  status,  -- COMPLETED, FAILED, EARLY_STOPPED
  -- Response variables
  kills, deaths, survival_time_ticks,
  damage_dealt, damage_taken,
  ammo_used, ammo_efficiency,
  health_items_used, armor_items_used,
  exploration_pct, distance_traveled,
  -- Computed metrics
  kill_death_ratio, damage_efficiency,
  score
) VALUES (...);
```

### Data Validation

After collection, validate:
- All response variables are non-null (unless run failed)
- Values are within expected ranges
- No duplicate run_id entries
- Replicate count matches design specification

### Summary Statistics

After all runs for a design point complete:

```sql
SELECT
  design_point,
  AVG(kills) as mean_kills,
  STDDEV(kills) as sd_kills,
  AVG(survival_time_ticks) as mean_survival,
  STDDEV(survival_time_ticks) as sd_survival,
  COUNT(*) as n_replicates
FROM experiment_runs
WHERE experiment_id = ?
GROUP BY design_point;
```

## Run Scheduling and Resource Management

### Resource Constraints

```yaml
constraints:
  max_parallel_containers: 4
  max_memory_per_container: 2GB
  max_cpu_per_container: 1.0
  total_memory_budget: 10GB
  total_cpu_budget: 4.0
```

### Queue Management

```
Run Queue States:
  PENDING    → waiting to be scheduled
  INJECTING  → MD variables being written
  STARTING   → container starting
  RUNNING    → game in progress
  COLLECTING → extracting results
  COMPLETED  → results in DuckDB
  FAILED     → error occurred, logged
```

### Failure Recovery

On batch failure:
1. Stop all containers in batch
2. Restore all config.md from backups
3. Record failure details
4. Re-queue failed runs for next available batch
5. Maximum 2 retries per run before marking as PERMANENT_FAILURE

## Output Artifacts

After execution completes:

```
artifacts/
  EXP-001/
    run_assignments.csv     # Which run on which container
    raw_logs/               # Container logs per run
      run_001.log
      run_002.log
    progress/               # Tick-by-tick progress
      run_001_progress.csv
    summary.csv             # Aggregated results
    failures.csv            # Failed run details
```
