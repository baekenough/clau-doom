# EXPERIMENT_ORDER_006: Memory x Strength Wide Range Re-validation with Real KILLCOUNT

> **Experiment ID**: DOE-006
> **DOE Phase**: Phase 1 (Re-validation with Corrected Measurement)
> **DOE Type**: 2^2 Full Factorial with Center Points
> **Status**: ORDERED
> **Date Ordered**: 2026-02-08
> **Author**: research-pi
> **Predecessor**: DOE-002 (same factor range, INVALID data), DOE-005 (expanded range, real data)

---

## Hypothesis Linkage

**Hypothesis**: H-010 (from HYPOTHESIS_BACKLOG.md)

- **H-010**: Memory weight and strength weight have significant main effects on kill_rate in the [0.3, 0.7] range when measured with correct VizDoom KILLCOUNT (real kills, not AMMO2 bug).

**Secondary Hypothesis**:
- **H-004** (partial): Optimal memory_weight exists between 0.3-0.9. DOE-006 re-tests the [0.3, 0.7] subrange with valid measurement.

**Research Question**: Do Memory and Strength genuinely affect kill_rate in the [0.3, 0.7] range, or were DOE-002's large effects (Memory eta2=0.42, Strength eta2=0.32) artifacts of the AMMO2 mapping bug?

**Reference Experiments**:
- DOE-002 (EXPERIMENT_ORDER_002.md): Same [0.3, 0.7] range but INVALID data (AMMO2 mapped as kills)
- DOE-005 (EXPERIMENT_ORDER_005.md, EXPERIMENT_REPORT_005.md): [0.7, 0.9] range with REAL data, found performance plateau

**Re-validation Rationale**: DOE-002 reported Memory eta2=0.42 and Strength eta2=0.32 in the [0.3, 0.7] range -- enormous effects. However, a critical KILLCOUNT mapping bug was discovered during DOE-005 execution: the variable read as "kills" was actually AMMO2=26 (a constant). All DOE-002 kill_rate values were computed from fabricated kill counts. DOE-006 repeats the same factorial design with corrected measurement to determine whether the [0.3, 0.7] range genuinely produces behavioral differentiation.

**Combined Interpretation Plan**: If DOE-006 confirms effects at [0.3, 0.7], combined with DOE-005's null result at [0.7, 0.9], the performance plateau onset lies between 0.7 and 0.9. If DOE-006 also shows no effects, then Memory and Strength weight parameters do not meaningfully influence kill_rate at any tested range, and the DOE-002 findings were entirely artifacts.

---

## Experimental Design

### Design Type

2^2 Full Factorial with 3 Center Points.

- 2 factors, each at 2 levels (Low, High)
- 4 factorial cells + 3 center points = 7 unique configurations
- 30 episodes per factorial cell, 10 episodes per center point batch
- Total: 4 x 30 + 3 x 10 = 150 episodes

### Factor Definitions

| Factor | Symbol | Low (-1) | Center (0) | High (+1) | Unit |
|--------|--------|----------|------------|-----------|------|
| Memory | A | 0.3 | 0.5 | 0.7 | weight parameter |
| Strength | B | 0.3 | 0.5 | 0.7 | weight parameter |

**Memory** (Factor A): Controls how heavily the agent weighs DuckDB cached experience in decision-making. At Memory=0.3, the agent relies minimally on past episode history. At Memory=0.7, the agent heavily weights cached experience. This range matches DOE-002 exactly.

**Strength** (Factor B): Controls the Rust scoring weight for offensive/aggressive action selection. At Strength=0.3, the agent is cautious. At Strength=0.7, the agent prioritizes aggressive actions. This range matches DOE-002 exactly.

**Key Design Feature**: Identical factor range as DOE-002 ([0.3, 0.7] for both factors) enables direct comparison of effect sizes. However, DOE-006 uses corrected KILLCOUNT measurement, making it the definitive test. DOE-005's (0.7, 0.7) cell provides a cross-experiment anchor: DOE-005 measured 8.03 kills/min at (0.7, 0.7); DOE-006's Run R4 should replicate this value.

### Design Matrix

