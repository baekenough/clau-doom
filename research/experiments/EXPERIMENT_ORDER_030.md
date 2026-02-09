# EXPERIMENT_ORDER_030: Difficulty Moderates Movement Dominance (2x5 Factorial)

## Metadata
- **DOE ID**: DOE-030
- **Hypothesis**: H-033
- **Design Type**: 2x5 Full Factorial
- **Phase**: 2 (Generalizability Testing)
- **Date Ordered**: 2026-02-10
- **Budget**: 300 episodes
- **Cumulative Episodes**: 5310

## Hypothesis

**H-033**: The dominance of movement as sole performance determinant (F-079, d=1.408) interacts with game difficulty (doom_skill). Specifically, movement's absolute benefit diminishes at extreme difficulties due to effect compression (F-054), but its RELATIVE importance (proportion of variance explained) may increase because non-movement agents become disproportionately worse.

### Rationale

DOE-023 showed doom_skill dominates kills variance at 72% (F-052) and strategy rankings change with difficulty (F-053). DOE-029 showed movement is the sole performance determinant in the default difficulty (doom_skill=3). Two competing predictions:

1. **Movement-amplification**: At higher difficulties, enemies are faster and deal more damage. Movement becomes MORE critical for survival (dodging projectiles), so the movement vs no-movement gap WIDENS in relative terms.
2. **Compression-dominance**: Effect compression (F-054, 5.2x shrinkage from Easy to Nightmare) reduces ALL effect sizes. The movement vs no-movement gap shrinks in ABSOLUTE terms, potentially becoming non-significant at Nightmare.

This experiment tests which prediction holds. The interaction between movement and doom_skill directly tests the GENERALIZABILITY of our central finding (F-079).

### Research Value

- Tests whether F-079 (movement dominance) is a universal law or a difficulty-specific artifact
- Extends the DOE-023 difficulty investigation with the more precise movement/no-movement contrast (instead of 4 strategy levels)
- Provides the doom_skill interaction term needed for the paper's generalizability claims

## Factors

| Factor | Levels | Type | Description |
|--------|--------|------|-------------|
| movement | 2 | Fixed | Whether agent performs lateral movement |
| doom_skill | 5 | Fixed | VizDoom difficulty (1-5) |

### Factor Levels

**movement** (2 levels):
- `present`: Random 50% attack / 50% movement strategy (random_50 from DOE-029). Actions 0-4 with p(attack)=0.5.
- `absent`: Pure attack (always action 4). No movement at all (pure_attack from DOE-029).

**doom_skill** (5 levels):
- 1 = I'm Too Young to Die (easiest)
- 2 = Hey, Not Too Rough
- 3 = Hurt Me Plenty (default, all prior DOEs)
- 4 = Ultra-Violence
- 5 = Nightmare! (hardest, enemies respawn)

### Why 5 Levels for doom_skill

DOE-023 tested only 3 levels {1, 3, 5}. The full 5-level gradient enables:
1. Detection of non-linear difficulty effects (quadratic curvature)
2. More precise identification of where effect compression begins
3. Better statistical power for the interaction term (more df)

### Action Space

5-action space (defend_the_line_5action.cfg): MOVE_LEFT(0), MOVE_RIGHT(1), TURN_LEFT(2), TURN_RIGHT(3), ATTACK(4).

Using 5-action for consistency with DOE-025 through DOE-029 findings.

## Response Variables

| Variable | Metric | Direction |
|----------|--------|-----------|
| kills | Total enemies killed per episode | Maximize |
| survival_time | Ticks alive before death or timeout | Maximize |
| kill_rate | kills / (survival_time / 35) | Maximize |

## Design Matrix

| Run | movement | doom_skill | Code | Episodes | Seeds |
|-----|----------|-----------|------|----------|-------|
| R01 | present | 1 | move_sk1 | 30 | 53001+i*139 |
| R02 | present | 2 | move_sk2 | 30 | 53001+i*139 |
| R03 | present | 3 | move_sk3 | 30 | 53001+i*139 |
| R04 | present | 4 | move_sk4 | 30 | 53001+i*139 |
| R05 | present | 5 | move_sk5 | 30 | 53001+i*139 |
| R06 | absent | 1 | stat_sk1 | 30 | 53001+i*139 |
| R07 | absent | 2 | stat_sk2 | 30 | 53001+i*139 |
| R08 | absent | 3 | stat_sk3 | 30 | 53001+i*139 |
| R09 | absent | 4 | stat_sk4 | 30 | 53001+i*139 |
| R10 | absent | 5 | stat_sk5 | 30 | 53001+i*139 |

