# Round 4 (Final) Trial 4: Practical Feasibility Confirmation

> **Reviewer**: claude (teammate agent)
> **Date**: 2026-02-07
> **Scope**: Template-to-experiment alignment, variable injection, SPC/FMEA readiness, episode budget, infrastructure, risk assessment
> **Round**: 4 (Final independent validation)

---

## Overall Verdict: PASS (Strong)

This research project is practically executable. The templates, experiment orders, SPC framework, FMEA registry, and episode budget are all well-structured, internally consistent, and ready for execution pending infrastructure build-out. The design reflects mature research engineering with clear separation between design, execution, and analysis phases.

---

## Category Grades

| Category | Grade | Summary |
|----------|-------|---------|
| Template-to-Experiment Alignment | **A** | All 4 templates map cleanly to their target experiments with correct variable slots |
| Variable Injection Completeness | **A** | All ${VAR} placeholders documented with valid ranges and injection examples |
| SPC Readiness | **B+** | Framework well-defined with Western Electric rules, but pre-data state is inherently empty |
| FMEA Completeness | **A-** | 5 failure modes with realistic RPNs, actionable mitigations, phased priority plan |
| Episode Budget Feasibility | **A** | 1050 total episodes across 5 DOEs, estimated 20-25 hours total runtime, practical |
| Infrastructure Readiness | **B** | Clear requirements documented, but infrastructure is not yet built |
| Risk Assessment | **B+** | Top risks identified and mitigated; some residual risk in first-run integration |

---

## 1. Template-to-Experiment Alignment: Grade A

### Coverage Analysis

| Template | Target Experiments | Conditions Covered | Alignment |
|----------|-------------------|-------------------|-----------|
| DOOM_PLAYER_BASELINE_RANDOM.md | DOE-001 Condition 1 | Random baseline (all layers OFF) | PERFECT |
| DOOM_PLAYER_BASELINE_RULEONLY.md | DOE-001 Condition 2 | Rule-only baseline (L0 only) | PERFECT |
| DOOM_PLAYER_GEN1.md | DOE-001 Cond 3, DOE-002, DOE-005 | Full RAG with ${MEMORY_WEIGHT}, ${STRENGTH_WEIGHT} | PERFECT |
| DOOM_PLAYER_DOE003.md | DOE-003 | Layer ablation with ${L0/L1/L2_ENABLED} | PERFECT |

### Observations

- **DOE-001**: 3 conditions map to 3 distinct templates (Random, Rule-Only, GEN1). Action space (3 discrete: MOVE_LEFT, MOVE_RIGHT, ATTACK) is explicitly documented in both DOE-001 order and Random baseline template.
- **DOE-002**: Uses GEN1 template with variable injection for Memory/Strength. The experiment order references `DOOM_PLAYER_DOE002.md` as agent config but the README maps GEN1 as the correct template. Minor naming inconsistency (DOE-002 order says "DOOM_PLAYER_DOE002.md" but no such template file exists). The GEN1 template covers the needed variables. **Note**: This is a documentation gap, not a functional gap -- the GEN1 template has the correct ${MEMORY_WEIGHT} and ${STRENGTH_WEIGHT} variables.
- **DOE-003**: Dedicated DOE003 template with ${L0_ENABLED}, ${L1_ENABLED}, ${L2_ENABLED} boolean injection. All 8 conditions (2^3) are explicitly enumerated in both the template and experiment order.
- **DOE-004**: Uses the GEN1 template with OpenSearch index configuration changes (Full, Degraded, Random indices). Template supports this via OpenSearch Config section.
- **DOE-005**: Uses GEN1 template with Memory/Strength injection at 3x2 factorial levels. Template variables match experiment order perfectly.

### Gap Identified

- **DOE-002 template naming**: EXPERIMENT_ORDER_002.md references `DOOM_PLAYER_DOE002.md` which does not exist as a separate template file. The README correctly maps GEN1 as the template for DOE-002. Recommend either creating a DOE002 alias template or updating the experiment order to reference GEN1 directly. **Severity**: Low (cosmetic, not functional).

---

## 2. Variable Injection Completeness: Grade A

### Variable Inventory

