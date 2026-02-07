# EXPERIMENT_ORDER_003: Decision Layer Ablation

> **Hypothesis**: H-005 — Each decision layer adds measurable value
> **DOE Type**: 2^3 Full Factorial (Phase 1)
> **Status**: READY_FOR_EXECUTION
> **Created**: 2026-02-07
> **Estimated Runtime**: ~3-4 hours (8 conditions × 30 episodes)

---

## Hypothesis Linkage

**Hypothesis ID**: H-005 (from HYPOTHESIS_BACKLOG.md)

**Statement**: Each decision layer (Level 0: MD rules, Level 1: DuckDB cache, Level 2: OpenSearch kNN) independently contributes measurable performance improvement. The full stack outperforms any subset.

**Rationale**: Tests the core architectural assumption that the three-tier decision system provides additive benefits. If Full Stack (L0+L1+L2) is not significantly better than L0 Only, the RAG architecture lacks justification.

**Source**: S2-02_CORE_ASSUMPTION_ABLATION.md, Ablation 3

---

## Research Question

Do the three decision layers contribute independently to agent performance?

**Primary Question**: Is Full Stack (L0+L1+L2) significantly better than any single-layer or two-layer configuration?

**Secondary Questions**:
1. What is the main effect of each layer (L0, L1, L2)?
2. Do layers interact (synergy or antagonism)?
3. Which layer contributes most to performance?

---

## Experimental Design

### Design Type

**2^3 Full Factorial Design**

- 3 Binary Factors (each ON or OFF)
- 8 Experimental Conditions
- Fully Randomized Run Order
- Phase 1: Main effects + 2-way + 3-way interactions

### Factors

| Factor | Name | Low Level (OFF) | High Level (ON) | Implementation |
|--------|------|----------------|-----------------|----------------|
| **L0** | MD Rules | DISABLED | ENABLED | `skip_md_rules = true/false` in agent config |
| **L1** | DuckDB Cache | DISABLED | ENABLED | `skip_duckdb_lookup = true/false` in agent config |
| **L2** | OpenSearch kNN | DISABLED | ENABLED | `skip_opensearch_query = true/false` in agent config |

### Design Matrix

| Run | L0 | L1 | L2 | Condition Name | Config |
|-----|----|----|-----|----------------|--------|
| 1 | ON | ON | ON | Full Stack | All layers active (control) |
| 2 | ON | ON | OFF | L0+L1 Only | Rules + Local experience |
| 3 | ON | OFF | ON | L0+L2 Only | Rules + Collective knowledge |
| 4 | ON | OFF | OFF | L0 Only | Rules only (Baseline 2) |
| 5 | OFF | ON | ON | L1+L2 Only | Cache + Knowledge base |
| 6 | OFF | ON | OFF | L1 Only | Local experience only |
| 7 | OFF | OFF | ON | L2 Only | Collective knowledge only |
| 8 | OFF | OFF | OFF | No Layers | Default action fallback |

**Fallback Behavior**:
- When active layer(s) miss: Default action (MOVE_FORWARD)
- Full Stack: Cascading fallback L0 → L1 → L2 → default
- Run 8 (No Layers): Always default action (controlled floor)

---

## Scenario Configuration

### Game Environment

**Map**: VizDoom "Defend the Center" (default scenario)

**Difficulty**: Medium

**Enemy Configuration**: Standard spawn rates, mixed enemy types

**Time Limit**: 2100 tics (60 seconds) per episode

**Health/Ammo**: Default VizDoom starting conditions

### Agent Configuration

**Base Agent**: doom-agent-A (standard MD file structure)

**Strategy Profile**: Default balanced configuration
- play_style: balanced
- weapon_preference: balanced
- retreat_threshold: 0.5
- exploration_tendency: 0.5

**Decision Layer Configuration**: Modified per condition (see Design Matrix)

---

## Response Variables

### Response Hierarchy

**Primary analysis (confirmatory)**: kill_rate. The 2^3 factorial ANOVA on kill_rate is the sole confirmatory test for H-005 and drives the decision gate logic. Significance thresholds apply to kill_rate only.

**Secondary analysis (exploratory)**: survival_time, ammo_efficiency, decision_latency_ms. Reported at nominal p-values with effect sizes for descriptive insight. These do not drive hypothesis decisions or the STOP/PROCEED gate.

### Primary Response

