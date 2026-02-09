# EXPERIMENT_ORDER_023: Cross-Scenario Strategy Robustness

## Metadata
- **Experiment ID**: DOE-023
- **Hypothesis**: H-026 — Top-tier strategies maintain performance advantage over baselines across scenario variants
- **DOE Phase**: Phase 1 (Generalization)
- **Design Type**: 3 x 4 factorial (Scenario x Strategy), split-plot with scenario as whole-plot factor
- **Date Ordered**: 2026-02-09
- **Prior Art**: DOE-008 through DOE-020 (all defend_the_line), DOE-015 (basic.cfg rejection), DOE-016 (deadly_corridor rejection)

## Research Question

Do the strategy performance rankings established on defend_the_line generalize to scenario variants with different difficulty parameters? Specifically, do burst_3 and adaptive_kill maintain their advantage over baselines (random, attack_only) when monster density, engagement distance, and episode duration are varied?

### Background

All DOE-008 through DOE-020 experiments used a single scenario configuration:

```
defend_the_line.cfg
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

Key established performance rankings on defend_the_line (from DOE-020, F-036, F-038):
- **burst_3**: 45.44 kr, 15.40 kills, 20.53s survival (kills champion)
- **adaptive_kill**: 45.97 kr, 13.03 kills, 17.16s survival (kill_rate champion)
- **random**: 42.40 kr, 13.27 kills, 18.80s survival (universal baseline)
- **attack_only**: 38.88 kr, 10.70 kills, 16.50s survival (pure aggression)

Critical limitation: these rankings have only been validated on ONE scenario. Publication requires evidence of generalization. Prior cross-scenario experiments (DOE-015: basic.cfg, DOE-016: deadly_corridor) failed due to floor effects. DOE-023 uses defend_the_line VARIANTS rather than entirely different scenarios to avoid domain mismatch while testing robustness.

### Why Variants Instead of New Scenarios

1. **Controlled manipulation**: Each variant changes exactly one parameter from defend_the_line, enabling causal attribution
2. **Avoidance of floor/ceiling effects**: basic.cfg (F-029) and deadly_corridor (F-030) were rejected due to extreme floor effects. Variants of a known-working scenario reduce this risk
3. **Same action space**: All variants use the same 3-action space (TURN_LEFT, TURN_RIGHT, ATTACK), enabling direct comparison with the 13-experiment defend_the_line corpus
4. **Same game variables**: KILLCOUNT, HEALTH, AMMO2 tracked identically across variants

### Hypothesis

**H-026: Strategy Performance Generalizes Across Defend_the_Line Variants**

Top-tier strategies (burst_3, adaptive_kill) maintain their performance advantage over baselines (random, attack_only) across scenario variants that modify difficulty parameters (monster density, engagement distance, episode duration). If true, the strategy rankings from DOE-008~020 are robust properties of the strategies, not artifacts of one specific scenario configuration.

**Predictions**:
1. Strategy main effect significant (p < 0.05) — rankings hold across scenarios
2. Scenario main effect significant (p < 0.05) — variants differ in difficulty
3. Strategy x Scenario interaction NOT significant — strategy effectiveness is scenario-independent
4. If interaction IS significant — strategy effectiveness depends on scenario context

## Factors

| Factor | Type | Role | Levels | Description |
|--------|------|------|--------|-------------|
| Scenario | Categorical | Whole-plot (blocking) | 3 | defend_the_line variant |
| Strategy | Categorical | Sub-plot (treatment) | 4 | Action strategy |

### Scenario Levels (Whole-Plot Factor)

| Level | Label | Modification from defend_the_line | Expected Effect |
|-------|-------|----------------------------------|-----------------|
| 1 | **hard** | Double monster spawn count (8 -> 16 initial), 1.5x projectile speed | Higher kill opportunity, lower survival, increased pressure |
| 2 | **close** | Reduced engagement distance (enemies spawn closer to player) | Higher kill_rate (shorter targeting time), lower survival (less reaction time) |
| 3 | **slow** | Double episode timeout (2100 -> 4200 ticks = 120s) | More total kills, similar kill_rate if strategy is stable over time |

### Strategy Levels (Sub-Plot Factor)

| Level | Label | Description | DOE-020 Baseline |
|-------|-------|-------------|-----------------|
| 1 | **burst_3** | 3 attacks + 1 turn (repeat) | 45.44 kr, 15.40 kills |
| 2 | **adaptive_kill** | State-dependent: attack when kills < 10, burst_3 when kills >= 10 | 45.97 kr, 13.03 kills |
| 3 | **random** | Uniform random from {TURN_LEFT, TURN_RIGHT, ATTACK} | 42.40 kr, 13.27 kills |
| 4 | **attack_only** | 100% ATTACK every tick | 38.88 kr, 10.70 kills |

### Strategy Selection Rationale

**Included**:
- **burst_3**: Kills champion across DOE-012/013/017/019/020 (5 experiments). Best total lethality.
- **adaptive_kill**: Kill_rate champion in DOE-018/019/020 (3 experiments). State-dependent logic.
- **random**: Universal baseline across 13 experiments. Anchors all comparisons.
- **attack_only**: Pure aggression baseline. Known deficit on kills (F-031) but useful lower bound.

**Excluded**:
- **compound_attack_turn**: Confirmed non-competitive in DOE-012 (F-026) and DOE-020 (F-037). No advantage over attack_only (d=0.01).
- **L0_only**: Definitively worst performer across 3 experiments (F-034, d=0.83-1.48). Excluding saves 90 episodes.

## Design Matrix

| Run | Scenario | Strategy | n | Seeds |
|-----|----------|----------|---|-------|
| R1 | hard | burst_3 | 30 | [25001, 25102, ..., 27930] |
| R2 | hard | adaptive_kill | 30 | [25001, 25102, ..., 27930] |
| R3 | hard | random | 30 | [25001, 25102, ..., 27930] |
| R4 | hard | attack_only | 30 | [25001, 25102, ..., 27930] |
| R5 | close | burst_3 | 30 | [25001, 25102, ..., 27930] |
| R6 | close | adaptive_kill | 30 | [25001, 25102, ..., 27930] |
| R7 | close | random | 30 | [25001, 25102, ..., 27930] |
| R8 | close | attack_only | 30 | [25001, 25102, ..., 27930] |
| R9 | slow | burst_3 | 30 | [25001, 25102, ..., 27930] |
| R10 | slow | adaptive_kill | 30 | [25001, 25102, ..., 27930] |
| R11 | slow | random | 30 | [25001, 25102, ..., 27930] |
| R12 | slow | attack_only | 30 | [25001, 25102, ..., 27930] |

**Total**: 3 scenarios x 4 strategies x 30 episodes = 360 episodes

### Randomized Execution Order

Within each scenario block (whole-plot), randomize strategy order:
- **hard**: R3 (random) -> R1 (burst_3) -> R4 (attack_only) -> R2 (adaptive_kill)
- **close**: R6 (adaptive_kill) -> R8 (attack_only) -> R5 (burst_3) -> R7 (random)
- **slow**: R11 (random) -> R9 (burst_3) -> R10 (adaptive_kill) -> R12 (attack_only)

Scenario block order: hard -> close -> slow

## Seed Set

**Formula**: seed_i = 25001 + i x 101, i = 0, 1, ..., 29
**Range**: [25001, 27930]
**Count**: 30 seeds per cell, identical across all 12 cells

**Full seed set**:
```
[25001, 25102, 25203, 25304, 25405, 25506, 25607, 25708, 25809, 25910,
 26011, 26112, 26213, 26314, 26415, 26516, 26617, 26718, 26819, 26920,
 27021, 27122, 27223, 27324, 27425, 27526, 27627, 27728, 27829, 27930]
