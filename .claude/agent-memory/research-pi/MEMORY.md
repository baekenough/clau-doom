# Research PI Memory

## Project State
- **Current Phase**: Phase 0/1 (Architectural Ablation)
- **Hypotheses**: 11 total (H-001 through H-011)
- **Experiment Orders**: 7 written (DOE-001 through DOE-007)
- **Findings**: 8 (F-001 through F-008; F-002 INVALIDATED, F-008 REJECTED; F-005/F-006/F-007 INVALIDATED by DOE-006)
- **Total Episodes Executed**: ~660 (DOE-001: 210, DOE-002: 150, DOE-005: 150, DOE-006: 150)
- **DOE-007**: ORDERED, 150 episodes pending (layer ablation)

## Memory-Strength Thread: CLOSED
- DOE-002: Large effects but INVALID data (AMMO2 bug)
- DOE-005: No effects at [0.7, 0.9] with real KILLCOUNT
- DOE-006: No effects at [0.3, 0.7] with real KILLCOUNT
- **Conclusion**: memory_weight and strength_weight have NO detectable effect on kill_rate at ANY tested range [0.3, 0.9]
- DOE-002 effects were entirely measurement artifacts
- F-005, F-006, F-007 should be marked INVALIDATED

## DOE-007: Layer Ablation Study
- Single-factor design: action_strategy with 5 levels
- Levels: random, L0_only, L0_memory, L0_strength, full_agent
- 30 episodes per level, 150 total
- Seeds: 4501 + i*31, i=0..29 (range [4501, 5400])
- Analysis: One-way ANOVA with Tukey HSD
- Key question: do heuristic layers contribute beyond L0 reflex rules?

## Seed Set Information
- DOE-001: 42 + i*31, i=0..69 (70 seeds, range [42, 2211])
- DOE-002: 1337 + i*17, i=0..29 (30 seeds, range [1337, 1830])
- DOE-005: 2501 + i*23, i=0..29 (30 seeds, range [2501, 3168])
- DOE-006: 3501 + i*29, i=0..29 (30 seeds, range [3501, 4342])
- DOE-007: 4501 + i*31, i=0..29 (30 seeds, range [4501, 5400])
- All ranges verified: zero cross-experiment collisions

## Hypothesis Status Summary
- H-001 (Full > Random): ADOPTED MEDIUM
- H-002 (Rule > Random): ADOPTED MEDIUM
- H-003 (Latency): ADOPTED MEDIUM
- H-004 (Memory optimization): CLOSED (superseded by DOE-005/006 nulls)
- H-005 (Doc quality): QUEUED
- H-006 (Memory main effect): ADOPTED MEDIUM (DOE-002 data INVALIDATED)
- H-007 (Strength main effect): ADOPTED MEDIUM (DOE-002 data INVALIDATED)
- H-008 (Interaction): ADOPTED MEDIUM (DOE-002 data INVALIDATED)
- H-009 (Trend beyond 0.7): REJECTED
- H-010 (Effects at [0.3, 0.7] real data): REJECTED (DOE-006 null)
- H-011 (Layer ablation): ACTIVE, DOE-007 ORDERED

## Lessons Learned
- Real VizDoom kill_rate is zero-inflated and right-skewed; always plan non-parametric fallbacks
- KILLCOUNT mapping must be verified before every experiment execution
- DOE-002 diagnostics all PASSED but data was fundamentally wrong -- diagnostics check assumptions, not measurement validity
- Performance is flat at ~8.4 kills/min regardless of memory_weight or strength_weight [0.3-0.9]
- Cross-experiment replication checks essential when measurement instruments change
- Arithmetic seed sequences (base + i*step) reliable for avoiding collisions
- Always verify seed ranges against ALL prior experiments
- When parameter optimization yields null results, ablation study is the correct next step to test whether the LAYERS themselves contribute
- 4 experiments on Memory-Strength produced no real effects -- pivot faster in future
