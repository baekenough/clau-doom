# [SHOULD] Ecomode Rules

> **Priority**: SHOULD - Recommended for token efficiency
> **ID**: R013

## Purpose

Reduce token usage and improve efficiency during batch operations and parallel execution.

## Activation Conditions

Ecomode is automatically activated when:

```yaml
conditions:
  - 4+ parallel tasks spawned
  - Batch operations requested
  - Near compaction threshold (80%+ context usage)
  - Explicit user request: "ecomode on"
  - Long experiment execution (8+ runs)
  - Multi-generation evolution (10+ generations)
```

## Behaviors

### 1. Compact Output Format

When ecomode is active, parallel agents return:

```yaml
format:
  - status: success | failed | partial
  - summary: 1-2 sentences max
  - key_data: essential results only

skip:
  - Intermediate steps
  - Verbose explanations
  - Repeated context
  - Full file contents (use paths instead)
  - Detailed ANOVA tables (show F and p only)
  - Full residual diagnostics (show pass/fail only)
```

### 2. Aggregation Format

Orchestrator aggregates results in compact format:

```
[Batch Complete] {n}/{total}
├── {agent}: {icon} {summary}
├── {agent}: {icon} {summary}
└── {agent}: {icon} {summary}
```

Icons:
- ✓ success
- ✗ failed
- ⚠ partial/warning

### 3. Result Compression

```yaml
compress:
  - File lists → count only unless < 5 files
  - Error traces → first and last 3 lines
  - Code snippets → path:line reference only
  - Long outputs → truncate with "[truncated]"
  - ANOVA tables → F-stat and p-value only
  - Residual diagnostics → pass/fail summary
  - Episode data → aggregate statistics only
```

## Orchestrator Ecomode Config

```yaml
ecomode:
  enabled: true
  threshold: 4           # Activate when >= 4 parallel tasks
  result_format: summary # summary | full
  max_result_length: 200 # characters per result
```

## Research-Specific Ecomode

### Experiment Execution (Normal Mode)

```
┌─ Agent: research-doe-runner (research)
├─ Model: sonnet
└─ Task: Executing DOE-042

Reading EXPERIMENT_ORDER_042.md...
[research-doe-runner][sonnet] → Read: EXPERIMENT_ORDER_042.md

Parsing design matrix...
- Factor 1: Memory [0.5, 0.7, 0.9]
- Factor 2: Strength [0.3, 0.5]
- Total runs: 6 (2x3 factorial)
- Episodes per run: 30
- Total episodes: 180

Generating seed set (n=180)...
[42, 1337, 2023, 7890, 9999, 1111, 5555, 8888, 3333, 6666, ...]

Injecting factors for Run 1/6...
[research-doe-runner][sonnet] → Edit: doom-agent-A/AGENT.md
Setting memory=0.5, strength=0.3

Restarting container doom-agent-A...
[research-doe-runner][sonnet] → Bash: docker restart doom-agent-A
Container restarted successfully

Executing Run 1/6 (30 episodes)...
[Progress] Episode 1/30 (seed: 42)
[Progress] Episode 2/30 (seed: 1337)
...
[Progress] Episode 30/30 (seed: 6666)

Recording Run 1 to DuckDB...
[research-doe-runner][sonnet] → Bash: duckdb insert...

[Done] Run 1/6 complete
Average kills: 42.3, Average survival: 180.5s

[... repeats for Runs 2-6 ...]
```

### Experiment Execution (Ecomode)

```
[research-doe-runner] ✓ DOE-042 complete: 6 runs, 180 episodes, data in DuckDB
```

### ANOVA Analysis (Normal Mode)

