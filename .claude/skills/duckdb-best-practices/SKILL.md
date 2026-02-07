---
name: duckdb-best-practices
description: DuckDB patterns for Rust duckdb-rs and Python API including per-agent data stores, DOE result schemas, window functions, and Parquet I/O
user-invocable: false
---

# DuckDB Best Practices for clau-doom Analytics

## Per-Agent Data Architecture

### File-Per-Agent Pattern

Each agent maintains its own DuckDB database to avoid write contention and enable independent analysis.

```
data/
├── doom-agent-A/
│   └── play_logs.duckdb
├── doom-agent-B/
│   └── play_logs.duckdb
└── doom-agent-C/
    └── play_logs.duckdb
```

### Agent Database Initialization (Python)

```python
import duckdb
from pathlib import Path

def init_agent_db(agent_id: str, data_dir: Path) -> duckdb.DuckDBPyConnection:
    """Initialize per-agent DuckDB database with schema."""
    db_path = data_dir / agent_id / "play_logs.duckdb"
    db_path.parent.mkdir(parents=True, exist_ok=True)

    conn = duckdb.connect(str(db_path))

    # Enable performance optimizations
    conn.execute("PRAGMA threads=4")
    conn.execute("PRAGMA memory_limit='2GB'")

    # Create schema
    conn.execute("""
        CREATE TABLE IF NOT EXISTS episodes (
            episode_id UUID PRIMARY KEY,
            agent_id VARCHAR NOT NULL,
            seed INTEGER NOT NULL,
            generation INTEGER,
            run_id VARCHAR,

            -- Performance metrics
            kills INTEGER DEFAULT 0,
            deaths INTEGER DEFAULT 0,
            damage_dealt INTEGER DEFAULT 0,
            damage_taken INTEGER DEFAULT 0,
            survival_time_ms BIGINT,
            ammo_efficiency DOUBLE,
            items_collected INTEGER DEFAULT 0,

            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)

    return conn
```

### Agent Database Initialization (Rust)

```rust
use duckdb::{Connection, Result, params};
use std::path::Path;

pub fn init_agent_db(agent_id: &str, data_dir: &Path) -> Result<Connection> {
    let db_path = data_dir.join(agent_id).join("play_logs.duckdb");
    std::fs::create_dir_all(db_path.parent().unwrap())?;

    let conn = Connection::open(&db_path)?;

    // Performance settings
    conn.execute_batch("
        PRAGMA threads=4;
        PRAGMA memory_limit='2GB';
    ")?;

    // Create schema
    conn.execute_batch("
        CREATE TABLE IF NOT EXISTS episodes (
            episode_id UUID PRIMARY KEY,
            agent_id VARCHAR NOT NULL,
            seed INTEGER NOT NULL,
            generation INTEGER,
            run_id VARCHAR,

            kills INTEGER DEFAULT 0,
            deaths INTEGER DEFAULT 0,
            damage_dealt INTEGER DEFAULT 0,
            damage_taken INTEGER DEFAULT 0,
            survival_time_ms BIGINT,
            ammo_efficiency DOUBLE,
            items_collected INTEGER DEFAULT 0,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        );
    ")?;

    Ok(conn)
}
```

### Cross-Agent Analysis via Parquet

```python
def export_agent_data(conn: duckdb.DuckDBPyConnection, output_path: Path) -> None:
    """Export agent data to Parquet for cross-agent analysis."""
    conn.execute(f"""
        COPY (
            SELECT * FROM episodes
            WHERE completed_at IS NOT NULL
        ) TO '{output_path}' (FORMAT PARQUET)
    """)

def aggregate_multi_agent_data(agent_ids: list[str], data_dir: Path) -> pd.DataFrame:
    """Aggregate data from multiple agents for DOE analysis."""
    conn = duckdb.connect(":memory:")

    parquet_files = [
        str(data_dir / agent_id / "episodes.parquet")
        for agent_id in agent_ids
    ]

    return conn.execute(f"""
        SELECT
            agent_id,
            generation,
            AVG(kills) as avg_kills,
            AVG(survival_time_ms) as avg_survival,
            AVG(ammo_efficiency) as avg_efficiency,
            COUNT(*) as n_episodes
        FROM read_parquet({parquet_files})
        GROUP BY agent_id, generation
        ORDER BY agent_id, generation
    """).fetchdf()
```

