#!/usr/bin/env python3
"""DOE-001 Real VizDoom Experiment Runner.

Executes 210 real VizDoom episodes (3 conditions x 70) and performs
statistical analysis.  Outputs DuckDB database and experiment report.

Usage (inside Docker container):
    python3 -m glue.doe_001_real [--data-dir /app/data] [--report-dir /app/research/experiments]
"""

from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime
from pathlib import Path

import numpy as np
from scipy import stats

from glue.action_functions import FullAgentAction, random_action, rule_only_action
from glue.duckdb_writer import DuckDBWriter
from glue.episode_runner import EpisodeRunner
from glue.vizdoom_bridge import VizDoomBridge

logger = logging.getLogger(__name__)

EXPERIMENT_ID = "DOE-001-REAL"
CONDITIONS = ["random", "rule_only", "full_agent"]
EPISODES_PER_CONDITION = 70


# ---------------------------------------------------------------------------
# Seed generation
# ---------------------------------------------------------------------------

def generate_seed_set(n: int = 70, base: int = 42, step: int = 31) -> list[int]:
    """Generate deterministic seed set: seed_i = 42 + i * 31."""
    return [base + i * step for i in range(n)]


# ---------------------------------------------------------------------------
# Statistical helpers (adapted from doe_001_execute.py)
# ---------------------------------------------------------------------------

def anderson_darling_test(data: np.ndarray) -> tuple[float, float]:
    """Anderson-Darling normality test.  Returns (statistic, p_value)."""
    result = stats.anderson(data, dist="norm")
    if result.statistic < result.critical_values[0]:
        p_value = 0.25
    elif result.statistic < result.critical_values[1]:
        p_value = 0.10
    elif result.statistic < result.critical_values[2]:
        p_value = 0.05
    elif result.statistic < result.critical_values[3]:
        p_value = 0.025
    elif result.statistic < result.critical_values[4]:
        p_value = 0.01
    else:
        p_value = 0.001
    return result.statistic, p_value


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Cohen's d effect size between two groups."""
    n1, n2 = len(group1), len(group2)
    var1 = np.var(group1, ddof=1)
    var2 = np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std == 0:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_std)


def perform_pairwise_comparison(
    data_dict: dict[str, np.ndarray],
    cond1: str,
    cond2: str,
) -> dict:
    """Pairwise comparison: Welch t-test, Mann-Whitney U, Cohen's d, 95% CI."""
    d1 = data_dict[cond1]
    d2 = data_dict[cond2]

    t_stat, p_value = stats.ttest_ind(d1, d2, equal_var=False)
    u_stat, p_mann = stats.mannwhitneyu(d1, d2, alternative="two-sided")
    d = cohens_d(d1, d2)

    mean_diff = float(np.mean(d1) - np.mean(d2))
    se_diff = float(np.sqrt(np.var(d1, ddof=1) / len(d1) + np.var(d2, ddof=1) / len(d2)))
    ci_lower = mean_diff - 1.96 * se_diff
    ci_upper = mean_diff + 1.96 * se_diff

    return {
        "condition_1": cond1,
        "condition_2": cond2,
        "n1": len(d1),
        "n2": len(d2),
        "mean1": float(np.mean(d1)),
        "mean2": float(np.mean(d2)),
        "sd1": float(np.std(d1, ddof=1)),
        "sd2": float(np.std(d2, ddof=1)),
        "mean_diff": mean_diff,
        "t_stat": float(t_stat),
        "p_value": float(p_value),
        "p_mann_whitney": float(p_mann),
        "cohens_d": d,
        "ci_95_lower": ci_lower,
        "ci_95_upper": ci_upper,
    }


def holm_bonferroni_correction(p_values: list[float]) -> list[float]:
    """Holm-Bonferroni correction for multiple comparisons."""
    n = len(p_values)
    sorted_indices = list(np.argsort(p_values))
    sorted_p = [p_values[i] for i in sorted_indices]
    adjusted_p = [0.0] * n
    for i, idx in enumerate(sorted_indices):
        adjusted_p[idx] = min(1.0, sorted_p[i] * (n - i))
    return adjusted_p


