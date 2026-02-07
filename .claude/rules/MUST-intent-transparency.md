# [MUST] Intent Transparency Rules

> **Priority**: MUST - Required for user control
> **ID**: R015

## Purpose

Ensure transparency when automatically detecting user intent and routing to agents. Users should always understand why a specific agent was chosen, especially for research tasks.

## Detection Display (REQUIRED)

When intent is detected, display the reasoning:

```
[Intent Detected]
├── Input: "{user input}"
├── Agent: {detected-agent}
├── Confidence: {percentage}%
└── Reason: {explanation}
```

## Confidence Thresholds

| Confidence | Action |
|------------|--------|
| >= 90% | Auto-execute with display |
| 70-89% | Request confirmation |
| < 70% | List options for user to choose |

## Detection Factors

Intent is detected using multiple factors:

```yaml
factors:
  keywords:
    weight: 40
    description: Domain-specific keywords in input
    example: "DOE", "ANOVA", "Python", "실험", "분석"

  file_patterns:
    weight: 30
    description: File extensions mentioned or in context
    example: "*.csv", "*.R", "DOE_DESIGN_*.md"

  action_verbs:
    weight: 20
    description: Action words in user input
    example: "design", "analyze", "clean", "설계", "분석"

  context:
    weight: 10
    description: Recent conversation context
    example: Previous agent used, current working directory
```

## Research-Specific Keywords

```yaml
research_keywords:
  doe_design:
    - DOE, CCD, BBD, factorial
    - 실험설계, 중심합성계획

  statistical_analysis:
    - ANOVA, regression, RSM
    - 분산분석, 회귀분석, 반응표면

  data_processing:
    - clean, process, validate
    - 데이터정제, 전처리, 검증

  optimization:
    - optimize, response surface
    - 최적화, 반응표면
```

## High Confidence Display (>= 90%)

```
[Intent Detected]
├── Input: "3-factor CCD 설계해줘"
├── Agent: research-pi
├── Confidence: 95%
└── Reason: "CCD" keyword (40%) + "설계" action verb (40%) + context (15%)

Executing...
```

## Medium Confidence Display (70-89%)

```
[Intent Detected]
├── Input: "실험 데이터 분석해줘"
├── Agent: research-analyst (?)
├── Confidence: 75%
└── Reason: "실험" keyword (30%) + "분석" action (30%) + .csv context (15%)

Possible alternatives:
  1. research-analyst (75%) - Statistical analysis
  2. research-data-engineer (65%) - Data processing
  3. lang-python-expert (55%) - Script-based analysis

Proceed with research-analyst? [Y/n/1-3]
```

## Low Confidence Display (< 70%)

```
[Intent Unclear]
├── Input: "이 데이터 좀 봐줘"
├── Confidence: < 70%
└── Need more context

Available agents:
  1. research-analyst (statistical analysis)
  2. research-data-engineer (data cleaning/validation)
  3. lang-python-expert (Python data processing)
  4. lang-r-expert (R statistical computing)

Which agent should handle this? [1-4]
```

## Override Syntax

Users can explicitly specify an agent:

```
@{agent-name} {command}
```

Examples:
```
@research-pi CCD 설계해줘
@research-analyst 실험 021 ANOVA 돌려줘
@research-data-engineer data/raw/experiment_022/ 정제해줘
```

Override bypasses intent detection:

```
[Override] Agent explicitly specified: research-pi
Executing...
```

## Implementation

### Main Conversation Workflow

```
1. Receive user input
2. Check for explicit override (@agent)
3. If no override:
   a. Extract keywords, file patterns, action verbs
   b. Match against agent triggers
   c. Calculate confidence score
   d. Display detection reasoning
   e. Execute or request confirmation based on threshold
4. Route to selected agent
```

### Detection Log

For debugging and transparency:

```yaml
detection_log:
  input: "3-factor CCD 설계해줘"
  extracted:
    keywords: ["CCD", "3-factor"]
    file_patterns: []
    action_verbs: ["설계"]
  matches:
    - agent: research-pi
      score: 95
      breakdown:
        keyword_ccd: 40
        action_design: 40
        context_research: 15
  selected: research-pi
  confidence: 95%
```

## Agent Triggers

Research agents have defined triggers in routing skills:

```yaml
agents:
  research-pi:
    keywords: [DOE, CCD, BBD, factorial, RSM, "실험설계", "반응표면"]
    file_patterns: ["DOE_DESIGN_*.md", "EXPERIMENT_ORDER_*.md"]
    actions: [design, plan, optimize, "설계", "계획"]
    base_confidence: 40

  research-analyst:
    keywords: [ANOVA, regression, "분산분석", "회귀분석", statistical]
    file_patterns: ["REPORT_*.md", "*.csv"]
    actions: [analyze, test, model, "분석", "검정"]
    base_confidence: 40

  research-data-engineer:
    keywords: [clean, process, validate, "정제", "전처리", "검증"]
    file_patterns: ["data/raw/*", "data/processed/*", "*.csv"]
    actions: [clean, transform, validate, "정제", "변환"]
    base_confidence: 40

  lang-python-expert:
    keywords: [python, pandas, numpy, matplotlib]
    file_patterns: ["*.py", "requirements.txt"]
    actions: [code, script, implement, "코드", "스크립트"]
    base_confidence: 40

  lang-r-expert:
    keywords: [R, ggplot, dplyr, "R언어"]
    file_patterns: ["*.R", "*.Rmd"]
    actions: [code, script, analyze, "코드", "분석"]
    base_confidence: 40
```

## Research Workflow Examples

### DOE Design Intent
```
User: "온도, 압력, 시간으로 CCD 만들어줘"

[Intent Detected]
├── Input: "온도, 압력, 시간으로 CCD 만들어줘"
├── Agent: research-pi
├── Confidence: 95%
└── Reason:
    - "CCD" keyword (40%)
    - "만들어줘" create action (35%)
    - 3 factors mentioned (20%)

Routing to research-pi for DOE design...
```

### Statistical Analysis Intent
```
User: "실험 021 ANOVA 돌려줘"

[Intent Detected]
├── Input: "실험 021 ANOVA 돌려줘"
├── Agent: research-analyst
├── Confidence: 92%
└── Reason:
    - "ANOVA" keyword (40%)
    - "실험 021" experimental context (30%)
    - "돌려줘" run action (22%)

Routing to research-analyst for statistical analysis...
```

### Ambiguous Intent
```
User: "데이터 처리해줘"

[Intent Unclear]
├── Input: "데이터 처리해줘"
├── Confidence: 68%
└── Multiple interpretations:
    1. research-data-engineer (68%) - Data cleaning
    2. lang-python-expert (62%) - Script-based processing
    3. research-analyst (55%) - Statistical processing

What type of processing do you need?
- Data cleaning/validation → research-data-engineer
- Python script development → lang-python-expert
- Statistical analysis → research-analyst
```

## Benefits

1. **Transparency**: Users understand agent selection
2. **Control**: Users can override or choose alternatives
3. **Trust**: Clear reasoning builds user confidence
4. **Learning**: Users learn which agents handle what
5. **Debugging**: Clear logs for troubleshooting
6. **Research Clarity**: Distinguishes DOE vs analysis vs data tasks

## Violations

Proceeding without displaying intent reasoning = Rule violation

The user must always know:
- Which agent was selected
- Why it was selected
- What confidence level
- How to override if needed
