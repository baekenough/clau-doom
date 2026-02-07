---
name: research-logging
description: Research logging formats for experiment logs, findings, hypotheses, and audit trail compliance
user-invocable: false
---

# Research Logging Skill

Standardized formats for research documentation: experiment logs, statistical findings, hypothesis backlog, and cross-referencing. Ensures reproducibility and audit trail compliance.

## RESEARCH_LOG.md Entry Format

### Entry Structure

```markdown
## [2026-02-07] — [Factorial Screening of Combat Parameters]

### Context
- **Experiment ID**: EXP-001
- **Phase**: Phase 1 (Factorial Screening)
- **Generation**: GEN-005
- **Hypothesis**: H-003 (retreat_threshold and ammo_conservation interact)
- **Design**: 2^3 Full Factorial with center points

### Hypothesis
Retreat threshold and ammo conservation have a synergistic interaction effect
on kill rate: conservative retreat combined with strict ammo conservation
produces disproportionately high kill rates compared to their individual effects.

### Design
- **Factors**: retreat_threshold [-1,+1], ammo_conservation [-1,+1], exploration_priority [-1,+1]
- **Runs**: 11 design points x 3 replicates = 33 total runs
- **Seeds**: [42, 137, 256]
- **Response**: kill_rate (primary), survival_time, ammo_efficiency
- **Blocking**: None
- **Center points**: 3 (for curvature test)

### Result
- **ANOVA**: A (retreat) significant [STAT:F(1,16)=12.34, p=0.002], B (ammo) significant [STAT:F(1,16)=6.30, p=0.021], A*B interaction significant [STAT:F(1,16)=8.64, p=0.008]
- **Effect sizes**: A [STAT:effect_size=partial_eta2=0.44], A*B [STAT:effect_size=partial_eta2=0.35]
- **Curvature test**: [STAT:F(1,16)=3.45, p=0.07] (marginal, not yet significant)
- **Power**: Achieved power = 0.87 for observed effect
- **Key finding**: retreat_threshold * ammo_conservation interaction is the second largest effect, confirming H-003

### Next Steps
1. Run Phase 1 confirmation experiment (different seed set)
2. If curvature becomes significant: augment to CCD (Phase 3)
3. Update FMEA: FM-005 for agents with low retreat + low ammo (stuck in combat)
4. Update TOPSIS weights: increase ammo_efficiency weight from 0.15 to 0.20

---
```

### Entry Rules

- Date in ISO format: [YYYY-MM-DD]
- Title concise but descriptive
- Always link to Experiment ID, Hypothesis ID
- Statistical results use [STAT:...] markers for automated extraction
- Next Steps must be actionable and specific

## Statistical Markers

### Marker Format

Statistical results are tagged with `[STAT:...]` markers for automated parsing and cross-referencing.

### Supported Marker Types

**p-values**:
```
[STAT:p=0.003]
[STAT:p<0.001]
[STAT:p=0.045]
```

**Confidence intervals**:
```
[STAT:ci=95%: 2.3-4.7]
[STAT:ci=99%: 1.8-5.2]
[STAT:ci=95%: 0.63-0.71]
```

**Effect sizes**:
```
[STAT:effect_size=Cohen's d=0.82]
[STAT:effect_size=partial_eta2=0.44]
[STAT:effect_size=omega2=0.38]
[STAT:effect_size=R2=0.67]
```

**Test statistics**:
```
[STAT:F(1,16)=12.34, p=0.002]
[STAT:t(23)=3.45, p=0.002]
[STAT:chi2(4)=15.67, p=0.003]
[STAT:H(3)=12.45, p=0.006]    (Kruskal-Wallis)
[STAT:W=0.95, p=0.34]          (Shapiro-Wilk)
[STAT:A2=0.34, p=0.48]         (Anderson-Darling)
```

**Power analysis**:
```
[STAT:power=0.87, alpha=0.05, N=33]
[STAT:power=0.72, need_N=48 for power=0.80]
```

**Capability indices**:
```
[STAT:Cp=1.45]
[STAT:Cpk=1.23]
[STAT:Pp=1.38]
```

**SPC signals**:
```
[STAT:SPC:rule1_violation at GEN-012]
[STAT:SPC:trend_detected GEN-008 to GEN-014]
```

### Compound Markers

For full ANOVA reporting:
```
Main effect A: [STAT:F(1,16)=12.34, p=0.002] [STAT:effect_size=partial_eta2=0.44]
```

### Automated Extraction

Markers can be extracted with regex:
```
\[STAT:([^\]]+)\]
```

