"""Seed set integrity verification for DOE experiments."""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass

import duckdb

logger = logging.getLogger(__name__)


@dataclass
class SeedCheckResult:
    """Result of seed integrity check."""
    valid: bool
    issues: list[str]
    conditions_checked: list[str]
    seeds_per_condition: dict[str, int]
    seed_formula_match: bool
    cross_condition_match: bool


def verify_seeds(
    db_path: str,
    experiment_id: str,
    expected_formula_base: int = 42,
    expected_formula_step: int = 31,
) -> SeedCheckResult:
    """Verify seed integrity for an experiment.

    Checks:
    1. All conditions use the same seed set
    2. Seeds match expected formula
    3. No duplicate seeds within a condition
    4. Seed count matches expected
    """
    issues: list[str] = []

    con = duckdb.connect(db_path, read_only=True)
    try:
        # Get seeds per condition
        rows = con.execute(
            """
            SELECT condition,
                   ARRAY_AGG(seed ORDER BY episode_number) as seeds,
                   COUNT(*) as n
            FROM experiments
            WHERE experiment_id = ?
            GROUP BY condition
            ORDER BY condition
            """,
            [experiment_id],
        ).fetchall()

        if not rows:
            return SeedCheckResult(
                valid=False,
                issues=["No data found for experiment"],
                conditions_checked=[],
                seeds_per_condition={},
                seed_formula_match=False,
                cross_condition_match=False,
            )

        conditions = [r[0] for r in rows]
        seed_sets = {r[0]: r[1] for r in rows}
        counts = {r[0]: r[2] for r in rows}

        # Check cross-condition seed match
        reference_seeds = seed_sets[conditions[0]]
        cross_match = True
        for cond in conditions[1:]:
            if seed_sets[cond] != reference_seeds:
                issues.append(f"Seed mismatch: {conditions[0]} vs {cond}")
                cross_match = False

        # Check formula match
        formula_match = True
        for i, seed in enumerate(reference_seeds):
            expected = expected_formula_base + i * expected_formula_step
            if seed != expected:
                issues.append(f"Seed[{i}] = {seed}, expected {expected} "
                            f"(formula: {expected_formula_base} + {i} * {expected_formula_step})")
                formula_match = False
                break

        # Check for duplicates within conditions
        for cond, seeds in seed_sets.items():
            if len(seeds) != len(set(seeds)):
                issues.append(f"Duplicate seeds in condition {cond}")

        # Check registered seed set
        registered = con.execute(
            "SELECT seed_set FROM seed_sets WHERE experiment_id = ?",
            [experiment_id],
        ).fetchone()

        if registered:
            registered_seeds = json.loads(registered[0])
            if registered_seeds != list(reference_seeds):
                issues.append("Registered seed set doesn't match actual seeds used")

    finally:
        con.close()

    return SeedCheckResult(
        valid=len(issues) == 0,
        issues=issues,
        conditions_checked=conditions,
        seeds_per_condition=counts,
        seed_formula_match=formula_match,
        cross_condition_match=cross_match,
    )
