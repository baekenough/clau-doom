#!/usr/bin/env python3
"""Embedding model benchmark for clau-doom situation vectorization.

Compares ONNX MiniLM (384-dim, local) vs Ollama nomic-embed-text (768-dim, container).

Usage:
    python scripts/benchmarks/embedding_bench.py
    python scripts/benchmarks/embedding_bench.py --onnx-only
    python scripts/benchmarks/embedding_bench.py --ollama-only
"""

from __future__ import annotations

import argparse
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Protocol

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

WARMUP_RUNS = 100
BENCH_RUNS = 1000
BATCH_SIZES = [10, 50, 100]

# Game situation templates for generating test corpus
_HEALTH_LEVELS = ["Health critical at 10%", "Health low at 30%", "Health moderate at 60%", "Full health at 100%"]
_ENEMY_COUNTS = ["1 enemy visible", "3 enemies closing in", "5 enemies surrounding", "no enemies nearby"]
_LOCATIONS = ["narrow corridor", "open arena", "small room", "elevated platform", "stairwell"]
_AMMO_STATES = ["no ammo remaining", "low ammo (10 rounds)", "moderate ammo (30 rounds)", "ammo abundant (80+ rounds)"]
_WEAPONS = ["fist only", "pistol equipped", "shotgun equipped", "chaingun ready", "rocket launcher armed"]


def generate_situation_corpus(np, n: int = 100, seed: int = 42) -> list[str]:
    """Generate n game situation descriptions from templates."""
    rng = np.random.default_rng(seed)
    corpus: list[str] = []
    for _ in range(n):
        health = rng.choice(_HEALTH_LEVELS)
        enemies = rng.choice(_ENEMY_COUNTS)
        location = rng.choice(_LOCATIONS)
        ammo = rng.choice(_AMMO_STATES)
        weapon = rng.choice(_WEAPONS)
        corpus.append(f"{health}, {enemies} in {location}, {ammo}, {weapon}")
    return corpus


# Pairs for semantic quality evaluation
SIMILAR_PAIRS = [
    ("Health critical at 15%, 4 enemies closing in from corridor, low ammo, pistol only",
     "Health very low at 10%, 3 enemies approaching in narrow hallway, almost no ammo, pistol equipped"),
    ("Full health, open arena, 1 distant imp, 50 ammo remaining",
     "Health at 100%, large open area, single enemy far away, plenty of ammo"),
    ("Trapped in small room, 5 enemies outside, shotgun ready, health dropping",
     "Cornered in tight space, multiple enemies blocking exit, shotgun equipped, taking damage"),
    ("Elevated position, 2 enemies below, rocket launcher, full health",
     "Standing on high platform, couple of enemies underneath, rocket launcher armed, health full"),
    ("Running through corridor, low health, being chased by 3 enemies, need medkit",
     "Fleeing down hallway, health critical, 3 enemies pursuing, desperately need health"),
    ("Open arena fight, circle strafing imp, chaingun blazing, health stable",
     "Large area combat, circle strafing around enemy, chaingun firing, health holding steady"),
    ("Ambushed from behind, multiple enemies, low ammo, need to retreat",
     "Surprised by enemies from rear, several hostiles, ammo running out, must fall back"),
    ("Holding chokepoint, enemies funneling in, shotgun effective, ammo draining",
     "Defending narrow passage, enemies approaching single file, shotgun working well, using ammo fast"),
    ("Long range engagement, single enemy, pistol shots, conserving ammo",
     "Distant target, one enemy, firing pistol carefully, saving ammunition"),
    ("Final boss room, BFG ready, full health and ammo, prepared for fight",
     "Boss arena entered, BFG charged, maximum health and ammunition, ready for battle"),
]

