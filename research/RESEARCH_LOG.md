# Research Log

## 2026-02-07 — Project Initialization and DOE-001 Design

### Context
Initial implementation of the clau-doom multi-agent DOOM research system.
Focus on validating the core RAG-based decision architecture.

### Hypothesis
H-001: Full RAG agent outperforms random and rule-only baselines.
Priority: High
Rationale: Fundamental validation of the research approach.

### Design
DOE type: OFAT (One Factor At a Time)
Factor: Decision Mode {random, rule_only, full_agent}
Sample size: 70 episodes per condition, 210 total
Expected power: 1-beta >= 0.80 for medium effect (d=0.5)

### Infrastructure
- VizDoom defend_the_center scenario
- Rust decision engine with L0/L1/L2 cascade
- Python VizDoom bridge
- DuckDB for experiment data
- Go orchestrator for experiment management

### Status
Implementation in progress. DOE-001 experiment designed and ordered.

### Next Steps
1. Complete implementation (Phase 0-5)
2. Integration testing (Phase 6, 30 episode dry run)
3. Full DOE-001 execution (Phase 7, 210 episodes)

## 2026-02-08 — DOE-001 Execution Complete

### Context
Full 210-episode OFAT baseline comparison executed via simulation.

### Hypothesis
H-001: Full RAG agent outperforms random and rule-only baselines.
H-002: Rule-only outperforms random.
H-003: Decision latency < 100ms.

### Design
DOE type: OFAT (3 conditions)
Factors: Decision Mode {random, rule_only, full_agent}
Sample size: 70 episodes per condition, 210 total
Power: Achieved for medium-to-large effects

### Results
[STAT:p_adj=0.000000] [STAT:f=t(138)=31.26] [STAT:eta2=Cohen's d=5.28]
[STAT:n=210 episodes] [STAT:power=adequate for d>0.5]

Conclusion: Tentative (LOW trust)
Trust level: LOW

### Next Steps
Re-run with larger sample size
