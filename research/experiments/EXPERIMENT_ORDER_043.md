# EXPERIMENT_ORDER_043: Hybrid Navigation+Combat Strategies for deadly_corridor

## Hypothesis
H-046: Hybrid strategies that combine structured forward navigation with stochastic combat/evasion elements outperform pure random_7 on deadly_corridor.cfg, where 73% of episodes currently produce zero kills.

## Research Question
DOE-041 established that random_7 significantly outperforms simple deterministic strategies (attack_only, forward_attack) on deadly_corridor (F-112, Cohen's d=0.856). However, pure random_7 still yields only 0.5 mean kills with 73% zero-kill episodes. Can we improve on randomness by biasing action selection toward corridor-relevant behaviors — specifically forward navigation (to reach enemies) and lateral evasion (to dodge projectiles) — while retaining stochastic diversity for combat situations? This tests whether informed randomness beats uninformed randomness in a navigation-heavy scenario.

## Design
- **Type**: One-Way CRD (five levels)
- **Factor**: Hybrid Action Strategy
- **Scenario**: deadly_corridor.cfg (7 actions available: MOVE_LEFT, MOVE_RIGHT, ATTACK, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT)
- **num_actions**: 7
- **doom_skill**: 3 (consistent with DOE-041)
- **Episodes per condition**: 30
- **Total episodes**: 150

## Conditions

| Run | Condition | Strategy | Action Probability Distribution | Rationale |
|-----|-----------|----------|-------------------------------|-----------|
| R1 | random_7 | random_7 | Uniform: each action = 1/7 (14.3%) | Baseline from DOE-041 (mean=0.50 kills). Uninformed stochastic exploration. |
| R2 | forward_biased | forward_biased_7 | MOVE_FORWARD=35%, ATTACK=25%, MOVE_LEFT=10%, MOVE_RIGHT=10%, MOVE_BACKWARD=5%, TURN_LEFT=7.5%, TURN_RIGHT=7.5% | Biases toward forward corridor traversal and attack. Reduces backward/turning waste. Hypothesis: reaching enemies faster increases kill opportunities. |
| R3 | strafe_dodge | strafe_dodge_7 | MOVE_LEFT=20%, MOVE_RIGHT=20%, ATTACK=25%, MOVE_FORWARD=20%, MOVE_BACKWARD=5%, TURN_LEFT=5%, TURN_RIGHT=5% | Emphasizes lateral dodging (40% strafe) + forward push + attack. Hypothesis: dodging projectiles while advancing increases survival and kills. |
| R4 | burst_advance | burst_advance_7 | Phase-based: 3-tick forward burst then 1-tick random from remaining 6 actions, cycling. Effective distribution: MOVE_FORWARD=75% of ticks in burst phase, other 6 actions=16.7% each in random phase. Overall: MOVE_FORWARD=56.25%, others=7.3% each. | Structured corridor traversal in bursts with stochastic combat/evasion interludes. Hypothesis: rapid advances close distance to enemies, random phases handle combat. |
| R5 | adaptive_aggression | adaptive_aggression_7 | MOVE_FORWARD=30%, ATTACK=30%, MOVE_LEFT=12.5%, MOVE_RIGHT=12.5%, MOVE_BACKWARD=5%, TURN_LEFT=5%, TURN_RIGHT=5% | Balanced forward+attack emphasis (60% combined) with moderate evasion. Compared to forward_biased, increases attack probability at cost of forward movement. Tests whether more shooting compensates for slower corridor progress. |

### Strategy Implementation Notes

All strategies use the 7-action space. Implementation approaches:

1. **random_7**: `random.choice(actions)` — uniform random (existing implementation).
2. **forward_biased_7**: Weighted random selection via `random.choices(actions, weights=[0.10, 0.10, 0.25, 0.35, 0.05, 0.075, 0.075])`.
3. **strafe_dodge_7**: Weighted random selection via `random.choices(actions, weights=[0.20, 0.20, 0.25, 0.20, 0.05, 0.05, 0.05])`.
4. **burst_advance_7**: State machine: `if tick_in_burst < 3: MOVE_FORWARD; else: random.choice(other_6_actions); reset burst counter after random tick`.
5. **adaptive_aggression_7**: Weighted random selection via `random.choices(actions, weights=[0.125, 0.125, 0.30, 0.30, 0.05, 0.05, 0.05])`.

Action order for weight vectors: [MOVE_LEFT, MOVE_RIGHT, ATTACK, MOVE_FORWARD, MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT].

## Seed Set
Formula: seed_i = 97001 + i * 199, i = 0..29
Set: [97001, 97200, 97399, 97598, 97797, 97996, 98195, 98394, 98593, 98792, 98991, 99190, 99389, 99588, 99787, 99986, 100185, 100384, 100583, 100782, 100981, 101180, 101379, 101578, 101777, 101976, 102175, 102374, 102573, 102772]

## Analysis Plan
1. One-way ANOVA on kills (primary metric)
2. Kruskal-Wallis test as non-parametric backup (zero-inflated distribution expected per DOE-041)
3. Dunnett's test: compare all hybrid strategies against random_7 baseline
4. Tukey HSD pairwise comparisons with 95% family-wise CI
5. Effect sizes: partial eta-squared for overall model, Cohen's d for pairwise comparisons
6. Residual diagnostics: normality (Anderson-Darling), equal variance (Levene)
7. Survival time analysis (secondary metric: corridor traversal efficiency)
8. Kill rate analysis (kills/min as tertiary metric)
9. Zero-kill proportion comparison across strategies (chi-squared or Fisher exact)
10. Summary statistics: mean, sd, min, max, median for each condition

### Statistical Power Considerations
- DOE-041 observed eta-squared=0.137 with 3 groups at n=30
- With 5 groups at n=30, power for detecting similar effect may be lower
- If overall ANOVA is marginal (0.01 < p < 0.05), focus on Dunnett comparisons against random_7 baseline
- Zero-inflation limits parametric power; non-parametric tests serve as primary confirmation

## Expected Outcome
- **forward_biased_7**: Moderate improvement over random_7. Reaching enemies faster should increase kill opportunity windows, but biased movement may be more predictable.
- **strafe_dodge_7**: Potential best performer. Lateral dodging addresses the primary death cause (projectile hits) while maintaining forward push and attack frequency.
- **burst_advance_7**: High variance expected. Rapid forward bursts close distance quickly but create vulnerability during burst phase. May produce bimodal outcomes (quick kills or quick deaths).
- **adaptive_aggression_7**: Similar to random_7 but with forward+attack emphasis. May show marginal improvement due to higher attack frequency.
- **Null hypothesis plausible**: If deadly_corridor's difficulty ceiling is structural (enemy density, corridor geometry), no action probability weighting may overcome the 73% zero-kill floor.

## Linked Hypotheses and Findings
- F-112: random_7 outperforms deterministic strategies on deadly_corridor (DOE-041, d=0.856)
- F-079: Movement is sole performance determinant on defend_the_line (DOE-029)
- F-087: Optimal action space is 5-7 actions (DOE-031)
- F-030: 3-action agents achieve 0 kills on deadly_corridor (DOE-016)
- H-044: Movement-based strategies outperform stationary on deadly_corridor (confirmed by DOE-041)
- This experiment extends the question: given that random movement helps, can structured movement help more?

## Execution Notes
- Use VizDoom deadly_corridor scenario
- doom_skill = 3 (moderate difficulty, consistent with DOE-041 for direct comparison)
- Record: kills, survival_time, ammo_efficiency, shots_fired
- DuckDB table: experiments.DOE_043
- Random seed consumption: 150 seeds total (30 per condition x 5 conditions)
- Implementation requires weighted random selection capability in the agent action function
- burst_advance_7 requires a simple state machine (3-tick counter) — may need custom action function
- Verify all 5 strategies use identical seed sets for within-seed comparison
- Note: deadly_corridor's 73% zero-kill rate (DOE-041) limits statistical resolution; focus on whether ANY hybrid strategy shifts the zero-kill proportion
