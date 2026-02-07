# clau-doom Literature Review

> Project: LLM-based Multi-Agent Evolutionary Doom Player
> Purpose: Establish theoretical foundations and position contributions
> Last Updated: 2026-02-07

---

**Total Papers**: 54 core references + 4 comprehensive surveys

---

## 1. Core References (Direct Precedents)

### 1.1 LLM + FPS Games

#### Will GPT-4 Run DOOM?

- **Authors**: Adrian de Wynter
- **Venue**: IEEE Transactions on Games, 2024; arXiv:2403.05468
- **Link**: https://arxiv.org/abs/2403.05468

**Core Contribution**: First study of GPT-4 playing Doom's E1M1 using only screenshots converted to text descriptions. Tests four prompting strategies (Naive, Walkthrough, Plan, K-Levels reasoning). Each strategy tested 10 times without intervention. Zero completion rate across all strategies despite reaching later rooms. Inference latency approximately 60 seconds per frame.

**Relevance to clau-doom**: Most direct prior work in the domain. Demonstrates that real-time LLM inference is impractical for FPS gameplay (60s/frame vs. required <100ms). Highlights need for structured knowledge retrieval rather than zero-shot LLM reasoning. clau-doom's design explicitly addresses these limitations: no real-time LLM calls, RAG-based strategy retrieval with <100ms decision latency, and accumulated knowledge through retrospection rather than zero-shot prompting.

---

### 1.2 Verbal Reinforcement / Episodic Learning

#### Reflexion: Language Agents with Verbal Reinforcement Learning

- **Authors**: Shinn et al.
- **Venue**: NeurIPS 2023; arXiv:2303.11366
- **Link**: https://arxiv.org/abs/2303.11366

**Core Contribution**: Introduces agents that learn through language-based self-reflection without weight updates. Three-module architecture: Actor (generates actions), Evaluator (assesses outcomes), Self-Reflection (generates verbal feedback). Reflexion agents store reflections in episodic memory and condition future behavior on past insights, achieving significant improvements across decision-making, coding, and reasoning tasks.

**Relevance to clau-doom**: Foundational theoretical basis for "episodic retrospection → knowledge update" pattern. clau-doom extends this from single-agent self-reflection to multi-agent generational evolution: where Reflexion maintains an episodic memory buffer per agent, clau-doom maintains a shared OpenSearch strategy repository with cross-generational knowledge accumulation and trust scoring.

---

### 1.3 Skill Libraries / Lifelong Learning

#### Voyager: An Open-Ended Embodied Agent with Large Language Models

- **Authors**: Wang et al.
- **Venue**: TMLR 2023; arXiv:2305.16291
- **Link**: https://arxiv.org/abs/2305.16291

**Core Contribution**: First LLM-powered embodied lifelong learning agent in Minecraft. Three key components: automatic curriculum for exploration, growing skill library of executable code, and iterative prompting with environment feedback. Voyager obtains 3.3x more unique items, travels 2.3x longer distances, and unlocks tech tree milestones 15.3x faster than prior SOTA.

**Relevance to clau-doom**: Voyager's skill library is structurally analogous to clau-doom's OpenSearch strategy repository. Both accumulate reusable behavioral knowledge without catastrophic forgetting. Key differences: Voyager stores executable code and uses real-time GPT-4 inference; clau-doom stores declarative strategy documents (Markdown) and eliminates real-time LLM dependency through RAG + Rust scoring (<100ms). Voyager operates single-agent; clau-doom uses multi-agent knowledge sharing via NATS.

---

### 1.4 LLM + RL Hierarchical Separation

#### RL-GPT: Integrating Reinforcement Learning and Code-as-policy

- **Authors**: Liu et al.
- **Venue**: NeurIPS 2024 Oral; arXiv:2402.19299
- **Link**: https://neurips.cc/virtual/2024/oral/97985

**Core Contribution**: Two-level hierarchical framework where high-level planning uses LLM code generation (slow agent) and low-level execution uses traditional RL (fast agent). The LLM generates reward functions and behavior abstractions as code, which the RL agent optimizes. Achieves strong results on Meta-World manipulation tasks.

**Relevance to clau-doom**: RL-GPT's slow/fast decomposition parallels clau-doom's decision hierarchy (offline LLM retrospection/evolution vs. online Rust scoring). Structural similarity validates the "LLM for high-level reasoning, fast engine for real-time decisions" architecture. Key difference: RL-GPT uses traditional RL for low-level control; clau-doom replaces RL entirely with RAG-based decision making, testing the hypothesis that retrieval can substitute for learned policies in constrained domains.

---

### 1.5 Agent Self-Evolution

#### Agent-Pro: Learning to Evolve via Policy-Level Reflection

- **Authors**: Zhang et al.
- **Venue**: ACL 2024; arXiv:2402.17574
- **Link**: https://aclanthology.org/2024.acl-long.292/

**Core Contribution**: Agents that self-evolve through policy-level reflection and optimization. Generates beliefs about tasks, reflects on belief quality, and uses depth-first search to optimize policies. Demonstrates emergent capabilities including skill composition, performance improvement through iteration, and effective zero-shot transfer.

**Relevance to clau-doom**: Agent-Pro's policy-level reflection directly parallels clau-doom's generational strategy evolution. Where Agent-Pro evolves abstract policies through DFS, clau-doom evolves concrete strategy documents through LLM-mediated crossover/mutation within a DOE-guided evolutionary framework. Both enable cumulative improvement without traditional RL training.

---

#### S-Agents: Self-Organizing Agents in Open-Ended Environments

- **Authors**: Chen et al.
- **Venue**: ICLR 2024 Workshop; arXiv:2402.04578
- **Link**: https://github.com/fudan-zvg/S-Agents

**Core Contribution**: Framework for multi-agent self-organization in Minecraft. Features tree-of-agents architecture, hourglass organizational structure (hierarchy formation and dissolution), and non-obstructive collaboration mechanisms. Demonstrates emergent specialization and coordination without centralized control.

**Relevance to clau-doom**: S-Agents' self-organization patterns inform clau-doom's NATS-based knowledge sharing architecture. While S-Agents use emergent hierarchy, clau-doom uses flat broadcast with selective document retrieval. Both enable agent specialization through differentiated experience accumulation.

---

## 2. Quality-Diversity and Evolutionary AI

### 2.1 MAP-Elites: Illuminating Search Spaces

#### Illuminating Search Spaces by Mapping Elites

- **Authors**: Mouret, J.-B. & Clune, J.
- **Venue**: arXiv:1504.04909 (2015)
- **Link**: https://arxiv.org/abs/1504.04909

**Core Contribution**: Introduces MAP-Elites, a quality-diversity algorithm that maintains a multi-dimensional archive of high-performing solutions organized by behavioral dimensions. Instead of converging to a single optimum, MAP-Elites fills a grid where each cell stores the best solution for that behavioral characteristic combination. Uses random variation (mutation/crossover) to generate candidates that replace existing entries only if they achieve higher fitness in the same cell.

**Relevance to clau-doom**: MAP-Elites' archive mechanism directly informs clau-doom's generational evolution design. Each agent's MD file represents a "genome," with behavioral dimensions defined by strategy characteristics (aggression level, exploration tendency). Provides principled way to maintain strategic diversity across populations while preserving high-performing configurations, preventing premature convergence to a single dominant playstyle.

