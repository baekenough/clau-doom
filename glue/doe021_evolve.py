#!/usr/bin/env python3
"""DOE-021 Generational Evolution: Gen 2 through Gen 5.

Implements TOPSIS-based selection, crossover, mutation, and VizDoom execution
for the evolutionary optimization of GenomeAction parameters.

Usage (inside doom-player Docker container):
    python3 -m glue.doe021_evolve
    python3 -m glue.doe021_evolve --dry-run
    python3 -m glue.doe021_evolve --max-gen 3
    python3 -m glue.doe021_evolve --db-path data/clau-doom.duckdb
"""

from __future__ import annotations

import argparse
import copy
import json
import logging
import math
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

DEFAULT_DB_PATH = Path("data/clau-doom.duckdb")

# ---------------------------------------------------------------------------
# Gene specification
# ---------------------------------------------------------------------------

GENE_SPEC = {
    "burst_length":          {"type": "int",   "min": 1,   "max": 7},
    "turn_direction":        {"type": "enum",  "values": ["random", "alternate", "sweep_left", "sweep_right"]},
    "turn_count":            {"type": "int",   "min": 1,   "max": 3},
    "health_threshold_high": {"type": "int",   "min": 0,   "max": 100},
    "health_threshold_low":  {"type": "int",   "min": 0,   "max": 100},
    "stagnation_window":     {"type": "int",   "min": 0,   "max": 10},
    "attack_probability":    {"type": "float", "min": 0.5, "max": 1.0},
    "adaptive_enabled":      {"type": "bool"},
}

# ---------------------------------------------------------------------------
# Gen 1 genome definitions (hardcoded)
# ---------------------------------------------------------------------------

GEN1_GENOMES: dict[str, dict] = {
    "G01_burst_3_base": {
        "burst_length": 3, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 0, "health_threshold_low": 0,
        "stagnation_window": 0, "attack_probability": 0.75, "adaptive_enabled": False,
    },
    "G02_burst_3_sweep": {
        "burst_length": 3, "turn_direction": "alternate", "turn_count": 1,
        "health_threshold_high": 0, "health_threshold_low": 0,
        "stagnation_window": 0, "attack_probability": 0.75, "adaptive_enabled": False,
    },
    "G03_adaptive_base": {
        "burst_length": 3, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 50, "health_threshold_low": 25,
        "stagnation_window": 5, "attack_probability": 0.80, "adaptive_enabled": True,
    },
    "G04_adaptive_tuned": {
        "burst_length": 3, "turn_direction": "alternate", "turn_count": 1,
        "health_threshold_high": 60, "health_threshold_low": 20,
        "stagnation_window": 7, "attack_probability": 0.85, "adaptive_enabled": True,
    },
    "G05_crossover_A": {
        "burst_length": 3, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 50, "health_threshold_low": 25,
        "stagnation_window": 5, "attack_probability": 0.75, "adaptive_enabled": True,
    },
    "G06_crossover_B": {
        "burst_length": 3, "turn_direction": "alternate", "turn_count": 2,
        "health_threshold_high": 60, "health_threshold_low": 20,
        "stagnation_window": 0, "attack_probability": 0.80, "adaptive_enabled": False,
    },
    "G07_burst_2": {
        "burst_length": 2, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 0, "health_threshold_low": 0,
        "stagnation_window": 0, "attack_probability": 0.70, "adaptive_enabled": False,
    },
    "G08_burst_5": {
        "burst_length": 5, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 0, "health_threshold_low": 0,
        "stagnation_window": 0, "attack_probability": 0.80, "adaptive_enabled": False,
    },
    "G09_aggressive": {
        "burst_length": 7, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 0, "health_threshold_low": 0,
        "stagnation_window": 0, "attack_probability": 0.95, "adaptive_enabled": False,
    },
    "G10_random_baseline": {
        "burst_length": 3, "turn_direction": "random", "turn_count": 1,
        "health_threshold_high": 0, "health_threshold_low": 0,
        "stagnation_window": 0, "attack_probability": 0.50, "adaptive_enabled": False,
    },
}

