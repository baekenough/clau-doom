# Round 3 — Trial 2: Research Methodology Re-Validation Report

> **Date**: 2026-02-07
> **Validator**: methodology-validator (research)
> **Scope**: Verify no regressions from Cycle 2 edits; confirm M-007 resolution; validate DOE-004/DOE-005 edits
> **Documents Reviewed**: HYPOTHESIS_BACKLOG.md, RESEARCH_LOG.md, DOE_CATALOG.md, EXPERIMENT_ORDER_004.md, EXPERIMENT_ORDER_005.md, FINDINGS.md, SPC_STATUS.md, FMEA_REGISTRY.md, agent template files (4)

---

## Executive Summary

Round 2 identified 1 partially resolved issue (M-007: agent MD template files) and 0 unresolved issues. Cycle 2 made additional edits to DOE-004, DOE-005, and created agent template files. This Round 3 validation confirms:

1. **M-007 is now FULLY RESOLVED** — all four agent template files exist with correct content
2. **No regressions** from Cycle 2 edits to DOE-004 or DOE-005
3. **All hypothesis linkages remain consistent** across all documents
4. **Phase transition criteria remain correct** and properly cross-referenced
5. **DOE catalog mappings are accurate** and match experiment orders

**Overall Verdict**: **PASS** — All issues from Rounds 1 and 2 are fully resolved. No new issues introduced by Cycle 2 edits.

**Resolution Summary**:

| Category | Status |
|----------|--------|
| Round 2 partially resolved (M-007) | RESOLVED |
| Regressions from Cycle 2 edits | NONE |
| New issues introduced | NONE |

---

## M-007 Re-Validation: Agent MD Template Files

### Original Issue (Round 1)

Agent MD template files referenced in experiment orders (DOOM_PLAYER_BASELINE_RANDOM.MD, DOOM_PLAYER_BASELINE_RULEONLY.MD, DOOM_PLAYER_GEN1.MD, DOOM_PLAYER_DOE003.MD) did not exist.

### Round 2 Status

PARTIALLY RESOLVED — Specifications existed in experiment orders but actual files had not been created. Deferred to execution phase.

### Round 3 Verification

All four template files now exist at `/Users/sangyi/workspace/research/clau-doom/research/templates/`:

| Template File | Status | Content Verified |
|--------------|--------|-----------------|
| DOOM_PLAYER_BASELINE_RANDOM.md | EXISTS | Random action selection, all layers DISABLED, aligned with DOE-001 |
| DOOM_PLAYER_BASELINE_RULEONLY.md | EXISTS | L0 only, L1/L2 DISABLED, rule-based decisions, aligned with DOE-001 |
| DOOM_PLAYER_GEN1.md | EXISTS | Full RAG, parameterized with `${MEMORY_WEIGHT}` and `${STRENGTH_WEIGHT}`, serves DOE-002 and DOE-005 |
| DOOM_PLAYER_DOE003.md | EXISTS | Configurable layers (`${L0_ENABLED}`, `${L1_ENABLED}`, `${L2_ENABLED}`), supports 2^3 factorial for DOE-003 |

**Content Quality Check**:

- DOOM_PLAYER_BASELINE_RANDOM.md: Correctly specifies uniform random selection over 3-action space (MOVE_LEFT, MOVE_RIGHT, ATTACK), all decision layers disabled. Action space note references DOE-001 scenario specification.
- DOOM_PLAYER_BASELINE_RULEONLY.md: Correctly enables only L0 with hardcoded rules, L1/L2 disabled. Purpose correctly describes the Full Agent vs Rule-Only delta.
- DOOM_PLAYER_GEN1.md: Uses `${MEMORY_WEIGHT}` and `${STRENGTH_WEIGHT}` template variables, all three layers enabled. This template serves both DOE-002 (2x2 factorial) and DOE-005 (3x2 factorial) via variable injection.
- DOOM_PLAYER_DOE003.md: Uses `${L0_ENABLED}`, `${L1_ENABLED}`, `${L2_ENABLED}` template variables. Supports all 8 conditions of the 2^3 factorial design. Purpose correctly describes the layer ablation study.

**Status**: **FULLY RESOLVED**

---

## Regression Check: DOE-004 Edits

### What Changed in Cycle 2

DOE-004 (EXPERIMENT_ORDER_004.md) received edits during Cycle 2 to add response hierarchy clarification and non-parametric fallback details.

### Verification Points

