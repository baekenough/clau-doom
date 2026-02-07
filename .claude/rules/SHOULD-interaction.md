# [SHOULD] Interaction Rules

> **Priority**: SHOULD - Strongly recommended
> **Exception**: Emergency or explicit user request

## Response Principles

### 1. Brevity
```
✓ Key information first
✓ Skip unnecessary preamble
✓ Answer only what's asked
✗ Over-explanation
✗ Repetitive confirmation
```

### 2. Clarity
```
✓ Specific expressions
✓ Unambiguous instructions
✓ Executable code format
✗ Abstract descriptions only
✗ Overuse of "maybe", "probably"
```

### 3. Transparency
```
✓ State actions performed
✓ Report changes
✓ Acknowledge uncertainty
✗ Hide actions
✗ Present guesses as facts
```

## Status Report Format

### Start
```
[Start] {task name}
```

### In Progress
```
[Progress] {current step} ({n}/{total})
```

### Complete
```
[Done] {task name}
Result: {summary}
```

### Failed
```
[Failed] {task name}
Cause: {reason}
Alternative: {possible solutions}
```

## Research-Specific Status Formats

### Experiment Progress
```
[Experiment] DOE-042 | Run 5/8 | Phase 1
```

### Generation Progress
```
[Generation] Gen 3/10 | Population 50 | Best fitness: 0.82
```

### Analysis Progress
```
[Analysis] ANOVA complete | Diagnostics in progress (2/3)
```

### Phase Transition
```
[Phase Transition] Phase 1 → Phase 2
Reason: Key factors identified, moving to interaction study
```

## Handling Requests

### Clear Request
→ Execute immediately

### Ambiguous Request
```
[Confirm]
Understood "{request}" as {interpretation}.

Proceed?
```

### Risky Request
```
[Warning]
This action has {risk factor}.

Continue?
- Yes: {action to perform}
- No: Cancel
```

### Research-Specific Confirmations

#### Experiment Design Change
```
[Confirm Experiment Design]
Changing DOE-042 design:
  Old: 2x2 factorial (4 conditions, 120 episodes)
  New: 2x3 factorial (6 conditions, 180 episodes)

This will:
- Increase runtime by ~50%
- Improve power for interaction detection

Proceed?
```

#### Large Sample Size
```
[Warning: Large Sample]
DOE-042 requires 300 episodes (10 conditions × 30 episodes).
Estimated runtime: ~6 hours.

Alternatives:
1. Reduce to 20 episodes/condition (power ≈ 0.75)
2. Use Taguchi fractional design (fewer conditions)
3. Proceed as designed (power ≈ 0.90)

Choice?
```

## Multiple Tasks

### Order
1. Dependent tasks: Sequential
2. Independent tasks: Parallel allowed

### Report
```
[Task 1/3] Done - {result}
[Task 2/3] In progress...
[Task 3/3] Pending
```

### Research Workflow Example
```
[Task 1/4] DOE-042 design complete
[Task 2/4] Seed set generated (n=180)
[Task 3/4] EXPERIMENT_ORDER_042.md written
[Task 4/4] research-doe-runner spawned
```

## Long-running Tasks

```
[In Progress] {task name}
Elapsed: {time}
Current: {step}
Remaining: {work left}
```

### Experiment Execution Example
```
[In Progress] DOE-042 Execution
Elapsed: 2h 15m
Current: Run 5/8 (agent-A: memory=0.7, strength=0.5)
Remaining: ~1h 30m (3 runs, 90 episodes)
```

## Research-Specific Response Patterns

### Reporting Statistical Results
```
[ANOVA Complete]
Factor: Memory
F(2,87) = 9.45, p = 0.003, partial η² = 0.18
Conclusion: Memory has significant main effect.

Next: Residual diagnostics
```

### Reporting Experiment Completion
```
[Experiment Complete] DOE-042
Total episodes: 180
Data quality: 100% (no failures)
Next: research-analyst for ANOVA
```

### Reporting Phase Transition
```
[Phase Transition Triggered]
Current: Phase 1 (Main effects)
Next: Phase 2 (Interactions)
Trigger: 3/3 key factors identified with HIGH trust
```

## Integration with HUD (R012)

Status reports should align with HUD statusline:

```
─── [Agent] research-analyst | [Progress] 2/3 | [Experiment] DOE-042 ───

[Progress] Residual diagnostics (2/3)
- Normality: PASS (Anderson-Darling p=0.42)
- Equal variance: PASS (Levene p=0.18)
- Independence: IN PROGRESS...
```
