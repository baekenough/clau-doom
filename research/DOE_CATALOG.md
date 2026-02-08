# clau-doom DOE Design Catalog

> **Project**: clau-doom — LLM Multi-Agent DOOM Research
> **Reference**: 04-DOE.md (DOE Framework), CLAUDE.md (DOE Phase Progression)
> **Last Updated**: 2026-02-08

---

## Phase 0: OFAT (One-Factor-At-A-Time)

### Description

Vary a single factor while holding all others constant. The simplest experimental design, used for initial exploration and variance estimation.

### When to Use

- **Early exploration** (generations 1-2): Estimating individual factor effect sizes and response variance
- **Factor screening**: Quick identification of which parameters matter at all
- **Baseline establishment**: SPC control chart baselines require stable single-factor data
- **Prerequisite information**: Effect size and variance estimates needed to size factorial designs properly

### Design Structure

```
Factor A at k levels: [a_1, a_2, ..., a_k]
All other factors: held at default/center values
n episodes per level
Total episodes: k * n
```

### Pros

- Simple to design and execute
- Easy to interpret (no confounding)
- Minimal computational investment
- Provides variance estimates for power analysis

### Cons

- Cannot detect interaction effects (e.g., Memory x Strength)
- Inefficient: same total episodes in a factorial design would yield more information
- Risk of misleading conclusions if interactions are strong

### Analysis Method

- One-way ANOVA (k levels) or Welch's t-test (2 levels)
- Effect size: Cohen's d (pairwise) or partial eta-squared (ANOVA)
- Post-hoc: Tukey HSD if k > 2

### Planned Usage in clau-doom

| Hypothesis | Factor | Levels | Response | Episodes |
|------------|--------|--------|----------|----------|
| Additional screening | TBD factors (retreat_threshold, exploration_priority, etc.) | 2-3 levels each | kill_rate | 60-90 per factor |

**Note**: H-006 (memory) and H-007 (strength) were originally planned as OFAT, but were combined with H-008 into DOE-002 (2×2 factorial) for efficiency.

### Transition Out

Exit OFAT when >= 3 factors show significant effects (p < 0.05). Use effect size and variance estimates to design Phase 1 factorial experiments.

---

## Phase 1: Full Factorial / Fractional Factorial

### Description

Vary multiple factors simultaneously using a structured design matrix. Full factorial tests all combinations; fractional factorial tests a strategically chosen subset.

### When to Use

- **After Phase 0**: When 3+ factors have significant main effects
- **Interaction detection**: When you suspect factors interact (non-additive effects)
- **Screening 5+ factors**: Fractional factorial (2^(k-p)) reduces runs while preserving main effects

### Design Structures

**Full Factorial (2^k)**:
```
k factors, each at 2 levels (low/high or -/+)
Total runs: 2^k
All main effects + all interactions estimable
Example: 2^3 = 8 runs for 3 factors
```

**Fractional Factorial (2^(k-p))**:
```
k factors, p generators (aliases)
Total runs: 2^(k-p)
Main effects estimable; high-order interactions confounded
Example: 2^(5-2) = 8 runs for 5 factors (Resolution III)
Example: 2^(7-4) = 8 runs for 7 factors (Resolution III)
```

**Design with Center Points**:
```
Add 3-5 center points to factorial design
Purpose: Test for curvature (linear vs. quadratic effects)
If center points differ significantly from factorial mean -> proceed to RSM
```

### Pros

