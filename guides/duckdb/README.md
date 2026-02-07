# DuckDB Reference Guide

Reference documentation for DuckDB usage in clau-doom analytics and data processing.

## Key Resources

- [DuckDB Official Documentation](https://duckdb.org/docs/)
- [duckdb-rs Rust API](https://docs.rs/duckdb/latest/duckdb/)
- [DuckDB Python API](https://duckdb.org/docs/api/python/overview)
- [SQL Features Overview](https://duckdb.org/docs/sql/introduction)
- [Parquet with DuckDB](https://duckdb.org/docs/data/parquet/overview)

## clau-doom Context

DuckDB is the embedded analytics database for per-agent play logs, episode data, and DOE experiment results. Each agent instance maintains its own DuckDB file for local data, with aggregation happening at the analytics layer via Python.

Key characteristics:
- **Per-agent storage**: Each agent has `data/{agent_id}/play_logs.duckdb`
- **Column-oriented**: Optimized for analytical queries (aggregations, scans)
- **Embedded**: No separate server process, direct file access
- **Parquet-compatible**: Export to Parquet for cross-agent analysis
- **OLAP-focused**: Fast aggregations for DOE factor-level summaries and ANOVA input

Project data layout:
```
data/
├── doom-agent-A/
│   └── play_logs.duckdb         # Agent A's episodes, encounters, metrics
├── doom-agent-B/
│   └── play_logs.duckdb         # Agent B's episodes, encounters, metrics
├── doom-agent-C/
│   └── play_logs.duckdb         # Agent C's episodes, encounters, metrics
├── processed/
│   ├── experiment_021.parquet   # Aggregated data for DOE-021
│   ├── experiment_022.parquet   # Aggregated data for DOE-022
│   └── ...
└── raw/
    ├── DOE_021_seeds.txt        # Seed sets (read-only)
    └── ...
```

## Per-Agent Data Architecture

### File-per-Agent Pattern

Each agent maintains its own DuckDB file to avoid write contention and enable parallel episode execution. Aggregation queries run across multiple databases via ATTACH or Parquet export.

```
Agent A game loop → writes to data/doom-agent-A/play_logs.duckdb
Agent B game loop → writes to data/doom-agent-B/play_logs.duckdb
Agent C game loop → writes to data/doom-agent-C/play_logs.duckdb

Analytics layer → reads all three → aggregates → ANOVA input
```

### Schema Design

Tables are normalized for write efficiency and denormalized for read performance in analytical contexts.

#### episodes Table

Episode-level metrics for each game run.

```sql
CREATE TABLE IF NOT EXISTS episodes (
    episode_id INTEGER PRIMARY KEY,
    agent_id VARCHAR NOT NULL,
    seed INTEGER NOT NULL,
    generation INTEGER,
    run_id VARCHAR,
    experiment_id VARCHAR,
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    damage_dealt DOUBLE DEFAULT 0.0,
    damage_taken DOUBLE DEFAULT 0.0,
    survival_time_ms BIGINT DEFAULT 0,
    ammo_efficiency DOUBLE DEFAULT 0.0,
    items_collected INTEGER DEFAULT 0,
    exploration_coverage DOUBLE DEFAULT 0.0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_episodes_agent ON episodes(agent_id);
CREATE INDEX idx_episodes_run ON episodes(run_id);
CREATE INDEX idx_episodes_experiment ON episodes(experiment_id);
CREATE INDEX idx_episodes_seed ON episodes(seed);
```

#### encounters Table

Granular enemy engagement data for tactical analysis.

```sql
CREATE TABLE IF NOT EXISTS encounters (
    encounter_id INTEGER PRIMARY KEY,
    episode_id INTEGER NOT NULL,
    enemy_type VARCHAR NOT NULL,
    distance DOUBLE,
    weapon_used VARCHAR,
    hits INTEGER DEFAULT 0,
    misses INTEGER DEFAULT 0,
    result VARCHAR CHECK(result IN ('kill', 'death', 'flee')),
    reaction_time_ms BIGINT,
    health_before DOUBLE,
    health_after DOUBLE,
    timestamp_ms BIGINT,
    FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
);

CREATE INDEX idx_encounters_episode ON encounters(episode_id);
CREATE INDEX idx_encounters_enemy ON encounters(enemy_type);
CREATE INDEX idx_encounters_weapon ON encounters(weapon_used);
```

#### experiment_runs Table

DOE run metadata and factor assignments.

```sql
CREATE TABLE IF NOT EXISTS experiment_runs (
    run_id VARCHAR PRIMARY KEY,
    experiment_id VARCHAR NOT NULL,
    agent_id VARCHAR NOT NULL,
    factor_levels JSON NOT NULL,  -- {"memory": 0.7, "strength": 0.5}
    seed_set JSON NOT NULL,        -- [42, 1337, 2023, ...]
    episodes_planned INTEGER,
    episodes_completed INTEGER DEFAULT 0,
    status VARCHAR CHECK(status IN ('pending', 'running', 'completed', 'failed')),
    started_at TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_runs_experiment ON experiment_runs(experiment_id);
CREATE INDEX idx_runs_agent ON experiment_runs(agent_id);
CREATE INDEX idx_runs_status ON experiment_runs(status);
```

#### metrics Table

Time-series metrics for detailed performance tracking.

```sql
CREATE TABLE IF NOT EXISTS metrics (
    metric_id INTEGER PRIMARY KEY,
    episode_id INTEGER NOT NULL,
    metric_name VARCHAR NOT NULL,
    metric_value DOUBLE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
);

CREATE INDEX idx_metrics_episode ON metrics(episode_id);
CREATE INDEX idx_metrics_name ON metrics(metric_name);
```

## Rust duckdb-rs Patterns

### Opening Database

```rust
use duckdb::{Connection, Result};

fn open_agent_db(agent_id: &str) -> Result<Connection> {
    let db_path = format!("data/{}/play_logs.duckdb", agent_id);
    Connection::open(&db_path)
}

// In-memory for testing
fn open_in_memory() -> Result<Connection> {
    Connection::open_in_memory()
}
```

### Schema Creation on Startup

```rust
fn initialize_schema(conn: &Connection) -> Result<()> {
    conn.execute_batch(
        r#"
        CREATE TABLE IF NOT EXISTS episodes (
            episode_id INTEGER PRIMARY KEY,
            agent_id VARCHAR NOT NULL,
            seed INTEGER NOT NULL,
            generation INTEGER,
            run_id VARCHAR,
            experiment_id VARCHAR,
            kills INTEGER DEFAULT 0,
            deaths INTEGER DEFAULT 0,
            damage_dealt DOUBLE DEFAULT 0.0,
            damage_taken DOUBLE DEFAULT 0.0,
            survival_time_ms BIGINT DEFAULT 0,
            ammo_efficiency DOUBLE DEFAULT 0.0,
            items_collected INTEGER DEFAULT 0,
            exploration_coverage DOUBLE DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE INDEX IF NOT EXISTS idx_episodes_agent ON episodes(agent_id);
        CREATE INDEX IF NOT EXISTS idx_episodes_run ON episodes(run_id);
        CREATE INDEX IF NOT EXISTS idx_episodes_seed ON episodes(seed);

        CREATE TABLE IF NOT EXISTS encounters (
            encounter_id INTEGER PRIMARY KEY,
            episode_id INTEGER NOT NULL,
            enemy_type VARCHAR NOT NULL,
            distance DOUBLE,
            weapon_used VARCHAR,
            hits INTEGER DEFAULT 0,
            misses INTEGER DEFAULT 0,
            result VARCHAR CHECK(result IN ('kill', 'death', 'flee')),
            reaction_time_ms BIGINT,
            health_before DOUBLE,
            health_after DOUBLE,
            timestamp_ms BIGINT,
            FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
        );

        CREATE INDEX IF NOT EXISTS idx_encounters_episode ON encounters(episode_id);
        "#,
    )
}
```

### Prepared Statements and Parameterized Queries

```rust
use duckdb::params;

fn insert_episode(
    conn: &Connection,
    agent_id: &str,
    seed: i32,
    kills: i32,
    deaths: i32,
    survival_time_ms: i64,
) -> Result<u64> {
    conn.execute(
        r#"
        INSERT INTO episodes (agent_id, seed, kills, deaths, survival_time_ms)
        VALUES (?, ?, ?, ?, ?)
        "#,
        params![agent_id, seed, kills, deaths, survival_time_ms],
    )
}

fn get_episodes_for_run(conn: &Connection, run_id: &str) -> Result<Vec<EpisodeRecord>> {
    let mut stmt = conn.prepare(
        r#"
        SELECT episode_id, seed, kills, deaths, survival_time_ms, ammo_efficiency
        FROM episodes
        WHERE run_id = ?
        ORDER BY episode_id
        "#,
    )?;

    let rows = stmt.query_map(params![run_id], |row| {
        Ok(EpisodeRecord {
            episode_id: row.get(0)?,
            seed: row.get(1)?,
            kills: row.get(2)?,
            deaths: row.get(3)?,
            survival_time_ms: row.get(4)?,
            ammo_efficiency: row.get(5)?,
        })
    })?;

    rows.collect()
}

#[derive(Debug)]
struct EpisodeRecord {
    episode_id: i32,
    seed: i32,
    kills: i32,
    deaths: i32,
    survival_time_ms: i64,
    ammo_efficiency: f64,
}
```

### Batch Inserts with Appender API

Use the appender API for high-throughput bulk inserts (10-100x faster than individual INSERTs).

```rust
use duckdb::Appender;

fn batch_insert_encounters(
    conn: &Connection,
    encounters: &[EncounterData],
) -> Result<()> {
    let mut appender = conn.appender("encounters")?;

    for enc in encounters {
        appender.append_row(params![
            enc.encounter_id,
            enc.episode_id,
            &enc.enemy_type,
            enc.distance,
            &enc.weapon_used,
            enc.hits,
            enc.misses,
            &enc.result,
            enc.reaction_time_ms,
            enc.health_before,
            enc.health_after,
            enc.timestamp_ms,
        ])?;
    }

    appender.flush()?;
    Ok(())
}

#[derive(Debug)]
struct EncounterData {
    encounter_id: i32,
    episode_id: i32,
    enemy_type: String,
    distance: f64,
    weapon_used: String,
    hits: i32,
    misses: i32,
    result: String,
    reaction_time_ms: i64,
    health_before: f64,
    health_after: f64,
    timestamp_ms: i64,
}
```

### Transaction Management

```rust
fn record_episode_with_encounters(
    conn: &Connection,
    episode_data: &EpisodeData,
    encounters: &[EncounterData],
) -> Result<()> {
    let tx = conn.transaction()?;

    // Insert episode
    tx.execute(
        "INSERT INTO episodes (agent_id, seed, kills, deaths) VALUES (?, ?, ?, ?)",
        params![episode_data.agent_id, episode_data.seed, episode_data.kills, episode_data.deaths],
    )?;

    // Get generated episode_id
    let episode_id: i32 = tx.query_row(
        "SELECT last_insert_rowid()",
        [],
        |row| row.get(0),
    )?;

    // Insert encounters
    for enc in encounters {
        tx.execute(
            r#"
            INSERT INTO encounters
            (episode_id, enemy_type, distance, weapon_used, hits, misses, result)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            "#,
            params![
                episode_id,
                &enc.enemy_type,
                enc.distance,
                &enc.weapon_used,
                enc.hits,
                enc.misses,
                &enc.result,
            ],
        )?;
    }

    tx.commit()
}

#[derive(Debug)]
struct EpisodeData {
    agent_id: String,
    seed: i32,
    kills: i32,
    deaths: i32,
}
```

### Error Handling

```rust
use duckdb::Error as DuckDBError;
use thiserror::Error;

#[derive(Debug, Error)]
pub enum DataError {
    #[error("DuckDB error: {0}")]
    DuckDB(#[from] DuckDBError),

    #[error("Episode not found: {episode_id}")]
    EpisodeNotFound { episode_id: i32 },

    #[error("Invalid seed set: {reason}")]
    InvalidSeedSet { reason: String },
}

fn verify_episode_count(conn: &Connection, run_id: &str, expected: usize) -> Result<(), DataError> {
    let count: usize = conn.query_row(
        "SELECT COUNT(*) FROM episodes WHERE run_id = ?",
        params![run_id],
        |row| row.get(0),
    )?;

    if count != expected {
        return Err(DataError::InvalidSeedSet {
            reason: format!(
                "Expected {} episodes for run {}, found {}",
                expected, run_id, count
            ),
        });
    }

    Ok(())
}
```

## Python duckdb API Patterns

### Connection Management

```python
import duckdb
from pathlib import Path

def get_agent_connection(agent_id: str) -> duckdb.DuckDBPyConnection:
    """Open connection to agent's DuckDB file."""
    db_path = Path(f"data/{agent_id}/play_logs.duckdb")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return duckdb.connect(str(db_path))


def get_experiment_connection(experiment_id: str) -> duckdb.DuckDBPyConnection:
    """Create in-memory connection with all agent data attached."""
    conn = duckdb.connect(":memory:")

    # Attach all agent databases
    agent_ids = ["doom-agent-A", "doom-agent-B", "doom-agent-C"]
    for agent_id in agent_ids:
        conn.execute(f"""
            ATTACH 'data/{agent_id}/play_logs.duckdb' AS {agent_id.replace('-', '_')}
        """)

    return conn
```

### SQL Queries Returning DataFrames

```python
import pandas as pd

def get_episode_summary(conn: duckdb.DuckDBPyConnection, run_id: str) -> pd.DataFrame:
    """Get episode-level summary statistics for a DOE run."""
    return conn.execute("""
        SELECT
            episode_id,
            seed,
            kills,
            deaths,
            CAST(survival_time_ms AS DOUBLE) / 1000.0 AS survival_time_sec,
            ammo_efficiency,
            items_collected,
            exploration_coverage
        FROM episodes
        WHERE run_id = ?
        ORDER BY episode_id
    """, [run_id]).df()


def get_factor_level_aggregates(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
) -> pd.DataFrame:
    """Aggregate metrics by factor levels for ANOVA input."""
    return conn.execute("""
        SELECT
            r.factor_levels->>'memory' AS memory,
            r.factor_levels->>'strength' AS strength,
            AVG(e.kills) AS avg_kills,
            AVG(CAST(e.survival_time_ms AS DOUBLE) / 1000.0) AS avg_survival_sec,
            AVG(e.ammo_efficiency) AS avg_ammo_efficiency,
            COUNT(*) AS n_episodes,
            STDDEV(e.kills) AS std_kills
        FROM experiment_runs r
        JOIN episodes e ON r.run_id = e.run_id
        WHERE r.experiment_id = ?
        GROUP BY memory, strength
        ORDER BY memory, strength
    """, [experiment_id]).df()
```

### Registering DataFrames as Virtual Tables

```python
def compute_fitness_scores(
    conn: duckdb.DuckDBPyConnection,
    episodes_df: pd.DataFrame,
    weights: dict[str, float],
) -> pd.DataFrame:
    """Compute fitness scores using SQL on a DataFrame."""
    # Register DataFrame as virtual table
    conn.register("episodes_df", episodes_df)

    return conn.execute(f"""
        SELECT
            episode_id,
            seed,
            (
                {weights['kills']} * kills +
                {weights['survival']} * (CAST(survival_time_ms AS DOUBLE) / 1000.0) +
                {weights['ammo_efficiency']} * ammo_efficiency +
                {weights['exploration']} * exploration_coverage
            ) AS fitness_score
        FROM episodes_df
        ORDER BY fitness_score DESC
    """).df()
```

### Parameterized Queries for Safety

```python
def insert_experiment_run(
    conn: duckdb.DuckDBPyConnection,
    run_id: str,
    experiment_id: str,
    agent_id: str,
    factor_levels: dict,
    seed_set: list[int],
) -> None:
    """Insert experiment run metadata with parameterized query."""
    import json

    conn.execute("""
        INSERT INTO experiment_runs
        (run_id, experiment_id, agent_id, factor_levels, seed_set, episodes_planned, status)
        VALUES (?, ?, ?, ?, ?, ?, 'pending')
    """, [
        run_id,
        experiment_id,
        agent_id,
        json.dumps(factor_levels),
        json.dumps(seed_set),
        len(seed_set),
    ])
```

### Cross-Agent Aggregate Queries

```python
def get_multi_agent_summary(experiment_id: str) -> pd.DataFrame:
    """Aggregate data across all agents for an experiment."""
    conn = get_experiment_connection(experiment_id)

    # Query across attached databases
    return conn.execute("""
        SELECT
            e.agent_id,
            r.factor_levels->>'memory' AS memory,
            r.factor_levels->>'strength' AS strength,
            COUNT(*) AS n_episodes,
            AVG(e.kills) AS avg_kills,
            AVG(CAST(e.survival_time_ms AS DOUBLE) / 1000.0) AS avg_survival_sec
        FROM (
            SELECT * FROM doom_agent_A.episodes
            UNION ALL
            SELECT * FROM doom_agent_B.episodes
            UNION ALL
            SELECT * FROM doom_agent_C.episodes
        ) e
        JOIN doom_agent_A.experiment_runs r ON e.run_id = r.run_id
        WHERE r.experiment_id = ?
        GROUP BY e.agent_id, memory, strength
        ORDER BY e.agent_id, memory, strength
    """, [experiment_id]).df()
```

## Window Functions for Analysis

### Moving Averages for Kill Rate Trends

```sql
-- 5-episode moving average of kill rate
SELECT
    episode_id,
    seed,
    kills,
    AVG(kills) OVER (
        ORDER BY episode_id
        ROWS BETWEEN 4 PRECEDING AND CURRENT ROW
    ) AS kill_rate_ma5
FROM episodes
WHERE agent_id = 'doom-agent-A'
ORDER BY episode_id;
```

Python wrapper:

```python
def get_kill_rate_trend(conn: duckdb.DuckDBPyConnection, agent_id: str, window: int = 5) -> pd.DataFrame:
    """Get moving average of kill rate for trend analysis."""
    return conn.execute(f"""
        SELECT
            episode_id,
            seed,
            kills,
            AVG(kills) OVER (
                ORDER BY episode_id
                ROWS BETWEEN {window - 1} PRECEDING AND CURRENT ROW
            ) AS kill_rate_ma{window}
        FROM episodes
        WHERE agent_id = ?
        ORDER BY episode_id
    """, [agent_id]).df()
```

### Ranking for Leaderboards

```sql
-- Rank episodes by fitness score within each generation
SELECT
    episode_id,
    generation,
    kills,
    survival_time_ms,
    ROW_NUMBER() OVER (PARTITION BY generation ORDER BY kills DESC) AS rank_by_kills,
    RANK() OVER (PARTITION BY generation ORDER BY survival_time_ms DESC) AS rank_by_survival
FROM episodes
WHERE agent_id = 'doom-agent-A'
ORDER BY generation, rank_by_kills;
```

### LAG/LEAD for Episode-over-Episode Comparisons

```sql
-- Compare each episode to the previous one
SELECT
    episode_id,
    kills,
    LAG(kills, 1) OVER (ORDER BY episode_id) AS prev_kills,
    kills - LAG(kills, 1) OVER (ORDER BY episode_id) AS kill_delta,
    survival_time_ms,
    LEAD(survival_time_ms, 1) OVER (ORDER BY episode_id) AS next_survival_time
FROM episodes
WHERE run_id = 'DOE-042-run-1'
ORDER BY episode_id;
```

### Cumulative Statistics

```sql
-- Running total of kills and deaths
SELECT
    episode_id,
    kills,
    deaths,
    SUM(kills) OVER (ORDER BY episode_id ROWS UNBOUNDED PRECEDING) AS cumulative_kills,
    SUM(deaths) OVER (ORDER BY episode_id ROWS UNBOUNDED PRECEDING) AS cumulative_deaths
FROM episodes
WHERE agent_id = 'doom-agent-A'
ORDER BY episode_id;
```

## Parquet I/O

### Export to Parquet

```sql
-- Export episode data to Parquet
COPY (
    SELECT * FROM episodes
    WHERE experiment_id = 'DOE-042'
) TO 'data/processed/experiment_042.parquet' (FORMAT PARQUET);
```

Python wrapper:

```python
def export_experiment_to_parquet(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
    output_path: str,
) -> None:
    """Export experiment data to Parquet for archival and cross-agent analysis."""
    conn.execute(f"""
        COPY (
            SELECT
                e.*,
                r.factor_levels,
                r.seed_set
            FROM episodes e
            JOIN experiment_runs r ON e.run_id = r.run_id
            WHERE r.experiment_id = ?
        ) TO ? (FORMAT PARQUET, COMPRESSION ZSTD)
    """, [experiment_id, output_path])
```

### Read from Parquet

```sql
-- Query Parquet file directly
SELECT
    agent_id,
    AVG(kills) AS avg_kills,
    COUNT(*) AS n_episodes
FROM read_parquet('data/processed/experiment_042.parquet')
GROUP BY agent_id;
```

Python wrapper:

```python
def load_experiment_from_parquet(parquet_path: str) -> pd.DataFrame:
    """Load experiment data from Parquet archive."""
    conn = duckdb.connect(":memory:")
    return conn.execute(f"""
        SELECT * FROM read_parquet('{parquet_path}')
    """).df()
```

### Cross-Agent Analysis via Parquet

```python
def aggregate_multiple_experiments(experiment_ids: list[str]) -> pd.DataFrame:
    """Aggregate data from multiple experiments stored as Parquet."""
    conn = duckdb.connect(":memory:")

    parquet_files = [f"data/processed/experiment_{eid}.parquet" for eid in experiment_ids]
    file_list = ", ".join([f"'{f}'" for f in parquet_files])

    return conn.execute(f"""
        SELECT
            json_extract_string(factor_levels, '$.memory') AS memory,
            json_extract_string(factor_levels, '$.strength') AS strength,
            AVG(kills) AS avg_kills,
            AVG(CAST(survival_time_ms AS DOUBLE) / 1000.0) AS avg_survival_sec,
            COUNT(*) AS total_episodes
        FROM read_parquet([{file_list}])
        GROUP BY memory, strength
        ORDER BY memory, strength
    """).df()
```

### Column Pruning and Predicate Pushdown

DuckDB automatically optimizes Parquet reads with column pruning and predicate pushdown.

```python
def get_high_kill_episodes(parquet_path: str, min_kills: int = 50) -> pd.DataFrame:
    """Query Parquet with predicate pushdown (only reads matching rows)."""
    conn = duckdb.connect(":memory:")

    # DuckDB pushes the WHERE clause down to Parquet reader
    # Only reads rows with kills >= min_kills
    return conn.execute(f"""
        SELECT episode_id, kills, survival_time_ms
        FROM read_parquet('{parquet_path}')
        WHERE kills >= {min_kills}
        ORDER BY kills DESC
    """).df()
```

## DOE-Specific Queries

### Factor-Level Aggregation for ANOVA Input

```python
def prepare_anova_data(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
    response_var: str = "kills",
) -> pd.DataFrame:
    """Prepare data for ANOVA with factor levels as columns."""
    return conn.execute(f"""
        SELECT
            json_extract_string(r.factor_levels, '$.memory') AS memory,
            json_extract_string(r.factor_levels, '$.strength') AS strength,
            e.{response_var} AS response
        FROM experiment_runs r
        JOIN episodes e ON r.run_id = e.run_id
        WHERE r.experiment_id = ?
        AND r.status = 'completed'
    """, [experiment_id]).df()
```

### Seed Set Verification

```python
def verify_seed_integrity(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
) -> pd.DataFrame:
    """Check that all runs used their assigned seed sets correctly."""
    return conn.execute("""
        WITH expected_seeds AS (
            SELECT
                run_id,
                json_array_length(seed_set) AS expected_count,
                seed_set
            FROM experiment_runs
            WHERE experiment_id = ?
        ),
        actual_seeds AS (
            SELECT
                run_id,
                COUNT(*) AS actual_count,
                json_group_array(seed ORDER BY episode_id) AS actual_seed_set
            FROM episodes
            WHERE run_id IN (SELECT run_id FROM expected_seeds)
            GROUP BY run_id
        )
        SELECT
            e.run_id,
            e.expected_count,
            a.actual_count,
            e.seed_set AS expected_seed_set,
            a.actual_seed_set,
            CASE
                WHEN e.expected_count = a.actual_count
                     AND e.seed_set = a.actual_seed_set THEN 'OK'
                ELSE 'MISMATCH'
            END AS status
        FROM expected_seeds e
        JOIN actual_seeds a ON e.run_id = a.run_id
    """, [experiment_id]).df()
```

### Run Completion Status

```python
def get_run_status(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
) -> pd.DataFrame:
    """Check completion status of all runs in an experiment."""
    return conn.execute("""
        SELECT
            r.run_id,
            r.agent_id,
            r.status,
            r.episodes_planned,
            r.episodes_completed,
            COUNT(e.episode_id) AS episodes_recorded,
            r.started_at,
            r.completed_at,
            CASE
                WHEN r.status = 'completed' AND r.episodes_completed = r.episodes_planned THEN 'OK'
                WHEN r.status = 'running' THEN 'IN_PROGRESS'
                ELSE 'INCOMPLETE'
            END AS validation_status
        FROM experiment_runs r
        LEFT JOIN episodes e ON r.run_id = e.run_id
        WHERE r.experiment_id = ?
        GROUP BY r.run_id, r.agent_id, r.status, r.episodes_planned,
                 r.episodes_completed, r.started_at, r.completed_at
        ORDER BY r.run_id
    """, [experiment_id]).df()
```

### Cross-Run Comparison

```python
def compare_runs(
    conn: duckdb.DuckDBPyConnection,
    run_ids: list[str],
) -> pd.DataFrame:
    """Compare performance metrics across multiple runs."""
    run_list = ", ".join([f"'{rid}'" for rid in run_ids])

    return conn.execute(f"""
        SELECT
            e.run_id,
            json_extract_string(r.factor_levels, '$.memory') AS memory,
            json_extract_string(r.factor_levels, '$.strength') AS strength,
            COUNT(*) AS n_episodes,
            AVG(e.kills) AS avg_kills,
            STDDEV(e.kills) AS std_kills,
            MIN(e.kills) AS min_kills,
            MAX(e.kills) AS max_kills,
            AVG(CAST(e.survival_time_ms AS DOUBLE) / 1000.0) AS avg_survival_sec
        FROM episodes e
        JOIN experiment_runs r ON e.run_id = r.run_id
        WHERE e.run_id IN ({run_list})
        GROUP BY e.run_id, memory, strength
        ORDER BY memory, strength, e.run_id
    """).df()
```

## Performance Tips

### Use Appender for Bulk Inserts

```python
# SLOW: Individual INSERT statements
for episode in episodes:
    conn.execute(
        "INSERT INTO episodes (agent_id, seed, kills) VALUES (?, ?, ?)",
        [episode.agent_id, episode.seed, episode.kills],
    )

# FAST: Appender API (10-100x faster)
appender = conn.appender("episodes")
for episode in episodes:
    appender.append_row([episode.agent_id, episode.seed, episode.kills])
appender.flush()
```

### Column-Oriented Storage Advantages

DuckDB's column-oriented storage is optimized for analytical queries:

- **Fast aggregations**: AVG, SUM, COUNT operations scan only relevant columns
- **Compression**: Each column compressed independently (better ratios)
- **Vectorized execution**: SIMD operations on column chunks

```python
# This query only reads 'kills' column, ignoring others
def get_avg_kills(conn: duckdb.DuckDBPyConnection, run_id: str) -> float:
    return conn.execute(
        "SELECT AVG(kills) FROM episodes WHERE run_id = ?",
        [run_id],
    ).fetchone()[0]
```

### Predicate Pushdown for Filtered Queries

DuckDB pushes filters down to storage layer, reducing rows scanned:

```python
# Efficient: Filter applied at storage layer
def get_high_performance_episodes(
    conn: duckdb.DuckDBPyConnection,
    agent_id: str,
    min_kills: int = 50,
) -> pd.DataFrame:
    return conn.execute("""
        SELECT episode_id, seed, kills, survival_time_ms
        FROM episodes
        WHERE agent_id = ? AND kills >= ?
        ORDER BY kills DESC
    """, [agent_id, min_kills]).df()
```

### Memory Limits Configuration

Control memory usage for large analytical workloads:

```python
def configure_memory_limits(conn: duckdb.DuckDBPyConnection, max_memory_gb: int = 4) -> None:
    """Set memory limits for DuckDB queries."""
    conn.execute(f"SET memory_limit = '{max_memory_gb}GB'")
    conn.execute("SET temp_directory = 'data/duckdb_temp'")
```

### Index Usage for Lookups

Indexes speed up filtered queries and joins:

```sql
-- Create indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_episodes_run ON episodes(run_id);
CREATE INDEX IF NOT EXISTS idx_episodes_agent ON episodes(agent_id);
CREATE INDEX IF NOT EXISTS idx_episodes_seed ON episodes(seed);

-- This query uses idx_episodes_run for fast lookup
SELECT * FROM episodes WHERE run_id = 'DOE-042-run-1';
```

### Parallel Query Execution

DuckDB automatically parallelizes queries across available CPU cores:

```python
# Query runs in parallel automatically
def aggregate_large_dataset(conn: duckdb.DuckDBPyConnection) -> pd.DataFrame:
    return conn.execute("""
        SELECT
            agent_id,
            generation,
            AVG(kills) AS avg_kills,
            COUNT(*) AS n_episodes
        FROM episodes
        GROUP BY agent_id, generation
        ORDER BY agent_id, generation
    """).df()

# Control thread count if needed
conn.execute("SET threads TO 4")
```
