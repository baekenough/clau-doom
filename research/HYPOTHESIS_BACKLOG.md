# clau-doom Hypothesis Backlog

> **Project**: clau-doom — LLM Multi-Agent DOOM Research
> **Maintained by**: research-pi (PI)
> **Last Updated**: 2026-02-07
> **Total Hypotheses**: 8 (0 adopted, 0 rejected, 1 queued, 7 ordered)

---

## Active Hypotheses

### H-001: RAG Agent Outperforms Random Baseline [HIGH PRIORITY]

**Statement**: The full clau-doom agent (all decision levels active) significantly outperforms the Random Agent baseline on kill_rate, survival_time, and ammo_efficiency.

**Formal**: Let mu_FULL and mu_RAND denote mean kill_rate for Full Agent and Random Agent respectively. H0: mu_FULL = mu_RAND. H1: mu_FULL > mu_RAND.

**Rationale**: This is the most fundamental validation. If a RAG-based agent cannot beat random action selection, the entire architecture is flawed. Expected to be a large effect (Cohen's d > 1.0) based on the structured decision hierarchy vs. uniform random.

**Priority**: High
**Status**: Experiment ordered (DOE-001)
**Phase**: 0 (Baseline)
**Linked Experiment**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Source**: S2-01_EVAL_BASELINES.md, Baseline 1
**Date Added**: 2026-02-07

---

### H-002: RAG Agent Outperforms Rule-Only Baseline [HIGH PRIORITY]

**Statement**: The full clau-doom agent (L0+L1+L2) significantly outperforms the Rule-Only agent (L0 only) on kill_rate. The performance delta quantifies the value added by RAG experience accumulation (OpenSearch + DuckDB).

**Formal**: Let mu_FULL and mu_RULE denote mean kill_rate for Full Agent and Rule-Only Agent respectively. H0: mu_FULL = mu_RULE. H1: mu_FULL != mu_RULE (two-sided).

**Rationale**: This is the primary comparison for the paper's core claim. The delta (Full - Rule-Only) = the contribution of Levels 1 and 2 (DuckDB cache + OpenSearch kNN). If this delta is not significant, the RAG pipeline does not add value over static rules, and the research direction must be reconsidered. Target effect: medium (Cohen's d >= 0.50).

**Priority**: High
**Status**: Experiment ordered (DOE-001)
**Phase**: 0 (Baseline)
**Linked Experiment**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Source**: S2-01_EVAL_BASELINES.md, Baseline 2
**Sample Size**: n = 70 per group (power = 0.80 for d = 0.50)
**Date Added**: 2026-02-07

---

### H-003: Document Quality Significantly Affects Agent Performance [HIGH PRIORITY]

**Statement**: Strategy document quality has a monotonically positive effect on agent kill_rate. Specifically: Full RAG (high-quality docs) > Degraded docs > Random docs.

**Formal**: Let mu_H, mu_D, mu_R denote mean kill_rate under High Quality, Degraded, and Random document conditions. H0: mu_H = mu_D = mu_R. H1: At least one pair differs.

**Rationale**: Tests the "Document Quality" factor of the core formula (Agent Skill = Document Quality x Scoring Accuracy). If document quality does not matter, the OpenSearch pipeline may not be retrieving situation-appropriate documents, or the Rust scoring may be compensating. This ablation isolates the semantic retrieval accuracy contribution.

**Priority**: High
**Status**: Experiment ordered (DOE-004)
**Phase**: 0 (Ablation)
**Linked Experiment**: DOE-004 (EXPERIMENT_ORDER_004.md)
**Source**: S2-02_CORE_ASSUMPTION_ABLATION.md, Ablation 1 (H-ABL-01)
**Sample Size**: n = 50 per group, 3 groups = 150 episodes total
**Statistical Test**: One-way ANOVA, post-hoc Tukey HSD
**Date Added**: 2026-02-07

---

### H-004: Scoring Weights Significantly Affect Agent Performance [MEDIUM PRIORITY]

**Statement**: The Rust scoring weight combination (similarity 0.4, confidence 0.4, recency 0.2) produces better kill_rate than any single-factor scoring or random selection from kNN results.

**Formal**: Let mu_OPT, mu_SIM, mu_CONF, mu_RAND denote mean kill_rate under Optimized, Similarity-only, Confidence-only, and Random scoring. H0: mu_OPT = mu_SIM = mu_CONF = mu_RAND. H1: At least one pair differs.

**Rationale**: Tests the "Scoring Accuracy" factor of the core formula. If scoring weights do not matter, all documents in the Top-K may be equivalently useful (homogeneous pool), or kNN pre-filtering already does most of the work. This would simplify the architecture. The extended 8-condition experiment enables response surface modeling over the weight simplex.

