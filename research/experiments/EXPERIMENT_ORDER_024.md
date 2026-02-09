# EXPERIMENT_ORDER_024: L2 Meta-Strategy Selection via RAG

## Metadata
- **Experiment ID**: DOE-024
- **Hypothesis**: H-027 -- L2 RAG meta-strategy selection outperforms fixed single-strategy performance across difficulty levels
- **DOE Phase**: Phase 2 (L2 Architecture Redesign)
- **Design Type**: 4 x 3 full factorial (decision_mode x doom_skill)
- **Date Ordered**: 2026-02-09
- **Prior Art**: DOE-022 (L2 failure -- coarse tactic-to-action mapping), DOE-023 (difficulty-dependent strategy rankings), DOE-020/021 (burst_3 global optimality in 3-action space)

## Research Question

Can L2 RAG provide value as a **meta-strategy selector** (choosing which L1 strategy to execute) rather than a raw action selector (choosing individual game actions)? DOE-022 showed L2 selecting actions directly DEGRADES performance (F-049, d=1.641) because the tactic-to-action mapping is too coarse and replaces burst_3's critical periodic turning. DOE-023 showed strategy rankings CHANGE across difficulty levels (F-053, p=6.02e-04), creating an opportunity for context-dependent strategy selection.

### Background

#### The L2 Action-Level Failure (DOE-022)

DOE-022 activated L2 for the first time. Results were devastating:
- L0_L1 (burst_3): 14.73 kills
- L0_L1_L2_good: 9.57 kills (regression to L0_only level)
- Document quality irrelevant (F-050, d=0.000)

Root cause (F-051): L2 queries return tactic names (e.g., "burst_fire_sweep"), which tactic_to_action() maps almost entirely to ACTION_ATTACK. This replaces burst_3's 3-attack+1-turn cycle with constant attacking, eliminating the lateral movement that drives performance (F-010).

#### The Difficulty-Dependent Opportunity (DOE-023)

DOE-023 revealed strategy rankings vary with difficulty:
- **Easy** (doom_skill=1): adaptive_kill best (22.93 kills), burst_3 3rd (19.73 kills)
- **Normal** (doom_skill=3): random best (13.73 kills), adaptive_kill 2nd (13.43 kills), burst_3 3rd (12.17 kills)
- **Nightmare** (doom_skill=5): random best (4.97 kills), burst_3 2nd (4.43 kills), adaptive_kill 3rd (3.87 kills)

Key insight: no single strategy dominates across all difficulties. adaptive_kill excels when survival time allows its switching mechanism to activate (Easy), but degrades to L0_only level when survival is too brief (Nightmare, F-055). burst_3 is robust but not optimal at Easy.

#### The Meta-Strategy Hypothesis

Instead of L2 selecting raw actions, L2 selects which L1 strategy to DELEGATE to. Strategy documents specify a `decision.strategy` field (e.g., "burst_3" or "adaptive_kill") rather than individual tactics. L2 queries OpenSearch with game-state context tags, retrieves the most relevant strategy document, and activates the specified L1 strategy for that tick.

If L2 can learn the DOE-023 difficulty-dependent rankings from strategy documents, it should select:
- adaptive_kill in favorable conditions (high health, many kills, slow game pace)
- burst_3 in harsh conditions (low health, few kills, fast enemy pressure)

This would outperform any fixed single strategy by adapting to environmental conditions.

### Hypothesis

**H-027: L2 RAG Meta-Strategy Selection Outperforms Fixed Strategies Across Difficulty Levels**

When L2 OpenSearch queries return strategy documents specifying which L1 strategy to delegate to (meta-strategy selection), the composite agent outperforms any fixed single-strategy agent when tested across multiple difficulty levels.

**Predictions**:
1. L2_meta_select matches or exceeds fixed_burst3 overall (main effect comparison)
2. L2_meta_select advantage is largest at Easy difficulty (where strategy choice matters most, F-054)
3. Significant decision_mode x doom_skill interaction: L2_meta_select maintains high performance across all difficulties while fixed strategies degrade differently
4. L2_meta_select outperforms random_select (meta-selection is intelligent, not random switching)

## Factors

| Factor | Type | Role | Levels | Description |
|--------|------|------|--------|-------------|
| decision_mode | Categorical | Treatment | 4 | Strategy selection mechanism |
| doom_skill | Categorical | Blocking (environmental) | 3 | Game difficulty level |

### Factor 1: decision_mode (4 levels)