## Schema Definitions

### Episodes Table

```sql
CREATE TABLE episodes (
    episode_id UUID PRIMARY KEY,
    agent_id VARCHAR NOT NULL,
    seed INTEGER NOT NULL,
    generation INTEGER,
    run_id VARCHAR,

    -- Combat metrics
    kills INTEGER DEFAULT 0,
    deaths INTEGER DEFAULT 0,
    damage_dealt INTEGER DEFAULT 0,
    damage_taken INTEGER DEFAULT 0,

    -- Survival metrics
    survival_time_ms BIGINT,
    health_remaining DOUBLE,

    -- Efficiency metrics
    ammo_efficiency DOUBLE,  -- kills / shots_fired
    items_collected INTEGER DEFAULT 0,
    secrets_found INTEGER DEFAULT 0,

    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP
);

CREATE INDEX idx_episodes_agent_gen ON episodes(agent_id, generation);
CREATE INDEX idx_episodes_run ON episodes(run_id);
CREATE INDEX idx_episodes_seed ON episodes(seed);
```

### Encounters Table

```sql
CREATE TABLE encounters (
    encounter_id UUID PRIMARY KEY,
    episode_id UUID NOT NULL,
    encounter_timestamp BIGINT,  -- milliseconds since episode start

    -- Enemy information
    enemy_type VARCHAR,  -- 'zombie', 'imp', 'demon', etc.
    distance DOUBLE,

    -- Agent response
    weapon_used VARCHAR,
    hits INTEGER DEFAULT 0,
    misses INTEGER DEFAULT 0,
    reaction_time_ms INTEGER,

    -- Outcome
    result VARCHAR CHECK (result IN ('kill', 'death', 'flee', 'ongoing')),
    damage_inflicted INTEGER DEFAULT 0,
    damage_received INTEGER DEFAULT 0,

    FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
);

CREATE INDEX idx_encounters_episode ON encounters(episode_id);
CREATE INDEX idx_encounters_enemy ON encounters(enemy_type);
```

### Experiment Runs Table

```sql
CREATE TABLE experiment_runs (
    run_id VARCHAR PRIMARY KEY,
    experiment_id VARCHAR NOT NULL,

    -- DOE configuration
    factor_levels JSON,  -- {"memory": 0.7, "strength": 0.5}
    seed_set INTEGER[],  -- Array of seeds for reproducibility

    -- Execution tracking
    status VARCHAR CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    episodes_planned INTEGER,
    episodes_completed INTEGER DEFAULT 0,

    -- Timestamps
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    -- Metadata
    notes TEXT
);

CREATE INDEX idx_runs_experiment ON experiment_runs(experiment_id);
CREATE INDEX idx_runs_status ON experiment_runs(status);
```

### Schema Migration Pattern

```python
def get_schema_version(conn: duckdb.DuckDBPyConnection) -> int:
    """Get current schema version."""
    try:
        result = conn.execute("""
            SELECT version FROM schema_version
            ORDER BY applied_at DESC
            LIMIT 1
        """).fetchone()
        return result[0] if result else 0
    except:
        return 0

def migrate_schema(conn: duckdb.DuckDBPyConnection, target_version: int) -> None:
    """Apply schema migrations up to target version."""
    current = get_schema_version(conn)

    # Migration 1: Add schema_version table
    if current < 1:
        conn.execute("""
            CREATE TABLE schema_version (
                version INTEGER PRIMARY KEY,
                description VARCHAR,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("INSERT INTO schema_version VALUES (1, 'Initial schema', CURRENT_TIMESTAMP)")

    # Migration 2: Add ammo_efficiency column
    if current < 2:
        conn.execute("ALTER TABLE episodes ADD COLUMN ammo_efficiency DOUBLE")
        conn.execute("INSERT INTO schema_version VALUES (2, 'Add ammo_efficiency', CURRENT_TIMESTAMP)")

    # Migration 3: Add encounters table
    if current < 3:
        conn.execute("""
            CREATE TABLE encounters (
                encounter_id UUID PRIMARY KEY,
                episode_id UUID NOT NULL,
                enemy_type VARCHAR,
                result VARCHAR,
                FOREIGN KEY (episode_id) REFERENCES episodes(episode_id)
            )
        """)
        conn.execute("INSERT INTO schema_version VALUES (3, 'Add encounters table', CURRENT_TIMESTAMP)")
```

