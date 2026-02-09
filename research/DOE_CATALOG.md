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
| H-011 | 0/1 | One-way ANOVA (5 levels) | DOE-007 | action_strategy on defend_the_center (5 levels) | 150 (COMPLETE, p=0.183 NS, Scenario D) |
| H-012 | 0/1 | One-way ANOVA (5 levels, scenario replication) | DOE-008 | action_strategy on defend_the_line (5 levels) | 150 (ORDERED) |
| H-013 | 1 | 3×3 factorial (memory × strength) | DOE-009 | memory_weight × strength_weight on defend_the_line | 270 (ORDERED) |
| H-014 | 1 | One-way CRD (5 levels) | DOE-010 | action_strategy structured patterns on defend_the_line | 150 (5 × 30) |
| H-015 | 1 | One-way CRD (5 levels, cross-space) | DOE-011 | 3-action vs 5-action space, strafing vs turning on defend_the_line | 150 (5 × 30) |
| H-016 | 1 | One-way CRD (5 levels) | DOE-012 | Compound simultaneous actions vs sequential on defend_the_line | 150 (5 × 30) |
| H-017 | 1 | One-way CRD (5 levels) | DOE-013 | Attack ratio 50-100% effect on kill_rate | 150 (5 × 30) |
| H-018 | 1 | One-way CRD (5 levels) | DOE-014 | L0 health threshold modulation | 150 (5 × 30) |
| H-019 | 1 | One-way CRD (5 levels) | DOE-015 | Strategy generalization to basic.cfg | 150 (5 × 30) |
| H-020 | 1 | One-way CRD (5 levels) | DOE-016 | Simple agents on deadly_corridor | 150 (5 × 30) |
| H-021 | 1 | One-way CRD (5 levels) | DOE-017 | Attack_only deficit replication | 150 (5 × 30) |
| H-022 | 1 | One-way CRD (5 levels) | DOE-018 | Adaptive vs fixed strategies | 150 (5 × 30) |
| H-023 | 1 | One-way CRD (5 levels) | DOE-019 | Cross-validation of top strategies | 150 (5 × 30) |
| H-024 | 1 | One-way CRD (5 levels) | DOE-020 | Best-of-breed comparison | 150 (5 × 30) |
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
| 1 — Scenario Replication | H-012 | DOE-008 | 150 (5 levels x 30 episodes) | 1500 |
| 1 — Memory × Strength Factorial | H-013 | DOE-009 | 270 (9 cells x 30 episodes) | 1770 |
| 1 — Structured Movement | H-014 | DOE-010 | 150 (5 levels x 30 episodes) | 1920 |
| 1 — Action Space Expansion | H-015 | DOE-011 | 150 (5 levels x 30 episodes) | 2070 |
| 1 — Compound Actions | H-016 | DOE-012 | 150 (5 levels x 30 episodes) | 2220 |
| 1 — Attack Ratio | H-017 | DOE-013 | 150 (5 levels x 30 episodes) | 2370 |
| 1 — Health Threshold | H-018 | DOE-014 | 150 (5 levels x 30 episodes) | 2520 |
| 1 — Scenario Generalization | H-019 | DOE-015 | 150 (5 levels x 30 episodes) | 2670 |
| 1 — Deadly_Corridor Test | H-020 | DOE-016 | 150 (5 levels x 30 episodes) | 2820 |
| 1 — Replication | H-021 | DOE-017 | 150 (5 levels x 30 episodes) | 2970 |
| 1 — Adaptive Strategies | H-022 | DOE-018 | 150 (5 levels x 30 episodes) | 3120 |
| 1 — Cross-Validation | H-023 | DOE-019 | 150 (5 levels x 30 episodes) | 3270 |
| 1 — Best-of-Breed | H-024 | DOE-020 | 150 (5 levels x 30 episodes) | 3420 |
| 1 — 5-Action Strategy Optimization | H-028 | DOE-025 | 180 (6 conditions x 30 episodes) | 3600 |
| 1 — L2 RAG 5-Action | H-029 | DOE-026 | 150 (5 conditions x 30 episodes) | 3750 |
| 1 — Attack Ratio Gradient | H-030 | DOE-027 | 210 (7 levels x 30 episodes) | 3960 |
| 1 — Temporal Attack Pattern | H-031 | DOE-028 | 150 (5 levels x 30 episodes) | 4110 |
| 1 — Emergency Health Override | H-032 | DOE-029 | 120 (4 cells x 30 episodes) | 5010 |
| 2 — RSM | TBD | TBD | 330-510 | 5340-5520 |
| 3 — Robust/Sequential | TBD | TBD | 1080+ | 5190-5550+ |

---

## Catalog Entries

