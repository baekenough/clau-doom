# Design of Experiments (DOE) Reference Guide

Reference documentation for experimental design methodology in clau-doom.

## Key Resources

- Montgomery, D.C. (2017). *Design and Analysis of Experiments*, 9th Edition. Wiley.
- Box, G.E.P., Hunter, J.S., Hunter, W.G. (2005). *Statistics for Experimenters*, 2nd Edition. Wiley.
- NIST/SEMATECH e-Handbook of Statistical Methods: https://www.itl.nist.gov/div898/handbook/

## clau-doom Context

DOE systematically varies agent strategy parameters to identify which factors significantly affect performance. Instead of ad-hoc tuning, clau-doom uses industrial DOE methodology to maximize information per experiment run.

Key factors (typical):
- `retreat_threshold` (continuous: 0.20 - 0.50)
- `ammo_conservation` (categorical: low / medium / high)
- `exploration_priority` (categorical: low / medium / high)
- `aggression_level` (continuous: 0.1 - 0.9)
- `weapon_preference` (categorical: shotgun / chaingun / balanced)
- `enemy_priority_method` (categorical: nearest / weakest / strongest)

Response variables:
- Primary: `kill_rate` (kills per episode)
- Secondary: `survival_time`, `damage_taken`, `ammo_efficiency`

## Full Factorial Design (2^k)

All combinations of k factors at 2 levels. Estimates all main effects and interactions without confounding.

### Design Matrix: 2^3 Example

Three factors (retreat_threshold, ammo_conservation, exploration_priority), each at 2 levels (- / +).

```
Run | A (retreat) | B (ammo) | C (explore) | AB  | AC  | BC  | ABC
----|-------------|----------|-------------|-----|-----|-----|----
1   | -1          | -1       | -1          | +1  | +1  | +1  | -1
2   | +1          | -1       | -1          | -1  | -1  | +1  | +1
3   | -1          | +1       | -1          | -1  | +1  | -1  | +1
4   | +1          | +1       | -1          | +1  | -1  | -1  | -1
5   | -1          | -1       | +1          | +1  | -1  | -1  | +1
6   | +1          | -1       | +1          | -1  | +1  | -1  | -1
7   | -1          | +1       | +1          | -1  | -1  | +1  | -1
8   | +1          | +1       | +1          | +1  | +1  | +1  | +1
```

Total runs: 2^3 = 8 (plus center points and replicates).

### Effect Calculation

Effect of factor A = (average response at A+) - (average response at A-)

```
Effect_A = (1/4)(y2 + y4 + y6 + y8) - (1/4)(y1 + y3 + y5 + y7)
```

Interaction effect AB:
```
Effect_AB = (1/4)(y1 + y4 + y5 + y8) - (1/4)(y2 + y3 + y6 + y7)
```

### clau-doom 2^3 Example

```
Factor   | Low (-)  | High (+) | Coded
---------|----------|----------|------
A: retreat_threshold    | 0.30     | 0.45     | x_A = (retreat - 0.375) / 0.075
B: ammo_conservation    | low      | high     | x_B = {low: -1, high: +1}
C: exploration_priority | low      | high     | x_C = {low: -1, high: +1}

Response: kill_rate (averaged over 30 episodes per run)
```

## Fractional Factorial Design (2^(k-p))

When k is large, run only a fraction of the full factorial. Trade higher-order interaction information for fewer runs.

### Resolution

| Resolution | Confounding | Use When |
|------------|-------------|----------|
| III | Main effects aliased with 2-factor interactions | Screening many factors |
| IV | Main effects clear; 2FI aliased with other 2FI | Moderate number of factors |
| V | Main effects and 2FI clear; 2FI aliased with 3FI | Need clean 2FI estimates |

### Generators and Alias Structure

Example: 2^(5-2) Resolution III (5 factors in 8 runs)

```
Base design: A, B, C (full 2^3)
Generators: D = AB, E = AC

Defining relation: I = ABD = ACE = BCDE

Alias structure:
  A = BD = CE
  B = AD = CDE
  C = AE = BDE
  D = AB = BCE
  E = AC = BCD
  BC = DE = ABE = ACD
```

Main effects are aliased with 2-factor interactions. Use for initial screening (Phase 1) to identify the 2-3 most important factors.

### clau-doom 2^(5-2) Screening Example

