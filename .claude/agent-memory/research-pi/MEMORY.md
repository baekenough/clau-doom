# Research PI Memory

## Project State
- **Current Phase**: Phase 0 (Baseline + Ablation Foundation)
- **Hypotheses**: 8 total (H-001 through H-008)
- **Experiment Orders**: 5 written (DOE-001 through DOE-005)
- **Findings**: 0 (no experiments executed yet)
- **Total Episode Budget**: 1050 episodes

## Key Decisions Made
- H-006/H-007/H-008 combined into DOE-002 (2x2 factorial) instead of separate OFAT
- DOE-003 has DECISION GATE: if Full Stack ~ L0 Only, STOP DOE-004/005
- Wave 1 parallel: DOE-001, DOE-002, DOE-003 (600 episodes)
- Wave 2 sequential: DOE-004, DOE-005 (450 episodes, contingent on gate)

## Seed Set Information
- DOE-001: 42 + i*31, i=0..69 (70 seeds)
- DOE-002: 1337 + i*17, i=0..29 (30 seeds)
- DOE-003: 2023 + i*23, i=0..29 (30 seeds)
- DOE-004: 7890 + i*13, i=0..49 (50 seeds)
- DOE-005: 9999 + i*19, i=0..29 (30 seeds)
- Known collision: DOE-001 x DOE-002 share seed 1592 (negligible impact)

## Verification History
- Phase 2 S1 literature verification: PASS
- Phase 2 S2 design verification: PASS (4 DuckDB issues fixed)
- Phase 2 cross-verification: alignment 4.5/5.0
- Phase 5 final verification: READY WITH MINOR FIXES (5 issues, 0 HIGH)

## Outstanding Issues (from Phase 5)
- I-001 (MEDIUM): FIXED - DOE_CATALOG mapping table updated for H-003/H-005/H-008
- I-002 (LOW): Seed 1592 collision between DOE-001 and DOE-002 (accepted, negligible)
- I-003 (LOW): Date typos in DOE-003/004/005 headers (2025 -> 2026) - still open
- I-004 (LOW): H-008 priority summary table still says LOW (should be MEDIUM) - still open
- I-005 (LOW): DOE-001 seed formula rationale not documented vs S2-01 master set - still open

## Trial 2 Validation Fixes Applied
- MJ-001: Added H-008 dual testing precedence rule (DOE-002 exploratory, DOE-005 confirmatory)
- MJ-002: Revised Phase 0->1 transition criteria to match actual plan (3 conditions)
- M-001: Updated H-003 linked experiment to DOE-004, status to "Experiment Ordered"
- M-002: Added design note to H-005 about 8-condition vs 4-condition scope
- M-003: Renamed H-007 title to "Kill Efficiency" (matches primary response variable)
- M-005: Added RESEARCH_LOG entries for DOE-003, DOE-004, DOE-005
- I-001: Updated DOE_CATALOG hypothesis-to-design mapping and episode budget summary
- Also updated H-005 status/linked experiment (was still "Queued" despite DOE-003 existing)

## Statistical Rigor + Methodology Fixes Applied (All 5 DOE files)
- CC-1: All 5 DOEs now have primary/secondary response hierarchy (kill_rate confirmatory, others exploratory)
- DOE-001: Fixed "Five" to "Three" pairwise comparisons; restructured to primary/secondary correction families
- DOE-001: Added Holm-Bonferroni power drop note (~0.70 for H-002) with adaptive stopping mitigation
- DOE-001: Added fixed run order risk note with covariate analysis requirement
- DOE-002: Aligned analysis plan header with CC-1 (confirmatory on kill_rate only)
- DOE-003: Added No Layers degenerate cell treatment (Welch/ART-ANOVA fallbacks)
- DOE-003: Added CONDITIONAL zone to decision gate (4 sub-cases for ambiguous results)
- DOE-003: Pre-specified expected best contrasts (Full Stack vs L0 Only, Full Stack vs L0+L2)
- DOE-004: Added quantitative manipulation check thresholds (sim differences > 0.40 and > 0.15)
- DOE-005: Replaced center point curvature test with polynomial contrasts (linear vs quadratic)
- DOE-005: Repurposed 90 center point episodes as pure error replicates for lack-of-fit
- DOE-005: Revised evolution test: fresh episodes, two-tailed Welch's t, proof-of-concept framing
- DOE-005: Added ART-ANOVA non-parametric fallback
- DOE-005: Added DuckDB cache policy (baseline snapshot reset)
- DOE-005: Specified pooled MSE for simple effects tests

## Literature Review Updates (Trial 3 Validation)
- Added Section 5: DOE and Quality Engineering Methodology (9 new refs)
- Added RETRO (Borgeaud 2022) to RAG section
- Expanded Coscientist (Boiko 2023) from table to full entry
- Added Modern RL Context subsection (DreamerV3, IMPALA)
- Added RL Baselines and Positioning subsection
- Added OpenAI Five, SMAC to multi-agent table
- Updated contribution positioning table with DOE/QE literature citations
- Total refs: 47 core + 4 surveys (51 total, up from 31+surveys)
- Key DOE vs BO justification: interaction detection, ANOVA interpretability, noise handling, model-free

## Lessons Learned
- Arithmetic seed sequences (base + i*step) are reliable for avoiding internal collisions
- Different base values do NOT guarantee no cross-experiment collisions (check mathematically)
- DOE catalog mapping tables need updating whenever experiment designs are consolidated
- Priority changes in hypothesis entries must be reflected in ALL summary tables
- Always verify dates in document headers match the actual creation date
