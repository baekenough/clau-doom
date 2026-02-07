# Quality Engineering Reference Guide

Reference documentation for quality engineering methods in clau-doom.

## Key Resources

- Montgomery, D.C. (2019). *Introduction to Statistical Quality Control*, 8th Edition. Wiley.
- AIAG (2019). *FMEA Handbook*, 1st Edition.
- Hwang, C.L., Yoon, K. (1981). *Multiple Attribute Decision Making*. Springer.
- Saaty, T.L. (1980). *The Analytic Hierarchy Process*. McGraw-Hill.

## clau-doom Context

Quality engineering tools monitor and optimize agent performance across generations:
- **SPC**: Detect anomalies in generation-over-generation performance
- **Process Capability**: Quantify strategy stability (Cpk)
- **FMEA**: Systematically prioritize failure modes for improvement
- **TOPSIS**: Rank agents when multiple metrics conflict
- **AHP**: Determine metric weights through structured comparison

## SPC (Statistical Process Control)

### X-bar Chart

Monitors the process mean over time (across generations).

```
Centerline: CL = X-double-bar (grand mean of subgroup means)
Upper Control Limit: UCL = X-double-bar + A2 * R-bar
Lower Control Limit: LCL = X-double-bar - A2 * R-bar
```

Constants table (by subgroup size n):

| n | A2 | D3 | D4 | d2 |
|---|------|------|------|------|
| 2 | 1.880 | 0 | 3.267 | 1.128 |
| 3 | 1.023 | 0 | 2.574 | 1.693 |
| 4 | 0.729 | 0 | 2.282 | 2.059 |
| 5 | 0.577 | 0 | 2.114 | 2.326 |
| 6 | 0.483 | 0 | 2.004 | 2.534 |
| 7 | 0.419 | 0.076 | 1.924 | 2.704 |
| 8 | 0.373 | 0.136 | 1.864 | 2.847 |
| 9 | 0.337 | 0.184 | 1.816 | 2.970 |
| 10 | 0.308 | 0.223 | 1.777 | 3.078 |

### R Chart

Monitors process variability (range within each generation).

```
Centerline: CL = R-bar (average of subgroup ranges)
UCL = D4 * R-bar
LCL = D3 * R-bar
```

### Western Electric Rules

Out-of-control signals indicating assignable causes:

| Rule | Description | Pattern |
|------|-------------|---------|
| 1 | 1 point beyond 3 sigma | Single extreme value |
| 2 | 2 out of 3 consecutive points beyond 2 sigma (same side) | Shift warning |
| 3 | 4 out of 5 consecutive points beyond 1 sigma (same side) | Sustained shift |
| 4 | 8 consecutive points on same side of center line | Systematic bias |
| 5 | 6 consecutive points steadily increasing or decreasing | Trend/drift |
| 6 | 15 consecutive points within 1 sigma (both sides) | Stratification |
| 7 | 14 consecutive points alternating up and down | Oscillation |
| 8 | 8 consecutive points beyond 1 sigma (both sides) | Mixture |

### clau-doom SPC Application

```
Subgroup: All agents in one generation
Metric: kill_rate per episode
Subgroup size: n = number of agents per generation (typically 5-8)

Baseline established: Generation 3+ (after initial Phase 0 exploration)
Monitoring: Each new generation is a new subgroup

Out-of-control signals trigger:
  - Rule 1 (3-sigma): Investigate specific agent mutation
  - Rule 4 (8 same side): Check for systematic improvement or degradation
  - Rule 5 (6 trending): Validate DOE optimization is working

PI reviews SPC dashboard to decide next experiment focus.
```

## Process Capability

### Cp (Potential Capability)

Measures how well the process fits within specification limits, assuming centered.

```
Cp = (USL - LSL) / (6 * sigma)

Where:
  USL = Upper Specification Limit (PI-defined target)
  LSL = Lower Specification Limit (PI-defined minimum)
  sigma = process standard deviation (estimated from R-bar / d2)
```

### Cpk (Actual Capability)

Accounts for process centering (how close the mean is to the nearest spec limit).

```
Cpk = min( (USL - X-bar) / (3 * sigma),  (X-bar - LSL) / (3 * sigma) )
```

### Interpretation

