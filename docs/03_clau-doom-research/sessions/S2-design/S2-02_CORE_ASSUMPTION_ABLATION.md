# S2-02: Core Assumption Validation Plan (Ablation Design)

> **Session**: S2 (Research Design Reinforcement)
> **Priority**: ORANGE high
> **Dependencies**: None
> **Status**: COMPLETE

---

## Purpose

Validate the project's core assumption: **"Agent Skill = OpenSearch Document Quality x Rust Scoring Accuracy"**. If this assumption fails, the entire feedback loop (play -> retrospect -> generate docs -> improve) loses its foundation. Three ablation studies systematically isolate each factor of this equation.

---

## Ablation 1: Document Quality Manipulation

### Hypothesis

**H-ABL-01**: Strategy document quality has a monotonically positive effect on agent performance. Specifically: High Quality docs > Degraded docs > Random docs.

**Formal Statement**: Let mu_H, mu_D, mu_R denote mean kill_rate under High Quality, Degraded, and Random document conditions respectively. We test:
- H0: mu_H = mu_D = mu_R (document quality has no effect)
- H1: At least one pair differs

**Directional Prediction**: mu_H > mu_D > mu_R

### Exact Manipulation Procedure

#### Condition A: Full RAG (Control)
- Normal operation: LLM-refined strategy documents in OpenSearch
- All document quality fields intact (situation_tags, success_rate, confidence_tier)
- Rust scoring uses standard weights: similarity(0.4) + confidence(0.4) + recency(0.2)
- This is the standard full-system configuration

#### Condition B: Degraded Documents
Systematically corrupt document quality while preserving document structure:

**Degradation Method**:
```python
def degrade_document(doc):
    """Corrupt semantic alignment while preserving structure."""
    degraded = doc.copy()

    # 1. Shuffle situation_tags across documents (breaks semantic match)
    #    e.g., ["narrow_corridor", "multi_enemy"] -> ["open_area", "low_ammo"]
    degraded["situation_tags"] = random_shuffle_from_pool(all_tags)

    # 2. Corrupt situation_embedding with Gaussian noise
    #    noise_level = 0.5 * std(original_embeddings)
    noise = np.random.normal(0, 0.5 * embedding_std, len(doc["situation_embedding"]))
    degraded["situation_embedding"] = doc["situation_embedding"] + noise
    # Re-normalize to unit vector
    degraded["situation_embedding"] /= np.linalg.norm(degraded["situation_embedding"])

    # 3. Preserve decision and quality fields (only semantic mapping is broken)
    #    decision.tactic and decision.weapon remain unchanged
    #    quality.success_rate and quality.confidence_tier remain unchanged

    return degraded
```

**Rationale**: By corrupting tags and embeddings but preserving the action recommendations, we test whether *semantic retrieval accuracy* matters. The agent still gets strategy recommendations, but they are mismatched to the current situation.

**Degradation Verification**:
- Measure mean cosine similarity between query and retrieved docs under each condition
- Expected: Condition A sim > 0.7, Condition B sim ~ 0.3-0.5, Condition C sim ~ 0.0-0.2

#### Condition C: Random Documents
Replace the OpenSearch index with irrelevant documents:

**Method**:
```python
def create_random_document():
    """Generate structurally valid but semantically random strategy doc."""
    return {
        "doc_id": f"random_{uuid4()}",
        "agent_id": "BASELINE",
        "generation": 0,
        "situation_embedding": random_unit_vector(embedding_dim),
        "situation_tags": random.sample(ALL_POSSIBLE_TAGS, k=3),
        "decision": {
            "tactic": random.choice(ALL_TACTICS),
            "weapon": random.choice(ALL_WEAPONS)
        },
        "quality": {
            "success_rate": random.uniform(0.1, 0.9),
            "sample_size": random.randint(5, 50),
            "confidence_tier": random.choice(["low", "medium", "high"])
        }
    }
```

- Generate same number of documents as in Condition A
- Index into a separate OpenSearch index (opensearch_random)
- Agent queries this index instead of the real one

### Measurement Plan

