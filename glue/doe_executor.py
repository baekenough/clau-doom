#!/usr/bin/env python3
"""Reusable DOE experiment executor for real VizDoom gameplay.

Runs factorial and center-point experiments with injected factor levels,
recording all results via DuckDBWriter for subsequent ANOVA analysis.

Usage (inside doom-player Docker container):
    python3 -m glue.doe_executor --experiment DOE-005

Design:
    1. ExperimentConfig / RunConfig dataclasses define the full design matrix
    2. build_doe005_config() constructs the DOE-005 specific design
    3. execute_experiment() orchestrates VizDoom episodes in randomized run order
    4. Supports resumption: skips already-completed episodes via DuckDBWriter
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("data/clau-doom.duckdb")


# ---------------------------------------------------------------------------
# Configuration dataclasses
# ---------------------------------------------------------------------------


@dataclass
class RunConfig:
    """Configuration for a single DOE run (one factor-level combination)."""

    run_id: str  # e.g., "DOE-005-R1" or "DOE-005-CP1"
    run_label: str  # e.g., "R1" or "CP1"
    memory_weight: float
    strength_weight: float
    seeds: list[int]
    condition: str  # e.g., "memory=0.7_strength=0.7"
    run_type: str  # "factorial" or "center"
    action_type: str = "full_agent"  # "random", "rule_only", "l0_memory", "l0_strength", "full_agent"


@dataclass
class ExperimentConfig:
    """Full DOE experiment configuration."""

    experiment_id: str
    runs: list[RunConfig]  # In randomized execution order
    seed_set: list[int]  # Complete seed pool
    seed_formula: str
    scenario: str = "defend_the_center.cfg"
    db_path: Path = field(default_factory=lambda: DEFAULT_DB_PATH)


# ---------------------------------------------------------------------------
# DOE-005 configuration builder
# ---------------------------------------------------------------------------


def _generate_seed_set(
    n: int = 30, base: int = 2501, step: int = 23
) -> list[int]:
    """Generate deterministic seed set: seed_i = base + i * step."""
    return [base + i * step for i in range(n)]


def build_doe005_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-005: 2^2 factorial + 3 center points.

    Factors:
        Memory:   [0.7, 0.9], center 0.8
        Strength: [0.7, 0.9], center 0.8

    Seed formula: seed_i = 2501 + i * 23, i=0..29

    Randomized run order: 4, CP1, 2, 1, CP3, 3, CP2
    """
    seeds = _generate_seed_set(n=30, base=2501, step=23)
    exp_id = "DOE-005"

    # Define all runs (will be reordered below)
    run1 = RunConfig(
        run_id=f"{exp_id}-R1",
        run_label="R1",
        memory_weight=0.7,
        strength_weight=0.7,
        seeds=list(seeds),  # all 30
        condition="memory=0.7_strength=0.7",
        run_type="factorial",
    )
    run2 = RunConfig(
        run_id=f"{exp_id}-R2",
        run_label="R2",
        memory_weight=0.9,
        strength_weight=0.7,
        seeds=list(seeds),
        condition="memory=0.9_strength=0.7",
        run_type="factorial",
    )
    run3 = RunConfig(
        run_id=f"{exp_id}-R3",
        run_label="R3",
        memory_weight=0.7,
        strength_weight=0.9,
        seeds=list(seeds),
        condition="memory=0.7_strength=0.9",
        run_type="factorial",
    )
    run4 = RunConfig(
        run_id=f"{exp_id}-R4",
        run_label="R4",
        memory_weight=0.9,
        strength_weight=0.9,
        seeds=list(seeds),
        condition="memory=0.9_strength=0.9",
        run_type="factorial",
    )
    cp1 = RunConfig(
        run_id=f"{exp_id}-CP1",
        run_label="CP1",
        memory_weight=0.8,
        strength_weight=0.8,
        seeds=seeds[0:10],
        condition="memory=0.8_strength=0.8",
        run_type="center",
    )
    cp2 = RunConfig(
        run_id=f"{exp_id}-CP2",
        run_label="CP2",
        memory_weight=0.8,
        strength_weight=0.8,
        seeds=seeds[10:20],
        condition="memory=0.8_strength=0.8",
        run_type="center",
    )
    cp3 = RunConfig(
        run_id=f"{exp_id}-CP3",
        run_label="CP3",
        memory_weight=0.8,
        strength_weight=0.8,
        seeds=seeds[20:30],
        condition="memory=0.8_strength=0.8",
        run_type="center",
    )

    # Randomized run order from EXPERIMENT_ORDER_005.md:
    # Execution order: 4, CP1, 2, 1, CP3, 3, CP2
    randomized_runs = [run4, cp1, run2, run1, cp3, run3, cp2]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=randomized_runs,
        seed_set=seeds,
        seed_formula="seed_i = 2501 + i * 23, i=0..29",
        scenario="defend_the_center.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe006_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-006: 2^2 factorial + 3 center points.

    Factors:
        Memory:   [0.3, 0.7], center 0.5
        Strength: [0.3, 0.7], center 0.5

    Seed formula: seed_i = 3501 + i * 29, i=0..29

    Randomized run order: R3, CP2, R1, R4, CP1, R2, CP3
    """
    seeds = _generate_seed_set(n=30, base=3501, step=29)
    exp_id = "DOE-006"

    # Define all runs (will be reordered below)
    run1 = RunConfig(
        run_id=f"{exp_id}-R1",
        run_label="R1",
        memory_weight=0.3,
        strength_weight=0.3,
        seeds=list(seeds),  # all 30
        condition="memory=0.3_strength=0.3",
        run_type="factorial",
    )
    run2 = RunConfig(
        run_id=f"{exp_id}-R2",
        run_label="R2",
        memory_weight=0.7,
        strength_weight=0.3,
        seeds=list(seeds),
        condition="memory=0.7_strength=0.3",
        run_type="factorial",
    )
    run3 = RunConfig(
        run_id=f"{exp_id}-R3",
        run_label="R3",
        memory_weight=0.3,
        strength_weight=0.7,
        seeds=list(seeds),
        condition="memory=0.3_strength=0.7",
        run_type="factorial",
    )
    run4 = RunConfig(
        run_id=f"{exp_id}-R4",
        run_label="R4",
        memory_weight=0.7,
        strength_weight=0.7,
        seeds=list(seeds),
        condition="memory=0.7_strength=0.7",
        run_type="factorial",
    )
    cp1 = RunConfig(
        run_id=f"{exp_id}-CP1",
        run_label="CP1",
        memory_weight=0.5,
        strength_weight=0.5,
        seeds=seeds[0:10],
        condition="memory=0.5_strength=0.5",
        run_type="center",
    )
    cp2 = RunConfig(
        run_id=f"{exp_id}-CP2",
        run_label="CP2",
        memory_weight=0.5,
        strength_weight=0.5,
        seeds=seeds[10:20],
        condition="memory=0.5_strength=0.5",
        run_type="center",
    )
    cp3 = RunConfig(
        run_id=f"{exp_id}-CP3",
        run_label="CP3",
        memory_weight=0.5,
        strength_weight=0.5,
        seeds=seeds[20:30],
        condition="memory=0.5_strength=0.5",
        run_type="center",
    )

    # Randomized run order: R3, CP2, R1, R4, CP1, R2, CP3
    randomized_runs = [run3, cp2, run1, run4, cp1, run2, cp3]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=randomized_runs,
        seed_set=seeds,
        seed_formula="seed_i = 3501 + i * 29, i=0..29",
        scenario="defend_the_center.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe007_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-007: Layer Ablation Study.

    Single factor: action_strategy, 5 levels.
    Seeds: seed_i = 4501 + i * 31, i=0..29
    Randomized run order: R4, R1, R5, R2, R3
    """
    seeds = _generate_seed_set(n=30, base=4501, step=31)
    exp_id = "DOE-007"

    run1 = RunConfig(
        run_id=f"{exp_id}-R1",
        run_label="R1",
        memory_weight=0.0,
        strength_weight=0.0,
        seeds=list(seeds),
        condition="action_strategy=random",
        run_type="factorial",
        action_type="random",
    )
    run2 = RunConfig(
        run_id=f"{exp_id}-R2",
        run_label="R2",
        memory_weight=0.0,
        strength_weight=0.0,
        seeds=list(seeds),
        condition="action_strategy=L0_only",
        run_type="factorial",
        action_type="rule_only",
    )
    run3 = RunConfig(
        run_id=f"{exp_id}-R3",
        run_label="R3",
        memory_weight=0.5,
        strength_weight=0.5,
        seeds=list(seeds),
        condition="action_strategy=L0_memory",
        run_type="factorial",
        action_type="l0_memory",
    )
    run4 = RunConfig(
        run_id=f"{exp_id}-R4",
        run_label="R4",
        memory_weight=0.5,
        strength_weight=0.5,
        seeds=list(seeds),
        condition="action_strategy=L0_strength",
        run_type="factorial",
        action_type="l0_strength",
    )
    run5 = RunConfig(
        run_id=f"{exp_id}-R5",
        run_label="R5",
        memory_weight=0.5,
        strength_weight=0.5,
        seeds=list(seeds),
        condition="action_strategy=full_agent",
        run_type="factorial",
        action_type="full_agent",
    )

    # Randomized execution order: R4, R1, R5, R2, R3
    randomized_runs = [run4, run1, run5, run2, run3]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=randomized_runs,
        seed_set=seeds,
        seed_formula="seed_i = 4501 + i * 31, i=0..29",
        scenario="defend_the_center.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