---

### 2.2 EvoPrompting: Language Models for Code-Level NAS

#### EvoPrompting: Language Models for Code-Level Neural Architecture Search

- **Authors**: Chen, A., Dohan, D. & So, D.
- **Venue**: NeurIPS 2023; arXiv:2302.14838
- **Link**: https://arxiv.org/abs/2302.14838

**Core Contribution**: Uses LLMs as adaptive mutation and crossover operators for evolutionary neural architecture search. Combines evolutionary prompt engineering with soft prompt-tuning, achieving SOTA results on MNIST-1D and CLRS Algorithmic Reasoning Benchmark. Demonstrates LLMs can serve as intelligent variation operators that understand domain semantics.

**Relevance to clau-doom**: EvoPrompting's "LLM as crossover/mutation operator" paradigm directly parallels clau-doom's approach. When clau-doom presents parent strategy documents to an LLM for offspring generation, it performs exactly the EvoPrompting operation. Key validation: LLM-mediated evolution produces meaningfully diverse offspring rather than degenerate copies, critical for clau-doom's strategy evolution.

---

### 2.3 FunSearch: Mathematical Discoveries from Program Search

#### Mathematical Discoveries from Program Search with Large Language Models

- **Authors**: Romera-Paredes, B. et al. (Google DeepMind)
- **Venue**: Nature 625, 468-475 (2024)
- **Link**: https://www.nature.com/articles/s41586-023-06924-6

**Core Contribution**: Pairs pretrained LLM with systematic evaluator in evolutionary loop to discover new mathematical constructions. Searches in program space rather than solution space, making discoveries interpretable and deployable. Discovered constructions surpassing previously best-known results in cap set problem (extremal combinatorics) and novel bin packing heuristics improving on widely-used baselines.

**Relevance to clau-doom**: FunSearch's key insight—searching in program space with automated evaluation produces better results than searching solution space—validates clau-doom's approach of evolving strategy documents (analogous to programs) rather than optimizing numerical parameters directly. The interpretability advantage (discovered programs can be understood/modified by humans) parallels clau-doom's human-readable MD documents.

---

### 2.4 AlphaEvolve: A Coding Agent for Scientific Discovery

#### AlphaEvolve: A Coding Agent for Scientific and Algorithmic Discovery

- **Authors**: Google DeepMind
- **Venue**: arXiv:2506.13131 (2025)
- **Link**: https://arxiv.org/abs/2506.13131

**Core Contribution**: Evolutionary coding agent powered by Gemini LLMs for general-purpose algorithm discovery. Pairs LLM creative problem-solving with automated evaluators using evolutionary framework to refine promising ideas. Uses ensemble approach: Gemini Flash for breadth, Gemini Pro for depth. Achievements include first improvement to Strassen's matrix multiplication in 56 years, 0.7% recovery of Google's worldwide compute resources, and 23-32% speedups in AI training kernels.

**Relevance to clau-doom**: Demonstrates scalability and practical impact of LLM-driven evolution at industrial scale. Ensemble approach (fast model for exploration, strong model for exploitation) directly informs clau-doom's model selection strategy: Haiku/Sonnet for rapid mutation, Opus for complex strategic reasoning. Evaluation-driven loop validates importance of automated, rigorous evaluation (clau-doom's DOE framework).

---

### 2.5 EvoAgent: Automatic Multi-Agent Generation

#### EvoAgent: Towards Automatic Multi-Agent Generation via Evolutionary Algorithms

- **Authors**: Yuan, S. et al.
- **Venue**: NAACL 2025; arXiv:2406.14228
- **Link**: https://arxiv.org/abs/2406.14228

**Core Contribution**: Generic method to automatically extend specialized LLM agents into multi-agent systems through evolutionary algorithms. Applies crossover, mutation, and selection to agent configurations, generating diverse agents with specialized skills. Framework-agnostic, consistently improves performance across knowledge QA, multi-modal reasoning, scientific problem-solving, and real-world planning tasks.

**Relevance to clau-doom**: Most directly comparable work to clau-doom's agent evolution mechanism. Both evolve agent configurations (EvoAgent: LLM settings; clau-doom: MD strategy documents) using evolutionary operators (crossover, mutation, selection). Both aim to generate diverse specialized agents from initial templates. Key difference: EvoAgent operates single-generation with real-time LLM inference; clau-doom maintains cross-generational knowledge accumulation through RAG with no real-time LLM dependency.

---

### 2.6 Neuroevolution Foundations

#### Evolving Neural Networks through Augmenting Topologies (NEAT)

- **Authors**: Stanley, K.O. & Miikkulainen, R.
- **Venue**: Evolutionary Computation 10(2), 99-127 (2002)
- **Link**: https://doi.org/10.1162/106365602320169811

**Core Contribution**: Introduces NeuroEvolution of Augmenting Topologies, which evolves both the topology and weights of neural networks simultaneously through complexification. Key innovations include historical markings for meaningful crossover between different topologies, speciation to protect structural innovations, and starting from minimal structures that grow incrementally.

**Relevance to clau-doom**: NEAT established that evolving structure (not just parameters) produces superior results -- a principle clau-doom extends from neural network topology to strategy document structure. Where NEAT evolves network graphs, clau-doom evolves Markdown strategy documents through LLM-mediated crossover and mutation, both enabling open-ended complexification of agent behavior.

---

#### Evolution Strategies as a Scalable Alternative to Reinforcement Learning

- **Authors**: Salimans, T. et al. (OpenAI)
- **Venue**: arXiv:1703.03864 (2017)
- **Link**: https://arxiv.org/abs/1703.03864

**Core Contribution**: Demonstrates that Evolution Strategies (ES) can match or exceed the performance of standard RL algorithms (A3C, TRPO) on MuJoCo and Atari benchmarks while offering superior parallelization -- training a 3D humanoid walker in 10 minutes on 1,440 CPUs. ES requires no value function, no temporal credit assignment, and scales linearly with available compute.

**Relevance to clau-doom**: Validates evolutionary approaches as viable alternatives to gradient-based RL for complex control tasks. ES's advantage in parallelization and simplicity parallels clau-doom's evolutionary pipeline design. Key difference: ES evolves numerical parameter vectors; clau-doom evolves text-based strategy documents via LLM operators, enabling richer behavioral representation and human interpretability.

---

## 3. Retrieval-Augmented Decision Making

### 3.1 Episodic Control

#### Model-Free Episodic Control

- **Authors**: Blundell, C. et al.
- **Venue**: ICML Workshop 2016; arXiv:1606.04460
- **Link**: https://arxiv.org/abs/1606.04460

**Core Contribution**: Non-parametric model storing highest Q-values observed for state-action pairs in tabular memory, using k-nearest-neighbor (kNN) lookup for action selection. At decision time, finds k closest states in memory for each available action and selects action with highest estimated return. Achieves significantly faster initial learning than deep RL baselines on Atari by directly replaying successful experiences rather than slowly updating neural network parameters.

**Relevance to clau-doom**: Most direct conceptual ancestor of clau-doom's decision architecture. OpenSearch kNN search for strategy documents is structurally identical to MFEC's kNN lookup for Q-values. Both bypass learned policy functions entirely, using nearest-neighbor retrieval over memory of past experiences for action selection. MFEC stores (state, action, return) tuples; clau-doom stores (situation_embedding, strategy_document, success_rate) tuples.

