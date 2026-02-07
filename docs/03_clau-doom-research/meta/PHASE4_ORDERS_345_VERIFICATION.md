# Phase 4 Verification: Experiment Orders 003-005
> Verifier: research-pi (sonnet)
> Date: 2026-02-07
> Status: PASS WITH NOTES

---

## Executive Summary

All three experiment orders (DOE-003, DOE-004, DOE-005) meet R100 compliance requirements for seed fixation, statistical design, audit trail, and execution instructions. Cross-consistency is maintained. Dependency chain is logically valid. Minor notes and recommendations provided below.

**Verdict**: **PASS WITH NOTES** — All orders are READY_FOR_EXECUTION.

---

## DOE-003 Verification: Decision Layer Ablation

### 1. Seed Set Integrity (R100) ✓ PASS

- **Seeds Explicitly Listed**: ✓ Yes (lines 162-168)
- **Seed Generation Formula Documented**: ✓ Yes (`seed_i = 2023 + i * 23` for i = 0..29)
- **All Conditions Use IDENTICAL Seeds**: ✓ Yes — all 8 conditions use same SEED_SET
- **No Seed Reuse Within Run**: ✓ Yes — each episode uses a unique seed from the set
- **Reproducibility Markers**: ✓ Yes — [STAT:seed_set=fixed] [STAT:n=30] present

**Compliance**: FULL

---

### 2. Statistical Design ✓ PASS

- **Sample Size Justified**: ✓ Yes (n=30 per cell, 8 cells = 240 episodes)
- **Power Analysis**: ✓ Yes (power ~0.82 for main effects, ~0.75 for interactions)
- **ANOVA Model Specified**: ✓ Yes (line 202: 2^3 factorial model with all interactions)
- **Residual Diagnostics Plan**: ✓ Yes (normality: Anderson-Darling; equal variance: Levene; independence: run order plot)
- **Effect Size Measure**: ✓ Yes (partial η²)
- **Power Analysis**: ✓ Yes (lines 132-146)

**Compliance**: FULL

---

### 3. Audit Trail (R102) ✓ PASS

- **Hypothesis ID Linked**: ✓ Yes (H-005, line 13)
- **Hypothesis Exists in Backlog**: ✓ Yes (HYPOTHESIS_BACKLOG.md line 85: H-005)
- **Experiment ID Format**: ✓ Yes ("DOE-003")
- **Expected Output Documents**: ✓ Yes (EXPERIMENT_REPORT_003.md, line 432)

**Compliance**: FULL

---

### 4. Execution Instructions ✓ PASS

- **DuckDB Schema Specified**: ✓ Yes (lines 389-426)
- **Factor Levels Defined**: ✓ Yes (L0, L1, L2 ON/OFF, lines 49-53)
- **Response Variables Defined**: ✓ Yes (primary: kill_rate; secondary: survival_time, ammo_efficiency, decision_latency_ms; tracking: decision_level_used, etc.)
- **Randomized Run Order**: ✓ Yes (lines 180-192)

**Compliance**: FULL

---

### 5. DOE-003 Special: Decision Gate Logic ✓ PASS

- **STOP Condition Specified**: ✓ Yes (lines 299-317)
- **PROCEED Condition Specified**: ✓ Yes (lines 319-332)
- **Clear Criteria**: ✓ Yes (Full Stack vs. L0 Only comparison, p-value and effect size thresholds)
- **Diagnostic Actions on STOP**: ✓ Yes (check decision_level distribution, investigate if L0 usage > 90%)

**Compliance**: FULL

---

### DOE-003 Issues Found

**None.** All criteria met.

---

## DOE-004 Verification: Document Quality Ablation

### 1. Seed Set Integrity (R100) ✓ PASS

- **Seeds Explicitly Listed**: ✓ Yes (lines 287-295)
- **Seed Generation Formula Documented**: ✓ Yes (`seed_i = 7890 + i * 13` for i = 0..49)
- **All Conditions Use IDENTICAL Seeds**: ✓ Yes — all 3 conditions use same SEED_SET
- **No Seed Reuse Within Run**: ✓ Yes — each episode uses a unique seed
- **Reproducibility Markers**: ✓ Yes — [STAT:seed_set=fixed] [STAT:n=50] present

**Compliance**: FULL

---

### 2. Statistical Design ✓ PASS

- **Sample Size Justified**: ✓ Yes (n=50 per group, 3 groups = 150 episodes)
- **Power Analysis**: ✓ Yes (power ~0.87 for f=0.30, lines 256-271)
- **ANOVA Model Specified**: ✓ Yes (line 323: one-way ANOVA)
- **Residual Diagnostics Plan**: ✓ Yes (normality: Anderson-Darling; equal variance: Levene; independence: run order plot)
- **Effect Size Measure**: ✓ Yes (partial η²)
- **Power Analysis**: ✓ Yes (lines 256-271)

