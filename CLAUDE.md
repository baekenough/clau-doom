# clau-doom

LLM multi-agent DOOM research: RAG experience accumulation + DOE/quality engineering optimization + generational evolution.

## Core Values

0. **Agent Teams First** - All multi-agent research work uses Agent Teams actively. Simple Task spawns only for truly isolated single tasks.

1. **Scientific Rigor** - All optimization through DOE, ANOVA, and statistical evidence. No ad-hoc tuning.
2. **Delegated Execution** - All work delegated to specialized sub-agents via Task tool. Orchestrator coordinates only.
3. **Transparent by Default** - Agent identification, tool calls, routing decisions visible. Intent detection shows confidence.
4. **Quality Gate** - mgr-sauron verification mandatory before push. No shortcuts.
5. **Orchestrated, Not Hierarchical** - Main conversation is sole orchestrator. Sub-agents work independently, no spawning sub-sub-agents.
6. **Experiment Integrity** - Fixed seeds, statistical evidence markers, trust scores. Results must be reproducible.

---
## ⚠️ STOP AND READ BEFORE EVERY RESPONSE ⚠️

```
╔══════════════════════════════════════════════════════════════════╗
║  MANDATORY CHECK BEFORE RESPONDING:                               ║
║                                                                   ║
║  1. Does my response start with agent identification?             ║
║     ┌─ Agent: {name} ({type})                                    ║
║     └─ Task: {description}                                       ║
║                                                                   ║
║  2. Do my tool calls include identification?                     ║
║     [agent-name] → Tool: {tool}                                  ║
║     [agent-name] → Target: {path}                                ║
║                                                                   ║
║  If NO to either → FIX IMMEDIATELY before continuing             ║
╚══════════════════════════════════════════════════════════════════╝
```

---

## CRITICAL: Scope of Rules

> **These rules apply ALWAYS, regardless of context:**

| Context | Rules Apply? |
|---------|-------------|
| Working on clau-doom project | **YES** |
| Working on external projects | **YES** |
| After context compaction | **YES** |
| Simple questions | **YES** |
| Research analysis | **YES** |
| ANY situation | **YES** |

```
The working directory may be clau-doom, but you might be
editing files in other projects. RULES STILL APPLY.

연구 프로젝트 작업 중이라도 이 지침은 반드시 준수해야 합니다.
```

---

## CRITICAL: Session Continuity

> **These rules apply at ALL times, including after context compaction.**

```
When a session continues after "compact conversation":
1. RE-READ this CLAUDE.md IMMEDIATELY
2. ALL enforcement rules remain ACTIVE
3. Previous context summary does NOT override these rules
4. First response MUST include agent identification

Context compaction = rules still apply
New session = rules still apply
Summary provided = rules still apply
External project = rules still apply

NO EXCEPTIONS. NO EXCUSES.
```

---

## CRITICAL: Enforcement Rules

> **These rules are NON-NEGOTIABLE. Violation = immediate correction required.**

### 1. Agent Identification (ENFORCED)
```
EVERY response MUST start with:

┌─ Agent: {agent-name} ({agent-type})
├─ Skill: {skill-name} (if applicable)
└─ Task: {brief-task-description}

NO EXCEPTIONS. Even for simple questions.
```

### 2. Tool Usage Identification (ENFORCED)
```
EVERY tool call MUST be prefixed with:

[agent-name] → Tool: <tool-name>
[agent-name] → Target: <file/path/url>

Example:
[lang-rust-expert] → Tool: Read
[lang-rust-expert] → Target: src/agent/mod.rs
```

### 3. Parallel Execution (ENFORCED for 2+ independent tasks)
```
When 2 or more tasks are INDEPENDENT:
→ MUST spawn parallel agent instances (max 4)
→ MUST NOT process sequentially

Detection: If tasks don't share state or have dependencies → PARALLEL

Example - WRONG:
  Task 1 → complete → Task 2 → complete → Task 3

Example - CORRECT:
  ┌── Task 1 (instance #1)
  ├── Task 2 (instance #2)
  └── Task 3 (instance #3)
  All complete in parallel
```

### 4. Orchestrator Coordination (ENFORCED for multi-agent tasks)
```
When task requires multiple agents:
→ Main conversation (orchestrator) MUST coordinate
→ Main conversation assigns tasks to appropriate agents
→ Main conversation aggregates results

Flow:
  User → Main conversation → [agent-1, agent-2, agent-3] → Main conversation → User
```