This enables:
- Automated summary of all statistical results
- Cross-validation of reported statistics
- Generation of statistical appendix

## FINDINGS.md Entry Format

### Finding Structure

```markdown
## F-003: Retreat-Ammo Interaction Drives Kill Rate

### Metadata
- **Finding ID**: F-003
- **Date**: 2026-02-07
- **Hypothesis ID**: H-003
- **Experiment IDs**: EXP-001, EXP-002
- **Trust Level**: ESTABLISHED
- **Evidence Strength**: Strong

### Statement
The interaction between retreat_threshold and ammo_conservation has a
larger effect on kill rate than either factor alone. Agents with moderate
retreat threshold (0.35-0.45) and high ammo conservation (0.70-0.80)
achieve 23% higher kill rates than predicted by main effects.

### Evidence
1. **EXP-001** (2^3 Factorial):
   - A*B interaction: [STAT:F(1,16)=8.64, p=0.008] [STAT:effect_size=partial_eta2=0.35]
   - Confirmed across 3 seed replicates
   - Residual diagnostics: all assumptions met

2. **EXP-002** (Confirmation):
   - A*B interaction: [STAT:F(1,16)=7.92, p=0.012] [STAT:effect_size=partial_eta2=0.33]
   - Different seed set, consistent results
   - Power: [STAT:power=0.85, alpha=0.05, N=33]

### Implications
- Evolution should favor agents with moderate retreat + high ammo conservation
- TOPSIS weights should increase ammo_efficiency importance
- DOE Phase 2 should keep retreat and ammo as paired factors

### Limitations
- Tested only in Phase 1 (linear model, no curvature)
- exploration_priority not significant (may become important in later phases)
- Limited to 2-level design (optimal levels within range unknown)

### Cross-References
- Hypothesis: H-003
- Experiments: EXP-001 (RESEARCH_LOG.md#2026-02-07), EXP-002 (RESEARCH_LOG.md#2026-02-08)
- FMEA: FM-005 (updated RPN based on this finding)
- Generation impact: GEN-006+ (TOPSIS weights updated)

---
```

### Trust Levels

| Level | Definition | Requirements |
|-------|-----------|-------------|
| PRELIMINARY | Single experiment, needs confirmation | 1 experiment |
| EMERGING | Replicated once, consistent direction | 2 experiments |
| ESTABLISHED | Multiple replications, strong evidence | 3+ experiments, consistent |
| ROBUST | Holds across conditions and phases | Cross-phase, cross-design |
| FOUNDATIONAL | Core insight, unlikely to be overturned | Extensive evidence, theoretical backing |

### Evidence Strength

| Strength | Criteria |
|----------|---------|
| Weak | p < 0.05, small effect, limited replication |
| Moderate | p < 0.01, medium effect, 2 replications |
| Strong | p < 0.001, large effect, 3+ replications |
| Very Strong | Consistent across designs, phases, robust to assumptions |

## HYPOTHESIS_BACKLOG.md Format

### Hypothesis Entry

```markdown
## H-003: Retreat-Ammo Interaction

### Metadata
- **ID**: H-003
- **Created**: 2026-02-05
- **Priority**: HIGH
- **Status**: CONFIRMED
- **Source**: Exploratory analysis of GEN-003 data

### Statement
Retreat threshold and ammo conservation interact: the combination of moderate
retreat (0.35-0.45) with high ammo conservation (0.70-0.80) produces synergistic
effects on kill rate beyond what either factor achieves independently.

### Rationale
Agents that retreat judiciously preserve health AND ammo, enabling sustained
combat effectiveness. Too much retreat wastes ammo on partial engagements.
Too little retreat depletes health rapidly.

### Test Plan
1. 2^3 factorial with retreat, ammo, exploration (EXP-001)
2. Check A*B interaction in ANOVA
3. If significant: confirmation experiment with new seeds (EXP-002)
4. If confirmed: augment to RSM for optimal level finding

### Results
- EXP-001: Confirmed [STAT:p=0.008]
- EXP-002: Confirmed [STAT:p=0.012]
- Finding: F-003

---
```

### Hypothesis Status Flow

```
PROPOSED → TESTABLE → TESTING → CONFIRMED / REJECTED / INCONCLUSIVE

PROPOSED:     Idea captured, not yet designed
TESTABLE:     Experiment designed, ready to run
TESTING:      Experiment in progress
CONFIRMED:    Evidence supports hypothesis
REJECTED:     Evidence contradicts hypothesis
INCONCLUSIVE: Insufficient evidence, needs more data
SUPERSEDED:   Replaced by more specific hypothesis
```

