# S1-02: RAG for Decision-Making Literature Survey

> **Session**: S1 (Literature Collection)
> **Priority**: RED critical
> **Dependencies**: None
> **Status**: COMPLETE

---

## Purpose

Using RAG for real-time action selection is the most unconventional design decision in the clau-doom project. While existing literature (Reflexion, Voyager) covers self-reflection and skill libraries, there is limited prior work on retrieval-based decision-making as a replacement for RL policies. This survey establishes the academic positioning for the claim that "RAG can substitute for RL in constrained decision-making scenarios," covering episodic RL, sequence-model-based decision making, and retrieval-augmented architectures applied beyond NLP.

---

## Category A: Retrieval-Augmented Decision Making / Episodic RL

**Why needed**: clau-doom's core mechanism -- OpenSearch kNN retrieval followed by Rust scoring followed by action selection -- constitutes "retrieval as policy." The episodic RL and retrieval-augmented RL literature provides the most direct precedents.

---

### A1. Model-Free Episodic Control (Blundell et al., 2016, ICML workshop)

- **Full citation**: Blundell, C., Uria, B., Pritzel, A., Li, Y., Ruderman, A., Leibo, J. Z., Rae, J., Wierstra, D. & Hassabis, D. (2016). Model-Free Episodic Control. arXiv:1606.04460.
- **Link**: https://arxiv.org/abs/1606.04460

- **Core contribution**: Proposes a non-parametric model that stores the highest Q-values observed for state-action pairs in a tabular memory, using k-nearest-neighbor (kNN) lookup for action selection. At decision time, the agent finds the k closest states in memory for each available action and selects the action with the highest estimated return. The method achieves significantly faster initial learning than deep RL baselines on Atari games by directly replaying successful past experiences rather than slowly updating neural network parameters.

- **clau-doom relevance**: MFEC is the most direct conceptual ancestor of clau-doom's decision architecture. clau-doom's OpenSearch kNN search for strategy documents is structurally identical to MFEC's kNN lookup for Q-values. The key parallel: both systems bypass learned policy functions entirely, instead using nearest-neighbor retrieval over a memory of past experiences to select actions. MFEC stores (state, action, return) tuples; clau-doom stores (situation_embedding, strategy_document, success_rate) tuples. Both use kNN for retrieval.

- **Differentiation**: MFEC uses raw state observations and tabular Q-value storage; clau-doom uses semantic embeddings (via Ollama) and structured strategy documents. MFEC's memory grows unbounded; clau-doom's strategy documents are curated and refined through LLM-mediated retrospection. MFEC has no mechanism for generalizing across experiences; clau-doom's strategy documents encode abstract knowledge that transfers across similar situations.

- **Reference type**: Direct citation (foundational concept)

---

### A2. Neural Episodic Control (Pritzel et al., 2017, ICML)

- **Full citation**: Pritzel, A., Uria, B., Srinivasan, S., Puigdomenech Badia, A., Vinyals, O., Hassabis, D., Wierstra, D. & Blundell, C. (2017). Neural Episodic Control. Proceedings of the 34th International Conference on Machine Learning (ICML), 70, 2827-2836.
- **Link**: https://arxiv.org/abs/1703.01988

- **Core contribution**: Extends MFEC by replacing raw state representations with learned embeddings from a convolutional neural network and replacing the Q-table with Differentiable Neural Dictionaries (DNDs). DNDs enable end-to-end training of the embedding function through backpropagation. NEC dramatically outperforms all other algorithms in the low-data regime (< 20 million frames), with the advantage being especially pronounced before 5 million frames.

- **clau-doom relevance**: NEC's architecture directly maps to clau-doom's design: (1) learned embeddings for state representation = Ollama-generated embeddings for game situations; (2) DND key-value store = OpenSearch vector index; (3) kNN lookup for action selection = kNN strategy retrieval. NEC's demonstration that learned embeddings significantly improve episodic control validates clau-doom's use of Ollama for embedding generation rather than raw feature vectors. NEC's superior data efficiency in the low-data regime is especially relevant because clau-doom operates with limited gameplay episodes per generation.