---

#### Neural Episodic Control

- **Authors**: Pritzel, A. et al.
- **Venue**: ICML 2017; arXiv:1703.01988
- **Link**: https://arxiv.org/abs/1703.01988

**Core Contribution**: Extends MFEC by replacing raw state representations with learned embeddings from CNN and replacing Q-table with Differentiable Neural Dictionaries (DNDs). DNDs enable end-to-end training of embedding function through backpropagation. NEC dramatically outperforms all other algorithms in low-data regime (<20 million frames), with advantage especially pronounced before 5 million frames.

**Relevance to clau-doom**: NEC's architecture directly maps to clau-doom: (1) learned embeddings for state representation = Ollama-generated embeddings for game situations; (2) DND key-value store = OpenSearch vector index; (3) kNN lookup for action selection = kNN strategy retrieval. NEC's superior data efficiency in low-data regime is especially relevant because clau-doom operates with limited gameplay episodes per generation.

---

### 3.2 Retrieval-Augmented RL

#### Retrieval-Augmented Reinforcement Learning

- **Authors**: Goyal, A. et al.
- **Venue**: ICML 2022; arXiv:2202.08417
- **Link**: https://arxiv.org/abs/2202.08417

**Core Contribution**: Augments RL agents with trainable retrieval process (parameterized as neural network) having direct access to dataset of experiences. Retrieval module learns to identify which past experiences are useful for current context, using case-based reasoning. Integrated into both offline DQN and online R2D2 agents, retrieval-augmented DQN avoids task interference and learns faster, while retrieval-augmented R2D2 significantly outperforms baseline R2D2 on Atari.

**Relevance to clau-doom**: Closest existing work to clau-doom's retrieval-based decision architecture. Both retrieve relevant past experiences to inform current decisions. Key difference: Goyal et al. use retrieval to augment an existing RL policy (retrieval complements learned behavior); clau-doom uses retrieval as primary decision mechanism (retrieval replaces learned behavior). This is fundamental architectural difference: augmentation vs. substitution.

---

### 3.3 Decision Transformer: RL via Sequence Modeling

#### Decision Transformer: Reinforcement Learning via Sequence Modeling

- **Authors**: Chen, L. et al.
- **Venue**: NeurIPS 2021; arXiv:2106.01345
- **Link**: https://arxiv.org/abs/2106.01345

**Core Contribution**: Casts RL as conditional sequence modeling, where causal Transformer autoregressively predicts actions conditioned on desired return, past states, and past actions. Unlike value function fitting or policy gradient methods, Decision Transformer simply generates actions that achieve desired return. Matches or exceeds SOTA model-free offline RL baselines on Atari, OpenAI Gym, and Key-to-Door tasks.

**Relevance to clau-doom**: DT's core insight—conditioning on desired outcomes enables effective decision-making without explicit value function learning—parallels clau-doom's approach. In clau-doom, strategy documents encode "if situation X, do action Y to achieve outcome Z," a retrieval-based form of return-conditioned action generation. DT conditions on desired return-to-go; clau-doom conditions on strategy document trust scores and success rates. Both bypass traditional RL value/policy learning.

---

### 3.4 Retrieval-Augmented Generation (RAG)

#### Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks

- **Authors**: Lewis, P. et al.
- **Venue**: NeurIPS 2020; arXiv:2005.11401
- **Link**: https://arxiv.org/abs/2005.11401

**Core Contribution**: Introduces Retrieval-Augmented Generation (RAG), combining pretrained seq2seq model (parametric memory) with dense vector index of Wikipedia (non-parametric memory) accessed through pretrained neural retriever. RAG models set SOTA on three open-domain QA tasks and generate more specific, diverse, and factual language than parametric-only baselines. Key insight: external retrieval provides scalable, updatable knowledge source complementing learned parametric knowledge.

**Relevance to clau-doom**: Establishes foundational paradigm that clau-doom extends from text generation to action generation. clau-doom's architecture maps directly: (1) OpenSearch strategy documents = non-parametric memory (Wikipedia in RAG); (2) Rust scoring engine = parametric decision logic (seq2seq in RAG); (3) Ollama embeddings + kNN = neural retriever (DPR in RAG). Fundamental innovation: applying RAG's retrieval-then-generate pattern to retrieval-then-decide, extending paradigm from NLP to real-time game decision-making.

---

### 3.5 Retrieval at Scale

#### Improving Language Models by Retrieving from Trillions of Tokens (RETRO)

- **Authors**: Borgeaud, S. et al. (DeepMind)
- **Venue**: ICML 2022; arXiv:2112.04426
- **Link**: https://arxiv.org/abs/2112.04426

**Core Contribution**: Demonstrates that retrieval from a massive external database (2 trillion tokens) can substitute for model capacity, achieving comparable performance to 25x larger models. RETRO uses chunked cross-attention to condition generation on retrieved neighbors, showing that retrieval provides a more compute-efficient path to knowledge than scaling parameters alone.

**Relevance to clau-doom**: RETRO's central finding -- that retrieval can substitute for model capacity -- provides theoretical support for clau-doom's "retrieval replaces RL" paradigm. If retrieval can substitute for 25x more parameters in language modeling, the analogous hypothesis that retrieval can substitute for learned RL policies in constrained game domains becomes more plausible. clau-doom's OpenSearch strategy retrieval operationalizes this principle for real-time decision making.

---

### 3.6 Nearest Neighbor Language Models

#### Generalization through Memorization: Nearest Neighbor Language Models (kNN-LM)

- **Authors**: Khandelwal, U., Levy, O., Jurafsky, D., Zettlemoyer, L., Lewis, M.
- **Venue**: ICLR 2020; arXiv:1911.00172
- **Link**: https://arxiv.org/abs/1911.00172

**Core Contribution**: Augments a pretrained language model with a nearest neighbor retrieval mechanism over a cached datastore of context-target pairs. At inference time, the model interpolates between its parametric next-token distribution and a kNN distribution computed over retrieved neighbors. Without any additional training, kNN-LM achieves significant perplexity improvements, demonstrating that explicit memorization via retrieval complements parametric generalization.

**Relevance to clau-doom**: kNN-LM provides direct theoretical support for clau-doom's kNN retrieval architecture. Both systems interpolate between a parametric component (LM parameters / Rust scoring weights) and a non-parametric retrieval component (cached datastore / OpenSearch strategy documents) using nearest neighbor lookup. kNN-LM's finding that retrieval improves generalization without retraining validates clau-doom's approach of improving agent behavior through strategy document accumulation rather than policy gradient updates.

---

### 3.7 Knowledge Distillation

#### Distilling the Knowledge in a Neural Network

- **Authors**: Hinton, G., Vinyals, O., Dean, J.
- **Venue**: NeurIPS Workshop on Deep Learning (2015); arXiv:1503.02531
- **Link**: https://arxiv.org/abs/1503.02531

**Core Contribution**: Introduces knowledge distillation, where a smaller "student" network is trained to mimic the soft output distributions of a larger "teacher" network. The soft targets carry richer information than hard labels (encoding inter-class similarities), enabling effective knowledge transfer with significant model compression.

