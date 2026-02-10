# EXPERIMENT_ORDER_044: Evolutionary Optimization in 5-Action Space

## Metadata

- **Experiment ID**: DOE-044
- **Hypothesis**: H-047 — Evolutionary optimization in 5-action defend_the_line discovers configurations that break tactical invariance (F-077) by exploiting the richer movement/attack parameter space
- **DOE Phase**: Phase 4 (Evolutionary Optimization)
- **Design Type**: Generational genetic algorithm with TOPSIS multi-objective fitness
- **Date Ordered**: 2026-02-10
- **Budget**: 1000 episodes maximum (5 generations × 10 genomes × 20 episodes)
- **Cumulative Episodes**: ~6800 (5010 through DOE-029, plus DOE-030 through DOE-043)

## Research Question

Can evolutionary optimization in the 5-action space (MOVE_LEFT, MOVE_RIGHT, TURN_LEFT, TURN_RIGHT, ATTACK) discover genome configurations that exceed the tactical invariance ceiling established by F-077 and F-099?

### Background

DOE-021 demonstrated that evolution in the 3-action space converges rapidly (Gen 2) to burst_3 as the global optimum, with population diversity collapsing to burst_length=3 in 9/10 genomes (F-046). This convergence was explained by tactical invariance (F-077): in the 3-action space, all movement-inclusive strategies achieve equivalent kill_rate because the action space is too constrained for meaningful differentiation.

The 5-action space is fundamentally different:

1. **Two movement modalities**: Strafing (MOVE_LEFT/MOVE_RIGHT) provides lateral displacement; turning (TURN_LEFT/TURN_RIGHT) provides rotational aiming. DOE-033 (F-094) confirmed that strafing, not turning, drives the movement effect.

2. **Two-tier performance structure**: F-100 (DOE-035) showed a clean binary split — any strategy with strafing achieves ~24-27 kills at doom_skill=1, while strategies without strafing achieve ~8-19 kills. Within the movement tier, F-099 showed tactical invariance (top 3 strategies statistically equivalent).

3. **More dimensions to optimize**: The 5-action genome has parameters DOE-021 lacked — strafe probability, strafe direction bias, forward tendency, and the balance between strafing and turning. These additional dimensions may provide room for evolution to find non-obvious combinations that the top-3 equivalence band in DOE-035 failed to differentiate (because DOE-035 used only fixed strategies, not parameter-space search).

4. **doom_skill=3 constraint**: Unlike DOE-035's sk1 (where absolute performance is high and ceiling effects may flatten differences), DOE-044 operates at sk3 where effect compression (F-054) creates a harder optimization landscape. Evolution must find robust strategies under pressure.

### Hypothesis

**H-047: 5-Action Evolutionary Optimization Breaks Tactical Invariance**

A genetic algorithm with a 5-action genome (including strafing, turning, and attack parameters) will:
1. Converge more slowly than DOE-021's 3-action evolution (>2 generations vs exactly 2)
2. Discover parameter combinations that differentiate within the movement-inclusive tier
3. Achieve kills exceeding the DOE-035 ar_50 baseline at sk3 difficulty
4. Show directional selection on strafe_probability (expected: high values selected)

Alternatively, if tactical invariance extends to the evolutionary parameter space:
- Convergence will be rapid (Gen 2-3) with no fitness improvement over random movement
- The fitness landscape is genuinely flat within the movement tier, validating F-077 as a hard constraint

## Genome Representation

Each genome encodes a 5-action agent behavior as 8 continuous/discrete parameters:

```
Genome = {
  attack_probability:      float [0.20 .. 0.80]   # Probability of choosing ATTACK on each tick
  strafe_probability:      float [0.00 .. 0.50]    # Probability of strafing (MOVE_LEFT or MOVE_RIGHT) vs turning
  strafe_direction_bias:   float [-1.0 .. 1.0]     # -1.0 = always left, 0.0 = balanced, 1.0 = always right
  burst_length:            int   [1 .. 5]           # Consecutive ATTACK actions before movement
  burst_cooldown:          int   [0 .. 3]           # Movement ticks between bursts
  forward_tendency:        float [0.00 .. 0.30]     # Probability of pressing forward (reduces ATTACK for approach)
  turn_vs_strafe_ratio:    float [0.00 .. 1.00]     # Among movement actions, fraction allocated to turning vs strafing
  movement_commitment:     int   [1 .. 4]           # Consecutive movement actions in same direction before switching
}
```

