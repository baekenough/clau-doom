# S1-01: Evolution and Collective Intelligence Literature Survey

> **Session**: S1 (Literature Collection)
> **Priority**: RED critical
> **Dependencies**: None
> **Status**: COMPLETE

---

## Purpose

Collect prior research supporting the core contribution of "multi-agent knowledge sharing + natural selection" in the clau-doom project. This survey covers Quality-Diversity algorithms, LLM-based evolutionary optimization, and multi-agent cooperation/competition mechanisms that form the theoretical foundation for MD-based agent evolution.

---

## Category A: Quality-Diversity / MAP-Elites

**Why needed**: clau-doom's generational evolution requires balancing elite preservation with mutation diversity. QD algorithms provide the theoretical basis for maintaining strategy diversity while improving performance across generations.

---

### A1. Illuminating Search Spaces by Mapping Elites (Mouret & Clune, 2015, arXiv)

- **Full citation**: Mouret, J.-B. & Clune, J. (2015). Illuminating search spaces by mapping elites. arXiv:1504.04909.
- **Link**: https://arxiv.org/abs/1504.04909

- **Core contribution**: Introduces the MAP-Elites algorithm, which maintains a multi-dimensional archive of high-performing solutions organized by user-defined behavioral dimensions. Instead of converging to a single optimum, MAP-Elites fills a grid where each cell stores the best solution found for that particular combination of behavioral characteristics. The algorithm uses random variation (mutation/crossover) to generate new candidates, which replace existing archive entries only if they achieve higher fitness in the same cell.

- **clau-doom relevance**: MAP-Elites' archive mechanism directly maps to clau-doom's generational evolution design. Each agent's MD file represents a "genome," and the behavioral dimensions could be defined by strategy characteristics (e.g., aggression level vs. exploration tendency). The archive concept provides a principled way to maintain strategic diversity across the agent population while preserving high-performing configurations, preventing premature convergence to a single dominant playstyle.

- **Differentiation**: MAP-Elites operates on continuous parameter vectors or neural network weights; clau-doom evolves structured text documents (MD files) through LLM-mediated crossover/mutation. This introduces semantic-level variation rather than numerical perturbation.

- **Reference type**: Direct citation (foundational algorithm)

---

### A2. Robots That Can Adapt Like Animals (Cully et al., 2015, Nature)

- **Full citation**: Cully, A., Clune, J., Tarapore, D. & Mouret, J.-B. (2015). Robots that can adapt like animals. Nature, 521(7553), 503-507.
- **Link**: https://arxiv.org/abs/1407.3501

- **Core contribution**: Demonstrates an Intelligent Trial-and-Error (IT&E) algorithm that enables robots to recover from damage in under two minutes. Before deployment, a QD algorithm (MAP-Elites) pre-computes a "behavioral repertoire map" of high-performing locomotion behaviors. When the robot is damaged, it uses Bayesian optimization over this map to rapidly find compensatory behaviors. The key insight is that the pre-computed map serves as a structured prior over the space of possible behaviors.

- **clau-doom relevance**: The two-phase architecture (offline map creation + online adaptation) is structurally similar to clau-doom's design: the OpenSearch strategy document collection serves as a "behavioral repertoire map," and the Rust scoring engine performs rapid online selection analogous to Bayesian optimization over the map. Cully et al.'s concept of a pre-computed behavioral prior validates clau-doom's approach of accumulating strategy documents offline (via episode retrospection) and using them for fast online decision-making (< 100ms kNN lookup).

- **Differentiation**: Cully et al. use continuous parameter spaces and Gaussian process regression for adaptation; clau-doom uses discrete strategy documents with Wilson score confidence intervals for trust-weighted selection. clau-doom's documents are human-readable and editable, enabling human-in-the-loop refinement.

- **Reference type**: Direct citation (methodology inspiration)

---

### A3. Differentiable Quality Diversity (Fontaine & Nikolaidis, 2021, NeurIPS)