**Relevance to clau-doom**: Knowledge distillation's teacher-student paradigm is conceptually analogous to clau-doom's cross-agent knowledge transfer mechanism. In clau-doom, high-performing agents' strategy documents (teacher knowledge) are shared via NATS pub/sub and ingested by other agents through OpenSearch retrieval (student learning), enabling knowledge transfer without direct parameter sharing or gradient updates.

---

## 4. LLM-as-Scientist and Automated Research

### 4.1 The AI Scientist: Fully Automated Scientific Discovery

#### The AI Scientist: Towards Fully Automated Open-Ended Scientific Discovery

- **Authors**: Lu, C. et al. (Sakana AI / Oxford / UBC)
- **Venue**: arXiv:2408.06292 (2024)
- **Link**: https://arxiv.org/abs/2408.06292

**Core Contribution**: First comprehensive framework for fully automated scientific discovery. Given research direction, system autonomously generates novel research ideas, writes and executes code, visualizes results, writes full scientific paper, and runs simulated peer review. End-to-end pipeline demonstrated on ML sub-fields including diffusion models, language modeling, and learning dynamics. Cost approximately $15 per paper generated.

**Relevance to clau-doom**: Both automate hypothesis → experiment → analysis loop. Key differences: AI Scientist generates single papers per run; clau-doom's PI accumulates knowledge across generations with trust scores. AI Scientist uses monolithic single-model pipeline; clau-doom separates PI (designs experiments) from executors (run experiments) and analysts (statistical analysis). AI Scientist uses informal evaluation; clau-doom enforces DOE, ANOVA, residual diagnostics, and trust scoring.

---

#### The AI Scientist-v2: Workshop-Level Automated Scientific Discovery

- **Authors**: Lu, C. et al. (Sakana AI)
- **Venue**: arXiv:2504.08066 (2025), ICLR 2025 Workshop
- **Link**: https://arxiv.org/abs/2504.08066

**Core Contribution**: Removes reliance on human-authored code templates, introduces experiment manager agent with novel agentic tree-search algorithm for deeper research exploration. Produced first entirely AI-generated paper accepted through peer review at workshop level (ICLR 2025 Workshop "I Can't Believe It's Not Better").

**Relevance to clau-doom**: v2's experiment manager agent parallels clau-doom's orchestrator pattern. Tree search over research directions conceptually similar to clau-doom's hypothesis backlog with priority ordering. Key difference: v2 explores breadth of ML topics; clau-doom explores depth in single domain (game AI) with systematic DOE phase progression. v2 evaluates by peer review acceptance; clau-doom evaluates by quantitative game performance with statistical significance tests.

---

### 4.2 Autonomous Chemical Research (Coscientist)

#### Autonomous Chemical Research with Large Language Models

- **Authors**: Boiko, D.A., MacKnight, R., Kline, B., Gomes, G.
- **Venue**: Nature 624, 570-578 (2023)
- **Link**: https://www.nature.com/articles/s41586-023-06792-0

**Core Contribution**: Demonstrates an LLM-powered system (Coscientist) capable of autonomously designing, planning, and executing chemical experiments. Uses GPT-4 to reason about experimental procedures, search literature, execute code, and operate robotic lab equipment. Successfully planned and executed palladium-catalyzed cross-coupling reactions autonomously, including Suzuki and Sonogashira reactions, with correct reagent selection and procedure optimization.

**Relevance to clau-doom**: Coscientist is the closest parallel to clau-doom's domain-specific PI approach: both use LLMs as autonomous experimental designers within a specific domain (chemistry vs. game AI). Key differences: Coscientist operates without formal DOE methodology (ad-hoc experimental iteration vs. factorial/RSM designs), without statistical validation (no ANOVA, no confidence intervals), and without multi-generational knowledge accumulation. clau-doom extends the "LLM as scientist" paradigm with formal experimental methodology and cumulative learning.

---

### 4.3 AI-Driven Autonomous Scientific Research (data-to-paper)

#### data-to-paper: AI-driven Autonomous Research, from Data to Human-Verifiable Research Papers

- **Authors**: Ifargan, T., Hafner, L., Kern, M., Alcalay, R., Kishony, R.
- **Venue**: arXiv:2404.17605 (2024)
- **Link**: https://arxiv.org/abs/2404.17605

**Core Contribution**: Framework for autonomous scientific research that takes raw data as input and produces complete, human-verifiable research papers. Enforces a structured pipeline mimicking traditional scientific workflow: data exploration, hypothesis generation, statistical analysis, and paper writing, with human-verifiable intermediate outputs at each stage.

**Relevance to clau-doom**: data-to-paper's emphasis on structured, verifiable scientific pipeline parallels clau-doom's audit trail requirements (hypothesis → experiment order → report → findings). Both prioritize reproducibility and human verifiability over end-to-end automation. Key difference: data-to-paper operates on existing datasets; clau-doom's PI actively designs and executes new experiments using formal DOE methodology.

---

### 4.4 FunSearch (Cross-Reference)

See Section 2.3 for full details. FunSearch demonstrates that LLM-driven evolutionary search with automated evaluation can discover novel mathematical constructions, validating clau-doom's evolutionary approach with DOE-based evaluation.

---

### 4.5 AgentHPO: LLM Agent for Hyperparameter Optimization

#### AgentHPO: Large Language Model Agent for Hyper-Parameter Optimization

- **Authors**: Liu, S., Gao, C., Li, Y.
- **Venue**: arXiv:2402.01881 (2024)
- **Link**: https://arxiv.org/abs/2402.01881

**Core Contribution**: LLM-based agent system for hyperparameter optimization using two specialized agents: Creator (generates initial hyperparameters from natural language task descriptions) and Executor (runs experiments and iteratively refines parameters based on historical trials). At T=10 trials, AgentHPO (GPT-3.5) outperforms random search by 2.65% and Bayesian optimization by 1.39% on 12 ML benchmarks.

**Relevance to clau-doom**: AgentHPO's Creator/Executor pattern directly parallels clau-doom's PI/DOE-runner separation. Both iterate based on historical trial performance. Key differences: AgentHPO optimizes ML hyperparameters with informal iteration; clau-doom optimizes game agent behavior parameters using formal DOE methodology (factorial/RSM designs with ANOVA validation). AgentHPO has no multi-generational evolution concept; clau-doom accumulates knowledge across generations.

---

## 5. DOE and Quality Engineering Methodology

### 5.1 Design of Experiments Foundations

#### Design and Analysis of Experiments

- **Authors**: Montgomery, D.C.
- **Publisher**: Wiley, 10th edition (2017)
- **ISBN**: 978-1119113478

**Core Contribution**: The standard textbook on Design of Experiments, covering full factorial designs, fractional factorials, response surface methodology, and split-plot designs. Provides complete ANOVA theory, effect estimation, and model adequacy checking procedures used across engineering and science for over four decades.

**Relevance to clau-doom**: Foundation for clau-doom's entire DOE phase progression (OFAT to Factorial to RSM). Montgomery's ANOVA decomposition, residual diagnostics, and center point curvature testing are implemented directly in clau-doom's research-analyst pipeline. The factorial and CCD design matrices used in EXPERIMENT_ORDER documents follow Montgomery's standard construction methods.

---

#### Statistics for Experimenters

