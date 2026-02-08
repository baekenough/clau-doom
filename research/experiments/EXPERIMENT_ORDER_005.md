# EXPERIMENT_ORDER_005: Memory x Strength Expanded Range Factorial

> **Experiment ID**: DOE-005
> **DOE Phase**: Phase 1 (Steepest Ascent -- Expanded Range Confirmation)
> **DOE Type**: 2^2 Full Factorial with Center Points
> **Status**: ORDERED
> **Date Ordered**: 2026-02-08
> **Author**: research-pi
> **Supersedes**: Previous DOE-005 (3x2 factorial + evolution hook, now obsolete after DOE-002 confirmed H-008)

---

## Hypothesis Linkage

**Hypothesis**: H-009 (from HYPOTHESIS_BACKLOG.md)

- **H-009**: Increasing memory_weight and strength_weight beyond 0.7 (toward 0.9) continues to improve kill_rate without diminishing returns.

**Secondary Hypothesis**:
- **H-004** (partial): Optimal memory_weight exists between 0.3-0.9. This experiment extends the tested range to [0.7, 0.9], contributing to H-004 resolution.

**Research Question**: Does the linear trend observed in DOE-002 (Memory and Strength both improve kill_rate at [0.3, 0.7]) continue at [0.7, 0.9], or does curvature (diminishing returns) appear?

**Reference Experiment**: DOE-002 (EXPERIMENT_ORDER_002.md, EXPERIMENT_REPORT_002.md)

**Steepest Ascent Rationale**: DOE-002 found a tilted plane with no curvature (p=0.9614) in the [0.3, 0.7] region. The optimal was at the high corner (0.7, 0.7) with 9.65 kills/min. Following steepest ascent methodology, we shift the design to the next region along the gradient -- the [0.7, 0.9] range -- to test whether the linear improvement continues.

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
| Memory | A | 0.7 | 0.8 | 0.9 | weight parameter |
| Strength | B | 0.7 | 0.8 | 0.9 | weight parameter |

**Memory** (Factor A): Controls how heavily the agent weighs DuckDB cached experience in decision-making. At Memory=0.7, matches DOE-002 high level. At Memory=0.9, pushes experience reliance near maximum.

**Strength** (Factor B): Controls the Rust scoring weight for offensive/aggressive action selection. At Strength=0.7, matches DOE-002 high level. At Strength=0.9, pushes aggression near maximum.

**Key Design Feature**: The low level (0.7) of this design overlaps with the high level (0.7) of DOE-002, providing a cross-experiment anchor point. Run 1 (Memory=0.7, Strength=0.7) should replicate DOE-002's best cell (9.65 kills/min), enabling direct comparison.

### Design Matrix

| Run | Memory (A) | Strength (B) | Coded A | Coded B | Pattern | Episodes | Seed Set |
|-----|-----------|-------------|---------|---------|---------|----------|----------|
| 1 | 0.7 | 0.7 | -1 | -1 | (1) | 30 | seeds[0..29] |
| 2 | 0.9 | 0.7 | +1 | -1 | a | 30 | seeds[0..29] |
| 3 | 0.7 | 0.9 | -1 | +1 | b | 30 | seeds[0..29] |
| 4 | 0.9 | 0.9 | +1 | +1 | ab | 30 | seeds[0..29] |
| CP1 | 0.8 | 0.8 | 0 | 0 | center | 10 | seeds[0..9] |
| CP2 | 0.8 | 0.8 | 0 | 0 | center | 10 | seeds[10..19] |
| CP3 | 0.8 | 0.8 | 0 | 0 | center | 10 | seeds[20..29] |

**Total Episodes**: 120 (factorial) + 30 (center) = 150

### Agent Configuration Template

All runs use the Full RAG agent (L0+L1+L2 enabled) with the following parameter injection:

```yaml
agent_md_file: DOOM_PLAYER_DOE005.md  # Parameterized template
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

**Note**: Same scenario as DOE-001 and DOE-002 to allow cross-experiment comparison.

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

**Note on Effect Size Expectations**: DOE-002 found very large effects (eta_p^2 = 0.41 for Memory, 0.32 for Strength) in the [0.3, 0.7] range. At [0.7, 0.9], effects may be smaller if diminishing returns begin. The n=30/cell design retains adequate power for medium effects even if the effects shrink substantially from DOE-002.

---

## Seed Set

**Seed Generation Formula**: `seed_i = 2501 + i * 23` for `i = 0, 1, ..., 29`

**Verification**: All 30 seeds are unique integers (min: 2501, max: 3168, step: 23).

**Cross-Experiment Seed Collision Check**:
- DOE-001 seed range: [42, 941] (formula: 42 + i*31, i=0..29) -- NO overlap with [2501, 3168]
- DOE-002 seed range: [1337, 1830] (formula: 1337 + i*17, i=0..29) -- NO overlap with [2501, 3168]
- Conclusion: Zero seed collisions across all experiments.

**Complete Seed Set (n = 30)**:

```
[2501, 2524, 2547, 2570, 2593, 2616, 2639, 2662, 2685, 2708,
 2731, 2754, 2777, 2800, 2823, 2846, 2869, 2892, 2915, 2938,
 2961, 2984, 3007, 3030, 3053, 3076, 3099, 3122, 3145, 3168]
```

**Seed Usage Rule**: ALL factorial cells use the IDENTICAL seed set (seeds[0..29]). Center points also draw from the same seed set (CP1: seeds[0..9], CP2: seeds[10..19], CP3: seeds[20..29]). This ensures identical map layouts and enemy spawns across conditions.

| Run | Condition | Seeds Used |
|-----|-----------|------------|
| 1 | Memory=0.7, Strength=0.7 | 2501, 2524, ..., 3168 (all 30) |
| 2 | Memory=0.9, Strength=0.7 | 2501, 2524, ..., 3168 (all 30) |
| 3 | Memory=0.7, Strength=0.9 | 2501, 2524, ..., 3168 (all 30) |
| 4 | Memory=0.9, Strength=0.9 | 2501, 2524, ..., 3168 (all 30) |
| CP1 | Memory=0.8, Strength=0.8 | 2501, 2524, ..., 2708 (seeds 0-9) |
| CP2 | Memory=0.8, Strength=0.8 | 2731, 2754, ..., 2938 (seeds 10-19) |
| CP3 | Memory=0.8, Strength=0.8 | 2961, 2984, ..., 3168 (seeds 20-29) |

---

## Run Order

Runs are randomized to control for temporal effects. The randomized execution order is:

| Execution Order | Run | Memory | Strength | Type |
|----------------|-----|--------|----------|------|
| 1 | 4 | 0.9 | 0.9 | Factorial |
| 2 | CP1 | 0.8 | 0.8 | Center |
| 3 | 2 | 0.9 | 0.7 | Factorial |
| 4 | 1 | 0.7 | 0.7 | Factorial |
| 5 | CP3 | 0.8 | 0.8 | Center |
| 6 | 3 | 0.7 | 0.9 | Factorial |
| 7 | CP2 | 0.8 | 0.8 | Center |

**Randomization Method**: Random permutation of runs with center points interspersed.

---

## Response Variables

### Response Hierarchy

**Primary analysis (confirmatory)**: kill_rate. The 2-way ANOVA on kill_rate is the sole confirmatory test for H-009. Significance thresholds and effect size criteria apply to kill_rate only.

**Secondary analysis (exploratory)**: survival_time, kills, damage_dealt, ammo_efficiency. Reported at nominal p-values with effect sizes and confidence intervals for descriptive insight. These do not drive hypothesis decisions.

### Primary Response

| Variable | Description | Unit | DuckDB Column |
|----------|-------------|------|---------------|
| kill_rate | Kills per minute of survival | kills/min | `kills / (survival_time / 60.0)` |

### Secondary Responses (Exploratory)

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
| decision_level | Which level produced action (0/1/2) | Check if Memory=0.9 changes L1 usage pattern |
| decision_latency_p99 | P99 tick decision time | Must be < 100ms |

---

## Statistical Analysis Plan

### Primary Analysis: 2-Way ANOVA on kill_rate (Confirmatory)

The confirmatory analysis is a 2-way ANOVA on kill_rate only. Secondary responses (survival_time, kills, damage_dealt, ammo_efficiency) are analyzed with the same ANOVA model but reported at nominal p-values as exploratory.

```
Source              | df  | Expected
--------------------|-----|----------
Memory (A)          | 1   | Significant if Memory still affects kill_rate at [0.7, 0.9]
Strength (B)        | 1   | Significant if Strength still affects kill_rate at [0.7, 0.9]
Memory*Strength (AxB)| 1  | Significant if interaction exists at expanded range
Error               | 116 | (120 - 4 model df)
Total               | 119 |
```

**Parameters**:
- Type III Sum of Squares (unbalanced design safe)
- alpha = 0.05

### Center Point Analysis (Curvature Test) -- CRITICAL FOR PHASE TRANSITION

Test whether the response surface has curvature (quadratic effects) at the expanded range:

```
H0: mean(factorial points) = mean(center points)
H1: mean(factorial points) != mean(center points)

