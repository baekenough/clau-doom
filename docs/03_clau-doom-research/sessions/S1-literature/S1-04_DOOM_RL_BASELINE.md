# S1-04: Doom RL Baseline Literature Review

> **Session**: S1 (Literature Review)
> **Priority**: Medium
> **Dependencies**: None
> **Status**: Complete

---

## Objective

Collect quantitative performance baselines from existing RL-based Doom agents. These numbers serve as comparison points to evaluate clau-doom's RAG-based approach. If clau-doom claims "RAG replaces RL," we need concrete RL numbers to compare against.

---

## Category A: VizDoom Competition Winners

### A1. ViZDoom Competitions: Playing Doom from Pixels

- **Authors**: Marek Wydmuch, Michal Kempka, Wojciech Jaskowski
- **Venue**: IEEE Transactions on Games, 11(3), 248-259 (2019); arXiv:1809.03470
- **URL**: https://arxiv.org/abs/1809.03470

**Summary**: Comprehensive summary of three editions of the Visual Doom AI Competition (2016-2018), including detailed results tables, open-source implementations of both the competition framework and competitors, and an improved evaluation across 20 games.

**Competition Setup**:
- Track 1: Known single map, all agents fight each other simultaneously
- Track 2: Unknown maps (multiple), agents must generalize
- 2016: 12 matches x 10 minutes per track (2 hours total gameplay)
- 2017: 10 matches x 10 minutes per track, 10-second respawn delay

**2016 Competition Results**:

| Track | Place | Agent | Frags | F/D Ratio | Architecture |
|-------|-------|-------|-------|-----------|--------------|
| Track 1 | 1st | F1 (Facebook AI) | 559 | 1.35 | A3C + Curriculum Learning |
| Track 1 | 2nd | Arnold (CMU) | 413 | 1.90 | DRQN + Action-Navigation |
| Track 1 | 3rd | Clyde | 393 | 0.77 | DQN variant |
| Track 1 | 4th | TUHO | 312 | 0.67 | DQN variant |
| Track 2 | 1st | IntelAct (Intel Labs) | 297 | 3.08 | Direct Future Prediction |
| Track 2 | 2nd | Arnold (CMU) | 167 | 32.8 | DRQN + Action-Navigation |
| Track 2 | 3rd | TUHO | 73 | 0.66 | DQN variant |

**2017 Competition Results**:

| Track | Place | Agent | Frags | F/D Ratio | Architecture |
|-------|-------|-------|-------|-----------|--------------|
| Track 1 | 1st | Marvin | 248 | 1.16 | DQN-based |
| Track 1 | 2nd | Arnold2 | 245 | 0.84 | DRQN + Action-Navigation |
| Track 1 | 3rd | Axon | 215 | 0.77 | DQN variant |
| Track 1 | 5th | F1 | 164 | 0.57 | A3C + Curriculum Learning |
| Track 2 | 1st | Arnold4 | 275 | 1.25 | DRQN (improved) |
| Track 2 | 2nd | YanShi | 275 | 1.47 | DQN variant |
| Track 2 | 3rd | IntelAct | 241 | 0.89 | Direct Future Prediction |

**Key Observations**:
- Arnold had the best F/D ratio in 2016 Track 2 (32.8) due to extreme caution (few deaths)
- Arnold4 won 2017 Track 2 on tiebreaker: 0 suicides vs. YanShi's 2 suicides (both had 275 kills)
- F1 dominated 2016 but dropped to 5th in 2017, suggesting overfitting to specific conditions
- Track 2 (unknown maps) required stronger generalization; results were generally lower

**clau-doom Connection**:
- These frag scores and F/D ratios are the primary quantitative baselines for deathmatch scenarios
- clau-doom should be tested on equivalent deathmatch maps to enable direct comparison
- Arnold's navigation/action architecture split is conceptually similar to clau-doom's multi-level decision hierarchy

### A2. Playing FPS Games with Deep Reinforcement Learning (Arnold)