- **Authors**: Box, G.E.P., Hunter, J.S., Hunter, W.G.
- **Publisher**: Wiley, 2nd edition (2005)
- **ISBN**: 978-0471718130

**Core Contribution**: Comprehensive treatment of Response Surface Methodology (RSM), sequential experimentation philosophy, and the iterative nature of experimental investigation. Introduces the concept of sequential assembly of designs and the importance of blocking and randomization in industrial contexts.

**Relevance to clau-doom**: Box et al.'s sequential experimentation philosophy directly informs clau-doom's DOE phase progression: screen factors first (fractional factorial), then model curvature (augment to CCD), then optimize (RSM). The emphasis on practical rather than statistical significance aligns with clau-doom's trust scoring framework, which requires both p-value thresholds and effect size criteria.

---

#### Response Surface Methodology

- **Authors**: Myers, R.H., Montgomery, D.C., Anderson-Cook, C.M.
- **Publisher**: Wiley, 4th edition (2016)
- **ISBN**: 978-1118916018

**Core Contribution**: Definitive reference on RSM theory and practice, covering Central Composite Designs (CCD), Box-Behnken Designs (BBD), optimal designs, and multi-response optimization. Provides detailed guidance on rotatability, orthogonality, and design augmentation strategies.

**Relevance to clau-doom**: CCD and BBD construction methods from this text are used in clau-doom's Phase 2 (RSM) experimental designs. The multi-response optimization techniques inform TOPSIS-based multi-criteria evaluation of agents. Design augmentation strategies guide clau-doom's phase transitions when curvature tests indicate the need for quadratic modeling.

---

### 5.2 Quality Engineering Methods

#### System of Experimental Design

- **Authors**: Taguchi, G.
- **Publisher**: UNIPUB/Kraus International, Volumes 1-2 (1987)

**Core Contribution**: Introduces robust parameter design methodology using orthogonal arrays (L4, L8, L9, L18, etc.) and signal-to-noise ratios. Separates controllable factors from noise factors using inner/outer array structure, enabling optimization for robustness rather than just mean performance.

**Relevance to clau-doom**: Taguchi L-arrays are available as screening designs in clau-doom's Phase 2 DOE catalog when many factors need screening efficiently. The signal-to-noise ratio concept informs how clau-doom evaluates agent robustness across different game scenarios (noise factors: map layout, enemy spawn patterns) rather than optimizing for a single scenario.

---

#### Multiple Attribute Decision Making

- **Authors**: Hwang, C.L. & Yoon, K.
- **Publisher**: Springer-Verlag (1981)

**Core Contribution**: Foundational work introducing the TOPSIS (Technique for Order Preference by Similarity to Ideal Solution) methodology for multi-criteria decision making. Establishes the mathematical framework for ranking alternatives based on geometric distance to ideal and anti-ideal solutions.

**Relevance to clau-doom**: TOPSIS is the primary multi-criteria ranking method in clau-doom's evolutionary pipeline. Each generation's agents are ranked on multiple objectives (kill rate, survival time, ammo efficiency, exploration coverage, damage ratio) using TOPSIS closeness coefficients, which then drive parent selection for the next generation. AHP weight calibration follows Hwang and Yoon's methodology.

---

#### FMEA Handbook

- **Publisher**: AIAG & VDA, 1st edition (2019)

**Core Contribution**: Industry-standard framework for Failure Mode and Effects Analysis, introducing the harmonized AIAG-VDA approach to risk assessment using Severity, Occurrence, and Detection ratings to compute Risk Priority Numbers (RPN) for systematic failure mode prioritization.

**Relevance to clau-doom**: clau-doom adapts the FMEA framework from manufacturing quality engineering to LLM agent evolution -- a novel cross-domain integration. Agent failure modes (e.g., "loops in corner," "depletes ammo early," "ignores health pickups") are cataloged with S/O/D ratings, and RPN drives prioritization of which behavioral failures to address in the next experimental design. SPC control charts monitor generation-over-generation performance for out-of-control signals.

---

### 5.3 DOE vs. Hyperparameter Optimization

The following works represent the dominant alternative paradigm for systematic ML system optimization. clau-doom deliberately chooses DOE over these methods for specific methodological reasons.

#### Practical Bayesian Optimization of Machine Learning Algorithms

- **Authors**: Snoek, J., Larochelle, H., Adams, R.P.
- **Venue**: NeurIPS 2012
- **Link**: https://proceedings.neurips.cc/paper/2012/hash/05311655a15b75fab86956663e1819cd-Abstract.html

**Core Contribution**: Demonstrates Gaussian Process-based Bayesian Optimization (BO) for automated ML hyperparameter tuning, using Expected Improvement as acquisition function. Shows BO consistently outperforms grid search and manual tuning across convolutional neural networks, latent Dirichlet allocation, and online LDA on multiple datasets.

**Relevance to clau-doom**: BO is the primary alternative to DOE for systematic optimization. clau-doom chooses DOE over BO for four reasons: (1) DOE provides explicit interaction detection via factorial structure, while BO treats the objective as a black-box surface; (2) DOE yields interpretable ANOVA tables with p-values and effect sizes, while BO provides only point predictions; (3) DOE designs are model-free and assumption-light, while BO assumes smooth objective landscape via GP kernel; (4) DOE naturally handles noisy game environments through replication and blocking, while BO's GP may overfit noise.

---

#### Random Search for Hyper-Parameter Optimization

- **Authors**: Bergstra, J. & Bengio, Y.
- **Venue**: Journal of Machine Learning Research 13 (2012), pp. 281-305
- **Link**: https://jmlr.org/papers/v13/bergstra12a.html

**Core Contribution**: Demonstrates that random search is more efficient than grid search for hyperparameter optimization, particularly when only a subset of hyperparameters significantly affects performance. The key insight is that grid search wastes evaluations on unimportant dimensions, while random search distributes samples more efficiently across the important subspace.

**Relevance to clau-doom**: Bergstra and Bengio's finding that few hyperparameters dominate performance motivates the need for factor screening, which is precisely what DOE's factorial designs provide. Rather than random search (which identifies good configurations but not why), DOE's ANOVA analysis identifies which factors matter and how they interact, enabling directed optimization and interpretable scientific conclusions.

---

#### A Tutorial on Bayesian Optimization

- **Authors**: Frazier, P.I.
- **Venue**: arXiv:1807.02811 (2018)
- **Link**: https://arxiv.org/abs/1807.02811

**Core Contribution**: Comprehensive tutorial on Bayesian Optimization, covering Gaussian Process surrogate models, acquisition functions (EI, KG, Entropy Search), and practical considerations for high-dimensional, noisy, and multi-fidelity settings. Provides unified mathematical framework for understanding BO's strengths and limitations.

**Relevance to clau-doom**: This tutorial clarifies when BO excels (smooth, expensive-to-evaluate objectives with few dimensions) versus when DOE is preferable (noisy objectives requiring statistical confidence, interpretable factor effects, and interaction detection). clau-doom's game environment produces inherently noisy responses (stochastic enemy behavior, spawn patterns), where DOE's replication-based variance estimation is more appropriate than BO's GP-based noise modeling.

---

## 6. VizDoom Platform and RL Baselines

### 6.1 VizDoom Platform

#### ViZDoom: A Doom-based AI Research Platform for Visual RL

