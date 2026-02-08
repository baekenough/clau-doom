# Research PI Memory

## Project State (Last Updated: 2026-02-08)
- DOE-001: Complete, MEDIUM trust (4 findings: F-001 to F-004)
- DOE-002: Complete, MEDIUM trust (3 findings: F-005 to F-007)
- Phase 0 baseline: ACHIEVED
- Phase 0/1 parameter screening: ACHIEVED
- DOE-005: ORDERED, 2x2 factorial at [0.7, 0.9] for H-009
- 8 hypotheses completed (H-001 to H-003, H-006 to H-008), 3 active (H-004, H-005, H-009)

## Key Findings

### Factor Importance Ranking (from DOE-002)
1. Memory (eta_p^2 = 0.4154) — dominant, 41.5% of variance
2. Strength (eta_p^2 = 0.3164) — strong, 31.6% of variance
3. Memory x Strength interaction (eta_p^2 = 0.0371) — small but significant synergy

### Critical Insight: No Curvature at [0.3, 0.7]
- Curvature test p=0.9614 → response surface is a tilted plane
- RSM is NOT warranted until curvature appears
- Follow steepest ascent: expand range upward before switching to RSM
- This overrides the default "significant factors → RSM" heuristic

### Interpretation Patterns
- "Knowing what to do" (Memory) > "how aggressively to act" (Strength)
- Informed cautious > uninformed aggressive (6.70 vs 5.99 kills/min)
- Synergistic interaction: experience amplifies aggression benefit

## Trust Elevation Decisions

### Pattern: Non-parametric Confirmation
- When normality fails but Mann-Whitney confirms: LOW → MEDIUM
- Requires: structural explanation + enormous effect sizes + adequate n

### Pattern: Clean Diagnostics but Small n
- When all diagnostics pass but n < 50/condition: MEDIUM (not HIGH)
- R100 HIGH threshold: n >= 50/condition + all diagnostics pass + p < 0.01
- DOE-002 had 30/cell — clean but not enough for HIGH

## Phase Transition Logic
- Phase 0 → Phase 1: When baseline validated (ACHIEVED after DOE-001)
- Phase 1 → Phase 2 (RSM): ONLY when curvature detected at center points
- If no curvature: stay in Phase 1, expand factorial range (steepest ascent)
- DOE-002 showed no curvature → expand to [0.7, 0.9] before RSM

## Experiment Sequence
- DOE-001: Baseline OFAT (complete, MEDIUM trust)
- DOE-002: 2x2 factorial memory x strength at [0.3, 0.7] (complete, MEDIUM trust)
- DOE-005: 2x2 factorial at expanded [0.7, 0.9] (next, H-009)
- DOE-003: Layer ablation 2^3 (planned, H-005)
- DOE-004: Doc quality (planned)

## Seed Formulas
- DOE-001: seed_i = 42 + i*31, range [42, 941]
- DOE-002: seed_i = 1337 + i*17, range [1337, 1830]
- DOE-005: seed_i = 2501 + i*23, range [2501, 3168]

## DOE-005 Design Notes
- Overwrote previous DOE-005 (obsolete 3x2 + evolution hook for H-008)
- Cross-experiment anchor: cell (0.7, 0.7) overlaps with DOE-002 best
- Curvature test is THE phase-transition criterion
- Three scenarios: (A) linear continues, (B) curvature/RSM, (C) plateau
