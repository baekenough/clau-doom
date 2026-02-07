# [MUST] Parallel Execution Rules

> **Priority**: MUST - ENFORCED for 2+ independent tasks
> **ID**: R009
> **Violation**: Sequential execution of parallelizable tasks = Rule violation

## CRITICAL

**When 2 or more tasks are INDEPENDENT, they MUST be executed in parallel.**

```
╔══════════════════════════════════════════════════════════════════╗
║  ⚠️  ABSOLUTE RULE: 2+ INDEPENDENT TASKS = PARALLEL              ║
║                                                                   ║
║  If you are about to process 2 or more independent:              ║
║  - Experimental datasets                                         ║
║  - Statistical analyses                                          ║
║  - DOE designs                                                   ║
║  - Data processing scripts                                       ║
║  → STOP                                                          ║
║  → Use Task tool to spawn parallel agents                        ║
║  → Each agent handles a subset                                   ║
║                                                                   ║
║  NO EXCEPTIONS for:                                              ║
║  - Batch ANOVA across experiments                                ║
║  - Multiple DOE design generations                               ║
║  - Parallel data cleaning                                        ║
║  - Any multi-task research operation                             ║
║                                                                   ║
║  VIOLATION = Processing 2+ tasks sequentially                    ║
║              when tasks are independent                          ║
╚══════════════════════════════════════════════════════════════════╝
```

```
Detection criteria for parallel execution:
- Tasks don't share mutable state
- Tasks don't have sequential dependencies
- Tasks can complete independently

If ALL criteria met → MUST execute in parallel (max 4 instances)
```

### How to Detect Independent Tasks

```
Independent (MUST parallelize):
✓ "Analyze experiments 021, 022, 023" → 3 separate analyses
✓ "Create DOE designs for 3 studies" → 3 separate designs
✓ "Clean data from 4 batches" → 4 separate cleaning operations

Dependent (sequential OK):
✗ "Design experiment then analyze results" → analysis depends on design
✗ "Clean data then run ANOVA" → ANOVA depends on cleaned data
✗ "Read data then fit model" → modeling depends on data
```

Failure to parallelize independent tasks = Rule violation = Must be corrected.

### Self-Check Before Every Multi-Task Operation

```
╔══════════════════════════════════════════════════════════════════╗
║  BEFORE processing multiple tasks, ASK YOURSELF:                 ║
║                                                                   ║
║  1. Are these tasks independent of each other?                   ║
║     → YES: Use Task tool to spawn parallel agents                ║
║     → NO: Sequential is OK                                       ║
║                                                                   ║
║  2. Am I about to run the same analysis on 3+ datasets?         ║
║     → STOP. This is likely a violation.                         ║
║     → Spawn parallel research-analyst agents instead.            ║
║                                                                   ║
║  3. Are there domain-specific experts available?                 ║
║     → YES: Delegate to them (research-analyst, research-pi)      ║
║     → NO: Create general-purpose parallel agents                 ║
╚══════════════════════════════════════════════════════════════════╝
```

### Common Violations to Avoid

```
❌ WRONG: Analyzing datasets one by one
   Bash(Rscript anova_021.R) → Bash(Rscript anova_022.R) → Bash(Rscript anova_023.R)

✓ CORRECT: Spawn parallel agents
   Task(research-analyst → analyze exp 021)  ┐
   Task(research-analyst → analyze exp 022)  ├─ All in single message
   Task(research-analyst → analyze exp 023)  ┘

❌ WRONG: Creating DOE designs sequentially
   Write(DOE_024.md) → Write(DOE_025.md) → Write(DOE_026.md)

✓ CORRECT: Parallel DOE design
   Task(research-pi → "Create DOE for study A")  ┐
   Task(research-pi → "Create DOE for study B")  ├─ Parallel
   Task(research-pi → "Create DOE for study C")  ┘

❌ WRONG: Data cleaning in sequence
   Bash(python clean_batch1.py) → Bash(python clean_batch2.py) → ...

✓ CORRECT: Parallel data cleaning
   Task(research-data-engineer → batch1)  ┐
   Task(research-data-engineer → batch2)  ├─ Parallel
   Task(research-data-engineer → batch3)  │
   Task(research-data-engineer → batch4)  ┘

❌ WRONG: Single Task delegating to multiple analyses
   Task(research-lead → "coordinate 3 ANOVA analyses")

   This creates a SEQUENTIAL bottleneck inside the Task!

✓ CORRECT: Multiple Tasks in parallel, one per analysis
   Task(research-analyst → ANOVA exp 021)  ┐
   Task(research-analyst → ANOVA exp 022)  ├─ All spawned together
   Task(research-analyst → ANOVA exp 023)  ┘
```

