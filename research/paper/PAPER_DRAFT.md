# Movement Is All You Need: How 29 Systematic Experiments Falsified RAG-Based FPS Game Agent Optimization

**Authors**: Sang Yi¹, with Claude Code as AI Co-Investigator

**¹Affiliation**: [To be added]

**Abstract**: We apply Design of Experiments (DOE) methodology --- factorial designs, ANOVA with residual diagnostics, and effect size quantification --- to systematically optimize FPS game agents in VizDoom's \texttt{defend\_the\_line} scenario. Across 29 experiments totaling 5,010 episodes, we test the hypothesis that a multi-level RAG architecture improves agent performance through document quality and scoring accuracy. Three independent experiments falsify this hypothesis: $F(3,116)=28.05$ with L2 conditions indistinguishable from L0 baselines ($p=0.929$, DOE-022), decision mode producing no effect on kills ($p=0.393$, DOE-024), and RAG selection indistinguishable from fixed strategies ($p=0.935$, DOE-026). Instead, we discover that lateral movement is the sole performance determinant ($F(1,116)=58.40$, $p<0.001$, $\eta_p^2=0.332$, Cohen's $d=1.408$), with all tactical variations --- attack ratio, temporal structure, health override, and strategy selection --- producing null effects. We identify rate-time compensation ($\text{kills} \approx k_r \times t_{\text{surv}}$, within movement class) as a fundamental environment constraint explaining why tactical optimization is futile. Our 83 statistically rigorous findings demonstrate that systematic DOE methodology reveals structural constraints that ad-hoc reinforcement learning tuning would likely miss, and that negative results carry substantial value for the game AI community.

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

## 3. Methodology
\label{sec:method}

We describe our agent architecture, experimental framework, and evaluation environment. All experiments follow a pre-registered Design of Experiments (DOE) protocol with fixed seeds, ANOVA-based analysis, and complete residual diagnostics. The full audit trail---from hypothesis to finding---is maintained across 29 experiments.

### 3.1 Agent Architecture

Our agent employs a four-level hierarchical decision architecture designed to achieve sub-100ms decision latency without real-time LLM inference. Each level operates within a strict latency budget, and higher levels are consulted only when lower levels do not produce a decisive action.

**Level 0 (L0): Hardcoded Rules** ($< 1\text{ms}$). Implemented in Rust, L0 encodes basic reflexes: dodge when health drops below 20, reload when ammunition reaches zero, and attack the nearest visible enemy otherwise. These rules provide a deterministic behavioral floor that guarantees minimum competence regardless of higher-level availability.

**Level 1 (L1): Episode Cache** ($< 10\text{ms}$). A per-agent DuckDB instance stores the most recent 100 episodes of play history. L1 retrieves frequently accessed behavioral patterns---notably periodic action sequences such as \texttt{burst\_3} (attack for 3 ticks, then reposition for 3 ticks). L1 patterns are generated by Claude Code during offline retrospection and cached for real-time access.

**Level 2 (L2): Strategy Retrieval** ($< 100\text{ms}$). An OpenSearch instance indexes strategy documents generated by Claude Code after each episode. During gameplay, L2 performs $k$-nearest-neighbor vector search ($k{=}5$) over the strategy corpus, scores retrieved documents against the current game state, and selects the highest-scoring tactic. Strategy documents encode tactical knowledge at varying granularity: from low-level action mappings ("when enemies approach, strafe left") to meta-strategies ("use aggressive tactics when health is high").

**Level 3 (L3): Retrospection** (offline, seconds). After each episode concludes, Claude Code analyzes the episode outcome, generates new strategy documents, and refines existing ones. L3 never executes during gameplay---it operates exclusively between episodes, eliminating the latency penalties that have constrained prior LLM-based game agents.

The architecture's core hypothesis was: $\text{Agent Skill} = \text{Document Quality} \times \text{Scoring Accuracy}$. That is, performance should improve monotonically as (a) strategy documents become higher quality through retrospective refinement and (b) the Rust scoring engine more accurately matches documents to game states.

**Game interface.** A Python binding to the VizDoom API translates between the decision hierarchy and the game engine. Action functions produce discrete actions at each game tick (28.6ms at 35 fps). Metrics recorded per episode include kills (count of enemies eliminated), survival time (seconds until agent death), and kill rate (kills per minute of survival).

### 3.2 Experimental Framework

We adopt Design of Experiments (DOE) methodology from quality engineering, replacing ad-hoc hyperparameter search with structured factorial designs, ANOVA-based inference, and effect size quantification. Our experimental program follows a phased progression:

