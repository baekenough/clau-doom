# [SHOULD] HUD Statusline Rules

> **Priority**: SHOULD - Recommended for visibility
> **ID**: R012

## Purpose

Display real-time status information during agent operations for improved visibility and progress tracking.

## Format

```
─── [Agent] {name} | [Progress] {n}/{total} | [Parallel] {count} ───
```

## Research-Specific Format Extensions

```
─── [Agent] {name} | [Progress] {n}/{total} | [Experiment] {DOE-ID} | [Phase] {phase} ───
```

```
─── [Agent] {name} | [Generation] {gen}/{max} | [Fitness] {best_fitness} ───
```

## Update Triggers

| Trigger | Description |
|---------|-------------|
| Agent activation | When an agent starts handling a task |
| Task start | When a specific task begins execution |
| Task complete | When a task finishes (success or failure) |
| Parallel spawn | When parallel instances are created |
| Parallel complete | When parallel instances finish |
| **Experiment phase change** | When DOE phase transitions (0→1→2→3) |
| **Generation progress** | When evolution algorithm completes a generation |
| **Run completion** | When an experiment run finishes |

## Components

| Component | Description | Example |
|-----------|-------------|---------|
| Agent | Active agent name | `research-pi` |
| Model | Model used (for parallel) | `opus` |
| Progress | Task progress (current/total) | `2/5` |
| Parallel | Parallel instance count | `3` |
| **Experiment** | Active experiment ID | `DOE-042` |
| **Phase** | Current DOE phase | `Phase 1` |
| **Generation** | Evolution generation | `Gen 3/10` |
| **Fitness** | Best fitness score | `0.82` |

## Display Rules

### Single Agent

```
─── [Agent] research-pi | [Progress] 1/3 ───
```

### With Parallel Execution (Model Display REQUIRED)

```
─── [Agent] research-orchestrator | [Progress] 0/4 | [Parallel] 4 ───

Instances:
  [1] Task(research-analyst):opus → ANOVA for DOE-042
  [2] Task(research-doe-runner):sonnet → Execute DOE-043
  [3] Task(research-viz-specialist):haiku → Generate plots
  [4] Task(doom-metrics-collector):haiku → Collect episode data
```

### With Experiment Context

```
─── [Agent] research-doe-runner | [Progress] 5/8 | [Experiment] DOE-042 | [Phase] 1 ───
```

### With Generation Progress

```
─── [Agent] research-evolution-mgr | [Generation] 3/10 | [Fitness] 0.82 | [Phase] 3 ───
```

### Completion

```
─── [Agent] research-analyst | [Progress] 5/5 | [Experiment] DOE-042 | [Done] ───
```

## Implementation

Status updates via stderr to avoid output pollution:

```bash
echo "─── [Agent] $AGENT | [Progress] $PROGRESS | [Experiment] $DOE_ID ───" >&2
```

## Research-Specific Examples

### Experiment Execution Progress

```
─── [Agent] research-doe-runner | [Progress] 3/8 | [Experiment] DOE-042 | [Phase] 1 ───

Current Run:
  Factors: memory=0.7, strength=0.5
  Episodes: 15/30 complete
  Elapsed: 12m 30s
  Estimated remaining: 12m 30s
```

### ANOVA Analysis Progress

```
─── [Agent] research-analyst | [Progress] 2/4 | [Experiment] DOE-042 ───

Steps:
  [✓] ANOVA table computed
  [✓] Residual diagnostics
  [→] Effect size calculation
  [ ] Power analysis
```

### Evolution Progress

```
─── [Agent] research-evolution-mgr | [Generation] 5/10 | [Fitness] 0.85 | [Phase] 3 ───

Population: 50 genomes
Mutations: 12 this generation
Best genome: {memory: 0.82, strength: 0.68, curiosity: 0.45}
```

### Literature Review Progress

```
─── [Agent] research-literature-mgr | [Progress] 3/10 | [Phase] 0 ───

Papers reviewed: 3/10
Relevant: 2 (RL in FPS, Memory-based exploration)
Citations extracted: 15
```

## Integration with Other Rules

| Rule | Integration |
|------|-------------|
| R007 (Agent ID) | HUD complements agent identification |
| R008 (Tool ID) | HUD shows overall progress, tool ID shows specific operations |
| R009 (Parallel) | HUD displays parallel instance count |
| R100 (Experiment Integrity) | HUD shows experiment context (DOE-ID, phase) |
| R101 (PI Boundary) | HUD shows which agent is executing (PI vs executor) |

## When to Display

| Situation | Display HUD |
|-----------|-------------|
| Single file operation | No (too brief) |
| Multi-step task | Yes |
| Parallel execution | Yes |
| Long-running operations | Yes |
| **Experiment execution** | **Yes** |
| **Statistical analysis** | **Yes** |
| **Evolution runs** | **Yes** |
| **Multi-run DOE** | **Yes** |

## Hook Usage

The HUD statusline is implemented as an inline hook in `.claude/hooks/hooks.json` (PreToolUse → Task matcher).

The hook automatically displays subagent details when the Task tool is used:

```
─── [Spawn] {subagent_type}:{model} | {description} ───
─── [Resume] {subagent_type}:{model} | {description} ───
```

### Examples

```
─── [Spawn] research-doe-runner:sonnet | Execute DOE-042 ───
─── [Spawn] research-analyst:opus | ANOVA for DOE-042 ───
─── [Spawn] research-evolution-mgr:sonnet | Run Generation 1-10 ───
─── [Resume] research-pi:opus | Interpret DOE-042 results ───
```

### Fields Displayed

| Field | Source | Purpose |
|-------|--------|---------|
| `subagent_type` | Task tool parameter | Which agent is running |
| `model` | Task tool parameter | Which model (opus/sonnet/haiku) |
| `description` | Task tool parameter | What the agent is doing (max 40 chars) |

## Research-Specific HUD Patterns

### Phase Transition Display

```
─── [Phase Transition] Phase 1 → Phase 2 ───

Trigger: 3/3 key factors identified
New Focus: Interaction effects
Next Experiment: DOE-043 (2x3 factorial)
```

### Multi-Run Experiment Display

```
─── [Experiment] DOE-042 | Run 5/8 | Episode 15/30 ───

Run 5 Config:
  memory: 0.7
  strength: 0.5
  seed: 9999 (current episode)

Overall Progress: 135/240 episodes (56%)
```

### Parallel Run Execution Display

```
─── [Agent] research-doe-runner | [Parallel] 3 | [Experiment] DOE-042 ───

Instances:
  [1] Task(doom-agent-A):sonnet → Run 1 (memory=0.5, strength=0.3)
  [2] Task(doom-agent-B):sonnet → Run 2 (memory=0.7, strength=0.3)
  [3] Task(doom-agent-C):sonnet → Run 3 (memory=0.9, strength=0.3)

Overall: 45/240 episodes complete (19%)
```
