# EXPERIMENT_REPORT_011: Expanded Action Space (5-Action) Strategy Differentiation

## Metadata
- **Experiment ID**: DOE-011
- **Hypothesis**: H-015
- **Experiment Order**: EXPERIMENT_ORDER_011.md
- **Date Executed**: 2026-02-08
- **Scenario**: defend_the_line.cfg (3-action) and defend_the_line_5action.cfg (5-action)
- **Total Episodes**: 150 (5 conditions x 30 episodes)

## Design Summary

One-way completely randomized design testing 5 action strategy levels across two action spaces (3-action and 5-action) on defend_the_line. Tests whether expanding from 3 actions (turn_left, turn_right, attack) to 5 actions (add move_left, move_right for strafing) enables meaningful strategy differentiation.

| Condition | Action Space | Strategy | Attack Rate | n |
|-----------|-------------|----------|-------------|---|
| random_3 | 3-action | Uniform random | 33% | 30 |
| random_5 | 5-action | Uniform random | 20% | 30 |
| turn_burst_3 | 3-action | 3 attacks + 1 random turn | 75% | 30 |
| strafe_burst_3 | 5-action | 3 attacks + 1 random strafe | 75% | 30 |
| smart_5 | 5-action | Phase-based aim-attack-dodge | ~60% | 30 |

## Descriptive Statistics

| Condition | kill_rate (mean +/- SD) | kills (mean +/- SD) | survival (mean +/- SD) |
|-----------|------------------------|---------------------|------------------------|
| turn_burst_3 | 45.49 +/- 4.38 | 13.40 +/- 4.34 | 17.60 +/- 5.42 |
| random_3 | 43.27 +/- 8.06 | 11.47 +/- 3.26 | 16.18 +/- 4.56 |
| strafe_burst_3 | 42.11 +/- 4.18 | 16.07 +/- 5.82 | 22.99 +/- 8.30 |
| smart_5 | 41.74 +/- 6.22 | 13.00 +/- 4.68 | 18.94 +/- 7.25 |
| random_5 | 39.74 +/- 6.13 | 17.33 +/- 6.18 | 26.35 +/- 8.76 |

**Notable Pattern**: kill_rate and kills/survival are INVERSELY ordered. The highest kill_rate conditions (turn_burst_3, random_3) have the FEWEST raw kills and SHORTEST survival. The lowest kill_rate condition (random_5) has the MOST raw kills and LONGEST survival. This paradox is explained by strafing: strafing extends survival dramatically (random_5 survives 63% longer than random_3), and more survival time means more kills in absolute terms, but the kill RATE (kills per minute) is lower because attack frequency is diluted by strafing actions.

## Primary Analysis: One-way ANOVA on kill_rate

### ANOVA Table

| Source | SS | df | MS | F | p | eta2 |
|--------|------|----|----|------|------|------|
| Strategy | 537.0 | 4 | 134.2 | 3.774 | 0.005969 | 0.094 |
| Error | 5158.3 | 145 | 35.6 | | | |
| Total | 5695.2 | 149 | | | | |

**Result**: [STAT:f=F(4,145)=3.774] [STAT:p=0.005969] [STAT:eta2=eta^2=0.094] -- **SIGNIFICANT**

### Non-parametric Confirmation
- Kruskal-Wallis: H(4) = 13.002 [STAT:p=0.011268] -- confirms significance

### Residual Diagnostics

| Diagnostic | Test | Statistic | p-value | Result |
|-----------|------|-----------|---------|--------|
| Normality | Shapiro-Wilk | W=0.9898 | 0.3464 | **PASS** |
| Equal Variance | Levene | W=3.8992 | 0.0049 | **FAIL** |

**Levene Note**: Variance heterogeneity is present (max SD/min SD = 8.06/4.18 = 1.93, approaching 2x threshold). The 3-action conditions (random_3 SD=8.06, turn_burst_3 SD=4.38) have heterogeneous variance, while 5-action conditions are more uniform (4.18-6.22). Kruskal-Wallis non-parametric test confirms significance. Welch's t-tests used for all planned contrasts (robust to unequal variance). Tukey HSD with equal group sizes (n=30 each) is moderately robust to this level of heteroscedasticity.

### Statistical Power
- Cohen's f = 0.323 (medium-to-large effect)
- Achieved power: [STAT:power=0.894] (good)
- MDE at 80% power: f = 0.29

## Planned Contrasts

All contrasts use Welch's t-test (robust to unequal variance). Bonferroni-corrected alpha = 0.05/5 = 0.01.

