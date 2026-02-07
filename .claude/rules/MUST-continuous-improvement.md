# [MUST] Continuous Improvement Rules

> **Priority**: MUST - Top-level enforcement
> **ID**: R016
> **Trigger**: User points out rule violation

## CRITICAL

**When user points out a rule violation, you MUST update the rules to prevent future violations BEFORE continuing with the task.**

```
╔══════════════════════════════════════════════════════════════════╗
║  WHEN USER POINTS OUT A VIOLATION:                               ║
║                                                                   ║
║  1. STOP current task immediately                                ║
║  2. UPDATE the relevant rule to be clearer/stronger              ║
║  3. COMMIT the rule update                                       ║
║  4. THEN continue with the original task                         ║
║                                                                   ║
║  DO NOT just apologize and continue.                             ║
║  DO NOT promise to do better next time.                          ║
║  ACTUALLY UPDATE THE RULES.                                      ║
╚══════════════════════════════════════════════════════════════════╝
```

## Workflow

```
User points out violation
         │
         ▼
┌─────────────────────────┐
│ 1. Acknowledge violation │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 2. Identify root cause   │
│    - Which rule was weak?│
│    - What was unclear?   │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 3. Update the rule       │
│    - Add clarity         │
│    - Add examples        │
│    - Add self-checks     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 4. Commit the change     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│ 5. Continue original task│
│    (now following rules) │
└─────────────────────────┘
```

## Examples

### Example 1: Parallel Execution Violation

```
User: "병렬 실행을 안 지킨거 아닌가?"

WRONG Response:
  "맞습니다, 죄송합니다. 다음부터 잘 지키겠습니다."
  [continues task without updating rules]

CORRECT Response:
  1. "맞습니다. R009 위반입니다."
  2. [Updates MUST-parallel-execution.md with clearer guidance]
  3. [Commits the update]
  4. [Continues task with proper parallel execution]
```

### Example 2: Wrong Agent Used

```
User: "research-pi 에이전트를 써야 하는거 아닌가?"

WRONG Response:
  "맞습니다. research-pi를 사용하겠습니다."
  [continues without updating rules]

CORRECT Response:
  1. "맞습니다. R010 위반입니다."
  2. [Updates relevant rules to clarify agent delegation for DOE tasks]
  3. [Commits the update]
  4. [Continues with proper agent delegation]
```

### Example 3: Research Workflow Violation

```
User: "ANOVA는 research-analyst가 해야하는거 아닌가?"

WRONG Response:
  "아, 맞습니다. research-analyst를 사용하겠습니다."
  [continues without updating rules]

CORRECT Response:
  1. "맞습니다. R010 위반입니다."
  2. [Updates MUST-orchestrator-coordination.md to clarify statistical analysis delegation]
  3. [Adds research-analyst trigger patterns to routing skills]
  4. [Commits the updates]
  5. [Continues with proper delegation to research-analyst]
```

## Why This Matters

```
Without rule updates:
  Violation → Apology → Same mistake later → Apology → ...

With rule updates:
  Violation → Rule improvement → Better behavior → Learning preserved
```

1. **Institutional Memory**: Rules capture learnings permanently
2. **Prevents Recurrence**: Clearer rules = fewer future violations
3. **Continuous Improvement**: System gets better over time
4. **Accountability**: Actions, not just words
5. **Research Quality**: Ensures consistent experimental workflows

## Integration with Other Rules

This rule takes precedence when violations are pointed out:

| Situation | Action |
|-----------|--------|
| User points out violation | STOP → Update rule → Continue |
| Self-detected violation | Fix immediately, consider rule update |
| Ambiguous situation | Ask user, then update if needed |

## Research-Specific Improvements

When violations occur in research workflows:

```yaml
common_violations:
  wrong_agent_for_doe:
    fix: Update R010 to clarify research-pi for DOE design
    example: "Use general-purpose instead of research-pi for CCD"

  wrong_agent_for_analysis:
    fix: Update R010 to clarify research-analyst for statistics
    example: "Direct ANOVA without delegating to research-analyst"

  no_parallelization:
    fix: Update R009 to add research examples
    example: "Sequential ANOVA on 3 experiments instead of parallel"

  missing_identification:
    fix: Update R007/R008 to emphasize research context
    example: "Tool calls without agent+model identification"

  sequential_instead_of_parallel:
    fix: Update R009 with research workflow examples
    example: "Process 3 DOE designs sequentially"
```

## Rule Update Template

When updating a rule:

```markdown
## Updated: [Date]

### Reason
User pointed out: [specific violation]

### Change
Added: [what was added]
- Example: [new example]
- Self-check: [new self-check section]
- Clarification: [clarified text]

### Impact
This prevents: [future violations]
This ensures: [correct behavior]
```

## Enforcement

```
Violation of this rule = Ignoring user feedback = Unacceptable

When caught violating this rule:
1. Stop immediately
2. Update THIS rule to be even clearer
3. Update the ORIGINAL violated rule
4. Continue with proper behavior
```

## Research Workflow Quality

Rule improvements directly impact research quality:

```yaml
improved_rules_ensure:
  - Consistent DOE design methodology
  - Proper statistical analysis delegation
  - Reproducible experimental workflows
  - Clear agent responsibility boundaries
  - Parallel processing for batch experiments
  - Proper data handling and safety
```

## Self-Check Before Responding to Violation

```
╔══════════════════════════════════════════════════════════════════╗
║  WHEN USER POINTS OUT VIOLATION, ASK YOURSELF:                   ║
║                                                                   ║
║  1. Did I acknowledge the specific rule violated (R###)?         ║
║  2. Did I UPDATE the rule file (not just apologize)?             ║
║  3. Did I COMMIT the rule change?                                ║
║  4. Did I explain what was added to prevent recurrence?          ║
║                                                                   ║
║  If NO to ANY → You are violating R016                           ║
╚══════════════════════════════════════════════════════════════════╝
```

## Examples of Good Rule Updates

### Example: Adding DOE Agent Clarity

```diff
# MUST-orchestrator-coordination.md

+ ### DOE Design Tasks (MANDATORY)
+
+ ```
+ ╔══════════════════════════════════════════════════════════════════╗
+ ║  ALL DOE DESIGN TASKS MUST USE research-pi                       ║
+ ║                                                                   ║
+ ║  Keywords triggering research-pi:                                ║
+ ║    - CCD, BBD, factorial, RSM                                    ║
+ ║    - "실험설계", "중심합성계획", "반응표면"                      ║
+ ║                                                                   ║
+ ║  WRONG: Main conversation → creates DOE directly                 ║
+ ║  CORRECT: Main conversation → Task(research-pi) → DOE design     ║
+ ╚══════════════════════════════════════════════════════════════════╝
+ ```
```

This update:
- Adds visual emphasis
- Lists specific keywords
- Shows wrong vs correct patterns
- Makes delegation rule unambiguous

## Integration with Research Memory

Rule updates should be reflected in agent memory:

```yaml
when_rule_updated:
  affected_agents:
    - research-pi: Update MEMORY.md with DOE delegation patterns
    - research-analyst: Update MEMORY.md with analysis delegation patterns
    - main-conversation: Update routing skill patterns

  ensure:
    - Agent memory reflects new rule
    - Routing skills match updated patterns
    - Examples include research-specific cases
```
