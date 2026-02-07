# Sauron Verification Memory

## Verification Baselines (2026-02-07)

- Agents: 18 files in .claude/agents/
- Skills: 32 SKILL.md files in .claude/skills/
- Rules: 20 files in .claude/rules/
- Memory scopes: project=16, user=1, local=1

## CLAUDE.md Count Locations

- Agent count: Agents Summary table says "Total 18"
- Skill count: Project Structure says "Skills (32 directories)"
- Rule count: Not explicitly numbered, but rules table lists 15 MUST + 5 SHOULD = 20

## Key Checks That Catch Issues

1. Skill reference validation: every skill in agent frontmatter must exist in .claude/skills/
2. Memory scope validation: only valid values are user|project|local
3. Count mismatches between CLAUDE.md and actual files
4. Missing frontmatter fields (name, description, model, tools are required)

## Rule R000-0 (Principle Zero)

- Added 2026-02-07: MUST-agent-teams.md
- Located at: .claude/rules/MUST-agent-teams.md
- Referenced in CLAUDE.md line 145
- Requires Agent Teams for all multi-agent tasks