| Cpk Value | Interpretation | clau-doom Action |
|-----------|----------------|------------------|
| Cpk < 0.67 | Not capable | Strategy needs major revision, high mutation priority |
| 0.67 <= Cpk < 1.00 | Barely capable | Strategy under observation, moderate mutation |
| 1.00 <= Cpk < 1.33 | Capable | Acceptable, low mutation priority |
| Cpk >= 1.33 | Highly capable | Elite strategy, preserve and propagate |
| Cpk >= 2.00 | Six Sigma level | Benchmark strategy for knowledge base |

### clau-doom Capability Application

```
Metric: kill_rate
USL: PI-defined target (e.g., 15 kills/episode)
LSL: PI-defined minimum (e.g., 5 kills/episode)
sigma: Standard deviation of agent's kill_rate across episodes

Parent selection weights:
  Score = mean_kill_rate * Cpk_weight

  Where Cpk_weight:
    Cpk >= 1.33: weight = 1.2 (bonus for stability)
    1.00 <= Cpk < 1.33: weight = 1.0
    Cpk < 1.00: weight = 0.8 (penalty for instability)
```

## FMEA (Failure Mode and Effects Analysis)

### Components

| Factor | Scale | Description |
|--------|-------|-------------|
| Severity (S) | 1-10 | Impact of the failure on game outcome |
| Occurrence (O) | 1-10 | Frequency of the failure mode |
| Detection (D) | 1-10 | Difficulty of detecting/preventing (10 = hardest to detect) |

### RPN (Risk Priority Number)

```
RPN = S x O x D

Range: 1 to 1000
Priority: Address highest RPN items first
```

### Severity Scale (clau-doom)

| Rating | Criteria | Example |
|--------|----------|---------|
| 1-2 | Minor: Slight score reduction | Missed ammo pickup |
| 3-4 | Low: Moderate score impact | Suboptimal weapon choice |
| 5-6 | Moderate: Significant score impact | Failed retreat, lost 30% health |
| 7-8 | High: Major score impact | Death with partial progress |
| 9-10 | Critical: Complete failure | Immediate death, no progress |

### Occurrence Scale (clau-doom)

| Rating | Frequency | Per 100 episodes |
|--------|-----------|------------------|
| 1 | Extremely rare | < 1 |
| 2-3 | Low | 1-5 |
| 4-5 | Moderate | 6-20 |
| 6-7 | High | 21-50 |
| 8-9 | Very high | 51-80 |
| 10 | Almost certain | > 80 |

### Detection Scale (clau-doom)

| Rating | Detection Ability | RAG Coverage |
|--------|-------------------|--------------|
| 1 | Almost certain | Strong strategy docs with high trust_score |
| 2-3 | High | Multiple relevant docs in OpenSearch |
| 4-5 | Moderate | Some docs but low confidence |
| 6-7 | Low | Few docs, untested strategies |
| 8-9 | Very low | No matching docs in knowledge base |
| 10 | Undetectable | Completely novel situation |

### FMEA Table Example

```
| Failure Mode          | S | O | D | RPN | Action Priority |
|----------------------|---|---|---|-----|-----------------|
| Ambush during explore | 7 | 6 | 6 | 252 | HIGH - New DOE experiment |
| Corridor multi-enemy  | 9 | 8 | 3 | 216 | HIGH - Strategy refinement |
| Ammo exhaustion       | 8 | 4 | 4 | 128 | MEDIUM - Adjust conservation |
| Open area sniping     | 5 | 7 | 2 | 70  | LOW - Existing strategy OK |

PI uses RPN to prioritize next generation's experiment focus.
After each generation, reassess O and D to track improvement.
Decreasing RPN over generations = evidence of systematic learning.
```

## TOPSIS (Technique for Order Preference by Similarity to Ideal Solution)

Multi-criteria decision making for ranking agents when metrics conflict.

### Procedure

**Step 1: Decision Matrix**

```
           | kill_rate | survival | Cpk  | ammo_eff | innovation
-----------|-----------|----------|------|----------|----------
Agent_001  | 8.2       | 420      | 1.35 | 0.72     | 3
Agent_002  | 6.5       | 580      | 1.60 | 0.85     | 1
Agent_003  | 9.1       | 350      | 0.95 | 0.60     | 5
Agent_004  | 7.0       | 500      | 1.20 | 0.80     | 2
```