### C1: Dilution (random_3 vs random_5)
- random_3 mean: 43.27, random_5 mean: 39.74
- Welch's t = 1.914 [STAT:p=0.061] [STAT:effect_size=Cohen's d=0.494] (medium)
- Diff = +3.54 kr (random_3 higher)
- **NOT SIGNIFICANT** after Bonferroni correction (p=0.061 > 0.01)
- Borderline: expanding to 5 actions with random selection TRENDS toward lower kill_rate, but does not reach significance. The 20% attack rate (vs 33%) and diversion of actions to strafing creates a dilution effect that is moderate in size but inconsistent.

### C2: Strafe Value (strafe_burst_3 vs turn_burst_3)
- strafe_burst_3 mean: 42.11, turn_burst_3 mean: 45.49
- Welch's t = -3.056 [STAT:p=0.003] [STAT:effect_size=Cohen's d=-0.789] (medium-large)
- Diff = -3.38 kr (strafe WORSE than turn)
- **SIGNIFICANT** after Bonferroni correction (p=0.003 < 0.01)
- **KEY FINDING**: Replacing the turn repositioning with strafe repositioning between burst windows REDUCES kill_rate. Strafing (physical lateral movement) is LESS effective than turning (rotational aiming) for between-burst repositioning. This makes tactical sense: turning between bursts scans new enemies into the crosshair, while strafing moves the body without reorienting the aim.

### C3: Strategy Differentiation (smart_5 vs random_5)
- smart_5 mean: 41.74, random_5 mean: 39.74
- Welch's t = 1.260 [STAT:p=0.213] [STAT:effect_size=Cohen's d=0.325] (small)
- Diff = +2.01 kr (smart_5 slightly higher)
- **NOT SIGNIFICANT** (p=0.213 > 0.01)
- The coordinated aim-attack-dodge strategy does NOT significantly outperform random in the 5-action space. The intelligent phase-based approach provides only a small, unreliable advantage over uniform random selection.

### C4: Cross-Space (3-action vs 5-action overall)
- 3-action mean: 44.38 (n=60), 5-action mean: 41.20 (n=90)
- Welch's t = 3.091 [STAT:p=0.003] [STAT:effect_size=Cohen's d=0.523] (medium)
- Diff = +3.18 kr (3-action higher)
- **SIGNIFICANT** after Bonferroni correction (p=0.003 < 0.01)
- **KEY FINDING**: The 3-action space produces HIGHER kill_rate overall than the 5-action space. Expanding the action space HURTS kill_rate, regardless of strategy. The additional strafing actions divert ticks away from aiming and attacking.

### C5: 5-Action Strategy Comparison (smart_5 vs strafe_burst_3)
- smart_5 mean: 41.74, strafe_burst_3 mean: 42.11
- Welch's t = -0.269 [STAT:p=0.789] [STAT:effect_size=Cohen's d=-0.070] (negligible)
- Diff = -0.37 kr (virtually identical)
- **NOT SIGNIFICANT** (p=0.789)
- The two 5-action strategies are statistically indistinguishable. Neither the burst-with-strafe nor the intelligent aim-attack-dodge approach gains any advantage over the other.

## Tukey HSD Pairwise Comparisons

| Pair | Diff | p_adj | Cohen's d | Sig |
|------|------|-------|-----------|-----|
| random_5 vs turn_burst_3 | +5.75 | 0.0025 | +1.081 | * |
| smart_5 vs turn_burst_3 | +3.75 | 0.1125 | +0.696 | |
| random_3 vs random_5 | +3.54 | 0.1515 | +0.494 | |
| strafe_burst_3 vs turn_burst_3 | +3.38 | 0.1880 | +0.789 | |
| random_5 vs strafe_burst_3 | +2.38 | 0.5363 | +0.453 | |
| random_3 vs turn_burst_3 | +2.22 | 0.6037 | +0.342 | |
| random_5 vs smart_5 | +2.01 | 0.6892 | +0.325 | |
| random_3 vs smart_5 | +1.53 | 0.8578 | +0.213 | |
| random_3 vs strafe_burst_3 | +1.16 | 0.9429 | +0.181 | |
| smart_5 vs strafe_burst_3 | +0.37 | 0.9993 | +0.070 | |

**Only one significant pair** (p_adj < 0.05): random_5 < turn_burst_3 (d=1.081, large effect). The overall ANOVA significance is driven primarily by the spread between the best 3-action strategy (turn_burst_3) and the worst 5-action strategy (random_5).

