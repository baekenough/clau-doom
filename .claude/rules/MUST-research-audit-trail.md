# [MUST] Research Audit Trail Rules

> **Priority**: MUST - Never violate
> **ID**: R102
> **Purpose**: Maintain complete traceability from hypothesis to finding

## CRITICAL

**Every finding MUST trace back through the complete research process.**

```
╔══════════════════════════════════════════════════════════════════╗
║  AUDIT CHAIN (NON-NEGOTIABLE)                                    ║
║                                                                   ║
║  Every finding MUST trace back through:                          ║
║                                                                   ║
║  HYPOTHESIS_BACKLOG.md                                           ║
║         ↓                                                        ║
║  EXPERIMENT_ORDER_{ID}.md                                        ║
║         ↓                                                        ║
║  EXPERIMENT_REPORT_{ID}.md                                       ║
║         ↓                                                        ║
║  FINDINGS.md                                                     ║
║                                                                   ║
║  Breaking this chain = Violation                                 ║
╚══════════════════════════════════════════════════════════════════╝
```

## Required Documents

| Document | Author | Purpose | Format |
|----------|--------|---------|--------|
| **RESEARCH_LOG.md** | research-pi | Cumulative research journal | Chronological entries |
| **HYPOTHESIS_BACKLOG.md** | research-pi | Hypothesis queue with priorities | Prioritized list |
| **EXPERIMENT_ORDER_{ID}.md** | research-pi | DOE design, factors, levels, seeds | Structured order |
| **EXPERIMENT_REPORT_{ID}.md** | research-analyst | ANOVA results, diagnostics, recommendations | Statistical report |
| **FINDINGS.md** | research-pi | Confirmed findings with evidence | Structured findings |
| **DOE_CATALOG.md** | research-pi | Design type catalog and usage history | Reference guide |
| **SPC_STATUS.md** | research-analyst | Control chart status and signals | Real-time monitoring |
| **FMEA_REGISTRY.md** | research-evolution-mgr | Failure modes, RPN trends | Risk tracking |

## Traceability Requirements

Every entry in FINDINGS.md MUST include:

```yaml
finding_entry:
  hypothesis_id: "H-042"  # From HYPOTHESIS_BACKLOG.md
  experiment_order_id: "DOE-042"  # From EXPERIMENT_ORDER_042.md
  experiment_report_id: "RPT-042"  # From EXPERIMENT_REPORT_042.md
  trust_level: "HIGH" | "MEDIUM" | "LOW"
  statistical_markers:
    - "[STAT:p=0.003]"
    - "[STAT:ci=95%: 2.3-4.7]"
    - "[STAT:effect_size=Cohen's d=0.82]"
  date_adopted: "2024-12-15"
  phase: 1  # DOE phase when adopted
```

### Example Finding Entry

```markdown
## F-042: Memory-Strength Interaction Significant

**Hypothesis**: H-042 — Memory and strength interact to affect kill efficiency.

**Experiment Order**: DOE-042 (2x3 factorial, n=180 episodes)

**Experiment Report**: RPT-042

**Evidence**:
- Interaction significant [STAT:p=0.002] [STAT:f=F(4,174)=6.78]
- Effect size large [STAT:eta2=partial η²=0.17]
- Sample size adequate [STAT:n=180] [STAT:power=1-β=0.92]
- Residuals clean (normality p=0.42, equal variance p=0.18)

**Trust Level**: HIGH

**Adopted**: 2024-12-15 (Phase 1)

**Interpretation**:
Memory enhances kill efficiency more at higher strength levels.
At strength=0.3, memory 0.5→0.9 increases kills by +8.2 [STAT:ci=95%: 5.1-11.3].
At strength=0.7, memory 0.5→0.9 increases kills by +18.7 [STAT:ci=95%: 14.5-22.9].

**Recommended Agent Config**:
For high-kill playstyles, use memory ≥ 0.7 AND strength ≥ 0.5.

**Next Steps**:
Phase 2: RSM to find optimal memory-strength combination.
```

## Research Log Entry Format

```markdown
## [DATE] — [TITLE]

### Context
What prompted this research direction.

### Hypothesis
H_{ID}: {statement}
Priority: {High|Medium|Low}
Rationale: {why this hypothesis matters}

### Design
DOE type: {factorial|Taguchi|RSM|split-plot}
Factors: {list with levels}
Sample size: {n per condition, total episodes}
Expected power: {1-β estimate}

### Result
[STAT:p=X.XXX] [STAT:effect_size=Y.YY] [STAT:n=ZZZ]
Conclusion: {adopted|rejected|follow-up}
Trust level: {HIGH|MEDIUM|LOW|UNTRUSTED}

### Next Steps
{next experiment or phase transition}
```

### Example Research Log Entry

