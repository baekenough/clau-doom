# EXPERIMENT_REPORT_008: Layer Ablation Study on defend_the_line

> **Report ID**: RPT-008
> **Experiment ID**: DOE-008
> **Hypothesis**: H-012 (HYPOTHESIS_BACKLOG.md)
> **Experiment Order**: EXPERIMENT_ORDER_008.md
> **Date Analyzed**: 2026-02-08
> **Author**: research-analyst
> **Status**: COMPLETE

---

## Executive Summary

DOE-008 replicated the DOE-007 layer ablation study on defend_the_line (higher kill ceiling: 4-26 kills/episode vs 0-3 on defend_the_center). Five architectural configurations were compared: random, L0_only, L0_memory, L0_strength, and full_agent.

**Primary Result**: The one-way ANOVA on kill_rate IS significant [STAT:f=F(4,145)=5.2560] [STAT:p=0.000555] [STAT:eta2=eta^2=0.1266]. The non-parametric Kruskal-Wallis test confirms significance [STAT:p=0.000465]. **Architectural configuration significantly affects kill_rate on defend_the_line.**

**Key Finding**: The significant effect is driven entirely by L0_only (pure reflex rules) performing dramatically WORSE than all other conditions (mean kill_rate=36.78 vs 42.22-43.35 for others). This is the opposite of DOE-007, where L0_only was the BEST performer. The pure rule-based agent that excelled in the simple scenario becomes the worst agent in the more complex scenario.

**Rank Order REVERSAL from DOE-007**:
- DOE-007 (defend_the_center): L0_only (best) > L0_memory > random > L0_strength > full_agent (worst)
- DOE-008 (defend_the_line): L0_memory > random > full_agent > L0_strength > **L0_only (worst)**

**Trust Level**: HIGH

---

## Data Summary

### Sample

| Property | Value |
|----------|-------|
| Total episodes | 150 |
| Episodes per condition | 30 |
| Invalid/excluded | 0 |
| Seed set | [6001, 6038, ..., 7074] (identical across all 5 conditions) |
| KILLCOUNT verified | Yes (kills range 4-26, not constant) |
| Scenario | defend_the_line |
| Zero-kill episodes | 0/150 (0%) |

### Descriptive Statistics: kill_rate (kills/min)

| Condition | n | Mean | SD | 95% CI | Median |
|-----------|---|------|-----|--------|--------|
| L0_memory | 30 | 43.35 | 6.59 | [40.89, 45.81] | 43.04 |
| random | 30 | 42.51 | 6.42 | [40.11, 44.91] | 43.18 |
| full_agent | 30 | 42.39 | 7.51 | [39.58, 45.20] | 41.88 |
| L0_strength | 30 | 42.22 | 5.90 | [40.02, 44.42] | 42.28 |
| **L0_only** | **30** | **36.78** | **4.87** | **[34.96, 38.60]** | **37.19** |

**Grand mean**: 41.45 kills/min [STAT:n=150]

### Descriptive Statistics: kills (count)

| Condition | n | Mean | SD | Min | Median | Max |
|-----------|---|------|-----|-----|--------|-----|
| L0_strength | 30 | 14.93 | 5.11 | 7 | 14.0 | 25 |
| L0_memory | 30 | 14.37 | 4.44 | 7 | 14.5 | 25 |
| random | 30 | 14.30 | 4.37 | 7 | 13.5 | 26 |
| full_agent | 30 | 11.90 | 3.77 | 6 | 12.0 | 21 |
| **L0_only** | **30** | **9.37** | **2.92** | **4** | **9.5** | **16** |

**Note**: Kill counts are substantially higher than DOE-007 (mean 12.97 vs 1.21 per episode). Zero-kill episodes: 0/150 (vs 14/150 = 9.3% in DOE-007). The defend_the_line scenario provides the discriminability that defend_the_center lacked.

### Descriptive Statistics: survival_time (seconds)

| Condition | n | Mean | SD |
|-----------|---|------|-----|
| L0_strength | 30 | 21.51 | 7.98 |
| random | 30 | 20.46 | 6.41 |
| L0_memory | 30 | 20.21 | 6.68 |
| full_agent | 30 | 17.13 | 5.62 |
| L0_only | 30 | 15.42 | 4.91 |

**Note**: L0_only survives the shortest. Full_agent also trends lower on survival. L0_strength and random survive longest.

### Descriptive Statistics: damage_taken

