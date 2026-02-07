# Trial 1: Statistical Rigor Validation Report

> **Date**: 2026-02-07
> **Validator**: research-pi (Principal Investigator)
> **Scope**: All 5 experiment orders (DOE-001 through DOE-005)
> **Validation Dimensions**: Power, Seeds, Methods, Corrections, Assumptions, Effect Sizes, Trust, Randomization

---

## Executive Summary

| DOE | Verdict | Critical | Major | Minor | Note |
|-----|---------|----------|-------|-------|------|
| DOE-001 | **CONDITIONAL** | 0 | 2 | 1 | 2 |
| DOE-002 | **PASS** | 0 | 0 | 2 | 2 |
| DOE-003 | **PASS** | 0 | 1 | 1 | 1 |
| DOE-004 | **PASS** | 0 | 0 | 2 | 1 |
| DOE-005 | **CONDITIONAL** | 0 | 2 | 2 | 1 |
| **Cross-cutting** | -- | 0 | 1 | 2 | 0 |
| **TOTAL** | | **0** | **6** | **10** | **7** |

**Overall Verdict**: **ADEQUATE WITH REVISIONS RECOMMENDED**

No critical issues were found. Six major issues require attention before execution to ensure statistical conclusions will be defensible. All experiment designs are scientifically sound in their core structure. The issues identified are refinements to analytic plans and sample size justifications, not fundamental redesigns.

---

## Validation Methodology

Each DOE was evaluated against 8 dimensions:

1. **Power Analysis**: Sample size adequacy, explicit power calculations, sensitivity to effect size assumptions
2. **Seed Design**: Collision-free seeds, adequate coverage, reproducibility guarantees
3. **Statistical Method Choice**: Appropriate test for design type, assumptions match data characteristics
4. **Multiple Comparison Correction**: Family-wise error rate control, correction method appropriateness
5. **ANOVA Assumptions**: Likelihood of normality, homoscedasticity, independence holding
6. **Effect Size Framework**: Appropriate metrics, meaningful thresholds, practical significance
7. **Trust Score Framework**: Criteria clarity, achievability, consistency across DOEs
8. **Blocking/Randomization**: Adequate control of nuisance variables, temporal effects

---

## DOE-001: Baseline Comparison (OFAT)

### 1. Power Analysis

**Finding**: Power calculation is well-justified but has a methodological mismatch.

The order states [STAT:n=70] per group for detecting Cohen's d >= 0.50 with Welch's t-test at [STAT:alpha=0.05] and [STAT:power=0.80]. The G*Power reference calculation (n=64, rounded to 70) is correct for a two-group t-test.

**Issue DOE001-M1 (MAJOR)**: The experiment has 3 groups (Random, Rule-Only, Full RAG) but the power analysis is computed for a two-group Welch's t-test. When performing 3 pairwise comparisons with Holm-Bonferroni correction, the effective alpha for the first test is alpha/3 = 0.0167. Power at this adjusted alpha is lower than the stated 0.80.

- At alpha_eff = 0.0167, n = 70, d = 0.50: [STAT:power~0.70], which falls below the 0.80 target.
- To achieve power = 0.80 at the adjusted significance level for the smallest expected effect (Full RAG vs Rule-Only, d = 0.50-1.0): n ~ 85-90 per group would be needed for d = 0.50 specifically.
- For the larger expected effects (d > 1.0 for Full RAG vs Random), n = 70 is more than adequate even with correction.

**Recommendation**: Either (a) increase n to 85 per group (total 255 episodes), or (b) acknowledge in the order that power for the H-002 comparison (Full RAG vs Rule-Only, expected d ~ 0.50) is approximately 0.70 after correction. Given the adaptive stopping rule already allows extension to n=100, option (b) with a note is acceptable.

**Severity**: MAJOR -- Power shortfall for the most critical comparison (H-002).

### 2. Seed Design

**Finding**: Seed formula `seed_i = 42 + i*31` for i=0..69 produces 70 unique seeds in [42, 2181]. Arithmetic sequence with prime step guarantees no internal collisions. One cross-experiment collision with DOE-002 (seed 1592), documented and assessed as negligible.

**Issue DOE001-N1 (NOTE)**: The S2-01 design document specified a different master seed set. DOE-001 uses formula-based seeds instead. This is documented in the Phase 5 verification (I-005) but not yet fixed in the experiment order itself.

**Verdict**: PASS (seed design is sound).

### 3. Statistical Method Choice

**Finding**: Welch's t-test for pairwise comparisons is appropriate given unequal variances are expected across conditions (Random will have very different variance characteristics than Full RAG). The non-parametric fallback (Mann-Whitney U) is correctly specified.

**Issue DOE001-M2 (MAJOR)**: The Statistical Analysis Plan lists "Five pairwise comparisons" but only specifies 3 comparisons (C1, C2, C3). The text says "3 comparisons x 7 metrics = 21 tests" for Holm-Bonferroni correction. The inconsistency ("Five" vs "3") should be resolved. If 7 response variables are each tested across 3 comparisons, the family of 21 tests is correct but aggressive. Consider separating the primary response (kill_rate, 3 comparisons) from secondary responses (6 metrics x 3 comparisons = 18 tests) with separate family-wise corrections.

