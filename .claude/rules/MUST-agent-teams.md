# [MUST] Agent Teams Active Usage

> **Priority**: MUST - ABSOLUTE, Principle Zero
> **ID**: R000-0
> **Principle**: Agent Teams First

## CRITICAL

**All multi-agent research tasks MUST use Agent Teams. Simple Task spawns are ONLY acceptable for truly isolated single tasks.**

```
╔══════════════════════════════════════════════════════════════════╗
║  PRINCIPLE ZERO: AGENT TEAMS FIRST                               ║
║                                                                   ║
║  When a task involves ANY of the following:                      ║
║  • Multiple validation trials                                    ║
║  • Parallel research execution                                   ║
║  • Collaborative analysis                                        ║
║  • Iterative fix+validate cycles                                 ║
║  • Inter-agent communication needs                               ║
║  • Task coordination and management                              ║
║                                                                   ║
║  → MUST use Agent Teams                                          ║
║                                                                   ║
║  Simple Task spawns are ONLY for:                                ║
║  • Truly isolated single tasks                                   ║
║  • No follow-up coordination needed                              ║
║  • No inter-agent messaging required                             ║
╚══════════════════════════════════════════════════════════════════╝
```

## Core Principle

Agent Teams provide:
- **Inter-agent messaging**: Native SendMessage tool for real-time coordination
- **Task management**: TaskCreate/TaskList/TaskUpdate for structured work tracking
- **Team coordination**: TeamCreate → Task(team_name) → SendMessage → TeamDelete workflow
- **Sub-agent collaboration**: Teammates can communicate directly within teams
- **Persistent tracking**: Tasks survive across conversation turns

Simple parallel Task spawns lack:
- ✗ Inter-agent communication (agents cannot talk to each other)
- ✗ Task tracking (no visibility into what each agent is doing)
- ✗ Coordination (no shared task list or status)
- ✗ Iterative workflows (no way to assign follow-up work)

## Mandatory Agent Teams Workflow

```
╔══════════════════════════════════════════════════════════════════╗
║  REQUIRED WORKFLOW FOR MULTI-AGENT TASKS                         ║
║                                                                   ║
║  1. TeamCreate                                                   ║
║     - Create team with descriptive name                          ║
║     - Set team_name and description                              ║
║                                                                   ║
║  2. TaskCreate (for each work item)                              ║
║     - Define subject, description, activeForm                    ║
║     - Tasks created with status: pending                         ║
║                                                                   ║
║  3. Task(team_name) - Spawn teammates                            ║
║     - subagent_type: specific agent (NOT general-purpose)        ║
║     - team_name: reference to created team                       ║
║     - name: unique teammate identifier                           ║
║     - model: opus/sonnet/haiku                                   ║
║                                                                   ║
║  4. SendMessage - Coordinate work                                ║
║     - type: "message" for direct messages                        ║
║     - type: "broadcast" for team-wide announcements (sparingly)  ║
║     - recipient: teammate name                                   ║
║     - content: instructions or updates                           ║
║                                                                   ║
║  5. TaskUpdate - Track progress                                  ║
║     - status: pending → in_progress → completed                  ║
║     - owner: assign tasks to teammates                           ║
║                                                                   ║
║  6. TeamDelete - Clean up                                        ║
║     - After all work complete                                    ║
║     - Gracefully shutdown teammates first                        ║
╚══════════════════════════════════════════════════════════════════╝
```

## When to Use Agent Teams (MANDATORY)

| Scenario | Use Agent Teams? | Reason |
|----------|------------------|--------|
| Multiple sauron verification rounds | **YES** | Iterative fix+validate cycles |
| Parallel experiment execution | **YES** | Need coordination and progress tracking |
| Batch ANOVA with review | **YES** | Results need to be reviewed and potentially revised |
| DOE design → validation → fixes | **YES** | Multi-step workflow with feedback |
| Research analysis with peer review | **YES** | Inter-agent communication needed |
| Data processing pipeline | **YES** | Sequential stages with handoffs |
| Multi-round optimization | **YES** | Iterative improvements based on results |
| Single file read for reference | **NO** | Truly isolated, no coordination |
| Independent one-shot analyses | **NO** | No follow-up or communication needed |

## When Simple Task is Acceptable

Simple Task (without team) is ONLY acceptable when:

