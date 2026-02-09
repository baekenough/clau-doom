# EXPERIMENT_ORDER_021: Generational Evolution — Gen 1

## Metadata
- **Experiment ID**: DOE-021
- **Hypothesis**: H-025 — Generational evolution discovers strategies superior to DOE-020 best-of-breed
- **DOE Phase**: Phase 2 (Optimization via evolutionary search)
- **Design Type**: Generational genetic algorithm with TOPSIS multi-objective fitness
- **Date Ordered**: 2026-02-09

## Research Question

Can a genetic algorithm, seeded with the best strategies from DOE-008 through DOE-020, evolve action strategies that exceed the Pareto front defined by burst_3 (kills champion, C_i=0.977) and adaptive_kill (efficiency champion, C_i=0.486)?

### Background

The DOE-008 through DOE-020 experimental campaign established:

1. **burst_3** is the kills champion (15.40 kills, 5 independent replications, CV=5.8%) and multi-objective optimal (TOPSIS C_i=0.977 with equal weights on kills, kill_rate, survival_time).
2. **adaptive_kill** is the efficiency champion (45.97 kr, 3 independent replications, CV=0.6%) but trades kills for efficiency.
3. **random** is near-optimal in the 3-action space (42.40 kr, within d=0.38 of top tier).
4. **Structured strategies do not outperform random** (F-018, HIGH trust, DOE-010).
5. **The action space is the bottleneck** (F-020, F-022): with 3 actions, random selection already achieves near-optimal lateral scanning.

The key insight from Phase 1 is that burst_3's advantage comes from sustained directional commitment (3 attacks in a row before turning), not from intelligent decision-making. This suggests the strategy parameter space contains local optima that can be explored more efficiently via evolutionary search than manual DOE.

### Hypothesis

**H-025: Generational Evolution Discovers Superior Strategies**

A genetic algorithm starting from burst_3 and adaptive_kill parents will evolve genomes that:
1. Match or exceed burst_3's kills (15.40) within 3 generations
2. Discover burst_length or turn_count configurations not tested in Phase 1
3. Identify whether adaptive switching improves upon pure burst patterns when co-optimized
4. Converge within 5 generations (or identify that burst_3 is already globally optimal)

## Genome Representation

Each genome encodes an action strategy as a set of tunable parameters:

```
Genome = {
  burst_length:            int   [1..7]       # Number of ATTACK actions per burst
  turn_direction:          enum  [random, alternate, sweep_left, sweep_right]
  turn_count:              int   [1..3]       # Number of TURN actions between bursts
  health_threshold_high:   int   [0..100]     # Above this: defensive mode (more turning)
  health_threshold_low:    int   [0..100]     # Below this: aggressive mode (more attacking)
  stagnation_window:       int   [0..10]      # Ticks without kill → force strategy change
  attack_probability:      float [0.5..1.0]   # Base probability of ATTACK vs TURN
  adaptive_enabled:        bool               # Use state-dependent switching
}
```

### Parameter Interpretation

| Parameter | Role | Interaction |
|-----------|------|-------------|
| **burst_length** | Core offensive output. burst_3's value = 3. Higher = more sustained fire, less scanning. | Primary knob for kills vs kill_rate tradeoff |
| **turn_direction** | How the agent reorients between bursts. `random` = DOE-010's near-optimal lateral movement. | Interacts with turn_count: more turns × directional commitment = more scanning |
| **turn_count** | Number of consecutive turns between bursts. burst_3 = 1. Higher = more scanning, less attacking. | Inverse of burst_length in offensive/defensive balance |
| **health_threshold_high** | Triggers defensive behavior (more turning) above this health. Irrelevant if adaptive_enabled=false. | Controls when to switch from offensive to defensive |
| **health_threshold_low** | Triggers aggressive behavior (all attack) below this health. Irrelevant if adaptive_enabled=false. | "Last stand" mode: attack continuously when near death |
| **stagnation_window** | If no kills in N ticks, force a turn to scan for new targets. 0 = disabled. | Prevents tunnel vision on empty sectors |
| **attack_probability** | Base probability of choosing ATTACK on each tick (used as fallback/noise). | Smooths transitions, adds exploration |
| **adaptive_enabled** | Master switch for state-dependent logic (health thresholds + stagnation). | Determines whether genome uses fixed cycle or adaptive switching |