- **Full citation**: Fontaine, M. C. & Nikolaidis, S. (2021). Differentiable Quality Diversity. Advances in Neural Information Processing Systems, 34.
- **Link**: https://arxiv.org/abs/2106.03894

- **Core contribution**: Formalizes the Differentiable Quality Diversity (DQD) problem and proposes MAP-Elites via a Gradient Arborescence (MEGA), which leverages gradient information from both objective and behavioral measure functions. When these functions are differentiable, MEGA achieves significantly faster and more effective archive filling than black-box QD methods. The paper introduces CMA-MEGA, combining Covariance Matrix Adaptation with gradient-based QD.

- **clau-doom relevance**: While clau-doom's MD file evolution is not directly differentiable, the DQD framework suggests that if behavioral descriptors (e.g., kill_rate, survival_time) can be related to document features through a differentiable proxy model, gradient information could accelerate evolution. This positions a potential future extension: training a surrogate model that predicts agent performance from document embeddings, enabling gradient-guided document evolution rather than purely random mutation.

- **Differentiation**: DQD requires differentiable objective/measure functions operating on continuous spaces. clau-doom's evolution operates on discrete text representations through LLM-mediated operators. The non-differentiable nature of text mutation is a fundamental architectural difference that clau-doom addresses through LLM semantic understanding rather than gradient computation.

- **Reference type**: Background reference (theoretical extension)

---

### A4. LLMatic: Neural Architecture Search via Large Language Models and Quality Diversity Optimization (Nasir et al., 2023, GECCO 2024)

- **Full citation**: Nasir, M. U., Earle, S., Togelius, J., James, S. & Cleghorn, C. (2023). LLMatic: Neural Architecture Search via Large Language Models and Quality Diversity Optimization. GECCO '24.
- **Link**: https://arxiv.org/abs/2306.01102

- **Core contribution**: Combines LLM code generation with MAP-Elites quality-diversity search for neural architecture search (NAS). LLMatic uses LLMs as mutation and crossover operators within a QD framework, where model complexity (FLOPS) serves as the diversity metric. The system discovers diverse, high-performing architectures while evaluating only 2,000 candidates, demonstrating that LLM-guided QD can be remarkably sample-efficient.

- **clau-doom relevance**: LLMatic is the closest existing work to clau-doom's architecture: both use LLMs as evolutionary operators within a QD framework, and both evolve structured text artifacts (code vs. MD documents). LLMatic's use of MAP-Elites to maintain architectural diversity directly parallels clau-doom's need to maintain strategic diversity across agent populations. The key difference is the domain (NAS vs. game agent strategies) and the artifact type (Python code vs. Markdown strategy documents).

- **Differentiation**: LLMatic evolves code that is evaluated by running neural network training; clau-doom evolves strategy documents that are evaluated through gameplay episodes. clau-doom's evaluation loop is longer (multiple episodes per evaluation) but produces richer behavioral data. LLMatic requires GPU-intensive evaluation; clau-doom's Rust scoring engine operates at < 100ms per decision.

- **Reference type**: Direct citation (closest related work in QD + LLM space)

---

### A5. Quality-Diversity through AI Feedback (Bradley et al., 2024, ICLR)

- **Full citation**: Bradley, H., Dai, A., Teuber, T., Zhang, M., Oostermeijer, K., Bellagente, M., Clune, J., Stanley, K., Schott, G. & Lehman, J. (2024). Quality-Diversity through AI Feedback. ICLR 2024.
- **Link**: https://openreview.net/forum?id=owokKCrGYr

- **Core contribution**: Introduces QDAIF, which uses LLMs as both variation operators and evaluators within a MAP-Elites framework. Unlike standard MAP-Elites which requires hand-designed quality and diversity metrics, QDAIF leverages LLM-based AI feedback to assess both the quality and diversity of generated text artifacts. Applied to creative writing domains (opinion pieces, stories, poetry), QDAIF produces archives that are both more diverse and higher-quality than baselines, as verified by human evaluation showing strong alignment between AI and human judgments.