- **Authors**: Kempka, M., Wydmuch, M. et al.
- **Venue**: IEEE CIG 2016; arXiv:1605.02097
- **Link**: https://arxiv.org/abs/1605.02097

**Core Contribution**: Foundational paper introducing VizDoom as RL research platform. Describes API, customizable scenarios, and provides baseline DQN results on basic scenarios. Standard scenarios include: Basic (shoot-the-monster), Defend the Center (enemies approach from all directions), Deadly Corridor (navigate with enemies), Health Gathering, Deathmatch (multi-agent combat), My Way Home (maze navigation).

**Relevance to clau-doom**: VizDoom is the exact platform clau-doom uses (via Python binding). These standard scenarios provide evaluation framework for clau-doom benchmarks. Basic, Defend the Center, and Deathmatch are primary comparison scenarios for demonstrating RAG-based approach vs. traditional RL baselines.

---

### 6.2 Competition Winners and Quantitative Baselines

#### ViZDoom Competitions: Playing Doom from Pixels

- **Authors**: Wydmuch, M., Kempka, M., Jaskowski, W.
- **Venue**: IEEE Transactions on Games 11(3), 248-259 (2019); arXiv:1809.03470
- **Link**: https://arxiv.org/abs/1809.03470

**Core Contribution**: Comprehensive summary of three editions of Visual Doom AI Competition (2016-2018), including detailed results tables, open-source implementations, and improved evaluation across 20 games. Track 1: Known single map, all agents fight simultaneously. Track 2: Unknown maps, agents must generalize.

**2016 Competition Quantitative Results**:

| Track | Place | Agent | Frags | F/D Ratio | Architecture |
|-------|-------|-------|-------|-----------|--------------|
| Track 1 | 1st | F1 (Facebook AI) | 559 | 1.35 | A3C + Curriculum |
| Track 1 | 2nd | Arnold (CMU) | 413 | 1.90 | DRQN + Action-Nav |
| Track 2 | 1st | IntelAct (Intel) | 297 | 3.08 | Direct Future Pred |
| Track 2 | 2nd | Arnold (CMU) | 167 | 32.8 | DRQN + Action-Nav |

**Relevance to clau-doom**: These frag scores and F/D ratios are primary quantitative baselines for deathmatch scenarios. clau-doom should be tested on equivalent deathmatch maps to enable direct comparison. Arnold's navigation/action architecture split conceptually similar to clau-doom's multi-level decision hierarchy.

---

#### Playing FPS Games with Deep RL (Arnold)

- **Authors**: Lample, G., Chaplot, D.S.
- **Venue**: AAAI 2017; arXiv:1609.05521
- **Link**: https://arxiv.org/abs/1609.05521

**Core Contribution**: Arnold, fully autonomous FPS agent using DRQN with separate navigation and action networks. Augments RL objective with auxiliary game feature prediction (enemy detection, item presence) during training, dramatically improving performance. Placed 2nd in both tracks of 2016 VizDoom competition with best kill-death ratio (1.90 Track 1, 32.8 Track 2). Training: several days on single GPU.

**Relevance to clau-doom**: Arnold's dual-network approach (navigation vs. action) validates clau-doom's multi-level decision hierarchy (Level 0: reflexes, Level 1: cached patterns, Level 2: RAG strategies). Arnold requires extensive training (days); clau-doom aims for faster knowledge acquisition via RAG. Arnold's game feature augmentation analogous to clau-doom's structured game state representation.

---

#### Training Agent for FPS with Actor-Critic Curriculum Learning (F1)

- **Authors**: Wu, Y., Tian, Y.
- **Venue**: ICLR 2017
- **Link**: https://openreview.net/forum?id=Hk3mPK5gg

