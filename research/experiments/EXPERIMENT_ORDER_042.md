# EXPERIMENT_ORDER_042: 5-Action Strategy Comparison at doom_skill=3

## Hypothesis

H-045: Strategy performance rankings established at doom_skill=1 (DOE-035: survival_burst ≈ ar_50 >> burst_3 ≈ attack_raw) do not hold at doom_skill=3 (intermediate difficulty). Specifically, the survival_burst advantage over ar_50 diminishes or reverses under increased enemy lethality, and the movement vs no-movement gap (ar_50 vs attack_raw) contracts from d=1.408 (DOE-029) due to reduced survival time compressing kill accumulation windows.

## Research Question

At doom_skill=3 (the experimental "gold standard" difficulty), which 5-action strategy produces the best performance? DOE-035 mapped the strategy landscape at doom_skill=1, establishing survival_burst and ar_50 as co-dominant (26.8 vs 26.6 kills) with burst_3 catastrophically failing (7.5 kills). DOE-025 tested 6 strategies at doom_skill=3 but used a different strategy set (no ar_50, no attack_raw). DOE-040 (F-109) showed performance drops linearly from sk1=24.76 to sk3=17.04 kills for random_5.

This experiment bridges the gap by testing the DOE-035 strategy set at doom_skill=3. Two questions:
1. Does the strategy ranking from DOE-035 (sk1) survive at sk3?
2. Does the survival_burst paradox (F-064: survival-first maximizes kills) persist under higher enemy lethality?

## Design

- **Type**: One-Way CRD (five levels)
- **Factor**: Action Strategy
- **Scenario**: defend_the_line_5action.cfg (5 actions: MOVE_LEFT, MOVE_RIGHT, TURN_LEFT, TURN_RIGHT, ATTACK)
- **num_actions**: 5
- **doom_skill**: 3
- **Episodes per condition**: 30
- **Total episodes**: 150

## Conditions

| Run | Condition | Strategy | Attack Ratio | Description |
|-----|-----------|----------|-------------|-------------|
| R1 | random_5 | random_5 | ~20% (1/5) | Uniform random over all 5 actions. Replication anchor from DOE-025/DOE-040 at sk3. |
| R2 | ar_50 | ar_50 | 50% | p_attack=0.5, else random from {MOVE_LEFT, MOVE_RIGHT, TURN_LEFT, TURN_RIGHT}. First test at sk3. |
| R3 | dodge_burst_3 | dodge_burst_3 | 60% | 3 attacks + 2 strafes (cycle period=5). Intermediate attack/strafe gradient. From DOE-025. |
| R4 | survival_burst | survival_burst | 40% | 2 attacks + 2 strafes + 1 turn (cycle period=5). Paradoxical kill leader at both sk3 (DOE-025) and sk1 (DOE-035). |
| R5 | attack_raw | attack_raw | 100% | Always action 4 (ATTACK). No movement. Movement-absence control. First explicit test at sk3 in 5-action. |

### Strategy Rationale

- **random_5**: Baseline anchor. DOE-025 tested this at sk3 (n=30). DOE-040 provides large-sample sk3 reference (17.04 kills, n=50). Internal replication check.
- **ar_50**: Never tested at sk3. At sk1 (DOE-035), achieved 26.6 kills, co-dominant with survival_burst. The "workhorse" strategy incorporating deliberate attack mixing with movement.
- **dodge_burst_3**: Tested in DOE-025 at sk3 (n=30). Higher attack frequency (60%) than random but lower than strafe_burst_3 (75%). Provides midpoint on attack-movement gradient.
- **survival_burst**: Tested in both DOE-025 (sk3, 19.63 kills, best of 6) and DOE-035 (sk1, 26.8 kills, best of 5). The F-064 paradox — survival-first strategy maximizes kills. This experiment tests whether the paradox is robust to difficulty.
- **attack_raw**: Never tested at sk3 in 5-action space. The critical no-movement control for quantifying the movement advantage (F-079) at intermediate difficulty.

## Seed Set

Formula: seed_i = 95001 + i × 197, i = 0..29

```
[95001, 95198, 95395, 95592, 95789, 95986, 96183, 96380, 96577, 96774,
 96971, 97168, 97365, 97562, 97759, 97956, 98153, 98350, 98547, 98744,
 98941, 99138, 99335, 99532, 99729, 99926, 100123, 100320, 100517, 100714]
```

Maximum seed: 100714

All 30 seeds are shared across all 5 conditions (identical seed set for fair comparison).

## Randomized Run Order

R4, R2, R5, R1, R3

## Response Variables

| Variable | Metric | Direction |
|----------|--------|-----------|
| kills | Total enemies killed per episode | Maximize |
| survival_time | Ticks alive before death or timeout | Maximize |
| kill_rate | kills / (survival_time / 35) | Diagnostic only (see F-111 caveat) |

Note: F-111 (DOE-040) established that kill_rate conflates lethality with time scarcity and should NOT be used as a primary performance metric. Report kill_rate for cross-experiment comparison but interpret with caution.

## Analysis Plan

### Primary Analysis

One-way ANOVA: kills ~ strategy (5 levels)

| Source | df |
|--------|-----|
| strategy (A) | 4 |
| Error | 145 |
| Total | 149 |

### Planned Contrasts

