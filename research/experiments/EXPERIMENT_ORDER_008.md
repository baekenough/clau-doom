# EXPERIMENT_ORDER_008: Layer Ablation Study on defend_the_line

> **Experiment ID**: DOE-008
> **DOE Phase**: Phase 0/1 (Architectural Ablation -- Scenario Replication)
> **DOE Type**: One-Way ANOVA (Single Factor, 5 Levels)
> **Status**: ORDERED
> **Date Ordered**: 2026-02-08
> **Author**: research-pi
> **Context**: DOE-007 found NO significant architectural differences on defend_the_center (Scenario D: too simple, 0-3 kills/episode). Replicate on defend_the_line for better discriminability.

---

## Hypothesis Linkage

**Hypothesis**: H-012 (from HYPOTHESIS_BACKLOG.md)

- **H-012**: The defend_the_line scenario, with its higher kill ceiling and more varied gameplay, will reveal statistically significant performance differences between action architecture levels that the simpler defend_the_center scenario (DOE-007, Scenario D) could not detect.

**Research Question**: Does switching to a higher-discriminability scenario (defend_the_line: 6-17 kills/episode vs defend_the_center: 0-3 kills/episode) uncover architectural effects that were masked by floor/ceiling compression in DOE-007?

**Motivation**: DOE-007 produced a clear Scenario D result: all 5 architectural configurations (random through full_agent) were statistically indistinguishable on defend_the_center. The analyst identified low kill counts (0-3 per episode) as a key limitation. Quick testing on defend_the_line shows 6-17 kills per episode, providing approximately 5x the dynamic range. If architectural differences exist but were undetectable on defend_the_center, defend_the_line should reveal them.

**Reference Experiments**:
- DOE-007 (EXPERIMENT_ORDER_007.md, EXPERIMENT_REPORT_007.md): Same 5-level ablation on defend_the_center. F(4,145)=1.579, p=0.183 -- NOT significant.
- DOE-001 (EXPERIMENT_ORDER_001.md): Baseline comparison (random vs rule_only vs full_agent) on defend_the_center.
- DOE-005, DOE-006: Memory/Strength parameter effects null on defend_the_center with real KILLCOUNT.

---

## Experimental Design

### Design Type

Single-factor design with 5 levels (action_strategy). Identical factor structure to DOE-007, changed scenario only. This is a direct replication with one controlled change (scenario), enabling paired comparison of scenario discriminability.

- 1 factor: action_strategy (categorical, 5 levels)
- 30 episodes per level
- Total: 5 x 30 = 150 episodes
- Analysis: One-way ANOVA with Tukey HSD post-hoc

### Factor Definition

| Factor | Symbol | Type | Levels | Unit |
|--------|--------|------|--------|------|
| action_strategy | A | Categorical | 5 (see below) | architectural configuration |

### Factor Levels

| Level | Label | Code | Description | Implementation |
|-------|-------|------|-------------|----------------|
| 1 | random | RND | Uniform random choice among 3 actions | `random_action(state)` |
| 2 | L0_only | L0 | Pure deterministic reflex rules | `rule_only_action(state)` |
| 3 | L0_memory | L0M | L0 rules + memory dodge heuristic, fixed 68% attack prob | `FullAgentAction(memory_weight=0.5, strength_weight=0.5)` with strength path disabled, attack_prob fixed at 0.68 |
| 4 | L0_strength | L0S | L0 rules + strength attack probability, no memory dodge | `FullAgentAction(memory_weight=0.5, strength_weight=0.5)` with memory path disabled |
| 5 | full_agent | FULL | L0 + memory + strength heuristics (complete pipeline) | `FullAgentAction(memory_weight=0.5, strength_weight=0.5)` |

### Architectural Layer Decomposition

```
Layer Stack (identical to DOE-007):

random:       [random choice]
L0_only:      [L0 reflex rules]
L0_memory:    [L0 reflex rules] + [memory dodge heuristic]
L0_strength:  [L0 reflex rules] + [strength attack modulation]
full_agent:   [L0 reflex rules] + [memory dodge] + [strength attack]
```

**L0 Reflex Rules** (from `rule_only_action`):
- health < 30 -> move_left (flee)
- ammo == 0 -> move_left (seek ammo)
- else -> attack