| Template | Variables | Types | Ranges | Injection Examples |
|----------|-----------|-------|--------|-------------------|
| GEN1 | ${MEMORY_WEIGHT} | Float | 0.0-1.0 | 0.3, 0.5, 0.7 documented |
| GEN1 | ${STRENGTH_WEIGHT} | Float | 0.0-1.0 | 0.3, 0.5, 0.7 documented |
| DOE003 | ${L0_ENABLED} | Boolean | true/false | All 8 combinations listed |
| DOE003 | ${L1_ENABLED} | Boolean | true/false | All 8 combinations listed |
| DOE003 | ${L2_ENABLED} | Boolean | true/false | All 8 combinations listed |

### Verification

- **GEN1 template**: Lines 7-8 define `${MEMORY_WEIGHT}` and `${STRENGTH_WEIGHT}`. Lines 41-52 show injection examples for DOE-002 runs. Lines 95-106 show expected metrics.
- **DOE003 template**: Lines 13-15 define `${L0_ENABLED}`, `${L1_ENABLED}`, `${L2_ENABLED}`. Lines 25-64 enumerate all 8 injection combinations.
- **Baseline templates**: No variables needed (static configurations). This is correct -- baselines should be parameter-free.

### Injection Process

The README documents the 4-step injection process:
1. Read experiment order
2. Select template + substitute variables
3. Write instantiated agent MD
4. Restart container + execute episodes

This process is clear and complete. The research-doe-runner agent has sufficient instructions to execute.

---

## 3. SPC Readiness: Grade B+

### Framework Assessment

| Component | Status | Quality |
|-----------|--------|---------|
| Kill Rate X-bar/R chart | Defined, not initialized | Good specification |
| Survival Time X-bar/R chart | Defined, not initialized | Good specification |
| Damage Dealt Cpk | Defined, one-sided | Correct for maximize-response |
| Western Electric Rules | All 8 rules listed | Comprehensive |
| Process Capability benchmarks | 4-tier scale defined | Industry standard |
| FMEA Integration | Linked (SPC signal -> FMEA update) | Well-connected |
| Update Schedule | Per-generation, per-experiment, manual | Practical |

### Strengths

- **Western Electric Rules**: All 8 standard rules documented (1-point beyond 3-sigma through 8-points beyond Zone C). This is the complete standard set.
- **Cpk Formula**: Correctly specified with both two-sided and one-sided variants. The one-sided note for Damage Dealt (no upper limit) is appropriate.
- **Rational Subgrouping**: Each generation = one subgroup with n = population size. This is correct for monitoring generational evolution.
- **Phase-Aware Control Limits**: Document specifies re-computing limits after 20+ generations and separating by experimental phase. This prevents false signals from confounding process changes with special cause variation.

### Limitations

- **Pre-Data State**: All charts show "NOT STARTED" with "TBD" for UCL/LCL. This is expected and correct -- limits cannot be established before DOE-001 data exists.
- **Subgroup Size**: Planned n=8 (agents per generation). This is adequate for X-bar/R charts but on the low side for detecting small shifts. After initial data, the team should verify whether n=8 provides sufficient sensitivity.
- **No Specification Limits for Kill Rate/Survival**: LSL/USL are "TBD". These should be set after DOE-001 baseline data is available. Recommend using the Random Agent mean as a natural LSL (anything below random is broken).

### Verdict

SPC framework is well-designed and ready to initialize once data arrives. The B+ grade reflects the inherently empty pre-data state, not a design flaw.

---

## 4. FMEA Completeness: Grade A-

### Failure Mode Assessment

| FM-ID | Failure Mode | S | O | D | RPN | Realistic? | Mitigation Actionable? |
|-------|-------------|---|---|---|-----|-----------|----------------------|
| FM-G01 | Agent dies immediately | 9 | 3 | 2 | 54 | YES | YES (parameter bounds) |
| FM-G02 | Agent stuck in corner/loop | 7 | 5 | 5 | 175 | YES | YES (entropy monitoring + unstuck logic) |
| FM-G03 | Ammo depleted early | 5 | 7 | 5 | 175 | YES | YES (ammo checkpoints) |
| FM-I01 | Container crash | 6 | 4 | 3 | 72 | YES | YES (health check + auto-restart) |
| FM-I02 | Silent data loss to DuckDB | 7 | 3 | 7 | 147 | YES | YES (post-episode validation) |