```markdown
## 2024-12-15 — Memory-Strength Interaction Confirmed

### Context
Phase 1 main effects study found memory and strength both significant.
Natural next question: Do they interact?

### Hypothesis
H-042: Memory and strength interact to affect kill efficiency.
Priority: High
Rationale: If interaction exists, agents need joint optimization, not separate tuning.

### Design
DOE type: 2x3 full factorial
Factors:
  - Memory: [0.5, 0.7, 0.9]
  - Strength: [0.3, 0.5, 0.7]
Sample size: 30 episodes per cell, 180 total
Expected power: 1-β ≈ 0.90 for medium effect size (f=0.25)

### Result
[STAT:p=0.002] [STAT:f=F(4,174)=6.78] [STAT:eta2=partial η²=0.17]
[STAT:n=180] [STAT:power=1-β=0.92]
Conclusion: Adopted to FINDINGS.md (F-042)
Trust level: HIGH

### Next Steps
Phase 2: RSM Central Composite Design around high-memory, high-strength region.
Target: Find optimal (memory, strength) combination for kill efficiency.
```

## Hypothesis Backlog Format

```markdown
# Hypothesis Backlog

## Active Hypotheses

### H-042: Memory-Strength Interaction [HIGH PRIORITY]
**Statement**: Memory and strength interact to affect kill efficiency.
**Rationale**: Main effects both significant, interaction untested.
**Status**: Experiment ordered (DOE-042)
**Date Added**: 2024-12-10

### H-043: Curiosity-Memory Synergy [MEDIUM PRIORITY]
**Statement**: Curiosity amplifies memory benefits.
**Rationale**: Curiosity drives exploration, memory retains discoveries.
**Status**: Queued (Phase 1)
**Date Added**: 2024-12-12

## Completed Hypotheses

### H-041: Memory Main Effect [ADOPTED]
**Statement**: Higher memory increases kill efficiency.
**Evidence**: RPT-041, F-041
**Trust**: HIGH
**Date Adopted**: 2024-12-08

### H-040: Strength Main Effect [ADOPTED]
**Statement**: Higher strength increases damage per hit.
**Evidence**: RPT-040, F-040
**Trust**: HIGH
**Date Adopted**: 2024-12-07

## Rejected Hypotheses

### H-039: Speed-Accuracy Tradeoff [REJECTED]
**Statement**: Higher speed reduces aim accuracy.
**Evidence**: RPT-039
**Trust**: UNTRUSTED (p=0.18)
**Date Rejected**: 2024-12-05
```

## Document Linkage Examples

### EXPERIMENT_ORDER Links to Hypothesis

```markdown
# EXPERIMENT_ORDER_042.md

## DOE-042: Memory-Strength Interaction

**Hypothesis**: H-042 (from HYPOTHESIS_BACKLOG.md)

**Research Question**: Do memory and strength interact?

[Rest of order...]
```

### EXPERIMENT_REPORT Links to Order

```markdown
# EXPERIMENT_REPORT_042.md

## RPT-042: Memory-Strength Interaction Results

**Experiment Order**: DOE-042 (EXPERIMENT_ORDER_042.md)

**Hypothesis**: H-042

**Design**: 2x3 full factorial

[Statistical results...]
```

### FINDINGS Links to All

```markdown
# FINDINGS.md

## F-042: Memory-Strength Interaction Significant

**Hypothesis**: H-042 (HYPOTHESIS_BACKLOG.md)
**Experiment Order**: DOE-042 (EXPERIMENT_ORDER_042.md)
**Experiment Report**: RPT-042 (EXPERIMENT_REPORT_042.md)

[Trust level, evidence, interpretation...]
```

## Violations

```
╔══════════════════════════════════════════════════════════════════╗
║  VIOLATIONS (ZERO TOLERANCE)                                     ║
║                                                                   ║
║  - Finding without experiment evidence                           ║
║  - Experiment without order document                             ║
║  - Order without hypothesis                                      ║
║  - Breaking the audit chain at any point                         ║
║  - Modifying past documents without version control              ║
║  - Deleting documents from the chain                             ║
║  - Claiming findings without traceability                        ║
╚══════════════════════════════════════════════════════════════════╝
```

## Audit Trail Verification Checklist

```yaml
before_adopting_finding:
  - [ ] Hypothesis exists in HYPOTHESIS_BACKLOG.md
  - [ ] EXPERIMENT_ORDER_{ID}.md created
  - [ ] EXPERIMENT_REPORT_{ID}.md generated
  - [ ] Statistical markers present ([STAT:p], [STAT:ci], etc.)
  - [ ] Trust level assessed (HIGH/MEDIUM/LOW)
  - [ ] All documents cross-referenced
  - [ ] RESEARCH_LOG.md updated
```

## Integration with Other Rules

| Rule | Integration |
|------|-------------|
| R100 (Experiment Integrity) | Audit trail enforces seed sets, ANOVA, diagnostics |
| R101 (PI Boundary) | PI owns audit trail documents, executors implement |
| R010 (Orchestrator) | Main conversation routes to research-pi for traceability |

## Document Storage

```
/Users/sangyi/workspace/research/clau-doom/research/
├── RESEARCH_LOG.md
├── HYPOTHESIS_BACKLOG.md
├── FINDINGS.md
├── DOE_CATALOG.md
├── SPC_STATUS.md
├── FMEA_REGISTRY.md
├── experiments/
│   ├── EXPERIMENT_ORDER_042.md
│   ├── EXPERIMENT_REPORT_042.md
│   ├── EXPERIMENT_ORDER_043.md
│   └── ...
└── archives/
    └── [old experiment files]
```