| Run | Memory (A) | Strength (B) | Coded A | Coded B | Pattern | Episodes | Seed Set |
|-----|-----------|-------------|---------|---------|---------|----------|----------|
| R1 | 0.3 | 0.3 | -1 | -1 | (1) | 30 | seeds[0..29] |
| R2 | 0.7 | 0.3 | +1 | -1 | a | 30 | seeds[0..29] |
| R3 | 0.3 | 0.7 | -1 | +1 | b | 30 | seeds[0..29] |
| R4 | 0.7 | 0.7 | +1 | +1 | ab | 30 | seeds[0..29] |
| CP1 | 0.5 | 0.5 | 0 | 0 | center | 10 | seeds[0..9] |
| CP2 | 0.5 | 0.5 | 0 | 0 | center | 10 | seeds[10..19] |
| CP3 | 0.5 | 0.5 | 0 | 0 | center | 10 | seeds[20..29] |

**Total Episodes**: 120 (factorial) + 30 (center) = 150

### Agent Configuration Template

All runs use the Full RAG agent (L0+L1+L2 enabled) with the following parameter injection:

```yaml
agent_md_file: DOOM_PLAYER_DOE006.md  # Parameterized template
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

**Note**: Same scenario as DOE-001, DOE-002, and DOE-005 for cross-experiment comparability.

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

**Effect Size Expectations**: DOE-005 found that real VizDoom kill_rate has SD ~ 3.7. If DOE-002's large effects (eta2 > 0.30) were genuine and not measurement artifacts, they should produce detectable differences at this sample size. If DOE-002 effects were artifacts, DOE-006 may observe small or null effects similar to DOE-005. The n=30/cell design retains adequate power to detect medium effects even in the pessimistic scenario.

---

## Seed Set

**Seed Generation Formula**: `seed_i = 3501 + i * 29` for `i = 0, 1, ..., 29`

**Verification**: All 30 seeds are unique integers (min: 3501, max: 4342, step: 29).

**Cross-Experiment Seed Collision Check**:
- DOE-001 seed range: [42, 2211] (formula: 42 + i*31, i=0..69) -- check [42, 2211] vs [3501, 4342] -- NO overlap
- DOE-002 seed range: [1337, 1830] (formula: 1337 + i*17, i=0..29) -- NO overlap with [3501, 4342]
- DOE-005 seed range: [2501, 3168] (formula: 2501 + i*23, i=0..29) -- NO overlap with [3501, 4342]
- Conclusion: Zero seed collisions across all experiments.

**Complete Seed Set (n = 30)**:

```
[3501, 3530, 3559, 3588, 3617, 3646, 3675, 3704, 3733, 3762,
 3791, 3820, 3849, 3878, 3907, 3936, 3965, 3994, 4023, 4052,
 4081, 4110, 4139, 4168, 4197, 4226, 4255, 4284, 4313, 4342]
