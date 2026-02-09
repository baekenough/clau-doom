#!/usr/bin/env python3
"""
DOE-021 Gen 1 Statistical Analysis Script

Performs:
1. One-way ANOVA on kills, kill_rate, survival_time
2. Effect sizes (partial eta-squared)
3. Residual diagnostics (normality, equal variance)
4. Tukey HSD pairwise comparisons
5. TOPSIS fitness computation

Run inside Docker container with access to /app/data/clau-doom.duckdb
"""

import sys
from typing import Dict, List, Tuple

import duckdb
import numpy as np
from scipy import stats
from statsmodels.stats.multicomp import pairwise_tukeyhsd


def load_experiment_data(db_path: str, experiment_id: str) -> duckdb.DuckDBPyConnection:
    """Connect to DuckDB and verify experiment data exists."""
    conn = duckdb.connect(db_path, read_only=True)

    # Check if data exists
    result = conn.execute("""
        SELECT COUNT(*) as n
        FROM experiments
        WHERE experiment_id = ?
    """, [experiment_id]).fetchone()

    if result[0] == 0:
        raise ValueError(f"No data found for experiment_id={experiment_id}")

    print(f"[Data] Found {result[0]} episodes for {experiment_id}")
    return conn


def compute_kill_rate(conn: duckdb.DuckDBPyConnection, experiment_id: str) -> None:
    """Add computed kill_rate column (kills / survival_time * 60)."""
    # Note: DuckDB connection is read_only, so we'll compute in memory
    pass  # kill_rate computed in query below


def fetch_data_by_condition(
    conn: duckdb.DuckDBPyConnection,
    experiment_id: str,
) -> Dict[str, np.ndarray]:
    """
    Fetch data grouped by condition.

    Returns:
        Dict mapping condition -> array of metric values
        Format: {
            'kills': {condition: [values...]},
            'kill_rate': {condition: [values...]},
            'survival_time': {condition: [values...]}
        }
    """
    query = """
        SELECT
            condition,
            kills,
            CASE
                WHEN survival_time > 0 THEN kills / survival_time * 60.0
                ELSE 0.0
            END as kill_rate,
            survival_time
        FROM experiments
        WHERE experiment_id = ?
        ORDER BY condition, episode_number
    """

    df = conn.execute(query, [experiment_id]).fetchdf()

    # Group by condition
    data = {
        'kills': {},
        'kill_rate': {},
        'survival_time': {}
    }

    for condition in df['condition'].unique():
        mask = df['condition'] == condition
        data['kills'][condition] = df.loc[mask, 'kills'].values
        data['kill_rate'][condition] = df.loc[mask, 'kill_rate'].values
        data['survival_time'][condition] = df.loc[mask, 'survival_time'].values

    print(f"[Data] Loaded {len(data['kills'])} conditions")
    for cond in sorted(data['kills'].keys()):
        n = len(data['kills'][cond])
        print(f"  {cond}: n={n} episodes")

    return data, df


def one_way_anova(
    data_by_condition: Dict[str, np.ndarray],
    metric_name: str,
) -> Dict[str, float]:
    """
    Perform one-way ANOVA using scipy.stats.f_oneway.

    Returns:
        Dict with F-statistic, p-value, df_between, df_within
    """
    groups = list(data_by_condition.values())

    # ANOVA
    f_stat, p_value = stats.f_oneway(*groups)

    # Degrees of freedom
    k = len(groups)  # number of groups
    n = sum(len(g) for g in groups)  # total observations
    df_between = k - 1
    df_within = n - k

    return {
        'metric': metric_name,
        'F': f_stat,
        'p': p_value,
        'df_between': df_between,
        'df_within': df_within,
    }


def compute_effect_size(data_by_condition: Dict[str, np.ndarray]) -> float:
    """
    Compute partial eta-squared: SS_between / SS_total.

    η² = SS_between / SS_total
    """
    all_data = np.concatenate(list(data_by_condition.values()))
    grand_mean = np.mean(all_data)

    # SS_total
    ss_total = np.sum((all_data - grand_mean) ** 2)

    # SS_between
    ss_between = 0.0
    for group in data_by_condition.values():
        group_mean = np.mean(group)
        n_group = len(group)
        ss_between += n_group * (group_mean - grand_mean) ** 2

    # Partial eta-squared
    if ss_total == 0:
        return 0.0

    eta_squared = ss_between / ss_total
    return eta_squared


