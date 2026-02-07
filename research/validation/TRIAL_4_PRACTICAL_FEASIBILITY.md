# Trial 4: Practical Feasibility Validation Report

> **Date**: 2026-02-07
> **Author**: research-pi (PI)
> **Scope**: All 5 experiments (DOE-001 through DOE-005), infrastructure, resources, schedule
> **Verdict**: ADEQUATE WITH CONDITIONS

---

## Executive Summary

This report validates the practical feasibility of executing the clau-doom research experiment portfolio: 5 experiments totaling 1050 episodes across the full technology stack. The assessment covers technical dependency readiness, episode budget analysis, resource requirements, FMEA risk assessment, known issue resolution, schedule feasibility, and data pipeline analysis.

**Key Findings**:

1. **Technical Stack**: All 7 major components required (VizDoom, Rust agent, OpenSearch, DuckDB, Docker Compose, Go orchestrator, Python glue). None are production-ready yet -- this is the most significant feasibility risk. The entire codebase is in design phase with no runnable infrastructure.
2. **Episode Budget**: 1050 total episodes is modest and computationally feasible once infrastructure exists. Estimated wall-clock time: 17-26 hours of pure episode execution.
3. **Resource Requirements**: A single developer workstation with 32GB RAM, 8+ CPU cores, and 50GB free disk is sufficient. No GPU required for agent decision-making (all CPU-bound Rust decisions).
4. **Risk**: The highest-RPN risks are infrastructure immaturity (no working containers yet) and VizDoom API instability. These are mitigated by the phased execution plan.
5. **Schedule**: The 4-session execution plan from EXECUTION_PLAN.md describes the research *design* phase (already complete), not experiment execution. Experiment execution requires a separate infrastructure build phase before any episodes can run.

**Overall Verdict**: ADEQUATE -- the experimental design is sound and the episode budget is feasible, but execution is contingent on infrastructure implementation. The design-to-execution gap is the primary practical constraint.

---

## 1. Technical Dependency Readiness Assessment

### 1.1 Component Inventory

| # | Component | Role | Status | Readiness |
|---|-----------|------|--------|-----------|
| 1 | VizDoom + Xvfb + noVNC | Game environment + screen streaming | NOT BUILT | Container Dockerfile not yet created |
| 2 | Rust Agent Core | Decision engine (< 100ms P99) | NOT BUILT | Architecture designed, no code |
| 3 | Python Glue | VizDoom API binding | NOT BUILT | API binding pattern defined |
| 4 | Go Orchestrator | Agent lifecycle, generation mgmt | NOT BUILT | Architecture designed |
| 5 | OpenSearch | RAG vector kNN search (< 100ms P99) | NOT DEPLOYED | Container config specified |
| 6 | DuckDB | Per-agent play logs, experiment data | NOT DEPLOYED | Schema designed (S2-02) |
| 7 | Docker Compose | Full orchestration | NOT BUILT | Service architecture designed |
| 8 | MongoDB | Knowledge catalog | NOT DEPLOYED | Specified in tech stack |
| 9 | NATS | Agent messaging pub/sub | NOT DEPLOYED | Specified in tech stack |
| 10 | Ollama | Embeddings (768-dim) | NOT DEPLOYED | Model selection TBD |

### 1.2 Readiness Assessment by Component

#### VizDoom + Xvfb + noVNC Container

- **Severity**: CRITICAL
- **Current State**: Design phase only. Dockerfile not created. EXECUTION_PLAN.md Session 3 (S3-01) planned Dockerfile creation and noVNC testing but has not been executed.
- **Dependencies**: VizDoom 1.2.x, Python 3.11+, Xvfb for headless rendering, noVNC for streaming
- **Key Risk**: VizDoom compilation on specific OS/architecture can fail. Xvfb configuration is non-trivial.
- **Feasibility**: HIGH -- VizDoom has mature Docker examples in the community. The `defend_the_center.cfg` scenario is one of the simplest and most stable.
- **Estimated Build Time**: 1-2 days for initial container, 1 day for noVNC integration

#### Rust Agent Core

- **Severity**: CRITICAL
- **Current State**: Architecture fully designed (4-level decision hierarchy, MD-based rules). No Rust code exists.
- **Performance Requirement**: < 100ms P99 decision latency per tick
- **Dependencies**: Rust stable toolchain, OpenSearch client crate, DuckDB Rust bindings
- **Key Risk**: The hierarchical decision cascade (L0 -> L1 -> L2 -> fallback) is architecturally sound but untested. OpenSearch kNN query latency is the bottleneck.
- **Feasibility**: HIGH -- The decision logic is straightforward pattern matching and scoring. 100ms P99 is achievable for Rust with well-configured OpenSearch.
- **Estimated Build Time**: 3-5 days for core decision engine, 2-3 days for OpenSearch/DuckDB integration