**Step 2: Normalize**

```
r_ij = x_ij / sqrt(sum(x_ij^2))

For kill_rate column:
  norm = sqrt(8.2^2 + 6.5^2 + 9.1^2 + 7.0^2) = 15.57
  r_11 = 8.2 / 15.57 = 0.527
  r_21 = 6.5 / 15.57 = 0.418
  ...
```

**Step 3: Apply Weights**

```
Weights (PI-defined, may use AHP):
  w = [0.30, 0.25, 0.20, 0.10, 0.15]

v_ij = w_j * r_ij
```

**Step 4: Determine Ideal Solutions**

```
Positive Ideal (A+): max of each beneficial criterion, min of cost criteria
Negative Ideal (A-): min of each beneficial criterion, max of cost criteria

A+ = (max(v_1j), max(v_2j), max(v_3j), max(v_4j), max(v_5j))
A- = (min(v_1j), min(v_2j), min(v_3j), min(v_4j), min(v_5j))
```

**Step 5: Euclidean Distance**

```
d_i+ = sqrt(sum((v_ij - A+_j)^2))   # Distance to positive ideal
d_i- = sqrt(sum((v_ij - A-_j)^2))   # Distance to negative ideal
```

**Step 6: Closeness Coefficient**

```
C_i = d_i- / (d_i+ + d_i-)

Range: 0 to 1 (1 = closest to ideal)
Rank agents by C_i descending.
```

### clau-doom TOPSIS Application

```
Criteria weights (PI adjusts per generation strategy):

  Aggressive generation focus:
    w = [0.40, 0.15, 0.15, 0.10, 0.20]  # Emphasis on kill_rate

  Survival generation focus:
    w = [0.15, 0.40, 0.20, 0.15, 0.10]  # Emphasis on survival

  Stability generation focus:
    w = [0.20, 0.20, 0.35, 0.15, 0.10]  # Emphasis on Cpk

Top-ranked agents by C_i become parents for next generation.
```

## AHP (Analytic Hierarchy Process)

Structured method for PI to derive criterion weights through pairwise comparison.

### Pairwise Comparison Matrix

Scale: 1 (equal) to 9 (extremely more important). Reciprocals for reverse comparisons.

```
          | kill  | surv  | Cpk   | ammo  | innov
----------|-------|-------|-------|-------|------
kill_rate | 1     | 2     | 3     | 5     | 2
survival  | 1/2   | 1     | 2     | 3     | 2
Cpk       | 1/3   | 1/2   | 1     | 2     | 1
ammo_eff  | 1/5   | 1/3   | 1/2   | 1     | 1/2
innovation| 1/2   | 1/2   | 1     | 2     | 1
```

### Priority Vector (Eigenvalue Method)

1. Normalize each column (divide by column sum)
2. Average each row = priority weight
3. Verify: w = [0.38, 0.24, 0.15, 0.08, 0.15]

### Consistency Check

```
Consistency Index: CI = (lambda_max - n) / (n - 1)
Random Index (n=5): RI = 1.12
Consistency Ratio: CR = CI / RI

CR < 0.10: Consistent (acceptable)
CR >= 0.10: Inconsistent (PI must revise comparisons)
```

### clau-doom AHP Application

```
PI performs pairwise comparison at generation start:
  "For this generation, how important is kill_rate vs survival_time?"
  PI: "Kill rate is moderately more important (3)"

System computes weights via AHP.
If CR >= 0.10, system flags inconsistency for PI review.
Weights feed into TOPSIS for agent ranking.
```

## Integration in clau-doom

```
Generation Lifecycle:

1. SPC: Monitor performance of current generation
   - Out-of-control? -> Investigate assignable cause
   - In control? -> Proceed to evolution

2. Capability: Assess Cpk for each agent
   - Cpk >= 1.33: Elite (preserve)
   - Cpk < 1.00: Unstable (mutate or retire)

3. FMEA: Analyze failure modes from encounter data
   - High RPN -> Priority for next experiment

4. AHP: PI sets criterion weights for this generation
   - Derives priority vector

5. TOPSIS: Rank agents using weighted multi-criteria
   - Top agents become parents

6. Evolution: Generate next generation from top parents
   - Mutation guided by FMEA priorities
   - Stability guided by Cpk thresholds
```
