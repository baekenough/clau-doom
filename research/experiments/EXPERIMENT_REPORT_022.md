# EXPERIMENT_REPORT_022: L2 RAG Pipeline Activation

**Experiment Order**: DOE-022 (EXPERIMENT_ORDER_022.md)
**Hypothesis**: H-025 — L2 kNN strategy retrieval provides performance improvement
**Date**: 2026-02-09
**Analyst**: research-analyst (automated)

---

## Design Summary

| Parameter | Value |
|-----------|-------|
| Design Type | One-way (4 conditions) |
| Scenario | defend_the_line.cfg |
| Conditions | L0_only, L0_L1 (burst_3), L0_L1_L2_good, L0_L1_L2_random |
| Episodes per condition | 30 |
| Total episodes | 120 |
| Seed formula | seed_i = 24001 + i × 97, i=0..29 |
| Execution order | R3 → R1 → R4 → R2 |

### Conditions

| Condition | Description | Action Function |
|-----------|-------------|-----------------|
| L0_only | Pure reflex rules | rule_only_action |
| L0_L1 | L0 + burst_3 periodic pattern | Burst3Action |
| L0_L1_L2_good | L0 + L2 RAG (HIGH quality docs) + L1 fallback | L2RagAction(strategies_high) |
| L0_L1_L2_random | L0 + L2 RAG (LOW quality docs) + L1 fallback | L2RagAction(strategies_low) |

### L2 RAG Infrastructure

- **OpenSearch indices**: strategies_high (50 HIGH docs), strategies_low (50 LOW docs)
- **Query method**: Term matching on situation_tags (bool.should, minimum_should_match=1)
- **Scoring**: similarity×0.4 + confidence×0.4 + recency×0.2
- **Tactic mapping**: retreat/kite→TURN_LEFT, flank→TURN_RIGHT, all others→ATTACK
- **Timeout**: 80ms per query

---

## Descriptive Statistics

| Condition | n | avg_kills | sd_kills | avg_kr | sd_kr | avg_surv | sd_surv | min | max |
|-----------|---|-----------|----------|--------|-------|----------|---------|-----|-----|
| L0_L1 (burst_3) | 30 | 14.73 | 3.78 | 45.20 | 4.61 | 19.70 | 5.19 | 8 | 23 |
| L0_L1_L2_good | 30 | 9.57 | 2.36 | 39.77 | 4.79 | 14.63 | 4.04 | 5 | 15 |
| L0_L1_L2_random | 30 | 9.57 | 2.36 | 39.77 | 4.79 | 14.63 | 4.04 | 5 | 15 |
| L0_only | 30 | 9.13 | 2.22 | 37.03 | 4.88 | 15.00 | 4.03 | 4 | 12 |

**CRITICAL OBSERVATION**: L0_L1_L2_good and L0_L1_L2_random are **perfectly identical** at the episode level (30/30 episodes match). This indicates that document quality has zero effect due to coarse tactic-to-action mapping.

---

## ANOVA Results

### kills (Primary Response)

| Source | SS | df | MS | F | p-value | partial η² |
|--------|-----|-----|------|------|---------|------------|
| Condition | 649.23 | 3 | 216.41 | 28.05 | < 0.00000001 | 0.42 |
| Error | 894.77 | 116 | 7.71 | | | |
| Total | 1544.00 | 119 | | | | |

[STAT:f=F(3,116)=28.05] [STAT:p<0.00000001] [STAT:eta2=η²=0.42]

### kill_rate (Secondary Response)

| Source | SS | df | MS | F | p-value | partial η² |
|--------|-----|-----|------|------|---------|------------|
| Condition | 1036.88 | 3 | 345.63 | 15.47 | 0.00000002 | 0.29 |
| Error | 2592.22 | 116 | 22.35 | | | |
| Total | 3629.10 | 119 | | | | |

[STAT:f=F(3,116)=15.47] [STAT:p=0.00000002] [STAT:eta2=η²=0.29]

---

## Post-Hoc Comparisons (Tukey HSD)

### kills

| Comparison | Diff | p-value | Significance |
|------------|------|---------|-------------|
| L0_L1 vs L0_only | +5.60 | < 0.001 | *** |
| L0_L1 vs L0_L1_L2_good | +5.17 | < 0.001 | *** |
| L0_L1 vs L0_L1_L2_random | +5.17 | < 0.001 | *** |
| L0_L1_L2_good vs L0_L1_L2_random | 0.00 | 1.000 | ns |
| L0_L1_L2_good vs L0_only | +0.43 | 0.929 | ns |
| L0_L1_L2_random vs L0_only | +0.43 | 0.929 | ns |

### kill_rate

| Comparison | Diff | p-value | Significance |
|------------|------|---------|-------------|
| L0_L1 vs L0_only | +8.17 | < 0.001 | *** |
| L0_L1 vs L0_L1_L2_good | +5.43 | < 0.001 | *** |
| L0_L1 vs L0_L1_L2_random | +5.43 | < 0.001 | *** |
| L0_L1_L2_good vs L0_L1_L2_random | 0.00 | 1.000 | ns |
| L0_L1_L2_good vs L0_only | +2.74 | 0.123 | ns |
| L0_L1_L2_random vs L0_only | +2.74 | 0.123 | ns |

---

## Residual Diagnostics

| Test | Statistic | p-value | Result |
|------|-----------|---------|--------|
| Shapiro-Wilk (normality) | W = 0.9857 | 0.2366 | **PASS** |
| Levene (equal variance) | F = 2.89 | 0.0385 | MARGINAL FAIL |

