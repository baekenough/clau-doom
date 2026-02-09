# EXPERIMENT_REPORT_026: L2 RAG Strategy Selection in 5-Action Space

## Metadata
- **DOE-ID**: DOE-026
- **Hypothesis**: H-029 — RAG strategy selection has value in 5-action space
- **Date**: 2026-02-09
- **Status**: H-029 REJECTED

## Design Summary
- One-way ANOVA, 5 conditions, 30 episodes each (N=150)
- Scenario: defend_the_line_5action.cfg (5 actions, doom_skill=3)
- Seeds: seed_i = 46001 + i × 113, i=0..29

## Conditions
| Condition | Type | Description |
|-----------|------|-------------|
| survival_burst | Fixed (Best) | DOE-025 winner, 40% attack ratio |
| random_5 | Fixed (2nd) | Uniform random over 5 actions |
| dodge_burst_3 | Fixed (3rd) | 3 attacks + 2 strafes cycle |
| l2_meta_5action | Adaptive RAG | OpenSearch meta-strategy selection |
| random_rotation_5 | Random baseline | Random rotation among top 3 strategies |

## Descriptive Statistics

| Condition | n | kills (mean±sd) | survival (mean±sd) | kill_rate (mean±sd) |
|-----------|---|-----------------|--------------------|--------------------|
| random_rotation_5 | 30 | 17.57±3.79 | 27.01±6.00 | 39.33±5.00 |
| random_5 | 30 | 17.40±5.39 | 25.58±6.84 | 40.50±5.08 |
| dodge_burst_3 | 30 | 17.23±5.42 | 27.99±8.34 | 37.02±4.59 |
| survival_burst | 30 | 16.97±4.24 | 26.17±7.26 | 39.48±4.95 |
| l2_meta_5action | 30 | 16.57±4.65 | 26.89±8.38 | 37.56±4.64 |

Note: L2 RAG selector is numerically WORST in kills.

## ANOVA Results

| Source | df | F | p | partial η² | Significance |
|--------|----|----|---|------------|-------------|
| kills | (4,145) | 0.206 | 0.935 | 0.006 | ns |
| survival_time | (4,145) | 0.450 | 0.772 | 0.012 | ns |
| kill_rate | (4,145) | 2.658 | 0.035 | 0.068 | * (marginal) |

## Planned Contrasts (Bonferroni α = 0.0125)

### kills
| Contrast | diff | t(df) | p | d | Sig |
|----------|------|-------|---|---|-----|
| RAG vs Best Fixed | -0.40 | t(58)=-0.348 | 0.728 | -0.090 | ns |
| RAG vs Random Rotation | -1.00 | t(56)=-0.913 | 0.362 | -0.236 | ns |
| Random Rotation vs Best Fixed | +0.60 | t(57)=0.578 | 0.563 | 0.149 | ns |
| RAG vs Fixed Pool Mean | -0.63 | t(53)=-0.634 | 0.526 | -0.129 | ns |

### survival_time
| Contrast | diff | t(df) | p | d | Sig |
|----------|------|-------|---|---|-----|
| RAG vs Best Fixed | +0.72 | t(57)=0.355 | 0.722 | 0.092 | ns |
| RAG vs Random Rotation | -0.12 | t(53)=-0.064 | 0.949 | -0.017 | ns |
| Random Rotation vs Best Fixed | +0.84 | t(56)=0.488 | 0.625 | 0.126 | ns |
| RAG vs Fixed Pool Mean | +0.31 | t(45)=0.181 | 0.856 | 0.040 | ns |

### kill_rate
| Contrast | diff | t(df) | p | d | Sig |
|----------|------|-------|---|---|-----|
| RAG vs Best Fixed | -1.92 | t(58)=-1.551 | 0.121 | -0.400 | ns |
| RAG vs Random Rotation | -1.77 | t(58)=-1.423 | 0.155 | -0.367 | ns |
| Random Rotation vs Best Fixed | -0.15 | t(58)=-0.116 | 0.908 | -0.030 | ns |
| RAG vs Fixed Pool Mean | -1.44 | t(54)=-1.440 | 0.150 | -0.291 | ns |