## Rust duckdb-rs Patterns

### Connection Management

```rust
use duckdb::{Connection, Result};

pub struct AgentDB {
    conn: Connection,
}

impl AgentDB {
    pub fn new(db_path: &str) -> Result<Self> {
        let conn = Connection::open(db_path)?;

        // Set pragmas for performance
        conn.execute_batch("
            PRAGMA threads=4;
            PRAGMA memory_limit='2GB';
            PRAGMA enable_object_cache=true;
        ")?;

        Ok(Self { conn })
    }

    pub fn new_in_memory() -> Result<Self> {
        let conn = Connection::open_in_memory()?;
        Ok(Self { conn })
    }
}
```

### Batch Inserts with Appender

```rust
use duckdb::appender::Appender;
use uuid::Uuid;

pub struct EpisodeResult {
    pub episode_id: Uuid,
    pub agent_id: String,
    pub seed: i32,
    pub generation: i32,
    pub kills: i32,
    pub deaths: i32,
    pub survival_time_ms: i64,
    pub ammo_efficiency: f64,
}

impl AgentDB {
    pub fn insert_episodes_batch(&self, results: Vec<EpisodeResult>) -> Result<()> {
        let mut appender = Appender::new(&self.conn, "main", "episodes")?;

        for result in results {
            appender.append_row(params![
                result.episode_id,
                result.agent_id,
                result.seed,
                result.generation,
                result.kills,
                result.deaths,
                result.survival_time_ms,
                result.ammo_efficiency,
            ])?;
        }

        appender.flush()?;
        Ok(())
    }
}
```

### Type Mapping (Rust to DuckDB)

```rust
// Rust types → DuckDB types
// i32, i64 → INTEGER, BIGINT
// f32, f64 → FLOAT, DOUBLE
// String, &str → VARCHAR
// uuid::Uuid → UUID
// chrono::NaiveDateTime → TIMESTAMP
// Vec<T> → ARRAY
// serde_json::Value → JSON

use chrono::NaiveDateTime;
use serde_json::Value;

appender.append_row(params![
    42_i32,                    // INTEGER
    1000_i64,                  // BIGINT
    3.14_f64,                  // DOUBLE
    "agent-A",                 // VARCHAR
    Uuid::new_v4(),            // UUID
    NaiveDateTime::default(),  // TIMESTAMP
    vec![1, 2, 3],             // INTEGER[]
    serde_json::json!({"key": "value"}), // JSON
])?;
```

### Prepared Statements

```rust
use duckdb::params;

impl AgentDB {
    pub fn get_generation_stats(&self, generation: i32) -> Result<(f64, f64, i64)> {
        let mut stmt = self.conn.prepare("
            SELECT
                AVG(kills) as avg_kills,
                AVG(survival_time_ms) as avg_survival,
                COUNT(*) as n_episodes
            FROM episodes
            WHERE generation = ?
        ")?;

        let mut rows = stmt.query(params![generation])?;

        if let Some(row) = rows.next()? {
            Ok((
                row.get(0)?,
                row.get(1)?,
                row.get(2)?,
            ))
        } else {
            Ok((0.0, 0.0, 0))
        }
    }
}
```

### Transaction Management

```rust
impl AgentDB {
    pub fn save_experiment_run(
        &self,
        run_id: &str,
        episodes: Vec<EpisodeResult>,
    ) -> Result<()> {
        let tx = self.conn.transaction()?;

        // Insert run metadata
        tx.execute(
            "INSERT INTO experiment_runs (run_id, status) VALUES (?, ?)",
            params![run_id, "running"],
        )?;

        // Batch insert episodes
        {
            let mut appender = Appender::new_with_connection(
                tx.connection(),
                "main",
                "episodes"
            )?;

            for ep in episodes {
                appender.append_row(params![
                    ep.episode_id,
                    ep.agent_id,
                    ep.seed,
                    ep.kills,
                    ep.deaths,
                ])?;
            }
            appender.flush()?;
        }

        // Update run status
        tx.execute(
            "UPDATE experiment_runs SET status = ? WHERE run_id = ?",
            params!["completed", run_id],
        )?;

        tx.commit()?;
        Ok(())
    }
}
```