**Recommendation**: Clarify that the primary analysis family is 3 comparisons on kill_rate (adjusted alpha = 0.05/3 = 0.017 for Holm step 1). Secondary analyses (survival_time, kills, etc.) should be corrected within their own family or labeled as exploratory.

**Severity**: MAJOR -- Ambiguity in the comparison count and overly conservative correction if all 21 tests are in one family.

### 4. Multiple Comparison Correction

**Finding**: Holm-Bonferroni is specified. This is appropriate -- it controls family-wise error rate while being less conservative than Bonferroni.

**Issue DOE001-m1 (MINOR)**: The correction family size (21 tests) may be too large if primary and secondary responses are pooled. Standard practice is to correct within response variable families (3 comparisons per response) or designate one primary response with formal correction and treat others as exploratory.

### 5. ANOVA Assumptions

**Finding**: Not directly applicable (t-tests, not ANOVA). Welch's t-test does not assume equal variances. Normality is checked via Anderson-Darling with Mann-Whitney fallback. This is appropriate.

**Issue DOE001-N2 (NOTE)**: The kill_rate metric (kills/minute) may exhibit floor effects for the Random agent (many episodes with 0 kills, short survival), producing a highly right-skewed or zero-inflated distribution. The Anderson-Darling test will likely reject normality for the Random condition. The Mann-Whitney fallback is correctly specified for this scenario. Consider also reporting bootstrap confidence intervals for robustness.

**Verdict**: PASS (assumptions framework is adequate with fallback).

### 6. Effect Size Framework

**Finding**: Cohen's d thresholds (< 0.20 negligible, 0.20-0.49 small, 0.50-0.79 medium, >= 0.80 large) are standard and appropriate. Expected effect sizes are plausible given the design.

**Verdict**: PASS.

### 7. Trust Score Framework

**Finding**: Trust scores are not explicitly defined for DOE-001 (it uses the project-wide framework from R100). The expected outcomes table and contingency plans are thorough.

**Verdict**: PASS.

### 8. Blocking/Randomization

**Issue DOE001-m2 (MINOR -- borderline MAJOR)**: Run order is fixed (Random -> Rule-Only -> Full RAG) rather than randomized, justified by container reconfiguration overhead. While identical seed sets mitigate most confounding, a fixed order introduces risk of temporal confounding (e.g., system warm-up, background process interference, resource contention changing over a 2-3 hour run).

**Recommendation**: Either randomize run order (preferred) or interleave blocks (e.g., 10 episodes Random, 10 Rule-Only, 10 Full RAG, repeat 7 times). If sequential is necessary, document the risk and consider run-order analysis as a covariate.

**Severity**: MINOR (mitigated by seed design, but sub-optimal).

### DOE-001 Summary

| Dimension | Verdict | Issues |
|-----------|---------|--------|
| Power Analysis | CONDITIONAL | DOE001-M1 (power after correction ~0.70 for H-002) |
| Seed Design | PASS | DOE001-N1 (S2-01 divergence documented) |
| Statistical Method | CONDITIONAL | DOE001-M2 (comparison count ambiguity) |
| Multiple Comparison | MINOR ISSUE | DOE001-m1 (family size too large) |
| ANOVA Assumptions | PASS | DOE001-N2 (floor effects expected, fallback available) |
| Effect Size | PASS | -- |
| Trust Framework | PASS | -- |
| Randomization | MINOR ISSUE | DOE001-m2 (fixed run order) |

---

## DOE-002: Memory x Strength Factorial

### 1. Power Analysis

**Finding**: Power justification states n=30 per cell for 2^2 factorial ANOVA detecting medium effect f=0.25 at [STAT:alpha=0.05] yields [STAT:power~0.85] for main effects and [STAT:power~0.80] for interaction. This is standard.

Verification: For a balanced 2-way ANOVA with 2 levels per factor:
- df_effect = 1, df_error = 116
- At f = 0.25, alpha = 0.05, n = 30 per cell: power ~ 0.83 for main effects.
- For interaction (also df=1): power ~ 0.83.

The stated values are reasonable. The center point power (~0.70 for curvature) is correctly noted as lower.

**Verdict**: PASS.

### 2. Seed Design

**Finding**: Formula `seed_i = 1337 + i*17` for i=0..29 produces 30 unique seeds in [1337, 1830]. One cross-experiment collision with DOE-001 (seed 1592), documented.

**Issue DOE002-N1 (NOTE)**: Center points use subsets of the same 30 seeds (CP1: seeds[0..9], CP2: seeds[10..19], CP3: seeds[20..29]). This is efficient but means center points and factorial cells share seeds. For the factorial cells, all 30 seeds are used per cell, while center points use 10 each. This is clearly documented and correctly designed.

**Verdict**: PASS.

### 3. Statistical Method Choice

**Finding**: 2-way ANOVA with Type III SS is appropriate for the 2^2 design. The curvature test (t-test comparing factorial mean vs center point mean) is correctly specified. Non-parametric fallback (Aligned Rank Transform ANOVA) is appropriate.

**Verdict**: PASS.

### 4. Multiple Comparison Correction

