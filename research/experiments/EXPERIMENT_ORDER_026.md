# EXPERIMENT_ORDER_026: L2 RAG Strategy Selection in 5-Action Space

## Metadata
- **DOE-ID**: DOE-026
- **Hypothesis**: H-029 — RAG strategy selection has value in 5-action space
- **Phase**: Phase 1 (Confirmatory)
- **Design**: One-way ANOVA (5 conditions)
- **Previous**: DOE-025 (5-action strategy optimization), DOE-024 (L2 meta rejected in 3-action), DOE-022 (L2 RAG null in 3-action)
- **Date**: 2026-02-09

## Research Question

Does L2 RAG-based adaptive strategy selection outperform fixed strategies in the 5-action space where strategy differentiation exists (F-062, F-063)?

This is the CRITICAL thesis test: "Agent Skill = Document Quality × Scoring Accuracy" (F-061). Previous L2 tests (DOE-022, DOE-024) produced null results in 3-action space where strategies converged. DOE-025 established that 5-action strategies meaningfully differentiate (kills p=0.0017, survival p=0.0009), creating the NECESSARY CONDITION for RAG value.

## Conditions

| Run | Condition | Strategy Type | Description |
|-----|-----------|---------------|-------------|
| R1 | survival_burst | Fixed (Best) | DOE-025 winner: kills=19.63, survival=30.1s |
| R2 | random_5 | Fixed (2nd) | DOE-025 runner-up: kills=18.13, survival=26.4s |
| R3 | dodge_burst_3 | Fixed (3rd) | DOE-025 third: kills=17.43, survival=26.8s |
| R4 | l2_meta_5action | Adaptive RAG | OpenSearch meta-strategy selection among top 3 |
| R5 | random_rotation_5 | Random baseline | Uniform random selection among top 3 strategies |

## Factor Details

### L2 Meta-Strategy Selector (R4)
- Index: `strategies_meta_5action` (new, populated before experiment)
- Query interval: 35 ticks (1 second) — re-evaluates strategy periodically
- Situation tags: health, ammo, enemy count (same as DOE-022/024)
- Strategy mapping: {survival_burst, random_5, dodge_burst_3}
- Fallback: survival_burst (best from DOE-025)
- Scoring: similarity*0.4 + confidence*0.4 + recency*0.2

### Random Rotation Selector (R5)
- Rotation interval: 35 ticks (1 second) — matches L2 query interval
- Selection: uniform random from {survival_burst, random_5, dodge_burst_3}
- Purpose: controls for strategy-switching benefit vs RAG-informed switching

### OpenSearch Strategy Documents (30 documents)
Tag-to-strategy mappings based on DOE-025 findings:
- low_health → survival_burst (defensive priority, F-064)
- low_ammo → survival_burst (resource conservation)
- multi_enemy + full_health → dodge_burst_3 (aggressive with evasion)
- single_enemy + full_health → random_5 (general purpose)
- ammo_abundant → dodge_burst_3 (can afford aggression)
- Default/mixed → survival_burst (globally optimal from DOE-025)

## Seed Set

Formula: seed_i = 46001 + i × 113, i = 0..29

```
Seeds (n=30):
[46001, 46114, 46227, 46340, 46453, 46566, 46679, 46792, 46905, 47018,
 47131, 47244, 47357, 47470, 47583, 47696, 47809, 47922, 48035, 48148,
 48261, 48374, 48487, 48600, 48713, 48826, 48939, 49052, 49165, 49278]
```

## Sample Size
- 30 episodes per condition
- 5 conditions
- Total: 150 episodes

## Response Variables
- kills (primary)
- kill_rate (kills per minute)
- survival_time (seconds)
- l2_query_count (RAG-specific: number of OpenSearch queries per episode)
- l2_strategy_switches (RAG-specific: number of strategy changes per episode)

## Planned Contrasts (Bonferroni-corrected α = 0.05/4 = 0.0125)

1. **RAG vs Best Fixed**: C4 vs C1 — core thesis test
2. **RAG vs Random Rotation**: C4 vs C5 — RAG value over random switching
3. **RAG vs Fixed Pool Mean**: C4 vs mean(C1,C2,C3) — RAG vs average fixed
4. **Random Rotation vs Best Fixed**: C5 vs C1 — switching benefit test

## Execution Order (Randomized)
R3, R1, R5, R4, R2

## Outcome Scenarios

### Outcome A: RAG Superior (H-029 SUPPORTED)
C4 significantly outperforms C1 AND C5 → RAG provides real adaptive value
- Action: Core thesis validated in 5-action space
- Next: Phase 2 RSM optimization of RAG parameters

### Outcome B: RAG = Random Rotation > Fixed (PARTIAL)
C4 ≈ C5 > C1 → Strategy switching helps but RAG selection not better than random
- Action: Strategy diversity valuable but RAG scoring adds no information
- Next: Investigate better situation features or scoring

### Outcome C: RAG = Best Fixed (H-029 REJECTED)
C4 ≈ C1 → RAG learns to always pick survival_burst (correctly)
- Action: RAG works but no practical value when one strategy dominates
- Next: Need scenarios where no single strategy is optimal

### Outcome D: All Equal (NULL)
No significant differences → 5-action space still too simple for RAG value
- Action: Core thesis likely needs fundamental revision
- Next: Consider multi-scenario or multi-map evaluation

## Statistical Analysis Plan
- One-way ANOVA with 5 groups
- Residual diagnostics: normality (Anderson-Darling), equal variance (Levene)
- Effect sizes: partial η²
- Planned contrasts with Bonferroni correction
- Kruskal-Wallis non-parametric confirmation if normality fails
- Power analysis for non-significant results