#### Python VizDoom Glue

- **Severity**: MAJOR
- **Current State**: Pattern defined (thin wrapper over VizDoom Python API)
- **Dependencies**: vizdoom Python package, gRPC or FFI bridge to Rust agent
- **Key Risk**: The Python-to-Rust bridge method (FFI, gRPC, or shared memory) has not been decided. EXECUTION_PLAN.md Session 3 (S3-02) planned PoC for all three.
- **Feasibility**: HIGH -- Python VizDoom API is well-documented. gRPC is the safest bridge option.
- **Estimated Build Time**: 2-3 days including bridge implementation

#### Go Orchestrator

- **Severity**: MAJOR
- **Current State**: Role defined (agent lifecycle, generation management, CLI, gRPC)
- **Dependencies**: Go 1.21+, gRPC for agent communication
- **Key Risk**: Not strictly required for Phase 0 experiments -- a simpler Python or shell script orchestrator could substitute.
- **Feasibility**: HIGH -- The orchestrator for Phase 0 is relatively simple (start/stop containers, inject parameters, collect data).
- **Estimated Build Time**: 3-5 days for full Go orchestrator, OR 1-2 days for a simplified Python/shell substitute

#### OpenSearch

- **Severity**: MAJOR
- **Current State**: Container architecture specified. Index schema partially designed (S2-02 specifies document structure). DOE-004 requires 3 separate indices (strategies, degraded, random).
- **Performance Requirement**: kNN query < 100ms P99
- **Dependencies**: opensearchproject/opensearch:2.x Docker image, 768-dim embedding index
- **Key Risk**: kNN performance depends on index size and embedding dimensionality. For Phase 0 with small document corpus (< 1000 docs), 100ms is easily achievable.
- **Feasibility**: HIGH for Phase 0 document counts.
- **Estimated Build Time**: 1 day for container + basic index, 1 day for document population scripts

#### DuckDB

- **Severity**: MINOR (low risk)
- **Current State**: Schema designed in S2-02 (experiments table, encounters table, metrics views). DuckDB issues from Phase 2 S2 verification all fixed.
- **Dependencies**: DuckDB library (embedded, no server needed)
- **Key Risk**: Minimal -- DuckDB is an embedded database requiring no infrastructure.
- **Feasibility**: VERY HIGH -- DuckDB is a single-file database. Schema creation is trivial.
- **Estimated Build Time**: 0.5 days

#### Docker Compose

- **Severity**: MAJOR
- **Current State**: Service architecture designed but docker-compose.yml not created.
- **Services Required**: vizdoom, opensearch, mongodb, nats, ollama (5 containers minimum for full stack)
- **Key Risk**: Resource contention when running all containers simultaneously.
- **Feasibility**: HIGH -- Standard Docker Compose orchestration.
- **Estimated Build Time**: 1-2 days

### 1.3 Technical Readiness Summary

| Rating | Description | Components |
|--------|-------------|------------|
| NOT STARTED | No code/config exists | VizDoom container, Rust agent, Python glue, Go orchestrator |
| DESIGNED | Architecture specified | OpenSearch schema, DuckDB schema, Docker Compose services |
| READY | Can deploy immediately | DuckDB (embedded, schema-only) |

**Overall Technical Readiness**: NOT READY FOR EXECUTION. Estimated 2-4 weeks of infrastructure implementation required before first experiment episode can run.

---

## 2. Episode Budget Analysis

### 2.1 Per-Experiment Breakdown

| Experiment | DOE Type | Conditions | Eps/Condition | Total Episodes | Seeds | Unique Seeds |
|------------|----------|------------|---------------|----------------|-------|-------------|
| DOE-001 | OFAT (3 conditions) | 3 (Random, Rule-Only, Full RAG) | 70 | 210 | 70 | 70 |
| DOE-002 | 2^2 Factorial + CP | 4 factorial + 3 center | 30 (factorial), 10 (CP) | 150 | 30 | 30 |
| DOE-003 | 2^3 Factorial | 8 (layer ON/OFF combos) | 30 | 240 | 30 | 30 |
| DOE-004 | One-Way ANOVA | 3 (Full, Degraded, Random docs) | 50 | 150 | 50 | 50 |
| DOE-005 | 3x2 Factorial + CP + Evol | 6 factorial + 3 CP + 1 evol | 30 | 300 | 30 | 30 |
| **TOTAL** | | | | **1050** | | **210 unique** |