```yaml
criteria_all_must_be_true:
  - Task is completely isolated (no dependencies)
  - No follow-up work or validation needed
  - No inter-agent communication required
  - Results are final and need no review
  - No iterative refinement expected
  - Single agent can complete independently
  - No coordination with other agents needed
```

Examples of acceptable simple Task usage:
- Reading a single reference file
- One-time file search for information
- Truly independent parallel data processing (no review/validation)

## Violation Examples

### WRONG: Simple parallel Tasks for sauron verification

```
User: "Run sauron verification"

WRONG:
  Main conversation spawns 5 parallel Tasks (one per round)
  → No coordination
  → No way to fix issues iteratively
  → No task tracking
  → Agents cannot communicate

CORRECT:
  1. TeamCreate(team_name: "sauron-verification")
  2. TaskCreate for each verification round
  3. Task(team_name: "sauron-verification", subagent_type: "mgr-sauron")
  4. SendMessage to coordinate fixes
  5. TaskUpdate to track progress
  6. TeamDelete after completion
```

### WRONG: Simple Tasks for iterative workflow

```
User: "Design DOE, validate, fix issues, validate again"

WRONG:
  Task(research-pi) → result
  → No way to coordinate with validator
  → No way to iterate on fixes

CORRECT:
  1. TeamCreate(team_name: "doe-design-validation")
  2. TaskCreate("Design initial DOE")
  3. TaskCreate("Validate DOE design")
  4. TaskCreate("Fix issues")
  5. Task(team_name, subagent_type: "research-pi", name: "designer")
  6. Task(team_name, subagent_type: "mgr-sauron", name: "validator")
  7. SendMessage coordination between designer and validator
  8. TaskUpdate to track each stage
  9. TeamDelete after validated
```

### WRONG: Simple Tasks for collaborative analysis

```
User: "Analyze experiments 021, 022, 023 and cross-reference findings"

WRONG:
  Task(research-analyst) → exp 021
  Task(research-analyst) → exp 022
  Task(research-analyst) → exp 023
  → No way to cross-reference
  → No inter-agent communication
  → No shared context

CORRECT:
  1. TeamCreate(team_name: "batch-anova-analysis")
  2. TaskCreate for each experiment
  3. TaskCreate("Cross-reference findings")
  4. Task(team_name, subagent_type: "research-analyst", name: "analyst-021")
  5. Task(team_name, subagent_type: "research-analyst", name: "analyst-022")
  6. Task(team_name, subagent_type: "research-analyst", name: "analyst-023")
  7. SendMessage between analysts to share findings
  8. TaskUpdate to coordinate cross-referencing
  9. TeamDelete after synthesis complete
```

## Benefits of Agent Teams

### 1. Real-time Coordination

```
With Teams:
  Analyst-1 → SendMessage(Analyst-2) → "Found outlier in exp 021, check yours too"
  Analyst-2 → Responds → "Same pattern in 022, need transformation"

Without Teams:
  Analyst-1 → (completes silently)
  Analyst-2 → (completes silently)
  → No coordination, duplicate work, missed patterns
```

### 2. Task Management

```
With Teams:
  TaskList shows:
    [pending] Validate DOE design
    [in_progress] Fix issue #1 (agent: designer)
    [completed] Initial design

Without Teams:
  → No visibility into what's happening
  → Can't track progress
  → Can't reassign work
```

### 3. Iterative Workflows

```
With Teams:
  Round 1: validator → finds issues → SendMessage(designer)
  Designer → fixes → TaskUpdate(completed)
  Round 2: validator → re-validates → success

Without Teams:
  Round 1: validator → finds issues → (stops, no way to communicate)
  → Manual intervention required
  → No automated iteration
```

### 4. Graceful Shutdown

```
With Teams:
  Main → SendMessage(type: "shutdown_request", recipient: "validator")
  Validator → SendMessage(type: "shutdown_response", approve: true)
  Main → TeamDelete

Without Teams:
  → Tasks just end, no cleanup
  → No graceful coordination
```

## Integration with Other Rules

| Rule | Integration |
|------|-------------|
| R009 (Parallel Execution) | Agent Teams for parallel work with coordination |
| R010 (Orchestrator Coordination) | Main conversation orchestrates via TeamCreate |
| R007/R008 (Identification) | Teammates identified by name and subagent_type |
| R017 (Sync Verification) | Multi-round verification REQUIRES Agent Teams |

