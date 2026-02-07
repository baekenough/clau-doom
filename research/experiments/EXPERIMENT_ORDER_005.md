# EXPERIMENT_ORDER_005: Memory-Strength Interaction with Evolution Hook

> **Hypothesis**: H-008 — Memory and strength interact to affect kill efficiency + Evolution test
> **DOE Type**: 3×2 Full Factorial with Center Points (Phase 1)
> **Status**: READY_FOR_EXECUTION
> **Created**: 2026-02-07
> **Estimated Runtime**: ~4-5 hours (6 conditions + 3 center points, 30 episodes each)

---

## Hypothesis Linkage

**Hypothesis ID**: H-008 (from HYPOTHESIS_BACKLOG.md)

**Statement**: Memory and strength interact to affect kill efficiency. Specifically, memory enhances kill efficiency more at higher strength levels (synergistic interaction).

**Formal Statement**:

Let Y_ijk denote kill_rate for Memory level i, Strength level j, replicate k.

**Null Hypotheses**:
- H0_M: No main effect of Memory
- H0_S: No main effect of Strength
- H0_MS: No Memory × Strength interaction

**Alternative Hypotheses**:
- H1_M: At least one Memory level differs
- H1_S: At least one Strength level differs
- H1_MS: Memory × Strength interaction exists (non-additive effects)

**Directional Prediction**: Interaction significant (p < 0.05), with Memory benefit increasing as Strength increases.

**Rationale**: Tests whether agent parameters interact (require joint optimization) or are independent (can be tuned separately). Also serves as the first test of the evolution system by using this experiment's results to inform Generation 1 → Generation 2 transition.

**Source**: Synthesis from clau-doom agent design patterns

---

## Research Question

Do Memory and Strength interact to affect kill efficiency?

**Primary Question**: Is the Memory × Strength interaction term significant?

**Secondary Questions**:
1. What is the main effect of Memory (averaged over Strength)?
2. What is the main effect of Strength (averaged over Memory)?
3. Which Memory-Strength combination yields the highest kill rate?
4. Can Generation 2 (evolved from best performer) outperform Generation 1 best?

---

## Experimental Design

### Design Type

**3×2 Full Factorial with Center Points (Phase 1)**

- 2 Factors (Memory, Strength)
- Memory: 3 Levels (0.3, 0.5, 0.7)
- Strength: 2 Levels (0.3, 0.7)
- 6 Factorial Conditions
- 3 Center Points (Memory=0.5, Strength=0.5, replicated 3 times)
- Fully Randomized Run Order

### Factors

| Factor | Symbol | Levels | Range | Unit |
|--------|--------|--------|-------|------|
| **Memory** | M | 3: [0.3, 0.5, 0.7] | 0.0-1.0 | Dimensionless (agent parameter) |
| **Strength** | S | 2: [0.3, 0.7] | 0.0-1.0 | Dimensionless (agent parameter) |

**Factor Interpretation**:
- **Memory**: Agent's ability to recall past encounters and apply learned strategies. Higher = better recall.
- **Strength**: Agent's combat effectiveness and damage output. Higher = more damage per hit.

### Design Matrix (Factorial Points)

| Run | Memory | Strength | Condition Label | Episodes |
|-----|--------|----------|----------------|----------|
| 1 | 0.3 | 0.3 | M_low_S_low | 30 |
| 2 | 0.3 | 0.7 | M_low_S_high | 30 |
| 3 | 0.5 | 0.3 | M_mid_S_low | 30 |
| 4 | 0.5 | 0.7 | M_mid_S_high | 30 |
| 5 | 0.7 | 0.3 | M_high_S_low | 30 |
| 6 | 0.7 | 0.7 | M_high_S_high | 30 |

**Total Factorial Episodes**: 6 conditions × 30 episodes = **180 episodes**

### Center Points

| Run | Memory | Strength | Condition Label | Episodes | Purpose |
|-----|--------|----------|----------------|----------|---------|
| CP1 | 0.5 | 0.5 | Center_1 | 30 | Detect curvature (non-linear effects) |
| CP2 | 0.5 | 0.5 | Center_2 | 30 | Replicate for pure error estimation |
| CP3 | 0.5 | 0.5 | Center_3 | 30 | Third replicate for robustness |

**Total Center Point Episodes**: 3 replicates × 30 episodes = **90 episodes**

**Total Experiment Episodes**: 180 + 90 = **270 episodes**