| Metric | Purpose |
|--------|---------|
| kill_rate | Primary response variable |
| survival_time | Secondary |
| ammo_efficiency | Tests whether wrong-situation tactics waste ammo |
| retrieval_similarity | Mean cosine sim between query and top-K docs (manipulation check) |
| rule_match_rate | Fraction of decisions falling back to L0 rules |
| encounter_success_rate | Per-encounter win rate |

### Sample Size

- 3 conditions x 50 episodes/condition = 150 episodes total
- Power analysis (one-way ANOVA, 3 groups, f = 0.30 medium effect):
  - alpha = 0.05, power = 0.80 -> n = 42 per group
  - Rounding up: n = 50 per group provides power ~ 0.87
- All conditions use IDENTICAL seed set (first 50 from master seed set)

### Statistical Analysis Plan

**Primary Analysis**: One-way ANOVA
```
Source              | df
--------------------|----
Document Quality    | 2
Error               | 147
Total               | 149

Post-hoc: Tukey HSD for pairwise comparisons (A vs B, A vs C, B vs C)
```

**Diagnostics**:
- Normality: Anderson-Darling test on residuals
- Equal variance: Levene's test
- Independence: run-order plot inspection

**Effect Size**: partial eta-squared and Cohen's d for each pairwise comparison

**Reporting**:
```
[STAT:f] F(2,147) = {value}
[STAT:p] p = {value}
[STAT:eta2] partial eta^2 = {value}
[STAT:ci] 95% CI for (mu_A - mu_B): [{lower}, {upper}]
[STAT:effect_size] Cohen's d(A vs B) = {value}
```

### Expected Outcomes

| Condition | Expected kill_rate | Expected retrieval_sim |
|-----------|-------------------|----------------------|
| A: Full RAG | Highest (8-12 kills) | > 0.7 |
| B: Degraded | Moderate (5-8 kills) | 0.3-0.5 |
| C: Random | Lowest (3-5 kills, near Rule-Only) | 0.0-0.2 |

### Contingency: What if Document Quality Does NOT Matter?

**Scenario**: No significant difference between A, B, and C (p > 0.05).

**Implications**:
1. The RAG pipeline may not be retrieving situation-appropriate documents even under normal conditions
2. The Rust scoring weights may be compensating (choosing decent actions regardless of document relevance)
3. The agent may be primarily relying on Level 0 rules, rarely using Level 2 results

**Diagnostic Actions**:
- Examine decision_level distribution in Full Agent: what fraction of decisions actually use L2?
- If L2 usage < 10%: the RAG system is not being reached often enough -> architecture problem
- If L2 usage > 30% but quality does not matter: the scoring function may be ignoring document content -> scoring bug
- Run Ablation 2 (scoring weights) to isolate the mechanism

**Recovery Plan**:
- If retrieval itself works (high similarity) but performance unchanged: investigate whether tactics in documents are actually better than random
- Consider: document quality may matter only in specific encounter types (narrow corridors, multi-enemy) -> subgroup analysis by encounter type
- Worst case: RAG pipeline redesign, starting from embedding model quality

---

## Ablation 2: Scoring Weight Isolation

### Hypothesis

**H-ABL-02**: The Rust scoring weight combination (similarity 0.4, confidence 0.4, recency 0.2) produces better performance than any single-factor scoring or random selection from kNN results.

**Formal Statement**: Let mu_OPT, mu_SIM, mu_CONF, mu_RAND denote mean kill_rate under Optimized, Similarity-only, Confidence-only, and Random scoring. We test:
- H0: mu_OPT = mu_SIM = mu_CONF = mu_RAND
- H1: At least one pair differs

**Directional Prediction**: mu_OPT >= max(mu_SIM, mu_CONF) > mu_RAND

### Exact Manipulation Procedure

All conditions use the SAME document pool (identical OpenSearch index). Only the scoring function changes.

#### Condition 1: Optimized Weights (Control)
```rust
fn score_document(doc: &Document, query: &Query) -> f64 {
    let similarity = cosine_similarity(query.embedding, doc.situation_embedding);
    let confidence = wilson_lower_bound(doc.quality.success_rate, doc.quality.sample_size);
    let recency = recency_decay(doc.quality.last_validated);

    0.4 * similarity + 0.4 * confidence + 0.2 * recency
}
```