```

### Cross-Experiment Seed Collision Check

| Experiment | Seed Range | Increment | Collision with DOE-023? |
|-----------|------------|-----------|------------------------|
| DOE-001 | [42, 2191] | 31 | NO (disjoint) |
| DOE-002 | [1337, 1830] | 17 | NO (disjoint) |
| DOE-003 | [2023, 2690] | 23 | NO (disjoint) |
| DOE-004 | [7890, 8527] | 13 | NO (disjoint) |
| DOE-005 | [2501, 3168] | 23 | NO (disjoint) |
| DOE-006 | [3501, 4342] | 29 | NO (disjoint) |
| DOE-007 | [4501, 5400] | 31 | NO (disjoint) |
| DOE-008 | [6001, 7074] | 37 | NO (disjoint) |
| DOE-009 | [8001, 9190] | 41 | NO (disjoint) |
| DOE-010 | [10001, 11248] | 43 | NO (disjoint) |
| DOE-011 | [12001, 13364] | 47 | NO (disjoint) |
| DOE-012 | [13001, 14538] | 53 | NO (disjoint) |
| DOE-013 | [14001, 15712] | 59 | NO (disjoint) |
| DOE-014 | [15001, 16770] | 61 | NO (disjoint) |
| DOE-015 | [16001, 17944] | 67 | NO (disjoint) |
| DOE-016 | [17001, 18060] | 71 | NO (disjoint) |
| DOE-017 | [18001, 19118] | 73 | NO (disjoint) |
| DOE-018 | [19001, 20292] | 79 | NO (disjoint) |
| DOE-019 | [20001, 22404] | 83 | NO (disjoint) |
| DOE-020 | [21001, 23581] | 89 | NO (disjoint) |
| DOE-021 | TBD | — | Check before execution |
| DOE-022 | TBD | — | Check before execution |

**Verdict**: DOE-023 range [25001, 27930] is strictly above the maximum of all prior experiments (23581). Zero seed collisions guaranteed. No GCD analysis needed (ranges are disjoint).

## Scenario Configuration Details

### Variant 1: defend_the_line_hard.cfg

**Modifications from defend_the_line.cfg**:
```diff
# Same base configuration
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
- episode_timeout = 2100
+ episode_timeout = 2100  # unchanged (60s)

