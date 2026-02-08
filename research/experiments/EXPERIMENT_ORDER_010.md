# EXPERIMENT_ORDER_010: Structured Lateral Movement Strategies

## Metadata
- **Experiment ID**: DOE-010
- **Hypothesis**: H-014
- **DOE Phase**: Phase 1 (architecture exploration)
- **Design Type**: One-way completely randomized design
- **Date Ordered**: 2026-02-08

## Research Question

Does the PATTERN of lateral movement matter for kill_rate on defend_the_line, or only its PRESENCE?

DOE-008 established that any lateral movement improves kill_rate over pure L0 rules (+5.7 kr, p<0.001), but random, L0_memory, L0_strength, and full_agent all performed equally (~38 kr). This experiment tests whether deterministic structured patterns (sweep, burst-fire) can outperform random movement.

## Hypothesis

**H-014**: Structured lateral movement patterns (sweep, burst-fire) produce higher kill_rate than random lateral movement on defend_the_line.

## Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| action_strategy | Categorical | 5 | Action selection architecture |

### Factor Levels

| Level | Condition Label | Description | Lateral Movement Ratio |
|-------|----------------|-------------|----------------------|
| 1 | strategy=random | Uniform random (33% each action) | 67% |
| 2 | strategy=L0_only | L0 rules: attack unless health<20/ammo=0 | ~5% |
| 3 | strategy=sweep_lr | Deterministic: attack->left->attack->right cycle | 50% |
| 4 | strategy=burst_3 | 3 attacks then 1 random move | 25% |
| 5 | strategy=burst_5 | 5 attacks then 1 random move | 17% |

### Strategy Design Rationale

- **sweep_lr** (50% lateral): Highest lateral movement among structured strategies. Tests whether systematic sweeping across the enemy line improves coverage.
- **burst_3** (25% lateral): Moderate lateral movement. Concentrated fire windows of 3 attacks separated by repositioning.
- **burst_5** (17% lateral): Low lateral movement. Longer burst windows of 5 attacks. Tests whether maximizing attack frequency improves kill rate.
- **L0_only** (~5% lateral): Negative control. Expected to be worst (DOE-008 F-010).
- **random** (67% lateral): Baseline. DOE-008 showed this performs as well as any reactive strategy.

## Design Matrix

| Run | Condition | Action Type | Episodes | Seeds |
|-----|-----------|-------------|----------|-------|
| R1 | strategy=random | random | 30 | [10001, ..., 11248] |
| R2 | strategy=L0_only | rule_only | 30 | [10001, ..., 11248] |
| R3 | strategy=sweep_lr | sweep_lr | 30 | [10001, ..., 11248] |
| R4 | strategy=burst_3 | burst_3 | 30 | [10001, ..., 11248] |
| R5 | strategy=burst_5 | burst_5 | 30 | [10001, ..., 11248] |

**Total**: 5 conditions x 30 episodes = 150 episodes

## Randomized Execution Order

R4 (burst_3) -> R2 (L0_only) -> R5 (burst_5) -> R1 (random) -> R3 (sweep_lr)

## Seed Set

**Formula**: seed_i = 10001 + i x 43, i = 0, 1, ..., 29
**Range**: [10001, 11248]
**No collisions**: Prior experiments used seeds <= 9190 (DOE-009)

## Scenario

**defend_the_line.cfg** (standard per F-012)
- Episode timeout: 2100 ticks (60s at 35 fps)
- Known limitation: AMMO2 tracking unreliable (enemy ammo drops)
- Primary response: kill_rate (kills per minute)
- Secondary responses: kills, survival_time

## Statistical Analysis Plan

1. **Primary**: One-way ANOVA on kill_rate (5 levels)
2. **Residual diagnostics**: Normality (Shapiro-Wilk), equal variance (Levene)
3. **If significant**: Tukey HSD pairwise comparisons, planned contrasts:
   - C1: L0_only vs all others (replication of DOE-008 F-010)
   - C2: random vs structured (sweep_lr, burst_3, burst_5) -- tests H-014
   - C3: sweep_lr vs burst strategies -- tests pattern type effect
4. **Effect sizes**: Cohen's d for pairwise, eta-squared for overall
5. **Non-parametric backup**: Kruskal-Wallis if normality violated

## Known Limitations

1. AMMO2 tracking broken for defend_the_line (ammo pickups from dead enemies)
2. L0 emergency rules (health<20, ammo=0) apply to all strategies -- may dilute pattern effects near death
3. 3-action space (attack, move_left, move_right) limits expressiveness
4. No aim/angle control -- movement only shifts firing angle indirectly
