#!/usr/bin/env python3
"""OpenSearch kNN latency benchmark for clau-doom Level 2 RAG search.

Tests cosine similarity kNN search at various index sizes to validate
the < 100ms P99 requirement for real-time strategy document retrieval.

Usage:
    # Requires OpenSearch running at localhost:9200
    python scripts/benchmarks/opensearch_knn_bench.py
    python scripts/benchmarks/opensearch_knn_bench.py --host localhost --port 9200
"""

from __future__ import annotations

import argparse
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

INDEX_NAME = "strategy_bench"
VECTOR_DIM = 384
K = 5
WARMUP_QUERIES = 100
BENCH_QUERIES = 1000
DOC_SIZES = [100, 500, 1000, 5000]
BATCH_INSERT_SIZE = 100

HNSW_EF_CONSTRUCTION = 256
HNSW_M = 16

SITUATION_TAGS_POOL = [
    "narrow_corridor", "open_arena", "multi_enemy", "single_enemy",
    "low_health", "full_health", "low_ammo", "ammo_abundant",
    "close_range", "long_range", "elevated_position", "trapped",
]

TACTICS_POOL = [
    "retreat_and_funnel", "aggressive_push", "circle_strafe",
    "cover_peek", "hold_position", "flank_left", "flank_right",
]

WEAPONS_POOL = ["fist", "pistol", "shotgun", "chaingun", "rocket_launcher", "plasma_rifle", "bfg"]


# ---------------------------------------------------------------------------
# Helpers (np imported lazily)
# ---------------------------------------------------------------------------

def random_normalized_vector(np, rng, dim: int = VECTOR_DIM) -> list[float]:
    """Generate a random unit-norm vector of given dimension."""
    vec = rng.standard_normal(dim).astype(np.float32)
    vec /= np.linalg.norm(vec)
    return vec.tolist()


def random_document(np, rng, doc_id: int) -> dict:
    """Generate a synthetic strategy document."""
    n_tags = rng.integers(1, 5)
    tags = rng.choice(SITUATION_TAGS_POOL, size=n_tags, replace=False).tolist()
    return {
        "_id": str(doc_id),
        "situation_embedding": random_normalized_vector(np, rng),
        "situation_tags": tags,
        "decision": {
            "tactic": rng.choice(TACTICS_POOL),
            "weapon": rng.choice(WEAPONS_POOL),
        },
        "quality": {
            "success_rate": round(float(rng.uniform(0.3, 0.95)), 2),
            "sample_size": int(rng.integers(10, 200)),
            "confidence_tier": rng.choice(["low", "medium", "high"]),
        },
    }


def percentile_ms(np, latencies_ns: list[int], p: float) -> float:
    """Return the p-th percentile latency in milliseconds."""
    return float(np.percentile(latencies_ns, p)) / 1e6


# ---------------------------------------------------------------------------
# Index Management
# ---------------------------------------------------------------------------

def create_index(client) -> None:
    """Create (or recreate) the benchmark index with kNN mapping."""
    if client.indices.exists(index=INDEX_NAME):
        client.indices.delete(index=INDEX_NAME)

    body = {
        "settings": {
            "index": {
                "knn": True,
                "knn.algo_param.ef_search": 256,
                "number_of_shards": 1,
                "number_of_replicas": 0,
            }
        },
        "mappings": {
            "properties": {
                "situation_embedding": {
                    "type": "knn_vector",
                    "dimension": VECTOR_DIM,
                    "method": {
                        "name": "hnsw",
                        "space_type": "cosinesimil",
                        "engine": "nmslib",
                        "parameters": {
                            "ef_construction": HNSW_EF_CONSTRUCTION,
                            "m": HNSW_M,
                        },
                    },
                },
                "situation_tags": {"type": "keyword"},
                "decision": {
                    "properties": {
                        "tactic": {"type": "keyword"},
                        "weapon": {"type": "keyword"},
                    }
                },
                "quality": {
                    "properties": {
                        "success_rate": {"type": "float"},
                        "sample_size": {"type": "integer"},
                        "confidence_tier": {"type": "keyword"},
                    }
                },
            }
        },
    }
    client.indices.create(index=INDEX_NAME, body=body)


