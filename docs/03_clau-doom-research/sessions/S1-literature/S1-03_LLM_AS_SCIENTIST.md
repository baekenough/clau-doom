# S1-03: LLM-as-Scientist Literature Review

> **Session**: S1 (Literature Review)
> **Priority**: Medium
> **Dependencies**: None
> **Status**: Complete

---

## Objective

Survey existing work on LLMs autonomously designing and conducting scientific experiments. Establish how clau-doom's research-pi agent (an LLM-based Principal Investigator that autonomously designs DOE experiments, interprets statistical results, and evolves agent populations across generations) differs from prior approaches.

---

## Category A: LLM-as-Scientist / Autonomous Research

### A1. The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery

- **Authors**: Chris Lu, Cong Lu, Robert Tjarko Lange, Jakob Foerster, Jeff Clune, David Ha
- **Venue**: arXiv:2408.06292 (2024), Sakana AI / University of Oxford / University of British Columbia
- **URL**: https://arxiv.org/abs/2408.06292

**Summary**: The AI Scientist is the first comprehensive framework for fully automated scientific discovery. Given a research direction, the system autonomously generates novel research ideas, writes and executes code, visualizes results, writes a full scientific paper, and runs a simulated peer review for evaluation. The system was demonstrated on ML sub-fields including diffusion models, language modeling, and learning dynamics.

**Key Results**:
- End-to-end pipeline: idea generation -> experiment execution -> paper writing -> automated review
- Cost approximately $15 per paper generated
- Papers evaluated by automated reviewer showed quality comparable to marginal workshop submissions
- Single-model architecture (Claude 3.5 Sonnet, GPT-4o, or Llama-3.1-405B as backbone)

**clau-doom Connection**:
- Both automate the hypothesis -> experiment -> analysis loop
- **Difference 1 (Cumulative vs. One-shot)**: AI Scientist generates single papers per run; clau-doom's PI accumulates knowledge across generations, building on prior findings with trust scores
- **Difference 2 (PI/Executor Separation)**: AI Scientist uses a monolithic single-model pipeline; clau-doom separates the PI (Opus, designs experiments) from executors (agents that run experiments) and analysts (statistical analysis agents)
- **Difference 3 (Domain)**: AI Scientist targets ML research; clau-doom targets game AI with physical simulation and real-time decision constraints
- **Difference 4 (Statistical Rigor)**: AI Scientist uses informal evaluation; clau-doom enforces DOE, ANOVA, residual diagnostics, and trust scoring

### A2. The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search

- **Authors**: Chris Lu, Cong Lu, Robert Tjarko Lange, Yutian Chen, Sebastian Riedel, David Ha
- **Venue**: arXiv:2504.08066 (2025), Sakana AI; presented at ICLR 2025 Workshop
- **URL**: https://arxiv.org/abs/2504.08066

**Summary**: The successor to AI Scientist v1 removes reliance on human-authored code templates and introduces an experiment manager agent with a novel agentic tree-search algorithm for deeper, more systematic exploration of the research space. Notably, it produced the first entirely AI-generated paper accepted through peer review at a workshop level (ICLR 2025 Workshop "I Can't Believe It's Not Better").

**Key Advances Over v1**:
- Autonomous code generation via tree search (no human templates)
- Enhanced VLM integration for experiment feedback and manuscript review
- Experiment manager agent that orchestrates the research process
- Workshop-level acceptance through formal peer review

**clau-doom Connection**:
- v2's experiment manager agent parallels clau-doom's orchestrator pattern
- v2's tree search over research directions is conceptually similar to clau-doom's hypothesis backlog with priority ordering
- **Key Difference**: v2 explores breadth of ML topics; clau-doom explores depth in a single domain (game AI) with systematic DOE phase progression (OFAT -> Factorial -> RSM -> Split-Plot)
- **Key Difference**: v2 evaluates success by peer review acceptance; clau-doom evaluates by quantitative game performance metrics with statistical significance tests

### A3. Autonomous Chemical Research with Large Language Models (Coscientist)

