# Research Analyst Memory

## Key Patterns

### Real VizDoom Data Characteristics (post-KILLCOUNT bug fix)
- Kill_rate is zero-inflated (9-17% zero-kill episodes depending on config) and right-skewed
- Typical SD for kill_rate: 3.5-5.3 kills/min (high variance, wider range = more variance)
- Normality tests (Shapiro-Wilk, Anderson-Darling) will FAIL for kill_rate data
- Always run non-parametric verification (Kruskal-Wallis, ART ANOVA) as primary
- ANOVA is still acceptable with balanced designs + equal variance (robust to non-normality)
- Consider Poisson/negative binomial regression for kill counts in future

### DOE-005 Results (2026-02-08)
- Memory [0.7, 0.9] and Strength [0.7, 0.9]: ALL non-significant
- Performance plateau in this range: ~8.4 kills/min regardless of configuration
- Strength has largest (still non-significant) trend: d=0.295
- Memory has slight negative trend: d=-0.164
- No curvature detected (p=0.62)
- DOE-002 data is INVALID (KILLCOUNT bug = AMMO2 constant as kills)
- DOE-005 is the first experiment with real kills data

### DOE-006 Results (2026-02-08)
- Memory [0.3, 0.7] and Strength [0.3, 0.7]: ALL non-significant (confirms DOE-002 was artifact)
- DOE-002 re-validation FAILED: large effects (eta2=0.42, 0.32) were AMMO2 bug artifacts
- Memory: F(1,116)=0.139, p=0.71, eta2=0.001, d=-0.067 (negligible)
- Strength: F(1,116)=2.571, p=0.11, eta2=0.022, d=+0.293 (small, same as DOE-005)
- Interaction: F(1,116)=1.985, p=0.16, eta2=0.017 (interesting asymmetry)
- Simple effect: Strength significant at Memory=0.3 (p=0.039, +2.61 kr) but not Memory=0.7 (p=0.89)
- No curvature (p=0.55), higher zero-kill rate (16.7% vs 9.3% in DOE-005)
- Cross-experiment replication (0.7,0.7) cell: CONFIRMED (p=0.91, d=0.030)
- CONCLUSION: Memory-Strength optimization thread CLOSED. Flat from 0.3 to 0.9.

### Analysis Infrastructure
- DuckDB accessible via: docker exec clau-doom-player python3
- Python packages available: scipy 1.17, statsmodels 0.14.6, pandas 3.0, numpy 2.4
- Host does NOT have duckdb Python module -- must use Docker container
- Data path in container: /app/data/clau-doom.duckdb
- ART ANOVA implementation: align by removing other effects, rank, then ANOVA on ranks
- QUOTING BUG: docker exec + inline python with single quotes fails for != operator
  - WORKAROUND: write script to /tmp, docker cp, then docker exec python3 /tmp/script.py
- statsmodels ANOVA anova_lm() does NOT have 'mean_sq' column; compute as SS/df manually

### Power Analysis Reference (2^2 factorial)
- n=30/cell: power ~0.78 for medium effect (f=0.25)
- n=32/cell: power ~0.80 for medium effect
- n=50/cell: power ~0.80 for small-medium effect (f=0.20)
- n=88/cell: power ~0.80 for small effect (f=0.15)

### Report Template
- Follow R102 audit trail: link to hypothesis, order, and findings
- Include [STAT:...] markers for all statistical claims
- Include trust level assessment (HIGH/MEDIUM/LOW)
- Always include both parametric and non-parametric results when normality fails
