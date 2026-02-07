# EXPERIMENT_ORDER_002: Memory x Strength Factorial

> **Experiment ID**: DOE-002
> **DOE Phase**: Phase 0/1 (Combined — Main Effects Screening + Interaction Detection)
> **DOE Type**: 2^2 Full Factorial with Center Points
> **Status**: ORDERED
> **Date Ordered**: 2026-02-07
> **Author**: research-pi

---

## Hypothesis Linkage

**Hypotheses**: H-006, H-007 (from HYPOTHESIS_BACKLOG.md)

- **H-006**: The Memory parameter (controlling DuckDB cache utilization and experience retention weight) has a significant main effect on agent kill efficiency in VizDoom Defend the Center.
- **H-007**: The Strength parameter (controlling Rust scoring weight for offensive actions) has a significant main effect on agent kill efficiency in VizDoom Defend the Center.

**Secondary Hypothesis**:
- **H-008** (exploratory): Memory and Strength interact — the benefit of higher Memory depends on the Strength level (and vice versa).

**Research Question**: Which agent configuration parameters (Memory, Strength) significantly affect kill efficiency, and do they interact?

**Reference Design Document**: S2-02_CORE_ASSUMPTION_ABLATION.md (factorial design principles)

---

## Experimental Design

### Design Type

2^2 Full Factorial with 3 Center Points.

- 2 factors, each at 2 levels (Low, High)
- 4 factorial cells + 3 center points = 7 unique configurations
- 30 episodes per factorial cell, 30 episodes per center point batch
- Total: 4 x 30 + 3 x 10 = 150 episodes

### Factor Definitions

| Factor | Symbol | Low (-1) | Center (0) | High (+1) | Unit |
|--------|--------|----------|------------|-----------|------|
| Memory | A | 0.3 | 0.5 | 0.7 | weight parameter |
| Strength | B | 0.3 | 0.5 | 0.7 | weight parameter |

**Memory** (Factor A): Controls how heavily the agent weighs DuckDB cached experience in decision-making. At low Memory (0.3), the agent relies less on past play history. At high Memory (0.7), past experience dominates over other signals.

**Strength** (Factor B): Controls the Rust scoring weight for offensive/aggressive action selection. At low Strength (0.3), the agent prefers defensive/cautious actions. At high Strength (0.7), the agent prioritizes attack actions.

### Design Matrix

| Run | Memory (A) | Strength (B) | Coded A | Coded B | Pattern | Episodes | Seed Set |
|-----|-----------|-------------|---------|---------|---------|----------|----------|
| 1 | 0.3 | 0.3 | -1 | -1 | (1) | 30 | seeds[0..29] |
| 2 | 0.7 | 0.3 | +1 | -1 | a | 30 | seeds[0..29] |
| 3 | 0.3 | 0.7 | -1 | +1 | b | 30 | seeds[0..29] |
| 4 | 0.7 | 0.7 | +1 | +1 | ab | 30 | seeds[0..29] |
| CP1 | 0.5 | 0.5 | 0 | 0 | center | 10 | seeds[0..9] |
| CP2 | 0.5 | 0.5 | 0 | 0 | center | 10 | seeds[10..19] |
| CP3 | 0.5 | 0.5 | 0 | 0 | center | 10 | seeds[20..29] |

**Total Episodes**: 120 (factorial) + 30 (center) = 150

### Agent Configuration Template

All runs use the Full RAG agent (L0+L1+L2 enabled) with the following parameter injection:

