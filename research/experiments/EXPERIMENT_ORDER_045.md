# EXPERIMENT_ORDER_045: Multi-Difficulty Strategy Tournament (5-Action)

## Hypothesis

H-048: Strategy performance rankings in the 5-action space change across difficulty levels on defend_the_line. Specifically, survival-oriented strategies (survival_burst) gain relative advantage at higher difficulty (doom_skill=5) where evasion matters more, while kill-focused strategies (dodge_burst_3) dominate at lower difficulty (doom_skill=1) where survival is easy. If true, no single strategy is universally optimal — the best strategy depends on difficulty context.

## Research Question

Do 5-action strategy performance rankings remain stable across difficulty levels? DOE-023 demonstrated that in the 3-action space, strategy rankings change with difficulty: adaptive_kill dropped from rank 1 to rank 3, with effect compression 5.2x from Easy to Nightmare (F-052 through F-056). The 5-action space may show different interaction patterns because: (1) strafing provides evasion advantage that matters more at high difficulty, (2) survival-first strategies may gain relative advantage at harder difficulties where staying alive is the bottleneck. This experiment creates the definitive strategy x difficulty performance map for the 5-action architecture.

### Background

Key prior findings establishing context:

- **F-109**: doom_skill explains 67.5% of kill variance. sk1=24.76, sk3=17.04, sk5=6.48 kills (DOE-040)
- **F-110**: Survival time compression 7.3x from easy to nightmare (DOE-040)
- **F-097/F-098**: At sk1, top movement strategies equivalent (~24-27 kills) (DOE-035)
- **F-052 through F-056**: Strategy rankings change with difficulty in 3-action space (DOE-023). adaptive_kill drops rank 1 to 3, effect compression 5.2x
- **F-062/F-063**: survival_burst paradoxically optimal for kills in 5-action space (DOE-025)
- **F-087**: Optimal action space is 5-7 actions (DOE-031)
- **F-084/F-086**: Movement universally beneficial d>0.9, non-monotonic benefit curve peaks at middle difficulty (DOE-030)
- **F-079**: Movement is SOLE performance determinant (d=1.408, largest in program)

### Why This Matters

DOE-023 tested strategy x difficulty in the 3-action space (TURN_LEFT, TURN_RIGHT, ATTACK). The 5-action space (adds MOVE_LEFT, MOVE_RIGHT) introduces strafing, which fundamentally changes the evasion-aggression tradeoff. At high difficulty, strafing may become the critical survival mechanism, potentially reshuffling rankings relative to the 3-action results. This experiment closes the gap by providing the 5-action counterpart to DOE-023.

## Design

- **Type**: Two-Way Factorial (Strategy x Difficulty)
- **Factor A**: Strategy (3 levels)
- **Factor B**: Difficulty / doom_skill (3 levels)
- **Scenario**: defend_the_line, 5-action space (defend_the_line_5action.cfg)
- **num_actions**: 5
- **Episodes per cell**: 30
- **Total cells**: 3 x 3 = 9
- **Total episodes**: 270

## Factors

| Factor | Type | Role | Levels | Description |
|--------|------|------|--------|-------------|
| Strategy | Categorical | Treatment | 3 | 5-action movement strategy |
| doom_skill | Ordinal | Treatment | 3 | VizDoom difficulty parameter |

### Factor A: Strategy (3 levels)

| Level | Label | Description | Prior Performance | Selection Rationale |
|-------|-------|-------------|-------------------|---------------------|
| 1 | **random_5** | Uniform random from 5 actions | Benchmark baseline across all 5-action experiments | Universal baseline; includes movement probabilistically (2/5 = 40% strafe actions) |
| 2 | **survival_burst** | Prioritize evasion (MOVE_LEFT/RIGHT), burst attack when safe | F-062/F-063: paradoxically optimal for kills in 5-action | Survival-first strategy; evasion advantage should scale with difficulty |
| 3 | **dodge_burst_3** | 3 attacks + dodge (strafe L or R alternating) | Competitive in DOE-025, high kill focus with evasion | Aggression-first with periodic evasion; balanced approach |

