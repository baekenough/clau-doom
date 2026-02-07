# S2-01: Evaluation Baselines Definition

> **Session**: S2 (Research Design Reinforcement)
> **Priority**: RED critical
> **Dependencies**: None (S1-04 results beneficial if available)
> **Status**: COMPLETE

---

## Purpose

The current design includes metrics (kill_rate, survival_time, etc.) but lacks comparison anchors. Before entering the experimental phase, we define three baselines to objectively evaluate clau-doom agent performance. Without baselines, any reported number is meaningless — we need a floor (Random), a mid-point (Rule-Only), and an external reference (RL).

---

## Baseline 1: Random Agent

### Behavioral Specification

**Definition**: At each game tick, the agent selects an action uniformly at random from the available action space.

**Implementation**:
```rust
// Pseudo-code for Random Agent decision loop
fn decide(state: &GameState) -> Action {
    let actions = Action::all_available(state);
    actions[rng.gen_range(0..actions.len())]
}
```

**Exact Configuration**:
- Decision hierarchy: NONE (all levels disabled)
- Level 0 (MD rules): DISABLED — no hardcoded rules loaded
- Level 1 (DuckDB cache): DISABLED — no local experience queries
- Level 2 (OpenSearch kNN): DISABLED — no strategy retrieval
- Level 3 (Claude async): DISABLED — no LLM retrospection
- Action space: All VizDoom discrete actions for the scenario (MOVE_FORWARD, MOVE_BACKWARD, MOVE_LEFT, MOVE_RIGHT, TURN_LEFT, TURN_RIGHT, ATTACK, USE)
- Selection method: Uniform random with fixed seed per episode
- No state memory between ticks — each tick is independent

**Agent MD File (DOOM_PLAYER_BASELINE_RANDOM.MD)**:
```markdown
# DOOM_PLAYER_BASELINE_RANDOM.MD

## Identity
- Generation: 0 (baseline)
- Parent: none
- Mutation: none

## Strategy Profile
- play_style: random
- retreat_threshold: none
- ammo_conservation: none
- exploration_priority: none

## Learned Rules
(empty — no rules)

## Active Experiments
(not applicable — baseline only)
```

**Purpose**: Absolute performance floor. Any agent with intentional behavior must exceed this. Also validates that the measurement framework itself works correctly — if a strategy agent cannot beat random, the framework has a bug.

**Expected Performance** (VizDoom Defend-the-Center):
- survival_time: 10-30 seconds (dies quickly from random movement)
- kills: 0-2 per episode (accidental hits only)
- damage_taken: maximum (no evasion behavior)
- ammo_efficiency: < 0.05 (nearly all shots miss)
- exploration_coverage: 0.05-0.15 (random walk covers little area)

---

## Baseline 2: Rule-Only Agent (Level 0 Only)

### Behavioral Specification

**Definition**: The agent uses ONLY the MD hardcoded rules (Level 0 of the decision hierarchy). OpenSearch kNN search (Level 2) and DuckDB cache (Level 1) are disabled. This isolates the contribution of the RAG experience accumulation system.

**Implementation**:
```rust
// Pseudo-code for Rule-Only Agent
fn decide(state: &GameState) -> Action {
    // Level 0 ONLY — MD hardcoded rules
    if let Some(action) = match_md_rules(state, &self.md_rules) {
        return action;
    }
    // Fallback: default action (move forward) when no rule matches
    Action::MoveForward
}
```

**Exact Configuration**:
- Decision hierarchy: Level 0 ONLY
- Level 0 (MD rules): ENABLED — standard learned rules from a Generation-1 agent
- Level 1 (DuckDB cache): DISABLED — `skip_duckdb_lookup = true`
- Level 2 (OpenSearch kNN): DISABLED — `skip_opensearch_query = true`
- Level 3 (Claude async): DISABLED — no inter-episode learning
- No strategy document retrieval — agent relies solely on its MD file rules
- No experience accumulation — performance is static across episodes
- Fallback behavior when no rule matches: move forward (deterministic)

**Hardcoded Rule Set** (representative Generation-1 rules):
```markdown
## Learned Rules
- If enemy_visible AND distance < 300: ATTACK with current weapon
- If enemy_visible AND distance >= 300: MOVE_FORWARD toward enemy
- If health < 30%: prioritize health item search (MOVE toward nearest health)
- If ammo_current_weapon == 0: switch weapon
- If wall_ahead AND distance < 50: TURN_LEFT or TURN_RIGHT (alternating)
- If no_enemy_visible: MOVE_FORWARD (explore)
- If damage_direction detected: TURN toward damage source
```

