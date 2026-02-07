---
name: latex-formatting
description: LaTeX formatting for NeurIPS/ICML papers including templates, tables, figures, algorithms, and bibliography
user-invocable: false
---

# LaTeX Formatting Skill

LaTeX formatting guidelines and patterns for producing publication-quality academic papers targeting NeurIPS, ICML, and ICLR venues.

## neurips_2024 Style Template

### Document Preamble

```latex
\documentclass{article}

% NeurIPS 2024 style
\usepackage[final]{neurips_2024}
% Use [preprint] for preprint, [final] for camera-ready

% Essential packages
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage{hyperref}
\usepackage{url}
\usepackage{booktabs}
\usepackage{amsfonts}
\usepackage{amsmath}
\usepackage{amssymb}
\usepackage{nicefrac}
\usepackage{microtype}
\usepackage{xcolor}
\usepackage{graphicx}
\usepackage{subcaption}
\usepackage{algorithm}
\usepackage[noend]{algpseudocode}
\usepackage{multirow}

% Custom colors
\definecolor{codeblue}{rgb}{0.0, 0.0, 0.8}
\definecolor{codegray}{rgb}{0.5, 0.5, 0.5}
```

### Document Structure

```latex
\title{Evolutionary DOE for Autonomous Game Agent Optimization}

\author{
  Author Name \\
  Affiliation \\
  \texttt{email@example.com}
}

\begin{document}

\maketitle

\begin{abstract}
Your abstract here (150-250 words).
\end{abstract}

\section{Introduction}
\label{sec:intro}

\section{Related Work}
\label{sec:related}

\section{Method}
\label{sec:method}

\section{Experiments}
\label{sec:experiments}

\section{Results}
\label{sec:results}

\section{Conclusion}
\label{sec:conclusion}

\bibliography{references}
\bibliographystyle{plainnat}

\appendix
\section{Additional Results}
\label{app:additional}

\end{document}
```

## Custom Command Definitions

### Convenience Commands

```latex
% Math shortcuts
\newcommand{\R}{\mathbb{R}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\Prob}{\mathbb{P}}
\newcommand{\bx}{\mathbf{x}}
\newcommand{\bw}{\mathbf{w}}
\newcommand{\bA}{\mathbf{A}}
\newcommand{\cS}{\mathcal{S}}
\newcommand{\cP}{\mathcal{P}}

% Statistical notation
\newcommand{\etap}{\eta_p^2}
\newcommand{\omegasq}{\omega^2}

% Method names (consistent formatting)
\newcommand{\methodname}{\textsc{DOE-Evo}}
\newcommand{\topsis}{\textsc{Topsis}}
\newcommand{\ahp}{\textsc{Ahp}}

% Inline annotations
\newcommand{\todo}[1]{\textcolor{red}{[TODO: #1]}}
\newcommand{\note}[1]{\textcolor{blue}{[Note: #1]}}

% Results highlighting
\newcommand{\best}[1]{\textbf{#1}}
\newcommand{\second}[1]{\underline{#1}}
```

### Cross-Reference Shortcuts

```latex
\newcommand{\secref}[1]{Section~\ref{#1}}
\newcommand{\figref}[1]{Figure~\ref{#1}}
\newcommand{\tabref}[1]{Table~\ref{#1}}
\newcommand{\algref}[1]{Algorithm~\ref{#1}}
\newcommand{\eqref}[1]{Eq.~(\ref{#1})}
```

## Table Formatting (booktabs)

### Basic Results Table

```latex
\begin{table}[t]
\centering
\caption{Main results. Mean $\pm$ std over 30 independent runs.
         \best{Bold}: best, \second{underline}: second best.}
\label{tab:main-results}
\small
\begin{tabular}{@{}lcccc@{}}
\toprule
Method & Kill Rate $\uparrow$ & Survival $\uparrow$ & Ammo Eff. $\uparrow$ & Score $\uparrow$ \\
\midrule
Random         & 0.42 \scriptsize{$\pm$ 0.12} & 2100 \scriptsize{$\pm$ 450} & 0.51 \scriptsize{$\pm$ 0.08} & 0.38 \\
Grid Search    & 0.48 \scriptsize{$\pm$ 0.09} & 2400 \scriptsize{$\pm$ 380} & 0.55 \scriptsize{$\pm$ 0.07} & 0.43 \\
Bayesian Opt   & \second{0.55} \scriptsize{$\pm$ 0.08} & \second{2800} \scriptsize{$\pm$ 320} & \second{0.61} \scriptsize{$\pm$ 0.06} & \second{0.51} \\
\midrule
\methodname{}  & \best{0.67} \scriptsize{$\pm$ 0.06} & \best{3800} \scriptsize{$\pm$ 280} & \best{0.72} \scriptsize{$\pm$ 0.05} & \best{0.65} \\
\bottomrule
\end{tabular}
\end{table}
```

### ANOVA Results Table

