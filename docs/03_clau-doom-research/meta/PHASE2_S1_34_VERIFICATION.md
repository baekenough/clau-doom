# Phase 2 Verification: S1-03 (LLM-as-Scientist) & S1-04 (Doom RL Baseline)

> **Verifier**: research-pi
> **Date**: 2026-02-07
> **Status**: PASS WITH AMENDMENTS (both documents updated)

---

## Verification Criteria

Per REVIEW_SUMMARY.md requirements:
- S1-03: 2+ LLM-as-Scientist papers, 1+ Hypothesis Search, clau-doom PI novelty defined
- S1-04: 2+ VizDoom Competition winners, 2+ DRL FPS papers, quantitative baselines extracted

---

## S1-03: LLM-as-Scientist Literature Review

### Coverage Assessment

| Requirement | Met? | Details |
|-------------|------|---------|
| 2+ LLM-as-Scientist papers | YES (3) | AI Scientist v1, AI Scientist v2, Coscientist |
| 1+ Hypothesis Search paper | YES (1) | FunSearch |
| clau-doom PI novelty defined | YES (6 claims) | Formal DOE, cumulative learning, PI/Executor/Analyst separation, statistical quality gates, DOE phase progression, quality engineering integration |

### Accuracy Check

| Paper | Key Claim in Doc | Verified? | Notes |
|-------|-----------------|-----------|-------|
| AI Scientist v1 (Lu et al. 2024) | First comprehensive framework for automated scientific discovery, ~$15/paper | YES | arXiv:2408.06292 confirmed. Cost figure and capability description accurate. |
| AI Scientist v2 (Lu et al. 2025) | First AI-generated paper accepted at workshop peer review (ICLR 2025) | YES | Confirmed via Sakana AI announcement and arXiv:2504.08066. Accepted at ICLR 2025 Workshop "I Can't Believe It's Not Better". Key addition: v2 eliminates reliance on human code templates, uses agentic tree search. |
| Coscientist (Boiko et al. 2023) | GPT-4-driven autonomous chemistry with robotic hardware | YES | Nature 624, 570-578 confirmed. Suzuki/Sonogashira reactions with Opentrons OT-2. |
| FunSearch (Romera-Paredes et al. 2024) | Improved cap set problem lower bound (first in 20 years) | YES | Nature 625, 468-475 confirmed. Island-based evolutionary strategy. |
| EMNLP Survey (HKUST-KnowComp 2025) | Three-level taxonomy: Tool/Analyst/Scientist | YES | arXiv:2505.13259, published at EMNLP 2025. |
| AgentHPO (Liu et al. 2024) | Outperforms random search by 2.65% at T=10 trials | PARTIAL | arXiv:2402.01881 confirmed. Specific percentage should be cited more carefully as it varies by benchmark. |
| Zhang et al. 2023 | LLMs match Bayesian optimization under constrained budgets | YES | arXiv:2312.04528 confirmed. |

### Gap Analysis: Missing Papers

| Paper | Why Missing is a Problem | Priority |
|-------|-------------------------|----------|
| **data-to-paper** (Ifargan et al., NEJM AI 2024) | Directly relevant: LLM agents through full research process with backward traceability. Parallels clau-doom's audit trail (R102). 80-90% success rate on simple datasets. | HIGH - Added |
| **"Why LLMs Aren't Scientists Yet"** (arXiv:2601.03315, 2026) | Documents 6 failure modes of autonomous LLM research. Directly relevant to clau-doom's design decisions (PI boundary, statistical rigor). | HIGH - Added |
| **AlphaEvolve** (Google DeepMind 2025) | LLM-generate-execute-verify closed loop for algorithm improvement. Already in LITERATURE_REVIEW.md but missing from S1-03. | MEDIUM - Added |

### Quality of Gap Analysis

The existing gap analysis in S1-03 is STRONG. Six novelty claims are well-articulated and differentiated. The "Remaining Gaps to Address" section correctly identifies the need for empirical comparison. However, it should acknowledge the failure mode literature (LLMs losing coherence over long research horizons) as a risk factor for clau-doom.