Test: t-test comparing average of 4 factorial cell means vs center point mean
If p < 0.05: Curvature present -> diminishing returns detected -> Phase 2 RSM needed
If p >= 0.05: Linear model adequate -> trend continues or plateau reached
```

**This curvature test is the primary phase-transition decision criterion for H-009.** DOE-002 found no curvature at [0.3, 0.7]. If DOE-005 detects curvature at [0.7, 0.9], the response surface is nonlinear in this higher range, and RSM is warranted to find the exact optimal.

### Cross-Experiment Comparison with DOE-002

DOE-005 Run 1 (Memory=0.7, Strength=0.7) replicates DOE-002's best cell. Compare:

```
DOE-002 cell (0.7, 0.7): 9.65 kills/min (SD=1.53, n=30)
DOE-005 cell (0.7, 0.7): {observed} kills/min (SD={observed}, n=30)

Test: Two-sample Welch's t-test
H0: mu_DOE002 = mu_DOE005 for (0.7, 0.7) cell
H1: mu_DOE002 != mu_DOE005

If p > 0.05: Replication confirmed, cross-experiment comparisons valid
If p < 0.05: Environmental drift detected, cross-experiment comparisons require caution
```

This replication check validates that the experimental setup is stable between DOE-002 and DOE-005.

### Trend Analysis (DOE-002 + DOE-005 Combined)

If the replication check confirms consistency, combine DOE-002 and DOE-005 data to analyze the full [0.3, 0.9] trend:

```
Memory levels across combined data: [0.3, 0.5, 0.7, 0.8, 0.9]
Strength levels across combined data: [0.3, 0.5, 0.7, 0.8, 0.9]

Regression: kill_rate = b0 + b1*Memory + b2*Strength + b3*Memory^2 + b4*Strength^2 + ...
Test quadratic terms: if b3 or b4 significant, curvature exists in full range
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
- [ ] Cross-experiment replication check (DOE-005 cell (0.7,0.7) vs DOE-002 cell (0.7,0.7))

---

## Expected Outcomes

### Factorial Cell Predictions

| Memory | Strength | Expected kill_rate | Rationale |
|--------|----------|-------------------|-----------|
| 0.7 | 0.7 | ~9.65 kills/min | Replication of DOE-002 best cell |
| 0.9 | 0.7 | 10-12 kills/min | If linear trend continues (+2-3 from Memory increase) |
| 0.7 | 0.9 | 10-12 kills/min | If linear trend continues (+1-2 from Strength increase) |
| 0.9 | 0.9 | 12-15 kills/min | Best case: linear trend + synergistic interaction |
| 0.8 | 0.8 | 10-12 kills/min | Center point: midpoint of trend |

### Scenario A: Linear Trend Continues (No Curvature)