- **Authors**: Daniil A. Boiko, Robert MacKnight, Ben Kline, Gabe Gomes
- **Venue**: Nature 624, 570-578 (2023)
- **URL**: https://www.nature.com/articles/s41586-023-06792-0

**Summary**: Coscientist is a GPT-4-driven system that autonomously designs, plans, and performs complex chemistry experiments. It integrates internet search, documentation lookup, code execution, and robotic laboratory automation. Demonstrated across six diverse tasks including successful reaction optimization of palladium-catalysed cross-couplings.

**Key Results**:
- Autonomous planning and execution of Suzuki and Sonogashira cross-coupling reactions
- Multi-module architecture: Planner (LLM), Web Searcher, Code Executor, Hardware Controller
- Successfully optimized reaction conditions (temperature, catalyst loading, solvent) through iterative experimentation
- Connected to physical robotic hardware (Opentrons OT-2) for real wet-lab execution

**clau-doom Connection**:
- Both use LLMs to drive iterative experimental optimization with real execution
- Coscientist's multi-module architecture (Planner + Executor + Hardware) mirrors clau-doom's PI + DOE-runner + game environment separation
- **Key Difference**: Coscientist operates in physical chemistry; clau-doom operates in simulated game environments allowing much faster iteration (episodes vs. real reactions)
- **Key Difference**: Coscientist optimizes a handful of parameters informally; clau-doom uses formal DOE methodology (factorial designs, ANOVA, effect sizes)

---

## Category B: Hypothesis Search / Automated Scientific Discovery

### B1. FunSearch: Mathematical Discoveries from Program Search with Large Language Models

- **Authors**: Bernardino Romera-Paredes, Mohammadamin Barekatain, Alexander Novikov, et al.
- **Venue**: Nature 625, 468-475 (2024), Google DeepMind
- **URL**: https://www.nature.com/articles/s41586-023-06924-6

**Summary**: FunSearch pairs a pre-trained LLM (Codey) with an automated evaluator in an evolutionary search loop. Instead of searching for solutions directly, it searches for programs that generate solutions. Applied to the cap set problem in extremal combinatorics, FunSearch discovered new constructions surpassing the best known results (the first improvement in 20 years to the asymptotic lower bound). Also applied to online bin packing, where it found heuristics improving on widely used baselines.

**Key Architecture**:
- LLM generates candidate programs (mutations of best-so-far programs)
- Evaluator scores programs automatically (no human in the loop)
- Island-based evolutionary strategy maintains population diversity
- Best programs are fed back to the LLM as few-shot examples

**clau-doom Connection**:
- FunSearch's evolutionary program search parallels clau-doom's generational evolution of agent configurations
- Both use automatic evaluation (FunSearch: mathematical score; clau-doom: game performance metrics)
- Both maintain population diversity (FunSearch: island model; clau-doom: TOPSIS multi-criteria selection)
- **Key Difference**: FunSearch evolves programs; clau-doom evolves agent parameters/strategies through DOE-guided optimization
- **Key Difference**: FunSearch uses informal evolutionary search; clau-doom uses formal DOE with statistical validation before adopting changes
- **Shared Principle**: LLM as generator + automated evaluator as fitness function

### B2. Survey: From Automation to Autonomy: LLMs in Scientific Discovery

- **Authors**: Multiple authors, HKUST-KnowComp
- **Venue**: EMNLP 2025, arXiv:2505.13259
- **URL**: https://arxiv.org/html/2505.13259v1

**Summary**: Comprehensive survey organizing LLM applications in scientific discovery into three levels of increasing autonomy:
1. **LLM as Tool**: Assists with specific subtasks (literature search, code generation)
2. **LLM as Analyst**: Processes and interprets data with more autonomy
3. **LLM as Scientist**: Autonomously conducts the full scientific method (observation -> hypothesis -> experiment -> analysis -> conclusion -> iteration)