### Strengths

- **RPN Scale**: Standard S x O x D = 1000 max. Target of all active RPNs < 100 by end of Phase 0 is ambitious but reasonable.
- **Category Prefixes**: FM-G## (gameplay) and FM-I## (infrastructure) avoid numbering collisions with Round 1 FMEA. Good organizational practice.
- **Phased Mitigation Plan**: Immediate (pre-Wave 1), short-term (during Wave 1), and long-term (post-Wave 1) priorities are clearly separated.
- **SPC Integration**: Explicit link between SPC out-of-control signals and FMEA updates.
- **RPN Trend Tracking**: Table structure ready for tracking mitigation effectiveness over time.

### RPN Reasonableness

- **FM-G02 (RPN=175)**: Highest priority. O=5 (moderately frequent for conservative params) and D=5 (needs pattern analysis) are plausible. Getting stuck is a known pathology in game AI.
- **FM-G03 (RPN=175)**: Tied for highest. O=7 (common in aggressive ranges) is realistic. Aggressive agents will frequently deplete ammo.
- **FM-I02 (RPN=147)**: D=7 (difficult to detect silently) is the key driver. Silent data loss is indeed harder to detect than container crashes. Post-episode validation is the right mitigation.
- **FM-I01 (RPN=72)**: Lower priority because D=3 (automated Docker health checks detect crashes quickly). Correct assessment.
- **FM-G01 (RPN=54)**: Lowest priority because O=3 (rare extreme parameter combos) and D=2 (trivially detected). Correct risk ranking.

### Gaps

- **Missing Failure Mode**: No entry for "OpenSearch returns stale/irrelevant documents due to index corruption". This could silently degrade agent performance without obvious detection. Recommend adding FM-I03.
- **Missing Failure Mode**: No entry for "Seed integrity violation between conditions" (using wrong seeds). EXPERIMENT_ORDER_001 explicitly warns about this, but FMEA doesn't cover it. Recommend adding FM-I04.
- **Severity Calibration**: S=9 for FM-G01 (zero data utility) seems high since the episode can simply be re-run. S=7-8 might be more accurate unless the cost of re-running is substantial.

### Verdict

FMEA is comprehensive for a pre-execution registry. The 5 failure modes cover the most likely gameplay and infrastructure risks. The A- reflects the 2 missing failure modes that were identified in experiment orders but not captured in the FMEA.

---

## 5. Episode Budget Feasibility: Grade A

### Budget Breakdown

| Experiment | Conditions | Episodes/Condition | Total Episodes | Est. Runtime |
|------------|------------|-------------------|----------------|-------------|
| DOE-001 | 3 (Random, Rule-Only, Full RAG) | 70 | 210 | 2-3 hours |
| DOE-002 | 4 factorial + 3 center points | 30/10 | 150 | 2-3 hours |
| DOE-003 | 8 (2^3 ablation) | 30 | 240 | 3-4 hours |
| DOE-004 | 3 (doc quality) | 50 | 150 | 2-3 hours |
| DOE-005 | 9 factorial/CP + 2 evolution | 30 | 270 + 60 = 330 | 4-5 hours + 30min |
| **TOTAL** | | | **1080** | **~15-20 hours** |

### DOE Catalog Cross-Check

The DOE_CATALOG.md states total Phase 0/1 budget of 1050 episodes. My count from individual experiment orders yields 1080 (210 + 150 + 240 + 150 + 330). The discrepancy is 30 episodes, likely from DOE-005's evolution test episodes (60 fresh episodes for Gen1+Gen2) vs the catalog's 300 estimate. **Minor discrepancy** -- the catalog says DOE-005 = 300, but the actual experiment order specifies 270 (factorial/CP) + 60 (evolution) = 330.

**Verdict**: The 30-episode discrepancy does not affect feasibility. 1080 episodes at ~60 seconds each = ~18 hours of game time + setup/restart overhead. Total estimated wall-clock time: **20-25 hours** including analysis time. This is practical for a research project.

### Runtime Reasonableness

- Episode duration: 2100 tics = 60 seconds per episode (documented consistently across all orders)
- Container restart: 5 seconds per condition change (documented in execution instructions)
- DOE-003 has 8 container restarts (8 conditions), DOE-005 has 9+2 = 11
- Total container restarts across all experiments: ~30
- Restart overhead: ~150 seconds total (negligible)