### Priority Levels

| Priority | Criteria | Action |
|----------|---------|--------|
| CRITICAL | Blocks other experiments | Test immediately |
| HIGH | Significant potential impact | Test in next batch |
| MEDIUM | Moderate expected value | Queue for testing |
| LOW | Exploratory, low expected impact | Test if resources allow |
| DEFERRED | Not currently relevant | Archive for later |

## Cross-Referencing Between Documents

### Reference Format

```
Within RESEARCH_LOG.md:
  See Finding F-003 in FINDINGS.md
  Tests Hypothesis H-003 from HYPOTHESIS_BACKLOG.md
  Updates FMEA FM-005

Within FINDINGS.md:
  Based on experiments: EXP-001 (RESEARCH_LOG.md#2026-02-07), EXP-002
  Tests hypothesis: H-003 (HYPOTHESIS_BACKLOG.md)
  Impacts: GEN-006+ evolution strategy

Within HYPOTHESIS_BACKLOG.md:
  Tested by: EXP-001, EXP-002
  Result: Finding F-003 (FINDINGS.md)
```

### Traceability Matrix

```
Hypothesis  → Experiment(s) → Finding(s) → Impact(s)

H-003       → EXP-001       → F-003      → TOPSIS weights
            → EXP-002                     → Evolution strategy
                                          → FMEA FM-005 update
```

### ID Conventions

| Entity | Pattern | Example |
|--------|---------|---------|
| Hypothesis | H-{seq} | H-003 |
| Experiment | EXP-{seq} | EXP-001 |
| Finding | F-{seq} | F-003 |
| FMEA Item | FM-{seq} | FM-005 |
| Generation | GEN-{seq} | GEN-005 |
| Strategy Doc | STR-{gen}-{seq} | STR-GEN005-003 |
| Run | {exp}-R{point}-S{seed} | EXP001-R03-S2 |

## Audit Trail Compliance

### What Must Be Logged

Every decision and action that affects research outcomes:

```
1. Experiment design decisions (why this design type?)
2. Factor selection and ranges (why these factors? why these levels?)
3. Seed selection (why these seeds?)
4. Statistical method choice (why ANOVA vs Kruskal-Wallis?)
5. Assumption violations and remediation (what failed, what was done?)
6. Phase transitions (what triggered the transition?)
7. Evolution parameter changes (why change mutation rate?)
8. TOPSIS weight changes (what prompted re-calibration?)
9. Document retirement decisions (why was strategy deprecated?)
10. Manual overrides of automated decisions
```

### Audit Log Entry

```markdown
### AUDIT: [2026-02-07T14:30:00Z] Phase Transition 1→3

- **Actor**: research-pi (opus model)
- **Action**: Transition from Phase 1 (Factorial) to Phase 3 (RSM)
- **Trigger**: Curvature test marginal in EXP-001 [STAT:p=0.07], significant in EXP-002 [STAT:p=0.03]
- **Rationale**: Two experiments show curvature trend; augmenting to CCD will model quadratic effects
- **Impact**: Design changes from 2^3 factorial to CCD with 6 axial points + 6 center points
- **Approved by**: User (2026-02-07T14:35:00Z)
```

### Reproducibility Requirements

Every experiment must be reproducible from its log entry:

```
Required for reproducibility:
  [ ] DOE design matrix (exact factor levels)
  [ ] Random seeds used
  [ ] Agent configuration files (exact parameters)
  [ ] Container versions (Docker image tags)
  [ ] Game engine version
  [ ] DuckDB schema version
  [ ] Statistical software/method used
  [ ] Any data transformations applied
```

### Log File Organization

```
research/
  RESEARCH_LOG.md          # Chronological experiment log
  FINDINGS.md              # Confirmed findings registry
  HYPOTHESIS_BACKLOG.md    # Hypothesis tracker
  FMEA_REGISTRY.md         # Failure mode registry
  AUDIT_LOG.md             # Decision audit trail
  experiments/
    EXP-001/
      design.yaml          # DOE matrix specification
      results.csv          # Raw results
      report.md            # EXPERIMENT_REPORT
      anova.txt            # ANOVA output
    EXP-002/
      ...
```

### Retention Policy

| Document | Retention | Archive |
|----------|-----------|---------|
| RESEARCH_LOG.md | Permanent | Git |
| FINDINGS.md | Permanent | Git |
| HYPOTHESIS_BACKLOG.md | Permanent | Git |
| Raw experiment data | Permanent | DuckDB + backup |
| Container logs | 30 days | Compressed archive |
| Intermediate outputs | 7 days | Delete after extraction |
