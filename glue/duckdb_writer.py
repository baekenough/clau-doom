"""DuckDB writer: persists experiment data for statistical analysis."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional

import duckdb

logger = logging.getLogger(__name__)

SCHEMA_SQL_PATH = Path(__file__).parent / "schema" / "init_duckdb.sql"
DEFAULT_DB_PATH = Path("volumes/data/clau-doom.duckdb")


class DuckDBWriter:
    """Writes experiment data to DuckDB."""

    def __init__(self, db_path: Optional[Path] = None):
        self._db_path = db_path or DEFAULT_DB_PATH
        self._db_path.parent.mkdir(parents=True, exist_ok=True)
        self._con = duckdb.connect(str(self._db_path))
        self._ensure_schema()

    def _ensure_schema(self) -> None:
        if SCHEMA_SQL_PATH.exists():
            # DuckDB Python API uses execute(), not executescript()
            self._con.execute(SCHEMA_SQL_PATH.read_text())

    def write_episode(
        self,
        experiment_id: str,
        run_id: str,
        condition: str,
        seed: int,
        episode_number: int,
        metrics: dict,
        decision_latency_p99: float = 0.0,
        rule_match_rate: float = 0.0,
        decision_level_counts: Optional[dict] = None,
    ) -> None:
        """Insert a single episode result into the experiments table."""
        survival_time = metrics.get("survival_time", 0.0)
        kills = metrics.get("kills", 0)
        kill_rate = (
            (kills / (survival_time / 60.0)) if survival_time > 0 else 0.0
        )

        self._con.execute(
            """
            INSERT INTO experiments (
                experiment_id, run_id, condition, baseline_type,
                seed, episode_number,
                kill_rate, kills, survival_time,
                damage_dealt, damage_taken,
                ammo_efficiency, exploration_coverage,
                decision_latency_p99, rule_match_rate,
                decision_level_counts,
                total_ticks, shots_fired, hits, cells_visited
            ) VALUES (
                ?, ?, ?, ?,
                ?, ?,
                ?, ?, ?,
                ?, ?,
                ?, ?,
                ?, ?,
                ?,
                ?, ?, ?, ?
            )
        """,
            [
                experiment_id,
                run_id,
                condition,
                condition,
                seed,
                episode_number,
                kill_rate,
                kills,
                survival_time,
                metrics.get("damage_dealt", 0.0),
                metrics.get("damage_taken", 0.0),
                metrics.get("ammo_efficiency", 0.0),
                metrics.get("exploration_coverage", 0.0),
                decision_latency_p99,
                rule_match_rate,
                json.dumps(decision_level_counts or {}),
                metrics.get("total_ticks", 0),
                metrics.get("shots_fired", 0),
                metrics.get("hits", 0),
                metrics.get("cells_visited", 0),
            ],
        )

    def write_seed_set(
        self,
        experiment_id: str,
        seed_set: list[int],
        formula: str = "",
    ) -> None:
        """Register a seed set for an experiment."""
        # Delete existing entry if present (upsert pattern)
        self._con.execute(
            "DELETE FROM seed_sets WHERE experiment_id = ?",
            [experiment_id],
        )
        self._con.execute(
            """
            INSERT INTO seed_sets (experiment_id, seed_set, seed_count, formula)
            VALUES (?, ?, ?, ?)
        """,
            [experiment_id, json.dumps(seed_set), len(seed_set), formula],
        )

    def get_episode_count(self, experiment_id: str, condition: str) -> int:
        """Count completed episodes for a condition."""
        result = self._con.execute(
            "SELECT COUNT(*) FROM experiments "
            "WHERE experiment_id = ? AND condition = ?",
            [experiment_id, condition],
        ).fetchone()
        return result[0] if result else 0

    def verify_integrity(self, experiment_id: str) -> dict:
        """Verify data integrity for an experiment."""
        issues: list[str] = []

        # Check episode counts per condition
        counts = self._con.execute(
            """
            SELECT condition, COUNT(*) as n
            FROM experiments WHERE experiment_id = ?
            GROUP BY condition
        """,
            [experiment_id],
        ).fetchall()

        # Check for NULL metrics
        nulls = self._con.execute(
            """
            SELECT COUNT(*) FROM experiments
            WHERE experiment_id = ?
              AND (kills IS NULL OR survival_time IS NULL)
        """,
            [experiment_id],
        ).fetchone()
        if nulls and nulls[0] > 0:
            issues.append(f"{nulls[0]} episodes with NULL metrics")

        # Check seed integrity
        seed_check = self._con.execute(
            """
            SELECT condition, COUNT(DISTINCT seed) as unique_seeds
            FROM experiments WHERE experiment_id = ?
            GROUP BY condition
        """,
            [experiment_id],
        ).fetchall()

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "counts": {row[0]: row[1] for row in counts},
            "unique_seeds": {row[0]: row[1] for row in seed_check},
        }

    def close(self) -> None:
        self._con.close()
