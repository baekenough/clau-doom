# EXPERIMENT_ORDER_034: Exact Replication of DOE-008

## Metadata

- **DOE ID**: DOE-034
- **Hypothesis**: H-037
- **Design Type**: One-way CRD (5 levels)
- **Phase**: 3 (Replication)
- **Date Ordered**: 2026-02-10
- **Budget**: 150 episodes
- **Cumulative Episodes**: 5640

## Hypothesis

**H-037**: DOE-008 (the foundational architectural ablation result) replicates with high fidelity when re-run 26 experiments later (DOE-034 vs DOE-008) using identical seeds. Specifically, correlation between original and replication kill_rate means exceeds r=0.95, and the same factors (L0_only worst, p<0.01) maintain significance.

### Rationale

DOE-008 established three critical findings (F-010, F-011, F-012) that form the backbone of current research direction:
- **F-010**: L0_only architecture significantly worse than all others (p=0.000555)
- **F-011**: Full agent architecture exhibits unexpected performance penalty relative to single-heuristic agents
- **F-012**: defend_the_line scenario discriminates architectures; defend_the_center does not

However, DOE-008 was run early in the experimental sequence (DOE-008, now DOE-034). Between DOE-008 and DOE-034, we have executed 25 additional DOEs spanning 5,490 episodes. The research infrastructure has been refined (seed management, scenario configs, logging). There is a non-zero risk of:
- Hidden state accumulation in agent memory or environment state
- VizDoom stochasticity not being perfectly fixed by seeds
- Configuration drift in scenario files
- Subtle changes in action functions or metrics

This replication experiment tests whether DOE-008 results are REPRODUCIBLE with identical seeds after 26 experiments, confirming the integrity of our experimental infrastructure and the robustness of the founding findings.

### Research Value

- Validates DOE-008 findings as reproducible and robust (not an artifact of early-stage infrastructure quirks)
- Provides a fidelity check on VizDoom seed determinism (if perfect, r=1.0; if drift, r<0.95)
- Confirms absence of hidden state accumulation that might confound subsequent DOEs
- Serves as quality assurance for the experimental infrastructure
- Provides a benchmark for comparing effect sizes across 25 experiments

## Factors

| Factor | Levels | Type | Description |
|--------|--------|------|-------------|
| architecture | L0_only, random, L0_memory, L0_strength, full_agent | Fixed | Agent decision-making architecture |

### Factor Levels (IDENTICAL to DOE-008)

**L0_only**: Lowest-level heuristic only. Actions determined by raw sensor input without learning or memory.

**random**: Uniform random action selection from action space.

**L0_memory**: L0 heuristic with episodic memory of recent enemy positions.

**L0_strength**: L0 heuristic with learned strength estimation (crude value function).

**full_agent**: Complete multi-heuristic agent with memory, strength estimation, curiosity, and learned strategy selection.

### Action Space

5-action space (defend_the_line_5action.cfg): MOVE_LEFT(0), MOVE_RIGHT(1), TURN_LEFT(2), TURN_RIGHT(3), ATTACK(4).

## Response Variables

| Variable | Metric | Direction |
|----------|--------|-----------|
| kills | Total enemies killed per episode | Maximize |
| survival_time | Ticks alive before death or timeout | Maximize |
| kill_rate | kills / (survival_time / 35) | Maximize |

## Design Matrix

| Run | architecture | Episodes | Seeds |
|-----|-------------|----------|-------|
| R01 | L0_only | 30 | 42+i*97 |
| R02 | random | 30 | 42+i*97 |
| R03 | L0_memory | 30 | 42+i*97 |
| R04 | L0_strength | 30 | 42+i*97 |
| R05 | full_agent | 30 | 42+i*97 |

### Seed Set (n=30, shared across all runs)

Formula: seed_i = 42 + i * 97, for i = 0, 1, ..., 29

**IDENTICAL to DOE-008 seed set.**