### Strategy Selection Rationale

**Included**:
- **random_5**: Universal baseline present in every 5-action experiment. Anchors all comparisons. Known performance across difficulty levels (F-109: 24.76 kills at sk1, 6.48 at sk5).
- **survival_burst**: Paradoxically the kill champion in 5-action space (F-062/F-063). Evasion-first design should show strongest difficulty interaction — survival advantage grows at higher difficulty.
- **dodge_burst_3**: Balanced kill-evasion hybrid. 75% attack, 25% dodge cycle. Tests whether structured aggression with evasion beats pure survival-first approach.

**Excluded**:
- **attack_only**: No movement, definitively worst in 5-action space (F-079, d=1.408). Including adds no information at any difficulty.
- **L0_only**: Consistently worst performer (F-010, F-034). Already excluded in Phase 2+.
- **predict_position**: Permanently excluded from all future experiments.

### Factor B: Difficulty / doom_skill (3 levels)

| Level | Label | doom_skill | Expected Kills (random_5) | Selection Rationale |
|-------|-------|------------|---------------------------|---------------------|
| 1 | **easy** | 1 | ~24.76 (F-109) | Performance ceiling; strategy differences maximally expressed |
| 2 | **medium** | 3 | ~17.04 (F-109) | Intermediate; non-monotonic benefit peak (F-084) |
| 3 | **nightmare** | 5 | ~6.48 (F-109) | Performance floor; survival becomes bottleneck |

### Difficulty Selection Rationale

These three levels span the full difficulty range established in DOE-040 (F-109):
- sk1 and sk5 are the endpoints where performance differences are maximized (24.76 vs 6.48 kills)
- sk3 is the inflection point where movement benefit peaks (F-084: non-monotonic curve)
- Using the same three levels as DOE-040 enables direct cross-experiment comparison

## Design Matrix

| Run | Strategy | doom_skill | Label | n | Seed Set |
|-----|----------|------------|-------|---|----------|
| R1 | random_5 | 1 | random_5 @ easy | 30 | [101001, 101224, ..., 107468] |
| R2 | random_5 | 3 | random_5 @ medium | 30 | [101001, 101224, ..., 107468] |
| R3 | random_5 | 5 | random_5 @ nightmare | 30 | [101001, 101224, ..., 107468] |
| R4 | survival_burst | 1 | survival_burst @ easy | 30 | [101001, 101224, ..., 107468] |
| R5 | survival_burst | 3 | survival_burst @ medium | 30 | [101001, 101224, ..., 107468] |
| R6 | survival_burst | 5 | survival_burst @ nightmare | 30 | [101001, 101224, ..., 107468] |
| R7 | dodge_burst_3 | 1 | dodge_burst_3 @ easy | 30 | [101001, 101224, ..., 107468] |
| R8 | dodge_burst_3 | 3 | dodge_burst_3 @ medium | 30 | [101001, 101224, ..., 107468] |
| R9 | dodge_burst_3 | 5 | dodge_burst_3 @ nightmare | 30 | [101001, 101224, ..., 107468] |

**Total**: 3 strategies x 3 difficulties x 30 episodes = 270 episodes

### Randomized Execution Order

Within each difficulty block, randomize strategy order:
- **easy (sk1)**: R4 (survival_burst) -> R7 (dodge_burst_3) -> R1 (random_5)
- **medium (sk3)**: R2 (random_5) -> R8 (dodge_burst_3) -> R5 (survival_burst)
- **nightmare (sk5)**: R9 (dodge_burst_3) -> R3 (random_5) -> R6 (survival_burst)

Difficulty block order: easy -> medium -> nightmare

## Seed Set

**Formula**: seed_i = 101001 + i x 223, i = 0, 1, ..., 29
**Range**: [101001, 107468]
**Count**: 30 seeds per cell, identical across all 9 cells (blocking on seed)

**Full seed set**:
```
[101001, 101224, 101447, 101670, 101893, 102116, 102339, 102562, 102785, 103008,
 103231, 103454, 103677, 103900, 104123, 104346, 104569, 104792, 105015, 105238,
 105461, 105684, 105907, 106130, 106353, 106576, 106799, 107022, 107245, 107468]
```