**Rationale for Center Points**: Center points at (0.5, 0.5) test whether the response surface is linear or quadratic. If center point mean differs significantly from the average of factorial points, curvature exists and Phase 2 RSM-CCD should be planned.

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

**Fixed Parameters** (not manipulated):
- play_style: balanced
- weapon_preference: balanced
- retreat_threshold: 0.5
- exploration_tendency: 0.5

**Manipulated Parameters** (per condition):
- memory: [0.3, 0.5, 0.7]
- strength: [0.3, 0.5, 0.7]

**Decision Layers**: All layers active (L0+L1+L2)
- `skip_md_rules: false`
- `skip_duckdb_lookup: false`
- `skip_opensearch_query: false`

---

## Response Variables

### Primary Response

| Variable | Definition | Source | Target |
|----------|-----------|--------|--------|
| **kill_rate** | Total kills per episode | `episodes.total_kills` | Maximize |

### Secondary Responses

| Variable | Definition | Source | Target |
|----------|-----------|--------|--------|
| **survival_time** | Seconds survived | `episodes.survival_time` | Maximize |
| **damage_dealt** | Total damage to enemies | `episodes.damage_dealt` | Maximize |
| **ammo_efficiency** | Kills per 100 shots fired | Calculated: `(kills / ammo_used) * 100` | Maximize |

### Evolution-Specific Tracking

| Variable | Definition | Source |
|----------|-----------|--------|
| **best_performer_combo** | Memory-Strength combination with highest mean kill_rate | Post-ANOVA analysis |
| **generation_1_best** | Best agent from this experiment's 6 conditions | Factorial point with max mean kill_rate |
| **generation_2_genome** | Evolved genome from Generation 1 best | Evolution operator output |

---

## Sample Size and Power

### Sample Size Calculation

**Design**: 3×2 factorial ANOVA

**Target Effect Size**: f = 0.25 (medium effect for interactions)

**Significance Level**: α = 0.05

**Desired Power**: 1 - β = 0.80

**Required Sample Size**:
- G*Power: n = 30 per cell for f=0.25, α=0.05, power=0.80
- Achieved: **n = 30 per cell**
- Total: 6 cells × 30 = 180 factorial episodes

**Center Points**: 3 replicates × 30 episodes = 90 center point episodes

**Total Power**:
- Main effects: power ≈ 0.85 (adequate)
- Interaction: power ≈ 0.80 (target achieved)
- Curvature test: power ≈ 0.75 (acceptable)

### Sample Allocation

```
All conditions (factorial + center points) use IDENTICAL seed set (30 seeds).
Same seeds ensure within-subject comparisons are valid.
```

---

## Seed Set (n=30)

**Seed Generation Formula**: `seed_i = 9999 + i * 19` for `i = 0 to 29`

```
SEED_SET = [
  9999, 10018, 10037, 10056, 10075, 10094, 10113, 10132, 10151, 10170,
  10189, 10208, 10227, 10246, 10265, 10284, 10303, 10322, 10341, 10360,
  10379, 10398, 10417, 10436, 10455, 10474, 10493, 10512, 10531, 10550
]
```

**Seed Assignment**: Each condition uses all 30 seeds in episode order 1-30.

**Reproducibility Requirement**: [STAT:seed_set=fixed] [STAT:n=30]

---

## Randomized Run Order

Randomization performed to control for nuisance variables.

**Run Sequence** (9 total runs: 6 factorial + 3 center points):

| Order | Condition | Memory | Strength | Episodes |
|-------|-----------|--------|----------|----------|
| 1 | Center_2 | 0.5 | 0.5 | 1-30 (seeds 0-29) |
| 2 | M_high_S_low (Run 5) | 0.7 | 0.3 | 1-30 (seeds 0-29) |
| 3 | M_low_S_high (Run 2) | 0.3 | 0.7 | 1-30 (seeds 0-29) |
| 4 | M_mid_S_high (Run 4) | 0.5 | 0.7 | 1-30 (seeds 0-29) |
| 5 | Center_1 | 0.5 | 0.5 | 1-30 (seeds 0-29) |
| 6 | M_low_S_low (Run 1) | 0.3 | 0.3 | 1-30 (seeds 0-29) |
| 7 | M_high_S_high (Run 6) | 0.7 | 0.7 | 1-30 (seeds 0-29) |
| 8 | M_mid_S_low (Run 3) | 0.5 | 0.3 | 1-30 (seeds 0-29) |
| 9 | Center_3 | 0.5 | 0.5 | 1-30 (seeds 0-29) |

