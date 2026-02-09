# Contributing to clau-doom

Thank you for your interest in contributing to clau-doom. This is an active academic research project investigating systematic optimization of game-playing AI through RAG-based skill accumulation, Design of Experiments (DOE), and generational evolution. We are targeting publication at NeurIPS/ICML venues.

Before contributing, please read this guide carefully. Research integrity and statistical rigor are non-negotiable.

For an overview of the project architecture and goals, see [README.md](README.md).

---

## Getting Started

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Docker + Docker Compose | Latest stable | Full stack orchestration |
| Rust | Stable toolchain | Agent core (decision engine) |
| Go | 1.21+ | Orchestrator, gRPC services |
| Python | 3.11+ | VizDoom glue layer |
| Node.js | 18+ | Dashboard frontend |
| Make | Any | Build automation |

### Setup

1. Fork the repository and clone your fork:

```bash
git clone https://github.com/<your-username>/clau-doom.git
cd clau-doom
```

2. Create a feature branch from `main`:

```bash
git checkout -b feature/your-feature-name
```

3. Verify your environment builds and passes tests:

```bash
make build && make test
```

If all tests pass, you are ready to contribute.

---

## Development Workflow

### Branch Strategy

```
main           - Stable releases only
feature/*      - New features -> PR to main
experiment/*   - Research experiments -> PR to main
docs/*         - Documentation updates -> PR to main
fix/*          - Bug fixes -> PR to main
```

All branches target `main` via pull request. Direct pushes to `main` are not permitted.

### Commit Convention

Follow the conventional commit format:

```
type(scope): subject
```

**Types:**

| Type | Use When |
|------|----------|
| `feat` | New feature or capability |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `exp` | Experiment (new DOE run, analysis result) |
| `refactor` | Code restructuring without behavior change |
| `test` | Test additions or modifications |
| `chore` | Build, tooling, CI changes |

**Scopes:**

| Scope | Covers |
|-------|--------|
| `agent-core` | Rust decision engine |
| `glue` | Python VizDoom binding |
| `orchestrator` | Go agent lifecycle management |
| `research` | Experiment orders, reports, findings |
| `infra` | Docker, Compose, deployment |
| `docs` | Documentation and guides |

**Examples:**

```
feat(agent-core): add weapon preference scoring to decision engine
exp(research): DOE-025 memory-strength interaction analysis
fix(glue): correct AMMO2 variable mapping in defend_the_line
docs(research): add interim report for DOE-020 through DOE-025
```

### Code Style

**Rust (agent-core/):**

```bash
cargo fmt --check
cargo clippy -- -D warnings
```

All code must pass both `cargo fmt` and `cargo clippy` with no warnings.

**Go (orchestrator/):**

```bash
gofmt -l .
go vet ./...
```

**Python (glue/):**

Follow existing patterns in the glue layer. Python is used only for VizDoom API binding; do not introduce complex application logic here.

**General:**

- All code, comments, variable names, and file contents must be in English.
- User-facing messages may be bilingual (Korean/English) where appropriate.

---

## Research Contributions

This section describes the standards required for any contribution that involves experimental results or statistical claims. These standards are enforced by project rules R100 (Experiment Integrity), R101 (PI Boundary), and R102 (Research Audit Trail).

### Experiment Integrity (R100)

All experiments MUST use fixed seed sets for reproducibility.

- Every DOE run specifies its seed set explicitly in the EXPERIMENT_ORDER document.
- Control and treatment conditions use IDENTICAL seed sets.
- Seeds are recorded in both the experiment order and the DuckDB execution log.
- Random or unrecorded seed usage will cause the contribution to be rejected.

**Example seed set (n=30):**

```
[42, 1337, 2023, 7890, 9999, 1111, 5555, 8888, 3333, 6666,
 1234, 5678, 9012, 3456, 7891, 2345, 6789, 1011, 1213, 1415,
 1617, 1819, 2021, 2223, 2425, 2627, 2829, 3031, 3233, 3435]
```

### Statistical Evidence

Every quantitative claim requires supporting statistical evidence. Claims without evidence markers are classified as UNTRUSTED and will not be accepted.

**Required analysis steps:**

1. ANOVA table with F-statistic and p-value
2. Residual diagnostics:
   - Normality: Anderson-Darling test
   - Equal variance: Levene test
   - Independence: Run order plot inspection
3. Effect size: partial eta-squared or Cohen's d
4. Power analysis (especially for non-significant results)
5. Pairwise comparisons: Tukey HSD (when factors are significant)

**Evidence markers (mandatory in all reports and findings):**

