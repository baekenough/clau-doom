# EXPERIMENT_ORDER_022: L2 RAG Pipeline Activation — Strategy Document kNN Retrieval

## Metadata
- **Experiment ID**: DOE-022
- **Hypothesis**: H-025 — L2 kNN strategy retrieval provides performance improvement over L0+L1 baseline
- **DOE Phase**: Phase 1 (L2 activation, first RAG pipeline test)
- **Design Type**: One-way completely randomized design (4 levels)
- **Date Ordered**: 2026-02-09
- **Prerequisite**: Phases A-C infrastructure validated before Phase D execution

## Research Question

Does activating the L2 OpenSearch kNN strategy retrieval layer improve agent performance on defend_the_line, and does strategy document quality matter?

### Background

The clau-doom architecture defines a 3-level decision cascade:
```
Level 0 (L0): Hardcoded reflex rules in Rust — < 1ms
Level 1 (L1): DuckDB episode cache — < 10ms
Level 2 (L2): OpenSearch kNN strategy documents — < 100ms target
```

DOE-001 through DOE-020 have validated L0 and L1 behavior extensively. Key findings:

- **F-010**: L0_only significantly inferior on defend_the_line (p=0.000555, d=0.89-1.13)
- **F-012**: defend_the_line is the discriminating scenario (eta2=0.127 vs 0.042)
- **F-013/F-014/F-015**: memory_weight and strength_weight have NO effect in real VizDoom (all p>0.10)
- **F-035**: adaptive_kill, burst_3, and random form statistically equivalent top tier (43-47 kr)

**The L2 layer has NEVER been tested with real strategy documents.** The Rust `RagClient` (agent-core/src/rag/mod.rs) is implemented and the cascade waterfall (cascade.rs lines 155-165) is functional, but:
1. No strategy documents exist in OpenSearch
2. No embedding pipeline has been executed
3. The L2 query path has never fired in a real experiment

DOE-022 is the FIRST experiment to activate and test the L2 layer — the core RAG innovation of the clau-doom project.

### Hypothesis

**H-025: L2 kNN Strategy Retrieval Provides Performance Improvement**

When the L2 OpenSearch kNN layer is populated with curated strategy documents derived from successful episode data:
1. L0+L1+L2_good will outperform L0+L1 on kill_rate (the RAG premise)
2. L0+L1+L2_good will outperform L0+L1+L2_random (document quality matters)
3. L0+L1 will outperform L0_only (replication of F-010, DOE-008)

If H-025.1 holds: RAG approach validated → Phase 2 document optimization
If H-025.2 holds: curation pipeline matters → invest in document quality
If neither holds: L2 provides no value → architectural reconsideration

### Related Hypotheses

- **H-005** (MEDIUM PRIORITY, queued since 2026-02-07): Strategy document quality affects agent performance via L2 layer. DOE-022 directly tests this.
- **H-001** (ADOPTED, F-001): Full RAG agent dramatically outperforms random — tested with mock data, needs real L2 validation.
- **F-002** (INVALIDATED): Full agent vs rule-only showed no difference at default parameters. DOE-022 uses curated strategy documents, not empty L2.

## Infrastructure Prerequisites (Phases A-C)

### Phase A: Strategy Document Generation

**Objective**: Create strategy document corpus from DOE-020 episode analysis.

**Inputs**: DOE-020 episode logs (150 episodes across 5 strategies)

**Outputs**: 50-100 strategy documents in two quality tiers:

#### HIGH Quality Documents (curated, n=50)
Source: LLM analysis of burst_3 and adaptive_kill episode data (top performers from DOE-020)
Content per document:
```json
{
  "doc_id": "strat_high_001",
  "situation_tags": ["multi_enemy", "ammo_abundant", "full_health"],
  "decision": {
    "tactic": "burst_fire_sweep",
    "weapon": "pistol",
    "positioning": "lateral_sweep"
  },
  "quality": {
    "trust_score": 0.85,
    "source_strategy": "burst_3",
    "source_experiment": "DOE-020",
    "source_episodes": 30,
    "mean_kills": 15.40
  },
  "metadata": {
    "created": "2026-02-09",
    "version": 1,
    "retired": false
  }
}
```

