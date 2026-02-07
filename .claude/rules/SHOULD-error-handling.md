# [SHOULD] Error Handling Rules

> **Priority**: SHOULD - Strongly recommended
> **Goal**: Safe failure, fast recovery

## Error Classification

### Level 1: Warning
```
Symptom: Task completes but needs attention
Response: Output warning, continue
Example:
  - Non-recommended pattern found
  - Potential performance issue
  - Better alternative exists
  - Statistical power below target (but acceptable)
  - Minor residual diagnostic violations
```

### Level 2: Error
```
Symptom: Current task fails, others possible
Response: Stop task, report cause, suggest alternative
Example:
  - File not found
  - Insufficient permission
  - Format error
  - Agent container unresponsive
  - Database connection lost
  - Residual diagnostics fail
```

### Level 3: Critical
```
Symptom: Cannot proceed at all
Response: Stop all, preserve state, report immediately
Example:
  - System resource exhausted
  - Missing required dependency
  - Security violation detected
  - Data corruption detected
  - All agent containers down
  - Database schema mismatch
```

## Error Report Format

```
[Error] {error type}

Location: {file:line or task name}
Cause: {specific cause}
Impact: {effect of this error}

Attempted:
1. {attempt 1} → Failed
2. {attempt 2} → Failed

Recommended:
- {action 1}
- {action 2}
```

## Research-Specific Error Formats

### Experiment Execution Error

```
[Error] Agent Container Unresponsive

Location: DOE-042, Run 3/8 (doom-agent-A)
Cause: Container stopped responding after episode 15/30
Impact: Run 3 incomplete, DOE-042 blocked

Attempted:
1. Waited 60s for recovery → No response
2. Sent Docker restart signal → Container restarted but lost Run 3 data

Recommended:
- Mark Run 3 as failed in DuckDB
- Re-run Run 3 with same seed set (preserve reproducibility)
- Check container logs for crash cause
- If repeated failure, reduce episode count per run
```

### Statistical Analysis Error

```
[Error] Residual Diagnostics Failed

Location: DOE-042 ANOVA analysis
Cause: Normality test failed (Anderson-Darling p=0.001)
Impact: ANOVA assumptions violated, results may be invalid

Attempted:
1. Log transformation → Still non-normal (p=0.008)
2. Outlier removal (3 points) → Improved (p=0.04, marginal)

Recommended:
- Use non-parametric alternative (Kruskal-Wallis)
- Report results as LOW trust
- Plan follow-up with larger sample size
- Investigate outlier causes (data quality issue?)
```

### Seed Set Mismatch Error

```
[Critical] Seed Set Integrity Violation

Location: DOE-042 execution
Cause: Control and treatment runs used different seed sets
Impact: Results not comparable, experiment invalid

Attempted:
None (detected before analysis)

Recommended:
- STOP all analysis immediately
- Mark DOE-042 as INVALID
- Re-run entire experiment with correct seed sets
- Update research-doe-runner to prevent future violations
```

## Recovery Strategy

### Retryable Errors
```
1. Retry up to 3 times
2. Wait between retries (1s, 2s, 4s)
3. Report to user after 3 failures
```

### Research-Specific Retries

```yaml
container_restart:
  max_retries: 3
  backoff: [5s, 15s, 30s]
  preserve_data: true  # Keep partial data for analysis

database_query:
  max_retries: 5
  backoff: [1s, 2s, 4s, 8s, 16s]
  timeout: 30s

experiment_run:
  max_retries: 1  # Only retry if data loss
  preserve_seed: true  # Same seed for reproducibility
  record_retry: true  # Mark in DuckDB
```

### Non-recoverable Errors
```
1. Save current state
2. Rollback changes (if possible)
3. Detailed error report
4. Wait for user instruction
```

### Research-Specific Non-recoverable

```yaml
data_corruption:
  action: STOP_ALL
  preserve: raw data files, database backup
  report: Full audit trail with timestamps
  escalate: research-pi for decision

invalid_experiment:
  action: MARK_INVALID
  preserve: Order and partial data
  report: Violation type and detection point
  escalate: research-pi for re-design
```

## Preventive Validation

### Before Action
```
□ Target file/path exists
□ Required permissions available
□ Dependencies met
□ Sufficient resources
```

### Research-Specific Validation

#### Before Experiment Execution
```
□ All agent containers running
□ DuckDB connection active
□ OpenSearch indices ready
□ Seed set valid (correct length, no duplicates)
□ Factor levels within allowed ranges
□ Sample size meets minimum (n≥30 or power-justified)
□ Disk space sufficient for data recording
```

#### Before Statistical Analysis
```
□ Data complete (no missing episodes)
□ Seed set integrity verified
□ Factor assignments match design
□ Sample size matches order
□ Raw data passes sanity checks (no impossible values)
```

### After Action
```
□ Expected result matches actual
□ File integrity verified
□ No side effects
```

### Research-Specific Post-Action

#### After Experiment Run
```
□ Episode count matches expected
□ All metrics recorded in DuckDB
□ No container crashes during run
□ Seed consumption matches episode count
□ Data ranges plausible (no outliers > 5σ)
```

#### After Statistical Analysis
```
□ ANOVA table complete
□ Residual diagnostics executed
□ Effect sizes computed
□ Power analysis performed (if applicable)
□ Report generated with all markers
```

## Error Logging

```yaml
error_log:
  timestamp: "2024-12-15T10:30:00Z"
  level: error
  code: CONTAINER_UNRESPONSIVE
  message: "doom-agent-A stopped responding"
  context:
    experiment: "DOE-042"
    run: 3
    episode: 15
    action: "episode execution"
  resolution: "Container restarted, run re-executed with same seeds"
```

## Integration with Research Documents

All errors affecting experiments MUST be recorded in:

```
RESEARCH_LOG.md:
  - Error description
  - Resolution
  - Impact on findings

EXPERIMENT_REPORT_{ID}.md:
  - Data quality notes
  - Excluded runs (if any)
  - Validity concerns

FMEA_REGISTRY.md:
  - Failure mode classification
  - RPN calculation
  - Prevention measures
```