| Marker | Format | Example |
|--------|--------|---------|
| `[STAT:p]` | p-value | `[STAT:p=0.003]` |
| `[STAT:ci]` | Confidence interval | `[STAT:ci=95%: 2.3-4.7]` |
| `[STAT:effect_size]` | Effect size | `[STAT:effect_size=Cohen's d=0.82]` |
| `[STAT:power]` | Statistical power | `[STAT:power=1-beta=0.85]` |
| `[STAT:n]` | Sample size | `[STAT:n=150 episodes]` |
| `[STAT:f]` | F-statistic | `[STAT:f=F(2,45)=12.34]` |
| `[STAT:eta2]` | Partial eta-squared | `[STAT:eta2=partial eta^2=0.35]` |

**Trust level framework:**

| Level | Criteria | Action |
|-------|----------|--------|
| HIGH | p < 0.01, n >= 50 per condition, residuals pass all diagnostics | Adopt finding |
| MEDIUM | p < 0.05, n >= 30 per condition, residuals mostly clean | Tentative adoption, plan follow-up |
| LOW | p < 0.10, n < 30, or residual violations | Exploratory only, do not adopt |
| UNTRUSTED | No statistical test or p >= 0.10 | Reject |

No cherry-picking of results (p-hacking) is tolerated.

### Audit Trail (R102)

Every finding must be fully traceable through the research document chain:

```
HYPOTHESIS_BACKLOG.md
        |
        v
EXPERIMENT_ORDER_{ID}.md
        |
        v
EXPERIMENT_REPORT_{ID}.md
        |
        v
FINDINGS.md
```

- Breaking this chain at any point will cause the contribution to be rejected.
- All experiment documents go in `research/experiments/`.
- The RESEARCH_LOG.md must be updated with a chronological entry for each experiment.

### Adding New Strategies

To contribute a new agent strategy:

1. Implement your strategy class in `glue/action_functions.py`, following the existing class pattern.

2. Your class must implement the standard protocol:
   - `reset(seed: int)` -- initialize with a fixed seed for reproducibility
   - `__call__(state: dict) -> int` -- accept game state, return action index

3. Include L0 emergency rules in your strategy:
   - Health below 20: prioritize health pickups or retreat
   - Ammo equals 0: switch to melee or seek ammo

4. Register your strategy in `doe_executor.py` action dispatch.

5. Write at least one DOE experiment order to evaluate your strategy against existing baselines on the `defend_the_line` scenario (the standard discriminating scenario).

---

## Pull Request Process

1. Ensure your branch is up to date with `main`.

2. Run the full test suite:

```bash
make test
```

3. Verify structural integrity counts match expectations:
   - 18 agents in `.claude/agents/`
   - 32 skills in `.claude/skills/`
   - 20 rules in `.claude/rules/`

   If your contribution adds or removes agents, skills, or rules, update all references accordingly (CLAUDE.md counts, routing skills, etc.).

4. Write a clear PR description:
   - Summarize what changed and why.
   - For research contributions, include statistical evidence with markers.
   - Reference relevant experiment IDs (e.g., DOE-025).
   - Link to related issues if applicable.

5. PRs that modify experimental results or findings require:
   - Complete audit trail (hypothesis through finding).
   - ANOVA tables with residual diagnostics.
   - Fixed seed sets documented in the experiment order.

6. Expect review feedback. Research PRs may require additional statistical analysis or larger sample sizes before merging.

---

## Reporting Issues

Use GitHub Issues for bug reports, research questions, and feature requests.

**Bug reports** should include:
- Steps to reproduce the issue
- Environment information (OS, Docker version, language versions)
- Relevant error messages or logs
- Which scenario and agent configuration triggered the bug

**Research questions** should:
- Reference the relevant DOE experiment IDs
- Include any statistical output or observations
- Describe the expected versus actual behavior

**Feature requests** should:
- Explain the impact on research methodology
- Describe how the feature supports DOE, ANOVA, or the generational evolution workflow
- Indicate whether the feature affects the agent-core, glue, orchestrator, or infrastructure layer

---

## Code of Conduct

- Be respectful and constructive in all interactions.
- Scientific integrity is paramount. Do not fabricate, falsify, or selectively report experimental results.
- Acknowledge the contributions of others. If you build on someone's work, cite it.
- Disagree on evidence, not on personality. Statistical arguments are welcome; personal attacks are not.
- Respect reproducibility. If someone cannot reproduce your results with the documented seeds and procedure, the finding is invalid until resolved.

---

## Citation

If your contribution to this project leads to a publication, please cite:

```bibtex
@misc{clau-doom2026,
  title  = {clau-doom: Systematic Optimization of Game-Playing AI
            through RAG, DOE, and Generational Evolution},
  author = {Yi, Sang},
  year   = {2026},
  url    = {https://github.com/sangyi/clau-doom}
}
```

---

## Questions

If anything in this guide is unclear, open an issue or reach out to the project maintainer. We appreciate your interest in contributing to rigorous, reproducible AI research.
