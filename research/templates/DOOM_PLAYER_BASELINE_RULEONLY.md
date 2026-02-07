# DOOM Player: Rule-Only Baseline

## Decision Mode
rule_only

## Parameters
- health_threshold: 0.3
- attack_priority: nearest_enemy
- retreat_distance: 100

## Decision Hierarchy
- L0 (MD Rules): ENABLED
- L1 (DuckDB Cache): DISABLED
- L2 (OpenSearch RAG): DISABLED

## Purpose
Rule-only baseline for DOE-001. Uses hardcoded MD rules (Level 0) without learning. This represents a static, manually designed decision policy. The delta between Full Agent (L0+L1+L2) and Rule-Only (L0 only) quantifies the value added by RAG experience accumulation (Levels 1 and 2).

## Decision Rules (Level 0)

### Emergency Rules (Highest Priority)
```
if health < health_threshold:
  → retreat_to_safe_distance(retreat_distance)

if ammo_primary == 0 and ammo_secondary > 0:
  → switch_weapon()

if ammo_all == 0:
  → search_for_ammo()
```

### Combat Rules
```
if enemy_visible and distance < 200:
  → attack(target = nearest_enemy)

if enemy_visible and distance >= 200:
  → move_closer()

if not enemy_visible:
  → patrol_forward()
```

### Item Pickup Rules
```
if health < 0.5 and health_pack_visible:
  → move_to_item(health_pack)

if ammo < 50 and ammo_box_visible:
  → move_to_item(ammo_box)
```

## Expected Metrics
- kill_rate: ~0.30 (structured combat, but no adaptation)
- survival_time: ~2000 ticks (basic self-preservation)
- damage_dealt: ~400 (focused attacks)
- ammo_efficiency: ~0.15 kills/ammo (moderate conservation)
- map_coverage: ~30% (basic exploration)

## Comparison Value
This baseline represents the capability of hand-crafted rules without learning. If Full Agent (with RAG) does not significantly outperform this, then DuckDB cache (L1) and OpenSearch kNN (L2) are not adding value, and the research direction must be reconsidered.

## Key Limitation
No adaptation: agent always uses the same rules regardless of experience. Cannot learn from mistakes, cannot discover new strategies, cannot improve over time. This is exactly what RAG (Levels 1 and 2) should address.