| Level | Label | Description | Mechanism |
|-------|-------|-------------|-----------|
| 1 | **fixed_burst3** | Always uses burst_3 strategy | Tick: 3 attacks + 1 turn (repeat). Phase 1 champion (F-039). |
| 2 | **fixed_adaptive_kill** | Always uses adaptive_kill strategy | If kills < 10: always attack. If kills >= 10: burst_3 pattern. Phase 1 kill_rate champion (F-032). |
| 3 | **L2_meta_select** | Queries OpenSearch for strategy documents; top document's `decision.strategy` field specifies which L1 strategy to delegate to | Game-state tags (health, kills, enemies_visible) -> OpenSearch query -> top document -> strategy name -> delegate to L1 strategy function. See "Meta-Strategy Document Design" below. |
| 4 | **random_select** | Randomly picks burst_3 or adaptive_kill each tick | Each tick: 50% chance burst_3, 50% chance adaptive_kill. No game-state awareness. Noise baseline for C3. |

### Factor 2: doom_skill (3 levels)

| Level | Label | VizDoom doom_skill | DOE-023 Baseline (kills) | DOE-023 Baseline (kill_rate) |
|-------|-------|--------------------|--------------------------|------------------------------|
| 1 | **Easy** | 1 | 19.69 (mean across strategies) | 42.75 |
| 2 | **Normal** | 3 | 12.23 | 42.36 |
| 3 | **Nightmare** | 5 | 4.29 | 39.92 |

### Strategy Selection Rationale

**Why burst_3 and adaptive_kill as the meta-strategy pool**:
- These are the two Pareto-optimal strategies from DOE-020 (F-038, F-039)
- burst_3: highest kills (15.40), robust across difficulties
- adaptive_kill: highest kill_rate (45.97 at Normal), best at Easy (22.93 kills)
- They have complementary strengths: burst_3 robust but suboptimal at Easy, adaptive_kill excellent at Easy but degrades at Nightmare (F-055)
- Adding more strategies to the pool (random, attack_only) would increase design complexity without adding value -- random matches burst_3 (F-035) and attack_only is inferior on all metrics (F-036)

**Why not include random as a meta-strategy option**:
- random is statistically equivalent to burst_3 on kill_rate (F-035, d=0.29 NS)
- Adding random to the meta-strategy pool would not improve the ceiling
- Two-strategy pool (burst_3, adaptive_kill) is the minimum viable test of meta-selection

## Meta-Strategy Document Design

### HIGH Quality Documents (n=30)

Derived from DOE-023 findings. Each document encodes a game-state condition and the empirically optimal strategy for that condition.

#### Document Schema

```json
{
  "doc_id": "meta_high_001",
  "situation_tags": ["multi_enemy", "low_health"],
  "decision": {
    "strategy": "burst_3",
    "rationale": "Harsh conditions favor burst_3 robustness (F-053, F-055)"
  },
  "quality": {
    "trust_score": 0.90,
    "source_experiment": "DOE-023",
    "source_finding": "F-053"
  },
  "metadata": {
    "created": "2026-02-09",
    "version": 1,
    "retired": false
  }
}
```

**CRITICAL DIFFERENCE from DOE-022**: The `decision` field contains `strategy` (a strategy name to delegate to) rather than `tactic` (an action-level instruction). This is the architectural fix for F-049.

#### Document Distribution

| Condition Tags | Strategy | n | Rationale |
|----------------|----------|---|-----------|
| low_health, multi_enemy | burst_3 | 5 | Harsh conditions -> robust strategy (F-055: adaptive_kill degrades) |
| low_health, single_enemy | burst_3 | 3 | Low survival time -> no time for adaptation |
| full_health, multi_enemy, high_kills | adaptive_kill | 5 | Favorable conditions with kills -> adaptive switching benefits |
| full_health, ammo_abundant | adaptive_kill | 5 | Resource-rich environment -> efficiency strategy |
| full_health, single_enemy | adaptive_kill | 3 | Safe environment -> maximize efficiency |
| multi_enemy, low_kills | burst_3 | 4 | Early game / high pressure -> burst robustness |
| (general fallback, no specific tags) | burst_3 | 5 | Default when uncertain -> safest option (F-039 global optimal) |

**Total**: 30 HIGH quality documents

#### Tag Derivation Logic

Mirrors DOE-022 Phase C but now maps to strategy names:

```python
def derive_situation_tags(state):
    tags = []
    if state.health < 30:
        tags.append("low_health")
    elif state.health >= 80:
        tags.append("full_health")
    if state.ammo < 10:
        tags.append("low_ammo")
    elif state.ammo >= 50:
        tags.append("ammo_abundant")
    if state.enemies_visible >= 3:
        tags.append("multi_enemy")
    elif state.enemies_visible == 1:
        tags.append("single_enemy")
    if state.kills >= 10:
        tags.append("high_kills")
    elif state.kills < 5:
        tags.append("low_kills")
    return tags
```

#### Meta-Strategy Execution Logic

```python
class L2MetaStrategyAction:
    """L2 meta-strategy selector.

    Queries OpenSearch for strategy documents.
    Top document's decision.strategy field selects which L1 strategy to delegate to.
    L1 strategies maintain their full periodic patterns (fixing F-051).
    """

    def __init__(self, opensearch_url, index_name, k=5):
        self.opensearch_url = opensearch_url
        self.index_name = index_name
        self.k = k
        # L1 strategy functions (the actual action generators)
        self.strategies = {
            "burst_3": Burst3Action(),
            "adaptive_kill": AdaptiveKillAction(),
        }
        self.current_strategy = "burst_3"  # default

    def __call__(self, state):
        # Step 1: Query OpenSearch for meta-strategy document
        tags = derive_situation_tags(state)
        if tags:
            docs = self.query_opensearch(tags)
            if docs:
                best = max(docs, key=self.score_document)
                strategy_name = best["decision"]["strategy"]
                if strategy_name in self.strategies:
                    self.current_strategy = strategy_name

        # Step 2: Delegate to selected L1 strategy
        # THIS IS THE KEY FIX: L1 patterns are PRESERVED, not replaced
        return self.strategies[self.current_strategy](state)
```

**Key architectural difference from DOE-022**:
- DOE-022: L2 query -> tactic name -> tactic_to_action() -> single action (REPLACES L1)
- DOE-024: L2 query -> strategy name -> delegate to L1 function (PRESERVES L1 patterns)

### Query Caching

To avoid querying OpenSearch every tick (35 fps = 35 queries/second), cache the meta-strategy decision:

```python
# Query OpenSearch every N ticks (not every tick)
QUERY_INTERVAL = 35  # Re-evaluate strategy once per second

def __call__(self, state):
    if state.tick % QUERY_INTERVAL == 0:
        self._update_strategy(state)
    return self.strategies[self.current_strategy](state)
```

This reduces OpenSearch load from 35 qps to 1 qps while allowing strategy switching approximately once per second.

## Design Matrix

| Run | decision_mode | doom_skill | n | Seeds |
|-----|---------------|------------|---|-------|
| R01 | fixed_burst3 | Easy (1) | 30 | [40001, ..., 42988] |
| R02 | fixed_burst3 | Normal (3) | 30 | [40001, ..., 42988] |
| R03 | fixed_burst3 | Nightmare (5) | 30 | [40001, ..., 42988] |
| R04 | fixed_adaptive_kill | Easy (1) | 30 | [40001, ..., 42988] |
| R05 | fixed_adaptive_kill | Normal (3) | 30 | [40001, ..., 42988] |
| R06 | fixed_adaptive_kill | Nightmare (5) | 30 | [40001, ..., 42988] |
| R07 | L2_meta_select | Easy (1) | 30 | [40001, ..., 42988] |
| R08 | L2_meta_select | Normal (3) | 30 | [40001, ..., 42988] |
| R09 | L2_meta_select | Nightmare (5) | 30 | [40001, ..., 42988] |
| R10 | random_select | Easy (1) | 30 | [40001, ..., 42988] |
| R11 | random_select | Normal (3) | 30 | [40001, ..., 42988] |
| R12 | random_select | Nightmare (5) | 30 | [40001, ..., 42988] |

**Total**: 4 decision_modes x 3 doom_skills x 30 episodes = 360 episodes

### Randomized Execution Order

Within each doom_skill block (blocking factor), randomize decision_mode order:

- **Easy block**: R10 (random_select) -> R04 (fixed_adaptive_kill) -> R07 (L2_meta_select) -> R01 (fixed_burst3)
- **Normal block**: R08 (L2_meta_select) -> R02 (fixed_burst3) -> R11 (random_select) -> R05 (fixed_adaptive_kill)
- **Nightmare block**: R03 (fixed_burst3) -> R12 (random_select) -> R06 (fixed_adaptive_kill) -> R09 (L2_meta_select)

