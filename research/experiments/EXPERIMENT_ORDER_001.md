# EXPERIMENT_ORDER_001: OFAT Baseline Comparison

## Metadata
- Experiment ID: DOE-001
- Hypothesis: H-001
- Design: OFAT (One Factor At a Time)
- Phase: 0
- Author: research-pi
- Date: 2026-02-07

## Research Question

Does a RAG-augmented decision system outperform random and rule-only baselines
in the VizDoom defend_the_center scenario?

## Hypothesis

H-001: Full RAG agent (L0+L1+L2) achieves significantly higher kill_rate
than random and rule-only baselines.

## Design

### Factor
- Decision Mode: {random, rule_only, full_agent}
- This is an OFAT comparison (3 levels of a single factor)

### Response Variables (Primary)
- kill_rate: kills per minute (kills / (survival_time / 60))

### Response Variables (Secondary)
- kills: total kills per episode
- survival_time: seconds survived
- damage_dealt: total damage dealt
- damage_taken: total damage taken
- ammo_efficiency: hits / shots_fired
- exploration_coverage: cells_visited / total_cells

### Tracking Metrics
- decision_latency_p99: milliseconds
- rule_match_rate: fraction of ticks with L0 rule match
- decision_level_counts: JSON distribution across L0/L1/L2

## Conditions

### Condition 1: Random Baseline
- Decision Mode: random
- All decision levels disabled
- Actions selected uniformly at random (deterministic PRNG)
- Factor injection: DECISION_MODE=random

### Condition 2: Rule-Only
- Decision Mode: rule_only
- L0 enabled, L1 disabled, L2 disabled
- MD rules only, fallback to random when no rule matches
- Factor injection: DECISION_MODE=rule_only, L1_ENABLED=DISABLED, L2_ENABLED=DISABLED

### Condition 3: Full RAG Agent
- Decision Mode: full_agent
- L0 enabled, L1 enabled, L2 enabled
- Full L0 -> L1 -> L2 cascade
- Factor injection: DECISION_MODE=full_agent, L1_ENABLED=ENABLED, L2_ENABLED=ENABLED

## Sample Size
- Episodes per condition: 70
- Total episodes: 210
- Justification: n=70 provides power >= 0.80 for detecting medium effect (d=0.5)

## Seed Set
- Formula: seed_i = 42 + i * 31, for i = 0..69
- Count: 70 seeds
- Seeds: [42, 73, 104, 135, ..., 2179]
- CRITICAL: All 3 conditions use IDENTICAL seed set

## Execution Order
1. Condition 1 (Random): 70 episodes
2. Condition 2 (Rule-Only): 70 episodes
3. Condition 3 (Full Agent): 70 episodes

## Statistical Analysis Plan
- Primary test: Welch's t-test for 3 pairwise comparisons
- Multiple comparison correction: Holm-Bonferroni (alpha=0.05)
- Effect size: Cohen's d
- Non-parametric alternative: Mann-Whitney U
- Normality check: Anderson-Darling test
- Equal variance check: Levene's test
- Significance level: alpha = 0.05

## Expected Results
- Full RAG vs Random: d > 1.5 (large effect)
- Full RAG vs Rule-Only: d = 0.5-1.0 (medium effect)
- Rule-Only vs Random: d = 0.5-1.0 (medium effect)

## Deliverables
- EXPERIMENT_REPORT_DOE_001.md with full statistical analysis
- Diagnostic plots (QQ, run-order, boxplot)
- DuckDB data with 210 episode records