```

**Seed Usage Rule**: ALL factorial cells use the IDENTICAL seed set (seeds[0..29]). Center points also draw from the same seed set (CP1: seeds[0..9], CP2: seeds[10..19], CP3: seeds[20..29]). This ensures identical map layouts and enemy spawns across conditions.

| Run | Condition | Seeds Used |
|-----|-----------|------------|
| R1 | Memory=0.3, Strength=0.3 | 3501, 3530, ..., 4342 (all 30) |
| R2 | Memory=0.7, Strength=0.3 | 3501, 3530, ..., 4342 (all 30) |
| R3 | Memory=0.3, Strength=0.7 | 3501, 3530, ..., 4342 (all 30) |
| R4 | Memory=0.7, Strength=0.7 | 3501, 3530, ..., 4342 (all 30) |
| CP1 | Memory=0.5, Strength=0.5 | 3501, 3530, ..., 3762 (seeds 0-9) |
| CP2 | Memory=0.5, Strength=0.5 | 3791, 3820, ..., 4052 (seeds 10-19) |
| CP3 | Memory=0.5, Strength=0.5 | 4081, 4110, ..., 4342 (seeds 20-29) |

---

## Run Order

Runs are randomized to control for temporal effects. The randomized execution order is:

| Execution Order | Run | Memory | Strength | Type |
|----------------|-----|--------|----------|------|
| 1 | R3 | 0.3 | 0.7 | Factorial |
| 2 | CP2 | 0.5 | 0.5 | Center |
| 3 | R1 | 0.3 | 0.3 | Factorial |
| 4 | R4 | 0.7 | 0.7 | Factorial |
| 5 | CP1 | 0.5 | 0.5 | Center |
| 6 | R2 | 0.7 | 0.3 | Factorial |
| 7 | CP3 | 0.5 | 0.5 | Center |

**Randomization Method**: Pre-specified random permutation with center points interspersed.

---

## Response Variables

### Response Hierarchy

**Primary analysis (confirmatory)**: kill_rate. The 2-way ANOVA on kill_rate is the sole confirmatory test for H-010. Significance thresholds and effect size criteria apply to kill_rate only.

**Secondary analysis (exploratory)**: survival_time, kills. Reported at nominal p-values with effect sizes and confidence intervals for descriptive insight. These do not drive hypothesis decisions.

### Primary Response

| Variable | Description | Unit | DuckDB Column |
|----------|-------------|------|---------------|
| kill_rate | Kills per minute of survival | kills/min | `kills / (survival_time / 60.0)` |

### Secondary Responses (Exploratory)

| Variable | Description | Unit | DuckDB Column |
|----------|-------------|------|---------------|
| survival_time | Time alive per episode | seconds | `experiments.survival_time` |
| kills | Total enemy kills per episode | integer | `experiments.kills` |

### Tracking Metrics

| Variable | Description | Purpose |
|----------|-------------|---------|
| decision_level | Which level produced action (0/1/2) | Check if Memory weight changes L1 usage pattern |
| decision_latency_p99 | P99 tick decision time | Must be < 100ms |

---

## Statistical Analysis Plan

### Primary Analysis: 2-Way ANOVA on kill_rate (Confirmatory)

The confirmatory analysis is a 2-way ANOVA on kill_rate only. Secondary responses (survival_time, kills) are analyzed with the same ANOVA model but reported at nominal p-values as exploratory.

```
Source              | df  | Expected
--------------------|-----|----------
Memory (A)          | 1   | Significant if Memory affects kill_rate at [0.3, 0.7] with real data
Strength (B)        | 1   | Significant if Strength affects kill_rate at [0.3, 0.7] with real data
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
If p < 0.05: Curvature present -> Phase 2 RSM warranted
If p >= 0.05: Linear model adequate
```

DOE-002 found no curvature at [0.3, 0.7] (p=0.9614), but that was with invalid data. DOE-005 found no curvature at [0.7, 0.9] (p=0.6242) with real data. DOE-006 re-tests curvature at [0.3, 0.7] with real data.

### Cross-Experiment Comparison with DOE-005

DOE-006 Run R4 (Memory=0.7, Strength=0.7) overlaps with DOE-005 Run 1 (Memory=0.7, Strength=0.7). Compare:

```
DOE-005 cell (0.7, 0.7): 8.03 kills/min (SD=3.67, n=30)
DOE-006 cell (0.7, 0.7): {observed} kills/min (SD={observed}, n=30)

Test: Two-sample Welch's t-test
H0: mu_DOE005 = mu_DOE006 for (0.7, 0.7) cell
H1: mu_DOE005 != mu_DOE006