**Rule Coverage Tracking**:
For every tick, record which rule fired (or "no_match" if fallback was used). This produces a rule_match_rate metric:
```
rule_match_rate = ticks_with_rule_match / total_ticks
```
This metric quantifies how much of gameplay the MD rules actually cover.

**Agent MD File (DOOM_PLAYER_BASELINE_RULEONLY.MD)**:
```markdown
# DOOM_PLAYER_BASELINE_RULEONLY.MD

## Identity
- Generation: 1 (baseline, frozen)
- Parent: none
- Mutation: none

## Strategy Profile
- play_style: reactive
- retreat_threshold: health < 30%
- ammo_conservation: none (not modeled)
- exploration_priority: low (move forward only)

## Learned Rules
- enemy_visible AND distance < 300 -> ATTACK
- enemy_visible AND distance >= 300 -> MOVE_FORWARD
- health < 30% -> seek health item
- ammo == 0 -> switch weapon
- wall_ahead -> turn
- no_enemy_visible -> MOVE_FORWARD
- damage_direction -> turn to face
```

**Purpose**: Measures the pure contribution of RAG experience accumulation. The delta between Rule-Only and Full Agent = the value added by OpenSearch document retrieval + DuckDB caching.

**Expected Performance** (VizDoom Defend-the-Center):
- survival_time: 45-90 seconds (basic evasion from rules)
- kills: 3-8 per episode (shoots when enemy visible, but no tactical depth)
- damage_taken: moderate (reactive only, no anticipation)
- ammo_efficiency: 0.15-0.30 (fires at enemies but no aim optimization)
- exploration_coverage: 0.10-0.25 (mostly forward movement)
- rule_match_rate: estimated 0.40-0.60 (many game states lack matching rules)

---

## Baseline 3: RL Reference Agent

### Behavioral Specification

**Definition**: A Deep Reinforcement Learning agent trained on the same VizDoom scenario, serving as an external performance reference point. This establishes where clau-doom sits relative to traditional approaches.

**Two-Track Approach**:

#### Track A: Literature Reference (Primary)
Collect reported performance numbers from published DRL results on VizDoom scenarios.

**Key References**:
| Source | Method | Scenario | Reported Performance |
|--------|--------|----------|---------------------|
| Kempka et al. (2016) | DQN | Defend-the-Center | ~10 kills/episode after 500K steps |
| Dosovitskiy & Koltun (2017) | Direct future prediction | Navigate/Gather | Navigation reward convergence |
| Lample & Chaplot (2017) | DRQN + game features | Deathmatch | ~50 frags/10min (full features) |
| Wu & Tian (2017) | A3C | Defend-the-Center | ~15 kills/episode |
| VizDoom Competition 2016-2018 winners | Various DRL | Deathmatch | Top performers baseline |

**Scenario Matching Requirements**:
- MUST use identical VizDoom scenario (map, enemy types, available weapons)
- MUST report comparable metrics (kills or survival time at minimum)
- If scenario differs, document differences and note comparison limitations
- Prefer results that include variance/CI, not just means

#### Track B: In-House PPO Reference (Secondary)
Train a simple PPO agent as a controlled reference if literature scenarios do not match exactly.

**PPO Configuration**:
```yaml
algorithm: PPO (Proximal Policy Optimization)
framework: stable-baselines3
environment: VizDoom (same .cfg as clau-doom experiments)
observation: screen_buffer (160x120, grayscale)
action_space: discrete (same actions as clau-doom agents)
training:
  total_timesteps: 2_000_000
  learning_rate: 0.00025
  n_steps: 2048
  batch_size: 64
  n_epochs: 4
  gamma: 0.99
  gae_lambda: 0.95
  clip_range: 0.2
  vf_coef: 0.5
  ent_coef: 0.01
seeds: [42, 1337, 2023]  # 3 independent training runs
evaluation:
  episodes_per_seed: 100  # 300 total evaluation episodes
  deterministic: true
```

**Purpose**: Establishes the RL ceiling for comparison. If clau-doom exceeds PPO performance, the RAG approach demonstrates competitive advantage. If not, we quantify the gap and analyze which aspects of gameplay RAG handles better or worse.

**Expected Performance** (VizDoom Defend-the-Center, PPO after 2M steps):
- survival_time: 90-180 seconds
- kills: 8-15 per episode
- damage_taken: low-moderate (learned evasion)
- ammo_efficiency: 0.30-0.50 (learned aim)
- exploration_coverage: variable (reward-dependent)

