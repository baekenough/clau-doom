# clau-doom Research Log

> **Project**: clau-doom — LLM Multi-Agent DOOM Research
> **PI**: Sang Yi
> **Started**: 2026-02-07
> **Status**: Active — Research Design Phase Complete

---

## Entry Template

```
## [DATE] — [TITLE]

### Context
What prompted this research direction.

### Hypothesis
H-{ID}: {statement}
Priority: {High|Medium|Low}
Rationale: {why this hypothesis matters}

### Design
DOE type: {OFAT|factorial|fractional|Taguchi|RSM-CCD|split-plot}
Factors: {list with levels}
Sample size: {n per condition, total episodes}
Expected power: {1-beta estimate}

### Result
[STAT:p=X.XXX] [STAT:effect_size=Y.YY] [STAT:n=ZZZ]
Conclusion: {adopted|rejected|follow-up}
Trust level: {HIGH|MEDIUM|LOW|UNTRUSTED}

### Next Steps
{next experiment or phase transition}
```

---

## 2026-02-07 — Research Design Phase Complete

### Context

The clau-doom project aims to demonstrate that LLM multi-agent DOOM players can systematically improve through RAG experience accumulation, DOE-driven optimization, and generational evolution. Before running experiments, a comprehensive research design phase was conducted across 8 design documents (S1-01 through S2-04) covering literature review, baseline definitions, ablation studies, diversity metrics, and agent teams workflow.

### Deliverables

**Session 1 — Literature Collection**:
- S1-01: Evolution/Collective Intelligence literature review
- S1-02: RAG-based Decision-Making literature review
- S1-03: LLM-as-Scientist methodology literature review
- S1-04: Doom RL Baseline literature review

**Session 2 — Research Design Reinforcement**:
- S2-01: Evaluation Baselines Definition (Random, Rule-Only, RL Reference)
- S2-02: Core Assumption Ablation Design (Document Quality, Scoring Weights, Layer Removal)
- S2-03: Evolutionary Convergence/Diversity Metrics (5 metrics with DuckDB schemas)
- S2-04: Agent Teams Workflow Design (4-session parallel execution)

**Verification**:
- Phase 2 S2 verification completed (see `docs/03_clau-doom-research/meta/PHASE2_S2_VERIFICATION.md`)
- 4 DuckDB schema issues identified and fixed across S2-01, S2-02, S2-04

### Key Decisions

1. **Baselines established**: Random (floor), Rule-Only (midpoint), RL-PPO (ceiling)
2. **Core assumption testable**: Three ablation studies isolate Document Quality, Scoring Accuracy, and Layer Architecture contributions
3. **Ablation execution order**: Layer Removal first (most fundamental), then Document Quality, then Scoring Weights, with decision gates between phases
4. **Master seed set**: 70 seeds defined for baseline comparisons; subsets used for ablation studies
5. **Diversity monitoring**: 5 metrics (entropy, coverage, QD-score, doc pool diversity, effective mutation rate) with 3-level alert escalation

### Hypothesis Backlog

8 initial hypotheses generated (see HYPOTHESIS_BACKLOG.md):
- H-001 through H-005: Baseline and ablation validation hypotheses
- H-006 through H-008: Initial factor screening and interaction hypotheses

### Next Steps

1. Design 5 experiment orders (EXPERIMENT_ORDER_001 through _005) covering baseline comparisons and initial ablation studies
2. Implement measurement framework in DuckDB (schema extensions from S2-01 and S2-02)
3. Begin Phase 0 baseline data collection (Random and Rule-Only agents)

---

## 2026-02-07 — Experiment Orders 001/002 Designed and Verified

### Context

First two experiment orders created and verified against HYPOTHESIS_BACKLOG and reference design documents (S2-01, S2-02). Phase 4 pre-work verification completed.

### Experiment Orders

**DOE-001: Baseline Comparison (OFAT)**
- Tests: H-001 (Full RAG vs Random), H-002 (Full RAG vs Rule-Only)
- Design: 3 conditions, n=70/condition, 210 total episodes
- Seed formula: seed_i = 42 + i*31 (verified, n=70)
- Statistical plan: Welch's t-test, Holm-Bonferroni, Cohen's d
- Scenario: Defend the Center (3-action space)

**DOE-002: Memory x Strength Factorial (Combined Phase 0/1)**
- Tests: H-006 (Memory main effect), H-007 (Strength main effect), H-008 (Interaction)
- Design: 2^2 full factorial + 3 center points, 150 total episodes
- Seed formula: seed_i = 1337 + i*17 (verified, n=30)
- Statistical plan: 2-way ANOVA, center point curvature test, ART fallback
- Key design choice: Combined 3 hypotheses (originally separate OFAT + factorial) into single experiment, saving ~210 episodes