### Parameter Interpretation

| Parameter | Role | Interaction with Prior Findings |
|-----------|------|-------------------------------|
| **attack_probability** | Base likelihood of attacking on each tick. Governs the attack/movement balance. | F-077 predicts this should be invariant (50-100% equivalent). Evolution tests whether fine-tuning breaks this invariance at sk3. |
| **strafe_probability** | When not attacking, probability of strafing vs turning. Higher = more lateral displacement. | F-094 (strafing drives movement effect) predicts evolution will select high values. |
| **strafe_direction_bias** | Asymmetry in strafe direction. 0.0 = equal left/right, ±1.0 = one direction only. | F-047 (non-random turn direction deleterious) may extend to strafe direction. Expect evolution to converge on ~0.0 (balanced). |
| **burst_length** | Number of consecutive attacks before inserting movement. | DOE-021 found burst_length=3 optimal in 3-action space (F-046). In 5-action, the optimal burst length may differ because strafing provides inter-burst utility. |
| **burst_cooldown** | Number of movement ticks between attack bursts. | Higher cooldown = more repositioning time. Interacts with burst_length to determine attack duty cycle. |
| **forward_tendency** | Probability of moving forward instead of attacking or strafing. | Forward movement closes distance to enemies but reduces dodging. Likely selected toward 0 (approaching is risky in defend_the_line). |
| **turn_vs_strafe_ratio** | Among movement actions, the fraction allocated to turning (vs strafing). | F-094 predicts low values (strafing preferred). But some turning is necessary for aiming — evolution should find the optimal balance. |
| **movement_commitment** | Number of consecutive ticks maintaining the same movement direction. | Tests whether sustained directional movement (like DOE-021's burst concept applied to movement) is beneficial for dodging patterns. |

### Genome-to-Action Mapping

```
On each tick:
  if in_burst (burst_counter > 0):
    action = ATTACK
    burst_counter -= 1
    if burst_counter == 0:
      cooldown_counter = burst_cooldown
  elif in_cooldown (cooldown_counter > 0):
    action = select_movement_action()
    cooldown_counter -= 1
    if cooldown_counter == 0:
      burst_counter = burst_length
  else:
    # Probabilistic selection
    r = random()
    if r < forward_tendency:
      action = MOVE_FORWARD  # Note: not in standard 5-action space; mapped to no-op or ATTACK
      # DESIGN NOTE: forward_tendency is mapped to a brief pause (no-op frame)
      # because defend_the_line has no forward movement button.
      # Instead, forward_tendency > 0 reduces attack frequency (hesitation).
    elif r < forward_tendency + attack_probability:
      burst_counter = burst_length
      action = ATTACK
      burst_counter -= 1
    else:
      action = select_movement_action()

select_movement_action():
  if movement_commitment_counter > 0:
    action = last_movement_action
    movement_commitment_counter -= 1
    return action

  r = random()
  if r < turn_vs_strafe_ratio:
    # Turning
    action = TURN_LEFT if random() < 0.5 else TURN_RIGHT
  else:
    # Strafing
    bias_r = random()
    if bias_r < (0.5 + strafe_direction_bias / 2.0):
      action = MOVE_RIGHT
    else:
      action = MOVE_LEFT

  movement_commitment_counter = movement_commitment - 1
  last_movement_action = action
  return action
```

### Design Note: forward_tendency Mapping

The standard 5-action space for defend_the_line is {MOVE_LEFT, MOVE_RIGHT, TURN_LEFT, TURN_RIGHT, ATTACK}. There is no MOVE_FORWARD button. The `forward_tendency` parameter models **hesitation** — ticks where the agent neither attacks nor moves laterally. When forward_tendency triggers, the agent performs a no-op equivalent (skips the tick with a neutral action). This tests whether brief pauses between action sequences improve performance (allowing enemies to enter better firing positions) or degrade it (wasted time).

If the 5-action .cfg file includes MOVE_FORWARD (making it 6 actions), forward_tendency maps directly. For standard 5-action, it maps to reduced attack frequency.

## Initial Population (Gen 1): 10 Genomes

### Genome Table

| ID | Name | attack_prob | strafe_prob | strafe_bias | burst_len | burst_cd | fwd_tend | turn_strafe | move_commit | Origin |
|----|------|------------|-------------|-------------|-----------|----------|----------|-------------|-------------|--------|
| G01 | ar_50_balanced | 0.50 | 0.50 | 0.0 | 1 | 0 | 0.00 | 0.00 | 1 | ar_50 analog (pure strafe) |
| G02 | ar_50_with_turn | 0.50 | 0.50 | 0.0 | 1 | 0 | 0.00 | 0.30 | 1 | ar_50 + turning |
| G03 | burst_3_strafe | 0.50 | 0.40 | 0.0 | 3 | 1 | 0.00 | 0.10 | 1 | burst_3 adapted for 5-action |
| G04 | burst_3_heavy | 0.60 | 0.30 | 0.0 | 3 | 2 | 0.00 | 0.20 | 2 | burst_3 with extended cooldown |
| G05 | strafe_dominant | 0.35 | 0.50 | 0.0 | 2 | 1 | 0.00 | 0.05 | 3 | Heavy strafing, less attack |
| G06 | attack_heavy | 0.70 | 0.30 | 0.0 | 4 | 1 | 0.00 | 0.15 | 1 | High attack ratio |
| G07 | biased_left | 0.50 | 0.45 | -0.6 | 2 | 1 | 0.00 | 0.10 | 2 | Left-strafe bias |
| G08 | turn_emphasis | 0.45 | 0.25 | 0.0 | 2 | 1 | 0.00 | 0.60 | 1 | More turning than strafing |
| G09 | hesitant | 0.40 | 0.40 | 0.0 | 2 | 1 | 0.15 | 0.10 | 1 | With forward_tendency (pauses) |
| G10 | random_baseline | 0.50 | 0.50 | 0.0 | 1 | 0 | 0.00 | 0.50 | 1 | Near-uniform random |

### Genome Design Rationale

**G01 (ar_50_balanced)**: Direct analog of DOE-035's ar_50 strategy — 50% attack, 50% pure strafing (turn_vs_strafe_ratio=0.0). Serves as performance anchor and baseline. Expected: ~8-10 kills at sk3 (extrapolated from DOE-030 movement data at sk3).

**G02 (ar_50_with_turn)**: Same as G01 but allocates 30% of movement to turning. Tests whether adding rotation (aiming) to strafing improves kills. If F-094 (strafing drives effect) is complete, G02 should underperform G01.

**G03 (burst_3_strafe)**: DOE-021's burst_3 concept (burst_length=3) adapted for 5-action by adding strafing during the cooldown period. Tests whether burst_3's strength (sustained fire) combines synergistically with strafing. DOE-035 (F-097) showed burst_3 fails in 5-action because it never strafes — this variant explicitly adds strafing.

**G04 (burst_3_heavy)**: Extended variant of G03 with longer cooldown (2 movement ticks between bursts) and commitment to movement direction (2 consecutive ticks). Tests whether longer repositioning between bursts improves targeting.

**G05 (strafe_dominant)**: Maximizes strafing at the expense of attack frequency (35% attack). If time-rate compensation (F-074) holds, reducing attack frequency should extend survival without proportionally reducing kills. Tests the lower bound of viable attack probability.

**G06 (attack_heavy)**: High attack ratio (70%) with burst_length=4. Tests the upper bound of attack commitment in 5-action space. DOE-021's aggressive (G09) with 95% attack was not the worst but not optimal either. At 70%, there's still meaningful strafing.

**G07 (biased_left)**: Asymmetric strafe bias (-0.6, favoring left). Tests whether directional preference creates a targeting advantage (enemies approach from specific angles in defend_the_line). F-047 found non-random turn direction deleterious — does this extend to strafe direction?

**G08 (turn_emphasis)**: High turn_vs_strafe_ratio (0.60), allocating most movement to turning rather than strafing. Direct test of F-094 (strafing drives effect). If F-094 holds, G08 should significantly underperform G01-G05. If turning provides complementary aiming benefit, G08 may surprise.

**G09 (hesitant)**: Includes forward_tendency=0.15 (15% of ticks are pauses/hesitation). Tests whether brief pauses improve targeting by allowing enemies to enter line of sight. Expected: slight negative effect (wasted time), but could provide micro-repositioning advantage.

**G10 (random_baseline)**: Near-uniform random over 5 actions (50% attack, 50% movement split equally between strafing and turning). This is the evolutionary lower bound and calibration against F-099 (top 3 strategies equivalent to random in DOE-035).

## Design Matrix — Gen 1

| Run | Genome | Description | Episodes | Seeds |
|-----|--------|-------------|----------|-------|
| R01 | G01 | ar_50_balanced | 20 | [99001, ..., 103010] |
| R02 | G02 | ar_50_with_turn | 20 | [99001, ..., 103010] |
| R03 | G03 | burst_3_strafe | 20 | [99001, ..., 103010] |
| R04 | G04 | burst_3_heavy | 20 | [99001, ..., 103010] |
| R05 | G05 | strafe_dominant | 20 | [99001, ..., 103010] |
| R06 | G06 | attack_heavy | 20 | [99001, ..., 103010] |
| R07 | G07 | biased_left | 20 | [99001, ..., 103010] |
| R08 | G08 | turn_emphasis | 20 | [99001, ..., 103010] |
| R09 | G09 | hesitant | 20 | [99001, ..., 103010] |
| R10 | G10 | random_baseline | 20 | [99001, ..., 103010] |

**Total Gen 1**: 10 genomes × 20 episodes = 200 episodes

### Randomized Execution Order (Gen 1)

R05 → R08 → R02 → R10 → R06 → R01 → R04 → R09 → R07 → R03

(Randomized via Python `random.sample(range(1,11), 10)` with seed=4401)

## Scenario Configuration

**Scenario**: defend_the_line (5-action space)

```
# defend_the_line_5action.cfg
available_buttons = { MOVE_LEFT MOVE_RIGHT TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
doom_skill = 3          # Hurt Me Plenty (default difficulty)
```

## Fitness Function: TOPSIS

Multi-objective fitness using TOPSIS.

### Criteria and Weights

| Criterion | Direction | Weight | Justification |
|-----------|-----------|--------|---------------|
| kills (mean per genome) | Maximize | 0.50 | Primary performance metric; lethality is the goal |
| survival_time (mean per genome) | Maximize | 0.30 | Longer survival provides more opportunities for kills |
| kill_rate (mean per genome) | Maximize | 0.20 | Efficiency metric; penalizes strategies that survive long but kill slowly |

### Weight Rationale (Changed from DOE-021)

DOE-021 used equal weights (0.333 each). DOE-044 adjusts based on Phase 1-3 findings:
- **kills weighted highest (0.50)**: F-079 established kills as the primary discriminator. Survival without kills is not valuable.
- **survival weighted moderate (0.30)**: F-074 (rate-time compensation) shows survival and kill_rate trade off inversely. Weighting survival provides selection pressure for strategies that can sustain performance.
- **kill_rate weighted lowest (0.20)**: F-077 (tactical invariance) showed kill_rate is largely invariant within movement strategies. It serves as a tiebreaker, not a primary selection criterion.

### TOPSIS Procedure

1. **Decision matrix** D: 10 genomes × 3 criteria (mean values from 20 episodes each)
2. **Normalize**: r_ij = x_ij / sqrt(sum(x_kj^2) for all k)
3. **Weight**: v_ij = w_j × r_ij
4. **Ideal best**: A+ = {max(v_j) for each criterion j}
5. **Ideal worst**: A- = {min(v_j) for each criterion j}
6. **Distances**: D_i^+ = sqrt(sum((v_ij - A+_j)^2)), D_i^- = sqrt(sum((v_ij - A-_j)^2))
7. **Closeness**: C_i = D_i^- / (D_i^+ + D_i^-)
8. **Rank** by C_i descending (highest = best)

## Selection Mechanism

### Parent Selection
- Rank all 10 genomes by TOPSIS C_i
- **Top 4** genomes become parents for next generation
- **Bottom 6** eliminated

### Elitism
- The **best genome** (highest C_i) survives unchanged to next generation (elitism = 1)
- Guarantees monotonic fitness improvement

### Diversity Preservation
- At least **1 random genome** per generation (randomly initialized)
- Maximum **2 children** from same parent pair (prevents inbreeding)
- **1 mutation-only clone** of a non-elite parent (preserves successful traits with variation)

## Crossover Operator

Uniform crossover between two parents:

1. Select 2 parents from Top 4 (without replacement for first pair)
2. For each gene independently: inherit from Parent A with p=0.5, Parent B with p=0.5
3. **Constraints enforced post-crossover**:
   - All parameters clamped to valid ranges
   - burst_cooldown = 0 if burst_length = 1 (no cooldown needed for single-shot)

### Example

```
Parent A (G01): attack_prob=0.50, strafe_prob=0.50, strafe_bias=0.0, burst_len=1, ...
Parent B (G03): attack_prob=0.50, strafe_prob=0.40, strafe_bias=0.0, burst_len=3, ...
Child:          attack_prob=0.50(A), strafe_prob=0.40(B), strafe_bias=0.0(A), burst_len=3(B), ...
```

## Mutation Operator

Per-gene mutation probability: **p_mut = 0.20** (same as DOE-021)

| Gene Type | Mutation Rule | Range | Example |
|-----------|--------------|-------|---------|
| float | Gaussian perturbation N(0, σ=0.15), clamp to [min, max] | per-parameter | attack_prob 0.50 → 0.50 + N(0,0.15) → 0.62 |
| int (bounded) | ±1 step with equal probability, clamp to [min, max] | per-parameter | burst_length 3 → 2 or 4 |

### Mutation σ Values (Parameter-Specific)

| Parameter | σ | Range | Rationale |
|-----------|---|-------|-----------|
| attack_probability | 0.15 | [0.20, 0.80] | Moderate exploration within viable range |
| strafe_probability | 0.12 | [0.00, 0.50] | Smaller range needs tighter steps |
| strafe_direction_bias | 0.20 | [-1.0, 1.0] | Wide range, allow significant shifts |
| burst_length | ±1 | [1, 5] | Integer step |
| burst_cooldown | ±1 | [0, 3] | Integer step |
| forward_tendency | 0.08 | [0.00, 0.30] | Small range, fine exploration |
| turn_vs_strafe_ratio | 0.15 | [0.00, 1.00] | Wide range, moderate steps |
| movement_commitment | ±1 | [1, 4] | Integer step |

### Mutation Constraints

- All float parameters clamped to valid range after mutation
- burst_cooldown set to 0 if burst_length mutates to 1
- forward_tendency clamped to [0.00, 0.30] (higher values lose too much agency)

## Generational Composition Template

### Gen N+1 Composition (10 Genomes)

| Slot | Source | Description |
|------|--------|-------------|
| 1 | Elite | Best genome from Gen N (unchanged) |
| 2-3 | Crossover + Mutation | Children of Rank 1 × Rank 2 parents |
| 4-5 | Crossover + Mutation | Children of Rank 1 × Rank 3, and Rank 2 × Rank 4 |
| 6-7 | Crossover + Mutation | Children of Rank 3 × Rank 4, and Rank 1 × Rank 4 |
| 8 | Mutation only | Clone of Rank 2 parent with mutations |
| 9 | Mutation only | Clone of Rank 3 parent with mutations |
| 10 | Random | Freshly randomized genome (diversity injection) |

**Constraint**: Maximum 2 children from same parent pair.

## Generational Design

| Generation | Genomes | Episodes | Cumulative | Source |
|------------|---------|----------|------------|--------|
| Gen 1 | 10 | 200 | 200 | Initial population (this order) |
| Gen 2 | 10 | 200 | 400 | Selection + crossover + mutation from Gen 1 |
| Gen 3 | 10 | 200 | 600 | Selection + crossover + mutation from Gen 2 |
| Gen 4 | 10 | 200 | 800 | Selection + crossover + mutation from Gen 3 |
| Gen 5 | 10 | 200 | 1000 | Selection + crossover + mutation from Gen 4 |

**Maximum**: 5 generations, 1000 total episodes.

### Convergence Criterion

Evolution terminates early if **best genome unchanged for 2 consecutive generations**:
- "Unchanged" = same genome (by parameter values, not ID) holds rank #1 for 2 generations
- This indicates the population has converged to a local (possibly global) optimum
- Elite genome identity tracked via parameter-vector Euclidean distance: if distance < 0.01 (normalized), genome is considered unchanged

### Comparison with DOE-021 Convergence

DOE-021 converged at Gen 2 in the 3-action space. Expected convergence behavior for DOE-044:
- **If tactical invariance holds in parameter space**: Convergence at Gen 2-3 (fitness landscape is flat, random drift dominates)
- **If 5-action provides exploitable structure**: Convergence at Gen 4-5 or not at all within 5 generations (fitness landscape has gradients)
- **Convergence speed itself is a finding**: Fast convergence = invariance extends to evolution. Slow convergence = dimensionality provides genuine optimization opportunity.

## Seed Sets

### Per-Generation Seed Allocation

Each generation uses an independent seed set. All genomes within a generation share the same seeds (paired comparison design).

| Generation | Formula | Range | Count |
|------------|---------|-------|-------|
| Gen 1 | seed_i = 99001 + i × 211, i=0..19 | [99001, 103010] | 20 |
| Gen 2 | seed_i = 104001 + i × 223, i=0..19 | [104001, 108238] | 20 |
| Gen 3 | seed_i = 109001 + i × 227, i=0..19 | [109001, 113314] | 20 |
| Gen 4 | seed_i = 114001 + i × 229, i=0..19 | [114001, 118352] | 20 |
| Gen 5 | seed_i = 119001 + i × 233, i=0..19 | [119001, 123428] | 20 |

All increments are prime (211, 223, 227, 229, 233). Non-overlapping ranges ensure zero cross-generation seed collisions.

### Gen 1 Full Seed Set (n=20)

```
[99001, 99212, 99423, 99634, 99845, 100056, 100267, 100478, 100689, 100900,
 101111, 101322, 101533, 101744, 101955, 102166, 102377, 102588, 102799, 103010]
```

### Gen 2 Full Seed Set (n=20)

```
[104001, 104224, 104447, 104670, 104893, 105116, 105339, 105562, 105785, 106008,
 106231, 106454, 106677, 106900, 107123, 107346, 107569, 107792, 108015, 108238]
```

### Gen 3 Full Seed Set (n=20)

```
[109001, 109228, 109455, 109682, 109909, 110136, 110363, 110590, 110817, 111044,
 111271, 111498, 111725, 111952, 112179, 112406, 112633, 112860, 113087, 113314]
```

### Gen 4 Full Seed Set (n=20)

```
[114001, 114230, 114459, 114688, 114917, 115146, 115375, 115604, 115833, 116062,
 116291, 116520, 116749, 116978, 117207, 117436, 117665, 117894, 118123, 118352]
```

### Gen 5 Full Seed Set (n=20)

```
[119001, 119234, 119467, 119700, 119933, 120166, 120399, 120632, 120865, 121098,
 121331, 121564, 121797, 122030, 122263, 122496, 122729, 122962, 123195, 123428]
```

### Cross-Experiment Seed Collision Check

DOE-044 seed range: [99001, 123428]

| Experiment | Seed Range | Collision? |
|------------|-----------|------------|
| DOE-001–020 | [42, 23581] | NO (max 23581 < 99001) |
| DOE-021 | [23001, 38104] (5 generations) | NO (max 38104 < 99001) |
| DOE-022 | [24001, 26814] | NO |
| DOE-023 | [25001, 27930] | NO |
| DOE-024 | [40001, 42988] | NO |
| DOE-025 | [45001, 48182] | NO |
| DOE-026 | [50001, 53162] | NO |
| DOE-027 | [47001, 50688] | NO |
| DOE-028 | [48001, 51811] | NO |
| DOE-029 | [49001, 52974] | NO |
| DOE-030 | [53001, 57032] | NO |
| DOE-031 | [57101, 61422] | NO |
| DOE-032 | [61501, 62977] | NO |
| DOE-033 | [65001, 69554] | NO |
| DOE-034 | Uses DOE-008 seeds [6001, 7074] | NO |
| DOE-035 | [69001, 73728] | NO |
| DOE-036 | [73001, 77844] | NO |
| DOE-037 | [77001, 82018] | NO |
| DOE-038 | [81001, 89822] | NO |
| DOE-039 | [85001, 90250] | NO |
| DOE-040 | [89001, 98350] | NO (max 98350 < 99001) |
| DOE-041 | [93001, 98598] | NO (max 98598 < 99001) |
| DOE-042 | TBD (parallel design) | Verified: DOE-044 base 99001 above all prior |
| DOE-043 | TBD (parallel design) | Verified: DOE-044 base 99001 above all prior |

**Verdict**: DOE-044 range [99001, 123428] starts above the maximum of all known prior experiments (98598 from DOE-041). Zero seed collisions guaranteed.

## Statistical Analysis Plan

### Per-Generation Analysis

1. **One-way ANOVA** on kills (10 genomes as levels)
   - Response: kills per episode
   - Factor: genome (10 levels)
   - alpha = 0.05
   - n = 20 per genome

2. **One-way ANOVA** on each response individually (kills, kill_rate, survival_time)

3. **Residual diagnostics**: Normality (Anderson-Darling), Equal variance (Levene), Independence (run order)

4. **Tukey HSD** pairwise comparisons if ANOVA significant

5. **Effect sizes**: Cohen's d for pairwise, partial eta-squared for ANOVA

6. **Non-parametric backup**: Kruskal-Wallis if normality violated

### Cross-Generation Analysis

7. **Fitness trend**: Track best/mean/worst TOPSIS C_i per generation
   - Plot convergence curve (C_i vs generation)
   - Test for monotonic improvement (Jonckheere-Terpstra trend test)

8. **Genetic diversity**: Shannon entropy per gene per generation
   - For continuous genes: bin into quartiles, compute entropy
   - For integer genes: compute entropy over unique values
   - Entropy → 0 indicates premature convergence

9. **Parameter convergence**: Track distribution of each gene across generations
   - Identify genes under directional selection (mean shifting systematically)
   - Identify genes under stabilizing selection (variance decreasing)
   - Identify neutral drift genes (no systematic change)

10. **Selection pressure analysis**: For each parameter, compute:
    - Mean value in Top 4 (selected) vs Bottom 6 (eliminated)
    - If difference is consistent across generations: parameter under selection
    - This directly tests which genome dimensions evolution exploits

### Final Comparison

11. **Best evolved genome vs DOE-035 ar_50**:
    - Use the Gen 1 seed set for direct comparison (G01 already serves as ar_50 baseline)
    - Welch's t-test on kills
    - Cohen's d for practical significance

12. **Convergence speed comparison with DOE-021**:
    - DOE-021: converged at Gen 2 (3-action space)
    - DOE-044: record generation of convergence
    - Qualitative comparison: faster convergence = flatter landscape

### Tactical Invariance Test

13. **Within-movement-tier ANOVA**: Among genomes with strafe_probability > 0.2 (i.e., movement-inclusive), does kills vary significantly?
    - If p > 0.05: tactical invariance confirmed in evolutionary space
    - If p < 0.05: evolution has found configurations that differentiate within movement tier — **this would be a breakthrough finding**

### Power Analysis

- Per-generation: k=10 groups, n=20/group, alpha=0.05
  - For large effect (f=0.40): power ≈ 0.95
  - For medium effect (f=0.25): power ≈ 0.65
  - For small effect (f=0.10): power ≈ 0.12
- **Limitation**: n=20 per genome (reduced from DOE-021's n=30) provides adequate power for large effects but is underpowered for medium effects. This is an acceptable tradeoff given the 5-generation design (1000 episode budget).
- Compensated by: cross-generation trend analysis aggregates across generations for higher total N.

## Expected Outcomes

| Outcome | Probability | Interpretation | Next Step |
|---------|------------|---------------|-----------|
| **A: Convergence at Gen 2-3, no improvement over G01** | 40% | Tactical invariance extends to evolutionary parameter space. The fitness landscape is genuinely flat within the movement tier. | Conclude that random movement is optimal; evolution adds no value beyond ensuring strafing is present. Strengthens F-077. |
| **B: Convergence at Gen 4-5 with modest improvement (d=0.3-0.5)** | 25% | 5-action space provides marginal optimization opportunity. Evolution finds a slightly better strafe/attack balance but not a qualitative breakthrough. | Document parameter values of converged genome. Design DOE-045 to validate with independent seeds. |
| **C: Significant improvement over G01 (d>0.5) with specific parameter combination** | 15% | Tactical invariance is breakable via evolutionary search. A non-obvious parameter combination exists that manual strategy design missed. | **Breakthrough**: RSM around converged genome, design DOE-045 for fine-tuning. |
| **D: strafe_probability and turn_vs_strafe_ratio under strong selection** | 50% | Evolution confirms F-094 (strafing > turning) via selection pressure analysis, even if fitness improvement is small. | Quantitative validation of F-094 via independent method. |
| **E: forward_tendency selected to zero** | 60% | Hesitation provides no benefit; continuous action is optimal. | Remove forward_tendency from future genomes (parameter pruning). |
| **F: No convergence within 5 generations** | 10% | Landscape has multiple equivalent optima (consistent with invariance) or evolution is too slow. | Increase population or generations, or conclude invariance. |

### Key Diagnostic: Convergence Speed

| Convergence Gen | Interpretation |
|-----------------|---------------|
| Gen 2 | Identical to DOE-021; 5-action space adds no optimization structure |
| Gen 3 | Marginal additional structure; slightly more complex than 3-action |
| Gen 4-5 | Meaningful optimization structure; 5-action provides genuine evolutionary value |
| No convergence | Multiple optima or flat landscape; tactical invariance at its strongest |

## DuckDB Schema

```sql
CREATE TABLE IF NOT EXISTS experiments.DOE_044 (
  generation    INT NOT NULL,           -- 1-5
  genome_id     VARCHAR NOT NULL,       -- G01, G02, ..., G10
  genome_name   VARCHAR NOT NULL,       -- Descriptive name
  episode       INT NOT NULL,           -- 1-20
  seed          INT NOT NULL,           -- Fixed seed
  kills         INT,                    -- KILLCOUNT
  survival_time INT,                    -- Ticks alive
  kill_rate     FLOAT,                  -- kills / (survival_time / 35)
  health_final  INT,                    -- Final health
  ammo_final    INT,                    -- Final AMMO2
  -- Genome parameters
  attack_probability    FLOAT,
  strafe_probability    FLOAT,
  strafe_direction_bias FLOAT,
  burst_length          INT,
  burst_cooldown        INT,
  forward_tendency      FLOAT,
  turn_vs_strafe_ratio  FLOAT,
  movement_commitment   INT,
  -- TOPSIS (computed post-generation)
  topsis_ci     FLOAT,                  -- Closeness coefficient
  topsis_rank   INT,                    -- Rank within generation
  PRIMARY KEY (generation, genome_id, episode)
);
```

## Execution Checklist

Before execution, verify:
- [ ] defend_the_line_5action.cfg exists with {MOVE_LEFT, MOVE_RIGHT, TURN_LEFT, TURN_RIGHT, ATTACK}
- [ ] doom_skill = 3 (Hurt Me Plenty)
- [ ] Genome-to-action mapping implemented (8 parameters → action selection per tick)
- [ ] G01 replicates DOE-035 ar_50 behavior pattern (50% attack, 50% pure strafing)
- [ ] G10 replicates near-random behavior over 5 actions
- [ ] TOPSIS fitness computation validated (using kills weight=0.50, survival=0.30, kill_rate=0.20)
- [ ] Crossover and mutation operators implemented with constraints
- [ ] Seed sets generated for all 5 generations (verify exact values match this order)
- [ ] DuckDB experiments.DOE_044 table created with correct schema
- [ ] Convergence detection: parameter-vector Euclidean distance < 0.01 for elite genome
- [ ] Per-generation ANOVA script prepared
- [ ] Shannon entropy computation for genetic diversity tracking

### Anchor Validation Protocol

Before running full Gen 1, execute a 3-episode pilot on G01, G08, G10 with seeds [99001, 99212, 99423]:

- **G01 (ar_50_balanced)**: Expected ~8-10 kills at sk3 (based on DOE-030 movement tier at sk3)
- **G08 (turn_emphasis)**: Expected lower than G01 if F-094 holds (turning < strafing)
- **G10 (random_baseline)**: Expected similar to G01 if F-099 holds (within-movement invariance)

Validation criteria:
- G01 kills > 0 (confirms agent is functional in 5-action space)
- G08 kills < G01 kills (directional check for F-094)
- If G01 kills = 0 or any genome crashes: STOP and investigate genome-to-action mapping
- If all genomes produce identical kills within ±1: check for factor injection failure (DOE-005 precedent)

## Cross-References

- **F-046**: burst_3 globally optimal in 3-action, convergence at Gen 2 (DOE-021)
- **F-047**: Non-random turn_direction deleterious (DOE-021)
- **F-077**: Tactical invariance — kills invariant to attack ratio within movement strategies (DOE-028)
- **F-079**: Movement sole determinant, d=1.408 (DOE-029)
- **F-087**: 5-action space optimal (DOE-031)
- **F-092**: Movement benefit amplified in larger action spaces (DOE-033)
- **F-094**: Strafing (not turning) drives the movement effect (DOE-033)
- **F-097**: burst_3 catastrophically fails in 5-action space (DOE-035)
- **F-098**: Absolute performance ceiling at doom_skill=1 (DOE-035)
- **F-099**: Top 3 strategies form statistical equivalence band (DOE-035)
- **F-100**: Movement binary creates two performance tiers (DOE-035)

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: arithmetic progressions with prime increments per generation |
| No seed collisions | YES: verified against all DOE-001 through DOE-043 |
| n >= 20 per condition | YES: 20 episodes per genome per generation |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, variance, independence per generation |
| Effect sizes | PLANNED: Cohen's d pairwise, partial eta-squared per ANOVA |
| Seeds identical across conditions | YES: all 10 genomes use same 20 seeds within each generation |
| Cross-generation seed independence | YES: each generation uses distinct non-overlapping seed set |

## Status

**ORDERED** — Ready for execution
