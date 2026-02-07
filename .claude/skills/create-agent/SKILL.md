---
name: create-agent
description: Create a new agent with complete structure following R006
argument-hint: "<name> --type <type>"
disable-model-invocation: true
---

# Create Agent Skill

Create a new agent with a complete .claude/agents/{name}.md file following R006 design guidelines.

## Parameters

| Name | Type | Required | Description |
|------|------|----------|-------------|
| name | string | yes | Agent name (kebab-case) |

## Options

```
--type, -t       Agent type (required)
                 Values: research, sw-engineer, sw-engineer/infra, sw-architect, manager, system
--desc, -d       Description
--skills         Comma-separated skills to include
--memory         Memory scope (user, project, local)
```

## Workflow

```
1. Validate input
   - Name is unique (no existing .claude/agents/{name}.md)
   - Name is kebab-case
   - Type is valid

2. Research (for language/framework agents)
   - Find authoritative references
   - Identify official docs, style guides, best practices

3. Create agent file
   - .claude/agents/{name}.md
   - YAML frontmatter (name, description, model, memory, effort, skills, tools)
   - Markdown content (purpose, capabilities, workflow, references)

4. Validate
   - Frontmatter has all required fields
   - Skill references exist in .claude/skills/
   - Memory scope is valid
```

## Templates

### Agent File Template

```markdown
---
name: {name}
description: {description}
model: sonnet
memory: project
effort: high
skills:
  - {skill-name}
tools:
  - Read
  - Write
  - Edit
  - Grep
  - Glob
  - Bash
---

You are a {type} specialist that {purpose}.

## Core Capabilities

1. {capability-1}
2. {capability-2}

## Workflow

{workflow description}

## Rules Applied

- R000: All files in English
- R006: Separation of concerns
```

## Output Format

```
[mgr-creator:agent {name} --type {type}]

Creating agent: {name}

[1/3] Validating...
  - Name available
  - Type valid: {type}

[2/3] Creating agent file...
  - .claude/agents/{name}.md

[3/3] Validating structure...
  - Frontmatter valid
  - Skill references OK

Agent created successfully: .claude/agents/{name}.md
```

## Related

- R006: Agent design rules
- mgr-creator: Agent creation specialist