If p > 0.05: Replication confirmed, experimental setup is stable
If p < 0.05: Environmental drift detected, investigate
```

This replication check validates measurement consistency between DOE-005 and DOE-006, both of which use corrected KILLCOUNT data.

### Residual Diagnostics

- [ ] Normality: Anderson-Darling test on residuals (p > 0.05 required)
- [ ] Equal variance: Levene's test across 4 cells (p > 0.05 required)
- [ ] Independence: Run-order plot (no systematic pattern)
- [ ] Outlier check: Studentized residuals > |3| flagged

### Non-Parametric Fallback

If normality fails (Anderson-Darling p < 0.05):
- Replace 2-way ANOVA with aligned rank transform (ART) ANOVA
- Or use Kruskal-Wallis as simplified alternative
- DOE-005 demonstrated that real VizDoom kill_rate data is typically non-normal (zero-inflated, right-skewed). Non-parametric methods should be planned as co-primary.

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
- [ ] KILLCOUNT mapping confirmed as real kills (not AMMO2)
- [ ] No duplicate episode IDs
- [ ] All metrics within plausible ranges

During analysis:
- [ ] Normality check (Anderson-Darling) on ANOVA residuals
- [ ] Equal variance check (Levene's test) across 4 factorial cells
- [ ] Run-order plot inspection (no systematic drift)
- [ ] Curvature test (factorial means vs center point mean)
- [ ] Interaction plot generated (Memory x Strength)
- [ ] Cross-experiment replication check (DOE-006 R4 vs DOE-005 Run 1)

---

## Expected Outcomes

### Factorial Cell Predictions

Based on DOE-005 baseline (~8.4 kills/min at [0.7, 0.9] plateau) and the wider factor separation in DOE-006:

| Memory | Strength | Expected kill_rate | Rationale |
|--------|----------|-------------------|-----------|
| 0.3 | 0.3 | 5-8 kills/min | Lowest settings, potentially below plateau |
| 0.7 | 0.3 | 6-9 kills/min | High memory, low strength |
| 0.3 | 0.7 | 5-8 kills/min | Low memory, high strength |
| 0.7 | 0.7 | ~8.0 kills/min | Replication of DOE-005 (0.7, 0.7) cell |
| 0.5 | 0.5 | 6-8 kills/min | Center point |

Note: Predictions are uncertain because DOE-002 data was invalid. Real kill_rate dynamics at [0.3, 0.7] are unknown.

### Scenario A: Effects Confirmed (Re-validation Succeeds)

Expected if Memory and/or Strength genuinely differentiate agent behavior:
- At least one main effect significant (p < 0.05) with medium or larger effect size
- Cell (0.7, 0.7) > cell (0.3, 0.3) by a practically meaningful margin
- Cross-experiment replication with DOE-005 cell (0.7, 0.7) succeeds (p > 0.05)

**Implication**: Memory and Strength DO matter in the [0.3, 0.7] range. Combined with DOE-005's null result at [0.7, 0.9], the plateau onset is between 0.7 and 0.9. Adopt Memory=0.7, Strength=0.7 as the optimal and close the Memory-Strength optimization thread.

### Scenario B: Effects Not Confirmed (DOE-002 Was Entirely Artifact)

Expected if the measurement bug was the sole driver of DOE-002's effects:
- No main effects significant (all p > 0.10)
- Similar to DOE-005: flat response surface across [0.3, 0.7]
- Memory and Strength weight parameters have no real influence on kill_rate

**Implication**: The entire DOE-002 effect structure was a measurement artifact. Memory_weight and strength_weight do not influence real gameplay performance at ANY tested range. Pivot entirely to other factors (layer ablation, document quality, scenario complexity).

### Scenario C: Partial Effects (Reduced but Real)

Expected if effects exist but are smaller than DOE-002 reported:
- One factor significant, the other borderline (p near 0.05)
- Effect sizes small-to-medium (eta2 between 0.03-0.10)
- Some cell separation but less dramatic than DOE-002

**Implication**: Parameters have real but modest influence. The large DOE-002 effects were inflated by measurement bias, but a genuine behavioral gradient exists. Further optimization may have limited practical value (small effect sizes suggest diminishing returns from parameter tuning).

---

## Contingency Plans

### If Both Factors Non-Significant (both p > 0.10)

1. Memory_weight and strength_weight do not influence kill_rate at any tested range
2. Close the Memory-Strength optimization thread completely
3. Investigate WHY these parameters have no effect (action function analysis)
4. Pivot to structural factors: layer ablation (DOE-003), document quality (DOE-004)

### If Curvature is Significant (p < 0.05)

1. Response surface is nonlinear in [0.3, 0.7] -- quadratic terms needed
2. Design DOE-007 as Central Composite Design (CCD) for RSM:
   - Center on estimated optimal from DOE-006 results
   - Add axial points at alpha = 1.414 (rotatable) or alpha = 1.0 (face-centered)
3. This transitions the research to Phase 2

### If Replication Check Fails (DOE-006 R4 differs from DOE-005 Run 1)

1. Environmental drift or system instability detected
2. Investigate: DuckDB state differences, container changes, KILLCOUNT mapping consistency
3. If drift is small (<1.5 kills/min): proceed with caution, note caveat
4. If drift is large (>2.0 kills/min): investigate root cause before interpreting DOE-006

---

## DuckDB Storage

```sql
-- All episodes stored in experiments table with:
experiment_id = 'DOE-006'
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
    AVG(kills) as mean_kills
FROM experiments
WHERE experiment_id = 'DOE-006'
GROUP BY memory_weight, strength_weight
ORDER BY memory_weight, strength_weight;

-- Center point comparison
SELECT
    CASE WHEN memory_weight = 0.5 THEN 'center' ELSE 'factorial' END as point_type,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    STDDEV(kills / (survival_time / 60.0)) as sd_kill_rate,
    COUNT(*) as n