**Priority**: Medium
**Status**: Queued
**Phase**: 0 (Ablation)
**Linked Experiment**: To be assigned (Ablation 2 — S2-02)
**Source**: S2-02_CORE_ASSUMPTION_ABLATION.md, Ablation 2 (H-ABL-02)
**Sample Size**: Primary: n = 40 per group, 4 groups = 160 episodes. Extended: n = 30 per condition, 8 conditions = 240 episodes.
**Statistical Test**: One-way ANOVA (primary), multiple regression on weight space (extended)
**Date Added**: 2026-02-07

---

### H-005: Each Decision Layer Independently Adds Measurable Value [HIGH PRIORITY]

**Statement**: Each decision layer (Level 0: MD rules, Level 1: DuckDB cache, Level 2: OpenSearch kNN) independently contributes measurable performance improvement. The full stack (L0+L1+L2) outperforms any proper subset.

**Formal**: Let mu_FULL, mu_L01, mu_L0, mu_L2 denote mean kill_rate under Full Stack, L0+L1, L0-only, and L2-only conditions. H0: No differences among conditions. H1: At least one pair differs.

**Rationale**: Tests the architectural foundation. The 2^3 factorial extension (8 conditions: each level ON/OFF) enables estimation of all main effects AND interaction effects (L0xL1, L0xL2, L1xL2, L0xL1xL2). This is the most fundamental ablation — run FIRST per S2-02 execution order. If Full Stack is not better than L0 Only, Ablations 1 and 2 are less meaningful.

**Priority**: High
**Status**: Experiment ordered (DOE-003)
**Phase**: 0 (Ablation)
**Linked Experiment**: DOE-003 (EXPERIMENT_ORDER_003.md)
**Source**: S2-02_CORE_ASSUMPTION_ABLATION.md, Ablation 3 (H-ABL-03)
**Sample Size**: Primary: n = 40 per condition, 4 conditions = 160 episodes. Full 2^3: n = 30 per cell, 8 cells = 240 episodes.
**Statistical Test**: One-way ANOVA (4 conditions), 2^3 factorial ANOVA (8 conditions)
**Decision Gate**: If Full Stack ~ L0 Only (p > 0.10), STOP and investigate before proceeding to H-003 and H-004.
**Design Note**: Formal statement describes 4 key conditions; DOE-003 implements full 2^3 factorial (8 conditions) to enable estimation of all main effects AND interaction effects (L0xL1, L0xL2, L1xL2, L0xL1xL2).
**Date Added**: 2026-02-07

---

### H-006: Memory Parameter Affects Kill Efficiency [MEDIUM PRIORITY]

**Statement**: The agent memory parameter (controlling DuckDB cache utilization and experience recall depth) has a significant main effect on kill_rate. Higher memory values lead to higher kill efficiency.

**Formal**: Let mu_LOW and mu_HIGH denote mean kill_rate at memory levels 0.3 and 0.7 respectively. H0: mu_LOW = mu_HIGH. H1: mu_LOW != mu_HIGH.

**Rationale**: Memory is a primary Strategy Profile parameter governing how much the agent relies on past experience. Originally planned as OFAT, but combined with H-007 and H-008 into a single 2^2 factorial design (DOE-002) for efficiency. The factorial approach tests main effects AND interaction simultaneously, saving ~30 episodes vs separate OFAT experiments.

**Priority**: Medium
**Status**: Experiment ordered (DOE-002)
**Phase**: 0/1 (Combined factorial — tests Phase 0 main effects and Phase 1 interaction in one design)
**Linked Experiment**: DOE-002 (EXPERIMENT_ORDER_002.md)
**Source**: CLAUDE.md core design (agent parameters), 04-DOE.md Phase 0/1
**Sample Size**: n = 30 per cell, 4 cells = 120 factorial episodes + 30 center points = 150 total (power ~ 0.85 for f = 0.25)
**Statistical Test**: 2-way ANOVA (factorial), Memory main effect F-test
**Level Change Note**: Levels changed from original (0.5, 0.7, 0.9) to (0.3, 0.7) with center at 0.5. Wider range (0.4 span vs 0.4 span) centered lower to better explore the practical operating range. Center points at 0.5 test for curvature.
**Date Added**: 2026-02-07

---

### H-007: Strength Parameter Affects Kill Efficiency [MEDIUM PRIORITY]

**Statement**: The agent strength parameter (controlling aggression and attack commitment) has a significant main effect on kill_rate per episode. Higher strength leads to higher kill efficiency (but potentially lower survival).

**Formal**: Let mu_LOW and mu_HIGH denote mean kill_rate at strength levels 0.3 and 0.7 respectively. H0: mu_LOW = mu_HIGH. H1: mu_LOW != mu_HIGH.

**Rationale**: Strength is a primary Strategy Profile parameter governing combat aggressiveness. Combined with H-006 and H-008 into DOE-002 factorial design for efficiency. The factorial approach tests main effects AND interaction simultaneously.

