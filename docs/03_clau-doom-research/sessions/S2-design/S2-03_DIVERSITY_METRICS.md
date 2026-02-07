# S2-03: Evolutionary Convergence/Diversity Metrics Design

> **Session**: S2 (Research Design Reinforcement)
> **Priority**: high
> **Dependencies**: None (S1-01 QD literature beneficial)
> **Status**: completed

---

## Purpose

No metrics currently exist to detect premature convergence or track strategy diversity across generations. This document defines 5 diversity/convergence metrics inspired by QD (Quality-Diversity) literature, maps them to DuckDB schemas, and establishes alert conditions.

---

## Metric 1: Strategy Distribution Entropy

### Definition

Shannon entropy of categorical strategy parameters across the agent population within a single generation. Measures how uniformly distributed agents are across strategy categories.

### Mathematical Definition

```
H(X) = -sum_{i=1}^{k} p_i * log2(p_i)

Where:
  k = number of distinct strategy categories
  p_i = proportion of agents using strategy category i
  H_max = log2(k)  (maximum entropy when uniform)
  H_normalized = H(X) / H_max  (0 to 1 scale)
```

### Measurement Targets

| Parameter | Categories | Example Values |
|-----------|------------|----------------|
| `play_style` | aggressive, balanced, defensive, stealth | Discrete |
| `weapon_preference` | shotgun_focus, chaingun_focus, balanced, plasma | Discrete |
| `retreat_threshold` | low (0-0.2), mid-low (0.2-0.4), mid (0.4-0.6), mid-high (0.6-0.8), high (0.8-1.0) | Continuous, discretized into 5 bins |
| `exploration_tendency` | low (0-0.33), medium (0.33-0.66), high (0.66-1.0) | Continuous, discretized into 3 bins |

### Composite Strategy Entropy

Compute entropy per parameter, then aggregate:

```
H_composite = (1/M) * sum_{m=1}^{M} H_normalized(X_m)

Where M = number of measured strategy parameters
```

### Interpretation

| H_normalized Range | Interpretation | Action |
|--------------------|----------------|--------|
| 0.8 - 1.0 | High diversity, healthy exploration | None |
| 0.5 - 0.8 | Moderate diversity, acceptable | Monitor |
| 0.2 - 0.5 | Low diversity, convergence in progress | Warning: increase exploration ratio |
| 0.0 - 0.2 | Near-total convergence | Alert: force diversity injection |

### Calculation Frequency

- **Per generation**: After all agents in generation N complete their episodes
- **Trigger**: Generation completion event

### Alert Conditions

| Condition | Threshold | Response |
|-----------|-----------|----------|
| Single-generation low entropy | H_normalized < 0.3 | Log warning |
| 3 consecutive generations declining | H_t < H_{t-1} < H_{t-2} | Increase exploration ratio from 30% to 50% |
| Entropy collapse | H_normalized < 0.1 | Emergency: inject 3 random strategy agents into next generation |

### Visualization

1. **Line chart**: H_normalized over generations (one line per parameter, one composite line)
2. **Stacked bar chart**: Strategy distribution per generation (shows category proportions shifting)
3. **Heatmap**: Parameter x Generation, cell color = proportion of dominant category

---

## Metric 2: Behavioral Coverage (MAP-Elites Inspired)

### Definition

Proportion of the discretized behavior space actually occupied by agents in the current generation. Behavior space is defined by two orthogonal behavioral descriptors extracted from gameplay data.

### Behavioral Descriptors

| Axis | Descriptor | Source | Discretization |
|------|-----------|--------|----------------|
| X | `aggression_level` | `encounters` table: (kills / total_encounters) per agent | 10 bins: [0.0-0.1, 0.1-0.2, ..., 0.9-1.0] |
| Y | `exploration_tendency` | `episodes` table: (unique_rooms_visited / total_rooms) per agent | 10 bins: [0.0-0.1, 0.1-0.2, ..., 0.9-1.0] |

### Mathematical Definition

```
Grid: G = N_x x N_y cells (default: 10 x 10 = 100 cells)

For each agent a in generation g:
  x_a = mean(kills / total_encounters) across all episodes
  y_a = mean(unique_rooms / total_rooms) across all episodes
  cell(a) = (floor(x_a * N_x), floor(y_a * N_y))

occupied_cells(g) = |{ cell(a) : a in generation g }|

Coverage(g) = occupied_cells(g) / (N_x * N_y)
```

### Extended Coverage: Temporal Tracking

```
cumulative_coverage(g) = |union_{t=1}^{g} { cell(a) : a in generation t }| / (N_x * N_y)

new_cells(g) = occupied_cells(g) - occupied_cells(g) intersect occupied_cells(g-1)
```