```yaml
agent_md_file: DOOM_PLAYER_DOE002.MD  # Parameterized template
decision_levels:
  level_0_md_rules: ENABLED
  level_1_duckdb_cache: ENABLED
  level_2_opensearch_knn: ENABLED
  level_3_claude_async: DISABLED
parameters:
  memory_weight: {A}    # Injected per run
  strength_weight: {B}  # Injected per run
scoring_weights:
  similarity: 0.4       # Fixed (not under study)
  confidence: 0.4       # Fixed (not under study)
  recency: 0.2          # Fixed (not under study)
baseline_type: full_agent
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

**Note**: Same scenario as DOE-001 to allow cross-experiment comparison.

---

## Sample Size

| Property | Value |
|----------|-------|
| Factorial cells | 4 |
| Center point runs | 3 |
| Episodes per factorial cell | 30 |
| Episodes per center point run | 10 |
| Total factorial episodes | 120 |
| Total center point episodes | 30 |
| Grand total episodes | 150 |
| Power target | 0.80 (1 - beta) |
| Significance level | alpha = 0.05 |
| Target effect size | f = 0.25 (medium, for ANOVA) |

**Power Justification**: For a 2^2 factorial ANOVA with n = 30 per cell:
- Main effect detection: power ~ 0.85 for medium effect (f = 0.25)
- Interaction detection: power ~ 0.80 for medium interaction effect
- Center points (n = 30 total) provide test for curvature with power ~ 0.70

---

## Seed Set

**Seed Generation Formula**: `seed_i = 1337 + i * 17` for `i = 0, 1, ..., 29`

**Verification**: All 30 seeds are unique integers (min: 1337, max: 1830, step: 17).

**Cross-Experiment Seed Collision Note**: This seed set shares one seed (1592) with DOE-001 seed set (seed_i = 42 + i*31 at i=50 yields 1592). This collision is acceptable because DOE-001 and DOE-002 test different factors (baseline comparison vs memory/strength parameters) with no paired comparison planned between them.

**Complete Seed Set (n = 30)**:

```
[1337, 1354, 1371, 1388, 1405, 1422, 1439, 1456, 1473, 1490,
 1507, 1524, 1541, 1558, 1575, 1592, 1609, 1626, 1643, 1660,
 1677, 1694, 1711, 1728, 1745, 1762, 1779, 1796, 1813, 1830]
```

**Seed Usage Rule**: ALL factorial cells use the IDENTICAL seed set (seeds[0..29]). Center points also draw from the same seed set (CP1: seeds[0..9], CP2: seeds[10..19], CP3: seeds[20..29]). This ensures identical map layouts and enemy spawns across conditions.

| Run | Condition | Seeds Used |
|-----|-----------|------------|
| 1 | Memory=0.3, Strength=0.3 | 1337, 1354, ..., 1830 (all 30) |
| 2 | Memory=0.7, Strength=0.3 | 1337, 1354, ..., 1830 (all 30) |
| 3 | Memory=0.3, Strength=0.7 | 1337, 1354, ..., 1830 (all 30) |
| 4 | Memory=0.7, Strength=0.7 | 1337, 1354, ..., 1830 (all 30) |
| CP1 | Memory=0.5, Strength=0.5 | 1337, 1354, ..., 1490 (seeds 0-9) |
| CP2 | Memory=0.5, Strength=0.5 | 1507, 1524, ..., 1660 (seeds 10-19) |
| CP3 | Memory=0.5, Strength=0.5 | 1677, 1694, ..., 1830 (seeds 20-29) |

---

## Run Order

Runs are randomized to control for temporal effects. The randomized execution order is:

| Execution Order | Run | Memory | Strength | Type |
|----------------|-----|--------|----------|------|
| 1 | 3 | 0.3 | 0.7 | Factorial |
| 2 | CP1 | 0.5 | 0.5 | Center |
| 3 | 1 | 0.3 | 0.3 | Factorial |
| 4 | 4 | 0.7 | 0.7 | Factorial |
| 5 | CP2 | 0.5 | 0.5 | Center |
| 6 | 2 | 0.7 | 0.3 | Factorial |
| 7 | CP3 | 0.5 | 0.5 | Center |

**Randomization Method**: Random permutation of runs with center points interspersed.

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

### Tracking Metrics

| Variable | Description | Purpose |
|----------|-------------|---------|
| decision_level | Which level produced action (0/1/2) | Check if Memory affects L1 usage |
| decision_latency_p99 | P99 tick decision time | Must be < 100ms |

---

## Statistical Analysis Plan

### Primary Analysis: 2-Way ANOVA

```
Source              | df  | Expected
--------------------|-----|----------
Memory (A)          | 1   | Significant if Memory affects kill_rate
Strength (B)        | 1   | Significant if Strength affects kill_rate
Memory*Strength (AxB)| 1  | Significant if interaction exists
Error               | 116 | (120 - 4 model df)
Total               | 119 |
```

**Parameters**:
- Type III Sum of Squares (unbalanced design safe)
- alpha = 0.05

### Center Point Analysis (Curvature Test)

Test whether the response surface has curvature (quadratic effects):

```
H0: mean(factorial points) = mean(center points)
H1: mean(factorial points) != mean(center points)