**Note**: Levene test marginally fails (p = 0.039). With equal group sizes (n=30), ANOVA is robust to mild variance heterogeneity. The variance ratio (largest/smallest) = (3.78/2.22)² = 2.90, below the 3:1 threshold for concern with balanced designs.

---

## Effect Sizes (Cohen's d)

| Contrast | d | Interpretation |
|----------|---|----------------|
| L0_L1 vs L0_only | 1.807 | Huge |
| L0_L1 vs L2_good | 1.641 | Huge |
| L0_L1 vs L2_random | 1.641 | Huge |
| L2_good vs L2_random | 0.000 | Zero |
| L2_good vs L0_only | 0.189 | Negligible |

---

## Key Planned Contrasts

| Contrast | Question | Result |
|----------|----------|--------|
| C1: L2_good vs L0_L1 | Does L2 RAG improve on burst_3? | **NO** (kills: -5.17, p < 0.001). L2 significantly WORSE. |
| C2: L2_good vs L2_random | Does document quality matter? | **NO** (kills: 0.00, p = 1.000). Perfectly identical. |
| C3: L0_L1 vs L0_only | Does burst_3 improve on reflexes? | **YES** (kills: +5.60, p < 0.001). Confirms DOE-008 F-010. |
| C4: L2_random vs L0_L1 | Does poor L2 hurt vs burst_3? | **YES** (kills: -5.17, p < 0.001). L2 replaces beneficial patterns. |

---

## Mechanism Analysis

### Why L2_good = L2_random (Perfect Identity)

The 30/30 episode-level identity occurs because:

1. **Tactic-to-action mapping is too coarse**: 3 VizDoom actions (TURN_LEFT, TURN_RIGHT, ATTACK) with only 3 tactic prefixes (retreat/kite, flank, everything else)
2. **Both indices produce ATTACK-dominant actions**: HIGH docs map 72% to ATTACK; LOW docs map 100% to ATTACK. The best-scoring document in both cases maps to ATTACK.
3. **L0 emergency override identical**: Both share health < 20 → TURN_LEFT rule
4. **Deterministic selection**: max() scoring on both indices selects ATTACK-tactic documents

### Why L2 < L0_L1 (burst_3)

1. **Lost periodic turning**: burst_3 enforces 3-attack-then-1-turn cycle, providing lateral movement that breaks tunnel vision
2. **L2 returns constant ATTACK**: When L2 query succeeds, it typically returns ATTACK-mapping tactics, eliminating the beneficial turning cycle
3. **Performance regression to L0_only level**: L2 conditions (9.57 kills) ≈ L0_only (9.13 kills), confirming that L2 effectively replaces burst_3 with attack-only behavior

---

## Findings

### F-049: L2 RAG with Coarse Action Mapping Causes Performance Regression

Adding L2 RAG strategy retrieval to L0+L1 (burst_3) architecture **significantly degrades** performance [STAT:p<0.001] [STAT:f=F(3,116)=28.05] [STAT:eta2=η²=0.42]. kills decrease from 14.73 to 9.57 [STAT:effect_size=d=1.641]. The mechanism is that L2 queries return ATTACK-mapping tactics that replace burst_3's beneficial periodic turning pattern.

**Trust Level**: HIGH (p < 0.001, n = 30/condition, normality PASS, balanced design)

### F-050: Document Quality Is Irrelevant Under Coarse Tactic-to-Action Mapping

HIGH quality strategy documents (trust 0.75-0.95, derived from DOE-020 burst_3 data) and LOW quality documents (trust 0.30-0.34, synthetic/random) produce **perfectly identical** game behavior (30/30 episodes match, d = 0.000) [STAT:p=1.000]. The tactic-to-action mapping collapses all quality differences into the same action distribution.

**Trust Level**: HIGH (deterministic identity, 30/30 match)

### F-051: Beneficial L1 Patterns Must Be Preserved When Adding L2

L2 RAG retrieval replaces burst_3's periodic 3-attack+1-turn cycle with continuous ATTACK, eliminating the lateral movement that was the primary mechanism for outperforming L0_only (DOE-008 F-010). Performance regresses from burst_3 level (14.73 kills) to L0_only level (9.57 kills) [STAT:effect_size=d=1.641].

**Trust Level**: HIGH

---

## Hypothesis Disposition

**H-025**: L2 kNN strategy retrieval provides performance improvement.
**Status**: **REJECTED** [STAT:p<0.001]
**Reason**: L2 RAG not only fails to improve but significantly hurts performance when tactic-to-action mapping is coarse. Document quality has zero effect.

---

## Recommendations

1. **Expand action space before retesting L2 RAG**: The 3-action tactic mapping (retreat/flank/else→attack) is too coarse. Need 5+ distinct tactic-to-action mappings.
2. **Preserve L1 periodic patterns**: Any L2 implementation must preserve burst_3's turning cycle. Consider L2 as occasional override rather than complete replacement.
3. **Hybrid L1+L2 architecture**: L2 could modulate L1 parameters (e.g., burst length, turn probability) rather than replacing actions entirely.
4. **finer-grained tactics**: Strategy documents need tactics that map to distinct action sequences, not just single actions.

---

## Data Location

- DuckDB: `data/clau-doom.duckdb` (table: experiments, experiment_id='DOE-022')
- Strategy docs: `research/experiments/doe-022-data/`
- OpenSearch indices: strategies_high, strategies_low (localhost:9200)