**Finding**: Tukey HSD is specified for post-hoc comparisons if interaction is significant, which is correct. For a 2^2 design with significant interaction, simple effects analysis is the right approach.

**Issue DOE002-m1 (MINOR)**: The order does not specify correction for testing multiple response variables (kill_rate + 5 secondary responses). If all 6 responses are analyzed with the same ANOVA model, there are 6 x 3 (main effects + interaction) = 18 F-tests. Recommend designating kill_rate as the primary response with formal significance testing and labeling secondary responses as exploratory.

**Verdict**: PASS with minor note.

### 5. ANOVA Assumptions

**Finding**: Standard diagnostic triplet (normality, equal variance, independence) is correctly specified. The 2^2 balanced design is robust to mild violations of normality (Central Limit Theorem applies well at n=30).

**Issue DOE002-N2 (NOTE)**: Kill_rate may not be normally distributed within cells (ratio of count to time). At n=30, CLT provides reasonable protection, but log-transformation should be considered if distributions are right-skewed.

**Verdict**: PASS.

### 6. Effect Size Framework

**Finding**: Partial eta-squared thresholds (small: 0.01, medium: 0.06, large: 0.14) are Cohen's standard benchmarks for ANOVA. Cohen's d for pairwise comparisons also specified. Both are appropriate.

**Verdict**: PASS.

### 7. Trust Score Framework

**Finding**: Not explicitly defined in DOE-002 order (relies on project-wide framework). Expected outcomes include predicted effect sizes and p-values, which is good practice.

**Verdict**: PASS.

### 8. Blocking/Randomization

**Finding**: Run order is randomized with center points interspersed. This is well-designed. The randomization sequence is explicitly provided (execution order: Run 3, CP1, Run 1, Run 4, CP2, Run 2, CP3). This controls for temporal effects effectively.

**Issue DOE002-m2 (MINOR)**: Within each run, episodes are executed sequentially using seeds in order. This is standard but introduces within-run temporal ordering. Given that each run is only 30 episodes (~30 minutes), this is acceptable.

**Verdict**: PASS.

### DOE-002 Summary

| Dimension | Verdict | Issues |
|-----------|---------|--------|
| Power Analysis | PASS | -- |
| Seed Design | PASS | DOE002-N1 (center point seed subsets, by design) |
| Statistical Method | PASS | -- |
| Multiple Comparison | MINOR | DOE002-m1 (multiple responses not corrected) |
| ANOVA Assumptions | PASS | DOE002-N2 (kill_rate distribution, CLT adequate) |
| Effect Size | PASS | -- |
| Trust Framework | PASS | -- |
| Randomization | PASS | DOE002-m2 (within-run sequential, acceptable) |

---

## DOE-003: Decision Layer Ablation (2^3 Factorial)

### 1. Power Analysis

**Finding**: States n=30 per cell for 2^3 factorial ANOVA at f=0.30, [STAT:alpha=0.05], targeting [STAT:power=0.80]. With 8 cells and 240 total episodes:
- df_error = 240 - 8 = 232
- For main effects (df=1): power at f=0.30 is approximately 0.90 (higher than stated 0.82)
- For two-way interactions (df=1): power at f=0.30 is similarly ~0.88
- For the three-way interaction (df=1): power ~ 0.88

The stated power values (~0.82 for main effects, ~0.75 for interactions) appear conservative. Actual power should be higher given the large error df. This is not an issue -- understating power is conservative and safe.

