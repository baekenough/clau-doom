---
name: memory-management
description: Memory persistence operations using native auto memory and claude-mem
user-invocable: false
---

## Purpose

Provide memory persistence operations for session context survival across compactions, using native auto memory as primary and claude-mem as optional supplement.

## Operations

### 1. Save Context

```yaml
operation: save
description: Store session context in memory
steps:
  1. Collect session data:
     - Tasks completed
     - Decisions made
     - Open items
     - Experiment results
     - Key code changes
  2. Format document:
     - Add project tag: "clau-doom"
     - Add session ID: {date}-{uuid}
     - Add relevant tags
  3. Store in memory:
     - Update MEMORY.md for persistent patterns
     - Use claude-mem (if available) for session observations
```

### 2. Recall Context

```yaml
operation: recall
description: Search and retrieve relevant memories
steps:
  1. Build query:
     - Always prefix with "clau-doom"
     - Add user-provided search terms
     - Include date for temporal searches
  2. Search memory sources:
     - Check native MEMORY.md first
     - Search claude-mem if available
  3. Format results:
     - Sort by relevance
     - Present summary
     - Provide access to full content
```

### 3. Get Specific Memory

```yaml
operation: get
description: Retrieve specific memory by ID
steps:
  1. Use claude-mem chroma_get_documents with ID (if available)
  2. Or read from MEMORY.md topic files
  3. Return full content
```

## Query Patterns

### Semantic Search (Primary)

```python
# Always include project name
chroma_query_documents(["clau-doom {search_terms}"])

# Examples:
chroma_query_documents(["clau-doom DOE factorial design results"])
chroma_query_documents(["clau-doom 2026-02-07 ANOVA analysis"])
```

## Document Format

### Save Format

```yaml
content: |
  ## Session Summary
  Date: {date}
  Session: {session_id}

  ### Tasks Completed
  - Task 1: Description

  ### Decisions Made
  - Decision 1: Rationale

  ### Experiment Results
  - Experiment: findings summary

  ### Open Items
  - Item 1: Status

metadata:
  project: clau-doom
  session: {date}-{uuid}
  tags: [session, task, decision, experiment]
  created_at: {timestamp}
```

## Best Practices

### Query Tips

```yaml
do:
  - Always include "clau-doom" prefix
  - Use semantic, intent-based queries
  - Include dates for temporal searches
  - Use multiple queries for better coverage

dont:
  - Use complex where filters
  - Omit project name
  - Use overly generic terms
```

### Save Tips

```yaml
do:
  - Include meaningful tags
  - Write clear summaries
  - Capture decisions with rationale
  - Record statistical findings with evidence

dont:
  - Save trivial conversations
  - Include sensitive data
  - Create duplicate entries
```

## Error Handling

```yaml
save_errors:
  - Connection failure: Retry 3 times, then log and continue
  - Invalid format: Validate before save, report issues
  - Storage full: Archive old memories, then retry

recall_errors:
  - No results: Suggest alternative queries
  - Connection failure: Return empty with warning
  - Invalid query: Help user reformulate
```

## Integration

### With sys-memory-keeper Agent

```
sys-memory-keeper agent uses this skill for:
- Memory save operations
- Memory recall operations
- Session context management
```