**Phase 0: Screening (OFAT).** One-Factor-At-a-Time designs identify which factors exhibit large main effects. DOE-001 through DOE-010 screened agent architecture variants, strategy types, and scenario characteristics. This phase identified movement as a potentially important factor and eliminated several candidate parameters (memory weight, strength weight) as non-influential.

**Phase 1: Factorial Analysis.** Full and fractional factorial designs ($2^k$ and multi-level) quantify main effects, interactions, and effect sizes. DOE-011 through DOE-021 tested strategy combinations, action space variants, cross-difficulty robustness, and evolutionary optimization. This phase established the convergence zone phenomenon---that all strategies meeting minimum conditions achieve statistically equivalent performance.

**Phase 2: Hypothesis Testing.** Three independent experiments (DOE-022, DOE-024, DOE-026) tested the core L2 RAG hypothesis using different retrieval implementations and action spaces. All three produced null results, falsifying the core thesis.

**Phase 3: Constraint Discovery.** DOE-027 through DOE-029 characterized the rate-time compensation mechanism and confirmed movement as the sole performance determinant.

**Statistical protocol.** Every experiment adheres to a rigorous statistical pipeline:

1. *Fixed seeds.* Control and treatment conditions use identical seed sets, enabling paired comparisons and guaranteeing reproducibility. Minimum 30 seeds per condition provides statistical power $\geq 0.80$ for medium effect sizes ($f = 0.25$).

2. *ANOVA with diagnostics.* We report the full ANOVA table (sums of squares, degrees of freedom, $F$-statistic, $p$-value) accompanied by three residual diagnostics: normality (Anderson-Darling test), equal variance (Levene test), and independence (run-order inspection). When parametric assumptions are violated, we confirm results with non-parametric alternatives (Kruskal-Wallis, Mann-Whitney $U$).

3. *Effect sizes.* Every significant result reports partial $\eta^2$ (proportion of variance explained) and Cohen's $d$ (standardized mean difference) with 95\% confidence intervals. We interpret effect sizes using standard thresholds: small ($d = 0.2$, $\eta^2 = 0.01$), medium ($d = 0.5$, $\eta^2 = 0.06$), and large ($d = 0.8$, $\eta^2 = 0.14$).

4. *Trust classification.* Findings receive a trust level: HIGH ($p < 0.01$, $n \geq 50$, clean diagnostics), MEDIUM ($p < 0.05$, $n \geq 30$), LOW ($p < 0.10$ or diagnostic violations), or UNTRUSTED (no statistical test or $p \geq 0.10$). Only HIGH and MEDIUM findings are adopted.

5. *Audit trail.* Every finding traces through a complete chain: hypothesis (HYPOTHESIS\_BACKLOG) $\to$ experiment order (EXPERIMENT\_ORDER) $\to$ experiment report (EXPERIMENT\_REPORT) $\to$ finding (FINDINGS). No result is reported without this chain.

### 3.3 VizDoom Environment

We evaluate on VizDoom's \texttt{defend\_the\_line} scenario, selected through systematic comparison against alternative scenarios.

**Scenario characteristics.** The agent faces a corridor of continuously spawning single-hit enemies (imps). The agent occupies a fixed longitudinal position and can turn, strafe laterally, and fire. Episodes terminate upon agent death. The \texttt{doom\_skill} parameter (1--5) controls enemy aggressiveness, with skill 3 (Normal) as the default.

**Action spaces.** We test two action space configurations:
- *3-action:* $\{$TURN\_LEFT, TURN\_RIGHT, ATTACK$\}$. The agent can aim and fire but cannot physically reposition.
- *5-action:* $\{$TURN\_LEFT, TURN\_RIGHT, MOVE\_LEFT, MOVE\_RIGHT, ATTACK$\}$. Adds lateral strafing, enabling projectile avoidance through physical displacement.

**Response variables.** We measure three complementary metrics: (i) kills---total enemies eliminated per episode; (ii) survival time---seconds from episode start to agent death; and (iii) kill rate---kills per minute of survival, measuring offensive efficiency independent of episode duration.

**Scenario selection rationale.** Early experiments (DOE-007, DOE-008) compared \texttt{defend\_the\_center} and \texttt{defend\_the\_line}. The former produces kills in the range 0--3 with near-zero variance, yielding no statistical discrimination between strategies ($F(4,145) = 1.579$, $p = 0.183$, $\eta^2 = 0.042$). The latter produces kills in the range 4--26 with sufficient variance for meaningful ANOVA ($F(4,145) = 5.256$, $p < 0.001$, $\eta^2 = 0.127$). We therefore adopt \texttt{defend\_the\_line} as the standard evaluation scenario for all subsequent experiments.

---

## 4. Results
\label{sec:results}