# ---------------------------------------------------------------------------
# Experiment executor
# ---------------------------------------------------------------------------


def execute_experiment(config: ExperimentConfig) -> None:
    """Execute a full DOE experiment with real VizDoom episodes.

    Args:
        config: Complete experiment configuration with runs in execution order.

    Raises:
        RuntimeError: If VizDoom fails to initialize.
    """
    # Defer heavy imports so --help works without dependencies
    from glue.action_functions import (
        FullAgentAction,
        L0MemoryAction,
        L0StrengthAction,
        random_action,
        rule_only_action,
    )
    from glue.duckdb_writer import DuckDBWriter
    from glue.episode_runner import EpisodeRunner
    from glue.vizdoom_bridge import VizDoomBridge

    total_episodes = sum(len(r.seeds) for r in config.runs)
    logger.info("=" * 70)
    logger.info(
        "DOE Experiment: %s (%d runs, %d total episodes)",
        config.experiment_id,
        len(config.runs),
        total_episodes,
    )
    logger.info("=" * 70)

    # Initialize VizDoom
    try:
        bridge = VizDoomBridge(scenario=config.scenario)
    except Exception as exc:
        logger.error(
            "Failed to initialize VizDoom: %s. "
            "Ensure VizDoom is installed and Xvfb is running.",
            exc,
        )
        raise RuntimeError(f"VizDoom init failed: {exc}") from exc

    runner = EpisodeRunner(bridge)
    db = DuckDBWriter(db_path=config.db_path)

    # Register seed set
    db.write_seed_set(
        experiment_id=config.experiment_id,
        seed_set=config.seed_set,
        formula=config.seed_formula,
    )
    logger.info(
        "Seed set registered: n=%d, formula=%s",
        len(config.seed_set),
        config.seed_formula,
    )

    experiment_start = time.monotonic()
    completed_episodes = 0
    skipped_episodes = 0

    try:
        for run_idx, run in enumerate(config.runs, start=1):
            logger.info("-" * 50)
            logger.info(
                "[%d/%d] Run %s  memory=%.1f  strength=%.1f  "
                "episodes=%d  type=%s",
                run_idx,
                len(config.runs),
                run.run_label,
                run.memory_weight,
                run.strength_weight,
                len(run.seeds),
                run.run_type,
            )

            # Check for resumption
            existing = db.get_episode_count(
                config.experiment_id, run.condition
            )

            # For center points sharing the same condition, we need to
            # count episodes relative to this specific run's seed subset.
            # Center points all share condition "memory=0.8_strength=0.8"
            # so we track per-run completion via run_id in a broader check.
            # Since the PK is (experiment_id, condition, episode_number),
            # center point episodes are numbered sequentially across CP1/CP2/CP3.
            # We handle this by checking if the run's episodes are complete
            # based on the seed count for center points.

            if run.run_type == "center":
                # For center points: check if all seeds for this run are done
                # by querying specific seed values
                run_done = _count_run_episodes(db, config.experiment_id, run)
                if run_done >= len(run.seeds):
                    skipped_episodes += len(run.seeds)
                    logger.info(
                        "  Skipping %s (already complete: %d episodes)",
                        run.run_label,
                        run_done,
                    )
                    continue
            else:
                if existing >= len(run.seeds):
                    skipped_episodes += len(run.seeds)
                    logger.info(
                        "  Skipping %s (already complete: %d episodes)",
                        run.run_label,
                        existing,
                    )
                    continue

            # Create action function based on run's action_type
            if run.action_type == "random":
                action_fn = random_action
            elif run.action_type == "rule_only":
                action_fn = rule_only_action
            elif run.action_type == "l0_memory":
                action_fn = L0MemoryAction()
            elif run.action_type == "l0_strength":
                action_fn = L0StrengthAction()
            else:  # "full_agent" (default)
                action_fn = FullAgentAction(
                    memory_weight=run.memory_weight,
                    strength_weight=run.strength_weight,
                )

            run_start = time.monotonic()

            for i, seed in enumerate(run.seeds):
                episode_number = i + 1

                # For center points, offset episode_number to avoid PK clash.
                # CP1 uses episodes 1-10, CP2 uses 11-20, CP3 uses 21-30.
                if run.run_type == "center":
                    if run.run_label == "CP2":
                        episode_number = i + 11
                    elif run.run_label == "CP3":
                        episode_number = i + 21

                # Skip already-completed episodes (resumption)
                if _episode_exists(
                    db,
                    config.experiment_id,
                    run.condition,
                    episode_number,
                ):
                    skipped_episodes += 1
                    continue

                # Reset action function state between episodes (if supported).
                # Plain functions (random_action, rule_only_action) have no
                # reset(); class-based actions do.
                if hasattr(action_fn, "reset"):
                    action_fn.reset(seed=seed)

                result = runner.run_episode(
                    seed=seed,
                    condition=run.condition,
                    episode_number=episode_number,
                    action_fn=action_fn,
                )

                # Convert EpisodeResult to DuckDB format
                metrics = {
                    "survival_time": result.metrics.survival_time,
                    "kills": result.metrics.kills,
                    "damage_dealt": result.metrics.damage_dealt,
                    "damage_taken": result.metrics.damage_taken,
                    "ammo_efficiency": result.metrics.ammo_efficiency,
                    "exploration_coverage": result.metrics.exploration_coverage,
                    "total_ticks": result.metrics.total_ticks,
                    "shots_fired": result.metrics.shots_fired,
                    "hits": result.metrics.hits,
                    "cells_visited": result.metrics.cells_visited,
                }

                # Count decision level occurrences
                level_counts: dict[str, int] = {}
                for level in result.decision_levels:
                    key = str(level)
                    level_counts[key] = level_counts.get(key, 0) + 1

                db.write_episode(
                    experiment_id=config.experiment_id,
                    run_id=run.run_id,
                    condition=run.condition,
                    seed=seed,
                    episode_number=episode_number,
                    metrics=metrics,
                    decision_latency_p99=result.decision_latency_p99,
                    rule_match_rate=result.rule_match_rate,
                    decision_level_counts=level_counts,
                )

                completed_episodes += 1

                # Progress logging: every 5 episodes or first/last
                if episode_number == 1 or i == len(run.seeds) - 1 or (i + 1) % 5 == 0:
                    logger.info(
                        "  [%s] ep %d/%d  seed=%d  kills=%d  "
                        "survival=%.1fs  kill_rate=%.2f/min",
                        run.run_label,
                        i + 1,
                        len(run.seeds),
                        seed,
                        result.metrics.kills,
                        result.metrics.survival_time,
                        result.metrics.kill_rate,
                    )

            run_elapsed = time.monotonic() - run_start
            logger.info(
                "  Run %s complete (%.1fs)",
                run.run_label,
                run_elapsed,
            )
    finally:
        bridge.close()

    # Verify data integrity
    logger.info("-" * 50)
    logger.info("Verifying data integrity...")
    integrity = db.verify_integrity(config.experiment_id)
    if integrity["valid"]:
        logger.info("Data integrity OK")
    else:
        logger.warning("Data integrity issues: %s", integrity["issues"])

    for cond, count in sorted(integrity["counts"].items()):
        logger.info("  %s: %d episodes", cond, count)

    db.close()

    total_elapsed = time.monotonic() - experiment_start
    logger.info("=" * 70)
    logger.info(
        "%s COMPLETE: %d new + %d skipped episodes in %.1fs",
        config.experiment_id,
        completed_episodes,
        skipped_episodes,
        total_elapsed,
    )
    logger.info("  DB: %s", config.db_path)
    logger.info("=" * 70)