### Interpretation

| Coverage Range | Interpretation |
|----------------|----------------|
| > 0.5 | Excellent behavioral diversity |
| 0.3 - 0.5 | Good diversity |
| 0.15 - 0.3 | Moderate diversity, watch for decline |
| < 0.15 | Low diversity, most agents cluster in few behavioral niches |

### Calculation Frequency

- **Per generation**: After all episodes complete
- **Requires**: Aggregated episode data per agent

### Alert Conditions

| Condition | Threshold | Response |
|-----------|-----------|----------|
| Coverage drop | Coverage(g) < 0.8 * Coverage(g-1) | Warning: behavioral narrowing detected |
| Sustained low coverage | Coverage < 0.15 for 3 generations | Force niche-seeking mutations |
| Zero new cells | new_cells(g) = 0 for 2 generations | Inject random agents targeting empty niches |

### Visualization

1. **Grid heatmap**: 10x10 grid colored by occupancy (empty=gray, occupied=blue intensity by fitness)
2. **Coverage line chart**: Coverage(g) over generations
3. **Animated grid**: Generation-by-generation grid evolution (dashboard replay)
4. **Cumulative coverage curve**: Shows how fast the population explores behavior space

---

## Metric 3: QD-Score (Quality-Diversity Score)

### Definition

Sum of the best fitness value achieved in each occupied cell of the behavior grid. Captures both quality (high fitness) and diversity (many occupied cells) in a single scalar.

### Mathematical Definition

```
For behavior grid G with cells c_1, c_2, ..., c_K:

best_fitness(c) = max{ fitness(a) : cell(a) = c, a in generation g }
                  (undefined if cell c is unoccupied)

QD-Score(g) = sum_{c in occupied_cells(g)} best_fitness(c)

Where:
  fitness(a) = TOPSIS relative closeness C_i for agent a
             = d_i^- / (d_i^+ + d_i^-)
  Range: 0.0 to 1.0 per cell
  QD-Score range: 0.0 to N_x * N_y (theoretical maximum)
```

### TOPSIS Fitness Components

```
Criteria for fitness(a):
  kill_rate        (w=0.30, maximize)
  survival_time    (w=0.25, maximize)
  Cpk              (w=0.20, maximize)
  experiment_adopt (w=0.15, maximize)
  ammo_efficiency  (w=0.10, maximize)

TOPSIS normalization:
  r_ij = x_ij / sqrt(sum x_ij^2)
  v_ij = w_j * r_ij
  d_i^+ = euclidean_distance(v_i, A+)
  d_i^- = euclidean_distance(v_i, A-)
  C_i = d_i^- / (d_i^+ + d_i^-)
```

### Decomposition for Analysis

```
QD-Score(g) = occupied_cells(g) * mean_best_fitness(g)

This allows diagnosing:
  - QD-Score stagnant, coverage up, mean fitness down = diversity at cost of quality
  - QD-Score stagnant, coverage down, mean fitness up = quality at cost of diversity
  - QD-Score rising, both up = healthy evolution
```

### Calculation Frequency

- **Per generation**: After TOPSIS scores computed for all agents
- **Depends on**: Metric 2 (behavioral coverage grid) + TOPSIS scores

### Alert Conditions

| Condition | Threshold | Response |
|-----------|-----------|----------|
| QD-Score plateau | < 5% increase over 5 generations | Increase mutation strength |
| QD-Score decline | QD(g) < 0.9 * QD(g-1) | Investigate: quality loss or diversity loss? |
| Mean fitness declining while coverage rising | mean_best_fitness dropping > 10% | Elite preservation rate too low, increase to 20% |

### Visualization

1. **QD-Score line chart**: QD-Score(g) over generations with decomposition (coverage x mean fitness)
2. **Quality-Diversity tradeoff scatter**: X=coverage, Y=mean_best_fitness, each point = one generation
3. **Grid heatmap with fitness**: 10x10 grid, cell color = best fitness in that cell (white=empty)
4. **Pareto front**: Generations plotted showing quality-diversity tradeoff evolution

---

## Metric 4: Document Pool Diversity

### Definition

Diversity of strategy documents in OpenSearch, measured by the distribution of pairwise cosine distances between document embeddings. Detects whether the knowledge base is collapsing into redundant documents.

### Mathematical Definition