**Key Findings**:
- The field is moving from tool-level assistance to scientist-level autonomy
- Key challenges include hallucination in hypothesis generation, reproducibility of experiments, and evaluation of novelty
- Most existing systems operate at the Analyst level; very few achieve true Scientist-level autonomy

**clau-doom Connection**:
- clau-doom's research-pi agent operates at the "LLM as Scientist" level
- The survey's framework helps position clau-doom: it is one of few systems attempting full autonomy with built-in statistical rigor
- clau-doom addresses the reproducibility challenge through fixed seeds, ANOVA, and audit trails (R100, R102)

---

## Category C: LLM for Experimental Design / Optimization

### C1. AgentHPO: Large Language Model Agent for Hyper-Parameter Optimization

- **Authors**: Siyi Liu, Chen Gao, Yong Li
- **Venue**: arXiv:2402.01881 (2024)
- **URL**: https://arxiv.org/abs/2402.01881

**Summary**: AgentHPO is an LLM-based agent system for hyperparameter optimization that uses two specialized agents: a Creator (generates initial hyperparameters from natural language task descriptions) and an Executor (runs experiments and iteratively refines parameters based on historical trials). Tested on 12 representative ML tasks.

**Key Results**:
- Matches or surpasses best human trials on 12 ML benchmarks
- At T=10 trials, AgentHPO (GPT-3.5) outperforms random search by 2.65% and Bayesian optimization by 1.39%
- Provides explainable optimization reasoning
- Reduces number of required trials compared to traditional AutoML

**clau-doom Connection**:
- AgentHPO's Creator/Executor pattern directly parallels clau-doom's PI/DOE-runner separation
- Both iterate based on historical trial performance
- **Key Difference**: AgentHPO optimizes ML hyperparameters; clau-doom optimizes game agent behavior parameters
- **Key Difference**: AgentHPO uses informal iteration; clau-doom uses formal DOE methodology (factorial/RSM designs with ANOVA validation)
- **Key Difference**: AgentHPO has no concept of multi-generational evolution; clau-doom accumulates knowledge across generations

### C2. Using Large Language Models for Hyperparameter Optimization

- **Authors**: Michael R. Zhang, Nishkrit Desai, Juhan Bae, Jonathan Lorraine, Jimmy Ba
- **Venue**: arXiv:2312.04528 (2023)
- **URL**: https://arxiv.org/abs/2312.04528

**Summary**: Demonstrates that LLMs can serve as effective hyperparameter optimizers by prompting them with dataset and model descriptions, then iteratively refining suggestions based on performance feedback. Within constrained search budgets, LLMs match or outperform traditional HPO methods like Bayesian optimization.

**Key Results**:
- LLMs match Bayesian optimization performance under constrained budgets
- Natural language interface simplifies experiment specification
- LLM can leverage prior knowledge about ML tasks and common hyperparameter ranges

**clau-doom Connection**:
- Demonstrates LLMs' capability to reason about experimental parameters, validating clau-doom's approach
- **Key Difference**: This work focuses on one-shot optimization; clau-doom's PI maintains long-term research memory and builds on cumulative findings

### A4. Autonomous LLM-Driven Research: From Data to Human-Verifiable Research Papers (data-to-paper)

- **Authors**: Tal Ifargan, Lukas Hafner, Maor Kern, Ori Alcalay, Roy Kishony
- **Venue**: NEJM AI, 2024; arXiv:2404.17605
- **URL**: https://ai.nejm.org/doi/full/10.1056/AIoa2400555

**Summary**: data-to-paper is an automation platform that guides interacting LLM agents through a complete stepwise research process starting with annotated data and resulting in comprehensive research papers. The system programmatically backtraces information flow, maintaining a complete audit trail of how each result was derived.

**Key Results**:
- In autopilot mode: raises hypotheses, designs research plans, writes/debugs analysis code, interprets results, creates complete papers
- 80-90% success rate on simple research goals without major errors (recapitulates findings of peer-reviewed publications)
- As goal/data complexity increases, human copiloting becomes critical
- Backward traceability: every claim traces to specific data transformations and code