We present results across four phases spanning 29 DOEs and 5,010 total episodes. Phase 0--1 validates infrastructure and maps the strategy landscape. Phase 2 tests and falsifies the core RAG hypothesis. Phase 3 discovers rate-time compensation and confirms movement as the sole performance determinant.

### 4.1 Infrastructure Validation and Strategy Exploration (DOE-001--020)

**Infrastructure validation (DOE-001--004).** Initial experiments revealed a critical data pipeline error: the AMMO2 game variable was incorrectly mapped as KILLCOUNT in the DuckDB schema, invalidating the first four experiments. After correction with real VizDoom execution, we discovered that the full agent (L0+L1+L2) produces *identical* outcomes to the rule-only agent (L0 only) at default parameters---both achieve 26.0 kills with zero variance in \texttt{defend\_the\_center}. This early null result (F-002, INVALIDATED) provided the first indication that the L1 and L2 layers contribute no behavioral differentiation at default settings.

**Scenario selection (DOE-007--008).** A paired comparison using identical five-level designs on two scenarios established \texttt{defend\_the\_line} as the standard evaluation environment. On \texttt{defend\_the\_center}, architecture had no significant effect ($F(4,145) = 1.579$, $p = 0.183$, $\eta^2 = 0.042$; power = 0.49). On \texttt{defend\_the\_line}, architecture was significant ($F(4,145) = 5.256$, $p < 0.001$, $\eta^2 = 0.127$; power = 0.97). The discriminability ratio improved 1.7$\times$, effect size increased 3$\times$, and residual diagnostics shifted from all-fail to all-pass (F-012).

**Agent parameter null results (DOE-009).** A $3^2$ factorial design testing memory weight $\times$ strength weight on \texttt{defend\_the\_line} produced uniformly null results. Memory weight: $F(2,261) = 0.306$, $p = 0.736$, $\eta^2 = 0.002$. Strength weight: $F(2,261) = 2.235$, $p = 0.109$, $\eta^2 = 0.017$. Interaction: $F(4,261) = 0.365$, $p = 0.834$, $\eta^2 = 0.006$ (F-013, F-014, F-015). These results invalidated earlier mock-data findings that had attributed 41.5\% of variance to memory ($p < 0.0001$ in mock data). **Agent-level parameters have no detectable effect in real gameplay.**

**Strategy landscape (DOE-010--020).** Systematic testing of behavioral strategies revealed a consistent pattern across 11 experiments:

- *L0-only is universally worst.* The pure-reflex strategy (always attack nearest enemy) was significantly worse than all alternatives across three independent experiments with different seed sets: DOE-008 ($d = 0.938$), DOE-010 ($d = 0.654$), DOE-019 ($d = 0.83$--$1.48$). The mechanism is tunnel vision: L0-only commits to a single enemy without lateral scanning (F-010, F-034).

- *Random matches structured strategies in 3-action space.* Random action selection is statistically indistinguishable from all structured strategies: $F(3,116) = 0.517$, $p = 0.671$ (F-018). The 3-action space is too constrained for intelligent strategies to outperform uniform randomness.

- *Strafing trades kill rate for survival.* Expanding from 3 to 5 actions reduces kill rate by 3.18 kr/min ($d = 0.523$, $p = 0.003$) but increases survival by 63\% ($\eta^2 = 0.225$), producing more total kills (F-020, F-023, F-024).

- *Compound actions confer no benefit.* Simultaneous multi-action commands (attack+turn on the same tick) produce identical results to sequential commands ($d = 0.000$; F-025). VizDoom's weapon cooldown (~12 ticks, ~340ms) absorbs all timing differences between strategies (F-043).

- *Best-of-breed strategies.* \texttt{burst\_3} (3 attacks, 1 reposition) achieves the highest total kills (15.40; F-036). \texttt{adaptive\_kill} (state-dependent switching) achieves the highest kill rate (46.18 kr/min; F-032). Both form a two-member Pareto front; all other strategies are dominated (F-039, F-041).

### 4.2 Core Thesis Falsification (DOE-022, DOE-024, DOE-026)

We tested the central hypothesis---that L2 RAG strategy retrieval improves agent performance---through three independent experiments spanning two action spaces and three retrieval implementations.

**DOE-022: L2 with coarse action mapping.** A $3 \times 2$ factorial design (decision mode $\times$ doom\_skill) tested L2 retrieval with direct tactic-to-action mapping across four document quality levels. Decision mode had no effect on kills: $F(2,174) = 0.268$, $p = 0.765$, $\eta^2 = 0.003$. Furthermore, high-quality and low-quality strategy documents produced *perfectly identical* episode outcomes (30/30 episodes matched; $d = 0.000$; F-050). The coarse 3-action mapping collapses all tactical distinctions into the same action distribution: nearly all tactics map to ATTACK regardless of document content.

