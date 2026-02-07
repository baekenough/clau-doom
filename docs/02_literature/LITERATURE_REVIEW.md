# clau-doom Literature Review

> Project: LLM-based Multi-Agent Evolutionary Doom Player
> Purpose: Establish theoretical foundations and position contributions
> Last Updated: 2026-02-07

---

**Total Papers**: 31 core references + comprehensive surveys

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

### 4.2 FunSearch (Cross-Reference)

See Section 2.3 for full details. FunSearch demonstrates that LLM-driven evolutionary search with automated evaluation can discover novel mathematical constructions, validating clau-doom's evolutionary approach with DOE-based evaluation.

---

### 4.3 AgentHPO: LLM Agent for Hyperparameter Optimization

#### AgentHPO: Large Language Model Agent for Hyper-Parameter Optimization

- **Authors**: Liu, S., Gao, C., Li, Y.
- **Venue**: arXiv:2402.01881 (2024)
- **Link**: https://arxiv.org/abs/2402.01881

**Core Contribution**: LLM-based agent system for hyperparameter optimization using two specialized agents: Creator (generates initial hyperparameters from natural language task descriptions) and Executor (runs experiments and iteratively refines parameters based on historical trials). At T=10 trials, AgentHPO (GPT-3.5) outperforms random search by 2.65% and Bayesian optimization by 1.39% on 12 ML benchmarks.

**Relevance to clau-doom**: AgentHPO's Creator/Executor pattern directly parallels clau-doom's PI/DOE-runner separation. Both iterate based on historical trial performance. Key differences: AgentHPO optimizes ML hyperparameters with informal iteration; clau-doom optimizes game agent behavior parameters using formal DOE methodology (factorial/RSM designs with ANOVA validation). AgentHPO has no multi-generational evolution concept; clau-doom accumulates knowledge across generations.

---

## 5. VizDoom Platform and RL Baselines

### 5.1 VizDoom Platform

#### ViZDoom: A Doom-based AI Research Platform for Visual RL

- **Authors**: Kempka, M., Wydmuch, M. et al.
- **Venue**: IEEE CIG 2016; arXiv:1605.02097
- **Link**: https://arxiv.org/abs/1605.02097

**Core Contribution**: Foundational paper introducing VizDoom as RL research platform. Describes API, customizable scenarios, and provides baseline DQN results on basic scenarios. Standard scenarios include: Basic (shoot-the-monster), Defend the Center (enemies approach from all directions), Deadly Corridor (navigate with enemies), Health Gathering, Deathmatch (multi-agent combat), My Way Home (maze navigation).

**Relevance to clau-doom**: VizDoom is the exact platform clau-doom uses (via Python binding). These standard scenarios provide evaluation framework for clau-doom benchmarks. Basic, Defend the Center, and Deathmatch are primary comparison scenarios for demonstrating RAG-based approach vs. traditional RL baselines.

---

### 5.2 Competition Winners and Quantitative Baselines

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

### 5.3 Defend the Center Baselines

**Quantitative Results from Technical Implementations**:

- **DDQN**: Converges within ~1,000 episodes, stable at ~11 average kills
- **A2C**: Converges within ~5,000 episodes, reaches ~12 average kills (higher but more variable)
- **Reward structure**: +1 per kill, -1 per death, -0.1 per health/ammo loss

**Source**: Technical blog by Felix Yu (2017), https://flyyufelix.github.io/2017/10/12/dqn-vs-pg.html

**Relevance to clau-doom**: These per-scenario convergence rates are critical baselines. clau-doom should report equivalent metrics: episodes to stable performance, average kills. If clau-doom's RAG approach achieves similar kill rates in fewer episodes, that supports the "RAG as RL replacement" thesis.

---

## 6. Survey Papers

### 6.1 LLM Game Agent Survey

#### A Survey on Large Language Model-Based Game Agents

- **Authors**: Hu et al.
- **Venue**: arXiv v4, 2025.11; arXiv:2404.02039
- **Link**: https://arxiv.org/abs/2404.02039

**Core Contribution**: Comprehensive survey organizing LLM-based game agents with unified reference architecture. Single agent: memory, reasoning, perception-action. Multi-agent: communication, organization. Classifies challenges across 6 game genres. Maintains curated repository of papers.

**Relevance to clau-doom**: Provides landscape context and memory/reasoning/action framework for agent design. clau-doom's agent design references this three-component framework: DuckDB/OpenSearch (memory), Rust scoring (reasoning), VizDoom API (perception-action).

---