Doom_skill block order: Easy -> Normal -> Nightmare (ascending difficulty for early detection of floor effects)

## Seed Set

**Formula**: seed_i = 40001 + i x 103, i = 0, 1, ..., 29
**Range**: [40001, 42988]
**Count**: 30 seeds per cell, identical across all 12 cells

**Full seed set**:
```
[40001, 40104, 40207, 40310, 40413, 40516, 40619, 40722, 40825, 40928,
 41031, 41134, 41237, 41340, 41443, 41546, 41649, 41752, 41855, 41958,
 42061, 42164, 42267, 42370, 42473, 42576, 42679, 42782, 42885, 42988]
```

**Verification**: seed_29 = 40001 + 29 x 103 = 40001 + 2987 = 42988. Correct.

### Cross-Experiment Seed Collision Check

| Experiment | Seed Range | Collision with DOE-024 [40001, 42988]? |
|-----------|------------|----------------------------------------|
| DOE-001 | [42, 2191] | NO (disjoint) |
| DOE-002 | [1337, 1830] | NO (disjoint) |
| DOE-003 | [2023, 2690] | NO (disjoint) |
| DOE-004 | [7890, 8527] | NO (disjoint) |
| DOE-005 | [2501, 3168] | NO (disjoint) |
| DOE-006 | [3501, 4342] | NO (disjoint) |
| DOE-007 | [4501, 5400] | NO (disjoint) |
| DOE-008 | [6001, 7074] | NO (disjoint) |
| DOE-009 | [8001, 9190] | NO (disjoint) |
| DOE-010 | [10001, 11248] | NO (disjoint) |
| DOE-011 | [12001, 13364] | NO (disjoint) |
| DOE-012 | [13001, 14538] | NO (disjoint) |
| DOE-013 | [14001, 15712] | NO (disjoint) |
| DOE-014 | [15001, 16770] | NO (disjoint) |
| DOE-015 | [16001, 17944] | NO (disjoint) |
| DOE-016 | [17001, 19056] | NO (disjoint) |
| DOE-017 | [18001, 20118] | NO (disjoint) |
| DOE-018 | [19001, 21284] | NO (disjoint) |
| DOE-019 | [20001, 22404] | NO (disjoint) |
| DOE-020 | [21001, 23581] | NO (disjoint) |
| DOE-021 | [23001, 38104] | NO (gap of 1897) |
| DOE-022 | [24001, 26814] | NO (disjoint) |
| DOE-023 | [25001, 27930] | NO (disjoint) |

**Verdict**: DOE-024 range [40001, 42988] is strictly above the maximum of all prior experiments (38104, DOE-021 Gen 5). Zero seed collisions guaranteed.

## Scenario Configuration

**Scenario**: defend_the_line.cfg (3-action space), same as DOE-008 through DOE-023.