Document types for HIGH quality:
1. **Engagement patterns** (n=15): When to attack, burst timing, fire rate
2. **Positioning heuristics** (n=15): Lateral movement patterns, sweep directions
3. **State-response rules** (n=10): Health-dependent tactics, kill-count-dependent switching
4. **Combined tactics** (n=10): Multi-factor situation-action mappings

#### LOW/RANDOM Quality Documents (control, n=50)
Source: Randomly generated or irrelevant strategy advice
Content: Same JSON schema but with:
- Irrelevant situation tags (mismatched to actual gameplay)
- Random/unhelpful tactics (e.g., "retreat" when full health and ammo)
- Low trust scores (0.3-0.4, minimum to pass filter)
- No connection to actual successful gameplay data

**Phase A Validation Criteria**:
- [ ] 50 HIGH quality documents pass schema validation
- [ ] 50 LOW quality documents pass schema validation
- [ ] HIGH documents reference real DOE-020 episode data
- [ ] LOW documents contain deliberately unhelpful tactics
- [ ] Document JSON schema matches OpenSearch mapping (rag/mod.rs)

### Phase B: Embedding & Indexing

**Objective**: Index strategy documents in OpenSearch with kNN configuration.

**Note on Current Implementation**: The existing RagClient (rag/mod.rs) uses **term-matching** on situation_tags (not vector kNN). The current query (lines 141-155) uses `bool.should` with `term` queries on `situation_tags`. This is adequate for the DOE-022 design because:
1. Situation tags are derived deterministically from GameState (lines 54-79)
2. Term matching is simpler, faster, and sufficient to test the L2 value proposition
3. Full kNN with embeddings can be tested in DOE-023 if DOE-022 shows L2 value

**Infrastructure Setup**:
```bash
# Verify OpenSearch health
curl -sf http://localhost:9200/_cluster/health

# Create strategies index with mapping
curl -X PUT http://localhost:9200/strategies -H 'Content-Type: application/json' -d '{
  "mappings": {
    "properties": {
      "doc_id": {"type": "keyword"},
      "situation_tags": {"type": "keyword"},
      "decision.tactic": {"type": "keyword"},
      "decision.weapon": {"type": "keyword"},
      "decision.positioning": {"type": "keyword"},
      "quality.trust_score": {"type": "float"},
      "quality.source_strategy": {"type": "keyword"},
      "quality.source_experiment": {"type": "keyword"},
      "quality.source_episodes": {"type": "integer"},
      "quality.mean_kills": {"type": "float"},
      "metadata.created": {"type": "date"},
      "metadata.version": {"type": "integer"},
      "metadata.retired": {"type": "boolean"}
    }
  }
}'

# Bulk index documents
curl -X POST http://localhost:9200/strategies/_bulk -H 'Content-Type: application/x-ndjson' --data-binary @high_quality_docs.ndjson
curl -X POST http://localhost:9200/strategies/_bulk -H 'Content-Type: application/x-ndjson' --data-binary @low_quality_docs.ndjson

# Verify index count
curl http://localhost:9200/strategies/_count
```

**Phase B Validation Criteria**:
- [ ] OpenSearch cluster health: green or yellow
- [ ] strategies index created with correct mapping
- [ ] HIGH quality docs indexed: document count = 50
- [ ] LOW quality docs indexed: document count = 50 (total 100)
- [ ] Test query returns results: `curl http://localhost:9200/strategies/_search?q=situation_tags:multi_enemy`
- [ ] Query latency < 50ms for term-match queries

### Phase C: L2 Integration Test

**Objective**: Verify Rust agent-core L2 cascade fires correctly with real OpenSearch data.

**Integration Points** (from cascade.rs lines 155-165):
```rust
// Level 2: OpenSearch kNN (< 100ms target)
if self.config.l2_enabled {
    if let Some(decision) = self.rag_client.query(state).await {
        self.cache_client.insert(state, &decision);
        return Decision { ... };
    }
}
```

**Test Protocol**:
1. Start OpenSearch container with indexed documents
2. Start agent-core with `CASCADE_MODE=full_agent` and `OPENSEARCH_URL=http://opensearch:9200`
3. Send test GameState via gRPC with conditions that trigger L2:
   - health=80, ammo=50, enemies_visible=4 → tags: [full_health, ammo_abundant, multi_enemy]
4. Verify decision.decision_level == 2
5. Verify decision.rule_matched starts with "RAG:"
6. Verify latency_ns < 100_000_000 (100ms)