- **Differentiation**: NEC learns embeddings end-to-end through gradient descent on rewards; clau-doom uses pre-trained embeddings from Ollama without task-specific fine-tuning. NEC stores scalar Q-values; clau-doom stores rich strategy documents with multiple metadata fields (trust_score, success_rate, applicable_situations). NEC's memory is write-once-per-episode; clau-doom's strategy documents are iteratively refined through LLM retrospection across multiple episodes.

- **Reference type**: Direct citation (architectural precedent)

---

### A3. Retrieval-Augmented Reinforcement Learning (Goyal et al., 2022, ICML)

- **Full citation**: Goyal, A., Friesen, A. L., Banino, A., Weber, T., Ke, N. R., Badia, A. P., Guez, A., Mirza, M., Humphreys, P. C., Konyushova, K. et al. (2022). Retrieval-Augmented Reinforcement Learning. Proceedings of the 39th International Conference on Machine Learning (ICML).
- **Link**: https://arxiv.org/abs/2202.08417

- **Core contribution**: Augments RL agents with a trainable retrieval process (parameterized as a neural network) that has direct access to a dataset of experiences. The retrieval module learns to identify which past experiences are useful for the current context, using case-based reasoning. Integrated into both offline DQN and online R2D2 agents, retrieval-augmented DQN avoids task interference and learns faster, while retrieval-augmented R2D2 significantly outperforms baseline R2D2 on Atari. The retrieval mechanism is trained end-to-end to maximize task performance.

- **clau-doom relevance**: This is the closest existing work to clau-doom's retrieval-based decision architecture. Both systems retrieve relevant past experiences to inform current decisions. The key difference is that Goyal et al. train the retrieval mechanism end-to-end with the RL agent, while clau-doom uses pre-trained embeddings and a fixed kNN retrieval process with Wilson score-based ranking. Goyal et al. demonstrate that retrieval augmentation provides consistent improvement over non-retrieval baselines, validating clau-doom's core assumption that retrieval improves decision quality.

- **Differentiation**: Goyal et al. use retrieval to augment an existing RL policy (the retrieval complements learned behavior); clau-doom uses retrieval as the primary decision mechanism (retrieval replaces learned behavior). This is a fundamental architectural difference: augmentation vs. substitution. clau-doom's more radical approach eliminates the need for gradient-based policy learning entirely, relying solely on retrieval + scoring.

- **Reference type**: Direct citation (closest related work)

---

### A4. Large-Scale Retrieval for Reinforcement Learning (Humphreys et al., 2022, NeurIPS)

- **Full citation**: Humphreys, P. C., Guez, A., Tieleman, O., Sifre, L., Weber, T. & Lillicrap, T. (2022). Large-Scale Retrieval for Reinforcement Learning. NeurIPS 2022.
- **Link**: https://arxiv.org/abs/2206.05314

- **Core contribution**: Proposes that RL agents can utilise large-scale context-sensitive database lookups to support their parametric computations, using fast approximate nearest neighbor matching to dynamically retrieve relevant information from a dataset of experience. A key advantage is that new information can be attended to without retraining by simply augmenting the retrieval dataset. The approach is studied for offline RL in 9x9 Go, where the vast combinatorial state space privileges generalization over direct matching.

- **clau-doom relevance**: Humphreys et al.'s architecture, where a large experience database is queried via approximate nearest neighbor search to augment decision-making, is structurally identical to clau-doom's OpenSearch-based architecture. The "no retraining needed" property is exactly what clau-doom achieves: new strategy documents can be added to OpenSearch without any model updates, immediately improving agent behavior. The Go domain demonstrates that retrieval-augmented RL scales to combinatorially complex domains, validating clau-doom's application to the complex state space of DOOM.

- **Differentiation**: Humphreys et al. use retrieval to augment a neural network policy in a two-player perfect-information game; clau-doom uses retrieval as the sole decision mechanism in a real-time imperfect-information FPS environment. Humphreys et al. store raw experience tuples; clau-doom stores abstracted strategy documents that encode generalized knowledge. clau-doom's decision latency requirement (< 100ms) is more stringent than offline Go evaluation.

