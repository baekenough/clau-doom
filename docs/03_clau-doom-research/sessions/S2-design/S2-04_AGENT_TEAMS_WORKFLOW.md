# S2-04: Agent Teams Workflow Design

> **Session**: S2 (Research Design Reinforcement)
> **Priority**: high
> **Dependencies**: None
> **Status**: completed

---

## Purpose

Formalize the operational workflow for using Claude Code Agent Teams across the 4 research sessions. Define session-team mappings, file ownership rules, CLAUDE.md templates for spawned agents, and fallback strategies for resilience.

---

## Session-Team-Role Mapping

### Research Process Position

```
Opus PI (Cowork)
  |
  |  EXPERIMENT_ORDER.MD
  v
Claude Code (4 Sessions in Parallel)
  +-- Session 1: Lead + Sub-agents -> Literature Collection
  +-- Session 2: Lead + Sub-agents -> Research Design Reinforcement
  +-- Session 3: Lead + Sub-agents -> Technical Verification (PoC)
  +-- Session 4: Lead + Sub-agents -> Document Integration
  |
  |  EXPERIMENT_REPORT.MD
  v
Opus PI (Cowork)
```

### Session 1: Literature Collection

| Role | Agent | Model | Responsibilities |
|------|-------|-------|------------------|
| Lead | research-literature-mgr | Opus | Quality filtering, deduplication, synthesis |
| Sub-A | literature-search-qd | Sonnet | QD algorithm papers (MAP-Elites, CMA-ME, novelty search) |
| Sub-B | literature-search-rl | Sonnet | RL-in-FPS papers (VizDoom, DeepMind FTW, OpenAI Five) |
| Sub-C | literature-search-evo | Sonnet | Neuroevolution papers (NEAT, HyperNEAT, evolutionary strategies) |

**Output**: `sessions/S1-literature/S1-*.md` (one per category)

**Coordination Pattern**:
```
Lead assigns category to each Sub
  -> Sub-A searches QD papers -> delivers S1-01_QD_ALGORITHMS.md
  -> Sub-B searches RL papers -> delivers S1-02_RL_IN_FPS.md
  -> Sub-C searches Evo papers -> delivers S1-03_NEUROEVOLUTION.md
Lead merges, deduplicates, quality-filters -> S1-00_LITERATURE_SYNTHESIS.md
```

### Session 2: Research Design Reinforcement

| Role | Agent | Model | Responsibilities |
|------|-------|-------|------------------|
| Lead | research-pi | Opus | Design consistency review, cross-reference validation |
| Sub-A | design-metrics | Sonnet | Diversity metrics design (S2-03) |
| Sub-B | design-workflow | Sonnet | Agent Teams workflow design (S2-04) |
| Sub-C | design-schema | Sonnet | DuckDB schema extensions, integration specs |

**Output**: `sessions/S2-design/S2-*.md`

**Coordination Pattern**:
```
Lead reviews existing design docs (07-EVOLUTION.md, 05-QUALITY.md)
  -> Sub-A writes S2-03 (diversity metrics)
  -> Sub-B writes S2-04 (agent teams workflow)
  -> Sub-C writes DuckDB migration scripts
Lead cross-checks consistency across all S2 outputs
```

### Session 3: Technical Verification (PoC)

| Role | Agent | Model | Responsibilities |
|------|-------|-------|------------------|
| Lead | research-doe-runner | Opus | PoC orchestration, benchmark design, integration testing |
| Sub-A | poc-rust-agent | Opus | Rust decision engine PoC (< 100ms latency) |
| Sub-B | poc-opensearch | Opus | OpenSearch kNN query PoC (embedding + retrieval) |
| Sub-C | poc-evolution | Opus | Evolution operator PoC (crossover, mutation on MD files) |

**Output**: `sessions/S3-poc/S3-*.md` + working PoC code

**Note**: S3 uses Opus for all sub-agents because code implementation and debugging quality is critical.

**Coordination Pattern**:
```
Lead defines benchmark criteria and integration test plan
  -> Sub-A implements Rust decision engine skeleton
  -> Sub-B implements OpenSearch indexing + kNN retrieval
  -> Sub-C implements MD crossover/mutation operators
Lead runs integration tests: Agent -> OpenSearch -> Decision -> DuckDB pipeline
```