DIFFERENT_PAIRS = [
    ("Health critical at 15%, 4 enemies closing in from corridor, low ammo, pistol only",
     "Full health, open arena, 1 distant imp, 50 ammo remaining"),
    ("Trapped in small room, 5 enemies outside, shotgun ready, health dropping",
     "Long range engagement, single enemy, pistol shots, conserving ammo"),
    ("Elevated position, 2 enemies below, rocket launcher, full health",
     "Running through corridor, low health, being chased by 3 enemies, need medkit"),
    ("Open arena fight, circle strafing imp, chaingun blazing, health stable",
     "Ambushed from behind, multiple enemies, low ammo, need to retreat"),
    ("Holding chokepoint, enemies funneling in, shotgun effective, ammo draining",
     "Full health, open arena, no enemies visible, exploring for secrets"),
    ("Final boss room, BFG ready, full health and ammo, prepared for fight",
     "Fleeing down hallway, health critical, no weapon, completely defenseless"),
    ("Peaceful exploration, no threats, full resources, searching for keys",
     "Desperate last stand, surrounded, 1 HP, fist only"),
    ("Sniping from distance with chaingun, enemies unaware, safe position",
     "Melee range, punching demon, health critical, nowhere to run"),
    ("Swimming through nukage, health draining, no enemies, need radiation suit",
     "Standing on safe ground, full health, 5 enemies, rocket launcher ready"),
    ("Secret area found, collecting powerups, no danger, bonus items",
     "Trapped in crusher, health dropping fast, enemies shooting, need escape"),
]


# ---------------------------------------------------------------------------
# Embedder Protocol
# ---------------------------------------------------------------------------

class Embedder(Protocol):
    name: str
    dimension: int

    def embed_single(self, text: str) -> list[float]: ...
    def embed_batch(self, texts: list[str]) -> list[list[float]]: ...


# ---------------------------------------------------------------------------
# ONNX MiniLM Embedder
# ---------------------------------------------------------------------------

class OnnxMiniLMEmbedder:
    name = "ONNX MiniLM-L6-v2"
    dimension = 384

    def __init__(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError:
            print(
                "ERROR: sentence-transformers not installed.\n"
                "  pip install sentence-transformers>=2.3.0\n"
                "  or: pip install -r scripts/benchmarks/requirements.txt"
            )
            sys.exit(1)

        print("Loading all-MiniLM-L6-v2 model...")
        self._model = SentenceTransformer("all-MiniLM-L6-v2")
        self._model.encode(["warmup text"])
        print("  Model loaded.")

    def embed_single(self, text: str) -> list[float]:
        embedding = self._model.encode([text], normalize_embeddings=True)
        return embedding[0].tolist()

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        embeddings = self._model.encode(texts, normalize_embeddings=True)
        return embeddings.tolist()


# ---------------------------------------------------------------------------
# Ollama Embedder
# ---------------------------------------------------------------------------

class OllamaEmbedder:
    name = "Ollama nomic-embed-text"
    dimension = 768

    def __init__(self, base_url: str = "http://localhost:11434") -> None:
        try:
            import requests
            self._requests = requests
        except ImportError:
            print("ERROR: requests not installed.\n  pip install requests>=2.31.0")
            sys.exit(1)

        self._base_url = base_url
        self._embed_url = f"{base_url}/api/embeddings"

        print(f"Connecting to Ollama at {base_url}...")
        try:
            resp = self._requests.get(f"{base_url}/api/tags", timeout=5)
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            if not any("nomic-embed-text" in m for m in models):
                print(
                    "WARNING: nomic-embed-text model not found in Ollama.\n"
                    "  Pull it with: ollama pull nomic-embed-text\n"
                    "  Available models:", models
                )
            else:
                print("  Ollama connected, nomic-embed-text available.")
        except Exception as e:
            print(
                f"ERROR: Cannot connect to Ollama at {base_url}\n"
                f"  {e}\n\n"
                f"Start Ollama first:\n"
                f"  docker compose up -d ollama\n"
                f"  # or:\n"
                f"  ollama serve"
            )
            raise

        self._embed_one("warmup text")

    def _embed_one(self, text: str) -> list[float]:
        resp = self._requests.post(
            self._embed_url,
            json={"model": "nomic-embed-text", "prompt": text},
            timeout=30,
        )
        resp.raise_for_status()
        return resp.json()["embedding"]

    def embed_single(self, text: str) -> list[float]:
        return self._embed_one(text)

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(t) for t in texts]