- **Authors**: Guillaume Lample, Devendra Singh Chaplot
- **Venue**: AAAI 2017; arXiv:1609.05521
- **URL**: https://arxiv.org/abs/1609.05521

**Summary**: Presents Arnold, a fully autonomous FPS agent using DRQN with separate navigation and action networks. The agent augments the RL objective with auxiliary game feature prediction (enemy detection, item presence) during training, which dramatically improves performance. Arnold placed 2nd in both tracks of the 2016 VizDoom competition.

**Architecture**:
- Navigation Network: Explores the map, picks up items, finds enemies
- Action Network (DRQN): Combat with detected enemies
- Automatic mode switching based on enemy detection
- Game feature augmentation during training (not at inference)

**Key Results**:
- Outperformed built-in AI and average human players in deathmatch
- Best kill-death ratio in the 2016 competition (1.90 Track 1, 32.8 Track 2)
- Training: several days on single GPU
- Reward shaping: +1 per kill, -1 per death, small penalties for damage/ammo loss

**clau-doom Connection**:
- Arnold's dual-network approach (navigation vs. action) validates clau-doom's multi-level decision hierarchy design (Level 0: reflexes, Level 1: cached patterns, Level 2: RAG strategies)
- Arnold requires extensive training (days); clau-doom aims for faster knowledge acquisition via RAG
- Arnold's game feature augmentation is analogous to clau-doom's structured game state representation

### A3. Training Agent for First-Person Shooter Game with Actor-Critic Curriculum Learning (F1)

- **Authors**: Yuxin Wu, Yuandong Tian
- **Venue**: ICLR 2017
- **URL**: https://openreview.net/forum?id=Hk3mPK5gg

**Summary**: Presents F1, the 2016 VizDoom Track 1 champion from Facebook AI Research. Uses A3C (Asynchronous Advantage Actor-Critic) combined with curriculum learning that progressively increases difficulty. Won 10 of 12 rounds in Track 1 with a score 35% higher than second place.

