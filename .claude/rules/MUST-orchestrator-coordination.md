# [MUST] Orchestrator Coordination Rules

> **Priority**: MUST - ENFORCED for multi-agent tasks
> **ID**: R010
> **Violation**: Direct agent execution without orchestrator = Rule violation

## CRITICAL

**The MAIN CONVERSATION is the sole orchestrator. It uses routing skills to delegate tasks to specialized subagents.**

### Flat Architecture (MANDATORY)

```
╔══════════════════════════════════════════════════════════════════╗
║  NEW ARCHITECTURE: FLAT, NO HIERARCHY                            ║
║                                                                   ║
║  Main Conversation (orchestrator)                                ║
║       │                                                          ║
║       ├─ Uses routing skills:                                    ║
║       │  • research-lead-routing (research tasks)                ║
║       │  • dev-lead-routing (development tasks)                  ║
║       │  • secretary-routing (system/agent tasks)                ║
║       │                                                          ║
║       └─ Spawns subagents (Task tool):                           ║
║          ├─ research-pi, research-analyst (research agents)      ║
║          ├─ lang-python-expert, lang-r-expert (language experts) ║
║          └─ mgr-creator, mgr-gitnerd (manager agents)            ║
║                                                                   ║
║  IMPORTANT: Subagents CANNOT spawn other subagents               ║
║            Only main conversation can spawn subagents            ║
╚══════════════════════════════════════════════════════════════════╝
```

### Session Continuity (MANDATORY)

```
╔══════════════════════════════════════════════════════════════════╗
║  AFTER SESSION RESTART / CONTEXT COMPACTION:                     ║
║                                                                   ║
║  1. Re-read CLAUDE.md and rules IMMEDIATELY                      ║
║  2. Agent delegation rules STILL APPLY                           ║
║  3. Main conversation uses routing skills to identify agents     ║
║  4. Spawn subagents with Task tool for actual work               ║
║                                                                   ║
║  WRONG after session restart:                                    ║
║    Main conversation → directly runs ANOVA/creates DOE           ║
║                                                                   ║
║  CORRECT after session restart:                                  ║
║    Main conversation → Task(research-analyst) → ANOVA            ║
║    Main conversation → Task(research-pi) → DOE design            ║
╚══════════════════════════════════════════════════════════════════╝
```

### Routing Logic (MANDATORY)

```
╔══════════════════════════════════════════════════════════════════╗
║  HOW TO ROUTE TASKS                                              ║
║                                                                   ║
║  Task Domain                    → Routing Skill → Agent          ║
║  ──────────────────────────────────────────────────────────────  ║
║  DOE design/planning            → research-lead-routing → research-pi ║
║  Statistical analysis/ANOVA     → research-lead-routing → research-analyst ║
║  Data cleaning/processing       → research-lead-routing → research-data-engineer ║
║  Python/R code development      → dev-lead-routing → lang-*-expert ║
║  Agent creation/updates         → secretary-routing → mgr-creator ║
║  Git operations                 → secretary-routing → mgr-gitnerd ║
║  System verification            → secretary-routing → mgr-sauron ║
║                                                                   ║
║  Routing skills contain the logic for:                           ║
║  • Which agent to use for which task                             ║
║  • When to spawn multiple agents in parallel                     ║
║  • How to aggregate results                                      ║
╚══════════════════════════════════════════════════════════════════╝
```

### Routing Skills

| Routing Skill | Manages | Handles |
|---------------|---------|---------|
| **research-lead-routing** | research-pi, research-analyst, research-data-engineer | DOE design, statistical analysis, data processing |
| **dev-lead-routing** | lang-python-expert, lang-r-expert | Code development, script optimization |
| **secretary-routing** | mgr-creator, mgr-updater, mgr-gitnerd, mgr-sauron | Agent management, git operations, verification |

```
Multi-agent detection (handled by routing skills):
- Task spans multiple experiments (batch ANOVA)
- Task requires different expertise (DOE + analysis + code)
- Task involves batch operations (multiple data files)

If multi-agent needed → Spawn multiple subagents in parallel
```

## Coordination Flow

```
CORRECT (Flat Architecture):
User Request
    │
    ▼
┌─────────────────────────────────┐
│  Main Conversation               │
│  - Analyzes task via routing     │
│  - Identifies required agents    │
│  - Plans execution               │
└─────────────┬───────────────────┘
              │
    ┌─────────┼─────────┐
    ▼         ▼         ▼
[research-analyst-1] [research-analyst-2] [research-analyst-3]
(spawned via Task tool)
    │         │         │
    └─────────┼─────────┘
              ▼
┌─────────────────────────────────┐
│  Main Conversation               │
│  - Aggregates results            │
│  - Reports to user               │
└─────────────────────────────────┘

WRONG (Hierarchical):
User Request
    │
    ▼
[research-pi] → spawns → [research-analyst] → spawns → [lang-python-expert]
(Subagents cannot spawn other subagents)

WRONG (No coordination):
User Request
    │
    ▼
[Agent-1] → [Agent-2] → [Agent-3]
(Sequential execution without planning)
```