# WAD/map modifications needed:
+ # Double initial monster spawn count: 8 -> 16
+ # Increase monster projectile speed: 1.5x base velocity
+ # Same spawn locations (line formation)
+ # Same player position
```

**Implementation Notes**:
- Modify the WAD file or use DeHackEd/DECORATE lumps to increase spawn count
- Alternatively, use VizDoom's `doom_skill` parameter or custom ACS scripts
- If WAD modification is complex, consider using VizDoom's `living_reward` or spawn rate manipulation via ACS
- Projectile speed modification may require DeHackEd patches

**Expected Behavior**:
- More targets available -> kills may increase
- Faster projectiles -> survival decreases
- Higher pressure -> strategy differences may amplify
- Risk: could become too hard (like deadly_corridor) if monsters overwhelm player instantly

**Mitigation**: Run 5-episode pilot before full experiment. If mean survival < 5s or mean kills < 3, reduce monster count to 12 instead of 16.

### Variant 2: defend_the_line_close.cfg

**Modifications from defend_the_line.cfg**:
```diff
# Same base configuration
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # unchanged (60s)

# WAD/map modifications needed:
+ # Reduce enemy spawn distance: move spawn line closer to player
+ # Approximately 50% of original distance
+ # Same number of monsters (8 initial)
+ # Same projectile speed
```

**Implementation Notes**:
- Modify the WAD map to move monster spawn line closer
- Player position unchanged, enemy starting positions moved forward
- This changes engagement dynamics without modifying monster parameters
- Requires WAD editor (SLADE or similar) to adjust thing positions

**Expected Behavior**:
- Shorter target acquisition time -> kill_rate may increase
- Less reaction time for dodging -> survival decreases
- Close-quarters combat favors aggressive strategies
- Risk: may change relative value of turning vs attacking (less aiming needed at close range)

**Mitigation**: Run 5-episode pilot. If survival < 5s, increase distance to 75% of original.

### Variant 3: defend_the_line_slow.cfg

**Modifications from defend_the_line.cfg**:
```diff
# Same base configuration
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
- episode_timeout = 2100   # 60s at 35 fps
+ episode_timeout = 4200   # 120s at 35 fps

