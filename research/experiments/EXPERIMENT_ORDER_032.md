# EXPERIMENT_ORDER_032: Cross-Episode Sequential Learning (2x2 Factorial)

## Metadata
- **DOE ID**: DOE-032
- **Hypothesis**: H-035
- **Design Type**: 2x2 Factorial with Repeated Measures
- **Phase**: 2 (Learning Mechanism Investigation)
- **Date Ordered**: 2026-02-10
- **Budget**: 400 episodes
- **Cumulative Episodes**: 5830

## Hypothesis

**H-035**: Cross-episode sequential exposure enables L1 cache-based learning that improves performance over a 10-episode sequence, while independent episodes show no learning curve. The learning effect manifests as higher kills in the LAST 5 episodes of a sequence compared to the FIRST 5.

### Rationale

The entire 29-DOE program evaluated single-episode performance. Each episode was treated as an independent observation. But the clau-doom architecture includes L1 DuckDB cache for per-agent play history. If the cache is populated across sequential episodes (same agent, no restart between episodes), the agent's L1 decisions may adapt based on accumulated experience.

The RAG hypothesis (L2) was falsified (F-070: triple null across DOE-022/024/026). But L1 was never tested for SEQUENTIAL learning. L1 operates at a different level: it stores local patterns from recent play, not strategy documents. If 10 episodes are played sequentially without resetting the DuckDB cache, the L1 layer accumulates game-specific patterns that could improve performance over the sequence.

This is a fundamentally different claim from "L2 RAG helps" -- it tests whether LOCAL, EXPERIENTIAL learning (L1 cache) provides value that DOCUMENT-BASED learning (L2 RAG) did not.

### Key Distinction from Prior Work

| Prior DOEs | This DOE |
|-----------|----------|
| Single episodes, independent | 10-episode sequences |
| L1 cache reset between episodes | L1 cache accumulates |
| Each episode = 1 observation | Learning curve across 10 episodes |
| Static strategy | Strategy adapts via cached experience |

### Critical Confound: Health/Ammo Reset

In VizDoom, each new_episode() resets health and ammo. The L1 cache provides a different kind of memory: knowledge of enemy spawn patterns, effective positions, timing patterns. Even though health resets, behavioral adaptation from cached patterns may improve performance.

## Factors

| Factor | Levels | Type | Description |
|--------|--------|------|-------------|
| l1_cache | 2 | Fixed | Whether L1 DuckDB cache persists across episodes |
| sequence_mode | 2 | Fixed | Whether episodes are independent or sequential |

### Factor Levels

**l1_cache** (2 levels):
- `on`: L1 DuckDB cache enabled. Patterns from previous episodes persist and inform decisions.
- `off`: L1 DuckDB cache disabled (or cleared between episodes). Each episode starts with empty local history.

**sequence_mode** (2 levels):
- `sequential_10`: 10 episodes played in sequence, same seed order. L1 cache persists (if enabled). Response measured as kills in episodes 6-10 (post-learning).
- `independent`: 10 episodes played independently (cache cleared between each regardless of l1_cache setting). Same seeds. Response measured as kills in episodes 6-10.

### Interaction Prediction

The critical cell is l1_cache=on + sequential_10: this is the ONLY condition where learning can occur. The interaction term tests whether sequential exposure WITH active cache produces improvement.

## Response Variables

| Variable | Metric | Direction |
|----------|--------|-----------|
| kills_late | Mean kills in episodes 6-10 of each sequence | Maximize |
| kills_early | Mean kills in episodes 1-5 of each sequence | Comparison |
| learning_slope | Linear regression slope of kills across episodes 1-10 | Maximize |
| kills_total | Mean kills across all 10 episodes | Maximize |

### Primary Response

kills_late (episodes 6-10 mean) is the primary response for ANOVA. This captures post-learning performance while controlling for early-sequence noise.

### Secondary Response

learning_slope (regression coefficient of kills ~ episode_number within each sequence) measures the RATE of learning. A positive slope indicates improvement over the sequence.

## Design Matrix