## Main Conversation Responsibilities

```yaml
before_execution:
  - Analyze user request
  - Apply routing skill (research-lead/dev-lead/secretary)
  - Identify required agents
  - Plan execution order (parallel vs sequential)
  - Announce coordination plan

during_execution:
  - Spawn subagent instances via Task tool
  - Monitor progress
  - Handle failures
  - Coordinate dependencies

after_execution:
  - Aggregate results
  - Report summary to user
  - Clean up resources
```

## Announcement Format

Main conversation MUST announce before delegating:

```
[Routing] Using research-lead-routing for batch ANOVA

[Plan]
├── Agent 1: research-analyst → ANOVA exp 021
├── Agent 2: research-analyst → ANOVA exp 022
└── Agent 3: research-analyst → ANOVA exp 023

[Execution] Parallel (3 instances)

Spawning subagents...
```

## When to Spawn Subagents

| Scenario | Spawn Subagents? |
|----------|------------------|
| Single experiment analysis | Maybe (if specialized agent needed) |
| Batch experiment analysis | **Yes** (parallel instances) |
| DOE design + analysis | **Yes** (different agents) |
| Data cleaning + ANOVA | **Yes** (sequential with different agents) |
| Multiple DOE designs | **Yes** (parallel instances) |

## Exception: Simple Tasks

Subagent NOT required for:
- Reading files for analysis
- Simple file searches
- Direct questions answered by main conversation

For specialized work, ALWAYS delegate to appropriate subagent.

## CRITICAL: Use Specialized Research Agents

**When a task matches a research agent's purpose, you MUST delegate to that agent.**

```
╔══════════════════════════════════════════════════════════════════╗
║  RESEARCH AGENT DELEGATION (MANDATORY)                           ║
║                                                                   ║
║  Task Type              → Required Agent                         ║
║  ─────────────────────────────────────────────────               ║
║  DOE design             → research-pi                            ║
║  Statistical analysis   → research-analyst                       ║
║  Data cleaning          → research-data-engineer                 ║
║  Python/R development   → lang-python-expert/lang-r-expert       ║
║  Agent creation         → mgr-creator                            ║
║  Git operations         → mgr-gitnerd                            ║
║                                                                   ║
║  DO NOT use general-purpose agents for these tasks.              ║
║  DO NOT have main conversation do the work directly.             ║
╚══════════════════════════════════════════════════════════════════╝
```

### Correct Delegation Pattern

```
User: "3-factor CCD 설계해줘"

WRONG:
  Main conversation → Task(general-purpose) → creates DOE directly

CORRECT:
  Main conversation → Task(research-pi) → follows DOE design workflow
```

### Research Agent Reference

| Agent | File | Purpose |
|-------|------|---------|
| research-pi | .claude/agents/research-pi.md | DOE design, experimental planning |
| research-analyst | .claude/agents/research-analyst.md | Statistical analysis, ANOVA, modeling |
| research-data-engineer | .claude/agents/research-data-engineer.md | Data cleaning, validation, processing |

### Manager Agents Reference

| Agent | File | Purpose |
|-------|------|---------|
| mgr-creator | .claude/agents/mgr-creator.md | Create new agents |
| mgr-updater | .claude/agents/mgr-updater.md | Update external sources |
| mgr-gitnerd | .claude/agents/mgr-gitnerd.md | Git operations (commit, push, PR) |
| mgr-sauron | .claude/agents/mgr-sauron.md | Full R017 verification |

## CRITICAL: All File Modifications Must Be Delegated

```
╔══════════════════════════════════════════════════════════════════╗
║  FILE EDITING = SPECIALIZED WORK = MUST DELEGATE                 ║
║                                                                   ║
║  The orchestrator must NEVER use Edit/Write/Bash directly        ║
║  to modify files. This applies to ALL file types:                ║
║  - DOE designs (DOE_DESIGN_*.md)                                 ║
║  - Experiment reports (REPORT_*.md)                              ║
║  - Statistical scripts (*.R, *.py)                               ║
║  - Data files (*.csv - processed only)                           ║
║  - Config files (CLAUDE.md, etc.)                                ║
║                                                                   ║
║  WRONG:                                                          ║
║    Orchestrator → Write(DOE_DESIGN_023.md)                       ║
║    Orchestrator → Edit(analysis_script.R)                        ║
║                                                                   ║
║  CORRECT:                                                        ║
║    Orchestrator → Task(research-pi) → creates DOE design         ║
║    Orchestrator → Task(lang-r-expert) → edits R script           ║
║                                                                   ║
║  Only READ operations (Read, Glob, Grep) may be used directly   ║
║  by the orchestrator. All mutations go through subagents.        ║
╚══════════════════════════════════════════════════════════════════╝
```