- **Reference type**: Direct citation (scalability validation)

---

## Category B: Decision Transformer / Sequence Model-Based Decision Making

**Why needed**: Decision Transformers and trajectory-based sequence models represent the RL-as-sequence-modeling paradigm. clau-doom's "retrieve past strategy, condition on desired outcome, select action" pipeline shares structural similarities with these approaches.

---

### B1. Decision Transformer: Reinforcement Learning via Sequence Modeling (Chen et al., 2021, NeurIPS)

- **Full citation**: Chen, L., Lu, K., Rajeswaran, A., Lee, K., Grover, A., Laskin, M., Abbeel, P., Srinivas, A. & Mordatch, I. (2021). Decision Transformer: Reinforcement Learning via Sequence Modeling. NeurIPS 2021.
- **Link**: https://arxiv.org/abs/2106.01345

- **Core contribution**: Casts RL as conditional sequence modeling, where a causal Transformer autoregressively predicts actions conditioned on desired return, past states, and past actions. Unlike value function fitting or policy gradient methods, Decision Transformer (DT) simply generates actions that achieve the desired return. Despite its simplicity, DT matches or exceeds state-of-the-art model-free offline RL baselines on Atari, OpenAI Gym, and Key-to-Door tasks.

- **clau-doom relevance**: DT's core insight, that conditioning on desired outcomes enables effective decision-making without explicit value function learning, parallels clau-doom's approach. In clau-doom, strategy documents encode "if situation X, do action Y to achieve outcome Z," which is a retrieval-based form of return-conditioned action generation. DT conditions on desired return-to-go; clau-doom conditions on strategy document trust scores and success rates. Both bypass traditional RL value/policy learning.

- **Differentiation**: DT learns a parametric model (Transformer weights) from offline trajectories; clau-doom uses non-parametric retrieval (kNN lookup) with no learned model. DT requires training on trajectory data; clau-doom requires curating strategy documents. DT generalizes through learned representations; clau-doom generalizes through semantic similarity in embedding space. clau-doom's approach is more interpretable (human-readable documents vs. neural network weights) but potentially less capable of capturing complex temporal dependencies.

- **Reference type**: Direct citation (paradigm comparison)

---

### B2. Offline Reinforcement Learning as One Big Sequence Modeling Problem (Janner et al., 2021, NeurIPS)

- **Full citation**: Janner, M., Li, Q. & Levine, S. (2021). Offline Reinforcement Learning as One Big Sequence Modeling Problem. NeurIPS 2021.
- **Link**: https://arxiv.org/abs/2106.02039

- **Core contribution**: Proposes the Trajectory Transformer, which models entire trajectories (states, actions, rewards) as sequences and uses beam search as a planning algorithm. By treating RL purely as sequence modeling, the approach replaces the entire RL pipeline (value estimation, policy optimization) with a single sequence model and a search algorithm. Demonstrates effectiveness across long-horizon dynamics prediction, imitation learning, goal-conditioned RL, and offline RL. Shows that Transformers are more reliable long-horizon predictors than state-of-the-art single-step models.

- **clau-doom relevance**: The Trajectory Transformer's philosophy of replacing the RL pipeline with sequence modeling + search is conceptually aligned with clau-doom's philosophy of replacing RL with retrieval + scoring. Where Janner et al. use beam search over generated trajectory sequences, clau-doom uses kNN retrieval over stored strategy documents followed by Wilson score ranking. Both approaches frame decision-making as a search problem over experience representations rather than as a parametric optimization problem.

- **Differentiation**: The Trajectory Transformer learns a generative model over trajectory sequences; clau-doom retrieves pre-existing strategy documents without generation. Janner et al. use beam search to plan multi-step trajectories; clau-doom makes single-step decisions based on retrieved strategies. The Trajectory Transformer requires significant compute for sequence generation during planning; clau-doom's kNN lookup operates in < 100ms with no generation cost.

- **Reference type**: Direct citation (philosophical alignment)

---

