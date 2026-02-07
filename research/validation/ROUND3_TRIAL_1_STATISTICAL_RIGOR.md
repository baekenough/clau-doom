# Round 3 Validation: Statistical Rigor (Trial 1)

> **Date**: 2026-02-07
> **Validator**: research-analyst (statistical-rigor-validator, Round 3)
> **Scope**: All 5 experiment orders (DOE-001 through DOE-005) — Round 3 re-validation after Cycle 2 remediation
> **Prior Reports**: TRIAL_1_STATISTICAL_RIGOR.md (Round 1: 6 MAJOR, 10 MINOR, 7 NOTE), ROUND2_TRIAL_1_STATISTICAL_RIGOR.md (Round 2: 21/23 resolved, 1 partial, 1 new)

---

## Executive Summary

- **Overall**: **PASS**
- **Round 2 Remaining Issues**: 2/2 RESOLVED
- **Regressions Introduced**: 0
- **Original 23 Issues**: All 23 still resolved
- **New Issues Found**: 0

All statistical rigor concerns from Rounds 1 and 2 are now fully addressed. The experiment portfolio is clean and ready for execution.

---

## Round 2 Remaining Issue Tracking

### Issue 1: DOE-004 Kruskal-Wallis Non-Parametric Fallback (was PARTIALLY RESOLVED in Round 2)

**Round 2 Status**: PARTIALLY RESOLVED — DOE-004 (one-way ANOVA design) lacked an explicit non-parametric fallback. Round 2 noted that while DOE-001 had Mann-Whitney, DOE-002/003/005 had ART-ANOVA, DOE-004 was missing an explicit statement.

**Round 2 Recommendation**: Add Kruskal-Wallis as the non-parametric fallback for DOE-004's one-way design.

**Round 3 Verification**: EXPERIMENT_ORDER_004.md line 352 now reads:

> "Non-Parametric Fallback: If Anderson-Darling p < 0.05, use Kruskal-Wallis test as a non-parametric alternative for the one-way design. If Kruskal-Wallis is significant, follow up with pairwise Dunn's test (Bonferroni-corrected) instead of Tukey HSD. Report both parametric and Kruskal-Wallis results when the normality assumption is violated."