---

## Measurement Framework

### Common Metrics (All Baselines, Identical Criteria)

| Metric | Description | Unit | Collection Method |
|--------|-------------|------|-------------------|
| survival_time | Time alive per episode | seconds (game ticks / 35) | DuckDB: episodes.survival_time |
| kills | Enemy kills per episode | integer | DuckDB: episodes.kills |
| damage_dealt | Total damage inflicted per episode | HP | DuckDB: episodes.damage_dealt |
| damage_taken | Total damage received per episode | HP | DuckDB: episodes.damage_taken |
| ammo_efficiency | hits / shots_fired | ratio [0,1] | DuckDB: episodes.hits / episodes.shots_fired |
| exploration_coverage | Fraction of map cells visited | ratio [0,1] | DuckDB: episodes.cells_visited / map.total_cells |
| encounter_success_rate | Encounters won / total encounters | ratio [0,1] | DuckDB: COUNT(outcome='win') / COUNT(*) from encounters |

### Derived Metrics

| Metric | Formula | Purpose |
|--------|---------|---------|
| kill_rate | kills / survival_time_minutes | Kills per minute (normalizes for survival) |
| damage_ratio | damage_dealt / damage_taken | Offensive-to-defensive efficiency |
| decision_latency_p99 | P99 of per-tick decision time | Ensures all baselines meet <100ms constraint |

### Data Collection Requirements

- All metrics recorded per-episode in DuckDB
- Encounter-level data captured for Rule-Only and Full Agent (encounter_success_rate)
- Random Agent: no encounter-level data (no meaningful encounter detection)
- RL Agent (Track B): metrics collected via VizDoom API, stored in same DuckDB schema
- RL Agent (Track A): literature values stored in `baselines_literature` reference table

---

## Statistical Comparison Methods

### Primary Test: Welch's t-test (Unequal Variances)

Used for pairwise comparisons between each baseline and the full clau-doom agent.

```
Comparisons:
  1. Full Agent vs. Random Agent
  2. Full Agent vs. Rule-Only Agent
  3. Full Agent vs. RL Reference Agent
  4. Rule-Only Agent vs. Random Agent
  5. RL Reference Agent vs. Rule-Only Agent
```

**Parameters**:
- Significance level: alpha = 0.05
- Alternative: two-sided (no directional assumption enforced, even if expected)
- Degrees of freedom: Welch-Satterthwaite approximation

**Reporting Format**:
```
[STAT:t] t({df}) = {value}
[STAT:p] p = {value}
[STAT:ci] 95% CI for mean difference: [{lower}, {upper}]
[STAT:effect_size] Cohen's d = {value}
```

### Non-Parametric Fallback: Mann-Whitney U Test

If normality assumption fails (Anderson-Darling p < 0.05 on residuals):
- Mann-Whitney U test replaces Welch's t-test
- Report: U statistic, p-value, rank-biserial correlation (effect size)

### Effect Size: Cohen's d

| d Value | Interpretation |
|---------|---------------|
| < 0.20 | Negligible |
| 0.20 - 0.49 | Small |
| 0.50 - 0.79 | Medium |
| >= 0.80 | Large |

### Multiple Comparison Correction

With 5 pairwise comparisons across 7 metrics = 35 tests:
- Apply Holm-Bonferroni correction to control family-wise error rate
- Report both raw p-values and adjusted p-values
- A finding is significant only if adjusted p < 0.05

### Confidence Intervals

All mean differences reported with 95% CI:
```
mean_diff = mean_fullAgent - mean_baseline
CI_95 = mean_diff +/- t_{alpha/2, df} * SE_diff
```

---

## Sample Size and Power Analysis

### Target Effect Size