Test: t-test comparing average of 4 factorial cell means vs center point mean
If p < 0.05: Curvature present → recommend RSM follow-up (Phase 2)
If p >= 0.05: Linear model adequate for this region
```

### Residual Diagnostics

- [ ] Normality: Anderson-Darling test on residuals (p > 0.05 required)
- [ ] Equal variance: Levene's test across 4 cells (p > 0.05 required)
- [ ] Independence: Run-order plot (no systematic pattern)
- [ ] Outlier check: Studentized residuals > |3| flagged

### Non-Parametric Fallback

If normality fails (Anderson-Darling p < 0.05):
- Replace 2-way ANOVA with aligned rank transform (ART) ANOVA
- Or use Kruskal-Wallis as simplified alternative

### Effect Sizes

| Effect | Measure | Interpretation |
|--------|---------|---------------|
| Memory main effect | partial eta-squared | Small (0.01), Medium (0.06), Large (0.14) |
| Strength main effect | partial eta-squared | Small (0.01), Medium (0.06), Large (0.14) |
| AxB interaction | partial eta-squared | Small (0.01), Medium (0.06), Large (0.14) |
| Pairwise (Tukey) | Cohen's d | < 0.20 negligible, 0.20-0.49 small, 0.50-0.79 medium, >= 0.80 large |

### Post-Hoc Comparisons (If Interaction Significant)

If AxB interaction is significant (p < 0.05):
- Simple effects analysis: Test Memory effect at each Strength level separately
- Simple effects analysis: Test Strength effect at each Memory level separately
- Report pairwise differences with Tukey HSD correction

### Reporting Format

```
[STAT:f] F(1,116) = {value}  (for each factor/interaction)
[STAT:p] p = {value}
[STAT:eta2] partial eta^2 = {value}
[STAT:ci] 95% CI for mean difference: [{lower}, {upper}]
[STAT:effect_size] Cohen's d = {value}  (for pairwise)
[STAT:n] n = 30 per cell, 120 total factorial episodes
[STAT:power] observed power = {value}
```

---

## Diagnostics Checklist

Before analysis:
- [ ] All 150 episodes completed without container crash
- [ ] Seed integrity: all factorial cells used identical seed set
- [ ] Center points used correct subsets of seed set
- [ ] Parameter injection verified: Memory and Strength values match design matrix
- [ ] No duplicate episode IDs
- [ ] All metrics within plausible ranges

During analysis:
- [ ] Normality check (Anderson-Darling) on ANOVA residuals
- [ ] Equal variance check (Levene's test) across 4 factorial cells
- [ ] Run-order plot inspection (no systematic drift)
- [ ] Curvature test (factorial means vs center point mean)
- [ ] Interaction plot generated (Memory x Strength)

---

## Expected Outcomes

### Factorial Cell Predictions

| Memory | Strength | Expected kill_rate | Rationale |
|--------|----------|-------------------|-----------|
| 0.3 | 0.3 | 5-7 kills/min | Low experience + low aggression = cautious, inefficient |
| 0.7 | 0.3 | 7-9 kills/min | High experience + low aggression = smart but passive |
| 0.3 | 0.7 | 6-9 kills/min | Low experience + high aggression = aggressive but uninformed |
| 0.7 | 0.7 | 10-13 kills/min | High experience + high aggression = smart and aggressive |
| 0.5 | 0.5 | 7-10 kills/min | Center point: moderate on both dimensions |

### Expected Statistical Results

| Effect | Expected partial eta-squared | Expected p-value |
|--------|-------------------------------|-----------------|
| Memory (A) | 0.08-0.15 (medium-large) | < 0.05 |
| Strength (B) | 0.05-0.12 (medium) | < 0.05 |
| AxB Interaction | 0.02-0.08 (small-medium) | 0.05-0.15 (may or may not reach significance) |
| Curvature | — | > 0.10 (linear model likely adequate) |

### Interaction Prediction

If interaction is significant, the expected pattern is **synergistic**:
- The benefit of high Memory is greater when Strength is also high
- At Strength = 0.3, Memory 0.3->0.7 adds ~2 kills/min
- At Strength = 0.7, Memory 0.3->0.7 adds ~4 kills/min

This would indicate that experience (Memory) amplifies the effectiveness of aggressive play (Strength).

---

## Contingency Plans

### If Neither Factor is Significant (both p > 0.10)
1. Check parameter injection: verify that Memory and Strength values were actually different across runs
2. Check decision_level distribution: if agent rarely uses L1 (DuckDB), Memory parameter has no channel to affect behavior
3. Consider widening factor ranges (e.g., Memory [0.1, 0.9]) for stronger effect
4. Report as evidence that these parameters do not affect performance at tested levels

### If Interaction is Significant but Main Effects Are Not
1. The effect is entirely conditional — parameters only matter in combination
2. This is a crossover interaction — report simple effects at each level
3. Recommend follow-up DOE with more levels to map the response surface

### If Curvature Test is Significant (p < 0.05)
1. The linear model is insufficient — quadratic terms matter
2. Recommend Phase 2: RSM Central Composite Design (CCD) around optimal region
3. Design DOE-003 as augmented CCD adding axial points to existing factorial

### If High Variance Within Cells
1. Extend to n = 50 per cell (200 factorial episodes)
2. Add blocking by specific seed subsets
3. Consider covariates (initial enemy positions, weapon pickups)

---

## DuckDB Storage

```sql
-- All episodes stored in experiments table with:
experiment_id = 'DOE-002'
baseline_type = 'full_agent'
-- Factor levels stored in dedicated columns:
-- memory_weight DOUBLE
-- strength_weight DOUBLE