# ---------------------------------------------------------------------------
# Seed sets per generation
# ---------------------------------------------------------------------------

SEED_FORMULAS = {
    2: {"base": 26001, "step": 97,  "n": 30},
    3: {"base": 29001, "step": 101, "n": 30},
    4: {"base": 32001, "step": 103, "n": 30},
    5: {"base": 35001, "step": 107, "n": 30},
}


def make_seed_set(gen: int) -> list[int]:
    """Generate deterministic seed set for a generation."""
    f = SEED_FORMULAS[gen]
    return [f["base"] + i * f["step"] for i in range(f["n"])]


# ---------------------------------------------------------------------------
# TOPSIS fitness computation
# ---------------------------------------------------------------------------

@dataclass
class GenomeFitness:
    """Fitness result for a single genome."""
    name: str
    genome: dict
    mean_kills: float
    mean_kill_rate: float
    mean_survival_time: float
    c_i: float  # TOPSIS closeness coefficient


def compute_topsis(genome_stats: list[dict]) -> list[GenomeFitness]:
    """Compute TOPSIS ranking from genome performance statistics.

    Args:
        genome_stats: list of dicts with keys:
            name, genome, mean_kills, mean_kill_rate, mean_survival_time

    Returns:
        List of GenomeFitness sorted by C_i descending (best first).
    """
    n = len(genome_stats)
    if n == 0:
        return []

    # Criteria: mean_kills, mean_kill_rate, mean_survival_time (all maximize)
    criteria_keys = ["mean_kills", "mean_kill_rate", "mean_survival_time"]
    weights = [1.0 / 3, 1.0 / 3, 1.0 / 3]

    # Build decision matrix (n x 3)
    matrix = []
    for gs in genome_stats:
        matrix.append([gs[k] for k in criteria_keys])

    # Step 1: Normalize (vector normalization)
    norm_matrix = []
    for j in range(3):
        col_sum_sq = sum(matrix[i][j] ** 2 for i in range(n))
        col_norm = math.sqrt(col_sum_sq) if col_sum_sq > 0 else 1.0
        norm_matrix.append(col_norm)

    normalized = []
    for i in range(n):
        row = [matrix[i][j] / norm_matrix[j] for j in range(3)]
        normalized.append(row)

    # Step 2: Weight
    weighted = []
    for i in range(n):
        row = [normalized[i][j] * weights[j] for j in range(3)]
        weighted.append(row)

    # Step 3: Ideal best and worst (all maximize)
    ideal_best = [max(weighted[i][j] for i in range(n)) for j in range(3)]
    ideal_worst = [min(weighted[i][j] for i in range(n)) for j in range(3)]

    # Step 4: Distances
    results = []
    for i in range(n):
        d_best = math.sqrt(sum((weighted[i][j] - ideal_best[j]) ** 2 for j in range(3)))
        d_worst = math.sqrt(sum((weighted[i][j] - ideal_worst[j]) ** 2 for j in range(3)))
        c_i = d_worst / (d_best + d_worst) if (d_best + d_worst) > 0 else 0.0

        results.append(GenomeFitness(
            name=genome_stats[i]["name"],
            genome=genome_stats[i]["genome"],
            mean_kills=genome_stats[i]["mean_kills"],
            mean_kill_rate=genome_stats[i]["mean_kill_rate"],
            mean_survival_time=genome_stats[i]["mean_survival_time"],
            c_i=c_i,
        ))

    results.sort(key=lambda r: r.c_i, reverse=True)
    return results


# ---------------------------------------------------------------------------
# Genetic operators
# ---------------------------------------------------------------------------

import random as _random_module