**Phase C Validation Criteria**:
- [ ] agent-core starts without errors
- [ ] L2 query reaches OpenSearch (check opensearch access log)
- [ ] Decision returned with decision_level=2
- [ ] Latency < 100ms P99
- [ ] L2 result cached in DuckDB L1 (verify cache entry)
- [ ] Graceful degradation: if OpenSearch down, cascade falls through to fallback

**Risk Mitigation**:
- If L2 latency > 100ms: reduce `k` from 5 to 3, or increase HTTP timeout from 80ms to 150ms
- If OpenSearch connection fails: verify docker network, check container health
- If no documents match: expand situation tags in derive_situation_tags()

## DOE-022 Phase D: Comparison Experiment

### Factor

| Factor | Type | Levels | Description |
|--------|------|--------|-------------|
| decision_cascade | Categorical | 4 | Active cascade layers with document quality variation |

### Factor Levels

| Level | Condition Label | Cascade Config | Strategy Docs | Expected kr | Rationale |
|-------|----------------|----------------|---------------|-------------|-----------|
| 1 | L0_only | l0=true, l1=false, l2=false | N/A | ~39 | Baseline, worst performer (F-010, F-034) |
| 2 | L0_L1 | l0=true, l1=true, l2=false | N/A | ~43-45 | Current default, no L2 |
| 3 | L0_L1_L2_good | l0=true, l1=true, l2=true | HIGH quality (50 docs) | ~45-50? | Full cascade with curated docs |
| 4 | L0_L1_L2_random | l0=true, l1=true, l2=true | LOW quality (50 docs) | ~42-45? | Full cascade with noise docs |

**Note on L0_L1 Condition**: In DOE-008 through DOE-020, the Python glue layer bypassed the Rust agent-core entirely, using action_functions.py directly. For DOE-022, L0_L1 will use the Python action functions that replicate L0+L1 behavior (burst_3 as the best-performing L0+L1 strategy from DOE-020, kill_rate=45.44). This provides the most meaningful comparison: "Can L2 beat the best known L0+L1 strategy?"

**IMPORTANT Design Decision**: The L0_L1 condition uses burst_3 (the empirically best L0+L1 strategy) rather than random, because we want to know if L2 adds value over the BEST available baseline, not just over an arbitrary one. If L2 cannot beat burst_3, it provides no practical value regardless of statistical significance over weaker baselines.

### Key Contrasts

| Contrast | Comparison | Scientific Question |
|----------|------------|---------------------|
| C1 | L0_L1_L2_good vs L0_L1 | Does L2 add value over best baseline? |
| C2 | L0_L1_L2_good vs L0_L1_L2_random | Does document quality matter? |
| C3 | L0_L1 vs L0_only | Replication of F-010 (L0_only deficit) |
| C4 | L0_L1_L2_random vs L0_L1 | Does low-quality L2 hurt performance? |

### Expected Outcomes

| Outcome | C1 Result | C2 Result | Interpretation | Next Step |
|---------|-----------|-----------|----------------|-----------|
| **A: L2 adds value, quality matters** | p<0.05 | p<0.05 | RAG validated, curation critical | Phase 2: document optimization |
| **B: L2 adds value, quality doesn't matter** | p<0.05 | p>0.05 | L2 helps regardless of doc quality | Explore why (retrieval as exploration?) |
| **C: L2 neutral, quality matters** | p>0.05 | p<0.05 | Documents affect behavior but not performance | Redesign L2 action selection |
| **D: L2 no value** | p>0.05 | p>0.05 | L2 architecture provides no benefit | Reconsider RAG approach |
| **E: L2 hurts performance** | negative | — | Strategy interference (similar to F-011 full_agent penalty) | Investigate tactic_to_action mapping |

## Design Matrix

| Run | Condition | Cascade Config | Documents | Episodes | Seeds |
|-----|-----------|----------------|-----------|----------|-------|
| R1 | L0_only | l0 only | None | 30 | [24001, ..., 26822] |
| R2 | L0_L1 | burst_3 (best L0+L1) | None | 30 | [24001, ..., 26822] |
| R3 | L0_L1_L2_good | full cascade | HIGH quality (50) | 30 | [24001, ..., 26822] |
| R4 | L0_L1_L2_random | full cascade | LOW quality (50) | 30 | [24001, ..., 26822] |

**Total**: 4 conditions x 30 episodes = 120 episodes

