# Research Paper Writer Memory

## NeurIPS Paper Structure (2026-02-10)

### Main Paper: PAPER_DRAFT.tex
- Title: "Movement Is All You Need: How 29 Systematic Experiments Falsified RAG-Based FPS Game Agent Optimization"
- Template: neurips_2025.sty (preprint mode)
- Sections: Introduction, Related Work, Methodology, Results, Analysis, Discussion, Conclusion
- Page budget: 8 pages main body (before bibliography)
- Uses `% MOVED TO APPENDIX` comments for appendix cross-reference

### Appendix: PAPER_APPENDIX.tex (current structure, sections A-H)
- A: Complete DOE Summary Table (longtable + timeline fig + strategy perf table + tactical invariance + stats + milestones + detailed Phase 0-1 results)
- B: Key Findings Catalogue (Top 20 of 83 findings)
- C: Rate-Time Compensation Evidence (DOE-027/028/029 data + ratio table + mechanism)
- D: Extended Analysis (Mathematical Model + Info-Theoretic + Variance Decomposition + Value of Negative Results)
- E: Statistical Methods and Reproducibility
- F: Glossary of Terms
- G: Future Work and Open Questions
- H: Acknowledgments and Ethics Statement

### Version 2 Trimming (original 17p -> 8p)
- Condensed all sections heavily; moved detailed content to appendix
- Kept all 6 figures, moved Table 1 (strategy ranking) + Table 3/4 (compensation data) to appendix
- Kept Table 2 (falsification evidence) in main body

### All 6 Figures
1. Figure 1 (architecture) -- Methodology
2. Figure 2 (DOE timeline) -- Methodology
3. Figure 3 (rate-time compensation) -- Analysis
4. Figure 4 (movement effect) -- Results 4.4
5. Figure 5 (L2 forest plot) -- Results 4.2
6. Figure 6 (tactical invariance) -- Results 4.3

### Key Statistical Values (must remain consistent across files)
- 29 experiments, 5,010 episodes, 83 findings
- L2 RAG falsification: DOE-022 (p=0.929), DOE-024 (p=0.393), DOE-026 (p=0.935), combined N=630
- Movement effect: F(1,116)=58.40, p<0.001, eta_p^2=0.332, d=1.408
- doom_skill dominance: eta^2=0.720 (72% variance)
- Rate-time compensation: C_movers=17.17, C_non-movers=10.38, elasticity ratio 1.15
- Info-theoretic: H_max=log2(3)=1.585, I(strategy;kill_rate)=0.082 bits (0.15% of max)
- 5-action: H_max=log2(5)=2.322 bits
- Bibliography: 16 references in thebibliography (not BibTeX)

### LaTeX Notes
- tectonic -Z continue-on-errors to compile
- Underscore escaping: \texttt{defend\_the\_line}
- Check pages: mdls -name kMDItemNumberOfPages PAPER_DRAFT.pdf

### Lessons Learned
- Always read current file before assuming changes needed; appendix was already complete after restructuring
- Previous expansion (I-O sections) was consolidated back into A-H structure