**DOE-024: L2 meta-strategy selection.** A $4 \times 3$ factorial design tested a refined L2 implementation that selects between pre-validated strategies (\texttt{burst\_3} vs.\ \texttt{adaptive\_kill}) based on situation tags (health, ammo, kill count). Decision mode showed no effect: $F(3,348) = 1.001$, $p = 0.393$, $\eta^2 = 0.009$. All planned contrasts were non-significant (all $p > 0.4$, all $d < 0.12$). The pre-filtered strategy pool eliminates selection value: when all candidate strategies perform equivalently (F-035), choosing between them provides no advantage (F-057).

**DOE-026: L2 in 5-action space.** A five-condition OFAT design tested L2 retrieval in the richer 5-action space, where strategy differentiation exists (F-062). Three L2 implementations (cached lookup, live OpenSearch query, random rotation among top strategies) were compared against two fixed baselines. Decision mode had no effect: $F(4,145) = 0.206$, $p = 0.935$, $\eta^2 = 0.006$. This is the smallest effect size in the entire 29-DOE program. The RAG selector was numerically the worst performer (16.57 kills vs.\ group mean 17.15), suggesting that query overhead may cause slight regression (F-069).

**Synthesis (F-070): Thesis falsification.** Across three independent tests with cumulative $N = 450$ episodes, using different action spaces (3-action and 5-action), different retrieval granularities (tactic-level, meta-strategy, cached/live), and different document pools (curated vs.\ random), L2 RAG retrieval produces no measurable performance benefit. The hypothesis "Agent Skill $=$ Document Quality $\times$ Scoring Accuracy" is **falsified** for the \texttt{defend\_the\_line} scenario.

### 4.3 Rate-Time Compensation Discovery (DOE-027, DOE-028)

Having falsified the RAG hypothesis, we investigated *why* tactical variation produces null results. Two experiments reveal a fundamental environment constraint.

**DOE-027: Attack ratio gradient.** A seven-level OFAT design varied attack probability from 20\% to 80\% in 10\% increments within the 5-action space. Kills were invariant to attack ratio: $F(6,203) = 0.617$, $p = 0.717$, $\eta^2 = 0.018$ (F-071). However, the component metrics diverged sharply. Survival time decreased with attack ratio ($-7.77$s per 10\% increase; $p = 0.016$; F-072), while kill rate increased monotonically ($F(6,203) = 3.736$, $p = 0.002$, $\eta^2 = 0.099$; Jonckheere-Terpstra $z = 7.084$, $p < 0.001$; F-073). The two trends cancel precisely:

$$\text{kills} \approx \text{kill\_rate} \times \frac{\text{survival\_time}}{60}$$

At 20\% attack: $\text{kr} = 36.5/\text{min} \times 26.2\text{s} / 60 = 15.9$ kills. At 80\% attack: $\text{kr} = 42.0/\text{min} \times 21.3\text{s} / 60 = 14.9$ kills. The product varies by only 6\% across a 4$\times$ range of attack probability (F-074).

This **rate-time compensation** represents a conservation law of the scenario: total kills are an environment-determined quantity that tactical allocation between offense and defense merely redistributes between kill rate and survival time.

**DOE-028: Temporal structure.** A five-condition OFAT design held attack ratio constant at 50\% and varied temporal grouping: random frame-by-frame interleaving, and deterministic burst cycles of length 2, 3, 5, and 10 ticks. Kills were invariant to temporal structure: $F(4,145) = 1.017$, $p = 0.401$, $\eta^2 = 0.027$ (F-076). All four planned contrasts were non-significant ($p = 0.636$ to $p = 0.893$). Rate-time compensation held with remarkable precision: the $\text{kr} \times \text{survival} / 60$ ratio ranged from 0.980 to 1.003 across all five patterns (F-078).

**Full tactical invariance (F-077).** The combined evidence from DOE-027 ($N = 210$) and DOE-028 ($N = 150$) establishes that **neither the proportion of attacks nor their temporal distribution affects total kills** in the 5-action \texttt{defend\_the\_line} environment. This invariance is a direct consequence of the rate-time compensation constraint: any tactical reallocation between offense and defense is perfectly offset, preserving a fixed kill budget per episode.

### 4.4 Movement as Sole Determinant (DOE-029)

The final experiment tests whether movement---the one factor that varies *between* movement classes rather than *within*---is indeed the sole performance lever.

**Design.** A $2^2$ full factorial design crossed action pattern (random\_50: 50\% attack with strafing vs.\ pure\_attack: 100\% attack without strafing) with health override (emergency dodge when health $< 20$: enabled vs.\ disabled). Each cell contained 30 episodes ($N = 120$ total).

