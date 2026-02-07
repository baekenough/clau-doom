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
- I-001 (MEDIUM): DOE_CATALOG mapping table outdated for H-006/H-007
- I-002 (LOW): Seed 1592 collision between DOE-001 and DOE-002
- I-003 (LOW): Date typos in DOE-003/004/005 headers (2025 -> 2026)
- I-004 (LOW): H-008 priority summary table still says LOW (should be MEDIUM)
- I-005 (LOW): DOE-001 seed formula rationale not documented vs S2-01 master set

## Lessons Learned
- Arithmetic seed sequences (base + i*step) are reliable for avoiding internal collisions
- Different base values do NOT guarantee no cross-experiment collisions (check mathematically)
- DOE catalog mapping tables need updating whenever experiment designs are consolidated
- Priority changes in hypothesis entries must be reflected in ALL summary tables
- Always verify dates in document headers match the actual creation date