## Secondary Responses

### kills
- [STAT:f=F(4,145)=6.936] [STAT:p=0.000039] [STAT:eta2=eta^2=0.161] -- **HIGHLY SIGNIFICANT**
- Kruskal-Wallis: H(4) = 23.405 [STAT:p=0.000105] -- confirms
- Order (most to fewest): random_5 (17.3) > strafe_burst_3 (16.1) > turn_burst_3 (13.4) > smart_5 (13.0) > random_3 (11.5)
- Significant Tukey pairs: random_5 > random_3 (p=0.0001), random_5 > smart_5 (p=0.008), random_5 > turn_burst_3 (p=0.022), strafe_burst_3 > random_3 (p=0.004)
- **Interpretation**: 5-action conditions produce MORE raw kills because agents survive longer. Strafing extends life, which accumulates more kills in absolute terms even though kill efficiency (kills/minute) is lower.

### survival_time
- [STAT:f=F(4,145)=10.548] [STAT:p=0.000000] [STAT:eta2=eta^2=0.225] -- **HIGHLY SIGNIFICANT**
- Kruskal-Wallis: H(4) = 36.316 [STAT:p=0.000000] -- confirms
- Order (longest to shortest): random_5 (26.3s) > strafe_burst_3 (23.0s) > smart_5 (18.9s) > turn_burst_3 (17.6s) > random_3 (16.2s)
- Significant Tukey pairs: random_5 > random_3 (p<0.001), random_5 > turn_burst_3 (p<0.001), random_5 > smart_5 (p=0.001), strafe_burst_3 > random_3 (p=0.002), strafe_burst_3 > turn_burst_3 (p=0.029)
- **Interpretation**: Strafing provides substantial survival benefit. random_5 survives 63% longer than random_3 (+10.2s). Strafing physically displaces the agent, making it harder for enemies to hit. This is the largest effect in the entire experiment (eta^2=0.225).

### Cross-Response Pattern

| Condition | kill_rate rank | kills rank | survival rank |
|-----------|---------------|------------|---------------|
| turn_burst_3 | 1st (45.5) | 3rd (13.4) | 4th (17.6) |
| random_3 | 2nd (43.3) | 5th (11.5) | 5th (16.2) |
| strafe_burst_3 | 3rd (42.1) | 2nd (16.1) | 2nd (23.0) |
| smart_5 | 4th (41.7) | 4th (13.0) | 3rd (18.9) |
| random_5 | 5th (39.7) | 1st (17.3) | 1st (26.3) |

The rank inversions between kill_rate and raw kills/survival reveal a **rate-vs-total tradeoff**: strafing extends survival and accumulates more total kills, but each minute of survival is less kill-efficient because strafing ticks displace attack/aim ticks. The kill_rate metric captures killing efficiency; raw kills capture total lethality over an episode.

## Cross-Experiment Replication Check (vs DOE-010)

| Condition | DOE-011 | DOE-010 | Cohen's d | Status |
|-----------|---------|---------|-----------|--------|
| random_3 | 43.27 (SD=8.06) | 42.16 (SD=6.74) | 0.150 | **REPLICATED** |
| turn_burst_3 | 45.49 (SD=4.38) | 44.55 (SD=6.39) | 0.172 | **REPLICATED** |

Both replication conditions are within 0.2 pooled SDs of DOE-010 values. Cross-experiment comparability is confirmed.

## Interpretation

### Key Discovery: Strafing is a Double-Edged Sword

The central finding of DOE-011 is that strafing (physical lateral movement) has profoundly different effects on different metrics:

1. **Strafing INCREASES survival** (eta^2=0.225, largest effect): Physical displacement makes the agent harder to hit. random_5 survives 63% longer than random_3.

2. **Strafing DECREASES kill_rate** (C4: d=0.523): Every tick spent strafing is a tick NOT spent aiming or attacking. The 5-action space inherently dilutes offensive actions.

3. **Strafing INCREASES total kills** (eta^2=0.161): Despite lower efficiency, longer survival accumulates more total kills. random_5 gets 51% more kills than random_3 in absolute terms.

### The Rate-vs-Total Paradox

This experiment reveals a fundamental tension in the kill_rate metric. The "best" strategy depends on what you optimize:

- **Maximize kill_rate**: Use 3-action space with burst strategy (turn_burst_3 = 45.5 kr). Short, violent life.
- **Maximize total kills**: Use 5-action space with random selection (random_5 = 17.3 kills). Long, steady life.
- **Maximize survival**: Use 5-action space with random selection (random_5 = 26.3s). Strafing is the best defense.