**Memory Dodge Heuristic** (from `FullAgentAction`):
- Tracks recent health loss over a window
- If recent health loss > threshold -> dodge (move_left or move_right randomly)
- Adds reactive evasion to the L0 base

**Strength Attack Modulation** (from `FullAgentAction`):
- attack_prob = 0.4 + 0.55 * strength_weight
- With probability attack_prob -> attack; else -> dodge randomly
- Replaces deterministic "always attack" with probabilistic decision

### Implementation Notes for research-doe-runner

**Scenario Change**: Use `defend_the_line.cfg` and `defend_the_line.wad` instead of `defend_the_center.cfg`. Same action space (TURN_LEFT, TURN_RIGHT, ATTACK) and same game variables (KILLCOUNT, HEALTH, AMMO2).

**Episode Timeout**: defend_the_line.cfg does NOT specify episode_timeout. Set episode_timeout = 2100 ticks (= 60 seconds at 35 ticks/sec) in code to match defend_the_center duration.

**CRITICAL -- shots_fired Tracking Broken**: In defend_the_line, AMMO2 INCREASES over time (possibly due to ammo pickups or scenario design). This means shots_fired computation (initial_ammo - current_ammo) will produce negative values. **DO NOT use shots_fired or ammo_efficiency as response variables.** Record raw AMMO2 values for documentation but exclude from analysis.

**Action function implementations**: Reuse the ablation variants created for DOE-007. No changes needed to action_functions.py.

### Design Matrix

| Run | action_strategy | Code | Episodes | Seed Set |
|-----|----------------|------|----------|----------|
| R1 | random | RND | 30 | seeds[0..29] |
| R2 | L0_only | L0 | 30 | seeds[0..29] |
| R3 | L0_memory | L0M | 30 | seeds[0..29] |
| R4 | L0_strength | L0S | 30 | seeds[0..29] |
| R5 | full_agent | FULL | 30 | seeds[0..29] |

**Total Episodes**: 5 x 30 = 150

**Key Design Feature**: All 5 levels use the IDENTICAL seed set (seeds[0..29]). This ensures identical map layouts, enemy spawns, and initial conditions across all conditions. Any observed performance difference is attributable solely to the action selection architecture.

---

## Scenario

| Property | Value |
|----------|-------|
| VizDoom Scenario | Defend the Line (`defend_the_line.cfg` / `defend_the_line.wad`) |
| Map | MAP01 |
| Enemy Types | Standard (as defined in scenario) |
| Available Weapons | Pistol (default) |
| Action Space | TURN_LEFT, TURN_RIGHT, ATTACK (3 discrete actions) |
| Episode Termination | Agent death or timeout (2100 ticks = 60 seconds) |
| Expected Kill Range | 6-17 kills per episode (from quick test) |

**Differences from defend_the_center**:
- Enemies approach from a LINE in front of the agent (not surrounding)
- Higher kill counts (6-17 vs 0-3 per episode)
- More varied gameplay provides better discriminability for architectural comparisons
- Same action space and game variables, enabling direct comparison with DOE-007

---

## Sample Size

| Property | Value |
|----------|-------|
| Factor levels | 5 |
| Episodes per level | 30 |
| Grand total episodes | 150 |
| Power target | 0.80 (1 - beta) |
| Significance level | alpha = 0.05 |
| Target effect size | f = 0.25 (medium, for one-way ANOVA) |
| df_between | 4 |
| df_within | 145 |

**Power Justification**: For a one-way ANOVA with k=5 groups, n=30 per group:
- Power for medium effect (f = 0.25): approximately 0.83 [STAT:power=0.83]
- Power for large effect (f = 0.40): approximately 0.99 [STAT:power=0.99]

**Effect Size Expectations**: With the higher kill range (6-17 vs 0-3), variance from actual game performance differences should be more detectable. If architectural layers contribute meaningful performance differences, the wider response range in defend_the_line should make effects at least medium-sized (f >= 0.25).

**DOE-007 Comparison**: DOE-007 had observed power of only 0.49 at f=0.209. The wider kill range in defend_the_line should either produce larger effect sizes (making them detectable) or confirm that architectures truly do not differ (replication of null across scenarios strengthens the conclusion).

---

## Seed Set

