# [MUST] Agent Identification Rules

> **Priority**: MUST - ENFORCED, NO EXCEPTIONS
> **ID**: R007
> **Violation**: Immediate correction required

## CRITICAL

**EVERY response MUST start with agent identification. This is NON-NEGOTIABLE.**

Failure to include agent identification = Rule violation = Must be corrected immediately.

## Purpose

Display which agent is responding and which skills are being used for transparency and traceability in research workflows.

## Response Header Format

Every response MUST start with an agent identification block:

```
┌─ Agent: {agent-name} ({agent-type})
├─ Skill: {skill-name} (if applicable)
└─ Task: {brief-task-description}
```

## Examples

### Research Agent Response
```
┌─ Agent: research-pi (research)
├─ Skill: doe-design
└─ Task: Creating Central Composite Design

[Response content...]
```

### Analysis Agent Response
```
┌─ Agent: research-analyst (research)
├─ Skill: anova
└─ Task: Analyzing factor effects

[Response content...]
```

### Single Agent Response
```
┌─ Agent: mgr-creator (manager)
└─ Task: Creating new agent

[Response content...]
```

### With Skill Usage
```
┌─ Agent: lang-python-expert (sw-engineer)
├─ Skill: python-best-practices
└─ Task: Optimizing data processing script

[Response content...]
```

### Multiple Skills
```
┌─ Agent: research-pi (research)
├─ Skills: doe-design, response-surface-methodology
└─ Task: Full experimental design

[Response content...]
```

### No Specific Agent (Default)
```
┌─ Agent: claude (default)
└─ Task: General assistance

[Response content...]
```

## When to Display

| Situation | Display |
|-----------|---------|
| Research task | Full header with research agent |
| Agent-specific task | Full header with agent |
| Using skill | Include skill name |
| General conversation | "claude (default)" |
| Multiple agents | Show primary agent |

## Agent Types

| Type | Symbol | Example |
|------|--------|---------|
| research | 🔬 | research-pi, research-analyst |
| sw-engineer | ⚙️ | lang-python-expert, lang-r-expert |
| manager | 🔧 | mgr-creator, mgr-updater |
| system | 🖥️ | sys-memory-keeper |
| default | 💬 | claude |

## Simplified Format (Optional)

For brief responses, use inline format:

```
[research-pi] Creating DOE design...
```

Or with skill:

```
[research-analyst → anova] Running factorial analysis...
```

## Status Updates

During long tasks, show progress with agent context:

```
┌─ Agent: research-analyst (research)
├─ Skill: anova
└─ Task: Analyzing 5 experiments

[Progress] Loading data (1/5)
[Progress] Running ANOVA (2/5)
[Progress] Generating diagnostic plots (3/5)
[Progress] Testing assumptions (4/5)
[Progress] Creating report (5/5)

[Done] Analysis complete
```

## Research-Specific Examples

### DOE Design Task
```
┌─ Agent: research-pi (research)
├─ Skills: doe-design, experimental-planning
└─ Task: Designing 3-factor CCD experiment

Factors identified:
- Temperature (150-200°C)
- Pressure (1-5 bar)
- Time (30-90 min)

Creating Central Composite Design with:
- 8 factorial points
- 6 axial points (α=1.682)
- 3 center points
- Total: 17 runs

[research-pi] → Write: designs/DOE_DESIGN_023.md
```

### Statistical Analysis Task
```
┌─ Agent: research-analyst (research)
├─ Skill: anova
└─ Task: Factorial ANOVA for experiment 021

[research-analyst] → Read: data/processed/experiment_021_clean.csv
[research-analyst] → Bash: Rscript analysis/anova_021.R

ANOVA Results:
- Temperature: F=45.2, p<0.001 (significant)
- Pressure: F=12.8, p=0.003 (significant)
- Temp×Press: F=8.4, p=0.012 (significant)

[research-analyst] → Write: results/021/ANOVA_REPORT.md
```

### Data Processing Task
```
┌─ Agent: research-data-engineer (research)
├─ Skill: data-cleaning
└─ Task: Cleaning experiment 022 data

[research-data-engineer] → Read: data/raw/experiment_022/measurements.csv

Data quality check:
- 120 observations loaded
- 3 outliers detected (2.5%)
- 0 missing values
- All within expected ranges

[research-data-engineer] → Write: data/processed/experiment_022_clean.csv
```

## Integration with Research Workflow

```
User (Korean): "3개 인자로 CCD 설계해줘"
    ↓
┌─ Agent: research-pi (research)
├─ Skill: doe-design
└─ Task: Creating 3-factor CCD design
    ↓
[research-pi] → Write: designs/DOE_DESIGN_024.md
    ↓
User receives: Korean explanation + English design file
```
