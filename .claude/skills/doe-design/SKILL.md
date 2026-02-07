---
name: doe-design
description: Design of Experiments matrix design for systematic game agent optimization
user-invocable: false
---

# DOE Design Skill

Design of Experiments (DOE) matrix design for systematic, statistically rigorous game agent optimization. Covers full lifecycle from screening designs through response surface methodology.

## Design Types

### Full Factorial (2^k)

Complete enumeration of all factor-level combinations. Use when k <= 4 factors and runs are cheap.

```
2^2 = 4 runs    (2 factors, 2 levels each)
2^3 = 8 runs    (3 factors, 2 levels each)
2^4 = 16 runs   (4 factors, 2 levels each)
```

Design matrix for 2^3 (factors A, B, C):

```
Run | A  | B  | C
----|----|----|----
1   | -1 | -1 | -1
2   | +1 | -1 | -1
3   | -1 | +1 | -1
4   | +1 | +1 | -1
5   | -1 | -1 | +1
6   | +1 | -1 | +1
7   | -1 | +1 | +1
8   | +1 | +1 | +1
```

### Fractional Factorial (2^(k-p))

Reduces runs by confounding higher-order interactions. Use when k >= 5 or runs are expensive.

Resolution levels:
- **Resolution III**: Main effects aliased with 2-factor interactions. Screening only.
- **Resolution IV**: Main effects clear of 2FI; 2FI aliased with each other.
- **Resolution V**: Main effects and 2FI clear of each other. Gold standard for screening.

Example 2^(5-2) Resolution III:
- 5 factors in 8 runs (instead of 32)
- Generator: D=AB, E=AC
- Defining relation: I=ABD=ACE=BCDE

### Taguchi L-Arrays

Orthogonal arrays for robust parameter design. Focus on signal-to-noise ratio.

Common arrays:
- **L4(2^3)**: 3 factors at 2 levels, 4 runs
- **L8(2^7)**: Up to 7 factors at 2 levels, 8 runs
- **L9(3^4)**: 4 factors at 3 levels, 9 runs
- **L18(2^1 x 3^7)**: Mixed 2/3 level, 18 runs

S/N ratios:
- Larger-is-better: S/N = -10 log(mean(1/y^2))
- Smaller-is-better: S/N = -10 log(mean(y^2))
- Nominal-is-best: S/N = 10 log(mean^2/variance)

### Response Surface Methodology (RSM)

For optimization after screening. Models curvature with quadratic terms.

**Central Composite Design (CCD)**:
- Factorial points (2^k or 2^(k-p))
- Axial/star points at distance alpha from center
- Center points (3-6 replicates)
- Rotatable: alpha = (2^k)^(1/4)
- Face-centered (alpha=1): stays within factor bounds

**Box-Behnken Design (BBD)**:
- No corner points (all factors never at extreme simultaneously)
- 3 levels per factor
- Fewer runs than CCD for k >= 3
- Requires: 2k(k-1) + center points

### Split-Plot Designs

When some factors are hard to change (e.g., Docker config requires restart).

```
Whole-plot factor: docker_memory_limit (hard to change)
Sub-plot factors: aggression, ammo_threshold (easy to change via MD injection)
```

Restricts randomization: whole-plot factors changed less frequently. ANOVA uses separate error terms for whole-plot and sub-plot.

## Factor-Level Coding

Standard coding convention:

| Symbol | Meaning | Numeric |
|--------|---------|---------|
| `-` or `-1` | Low level | Factor minimum |
| `0` | Center point | Factor midpoint |
| `+` or `+1` | High level | Factor maximum |

For 3+ levels:
- `-1, -0.5, 0, +0.5, +1` for 5 levels
- Map to actual values via: actual = center + coded * half_range

Example factor coding:

```
Factor: retreat_threshold
  Low (-1):    0.20 (aggressive, rarely retreats)
  Center (0):  0.40
  High (+1):   0.60 (conservative, retreats early)

Factor: ammo_conservation
  Low (-1):    0.30 (liberal ammo usage)
  Center (0):  0.55
  High (+1):   0.80 (strict conservation)

Factor: exploration_priority
  Low (-1):    0.20 (minimal exploration)
  Center (0):  0.50
  High (+1):   0.80 (heavy exploration)
```

## Design Matrix Generation

### Standard Order
Factors cycle at different rates:
- Factor A: alternates every run (-,+,-,+,...)
- Factor B: alternates every 2 runs (-,-,+,+,-,-,+,+,...)
- Factor C: alternates every 4 runs (-,-,-,-,+,+,+,+)

### Randomization
Always randomize run order within blocks to avoid systematic bias. Use fixed seeds for reproducibility.

### Replication
- **Replicates**: Independent runs at same factor settings with different random seeds
- Minimum 2-3 replicates per design point
- Center point replicates: 3-6 for curvature estimation and pure error

## Blocking Strategies

