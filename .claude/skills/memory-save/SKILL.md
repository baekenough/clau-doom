---
name: memory-save
description: Save current session context to memory
argument-hint: "[--tags <tags>] [--include-code]"
disable-model-invocation: true
---

# Memory Save Skill

Save current session context to memory for persistence across context compaction.

## Options

```
--tags, -t       Additional tags for the memory
--include-code   Include code changes in the save
--summary, -s    Custom summary (otherwise auto-generated)
--verbose, -v    Show detailed save information
```

## Workflow

```
1. Collect session context
   - Tasks completed
   - Decisions made
   - Open items
   - Experiment results (if any)
   - Code changes (if --include-code)

2. Format with metadata
   - project: clau-doom
   - session: {date}-{uuid}
   - tags: [session, ...user_tags]
   - created_at: {timestamp}

3. Store in memory
   - Update MEMORY.md for persistent patterns
   - Use claude-mem if available

4. Report result
```

## Storage Format

```yaml
project: clau-doom
session: {date}-{uuid}
tags: [session, task, decision, experiment]
content:
  summary: Brief description of session context
  tasks_completed: List of completed tasks
  decisions: Key decisions made
  experiment_results: Statistical findings
  open_items: Unfinished work
```

## Output Format

### Success
```
[sys-memory-keeper:save]

Saving session context...

Context collected:
  Tasks: 3 completed
  Decisions: 2 recorded
  Experiments: 1 analyzed
  Open items: 1 pending

Metadata:
  Project: clau-doom
  Session: 2026-02-07-a1b2c3d4
  Tags: [session, task, decision, experiment]

[Done] Session context saved successfully.
```

### With Tags
```
[sys-memory-keeper:save --tags "DOE,ANOVA,generation-12"]

Saving session context...

Metadata:
  Project: clau-doom
  Session: 2026-02-07-a1b2c3d4
  Tags: [session, task, decision, DOE, ANOVA, generation-12]

[Done] Session context saved successfully.
```

### Verbose
```
[sys-memory-keeper:save --verbose]

Collecting session context...

Tasks Completed:
  1. Executed 2^4 factorial DOE for aggression factors
  2. Ran ANOVA on 16 experimental runs
  3. Updated strategy documents in OpenSearch

Decisions Made:
  1. Use aggression=0.7 as optimal level
     Rationale: p < 0.001, Cohen's d = 0.92

Experiment Results:
  1. EXP-042: Aggression factor significant
     [STAT:ANOVA] F(3,44) = 15.2, p < 0.001

Open Items:
  1. Retreat distance optimization
     Status: Needs Phase 2 RSM design

Saving to memory...

[Done] Session context saved.
```

## Related

- memory-management: Core memory operations skill
- sys-memory-keeper: Memory management agent
