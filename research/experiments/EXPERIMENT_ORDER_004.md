# EXPERIMENT_ORDER_004: Document Quality Ablation

> **Hypothesis**: H-003 — Document quality significantly affects agent performance
> **DOE Type**: One-Way ANOVA (Phase 0/1 hybrid)
> **Status**: READY_FOR_EXECUTION
> **Created**: 2026-02-07
> **Estimated Runtime**: ~2-3 hours (3 conditions × 50 episodes)

---

## Hypothesis Linkage

**Hypothesis ID**: H-003 (from HYPOTHESIS_BACKLOG.md)

**Statement**: Strategy document quality has a monotonically positive effect on agent performance. Specifically: High Quality docs > Degraded docs > Random docs.

**Formal Statement**:

Let μ_H, μ_D, μ_R denote mean kill_rate under High Quality, Degraded, and Random document conditions respectively.

**Null Hypothesis**: H0: μ_H = μ_D = μ_R (document quality has no effect)

**Alternative Hypothesis**: H1: At least one pair differs

**Directional Prediction**: μ_H > μ_D > μ_R (dose-response relationship)

**Rationale**: Tests the "Document Quality" factor in the core formula: **Agent Skill = OpenSearch Document Quality × Rust Scoring Accuracy**. If document quality does not affect performance, the RAG feedback loop lacks justification.

**Source**: S2-02_CORE_ASSUMPTION_ABLATION.md, Ablation 1

---

## Research Question

Does strategy document quality causally affect agent performance?

**Primary Question**: Is Full RAG (high-quality documents) significantly better than Degraded or Random documents?

**Secondary Questions**:
1. Is there a dose-response relationship (Full > Degraded > Random)?
2. Does Degraded RAG provide any benefit over Random documents?
3. At what quality level do documents stop being useful?

---

## Experimental Design

### Design Type

**One-Way ANOVA with 3 Levels (Phase 0/1 hybrid)**

- 1 Categorical Factor (Document Quality)
- 3 Levels: Full, Degraded, Random
- Fully Randomized Design
- Fixed seed set across all conditions

### Factor

| Factor | Levels | Description |
|--------|--------|-------------|
| **Document Quality** | 1. Full RAG (Control)<br>2. Degraded Documents<br>3. Random Documents | Quality of strategy documents retrieved from OpenSearch |

### Conditions

| Condition | Label | Description | Manipulation |
|-----------|-------|-------------|--------------|
| **A** | Full RAG | Normal operation with LLM-refined strategy documents | No manipulation (control) |
| **B** | Degraded | Semantically corrupted documents (shuffled tags, noisy embeddings) | Shuffle `situation_tags`, add Gaussian noise to embeddings (σ=0.1) |
| **C** | Random | Structurally valid but semantically random documents | Replace OpenSearch index with random documents (random tags, actions, embeddings) |

---

## Document Manipulation Procedures

### Condition A: Full RAG (Control)

**Description**: Standard RAG operation with LLM-refined strategy documents.

**OpenSearch Index**: `opensearch_strategies` (default index)

**Document Properties**:
- `situation_tags`: Relevant to game situations (e.g., `["narrow_corridor", "multi_enemy"]`)
- `situation_embedding`: 768-dim Ollama embedding, semantically aligned
- `decision.tactic`: LLM-generated tactics (e.g., `"retreat_and_regroup"`)
- `decision.weapon`: Weapon recommendations (e.g., `"shotgun"`)
- `quality.success_rate`: Real success rates from agent episodes
- `quality.confidence_tier`: High/Medium/Low based on sample size

**No manipulation** — this is the baseline Full RAG configuration.

### Condition B: Degraded Documents

**Description**: Systematically corrupt semantic alignment while preserving document structure.

**OpenSearch Index**: `opensearch_degraded` (new index, populated from `opensearch_strategies`)

**Degradation Procedure**:

```python
def degrade_document(doc, all_tags_pool, embedding_std):
    """
    Corrupt semantic alignment while preserving structure.

    Args:
        doc: Original document from opensearch_strategies
        all_tags_pool: Set of all possible situation_tags
        embedding_std: Standard deviation of original embeddings (compute once)

    Returns:
        degraded: Document with corrupted semantics
    """
    degraded = doc.copy()

    # 1. Shuffle situation_tags (breaks semantic match)
    #    Replace original tags with random tags from pool
    degraded["situation_tags"] = random.sample(all_tags_pool, k=len(doc["situation_tags"]))

    # 2. Add Gaussian noise to situation_embedding
    #    noise_level = 0.1 * std(original_embeddings) — moderate corruption
    noise = np.random.normal(0, 0.1 * embedding_std, len(doc["situation_embedding"]))
    degraded["situation_embedding"] = doc["situation_embedding"] + noise

    # 3. Re-normalize to unit vector (preserve embedding norm)
    degraded["situation_embedding"] /= np.linalg.norm(degraded["situation_embedding"])

    # 4. Preserve decision and quality fields (actions unchanged, only retrieval broken)
    #    decision.tactic and decision.weapon UNCHANGED
    #    quality.success_rate and quality.confidence_tier UNCHANGED

    return degraded
```

**Rationale**: By corrupting tags and embeddings but preserving action recommendations, we test whether **semantic retrieval accuracy** matters. The agent still gets strategy recommendations, but they are mismatched to the current situation.

**Verification**:
- Measure mean cosine similarity between query and retrieved docs
- Expected: Full RAG sim > 0.7, Degraded sim ~ 0.3-0.5

### Condition C: Random Documents

**Description**: Replace OpenSearch index with structurally valid but semantically random documents.

**OpenSearch Index**: `opensearch_random` (new index, generated from scratch)

**Document Generation Procedure**:

```python
def create_random_document(doc_id, all_tags_pool, all_tactics, all_weapons, embedding_dim=768):
    """
    Generate structurally valid but semantically random strategy document.

    Args:
        doc_id: Unique document identifier
        all_tags_pool: Set of all possible situation_tags
        all_tactics: List of all tactics (e.g., ["aggressive_push", "defensive_hold", ...])
        all_weapons: List of all weapons (e.g., ["shotgun", "chaingun", "plasma", ...])
        embedding_dim: Embedding dimensionality (768 for Ollama)

    Returns:
        random_doc: Random document with valid structure
    """
    return {
        "doc_id": f"random_{doc_id}",
        "agent_id": "BASELINE",
        "generation": 0,
        "situation_embedding": random_unit_vector(embedding_dim),  # Uniform random direction
        "situation_tags": random.sample(all_tags_pool, k=3),       # 3 random tags
        "decision": {
            "tactic": random.choice(all_tactics),
            "weapon": random.choice(all_weapons)
        },
        "quality": {
            "success_rate": random.uniform(0.1, 0.9),              # Uniform [0.1, 0.9]
            "sample_size": random.randint(5, 50),                  # Uniform [5, 50]
            "confidence_tier": random.choice(["low", "medium", "high"])
        }
    }
```

**Index Population**:
- Generate N documents (same count as `opensearch_strategies`)
- Index into `opensearch_random`
- Agent queries this index instead of the real one

**Rationale**: Tests whether any strategy document is better than random advice. If Random performs as well as Full RAG, documents are not being used effectively.

**Verification**:
- Mean cosine similarity between query and retrieved docs
- Expected: Random sim ~ 0.0-0.2 (no semantic alignment)

---

## Scenario Configuration

### Game Environment

**Map**: VizDoom "Defend the Center" (default scenario)

**Difficulty**: Medium

**Enemy Configuration**: Standard spawn rates, mixed enemy types

**Time Limit**: 2100 tics (60 seconds) per episode

**Health/Ammo**: Default VizDoom starting conditions

### Agent Configuration

**Base Agent**: doom-agent-A (standard MD file structure)