```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

doom_skill is set via VizDoom API: `game.set_doom_skill(skill_level)` before each episode.

## Response Variables

### Primary
- **kills**: Total KILLCOUNT per episode (integer)
- **kill_rate**: kills / survival_time_seconds * 60 (kills per minute)

### Secondary
- **survival_time**: Seconds survived per episode (continuous)
- **l2_query_count**: Number of OpenSearch queries per episode (L2_meta_select only)
- **l2_strategy_switches**: Number of times L2 changed the active L1 strategy within an episode
- **strategy_distribution**: Proportion of ticks spent in each L1 strategy (L2_meta_select and random_select only)

### Diagnostic
- **l2_latency_p50_ms**: Median OpenSearch query latency (L2_meta_select only)
- **l2_latency_p99_ms**: P99 OpenSearch query latency (target: < 100ms)

## Statistical Analysis Plan

### Primary Analysis: Two-Way ANOVA

**Model**: kills ~ decision_mode + doom_skill + decision_mode:doom_skill

**Factors**:
- decision_mode (4 levels): fixed_burst3, fixed_adaptive_kill, L2_meta_select, random_select -- fixed effect
- doom_skill (3 levels): Easy, Normal, Nightmare -- fixed effect (blocking)
- decision_mode x doom_skill interaction

**Degrees of Freedom**:
- decision_mode: df = 3
- doom_skill: df = 2
- decision_mode x doom_skill: df = 6
- Error: df = 348 (360 - 12)
- Total: df = 359

### Key Questions (priority order)

**Q1: Does L2_meta_select outperform fixed strategies overall?**
- decision_mode main effect comparison
- If L2_meta_select marginal mean >= fixed_burst3 marginal mean: meta-selection adds value
- Expected: YES if strategy documents encode DOE-023 difficulty-dependent findings correctly

**Q2: Does L2_meta_select x doom_skill interaction differ from fixed strategies?**
- If L2_meta_select maintains high performance across all doom_skills while fixed strategies degrade: L2 provides adaptive benefit
- This is the CORE SCIENTIFIC CLAIM: meta-strategy selection adapts to environmental conditions

**Q3: Is L2_meta_select better than random strategy switching?**
- If L2_meta_select > random_select: intelligent selection (via RAG documents) outperforms random switching
- If NS: the value comes from strategy MIXING, not intelligent SELECTION

**Q4: Do DOE-023 difficulty rankings replicate?**
- Independent seed set replication of F-052, F-053
- Expected: doom_skill main effect highly significant (DOE-023: F=446.73, p=7.77e-97)

### Planned Contrasts

| Contrast | Comparison | Scientific Question | Expected | Bonferroni alpha |
|----------|------------|---------------------|----------|------------------|
| C1 | L2_meta_select vs fixed_burst3 (marginal means) | Does meta-selection beat Phase 1 champion? | L2_meta >= burst3 | 0.01 |
| C2 | L2_meta_select vs fixed_adaptive_kill (marginal means) | Does meta-selection beat runner-up? | L2_meta > adaptive_kill (especially at Nightmare) | 0.01 |
| C3 | L2_meta_select vs random_select | Is RAG-guided selection better than random switching? | L2_meta > random | 0.01 |
| C4 | Interaction: decision_mode x doom_skill | Does L2 benefit vary by difficulty? | Significant interaction | 0.01 |
| C5 | L2_meta_select at Nightmare vs fixed_adaptive_kill at Nightmare | Does L2 fix adaptive_kill's Nightmare degradation? | L2_meta > adaptive_kill at Nightmare | 0.01 |

**Bonferroni correction**: alpha = 0.05 / 5 = 0.01 for planned contrasts

### Residual Diagnostics (R100 Compliance)

1. **Normality**: Shapiro-Wilk or Anderson-Darling on residuals
2. **Equal variance**: Levene test across all 12 cells
3. **Independence**: Residuals vs run order within each doom_skill block
4. **Outlier detection**: Studentized residuals > |3|

### If Interaction IS Significant

Perform simple effects analysis:
- One-way ANOVA of decision_mode within each doom_skill level
- Compare strategy rankings per difficulty level
- Tukey HSD within each difficulty for pairwise comparisons
- Test specific prediction: L2_meta_select should be top-ranked at EVERY difficulty level

### If ANOVA Assumptions Violated

- Normality violation: Kruskal-Wallis per doom_skill + Scheirer-Ray-Hare for interaction
- Variance heterogeneity: Welch's ANOVA per doom_skill, Brown-Forsythe test
- Both: Aligned Rank Transform (ART) ANOVA

### Effect Sizes

- Partial eta-squared for all ANOVA effects
- Cohen's d for all planned contrasts
- Generalized eta-squared for cross-experiment comparison with DOE-023

### Secondary Responses

Repeat full analysis for:
- **kill_rate** (kills per minute)
- **survival_time** (seconds survived)
- **strategy_distribution** (for L2_meta_select: what proportion of ticks used burst_3 vs adaptive_kill at each difficulty?)

### Cross-Experiment Comparison

Compare DOE-024 fixed conditions to DOE-023 equivalents:

| Strategy | DOE-024 (seed 40001-42988) | DOE-023 (seed 25001-27930) | Expected |
|----------|---------------------------|---------------------------|----------|
| burst_3 x Easy | R01 | DOE-023 burst_3 Easy (19.73 kills) | d < 0.3 (replication) |
| burst_3 x Normal | R02 | DOE-023 burst_3 Normal (12.17 kills) | d < 0.3 |
| burst_3 x Nightmare | R03 | DOE-023 burst_3 Nightmare (4.43 kills) | d < 0.3 |
| adaptive_kill x Easy | R04 | DOE-023 adaptive_kill Easy (22.93 kills) | d < 0.3 |

Use independent-samples t-tests with Bonferroni correction. If d > 0.5, investigate seed-set sensitivity.

### Power Analysis

- Two-way ANOVA with 4 x 3 = 12 cells, n = 30 per cell, alpha = 0.05
- For decision_mode main effect (df = 3): Power > 0.95 for medium effect (f = 0.25) with N = 360
- For doom_skill main effect (df = 2): Power > 0.99 (DOE-023 observed f > 1.0)
- For interaction (df = 6): Power > 0.85 for medium effect
- DOE-023 observed strategy effect f = 0.35-0.45: Power > 0.99 for main effects

## Success Criteria

### Outcome A: Meta-Strategy Validated (STRONGEST)

**Condition**: L2_meta_select marginal mean >= fixed_burst3 AND L2_meta_select > random_select (p < 0.01)

**Interpretation**: L2 RAG as a meta-strategy selector provides genuine value. The RAG documents encode useful environmental knowledge, and the L2 retrieval mechanism correctly identifies which L1 strategy to use in context. The "Agent Skill = Document Quality x Scoring Accuracy" thesis is VALIDATED at the meta-strategy level.

**Publication Claim**: "RAG-guided meta-strategy selection outperforms fixed strategies by adapting to environmental conditions, achieving X% improvement over the best fixed strategy."

**Next Step**: Phase 3 -- optimize document corpus through evolutionary selection of strategy documents. Test with additional L1 strategies. Scale to more difficulty/scenario dimensions.

### Outcome B: Meta-Strategy Equivalent to Fixed (PARTIAL)

**Condition**: L2_meta_select is not significantly different from fixed_burst3 overall, but shows advantage at specific doom_skill levels (interaction significant)

**Interpretation**: Meta-strategy selection provides CONDITIONAL value -- useful in some environments but not universally. The value proposition is narrower than hoped but still scientifically interesting.

**Publication Claim**: "Context-dependent strategy selection provides environment-specific benefits, particularly in [specific difficulty level]."

**Next Step**: Investigate which environmental features L2 responds to. Expand strategy pool. Test whether human-authored documents vs learned documents differ.

### Outcome C: Random Switching Equals Meta-Selection (CONCERNING)

**Condition**: L2_meta_select and random_select are statistically equivalent (d < 0.3)

**Interpretation**: The value comes from strategy MIXING (alternating between burst_3 and adaptive_kill), not from intelligent SELECTION. RAG retrieval adds no information. The OpenSearch pipeline provides no benefit over random diversification.

**Publication Claim**: "Strategy diversity matters more than strategy selection intelligence."

**Next Step**: Test whether a simple rule-based selector (if health < X: burst_3, else: adaptive_kill) matches L2_meta_select. If yes, L2 RAG adds no value even as meta-selector.

### Outcome D: All Four Decision Modes Equivalent (NULL)

**Condition**: decision_mode main effect NOT significant (p >= 0.05)

**Interpretation**: Neither meta-strategy selection nor the choice between burst_3 and adaptive_kill matters. The 3-action space ceiling (~43 kr) applies regardless of selection mechanism.

**Publication Claim**: "In constrained action spaces, strategy selection provides no benefit -- the performance ceiling is determined by action space geometry."

**Next Step**: Pivot to action space expansion (5+ actions) combined with meta-strategy selection, or abandon meta-strategy approach entirely.

### Outcome E: Meta-Strategy DEGRADES Performance (FAILURE)

**Condition**: L2_meta_select significantly WORSE than fixed_burst3 (p < 0.01)

**Interpretation**: Meta-strategy selection introduces harmful switching overhead or incorrect strategy assignments. Strategy switching itself is costly (pattern interruption).

**Publication Claim**: None (negative result to document and learn from).

**Next Step**: Investigate switching cost (F-051 pattern disruption hypothesis). Test whether L2 switching frequency correlates with performance loss.

## Infrastructure Requirements

### OpenSearch Setup

```bash
# Verify OpenSearch container health
curl -sf http://localhost:9200/_cluster/health

