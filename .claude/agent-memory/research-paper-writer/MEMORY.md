# Research Paper Writer Memory

## Project: clau-doom
## Paper: "Movement Is All You Need"
## Target: NeurIPS 2026

## Key Statistical Values (from actual experiment reports)

### Triple RAG Falsification
- DOE-022: L2_good vs L0_only kills p=0.929 (Tukey HSD), overall ANOVA F(3,116)=28.05 p<0.001 but driven by burst_3
- DOE-024: decision_mode F(3,348)=1.001, p=0.393 for kills; doom_skill F(2,348)=651.88, p<0.001
- DOE-026: kills F(4,145)=0.206, p=0.935; L2 RAG numerically worst (16.57 vs 17.15 group mean)
- F-070 cumulative N=450 across three independent tests

### Movement Dominance (DOE-029)
- Pattern (movement): F(1,116)=58.402, p<0.001, eta2=0.332, d=1.408
- Override (health): F(1,116)=0.784, p=0.378, eta2=0.004
- Interaction: F(1,116)=0.987, p=0.322
- Movers: 17.00 kills, Non-movers: 9.95 kills

### Rate-Time Compensation (DOE-027)
- kills ~ attack_ratio: F(6,203)=0.617, p=0.717 (NULL)
- kill_rate ~ attack_ratio: F(6,203)=3.736, p=0.0015 (significant)
- Linear regression: kills approx kr * survival_time

### Temporal Invariance (DOE-028)
- kills: F(4,145)=1.017, p=0.401
- survival: F(4,145)=1.634, p=0.169
- kill_rate: F(4,145)=1.069, p=0.374

## Data Discrepancy Notes
- PAPER_OUTLINE.md uses p-values (0.765, 0.598, 0.954) that differ from actual reports
- Actual DOE-022 L2 effect: L2_good vs L0_only p=0.929, or contrast-specific values
- Actual DOE-024 decision_mode: p=0.393
- Actual DOE-026 kills: p=0.935
- Always use values from EXPERIMENT_REPORT documents, not from outline

## Writing Conventions
- All sections in English
- LaTeX cross-references: \label{sec:intro}, \ref{sec:method}, etc.
- Citation style: \cite{author_year} and \citet{author_year}
- Statistical format: F(df1,df2)=XX.XX, p=X.XXX, eta2=X.XXX, d=X.XXX
- Use actual p-values not rounded unless p<0.001

## Rate-Time Model Constants
- C_movers = 42.2 kr/min * 24.4s / 60 = 17.17
- C_nonmovers = 40.8 kr/min * 15.3s / 60 = 10.38
- Gap: ~65%, driven by survival advantage
- Kill rate difference between movers/non-movers: p=0.180 (NOT significant)
- Compensation ratio range (DOE-028): 0.980-1.003 across 5 burst structures

## Information-Theoretic Values
- F-044: I(strategy; kill_rate) ~ 0.082 bits, CI [0.05, 0.11]
- Theoretical max: 54.1 bits/episode
- Utilization: 0.15%
- 3-action H_max = log2(3) = 1.585 bits
- 5-action H_max = log2(5) = 2.322 bits

## Variance Decomposition
- doom_skill: eta2=0.486 (DOE-023)
- Movement: eta2=0.332 (DOE-029)
- Strategy within class: <0.03 (DOE-027/028)
- L2 RAG: 0.001-0.006 (DOE-022/024/026)
- Agent params: 0.002 (DOE-009)

## Sections Written
- 01_front_matter.md: Abstract, Introduction (Sec 1), Related Work (Sec 2) -- 2026-02-09
- 02_core_content.md: Methodology (Sec 3), Results (Sec 4) -- 2026-02-09
- 03_back_matter.md: Analysis (Sec 5), Discussion (Sec 6), Conclusion (Sec 7) -- 2026-02-09

## Writing Lessons
- Ground all claims in FINDINGS.md [STAT:] markers before writing
- Variance decomposition table is effective for summarizing multi-DOE programs
- Negative results framing: "saves community from pursuing X" is compelling
- Mathematical formalization of rate-time compensation uses k = r * s identity
- Limitations should be specific and actionable, not generic disclaimers
