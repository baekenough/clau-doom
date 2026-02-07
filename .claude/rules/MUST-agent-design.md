# [MUST] Agent Design Rules

> **Priority**: MUST - Never violate
> **ID**: R006

## Agent Structure

### Single File Format
```
.claude/agents/{name}.md

Format:
---
name: agent-name
description: Brief agent description
model: sonnet | opus | haiku
memory: project            # Optional
effort: high | medium | low
tools:
  - Read
  - Write
  - Bash
skills:
  - skill-name-1
  - skill-name-2
---

# Agent Content

Agent purpose and role description...
```

### Frontmatter Fields (REQUIRED)
```yaml
name: agent-name           # Unique identifier (kebab-case)
description: Brief desc    # One-line summary
model: sonnet             # Default model (sonnet | opus | haiku)
memory: project           # Persistent memory scope (user | project | local)
effort: high              # Effort level (low | medium | high)
tools: [Read, Write, ...]  # Allowed tools (MUST be array)
skills: [skill-1, ...]     # Required skill names (MUST be array)
```

### Memory Scope Reference
| Scope | Location | Use Case |
|-------|----------|----------|
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project research patterns |
| `project` | `.claude/agent-memory/<name>/` | Project-specific, versioned |
| `local` | `.claude/agent-memory-local/<name>/` | Project-specific, not versioned |

### Effort Level Reference
| Level | Use Case | Agents |
|-------|----------|--------|
| `high` | Complex reasoning, research design | research-pi, research-analyst |
| `medium` | Data processing, routine analysis | research-data-engineer |
| `low` | File validation, simple checks | mgr-supplier, mgr-sync-checker |

### Agent Types

| Type | Symbol | Purpose | Examples |
|------|--------|---------|----------|
| research | 🔬 | Research-specific agents | research-pi, research-analyst |
| sw-engineer | ⚙️ | Software development | lang-python-expert, lang-r-expert |
| manager | 🔧 | System management | mgr-creator, mgr-gitnerd |
| system | 🖥️ | System utilities | sys-memory-keeper |

### Agent Content Must NOT Contain
```
✗ Detailed skill instructions (use .claude/skills/ instead)
✗ Reference documentation (use guides/ instead)
✗ Implementation scripts (use .claude/skills/{name}/scripts/ instead)
✗ Statistical formulas (use guides/statistics/ instead)
✗ DOE design templates (use guides/doe/ instead)
```

### Agent Content Should Contain
```
✓ Agent purpose and role
✓ Capabilities overview (not details)
✓ Required skills (by name reference)
✓ Workflow description
✓ Source info (if external)
✓ Research domain (if research agent)
```

## Memory Scope (OPTIONAL)

Agents can have persistent memory that survives across conversations.

| Scope | Location | Use Case | Git Tracked |
|-------|----------|----------|-------------|
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project research learnings | No |
| `project` | `.claude/agent-memory/<name>/` | Project-specific patterns | Yes |
| `local` | `.claude/agent-memory-local/<name>/` | Local-only knowledge | No |

When enabled:
- First 200 lines of MEMORY.md loaded into agent's system prompt
- Read/Write/Edit tools automatically enabled for memory directory
- Agent builds knowledge across conversations

### Research Agent Memory Examples

```yaml
# research-pi (project scope)
memory: project
purpose: |
  Learns experimental patterns, successful DOE strategies,
  common pitfalls in this project's domain

# research-analyst (project scope)
memory: project
purpose: |
  Remembers statistical approaches used, model assumptions,
  successful analysis techniques for this project

# lang-r-expert (user scope)
memory: user
purpose: |
  Cross-project R programming patterns, package preferences,
  statistical computing best practices
```

Agents that should NOT have memory (stateless by design):
- Manager agents for one-time operations (mgr-creator, mgr-updater, mgr-supplier)
- Validation agents (mgr-sync-checker)
- Meta-agents (sys-memory-keeper)

## External Agent Requirements

External agents (from GitHub, npm, etc.) MUST include source information in frontmatter:

### Frontmatter Source Fields
```yaml
source:
  type: external
  origin: github | npm | other
  url: https://github.com/org/repo
  version: 1.0.0
  last_updated: 2025-01-22
  update_command: "npx add-skill org/repo"
```

### Update Tracking
```
- version: Current version installed
- last_updated: Date of last sync
- update_command: Command to update
- changelog_url: Where to check updates
```

## Separation of Concerns

### .claude/agents/
```
Purpose: Define WHAT the agent does
Content: Role, capabilities, workflow
Format: Single .md file with YAML frontmatter
NOT: How to do it (that's skills/)
```

### .claude/skills/
```
Purpose: Define HOW to do tasks
Content: Instructions, scripts, rules
Location: .claude/skills/{name}/SKILL.md
```

### guides/
```
Purpose: Reference documentation
Content: Best practices, tutorials, statistical methods
Location: guides/{topic}/
```

## Agent → Skill References

### In Frontmatter
```yaml
---
name: research-pi
skills:
  - doe-design
  - response-surface-methodology
  - experimental-planning
---
```

Skills are referenced by name only. The system automatically discovers skills in `.claude/skills/` by scanning for `SKILL.md` files.

## Naming Conventions

| Type | Pattern | Example |
|------|---------|---------|
| Agent file | `kebab-case.md` | `.claude/agents/research-pi.md` |
| Skill directory | `kebab-case/` | `.claude/skills/doe-design/` |
| Guide directory | `kebab-case/` | `guides/statistics/` |
| Agent filename | lowercase | `{name}.md` |
| Skill file | UPPERCASE | `SKILL.md` |

## Research Agent Specific

### Research Agent Categories

```yaml
research_agents:
  research-pi:
    focus: Experimental design, planning, oversight
    skills: [doe-design, experimental-planning]
    memory: project
    effort: high

  research-analyst:
    focus: Statistical analysis, modeling, interpretation
    skills: [statistical-analysis, anova, regression]
    memory: project
    effort: high

  research-data-engineer:
    focus: Data processing, cleaning, transformation
    skills: [data-cleaning, data-validation]
    memory: project
    effort: medium
```

### Required Skills for Research Agents

```yaml
research-pi:
  must_have:
    - doe-design
    - experimental-planning
  recommended:
    - response-surface-methodology
    - optimization

research-analyst:
  must_have:
    - statistical-analysis
    - anova
  recommended:
    - regression
    - model-validation
```

### Research Agent Workflow

```
User request (Korean)
    │
    ▼
Research Agent (identified in header)
    │
    ├─ Consult memory (first 200 lines)
    ├─ Load required skills
    ├─ Execute research task
    └─ Update memory (if patterns learned)
    │
    ▼
Response (Korean to user, English in files)
```