```latex
\begin{table}[t]
\centering
\caption{ANOVA results for $2^3$ factorial experiment.
         Significant effects ($p < 0.05$) marked with *.}
\label{tab:anova}
\small
\begin{tabular}{@{}lrrrrr@{}}
\toprule
Source & SS & df & MS & $F$ & $p$ \\
\midrule
Retreat (A)         & 45.23 & 1  & 45.23 & 12.34 & 0.002* \\
Ammo (B)            & 23.11 & 1  & 23.11 &  6.30 & 0.021* \\
Explore (C)         &  8.45 & 1  &  8.45 &  2.31 & 0.145 \\
A $\times$ B        & 31.67 & 1  & 31.67 &  8.64 & 0.008* \\
A $\times$ C        &  2.12 & 1  &  2.12 &  0.58 & 0.456 \\
B $\times$ C        &  5.89 & 1  &  5.89 &  1.61 & 0.220 \\
A $\times$ B $\times$ C & 1.23 & 1 & 1.23 & 0.34 & 0.570 \\
Residual            & 58.67 & 16 &  3.67 &       & \\
\midrule
Total               & 176.37 & 23 & & & \\
\bottomrule
\end{tabular}
\end{table}
```

### Multi-Row/Multi-Column Table

```latex
\begin{table}[t]
\centering
\caption{Ablation study across DOE phases.}
\label{tab:ablation-phase}
\small
\begin{tabular}{@{}llcc@{}}
\toprule
Phase & Component Removed & Kill Rate & $\Delta$ \\
\midrule
\multirow{2}{*}{Phase 1}
  & DOE factorial design   & 0.52 & $-$22\% \\
  & Replicate seeds        & 0.60 & $-$10\% \\
\midrule
\multirow{2}{*}{Phase 2}
  & TOPSIS selection       & 0.55 & $-$18\% \\
  & Mutation scheduling    & 0.58 & $-$13\% \\
\midrule
\multirow{2}{*}{Phase 3}
  & RSM augmentation       & 0.61 & $-$9\% \\
  & RAG pipeline           & 0.59 & $-$12\% \\
\bottomrule
\end{tabular}
\end{table}
```

## Figure Placement and Referencing

### Single Figure

```latex
\begin{figure}[t]
\centering
\includegraphics[width=0.8\linewidth]{figures/convergence.pdf}
\caption{Convergence of average kill rate across generations.
\methodname{} (red) converges $3\times$ faster than the genetic
algorithm baseline (blue) and achieves 15\% higher final performance.}
\label{fig:convergence}
\end{figure}
```

### Side-by-Side Figures

```latex
\begin{figure}[t]
\centering
\begin{subfigure}[b]{0.48\linewidth}
  \centering
  \includegraphics[width=\linewidth]{figures/main_effects.pdf}
  \caption{Main effects plot.}
  \label{fig:main-effects}
\end{subfigure}
\hfill
\begin{subfigure}[b]{0.48\linewidth}
  \centering
  \includegraphics[width=\linewidth]{figures/interaction.pdf}
  \caption{Interaction plot (A $\times$ B).}
  \label{fig:interaction}
\end{subfigure}
\caption{(a) Main effect of each factor on kill rate.
Retreat threshold shows the largest effect.
(b) Interaction between retreat threshold and ammo conservation.
Non-parallel lines indicate significant interaction ($p = 0.008$).}
\label{fig:effects}
\end{figure}
```

### Figure Placement Rules

| Specifier | Meaning | Use When |
|-----------|---------|----------|
| `[t]` | Top of page | Default choice |
| `[b]` | Bottom of page | When top is crowded |
| `[h]` | Here if possible | Rarely (can cause issues) |
| `[H]` | Force here | Never in submissions |
| `[tp]` | Top or own page | Large figures |

### Figure File Format

- PDF: vector graphics (plots, diagrams)
- PNG: raster graphics (screenshots, photos) at 300+ DPI
- Avoid: JPG (lossy compression artifacts)

## Algorithm Environment (algorithm2e)

### Basic Algorithm

```latex
\begin{algorithm}[t]
\caption{\methodname{} Generation Lifecycle}
\label{alg:doe-evo}
\begin{algorithmic}[1]
\Require Population $\cP_0$, DOE design $\bA$, generations $T$
\Ensure Optimized population $\cP_T$
\State Initialize population $\cP_0$ with random configurations
\For{$t = 1$ to $T$}
  \State $\bA_t \gets \textsc{DesignExperiment}(\cP_{t-1})$
    \Comment{DOE matrix}
  \State $\mathbf{R}_t \gets \textsc{Execute}(\bA_t)$
    \Comment{Run experiments}
  \State $\mathbf{s}_t \gets \textsc{Analyze}(\mathbf{R}_t)$
    \Comment{ANOVA + effect sizes}
  \State $\mathbf{c}_t \gets \topsis(\cP_{t-1}, \bw)$
    \Comment{Rank agents}
  \State $\text{parents} \gets \textsc{Select}(\cP_{t-1}, \mathbf{c}_t, k)$
  \State $\text{offspring} \gets \textsc{Crossover}(\text{parents})$
  \State $\text{offspring} \gets \textsc{Mutate}(\text{offspring}, T_t)$
  \State $\text{elite} \gets \textsc{TopK}(\cP_{t-1}, \mathbf{c}_t, n_e)$
  \State $\cP_t \gets \text{elite} \cup \text{offspring}$
  \If{$\textsc{Curvature}(\mathbf{s}_t) > \tau$}
    \State Augment design to RSM \Comment{Phase transition}
  \EndIf
\EndFor
\State \Return $\cP_T$
\end{algorithmic}
\end{algorithm}
```