| ID | Contrast | Tests |
|----|----------|-------|
| C1 | Movement strategies (random_5, ar_50, dodge_burst_3, survival_burst) vs attack_raw | Overall movement advantage at sk3 |
| C2 | survival_burst vs ar_50 | Does survival-first paradox hold at sk3? |
| C3 | ar_50 vs random_5 | Does deliberate attack mixing outperform random at sk3? |
| C4 | dodge_burst_3 vs survival_burst | Does higher attack ratio (60% vs 40%) help or hurt at sk3? |

### Cross-Experiment Comparisons (Descriptive)

| Comparison | Source | Tests |
|------------|--------|-------|
| random_5 sk3 here vs DOE-025 random_5 sk3 | DOE-025 R1 | Internal replication (same difficulty, same strategy, different seeds) |
| survival_burst sk3 here vs DOE-025 survival_burst sk3 | DOE-025 R6 | Internal replication of the paradox |
| random_5 sk3 here vs DOE-040 random_5 sk3 | DOE-040 R2 | Cross-power replication (n=30 vs n=50) |
| Movement gap at sk3 vs DOE-029 movement gap sk3 | DOE-029 | F-079 replication with different strategies |

### Diagnostics

- Normality: Anderson-Darling on residuals
- Equal variance: Levene test
- Independence: Run order plot
- Non-parametric fallback: Kruskal-Wallis

### Effect Size Metrics

- Partial eta-squared for strategy factor
- Pairwise Cohen's d between all strategy pairs
- Compare movement gap (ar_50 vs attack_raw) to F-079 benchmark (d=1.408 at sk3)
- Compare overall η² to DOE-025 (η²=0.104) and DOE-035 (η²=0.572) to assess discrimination at sk3

## Power Analysis

- Alpha = 0.05
- With n=30 per level (5 levels, N=150):
  - Power for large effect (η²≈0.15): > 0.95
  - Power for medium effect (η²≈0.06): ≈ 0.70
  - Power for small effect (η²≈0.02): ≈ 0.35
- Prior: DOE-025 at sk3 found η²=0.104 (medium-large). If strategy effect is similar magnitude, power ≈ 0.85.

## Expected Outcomes

| Outcome | Probability | Implication |
|---------|------------|-------------|
| A: survival_burst still dominates (replicates DOE-025 F-064) | 35% | Survival-first paradox is difficulty-robust; prioritize for evolution |
| B: ar_50 overtakes survival_burst at sk3 | 25% | Rankings shift with difficulty (supports H-026); attack-mixing more valuable under pressure |
| C: Movement strategies converge (all ~17 kills) but >> attack_raw | 25% | F-077 tactical invariance extends to sk3; movement is the only lever |
| D: All strategies converge including attack_raw (F-079 contracts) | 10% | Difficulty compresses both strategy AND movement effects; sk3 less discriminating |
| E: Surprise result — dodge_burst_3 or random_5 wins | 5% | Unexpected; would require re-evaluation of strategy landscape |

## Linked Hypotheses and Findings

| ID | Type | Relevance |
|----|------|-----------|
| F-062 | Finding | 5-action strategies differentiate kills at sk3 (η²=0.104, DOE-025) |
| F-063 | Finding | 5-action strategies differentiate survival at sk3 (η²=0.111, DOE-025) |
| F-064 | Finding | Survival-first paradox: survival_burst maximizes kills (DOE-025) |
| F-077 | Finding | Tactical invariance — kills invariant to attack ratio within movement class (DOE-028) |
| F-079 | Finding | Movement is sole determinant at sk3 (d=1.408, DOE-029) |
| F-087 | Finding | 5-action space optimal (DOE-031) |
| F-097 | Finding | burst_3 catastrophically fails in 5-action at sk1 (DOE-035) |
| F-098 | Finding | Performance ceiling ~27 kills at sk1 (DOE-035) |
| F-109 | Finding | Linear difficulty gradient: sk3=17.04 kills for random_5 (DOE-040) |
| F-111 | Finding | Kill-rate paradox — not a pure performance metric (DOE-040) |
| H-026 | Hypothesis | Strategy rankings change with difficulty |
| H-028 | Hypothesis | 5-action space enables strategy differentiation (TESTED in DOE-025) |
| H-038 | Hypothesis | Best-of-breed combination produces synergistic performance (DOE-035) |

## Execution Notes

- Use VizDoom defend_the_line with 5-action configuration
- doom_skill = 3 (Normal difficulty)
- Record: kills, survival_time, shots_fired
- Compute kill_rate = kills / (survival_time / 35)
- DuckDB table: experiments.DOE_042
- Random seed consumption: 150 seeds total (30 per condition × 5 conditions)
- Follow randomized run order: R4, R2, R5, R1, R3
- Strategy implementations:
  - random_5: uniform random from {0, 1, 2, 3, 4}
  - ar_50: p_attack=0.5 (action 4), else random from {0, 1, 2, 3}
  - dodge_burst_3: cycle [ATK, ATK, ATK, STRAFE_L, STRAFE_R] (actions 4,4,4,0,1)
  - survival_burst: cycle [ATK, ATK, STRAFE_L, STRAFE_R, TURN_L] (actions 4,4,0,1,2)
  - attack_raw: always action 4 (ATTACK)

## Budget

| Item | Count |
|------|-------|
| Conditions | 5 |
| Episodes per condition | 30 |
| Total episodes | 150 |
| Cumulative project episodes | ~5940 |