### Error Handling

```rust
use duckdb::Error as DuckDBError;

impl AgentDB {
    pub fn insert_with_retry(&self, episode: EpisodeResult) -> Result<()> {
        const MAX_RETRIES: u32 = 3;
        let mut attempts = 0;

        loop {
            match self.insert_episode(&episode) {
                Ok(_) => return Ok(()),
                Err(e) => {
                    attempts += 1;
                    if attempts >= MAX_RETRIES {
                        return Err(e);
                    }

                    // Wait before retry (exponential backoff)
                    std::thread::sleep(
                        std::time::Duration::from_millis(100 * 2_u64.pow(attempts))
                    );
                }
            }
        }
    }

    fn insert_episode(&self, episode: &EpisodeResult) -> Result<()> {
        self.conn.execute(
            "INSERT INTO episodes VALUES (?, ?, ?, ?, ?)",
            params![
                episode.episode_id,
                episode.agent_id,
                episode.seed,
                episode.kills,
                episode.deaths,
            ],
        )?;
        Ok(())
    }
}
```

## Python duckdb API Patterns

### Connection and Querying

```python
import duckdb
import pandas as pd

# File-based connection
conn = duckdb.connect("data/analytics.duckdb")

# In-memory connection
conn = duckdb.connect(":memory:")

# Query returning DataFrame
df = conn.execute("""
    SELECT agent_id, AVG(kills) as avg_kills
    FROM episodes
    GROUP BY agent_id
""").fetchdf()

# Query with parameters
result = conn.execute("""
    SELECT * FROM episodes
    WHERE agent_id = $1 AND generation >= $2
""", ["agent-A", 5]).fetchdf()

# Register DataFrame as virtual table
episodes_df = pd.read_csv("episodes.csv")
conn.register("episodes_view", episodes_df)

result = conn.execute("""
    SELECT * FROM episodes_view
    WHERE kills > 10
""").fetchdf()
```

### DOE Analysis Queries

```python
def prepare_anova_data(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
) -> pd.DataFrame:
    """Prepare data for factorial ANOVA analysis."""
    return conn.execute("""
        SELECT
            er.factor_levels->>'memory' as memory,
            er.factor_levels->>'strength' as strength,
            AVG(e.kills) as avg_kills,
            STDDEV(e.kills) as sd_kills,
            COUNT(*) as n_episodes
        FROM experiment_runs er
        JOIN episodes e ON e.run_id = er.run_id
        WHERE er.experiment_id = ?
        GROUP BY
            er.factor_levels->>'memory',
            er.factor_levels->>'strength'
    """, [experiment_id]).fetchdf()


def verify_seed_sets(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
) -> pd.DataFrame:
    """Verify all runs in experiment use identical seed sets."""
    return conn.execute("""
        SELECT
            run_id,
            seed_set,
            LIST_SORT(seed_set) as sorted_seeds,
            LEN(seed_set) as seed_count
        FROM experiment_runs
        WHERE experiment_id = ?
        ORDER BY run_id
    """, [experiment_id]).fetchdf()


def get_run_completion_status(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
) -> pd.DataFrame:
    """Get completion dashboard for DOE experiment."""
    return conn.execute("""
        SELECT
            er.run_id,
            er.factor_levels,
            er.episodes_planned,
            er.episodes_completed,
            ROUND(100.0 * er.episodes_completed / er.episodes_planned, 1) as pct_complete,
            er.status,
            er.started_at,
            er.completed_at,
            DATE_DIFF('minute', er.started_at, COALESCE(er.completed_at, CURRENT_TIMESTAMP)) as runtime_minutes
        FROM experiment_runs er
        WHERE er.experiment_id = ?
        ORDER BY er.run_id
    """, [experiment_id]).fetchdf()
```

### DataFrame Integration