We want to detect at least a medium effect (Cohen's d >= 0.50) between Full Agent and Rule-Only Agent, as this represents a practically meaningful improvement from RAG.

### Power Analysis

```
Parameters:
  alpha = 0.05 (two-sided)
  power = 0.80 (1 - beta)
  effect_size = 0.50 (Cohen's d, medium)

Required sample size per group (Welch's t-test):
  n = (z_{alpha/2} + z_{beta})^2 * 2 * sigma^2 / delta^2
  n approx 64 per group

Rounding up for safety: n = 70 episodes per group
```

### Recommended Sample Sizes

| Comparison | Minimum n/group | Rationale |
|------------|----------------|-----------|
| Full vs. Random | 30 | Expected large effect (d > 1.0), lower n sufficient |
| Full vs. Rule-Only | 70 | Target medium effect (d = 0.50), primary comparison |
| Full vs. RL Reference | 70 | Unknown effect size, need adequate power |
| Rule-Only vs. Random | 30 | Expected large effect |

**Seed Set Requirements**:
- All groups use IDENTICAL seed sets (same map layouts, enemy spawns)
- Minimum 70 seeds per comparison (can reuse seeds across comparisons)
- Master seed set: 70 seeds, shared across all baselines
- Seeds stored in DuckDB `seed_sets` table and in EXPERIMENT_ORDER document

**Master Seed Set (n=70)**:
```
[42, 1337, 2023, 7890, 9999, 1111, 5555, 8888, 3333, 6666,
 1234, 5678, 9012, 3456, 7891, 2345, 6789, 1011, 1213, 1415,
 1617, 1819, 2021, 2223, 2425, 2627, 2829, 3031, 3233, 3435,
 3637, 3839, 4041, 4243, 4445, 4647, 4849, 5051, 5253, 5455,
 5657, 5859, 6061, 6263, 6465, 6667, 6869, 7071, 7273, 7475,
 7677, 7879, 8081, 8283, 8485, 8687, 8889, 9091, 9293, 9495,
 9697, 9899, 10001, 10003, 10005, 10007, 10009, 10011, 10013, 10015]
```

### Adaptive Stopping Rule

After 30 episodes, perform interim power analysis:
- If observed effect d > 1.0 with p < 0.01: may stop early (overwhelming effect)
- If observed effect d < 0.20: consider extending to n = 100 (underpowered for small effects)
- Otherwise: continue to planned n = 70

---

## DuckDB Schema Additions

### Baseline Type Column

> **Note**: The core per-episode table is `experiments` (as defined in 03-EXPERIMENT.md).
> S2-01 adds columns to the `experiments` table. The `decision_level` column on `encounters`
> is shared with S2-02 (Ablation design) — only one ALTER is needed.

```sql
-- Add baseline_type to experiments table
ALTER TABLE experiments ADD COLUMN baseline_type VARCHAR DEFAULT 'full_agent';
-- Values: 'random', 'rule_only', 'full_agent', 'rl_ppo', 'rl_literature'

-- Add rule_match tracking for Rule-Only baseline
ALTER TABLE experiments ADD COLUMN rule_match_rate DOUBLE;
-- Fraction of ticks where an MD rule matched (NULL for non-rule-only agents)

-- Add decision_level tracking per encounter (for Rule-Only vs Full comparison)
-- NOTE: Also used by S2-02 ablation studies. Define once, use in both contexts.
ALTER TABLE encounters ADD COLUMN decision_level INT;
-- 0: MD rule, 1: DuckDB cache, 2: OpenSearch kNN, NULL: random/RL
```

### Baseline Comparison View

```sql
CREATE VIEW baseline_comparison AS
SELECT
    baseline_type,
    COUNT(*) as n_episodes,
    AVG(survival_time) as mean_survival,
    STDDEV(survival_time) as sd_survival,
    AVG(kill_rate) as mean_kill_rate,
    STDDEV(kill_rate) as sd_kill_rate,
    AVG(damage_dealt) as mean_damage_dealt,
    STDDEV(damage_dealt) as sd_damage_dealt,
    AVG(damage_taken) as mean_damage_taken,
    STDDEV(damage_taken) as sd_damage_taken,
    AVG(ammo_efficiency) as mean_ammo_eff,
    STDDEV(ammo_efficiency) as sd_ammo_eff,
    AVG(CAST(rooms_visited AS DOUBLE) / total_rooms) as mean_exploration,
    STDDEV(CAST(rooms_visited AS DOUBLE) / total_rooms) as sd_exploration
FROM experiments
WHERE experiment_id = '{baseline_experiment_id}'
GROUP BY baseline_type;
```

### Literature Reference Table

```sql
CREATE TABLE baselines_literature (
    source_id VARCHAR PRIMARY KEY,
    authors VARCHAR,
    year INT,
    method VARCHAR,
    scenario VARCHAR,
    metric_name VARCHAR,
    metric_value DOUBLE,
    metric_sd DOUBLE,
    sample_size INT,
    notes VARCHAR
);
```

### Pairwise Comparison Results Table

```sql
CREATE TABLE baseline_pairwise_results (
    comparison_id VARCHAR PRIMARY KEY,
    group_a VARCHAR,
    group_b VARCHAR,
    metric VARCHAR,
    mean_diff DOUBLE,
    ci_lower DOUBLE,
    ci_upper DOUBLE,
    test_statistic DOUBLE,
    p_value_raw DOUBLE,
    p_value_adjusted DOUBLE,
    effect_size_d DOUBLE,
    test_type VARCHAR,  -- 'welch_t' or 'mann_whitney_u'
    n_a INT,
    n_b INT,
    significant BOOLEAN  -- adjusted p < 0.05
);
```

---

## Execution Plan

### Phase 1: Random Agent Baseline (estimated: 1-2 hours)
1. Create DOOM_PLAYER_BASELINE_RANDOM.MD with empty rules
2. Disable all decision levels in Rust agent config
3. Run 70 episodes with master seed set
4. Record all metrics to DuckDB with baseline_type = 'random'

### Phase 2: Rule-Only Agent Baseline (estimated: 2-3 hours)
1. Create DOOM_PLAYER_BASELINE_RULEONLY.MD with Generation-1 rules
2. Disable Level 1 (DuckDB) and Level 2 (OpenSearch) in config
3. Enable rule_match_rate tracking
4. Run 70 episodes with master seed set
5. Record all metrics with baseline_type = 'rule_only'

### Phase 3: RL Reference — Track A (estimated: 1 day literature review)
1. Collect published results from VizDoom DRL literature
2. Map to our metric framework where possible
3. Document scenario differences and comparison limitations
4. Populate baselines_literature table

### Phase 4: RL Reference — Track B (estimated: 1-2 days training)
1. Set up stable-baselines3 PPO training environment
2. Train with 3 seeds (42, 1337, 2023) for 2M timesteps each
3. Evaluate each trained model on 100 episodes with master seed set (subset of 70)
4. Record metrics with baseline_type = 'rl_ppo'

### Phase 5: Statistical Comparison (estimated: 2-3 hours)
1. Run pairwise Welch's t-tests (or Mann-Whitney U) for all comparisons
2. Compute Cohen's d and 95% CIs
3. Apply Holm-Bonferroni correction
4. Generate comparison table and visualization
5. Write EXPERIMENT_REPORT for baseline comparison

---

## Visualization Requirements

### Baseline Comparison Plot (Primary)
- Box plot with overlaid individual points for each metric
- X-axis: baseline_type (Random, Rule-Only, Full Agent, RL-PPO)
- Y-axis: metric value
- Include mean marker and 95% CI error bars
- One subplot per metric (2x3 grid)

### Performance Radar Chart
- One polygon per baseline type
- Axes: survival_time, kills, ammo_efficiency, exploration_coverage, encounter_success_rate
- Normalized to [0, 1] range for visual comparison

### Decision Level Utilization (Rule-Only vs Full Agent)
- Stacked bar chart showing fraction of decisions at each level (L0, L1, L2)
- Compares Rule-Only (100% L0) with Full Agent (L0 + L1 + L2 distribution)

---

## Contingency Plans

### If Random Agent performs unexpectedly well
- Verify action space is correctly configured (no hidden bias)
- Check seed implementation (truly uniform random, not pseudo-strategic)
- If confirmed: the scenario may be too easy; switch to harder scenario

### If Rule-Only Agent matches Full Agent
- Core assumption (RAG adds value) is challenged
- Investigate: Are the rules comprehensive enough to cover most situations?
- Check rule_match_rate: If > 0.90, rules may be sufficient for this scenario
- Escalate to more complex scenarios (larger maps, more enemy types)
- This finding itself is publishable (negative result)

### If RL Agent significantly outperforms Full Agent
- Expected initially (RL has end-to-end optimization advantage)
- Quantify the gap by metric
- Identify which gameplay aspects RAG handles better (interpretability, adaptation speed)
- Plan generation-over-generation learning curve comparison

### If metrics show high variance
- Increase sample size beyond 70 (up to 150 episodes)
- Add blocking by map region or enemy density
- Consider episode-level covariates in ANCOVA model

---

## Completion Criteria

- [x] Baseline 1 (Random) spec finalized with exact behavioral definition
- [x] Baseline 2 (Rule-Only) spec finalized with RAG disable method and rule set
- [x] Baseline 3 (RL) dual-track approach defined (literature + PPO)
- [x] Comparison statistics defined (Welch's t, Cohen's d, 95% CI, Holm-Bonferroni)
- [x] DuckDB schema additions specified (baseline_type, rule_match_rate, comparison views)
- [x] Sample sizes justified via power analysis (n=70 for primary comparisons)
- [x] Seed set defined (master set of 70 seeds)
- [x] Execution plan with estimated timelines
- [x] Contingency plans for unexpected outcomes
- [x] Lead review complete
