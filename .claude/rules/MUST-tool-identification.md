# [MUST] Tool Usage Identification Rules

> **Priority**: MUST - ENFORCED, NO EXCEPTIONS
> **ID**: R008
> **Violation**: Immediate correction required

## CRITICAL

**EVERY tool call MUST be prefixed with agent and model identification. This is NON-NEGOTIABLE.**

```
Before EVERY tool call, output:
[agent-name][model] → Tool: <tool-name>
[agent-name][model] → Target: <file/path/url>
```

Failure to identify tool usage = Rule violation = Must be corrected immediately.

### Self-Check Before EVERY Tool Call

```
╔══════════════════════════════════════════════════════════════════╗
║  BEFORE INVOKING ANY TOOL, ASK YOURSELF:                         ║
║                                                                   ║
║  1. Did I output the tool identification line with MODEL?        ║
║     [agent-name][model] → Tool: <tool-name>                      ║
║     [agent-name][model] → Target: <target>                       ║
║                                                                   ║
║  2. Am I about to call multiple tools in parallel?               ║
║     → EACH tool needs its own identification line                ║
║     → List all identifications BEFORE the tool calls             ║
║                                                                   ║
║  If NO to #1 → STOP. Output identification FIRST.                ║
╚══════════════════════════════════════════════════════════════════╝
```

### Model Values

| Model | When to Use |
|-------|-------------|
| `opus` | Complex reasoning, experimental design, statistical modeling |
| `sonnet` | General tasks, data processing, code generation (default) |
| `haiku` | Fast simple tasks, file search, data validation |

### Common Violations to Avoid

```
❌ WRONG: Calling tools without identification
   "DOE 설계를 생성하겠습니다."
   <tool_call>Write(...)</tool_call>

❌ WRONG: Missing model in identification
   [research-pi] → Tool: Write
   [research-pi] → Target: designs/DOE_DESIGN_023.md

✓ CORRECT: Always identify with agent AND model
   "DOE 설계를 생성하겠습니다."
   [research-pi][opus] → Tool: Write
   [research-pi][opus] → Target: designs/DOE_DESIGN_023.md
   <tool_call>Write(...)</tool_call>

❌ WRONG: Parallel calls without listing all identifications
   <tool_call>Read(data1.csv)</tool_call>
   <tool_call>Read(data2.csv)</tool_call>
   <tool_call>Bash(Rscript analysis.R)</tool_call>

✓ CORRECT: List all identifications with models, then call
   [research-analyst][opus] → Tool: Read
   [research-analyst][opus] → Target: data/processed/exp_021.csv
   [research-analyst][opus] → Tool: Read
   [research-analyst][opus] → Target: data/processed/exp_022.csv
   [research-analyst][opus] → Tool: Bash
   [research-analyst][opus] → Running: Rscript analysis/anova.R
   <tool_call>Read(data1.csv)</tool_call>
   <tool_call>Read(data2.csv)</tool_call>
   <tool_call>Bash(Rscript analysis.R)</tool_call>
```

## Purpose

Display which agent is using which tool for transparency and debugging in research workflows. This extends R007 (Agent Identification) to cover tool operations.

## Tool Usage Format

When invoking a tool, prefix with agent and model identification:

```
[agent-name][model] → Tool: <tool-name>
```

### Research Agent Examples

```
[research-pi][opus] → Tool: Write
[research-pi][opus] → Writing: designs/DOE_DESIGN_023.md

[research-analyst][opus] → Tool: Bash
[research-analyst][opus] → Running: Rscript analysis/anova_021.R

[research-data-engineer][sonnet] → Tool: Read
[research-data-engineer][sonnet] → Reading: data/raw/experiment_022/measurements.csv

[lang-python-expert][sonnet] → Tool: Edit
[lang-python-expert][sonnet] → Editing: scripts/data_processing.py
```

## Extended Format (Verbose)

For detailed tracking:

```
┌─ Agent: research-pi (research)
├─ Model: opus
├─ Skill: doe-design
├─ Tool: Write
└─ Target: designs/DOE_DESIGN_023.md
```

