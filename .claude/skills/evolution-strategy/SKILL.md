---
name: evolution-strategy
description: Evolutionary optimization strategy for agent generation lifecycle, selection, crossover, mutation, and diversity
user-invocable: false
---

# Evolution Strategy Skill

Evolutionary optimization strategy for evolving game agent populations across generations. Covers the full lifecycle: evaluation, parent selection, crossover, mutation, elitism, and diversity preservation.

## Generation Lifecycle

```
Generation N
    |
    v
[Evaluate] Run DOE experiments, collect metrics for all agents
    |
    v
[Select Parents] TOPSIS/AHP ranking -> top agents become parents
    |
    v
[Crossover] Blend parent MD DNA parameters to create offspring
    |
    v
[Mutate] Add controlled perturbation to offspring parameters
    |
    v
[Elitism] Preserve top N agents unchanged into next generation
    |
    v
[Create Offspring] Combine elite + crossed + mutated agents
    |
    v
[Validate] Ensure all agents have valid parameter ranges
    |
    v
Generation N+1
```

### Generation Record

```yaml
generation:
  id: GEN-005
  parent_generation: GEN-004
  population_size: 8
  elite_count: 2
  offspring_count: 6
  mutation_rate: 0.15
  mutation_scale: 0.10
  crossover_method: weighted_blend
  selection_method: topsis
  timestamp: 2026-02-07T14:30:00Z
```

## Parent Selection via TOPSIS/AHP

### Multi-Criteria Evaluation

Each agent is evaluated on multiple response variables:

```yaml
criteria:
  kill_rate:
    weight: 0.30
    direction: maximize
    description: "Kills per game tick (normalized)"

  survival_time:
    weight: 0.25
    direction: maximize
    description: "Ticks alive before death"

  damage_taken:
    weight: 0.15
    direction: minimize
    description: "Total damage received"

  ammo_efficiency:
    weight: 0.15
    direction: maximize
    description: "Kills per ammo unit consumed"

  exploration:
    weight: 0.15
    direction: maximize
    description: "Map coverage percentage"
```

### Selection Process

1. Compute TOPSIS closeness coefficient for each agent
2. Rank agents by closeness (descending)
3. Select top K agents as parents (K = population_size / 2, minimum 2)
4. Assign selection probability proportional to closeness coefficient

```
Agent rankings (TOPSIS):
  Agent_3: C = 0.82  --> Parent (probability 0.30)
  Agent_1: C = 0.71  --> Parent (probability 0.26)
  Agent_5: C = 0.65  --> Parent (probability 0.24)
  Agent_7: C = 0.55  --> Parent (probability 0.20)
  Agent_2: C = 0.43  --> Not selected
  Agent_4: C = 0.38  --> Not selected
  Agent_6: C = 0.31  --> Not selected
  Agent_8: C = 0.22  --> Not selected
```

### AHP Weight Calibration

Re-calibrate TOPSIS weights using AHP when:
- Phase transition occurs (different objectives at different phases)
- Dominant failure mode changes (FMEA update)
- Research PI explicitly requests weight change

## Crossover: Blend MD DNA Parameters

### DNA Representation

Agent "DNA" is the set of tunable parameters in the agent's config.md:

```yaml
agent_dna:
  retreat_threshold: 0.40      # [0.0, 1.0]
  ammo_conservation: 0.55      # [0.0, 1.0]
  exploration_priority: 0.50   # [0.0, 1.0]
  aggression_level: 0.60       # [0.0, 1.0]
  health_caution: 0.45         # [0.0, 1.0]
  weapon_switch_threshold: 0.30 # [0.0, 1.0]
  enemy_distance_preference: 0.50 # [0.0, 1.0] (0=melee, 1=ranged)
  item_priority: 0.50          # [0.0, 1.0] (0=weapons, 1=health)
```

### Weighted Blend Crossover

For two parents P1 and P2 with TOPSIS scores C1 and C2:

```
offspring_param = alpha * P1_param + (1 - alpha) * P2_param

where alpha = C1 / (C1 + C2)   (proportional to parent fitness)
```

Example:
```
P1 (C=0.82): retreat_threshold = 0.35
P2 (C=0.65): retreat_threshold = 0.55

alpha = 0.82 / (0.82 + 0.65) = 0.558

offspring: retreat_threshold = 0.558 * 0.35 + 0.442 * 0.55
         = 0.195 + 0.243 = 0.438
```