**Execution Note**: Within each condition block, episodes are executed sequentially using seeds in order 0-29.

---

## Statistical Analysis Plan

### Primary Analysis: Two-Way ANOVA with Interaction

**Model** (Factorial Points Only):
```
kill_rate ~ Memory + Strength + Memory*Strength + error
```

**ANOVA Table**:

| Source | df | Expected F-test |
|--------|----|--------------------|
| Memory (M) | 2 | Main effect of memory |
| Strength (S) | 1 | Main effect of strength |
| Memory × Strength (M×S) | 2 | Interaction effect |
| Error | 174 | Residual variance |
| **Total** | **179** | |

**Significance Criterion**: [STAT:alpha=0.05]

**Effect Size**: Partial eta-squared (η²) per factor and interaction

### Curvature Test (Center Points)

**Comparison**: Mean of center points vs. mean of factorial points

**Model**:
```
kill_rate ~ Factorial_vs_Center + error
```

**Test Statistic**:
```
t = (mean_center - mean_factorial) / SE_pooled
df = 180 + 90 - 2 = 268
```

**Significance**: [STAT:p<0.05] indicates curvature (non-linear effects present)

**If Significant**: Plan Phase 2 RSM-CCD around optimal region

### Residual Diagnostics

**Normality Test**: Anderson-Darling test on residuals
- H0: Residuals are normally distributed
- Threshold: [STAT:p>0.05] for pass

**Equal Variance Test**: Levene's test
- H0: Variances are equal across conditions
- Threshold: [STAT:p>0.05] for pass

**Independence Check**: Run order plot inspection
- Visual check for systematic patterns

### Simple Effects Analysis (if interaction significant)

**If Memory × Strength interaction is significant (p < 0.05)**:

Decompose interaction by testing:

1. **Simple effect of Memory at each Strength level**:
   - Memory effect at Strength=0.3 (one-way ANOVA on 3 Memory levels)
   - Memory effect at Strength=0.7 (one-way ANOVA on 3 Memory levels)

2. **Simple effect of Strength at each Memory level**:
   - Strength effect at Memory=0.3 (t-test on 2 Strength levels)
   - Strength effect at Memory=0.5 (t-test on 2 Strength levels)
   - Strength effect at Memory=0.7 (t-test on 2 Strength levels)

**Interpretation**: Identify at which levels of one factor the other factor matters most.

### Post-Hoc Comparisons

**Method**: Tukey HSD for pairwise comparisons within significant main effects

**Comparisons**:
- If Memory main effect significant: 3 choose 2 = 3 pairs (0.3 vs 0.5, 0.3 vs 0.7, 0.5 vs 0.7)
- If Strength main effect significant: 1 pair (0.3 vs 0.7)

**Family-wise Error Rate**: Controlled at α = 0.05

**Confidence Intervals**: [STAT:ci=95%] for each pairwise difference

---

## Expected Outcomes

### Performance Expectations

| Memory | Strength | Expected kill_rate (mean) | Rationale |
|--------|----------|---------------------------|-----------|
| 0.3 | 0.3 | 5-7 | Low memory, low strength → baseline |
| 0.3 | 0.7 | 7-9 | High strength compensates for low memory |
| 0.5 | 0.3 | 6-8 | Moderate memory, low strength |
| 0.5 | 0.5 | 8-10 | Balanced (center point average) |
| 0.5 | 0.7 | 9-11 | Moderate memory, high strength |
| 0.7 | 0.3 | 8-10 | High memory compensates for low strength |
| 0.7 | 0.7 | 11-14 | High memory + high strength → synergy |

**Center Point** (0.5, 0.5): mean ~ 8-10

**Predicted Best Performer**: Memory=0.7, Strength=0.7 (synergistic combination)

### Statistical Predictions

**Main Effects**:
- Memory main effect: [STAT:f=F(2,174)>6.0] [STAT:p<0.01] [STAT:eta2>0.06]
- Strength main effect: [STAT:f=F(1,174)>8.0] [STAT:p<0.01] [STAT:eta2>0.04]

**Interaction**:
- Memory × Strength: [STAT:f=F(2,174)>4.0] [STAT:p<0.05] [STAT:eta2>0.04]
- **Interpretation**: Memory enhances kill efficiency more at higher Strength levels