### Design Decision: OFAT -> Factorial Combination

H-006 and H-007 were originally planned as separate OFAT experiments (Phase 0), with H-008 as a contingent Phase 1 factorial. DOE-002 combines all three into a single 2^2 factorial with center points. Trade-offs:
- Savings: 150 episodes vs 360 if run separately (-58%)
- Gain: Interaction effects (H-008) tested at zero additional cost
- Trade-off: 2 factor levels (low/high) instead of 3 (low/mid/high) per factor
- Mitigation: Center points (at midpoint) detect curvature, triggering Phase 2 RSM if needed

### Verification Results

Phase 4 verification report: `research/PHASE4_ORDERS_12_VERIFICATION.md`
- 8 checks performed across DOE-001, DOE-002, HYPOTHESIS_BACKLOG, DOE_CATALOG
- 5 issues found and fixed (1 HIGH, 2 MEDIUM, 2 LOW)
- 3 informational items documented (no fix needed)
- All documents now consistent and cross-referenced

### Next Steps

1. Design EXPERIMENT_ORDER_003 through _005 (ablation studies: Layer Removal, Document Quality, Scoring Weights)
2. Cross-verify all 5 orders against S2-01, S2-02, and each other
3. Begin experiment execution infrastructure preparation

---

## 2026-02-07 — Experiment Orders 003/004/005 Designed

### Context

Remaining three experiment orders designed to complete the Phase 0 ablation suite and provide an evolution system test. These orders complete the Wave 1 (parallel: DOE-001, DOE-002, DOE-003) and Wave 2 (sequential: DOE-004, DOE-005) execution plan.

### Experiment Orders

**DOE-003: Decision Layer Ablation (2^3 Full Factorial)**
- Tests: H-005 (Each decision layer independently adds value)
- Design: 2^3 full factorial, 8 conditions (each layer ON/OFF), n=30/condition, 240 total episodes
- Seed formula: seed_i = 2023 + i*23 (verified, n=30)
- Statistical plan: 3-way ANOVA (L0, L1, L2), planned contrasts, Tukey HSD
- Decision Gate: If Full Stack ~ L0 Only (p > 0.10), STOP DOE-004/005

**DOE-004: Document Quality Ablation (One-Way ANOVA)**
- Tests: H-003 (Document quality affects agent performance)
- Design: 3 conditions (Full RAG, Degraded docs, Random docs), n=50/condition, 150 total episodes
- Seed formula: seed_i = 7890 + i*13 (verified, n=50)
- Statistical plan: One-way ANOVA, dose-response contrasts, Tukey HSD, manipulation check
- Contingent on: DOE-003 Decision Gate PROCEED

**DOE-005: Memory-Strength Interaction with Evolution Hook (3x2 Factorial + CPs)**
- Tests: H-008 (Memory x Strength interaction, confirmatory)
- Design: 3x2 full factorial + 3 center points, Memory=[0.3, 0.5, 0.7], Strength=[0.3, 0.7], n=30/cell, 270 total episodes
- Seed formula: seed_i = 9999 + i*19 (verified, n=30)
- Statistical plan: 2-way ANOVA with interaction, curvature test, simple effects analysis
- Evolution hook: Gen1 best performer -> Gen2 evolved genome, paired t-test validation
- Contingent on: DOE-003 Decision Gate PROCEED

### Design Decisions

1. **DOE-003 as Decision Gate**: Layer ablation is the most fundamental test. If the multi-tier architecture (L0+L1+L2) does not outperform L0 Only, ablation experiments on document quality and scoring become less meaningful. DOE-003 gates DOE-004 and DOE-005.
2. **DOE-005 confirms DOE-002**: H-008 is tested in both DOE-002 (2x2 exploratory) and DOE-005 (3x2 confirmatory). If results conflict, DOE-005 takes precedence due to larger design and finer factor resolution.
3. **Evolution hook in DOE-005**: Rather than a separate experiment, the evolution test is embedded as a second phase of DOE-005. This reuses the seed set and provides direct paired comparison.

### Episode Budget Summary

| Experiment | Episodes | Status |
|------------|----------|--------|
| DOE-001 | 210 | Ordered |
| DOE-002 | 150 | Ordered |
| DOE-003 | 240 | Ordered |
| DOE-004 | 150 | Ordered (contingent) |
| DOE-005 | 270 (+30 evolution) | Ordered (contingent) |
| **Total** | **1050** | |

### Next Steps

1. Cross-verify all 5 experiment orders for internal consistency
2. Prepare experiment execution infrastructure (DuckDB schemas, OpenSearch indices)
3. Begin Wave 1 parallel execution: DOE-001, DOE-002, DOE-003
