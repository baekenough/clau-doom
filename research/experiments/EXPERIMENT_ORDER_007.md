# EXPERIMENT_ORDER_007: Layer Ablation Study

> **Experiment ID**: DOE-007
> **DOE Phase**: Phase 0/1 (Architectural Ablation)
> **DOE Type**: One-Way ANOVA (Single Factor, 5 Levels)
> **Status**: ORDERED
> **Date Ordered**: 2026-02-08
> **Author**: research-pi
> **Context**: Memory-Strength thread CLOSED (DOE-005 + DOE-006 null results). Pivot to structural investigation.

---

## Hypothesis Linkage

**Hypothesis**: H-011 (from HYPOTHESIS_BACKLOG.md)

- **H-011**: Action selection architecture (L0 rules, memory heuristic, strength heuristic) has a significant effect on kill_rate performance in defend_the_center.

**Research Question**: Which architectural layers of the action selection pipeline actually contribute to kill performance? Specifically, do the memory dodge heuristic and/or the strength attack probability modulation provide any measurable improvement over bare L0 reflex rules?

**Motivation**: DOE-005 and DOE-006 both found that varying memory_weight and strength_weight produces NO significant effect on kill_rate. This raises a fundamental question: do these heuristic layers contribute at all, or does all performance come from the L0 reflex rules? An ablation study isolates the contribution of each layer by systematically enabling/disabling components.

**Reference Experiments**:
- DOE-001 (EXPERIMENT_ORDER_001.md): Baseline comparison (random vs rule_only vs full_agent). NOTE: rule_only and full_agent data collected with AMMO2 bug -- only random baseline is reliable.
- DOE-005 (EXPERIMENT_REPORT_005.md): Performance plateau at [0.7, 0.9] -- no Memory/Strength effect.
- DOE-006 (EXPERIMENT_ORDER_006.md): Re-validation at [0.3, 0.7] -- all effects non-significant (pending formal report, but outcome communicated by team lead).

---

## Experimental Design

### Design Type

Single-factor design with 5 levels (action_strategy). Each level represents a distinct architectural configuration of the action selection pipeline.

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
Layer Stack:

random:       [random choice]
L0_only:      [L0 reflex rules]
L0_memory:    [L0 reflex rules] + [memory dodge heuristic]
L0_strength:  [L0 reflex rules] + [strength attack modulation]
full_agent:   [L0 reflex rules] + [memory dodge] + [strength attack]
```

**L0 Reflex Rules** (from `rule_only_action`):
- health < 30 → move_left (flee)
- ammo == 0 → move_left (seek ammo)
- else → attack

**Memory Dodge Heuristic** (from `FullAgentAction`):
- Tracks recent health loss over a window
- If recent health loss > threshold → dodge (move_left or move_right randomly)
- Adds reactive evasion to the L0 base

**Strength Attack Modulation** (from `FullAgentAction`):
- attack_prob = 0.4 + 0.55 * strength_weight
- With probability attack_prob → attack; else → dodge randomly
- Replaces deterministic "always attack" with probabilistic decision

### Implementation Notes for research-doe-runner

The existing `glue/action_functions.py` provides `random_action()`, `rule_only_action()`, and `FullAgentAction` class. For the ablation levels L0_memory and L0_strength, the runner must create modified versions:

**L0_memory (Level 3)**:
- Use FullAgentAction with memory_weight=0.5
- **Disable** the strength modulation path: set attack_prob to a fixed 0.68 (equivalent to 0.4 + 0.55 * 0.5 = 0.675, rounded to match default behavior)
- The memory dodge heuristic remains active

**L0_strength (Level 4)**:
- Use FullAgentAction with strength_weight=0.5
- **Disable** the memory dodge path: skip the recent-health-loss check entirely
- The strength attack probability modulation remains active

**Full Agent (Level 5)**:
- Use FullAgentAction with memory_weight=0.5, strength_weight=0.5
- Both heuristics active (default configuration)

**Note**: The PI specifies WHAT each level should do. The research-doe-runner (with assistance from lang-python-expert if needed) implements HOW. If creating ablation variants requires modifying action_functions.py, that is an implementation decision for the runner.

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
| VizDoom Scenario | Defend the Center (`defend_the_center.cfg`) |
| Map | MAP01 |
| Enemy Types | Standard (as defined in scenario) |
| Available Weapons | Pistol (default) |
| Action Space | MOVE_LEFT, MOVE_RIGHT, ATTACK (3 discrete actions) |
| Episode Termination | Agent death or timeout (2100 tics = 60 seconds) |

**Note**: Same scenario as all prior experiments (DOE-001 through DOE-006) for cross-experiment comparability.

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
- DOE-001 found enormous differences between random and rule-based agents (d > 5). If architectural layers contribute meaningfully, effects should be medium or larger.

**Effect Size Expectations**: Based on DOE-001 (random vs non-random: d=6.84), the random baseline will be dramatically different from all structured approaches. The scientifically interesting comparisons are:
1. L0_only vs random (expected: LARGE, replicating DOE-001/F-003)
2. L0_memory vs L0_only (expected: UNKNOWN -- does memory help?)
3. L0_strength vs L0_only (expected: UNKNOWN -- does strength modulation help?)
4. full_agent vs L0_only (expected: UNKNOWN -- does combined pipeline help?)

---

## Seed Set

**Seed Generation Formula**: `seed_i = 4501 + i * 31` for `i = 0, 1, ..., 29`

**Verification**: All 30 seeds are unique integers (min: 4501, max: 5400, step: 31).

**Cross-Experiment Seed Collision Check**:
- DOE-001 seed range: [42, 2211] (formula: 42 + i*31, i=0..69) -- NO overlap with [4501, 5400]
- DOE-002 seed range: [1337, 1830] (formula: 1337 + i*17, i=0..29) -- NO overlap with [4501, 5400]
- DOE-005 seed range: [2501, 3168] (formula: 2501 + i*23, i=0..29) -- NO overlap with [4501, 5400]
- DOE-006 seed range: [3501, 4342] (formula: 3501 + i*29, i=0..29) -- NO overlap with [4501, 5400]
- Conclusion: Zero seed collisions across all experiments.

**Complete Seed Set (n = 30)**:

```
[4501, 4532, 4563, 4594, 4625, 4656, 4687, 4718, 4749, 4780,
 4811, 4842, 4873, 4904, 4935, 4966, 4997, 5028, 5059, 5090,
 5121, 5152, 5183, 5214, 5245, 5276, 5307, 5338, 5369, 5400]