---

## Global Rules (MUST comply)

> See `.claude/rules/`

### MUST (Never violate)
| ID | Rule | Description |
|----|------|-------------|
| R000-0 | [Agent Teams](/.claude/rules/MUST-agent-teams.md) | **PRINCIPLE ZERO** - Active Agent Teams usage for all multi-agent tasks |
| R000 | [Language Policy](/.claude/rules/MUST-language-policy.md) | Korean I/O, English files, delegation model |
| R001 | [Safety Rules](/.claude/rules/MUST-safety.md) | Prohibited actions, required checks |
| R002 | [Permission Rules](/.claude/rules/MUST-permissions.md) | Tool tiers, file access scope |
| R006 | [Agent Design](/.claude/rules/MUST-agent-design.md) | Agent structure, separation of concerns |
| R007 | [Agent Identification](/.claude/rules/MUST-agent-identification.md) | **ENFORCED** - Display agent/skill in ALL responses |
| R008 | [Tool Identification](/.claude/rules/MUST-tool-identification.md) | **ENFORCED** - Display agent when using ANY tool |
| R009 | [Parallel Execution](/.claude/rules/MUST-parallel-execution.md) | **ENFORCED** - Parallel execution, large task decomposition |
| R010 | [Orchestrator Coordination](/.claude/rules/MUST-orchestrator-coordination.md) | **ENFORCED** - Orchestrator coordination, session continuity, direct action prohibition |
| R015 | [Intent Transparency](/.claude/rules/MUST-intent-transparency.md) | **ENFORCED** - Transparent agent routing |
| R016 | [Continuous Improvement](/.claude/rules/MUST-continuous-improvement.md) | **ENFORCED** - Update rules when violations are pointed out |
| R017 | [Sync Verification](/.claude/rules/MUST-sync-verification.md) | **ENFORCED** - Verify sync before committing structural changes |
| R100 | [Experiment Integrity](/.claude/rules/MUST-experiment-integrity.md) | **ENFORCED** - Seed fixation, statistical evidence, trust scores |
| R101 | [PI Boundary](/.claude/rules/MUST-pi-boundary.md) | **ENFORCED** - PI outputs EXPERIMENT_ORDER only, no direct execution |
| R102 | [Research Audit Trail](/.claude/rules/MUST-research-audit-trail.md) | **ENFORCED** - hypothesis→order→report→findings chain |

### SHOULD (Strongly recommended)
| ID | Rule | Description |
|----|------|-------------|
| R003 | [Interaction Rules](/.claude/rules/SHOULD-interaction.md) | Response principles, status format |
| R004 | [Error Handling](/.claude/rules/SHOULD-error-handling.md) | Error levels, recovery strategy |
| R011 | [Memory Integration](/.claude/rules/SHOULD-memory-integration.md) | Session persistence |
| R012 | [HUD Statusline](/.claude/rules/SHOULD-hud-statusline.md) | Real-time status display (experiment/generation) |
| R013 | [Ecomode](/.claude/rules/SHOULD-ecomode.md) | Token efficiency for batch ops |

---

## Commands

### Slash Commands (from Skills)

| Command | Description |
|---------|-------------|
| `/create-agent` | Create a new agent |
| `/sauron-watch` | Full R017 verification |
| `/memory-save` | Save session context |
| `/memory-recall` | Search and recall memories |
| `/lists` | Show all available commands |
| `/status` | Show system status |
| `/help` | Show help information |

---

## Project Structure

```
clau-doom/
├── CLAUDE.md                    # Entry point (this file)
├── .claude/
│   ├── agents/                  # Subagent definitions (18 files)
│   ├── skills/                  # Skills (32 directories)
│   ├── rules/                   # Global rules (R000-R102)
│   ├── hooks/                   # Hook scripts (HUD)
│   └── contexts/                # Context files (ecomode)
├── guides/                      # Reference docs (18 topics)
│   ├── rust/
│   ├── golang/
│   ├── python/
│   ├── typescript/
│   ├── doe/
│   ├── quality-engineering/
│   ├── anova/
│   ├── vizdoom/
│   ├── docker/
│   ├── opensearch/
│   ├── mongodb/
│   ├── nats/
│   ├── grpc/
│   ├── duckdb/
│   ├── testing/
│   ├── observability/
│   ├── deployment/
│   └── security/
└── docs/                        # Research documentation (existing)
    ├── 01_clau-doom-docs/
    ├── 02_literature/
    └── 03_clau-doom-research/
```

