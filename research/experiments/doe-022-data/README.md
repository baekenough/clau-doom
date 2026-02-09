# DOE-022 Phase A: Strategy Document Generation

**Generated**: 2026-02-09
**Script**: `/Users/sangyi/workspace/research/clau-doom/glue/doe022_gen_docs.py`
**Random Seed**: 42 (deterministic, reproducible)

## Overview

Generated 100 strategy documents for L2 RAG testing:
- **50 HIGH quality documents**: Based on DOE-020 top performers (burst_3, adaptive_kill)
- **50 LOW quality documents**: Mismatched/unhelpful tactics (synthetic noise)

## Files

| File | Format | Purpose |
|------|--------|---------|
| `high_quality_docs.json` | JSON array | HIGH quality documents for analysis |
| `low_quality_docs.json` | JSON array | LOW quality documents for analysis |
| `high_quality_docs.ndjson` | NDJSON | OpenSearch bulk index format (strategies_high) |
| `low_quality_docs.ndjson` | NDJSON | OpenSearch bulk index format (strategies_low) |

## Document Schema

```json
{
  "doc_id": "strat_high_001",
  "situation_tags": ["full_health", "multi_enemy"],
  "decision": {
    "tactic": "burst_fire_sweep",
    "weapon": "pistol",
    "positioning": "hold_position"
  },
  "quality": {
    "trust_score": 0.80,
    "source_strategy": "burst_3",
    "source_experiment": "DOE-020",
    "source_episodes": 30,
    "mean_kills": 40.95
  },
  "metadata": {
    "created": "2026-02-09",
    "version": 1,
    "retired": false
  }
}
```

## HIGH Quality Document Distribution

| Category | Count | Tactics | Action Mapping |
|----------|-------|---------|----------------|
| Engagement patterns | 15 | burst_fire_sweep, attack_visible_enemy, charge_and_fire, ... | → ATTACK (2) |
| Positioning heuristics | 15 | flank_to_angle, lateral_sweep_left, flank_and_fire, ... | → TURN_RIGHT (1) / ATTACK (2) |
| State-response rules | 10 | retreat_to_cover, kite_backwards, retreat_and_reload, ... | → TURN_LEFT (0) |
| Combined tactics | 10 | aggressive_push, hold_and_fire, cover_fire_burst, ... | → ATTACK (2) |

## Situation Tags (from Rust rag/mod.rs)

| Tag | Condition | Example Use |
|-----|-----------|-------------|
| `low_health` | health < 30 | Retreat/kite tactics |
| `full_health` | health >= 80 | Aggressive/attack tactics |
| `low_ammo` | ammo < 10 | Conserve ammo/retreat |
| `ammo_abundant` | ammo >= 50 | Burst fire/sustained attack |
| `multi_enemy` | enemies_visible >= 3 | Sweep/area tactics |
| `single_enemy` | enemies_visible == 1 | Focused attack |

## Tactic-to-Action Mapping

| Tactic Pattern | Action | Index |
|----------------|--------|-------|
| `retreat*`, `kite*` | TURN_LEFT | 0 |
| `flank*` | TURN_RIGHT | 1 |
| `attack*`, `burst*`, `fire*`, `hold*`, `charge*`, `cover*` | ATTACK | 2 |

## Validation Results

```
✓ HIGH quality documents: 50
✓ LOW quality documents: 50
✓ Total unique doc_ids: 100
✓ Documents with empty tags: 0
✓ Invalid trust scores: 0
✓ HIGH trust_score range: 0.66 - 0.95
✓ HIGH mean_kills average: 42.32
✓ LOW trust_score range: 0.30 - 0.45
✓ LOW mean_kills average: 5.87
✓ HIGH docs with retreat/kite tactics: 10
✓ HIGH docs with flank tactics: 6
✓ HIGH docs with attack/burst/fire tactics: 29
```

## Usage

### Load documents in Python

```python
import json

high_docs = json.load(open("high_quality_docs.json"))
low_docs = json.load(open("low_quality_docs.json"))

print(f"Total: {len(high_docs) + len(low_docs)} documents")
```

### Bulk index to OpenSearch

```bash
# Index HIGH quality documents
curl -X POST "localhost:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @high_quality_docs.ndjson

# Index LOW quality documents
curl -X POST "localhost:9200/_bulk" \
  -H "Content-Type: application/x-ndjson" \
  --data-binary @low_quality_docs.ndjson
```

### Query by tags

```bash
# Find strategies for low health + multi enemy
curl -X GET "localhost:9200/strategies_high/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "bool": {
        "must": [
          {"term": {"situation_tags": "low_health"}},
          {"term": {"situation_tags": "multi_enemy"}}
        ]
      }
    }
  }'
```

## Source Strategy Performance (DOE-020)

| Strategy | Mean Kills | Survival Time | Trust Score |
|----------|-----------|---------------|-------------|
| burst_3 | 44.55 | High | 0.75-0.95 |
| adaptive_kill | ~40 | Medium | 0.70-0.90 |
| random_noise (LOW) | 3-8 | Low | 0.30-0.45 |

## Next Steps (DOE-022 Phase B)

1. Index documents to OpenSearch (strategies_high, strategies_low)
2. Configure Rust rag/mod.rs to query these indices
3. Run L2 experiments with HIGH vs LOW quality RAG retrieval
4. Measure decision_level distribution and kill_rate by RAG quality
5. ANOVA: kill_rate ~ RAG_quality (HIGH vs LOW)

## Reproducibility

All documents generated with fixed seed 42. Re-running the script produces identical output:

```bash
docker exec clau-doom-player python3 -m glue.doe022_gen_docs
```