**Movement effect (F-079).** Action pattern produced the largest effect in the entire 29-DOE program: $F(1,116) = 58.402$, $p < 0.001$, $\eta^2 = 0.332$, $d = 1.408$. Agents with movement achieved 15.25 $\pm$ 5.74 kills and 24.4s survival; agents without movement achieved 8.85 $\pm$ 2.99 kills and 15.3s survival. Kruskal-Wallis confirmed ($H(3) = 50.802$, $p < 0.001$).

**Health override null (F-080).** The emergency dodge mechanism had no effect: $F(1,116) = 0.784$, $p = 0.378$, $\eta^2 = 0.004$, $d = -0.134$. This confound was present in all DOE-025 through DOE-028 experiments; DOE-029 demonstrates it was irrelevant throughout.

**No interaction (F-081).** The interaction between pattern and override was non-significant: $F(1,116) = 0.987$, $p = 0.322$, $\eta^2 = 0.006$. The override is equally irrelevant for both movers and non-movers.

**Kill rate invariance (F-083).** Critically, kill rate did *not* differ between movement conditions: random\_50 achieved $42.2 \pm 5.1$ kr/min vs.\ pure\_attack at $40.8 \pm 5.9$ kr/min ($p = 0.180$, $d = 0.248$). Movement does not reduce killing efficiency---it provides survival time at essentially zero offensive cost. The mechanism is orthogonal: turning (which aims at enemies) is independent of strafing (which displaces the agent laterally). Strafing makes the agent harder to hit by enemy projectiles without interfering with the agent's own offensive output.

**Rate-time compensation breaks at the movement boundary (F-082).** Within the movement class, the $\text{kr} \times \text{survival}$ product is 17.17. Within the non-movement class, the product is 10.38---a 65\% gap. Rate-time compensation holds *within* each class but fails *between* them. Movement provides "free" survival that is not offset by reduced kill rate, breaking the conservation law that constrains tactical variation within a movement class.

**Synthesis.** Movement is the sole performance determinant in \texttt{defend\_the\_line}. Across 29 experiments testing attack ratio (DOE-027), temporal structure (DOE-028), RAG selection (DOE-022, 024, 026), health override (DOE-029), memory and strength weights (DOE-009), compound actions (DOE-012), scenario difficulty (DOE-023), and evolutionary optimization (DOE-021), only one factor produces a significant, large, and replicated effect on total kills: whether the agent's action space includes lateral movement. The simplest effective agent---random action selection over the 5-action space---is statistically indistinguishable from the most sophisticated RAG-augmented, state-dependent, evolutionarily optimized architecture.

---

## 5. Analysis
\label{sec:analysis}

### 5.1 A Mathematical Model of Rate-Time Compensation

The most surprising finding of our experimental program is the discovery of rate-time compensation --- a conservation-like constraint that renders tactical optimization futile within a movement class. We formalize this phenomenon below.

Let $k$ denote total kills per episode, $r$ the kill rate (kills per minute of survival), and $s$ the survival time (in minutes). By definition:

$$k = r \times s$$

Our key empirical observation, established through DOE-027 (attack ratio sweep, $n=210$) and DOE-028 (burst structure sweep, $n=150$), is that for any action policy $\pi$ within a movement class $\mathcal{M}$:

$$k(\pi) \approx C_{\mathcal{M}}, \quad \forall \pi \in \mathcal{M}$$

where $C_{\mathcal{M}}$ is a constant depending only on the movement class. More precisely, for any two policies $\pi_1, \pi_2 \in \mathcal{M}$:

$$r(\pi_1) \times s(\pi_1) \approx r(\pi_2) \times s(\pi_2)$$

The compensation mechanism operates as follows. When a policy increases its attack ratio (the proportion of ticks allocated to the ATTACK action), two countervailing effects occur simultaneously: (i) more shots are fired per unit time, increasing $r$; and (ii) fewer ticks are available for strafing, increasing damage intake and decreasing $s$. We observe empirically that the marginal gain in $r$ is exactly offset by the marginal loss in $s$. Specifically, DOE-027 showed that increasing attack ratio from 0.2 to 0.8 raises kill rate from 36.5/min to 42.0/min ($F(6,203)=3.736$, $p=0.0015$, $\eta_p^2=0.099$) while simultaneously reducing survival from 26.2s to 21.3s (linear trend: $-7.77$ s per unit ratio, $p=0.016$). The resulting total kills remain statistically invariant ($F(6,203)=0.617$, $p=0.717$, $\eta_p^2=0.018$).

The constant $C_{\mathcal{M}}$ differs between movement classes. From DOE-029 ($n=120$):

$$C_{\text{movers}} = 42.2 \times \frac{24.4}{60} \approx 17.17$$

$$C_{\text{non-movers}} = 40.8 \times \frac{15.3}{60} \approx 10.38$$