**Priority**: Medium
**Status**: Experiment ordered (DOE-002)
**Phase**: 0/1 (Combined factorial — tests Phase 0 main effects and Phase 1 interaction in one design)
**Linked Experiment**: DOE-002 (EXPERIMENT_ORDER_002.md)
**Source**: CLAUDE.md core design (agent parameters), 04-DOE.md Phase 0/1
**Sample Size**: n = 30 per cell, 4 cells = 120 factorial episodes + 30 center points = 150 total
**Statistical Test**: 2-way ANOVA (factorial), Strength main effect F-test. Primary response: kill_rate (aligned with DOE-002). Secondary: damage_dealt, survival_time.
**Date Added**: 2026-02-07

---

### H-008: Memory and Strength Interact [LOW PRIORITY → MEDIUM]

**Statement**: Memory and strength interact to affect kill_rate. The effect of memory on kill efficiency depends on the strength level, and vice versa.

**Formal**: In a 2-factor ANOVA with memory and strength as factors, the interaction term (Memory x Strength) is significant. H0: No interaction. H1: Interaction exists.

**Rationale**: Originally planned as a separate Phase 1 experiment contingent on H-006 and H-007 results. However, combining all three hypotheses into a single 2^2 factorial design (DOE-002) tests interaction at no additional cost — the same 120 factorial episodes that test main effects also test interaction. This is the key efficiency advantage of factorial over OFAT.

**Priority**: Medium (elevated from Low because DOE-002 tests it at zero additional cost)
**Status**: Experiment ordered (DOE-002, exploratory)
**Phase**: 0/1 (Combined factorial)
**Linked Experiment**: DOE-002 (EXPERIMENT_ORDER_002.md)
**Source**: 04-DOE.md Phase 1, CLAUDE.md DOE Phase Progression
**Sample Size**: n = 30 per cell, 2x2 = 4 cells = 120 factorial episodes (shared with H-006 and H-007)
**Statistical Test**: Two-way ANOVA (factorial), interaction F-test (AxB term)
**Note**: If interaction is significant, this directly triggers Phase 2 RSM transition.
**Dual Testing Precedence**: H-008 is tested in two experiments:
- DOE-002 = exploratory screening for interaction (2x2 factorial, 2 levels per factor)
- DOE-005 = confirmatory test with finer resolution (3x2 factorial, 3 Memory levels)
- If results conflict: **DOE-005 takes precedence** (larger design, more factor levels, higher resolution)
**Date Added**: 2026-02-07

---

## Completed Hypotheses

(None yet.)

---

## Rejected Hypotheses

(None yet.)

---

## Priority Queue Summary

| Priority | Count | Hypotheses |
|----------|-------|------------|
| High | 4 | H-001, H-002, H-003, H-005 |
| Medium | 4 | H-004, H-006, H-007, H-008 |
| Low | 0 | — |

## Execution Order (Recommended)

```
Phase 0 — Baseline + Ablation Foundation:
  1. H-005 (Layer Removal) — FIRST: most fundamental architectural validation
  2. H-001 + H-002 (Baseline comparisons via DOE-001) — can run in parallel with H-005
  3. H-003 (Document Quality) — only if H-005 confirms L2 adds value
  4. H-004 (Scoring Weights) — only if H-003 confirms docs matter

Phase 0/1 — Combined Factorial (can run in parallel with ablations):
  5. H-006 + H-007 + H-008 (Memory x Strength via DOE-002) — single 2^2 factorial
     tests all three hypotheses simultaneously. Main effects (H-006, H-007) and
     interaction (H-008) from one experiment. Center points test for curvature.

Phase 2 — RSM (contingent on DOE-002 results):
  6. If DOE-002 shows significant factors + curvature → CCD around optimal region
```

**Design Choice Note**: H-006 and H-007 were originally planned as separate OFAT experiments (Phase 0), and H-008 as a contingent Phase 1 factorial. DOE-002 combines all three into a single 2^2 factorial with center points. This saves ~30 episodes (150 vs 90+90+180=360 if run separately) while providing strictly more information (interaction effects + curvature test). The trade-off is that factor levels are reduced from 3 (OFAT) to 2 (factorial) per factor, compensated by center points for curvature detection.

## Phase Transition Criteria

```
Phase 0 -> Phase 1:
  Trigger: ALL of the following:
    (a) Baseline validated: H-001/H-002 confirm Full Agent outperforms baselines (via DOE-001)
    (b) Architecture validated: H-005 confirms Full Stack outperforms L0 Only (via DOE-003)
    (c) At least 2 agent parameters show significant main effects: H-006/H-007 (via DOE-002)

Phase 1 -> Phase 2:
  Trigger: Significant interaction effects confirmed in factorial design
  Evidence: H-008 adopted, interaction plot shows non-parallel lines

Phase 2 -> Phase 3:
  Trigger: Optimal region identified via RSM, need robustness validation
  Evidence: Stationary point found in CCD, confirmation runs needed
```