```python
# Query results → pandas DataFrame
df = conn.execute("SELECT * FROM episodes").fetchdf()

# DataFrame → DuckDB table
conn.execute("CREATE TABLE episodes_copy AS SELECT * FROM df")

# Filtering and joining
episodes_df = pd.read_csv("episodes.csv")
runs_df = pd.read_csv("runs.csv")

conn.register("episodes_tmp", episodes_df)
conn.register("runs_tmp", runs_df)

result = conn.execute("""
    SELECT
        r.run_id,
        r.factor_levels->>'memory' as memory,
        AVG(e.kills) as avg_kills
    FROM runs_tmp r
    JOIN episodes_tmp e ON e.run_id = r.run_id
    GROUP BY r.run_id, r.factor_levels->>'memory'
""").fetchdf()
```

## Window Functions for Research

### Moving Average Kill Rate

```sql
SELECT
    episode_id,
    agent_id,
    kills,
    AVG(kills) OVER (
        PARTITION BY agent_id
        ORDER BY created_at
        ROWS BETWEEN 9 PRECEDING AND CURRENT ROW
    ) as moving_avg_kills_10
FROM episodes
ORDER BY agent_id, created_at;
```

### Generation Ranking

```sql
SELECT
    generation,
    agent_id,
    kills,
    RANK() OVER (
        PARTITION BY generation
        ORDER BY kills DESC
    ) as rank_in_generation,
    PERCENT_RANK() OVER (
        PARTITION BY generation
        ORDER BY kills DESC
    ) as percentile
FROM episodes
ORDER BY generation, rank_in_generation;
```

### Episode-over-Episode Delta

```sql
SELECT
    episode_id,
    agent_id,
    kills,
    kills - LAG(kills) OVER (
        PARTITION BY agent_id
        ORDER BY created_at
    ) as kills_delta,
    survival_time_ms - LAG(survival_time_ms) OVER (
        PARTITION BY agent_id
        ORDER BY created_at
    ) as survival_delta
FROM episodes
ORDER BY agent_id, created_at;
```

### Cumulative Statistics

```sql
SELECT
    agent_id,
    created_at,
    damage_dealt,
    SUM(damage_dealt) OVER (
        PARTITION BY agent_id
        ORDER BY created_at
    ) as cumulative_damage,
    AVG(damage_dealt) OVER (
        PARTITION BY agent_id
        ORDER BY created_at
        ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW
    ) as running_avg_damage
FROM episodes
ORDER BY agent_id, created_at;
```

### Running Statistics Per Agent

```python
def get_agent_running_stats(
    conn: duckdb.DuckDBPyConnection,
    agent_id: str,
) -> pd.DataFrame:
    """Get running statistics for an agent's performance."""
    return conn.execute("""
        SELECT
            episode_id,
            created_at,
            kills,

            -- Moving averages
            AVG(kills) OVER w10 as ma_kills_10,
            AVG(survival_time_ms) OVER w10 as ma_survival_10,

            -- Cumulative stats
            SUM(kills) OVER w_all as total_kills,
            AVG(kills) OVER w_all as avg_kills_to_date,

            -- Episode rank
            ROW_NUMBER() OVER (ORDER BY created_at) as episode_number,
            RANK() OVER (ORDER BY kills DESC) as kills_rank

        FROM episodes
        WHERE agent_id = ?

        WINDOW
            w10 AS (ORDER BY created_at ROWS BETWEEN 9 PRECEDING AND CURRENT ROW),
            w_all AS (ORDER BY created_at ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)

        ORDER BY created_at
    """, [agent_id]).fetchdf()
```

## Parquet I/O

### Export to Parquet

```sql
-- Export entire table
COPY episodes TO 'data/episodes.parquet' (FORMAT PARQUET);

-- Export with column selection
COPY (
    SELECT episode_id, agent_id, kills, deaths, survival_time_ms
    FROM episodes
    WHERE generation >= 5
) TO 'data/episodes_gen5plus.parquet' (FORMAT PARQUET);

-- Partitioned export by generation
COPY (
    SELECT * FROM episodes
) TO 'data/episodes' (FORMAT PARQUET, PARTITION_BY (generation));
```

```python
# Python API
conn.execute("""
    COPY episodes
    TO 'data/episodes.parquet'
    (FORMAT PARQUET, COMPRESSION 'zstd')
""")
```

### Import from Parquet

