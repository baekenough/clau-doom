---
name: research-lead-routing
description: Routes research tasks by experiment lifecycle phase to the correct research agent
user-invocable: false
---

# Research Lead Routing Skill

## Purpose

Routes research tasks to appropriate research agents based on experiment lifecycle phase. This skill contains the coordination logic for orchestrating research agents across hypothesis formation, DOE execution, statistical analysis, RAG curation, evolution management, and paper writing.

## Research Agents Under Management

| Agent | Purpose | Phase |
|-------|---------|-------|
| research-pi | Hypothesis formation, DOE design, EXPERIMENT_ORDER output | Design |
| research-doe-runner | Experiment execution, parallel runs, measurement collection | Execution |
| research-analyst | ANOVA, p-values, SPC, FMEA, TOPSIS analysis | Analysis |
| research-rag-curator | RAG document management, OpenSearch curation, trust scores | Knowledge |
| research-evolution-mgr | Generation transitions, genome management, fitness tracking | Evolution |
| research-paper-writer | NeurIPS/ICML paper sections, LaTeX formatting | Publication |

## Keyword Mapping

| Keyword | Agent |
|---------|-------|
| "hypothesis", "experiment design", "DOE design", "factor", "EXPERIMENT_ORDER" | research-pi |
| "run experiment", "execute", "DOE run", "parallel runs", "measurement" | research-doe-runner |
| "ANOVA", "p-value", "statistical", "SPC", "FMEA", "TOPSIS", "significance" | research-analyst |
| "RAG", "document", "OpenSearch", "strategy doc", "trust score", "curation" | research-rag-curator |
| "evolution", "generation", "genome", "fitness", "mutation", "crossover" | research-evolution-mgr |
| "paper", "NeurIPS", "ICML", "LaTeX", "abstract", "related work", "section" | research-paper-writer |

## Command Routing

```
Research Request -> Phase Detection -> Research Agent

Hypothesis/Design   -> research-pi (opus)
Execution/Runs      -> research-doe-runner (sonnet)
Analysis/Stats      -> research-analyst (sonnet)
RAG/Documents       -> research-rag-curator (sonnet)
Evolution/Genomes   -> research-evolution-mgr (sonnet)
Paper/Publication   -> research-paper-writer (sonnet)
Full lifecycle      -> Sequential pipeline (PI -> Runner -> Analyst -> Curator -> Evolution)
```

## Routing Rules

### 1. Experiment Lifecycle Routing

```
1. Parse user request and identify experiment phase
2. Select appropriate research agent:
   - Hypothesis/design keywords -> research-pi
   - Execution/run keywords -> research-doe-runner
   - Analysis/statistical keywords -> research-analyst
   - RAG/document keywords -> research-rag-curator
   - Evolution/generation keywords -> research-evolution-mgr
   - Paper/publication keywords -> research-paper-writer
3. Spawn Task with selected agent role
4. Monitor execution
5. Report result to user
```

### 2. Full Experiment Pipeline

When user requests a complete experiment cycle:

```
1. Task(research-pi) -> EXPERIMENT_ORDER.yaml
2. Task(research-doe-runner) -> Run measurements
3. Task(research-analyst) -> ANOVA results
4. Task(research-rag-curator) -> Strategy documents
5. Task(research-evolution-mgr) -> Next generation
6. Aggregate and report
```

Note: Pipeline steps are sequential (each depends on previous output).

### 3. Parallel Execution Opportunities

Independent analysis tasks can run in parallel:

```
Example: "Analyze last 3 experiments"

Route (parallel):
  Task(research-analyst) -> Experiment 1 ANOVA
  Task(research-analyst) -> Experiment 2 ANOVA
  Task(research-analyst) -> Experiment 3 ANOVA

Aggregate results
```

## Sub-agent Model Selection

### Model Mapping

| Agent | Recommended Model | Reason |
|-------|-------------------|--------|
| research-pi | `opus` | Complex hypothesis reasoning, DOE design requires deep thinking |
| research-doe-runner | `sonnet` | Execution coordination, standard operations |
| research-analyst | `sonnet` | Statistical analysis, structured output |
| research-rag-curator | `sonnet` | Document management, embedding coordination |
| research-evolution-mgr | `sonnet` | Generation management, balanced complexity |
| research-paper-writer | `sonnet` | Academic writing, structured sections |

### Task Call Examples

```
# Hypothesis formation (requires deep reasoning)
Task(
  subagent_type: "general-purpose",
  prompt: "Form hypothesis and create EXPERIMENT_ORDER following research-pi workflow",
  model: "opus"
)

# Standard DOE execution
Task(
  subagent_type: "general-purpose",
  prompt: "Execute DOE runs following research-doe-runner workflow",
  model: "sonnet"
)

# Statistical analysis
Task(
  subagent_type: "general-purpose",
  prompt: "Run ANOVA analysis following research-analyst workflow",
  model: "sonnet"
)
```

## Parallel Execution

Following R009:
- Maximum 4 parallel instances
- Only for independent analysis/curation tasks
- Pipeline steps remain sequential
- Coordinate cross-agent data handoffs

Example:
```
User: "Analyze experiments 12, 13, 14 and update RAG docs"

Detection:
  - Experiments 12, 13, 14 -> research-analyst (parallel)
  - RAG update -> research-rag-curator (after analysis)

Route (parallel):
  Task(research-analyst) -> Experiment 12
  Task(research-analyst) -> Experiment 13
  Task(research-analyst) -> Experiment 14

Then (sequential):
  Task(research-rag-curator) -> Update docs with findings
```

## Display Format

```
[Analyzing] Detected: Experiment lifecycle phase - Analysis
[Routing] research-analyst:sonnet -> ANOVA for experiment 42

[Delegating] research-analyst:sonnet -> Experiment 42 analysis
[Delegating] research-rag-curator:sonnet -> Document update

[Progress] 1/2 agents completed

[Summary]
  Analysis: p < 0.001 for aggression factor
  RAG: 3 strategy documents updated

Research task completed.
```

## Integration with Research Rules

| Rule | Integration |
|------|-------------|
| R100 (Experiment Integrity) | Ensure seeds fixed, statistical evidence markers present |
| R101 (PI Boundary) | PI outputs EXPERIMENT_ORDER only, never executes directly |
| R102 (Research Audit Trail) | Maintain hypothesis->order->report->findings chain |

## Usage

This skill is NOT user-invocable. It should be automatically triggered when the main conversation detects research intent.

Detection criteria:
- User mentions experiment, hypothesis, DOE, ANOVA
- User requests analysis of game performance
- User discusses generation evolution
- User wants paper section drafted
- Research-related keywords detected