| ID | Design Type | Scenario | Conditions | Episodes | Key Finding | Status |
|----|-------------|----------|------------|----------|-------------|--------|
| DOE-001 | OFAT | defend_the_center | 3 (random, rule_only, full_agent) | 210 | Full vs Random confirmed (d=6.84), Full = Rule-Only (mock data artifact) | COMPLETE |
| DOE-002 | 2x2 Factorial + CP | defend_the_center | 4 cells + 3 CP | 150 | INVALIDATED (AMMO2 bug, mock data) | INVALID |
| DOE-005 | 2x2 Factorial + CP | defend_the_center | 4 cells + 3 CP | 150 | Performance plateau at [0.7, 0.9], all p>0.10 | COMPLETE |
| DOE-006 | 2x2 Factorial + CP | defend_the_center | 4 cells + 3 CP | 150 | Re-validation FAILED, all p>0.10 | COMPLETE |
| DOE-007 | One-way CRD | defend_the_center | 5 (architecture levels) | 150 | Scenario D: no discrimination (p=0.183) | COMPLETE |
| DOE-008 | One-way CRD | defend_the_line | 5 (architecture levels) | 150 | L0_only worst (p<0.001), lateral movement essential | COMPLETE |
| DOE-009 | 3x3 Factorial | defend_the_line | 9 cells | 270 | Memory/Strength NULL (all p>0.10) | COMPLETE |
| DOE-010 | One-way CRD | defend_the_line | 5 (structured patterns) | 150 | Random ≈ structured, burst > sweep (p<0.001) | COMPLETE |
| DOE-011 | One-way CRD | defend_the_line (3/5 action) | 5 (action space) | 150 | 3-action > 5-action, strafing hurts kill_rate, boosts survival | COMPLETE |
| DOE-012 | One-way CRD | defend_the_line | 5 (compound vs sequential) | 150 | Compound actions WORSE than burst_3 (p<0.000001) | COMPLETE |
| DOE-013 | One-way CRD | defend_the_line | 5 (attack ratio 50-100%) | 150 | Attack ratio does NOT affect kill_rate (p=0.812) | COMPLETE |
| DOE-014 | One-way CRD | defend_the_line | 5 (L0 health threshold 0-100) | 150 | Monotonic gradient: threshold_0 best (46.3 kr, p=0.005) | COMPLETE |
| DOE-015 | One-way CRD | basic.cfg | 5 (strategy generalization) | 150 | Floor effect: basic.cfg unsuitable (eta2=0.828 difference) | COMPLETE |
| DOE-016 | One-way CRD | deadly_corridor | 5 (survival test) | 150 | Complete floor effect: all ≈0 kills (p=0.596) | COMPLETE |
| DOE-017 | One-way CRD | defend_the_line | 5 (replication) | 150 | attack_only deficit REPLICATES (p=0.001, d=0.66) | COMPLETE |
| DOE-018 | One-way CRD | defend_the_line | 5 (adaptive strategies) | 150 | adaptive_kill achieves highest kill_rate (46.18 kr, p<0.000002) | COMPLETE |
| DOE-019 | One-way CRD | defend_the_line | 5 (cross-validation) | 150 | L0_only worst across 3 experiments (3x replicated) | COMPLETE |
| DOE-020 | One-way CRD | defend_the_line | 5 (best-of-breed) | 150 | burst_3 highest kills (15.40), compound ≈ attack_only (no advantage) | COMPLETE |
| DOE-021 | One-way CRD | defend_the_line | 10 (evolution genomes) | 300 | Generational evolution Gen 1 with TOPSIS fitness | DESIGNED |
| DOE-022 | One-way CRD | defend_the_line | 4 (L0/L1/L2 layers) | 120 | L2 RAG pipeline activation: L0_only, L0_L1, L0_L1_L2_good, L0_L1_L2_random | DESIGNED |
| DOE-023 | 3x4 Factorial | defend_the_line (doom_skill) | 12 (3 skills x 4 strategies) | 360 | Cross-difficulty strategy robustness: doom_skill {1,3,5} x strategy {burst_3, random, adaptive_kill, L0_only} | COMPLETE |
| DOE-024 | 4×3 Full Factorial | defend_the_line (doom_skill) | 12 (4 modes x 3 skills) | 360 | H-027 REJECTED: L2 meta-strategy no main effect (p=0.39), F-057~F-061 | COMPLETE |
| DOE-025 | One-way ANOVA | defend_the_line_5action.cfg | 6 (strategy types) | 180 | H-028 PARTIALLY SUPPORTED: kills F(5,174)=4.057 p=0.0017 η²=0.104, survival F(5,174)=4.350 p=0.0009 η²=0.111, F-062~F-066 | COMPLETE |
| DOE-026 | One-way (5 groups) | L2 RAG strategy selection in 5-action space | 5 conditions × 30 = 150 | H-029 REJECTED | F-067~F-070 |
| DOE-027 | One-way (7 levels) | defend_the_line_5action | attack_ratio (0.2-0.8) | 210 | H-030 REJECTED: kills invariant to attack ratio (p=0.717), rate-time compensation, F-071~F-075 | COMPLETE |
| DOE-028 | OFAT (5 levels) | defend_the_line_5action | burst_pattern (random_50, cycle_2, cycle_3, cycle_5, cycle_10) | 150 | H-031 REJECTED: temporal grouping null (kills p=0.401, survival p=0.169, kill_rate p=0.374), F-076~F-078 | COMPLETE |
| DOE-029 | 2² Factorial | defend_the_line_5action | action_pattern (2 levels) × health_override (2 levels) | 120 | H-032 PARTIALLY SUPPORTED: Pattern SIGNIFICANT (p<0.001, d=1.408), Override NULL (p=0.378), F-079~F-083 | COMPLETE |