| Run | l1_cache | sequence_mode | Code | Sequences | Episodes per Sequence | Total Episodes | Seeds |
|-----|----------|--------------|------|-----------|----------------------|----------------|-------|
| R1 | on | sequential_10 | cache_seq | 10 | 10 | 100 | See below |
| R2 | on | independent | cache_ind | 10 | 10 | 100 | See below |
| R3 | off | sequential_10 | nocache_seq | 10 | 10 | 100 | See below |
| R4 | off | independent | nocache_ind | 10 | 10 | 100 | See below |

### Seed Structure

Each "sequence" of 10 episodes uses 10 consecutive seeds. There are 10 sequences per condition, for 100 episodes per condition, 400 total.

**Sequence seeds**: Each sequence k (k=0..9) uses seeds starting from a base:

Formula: seed_{k,i} = 61501 + k * 151 + i * 13, for k = 0..9 (sequence), i = 0..9 (episode within sequence)

This produces 10 blocks of 10 seeds each:
```
Sequence 0: [61501, 61514, 61527, 61540, 61553, 61566, 61579, 61592, 61605, 61618]
Sequence 1: [61652, 61665, 61678, 61691, 61704, 61717, 61730, 61743, 61756, 61769]
Sequence 2: [61803, 61816, 61829, 61842, 61855, 61868, 61881, 61894, 61907, 61920]
Sequence 3: [61954, 61967, 61980, 61993, 62006, 62019, 62032, 62045, 62058, 62071]
Sequence 4: [62105, 62118, 62131, 62144, 62157, 62170, 62183, 62196, 62209, 62222]
Sequence 5: [62256, 62269, 62282, 62295, 62308, 62321, 62334, 62347, 62360, 62373]
Sequence 6: [62407, 62420, 62433, 62446, 62459, 62472, 62485, 62498, 62511, 62524]
Sequence 7: [62558, 62571, 62584, 62597, 62610, 62623, 62636, 62649, 62662, 62675]
Sequence 8: [62709, 62722, 62735, 62748, 62761, 62774, 62787, 62800, 62813, 62826]
Sequence 9: [62860, 62873, 62886, 62899, 62912, 62925, 62938, 62951, 62964, 62977]
```

Maximum seed: 62977

Same seeds used across all 4 conditions for paired comparison.

### Randomized Run Order

R3, R1, R4, R2

## Analysis Plan

### Primary Analysis: 2x2 ANOVA on kills_late

Two-way ANOVA: l1_cache (2) x sequence_mode (2)

| Source | df |
|--------|-----|
| l1_cache (A) | 1 |
| sequence_mode (B) | 1 |
| A x B (interaction) | 1 |
| Error (between sequences) | 36 |
| Total | 39 |

Note: The unit of observation is the SEQUENCE (n=10 sequences per condition, total N=40). Each sequence yields one kills_late value (mean of episodes 6-10).

### Key Test

The **interaction** A x B is the critical test. If l1_cache=on AND sequence_mode=sequential produces higher kills_late than all other conditions, it demonstrates that sequential cache-based learning works.

### Secondary Analysis: Learning Slope

Mixed-effects model: kills ~ episode_number * l1_cache * sequence_mode + (1|sequence)

This tests whether the within-sequence slope (kills vs episode number) differs across conditions. The three-way interaction (episode_number x l1_cache x sequence_mode) is the critical term: a positive slope ONLY in the cache_seq condition = learning.

### Planned Contrasts

| ID | Contrast | Tests |
|----|----------|-------|
| C1 | R1 (cache_seq) vs R4 (nocache_ind) | Full learning vs no learning baseline |
| C2 | R1 (cache_seq) vs R2 (cache_ind) | Sequential benefit with cache |
| C3 | R1 (cache_seq) vs R3 (nocache_seq) | Cache benefit in sequential mode |
| C4 | R2 (cache_ind) vs R4 (nocache_ind) | Cache main effect (independent episodes) |

### Diagnostics

- Normality: Anderson-Darling on residuals (sequence-level means)
- Equal variance: Levene test
- Independence: Between sequences (within sequences, repeated measures structure)
- Learning curve visualization: Plot kills vs episode number by condition

## Power Analysis