**clau-doom Connection**:
- data-to-paper's backward traceability directly parallels clau-doom's audit trail (R102: hypothesis -> order -> report -> findings)
- Both enforce structured stepwise research processes rather than monolithic generation
- **Key Difference**: data-to-paper processes existing datasets; clau-doom's PI designs and orders new experiments with DOE methodology
- **Key Difference**: data-to-paper's traceability is code-based; clau-doom's is document-based (MD files with statistical markers)
- **Key Insight**: The 80-90% accuracy on simple tasks and degradation on complex tasks validates clau-doom's approach of using statistical quality gates (ANOVA, trust scores) rather than relying on LLM correctness alone

---

## Category B: Hypothesis Search / Automated Scientific Discovery

(continued from above)

### B3. Why LLMs Aren't Scientists Yet: Lessons from Four Autonomous Research Attempts

- **Authors**: Multiple authors
- **Venue**: arXiv:2601.03315 (2026)
- **URL**: https://arxiv.org/abs/2601.03315

**Summary**: A critical case study examining four end-to-end attempts to autonomously generate ML research papers using a pipeline of six LLM agents. Three of four attempts failed during implementation or evaluation, yielding six documented failure modes.

**Six Failure Modes**:
1. Bias toward training data defaults (LLMs default to familiar configurations)
2. Implementation drift under execution pressure (code diverges from plan)
3. Memory and context degradation across long-horizon tasks
4. Overexcitement (declares success despite obvious failures)
5. Insufficient domain intelligence
6. Weak scientific taste in experimental design

**clau-doom Connection**:
- These failure modes directly validate clau-doom's architectural decisions:
  - Failure mode 1 (bias) -> DOE methodology forces systematic exploration, not LLM defaults
  - Failure mode 2 (implementation drift) -> PI boundary (R101) separates design from execution
  - Failure mode 3 (context degradation) -> MD file-based audit trail (R102) provides persistent state
  - Failure mode 4 (overexcitement) -> Statistical quality gates (ANOVA, trust scores) prevent false positives
  - Failure mode 6 (weak taste) -> Formal DOE phase progression provides structured research methodology
- This paper strengthens clau-doom's positioning: addressing known LLM-as-scientist failure modes through engineering safeguards

### B4. AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery

- **Authors**: Google DeepMind
- **Venue**: Google DeepMind Technical Report (2025)
- **URL**: Referenced in LITERATURE_REVIEW.md

**Summary**: AlphaEvolve is a coding agent that combines LLM-based code generation with automated evaluation in a closed loop to discover improved algorithms. The system generates candidate solutions, executes them against formal evaluators, and iteratively refines based on results.

**clau-doom Connection**:
- AlphaEvolve's generate-evaluate-refine loop parallels clau-doom's PI -> execute -> analyze -> refine cycle
- Both use automated evaluation (AlphaEvolve: formal verifiers; clau-doom: game performance metrics + ANOVA)
- **Key Difference**: AlphaEvolve discovers algorithms (code); clau-doom discovers agent strategies (MD configurations)
- **Key Difference**: AlphaEvolve has no concept of experimental design methodology; clau-doom uses formal DOE

---

## Gap Analysis: What Makes clau-doom's PI Novel

### Existing Approaches Summary

| System | Autonomy | Statistical Rigor | Cumulative Learning | Domain | PI/Executor Split |
|--------|----------|-------------------|--------------------|---------|--------------------|
| AI Scientist v1 | Full (single paper) | Informal (automated review) | None (one-shot) | ML research | No (monolithic) |
| AI Scientist v2 | Full (workshop paper) | Informal (peer review) | Limited (tree search) | ML research | Partial (experiment manager) |
| Coscientist | Full (wet-lab) | Informal (yield optimization) | None (single experiment) | Chemistry | Yes (Planner/Executor) |
| data-to-paper | Full (data to paper) | Code-traced (backward) | None (single dataset) | Biomedical | Yes (multi-agent stepwise) |
| FunSearch | Full (program search) | Automated scoring | Evolutionary (programs) | Mathematics | No (LLM + Evaluator) |
| AlphaEvolve | Full (algorithm search) | Formal verifier | Evolutionary (code) | Math/Algorithms | No (LLM + Evaluator) |
| AgentHPO | Partial (HPO only) | Informal (accuracy comparison) | Limited (within session) | ML HPO | Yes (Creator/Executor) |