-- Query template for cell means
SELECT
    memory_weight,
    strength_weight,
    COUNT(*) as n,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    STDDEV(kills / (survival_time / 60.0)) as sd_kill_rate,
    AVG(survival_time) as mean_survival,
    AVG(ammo_efficiency) as mean_ammo_eff
FROM experiments
WHERE experiment_id = 'DOE-002'
GROUP BY memory_weight, strength_weight
ORDER BY memory_weight, strength_weight;

-- Center point comparison
SELECT
    CASE WHEN memory_weight = 0.5 THEN 'center' ELSE 'factorial' END as point_type,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    STDDEV(kills / (survival_time / 60.0)) as sd_kill_rate,
    COUNT(*) as n
FROM experiments
WHERE experiment_id = 'DOE-002'
GROUP BY point_type;
```

---

## Execution Instructions for research-doe-runner

1. **Setup Phase**:
   - Verify VizDoom container running with `defend_the_center.cfg`
   - Prepare parameterized agent MD template (DOOM_PLAYER_DOE002.MD)
   - Initialize DuckDB experiment_id = 'DOE-002'

2. **Execute in Randomized Order** (see Run Order table):
   - For each run: inject Memory and Strength values into agent MD file
   - Restart agent container with new parameters
   - Execute episodes with assigned seed set
   - Record all metrics with memory_weight and strength_weight columns

3. **Center Points**:
   - CP1, CP2, CP3 use Memory=0.5, Strength=0.5
   - Each uses a different 10-seed subset (for independent replication)

4. **Validation**:
   - Verify 150 episodes recorded (120 factorial + 30 center)
   - Confirm parameter values match design matrix
   - Seed integrity confirmed across all runs

---

## Visualization Requirements

### Main Effects Plot
- X-axis: Factor level (Low, High)
- Y-axis: Mean kill_rate with 95% CI error bars
- Two panels: one for Memory, one for Strength
- Include center point as reference marker

### Interaction Plot
- X-axis: Memory level (0.3, 0.5, 0.7)
- Y-axis: Mean kill_rate
- Separate lines for each Strength level
- Non-parallel lines indicate interaction

### Cell Means Table
- 2x2 table of mean (SD) kill_rate for each factorial cell
- Center point mean in the middle
- Color-coded by performance level

---

## Phase Transition Criteria

### If DOE-002 Results Support Phase 2 Transition

Trigger conditions for recommending Phase 2 (RSM):
1. At least one factor significant (p < 0.05) with medium+ effect
2. Interaction effect present (p < 0.10, suggestive)
3. OR curvature test significant (p < 0.05)

If triggered:
- Design DOE-003 as Central Composite Design (CCD) augmenting DOE-002
- Add axial points at alpha = 1.414 (face-centered or rotatable)
- Center on optimal region from DOE-002 results
- This enables response surface modeling for optimization

### If DOE-002 Does NOT Support Phase 2

If no significant effects:
- Widen factor ranges and retest (DOE-002b)
- OR add additional factors (e.g., Curiosity, Aggression)
- OR re-examine if parameters actually affect Rust scoring function

---

## Audit Trail

| Document | Status |
|----------|--------|
| HYPOTHESIS_BACKLOG.md | H-006, H-007, H-008 defined |
| EXPERIMENT_ORDER_002.md | This document (ORDERED) |
| EXPERIMENT_REPORT_002.md | Pending (after execution) |
| FINDINGS.md | Pending (after analysis) |
| RESEARCH_LOG.md | Entry pending |

---

## Metadata

| Property | Value |
|----------|-------|
| DOE Phase | 0/1 (Combined main effects + interaction) |
| Estimated Runtime | 2-3 hours (7 runs x 10-30 episodes each) |
| Data Volume | ~150 rows in experiments table |
| Dependencies | VizDoom container, DuckDB, OpenSearch, agent MD template |
| Predecessor Experiment | DOE-001 (Baseline comparison) |
| Potential Successor | DOE-003 (RSM-CCD if phase transition triggered) |
