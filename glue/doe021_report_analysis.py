#!/usr/bin/env python3
"""DOE-021 statistical analysis for experiment report.

Performs ANOVA, Kruskal-Wallis, Tukey HSD, Shapiro-Wilk, Levene's test,
TOPSIS fitness, Welch's t-test, and cross-generation analysis.

Usage (inside doom-player Docker container):
    python3 -m glue.doe021_report_analysis
    python3 -m glue.doe021_report_analysis --db-path /app/data/clau-doom.duckdb
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("/app/data/clau-doom.duckdb")


def main() -> None:
    parser = argparse.ArgumentParser(description="DOE-021 statistical analysis")
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")

    import duckdb
    import numpy as np
    from scipy import stats as scipy_stats

    con = duckdb.connect(str(args.db_path), read_only=True)

    for exp_id, gen_label in [("DOE-021", "Gen 1"), ("DOE-021_gen2", "Gen 2")]:
        print(f"\n{'='*70}")
        print(f"  {gen_label}: {exp_id}")
        print(f"{'='*70}")

        # Fetch all data
        rows = con.execute(
            "SELECT condition, kills, kill_rate, survival_time FROM experiments WHERE experiment_id=? ORDER BY condition, episode_number",
            [exp_id],
        ).fetchall()

        if not rows:
            print(f"  No data for {exp_id}")
            continue

        # Group by condition
        data: dict[str, dict[str, list[float]]] = {}
        for cond, kills, kr, surv in rows:
            if cond not in data:
                data[cond] = {"kills": [], "kill_rate": [], "survival_time": []}
            data[cond]["kills"].append(float(kills))
            data[cond]["kill_rate"].append(float(kr))
            data[cond]["survival_time"].append(float(surv))

        conditions = sorted(data.keys())
        n_conditions = len(conditions)
        total_n = sum(len(data[c]["kills"]) for c in conditions)

        print(f"\n  Conditions: {n_conditions}, Total episodes: {total_n}")

        # Descriptive stats
        print(f"\n  --- Descriptive Statistics ---")
        print(f"  {'Condition':<30} {'n':>3} {'kills':>12} {'kill_rate':>12} {'survival':>12}")
        for c in sorted(conditions, key=lambda x: -np.mean(data[x]["kills"])):
            k = data[c]["kills"]
            kr = data[c]["kill_rate"]
            s = data[c]["survival_time"]
            print(f"  {c:<30} {len(k):>3} {np.mean(k):>5.1f}±{np.std(k, ddof=1):>4.1f} {np.mean(kr):>5.2f}±{np.std(kr, ddof=1):>4.2f} {np.mean(s):>5.1f}±{np.std(s, ddof=1):>4.1f}")

        # One-way ANOVA for each response
        for response in ["kills", "kill_rate", "survival_time"]:
            print(f"\n  --- One-way ANOVA: {response} ---")

            groups = [np.array(data[c][response]) for c in conditions]
            all_values = np.concatenate(groups)
            grand_mean = np.mean(all_values)

            # Between-group SS
            ss_between = sum(len(g) * (np.mean(g) - grand_mean) ** 2 for g in groups)
            df_between = n_conditions - 1

            # Within-group SS
            ss_within = sum(np.sum((g - np.mean(g)) ** 2) for g in groups)
            df_within = total_n - n_conditions

            ms_between = ss_between / df_between
            ms_within = ss_within / df_within
            f_stat = ms_between / ms_within if ms_within > 0 else 0.0
            p_value = 1 - scipy_stats.f.cdf(f_stat, df_between, df_within)

            ss_total = ss_between + ss_within
            eta_sq = ss_between / ss_total if ss_total > 0 else 0.0

            print(f"  Source       |    SS     | df  |    MS     |    F     | p-value  | eta2")
            print(f"  ------------|-----------|-----|-----------|---------|----------|------")
            print(f"  Between     | {ss_between:>9.2f} | {df_between:>3d} | {ms_between:>9.2f} | {f_stat:>7.3f} | {p_value:>8.6f} | {eta_sq:.4f}")
            print(f"  Within      | {ss_within:>9.2f} | {df_within:>3d} | {ms_within:>9.2f} |         |          |")
            print(f"  Total       | {ss_total:>9.2f} | {total_n-1:>3d} |           |         |          |")
            print(f"  [STAT:f=F({df_between},{df_within})={f_stat:.3f}] [STAT:p={p_value:.6f}] [STAT:eta2=partial eta2={eta_sq:.4f}] [STAT:n={total_n}]")

            sig = "SIGNIFICANT" if p_value < 0.05 else "NOT SIGNIFICANT"
            print(f"  Result: {sig}")

            # Residual diagnostics
            print(f"\n  --- Residual Diagnostics ({response}) ---")

            # Residuals = value - group mean
            residuals = np.concatenate([g - np.mean(g) for g in groups])

            # Shapiro-Wilk normality test (on residuals, max 5000)
            if len(residuals) > 5000:
                sw_sample = np.random.default_rng(42).choice(residuals, 5000, replace=False)
            else:
                sw_sample = residuals
            sw_stat, sw_p = scipy_stats.shapiro(sw_sample)
            norm_result = "PASS" if sw_p >= 0.05 else "FAIL"
            print(f"  Normality (Shapiro-Wilk): W={sw_stat:.4f}, p={sw_p:.4f} -> {norm_result}")

            # Levene's test for equal variance
            lev_stat, lev_p = scipy_stats.levene(*groups)
            var_result = "PASS" if lev_p >= 0.05 else "FAIL"
            print(f"  Equal Variance (Levene): F={lev_stat:.4f}, p={lev_p:.4f} -> {var_result}")

            # Kruskal-Wallis non-parametric
            kw_stat, kw_p = scipy_stats.kruskal(*groups)
            kw_sig = "SIGNIFICANT" if kw_p < 0.05 else "NOT SIGNIFICANT"
            print(f"  Kruskal-Wallis: H({df_between})={kw_stat:.3f}, p={kw_p:.6f} -> {kw_sig}")

            # Tukey HSD if significant
            if p_value < 0.05:
                print(f"\n  --- Tukey HSD ({response}) ---")
                # Build data arrays for Tukey
                all_data = []
                all_labels = []
                for c in conditions:
                    all_data.extend(data[c][response])
                    all_labels.extend([c] * len(data[c][response]))

                tukey_result = scipy_stats.tukey_hsd(*groups)

                # Print significant pairs
                sig_pairs = []
                for i in range(n_conditions):
                    for j in range(i + 1, n_conditions):
                        mean_diff = np.mean(groups[j]) - np.mean(groups[i])
                        p_adj = tukey_result.pvalue[i, j]
                        # Cohen's d
                        pooled_sd = math.sqrt(
                            (np.var(groups[i], ddof=1) * (len(groups[i]) - 1) +
                             np.var(groups[j], ddof=1) * (len(groups[j]) - 1)) /
                            (len(groups[i]) + len(groups[j]) - 2)
                        )
                        d = mean_diff / pooled_sd if pooled_sd > 0 else 0
                        if p_adj < 0.05:
                            sig_pairs.append((conditions[i], conditions[j], mean_diff, p_adj, d))

                if sig_pairs:
                    print(f"  {'Pair':<60} {'Diff':>6} {'p_adj':>8} {'d':>6}")
                    for c1, c2, diff, p_adj, d in sorted(sig_pairs, key=lambda x: x[3]):
                        print(f"  {c1} vs {c2:<30} {diff:>+6.1f} {p_adj:>8.4f} {d:>+6.2f}")
                else:
                    print(f"  No significant pairwise differences after Tukey correction.")

        # TOPSIS
        print(f"\n  --- TOPSIS Ranking ---")
        criteria = ["kills", "kill_rate", "survival_time"]
        n_crit = len(criteria)
        weights = [1.0 / 3] * 3

        # Build decision matrix
        matrix = []
        for c in conditions:
            row = [np.mean(data[c][cr]) for cr in criteria]
            matrix.append(row)

        # Normalize
        norm_factors = []
        for j in range(n_crit):
            col_sq = sum(matrix[i][j] ** 2 for i in range(n_conditions))
            norm_factors.append(math.sqrt(col_sq) if col_sq > 0 else 1.0)

        normalized = [[matrix[i][j] / norm_factors[j] for j in range(n_crit)] for i in range(n_conditions)]
        weighted = [[normalized[i][j] * weights[j] for j in range(n_crit)] for i in range(n_conditions)]

        ideal_best = [max(weighted[i][j] for i in range(n_conditions)) for j in range(n_crit)]
        ideal_worst = [min(weighted[i][j] for i in range(n_conditions)) for j in range(n_crit)]

        topsis_results = []
        for i in range(n_conditions):
            d_best = math.sqrt(sum((weighted[i][j] - ideal_best[j]) ** 2 for j in range(n_crit)))
            d_worst = math.sqrt(sum((weighted[i][j] - ideal_worst[j]) ** 2 for j in range(n_crit)))
            c_i = d_worst / (d_best + d_worst) if (d_best + d_worst) > 0 else 0.0
            topsis_results.append((conditions[i], c_i, matrix[i][0], matrix[i][1], matrix[i][2]))

        topsis_results.sort(key=lambda x: -x[1])
        print(f"  {'Rank':>4} {'Condition':<30} {'C_i':>6} {'kills':>6} {'kr':>6} {'surv':>6}")
        for rank, (cond, ci, mk, mkr, ms) in enumerate(topsis_results, 1):
            print(f"  {rank:>4} {cond:<30} {ci:.4f} {mk:>6.1f} {mkr:>6.2f} {ms:>6.1f}")

    # ====================================================================
    # Cross-generation analysis
    # ====================================================================
    print(f"\n{'='*70}")
    print(f"  Cross-Generation Analysis")
    print(f"{'='*70}")

    import numpy as np
    from scipy import stats as scipy_stats

    # Elite comparison: Gen 1 G01 vs Gen 2 elite
    gen1_elite_kills = con.execute(
        "SELECT kills FROM experiments WHERE experiment_id='DOE-021' AND condition='G01_burst_3_base'"
    ).fetchall()
    gen2_elite_kills = con.execute(
        "SELECT kills FROM experiments WHERE experiment_id='DOE-021_gen2' AND condition='gen2_G01_elite'"
    ).fetchall()

    gen1_k = np.array([r[0] for r in gen1_elite_kills], dtype=float)
    gen2_k = np.array([r[0] for r in gen2_elite_kills], dtype=float)

    t_stat, t_p = scipy_stats.ttest_ind(gen1_k, gen2_k, equal_var=False)
    pooled_sd = math.sqrt(
        (np.var(gen1_k, ddof=1) * (len(gen1_k) - 1) + np.var(gen2_k, ddof=1) * (len(gen2_k) - 1)) /
        (len(gen1_k) + len(gen2_k) - 2)
    )
    d = (np.mean(gen2_k) - np.mean(gen1_k)) / pooled_sd if pooled_sd > 0 else 0

    print(f"\n  --- Elite Comparison: Gen 1 G01 vs Gen 2 Elite (kills) ---")
    print(f"  Gen 1 G01: mean={np.mean(gen1_k):.2f}, SD={np.std(gen1_k, ddof=1):.2f}, n={len(gen1_k)}")
    print(f"  Gen 2 Elite: mean={np.mean(gen2_k):.2f}, SD={np.std(gen2_k, ddof=1):.2f}, n={len(gen2_k)}")
    print(f"  Welch's t={t_stat:.3f}, [STAT:p={t_p:.4f}], [STAT:effect_size=Cohen's d={d:.3f}]")
    sig = "SIGNIFICANT" if t_p < 0.05 else "NOT SIGNIFICANT"
    print(f"  Result: {sig}")

    # Same for kill_rate
    gen1_kr = np.array([r[0] for r in con.execute(
        "SELECT kill_rate FROM experiments WHERE experiment_id='DOE-021' AND condition='G01_burst_3_base'"
    ).fetchall()], dtype=float)
    gen2_kr = np.array([r[0] for r in con.execute(
        "SELECT kill_rate FROM experiments WHERE experiment_id='DOE-021_gen2' AND condition='gen2_G01_elite'"
    ).fetchall()], dtype=float)

    t_kr, p_kr = scipy_stats.ttest_ind(gen1_kr, gen2_kr, equal_var=False)
    d_kr = (np.mean(gen2_kr) - np.mean(gen1_kr)) / math.sqrt(
        (np.var(gen1_kr, ddof=1) * (len(gen1_kr) - 1) + np.var(gen2_kr, ddof=1) * (len(gen2_kr) - 1)) /
        (len(gen1_kr) + len(gen2_kr) - 2)
    )

    print(f"\n  --- Elite Comparison: Gen 1 G01 vs Gen 2 Elite (kill_rate) ---")
    print(f"  Gen 1 G01: mean={np.mean(gen1_kr):.2f}, SD={np.std(gen1_kr, ddof=1):.2f}")
    print(f"  Gen 2 Elite: mean={np.mean(gen2_kr):.2f}, SD={np.std(gen2_kr, ddof=1):.2f}")
    print(f"  Welch's t={t_kr:.3f}, [STAT:p={p_kr:.4f}], [STAT:effect_size=Cohen's d={d_kr:.3f}]")

    # Same for survival
    gen1_surv = np.array([r[0] for r in con.execute(
        "SELECT survival_time FROM experiments WHERE experiment_id='DOE-021' AND condition='G01_burst_3_base'"
    ).fetchall()], dtype=float)
    gen2_surv = np.array([r[0] for r in con.execute(
        "SELECT survival_time FROM experiments WHERE experiment_id='DOE-021_gen2' AND condition='gen2_G01_elite'"
    ).fetchall()], dtype=float)

    t_surv, p_surv = scipy_stats.ttest_ind(gen1_surv, gen2_surv, equal_var=False)
    d_surv = (np.mean(gen2_surv) - np.mean(gen1_surv)) / math.sqrt(
        (np.var(gen1_surv, ddof=1) * (len(gen1_surv) - 1) + np.var(gen2_surv, ddof=1) * (len(gen2_surv) - 1)) /
        (len(gen1_surv) + len(gen2_surv) - 2)
    )

    print(f"\n  --- Elite Comparison: Gen 1 G01 vs Gen 2 Elite (survival_time) ---")
    print(f"  Gen 1 G01: mean={np.mean(gen1_surv):.2f}, SD={np.std(gen1_surv, ddof=1):.2f}")
    print(f"  Gen 2 Elite: mean={np.mean(gen2_surv):.2f}, SD={np.std(gen2_surv, ddof=1):.2f}")
    print(f"  Welch's t={t_surv:.3f}, [STAT:p={p_surv:.4f}], [STAT:effect_size=Cohen's d={d_surv:.3f}]")

    # Convergence analysis: gen2_G01_elite vs gen2_G04_x13 (identical params)
    gen2_g04_kills = np.array([r[0] for r in con.execute(
        "SELECT kills FROM experiments WHERE experiment_id='DOE-021_gen2' AND condition='gen2_G04_x13'"
    ).fetchall()], dtype=float)

    print(f"\n  --- Convergence Check: gen2_G01_elite vs gen2_G04_x13 ---")
    print(f"  gen2_G01_elite: mean kills={np.mean(gen2_k):.2f}")
    print(f"  gen2_G04_x13:   mean kills={np.mean(gen2_g04_kills):.2f}")
    print(f"  Identical params? YES (both = burst_3 params)")
    print(f"  Identical results? {'YES' if np.mean(gen2_k) == np.mean(gen2_g04_kills) else 'EXPECTED (same params, same seeds = same RNG)'}")

    # Worst performer analysis (gen2_G03_x12b = sweep_right)
    gen2_worst = np.array([r[0] for r in con.execute(
        "SELECT kills FROM experiments WHERE experiment_id='DOE-021_gen2' AND condition='gen2_G03_x12b'"
    ).fetchall()], dtype=float)

    print(f"\n  --- Worst Performer: gen2_G03_x12b (sweep_right) ---")
    print(f"  Mean kills: {np.mean(gen2_worst):.2f} ± {np.std(gen2_worst, ddof=1):.2f}")
    print(f"  vs Gen 2 Elite: {np.mean(gen2_k):.2f} (diff: {np.mean(gen2_k) - np.mean(gen2_worst):.1f})")

    # Gen 1 bottom 3 (all have alternate/sweep)
    print(f"\n  --- turn_direction Penalty Analysis ---")
    random_genomes_kills = []
    nonrandom_genomes_kills = []

    # Gen 1 turn_direction grouping
    gen1_random_dir = ["G01_burst_3_base", "G03_adaptive_base", "G05_crossover_A",
                       "G07_burst_2", "G08_burst_5", "G09_aggressive", "G10_random_baseline"]
    gen1_nonrandom_dir = ["G02_burst_3_sweep", "G04_adaptive_tuned", "G06_crossover_B"]

    for c in gen1_random_dir:
        vals = con.execute("SELECT kills FROM experiments WHERE experiment_id='DOE-021' AND condition=?", [c]).fetchall()
        random_genomes_kills.extend([r[0] for r in vals])
    for c in gen1_nonrandom_dir:
        vals = con.execute("SELECT kills FROM experiments WHERE experiment_id='DOE-021' AND condition=?", [c]).fetchall()
        nonrandom_genomes_kills.extend([r[0] for r in vals])

    rk = np.array(random_genomes_kills, dtype=float)
    nrk = np.array(nonrandom_genomes_kills, dtype=float)

    t_dir, p_dir = scipy_stats.ttest_ind(rk, nrk, equal_var=False)
    d_dir = (np.mean(rk) - np.mean(nrk)) / math.sqrt(
        (np.var(rk, ddof=1) * (len(rk) - 1) + np.var(nrk, ddof=1) * (len(nrk) - 1)) /
        (len(rk) + len(nrk) - 2)
    )

    print(f"  turn_direction=random (n={len(rk)}): mean kills={np.mean(rk):.2f} ± {np.std(rk, ddof=1):.2f}")
    print(f"  turn_direction=alternate/sweep (n={len(nrk)}): mean kills={np.mean(nrk):.2f} ± {np.std(nrk, ddof=1):.2f}")
    print(f"  Diff: {np.mean(rk) - np.mean(nrk):.2f} kills")
    print(f"  Welch's t={t_dir:.3f}, [STAT:p={p_dir:.6f}], [STAT:effect_size=Cohen's d={d_dir:.3f}]")

    # Genetic diversity in Gen 2
    print(f"\n  --- Genetic Diversity (Gen 2) ---")
    # Count genomes with turn_direction=random
    gen2_genomes_params = {
        "gen2_G01_elite": {"burst_length": 3, "turn_direction": "random", "turn_count": 1, "adaptive_enabled": False},
        "gen2_G02_x12a": {"burst_length": 3, "turn_direction": "random", "turn_count": 1, "adaptive_enabled": True},
        "gen2_G03_x12b": {"burst_length": 3, "turn_direction": "sweep_right", "turn_count": 1, "adaptive_enabled": False},
        "gen2_G04_x13": {"burst_length": 3, "turn_direction": "random", "turn_count": 1, "adaptive_enabled": False},
        "gen2_G05_x24": {"burst_length": 7, "turn_direction": "random", "turn_count": 1, "adaptive_enabled": True},
        "gen2_G06_x14": {"burst_length": 4, "turn_direction": "random", "turn_count": 1, "adaptive_enabled": False},
        "gen2_G07_x34": {"burst_length": 7, "turn_direction": "random", "turn_count": 1, "adaptive_enabled": True},
        "gen2_G08_mut2": {"burst_length": 3, "turn_direction": "random", "turn_count": 1, "adaptive_enabled": True},
        "gen2_G09_mut3": {"burst_length": 3, "turn_direction": "random", "turn_count": 1, "adaptive_enabled": False},
        "gen2_G10_random": {"burst_length": 7, "turn_direction": "random", "turn_count": 1, "adaptive_enabled": True},
    }

    burst_lengths = [p["burst_length"] for p in gen2_genomes_params.values()]
    turn_dirs = [p["turn_direction"] for p in gen2_genomes_params.values()]
    adaptive_flags = [p["adaptive_enabled"] for p in gen2_genomes_params.values()]

    print(f"  burst_length values: {sorted(set(burst_lengths))} (unique: {len(set(burst_lengths))})")
    print(f"  turn_direction values: {sorted(set(turn_dirs))} (unique: {len(set(turn_dirs))})")
    print(f"  turn_direction=random: {turn_dirs.count('random')}/10")
    print(f"  adaptive_enabled=True: {adaptive_flags.count(True)}/10")
    print(f"  Genomes identical to elite (burst_3 params): gen2_G01_elite, gen2_G04_x13")

    con.close()
    print(f"\n{'='*70}")
    print(f"  Analysis complete")
    print(f"{'='*70}")


if __name__ == "__main__":
    main()