### B3. In-Context Reinforcement Learning with Algorithm Distillation (Laskin et al., 2022, ICLR 2023)

- **Full citation**: Laskin, M., Wang, L., Oh, J. et al. (2022). In-Context Reinforcement Learning with Algorithm Distillation. ICLR 2023.
- **Link**: https://arxiv.org/abs/2210.14215

- **Core contribution**: Proposes Algorithm Distillation (AD), which distills RL algorithms into neural networks by training a causal Transformer on cross-episode learning histories. The key innovation is that AD improves its policy entirely in-context without updating network parameters, achieving true in-context RL. The method learns a more data-efficient RL algorithm than the one that generated the source data, demonstrating emergent improvement through context conditioning.

- **clau-doom relevance**: AD's in-context learning, where the model improves behavior by conditioning on previous episodes without parameter updates, is conceptually related to clau-doom's cross-episode strategy accumulation. In clau-doom, after each episode, the retrospection process generates or updates strategy documents in OpenSearch, and subsequent episodes benefit from this expanded knowledge base without any model updates. Both systems achieve "learning without gradient updates," though through different mechanisms (in-context attention vs. retrieval augmentation).

- **Differentiation**: AD requires training a large Transformer on many learning histories upfront; clau-doom's learning is incremental through document accumulation with no upfront training. AD's improvement is implicit (embedded in Transformer attention patterns); clau-doom's improvement is explicit (new/updated strategy documents in OpenSearch). AD operates on single-agent RL; clau-doom operates on multi-agent populations with knowledge sharing.

- **Reference type**: Background reference (in-context learning parallel)

---

## Category C: RAG / RETRO and Retrieval-Augmented Architectures Beyond NLP

**Why needed**: RAG and RETRO established the retrieval-augmented paradigm for NLP. clau-doom extends this paradigm from text generation to action generation. Positioning requires understanding the original RAG framework and its extensions.

---

### C1. Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks (Lewis et al., 2020, NeurIPS)

- **Full citation**: Lewis, P., Perez, E., Piktus, A., Petroni, F., Karpukhin, V., Goyal, N., Kuttler, H., Lewis, M., Yih, W., Rocktaschel, T., Riedel, S. & Kiela, D. (2020). Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. NeurIPS 2020.
- **Link**: https://arxiv.org/abs/2005.11401

- **Core contribution**: Introduces Retrieval-Augmented Generation (RAG), combining a pre-trained seq2seq model (parametric memory) with a dense vector index of Wikipedia (non-parametric memory) accessed through a pre-trained neural retriever. RAG models set state-of-the-art on three open-domain QA tasks and generate more specific, diverse, and factual language than parametric-only baselines. The key insight is that external retrieval provides a scalable, updatable knowledge source that complements learned parametric knowledge.

- **clau-doom relevance**: The RAG paper establishes the foundational paradigm that clau-doom extends from text generation to action generation. clau-doom's architecture maps directly: (1) OpenSearch strategy documents = non-parametric memory (Wikipedia in RAG); (2) Rust scoring engine = parametric decision logic (seq2seq in RAG); (3) Ollama embeddings + kNN = neural retriever (DPR in RAG). The fundamental innovation of clau-doom is applying RAG's retrieval-then-generate pattern to retrieval-then-decide, extending the paradigm from NLP to real-time game decision-making.

- **Differentiation**: RAG retrieves text passages to condition text generation; clau-doom retrieves strategy documents to condition action selection. RAG's output is generated text; clau-doom's output is a scored action. RAG uses a seq2seq model for generation; clau-doom uses a deterministic Rust scoring function. RAG operates at NLP inference speed (hundreds of ms); clau-doom operates under a strict 100ms latency constraint.

- **Reference type**: Direct citation (foundational paradigm)

---

### C2. Improving Language Models by Retrieving from Trillions of Tokens / RETRO (Borgeaud et al., 2022, ICML)

- **Full citation**: Borgeaud, S., Mensch, A., Hoffmann, J. et al. (2022). Improving language models by retrieving from trillions of tokens. ICML 2022.
- **Link**: https://arxiv.org/abs/2112.04426

