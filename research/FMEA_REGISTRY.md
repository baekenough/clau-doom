# FMEA Registry

> **Last Updated**: 2026-02-07
> **Author**: research-evolution-mgr
> **Status**: Pre-Experiment (Trial 4 FMEA Analysis Incorporated)

## Risk Priority Number (RPN) Scale

```
RPN = Severity (S) × Occurrence (O) × Detection (D)

Severity (S):    1-10 (10 = catastrophic impact)
Occurrence (O):  1-10 (10 = certain to occur)
Detection (D):   1-10 (10 = undetectable)

Maximum RPN: 1000
Target: All active failure modes < 100 RPN
```

## Numbering Convention

Failure modes use category prefixes to avoid overlap with Round 1 infrastructure FMEA (FM-01 through FM-14):
- **FM-G##**: Gameplay failure modes (agent behavior, in-game issues)
- **FM-I##**: Infrastructure failure modes (containers, data pipeline)

## Active Failure Modes

### FM-G01: Agent Dies Immediately Without Any Action [CRITICAL]
- **ID**: FM-G01
- **Failure Mode**: Agent spawns and dies within 1-2 ticks without taking any meaningful action
- **Cause**: Extreme parameter combinations (e.g., memory=0, strength=0, health_caution=1.0) result in decision paralysis or immediate retreat without engagement
- **Effect**: Zero kills, zero damage dealt, wasted experimental run, no data utility
- **Severity**: 9 (Run produces no usable data)
- **Occurrence**: 3 (Rare but possible in evolutionary search space extremes)
- **Detection**: 2 (Easily detected: survival_time < 10 ticks in post-run analysis)
- **RPN**: **54**
- **Recommended Actions**:
  1. Add pre-run parameter validation (sanity bounds: memory >= 0.1, strength >= 0.1)
  2. Implement "stuck detection" in doom-env-mgr: if agent does not move for 5 consecutive ticks, log warning
  3. Add episode timeout (max 10000 ticks): if agent alive but no movement for 20 ticks, force episode end
- **Status**: Open (mitigation planned in doom-env-mgr, doom-agent-tester)
- **Date Added**: 2026-02-07 (from Trial 4 FMEA)

---

### FM-G02: Agent Gets Stuck in Corner/Loop [HIGH]
- **ID**: FM-G02
- **Failure Mode**: Agent enters repetitive movement loop (e.g., alternating TURN_LEFT/TURN_RIGHT) or gets stuck against a wall
- **Cause**: Low exploration_priority combined with high retreat_threshold leads to excessive retreat behavior without strategic repositioning
- **Effect**: Zero kills after initial phase, reduced survival (eventually overrun), low map coverage
- **Severity**: 7 (Run completes but produces near-zero utility)
- **Occurrence**: 5 (Moderately frequent in conservative parameter combinations)
- **Detection**: 5 (Requires pattern analysis: action sequence or position logs)
- **RPN**: **175**
- **Recommended Actions**:
  1. Add positional diversity metric to DuckDB episode logs (track unique grid cells visited)
  2. Implement action sequence entropy monitoring: if last 10 actions repeat pattern, inject random exploration
  3. Add "unstuck" logic in MD rules (Level 0): if position unchanged for 15 ticks, force MOVE_FORWARD + random turn
  4. Penalize low map coverage in TOPSIS multi-criteria scoring
- **Status**: Open (highest priority for mitigation)
- **Date Added**: 2026-02-07 (from Trial 4 FMEA)

---

### FM-G03: Ammo Depleted Early, Agent Becomes Ineffective [MODERATE]
- **ID**: FM-G03
- **Failure Mode**: Agent exhausts primary weapon ammo within first 30% of episode duration
- **Cause**: Low ammo_conservation setting combined with high aggression_level leads to wasteful shooting (firing at missed targets, firing at long range with low accuracy)
- **Effect**: Agent forced to use fists only, kill_rate drops to near-zero after ammo depletion, cannot engage enemies effectively in second half
- **Severity**: 5 (Partial run utility: first half useful, second half wasted)
- **Occurrence**: 7 (Common in aggressive parameter ranges)
- **Detection**: 5 (Requires metric tracking: ammo_remaining over time)
- **RPN**: **175**
- **Recommended Actions**:
  1. Add ammo checkpoint logic in strategy documents: if ammo < 20% remaining, switch to defensive mode (retreat priority higher)
  2. Implement ammo efficiency metric: kills per ammo consumed, track in DuckDB
  3. Add weapon switching logic: if primary ammo depleted, prioritize item pickup (search for ammo boxes)
  4. Penalize low ammo efficiency in TOPSIS scoring
- **Status**: Open (medium priority, can be addressed in strategy document refinement)
- **Date Added**: 2026-02-07 (from Trial 4 FMEA)

---