---

## 6. Infrastructure Readiness: Grade B

### Readiness Checklist

| Component | Required | Status | Risk |
|-----------|----------|--------|------|
| VizDoom container (Xvfb + noVNC) | Required for all DOEs | NOT BUILT | High |
| Rust agent binary | Required for all DOEs | NOT BUILT | High |
| Python VizDoom binding | Required for game glue | NOT BUILT | Medium |
| DuckDB file | Required for data recording | NOT INITIALIZED | Low |
| OpenSearch container | Required for DOE-001 (Full RAG), DOE-004 | NOT RUNNING | Medium |
| MongoDB container | Required for knowledge catalog | NOT RUNNING | Low |
| NATS container | Required for agent messaging | NOT RUNNING | Low |
| Ollama container | Required for embeddings (DOE-004) | NOT RUNNING | Medium |
| Docker Compose | Required for orchestration | NOT CONFIGURED | Medium |
| DuckDB schema | Required for data recording | DESIGNED (in experiment orders) | Low |
| OpenSearch indices | Required for DOE-004 (3 indices) | NOT CREATED | Medium |
| Strategy documents | Required for Full RAG conditions | NOT POPULATED | High |
| Agent MD injection scripts | Required for research-doe-runner | NOT IMPLEMENTED | Medium |
| Degradation scripts | Required for DOE-004 | NOT IMPLEMENTED | Medium |

### Critical Path

The longest dependency chain for first execution (DOE-001) is:

```
1. Build VizDoom container (Xvfb + noVNC + Python binding)
2. Build Rust agent binary (decision engine + OpenSearch client)
3. Initialize DuckDB schema
4. Populate OpenSearch with initial strategy documents
5. Test end-to-end: agent plays one episode and records metrics
6. Execute DOE-001
```

Steps 1-4 are parallelizable. Step 5 is the integration test that validates the full stack.

### Verdict

The research design is execution-ready, but the infrastructure has not been built. The B grade reflects excellent design documentation paired with zero implementation. This is expected for a research preparation phase -- the designs are ready to guide implementation.

---

## 7. Risk Assessment: Grade B+

### Top 3 Execution Risks

#### Risk 1: Integration Failure (First End-to-End Run)

**Probability**: High (first-time integration of 6+ services)

**Impact**: Delays DOE-001 by days/weeks

**Description**: The Rust agent, Python VizDoom binding, DuckDB recording, and OpenSearch retrieval have never been integrated. First-run failures are highly likely at integration boundaries (e.g., Rust agent fails to parse VizDoom observation buffer, DuckDB schema mismatch with actual metric names, OpenSearch returns unexpected response format).

**Mitigation**:
- Build a minimal integration test: 1 agent, 1 episode, 1 seed, verify data in DuckDB
- Test each integration boundary in isolation before full stack
- Budget 1-2 weeks for integration debugging

#### Risk 2: Strategy Document Cold Start (DOE-001 Condition 3)

**Probability**: Medium

**Impact**: Full RAG agent performs at Rule-Only level, DOE-001 H-002 test becomes meaningless

**Description**: DOE-001 Condition 3 (Full RAG) requires populated OpenSearch strategy documents. If initial documents are poor quality or insufficient quantity, the Full RAG agent may not benefit from L1/L2, collapsing the expected performance gap between Conditions 2 and 3. The experiment order acknowledges this risk but the initial document population strategy is not fully specified.

**Mitigation**:
- Pre-populate OpenSearch with manually crafted strategy documents based on domain knowledge
- Run a pre-experiment calibration: 20-30 episodes to verify Full RAG utilizes L2 at >10% of decisions
- If L2 usage < 10%, investigate and fix before proceeding with DOE-001

#### Risk 3: VizDoom Episode Variability

**Probability**: Medium

**Impact**: High within-condition variance reduces statistical power, tests become underpowered

**Description**: Even with fixed seeds, VizDoom scenarios may have high intrinsic variability in kill_rate (e.g., due to enemy movement patterns, weapon pickup timing). If within-condition standard deviation is large relative to between-condition differences, the planned sample sizes (n=30-70 per condition) may be insufficient.