### 2.2 Wall-Clock Time Estimation

**Per-Episode Timing** (based on VizDoom Defend the Center scenario):

| Component | Duration | Notes |
|-----------|----------|-------|
| Episode game time | 10-60s | Timeout at 2100 tics (60s), early death possible |
| Agent decision overhead | < 100ms/tick | ~35 ticks/sec, < 3.5s overhead per 60s episode |
| DuckDB write | < 10ms | Single row INSERT per episode |
| Inter-episode gap | 2-5s | Container state reset, seed injection |
| **Average per episode** | **15-70s** | Varies by agent survival time |
| **Conservative estimate** | **60s** | Assume most episodes run near timeout |

**Per-Experiment Timing**:

| Experiment | Episodes | Container Reconfigs | Episode Time (min) | Reconfig Time (min) | Total (hours) |
|------------|----------|--------------------|--------------------|---------------------|---------------|
| DOE-001 | 210 | 3 | 210 | 1.5 | 3.5 |
| DOE-002 | 150 | 7 | 150 | 3.5 | 2.6 |
| DOE-003 | 240 | 8 | 240 | 4.0 | 4.1 |
| DOE-004 | 150 | 3 | 150 | 1.5 | 2.5 |
| DOE-005 | 300 | 10 | 300 | 5.0 | 5.1 |
| **TOTAL** | **1050** | **31** | **1050 min** | **15.5 min** | **17.8 hours** |

**Notes**:
- Container reconfiguration includes: modify agent MD file, restart container, wait 5s for initialization.
- Add 20-30% overhead for monitoring, error recovery, and inter-run validation.
- **Realistic total**: 22-26 hours of execution time (not including analysis).

### 2.3 Parallel Execution Potential

**Wave 1** (can run simultaneously if hardware permits):

| Experiment | Episodes | Parallelizable? |
|------------|----------|----------------|
| DOE-001 | 210 | YES -- independent VizDoom instance |
| DOE-002 | 150 | YES -- independent VizDoom instance |
| DOE-003 | 240 | YES -- independent VizDoom instance |

Running 3 VizDoom instances in parallel requires ~3x resources but reduces Wave 1 from ~10 hours to ~4 hours (limited by DOE-003, the longest).

**Wave 2** (sequential after DOE-003 decision gate):

| Experiment | Episodes | Parallelizable? |
|------------|----------|----------------|
| DOE-004 | 150 | Requires DOE-003 gate pass |
| DOE-005 | 300 | Requires DOE-003 gate pass + DOE-002 results |

DOE-004 and DOE-005 could potentially run in parallel if the decision gate passes, reducing Wave 2 from ~7.5 hours to ~5 hours.

**Best Case Total**: ~9-12 hours (with parallel execution).
**Worst Case Total**: ~22-26 hours (fully sequential).

---

## 3. Resource Requirements

### 3.1 Compute Requirements

| Resource | Minimum | Recommended | Notes |
|----------|---------|-------------|-------|
| CPU Cores | 4 | 8+ | VizDoom (1-2 cores), Rust agent (1 core), OpenSearch (2 cores), other services |
| RAM | 16 GB | 32 GB | OpenSearch JVM heap (4-8 GB), VizDoom (1-2 GB), MongoDB (1-2 GB), Rust agent (< 256 MB) |
| GPU | Not required | Not required | All agent decisions are CPU-bound (Rust). No neural network inference during gameplay. |
| Disk (SSD) | 20 GB | 50 GB | Docker images (~10 GB), OpenSearch indices (~2-5 GB), DuckDB (~100 MB for 1050 episodes), VizDoom WAD files (~50 MB) |

### 3.2 Memory Breakdown (Single Experiment)

| Container | RAM Usage | Notes |
|-----------|-----------|-------|
| VizDoom + Xvfb | 1-2 GB | Game engine + headless X server |
| doom-agent-A (Rust) | 100-256 MB | Decision engine + local state |
| OpenSearch | 4-8 GB | JVM heap for kNN search |
| MongoDB | 512 MB - 1 GB | Knowledge catalog |
| NATS | 64-128 MB | Lightweight message broker |
| Ollama | 2-4 GB | Embedding model (only for async refinement, not during gameplay) |
| DuckDB | 50-100 MB | Embedded, in-process |
| **Total (single)** | **8-16 GB** | |

