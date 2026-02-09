# EXPERIMENT_ORDER_035: Best-of-Breed Configuration Tournament

## Metadata

- **DOE ID**: DOE-035
- **Hypothesis**: H-038
- **Design Type**: One-way CRD (5 levels)
- **Phase**: 3 (Synthesis)
- **Date Ordered**: 2026-02-10
- **Budget**: 150 episodes
- **Cumulative Episodes**: 5790

## Hypothesis

**H-038**: Combining independently optimized factors produces synergistic effects on absolute performance. Specifically, when all five best-of-breed configurations are evaluated in the optimal environment (5-action space, doom_skill=1, allowing clear discrimination), at least one configuration achieves kills ≥ 25, and configurations incorporating movement strategies outperform attack-only strategies by more than the independent effect sizes would predict (Cohen's d > 1.0).

### Rationale

Phases 1-2 identified multiple independent optimizations:
1. **F-087** (DOE-031): 5-action space optimal relative to 3, 7, 9 actions
2. **F-079** (DOE-029): Movement is the sole determinant (d=1.408)
3. **F-066** (DOE-025): In 5-action space, random and ar_50 are competitively equivalent
4. **F-063** (DOE-025): Survival-burst strategy produces paradoxical performance gains (survival-first prioritization)
5. **F-085** (DOE-032): doom_skill=1 (I'm Too Young to Die) is necessary for clear signal (avoids degeneracy at doom_skill=3 where all strategies converge)

DOE-035 combines these findings into a tournament comparing five "best-of-breed" candidate strategies, all evaluated in the optimal environment. This addresses three questions:
1. What is the absolute performance ceiling achievable in our current agent framework?
2. Do synergistic effects emerge from combining independently optimized factors?
3. Which strategy should serve as the baseline for Phase 4 (generation evolution and refinement)?

### Research Value

- Establishes absolute performance ceiling for the agent framework
- Tests synergy hypothesis: interaction effects from combining multiple optimizations
- Provides the best baseline for subsequent evolution and refinement experiments
- Identifies which combinations of factors yield the highest performance

## Factors

| Factor | Levels | Type | Description |
|--------|--------|------|-------------|
| strategy | random_5, ar_50, burst_3, survival_burst, attack_raw | Fixed | Behavioral strategy (all in 5-action space, doom_skill=1) |

### Factor Levels (Best-of-Breed Candidates)

**random_5**: Uniform random action from 5-action space. Baseline random control in optimal action space. From F-066 (DOE-025), random is competitive in 5-action.

**ar_50**: Standard 50% attack, 50% random movement from 5-action space. The "workhorse" strategy from Phases 1-2. Incorporates movement optimality. Expected strong performance.

**burst_3**: Burst-intensive strategy optimized for 3-action space (DOE-021). Transferred to 5-action, this tests whether strategies optimized for constrained action spaces generalize to richer action spaces.

**survival_burst**: From DOE-025 (F-063), this strategy prioritizes survival-first (maximize survival_time), then burst attacks. Paradoxically outperformed ar_50 in some analyses. Expected to maximize kills via extended survival.

**attack_raw**: Pure attack (always action 4 in 5-action space). Movement-free control. Expected to underperform ar_50 by the magnitude of F-079 (d ≈ 1.408).

### Why doom_skill=1?

DOE-032 (F-085) found that doom_skill=3 (default) exhibits convergence and degeneracy: all strategies achieve similar performance, and agent variance dominates signal. doom_skill=1 (I'm Too Young to Die) provides clear discrimination and allows absolute performance to be evaluated without ceiling effects. This is a temporary choice for this synthesis experiment; later phases will revisit the full difficulty gradient.

## Response Variables

| Variable | Metric | Direction |
|----------|--------|-----------|
| kills | Total enemies killed per episode | Maximize |
| survival_time | Ticks alive before death or timeout | Maximize |
| kill_rate | kills / (survival_time / 35) | Maximize |

## Design Matrix

| Run | strategy | Action Space | doom_skill | Config | Episodes | Seeds |
|-----|----------|-------------|-----------|--------|----------|-------|
| R01 | random_5 | 5 | 1 | defend_the_line_5action_easy.cfg | 30 | 69001+i*163 |
| R02 | ar_50 | 5 | 1 | defend_the_line_5action_easy.cfg | 30 | 69001+i*163 |
| R03 | burst_3 | 5 | 1 | defend_the_line_5action_easy.cfg | 30 | 69001+i*163 |
| R04 | survival_burst | 5 | 1 | defend_the_line_5action_easy.cfg | 30 | 69001+i*163 |
| R05 | attack_raw | 5 | 1 | defend_the_line_5action_easy.cfg | 30 | 69001+i*163 |

### Seed Set (n=30, shared across all runs)

Formula: seed_i = 69001 + i * 163, for i = 0, 1, ..., 29

```
[69001, 69164, 69327, 69490, 69653, 69816, 69979, 70142, 70305, 70468,
 70631, 70794, 70957, 71120, 71283, 71446, 71609, 71772, 71935, 72098,
 72261, 72424, 72587, 72750, 72913, 73076, 73239, 73402, 73565, 73728]
```

Maximum seed: 73728

### Randomized Run Order

R02, R05, R04, R01, R03

## Analysis Plan

### Primary Analysis

One-way ANOVA: kills ~ strategy (5 levels)

| Source | df |
|--------|-----|
| strategy (A) | 4 |
| Error | 145 |
| Total | 149 |

Key test:
1. **Main effect of strategy**: Do strategies differ significantly?
2. **Planned contrasts**: Movement vs no-movement effect at doom_skill=1

### Planned Contrasts

| ID | Contrast | Tests |
|----|----------|-------|
| C1 | Movement strategies (random_5, ar_50, burst_3, survival_burst) vs attack_raw | Overall movement advantage |
| C2 | ar_50 vs (random_5, burst_3, survival_burst) | Does deliberate attack mixing outperform random movement? |
| C3 | random_5 vs (burst_3, survival_burst) | Does strategy-specific tuning outperform baseline random? |
| C4 | burst_3 vs survival_burst | Which strategy design better transfers to 5-action space? |

### Diagnostics

- Normality: Anderson-Darling on residuals
- Equal variance: Levene test
- Independence: Run order plot
- Non-parametric fallback: Kruskal-Wallis

### Effect Size Metrics

- Partial eta-squared for strategy factor
- Pairwise Cohen's d between all strategy pairs
- Comparison to DOE-030 movement effect (d=1.408 at doom_skill=3): is d larger at doom_skill=1?

### Absolute Performance Evaluation

| Performance Metric | Success Criterion | Interpretation |
|--------------------|------------------|-----------------|
| Highest mean kills | ≥ 25 | Ceiling reached; agent framework is effective |
| ar_50 vs attack_raw | d > 1.0 | Movement synergy exceeds Phase 2 finding (super-additive) |
| burst_3 vs random_5 | d > 0.3 | Strategy design generalizes across action spaces |
| survival_burst vs ar_50 | d (either direction) | Determines best baseline for evolution |

## Power Analysis

- Alpha = 0.05
- Expected effect sizes: variable (unknown a priori due to doom_skill=1 novelty)
- With n=30 per level (5 levels, N=150):
  - Power for large effect (η²≈0.15): > 0.95
  - Power for medium effect (η²≈0.06): ≈ 0.70
  - Power for small effect (η²≈0.02): ≈ 0.35

## Execution Instructions for research-doe-runner

1. Use defend_the_line_5action.cfg with doom_skill=1 (I'm Too Young to Die, easy difficulty)
2. Ensure scenario config includes early-stage enemy spawning and relaxed difficulty parameters
3. Instantiate 5 agents, each using one strategy: random_5, ar_50, burst_3, survival_burst, attack_raw
4. For random_5: uniform random action from {0, 1, 2, 3, 4}
5. For ar_50: p_attack=0.5, else random action from {0, 1, 2, 3}
6. For burst_3: transfer the burst-3 strategy from DOE-021 to 5-action space (likely action 5 or custom burst logic)
7. For survival_burst: prioritize survival_time maximization via high movement frequency, burst on opportunity
8. For attack_raw: always action 4 (attack), no movement actions selected
9. Record kills, survival_time (ticks), compute kill_rate = kills / (survival_time / 35)
10. 30 episodes per strategy
11. Follow randomized run order: R02, R05, R04, R01, R03

## Expected Outcomes

| Outcome | Probability | Implication |
|---------|------------|-------------|
| A: ar_50 and survival_burst dominate, both > 20 kills | 40% | Phase 2 findings transfer well; movement + deliberate strategy optimal |
| B: One surprise winner (burst_3 or random_5) emerges | 30% | Action space generalization is complex; strategy tuning matters |
| C: Movement vs attack gap replicates (ar_50 vs attack_raw d > 0.9) | 50% | F-079 generalizes to doom_skill=1 |
| D: All strategies converge (kills 10-12) | 15% | doom_skill=1 may have unexpected saturation; revision needed |
| E: Highest mean < 15 kills | 5% | Unexpected ceiling or config issue |

## Cross-References

- F-063: Survival-burst paradoxical performance (DOE-025)
- F-066: random_5 competitive with deliberate strategies (DOE-025)
- F-079: Movement sole determinant (DOE-029, d=1.408)
- F-085: doom_skill=1 necessary for clear signal (DOE-032)
- F-087: 5-action space optimal (DOE-031)
