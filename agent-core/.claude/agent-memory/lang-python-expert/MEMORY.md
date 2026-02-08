# Python Expert Agent Memory

## Project Environment
- Python venv location: `/Users/sangyi/workspace/research/clau-doom/.venv/`
- System Python (3.14) has PEP 668 restriction, always use venv
- Use `.venv/bin/python3 -m pip` to install (no standalone pip binary initially)
- Key deps: numpy, scipy, duckdb (installed in venv)

## Statistical Analysis Framework
- Location: `glue/analysis/` (statistical_tests.py, diagnostics.py, report_generator.py)
- Location: `glue/validation/` (seed_checker.py)
- Location: `glue/data/` (strategy_seed_generator.py)
- scipy 1.17+ requires `method='interpolate'` for `stats.anderson()` -- wrapped with try/except for backwards compat
- DuckDB schema at `glue/schema/init_duckdb.sql` with 7 tables
- Statistical evidence markers: `[STAT:p=X.XXX]`, `[STAT:ci=95%: X.X-Y.Y]`, `[STAT:effect_size=Cohen's d=X.XX]`

## DOE-001 Context
- 3 conditions: random, rule_only, full_agent
- 70 episodes each (210 total)
- Primary metric: kill_rate
- Seed formula: seed_i = 42 + i * 31

## DOE-002 Context
- 2^2 factorial: Memory [0.3, 0.7] x Strength [0.3, 0.7] + 3 center points
- 30 episodes per factorial cell (120) + 3x10 center (30) = 150 total
- Seed formula: seed_i = 1337 + i * 17
- Used separate DuckDB file: volumes/data/doe_002.duckdb (with memory_weight, strength_weight columns)
- statsmodels 0.14.6 installed for Type III ANOVA via ols() + anova_lm(typ=3)
- Key results: Memory p<0.0001 (eta2=0.42), Strength p<0.0001 (eta2=0.32), Interaction p=0.037 (eta2=0.04)
- Trust: MEDIUM (n=30 per cell, all diagnostics PASS)
- Phase transition triggered -> recommend RSM (DOE-003)

## Key Patterns for Factorial DOE Scripts
- Use np.random.default_rng(seed) per episode for reproducibility
- statsmodels ols("y ~ C(A) * C(B)") for factorial ANOVA
- anova_lm(model, typ=3) for Type III SS
- model.get_influence().resid_studentized_internal for outlier detection
- Curvature test: t-test comparing factorial vs center point observations
- DuckDB: use separate .duckdb files per DOE for isolation