### 3.3 Memory Breakdown (Parallel Wave 1 -- 3 experiments)

| Scenario | Additional Resources | Total RAM |
|----------|---------------------|-----------|
| Shared infrastructure | 3 VizDoom + 3 agents, shared OpenSearch/MongoDB/NATS | +3-6 GB over single |
| Full isolation | 3 complete stacks | 3x single = 24-48 GB |
| **Recommended** | Shared infra + 3 game instances | 12-22 GB |

### 3.4 Disk Space Breakdown

| Component | Size | Notes |
|-----------|------|-------|
| Docker images (pulled) | ~8 GB | OpenSearch, MongoDB, NATS, Ollama, VizDoom base |
| Custom VizDoom image | ~2 GB | Built from Dockerfile with game files |
| OpenSearch indices | 1-5 GB | Depends on document count and embedding dim (768) |
| DuckDB files | < 100 MB | 1050 episodes x ~50 columns = modest |
| VizDoom WAD files | < 100 MB | defend_the_center.wad and dependencies |
| Agent logs | < 500 MB | Per-encounter decision logs |
| Ollama models | 2-4 GB | Embedding model weights |
| **Total** | **15-20 GB** | Well within 50 GB recommendation |

### 3.5 Network Requirements

| Traffic | Volume | Notes |
|---------|--------|-------|
| NATS pub/sub | Negligible | Intra-host localhost traffic |
| OpenSearch queries | ~35 queries/sec during gameplay | kNN search, all localhost |
| gRPC (Python <-> Rust) | ~35 calls/sec | Decision requests, all localhost |
| External network | None during gameplay | No real-time LLM calls |
| noVNC streaming | Optional | Only for human spectation |

All experiment traffic is localhost-only. No external network dependencies during episode execution.

---

## 4. FMEA Risk Matrix

### 4.1 Risk Assessment Table

| # | Failure Mode | Severity (S) | Occurrence (O) | Detection (D) | RPN | Category |
|---|-------------|:---:|:---:|:---:|:---:|----------|
| FM-01 | Infrastructure not built in time | 9 | 8 | 2 | 144 | CRITICAL |
| FM-02 | VizDoom container crash during episode | 7 | 5 | 3 | 105 | MAJOR |
| FM-03 | OpenSearch kNN latency > 100ms P99 | 6 | 4 | 4 | 96 | MAJOR |
| FM-04 | Agent decision latency > 100ms P99 | 7 | 3 | 3 | 63 | MAJOR |
| FM-05 | DuckDB data loss (file corruption) | 9 | 2 | 5 | 90 | MAJOR |
| FM-06 | Seed set corruption (wrong seeds used) | 9 | 2 | 3 | 54 | MAJOR |
| FM-07 | Python-Rust bridge instability | 6 | 4 | 4 | 96 | MAJOR |
| FM-08 | Container resource exhaustion (OOM) | 7 | 3 | 4 | 84 | MAJOR |
| FM-09 | VizDoom API instability (version mismatch) | 6 | 3 | 5 | 90 | MAJOR |
| FM-10 | OpenSearch index corruption | 8 | 2 | 4 | 64 | MAJOR |
| FM-11 | Parameter injection failure (wrong config) | 8 | 3 | 2 | 48 | MINOR |
| FM-12 | Docker Compose service dependency failure | 5 | 3 | 3 | 45 | MINOR |
| FM-13 | Ollama embedding quality insufficient | 5 | 3 | 6 | 90 | MAJOR |
| FM-14 | Decision gate data insufficient for conclusion | 6 | 3 | 5 | 90 | MAJOR |

**Scale**: S, O, D each 1-10 (10 = worst). RPN = S x O x D (max 1000).

### 4.2 Top 5 Risks by RPN

| Rank | Failure Mode | RPN | Mitigation Strategy |
|------|-------------|:---:|---------------------|
| 1 | **FM-01**: Infrastructure not built | 144 | Prioritize minimal viable stack: VizDoom + DuckDB + simple Python agent first. Defer OpenSearch/Go orchestrator for later experiments. |
| 2 | **FM-02**: VizDoom container crash | 105 | Implement episode-level checkpointing. Use `docker restart` with 5s wait. Mark crashed episodes for re-run with same seed. Limit to 3 retries per episode. |
| 3 | **FM-03**: OpenSearch latency | 96 | Start with small index (< 500 docs). Use HNSW algorithm with appropriate m/ef parameters. Profile query latency before experiments. |
| 4 | **FM-07**: Python-Rust bridge | 96 | Select gRPC (most robust option) over FFI or shared memory. Run bridge stress test before experiments. |
| 5 | **FM-09**: VizDoom API instability | 90 | Pin VizDoom version in Dockerfile. Test defend_the_center scenario independently. Use VizDoom's built-in recording for debugging. |

