"""DOE-022 Phase A: Generate 100 strategy documents for L2 RAG testing.

This script generates:
- 50 HIGH quality documents: tactics based on DOE-020 top performers (burst_3, adaptive_kill)
- 50 LOW quality documents: mismatched/unhelpful tactics (synthetic noise)

Strategy documents follow OpenSearch schema with situation_tags that match
the Rust rag/mod.rs tag generation logic.

All documents are deterministic (fixed random seed 42) for reproducibility.
"""

from __future__ import annotations

import json
import random
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Literal


@dataclass
class StrategyDocument:
    """Strategy document matching OpenSearch schema."""

    doc_id: str
    situation_tags: list[str]
    decision: dict[str, str]
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


class DOE022DataGenerator:
    """Generate HIGH and LOW quality strategy documents."""

    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)
        self.today = date.today().isoformat()

        # DOE-020 findings: top performers
        self.top_strategy = "burst_3"
        self.top_mean_kills = 44.55
        self.top_experiment = "DOE-020"
        self.top_episodes = 30

        # Situation tags (from Rust rag/mod.rs logic)
        self.tag_health_low = "low_health"  # health < 30
        self.tag_health_full = "full_health"  # health >= 80
        self.tag_ammo_low = "low_ammo"  # ammo < 10
        self.tag_ammo_abundant = "ammo_abundant"  # ammo >= 50
        self.tag_multi_enemy = "multi_enemy"  # enemies_visible >= 3
        self.tag_single_enemy = "single_enemy"  # enemies_visible == 1

        # Tactic-to-action mapping (from Python comment in task description)
        # - "retreat*" or "kite*" → ACTION_MOVE_LEFT (0)
        # - "flank*" → ACTION_MOVE_RIGHT (1)
        # - Everything else (attack, burst, hold, charge, cover) → ACTION_ATTACK (2)

    def generate_high_quality_docs(self, count: int = 50) -> list[StrategyDocument]:
        """Generate HIGH quality documents based on DOE-020 findings.

        Distribution:
        - 15 docs: Engagement patterns (attack-focused tactics)
        - 15 docs: Positioning heuristics (flank/lateral tactics)
        - 10 docs: State-response rules (retreat/kite tactics)
        - 10 docs: Combined tactics (hold/cover/aggressive)
        """
        docs = []

        # 1. Engagement patterns (15 docs) - ATTACK dominant
        engagement_tactics = [
            "burst_fire_sweep",
            "attack_visible_enemy",
            "charge_and_fire",
            "sustained_burst",
            "aggressive_fire",
            "multi_target_sweep",
            "attack_closest_enemy",
            "fire_on_sight",
            "burst_attack_pattern",
            "rapid_fire_sweep",
            "target_priority_fire",
            "attack_high_threat",
            "burst_fire_pattern",
            "aggressive_engagement",
            "fire_control_burst",
        ]

        for i, tactic in enumerate(engagement_tactics):
            doc_id = f"strat_high_{i+1:03d}"
            tags = random.sample(
                [
                    self.tag_health_full,
                    self.tag_ammo_abundant,
                    self.tag_multi_enemy,
                    self.tag_single_enemy,
                ],
                k=random.randint(2, 3),
            )
            docs.append(
                StrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "tactic": tactic,
                        "weapon": "pistol",
                        "positioning": random.choice(
                            ["lateral_sweep", "hold_position", "advance"]
                        ),
                    },
                    quality={
                        "trust_score": round(random.uniform(0.75, 0.95), 2),
                        "source_strategy": self.top_strategy,
                        "source_experiment": self.top_experiment,
                        "source_episodes": self.top_episodes,
                        "mean_kills": round(
                            random.uniform(
                                self.top_mean_kills - 5, self.top_mean_kills + 5
                            ),
                            2,
                        ),
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        # 2. Positioning heuristics (15 docs) - Mix of flank (TURN_RIGHT) and attack-related
        positioning_tactics = [
            "flank_to_angle",
            "lateral_sweep_left",
            "lateral_reposition",
            "flank_right_side",
            "attack_from_flank",
            "lateral_sweep_right",
            "flank_and_fire",
            "sweep_left_attack",
            "repositioning_burst",
            "flank_maneuver",
            "lateral_attack_sweep",
            "attack_lateral_move",
            "flank_positioning",
            "sweep_attack_pattern",
            "attack_reposition",
        ]

        for i, tactic in enumerate(positioning_tactics):
            doc_id = f"strat_high_{i+16:03d}"
            tags = random.sample(
                [
                    self.tag_health_full,
                    self.tag_ammo_abundant,
                    self.tag_multi_enemy,
                ],
                k=2,
            )
            docs.append(
                StrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "tactic": tactic,
                        "weapon": "pistol",
                        "positioning": random.choice(
                            ["flank_right", "lateral_left", "sweep"]
                        ),
                    },
                    quality={
                        "trust_score": round(random.uniform(0.70, 0.90), 2),
                        "source_strategy": self.top_strategy,
                        "source_experiment": self.top_experiment,
                        "source_episodes": self.top_episodes,
                        "mean_kills": round(random.uniform(35.0, 50.0), 2),
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        # 3. State-response rules (10 docs) - RETREAT/KITE (TURN_LEFT)
        retreat_tactics = [
            "retreat_to_cover",
            "kite_backwards",
            "defensive_dodge",
            "retreat_and_reload",
            "kite_to_distance",
            "retreat_low_health",
            "kite_and_evade",
            "retreat_conserve_ammo",
            "kite_to_safety",
            "retreat_tactical",
        ]

        for i, tactic in enumerate(retreat_tactics):
            doc_id = f"strat_high_{i+31:03d}"
            # Low health or low ammo tags (state-response)
            tags = [
                random.choice([self.tag_health_low, self.tag_ammo_low])
            ] + random.sample(
                [self.tag_multi_enemy, self.tag_single_enemy],
                k=1,
            )
            docs.append(
                StrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "tactic": tactic,
                        "weapon": "pistol",
                        "positioning": random.choice(
                            ["retreat_backward", "evade", "kite"]
                        ),
                    },
                    quality={
                        "trust_score": round(random.uniform(0.65, 0.85), 2),
                        "source_strategy": "adaptive_kill",
                        "source_experiment": self.top_experiment,
                        "source_episodes": self.top_episodes,
                        "mean_kills": round(random.uniform(30.0, 45.0), 2),
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        # 4. Combined tactics (10 docs)
        combined_tactics = [
            "aggressive_push",
            "hold_and_fire",
            "cover_fire_burst",
            "attack_then_retreat",
            "burst_then_reposition",
            "hold_position_fire",
            "aggressive_hold",
            "cover_and_burst",
            "attack_advance_fire",
            "hold_sustained_fire",
        ]

        for i, tactic in enumerate(combined_tactics):
            doc_id = f"strat_high_{i+41:03d}"
            tags = random.sample(
                [
                    self.tag_health_full,
                    self.tag_ammo_abundant,
                    self.tag_multi_enemy,
                    self.tag_single_enemy,
                ],
                k=random.randint(2, 3),
            )
            docs.append(
                StrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "tactic": tactic,
                        "weapon": "pistol",
                        "positioning": random.choice(
                            ["hold", "advance", "cover"]
                        ),
                    },
                    quality={
                        "trust_score": round(random.uniform(0.80, 0.95), 2),
                        "source_strategy": self.top_strategy,
                        "source_experiment": self.top_experiment,
                        "source_episodes": self.top_episodes,
                        "mean_kills": round(random.uniform(40.0, 50.0), 2),
                    },
                    metadata={
                        "created": self.today,
                        "version": 1,
                        "retired": False,
                    },
                )
            )

        return docs

    def generate_low_quality_docs(self, count: int = 50) -> list[StrategyDocument]:
        """Generate LOW quality documents (mismatched/unhelpful tactics).

        These are intentionally BAD advice:
        - Mismatched tags (e.g., retreat when at full health)
        - Random tag combinations that don't match tactic
        - Low trust scores (0.30-0.45)
        - Poor performance metrics (3.0-8.0 kills)
        """
        docs = []

        # Intentionally bad tactics
        bad_tactics = [
            "aggressive_charge",
            "reckless_fire",
            "stand_still",
            "ignore_enemy",
            "waste_ammo",
            "panic_fire",
            "random_movement",
            "overcommit_attack",
            "needless_retreat",
            "confused_positioning",
            "aimless_wander",
            "excessive_caution",
            "poor_timing_attack",
            "misaligned_flank",
            "weak_burst",
            "ineffective_kite",
            "bad_angle_attack",
            "poor_cover_usage",
            "wrong_target_priority",
            "suboptimal_positioning",
        ]

        all_tags = [
            self.tag_health_low,
            self.tag_health_full,
            self.tag_ammo_low,
            self.tag_ammo_abundant,
            self.tag_multi_enemy,
            self.tag_single_enemy,
        ]

        for i in range(count):
            doc_id = f"strat_low_{i+1:03d}"

            # Random tag combinations (often mismatched)
            tags = random.sample(all_tags, k=random.randint(1, 3))

            # Pick a random bad tactic (cycle through, repeat if needed)
            tactic = bad_tactics[i % len(bad_tactics)]

            docs.append(
                StrategyDocument(
                    doc_id=doc_id,
                    situation_tags=tags,
                    decision={
                        "tactic": tactic,
                        "weapon": random.choice(["pistol", "fist"]),
                        "positioning": random.choice(
                            ["random", "confused", "misaligned"]
                        ),
                    },
                    quality={
                        "trust_score": round(random.uniform(0.30, 0.45), 2),
                        "source_strategy": "random_noise",
                        "source_experiment": "synthetic",
                        "source_episodes": 10,
                        "mean_kills": round(random.uniform(3.0, 8.0), 2),
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
        high_docs = self.generate_high_quality_docs(50)
        low_docs = self.generate_low_quality_docs(50)

        # Validate uniqueness
        all_doc_ids = [d.doc_id for d in high_docs + low_docs]
        assert len(all_doc_ids) == len(set(all_doc_ids)), "Duplicate doc_id found!"

        # Validate tags non-empty
        for doc in high_docs + low_docs:
            assert len(doc.situation_tags) > 0, f"{doc.doc_id} has empty tags!"

        # Validate trust_score range
        for doc in high_docs + low_docs:
            ts = doc.quality["trust_score"]
            assert 0.0 <= ts <= 1.0, f"{doc.doc_id} trust_score {ts} out of range!"

        # Save as JSON arrays
        with open(output_dir / "high_quality_docs.json", "w") as f:
            json.dump([d.to_dict() for d in high_docs], f, indent=2)

        with open(output_dir / "low_quality_docs.json", "w") as f:
            json.dump([d.to_dict() for d in low_docs], f, indent=2)

        # Save as NDJSON for OpenSearch bulk indexing
        with open(output_dir / "high_quality_docs.ndjson", "w") as f:
            for doc in high_docs:
                f.write(doc.to_opensearch_bulk_line("strategies_high") + "\n")

        with open(output_dir / "low_quality_docs.ndjson", "w") as f:
            for doc in low_docs:
                f.write(doc.to_opensearch_bulk_line("strategies_low") + "\n")

        print(f"Generated {len(high_docs)} HIGH quality documents")
        print(f"Generated {len(low_docs)} LOW quality documents")
        print(f"Saved to: {output_dir}")
        print("✓ All documents pass validation")


def main():
    """Entry point for script execution."""
    # Output to container-side path
    output_dir = Path("/app/data/doe-022-data")
    generator = DOE022DataGenerator(seed=42)
    generator.save_documents(output_dir)


if __name__ == "__main__":
    main()