Block on nuisance variables that cannot be controlled:
- **Time blocks**: Morning vs afternoon runs
- **Hardware blocks**: Different GPU nodes
- **Seed blocks**: Different random seed groups

Block assignment rule: confound blocks with highest-order interactions only.

For 2^3 in 2 blocks: confound ABC interaction with blocks.

## Center Points for Curvature Testing

Add center points (all factors at 0) to factorial designs:

- Detect curvature (quadratic effects) without full RSM
- Estimate pure error for lack-of-fit test
- 3-6 center points recommended
- F-test for curvature: compare center point mean to factorial point mean

If curvature significant (p < 0.05): augment to RSM (CCD or BBD).

## Resolution and Aliasing Structure

Resolution determines what effects can be estimated independently:

```
Resolution III:  Main effects aliased with 2FI
Resolution IV:   Main effects clear; 2FI aliased with 2FI
Resolution V:    Main effects and 2FI clear; 2FI aliased with 3FI
Resolution VI+:  Main effects, 2FI, and some 3FI clear
```

Alias structure example (2^(4-1), generator D=ABC):
```
I = ABCD
A = BCD
B = ACD
C = ABD
D = ABC
AB = CD
AC = BD
AD = BC
```

## Phase Progression

DOE phases progress from simple to complex as understanding grows:

```
Phase 0: OFAT (One-Factor-At-a-Time)
  Purpose: Baseline establishment, factor range discovery
  Runs: k factors * (levels-1) + 1
  Limitation: Cannot detect interactions
  When: Very first exploration, unknown factor ranges

Phase 1: Factorial / Fractional Factorial
  Purpose: Screen important factors, detect interactions
  Design: 2^k or 2^(k-p) with replicates
  Analysis: Main effects, 2FI, significance testing
  When: After OFAT establishes reasonable ranges

Phase 2: Taguchi L-Array
  Purpose: Robust parameter design, noise factor analysis
  Design: Inner array (control) x outer array (noise)
  Analysis: S/N ratios, factor contribution
  When: Need robustness against uncontrollable variation

Phase 3: RSM (CCD or BBD)
  Purpose: Optimization, find optimal operating conditions
  Design: Augment factorial with axial + center points
  Analysis: Quadratic model, contour/surface plots, optimization
  When: Significant curvature detected in Phase 1
```

Transition criteria:
- Phase 0 -> 1: Factor ranges established, at least 2 factors identified
- Phase 1 -> 2: Significant factors identified, need robustness
- Phase 1 -> 3: Curvature detected in center point test (p < 0.05)
- Phase 2 -> 3: Robust settings found, need fine optimization

## Example: 2^3 Factorial Design

Factors:
- A: retreat_threshold (0.20, 0.60)
- B: ammo_conservation (0.30, 0.80)
- C: exploration_priority (0.20, 0.80)

```
Run | A     | B     | C     | retreat | ammo  | explore
----|-------|-------|-------|---------|-------|--------
1   | -1    | -1    | -1    | 0.20    | 0.30  | 0.20
2   | +1    | -1    | -1    | 0.60    | 0.30  | 0.20
3   | -1    | +1    | -1    | 0.20    | 0.80  | 0.20
4   | +1    | +1    | -1    | 0.60    | 0.80  | 0.20
5   | -1    | -1    | +1    | 0.20    | 0.30  | 0.80
6   | +1    | -1    | +1    | 0.60    | 0.30  | 0.80
7   | -1    | +1    | +1    | 0.20    | 0.80  | 0.80
8   | +1    | +1    | +1    | 0.60    | 0.80  | 0.80
CP  |  0    |  0    |  0    | 0.40    | 0.55  | 0.50
```

Add 3 center point replicates (runs 9-11) for curvature test.

With 3 replicates per run: 11 design points * 3 seeds = 33 total runs.

## Design Selection Guide

| Factors | Budget (runs) | Recommended Design |
|---------|---------------|-------------------|
| 2-3     | Low           | Full factorial 2^k |
| 4-5     | Low           | Fractional 2^(k-1) Res V |
| 6-8     | Low           | Fractional 2^(k-p) Res IV |
| 3-5     | High          | CCD (rotatable) |
| 3-7     | Medium        | BBD |
| 3+      | Very low      | Taguchi L-array |
| Mixed   | Any           | Split-plot |

## Output Format

Design specifications are recorded in EXPERIMENT_ORDER documents:

```yaml
experiment_id: EXP-001
phase: 1
design_type: full_factorial_2k
factors:
  - name: retreat_threshold
    levels: [0.20, 0.60]
    coded: [-1, +1]
  - name: ammo_conservation
    levels: [0.30, 0.80]
    coded: [-1, +1]
  - name: exploration_priority
    levels: [0.20, 0.80]
    coded: [-1, +1]
center_points: 3
replicates: 3
seeds: [42, 137, 256]
blocking: none
total_runs: 33
randomization_seed: 12345
```
