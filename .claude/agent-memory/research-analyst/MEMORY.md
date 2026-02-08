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

### DOE-007 Results (2026-02-08) - Layer Ablation Study
- 5-level one-way ANOVA (random, L0_only, L0_memory, L0_strength, full_agent)
- Overall ANOVA: F(4,145)=1.579, p=0.183, eta2=0.042 -- NOT significant
- Kruskal-Wallis: H(4)=3.340, p=0.503 -- confirms non-significance
- Random agent comparable to all structured agents (C1 contrast p=0.656)
- Full_agent WORST performer: mean=6.74, 20% zero-kill rate
- L0_only BEST performer: mean=9.08, SD=2.75, 0% zero-kill
- Both normality AND equal variance FAILED (Levene p=0.039)
- Combined heuristics may be counterproductive (C3 p=0.051, borderline)
- Power only 49% at observed effect; MDE at 80% power = f=0.287
- defend_the_center produces only 0-3 kills/episode -- ceiling limits differentiation
- Consistent with DOE-005/006: parameters AND architecture both non-significant

### DuckDB Schema Note
- Table is `experiments` (NOT `experiment_runs`)
- Has pre-computed `kill_rate` and `ammo_efficiency` columns
- `condition` column format: "action_strategy=random", etc.
- Parse with: str.replace('action_strategy=', '')

### Power Analysis Reference (one-way, k=5)
- n=30/group: power ~0.67 for medium effect (f=0.25), ~0.98 for large (f=0.40)
- MDE at 80% power with k=5, n=30: f=0.287
- Need n=55/group for 80% power at observed f=0.209

### DOE-008 Results (2026-02-08) - Layer Ablation on defend_the_line
- FIRST SIGNIFICANT RESULT in clau-doom
- Overall ANOVA: F(4,145)=5.256, p=0.000555, eta2=0.127 -- SIGNIFICANT
- Kruskal-Wallis: H(4)=20.158, p=0.000465 -- confirms
- ALL residual diagnostics PASS (normality AND equal variance) -- first ablation to achieve this
- Effect driven entirely by L0_only performing WORST (36.78 vs 42.2-43.4 for others)
- L0_only went from BEST (DOE-007, defend_center) to WORST (DOE-008, defend_line) -- RANK REVERSAL
- Heuristic layers equivalent to random: lateral movement is the key, not the heuristic design
- C2 contrast (L0_only vs augmented): p=0.000019, d=-0.938 (large)
- C3 kills (single vs combined): p=0.007, d=0.487 (full_agent fewer raw kills)
- C3 kill_rate: p=0.792 (NOT significant -- survival time compensates)
- Power: 97% at observed f=0.381
- Trust: HIGH (all diagnostics pass, p<0.001, large effect, triple test convergence)
- defend_the_line: 4-26 kills/episode, 0% zero-kill, superior diagnostic properties

### Scenario Dependency Finding
- Agent performance ranking is SCENARIO-DEPENDENT
- defend_the_center: too simple (0-3 kills), all architectures indistinguishable
- defend_the_line: sufficient range (4-26 kills), reveals L0_only deficit
- Always test on defend_the_line for future experiments
- defend_the_line eliminates zero-inflation and produces normal residuals

### DOE-010 Results (2026-02-08) - Structured Lateral Movement
- Overall ANOVA: F(4,145)=4.938, p=0.000923, eta2=0.120 -- SIGNIFICANT
- Confirms F-010 from DOE-008; L0_only worst
- sweep_lr = L0_only (Tukey p=0.968) -- deterministic oscillation = no movement
- burst_3 best performer (44.55 kr), matches random (42.16), both beat sweep/L0
- H-014 REJECTED: structured patterns do NOT outperform random

### DOE-011 Results (2026-02-08) - 5-Action Expanded Space
- Overall ANOVA: F(4,145)=3.774, p=0.006, eta2=0.094 -- SIGNIFICANT
- Kruskal-Wallis: H(4)=13.002, p=0.011 -- confirms
- Normality PASS (Shapiro p=0.346), Levene FAIL (p=0.005, SD ratio 1.93x)
- C2 (strafe vs turn burst): p=0.003, d=-0.789 -- TURNING > STRAFING for kill_rate
- C4 (3-action vs 5-action): p=0.003, d=0.523 -- 3-ACTION > 5-ACTION for kill_rate
- C1 (dilution): p=0.061 -- borderline, random_5 trends lower but NS after Bonferroni
- C3 (smart_5 vs random_5): p=0.213 -- intelligent strategy does NOT beat random
- SURVIVAL: strafing hugely beneficial (eta2=0.225, random_5 survives 63% longer)
- RATE-VS-TOTAL PARADOX: kill_rate and kills inversely ranked across conditions
- Strafing = defensive (survival) not offensive (kill_rate)
- turn_burst_3 remains best for kill_rate at 45.5 kr (replicates DOE-010 burst_3)
- Cross-experiment replication: both anchors within d<0.2 of DOE-010

### DOE-011 Per-Experiment DB
- DOE-011 uses SEPARATE duckdb file: /app/data/doe011.duckdb (NOT clau-doom.duckdb)
- Same schema: experiments table with condition, kill_rate, kills, survival_time etc.
- Condition format: "action_strategy=random_3", "action_strategy=smart_5", etc.

### Report Template
- Follow R102 audit trail: link to hypothesis, order, and findings
- Include [STAT:...] markers for all statistical claims
- Include trust level assessment (HIGH/MEDIUM/LOW)
- Always include both parametric and non-parametric results when normality fails
- Include Alexander-Govern test as additional robust alternative
- For experiments with cross-space comparisons, report ALL response variables (kill_rate, kills, survival)
- Note rate-vs-total tradeoffs when survival varies across conditions