### 6.2 LLM Agent Memory Survey

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

### 6.3 LLM + Evolutionary Computation Survey

#### Evolutionary Computation in the Era of LLM: Survey and Roadmap

- **Authors**: Wu et al.
- **Venue**: arXiv, 2024.01
- **Link**: https://arxiv.org/abs/2401.xxxxx

**Core Contribution**: Comprehensive survey of LLM-evolutionary algorithm interactions. Covers LLMs as mutation/crossover operators, prompt evolution, evolutionary prompt engineering, and hybrid approaches. Identifies key challenges: computational cost, fitness landscape complexity, and evaluation reliability.

**Relevance to clau-doom**: Provides theoretical foundation for clau-doom's LLM-mediated MD file evolution. Survey validates using LLMs as evolutionary operators while highlighting need for rigorous evaluation (addressed by clau-doom's DOE/ANOVA framework). Positions clau-doom within broader LLM+EA research landscape.

---

## 7. Additional Related Work

### 7.1 Game Environment LLM Agents

| Paper | Venue | Core Contribution | Relevance |
|-------|-------|-------------------|-----------|
| **JARVIS-1** | arXiv 2023.11 | Memory-Augmented Multimodal LLM for Minecraft open-world multitask | Memory augmentation patterns |
| **Ghost in the Minecraft (GITM)** | arXiv 2023.05 | Text-based knowledge + memory for Minecraft general agent | Text-based knowledge utilization |
| **Generative Agents** | Park et al. 2023 | Human behavior simulation with memory stream + reflection + planning | Agent memory architecture prototype |
| **Cradle** | arXiv 2024.03 | Foundation agent for general-purpose computer control including games | Universal agent design reference |

---

### 7.2 Multi-Agent Cooperation/Competition

| Paper | Venue | Core Contribution | Relevance |
|-------|-------|-------------------|-----------|
| **Emergent Tool Use** | Baker et al., ICLR 2020 | Multi-agent competition produces emergent tool use and strategies via autocurriculum | Validates competitive pressure for improvement |
| **Population Based Training (PBT)** | Jaderberg et al., arXiv 2017 | Asynchronous optimization of model populations with exploit/explore dynamics | Population-level optimization parallel |
| **Embodied LLM Agents Cooperate** | arXiv 2024.03 | LLM coordinator iteratively improves organization in VirtualHome | NATS pub/sub knowledge sharing design |

---

### 7.3 LLM-Based Evolution/Optimization

| Paper | Venue | Core Contribution | Relevance |
|-------|-------|-------------------|-----------|
| **LLM_GP** | Genetic Programming & Evolvable Machines 2024 | LLM as evolution operator, text-based genomes, LLM mutation/crossover | Direct reference for MD file crossover/mutation |
| **Language Model Crossover (LMX)** | ACM TELO 2023; arXiv:2302.12170 | LLMs as crossover operators via few-shot prompting, domain-general | Validates MD document crossover feasibility |
| **EvoPrompt** | Guo et al. | EA-based prompt optimization using GA and DE for prompt evolution | Applicable to agent MD prompt evolution |

---

## 8. clau-doom Contribution Positioning vs. Prior Work

