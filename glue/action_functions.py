"""Action selection functions for VizDoom defend_the_center scenario.

Provides three action strategies:
1. random_action -- uniform random choice
2. rule_only_action -- L0 hardcoded reflex rules (from Rust agent-core)
3. FullAgentAction -- callable class with memory/strength heuristics
"""

from __future__ import annotations

import random
from collections import deque

from glue.vizdoom_bridge import (
    ACTION_ATTACK,
    ACTION_MOVE_LEFT,
    ACTION_MOVE_RIGHT,
    GameState,
)


def random_action(state: GameState) -> int:
    """Uniform random action selection."""
    return random.randint(0, 2)


def rule_only_action(state: GameState) -> int:
    """L0 rule-based action, faithful translation of Rust agent-core rules.

    Priority-ordered evaluation:
      1. (priority 100) health < 30 -> dodge left (emergency retreat)
      2. (priority 10)  ammo == 0   -> dodge left (reposition, no ammo)
      3. (priority 50)  default     -> attack (enemies always approaching)

    Note: enemies_visible is always 0 in defend_the_center because the
    game variable is unavailable.  Enemies are always present and
    approaching, so ATTACK is the sensible default action.
    """
    if state.health < 30:
        return ACTION_MOVE_LEFT
    if state.ammo == 0:
        return ACTION_MOVE_LEFT
    return ACTION_ATTACK


class FullAgentAction:
    """Full agent action with memory and strength heuristics.

    Implements ``ActionFn`` protocol via ``__call__``.

    Args:
        memory_weight: Sensitivity to recent damage (0.0-1.0).
            Higher = more dodging when taking damage.
        strength_weight: Aggressiveness of attack bursts (0.0-1.0).
            Higher = longer attack bursts before dodge break.
    """

    def __init__(
        self,
        memory_weight: float = 0.5,
        strength_weight: float = 0.5,
    ) -> None:
        self.memory_weight = memory_weight
        self.strength_weight = strength_weight

        # Internal state -- cleared by reset()
        self._health_history: deque[int] = deque(maxlen=10)
        self._tick_counter: int = 0
        self._dodge_direction: int = ACTION_MOVE_LEFT

    def reset(self) -> None:
        """Clear internal state between episodes."""
        self._health_history.clear()
        self._tick_counter = 0
        self._dodge_direction = ACTION_MOVE_LEFT

    def __call__(self, state: GameState) -> int:
        # Record health for memory heuristic
        self._health_history.append(state.health)
        self._tick_counter += 1

        # --- L0 emergency rules (highest priority) ---
        if state.health < 30:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT

        # --- Memory heuristic: detect rapid health loss ---
        if self._should_dodge_memory():
            action = self._dodge_direction
            # Alternate dodge direction each time
            self._dodge_direction = (
                ACTION_MOVE_RIGHT
                if self._dodge_direction == ACTION_MOVE_LEFT
                else ACTION_MOVE_LEFT
            )
            return action

        # --- Strategy heuristic: burst attack with dodge breaks ---
        return self._strategy_action()

    def _should_dodge_memory(self) -> bool:
        """Check if recent health trend warrants dodging.

        Higher memory_weight = more sensitive = dodges on smaller health drops.
        Threshold: -2.0 * (1.0 - memory_weight + 0.1)
          memory_weight=0.9 → threshold = -0.4 (very sensitive)
          memory_weight=0.5 → threshold = -1.2
          memory_weight=0.1 → threshold = -2.0 (less sensitive)
        """
        if len(self._health_history) < 2:
            return False
        history = list(self._health_history)
        deltas = [history[i + 1] - history[i] for i in range(len(history) - 1)]
        avg_delta = sum(deltas) / len(deltas)
        threshold = -2.0 * (1.0 - self.memory_weight + 0.1)
        return avg_delta < threshold

    def _strategy_action(self) -> int:
        """Burst-attack pattern with periodic dodge breaks."""
        burst_length = int(3 + self.strength_weight * 7)
        cycle_length = burst_length + 2  # 2 ticks of dodge after burst
        phase = self._tick_counter % cycle_length
        if phase < burst_length:
            return ACTION_ATTACK
        return ACTION_MOVE_LEFT