- **clau-doom relevance**: QDAIF demonstrates that LLMs can serve as the evaluation mechanism within QD loops, not just as variation operators. In clau-doom, the LLM already serves as the mutation/crossover operator (like EvoPrompting, LMX); QDAIF suggests the LLM could additionally evaluate strategy document diversity and quality during the curation process. More directly, QDAIF's demonstration that MAP-Elites works effectively on text artifacts (not just numerical parameters or code) validates clau-doom's approach of evolving Markdown strategy documents through QD-inspired mechanisms.

- **Differentiation**: QDAIF operates on creative writing with subjective quality metrics evaluated by LLMs; clau-doom evaluates strategy documents through objective gameplay metrics (kill_rate, survival_time) with statistical rigor (DOE/ANOVA). QDAIF uses the same LLM for both variation and evaluation; clau-doom separates these roles (LLM for variation/retrospection, Rust scoring engine + DOE for evaluation). QDAIF's evaluation is immediate (single LLM call); clau-doom's evaluation requires multi-episode gameplay.

- **Reference type**: Direct citation (QD + LLM + text artifacts)

---

## Category B: LLM-Based Evolutionary Optimization

**Why needed**: clau-doom's MD file crossover/mutation is fundamentally "evolving text through LLMs." Direct comparison with existing LLM-as-evolutionary-operator approaches is essential for positioning the contribution.

---

### B1. EvoPrompting: Language Models for Code-Level Neural Architecture Search (Chen et al., 2023, NeurIPS)

- **Full citation**: Chen, A., Dohan, D. & So, D. (2023). EvoPrompting: Language Models for Code-Level Neural Architecture Search. NeurIPS 2023.
- **Link**: https://arxiv.org/abs/2302.14838

- **Core contribution**: Uses LLMs as adaptive mutation and crossover operators for evolutionary NAS. EvoPrompting combines evolutionary prompt engineering with soft prompt-tuning, achieving state-of-the-art results on MNIST-1D and the CLRS Algorithmic Reasoning Benchmark. The method outperforms both human-designed architectures and naive few-shot prompting, demonstrating that LLMs can serve as intelligent variation operators that understand domain semantics.

- **clau-doom relevance**: EvoPrompting's "LLM as crossover/mutation operator" paradigm is directly analogous to clau-doom's approach. In clau-doom, the LLM takes two parent strategy documents and produces offspring documents, paralleling EvoPrompting's code crossover. The key validation from EvoPrompting is that LLM-mediated evolution produces meaningfully diverse offspring rather than degenerate copies, which is critical for clau-doom's strategy evolution to work.

- **Differentiation**: EvoPrompting operates on Python code for neural architectures with automated fitness evaluation (accuracy/FLOPS); clau-doom operates on Markdown strategy documents with multi-episode gameplay evaluation. EvoPrompting targets a single optimization objective; clau-doom requires multi-objective optimization (kill_rate, survival_time, ammo_efficiency) handled through TOPSIS/AHP.

- **Reference type**: Direct citation (methodology parallel)

---

### B2. Evolution through Large Models (Lehman et al., 2023, Handbook of Evolutionary Machine Learning)

- **Full citation**: Lehman, J., Gordon, J., Jain, S., Ndousse, K., Yeh, C. & Stanley, K. O. (2023). Evolution through Large Models. In Handbook of Evolutionary Machine Learning, Springer.
- **Link**: https://arxiv.org/abs/2206.08896

- **Core contribution**: Proposes using LLMs trained on code as mutation operators for genetic programming, introducing the "diff" mutation operator that generates incremental code changes mimicking human programming behavior. Combined with MAP-Elites, the system (ELM) generates hundreds of thousands of functional Python programs for Sodarace walker design. A key contribution is bootstrapping: ELM-generated examples are used to fine-tune a conditional language model for terrain-specific walker generation.