### H-015 Disposition: PARTIALLY REJECTED

H-015 predicted that expanding the action space would enable strategy differentiation, with smart_5 outperforming random_5. The results show:

- **Action space expansion DID create differentiation** — between action spaces (C4: p=0.003), not within them. 3-action and 5-action form distinct performance tiers on kill_rate.
- **Intelligent strategy did NOT outperform random** within the 5-action space (C3: p=0.213, d=0.325). smart_5 matches random_5 but cannot beat it.
- **Strafing is WORSE than turning** for burst repositioning (C2: p=0.003, d=-0.789). The hypothesis assumed strafing would add value; instead it reduces kill_rate.
- **The predicted outcome was C** (from EXPERIMENT_ORDER_011): "random_3 >= smart_5 > random_5" — this is close to what was observed (turn_burst_3 > random_3 > smart_5 ~ strafe_burst_3 > random_5), though the smart_5 vs random_5 gap is not significant.

### Implications for Agent Design

1. **Do NOT expand action space for kill_rate optimization**: The 3-action space (turn_left, turn_right, attack) is superior for kill efficiency. Adding strafing dilutes attack frequency.
2. **Consider multi-objective optimization**: If survival matters alongside kill_rate, strafing is valuable. A TOPSIS-weighted objective could balance the tradeoff.
3. **Turning > strafing for between-burst repositioning**: Turning reorients the crosshair toward new enemies; strafing moves the body without changing aim direction.
4. **Random remains near-optimal within each action space**: smart_5 does not beat random_5; burst strategies only match random in their respective spaces. The action space itself is the primary determinant.
5. **Burst strategies replicate across experiments**: turn_burst_3 at 45.5 kr (DOE-011) matches DOE-010's burst_3 at 44.6 kr (d=0.17). This is a stable, reliable strategy.

### Recommended Next Steps

1. **Multi-objective TOPSIS analysis**: Weight kill_rate, kills, and survival_time to determine Pareto-optimal strategies across action spaces.
2. **Test compound actions**: Simultaneous attack + turn (if VizDoom supports it) could achieve both high attack rate AND aiming.
3. **Scale test**: Run turn_burst_3 at larger n to narrow confidence intervals, since it consistently ranks highest on kill_rate.
4. **New scenario**: Test on a scenario where survival is rewarded (not just kill efficiency) to see if strafing strategies dominate.

## Findings

- **F-020**: Expanding from 3-action to 5-action space REDUCES kill_rate overall [STAT:p=0.003] [STAT:effect_size=Cohen's d=0.523]. 3-action mean=44.38 kr vs 5-action mean=41.20 kr. Strafing actions dilute attack frequency.
- **F-021**: Strafing between burst windows is WORSE than turning for kill_rate [STAT:p=0.003] [STAT:effect_size=Cohen's d=-0.789]. Turn repositioning scans new enemies; strafe repositioning does not change aim direction.
- **F-022**: Intelligent 5-action strategy (smart_5) does NOT outperform random_5 [STAT:p=0.213] [STAT:effect_size=Cohen's d=0.325]. H-015 partially rejected: action space expansion does not enable strategy differentiation within the 5-action space.
- **F-023**: Strafing dramatically increases survival time [STAT:f=F(4,145)=10.548] [STAT:p<0.000001] [STAT:eta2=0.225]. random_5 survives 63% longer than random_3 (+10.2s). Physical displacement provides the best defense.
- **F-024**: Kill_rate and total kills are INVERSELY ranked across conditions. The rate-vs-total tradeoff means strategy selection depends on the optimization objective. Multi-objective optimization (TOPSIS) is needed.

## Trust Assessment

| Aspect | Assessment |
|--------|-----------|
| ANOVA significance | p = 0.006, confirmed by Kruskal-Wallis (p = 0.011) |
| Diagnostics | Normality PASS, Levene FAIL (1.93x SD ratio) |
| Effect size | eta^2 = 0.094, Cohen's f = 0.323 (medium) |
| Power | 0.894 (good) |
| Replication | Both DOE-010 anchors replicate (d < 0.2) |
| Overall Trust | **HIGH** (for significant findings F-020, F-021); note Levene violation is compensated by Kruskal-Wallis confirmation and Welch's t-tests for contrasts. **MEDIUM** for null findings (F-022) due to moderate power for small effects. |