### Randomized Execution Order

R3 (L0_L1_L2_good) -> R1 (L0_only) -> R4 (L0_L1_L2_random) -> R2 (L0_L1)

**Rationale**: OpenSearch-dependent conditions (R3, R4) run first to detect infrastructure issues early. Index swap between R3 and R4 (replace HIGH docs with LOW docs, or use separate indices).

### Document Index Management Between Conditions

```
R3 (L0_L1_L2_good):
  Index: strategies_high (50 HIGH quality documents)
  Config: OPENSEARCH_INDEX=strategies_high

R4 (L0_L1_L2_random):
  Index: strategies_low (50 LOW quality documents)
  Config: OPENSEARCH_INDEX=strategies_low

R1, R2: L2 disabled, index irrelevant
```

Two separate indices avoid accidental cross-contamination. Both indices use identical schema but different document contents.

## Seed Set

**Formula**: seed_i = 24001 + i x 97, i = 0, 1, ..., 29
**Range**: [24001, 26822]
**Count**: 30 seeds per condition, identical across all 4 conditions

**Full seed set**:
```
[24001, 24098, 24195, 24292, 24389, 24486, 24583, 24680, 24777, 24874,
 24971, 25068, 25165, 25262, 25359, 25456, 25553, 25650, 25747, 25844,
 25941, 26038, 26135, 26232, 26329, 26426, 26523, 26620, 26717, 26822]
```

**Correction**: seed_29 = 24001 + 29 x 97 = 24001 + 2813 = 26814 (not 26822).

**Corrected full seed set**:
```
[24001, 24098, 24195, 24292, 24389, 24486, 24583, 24680, 24777, 24874,
 24971, 25068, 25165, 25262, 25359, 25456, 25553, 25650, 25747, 25844,
 25941, 26038, 26135, 26232, 26329, 26426, 26523, 26620, 26717, 26814]
```

**Range**: [24001, 26814]

### Cross-Experiment Seed Collision Check

This seed set ([24001, 26814]) is COMPLETELY INDEPENDENT from all prior experiments:

| Experiment | Seed Range | Overlap with [24001, 26814]? |
|------------|------------|------------------------------|
| DOE-001 | [42, 2211] | NO |
| DOE-002 | [1337, 1830] | NO |
| DOE-003 | [2023, 2690] | NO |
| DOE-004 | [7890, 8527] | NO |
| DOE-005 | [2501, 3168] | NO |
| DOE-006 | [3501, 4342] | NO |
| DOE-007 | [4501, 5400] | NO |
| DOE-008 | [6001, 7074] | NO |
| DOE-009 | [8001, 9190] | NO |
| DOE-010 | [10001, 11248] | NO |
| DOE-011 | [12001, 13372] | NO |
| DOE-012 | [13001, 14538] | NO |
| DOE-013 | [14001, 15712] | NO |
| DOE-014 | [15001, 16770] | NO |
| DOE-015 | [16001, 17944] | NO |
| DOE-016 | [17001, 19056] | NO |
| DOE-017 | [18001, 20118] | NO |
| DOE-018 | [19001, 21284] | NO |
| DOE-019 | [20001, 22404] | NO |
| DOE-020 | [21001, 23581] | NO |

**Verdict**: Maximum prior seed = 23581 (DOE-020). DOE-022 starts at 24001. Gap of 420. Zero seed collisions. True independent validation.

## Scenario Configuration

**Scenario**: defend_the_line.cfg (3-action space)
```
available_buttons = { TURN_LEFT TURN_RIGHT ATTACK }
available_game_variables = { KILLCOUNT HEALTH AMMO2 }
episode_timeout = 2100  # 60s at 35 fps
```

## Implementation Notes

### L0_L1_L2_good and L0_L1_L2_random Conditions

These conditions require the Rust agent-core cascade to be active (unlike DOE-008 through DOE-020 which used Python action functions). Two options:

**Option 1: Rust Agent-Core Integration** (preferred but complex)
- Start agent-core container with l2_enabled=true
- Python glue sends GameState via gRPC, receives Decision
- Requires full gRPC integration and container orchestration
- Latency includes gRPC round-trip