### Cross-Experiment Seed Collision Check

| Experiment | Seed Range | Collision with DOE-045? |
|-----------|------------|------------------------|
| DOE-001 through DOE-029 | [42, 52974] | NO (disjoint, max 52974 < 101001) |
| DOE-030 | [53001, 57032] | NO (disjoint) |
| DOE-031 | [57101, 61422] | NO (disjoint) |
| DOE-032 | [61501, 62977] | NO (disjoint) |
| DOE-033 through DOE-039 | [63001, 89000] est. | NO (disjoint) |
| DOE-040 | [89001, 98360] | NO (disjoint) |
| DOE-041 | [93001, 98598] | NO (disjoint) |
| DOE-042 through DOE-044 | [99001, 101000] est. | NO (101001 > 101000) |

**Verdict**: DOE-045 range [101001, 107468] is strictly above all prior and concurrent experiment maxima. Zero seed collisions guaranteed.

## Statistical Analysis Plan

### Primary Analysis: Two-Way ANOVA

**Model**: kills ~ Strategy + doom_skill + Strategy:doom_skill

**Factors**:
- Strategy (3 levels): random_5, survival_burst, dodge_burst_3 — fixed effect
- doom_skill (3 levels): 1, 3, 5 — fixed effect (treated as categorical for ANOVA, ordinal for trend)
- Strategy x doom_skill interaction — the key test

**Degrees of Freedom**:
- Strategy: df = 2
- doom_skill: df = 2
- Strategy x doom_skill: df = 4
- Error: df = 261 (270 - 9)
- Total: df = 269

### Key Questions (in priority order)

**Q1: Strategy x Difficulty Interaction** — Do strategy rankings change across difficulty?
- If significant (p < 0.05): Rankings are difficulty-dependent → different strategies optimal at different difficulties
- If NOT significant (p >= 0.05): Rankings are stable → same strategy optimal everywhere
- This is the PRIMARY research question and differentiates from DOE-023 (3-action findings)

**Q2: Strategy Main Effect** — Do strategies differ overall (collapsed across difficulty)?
- If significant: At least one strategy outperforms others on average
- Expected: YES, based on F-062/F-063 (survival_burst advantage)

**Q3: Difficulty Main Effect** — Does difficulty affect performance (collapsed across strategy)?
- If significant: YES (expected based on F-109, η² = 0.675)
- This serves as manipulation check — difficulty MUST be significant or experiment validity is questioned

### Planned Contrasts

| Contrast | Comparison | Tests | Expected |
|----------|------------|-------|----------|
| C1 | survival_burst vs random_5 (across all difficulties) | Survival-first advantage | Significant (from F-062/F-063) |
| C2 | dodge_burst_3 vs random_5 (across all difficulties) | Structured aggression advantage | Marginal |
| C3 | survival_burst vs dodge_burst_3 (at sk5 only) | Survival advantage at nightmare | Significant if interaction exists |
| C4 | Linear difficulty trend per strategy | Performance gradient shape | Linear for random_5, possibly nonlinear for survival_burst |

**Bonferroni correction**: alpha = 0.05 / 4 = 0.0125 for contrasts

### Simple Effects Analysis (if interaction significant)

If Strategy x doom_skill interaction is significant:
1. One-way ANOVA on Strategy within each doom_skill level (3 separate ANOVAs)
2. Tukey HSD pairwise at each difficulty level
3. Rank strategies at each difficulty → construct rank table
4. Compare rank table to DOE-023 3-action rank table (F-052 through F-056)

### Residual Diagnostics (R100 Compliance)

1. **Normality**: Anderson-Darling on residuals (overall and per cell)
2. **Equal variance**: Levene test across all 9 cells
3. **Independence**: Residuals vs run order within each difficulty block
4. **Outlier detection**: Studentized residuals > |3|

### If ANOVA Assumptions Violated

