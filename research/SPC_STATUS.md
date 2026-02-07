# SPC Status

> **Last Updated**: 2026-02-07
> **Author**: research-analyst
> **Status**: Pre-Experiment (No Data)

## Control Charts

### Kill Rate (X-bar, R)
- **Status**: NOT STARTED
- **UCL/LCL**: TBD (established after DOE-001)
- **Purpose**: Monitor agent generation kill efficiency over time
- **Subgroup Size**: n = number of agents per generation (planned: 8)
- **Target**: Detect out-of-control signals (special cause variation)

### Survival Time (X-bar, R)
- **Status**: NOT STARTED
- **UCL/LCL**: TBD (established after DOE-001)
- **Purpose**: Monitor agent generation survival duration
- **Subgroup Size**: n = number of agents per generation (planned: 8)
- **Target**: Detect trends or shifts in survival capability

### Damage Dealt (Cpk)
- **Status**: NOT STARTED
- **Cpk Target**: >= 1.33 (capable process)
- **Purpose**: Process capability for damage output
- **Specification**: LSL = TBD (minimum acceptable damage), USL = none (higher is better)
- **Note**: One-sided capability index (no upper limit on damage)

## Out-of-Control Signals

| Signal ID | Date | Chart | Rule Violated | Action Taken |
|-----------|------|-------|---------------|--------------|
| — | — | — | — | No data yet |

### Western Electric Rules
- **Rule 1**: One point beyond 3σ
- **Rule 2**: 2 of 3 consecutive points in Zone A or beyond (same side)
- **Rule 3**: 4 of 5 consecutive points in Zone B or beyond (same side)
- **Rule 4**: 8 consecutive points on same side of center line
- **Rule 5**: 6 consecutive points steadily increasing or decreasing
- **Rule 6**: 14 consecutive points alternating up and down
- **Rule 7**: 15 consecutive points within Zone C (stratification)
- **Rule 8**: 8 consecutive points beyond Zone C on both sides (mixture)

## Process Capability

| Metric | Cp | Cpk | Pp | Ppk | Interpretation |
|--------|----|----|----|----|----------------|
| Kill Rate | — | — | — | — | No data yet |
| Survival Time | — | — | — | — | No data yet |
| Damage Dealt | — | — | — | — | No data yet |

**Process Capability Formula**:

```
Cpk = min((USL - X_bar) / (3 * sigma_within), (X_bar - LSL) / (3 * sigma_within))
```

Where:
- USL = Upper Specification Limit
- LSL = Lower Specification Limit
- X_bar = Process mean
- sigma_within = Within-subgroup standard deviation (estimated from R-bar / d2)

For one-sided specifications (e.g., Damage Dealt with no USL): Cpk = (X_bar - LSL) / (3 * sigma_within)

**Capability Benchmarks**:
- Cpk < 1.0: Not capable
- Cpk 1.0-1.33: Marginally capable
- Cpk 1.33-1.67: Capable
- Cpk > 1.67: Highly capable

## Chart Initialization

After first experiment execution (DOE-001):
1. Compute baseline statistics (X-bar-bar, R-bar, sigma)
2. Establish control limits (UCL/LCL) using A2, D3, D4 constants
3. Plot first generation data
4. Monitor subsequent generations for out-of-control signals

After 20+ generations:
- Re-compute control limits if process has fundamentally changed
- Separate phases by experimental conditions (e.g., Phase 0, Phase 1, Phase 2)
- Use rational subgrouping (same generation = subgroup)

## FMEA Integration

When out-of-control signal detected:
1. Investigate root cause
2. Update FMEA_REGISTRY.md with failure mode (if new)
3. Compute RPN (Severity x Occurrence x Detection)
4. Prioritize corrective actions by RPN

## Update Schedule

- **During Evolution**: After each generation execution
- **After Experiments**: When new DOE data available
- **Manual Review**: Every 10 generations or phase transition

## Notes

- Control charts track generation-level aggregates, not individual episodes
- Each generation produces one subgroup (n = population size)
- Use rational subgrouping: generation ID as subgroup identifier
- If multi-objective optimization active, track separate charts for each objective
- Center point replicates from DOE provide pure error estimates for capability analysis