| clau-doom Contribution | Closest Prior Work | Differentiation |
|------------------------|-------------------|-----------------|
| **RAG + experience docs improve behavior without RL** | Reflexion (verbal RL), MFEC/NEC (episodic control) | Reflexion uses episodic memory buffer; MFEC/NEC store (state, action, value) tuples. clau-doom uses OpenSearch kNN + structured strategy documents with trust-weighted scoring (Wilson lower bound). No gradient updates at decision time. |
| **Multi-agent knowledge sharing + natural selection** | EvoAgent, S-Agents, PBT | EvoAgent generates agents via evolution; PBT uses exploit/explore over populations. clau-doom combines NATS pub/sub knowledge broadcast + generational evolution + QD-inspired diversity maintenance (MAP-Elites behavioral coverage). |
| **LLM as PI: autonomous experiment design/control** | AI Scientist v1/v2, Coscientist, data-to-paper | AI Scientist uses informal evaluation; Coscientist operates in chemistry with no DOE. clau-doom's PI uses formal DOE methodology (factorial, RSM, Taguchi) with ANOVA validation, trust scoring, and DOE phase progression (OFAT → Factorial → RSM → Split-Plot). |
| **RAG-based agent in FPS domain** | Will GPT-4 Run DOOM? (de Wynter 2024) | GPT-4 achieves 0/10 completion with ~60s/frame latency. clau-doom eliminates real-time LLM calls (< 100ms decision via Rust scoring) through RAG knowledge accumulation + generational evolution. |
| **MD file-based agent DNA (text-based genomes)** | Voyager skill library, LLMatic (NAS + QD) | Voyager stores executable code skills; LLMatic evolves code within MAP-Elites. clau-doom evolves declarative Markdown strategy documents serving dual roles: evolutionary genomes AND retrievable knowledge for real-time decision-making. |
| **Retrieval as complete RL policy replacement** | Retrieval-Augmented RL (Goyal et al.), Decision Transformer | Goyal et al. augment RL with retrieval; Decision Transformer conditions on return-to-go. clau-doom substitutes learned policy entirely with kNN retrieval + deterministic Rust scoring—stronger claim than augmentation. |
| **DOE-based statistical evaluation for agent evolution** | FunSearch, AlphaEvolve | FunSearch uses automated scoring; AlphaEvolve uses formal verifiers. Neither applies DOE (ANOVA, effect sizes, power analysis, confidence intervals). clau-doom provides statistical guarantees absent from all prior LLM evolution work. |
| **Quality engineering for generational evolution** | None (novel integration) | SPC control charts, FMEA risk analysis, TOPSIS multi-criteria selection integrated into evolutionary pipeline. No prior work combines quality engineering with LLM-driven evolution. |

---

## 9. Research Gaps and clau-doom Opportunities

### 9.1 Identified Gaps

1. **Retrieval as Policy Replacement**: All retrieval-augmented RL systems use retrieval to augment learned policies. No prior work tests complete substitution in complex game environments.

2. **Statistical Rigor in LLM Evolution**: FunSearch, AlphaEvolve, EvoAgent lack formal DOE methodology. No confidence intervals, effect sizes, or power analysis.

3. **Real-Time LLM Elimination**: Voyager, GITM, and other LLM agents require real-time inference. No prior FPS agent demonstrates LLM-free real-time decisions with offline LLM knowledge accumulation.

4. **Multi-Generational Scientific Method**: AI Scientist generates single papers; no system maintains cumulative research knowledge base with trust scoring across generations.

5. **Quality Engineering for Agent Evolution**: No prior work integrates SPC, FMEA, TOPSIS into LLM-driven evolutionary pipelines.

---

### 9.2 clau-doom's Novel Contributions

1. **Retrieval-only decision architecture** with no learned policy (MFEC/NEC foundation + RAG paradigm extension)
2. **Trust-weighted retrieval** using Wilson score confidence intervals (no precedent in episodic RL)
3. **Dynamic strategy refinement** through LLM retrospection (vs. static/append-only memories)
4. **Formal DOE methodology** for agent evaluation (factorial, RSM, ANOVA, power analysis)
5. **Multi-generational cumulative knowledge** with trust scoring and audit trails
6. **Quality engineering integration** (SPC, FMEA, TOPSIS) into evolutionary AI
7. **No real-time LLM dependency** for FPS gameplay (< 100ms decision latency)

---

## 10. Recommended Reading Priority

### Must Read (Core Theoretical Foundation)
1. **Reflexion** — Episodic learning without weight updates
2. **Will GPT-4 Run DOOM?** — Direct domain precedent
3. **Voyager** — Skill library architecture
4. **RL-GPT** — Hierarchical LLM+RL separation
5. **LLM Game Agents Survey** — Landscape overview
6. **MFEC/NEC** — Episodic control foundations
7. **RAG (Lewis et al.)** — Retrieval-augmented paradigm

### Deep Dive (Methodological Details)
8. **MAP-Elites** — Quality-diversity foundations
9. **EvoPrompting** — LLM as evolutionary operator
10. **FunSearch** — Program search with LLM+evaluation
11. **AI Scientist v1/v2** — Autonomous research systems
12. **Goyal et al. RA-RL** — Retrieval-augmented RL
13. **Decision Transformer** — RL as sequence modeling
14. **VizDoom Competitions** — Quantitative baselines

### Technical Reference (Implementation)
15. **VizDoom original paper** — Game environment API
16. **Arnold/F1 papers** — RL baseline architectures
17. **AgentHPO** — LLM-based experimental optimization
18. **LMX** — Language model crossover mechanics
19. **Memory Mechanism Survey** — Memory architecture design
20. **Evolutionary Computation + LLM Survey** — LLM+EA integration patterns

---

## References

See individual paper entries above for full citations. Total references: 31 core papers + comprehensive surveys.