### FM-I01: Container Crash During Experiment Run [MODERATE]
- **ID**: FM-I01
- **Failure Mode**: Docker container (doom-env, doom-agent-A, doom-agent-B, etc.) crashes mid-episode or mid-run
- **Cause**: Resource exhaustion (memory leak in VizDoom Python binding, OOM in Xvfb), segfault in game engine, Docker daemon instability
- **Effect**: Partial data loss for affected run, experiment blocked until manual restart, reduced trust in results if crash pattern correlates with specific factor levels
- **Severity**: 6 (Data loss, but run can be re-executed with same seed)
- **Occurrence**: 4 (Occasional, especially during long multi-run experiments)
- **Detection**: 3 (Automated: Docker health check + doom-env-mgr monitoring)
- **RPN**: **72**
- **Recommended Actions**:
  1. Implement automatic container restart in doom-env-mgr: if health check fails, restart and resume from last checkpoint
  2. Log all crashes to research/logs/container_crashes.log with timestamp, agent ID, episode count
  3. Add pre-run memory check: if available memory < 2GB, delay run and alert
  4. Periodic container restart policy: restart doom-env every 100 episodes to prevent memory leak accumulation
- **Status**: Open (infrastructure hardening task for doom-env-mgr)
- **Date Added**: 2026-02-07 (from Trial 4 FMEA)

---

### FM-I02: Data Not Written to DuckDB (Silent Failure) [MODERATE]
- **ID**: FM-I02
- **Failure Mode**: Episode completes successfully but metrics are not recorded to DuckDB (database connection lost, write permission issue, schema mismatch)
- **Cause**: DuckDB connection timeout, concurrent write conflict, schema evolution without migration, file system permissions change
- **Effect**: Analysis cannot proceed (missing data), experiment must be re-run, potential bias if failure correlates with specific conditions
- **Severity**: 7 (Complete data loss for affected episode)
- **Occurrence**: 3 (Rare, but catastrophic when occurs)
- **Detection**: 7 (Difficult to detect without post-run validation: expected row count vs actual)
- **RPN**: **147**
- **Recommended Actions**:
  1. Add post-episode data validation in research-doe-runner: after each episode, verify row exists in DuckDB with correct run_id + episode_id
  2. Implement write-ahead logging: buffer metrics in memory, flush to DuckDB with retry logic (max 3 attempts)
  3. Add schema version check: before writing, verify DuckDB table schema matches expected schema (fail fast if mismatch)
  4. Generate data quality report after each DOE run: expected episodes vs actual rows, flag missing data
- **Status**: Open (data integrity task for research-doe-runner + doom-metrics-collector)
- **Date Added**: 2026-02-07 (from Trial 4 FMEA)

---

## RPN Priority Queue

| Rank | FM-ID | Failure Mode | RPN | Status |
|------|-------|--------------|-----|--------|
| 1 | FM-G02 | Agent stuck in corner/loop | 175 | Open |
| 2 | FM-G03 | Ammo depleted early | 175 | Open |
| 3 | FM-I02 | Data not written to DuckDB | 147 | Open |
| 4 | FM-I01 | Container crash during run | 72 | Open |
| 5 | FM-G01 | Agent dies immediately | 54 | Open |

## RPN Trend Tracking

| Date | FM-ID | Old RPN | New RPN | Action Taken |
|------|-------|---------|---------|--------------|
| — | — | — | — | No mitigations implemented yet |

## Mitigation Plan

### Immediate (Before Wave 1 Execution)
1. **FM-G01**: Add parameter sanity bounds validation (memory >= 0.1, strength >= 0.1)
2. **FM-I01**: Implement Docker health check + auto-restart in doom-env-mgr
3. **FM-I02**: Add post-episode data validation in research-doe-runner

### Short-term (During Wave 1 Execution)
1. **FM-G02**: Add action sequence entropy monitoring + unstuck logic
2. **FM-G03**: Add ammo checkpoint logic in strategy documents

### Long-term (After Wave 1 Results)
1. **FM-G02**: Penalize low map coverage in TOPSIS scoring
2. **FM-G03**: Implement weapon switching logic, ammo efficiency metric
3. **FM-I01**: Periodic container restart policy
4. **FM-I02**: Schema version check + write-ahead logging

## Update Schedule

- **Before Each Wave**: Review RPN queue, update occurrence estimates based on previous wave data
- **After Each DOE**: Log any new failure modes discovered, re-compute RPN with updated occurrence rates
- **After Mitigation**: Re-assess RPN (new RPN = S × reduced O × reduced D), track improvement

## Integration with SPC

When SPC chart detects out-of-control signal:
1. Investigate if signal correlates with known failure mode
2. If yes: update occurrence (O) estimate in FMEA
3. If no: add new failure mode to registry
4. Re-prioritize RPN queue

## Notes

- Severity scale (S) is domain-specific: 9-10 = experiment invalid, 5-8 = partial data loss, 1-4 = minor quality degradation
- Detection scale (D) reflects automation level: 1-3 = automated detection, 4-7 = manual analysis required, 8-10 = undetectable until paper review
- Target: All active RPN < 100 by end of Phase 0
- FMEA is a living document: update after every wave execution