| Variable | Definition | Source | Target |
|----------|-----------|--------|--------|
| **kill_rate** | Total kills per episode | `episodes.total_kills` | Maximize |

### Secondary Responses (Exploratory)

| Variable | Definition | Source | Target |
|----------|-----------|--------|--------|
| **survival_time** | Seconds survived | `episodes.survival_time` | Maximize |
| **ammo_efficiency** | Kills per 100 shots fired | Calculated: `(kills / ammo_used) * 100` | Maximize |
| **decision_latency_ms** | P99 decision time (ms) | `encounters.decision_latency_ms` aggregated | Minimize (< 100ms) |

### Tracking Variables (for analysis)

| Variable | Definition | Source |
|----------|-----------|--------|
| **decision_level_used** | Which level made decision (0/1/2/-1) | `encounters.decision_level` |
| **level_utilization_rate** | Fraction of decisions per level | Calculated per episode |
| **fallback_rate** | Fraction using default action | Calculated per episode |
| **action_divergence** | Cross-condition action difference | Pairwise comparison by situation_hash |

---

## Sample Size and Power

### Sample Size Calculation

**Target Effect Size**: f = 0.30 (medium effect for main factors)

**Significance Level**: α = 0.05

**Desired Power**: 1 - β = 0.80

**ANOVA Configuration**: 2^3 factorial (3 main effects, 3 two-way interactions, 1 three-way interaction)

**Required Sample Size**: n = 30 episodes per cell

- Power for main effects: ~0.82 (adequate)
- Power for two-way interactions: ~0.75 (acceptable)
- Total episodes: 8 conditions × 30 episodes = **240 episodes**

### Sample Allocation

```
All 8 conditions use IDENTICAL seed set (30 seeds).
Same seeds ensure within-subject comparisons are valid.
Differences are due to layer configuration only.
```

---

## Seed Set (n=30)

**Seed Generation Formula**: `seed_i = 2023 + i * 23` for `i = 0 to 29`

```
SEED_SET = [
  2023, 2046, 2069, 2092, 2115, 2138, 2161, 2184, 2207, 2230,
  2253, 2276, 2299, 2322, 2345, 2368, 2391, 2414, 2437, 2460,
  2483, 2506, 2529, 2552, 2575, 2598, 2621, 2644, 2667, 2690
]
```

**Seed Assignment**: Each condition uses all 30 seeds in episode order 1-30.

**Reproducibility Requirement**: [STAT:seed_set=fixed] [STAT:n=30]

---

## Randomized Run Order

Randomization performed to control for nuisance variables (time-of-day effects, system state, etc.).

**Run Sequence** (8 conditions, each with 30 episodes):

| Order | Condition | L0 | L1 | L2 | Episodes |
|-------|-----------|----|----|-----|----------|
| 1 | L1+L2 Only (Run 5) | OFF | ON | ON | 1-30 (seeds 0-29) |
| 2 | Full Stack (Run 1) | ON | ON | ON | 1-30 (seeds 0-29) |
| 3 | L0 Only (Run 4) | ON | OFF | OFF | 1-30 (seeds 0-29) |
| 4 | L2 Only (Run 7) | OFF | OFF | ON | 1-30 (seeds 0-29) |
| 5 | L0+L1 Only (Run 2) | ON | ON | OFF | 1-30 (seeds 0-29) |
| 6 | No Layers (Run 8) | OFF | OFF | OFF | 1-30 (seeds 0-29) |
| 7 | L0+L2 Only (Run 3) | ON | OFF | ON | 1-30 (seeds 0-29) |
| 8 | L1 Only (Run 6) | OFF | ON | OFF | 1-30 (seeds 0-29) |

**Execution Note**: Within each condition block, episodes are executed sequentially using seeds in order 0-29.

---

## Statistical Analysis Plan

### Primary Analysis: 2^3 Factorial ANOVA

**Model**:
```
kill_rate ~ L0 + L1 + L2 + L0*L1 + L0*L2 + L1*L2 + L0*L1*L2 + error
```

