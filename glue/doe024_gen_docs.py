"""DOE-024 Meta-Strategy Document Generator: L1 Strategy Delegation (30 HIGH documents).

This script generates meta-strategy documents for DOE-024 that specify which L1 strategy
to delegate to (burst_3 or adaptive_kill) based on situation tags.

Key Difference from DOE-022:
- DOE-022: decision.tactic field → maps to raw actions (ACTION_ATTACK, ACTION_MOVE_LEFT, etc.)
- DOE-024: decision.strategy field → specifies L1 strategy NAME ("burst_3" or "adaptive_kill")

Document Distribution (30 total):
- 15 docs → burst_3 (robust strategy for harsh conditions, F-053/F-055)
- 15 docs → adaptive_kill (efficiency strategy for favorable conditions)

All documents are deterministic (fixed seed 42) for reproducibility.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass
class MetaStrategyDocument:
    """Meta-strategy document matching OpenSearch schema for L1 delegation."""

    doc_id: str
    situation_tags: list[str]
    decision: dict[str, str]  # {strategy: "burst_3" | "adaptive_kill", rationale: "..."}
    quality: dict[str, float | str | int]
    metadata: dict[str, str | int | bool]

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "doc_id": self.doc_id,
            "situation_tags": self.situation_tags,
            "decision": self.decision,
            "quality": self.quality,
            "metadata": self.metadata,
        }

    def to_opensearch_bulk_line(self, index_name: str) -> str:
        """Convert to OpenSearch bulk index format (2 lines)."""
        action = json.dumps({"index": {"_index": index_name, "_id": self.doc_id}})
        doc = json.dumps(self.to_dict())
        return f"{action}\n{doc}"


class DOE024MetaDataGenerator:
    """Generate meta-strategy documents for L1 delegation (burst_3 vs adaptive_kill)."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        self.today = date.today().isoformat()

        # DOE-023 findings (F-053, F-055)
        self.finding_burst3 = "F-053"
        self.finding_adaptive = "F-055"
        self.source_experiment = "DOE-023"

        # Situation tags (from Rust rag/mod.rs logic)
        self.tag_health_low = "low_health"  # health < 30
        self.tag_health_full = "full_health"  # health >= 80
        self.tag_ammo_low = "low_ammo"  # ammo < 10
        self.tag_ammo_abundant = "ammo_abundant"  # ammo >= 50
        self.tag_multi_enemy = "multi_enemy"  # enemies_visible >= 3
        self.tag_single_enemy = "single_enemy"  # enemies_visible == 1
        self.tag_high_kills = "high_kills"  # kills >= 10 (NEW for DOE-024)
        self.tag_low_kills = "low_kills"  # kills < 5 (NEW for DOE-024)

    def generate_meta_strategy_docs(self) -> list[MetaStrategyDocument]:
        """Generate 30 HIGH quality meta-strategy documents.

        Distribution:
        - 5 docs: low_health + multi_enemy → burst_3 (harsh → robust)
        - 3 docs: low_health + single_enemy → burst_3 (low survival time)
        - 5 docs: full_health + multi_enemy + high_kills → adaptive_kill (favorable + kills)
        - 5 docs: full_health + ammo_abundant → adaptive_kill (resource-rich)
        - 3 docs: full_health + single_enemy → adaptive_kill (safe → efficiency)
        - 4 docs: multi_enemy + low_kills → burst_3 (early game pressure)
        - 5 docs: general fallback → burst_3 (default safest)
        """
        docs = []
        doc_counter = 1

        # 1. Harsh conditions → burst_3 (5 docs: low_health + multi_enemy)
        for i in range(5):
            doc_id = f"meta_high_{doc_counter:03d}"
            doc_counter += 1
            tags = [self.tag_health_low, self.tag_multi_enemy]
            docs.append(
                MetaStrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "strategy": "burst_3",
                        "rationale": "Harsh conditions favor burst_3 robustness (F-053, F-055)",
                    },
                    quality={
                        "trust_score": round(random.uniform(0.85, 0.95), 2),
                        "source_experiment": self.source_experiment,
                        "source_finding": self.finding_burst3,
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        # 2. Low health + single_enemy → burst_3 (3 docs: no time for adaptation)
        for i in range(3):
            doc_id = f"meta_high_{doc_counter:03d}"
            doc_counter += 1
            tags = [self.tag_health_low, self.tag_single_enemy]
            docs.append(
                MetaStrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "strategy": "burst_3",
                        "rationale": "Low survival time prevents adaptation (F-053)",
                    },
                    quality={
                        "trust_score": round(random.uniform(0.80, 0.90), 2),
                        "source_experiment": self.source_experiment,
                        "source_finding": self.finding_burst3,
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        # 3. Favorable + high_kills → adaptive_kill (5 docs: full_health + multi_enemy + high_kills)
        for i in range(5):
            doc_id = f"meta_high_{doc_counter:03d}"
            doc_counter += 1
            tags = [self.tag_health_full, self.tag_multi_enemy, self.tag_high_kills]
            docs.append(
                MetaStrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "strategy": "adaptive_kill",
                        "rationale": "Favorable conditions with kills enable adaptive efficiency (F-055)",
                    },
                    quality={
                        "trust_score": round(random.uniform(0.88, 0.97), 2),
                        "source_experiment": self.source_experiment,
                        "source_finding": self.finding_adaptive,
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        # 4. Resource-rich → adaptive_kill (5 docs: full_health + ammo_abundant)
        for i in range(5):
            doc_id = f"meta_high_{doc_counter:03d}"
            doc_counter += 1
            tags = [self.tag_health_full, self.tag_ammo_abundant]
            # Optionally add multi_enemy or single_enemy
            if i % 2 == 0:
                tags.append(self.tag_multi_enemy)
            else:
                tags.append(self.tag_single_enemy)
            docs.append(
                MetaStrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "strategy": "adaptive_kill",
                        "rationale": "Resource abundance enables efficiency strategy (F-055)",
                    },
                    quality={
                        "trust_score": round(random.uniform(0.85, 0.95), 2),
                        "source_experiment": self.source_experiment,
                        "source_finding": self.finding_adaptive,
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        # 5. Safe environment → adaptive_kill (3 docs: full_health + single_enemy)
        for i in range(3):
            doc_id = f"meta_high_{doc_counter:03d}"
            doc_counter += 1
            tags = [self.tag_health_full, self.tag_single_enemy]
            docs.append(
                MetaStrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "strategy": "adaptive_kill",
                        "rationale": "Safe environment allows efficiency maximization (F-055)",
                    },
                    quality={
                        "trust_score": round(random.uniform(0.82, 0.92), 2),
                        "source_experiment": self.source_experiment,
                        "source_finding": self.finding_adaptive,
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        # 6. Early game / high pressure → burst_3 (4 docs: multi_enemy + low_kills)
        for i in range(4):
            doc_id = f"meta_high_{doc_counter:03d}"
            doc_counter += 1
            tags = [self.tag_multi_enemy, self.tag_low_kills]
            # Optionally add health tag variation
            if i % 2 == 0:
                tags.append(self.tag_health_full)
            else:
                tags.append(self.tag_health_low)
            docs.append(
                MetaStrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "strategy": "burst_3",
                        "rationale": "Early game or high pressure favors burst robustness (F-053)",
                    },
                    quality={
                        "trust_score": round(random.uniform(0.78, 0.88), 2),
                        "source_experiment": self.source_experiment,
                        "source_finding": self.finding_burst3,
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        # 7. General fallback → burst_3 (5 docs: various tag combinations, default safe)
        fallback_tag_combos = [
            [self.tag_ammo_low, self.tag_multi_enemy],
            [self.tag_health_low, self.tag_ammo_low],
            [self.tag_multi_enemy],
            [self.tag_single_enemy, self.tag_ammo_low],
            [self.tag_low_kills],
        ]

        for i, tags in enumerate(fallback_tag_combos):
            doc_id = f"meta_high_{doc_counter:03d}"
            doc_counter += 1
            docs.append(
                MetaStrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "strategy": "burst_3",
                        "rationale": "Default to safest option when uncertain (F-053)",
                    },
                    quality={
                        "trust_score": round(random.uniform(0.75, 0.85), 2),
                        "source_experiment": self.source_experiment,
                        "source_finding": self.finding_burst3,
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        return docs

    def save_documents(self, output_dir: Path) -> None:
        """Generate and save all documents in multiple formats."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Generate documents
        all_docs = self.generate_meta_strategy_docs()

        # Validate uniqueness
        all_doc_ids = [d.doc_id for d in all_docs]
        assert len(all_doc_ids) == len(set(all_doc_ids)), "Duplicate doc_id found!"
        assert len(all_doc_ids) == 30, f"Expected 30 docs, got {len(all_doc_ids)}"

        # Validate tags non-empty
        for doc in all_docs:
            assert len(doc.situation_tags) > 0, f"{doc.doc_id} has empty tags!"

        # Validate trust_score range
        for doc in all_docs:
            ts = doc.quality["trust_score"]
            assert 0.0 <= ts <= 1.0, f"{doc.doc_id} trust_score {ts} out of range!"

        # Validate decision.strategy field
        for doc in all_docs:
            strategy = doc.decision.get("strategy")
            assert strategy in [
                "burst_3",
                "adaptive_kill",
            ], f"{doc.doc_id} has invalid strategy: {strategy}"

        # Count strategy distribution
        burst_count = sum(1 for d in all_docs if d.decision["strategy"] == "burst_3")
        adaptive_count = sum(
            1 for d in all_docs if d.decision["strategy"] == "adaptive_kill"
        )
        print(f"Strategy distribution: burst_3={burst_count}, adaptive_kill={adaptive_count}")

        # Save as JSON array
        with open(output_dir / "meta_strategy_docs.json", "w") as f:
            json.dump([d.to_dict() for d in all_docs], f, indent=2)

        # Save as NDJSON for OpenSearch bulk indexing
        with open(output_dir / "meta_strategy_docs.ndjson", "w") as f:
            for doc in all_docs:
                f.write(doc.to_opensearch_bulk_line("strategies_meta") + "\n")

        print(f"Generated {len(all_docs)} meta-strategy documents")
        print(f"Saved to: {output_dir}")
        print("✓ All documents pass validation")


def main():
    """Entry point for script execution."""
    # Output to container-side path
    output_dir = Path("/app/data/doe-024-data")
    generator = DOE024MetaDataGenerator(seed=42)
    generator.save_documents(output_dir)


if __name__ == "__main__":
    main()