FROM experiments
WHERE experiment_id = 'DOE-006'
GROUP BY point_type;

-- Cross-experiment replication check (DOE-006 R4 vs DOE-005 Run 1)
SELECT
    experiment_id,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    STDDEV(kills / (survival_time / 60.0)) as sd_kill_rate,
    COUNT(*) as n
FROM experiments
WHERE memory_weight = 0.7
  AND strength_weight = 0.7
  AND experiment_id IN ('DOE-005', 'DOE-006')
GROUP BY experiment_id;
```

---

## Execution Instructions for research-doe-runner

1. **Setup Phase**:
   - Verify VizDoom container running with `defend_the_center.cfg`
   - **CRITICAL**: Verify KILLCOUNT mapping reads REAL kills (not AMMO2). Run 1-2 test episodes and confirm kills vary (not constant 26).
   - Prepare parameterized agent MD template (DOOM_PLAYER_DOE006.md)
   - Initialize DuckDB experiment_id = 'DOE-006'

2. **Execute in Randomized Order** (see Run Order table):
   - Execution order: R3, CP2, R1, R4, CP1, R2, CP3
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
   - Verify kills values are NOT constant (AMMO2 bug regression check)

---

## Visualization Requirements

### Main Effects Plot
- X-axis: Factor level (0.3, 0.5, 0.7)
- Y-axis: Mean kill_rate with 95% CI error bars
- Two panels: one for Memory, one for Strength
- Include center point as reference marker
- Overlay DOE-005 (0.7, 0.7) data point for cross-experiment comparison

### Interaction Plot
- X-axis: Memory level (0.3, 0.5, 0.7)
- Y-axis: Mean kill_rate
- Separate lines for each Strength level
- Non-parallel lines indicate interaction

### Cross-Experiment Comparison Plot
- X-axis: Factor level (0.3, 0.5, 0.7, 0.8, 0.9) from DOE-006 + DOE-005
- Y-axis: Mean kill_rate
- Show combined trend from DOE-006 through DOE-005 (all real data)
- Mark plateau region if DOE-006 shows effects but DOE-005 does not

### Cell Means Table
- 2x2 table of mean (SD) kill_rate for each factorial cell
- Center point mean in the middle
- Color-coded by performance level
- Include DOE-005 (0.7, 0.7) reference value (8.03 kills/min)

---

## Phase Transition Criteria

### If DOE-006 Confirms Effects + Curvature Detected

Trigger conditions for Phase 2 RSM:
1. At least one main effect significant (p < 0.05)
2. Curvature test significant (p < 0.05)
3. Performance gradient exists in the design region

If triggered:
- Design DOE-007 as Central Composite Design (CCD) covering [0.2, 0.8]
- Center on estimated optimal from DOE-006 results
- Add axial points for second-order model
- Enable response surface modeling for optimization

### If DOE-006 Confirms Effects + No Curvature

If effects are real but linear:
- Optimal is at the (0.7, 0.7) corner of the design region
- Combined with DOE-005 plateau result: (0.7, 0.7) IS the optimal
- Adopt Memory=0.7, Strength=0.7 as best configuration
- Close Memory-Strength optimization thread

### If DOE-006 Shows No Effects

If effects are non-significant (all p > 0.10):
- Memory_weight and strength_weight do not influence real gameplay
- Close Memory-Strength optimization thread
- Pivot to other factors entirely

---

## Audit Trail

| Document | Status |
|----------|--------|
| HYPOTHESIS_BACKLOG.md | H-010 active |
| EXPERIMENT_ORDER_006.md | This document (ORDERED) |
| EXPERIMENT_REPORT_006.md | Pending (after execution) |
| FINDINGS.md | Pending (after analysis) |
| RESEARCH_LOG.md | Entry logged (2026-02-08) |

---

## Metadata

| Property | Value |
|----------|-------|
| DOE Phase | 1 (Re-validation with Corrected Measurement) |
| Estimated Runtime | 2-3 hours (7 runs x 10-30 episodes each) |
| Data Volume | ~150 rows in experiments table |
| Dependencies | VizDoom container, DuckDB, OpenSearch, agent MD template |
| Predecessor Experiments | DOE-002 (same range, invalid data), DOE-005 (expanded range, real data) |
| Potential Successors | DOE-007 (RSM-CCD if curvature), or close thread (if plateau confirmed) |