**Assessment**: **RESOLVED**. The fallback is:
- Methodologically appropriate (Kruskal-Wallis is the standard non-parametric analog of one-way ANOVA)
- Complete (includes post-hoc follow-up with Dunn's test and Bonferroni correction)
- Consistent with the project-wide pattern (each DOE now has an appropriate non-parametric fallback matching its design type)

**Non-Parametric Fallback Coverage (Final State)**:

| DOE | Design Type | Non-Parametric Fallback | Status |
|-----|------------|------------------------|--------|
| DOE-001 | Pairwise t-tests | Mann-Whitney U | Appropriate |
| DOE-002 | 2^2 Factorial ANOVA | ART-ANOVA / Kruskal-Wallis | Appropriate |
| DOE-003 | 2^3 Factorial ANOVA | Welch's ANOVA / ART-ANOVA | Appropriate |
| DOE-004 | One-Way ANOVA | **Kruskal-Wallis + Dunn's** | **Now Appropriate** |
| DOE-005 | 3x2 Factorial ANOVA | ART-ANOVA | Appropriate |

---

### Issue 2: DOE-005 Stale "Paired t-test" References (was NEW-1 in Round 2)

**Round 2 Status**: NEW issue found — Lines 601 and 716 of EXPERIMENT_ORDER_005.md still referenced "paired t-test" despite the main body correctly specifying an independent two-sample Welch's t-test.

**Round 2 Recommendation**: Update lines 601 and 716 to say "Welch's t-test (independent, two-tailed)" instead of "paired t-test."

**Round 3 Verification**:

1. **Grep for "paired t-test"** in EXPERIMENT_ORDER_005.md: **Zero matches**. The phrase "paired t-test" does not appear anywhere in the document.

2. **Line 601** now reads: "Independent two-sample Welch's t-test results (Gen2 vs. Gen1) [STAT:t-test] [STAT:p]" — Correct.

3. **Line 716** now reads: "Evolution hook specified (Gen1 -> Gen2 transition, independent two-sample Welch's t-test)" — Correct.

4. **All other references to the evolution test** in DOE-005:
   - Line 433: "Independent two-sample comparison (NOT paired)" — Correct
   - Line 447: "Two-tailed Welch's t-test (unpaired, unequal variances assumed)" — Correct
   - Line 526: "Handoff to research-analyst for two-tailed Welch's t-test (Gen2 vs. Gen1 fresh)" — Correct
   - Line 582: "independent two-sample Welch's t-test" — Correct
   - Line 731: "Perform independent two-sample Welch's t-test" — Correct

5. **Only "paired" occurrences** in DOE-005 are contextual negations at lines 433 ("NOT paired") and 447 ("unpaired"), which are appropriate.

**Assessment**: **RESOLVED**. All stale "paired t-test" references have been replaced with "independent two-sample Welch's t-test." The document is internally consistent throughout.

---

## Regression Check

### Verification of All 23 Original Issues

Each of the 23 issues from the Round 1 report was re-verified to ensure no regressions were introduced during Cycle 2 remediation.

#### MAJOR Issues (6/6 still resolved)

| ID | Issue | Round 1 | Round 2 | Round 3 |
|----|-------|---------|---------|---------|
| DOE001-M1 | Power ~0.70 after Holm-Bonferroni | OPEN | RESOLVED | Still RESOLVED (line 121 power note intact) |
| DOE001-M2 | "Five pairwise" text / family size 21 | OPEN | RESOLVED | Still RESOLVED (lines 210-236 restructured) |
| DOE003-M1 | No Layers degenerate cell | OPEN | RESOLVED | Still RESOLVED (lines 212-215 fallback intact) |
| DOE005-M1 | Curvature test methodology | OPEN | RESOLVED | Still RESOLVED (lines 269-301 polynomial contrasts) |
| DOE005-M2 | Evolution test issues | OPEN | RESOLVED | Still RESOLVED (lines 429-474 rewritten) |
| CC-1 | Multiple response testing | OPEN | RESOLVED | Still RESOLVED (all 5 DOEs have Response Hierarchy) |

#### MINOR Issues (10/10 still resolved)

| ID | Issue | Round 3 Status |
|----|-------|---------------|
| DOE001-m1 | Correction family size | Still RESOLVED (subsumed by CC-1) |
| DOE001-m2 | Fixed run order | Still RESOLVED (line 169 covariate analysis) |
| DOE002-m1 | Multiple responses | Still RESOLVED (lines 174-178 hierarchy) |
| DOE002-m2 | Within-run sequential | Still RESOLVED (accepted as-is) |
| DOE003-m1 | Data-dependent contrasts | Still RESOLVED (lines 249-268 pre-specified) |
| DOE004-m1 | Overlapping contrasts/Tukey | Still RESOLVED (accepted as-is) |
| DOE004-m2 | Manipulation check thresholds | Still RESOLVED (lines 415-419 quantitative) |
| DOE005-m1 | Simple effects pooled error | Still RESOLVED (line 337 pooled MSE) |
| DOE005-m2 | Center points underutilized | Still RESOLVED (lines 287-301 pure error) |
| CC-2 | Inconsistent non-parametric fallbacks | **Now FULLY RESOLVED** (DOE-004 gap closed) |

#### NOTE Issues (7/7 still resolved)

| ID | Issue | Round 3 Status |
|----|-------|---------------|
| DOE001-N1 | S2-01 master seed divergence | Still RESOLVED (informational) |
| DOE001-N2 | Floor effects Random agent | Still RESOLVED (Mann-Whitney fallback) |
| DOE002-N1 | Center point seed subsets | Still RESOLVED (by design) |
| DOE002-N2 | Kill_rate skewness | Still RESOLVED (CLT adequate) |
| DOE003-N1 | L1 Only cold start | Still RESOLVED (by design) |
| DOE004-N1 | Manipulation check qualitative | Still RESOLVED (covered by DOE004-m2) |
| DOE005-N1 | Non-parametric fallback | Still RESOLVED (ART-ANOVA at line 309) |

#### Round 2 New Issue (1/1 now resolved)

| ID | Issue | Round 3 Status |
|----|-------|---------------|
| NEW-1 | DOE-005 stale "paired t-test" | **RESOLVED** (all references updated) |

---

## Cross-Consistency Verification (Round 3)

### 1. Response Hierarchy Consistency
All 5 experiment orders contain a "Response Hierarchy" section with kill_rate as the sole confirmatory primary response:
- DOE-001 line 175: Present and correct
- DOE-002 line 174: Present and correct
- DOE-003 line 105: Present and correct
- DOE-004 line 231: Present and correct
- DOE-005 line 143: Present and correct
- **Status**: CONSISTENT

### 2. Non-Parametric Fallback Consistency
All 5 experiment orders now have explicit, design-appropriate non-parametric fallbacks:
- DOE-001: Mann-Whitney U (for pairwise tests)
- DOE-002: ART-ANOVA / Kruskal-Wallis (for factorial)
- DOE-003: Welch's ANOVA / ART-ANOVA (for factorial with degenerate cell)
- DOE-004: Kruskal-Wallis + Dunn's test (for one-way)
- DOE-005: ART-ANOVA (for factorial with interactions)
- **Status**: CONSISTENT (all gaps closed)

### 3. Seed Set Integrity
- All 5 DOEs have verified seed sets with no undocumented collisions
- DOE-001/DOE-002 shared seed (1592) documented in both orders
- **Status**: CONSISTENT (no change from Round 2)

### 4. Sample Sizes
- All justified with power analysis
- **Status**: CONSISTENT (no change from Round 2)

### 5. Statistical Marker Format
- All orders use [STAT:p], [STAT:f], [STAT:eta2], [STAT:ci], [STAT:effect_size], [STAT:n], [STAT:power] consistently
- **Status**: CONSISTENT (no change from Round 2)

### 6. Evolution Test Internal Consistency (DOE-005)
- Main body (lines 429-474): Independent two-sample Welch's t-test, fresh episodes, two-tailed, proof-of-concept framing
- Report spec (lines 597-606): "Independent two-sample Welch's t-test"
- Completion criteria (line 716): "independent two-sample Welch's t-test"
- Execution instructions (line 526): "two-tailed Welch's t-test"
- Next steps (line 731): "independent two-sample Welch's t-test"
- **Status**: CONSISTENT (no stale references remain)

---

## Final Assessment

**Verdict: PASS**

All 25 tracked issues (23 original + 1 partial from Round 2 + 1 new from Round 2) are now fully resolved. No regressions were introduced during Cycle 2 remediation. Cross-consistency is maintained across all 5 experiment orders.

The experiment portfolio meets statistical rigor standards for execution.

### Summary of Improvements Across 3 Rounds

| Round | Issues Found | Resolved | Remaining |
|-------|-------------|----------|-----------|
| Round 1 | 23 (6 MAJOR, 10 MINOR, 7 NOTE) | — | 23 |
| Round 2 | +1 NEW | 22 (21 full + 1 partial) | 2 |
| Round 3 | 0 NEW | 2 | **0** |

### Convergence
The validation process has converged. All issues are resolved and no new issues were detected in Round 3. The iterative remediation cycle is complete.

---

*Report generated by research-analyst (statistical-rigor-validator). Round 3 re-validation against ROUND2_TRIAL_1_STATISTICAL_RIGOR.md findings.*