- Alpha = 0.05
- Expected effect: Unknown (novel experiment). Using medium effect size d=0.5 as planning estimate.
- Unit of observation: sequence mean (n=10 per condition, N=40)
- With N=40 (10 per cell):
  - Power for detecting d=0.5 on interaction: approximately 0.40
  - Power for detecting d=0.8 on interaction: approximately 0.65
  - Power for detecting d=1.0 on interaction: approximately 0.78

### Power Mitigation

The primary power concern is addressed by:
1. Using sequence means (variance reduction via averaging 5 episodes)
2. The learning slope analysis uses all 400 individual episodes with mixed-effects structure
3. If interaction is non-significant but trending, this informs whether a larger follow-up is warranted
4. This is an EXPLORATORY experiment -- the goal is to detect whether learning exists at all, not to precisely estimate its magnitude

### Note on Sample Size

10 sequences per condition (100 episodes per condition) was chosen to balance:
- Statistical power (N=40 sequence-level observations)
- Execution time (400 total episodes, approximately 2 hours)
- Learning opportunity (10 episodes per sequence provides meaningful adaptation window)

## Execution Instructions for research-doe-runner

### Implementation: Sequential Mode

For `sequential_10`:
1. Start the agent container
2. Initialize L1 DuckDB cache (or leave empty if l1_cache=off)
3. Play 10 episodes IN ORDER using seeds from one sequence block
4. Between episodes: call new_episode() but do NOT restart the agent container or clear the cache
5. Record kills for each individual episode (all 10)
6. After 10 episodes, compute kills_early (mean of episodes 1-5), kills_late (mean of episodes 6-10), learning_slope
7. Repeat for all 10 sequences

### Implementation: Independent Mode

For `independent`:
1. For each of 100 episodes:
   - Clear L1 DuckDB cache (regardless of l1_cache setting)
   - Play single episode
   - Record kills
2. Group into 10 "sequences" of 10 episodes for analysis comparability
3. Seeds should match sequential mode for pairing

### Strategy

Use random_50 action function (p_attack=0.5, else random movement 0-3) for ALL conditions. This removes strategy confound and isolates the cache/sequence learning effect.

### Action Space

Use defend_the_line_5action.cfg with 5 actions, doom_skill=3 (default).

### Recording

For each episode, record:
- episode_number_in_sequence (1-10)
- sequence_id (0-9)
- condition (cache_seq, cache_ind, nocache_seq, nocache_ind)
- kills
- survival_time
- kill_rate
- seed

## Expected Outcomes

| Outcome | Probability | Implication |
|---------|------------|-------------|
| A: Significant interaction (cache_seq > all others) | 20% | L1 sequential learning IS real; local experience accumulation provides value that L2 RAG cannot |
| B: Sequence mode main effect only (both seq conditions improve) | 10% | Practice effect exists but is not cache-dependent (warm-up artifact) |
| C: Cache main effect only (both cache conditions improve) | 10% | Cache helps even in independent episodes (unlikely given DOE-022 null) |
| D: Complete null (no effects, no interaction) | 55% | L1 cache does not create measurable learning on this scenario within 10 episodes |
| E: Negative effect (cache HURTS performance) | 5% | L1 cached patterns are counterproductive (similar to L2 RAG degradation in DOE-022) |

### Interpretation Framework

If Outcome D (most likely): This completes the falsification narrative. Neither L2 document-based learning (DOE-022/024/026) NOR L1 experiential learning produces measurable improvement in defend_the_line. The environment is too simple/noisy for learning to manifest.

If Outcome A: This is a breakthrough finding. It means the RAG system's failure was specifically an L2/document problem, not a learning problem. Local experience accumulation works; abstract strategy documents do not. This would redirect the research toward L1 optimization.

## Cross-References

- F-049: L2 RAG degrades performance (DOE-022)
- F-070: RAG hypothesis triple-null falsification (DOE-022/024/026)
- F-077: Full tactical invariance in 5-action space (DOE-028)
- F-079: Movement sole determinant (DOE-029)
- H-005: Strategy document quality (partially addressed)
- DOE-022: L2 RAG pipeline activation (first null)
- DOE-024: L2 meta-strategy selection (second null)
- DOE-026: L2 RAG in 5-action space (third null, definitive)