```

**Seed Usage Rule**: ALL 5 levels use the IDENTICAL seed set (seeds[0..29]). This is critical for the ablation design: same seeds across all conditions ensures that performance differences are attributable to the action selection architecture alone, not to environmental variation.

| Run | Condition | Seeds Used |
|-----|-----------|------------|
| R1 | random | 4501, 4532, ..., 5400 (all 30) |
| R2 | L0_only | 4501, 4532, ..., 5400 (all 30) |
| R3 | L0_memory | 4501, 4532, ..., 5400 (all 30) |
| R4 | L0_strength | 4501, 4532, ..., 5400 (all 30) |
| R5 | full_agent | 4501, 4532, ..., 5400 (all 30) |

---

## Run Order

Runs are randomized to control for temporal effects. The randomized execution order is:

| Execution Order | Run | action_strategy | Type |
|----------------|-----|----------------|------|
| 1 | R4 | L0_strength | Ablation |
| 2 | R1 | random | Baseline |
| 3 | R5 | full_agent | Complete |
| 4 | R2 | L0_only | Ablation |
| 5 | R3 | L0_memory | Ablation |

**Randomization Method**: Pre-specified random permutation.

---

## Response Variables

### Response Hierarchy

**Primary analysis (confirmatory)**: kill_rate. The one-way ANOVA on kill_rate is the sole confirmatory test for H-011. Significance thresholds and effect size criteria apply to kill_rate only.

**Secondary analysis (exploratory)**: kills, survival_time, ammo_efficiency, damage_dealt. Reported at nominal p-values with effect sizes and confidence intervals for descriptive insight. These do not drive hypothesis decisions but provide mechanistic understanding of why layers help (or not).

### Primary Response

| Variable | Description | Unit | Computation |
|----------|-------------|------|-------------|
| kill_rate | Kills per minute of survival | kills/min | `kills / (survival_time / 60.0)` |

### Secondary Responses (Exploratory)

| Variable | Description | Unit | Computation |
|----------|-------------|------|-------------|
| kills | Total enemy kills per episode | integer | `experiments.kills` |
| survival_time | Time alive per episode | seconds | `experiments.survival_time` |
| ammo_efficiency | Hits / shots fired | ratio [0,1] | `experiments.hits / experiments.shots_fired` |
| damage_dealt | Total damage inflicted | HP | `experiments.damage_dealt` |

### Tracking Metrics

| Variable | Description | Purpose |
|----------|-------------|---------|
| action_distribution | Proportion of each action chosen | Verify architectural differences produce behavioral differences |
| dodge_frequency | Number of dodge actions per episode | Quantify memory and strength heuristic activation rates |

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
1. L0_only vs random (replication of DOE-001 F-003 with real data)
2. full_agent vs random (replication of DOE-001 F-001)

**Tier 2 -- Layer Contribution (Key Scientific Questions)**:
3. L0_memory vs L0_only (does memory dodge help beyond L0?)
4. L0_strength vs L0_only (does strength modulation help beyond L0?)
5. full_agent vs L0_only (does the combined pipeline help beyond L0?)

**Tier 3 -- Layer Comparison**:
6. L0_memory vs L0_strength (which heuristic contributes more?)
7. full_agent vs L0_memory (does adding strength to L0+memory help?)
8. full_agent vs L0_strength (does adding memory to L0+strength help?)

**Tier 4 -- Additive vs Synergistic**:
9. full_agent vs L0_memory + L0_strength expected (is the combination more than the sum of parts?)
10. L0_memory vs random (sanity check)

**Multiplicity Correction**: Tukey HSD controls family-wise error rate across all 10 comparisons at alpha = 0.05.

### Planned Contrasts (Orthogonal)

```
C1: random vs all others       (structured vs unstructured)
C2: L0_only vs {L0M, L0S, FULL}  (bare rules vs augmented rules)
C3: {L0M, L0S} vs FULL         (single heuristic vs combined)
C4: L0M vs L0S                 (memory heuristic vs strength heuristic)
```

These orthogonal contrasts partition the between-group SS into scientifically interpretable components.

### Non-Parametric Fallback

Based on DOE-005 experience, real VizDoom kill_rate data is typically non-normal (zero-inflated, right-skewed). Plan non-parametric methods as co-primary:

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
- [ ] All metrics within plausible ranges
- [ ] Action distribution logged to verify behavioral differentiation

During analysis:
- [ ] Normality check (Anderson-Darling) on ANOVA residuals
- [ ] Equal variance check (Levene's test) across 5 groups
- [ ] Run-order plot inspection (no systematic drift)
- [ ] Box plots for each group (visual distribution comparison)
- [ ] Kruskal-Wallis as non-parametric co-primary
- [ ] Tukey HSD pairwise comparisons with confidence intervals

---

## Expected Outcomes

### Group Mean Predictions

| Level | Expected kill_rate | Rationale |
|-------|-------------------|-----------|
| random | ~8-10 kills/min | DOE-001 random had 9.9 kills (but AMMO2 data). Real random performance unknown but expected lowest. |
| L0_only | ~8-10 kills/min | DOE-005/006 showed ~8.4 kills/min for full_agent. L0_only may be similar if heuristics add nothing. |
| L0_memory | ~8-10 kills/min | Memory dodge may improve survival but not necessarily kills. Unknown. |
| L0_strength | ~8-10 kills/min | Strength modulation changes attack probability. May increase or decrease kill_rate. Unknown. |
| full_agent | ~8-10 kills/min | DOE-005/006 baseline: ~8.4 kills/min at default parameters. |

**Honest Assessment**: DOE-005 and DOE-006 showed that varying parameters within the full_agent architecture produces no significant differences. It is entirely possible that L0_only, L0_memory, L0_strength, and full_agent ALL perform similarly (~8.4 kills/min) and only random is different. This would indicate that the L0 reflex rules dominate all behavior and the memory/strength heuristics are effectively inert in defend_the_center.

### Scenario A: Clear Layer Hierarchy

```
random << L0_only < L0_memory ~ L0_strength < full_agent
```

Implication: Each layer adds measurable value. The heuristics contribute beyond L0 rules. Future research should optimize heuristic parameters.

### Scenario B: L0 Dominance (Heuristics Inert)

```
random << L0_only ~ L0_memory ~ L0_strength ~ full_agent
```

Implication: L0 rules account for ALL structured performance. Memory dodge and strength modulation are inert in this scenario. This explains why DOE-005/006 found no parameter effects -- the parameters modulate layers that have no impact. Future research should focus on improving L0 rules or introducing genuinely different decision mechanisms.

### Scenario C: One Heuristic Matters

```
random << L0_only ~ L0_strength < L0_memory ~ full_agent
      or
