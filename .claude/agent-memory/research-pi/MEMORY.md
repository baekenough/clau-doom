# Research PI Memory

## Project State
- **Current Phase**: Phase 1 (Factorial Re-validation)
- **Hypotheses**: 10 total (H-001 through H-010)
- **Experiment Orders**: 6 written (DOE-001 through DOE-006)
- **Findings**: 8 (F-001 through F-008; F-002 INVALIDATED, F-008 REJECTED)
- **Total Episodes Executed**: ~510 (DOE-001: 210, DOE-002: 150, DOE-005: 150)
- **DOE-006**: ORDERED, 150 episodes pending

## Critical Data Integrity Issue
- **KILLCOUNT Bug**: AMMO2 was mapped as kills in DOE-001 and DOE-002
- DOE-002 effects (Memory eta2=0.42, Strength eta2=0.32) computed from invalid data
- DOE-005 is FIRST experiment with real KILLCOUNT data
- DOE-006 re-validates DOE-002's [0.3, 0.7] range with corrected measurement
- Cross-experiment comparison DOE-002 vs DOE-005 is INVALID

## DOE-005 Key Results (First Real Data)
- Performance plateau at [0.7, 0.9]: all effects non-significant
- Real VizDoom baseline: ~8.4 kills/min, ~1.2 kills/ep, ~8.5s survival
- kill_rate data is zero-inflated, non-normal (plan non-parametric as co-primary)
- Normality violated but mitigated by balanced design + non-parametric verification

## Seed Set Information
- DOE-001: 42 + i*31, i=0..69 (70 seeds, range [42, 2211])
- DOE-002: 1337 + i*17, i=0..29 (30 seeds, range [1337, 1830])
- DOE-005: 2501 + i*23, i=0..29 (30 seeds, range [2501, 3168])
- DOE-006: 3501 + i*29, i=0..29 (30 seeds, range [3501, 4342])
- All ranges verified: zero cross-experiment collisions

## Hypothesis Status Summary
- H-001 (Full > Random): ADOPTED MEDIUM
- H-002 (Rule > Random): ADOPTED MEDIUM
- H-003 (Latency): ADOPTED MEDIUM
- H-004 (Memory optimization): ACTIVE, partially addressed
- H-005 (Doc quality): QUEUED
- H-006 (Memory main effect): ADOPTED MEDIUM (DOE-002, NEEDS RE-VALIDATION)
- H-007 (Strength main effect): ADOPTED MEDIUM (DOE-002, NEEDS RE-VALIDATION)
- H-008 (Interaction): ADOPTED MEDIUM (DOE-002, NEEDS RE-VALIDATION)
- H-009 (Trend beyond 0.7): REJECTED (DOE-005, plateau confirmed)
- H-010 (Effects at [0.3, 0.7] with real data): ACTIVE, DOE-006 ORDERED

## Lessons Learned
- Real VizDoom kill_rate is zero-inflated and right-skewed; always plan non-parametric fallbacks
- KILLCOUNT mapping must be verified before every experiment execution
- DOE-002 diagnostics all PASSED but data was fundamentally wrong -- diagnostics check assumptions, not measurement validity
- Performance plateau in [0.7, 0.9] means parameters have limited dynamic range at high values
- Cross-experiment replication checks are essential when measurement instruments change
- Arithmetic seed sequences (base + i*step) reliable for avoiding collisions
- Always verify seed ranges against ALL prior experiments, not just adjacent ones

## Design Decisions for DOE-006
- Chose [0.3, 0.7] (not [0.3, 0.9]) to match DOE-002 exactly for direct comparison
- R4 cell (0.7, 0.7) serves as cross-experiment anchor with DOE-005
- Seeds: 3501 + i*29, chosen to avoid all prior experiment ranges
- Randomized run order: R3, CP2, R1, R4, CP1, R2, CP3
