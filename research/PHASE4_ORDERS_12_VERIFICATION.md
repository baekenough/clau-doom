# Phase 4 Verification Report: EXPERIMENT_ORDER 001 & 002

> **Date**: 2026-02-07
> **Author**: research-pi
> **Scope**: Verify DOE-001, DOE-002, HYPOTHESIS_BACKLOG.md, DOE_CATALOG.md
> **Status**: COMPLETE — All issues identified and resolved

---

## Documents Verified

| Document | Path | Version |
|----------|------|---------|
| EXPERIMENT_ORDER_001.md | research/experiments/EXPERIMENT_ORDER_001.md | Initial |
| EXPERIMENT_ORDER_002.md | research/experiments/EXPERIMENT_ORDER_002.md | Initial |
| HYPOTHESIS_BACKLOG.md | research/HYPOTHESIS_BACKLOG.md | Post-fix |
| DOE_CATALOG.md | research/DOE_CATALOG.md | Post-fix |

---

## Check 1: Hypothesis-to-Experiment Linkage

### DOE-001

| Property | Expected | Actual | Status |
|----------|----------|--------|--------|
| Linked hypotheses | H-001, H-002 | H-001, H-002 | PASS |
| H-001 statement match | Full Agent > Random | Full RAG >> Random | PASS |
| H-002 statement match | Full Agent > Rule-Only | Full RAG > Rule-Only | PASS |
| Backlog status updated | Ordered | Updated to "Experiment ordered (DOE-001)" | PASS (fixed) |
| Audit trail | Present | Hypothesis → Order → Report → Findings chain defined | PASS |

### DOE-002

| Property | Expected | Actual | Status |
|----------|----------|--------|--------|
| Linked hypotheses | H-006, H-007 (primary), H-008 (exploratory) | H-006, H-007, H-008 | PASS |
| H-006 statement match | Memory main effect | Memory main effect on kill_rate | PASS |
| H-007 statement match | Strength main effect | Strength main effect on kill_rate | PASS |
| H-008 statement match | Memory x Strength interaction | Interaction term significant | PASS |
| Backlog status updated | Ordered | Updated to "Experiment ordered (DOE-002)" | PASS (fixed) |
| Audit trail | Present | Hypothesis → Order → Report → Findings chain defined | PASS |

---

## Check 2: Seed Set Integrity

### DOE-001 Seeds

**Formula**: `seed_i = 42 + i * 31` for `i = 0, 1, ..., 69`

| Verification | Result | Status |
|-------------|--------|--------|
| seed_0 = 42 + 0*31 = 42 | Listed: 42 | PASS |
| seed_1 = 42 + 1*31 = 73 | Listed: 73 | PASS |
| seed_69 = 42 + 69*31 = 2181 | Listed: 2181 | PASS |
| All 70 seeds unique | Step = 31 (prime), guaranteed unique | PASS |
| Min value | 42 | PASS |
| Max value | 2181 | PASS |
| Same seeds for all 3 conditions | Explicitly stated | PASS |
| Seed consumption order | Sequential (seed_i maps to episode i) | PASS |

### DOE-002 Seeds

**Formula**: `seed_i = 1337 + i * 17` for `i = 0, 1, ..., 29`

| Verification | Result | Status |
|-------------|--------|--------|
| seed_0 = 1337 + 0*17 = 1337 | Listed: 1337 | PASS |
| seed_1 = 1337 + 1*17 = 1354 | Listed: 1354 | PASS |
| seed_29 = 1337 + 29*17 = 1830 | Listed: 1830 | PASS |
| All 30 seeds unique | Step = 17 (prime), guaranteed unique | PASS |
| Min value | 1337 | PASS |
| Max value | 1830 | PASS |
| Same seeds for all factorial cells | Explicitly stated (seeds[0..29]) | PASS |
| Center point seed subsets correct | CP1: [0..9], CP2: [10..19], CP3: [20..29] | PASS |
| No seed overlap with DOE-001 | DOE-001: 42-2181 (step 31), DOE-002: 1337-1830 (step 17) | OVERLAP EXISTS |

