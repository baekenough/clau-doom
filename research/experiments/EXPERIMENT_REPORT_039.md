# Experiment Report: DOE-039

## Experiment Metadata

**Experiment ID**: DOE-039
**Order File**: EXPERIMENT_ORDER_039.md
**Hypothesis**: H-039 (HYPOTHESIS_BACKLOG.md)
**Date Executed**: 2026-02-10
**Scenario**: predict_position.cfg
**Analyst**: research-analyst
**Model**: opus

## Experiment Design

**Design Type**: Two-condition comparison (random movement vs pure attack)

**Conditions**:
- `random` (random_3): Random action selection from 3 actions including turns
- `attack_raw`: Pure attack strategy (PureAttackAction), no turning, health_override=False

**Sample Size**: n=30 episodes per condition (60 total episodes)

**Design Rationale**: Test whether the predict_position scenario is viable for discriminating agent strategies. Previous experiments used defend_the_line or defend_the_center. This scenario was expected to require predictive positioning against moving enemies.

## Results Summary

### Primary Outcome: Kills

**Descriptive Statistics**:
- Random: mean=0.067, sd=0.254, median=0.0, range=[0, 1]
- Attack_raw: mean=0.000, sd=0.000, median=0.0, range=[0, 0]

**Inferential Statistics**:
- Welch's t-test: [STAT:t(29)=1.439, p=0.161]
- Mann-Whitney U: [STAT:U=480.0, p=0.161]
- Cohen's d: [STAT:d=0.378] (small-to-medium effect, but non-significant)
- Mean difference: [STAT:diff=+0.067 kills, 95% CI: -0.023 to +0.156]

**Conclusion**: No significant difference in kills between random and attack_raw [STAT:p=0.161]. Both conditions produced near-zero kills.

### Secondary Outcome: Survival Time

**Descriptive Statistics**:
- Random: mean=1.65s, sd=0.14s
- Attack_raw: mean=60.00s, sd=0.00s

**Inferential Statistics**:
- Welch's t-test: [STAT:t=-2284.0, p<0.001]
- Interpretation: attack_raw survived entire episode duration (60s timeout), while random died almost immediately (mean survival 1.65s)

**Conclusion**: Attack_raw survives significantly longer [STAT:p<0.001], but this is an artifact of game timeout, not meaningful survival.

### Zero-Kill Rate

- Random: 28/30 episodes (93.3%) with zero kills
- Attack_raw: 30/30 episodes (100%) with zero kills

**Interpretation**: Both strategies effectively failed to kill any enemies. The scenario is too difficult or both strategies are inappropriate.

### Shots Fired

- Random: mean=0.0 (no shots fired)
- Attack_raw: mean=0.0 (no shots fired)

**Interpretation**: Neither strategy fired any shots, indicating both failed to engage enemies at all.

## Residual Diagnostics

### Normality Tests

**Shapiro-Wilk Test**:
- Random kills: [STAT:W=0.275, p<0.001] → FAIL (non-normal)
- Attack_raw kills: [STAT:W=1.000, p=1.000] → Degenerate (all zeros)

**Assessment**: Both distributions are severely non-normal. Random has extreme zero-inflation (93.3%), attack_raw is constant (100%). Parametric tests are inappropriate, but non-parametric tests (Mann-Whitney U) confirm no significant difference.

### Equal Variance Test

**Levene's Test**: [STAT:F=2.071, p=0.155] → PASS

**Assessment**: Equal variance assumption technically met, but both variances are near-zero.

### Independence

**Assessment**: Episodes used fixed seed sets with random assignment. Independence assumption is met by design.

## Effect Sizes

**Cohen's d**: [STAT:d=0.378] (small-to-medium)
**Practical Significance**: Even if statistically significant, a difference of 0.067 kills (95% CI: -0.023 to +0.156) is negligible.

## Power Analysis

**Achieved Power**: [STAT:power=0.30] at observed effect size (d=0.378)
**Sample Size**: [STAT:n=30] per condition
**Minimum Detectable Effect (MDE)**: At 80% power with n=30, MDE ≈ d=0.74 (medium-large effect)

**Interpretation**: The experiment was underpowered to detect the observed small-to-medium effect (d=0.378). However, even if the effect were real, the absolute difference (0.067 kills) is too small to be meaningful. **Power is not the limiting factor; the scenario itself is not discriminatory.**

