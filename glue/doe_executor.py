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
    action_type: str = "full_agent"  # "random", "rule_only", "l0_memory", "l0_strength", "full_agent", "random_5", "strafe_burst_3", "smart_5", "genome"
    scenario: str = "defend_the_line.cfg"  # Per-run scenario override (used by DOE-011)
    num_actions: int = 3  # Number of available actions (3 or 5)
    genome_params: dict | None = None  # For genome-based action functions (DOE-021+)
    doom_skill: int = 3  # Difficulty level (1=Easy, 2=Normal, 3=Hard, 4=Very Hard, 5=Nightmare)


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


def build_doe008_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-008: Layer Ablation on defend_the_line.

    Single factor: action_strategy, 5 levels (same as DOE-007).
    Seeds: seed_i = 6001 + i * 37, i=0..29
    Randomized run order: R3, R5, R1, R4, R2
    Scenario: defend_the_line.cfg
    """
    seeds = _generate_seed_set(n=30, base=6001, step=37)
    exp_id = "DOE-008"

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

    # Randomized execution order: R3, R5, R1, R4, R2
    randomized_runs = [run3, run5, run1, run4, run2]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=randomized_runs,
        seed_set=seeds,
        seed_formula="seed_i = 6001 + i * 37, i=0..29",
        scenario="defend_the_line.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe009_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-009: Memory x Strength 3x3 Factorial on defend_the_line.

    Factors:
        Memory:   [0.1, 0.5, 0.9]
        Strength: [0.1, 0.5, 0.9]

    Seed formula: seed_i = 8001 + i * 41, i=0..29

    Randomized run order: R7, R2, R9, R4, R1, R6, R8, R3, R5
    """
    seeds = _generate_seed_set(n=30, base=8001, step=41)
    exp_id = "DOE-009"

    # 3x3 factorial: memory_weight [0.1, 0.5, 0.9] x strength_weight [0.1, 0.5, 0.9]
    # All 9 runs use FullAgentAction with varying parameters
    factor_combinations = [
        # (run_label, memory_weight, strength_weight)
        ("R1", 0.1, 0.1),
        ("R2", 0.1, 0.5),
        ("R3", 0.1, 0.9),
        ("R4", 0.5, 0.1),
        ("R5", 0.5, 0.5),
        ("R6", 0.5, 0.9),
        ("R7", 0.9, 0.1),
        ("R8", 0.9, 0.5),
        ("R9", 0.9, 0.9),
    ]

    runs = []
    for run_label, mem_w, str_w in factor_combinations:
        runs.append(RunConfig(
            run_id=f"{exp_id}-{run_label}",
            run_label=run_label,
            memory_weight=mem_w,
            strength_weight=str_w,
            seeds=list(seeds),
            condition=f"m{mem_w}_s{str_w}",
            run_type="factorial",
            action_type="full_agent",
        ))

    # Randomized run order: R7, R2, R9, R4, R1, R6, R8, R3, R5
    order = [6, 1, 8, 3, 0, 5, 7, 2, 4]  # indices into runs list
    randomized_runs = [runs[i] for i in order]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=randomized_runs,
        seed_set=seeds,
        seed_formula="seed_i = 8001 + i * 41, i=0..29",
        scenario="defend_the_line.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe010_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-010: New Strategy Architectures on defend_the_line.

    Single factor: action_strategy, 5 levels.
    Tests structured lateral movement patterns vs random/L0.
    Seeds: seed_i = 10001 + i * 43, i=0..29
    Randomized run order: R4, R2, R5, R1, R3
    Scenario: defend_the_line.cfg
    """
    seeds = _generate_seed_set(n=30, base=10001, step=43)
    exp_id = "DOE-010"

    run1 = RunConfig(
        run_id=f"{exp_id}-R1",
        run_label="R1",
        memory_weight=0.0,
        strength_weight=0.0,
        seeds=list(seeds),
        condition="strategy=random",
        run_type="factorial",
        action_type="random",
    )
    run2 = RunConfig(
        run_id=f"{exp_id}-R2",
        run_label="R2",
        memory_weight=0.0,
        strength_weight=0.0,
        seeds=list(seeds),
        condition="strategy=L0_only",
        run_type="factorial",
        action_type="rule_only",
    )
    run3 = RunConfig(
        run_id=f"{exp_id}-R3",
        run_label="R3",
        memory_weight=0.0,
        strength_weight=0.0,
        seeds=list(seeds),
        condition="strategy=sweep_lr",
        run_type="factorial",
        action_type="sweep_lr",
    )
    run4 = RunConfig(
        run_id=f"{exp_id}-R4",
        run_label="R4",
        memory_weight=0.0,
        strength_weight=0.0,
        seeds=list(seeds),
        condition="strategy=burst_3",
        run_type="factorial",
        action_type="burst_3",
    )
    run5 = RunConfig(
        run_id=f"{exp_id}-R5",
        run_label="R5",
        memory_weight=0.0,
        strength_weight=0.0,
        seeds=list(seeds),
        condition="strategy=burst_5",
        run_type="factorial",
        action_type="burst_5",
    )

    # Randomized execution order: R4, R2, R5, R1, R3
    randomized_runs = [run4, run2, run5, run1, run3]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=randomized_runs,
        seed_set=seeds,
        seed_formula="seed_i = 10001 + i * 43, i=0..29",
        scenario="defend_the_line.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe011_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-011: Expanded Action Space (5-Action) Strategy Differentiation.

    H-015: Turn+Strafe enables strategy differentiation.
    5 conditions: random_3, random_5, turn_burst_3, strafe_burst_3, smart_5.
    Two cfgs: defend_the_line.cfg (3-action) and defend_the_line_5action.cfg (5-action).

    Seeds: seed_i = 12001 + i * 47, i=0..29
    Randomized run order: R3, R5, R1, R4, R2
    """
    seeds = [12001 + i * 47 for i in range(30)]
    exp_id = "DOE-011"

    runs = [
        RunConfig(
            run_id=f"{exp_id}-R1",
            run_label="R1",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="random_3",
            run_type="factorial",
            action_type="random",
            scenario="defend_the_line.cfg",
            num_actions=3,
        ),
        RunConfig(
            run_id=f"{exp_id}-R2",
            run_label="R2",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="random_5",
            run_type="factorial",
            action_type="random_5",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R3",
            run_label="R3",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="turn_burst_3",
            run_type="factorial",
            action_type="burst_3",
            scenario="defend_the_line.cfg",
            num_actions=3,
        ),
        RunConfig(
            run_id=f"{exp_id}-R4",
            run_label="R4",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="strafe_burst_3",
            run_type="factorial",
            action_type="strafe_burst_3",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R5",
            run_label="R5",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="smart_5",
            run_type="factorial",
            action_type="smart_5",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
    ]

    # Randomized order: R3, R5, R1, R4, R2
    order = [runs[2], runs[4], runs[0], runs[3], runs[1]]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=order,
        seed_set=seeds,
        seed_formula="seed_i = 12001 + i * 47, i=0..29",
        scenario="defend_the_line.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe012_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-012: Compound Actions (simultaneous button presses).

    H-016: Compound attack+turn outperforms sequential single actions.
    5 conditions: random_3, burst_3 (sequential), attack_only,
    compound_attack_turn, compound_burst_3.
    Seeds: seed_i = 13001 + i * 53, i=0..29
    """
    seeds = [13001 + i * 53 for i in range(30)]
    exp_id = "DOE-012"
    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="random_3", run_type="factorial", action_type="random"),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_3", run_type="factorial", action_type="burst_3"),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="attack_only", run_type="factorial", action_type="attack_only"),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="compound_attack_turn", run_type="factorial", action_type="compound_attack_turn"),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="compound_burst_3", run_type="factorial", action_type="compound_burst_3"),
    ]
    return ExperimentConfig(
        experiment_id=exp_id, runs=runs, scenario="defend_the_line.cfg",
        seed_set=seeds, seed_formula="seed_i = 13001 + i * 53, i=0..29",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe013_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-013: Attack Ratio Sweep.

    H-017: Optimal attack ratio exists between 50-100%.
    5 conditions: burst_1(50%), burst_3(75%), burst_5(83%),
    burst_7(87.5%), attack_only(100%).
    Seeds: seed_i = 14001 + i * 59, i=0..29
    """
    seeds = [14001 + i * 59 for i in range(30)]
    exp_id = "DOE-013"
    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_1_50pct", run_type="factorial", action_type="burst_1"),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_3_75pct", run_type="factorial", action_type="burst_3"),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_5_83pct", run_type="factorial", action_type="burst_5"),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_7_88pct", run_type="factorial", action_type="burst_7"),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="attack_only_100pct", run_type="factorial", action_type="attack_only"),
    ]
    return ExperimentConfig(
        experiment_id=exp_id, runs=runs, scenario="defend_the_line.cfg",
        seed_set=seeds, seed_formula="seed_i = 14001 + i * 59, i=0..29",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe014_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-014: L0 Emergency Health Threshold Tuning.

    H-018: Optimal health threshold for L0 emergency dodge.
    5 conditions: threshold=0 (no L0), 10, 20, 30, 50.
    Seeds: seed_i = 15001 + i * 61, i=0..29
    """
    seeds = [15001 + i * 61 for i in range(30)]
    exp_id = "DOE-014"
    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="threshold_0", run_type="factorial", action_type="burst3_threshold_0"),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="threshold_10", run_type="factorial", action_type="burst3_threshold_10"),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="threshold_20", run_type="factorial", action_type="burst3_threshold_20"),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="threshold_30", run_type="factorial", action_type="burst3_threshold_30"),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="threshold_50", run_type="factorial", action_type="burst3_threshold_50"),
    ]
    return ExperimentConfig(
        experiment_id=exp_id, runs=runs, scenario="defend_the_line.cfg",
        seed_set=seeds, seed_formula="seed_i = 15001 + i * 61, i=0..29",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe015_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-015: basic Scenario (actual strafing with MOVE_LEFT/MOVE_RIGHT).

    H-019: Findings generalize to scenarios with actual physical movement.
    3 conditions from defend_the_line replicated on basic: random, burst_3,
    attack_only. Plus 2 defend_the_line controls.
    Seeds: seed_i = 16001 + i * 67, i=0..29
    Note: basic.cfg has MOVE_LEFT, MOVE_RIGHT, ATTACK (same 3 buttons,
    but physical strafing not turning). episode_timeout=300, doom_skill=5.
    """
    seeds = [16001 + i * 67 for i in range(30)]
    exp_id = "DOE-015"
    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="basic_random", run_type="factorial", action_type="random",
                  scenario="basic.cfg", num_actions=3),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="basic_burst_3", run_type="factorial", action_type="burst_3",
                  scenario="basic.cfg", num_actions=3),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="basic_attack_only", run_type="factorial", action_type="attack_only",
                  scenario="basic.cfg", num_actions=3),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="dtl_random", run_type="factorial", action_type="random",
                  scenario="defend_the_line.cfg", num_actions=3),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="dtl_burst_3", run_type="factorial", action_type="burst_3",
                  scenario="defend_the_line.cfg", num_actions=3),
    ]
    return ExperimentConfig(
        experiment_id=exp_id, runs=runs, scenario="defend_the_line.cfg",
        seed_set=seeds, seed_formula="seed_i = 16001 + i * 67, i=0..29",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe016_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-016: deadly_corridor Scenario (7-action space).

    H-020: Strategy findings generalize to complex action spaces.
    5 conditions: random_7, attack_only_7, forward_attack_7,
    burst_3_turn_7, adaptive_7.
    7 buttons: MOVE_LEFT(0), MOVE_RIGHT(1), ATTACK(2), MOVE_FORWARD(3),
    MOVE_BACKWARD(4), TURN_LEFT(5), TURN_RIGHT(6).
    Seeds: seed_i = 17001 + i * 71, i=0..29
    """
    seeds = [17001 + i * 71 for i in range(30)]
    exp_id = "DOE-016"
    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="dc_random_7", run_type="factorial", action_type="random_7",
                  scenario="deadly_corridor.cfg", num_actions=7),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="dc_attack_only", run_type="factorial", action_type="attack_only",
                  scenario="deadly_corridor.cfg", num_actions=7),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="dc_forward_attack", run_type="factorial", action_type="forward_attack",
                  scenario="deadly_corridor.cfg", num_actions=7),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="dc_burst_3_turn", run_type="factorial", action_type="burst_3",
                  scenario="deadly_corridor.cfg", num_actions=7),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="dc_adaptive", run_type="factorial", action_type="adaptive_kill",
                  scenario="deadly_corridor.cfg", num_actions=7),
    ]
    return ExperimentConfig(
        experiment_id=exp_id, runs=runs, scenario="deadly_corridor.cfg",
        seed_set=seeds, seed_formula="seed_i = 17001 + i * 71, i=0..29",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe017_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-017: Doom Skill Level Effect (Independent Confirmation).

    H-021: Difficulty level modulates strategy effectiveness.
    Replicates DOE-013 attack ratio sweep with independent seeds
    for confirmation. 5 conditions: random, burst_1, burst_3,
    burst_5, attack_only.
    Seeds: seed_i = 18001 + i * 73, i=0..29
    """
    seeds = [18001 + i * 73 for i in range(30)]
    exp_id = "DOE-017"
    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="random", run_type="factorial", action_type="random"),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_1", run_type="factorial", action_type="burst_1"),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_3", run_type="factorial", action_type="burst_3"),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_5", run_type="factorial", action_type="burst_5"),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="attack_only", run_type="factorial", action_type="attack_only"),
    ]
    return ExperimentConfig(
        experiment_id=exp_id, runs=runs, scenario="defend_the_line.cfg",
        seed_set=seeds, seed_formula="seed_i = 18001 + i * 73, i=0..29",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe018_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-018: Adaptive State-Dependent Strategy.

    H-022: State-dependent behavior outperforms fixed patterns.
    5 conditions: random, burst_3, attack_only, adaptive_kill,
    aggressive_adaptive.
    Seeds: seed_i = 19001 + i * 79, i=0..29
    """
    seeds = [19001 + i * 79 for i in range(30)]
    exp_id = "DOE-018"
    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="random", run_type="factorial", action_type="random"),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_3", run_type="factorial", action_type="burst_3"),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="attack_only", run_type="factorial", action_type="attack_only"),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="adaptive_kill", run_type="factorial", action_type="adaptive_kill"),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="aggressive_adaptive", run_type="factorial", action_type="aggressive_adaptive"),
    ]
    return ExperimentConfig(
        experiment_id=exp_id, runs=runs, scenario="defend_the_line.cfg",
        seed_set=seeds, seed_formula="seed_i = 19001 + i * 79, i=0..29",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe019_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-019: Replication with New Seeds.

    H-023: Strategy rankings are robust across seed sets.
    5 conditions: random, burst_3, attack_only, l0_only, adaptive_kill.
    Seeds: seed_i = 20001 + i * 83, i=0..29
    """
    seeds = [20001 + i * 83 for i in range(30)]
    exp_id = "DOE-019"
    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="random", run_type="factorial", action_type="random"),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_3", run_type="factorial", action_type="burst_3"),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="attack_only", run_type="factorial", action_type="attack_only"),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="l0_only", run_type="factorial", action_type="rule_only"),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="adaptive_kill", run_type="factorial", action_type="adaptive_kill"),
    ]
    return ExperimentConfig(
        experiment_id=exp_id, runs=runs, scenario="defend_the_line.cfg",
        seed_set=seeds, seed_formula="seed_i = 20001 + i * 83, i=0..29",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe020_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-020: Best-of-Breed Confirmation.

    H-024: Confirming top strategies across all prior DOEs.
    5 conditions: the best performers from DOE-008 through DOE-019.
    Seeds: seed_i = 21001 + i * 89, i=0..29
    """
    seeds = [21001 + i * 89 for i in range(30)]
    exp_id = "DOE-020"
    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="burst_3", run_type="factorial", action_type="burst_3"),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="attack_only", run_type="factorial", action_type="attack_only"),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="random", run_type="factorial", action_type="random"),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="compound_attack_turn", run_type="factorial", action_type="compound_attack_turn"),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.0, strength_weight=0.0,
                  seeds=list(seeds), condition="adaptive_kill", run_type="factorial", action_type="adaptive_kill"),
    ]
    return ExperimentConfig(
        experiment_id=exp_id, runs=runs, scenario="defend_the_line.cfg",
        seed_set=seeds, seed_formula="seed_i = 21001 + i * 89, i=0..29",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe021_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-021: Generational Evolution — Gen 1.

    H-025: Generational evolution discovers strategies superior to DOE-020 best-of-breed.
    10 genomes × 30 episodes = 300 episodes.
    Seeds: seed_i = 23001 + i * 91, i=0..29
    Randomized run order: R07, R03, R10, R05, R01, R09, R06, R02, R08, R04
    """
    # Corrected seed formula: seed_29 = 23001 + 29*91 = 25640
    seeds = [23001 + i * 91 for i in range(30)]
    exp_id = "DOE-021"

    # Define all 10 genomes as RunConfigs
    genome_definitions = [
        # G01: burst_3 exact replica
        ("R01", "G01_burst_3_base", {
            "burst_length": 3, "turn_direction": "random", "turn_count": 1,
            "health_threshold_high": 0, "health_threshold_low": 0,
            "stagnation_window": 0, "attack_probability": 0.75, "adaptive_enabled": False
        }),
        # G02: burst_3 with alternating turns
        ("R02", "G02_burst_3_sweep", {
            "burst_length": 3, "turn_direction": "alternate", "turn_count": 1,
            "health_threshold_high": 0, "health_threshold_low": 0,
            "stagnation_window": 0, "attack_probability": 0.75, "adaptive_enabled": False
        }),
        # G03: adaptive_kill exact replica
        ("R03", "G03_adaptive_base", {
            "burst_length": 3, "turn_direction": "random", "turn_count": 1,
            "health_threshold_high": 50, "health_threshold_low": 25,
            "stagnation_window": 5, "attack_probability": 0.80, "adaptive_enabled": True
        }),
        # G04: adaptive_kill variant
        ("R04", "G04_adaptive_tuned", {
            "burst_length": 3, "turn_direction": "alternate", "turn_count": 1,
            "health_threshold_high": 60, "health_threshold_low": 20,
            "stagnation_window": 7, "attack_probability": 0.85, "adaptive_enabled": True
        }),
        # G05: crossover (burst_3 + adaptive switching)
        ("R05", "G05_crossover_A", {
            "burst_length": 3, "turn_direction": "random", "turn_count": 1,
            "health_threshold_high": 50, "health_threshold_low": 25,
            "stagnation_window": 5, "attack_probability": 0.75, "adaptive_enabled": True
        }),
        # G06: crossover (burst_3 + more scanning)
        ("R06", "G06_crossover_B", {
            "burst_length": 3, "turn_direction": "alternate", "turn_count": 2,
            "health_threshold_high": 60, "health_threshold_low": 20,
            "stagnation_window": 0, "attack_probability": 0.80, "adaptive_enabled": False
        }),
        # G07: burst_2 (faster scanning)
        ("R07", "G07_burst_2", {
            "burst_length": 2, "turn_direction": "random", "turn_count": 1,
            "health_threshold_high": 0, "health_threshold_low": 0,
            "stagnation_window": 0, "attack_probability": 0.70, "adaptive_enabled": False
        }),
        # G08: burst_5 (longer bursts)
        ("R08", "G08_burst_5", {
            "burst_length": 5, "turn_direction": "random", "turn_count": 1,
            "health_threshold_high": 0, "health_threshold_low": 0,
            "stagnation_window": 0, "attack_probability": 0.80, "adaptive_enabled": False
        }),
        # G09: aggressive (maximum burst)
        ("R09", "G09_aggressive", {
            "burst_length": 7, "turn_direction": "random", "turn_count": 1,
            "health_threshold_high": 0, "health_threshold_low": 0,
            "stagnation_window": 0, "attack_probability": 0.95, "adaptive_enabled": False
        }),
        # G10: random baseline
        ("R10", "G10_random_baseline", {
            "burst_length": 3, "turn_direction": "random", "turn_count": 1,
            "health_threshold_high": 0, "health_threshold_low": 0,
            "stagnation_window": 0, "attack_probability": 0.50, "adaptive_enabled": False
        }),
    ]

    runs = []
    for run_label, condition, genome_params in genome_definitions:
        runs.append(RunConfig(
            run_id=f"{exp_id}-{run_label}",
            run_label=run_label,
            memory_weight=0.0,  # Not used for genome action
            strength_weight=0.0,  # Not used for genome action
            seeds=list(seeds),
            condition=condition,
            run_type="factorial",
            action_type="genome",
            genome_params=genome_params,
        ))

    # Randomized run order: R07, R03, R10, R05, R01, R09, R06, R02, R08, R04
    # Map run labels to indices in the runs list
    run_order_map = {r.run_label: i for i, r in enumerate(runs)}
    order = [run_order_map[label] for label in ["R07", "R03", "R10", "R05", "R01", "R09", "R06", "R02", "R08", "R04"]]
    randomized_runs = [runs[i] for i in order]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=randomized_runs,
        seed_set=seeds,
        seed_formula="seed_i = 23001 + i * 91, i=0..29",
        scenario="defend_the_line.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe022_config(db_path=None):
    """DOE-022: L2 RAG Pipeline Activation.

    H-025: L2 kNN strategy retrieval provides performance improvement.
    4 conditions x 30 episodes = 120 episodes.
    Seeds: seed_i = 24001 + i * 97, i=0..29
    Execution order: R3 (L2_good), R1 (L0_only), R4 (L2_random), R2 (L0_L1)
    """
    seeds = [24001 + i * 97 for i in range(30)]
    exp_id = "DOE-022"

    runs = [
        # Execution order: R3, R1, R4, R2
        RunConfig(
            run_id=f"{exp_id}-R3", run_label="R3",
            memory_weight=0.0, strength_weight=0.0,
            seeds=list(seeds),
            condition="L0_L1_L2_good",
            run_type="factorial",
            action_type="l2_rag_good",
        ),
        RunConfig(
            run_id=f"{exp_id}-R1", run_label="R1",
            memory_weight=0.0, strength_weight=0.0,
            seeds=list(seeds),
            condition="L0_only",
            run_type="factorial",
            action_type="rule_only",
        ),
        RunConfig(
            run_id=f"{exp_id}-R4", run_label="R4",
            memory_weight=0.0, strength_weight=0.0,
            seeds=list(seeds),
            condition="L0_L1_L2_random",
            run_type="factorial",
            action_type="l2_rag_random",
        ),
        RunConfig(
            run_id=f"{exp_id}-R2", run_label="R2",
            memory_weight=0.0, strength_weight=0.0,
            seeds=list(seeds),
            condition="L0_L1",
            run_type="factorial",
            action_type="burst_3",
        ),
    ]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=runs,
        seed_set=seeds,
        seed_formula="seed_i = 24001 + i * 97, i=0..29",
        scenario="defend_the_line.cfg",
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
        Adaptive5Action,
        AdaptiveKillAction,
        AggressiveAdaptiveAction,
        AttackOnlyAction,
        AttackRatioAction,
        AttackRatioActionRaw,
        Burst1Action,
        Burst3Action,
        Burst3ThresholdAction,
        Burst5Action,
        Burst7Action,
        BurstCycleAction,
        CompoundAttackTurnAction,
        CompoundBurst3Action,
        DodgeBurst3Action,
        ForwardAttackAction,
        FullAgentAction,
        GenomeAction,
        L0MemoryAction,
        L0StrengthAction,
        L2MetaStrategyAction,
        L2MetaStrategy5Action,
        L2RagAction,
        PureAttackAction,
        Random5Action,
        Random7Action,
        Random9Action,
        RandomRotation5Action,
        RandomSelectAction,
        Smart5Action,
        StrafeBurst3Action,
        SurvivalBurstAction,
        SweepLRAction,
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

    # Initialize VizDoom with default scenario
    current_scenario = config.scenario
    current_num_actions = 3  # default
    current_doom_skill = 3  # default
    try:
        bridge = VizDoomBridge(scenario=current_scenario, num_actions=current_num_actions, doom_skill=current_doom_skill)
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

            # Switch scenario if this run requires a different one
            run_scenario = getattr(run, "scenario", config.scenario)
            run_num_actions = getattr(run, "num_actions", 3)
            run_doom_skill = getattr(run, "doom_skill", 3)
            if run_scenario != current_scenario or run_num_actions != current_num_actions or run_doom_skill != current_doom_skill:
                logger.info(
                    "  Switching scenario: %s -> %s (num_actions: %d -> %d, doom_skill: %d -> %d)",
                    current_scenario,
                    run_scenario,
                    current_num_actions,
                    run_num_actions,
                    current_doom_skill,
                    run_doom_skill,
                )
                bridge.close()
                bridge = VizDoomBridge(scenario=run_scenario, num_actions=run_num_actions, doom_skill=run_doom_skill)
                runner = EpisodeRunner(bridge)
                current_scenario = run_scenario
                current_num_actions = run_num_actions
                current_doom_skill = run_doom_skill

            # Create action function based on run's action_type
            if run.action_type == "random":
                action_fn = random_action
            elif run.action_type == "rule_only":
                action_fn = rule_only_action
            elif run.action_type == "l0_memory":
                action_fn = L0MemoryAction()
            elif run.action_type == "l0_strength":
                action_fn = L0StrengthAction()
            elif run.action_type == "sweep_lr":
                action_fn = SweepLRAction()
            elif run.action_type == "burst_3":
                action_fn = Burst3Action()
            elif run.action_type == "burst_5":
                action_fn = Burst5Action()
            elif run.action_type == "random_5":
                action_fn = Random5Action()
            elif run.action_type == "strafe_burst_3":
                action_fn = StrafeBurst3Action()
            elif run.action_type == "smart_5":
                action_fn = Smart5Action()
            elif run.action_type == "adaptive_5":
                action_fn = Adaptive5Action()
            elif run.action_type == "dodge_burst_3":
                action_fn = DodgeBurst3Action()
            elif run.action_type == "survival_burst":
                action_fn = SurvivalBurstAction()
            elif run.action_type == "compound_attack_turn":
                action_fn = CompoundAttackTurnAction()
            elif run.action_type == "compound_burst_3":
                action_fn = CompoundBurst3Action()
            elif run.action_type == "burst_1":
                action_fn = Burst1Action()
            elif run.action_type == "burst_7":
                action_fn = Burst7Action()
            elif run.action_type == "attack_only":
                action_fn = AttackOnlyAction()
            elif run.action_type.startswith("burst3_threshold_"):
                threshold = int(run.action_type.split("_")[-1])
                action_fn = Burst3ThresholdAction(health_threshold=threshold)
            elif run.action_type == "random_7":
                action_fn = Random7Action()
            elif run.action_type == "random_9":
                action_fn = Random9Action()
            elif run.action_type == "forward_attack":
                action_fn = ForwardAttackAction()
            elif run.action_type == "adaptive_kill":
                action_fn = AdaptiveKillAction()
            elif run.action_type == "aggressive_adaptive":
                action_fn = AggressiveAdaptiveAction()
            elif run.action_type == "genome":
                action_fn = GenomeAction(**run.genome_params)
            elif run.action_type == "l2_rag_good":
                action_fn = L2RagAction(
                    opensearch_url="http://opensearch:9200",
                    index_name="strategies_high",
                    k=5,
                )
            elif run.action_type == "l2_rag_random":
                action_fn = L2RagAction(
                    opensearch_url="http://opensearch:9200",
                    index_name="strategies_low",
                    k=5,
                )
            elif run.action_type == "l2_meta_select":
                action_fn = L2MetaStrategyAction(
                    opensearch_url="http://opensearch:9200",
                    index_name="strategies_meta",
                    k=5,
                )
            elif run.action_type == "random_select":
                action_fn = RandomSelectAction()
            elif run.action_type == "l2_meta_5action":
                action_fn = L2MetaStrategy5Action(
                    opensearch_url="http://opensearch:9200",
                    index_name="strategies_meta_5action",
                    k=5,
                )
            elif run.action_type == "random_rotation_5":
                action_fn = RandomRotation5Action()
            elif run.action_type.startswith("ar_"):
                ratio = int(run.action_type.split("_")[1]) / 100.0
                action_fn = AttackRatioAction(attack_ratio=ratio)
            elif run.action_type.startswith("cycle_"):
                burst_len = int(run.action_type.split("_")[1])
                action_fn = BurstCycleAction(burst_length=burst_len)
            elif run.action_type == "rand50_raw":
                action_fn = AttackRatioActionRaw(attack_ratio=0.5)
            elif run.action_type == "attack_ovr":
                action_fn = PureAttackAction(health_override=True)
            elif run.action_type == "attack_raw":
                action_fn = PureAttackAction(health_override=False)
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


def build_doe023_config(db_path=None):
    """Build config for DOE-023: Difficulty-Level Strategy Robustness.

    Revised design using doom_skill as scenario factor (original WAD-based
    variants not feasible without binary editing).

    Factors:
        doom_skill: [1 (Easy), 3 (Normal), 5 (Nightmare)]
        Strategy:   [burst_3, random, adaptive_kill, L0_only]

    Design: 3x4 full factorial, 30 episodes/cell, 360 total
    Seeds: seed_i = 25001 + i * 101, i=0..29
    """
    seeds = [25001 + i * 101 for i in range(30)]
    exp_id = "DOE-023"

    strategies = [
        ("burst_3", "burst_3"),
        ("random", "random"),
        ("adaptive_kill", "adaptive_kill"),
        ("L0_only", "rule_only"),
    ]
    skill_levels = [
        (1, "easy"),
        (3, "normal"),
        (5, "nightmare"),
    ]

    runs = []
    run_num = 1
    for skill, skill_label in skill_levels:
        for strat_name, action_type in strategies:
            condition = f"skill_{skill_label}_{strat_name}"
            runs.append(
                RunConfig(
                    run_id=f"{exp_id}-R{run_num:02d}",
                    run_label=f"R{run_num:02d}",
                    memory_weight=0.0,
                    strength_weight=0.0,
                    seeds=list(seeds),
                    condition=condition,
                    run_type="factorial",
                    action_type=action_type,
                    scenario="defend_the_line.cfg",
                    doom_skill=skill,
                )
            )
            run_num += 1

    # Randomize run order for experimental validity
    import random as _rng
    rng = _rng.Random(20230223)
    rng.shuffle(runs)

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=runs,
        seed_set=seeds,
        seed_formula="seed_i = 25001 + i * 101, i=0..29",
        scenario="defend_the_line.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe024_config(db_path=None):
    """Build config for DOE-024: L2 Meta-Strategy Selection via RAG.

    Tests whether L2 RAG as a meta-strategy selector (choosing which L1
    strategy to delegate to based on game-state context) outperforms
    fixed single-strategy performance across difficulty levels.

    Factors:
        decision_mode: [fixed_burst3, fixed_adaptive_kill, L2_meta_select, random_select]
        doom_skill: [1 (Easy), 3 (Normal), 5 (Nightmare)]

    Design: 4x3 full factorial, 30 episodes/cell, 360 total
    Seeds: seed_i = 40001 + i * 103, i=0..29
    """
    seeds = [40001 + i * 103 for i in range(30)]
    exp_id = "DOE-024"

    decision_modes = [
        ("fixed_burst3", "burst_3"),
        ("fixed_adaptive_kill", "adaptive_kill"),
        ("L2_meta_select", "l2_meta_select"),
        ("random_select", "random_select"),
    ]
    skill_levels = [
        (1, "easy"),
        (3, "normal"),
        (5, "nightmare"),
    ]

    runs = []
    run_num = 1
    for skill, skill_label in skill_levels:
        for mode_name, action_type in decision_modes:
            condition = f"skill_{skill_label}_{mode_name}"
            runs.append(
                RunConfig(
                    run_id=f"{exp_id}-R{run_num:02d}",
                    run_label=f"R{run_num:02d}",
                    memory_weight=0.0,
                    strength_weight=0.0,
                    seeds=list(seeds),
                    condition=condition,
                    run_type="factorial",
                    action_type=action_type,
                    scenario="defend_the_line.cfg",
                    doom_skill=skill,
                )
            )
            run_num += 1

    # Randomize run order for experimental validity
    import random as _rng
    rng = _rng.Random(20240224)
    rng.shuffle(runs)

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=runs,
        seed_set=seeds,
        seed_formula="seed_i = 40001 + i * 103, i=0..29",
        scenario="defend_the_line.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe025_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-025: 5-Action Strategy Optimization.

    H-028: 5-action strategies create separable performance tiers.
    6 conditions: random_5, strafe_burst_3, smart_5, adaptive_5, dodge_burst_3, survival_burst.
    All use defend_the_line_5action.cfg with 5 actions.

    Seeds: seed_i = 45001 + i * 107, i=0..29
    Randomized run order (seed 20250225): R3, R6, R1, R4, R2, R5
    """
    seeds = [45001 + i * 107 for i in range(30)]
    exp_id = "DOE-025"

    runs = [
        RunConfig(
            run_id=f"{exp_id}-R1",
            run_label="R1",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="random_5",
            run_type="factorial",
            action_type="random_5",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R2",
            run_label="R2",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="strafe_burst_3",
            run_type="factorial",
            action_type="strafe_burst_3",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R3",
            run_label="R3",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="smart_5",
            run_type="factorial",
            action_type="smart_5",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R4",
            run_label="R4",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="adaptive_5",
            run_type="factorial",
            action_type="adaptive_5",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R5",
            run_label="R5",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="dodge_burst_3",
            run_type="factorial",
            action_type="dodge_burst_3",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R6",
            run_label="R6",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="survival_burst",
            run_type="factorial",
            action_type="survival_burst",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
    ]

    # Randomized order (seed 20250225): R3, R6, R1, R4, R2, R5
    order = [runs[2], runs[5], runs[0], runs[3], runs[1], runs[4]]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=order,
        seed_set=seeds,
        seed_formula="seed_i = 45001 + i * 107, i=0..29",
        scenario="defend_the_line_5action.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe026_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-026: L2 RAG Strategy Selection in 5-Action Space.

    H-029: RAG strategy selection has value in 5-action space.
    5 conditions: survival_burst, random_5, dodge_burst_3, l2_meta_5action, random_rotation_5.
    All use defend_the_line_5action.cfg with 5 actions.

    Seeds: seed_i = 46001 + i * 113, i=0..29
    Randomized run order: R3, R1, R5, R4, R2
    """
    seeds = [46001 + i * 113 for i in range(30)]
    exp_id = "DOE-026"

    runs = [
        RunConfig(
            run_id=f"{exp_id}-R1",
            run_label="R1",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="survival_burst",
            run_type="factorial",
            action_type="survival_burst",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R2",
            run_label="R2",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="random_5",
            run_type="factorial",
            action_type="random_5",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R3",
            run_label="R3",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="dodge_burst_3",
            run_type="factorial",
            action_type="dodge_burst_3",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R4",
            run_label="R4",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="l2_meta_5action",
            run_type="factorial",
            action_type="l2_meta_5action",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R5",
            run_label="R5",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="random_rotation_5",
            run_type="factorial",
            action_type="random_rotation_5",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
    ]

    # Randomized order: R3, R1, R5, R4, R2
    order = [runs[2], runs[0], runs[4], runs[3], runs[1]]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=order,
        seed_set=seeds,
        seed_formula="seed_i = 46001 + i * 113, i=0..29",
        scenario="defend_the_line_5action.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe027_config(db_path: Path | None = None) -> ExperimentConfig:
    """Build configuration for DOE-027: Attack Ratio Gradient Sweep.

    Factor: attack_ratio (0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8)
    Design: One-way ANOVA (7 levels × 30 episodes = 210 total)
    Seed formula: seed_i = 47001 + i × 127, i=0..29
    Randomized run order: R5, R2, R7, R1, R4, R6, R3
    """
    seeds = [47001 + i * 127 for i in range(30)]
    exp_id = "DOE-027"

    runs = [
        RunConfig(run_id=f"{exp_id}-R1", run_label="R1", memory_weight=0.5, strength_weight=0.5,
                  seeds=list(seeds), condition="ar_20", run_type="factorial",
                  action_type="ar_20", scenario="defend_the_line_5action.cfg", num_actions=5),
        RunConfig(run_id=f"{exp_id}-R2", run_label="R2", memory_weight=0.5, strength_weight=0.5,
                  seeds=list(seeds), condition="ar_30", run_type="factorial",
                  action_type="ar_30", scenario="defend_the_line_5action.cfg", num_actions=5),
        RunConfig(run_id=f"{exp_id}-R3", run_label="R3", memory_weight=0.5, strength_weight=0.5,
                  seeds=list(seeds), condition="ar_40", run_type="factorial",
                  action_type="ar_40", scenario="defend_the_line_5action.cfg", num_actions=5),
        RunConfig(run_id=f"{exp_id}-R4", run_label="R4", memory_weight=0.5, strength_weight=0.5,
                  seeds=list(seeds), condition="ar_50", run_type="factorial",
                  action_type="ar_50", scenario="defend_the_line_5action.cfg", num_actions=5),
        RunConfig(run_id=f"{exp_id}-R5", run_label="R5", memory_weight=0.5, strength_weight=0.5,
                  seeds=list(seeds), condition="ar_60", run_type="factorial",
                  action_type="ar_60", scenario="defend_the_line_5action.cfg", num_actions=5),
        RunConfig(run_id=f"{exp_id}-R6", run_label="R6", memory_weight=0.5, strength_weight=0.5,
                  seeds=list(seeds), condition="ar_70", run_type="factorial",
                  action_type="ar_70", scenario="defend_the_line_5action.cfg", num_actions=5),
        RunConfig(run_id=f"{exp_id}-R7", run_label="R7", memory_weight=0.5, strength_weight=0.5,
                  seeds=list(seeds), condition="ar_80", run_type="factorial",
                  action_type="ar_80", scenario="defend_the_line_5action.cfg", num_actions=5),
    ]

    # Randomized order: R5, R2, R7, R1, R4, R6, R3
    order = [runs[4], runs[1], runs[6], runs[0], runs[3], runs[5], runs[2]]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=order,
        seed_set=seeds,
        seed_formula="seed_i = 47001 + i × 127, i=0..29",
        scenario="defend_the_line_5action.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe028_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-028: Temporal Attack Pattern Study (Burst Cycle)

    5 conditions all at 50% attack ratio, varying temporal grouping:
    random_50, cycle_2, cycle_3, cycle_5, cycle_10
    """
    seeds = [48001 + i * 131 for i in range(30)]
    exp_id = "DOE-028"

    runs = [
        # Randomized order: R3, R5, R1, R4, R2
        RunConfig(
            run_id=f"{exp_id}-R3",
            run_label="R3",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="cycle_3",
            run_type="factorial",
            action_type="cycle_3",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R5",
            run_label="R5",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="cycle_10",
            run_type="factorial",
            action_type="cycle_10",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R1",
            run_label="R1",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="random_50",
            run_type="factorial",
            action_type="ar_50",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R4",
            run_label="R4",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="cycle_5",
            run_type="factorial",
            action_type="cycle_5",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R2",
            run_label="R2",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="cycle_2",
            run_type="factorial",
            action_type="cycle_2",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
    ]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=runs,
        seed_set=seeds,
        seed_formula="seed_i = 48001 + i * 131, i=0..29",
        scenario="defend_the_line_5action.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe029_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-029: Emergency Health Override Effect (2x2 Factorial)

    Tests whether health<20 emergency dodge override matters.
    Factor A: action_pattern (random_50 vs pure_attack)
    Factor B: health_override (enabled vs disabled)
    """
    seeds = [49001 + i * 137 for i in range(30)]
    exp_id = "DOE-029"

    runs = [
        # Randomized order: R3, R1, R4, R2
        RunConfig(
            run_id=f"{exp_id}-R3",
            run_label="R3",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="attack_ovr",
            run_type="factorial",
            action_type="attack_ovr",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R1",
            run_label="R1",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="rand50_ovr",
            run_type="factorial",
            action_type="ar_50",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R4",
            run_label="R4",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="attack_raw",
            run_type="factorial",
            action_type="attack_raw",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R2",
            run_label="R2",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="rand50_raw",
            run_type="factorial",
            action_type="rand50_raw",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
        ),
    ]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=runs,
        seed_set=seeds,
        seed_formula="seed_i = 49001 + i * 137, i=0..29",
        scenario="defend_the_line_5action.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe030_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-030: Movement × Doom Skill Interaction (2×5 Full Factorial)

    Tests how movement availability interacts with enemy difficulty.
    Factor A: movement (present=ar_50 vs absent=attack_raw)
    Factor B: doom_skill (1, 2, 3, 4, 5)

    Design: 2×5 full factorial, 30 episodes/cell, 300 total
    Randomized run order: R07, R03, R10, R01, R05, R08, R02, R09, R04, R06
    """
    seeds = [53001 + i * 139 for i in range(30)]
    exp_id = "DOE-030"

    runs = [
        # Randomized order: R07, R03, R10, R01, R05, R08, R02, R09, R04, R06
        RunConfig(
            run_id=f"{exp_id}-R07",
            run_label="R07",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="stat_sk2",
            run_type="factorial",
            action_type="attack_raw",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=2,
        ),
        RunConfig(
            run_id=f"{exp_id}-R03",
            run_label="R03",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="move_sk3",
            run_type="factorial",
            action_type="ar_50",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=3,
        ),
        RunConfig(
            run_id=f"{exp_id}-R10",
            run_label="R10",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="stat_sk5",
            run_type="factorial",
            action_type="attack_raw",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R01",
            run_label="R01",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="move_sk1",
            run_type="factorial",
            action_type="ar_50",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=1,
        ),
        RunConfig(
            run_id=f"{exp_id}-R05",
            run_label="R05",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="move_sk5",
            run_type="factorial",
            action_type="ar_50",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R08",
            run_label="R08",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="stat_sk3",
            run_type="factorial",
            action_type="attack_raw",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=3,
        ),
        RunConfig(
            run_id=f"{exp_id}-R02",
            run_label="R02",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="move_sk2",
            run_type="factorial",
            action_type="ar_50",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=2,
        ),
        RunConfig(
            run_id=f"{exp_id}-R09",
            run_label="R09",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="stat_sk4",
            run_type="factorial",
            action_type="attack_raw",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=4,
        ),
        RunConfig(
            run_id=f"{exp_id}-R04",
            run_label="R04",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="move_sk4",
            run_type="factorial",
            action_type="ar_50",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=4,
        ),
        RunConfig(
            run_id=f"{exp_id}-R06",
            run_label="R06",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="stat_sk1",
            run_type="factorial",
            action_type="attack_raw",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=1,
        ),
    ]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=runs,
        seed_set=seeds,
        seed_formula="seed_i = 53001 + i * 139, i=0..29",
        scenario="defend_the_line_5action.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe031_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-031: Action Space Granularity Threshold (One-Way, 4 Levels)

    Tests how action space dimensionality affects random agent performance.
    Factor: action_space (3, 5, 7, 9 actions)

    Design: One-way ANOVA, 30 episodes/level, 120 total
    Randomized run order: R3, R1, R4, R2
    """
    seeds = [57101 + i * 149 for i in range(30)]
    exp_id = "DOE-031"

    runs = [
        # Randomized order: R3, R1, R4, R2
        RunConfig(
            run_id=f"{exp_id}-R3",
            run_label="R3",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="action_7",
            run_type="one_way",
            action_type="random_7",
            scenario="defend_the_line_7action.cfg",
            num_actions=7,
            doom_skill=3,
        ),
        RunConfig(
            run_id=f"{exp_id}-R1",
            run_label="R1",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="action_3",
            run_type="one_way",
            action_type="random",
            scenario="defend_the_line.cfg",
            num_actions=3,
            doom_skill=3,
        ),
        RunConfig(
            run_id=f"{exp_id}-R4",
            run_label="R4",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="action_9",
            run_type="one_way",
            action_type="random_9",
            scenario="defend_the_line_9action.cfg",
            num_actions=9,
            doom_skill=3,
        ),
        RunConfig(
            run_id=f"{exp_id}-R2",
            run_label="R2",
            memory_weight=0.0,
            strength_weight=0.0,
            seeds=list(seeds),
            condition="action_5",
            run_type="one_way",
            action_type="random_5",
            scenario="defend_the_line_5action.cfg",
            num_actions=5,
            doom_skill=3,
        ),
    ]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=runs,
        seed_set=seeds,
        seed_formula="seed_i = 57101 + i * 149, i=0..29",
        scenario="defend_the_line.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def build_doe032_config(db_path: Path | None = None) -> ExperimentConfig:
    """DOE-032: Cross-Episode Sequential Learning (2×2 Factorial).

    Tests whether sequential episode execution with persistent action function
    state produces learning effects vs independent episodes.

    Factors:
        l1_cache: on/off (whether action function state persists)
        sequence_mode: sequential_10 / independent

    4 conditions × 10 sequences × 10 episodes = 400 total episodes.
    Uses ar_50 (AttackRatioAction with 50% attack) for all conditions.

    Seed formula: seed_{k,i} = 61501 + k*151 + i*13, k=0..9, i=0..9
    Randomized run order: R3, R1, R4, R2
    """
    exp_id = "DOE-032"

    # Generate seed set: 10 sequences × 10 episodes per sequence
    all_seeds = []
    for k in range(10):
        for i in range(10):
            all_seeds.append(61501 + k * 151 + i * 13)

    # 4 conditions, each gets all 100 seeds (same seeds for paired comparison)
    # R1: cache_seq, R2: cache_ind, R3: nocache_seq, R4: nocache_ind
    runs = [
        # Randomized order: R3, R1, R4, R2
        RunConfig(
            run_id=f"{exp_id}-R3", run_label="R3",
            memory_weight=0.0, strength_weight=0.0,
            seeds=list(all_seeds), condition="nocache_seq",
            run_type="factorial", action_type="ar_50",
            scenario="defend_the_line_5action.cfg", num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R1", run_label="R1",
            memory_weight=0.0, strength_weight=0.0,
            seeds=list(all_seeds), condition="cache_seq",
            run_type="factorial", action_type="ar_50",
            scenario="defend_the_line_5action.cfg", num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R4", run_label="R4",
            memory_weight=0.0, strength_weight=0.0,
            seeds=list(all_seeds), condition="nocache_ind",
            run_type="factorial", action_type="ar_50",
            scenario="defend_the_line_5action.cfg", num_actions=5,
        ),
        RunConfig(
            run_id=f"{exp_id}-R2", run_label="R2",
            memory_weight=0.0, strength_weight=0.0,
            seeds=list(all_seeds), condition="cache_ind",
            run_type="factorial", action_type="ar_50",
            scenario="defend_the_line_5action.cfg", num_actions=5,
        ),
    ]

    return ExperimentConfig(
        experiment_id=exp_id,
        runs=runs,
        seed_set=all_seeds,
        seed_formula="seed_{k,i} = 61501 + k*151 + i*13, k=0..9, i=0..9",
        scenario="defend_the_line_5action.cfg",
        db_path=db_path or DEFAULT_DB_PATH,
    )


def execute_doe032(config: ExperimentConfig) -> None:
    """Special executor for DOE-032: Sequential Learning experiment.

    Handles 4 conditions with different reset behavior:
    - cache_seq: Action function NOT reset between episodes within sequence
    - cache_ind: Action function reset before every episode
    - nocache_seq: Action function NOT reset between episodes (same as cache_seq)
    - nocache_ind: Action function reset before every episode (same as cache_ind)

    Since there's no actual L1 DuckDB cache in the action functions,
    cache_seq ≡ nocache_seq and cache_ind ≡ nocache_ind.
    But we keep all 4 conditions for the designed 2×2 factorial analysis.

    Episodes are grouped into sequences of 10 for analysis.
    """
    from glue.action_functions import AttackRatioAction
    from glue.duckdb_writer import DuckDBWriter
    from glue.episode_runner import EpisodeRunner
    from glue.vizdoom_bridge import VizDoomBridge

    total_episodes = sum(len(r.seeds) for r in config.runs)
    logger.info("=" * 70)
    logger.info(
        "DOE-032 Sequential Learning: %s (%d runs, %d total episodes)",
        config.experiment_id, len(config.runs), total_episodes,
    )
    logger.info("=" * 70)

    bridge = VizDoomBridge(
        scenario="defend_the_line_5action.cfg", num_actions=5, doom_skill=3
    )
    runner = EpisodeRunner(bridge)
    db = DuckDBWriter(db_path=config.db_path)

    db.write_seed_set(
        experiment_id=config.experiment_id,
        seed_set=config.seed_set,
        formula=config.seed_formula,
    )

    experiment_start = time.monotonic()
    completed = 0
    skipped = 0

    try:
        for run_idx, run in enumerate(config.runs, start=1):
            logger.info("-" * 50)
            logger.info(
                "[%d/%d] Condition: %s", run_idx, len(config.runs), run.condition
            )

            # Determine reset behavior from condition name
            is_sequential = run.condition.endswith("_seq")

            # Create action function for this condition
            action_fn = AttackRatioAction(attack_ratio=0.5)

            # Group seeds into sequences of 10
            for seq_id in range(10):
                seq_seeds = run.seeds[seq_id * 10 : (seq_id + 1) * 10]

                # For sequential mode: reset action function only at sequence start
                # For independent mode: reset before every episode
                if is_sequential:
                    # Reset at start of each sequence with first seed
                    action_fn.reset(seed=seq_seeds[0])

                for ep_in_seq, seed in enumerate(seq_seeds):
                    # Episode number: global within this condition (1-100)
                    episode_number = seq_id * 10 + ep_in_seq + 1

                    # Skip already-completed episodes
                    if _episode_exists(
                        db, config.experiment_id, run.condition, episode_number
                    ):
                        skipped += 1
                        continue

                    # For independent mode: reset before EVERY episode
                    if not is_sequential:
                        action_fn.reset(seed=seed)

                    result = runner.run_episode(
                        seed=seed,
                        condition=run.condition,
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

                    completed += 1

                    # Progress logging
                    if ep_in_seq == 0 or ep_in_seq == 9 or (ep_in_seq + 1) % 5 == 0:
                        logger.info(
                            "  [%s] seq=%d ep=%d/%d seed=%d kills=%d "
                            "survival=%.1fs",
                            run.condition, seq_id, ep_in_seq + 1, 10,
                            seed, result.metrics.kills,
                            result.metrics.survival_time,
                        )

                logger.info(
                    "  Sequence %d/%d complete", seq_id + 1, 10
                )

            logger.info("  Condition %s complete", run.condition)

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
        config.experiment_id, completed, skipped, total_elapsed,
    )
    logger.info("=" * 70)


# ---------------------------------------------------------------------------
# Experiment registry
# ---------------------------------------------------------------------------

EXPERIMENT_BUILDERS: dict[str, object] = {
    "DOE-005": build_doe005_config,
    "DOE-006": build_doe006_config,
    "DOE-007": build_doe007_config,
    "DOE-008": build_doe008_config,
    "DOE-009": build_doe009_config,
    "DOE-010": build_doe010_config,
    "DOE-011": build_doe011_config,
    "DOE-012": build_doe012_config,
    "DOE-013": build_doe013_config,
    "DOE-014": build_doe014_config,
    "DOE-015": build_doe015_config,
    "DOE-016": build_doe016_config,
    "DOE-017": build_doe017_config,
    "DOE-018": build_doe018_config,
    "DOE-019": build_doe019_config,
    "DOE-020": build_doe020_config,
    "DOE-021": build_doe021_config,
    "DOE-022": build_doe022_config,
    "DOE-023": build_doe023_config,
    "DOE-024": build_doe024_config,
    "DOE-025": build_doe025_config,
    "DOE-026": build_doe026_config,
    "DOE-027": build_doe027_config,
    "DOE-028": build_doe028_config,
    "DOE-029": build_doe029_config,
    "DOE-030": build_doe030_config,
    "DOE-031": build_doe031_config,
    "DOE-032": build_doe032_config,
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

    # DOE-032 uses special sequential executor
    if args.experiment == "DOE-032":
        execute_doe032(config)
    else:
        execute_experiment(config)


if __name__ == "__main__":
    main()