**Seed Overlap Analysis**: DOE-001 seeds = {42, 73, 104, ..., 2181}. DOE-002 seeds = {1337, 1354, ..., 1830}. Checking for intersections: DOE-001 seeds in DOE-002 range [1337,1830] are {1344, 1375, 1406, 1437, 1468, 1499, 1530, 1561, 1592, 1623, 1654, 1685, 1716, 1747, 1778, 1809}. DOE-002 seeds are {1337, 1354, 1371, 1388, 1405, 1422, 1439, 1456, 1473, 1490, 1507, 1524, 1541, 1558, 1575, 1592, 1609, 1626, 1643, 1660, 1677, 1694, 1711, 1728, 1745, 1762, 1779, 1796, 1813, 1830}. Intersection: **1592** appears in both sets (DOE-001: 42+50*31=1592, DOE-002: 1337+15*17=1592).

**Impact**: MINIMAL. Seed overlap between experiments is NOT a problem since DOE-001 and DOE-002 test different factors/conditions. The overlap would only matter if we were pooling data across experiments, which is not planned. Each experiment is independently analyzed.

---

## Check 3: Sample Size Verification

### DOE-001

| Property | S2-01 Reference | DOE-001 | Status |
|----------|----------------|---------|--------|
| n per condition | 70 (for d=0.50) | 70 | PASS |
| Total conditions | 3 (Random, Rule-Only, Full RAG) | 3 | PASS |
| Total episodes | 210 | 210 | PASS |
| Power target | 0.80 | 0.80 | PASS |
| Alpha | 0.05 | 0.05 | PASS |
| Effect size target | Cohen's d >= 0.50 (medium) | Cohen's d >= 0.50 | PASS |
| RL Reference included | Yes (S2-01 has 5 comparisons) | No (3 conditions only) | INFO |

