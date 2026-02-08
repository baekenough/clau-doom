# EXPERIMENT_REPORT_013: Attack Ratio Sweep

## Metadata
- **Experiment ID**: DOE-013
- **Hypothesis**: H-017
- **Experiment Order**: EXPERIMENT_ORDER_013.md
- **Date Executed**: 2026-02-08
- **Scenario**: defend_the_line.cfg (3-action)
- **Total Episodes**: 150 (5 conditions x 30 episodes)

## Design Summary

One-way completely randomized design testing 5 attack ratio levels on defend_the_line. Tests the relationship between attack-to-movement ratio and kill_rate to identify the optimal burst pattern.

| Condition | Attack Rate | Pattern | n |
|-----------|-------------|---------|---|
| burst_1_50pct | 50% | 1 attack + 1 turn | 30 |
| burst_3_75pct | 75% | 3 attacks + 1 turn | 30 |
| burst_5_83pct | 83% | 5 attacks + 1 turn | 30 |
| burst_7_88pct | 88% | 7 attacks + 1 turn | 30 |
| attack_only_100pct | 100% | Pure attack | 30 |

## Descriptive Statistics

| Condition | kill_rate (mean +/- SD) | kills (mean +/- SD) | survival (mean +/- SD) |
|-----------|------------------------|---------------------|------------------------|
| burst_1_50pct | 42.34 +/- 6.79 | 14.10 +/- 5.66 | 20.02 +/- 5.40 |
| burst_3_75pct | 43.07 +/- 6.07 | 13.40 +/- 4.95 | 18.80 +/- 5.19 |
| burst_5_83pct | 43.98 +/- 5.24 | 14.07 +/- 4.84 | 19.03 +/- 5.24 |
| burst_7_88pct | 42.65 +/- 5.16 | 13.40 +/- 4.76 | 18.91 +/- 5.54 |
| attack_only_100pct | 42.86 +/- 3.18 | 10.67 +/- 2.49 | 15.03 +/- 3.75 |

**Notable Pattern**: kill_rate values are remarkably similar across the 50-100% attack ratio spectrum (42.3-44.0 kr). All conditions cluster within 1.7 kr of each other. The SDs overlap substantially. This suggests attack ratio has minimal effect on kill_rate within this range.

## Primary Analysis: One-way ANOVA on kill_rate

### ANOVA Table

| Source | SS | df | MS | F | p | eta2 |
|--------|------|----|----|------|------|------|
| Strategy | 42.2 | 4 | 10.5 | 0.395 | 0.8120 | 0.0108 |
| Error | 3865.5 | 145 | 26.7 | | | |
| Total | 3907.7 | 149 | | | | |

**Result**: [STAT:f=F(4,145)=0.395] [STAT:p=0.8120] [STAT:eta2=eta^2=0.0108] -- **NOT SIGNIFICANT**

### Non-parametric Confirmation
- Kruskal-Wallis: H(4) = 1.865 [STAT:p=0.7607] -- confirms non-significance

### Residual Diagnostics

| Diagnostic | Test | Statistic | p-value | Result |
|-----------|------|-----------|---------|--------|
| Normality | Shapiro-Wilk | W=0.9925 | 0.7253 | **PASS** |
| Equal Variance | Levene | W=1.9478 | 0.1066 | **PASS** |

**Assessment**: ANOVA assumptions met. The non-significant result is valid.

### Statistical Power
- Cohen's f = 0.104 (very small effect)
- Achieved power: [STAT:power=0.146] (very low)
- **Interpretation**: The experiment had low power to detect the tiny effect that exists. However, the effect size itself (eta^2=0.011) indicates that attack ratio explains only 1% of kill_rate variance. Even with higher power, the practical significance would be negligible.

## Planned Contrasts

Despite the non-significant ANOVA, planned contrasts are reported for completeness. Bonferroni-corrected alpha = 0.05/5 = 0.01.

