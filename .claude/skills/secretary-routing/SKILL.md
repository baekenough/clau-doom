---
name: secretary-routing
description: Routes agent management tasks to manager agents
user-invocable: false
---

# Secretary Routing Skill

## Purpose

Routes agent management tasks to the appropriate manager or system agent. This skill contains the coordination logic for orchestrating manager agents (mgr-creator, mgr-gitnerd, mgr-sauron) and system agents (sys-memory-keeper, sys-research-log).

## Manager and System Agents

| Agent | Purpose | Triggers |
|-------|---------|----------|
| mgr-creator | Create new agents | "create agent", "new agent" |
| mgr-gitnerd | Git operations | "commit", "push", "pr", "branch" |
| mgr-sauron | R017 verification | "verify", "sauron", "full check" |
| sys-memory-keeper | Memory operations | "save memory", "recall", "remember" |
| sys-research-log | Research audit trail | "log experiment", "research log", "audit trail" |

## Command Routing

```
User Input -> Routing -> Agent

create agent -> mgr-creator
git commit   -> mgr-gitnerd
git push     -> mgr-gitnerd
git pr       -> mgr-gitnerd
verify       -> mgr-sauron
sauron watch -> mgr-sauron
save memory  -> sys-memory-keeper
recall       -> sys-memory-keeper
research log -> sys-research-log
batch        -> multiple (parallel)
```

## Routing Rules

### 1. Single Task Routing

```
1. Parse user command and identify intent
2. Select appropriate agent:
   - "create agent X" -> mgr-creator
   - "git commit/push/pr" -> mgr-gitnerd
   - "verify" / "sauron watch" -> mgr-sauron
   - "save memory" / "recall" -> sys-memory-keeper
   - "log experiment" / "research log" -> sys-research-log
3. Spawn Task with selected agent role
4. Monitor execution
5. Report result to user
```

### 2. Batch/Parallel Task Routing

When command requires multiple independent operations:

```
1. Break down into sub-tasks
2. Identify parallelizable tasks (max 4)
3. Spawn parallel Task instances
4. Coordinate execution following R009
5. Aggregate results following R013 (ecomode)
6. Report summary to user
```

Example:
```
User: "Create rust, golang, python expert agents"

Route:
  Task(mgr-creator role -> create lang-rust-expert, model: "sonnet")
  Task(mgr-creator role -> create lang-golang-expert, model: "sonnet")
  Task(mgr-creator role -> create lang-python-expert, model: "sonnet")

Result: 3 agents created in parallel
```

### 3. Verification Before Push

```
When push is requested:
1. Check if mgr-sauron:watch has been run
2. If not -> run mgr-sauron:watch first
3. If sauron passes -> delegate push to mgr-gitnerd
4. If sauron fails -> report issues, do NOT push
```

## Sub-agent Model Selection

Use Task tool's `model` parameter to optimize cost and performance:

### Model Mapping

| Agent | Recommended Model | Reason |
|-------|-------------------|--------|
| mgr-creator | `sonnet` | File generation, balanced |
| mgr-gitnerd | `sonnet` | Commit message quality |
| mgr-sauron | `sonnet` | Multi-round verification |
| sys-memory-keeper | `sonnet` | Context management |
| sys-research-log | `haiku` | Simple structured logging |

### Task Call Examples

```
# Create new agent
Task(
  subagent_type: "general-purpose",
  prompt: "Create new lang-rust-expert agent following mgr-creator workflow",
  model: "sonnet"
)

# Git commit
Task(
  subagent_type: "general-purpose",
  prompt: "Commit staged changes following mgr-gitnerd workflow",
  model: "sonnet"
)

# Quick verification
Task(
  subagent_type: "general-purpose",
  prompt: "Run sauron quick verification",
  model: "sonnet"
)

# Save memory
Task(
  subagent_type: "general-purpose",
  prompt: "Save session context following sys-memory-keeper workflow",
  model: "sonnet"
)
```

## Parallel Execution

Following R009:
- Maximum 4 parallel instances
- Only non-orchestrator agents
- Independent tasks only
- Proper resource management

## Display Format

When spawning parallel tasks:

```
[Parallel] Spawning 3 instances...

[Instance 1] mgr-creator:sonnet -> lang-rust-expert
[Instance 2] mgr-creator:sonnet -> lang-golang-expert
[Instance 3] mgr-creator:sonnet -> lang-python-expert

[Progress] 2/3

[Instance 1] mgr-creator:sonnet -> lang-rust-expert created
[Instance 2] mgr-creator:sonnet -> lang-golang-expert created
[Instance 3] mgr-creator:sonnet -> lang-python-expert created

[Summary] 3/3 tasks completed successfully
```

## Ecomode Integration

When 4+ parallel tasks are spawned, activate ecomode (R013):
- Compact output format (status + 1-2 sentence summary)
- Skip intermediate steps
- Return essential results only
- Aggregate with icons: success, failed, partial

## Error Handling

```yaml
retry_policy:
  max_retries: 3
  backoff: exponential

failure_modes:
  single_failure: Report and continue
  critical_failure: Stop and escalate
  timeout: Retry or skip with notice
  sauron_failure: Block push, report issues
```

## Usage

This skill is NOT user-invocable. It should be automatically triggered when the main conversation detects agent management intent.

Detection criteria:
- User mentions agent creation/update
- Command starts with manager agent name
- Git operations requested
- Verification requested
- Memory operations requested
- Research logging requested