### Seed Set (n=30, shared across all runs)

Formula: seed_i = 53001 + i * 139, for i = 0, 1, ..., 29

```
[53001, 53140, 53279, 53418, 53557, 53696, 53835, 53974, 54113, 54252,
 54391, 54530, 54669, 54808, 54947, 55086, 55225, 55364, 55503, 55642,
 55781, 55920, 56059, 56198, 56337, 56476, 56615, 56754, 56893, 57032]
```

Maximum seed: 57032

### Randomized Run Order

R07, R03, R10, R01, R05, R08, R02, R09, R04, R06

## Analysis Plan

### Primary Analysis

Two-way ANOVA: movement (2) x doom_skill (5)

| Source | df |
|--------|-----|
| movement (A) | 1 |
| doom_skill (B) | 4 |
| A x B (interaction) | 4 |
| Error | 290 |
| Total | 299 |

Key tests:
1. **Main effect of movement**: Replication of F-079 across all difficulties
2. **Main effect of doom_skill**: Replication of F-052 (doom_skill dominance)
3. **Interaction A x B**: Does movement benefit vary by difficulty?

### Planned Contrasts

| ID | Contrast | Tests |
|----|----------|-------|
| C1 | Movement present vs absent (collapsed across doom_skill) | Overall movement effect |
| C2 | Linear trend of doom_skill | Monotonic difficulty effect |
| C3 | Quadratic trend of doom_skill | Curvature in difficulty response |
| C4 | Movement x Linear doom_skill | Does movement benefit change linearly with difficulty? |
| C5 | Movement x Quadratic doom_skill | Non-linear interaction |

### Diagnostics

- Normality: Anderson-Darling on residuals
- Equal variance: Levene test (important: variance may differ by doom_skill)
- Independence: Run order plot
- Non-parametric fallback: Kruskal-Wallis per doom_skill level

### Effect Size Metrics

- Partial eta-squared for each ANOVA term
- Cohen's d for movement effect at EACH doom_skill level separately
- Comparison of d values across difficulties (does d shrink?)

## Power Analysis

- Alpha = 0.05
- From DOE-029: movement effect d = 1.408 (massive)
- From DOE-023: doom_skill x strategy interaction eta2 = 0.028
- With n=30 per cell (10 cells, N=300):
  - Power for movement main effect (d=1.4): > 0.99
  - Power for doom_skill main effect (eta2=0.72): > 0.99
  - Power for interaction (eta2=0.028): approximately 0.85
- Sample size adequate for all terms of interest

## Execution Instructions for research-doe-runner

1. Use defend_the_line_5action.cfg for all runs
2. Set doom_skill parameter via VizDoomBridge(doom_skill=X)
3. For "present" movement: use random_50 action function (p_attack=0.5, else random 0-3)
4. For "absent" movement: use pure_attack action function (always action 4)
5. No health override for either condition (DOE-029 showed override is null)
6. Record kills, survival_time (ticks), and compute kill_rate = kills / (survival_time / 35)
7. 30 episodes per cell, all cells use same seed set
8. Follow randomized run order: R07, R03, R10, R01, R05, R08, R02, R09, R04, R06

## Expected Outcomes

| Outcome | Probability | Implication |
|---------|------------|-------------|
| A: Interaction significant, movement d increases with difficulty | 40% | Movement is MORE critical at hard difficulties (amplification) |
| B: Interaction significant, movement d decreases with difficulty | 30% | Effect compression dominates; F-079 is difficulty-specific |
| C: No interaction, movement dominant at all levels | 25% | F-079 is universal; movement is THE fundamental determinant |
| D: Movement effect disappears at extreme difficulties | 5% | F-079 is an artifact of default difficulty |

## Cross-References

- F-079: Movement sole determinant (DOE-029, d=1.408)
- F-052: doom_skill explains 72% variance (DOE-023)
- F-053: Strategy rankings change with difficulty (DOE-023)
- F-054: Effect compression 5.2x from Easy to Nightmare (DOE-023)
- F-082: Rate-time compensation breaks at movement boundary (DOE-029)
