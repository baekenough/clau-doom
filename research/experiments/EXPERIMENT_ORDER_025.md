# EXPERIMENT_ORDER_025.md

## DOE-025: 5-Action Strategy Optimization

**Hypothesis**: H-028 — In the 5-action space (turn+strafe+attack), strategies that balance attack and strafe actions create separable performance tiers for both kill-rate and survival, with meaningful differentiation absent in the 3-action space.

**Rationale**: DOE-001 through DOE-024 exhaustively explored the 3-action space (TURN_LEFT, TURN_RIGHT, ATTACK), establishing burst_3 as globally optimal (DOE-021) and demonstrating that L2 RAG cannot add value due to near-optimal random performance (F-018, F-057, F-061). DOE-011 briefly explored the 5-action space and found strafing dramatically improves survival (F-023, η²=0.225) while reducing kill_rate (F-020). This experiment systematically maps the 5-action strategy landscape by varying the attack/strafe ratio from 20% to 75%.

**Research Question**: Does the 5-action space create sufficient strategy differentiation that structured strategies meaningfully outperform random, unlike the 3-action space?

---

## Design

**Type**: One-way ANOVA (6 conditions)

**Scenario**: defend_the_line_5action.cfg

**Actions**: 0=TURN_LEFT, 1=TURN_RIGHT, 2=MOVE_LEFT, 3=MOVE_RIGHT, 4=ATTACK

**Difficulty**: doom_skill=3 (Normal)

**Episode Timeout**: 2100 ticks (60 seconds at 35fps)

**Sample Size**: 30 episodes per condition, 180 total

**Seed Formula**: seed_i = 45001 + i × 107, i=0..29

**Seed Set**: [45001, 45108, 45215, 45322, 45429, 45536, 45643, 45750, 45857, 45964, 46071, 46178, 46285, 46392, 46499, 46606, 46713, 46820, 46927, 47034, 47141, 47248, 47355, 47462, 47569, 47676, 47783, 47890, 47997, 48104]

---

## Conditions

### R1: random_5 (Baseline)
- **Action type**: random_5
- **Logic**: Uniform random over 5 actions
- **Attack ratio**: ~20% (1/5 actions)
- **Purpose**: Baseline for 5-action space, replicates DOE-011 anchor

### R2: strafe_burst_3 (Existing)
- **Action type**: strafe_burst_3
- **Logic**: 3 attacks + 1 random strafe (cycle period = 4)
- **Attack ratio**: 75%
- **Purpose**: Existing high-attack strategy, replicates DOE-011

### R3: smart_5 (Existing)
- **Action type**: smart_5
- **Logic**: 3 attacks → if kill: dodge (strafe), if no kill: turn to scan
- **Attack ratio**: ~60-70% (state-dependent)
- **Purpose**: Existing state-dependent strategy, replicates DOE-011

### R4: adaptive_5 (NEW)
- **Action type**: adaptive_5
- **Logic**: Health-responsive switching. When health declining (delta < -10 in 10 ticks): strafe+occasional attack. When health stable: burst_3 turn+attack pattern. Post-kill: brief dodge.
- **Attack ratio**: Variable (40-70% depending on state)
- **Purpose**: Tests value of health-responsive behavior in 5-action space

### R5: dodge_burst_3 (NEW)
- **Action type**: dodge_burst_3
- **Logic**: 3 attacks + 2 strafes (cycle period = 5)
- **Attack ratio**: 60%
- **Purpose**: Intermediate point on attack/strafe gradient

### R6: survival_burst (NEW)
- **Action type**: survival_burst
- **Logic**: 2 attacks + 2 strafes + 1 turn (cycle period = 5)
- **Attack ratio**: 40%
- **Purpose**: Maximum survival with minimal offense

---

## Run Order

Randomized (seed 20250225): R3, R6, R1, R4, R2, R5

---

## Response Variables

| Variable | Unit | Measurement |
|----------|------|-------------|
| kills | count | KILLCOUNT at episode end |
| kill_rate | kills/min | kills / (survival_time / 60) |
| survival_time | seconds | Time alive (total_ticks / 35) |

---

## Planned Contrasts (Bonferroni α = 0.01)

| ID | Contrast | Description |
|----|----------|-------------|
| C1 | random_5 vs all structured | Does structure help in 5-action? |
| C2 | strafe_burst_3 vs dodge_burst_3 | Effect of strafe ratio (25% vs 40%) |
| C3 | survival_burst vs strafe_burst_3 | Survival vs kill tradeoff |
| C4 | adaptive_5 vs non-adaptive mean | Value of state-dependent behavior |
| C5 | All 5-action vs DOE-011 random_5 baseline | Cross-experiment replication |

---

## Outcome Scenarios

| Outcome | Condition | Implication |
|---------|-----------|-------------|
| A | Strategies form separable tiers (p<0.01) | 5-action space enables differentiation → proceed to RAG test |
| B | Survival varies significantly but kill_rate doesn't | Strafe/attack tradeoff confirmed → multi-objective optimization needed |
| C | No strategy differentiation (null) | 5-action still too simple → consider 7-action or compound |
| D | adaptive_5 significantly better | State-dependent logic has value → RAG context accumulation may work |
| E | strafe_burst_3 dominates (DOE-011 replication) | Confirms DOE-011, no new information |

---

## Execution Instructions for research-doe-runner

1. Use defend_the_line_5action.cfg with num_actions=5
2. Set doom_skill=3 (Normal)
3. Use seed set above (identical seeds for all conditions)
4. Run 30 episodes per condition in randomized order (R3, R6, R1, R4, R2, R5)
5. Record all three response variables to DuckDB
6. Total: 180 episodes

---

## Budget

| Item | Count |
|------|-------|
| Conditions | 6 |
| Episodes per condition | 30 |
| Total episodes | 180 |
| Estimated runtime | ~60 seconds |
| Cumulative project episodes | ~5,000 |