**Issue DOE003-M1 (MAJOR)**: The "No Layers" condition (Run 8: L0=OFF, L1=OFF, L2=OFF) always produces the default action (MOVE_FORWARD). This creates a near-deterministic floor condition with extremely low variance. In a factorial ANOVA, this cell will violate the equal variance assumption (Levene's test will likely fail). The "No Layers" cell is qualitatively different from all other cells -- it is not a natural extension of the factor levels but rather a degenerate condition.

**Recommendation**: Consider one of:
(a) Exclude the "No Layers" condition from the factorial ANOVA and analyze it separately as a floor reference (reduce to 7 conditions, or treat as a 2^3 - 1 design).
(b) Keep all 8 conditions but expect and plan for Levene's test failure. Use Welch's ANOVA or the Aligned Rank Transform as the primary analysis.
(c) Replace the "No Layers" condition with a "Random Action" condition (which has some variance) to maintain ANOVA assumptions.

Option (a) is recommended: analyze the 7 non-degenerate conditions in the factorial ANOVA, and separately compare each condition against the No Layers floor using Welch's t-test.

**Severity**: MAJOR -- The degenerate cell will contaminate the error estimate in the factorial ANOVA.

### 2. Seed Design

**Finding**: Formula `seed_i = 2023 + i*23` for i=0..29 produces 30 unique seeds in [2023, 2690]. No cross-experiment collisions found. All 8 conditions use the same 30 seeds, enabling paired comparisons.

**Verdict**: PASS.

### 3. Statistical Method Choice

**Finding**: 2^3 factorial ANOVA is the correct design for testing 3 binary factors. Planned contrasts (Full Stack vs Best Single Layer, Full Stack vs Best Two-Layer) are well-chosen and scientifically meaningful. Post-hoc Tukey HSD across all 28 pairwise comparisons is comprehensive.

**Issue DOE003-m1 (MINOR)**: The planned contrasts select "max(L0 Only, L1 Only, L2 Only)" and "max(L0+L1, L0+L2, L1+L2)" as comparators. These are data-dependent contrasts (choosing the best performer after observing data). Pre-specifying contrasts that depend on observed outcomes inflates Type I error. Consider either (a) pre-specifying the expected best single-layer (L0) and best two-layer (L0+L2) as fixed contrasts, or (b) using Scheffe's method which allows post-hoc complex contrasts with proper correction.

**Severity**: MINOR -- The contrasts are scientifically reasonable but technically non-standard.

### 4. Multiple Comparison Correction

**Finding**: Tukey HSD for all 28 pairwise comparisons at alpha=0.05 is conservative but appropriate for exploratory pairwise analysis. The decision gate uses a single pre-specified comparison (Full Stack vs L0 Only) which does not require correction.

**Verdict**: PASS.

### 5. ANOVA Assumptions

**Finding**: See Issue DOE003-M1 above. The "No Layers" condition will likely violate equal variance and normality assumptions. Otherwise, the 7 non-degenerate conditions should produce reasonable variance homogeneity.

**Issue DOE003-N1 (NOTE)**: The L1 Only and L2 Only conditions may have unusual performance distributions. L1 Only relies solely on DuckDB cache, which may be empty at the start of the experiment (cold start problem). If the cache is pre-populated from previous experiments, this should be documented. If not, early episodes will behave like "No Layers" until the cache accumulates data.

**Verdict**: CONDITIONAL (depends on treatment of No Layers condition).

### 6. Effect Size Framework

**Finding**: Partial eta-squared is appropriate. The trust level criteria (HIGH: eta2 > 0.10, MEDIUM: eta2 > 0.05, LOW: eta2 > 0.05) are reasonable for the 2^3 design.

**Verdict**: PASS.

### 7. Trust Score Framework

**Finding**: Trust levels are explicitly defined in the order (HIGH: p<0.01, eta2>0.10, all diagnostics pass; MEDIUM: p<0.05, eta2>0.05, minor violations; LOW: p<0.10 or eta2<0.05; UNTRUSTED: p>=0.10). These are achievable and well-calibrated.

**Verdict**: PASS.

### 8. Blocking/Randomization

**Finding**: Fully randomized run order is specified with an explicit sequence table. This is well-designed and controls for temporal effects.

**Verdict**: PASS.

### DOE-003 Summary

| Dimension | Verdict | Issues |
|-----------|---------|--------|
| Power Analysis | CONDITIONAL | DOE003-M1 (degenerate "No Layers" cell) |
| Seed Design | PASS | -- |
| Statistical Method | MINOR | DOE003-m1 (data-dependent contrasts) |
| Multiple Comparison | PASS | -- |
| ANOVA Assumptions | CONDITIONAL | See DOE003-M1, DOE003-N1 (cold start) |
| Effect Size | PASS | -- |
| Trust Framework | PASS | -- |
| Randomization | PASS | -- |

---

## DOE-004: Document Quality Ablation (One-Way ANOVA)

### 1. Power Analysis

**Finding**: States n=50 per group for one-way ANOVA (3 groups) at f=0.30, [STAT:alpha=0.05], targeting [STAT:power=0.80]. G*Power calculation yields n=42 per group; n=50 provides [STAT:power~0.87]. This is well-justified with appropriate safety margin.

Verification: For one-way ANOVA, 3 groups:
- df_between = 2, df_within = 147
- At f = 0.30, alpha = 0.05, n = 50 per group: power ~ 0.88
- The stated ~0.87 is accurate.

**Verdict**: PASS.

### 2. Seed Design

**Finding**: Formula `seed_i = 7890 + i*13` for i=0..49 produces 50 unique seeds in [7890, 8527]. No cross-experiment collisions. All 3 conditions use the same 50 seeds.

**Verdict**: PASS.

### 3. Statistical Method Choice

**Finding**: One-way ANOVA is appropriate for a 3-level single-factor design. Tukey HSD for post-hoc pairwise comparisons is standard. The planned contrasts (Full vs Degraded, Full vs Random, Degraded vs Random) are orthogonal-adjacent and well-specified.

**Issue DOE004-m1 (MINOR)**: The order includes both planned contrasts and Tukey HSD. These serve overlapping purposes. If planned contrasts are pre-specified (which they are), they can be tested at alpha=0.05 each without correction (Dunnett-like structure with Full RAG as control). The additional Tukey HSD is then redundant for the three pairwise comparisons but provides simultaneous confidence intervals. This is not incorrect but could be simplified.

**Verdict**: PASS (redundancy is conservative, not harmful).

### 4. Multiple Comparison Correction

**Finding**: Tukey HSD controls family-wise error rate across 3 pairwise comparisons. For 3 groups, the correction is modest. Additionally, the dose-response (linear trend) test is specified as a separate planned contrast. This is a good approach.

**Verdict**: PASS.

### 5. ANOVA Assumptions

**Finding**: Standard diagnostic triplet specified. The manipulation check (verifying mean cosine similarity differs across conditions) is a strong design feature that adds credibility to the experiment.

**Issue DOE004-m2 (MINOR)**: If the manipulation check fails (e.g., Degraded documents still retrieve well because the corruption was insufficient), the experiment is invalidated. The order correctly specifies stopping if the check fails, but does not specify a quantitative threshold for the manipulation check beyond the expected ranges (Full > 0.7, Degraded 0.3-0.5, Random 0.0-0.2). Consider specifying: "Manipulation check passes if mean_sim(Full) - mean_sim(Degraded) > 0.15 AND mean_sim(Degraded) - mean_sim(Random) > 0.10."

**Severity**: MINOR -- Qualitative thresholds are provided but quantitative pass/fail criteria would strengthen the manipulation check.

### 6. Effect Size Framework

**Finding**: Partial eta-squared for the omnibus test and Cohen's d for pairwise comparisons. The dose-response prediction (linear trend) adds a meaningful dimension beyond simple group comparisons.

**Verdict**: PASS.

### 7. Trust Score Framework

**Finding**: Trust levels are explicitly and comprehensively defined with a 5-column table covering p-value, effect size, diagnostics, sample size, and manipulation check. This is the most thorough trust framework among all 5 DOEs.

**Issue DOE004-N1 (NOTE)**: The trust framework includes "Manipulation Check" as a criterion, which is excellent. However, the "Pass/Marginal/Fail" values for the manipulation check are qualitative. See DOE004-m2 above for recommendation.

**Verdict**: PASS.

### 8. Blocking/Randomization

**Finding**: Randomized run order (Degraded -> Full RAG -> Random). With only 3 runs, the randomization space is limited (3! = 6 possible orders). The chosen order places the control (Full RAG) in the middle, which is reasonable to avoid first-run and last-run effects.

**Verdict**: PASS.

### DOE-004 Summary

| Dimension | Verdict | Issues |
|-----------|---------|--------|
| Power Analysis | PASS | -- |
| Seed Design | PASS | -- |
| Statistical Method | PASS | DOE004-m1 (overlapping contrasts/Tukey, not harmful) |
| Multiple Comparison | PASS | -- |
| ANOVA Assumptions | PASS | -- |
| Effect Size | PASS | -- |
| Trust Framework | PASS | DOE004-N1 (quantitative manipulation thresholds) |
| Randomization | PASS | -- |

---

## DOE-005: Memory-Strength Interaction with Evolution Hook

### 1. Power Analysis

**Finding**: States n=30 per cell for 3x2 factorial ANOVA at f=0.25, [STAT:alpha=0.05], targeting [STAT:power=0.80]. With 6 factorial cells and 180 episodes:
- df_Memory = 2, df_Strength = 1, df_MxS = 2, df_error = 174
- At f = 0.25, alpha = 0.05, n = 30 per cell: power ~ 0.82-0.85 for main effects, ~0.80 for interaction.

The stated values are reasonable and verified.

**Issue DOE005-M1 (MAJOR)**: The center point analysis pools 90 center point episodes against 180 factorial episodes for a curvature test. However, the center point is at (Memory=0.5, Strength=0.5), and only one of the factorial cells has this Memory level (M_mid at 0.5 appears in 2 factorial cells: M_mid_S_low and M_mid_S_high). The 3x2 design is NOT a 2^k design with center points in the classical sense -- it is a full factorial with an added intermediate level for Memory. The "curvature test" as described (comparing factorial mean vs center point mean via t-test) is methodologically problematic because:

1. The factorial design includes 3 levels of Memory (0.3, 0.5, 0.7), so curvature in Memory can be tested directly from the factorial data using polynomial contrasts (linear vs quadratic).
2. The center point (0.5, 0.5) is actually ON a factorial level for Memory (0.5 is one of the 3 levels). It is only "center" for Strength (halfway between 0.3 and 0.7).
3. The t-test comparing all factorial means vs center point mean conflates the center point test with factor effects.

**Recommendation**: Replace the center point curvature test with:
(a) A polynomial contrast for Memory: test the quadratic component (does kill_rate at Memory=0.5 deviate from the linear interpolation of Memory=0.3 and Memory=0.7?).
(b) Use the 3 center point replicates (M=0.5, S=0.5) for pure error estimation rather than curvature detection.
(c) If curvature in Strength is of interest, it cannot be tested with only 2 levels (0.3 and 0.7) plus a center at 0.5 embedded within the factorial.

**Severity**: MAJOR -- The curvature test as specified conflates factorial point analysis with center point methodology.

### 2. Seed Design

**Finding**: Formula `seed_i = 9999 + i*19` for i=0..29 produces 30 unique seeds in [9999, 10550]. No cross-experiment collisions. All 9 conditions (6 factorial + 3 center) use the same 30 seeds.

**Verdict**: PASS.

### 3. Statistical Method Choice

**Finding**: Two-way ANOVA with interaction is correct for the 3x2 factorial. Simple effects analysis (if interaction significant) and Tukey HSD are correctly specified.

**Issue DOE005-m1 (MINOR)**: The simple effects analysis for "Strength effect at each Memory level" uses t-tests. With n=30 per cell, these are well-powered but should use the pooled error term from the full ANOVA model (not separate t-tests) to maintain the same error rate assumptions.

**Verdict**: PASS with minor note.

### 4. Multiple Comparison Correction

**Finding**: Tukey HSD for pairwise comparisons within significant main effects. For Memory (3 levels): 3 pairwise comparisons. For Strength (2 levels): 1 comparison (no correction needed). This is correctly specified.

**Verdict**: PASS.

### 5. ANOVA Assumptions

**Finding**: Standard diagnostic triplet specified. The 3x2 balanced design with n=30 per cell is robust to mild assumption violations.

**Issue DOE005-m2 (MINOR)**: The analysis plan says the factorial ANOVA is on "Factorial Points Only" (180 episodes), excluding center points. This is correct for the ANOVA but raises the question of what the 90 center point episodes are used for beyond the (problematic) curvature test. At 270 total episodes, 90 are essentially wasted if the curvature test is not meaningful. Consider incorporating center points as an additional cell in the ANOVA (making it a 3x3 design with one missing cell, or using them for lack-of-fit testing).

**Verdict**: PASS with caveat on center point utility (see DOE005-M1).

### 6. Effect Size Framework

**Finding**: Partial eta-squared with standard benchmarks. Cohen's d for pairwise comparisons. Both appropriate.

**Verdict**: PASS.

### 7. Trust Score Framework

**Finding**: Trust levels defined with thresholds. The criteria include curvature test result, which is problematic (see DOE005-M1). If the curvature test is revised, the trust criteria should be updated accordingly.

**Verdict**: PASS (contingent on curvature test revision).

### 8. Blocking/Randomization

**Finding**: Fully randomized run order with center points interspersed. Well-designed.

**Verdict**: PASS.

### 9. Evolution Hook (Additional Dimension)

**Issue DOE005-M2 (MAJOR)**: The evolution test (Gen2 vs Gen1, paired t-test, n=30) has several statistical concerns:

1. **Pre-determined mutation**: Gen2 is always (Memory+0.1, Strength+0.1) from the best Gen1. This is not truly evolution -- it is a single fixed perturbation in one direction. The one-tailed t-test assumes Gen2 is better, but the perturbation direction is arbitrary (why not Memory-0.1?).

2. **Paired test validity**: The paired t-test uses the same 30 seeds as the Gen1 best condition. These Gen1 episodes have already been run as part of DOE-005. Re-using them as the "Gen1" comparison introduces a subtle issue: the Gen1 data was selected as the best-performing cell post-hoc. Comparing a post-hoc-selected cell against a new condition inflates Type I error (regression to the mean effect).

3. **Power for small improvement**: At n=30, a paired t-test detects d=0.30 (small-medium) at power ~0.50 for a one-tailed test. If the evolution improvement is small (which is likely for a +0.1 perturbation), the test is underpowered.

**Recommendation**:
(a) Increase n for the evolution test to 50 or use the DOE-005 data more carefully.
(b) Run fresh Gen1 episodes (not re-use post-hoc-selected cell) to avoid selection bias.
(c) Consider a two-tailed test (Gen2 could be worse if we are near a boundary).
(d) Acknowledge that this is a proof-of-concept for the evolution system, not a definitive validation.

**Severity**: MAJOR -- Methodological concerns with reuse of post-hoc-selected data and low power.

### DOE-005 Summary

| Dimension | Verdict | Issues |
|-----------|---------|--------|
| Power Analysis | CONDITIONAL | DOE005-M1 (curvature test methodology) |
| Seed Design | PASS | -- |
| Statistical Method | MINOR | DOE005-m1 (simple effects should use pooled error) |
| Multiple Comparison | PASS | -- |
| ANOVA Assumptions | PASS | DOE005-m2 (center point utility) |
| Effect Size | PASS | -- |
| Trust Framework | PASS | -- |
| Randomization | PASS | -- |
| Evolution Hook | CONDITIONAL | DOE005-M2 (selection bias, power, directionality) |

---

## Cross-Cutting Issues

### CC-1: Multiple Response Variable Testing (MAJOR)

**Scope**: DOE-001, DOE-002, DOE-003, DOE-004, DOE-005

All five experiment orders define a primary response (kill_rate) plus 3-5 secondary responses (survival_time, kills, damage_dealt, ammo_efficiency, etc.). However, none of the orders explicitly addresses how to control Type I error inflation when running the same statistical test across multiple response variables.

**Current state**: Each order specifies correction for multiple comparisons within a single response (e.g., Holm-Bonferroni for pairwise, Tukey HSD). But none addresses the multiplicity across responses.

**Recommendation**: For each DOE, designate kill_rate as the confirmatory primary analysis. All secondary responses should be labeled as exploratory/descriptive with the understanding that p-values are nominal (not adjusted). Alternatively, use a MANOVA approach for the secondary responses.

**Severity**: MAJOR -- Without this designation, readers/reviewers will question the inferential validity of claims based on secondary responses.

### CC-2: Consistent Non-Parametric Fallback Specification (MINOR)

**Scope**: DOE-001 through DOE-005

DOE-001 specifies Mann-Whitney U as fallback. DOE-002 specifies Aligned Rank Transform (ART) ANOVA. DOE-003 and DOE-004 specify ART or Kruskal-Wallis. DOE-005 does not explicitly specify a non-parametric fallback.

**Recommendation**: Standardize the non-parametric fallback across all DOEs. For factorial designs (DOE-002, DOE-003, DOE-005), ART-ANOVA is the appropriate non-parametric alternative. For one-way designs (DOE-001 pairwise, DOE-004), Mann-Whitney U (pairwise) or Kruskal-Wallis (omnibus) are correct. DOE-005 should add this specification.

**Severity**: MINOR -- Non-parametric fallbacks are secondary analyses, but consistency aids reproducibility.

### CC-3: Episode Independence Assumption Across All DOEs (MINOR)

**Scope**: DOE-001 through DOE-005

All DOEs assume episodes within a condition are independent. However, if the DuckDB cache (Level 1) accumulates data across episodes within a run, later episodes within the same condition may benefit from earlier episodes' cached experience. This creates within-run temporal dependence that violates the independence assumption for ANOVA.

**Mitigation in current design**: DOE-001 explicitly disables L1 for Random and Rule-Only. DOE-003 varies L1 on/off across conditions. DOE-002, DOE-004, and DOE-005 keep L1 enabled for all conditions.

**Recommendation**: For DOE-002, DOE-004, and DOE-005, either:
(a) Reset the DuckDB cache between conditions (but not between episodes within a condition) to ensure a consistent starting point, OR
(b) Pre-populate the DuckDB cache identically for all conditions (using a common warm-up set), OR
(c) Analyze with an AR(1) covariance structure or mixed model to account for within-run dependence.

Document whichever approach is chosen. Option (b) is recommended for simplicity and ecological validity.

**Severity**: MINOR -- The effect is likely small for 30-episode runs, but should be documented.

---

## Issue Registry

| ID | DOE | Severity | Summary | Recommendation |
|----|-----|----------|---------|---------------|
| DOE001-M1 | DOE-001 | MAJOR | Power ~0.70 for H-002 after Holm-Bonferroni correction | Increase n to 85 or note reduced power |
| DOE001-M2 | DOE-001 | MAJOR | "Five pairwise comparisons" but only 3 listed; family of 21 tests too large | Clarify count; separate primary/secondary families |
| DOE001-m1 | DOE-001 | MINOR | Correction family size 21 too large if pooling all responses | Correct within response families |
| DOE001-m2 | DOE-001 | MINOR | Fixed run order (not randomized) | Randomize or add run-order covariate |
| DOE001-N1 | DOE-001 | NOTE | S2-01 master seed set divergence | Document rationale in order |
| DOE001-N2 | DOE-001 | NOTE | Floor effects expected for Random agent | Mann-Whitney fallback adequate |
| DOE002-m1 | DOE-002 | MINOR | Multiple responses not corrected | Designate kill_rate as primary |
| DOE002-m2 | DOE-002 | MINOR | Within-run sequential episodes | Acceptable at n=30 |
| DOE002-N1 | DOE-002 | NOTE | Center point seed subsets | By design, documented |
| DOE002-N2 | DOE-002 | NOTE | Kill_rate distribution may be skewed | CLT adequate at n=30 |
| DOE003-M1 | DOE-003 | MAJOR | "No Layers" degenerate cell violates ANOVA assumptions | Analyze separately or use Welch's ANOVA |
| DOE003-m1 | DOE-003 | MINOR | Data-dependent planned contrasts | Pre-specify or use Scheffe |
| DOE003-N1 | DOE-003 | NOTE | L1 Only cold start problem | Document DuckDB cache state |
| DOE004-m1 | DOE-004 | MINOR | Overlapping contrasts and Tukey HSD | Not harmful, conservative |
| DOE004-m2 | DOE-004 | MINOR | Manipulation check lacks quantitative thresholds | Specify numeric pass/fail criteria |
| DOE004-N1 | DOE-004 | NOTE | Manipulation check pass/fail qualitative | See DOE004-m2 |
| DOE005-M1 | DOE-005 | MAJOR | Curvature test conflates factorial and center point methodologies | Use polynomial contrasts instead |
| DOE005-M2 | DOE-005 | MAJOR | Evolution test: selection bias, low power, directional assumptions | Fresh Gen1 data; increase n; two-tailed test |
| DOE005-m1 | DOE-005 | MINOR | Simple effects should use pooled error | Use MSE from full model |
| DOE005-m2 | DOE-005 | MINOR | Center points underutilized (90 episodes) | Use for lack-of-fit or pure error |
| DOE005-N1 | DOE-005 | NOTE | Non-parametric fallback not specified | Add ART-ANOVA as fallback |
| CC-1 | ALL | MAJOR | Multiple response testing not addressed | Designate primary/exploratory |
| CC-2 | ALL | MINOR | Inconsistent non-parametric fallbacks | Standardize across DOEs |
| CC-3 | ALL | MINOR | DuckDB cache may introduce within-run dependence | Pre-populate or reset cache |

---

## Severity Definitions

| Severity | Definition | Action Required |
|----------|-----------|----------------|
| **CRITICAL** | Fundamental design flaw; experiment cannot produce valid conclusions | Redesign before execution |
| **MAJOR** | Significant methodological concern; conclusions may be challenged | Revise before execution |
| **MINOR** | Sub-optimal practice; does not invalidate conclusions | Fix when convenient |
| **NOTE** | Informational; documents a consideration for future reference | No action required |

---

## Detailed Recommendations by Priority

### Must Fix Before Execution (MAJOR issues)

1. **DOE001-M1**: Add a note to DOE-001 acknowledging that power for the H-002 comparison (Full RAG vs Rule-Only, d=0.50) drops to ~0.70 after Holm-Bonferroni correction. State that the adaptive stopping rule (extend to n=100) will be invoked if the initial 70-episode results are suggestive but non-significant (0.05 < p_adj < 0.15).

2. **DOE001-M2**: Correct "Five pairwise comparisons" to "Three pairwise comparisons" in the Statistical Analysis Plan. Restructure the correction family: primary family = 3 comparisons on kill_rate (Holm-Bonferroni), secondary family = 3 comparisons x 6 secondary metrics = 18 tests (exploratory, report nominal p-values).

3. **DOE003-M1**: Add a section to DOE-003's analysis plan: "The No Layers condition (Run 8) is analyzed separately as a floor reference. The primary 2^3 factorial ANOVA is computed on the 7 non-degenerate conditions (Runs 1-7), treating the full 2^3 design with the understanding that the degenerate cell may violate variance homogeneity. If Levene's test fails, Welch's ANOVA or ART-ANOVA is used as primary analysis. Alternatively, the No Layers condition is excluded from the factorial ANOVA and compared to each other condition via separate Welch's t-tests."

4. **DOE005-M1**: Replace the center point curvature test with polynomial contrasts for Memory (linear vs quadratic component). Repurpose the 90 center point episodes as pure error replicates for lack-of-fit testing or as an independent validation of the factorial model's predictions at the center.

5. **DOE005-M2**: Revise the evolution test to: (a) Run 30 fresh episodes for Gen1 best configuration (not re-use data from the factorial), (b) Use a two-tailed paired t-test (do not assume direction), (c) Acknowledge that n=30 provides limited power for small improvements and label the evolution test as proof-of-concept rather than confirmatory.

6. **CC-1**: Add a section to each DOE's Statistical Analysis Plan: "Primary analysis: kill_rate (confirmatory, p-values adjusted). Secondary analyses: survival_time, kills, damage_dealt, ammo_efficiency (exploratory, nominal p-values reported)."

### Should Fix (MINOR issues)

7. **DOE001-m1, DOE002-m1**: See CC-1 above (covered by recommendation 6).

8. **DOE001-m2**: Add a note: "Run order is fixed for operational reasons. Run-order effects will be assessed post-hoc via regression of residuals on execution timestamp."

9. **DOE003-m1**: Pre-specify expected best comparators: "Contrast 1: Full Stack vs L0 Only (hypothesized strongest single layer). Contrast 2: Full Stack vs L0+L2 (hypothesized strongest two-layer combination)."

10. **DOE004-m2**: Add quantitative manipulation check: "Manipulation passes if mean_sim(Full) - mean_sim(Random) > 0.40 AND mean_sim(Full) - mean_sim(Degraded) > 0.15."

11. **DOE005-m1**: Specify: "Simple effects analysis uses the pooled MSE from the full 3x2 ANOVA model."

12. **CC-2**: Add to DOE-005: "Non-parametric fallback: If Anderson-Darling p < 0.05, use Aligned Rank Transform (ART) ANOVA as the primary analysis."

13. **CC-3**: Document DuckDB cache policy: "All conditions start with the same pre-populated DuckDB cache state (copied from the standard Gen1 agent). Cache is not reset between episodes within a condition but is restored to the standard state before each new condition begins."

---

## Overall Verdict

### ADEQUATE WITH REVISIONS RECOMMENDED

The experimental design portfolio is scientifically sound and covers the key research questions with appropriate DOE methodologies. No critical flaws were found that would require fundamental redesign.

**Strengths**:
- Well-chosen designs for each research question (OFAT for baselines, factorial for screening, one-way for ablation)
- Consistent seed fixation protocol across all experiments
- Thorough specification of response variables, expected outcomes, and contingency plans
- Decision gates prevent wasted computation if core assumptions fail
- Trust score framework provides clear adoption criteria
- Comprehensive diagnostics checklists in each order

**Areas for Improvement**:
- Power analysis should account for multiple comparison correction (DOE-001)
- Degenerate conditions need special treatment in factorial ANOVA (DOE-003)
- Center point methodology needs alignment with the non-2^k design structure (DOE-005)
- Evolution test methodology needs strengthening (DOE-005)
- Primary vs secondary response designation needed across all DOEs

**Recommendation**: Implement the 6 MAJOR fixes before execution. The 7 MINOR fixes should be incorporated when updating the orders but are not blocking. The 7 NOTES are informational and require no action.

---

*Report generated by research-pi. Validation performed against R100 (Experiment Integrity), R101 (PI Boundary), and R102 (Research Audit Trail) rules.*