- Normality violation: Kruskal-Wallis per difficulty + Scheirer-Ray-Hare for interaction
- Variance heterogeneity: Welch's ANOVA per difficulty, Brown-Forsythe test
- Both: Aligned Rank Transform (ART) ANOVA
- VizDoom kill data is known to be zero-inflated and right-skewed (PI memory); plan non-parametric fallbacks

### Effect Sizes

- Partial eta-squared (η²p) for all ANOVA effects
- Cohen's d for planned contrasts and pairwise comparisons
- Generalized eta-squared for cross-experiment comparison with DOE-023

## Secondary Responses

Repeat full analysis for:
- **survival_time** (seconds survived per episode)
- **kill_rate** (kills per minute survived)

### Cross-Metric Interpretation

| Pattern | Interpretation |
|---------|---------------|
| Higher kills AND higher survival | Strategy genuinely superior |
| Higher kills BUT lower survival | Aggressive strategy burns out faster but kills more |
| Lower kills BUT higher survival | Evasion strategy survives but doesn't capitalize |
| Lower kills AND lower survival | Strategy is strictly inferior |

## Expected Outcomes

### Prediction 1: Significant Interaction (PRIMARY HYPOTHESIS)

Expected interaction pattern:

| Strategy | sk1 (easy) | sk3 (medium) | sk5 (nightmare) |
|----------|-----------|-------------|-----------------|
| random_5 | ~24.76 | ~17.04 | ~6.48 |
| survival_burst | ~26 | ~19 | ~9 |
| dodge_burst_3 | ~27 | ~17 | ~6 |

- At sk1: dodge_burst_3 > survival_burst > random_5 (all high, aggression pays)
- At sk3: survival_burst > dodge_burst_3 ≈ random_5 (evasion starts mattering)
- At sk5: survival_burst >> random_5 ≈ dodge_burst_3 (survival is bottleneck)

This would show survival_burst gaining RELATIVE advantage as difficulty increases.

### Prediction 2: No Interaction (Alternative)

If no interaction: all strategies compress proportionally with difficulty (as in rate-time compensation, F-074). This would mean the 5-action space shows the same invariance as the 3-action space for kill_rate, extending F-077 (full tactical invariance).

### Prediction 3: Difficulty Main Effect Dominates

doom_skill expected to explain >60% of variance (consistent with F-109: 67.5%). Strategy effect expected smaller (~5-15%). Interaction effect, if present, likely ~3-8%.

## Cross-Experiment Comparison Plan

### DOE-045 vs DOE-023 (3-action vs 5-action at same difficulties)

| Comparison | DOE-023 (3-action) | DOE-045 (5-action) | Test |
|------------|--------------------|--------------------|------|
| Ranking stability | Rankings changed (F-052) | Rankings TBD | Compare rank correlation |
| Effect compression | 5.2x easy to nightmare (F-054) | TBD | Compare compression ratios |
| Interaction strength | Significant | TBD | Compare η²p for interaction |
| Best strategy at sk5 | TBD | survival_burst predicted | Compare winners |

### DOE-045 vs DOE-040 (same strategies, matched difficulties)

DOE-040 used random_5 at sk1, sk3, sk5. DOE-045 adds survival_burst and dodge_burst_3 at the same difficulties. The random_5 cells in DOE-045 serve as replication of DOE-040.

## Success Criteria

### Outcome A: Interaction Confirmed — Rankings Change with Difficulty

**Condition**: Strategy x doom_skill interaction significant (p < 0.05)

**Interpretation**: Strategy performance rankings in 5-action space depend on difficulty. Different strategies are optimal at different difficulties. This parallels DOE-023 findings in 3-action space but with potentially different ranking patterns due to strafing.

**Publication Claim**: "In the 5-action space with strafing, strategy-difficulty interaction is significant. Survival-oriented strategies gain relative advantage at higher difficulties, suggesting that evasion becomes the critical capability when enemy lethality increases."

**Next Step**: Design adaptive meta-strategy that selects sub-strategy based on doom_skill level.

### Outcome B: No Interaction — Rankings Stable Across Difficulty

**Condition**: Strategy x doom_skill interaction NOT significant (p >= 0.05)