---

## Orchestration

Orchestration is handled by routing skills in the main conversation:
- **research-lead-routing**: Routes experiment lifecycle (PI→runner→analyst→evolution→paper)
- **dev-lead-routing**: Routes development tasks to language/framework experts
- **secretary-routing**: Routes agent management tasks

The main conversation acts as the sole orchestrator. Subagents cannot spawn other subagents.

---

## Agents Summary

| Type | Count | Agents |
|------|-------|--------|
| Research | 6 | research-pi, research-analyst, research-doe-runner, research-rag-curator, research-evolution-mgr, research-paper-writer |
| SW Engineer/Language | 4 | lang-rust-expert, lang-golang-expert, lang-python-expert, lang-typescript-expert |
| SW Engineer/Infra | 2 | infra-docker-expert, infra-grpc-expert |
| SW Architect | 1 | arch-documenter |
| Manager | 3 | mgr-gitnerd, mgr-sauron, mgr-creator |
| System | 2 | sys-memory-keeper, sys-research-log |
| **Total** | **18** | |

---

## Tech Stack

| Layer | Tech | Role |
|-------|------|------|
| Game Environment | VizDoom + Xvfb + noVNC | Doom engine + screen streaming |
| Agent Core | Rust | Decision engine, RAG client, scoring (< 100ms) |
| Game Glue | Python | VizDoom API binding only |
| Orchestrator | Go | Agent lifecycle, generation mgmt, CLI, gRPC |
| Dashboard | Next.js + WebSocket + noVNC | Real-time spectation, research visualization |
| AI Reasoning (Research) | Claude Code CLI (host) | Episode retrospection, evolution, experiment analysis |
| RAG Search | OpenSearch (container) | Strategy document kNN vector search |
| Knowledge Store | MongoDB (container) | Know-how/strategy catalog |
| Messaging | NATS (container) | Agent pub/sub broadcast |
| Local DB | DuckDB (file) | Per-agent play logs |
| Infra | Docker Compose | Full orchestration |

---

## Decision Hierarchy

```
Level 0: MD hardcoded rules (Rust, < 1ms)
  - Basic reflexes, emergency responses
  - Hardcoded in agent binary

Level 1: DuckDB local cache (SQL, < 10ms)
  - Per-agent play history
  - Frequently accessed patterns

Level 2: OpenSearch kNN (vector search, < 100ms)
  - Strategy document retrieval
  - Cross-agent know-how search

Level 3: Claude Code CLI (async, seconds)
  - Episode retrospection
  - Generation evolution
  - DOE experiment design
```

**No real-time LLM calls during gameplay.**

---

## Agent Skill Formula

```
Agent Skill = OpenSearch Document Quality × Rust Scoring Accuracy
```

Improvement vectors:
1. **Document Quality**: Refinement via Ollama (embedding quality + relevance)
2. **Scoring Accuracy**: DOE optimization of Rust decision weights

---

## Experiment Lifecycle

```
Hypothesis → DOE Design → Parallel Execution → Measurement → ANOVA → Knowledge
    ↑                                                                    │
    └── SPC anomaly / FMEA priority / Meta-analysis ←──────────────────┘
```

### Phases

| Phase | Agent | Output |
|-------|-------|--------|
| Hypothesis | research-pi | EXPERIMENT_ORDER.yaml |
| DOE Design | research-pi | Factor levels, design matrix |
| Execution | research-doe-runner | Run_ID → measurements |
| Analysis | research-analyst | p-values, significant factors |
| Knowledge | research-rag-curator | Strategy documents → OpenSearch |
| Evolution | research-evolution-mgr | Generation N → N+1 |
| Publication | research-paper-writer | NeurIPS/ICML paper sections |

---

## DOE Phase Progression

| Phase | Design | Use When | Example |
|-------|--------|----------|---------|
| 0 | OFAT (One Factor At a Time) | Initial exploration, few factors | Test aggression 0.1→0.9 alone |
| 1 | Factorial / Fractional | Multiple factors, interaction effects | 2^4 design: aggression × health_threshold × weapon_pref × retreat_dist |
| 2 | RSM-CCD (Response Surface) | Fine-tuning after significant factors found | Central Composite Design around optimal region |
| 3 | Split-Plot / Sequential | Complex constraints, adaptive | Whole-plot: map type, sub-plot: agent params |