# Create meta-strategy index
curl -X PUT http://localhost:9200/strategies_meta -H 'Content-Type: application/json' -d '{
  "mappings": {
    "properties": {
      "doc_id": {"type": "keyword"},
      "situation_tags": {"type": "keyword"},
      "decision.strategy": {"type": "keyword"},
      "decision.rationale": {"type": "text"},
      "quality.trust_score": {"type": "float"},
      "quality.source_experiment": {"type": "keyword"},
      "quality.source_finding": {"type": "keyword"},
      "metadata.created": {"type": "date"},
      "metadata.version": {"type": "integer"},
      "metadata.retired": {"type": "boolean"}
    }
  }
}'

# Bulk index 30 meta-strategy documents
curl -X POST http://localhost:9200/strategies_meta/_bulk \
  -H 'Content-Type: application/x-ndjson' \
  --data-binary @meta_strategy_docs.ndjson

# Verify
curl http://localhost:9200/strategies_meta/_count
```

### New Action Functions Required

| Function | Status | Implementation |
|----------|--------|----------------|
| Burst3Action | EXISTS | action_functions.py (from DOE-010+) |
| AdaptiveKillAction | EXISTS | action_functions.py (from DOE-018+) |
| L2MetaStrategyAction | NEW | See "Meta-Strategy Execution Logic" above |
| RandomSelectAction | NEW | Simple: each tick randomly choose Burst3Action or AdaptiveKillAction |
| L0OnlyAction | NOT NEEDED | Not included in DOE-024 design (well-established baseline) |

### RandomSelectAction Implementation

```python
class RandomSelectAction:
    """Random strategy selector (noise baseline).

    Each tick, randomly selects burst_3 or adaptive_kill
    with equal probability. No game-state awareness.
    """

    def __init__(self, rng_seed=None):
        self.strategies = {
            "burst_3": Burst3Action(),
            "adaptive_kill": AdaptiveKillAction(),
        }
        self.rng = random.Random(rng_seed)

    def __call__(self, state):
        strategy = self.rng.choice(["burst_3", "adaptive_kill"])
        return self.strategies[strategy](state)