# No WAD/map modifications needed
# Same monster count, speed, positions
```

**Implementation Notes**:
- Simplest variant: only change episode_timeout in cfg file
- No WAD modifications required
- Tests strategy stability over longer episodes (fatigue test)
- If a strategy degrades over time (e.g., health depletion becomes inevitable), it will show in the second half

**Expected Behavior**:
- Total kills approximately double (proportional to time)
- kill_rate should remain similar if strategy is time-stable
- If kill_rate diverges from defend_the_line baseline, strategy has time-dependent performance
- Most informative for adaptive_kill (state transitions may occur more frequently in longer episodes)

**Mitigation**: No floor/ceiling risk (defend_the_line already validated). No pilot needed.

## Statistical Analysis Plan

### Primary Analysis: Two-Way ANOVA

**Model**: kill_rate ~ Scenario + Strategy + Scenario:Strategy

**Factors**:
- Scenario (3 levels): hard, close, slow — treated as fixed effect
- Strategy (4 levels): burst_3, adaptive_kill, random, attack_only — treated as fixed effect
- Scenario x Strategy interaction

**Degrees of Freedom**:
- Scenario: df = 2
- Strategy: df = 3
- Scenario x Strategy: df = 6
- Error: df = 348 (360 - 12)
- Total: df = 359

### Key Questions (in priority order)

**Q1: Strategy Main Effect** — Do strategy rankings hold across scenarios?
- If significant (p < 0.05): Strategy differences are ROBUST across scenario variants
- Expected: YES, based on consistent rankings across 5 prior seed validations (DOE-008/010/017/019/020)

**Q2: Scenario Main Effect** — Do scenarios differ in difficulty?
- If significant (p < 0.05): Variants successfully created different difficulty levels
- Expected: YES (hard should be harder, slow should produce more kills, close should change engagement dynamics)

**Q3: Strategy x Scenario Interaction** — Does strategy effectiveness depend on scenario?
- If NOT significant (p >= 0.05): Strategy rankings GENERALIZE — **strongest publication claim**
- If significant (p < 0.05): Strategy effectiveness is scenario-dependent — **more nuanced conclusion**

### Planned Contrasts

| Contrast | Comparison | Tests | Expected |
|----------|------------|-------|----------|
| C1 | {burst_3, adaptive_kill} vs {random, attack_only} | Top tier vs baselines across ALL scenarios | Significant (p < 0.01) |
| C2 | burst_3 vs adaptive_kill | Kills champion vs efficiency champion | NS (d < 0.3) based on DOE-020 |
| C3 | Interaction: C1 x Scenario | Does top-tier advantage vary by scenario? | NS if rankings generalize |
| C4 | hard vs close vs slow main effect | Difficulty gradient verification | Significant |

**Bonferroni correction**: alpha = 0.05 / 4 = 0.0125 for contrasts

### Residual Diagnostics (R100 Compliance)

1. **Normality**: Shapiro-Wilk or Anderson-Darling on residuals
2. **Equal variance**: Levene test across all 12 cells
3. **Independence**: Residuals vs run order within each scenario block
4. **Outlier detection**: Studentized residuals > |3|

### If Interaction IS Significant

Perform simple effects analysis:
- One-way ANOVA within each scenario (hard, close, slow separately)
- Compare strategy rankings per scenario
- Identify which scenario drives the interaction
- Report per-scenario Tukey HSD

### If ANOVA Assumptions Violated

- Normality violation: Kruskal-Wallis per scenario + Scheirer-Ray-Hare for interaction
- Variance heterogeneity: Welch's ANOVA per scenario, Brown-Forsythe test
- Both: Aligned Rank Transform (ART) ANOVA

### Effect Sizes

- Partial eta-squared for all ANOVA effects
- Cohen's d for planned contrasts
- Generalized eta-squared for cross-experiment comparison

### Secondary Responses

Repeat full analysis for:
- **kills** (total kills per episode)
- **survival_time** (seconds survived)

### Cross-Experiment Comparison

Compare DOE-023 results to DOE-020 defend_the_line baseline:
- burst_3 DOE-023 (per scenario) vs DOE-020 burst_3 (45.44 kr)
- adaptive_kill DOE-023 (per scenario) vs DOE-020 adaptive_kill (45.97 kr)
- random DOE-023 (per scenario) vs DOE-020 random (42.40 kr)
- attack_only DOE-023 (per scenario) vs DOE-020 attack_only (38.88 kr)

Use independent-samples t-tests with Bonferroni correction for cross-experiment comparisons.

### Power Analysis

- Two-way ANOVA with 3 x 4 = 12 cells, n = 30 per cell, alpha = 0.05
- For Strategy main effect (df = 3): Power > 0.95 for medium effect (f = 0.25) with N = 360
- For Scenario main effect (df = 2): Power > 0.95 for medium effect
- For interaction (df = 6): Power > 0.85 for medium effect
- Prior experiments observed f = 0.30-0.45 for strategy effects: Power > 0.99

## Success Criteria

### Outcome A: Generalization Confirmed (STRONGEST)

**Condition**: Strategy main effect significant AND interaction NOT significant

**Interpretation**: Strategy rankings from defend_the_line are ROBUST across scenario variants. burst_3 and adaptive_kill consistently outperform baselines regardless of monster density, engagement distance, or episode duration.

**Publication Claim**: "The performance hierarchy (burst > adaptive > random > attack_only) is a stable property of the strategies, not an artifact of one scenario configuration."

**Next Step**: Proceed to Phase 2 (generational evolution with confirmed optimal strategies)

### Outcome B: Scenario-Dependent Performance (NUANCED)

**Condition**: Strategy main effect significant AND interaction significant

**Interpretation**: Strategy effectiveness DEPENDS on scenario context. Some strategies may be better in specific conditions (e.g., burst_3 better in hard, adaptive_kill better in slow).

**Publication Claim**: "Strategy selection should be context-aware. Different environmental conditions favor different strategies."

**Next Step**: Characterize the interaction pattern; design adaptive meta-strategy that selects sub-strategy based on scenario features

### Outcome C: Strategy Differences Vanish (CONCERNING)

**Condition**: Strategy main effect NOT significant in new scenarios

**Interpretation**: Performance rankings from defend_the_line do NOT generalize. The established hierarchy was an artifact of the specific scenario configuration.

**Publication Claim**: "Strategy performance is scenario-specific, not a generalizable property of the strategy design."

**Next Step**: Investigate what scenario features drive performance; pivot to scenario-adaptive architecture

### Outcome D: Floor/Ceiling Effects (DIAGNOSTIC FAILURE)

**Condition**: One or more scenarios produce degenerate data (all kills = 0, or all survival < 5s)

**Interpretation**: Scenario variant too extreme. Not informative.

**Next Step**: Adjust variant parameters and re-run affected cells

## Risk Assessment

### Risk 1: Hard Variant Floor Effect (HIGH RISK)

**Concern**: 16 monsters with 1.5x projectile speed may overwhelm agents instantly, producing deadly_corridor-like floor effect (F-030).

**Mitigation**:
1. Run 5-episode pilot with random strategy before committing to full experiment
2. If mean survival < 5s OR mean kills < 3: reduce to 12 monsters or 1.25x projectile speed
3. Fallback: hard variant = 12 monsters, 1.0x speed (density only, no speed change)

### Risk 2: Close Variant Action Dynamics Change (MEDIUM RISK)

**Concern**: At very close range, ATTACK becomes nearly always optimal (enemies fill the screen). This could eliminate the value of turning/scanning, making random and burst_3 converge to attack_only behavior.

**Mitigation**:
1. Use 50% distance reduction as baseline (not extreme close-range)
2. If pilot shows all strategies converging to same kill_rate: increase distance to 75% of original
3. Monitor whether burst_3 and random still differentiate

### Risk 3: Slow Variant Non-Informative (LOW RISK)

**Concern**: Simply doubling timeout may produce proportionally scaled results (2x kills, same kill_rate) with no new information about strategy robustness.

**Mitigation**:
1. This is actually a POSITIVE outcome — if kill_rate is stable over 120s, it confirms time-invariance
2. The interesting case is if kill_rate CHANGES over time (health depletion, ammo effects)
3. Secondary analysis: split slow episodes into first-60s and second-60s to test time stability

### Risk 4: WAD Modification Complexity (MEDIUM RISK)

**Concern**: Creating hard and close variants requires WAD file editing, which may introduce unexpected behavior changes.

**Mitigation**:
1. Start with slow variant (cfg-only change, no WAD needed) as proof-of-concept
2. Use SLADE WAD editor for controlled modifications
3. Test each variant with 5-10 episodes before committing to full experiment
4. Document exact WAD changes for reproducibility

## Scenario Creation Guide

### defend_the_line_slow.cfg (Simplest — cfg-only)

```
# Copy defend_the_line.cfg and modify only:
episode_timeout = 4200  # 120 seconds (was 2100 = 60 seconds)