### Genome-to-Strategy Mapping

When `adaptive_enabled = false`:
```
repeat forever:
  for i in 1..burst_length:
    action = ATTACK
  for i in 1..turn_count:
    action = TURN_{turn_direction}
```

When `adaptive_enabled = true`:
```
if health > health_threshold_high:
  # Defensive: more turning for survivability
  action = TURN_{turn_direction} with p = 1 - attack_probability
  action = ATTACK with p = attack_probability
elif health < health_threshold_low:
  # Aggressive: maximum attack
  action = ATTACK
else:
  # Normal: burst cycle
  for i in 1..burst_length:
    action = ATTACK
  for i in 1..turn_count:
    action = TURN_{turn_direction}

if stagnation_window > 0 and ticks_since_last_kill >= stagnation_window:
  action = TURN_{turn_direction}  # Force reorientation
```

## Initial Population (Gen 1): 10 Genomes

### Genome Table

| ID | Name | burst_length | turn_direction | turn_count | health_thresh_high | health_thresh_low | stagnation_window | attack_prob | adaptive | Origin |
|----|------|-------------|----------------|------------|-------------------|------------------|-------------------|-------------|----------|--------|
| G01 | burst_3_base | 3 | random | 1 | 0 | 0 | 0 | 0.75 | false | burst_3 exact |
| G02 | burst_3_sweep | 3 | alternate | 1 | 0 | 0 | 0 | 0.75 | false | burst_3 variant |
| G03 | adaptive_base | 3 | random | 1 | 50 | 25 | 5 | 0.80 | true | adaptive_kill exact |
| G04 | adaptive_tuned | 3 | alternate | 1 | 60 | 20 | 7 | 0.85 | true | adaptive_kill variant |
| G05 | crossover_A | 3 | random | 1 | 50 | 25 | 5 | 0.75 | true | burst_3 × adaptive_kill |
| G06 | crossover_B | 3 | alternate | 2 | 60 | 20 | 0 | 0.80 | false | burst_3 × adaptive_kill |
| G07 | burst_2 | 2 | random | 1 | 0 | 0 | 0 | 0.70 | false | New exploration |
| G08 | burst_5 | 5 | random | 1 | 0 | 0 | 0 | 0.80 | false | New exploration |
| G09 | aggressive | 7 | random | 1 | 0 | 0 | 0 | 0.95 | false | Max attack |
| G10 | random_baseline | 3 | random | 1 | 0 | 0 | 0 | 0.50 | false | Random comparison |

### Genome Design Rationale

**G01 (burst_3_base)**: Exact replication of burst_3 from DOE-012/017/018/019/020. Serves as performance anchor. Expected: ~15.4 kills, ~45.4 kr.

**G02 (burst_3_sweep)**: Identical to G01 except `turn_direction=alternate` (alternates left-right instead of random). Tests whether systematic alternation outperforms random reorientation. DOE-010 F-017 showed pure oscillation (sweep_lr) is equivalent to stasis; this tests single-turn alternation vs single-turn random.

**G03 (adaptive_base)**: Exact replication of adaptive_kill from DOE-018/019/020. Health-dependent switching (defensive above 50hp, aggressive below 25hp, normal burst cycle otherwise). Expected: ~13.0 kills, ~46.0 kr.

**G04 (adaptive_tuned)**: Slightly adjusted adaptive_kill: higher health_threshold_high (60 vs 50), lower health_threshold_low (20 vs 25), longer stagnation_window (7 vs 5), alternating turns, higher attack_probability (0.85 vs 0.80). Tests moderate mutations on adaptive_kill.

**G05 (crossover_A)**: burst_3 structure (burst_length=3, turn_count=1) with adaptive_kill's state-dependent switching enabled (thresholds 50/25, stagnation=5). Tests whether adding adaptive switching to burst_3 improves it. Related to F-011 (full_agent penalty from stacked heuristics).