**Key Results**:
- 559 frags in Track 1 (35% above Arnold's 413)
- Won 10/12 rounds in 2016 Track 1
- Curriculum learning key to performance: direct A3C without curriculum failed to learn in complex scenarios
- A3C trained on progressively harder scenarios: empty map -> static enemies -> moving enemies -> full deathmatch

**clau-doom Connection**:
- F1's curriculum learning parallels clau-doom's DOE phase progression (simple -> complex factors)
- F1's pure RL approach required careful curriculum design; clau-doom's RAG approach could bypass this by retrieving relevant strategies directly
- F1's performance degradation from 2016 (1st) to 2017 (5th) suggests overfitting; clau-doom's cumulative knowledge approach may offer better generalization

---

## Category B: Deep RL for FPS Games

### B1. Learning to Act by Predicting the Future (IntelAct / Direct Future Prediction)

- **Authors**: Alexey Dosovitskiy, Vladlen Koltun
- **Venue**: ICLR 2017; arXiv:1611.01779
- **URL**: https://arxiv.org/abs/1611.01779

**Summary**: Introduces Direct Future Prediction (DFP), an approach that trains agents to predict the effect of different actions on future measurements (health, ammo, frags) rather than directly optimizing a reward signal. Won 2016 VizDoom Track 2 (unknown maps) as IntelAct.

**Architecture**:
- Sensory input: screen pixels
- Measurement stream: health, ammo, frag count
- Learns to predict future measurements conditioned on actions and goals
- Goal-parametric architecture allows flexible objective specification at test time

**Key Results**:
- Won 2016 Track 2 with 297 frags (F/D ratio 3.08)
- Superior generalization to unknown maps compared to DQN/A3C methods
- Training required millions of frames of interaction

**clau-doom Connection**:
- DFP's measurement prediction is conceptually related to clau-doom's structured game state representation
- DFP's superior generalization on unknown maps supports clau-doom's emphasis on generalizable strategies stored in RAG
- clau-doom's strategy documents could encode the kind of goal-conditioned knowledge that DFP learns implicitly

### B2. ViZDoom: A Doom-based AI Research Platform for Visual Reinforcement Learning

- **Authors**: Michal Kempka, Marek Wydmuch, Grzegorz Runc, Jakub Toczek, Wojciech Jaskowski
- **Venue**: IEEE Conference on Computational Intelligence and Games (CIG), 2016; arXiv:1605.02097
- **URL**: https://arxiv.org/abs/1605.02097

**Summary**: The foundational paper introducing VizDoom as an RL research platform. Describes the API, customizable scenarios, and provides baseline DQN results on basic scenarios.

**Standard Scenarios Defined**:
- **Basic**: Simple shoot-the-monster task, single room, one enemy
- **Defend the Center**: Agent stands in center, enemies approach from all directions
- **Deadly Corridor**: Navigate a corridor with enemies to reach a goal
- **Health Gathering**: Collect health packs to survive as long as possible
- **Health Gathering Supreme**: Harder version of Health Gathering
- **Deathmatch**: Full multi-agent combat on complex maps
- **My Way Home**: Navigation to find a goal in a maze

**Baseline DQN Results (Basic Scenario)**:
- DQN converges to near-optimal policy within thousands of episodes
- Action space: 3 buttons (move left, move right, shoot)
- Reward: +101 for kill, -5 per time step

**clau-doom Connection**:
- VizDoom is the exact platform clau-doom uses (via Python binding)
- These standard scenarios provide the evaluation framework for clau-doom benchmarks
- Basic, Defend the Center, and Deathmatch are the primary comparison scenarios

### B3. Deep Reinforcement Learning with DQN vs. PPO in VizDoom

- **Authors**: Multiple authors (Schulze et al.)
- **Venue**: IEEE CINTI 2021
- **URL**: https://ieeexplore.ieee.org/document/9668479/

**Summary**: Direct comparison of DQN variants (Dueling DQN) and PPO on VizDoom scenarios including Basic and Health Gathering Supreme. Provides convergence analysis and stability comparison.

**Key Results**:
- PPO shows better convergence stability than Dueling DQN across scenarios
- PPO less sensitive to hyperparameter choices
- Dueling DQN achieves comparable final performance but with higher variance
- Health Gathering Supreme: mean survival time used as primary metric

**clau-doom Connection**:
- Confirms PPO as a strong RL baseline for VizDoom
- Health Gathering Supreme survival time is a key metric for clau-doom comparison
- PPO's stability advantage is relevant: clau-doom's RAG approach should show even more stability across episodes

### B4. DQN vs. Policy Gradient Comparison on VizDoom (Felix Yu, 2017)

- **Source**: Technical blog with detailed experimental results
- **URL**: https://flyyufelix.github.io/2017/10/12/dqn-vs-pg.html

**Summary**: Detailed empirical comparison of DDQN, A2C, and REINFORCE on VizDoom's Defend the Center scenario over 20,000 episodes.

**Quantitative Results (Defend the Center)**:
- **DDQN**: Converges within ~1,000 episodes, stable at ~11 average kills
- **A2C**: Converges within ~5,000 episodes, reaches ~12 average kills (higher but more variable)
- **REINFORCE**: Converges within ~5,000 episodes, lower performance than A2C
- Reward structure: +1 per kill, -1 per death, -0.1 per health/ammo loss

**clau-doom Connection**:
- These per-scenario convergence rates are critical baselines
- clau-doom should report equivalent metrics: episodes to stable performance, average kills
- If clau-doom's RAG approach achieves similar kill rates in fewer episodes, that supports the "RAG as RL replacement" thesis

### B5. Gunner: Playing FPS Game Doom with Scalable Deep Reinforcement Learning

- **Authors**: Multiple authors
- **Venue**: PeerJ Computer Science, 2025
- **URL**: https://peerj.com/articles/cs-3410/

**Summary**: Gunner is a novel deep RL agent for Doom deathmatch that integrates four key components: a scalable network architecture for visual feature extraction, an LSTM module for temporal memory, Dueling Networks for stable value estimation, and Noisy Networks for enhanced exploration.

**Key Results**:
- Significantly outperformed DQN, DDQN, Dueling DQN, and A2C in deathmatch
- Superior in kills, K/D ratio, and item acquisition under identical conditions
- Five algorithms compared on same Doom deathmatch scenario
- Scalable architecture allows performance scaling with network depth

**clau-doom Connection**:
- Gunner represents the latest (2025) state-of-the-art for RL-based Doom agents
- Its deathmatch performance provides an updated RL baseline for clau-doom comparison
- Gunner's LSTM temporal memory is analogous to clau-doom's DuckDB encounter history (Level 1 cache)
- **Key Difference**: Gunner requires extensive training on frames; clau-doom aims for sample-efficient knowledge via RAG

### B6. Optimizing RL Agents in FPS Using Curriculum Learning and Reward Shaping

- **Authors**: Khan et al.
- **Venue**: Computer Animation and Virtual Worlds (CAVW), 2025
- **URL**: https://onlinelibrary.wiley.com/doi/10.1002/cav.70008

**Summary**: Analyzes PPO with curriculum learning and reward shaping on VizDoom's Deadly Corridor scenario across five difficulty levels. Demonstrates that combining PPO with progressive difficulty scheduling and auxiliary reward signals achieves record-breaking scores.

**Key Results**:
- Difficulty 1: 734 score
- Difficulty 2: 1576 score
- Difficulty 3: 1920 score
- Difficulty 4: 2280 score (highest)
- Difficulty 5: 1605 score
- Curriculum learning essential for convergence on harder difficulties

**clau-doom Connection**:
- Provides the latest PPO + curriculum learning baselines for Deadly Corridor
- Khan's progressive difficulty approach parallels clau-doom's DOE phase progression
- The score regression from difficulty 4 to 5 suggests overfitting to specific difficulty levels; clau-doom's RAG approach may generalize better
- **Key Baseline**: Deadly Corridor is a primary evaluation scenario for clau-doom

---

## Category C: LLM-based Doom Playing

### C1. Will GPT-4 Run DOOM?

- **Authors**: Adrian de Wynter
- **Venue**: arXiv:2403.05468 (2024)
- **URL**: https://arxiv.org/abs/2403.05468

**Summary**: Tests GPT-4's ability to play Doom's E1M1 ("Hangar") on "Hurt Me Plenty" difficulty using only screenshots converted to text descriptions. Tests four prompting strategies: Naive, Walkthrough, Plan, and K-Levels reasoning. Each strategy tested 10 times without intervention.

**Quantitative Results (E1M1, 10 trials each)**:

| Prompt Strategy | Room A (frames) | Room B (frames) | Room C (frames) | Room D (frames) | Deaths | Timeouts | Completion |
|----------------|-----------------|-----------------|-----------------|-----------------|--------|----------|------------|
| Naive | 1409 | 634 | - | - | 40% | 60% | 0/10 |
| Walkthrough | 671 | 657 | 259 | - | 90% | 10% | 0/10 |
| Plan | 559 | 903 | 193 | 47 | 90% | 10% | 0/10 |
| K-Levels | 434 | 671 | 731 | - | 80% | 20% | 0/10 |
| **Human** | **78** | **108** | **158** | **104** | **0%** | **0%** | **10/10** |

**Key Findings**:
- Zero completion rate across all strategies (human completes 100%)
- Plan strategy reached the final room once before dying
- Inference speed: approximately 1 minute per frame (impractical for real-time play)
- GPT-4 can manipulate doors, combat enemies, and perform basic pathing
- Gets stuck in loops and forgets environmental hazards (acid pools)
- Human is 5-20x faster in frame count per room

**clau-doom Connection**:
- This is the most direct comparison point for clau-doom
- de Wynter shows LLMs alone cannot play Doom at human level (zero completion rate)
- clau-doom's key innovation: avoid real-time LLM inference entirely, use Rust decision engine with RAG-retrieved strategies
- clau-doom should demonstrate that structured knowledge retrieval (RAG) outperforms raw LLM reasoning (GPT-4 zero-shot)
- The 1-minute-per-frame latency validates clau-doom's design decision: no real-time LLM calls during gameplay

---

## Quantitative Baseline Summary Table

### Competition Deathmatch Baselines (10-minute matches)

| Agent | Year | Track | Frags | F/D Ratio | Architecture | Training |
|-------|------|-------|-------|-----------|--------------|----------|
| F1 | 2016 | T1 (known) | 559 | 1.35 | A3C + Curriculum | Days, multi-GPU |
| Arnold | 2016 | T1 (known) | 413 | 1.90 | DRQN + Nav/Action | Days, single GPU |
| IntelAct | 2016 | T2 (unknown) | 297 | 3.08 | Direct Future Prediction | Millions of frames |
| Arnold | 2016 | T2 (unknown) | 167 | 32.8 | DRQN + Nav/Action | Days, single GPU |
| Marvin | 2017 | T1 (known) | 248 | 1.16 | DQN-based | Not reported |
| Arnold4 | 2017 | T2 (unknown) | 275 | 1.25 | DRQN (improved) | Not reported |

### Standard Scenario Baselines (Academic Benchmarks)

| Scenario | Algorithm | Key Metric | Value | Episodes to Converge | Source |
|----------|-----------|------------|-------|---------------------|--------|
| Basic | DQN | Reward convergence | Near-optimal | ~1,000 | Kempka et al. 2016 |
| Defend the Center | DDQN | Avg kills | ~11 | ~1,000 | Felix Yu 2017 |
| Defend the Center | A2C | Avg kills | ~12 | ~5,000 | Felix Yu 2017 |
| Health Gathering Supreme | PPO | Survival time | Best in class | - | Schulze et al. 2021 |
| E1M1 (GPT-4 Plan) | LLM (GPT-4) | Completion | 0/10 | N/A (zero-shot) | de Wynter 2024 |
| E1M1 (Human) | Human | Completion | 10/10 | N/A | de Wynter 2024 |

### Deadly Corridor Baselines (Khan et al. 2025, PPO + Curriculum)

| Difficulty Level | Score | Notes |
|-----------------|-------|-------|
| 1 (Easiest) | 734 | PPO + reward shaping + curriculum |
| 2 | 1576 | Progressive difficulty increase |
| 3 | 1920 | Near-peak performance |
| 4 | 2280 | Highest score achieved |
| 5 (Hardest) | 1605 | Performance regression suggests overfitting |

### Training Requirements Comparison

| Approach | Training Data | Training Time | Inference Latency | Real-time Capable |
|----------|--------------|---------------|-------------------|-------------------|
| DQN/DRQN (Arnold) | Millions of frames | Days (single GPU) | < 50ms | Yes |
| A3C (F1) | Millions of frames | Days (multi-GPU) | < 50ms | Yes |
| PPO | Millions of frames | Hours-Days | < 50ms | Yes |
| GPT-4 (de Wynter) | Zero (pretrained) | None | ~60,000ms (1 min/frame) | No |
| **clau-doom (target)** | **Episode retrospection** | **RAG accumulation** | **< 100ms (P99)** | **Yes** |

---

## Gap Analysis

### What Existing RL Baselines Demonstrate

1. **Strong RL Agents Exist**: Competition winners achieve hundreds of frags in 10-minute deathmatch
2. **Training Cost is High**: Days of training on GPU hardware with millions of frames required
3. **Generalization is Hard**: F1 dropped from 1st (2016) to 5th (2017) on Track 1; Track 2 (unknown maps) consistently produces lower scores
4. **LLM Zero-Shot Fails**: GPT-4 cannot complete even E1M1 (0/10 completion rate)

### What clau-doom Must Demonstrate

1. **RAG vs. RL Comparison**: On equivalent VizDoom scenarios (Basic, Defend the Center, Deathmatch), does the RAG approach achieve comparable kill rates? At what episode count?
2. **Learning Efficiency**: RL requires millions of frames. How many episodes does clau-doom need to build effective RAG knowledge?
3. **Generalization**: On unknown maps (Track 2 equivalent), does RAG-based knowledge transfer better than RL policies?
4. **Latency Compliance**: Decision latency must stay under 100ms (P99) per the design constraints.
5. **LLM Enhancement**: Compared to de Wynter's zero-shot GPT-4 (0% completion), does clau-doom's structured RAG approach meaningfully improve?

### Recommended Evaluation Scenarios

| Scenario | Purpose | Primary Metric | RL Baseline |
|----------|---------|---------------|-------------|
| Basic | Minimum viable agent | Score convergence | DQN ~1,000 episodes |
| Defend the Center | Combat effectiveness | Average kills per episode | DDQN ~11 kills, A2C ~12 kills |
| Deadly Corridor | Navigation + combat | Completion rate, kills | Available in VizDoom |
| Deathmatch (known map) | Full agent capability | Frags per 10 min | F1: 559, Arnold: 413 |
| Deathmatch (unknown map) | Generalization | Frags per 10 min | IntelAct: 297, Arnold: 167 |

### Key Questions for S2 Experiments

1. How many retrospection episodes does clau-doom need to match DDQN's ~11 kills on Defend the Center?
2. Can clau-doom's RAG approach generalize to unknown maps better than RL agents (Track 2 comparison)?
3. What is the knowledge accumulation curve? (Episodes vs. kill rate, analogous to RL's learning curve)
4. Does DOE-guided optimization of agent parameters converge faster than RL hyperparameter search?

---

## Completion Criteria

- [x] VizDoom Competition winners: 3 papers collected with quantitative results (Wydmuch et al., Lample & Chaplot, Wu & Tian)
- [x] DRL Doom AI: 6 papers collected with scenario-specific baselines (Dosovitskiy & Koltun, Kempka et al., Schulze et al., Felix Yu, Gunner, Khan et al.)
- [x] LLM Doom playing: 1 paper collected (de Wynter 2024)
- [x] Standard scenario baseline table created with per-algorithm numbers
- [x] Competition deathmatch baseline table created with frag scores
- [x] Deadly Corridor baseline table added (Khan et al. 2025)
- [x] Gap analysis identifying required clau-doom experiments
- [x] Phase 2 verification: 2 missing papers added (2026-02-07)

---

## References

1. Wydmuch, M., Kempka, M., Jaskowski, W. (2019). ViZDoom Competitions: Playing Doom from Pixels. IEEE Transactions on Games 11(3), 248-259. arXiv:1809.03470.
2. Lample, G., Chaplot, D.S. (2017). Playing FPS Games with Deep Reinforcement Learning. AAAI 2017. arXiv:1609.05521.
3. Wu, Y., Tian, Y. (2017). Training Agent for First-Person Shooter Game with Actor-Critic Curriculum Learning. ICLR 2017.
4. Dosovitskiy, A., Koltun, V. (2017). Learning to Act by Predicting the Future. ICLR 2017. arXiv:1611.01779.
5. Kempka, M., Wydmuch, M., Runc, G., Toczek, J., Jaskowski, W. (2016). ViZDoom: A Doom-based AI Research Platform for Visual Reinforcement Learning. IEEE CIG 2016. arXiv:1605.02097.
6. Schulze et al. (2021). Deep Reinforcement Learning with DQN vs. PPO in VizDoom. IEEE CINTI 2021.
7. de Wynter, A. (2024). Will GPT-4 Run DOOM? arXiv:2403.05468; IEEE Trans. on Games 2024.
8. Yu, F. (2017). Deep Q Network vs Policy Gradients - An Experiment on VizDoom with Keras. Technical report.
9. Multiple authors (2025). Gunner: Playing FPS Game Doom with Scalable Deep Reinforcement Learning. PeerJ Computer Science.
10. Khan et al. (2025). Optimizing Reinforcement Learning Agents in Games Using Curriculum Learning and Reward Shaping. Computer Animation and Virtual Worlds (CAVW).
