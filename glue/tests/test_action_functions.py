"""Tests for action selection functions."""

import pytest

from glue.vizdoom_bridge import (
    ACTION_ATTACK,
    ACTION_MOVE_LEFT,
    ACTION_MOVE_RIGHT,
    GameState,
)
from glue.action_functions import FullAgentAction, random_action, rule_only_action


def make_state(
    health: int = 100,
    ammo: int = 50,
    kills: int = 0,
    tick: int = 0,
) -> GameState:
    return GameState(
        health=health,
        ammo=ammo,
        kills=kills,
        enemies_visible=0,
        position_x=0.0,
        position_y=0.0,
        position_z=0.0,
        angle=0.0,
        episode_time=0.0,
        is_dead=False,
        tick=tick,
    )


class TestRandomAction:
    def test_valid_range(self):
        state = make_state()
        for _ in range(100):
            action = random_action(state)
            assert action in (0, 1, 2)


class TestRuleOnlyAction:
    def test_emergency_dodge(self):
        state = make_state(health=10, ammo=50)
        assert rule_only_action(state) == ACTION_MOVE_LEFT

    def test_no_ammo(self):
        state = make_state(health=100, ammo=0)
        assert rule_only_action(state) == ACTION_MOVE_LEFT

    def test_default_attack(self):
        state = make_state(health=100, ammo=50)
        assert rule_only_action(state) == ACTION_ATTACK


class TestFullAgentAction:
    def test_callable(self):
        agent = FullAgentAction()
        action = agent(make_state())
        assert action in (ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT, ACTION_ATTACK)

    def test_reset_clears_state(self):
        agent = FullAgentAction()
        # Accumulate some internal state
        for i in range(5):
            agent(make_state(health=100 - i * 10, tick=i))
        agent.reset()
        assert len(agent._health_history) == 0
        assert agent._tick_counter == 0

    def test_high_memory_dodges_more(self):
        agent_high = FullAgentAction(memory_weight=0.9, strength_weight=0.5)
        agent_low = FullAgentAction(memory_weight=0.1, strength_weight=0.5)

        # Moderate health loss: 1 HP per tick
        # memory_weight=0.9 threshold: -2.0 * (1-0.9+0.1) = -0.4, triggers at -1
        # memory_weight=0.1 threshold: -2.0 * (1-0.1+0.1) = -2.0, -1 > -2.0 so no trigger
        dodge_count_high = 0
        dodge_count_low = 0
        for t in range(30):
            health = max(50, 100 - t)  # lose 1 HP/tick, floor at 50
            state = make_state(health=health, ammo=50, tick=t)
            a_high = agent_high(state)
            a_low = agent_low(state)
            if a_high in (ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT):
                dodge_count_high += 1
            if a_low in (ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT):
                dodge_count_low += 1

        assert dodge_count_high > dodge_count_low

    def test_high_strength_attacks_more(self):
        agent_strong = FullAgentAction(memory_weight=0.0, strength_weight=0.9)
        agent_weak = FullAgentAction(memory_weight=0.0, strength_weight=0.1)

        attack_count_strong = 0
        attack_count_weak = 0
        for t in range(30):
            state = make_state(health=100, ammo=50, tick=t)
            if agent_strong(state) == ACTION_ATTACK:
                attack_count_strong += 1
            if agent_weak(state) == ACTION_ATTACK:
                attack_count_weak += 1

        assert attack_count_strong > attack_count_weak

    def test_emergency_rules_override(self):
        agent = FullAgentAction(memory_weight=0.0, strength_weight=1.0)
        state = make_state(health=10, ammo=50)
        assert agent(state) == ACTION_MOVE_LEFT

    def test_no_ammo_dodges(self):
        agent = FullAgentAction()
        state = make_state(health=100, ammo=0)
        assert agent(state) == ACTION_MOVE_LEFT