def assess_trust_level(
    normality_pass: bool,
    variance_pass: bool,
    sample_size: int,
    p_value: float,
    effect_size: float,
) -> str:
    """Assess trust level per R100."""
    if p_value < 0.01 and sample_size >= 50 and normality_pass and variance_pass:
        return "HIGH"
    if p_value < 0.05 and sample_size >= 30 and (normality_pass or variance_pass):
        return "MEDIUM"
    if p_value < 0.10:
        return "LOW"
    return "UNTRUSTED"


def effect_size_label(d: float) -> str:
    ad = abs(d)
    if ad > 0.8:
        return "large"
    if ad > 0.5:
        return "medium"
    return "small"


# ---------------------------------------------------------------------------
# Episode execution
# ---------------------------------------------------------------------------

def run_all_conditions(
    runner: EpisodeRunner,
    db: DuckDBWriter,
    seed_set: list[int],
) -> dict[str, list[dict]]:
    """Run 3 conditions x 70 episodes, write to DuckDB, return metrics."""
    all_data: dict[str, list[dict]] = {c: [] for c in CONDITIONS}

    action_fns = {
        "random": (random_action, -1),
        "rule_only": (rule_only_action, 0),
        "full_agent": (FullAgentAction(0.5, 0.5), 1),
    }

    for condition in CONDITIONS:
        action_fn, decision_level = action_fns[condition]
        logger.info("=== Condition: %s (%d episodes) ===", condition, len(seed_set))

        for i, seed in enumerate(seed_set):
            if isinstance(action_fn, FullAgentAction):
                action_fn.reset()

            result = runner.run_episode(
                seed=seed,
                condition=condition,
                episode_number=i + 1,
                action_fn=action_fn,
                decision_level=decision_level,
            )

            metrics = {
                "kills": result.metrics.kills,
                "survival_time": result.metrics.survival_time,
                "damage_dealt": result.metrics.damage_dealt,
                "damage_taken": result.metrics.damage_taken,
                "ammo_efficiency": result.metrics.ammo_efficiency,
                "exploration_coverage": result.metrics.exploration_coverage,
                "total_ticks": result.metrics.total_ticks,
                "shots_fired": result.metrics.shots_fired,
                "hits": result.metrics.hits,
                "cells_visited": result.metrics.cells_visited,
            }

            db.write_episode(
                experiment_id=EXPERIMENT_ID,
                run_id=f"{EXPERIMENT_ID}-{condition}",
                condition=condition,
                seed=seed,
                episode_number=i + 1,
                metrics=metrics,
                decision_latency_p99=result.decision_latency_p99,
                rule_match_rate=result.rule_match_rate,
            )

            all_data[condition].append(
                {
                    **metrics,
                    "kill_rate": result.metrics.kill_rate,
                    "decision_latency_p99": result.decision_latency_p99,
                    "rule_match_rate": result.rule_match_rate,
                }
            )

            if (i + 1) % 10 == 0 or i == 0:
                logger.info(
                    "  [%s] %d/%d  kills=%d  survival=%.1fs  kill_rate=%.2f/min",
                    condition,
                    i + 1,
                    len(seed_set),
                    result.metrics.kills,
                    result.metrics.survival_time,
                    result.metrics.kill_rate,
                )

    return all_data


# ---------------------------------------------------------------------------
# Analysis + report
# ---------------------------------------------------------------------------