**Note on RL exclusion**: DOE-001 excludes the RL Reference baseline (S2-01's Baseline 3). This is acceptable because RL Reference requires separate infrastructure (PPO training or literature review) and is independent of the primary hypotheses H-001 and H-002. RL comparison can be added as a separate experiment (DOE-00X) later.

### DOE-002

| Property | Value | Justification | Status |
|----------|-------|--------------|--------|
| n per factorial cell | 30 | Power ~ 0.85 for f=0.25 | PASS |
| Factorial cells | 4 (2x2) | 2 factors, 2 levels each | PASS |
| Center point episodes | 30 (3 x 10) | Curvature test with power ~ 0.70 | PASS |
| Total episodes | 150 | 120 factorial + 30 center | PASS |
| Power target | 0.80 | Achieved for main effects | PASS |
| Alpha | 0.05 | Standard | PASS |

---

## Check 4: Statistical Plan Consistency

### DOE-001

| Component | S2-01 Reference | DOE-001 | Status |
|-----------|----------------|---------|--------|
| Primary test | Welch's t-test | Welch's t-test | PASS |
| Alternative | Two-sided | Two-sided | PASS |
| Comparisons | 5 (includes RL) | 3 (no RL) | PASS (scope-appropriate) |
| Multiple correction | Holm-Bonferroni, 5x7=35 tests | Holm-Bonferroni, 3x7=21 tests | PASS (scope-appropriate) |
| Non-parametric fallback | Mann-Whitney U | Mann-Whitney U | PASS |
| Effect size | Cohen's d | Cohen's d | PASS |
| Reporting format | [STAT:t], [STAT:p], etc. | [STAT:t], [STAT:p], etc. | PASS |
| Adaptive stopping | Not in S2-01 | After 30 episodes: early stop / extend rules | INFO (enhancement) |

**Note on adaptive stopping**: DOE-001 adds an adaptive stopping rule not present in S2-01. This is a valid enhancement that improves efficiency (can stop early if overwhelming effect or extend if underpowered).

### DOE-002

| Component | Expected | DOE-002 | Status |
|-----------|----------|---------|--------|
| Primary test | 2-way ANOVA | 2-way ANOVA | PASS |
| SS type | Type III | Type III | PASS |
| df (Error) | 120-4=116 | 116 | PASS |
| df (Total) | 120-1=119 | 119 | PASS |
| Curvature test | factorial mean vs center mean | t-test comparing means | PASS |
| Residual diagnostics | Anderson-Darling, Levene's, run-order | All three specified | PASS |
| Non-parametric fallback | ART ANOVA or Kruskal-Wallis | Both specified | PASS |
| Effect size | partial eta-squared | partial eta-squared | PASS |
| Post-hoc (if interaction) | Simple effects + Tukey HSD | Specified | PASS |
| Reporting format | [STAT:f], [STAT:p], etc. | R100-compliant markers | PASS |

---

## Check 5: DOE_CATALOG Alignment

| Item | Before Fix | After Fix | Status |
|------|-----------|-----------|--------|
| H-001 design type | Baseline comparison (t-test) | Baseline comparison (Welch's t) | FIXED |
| H-002 design type | Baseline comparison (t-test) | Baseline comparison (Welch's t) | FIXED |
| H-006 design type | OFAT (one-way ANOVA) | 2^2 factorial (main effect) | FIXED |
| H-007 design type | OFAT (one-way ANOVA) | 2^2 factorial (main effect) | FIXED |
| H-008 design type | 2-factor factorial | 2^2 factorial (interaction) | FIXED |
| H-006 experiment link | (none) | DOE-002 | FIXED |
| H-007 experiment link | (none) | DOE-002 | FIXED |
| H-008 experiment link | (none) | DOE-002 | FIXED |
| Episode budget | OFAT: 270-450 + Factorial: 180-480 = 450-930 | Combined: 150 | FIXED |

**Design Choice Rationale**: Converting H-006/H-007 from OFAT to 2^2 factorial and combining with H-008 saves approximately 210 episodes (150 vs 360 if run separately). The trade-off is reduced factor levels (2 vs 3 per factor), compensated by center points for curvature detection. The factorial approach provides strictly more information (interaction effects) per episode.

---

## Check 6: R100 Compliance (Experiment Integrity)

### DOE-001

| R100 Requirement | Status | Evidence |
|-----------------|--------|----------|
| Fixed seeds | PASS | Formula: seed_i = 42 + i*31, all seeds listed |
| Identical seeds across conditions | PASS | All 3 conditions use seeds[0..69] |
| Seeds stored in EXPERIMENT_ORDER | PASS | Complete set listed (lines 131-138) |
| Statistical evidence markers defined | PASS | [STAT:t], [STAT:p], [STAT:ci], [STAT:effect_size], [STAT:n] |
| Trust score framework referenced | PASS | Via R100 compliance |
| ANOVA diagnostics specified | PASS | Normality, equal variance, run-order |
| No cherry-picking controls | PASS | All comparisons pre-specified |

### DOE-002

| R100 Requirement | Status | Evidence |
|-----------------|--------|----------|
| Fixed seeds | PASS | Formula: seed_i = 1337 + i*17, all seeds listed |
| Identical seeds across factorial cells | PASS | All 4 cells use seeds[0..29] |
| Center point seed subsets explicit | PASS | CP1:[0..9], CP2:[10..19], CP3:[20..29] |
| Seeds stored in EXPERIMENT_ORDER | PASS | Complete set listed (lines 132-135) |
| Statistical evidence markers defined | PASS | [STAT:f], [STAT:p], [STAT:eta2], etc. |
| ANOVA diagnostics specified | PASS | Anderson-Darling, Levene's, run-order, outlier check |
| No cherry-picking controls | PASS | Analysis plan pre-registered |
| Curvature test pre-specified | PASS | Prevents post-hoc model selection |

---

## Check 7: R102 Compliance (Research Audit Trail)

### DOE-001

| R102 Requirement | Status | Evidence |
|-----------------|--------|----------|
| Hypothesis exists in HYPOTHESIS_BACKLOG.md | PASS | H-001, H-002 defined |
| EXPERIMENT_ORDER document created | PASS | EXPERIMENT_ORDER_001.md |
| Links to hypothesis | PASS | Explicit H-001, H-002 references |
| Links to reference design doc | PASS | S2-01_EVAL_BASELINES.md |
| EXPERIMENT_REPORT placeholder | PASS | Listed as "Pending" |
| FINDINGS.md placeholder | PASS | Listed as "Pending" |
| RESEARCH_LOG.md entry | PASS | Listed as "Entry pending" |

### DOE-002

| R102 Requirement | Status | Evidence |
|-----------------|--------|----------|
| Hypothesis exists in HYPOTHESIS_BACKLOG.md | PASS | H-006, H-007, H-008 defined |
| EXPERIMENT_ORDER document created | PASS | EXPERIMENT_ORDER_002.md |
| Links to hypothesis | PASS | Explicit H-006, H-007, H-008 references |
| Links to reference design doc | PASS | S2-02_CORE_ASSUMPTION_ABLATION.md |
| EXPERIMENT_REPORT placeholder | PASS | Listed as "Pending" |
| FINDINGS.md placeholder | PASS | Listed as "Pending" |
| RESEARCH_LOG.md entry | PASS | Listed as "Entry pending" |

---

## Check 8: Factor Level Appropriateness (DOE-002)

### Memory (Factor A): Range 0.3 - 0.7

| Criterion | Assessment | Status |
|-----------|-----------|--------|
| Range span | 0.4 (from 0.3 to 0.7) | ADEQUATE |
| Center point | 0.5 (geometric center) | PASS |
| Lower bound | 0.3 (meaningful low utilization) | ACCEPTABLE |
| Upper bound | 0.7 (meaningful high utilization) | ACCEPTABLE |
| Comparison to H-006 original | Originally 0.5-0.9, now 0.3-0.7 | NOTED |

**Assessment**: The shift from (0.5, 0.7, 0.9) to (0.3, 0.7) broadens the low end to capture very low memory utilization effects, at the cost of not testing extreme high memory (0.9). This is a reasonable choice for a screening experiment — the factorial design's purpose is to detect whether factors matter, not to find the optimum (that is Phase 2 RSM's job). If Memory is significant, DOE-003 (CCD) would expand the design region to include 0.9.

### Strength (Factor B): Range 0.3 - 0.7

| Criterion | Assessment | Status |
|-----------|-----------|--------|
| Range span | 0.4 (from 0.3 to 0.7) | ADEQUATE |
| Center point | 0.5 (geometric center) | PASS |
| Lower bound | 0.3 (cautious/defensive play) | ACCEPTABLE |
| Upper bound | 0.7 (aggressive play) | ACCEPTABLE |
| Comparison to H-007 original | Originally 0.3, 0.5, 0.7 | EXACT MATCH |

**Assessment**: Strength levels exactly match the original H-007 specification (low=0.3, high=0.7). The range provides a meaningful contrast between cautious and aggressive play styles.

### Curvature Detection

Center points at (0.5, 0.5) test for non-linear effects within the [0.3, 0.7] x [0.3, 0.7] region. If curvature is detected, this signals the need for Phase 2 RSM with expanded range.

---

## Issues Found and Resolved

### Issue 1 (HIGH): Phase Label Mismatch
- **Location**: DOE-002 header, HYPOTHESIS_BACKLOG H-006/H-007
- **Problem**: DOE-002 labeled "Phase 1 (Screening)" but H-006/H-007 were labeled "Phase 0 (OFAT screening)"
- **Root Cause**: DOE-002 combines Phase 0 main effects and Phase 1 interaction into one experiment
- **Fix**: Changed DOE-002 phase to "Phase 0/1 (Combined)". Updated H-006/H-007/H-008 phases in HYPOTHESIS_BACKLOG to "Phase 0/1".

### Issue 2 (MEDIUM): Memory Level Range Mismatch
- **Location**: HYPOTHESIS_BACKLOG H-006 vs DOE-002 Factor A
- **Problem**: H-006 specified levels (0.5, 0.7, 0.9) but DOE-002 uses (0.3, 0.7) with center at 0.5
- **Root Cause**: Design evolution from OFAT (3 levels) to factorial (2 levels + center)
- **Fix**: Updated H-006 formal statement to use levels (0.3, 0.7). Added "Level Change Note" explaining the rationale.

### Issue 3 (MEDIUM): Hypothesis Status Not Updated
- **Location**: HYPOTHESIS_BACKLOG H-001, H-002, H-006, H-007, H-008
- **Problem**: All showed "Status: Queued" and "Linked Experiment: To be assigned" despite experiment orders existing
- **Fix**: Updated all 5 hypotheses to "Status: Experiment ordered (DOE-00X)" with linked experiment references.

### Issue 4 (LOW): DOE_CATALOG Design Mapping Outdated
- **Location**: DOE_CATALOG.md hypothesis-to-design mapping table
- **Problem**: H-006/H-007 mapped to OFAT, H-008 mapped to separate factorial. No experiment ID column.
- **Fix**: Added "Experiment" column to mapping table. Updated H-006/H-007 to "2^2 factorial (main effect)" and H-008 to "2^2 factorial (interaction)". Added DOE-001 and DOE-002 experiment IDs. Updated episode budget.

### Issue 5 (LOW): Hypothesis Header Count Outdated
- **Location**: HYPOTHESIS_BACKLOG.md header
- **Problem**: "8 (0 adopted, 0 rejected, 8 queued)" — but 5 are now ordered
- **Fix**: Updated to "8 (0 adopted, 0 rejected, 3 queued, 5 ordered)"

### Issue 6 (INFO): DOE-001 Action Space Narrower Than S2-01
- **Location**: DOE-001 Scenario table vs S2-01 Random Agent spec
- **Description**: DOE-001 lists 3 actions (MOVE_LEFT, MOVE_RIGHT, ATTACK) while S2-01's general spec lists 8 actions
- **Status**: NO FIX NEEDED. Defend the Center scenario correctly uses only 3 discrete actions. S2-01's 8-action list is the general VizDoom action space, not scenario-specific. DOE-001 is correct.

### Issue 7 (INFO): DOE-001 Has 3 Comparisons vs S2-01's 5
- **Location**: DOE-001 Statistical Analysis Plan vs S2-01 Pairwise Comparisons
- **Description**: S2-01 specifies 5 pairwise comparisons (including RL), DOE-001 has 3 (no RL)
- **Status**: NO FIX NEEDED. DOE-001 runs only 3 conditions (no RL Reference). The 3 comparisons are correct for its scope. RL comparison would require a separate experiment.

### Issue 8 (INFO): Seed Overlap Between DOE-001 and DOE-002
- **Location**: Seed sets of both experiments
- **Description**: Seed value 1592 appears in both DOE-001 (42+50*31) and DOE-002 (1337+15*17)
- **Status**: NO FIX NEEDED. Cross-experiment seed overlap has no impact because experiments are independently analyzed with different conditions and factors.

---

## Summary

| Check | DOE-001 | DOE-002 |
|-------|---------|---------|
| 1. Hypothesis linkage | PASS | PASS (after fix) |
| 2. Seed integrity | PASS | PASS |
| 3. Sample size | PASS | PASS |
| 4. Statistical plan | PASS | PASS |
| 5. DOE_CATALOG alignment | PASS (after fix) | PASS (after fix) |
| 6. R100 compliance | PASS | PASS |
| 7. R102 compliance | PASS | PASS |
| 8. Factor levels | N/A | PASS (acceptable) |

**Overall Verdict**: PASS — All critical and medium issues resolved. No blocking issues remain.

---

## Files Modified During Verification

| File | Changes |
|------|---------|
| research/HYPOTHESIS_BACKLOG.md | Updated H-001, H-002 linked experiments. Updated H-006 levels and phase. Updated H-007 phase and response. Updated H-008 priority and phase. Updated execution order. Updated header count. |
| research/experiments/EXPERIMENT_ORDER_002.md | Changed phase label from "Phase 1" to "Phase 0/1". Updated metadata. |
| research/DOE_CATALOG.md | Added Experiment column to mapping table. Updated H-006/H-007/H-008 design types. Updated episode budget summary. |