- **clau-doom relevance**: ELM's "diff" operator is conceptually identical to what clau-doom does when mutating MD strategy documents: the LLM generates incremental modifications rather than regenerating from scratch. The bootstrapping concept, where evolution-generated examples improve the LLM itself, maps to clau-doom's RAG curation loop where successful strategies improve the OpenSearch knowledge base, which in turn informs future strategy generation. ELM combined with MAP-Elites provides the most direct precedent for clau-doom's architecture.

- **Differentiation**: ELM evolves code for physical simulation (robot walkers); clau-doom evolves declarative strategy documents for real-time game agents. ELM's bootstrapping fine-tunes the LLM weights; clau-doom's improvement loop operates through RAG (document quality improvement) rather than model fine-tuning, avoiding the computational cost and catastrophic forgetting risks of fine-tuning.

- **Reference type**: Direct citation (closest theoretical framework)

---

### B3. FunSearch: Mathematical Discoveries from Program Search with Large Language Models (Romera-Paredes et al., 2024, Nature)

- **Full citation**: Romera-Paredes, B., Barekatain, M., Novikov, A. et al. (2024). Mathematical discoveries from program search with large language models. Nature, 625, 468-475.
- **Link**: https://www.nature.com/articles/s41586-023-06924-6

- **Core contribution**: Pairs a pretrained LLM with a systematic evaluator in an evolutionary loop to discover new mathematical constructions. FunSearch searches in the space of programs rather than solutions, making discoveries interpretable and deployable. Applied to the cap set problem in extremal combinatorics, FunSearch discovered constructions surpassing the previously best-known results. Also found novel bin packing heuristics that improve on widely-used baselines.

- **clau-doom relevance**: FunSearch's key insight, that searching in program space with automated evaluation produces better results than searching in solution space, validates clau-doom's approach of evolving strategy documents (analogous to programs) rather than directly optimizing numerical parameters. The automated evaluator concept maps to clau-doom's DOE-based evaluation framework, where statistical rigor replaces ad-hoc evaluation. FunSearch's interpretability advantage (discovered programs can be understood and modified by humans) parallels clau-doom's MD documents being human-readable.

- **Differentiation**: FunSearch targets mathematical optimization with deterministic evaluation; clau-doom operates in a stochastic game environment requiring statistical evaluation (ANOVA, confidence intervals). FunSearch uses a single-agent evolutionary loop; clau-doom uses multi-agent co-evolution with knowledge sharing through NATS messaging.

- **Reference type**: Direct citation (methodology validation)

---

### B4. Language Model Crossover: Variation through Few-Shot Prompting (Meyerson et al., 2023, ACM TELO)

- **Full citation**: Meyerson, E. et al. (2023). Language Model Crossover: Variation through Few-Shot Prompting. ACM Transactions on Evolutionary Learning and Optimization.
- **Link**: https://arxiv.org/abs/2302.12170

- **Core contribution**: Formalizes Language Model Crossover (LMX), demonstrating that LLMs naturally serve as crossover operators through few-shot prompting. By presenting a small number of text-based genotypes as prompts, the LLM generates offspring incorporating associations from all parents. LMX produces high-quality offspring across diverse domains: binary strings, mathematical expressions, English sentences, image generation prompts, and Python code. The work shows that in-context learning enables domain-general crossover without domain-specific engineering.

- **clau-doom relevance**: LMX provides direct theoretical justification for clau-doom's MD document crossover mechanism. When clau-doom presents two parent strategy documents to an LLM and asks for an offspring, it is performing exactly the LMX operation. Meyerson et al.'s demonstration that LMX works across diverse text representations (including structured documents and code) validates the feasibility of crossing over Markdown strategy documents. The domain-generality of LMX means clau-doom does not need to engineer domain-specific crossover operators.

- **Differentiation**: LMX studies crossover in isolation as a standalone operator; clau-doom integrates crossover within a full evolutionary pipeline including selection (TOPSIS), evaluation (DOE), and knowledge accumulation (RAG). LMX does not address the question of maintaining archive diversity; clau-doom combines crossover with QD-inspired diversity maintenance.