def enforce_constraints(genome: dict) -> dict:
    """Enforce genome constraints after crossover/mutation."""
    # health_threshold_low < health_threshold_high (if both > 0)
    if genome["health_threshold_low"] > 0 and genome["health_threshold_high"] > 0:
        if genome["health_threshold_low"] >= genome["health_threshold_high"]:
            genome["health_threshold_low"] = max(0, genome["health_threshold_high"] - 1)

    # stagnation_window = 0 if adaptive_enabled = false
    if not genome["adaptive_enabled"]:
        genome["stagnation_window"] = 0

    return genome


def crossover_uniform(parent_a: dict, parent_b: dict, rng: _random_module.Random) -> dict:
    """Uniform crossover: each gene from A or B with p=0.5."""
    child = {}
    for gene_name in GENE_SPEC:
        if rng.random() < 0.5:
            child[gene_name] = copy.deepcopy(parent_a[gene_name])
        else:
            child[gene_name] = copy.deepcopy(parent_b[gene_name])
    return enforce_constraints(child)


def mutate(genome: dict, rng: _random_module.Random, mutation_prob: float = 0.2) -> dict:
    """Per-gene mutation with probability mutation_prob."""
    mutated = copy.deepcopy(genome)

    for gene_name, spec in GENE_SPEC.items():
        if rng.random() >= mutation_prob:
            continue

        if spec["type"] == "int":
            delta = rng.choice([-1, 1])
            mutated[gene_name] = max(spec["min"], min(spec["max"], mutated[gene_name] + delta))

        elif spec["type"] == "float":
            delta = rng.choice([-0.1, 0.1])
            mutated[gene_name] = max(spec["min"], min(spec["max"], round(mutated[gene_name] + delta, 2)))

        elif spec["type"] == "bool":
            mutated[gene_name] = not mutated[gene_name]

        elif spec["type"] == "enum":
            mutated[gene_name] = rng.choice(spec["values"])

    return enforce_constraints(mutated)


def generate_random_genome(rng: _random_module.Random) -> dict:
    """Generate a completely random genome."""
    genome = {}
    for gene_name, spec in GENE_SPEC.items():
        if spec["type"] == "int":
            genome[gene_name] = rng.randint(spec["min"], spec["max"])
        elif spec["type"] == "float":
            genome[gene_name] = round(rng.uniform(spec["min"], spec["max"]), 2)
        elif spec["type"] == "bool":
            genome[gene_name] = rng.choice([True, False])
        elif spec["type"] == "enum":
            genome[gene_name] = rng.choice(spec["values"])
    return enforce_constraints(genome)


def create_next_generation(
    parents: list[GenomeFitness],
    rng: _random_module.Random,
    gen_number: int,
) -> dict[str, dict]:
    """Create 10 genomes for the next generation.

    Slot 1:  Elite (best genome unchanged)
    Slot 2:  Crossover + mutation of parents #1 x #2
    Slot 3:  Crossover + mutation of parents #1 x #2
    Slot 4:  Crossover + mutation of parents #1 x #3
    Slot 5:  Crossover + mutation of parents #2 x #4
    Slot 6:  Crossover + mutation of parents #1 x #4
    Slot 7:  Crossover + mutation of parents #3 x #4
    Slot 8:  Mutation-only clone of parent #2
    Slot 9:  Mutation-only clone of parent #3
    Slot 10: Random genome (diversity)
    """
    p = [parents[i].genome for i in range(4)]

    genomes: dict[str, dict] = {}

    # Slot 1: Elite
    genomes[f"gen{gen_number}_G01_elite"] = copy.deepcopy(p[0])

    # Slots 2-3: Crossover parents #1 x #2
    genomes[f"gen{gen_number}_G02_x12a"] = mutate(crossover_uniform(p[0], p[1], rng), rng)
    genomes[f"gen{gen_number}_G03_x12b"] = mutate(crossover_uniform(p[0], p[1], rng), rng)

    # Slots 4-5: Crossover parents #1x#3, #2x#4
    genomes[f"gen{gen_number}_G04_x13"] = mutate(crossover_uniform(p[0], p[2], rng), rng)
    genomes[f"gen{gen_number}_G05_x24"] = mutate(crossover_uniform(p[1], p[3], rng), rng)

    # Slots 6-7: Crossover parents #1x#4, #3x#4
    genomes[f"gen{gen_number}_G06_x14"] = mutate(crossover_uniform(p[0], p[3], rng), rng)
    genomes[f"gen{gen_number}_G07_x34"] = mutate(crossover_uniform(p[2], p[3], rng), rng)

    # Slot 8: Mutation-only clone of parent #2
    genomes[f"gen{gen_number}_G08_mut2"] = mutate(copy.deepcopy(p[1]), rng)

    # Slot 9: Mutation-only clone of parent #3
    genomes[f"gen{gen_number}_G09_mut3"] = mutate(copy.deepcopy(p[2]), rng)

    # Slot 10: Random genome
    genomes[f"gen{gen_number}_G10_random"] = generate_random_genome(rng)

    return genomes


