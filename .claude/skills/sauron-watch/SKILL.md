---
name: sauron-watch
description: Full R017 verification (5+3 rounds) before commit
disable-model-invocation: true
---

# Sauron Watch Skill

Execute full R017 verification process with 5 rounds of manager agent verification and 3 rounds of deep review.

## Purpose

Ensure complete synchronization of agents, skills, documentation, and project structure before committing changes.

## Workflow

### Phase 1: Manager Agent Verification (5 rounds)

#### Round 1-2: Basic Sync
```
- Check all agent frontmatter (name, description, model, tools)
- Verify skill references exist in .claude/skills/
- Verify agent count matches CLAUDE.md
- Fix any issues found
```

#### Round 3-4: Deep Sync
```
- Re-verify frontmatter after fixes
- Re-verify skill references
- Check documentation sync
- Verify memory scope distribution
- Fix any remaining issues
```

#### Round 5: Final Verification
```
- All agent counts match (CLAUDE.md vs actual .md files)
- All skill counts match (CLAUDE.md vs actual SKILL.md files)
- All frontmatter valid
- All memory field values valid (user | project | local)
- Memory distribution matches CLAUDE.md
```

### Phase 2: Deep Review (3 rounds)

#### Deep Round 1: Workflow Alignment
```
- Agent creation workflow documented and functional
- Development workflow uses proper routing skills
- Research workflow follows experiment lifecycle
- All routing skills have complete agent pattern mappings
```

#### Deep Round 2: Reference Verification
```
- All routing skills properly reference their managed agents
- All rules are properly referenced
- No orphaned agents (not referenced by any routing skill)
- No circular references
- All skill references in agent frontmatter are valid
```

#### Deep Round 3: Philosophy Compliance
```
- R006: Separation of concerns (agent file = role only)
- R009: Parallel execution enabled
- R010: Multi-agent tasks use routing skills and Task tool
- R007/R008: Agent/tool identification documented
- R100: Experiment integrity (seeds, evidence, trust scores)
- All MUST rules enforced
```

### Phase 3: Fix Issues
```
- All issues from Phase 1 fixed
- All issues from Phase 2 fixed
- Re-run verification if major fixes made
```

### Phase 4: Commit Ready
```
- All verification passed
- Ready to delegate to mgr-gitnerd for commit
```

## Output Format

```
[mgr-sauron:watch]

Starting full R017 verification...

=== Phase 1: Manager Agent Verification (5 rounds) ===

[Round 1/5] Basic sync - Frontmatter validation
  - All agents have valid frontmatter

[Round 2/5] Basic sync - Reference checks
  - All skill references valid

[Round 3/5] Deep sync - Re-verification
  - Dependencies verified after fixes

[Round 4/5] Deep sync - Documentation
  - Documentation synchronized

[Round 5/5] Final verification
  - Agent counts match across all sources
  - Skill counts match
  - Memory distribution correct

=== Phase 2: Deep Review (3 rounds) ===

[Round 1/3] Workflow alignment
  - Agent creation workflow documented
  - Development workflow uses routing skills
  - Research workflow follows lifecycle

[Round 2/3] Reference verification
  - All routing references valid
  - All rules referenced
  - No orphaned agents

[Round 3/3] Philosophy compliance
  - R006 separation enforced
  - R009 parallel execution enabled
  - R010 orchestrator coordination documented
  - R007/R008 identification rules present

=== VERIFICATION COMPLETE ===

Status: ALL CHECKS PASSED

Ready to commit.
```

## Quick Verification Commands

```bash
# Agent count check
ls .claude/agents/*.md | wc -l

# Skill count check
find .claude/skills -name "SKILL.md" | wc -l

# Frontmatter validation
for f in .claude/agents/*.md; do head -1 "$f" | grep -q "^---" || echo "MISSING: $f"; done

# Memory field validation
for f in .claude/agents/*.md; do
  mem=$(grep "^memory:" "$f" | awk '{print $2}')
  if [ -n "$mem" ] && [ "$mem" != "project" ] && [ "$mem" != "user" ] && [ "$mem" != "local" ]; then
    echo "INVALID MEMORY in $f: $mem"
  fi
done
```

## Related

- R017: Sync Verification Rules
- mgr-gitnerd: Git operations agent
- mgr-sauron: Verification agent