```
Factors: A=retreat, B=ammo, C=explore, D=weapon_switch (=AB), E=enemy_priority (=AC)

Run | A  | B  | C  | D(=AB) | E(=AC) | Agent
----|----|----|----|----- --|--------|------
1   | -  | -  | -  | +      | +      | P_001
2   | +  | -  | -  | -      | -      | P_002
3   | -  | +  | -  | -      | +      | P_003
4   | +  | +  | -  | +      | -      | P_004
5   | -  | -  | +  | +      | -      | P_005
6   | +  | -  | +  | -      | +      | P_006
7   | -  | +  | +  | -      | -      | P_007
8   | +  | +  | +  | +      | +      | P_008

8 runs screen 5 factors (vs 32 for full factorial: 75% savings)
```

## Taguchi Orthogonal Arrays

Taguchi methods focus on finding factor settings that are robust to noise (uncontrollable factors).

### Standard Arrays

| Array | Factors | Levels | Runs | Use Case |
|-------|---------|--------|------|----------|
| L4 | 3 | 2 | 4 | Quick screening |
| L8 | 7 | 2 | 8 | Two-level screening |
| L9 | 4 | 3 | 9 | Three-level factors |
| L16 | 15 | 2 | 16 | Large two-level screening |
| L27 | 13 | 3 | 27 | Full three-level design |

### L9 Array (4 factors, 3 levels)

```
Run | A | B | C | D
----|---|---|---|---
1   | 1 | 1 | 1 | 1
2   | 1 | 2 | 2 | 2
3   | 1 | 3 | 3 | 3
4   | 2 | 1 | 2 | 3
5   | 2 | 2 | 3 | 1
6   | 2 | 3 | 1 | 2
7   | 3 | 1 | 3 | 2
8   | 3 | 2 | 1 | 3
9   | 3 | 3 | 2 | 1
```

### Signal-to-Noise Ratios

| Type | Formula | Use When |
|------|---------|----------|
| Larger-is-better | SN = -10 log(mean(1/y^2)) | Maximizing kill_rate |
| Smaller-is-better | SN = -10 log(mean(y^2)) | Minimizing damage_taken |
| Nominal-is-best | SN = 10 log(mean^2 / variance) | Targeting specific value |

### clau-doom Taguchi Example

Inner array (control factors, L9): retreat_threshold (3 levels), ammo_conservation (3 levels), exploration_priority (3 levels), weapon_preference (3 levels).

Outer array (noise factors, L4): map_difficulty (easy/hard), enemy_density (sparse/dense).

```
Total runs: 9 (inner) x 4 (outer) = 36
Each run: 30 episodes (for statistical stability)

For each inner array row, compute:
  SN_kill = -10 * log10(mean(1/kill_rate^2))  across the 4 noise conditions

Select factor levels that maximize SN ratio = robust to map/enemy variation.
```

## Response Surface Methodology (RSM)

After screening identifies significant factors (Phase 1), RSM fits a second-order polynomial to find the optimum.

### Central Composite Design (CCD)

CCD = 2^k factorial points + 2k axial (star) points + center points.

For k=2 factors:

```
Point Type | x1    | x2    | Count
-----------|-------|-------|------
Factorial  | -1    | -1    | 1
           | +1    | -1    | 1
           | -1    | +1    | 1
           | +1    | +1    | 1
Axial      | -alpha| 0     | 1
           | +alpha| 0     | 1
           | 0     | -alpha| 1
           | 0     | +alpha| 1
Center     | 0     | 0     | 3-5

Total: 4 + 4 + 5 = 13 runs
```

Alpha values:
- Rotatable: alpha = (2^k)^(1/4) = 1.414 for k=2
- Face-centered: alpha = 1

### Model

```
y = b0 + b1*x1 + b2*x2 + b12*x1*x2 + b11*x1^2 + b22*x2^2 + epsilon
```

Find stationary point by setting partial derivatives to zero:
```
dy/dx1 = b1 + b12*x2 + 2*b11*x1 = 0
dy/dx2 = b2 + b12*x1 + 2*b22*x2 = 0
```

### Box-Behnken Design (BBD)

Alternative to CCD for 3+ factors. No extreme corner points (all factorial points have at least one factor at center level).

For k=3 factors:

```
Run | x1 | x2 | x3
----|----|----|----
1   | -1 | -1 | 0
2   | +1 | -1 | 0
3   | -1 | +1 | 0
4   | +1 | +1 | 0
5   | -1 | 0  | -1
6   | +1 | 0  | -1
7   | -1 | 0  | +1
8   | +1 | 0  | +1
9   | 0  | -1 | -1
10  | 0  | +1 | -1
11  | 0  | -1 | +1
12  | 0  | +1 | +1
13-15| 0 | 0  | 0   (center points)

Total: 15 runs (vs 20 for CCD with k=3)
```