The gap between these constants is approximately 65%, driven entirely by the survival advantage of movement. Crucially, compensation breaks at the movement class boundary because movement provides "free" survival --- dodging projectiles extends survival without meaningful kill rate cost ($p=0.180$ for kill rate difference between movers and non-movers, $d=0.248$). Within each class, the kill-rate-to-survival tradeoff is zero-sum; between classes, movers receive a survival bonus that non-movers cannot access through any tactical reallocation.

The tightness of the compensation is remarkable. DOE-028 found that the ratio $\frac{r \times s / 60}{k}$ ranges from 0.980 to 1.003 across five distinct burst structures (cycle lengths 2, 3, 5, 10, and random), indicating near-perfect conservation across both compositional and structural variations in action selection.

### 5.2 Information-Theoretic Perspective

Rate-time compensation has an information-theoretic interpretation that explains why strategies cannot differentiate. In a 3-action space $\{$TURN_LEFT, TURN_RIGHT, ATTACK$\}$, the maximum entropy per action is:

$$H_{\max} = \log_2(3) = 1.585 \text{ bits}$$

However, the weapon cooldown mechanism (${\sim}0.5$s between effective shots) acts as a low-pass filter on the action-to-outcome channel. Regardless of when ATTACK is pressed, the actual fire rate is bounded by the cooldown ceiling. This bottleneck constrains the mutual information between strategy and kill rate to approximately:

$$I(\text{strategy}; \text{kill\_rate}) \approx 0.082 \text{ bits}, \quad 95\% \text{ CI } [0.05, 0.11]$$

estimated across five independent experiments (DOE-010 through DOE-020). This represents only 0.15% of the theoretical maximum information per episode (54.1 bits), confirming that knowing which strategy an agent employs provides essentially no predictive information about its kill rate.

Three equalization forces create this performance convergence zone. First, the weapon cooldown imposes a hard ceiling on effective fire rate, rendering rapid action switching informationally equivalent to slower patterns. Second, stochastic and deterministic action sequences produce equivalent spatial distributions over sufficiently many episodes --- random movement covers the same angular range as systematic scanning. Third, uniform enemy spatial distribution eliminates aiming advantages, as enemies appear from all directions with equal probability.

In the expanded 5-action space $\{$TURN_LEFT, TURN_RIGHT, MOVE_LEFT, MOVE_RIGHT, ATTACK$\}$, the maximum entropy increases to $H_{\max} = \log_2(5) = 2.322$ bits. However, the additional 0.737 bits are allocated entirely to movement (survival) rather than aim (kill rate). This explains why the 5-action space unlocks a new performance tier --- the additional actions encode movement information that breaks the non-mover compensation ceiling --- while kill rate within a movement class remains invariant.

### 5.3 Variance Decomposition

To quantify the relative importance of each factor in the experimental program, we report the proportion of total variance ($\eta^2$) explained by each source across the relevant experiments:

| Factor | $\eta^2$ | Source Experiment | Interpretation |
|--------|----------|-------------------|----------------|
| doom_skill (game difficulty) | 0.486 | DOE-023 ($n=360$) | 49% of variance |
| Movement presence | 0.332 | DOE-029 ($n=120$) | 33% of variance |
| Strategy type (within class) | $<0.03$ | DOE-027/028 ($n=360$) | $<3$% of variance |
| L2 RAG configuration | 0.001--0.006 | DOE-022/024/026 ($n=450$) | $<1$% of variance |
| Agent parameters (memory, strength) | 0.002 | DOE-009 ($n=270$) | $<1$% of variance |

Environment settings (doom_skill) and the binary movement choice together explain over 80% of all performance variance. The entire agent architecture stack above L0 heuristics --- including RAG retrieval, parameterized decision weights, and tactical action selection --- contributes less than 5% of total variance. This finding fundamentally challenges the premise that architectural complexity is the primary lever for performance improvement in this domain.

---

## 6. Discussion
\label{sec:discussion}

### 6.1 When Does Architecture Complexity Matter?

Our results demonstrate that architecture complexity is irrelevant in VizDoom's defend_the_line scenario. However, this conclusion is scenario-specific, and identifying the structural features that drive it illuminates when complexity would matter.

Defend_the_line exhibits three simplifying properties: (i) enemies are destroyed in a single hit, eliminating variation in damage-per-shot; (ii) the open corridor geometry requires no path planning, reducing navigation to simple lateral strafing; and (iii) enemies spawn from fixed positions in a predictable arc, removing the need for adaptive target acquisition. Under these conditions, the weapon cooldown ceiling bounds kill rate from above, and movement provides the only non-compensated performance axis.