**Strategy Profile**: Default balanced configuration
- play_style: balanced
- weapon_preference: balanced
- retreat_threshold: 0.5
- exploration_tendency: 0.5

**Decision Layers**: All layers active (L0+L1+L2)
- `skip_md_rules: false`
- `skip_duckdb_lookup: false`
- `skip_opensearch_query: false`

**OpenSearch Index Configuration**: Modified per condition
- Condition A: `opensearch_index: opensearch_strategies`
- Condition B: `opensearch_index: opensearch_degraded`
- Condition C: `opensearch_index: opensearch_random`

---

## Response Variables

### Primary Response

| Variable | Definition | Source | Target |
|----------|-----------|--------|--------|
| **kill_rate** | Total kills per episode | `episodes.total_kills` | Maximize |

### Secondary Responses

| Variable | Definition | Source | Target |
|----------|-----------|--------|--------|
| **survival_time** | Seconds survived | `episodes.survival_time` | Maximize |
| **retrieval_similarity** | Mean cosine similarity of top-K retrieved docs | `encounters.retrieval_similarity` aggregated | Higher = better semantic match |

### Diagnostic Variables (Manipulation Check)

| Variable | Definition | Source | Purpose |
|----------|-----------|--------|---------|
| **mean_retrieval_similarity** | Mean cosine sim across all L2 queries | `encounters.retrieval_similarity` where `decision_level=2` | Verify degradation worked |
| **rule_match_rate** | Fraction of decisions using L0 rules | `encounters.decision_level=0` count / total | Check if fallback to L0 increases |
| **l2_usage_rate** | Fraction of decisions using L2 | `encounters.decision_level=2` count / total | Check if L2 still used |

---

## Sample Size and Power

### Sample Size Calculation

**Design**: One-way ANOVA, 3 groups

**Target Effect Size**: f = 0.30 (medium effect)

**Significance Level**: α = 0.05

**Desired Power**: 1 - β = 0.80

**Required Sample Size**:
- G*Power calculation: n = 42 per group for f=0.30, α=0.05, power=0.80
- Safety margin: Use **n = 50 per group**
- Achieved power: ~0.87

**Total Episodes**: 3 conditions × 50 episodes = **150 episodes**

### Sample Allocation

```
All 3 conditions use IDENTICAL seed set (50 seeds).
Same seeds ensure within-subject comparisons are valid.
Differences are due to document quality only.
```

---

## Seed Set (n=50)

**Seed Generation Formula**: `seed_i = 7890 + i * 13` for `i = 0 to 49`

```
SEED_SET = [
  7890, 7903, 7916, 7929, 7942, 7955, 7968, 7981, 7994, 8007,
  8020, 8033, 8046, 8059, 8072, 8085, 8098, 8111, 8124, 8137,
  8150, 8163, 8176, 8189, 8202, 8215, 8228, 8241, 8254, 8267,
  8280, 8293, 8306, 8319, 8332, 8345, 8358, 8371, 8384, 8397,
  8410, 8423, 8436, 8449, 8462, 8475, 8488, 8501, 8514, 8527
]
```

**Seed Assignment**: Each condition uses all 50 seeds in episode order 1-50.

**Reproducibility Requirement**: [STAT:seed_set=fixed] [STAT:n=50]

---

## Randomized Run Order

Randomization performed to control for nuisance variables.

**Run Sequence** (3 conditions, each with 50 episodes):

| Order | Condition | Document Quality | Episodes |
|-------|-----------|-----------------|----------|
| 1 | Degraded (B) | Degraded | 1-50 (seeds 0-49) |
| 2 | Full RAG (A) | Full | 1-50 (seeds 0-49) |
| 3 | Random (C) | Random | 1-50 (seeds 0-49) |

**Execution Note**: Within each condition block, episodes are executed sequentially using seeds in order 0-49.

---

## Statistical Analysis Plan

### Primary Analysis: One-Way ANOVA

**Model**:
```
kill_rate ~ Document_Quality + error
```