## Split-Plot Design

When some factors are hard to change (require agent restart) and others are easy to change (MD parameter edit).

```
Whole-plot factors (hard to change):
  - Map type / seed (requires restart)
  - Agent base architecture

Sub-plot factors (easy to change):
  - retreat_threshold (MD edit)
  - ammo_conservation (MD edit)
  - exploration_priority (MD edit)

Randomization restriction:
  1. Randomly assign whole-plot levels to containers
  2. Within each container, randomly assign sub-plot combinations
  3. This minimizes container restarts

Analysis: REML (Restricted Maximum Likelihood) to separate whole-plot
and sub-plot error terms.
```

## Blocking

Remove nuisance variation by grouping experimental runs into blocks.

```
Block variable: map_difficulty (easy / hard)

Block 1 (easy): Runs 1-4
Block 2 (hard): Runs 5-8

The block effect is estimated and removed from error, increasing
sensitivity for detecting factor effects.

ANOVA with blocking:
  Source      | SS  | df | MS  | F
  ------------|-----|----|-----|----
  Blocks      | SSB | 1  | MSB | (not tested)
  Factor A    | SSA | 1  | MSA | MSA/MSE
  Factor B    | SSB | 1  | MSB | MSB/MSE
  Error       | SSE | 4  | MSE |
```

## Center Points

Add runs at the midpoint of all factors to test for curvature (nonlinear effects).

```
Factorial runs at corners: (-1, -1), (+1, -1), (-1, +1), (+1, +1)
Center points at: (0, 0, 0) with 3-5 replicates

Test for curvature:
  H0: No curvature (linear model sufficient)
  H1: Curvature present (need RSM)

  SS_curvature = (n_f * n_c * (y_bar_f - y_bar_c)^2) / (n_f + n_c)

If significant curvature detected: proceed to Phase 2 (RSM-CCD).
```

## clau-doom DOE Matrix Examples

### Phase 0: OFAT Baseline

```
Experiment: Vary aggression_level only
Levels: 0.1, 0.3, 0.5, 0.7, 0.9
Other factors: fixed at defaults
Episodes: 30 per level
Purpose: Estimate effect size and variance for power analysis
```

### Phase 1: Screening (2^4 Factorial)

```
Factors:
  A: retreat_threshold (0.30 / 0.45)
  B: ammo_conservation (low / high)
  C: exploration_priority (low / high)
  D: aggression_level (0.3 / 0.7)

Runs: 16 + 4 center points = 20
Replicates: 30 episodes per run
Blocking: map_difficulty (easy/hard)
Agents: P_001 through P_020

Analysis: Full ANOVA with all main effects and 2FI.
Identify significant factors (p < 0.05) for Phase 2.
```

### Phase 2: RSM-CCD

```
Significant factors from Phase 1: retreat_threshold, aggression_level
Design: CCD with alpha = 1.414 (rotatable)

  Run | retreat (coded) | aggression (coded) | Agent
  ----|-----------------|---------------------|------
  1   | -1              | -1                  | P_001
  2   | +1              | -1                  | P_002
  3   | -1              | +1                  | P_003
  4   | +1              | +1                  | P_004
  5   | -1.414          | 0                   | P_005
  6   | +1.414          | 0                   | P_006
  7   | 0               | -1.414              | P_007
  8   | 0               | +1.414              | P_008
  9-13| 0               | 0                   | P_009 (5 center points)

Fit: y = b0 + b1*x1 + b2*x2 + b12*x1*x2 + b11*x1^2 + b22*x2^2
Find stationary point and confirm with 10 validation episodes.
```

## DOE Phase Progression

```
Phase 0 (OFAT)
  |  Identified > 3 interesting factors
  v
Phase 1 (Factorial / Fractional)
  |  Found significant main effects + interactions
  v
Phase 2 (RSM - CCD/BBD)
  |  Near-optimal region, converging
  v
Phase 3 (Taguchi Robust Design)
  |  Optimal robust to noise
  v
Meta-analysis across experiments
```

Transition criteria:
- 0 to 1: Variance estimates available, > 3 candidate factors identified
- 1 to 2: Significant main effects found (p < 0.05), curvature detected
- 2 to 3: Optimal region identified, need robustness against map/enemy variation
- 3 to Meta: Multiple generations of experiments, cross-study synthesis needed
