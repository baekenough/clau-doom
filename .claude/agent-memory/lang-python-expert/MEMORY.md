# Python Expert Agent Memory

## Key Patterns

### Deferred Imports for CLI Scripts
- Always defer heavy imports (numpy, opensearch-py, sentence-transformers) into `main()`
- This ensures `--help` works without installing dependencies
- Pass `np` as first argument to functions that need it
- Keep only stdlib imports at module level

### Benchmark Script Structure
- Use `time.perf_counter_ns()` for nanosecond precision timing
- Warmup queries (100) before benchmark queries (1000) for stable measurements
- Output both to stdout AND save to markdown file in results/
- Include PASS/FAIL verdicts against target thresholds
- Use argparse with sensible defaults

### OpenSearch kNN
- Index: knn_vector field with HNSW (nmslib engine)
- Params: ef_construction=256, m=16, cosinesimil space_type
- Auth: admin/admin for default Docker setup
- Force merge after bulk indexing for consistent results
- Strategy doc schema: situation_embedding (384d), situation_tags, decision, quality

### Embedding Models
- ONNX MiniLM-L6-v2: 384 dim, local CPU, sentence-transformers
- Ollama nomic-embed-text: 768 dim, container HTTP API (localhost:11434)
- Semantic quality: similar pairs > 0.7 cosine, different pairs < 0.3

### DuckDB Python API
- Use `con.execute(sql)` for multi-statement SQL (handles comments and semicolons)
- `executescript` does NOT exist in DuckDB Python API (unlike sqlite3)
- `SHOW TABLES` returns list of tuples: `[('table_name',), ...]`
- `CREATE IF NOT EXISTS` makes schema idempotent
- DuckDB supports `STDDEV()` aggregate natively
- Default DB path: `data/clau-doom.duckdb` (matches Docker mount ../volumes/data:/app/data)
- Schema file: `glue/schema/init_duckdb.sql` (7 tables + 1 view)
- Init script: `glue/schema/init_duckdb.py` (CLI with --db-path)

### Virtual Environment
- Project uses `.venv` at project root (created via `uv`)
- Run scripts with `.venv/bin/python` for correct deps
- `uv` available at `/Users/sangyi/.local/bin/uv`
- System python is externally-managed (Homebrew), cannot pip install directly

### DOE Executor Pattern (glue/doe_executor.py)
- Reusable executor: ExperimentConfig + RunConfig dataclasses
- Builder functions (e.g. build_doe005_config) create experiment-specific configs
- EXPERIMENT_BUILDERS dict maps experiment IDs to builder functions
- Center points share condition string; use episode_number offsets (CP1: 1-10, CP2: 11-20, CP3: 21-30)
- Resumption: check _episode_exists() per episode, _count_run_episodes() per run
- action_fn.reset(seed=seed) MUST be called between episodes (passes seed for param-dependent RNG)
- Condition format: "memory={X}_strength={Y}"
- Run ID format: "{exp_id}-R{n}" for factorial, "{exp_id}-CP{n}" for center
- VizDoom/DuckDB imports deferred into execute_experiment() for --help

### VizDoom Glue Interfaces
- EpisodeRunner.run_episode(seed, condition, episode_number, action_fn) -> EpisodeResult
- EpisodeResult.metrics: EpisodeMetrics dataclass (kills, survival_time, etc.)
- FullAgentAction(memory_weight, strength_weight): __call__(state) -> int, reset(seed=0)
- FullAgentAction uses per-episode RNG seeded with hash((seed, memory, strength))
- Stochastic action selection: attack_prob = 0.4 + 0.55 * strength_weight
- Memory dodge: probability based on recent_health_loss / (30 * (1.1 - memory_weight))
- DOE-005 bug: old deterministic burst pattern produced identical results per seed
- Fix: stochastic + param-dependent RNG ensures different params -> different outcomes
- DuckDBWriter.write_episode(): metrics as dict, decision_level_counts as dict
- PK: (experiment_id, condition, episode_number) -- must avoid clashes for center points

## Project Files
- Benchmarks: `/Users/sangyi/workspace/research/clau-doom/scripts/benchmarks/`
- Results: `scripts/benchmarks/results/`
- Requirements: `scripts/benchmarks/requirements.txt`
