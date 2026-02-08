"""Generate initial strategy documents for OpenSearch seeding.

Creates 50-100 synthetic strategy documents for the Full RAG condition
in DOE-001. These provide the initial knowledge base for kNN search.
"""
from __future__ import annotations

import json
import logging
import math
import random
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)

SEED_CREATED_AT = "2026-02-08T00:00:00Z"


def wilson_lower_bound(successes: int, total: int, z: float = 1.96) -> float:
    """Compute Wilson score lower bound for a binomial proportion."""
    if total == 0:
        return 0.0
    p = successes / total
    denominator = 1 + z**2 / total
    center = p + z**2 / (2 * total)
    spread = z * math.sqrt(p * (1 - p) / total + z**2 / (4 * total**2))
    return (center - spread) / denominator

SITUATION_TAGS = [
    "narrow_corridor", "open_arena", "multi_enemy", "single_enemy",
    "low_health", "full_health", "low_ammo", "ammo_abundant",
    "close_range", "long_range", "elevated_position", "trapped",
    "surrounded", "flanked", "retreating", "advancing",
]

TACTICS = [
    "retreat_and_funnel", "aggressive_push", "circle_strafe",
    "cover_peek", "hold_position", "flank_left", "flank_right",
    "kite_backward", "charge_forward", "dodge_and_shoot",
]

WEAPONS = ["fist", "pistol", "shotgun", "chaingun", "rocket_launcher", "plasma_rifle", "bfg"]


@dataclass
class StrategyDocument:
    """A strategy document for OpenSearch seeding."""
    doc_id: str
    situation_tags: list[str]
    tactic: str
    weapon: str
    success_rate: float
    sample_size: int
    confidence_tier: str  # low, medium, high
    agent_id: str = "GEN1_SEED"
    generation: int = 0
    description: str = ""
    trust_score: float = 0.0

    def to_opensearch_doc(self) -> dict:
        """Format for OpenSearch bulk indexing."""
        return {
            "doc_id": self.doc_id,
            "agent_id": self.agent_id,
            "generation": self.generation,
            "situation_tags": self.situation_tags,
            "decision": {
                "tactic": self.tactic,
                "weapon": self.weapon,
            },
            "quality": {
                "success_rate": self.success_rate,
                "sample_size": self.sample_size,
                "confidence_tier": self.confidence_tier,
                "trust_score": self.trust_score,
            },
            "metadata": {
                "created_at": SEED_CREATED_AT,
                "source_experiment": "SEED",
                "retired": False,
            },
            "description": self.description,
        }


def generate_strategy_docs(
    count: int = 75,
    seed: int = 42,
) -> list[StrategyDocument]:
    """Generate synthetic strategy documents.

    Uses fixed seed for reproducibility.
    """
    rng = random.Random(seed)
    np_rng = np.random.default_rng(seed)

    docs: list[StrategyDocument] = []

    for i in range(count):
        n_tags = rng.randint(1, 4)
        tags = rng.sample(SITUATION_TAGS, n_tags)
        tactic = rng.choice(TACTICS)
        weapon = rng.choice(WEAPONS)

        success_rate = round(float(np_rng.uniform(0.3, 0.95)), 2)
        sample_size = rng.randint(10, 200)

        if sample_size >= 100 and success_rate >= 0.7:
            confidence = "high"
        elif sample_size >= 30:
            confidence = "medium"
        else:
            confidence = "low"

        description = (
            f"When facing {', '.join(tags)}: "
            f"use {tactic} with {weapon}. "
            f"Success rate: {success_rate:.0%} over {sample_size} trials."
        )

        successes = int(round(success_rate * sample_size))
        trust = round(wilson_lower_bound(successes, sample_size), 4)

        docs.append(StrategyDocument(
            doc_id=f"strategy_{i:04d}",
            situation_tags=tags,
            tactic=tactic,
            weapon=weapon,
            success_rate=success_rate,
            sample_size=sample_size,
            confidence_tier=confidence,
            description=description,
            trust_score=trust,
        ))

    return docs


def save_strategy_docs_json(docs: list[StrategyDocument], output_path: str) -> None:
    """Save strategy docs to JSON for later OpenSearch bulk import."""
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    data = [{"_id": d.doc_id, **d.to_opensearch_doc()} for d in docs]
    out.write_text(json.dumps(data, indent=2))
    logger.info(f"Saved {len(docs)} strategy documents to {out}")


if __name__ == "__main__":
    docs = generate_strategy_docs(75, seed=42)
    save_strategy_docs_json(docs, "volumes/data/strategy_seed_docs.json")
    print(f"Generated {len(docs)} strategy documents")

    # Summary
    from collections import Counter
    tactics = Counter(d.tactic for d in docs)
    confidences = Counter(d.confidence_tier for d in docs)
    print(f"Tactics distribution: {dict(tactics)}")
    print(f"Confidence distribution: {dict(confidences)}")
