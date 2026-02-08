"""Initialize DuckDB with clau-doom schema.

Usage:
    python -m glue.schema.init_duckdb [--db-path path/to/db.duckdb]
"""
import argparse
import duckdb
from pathlib import Path

SCHEMA_PATH = Path(__file__).parent / "init_duckdb.sql"
DEFAULT_DB_PATH = Path("volumes/data/clau-doom.duckdb")


def init_database(db_path: Path) -> None:
    """Create tables from schema SQL file."""
    schema_sql = SCHEMA_PATH.read_text()
    db_path.parent.mkdir(parents=True, exist_ok=True)

    con = duckdb.connect(str(db_path))
    try:
        con.execute(schema_sql)
        # Verify tables created
        tables = con.execute("SHOW TABLES").fetchall()
        table_names = [t[0] for t in tables]
        expected = [
            "experiments",
            "encounters",
            "doe_runs",
            "strategy_docs",
            "agent_configs",
            "generations",
            "seed_sets",
        ]
        for t in expected:
            assert t in table_names, f"Missing table: {t}"
        print(f"Database initialized at {db_path}")
        print(f"Tables: {', '.join(table_names)}")
    finally:
        con.close()


def main():
    parser = argparse.ArgumentParser(
        description="Initialize clau-doom DuckDB schema"
    )
    parser.add_argument("--db-path", type=Path, default=DEFAULT_DB_PATH)
    args = parser.parse_args()
    init_database(args.db_path)


if __name__ == "__main__":
    main()