**Option 2: Python RAG Shim** (simpler, recommended for DOE-022)
- Implement OpenSearch query in Python glue (mirror rag/mod.rs logic)
- Python directly queries OpenSearch for strategy documents
- Apply same scoring (similarity * 0.4 + confidence * 0.4 + recency * 0.2)
- Map winning tactic to action via same tactic_to_action() logic
- **Advantage**: No gRPC dependency, simpler debugging, faster iteration
- **Limitation**: Tests the L2 strategy concept, not the full Rust pipeline integration

**Recommendation**: Use Option 2 for DOE-022. The scientific question is "Do strategy documents improve performance?" not "Does the Rust gRPC pipeline work?" Integration testing can follow in DOE-023.

### Python RAG Shim Specification

```python
class L2RagAction:
    """L2 strategy document retrieval action function.

    Mirrors agent-core/src/rag/mod.rs logic in Python.
    Queries OpenSearch for matching strategy documents,
    scores them, and selects the best action.
    """

    def __init__(self, opensearch_url, index_name, k=5):
        self.opensearch_url = opensearch_url
        self.index_name = index_name
        self.k = k
        self.weights = {"similarity": 0.4, "confidence": 0.4, "recency": 0.2}

    def derive_situation_tags(self, state):
        """Mirror derive_situation_tags() from rag/mod.rs lines 54-79."""
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
        return tags

    def query_opensearch(self, tags):
        """Execute OpenSearch term-match query."""
        # Build same query as rag/mod.rs lines 141-155
        # POST {opensearch_url}/{index_name}/_search
        # Returns top-k documents matching situation tags
        pass

    def score_document(self, doc):
        """Score document: similarity*0.4 + confidence*0.4 + recency*0.2"""
        pass

    def tactic_to_action(self, tactic):
        """Map tactic string to action index (mirrors rag/mod.rs lines 82-91)."""
        if tactic.startswith("retreat") or tactic.startswith("kite"):
            return ACTION_MOVE_LEFT
        elif tactic.startswith("flank"):
            return ACTION_MOVE_RIGHT
        else:
            return ACTION_ATTACK

    def __call__(self, state):
        """Full L0 + L1 + L2 cascade in Python."""
        # L0: Emergency rules (health < 30 -> dodge)
        if state.health < 30:
            return ACTION_MOVE_LEFT

        # L2: Query OpenSearch
        tags = self.derive_situation_tags(state)
        if tags:
            docs = self.query_opensearch(tags)
            if docs:
                best = max(docs, key=self.score_document)
                return self.tactic_to_action(best["decision"]["tactic"])

        # Fallback: burst_3 pattern (best known L0+L1)
        # This mirrors the cascade fallback to lower levels
        return self._burst_3_fallback(state)
```

### L0_L1 Condition

Uses existing `Burst3Action` from action_functions.py — the empirically best L0+L1 strategy (DOE-020: 45.44 kr, 15.40 kills).

### L0_only Condition

Uses existing `rule_only_action` from action_functions.py (L0 reflex rules only, tunnel vision baseline).

## Statistical Analysis Plan

### Primary Analysis
1. **One-way ANOVA** on kill_rate (4 levels)
   - Response: kill_rate = (kills / survival_time) * 60
   - Factor: decision_cascade (4 conditions)
   - alpha = 0.05

### Residual Diagnostics
2. **Normality**: Shapiro-Wilk or Anderson-Darling test
3. **Equal variance**: Levene test
4. **Independence**: Residuals vs run order

### If ANOVA significant (p < 0.05):
5. **Planned Contrasts** (4 contrasts, Bonferroni alpha = 0.0125):
   - C1: L0_L1_L2_good vs L0_L1 (does L2 add value over best baseline?)
   - C2: L0_L1_L2_good vs L0_L1_L2_random (does document quality matter?)
   - C3: L0_L1 vs L0_only (replication of F-010, DOE-008 finding)
   - C4: L0_L1_L2_random vs L0_L1 (does low-quality L2 hurt performance?)

6. **Tukey HSD** all pairwise comparisons (6 pairs)
7. **Effect sizes**: Cohen's d for each contrast, partial eta-squared for omnibus
8. **Power analysis**: Post-hoc for observed effect sizes

### Non-Parametric Backup
9. **Kruskal-Wallis** if normality violated
10. **Mann-Whitney U** for individual contrasts if non-parametric required

### Secondary Responses
11. Repeat primary analysis for:
    - kills (total kills per episode)
    - survival_time (seconds survived)
    - l2_hit_rate (proportion of decisions from L2, for L2 conditions only)
    - l2_latency_p50 and l2_latency_p99 (OpenSearch query latency)