### Integration Readiness for S4

S1-03 is READY for S4-01 Related Work integration with the following structure:
- Section "LLM as Autonomous Scientist": AI Scientist v1/v2, Coscientist, data-to-paper
- Section "Hypothesis and Program Search": FunSearch, AlphaEvolve
- Section "LLM for Experimental Optimization": AgentHPO, Zhang et al.
- Section "Challenges and Limitations": EMNLP Survey, "Why LLMs Aren't Scientists Yet"

---

## S1-04: Doom RL Baseline Literature Review

### Coverage Assessment

| Requirement | Met? | Details |
|-------------|------|---------|
| 2+ VizDoom Competition winners | YES (3) | F1 (2016 T1 winner), Arnold (2016 T2 2nd), IntelAct (2016 T2 winner) |
| 2+ DRL FPS papers | YES (4) | DFP/IntelAct, VizDoom platform, Schulze PPO, Felix Yu DQN-vs-PG |
| Quantitative baselines extracted | YES | Frag tables, per-scenario metrics, convergence episodes |
| LLM Doom baseline | YES (1) | de Wynter GPT-4 (0% completion) |

### Accuracy Check

| Paper | Key Claim in Doc | Verified? | Notes |
|-------|-----------------|-----------|-------|
| VizDoom Competitions (Wydmuch et al. 2019) | F1: 559 frags T1 2016, Arnold: 32.8 F/D T2 2016 | YES | IEEE Trans. Games 11(3), arXiv:1809.03470. Competition results tables match. |
| Arnold (Lample & Chaplot 2017) | DRQN + Nav/Action dual network, 2nd in 2016 both tracks | YES | AAAI 2017, arXiv:1609.05521. Architecture description accurate. |
| F1 (Wu & Tian 2017) | A3C + curriculum learning, won 10/12 rounds T1 2016 | YES | ICLR 2017. Performance claims accurate. |
| IntelAct/DFP (Dosovitskiy & Koltun 2017) | Direct Future Prediction, won T2 2016 with 297 frags | YES | ICLR 2017, arXiv:1611.01779. Architecture and results accurate. |
| VizDoom platform (Kempka et al. 2016) | Standard scenarios defined, DQN baseline on Basic | YES | IEEE CIG 2016, arXiv:1605.02097. Scenario list accurate. |
| Schulze et al. 2021 | PPO better convergence stability than Dueling DQN | PARTIAL | IEEE CINTI 2021 confirmed. Specific survival time numbers for Health Gathering Supreme are missing from S1-04 (says "Best in class" without number). |
| Felix Yu 2017 | DDQN ~11 kills, A2C ~12 kills on Defend the Center | YES | Blog post confirmed. Numbers match. |
| de Wynter 2024 | GPT-4 0/10 completion on E1M1, ~1 min/frame | YES | arXiv:2403.05468, also published in IEEE Trans. on Games 2024. Results table matches. |

### Gap Analysis: Missing Papers

| Paper | Why Missing is a Problem | Priority |
|-------|-------------------------|----------|
| **Gunner** (PeerJ CS 2025) | Latest VizDoom deathmatch results. Integrates scalable network + LSTM + Dueling + Noisy Networks. Already referenced in LITERATURE_REVIEW.md but not in S1-04. | HIGH - Added |
| **Khan et al. 2025** (CAVW 2025) | PPO + reward shaping + curriculum learning on Deadly Corridor. Record scores up to 2280 on difficulty 4. Provides latest RL baselines. Referenced in LITERATURE_REVIEW.md. | MEDIUM - Added |
| **Diffusion Models as Game Engines** (arXiv:2408.14837, GameNGen) | Not directly an RL agent but demonstrates neural Doom rendering. Relevant for context. | LOW - Not added (tangential) |

### Quantitative Baselines Quality

