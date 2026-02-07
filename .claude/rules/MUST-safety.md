# [MUST] Safety Rules

> **Priority**: MUST - Never violate
> **On violation**: Stop immediately, report to user

## Prohibited Actions

### 1. Data Protection
```
[PROHIBITED]
- Expose API keys, secrets, passwords
- Collect personal info without consent
- Log authentication tokens
- Share proprietary experimental data externally
- Expose sensitive research findings before publication
```

### 2. File System
```
[PROHIBITED]
- Modify system files (/etc, /usr, /bin)
- Delete files outside project
- Modify hidden configs (.env, .git/config) without approval
- Delete experimental data without explicit confirmation
- Overwrite original raw data files
```

### 3. Command Execution
```
[PROHIBITED]
- rm -rf / or broad delete commands
- System shutdown/restart
- Privilege escalation (sudo, su)
- Network configuration changes
- Unvetted script execution from external sources
```

### 4. External Communication
```
[PROHIBITED]
- Access external URLs without approval
- Send user data externally
- Download and execute unknown scripts
- Upload experimental data to public repositories without permission
- Share unpublished research findings
```

### 5. Research-Specific Safety

```
[PROHIBITED]
- Delete raw experimental data
- Modify original data files (always create processed versions)
- Overwrite previous analysis results without versioning
- Run destructive statistical operations without backup
- Commit sensitive research data to public repositories

[REQUIRED]
- Version all experimental data
- Preserve original raw data files
- Document all data transformations
- Backup before destructive operations
- Verify data integrity after processing
```

## Required Actions

### Before Destructive Operations
```
[REQUIRED]
□ Verify target
□ Assess impact scope
□ Check recoverability
□ Get user approval
```

### Before Data Processing
```
[REQUIRED]
□ Verify input data integrity
□ Create backup of original data
□ Document transformation steps
□ Validate output data
□ Log processing parameters
```

### On Risk Detection
```
→ Stop immediately
→ Report risk
→ Wait for user instruction
```

## Violation Response

```
1. Stop all operations
2. Preserve current state
3. Report to user:
   - What was detected
   - Why it's risky
   - What action was taken
4. Wait for instructions
```

## Research Data Safety

### Data Versioning
```
Original data: data/raw/{experiment_id}/
Processed data: data/processed/{experiment_id}/
Analysis results: results/{experiment_id}/

Never modify files in data/raw/
Always create new versions in processed/
```

### Analysis Safety
```
Before running analysis:
□ Verify data file exists
□ Check data integrity (checksums if available)
□ Confirm analysis parameters
□ Create output directory
□ Log analysis start time and parameters

After analysis:
□ Verify results generated
□ Check for errors/warnings
□ Log completion time
□ Save analysis script with results
```

### Backup Strategy
```
Before:
- Deleting any data files
- Running batch processing
- Modifying analysis scripts
- Updating DOE designs

Create:
- Timestamped backup
- Clear backup location log
- Recovery instructions
```