def bulk_index_documents(client, docs: list[dict]) -> None:
    """Index documents using the bulk API in batches."""
    actions: list[dict] = []
    for doc in docs:
        doc_id = doc.pop("_id")
        actions.append({"index": {"_index": INDEX_NAME, "_id": doc_id}})
        actions.append(doc)

    for start in range(0, len(actions), BATCH_INSERT_SIZE * 2):
        batch = actions[start : start + BATCH_INSERT_SIZE * 2]
        client.bulk(body=batch)

    client.indices.refresh(index=INDEX_NAME)
    client.indices.forcemerge(index=INDEX_NAME, max_num_segments=1)
    time.sleep(0.5)


# ---------------------------------------------------------------------------
# Benchmark
# ---------------------------------------------------------------------------

def run_knn_queries(np, client, rng, n_warmup: int, n_bench: int) -> list[int]:
    """Run kNN queries and return latencies in nanoseconds (bench only)."""
    query_template = {
        "size": K,
        "query": {
            "knn": {
                "situation_embedding": {
                    "vector": [],
                    "k": K,
                }
            }
        },
        "_source": ["situation_tags", "decision", "quality"],
    }

    for _ in range(n_warmup):
        query_template["query"]["knn"]["situation_embedding"]["vector"] = random_normalized_vector(np, rng)
        client.search(index=INDEX_NAME, body=query_template)

    latencies_ns: list[int] = []
    for _ in range(n_bench):
        query_template["query"]["knn"]["situation_embedding"]["vector"] = random_normalized_vector(np, rng)
        t0 = time.perf_counter_ns()
        client.search(index=INDEX_NAME, body=query_template)
        t1 = time.perf_counter_ns()
        latencies_ns.append(t1 - t0)

    return latencies_ns


# ---------------------------------------------------------------------------
# Result Formatting
# ---------------------------------------------------------------------------