| Condition | n | Mean | SD |
|-----------|---|------|-----|
| L0_strength | 30 | 92.13 | 5.53 |
| full_agent | 30 | 90.23 | 5.72 |
| L0_memory | 30 | 89.60 | 5.86 |
| random | 30 | 89.13 | 8.45 |
| L0_only | 30 | 87.37 | 7.82 |

**Note**: No significant difference in damage_taken [STAT:f=F(4,145)=1.952] [STAT:p=0.105]. All agents absorb similar damage before death.

---

## Primary Analysis: One-Way ANOVA on kill_rate

### ANOVA Table

| Source | SS | df | MS | F | p | eta^2 |
|--------|------|-----|-------|--------|--------|-------|
| action_strategy | 850.25 | 4 | 212.56 | 5.2560 | 0.000555 | 0.1266 |
| Error | 5864.00 | 145 | 40.44 | | | |
| Total | 6714.25 | 149 | | | | |

[STAT:f=F(4,145)=5.2560] [STAT:p=0.000555] [STAT:eta2=eta^2=0.1266]

### Effect Sizes

| Measure | Value | Interpretation |
|---------|-------|----------------|
| eta-squared | 0.1266 | Medium-to-large |
| omega-squared | 0.1019 | Medium |
| Cohen's f | 0.3808 | Large |

**Conclusion**: The overall ANOVA IS significant at alpha=0.05. Action selection architecture significantly affects kill_rate in defend_the_line. The effect size is medium-to-large (eta^2=0.1266), indicating architecture explains 12.7% of kill_rate variance. This is 3x the effect size seen in DOE-007 (eta^2=0.042).

---

## Residual Diagnostics

### Normality

| Test | Statistic | p | Result |
|------|-----------|---|--------|
| D'Agostino-Pearson | 1.7625 | 0.414 | **PASS** |
| Shapiro-Wilk | W = 0.9955 | 0.931 | **PASS** |
| Anderson-Darling | A^2 = 0.1680 | > 0.15 | **PASS** (all significance levels) |

**All three normality tests PASS.** Residuals are normally distributed. This is a marked improvement over DOE-007 (where normality failed), attributable to the elimination of zero-kill episodes and the wider kill range in defend_the_line.

### Equal Variance

| Test | Statistic | p | Result |
|------|-----------|---|--------|
| Levene | W = 1.5577 | 0.189 | **PASS** |
| Bartlett | chi^2 = 5.5712 | 0.234 | **PASS** |

Both variance homogeneity tests PASS. Group standard deviations range from 4.87 (L0_only) to 7.51 (full_agent), a 1.54:1 ratio which is within acceptable bounds.

### Diagnostic Summary

**Both ANOVA assumptions are satisfied:**
1. **Normality**: PASS (all three tests p > 0.15)
2. **Equal variance**: PASS (Levene p = 0.189, Bartlett p = 0.234)

This is the first layer ablation experiment where all residual diagnostics PASS. The defend_the_line scenario eliminates the zero-inflation and floor compression that plagued DOE-007's diagnostics. ANOVA results can be interpreted with full confidence.

---

## Non-Parametric Co-Primary: Kruskal-Wallis

[STAT:p=0.000465]

| Statistic | Value |
|-----------|-------|
| H | 20.1577 |
| df | 4 |
| p | 0.000465 |

**Conclusion**: The Kruskal-Wallis test CONFIRMS the ANOVA result. The kill_rate distribution differs significantly across the five architectural conditions. Both parametric and non-parametric tests agree: the effect is real.

### Alexander-Govern Test (Robust Alternative)

| Statistic | Value |
|-----------|-------|
| stat | 24.2407 |
| p | 0.000071 |

The Alexander-Govern test (robust to heteroscedasticity) also confirms significance.

---

## Post-Hoc: Tukey HSD Pairwise Comparisons (kill_rate)

| Comparison | Mean Diff | p_adj | 95% CI | Reject |
|------------|-----------|-------|--------|--------|
| **L0_memory vs L0_only** | **+6.56** | **0.0009** | **[+2.06, +11.07]** | **Yes** |
| L0_memory vs L0_strength | +1.13 | 0.958 | [-3.38, +5.63] | No |
| L0_memory vs full_agent | +0.96 | 0.977 | [-3.55, +5.46] | No |
| L0_memory vs random | +0.84 | 0.986 | [-3.67, +5.35] | No |
| **L0_strength vs L0_only** | **+5.44** | **0.010** | **[+0.93, +9.94]** | **Yes** |
| **full_agent vs L0_only** | **+5.61** | **0.007** | **[+1.10, +10.11]** | **Yes** |
| **random vs L0_only** | **+5.72** | **0.005** | **[+1.22, +10.23]** | **Yes** |
| L0_strength vs full_agent | -0.17 | 1.000 | [-4.68, +4.34] | No |
| L0_strength vs random | -0.29 | 1.000 | [-4.79, +4.22] | No |
| full_agent vs random | -0.12 | 1.000 | [-4.62, +4.39] | No |