**No Layers (Run 8) Degenerate Cell Treatment**: The No Layers condition (Run 8: L0=OFF, L1=OFF, L2=OFF) is a degenerate cell where the agent always takes the default action (MOVE_FORWARD), producing a performance floor with near-zero variance. This cell is analyzed separately as a floor reference. The primary 2^3 factorial ANOVA uses all 8 conditions in the full model. If Levene's test fails due to variance heterogeneity driven by the No Layers cell, use one of the following fallbacks:
1. **Welch's ANOVA** (robust to unequal variances) for main-effect-only tests
2. **ART-ANOVA** (Aligned Rank Transform) for the full factorial model including interactions
3. Report results both with and without the No Layers cell and note any discrepancies

**ANOVA Table**:

| Source | df | Expected F-test |
|--------|----|--------------------|
| L0 (MD Rules) | 1 | Main effect of rules |
| L1 (DuckDB Cache) | 1 | Main effect of cache |
| L2 (OpenSearch kNN) | 1 | Main effect of kNN |
| L0 × L1 | 1 | Rules × Cache interaction |
| L0 × L2 | 1 | Rules × kNN interaction |
| L1 × L2 | 1 | Cache × kNN interaction |
| L0 × L1 × L2 | 1 | Three-way interaction |
| Error | 232 | Residual variance |
| **Total** | **239** | |

**Significance Criterion**: [STAT:alpha=0.05]

**Effect Size**: Partial eta-squared (η²) per factor and interaction

### Residual Diagnostics

**Normality Test**: Anderson-Darling test on residuals
- H0: Residuals are normally distributed
- Threshold: [STAT:p>0.05] for pass

**Equal Variance Test**: Levene's test
- H0: Variances are equal across conditions
- Threshold: [STAT:p>0.05] for pass

**Independence Check**: Run order plot inspection
- Visual check for systematic patterns
- No autocorrelation expected (randomized order)

### Planned Contrasts

**Pre-specified Expected Best Contrasts** (based on architectural rationale):
- **Contrast 1: Full Stack vs L0 Only** — Tests whether adding L1+L2 to the base rule system adds value. This is the primary contrast driving the decision gate.
- **Contrast 2: Full Stack vs L0+L2** — Tests whether L1 (DuckDB cache) adds incremental value on top of rules + knowledge base. L0+L2 is expected to be the strongest two-layer configuration.

These two contrasts are pre-specified because they test the most architecturally meaningful comparisons. Additional exploratory contrasts below are reported for completeness.

**Contrast 1: Full Stack vs. L0 Only** (PRIMARY — drives decision gate)
```
C1: (L0+L1+L2) vs. (L0 Only)
```

**Contrast 2: Full Stack vs. L0+L2** (SECONDARY — tests L1 incremental value)
```
C2: (L0+L1+L2) vs. (L0+L2 Only)
```

**Contrast 3: Two-Layer vs. Single-Layer (averaged, EXPLORATORY)**
```
C3: mean(L0+L1, L0+L2, L1+L2) vs. mean(L0, L1, L2)
```

### Post-Hoc Comparisons

**Method**: Tukey HSD for all pairwise comparisons

**Comparisons**: 8 choose 2 = 28 pairwise tests

**Family-wise Error Rate**: Controlled at α = 0.05

**Confidence Intervals**: [STAT:ci=95%] for each pairwise difference

---

## Expected Outcomes

### Performance Expectations

| Condition | Expected kill_rate (mean) | Expected decision_latency_p99 (ms) | Rationale |
|-----------|---------------------------|-------------------------------------|-----------|
| Full Stack (L0+L1+L2) | 10-12 | < 100 | All layers contribute, cascading fallback |
| L0+L1 Only | 7-10 | < 15 | Rules + local experience, fast |
| L0+L2 Only | 8-11 | < 100 | Rules + collective knowledge |
| L0 Only (Baseline 2) | 5-8 | < 3 | Static rules only, very fast |
| L1+L2 Only | 7-10 | < 100 | No rules, but cache + knowledge |
| L1 Only | 3-5 | < 10 | Local experience only, limited scope |
| L2 Only | 4-10 (variable) | < 100 | Knowledge base only, depends on doc quality |
| No Layers (default) | 1-3 | < 1 | Always MOVE_FORWARD, floor performance |

### Statistical Predictions

**Main Effects**:
- L0 main effect: [STAT:p<0.01] (rules provide baseline competence)
- L2 main effect: [STAT:p<0.05] (collective knowledge adds value)
- L1 main effect: [STAT:p<0.10] (cache may be weaker, depends on history)