### Session 4: Document Integration

| Role | Agent | Model | Responsibilities |
|------|-------|-------|------------------|
| Lead | arch-documenter | Opus | Final merge review, consistency validation |
| Sub-A | doc-design-merge | Sonnet | Merge S2 design outputs into main design docs |
| Sub-B | doc-api-spec | Sonnet | API and interface specification updates |
| Sub-C | doc-schema-merge | Sonnet | DuckDB schema documentation, migration guide |

**Output**: Updated `docs/01_clau-doom-docs/` main documents

**Coordination Pattern**:
```
Lead reviews all S1/S2/S3 outputs, creates merge plan
  -> Sub-A updates 07-EVOLUTION.md, 05-QUALITY.md with S2 designs
  -> Sub-B updates API specs with S3 PoC findings
  -> Sub-C updates schema docs with new tables from S2-03
Lead does final consistency check across all updated documents
```

---

## File Ownership Matrix

### Principle: No Concurrent Writes to Same File

One file is owned by exactly one team member at any time. Read access is always open.

### Per-Session Ownership

| File/Directory | S1 | S2 | S3 | S4 |
|----------------|----|----|----|----|
| `docs/01_clau-doom-docs/docs/*.md` | Read | Read | Read | **Write** (Sub-A, Sub-B) |
| `docs/01_clau-doom-docs/DOOM_ARENA_CLAUDE.md` | Read | Read | Read | **Write** (Lead) |
| `sessions/S1-literature/*.md` | **Write** (Subs) | Read | Read | Read |
| `sessions/S2-design/*.md` | Read | **Write** (Subs) | Read | Read |
| `sessions/S3-poc/*.md` | -- | -- | **Write** (Subs) | Read |
| `sessions/S3-poc/src/*` | -- | -- | **Write** (Subs) | Read |
| `sessions/S4-integration/*.md` | -- | -- | -- | **Write** (Lead) |
| `volumes/agents/active/DOOM_PLAYER_*.MD` | Read | Read | **Write** (Sub-C) | Read |
| `volumes/research/orders/*.md` | Read | Read | Read | Read |
| `volumes/research/reports/*.md` | Read | Read | Read | **Write** (Lead) |

### Within-Session Ownership (Sub-Agent Level)

```
Session 2 Example:

Sub-A owns: sessions/S2-design/S2-03_DIVERSITY_METRICS.md
Sub-B owns: sessions/S2-design/S2-04_AGENT_TEAMS_WORKFLOW.md
Sub-C owns: sessions/S2-design/S2-05_SCHEMA_EXTENSIONS.sql
Lead owns:  sessions/S2-design/S2-00_DESIGN_REVIEW.md

Rule: Sub-agents NEVER write to another Sub-agent's file.
      Lead can read all files but writes only to Lead-owned files.
      Lead merges by reading Sub outputs and writing to Lead files.
```

### Conflict Resolution Rules

| Scenario | Resolution |
|----------|------------|
| Two Subs need to modify same file | Lead splits file into sections, assigns one section per Sub |
| Sub discovers it needs to update another Sub's file | Sub sends message to Lead with proposed change, Lead coordinates |
| Lead and Sub both need to write to same file | Lead takes priority; Sub writes to temp file, Lead merges |
| Cross-session file conflict | Later session wins; earlier session's changes are read-only inputs |
| Merge conflict in git | Lead resolves; prefer later session's changes for evolving docs |

### MD File Locking Mechanism

Since Agent Teams uses filesystem, implement logical locking via convention:

```
Convention-based locking (no actual file locks):

1. File header comment:
   <!-- OWNER: Sub-A | SESSION: S2 | SINCE: 2024-12-15T10:00:00Z -->

2. Before writing, check header:
   - If OWNER matches current agent -> proceed
   - If OWNER is different -> send message to Lead
   - If no OWNER header -> claim by adding header

3. On task completion, remove OWNER header:
   <!-- RELEASED: Sub-A | SESSION: S2 | AT: 2024-12-15T12:00:00Z -->
```

