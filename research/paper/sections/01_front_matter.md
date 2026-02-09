# Front Matter: Movement Is All You Need

**File**: `research/paper/sections/01_front_matter.md`
**Sections**: Abstract, Introduction, Related Work
**Target Venue**: NeurIPS 2026
**Last Updated**: 2026-02-09

---

## Abstract
\label{sec:abstract}

We apply Design of Experiments (DOE) methodology --- factorial designs, ANOVA with residual diagnostics, and effect size quantification --- to systematically optimize FPS game agents in VizDoom's \texttt{defend\_the\_line} scenario. Across 29 experiments totaling 5,010 episodes, we test the hypothesis that a multi-level RAG architecture improves agent performance through document quality and scoring accuracy. Three independent experiments falsify this hypothesis: $F(3,116)=28.05$ with L2 conditions indistinguishable from L0 baselines ($p=0.929$, DOE-022), decision mode producing no effect on kills ($p=0.393$, DOE-024), and RAG selection indistinguishable from fixed strategies ($p=0.935$, DOE-026). Instead, we discover that lateral movement is the sole performance determinant ($F(1,116)=58.40$, $p<0.001$, $\eta_p^2=0.332$, Cohen's $d=1.408$), with all tactical variations --- attack ratio, temporal structure, health override, and strategy selection --- producing null effects. We identify rate-time compensation ($\text{kills} \approx k_r \times t_{\text{surv}}$, within movement class) as a fundamental environment constraint explaining why tactical optimization is futile. Our 83 statistically rigorous findings demonstrate that systematic DOE methodology reveals structural constraints that ad-hoc reinforcement learning tuning would likely miss, and that negative results carry substantial value for the game AI community.

---

## 1. Introduction
\label{sec:intro}

### 1.1 The Game AI Optimization Problem

Autonomous game agents have become a prominent testbed for artificial intelligence research, with first-person shooter (FPS) environments presenting particular challenges in real-time decision-making under uncertainty \cite{kempka2016vizdoom}. The dominant paradigm for optimizing game agents relies on deep reinforcement learning (RL), where agents learn policies through trial-and-error interaction with the environment \cite{mnih2015human, schulman2017proximal}. While RL has achieved remarkable results in controlled settings, the practical optimization of game agents typically involves ad-hoc hyperparameter tuning --- manual or grid-based searches over learning rates, network architectures, reward shaping coefficients, and exploration schedules.

This ad-hoc approach suffers from three fundamental limitations. First, it is statistically inefficient: grid search scales exponentially with the number of factors, while random search provides no principled decomposition of which factors actually matter \cite{bergstra2012random}. Second, it produces publication bias toward positive results --- researchers report configurations that work but rarely characterize the boundaries of failure or identify fundamental constraints that render entire classes of optimization futile. Third, it conflates correlation with causation: when a particular configuration outperforms others, the attribution of improvement to specific factors remains ambiguous without controlled experimental design.

An alternative methodology exists in quality engineering and industrial statistics: Design of Experiments (DOE). Originating with Fisher's agricultural experiments and formalized through factorial designs, ANOVA, and Response Surface Methodology \cite{montgomery2017doe}, DOE provides a principled framework for decomposing complex systems into orthogonal factor dimensions, quantifying main effects and interactions, and establishing statistically rigorous claims about which factors matter and how much. Despite its proven effectiveness in manufacturing and process optimization, DOE methodology remains remarkably underutilized in machine learning research \cite{bouthillier2021accounting}.

### 1.2 Our Approach: DOE for Game AI

We apply formal DOE methodology to the optimization of FPS game agents in VizDoom \cite{kempka2016vizdoom}. Rather than searching for the best configuration, we seek to understand the causal structure of performance: which factors contribute meaningfully, which are irrelevant, and what fundamental constraints the environment imposes on agent performance.

Our experimental framework follows a structured phase progression adapted from quality engineering practice:

- **Phase 0 (Screening)**: One-Factor-At-a-Time (OFAT) designs to identify candidate factors with large effects.
- **Phase 1 (Factorial Analysis)**: Full and fractional factorial designs ($2^k$, multi-level) to quantify main effects, detect interactions, and identify the environment's performance structure.
- **Phase 2 (Hypothesis Testing)**: Targeted experiments to test the core architectural hypothesis through independent replications.
- **Phase 3 (Constraint Discovery)**: Fine-grained exploration of discovered constraints, including parametric sweeps and boundary-condition analysis.