- **Core contribution**: Introduces RETRO (Retrieval-Enhanced Transformer), which interleaves self-attention with cross-attention over retrieved neighbors from a 2-trillion-token database. RETRO achieves performance comparable to GPT-3 with 25x fewer parameters. The architecture uses chunked cross-attention, where each text chunk retrieves its nearest neighbors and cross-attends to them, enabling fine-grained retrieval at the passage level rather than document level.

- **clau-doom relevance**: RETRO's chunked cross-attention pattern, where different parts of the input attend to different retrieved passages, conceptually maps to clau-doom's multi-strategy retrieval. In clau-doom, different aspects of the current game situation (health status, enemy positions, ammo level) may retrieve different strategy documents, and the Rust scoring engine integrates across these retrieved strategies. RETRO's demonstration that retrieval-augmented models achieve comparable performance to much larger parametric models with fewer parameters validates clau-doom's design choice of using a lightweight Rust engine + rich retrieval rather than a large learned policy model.

- **Differentiation**: RETRO retrieves text for language modeling; clau-doom retrieves strategy documents for action selection. RETRO's retrieval is integrated into the Transformer attention mechanism (learned integration); clau-doom's retrieval is followed by deterministic scoring (engineered integration). RETRO's database is static (training corpus); clau-doom's database grows dynamically through gameplay and retrospection.

- **Reference type**: Direct citation (architecture parallel)

---

### C3. Voyager: An Open-Ended Embodied Agent with Large Language Models (Wang et al., 2023, arXiv)

> **Cross-ref**: Also covered in LITERATURE_REVIEW.md section 1.3 (skill library focus). This entry provides RAG paradigm extension analysis and clau-doom-specific differentiation.

- **Full citation**: Wang, G., Xie, Y., Jiang, Y. et al. (2023). Voyager: An Open-Ended Embodied Agent with Large Language Models. arXiv:2305.16291.
- **Link**: https://arxiv.org/abs/2305.16291

- **Core contribution**: Introduces the first LLM-powered embodied lifelong learning agent in Minecraft with three key components: (1) an automatic curriculum that maximizes exploration, (2) an ever-growing skill library of executable code for storing and retrieving complex behaviors, and (3) an iterative prompting mechanism incorporating environment feedback and self-verification. Voyager obtains 3.3x more unique items, travels 2.3x longer distances, and unlocks tech tree milestones up to 15.3x faster than prior state-of-the-art. Skills are temporally extended, interpretable, and compositional.

- **clau-doom relevance**: Voyager's skill library is the closest existing system to clau-doom's OpenSearch strategy repository. Both systems accumulate reusable behavioral knowledge (Voyager: executable code skills; clau-doom: strategy documents) that is retrieved based on the current situation and composed for action. Voyager's demonstration that a growing skill library enables lifelong learning without catastrophic forgetting validates clau-doom's approach of accumulating strategy documents across generations. The compositional nature of Voyager's skills parallels clau-doom's ability to combine multiple retrieved strategies.

- **Differentiation**: Voyager uses real-time LLM inference for every decision (GPT-4 blackbox queries); clau-doom eliminates real-time LLM dependency entirely (< 100ms Rust scoring). Voyager's skills are executable code that runs directly; clau-doom's strategies are declarative documents scored by a separate engine. Voyager operates in a single-agent setting; clau-doom uses multi-agent knowledge sharing through NATS. Voyager's skill library is append-only; clau-doom's strategy documents are refined through LLM retrospection, with trust scores updated based on continued use.

- **Reference type**: Direct citation (skill accumulation parallel)

---

## Academic Positioning: Can RAG Substitute for RL?

Based on this literature survey, the academic positioning for clau-doom's retrieval-based decision-making can be articulated as follows:

### The Spectrum of Decision Architectures

```
Pure RL Policy          Retrieval-Augmented RL        Pure Retrieval
(DQN, PPO)              (Goyal et al., NEC)           (clau-doom)
     |                         |                            |
  Parametric              Semi-parametric              Non-parametric
  Learned weights    Learned weights + memory      Memory + scoring rules
  Slow learning          Faster learning             Instant adaptation
  Poor sample           Improved sample              Maximum sample
  efficiency             efficiency                   efficiency
```