### Multi-Parent Crossover

When more than 2 parents are selected, use weighted average:

```
offspring_param = sum(C_i * P_i_param) / sum(C_i)  for all parent i
```

### Uniform Crossover (Alternative)

For each parameter, randomly choose from one parent:

```
For each parameter:
  if random() < alpha:
    offspring_param = P1_param
  else:
    offspring_param = P2_param
```

Use uniform crossover when blend produces too much convergence.

## Mutation

### Gaussian Mutation

Add random perturbation to offspring parameters:

```
mutated_param = param + N(0, sigma * scale)

where:
  sigma = mutation_scale (base noise level)
  scale = temperature factor (decreases over generations)
```

### Temperature Schedule

```
temperature(gen) = T_initial * decay^gen

T_initial = 1.0
decay = 0.95

Gen 1:  T = 1.00  (high exploration)
Gen 5:  T = 0.77
Gen 10: T = 0.60
Gen 20: T = 0.36
Gen 50: T = 0.08  (low exploration, mostly exploitation)
```

### Mutation Rate

Probability that each parameter gets mutated:

```
mutation_rate = base_rate * temperature

base_rate = 0.20 (20% of parameters mutated)

Gen 1:  effective rate = 0.20
Gen 10: effective rate = 0.12
Gen 50: effective rate = 0.02
```

### Boundary Enforcement

After mutation, clamp parameters to valid ranges:

```
mutated_param = max(lower_bound, min(upper_bound, mutated_param))
```

For parameters near boundaries, use reflected mutation:
```
if mutated_param > upper:
  mutated_param = upper - (mutated_param - upper)
if mutated_param < lower:
  mutated_param = lower + (lower - mutated_param)
```

### Adaptive Mutation

Increase mutation when population diversity drops:

```
if diversity_index < diversity_threshold:
  mutation_scale *= 2.0    # boost exploration
  mutation_rate *= 1.5

if diversity_index > 2 * diversity_threshold:
  mutation_scale *= 0.5    # reduce exploration
  mutation_rate *= 0.75
```

## Elitism

### Preserve Top Agents

Copy the best N agents directly to next generation without modification:

```yaml
elitism:
  count: 2              # number of elite agents
  selection: topsis_rank # use TOPSIS ranking
  modification: none     # no crossover or mutation
```

### Elitism Strategy

```
Population size: 8
Elite count: 2 (25%)
Offspring from crossover: 4
Offspring from mutation-only: 2

Next generation composition:
  [Elite 1] = Best agent from current gen (unchanged)
  [Elite 2] = Second best agent (unchanged)
  [Offspring 1] = Crossover(Parent1, Parent2) + Mutation
  [Offspring 2] = Crossover(Parent1, Parent3) + Mutation
  [Offspring 3] = Crossover(Parent2, Parent3) + Mutation
  [Offspring 4] = Crossover(Parent1, Parent4) + Mutation
  [Mutant 1]   = Clone(Parent1) + Heavy Mutation
  [Mutant 2]   = Clone(Parent3) + Heavy Mutation
```

### Elitism Size Guidelines

| Population | Elite Count | Ratio |
|-----------|-------------|-------|
| 4         | 1           | 25%   |
| 8         | 2           | 25%   |
| 16        | 3-4         | 19-25%|
| 32        | 5-8         | 16-25%|

Too many elites: premature convergence
Too few elites: loss of good solutions

## Diversity Preservation

### Distance Metric

Euclidean distance between agent DNA vectors:

```
d(A, B) = sqrt(sum((A_i - B_i)^2)) / sqrt(num_params)

Normalized to [0, 1] range.
```

### Population Diversity Index

Average pairwise distance across all agents:

```
diversity = (2 / (N * (N-1))) * sum(d(A_i, A_j)) for all i < j
```

### Minimum Diversity Threshold

```yaml
diversity:
  threshold: 0.10          # minimum acceptable diversity index
  check_frequency: every_generation
  action_on_low: boost_mutation
```

### Crowding Distance (NSGA-II inspired)

For maintaining spread across objective space:

```
For each agent:
  crowding_distance = sum over each objective:
    (neighbor_above - neighbor_below) / (max - min of objective)

Prefer agents with larger crowding distance (more unique)
```

### Diversity Injection

When diversity drops below threshold despite adaptive mutation:

1. Replace worst 1-2 agents with random configurations
2. Increase mutation scale by 3x for one generation
3. Switch to uniform crossover temporarily
4. Re-seed from historical best agents (different generations)

## Fitness Landscape Tracking

### Generation Statistics

Track per generation:

```yaml
generation_stats:
  gen_id: GEN-005
  best_fitness: 0.82       # best TOPSIS score
  mean_fitness: 0.58       # mean TOPSIS score
  worst_fitness: 0.22      # worst TOPSIS score
  std_fitness: 0.18        # standard deviation
  diversity_index: 0.15    # population diversity
  num_improved: 5          # agents better than previous gen best
  convergence_rate: 0.03   # change in mean fitness from previous gen
```

### Convergence Detection

```
Population has converged when:
  1. diversity_index < 0.05 for 3+ consecutive generations
  2. convergence_rate < 0.01 for 5+ consecutive generations
  3. best_fitness has not improved for 10+ generations

On convergence:
  - If good solution found: stop evolution, report final results
  - If suboptimal: restart with higher diversity (re-seed)
  - Consider Phase transition to RSM for fine-tuning
```

### Fitness History

```sql
CREATE TABLE generation_history (
  gen_id TEXT PRIMARY KEY,
  parent_gen_id TEXT,
  best_fitness REAL,
  mean_fitness REAL,
  worst_fitness REAL,
  std_fitness REAL,
  diversity_index REAL,
  temperature REAL,
  mutation_rate REAL,
  mutation_scale REAL,
  elite_count INTEGER,
  timestamp TIMESTAMP
);
```

## Phase-Specific Evolution

### Early Phase (Generations 1-10): Exploration Heavy

```yaml
early_phase:
  temperature: 1.0 - 0.60
  mutation_rate: 0.20 - 0.15
  mutation_scale: 0.15 - 0.10
  crossover: weighted_blend
  elite_ratio: 0.125 (1 of 8)
  focus: "Discover promising regions of parameter space"
```

### Middle Phase (Generations 11-30): Balanced

```yaml
middle_phase:
  temperature: 0.60 - 0.20
  mutation_rate: 0.15 - 0.08
  mutation_scale: 0.10 - 0.05
  crossover: weighted_blend
  elite_ratio: 0.25 (2 of 8)
  focus: "Refine promising configurations"
```

### Late Phase (Generations 31+): Exploitation Heavy

```yaml
late_phase:
  temperature: 0.20 - 0.05
  mutation_rate: 0.08 - 0.02
  mutation_scale: 0.05 - 0.01
  crossover: weighted_blend with high alpha bias
  elite_ratio: 0.25-0.375 (2-3 of 8)
  focus: "Fine-tune best configurations"
```

### Phase Transition Triggers

```
Early -> Middle:
  - diversity_index stabilizes above threshold
  - clear leader(s) emerged (best >> mean)
  - 10+ generations completed

Middle -> Late:
  - convergence_rate < 0.02 for 5 generations
  - best_fitness plateau detected
  - diversity approaching minimum threshold
  - 30+ generations completed
```

## Output: Generation Report

```markdown
# Generation Report: GEN-005

## Population
- Size: 8 agents
- Elite: 2 (Agent_3, Agent_1)
- New offspring: 4 (crossover + mutation)
- Mutants: 2 (heavy mutation)

## Fitness Summary
| Metric | Value |
|--------|-------|
| Best   | 0.82 (Agent_3) |
| Mean   | 0.58 |
| Worst  | 0.22 (Agent_8) |
| Std    | 0.18 |
| Diversity | 0.15 |

## Parent Selection (TOPSIS)
[Ranking table]

## Crossover Details
[Parent pairs and offspring parameters]

## Mutation Applied
[Parameters mutated, old/new values]

## Phase: Middle (Gen 11-30)
- Temperature: 0.45
- Mutation rate: 0.12
- Convergence rate: 0.02

## Next Steps
- Continue middle phase evolution
- Monitor diversity (currently healthy at 0.15)
- Agent_8 consistently worst - consider replacement with random seed
```