### Algorithm Style Guidelines

- Number all lines
- Use `\Comment{}` for inline explanations
- Use `\Require` and `\Ensure` for pre/post conditions
- Function names in small caps: `\textsc{FunctionName}`
- Math variables in standard math mode
- Keep to 15-25 lines (split into sub-algorithms if longer)

## BibTeX Bibliography Management

### Entry Types

```bibtex
% Conference paper
@inproceedings{author2024method,
  title     = {Method Name: A Description},
  author    = {Last, First and Second, Author},
  booktitle = {Advances in Neural Information Processing Systems (NeurIPS)},
  year      = {2024},
  volume    = {37}
}

% Journal paper
@article{author2024journal,
  title   = {Title of the Article},
  author  = {Last, First and Second, Author},
  journal = {Journal of Machine Learning Research},
  volume  = {25},
  number  = {1},
  pages   = {1--42},
  year    = {2024}
}

% Preprint
@article{author2024arxiv,
  title  = {Title of the Preprint},
  author = {Last, First},
  journal = {arXiv preprint arXiv:2401.12345},
  year   = {2024}
}

% Book
@book{montgomery2017doe,
  title     = {Design and Analysis of Experiments},
  author    = {Montgomery, Douglas C.},
  edition   = {9th},
  publisher = {Wiley},
  year      = {2017}
}
```

### Bibliography Best Practices

- Use consistent formatting across all entries
- Include DOI or URL when available
- Use full venue names (not abbreviations) for clarity
- Sort by citation key (alphabetical by first author)
- Keep a single .bib file per project
- 15-25 references for main conference papers

### Citation Commands

```latex
\cite{author2024method}           % (Author et al., 2024)
\citet{author2024method}          % Author et al. (2024)
\citep{author2024method}          % (Author et al., 2024)
\citep[see][]{author2024method}   % (see Author et al., 2024)
```

Use `\citet` when the author is the grammatical subject:
```latex
\citet{montgomery2017doe} provides a comprehensive overview of DOE methods.
```

Use `\citep` for parenthetical citations:
```latex
DOE methods have been widely studied~\citep{montgomery2017doe, box2005statistics}.
```

## Math Notation Conventions

### Standard Notation

```latex
% Scalars: italic lowercase
$x$, $y$, $\alpha$, $\theta$

% Vectors: bold lowercase
$\bx$, $\bw$, $\boldsymbol{\theta}$

% Matrices: bold uppercase
$\bA$, $\mathbf{X}$, $\mathbf{W}$

% Sets: calligraphic
$\cS$, $\cP$, $\mathcal{A}$

% Operators: roman
$\operatorname{argmax}$, $\operatorname{TOPSIS}$, $\operatorname{RPN}$

% Norms
$\|\bx\|_2$, $\|\bx - \bx'\|$

% Expected value
$\E[\bx]$, $\E_{\bx \sim p}[f(\bx)]$
```

### Equation Formatting

```latex
% Numbered equation
\begin{equation}
C_i = \frac{D_i^-}{D_i^+ + D_i^-}
\label{eq:topsis-closeness}
\end{equation}

% Multi-line equation
\begin{align}
D_i^+ &= \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^+)^2} \\
D_i^- &= \sqrt{\sum_{j=1}^{n} (v_{ij} - v_j^-)^2}
\label{eq:topsis-distance}
\end{align}

% Unnumbered inline
The fitness is $f(\bx) = \sum_{k} w_k \cdot r_k(\bx)$.

% Cases
\begin{equation}
\text{S/N} = \begin{cases}
-10 \log\left(\frac{1}{n}\sum y_i^2\right) & \text{smaller-is-better} \\
-10 \log\left(\frac{1}{n}\sum \frac{1}{y_i^2}\right) & \text{larger-is-better}
\end{cases}
\end{equation}
```

## Page Budget (NeurIPS)

```
Main paper: 9 pages (including figures and tables)
References: unlimited (do not count toward 9 pages)
Appendix: unlimited (after references)

Typical allocation:
  Abstract:     ~0.3 pages
  Introduction: ~1.5 pages
  Related Work: ~1.0 pages
  Method:       ~2.5 pages
  Experiments:  ~2.0 pages
  Results:      ~1.2 pages
  Conclusion:   ~0.5 pages
  Total:        ~9.0 pages
```

## Submission Checklist

```
[ ] Paper compiles without errors
[ ] Page limit respected (9 pages + refs)
[ ] All figures are legible at printed size
[ ] No placeholder text (TODO, TBD, XXX)
[ ] Author information correct (or anonymized for review)
[ ] All cross-references resolve (\ref warnings = 0)
[ ] Bibliography entries are complete and consistent
[ ] Supplementary material referenced from main text
[ ] PDF is within file size limit (typically 50MB)
[ ] No identifying information in review version
```
