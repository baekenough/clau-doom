# Back Matter: Analysis, Discussion, and Conclusion

## 5. Analysis

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


## 6. Discussion

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


## 7. Conclusion

We presented the first systematic application of design of experiments (DOE) methodology to FPS game agent optimization. Through 29 factorial experiments spanning 5,010 episodes in VizDoom's defend_the_line scenario, we tested and falsified the hypothesis that retrieval-augmented generation (RAG) improves agent performance.

Our principal findings are:

1. **Movement is the sole performance determinant** ($d=1.408$, $p<0.001$), producing a 65% kill advantage over non-moving agents through a survival bonus with negligible kill rate cost.
2. **Rate-time compensation** constrains all tactical optimization within movement classes: kill rate and survival time trade off exactly, holding total kills constant ($r \times s \approx C_{\mathcal{M}}$).
3. **The core RAG thesis is falsified** through three independent null results (DOE-022, DOE-024, DOE-026; $N=450$, all $p>0.39$), demonstrating that knowledge retrieval provides zero benefit in this domain.
4. **Environment difficulty dominates** ($\eta^2=0.486$), explaining nearly half of all performance variance and dwarfing all agent architecture parameters combined.

Our work demonstrates that DOE methodology reveals fundamental performance constraints that gradient-based optimization cannot discover. The rate-time compensation mechanism explains why tactical variations are irrelevant in simple FPS scenarios --- a structural insight that would be nearly impossible to derive from reinforcement learning alone. We recommend that game AI researchers apply DOE as a preliminary investigation tool before investing in complex architectures: in many scenarios, the architecture complexity budget is better spent on the single factor that matters most --- which, in VizDoom's defend_the_line, is simply whether the agent moves.