**G06 (crossover_B)**: burst_3 structure with doubled turn_count (2 instead of 1) and adaptive_kill's turn direction (alternate), but adaptive_enabled=false. Tests whether more scanning between bursts helps.

**G07 (burst_2)**: Shorter bursts (2 attacks per burst). More frequent repositioning. Tests whether faster scanning compensates for fewer attacks per burst.

**G08 (burst_5)**: Longer bursts (5 attacks per burst). Less repositioning. Tests whether sustained fire outperforms burst_3's 3-attack cycle. DOE-010 tested burst_5 and found it statistically equivalent to burst_3 (F-018, d=0.191, NS). This replication uses a different seed set.

**G09 (aggressive)**: Maximum burst (7 attacks per burst), near-maximum attack_probability (0.95). Extreme aggression. Tests upper boundary of attack ratio. Related to H-017 (rejected: attack ratio 50-100% does not affect kill_rate, F-027). This pushes even further.

**G10 (random_baseline)**: Near-random behavior (attack_probability=0.50, effectively 50% attack, 50% random turn). Serves as evolutionary lower bound and calibration against DOE-020's random strategy (42.40 kr).

## Design Matrix

| Run | Genome | Description | Episodes | Seeds |
|-----|--------|-------------|----------|-------|
| R01 | G01 | burst_3_base | 30 | [23001, ..., 25641] |
| R02 | G02 | burst_3_sweep | 30 | [23001, ..., 25641] |
| R03 | G03 | adaptive_base | 30 | [23001, ..., 25641] |
| R04 | G04 | adaptive_tuned | 30 | [23001, ..., 25641] |
| R05 | G05 | crossover_A | 30 | [23001, ..., 25641] |
| R06 | G06 | crossover_B | 30 | [23001, ..., 25641] |
| R07 | G07 | burst_2 | 30 | [23001, ..., 25641] |
| R08 | G08 | burst_5 | 30 | [23001, ..., 25641] |
| R09 | G09 | aggressive | 30 | [23001, ..., 25641] |
| R10 | G10 | random_baseline | 30 | [23001, ..., 25641] |

**Total**: 10 genomes × 30 episodes = 300 episodes

## Randomized Execution Order

R07 (burst_2) → R03 (adaptive_base) → R10 (random_baseline) → R05 (crossover_A) → R01 (burst_3_base) → R09 (aggressive) → R06 (crossover_B) → R02 (burst_3_sweep) → R08 (burst_5) → R04 (adaptive_tuned)

(Randomized via Python `random.sample(range(1,11), 10)` with seed=2109)

## Seed Set

**Formula**: seed_i = 23001 + i × 91, i = 0, 1, ..., 29
**Range**: [23001, 25641]
**Count**: 30 seeds per genome, identical across all 10 genomes

**Full seed set**:
```
[23001, 23092, 23183, 23274, 23365, 23456, 23547, 23638, 23729, 23820,
 23911, 24002, 24093, 24184, 24275, 24366, 24457, 24548, 24639, 24730,
 24821, 24912, 25003, 25094, 25185, 25276, 25367, 25458, 25549, 25641]
```

Note: Last seed is 23001 + 29×91 = 23001 + 2639 = 25640. Correction: 23001 + 29×91 = 25640. Updated: seed_29 = 25640.

**Corrected full seed set**:
```
[23001, 23092, 23183, 23274, 23365, 23456, 23547, 23638, 23729, 23820,
 23911, 24002, 24093, 24184, 24275, 24366, 24457, 24548, 24639, 24730,
 24821, 24912, 25003, 25094, 25185, 25276, 25367, 25458, 25549, 25640]
```

### Cross-Experiment Seed Collision Check

This seed set ([23001, 25640]) is independent from all prior experiments:
- DOE-008: [6001, 7074], increment 37
- DOE-009: [8001, 10342], increment 83
- DOE-010: [10001, 11248], increment 43
- DOE-011: [12001, 13364], increment 47
- DOE-012: [14001, 15364], increment 47
- DOE-013: [15001, 16364], increment 47
- DOE-014: [16001, 17248], increment 43
- DOE-015: [17001, 18364], increment 47
- DOE-016: [18001, 19248], increment 43
- DOE-017: [17001, 18364], increment 47
- DOE-018: [19001, 21284], increment 79
- DOE-019: [20001, 22404], increment 83
- DOE-020: [21001, 23581], increment 89

