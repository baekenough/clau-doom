# Research PI Memory

## Project State
- **Current Phase**: Phase 2 (Generalizability Testing)
- **Hypotheses**: 35 total (H-001 through H-035)
- **Experiment Orders**: 32 written (DOE-001 through DOE-032)
- **Findings**: 83 (F-001 through F-083)
- **Total Episodes Executed**: 5010 (DOE-001 through DOE-029 complete)
- **DOE-030/031/032**: ORDERED, 820 episodes pending

## Active Research Thread: Generalizability Testing
- DOE-030 (H-033): Movement x difficulty interaction, 2x5 factorial, 300 ep
- DOE-031 (H-034): Action space dilution (3/5/7/9), one-way, 120 ep
- DOE-032 (H-035): L1 sequential cache learning, 2x2 factorial, 400 ep

## Central Findings (29-DOE Summary)
- F-079: Movement is SOLE performance determinant (d=1.408, largest in program)
- F-070: RAG hypothesis FALSIFIED (triple null: DOE-022/024/026)
- F-074: Rate-time compensation is fundamental environment constraint
- F-077: Full tactical invariance in 5-action space
- F-082/F-083: Compensation breaks at movement boundary
- F-052: doom_skill explains 72% of kills variance
- F-054: Effect compression 5.2x from Easy to Nightmare

## Seed Set Information (Comprehensive)
- DOE-001 through DOE-020: ranges [42, 23581]
- DOE-021: [23001, 38104]
- DOE-022: [24001, 26814]
- DOE-023: [25001, 27930]
- DOE-024: [40001, 42988]
- DOE-025: [45001, 48182] (45001 + i*107)
- DOE-026: [50001, 53162] (50001 + i*109)
- DOE-027: [47001, 50688] (47001 + i*127)
- DOE-028: [48001, 51811] (48001 + i*131)
- DOE-029: [49001, 52974] (49001 + i*137)
- DOE-030: [53001, 57032] (53001 + i*139)
- DOE-031: [57101, 61422] (57101 + i*149)
- DOE-032: [61501, 62977] (61501 + k*151 + i*13)
- Maximum seed used: 62977 (DOE-032)
- All ranges verified: zero cross-experiment collisions

## Key Architecture Lessons
- L2 RAG fails at ALL tested levels (action, meta-strategy, 5-action context)
- L1 sequential learning untested (DOE-032 will test)
- Movement is the only lever; all tactical choices are noise
- Rate-time compensation makes kill_rate invariant to strategy within movement class
- defend_the_line is standard scenario; basic.cfg and deadly_corridor have floor effects

## Lessons Learned (Cumulative)
- VizDoom kill_rate is zero-inflated and right-skewed; always plan non-parametric fallbacks
- Arithmetic seed sequences (base + i*step) reliable for avoiding collisions
- Pivot faster when parameter optimization yields null results
- doom_skill parameter works for difficulty variation (no WAD editing needed)
- Effect compression at high difficulty limits strategy differentiation absolute values
- 7-action and 9-action .cfg files need to be created for DOE-031
- DOE-032 requires careful L1 cache management (clear vs persist between episodes)
- Sequence-level means (not individual episodes) are the unit of observation for learning experiments

## Notes on DOE-032 Design
- Unit of observation: sequence mean (N=40), not individual episode (N=400)
- Mixed-effects model for learning slope uses all 400 episodes
- Power is marginal for medium effects; primarily exploratory
- If null: completes falsification narrative (neither L1 nor L2 learning helps)
- If positive: redirects research toward L1 optimization (breakthrough)