**Seed Generation Formula**: `seed_i = 6001 + i * 37` for `i = 0, 1, ..., 29`

**Verification**: All 30 seeds are unique integers (min: 6001, max: 7074, step: 37).

**Cross-Experiment Seed Collision Check**:
- DOE-001 seed range: [42, 2211] (formula: 42 + i*31, i=0..69) -- NO overlap with [6001, 7074]
- DOE-002 seed range: [1337, 1830] (formula: 1337 + i*17, i=0..29) -- NO overlap with [6001, 7074]
- DOE-005 seed range: [2501, 3168] (formula: 2501 + i*23, i=0..29) -- NO overlap with [6001, 7074]
- DOE-006 seed range: [3501, 4342] (formula: 3501 + i*29, i=0..29) -- NO overlap with [6001, 7074]
- DOE-007 seed range: [4501, 5400] (formula: 4501 + i*31, i=0..29) -- NO overlap with [6001, 7074]
- Conclusion: Zero seed collisions across all experiments.

**Complete Seed Set (n = 30)**:

```
[6001, 6038, 6075, 6112, 6149, 6186, 6223, 6260, 6297, 6334,
 6371, 6408, 6445, 6482, 6519, 6556, 6593, 6630, 6667, 6704,
 6741, 6778, 6815, 6852, 6889, 6926, 6963, 7000, 7037, 7074]
```

**Seed Usage Rule**: ALL 5 levels use the IDENTICAL seed set (seeds[0..29]). Same rationale as DOE-007: isolate the effect of action selection architecture from environmental variation.

| Run | Condition | Seeds Used |
|-----|-----------|------------|
| R1 | random | 6001, 6038, ..., 7074 (all 30) |
| R2 | L0_only | 6001, 6038, ..., 7074 (all 30) |
| R3 | L0_memory | 6001, 6038, ..., 7074 (all 30) |
| R4 | L0_strength | 6001, 6038, ..., 7074 (all 30) |
| R5 | full_agent | 6001, 6038, ..., 7074 (all 30) |

---

## Run Order

Runs are randomized to control for temporal effects. The randomized execution order is:

| Execution Order | Run | action_strategy | Type |
|----------------|-----|----------------|------|
| 1 | R3 | L0_memory | Ablation |
| 2 | R5 | full_agent | Complete |
| 3 | R1 | random | Baseline |
| 4 | R4 | L0_strength | Ablation |
| 5 | R2 | L0_only | Ablation |

**Randomization Method**: Pre-specified random permutation (different from DOE-007 order to avoid systematic confound).

---

## Response Variables

### Response Hierarchy

**Primary analysis (confirmatory)**: kill_rate. The one-way ANOVA on kill_rate is the sole confirmatory test for H-012. Significance thresholds and effect size criteria apply to kill_rate only.

**Secondary analysis (exploratory)**: kills, survival_time. Reported at nominal p-values with effect sizes and confidence intervals for descriptive insight. These do not drive hypothesis decisions but provide mechanistic understanding.

**EXCLUDED**: shots_fired and ammo_efficiency are NOT reliable for defend_the_line because AMMO2 increases instead of decreasing. Do NOT compute or analyze these variables.

### Primary Response

| Variable | Description | Unit | Computation |
|----------|-------------|------|-------------|
| kill_rate | Kills per minute of survival | kills/min | `kills / (survival_time / 60.0)` |

### Secondary Responses (Exploratory)

| Variable | Description | Unit | Computation |
|----------|-------------|------|-------------|
| kills | Total enemy kills per episode | integer | `experiments.kills` (from KILLCOUNT game variable) |
| survival_time | Time alive per episode | seconds | `experiments.survival_time` |

### Tracking Metrics

| Variable | Description | Purpose |
|----------|-------------|---------|
| action_distribution | Proportion of each action chosen | Verify architectural differences produce behavioral differences |
| dodge_frequency | Number of dodge actions per episode | Quantify memory and strength heuristic activation rates |
| raw_ammo2 | Raw AMMO2 game variable value | Documentation only -- do NOT use for analysis |

---

## Statistical Analysis Plan

### Primary Analysis: One-Way ANOVA on kill_rate (Confirmatory)

```
Source          | df  | Expected
----------------|-----|----------
action_strategy | 4   | Significant if architectural layers affect kill_rate
Error           | 145 | (150 - 5)
Total           | 149 |
```