- **Reference type**: Direct citation (operator validation)

---

### B5. AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery (Google DeepMind, 2025)

> **Cross-ref**: Also mentioned briefly in LITERATURE_REVIEW.md section 4.3. This entry provides full academic analysis.

- **Full citation**: Google DeepMind. (2025). AlphaEvolve: A coding agent for scientific and algorithmic discovery. arXiv:2506.13131.
- **Link**: https://arxiv.org/abs/2506.13131

- **Core contribution**: An evolutionary coding agent powered by Gemini LLMs for general-purpose algorithm discovery. AlphaEvolve pairs LLM creative problem-solving with automated evaluators, using an evolutionary framework to refine the most promising ideas. It uses an ensemble approach: Gemini Flash for breadth of exploration, Gemini Pro for depth. Achievements include the first improvement to Strassen's matrix multiplication algorithm in 56 years, a 0.7% recovery of Google's worldwide compute resources through better heuristics, and 23-32% speedups in AI training kernels.

- **clau-doom relevance**: AlphaEvolve demonstrates the scalability and practical impact of LLM-driven evolution at industrial scale. Its ensemble approach (fast model for exploration, strong model for exploitation) directly informs clau-doom's model selection strategy: using Haiku/Sonnet for rapid mutation generation and Opus for complex strategic reasoning. AlphaEvolve's evaluation-driven evolution loop validates the importance of automated, rigorous evaluation (clau-doom's DOE framework) in LLM evolutionary systems.

- **Differentiation**: AlphaEvolve focuses on code optimization for well-defined computational problems with clear metrics; clau-doom operates in a stochastic multi-agent game environment with multi-objective evaluation. AlphaEvolve uses Google's Gemini models; clau-doom uses Claude models. AlphaEvolve evolves code; clau-doom evolves declarative strategy documents that are interpreted by a Rust scoring engine.

- **Reference type**: Background reference (industrial-scale validation)

---

### B6. EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms (Yuan et al., 2024, NAACL 2025)

> **Cross-ref**: Also mentioned briefly in LITERATURE_REVIEW.md section 2.3. This entry provides full academic analysis with clau-doom-specific differentiation.

- **Full citation**: Yuan, S. et al. (2024). EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms. NAACL 2025.
- **Link**: https://arxiv.org/abs/2406.14228

- **Core contribution**: Proposes a generic method to automatically extend specialized LLM agents into multi-agent systems through evolutionary algorithms. EvoAgent applies crossover, mutation, and selection operators to agent configurations, generating diverse agents with specialized skills. The method is framework-agnostic and consistently improves performance across knowledge QA, multi-modal reasoning, interactive scientific problem-solving, and real-world planning tasks.

- **clau-doom relevance**: EvoAgent is the most directly comparable work to clau-doom's agent evolution mechanism. Both systems evolve agent configurations (EvoAgent: LLM agent settings; clau-doom: MD strategy documents) using evolutionary operators (crossover, mutation, selection). Both aim to generate diverse specialized agents from initial templates. The key parallel is using evolution to create a population of agents with different strengths rather than optimizing a single agent.

- **Differentiation**: EvoAgent evolves LLM agent configurations for NLP tasks and relies on real-time LLM inference; clau-doom evolves strategy documents for game agents with no real-time LLM calls (< 100ms decision latency via Rust scoring). EvoAgent operates in a single-generation context (no persistent knowledge accumulation); clau-doom maintains cross-generational knowledge through RAG, enabling cumulative improvement across generations.

- **Reference type**: Direct citation (closest work in agent evolution)

---

## Category C: Multi-Agent Cooperation/Competition Learning

**Why needed**: clau-doom uses NATS pub/sub for inter-agent knowledge sharing and natural selection across generations. Comparison with established MARL cooperation/competition mechanisms provides theoretical grounding.

---

### C1. Emergent Tool Use From Multi-Agent Autocurricula (Baker et al., 2019, ICLR 2020)

- **Full citation**: Baker, B. et al. (2019). Emergent Tool Use From Multi-Agent Autocurricula. ICLR 2020.
- **Link**: https://arxiv.org/abs/1909.07528

- **Core contribution**: Demonstrates that multi-agent competition in a hide-and-seek environment produces emergent tool use, cooperation, and increasingly sophisticated strategies through an autocurriculum. Agents progress through six distinct strategic phases, each building on previous discoveries: from basic chasing to shelter construction, ramp usage, ramp locking, and box surfing. All emergent behaviors arise purely from competition pressure without explicit incentives for tool use or exploration.

- **clau-doom relevance**: Baker et al.'s autocurriculum concept validates clau-doom's design where competitive pressure drives strategic improvement. In clau-doom, agents that accumulate better strategy documents through RAG naturally create competitive pressure for others to improve. The phase-based emergence pattern (increasingly sophisticated strategies over time) is exactly what clau-doom's generational evolution aims to produce, with the addition of explicit knowledge transfer through NATS rather than purely implicit learning through competition.

- **Differentiation**: Baker et al. use standard MARL with shared reward signals and gradient-based learning; clau-doom uses document-based knowledge transfer (no gradient sharing) and DOE-evaluated evolution. The key difference is that clau-doom's agents share explicit knowledge (strategy documents) rather than learning implicitly through interaction, enabling faster knowledge transfer but potentially reducing the diversity of emergent strategies.

- **Reference type**: Direct citation (emergence through competition)

---

### C2. Population Based Training of Neural Networks (Jaderberg et al., 2017, arXiv)

- **Full citation**: Jaderberg, M., Dalibard, V., Czarnecki, W. M. et al. (2017). Population Based Training of Neural Networks. arXiv:1711.09846.
- **Link**: https://arxiv.org/abs/1711.09846

- **Core contribution**: Proposes Population Based Training (PBT), an asynchronous optimization algorithm that jointly optimizes a population of models and their hyperparameters. PBT discovers hyperparameter schedules rather than fixed settings, using "exploit" (copy weights from better-performing members) and "explore" (perturb hyperparameters) operations. The approach bridges random search and hand-tuning, achieving strong results across machine translation, GANs, and RL tasks including Atari and StarCraft.

- **clau-doom relevance**: PBT's population-level optimization with exploit/explore dynamics is directly analogous to clau-doom's generational evolution. The "exploit" operation (copying successful configurations) maps to clau-doom's elite preservation and strategy document sharing via NATS. The "explore" operation (perturbing hyperparameters) maps to clau-doom's LLM-mediated mutation of MD files. PBT's key insight, that hyperparameter schedules outperform fixed settings, suggests that clau-doom's strategy documents should evolve over time rather than being fixed, which is exactly what the generational evolution mechanism achieves.

- **Differentiation**: PBT operates on continuous hyperparameters with gradient-based model training; clau-doom operates on discrete text-based strategy documents without gradient computation. PBT's exploit operation copies neural network weights directly; clau-doom's knowledge transfer operates through document-level abstraction, which is more interpretable but potentially loses fine-grained information. PBT requires running multiple training jobs simultaneously; clau-doom's evaluation is through game episodes, which are cheaper but noisier.

- **Reference type**: Direct citation (population-level optimization)

---

### C3. Multi-Agent Reinforcement Learning Survey: Knowledge Sharing and Transfer (Various, 2024)

- **Full citation**: Multiple survey papers, including: Du, W. et al. (2024). A Survey on Multi-Agent Reinforcement Learning. arXiv:2312.10256.
- **Link**: https://arxiv.org/abs/2312.10256

- **Core contribution**: Recent MARL surveys identify several knowledge sharing paradigms: (1) Policy distillation, where a teacher agent's policy is compressed into a student agent. (2) Centralized training with decentralized execution (CTDE), where agents share information during training but act independently. (3) Communication channels, where agents exchange messages during execution. (4) Population-based methods, where agent populations evolve through selection pressure. The Double Distillation Network (DDN) introduces external distillation (global-to-local knowledge transfer) and internal distillation (intrinsic reward for exploration).

- **clau-doom relevance**: clau-doom's knowledge sharing architecture maps to multiple MARL paradigms: NATS pub/sub messaging implements explicit communication channels; the OpenSearch strategy repository acts as a shared knowledge base (analogous to centralized knowledge in CTDE); generational evolution implements population-based selection. The Centralized Reward Agent (CRA) concept, which distills knowledge from various tasks and distributes via shaped rewards, is similar to clau-doom's approach of curating strategy documents that encode cross-agent knowledge.

- **Differentiation**: Traditional MARL knowledge sharing operates on neural network parameters or reward signals; clau-doom shares knowledge through human-readable strategy documents. This makes clau-doom's knowledge transfer interpretable and auditable, at the cost of potentially losing sub-symbolic patterns that neural transfer captures. clau-doom's DOE-based evaluation provides statistical rigor not found in typical MARL evaluation frameworks.

- **Reference type**: Background reference (literature positioning)

---

## Gap Analysis: What clau-doom Does Differently

### 1. Text-Based Genomes (MD Files) vs. Numerical Parameters

All existing QD and LLM-evolution systems operate on either continuous parameter vectors or code. clau-doom uniquely evolves Markdown strategy documents that serve dual purposes: (a) genomes for evolutionary operators, and (b) retrievable knowledge for real-time decision-making via RAG. No prior work combines these two roles in a single artifact.

### 2. RAG-Integrated Evolution

Existing LLM evolution systems (EvoPrompting, FunSearch, ELM, AlphaEvolve) use LLMs purely as variation operators. clau-doom additionally uses the accumulated strategy documents as a RAG knowledge base, creating a feedback loop where evolutionary improvement directly improves online decision-making without model retraining. This RAG-evolution coupling is novel.

### 3. DOE-Based Statistical Evaluation

While LLM evolution papers use simple fitness metrics (accuracy, reward), clau-doom applies formal Design of Experiments methodology (ANOVA, factorial designs, response surface methods) to evaluate agent performance. This provides statistical guarantees (p-values, confidence intervals, effect sizes) absent from prior work, making claims about improvement more rigorous.

### 4. No Real-Time LLM Dependency

Unlike EvoAgent and other LLM-agent systems that require real-time LLM inference, clau-doom's agents make decisions in < 100ms using a Rust scoring engine and OpenSearch kNN lookup. The LLM is used only offline for evolution, retrospection, and analysis. This architectural choice enables deployment in latency-critical environments.

### 5. Multi-Objective Quality-Diversity

clau-doom combines QD-inspired diversity maintenance with TOPSIS/AHP multi-criteria decision making for generation selection. While individual components exist in prior work (MAP-Elites for diversity, TOPSIS for MCDM), their integration within an LLM-driven text evolution system is novel.

### 6. Explicit Knowledge Accumulation via NATS

Where PBT and MARL systems transfer knowledge implicitly (weight copying, reward shaping), clau-doom transfers knowledge explicitly through NATS-published strategy documents. This makes the knowledge transfer process transparent, auditable, and amenable to human intervention, aligning with the project's quality engineering philosophy.

---

## Completion Checklist

- [x] Category A: 5 papers collected (MAP-Elites, Cully robots, DQD, LLMatic, QDAIF)
- [x] Category B: 6 papers collected (EvoPrompting, ELM, FunSearch, LMX, AlphaEvolve, EvoAgent)
- [x] Category C: 3 papers collected (Baker hide-and-seek, PBT, MARL survey)
- [x] clau-doom relevance documented for each paper
- [x] Gap analysis identifying novel contributions
- [x] Lead review complete