**Compliance**: FULL

---

### 3. Audit Trail (R102) ✓ PASS

- **Hypothesis ID Linked**: ✓ Yes (H-003, line 13)
- **Hypothesis Exists in Backlog**: ✓ Yes (HYPOTHESIS_BACKLOG.md line 47: H-003)
- **Experiment ID Format**: ✓ Yes ("DOE-004")
- **Expected Output Documents**: ✓ Yes (EXPERIMENT_REPORT_004.md, line 562)

**Compliance**: FULL

---

### 4. Execution Instructions ✓ PASS

- **DuckDB Schema Specified**: ✓ Yes (lines 533-556)
- **Factor Levels Defined**: ✓ Yes (Full RAG, Degraded, Random; lines 60-69)
- **Response Variables Defined**: ✓ Yes (primary: kill_rate; secondary: survival_time, retrieval_similarity; diagnostic: mean_retrieval_similarity, rule_match_rate, l2_usage_rate)
- **Randomized Run Order**: ✓ Yes (lines 303-315)

**Compliance**: FULL

---

### 5. DOE-004 Special: Document Manipulation Procedures ✓ PASS

- **Full RAG Condition**: ✓ Yes (lines 75-89, no manipulation)
- **Degraded Condition**: ✓ Yes (lines 91-133, degradation procedure specified with Python pseudocode)
- **Random Condition**: ✓ Yes (lines 139-189, random document generation procedure specified)
- **Manipulation Check Query**: ✓ Yes (lines 386-409, SQL query for mean retrieval similarity)
- **Verification Criteria**: ✓ Yes (Full > 0.7, Degraded 0.3-0.5, Random 0.0-0.2)

**Compliance**: FULL

---

### DOE-004 Issues Found

**None.** All criteria met.

---

## DOE-005 Verification: Memory-Strength Interaction + Evolution Hook

### 1. Seed Set Integrity (R100) ✓ PASS

- **Seeds Explicitly Listed**: ✓ Yes (lines 204-209)
- **Seed Generation Formula Documented**: ✓ Yes (`seed_i = 9999 + i * 19` for i = 0..29)
- **All Conditions Use IDENTICAL Seeds**: ✓ Yes — all 9 conditions (6 factorial + 3 center) use same SEED_SET
- **Evolution Test Uses SAME Seeds**: ✓ Yes (lines 412, 474: Gen2 uses same SEED_SET as Gen1)
- **No Seed Reuse Within Run**: ✓ Yes — each episode uses a unique seed
- **Reproducibility Markers**: ✓ Yes — [STAT:seed_set=fixed] [STAT:n=30] present

**Compliance**: FULL

---

### 2. Statistical Design ✓ PASS

- **Sample Size Justified**: ✓ Yes (n=30 per cell, 6 factorial + 3 center = 270 episodes)
- **Power Analysis**: ✓ Yes (power ~0.85 for main effects, ~0.80 for interaction, lines 167-189)
- **ANOVA Model Specified**: ✓ Yes (line 245: 2-way ANOVA with interaction)
- **Residual Diagnostics Plan**: ✓ Yes (normality: Anderson-Darling; equal variance: Levene; independence: run order plot)
- **Effect Size Measure**: ✓ Yes (partial η²)
- **Power Analysis**: ✓ Yes (lines 167-189)
- **Center Points Justified**: ✓ Yes (lines 91-102: detect curvature, test for non-linear effects)

**Compliance**: FULL

---

### 3. Audit Trail (R102) ✓ PASS

- **Hypothesis ID Linked**: ✓ Yes (H-008, line 13)
- **Hypothesis Exists in Backlog**: ✓ Yes (HYPOTHESIS_BACKLOG.md line 144: H-008)
- **Experiment ID Format**: ✓ Yes ("DOE-005" for factorial, "DOE-005-EVOL" for evolution test)
- **Expected Output Documents**: ✓ Yes (EXPERIMENT_REPORT_005.md, EVOLUTION_REPORT_001.md, lines 535-562)

**Compliance**: FULL

---

### 4. Execution Instructions ✓ PASS

- **DuckDB Schema Specified**: ✓ Yes (lines 509-529)
- **Factor Levels Defined**: ✓ Yes (Memory: [0.3, 0.5, 0.7]; Strength: [0.3, 0.7], lines 66-75)
- **Response Variables Defined**: ✓ Yes (primary: kill_rate; secondary: survival_time, damage_dealt, ammo_efficiency; evolution tracking: best_performer_combo, generation_1_best, generation_2_genome)
- **Randomized Run Order**: ✓ Yes (lines 218-235)