---

## CLAUDE.md Template for Agent Teams

### Minimal Project Context (Injected at Spawn)

```markdown
# CLAUDE.md - clau-doom Agent Teams Context

## Project
LLM multi-agent evolutionary Doom player research.
Agents use RAG (OpenSearch) + Rust rule engine for real-time decisions.
No LLM calls during gameplay. LLM used only for retrospection, evolution, and analysis.

## Core Rules
- No real-time LLM calls (RAG + Rust only, < 100ms decision latency)
- Python is VizDoom glue only
- All experiments: fixed seeds, variable isolation, A/B comparison
- Statistical claims require evidence markers: [STAT:p=X.XX]
- Trust levels: HIGH (p<0.01, n>=50), MEDIUM (p<0.05, n>=30), LOW, UNTRUSTED

## Architecture
- Game: VizDoom + Xvfb + noVNC (container)
- Agent core: Rust (decision engine, scoring)
- Orchestrator: Go (lifecycle, gRPC)
- Dashboard: Next.js (WebSocket + noVNC)
- RAG: OpenSearch (kNN vector search, 768-dim Ollama embeddings)
- Knowledge: MongoDB (strategy catalog)
- Messaging: NATS (agent pub/sub)
- Local DB: DuckDB (per-agent play logs)

## Decision Hierarchy
- Level 0: MD hardcoded rules (Rust, < 1ms)
- Level 1: DuckDB local cache (SQL, < 10ms)
- Level 2: OpenSearch kNN (vector, < 100ms)
- Level 3: Claude CLI (async, seconds, offline only)

## File Paths
- Agent definitions: volumes/agents/active/DOOM_PLAYER_{SEQ}.MD
- Play logs: volumes/data/player-{SEQ}/game.duckdb
- Research docs: volumes/research/
- Strategy documents: OpenSearch index "doom_strategies"
- Session outputs: docs/03_clau-doom-research/sessions/

## DuckDB Core Schema
```sql
-- Per-episode metrics
CREATE TABLE experiments (
    experiment_id   VARCHAR,
    episode_id      INT,
    variant         VARCHAR,    -- 'control' or 'treatment'
    seed            INT,
    kill_rate       FLOAT,
    survival_time   FLOAT,
    damage_dealt    FLOAT,
    damage_taken    FLOAT,
    ammo_efficiency FLOAT,
    items_collected INT,
    rooms_visited   INT,
    total_rooms     INT
);

-- Per-encounter decisions
CREATE TABLE encounters (
    encounter_id        VARCHAR,
    episode_id          INT,
    situation_snapshot  JSON,    -- {enemies, health, ammo, room_type}
    strategy_used       VARCHAR, -- OpenSearch doc ID
    tactic              VARCHAR, -- 'attack', 'retreat', 'flank', etc.
    outcome             VARCHAR, -- 'kill', 'death', 'escape', 'damage_dealt'
    damage_dealt        FLOAT,
    damage_taken        FLOAT
);

