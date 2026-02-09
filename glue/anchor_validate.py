"""DOE-021 Anchor Validation Pilot.

Runs 5 episodes each on G01 (burst_3_base), G03 (adaptive_base), G10 (random_baseline)
to verify genome mapping matches DOE-020 baselines before full 300-episode execution.

Usage:
    python3 -m glue.anchor_validate
"""
import logging
import statistics
import sys

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


# DOE-020 baselines for comparison
BASELINES = {
    "G01_burst_3_base": {"kills_mean": 15.40, "kills_sd": 5.93, "kr_mean": 45.44},
    "G03_adaptive_base": {"kills_mean": 13.03, "kills_sd": 4.59, "kr_mean": 45.97},
    "G10_random_baseline": {"kills_mean": 13.27, "kills_sd": 4.22, "kr_mean": 42.40},
}

# Genome definitions (subset of DOE-021)
ANCHOR_GENOMES = {
    "G01_burst_3_base": {
        "burst_length": 3, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 0, "health_threshold_low": 0,
        "stagnation_window": 0, "attack_probability": 0.75, "adaptive_enabled": False,
    },
    "G03_adaptive_base": {
        "burst_length": 3, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 50, "health_threshold_low": 25,
        "stagnation_window": 5, "attack_probability": 0.80, "adaptive_enabled": True,
    },
    "G10_random_baseline": {
        "burst_length": 3, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 0, "health_threshold_low": 0,
        "stagnation_window": 0, "attack_probability": 0.50, "adaptive_enabled": False,
    },
}

PILOT_SEEDS = [23001, 23092, 23183, 23274, 23365]


def run_anchor_validation() -> bool:
    """Run anchor validation and return True if all anchors pass."""
    from glue.action_functions import GenomeAction
    from glue.episode_runner import EpisodeRunner
    from glue.vizdoom_bridge import VizDoomBridge

    logger.info("=" * 60)
    logger.info("DOE-021 ANCHOR VALIDATION PILOT")
    logger.info("Seeds: %s", PILOT_SEEDS)
    logger.info("=" * 60)

    bridge = VizDoomBridge(scenario="defend_the_line.cfg", num_actions=3)
    runner = EpisodeRunner(bridge)

    all_pass = True
    results_summary = []

    for genome_name, genome_params in ANCHOR_GENOMES.items():
        logger.info("-" * 50)
        logger.info("Testing %s", genome_name)
        action_fn = GenomeAction(**genome_params)

        kills_list = []
        kr_list = []
        survival_list = []

        for i, seed in enumerate(PILOT_SEEDS):
            action_fn.reset(seed=seed)
            result = runner.run_episode(
                seed=seed,
                condition=genome_name,
                episode_number=i + 1,
                action_fn=action_fn,
            )
            k = result.metrics.kills
            st = result.metrics.survival_time
            kr = (k / st * 60.0) if st > 0 else 0.0
            kills_list.append(k)
            kr_list.append(kr)
            survival_list.append(st)
            logger.info(
                "  Episode %d (seed=%d): kills=%d, survival=%.1f, kr=%.1f",
                i + 1, seed, k, st, kr,
            )

        # Compute pilot statistics
        pilot_kills_mean = statistics.mean(kills_list)
        pilot_kr_mean = statistics.mean(kr_list)
        pilot_survival_mean = statistics.mean(survival_list)

        # Compare against baseline
        baseline = BASELINES[genome_name]
        kills_deviation = abs(pilot_kills_mean - baseline["kills_mean"]) / baseline["kills_sd"]

        status = "PASS" if kills_deviation <= 2.0 else "FAIL"
        if status == "FAIL":
            all_pass = False

        results_summary.append({
            "genome": genome_name,
            "pilot_kills": pilot_kills_mean,
            "pilot_kr": pilot_kr_mean,
            "pilot_survival": pilot_survival_mean,
            "baseline_kills": baseline["kills_mean"],
            "baseline_sd": baseline["kills_sd"],
            "deviation_sd": kills_deviation,
            "status": status,
        })

        logger.info(
            "  RESULT: kills=%.1f (baseline=%.1f, SD=%.2f), "
            "deviation=%.2f SD → %s",
            pilot_kills_mean, baseline["kills_mean"],
            baseline["kills_sd"], kills_deviation, status,
        )

    bridge.close()

    # Final summary
    logger.info("=" * 60)
    logger.info("ANCHOR VALIDATION SUMMARY")
    logger.info("=" * 60)
    for r in results_summary:
        logger.info(
            "  %-25s kills=%.1f (baseline=%.1f ± %.1f) dev=%.2f SD → %s",
            r["genome"], r["pilot_kills"], r["baseline_kills"],
            r["baseline_sd"], r["deviation_sd"], r["status"],
        )

    if all_pass:
        logger.info("ALL ANCHORS PASS — safe to proceed with full DOE-021 execution")
    else:
        logger.error("ANCHOR VALIDATION FAILED — investigate genome mapping before proceeding")

    return all_pass


if __name__ == "__main__":
    ok = run_anchor_validation()
    sys.exit(0 if ok else 1)