**Curvature Test**:
- Center point vs. factorial: [STAT:p>0.10] (likely linear, but test required)
- If significant: Plan RSM-CCD in Phase 2

---

## Evolution Hook: Generation 1 → Generation 2

### Phase 1: Identify Best Performer (Generation 1)

After ANOVA completes, identify the Memory-Strength combination with the highest mean kill_rate.

**Expected Best**: Memory=0.7, Strength=0.7

**Generation 1 Genome** (best performer):
```yaml
agent_id: doom-agent-Gen1-best
memory: 0.7
strength: 0.7
play_style: balanced
weapon_preference: balanced
retreat_threshold: 0.5
exploration_tendency: 0.5
```

### Phase 2: Evolution Operator (Generation 1 → 2)

Apply evolution operator to generate **Generation 2 genome**:

**Evolution Strategy**: Mutation around best performer
- Perturb Memory: ±0.1 (bounds: [0.0, 1.0])
- Perturb Strength: ±0.1 (bounds: [0.0, 1.0])
- Small perturbations test local optimization

**Generation 2 Genome Candidates** (3 variants):

| Variant | Memory | Strength | Mutation |
|---------|--------|----------|----------|
| Gen2-A | 0.8 | 0.7 | Memory +0.1 |
| Gen2-B | 0.7 | 0.8 | Strength +0.1 |
| Gen2-C | 0.8 | 0.8 | Both +0.1 |

**Selection**: Choose Gen2-C (both parameters increased) as primary Generation 2 genome.

**Capping**: If Memory or Strength exceeds 1.0, cap at 1.0. If below 0.0, cap at 0.0.

### Phase 3: Evolution Test (Generation 2 vs. Generation 1)

**Test Design**: Paired comparison

**Hypothesis**: H_evol: Generation 2 (evolved) outperforms Generation 1 (best)

**Null Hypothesis**: H0: μ_Gen2 = μ_Gen1

**Alternative Hypothesis**: H1: μ_Gen2 > μ_Gen1 (one-tailed test)

**Sample Size**: n = 30 episodes per generation

**Seed Set**: **SAME** as DOE-005 (SEED_SET from above)

**Test**: Paired t-test
```
t = (mean_Gen2 - mean_Gen1) / SE_diff
df = 29
One-tailed p-value: P(T > t | H0)
```

**Execution**:
1. Run Generation 1 best (Memory=0.7, Strength=0.7) for 30 episodes (ALREADY DONE in DOE-005)
2. Run Generation 2 (Memory=0.8, Strength=0.8) for 30 episodes (NEW, same seeds)
3. Compute paired differences: d_i = Gen2_kills_i - Gen1_kills_i for i=1..30
4. Test: [STAT:t-test] [STAT:p<0.05] for significance