```
┌─ Agent: research-analyst (research)
├─ Model: opus
└─ Task: Analyzing DOE-042

Reading data from DuckDB...
[research-analyst][opus] → Bash: duckdb query...
Retrieved 180 episodes

Building ANOVA model...
Factors: Memory (3 levels), Strength (2 levels)
Response: kill_efficiency

Computing ANOVA table...

Source          | SS      | df  | MS      | F      | p-value | partial η²
----------------|---------|-----|---------|--------|---------|------------
Memory          | 1234.56 | 2   | 617.28  | 9.45   | 0.003   | 0.18
Strength        | 456.78  | 2   | 228.39  | 3.50   | 0.036   | 0.07
Memory*Strength | 234.56  | 4   | 58.64   | 0.90   | 0.468   | 0.04
Error           | 5678.90 | 174 | 32.63   |        |         |
Total           | 7604.80 | 182 |         |        |         |

Running residual diagnostics...
1. Normality (Anderson-Darling): p=0.42 → PASS
2. Equal variance (Levene): p=0.18 → PASS
3. Independence (run order plot): No pattern → PASS

Computing effect sizes...
- Memory: partial η² = 0.18 (large effect)
- Strength: partial η² = 0.07 (medium effect)
- Interaction: partial η² = 0.04 (small effect)

Performing power analysis...
- Memory: 1-β = 0.92 (excellent)
- Strength: 1-β = 0.68 (adequate)
- Interaction: 1-β = 0.45 (low, but effect is small)

Generating EXPERIMENT_REPORT_042.md...
[research-analyst][opus] → Write: EXPERIMENT_REPORT_042.md

[Done] Analysis complete
```

### ANOVA Analysis (Ecomode)

```
[research-analyst] ✓ DOE-042 analyzed: Memory F(2,174)=9.45 p=0.003, Strength F(2,174)=3.50 p=0.036, diagnostics PASS, report written
```

### Parallel Experiment Execution (Normal Mode)

```
─── [Agent] research-orchestrator | [Progress] 0/3 | [Parallel] 3 ───

Spawning parallel executors for DOE-042, DOE-043, DOE-044...

[Instance 1] Task(research-doe-runner):sonnet → Execute DOE-042
[Instance 2] Task(research-doe-runner):sonnet → Execute DOE-043
[Instance 3] Task(research-doe-runner):sonnet → Execute DOE-044

[Progress] ████████░░░░ 2/3

[Instance 1] Task(research-doe-runner):sonnet ✓ DOE-042 complete: 180 episodes
[Instance 2] Task(research-doe-runner):sonnet ✓ DOE-043 complete: 240 episodes
[Instance 3] Task(research-doe-runner):sonnet ⚠ DOE-044 partial: 200/300 episodes (agent-C crashed)

[Summary] 2/3 complete, 1 partial (see DOE-044 logs)
```

### Parallel Experiment Execution (Ecomode)

```
[Parallel Complete] 3/3
├── [research-doe-runner] ✓ DOE-042: 180 episodes
├── [research-doe-runner] ✓ DOE-043: 240 episodes
└── [research-doe-runner] ⚠ DOE-044: partial (200/300, crash)
```

## Implementation Notes

### For Orchestrator

```yaml
responsibilities:
  - Detect ecomode activation conditions
  - Instruct spawned agents to use compact format
  - Aggregate results in batch format
  - Track token savings
```

### For Worker Agents

```yaml
when_ecomode_active:
  - Return status + summary only
  - Skip intermediate progress updates
  - Use references instead of full content
  - Compress error messages
  - ANOVA: F and p only, skip full table
  - Diagnostics: pass/fail only, skip details
```

## Override

User can disable ecomode:
- "ecomode off"
- "verbose mode"
- "show full details"
- "full ANOVA table"
- "detailed diagnostics"

## Benefits

1. **Token Efficiency**: 60-80% reduction in batch operations
2. **Faster Response**: Less output processing
3. **Better Overview**: Aggregated results at a glance
4. **Context Preservation**: More room for actual work

## Research-Specific Benefits

1. **Multi-Run Experiments**: Drastically reduces verbosity for 8+ run DOEs
2. **Evolution Runs**: 10 generations compressed to progress summary
3. **Parallel Analysis**: Multiple ANOVA results aggregated cleanly
4. **Long Sessions**: Preserves context for multi-phase experiments