# All other parameters unchanged:
# - Same WAD file
# - Same buttons, variables
# - Same monster configuration
```

### defend_the_line_hard.cfg (WAD modification required)

**Option A: ACS Script (preferred if VizDoom supports)**
```
# Add ACS script to spawn additional monsters at episode start
# Modify spawn frequency to increase density
# Increase projectile speed via DeHackEd
```

**Option B: WAD Editor (SLADE)**
```
1. Open defend_the_line.wad in SLADE
2. Duplicate existing monster things (copy 8 monster placements)
3. Place duplicates at same spawn line positions
4. If projectile speed modification needed:
   - Create DEHACKED lump
   - Modify missile speed for relevant monster type
5. Save as defend_the_line_hard.wad
6. Update cfg to reference new WAD
```

### defend_the_line_close.cfg (WAD modification required)

```
1. Open defend_the_line.wad in SLADE
2. Select all monster thing entries
3. Move spawn line Y-coordinate closer to player position
4. Target: approximately 50% of original distance
5. Keep all other thing properties unchanged
6. Save as defend_the_line_close.wad
7. Update cfg to reference new WAD
```

## Pilot Study Plan

**Before full experiment**, run pilot studies on hard and close variants:

| Variant | Pilot Episodes | Strategy | Pass Criteria |
|---------|---------------|----------|---------------|
| hard | 5 | random | mean survival > 5s AND mean kills > 3 |
| close | 5 | random | kill_rate within 2x of baseline AND survival > 5s |
| slow | 0 (no pilot needed) | — | cfg-only change, known-safe |

If pilot fails, adjust variant parameters and re-pilot.

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 25001 + i x 101, i=0..29 |
| No seed collisions | YES: [25001, 27930] above all prior maxima (23581) |
| n >= 30 per condition | YES: 30 episodes per cell, 12 cells, 360 total |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, variance, independence per R100 |
| Effect sizes | PLANNED: partial eta-squared, Cohen's d |
| Seeds identical across conditions | YES: same 30 seeds for all 12 cells |
| Power adequate | YES: N=360 provides >0.95 power for medium effects |

## Execution Checklist

Before execution, verify:
- [ ] defend_the_line_hard.cfg created and tested (5-episode pilot passed)
- [ ] defend_the_line_close.cfg created and tested (5-episode pilot passed)
- [ ] defend_the_line_slow.cfg created and tested
- [ ] All 4 action functions available: burst_3, adaptive_kill, random, attack_only
- [ ] burst_3 replicates DOE-020 pattern (3 attacks + 1 turn)
- [ ] adaptive_kill replicates DOE-018/019/020 state-dependent logic
- [ ] Seed set generated and logged (30 seeds, formula verified)
- [ ] DuckDB experiment table ready with DOE-023 schema
- [ ] WAD files documented for reproducibility
- [ ] Pilot study results documented in RESEARCH_LOG.md

## Audit Trail

| Document | Status | Owner |
|----------|--------|-------|
| H-026 in HYPOTHESIS_BACKLOG.md | PENDING | research-pi |
| EXPERIMENT_ORDER_023.md | ORDERED | research-pi |
| EXPERIMENT_REPORT_023.md | PENDING | research-analyst |
| FINDINGS.md update | PENDING | research-pi |
| RESEARCH_LOG.md update | PENDING | research-pi |

## Status

**ORDERED** — Awaiting scenario variant creation and pilot validation before execution
