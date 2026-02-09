# EXPERIMENT_REPORT_025.md

## RPT-025: 5-Action Strategy Optimization Results

**Experiment Order**: DOE-025 (EXPERIMENT_ORDER_025.md)
**Hypothesis**: H-028 — 5-action strategies create separable performance tiers
**Date**: 2026-02-09
**Analyst**: research-analyst (automated)

---

## Design Summary

| Parameter | Value |
|-----------|-------|
| Type | One-way ANOVA (6 conditions) |
| Scenario | defend_the_line_5action.cfg |
| Actions | 5 (TURN_LEFT, TURN_RIGHT, MOVE_LEFT, MOVE_RIGHT, ATTACK) |
| Difficulty | doom_skill=3 |
| Episodes per condition | 30 |
| Total episodes | 180 |
| Seed formula | seed_i = 45001 + i × 107 |
| Runtime | 31.7 seconds |

---

## Summary Statistics

| Strategy | n | kills (mean±sd) | kill_rate (mean±sd) | survival (mean±sd) |
|----------|---|-----------------|---------------------|--------------------|
| survival_burst | 30 | 19.63±7.37 | 39.24±4.74 | 30.10±10.79 |
| random_5 | 30 | 18.13±6.09 | 41.70±5.83 | 26.35±9.24 |
| dodge_burst_3 | 30 | 17.43±5.66 | 39.54±3.84 | 26.75±9.34 |
| strafe_burst_3 | 30 | 17.07±3.89 | 41.57±5.54 | 24.88±5.94 |
| adaptive_5 | 30 | 15.53±5.42 | 42.84±5.95 | 22.02±7.69 |
| smart_5 | 30 | 13.73±4.47 | 39.55±5.91 | 21.25±7.74 |
| **Grand Mean** | **180** | **16.92** | **40.74** | **25.22** |

---

## ANOVA Results

### kills (Total Kill Count)

| Source | SS | df | MS | F | p | η² |
|--------|------|-----|-------|--------|----------|--------|
| Strategy | 579.92 | 5 | 115.98 | 4.057 | 0.001654 | 0.1044 |
| Error | 4974.67 | 174 | 28.59 | | | |
| Total | 5554.58 | 179 | | | | |

**Conclusion**: Strategy has significant main effect on kills [STAT:p=0.0017] [STAT:F(5,174)=4.057] [STAT:eta2=0.104]

### kill_rate (Kills per Minute)

| Source | SS | df | MS | F | p | η² |
|--------|------|-----|-------|--------|----------|--------|
| Strategy | 327.60 | 5 | 65.52 | 2.323 | 0.045007 | 0.0626 |
| Error | 4907.51 | 174 | 28.20 | | | |
| Total | 5235.11 | 179 | | | | |

**Conclusion**: Strategy has marginal effect on kill_rate [STAT:p=0.045] [STAT:F(5,174)=2.323] [STAT:eta2=0.063]. Not significant at Bonferroni-corrected α=0.01.

### survival_time (Seconds Alive)

| Source | SS | df | MS | F | p | η² |
|--------|------|-----|-------|--------|----------|--------|
| Strategy | 1530.15 | 5 | 306.03 | 4.350 | 0.000936 | 0.1111 |
| Error | 12240.85 | 174 | 70.35 | | | |
| Total | 13771.00 | 179 | | | | |

**Conclusion**: Strategy has highly significant main effect on survival [STAT:p=0.0009] [STAT:F(5,174)=4.350] [STAT:eta2=0.111]

---

## Non-Parametric Confirmation (Kruskal-Wallis)

Residual normality failed for kills (AD=2.974) and survival_time (AD=3.611). Non-parametric tests confirm:

| Variable | H statistic | p-value | Confirms ANOVA? |
|----------|-------------|---------|-----------------|
| kills | 20.385 | 0.001058 | YES |
| survival_time | 20.642 | 0.000946 | YES |

---

## Residual Diagnostics

| Variable | Normality (A-D) | Equal Variance (Levene) |
|----------|-----------------|------------------------|
| kills | FAIL (AD=2.974) | PASS (p=0.173) |
| kill_rate | PASS (AD=0.280) | PASS (p=0.493) |
| survival_time | FAIL (AD=3.611) | PASS (p=0.205) |

**Note**: Normality violations for kills and survival_time mitigated by Kruskal-Wallis confirmation and adequate sample size (n=30 per group, CLT applies).

---

## Power Analysis

| Variable | Effect size (f) | Non-centrality | Power (1-β) |
|----------|-----------------|----------------|-------------|
| kills | 0.341 | 21.0 | 0.956 |
| survival_time | 0.354 | 22.5 | 0.968 |