#### Condition 2: Similarity Only
```rust
fn score_document(doc: &Document, query: &Query) -> f64 {
    cosine_similarity(query.embedding, doc.situation_embedding)
    // Ignores document reliability and age
}
```

#### Condition 3: Confidence Only
```rust
fn score_document(doc: &Document, query: &Query) -> f64 {
    wilson_lower_bound(doc.quality.success_rate, doc.quality.sample_size)
    // Always picks the most "proven" document, regardless of situation relevance
}
```

#### Condition 4: Random Selection from kNN Top-K
```rust
fn score_document(_doc: &Document, _query: &Query) -> f64 {
    rand::random::<f64>()
    // Random selection among the kNN results (still within Top-K, not truly random)
}
```

**Implementation Note**: Weight changes are in the Rust scoring function only. No changes to OpenSearch queries, document pool, or game environment.

### Additional Weight Combinations (Exploratory)

Beyond the four primary conditions, test extreme weights for regression modeling:

| Condition | Sim | Conf | Rec | Purpose |
|-----------|-----|------|-----|---------|
| W5 | 0.8 | 0.1 | 0.1 | Similarity-dominant |
| W6 | 0.1 | 0.8 | 0.1 | Confidence-dominant |
| W7 | 0.1 | 0.1 | 0.8 | Recency-dominant |
| W8 | 0.33 | 0.33 | 0.34 | Equal weights |

Total: 8 conditions for a richer response surface.

### Sample Size

**Primary analysis (4 conditions)**:
- One-way ANOVA with 4 groups, f = 0.30 (medium effect)
- alpha = 0.05, power = 0.80 -> n = 33 per group
- Use n = 40 per group for safety: 4 x 40 = 160 episodes

**Extended analysis (8 conditions)**:
- Use n = 30 per condition: 8 x 30 = 240 episodes
- Same seed set across all conditions (first 40 from master set for primary, full 70 for extended)

### Statistical Analysis Plan

**Primary Analysis**: One-way ANOVA (4 conditions)
```
Source          | df
----------------|----
Scoring Weight  | 3
Error           | 156
Total           | 159
```

**Extended Analysis**: Multiple regression on weight space
```
kill_rate = beta_0 + beta_1*w_sim + beta_2*w_conf + beta_3*w_rec
            + beta_12*w_sim*w_conf + beta_13*w_sim*w_rec + beta_23*w_conf*w_rec
            + epsilon

(Note: w_sim + w_conf + w_rec = 1.0, so one weight is determined by the others.
Use w_sim and w_conf as independent variables, w_rec = 1 - w_sim - w_conf.)
```

This regression model estimates the response surface over the weight simplex, allowing identification of the optimal weight combination.

**Post-hoc**: Tukey HSD for pairwise comparisons
**Diagnostics**: Anderson-Darling, Levene, run-order plot
**Effect Size**: partial eta-squared, Cohen's d per pair

### Expected Outcomes

| Condition | Expected kill_rate | Rationale |
|-----------|-------------------|-----------|
| Optimized (0.4/0.4/0.2) | Highest (10-12) | Balanced retrieval quality |
| Similarity Only | Moderate-High (8-10) | Good situation match but unreliable docs used |
| Confidence Only | Moderate (7-9) | Reliable docs but poor situation match |
| Random from kNN | Lowest (5-7) | No selection signal within Top-K |

### Contingency: What if Scoring Weights Do NOT Matter?

**Scenario**: No significant difference among conditions (p > 0.05).

**Implications**:
1. All documents in the Top-K may be equivalently useful (homogeneous pool)
2. The kNN pre-filtering already does most of the work; scoring is refinement
3. Document quality variance may be too low to differentiate

**Diagnostic Actions**:
- Examine Top-K document diversity: if all Top-K docs recommend the same action, scoring cannot matter
- Measure action entropy across conditions: if all conditions produce same actions, the scoring is irrelevant
- Check document pool size: if pool is small, kNN and scoring converge