random << L0_only ~ L0_memory < L0_strength ~ full_agent
```

Implication: Only one heuristic contributes. Future optimization should focus on the contributing layer.

### Scenario D: Random Is Not That Bad

```
random ~ L0_only ~ L0_memory ~ L0_strength ~ full_agent
```

Implication: In defend_the_center with real KILLCOUNT, even random performance is comparable to structured agents. The scenario is too simple to differentiate architectures. Consider testing on harder scenarios.

---

## Contingency Plans

### If Overall ANOVA Non-Significant (p > 0.10)

1. Report non-significance with confidence intervals and observed power
2. If random is visually separated but pairwise comparison is non-significant after Tukey correction, consider Dunnett's test (all vs control)
3. Compute minimum detectable effect size at power = 0.80
4. Consider: is defend_the_center too simple to differentiate architectures?
5. Plan follow-up with harder scenario (e.g., defend_the_line, my_way_home)

### If ANOVA Significant But Only Random Differs

1. Confirms Scenario B (L0 dominance)
2. Close the heuristic optimization thread
3. Pivot research to: (a) improving L0 rules, (b) introducing qualitatively different decision mechanisms, (c) testing in harder scenarios
4. Update project thesis: "RAG experience accumulation is not the primary driver of performance in simple scenarios"

### If Normality Severely Violated

1. Use Kruskal-Wallis as primary (with Dunn's post-hoc)
2. Report parametric ANOVA alongside for comparison
3. Consider rank transformation or bootstrap confidence intervals

### If High Variance Obscures Differences

1. Check for zero-inflation (proportion of zero-kill episodes per group)
2. If zero-inflation varies by group: use zero-inflated model or analyze conditional on kills > 0
3. Consider survival_time as alternative primary (may be less noisy)

---

## Cross-Experiment Comparisons

### DOE-007 vs DOE-001 (Baseline Replication)

DOE-001 tested random vs rule_only vs full_agent with 70 episodes per condition (but with AMMO2 bug for rule_only and full_agent). DOE-007 repeats the random condition with 30 episodes and CORRECT KILLCOUNT mapping:

```
DOE-001 random:      kills=9.9, SD=3.3, n=70 (AMMO2 bug present but irrelevant for random)
DOE-007 random (R1): {observed}, n=30 (correct KILLCOUNT)