# ---------------------------------------------------------------------------
# Helper queries for resumption
# ---------------------------------------------------------------------------


def _episode_exists(
    db: "DuckDBWriter",
    experiment_id: str,
    condition: str,
    episode_number: int,
) -> bool:
    """Check if a specific episode already exists in the database."""
    result = db._con.execute(
        "SELECT COUNT(*) FROM experiments "
        "WHERE experiment_id = ? AND condition = ? AND episode_number = ?",
        [experiment_id, condition, episode_number],
    ).fetchone()
    return bool(result and result[0] > 0)


def _count_run_episodes(
    db: "DuckDBWriter",
    experiment_id: str,
    run: RunConfig,
) -> int:
    """Count how many episodes from a specific run exist.

    For center points that share a condition, checks by seed values.
    """
    placeholders = ", ".join(["?"] * len(run.seeds))
    result = db._con.execute(
        f"SELECT COUNT(*) FROM experiments "
        f"WHERE experiment_id = ? AND condition = ? "
        f"AND seed IN ({placeholders})",
        [experiment_id, run.condition, *run.seeds],
    ).fetchone()
    return result[0] if result else 0


# ---------------------------------------------------------------------------
# Experiment registry
# ---------------------------------------------------------------------------

EXPERIMENT_BUILDERS: dict[str, object] = {
    "DOE-005": build_doe005_config,
    "DOE-006": build_doe006_config,
    "DOE-007": build_doe007_config,
}


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    """CLI entry point for DOE experiment execution."""
    parser = argparse.ArgumentParser(
        description="Execute DOE experiments with real VizDoom gameplay",
    )
    parser.add_argument(
        "--experiment",
        required=True,
        choices=list(EXPERIMENT_BUILDERS.keys()),
        help="Experiment ID to execute (e.g., DOE-005)",
    )
    parser.add_argument(
        "--db-path",
        type=Path,
        default=None,
        help=f"DuckDB database path (default: {DEFAULT_DB_PATH})",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    builder = EXPERIMENT_BUILDERS[args.experiment]
    config = builder(db_path=args.db_path)

    execute_experiment(config)


if __name__ == "__main__":
    main()
