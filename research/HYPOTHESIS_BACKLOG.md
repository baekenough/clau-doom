# Hypothesis Backlog

## Active Hypotheses

### H-001: RAG System Outperforms Baselines [HIGH PRIORITY]
**Statement**: Full RAG agent (L0+L1+L2) achieves significantly higher kill_rate than random and rule-only baselines in defend_the_center.
**Rationale**: Core validation of the RAG-based decision system. If this fails, the entire approach needs rethinking.
**Status**: TENTATIVE (DOE-001 complete, 2026-02-08, LOW trust)
**Date Added**: 2026-02-07

### H-002: Rule Engine Provides Meaningful Structure [MEDIUM PRIORITY]
**Statement**: Rule-only baseline significantly outperforms random baseline.
**Rationale**: Validates that L0 rules provide value before adding complexity.
**Status**: Tested within DOE-001 (Rule-Only vs Random comparison)
**Date Added**: 2026-02-07

### H-003: Decision Latency Within Bounds [HIGH PRIORITY]
**Statement**: Full cascade decision latency P99 < 100ms.
**Rationale**: Real-time gameplay requires fast decisions.
**Status**: Tracked in DOE-001 (decision_latency_p99 metric)
**Date Added**: 2026-02-07

## Queued Hypotheses

### H-004: Memory Weight Optimization [MEDIUM PRIORITY]
**Statement**: Optimal memory_weight exists between 0.5-0.9 for maximizing kill_rate.
**Rationale**: After baseline validation, optimize agent parameters.
**Status**: Queued (Phase 1, after DOE-001)
**Date Added**: 2026-02-07

### H-005: Strategy Document Quality Matters [MEDIUM PRIORITY]
**Statement**: Higher quality strategy documents (higher confidence_tier) lead to better agent performance.
**Rationale**: Validates the RAG curation pipeline importance.
**Status**: Queued (Phase 1)
**Date Added**: 2026-02-07

## Completed Hypotheses

(None yet)

## Rejected Hypotheses

(None yet)