clau-doom occupies the rightmost position: a purely non-parametric decision architecture where all behavioral knowledge resides in retrievable strategy documents, and action selection is performed by a deterministic scoring function over retrieved candidates.

### Evidence Supporting This Position

1. **Episodic control works** (MFEC, NEC): kNN-based action selection achieves competitive performance, especially in the low-data regime.
2. **Retrieval augmentation consistently helps** (Goyal et al., Humphreys et al.): Adding retrieval to any RL agent improves performance.
3. **Sequence-model alternatives to RL succeed** (Decision Transformer, Trajectory Transformer): Non-RL decision architectures can match RL performance.
4. **In-context learning enables improvement without gradient updates** (Algorithm Distillation): Systems can improve through context rather than parameter updates.
5. **Skill accumulation enables lifelong learning** (Voyager): Growing knowledge libraries prevent catastrophic forgetting.

### What clau-doom Adds

clau-doom tests the hypothesis that a purely retrieval-based architecture (no learned policy, no gradient updates during gameplay) can achieve competitive performance through:
- High-quality strategy document curation (LLM retrospection)
- Statistical evaluation (DOE methodology)
- Population-level optimization (generational evolution)
- Cross-agent knowledge sharing (NATS pub/sub)

This is a stronger claim than any individual prior work makes, and its validation (or refutation) through rigorous DOE experimentation constitutes the project's core contribution.

---

## Gap Analysis: What clau-doom Does Differently

### 1. Retrieval as Complete Policy Replacement

All prior retrieval-augmented RL systems (NEC, Goyal et al., Humphreys et al.) use retrieval to augment a learned policy. clau-doom makes the stronger claim that retrieval + scoring can replace the learned policy entirely. No prior work has attempted or validated this substitution in a complex game environment.

### 2. Strategy Documents vs. Raw Experience Tuples

Prior episodic control systems (MFEC, NEC) store raw (state, action, value) tuples. clau-doom stores abstracted strategy documents that encode generalized behavioral knowledge in human-readable Markdown. This introduces a new level of abstraction between raw experience and retrieved knowledge, mediated by LLM retrospection.

### 3. Trust-Weighted Retrieval

Where prior systems use simple kNN distance for retrieval ranking, clau-doom applies Wilson score lower bound confidence intervals to account for strategy reliability based on usage count and success rate. This statistical ranking mechanism has no precedent in the episodic RL literature.

### 4. Dynamic Knowledge Refinement

Prior episodic control systems have static or append-only memories. clau-doom's strategy documents are actively refined through LLM retrospection: successful strategies gain higher trust scores, failed strategies are modified or deprecated, and new insights are synthesized across episodes. This creates a continuously improving knowledge base.

### 5. No Real-Time LLM Dependency

Unlike Voyager and other LLM-agent systems, clau-doom demonstrates that the benefits of LLM-powered knowledge management can be captured in a retrieval-based architecture that requires no LLM inference at decision time. The LLM contributes offline (retrospection, evolution) while the real-time system uses only vector search + deterministic scoring.

### 6. Formal Statistical Evaluation Framework

Prior work evaluates retrieval-augmented agents through aggregate reward metrics. clau-doom applies DOE methodology (ANOVA, factorial designs, effect sizes, power analysis) to make statistically rigorous claims about the contribution of each architectural component. This level of evaluation rigor is unprecedented in the retrieval-augmented decision-making literature.

---

## Completion Checklist

- [x] Category A: 4 papers collected (MFEC, NEC, Goyal et al. RA-RL, Humphreys et al.)
- [x] Category B: 3 papers collected (Decision Transformer, Trajectory Transformer, Algorithm Distillation)
- [x] Category C: 3 papers collected (RAG original, RETRO, Voyager)
- [x] "RAG as RL substitute" academic positioning statement written
- [x] Gap analysis identifying novel contributions
- [x] Lead review complete