### Phase Transition Criteria

```
Phase 0 → 1: Identified > 3 interesting factors
Phase 1 → 2: Found significant main effects + interactions
Phase 2 → 3: Near-optimal region, need fine control
Phase 3 → Meta: Multiple experiments, need cross-study synthesis
```

---

## Quality Engineering Integration

### SPC (Statistical Process Control)
```yaml
purpose: Detect anomalies in agent performance across generations
metrics:
  - kill_rate control chart (X-bar, R)
  - survival_time control chart
  - damage_dealt Cpk (process capability)
trigger: Out-of-control signal → investigate + FMEA
```

### FMEA (Failure Mode and Effects Analysis)
```yaml
purpose: Prioritize experiment focus areas
inputs:
  - Severity: Impact on final score
  - Occurrence: Frequency of failure mode
  - Detection: How easily detected
output: RPN (Risk Priority Number) → experiment queue
```

### TOPSIS (Multi-Criteria Decision Making)
```yaml
purpose: Select best generation when trade-offs exist
criteria:
  - kill_rate (maximize)
  - survival_time (maximize)
  - ammo_efficiency (maximize)
  - damage_taken (minimize)
weights: Learned from meta-analysis
```

---

## Research Workflow

### Typical Session Flow

```
1. User: "새로운 실험을 시작하자. 에이전트의 공격성과 후퇴 거리를 최적화하고 싶어."

2. Main conversation → Task(research-pi)
   PI: Hypothesis + EXPERIMENT_ORDER.yaml

3. Main conversation → Task(research-doe-runner)
   Runner: Execute 16 runs (2^2 factorial design)

4. Main conversation → Task(research-analyst)
   Analyst: ANOVA → p-values, significant factors

5. Main conversation → Task(research-rag-curator)
   Curator: Generate strategy docs → OpenSearch

6. Main conversation → Task(research-evolution-mgr)
   Evolution: Generation N → N+1 genome

7. Main conversation aggregates → reports to user
```

---

## Quick Reference

```bash
# Show all commands
/lists

# Agent management
/create-agent my-agent
/sauron-watch

# Memory management
/memory-save
/memory-recall DOE factorial design

# Context management
/compact focus on {topic}
/compact focus on experiment 42 ANOVA results
```

---

## Memory Scopes

### Current Agent Memory Map

| Scope | Count | Agents |
|-------|-------|--------|
| `project` | 16 | research-*, lang-*, infra-grpc-expert, arch-documenter, mgr-gitnerd, mgr-sauron, mgr-creator, sys-memory-keeper |
| `user` | 1 | infra-docker-expert |
| `local` | 1 | sys-research-log |

### Scope Definitions

| Scope | Location | Use Case | Git Tracked |
|-------|----------|----------|-------------|
| `user` | `~/.claude/agent-memory/<name>/` | Cross-project learnings | No |
| `project` | `.claude/agent-memory/<name>/` | Project-specific patterns | Yes |
| `local` | `.claude/agent-memory-local/<name>/` | Local-only knowledge | No |

---

## Compact Instructions

When compacting this conversation, preserve:
- Current experiment phase and DOE status
- Agent routing decisions made in this session
- All file paths referenced in current task
- Error patterns and resolutions
- Statistical findings and p-values from current experiments
- Generation evolution history (N → N+1 transitions)
- ANOVA tables and significant factor lists
- SPC out-of-control signals
- FMEA RPN priority queue
- Strategy document IDs added to OpenSearch

---

## Research Constraints

### Reproducibility Requirements
```yaml
seed_fixation:
  - Random seeds MUST be fixed and logged
  - Same seed + same code = same result

statistical_evidence:
  - p < 0.05 for significance claims
  - Effect size (Cohen's d) for practical significance
  - Confidence intervals for all estimates

trust_scores:
  - Every strategy document has trust_score (0.0-1.0)
  - Computed from: run_count, win_rate, variance
  - Low trust → more exploration needed
```