**Overlap analysis**: DOE-020 ends at 23581. DOE-021 starts at 23001. Potential overlap in [23001, 23581].
- DOE-020 seeds: 21001 + i×89, i=0..29. Seeds in [23001, 23581]: i values where 21001 + i×89 >= 23001 → i >= 22.47 → i = 23..29, seeds = {23048, 23137, 23226, 23315, 23404, 23493, 23581}
- DOE-021 seeds: 23001 + i×91, i=0..29. Seeds in [23001, 23581]: i = 0..6, seeds = {23001, 23092, 23183, 23274, 23365, 23456, 23547}

**Actual collision check** (DOE-020 seeds in overlap range vs DOE-021 seeds in overlap range):
- DOE-020: {23048, 23137, 23226, 23315, 23404, 23493, 23581}
- DOE-021: {23001, 23092, 23183, 23274, 23365, 23456, 23547}

Common elements: None. GCD(89, 91) = 1, so the linear progressions never coincide in this range.

**Verdict**: Zero seed collisions. True independent validation.

## Scenario Configuration

**Scenario**: defend_the_line.cfg (3-action space)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

## Fitness Function: TOPSIS

Multi-objective fitness using TOPSIS (Technique for Order of Preference by Similarity to Ideal Solution).

### Criteria and Weights

| Criterion | Direction | Weight | Justification |
|-----------|-----------|--------|---------------|
| kills (mean per genome) | Maximize | 0.333 | Total lethality |
| kill_rate (mean per genome) | Maximize | 0.333 | Kill efficiency |
| survival_time (mean per genome) | Maximize | 0.333 | Survivability |

### TOPSIS Procedure

1. **Decision matrix** D: 10 genomes × 3 criteria (mean values from 30 episodes each)
2. **Normalize**: r_ij = x_ij / sqrt(sum(x_kj^2) for all k)
3. **Weight**: v_ij = w_j × r_ij
4. **Ideal best**: A+ = {max(v_j) for each criterion j}
5. **Ideal worst**: A- = {min(v_j) for each criterion j}
6. **Distances**: D_i^+ = sqrt(sum((v_ij - A+_j)^2)), D_i^- = sqrt(sum((v_ij - A-_j)^2))
7. **Closeness**: C_i = D_i^- / (D_i^+ + D_i^-)
8. **Rank** by C_i descending (highest = best)

### Reference Point (DOE-020 burst_3)

From DOE-020: burst_3 achieves C_i ≈ 0.977 (kills=15.40, kr=45.44, survival=20.53).
A Gen 1 genome exceeding this C_i would represent evolutionary improvement.

## Selection Mechanism

### Parent Selection
- Rank all 10 genomes by TOPSIS C_i
- **Top 4** genomes become parents for Gen 2
- **Bottom 6** eliminated

### Elitism
- The **best genome** (highest C_i) survives unchanged to Gen 2 (elitism = 1)
- This guarantees monotonic fitness improvement across generations

### Diversity Preservation
- At least **1 random genome** per generation (randomly initialized, ignoring parent genes)
- Maximum **2 children** from same parent pair (prevents inbreeding)

## Crossover Operator

Two-parent uniform crossover:
1. Select 2 parents from Top 4 (without replacement for first pair, with replacement after)
2. For each gene independently: inherit from Parent A with p=0.5, Parent B with p=0.5
3. Constraint: health_threshold_low < health_threshold_high (re-sample if violated)

### Example

```
Parent A (G01): burst_length=3, turn_dir=random,    turn_count=1, ..., adaptive=false
Parent B (G03): burst_length=3, turn_dir=random,    turn_count=1, ..., adaptive=true
Child:          burst_length=3, turn_dir=random,    turn_count=1, ..., adaptive=true  (from B)
                health_thresh_high=50 (from B), stagnation=0 (from A), attack_prob=0.75 (from A)
```

## Mutation Operator

Per-gene mutation probability: **20%** (p_mut = 0.20)