```
Let D = {d_1, d_2, ..., d_n} be document embeddings in OpenSearch (768-dim Ollama vectors)

Pairwise cosine distance:
  dist(d_i, d_j) = 1 - cos_sim(d_i, d_j)
                 = 1 - (d_i . d_j) / (||d_i|| * ||d_j||)

Mean pairwise distance:
  MPD(g) = (2 / n(n-1)) * sum_{i<j} dist(d_i, d_j)

Minimum spanning tree spread:
  MST_spread(g) = sum of edge weights in MST of distance matrix

Effective dimensionality (PCA):
  ED(g) = number of principal components explaining 90% variance
```

### Trust-Weighted Variant

Weight distances by document trust scores to focus on high-quality documents:

```
trust_weighted_MPD(g) = sum_{i<j} trust(d_i) * trust(d_j) * dist(d_i, d_j)
                        / sum_{i<j} trust(d_i) * trust(d_j)
```

### Measurement Scope

| Scope | Documents | Purpose |
|-------|-----------|---------|
| Active pool | Documents with trust_score > 0.3 | Current useful knowledge |
| Full pool | All documents | Total knowledge diversity |
| New documents | Added in last generation | Quality of new knowledge |

### Calculation Frequency

- **Per generation**: After knowledge curation step (research-rag-curator)
- **After document operations**: Bulk add, prune, or update

### Alert Conditions

| Condition | Threshold | Response |
|-----------|-----------|----------|
| MPD declining | MPD(g) < 0.85 * MPD(g-1) | Warning: documents becoming redundant |
| Low effective dimensionality | ED(g) < 5 | Knowledge base losing thematic diversity |
| Cluster collapse | > 80% documents in single cluster | Prune duplicates, seed new strategy categories |
| Trust concentration | > 60% of trust-weighted mass in < 20% of documents | Encourage exploration of underused strategies |

### Visualization

1. **MPD line chart**: Mean pairwise distance over generations
2. **t-SNE/UMAP scatter**: Document embeddings colored by trust_score, one plot per generation
3. **Cluster size distribution**: Bar chart of documents per cluster, per generation
4. **Effective dimensionality line chart**: ED(g) over generations

---

## Metric 5: Effective Mutation Rate

### Definition

Proportion of mutations (crossover + mutation operations) that produce meaningfully different behavior in the offspring. Distinguishes between genotypic change (MD file edits) and phenotypic change (actual behavioral difference in gameplay).

### Mathematical Definition

```
For parent p and child c in generation g:

Genotypic distance:
  geno_dist(p, c) = normalized_edit_distance(MD_params(p), MD_params(c))

  Where MD_params extracts numerical parameters from Strategy Profile:
    geno_dist = (1/K) * sum_{k=1}^{K} |param_k(p) - param_k(c)| / range_k

Phenotypic distance:
  pheno_dist(p, c) = euclidean_distance(behavior_vector(p), behavior_vector(c))

  Where behavior_vector = (aggression_level, exploration_tendency, mean_kill_rate,
                           mean_survival_time, ammo_efficiency)
  Normalized to [0,1] per dimension.

Effective mutation rate:
  EMR(g) = |{ (p,c) : pheno_dist(p,c) > delta }| / |{ (p,c) : all parent-child pairs }|

  Where delta = 0.1 (minimum meaningful behavioral change threshold)

Mutation efficiency:
  ME(g) = mean(pheno_dist(p,c)) / mean(geno_dist(p,c))

  ME > 1: Small genotypic changes cause large behavioral shifts (sensitive region)
  ME < 1: Large genotypic changes have little behavioral effect (plateau region)
```

### Component Tracking

| Component | Source | Measurement |
|-----------|--------|-------------|
| Parameter changes | Diff of parent/child MD files | Count of changed params, magnitude |
| Learned Rules changes | Diff of rules sections | Count added/deleted/modified |
| Strategy document changes | Cosine similarity of associated docs | Parent-child doc similarity |
| Behavioral outcome | Episode data comparison | Behavior vector distance |

### Calculation Frequency

- **Per generation**: After all offspring have completed their episodes
- **Per parent-child pair**: Immediately after each offspring evaluation

### Alert Conditions

| Condition | Threshold | Response |
|-----------|-----------|----------|
| Low EMR | EMR(g) < 0.1 for 3 generations | Mutations too weak, increase perturbation magnitude |
| Declining ME | ME(g) < 0.5 * ME(g-3) | Evolution hitting plateau, consider phase transition |
| EMR = 0 | No phenotypic change in any offspring | Critical: mutation operator broken or parameters at boundary |
| High geno, low pheno | geno_dist high but pheno_dist near 0 | Neutral mutations dominating, refocus on impactful parameters |

### Visualization