### Key Findings from Tukey HSD (kill_rate)

1. **L0_only is significantly WORSE than ALL other conditions** (all p_adj < 0.01)
2. **The other four conditions (L0_memory, random, full_agent, L0_strength) are statistically indistinguishable** (all p_adj > 0.95)
3. The effect is driven entirely by L0_only's deficit

### Tukey HSD on kills (count)

| Comparison | Mean Diff | p_adj | Reject |
|------------|-----------|-------|--------|
| **L0_memory vs L0_only** | **+5.00** | **0.0001** | **Yes** |
| **L0_strength vs L0_only** | **+5.57** | **< 0.0001** | **Yes** |
| **random vs L0_only** | **+4.93** | **0.0001** | **Yes** |
| full_agent vs L0_only | +2.53 | 0.138 | No |
| **L0_strength vs full_agent** | **+3.03** | **0.045** | **Yes** |
| L0_memory vs L0_strength | -0.57 | 0.985 | No |
| L0_memory vs full_agent | +2.47 | 0.157 | No |
| L0_memory vs random | +0.07 | 1.000 | No |
| L0_strength vs random | +0.63 | 0.977 | No |
| full_agent vs random | -2.40 | 0.179 | No |

**Notable**: On raw kills, full_agent vs L0_only is NOT significant (p=0.138), though their kill_rate difference IS significant (p=0.007). This discrepancy arises because full_agent has shorter survival time, inflating its kill_rate relative to raw kills. Also: L0_strength significantly outperforms full_agent on raw kills (p=0.045).

### Cohen's d for All Pairwise Comparisons (kill_rate)

| Comparison | Mean Diff | Cohen's d | Interpretation |
|------------|-----------|-----------|----------------|
| **L0_memory vs L0_only** | **+6.56** | **+1.132** | **Large** |
| L0_memory vs L0_strength | +1.13 | +0.180 | Negligible |
| L0_memory vs full_agent | +0.96 | +0.135 | Negligible |
| L0_memory vs random | +0.84 | +0.129 | Negligible |
| **L0_strength vs L0_only** | **+5.44** | **+1.005** | **Large** |
| **full_agent vs L0_only** | **+5.61** | **+0.885** | **Large** |
| **random vs L0_only** | **+5.72** | **+1.005** | **Large** |
| L0_strength vs full_agent | -0.17 | -0.025 | Negligible |
| L0_strength vs random | -0.29 | -0.047 | Negligible |
| full_agent vs random | -0.12 | -0.017 | Negligible |

All L0_only pairwise effects are LARGE (|d| >= 0.89). All non-L0_only pairwise effects are NEGLIGIBLE (|d| < 0.18).

---

## Planned Contrasts

### C1: random vs all structured (unstructured vs structured)

t = 0.9716, [STAT:p=0.333]

**Result**: NOT significant. Random performance (42.51) is not different from the average of structured approaches (41.19). On defend_the_line, random action selection remains competitive with all structured architectures.

### C2: L0_only vs {L0_memory, L0_strength, full_agent} (bare rules vs augmented rules)

t = -4.4512, [STAT:p=0.000019], d = -0.938

**Result**: HIGHLY significant. L0_only (36.78) performs significantly WORSE than augmented architectures (42.65). Cohen's d = -0.938 (large effect). Adding ANY heuristic to L0 rules substantially improves performance on defend_the_line. **This is the reverse of DOE-007 (defend_the_center), where C2 was non-significant (p=0.151) and L0_only was the best.**

### C3: {L0_memory, L0_strength} vs full_agent (single heuristic vs combined)

**kill_rate**: t = 0.2640, [STAT:p=0.792], d = 0.059 -- NOT significant. Single-heuristic agents (mean kill_rate 42.79) perform identically to the full combined pipeline (42.39).