# ---------------------------------------------------------------------------
# DuckDB queries for fitness evaluation
# ---------------------------------------------------------------------------


def fetch_generation_stats(con, experiment_id: str) -> list[dict]:
    """Fetch per-genome mean statistics from DuckDB for TOPSIS evaluation.

    Args:
        con: DuckDB connection.
        experiment_id: e.g., "DOE-021" or "DOE-021_gen2".

    Returns:
        List of dicts with name, mean_kills, mean_kill_rate, mean_survival_time.
    """
    rows = con.execute(
        """
        SELECT
            condition,
            AVG(kills) AS mean_kills,
            AVG(kill_rate) AS mean_kill_rate,
            AVG(survival_time) AS mean_survival_time
        FROM experiments
        WHERE experiment_id = ?
        GROUP BY condition
        ORDER BY condition
        """,
        [experiment_id],
    ).fetchall()

    return [
        {
            "name": row[0],
            "mean_kills": row[1],
            "mean_kill_rate": row[2],
            "mean_survival_time": row[3],
        }
        for row in rows
    ]


def episode_exists(con, experiment_id: str, condition: str, episode_number: int) -> bool:
    """Check if a specific episode already exists."""
    result = con.execute(
        "SELECT 1 FROM experiments WHERE experiment_id=? AND condition=? AND episode_number=?",
        [experiment_id, condition, episode_number],
    ).fetchone()
    return result is not None


# ---------------------------------------------------------------------------
# Execution engine
# ---------------------------------------------------------------------------


