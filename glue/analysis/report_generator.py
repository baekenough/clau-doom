"""Generate EXPERIMENT_REPORT markdown from DuckDB data."""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path
from typing import Optional

import duckdb
import numpy as np

from glue.analysis.statistical_tests import (
    PairwiseResult,
    holm_bonferroni,
    pairwise_comparison,
    test_equal_variance,
    test_normality,
)
from glue.analysis.diagnostics import run_diagnostics

logger = logging.getLogger(__name__)

REPORT_DIR = Path("research/experiments")


def load_experiment_data(
    db_path: str, experiment_id: str, metric: str = "kill_rate"
) -> dict[str, np.ndarray]:
    """Load experiment data grouped by condition from DuckDB."""
    con = duckdb.connect(db_path, read_only=True)
    try:
        rows = con.execute(
            f"SELECT condition, {metric} FROM experiments "
            f"WHERE experiment_id = ? AND {metric} IS NOT NULL "
            f"ORDER BY condition, episode_number",
            [experiment_id],
        ).fetchall()
    finally:
        con.close()

    data: dict[str, list[float]] = {}
    for condition, value in rows:
        data.setdefault(condition, []).append(value)

    return {k: np.array(v) for k, v in data.items()}


def assess_trust_level(
    results: list[PairwiseResult],
    diagnostics_pass: bool,
    min_n: int = 30,
) -> str:
    """Assess trust level based on evidence quality."""
    if not results:
        return "UNTRUSTED"

    n_per_condition = min(r.n_a for r in results)
    any_significant = any(r.p_value_welch < 0.05 for r in results)
    all_strong = all(r.p_value_welch < 0.01 for r in results if r.is_significant())

    if all_strong and diagnostics_pass and n_per_condition >= 50:
        return "HIGH"
    elif any_significant and diagnostics_pass and n_per_condition >= min_n:
        return "MEDIUM"
    elif any_significant and n_per_condition >= min_n:
        return "LOW"
    else:
        return "UNTRUSTED"


def generate_report(
    db_path: str,
    experiment_id: str,
    metrics: Optional[list[str]] = None,
    output_dir: Optional[Path] = None,
) -> str:
    """Generate full experiment report.

    Returns the report markdown string.
    """
    if metrics is None:
        metrics = ["kill_rate", "kills", "survival_time", "damage_dealt",
                   "ammo_efficiency"]

    out_dir = output_dir or REPORT_DIR
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    lines = [
        f"# EXPERIMENT_REPORT_{experiment_id.replace('-', '_')}",
        "",
        f"**Experiment**: {experiment_id}",
        f"**Generated**: {timestamp}",
        f"**Design**: OFAT Baseline Comparison",
        "",
    ]

    primary_metric = metrics[0]  # kill_rate
    primary_data = load_experiment_data(db_path, experiment_id, primary_metric)

    if not primary_data:
        lines.append("**ERROR**: No data found for this experiment.")
        report = "\n".join(lines)
        report_path = out_dir / f"EXPERIMENT_REPORT_{experiment_id.replace('-', '_')}.md"
        report_path.write_text(report)
        return report

    # Sample sizes
    lines.append("## Sample Sizes")
    lines.append("")
    lines.append("| Condition | n |")
    lines.append("|-----------|---|")
    for cond, values in sorted(primary_data.items()):
        lines.append(f"| {cond} | {len(values)} |")
    lines.append("")

    # Descriptive statistics for all metrics
    lines.append("## Descriptive Statistics")
    lines.append("")

    for metric in metrics:
        data = load_experiment_data(db_path, experiment_id, metric)
        if not data:
            continue

        lines.append(f"### {metric}")
        lines.append("")
        lines.append("| Condition | Mean | SD | Min | Max |")
        lines.append("|-----------|------|-----|-----|-----|")
        for cond in sorted(data.keys()):
            v = data[cond]
            lines.append(f"| {cond} | {np.mean(v):.3f} | {np.std(v, ddof=1):.3f} | "
                        f"{np.min(v):.3f} | {np.max(v):.3f} |")
        lines.append("")

    # Diagnostics on primary metric
    lines.append("## Residual Diagnostics (Primary: kill_rate)")
    lines.append("")
    diag = run_diagnostics(primary_data)
    lines.append(diag.format_summary())
    lines.append("")

    # Normality per condition
    lines.append("### Per-Condition Normality")
    lines.append("")
    for cond, values in sorted(primary_data.items()):
        norm_result = test_normality(values, cond, primary_metric)
        status = "PASS" if norm_result.is_normal else "FAIL"
        lines.append(f"- {cond}: {status} {norm_result.format_stat_marker()}")
    lines.append("")

    # Equal variance
    var_result = test_equal_variance(primary_data, primary_metric)
    lines.append(f"### Equal Variance: {'PASS' if var_result.variances_equal else 'FAIL'} "
                f"{var_result.format_stat_marker()}")
    lines.append("")

    # Pairwise comparisons
    lines.append("## Pairwise Comparisons (Primary: kill_rate)")
    lines.append("")

    conditions = sorted(primary_data.keys())
    all_results: list[PairwiseResult] = []

    for cond_a, cond_b in combinations(conditions, 2):
        result = pairwise_comparison(
            primary_data[cond_a], primary_data[cond_b],
            cond_a, cond_b, primary_metric,
        )
        all_results.append(result)

    # Holm-Bonferroni correction
    p_values = [r.p_value_welch for r in all_results]
    significant_corrected = holm_bonferroni(p_values)

    for i, result in enumerate(all_results):
        sig_raw = "significant" if result.is_significant() else "not significant"
        sig_corr = "significant" if significant_corrected[i] else "not significant"

        lines.append(f"### {result.condition_a} vs {result.condition_b}")
        lines.append("")
        lines.append(f"- Difference: {result.mean_a:.3f} - {result.mean_b:.3f} = "
                    f"{result.mean_a - result.mean_b:.3f}")
        lines.append(f"- Welch's t-test: {result.format_stat_markers()}")
        lines.append(f"- Mann-Whitney U: U={result.u_statistic:.1f}, "
                    f"p={result.p_value_mann_whitney:.4f}")
        lines.append(f"- Raw: {sig_raw} | Holm-Bonferroni: {sig_corr}")

        d_interp = "negligible"
        abs_d = abs(result.cohens_d)
        if abs_d >= 0.8:
            d_interp = "large"
        elif abs_d >= 0.5:
            d_interp = "medium"
        elif abs_d >= 0.2:
            d_interp = "small"
        lines.append(f"- Effect size: {d_interp} (d={result.cohens_d:.2f})")
        lines.append("")

    # Trust level
    trust = assess_trust_level(all_results, diag.overall_pass)
    lines.append("## Verdict")
    lines.append("")
    lines.append(f"**Trust Level: {trust}**")
    lines.append("")

    if trust == "HIGH":
        lines.append("Evidence is strong. Findings can be adopted to FINDINGS.md.")
    elif trust == "MEDIUM":
        lines.append("Evidence is moderate. Tentative adoption recommended with follow-up.")
    elif trust == "LOW":
        lines.append("Evidence is weak. Exploratory only, do not adopt.")
    else:
        lines.append("Insufficient evidence. Results are untrusted.")

    lines.append("")

    report = "\n".join(lines)

    # Write report
    report_path = out_dir / f"EXPERIMENT_REPORT_{experiment_id.replace('-', '_')}.md"
    report_path.write_text(report)
    logger.info(f"Report written to {report_path}")

    return report