def format_results(np, all_results: dict[int, list[int]], timestamp: str) -> str:
    """Format benchmark results as a markdown report."""
    lines = [
        "# OpenSearch kNN Benchmark Results",
        "",
        f"**Timestamp**: {timestamp}",
        f"**Vector dimension**: {VECTOR_DIM}",
        f"**k**: {K}",
        f"**Queries per size**: {BENCH_QUERIES} (+ {WARMUP_QUERIES} warmup)",
        f"**HNSW params**: ef_construction={HNSW_EF_CONSTRUCTION}, m={HNSW_M}",
        "**Space type**: cosinesimil",
        "**Engine**: nmslib",
        "",
        "## Latency Results",
        "",
        "| Docs | p50 (ms) | p90 (ms) | p95 (ms) | p99 (ms) | max (ms) |",
        "|-----:|---------:|---------:|---------:|---------:|---------:|",
    ]

    for doc_count in DOC_SIZES:
        if doc_count not in all_results:
            continue
        lats = all_results[doc_count]
        p50 = percentile_ms(np, lats, 50)
        p90 = percentile_ms(np, lats, 90)
        p95 = percentile_ms(np, lats, 95)
        p99 = percentile_ms(np, lats, 99)
        mx = percentile_ms(np, lats, 100)
        lines.append(
            f"| {doc_count:>5} | {p50:>8.2f} | {p90:>8.2f} | {p95:>8.2f} | {p99:>8.2f} | {mx:>8.2f} |"
        )

    target_size = 1000
    if target_size in all_results:
        p99_at_target = percentile_ms(np, all_results[target_size], 99)
        passed = p99_at_target < 100.0
        verdict = "PASS" if passed else "FAIL"
        lines.extend([
            "",
            "## Verdict",
            "",
            f"P99 at {target_size} docs: **{p99_at_target:.2f} ms**",
            "",
            f"Requirement: P99 < 100ms at {target_size} docs",
            "",
            f"**Result: {verdict}**",
        ])
        if not passed:
            lines.extend([
                "",
                "> CONCERN: P99 exceeds 100ms threshold. Consider:",
                "> - Increasing DuckDB L1 cache scope",
                "> - Reducing OpenSearch ef_search parameter",
                "> - Pre-filtering with situation_tags before kNN",
            ])
    else:
        lines.extend([
            "",
            "## Verdict",
            "",
            f"Target size ({target_size}) was not tested.",
        ])

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="OpenSearch kNN latency benchmark for clau-doom Level 2 RAG search.",
    )
    parser.add_argument("--host", default="localhost", help="OpenSearch host (default: localhost)")
    parser.add_argument("--port", type=int, default=9200, help="OpenSearch port (default: 9200)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducibility")
    parser.add_argument(
        "--sizes",
        nargs="+",
        type=int,
        default=DOC_SIZES,
        help=f"Document sizes to test (default: {DOC_SIZES})",
    )
    parser.add_argument(
        "--queries",
        type=int,
        default=BENCH_QUERIES,
        help=f"Number of benchmark queries per size (default: {BENCH_QUERIES})",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

    # Deferred imports so --help works without dependencies
    try:
        import numpy as np
    except ImportError:
        print("ERROR: numpy not installed.\n  pip install -r scripts/benchmarks/requirements.txt")
        sys.exit(1)

    try:
        from opensearchpy import OpenSearch
    except ImportError:
        print(
            "ERROR: opensearch-py not installed.\n"
            "  pip install opensearch-py>=2.4.0\n"
            "  or: pip install -r scripts/benchmarks/requirements.txt"
        )
        sys.exit(1)

    rng = np.random.default_rng(args.seed)

    client = OpenSearch(
        hosts=[{"host": args.host, "port": args.port}],
        http_auth=("admin", "admin"),
        use_ssl=False,
        verify_certs=False,
        ssl_show_warn=False,
    )

    try:
        info = client.info()
        print(f"Connected to OpenSearch {info['version']['number']}")
    except Exception as e:
        print(
            f"ERROR: Cannot connect to OpenSearch at {args.host}:{args.port}\n"
            f"  {e}\n\n"
            f"Start OpenSearch first:\n"
            f"  docker compose up -d opensearch\n"
            f"  # or:\n"
            f"  docker run -d -p 9200:9200 -e 'discovery.type=single-node' "
            f"-e 'DISABLE_SECURITY_PLUGIN=true' opensearchproject/opensearch:2.17.1"
        )
        sys.exit(1)

    all_results: dict[int, list[int]] = {}

    for doc_count in args.sizes:
        print(f"\n--- Benchmarking with {doc_count} documents ---")

        print(f"  Creating index with {doc_count} documents...")
        create_index(client)
        docs = [random_document(np, rng, i) for i in range(doc_count)]
        bulk_index_documents(client, docs)

        count = client.count(index=INDEX_NAME)["count"]
        print(f"  Indexed {count} documents (expected {doc_count})")

        print(f"  Running {WARMUP_QUERIES} warmup + {args.queries} benchmark queries...")
        latencies_ns = run_knn_queries(np, client, rng, WARMUP_QUERIES, args.queries)
        all_results[doc_count] = latencies_ns

        p50 = percentile_ms(np, latencies_ns, 50)
        p99 = percentile_ms(np, latencies_ns, 99)
        print(f"  Results: p50={p50:.2f}ms, p99={p99:.2f}ms")

    try:
        client.indices.delete(index=INDEX_NAME)
    except Exception:
        pass

    report = format_results(np, all_results, timestamp)
    print(f"\n{'=' * 60}")
    print(report)

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_path = results_dir / "opensearch_knn_results.md"
    results_path.write_text(report)
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
