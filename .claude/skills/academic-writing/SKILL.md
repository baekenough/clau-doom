---
name: academic-writing
description: Academic paper writing for NeurIPS/ICML format including structure, contribution statements, and experiment reporting
user-invocable: false
---

# Academic Writing Skill

Guidelines for producing academic papers targeting top ML/AI venues (NeurIPS, ICML, ICLR). Covers paper structure, contribution framing, related work, experiment reporting, and statistical result presentation.

## NeurIPS/ICML Paper Structure

### Standard Sections

```
1. Title
2. Abstract (150-250 words)
3. Introduction (~1.5 pages)
4. Related Work (~1 page)
5. Method / Approach (~2-3 pages)
6. Experiments (~2-3 pages)
7. Results and Discussion (~1-2 pages)
8. Conclusion (~0.5 page)
9. References
10. Appendix (supplementary, no page limit)
```

### Section Guidelines

**Title**: Concise, specific, avoid buzzwords. Include key method name if novel.
```
Good: "Evolutionary DOE for Autonomous Game Agent Optimization"
Bad:  "A Novel AI Framework for Next-Generation Gaming"
```

**Abstract** (structured):
```
[Problem] What problem are we solving? (1-2 sentences)
[Gap] What is missing in current approaches? (1 sentence)
[Method] What do we propose? (2-3 sentences)
[Results] Key quantitative results. (1-2 sentences)
[Impact] Why does this matter? (1 sentence)
```

**Introduction** (funnel structure):
```
Paragraph 1: Broad context and motivation
Paragraph 2: Specific problem statement
Paragraph 3: Limitations of existing approaches
Paragraph 4: Our approach and key insight
Paragraph 5: Contributions (bulleted list)
Paragraph 6: Paper organization (optional)
```

**Method**: Describe the approach formally. Use definitions, algorithms, equations. Build from simple to complex. Reference related work for borrowed concepts.

**Experiments**: Design, setup, baselines, metrics. Reproducibility details.

**Results**: Tables, figures, statistical analysis. Ablation studies.

**Conclusion**: Summarize findings, limitations, future work. No new information.

## Contribution Statement Patterns

### 1-3 Bullet Points

Contributions must be concrete, specific, and verifiable.

**Pattern 1: Method + Theory + Empirical**
```
Our contributions are:
- We propose [METHOD NAME], a [brief description] that [key innovation].
- We provide [theoretical result: convergence proof / bound / analysis].
- We demonstrate [X]% improvement over [baseline] on [benchmark].
```

**Pattern 2: Framework + Insight + Application**
```
We make the following contributions:
- A [framework/system] for [task] that integrates [component A] with [component B].
- An empirical finding that [surprising insight from experiments].
- Validation on [domain] showing [quantitative improvements].
```

**Pattern 3: Problem + Solution + Evidence**
```
This paper contributes:
- A formal definition of [problem] in the context of [domain].
- [Algorithm/Method] that addresses [specific challenge] via [mechanism].
- Comprehensive experiments showing [result] across [N conditions/datasets].
```

### Contribution Anti-Patterns

```
BAD: "We apply deep learning to game agents" (too vague)
BAD: "We propose a novel framework" (everything claims novelty)
BAD: "We achieve state-of-the-art results" (without specifics)
BAD: "We provide extensive experiments" (not a contribution)

GOOD: "We demonstrate that DOE-guided evolution converges 3x faster
       than random search while achieving 15% higher kill rates"
```

## Related Work Organization

### By Theme (Most Common)

```
\section{Related Work}

\paragraph{Game Agent Optimization.}
[Papers on optimizing game agents: RL approaches, evolutionary methods, ...]

\paragraph{Design of Experiments in ML.}
[Papers applying DOE to ML: hyperparameter tuning, architecture search, ...]

\paragraph{Retrieval-Augmented Generation.}
[Papers on RAG: knowledge retrieval, strategy documents, ...]

\paragraph{Multi-Criteria Decision Making.}
[Papers on TOPSIS, AHP in optimization contexts, ...]
```

### Organization Rules

- 15-25 references for a main conference paper
- Each paragraph: 3-6 papers, grouped by relevance
- Last sentence of each paragraph: distinguish our work
- Template for distinction: "In contrast to [prior work], we [our difference]."

### Citation Density

```
Introduction: 5-8 citations (motivate the problem)
Related Work: 15-20 citations (comprehensive coverage)
Method: 2-5 citations (borrowed techniques)
Experiments: 3-5 citations (baselines, benchmarks)
```

## Experiment Reporting

### Table Format

Use booktabs style (no vertical lines):

```latex
\begin{table}[t]
\centering
\caption{Kill rate comparison across methods. Mean $\pm$ std over 30 runs.
         Best results in \textbf{bold}, second best \underline{underlined}.}
\label{tab:main-results}
\begin{tabular}{lcccc}
\toprule
Method & Kill Rate & Survival & Ammo Eff. & Overall \\
\midrule
Random Search    & 0.42 $\pm$ 0.12 & 2100 $\pm$ 450 & 0.51 $\pm$ 0.08 & 0.38 \\
Grid Search      & 0.48 $\pm$ 0.09 & 2400 $\pm$ 380 & 0.55 $\pm$ 0.07 & 0.43 \\
Bayesian Opt     & 0.55 $\pm$ 0.08 & 2800 $\pm$ 320 & 0.61 $\pm$ 0.06 & 0.51 \\
Genetic Algorithm& 0.58 $\pm$ 0.10 & 3100 $\pm$ 400 & 0.58 $\pm$ 0.09 & 0.53 \\
\midrule
\textbf{Ours (DOE-Evo)} & \textbf{0.67} $\pm$ 0.06 & \textbf{3800} $\pm$ 280 & \textbf{0.72} $\pm$ 0.05 & \textbf{0.65} \\
\bottomrule
\end{tabular}
\end{table}
```