-- Generation diversity (from S2-03 — full schema, see S2-03 for column definitions)
CREATE TABLE generation_diversity (
    generation_id       INT PRIMARY KEY,
    strategy_entropy    FLOAT,          -- H_composite (normalized, 0-1)
    behavioral_coverage FLOAT,          -- Coverage ratio (0-1)
    qd_score            FLOAT,          -- QD-Score (0 to grid_size)
    doc_pool_mpd        FLOAT,          -- Mean pairwise distance of doc embeddings
    doc_pool_ed         INT,            -- Effective dimensionality (PCA 90% variance)
    effective_mutation_rate FLOAT,       -- EMR (0-1)
    mutation_efficiency FLOAT,          -- ME (pheno/geno ratio)
    num_agents          INT,            -- Population size
    num_unique_strategies INT,          -- Distinct play_style count
    occupied_cells      INT,            -- Behavioral grid occupied cells
    total_cells         INT,            -- Behavioral grid total cells (default 100)
    cumulative_coverage FLOAT,          -- Cumulative coverage up to this generation
    measured_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Evolution Mechanism
- Parent selection: TOPSIS multi-criteria (kill_rate, survival, Cpk, innovation, efficiency)
- Crossover: Merge Strategy Profile params from top-2 parents
- Mutation: DOE-significant variables toward effect direction (exploitation 70%, exploration 30%)
- Elitism: Cpk > 1.33 and TOPSIS top -> preserved unchanged
- Quality: SPC control charts, FMEA failure modes, Cp/Cpk process capability

## Your Assignment
[SESSION-SPECIFIC CONTENT INJECTED HERE]

Session: {session_id}
Role: {lead|sub-agent-A|sub-agent-B|sub-agent-C}
Task: {specific task description}
Output file: {path to output file}
Owned files: {list of files this agent can write to}
Read-only files: {list of files for reference}

## Communication Rules
- Send findings to Lead via message
- Do NOT write to files you do not own
- If you need to modify another agent's file, message Lead
- Record intermediate results in your owned output file
- On completion, message Lead with summary
```

### Session-Specific Injection Examples

**S1 Sub-A (QD Literature)**:
```markdown
## Your Assignment
Session: S1
Role: Sub-agent-A
Task: Search and summarize Quality-Diversity algorithm papers (MAP-Elites, CMA-ME, novelty search, curiosity-driven exploration). Focus on metrics, archives, and behavior characterization methods applicable to game AI.
Output file: sessions/S1-literature/S1-01_QD_ALGORITHMS.md
Owned files: [sessions/S1-literature/S1-01_QD_ALGORITHMS.md]
Read-only files: [docs/01_clau-doom-docs/docs/07-EVOLUTION.md]
```

**S3 Sub-A (Rust PoC)**:
```markdown
## Your Assignment
Session: S3
Role: Sub-agent-A
Task: Implement Rust decision engine skeleton. Must: (1) Parse DOOM_PLAYER MD file for strategy params, (2) Query DuckDB for recent encounter history, (3) Make decision in < 100ms P99. Benchmark with 1000 simulated decisions.
Output file: sessions/S3-poc/S3-01_RUST_DECISION_ENGINE.md
Owned files: [sessions/S3-poc/S3-01_RUST_DECISION_ENGINE.md, sessions/S3-poc/src/decision_engine/]
Read-only files: [docs/01_clau-doom-docs/docs/02-ARCHITECTURE.md, volumes/agents/active/DOOM_PLAYER_001.MD]
```

---

## Agent Teams Operating Rules

### 1. Team Creation

```bash
# Environment variable (required)
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1

# Session start prompt template
"Create an agent team for {session_purpose}. Spawn {N} teammates:
- Teammate A ({model}): {role_description}. Output: {file_path}
- Teammate B ({model}): {role_description}. Output: {file_path}
- Teammate C ({model}): {role_description}. Output: {file_path}

File ownership rules:
- Each teammate writes ONLY to their assigned output file
- All other project files are read-only
- Send findings to Lead via message, not by writing to shared files

Start working immediately. Report progress via task list."
```

### 2. Task Management

```
Task list structure per session:

[Session S2 Tasks]
  Task 1: [Sub-A] Write diversity metrics design (S2-03)
    Status: in_progress
    Depends: none
    Output: sessions/S2-design/S2-03_DIVERSITY_METRICS.md

  Task 2: [Sub-B] Write agent teams workflow (S2-04)
    Status: in_progress
    Depends: none
    Output: sessions/S2-design/S2-04_AGENT_TEAMS_WORKFLOW.md

  Task 3: [Sub-C] Write DuckDB schema extensions
    Status: pending
    Depends: Task 1 (needs table definitions from S2-03)
    Output: sessions/S2-design/S2-05_SCHEMA_EXTENSIONS.sql

  Task 4: [Lead] Cross-reference review
    Status: pending
    Depends: Task 1, Task 2, Task 3
    Output: sessions/S2-design/S2-00_DESIGN_REVIEW.md
```

**Dependency Rules**:
- Tasks with `depends: none` start immediately in parallel
- Tasks with dependencies wait until all deps are `completed`
- Lead's review task always depends on all Sub tasks
- Cross-session dependencies expressed in session-level metadata

### 3. Inter-Agent Communication Protocol

| Message Type | Sender | Receiver | When |
|-------------|--------|----------|------|
| Progress update | Sub | Lead | Every major milestone (25%, 50%, 75%, done) |
| Blocking issue | Sub | Lead | Cannot proceed without resolution |
| Discovery | Sub | Lead (or specific Sub) | Found information relevant to another agent |
| File conflict | Sub | Lead | Needs to modify file owned by another agent |
| Review request | Sub | Lead | Task complete, requesting review |
| Feedback | Lead | Sub | Review comments, revision requests |
| Completion | Lead | All Subs | All tasks done, session wrapping up |

**Message Format Convention**:
```
[PROGRESS] S2-03 diversity metrics: 3/5 metrics defined (60%)
[BLOCKING] Need DuckDB schema from S2-05 for alert table design
[DISCOVERY] Found relevant QD metric in S1-01 that applies to S2-03
[CONFLICT] Need to add column to generation_diversity table (owned by Sub-A)
[REVIEW] S2-03 complete, ready for Lead review
[FEEDBACK] S2-03: Add trust-weighted variant to Doc Pool Diversity metric
[COMPLETE] All S2 tasks reviewed and approved. Session closing.
```

### 4. Session Lifecycle

```
Phase 1: Initialization (Lead)
  - Read EXPERIMENT_ORDER or session brief
  - Create task list with dependencies
  - Spawn sub-agents with CLAUDE.md context
  - Assign file ownership

Phase 2: Parallel Execution (All)
  - Sub-agents work on independent tasks
  - Communication via messages (not shared files)
  - Lead monitors progress, unblocks issues
  - Dependent tasks start as prerequisites complete

Phase 3: Integration (Lead)
  - All Sub tasks completed
  - Lead reads all outputs
  - Cross-reference validation
  - Consistency check against existing docs
  - Write session synthesis document (S*-00)

Phase 4: Cleanup (Lead)
  - Verify all output files exist and are complete
  - Remove file ownership headers
  - Create session completion summary
  - Notify PI (via EXPERIMENT_REPORT or session log)
  - Shut down sub-agents
```

---

## Fallback Strategies

### Failure Mode 1: Sub-Agent Spawn Failure

| Symptom | Cause | Response |
|---------|-------|----------|
| Agent Teams feature unavailable | Feature flag not set or API limitation | Switch to sequential single-agent execution |
| Sub-agent fails to spawn | Resource limit, API error | Lead handles that Sub's task directly |
| Partial spawn (2/3 agents) | Intermittent error | Redistribute failed agent's task to surviving agents |

**Recovery Procedure**:
```
1. Lead detects spawn failure
2. Log failure in session notes
3. Reassign task:
   Option A: Lead handles directly
   Option B: Spawn replacement agent
   Option C: Merge task with another Sub's workload
4. Update task list with reassignment
5. Continue session
```

### Failure Mode 2: Sub-Agent Produces Incorrect Output

| Symptom | Detection | Response |
|---------|-----------|----------|
| Output missing required sections | Lead review checklist | Lead sends feedback with specific requirements |
| Output contradicts existing design | Cross-reference check | Lead identifies conflicts, Sub revises |
| Output has incorrect formulas/schema | Technical review | Lead corrects inline or assigns revision task |
| Output is incomplete | Completion criteria check | Lead asks Sub to continue or finishes directly |

**Quality Gate Checklist** (Lead applies to every Sub output):
```
[ ] All required sections present per template
[ ] Mathematical formulas are well-defined and consistent
[ ] DuckDB schema types are correct (INT, FLOAT, VARCHAR, TIMESTAMP)
[ ] Cross-references to other documents are valid file paths
[ ] Alert thresholds are specified with numeric values
[ ] No contradictions with 07-EVOLUTION.md or 05-QUALITY.md
[ ] Visualization specs include chart type, axes, and data source
```

### Failure Mode 3: Session Interruption

| Symptom | Cause | Response |
|---------|-------|----------|
| Session terminated mid-task | Timeout, crash, network | Resume from last written file |
| Context window exhausted | Large outputs, long conversation | Compact and resume with focus |
| API rate limit | Too many parallel calls | Reduce sub-agent count, retry |

**Recovery Procedure**:
```
1. MD files persist on filesystem regardless of session state
2. Start new session, load CLAUDE.md context
3. Read all existing session output files
4. Identify incomplete tasks from file content
5. Resume from last checkpoint
6. DO NOT restart completed tasks
```

**Key Insight**: Because all outputs are MD files on disk, session interruption is a soft failure. No in-memory state is lost. The file system IS the checkpoint.

### Failure Mode 4: Token Budget Exceeded

| Budget Level | Strategy |
|-------------|----------|
| > 80% used | Switch Sub-agents to Haiku model for remaining work |
| > 90% used | Reduce Sub-agent count to 1, Lead delegates one task at a time |
| > 95% used | Lead completes remaining work directly (no Sub-agents) |
| Budget exhausted | Save progress, document remaining tasks for next session |

**Cost Optimization Rules**:
```
1. Use Sonnet for Sub-agents by default (except S3 PoC which needs Opus)
2. Keep CLAUDE.md template under 2000 tokens
3. Sub-agents return concise summaries, not full reasoning chains
4. Ecomode (R013) activated when 4+ agents spawn
5. Lead uses Opus for review/synthesis only, not for data gathering
```

### Failure Mode 5: Agent Teams Feature Regression

If Claude Code Agent Teams feature becomes unavailable or unstable:

**Sequential Fallback Plan**:
```
Replace parallel Agent Teams with sequential Task tool execution:

Original (Agent Teams):
  Lead + Sub-A + Sub-B + Sub-C  (parallel)

Fallback (Task tool):
  Task(research-pi) -> Sub-A's work
  Task(research-pi) -> Sub-B's work
  Task(research-pi) -> Sub-C's work
  Main conversation aggregates results

Key difference:
  - No inter-agent messaging (each Task is isolated)
  - Main conversation coordinates instead of Lead agent
  - Same file outputs, same completion criteria
  - Slightly slower (sequential) but identical results
```

**Output format is identical regardless of execution mode.** This is by design: MD file-based workflow ensures the execution mechanism (parallel Agent Teams vs sequential Task tool) does not affect deliverable format.

---

## Cross-Session Coordination

### Session Execution Order

```
Fully parallel (no cross-session dependencies):
  S1 (Literature) | S2 (Design) | S3 (PoC) | S4 waits

S4 depends on S1, S2, S3:
  S4 starts after all others complete

Timeline:
  T=0: S1, S2, S3 start in parallel
  T=X: S1, S2, S3 complete (at different times)
  T=max(S1,S2,S3): S4 starts
  T=S4_done: All sessions complete, PI review
```

### Cross-Session Data Flow

```
S1 -> S2: Literature findings inform metric design choices
S1 -> S3: Literature benchmarks inform PoC acceptance criteria
S2 -> S3: Design specs define what PoC must implement
S2 -> S4: Design docs are primary input for document updates

S1 -> S4: Literature references for document citations
S3 -> S4: PoC findings for architecture documentation
```

### Handoff Protocol

```
When Session X completes and Session Y needs its output:

1. Session X Lead writes completion summary to:
   sessions/SX-*/SX-00_COMPLETION_SUMMARY.md

2. Summary includes:
   - List of output files with one-line descriptions
   - Key findings relevant to downstream sessions
   - Open questions or caveats
   - Recommended reading order

3. Session Y Lead reads summary first, then specific files as needed
```

---

## Completion Criteria

- [x] 4-session role mapping tables with agent names, models, and responsibilities
- [x] File ownership matrix (per-session and within-session)
- [x] Conflict resolution rules and MD file locking convention
- [x] CLAUDE.md template with session-specific injection examples
- [x] Agent Teams operating rules (creation, task management, communication, lifecycle)
- [x] 5 failure modes with recovery procedures
- [x] Cross-session coordination and handoff protocol
- [x] Fallback from Agent Teams to sequential Task tool execution