### Cross-Experiment Comparison
12. Compare L0_L1 (burst_3) results to:
    - DOE-020 burst_3: 45.44 kr (seed [21001, 23581])
    - DOE-017 burst_3: 45.42 kr (seed [18001, 20118])
    - DOE-012 burst_3: 44.55 kr (seed [14001, 15364])
    - Cohen's d between DOE-022 and prior experiments (expect d < 0.2, replication)

### Decision Framework
13. Based on contrasts C1 and C2:

| C1 Result | C2 Result | Decision |
|-----------|-----------|----------|
| L2_good > L0_L1 (p<0.0125) | L2_good > L2_random (p<0.0125) | RAG VALIDATED, quality matters → Phase 2 curation |
| L2_good > L0_L1 (p<0.0125) | NS | L2 helps but quality irrelevant → investigate mechanism |
| NS | L2_good > L2_random (p<0.0125) | Docs differ but no net improvement → redesign L2 action selection |
| NS | NS | L2 provides no value → reconsider architecture |

### Power
- Expected power for medium effect (f=0.25) with k=4, n=30, alpha=0.05: approximately 0.72
- Expected power for large effect (f=0.40) with k=4, n=30, alpha=0.05: approximately 0.96
- Prior experiments observed f=0.30-0.45 on defend_the_line: power > 0.85

**Note**: If DOE-022 finds marginal results (0.05 < p < 0.10), increase n to 50 per condition (200 total) in a follow-up DOE-022b to improve power.

## R100 Compliance

| Requirement | Status |
|-------------|--------|
| Fixed seeds | YES: seed_i = 24001 + i x 97, i=0..29 |
| No seed collisions | YES: verified against all 20 prior experiments |
| n >= 30 per condition | YES: 30 episodes per condition |
| Statistical evidence markers | PLANNED: all results will include [STAT:] markers |
| Residual diagnostics | PLANNED: normality, variance, independence |
| Effect sizes | PLANNED: Cohen's d, partial eta-squared |
| Seeds identical across conditions | YES: all 4 conditions use same 30 seeds |
| Trust score assignment | PLANNED: per trust framework in R100 |

## Execution Checklist

### Phase A: Strategy Document Generation
- [ ] Analyze DOE-020 burst_3 episodes (30 episodes, seeds [21001, 23581])
- [ ] Analyze DOE-020 adaptive_kill episodes (30 episodes, seeds [21001, 23581])
- [ ] Generate 50 HIGH quality strategy documents
- [ ] Generate 50 LOW quality strategy documents (random/irrelevant)
- [ ] Validate all 100 documents against JSON schema
- [ ] Store documents in research/experiments/doe-022-data/

### Phase B: Embedding & Indexing
- [ ] Verify OpenSearch container running: `curl http://localhost:9200`
- [ ] Create strategies_high index with mapping
- [ ] Create strategies_low index with mapping
- [ ] Bulk index 50 HIGH quality docs into strategies_high
- [ ] Bulk index 50 LOW quality docs into strategies_low
- [ ] Verify index counts: `curl http://localhost:9200/strategies_high/_count`
- [ ] Test query: `curl http://localhost:9200/strategies_high/_search?q=situation_tags:multi_enemy`
- [ ] Measure query latency (target: < 50ms)

### Phase C: L2 Integration Test
- [ ] Implement Python RAG shim (L2RagAction class)
- [ ] Unit test: derive_situation_tags() matches Rust implementation
- [ ] Unit test: tactic_to_action() matches Rust implementation
- [ ] Integration test: query OpenSearch, get results, score, select action
- [ ] Latency test: end-to-end L2 decision < 100ms
- [ ] Fallback test: L2 gracefully degrades when no docs match
- [ ] Fallback test: L2 gracefully degrades when OpenSearch down

### Phase D: DOE-022 Execution
- [ ] Seed set generated and logged
- [ ] All 4 action functions implemented and tested
- [ ] L0_only: rule_only_action (existing)
- [ ] L0_L1: Burst3Action (existing)
- [ ] L0_L1_L2_good: L2RagAction with strategies_high index
- [ ] L0_L1_L2_random: L2RagAction with strategies_low index
- [ ] DuckDB experiment table ready
- [ ] Execute R3 (L0_L1_L2_good) — 30 episodes
- [ ] Record l2_hit_rate and l2_latency for R3
- [ ] Execute R1 (L0_only) — 30 episodes
- [ ] Execute R4 (L0_L1_L2_random) — 30 episodes
- [ ] Record l2_hit_rate and l2_latency for R4
- [ ] Execute R2 (L0_L1) — 30 episodes
- [ ] Verify 120 total episodes recorded
- [ ] Data quality check: no missing values, plausible ranges