# ---------------------------------------------------------------------------
# Benchmark Logic
# ---------------------------------------------------------------------------

@dataclass
class LatencyResult:
    p50_ms: float = 0.0
    p90_ms: float = 0.0
    p95_ms: float = 0.0
    p99_ms: float = 0.0
    max_ms: float = 0.0


@dataclass
class BenchmarkResult:
    model_name: str = ""
    dimension: int = 0
    single_latency: LatencyResult = field(default_factory=LatencyResult)
    batch_latencies: dict[int, float] = field(default_factory=dict)
    memory_mb: float = 0.0
    semantic_similar_mean: float = 0.0
    semantic_different_mean: float = 0.0


def cosine_similarity(np, a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    dot = float(np.dot(va, vb))
    norm = float(np.linalg.norm(va) * np.linalg.norm(vb))
    if norm == 0:
        return 0.0
    return dot / norm


def measure_memory_mb() -> float:
    """Return current process RSS in MB."""
    try:
        import psutil
        proc = psutil.Process()
        return proc.memory_info().rss / (1024 * 1024)
    except ImportError:
        return 0.0


def benchmark_embedder(
    np,
    embedder: Embedder,
    corpus: list[str],
    n_warmup: int = WARMUP_RUNS,
    n_bench: int = BENCH_RUNS,
) -> BenchmarkResult:
    """Run full benchmark suite on an embedder."""
    result = BenchmarkResult(
        model_name=embedder.name,
        dimension=embedder.dimension,
    )

    mem_before = measure_memory_mb()

    # Single embedding latency
    print(f"  Single embedding: {n_warmup} warmup + {n_bench} benchmark...")
    for i in range(n_warmup):
        embedder.embed_single(corpus[i % len(corpus)])

    latencies_ns: list[int] = []
    for i in range(n_bench):
        text = corpus[i % len(corpus)]
        t0 = time.perf_counter_ns()
        embedder.embed_single(text)
        t1 = time.perf_counter_ns()
        latencies_ns.append(t1 - t0)

    arr = np.array(latencies_ns, dtype=np.float64) / 1e6
    result.single_latency = LatencyResult(
        p50_ms=float(np.percentile(arr, 50)),
        p90_ms=float(np.percentile(arr, 90)),
        p95_ms=float(np.percentile(arr, 95)),
        p99_ms=float(np.percentile(arr, 99)),
        max_ms=float(np.max(arr)),
    )

    # Batch embedding latency
    for batch_size in BATCH_SIZES:
        batch = corpus[:batch_size]
        print(f"  Batch {batch_size}: measuring total time...")
        t0 = time.perf_counter_ns()
        embedder.embed_batch(batch)
        t1 = time.perf_counter_ns()
        result.batch_latencies[batch_size] = (t1 - t0) / 1e6

    mem_after = measure_memory_mb()
    result.memory_mb = mem_after - mem_before if mem_before > 0 else mem_after

    # Semantic quality
    print("  Semantic quality: similar pairs...")
    sim_scores: list[float] = []
    for text_a, text_b in SIMILAR_PAIRS:
        emb_a = embedder.embed_single(text_a)
        emb_b = embedder.embed_single(text_b)
        sim_scores.append(cosine_similarity(np, emb_a, emb_b))
    result.semantic_similar_mean = float(np.mean(sim_scores))

    print("  Semantic quality: different pairs...")
    diff_scores: list[float] = []
    for text_a, text_b in DIFFERENT_PAIRS:
        emb_a = embedder.embed_single(text_a)
        emb_b = embedder.embed_single(text_b)
        diff_scores.append(cosine_similarity(np, emb_a, emb_b))
    result.semantic_different_mean = float(np.mean(diff_scores))

    return result


# ---------------------------------------------------------------------------
# Result Formatting
# ---------------------------------------------------------------------------

def format_results(results: list[BenchmarkResult], timestamp: str) -> str:
    """Format benchmark results as a markdown report."""
    lines = [
        "# Embedding Model Benchmark Results",
        "",
        f"**Timestamp**: {timestamp}",
        f"**Single latency**: {BENCH_RUNS} runs (+ {WARMUP_RUNS} warmup)",
        f"**Batch sizes**: {BATCH_SIZES}",
        f"**Similar pairs**: {len(SIMILAR_PAIRS)}",
        f"**Different pairs**: {len(DIFFERENT_PAIRS)}",
        "",
        "## Comparison Table",
        "",
    ]

    if len(results) == 0:
        lines.append("No results to display.")
        return "\n".join(lines)

    # Build comparison table
    headers = ["Metric"] + [r.model_name for r in results]
    rows: list[list[str]] = []

    rows.append(["Dimension"] + [str(r.dimension) for r in results])
    rows.append(["Single p50 (ms)"] + [f"{r.single_latency.p50_ms:.2f}" for r in results])
    rows.append(["Single p90 (ms)"] + [f"{r.single_latency.p90_ms:.2f}" for r in results])
    rows.append(["Single p95 (ms)"] + [f"{r.single_latency.p95_ms:.2f}" for r in results])
    rows.append(["Single p99 (ms)"] + [f"{r.single_latency.p99_ms:.2f}" for r in results])
    rows.append(["Single max (ms)"] + [f"{r.single_latency.max_ms:.2f}" for r in results])

    for bs in BATCH_SIZES:
        rows.append([f"Batch {bs} (ms)"] + [
            f"{r.batch_latencies.get(bs, 0):.1f}" for r in results
        ])

    rows.append(["Memory delta (MB)"] + [
        f"{r.memory_mb:.1f}" if r.memory_mb > 0 else "N/A" for r in results
    ])
    rows.append(["Sim. pairs mean cos"] + [f"{r.semantic_similar_mean:.3f}" for r in results])
    rows.append(["Diff. pairs mean cos"] + [f"{r.semantic_different_mean:.3f}" for r in results])

    # Format as markdown table
    col_widths = [max(len(h), max(len(row[i]) for row in rows)) for i, h in enumerate(headers)]
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    sep_line = "|" + "|".join("-" * (w + 2) for w in col_widths) + "|"
    lines.append(header_line)
    lines.append(sep_line)
    for row in rows:
        lines.append("| " + " | ".join(row[i].ljust(col_widths[i]) for i, _ in enumerate(headers)) + " |")

    # Semantic quality verdict
    lines.extend(["", "## Semantic Quality Verdict", ""])
    for r in results:
        sim_pass = r.semantic_similar_mean > 0.7
        diff_pass = r.semantic_different_mean < 0.3
        lines.append(f"### {r.model_name}")
        lines.append(f"- Similar pairs mean cosine: **{r.semantic_similar_mean:.3f}** "
                      f"({'PASS' if sim_pass else 'BELOW TARGET'}, target > 0.7)")
        lines.append(f"- Different pairs mean cosine: **{r.semantic_different_mean:.3f}** "
                      f"({'PASS' if diff_pass else 'ABOVE TARGET'}, target < 0.3)")
        overall = "GOOD" if sim_pass and diff_pass else "ACCEPTABLE" if sim_pass else "NEEDS REVIEW"
        lines.append(f"- Overall semantic quality: **{overall}**")
        lines.append("")

    # Latency verdict
    lines.extend(["## Latency Verdict", ""])
    for r in results:
        passed = r.single_latency.p99_ms < 10.0
        lines.append(f"### {r.model_name}")
        lines.append(f"- Single p99: **{r.single_latency.p99_ms:.2f} ms** "
                      f"({'PASS' if passed else 'ABOVE TARGET'}, target < 10ms)")
        lines.append("")

    # Recommendation
    lines.extend(["## Recommendation", ""])
    if len(results) == 2:
        onnx_r = results[0] if "ONNX" in results[0].model_name else results[1]
        ollama_r = results[1] if "ONNX" in results[0].model_name else results[0]

        if onnx_r.single_latency.p99_ms < 10.0 and onnx_r.semantic_similar_mean > 0.7:
            lines.append("**ONNX MiniLM recommended**: Meets latency target with good semantic quality, "
                          "no external dependency required.")
        elif ollama_r.single_latency.p99_ms < 10.0 and ollama_r.semantic_similar_mean > 0.7:
            lines.append("**Ollama nomic-embed-text recommended**: Better semantic quality justifies "
                          "container dependency.")
        else:
            lines.append("**Neither model fully meets all targets.** Review results and consider trade-offs.")
    elif len(results) == 1:
        r = results[0]
        if r.single_latency.p99_ms < 10.0 and r.semantic_similar_mean > 0.7:
            lines.append(f"**{r.model_name}**: Meets latency and quality targets.")
        else:
            lines.append(f"**{r.model_name}**: Review results against targets.")

    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Embedding model benchmark for clau-doom situation vectorization.",
    )
    parser.add_argument("--onnx-only", action="store_true", help="Only benchmark ONNX MiniLM")
    parser.add_argument("--ollama-only", action="store_true", help="Only benchmark Ollama nomic-embed-text")
    parser.add_argument("--ollama-url", default="http://localhost:11434", help="Ollama base URL")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for corpus generation")
    parser.add_argument(
        "--bench-runs",
        type=int,
        default=BENCH_RUNS,
        help=f"Number of benchmark runs for single latency (default: {BENCH_RUNS})",
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

    global BENCH_RUNS
    BENCH_RUNS = args.bench_runs

    corpus = generate_situation_corpus(np, 100, seed=args.seed)
    print(f"Generated {len(corpus)} situation descriptions")
    print(f"Sample: '{corpus[0]}'")

    run_onnx = not args.ollama_only
    run_ollama = not args.onnx_only

    results: list[BenchmarkResult] = []

    if run_onnx:
        print(f"\n{'=' * 50}")
        print("Benchmarking ONNX MiniLM-L6-v2")
        print(f"{'=' * 50}")
        try:
            embedder = OnnxMiniLMEmbedder()
            result = benchmark_embedder(np, embedder, corpus, n_bench=BENCH_RUNS)
            results.append(result)
            print(f"  Single p99: {result.single_latency.p99_ms:.2f} ms")
            print(f"  Semantic similar: {result.semantic_similar_mean:.3f}")
            print(f"  Semantic different: {result.semantic_different_mean:.3f}")
        except Exception as e:
            print(f"  ONNX benchmark failed: {e}")

    if run_ollama:
        print(f"\n{'=' * 50}")
        print("Benchmarking Ollama nomic-embed-text")
        print(f"{'=' * 50}")
        try:
            embedder = OllamaEmbedder(base_url=args.ollama_url)
            result = benchmark_embedder(np, embedder, corpus, n_bench=BENCH_RUNS)
            results.append(result)
            print(f"  Single p99: {result.single_latency.p99_ms:.2f} ms")
            print(f"  Semantic similar: {result.semantic_similar_mean:.3f}")
            print(f"  Semantic different: {result.semantic_different_mean:.3f}")
        except Exception as e:
            print(f"  Ollama benchmark failed: {e}")

    if not results:
        print("\nNo benchmarks completed successfully.")
        sys.exit(1)

    report = format_results(results, timestamp)
    print(f"\n{'=' * 60}")
    print(report)

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(parents=True, exist_ok=True)
    results_path = results_dir / "embedding_results.md"
    results_path.write_text(report)
    print(f"\nResults saved to {results_path}")


if __name__ == "__main__":
    main()