## Tool Categories

| Category | Tools | Format |
|----------|-------|--------|
| File Read | Read, Glob, Grep | `→ Reading:` / `→ Searching:` |
| File Write | Write, Edit | `→ Writing:` / `→ Editing:` |
| Network | WebFetch | `→ Fetching:` |
| Execution | Bash, Task | `→ Running:` / `→ Spawning:` |

## Research-Specific Tool Usage

### Statistical Analysis
```
[research-analyst][opus] → Tool: Bash
[research-analyst][opus] → Running: Rscript analysis/factorial_anova.R
[research-analyst][opus] → Input: data/processed/experiment_021_clean.csv
[research-analyst][opus] → Output: results/021/anova_results.txt
```

### Data Processing
```
[research-data-engineer][sonnet] → Tool: Bash
[research-data-engineer][sonnet] → Running: python scripts/clean_data.py
[research-data-engineer][sonnet] → Input: data/raw/experiment_022/
[research-data-engineer][sonnet] → Output: data/processed/experiment_022_clean.csv
```

### DOE Design Generation
```
[research-pi][opus] → Tool: Write
[research-pi][opus] → Writing: designs/DOE_DESIGN_024.md
[research-pi][opus] → Design: 3-factor CCD with 17 runs
```

## When to Display

| Situation | Display |
|-----------|---------|
| Reading data files | Agent + model + file path |
| Writing results | Agent + model + file path |
| Running statistical scripts | Agent + model + command + I/O files |
| Searching files | Agent + model + pattern |
| Fetching references | Agent + model + URL |

## Simplified Format

For inline operations:

```
[research-pi][opus] → Write: designs/DOE_DESIGN_024.md
[research-analyst][opus] → Bash: Rscript analysis/anova.R
[lang-r-expert][sonnet] → Edit: scripts/regression_model.R
```

## Integration with R007

R008 extends R007 for tool operations:

```
┌─ Agent: research-pi (research)
├─ Model: opus
├─ Skill: doe-design
└─ Task: Creating 3-factor CCD

[research-pi][opus] → Write: designs/DOE_DESIGN_024.md

[Done] DOE design created (17 runs)
```

## Task Tool Display Format

When spawning subagents via the Task tool, the display MUST use the actual `subagent_type` parameter:

```
Task(subagent_type):model → description
```

### Examples

```
[research-pi][opus] → Spawning parallel analysis agents:
  [1] Task(research-analyst):opus → ANOVA on experiment 021
  [2] Task(research-analyst):opus → ANOVA on experiment 022
  [3] Task(research-data-engineer):sonnet → Validate data quality
```

### Rules

- `subagent_type` MUST match the actual Task tool parameter value
- Custom/invented names are NOT allowed
- Model specification shows cost/performance intent

## Research Workflow Example

```
┌─ Agent: research-pi (research)
├─ Model: opus
├─ Skill: doe-design
└─ Task: Designing 3-factor optimization study

Step 1: Define factors
[research-pi][opus] → Read: guides/doe/factor-selection.md

Step 2: Create DOE design
[research-pi][opus] → Write: designs/DOE_DESIGN_024.md
[research-pi][opus] → Design type: Central Composite Design
[research-pi][opus] → Factors: 3
[research-pi][opus] → Runs: 17 (8 factorial + 6 axial + 3 center)

Step 3: Generate experiment order
[research-pi][opus] → Write: designs/EXPERIMENT_ORDER_024.md
[research-pi][opus] → Randomization: Complete

[Done] Experimental design complete
```

## Benefits

1. **Debugging**: Know which agent performed which operation
2. **Transparency**: User sees all agent activities
3. **Audit Trail**: Track file changes and analysis runs by agent
4. **Error Attribution**: Identify which agent caused issues
5. **Research Reproducibility**: Clear record of who did what
6. **Model Cost Tracking**: Understand which models used for which tasks

## Implementation

Agents should:
1. Identify themselves before tool operations
2. Include tool name and target
3. Use consistent format across all tools
4. Group related operations together
5. Show input/output files for analysis operations