1. **EMR line chart**: Effective mutation rate over generations
2. **Scatter plot**: geno_dist vs pheno_dist per parent-child pair (reveals genotype-phenotype mapping)
3. **ME line chart**: Mutation efficiency over generations (detects plateaus)
4. **Parallel coordinates**: Show how specific parameter changes map to behavioral changes

---

## DuckDB Schema

```sql
-- Generation-level diversity metrics
CREATE TABLE generation_diversity (
    generation_id       INT NOT NULL,
    strategy_entropy    FLOAT,          -- H_composite (normalized, 0-1)
    behavioral_coverage FLOAT,          -- Coverage ratio (0-1)
    qd_score            FLOAT,          -- QD-Score (0 to grid_size)
    doc_pool_mpd        FLOAT,          -- Mean pairwise distance of doc embeddings
    doc_pool_ed         INT,            -- Effective dimensionality (PCA 90% variance)
    effective_mutation_rate FLOAT,       -- EMR (0-1)
    mutation_efficiency FLOAT,          -- ME (pheno/geno ratio)
    num_agents          INT,            -- Population size
    num_unique_strategies INT,          -- Distinct play_style count
    occupied_cells      INT,            -- Behavioral grid occupied cells
    total_cells         INT,            -- Behavioral grid total cells (default 100)
    cumulative_coverage FLOAT,          -- Cumulative coverage up to this generation
    measured_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (generation_id)
);

-- Per-parameter strategy distribution within a generation
CREATE TABLE generation_strategy_distribution (
    generation_id   INT NOT NULL,
    parameter_name  VARCHAR NOT NULL,   -- 'play_style', 'weapon_preference', 'retreat_threshold_bin', etc.
    parameter_value VARCHAR NOT NULL,   -- Discretized value label
    count           INT NOT NULL,       -- Number of agents with this value
    proportion      FLOAT NOT NULL,     -- count / total agents in generation
    entropy         FLOAT,              -- Per-parameter Shannon entropy (bits)
    entropy_normalized FLOAT,           -- Per-parameter normalized entropy (0-1)
    PRIMARY KEY (generation_id, parameter_name, parameter_value)
);

-- Behavioral grid archive (MAP-Elites style)
CREATE TABLE behavioral_grid (
    generation_id   INT NOT NULL,
    cell_x          INT NOT NULL,       -- Aggression bin index (0 to N_x-1)
    cell_y          INT NOT NULL,       -- Exploration bin index (0 to N_y-1)
    best_agent_id   VARCHAR,            -- Agent with best fitness in this cell
    best_fitness    FLOAT,              -- TOPSIS C_i of best agent
    agent_count     INT,                -- Number of agents in this cell
    mean_fitness    FLOAT,              -- Mean fitness of agents in this cell
    PRIMARY KEY (generation_id, cell_x, cell_y)
);

-- Parent-child mutation tracking
CREATE TABLE mutation_tracking (
    generation_id       INT NOT NULL,
    child_agent_id      VARCHAR NOT NULL,
    parent1_agent_id    VARCHAR,         -- First parent (crossover) or sole parent (mutation)
    parent2_agent_id    VARCHAR,         -- Second parent (crossover only, NULL for mutation)
    operation_type      VARCHAR NOT NULL, -- 'crossover', 'mutation', 'elite_copy'
    genotypic_distance  FLOAT,           -- Normalized parameter edit distance
    phenotypic_distance FLOAT,           -- Behavioral vector distance
    mutation_effective  BOOLEAN,         -- pheno_dist > delta
    params_changed      INT,             -- Count of parameters that changed
    rules_added         INT,             -- Learned rules added
    rules_removed       INT,             -- Learned rules removed
    PRIMARY KEY (generation_id, child_agent_id)
);

-- Convergence alert log
CREATE TABLE convergence_alerts (
    alert_id        INT PRIMARY KEY,
    generation_id   INT NOT NULL,
    metric_name     VARCHAR NOT NULL,    -- 'strategy_entropy', 'behavioral_coverage', etc.
    alert_level     VARCHAR NOT NULL,    -- 'warning', 'alert', 'critical'
    current_value   FLOAT,
    threshold_value FLOAT,
    message         VARCHAR,
    response_taken  VARCHAR,             -- Action taken in response
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at     TIMESTAMP            -- NULL if unresolved
);
```

---

## Premature Convergence Alert Conditions (Summary)