**Recovery Plan**:
- If kNN already sufficient: simplify architecture (remove Rust scoring, use kNN rank directly)
- This simplification is itself a publishable finding (complexity reduction)
- Consider: scoring may only matter under specific conditions (large document pool, diverse situations) -> subgroup analysis
- Plan follow-up with artificially enlarged document pool to test scaling effects

---

## Ablation 3: RAG Layer Removal

### Hypothesis

**H-ABL-03**: Each decision layer (Level 0: MD rules, Level 1: DuckDB cache, Level 2: OpenSearch kNN) independently contributes measurable performance improvement. The full stack outperforms any subset.

**Formal Statement**: Let mu_FULL, mu_L01, mu_L0, mu_L2 denote mean kill_rate under Full Stack, L0+L1, L0-only, and L2-only conditions. We test:
- H0: mu_FULL = mu_L01 = mu_L0 = mu_L2
- H1: At least one pair differs

**Directional Predictions**:
- mu_FULL > mu_L01 > mu_L0 (additive layer value)
- mu_L2 position unknown (may outperform L0 or underperform depending on rule coverage)

### Exact Manipulation Procedure

#### Condition 1: Full Stack (Control)
All decision levels active:
```
Level 0 (MD rules): ENABLED
Level 1 (DuckDB cache): ENABLED
Level 2 (OpenSearch kNN): ENABLED
```
Decision flow: L0 match -> use L0. L0 miss -> L1 query -> L1 hit -> use L1. L1 miss -> L2 query -> use L2. L2 miss -> default action.

#### Condition 2: Level 0 Only (MD Rules)
```
Level 0 (MD rules): ENABLED
Level 1 (DuckDB cache): DISABLED (skip_duckdb_lookup = true)
Level 2 (OpenSearch kNN): DISABLED (skip_opensearch_query = true)
```
Same as Baseline 2 (Rule-Only Agent from S2-01). Cross-references provide consistency.

#### Condition 3: Level 0 + Level 1 (MD Rules + DuckDB Cache)
```
Level 0 (MD rules): ENABLED
Level 1 (DuckDB cache): ENABLED
Level 2 (OpenSearch kNN): DISABLED (skip_opensearch_query = true)
```
Tests whether local experience (DuckDB) alone adds value over static rules. DuckDB contains the agent's own play history, retrieved via SQL pattern matching.

#### Condition 4: Level 2 Only (OpenSearch kNN)
```
Level 0 (MD rules): DISABLED (skip_md_rules = true)
Level 1 (DuckDB cache): DISABLED (skip_duckdb_lookup = true)
Level 2 (OpenSearch kNN): ENABLED
```
Tests whether the collective knowledge base alone (without personal rules or experience) is sufficient. Every decision goes directly to OpenSearch kNN.

**Fallback behavior when active level misses**:
- L0-only: if no rule match -> default action (MOVE_FORWARD)
- L0+L1: if no rule match and no DuckDB hit -> default action
- L2-only: if no kNN result above similarity threshold -> default action
- Full: cascading fallback through levels

### Additional Tracking Per Condition

For every decision tick, record:
```sql
decision_log:
  tick_id INT,
  episode_id VARCHAR,
  ablation_condition VARCHAR,
  decision_level_used INT,      -- 0, 1, 2, or -1 (default/fallback)
  query_latency_ms DOUBLE,
  action_selected VARCHAR,
  situation_hash VARCHAR         -- for cross-condition comparison
```

This enables analysis of:
- Decision level utilization distribution per condition
- Latency differences across conditions
- Action divergence: how often do conditions produce different actions for the same situation?

### Factorial Extension: 2^3 Design

The 4 conditions above can be reframed as a 2^3 factorial (each level ON/OFF):

| Run | L0 | L1 | L2 | Condition Name |
|-----|----|----|-----|---------------|
| 1 | ON | ON | ON | Full Stack |
| 2 | ON | ON | OFF | L0+L1 |
| 3 | ON | OFF | ON | L0+L2 |
| 4 | ON | OFF | OFF | L0 Only |
| 5 | OFF | ON | ON | L1+L2 |
| 6 | OFF | ON | OFF | L1 Only |
| 7 | OFF | OFF | ON | L2 Only |
| 8 | OFF | OFF | OFF | No Layers (= Random fallback) |