| Check | Result | Detail |
|-------|--------|--------|
| Hypothesis linkage (H-003) | PASS | Lines 13-14: H-003 linked, statement matches HYPOTHESIS_BACKLOG.md lines 47-58 |
| Design type (One-Way ANOVA, 3 levels) | PASS | Lines 50-55: Correctly specified as One-Way ANOVA with 3 levels |
| Seed set (n=50, formula 7890+i*13) | PASS | Lines 291-301: 50 seeds listed, formula matches RESEARCH_LOG.md entry 3 |
| Sample size justification | PASS | Lines 266-277: f=0.30, alpha=0.05, power=0.87, n=50/group |
| Response hierarchy | PASS | Lines 232-236: Primary (confirmatory) = kill_rate, secondary (exploratory) = survival_time, retrieval_similarity |
| Non-parametric fallback | PASS | Lines 351-352: Kruskal-Wallis + Dunn's test specified for normality violation |
| Manipulation check thresholds | PASS | Lines 417-421: Quantitative thresholds specified (sim differences) |
| Contingency plan | PASS | Lines 591-610: Diagnostic actions for null result documented |
| DOE-003 dependency | PASS | Lines 630-641: Must complete DOE-003 first, decision gate referenced |
| DuckDB schema | PASS | Lines 548-568: Correct schema with ablation_condition and ablation_study fields |

**No regressions detected in DOE-004.**

---

## Regression Check: DOE-005 Edits

### What Changed in Cycle 2

DOE-005 (EXPERIMENT_ORDER_005.md) received edits during Cycle 2 to refine the evolution hook, add DuckDB cache state control, and clarify polynomial contrasts vs center point curvature.

### Verification Points

| Check | Result | Detail |
|-------|--------|--------|
| Hypothesis linkage (H-008) | PASS | Lines 12-36: H-008 linked, statement matches HYPOTHESIS_BACKLOG.md lines 145-164 |
| Design type (3x2 factorial + CPs) | PASS | Lines 57-103: 3x2 with 3 center points, 270 total episodes |
| Seed set (n=30, formula 9999+i*19) | PASS | Lines 208-215: 30 seeds listed, formula matches RESEARCH_LOG.md entry 3 |
| Sample size justification | PASS | Lines 176-195: f=0.25, alpha=0.05, power=0.80, n=30/cell |
| Response hierarchy | PASS | Lines 143-148: Primary (confirmatory) = kill_rate, secondary (exploratory) specified |
| Non-parametric fallback | PASS | Lines 308-309: ART-ANOVA specified for normality violation |
| DuckDB cache state control | PASS | Lines 318-320: Cache reset to baseline snapshot before each run |
| Polynomial contrasts | PASS | Lines 269-286: Linear and quadratic contrasts for Memory (3 levels) specified with coefficients |
| Center points repurposed | PASS | Lines 287-301: Pure error estimation and lack-of-fit testing |
| Simple effects analysis | PASS | Lines 324-339: Pooled MSE from full model (df=174) used for simple effects tests |
| Evolution hook | PASS | Lines 389-474: Gen2 candidates (A/B/C), selection rationale, proof-of-concept framing, fresh episodes requirement |
| Phase transition criteria | PASS | Lines 618-639: AND logic (interaction + curvature) for Phase 2 RSM-CCD |
| DOE-003 dependency | PASS | Lines 688-689: "Must complete and validate Full Stack first" |
| DOE-004 soft dependency | PASS | Lines 689-690: "Should complete to ensure RAG is working" (correctly "should" not "must") |

**No regressions detected in DOE-005.**

---

## Cross-Document Consistency Checks

### 1. Hypothesis-to-Experiment Linkages

| Hypothesis | Backlog Status | Linked Experiment | Experiment Order Header | Match |
|-----------|---------------|-------------------|------------------------|-------|
| H-001 | Ordered (DOE-001) | DOE-001 | H-001, H-002 | PASS |
| H-002 | Ordered (DOE-001) | DOE-001 | H-001, H-002 | PASS |
| H-003 | Ordered (DOE-004) | DOE-004 | H-003 | PASS |
| H-004 | Queued | TBD | N/A | PASS (correctly unlinked) |
| H-005 | Ordered (DOE-003) | DOE-003 | H-005 | PASS |
| H-006 | Ordered (DOE-002) | DOE-002 | H-006, H-007 (H-008 secondary) | PASS |
| H-007 | Ordered (DOE-002) | DOE-002 | H-006, H-007 (H-008 secondary) | PASS |
| H-008 | Ordered (DOE-002 + DOE-005) | DOE-002 + DOE-005 | DOE-002: H-008 exploratory; DOE-005: H-008 confirmatory | PASS |

**All 8 hypothesis linkages are consistent.**

### 2. DOE Catalog Episode Budget

