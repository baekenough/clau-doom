# Agent MD Templates

This directory contains template agent MD files for experimental conditions. The research-doe-runner agent injects factor values into these templates via MD variable substitution to create experiment-specific agent configurations.

## Template Files

### DOOM_PLAYER_BASELINE_RANDOM.md
- **Purpose**: Random action baseline (floor comparison)
- **Decision Levels**: All disabled (L0=OFF, L1=OFF, L2=OFF)
- **Usage**: DOE-001 Condition 1
- **Expected Performance**: Very low (kill_rate ~0.05, survival ~500 ticks)

### DOOM_PLAYER_BASELINE_RULEONLY.md
- **Purpose**: Rule-only baseline (no RAG)
- **Decision Levels**: L0 only (MD rules enabled, cache and RAG disabled)
- **Usage**: DOE-001 Condition 2
- **Expected Performance**: Moderate (kill_rate ~0.30, survival ~2000 ticks)

### DOOM_PLAYER_GEN1.md
- **Purpose**: Full RAG agent (all levels active)
- **Decision Levels**: L0+L1+L2 (all enabled)
- **Usage**: DOE-001 Condition 3, DOE-002, DOE-005
- **Injected Variables**: ${MEMORY_WEIGHT}, ${STRENGTH_WEIGHT}
- **Expected Performance**: Best (kill_rate ~0.50+, survival ~3500+ ticks)

### DOOM_PLAYER_DOE003.md
- **Purpose**: Layer ablation (each level independently controlled)
- **Decision Levels**: Configurable (${L0_ENABLED}, ${L1_ENABLED}, ${L2_ENABLED})
- **Usage**: DOE-003 (2^3 factorial, 8 conditions)
- **Injected Variables**: ${L0_ENABLED}, ${L1_ENABLED}, ${L2_ENABLED}
- **Expected Performance**: Varies by condition (Full Stack best, All OFF worst)

## Variable Injection Process

1. research-doe-runner reads EXPERIMENT_ORDER_{ID}.md
2. For each experimental run:
   - Select appropriate template
   - Substitute ${VARIABLE} placeholders with factor values
   - Write instantiated agent MD to doom-agent-{ID}/AGENT.md
   - Restart Docker container to load new configuration
3. Execute episodes with fixed seed set
4. Record metrics to DuckDB

## Template Syntax

Variables use `${VARIABLE_NAME}` syntax:
```
memory_weight: ${MEMORY_WEIGHT}
```

Boolean flags use `true`/`false`:
```
L0 (MD Rules): ${L0_ENABLED}  # injected as "true" or "false"
```

## Usage in Experiment Orders

Example from EXPERIMENT_ORDER_002.md:
```yaml
template: research/templates/DOOM_PLAYER_GEN1.md
variable_mappings:
  - run: 1
    factors:
      MEMORY_WEIGHT: 0.3
      STRENGTH_WEIGHT: 0.3
  - run: 2
    factors:
      MEMORY_WEIGHT: 0.3
      STRENGTH_WEIGHT: 0.7
```

Example from EXPERIMENT_ORDER_003.md:
```yaml
template: research/templates/DOOM_PLAYER_DOE003.md
variable_mappings:
  - run: 1  # Full Stack
    factors:
      L0_ENABLED: true
      L1_ENABLED: true
      L2_ENABLED: true
  - run: 8  # All OFF (floor)
    factors:
      L0_ENABLED: false
      L1_ENABLED: false
      L2_ENABLED: false
```

## Notes

- All templates are in English (per R000 Language Policy)
- Templates are read-only reference files (never modified during experiments)
- Instantiated agent configurations are written to agent-specific directories (doom-agent-A/, doom-agent-B/, etc.)
- Same template can be used for multiple experiments with different variable values
- Template design supports reproducibility: same template + same variables + same seeds = identical agent behavior