### Parallel Task Spawning Rule

```
╔══════════════════════════════════════════════════════════════════╗
║  PARALLEL MEANS PARALLEL AT THE TOOL CALL LEVEL                  ║
║                                                                   ║
║  When spawning Tasks for parallel work:                          ║
║  - Each independent analysis = separate Task tool call           ║
║  - All Task calls in the SAME message = truly parallel           ║
║  - One Task that "coordinates" others = still sequential inside  ║
║                                                                   ║
║  Rule: If work can be split, split it into separate Tasks.       ║
╚══════════════════════════════════════════════════════════════════╝
```

### Large Task Decomposition (MANDATORY)

```
╔══════════════════════════════════════════════════════════════════╗
║  LARGE RESEARCH TASKS MUST BE SPLIT INTO PARALLEL SUB-TASKS      ║
║                                                                   ║
║  Before spawning a single large Task, ASK:                       ║
║                                                                   ║
║  1. Can this work be divided into independent parts?             ║
║     → Experiment 021, 022, 023 analyses                          ║
║     → Factor screening, optimization, validation                 ║
║     → Data cleaning, outlier detection, normalization            ║
║                                                                   ║
║  2. How many parallel slots available? (max 4)                   ║
║     → If 3 experiments, split into 3 parallel Tasks             ║
║     → Maximize parallelism to minimize total time                ║
║                                                                   ║
║  3. Is estimated Task duration > 5 minutes?                      ║
║     → MUST split if work is decomposable                        ║
║     → 20 min single Task → 5 min with 4 parallel Tasks          ║
╚══════════════════════════════════════════════════════════════════╝

Example - WRONG:
  Task("Run ANOVA on exp 021, 022, 023, 024")
  → Single agent works 20+ minutes sequentially

Example - CORRECT (4 parallel Tasks):
  Task(research-analyst → "ANOVA exp 021")  ┐
  Task(research-analyst → "ANOVA exp 022")  ├─ ~5 min total
  Task(research-analyst → "ANOVA exp 023")  │
  Task(research-analyst → "ANOVA exp 024")  ┘
```

## Purpose

Enable parallel execution of agents as separate instances to improve throughput for batch research operations and independent tasks.

## Core Concept

Each agent (except orchestrators) can be instantiated multiple times to work on independent tasks in parallel.

```
Agent (Template)
    │
    ├── Instance 1 → ANOVA on exp 021
    ├── Instance 2 → ANOVA on exp 022
    ├── Instance 3 → ANOVA on exp 023
    └── Instance 4 → ANOVA on exp 024
```

## Rules

### 1. Maximum Parallel Instances

```yaml
limit: 4
reason: Balance between throughput and resource usage
```

### 2. Exclusions

```yaml
not_parallelizable:
  - Main conversation (must remain singleton for coordination)

reason: |
  The main conversation orchestrates research workflow and must maintain
  a single point of coordination to prevent conflicts.
```

### 3. Instance Independence

```yaml
requirements:
  - Tasks must be independent (no shared state)
  - No cross-instance communication required
  - Each instance has isolated context
  - Separate data files (no concurrent writes to same file)
```

### 4. Subagent Visibility (MANDATORY)

```
╔══════════════════════════════════════════════════════════════════╗
║  TASK TOOL MUST USE SPECIFIC subagent_type (NOT general-purpose) ║
║                                                                   ║
║  When a specialized agent exists for the task:                   ║
║    → MUST use that agent's subagent_type                         ║
║    → DO NOT use "general-purpose" as a catch-all                 ║
║                                                                   ║
║  The HUD hook displays: [Spawn] {subagent_type}:{model} | {desc}║
║  Using "general-purpose" makes all spawns look identical.        ║
║                                                                   ║
║  WRONG:                                                          ║
║    Task(subagent_type: "general-purpose", desc: "Analyze exp")   ║
║    Task(subagent_type: "general-purpose", desc: "Analyze exp")   ║
║    → HUD shows: [Spawn] general-purpose:opus | Analyze exp      ║
║    → HUD shows: [Spawn] general-purpose:opus | Analyze exp      ║
║    → User cannot distinguish which is which                      ║
║                                                                   ║
║  CORRECT:                                                        ║
║    Task(subagent_type: "research-analyst", desc: "ANOVA exp 021")║
║    Task(subagent_type: "research-analyst", desc: "ANOVA exp 022")║
║    → HUD shows: [Spawn] research-analyst:opus | ANOVA exp 021   ║
║    → HUD shows: [Spawn] research-analyst:opus | ANOVA exp 022   ║
╚══════════════════════════════════════════════════════════════════╝
```