**Core Contribution**: F1, the 2016 VizDoom Track 1 champion from Facebook AI Research. Uses A3C combined with curriculum learning that progressively increases difficulty. Won 10 of 12 rounds in Track 1 with 559 frags (35% above Arnold's 413). Curriculum learning key: direct A3C without curriculum failed in complex scenarios. Trained on progressively harder scenarios: empty map → static enemies → moving enemies → full deathmatch.

**Relevance to clau-doom**: F1's curriculum learning parallels clau-doom's DOE phase progression (simple → complex factors). F1's pure RL approach required careful curriculum design; clau-doom's RAG approach could bypass this by retrieving relevant strategies directly. F1's performance degradation from 2016 (1st) to 2017 (5th) suggests overfitting; clau-doom's cumulative knowledge approach may offer better generalization.

---

### 6.3 Modern RL Context

While clau-doom's VizDoom experiments run in the same environment as these RL baselines, the modern RL landscape has advanced considerably beyond the 2016-2017 competition era. The following references contextualize clau-doom's positioning: not as an RL replacement for maximum performance, but as an alternative paradigm offering interpretability, sample efficiency, and cumulative knowledge transfer.

#### Mastering Diverse Domains through World Models (DreamerV3)

- **Authors**: Hafner, D. et al.
- **Venue**: arXiv:2301.04104 (2023)
- **Link**: https://arxiv.org/abs/2301.04104

**Core Contribution**: World-model-based RL agent achieving human-level performance across diverse domains including Atari, DMLab, and Minecraft without domain-specific modifications. Learns a world model from experience, then plans within the learned model using actor-critic methods. Demonstrates that model-based RL can now generalize broadly across vastly different environments with a single algorithm.

**Relevance to clau-doom**: DreamerV3 represents the state of the art in general-purpose RL. clau-doom does not compete on asymptotic RL performance but on knowledge efficiency and interpretability -- areas where retrieval-based approaches offer structural advantages. DreamerV3 requires millions of environment interactions for training; clau-doom aims for effective behavior with orders of magnitude fewer episodes through knowledge accumulation.

---

#### IMPALA: Scalable Distributed Deep-RL with Importance Weighted Actor-Learner Architectures

- **Authors**: Espeholt, L. et al. (DeepMind)
- **Venue**: ICML 2018; arXiv:1802.01561
- **Link**: https://arxiv.org/abs/1802.01561

**Core Contribution**: Scalable distributed deep RL architecture that decouples acting from learning, enabling efficient training across many parallel actors with a centralized learner. Introduces V-trace off-policy correction to handle the lag between actors and learner. Achieves strong results across 57 Atari games and 30 DMLab environments simultaneously.

**Relevance to clau-doom**: IMPALA represents the scale of compute modern RL can leverage for distributed training. clau-doom's RAG approach targets scenarios where sample efficiency matters more than asymptotic optimality, achieving useful performance with orders of magnitude fewer environment interactions than IMPALA's distributed training regime.

---

### 6.4 RL Baselines and Positioning

Trained RL agents (DQN, PPO, A3C) are expected to achieve higher asymptotic performance through millions of training frames and gradient-based policy optimization. clau-doom does not compete on asymptotic performance. Its strengths lie in: (1) sample efficiency -- knowledge accumulation via RAG requires orders of magnitude fewer episodes than RL training; (2) interpretability -- strategy documents are human-readable, unlike neural network weights; (3) knowledge accumulation -- strategies transfer across agents and generations without retraining; (4) no training required -- agents are immediately deployable with retrieved strategies. A full RL baseline comparison with matched episode budgets is planned as future work; current experiments focus on validating the RAG architecture's contribution to agent performance and the DOE framework's ability to systematically optimize agent parameters.

---

### 6.5 Defend the Center Baselines

**Quantitative Results from Technical Implementations**:

- **DDQN**: Converges within ~1,000 episodes, stable at ~11 average kills
- **A2C**: Converges within ~5,000 episodes, reaches ~12 average kills (higher but more variable)
- **Reward structure**: +1 per kill, -1 per death, -0.1 per health/ammo loss

**Source**: Technical blog by Felix Yu (2017), https://flyyufelix.github.io/2017/10/12/dqn-vs-pg.html (informal benchmark; no peer-reviewed source available -- these figures should be treated as approximate reference points rather than authoritative baselines. For rigorous comparison, running matched RL baselines with identical environment configuration is recommended.)

**Relevance to clau-doom**: These per-scenario convergence rates are critical baselines. clau-doom should report equivalent metrics: episodes to stable performance, average kills. If clau-doom's RAG approach achieves similar kill rates in fewer episodes, that supports the "RAG as RL replacement" thesis.

---

## 7. Survey Papers

### 7.1 LLM Game Agent Survey

#### A Survey on Large Language Model-Based Game Agents

- **Authors**: Hu et al.
- **Venue**: arXiv v4, 2025.11; arXiv:2404.02039
- **Link**: https://arxiv.org/abs/2404.02039

**Core Contribution**: Comprehensive survey organizing LLM-based game agents with unified reference architecture. Single agent: memory, reasoning, perception-action. Multi-agent: communication, organization. Classifies challenges across 6 game genres. Maintains curated repository of papers.

**Relevance to clau-doom**: Provides landscape context and memory/reasoning/action framework for agent design. clau-doom's agent design references this three-component framework: DuckDB/OpenSearch (memory), Rust scoring (reasoning), VizDoom API (perception-action).

---

### 7.2 LLM Agent Memory Survey

#### A Survey on the Memory Mechanism of LLM-based Agents

- **Venue**: ACM TOIS, 2025
- **Core Contribution**: Comprehensive survey of LLM agent memory mechanisms, systematizing memory design and evaluation methodologies. Covers memory structures, update strategies, retrieval methods, and integration with reasoning.

**Relevance to clau-doom**: Provides theoretical framework for clau-doom's three-tier memory architecture: DuckDB (Storage: raw episode data), Ollama refinement (Reflection: trajectory analysis), OpenSearch strategy documents (Experience: abstracted knowledge for retrieval).

---

#### From Storage to Experience: Evolution of LLM Agent Memory

- **Venue**: Preprints, 2026.01
- **Core Contribution**: Proposes memory evolution framework with three stages: Storage (trajectory preservation) → Reflection (trajectory refinement) → Experience (trajectory abstraction). Each stage builds on previous, enabling increasingly sophisticated agent behavior.

**Relevance to clau-doom**: clau-doom's memory architecture directly implements this three-stage evolution: DuckDB stores raw trajectories (Storage), Ollama-powered retrospection refines insights (Reflection), OpenSearch strategy documents abstract generalizable knowledge (Experience). This theoretical alignment validates clau-doom's design.

---

### 7.3 LLM + Evolutionary Computation Survey

#### Evolutionary Computation in the Era of LLM: Survey and Roadmap

- **Authors**: Wu et al.
- **Venue**: arXiv, 2024.01
- **Link**: https://arxiv.org/abs/2401.xxxxx

**Core Contribution**: Comprehensive survey of LLM-evolutionary algorithm interactions. Covers LLMs as mutation/crossover operators, prompt evolution, evolutionary prompt engineering, and hybrid approaches. Identifies key challenges: computational cost, fitness landscape complexity, and evaluation reliability.

**Relevance to clau-doom**: Provides theoretical foundation for clau-doom's LLM-mediated MD file evolution. Survey validates using LLMs as evolutionary operators while highlighting need for rigorous evaluation (addressed by clau-doom's DOE/ANOVA framework). Positions clau-doom within broader LLM+EA research landscape.

---

## 8. Additional Related Work

### 8.1 Game Environment LLM Agents

| Paper | Venue | Core Contribution | Relevance |
|-------|-------|-------------------|-----------|
| **JARVIS-1** | arXiv 2023.11 | Memory-Augmented Multimodal LLM for Minecraft open-world multitask | Memory augmentation patterns |
| **Ghost in the Minecraft (GITM)** | arXiv 2023.05 | Text-based knowledge + memory for Minecraft general agent | Text-based knowledge utilization |
| **Generative Agents** | Park et al. 2023 | Human behavior simulation with memory stream + reflection + planning | Agent memory architecture prototype |
| **Cradle** | arXiv 2024.03 | Foundation agent for general-purpose computer control including games | Universal agent design reference |
| **SayCan** | Ahn et al., arXiv:2204.01691 (2022) | Grounds language in robotic affordances; LLM proposes actions scored by learned affordance functions to select executable plans | Demonstrates grounding LLM reasoning in physical/environmental affordances -- analogous to how clau-doom grounds strategy retrieval in game-state feasibility via Rust scoring |
| **MineDojo** | Fan et al., NeurIPS 2022 | Open-ended embodied agent benchmark built on Minecraft with internet-scale knowledge (YouTube, Wiki, Reddit) for training and evaluation | Validates internet-scale knowledge integration for game agents; clau-doom's OpenSearch strategy repository serves analogous role as curated domain knowledge base for agent decision-making |

---

### 8.2 Multi-Agent Cooperation/Competition

| Paper | Venue | Core Contribution | Relevance |
|-------|-------|-------------------|-----------|
| **Emergent Tool Use** | Baker et al., ICLR 2020 | Multi-agent competition produces emergent tool use and strategies via autocurriculum | Validates competitive pressure for improvement |
| **Population Based Training (PBT)** | Jaderberg et al., arXiv 2017 | Asynchronous optimization of model populations with exploit/explore dynamics | Population-level optimization parallel |
| **Embodied LLM Agents Cooperate** | arXiv 2024.03 | LLM coordinator iteratively improves organization in VirtualHome | NATS pub/sub knowledge sharing design |
| **OpenAI Five** | Berner et al., arXiv 2019 | Multi-agent coordination at scale in Dota 2, defeating world champions using distributed PPO with self-play across thousands of GPUs | Demonstrates multi-agent coordination scaling; clau-doom targets same coordination goals via knowledge sharing rather than massive compute |
| **SMAC (StarCraft Multi-Agent Challenge)** | Samvelyan et al., AAMAS 2019 | Cooperative multi-agent benchmark suite on StarCraft II micromanagement scenarios, establishing standardized evaluation for MARL | Standard MARL benchmark; contextualizes clau-doom's multi-agent approach within cooperative/competitive evaluation frameworks |

---

### 8.3 LLM-Based Evolution/Optimization

| Paper | Venue | Core Contribution | Relevance |
|-------|-------|-------------------|-----------|
| **LLM_GP** | Genetic Programming & Evolvable Machines 2024 | LLM as evolution operator, text-based genomes, LLM mutation/crossover | Direct reference for MD file crossover/mutation |
| **Language Model Crossover (LMX)** | ACM TELO 2023; arXiv:2302.12170 | LLMs as crossover operators via few-shot prompting, domain-general | Validates MD document crossover feasibility |
| **EvoPrompt** | Guo et al. | EA-based prompt optimization using GA and DE for prompt evolution | Applicable to agent MD prompt evolution |