- Detects interaction effects (factorial's key advantage over OFAT)
- Statistically efficient: more information per episode than OFAT
- Orthogonal design: factor effects cleanly separated
- Center points test for curvature

### Cons

- Full factorial: runs grow exponentially with factors (2^k)
- Fractional factorial: some effects confounded (aliased)
- Requires careful level selection (too narrow -> miss optimum, too wide -> miss curvature)
- Assumes linear effects within the design region (unless center points added)

### Analysis Method

- k-way ANOVA (full factorial) or alias-aware ANOVA (fractional)
- Main effect plots + interaction plots
- Effect size: partial eta-squared per factor and interaction
- Diagnostics: normality, equal variance, independence (standard triplet)
- Planned contrasts: Helmert (compare each condition vs. average of remaining)

### Planned Usage in clau-doom

| Hypothesis | Design | Factors | Runs | Episodes/Run | Total |
|------------|--------|---------|------|-------------|-------|
| H-005 (Layer Removal) | 2^3 full factorial | L0, L1, L2 (ON/OFF) | 8 | 30 | 240 (DOE-003) |
| H-008 (Memory x Strength, confirmatory) | 3x2 full factorial + 3 CPs | memory (3 lvl), strength (2 lvl) | 9 | 30 | 270 (DOE-005) |
| Factor screening (5+ factors) | 2^(k-2) fractional | TBD from Phase 0 | 8-16 | 30 | 240-480 |

### Transition Out

Exit factorial when:
- Significant interactions confirmed (need RSM for continuous optimization)
- Curvature detected at center points (need 2nd-order model)
- Optimal region identified but need finer resolution

---

## Phase 2: RSM — Central Composite Design (CCD) / Box-Behnken Design (BBD)

### Description

Response Surface Methodology fits a second-order polynomial model to find the optimal combination of continuous factors. CCD and BBD are the two standard designs.

### When to Use

- **After Phase 1**: When significant factors and interactions are confirmed
- **Continuous optimization**: Finding the exact optimal parameter values (not just "high" vs. "low")
- **Curvature present**: When center point analysis in Phase 1 detected non-linear effects

### Design Structures

**Central Composite Design (CCD)**:
```
For k factors:
  Factorial points: 2^k (corner points)
  Axial points: 2k (star points at distance alpha from center)
  Center points: 3-5 (replication at center)

  alpha values:
    Rotatable: alpha = (2^k)^(1/4)
    Face-centered: alpha = 1.0

  Total runs (k=2): 4 + 4 + 3 = 11
  Total runs (k=3): 8 + 6 + 3 = 17
```

**Box-Behnken Design (BBD)**:
```
For k factors (k >= 3):
  No corner points (factors never at extreme levels simultaneously)
  Center points: 3-5

  Total runs (k=3): 12 + 3 = 15
  Total runs (k=4): 24 + 3 = 27
```

**Model**:
```
y = beta_0 + sum(beta_i * x_i) + sum(beta_ii * x_i^2) + sum(beta_ij * x_i * x_j) + epsilon

For k=2:
  y = beta_0 + beta_1*x_1 + beta_2*x_2 + beta_12*x_1*x_2 + beta_11*x_1^2 + beta_22*x_2^2
```

### Pros

- Finds optimal parameter values in continuous space
- Models curvature (quadratic terms)
- Efficient: fewer runs than testing many discrete levels
- CCD is rotatable (equal prediction variance at equal distances from center)

### Cons

- Only 2-3 factors practical (runs grow quickly)
- Requires good center point (should be near optimum from Phase 1)
- Assumes quadratic model is adequate (may miss higher-order effects)
- Sensitive to outliers (small n per point)

### Analysis Method

- Multiple regression (2nd-order polynomial)
- Stationary point analysis: partial derivatives = 0
- Canonical analysis: eigenvalues determine surface shape (maximum, minimum, saddle point)
- Ridge analysis if saddle point detected
- Contour plots and surface plots for visualization
- Lack-of-fit test (compare model to pure error from center points)
- R-squared, adjusted R-squared, predicted R-squared

### Planned Usage in clau-doom

| Scenario | Design | Factors | Runs | Purpose |
|----------|--------|---------|------|---------|
| Memory-Strength optimization | CCD (k=2) | memory, strength | 11-13 | Find optimal (memory, strength) combination |
| Multi-factor optimization | CCD (k=3) or BBD (k=3) | Top 3 from Phase 1 | 15-17 | Find optimal 3-factor combination |
| Scoring weight optimization | Simplex design | w_sim, w_conf (w_rec = 1-w_sim-w_conf) | 8+ | Optimal scoring weights from S2-02 Ablation 2 extended analysis |

### Transition Out

Exit RSM when:
- Optimal region confirmed by confirmation runs
- Need robustness validation (noise factors)
- Optimal point is at design boundary (expand region and re-run)

---

## Phase 3: Split-Plot / Taguchi / Sequential Designs

### Description

Advanced designs for complex constraints. Split-plot handles hard-to-change factors. Taguchi designs for robustness against noise. Sequential/adaptive designs use Bayesian optimization for high-dimensional spaces.

### When to Use

- **Split-plot**: When some factors require agent restart (hard-to-change) while others are MD parameter edits (easy-to-change)
- **Taguchi**: When robustness to map/enemy variation matters more than mean performance
- **Sequential**: When parameter space is too large for RSM (> 4 factors in continuous space)

### Split-Plot Design

```
Whole-plot factors (hard-to-change):
  - Map seed / map type
  - Agent architecture variant
  - OpenSearch index configuration

Sub-plot factors (easy-to-change):
  - retreat_threshold
  - ammo_conservation
  - exploration_priority
  - weapon_preference

Analysis: REML (Restricted Maximum Likelihood)
  - Whole-plot error term separate from sub-plot error
  - F-tests use appropriate error terms
```

### Taguchi Robust Design

```
Control factors (inner array): Agent strategy parameters
Noise factors (outer array): Map difficulty, enemy density, spawn randomness

Signal-to-Noise ratios:
  Larger-is-better (kill_rate): SN = -10 * log10(mean(1/y^2))
  Smaller-is-better (damage_taken): SN = -10 * log10(mean(y^2))
  Nominal-is-best (ammo_efficiency): SN = 10 * log10(mean^2/variance)

Design: L9 inner x L4 outer = 36 runs
Parent selection: SN-ratio based (instead of mean performance)
```

### Sequential / Bayesian Optimization

```
1. Initial DOE (Latin Hypercube Sampling or orthogonal array)
2. Fit Gaussian Process surrogate model
3. Select next evaluation point via Expected Improvement
4. Iterate until convergence

Advantage: Efficient in high-dimensional continuous spaces (> 4 factors)
Application: Fine-tuning after RSM identifies approximate optimal region
```

### Planned Usage in clau-doom

| Design | When | Purpose |
|--------|------|---------|
| Split-plot | Generation 6+, multiple map types | Optimize agent params across map variations efficiently |
| Taguchi L9 x L4 | Generation 8+, stability focus | Find strategies robust to map/enemy variation |
| Bayesian optimization | Generation 10+, 5+ continuous factors | Fine-tune agent in high-dimensional parameter space |

### Pros

- Split-plot: Reduces agent restarts (saves execution time)
- Taguchi: Explicitly optimizes for robustness (Cpk improvement)
- Sequential: Efficient for high-dimensional spaces

### Cons

- Split-plot: Complex analysis (REML), easy to use wrong error terms
- Taguchi: Assumes control-noise interaction structure; may miss control-control interactions
- Sequential: Requires GP fitting infrastructure; longer per-iteration computation

---

## Design Selection Guide

```
Decision Tree:

How many factors are you testing?
  |
  +-- 1 factor -> OFAT (Phase 0)
  |
  +-- 2-4 factors
  |     |
  |     +-- First time testing? -> Full Factorial (Phase 1)
  |     |
  |     +-- Interactions confirmed? -> RSM-CCD (Phase 2)
  |     |
  |     +-- Need robustness? -> Taguchi (Phase 3)
  |
  +-- 5-8 factors
  |     |
  |     +-- Screening -> Fractional Factorial 2^(k-p) (Phase 1)
  |     |
  |     +-- After screening -> RSM on top 2-3 factors (Phase 2)
  |
  +-- 8+ factors
  |     |
  |     +-- Screening -> Taguchi L18 or Plackett-Burman (Phase 1)
  |     |
  |     +-- Optimization -> Bayesian/Sequential (Phase 3)
  |
  +-- Hard-to-change factors present? -> Split-Plot (Phase 3)
```

---

## Hypothesis-to-Design Mapping

| Hypothesis | Phase | Design Type | Experiment | Factors | Estimated Episodes |
|------------|-------|-------------|------------|---------|-------------------|
| H-001 | 0 | Baseline comparison (Welch's t) | DOE-001 | Full Agent vs Random | 210 (3 x 70, shared) |
| H-002 | 0 | Baseline comparison (Welch's t) | DOE-001 | Full Agent vs Rule-Only | (shared with H-001) |
| H-003 | 0 | One-way ANOVA | DOE-004 | Doc quality (3 levels) | 3 x 50 = 150 |
| H-004 | 0 | One-way ANOVA + regression | TBD | Scoring weights (4-8 levels) | 4 x 40 = 160 (primary) |
| H-005 | 0/1 | 2^3 full factorial | DOE-003 | L0, L1, L2 (ON/OFF) | 8 x 30 = 240 |
| H-006 | 0/1 | 2×2 factorial (main effect) | DOE-002 | Memory (0.3, 0.7) | 150 (shared with H-007, H-008) |
| H-007 | 0/1 | 2×2 factorial (main effect) | DOE-002 | Strength (0.3, 0.7) | (shared with H-006, H-008) |
| H-008 | 0/1 | 2x2 factorial (exploratory) + 3x2 factorial (confirmatory) | DOE-002 + DOE-005 | Memory x Strength | DOE-002: shared; DOE-005: 270 |
| H-009 | 1 | 2x2 factorial + center points | DOE-005 | Memory [0.7,0.9] x Strength [0.7,0.9] | 150 (COMPLETE, REJECTED) |
| H-010 | 1 | 2x2 factorial + center points (re-validation) | DOE-006 | Memory [0.3,0.7] x Strength [0.3,0.7] | 150 (COMPLETE, ALL NON-SIGNIFICANT) |
| H-011 | 0/1 | One-way ANOVA (5 levels) | DOE-007 | action_strategy (random, L0_only, L0_memory, L0_strength, full_agent) | 150 (ORDERED) |
| TBD | 2 | RSM-CCD | TBD | Top factors from Phase 0/1 | 11-17 runs x 30 = 330-510 |
| TBD | 3 | Taguchi L9 x L4 | TBD | Control x Noise factors | 36 x 30 = 1080 |

---

## Episode Budget Summary

| Phase | Hypotheses | Experiment | Estimated Total Episodes | Cumulative |
|-------|-----------|------------|-------------------------|------------|
| 0 — Baselines | H-001, H-002 | DOE-001 | 210 (3 conditions x 70 episodes) | 210 |
| 0 — Layer Ablation | H-005 | DOE-003 | 240 (8 conditions x 30 episodes) | 450 |
| 0/1 — Combined Factorial | H-006, H-007, H-008 | DOE-002 | 150 (4 cells x 30 + 3 CPs x 10) | 600 |
| 0 — Doc Quality Ablation | H-003 | DOE-004 | 150 (3 conditions x 50 episodes) | 750 |
| 1 — Expanded Range | H-009 | DOE-005 | 150 (4 cells x 30 + 3 CPs x 10) | 1050 |
| 1 — Wide Range Re-validation | H-010 | DOE-006 | 150 (4 cells x 30 + 3 CPs x 10) | 1200 |
| 0/1 — Layer Ablation | H-011 | DOE-007 | 150 (5 levels x 30 episodes) | 1350 |
| 2 — RSM | TBD | TBD | 330-510 | 1530-1710 |
| 3 — Robust/Sequential | TBD | TBD | 1080+ | 2460-2640+ |

**Notes**:
- DOE-001 tests H-001 and H-002 simultaneously with shared seed set (70 seeds, 3 conditions).
- DOE-002 combines H-006, H-007, H-008 into a single factorial, saving ~210 episodes vs separate OFAT + factorial (150 vs 90+90+180=360).
- DOE-003 gates DOE-004 and DOE-005 via Decision Gate (Full Stack vs L0 Only).
- DOE-005 provides confirmatory test for H-008 (DOE-002 is exploratory). If results conflict, DOE-005 takes precedence.
- Total Phase 0/1 budget: **1050 episodes** across 5 experiments (DOE-001 through DOE-005).
- Episode reuse between S2-01 Baseline 2 (Rule-Only) and S2-02 Ablation 3 (L0 Only) saves ~70 episodes.
- Shared seed sets enable cross-experiment comparisons.