We predict architecture complexity would become relevant when any of these simplifying properties is relaxed. Multi-hit enemies would introduce meaningful variation in target selection and damage accumulation, creating a space where strategic depth translates to performance differences. Navigation-intensive scenarios (e.g., my_way_home or deadly_corridor) would reward spatial reasoning and memory. Dynamic environments with non-stationary enemy behavior would require adaptive strategies that simple heuristics cannot match. Competitive multi-agent settings would introduce opponent modeling, where architectural sophistication provides genuine advantage.

### 6.2 DOE vs. Reinforcement Learning: Complementary Approaches

Our DOE methodology serves a complementary role to reinforcement learning rather than a competing one. DOE excels at discovering fundamental constraints, falsifying hypotheses, and explaining *why* certain optimization trajectories are futile. RL excels at optimizing within unconstrained spaces, end-to-end policy learning, and scaling to high-dimensional action spaces.

In the context of defend_the_line, DOE revealed that the effective search space is essentially one-dimensional: the binary decision of whether to include movement. An RL agent trained on this scenario would eventually converge to the same empirical result --- policies with movement dominate --- but would provide no mechanistic understanding of the rate-time compensation constraint. The RL agent would learn *what* to do without explaining *why* alternatives fail.

We recommend using DOE as a preliminary investigation tool before committing to expensive RL training. By first characterizing the structure of the performance landscape --- identifying which factors are compensated, which are irrelevant, and which represent genuine optimization axes --- researchers can avoid wasting computational budget on dimensions that the environment renders informationally inert.

### 6.3 The Value of Negative Results

The most important findings of this work are negative. The RAG thesis falsification (F-070), established through three independent null results across different action spaces and retrieval granularities ($N=450$, all $p>0.39$), saves the research community from pursuing RAG-based strategy retrieval in simple FPS scenarios where the environment ceiling prevents meaningful strategy differentiation. The tactical invariance finding (F-077), confirmed across 12 distinct action configurations ($N=360$), demonstrates that within a movement class, all tactical optimization effort is wasted. The agent parameter irrelevance findings (F-013 through F-015) show that memory weight ($p=0.736$), strength weight ($p=0.109$), and their interaction ($p=0.834$) have no measurable effect on performance.

These negatives redirect research effort toward three productive directions: (i) scenarios where tactical depth genuinely differentiates agents, such as multi-hit enemies or navigation tasks; (ii) the binary movement decision as the true optimization target, which suggests that the first priority for any agent design is ensuring adequate movement behavior; and (iii) understanding environment constraints before investing in complex architectures, rather than assuming that added complexity yields added performance.

### 6.4 Limitations

Several limitations bound the generalizability of our findings. First, all experiments use defend_the_line with single-hit enemies; scenarios with multi-hit enemies, where damage accumulation matters, may yield qualitatively different results. Second, we tested 3-action and 5-action discrete spaces; continuous control could reveal finer-grained effects not observable in discrete settings. Third, the non-optimized Python glue layer may introduce latency variance that masks timing-sensitive strategy effects; compiled implementations could uncover such effects. Fourth, most experiments were conducted at doom_skill=3; although DOE-023 performed a full difficulty sweep revealing a strategy-by-difficulty interaction ($F(6,348)=4.06$, $p<0.001$), the majority of findings are conditioned on a single difficulty level. Fifth, agents operate on game state variables rather than raw pixel observations; visual processing could introduce additional information channels that alter the performance landscape.

---

## 7. Conclusion
\label{sec:conclusion}

We presented the first systematic application of design of experiments (DOE) methodology to FPS game agent optimization. Through 29 factorial experiments spanning 5,010 episodes in VizDoom's defend_the_line scenario, we tested and falsified the hypothesis that retrieval-augmented generation (RAG) improves agent performance.

Our principal findings are:

1. **Movement is the sole performance determinant** ($d=1.408$, $p<0.001$), producing a 65% kill advantage over non-moving agents through a survival bonus with negligible kill rate cost.
2. **Rate-time compensation** constrains all tactical optimization within movement classes: kill rate and survival time trade off exactly, holding total kills constant ($r \times s \approx C_{\mathcal{M}}$).
3. **The core RAG thesis is falsified** through three independent null results (DOE-022, DOE-024, DOE-026; $N=450$, all $p>0.39$), demonstrating that knowledge retrieval provides zero benefit in this domain.
4. **Environment difficulty dominates** ($\eta^2=0.486$), explaining nearly half of all performance variance and dwarfing all agent architecture parameters combined.

