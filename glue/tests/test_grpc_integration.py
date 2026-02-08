"""Integration tests: gRPC pipeline with Rust agent-core.

Requires running services:
- agent-core gRPC server (default localhost:50052 on host)
- OpenSearch (for L2 kNN retrieval in full_agent mode)

Tests verify:
1. Decision level differentiation (L0/L2/random)
2. Cascade mode behavior (random, rule_only, full_agent)
3. Latency budget compliance (< 200ms P99)
4. Deterministic behavior for rule-based decisions
"""

from __future__ import annotations

import os
import time

import pytest

from glue.grpc_client import GrpcActionClient, check_grpc_health
from glue.vizdoom_bridge import GameState

SERVER_HOST = os.environ.get("GRPC_HOST", "localhost")
SERVER_PORT = int(os.environ.get("GRPC_PORT", "50052"))

pytestmark = pytest.mark.skipif(
    not check_grpc_health(SERVER_HOST, SERVER_PORT, timeout=3.0),
    reason="gRPC server not reachable",
)


class TestGrpcIntegration:
    """Integration tests requiring running agent-core + opensearch."""

    def test_random_mode_returns_level_255(self):
        """Random cascade_mode should return decision_level=255."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="random")
        try:
            state = GameState(health=100, ammo=50, enemies_visible=0)
            action = client(state)
            assert 0 <= action <= 2
            assert client.last_decision_level == 255
            assert client.last_confidence == 0.0
        finally:
            client.close()

    def test_rule_only_fires_l0(self):
        """rule_only with enemies_visible=0 should fire L0 reposition rule."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="rule_only")
        try:
            state = GameState(health=80, ammo=50, enemies_visible=0)
            action = client(state)
            assert client.last_decision_level == 0  # L0 rule fires
        finally:
            client.close()

    def test_rule_only_low_health_enemy_visible(self):
        """rule_only with enemies and low health fires emergency_retreat (MoveLeft)."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="rule_only")
        try:
            state = GameState(health=20, ammo=50, enemies_visible=2)
            action = client(state)
            assert action == 0  # MOVE_LEFT (emergency_retreat)
            assert client.last_decision_level == 0
            assert "emergency_retreat" in client.last_rule_matched
        finally:
            client.close()

    def test_rule_only_enemy_visible_healthy(self):
        """rule_only with enemies visible and healthy fires attack_visible_enemy."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="rule_only")
        try:
            state = GameState(health=80, ammo=50, enemies_visible=2)
            action = client(state)
            assert action == 2  # ATTACK (attack_visible_enemy)
            assert client.last_decision_level == 0
            assert "attack_visible_enemy" in client.last_rule_matched
        finally:
            client.close()

    def test_rule_only_no_enemies_low_ammo(self):
        """rule_only with no enemies and low ammo fires reposition_no_ammo (MoveRight)."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="rule_only")
        try:
            state = GameState(health=80, ammo=5, enemies_visible=0)
            action = client(state)
            assert action == 1  # MOVE_RIGHT (reposition_no_ammo)
            assert client.last_decision_level == 0
            assert "reposition_no_ammo" in client.last_rule_matched
        finally:
            client.close()

    def test_rule_only_no_enemies_has_ammo(self):
        """rule_only with no enemies and ammo fires reposition_no_enemies (MoveLeft)."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="rule_only")
        try:
            state = GameState(health=80, ammo=50, enemies_visible=0)
            action = client(state)
            assert action == 0  # MOVE_LEFT (reposition_no_enemies)
            assert client.last_decision_level == 0
            assert "reposition_no_enemies" in client.last_rule_matched
        finally:
            client.close()

    def test_full_agent_l0_priority(self):
        """full_agent should still fire L0 rules when they match."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="full_agent")
        try:
            state = GameState(health=20, ammo=50, enemies_visible=2)
            action = client(state)
            assert client.last_decision_level == 0  # L0 has priority
        finally:
            client.close()

    def test_full_agent_returns_valid_action(self):
        """full_agent should always return a valid action index."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="full_agent")
        try:
            state = GameState(health=90, ammo=5, enemies_visible=3)
            action = client(state)
            assert 0 <= action <= 2
        finally:
            client.close()

    def test_latency_budget(self):
        """Decision latency P99 should be within 200ms budget."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="full_agent")
        try:
            state = GameState(health=50, ammo=30, enemies_visible=2)

            latencies = []
            for _ in range(10):
                t0 = time.perf_counter_ns()
                client(state)
                t1 = time.perf_counter_ns()
                latencies.append((t1 - t0) / 1e6)

            p99 = sorted(latencies)[min(9, len(latencies) - 1)]
            assert p99 < 200, f"P99 latency {p99:.1f}ms exceeds 200ms budget"
        finally:
            client.close()

    def test_different_cascade_modes_produce_different_behavior(self):
        """random vs rule_only should produce different decision_levels."""
        random_client = GrpcActionClient(
            SERVER_HOST, SERVER_PORT, cascade_mode="random"
        )
        rule_client = GrpcActionClient(
            SERVER_HOST, SERVER_PORT, cascade_mode="rule_only"
        )
        try:
            state = GameState(health=80, ammo=50, enemies_visible=0)

            random_client(state)
            rule_client(state)

            assert random_client.last_decision_level == 255  # random
            assert rule_client.last_decision_level == 0  # L0 rule
        finally:
            random_client.close()
            rule_client.close()

    def test_deterministic_with_same_state(self):
        """Same cascade_mode + same state should produce consistent results."""
        client = GrpcActionClient(SERVER_HOST, SERVER_PORT, cascade_mode="rule_only")
        try:
            state = GameState(health=50, ammo=30, enemies_visible=0)

            results = [client(state) for _ in range(5)]
            assert len(set(results)) == 1, "Same state should give same action"
        finally:
            client.close()