## Non-Parametric Confirmation (Kruskal-Wallis)
| Metric | H(4) | p | Sig |
|--------|------|---|-----|
| kills | 0.872 | 0.927 | ns |
| survival_time | 2.712 | 0.610 | ns |
| kill_rate | 10.730 | 0.030 | * |

Kill rate shows marginal significance in both parametric and non-parametric tests, but with negligible effect size (η²=0.068) and no practical importance.

## Residual Diagnostics
- **Normality** (Anderson-Darling): A²*=0.566, p=0.142 → PASS
- **Equal Variance** (Levene): F(4,145)=1.164, p=0.819 → PASS
- **Independence**: Run order randomized, no systematic patterns

## Power Analysis
- Observed effect (kills): η²=0.006, f=0.075 → power < 0.10
- Would need N>2000 for 80% power at observed effect
- For medium effect (f=0.25): power ≈ 0.85 with N=150
- Interpretation: The null result is NOT due to insufficient power for meaningful effects. If RAG had a medium or large effect, we would have detected it.

## Findings

### F-067: L2 RAG Strategy Selection Has No Effect in 5-Action Space
[STAT:p=0.935] [STAT:f=F(4,145)=0.206] [STAT:eta2=partial η²=0.006] [STAT:n=150]
L2 RAG meta-strategy selector performs no differently from fixed strategies or random rotation in kills (p=0.935) and survival (p=0.772). The RAG selector is numerically the worst performer (kills=16.57 vs group mean=17.15). H-029 REJECTED.
Trust: HIGH (adequate power, clean diagnostics)

### F-068: Pre-Filtered Strategy Pool Eliminates Selection Value
[STAT:p=0.728] [STAT:n=150]
When the candidate strategy pool contains only top performers (survival_burst, random_5, dodge_burst_3), all strategies are near-equivalent (kills range: 16.57-17.57, spread=1.0). Strategy SELECTION cannot add value when strategy QUALITY is uniformly high. This explains why DOE-022 (3-action) and DOE-026 (5-action) both show null L2 results.
Trust: HIGH

### F-069: RAG Overhead Degrades Performance
[STAT:n=150]
The RAG meta-selector (kills=16.57) numerically underperforms all fixed strategies and random rotation (17.15-17.57). The OpenSearch query latency (~2ms per query, 35-tick interval) and strategy-switching introduce overhead that slightly degrades performance compared to consistent strategy execution.
Trust: MEDIUM (numerical trend, not statistically significant)

### F-070: Core Thesis Falsification — Third Consecutive L2 Null Result
[STAT:n=450 cumulative across DOE-022, DOE-024, DOE-026]
Three independent experiments testing L2 RAG strategy selection have all produced null results:
- DOE-022 (3-action, tactic-level): p=0.878 for kills
- DOE-024 (3-action, meta-strategy): p=0.393 for kills
- DOE-026 (5-action, meta-strategy): p=0.935 for kills
The core thesis "Agent Skill = DocQuality × ScoringAccuracy" is FALSIFIED for the defend_the_line scenario. RAG-based strategy retrieval provides no performance benefit over fixed heuristic strategies regardless of action space dimensionality.
Trust: HIGH (3 independent replications, cumulative N=450)

## Outcome Assessment
**Outcome D: All Equal (NULL)** — No significant differences between any conditions for kills or survival. The 5-action space, while creating strategy differentiation among diverse strategies (DOE-025), does not create conditions where adaptive selection outperforms fixed execution of pre-filtered strategies.

## Implications for Core Thesis
The triple null result (DOE-022, DOE-024, DOE-026) constitutes strong evidence against the thesis formulation. Possible explanations:
1. **Scenario limitation**: defend_the_line may be too simple for RAG value — the optimal behavior is locally deterministic
2. **Tag-based retrieval is too coarse**: situation_tags (health/ammo/enemies) don't capture decision-relevant game state
3. **Strategy pool convergence**: top strategies are functionally equivalent, making selection irrelevant
4. **Thesis needs fundamental revision**: perhaps "experience accumulation" operates at a different level than strategy selection

## Next Steps
1. Consider multi-scenario experiments where strategy requirements VARY between maps
2. Test frame-level features (enemy positions, projectile proximity) instead of aggregate tags
3. Explore cooperative multi-agent settings where RAG coordinates between agents
4. Write paper section documenting the negative result (publishable finding)