**Rationale for full 2^3**: Enables estimation of all main effects AND interaction effects:
- Main: L0 effect, L1 effect, L2 effect
- 2-way: L0xL1, L0xL2, L1xL2
- 3-way: L0xL1xL2

**Practical constraint**: Run 8 (no layers) is equivalent to "always default action" which is not quite Random (it always moves forward). This provides a controlled floor distinct from Random Agent baseline.

### Sample Size

**Primary (4 conditions)**:
- One-way ANOVA, 4 groups, f = 0.30 -> n = 40 per group = 160 episodes
- Same seed set across all conditions

**Full factorial (8 conditions)**:
- 2^3 ANOVA, n = 30 per cell -> 240 episodes total
- Power for detecting medium main effect in 2^3: adequate at n = 30 (effect spread across 4 cells per factor)

### Statistical Analysis Plan

**Primary Analysis**: One-way ANOVA (4 conditions)
```
Source              | df
--------------------|----
Decision Layer      | 3
Error               | 156
Total               | 159
```

**Full Factorial Analysis**: 2^3 ANOVA
```
Source      | df
------------|----
L0          | 1
L1          | 1
L2          | 1
L0*L1       | 1
L0*L2       | 1
L1*L2       | 1
L0*L1*L2    | 1
Error       | 232
Total       | 239
```

**Key Contrasts**:
1. L2 main effect: Does OpenSearch add value? (averaged over L0, L1)
2. L1 main effect: Does DuckDB add value?
3. L0 main effect: Do MD rules add value?
4. L1xL2 interaction: Does DuckDB + OpenSearch synergize?
5. Full Stack vs. best single layer: Is combination better than any individual?

**Post-hoc**: Tukey HSD on the 4 primary conditions
**Planned Contrasts**: Full Stack vs. average of others (Helmert contrast)
**Diagnostics**: Standard ANOVA diagnostics
**Effect Size**: partial eta-squared per factor and interaction

### Expected Outcomes

| Condition | Expected kill_rate | Expected decision_latency_p99 |
|-----------|-------------------|-------------------------------|
| Full Stack | Highest (10-12) | < 100ms |
| L0+L1 | Moderate-High (7-10) | < 15ms |
| L0 Only | Moderate (5-8) | < 3ms |
| L2 Only | Variable (4-10) | < 100ms |
| L0+L2 | High (8-11) | < 100ms |
| L1+L2 | Moderate-High (7-10) | < 100ms |
| L1 Only | Low-Moderate (3-5) | < 10ms |
| No Layers | Lowest (1-3) | < 1ms |

**Interesting prediction**: L2 Only may outperform L0 Only if the document pool is rich and well-matched, but may underperform if documents are sparse or query situations are novel.

### Contingency: What if Layers Do NOT Add Value Independently?

**Scenario A**: L0+L1+L2 performs no better than L0 alone.
- Implies DuckDB and OpenSearch are not being used effectively
- Check: decision_level distribution shows L0 handles > 90% of decisions
- Action: Increase L0 rule miss rate (reduce rules) to force upper-level usage
- The agent may have too many rules, making upper levels unreachable

**Scenario B**: No significant interaction effects.
- Layers contribute independently (additive model sufficient)
- This simplifies the architecture analysis
- Publishable finding: modular decision system with additive benefits

**Scenario C**: Negative interaction (L1+L2 worse than L2 alone).
- DuckDB cache may provide stale or conflicting information
- Investigate DuckDB cache staleness and update frequency
- Consider cache invalidation strategy

**Recovery Plan**:
- If Full Stack not better than L0+L2: consider removing DuckDB layer (simplification)
- If Full Stack not better than L0: fundamental architecture problem -> redesign RAG pipeline
- In all cases: report findings honestly; negative results are valuable for the field

---

## Cross-Ablation Analysis

### Interaction Between Ablation 1 and Ablation 3

If both ablation studies are complete, cross-reference findings:

```
Expected consistency checks:
1. Ablation 1 Condition C (Random docs) should perform similarly to
   Ablation 3 L0 Only (both lack useful OpenSearch content)
2. Ablation 1 Condition A (Full RAG) should match
   Ablation 3 Full Stack (same configuration)
```

If these cross-references are inconsistent, investigate order effects or seed set differences.

### Comprehensive Model

After all three ablations, fit a unified model:

```
kill_rate = f(document_quality, scoring_weights, layer_configuration)
```

This enables quantifying the relative contribution of each component to the core formula:
```
Agent Skill = Document Quality x Scoring Accuracy
```

Specifically:
- Ablation 1 estimates the Document Quality coefficient
- Ablation 2 estimates the Scoring Accuracy coefficient
- Ablation 3 estimates the Layer Architecture contribution
- Cross-ablation analysis tests for multiplicative vs. additive relationships

---

## DuckDB Schema Additions

> **Note**: The core per-episode table is `experiments` (as defined in 03-EXPERIMENT.md).
> The `decision_level` column on `encounters` is shared with S2-01 (Baselines) — only
> one ALTER is needed across both designs.

```sql
-- Ablation condition column
ALTER TABLE experiments ADD COLUMN ablation_condition VARCHAR;
-- Values for Ablation 1: 'doc_full', 'doc_degraded', 'doc_random'
-- Values for Ablation 2: 'score_optimized', 'score_sim_only', 'score_conf_only',
--                         'score_random', 'score_w5'...'score_w8'
-- Values for Ablation 3: 'layer_full', 'layer_l0', 'layer_l01', 'layer_l2',
--                         'layer_l0l2', 'layer_l1l2', 'layer_l1', 'layer_none'

-- Ablation study identifier
ALTER TABLE experiments ADD COLUMN ablation_study VARCHAR;
-- Values: 'abl_1_doc_quality', 'abl_2_scoring', 'abl_3_layers'

-- Decision level per encounter (shared with S2-01 Baselines — define once)
-- NOTE: If S2-01 baseline schema is applied first, this ALTER is a no-op.
ALTER TABLE encounters ADD COLUMN IF NOT EXISTS decision_level INT;
-- 0: MD rule, 1: DuckDB cache, 2: OpenSearch kNN, -1: default/fallback

-- Retrieval quality tracking
ALTER TABLE encounters ADD COLUMN retrieval_similarity DOUBLE;
-- Mean cosine similarity of top-K docs for this encounter query

-- Decision latency per encounter
ALTER TABLE encounters ADD COLUMN decision_latency_ms DOUBLE;

-- Decision log table (tick-level granularity for Ablation 3)
CREATE TABLE decision_log (
    tick_id BIGINT,
    episode_id VARCHAR,
    ablation_condition VARCHAR,
    decision_level_used INT,
    query_latency_ms DOUBLE,
    action_selected VARCHAR,
    situation_hash VARCHAR,
    top_k_similarity DOUBLE[],
    PRIMARY KEY (episode_id, tick_id)
);

-- Ablation results summary view
CREATE VIEW ablation_summary AS
SELECT
    ablation_study,
    ablation_condition,
    COUNT(*) as n_episodes,
    AVG(kill_rate) as mean_kill_rate,
    STDDEV(kill_rate) as sd_kill_rate,
    AVG(survival_time) as mean_survival,
    STDDEV(survival_time) as sd_survival,
    AVG(ammo_efficiency) as mean_ammo_eff,
    AVG(CAST(rooms_visited AS DOUBLE) / total_rooms) as mean_exploration
FROM experiments
WHERE ablation_study IS NOT NULL
GROUP BY ablation_study, ablation_condition
ORDER BY ablation_study, mean_kill_rate DESC;
```

---

## Execution Order

### Recommended Sequence

