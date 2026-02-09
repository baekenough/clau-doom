# Research PI Memory

## Project State
- **Current Phase**: Phase 2 (L2 Architecture Redesign / Meta-Strategy)
- **Hypotheses**: 27 total (H-001 through H-027)
- **Experiment Orders**: 24 written (DOE-001 through DOE-024)
- **Findings**: 56 (F-001 through F-056)
- **Total Episodes Executed**: ~3000+ (DOE-001 through DOE-023 complete)
- **DOE-024**: ORDERED, 360 episodes pending (L2 meta-strategy selection)

## Active Research Thread: L2 Meta-Strategy Selection
- DOE-022: L2 action-level selection FAILED (F-049, d=1.641 regression)
- Root cause: tactic_to_action() too coarse, replaces burst_3 patterns with constant ATTACK
- F-050: Document quality irrelevant under coarse mapping (d=0.000)
- F-051: L1 periodic patterns MUST be preserved when adding L2
- DOE-023: Strategy rankings change with difficulty (F-053, interaction p=6.02e-04)
- **DOE-024 Fix**: L2 selects STRATEGY NAME (meta-level), delegates to L1 function (preserves patterns)
- H-027: ACTIVE -- L2 meta-strategy selection vs fixed strategies across 3 difficulty levels

## Key Phase 1 Results (DOE-008 through DOE-021)
- burst_3 globally optimal in 3-action space (F-039, DOE-021 evolution confirmed F-046)
- adaptive_kill: kill_rate champion but degrades at Nightmare (F-055)
- L0_only: universally worst (F-034, 3x replication)
- 3-action space ceiling: ~43 kr regardless of strategy (F-035)
- doom_skill dominates kills variance at 72% (F-052)

## DOE-023 Cross-Difficulty Rankings (Critical for DOE-024)
- Easy: adaptive_kill (22.93) > random (19.73) > burst_3 (19.73) > L0_only (15.63)
- Normal: random (13.73) > adaptive_kill (13.43) > burst_3 (12.17) > L0_only (9.57)
- Nightmare: random (4.97) > burst_3 (4.43) > adaptive_kill (3.87) > L0_only (3.57)
- Effect compression: strategy spread shrinks 5.2x from Easy to Nightmare (F-054)

## Seed Set Information (Comprehensive)
- DOE-001 through DOE-020: ranges [42, 23581]
- DOE-021: [23001, 38104] (5 generations)
- DOE-022: [24001, 26814]
- DOE-023: [25001, 27930]
- DOE-024: [40001, 42988] (40001 + i*103, i=0..29)
- Maximum seed used: 42988 (DOE-024)
- All ranges verified: zero cross-experiment collisions

## Hypothesis Status Summary (Active)
- H-005 (Doc quality): Tested by DOE-022, document quality irrelevant under coarse mapping
- H-027 (L2 meta-strategy): ACTIVE -- DOE-024 ORDERED

## Key L2 Architecture Lessons
- L2 must NOT replace L1 patterns -- it must select which L1 to delegate to
- tactic_to_action() mapping is fundamentally broken for 3-action space (most tactics -> ATTACK)
- Document quality only matters when the action mapping has sufficient granularity
- Meta-strategy selection (strategy name, not action) is the correct L2 abstraction level
- Query caching (1 qps not 35 qps) essential for OpenSearch load management
- Strategy switching has overhead cost -- must be infrequent (once/second max)

## Lessons Learned (Cumulative)
- Real VizDoom kill_rate is zero-inflated and right-skewed; always plan non-parametric fallbacks
- Performance is flat at ~42 kr regardless of strategy in 3-action space
- defend_the_line is standard scenario (F-012); basic.cfg and deadly_corridor have floor effects
- TURN_LEFT/TURN_RIGHT != MOVE_LEFT/MOVE_RIGHT -- always verify button mapping
- Cross-experiment replication essential when measurement instruments change
- Arithmetic seed sequences (base + i*step) reliable for avoiding collisions
- Pivot faster when parameter optimization yields null results
- L2 RAG at action level fails; L2 RAG at meta-strategy level is the corrective hypothesis
- doom_skill parameter works for difficulty variation (no WAD editing needed)
- Effect compression at high difficulty limits strategy differentiation absolute values