**kills**: t = 2.759, [STAT:p=0.007], d = 0.487 -- SIGNIFICANT. Single-heuristic agents (mean kills 14.65) significantly outperform full_agent (11.90) on raw kills. The kill_rate non-significance arises because full_agent dies faster, partially compensating for fewer kills. Combined heuristics may induce excessive dodging.

### C4: L0_memory vs L0_strength (memory vs strength heuristic)

Embedded in Tukey HSD: Mean diff = +1.13, p_adj = 0.958, d = 0.180

**Result**: NOT significant. Memory dodge and strength modulation produce indistinguishable kill_rate outcomes. Consistent across both scenarios.

---

## Secondary Responses

### kills (count per episode)

[STAT:f=F(4,145)=9.2747] [STAT:p=0.000001] [STAT:eta2=0.2037]
Kruskal-Wallis: H=32.115, p=0.000002

HIGHLY significant. Eta-squared = 0.2037 (large effect). Architecture explains 20.4% of kill count variance. L0_only gets fewest kills (9.37 vs 11.9-14.9 for others).

### survival_time (seconds)

[STAT:f=F(4,145)=4.7993] [STAT:p=0.001153] [STAT:eta2=0.117]

Significant. L0_only survives shortest (15.42s vs 17.1-21.5s for others). L0_strength survives longest (21.51s).

### damage_taken (HP)

[STAT:f=F(4,145)=1.9521] [STAT:p=0.105] [STAT:eta2=0.051]

NOT significant. All agents absorb similar total damage (87-92 HP). The scenario kills all agents eventually; what differs is how much they accomplish before death.

**Summary**: kill_rate, kills, and survival_time all show significant architectural effects. damage_taken does not. The three significant responses converge on the same pattern: L0_only is the outlier performing worst.

---

## Power Analysis

| Property | Value |
|----------|-------|
| Observed Cohen's f | 0.3808 |
| Observed power | 0.9719 [STAT:power=0.97] |
| Power for small effect (f=0.10) | 0.18 |
| Power for medium effect (f=0.25) | 0.67 |
| Power for large effect (f=0.40) | 0.98 |
| MDE at power=0.80 | f = 0.29 |

**Interpretation**: The study achieved 97% power at the observed effect size (f=0.381). This is well-powered, far exceeding the 80% target. The observed effect is large, confirming that the defend_the_line scenario provided the discriminability needed. Compare to DOE-007: observed power was only 49% at f=0.209.

---

## Cross-Experiment Comparison: DOE-007 vs DOE-008

### Performance by Condition Across Scenarios

| Condition | DOE-007 kill_rate (defend_center) | DOE-008 kill_rate (defend_line) | Change | Cross-scenario d |
|-----------|-----------------------------------|----------------------------------|--------|-------------------|
| random | 8.54 | 42.51 | +33.97 | -5.80 |
| L0_only | 9.08 | 36.78 | +27.70 | -7.00 |
| L0_memory | 8.66 | 43.35 | +34.69 | -6.81 |
| L0_strength | 8.26 | 42.22 | +33.96 | -6.65 |
| full_agent | 6.74 | 42.39 | +35.65 | -5.93 |

All conditions show dramatically higher kill_rates on defend_the_line (4-5x higher), confirming the scenario provides much greater dynamic range.

**Critical observation**: L0_only has the SMALLEST improvement from scenario change (+27.70), while full_agent has the LARGEST (+35.65). The L0_only rules transfer poorly to defend_the_line, while the heuristic layers (and even random) adapt better.

### Rank Order Reversal

| Rank | DOE-007 (defend_center) | DOE-008 (defend_line) |
|------|-------------------------|-----------------------|
| 1 (best) | L0_only (9.08) | L0_memory (43.35) |
| 2 | L0_memory (8.66) | random (42.51) |
| 3 | random (8.54) | full_agent (42.39) |
| 4 | L0_strength (8.26) | L0_strength (42.22) |
| 5 (worst) | full_agent (6.74) | **L0_only (36.78)** |

**The rank order is dramatically different.** L0_only went from 1st (best) to 5th (worst). Full_agent went from 5th (worst) to 3rd. The relative performance of architectural layers is SCENARIO-DEPENDENT, not a fixed property.

### Discriminability Comparison