### 4.3 Risk Mitigation Summary

**Pre-Experiment Mitigations** (before any episode runs):

1. Build and test VizDoom container independently (FM-01, FM-02, FM-09)
2. Run OpenSearch latency benchmark with target document count (FM-03)
3. Implement and stress-test Python-Rust bridge (FM-07)
4. Validate DuckDB schema with synthetic data (FM-05)
5. Implement seed set validation script (FM-06)
6. Run full-stack integration test with 10 episodes before committing to 1050 (FM-01)

**During-Experiment Mitigations**:

1. Checkpoint DuckDB after each condition (FM-05)
2. Validate seed consumption matches expected after each run (FM-06)
3. Monitor container resource usage (FM-08)
4. Log decision latency P99 per condition (FM-04)
5. Verify parameter injection by reading back agent config (FM-11)

---

## 5. Known Issues Resolution Plan

### 5.1 Issue Assessment

| Issue | Severity | Current Status | Resolution | Effort | Blocking? |
|-------|----------|---------------|------------|--------|-----------|
| I-001 | MEDIUM | DOE_CATALOG mapping table outdated for H-006/H-007 | Update mapping table to reflect DOE-002 consolidation | 10 min | No |
| I-002 | LOW | Seed 1592 collision between DOE-001 and DOE-002 | Already documented in both orders. No formula change needed. | 0 min | No |
| I-003 | LOW | Date typos in DOE-003/004/005 headers (2025 -> 2026) | **Already fixed** -- all orders show 2026-02-07 | 0 min | No |
| I-004 | LOW | H-008 priority table inconsistency | **Already fixed** -- HYPOTHESIS_BACKLOG.md now shows correct Medium priority with 0 Low | 0 min | No |
| I-005 | LOW | DOE-001 seed rationale not documented vs S2-01 master set | **Already documented** -- DOE-001 includes rationale section | 0 min | No |

### 5.2 Resolution Status

**Already Resolved** (3 of 5):
- I-003: Date typos fixed in current documents (verified: all show 2026-02-07)
- I-004: Priority Queue Summary already updated (verified: H-008 under Medium, Low shows 0)
- I-005: Seed rationale already documented in DOE-001 (verified: paragraph explains formula choice)

**Pending Resolution** (1 of 5):
- I-001: DOE_CATALOG hypothesis-to-design mapping table needs update for H-006/H-007/H-008. Currently partially correct (shows DOE-002 for H-006/H-007/H-008 but still references OFAT in some fields). The mapping table on lines 345-354 of DOE_CATALOG.md is actually already partially updated but retains old episode count references in the Episode Budget Summary section.

**Accepted As-Is** (1 of 5):
- I-002: Seed collision documented and impact assessed as negligible.

### 5.3 Pre-Execution Fix Priority

| Priority | Action | Effort |
|----------|--------|--------|
| P1 | Update DOE_CATALOG Episode Budget Summary to match actual experiment totals | 15 min |
| P2 | Add cross-reference note from DOE_CATALOG to DOE-002 for H-006/H-007/H-008 | 5 min |
| **Total** | | **20 min** |

---

## 6. Schedule Feasibility Analysis

### 6.1 EXECUTION_PLAN.md Assessment

The EXECUTION_PLAN.md describes a **research design preparation** workflow (literature review, design documents, tech verification, documentation), NOT an experiment execution schedule. The 4 sessions described are:

| Session | Content | Status |
|---------|---------|--------|
| S1: Literature Collection | 6 literature search sub-agents | COMPLETE |
| S2: Research Design | 8 design sub-agents | COMPLETE |
| S3: Technical Verification | 7 PoC sub-agents | NOT EXECUTED |
| S4: Document Integration | 4 integration sub-agents | COMPLETE |

**Key Observation**: Session 3 (Technical Verification) has NOT been executed. This is the session that would validate the infrastructure stack (Dockerfile, noVNC, FFI PoC, gRPC PoC, OpenSearch config, embedding benchmark). Without S3, the infrastructure is designed but untested.