```sql
-- Read single file
SELECT * FROM read_parquet('data/episodes.parquet');

-- Read multiple files with glob
SELECT * FROM read_parquet('data/episodes_*.parquet');

-- Read partitioned directory
SELECT * FROM read_parquet('data/episodes/**/*.parquet', hive_partitioning=true);

-- Create table from Parquet
CREATE TABLE episodes AS
SELECT * FROM read_parquet('data/episodes.parquet');
```

### Predicate Pushdown

```sql
-- Efficient: predicate pushed down to Parquet reader
SELECT * FROM read_parquet('data/episodes.parquet')
WHERE generation = 5 AND kills > 10;

-- Statistics-based filtering (no reading unnecessary row groups)
SELECT * FROM read_parquet('data/large_episodes.parquet')
WHERE created_at BETWEEN '2024-01-01' AND '2024-01-31';
```

### Cross-Agent Analysis

```python
def analyze_multi_agent_parquet(data_dir: Path) -> pd.DataFrame:
    """Analyze data from multiple agents via Parquet files."""
    conn = duckdb.connect(":memory:")

    # Read all agent Parquet files
    parquet_pattern = str(data_dir / "*/episodes.parquet")

    return conn.execute(f"""
        SELECT
            agent_id,
            generation,
            COUNT(*) as n_episodes,
            AVG(kills) as mean_kills,
            STDDEV(kills) as sd_kills,
            PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY kills) as median_kills,
            MAX(kills) as max_kills
        FROM read_parquet('{parquet_pattern}')
        GROUP BY agent_id, generation
        ORDER BY agent_id, generation
    """).fetchdf()
```

## DOE-Specific Query Patterns

### ANOVA Data Preparation

```python
def prepare_factorial_anova(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
) -> pd.DataFrame:
    """Prepare data for factorial ANOVA with all factor combinations."""
    return conn.execute("""
        SELECT
            er.factor_levels->>'memory' as memory,
            er.factor_levels->>'strength' as strength,
            e.kills as response
        FROM experiment_runs er
        JOIN episodes e ON e.run_id = er.run_id
        WHERE er.experiment_id = ?
        AND er.status = 'completed'
    """, [experiment_id]).fetchdf()
```

### Interaction Analysis

```sql
SELECT
    er.factor_levels->>'memory' as memory,
    er.factor_levels->>'strength' as strength,
    AVG(e.kills) as mean_kills,
    STDDEV(e.kills) as sd_kills,
    COUNT(*) as n
FROM experiment_runs er
JOIN episodes e ON e.run_id = er.run_id
WHERE er.experiment_id = 'DOE-042'
GROUP BY
    er.factor_levels->>'memory',
    er.factor_levels->>'strength'
ORDER BY memory, strength;
```

### Run Comparison with Window Functions

```sql
SELECT
    run_id,
    episode_id,
    kills,
    AVG(kills) OVER (PARTITION BY run_id) as run_mean,
    kills - AVG(kills) OVER (PARTITION BY run_id) as deviation_from_mean,
    RANK() OVER (PARTITION BY run_id ORDER BY kills DESC) as rank_in_run
FROM episodes
WHERE run_id IN (
    SELECT run_id FROM experiment_runs
    WHERE experiment_id = 'DOE-042'
)
ORDER BY run_id, rank_in_run;
```

### Outlier Detection

```python
def detect_outliers_zscore(
    conn: duckdb.DuckDBPyConnection,
    run_id: str,
    threshold: float = 3.0,
) -> pd.DataFrame:
    """Detect outliers using z-score method."""
    return conn.execute("""
        WITH stats AS (
            SELECT
                episode_id,
                kills,
                AVG(kills) OVER () as mean_kills,
                STDDEV(kills) OVER () as sd_kills
            FROM episodes
            WHERE run_id = ?
        )
        SELECT
            episode_id,
            kills,
            (kills - mean_kills) / NULLIF(sd_kills, 0) as z_score,
            CASE
                WHEN ABS((kills - mean_kills) / NULLIF(sd_kills, 0)) > ?
                THEN true
                ELSE false
            END as is_outlier
        FROM stats
        ORDER BY ABS(z_score) DESC
    """, [run_id, threshold]).fetchdf()
```

### Sample Size Verification