```

## Risk Assessment

### Risk 1: L2 Query Latency Exceeds Budget (MEDIUM)

**Concern**: 1 query/second at 30 concurrent episodes may stress OpenSearch.

**Mitigation**:
1. Query interval = 35 ticks (1 qps) reduces load to manageable level
2. If latency > 100ms: increase query interval to 70 ticks (0.5 qps)
3. Monitor l2_latency_p99_ms throughout execution
4. Fallback: if OpenSearch down, L2_meta_select defaults to burst_3

### Risk 2: Strategy Switching Cost (HIGH)

**Concern**: Switching from burst_3 to adaptive_kill mid-pattern may disrupt the 3-attack+1-turn cycle, causing temporary performance loss. If switching is frequent enough, this overhead may eliminate any selection benefit.

**Mitigation**:
1. Query interval (35 ticks = 1s) limits switching frequency to max 1 switch/second
2. Monitor l2_strategy_switches metric
3. If switching > 10/episode correlates with poor performance, increase query interval
4. Both strategies share common fallback (attack), so switches during attack phase are seamless

### Risk 3: Document Tags Never Match (MEDIUM)

**Concern**: derive_situation_tags() may produce tags that never match any document, causing L2_meta_select to always default to burst_3 (functionally identical to fixed_burst3).

**Mitigation**:
1. Include 5 general fallback documents with no specific tags (match everything)
2. Monitor l2_query_count -- if zero for most episodes, tag coverage is insufficient
3. Pre-validate: run 5-episode pilot, check hit rate > 50%
4. If hit rate < 20%, expand tag vocabulary in documents

### Risk 4: Random_Select Per-Tick Switching Creates Incoherent Behavior (LOW)

**Concern**: Switching strategy every tick means burst_3's 3-attack+1-turn cycle never completes. random_select may degenerate to approximately random action selection.

**Assessment**: This is EXPECTED and ACCEPTABLE. random_select is the noise baseline. If it degenerates to random-like performance (~43 kr from F-035), that validates it as the correct baseline. If L2_meta_select (which switches at most 1x/second, preserving L1 patterns within each second) outperforms random_select (which switches every tick, disrupting patterns), the comparison demonstrates that pattern preservation matters.

### Risk 5: DOE-023 Rankings Don't Replicate (LOW)

**Concern**: Different seed set may produce different difficulty-dependent rankings.

**Mitigation**:
1. Cross-experiment comparison (see Statistical Analysis Plan) will detect non-replication
2. If rankings don't replicate, the meta-strategy documents are based on incorrect assumptions
3. DOE-023 had n=30/cell with highly significant effects (p < 0.001); non-replication unlikely

## Data Collection

### Per-Episode Metrics (DuckDB)

```sql
CREATE TABLE IF NOT EXISTS doe_024 (
  episode_id INTEGER,
  decision_mode TEXT,
  doom_skill INTEGER,
  seed INTEGER,
  kills INTEGER,
  health_remaining INTEGER,
  ammo_remaining INTEGER,
  survival_time_seconds REAL,
  kill_rate REAL,
  l2_query_count INTEGER DEFAULT 0,
  l2_strategy_switches INTEGER DEFAULT 0,
  burst3_tick_pct REAL DEFAULT NULL,
  adaptive_kill_tick_pct REAL DEFAULT NULL,
  l2_latency_p50_ms REAL DEFAULT NULL,
  l2_latency_p99_ms REAL DEFAULT NULL,
  PRIMARY KEY (decision_mode, doom_skill, seed)
);
```

## Execution Checklist

### Phase A: Meta-Strategy Document Generation
- [ ] Create 30 HIGH quality meta-strategy documents (JSON format)
- [ ] Validate document schema (decision.strategy must be "burst_3" or "adaptive_kill")
- [ ] Verify tag distribution covers common game states
- [ ] Store documents in research/experiments/doe-024-data/

### Phase B: OpenSearch Setup
- [ ] Verify OpenSearch container running
- [ ] Create strategies_meta index with correct mapping
- [ ] Bulk index 30 documents
- [ ] Verify index count = 30
- [ ] Test query: `curl http://localhost:9200/strategies_meta/_search?q=situation_tags:multi_enemy`
- [ ] Measure query latency (target: < 50ms)