def execute_generation(
    gen_number: int,
    genomes: dict[str, dict],
    seeds: list[int],
    db_path: Path,
    dry_run: bool = False,
) -> None:
    """Execute all episodes for a single generation.

    Args:
        gen_number: Generation number (2-5).
        genomes: dict mapping genome_name -> genome_params.
        seeds: Seed set for this generation (30 seeds).
        db_path: Path to DuckDB database.
        dry_run: If True, print genomes and exit without executing.
    """
    experiment_id = f"DOE-021_gen{gen_number}"

    if dry_run:
        logger.info("=== DRY RUN: Gen %d (%s) ===", gen_number, experiment_id)
        for name, params in genomes.items():
            logger.info("  %s: %s", name, json.dumps(params, default=str))
        return

    # Defer heavy imports
    from glue.action_functions import GenomeAction
    from glue.duckdb_writer import DuckDBWriter
    from glue.episode_runner import EpisodeRunner
    from glue.vizdoom_bridge import VizDoomBridge

    logger.info("=" * 70)
    logger.info("Gen %d: %s — %d genomes × %d episodes = %d total",
                gen_number, experiment_id, len(genomes), len(seeds),
                len(genomes) * len(seeds))
    logger.info("=" * 70)

    db = DuckDBWriter(db_path=db_path)

    # Register seed set
    formula = f"seed_i = {SEED_FORMULAS[gen_number]['base']} + i * {SEED_FORMULAS[gen_number]['step']}, i=0..29"
    db.write_seed_set(experiment_id, seeds, formula)

    bridge = VizDoomBridge(scenario="defend_the_line.cfg")
    runner = EpisodeRunner(bridge)

    # Randomize genome execution order
    genome_names = list(genomes.keys())
    exec_rng = _random_module.Random(gen_number * 1000)
    exec_rng.shuffle(genome_names)

    gen_start = time.monotonic()
    completed = 0
    skipped = 0

    try:
        for g_idx, genome_name in enumerate(genome_names, start=1):
            genome_params = genomes[genome_name]
            action_fn = GenomeAction(**genome_params)

            logger.info("-" * 50)
            logger.info("[%d/%d] Genome: %s", g_idx, len(genome_names), genome_name)
            logger.info("  Params: %s", json.dumps(genome_params, default=str))

            for i, seed in enumerate(seeds):
                episode_number = i + 1

                # Resumption check
                if episode_exists(db._con, experiment_id, genome_name, episode_number):
                    skipped += 1
                    continue

                action_fn.reset(seed=seed)

                result = runner.run_episode(
                    seed=seed,
                    condition=genome_name,
                    episode_number=episode_number,
                    action_fn=action_fn,
                )

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

                level_counts: dict[str, int] = {}
                for level in result.decision_levels:
                    key = str(level)
                    level_counts[key] = level_counts.get(key, 0) + 1

                db.write_episode(
                    experiment_id=experiment_id,
                    run_id=f"{experiment_id}-{genome_name}",
                    condition=genome_name,
                    seed=seed,
                    episode_number=episode_number,
                    metrics=metrics,
                    decision_latency_p99=result.decision_latency_p99,
                    rule_match_rate=result.rule_match_rate,
                    decision_level_counts=level_counts,
                )

                completed += 1

                if episode_number == 1 or i == len(seeds) - 1 or (i + 1) % 10 == 0:
                    logger.info(
                        "  [%s] ep %d/%d  seed=%d  kills=%d  survival=%.1fs",
                        genome_name, i + 1, len(seeds), seed,
                        result.metrics.kills, result.metrics.survival_time,
                    )

            logger.info("  Genome %s complete", genome_name)

    finally:
        bridge.close()

    elapsed = time.monotonic() - gen_start
    logger.info("=" * 70)
    logger.info("Gen %d COMPLETE: %d new + %d skipped in %.1fs",
                gen_number, completed, skipped, elapsed)
    logger.info("=" * 70)

    db.close()


# ---------------------------------------------------------------------------
# Main evolution loop
# ---------------------------------------------------------------------------