| Metric | DOE-007 (defend_center) | DOE-008 (defend_line) |
|--------|-------------------------|-----------------------|
| Kill range per episode | 0-3 | 4-26 |
| Grand mean kill_rate | 8.25 | 41.45 |
| Range of group means | 2.34 | 6.56 |
| Pooled SD | 3.92 | 6.32 |
| Range/Pooled SD | 0.598 | 1.039 |
| eta-squared | 0.042 | 0.127 |
| Cohen's f | 0.209 | 0.381 |
| ANOVA p-value | 0.183 | 0.000555 |
| Observed power | 49% | 97% |
| Zero-kill episodes | 14/150 (9.3%) | 0/150 (0%) |
| Normality PASS | No | **Yes** |
| Equal variance PASS | No | **Yes** |

Defend_the_line provides 1.7x better signal-to-noise ratio (Range/Pooled SD: 1.04 vs 0.60), 3x larger effect size (eta^2: 0.127 vs 0.042), and full diagnostic compliance.

### Full Agent Paradox: Partial Resolution

In DOE-007 (defend_the_center), full_agent was the WORST performer (mean=6.74, 20% zero-kill rate). In DOE-008 (defend_the_line), full_agent recovers to 3rd place (42.39, 0% zero-kill rate) and is statistically indistinguishable from L0_memory, L0_strength, and random on kill_rate.

However, on raw kills, full_agent still underperforms L0_strength significantly (p=0.045) and trends lower than L0_memory and random. The combined heuristics may still cause some performance penalty through excessive dodging, but the penalty is masked in kill_rate by the compensating shorter survival time.

---

## Trust Level Assessment

**Trust Level: HIGH**

### Trust Justification

