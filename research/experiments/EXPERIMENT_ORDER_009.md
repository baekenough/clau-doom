# EXPERIMENT_ORDER_009: Memory × Strength Factorial on defend_the_line

## Metadata
- **Experiment ID**: DOE-009
- **Hypothesis**: H-013 (Memory and strength weights have significant main effects and interaction on kill_rate in defend_the_line)
- **Prior**: H-006/H-007/H-008 adopted from MOCK data (DOE-002). DOE-009 is first REAL validation.
- **Predecessor**: DOE-008 (ablation, same scenario)
- **Date Ordered**: 2026-02-08
- **PI**: research-pi

## Research Question
Do memory_weight and strength_weight have significant main effects and/or interaction on kill_rate when tested with real VizDoom gameplay on defend_the_line?

## Design
- **Type**: 3×3 Full Factorial (Phase 1)
- **Factors**:
  - Factor A: memory_weight [0.1, 0.5, 0.9]
  - Factor B: strength_weight [0.1, 0.5, 0.9]
- **Response Variables**:
  - Primary: kill_rate (kills per minute)
  - Secondary: kills, survival_time
- **Excluded**: shots_fired, ammo_efficiency (AMMO2 broken on defend_the_line)
- **Cells**: 9
- **Episodes per cell**: 30
- **Total episodes**: 270

## Scenario
- **File**: defend_the_line.cfg
- **Episode timeout**: 2100 ticks (60 seconds at 35 fps)
- **Action space**: TURN_LEFT, TURN_RIGHT, ATTACK
- **Game variables**: KILLCOUNT (idx 0), HEALTH (idx 1), AMMO2 (idx 2)

## Action Function
All 9 runs use FullAgentAction with varying memory_weight and strength_weight.

## Seed Set
- **Formula**: seed_i = 8001 + i × 41, i = 0..29
- **Range**: [8001, 9190]
- **Count**: 30 seeds
- **Collision check**: No overlap with DOE-007 (5001+i*31: [5001,5900]), DOE-008 (6001+i*37: [6001,7074])

## Design Matrix (Randomized Run Order)

| Run Order | Run ID | memory_weight | strength_weight |
|-----------|--------|---------------|-----------------|
| 1 | R7 | 0.9 | 0.1 |
| 2 | R2 | 0.1 | 0.5 |
| 3 | R9 | 0.9 | 0.9 |
| 4 | R4 | 0.5 | 0.1 |
| 5 | R1 | 0.1 | 0.1 |
| 6 | R6 | 0.5 | 0.9 |
| 7 | R8 | 0.9 | 0.5 |
| 8 | R3 | 0.1 | 0.9 |
| 9 | R5 | 0.5 | 0.5 |

## Statistical Analysis Plan
1. Two-way ANOVA: memory_weight × strength_weight on kill_rate
2. Main effects: F-test for each factor
3. Interaction: F-test for memory × strength
4. Residual diagnostics: normality (Shapiro-Wilk), equal variance (Levene), independence
5. Effect sizes: partial η² for each factor and interaction
6. If significant: Tukey HSD post-hoc
7. Non-parametric fallback: Kruskal-Wallis if assumptions violated

## Expected Outcomes
- **A**: Both main effects significant, interaction significant (validates H-006/H-007/H-008 with real data)
- **B**: Main effects significant, no interaction (simpler model, memory and strength additive)
- **C**: One factor significant, other not (partial validation)
- **D**: No significant effects (DOE-002 mock results do not replicate)

## Known Limitations
- shots_fired and ammo_efficiency NOT available (AMMO2 increases in defend_the_line)
- FullAgentAction uses same L0 emergency rules (health<20 → dodge) for all conditions
- L0 dodge-left rule known to be counterproductive (DOE-008 F-010)

## Execution Instructions for research-doe-runner
1. Build config: `EXPERIMENT_BUILDERS['DOE-009']()`
2. Execute: `execute_experiment(config)`
3. Verify: 270 episodes in DuckDB, 9 conditions × 30 episodes each