## Risk Assessment

| Risk | Severity | Probability | Mitigation |
|------|----------|-------------|------------|
| L2 latency > 100ms | MEDIUM | LOW | Reduce k from 5 to 3; increase HTTP timeout |
| OpenSearch container crashes | MEDIUM | LOW | Health check, auto-restart, run L2 conditions first |
| No documents match situation tags | HIGH | MEDIUM | Expand tag coverage in Phase A; add catch-all tags |
| Strategy docs don't translate to actions well | HIGH | MEDIUM | tactic_to_action mapping too coarse (only 3 outcomes); refine mapping |
| L2 action selection equivalent to random | HIGH | MEDIUM | If all situations map to "attack", L2 degenerates; ensure diverse tactics |
| Rust-Python behavioral mismatch | LOW | HIGH | Use Python shim for DOE-022, defer Rust integration to DOE-023 |

### Critical Risk: tactic_to_action Granularity

The current tactic_to_action mapping (rag/mod.rs lines 82-91) maps all tactics to only 3 actions:
- "retreat*" or "kite*" → MoveLeft
- "flank*" → MoveRight
- Everything else → Attack

This means L2 strategy selection effectively reduces to:
1. Should the agent retreat? → MoveLeft
2. Should the agent flank? → MoveRight
3. Everything else → Attack

With the 3-action space (TURN_LEFT, TURN_RIGHT, ATTACK), the mapping becomes:
- retreat → TURN_LEFT (not actual retreat in defend_the_line, just turns left)
- flank → TURN_RIGHT (just turns right)
- attack → ATTACK

**This may be too coarse to differentiate from random action selection.** If DOE-022 shows no L2 value, the tactic_to_action mapping should be investigated as a confound before concluding RAG is worthless.

**Mitigation**: Ensure HIGH quality documents include diverse tactic types (burst_fire_sweep → alternating attack/turn, not just "attack"). The key is whether L2 can introduce TEMPORAL patterns (e.g., "attack 3 times then turn" via sequential L2 calls) rather than single-tick decisions.

## Data Collection

### Per-Episode Metrics (DuckDB)

```sql
CREATE TABLE IF NOT EXISTS doe_022 (
  episode_id INTEGER,
  condition TEXT,
  seed INTEGER,
  kills INTEGER,
  health_remaining INTEGER,
  ammo_remaining INTEGER,
  survival_time_seconds REAL,
  kill_rate REAL,
  l2_decisions INTEGER DEFAULT 0,     -- count of L2-sourced decisions
  l2_total_decisions INTEGER DEFAULT 0, -- total decisions in episode
  l2_hit_rate REAL DEFAULT 0.0,        -- l2_decisions / l2_total_decisions
  l2_latency_mean_ms REAL DEFAULT 0.0, -- mean OpenSearch query time
  l2_latency_p99_ms REAL DEFAULT 0.0,  -- P99 OpenSearch query time
  PRIMARY KEY (condition, seed)
);
```

### Per-Decision Metrics (Optional, for L2 debugging)

```sql
CREATE TABLE IF NOT EXISTS doe_022_decisions (
  episode_id INTEGER,
  condition TEXT,
  tick INTEGER,
  decision_level INTEGER,  -- 0=L0, 1=L1, 2=L2, 255=fallback
  action INTEGER,
  situation_tags TEXT,      -- JSON array of tags
  doc_id TEXT,              -- matched document (if L2)
  doc_score REAL,           -- weighted score (if L2)
  latency_ms REAL,
  PRIMARY KEY (condition, episode_id, tick)
);
```

## Status

**ORDERED** — Requires Phases A-C infrastructure setup before Phase D execution.

### Dependencies
- OpenSearch container running and healthy
- Strategy document corpus generated (Phase A)
- Documents indexed in OpenSearch (Phase B)
- Python RAG shim implemented and tested (Phase C)
- All existing action functions available (action_functions.py)