### 6.2 Proposed Experiment Execution Schedule

A realistic execution schedule must account for the infrastructure build phase:

| Phase | Duration | Activities |
|-------|----------|------------|
| **Phase A: Infrastructure Build** | 2-3 weeks | Build VizDoom container, Rust agent core, Python-Rust bridge, Docker Compose, OpenSearch setup, DuckDB schema |
| **Phase B: Integration Test** | 3-5 days | Full-stack integration test (10 episodes), latency benchmarks, seed validation |
| **Phase C: Wave 1 Execution** | 1-2 days | DOE-001 (210 eps), DOE-002 (150 eps), DOE-003 (240 eps) -- potentially parallel |
| **Phase D: Wave 1 Analysis** | 1-2 days | Statistical analysis of DOE-001, DOE-002, DOE-003. Apply DOE-003 decision gate. |
| **Phase E: Wave 2 Execution** | 1-2 days | DOE-004 (150 eps) + DOE-005 (300 eps) -- contingent on gate pass |
| **Phase F: Wave 2 Analysis** | 1-2 days | Statistical analysis, evolution test, findings adoption |
| **TOTAL** | **4-6 weeks** | From start to final findings |

### 6.3 Decision Gate Timing

The DOE-003 decision gate is the critical scheduling constraint:

```
DOE-003 MUST complete and be analyzed BEFORE DOE-004 and DOE-005 can begin.

Gate Criteria:
  - Full Stack vs L0 Only: p < 0.10 AND Cohen's d > 0.3
  - IF FAIL: STOP DOE-004/005, investigate architecture
  - IF PASS: Proceed to Wave 2

Timing Impact:
  - DOE-003 execution: ~4 hours
  - DOE-003 analysis: ~2 hours
  - Gate decision: ~1 hour
  - Total gate delay: ~7 hours between Wave 1 completion and Wave 2 start
```

### 6.4 Parallel vs Sequential Trade-offs

| Strategy | Total Time | Resource Cost | Risk |
|----------|-----------|---------------|------|
| Fully Sequential | 22-26 hours | 1x baseline | Lowest risk, but slow |
| Wave 1 Parallel (3x) | 14-18 hours | 1.5-2x RAM | Moderate risk (resource contention) |
| Full Parallel (5x) | N/A | N/A | NOT POSSIBLE (Wave 2 depends on gate) |

**Recommendation**: Run Wave 1 with 2-3 parallel VizDoom instances (DOE-001 + DOE-002 parallel, DOE-003 sequential or parallel depending on resources). Run Wave 2 sequentially.

---

## 7. Data Pipeline Feasibility

### 7.1 Pipeline Architecture

```
VizDoom (Python API)
    |
    | Game state per tick (actions, observations, rewards)
    v
Python Glue Layer
    |
    | gRPC / FFI call per tick
    v
Rust Agent Core
    |
    +---> Level 0: MD Rules (< 1ms)
    |         |
    |         v (if miss)
    +---> Level 1: DuckDB Cache (< 10ms)
    |         |
    |         v (if miss)
    +---> Level 2: OpenSearch kNN (< 100ms)
    |
    | Decision (action to take)
    v
Python Glue Layer
    |
    | Apply action to VizDoom
    v
VizDoom (executes action)
    |
    | Episode-level metrics
    v
DuckDB (experiments table)
    |
    | Per-encounter metrics
    v
DuckDB (encounters table)
```

### 7.2 Per-Tick Data Flow

| Step | Latency Budget | Data Size | Notes |
|------|---------------|-----------|-------|
| VizDoom -> Python | < 1ms | Game state (~1KB) | In-process Python API |
| Python -> Rust (gRPC) | < 5ms | Serialized state (~2KB) | localhost gRPC |
| Rust L0 decision | < 1ms | MD rule match | Pattern matching |
| Rust L1 DuckDB query | < 10ms | SQL query result | Embedded DB |
| Rust L2 OpenSearch kNN | < 100ms | Top-K vectors (~5KB) | HTTP REST API |
| Rust -> Python (gRPC) | < 5ms | Action + metadata (~500B) | localhost gRPC |
| Python -> VizDoom | < 1ms | Action command | In-process API |
| **Total per tick** | **< 120ms** | **~10KB** | Within 100ms P99 budget (L2 is rare) |

### 7.3 Per-Episode Data Recording