**Interactions**:
- L0×L2 interaction: Possible synergy (rules guide when to use kNN)
- L1×L2 interaction: Possible redundancy (both retrieve strategies)
- L0×L1×L2: Likely non-significant (additive model sufficient)

---

## Decision Gate (CRITICAL)

The decision gate is evaluated on the **primary response (kill_rate)** only, using the post-hoc comparison: Full Stack vs. L0 Only.

### STOP Condition

**IF Full Stack (L0+L1+L2) is NOT significantly better than L0 Only:**

```
Criteria:
  - Post-hoc comparison: Full Stack vs. L0 Only
  - p-value: [STAT:p>0.10]
  - Effect size: [STAT:effect_size=Cohen's d<0.3] (small or negligible)
```

**THEN**:
1. **STOP** all subsequent experiments (DOE-004, DOE-005)
2. **Investigate** why upper layers (L1, L2) do not contribute
3. **Diagnostic Actions**:
   - Check decision_level distribution: Are L1/L2 actually being reached?
   - If L0 usage > 90%: Rule set is too comprehensive, reduces L1/L2 opportunity
   - If L2 usage > 10% but no performance gain: Document quality issue (see DOE-004)
4. **Recovery Plan**: Architectural redesign or simplification before proceeding

### PROCEED Condition

**IF Full Stack >> L0 Only:**

```
Criteria:
  - [STAT:p<0.05]
  - [STAT:effect_size=Cohen's d>0.5] (medium or large)
```

**THEN**:
- Proceed to DOE-004 (Document Quality Ablation)
- Proceed to DOE-005 (Evolution Test)
- RAG architecture validated

### CONDITIONAL Zone

**IF results fall between STOP and PROCEED thresholds** (i.e., neither clearly significant nor clearly null):

| Sub-case | Criteria | Action |
|----------|----------|--------|
| **C-1: Trending significant** | 0.05 < p < 0.10 AND d > 0.3 | Extend DOE-003 to n=50 per condition (400 total episodes) for higher power, then re-evaluate gate |
| **C-2: Significant but small** | p < 0.05 AND d < 0.5 | PROCEED with DOE-004 but flag as MEDIUM confidence; DOE-005 proceeds only if DOE-004 confirms RAG value |
| **C-3: Non-significant but moderate effect** | p > 0.10 AND 0.3 < d < 0.5 | Extend DOE-003 to n=50 per condition; if still non-significant after extension, STOP |
| **C-4: Diagnostic anomaly** | Any p-value AND L2 usage < 5% | STOP and investigate L2 utilization before proceeding (RAG may not be reached) |

**Rationale**: A binary STOP/PROCEED gate may discard borderline findings prematurely. The CONDITIONAL zone provides structured sub-rules to handle ambiguous results without ad-hoc post-hoc decisions.

---

## Execution Instructions

### For research-doe-runner

1. **Read** this EXPERIMENT_ORDER_003.md
2. **For each condition** (Run 1-8 in randomized order):
   a. Modify `doom-agent-A/AGENT.md` decision layer flags:
      - `skip_md_rules: {true|false}`
      - `skip_duckdb_lookup: {true|false}`
      - `skip_opensearch_query: {true|false}`
   b. Restart `doom-agent-A` container (wait 5s for initialization)
   c. Execute 30 episodes using SEED_SET in order
   d. Record to DuckDB `experiments` table:
      - `experiment_id = "DOE-003"`
      - `ablation_condition = "{condition_name}"` (e.g., "layer_full", "layer_l0")
      - `ablation_study = "abl_3_layers"`
      - `seed_set = SEED_SET`
   e. Record per-encounter `decision_level_used` to `encounters` table
3. **After all 240 episodes complete**:
   - Aggregate decision-level utilization statistics
   - Generate summary report: level_utilization_rate per condition
4. **Handoff to research-analyst** for ANOVA execution

### Agent MD Configuration Examples

**Full Stack (L0+L1+L2)**:
```yaml
decision_layers:
  skip_md_rules: false
  skip_duckdb_lookup: false
  skip_opensearch_query: false
```

**L0 Only**:
```yaml
decision_layers:
  skip_md_rules: false
  skip_duckdb_lookup: true
  skip_opensearch_query: true
```

**L2 Only**:
```yaml
decision_layers:
  skip_md_rules: true
  skip_duckdb_lookup: true
  skip_opensearch_query: false
```

---

## Data Recording

