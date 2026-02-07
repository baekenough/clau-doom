# [MUST] Permission Rules

> **Priority**: MUST - Never violate
> **Principle**: Least privilege, explicit approval

## Tool Permission Tiers

### Tier 1: Always Allowed
```yaml
always_allowed:
  - Read        # Read files
  - Glob        # Search files
  - Grep        # Search content
```

### Tier 2: Default Allowed (Use with care)
```yaml
default_allowed:
  - Write       # Create files
  - Edit        # Modify files
```
→ State changes explicitly
→ Notify before modifying important files
→ NEVER modify raw data files without explicit approval

### Tier 3: Requires Approval
```yaml
requires_approval:
  - Bash        # Execute commands
  - WebFetch    # Web access
  - WebSearch   # Web search
```
→ Request user approval on first use
→ State command/URL to be accessed
→ Especially for statistical analysis scripts

### Tier 4: Explicit Request Only
```yaml
explicit_request_only:
  - Task        # Create subagents
```
→ Only when user explicitly requests
→ For parallel DOE analysis or batch processing

## File Access

### Read Access
```
✓ All source code in project
✓ Config files (read-only)
✓ Documentation files
✓ Experimental data (raw and processed)
✓ Analysis results
✓ DOE designs
```

### Write Access
```
✓ Source code in project
✓ New files in project
✓ Processed data files (data/processed/)
✓ Analysis results (results/)
✓ Generated reports
✗ Raw data files (data/raw/) - READ ONLY
✗ Sensitive configs (.env, .git/config)
✗ Paths outside project
```

### Delete Access
```
✓ Temp files created by agent
✓ Generated plots/figures (with backup)
✗ Raw experimental data (NEVER)
✗ Original data files (without explicit request)
✗ Entire data directories
```

## Research-Specific Permissions

### Data Files

| Operation | Permission | Notes |
|-----------|------------|-------|
| Read raw data | Always allowed | Read-only access |
| Write processed data | Default allowed | Must be in data/processed/ |
| Delete raw data | **PROHIBITED** | Never allowed |
| Delete processed data | Requires approval | Must confirm with user |
| Overwrite analysis results | Requires approval | Version previous results |

### Statistical Analysis

| Operation | Permission | Notes |
|-----------|------------|-------|
| Run R/Python scripts | Requires approval | Review script before execution |
| Install packages | Requires approval | State package name and source |
| Modify analysis parameters | Default allowed | Log parameter changes |
| Generate plots | Default allowed | Save to results/ |
| Export results | Requires approval | Confirm export format and destination |

### DOE Operations

| Operation | Permission | Notes |
|-----------|------------|-------|
| Create DOE design | Default allowed | Save to designs/ |
| Modify existing DOE | Requires approval | Explain changes |
| Delete DOE design | Requires approval | Confirm impact |
| Run optimization | Requires approval | Review objective function |
| Generate experiment order | Default allowed | Randomization preserved |

## Permission Request Format

```
[Permission Request]
Action: {intended action}
Required: {tool/access needed}
Reason: {why needed}
Risk: Low / Medium / High
Data Impact: {which data files affected}

Approve?
```

### Example: Statistical Analysis

```
[Permission Request]
Action: Run ANOVA analysis on experiment 021 data
Required: Bash (Rscript anova_analysis.R)
Reason: Analyze factor effects from DOE
Risk: Low
Data Impact:
  - Read: data/processed/experiment_021_clean.csv
  - Write: results/021/anova_results.csv

Approve?
```

## On Insufficient Permission

```
1. Do not attempt action
2. Notify user of insufficient permission
3. Request permission or suggest alternative
4. For data operations, explain data safety implications
```

## Research Data Protection

### Raw Data (ABSOLUTE PROTECTION)
```
Location: data/raw/
Permission: READ ONLY
Modification: NEVER allowed
Deletion: NEVER allowed

If user requests modification:
→ Refuse politely
→ Suggest creating processed version
→ Explain data integrity importance
```

### Processed Data (CONTROLLED)
```
Location: data/processed/
Permission: Write allowed (with notification)
Modification: Allowed (log changes)
Deletion: Requires approval

Before modification:
□ Notify user of which files will be modified
□ Explain transformation/processing steps
□ Offer to version previous version
```

### Analysis Results (FLEXIBLE)
```
Location: results/
Permission: Write/Edit allowed
Modification: Allowed (version control recommended)
Deletion: Requires approval for final results

Best practice:
- Timestamp result directories
- Keep analysis script with results
- Version control via git
```