Each experiment employs fixed seed protocols for reproducibility, full ANOVA with residual diagnostics (normality, equal variance, independence), effect size quantification (partial $\eta^2$, Cohen's $d$, 95\% confidence intervals), and a trust-scoring framework that classifies findings as HIGH, MEDIUM, LOW, or UNTRUSTED based on statistical evidence quality. This produces a complete audit trail from hypothesis through experimental design, execution, analysis, and finding adoption.

### 1.3 Architecture and Initial Hypothesis

We implement a four-level hierarchical agent architecture for VizDoom's \texttt{defend\_the\_line} scenario:

- **L0 (Hardcoded rules)**: Reflex-based responses with $<1$ms latency, including emergency behaviors triggered by low health or proximity.
- **L1 (DuckDB cache)**: Episode-level pattern cache with $<10$ms lookup, providing access to frequently encountered tactical situations from recent play history.
- **L2 (OpenSearch kNN)**: Strategy document retrieval via $k$-nearest neighbor vector search with $<100$ms latency, drawing from a curated repository of tactical knowledge.
- **L3 (Claude Code retrospection)**: Offline between-episode analysis using a large language model for reflective learning. Critically, L3 operates only between episodes and introduces no real-time latency during gameplay.

This architecture is motivated by the core thesis:

$$\text{Agent Skill} = f(\text{DocQuality}, \text{ScoringAccuracy})$$

\noindent which proposes that agent performance improves monotonically with (1) the quality of strategy documents available for retrieval and (2) the accuracy of the scoring function that selects among retrieved strategies. If correct, this thesis implies that systematic improvement of the RAG pipeline --- better embeddings, more relevant documents, more discriminating scoring --- should yield corresponding performance gains. This would validate a knowledge-engineering approach to game AI as a complement or alternative to end-to-end RL.

### 1.4 What We Actually Found

Through 29 systematic experiments spanning 5,010 episodes, we discovered that the core thesis is false. Specifically:

1. **Triple independent falsification of the RAG hypothesis.** Three experiments testing L2 knowledge retrieval under different conditions (coarse tactic mapping, meta-strategy selection, and expanded action space) all produced null results. L2 retrieval provided no measurable benefit over simple heuristic baselines, with effect sizes indistinguishable from zero ($\eta_p^2 < 0.01$ in all three tests).

2. **Movement as the sole performance determinant.** Across all 29 experiments, the presence of lateral movement in the action space was the only factor that produced a large, statistically significant effect on total kills ($F(1,116)=58.40$, $p<0.001$, $d=1.408$). All other factors --- attack ratio, temporal pattern, health override, strategy selection, document quality, and agent parameters --- produced null effects.

3. **Rate-time compensation as a fundamental constraint.** We discover that within a movement class (movers or non-movers), total kills are governed by the relationship $\text{kills} \approx k_r \times t_{\text{surv}}$, where the kill rate $k_r$ remains approximately constant regardless of tactical decisions. Agents that attack less frequently survive longer but kill at the same rate per unit time, yielding the same total kills. This compensation mechanism explains why all tactical variations are futile.

4. **Environment dominance over architecture.** Variance decomposition across all experiments reveals that environmental difficulty (\texttt{doom\_skill}) explains 49\% of kill variance, movement explains 33\%, and all agent architectural parameters collectively explain less than 5\%. The remaining variance is attributable to stochastic episode variation.

### 1.5 Contributions

Our contributions are as follows:

1. **Methodological.** We present the first application of formal DOE methodology (factorial designs, ANOVA, RSM, split-plot) to FPS game AI optimization, demonstrating its effectiveness for discovering fundamental constraints that ad-hoc tuning would likely miss.

2. **Empirical.** We report the results of 29 DOEs comprising 5,010 episodes and producing 83 statistically rigorous findings with complete audit trails, fixed seed protocols, and trust-level classifications --- to our knowledge, the largest systematic experimental campaign in VizDoom research.

3. **Theoretical.** We identify rate-time compensation as a fundamental environment constraint in \texttt{defend\_the\_line}: within a movement class, $\text{kills} \approx k_r \times t_{\text{surv}}$ with $k_r$ approximately constant, rendering all tactical optimization futile.

4. **Negative result.** We provide rigorous falsification of the hypothesis that RAG-based knowledge retrieval improves FPS agent performance, through three independent null results with adequate statistical power. Negative results of this quality carry substantial value for the community by preventing wasted effort on architecturally complex solutions to problems that do not exist.

### 1.6 Paper Organization

Section~\ref{sec:related} reviews related work in LLM-based game agents, VizDoom research, and DOE methodology in machine learning. Section~\ref{sec:method} describes our experimental framework, agent architecture, and statistical protocols. Section~\ref{sec:results} presents results across four experimental phases: infrastructure validation and screening (DOE-001--020), hypothesis falsification (DOE-022/024/026), rate-time compensation discovery (DOE-027/028), and movement dominance confirmation (DOE-029). Section~\ref{sec:analysis} analyzes the rate-time compensation model and information-theoretic constraints. Section~\ref{sec:discussion} discusses implications, limitations, and future directions.

---

## 2. Related Work
\label{sec:related}

### 2.1 LLM-Based Game Agents

Recent work has explored large language models as components of autonomous game agents. \citet{dewynter2024doom} applied GPT-4 directly to VizDoom via screenshot-to-text conversion, but encountered prohibitive latency ($\sim$60 seconds per frame) and was unable to complete any scenario --- a result that underscores the impracticality of real-time LLM inference for FPS gameplay. Reflexion \cite{shinn2023reflexion} introduced verbal reinforcement learning with episodic memory and natural language self-reflection, demonstrating learning improvements on text-based and simple visual tasks, and providing the conceptual foundation for our L3 retrospection layer. Voyager \cite{wang2023voyager} implemented a lifelong learning agent for Minecraft that accumulates a skill library through LLM-driven exploration, representing a structural analog to our OpenSearch strategy repository. RL-GPT \cite{zhai2024rlgpt} proposed hierarchical separation of LLM reasoning (slow, strategic) from RL execution (fast, tactical), an architecture conceptually similar to our four-level hierarchy. DEPS \cite{wang2024deps} introduced a describe-explain-plan-select framework for Minecraft that shares our emphasis on structured decision decomposition.

Our work differs from these approaches in two key respects. First, we use the LLM exclusively for offline retrospection (L3), eliminating real-time latency entirely. Second, rather than demonstrating that LLM-augmented agents can succeed, we rigorously test whether knowledge retrieval (L2) provides any benefit, ultimately falsifying this hypothesis.

### 2.2 VizDoom and Deep RL for FPS

VizDoom \cite{kempka2016vizdoom} has served as a standard benchmark for FPS game AI since its introduction, supporting scenarios ranging from basic navigation to full deathmatch. Deep RL approaches have achieved strong performance in VizDoom: \citet{lample2017playing} combined deep RL with game-feature prediction for navigation and combat, while subsequent work applied A3C, PPO, and IMPALA to various VizDoom scenarios \cite{dosovitskiy2017learning}. \citet{jaderberg2019human} demonstrated human-level performance in a Capture the Flag variant using population-based training with $\sim$450,000 agent-hours of experience. The annual VizDoom Competition has driven progress across navigation, known-map, and full deathmatch tracks.

A notable limitation of this body of work is its focus on end-to-end policy optimization without systematic factor analysis. Researchers typically report that a particular architecture or training procedure achieves a certain performance level, but do not decompose which architectural decisions actually matter or quantify their individual contributions. Our DOE-based approach fills this gap by providing ANOVA decomposition of factor effects with effect sizes, interaction detection, and residual diagnostics.

### 2.3 DOE and Statistical Rigor in Machine Learning

The application of DOE methodology to machine learning remains limited despite its potential. In hyperparameter optimization, Bayesian optimization \cite{snoek2012practical} and random search \cite{bergstra2012random} are standard, but these methods find optima without explaining why particular configurations succeed --- DOE provides the missing causal decomposition through ANOVA. \citet{bouthillier2021accounting} and \citet{henderson2018deep} highlighted persistent issues with statistical rigor in ML evaluation, including insufficient reporting of variance, absence of effect sizes, and lack of proper hypothesis testing. Quality engineering tools --- Statistical Process Control (SPC), Failure Mode and Effects Analysis (FMEA), and multi-criteria decision methods such as TOPSIS --- have been applied extensively in manufacturing \cite{montgomery2017doe} but remain almost entirely absent from ML research.

Our work demonstrates that DOE methodology can be directly applied to game AI optimization, revealing not only which factors are significant but also discovering fundamental constraints (rate-time compensation) that explain why large classes of optimization are futile. This is precisely the type of structural insight that ad-hoc tuning, Bayesian optimization, and standard RL training procedures are unlikely to produce.

---

<!-- REFERENCES (to be converted to BibTeX)

\bibitem{kempka2016vizdoom}
Kempka, M., Wydmuch, M., Runc, G., Toczek, J., and Jaskowski, W. (2016). ViZDoom: A Doom-based AI research platform for visual reinforcement learning. In IEEE Conference on Computational Intelligence and Games (CIG).

\bibitem{dewynter2024doom}
de Wynter, A. (2024). Can GPT Play Doom? GPT-4 and VizDoom. arXiv preprint.

\bibitem{shinn2023reflexion}
Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., and Yao, S. (2023). Reflexion: Language agents with verbal reinforcement learning. In Advances in Neural Information Processing Systems (NeurIPS), 36.

\bibitem{wang2023voyager}
Wang, G., Xie, Y., Jiang, Y., Mandlekar, A., Xiao, C., Zhu, Y., Fan, L., and Anandkumar, A. (2023). Voyager: An open-ended embodied agent with large language models. Transactions on Machine Learning Research (TMLR).

\bibitem{zhai2024rlgpt}
Zhai, Y., Tong, S., Li, X., Cai, M., Qu, Q., Lee, Y. J., and Ma, Y. (2024). Fine-tuning large vision-language models as decision-making agents via reinforcement learning. arXiv preprint arXiv:2405.10292.

\bibitem{wang2024deps}
Wang, Z., Cai, S., Chen, G., Liu, A., Ma, X., and Liang, Y. (2024). Describe, explain, plan and select: Interactive planning with large language models enables open-world multi-task agents. In Advances in Neural Information Processing Systems (NeurIPS), 37.

\bibitem{lample2017playing}
Lample, G. and Chaplot, D. S. (2017). Playing FPS games with deep reinforcement learning. In Proceedings of the AAAI Conference on Artificial Intelligence, 31(1).

\bibitem{dosovitskiy2017learning}
Dosovitskiy, A. and Koltun, V. (2017). Learning to act by predicting the future. In International Conference on Learning Representations (ICLR).

\bibitem{jaderberg2019human}
Jaderberg, M., Czarnecki, W. M., Dunning, I., et al. (2019). Human-level performance in 3D multiplayer games with population-based reinforcement learning. Science, 364(6443), 859--865.

\bibitem{montgomery2017doe}
Montgomery, D. C. (2017). Design and Analysis of Experiments (9th ed.). John Wiley \& Sons.

\bibitem{snoek2012practical}
Snoek, J., Larochelle, H., and Adams, R. P. (2012). Practical Bayesian optimization of machine learning algorithms. In Advances in Neural Information Processing Systems (NeurIPS), 25.

\bibitem{bergstra2012random}
Bergstra, J. and Bengio, Y. (2012). Random search for hyper-parameter optimization. Journal of Machine Learning Research, 13, 281--305.

\bibitem{bouthillier2021accounting}
Bouthillier, X., Delaunay, P., Bronzi, M., Trofimov, A., Nichyporuk, B., Szeto, J., Sepah, N., Raff, E., Madan, K., Voleti, V., Kahou, S. E., Michalski, V., Arbel, T., Pal, C., Varoquaux, G., and Vincent, P. (2021). Accounting for variance in machine learning benchmarks. In Proceedings of Machine Learning and Systems (MLSys), 3.

\bibitem{henderson2018deep}
Henderson, P., Islam, R., Bachman, P., Pineau, J., Precup, D., and Meger, D. (2018). Deep reinforcement learning that matters. In Proceedings of the AAAI Conference on Artificial Intelligence, 32(1).

\bibitem{mnih2015human}
Mnih, V., Kavukcuoglu, K., Silver, D., et al. (2015). Human-level control through deep reinforcement learning. Nature, 518(7540), 529--533.

\bibitem{schulman2017proximal}
Schulman, J., Wolski, F., Dhariwal, P., Radford, A., and Klimov, O. (2017). Proximal policy optimization algorithms. arXiv preprint arXiv:1707.06347.

-->