**Interpretation**: Strategy rankings are stable across difficulty in 5-action space. This contrasts with DOE-023 (3-action, interaction was significant) and would suggest that strafing provides uniform benefit regardless of difficulty.

**Publication Claim**: "In the 5-action space, strafing equalizes strategy performance across difficulty levels, unlike the 3-action space where rankings are difficulty-dependent."

**Next Step**: This finding combined with DOE-023 creates a compelling action-space x difficulty x strategy three-way narrative.

### Outcome C: Strategies Equivalent at All Difficulties

**Condition**: Strategy main effect NOT significant AND interaction NOT significant

**Interpretation**: All three 5-action movement strategies produce equivalent performance regardless of difficulty. This extends F-077 (full tactical invariance) to cross-difficulty contexts.

**Publication Claim**: "Within the class of movement-inclusive strategies, tactical choice is irrelevant in the 5-action space — only the presence of movement matters (F-079)."

**Next Step**: Closes the strategy optimization line of inquiry. Movement is the only lever, consistent with the central thesis.

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 101001 + i x 223, i=0..29 |
| No seed collisions | YES: [101001, 107468] above all prior maxima |
| n >= 30 per condition | YES: 30 episodes per cell, 9 cells, 270 total |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, variance, independence per R100 |
| Effect sizes | PLANNED: partial eta-squared, Cohen's d |
| Seeds identical across conditions | YES: same 30 seeds for all 9 cells (blocking) |
| Power adequate | YES: N=270 provides >0.90 power for medium interaction effect |

## Power Analysis

- Two-way ANOVA: 3 x 3 = 9 cells, n = 30 per cell, alpha = 0.05
- For Strategy main effect (df = 2): Power > 0.95 for medium effect (f = 0.25) with N = 270
- For doom_skill main effect (df = 2): Power > 0.99 for large effect (f = 0.40, based on F-109 η² = 0.675)
- For interaction (df = 4): Power > 0.85 for medium effect (f = 0.25)
- For small interaction (f = 0.15): Power ≈ 0.60 — marginal, but interaction is exploratory

## Execution Notes

- Use VizDoom defend_the_line with 5-action set (defend_the_line_5action.cfg)
- doom_skill conditions: 1 (easy/minimum), 3 (medium), 5 (nightmare/maximum)
- Strategy implementations must match prior 5-action experiments (DOE-025, DOE-035, DOE-040)
- Record: kills, survival_time, kill_rate, ammo_efficiency, shots_fired
- DuckDB table: experiments.DOE_045
- Random seed consumption: 270 seeds total (30 seeds x 9 cells, same 30 seeds reused across cells)

## Audit Trail

| Document | Status | Owner |
|----------|--------|-------|
| H-048 in HYPOTHESIS_BACKLOG.md | ACTIVE | research-pi |
| EXPERIMENT_ORDER_045.md | ORDERED | research-pi |
| EXPERIMENT_REPORT_045.md | PENDING | research-analyst |
| FINDINGS.md update | PENDING | research-pi |
| RESEARCH_LOG.md update | PENDING | research-pi |

## Linked Findings

- F-052: doom_skill explains 72% of kills variance (DOE-023, 3-action)
- F-054: Effect compression 5.2x from Easy to Nightmare (DOE-023, 3-action)
- F-062/F-063: survival_burst paradoxically optimal for kills in 5-action (DOE-025)
- F-074: Rate-time compensation is fundamental environment constraint
- F-077: Full tactical invariance in 5-action space (same difficulty)
- F-079: Movement is SOLE performance determinant (d=1.408)
- F-084/F-086: Movement benefit non-monotonic, peaks at middle difficulty (DOE-030)
- F-087: Optimal action space is 5-7 actions (DOE-031)
- F-097/F-098: At sk1, top movement strategies equivalent (DOE-035)
- F-109: doom_skill explains 67.5% of kill variance in 5-action (DOE-040)
- F-110: Survival time compression 7.3x from easy to nightmare (DOE-040)

## Status

**ORDERED** — Ready for execution by research-doe-runner