**Mitigation**:
- DOE-001 includes adaptive stopping rule: if d < 0.20 at interim (30 episodes), extend to n=100
- All experiments use identical seeds across conditions to reduce between-condition variance
- DOE-002 and DOE-005 include center point replicates for pure error estimation
- Post DOE-001: use observed variance to refine sample sizes for subsequent experiments

### Additional Risks (Lower Priority)

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| Container memory leak during long runs | Low-Medium | Partial data loss | FM-I01 mitigation (periodic restart every 100 episodes) |
| DuckDB concurrent write conflict | Low | Silent data loss | FM-I02 mitigation (post-episode validation) |
| Seed collision between experiments | Very Low | Minor confusion | Already analyzed in DOE-001/002 orders; accepted |
| Run-order confounding in DOE-001 | Medium | Biased results | Analyst MUST include run-order covariate analysis (documented in DOE-001) |

---

## Execution Readiness Checklist

### Phase 0: Infrastructure Build (Before Any Experiment)

- [ ] VizDoom container built and tested (Xvfb + noVNC + Python binding)
- [ ] Rust agent binary compiled with OpenSearch client + DuckDB writer
- [ ] Docker Compose configuration for full stack (VizDoom, OpenSearch, MongoDB, NATS, Ollama, DuckDB)
- [ ] DuckDB schema initialized (experiments table + encounters table)
- [ ] OpenSearch index created and populated with initial strategy documents
- [ ] Agent MD injection script implemented (template + variable substitution + container restart)
- [ ] End-to-end integration test: 1 agent, 1 episode, 1 seed, metrics recorded in DuckDB
- [ ] Seed set verification tool: confirm seed uniqueness and formula correctness

### Phase 1: DOE-001 Execution

- [ ] 3 agent MD templates deployed (Random, Rule-Only, GEN1)
- [ ] VizDoom "Defend the Center" scenario loaded and verified
- [ ] DuckDB experiment_id = 'DOE-001' initialized
- [ ] Execute 210 episodes (3 conditions x 70 episodes)
- [ ] Post-execution validation: 210 rows, no missing data, seed integrity
- [ ] Handoff to research-analyst for Welch's t-tests

### Phase 2: DOE-002 through DOE-005 (Sequential with Decision Gates)

- [ ] DOE-002: 150 episodes (4 factorial + 3 center point runs)
- [ ] DOE-003: 240 episodes (8 conditions, 2^3 factorial) -- GATES DOE-004/005
- [ ] DOE-004: 150 episodes (3 document quality conditions) -- Requires degradation/random scripts
- [ ] DOE-005: 330 episodes (9 factorial/CP runs + 2 evolution runs)

---

## Final Recommendation

**PROCEED with infrastructure implementation.**

The research design is comprehensive, internally consistent, and practically executable. The 5 experiment orders provide clear, detailed instructions for the research-doe-runner agent. The SPC framework is ready to initialize. The FMEA covers the primary risk scenarios.

The primary bottleneck is infrastructure build-out (VizDoom container, Rust agent, Docker Compose stack). Once the stack is operational and passes an end-to-end integration test, DOE-001 can begin immediately.

**Key Action Items Before Execution**:
1. Build Docker Compose stack with all required services
2. Implement Rust agent decision engine with L0/L1/L2 cascade
3. Populate OpenSearch with initial strategy documents (cold-start mitigation)
4. Implement agent MD injection script (template substitution + container restart)
5. Run end-to-end integration test (1 episode, verify DuckDB recording)
6. Fix DOE-002 template naming inconsistency (DOOM_PLAYER_DOE002.md reference)
7. Add 2 missing FMEA entries (OpenSearch index corruption, seed integrity violation)

**Estimated Time to First Experiment**: 2-4 weeks of engineering effort for infrastructure build-out.

---

## Document Metadata

| Property | Value |
|----------|-------|
| Review Type | Practical Feasibility |
| Round | 4 (Final) |
| Trial | 4 |
| Materials Reviewed | 11 documents (SPC, FMEA, 4 templates, README, 4 experiment orders, DOE catalog) |
| Total Pages Reviewed | ~1200 lines across all documents |
| Reviewer Independence | Fresh evaluation, no prior round context |