| Table | Columns | Rows per Episode | Write Latency |
|-------|---------|-----------------|---------------|
| experiments | ~20 (seed, kills, survival_time, etc.) | 1 | < 5ms |
| encounters | ~10 (decision_level, latency, similarity) | 50-200 | < 50ms (batch) |

**Total data per experiment**:
- DOE-001 (210 episodes): ~210 rows in experiments, ~21,000-42,000 rows in encounters
- DOE-003 (240 episodes): ~240 rows, ~24,000-48,000 rows
- All experiments: ~1,050 rows in experiments, ~105,000-210,000 rows in encounters

DuckDB can handle this volume trivially (designed for millions of rows).

### 7.4 Cross-Experiment Data Aggregation

All experiments share the same DuckDB schema, differentiated by `experiment_id`:

```sql
-- Cross-experiment comparison (e.g., DOE-001 Full RAG vs DOE-003 Full Stack)
SELECT
    experiment_id,
    condition,
    AVG(kill_rate) as mean_kill_rate,
    STDDEV(kill_rate) as sd_kill_rate,
    COUNT(*) as n
FROM experiments
WHERE experiment_id IN ('DOE-001', 'DOE-003')
  AND condition IN ('full_agent', 'layer_full')
GROUP BY experiment_id, condition;
```

**Feasibility**: Straightforward SQL aggregation. No pipeline complexity issues.

### 7.5 DOE-004 Special Requirements

DOE-004 (Document Quality Ablation) has unique pipeline requirements:

1. **Pre-execution**: Must create 2 additional OpenSearch indices (`opensearch_degraded`, `opensearch_random`)
2. **Degradation script**: Python script to shuffle tags and add noise to embeddings
3. **Random generation script**: Python script to create structurally valid but random documents
4. **Index switching**: Agent must be reconfigured to query different indices per condition

**Feasibility**: Moderate complexity. Requires custom Python scripts that do not yet exist. The degradation procedure is well-specified in DOE-004, so implementation is straightforward.

**Estimated Additional Build Time**: 1-2 days for DOE-004-specific scripts and index management.

### 7.6 DOE-005 Evolution Hook

DOE-005 has a two-phase execution:
1. **Phase 1**: Standard factorial (270 episodes) -- standard pipeline
2. **Phase 2**: Evolution test (30 episodes) -- requires analyzing Phase 1 results before executing Phase 2

**Pipeline Impact**: The evolution hook requires an intermediate analysis step between Phase 1 and Phase 2. The research-analyst must complete ANOVA and identify the best performer before research-doe-runner can configure Generation 2.

**Feasibility**: Straightforward but sequential. Cannot be fully automated without the analysis step.

---

## 8. Experiment-Specific Feasibility Notes

### 8.1 DOE-001: Baseline Comparison

- **Feasibility**: HIGH
- **Special Requirements**: Three different agent configurations (Random, Rule-Only, Full RAG). Each needs a separate agent MD file.
- **Risk**: Random agent implementation is trivial. Rule-Only requires L0 rules to exist. Full RAG requires all infrastructure.
- **Note**: Could partially execute (Random vs Rule-Only) with minimal infrastructure, deferring Full RAG condition.

### 8.2 DOE-002: Memory x Strength Factorial

- **Feasibility**: HIGH
- **Special Requirements**: Parameter injection (memory_weight, strength_weight) into agent MD file. Container restart between runs.
- **Risk**: Parameter injection is a simple file edit + restart. 7 run reconfigurations needed.
- **Note**: Randomized run order specified. Must follow exact order for validity.

### 8.3 DOE-003: Decision Layer Ablation (DECISION GATE)

- **Feasibility**: HIGH but CRITICAL path
- **Special Requirements**: 8 different layer ON/OFF configurations. Some configurations (e.g., "No Layers") may produce zero kills (expected).
- **Risk**: The "No Layers" condition (Run 8) always uses MOVE_FORWARD -- agent will die quickly. This is by design (controlled floor).
- **Gate Risk**: If Full Stack is not significantly better than L0 Only, DOE-004 and DOE-005 are cancelled. This is a scientific risk, not a technical one.

### 8.4 DOE-004: Document Quality Ablation

- **Feasibility**: MODERATE
- **Special Requirements**: Requires 3 OpenSearch indices with different document quality levels. Degradation and random generation scripts must be built.
- **Risk**: The manipulation check (verifying cosine similarity differs across conditions) is essential. If degradation does not actually change retrieval behavior, the experiment is invalid.
- **Dependency**: DOE-003 gate must pass first.