## Self-Check Before Task Spawning

```
╔══════════════════════════════════════════════════════════════════╗
║  BEFORE SPAWNING TASKS, ASK YOURSELF:                            ║
║                                                                   ║
║  1. Does this involve multiple rounds of work?                   ║
║     → YES: Use Agent Teams                                       ║
║                                                                   ║
║  2. Will agents need to communicate with each other?             ║
║     → YES: Use Agent Teams                                       ║
║                                                                   ║
║  3. Is this an iterative fix+validate cycle?                     ║
║     → YES: Use Agent Teams                                       ║
║                                                                   ║
║  4. Do I need to track progress across multiple tasks?           ║
║     → YES: Use Agent Teams                                       ║
║                                                                   ║
║  5. Is this a truly isolated one-shot task?                      ║
║     → NO: Use Agent Teams                                        ║
║     → YES: Simple Task acceptable                                ║
║                                                                   ║
║  If ANY of 1-4 are YES → Use Agent Teams                         ║
║  Only if ALL of 1-4 are NO and 5 is YES → Simple Task           ║
╚══════════════════════════════════════════════════════════════════╝
```

## Enforcement

```
╔══════════════════════════════════════════════════════════════════╗
║  VIOLATIONS (ZERO TOLERANCE)                                     ║
║                                                                   ║
║  - Using simple Task spawns for multi-round verification         ║
║  - Using simple Task spawns for iterative workflows              ║
║  - Using simple Task spawns when coordination needed             ║
║  - Spawning parallel Tasks without TeamCreate first              ║
║  - Not using SendMessage when agents need to communicate         ║
║  - Not using TaskCreate/TaskUpdate for work tracking             ║
║                                                                   ║
║  When caught:                                                    ║
║  1. STOP immediately                                             ║
║  2. Switch to Agent Teams workflow                               ║
║  3. Update this rule if new pattern discovered                   ║
╚══════════════════════════════════════════════════════════════════╝
```

## Research-Specific Examples

### Sauron Verification (R017)

```
CORRECT Agent Teams approach:

1. TeamCreate(team_name: "sauron-verification-batch")

2. TaskCreate for each round:
   - "Round 1: mgr-supplier audit"
   - "Round 2: mgr-sync-checker verification"
   - "Round 3: mgr-updater docs sync"
   - "Round 4: Re-verify after fixes"
   - "Round 5: Final validation"

3. Task(team_name: "sauron-verification-batch",
        subagent_type: "mgr-sauron",
        name: "sauron-lead",
        model: "opus")

4. SendMessage coordination:
   - sauron-lead → reports issues
   - main → fixes issues
   - sauron-lead → re-validates

5. TaskUpdate after each round:
   - Mark completed rounds
   - Update status
   - Track progress

6. TeamDelete after all 5 rounds pass
```

### DOE Design Validation

```
CORRECT Agent Teams approach:

1. TeamCreate(team_name: "doe-024-design")

2. TaskCreate:
   - "Design 3-factor CCD"
   - "Validate design structure"
   - "Fix identified issues"
   - "Final validation"

3. Task(team_name: "doe-024-design", subagent_type: "research-pi", name: "designer")
4. Task(team_name: "doe-024-design", subagent_type: "mgr-sauron", name: "validator")

5. SendMessage flow:
   designer → completes design → TaskUpdate(completed)
   validator → finds issues → SendMessage(designer, "Fix factor levels")
   designer → fixes → SendMessage(validator, "Ready for re-validation")
   validator → approves → TaskUpdate(completed)

6. TeamDelete after validated
```

## Violations and Corrections

```
User points out: "You should have used Agent Teams for this"

Response (following R016):
1. Acknowledge: "Correct, R000-0 violation"
2. Explain: "This task required [coordination/iteration/tracking]"
3. Correct: Switch to Agent Teams workflow immediately
4. Update: Add example to this rule if new pattern
5. Continue: Complete task using proper Agent Teams approach
```

## Summary

```
Principle Zero: Agent Teams First

Default: Use Agent Teams for all multi-agent work
Exception: Simple Task only for truly isolated one-shot tasks

When in doubt → Use Agent Teams
Better to use Teams unnecessarily than to miss coordination needs
```
