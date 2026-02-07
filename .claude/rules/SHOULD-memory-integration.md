# [SHOULD] Memory Integration Rules

> **Priority**: SHOULD - Recommended for context persistence
> **ID**: R011

## Purpose

Provide persistent memory for agents using Claude Code's native auto memory system.

## Architecture: Native First

```
Primary: Native Auto Memory (memory field in agent frontmatter)
  - Agent-specific persistent knowledge
  - Automatic system prompt injection (MEMORY.md)
  - No external dependencies

Supplementary: claude-mem MCP (optional)
  - Session-level temporal observations
  - Cross-agent semantic search
  - Only if installed and configured

RULE: If native auto memory can handle the task,
      DO NOT use claude-mem.
```

## Native Auto Memory

### How It Works

1. Agent frontmatter includes `memory` field:
   ```yaml
   memory: project  # or user, local
   ```

2. System automatically:
   - Creates memory directory for the agent
   - Loads first 200 lines of MEMORY.md into system prompt
   - Enables Read/Write/Edit tools for memory directory
   - Agent learns and records patterns across conversations

### Memory Scopes

| Scope | Location | Use Case | Git Tracked |
|-------|----------|----------|-------------|
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project patterns | No |
| `project` | `.claude/agent-memory/<name>/` | Project-specific patterns | Yes |
| `local` | `.claude/agent-memory-local/<name>/` | Local-only knowledge | No |

### Current Agent Memory Map (clau-doom)

| Scope | Agents | Count |
|-------|--------|-------|
| `project` | research-pi, research-analyst, research-doe-runner, research-evolution-mgr, research-pareto-optimizer, research-data-eng, research-viz-specialist, research-literature-mgr, research-ci-cd-mgr, doom-env-mgr, doom-agent-designer, doom-agent-tester, doom-agent-deployer, doom-metrics-collector, doom-config-optimizer, sys-research-log | 16 |
| `user` | infra-docker-expert | 1 |
| `local` | sys-research-log | 1 |

**Total**: 18 agents (16 project + 1 user + 1 local)

### Memory Best Practices

```yaml
do:
  - Let agents consult memory before starting work
  - Update memory after discovering patterns or conventions
  - Keep MEMORY.md under 200 lines (auto-curate if exceeded)
  - Use separate topic files for detailed notes

dont:
  - Store sensitive data (API keys, credentials)
  - Duplicate information already in CLAUDE.md
  - Use memory for temporary session state
```

### Research-Specific Memory Patterns

#### research-pi Memory

```yaml
patterns_to_remember:
  - DOE design preferences (which designs work well)
  - Factor level ranges that produce good results
  - Interaction patterns discovered
  - Phase transition criteria
  - Hypothesis generation strategies
  - Successful experiment sequences

example_memory:
  - "Memory 0.7-0.9 range consistently shows strong effects"
  - "Curiosity-Memory interaction significant in 3/3 experiments"
  - "Phase 1→2 transition best at 3 key factors identified"
  - "Taguchi L18 effective for 7+ factor screening"
```

#### research-analyst Memory

```yaml
patterns_to_remember:
  - Common residual diagnostic issues
  - Effective transformations for non-normal data
  - Typical effect sizes for different factors
  - Power analysis results
  - Visualization preferences

example_memory:
  - "Kill efficiency data often right-skewed, log transform works"
  - "Memory factor typically large effect (η² > 0.15)"
  - "Sample size n=30 gives power ≈ 0.85 for medium effects"
  - "Interaction plots more informative than main effect plots"
```

#### research-doe-runner Memory

```yaml
patterns_to_remember:
  - Container restart sequences
  - Common execution errors and solutions
  - MD variable injection patterns
  - Episode failure patterns
  - Runtime estimates per design type

example_memory:
  - "doom-agent-A occasionally hangs after 50 episodes, restart helps"
  - "Factor injection requires 5s container restart wait time"
  - "2^3 factorial takes ~45 min for 240 episodes"
  - "Map E1M1 causes crashes at speed > 0.9, avoid in designs"
```

## Claude-mem (Optional Supplement)

claude-mem MCP provides session-level observations and semantic search.
It is NOT required for basic memory functionality.

### When to Use claude-mem

| Scenario | Use Native Memory | Use claude-mem |
|----------|------------------|---------------|
| Agent learns project patterns | Yes | |
| Record debugging insights | Yes | |
| Search across multiple sessions | | Yes |
| Temporal queries (date-based) | | Yes |
| Cross-agent knowledge sharing | | Yes |
| Basic context persistence | Yes | |

### claude-mem Integration (if installed)

```yaml
provider: claude-mem
collection: claude_memories
project_tag: clau-doom
status: optional
```

## Context Compaction

### Compaction Controls

```yaml
# Targeted compaction - preserve specific context
/compact focus on {topic}

# Examples
/compact focus on DOE-042 design decisions
/compact focus on memory-strength interaction findings
/compact focus on Phase 1 results
/compact focus on ANOVA diagnostics for DOE-042
```

### Best Practices

```
do:
  - Use /compact focus when nearing context limits
  - Focus on the most relevant topic for current work
  - Let auto-compaction handle routine cleanup

dont:
  - Manually compact when not near limits
  - Lose important decision context by unfocused compaction
  - Compact during active experiment execution
```

### Research-Specific Compaction

```yaml
preserve_during_compaction:
  - Active experiment orders (DOE-{ID})
  - Current experiment reports (RPT-{ID})
  - Recent RESEARCH_LOG entries (last 5)
  - Active hypothesis from HYPOTHESIS_BACKLOG
  - Current phase information
  - Seed sets for active experiments

compact_away:
  - Completed experiment details (keep summary only)
  - Old hypothesis discussions (adopted/rejected)
  - Intermediate analysis attempts
  - Verbose statistical output (keep markers only)
```

## Error Handling

```yaml
on_memory_write_failure:
  - Log error
  - Continue without blocking main task
  - Memory is enhancement, not requirement
```

## Research Memory Integration with Documents

```
Agent memory supplements, does NOT replace, research documents:

RESEARCH_LOG.md:
  - Canonical research history
  - Git-tracked, permanent

Agent MEMORY.md:
  - Operational patterns
  - Quick reference
  - Auto-curated (200 line limit)

Relationship:
  - Memory helps agents work efficiently
  - Research log provides audit trail
  - Both are complementary
```

## Memory Update Triggers

### research-pi

```yaml
update_memory_when:
  - Finding adopted with HIGH trust
  - New phase transition criteria discovered
  - DOE design proves particularly effective
  - Hypothesis generation pattern emerges
  - Factor interaction pattern confirmed
```

### research-analyst

```yaml
update_memory_when:
  - New transformation technique works
  - Residual diagnostic pattern identified
  - Effect size pattern observed
  - Power analysis reveals insight
  - Visualization approach effective
```

### research-doe-runner

```yaml
update_memory_when:
  - New container issue encountered and resolved
  - Runtime estimate refined
  - Execution error pattern discovered
  - MD injection technique improved
  - Resource bottleneck identified
```