### 8.5 DOE-005: Memory-Strength Interaction + Evolution

- **Feasibility**: MODERATE
- **Special Requirements**: Two-phase execution (factorial + evolution). Evolution hook requires intermediate analysis. 9 run configurations in Phase 1.
- **Risk**: The evolution test (Gen2 vs Gen1) is a paired comparison with n=30. If the effect is small (d < 0.3), it may not reach significance. This is a statistical power risk, not a technical one.
- **Dependency**: DOE-003 gate must pass. DOE-002 results inform interpretation.

---

## 9. Recommendations

### 9.1 CRITICAL -- Before Any Execution

| # | Recommendation | Priority | Effort |
|---|---------------|----------|--------|
| R-01 | Complete Session 3 (Technical Verification) from EXECUTION_PLAN.md -- build and test VizDoom container, bridge PoC, OpenSearch setup | CRITICAL | 2-3 weeks |
| R-02 | Implement minimal viable stack: VizDoom + DuckDB + Python agent (no Rust initially) | CRITICAL | 1-2 weeks |
| R-03 | Run 10-episode integration test before committing to 1050-episode campaign | CRITICAL | 1 day |

### 9.2 MAJOR -- Before Wave 1

| # | Recommendation | Priority | Effort |
|---|---------------|----------|--------|
| R-04 | Implement seed validation script (verify correct seeds used per condition) | MAJOR | 0.5 days |
| R-05 | Implement DuckDB checkpointing (backup after each condition/run) | MAJOR | 0.5 days |
| R-06 | Profile OpenSearch kNN latency with target document count | MAJOR | 0.5 days |
| R-07 | Create parameter injection automation (agent MD file templating) | MAJOR | 1 day |

### 9.3 MINOR -- Before Wave 2

| # | Recommendation | Priority | Effort |
|---|---------------|----------|--------|
| R-08 | Build DOE-004 degradation and random document generation scripts | MINOR | 1-2 days |
| R-09 | Build DOE-005 evolution hook (Gen1 -> Gen2 genome mutation) | MINOR | 0.5 days |
| R-10 | Resolve remaining I-001 (DOE_CATALOG update) | MINOR | 20 min |

### 9.4 Phased Approach Recommendation

Given the infrastructure gap, recommend a phased approach:

**Immediate (Phase A)**: Build minimal stack and run DOE-001 (Random vs Rule-Only only -- 2 of 3 conditions, 140 episodes). This validates the execution pipeline with minimal infrastructure.

**Short-term (Phase B)**: Add OpenSearch + Full RAG capability. Complete DOE-001 (third condition, 70 episodes). Begin DOE-002 and DOE-003.

**Medium-term (Phase C)**: Complete Wave 1, apply decision gate, execute Wave 2.

---

## 10. Overall Verdict

### ADEQUATE WITH CONDITIONS

The experiment portfolio is scientifically sound, the episode budget is computationally feasible, and the statistical designs are appropriate. The research preparation quality is high.

**Conditions for execution**:

1. **Infrastructure implementation must precede experiment execution** (2-4 weeks). No experiments can run until the VizDoom container, agent core, and data pipeline are built and tested.
2. **Session 3 (Technical Verification) should be completed** to reduce implementation risk for the Python-Rust bridge, OpenSearch configuration, and embedding benchmarks.
3. **Integration test (10 episodes minimum)** must pass before committing to the full 1050-episode campaign.
4. **DuckDB checkpointing and seed validation** must be implemented to prevent data loss and ensure reproducibility.

**What is ready**:
- Experimental designs (all 5 DOEs fully specified)
- Seed sets (verified, collision-free within experiments)
- Statistical analysis plans (ANOVA, diagnostics, effect sizes)
- Decision gate logic (DOE-003 controls DOE-004/005)
- Audit trail framework (R102 compliant)
- Episode budget (1050 episodes, 17-26 hours execution)

**What is NOT ready**:
- VizDoom container
- Rust agent core
- Python-Rust bridge
- Go orchestrator
- OpenSearch deployment
- Docker Compose configuration
- DOE-004 document manipulation scripts
- DOE-005 evolution hook implementation

**Bottom Line**: The research design is excellent. The execution gap is infrastructure, not methodology. Once infrastructure is built and validated, experiment execution is straightforward.

---

*Report generated by research-pi. Validated against CLAUDE.md tech stack, EXECUTION_PLAN.md, and all 5 EXPERIMENT_ORDER documents.*