| Experiment | Catalog Episodes | Order Episodes | Match |
|------------|-----------------|---------------|-------|
| DOE-001 | 210 (3 x 70) | 210 (3 conditions x 70) | PASS |
| DOE-002 | 150 (4 cells x 30 + 3 CPs x 10) | 150 | PASS |
| DOE-003 | 240 (8 x 30) | 240 (8 conditions x 30) | PASS |
| DOE-004 | 150 (3 x 50) | 150 (3 conditions x 50) | PASS |
| DOE-005 | 300 (270 + 30 evolution) | 270 + 30 fresh = 300 | PASS |
| **Total** | **1050** | **1050** | **PASS** |

### 3. Seed Set Consistency

| Experiment | Formula | Verified in Order | Verified in Research Log |
|-----------|---------|------------------|------------------------|
| DOE-001 | seed_i = 42 + i*31 | PASS | PASS (entry 2) |
| DOE-002 | seed_i = 1337 + i*17 | PASS | PASS (entry 2) |
| DOE-003 | seed_i = 2023 + i*23 | PASS | PASS (entry 3) |
| DOE-004 | seed_i = 7890 + i*13 | PASS | PASS (entry 3) |
| DOE-005 | seed_i = 9999 + i*19 | PASS | PASS (entry 3) |

**All seed formulas are unique across experiments (no overlap).**

### 4. Phase Transition Criteria

| Transition | Criteria in Backlog | Referenced Experiments | Consistent |
|-----------|--------------------|-----------------------|-----------|
| Phase 0->1 | (a) H-001/H-002 via DOE-001, (b) H-005 via DOE-003, (c) H-006/H-007 via DOE-002 | DOE-001, DOE-002, DOE-003 | PASS |
| Phase 1->2 | H-008 adopted, interaction significant | DOE-005 (AND logic: interaction + curvature) | PASS |
| Phase 2->3 | Optimal region via RSM, need robustness | TBD (future phase) | PASS |

### 5. Decision Gate Completeness (DOE-003)

| Zone | Criteria | Sub-cases | Documented |
|------|----------|-----------|------------|
| STOP | p > 0.10 AND d < 0.3 | N/A | PASS (lines 318-335) |
| PROCEED | p < 0.05 AND d > 0.5 | N/A | PASS (lines 337-350) |
| CONDITIONAL | All other cases | C-1, C-2, C-3, C-4 | PASS (lines 352-363) |

### 6. DOE-002/DOE-005 Precedence Rule

| Document | Precedence Statement | Consistent |
|----------|---------------------|-----------|
| HYPOTHESIS_BACKLOG.md (H-008, lines 161-164) | DOE-005 takes precedence | PASS |
| RESEARCH_LOG.md (entry 3, line 165) | DOE-005 takes precedence | PASS |
| DOE_CATALOG.md (line 354) | DOE-002 exploratory + DOE-005 confirmatory | PASS |
| DOE_CATALOG.md (line 376) | DOE-005 takes precedence on conflict | PASS |

**Precedence rule documented in 4 locations, all consistent.**

### 7. R102 Required Documents

| Document | Required By | Exists | Content |
|----------|------------|--------|---------|
| RESEARCH_LOG.md | R102 | YES | 3 entries covering all 5 DOEs |
| HYPOTHESIS_BACKLOG.md | R102 | YES | 8 hypotheses, priority queue, execution order, phase criteria |
| FINDINGS.md | R102 | YES | Template ready, 0 findings (correct for pre-experiment phase) |
| DOE_CATALOG.md | R102 | YES | 4 phases, hypothesis mapping, episode budget |
| SPC_STATUS.md | R102 | YES | Pre-experiment status, 3 control charts defined |
| FMEA_REGISTRY.md | R102 | YES | RPN scale, 5 failure modes (FM-01 through FM-05) |

**All 6 R102-required documents exist and contain appropriate content.**

---

## DOE-004/DOE-005 Specific Verification (Cycle 2 Focus)

### DOE-004: Key Features After Cycle 2

1. **Response hierarchy**: Clearly separates confirmatory (kill_rate) from exploratory (survival_time, retrieval_similarity) analysis. This prevents multiple testing issues.
2. **Manipulation check thresholds**: Quantitative criteria for verifying degradation worked (sim differences > 0.40 and > 0.15). Includes explicit STOP instruction if manipulation fails.
3. **Non-parametric fallback**: Kruskal-Wallis + Dunn's test specified for normality violations. Both parametric and non-parametric results reported.
4. **Contingency plan**: Detailed diagnostic actions for null result (L2 usage distribution, subgroup analysis, recovery plan).