### Figure Descriptions

```
Figure types and when to use:
- Line plot: Performance over generations (convergence)
- Bar chart: Comparison across methods (final results)
- Box plot: Distribution comparison (variance visualization)
- Heat map: Interaction effects between factors
- Scatter plot: Correlation between metrics
```

Figure caption pattern:
```
\caption{[What the figure shows]. [Key observation]. [Optional: implication].}

Example:
\caption{Convergence of kill rate across generations for different methods.
DOE-Evo (red) converges 3$\times$ faster than Genetic Algorithm (blue)
and achieves a 15\% higher final performance.}
```

### Ablation Study Structure

```
Ablation studies systematically remove components to show their value.

\begin{table}[t]
\centering
\caption{Ablation study. Each row removes one component from the full model.}
\begin{tabular}{lccc}
\toprule
Configuration & Kill Rate & Survival & Overall \\
\midrule
Full model (DOE-Evo)     & \textbf{0.67} & \textbf{3800} & \textbf{0.65} \\
\quad w/o DOE phases     & 0.59 (-12\%) & 3200 (-16\%) & 0.55 (-15\%) \\
\quad w/o RAG pipeline   & 0.62 (-7\%)  & 3500 (-8\%)  & 0.60 (-8\%) \\
\quad w/o TOPSIS select. & 0.60 (-10\%) & 3300 (-13\%) & 0.57 (-12\%) \\
\quad w/o SPC monitoring & 0.64 (-4\%)  & 3600 (-5\%)  & 0.62 (-5\%) \\
\bottomrule
\end{tabular}
\end{table}
```

## Statistical Result Presentation

### APA-Style Reporting

```
Main effect: F(1, 46) = 12.34, p = .002, partial eta^2 = .21
Interaction: F(2, 46) = 8.67, p < .001, partial eta^2 = .27
Post-hoc: Tukey HSD, p < .05 for all pairwise comparisons

In LaTeX:
$F(1, 46) = 12.34$, $p = .002$, $\eta_p^2 = .21$
```

### Reporting Rules

- Always report: test statistic, degrees of freedom, p-value, effect size
- Use exact p-values unless p < .001
- Report means with standard deviations or standard errors
- State which statistical test was used and why
- For multiple comparisons: state correction method (Bonferroni, etc.)

### Confidence Intervals

```
Mean kill rate: 0.67, 95% CI [0.63, 0.71]

In LaTeX:
$\bar{x} = 0.67$, 95\% CI $[0.63, 0.71]$
```

### Effect Size Reporting

```
Small:  d = 0.2,  eta^2 = 0.01
Medium: d = 0.5,  eta^2 = 0.06
Large:  d = 0.8,  eta^2 = 0.14

"The effect of retreat threshold on kill rate was large
($d = 0.92$, $\eta_p^2 = .21$)."
```

## LaTeX Integration Notes

### Cross-Referencing

```
\label{sec:method}, \label{tab:results}, \label{fig:convergence}
\ref{sec:method}, \ref{tab:results}, \ref{fig:convergence}
```

### Math Mode Conventions

```
Variables: italic ($x$, $\theta$, $\alpha$)
Functions: roman (\operatorname{TOPSIS}, \text{RPN})
Vectors: bold ($\mathbf{x}$, $\mathbf{w}$)
Matrices: bold capital ($\mathbf{A}$, $\mathbf{X}$)
Sets: calligraphic ($\mathcal{S}$, $\mathcal{A}$)
```

### Common Notation for This Domain

```
$\mathbf{x}_i$: agent DNA vector for agent $i$
$f(\mathbf{x})$: fitness function
$\mathcal{P}_t$: population at generation $t$
$\mathcal{S}$: strategy document set
$\phi(\cdot)$: embedding function
$d(\mathbf{x}_i, \mathbf{x}_j)$: distance between agent configs
$\eta_p^2$: partial eta-squared (effect size)
$\omega^2$: omega-squared (less biased effect size)
```

## Writing Quality Checklist

Before submission:

```
[ ] Title is concise and specific
[ ] Abstract follows problem-gap-method-results-impact structure
[ ] Contributions are concrete and verifiable (1-3 bullets)
[ ] Related work covers all relevant areas, distinguishes our work
[ ] Method section is self-contained and reproducible
[ ] All experiments have clear baselines
[ ] Statistical tests are appropriate and fully reported
[ ] Effect sizes are reported alongside p-values
[ ] Ablation study demonstrates value of each component
[ ] Figures are readable at printed size
[ ] Tables use booktabs style
[ ] All claims are supported by evidence
[ ] Limitations are acknowledged
[ ] Future work is specific, not hand-wavy
[ ] Page limit respected (NeurIPS: 9 pages + refs)
```