## Statistical Markers Summary

| Metric | Value | Interpretation |
|--------|-------|---------------|
| [STAT:t] | 1.439 | t-statistic |
| [STAT:p] | 0.161 | Not significant (α=0.05) |
| [STAT:d] | 0.378 | Small-to-medium effect |
| [STAT:diff] | +0.067 | Mean difference (random - attack_raw) |
| [STAT:ci] | -0.023 to +0.156 | 95% confidence interval |
| [STAT:power] | 0.30 | Underpowered |
| [STAT:n] | 30 | Per condition |

## Trust Level

**UNTRUSTED**

**Rationale**:
1. Non-significant result [STAT:p=0.161]
2. Zero-inflation in both conditions (93-100%)
3. Both strategies failed to engage enemies (0 shots fired)
4. Scenario appears broken or too difficult
5. Survival time difference is timeout artifact, not meaningful

## Findings

### F-039: predict_position Scenario is Not Viable

**Hypothesis**: H-039 (predict_position discriminates strategies)
**Experiment Order**: DOE-039
**Experiment Report**: RPT-039
**Trust Level**: UNTRUSTED

**Evidence**:
- Random vs attack_raw comparison: [STAT:p=0.161] (not significant)
- Both strategies achieved near-zero kills (93-100% zero-inflation)
- Neither strategy fired any shots [STAT:mean_shots=0.0]
- Survival time difference is timeout artifact (1.65s vs 60s)

**Interpretation**:
The predict_position scenario is not suitable for agent evaluation. Both random movement and pure attack strategies failed to engage enemies. Possible causes:
1. Enemies may be too fast or too evasive
2. Map geometry may prevent line-of-sight
3. Weapon mechanics may be inappropriate for this scenario
4. Agent decision loop may not be detecting enemy presence

**Recommendation**: **REJECT** predict_position as a viable scenario. Revert to defend_the_line for future experiments.

## Recommendations

### For Future Experiments

1. **Do not use predict_position scenario** for agent evaluation
   - Zero-kill rate indicates broken scenario or inappropriate mechanics
   - No discrimination between strategies

2. **Revert to defend_the_line scenario** (established as viable in DOE-008)
   - Proven to discriminate between strategies
   - Reasonable kill rates (4-26 kills/episode)
   - Good diagnostic properties (normal residuals, equal variance)

3. **If investigating new scenarios**, pre-test with baseline agent
   - Ensure non-zero kills achievable
   - Verify shots fired > 0
   - Check enemy engagement mechanics

4. **For predict_position debugging** (if scenario must be used):
   - Investigate why shots_fired = 0
   - Check enemy detection logic
   - Review map geometry and line-of-sight
   - Consider weapon range and enemy speed parameters

### Next Experiment

**Recommended**: Return to defend_the_line scenario for DOE-040+ experiments.

**Rationale**: DOE-008 established defend_the_line as viable (p=0.000555, strong discrimination). predict_position is not a viable alternative based on DOE-039 results.

## Audit Trail

- Hypothesis: H-039 (HYPOTHESIS_BACKLOG.md)
- Order: EXPERIMENT_ORDER_039.md
- Report: EXPERIMENT_REPORT_039.md (this document)
- Finding: F-039 (UNTRUSTED, reject predict_position scenario)
- Date: 2026-02-10

## Data Quality

**Completeness**: 60/60 episodes recorded (100%)
**Seed Sets**: Fixed seeds used, reproducible
**Execution Errors**: None
**Data Integrity**: Verified via DuckDB queries

## Appendix: Raw Data Summary

```
=== Random (n=30) ===
  kills: mean=0.067, sd=0.254, median=0.0, min=0, max=1
  survival_time: mean=1.65s, sd=0.14s, median=1.67s, min=1.14s, max=1.89s
  kill_rate: mean=3.27 kr, sd=12.48, median=0.0, min=0, max=52.5
  shots_fired: mean=0.0, sd=0.0
  zero_kills: 28/30 (93.3%)

=== Attack_raw (n=30) ===
  kills: mean=0.0, sd=0.0, median=0.0, min=0, max=0
  survival_time: mean=60.0s, sd=0.0, median=60.0s (timeout)
  kill_rate: mean=0.0 kr, sd=0.0
  shots_fired: mean=0.0, sd=0.0
  zero_kills: 30/30 (100%)
```

---

**End of Report**
