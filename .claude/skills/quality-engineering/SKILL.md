---
name: quality-engineering
description: Quality engineering methods including SPC, capability indices, FMEA, TOPSIS, and AHP
user-invocable: false
---

# Quality Engineering Skill

Comprehensive quality engineering methods for monitoring agent performance, prioritizing improvements, and multi-criteria decision making in the evolutionary optimization pipeline.

## Statistical Process Control (SPC)

### X-bar/R Control Charts

Monitor agent generation performance over time to detect special-cause variation.

**X-bar chart** (monitors process mean):
```
UCL = X-bar-bar + A2 * R-bar
CL  = X-bar-bar
LCL = X-bar-bar - A2 * R-bar
```

**R chart** (monitors process variability):
```
UCL = D4 * R-bar
CL  = R-bar
LCL = D3 * R-bar
```

Constants (subgroup size n):

| n | A2    | D3   | D4    |
|---|-------|------|-------|
| 2 | 1.880 | 0    | 3.267 |
| 3 | 1.023 | 0    | 2.574 |
| 4 | 0.729 | 0    | 2.282 |
| 5 | 0.577 | 0    | 2.114 |

Application: Each generation is a subgroup. Track kill_rate, survival_time, or composite score across generations.

### Western Electric Rules (Zone Tests)

Divide control chart into zones:
- Zone A: between 2sigma and 3sigma from center
- Zone B: between 1sigma and 2sigma from center
- Zone C: within 1sigma of center

Out-of-control signals:
1. **Rule 1**: One point beyond 3sigma (Zone A boundary)
2. **Rule 2**: 2 out of 3 consecutive points in Zone A or beyond (same side)
3. **Rule 3**: 4 out of 5 consecutive points in Zone B or beyond (same side)
4. **Rule 4**: 8 consecutive points on same side of center line
5. **Rule 5**: 6 consecutive points steadily increasing or decreasing (trend)
6. **Rule 6**: 14 consecutive points alternating up and down (oscillation)
7. **Rule 7**: 15 consecutive points within Zone C (stratification)
8. **Rule 8**: 8 consecutive points beyond Zone C on both sides (mixture)

When any rule triggers: investigate the generation for special-cause variation.

### Control Limit Computation

```
X-bar-bar = grand mean of all subgroup means
R-bar = mean of all subgroup ranges
sigma_hat = R-bar / d2  (d2 from table, e.g., d2=1.128 for n=2)

UCL = X-bar-bar + 3 * sigma_hat / sqrt(n)
LCL = X-bar-bar - 3 * sigma_hat / sqrt(n)
```

## Capability Indices

Measure how well a process meets specifications.

### Cp (Process Capability)

```
Cp = (USL - LSL) / (6 * sigma)
```

Measures spread relative to specification width. Does NOT account for centering.

| Cp Value | Interpretation |
|----------|---------------|
| < 1.0    | Not capable |
| 1.0-1.33 | Marginally capable |
| 1.33-1.67| Capable |
| > 1.67   | Highly capable |

### Cpk (Process Capability Index)

```
CPU = (USL - X-bar) / (3 * sigma)
CPL = (X-bar - LSL) / (3 * sigma)
Cpk = min(CPU, CPL)
```

Accounts for centering. Cpk <= Cp always. If Cpk = Cp, process is perfectly centered.

### Pp and Ppk (Process Performance)

Same formulas as Cp/Cpk but use overall standard deviation (not within-subgroup):

```
Pp = (USL - LSL) / (6 * s_overall)
Ppk = min((USL - X-bar)/(3*s_overall), (X-bar - LSL)/(3*s_overall))
```

Use Pp/Ppk for long-term performance, Cp/Cpk for short-term capability.

### Application to Agent Evolution

Define specifications based on objectives:
```
kill_rate:
  LSL: 0.5   (minimum acceptable kill rate)
  USL: none  (higher is always better, use one-sided Cpk)
  Target: 0.8

survival_time:
  LSL: 1000 ticks
  USL: none
  Target: 5000 ticks
```

One-sided capability (no USL):
```
Cpk = CPL = (X-bar - LSL) / (3 * sigma)
```

## Failure Mode and Effects Analysis (FMEA)

### RPN Calculation

```
RPN = Severity * Occurrence * Detection

Severity (S):    1-10 (impact of failure)
Occurrence (O):  1-10 (frequency of failure)
Detection (D):   1-10 (ability to detect before failure, 10=undetectable)
```

### Severity Scale (Agent Context)

| S | Description | Example |
|---|-------------|---------|
| 1 | No effect | Cosmetic log difference |
| 3 | Minor | Slightly suboptimal ammo usage |
| 5 | Moderate | Misses 20% of kill opportunities |
| 7 | High | Agent gets stuck temporarily |
| 9 | Critical | Agent dies repeatedly in same pattern |
| 10| Catastrophic | Agent crashes, no data collected |

### Occurrence Scale