### Phase C: Action Function Implementation
- [ ] Implement L2MetaStrategyAction class (meta-strategy selector)
- [ ] Implement RandomSelectAction class (noise baseline)
- [ ] Unit test: derive_situation_tags() produces expected tags for known states
- [ ] Unit test: L2MetaStrategyAction delegates to correct L1 strategy
- [ ] Unit test: RandomSelectAction produces approximately 50/50 split
- [ ] Integration test: L2MetaStrategyAction queries OpenSearch and returns correct strategy
- [ ] Latency test: end-to-end L2 meta-query < 100ms
- [ ] Fallback test: L2 defaults to burst_3 when no documents match

### Phase D: Pilot Study
- [ ] Run 5-episode pilot for L2_meta_select at Normal difficulty
- [ ] Verify l2_query_count > 0 (queries are reaching OpenSearch)
- [ ] Verify l2_strategy_switches > 0 (strategy switching actually occurs)
- [ ] Verify burst3_tick_pct and adaptive_kill_tick_pct are both > 0
- [ ] Verify performance is plausible (not degenerate like DOE-022)
- [ ] If pilot fails, debug tag coverage and document matching

### Phase E: DOE-024 Execution
- [ ] Seed set generated and logged (30 seeds, formula verified)
- [ ] All 4 action functions implemented and tested
- [ ] DuckDB experiment table created
- [ ] Execute Easy block (R10, R04, R07, R01) -- 120 episodes
- [ ] Execute Normal block (R08, R02, R11, R05) -- 120 episodes
- [ ] Execute Nightmare block (R03, R12, R06, R09) -- 120 episodes
- [ ] Verify 360 total episodes recorded
- [ ] Data quality check: no missing values, plausible ranges
- [ ] Record l2 diagnostic metrics for R07, R08, R09

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 40001 + i x 103, i=0..29 |
| No seed collisions | YES: [40001, 42988] above all prior maxima (38104) |
| n >= 30 per condition | YES: 30 episodes per cell, 12 cells, 360 total |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, variance, independence per R100 |
| Effect sizes | PLANNED: partial eta-squared, Cohen's d |
| Seeds identical across conditions | YES: same 30 seeds for all 12 cells |
| Power adequate | YES: N=360 provides >0.95 power for medium effects |

## Audit Trail

| Document | Status | Owner |
|----------|--------|-------|
| H-027 in HYPOTHESIS_BACKLOG.md | ACTIVE | research-pi |
| EXPERIMENT_ORDER_024.md | ORDERED | research-pi |
| EXPERIMENT_REPORT_024.md | PENDING | research-analyst |
| FINDINGS.md update | PENDING | research-pi |
| RESEARCH_LOG.md update | PENDING | research-pi |

## Status

**ORDERED** -- Requires Phases A-C infrastructure setup before Phase E execution.

### Dependencies
- OpenSearch container running and healthy
- Meta-strategy document corpus generated (Phase A)
- Documents indexed in OpenSearch (Phase B)
- L2MetaStrategyAction and RandomSelectAction implemented (Phase C)
- Existing Burst3Action and AdaptiveKillAction available (action_functions.py)
- VizDoom doom_skill parameter confirmed working (validated in DOE-023)