| Gene Type | Mutation Rule | Example |
|-----------|--------------|---------|
| int (bounded) | ±1 step, clamp to [min, max] | burst_length 3 → 2 or 4 |
| float (bounded) | ±0.1, clamp to [min, max] | attack_prob 0.75 → 0.65 or 0.85 |
| bool | flip | adaptive true → false |
| enum | uniform random from allowed values | turn_dir random → alternate |

### Mutation Constraints
- health_threshold_low must remain < health_threshold_high (re-mutate if violated)
- stagnation_window = 0 if adaptive_enabled = false (disabled when no adaptive logic)

## Gen 2 Composition (10 Genomes)

| Slot | Source | Description |
|------|--------|-------------|
| 1 | Elite | Best genome from Gen 1 (unchanged) |
| 2-3 | Crossover + Mutation | Children of Top 2 parents |
| 4-5 | Crossover + Mutation | Children of Top 2 × Top 3-4 parents |
| 6-7 | Crossover + Mutation | Children of various parent pairs |
| 8 | Mutation only | Clone of 2nd-best parent with mutations |
| 9 | Mutation only | Clone of 3rd-best parent with mutations |
| 10 | Random | Freshly randomized genome (diversity) |

**Constraint**: Maximum 2 children from same parent pair.

## Generational Design

| Generation | Genomes | Episodes | Cumulative Episodes | Source |
|------------|---------|----------|---------------------|--------|
| Gen 1 | 10 | 300 | 300 | Initial population (this order) |
| Gen 2 | 10 | 300 | 600 | Selection + crossover + mutation |
| Gen 3 | 10 | 300 | 900 | Selection + crossover + mutation |
| Gen 4 | 10 | 300 | 1200 | Selection + crossover + mutation |
| Gen 5 | 10 | 300 | 1500 | Selection + crossover + mutation |

**Maximum**: 5 generations, 1500 total episodes.

### Convergence Criterion

Evolution terminates early if **best genome unchanged for 2 consecutive generations**:
- "Unchanged" = same genome ID holds rank #1 for 2 generations
- This indicates the population has converged to a local (possibly global) optimum
- Example: If G01 is best in Gen 1 and Gen 2 (same genome, no child surpasses it), evolution terminates after Gen 2

### Seed Sets for Subsequent Generations

Each generation uses a fresh independent seed set:

| Generation | Formula | Range |
|------------|---------|-------|
| Gen 1 | seed_i = 23001 + i×91, i=0..29 | [23001, 25640] |
| Gen 2 | seed_i = 26001 + i×97, i=0..29 | [26001, 28814] |
| Gen 3 | seed_i = 29001 + i×101, i=0..29 | [29001, 31930] |
| Gen 4 | seed_i = 32001 + i×103, i=0..29 | [32001, 34988] |
| Gen 5 | seed_i = 35001 + i×107, i=0..29 | [35001, 38104] |

All increments are prime (91=7×13 — not prime, but coprime with others; 97, 101, 103, 107 are prime). No cross-generation seed collisions (non-overlapping ranges).

## Statistical Analysis Plan

### Per-Generation Analysis

1. **One-way ANOVA** on TOPSIS C_i (10 genomes)
   - Response: TOPSIS closeness coefficient C_i per episode (computed from per-episode kills, kr, survival)
   - Factor: genome (10 levels)
   - alpha = 0.05

2. **One-way ANOVA** on each response individually (kills, kill_rate, survival_time)

3. **Residual diagnostics**: Normality (Shapiro-Wilk), Equal variance (Levene), Independence (run order)

4. **Tukey HSD** pairwise comparisons if ANOVA significant

5. **Effect sizes**: Cohen's d for pairwise, partial eta-squared for ANOVA

### Cross-Generation Analysis

