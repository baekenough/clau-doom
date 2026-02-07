# Round 4 Final Validation: Statistical Rigor

> **Reviewer**: Statistical Rigor Reviewer (Independent)
> **Date**: 2026-02-07
> **Scope**: All 5 experiment orders (DOE-001 through DOE-005)
> **Method**: Fresh, independent read of each document; no prior round bias

---

## Overall Verdict: READY FOR EXECUTION

All five experiment orders demonstrate strong statistical design. Each has clearly specified hypotheses, justified sample sizes, fixed seed sets, complete analysis plans with non-parametric fallbacks, residual diagnostic checklists, effect size measures, and reproducibility controls. The issues noted below are minor and do not block execution.

---

## Individual DOE Grades

### DOE-001: Grade A (Baseline Comparison — OFAT)

**Design Appropriateness**: Excellent. A three-condition single-factor comparison (Random vs Rule-Only vs Full RAG) is the correct first experiment. Welch's t-test for pairwise comparisons is appropriate given unequal variances are expected across very different agent types.

**Sample Size**: Well-justified. n=70 per group with power analysis showing ~0.80 for medium effect (d=0.50). The Holm-Bonferroni correction is correctly noted to reduce power to ~0.70 for the hardest comparison, and the adaptive stopping rule mitigates this.