### C1: burst_1 vs burst_3
- burst_1 mean: 42.34, burst_3 mean: 43.07
- t = -0.463 [STAT:p=0.644] [STAT:effect_size=Cohen's d=-0.119] (negligible)
- Diff = -0.73 kr
- **NOT SIGNIFICANT**

### C2: burst_3 vs burst_5
- burst_3 mean: 43.07, burst_5 mean: 43.98
- t = -0.664 [STAT:p=0.508] [STAT:effect_size=Cohen's d=-0.171] (negligible)
- Diff = -0.91 kr
- **NOT SIGNIFICANT**

### C3: burst_5 vs burst_7
- burst_5 mean: 43.98, burst_7 mean: 42.65
- t = 1.173 [STAT:p=0.243] [STAT:effect_size=Cohen's d=0.302] (small)
- Diff = +1.33 kr
- **NOT SIGNIFICANT**

### C4: burst_7 vs attack_only
- burst_7 mean: 42.65, attack_only mean: 42.86
- t = -0.199 [STAT:p=0.843] [STAT:effect_size=Cohen's d=-0.051] (negligible)
- Diff = -0.21 kr
- **NOT SIGNIFICANT**

### C5: burst_1 vs attack_only
- burst_1 mean: 42.34, attack_only mean: 42.86
- t = -0.393 [STAT:p=0.695] [STAT:effect_size=Cohen's d=-0.088] (negligible)
- Diff = -0.52 kr
- **NOT SIGNIFICANT**

**Summary**: No pairwise comparison approaches significance. All effect sizes are negligible (|d| < 0.3). The attack ratio spectrum from 50% to 100% produces statistically indistinguishable kill_rate values.

## Tukey HSD Pairwise Comparisons

| Pair | Diff | p_adj | Cohen's d | Sig |
|------|------|-------|-----------|-----|
| burst_5 vs burst_7 | +1.33 | 0.8468 | +0.302 | |
| burst_5 vs burst_1 | +1.64 | 0.7101 | +0.346 | |
| burst_5 vs attack_only | +1.12 | 0.9052 | +0.256 | |
| burst_3 vs attack_only | +0.21 | 1.0000 | +0.047 | |
| burst_3 vs burst_7 | +0.42 | 0.9998 | +0.096 | |
| burst_3 vs burst_1 | +0.73 | 0.9906 | +0.166 | |
| burst_7 vs attack_only | -0.21 | 1.0000 | -0.051 | |
| burst_7 vs burst_1 | -0.31 | 0.9999 | -0.071 | |
| burst_1 vs attack_only | -0.52 | 0.9982 | -0.088 | |
| burst_5 vs burst_3 | +0.91 | 0.9705 | +0.207 | |

**No significant pairs** after Bonferroni correction. The largest difference is burst_5 vs burst_1 (+1.64 kr, d=0.35), which is small and non-significant (p_adj=0.71).

## Trend Analysis

| Trend | SS | df | MS | F | p |
|-------|----|----|----|----|---|
| Linear | 5.45 | 1 | 5.45 | 0.204 | 0.652 |
| Quadratic | 31.38 | 1 | 31.38 | 1.177 | 0.280 |
| Cubic | 4.98 | 1 | 4.98 | 0.187 | 0.666 |
| Quartic | 0.35 | 1 | 0.35 | 0.013 | 0.909 |

**Result**: No significant linear, quadratic, cubic, or quartic trend across the attack ratio spectrum. kill_rate is FLAT across 50-100%.

## Secondary Responses

### kills
- [STAT:f=F(4,145)=3.939] [STAT:p=0.0048] [STAT:eta2=eta^2=0.0980] -- **SIGNIFICANT**
- Normality: FAIL (Shapiro-Wilk p=0.048)
- Kruskal-Wallis: H(4) = 12.968 [STAT:p=0.0114] -- confirms significance
- Order (most to fewest): burst_1 (14.1) ~ burst_5 (14.1) > burst_3 (13.4) = burst_7 (13.4) > attack_only (10.7)
- Significant Tukey pairs: attack_only vs burst_1 (p=0.004, d=-0.98), attack_only vs burst_3 (p=0.015, d=-0.86), attack_only vs burst_5 (p=0.007, d=-0.92), attack_only vs burst_7 (p=0.029, d=-0.80)
- **Interpretation**: attack_only produces significantly FEWER total kills than all 4 burst conditions. The burst conditions (regardless of attack ratio) are indistinguishable from each other. Kills is driven by MOVEMENT presence, not attack frequency.

### survival_time
- [STAT:f=F(4,145)=4.315] [STAT:p=0.0026] [STAT:eta2=eta^2=0.1063] -- **SIGNIFICANT**
- Normality: PASS (Shapiro-Wilk p=0.070)
- Levene: PASS (p=0.262)
- Order (longest to shortest): burst_1 (20.0s) > burst_5 (19.0s) > burst_7 (18.9s) > burst_3 (18.8s) > attack_only (15.0s)
- Significant Tukey pairs: attack_only vs burst_1 (p=0.001, d=-1.07), attack_only vs burst_3 (p=0.019, d=-0.87), attack_only vs burst_5 (p=0.009, d=-0.92), attack_only vs burst_7 (p=0.025, d=-0.82)
- **Interpretation**: attack_only has significantly SHORTER survival than all burst conditions. The presence of ANY repositioning (even 1 turn per 8 ticks) extends survival by ~4s compared to pure attack. Survival differences among burst conditions are negligible.

### Cross-Response Pattern

| Condition | kill_rate rank | kills rank | survival rank |
|-----------|---------------|------------|---------------|
| burst_5_83pct | 1st (44.0) | 1st (14.1) | 2nd (19.0) |
| burst_3_75pct | 2nd (43.1) | 3rd (13.4) | 4th (18.8) |
| attack_only_100pct | 3rd (42.9) | 5th (10.7) | 5th (15.0) |
| burst_7_88pct | 4th (42.7) | 3rd (13.4) | 3rd (18.9) |
| burst_1_50pct | 5th (42.3) | 1st (14.1) | 1st (20.0) |

The kill_rate ranking is essentially random (range: 42.3-44.0 kr, all within noise). Kills and survival are dominated by the attack_only vs burst contrast (movement presence), not by attack ratio variation within bursts.

## Cross-Experiment Replication Check

| Condition | DOE-013 | Prior Experiment | Cohen's d | Status |
|-----------|---------|------------------|-----------|--------|
| burst_3_75pct | 43.07 (SD=6.07) | DOE-010: 44.55 (SD=6.39) | -0.238 | **REPLICATED** |
| attack_only_100pct | 42.86 (SD=3.18) | DOE-012: 42.99 (SD=2.61) | -0.045 | **REPLICATED** |

Both replication conditions are within 0.25 pooled SDs of prior values. Cross-experiment comparability is confirmed.

## Interpretation

### Key Discovery: Attack Ratio Does Not Affect Kill_Rate

The central finding of DOE-013 is that **attack ratio has NO significant effect on kill_rate** within the 50-100% range [STAT:p=0.812] [STAT:eta2=0.011]. All 5 conditions produce ~42-44 kr regardless of whether the agent attacks 50% of the time or 100% of the time.

**Why attack ratio doesn't matter for kill_rate**:
1. **Weapon cooldown is the limiting factor**: The pistol's ~8 tic cooldown imposes a ceiling on firing rate. Whether the agent attempts to attack 75% or 100% of the time, the weapon can only fire ~once every 8 ticks. The extra attack button presses above the cooldown-limited rate are wasted.
2. **Repositioning benefit is binary, not scalar**: The presence of ANY repositioning ticks (even 1 per 8 ticks in burst_7) is sufficient to maintain aiming. Increasing repositioning frequency from 12% (burst_7) to 50% (burst_1) provides no additional benefit for kill_rate.
3. **kill_rate = efficiency, not totals**: While attack_only produces fewer TOTAL kills (10.7 vs 13-14 for bursts), its shorter survival time (15.0s vs 18.8-20.0s) means the kill RATE is similar. The kills/survival tradeoff cancels out across the attack ratio spectrum.

### The Rate-vs-Total Tradeoff (Revisited)

DOE-011 identified this tradeoff for strafing (survival vs kill_rate). DOE-013 reveals it applies to attack ratio as well:

- **kill_rate**: FLAT across 50-100% attack ratio (p=0.812). Ratio doesn't matter.
- **Total kills**: Significantly LOWER for attack_only (p=0.005). Movement presence matters, not frequency.
- **Survival**: Significantly SHORTER for attack_only (p=0.003). Movement presence matters, not frequency.

The tradeoff: ANY movement extends survival and accumulates more kills, but kill_rate (efficiency) is insensitive to movement frequency as long as SOME movement exists.

### H-017 Disposition: REJECTED

H-017 predicted that higher attack ratio would produce higher kill_rate. The results show:

- **No monotonic relationship** [STAT:p=0.652 for linear trend]. kill_rate is FLAT across the spectrum.
- **No optimal peak**. All burst conditions (50-88%) produce indistinguishable kill_rate values.
- **attack_only (100%) is NOT superior** to burst strategies. It produces similar kill_rate but fewer total kills and shorter survival.

H-017 is REJECTED: Attack ratio does NOT affect kill_rate within the 50-100% range.

### Implications for Agent Design

1. **Attack ratio is a FREE parameter for kill_rate optimization**: Any ratio from 50% to 100% produces ~42-44 kr. Choose based on other objectives (survival, total kills, simplicity).
2. **burst_3 (75%) remains a good default**: It replicates across experiments, is simple to implement, and falls in the middle of the indifference range.
3. **Pure attack (100%) is SUBOPTIMAL for total performance**: While kill_rate is similar, attack_only sacrifices total kills and survival. If anything beyond kill_rate matters, include some movement.
4. **Movement presence is binary**: The presence of ANY repositioning ticks (even 12% in burst_7) is sufficient. Increasing to 50% (burst_1) provides no additional benefit.

### Recommended Next Steps

1. **Multi-objective optimization**: Since kill_rate is insensitive to attack ratio, use TOPSIS to weight kill_rate, kills, and survival. burst_1 may rank highest if survival is valued.
2. **Test L0 health threshold**: DOE-014 explores whether health-based dodge behavior (a different type of movement) affects kill_rate.
3. **Scenario generalization**: Test attack ratio sweep on a different scenario (e.g., health_gathering) to see if the flat kill_rate pattern holds universally.

## Findings

- **F-027**: Attack ratio does NOT significantly affect kill_rate [STAT:p=0.812]. All 5 conditions (50%, 75%, 83%, 88%, 100% attack rate) produce statistically indistinguishable kill_rate values (~42-44 kr). However, kills [STAT:p=0.005] and survival_time [STAT:p=0.003] ARE significant: attack_only produces fewer total kills and shorter survival because it never moves. ANY amount of movement (even 50% attack rate) extends survival and accumulates more kills. This extends F-024 (rate-vs-total tradeoff from DOE-011): kill_rate is robust to attack ratio variation in the [50-100%] range, while total kills depends on movement for survival.
- **H-017 REJECTED**: Higher attack ratio does NOT produce higher kill_rate. The relationship is FLAT across 50-100% [STAT:p=0.652 for linear trend]. Weapon cooldown and repositioning benefit saturation prevent attack ratio from affecting kill efficiency.

## Trust Assessment

| Aspect | Assessment |
|--------|-----------|
| ANOVA significance | p = 0.812 (clearly non-significant) |
| Diagnostics | Normality PASS, Levene PASS |
| Effect size | eta^2 = 0.011 (1% variance explained, negligible) |
| Power | 0.146 (low for this tiny effect) |
| Replication | Both anchors replicate (d < 0.25) |
| Overall Trust | **HIGH** for the null finding (F-027). Strong evidence that attack ratio has no practical effect on kill_rate. The non-significant result is robust: low effect size, clean diagnostics, cross-experiment replication. **HIGH** for secondary findings (kills, survival significant). |