### DuckDB Schema

**experiments table** (per-episode):
```sql
experiment_id: "DOE-003"
ablation_condition: VARCHAR  -- "layer_full", "layer_l0", "layer_l01", etc.
ablation_study: "abl_3_layers"
seed: INT  -- one of SEED_SET
episode_number: INT  -- 1 to 30
total_kills: INT
survival_time: FLOAT
ammo_used: INT
-- Additional columns as per standard schema
```

**encounters table** (per-encounter):
```sql
episode_id: VARCHAR (FK to experiments)
decision_level: INT  -- 0 (L0), 1 (L1), 2 (L2), -1 (fallback)
decision_latency_ms: FLOAT
retrieval_similarity: FLOAT  -- if L2 used
-- Additional columns as per standard schema
```

**Aggregated Metrics** (computed post-execution):
```sql
-- Level utilization per condition
SELECT
  ablation_condition,
  decision_level,
  COUNT(*) as n_decisions,
  COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY ablation_condition) as utilization_pct,
  AVG(decision_latency_ms) as mean_latency
FROM encounters e
JOIN experiments ep ON e.episode_id = ep.episode_id
WHERE ep.experiment_id = 'DOE-003'
GROUP BY ablation_condition, decision_level
ORDER BY ablation_condition, decision_level;
```

---

## Analysis Output

**Target Document**: `EXPERIMENT_REPORT_003.md`

**Contents**:
1. ANOVA table with F-statistics and p-values [STAT:f] [STAT:p]
2. Effect sizes (partial η²) per factor and interaction [STAT:eta2]
3. Residual diagnostics results (normality, equal variance, independence)
4. Planned contrast results with confidence intervals [STAT:ci=95%]
5. Post-hoc pairwise comparisons (Tukey HSD)
6. Decision-level utilization summary table per condition
7. Interaction plots (if significant interactions found)
8. Recommendations for proceeding or stopping

**Trust Level Criteria**:
- **HIGH**: p < 0.01, effect size η² > 0.10, all diagnostics pass, n = 240
- **MEDIUM**: p < 0.05, effect size η² > 0.05, minor diagnostic violations
- **LOW**: p < 0.10 or effect size η² < 0.05
- **UNTRUSTED**: p ≥ 0.10

---

## Timeline

**Estimated Execution Time**:
- Setup: 30 min (agent config template preparation)
- Execution: 3-4 hours (8 conditions × 30 episodes × ~60s/episode)
- Analysis: 1-2 hours (ANOVA, diagnostics, plots)
- Reporting: 1 hour (EXPERIMENT_REPORT_003.md generation)

**Total**: ~6-8 hours

---

## Integration with Other Experiments

### Cross-References

- **Baseline 2** (from S2-01): L0 Only condition is identical. Data can be shared if same seed set used.
- **DOE-004** (Document Quality): Only proceed if Full Stack validates in DOE-003.
- **DOE-005** (Evolution Test): Only proceed if Full Stack validates in DOE-003.

### Dependency Chain

```
DOE-003 (Layer Ablation) → Decision Gate
  ├─ IF STOP: Investigate architecture, delay DOE-004/005
  └─ IF PROCEED: Execute DOE-004 and DOE-005
```

---

## Completion Criteria

- [x] Hypothesis H-005 linked to HYPOTHESIS_BACKLOG.md
- [x] 2^3 factorial design specified with all 8 conditions
- [x] Seed set generated (n=30, fixed)
- [x] Randomized run order specified
- [x] Response variables defined (primary + secondary + tracking)
- [x] Sample size justified with power analysis [STAT:n=240] [STAT:power≈0.80]
- [x] Statistical analysis plan specified (ANOVA, diagnostics, contrasts, post-hoc)
- [x] Decision gate criteria specified (STOP/PROCEED logic)
- [x] Execution instructions for research-doe-runner provided
- [x] DuckDB data recording schema specified
- [x] Expected outcomes and predictions documented
- [x] Integration with S2-01 baselines documented
- [x] EXPERIMENT_REPORT_003.md output specification provided

---

**Document Status**: READY_FOR_EXECUTION

**Next Steps**:
1. research-doe-runner → Execute DOE-003 as specified
2. research-analyst → Perform ANOVA and generate EXPERIMENT_REPORT_003.md
3. research-pi → Review report and apply Decision Gate logic