def run_evolution(
    max_gen: int = 5,
    db_path: Path = DEFAULT_DB_PATH,
    dry_run: bool = False,
) -> None:
    """Run the full generational evolution from Gen 2 to max_gen.

    Reads Gen 1 results from DuckDB, computes TOPSIS, breeds Gen 2,
    executes, evaluates, breeds Gen 3, etc.

    Convergence: stops if elite genome is identical for 2 consecutive generations.
    """
    import duckdb

    evo_rng = _random_module.Random(20260209)

    con = duckdb.connect(str(db_path))

    # Track elite genome across generations for convergence check
    prev_elite_genome: Optional[dict] = None

    # We need to know genomes for each generation to attach to TOPSIS
    # Gen 1 genomes are hardcoded; subsequent ones are created by evolution
    current_genomes = GEN1_GENOMES
    current_experiment_id = "DOE-021"

    for gen in range(2, max_gen + 1):
        logger.info("")
        logger.info("*" * 70)
        logger.info("EVOLUTION: Preparing Gen %d", gen)
        logger.info("*" * 70)

        # Fetch stats from the PREVIOUS generation
        stats = fetch_generation_stats(con, current_experiment_id)

        if len(stats) == 0:
            logger.error("No data found for %s. Cannot proceed.", current_experiment_id)
            break

        # Attach genome params to stats
        for s in stats:
            if s["name"] in current_genomes:
                s["genome"] = current_genomes[s["name"]]
            else:
                logger.warning("Genome %s not found in current_genomes, skipping", s["name"])

        stats = [s for s in stats if "genome" in s]

        if len(stats) < 4:
            logger.error("Need at least 4 genomes with data, got %d. Cannot proceed.", len(stats))
            break

        # Compute TOPSIS
        ranked = compute_topsis(stats)

        logger.info("TOPSIS Rankings for %s:", current_experiment_id)
        for i, r in enumerate(ranked):
            logger.info(
                "  #%d: %s  C_i=%.4f  (kills=%.1f, kill_rate=%.2f, survival=%.1f)",
                i + 1, r.name, r.c_i,
                r.mean_kills, r.mean_kill_rate, r.mean_survival_time,
            )

        # Select top 4 parents
        parents = ranked[:4]
        logger.info("Selected parents: %s",
                     ", ".join(p.name for p in parents))

        # Convergence check: is elite the same as previous gen?
        elite_genome = parents[0].genome
        if prev_elite_genome is not None and elite_genome == prev_elite_genome:
            logger.info("CONVERGENCE: Elite genome unchanged for 2 consecutive generations.")
            logger.info("Stopping evolution at Gen %d.", gen)
            break
        prev_elite_genome = copy.deepcopy(elite_genome)

        # Create next generation
        next_genomes = create_next_generation(parents, evo_rng, gen)

        logger.info("Gen %d genomes:", gen)
        for name, params in next_genomes.items():
            logger.info("  %s: %s", name, json.dumps(params, default=str))

        # Generate seeds
        seeds = make_seed_set(gen)

        # Execute
        con.close()  # Close before execution (DuckDBWriter opens its own connection)

        execute_generation(
            gen_number=gen,
            genomes=next_genomes,
            seeds=seeds,
            db_path=db_path,
            dry_run=dry_run,
        )

        # Reopen connection for next iteration
        con = duckdb.connect(str(db_path))

        # Update tracking for next iteration
        current_genomes = next_genomes
        current_experiment_id = f"DOE-021_gen{gen}"

    con.close()

    # Print final summary
    logger.info("")
    logger.info("=" * 70)
    logger.info("EVOLUTION COMPLETE")
    logger.info("=" * 70)

    # Reopen to print final rankings
    con = duckdb.connect(str(db_path))
    final_stats = fetch_generation_stats(con, current_experiment_id)
    if final_stats:
        for s in final_stats:
            if s["name"] in current_genomes:
                s["genome"] = current_genomes[s["name"]]
        final_stats = [s for s in final_stats if "genome" in s]
        if final_stats:
            final_ranked = compute_topsis(final_stats)
            logger.info("Final TOPSIS Rankings (%s):", current_experiment_id)
            for i, r in enumerate(final_ranked):
                logger.info(
                    "  #%d: %s  C_i=%.4f  (kills=%.1f, kill_rate=%.2f, survival=%.1f)",
                    i + 1, r.name, r.c_i,
                    r.mean_kills, r.mean_kill_rate, r.mean_survival_time,
                )
            logger.info("Best genome: %s", json.dumps(final_ranked[0].genome, default=str))
    con.close()


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="DOE-021 generational evolution (Gen 2 through Gen 5)",
    )
    parser.add_argument(
        "--max-gen", type=int, default=5,
        help="Maximum generation to evolve to (default: 5)",
    )
    parser.add_argument(
        "--db-path", type=Path, default=None,
        help=f"DuckDB database path (default: {DEFAULT_DB_PATH})",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print genomes without executing episodes",
    )
    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    run_evolution(
        max_gen=args.max_gen,
        db_path=args.db_path or DEFAULT_DB_PATH,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