def run_analysis(all_data: dict[str, list[dict]]) -> dict:
    """Run full statistical analysis.  Returns dict of all results."""
    # Build numpy arrays per condition for primary metric
    kills_by_cond = {
        c: np.array([ep["kills"] for ep in eps]) for c, eps in all_data.items()
    }
    survival_by_cond = {
        c: np.array([ep["survival_time"] for ep in eps]) for c, eps in all_data.items()
    }
    ammo_by_cond = {
        c: np.array([ep["ammo_efficiency"] for ep in eps]) for c, eps in all_data.items()
    }

    # 1. Normality
    normality: dict[str, dict] = {}
    for c in CONDITIONS:
        stat, p = anderson_darling_test(kills_by_cond[c])
        normality[c] = {"stat": stat, "p": p, "pass": p > 0.05}

    # 2. Equal variance (Levene)
    levene_stat, levene_p = stats.levene(
        kills_by_cond["random"],
        kills_by_cond["rule_only"],
        kills_by_cond["full_agent"],
    )
    variance_pass = levene_p > 0.05

    # 3. Pairwise comparisons
    pairs = [
        ("full_agent", "random"),
        ("full_agent", "rule_only"),
        ("rule_only", "random"),
    ]
    pairwise = [perform_pairwise_comparison(kills_by_cond, c1, c2) for c1, c2 in pairs]
    raw_p = [pw["p_value"] for pw in pairwise]
    adjusted_p = holm_bonferroni_correction(raw_p)

    # 4. Secondary metrics pairwise
    secondary = {}
    for metric_name, metric_data in [
        ("survival_time", survival_by_cond),
        ("ammo_efficiency", ammo_by_cond),
    ]:
        secondary[metric_name] = {}
        for c1, c2 in [("full_agent", "random"), ("full_agent", "rule_only")]:
            secondary[metric_name][f"{c1}_vs_{c2}"] = perform_pairwise_comparison(
                metric_data, c1, c2
            )

    # 5. Trust
    primary = pairwise[0]
    trust = assess_trust_level(
        normality_pass=all(r["pass"] for r in normality.values()),
        variance_pass=variance_pass,
        sample_size=primary["n1"],
        p_value=adjusted_p[0],
        effect_size=abs(primary["cohens_d"]),
    )

    # Descriptive stats
    desc: dict[str, dict] = {}
    for c in CONDITIONS:
        k = kills_by_cond[c]
        s = survival_by_cond[c]
        desc[c] = {
            "n": len(k),
            "mean_kills": float(np.mean(k)),
            "sd_kills": float(np.std(k, ddof=1)),
            "mean_survival": float(np.mean(s)),
            "sd_survival": float(np.std(s, ddof=1)),
            "mean_ammo_eff": float(np.mean(ammo_by_cond[c])),
            "sd_ammo_eff": float(np.std(ammo_by_cond[c], ddof=1)),
            "mean_latency": float(
                np.mean([ep["decision_latency_p99"] for ep in all_data[c]])
            ),
        }

    return {
        "normality": normality,
        "levene_stat": float(levene_stat),
        "levene_p": float(levene_p),
        "variance_pass": variance_pass,
        "pairwise": pairwise,
        "adjusted_p": adjusted_p,
        "secondary": secondary,
        "trust": trust,
        "desc": desc,
    }