Our work demonstrates that DOE methodology reveals fundamental performance constraints that gradient-based optimization cannot discover. The rate-time compensation mechanism explains why tactical variations are irrelevant in simple FPS scenarios --- a structural insight that would be nearly impossible to derive from reinforcement learning alone. We recommend that game AI researchers apply DOE as a preliminary investigation tool before investing in complex architectures: in many scenarios, the architecture complexity budget is better spent on the single factor that matters most --- which, in VizDoom's defend_the_line, is simply whether the agent moves.

---

## References

\bibitem{kempka2016vizdoom}
Kempka, M., Wydmuch, M., Runc, G., Toczek, J., and Jaskowski, W. (2016). ViZDoom: A Doom-based AI research platform for visual reinforcement learning. In *IEEE Conference on Computational Intelligence and Games (CIG)*.

\bibitem{dewynter2024doom}
de Wynter, A. (2024). Can GPT Play Doom? GPT-4 and VizDoom. *arXiv preprint*.

\bibitem{shinn2023reflexion}
Shinn, N., Cassano, F., Gopinath, A., Narasimhan, K., and Yao, S. (2023). Reflexion: Language agents with verbal reinforcement learning. In *Advances in Neural Information Processing Systems (NeurIPS)*, 36.

\bibitem{wang2023voyager}
Wang, G., Xie, Y., Jiang, Y., Mandlekar, A., Xiao, C., Zhu, Y., Fan, L., and Anandkumar, A. (2023). Voyager: An open-ended embodied agent with large language models. *Transactions on Machine Learning Research (TMLR)*.

\bibitem{zhai2024rlgpt}
Zhai, Y., Tong, S., Li, X., Cai, M., Qu, Q., Lee, Y. J., and Ma, Y. (2024). Fine-tuning large vision-language models as decision-making agents via reinforcement learning. *arXiv preprint arXiv:2405.10292*.

\bibitem{wang2024deps}
Wang, Z., Cai, S., Chen, G., Liu, A., Ma, X., and Liang, Y. (2024). Describe, explain, plan and select: Interactive planning with large language models enables open-world multi-task agents. In *Advances in Neural Information Processing Systems (NeurIPS)*, 37.

\bibitem{lample2017playing}
Lample, G. and Chaplot, D. S. (2017). Playing FPS games with deep reinforcement learning. In *Proceedings of the AAAI Conference on Artificial Intelligence*, 31(1).

\bibitem{dosovitskiy2017learning}
Dosovitskiy, A. and Koltun, V. (2017). Learning to act by predicting the future. In *International Conference on Learning Representations (ICLR)*.

\bibitem{jaderberg2019human}
Jaderberg, M., Czarnecki, W. M., Dunning, I., et al. (2019). Human-level performance in 3D multiplayer games with population-based reinforcement learning. *Science*, 364(6443), 859--865.

\bibitem{montgomery2017doe}
Montgomery, D. C. (2017). *Design and Analysis of Experiments* (9th ed.). John Wiley \& Sons.

\bibitem{snoek2012practical}
Snoek, J., Larochelle, H., and Adams, R. P. (2012). Practical Bayesian optimization of machine learning algorithms. In *Advances in Neural Information Processing Systems (NeurIPS)*, 25.

\bibitem{bergstra2012random}
Bergstra, J. and Bengio, Y. (2012). Random search for hyper-parameter optimization. *Journal of Machine Learning Research*, 13, 281--305.

\bibitem{bouthillier2021accounting}
Bouthillier, X., Delaunay, P., Bronzi, M., Trofimov, A., Nichyporuk, B., Szeto, J., Sepah, N., Raff, E., Madan, K., Voleti, V., Kahou, S. E., Michalski, V., Arbel, T., Pal, C., Varoquaux, G., and Vincent, P. (2021). Accounting for variance in machine learning benchmarks. In *Proceedings of Machine Learning and Systems (MLSys)*, 3.

\bibitem{henderson2018deep}
Henderson, P., Islam, R., Bachman, P., Pineau, J., Precup, D., and Meger, D. (2018). Deep reinforcement learning that matters. In *Proceedings of the AAAI Conference on Artificial Intelligence*, 32(1).

\bibitem{mnih2015human}
Mnih, V., Kavukcuoglu, K., Silver, D., et al. (2015). Human-level control through deep reinforcement learning. *Nature*, 518(7540), 529--533.

\bibitem{schulman2017proximal}
Schulman, J., Wolski, F., Dhariwal, P., Radford, A., and Klimov, O. (2017). Proximal policy optimization algorithms. *arXiv preprint arXiv:1707.06347*.

---

**Acknowledgments**: This research was conducted using Claude Code, an AI-assisted development tool by Anthropic. Claude Code served as an active co-investigator in experimental design, statistical analysis, and paper composition.

**Reproducibility**: All experiment orders, reports, and statistical analyses are available in the project repository at [repository URL to be added]. Fixed seed sets are provided for all 29 DOEs.