### 5. Model Specification (RECOMMENDED)

```
╔══════════════════════════════════════════════════════════════════╗
║  USE MODEL PARAMETER FOR COST/PERFORMANCE OPTIMIZATION           ║
║                                                                   ║
║  Task tool supports `model` parameter:                           ║
║                                                                   ║
║    Task(                                                         ║
║      subagent_type: "research-analyst",                          ║
║      prompt: "Run ANOVA on experiment 021",                      ║
║      model: "opus"  ← Specify model                              ║
║    )                                                             ║
║                                                                   ║
║  Model Selection:                                                ║
║    - opus   : Statistical modeling, complex DOE (expensive)      ║
║    - sonnet : Data processing, routine analysis (balanced)       ║
║    - haiku  : File validation, simple checks (fast, cheap)       ║
║                                                                   ║
║  Parallel Task Optimization:                                     ║
║    - Use haiku for data validation tasks                         ║
║    - Use sonnet for standard ANOVA/regression                    ║
║    - Use opus only for complex modeling/optimization             ║
╚══════════════════════════════════════════════════════════════════╝
```

Example with model specification:
```
# Parallel research tasks with appropriate models
Task(prompt: "Validate data quality", model: "haiku")           ┐
Task(prompt: "Run factorial ANOVA", model: "sonnet")            ├─ Optimized
Task(prompt: "Fit response surface model", model: "opus")       │
Task(prompt: "Optimize process parameters", model: "opus")      ┘
```

## Research-Specific Usage Patterns

### Batch Statistical Analysis

```
User: "실험 021, 022, 023 ANOVA 분석해줘"

Main conversation:
  │
  ├── [exp 021] research-analyst instance #1
  ├── [exp 022] research-analyst instance #2
  └── [exp 023] research-analyst instance #3

Execution: Parallel (3 instances)
```

### Batch DOE Design

```
User: "3개 연구 프로젝트 DOE 설계해줘"

Main conversation:
  │
  ├── [project A] research-pi instance #1
  ├── [project B] research-pi instance #2
  └── [project C] research-pi instance #3

Execution: Parallel (3 instances)
```

### Parallel Data Processing

```
User: "4개 배치 데이터 클리닝해줘"

Main conversation:
  │
  ├── [batch 1] research-data-engineer instance #1
  ├── [batch 2] research-data-engineer instance #2
  ├── [batch 3] research-data-engineer instance #3
  └── [batch 4] research-data-engineer instance #4

Execution: Parallel (4 instances)
```

## Display Format

When parallel execution occurs, MUST display `Task({subagent_type}):{model}` format:

```
┌─ Agent: main-conversation (orchestrator)
└─ Task: Batch ANOVA analysis

[Parallel] Spawning 3 instances...

[Instance 1] Task(research-analyst):opus → ANOVA exp 021
[Instance 2] Task(research-analyst):opus → ANOVA exp 022
[Instance 3] Task(research-analyst):opus → ANOVA exp 023

[Progress] ████████████ 2/3

[Instance 1] Task(research-analyst):opus ✓ ANOVA complete (3 significant factors)
[Instance 2] Task(research-analyst):opus ✓ ANOVA complete (2 significant factors)
[Instance 3] Task(research-analyst):opus ✓ ANOVA complete (1 significant factor)

[Summary] 3/3 analyses completed successfully
```

### Display Format Rules

```
╔══════════════════════════════════════════════════════════════════╗
║  PARALLEL AGENT DISPLAY FORMAT (MANDATORY)                       ║
║                                                                   ║
║  When announcing parallel agents, MUST show:                     ║
║                                                                   ║
║    Task({subagent_type}):{model}                                 ║
║                                                                   ║
║  Examples:                                                       ║
║    [Instance 1] Task(research-analyst):opus → ANOVA exp 021      ║
║    [Instance 2] Task(research-pi):opus → CCD design study A      ║
║    [Instance 3] Task(research-data-engineer):sonnet → Clean batch 1 ║
║    [Instance 4] Task(lang-python-expert):sonnet → Script optimization ║
║                                                                   ║
║  The subagent_type MUST match the Task tool's subagent_type      ║
║  parameter. Custom names are NOT allowed.                        ║
╚══════════════════════════════════════════════════════════════════╝
```

## Benefits

1. **Throughput**: N experiments analyzed in ~1/N time
2. **Efficiency**: Better resource utilization
3. **User Experience**: Faster batch research operations
4. **Scalability**: Handles large experimental campaigns
5. **Cost Optimization**: Parallel haiku tasks vs sequential opus