The baseline tables are STRONG. Key numbers present:
- Competition frags: F1 559, Arnold 413, IntelAct 297 (all verified)
- Per-scenario: DDQN ~11 kills, A2C ~12 kills (Defend the Center)
- Convergence: ~1,000 episodes (DQN Basic), ~5,000 episodes (A2C)
- LLM baseline: 0% completion, ~60,000ms latency
- Training requirements comparison table is excellent

**Minor issue**: Schulze et al. Health Gathering Supreme lacks a specific survival time number (just "Best in class"). This should be flagged for future update when the paper is consulted in detail.

### Integration Readiness for S4

S1-04 is READY for S4-01 Related Work integration with the following structure:
- Section "VizDoom Competition Agents": F1, Arnold, IntelAct, Marvin
- Section "DRL Approaches for FPS": DFP, PPO (Schulze, Khan), Gunner
- Section "LLM-Based Game Playing": de Wynter GPT-4
- Baseline comparison table can be directly included in Evaluation section

---

## Cross-Reference Check with LITERATURE_REVIEW.md

| Paper in LITERATURE_REVIEW.md | In S1-03? | In S1-04? | Notes |
|-------------------------------|-----------|-----------|-------|
| Reflexion (Shinn et al. 2023) | No (in S1-01/S1-02) | No | Correctly in S1-01 scope |
| Voyager (Wang et al. 2023) | No (in S1-01/S1-02) | No | Correctly in S1-01 scope |
| RL-GPT (Liu et al. 2024) | No (in S1-01/S1-02) | No | Correctly in S1-01 scope |
| Agent-Pro (Zhang et al. 2024) | No (in S1-01/S1-02) | No | Correctly in S1-01 scope |
| Will GPT-4 Run DOOM? | No | Yes | Correct placement |
| Arnold | No | Yes | Correct placement |
| F1 | No | Yes | Correct placement |
| Gunner | No | Missing -> Added | Now in S1-04 |
| Khan PPO 2025 | No | Missing -> Added | Now in S1-04 |
| AlphaEvolve | Missing -> Added | No | Now in S1-03 |

Cross-referencing is consistent. No duplicate coverage across S1 documents. Each document owns its topic area.

---

## Summary Verdicts

### S1-03: PASS WITH AMENDMENTS

**Strengths**:
- Comprehensive coverage of LLM-as-Scientist landscape (7 papers)
- Well-structured gap analysis with 6 specific novelty claims
- Strong differentiation table (System x Feature matrix)
- EMNLP survey provides taxonomic framing

**Amendments Made**:
- Added data-to-paper (NEJM AI 2024) as Category A4
- Added "Why LLMs Aren't Scientists Yet" (2026) as Category B3
- Added AlphaEvolve (DeepMind 2025) as Category B4

**Remaining Minor Issues**:
- AgentHPO "2.65% improvement" should note this is average across benchmarks
- No discussion of computational cost comparison (acknowledged in gap section)

### S1-04: PASS WITH AMENDMENTS

**Strengths**:
- Excellent quantitative baseline tables (competition + academic)
- Training requirements comparison table is publication-ready
- de Wynter GPT-4 paper provides perfect LLM baseline
- Gap analysis correctly identifies 5 key experiments clau-doom must run
- Recommended evaluation scenarios table is directly actionable

**Amendments Made**:
- Added Gunner (PeerJ CS 2025) as Category B5
- Added Khan et al. (CAVW 2025) as Category B6

**Remaining Minor Issues**:
- Schulze et al. Health Gathering Supreme lacks specific survival time number
- No 2018 competition results included (only 2016 and 2017)

---

## Verification Checklist

- [x] Paper coverage meets REVIEW_SUMMARY.md requirements
- [x] Key claims spot-checked via WebSearch (all verified or marked PARTIAL)
- [x] Quantitative baselines present with specific numbers
- [x] Gap analysis clearly articulates clau-doom novelty
- [x] Missing recent papers identified and added to source documents
- [x] Integration readiness for S4-01 assessed (both READY)
- [x] Cross-reference with LITERATURE_REVIEW.md checked (no gaps)