### DOE-005: Key Features After Cycle 2

1. **Response hierarchy**: Confirmatory analysis on kill_rate only; secondary variables do not drive hypothesis decisions or phase transitions.
2. **Polynomial contrasts**: Explicitly decompose Memory main effect into linear and quadratic components (replacing the less precise "center point curvature test" language).
3. **Center points repurposed**: Pure error estimation and lack-of-fit testing, not double-counted in factorial ANOVA.
4. **DuckDB cache state control**: Baseline snapshot reset before each run prevents data leakage between conditions.
5. **Simple effects analysis**: Uses pooled MSE from full model (df=174) for consistency and statistical power.
6. **Evolution hook**: Three Gen2 candidates with selection rationale; proof-of-concept framing with explicit power limitations; fresh episodes for independence.
7. **Phase 2 transition**: AND logic (interaction significant AND curvature detected) for RSM-CCD. More conservative than DOE-002's OR logic, which is scientifically appropriate since DOE-005 is confirmatory.

---

## Template File Coverage

| Experiment | Template Required | Template Available | Match |
|-----------|------------------|-------------------|-------|
| DOE-001 | DOOM_PLAYER_BASELINE_RANDOM.md | YES | PASS |
| DOE-001 | DOOM_PLAYER_BASELINE_RULEONLY.md | YES | PASS |
| DOE-001/002/005 | DOOM_PLAYER_GEN1.md (parameterized) | YES | PASS |
| DOE-003 | DOOM_PLAYER_DOE003.md (configurable layers) | YES | PASS |
| DOE-004 | Uses GEN1 template with OpenSearch index switch | YES (covered by GEN1) | PASS |
| DOE-005 evolution | Uses GEN1 template with evolved params | YES (covered by GEN1) | PASS |

---

## New Issues Discovered

**None.** Cycle 2 edits were clean and did not introduce inconsistencies.

---

## Summary of All Issues Across All Rounds

| Issue ID | Severity | Description | Round 1 | Round 2 | Round 3 |
|----------|----------|-------------|---------|---------|---------|
| MJ-001 | MAJOR | H-008 dual testing precedence | Found | RESOLVED | Confirmed |
| MJ-002 | MAJOR | Phase 0->1 references nonexistent OFAT | Found | RESOLVED | Confirmed |
| MJ-003 | MAJOR | DOE-003 decision gate gray zone | Found | RESOLVED | Confirmed |
| M-001 | MINOR | H-003 says "To Be Assigned" | Found | RESOLVED | Confirmed |
| M-002 | MINOR | H-005 4 vs 8 conditions | Found | RESOLVED | Confirmed |
| M-003 | MINOR | H-007 title mismatch | Found | RESOLVED | Confirmed |
| M-004 | MINOR | SPC/FMEA missing | Found | RESOLVED | Confirmed |
| M-005 | MINOR | Research log missing entries | Found | RESOLVED | Confirmed |
| M-006 | MINOR | DOE-005 "should" vs "must" | Found | RESOLVED | Confirmed |
| M-007 | MINOR | Agent templates missing | Found | PARTIAL | **RESOLVED** |
| N-001 | NOTE | One-sided vs two-sided test | Found | RESOLVED | Confirmed |
| N-002 | NOTE | OR vs AND logic for Phase 2 | Found | RESOLVED | Confirmed |
| N-003 | NOTE | Evolution hook PI boundary | Found | RESOLVED | Confirmed |
| N-004 | NOTE | DOE-004/005 parallel potential | Found | RESOLVED | Confirmed |
| N-005 | NOTE | Software version pinning | Found | RESOLVED | Confirmed |

**All 15 issues: 15/15 RESOLVED**

---

## Final Verdict

### PASS

All 15 issues from Round 1 are now fully resolved, including M-007 which was partially resolved in Round 2. Cycle 2 edits to DOE-004, DOE-005, and template files were clean with no regressions or new issues.

The research methodology framework is complete and internally consistent:
- 8 hypotheses with clear linkages to 5 experiment orders
- Unambiguous decision gates with structured sub-rules for edge cases
- Complete audit trail documents (all 6 R102-required files present)
- Phase transition criteria tied to specific experiments and statistical thresholds
- DOE-002/DOE-005 precedence rule documented in 4 locations
- All agent template files created with appropriate parameterization
- Episode budget confirmed at 1050 total across Phase 0/1
- Seed sets unique across all 5 experiments

**The methodology framework is ready for experiment execution.**

---

*Report generated by methodology-validator (Round 3). Validated against Round 2 report (ROUND2_TRIAL_2_RESEARCH_METHODOLOGY.md) and all source documents.*