**Compliance**: FULL

---

### 5. DOE-005 Special: Evolution Test Specification ✓ PASS

- **Gen1 Best Identification**: ✓ Yes (lines 362-377, ANOVA identifies best performer)
- **Gen2 Genome Generation**: ✓ Yes (lines 379-399, mutation operator specified: ±0.1 perturbation)
- **Paired Test Design**: ✓ Yes (lines 400-438, paired t-test with same seeds)
- **Mutation Strategy Documented**: ✓ Yes (lines 381-397, perturbation magnitude and boundary enforcement)
- **Success Criteria**: ✓ Yes (lines 429-437, [STAT:p<0.05] [STAT:effect_size>0.3])
- **Failure Contingency**: ✓ Yes (lines 434-437, investigate mutation strategy)

**Compliance**: FULL

---

### DOE-005 Issues Found

**None.** All criteria met.

---

## Cross-Consistency (DOE-003, DOE-004, DOE-005)

### Seed Set Non-Collision ✓ PASS

| Experiment | Seed Formula | First Seed | Last Seed | Range |
|------------|--------------|-----------|-----------|-------|
| DOE-003 | 2023 + i*23 | 2023 | 2690 | 667 |
| DOE-004 | 7890 + i*13 | 7890 | 8527 | 637 |
| DOE-005 | 9999 + i*19 | 9999 | 10550 | 551 |

**Analysis**: All seed ranges are non-overlapping. No collision possible between experiments.

**Compliance**: FULL

---

### Design Types Appropriate for Hypotheses ✓ PASS

| Experiment | Hypothesis | Design Type | Appropriateness |
|------------|------------|-------------|----------------|
| DOE-003 | H-005 (layer ablation) | 2^3 Full Factorial | ✓ Correct: 3 binary factors, need all interactions |
| DOE-004 | H-003 (doc quality) | One-Way ANOVA (3 levels) | ✓ Correct: single factor with ordered levels (dose-response) |
| DOE-005 | H-008 (interaction) | 3×2 Factorial + Center Points | ✓ Correct: test interaction, detect curvature |

**Compliance**: FULL

---

### Response Variable Consistency ✓ PASS

All three experiments use **kill_rate** as primary response. Secondary responses differ appropriately based on experiment focus:

- DOE-003: decision_latency_ms (layer-specific)
- DOE-004: retrieval_similarity (document-specific)
- DOE-005: damage_dealt (factor-specific)

**Compliance**: FULL

---

## Dependency Chain Verification

### Dependency Graph

```
DOE-003 (Layer Ablation)
    │
    ├─ Decision Gate: Full Stack >> L0 Only?
    │   ├─ IF YES (p<0.05, d>0.5) → PROCEED
    │   └─ IF NO (p>0.10) → STOP, investigate
    │
    ├─ [PROCEED Path] ────────────────────────┐
    │                                         │
    v                                         v
DOE-004 (Document Quality)            DOE-005 (Memory-Strength)
    │                                         │
    ├─ Trust Level                            ├─ Interaction Significant?
    │   ├─ HIGH/MEDIUM → Adopt                │   ├─ YES + Curvature → Phase 2 RSM
    │   └─ LOW/UNTRUSTED → Reject             │   └─ NO → Linear model sufficient
    │                                         │
    v                                         v
Proceed to Multi-Generation Evolution    Evolution Test (Gen1 vs Gen2)
```

### Dependency Logic ✓ VALID

1. **DOE-003 is prerequisite for both DOE-004 and DOE-005**:
   - DOE-003 validates Full Stack (L0+L1+L2) > L0 Only
   - If this fails, DOE-004 (document quality) and DOE-005 (parameter optimization) lose scientific justification
   - Decision gate logic clearly specified (lines 299-332 in DOE-003)

2. **DOE-004 and DOE-005 are independent of each other**:
   - Both depend on DOE-003 passing
   - Neither depends on the other's results
   - Can be executed in parallel after DOE-003 completes

3. **DOE-005 evolution test is sequential within itself**:
   - Phase 1 (factorial ANOVA) must complete first
   - Phase 2 (Gen1 vs Gen2) uses results from Phase 1
   - Proper handoff specified (lines 462-481)

**Compliance**: VALID

---

## Issues Found

### Critical Issues

**None.**

---

### Minor Issues / Notes

#### DOE-003 Note 1: Decision Gate Threshold Sensitivity

**Line**: 306 (`[STAT:p>0.10]`)

**Issue**: The STOP condition uses p>0.10, which is more lenient than the standard p>0.05. This increases the risk of proceeding when Full Stack is only marginally better than L0 Only.