```
Phase 1: Ablation 3 (Layer Removal) — RUN FIRST
  Rationale: Tests the most fundamental assumption (layer architecture).
  If Full Stack is not better than L0 Only, Ablations 1 and 2
  (which test OpenSearch-specific properties) are less meaningful.

  Estimated time: 3-4 hours (8 conditions x 30 episodes)

Phase 2: Ablation 1 (Document Quality) — RUN SECOND
  Rationale: Tests document quality, which is the Document Quality factor
  of the core formula. Only meaningful if Layer Removal showed L2 adds value.

  Estimated time: 2-3 hours (3 conditions x 50 episodes)

Phase 3: Ablation 2 (Scoring Weights) — RUN THIRD
  Rationale: Tests scoring accuracy, the other factor of the core formula.
  Fine-grained optimization that assumes documents and layers work.

  Estimated time: 3-4 hours (8 conditions x 30 episodes for full exploration)

Phase 4: Cross-Ablation Analysis
  Rationale: Synthesize findings from all three ablations.
  Fit unified model, check consistency, prepare for publication.

  Estimated time: 2-3 hours (analysis only, no new episodes)
```

### Decision Gates

```
After Ablation 3:
  IF Full Stack >> L0 Only (p < 0.05, d > 0.5):
    -> Proceed to Ablation 1 and 2 (RAG confirmed valuable)
  IF Full Stack ~ L0 Only (p > 0.10):
    -> STOP. Fundamental architecture problem.
    -> Investigate why upper layers are not contributing.
    -> Do NOT proceed to Ablation 1/2 until resolved.

After Ablation 1:
  IF Full RAG >> Random Docs (p < 0.05, d > 0.5):
    -> Proceed to Ablation 2 (document quality confirmed important)
  IF Full RAG ~ Random Docs (p > 0.10):
    -> Scoring weights (Ablation 2) probably irrelevant too.
    -> Focus on understanding WHY documents do not help.
    -> May still run Ablation 2 for completeness, but lower priority.
```

---

## Integration with S2-01 Baselines

Ablation conditions overlap with baseline definitions:

| S2-01 Baseline | S2-02 Ablation | Relationship |
|---------------|----------------|-------------|
| Baseline 1: Random Agent | Ablation 3, Run 8 (No Layers) | Similar but not identical (Random selects actions randomly; No Layers uses default MOVE_FORWARD) |
| Baseline 2: Rule-Only | Ablation 3, L0 Only | IDENTICAL — use same data |
| Baseline 3: RL Reference | N/A | External reference, not part of ablation |

**Data Reuse**: L0 Only episodes from Ablation 3 can serve as Baseline 2 data in S2-01, provided same seed set is used.

---

## Publication Framing

### Contribution to Paper

These ablation studies directly support the paper's core claims:
1. **RAG-based agent skill accumulation works** (Ablation 3: Full Stack > L0 Only)
2. **Document quality is a lever for improvement** (Ablation 1: Full > Degraded > Random)
3. **Scoring optimization matters** (Ablation 2: Optimized > Single-factor > Random)
4. **The multiplicative formula holds** (Cross-ablation: interaction effects present)

### Tables for Paper

Table: Ablation Study Results Summary
```
| Study | Condition | kill_rate (mean +/- SD) | Cohen's d vs Control | p-value |
|-------|-----------|------------------------|---------------------|---------|
| Doc Quality | Full RAG (A) | ... | — | — |
| | Degraded (B) | ... | ... | ... |
| | Random (C) | ... | ... | ... |
| Scoring | Optimized | ... | — | — |
| | Sim Only | ... | ... | ... |
| | Conf Only | ... | ... | ... |
| | Random | ... | ... | ... |
| Layers | Full Stack | ... | — | — |
| | L0+L1 | ... | ... | ... |
| | L0 Only | ... | ... | ... |
| | L2 Only | ... | ... | ... |
```

---

## Completion Criteria

- [x] Ablation 1 (Document Quality): manipulation, measurement, and analysis methods defined
- [x] Ablation 2 (Scoring Weights): weight conditions, extended exploration, regression plan defined
- [x] Ablation 3 (Layer Removal): 2^3 factorial design, all 8 conditions specified
- [x] DuckDB schema extensions specified (ablation_condition, ablation_study, decision_log table)
- [x] Execution order with decision gates defined
- [x] Contingency plans for each ablation failure scenario
- [x] Cross-ablation analysis plan specified
- [x] Integration with S2-01 baselines documented
- [x] Publication framing outlined
- [x] Lead review complete