**Strengths**:
- **All residual diagnostics PASS** (normality, equal variance -- first ablation experiment to achieve this)
- Balanced design (n=30 per condition, 150 total) [STAT:n=150]
- Identical seed set across all 5 conditions (strong internal validity)
- KILLCOUNT verified as real kills (not AMMO2)
- Both parametric and non-parametric tests agree on significance
- Alexander-Govern robust test confirms (p=0.000071)
- No outliers detected
- No zero-kill episodes (0% vs 9.3% in DOE-007)
- High achieved power: [STAT:power=0.97]
- p < 0.001 (well below alpha=0.05)
- Large effect size (eta^2=0.127, Cohen's f=0.381)

**Why HIGH**: All R100 checklist items satisfied. All residual diagnostics pass (first ablation experiment to achieve this). p < 0.01. Effect size large. Three independent tests (ANOVA, Kruskal-Wallis, Alexander-Govern) converge on significance.

---

## Interpretation (Statistical Only)

### Overall Pattern

The data show a clear pattern:

```
L0_memory ~ random ~ full_agent ~ L0_strength >> L0_only
```

L0_only is the sole outlier, performing significantly worse than all other conditions by large effect sizes (d = 0.89 to 1.13). The remaining four conditions form a statistically homogeneous group with mean kill_rate approximately 42.6 kills/min.

### L0_only Deficit: Why Rules Hurt on defend_the_line

L0_only uses three fixed rules:
1. health < 30 -> move_left (flee)
2. ammo == 0 -> move_left (seek ammo)
3. else -> attack

On defend_the_center (DOE-007), this was the best strategy: enemies come from all directions, and "always attack" is near-optimal for a few enemies in an open arena. Kill counts were 0-3 regardless of strategy.

On defend_the_line, enemies approach in a LINE from in front. The "else -> attack" rule means L0_only commits to attacking ONE enemy at a time without sweeping (turning) across multiple targets. The flee-left rules (health < 30, ammo == 0) also point the agent away from the enemy line, losing precious attack time.

The other architectures avoid this trap:
- **random**: 33% attack, 33% turn_left, 33% turn_right -- provides natural sweeping behavior across the enemy line
- **L0_memory**: L0 rules + memory dodge adds lateral movement, creating incidental sweeping
- **L0_strength**: L0 rules + probabilistic attack (attack_prob=0.675) means 32.5% of the time the agent dodges instead of attacking, again creating sweeping
- **full_agent**: Both heuristics combined provide dodging and probabilistic attack

### Mechanistic Decomposition

| Mechanism | Effect on kill_rate | Evidence |
|-----------|---------------------|----------|
| Lateral movement (any source) | +5.7 kills/min vs L0_only | C2 contrast: d = -0.938, p = 0.000019 |
| Memory dodge specifically | No additional benefit vs random | L0_memory vs random: d = 0.129 (negligible) |
| Strength modulation specifically | No additional benefit vs random | L0_strength vs random: d = -0.047 (negligible) |
| Combined heuristics | No additional benefit vs random | full_agent vs random: d = -0.017 (negligible) |

The performance hierarchy is:
1. Having ANY lateral movement >> pure forward-attacking rules
2. The SOURCE of lateral movement does not matter (random, memory dodge, strength modulation all equivalent)
3. The heuristic layers add no value BEYOND the lateral movement they incidentally produce

### Consistency with Prior Experiments

DOE-008 reveals a critical scenario dependency:
- **DOE-007 (defend_center)**: All architectures indistinguishable (p=0.183). Scenario too simple.
- **DOE-008 (defend_line)**: Significant effect (p=0.000555), driven by L0_only deficit, not heuristic superiority.
- **DOE-005/006**: No memory/strength parameter effect at any range [0.3, 0.9]. Confirmed: the heuristics' value is not in their tuned parameters but in the lateral movement they incidentally produce.

---

## Statistical Markers Summary

| Marker | Value |
|--------|-------|
| [STAT:f] | F(4,145) = 5.2560 |
| [STAT:p] | p = 0.000555 |
| [STAT:eta2] | eta^2 = 0.1266 (medium-to-large) |
| [STAT:n] | n = 150 (30 per group) |
| [STAT:power] | observed power = 0.97 |
| [STAT:effect_size] | Cohen's f = 0.381 (large) |
| Kruskal-Wallis | H(4) = 20.158, p = 0.000465 |
| Alexander-Govern | stat = 24.241, p = 0.000071 |
| C1 (random vs structured) | t = 0.972, p = 0.333 |
| C2 (L0_only vs augmented) | t = -4.451, p = 0.000019, d = -0.938 |
| C3 (single vs combined, kill_rate) | t = 0.264, p = 0.792, d = 0.059 |
| C3 (single vs combined, kills) | t = 2.759, p = 0.007, d = 0.487 |
| C4 (memory vs strength) | p_adj = 0.958, d = 0.180 |
| kills ANOVA | F(4,145) = 9.275, p = 0.000001, eta^2 = 0.204 |
| survival_time ANOVA | F(4,145) = 4.799, p = 0.001, eta^2 = 0.117 |
| damage_taken ANOVA | F(4,145) = 1.952, p = 0.105 (NS) |

---

## Recommendations for PI

1. **H-012 Disposition**: The scenario replication SUCCEEDS. Defend_the_line reveals significant architectural differences that defend_the_center masked. H-012 is SUPPORTED. Recommend ADOPT with HIGH trust.

2. **Finding F-010**: The significant effect is driven by L0_only's deficit, not by heuristic superiority. The finding should state: "Pure reflex rules (L0_only) are significantly inferior to architectures with lateral movement on defend_the_line." The corollary: adding any source of lateral movement (random, memory dodge, or strength modulation) provides equivalent large benefit over pure rules.

3. **Finding F-011 (kills-specific)**: On raw kills, full_agent underperforms single-heuristic agents (C3 p=0.007, d=0.487). Combined heuristics may cause excessive dodging, reducing kills and survival. This is a weaker finding (moderate effect, present only on kills not kill_rate).

4. **L0_only Performance Paradox**: L0_only went from BEST (DOE-007) to WORST (DOE-008). This is a scenario-specific interaction: the fixed "attack" rule creates tunnel vision that is harmless on defend_the_center but catastrophic on defend_the_line. This is a scientifically important finding about rule-based agent generalization.

5. **Random Agent Competitiveness**: Random remains competitive (2nd place). The heuristic layers provide no advantage over random lateral movement. This challenges the project thesis that structured decision-making provides value -- at least with the current 3-action space and heuristic design.

6. **Next Steps**:
   - Investigate whether restructuring L0 rules (e.g., adding turn-toward-nearest-enemy) resolves the L0_only deficit
   - Test on a third scenario for further generalization evidence
   - Consider expanding action space (e.g., move_forward, move_backward) to give heuristics more expressive power
   - Redesign heuristics to provide intentional targeting behavior rather than incidental lateral movement
   - Standardize on defend_the_line for future experiments given superior diagnostic properties

---

## Audit Trail

| Document | ID | Status |
|----------|----|--------|
| Hypothesis | H-012 | SUPPORTED (pending PI adoption) |
| Experiment Order | EXPERIMENT_ORDER_008.md | COMPLETED |
| Experiment Report | This document (RPT-008) | COMPLETE |
| Findings | F-010, F-011 pending PI adoption | |
| Research Log | Entry logged 2026-02-08 | |