6. **Fitness trend**: Track best/mean/worst TOPSIS C_i per generation
   - Plot convergence curve
   - Test for monotonic improvement (Page's L test or trend regression)

7. **Genetic diversity**: Track unique parameter values per gene across population
   - Shannon entropy per gene per generation
   - Detect premature convergence (entropy → 0)

8. **Parameter convergence**: Track distribution of each gene across generations
   - Identify which parameters are under selection pressure (narrowing distribution)
   - Identify which parameters drift neutrally (stable distribution)

### Final Comparison

9. **Paired comparison**: Gen-final best genome vs DOE-020 burst_3
   - Use DOE-020 seed set [21001, 23581] for direct comparison
   - Welch's t-test on kills, kill_rate, survival_time
   - TOPSIS C_i comparison

10. **Effect size**: Cohen's d for improvement over burst_3
    - If d > 0.5 (medium): evolution found meaningful improvement
    - If d < 0.2 (small): burst_3 was already near-optimal

### Non-Parametric Backup

11. **Kruskal-Wallis** per generation if normality violated
12. **Friedman test** for cross-generation comparisons

### Power Analysis

- Per-generation: k=10 groups, n=30/group, alpha=0.05
  - For medium effect (f=0.25): [STAT:power=0.90]
  - For small effect (f=0.10): [STAT:power=0.24]
- Can detect medium effects within each generation with 90% power

## Expected Outcomes

| Outcome | Interpretation | Next Step |
|---------|---------------|-----------|
| **A: Evolved genome > burst_3 by d>0.5** | Evolution found improvement beyond DOE-020 optimum | Continue evolution or RSM on evolved genome |
| **B: Evolved genome ≈ burst_3 (d<0.2)** | burst_3 is near globally optimal in 3-action space | Explore expanded action spaces (5-action, compound) |
| **C: Adaptive genomes outperform fixed** | State-dependent switching adds value when co-optimized | RSM on adaptive parameters |
| **D: Convergence in Gen 1-2** | Parameter space is small, burst_3 is in the basin of attraction | Evolution unnecessary for this action space |
| **E: burst_length≠3 emerges as optimal** | Phase 1 missed the optimal burst length | Validate with independent seeds |

### Outcome-Specific Actions

**Outcome A** → Design DOE-022 as RSM around evolved genome's parameter region
**Outcome B** → Pivot to action space expansion (5-action evolution, DOE-022)
**Outcome C** → Design DOE-022 as RSM on adaptive parameters (thresholds, stagnation)
**Outcome D** → Conclude optimization, draft publication Section 4 (Results)
**Outcome E** → Replication study with burst_length={E} and independent seeds

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 23001 + i×91, i=0..29 (Gen 1) |
| No seed collisions | YES: verified against DOE-008 through DOE-020 |
| n >= 30 per condition | YES: 30 episodes per genome |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, variance, independence per generation |
| Effect sizes | PLANNED: Cohen's d pairwise, partial eta-squared per ANOVA |
| Seeds identical across conditions | YES: all 10 genomes use same 30 seeds within each generation |
| Cross-generation seed independence | YES: each generation uses distinct seed set |

## Execution Checklist

Before execution, verify:
- [ ] Genome-to-strategy mapping implemented (8 parameters → action function)
- [ ] G01 replicates DOE-020 burst_3 performance (~15.4 kills, ~45.4 kr)
- [ ] G03 replicates DOE-020 adaptive_kill performance (~13.0 kills, ~46.0 kr)
- [ ] G10 replicates DOE-020 random performance (~13.3 kills, ~42.4 kr)
- [ ] TOPSIS fitness computation validated against DOE-020 known values
- [ ] Crossover and mutation operators implemented with constraints
- [ ] Seed sets generated and logged for all 5 generations
- [ ] DuckDB experiment table ready (columns: generation, genome_id, episode, seed, kills, kill_rate, survival_time, all 8 genome parameters)
- [ ] Convergence detection implemented (same best genome for 2 consecutive generations)
- [ ] Per-generation ANOVA script prepared

### Anchor Validation Protocol

Before running full Gen 1, execute a 5-episode pilot on G01, G03, G10 with seeds [23001, 23092, 23183, 23274, 23365]:
- G01 expected: ~15 kills, ~45 kr (matches burst_3)
- G03 expected: ~13 kills, ~46 kr (matches adaptive_kill)
- G10 expected: ~13 kills, ~42 kr (matches random)
- If any anchor deviates by >2 SD from DOE-020 values, STOP and investigate genome mapping

## Status

**ORDERED** — Ready for execution