**ANOVA Table**:

| Source | df | Expected F-test |
|--------|----|--------------------|
| Document Quality | 2 | Between-group variance |
| Error | 147 | Within-group variance |
| **Total** | **149** | |

**Significance Criterion**: [STAT:alpha=0.05]

**Effect Size**: Partial eta-squared (η²)

### Residual Diagnostics

**Normality Test**: Anderson-Darling test on residuals
- H0: Residuals are normally distributed
- Threshold: [STAT:p>0.05] for pass

**Equal Variance Test**: Levene's test
- H0: Variances are equal across conditions
- Threshold: [STAT:p>0.05] for pass

**Independence Check**: Run order plot inspection
- Visual check for systematic patterns

### Planned Contrasts (Dose-Response)

**Contrast 1: Full RAG vs. Degraded**
```
C1: μ_H - μ_D
Expected: [STAT:p<0.05], [STAT:ci=95%: positive interval]
```

**Contrast 2: Full RAG vs. Random**
```
C2: μ_H - μ_R
Expected: [STAT:p<0.01], [STAT:ci=95%: large positive interval]
```

**Contrast 3: Degraded vs. Random**
```
C3: μ_D - μ_R
Expected: [STAT:p<0.10], [STAT:ci=95%: may overlap zero or small positive]
```

### Post-Hoc Comparisons

**Method**: Tukey HSD for all pairwise comparisons

**Comparisons**: 3 choose 2 = 3 pairwise tests
- Full RAG vs. Degraded
- Full RAG vs. Random
- Degraded vs. Random

**Family-wise Error Rate**: Controlled at α = 0.05

**Confidence Intervals**: [STAT:ci=95%] for each pairwise difference

### Manipulation Check Analysis

**Verify degradation worked**:

```sql
-- Mean retrieval similarity per condition
SELECT
  ablation_condition,
  AVG(retrieval_similarity) as mean_sim,
  STDDEV(retrieval_similarity) as sd_sim,
  MIN(retrieval_similarity) as min_sim,
  MAX(retrieval_similarity) as max_sim
FROM encounters e
JOIN experiments ep ON e.episode_id = ep.episode_id
WHERE ep.experiment_id = 'DOE-004' AND e.decision_level = 2
GROUP BY ablation_condition;
```

**Expected**:
- Full RAG: mean_sim > 0.7
- Degraded: mean_sim ~ 0.3-0.5
- Random: mean_sim ~ 0.0-0.2

If manipulation check fails (e.g., Degraded sim > 0.6), re-examine degradation procedure.

---

## Expected Outcomes

### Performance Expectations

| Condition | Expected kill_rate (mean) | Expected retrieval_similarity (mean) | Rationale |
|-----------|---------------------------|--------------------------------------|-----------|
| A: Full RAG | 10-12 | > 0.7 | Semantically aligned documents |
| B: Degraded | 5-8 | 0.3-0.5 | Moderate corruption, some signal remains |
| C: Random | 3-5 | 0.0-0.2 | No semantic alignment, near Rule-Only baseline |

### Statistical Predictions

**Main Effect**: [STAT:f=F(2,147)>10.0] [STAT:p<0.001]

**Effect Size**: [STAT:eta2=partial η²>0.14] (large effect)

