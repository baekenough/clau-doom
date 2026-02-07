# [MUST] Language & Delegation Policy

> **Priority**: MUST - Never violate
> **ID**: R000

## Core Principles

### 1. User Input Language
```
User prompts are in Korean.
Always understand and process Korean input.
```

### 2. Output Language

| Context | Language | Example |
|---------|----------|---------|
| User communication | Korean | 상태 보고, 질문, 설명 |
| Code | English | variables, functions, comments |
| File contents | English | .md, .yaml, configs |
| Commit messages | English | git commits |
| Error messages to user | Korean | 에러 설명, 해결 방안 |
| Research documents | English | EXPERIMENT_ORDER, REPORT |
| Statistical output | English | ANOVA tables, p-values |
| DOE designs | English | Factor names, level descriptions |
| Experiment logs | English | Observations, measurements |

### 3. Delegation Model
```
User does NOT directly edit files.
User delegates ALL file operations to AI agent.

User → (Korean prompt) → Agent → (file operations)
```

### 4. Context Efficiency
```
All file contents in English for:
- Token efficiency
- Consistent parsing
- Universal compatibility
- Academic publication readiness
- Statistical analysis compatibility
- Reproducible research standards
```

## Examples

### Correct
```
User: "새로운 DOE 디자인을 만들어줘"
Agent: "DOE 디자인을 생성하겠습니다." (Korean to user)
Agent writes DOE_DESIGN_*.md in English
```

### Incorrect
```
Agent writes: "# 실험 설계" in file  ← Wrong
Agent writes: "# Experimental Design" in file     ← Correct
```

## File Naming

| Type | Convention | Example |
|------|------------|---------|
| Rules | `{PRIORITY}-{name}.md` | `MUST-safety.md` |
| Agents | `{name}.md` | `research-pi.md` |
| Skills | `SKILL.md` | In skill directory |
| Research docs | `UPPERCASE.md` | `EXPERIMENT_ORDER_021.md` |
| DOE designs | `DOE_DESIGN_{id}.md` | `DOE_DESIGN_001.md` |
| Experiment reports | `REPORT_{id}.md` | `REPORT_021_ANOVA.md` |
| Data files | `snake_case.csv` | `experiment_021_data.csv` |

## Research-Specific Language Rules

### Statistical Terminology
```
Always use English for:
- Factor names (e.g., "Temperature", not "온도")
- Response variables (e.g., "Yield", not "수율")
- Statistical terms (e.g., "p-value", not "p-값")
- Analysis method names (e.g., "ANOVA", not "분산분석")
```

### Experiment Documentation
```
Structure in English:
- Objective
- Factors and levels
- Response variables
- Experimental design (CCD, BBD, etc.)
- Analysis method
- Results and conclusions
```

### Code Comments
```
Python/R scripts:
- Variable names: English
- Function names: English
- Comments: English
- Docstrings: English

This ensures:
- Compatibility with statistical packages
- Publication-ready code
- Collaboration with international researchers
```