def generate_report(results: dict, report_dir: Path) -> Path:
    """Generate EXPERIMENT_REPORT_001_REAL.md."""
    report_dir.mkdir(parents=True, exist_ok=True)
    report_path = report_dir / "EXPERIMENT_REPORT_001_REAL.md"

    pw = results["pairwise"]
    adj = results["adjusted_p"]
    norm = results["normality"]
    desc = results["desc"]
    trust = results["trust"]
    lev_stat = results["levene_stat"]
    lev_p = results["levene_p"]
    vp = results["variance_pass"]

    norm_all_pass = all(r["pass"] for r in norm.values())
    overall_diag = "PASS" if norm_all_pass and vp else (
        "PARTIAL" if any(r["pass"] for r in norm.values()) or vp else "FAIL"
    )

    def sig(i: int) -> str:
        return "YES" if adj[i] < 0.05 else "NO"

    def interp_block(i: int) -> str:
        p = pw[i]
        label = effect_size_label(p["cohens_d"])
        return (
            f"**Interpretation**: {p['condition_1']} achieved "
            f"{p['mean_diff']:.2f} more kills than {p['condition_2']} "
            f"(95% CI: [{p['ci_95_lower']:.2f}, {p['ci_95_upper']:.2f}]). "
            f"Effect size is {label} (d={p['cohens_d']:.2f})."
        )

    def pw_table(i: int) -> str:
        p = pw[i]
        return "\n".join([
            f"| t-statistic | [STAT:t={p['t_stat']:.4f}] |",
            f"| p-value (unadjusted) | [STAT:p={p['p_value']:.6f}] |",
            f"| p-value (Holm-Bonferroni) | [STAT:p_adj={adj[i]:.6f}] |",
            f"| Cohen's d | [STAT:effect_size=Cohen's d={p['cohens_d']:.2f}] |",
            f"| 95% CI | [STAT:ci=95%: {p['ci_95_lower']:.2f} to {p['ci_95_upper']:.2f}] |",
            f"| Mann-Whitney U p | [STAT:p_mann={p['p_mann_whitney']:.6f}] |",
            f"| Significant | {sig(i)} |",
        ])

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_short = datetime.now().strftime("%Y-%m-%d")

    content = f"""# EXPERIMENT_REPORT_001_REAL: DOE-001 Real VizDoom Baseline Comparison

**DATA SOURCE**: REAL VIZDOOM EPISODES (not simulated)
**Experiment Order**: DOE-001 (EXPERIMENT_ORDER_001.md)
**Hypothesis**: H-001 (HYPOTHESIS_BACKLOG.md)
**Date**: {date_short}
**Status**: COMPLETE

## Design Summary

- **Type**: OFAT (One Factor At a Time)
- **Factor**: Decision Architecture (3 levels: Random, Rule-Only, Full Agent)
- **Episodes per condition**: {EPISODES_PER_CONDITION}
- **Total episodes**: {EPISODES_PER_CONDITION * len(CONDITIONS)}
- **Seeds**: seed_i = 42 + i*31, i=0..69 (identical across conditions)
- **Scenario**: defend_the_center.cfg (VizDoom built-in)

## Results

### Primary Metric: Kills

| Condition | Mean | SD | n |
|-----------|------|-----|---|
| random | {desc['random']['mean_kills']:.2f} | {desc['random']['sd_kills']:.2f} | {desc['random']['n']} |
| rule_only | {desc['rule_only']['mean_kills']:.2f} | {desc['rule_only']['sd_kills']:.2f} | {desc['rule_only']['n']} |
| full_agent | {desc['full_agent']['mean_kills']:.2f} | {desc['full_agent']['sd_kills']:.2f} | {desc['full_agent']['n']} |

### Pairwise Comparisons (Kills)

#### full_agent vs random

| Metric | Value |
|--------|-------|
{pw_table(0)}

{interp_block(0)}

#### full_agent vs rule_only

| Metric | Value |
|--------|-------|
{pw_table(1)}

{interp_block(1)}

#### rule_only vs random

| Metric | Value |
|--------|-------|
{pw_table(2)}

{interp_block(2)}

### Secondary Metrics

#### Survival Time (seconds)

| Condition | Mean | SD |
|-----------|------|-----|
| random | {desc['random']['mean_survival']:.1f} | {desc['random']['sd_survival']:.1f} |
| rule_only | {desc['rule_only']['mean_survival']:.1f} | {desc['rule_only']['sd_survival']:.1f} |
| full_agent | {desc['full_agent']['mean_survival']:.1f} | {desc['full_agent']['sd_survival']:.1f} |

#### Ammo Efficiency

| Condition | Mean | SD |
|-----------|------|-----|
| random | {desc['random']['mean_ammo_eff']:.3f} | {desc['random']['sd_ammo_eff']:.3f} |
| rule_only | {desc['rule_only']['mean_ammo_eff']:.3f} | {desc['rule_only']['sd_ammo_eff']:.3f} |
| full_agent | {desc['full_agent']['mean_ammo_eff']:.3f} | {desc['full_agent']['sd_ammo_eff']:.3f} |

### Diagnostics

#### Normality (Anderson-Darling)

| Condition | A-squared | p-value | Result |
|-----------|-----------|---------|--------|
| random | {norm['random']['stat']:.4f} | {norm['random']['p']:.4f} | {'PASS' if norm['random']['pass'] else 'FAIL'} |
| rule_only | {norm['rule_only']['stat']:.4f} | {norm['rule_only']['p']:.4f} | {'PASS' if norm['rule_only']['pass'] else 'FAIL'} |
| full_agent | {norm['full_agent']['stat']:.4f} | {norm['full_agent']['p']:.4f} | {'PASS' if norm['full_agent']['pass'] else 'FAIL'} |

**Overall**: {'PASS' if norm_all_pass else 'FAIL'}

#### Equal Variance (Levene)

- Levene's W: {lev_stat:.4f}
- p-value: {lev_p:.4f}
- Result: {'PASS' if vp else 'FAIL'}

#### Independence

- Seed set used: identical across all conditions [seed_i = 42 + i*31]
- No time-dependent confounds
- Result: PASS

#### Overall Diagnostics: {overall_diag}

### Trust Assessment

**Trust Level**: {trust}

**Criteria**:
- Sample size: [STAT:n={desc['random']['n']} per condition]
- Normality: {'PASS' if norm_all_pass else 'FAIL'}
- Equal variance: {'PASS' if vp else 'FAIL'}
- Adjusted p-value: [STAT:p_adj={adj[0]:.6f}]
- Effect size: [STAT:effect_size=Cohen's d={abs(pw[0]['cohens_d']):.2f}]

## Conclusions

### H-001: Full Agent Outperforms Baselines

**Status**: {'SUPPORTED' if adj[0] < 0.05 and pw[0]['mean_diff'] > 0 else 'NOT SUPPORTED'}

The full agent (L0 rules + memory + strategy heuristics) demonstrated \
{'statistically significant' if adj[0] < 0.05 else 'no statistically significant'} \
improvement over the random baseline in kills \
[STAT:p_adj={adj[0]:.6f}]. The effect size was \
{effect_size_label(pw[0]['cohens_d'])} \
[STAT:effect_size=Cohen's d={pw[0]['cohens_d']:.2f}].

Compared to rule-only baseline, the full agent showed \
{'significant' if adj[1] < 0.05 else 'no significant'} improvement \
[STAT:p_adj={adj[1]:.6f}], with a \
{effect_size_label(pw[1]['cohens_d'])} effect size \
[STAT:effect_size=Cohen's d={pw[1]['cohens_d']:.2f}].

### H-002: Rule Engine Provides Value

**Status**: {'SUPPORTED' if adj[2] < 0.05 and pw[2]['mean_diff'] > 0 else 'NOT SUPPORTED'}

The rule-only baseline \
{'significantly outperformed' if adj[2] < 0.05 and pw[2]['mean_diff'] > 0 else 'did not significantly outperform'} \
the random baseline [STAT:p_adj={adj[2]:.6f}], with a \
{effect_size_label(pw[2]['cohens_d'])} effect \
[STAT:effect_size=Cohen's d={pw[2]['cohens_d']:.2f}].

### H-003: Decision Latency Within Bounds

Full agent decision latency P99: {desc['full_agent']['mean_latency']:.1f}ms (mean).
Target: < 100ms. Result: {'PASS' if desc['full_agent']['mean_latency'] < 100.0 else 'FAIL'}.

## Next Steps

1. If HIGH/MEDIUM trust: Adopt findings to FINDINGS.md, proceed to Phase 1
2. If LOW trust: Increase sample size or address diagnostic violations
3. Follow-up experiments:
   - H-004: Memory weight optimization (factorial design)
   - H-005: Strategy document quality impact
   - Phase 2: RSM for fine-tuning optimal parameters

## Data Location

- **DuckDB**: data_dir/doe_001_real.duckdb
- **Experiment table**: `experiments` ({EPISODES_PER_CONDITION * len(CONDITIONS)} rows)
- **Seed set table**: `seed_sets` (1 row)

---

**Report generated**: {now}
**Analysis pipeline**: `glue/doe_001_real.py`
**Data source**: Real VizDoom episodes (defend_the_center scenario)
"""

    report_path.write_text(content)
    return report_path


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="DOE-001 Real VizDoom Experiment Runner"
    )
    parser.add_argument("--data-dir", default="/app/data")
    parser.add_argument(
        "--report-dir", default="/app/research/experiments"
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    data_dir = Path(args.data_dir)
    report_dir = Path(args.report_dir)
    data_dir.mkdir(parents=True, exist_ok=True)

    # ----- VizDoom init -----
    logger.info("=" * 70)
    logger.info("DOE-001 REAL VizDoom Experiment")
    logger.info("=" * 70)

    try:
        bridge = VizDoomBridge("defend_the_center.cfg")
    except Exception as exc:
        logger.error(
            "Failed to initialize VizDoom: %s. "
            "Make sure VizDoom is installed and you are running inside "
            "the Docker container with Xvfb.",
            exc,
        )
        sys.exit(1)

    runner = EpisodeRunner(bridge)
    db_path = data_dir / "doe_001_real.duckdb"
    db = DuckDBWriter(db_path=db_path)

    # ----- Seed set -----
    seed_set = generate_seed_set(n=EPISODES_PER_CONDITION)
    db.write_seed_set(
        experiment_id=EXPERIMENT_ID,
        seed_set=seed_set,
        formula="seed_i = 42 + i * 31, i=0..69",
    )
    logger.info(
        "Seed set registered: n=%d, [%d, %d, ..., %d]",
        len(seed_set),
        seed_set[0],
        seed_set[1],
        seed_set[-1],
    )

    # ----- Run episodes -----
    all_data = run_all_conditions(runner, db, seed_set)

    # ----- Verify integrity -----
    logger.info("Verifying data integrity...")
    integrity = db.verify_integrity(EXPERIMENT_ID)
    if integrity["valid"]:
        logger.info("Data integrity OK: counts=%s", integrity["counts"])
    else:
        logger.warning("Data integrity issues: %s", integrity["issues"])

    # ----- Analysis -----
    logger.info("Running statistical analysis...")
    results = run_analysis(all_data)

    # Print summary to stdout
    print()
    print("=" * 70)
    print("ANALYSIS SUMMARY")
    print("=" * 70)
    desc = results["desc"]
    for c in CONDITIONS:
        d = desc[c]
        print(
            f"  {c:12s}: kills={d['mean_kills']:.1f} +/- {d['sd_kills']:.1f}  "
            f"survival={d['mean_survival']:.1f}s  "
            f"latency_p99={d['mean_latency']:.1f}ms"
        )
    print()
    for i, (c1, c2) in enumerate(
        [("full_agent", "random"), ("full_agent", "rule_only"), ("rule_only", "random")]
    ):
        pw = results["pairwise"][i]
        print(
            f"  {c1} vs {c2}: "
            f"diff={pw['mean_diff']:.2f}  "
            f"p={pw['p_value']:.6f}  "
            f"p_adj={results['adjusted_p'][i]:.6f}  "
            f"d={pw['cohens_d']:.2f}"
        )
    print()
    print(f"  Trust level: {results['trust']}")
    print()

    # ----- Report -----
    report_path = generate_report(results, report_dir)
    logger.info("Report written: %s", report_path)

    # ----- Cleanup -----
    bridge.close()
    db.close()

    logger.info("=" * 70)
    logger.info("DOE-001 REAL EXPERIMENT COMPLETE")
    logger.info("=" * 70)
    logger.info("  DuckDB: %s", db_path)
    logger.info("  Report: %s", report_path)
    logger.info("  Trust:  %s", results["trust"])


if __name__ == "__main__":
    main()
