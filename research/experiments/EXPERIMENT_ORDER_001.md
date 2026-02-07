# EXPERIMENT_ORDER_001: Baseline Comparison (OFAT)

> **Experiment ID**: DOE-001
> **DOE Phase**: Phase 0 (Initial Comparison)
> **DOE Type**: OFAT (One Factor At a Time)
> **Status**: ORDERED
> **Date Ordered**: 2026-02-07
> **Author**: research-pi

---

## Hypothesis Linkage

**Hypotheses**: H-001, H-002 (from HYPOTHESIS_BACKLOG.md)

- **H-001**: The full RAG agent (L0+L1+L2) significantly outperforms a random action agent on VizDoom Defend the Center scenario.
- **H-002**: The full RAG agent (L0+L1+L2) significantly outperforms a rule-only agent (L0 only) on VizDoom Defend the Center scenario, demonstrating that RAG experience accumulation adds measurable value.

**Research Question**: Does the clau-doom RAG-based decision system produce statistically significant improvement over random and rule-only baselines?

**Reference Design Document**: S2-01_EVAL_BASELINES.md

---

## Experimental Design

### Design Type

OFAT — Three-condition single-factor comparison. The factor is **agent_type** with 3 levels:

| Level | Label | Description |
|-------|-------|-------------|
| 1 | Random | Uniform random action selection per tick (all decision levels disabled) |
| 2 | Rule-Only | Level 0 MD rules only (L1 DuckDB and L2 OpenSearch disabled) |
| 3 | Full RAG | Full decision hierarchy (L0 + L1 + L2 all enabled) |

### Factor: agent_type

| Property | Value |
|----------|-------|
| Name | agent_type |
| Type | Categorical (nominal) |
| Levels | 3 (Random, Rule-Only, Full RAG) |
| Nature | Between-subjects (each episode uses exactly one condition) |

### Configuration Per Condition

#### Condition 1: Random Agent

```yaml
agent_md_file: DOOM_PLAYER_BASELINE_RANDOM.MD
decision_levels:
  level_0_md_rules: DISABLED
  level_1_duckdb_cache: DISABLED
  level_2_opensearch_knn: DISABLED
  level_3_claude_async: DISABLED
action_selection: uniform_random
fallback_action: null  # Random selects from full action space
baseline_type: random
```

#### Condition 2: Rule-Only Agent

```yaml
agent_md_file: DOOM_PLAYER_BASELINE_RULEONLY.MD
decision_levels:
  level_0_md_rules: ENABLED
  level_1_duckdb_cache: DISABLED  # skip_duckdb_lookup = true
  level_2_opensearch_knn: DISABLED  # skip_opensearch_query = true
  level_3_claude_async: DISABLED
action_selection: rule_based
fallback_action: MOVE_FORWARD  # When no rule matches
baseline_type: rule_only
```

#### Condition 3: Full RAG Agent

```yaml
agent_md_file: DOOM_PLAYER_GEN1.MD  # Standard Generation-1 agent
decision_levels:
  level_0_md_rules: ENABLED
  level_1_duckdb_cache: ENABLED
  level_2_opensearch_knn: ENABLED
  level_3_claude_async: DISABLED  # No inter-episode LLM during experiment
action_selection: hierarchical_cascade
fallback_action: MOVE_FORWARD  # Only if all levels miss
baseline_type: full_agent
scoring_weights:
  similarity: 0.4
  confidence: 0.4
  recency: 0.2
```

---

## Scenario

| Property | Value |
|----------|-------|
| VizDoom Scenario | Defend the Center (`defend_the_center.cfg`) |
| Map | MAP01 |
| Enemy Types | Standard (as defined in scenario) |
| Available Weapons | Pistol (default) |
| Action Space | MOVE_LEFT, MOVE_RIGHT, ATTACK (3 discrete actions) |
| Episode Termination | Agent death or timeout (2100 tics = 60 seconds) |

---

## Sample Size

| Property | Value |
|----------|-------|
| Conditions | 3 |
| Episodes per condition | 70 |
| Total episodes | 210 |
| Power target | 0.80 (1 - beta) |
| Significance level | alpha = 0.05 (two-sided) |
| Target effect size | Cohen's d >= 0.50 (medium) |
| Justification | Power analysis (S2-01): n = 64 per group for medium effect with Welch's t-test, rounded to 70 for safety margin |

---

## Seed Set

**Seed Generation Formula**: `seed_i = 42 + i * 31` for `i = 0, 1, ..., 69`