**Pairwise Comparisons**:
- Full vs. Degraded: [STAT:p<0.05] [STAT:effect_size=Cohen's d>0.5]
- Full vs. Random: [STAT:p<0.001] [STAT:effect_size=Cohen's d>1.0]
- Degraded vs. Random: [STAT:p<0.10] [STAT:effect_size=Cohen's d~0.3-0.5]

**Dose-Response**: Linear trend test should be significant [STAT:p<0.01]

---

## Trust Level Criteria

| Criterion | HIGH Trust | MEDIUM Trust | LOW Trust | UNTRUSTED |
|-----------|-----------|-------------|-----------|-----------|
| **p-value** | p < 0.01 | p < 0.05 | p < 0.10 | p ≥ 0.10 |
| **Effect Size** | η² > 0.14 (large) | η² > 0.06 (medium) | η² > 0.01 (small) | η² ≤ 0.01 |
| **Diagnostics** | All pass | 1 violation | 2 violations | > 2 violations |
| **Sample Size** | n = 150 | n = 150 | n < 100 | n < 50 |
| **Manipulation Check** | Pass (sim differences clear) | Pass | Marginal | Fail |

**Adoption Decision**:
- **HIGH trust**: Adopt finding to FINDINGS.md, update RESEARCH_LOG.md
- **MEDIUM trust**: Tentative adoption, plan follow-up experiment
- **LOW trust**: Exploratory only, do not adopt
- **UNTRUSTED**: Reject finding, investigate null result

---

## Execution Instructions

### For research-doe-runner

#### Pre-Execution Setup

1. **Populate Degraded Index** (`opensearch_degraded`):
   ```bash
   python scripts/degrade_documents.py \
     --input-index opensearch_strategies \
     --output-index opensearch_degraded \
     --noise-level 0.1 \
     --shuffle-tags
   ```

2. **Populate Random Index** (`opensearch_random`):
   ```bash
   python scripts/generate_random_documents.py \
     --output-index opensearch_random \
     --num-docs $(curl -s localhost:9200/opensearch_strategies/_count | jq '.count')
   ```

3. **Verify Indices**:
   ```bash
   curl -s localhost:9200/_cat/indices | grep opensearch
   ```

#### Execution Loop

1. **Read** this EXPERIMENT_ORDER_004.md
2. **For each condition** (A, B, C in randomized order):
   a. Modify `doom-agent-A/AGENT.md` OpenSearch configuration:
      - Condition A: `opensearch_index: opensearch_strategies`
      - Condition B: `opensearch_index: opensearch_degraded`
      - Condition C: `opensearch_index: opensearch_random`
   b. Restart `doom-agent-A` container (wait 5s for initialization)
   c. Execute 50 episodes using SEED_SET in order
   d. Record to DuckDB `experiments` table:
      - `experiment_id = "DOE-004"`
      - `ablation_condition = "{doc_full|doc_degraded|doc_random}"`
      - `ablation_study = "abl_1_doc_quality"`
      - `seed_set = SEED_SET`
   e. Record per-encounter `retrieval_similarity` to `encounters` table
3. **After all 150 episodes complete**:
   - Run manipulation check query (mean retrieval similarity per condition)
   - If manipulation check fails: STOP and investigate
4. **Handoff to research-analyst** for ANOVA execution

### Agent MD Configuration Examples

**Full RAG (Condition A)**:
```yaml
opensearch:
  index: opensearch_strategies
  host: localhost
  port: 9200
```

**Degraded (Condition B)**:
```yaml
opensearch:
  index: opensearch_degraded
  host: localhost
  port: 9200
```

**Random (Condition C)**:
```yaml
opensearch:
  index: opensearch_random
  host: localhost
  port: 9200
```

---

## Data Recording

### DuckDB Schema

**experiments table** (per-episode):
```sql
experiment_id: "DOE-004"
ablation_condition: VARCHAR  -- "doc_full", "doc_degraded", "doc_random"
ablation_study: "abl_1_doc_quality"
seed: INT  -- one of SEED_SET
episode_number: INT  -- 1 to 50
total_kills: INT
survival_time: FLOAT
ammo_used: INT
-- Additional columns as per standard schema
```

**encounters table** (per-encounter):
```sql
episode_id: VARCHAR (FK to experiments)
decision_level: INT  -- 0 (L0), 1 (L1), 2 (L2), -1 (fallback)
retrieval_similarity: FLOAT  -- cosine similarity of top-K docs (if L2 used)
decision_latency_ms: FLOAT
-- Additional columns as per standard schema
```

---

## Analysis Output

**Target Document**: `EXPERIMENT_REPORT_004.md`

**Contents**:
1. ANOVA table with F-statistic and p-value [STAT:f] [STAT:p]
2. Effect size (partial η²) [STAT:eta2]
3. Residual diagnostics results (normality, equal variance, independence)
4. Planned contrasts with confidence intervals [STAT:ci=95%]
5. Post-hoc pairwise comparisons (Tukey HSD)
6. Manipulation check table (mean retrieval similarity per condition)
7. Dose-response analysis (linear trend test)
8. Main effect plot (mean kill_rate per condition with error bars)
9. Recommendations: Trust level and adoption decision

**Trust Level Assignment**: Based on criteria table above

---

## Contingency: What if Document Quality Does NOT Matter?

**Scenario**: No significant difference between Full RAG, Degraded, and Random (p > 0.05).

**Implications**:
1. The RAG pipeline may not be retrieving situation-appropriate documents even under normal conditions
2. The Rust scoring weights may be compensating (choosing decent actions regardless of document relevance)
3. The agent may be primarily relying on Level 0 rules, rarely using Level 2 results

**Diagnostic Actions**:
1. Examine decision_level distribution in Full RAG: What fraction of decisions actually use L2?
   - If L2 usage < 10%: RAG system not being reached often enough → architecture problem
   - If L2 usage > 30% but quality does not matter: Scoring function may be ignoring document content → scoring bug
2. Run DOE-003 (Layer Ablation) to isolate the mechanism if not already completed
3. Subgroup analysis: Does document quality matter only in specific encounter types (narrow corridors, multi-enemy)?

**Recovery Plan**:
- If retrieval itself works (high similarity) but performance unchanged: Investigate whether tactics in documents are actually better than random
- Worst case: RAG pipeline redesign, starting from embedding model quality
- Consider: Document quality may require larger sample size to detect → increase n to 100 per condition

---

## Timeline

**Estimated Execution Time**:
- Setup: 1 hour (degrade + random index population, verification)
- Execution: 2-3 hours (3 conditions × 50 episodes × ~60s/episode)
- Analysis: 1-2 hours (ANOVA, diagnostics, plots)
- Reporting: 1 hour (EXPERIMENT_REPORT_004.md generation)

**Total**: ~5-7 hours

---

## Integration with Other Experiments

### Cross-References

- **DOE-003** (Layer Ablation): Must complete first. Only proceed with DOE-004 if Full Stack validated.
- **Baseline 2** (from S2-01): Random documents should perform near L0 Only baseline.

### Dependency Chain

```
DOE-003 (Layer Ablation) → Decision Gate → PROCEED
  ↓
DOE-004 (Document Quality) ← You are here
  ↓
If HIGH/MEDIUM trust → Adopt finding, proceed to DOE-005
```

---

## Completion Criteria

- [x] Hypothesis H-003 linked to HYPOTHESIS_BACKLOG.md
- [x] One-way ANOVA design specified with 3 conditions
- [x] Document manipulation procedures detailed (degradation + random generation)
- [x] Seed set generated (n=50, fixed)
- [x] Randomized run order specified
- [x] Response variables defined (primary + secondary + diagnostic)
- [x] Sample size justified with power analysis [STAT:n=150] [STAT:power≈0.87]
- [x] Statistical analysis plan specified (ANOVA, diagnostics, contrasts, post-hoc)
- [x] Manipulation check query specified
- [x] Trust level criteria defined
- [x] Execution instructions for research-doe-runner provided
- [x] DuckDB data recording schema specified
- [x] Expected outcomes and predictions documented
- [x] Contingency plan for null result documented
- [x] EXPERIMENT_REPORT_004.md output specification provided

---

**Document Status**: READY_FOR_EXECUTION

**Next Steps**:
1. research-doe-runner → Execute DOE-004 as specified
2. research-analyst → Perform ANOVA and generate EXPERIMENT_REPORT_004.md
3. research-pi → Review report, assign trust level, update FINDINGS.md if HIGH/MEDIUM trust