### clau-doom PI Novelty Claims

1. **Formal DOE Methodology**: No existing LLM-as-scientist system uses formal Design of Experiments (factorial, RSM, Taguchi) with ANOVA validation. Existing systems either use informal iteration or evolutionary search without statistical rigor.

2. **Multi-Generational Cumulative Learning**: While FunSearch evolves programs and AI Scientist generates papers, neither maintains a structured knowledge base (FINDINGS.md, trust scores) that accumulates across experiment generations. clau-doom's PI builds on prior findings with explicit trust levels.

3. **PI/Executor/Analyst Separation**: While Coscientist and AgentHPO have creator/executor patterns, clau-doom is unique in having a three-role separation (PI designs, DOE-runner executes, Analyst interprets) with strict boundary rules (R101).

4. **Statistical Quality Gates**: clau-doom enforces ANOVA residual diagnostics, effect size reporting, power analysis, and trust scoring before adopting findings. No existing system has this level of statistical rigor.

5. **DOE Phase Progression**: clau-doom has a systematic progression from OFAT -> Factorial -> RSM -> Split-Plot, with explicit phase transition criteria. This is a methodological contribution not found in any existing LLM-as-scientist system.

6. **Quality Engineering Integration**: SPC (Statistical Process Control), FMEA (Failure Mode and Effects Analysis), and TOPSIS (multi-criteria decision making) are integrated into the research workflow. This is entirely novel in the LLM-as-scientist space.

### Remaining Gaps to Address

- No direct empirical comparison with AI Scientist or Coscientist exists yet
- clau-doom's system is designed but not yet validated with end-to-end experimental results
- The claim that DOE is superior to informal LLM iteration needs experimental evidence (target for S2 experiments)
- Computational cost comparison (clau-doom's multi-agent overhead vs. single-model approaches) is needed

---

## Completion Criteria

- [x] Category A: 4 papers collected (AI Scientist v1, v2, Coscientist, data-to-paper)
- [x] Category B: 4 papers collected (FunSearch, EMNLP Survey, "Why LLMs Aren't Scientists Yet", AlphaEvolve)
- [x] Category C: 2 papers collected (AgentHPO, Zhang et al.)
- [x] clau-doom PI novelty claims articulated with 6 specific differentiators
- [x] Gap analysis completed with remaining work identified
- [x] Phase 2 verification: 3 missing papers added (2026-02-07)

---

## References

1. Lu, C. et al. (2024). The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery. arXiv:2408.06292.
2. Lu, C. et al. (2025). The AI Scientist-v2: Workshop-Level Automated Scientific Discovery via Agentic Tree Search. arXiv:2504.08066.
3. Boiko, D.A. et al. (2023). Autonomous chemical research with large language models. Nature 624, 570-578.
4. Romera-Paredes, B. et al. (2024). Mathematical discoveries from program search with large language models. Nature 625, 468-475.
5. HKUST-KnowComp (2025). From Automation to Autonomy: A Survey on LLMs in Scientific Discovery. EMNLP 2025. arXiv:2505.13259.
6. Liu, S. et al. (2024). AgentHPO: Large Language Model Agent for Hyper-Parameter Optimization. arXiv:2402.01881.
7. Zhang, M.R. et al. (2023). Using Large Language Models for Hyperparameter Optimization. arXiv:2312.04528.
8. Ifargan, T. et al. (2024). Autonomous LLM-Driven Research: From Data to Human-Verifiable Research Papers. NEJM AI. arXiv:2404.17605.
9. Multiple authors (2026). Why LLMs Aren't Scientists Yet: Lessons from Four Autonomous Research Attempts. arXiv:2601.03315.
10. Google DeepMind (2025). AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery.