---

## 9. clau-doom Contribution Positioning vs. Prior Work

| clau-doom Contribution | Closest Prior Work | Differentiation |
|------------------------|-------------------|-----------------|
| **RAG + experience docs improve behavior without RL** | Reflexion (verbal RL), MFEC/NEC (episodic control) | Reflexion uses episodic memory buffer; MFEC/NEC store (state, action, value) tuples. clau-doom uses OpenSearch kNN + structured strategy documents with trust-weighted scoring (Wilson lower bound). No gradient updates at decision time. |
| **Multi-agent knowledge sharing + natural selection** | EvoAgent, S-Agents, PBT | EvoAgent generates agents via evolution; PBT uses exploit/explore over populations. clau-doom combines NATS pub/sub knowledge broadcast + generational evolution + QD-inspired diversity maintenance (MAP-Elites behavioral coverage). |
| **LLM as PI: autonomous experiment design/control** | AI Scientist v1/v2, Coscientist, data-to-paper | AI Scientist uses informal evaluation; Coscientist operates in chemistry with no DOE. clau-doom's PI uses formal DOE methodology (factorial, RSM, Taguchi) with ANOVA validation, trust scoring, and DOE phase progression (OFAT → Factorial → RSM → Split-Plot). |
| **RAG-based agent in FPS domain** | Will GPT-4 Run DOOM? (de Wynter 2024) | GPT-4 achieves 0/10 completion with ~60s/frame latency. clau-doom eliminates real-time LLM calls (< 100ms decision via Rust scoring) through RAG knowledge accumulation + generational evolution. |
| **MD file-based agent DNA (text-based genomes)** | Voyager skill library, LLMatic (NAS + QD) | Voyager stores executable code skills; LLMatic evolves code within MAP-Elites. clau-doom evolves declarative Markdown strategy documents serving dual roles: evolutionary genomes AND retrievable knowledge for real-time decision-making. |
| **Retrieval as complete RL policy replacement** | Retrieval-Augmented RL (Goyal et al.), Decision Transformer | Goyal et al. augment RL with retrieval; Decision Transformer conditions on return-to-go. clau-doom substitutes learned policy entirely with kNN retrieval + deterministic Rust scoring—stronger claim than augmentation. |
| **DOE-based statistical evaluation for agent evolution** | FunSearch, AlphaEvolve, Snoek et al. (BO) | FunSearch uses automated scoring; AlphaEvolve uses formal verifiers; BO (Snoek et al.) provides systematic optimization but no interaction detection or ANOVA. clau-doom provides interpretable statistical guarantees (Montgomery DOE framework) absent from all prior LLM evolution work. |
| **Quality engineering for generational evolution** | Taguchi (robust design), Hwang & Yoon (TOPSIS), AIAG (FMEA) | Industrial QE methods (SPC control charts, FMEA risk analysis, TOPSIS multi-criteria selection) integrated into evolutionary pipeline. No prior work combines quality engineering methodology with LLM-driven agent evolution -- a novel cross-domain integration. |

---

## 10. Research Gaps and clau-doom Opportunities

### 10.1 Identified Gaps

1. **Retrieval as Policy Replacement**: All retrieval-augmented RL systems use retrieval to augment learned policies. No prior work tests complete substitution in complex game environments.

2. **Statistical Rigor in LLM Evolution**: FunSearch, AlphaEvolve, EvoAgent lack formal DOE methodology. No confidence intervals, effect sizes, or power analysis.

3. **Real-Time LLM Elimination**: Voyager, GITM, and other LLM agents require real-time inference. No prior FPS agent demonstrates LLM-free real-time decisions with offline LLM knowledge accumulation.

4. **Multi-Generational Scientific Method**: AI Scientist generates single papers; no system maintains cumulative research knowledge base with trust scoring across generations.

5. **Quality Engineering for Agent Evolution**: No prior work integrates SPC, FMEA, TOPSIS into LLM-driven evolutionary pipelines.

---

### 10.2 clau-doom's Novel Contributions

1. **Retrieval-only decision architecture** with no learned policy (MFEC/NEC foundation + RAG paradigm extension)
2. **Trust-weighted retrieval** using Wilson score confidence intervals (no precedent in episodic RL)
3. **Dynamic strategy refinement** through LLM retrospection (vs. static/append-only memories)
4. **Formal DOE methodology** for agent evaluation (factorial, RSM, ANOVA, power analysis)
5. **Multi-generational cumulative knowledge** with trust scoring and audit trails
6. **Quality engineering integration** (SPC, FMEA, TOPSIS) into evolutionary AI
7. **No real-time LLM dependency** for FPS gameplay (< 100ms decision latency)

---

## 11. Recommended Reading Priority

### Must Read (Core Theoretical Foundation)
1. **Reflexion** — Episodic learning without weight updates
2. **Will GPT-4 Run DOOM?** — Direct domain precedent
3. **Voyager** — Skill library architecture
4. **RL-GPT** — Hierarchical LLM+RL separation
5. **LLM Game Agents Survey** — Landscape overview
6. **MFEC/NEC** — Episodic control foundations
7. **RAG (Lewis et al.)** — Retrieval-augmented paradigm
8. **Montgomery (2017)** — DOE methodology foundation

### Deep Dive (Methodological Details)
9. **MAP-Elites** — Quality-diversity foundations
10. **EvoPrompting** — LLM as evolutionary operator
11. **FunSearch** — Program search with LLM+evaluation
12. **AI Scientist v1/v2** — Autonomous research systems
13. **Goyal et al. RA-RL** — Retrieval-augmented RL
14. **Decision Transformer** — RL as sequence modeling
15. **VizDoom Competitions** — Quantitative baselines
16. **Snoek et al. (BO)** — Bayesian optimization baseline for DOE comparison
17. **RETRO (Borgeaud et al.)** — Retrieval substitutes for model capacity
18. **Coscientist (Boiko et al.)** — LLM as autonomous experimental scientist

### Technical Reference (Implementation)
19. **VizDoom original paper** — Game environment API
20. **Arnold/F1 papers** — RL baseline architectures
21. **AgentHPO** — LLM-based experimental optimization
22. **LMX** — Language model crossover mechanics
23. **Memory Mechanism Survey** — Memory architecture design
24. **Evolutionary Computation + LLM Survey** — LLM+EA integration patterns
25. **Box, Hunter & Hunter (2005)** — RSM methodology
26. **Myers, Montgomery & Anderson-Cook (2016)** — CCD/BBD design theory
27. **Hwang & Yoon (1981)** — TOPSIS methodology
28. **kNN-LM (Khandelwal et al., 2020)** — Nearest neighbor retrieval for generalization
29. **NEAT (Stanley & Miikkulainen, 2002)** — Neuroevolution topology evolution
30. **Evolution Strategies (Salimans et al., 2017)** — ES as RL alternative
31. **Knowledge Distillation (Hinton et al., 2015)** — Cross-model knowledge transfer
32. **data-to-paper (Ifargan et al., 2024)** — Autonomous data-to-paper pipeline

---

## References

See individual paper entries above for full citations. Total references: 54 core papers + 4 comprehensive surveys (58 total).
