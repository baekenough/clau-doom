# [MUST] Experiment Integrity Rules

> **Priority**: MUST - Never violate
> **ID**: R100
> **Purpose**: Ensure all experiments produce reproducible, statistically valid results

## CRITICAL

**All experiments MUST follow rigorous statistical protocols. No claims without evidence.**

## Seed Fixation (MANDATORY)

All experiments MUST use fixed seed sets for reproducibility.

```
╔══════════════════════════════════════════════════════════════════╗
║  SEED FIXATION IS NON-NEGOTIABLE                                 ║
║                                                                   ║
║  - Every DOE Run specifies its seed set explicitly               ║
║  - Control and treatment use IDENTICAL seeds                     ║
║  - Seed sets stored in EXPERIMENT_ORDER and recorded in DuckDB   ║
║  - Random seed usage = Rule violation                            ║
║                                                                   ║
║  Example seed set (10 episodes):                                 ║
║    [42, 1337, 2023, 7890, 9999, 1111, 5555, 8888, 3333, 6666]    ║
║                                                                   ║
║  Control Run:   Uses seeds [42, 1337, 2023, ...]                 ║
║  Treatment Run: Uses seeds [42, 1337, 2023, ...]  ← SAME         ║
╚══════════════════════════════════════════════════════════════════╝
```

### Seed Set Requirements

```yaml
seed_set:
  size: 30  # Minimum 30 seeds per Run (adjustable by power analysis)
  format: array of integers
  storage:
    - EXPERIMENT_ORDER_{ID}.md (design phase)
    - DuckDB experiments table (execution phase)
    - OpenSearch metrics (cross-reference)
  usage:
    - Each seed corresponds to one episode
    - Seeds consumed sequentially
    - No seed reuse within same Run
    - Same seeds for control vs treatment comparison
```

### Seed Set Example

```markdown
## DOE-042: Memory-Strength Interaction

### Seed Set (n=30)
```
[42, 1337, 2023, 7890, 9999, 1111, 5555, 8888, 3333, 6666,
 1234, 5678, 9012, 3456, 7891, 2345, 6789, 1011, 1213, 1415,
 1617, 1819, 2021, 2223, 2425, 2627, 2829, 3031, 3233, 3435]
```

### Runs
- Run 1 (Control): memory=0.5, strength=0.3, seeds=[42, 1337, ...]
- Run 2 (Treatment): memory=0.7, strength=0.3, seeds=[42, 1337, ...]
```
```

## Statistical Evidence Markers (MANDATORY)

All statistical claims MUST include evidence markers:

| Marker | Format | Example |
|--------|--------|---------|
| `[STAT:p]` | p-value | [STAT:p=0.003] |
| `[STAT:ci]` | Confidence interval | [STAT:ci=95%: 2.3-4.7] |
| `[STAT:effect_size]` | Effect size | [STAT:effect_size=Cohen's d=0.82] |
| `[STAT:power]` | Statistical power | [STAT:power=1-β=0.85] |
| `[STAT:n]` | Sample size | [STAT:n=150 episodes] |
| `[STAT:f]` | F-statistic | [STAT:f=F(2,45)=12.34] |
| `[STAT:eta2]` | Effect size (ANOVA) | [STAT:eta2=partial η²=0.35] |

### Example Usage

```markdown
## Finding: Memory Factor Significant

Memory has a significant effect on kill efficiency [STAT:p=0.003] [STAT:f=F(2,87)=9.45].
Effect size is large [STAT:eta2=partial η²=0.18].
Pairwise comparisons (Tukey HSD):
- 0.7 vs 0.5: +12.3 kills [STAT:ci=95%: 8.1-16.5]
- 0.9 vs 0.5: +18.7 kills [STAT:ci=95%: 14.5-22.9]
- 0.9 vs 0.7: +6.4 kills [STAT:ci=95%: 2.2-10.6]

Sample size: [STAT:n=90 episodes (30/level)]
Statistical power: [STAT:power=1-β=0.92]
```

### Claims Without Markers = Untrusted

```
WRONG:
"Memory seems to improve performance."
→ No evidence, no trust.

CORRECT:
"Memory improves kill efficiency [STAT:p=0.003] [STAT:effect_size=Cohen's d=0.82]."
→ Evidence provided, can be trusted.
```

## Trust Score Framework

| Trust Level | Criteria | Actions |
|-------------|----------|---------|
| **HIGH** | p < 0.01, n ≥ 50/condition, residuals pass all diagnostics | Adopt finding, update FINDINGS.md |
| **MEDIUM** | p < 0.05, n ≥ 30/condition, residuals mostly clean | Tentative adoption, plan follow-up |
| **LOW** | p < 0.10, n < 30, or residual violations | Exploratory only, do not adopt |
| **UNTRUSTED** | No statistical test, anecdotal, or p ≥ 0.10 | Reject, do not record |

### Trust Level Examples

```markdown
## HIGH TRUST Example
Finding: Curiosity-Memory interaction significant.
[STAT:p=0.002] [STAT:f=F(4,135)=6.78] [STAT:eta2=partial η²=0.17]
[STAT:n=150 episodes (30/cell in 2x3 factorial)]
Residuals: Normal (Anderson-Darling p=0.42), Equal variance (Levene p=0.18)
Trust: HIGH → Adopted to FINDINGS.md