---

**Notes**:
- DOE-001 tests H-001 and H-002 simultaneously with shared seed set (70 seeds, 3 conditions).
- DOE-002 combines H-006, H-007, H-008 into a single factorial, saving ~210 episodes vs separate OFAT + factorial (150 vs 90+90+180=360).
- DOE-003 gates DOE-004 and DOE-005 via Decision Gate (Full Stack vs L0 Only).
- DOE-005 provides confirmatory test for H-008 (DOE-002 is exploratory). If results conflict, DOE-005 takes precedence.
- Total Phase 0/1 budget: **3600 episodes** across 21 experiments (DOE-001 through DOE-020, DOE-025).
- Episode reuse between S2-01 Baseline 2 (Rule-Only) and S2-02 Ablation 3 (L0 Only) saves ~70 episodes.
- Shared seed sets enable cross-experiment comparisons.
- DOE-021 tests H-025 (evolution discovers superior strategies) using 8-parameter genome with TOPSIS-based fitness. Seeds: 23001 + i*91.
- DOE-022 tests H-005 (strategy document quality) via L2 RAG pipeline. First empirical test of OpenSearch kNN retrieval. Seeds: 24001 + i*97.
- DOE-023 tests H-026 (strategy generalization) across 3 doom_skill levels {1=Easy, 3=Normal, 5=Nightmare}. Full factorial design (revised from original split-plot WAD variant plan — WAD editing infeasible). Seeds: 25001 + i*101. Result: doom_skill dominant (η²=0.720), significant interaction (p=6e-4), H-026 PARTIALLY SUPPORTED.
- Total Phase 2 planned budget: **780 episodes** across 3 experiments (DOE-021 through DOE-023).
- DOE-025 tests H-028 (5-action strategy space creates separable tiers) with 6 conditions: random_5, strafe_burst_3, smart_5, adaptive_5, dodge_burst_3, survival_burst. Seeds: 45001 + i×107. Result: H-028 PARTIALLY SUPPORTED. Strategy separation confirmed (kills p=0.0017, survival p=0.0009), but survival_burst (defensive, 40% attack) is paradoxically optimal (F-064).
- DOE-026 tests H-029 (L2 RAG has value in 5-action space where strategies differentiate). One-way ANOVA with 5 conditions: survival_burst, random_5, dodge_burst_3, l2_meta_5action, random_rotation_5. Seeds: 50001 + i×109. Result: H-029 REJECTED. L2 RAG produces completely null effect (kills p=0.935, survival p=0.772). F-067 (L2 RAG no effect), F-068 (pre-filtered pool), F-069 (RAG overhead), F-070 (core thesis falsified).
- DOE-027 tests H-030 (non-monotonic attack ratio relationship). One-way ANOVA with 7 levels: attack_ratio (0.2-0.8). Seeds: 47001 + i×127. Result: H-030 REJECTED. Kills invariant to attack ratio (p=0.717) due to rate-time compensation (F-074). F-071~F-075 adopted.
- DOE-028 tests H-031 (temporal attack grouping affects kills). OFAT with 5 levels: burst_pattern (random_50, cycle_2, cycle_3, cycle_5, cycle_10). Seeds: 48001 + i×131. Result: H-031 REJECTED. Temporal grouping has no effect (kills p=0.401, survival p=0.169). F-076~F-078 adopted.
- DOE-029 tests H-032 (emergency health override improves performance). 2×2 factorial: action_pattern (random_50 vs pure_attack) × health_override (enabled vs disabled). Seeds: 49001 + i×137. Result: H-032 PARTIALLY SUPPORTED. Pattern MASSIVE effect (p<0.001, d=1.408), override NULL (p=0.378). F-079~F-083 adopted.
- Cumulative budget (all phases): **5010 episodes** (4110 prior + 900 DOE-027~029).