**Expected Outcome**: [STAT:p<0.05] [STAT:effect_size=Cohen's d>0.3] (Gen2 improves on Gen1)

**If Successful**:
- Generation 2 validated as an improvement
- Evolution system confirmed functional
- Proceed to multi-generation experiments (10+ generations)

**If Unsuccessful**:
- Gen2 does not improve on Gen1
- Investigate mutation strategy (perturbation too small or too large?)
- Consider: Local optimum reached, require exploration vs. exploitation balance

---

## Execution Instructions

### For research-doe-runner

#### Phase 1: Factorial + Center Points (DOE-005)

1. **Read** this EXPERIMENT_ORDER_005.md
2. **For each condition** (9 runs: 6 factorial + 3 center points, in randomized order):
   a. Modify `doom-agent-A/AGENT.md` parameters:
      - `memory: {0.3|0.5|0.7}`
      - `strength: {0.3|0.5|0.7}`
   b. Restart `doom-agent-A` container (wait 5s for initialization)
   c. Execute 30 episodes using SEED_SET in order
   d. Record to DuckDB `experiments` table:
      - `experiment_id = "DOE-005"`
      - `condition = "{M_low_S_low|M_low_S_high|...}"`
      - `memory = {0.3|0.5|0.7}`
      - `strength = {0.3|0.5|0.7}`
      - `is_center_point = {false|true}`
      - `seed_set = SEED_SET`
3. **After all 270 episodes complete**:
   - Handoff to research-analyst for ANOVA execution

#### Phase 2: Evolution Test (Generation 1 vs. 2)

1. **Wait for research-analyst** to complete ANOVA and identify best performer
2. **Read** best performer from EXPERIMENT_REPORT_005.md (expected: Memory=0.7, Strength=0.7)
3. **Generate Generation 2 genome**: Memory=0.8, Strength=0.8
4. **Execute Generation 2**:
   a. Modify `doom-agent-A/AGENT.md` parameters:
      - `memory: 0.8`
      - `strength: 0.8`
   b. Restart container
   c. Execute 30 episodes using SEED_SET (SAME seeds as DOE-005)
   d. Record to DuckDB `experiments` table:
      - `experiment_id = "DOE-005-EVOL"`
      - `condition = "Gen2_evolved"`
      - `generation = 2`
      - `parent_genome = "Gen1_best"`
      - `seed_set = SEED_SET`
5. **Handoff to research-analyst** for paired t-test (Gen2 vs. Gen1)

### Agent MD Configuration Examples

**Generation 1 Best** (Memory=0.7, Strength=0.7):
```yaml
strategy_profile:
  memory: 0.7
  strength: 0.7
  play_style: balanced
  weapon_preference: balanced
  retreat_threshold: 0.5
  exploration_tendency: 0.5
```

**Generation 2 Evolved** (Memory=0.8, Strength=0.8):
```yaml
strategy_profile:
  memory: 0.8
  strength: 0.8
  play_style: balanced
  weapon_preference: balanced
  retreat_threshold: 0.5
  exploration_tendency: 0.5
```

---

## Data Recording

### DuckDB Schema

**experiments table** (per-episode):
```sql
experiment_id: VARCHAR  -- "DOE-005" or "DOE-005-EVOL"
condition: VARCHAR  -- "M_low_S_low", "M_high_S_high", "Gen2_evolved", etc.
memory: FLOAT  -- 0.3, 0.5, 0.7, or 0.8
strength: FLOAT  -- 0.3, 0.5, 0.7, or 0.8
is_center_point: BOOLEAN  -- true for center points, false for factorial
generation: INT  -- 1 for DOE-005, 2 for DOE-005-EVOL
parent_genome: VARCHAR  -- NULL for Gen1, "Gen1_best" for Gen2
seed: INT  -- one of SEED_SET
episode_number: INT  -- 1 to 30
total_kills: INT
survival_time: FLOAT
damage_dealt: FLOAT
ammo_used: INT
-- Additional columns as per standard schema
```

---

## Analysis Output

**Target Documents**:
1. `EXPERIMENT_REPORT_005.md` (ANOVA, curvature test, best performer identification)
2. `EVOLUTION_REPORT_001.md` (Generation 1 vs. 2 comparison, paired t-test)

### EXPERIMENT_REPORT_005.md Contents

1. Two-way ANOVA table (Memory, Strength, M×S) with F-statistics and p-values [STAT:f] [STAT:p]
2. Effect sizes (partial η²) per factor and interaction [STAT:eta2]
3. Residual diagnostics results (normality, equal variance, independence)
4. Curvature test results (center point vs. factorial)
5. Simple effects analysis (if interaction significant)
6. Post-hoc pairwise comparisons (Tukey HSD)
7. Interaction plot (Memory × Strength)
8. Main effect plots (Memory, Strength)
9. Best performer identification: Memory=?, Strength=?, mean kill_rate=?
10. Recommendations: Adopt finding? Plan Phase 2 RSM-CCD?

### EVOLUTION_REPORT_001.md Contents

1. Generation 1 best genome specification
2. Generation 2 evolved genome specification
3. Paired t-test results (Gen2 vs. Gen1) [STAT:t-test] [STAT:p]
4. Effect size (Cohen's d) [STAT:effect_size]
5. Mean difference and confidence interval [STAT:ci=95%]
6. Line plot: Gen1 vs. Gen2 kill_rate across 30 episodes
7. Interpretation: Did Gen2 improve on Gen1?
8. Recommendations: Proceed to multi-generation evolution? Adjust mutation strategy?

**Trust Level Criteria**:
- **HIGH**: p < 0.01, effect size η² > 0.06, all diagnostics pass, curvature test clear
- **MEDIUM**: p < 0.05, effect size η² > 0.04, minor diagnostic violations
- **LOW**: p < 0.10 or effect size η² < 0.02
- **UNTRUSTED**: p ≥ 0.10

---

## Phase Transition Criteria

### PROCEED to Phase 2 RSM-CCD (if both conditions met)

**Condition 1: Interaction Significant**
```
Memory × Strength interaction: [STAT:p<0.05] [STAT:eta2>0.06]
```

**Condition 2: Curvature Detected**
```
Center point vs. factorial: [STAT:p<0.05]
```

**If both TRUE**:
- Plan RSM-CCD (Central Composite Design) around optimal region
- Optimal region: (Memory≈0.7, Strength≈0.7) with ±0.2 axial points
- Goal: Find exact optimal Memory-Strength combination

**If both FALSE**:
- Linear additive model sufficient
- No Phase 2 RSM needed
- Proceed to multi-generation evolution experiments

---

## Expected Findings

### Interaction Interpretation

**If Memory × Strength interaction is significant**:

**Simple Effects Prediction**:
- At Strength=0.3 (low): Memory effect is moderate [STAT:f≈3.0] [STAT:p<0.10]
- At Strength=0.7 (high): Memory effect is large [STAT:f≈10.0] [STAT:p<0.001]

**Interpretation**: Memory benefits are amplified at higher Strength levels. High-strength agents gain more from improved memory (can capitalize on learned strategies), while low-strength agents are limited regardless of memory.

**Actionable Insight**: For high-kill playstyles, prioritize both Memory ≥ 0.7 AND Strength ≥ 0.7. For survival playstyles, Strength may be less critical.

### Evolution System Validation

**If Gen2 > Gen1**:
- Evolution operator functional
- Local gradient search works
- Proceed to multi-generation experiments (10+ generations)

**If Gen2 ≤ Gen1**:
- Mutation strategy requires tuning
- May be at local optimum (plateau)
- Consider: Increase perturbation magnitude or add exploration (random genomes)

---

## Timeline

**Estimated Execution Time**:
- Setup: 30 min (agent config template preparation)
- Phase 1 (DOE-005): 4-5 hours (9 runs × 30 episodes × ~60s/episode)
- Analysis (ANOVA, curvature): 2 hours
- Phase 2 (Evolution test): 30 min (1 run × 30 episodes)
- Analysis (paired t-test): 30 min
- Reporting: 1 hour (both reports)

**Total**: ~8-10 hours

---

## Integration with Other Experiments

### Cross-References

- **DOE-003** (Layer Ablation): Must complete and validate Full Stack first
- **DOE-004** (Document Quality): Should complete to ensure RAG is working
- **Evolution Experiments**: This experiment initializes the evolution system

### Dependency Chain

```
DOE-003 → Decision Gate → PROCEED
DOE-004 → HIGH/MEDIUM trust → PROCEED
  ↓
DOE-005 (Memory-Strength Interaction + Evolution Hook) ← You are here
  ↓
If interaction significant + curvature → Phase 2 RSM-CCD
If Gen2 > Gen1 → Multi-generation evolution experiments (10+ generations)
```

---

## Completion Criteria

- [x] Hypothesis H-008 linked to HYPOTHESIS_BACKLOG.md
- [x] 3×2 factorial design with center points specified (9 runs total)
- [x] Seed set generated (n=30, fixed)
- [x] Randomized run order specified
- [x] Response variables defined (primary + secondary + evolution tracking)
- [x] Sample size justified with power analysis [STAT:n=270] [STAT:power≈0.80]
- [x] Statistical analysis plan specified (2-way ANOVA, curvature test, simple effects, post-hoc)
- [x] Evolution hook specified (Gen1 → Gen2 transition, paired t-test)
- [x] Phase transition criteria defined (RSM-CCD if interaction + curvature)
- [x] Execution instructions for research-doe-runner provided
- [x] DuckDB data recording schema specified
- [x] Expected outcomes and predictions documented
- [x] EXPERIMENT_REPORT_005.md and EVOLUTION_REPORT_001.md output specifications provided

---

**Document Status**: READY_FOR_EXECUTION

**Next Steps**:
1. research-doe-runner → Execute DOE-005 Phase 1 (factorial + center points)
2. research-analyst → Perform ANOVA and generate EXPERIMENT_REPORT_005.md
3. research-doe-runner → Execute DOE-005 Phase 2 (Evolution test: Gen2 vs. Gen1)
4. research-analyst → Perform paired t-test and generate EVOLUTION_REPORT_001.md
5. research-pi → Review reports, decide on Phase 2 RSM-CCD and multi-generation evolution