def check_normality(residuals: np.ndarray) -> Tuple[float, float]:
    """
    Test residuals for normality using Shapiro-Wilk test.

    Returns:
        (statistic, p_value)
    """
    stat, p = stats.shapiro(residuals)
    return stat, p


def check_equal_variance(data_by_condition: Dict[str, np.ndarray]) -> Tuple[float, float]:
    """
    Test equal variance using Levene test.

    Returns:
        (statistic, p_value)
    """
    groups = list(data_by_condition.values())
    stat, p = stats.levene(*groups, center='median')
    return stat, p


def compute_residuals(data_by_condition: Dict[str, np.ndarray]) -> np.ndarray:
    """
    Compute residuals: observation - group_mean.
    """
    residuals = []
    for group in data_by_condition.values():
        group_mean = np.mean(group)
        residuals.extend(group - group_mean)

    return np.array(residuals)


def tukey_hsd_test(df, response_col: str) -> str:
    """
    Perform Tukey HSD post-hoc test.

    Args:
        df: DataFrame with 'condition' and response column
        response_col: Name of response variable column

    Returns:
        String summary of pairwise comparisons
    """
    result = pairwise_tukeyhsd(
        endog=df[response_col],
        groups=df['condition'],
        alpha=0.05
    )

    return str(result)


def topsis_fitness(
    condition_means: Dict[str, Dict[str, float]],
    weights: List[float] = None,
) -> Dict[str, float]:
    """
    Compute TOPSIS fitness scores.

    Args:
        condition_means: {condition: {'kills': mean, 'kill_rate': mean, 'survival_time': mean}}
        weights: [w_kills, w_kr, w_survival] (default: equal weights)

    Returns:
        {condition: C_i (closeness coefficient)}
    """
    if weights is None:
        weights = [1/3, 1/3, 1/3]

    # Build decision matrix (conditions × criteria)
    conditions = sorted(condition_means.keys())
    matrix = np.array([
        [
            condition_means[cond]['kills'],
            condition_means[cond]['kill_rate'],
            condition_means[cond]['survival_time'],
        ]
        for cond in conditions
    ])

    # Step 1: Normalize matrix (vector normalization)
    norm_matrix = matrix / np.sqrt(np.sum(matrix**2, axis=0))

    # Step 2: Weighted normalized matrix
    weighted_matrix = norm_matrix * weights

    # Step 3: Ideal best and worst
    ideal_best = np.max(weighted_matrix, axis=0)
    ideal_worst = np.min(weighted_matrix, axis=0)

    # Step 4: Distances
    dist_best = np.sqrt(np.sum((weighted_matrix - ideal_best)**2, axis=1))
    dist_worst = np.sqrt(np.sum((weighted_matrix - ideal_worst)**2, axis=1))

    # Step 5: Closeness coefficient
    C_i = dist_worst / (dist_best + dist_worst)

    return {cond: c for cond, c in zip(conditions, C_i)}


def print_anova_table(result: Dict[str, float], eta_squared: float) -> None:
    """Print ANOVA table with statistical markers."""
    print("\n" + "="*70)
    print(f"ANOVA: {result['metric']}")
    print("="*70)
    print(f"F({result['df_between']}, {result['df_within']}) = {result['F']:.4f}")
    print(f"[STAT:p={result['p']:.6f}]")
    print(f"[STAT:f=F({result['df_between']},{result['df_within']})={result['F']:.4f}]")
    print(f"[STAT:eta2=partial η²={eta_squared:.4f}]")

    if result['p'] < 0.001:
        print("Conclusion: HIGHLY SIGNIFICANT (p < 0.001)")
    elif result['p'] < 0.05:
        print("Conclusion: SIGNIFICANT (p < 0.05)")
    else:
        print("Conclusion: NOT SIGNIFICANT (p >= 0.05)")