**Recommendation**: Consider using p>0.05 for the decision gate if the research goal is to establish strong evidence for the RAG architecture. However, p>0.10 is acceptable if exploratory (allows proceeding with marginal evidence).

**Severity**: Low (design choice, not a violation)

---

#### DOE-004 Note 1: Manipulation Check Critical

**Lines**: 386-409 (manipulation check query)

**Issue**: The manipulation check is critical for DOE-004 validity. If degradation fails (e.g., Degraded sim > 0.6), the experiment must STOP and be re-run after fixing the degradation procedure.

**Recommendation**: The execution instructions (lines 485-502) correctly specify "If manipulation check fails: STOP and investigate." Emphasize this in the pre-execution briefing to research-doe-runner.

**Severity**: Low (already addressed in instructions)

---

#### DOE-005 Note 1: Evolution Test Sample Size

**Lines**: 410-427 (paired t-test, n=30)

**Issue**: The evolution test uses n=30 episodes per generation, which is adequate for detecting medium effects (d ≥ 0.5) but may lack power for small improvements (d < 0.3). If Gen2 is only slightly better than Gen1, the test may miss it.

**Recommendation**: If initial evolution test fails (p>0.05), consider increasing sample size to n=50 per generation for a replication study before rejecting the evolution hypothesis.

**Severity**: Low (power is adequate for medium effects, which is the target)

---

#### DOE-005 Note 2: Center Point Analysis

**Lines**: 263-280 (curvature test)

**Issue**: The curvature test compares center point mean to factorial point mean. This is a valid approach, but it assumes the center point (0.5, 0.5) is within the convex hull of the 6 factorial points. Given the design (Memory: [0.3, 0.5, 0.7], Strength: [0.3, 0.7]), the center is NOT at the geometric center of the factorial design (which would be Memory=0.5, Strength=0.5, but factorial points are at Strength=0.3 and 0.7).

**Recommendation**: The center point (0.5, 0.5) is correctly placed at the center of the factor ranges, not the factorial design points. The curvature test is valid as specified. No change needed, but clarify in EXPERIMENT_REPORT_005.md that the center is the factor space center, not the design center.

**Severity**: Low (design is valid, clarification helps interpretation)

---

## Overall Assessment

### Strengths

1. **Seed Fixation Rigorous**: All experiments use fixed, non-overlapping seed sets with documented generation formulas. Full R100 compliance.

2. **Statistical Design Sound**: Power analyses justify sample sizes. ANOVA models are appropriate. Residual diagnostics plans are comprehensive.

3. **Audit Trail Complete**: All hypotheses link back to HYPOTHESIS_BACKLOG.md. Experiment IDs are consistent. Output documents are specified.

4. **Dependency Chain Logical**: DOE-003 decision gate correctly gates DOE-004 and DOE-005. Evolution test within DOE-005 has proper handoff.

5. **Execution Instructions Detailed**: research-doe-runner has clear instructions for each experiment, including DuckDB schemas, agent MD configuration examples, and data recording procedures.

### Recommendations

1. **Pre-Execution Checklist**: Before starting DOE-003, verify:
   - All 8 agent configurations (L0/L1/L2 ON/OFF combinations) are valid
   - DuckDB `experiments` and `encounters` tables are ready
   - Seed set is loaded and accessible

2. **DOE-004 Manipulation Check Emphasis**: Stress to research-doe-runner that the manipulation check is a GO/NO-GO decision. If degradation fails, STOP and fix before proceeding.

3. **DOE-005 Evolution Test Monitoring**: Track Gen2 performance carefully. If paired t-test is marginal (p=0.05-0.10), plan a replication with larger n before concluding.

4. **Cross-Experiment Integration**: After DOE-003, DOE-004, DOE-005 complete, perform a meta-analysis to synthesize findings across all three experiments. This will inform the overall RAG architecture validity.

---

## Verdict

**PASS WITH NOTES**

All three experiment orders (DOE-003, DOE-004, DOE-005) meet R100 compliance and are scientifically sound. Minor notes are provided for monitoring and clarification, but none require design changes.

**Status**: All orders are **READY_FOR_EXECUTION**.

**Next Steps**:
1. research-doe-runner → Execute DOE-003 (Layer Ablation)
2. research-analyst → Analyze DOE-003, generate EXPERIMENT_REPORT_003.md
3. research-pi → Apply decision gate logic
4. **IF PROCEED**: research-doe-runner → Execute DOE-004 and DOE-005 (can be parallel)
5. **IF STOP**: Investigate and resolve before proceeding to DOE-004/005

---

**Verification Complete**: 2026-02-07
**Verifier**: research-pi (sonnet)
**Verification Duration**: ~15 minutes (manual review of 3 orders + cross-checks)
