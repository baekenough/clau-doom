# Research PI Memory

## Project State
- **Current Phase**: Phase 1 (Architecture Exploration / Action Space)
- **Hypotheses**: 15 total (H-001 through H-015)
- **Experiment Orders**: 11 written (DOE-001 through DOE-011)
- **Findings**: 19 (F-001 through F-019; F-002 INVALIDATED; F-005/F-006/F-007 INVALIDATED by DOE-009; F-008 REJECTED)
- **Total Episodes Executed**: ~1110 (DOE-001:210, DOE-002:150, DOE-005:150, DOE-006:150, DOE-007:150, DOE-008:150, DOE-009:270 est, DOE-010:150 est -- some pending verification)
- **DOE-011**: ORDERED, 150 episodes pending (5-action space experiment)

## Active Research Thread: Action Space Expansion
- DOE-008: L0_only worst (p=0.000555), any lateral movement helps equally
- DOE-010: Structured patterns do NOT outperform random (p=0.741)
- **Critical Discovery**: defend_the_line TURN_LEFT/TURN_RIGHT are rotation, not strafing
- Agent has NO physical movement in current action space
- DOE-011: Tests 5-action space (add true MOVE_LEFT/MOVE_RIGHT strafing)
- H-015: ACTIVE -- expanded action space should enable strategy differentiation

## Memory-Strength Thread: CLOSED
- memory_weight and strength_weight have NO detectable effect on kill_rate at ANY range [0.1, 0.9]
- DOE-002 effects were measurement artifacts (AMMO2 bug)
- DOE-005, DOE-006, DOE-009 all confirm null
- F-005, F-006, F-007 INVALIDATED

## Key Experimental Results
- defend_the_line is the standard evaluation scenario (F-012, HIGH trust)
- 3-action space ceiling: ~43 kr for any effective displacement strategy (F-019)
- L0_only deficit: ~39 kr due to tunnel vision (F-010, F-016)
- sweep_lr oscillation = functional stasis (F-017)
- Random is near-optimal in 3-action space (F-018)
- Performance hierarchy: {burst_3~burst_5~random ~43kr} > {sweep_lr~L0_only ~39kr}

## Seed Set Information
- DOE-001: 42 + i*31, i=0..69 (range [42, 2211])
- DOE-002: 1337 + i*17, i=0..29 (range [1337, 1830])
- DOE-005: 2501 + i*23, i=0..29 (range [2501, 3168])
- DOE-006: 3501 + i*29, i=0..29 (range [3501, 4342])
- DOE-007: 4501 + i*31, i=0..29 (range [4501, 5400])
- DOE-008: 6001 + i*37, i=0..29 (range [6001, 7074])
- DOE-009: 8001 + i*41, i=0..29 (range [8001, 9190])
- DOE-010: 10001 + i*43, i=0..29 (range [10001, 11248])
- DOE-011: 12001 + i*47, i=0..29 (range [12001, 13364])
- All ranges verified: zero cross-experiment collisions

## Hypothesis Status Summary
- H-001 (Full > Random): ADOPTED MEDIUM
- H-002 (Rule > Random): ADOPTED MEDIUM
- H-003 (Latency): ADOPTED MEDIUM
- H-004 (Memory optimization): CLOSED
- H-005 (Doc quality): QUEUED
- H-006/H-007/H-008: INVALIDATED by DOE-009
- H-009: REJECTED (plateau)
- H-010: REJECTED (DOE-006 null)
- H-011: CLOSED (Scenario D)
- H-012: ADOPTED HIGH (scenario discriminability)
- H-013: REJECTED (no parameter effects on defend_the_line)
- H-014: REJECTED (structured patterns do not beat random)
- H-015: ACTIVE (expanded action space) -- DOE-011 ORDERED

## Lessons Learned
- Real VizDoom kill_rate is zero-inflated and right-skewed; always plan non-parametric fallbacks
- KILLCOUNT mapping must be verified before every experiment execution
- Diagnostics check assumptions, not measurement validity
- Performance is flat at ~42 kr regardless of strategy in 3-action space
- Cross-experiment replication checks essential when measurement instruments change
- Arithmetic seed sequences (base + i*step) reliable for avoiding collisions
- Pivot faster when parameter optimization yields null results
- defend_the_center: 0-3 kills/episode, too simple; defend_the_line: 4-26 kills, better variance
- shots_fired/ammo_efficiency NOT reliable for defend_the_line (AMMO2 weapon type mismatch)
- TURN_LEFT/TURN_RIGHT != MOVE_LEFT/MOVE_RIGHT -- always verify button mapping in cfg
- When 3-action space shows random=optimal, expand action space before concluding strategies are useless
- Code variable names can be misleading (ACTION_MOVE_LEFT mapped to TURN_LEFT button)