```
[42, 139, 236, 333, 430, 527, 624, 721, 818, 915,
 1012, 1109, 1206, 1303, 1400, 1497, 1594, 1691, 1788, 1885,
 1982, 2079, 2176, 2273, 2370, 2467, 2564, 2661, 2758, 2855]
```

Maximum seed: 2855

### Randomized Run Order

R03, R01, R05, R02, R04

## Analysis Plan

### Primary Analysis

One-way ANOVA: kills ~ architecture (5 levels)

| Source | df |
|--------|-----|
| architecture (A) | 4 |
| Error | 145 |
| Total | 149 |

Key test:
1. **Main effect of architecture**: L0_only significantly worse than all others?

### Replication Comparison

**Direct comparison of means:**

| Architecture | DOE-008 Mean | DOE-034 Mean | Difference | Expected |
|-------------|-------------|-------------|-----------|----------|
| L0_only | (from report) | (to be measured) | ≤ ±1 kill | Perfect replication |
| random | (from report) | (to be measured) | ≤ ±1 kill | Perfect replication |
| L0_memory | (from report) | (to be measured) | ≤ ±1 kill | Perfect replication |
| L0_strength | (from report) | (to be measured) | ≤ ±1 kill | Perfect replication |
| full_agent | (from report) | (to be measured) | ≤ ±1 kill | Perfect replication |

**Correlation test:**
- Pearson r(DOE-008 means, DOE-034 means)
- Interpretation:
  - r > 0.95: Excellent replication, VizDoom is deterministic with seeds
  - 0.85 < r ≤ 0.95: Good replication, minor environmental drift
  - r ≤ 0.85: Poor replication, significant drift or hidden state issues

**Bland-Altman analysis:**
- Plot: (DOE-008 + DOE-034) / 2 vs (DOE-034 - DOE-008)
- Interpretation: systematic bias or heteroscedasticity across the mean range

### Diagnostics

- Normality: Anderson-Darling on residuals
- Equal variance: Levene test
- Independence: Run order plot
- Non-parametric fallback: Kruskal-Wallis (5 levels)

### Effect Size Metrics

- Partial eta-squared for architecture factor
- Pairwise Cohen's d for L0_only vs each other architecture
- Compare effect sizes to DOE-008 report (are they similar?)

## Power Analysis

- Alpha = 0.05
- From DOE-008: architecture effect (L0_only vs others) large
- With n=30 per level (5 levels, N=150):
  - Power for architecture main effect: > 0.99 (large expected effect)
  - Power to detect r=0.95 correlation (vs r=0): > 0.98

## Execution Instructions for research-doe-runner

1. Use defend_the_line_5action.cfg and doom_skill=3 (EXACT settings as DOE-008)
2. Instantiate 5 agents, each using one architecture: L0_only, random, L0_memory, L0_strength, full_agent
3. Use IDENTICAL seed set as DOE-008: [42, 139, 236, ...]
4. Record kills, survival_time (ticks), compute kill_rate = kills / (survival_time / 35)
5. 30 episodes per architecture
6. Follow randomized run order: R03, R01, R05, R02, R04

## Expected Outcomes

| Outcome | Probability | Interpretation |
|---------|------------|-----------------|
| A: Perfect replication (r > 0.95, same significance) | 60% | VizDoom is deterministic, infrastructure is robust |
| B: Good replication (r = 0.85-0.95, same significance) | 25% | Minor environmental drift, but conclusions hold |
| C: Moderate replication (r = 0.70-0.85, different significance) | 10% | Hidden state accumulation or subtle environmental shift |
| D: Poor replication (r < 0.70 or different conclusions) | 5% | Critical infrastructure issue, DOE-008 findings questionable |

## Cross-References

- F-010: L0_only significantly worse (DOE-008, p=0.000555)
- F-011: Full agent performance penalty (DOE-008)
- F-012: defend_the_line discriminates architectures, defend_the_center doesn't (DOE-008)