**Parameters**:
- Type I Sum of Squares (balanced design, all cell sizes equal)
- alpha = 0.05

### Post-Hoc Comparisons: Tukey HSD (If ANOVA Significant)

The 10 pairwise comparisons, with scientifically motivated grouping:

**Tier 1 -- Baseline Separation (Expected Large)**:
1. L0_only vs random (does L0 outperform random on defend_the_line?)
2. full_agent vs random (does the full pipeline beat random?)

**Tier 2 -- Layer Contribution (Key Scientific Questions)**:
3. L0_memory vs L0_only (does memory dodge help beyond L0?)
4. L0_strength vs L0_only (does strength modulation help beyond L0?)
5. full_agent vs L0_only (does the combined pipeline help beyond L0?)

**Tier 3 -- Layer Comparison**:
6. L0_memory vs L0_strength (which heuristic contributes more?)
7. full_agent vs L0_memory (does adding strength to L0+memory help?)
8. full_agent vs L0_strength (does adding memory to L0+strength help?)

**Tier 4 -- Additive vs Synergistic**:
9. full_agent vs expected additive combination (is combination more than sum of parts?)
10. L0_memory vs random (sanity check)

**Multiplicity Correction**: Tukey HSD controls family-wise error rate across all 10 comparisons at alpha = 0.05.

### Planned Contrasts (Orthogonal)

```
C1: random vs all others       (structured vs unstructured)
C2: L0_only vs {L0M, L0S, FULL}  (bare rules vs augmented rules)
C3: {L0M, L0S} vs FULL         (single heuristic vs combined)
C4: L0M vs L0S                 (memory heuristic vs strength heuristic)
```

These orthogonal contrasts partition the between-group SS into scientifically interpretable components. Identical structure to DOE-007 for direct comparison.

### Non-Parametric Fallback

Based on DOE-005/006/007 experience, real VizDoom kill_rate data may be non-normal (zero-inflated, right-skewed). However, with the higher kill range (6-17), zero-inflation should be much less of an issue. Plan non-parametric methods as co-primary regardless:

**If normality fails (Anderson-Darling p < 0.05)**:
- Kruskal-Wallis test (non-parametric one-way ANOVA)
- Dunn's test for post-hoc pairwise comparisons (Holm correction)
- Report both parametric and non-parametric results

### Residual Diagnostics

- [ ] Normality: Anderson-Darling test on ANOVA residuals (p > 0.05 required)
- [ ] Equal variance: Levene's test across 5 groups (p > 0.05 required)
- [ ] Independence: Run-order plot (no systematic pattern)
- [ ] Outlier check: Studentized residuals > |3| flagged

### Effect Sizes

| Effect | Measure | Interpretation |
|--------|---------|---------------|
| Overall ANOVA | eta-squared | Small (0.01), Medium (0.06), Large (0.14) |
| Overall ANOVA | omega-squared | More conservative than eta-squared |
| Pairwise (Tukey) | Cohen's d | < 0.20 negligible, 0.20-0.49 small, 0.50-0.79 medium, >= 0.80 large |

### Power Analysis

| Effect Size | Power (k=5, n=30) |
|-------------|-------------------|
| f = 0.10 (small) | ~0.18 |
| f = 0.25 (medium) | ~0.83 |
| f = 0.40 (large) | ~0.99 |

If the primary ANOVA is non-significant, report observed power and minimum detectable effect size at power = 0.80.

### Reporting Format

```
[STAT:f] F(4,145) = {value}  (overall ANOVA)
[STAT:p] p = {value}
[STAT:eta2] eta^2 = {value}
[STAT:ci] 95% CI for mean difference: [{lower}, {upper}] (pairwise)
[STAT:effect_size] Cohen's d = {value}  (pairwise)
[STAT:n] n = 30 per level, 150 total
[STAT:power] observed power = {value}
```

---

## Diagnostics Checklist

