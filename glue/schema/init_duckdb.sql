-- clau-doom DuckDB Schema
-- Stores all experiment data for DOE analysis

-- 1. experiments: Episode-level results (primary analysis table)
CREATE TABLE IF NOT EXISTS experiments (
    experiment_id TEXT NOT NULL,       -- e.g., 'DOE-001'
    run_id TEXT NOT NULL,              -- e.g., 'DOE-001-R1'
    condition TEXT NOT NULL,           -- 'random', 'rule_only', 'full_agent'
    baseline_type TEXT NOT NULL,       -- same as condition (for DOE-001)
    seed INTEGER NOT NULL,             -- episode seed for reproducibility
    episode_number INTEGER NOT NULL,   -- 1-indexed within condition

    -- Primary response
    kill_rate DOUBLE,                  -- kills per minute (kills / (survival_time / 60))

    -- Secondary responses
    kills INTEGER,
    survival_time DOUBLE,              -- seconds
    damage_dealt DOUBLE,
    damage_taken DOUBLE,
    ammo_efficiency DOUBLE,            -- hits / shots_fired [0,1]
    exploration_coverage DOUBLE,       -- cells_visited / total_cells [0,1]

    -- Tracking metrics
    decision_latency_p99 DOUBLE,       -- milliseconds
    rule_match_rate DOUBLE,            -- fraction of ticks with rule match [0,1]
    decision_level_counts TEXT,        -- JSON: {"0": N, "1": N, "2": N}

    -- Metadata
    total_ticks INTEGER,
    shots_fired INTEGER,
    hits INTEGER,
    cells_visited INTEGER,
    started_at TIMESTAMP DEFAULT current_timestamp,
    completed_at TIMESTAMP,

    PRIMARY KEY (experiment_id, condition, episode_number)
);

-- 2. encounters: Per-tick encounter records (detailed tracking)
CREATE TABLE IF NOT EXISTS encounters (
    experiment_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    episode_number INTEGER NOT NULL,
    tick INTEGER NOT NULL,

    enemies_visible INTEGER,
    health INTEGER,
    ammo INTEGER,
    position_x DOUBLE,
    position_y DOUBLE,
    angle DOUBLE,

    action_taken TEXT,                 -- 'MOVE_LEFT', 'MOVE_RIGHT', 'ATTACK'
    decision_level INTEGER,            -- 0, 1, or 2
    latency_ms DOUBLE,

    PRIMARY KEY (experiment_id, condition, episode_number, tick)
);

-- 3. doe_runs: DOE design matrix tracking
CREATE TABLE IF NOT EXISTS doe_runs (
    doe_id TEXT NOT NULL,              -- e.g., 'DOE-001'
    run_id TEXT NOT NULL,
    condition TEXT NOT NULL,
    factors TEXT,                       -- JSON: factor levels
    episodes_planned INTEGER,
    episodes_completed INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending',     -- pending/running/completed/failed
    started_at TIMESTAMP,
    completed_at TIMESTAMP,

    PRIMARY KEY (doe_id, run_id)
);

-- 4. strategy_docs: Local cache of OpenSearch strategy documents
CREATE TABLE IF NOT EXISTS strategy_docs (
    doc_id TEXT PRIMARY KEY,
    agent_id TEXT,
    generation INTEGER,
    situation_tags TEXT,                -- JSON array
    tactic TEXT,
    weapon TEXT,
    success_rate DOUBLE,
    sample_size INTEGER,
    confidence_tier TEXT,
    created_at TIMESTAMP DEFAULT current_timestamp,
    last_validated TIMESTAMP
);

-- 5. agent_configs: Agent configuration history
CREATE TABLE IF NOT EXISTS agent_configs (
    agent_id TEXT NOT NULL,
    generation INTEGER NOT NULL,
    config TEXT,                        -- JSON: full agent config
    md_path TEXT,
    created_at TIMESTAMP DEFAULT current_timestamp,

    PRIMARY KEY (agent_id, generation)
);

-- 6. generations: Generation evolution tracking
CREATE TABLE IF NOT EXISTS generations (
    generation INTEGER PRIMARY KEY,
    population_size INTEGER,
    best_fitness DOUBLE,
    mean_fitness DOUBLE,
    std_fitness DOUBLE,
    diversity_score DOUBLE,
    parent_selection TEXT,              -- JSON: selected parents
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- 7. seed_sets: Seed set registry for reproducibility
CREATE TABLE IF NOT EXISTS seed_sets (
    experiment_id TEXT PRIMARY KEY,
    seed_set TEXT NOT NULL,             -- JSON array of integers
    seed_count INTEGER NOT NULL,
    formula TEXT,                       -- e.g., 'seed_i = 42 + i * 31'
    created_at TIMESTAMP DEFAULT current_timestamp
);

-- Useful views for analysis
CREATE VIEW IF NOT EXISTS v_experiment_summary AS
SELECT
    experiment_id,
    condition,
    COUNT(*) as n,
    AVG(kill_rate) as mean_kill_rate,
    STDDEV(kill_rate) as sd_kill_rate,
    AVG(survival_time) as mean_survival,
    STDDEV(survival_time) as sd_survival,
    AVG(kills) as mean_kills,
    AVG(damage_dealt) as mean_damage,
    AVG(ammo_efficiency) as mean_ammo_eff,
    AVG(decision_latency_p99) as mean_latency_p99
FROM experiments
GROUP BY experiment_id, condition;