def print_diagnostics(
    normality_stat: float,
    normality_p: float,
    levene_stat: float,
    levene_p: float,
) -> None:
    """Print residual diagnostics."""
    print("\n" + "="*70)
    print("RESIDUAL DIAGNOSTICS")
    print("="*70)

    print(f"\nNormality Test (Shapiro-Wilk):")
    print(f"  W = {normality_stat:.4f}, p = {normality_p:.4f}")
    if normality_p > 0.05:
        print(f"  ✓ PASS: Residuals are normally distributed (p > 0.05)")
    else:
        print(f"  ✗ FAIL: Residuals not normal (p <= 0.05)")

    print(f"\nEqual Variance Test (Levene):")
    print(f"  W = {levene_stat:.4f}, p = {levene_p:.4f}")
    if levene_p > 0.05:
        print(f"  ✓ PASS: Equal variance assumption met (p > 0.05)")
    else:
        print(f"  ✗ FAIL: Unequal variances detected (p <= 0.05)")


def print_topsis_ranking(
    topsis_scores: Dict[str, float],
    condition_means: Dict[str, Dict[str, float]],
) -> None:
    """Print TOPSIS ranking."""
    print("\n" + "="*70)
    print("TOPSIS FITNESS RANKING")
    print("="*70)
    print(f"\nCriteria: kills (maximize), kill_rate (maximize), survival_time (maximize)")
    print(f"Weights: Equal (0.333, 0.333, 0.333)")
    print()

    # Sort by C_i descending
    ranked = sorted(topsis_scores.items(), key=lambda x: x[1], reverse=True)

    print(f"{'Rank':<6} {'Condition':<15} {'C_i':<10} {'Kills':<10} {'KillRate':<12} {'Survival':<10}")
    print("-" * 70)

    for rank, (condition, c_i) in enumerate(ranked, start=1):
        means = condition_means[condition]
        print(
            f"{rank:<6} {condition:<15} {c_i:.4f}    "
            f"{means['kills']:>6.1f}    {means['kill_rate']:>8.2f}    {means['survival_time']:>8.1f}"
        )

    print("\n" + "="*70)
    print("TOP 4 PARENTS FOR GEN 2")
    print("="*70)
    for rank, (condition, c_i) in enumerate(ranked[:4], start=1):
        print(f"{rank}. {condition} (C_i = {c_i:.4f})")


def main():
    """Main analysis workflow."""
    db_path = "/app/data/clau-doom.duckdb"
    experiment_id = "DOE-021"

    print(f"{'='*70}")
    print(f"DOE-021 Gen 1 Statistical Analysis")
    print(f"{'='*70}\n")

    # Step 1: Load data
    conn = load_experiment_data(db_path, experiment_id)
    data, df = fetch_data_by_condition(conn, experiment_id)

    # Step 2: ANOVA for each metric
    metrics = ['kills', 'kill_rate', 'survival_time']
    anova_results = {}

    for metric in metrics:
        print(f"\n{'='*70}")
        print(f"Analyzing: {metric}")
        print(f"{'='*70}")

        # ANOVA
        result = one_way_anova(data[metric], metric)
        eta_squared = compute_effect_size(data[metric])

        print_anova_table(result, eta_squared)
        anova_results[metric] = result

        # Residual diagnostics
        residuals = compute_residuals(data[metric])
        norm_stat, norm_p = check_normality(residuals)
        levene_stat, levene_p = check_equal_variance(data[metric])

        print_diagnostics(norm_stat, norm_p, levene_stat, levene_p)

    # Step 3: Tukey HSD for kills
    print(f"\n{'='*70}")
    print("TUKEY HSD POST-HOC TEST: kills")
    print(f"{'='*70}\n")
    tukey_result = tukey_hsd_test(df, 'kills')
    print(tukey_result)

    # Step 4: TOPSIS
    condition_means = {}
    for condition in sorted(data['kills'].keys()):
        condition_means[condition] = {
            'kills': np.mean(data['kills'][condition]),
            'kill_rate': np.mean(data['kill_rate'][condition]),
            'survival_time': np.mean(data['survival_time'][condition]),
        }

    topsis_scores = topsis_fitness(condition_means)
    print_topsis_ranking(topsis_scores, condition_means)

    # Close connection
    conn.close()

    print(f"\n{'='*70}")
    print("ANALYSIS COMPLETE")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        sys.exit(1)