## CRITICAL: Sub-agent Model Specification

```
╔══════════════════════════════════════════════════════════════════╗
║  TASK TOOL MODEL PARAMETER (RECOMMENDED)                         ║
║                                                                   ║
║  Claude Code Task tool supports `model` parameter to specify     ║
║  which model the sub-agent should use.                           ║
║                                                                   ║
║  Available models:                                                ║
║    - opus   : Complex reasoning, DOE design, statistical modeling║
║    - sonnet : Balanced performance (default)                     ║
║    - haiku  : Fast, simple tasks, data validation                ║
║    - inherit: Use parent conversation's model                    ║
║                                                                   ║
║  Usage:                                                          ║
║    Task(                                                         ║
║      subagent_type: "research-pi",                               ║
║      prompt: "Design 3-factor CCD",                              ║
║      model: "opus"                                               ║
║    )                                                             ║
╚══════════════════════════════════════════════════════════════════╝
```

### Model Selection by Task Type

| Task Type | Recommended Model | Reason |
|-----------|-------------------|--------|
| DOE design | `opus` | Complex optimization required |
| Statistical modeling | `opus` | Deep reasoning for model selection |
| Standard ANOVA | `sonnet` | Balanced performance |
| Data validation | `haiku` | Fast, simple checks |
| Data cleaning | `sonnet` | Moderate complexity |
| Script optimization | `sonnet` | Code generation |

### Model Selection by Agent Type

| Agent Category | Model | Examples |
|----------------|-------|----------|
| Research design | `opus` | research-pi (DOE), complex planning |
| Research analysis | `opus` | research-analyst (statistical modeling) |
| Data processing | `sonnet` | research-data-engineer |
| Simple validation | `haiku` | Data quality checks |
| Code development | `sonnet` | lang-python-expert, lang-r-expert |

## CRITICAL: Git Operations Delegation

```
╔══════════════════════════════════════════════════════════════════╗
║  GIT OPERATIONS MUST BE DELEGATED TO mgr-gitnerd                 ║
║                                                                   ║
║  WRONG:                                                          ║
║    Main conversation → directly runs git commit/push             ║
║                                                                   ║
║  CORRECT:                                                        ║
║    Main conversation → Task(mgr-gitnerd) → git commit/push       ║
║                                                                   ║
║  mgr-gitnerd handles:                                            ║
║  ✓ git commit (with proper message format)                       ║
║  ✓ git push                                                      ║
║  ✓ git branch operations                                         ║
║  ✓ PR creation (gh pr create)                                    ║
║                                                                   ║
║  This ensures:                                                   ║
║  - Consistent commit message format                              ║
║  - Safety checks before destructive operations                   ║
║  - Proper Co-Authored-By attribution                             ║
╚══════════════════════════════════════════════════════════════════╝
```

## Research Workflow Examples

### DOE Design Workflow
```
User: "온도, 압력, 시간 3개 인자로 CCD 설계해줘"

Main conversation:
  ├─ Analyzes request
  ├─ Routing: research-lead-routing
  ├─ Agent: research-pi
  └─ Spawns: Task(research-pi):opus
      │
      └─ Creates DOE_DESIGN_024.md with:
         - 3 factors (Temperature, Pressure, Time)
         - 17 runs (8 factorial + 6 axial + 3 center)
         - Randomized experiment order

User receives: Korean explanation + English DOE design file
```

### Batch Analysis Workflow
```
User: "실험 021, 022, 023 ANOVA 분석해줘"

Main conversation:
  ├─ Analyzes request
  ├─ Routing: research-lead-routing
  ├─ Detects: 3 independent analyses → PARALLEL
  └─ Spawns 3 parallel instances:
      ├─ Task(research-analyst):opus → ANOVA exp 021
      ├─ Task(research-analyst):opus → ANOVA exp 022
      └─ Task(research-analyst):opus → ANOVA exp 023

Aggregates results:
  - Exp 021: 3 significant factors (p<0.001)
  - Exp 022: 2 significant factors (p<0.05)
  - Exp 023: 1 significant factor (p<0.01)

User receives: Korean summary + 3 English ANOVA reports
```

## Enforcement

```
Violation examples:
✗ Analyzing 3 experiments sequentially without parallelization
✗ Creating DOE design directly in main conversation
✗ Running ANOVA without delegating to research-analyst

Correct examples:
✓ Main conversation announces plan, spawns agents, aggregates results
✓ Clear execution plan with research agent assignments
✓ Progress updates during multi-experiment analysis
```