Expected if the response surface remains planar:
- All factor levels significant (p < 0.05)
- Curvature test NOT significant (p > 0.05)
- Center point mean near average of factorial means
- DOE-005 (0.9, 0.9) >> DOE-002 (0.7, 0.7)

**Implication**: Optimal lies at or beyond (0.9, 0.9). Consider testing [0.9, 1.0] or adopt (0.9, 0.9) as current best.

### Scenario B: Curvature Detected (Diminishing Returns)

Expected if the response surface curves:
- Curvature test significant (p < 0.05)
- Center point mean ABOVE average of factorial means (concave surface)
- Performance gains from 0.7->0.9 smaller than from 0.3->0.7

**Implication**: Optimal lies within [0.7, 0.9]. Proceed to Phase 2: RSM Central Composite Design (DOE-006) centered on the optimal region.

### Scenario C: Performance Plateau or Decline

Expected if extreme values cause problems (e.g., over-reliance on memory, over-aggression):
- Some cells may show decline relative to (0.7, 0.7)
- Particularly (0.9, 0.9) if extreme values cause pathological behavior

**Implication**: Optimal found near 0.7-0.8. Adopt as current best and focus on other factors.

### Expected Statistical Results

| Effect | Expected partial eta-squared | Expected p-value |
|--------|-------------------------------|-----------------|
| Memory (A) | 0.04-0.15 (smaller than DOE-002 if diminishing returns) | < 0.05 if trend continues |
| Strength (B) | 0.03-0.12 (smaller than DOE-002 if diminishing returns) | < 0.05 if trend continues |
| AxB Interaction | 0.01-0.06 | 0.05-0.20 (may or may not reach significance) |
| Curvature | -- | CRITICAL: determines phase transition |

---

## Contingency Plans

### If Both Factors Non-Significant (both p > 0.10)

1. Performance has plateaued -- the 0.7->0.9 range adds nothing
2. Optimal is near (0.7, 0.7) as found in DOE-002
3. Adopt (0.7, 0.7) as the best configuration for Memory and Strength
4. Pivot to other factors (H-005: document quality, DOE-003: layer ablation)

### If Curvature is Significant (p < 0.05)

1. Response surface is nonlinear at [0.7, 0.9] -- quadratic terms needed
2. Design DOE-006 as Central Composite Design (CCD) for RSM:
   - Center on estimated optimal from DOE-005 results
   - Add axial points at alpha = 1.414 (rotatable) or alpha = 1.0 (face-centered)
   - Enable response surface modeling: y = b0 + b1*A + b2*B + b11*A^2 + b22*B^2 + b12*A*B
3. This transitions the research to Phase 2

### If Replication Check Fails (DOE-005 (0.7,0.7) differs from DOE-002 (0.7,0.7))

1. Environmental drift or system instability detected
2. Investigate: seed differences, container changes, DuckDB state differences
3. If drift is small (<1 kill/min): proceed with caution, note caveat
4. If drift is large (>2 kills/min): investigate root cause before interpreting DOE-005

### If Interaction Pattern Changes

1. In DOE-002, interaction was synergistic (Memory amplifies Strength)
2. At [0.7, 0.9], interaction pattern may change (e.g., become antagonistic at extreme values)
3. Report interaction pattern change and implications for joint optimization

---

## DuckDB Storage

```sql
-- All episodes stored in experiments table with:
experiment_id = 'DOE-005'
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
WHERE experiment_id = 'DOE-005'
GROUP BY memory_weight, strength_weight
ORDER BY memory_weight, strength_weight;

-- Center point comparison
SELECT
    CASE WHEN memory_weight = 0.8 THEN 'center' ELSE 'factorial' END as point_type,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    STDDEV(kills / (survival_time / 60.0)) as sd_kill_rate,
    COUNT(*) as n
FROM experiments
WHERE experiment_id = 'DOE-005'
GROUP BY point_type;

-- Cross-experiment replication check
SELECT
    experiment_id,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    STDDEV(kills / (survival_time / 60.0)) as sd_kill_rate,
    COUNT(*) as n
FROM experiments
WHERE memory_weight = 0.7
  AND strength_weight = 0.7
  AND experiment_id IN ('DOE-002', 'DOE-005')
GROUP BY experiment_id;
```