Compare: If DOE-007 random ~ DOE-001 random, the random baseline is stable across experiments.
```

### DOE-007 vs DOE-005/006 (Full Agent Replication)

DOE-005 and DOE-006 used full_agent at various parameter settings. DOE-007 R5 uses full_agent at default (0.5, 0.5):

```
DOE-005 grand mean: ~8.4 kills/min (at [0.7, 0.9])
DOE-006 (0.7, 0.7): {pending} kills/min (at [0.3, 0.7])
DOE-007 R5 full_agent: {observed} kills/min (at default 0.5, 0.5)

Consistency across experiments validates measurement stability.
```

---

## DuckDB Storage

```sql
-- All episodes stored in experiments table with:
experiment_id = 'DOE-007'
-- Factor stored as:
-- action_strategy VARCHAR ('random', 'L0_only', 'L0_memory', 'L0_strength', 'full_agent')

-- Query template for group means
SELECT
    action_strategy,
    COUNT(*) as n,
    AVG(kills / (survival_time / 60.0)) as mean_kill_rate,
    STDDEV(kills / (survival_time / 60.0)) as sd_kill_rate,
    AVG(kills) as mean_kills,
    AVG(survival_time) as mean_survival,
    AVG(ammo_efficiency) as mean_ammo_eff,
    AVG(damage_dealt) as mean_damage
FROM experiments
WHERE experiment_id = 'DOE-007'
GROUP BY action_strategy
ORDER BY
    CASE action_strategy
        WHEN 'random' THEN 1
        WHEN 'L0_only' THEN 2
        WHEN 'L0_memory' THEN 3
        WHEN 'L0_strength' THEN 4
        WHEN 'full_agent' THEN 5
    END;

-- Cross-experiment random baseline comparison
SELECT
    experiment_id,
    AVG(kills) as mean_kills,
    STDDEV(kills) as sd_kills,
    COUNT(*) as n
FROM experiments
WHERE action_strategy = 'random'
  AND experiment_id IN ('DOE-001', 'DOE-007')