Before analysis:
- [ ] All 150 episodes completed without container crash
- [ ] Seed integrity: all 5 levels used identical seed set
- [ ] Action strategy verified: each level uses correct action function
- [ ] KILLCOUNT mapping confirmed as real kills (not AMMO2)
- [ ] No duplicate episode IDs
- [ ] All metrics within plausible ranges (kills expected 6-17 per episode)
- [ ] Action distribution logged to verify behavioral differentiation
- [ ] Episode timeout set to 2100 ticks (60 seconds)
- [ ] Scenario is defend_the_line.cfg (NOT defend_the_center.cfg)

During analysis:
- [ ] Normality check (Anderson-Darling) on ANOVA residuals
- [ ] Equal variance check (Levene's test) across 5 groups
- [ ] Run-order plot inspection (no systematic drift)
- [ ] Box plots for each group (visual distribution comparison)
- [ ] Kruskal-Wallis as non-parametric co-primary
- [ ] Tukey HSD pairwise comparisons with confidence intervals
- [ ] DO NOT analyze shots_fired or ammo_efficiency

---

## Expected Outcomes

### Kill Range Improvement

| Property | defend_the_center (DOE-007) | defend_the_line (DOE-008) |
|----------|-----------------------------|---------------------------|
| Kill range | 0-3 per episode | 6-17 per episode (expected) |
| Dynamic range | ~3 kills | ~11 kills |
| Discriminability | Very poor | Much better |
| Zero-kill episodes | 14/150 (9.3%) | Expected near 0% |

### Group Mean Predictions

| Level | Expected kill_rate | Rationale |
|-------|-------------------|-----------|
| random | Lower than structured | With more targets available, random should waste more opportunities |
| L0_only | Moderate-high | Pure attack rules should perform well against line of enemies |
| L0_memory | Similar to L0_only or higher | Dodge heuristic may help avoid damage, extending survival |
| L0_strength | Similar to L0_only | Attack probability modulation may be less relevant with more targets |
| full_agent | Unknown | DOE-007 showed worst performance; may repeat or differ on new scenario |

### Scenario A: Significant Differences Detected

```
random << L0_only < L0_memory ~ L0_strength < full_agent
   or any ordering with significant separation
```

Implication: defend_the_center was genuinely too simple. Architectural layers DO contribute when the scenario provides sufficient dynamic range. This reopens the optimization thread for heuristic parameters.

### Scenario B: L0 Dominance (Same as DOE-007)

```
random << L0_only ~ L0_memory ~ L0_strength ~ full_agent
```

Implication: L0 rules dominate regardless of scenario complexity. The heuristic layers are truly inert. The research program should pivot to improving L0 rules or introducing qualitatively different mechanisms.

### Scenario C: Full Replication of DOE-007 Null

```
random ~ L0_only ~ L0_memory ~ L0_strength ~ full_agent
```

Implication: Even with better discriminability, no architecture differences are detectable. This would strongly suggest that the current action space (3 actions: turn_left, turn_right, attack) is too limited for architectural complexity to matter. Consider expanding the action space.

### Scenario D: Full Agent Paradox Repeats

```
L0_only > L0_memory ~ L0_strength > full_agent
```

Implication: Combined heuristics are counterproductive across scenarios. The memory dodge and strength attack modulation interfere with basic L0 attack behavior. This would indicate a design flaw in the heuristic layers.

---

## Contingency Plans

### If Overall ANOVA Significant (p < 0.05)

1. Report full Tukey HSD pairwise comparisons
2. Identify which contrasts (C1-C4) are significant
3. Compute effect sizes for all pairwise comparisons
4. Compare effect sizes to DOE-007 (same comparisons, different scenario)
5. Design follow-up optimization experiment targeting contributing layers
6. Update FINDINGS.md with new finding (H-012 supported)

### If Overall ANOVA Non-Significant (p > 0.10)

1. Report non-significance with confidence intervals and observed power
2. Combine DOE-007 and DOE-008 null results to strengthen cross-scenario conclusion
3. Compute minimum detectable effect size at power = 0.80
4. Consider: is the action space (3 actions) too limited for architectural differentiation?
5. Plan follow-up with expanded action space or fundamentally different scenarios

### If Borderline (0.05 < p < 0.10)

1. Report with appropriate caveats
2. Focus on planned contrasts (C1-C4) which have more power for specific comparisons
3. Consider whether increased n would be informative
4. Design confirmatory study if specific contrasts are significant

### If Normality Severely Violated

1. Use Kruskal-Wallis as primary (with Dunn's post-hoc)
2. Report parametric ANOVA alongside for comparison
3. Note: with kill range 6-17, zero-inflation should be minimal compared to DOE-007

---

## Cross-Experiment Comparisons

### DOE-008 vs DOE-007 (Same Design, Different Scenario)

This is the primary scientific comparison. DOE-008 replicates DOE-007's design on a different scenario to test whether the null result is scenario-specific or universal.

```
DOE-007 (defend_the_center):
  Overall ANOVA: F(4,145)=1.579, p=0.183 (NOT significant)
  Kill range: 0-3 per episode
  Group means: 6.74 (full_agent) to 9.08 (L0_only)

DOE-008 (defend_the_line):
  Overall ANOVA: {to be computed}
  Kill range: 6-17 per episode (expected)
  Group means: {to be computed}

Comparison questions:
1. Does the wider kill range produce a significant ANOVA?
2. Does the rank ordering of groups change across scenarios?
3. Does the full_agent paradox (worst performance) replicate?
4. Are the contrast patterns (C1-C4) consistent?
```

### Discriminability Metrics

Report the following to compare scenario discriminability:
- Coefficient of Variation (CV) within and between groups
- Range of group means / pooled SD
- Observed effect size (Cohen's f) -- compare to DOE-007 f=0.209

---

## DuckDB Storage

```sql
-- All episodes stored in experiments table with:
experiment_id = 'DOE-008'
-- Factor stored as:
-- action_strategy VARCHAR ('random', 'L0_only', 'L0_memory', 'L0_strength', 'full_agent')
-- scenario VARCHAR ('defend_the_line')

-- Query template for group means
SELECT
    action_strategy,
    COUNT(*) as n,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    STDDEV(kills / (survival_time / 60.0)) as sd_kill_rate,
    AVG(kills) as mean_kills,
    AVG(survival_time) as mean_survival
FROM experiments
WHERE experiment_id = 'DOE-008'
GROUP BY action_strategy
ORDER BY
    CASE action_strategy
        WHEN 'random' THEN 1
        WHEN 'L0_only' THEN 2
        WHEN 'L0_memory' THEN 3
        WHEN 'L0_strength' THEN 4
        WHEN 'full_agent' THEN 5
    END;

-- Cross-scenario comparison (DOE-007 vs DOE-008)
SELECT
    experiment_id,
    action_strategy,
    AVG(kills) as mean_kills,
    STDDEV(kills) as sd_kills,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    COUNT(*) as n
FROM experiments
WHERE experiment_id IN ('DOE-007', 'DOE-008')
GROUP BY experiment_id, action_strategy
ORDER BY experiment_id, action_strategy;
```

---

## Execution Instructions for research-doe-runner

1. **Setup Phase**:
   - Switch VizDoom scenario to `defend_the_line.cfg` / `defend_the_line.wad`
   - Set episode_timeout = 2100 ticks (60 seconds) in the game initialization code
   - **CRITICAL**: Verify KILLCOUNT mapping reads REAL kills (not AMMO2). Run 1-2 test episodes and confirm kills are in 6-17 range (not constant).
   - **CRITICAL**: Do NOT track or compute shots_fired or ammo_efficiency. AMMO2 is unreliable on defend_the_line (increases instead of decreasing).
   - Reuse action function variants from DOE-007 (no changes needed)
   - Initialize DuckDB experiment_id = 'DOE-008'

2. **Action Function Preparation** (reuse DOE-007 implementations):
   - Level 1 (random): Use existing `random_action(state)` as-is
   - Level 2 (L0_only): Use existing `rule_only_action(state)` as-is
   - Level 3 (L0_memory): Use DOE-007 variant of FullAgentAction with strength path disabled
   - Level 4 (L0_strength): Use DOE-007 variant of FullAgentAction with memory path disabled
   - Level 5 (full_agent): Use existing `FullAgentAction(0.5, 0.5)` as-is

3. **Execute in Randomized Order** (see Run Order table):
   - Execution order: R3 (L0_memory), R5 (full_agent), R1 (random), R4 (L0_strength), R2 (L0_only)
   - For each run: select the appropriate action function
   - Execute 30 episodes with seed set [6001, 6038, ..., 7074]
   - Record all metrics with action_strategy column and scenario = 'defend_the_line'

4. **Behavioral Verification** (CRITICAL for ablation validity):
   - After each level, spot-check action distributions:
     - random: approximately 33%/33%/33% (left/right/attack)
     - L0_only: should show high attack rate when health>30 and ammo>0
     - L0_memory: should show dodge actions after health loss events
     - L0_strength: should show attack_prob ~ 0.675
     - full_agent: should show both dodge-after-damage and probabilistic attack
   - If action distributions are IDENTICAL across L0_only, L0_memory, L0_strength, and full_agent, the ablation has FAILED -- the heuristics are not activating
   - **New for defend_the_line**: Verify kills are in 6-17 range. If kills are still 0-3, the scenario configuration is wrong.

5. **Validation**:
   - Verify 150 episodes recorded (30 per level x 5 levels)
   - Confirm action_strategy values match design matrix
   - Seed integrity confirmed: all levels used identical seeds
   - Verify kills values are NOT constant (AMMO2 bug regression check)
   - Verify kills are substantially higher than DOE-007 (expected 6-17 vs 0-3)
   - Verify scenario field = 'defend_the_line'

---

## Visualization Requirements

### Box Plot (Primary)
- X-axis: action_strategy (ordered: random, L0_only, L0_memory, L0_strength, full_agent)
- Y-axis: kill_rate
- Show individual data points (jittered) overlaid on box plots
- Add group means as diamond markers
- Add DOE-007 group means as reference line or overlay for cross-scenario comparison

### Group Means with CIs
- X-axis: action_strategy
- Y-axis: Mean kill_rate with 95% CI error bars
- Overlay DOE-007 means for direct comparison

### Cross-Scenario Comparison Plot
- Grouped bar chart: DOE-007 means vs DOE-008 means for each action_strategy
- Error bars: 95% CI
- Highlight significant differences

### Pairwise Comparison Plot
- Matrix of pairwise differences with Tukey HSD confidence intervals
- Highlight significant pairs (CI does not include 0)

### Action Distribution
- Stacked bar chart showing proportion of each action (turn_left, turn_right, attack) per level
- Verifies behavioral differentiation between levels

---

## Phase Transition Criteria

### If Significant Layer Effects Found

If one-way ANOVA is significant AND pairwise comparisons reveal meaningful layer contributions:
- Identify which layers contribute (memory? strength? both?)
- Compare effect patterns to DOE-007 (same layers, different scenario)
- Design follow-up optimization experiment targeting the contributing layer(s)
- Reopen parameter optimization thread for the contributing layer(s) specifically on defend_the_line

### If Only Random Differs (L0 Dominance on defend_the_line)

If ANOVA significant but only random vs others:
- Confirms L0 dominance is scenario-invariant
- Close heuristic layer investigation definitively
- Pivot to: improved L0 rules, expanded action space, fundamentally different decision mechanisms

### If Full Replication of DOE-007 Null (No Significant Differences)

If ANOVA non-significant (all p > 0.10):
- Combined DOE-007 + DOE-008 null provides strong cross-scenario evidence
- The current 3-action architecture is insufficient for differentiating decision strategies
- Consider: expanding action space, introducing new game variables, or testing fundamentally different agent architectures
- This finding significantly impacts the project thesis about RAG-based agent improvement

---

## Audit Trail

| Document | Status |
|----------|--------|
| HYPOTHESIS_BACKLOG.md | H-012 active |
| EXPERIMENT_ORDER_008.md | This document (ORDERED) |
| EXPERIMENT_REPORT_008.md | Pending (after execution) |
| FINDINGS.md | Pending (after analysis) |
| RESEARCH_LOG.md | Entry logged (2026-02-08) |

---

## Metadata

| Property | Value |
|----------|-------|
| DOE Phase | 0/1 (Architectural Ablation -- Scenario Replication) |
| Estimated Runtime | 1.5-2.5 hours (5 runs x 30 episodes each) |
| Data Volume | ~150 rows in experiments table |
| Dependencies | VizDoom container with defend_the_line.wad, DuckDB, DOE-007 action function variants |
| Predecessor Experiments | DOE-007 (same design, defend_the_center) |
| Potential Successors | Layer-specific optimization on defend_the_line, expanded action space study, or multi-scenario meta-analysis |
