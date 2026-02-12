# Experiment Data Export

CSV exports from DuckDB databases for git-tracked reproducibility.
Enables statistical analysis reproduction without VizDoom runtime.

## Files

| File | Rows | Description |
|------|------|-------------|
| `experiments_all.csv` | 8,700 | Episode-level data for all experiments (DOE-001 through DOE-045) |
| `experiments_doe002.csv` | 150 | DOE-002 data (different schema, early infrastructure experiment) |
| `seed_sets.csv` | 36 | Seed configurations for reproducibility |
| `experiment_summary.csv` | 230 | Aggregated per-condition statistics |

## Schema: experiments_all.csv

| Column | Type | Description |
|--------|------|-------------|
| experiment_id | VARCHAR | DOE identifier (e.g., "DOE-042", "DOE-044_gen3") |
| run_id | VARCHAR | Run identifier within experiment |
| condition | VARCHAR | Experimental condition label |
| baseline_type | VARCHAR | Strategy type used |
| seed | INTEGER | Random seed for this episode |
| episode_number | INTEGER | Sequential episode number |
| kill_rate | DOUBLE | Kills per unit time |
| kills | INTEGER | Total enemy kills |
| survival_time | DOUBLE | Time survived (seconds) |
| damage_dealt | DOUBLE | Total damage dealt |
| damage_taken | DOUBLE | Total damage received |
| ammo_efficiency | DOUBLE | Hits per shot fired |
| exploration_coverage | DOUBLE | Map area explored (fraction) |
| decision_latency_p99 | DOUBLE | P99 decision time (ms) |
| rule_match_rate | DOUBLE | Fraction of decisions from rule cache |
| decision_level_counts | VARCHAR | JSON: count per decision level (L0/L1/L2) |
| total_ticks | INTEGER | Game ticks elapsed |
| shots_fired | INTEGER | Total shots fired |
| hits | INTEGER | Total hits on enemies |
| cells_visited | INTEGER | Unique map cells visited |
| started_at | TIMESTAMP | Episode start time |
| completed_at | TIMESTAMP | Episode end time |

## Schema: experiments_doe002.csv

Early infrastructure experiment with simplified schema:

| Column | Type | Description |
|--------|------|-------------|
| episode_id | INTEGER | Sequential ID |
| experiment_id | VARCHAR | "DOE-002" |
| run_id | VARCHAR | Run identifier |
| seed | INTEGER | Random seed |
| baseline_type | VARCHAR | Strategy type |
| memory_weight | DOUBLE | Memory factor level |
| strength_weight | DOUBLE | Strength factor level |
| kills | INTEGER | Total kills |
| survival_time | DOUBLE | Survival time (seconds) |
| kill_rate | DOUBLE | Kills per unit time |
| damage_dealt | DOUBLE | Damage dealt |
| damage_taken | DOUBLE | Damage taken |
| ammo_efficiency | DOUBLE | Hit accuracy |
| decision_latency_p99 | DOUBLE | P99 decision time (ms) |

## Experiment ID Conventions

- `DOE-NNN`: Standard experiment
- `DOE-NNN_genM`: Generation M of evolutionary experiment (DOE-021, DOE-044)
- `DOE-001-REAL`: Production validation run of DOE-001

## Episode Counts by Phase

| Phase | Experiments | Episodes | Description |
|-------|-------------|----------|-------------|
| Phase 0 | DOE-001, 001-REAL, 002, 005-010 | 1,500 | Infrastructure validation |
| Phase 1 | DOE-011-020 | 1,500 | Main effects exploration |
| Phase 2 | DOE-021-029 | 2,130 | Optimization and falsification |
| Phase 3 | DOE-030-035 | 1,300 | Confirmation and replication |
| Phase 4 | DOE-036-045 | 2,420 | Generalization and evolution |
| **Total** | **48 IDs** | **8,850** | |

Note: The consolidated DuckDB database contains 6,780 episodes (DOE-005~010, DOE-021~045).
Individual databases add 2,070 episodes (DOE-001, DOE-001-REAL, DOE-002, DOE-011~020).

## Reproducing Statistical Analysis

```python
import pandas as pd

# Load all episode data
df = pd.read_csv('experiments_all.csv')

# Filter to specific experiment
doe042 = df[df['experiment_id'] == 'DOE-042']

# Reproduce ANOVA (example)
from scipy import stats
groups = [g['kills'].values for _, g in doe042.groupby('condition')]
f_stat, p_value = stats.f_oneway(*groups)
print(f'F = {f_stat:.2f}, p = {p_value:.4f}')
```

## Source

Exported from DuckDB databases in `volumes/data/` on 2026-02-12.
Seed formula: `seed_i = base_seed + i * step` (deterministic).
