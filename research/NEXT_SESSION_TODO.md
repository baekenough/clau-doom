> **STATUS**: Priority 1 tasks COMPLETED (2026-02-10). Findings F-108~F-112 registered, RESEARCH_LOG updated, DOE_CATALOG updated, HYPOTHESIS_BACKLOG updated. Committed and pushed.

# Next Session TODO — Post DOE-039/040/041

## Priority 1: Documentation Updates
- [ ] Register new findings in FINDINGS.md (3 new findings from DOE-039/040/041)
  - F-xxx: doom_skill explains 67.5% of kill variance (DOE-040, HIGH trust, p<10^-10)
  - F-xxx: Kill-Rate Paradox — higher difficulty → higher kill_rate but lower total kills (DOE-040)
  - F-xxx: Random exploration outperforms deterministic strategies in deadly_corridor (DOE-041, MEDIUM trust, p=0.00169)
  - Note: predict_position (DOE-039) produced UNTRUSTED results — scenario non-viable
- [ ] Update RESEARCH_LOG.md with DOE-039/040/041 session entry
- [ ] Update DOE_CATALOG.md with DOE-039/040/041 entries
- [ ] Update HYPOTHESIS_BACKLOG.md — mark H-042/043/044 as tested

## Priority 2: Git Commit
- [ ] Stage all new experiment files (EXPERIMENT_ORDER_039-041, EXPERIMENT_REPORT_039-041)
- [ ] Stage updated doe_executor.py (already has build_doe039/040/041_config)
- [ ] Commit: `exp(research): DOE-039~041 phase 4 new scenario exploration`

## Priority 3: Next Experiment Design (Phase 4 continued)
- [ ] Design DOE-042+: Consider these directions:
  - **Option A**: Genome evolution on defend_the_line — use GenomeAction with evolutionary optimization
  - **Option B**: Attack ratio fine-tuning on sk3 difficulty (medium, best discrimination)
  - **Option C**: Multi-scenario tournament (defend_the_line sk1/sk3/sk5 × top 3 strategies)
  - **Option D**: Hybrid strategies for deadly_corridor (structured + stochastic)
- [ ] predict_position.cfg: debug or permanently exclude from research program

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