**Rationale**: Base seed 42 is a conventional starting point in randomized testing (popularized by The Hitchhiker's Guide to the Galaxy). Step 31 is prime to avoid systematic patterns and ensure good dispersion. This formula aligns with the S2-01 master seed set methodology.

**Verification**: All 70 seeds are unique integers (min: 42, max: 2181, step: 31).

**Cross-Experiment Seed Collision Note**: This seed set shares one seed (1592) with DOE-002 seed set (seed_i = 1337 + i*17 at i=15 yields 1592). This collision is acceptable because DOE-001 and DOE-002 test different factors (baseline comparison vs memory/strength parameters) with no paired comparison planned between them.

**Complete Seed Set (n = 70)**:

```
[42, 73, 104, 135, 166, 197, 228, 259, 290, 321,
 352, 383, 414, 445, 476, 507, 538, 569, 600, 631,
 662, 693, 724, 755, 786, 817, 848, 879, 910, 941,
 972, 1003, 1034, 1065, 1096, 1127, 1158, 1189, 1220, 1251,
 1282, 1313, 1344, 1375, 1406, 1437, 1468, 1499, 1530, 1561,
 1592, 1623, 1654, 1685, 1716, 1747, 1778, 1809, 1840, 1871,
 1902, 1933, 1964, 1995, 2026, 2057, 2088, 2119, 2150, 2181]
```

**Seed Usage Rule**: ALL three conditions use the IDENTICAL seed set. Seed `seed_i` maps to episode `i` within each condition. This ensures identical map layouts and enemy spawns across conditions.

| Condition | Seed Set | Episodes |
|-----------|----------|----------|
| Random | seeds[0..69] | Episodes 1-70 |
| Rule-Only | seeds[0..69] | Episodes 71-140 |
| Full RAG | seeds[0..69] | Episodes 141-210 |

---

## Run Order

Runs are executed sequentially by condition (not interleaved) to avoid container reconfiguration overhead. Within each condition, episodes are executed in seed order.

| Run | Condition | Episode Range | Seeds Used |
|-----|-----------|---------------|------------|
| 1 | Random | 1-70 | 42, 73, ..., 2181 |
| 2 | Rule-Only | 71-140 | 42, 73, ..., 2181 |
| 3 | Full RAG | 141-210 | 42, 73, ..., 2181 |

**Randomization Note**: Run order is fixed (Random -> Rule-Only -> Full RAG) because conditions require different container configurations. Order effects are mitigated by identical seed sets and independent episodes.

---

## Response Variables

### Primary Response

| Variable | Description | Unit | DuckDB Column |
|----------|-------------|------|---------------|
| kill_rate | Kills per minute of survival | kills/min | `kills / (survival_time / 60.0)` |

### Secondary Responses

| Variable | Description | Unit | DuckDB Column |
|----------|-------------|------|---------------|
| survival_time | Time alive per episode | seconds | `experiments.survival_time` |
| kills | Total enemy kills per episode | integer | `experiments.kills` |
| damage_dealt | Total damage inflicted | HP | `experiments.damage_dealt` |
| damage_taken | Total damage received | HP | `experiments.damage_taken` |
| ammo_efficiency | Hits / shots fired | ratio [0,1] | `experiments.hits / experiments.shots_fired` |
| exploration_coverage | Fraction of map cells visited | ratio [0,1] | `experiments.cells_visited / map.total_cells` |

### Tracking Metrics (Non-response)

| Variable | Description | Conditions |
|----------|-------------|------------|
| rule_match_rate | Fraction of ticks with MD rule match | Rule-Only, Full RAG |
| decision_level | Which decision level produced action | Rule-Only (always 0), Full RAG (0/1/2) |
| decision_latency_p99 | P99 tick decision time | All (must be < 100ms) |

---

## Statistical Analysis Plan

### Primary Analysis: Welch's t-test (Pairwise)

Five pairwise comparisons:

| Comparison | Group A | Group B | Expected Direction |
|------------|---------|---------|-------------------|
| C1 | Full RAG | Random | Full RAG >> Random |
| C2 | Full RAG | Rule-Only | Full RAG > Rule-Only |
| C3 | Rule-Only | Random | Rule-Only > Random |

**Parameters**:
- Test: Welch's t-test (unequal variances assumed)
- Alternative: two-sided
- Significance: alpha = 0.05

### Multiple Comparison Correction

- Method: Holm-Bonferroni
- Family: 3 comparisons x 7 metrics = 21 tests
- Report both raw and adjusted p-values
- Significance threshold: adjusted p < 0.05

### Non-Parametric Fallback

If Anderson-Darling test on residuals yields p < 0.05:
- Replace Welch's t-test with Mann-Whitney U test
- Report: U statistic, p-value, rank-biserial correlation

### Effect Size

- Cohen's d for each pairwise comparison
- Interpretation: < 0.20 negligible, 0.20-0.49 small, 0.50-0.79 medium, >= 0.80 large

### Adaptive Stopping Rule

After 30 episodes per condition (90 total):
- If observed d > 1.0 with p < 0.01 for Full RAG vs Random: may stop early (overwhelming effect)
- If observed d < 0.20 for Full RAG vs Rule-Only: consider extending to n = 100
- Otherwise: continue to planned n = 70

### Reporting Format

```
[STAT:t] t({df}) = {value}
[STAT:p] p = {value} (adjusted: {adj_value})
[STAT:ci] 95% CI for mean difference: [{lower}, {upper}]
[STAT:effect_size] Cohen's d = {value}
[STAT:n] n_A = 70, n_B = 70
```

---

## Diagnostics Checklist

Before analysis:
- [ ] All 210 episodes completed without container crash
- [ ] Seed integrity: each condition used identical seed set
- [ ] No duplicate episode IDs
- [ ] All metrics within plausible ranges (kills >= 0, survival_time > 0)
- [ ] Decision latency P99 < 100ms for all conditions

During analysis:
- [ ] Normality check (Anderson-Darling) on residuals
- [ ] Equal variance check (Levene's test) on groups
- [ ] Run-order plot inspection (no systematic drift)

---

## Expected Outcomes

| Condition | Expected kill_rate | Expected survival_time | Rationale |
|-----------|--------------------|----------------------|-----------|
| Random | 0-2 kills/min | 10-30s | No intentional behavior |
| Rule-Only | 4-10 kills/min | 45-90s | Basic reactive rules |
| Full RAG | 10-15 kills/min | 60-120s | Situation-appropriate strategy retrieval |

### Expected Statistical Results

| Comparison | Expected Cohen's d | Expected p-value |
|------------|-------------------|-----------------|
| Full RAG vs Random | > 1.5 (large) | < 0.001 |
| Full RAG vs Rule-Only | 0.5-1.0 (medium-large) | < 0.05 |
| Rule-Only vs Random | > 1.0 (large) | < 0.001 |

---

## Contingency Plans

### If Random Agent performs unexpectedly well (> 5 kills/min)
1. Verify action space configuration (no hidden bias)
2. Check seed implementation (truly uniform random)
3. If confirmed: scenario may be too easy; switch to harder scenario

### If Rule-Only matches Full RAG (d < 0.20)
1. Core assumption (RAG adds value) challenged
2. Check rule_match_rate: if > 0.90, rules may cover most situations
3. Escalate to more complex scenarios
4. This is a publishable negative result

### If high variance makes comparison underpowered
1. Extend to n = 100 episodes per condition
2. Add blocking by map region or enemy density
3. Consider ANCOVA with episode-level covariates

---

## DuckDB Storage

```sql
-- All episodes stored in experiments table with:
experiment_id = 'DOE-001'
baseline_type IN ('random', 'rule_only', 'full_agent')
seed = {episode seed from seed set}

-- Query template for results
SELECT
    baseline_type,
    COUNT(*) as n,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    STDDEV(kills / (survival_time / 60.0)) as sd_kill_rate,
    AVG(survival_time) as mean_survival,
    AVG(ammo_efficiency) as mean_ammo_eff
FROM experiments
WHERE experiment_id = 'DOE-001'
GROUP BY baseline_type;
```

---

## Execution Instructions for research-doe-runner

1. **Setup Phase**:
   - Verify VizDoom container running with `defend_the_center.cfg`
   - Prepare agent MD files for each condition
   - Initialize DuckDB experiment_id = 'DOE-001'

2. **Run 1 (Random)**: Deploy DOOM_PLAYER_BASELINE_RANDOM.MD, disable all decision levels, run 70 episodes with seed set, record with baseline_type = 'random'

3. **Run 2 (Rule-Only)**: Deploy DOOM_PLAYER_BASELINE_RULEONLY.MD, enable L0 only, run 70 episodes with same seed set, record with baseline_type = 'rule_only'

4. **Run 3 (Full RAG)**: Deploy DOOM_PLAYER_GEN1.MD, enable all levels, run 70 episodes with same seed set, record with baseline_type = 'full_agent'

5. **Validation**: Verify 210 episodes recorded, seed integrity confirmed, no missing data

---

## Audit Trail

| Document | Status |
|----------|--------|
| HYPOTHESIS_BACKLOG.md | H-001, H-002 defined |
| EXPERIMENT_ORDER_001.md | This document (ORDERED) |
| EXPERIMENT_REPORT_001.md | Pending (after execution) |
| FINDINGS.md | Pending (after analysis) |
| RESEARCH_LOG.md | Entry pending |

---

## Metadata

| Property | Value |
|----------|-------|
| DOE Phase | 0 (Initial Comparison) |
| Estimated Runtime | 2-3 hours (3 runs x 70 episodes) |
| Data Volume | ~210 rows in experiments table |
| Dependencies | VizDoom container, DuckDB, agent MD files |
| Successor Experiment | DOE-002 (Memory x Strength factorial) |