## MEDIUM TRUST Example
Finding: Curiosity main effect borderline significant.
[STAT:p=0.04] [STAT:f=F(1,58)=4.32] [STAT:eta2=partial η²=0.07]
[STAT:n=60 episodes (30/level)]
Residuals: Normal (p=0.12), Slight variance heterogeneity (Levene p=0.08)
Trust: MEDIUM → Tentative adoption, plan Phase 2 confirmation study

## LOW TRUST Example
Finding: Memory trend observed.
[STAT:p=0.09] [STAT:f=F(2,27)=2.65]
[STAT:n=30 episodes (10/level)]
Trust: LOW → Exploratory only, insufficient evidence

## UNTRUSTED Example
Finding: Agents "seem faster" with higher memory.
[No statistical test performed]
Trust: UNTRUSTED → Reject, anecdotal
```

## ANOVA Requirements

Before claiming any factor is significant:

```
╔══════════════════════════════════════════════════════════════════╗
║  ANOVA CHECKLIST (MANDATORY)                                     ║
║                                                                   ║
║  1. ANOVA table with F-statistic and p-value                     ║
║  2. Residual diagnostics:                                        ║
║     - Normality (Anderson-Darling test)                          ║
║     - Equal variance (Levene test)                               ║
║     - Independence (run order plot)                              ║
║  3. Effect size (partial η² or Cohen's d)                        ║
║  4. Power analysis (if non-significant: was sample sufficient?)  ║
║  5. Pairwise comparisons (Tukey HSD if factor significant)       ║
║                                                                   ║
║  Skipping ANY step = Incomplete analysis = Do not adopt finding  ║
╚══════════════════════════════════════════════════════════════════╝
```

### ANOVA Table Example

```
Source          | SS      | df  | MS      | F      | p-value | partial η²
----------------|---------|-----|---------|--------|---------|------------
Memory          | 1234.56 | 2   | 617.28  | 9.45   | 0.003   | 0.18
Strength        | 456.78  | 2   | 228.39  | 3.50   | 0.036   | 0.07
Memory*Strength | 234.56  | 4   | 58.64   | 0.90   | 0.468   | 0.04
Error           | 5678.90 | 87  | 65.28   |        |         |
Total           | 7604.80 | 95  |         |        |         |
```

### Residual Diagnostics Example

```
Normality Test (Anderson-Darling):
  Statistic: 0.423
  p-value: 0.312
  Conclusion: Residuals are normally distributed (p > 0.05)

Equal Variance Test (Levene):
  Statistic: 1.85
  p-value: 0.142
  Conclusion: Homogeneity of variance assumption met (p > 0.05)

Independence Check (Run Order Plot):
  No systematic pattern observed
  Conclusion: Independence assumption met
```

## DOE Run Requirements

```yaml
minimum_episodes_per_run: 30  # Adjustable by power analysis
blocking:
  use_blocks: true
  block_variables: [map_difficulty, enemy_density]
center_points:
  count: 3-5 per design
  purpose: Test for curvature (linear vs quadratic effects)
replication:
  minimum: 2 replicates per condition
  purpose: Error estimation
randomization:
  run_order: randomized
  purpose: Control for nuisance variables
```

### DOE Run Example

```markdown
## DOE-042: 2x3 Factorial Design

### Factors
- Memory: [0.5, 0.7, 0.9]
- Strength: [0.3, 0.5]

### Design Matrix
| Run | Memory | Strength | Seed Set | Replicate |
|-----|--------|----------|----------|-----------|
| 1   | 0.5    | 0.3      | [42, ...]| 1         |
| 2   | 0.5    | 0.5      | [1337, ...]| 1       |
| 3   | 0.7    | 0.3      | [2023, ...]| 1       |
| 4   | 0.7    | 0.5      | [7890, ...]| 1       |
| 5   | 0.9    | 0.3      | [9999, ...]| 1       |
| 6   | 0.9    | 0.5      | [1111, ...]| 1       |
| 7   | 0.5    | 0.3      | [5555, ...]| 2       |
... (30 episodes per cell, 180 total episodes)

### Center Points
| Run | Memory | Strength | Seed Set |
|-----|--------|----------|----------|
| CP1 | 0.7    | 0.4      | [8888, ...]|
| CP2 | 0.7    | 0.4      | [3333, ...]|
| CP3 | 0.7    | 0.4      | [6666, ...]|
```

## Violations

```
╔══════════════════════════════════════════════════════════════════╗
║  VIOLATIONS (ZERO TOLERANCE)                                     ║
║                                                                   ║
║  - Running experiments without fixed seeds                       ║
║  - Claiming significance without ANOVA                           ║
║  - Skipping residual diagnostics                                 ║
║  - Cherry-picking results (p-hacking)                            ║
║  - Modifying raw data                                            ║
║  - Publishing findings without evidence markers                  ║
║  - Using different seeds for control vs treatment                ║
║  - Sample size < 30 per condition without justification          ║
╚══════════════════════════════════════════════════════════════════╝
```

## Integration with Other Rules

| Rule | Integration |
|------|-------------|
| R101 (PI Boundary) | PI designs experiments, analyst validates integrity |
| R102 (Audit Trail) | All findings trace back to experiment orders |
| R010 (Orchestrator) | research-analyst executes ANOVA, research-pi interprets |