| O | Description | Rate |
|---|-------------|------|
| 1 | Rare | < 1 in 1000 runs |
| 3 | Low | 1 in 100 runs |
| 5 | Moderate | 1 in 20 runs |
| 7 | High | 1 in 10 runs |
| 9 | Very high | 1 in 3 runs |
| 10| Certain | Every run |

### Detection Scale

| D | Description | Method |
|---|-------------|--------|
| 1 | Certain | Automated pre-run validation |
| 3 | High | SPC chart monitoring |
| 5 | Moderate | Post-run statistical analysis |
| 7 | Low | Manual log review |
| 9 | Very low | Only discovered in aggregate |
| 10| None | Undetectable until paper review |

### FMEA Registry

Maintain a living FMEA document:

```yaml
fmea_registry:
  - id: FM-001
    failure_mode: "Agent loops in corner"
    cause: "Exploration priority too low with high retreat_threshold"
    effect: "Zero kills, wasted run"
    severity: 7
    occurrence: 5
    detection: 3
    rpn: 105
    action: "Add stuck detection, auto-restart"
    status: mitigated
    new_rpn: 21

  - id: FM-002
    failure_mode: "Ammo depleted early"
    cause: "Low ammo_conservation with aggressive playstyle"
    effect: "Cannot engage enemies in second half"
    severity: 5
    occurrence: 7
    detection: 5
    rpn: 175
    action: "Add ammo checkpoint logic in strategy"
    status: open
```

Priority actions: Address highest RPN items first. Target RPN < 100 for all items.

## TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)

Multi-criteria decision making for ranking agents in a generation.

### Algorithm Steps

**Step 1: Construct decision matrix**
```
         kill_rate  survival  ammo_eff  explore_pct  damage_ratio
Agent_1  [  0.75     3200      0.82       0.65         1.40    ]
Agent_2  [  0.60     4100      0.71       0.80         1.10    ]
Agent_3  [  0.85     2800      0.65       0.55         1.80    ]
Agent_4  [  0.70     3500      0.78       0.70         1.30    ]
```

**Step 2: Normalize (vector normalization)**
```
r_ij = x_ij / sqrt(sum(x_ij^2)) for each column j
```

**Step 3: Apply weights**
```
v_ij = w_j * r_ij

Weights example:
  kill_rate: 0.30
  survival: 0.25
  ammo_efficiency: 0.15
  exploration_pct: 0.15
  damage_ratio: 0.15
```

**Step 4: Determine ideal and anti-ideal solutions**
```
A+ = (max(v_1j), max(v_2j), ..., max(v_nj))  for benefit criteria
A- = (min(v_1j), min(v_2j), ..., min(v_nj))  for benefit criteria
(reverse for cost criteria)
```

**Step 5: Calculate distances**
```
D_i+ = sqrt(sum((v_ij - v_j+)^2))   distance to ideal
D_i- = sqrt(sum((v_ij - v_j-)^2))   distance to anti-ideal
```

**Step 6: Calculate closeness coefficient**
```
C_i = D_i- / (D_i+ + D_i-)
```

Range: 0 (worst) to 1 (best). Rank agents by C_i descending.

## AHP (Analytic Hierarchy Process)

Determine criteria weights through pairwise comparison.

### Pairwise Comparison Scale

| Intensity | Definition |
|-----------|------------|
| 1 | Equal importance |
| 3 | Moderate importance |
| 5 | Strong importance |
| 7 | Very strong importance |
| 9 | Extreme importance |
| 2,4,6,8 | Intermediate values |

### Comparison Matrix Example

```
              kill_rate  survival  ammo_eff  explore  damage
kill_rate        1         2         3         3        2
survival        1/2        1         2         2        1
ammo_eff        1/3       1/2        1         1       1/2
explore         1/3       1/2        1         1       1/2
damage          1/2        1         2         2        1
```

### Priority Vector Computation

1. Normalize each column (divide by column sum)
2. Average each row = priority vector (weights)
3. Check consistency

### Consistency Ratio (CR)

```
lambda_max = sum of (column_sum * weight) for each criterion
CI = (lambda_max - n) / (n - 1)
CR = CI / RI
```

Random Index (RI) table:

| n | RI |
|---|------|
| 3 | 0.58 |
| 4 | 0.90 |
| 5 | 1.12 |
| 6 | 1.24 |

Acceptable: CR < 0.10. If CR >= 0.10, revise pairwise comparisons.

## Integration Pipeline

SPC, FMEA, TOPSIS, and AHP form an integrated quality loop:

```
Generation N completes
      |
      v
[SPC] Plot generation metrics on control charts
      |
      +--> Signal detected? --> [FMEA] Update failure modes
      |                              |
      v                              v
[TOPSIS] Rank agents in generation   Update RPN scores
      |                              |
      v                              v
[AHP] Validate/update criteria      Prioritize corrective actions
      weights if needed
      |
      v
Parent selection for Generation N+1
      |
      v
[Evolution Strategy] Crossover + Mutation
```

### When to Update AHP Weights

- After Phase transition (Phase 1 -> Phase 2, etc.)
- When FMEA reveals new dominant failure mode
- Every 5-10 generations (scheduled review)
- When SPC detects significant process shift