GROUP BY experiment_id;
```

---

## Execution Instructions for research-doe-runner

1. **Setup Phase**:
   - Verify VizDoom container running with `defend_the_center.cfg`
   - **CRITICAL**: Verify KILLCOUNT mapping reads REAL kills (not AMMO2). Run 1-2 test episodes and confirm kills vary (not constant 26).
   - Prepare action function variants for ablation levels (see Implementation Notes above)
   - Initialize DuckDB experiment_id = 'DOE-007'

2. **Action Function Preparation** (may require lang-python-expert):
   - Level 1 (random): Use existing `random_action(state)` as-is
   - Level 2 (L0_only): Use existing `rule_only_action(state)` as-is
   - Level 3 (L0_memory): Create variant of FullAgentAction with strength path disabled
   - Level 4 (L0_strength): Create variant of FullAgentAction with memory path disabled
   - Level 5 (full_agent): Use existing `FullAgentAction(0.5, 0.5)` as-is

3. **Execute in Randomized Order** (see Run Order table):
   - Execution order: R4 (L0_strength), R1 (random), R5 (full_agent), R2 (L0_only), R3 (L0_memory)
   - For each run: select the appropriate action function
   - Execute 30 episodes with seed set [4501, 4532, ..., 5400]
   - Record all metrics with action_strategy column

4. **Behavioral Verification** (CRITICAL for ablation validity):
   - After each level, spot-check action distributions:
     - random: approximately 33%/33%/33% (left/right/attack)
     - L0_only: should show high attack rate when health>30 and ammo>0
     - L0_memory: should show dodge actions after health loss events
     - L0_strength: should show attack_prob ~ 0.675
     - full_agent: should show both dodge-after-damage and probabilistic attack
   - If action distributions are IDENTICAL across L0_only, L0_memory, L0_strength, and full_agent, the ablation has FAILED -- the heuristics are not activating

5. **Validation**:
   - Verify 150 episodes recorded (30 per level x 5 levels)
   - Confirm action_strategy values match design matrix
   - Seed integrity confirmed: all levels used identical seeds
   - Verify kills values are NOT constant (AMMO2 bug regression check)

---

## Visualization Requirements

### Box Plot (Primary)
- X-axis: action_strategy (ordered: random, L0_only, L0_memory, L0_strength, full_agent)
- Y-axis: kill_rate
- Show individual data points (jittered) overlaid on box plots
- Add group means as diamond markers

### Group Means with CIs
- X-axis: action_strategy
- Y-axis: Mean kill_rate with 95% CI error bars
- Horizontal reference line at DOE-005 grand mean (~8.4 kills/min)

### Pairwise Comparison Plot
- Matrix of pairwise differences with Tukey HSD confidence intervals
- Highlight significant pairs (CI does not include 0)

### Action Distribution
- Stacked bar chart showing proportion of each action (move_left, move_right, attack) per level
- Verifies behavioral differentiation between levels

---

## Phase Transition Criteria

### If Significant Layer Effects Found

If one-way ANOVA is significant AND pairwise comparisons reveal meaningful layer contributions:
- Identify which layers contribute (memory? strength? both?)
- Design follow-up optimization experiment targeting the contributing layer(s)
- Consider factorial design if multiple layers contribute with potential interaction

### If Only Random Differs (L0 Dominance)

If ANOVA significant but only random vs others:
- Close current architecture optimization thread
- Pivot to: improved L0 rules, different decision mechanisms, harder scenarios
- Consider: the defend_the_center scenario may be too simple for the current agent architecture

### If ALL Groups Similar (No Significant Differences)

If ANOVA non-significant (all p > 0.10):
- Even random performs comparably to structured approaches
- The scenario is too simple to differentiate ANY architecture
- Mandatory pivot to harder scenarios
- This would fundamentally reshape the project thesis

---

## Audit Trail

| Document | Status |
|----------|--------|
| HYPOTHESIS_BACKLOG.md | H-011 active |
| EXPERIMENT_ORDER_007.md | This document (ORDERED) |
| EXPERIMENT_REPORT_007.md | Pending (after execution) |
| FINDINGS.md | Pending (after analysis) |
| RESEARCH_LOG.md | Entry logged (2026-02-08) |

---

## Metadata

| Property | Value |
|----------|-------|
| DOE Phase | 0/1 (Architectural Ablation) |
| Estimated Runtime | 1.5-2.5 hours (5 runs x 30 episodes each) |
| Data Volume | ~150 rows in experiments table |
| Dependencies | VizDoom container, DuckDB, action function variants |
| Predecessor Experiments | DOE-001 (baseline), DOE-005 (plateau), DOE-006 (re-validation null) |
| Potential Successors | Layer-specific optimization or scenario complexity study |