---

## Execution Instructions for research-doe-runner

1. **Setup Phase**:
   - Verify VizDoom container running with `defend_the_center.cfg`
   - Prepare parameterized agent MD template (DOOM_PLAYER_DOE005.md)
   - Initialize DuckDB experiment_id = 'DOE-005'

2. **Execute in Randomized Order** (see Run Order table):
   - For each run: inject Memory and Strength values into agent MD file
   - Restart agent container with new parameters
   - Execute episodes with assigned seed set
   - Record all metrics with memory_weight and strength_weight columns

3. **Center Points**:
   - CP1, CP2, CP3 use Memory=0.8, Strength=0.8
   - Each uses a different 10-seed subset (for independent replication)

4. **Validation**:
   - Verify 150 episodes recorded (120 factorial + 30 center)
   - Confirm parameter values match design matrix
   - Seed integrity confirmed across all runs

---

## Visualization Requirements

### Main Effects Plot
- X-axis: Factor level (0.7, 0.8, 0.9)
- Y-axis: Mean kill_rate with 95% CI error bars
- Two panels: one for Memory, one for Strength
- Include center point as reference marker
- Overlay DOE-002 data points for trend visualization

### Interaction Plot
- X-axis: Memory level (0.7, 0.8, 0.9)
- Y-axis: Mean kill_rate
- Separate lines for each Strength level
- Non-parallel lines indicate interaction

### Cross-Experiment Trend Plot
- X-axis: Factor level (0.3, 0.5, 0.7, 0.8, 0.9) from DOE-002 + DOE-005
- Y-axis: Mean kill_rate
- Show full trend from DOE-002 through DOE-005
- Mark curvature detection threshold
- This is the most important visualization: does the line bend?

### Cell Means Table
- 2x2 table of mean (SD) kill_rate for each factorial cell
- Center point mean in the middle
- Color-coded by performance level
- Include DOE-002 best cell (9.65) as reference

---

## Phase Transition Criteria

### If DOE-005 Results Support Phase 2 Transition (RSM)

Trigger conditions for recommending Phase 2:
1. Curvature test significant (p < 0.05)
2. Performance gains diminishing but not zero
3. Response surface clearly nonlinear

If triggered:
- Design DOE-006 as Central Composite Design (CCD) covering [0.6, 1.0]
- Center on optimal region from DOE-005 results
- Add axial points at alpha = 1.414 (rotatable)
- Enable response surface modeling for optimization

### If DOE-005 Does NOT Support Phase 2

If curvature NOT significant and trend continues:
- Optimal is at boundary (0.9, 0.9) or beyond
- Consider one more steepest ascent step at [0.85, 1.0] if mechanistically plausible
- OR adopt (0.9, 0.9) as practical optimum if theoretical maximum approaches 1.0

If curvature NOT significant and no trend (plateau):
- Optimal is near (0.7, 0.7) -- DOE-002 result stands
- Pivot to other factors (DOE-003 layer ablation, DOE-004 doc quality)

---

## Audit Trail

| Document | Status |
|----------|--------|
| HYPOTHESIS_BACKLOG.md | H-009 active |
| EXPERIMENT_ORDER_005.md | This document (ORDERED) |
| EXPERIMENT_REPORT_005.md | Pending (after execution) |
| FINDINGS.md | Pending (after analysis) |
| RESEARCH_LOG.md | Entry pending |

---

## Metadata

| Property | Value |
|----------|-------|
| DOE Phase | 1 (Steepest Ascent -- Expanded Range) |
| Estimated Runtime | 2-3 hours (7 runs x 10-30 episodes each) |
| Data Volume | ~150 rows in experiments table |
| Dependencies | VizDoom container, DuckDB, OpenSearch, agent MD template |
| Predecessor Experiment | DOE-002 (Memory x Strength at [0.3, 0.7]) |
| Potential Successor | DOE-006 (RSM-CCD if curvature detected) |