```python
def verify_sample_sizes(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
    expected_n: int = 30,
) -> pd.DataFrame:
    """Check that all factor combinations have expected sample size."""
    return conn.execute("""
        SELECT
            er.factor_levels->>'memory' as memory,
            er.factor_levels->>'strength' as strength,
            COUNT(*) as actual_n,
            ? as expected_n,
            COUNT(*) >= ? as meets_minimum
        FROM experiment_runs er
        JOIN episodes e ON e.run_id = er.run_id
        WHERE er.experiment_id = ?
        GROUP BY
            er.factor_levels->>'memory',
            er.factor_levels->>'strength'
        ORDER BY memory, strength
    """, [expected_n, expected_n, experiment_id]).fetchdf()
```

## Performance Tips

### Use Appender for Bulk Writes

```python
# SLOW: Row-by-row INSERT
for episode in episodes:
    conn.execute("INSERT INTO episodes VALUES (?, ?, ?)", [
        episode.id, episode.kills, episode.deaths
    ])

# FAST: Batch insert via Appender (Rust) or DataFrame (Python)
df = pd.DataFrame(episodes)
conn.execute("INSERT INTO episodes SELECT * FROM df")
```

### Set Appropriate Memory Limit

```python
conn.execute("PRAGMA memory_limit='4GB'")
conn.execute("PRAGMA threads=8")
```

### Use Columnar Operations

```python
# SLOW: Row-by-row processing
results = []
for row in conn.execute("SELECT * FROM episodes").fetchall():
    results.append(row[0] * 2)

# FAST: Columnar operation
df = conn.execute("SELECT kills * 2 as double_kills FROM episodes").fetchdf()
```

### Predicate Pushdown with Parquet

```python
# Efficient: filter pushed to Parquet reader
conn.execute("""
    SELECT * FROM read_parquet('large_file.parquet')
    WHERE generation = 5
""").fetchdf()
```

### EXPLAIN for Query Planning

```python
plan = conn.execute("""
    EXPLAIN SELECT
        agent_id, AVG(kills)
    FROM episodes
    GROUP BY agent_id
""").fetchdf()

print(plan)
```

## Anti-Patterns to Avoid

### Row-by-Row INSERT

```python
# ❌ WRONG: Very slow
for episode in episodes:
    conn.execute("INSERT INTO episodes VALUES (?, ?)", [episode.id, episode.kills])

# ✓ CORRECT: Batch insert
df = pd.DataFrame(episodes)
conn.execute("INSERT INTO episodes SELECT * FROM df")
```

### SELECT * When Few Columns Needed

```python
# ❌ WRONG: Reads all columns
df = conn.execute("SELECT * FROM episodes").fetchdf()
kills = df["kills"]

# ✓ CORRECT: Select only needed columns
kills = conn.execute("SELECT kills FROM episodes").fetchdf()["kills"]
```

### Not Using Transactions for Batch Operations

```python
# ❌ WRONG: Each insert is separate transaction
for episode in episodes:
    conn.execute("INSERT INTO episodes VALUES (?, ?)", [episode.id, episode.kills])

# ✓ CORRECT: Single transaction for batch
conn.execute("BEGIN TRANSACTION")
df = pd.DataFrame(episodes)
conn.execute("INSERT INTO episodes SELECT * FROM df")
conn.execute("COMMIT")
```

### Leaving Connections Open Unnecessarily

```python
# ❌ WRONG: Connection left open
def analyze_data():
    conn = duckdb.connect("data.duckdb")
    result = conn.execute("SELECT * FROM episodes").fetchdf()
    return result  # connection not closed!

# ✓ CORRECT: Use context manager
def analyze_data():
    with duckdb.connect("data.duckdb") as conn:
        return conn.execute("SELECT * FROM episodes").fetchdf()
```

### Ignoring WAL Mode for Concurrent Reads

```python
# For concurrent reads while writing, ensure WAL mode
conn.execute("PRAGMA journal_mode=WAL")
```

## Summary

- **Per-agent databases**: Avoid write contention, enable parallel processing
- **Parquet export/import**: Cross-agent analysis and archiving
- **Appender API (Rust)**: High-throughput bulk inserts
- **Window functions**: Powerful for time-series and ranking analysis
- **Predicate pushdown**: Critical for Parquet performance
- **Batch operations**: Always prefer batch over row-by-row
- **DOE schemas**: Structured for factorial analysis and ANOVA input