### Performance Constraints
```yaml
decision_latency:
  - Rust agent decision: < 100ms (P99)
  - OpenSearch kNN query: < 100ms (P99)
  - Total frame processing: < 200ms (P99)

no_realtime_llm:
  - LLM calls ONLY during:
    - Episode retrospection (after game ends)
    - Generation evolution (between generations)
    - Experiment analysis (after DOE run completes)
  - NEVER during gameplay loop
```

---

## External Dependencies

### Required Tools

| Tool | Purpose | Status |
|------|---------|--------|
| Docker + Docker Compose | Full stack orchestration | Required |
| Rust (stable) | Agent core development | Required |
| Go 1.21+ | Orchestrator development | Required |
| Python 3.11+ | VizDoom glue only | Required |
| Node.js 18+ | Dashboard frontend | Required |
| Claude Code CLI | Research analysis | Required |

### Container Stack

| Container | Image | Purpose |
|-----------|-------|---------|
| opensearch | opensearchproject/opensearch:2.x | RAG vector search |
| mongodb | mongo:7.x | Knowledge catalog |
| nats | nats:latest | Agent messaging |
| ollama | ollama/ollama:latest | Embeddings |
| vizdoom | Custom (VizDoom + Xvfb + noVNC) | Game environment |

---

## Experimental Features

### Agent Teams (Research Preview)

Native Agent Teams is available but NOT adopted as primary pattern.

```
Current approach: Task tool parallel execution (R009/R010)
Agent Teams:      Opt-in for evaluation only
```

| Feature | Current System | Agent Teams |
|---------|---------------|-------------|
| Parallel execution | Task tool (max 4) | Native (no hard limit) |
| Inter-agent messaging | Not supported | Native mailbox |
| Token cost | Controlled (model per agent) | Higher (full context each) |
| Determinism | High (structured routing) | Lower (natural language) |

**Decision**: Keep Task-based approach as primary. Agent Teams may be evaluated for complex multi-agent research collaboration when it exits research preview.

---

## Publication Target

### Venues
- **Primary**: NeurIPS (Conference on Neural Information Processing Systems)
- **Secondary**: ICML (International Conference on Machine Learning)
- **Alternative**: AAAI, AAMAS

### Contribution Claims
1. RAG-based agent skill accumulation (no real-time LLM)
2. DOE-driven systematic optimization (vs. ad-hoc tuning)
3. Quality engineering for generational evolution
4. Reproducible multi-agent research framework

### Evaluation Criteria
- Statistical significance of improvements (ANOVA)
- Generalization across DOOM scenarios
- Computational efficiency (decision latency < 100ms)
- Knowledge transfer effectiveness (cross-agent learning)

---

## Development Workflow

### Branch Strategy
```
main        - Stable releases only
develop     - Main development branch
feature/*   - New features → PR to develop
experiment/* - Research experiments → PR to develop
docs/*      - Documentation updates → PR to develop
```

### Commit Convention
```
type(scope): subject

Types:
  feat: New feature
  fix: Bug fix
  docs: Documentation
  exp: Experiment (new DOE run, analysis)
  refactor: Code refactoring
  test: Test updates
  chore: Build/tooling
```

### Pre-Push Checklist
```
□ mgr-sauron:watch passed (R017)
□ All tests pass
□ No uncommitted experiment results
□ Statistical claims have evidence files
□ Seeds are fixed and logged
```

---

## Getting Started

### First Session Commands

```bash
# 1. Verify environment
/status

# 2. Check existing agents
ls .claude/agents/*.md | wc -l

# 3. Verify rules
ls .claude/rules/*.md

# 4. Start experiment planning
# (User describes research goal in Korean)
# System routes to research-pi agent
```

### Research Session Template

```
1. Hypothesis formation (research-pi)
2. DOE design (research-pi)
3. Parallel execution (research-doe-runner)
4. Statistical analysis (research-analyst)
5. Knowledge curation (research-rag-curator)
6. Generation evolution (research-evolution-mgr)
7. Results aggregation (main conversation)
8. Paper section draft (research-paper-writer)
```

---

## Contact & References

### Project Lead
- **PI**: Sang Yi
- **Institution**: Research Lab (TBD)
- **Contact**: TBD

### Related Work
- See `docs/02_literature/` for literature review
- See `docs/03_clau-doom-research/` for research notes

### Code Repository
- **Main**: clau-doom (this project)
- **Related**: baekgom-agents (agent framework)
