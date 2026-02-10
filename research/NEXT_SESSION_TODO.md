> **STATUS**: Priority 3 COMPLETED (2026-02-10). DOE-042~045 designed. predict_position permanently excluded.

# Next Session TODO — Post DOE-039/040/041

## Priority 1: Documentation Updates [COMPLETED]
- [x] Register new findings in FINDINGS.md (F-108~F-112)
- [x] Update RESEARCH_LOG.md with DOE-039/040/041 session entry
- [x] Update DOE_CATALOG.md with DOE-039/040/041 entries
- [x] Update HYPOTHESIS_BACKLOG.md — mark H-042/043/044 as tested

## Priority 2: Git Commit [COMPLETED]
- [x] Stage all new experiment files (EXPERIMENT_ORDER_039-041, EXPERIMENT_REPORT_039-041)
- [x] Stage updated doe_executor.py
- [x] Commit: `exp(research): DOE-039~041 phase 4 new scenario exploration`

## Priority 3: Next Experiment Design (Phase 4 continued) [COMPLETED]
- [x] DOE-042: 5-action strategy comparison at doom_skill=3 (H-045)
- [x] DOE-043: Hybrid navigation strategies for deadly_corridor (H-046)
- [x] DOE-044: Evolutionary optimization in 5-action space (H-047)
- [x] DOE-045: Multi-difficulty strategy tournament (H-048)
- [x] predict_position.cfg: **permanently excluded** from research program (F-108, zero engagement)

## Context for Next Session
- Total episodes run: 4910 + 300 = 5210
- Cumulative DOE count: DOE-001 through DOE-041
- Key scenario: defend_the_line remains gold standard
- deadly_corridor: viable but very difficult (kills 0-2), needs advanced strategies
- predict_position: non-viable (shots_fired=0, scenario broken)
- Best architecture: random_5 (movement-inclusive) confirmed across multiple scenarios
- DOE-040 established full difficulty curve: sk1=24.8, sk3=17.0, sk5=6.5 kills

## Pending Experiment Reports
- EXPERIMENT_REPORT_036.md — exists but verify completeness
- EXPERIMENT_REPORT_037.md — exists but verify completeness
- EXPERIMENT_REPORT_038.md — exists but verify completeness
- EXPERIMENT_REPORT_039.md ✅ (just created)
- EXPERIMENT_REPORT_040.md ✅ (just created)
- EXPERIMENT_REPORT_041.md ✅ (just created)