Both analyses have excellent statistical power (>0.95).

---

## Planned Contrasts

### C1: Random vs All Structured (kills)
- Difference: +1.45 (random higher)
- p = 0.2138, d = 0.248
- **Result**: NOT SIGNIFICANT. Random remains competitive in 5-action space.

### C2: strafe_burst_3 vs dodge_burst_3 (kills)
- Difference: -0.37
- p = 0.7711, d = -0.077
- **Result**: NOT SIGNIFICANT. Reducing attack from 75% to 60% has negligible effect.

### C3: survival_burst vs strafe_burst_3 (survival_time)
- Difference: +5.22 seconds (survival_burst lives longer)
- p = 0.0237, d = 0.610
- **Result**: MEDIUM EFFECT but not significant at Bonferroni α=0.01. Trend toward survival advantage.

### C4: adaptive_5 vs non-adaptive (kill_rate)
- Difference: +2.52 (adaptive higher kill_rate)
- p = 0.0203, d = 0.454
- **Result**: MEDIUM EFFECT but not significant at Bonferroni α=0.01. Adaptive has higher kill efficiency when alive but survives less.

---

## Significant Pairwise Comparisons (Bonferroni-corrected α=0.0033)

### kills
| Pair | Difference | p-value |
|------|-----------|---------|
| random_5 vs smart_5 | +4.40 | 0.002297 |
| smart_5 vs strafe_burst_3 | -3.33 | 0.003172 |
| smart_5 vs survival_burst | -5.90 | 0.000414 |

### survival_time
| Pair | Difference | p-value |
|------|-----------|---------|
| adaptive_5 vs survival_burst | -8.08 | 0.001462 |
| smart_5 vs survival_burst | -8.85 | 0.000565 |

---

## Key Findings

### F-062: 5-Action Strategy Differentiates Kills
Strategy type has significant main effect on total kills in the 5-action space [STAT:p=0.0017] [STAT:F(5,174)=4.057] [STAT:eta2=0.104]. Unlike the 3-action space where random was near-optimal (F-018), structured strategies now create meaningful performance tiers.

### F-063: 5-Action Strategy Differentiates Survival
Strategy type has highly significant main effect on survival time [STAT:p=0.0009] [STAT:F(5,174)=4.350] [STAT:eta2=0.111]. Strafing-heavy strategies enable longer survival, confirming and extending DOE-011 finding F-023.

### F-064: Survival-First Paradox
survival_burst (40% attack ratio) achieves highest kills (19.63) AND longest survival (30.10s), while strafe_burst_3 (75% attack) achieves fewer kills (17.07) and shorter survival (24.88s). **Defensive play enables more killing time**, inverting the expected attack-focused optimality.

### F-065: State-Dependent Heuristics Degrade Performance
smart_5 is the worst performer in kills (13.73) — significantly worse than random_5 (p=0.002), strafe_burst_3 (p=0.003), and survival_burst (p<0.001). The state-dependent "if kill → dodge, if miss → scan" heuristic actively hurts performance in the 5-action space.

### F-066: Adaptive Health-Responsiveness Trades Survival for Kill Efficiency
adaptive_5 shows highest kill_rate (42.84/min) but shortest survival after smart_5 (22.02s). Health-responsive switching increases per-second lethality but reduces total output due to lower survival.

---

## Hypothesis Assessment

**H-028**: PARTIALLY SUPPORTED

5-action strategies DO form separable performance tiers for both kills (p=0.0017) and survival (p=0.0009), matching **Outcome A** partially. However:
- The gradient does NOT align with attack ratio as predicted
- survival_burst (40% attack) outperforms strafe_burst_3 (75% attack)
- Random remains competitive (Outcome E partially applies)
- State-dependent heuristics hurt (contradicts Outcome D)

**Trust Level**: HIGH (confirmed by non-parametric tests, power >0.95, Levene PASS)

---

## Implications for Core Thesis

The finding that 5-action strategies differentiate while 3-action strategies don't (F-018 vs F-062) supports the interpretation that the 3-action space was too constrained for RAG to add value (explanation (a) from F-061). This reopens the possibility of testing RAG in the 5-action space where strategy selection actually matters.

---

## Next Steps

1. **DOE-026**: Test L2 RAG strategy selection in the 5-action space
   - Use top 3 strategies from DOE-025 as RAG candidates
   - Test whether RAG can learn to switch between strategies based on game state
2. Investigate why survival-first strategies paradoxically maximize kills
3. Explore multi-objective optimization (Pareto front of kills vs survival)