**Analysis Plan**: Complete.
- Primary response (kill_rate) clearly separated from secondary (exploratory) responses
- Holm-Bonferroni correction for 3 primary comparisons
- Non-parametric fallback (Mann-Whitney U) specified with trigger condition (Anderson-Darling p < 0.05)
- Effect sizes (Cohen's d) with interpretation benchmarks
- Adaptive stopping rule with clear criteria

**Seed Set**: Properly specified with deterministic formula (seed_i = 42 + i*31). All conditions use identical seeds. Cross-experiment collision with DOE-002 acknowledged and justified.

**Residual Diagnostics**: Normality (Anderson-Darling), equal variance (Levene's), run-order plot all specified.

**Minor Notes**:
- Fixed run order (Random -> Rule-Only -> Full RAG) creates a potential confound with temporal drift. The document correctly identifies this risk and mandates a run-order covariate analysis. This is a thoughtful mitigation.
- The kill_rate variable (kills/min) could produce division-by-zero or extreme values for very short survival times. A floor on survival_time (e.g., minimum 1 second) should be enforced during data processing. This is a minor data cleaning concern, not a design flaw.

---

### DOE-002: Grade A (Memory x Strength Factorial)

**Design Appropriateness**: Excellent. A 2^2 full factorial with center points is textbook-correct for screening two continuous factors and detecting curvature. The combined Phase 0/1 framing is sensible.

**Sample Size**: n=30 per factorial cell (120 factorial + 30 center = 150 total). Power ~0.85 for main effects (f=0.25), ~0.80 for interaction. Adequate.

**Analysis Plan**: Complete and well-structured.
- 2-way ANOVA with Type III SS (correct for potentially unbalanced design, though this is balanced)
- Center point curvature test properly specified (t-test comparing factorial means vs center point mean)
- Non-parametric fallback: ART-ANOVA or Kruskal-Wallis
- Effect sizes (partial eta-squared) with interpretation benchmarks
- Post-hoc: Tukey HSD for simple effects if interaction is significant
- Response hierarchy: kill_rate confirmatory, others exploratory

**Seed Set**: Deterministic formula (seed_i = 1337 + i*17, n=30). Cross-experiment collision documented. Center points correctly use disjoint subsets of the same seed set.

**Run Order**: Properly randomized (not sequential by condition). Center points interspersed. This is better than DOE-001's fixed order.

**Phase Transition Criteria**: Well-defined triggers for moving to RSM (Phase 2).

**Minor Notes**:
- The design matrix shows all factorial cells using seeds[0..29] (identical). This is correct for controlling map/spawn variation.
- Visualization requirements are well-specified (main effects plot, interaction plot, cell means table).

---

### DOE-003: Grade A- (Decision Layer Ablation)

**Design Appropriateness**: Excellent. A 2^3 full factorial is the correct design for testing 3 binary factors (L0, L1, L2 decision layers). All 8 combinations are tested, enabling main effects, 2-way interactions, and the 3-way interaction.

**Sample Size**: n=30 per cell, 8 cells = 240 total. Power ~0.82 for main effects (f=0.30), ~0.75 for two-way interactions. The power for interactions is somewhat low but acceptable for Phase 1 screening.

**Analysis Plan**: Thorough.
- Full factorial ANOVA model with all interaction terms
- Planned contrasts well-chosen: (1) Full Stack vs L0 Only (primary, drives decision gate), (2) Full Stack vs L0+L2 (secondary, tests L1 incremental value)
- Post-hoc: Tukey HSD (28 pairwise comparisons, family-wise error controlled)
- Non-parametric fallback: ART-ANOVA and Welch's ANOVA for variance heterogeneity
- The "No Layers" (Run 8) degenerate cell is explicitly addressed with fallback strategies if it violates equal variance assumptions. This is good foresight.

**Decision Gate**: The STOP/PROCEED/CONDITIONAL logic is well-structured. The four CONDITIONAL sub-cases (C-1 through C-4) prevent premature binary decisions on ambiguous results. This is sophisticated and appropriate.

**Seed Set**: Deterministic formula (seed_i = 2023 + i*23, n=30). Correctly shared across all 8 conditions.

**Run Order**: Properly randomized.

**Minor Notes**:
- The response variable "kill_rate" is defined as "Total kills per episode" (line 116), whereas in DOE-001 and DOE-002 it is defined as "Kills per minute of survival" (kills/min). This inconsistency in variable definition needs attention. If DOE-003 uses raw kill count while DOE-001/002 use kills/min, cross-experiment comparisons become problematic. The analyst should ensure the same definition is used or clearly distinguish them.
- Power for two-way interactions (0.75) is below 0.80 target. This is acceptable for Phase 1 screening but should be noted in the report.

**Grade Rationale**: A- rather than A due to the kill_rate definition inconsistency that could cause confusion during cross-experiment interpretation. This is an easily resolvable issue at analysis time.

---

### DOE-004: Grade A (Document Quality Ablation)

**Design Appropriateness**: Excellent. A one-way ANOVA with 3 levels (Full RAG, Degraded, Random) directly tests whether document quality causally affects performance. The manipulation procedure is scientifically rigorous.

**Sample Size**: n=50 per group (150 total). Power ~0.87 for f=0.30. This exceeds the 0.80 target, providing a safety margin. Good decision to use n=50 rather than the calculated minimum of n=42.

**Analysis Plan**: Complete.
- One-way ANOVA with planned contrasts for dose-response
- Non-parametric fallback explicitly specified: Kruskal-Wallis with Dunn's test (Bonferroni-corrected). This is correctly specified for a one-way design.
- Tukey HSD for post-hoc pairwise comparisons
- Effect sizes with interpretation benchmarks
- Trust level criteria table is clear and operationalized

**Manipulation Check**: This is a standout feature. The quantitative manipulation check thresholds (mean_sim differences) are explicitly specified, with a clear STOP rule if manipulation fails. This is excellent experimental methodology.

**Seed Set**: Deterministic formula (seed_i = 7890 + i*13, n=50). Correctly shared across all 3 conditions.

**Document Manipulation Procedures**: The degradation procedure (tag shuffling + embedding noise) and random document generation are well-specified with Python code. The verification criteria (expected cosine similarity ranges) are concrete and testable.

**Minor Notes**:
- Same kill_rate definition concern as DOE-003: line 241 defines it as "Total kills per episode" rather than kills/min. Should be reconciled.
- The dependency on DOE-003's decision gate is correctly documented.

---

### DOE-005: Grade A (Memory-Strength Interaction with Evolution Hook)

**Design Appropriateness**: Excellent. A 3x2 full factorial with center points is the right design for detecting interaction between Memory (3 levels) and Strength (2 levels). The evolution hook adds scientific value beyond the factorial.

**Sample Size**: n=30 per cell, 6 cells = 180 factorial + 90 center points = 270 total. Power ~0.80 for interaction (f=0.25). Meets target.

**Analysis Plan**: The most comprehensive of all five DOEs.
- Two-way ANOVA with interaction term
- Memory polynomial contrasts (linear + quadratic) replace the standard curvature test. This is statistically more informative because it tests curvature within the factorial design itself, not just center vs factorial.
- Center points repurposed for pure error estimation and lack-of-fit testing. This is an efficient dual use of the center point data.
- Simple effects analysis clearly specified (with pooled MSE from full model, df=174). Using the pooled error term is the correct approach.
- Non-parametric fallback: ART-ANOVA preserving interaction testing ability
- DuckDB cache state control: explicit reset to baseline snapshot before each condition. This prevents confounding from accumulated experience. Important and well-considered.

**Evolution Test**: The proof-of-concept framing is honest and appropriate.
- Fresh episodes for Gen1 re-run (not re-using factorial data) ensures independence
- Two-tailed Welch's t-test is correct for unpaired comparison
- Power limitation explicitly acknowledged (0.50 for d=0.30, 0.80 for d=0.50)
- Clear interpretation guidelines for both significant and non-significant results

**Seed Set**: Deterministic formula (seed_i = 9999 + i*19, n=30). Correctly shared across all conditions.

**Run Order**: Properly randomized, center points interspersed.

**Minor Notes**:
- Same kill_rate definition inconsistency (line 152: "Total kills per episode" vs DOE-001/002 "Kills per minute"). Must be reconciled before cross-experiment analysis.
- The evolution test adds 60 additional episodes (30 Gen1 fresh + 30 Gen2), bringing the true total to 330 episodes for DOE-005. This is correctly documented in the execution instructions but the header says "~4-5 hours" which likely underestimates Phase 2 execution time.

---

## Summary Table

| DOE | Grade | Design Type | N | Power | Fallback | Seeds | Run Order |
|-----|-------|-------------|---|-------|----------|-------|-----------|
| 001 | A | OFAT (3 conditions) | 210 | 0.80 | Mann-Whitney U | Fixed (n=70) | Fixed (mitigated) |
| 002 | A | 2^2 Factorial + CP | 150 | 0.85 | ART-ANOVA / K-W | Fixed (n=30) | Randomized |
| 003 | A- | 2^3 Factorial | 240 | 0.82 | ART-ANOVA / Welch | Fixed (n=30) | Randomized |
| 004 | A | One-Way ANOVA (3 levels) | 150 | 0.87 | Kruskal-Wallis + Dunn | Fixed (n=50) | Randomized |
| 005 | A | 3x2 Factorial + CP + Evol | 270+60 | 0.80 | ART-ANOVA | Fixed (n=30) | Randomized |

---

## Strengths

1. **Consistent statistical framework**: All DOEs follow the same pattern of (a) primary confirmatory response, (b) secondary exploratory responses, (c) clear separation of confirmatory and exploratory analyses. This prevents p-hacking and maintains interpretive clarity.

2. **Non-parametric fallbacks universally specified**: Every DOE has a specific non-parametric alternative identified (Mann-Whitney U, ART-ANOVA, Kruskal-Wallis) with clear trigger conditions. This is uncommon in experiment orders and shows maturity.

3. **Fixed seed sets with deterministic formulas**: All seed sets use deterministic generation formulas. Cross-experiment collisions are documented. Identical seeds across conditions within each DOE ensure controlled comparisons.

4. **Decision gates and phase transition logic**: DOE-003's STOP/PROCEED/CONDITIONAL gate with four sub-cases is particularly well-designed. The dependency chain (DOE-003 gates DOE-004 and DOE-005) is clearly documented across all relevant experiments.

5. **Manipulation checks**: DOE-004's quantitative manipulation check with explicit thresholds and a STOP rule is exemplary. This kind of built-in validity check is often missing from experiment plans.

6. **Effect size reporting planned**: Every DOE specifies partial eta-squared for ANOVA effects and Cohen's d for pairwise comparisons, with interpretation benchmarks. This goes beyond mere significance testing.

7. **Residual diagnostics**: All DOEs specify Anderson-Darling (normality), Levene's (equal variance), and run-order plot (independence) checks.

8. **DOE-005 cache state control**: The DuckDB baseline snapshot reset between conditions prevents data leakage. This is a subtle but important control that many would overlook.

---

## Remaining Concerns (Minor)

1. **kill_rate definition inconsistency across DOEs**: DOE-001 and DOE-002 define kill_rate as "kills per minute of survival" (kills/min), while DOE-003, DOE-004, and DOE-005 define kill_rate as "total kills per episode" (raw count). These are fundamentally different metrics. Before execution, the research-pi should decide on ONE definition and ensure all DOEs use it consistently. If raw kill count is used, survival time variation becomes a confound. If kills/min is used, very short survival times can produce extreme values. **Recommendation**: Use kills/min (matching DOE-001/002) with a minimum survival_time floor of 1 second for division safety.

2. **DOE-001 fixed run order**: While mitigated by the run-order covariate analysis, this remains a design weakness compared to the randomized orders in DOE-002 through DOE-005. If temporal drift is detected, the finding will require replication with randomized order. This is correctly documented but worth noting.

3. **Power for DOE-003 two-way interactions (0.75)**: Slightly below the 0.80 target. If a two-way interaction is theoretically important (e.g., L0 x L2 synergy), a non-significant result should be interpreted cautiously given the marginal power. The analyst should report observed power alongside non-significant interaction results.

4. **DOE-005 evolution test power for small effects (0.50)**: Explicitly acknowledged in the document as a proof-of-concept limitation. Adequate for the stated purpose but should not be used to conclude "no effect" if non-significant.

---

## Final Recommendation

**The five experiment orders are READY FOR EXECUTION.** The statistical designs are appropriate for their respective research questions, sample sizes are justified, analysis plans are complete with fallbacks, and reproducibility controls (seed sets, cache resets) are in place. The minor concerns above (primarily the kill_rate definition inconsistency) should be resolved before analysis begins but do not require redesign.

**Pre-execution action item**: Standardize the kill_rate definition across all 5 DOEs to either (a) kills per minute of survival (kills/min) or (b) total kills per episode, and update the remaining documents accordingly. This is a documentation fix, not a design change.

---

## Validation Metadata

| Property | Value |
|----------|-------|
| Documents reviewed | 5 (DOE-001 through DOE-005) |
| Review method | Independent fresh read, no prior round influence |
| Total planned episodes | 1,020 (210 + 150 + 240 + 150 + 270) + 60 evolution |
| Statistical methods covered | Welch's t-test, one-way ANOVA, 2-way ANOVA, 2^3 factorial ANOVA, polynomial contrasts, Tukey HSD, Holm-Bonferroni, ART-ANOVA, Kruskal-Wallis, Mann-Whitney U |
| Reviewer confidence | HIGH |