| Metric | Warning | Alert | Critical | Response |
|--------|---------|-------|----------|----------|
| Strategy Entropy | H_norm < 0.5 | 3 gen declining | H_norm < 0.1 | Increase exploration 30%->50%, inject random agents |
| Behavioral Coverage | Coverage < 0.8 * prev | Coverage < 0.15 for 3 gen | new_cells = 0 for 2 gen | Niche-seeking mutations, inject agents targeting empty cells |
| QD-Score | < 5% increase / 5 gen | QD decline > 10% | QD decline > 25% | Increase mutation strength, investigate quality vs diversity loss |
| Doc Pool Diversity | MPD declining | ED < 5 | > 80% in single cluster | Prune duplicates, seed new strategy categories |
| Effective Mutation Rate | EMR < 0.2 | EMR < 0.1 for 3 gen | EMR = 0 | Increase perturbation magnitude, check parameter boundaries |

### Automated Response Escalation

```
Level 1 (Warning):
  - Log to convergence_alerts table
  - Display on dashboard Evolution tab
  - PI notified in next RESEARCH_LOG entry

Level 2 (Alert):
  - All Level 1 actions
  - PI generates EXPERIMENT_ORDER for diversity recovery
  - Exploration ratio increased automatically (30% -> 50%)

Level 3 (Critical):
  - All Level 2 actions
  - Evolution paused pending PI review
  - Emergency diversity injection: 3 random agents added to next generation
  - Current generation marked in SPC control chart
```

---

## Dashboard Visualization Spec (Evolution Tab)

### Panel 1: Diversity Overview (Top Row)

```
Layout: 5 mini-charts in a row, one per metric
Type: Sparkline with current value displayed prominently
Update: Per generation
Color coding: Green (healthy) / Yellow (warning) / Red (alert)
```

### Panel 2: Behavioral Grid (Center Left)

```
Type: 10x10 heatmap
X-axis: Aggression level (0.0 to 1.0)
Y-axis: Exploration tendency (0.0 to 1.0)
Cell color: Best fitness (white=empty, blue gradient=occupied)
Annotation: Agent count per cell on hover
Controls: Generation slider to animate over time
```

### Panel 3: Entropy Breakdown (Center Right)

```
Type: Stacked area chart
X-axis: Generation
Y-axis: Normalized entropy (0-1)
Layers: One per strategy parameter (play_style, weapon_pref, etc.)
Overlay: Composite entropy as bold line
Reference lines: Warning (0.5) and Alert (0.3) thresholds
```

### Panel 4: QD-Score Decomposition (Bottom Left)

```
Type: Dual-axis line chart
X-axis: Generation
Left Y-axis: QD-Score (absolute)
Right Y-axis: Coverage (ratio) and Mean Best Fitness
Lines: QD-Score (bold), Coverage (dashed), Mean Fitness (dotted)
```

### Panel 5: Mutation Effectiveness (Bottom Right)

```
Type: Scatter plot with marginal histograms
X-axis: Genotypic distance
Y-axis: Phenotypic distance
Points: One per parent-child pair, colored by generation
Diagonal line: ME = 1 reference
Marginal histograms: Distribution of each distance
```

### Panel 6: Alert Timeline (Bottom Banner)

```
Type: Timeline / event strip
X-axis: Generation
Markers: Triangle icons at alert events, colored by severity
Tooltip: Alert details on hover
Filter: By metric type
```

---

## Integration with Existing Systems

### SPC Integration

- Strategy entropy tracked on X-bar/R control chart alongside kill_rate
- Western Electric Rules applied to entropy: 7-point run below center = convergence signal
- Cpk computed for entropy: Cpk < 1.0 = diversity process not capable

### FMEA Integration

- Add failure mode: "Premature convergence" to FMEA registry
- Severity: 8 (loss of evolutionary potential)
- Occurrence: Tracked via convergence_alerts frequency
- Detection: 3 (metrics provide early detection)
- RPN updated per generation

### TOPSIS Integration

- Add diversity_contribution criterion (w6) to TOPSIS evaluation
- diversity_contribution(a) = number of unique behavioral cells agent occupies
- Rewards agents that explore underrepresented niches

### Evolution Operator Integration

- When alerts fire, evolution operators adjust:
  - Crossover: Prefer parents from different behavioral niches
  - Mutation: Increase perturbation magnitude for low-EMR parameters
  - Elite: Cap elite preservation at 10% during convergence alerts

---

## Completion Criteria

- [x] 5 metrics defined with mathematical formulas
- [x] DuckDB schema with 5 tables (generation_diversity, generation_strategy_distribution, behavioral_grid, mutation_tracking, convergence_alerts)
- [x] Alert conditions with 3-level escalation
- [x] Dashboard visualization spec (6 panels)
- [x] Integration with SPC, FMEA, TOPSIS, and evolution operators
