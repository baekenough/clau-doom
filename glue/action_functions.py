"""Action selection functions for VizDoom defend_the_center/defend_the_line scenarios.

Provides eleven action strategies (DOE-007/008/010/011 ablation levels):
1. random_action -- uniform random choice (3-action space)
2. rule_only_action -- L0 hardcoded reflex rules (from Rust agent-core)
3. L0MemoryAction -- L0 rules + memory dodge heuristic (no strength modulation)
4. L0StrengthAction -- L0 rules + strength attack probability (no memory dodge)
5. FullAgentAction -- callable class with memory + strength heuristics
6. SweepLRAction -- deterministic sweep-fire: attack-left-attack-right cycle
7. Burst3Action -- burst-fire with repositioning: 3 attacks then 1 random move
8. Burst5Action -- burst-fire with repositioning: 5 attacks then 1 random move
9. Random5Action -- uniform random over 5-action space (DOE-011)
10. StrafeBurst3Action -- 3 attacks then 1 random strafe (DOE-011, 5-action)
11. Smart5Action -- coordinated aim-attack-dodge for 5-action space (DOE-011)
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


class L0MemoryAction:
    """L0 rules + memory dodge heuristic, fixed 68% attack probability.

    Ablation level 3: tests the value of the memory dodge layer in
    isolation, without strength-modulated attack probability.
    """

    def __init__(self) -> None:
        self._rng: random.Random = random.Random(0)
        self._health_history: deque[int] = deque(maxlen=10)

    def reset(self, seed: int = 0) -> None:
        """Reset state between episodes."""
        self._rng = random.Random(hash(seed))
        self._health_history.clear()

    def __call__(self, state: GameState) -> int:
        self._health_history.append(state.health)

        # L0 emergency rules
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT

        # Memory dodge heuristic (memory_weight=0.5)
        if self._should_dodge_memory():
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])

        # Fixed 68% attack probability (no strength modulation)
        if self._rng.random() < 0.68:
            return ACTION_ATTACK
        else:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])

    def _should_dodge_memory(self) -> bool:
        """Memory dodge with memory_weight=0.5 (same logic as FullAgentAction)."""
        if len(self._health_history) < 3:
            return False
        history = list(self._health_history)
        recent_loss = history[-3] - history[-1]
        if recent_loss <= 0:
            return False
        # dodge_threshold at memory=0.5 -> 30.0 * 0.6 = 18.0
        dodge_threshold = 30.0 * (1.1 - 0.5)
        dodge_prob = min(0.9, recent_loss / dodge_threshold)
        return self._rng.random() < dodge_prob


class L0StrengthAction:
    """L0 rules + strength attack probability, no memory dodge.

    Ablation level 4: tests the value of strength-modulated attack
    probability in isolation, without the memory dodge layer.
    """

    def __init__(self) -> None:
        self._rng: random.Random = random.Random(0)

    def reset(self, seed: int = 0) -> None:
        """Reset state between episodes."""
        self._rng = random.Random(hash(seed))

    def __call__(self, state: GameState) -> int:
        # L0 emergency rules
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT

        # No memory dodge -- skip directly to attack decision

        # Strength attack probability (strength_weight=0.5)
        # attack_prob = 0.4 + 0.55 * 0.5 = 0.675
        attack_prob = 0.4 + 0.55 * 0.5
        if self._rng.random() < attack_prob:
            return ACTION_ATTACK
        else:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])


class FullAgentAction:
    """Full agent action with stochastic memory and strength heuristics.

    Implements ``ActionFn`` protocol via ``__call__``.

    The action selection uses a per-episode RNG seeded with a hash of
    (episode_seed, memory_weight, strength_weight).  This guarantees:
    - Determinism: same seed + same params = identical action sequence
    - Differentiation: different params = different RNG = different outcomes

    Args:
        memory_weight: Sensitivity to recent damage (0.0-1.0).
            Higher = more likely to dodge when taking damage.
            Controls dodge PROBABILITY based on recent health loss.
        strength_weight: Aggressiveness (0.0-1.0).
            Higher = higher base attack probability.
            attack_prob = 0.4 + 0.55 * strength_weight
            (range: 0.40 at s=0.0  to  0.95 at s=1.0)
    """

    def __init__(
        self,
        memory_weight: float = 0.5,
        strength_weight: float = 0.5,
    ) -> None:
        self.memory_weight = memory_weight
        self.strength_weight = strength_weight

        # Internal state -- cleared by reset()
        self._rng: random.Random = random.Random(0)
        self._health_history: deque[int] = deque(maxlen=10)
        self._tick_counter: int = 0

    def reset(self, seed: int = 0) -> None:
        """Clear internal state between episodes.

        Seeds the internal RNG with a hash of (seed, memory_weight,
        strength_weight) so that different parameter levels produce
        different action sequences even for the same episode seed.

        Args:
            seed: Episode seed (from DOE seed set).
        """
        # CRITICAL: hash includes rounded params so that different
        # factor levels get different RNG streams.
        combined = hash((
            seed,
            round(self.memory_weight, 4),
            round(self.strength_weight, 4),
        ))
        self._rng = random.Random(combined)
        self._health_history.clear()
        self._tick_counter = 0

    def __call__(self, state: GameState) -> int:
        # Record health for memory heuristic
        self._health_history.append(state.health)
        self._tick_counter += 1

        # --- L0 emergency rules (highest priority, deterministic) ---
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT

        # --- Memory heuristic: dodge when taking damage ---
        # Higher memory_weight = more reactive to health loss.
        if self._should_dodge_memory():
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])

        # --- Strength heuristic: stochastic attack probability ---
        # strength=0.0 -> 40% attack
        # strength=0.3 -> 57% attack
        # strength=0.5 -> 68% attack
        # strength=0.7 -> 79% attack
        # strength=0.9 -> 90% attack
        # strength=1.0 -> 95% attack
        attack_prob = 0.4 + 0.55 * self.strength_weight
        if self._rng.random() < attack_prob:
            return ACTION_ATTACK
        else:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])

    def _should_dodge_memory(self) -> bool:
        """Check if recent health loss warrants dodging.

        Higher memory_weight = more sensitive to health drops = dodges
        more often.

        Dodge probability scales with both the health loss magnitude and
        the memory_weight parameter:
          - memory=0.3: needs ~33 hp loss in 3 ticks for 50% dodge chance
          - memory=0.7: needs ~13 hp loss in 3 ticks for 50% dodge chance
          - memory=0.9: needs ~7 hp loss in 3 ticks for 50% dodge chance

        Returns:
            True if the agent should dodge this tick.
        """
        if len(self._health_history) < 3:
            return False

        history = list(self._health_history)
        # Health lost over the last 3 ticks
        recent_loss = history[-3] - history[-1]
        if recent_loss <= 0:
            return False

        # Dodge threshold inversely proportional to memory_weight.
        # Higher memory -> lower threshold -> easier to trigger dodge.
        # dodge_threshold at memory=0.1 -> 30.0 * 1.0 = 30.0
        # dodge_threshold at memory=0.5 -> 30.0 * 0.6 = 18.0
        # dodge_threshold at memory=0.7 -> 30.0 * 0.4 = 12.0
        # dodge_threshold at memory=0.9 -> 30.0 * 0.2 = 6.0
        dodge_threshold = 30.0 * (1.1 - self.memory_weight)
        dodge_prob = min(0.9, recent_loss / dodge_threshold)
        return self._rng.random() < dodge_prob


class SweepLRAction:
    """Deterministic sweep-fire: attack-left-attack-right cycle.

    Creates a sweeping fire pattern across the enemy line by alternating
    attacks with lateral repositioning. Unlike reactive strategies,
    this pattern is completely deterministic (no RNG).
    """

    def __init__(self) -> None:
        self._tick: int = 0
        self._pattern = [ACTION_ATTACK, ACTION_MOVE_LEFT, ACTION_ATTACK, ACTION_MOVE_RIGHT]

    def reset(self, seed: int = 0) -> None:
        self._tick = 0

    def __call__(self, state: GameState) -> int:
        # L0 emergency rules
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT

        action = self._pattern[self._tick % len(self._pattern)]
        self._tick += 1
        return action


class Burst3Action:
    """Burst-fire with repositioning: 3 attacks then 1 random move.

    Groups attacks into short bursts followed by lateral repositioning.
    Tests whether concentrated fire windows improve kill efficiency
    compared to random movement mixing.
    """

    def __init__(self) -> None:
        self._rng: random.Random = random.Random(0)
        self._tick: int = 0

    def reset(self, seed: int = 0) -> None:
        self._rng = random.Random(hash(seed))
        self._tick = 0

    def __call__(self, state: GameState) -> int:
        # L0 emergency rules
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT

        cycle_pos = self._tick % 4  # 0,1,2 = attack; 3 = move
        self._tick += 1

        if cycle_pos < 3:
            return ACTION_ATTACK
        else:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])


class Burst5Action:
    """Burst-fire with repositioning: 5 attacks then 1 random move.

    Longer burst window than Burst3Action. Tests whether extending
    the attack duration between repositioning improves or hurts
    kill efficiency.
    """

    def __init__(self) -> None:
        self._rng: random.Random = random.Random(0)
        self._tick: int = 0

    def reset(self, seed: int = 0) -> None:
        self._rng = random.Random(hash(seed))
        self._tick = 0

    def __call__(self, state: GameState) -> int:
        # L0 emergency rules
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT

        cycle_pos = self._tick % 6  # 0,1,2,3,4 = attack; 5 = move
        self._tick += 1

        if cycle_pos < 5:
            return ACTION_ATTACK
        else:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])


class Random5Action:
    """Uniform random over 5-action space (turn_left, turn_right, move_left, move_right, attack).

    For DOE-011: Tests dilution effect of expanded action space.
    Only 20% attack rate vs 33% for 3-action random.
    Actions: 0=TURN_LEFT, 1=TURN_RIGHT, 2=MOVE_LEFT, 3=MOVE_RIGHT, 4=ATTACK
    """

    def __init__(self):
        self._rng = None

    def reset(self, seed: int) -> None:
        import random as _random
        self._rng = _random.Random(seed)

    def __call__(self, state) -> int:
        if self._rng is None:
            import random as _random
            self._rng = _random.Random(42)
        return self._rng.randint(0, 4)


class StrafeBurst3Action:
    """3 attacks then 1 random strafe (move_left or move_right).

    For DOE-011: Tests value of strafing vs turning between attack bursts.
    Actions: 0=TURN_LEFT, 1=TURN_RIGHT, 2=MOVE_LEFT, 3=MOVE_RIGHT, 4=ATTACK
    L0 emergency rules still use turn (actions 0,1) for aiming.
    """

    def __init__(self):
        self._rng = None
        self._cycle_pos = 0

    def reset(self, seed: int) -> None:
        import random as _random
        self._rng = _random.Random(seed)
        self._cycle_pos = 0

    def __call__(self, state) -> int:
        if self._rng is None:
            import random as _random
            self._rng = _random.Random(42)

        # L0 emergency: low health -> strafe away
        if state.health < 20:
            return 2  # MOVE_LEFT (strafe to dodge)
        if state.ammo == 0:
            return 2  # MOVE_LEFT

        pos = self._cycle_pos % 4
        self._cycle_pos += 1

        if pos < 3:
            return 4  # ATTACK
        else:
            return self._rng.choice([2, 3])  # random strafe: MOVE_LEFT or MOVE_RIGHT


class Smart5Action:
    """Coordinated aim-attack-dodge strategy for 5-action space.

    For DOE-011: Flagship test of strategy differentiation in expanded space.
    Cycle: attack 3 ticks -> if got kill, dodge (strafe); if no kill, turn to scan -> repeat.
    Actions: 0=TURN_LEFT, 1=TURN_RIGHT, 2=MOVE_LEFT, 3=MOVE_RIGHT, 4=ATTACK
    """

    def __init__(self):
        self._rng = None
        self._phase = "attack"  # attack, turn, dodge
        self._phase_counter = 0
        self._last_kills = 0

    def reset(self, seed: int) -> None:
        import random as _random
        self._rng = _random.Random(seed)
        self._phase = "attack"
        self._phase_counter = 0
        self._last_kills = 0

    def __call__(self, state) -> int:
        if self._rng is None:
            import random as _random
            self._rng = _random.Random(42)

        # L0 emergency: low health -> strafe to dodge
        if state.health < 20:
            return self._rng.choice([2, 3])  # random strafe
        if state.ammo == 0:
            return self._rng.choice([2, 3])  # strafe away

        if self._phase == "attack":
            self._phase_counter += 1
            if self._phase_counter >= 3:
                # After 3 attacks, decide next phase
                if state.kills > self._last_kills:
                    # Got a kill -> dodge to avoid return fire
                    self._phase = "dodge"
                    self._last_kills = state.kills
                else:
                    # No kill -> turn to find enemy
                    self._phase = "turn"
                self._phase_counter = 0
            return 4  # ATTACK

        elif self._phase == "turn":
            self._phase_counter += 1
            if self._phase_counter >= 2:
                self._phase = "attack"
                self._phase_counter = 0
            return self._rng.choice([0, 1])  # random turn direction

        elif self._phase == "dodge":
            # Single strafe then back to attack
            self._phase = "attack"
            self._phase_counter = 0
            return self._rng.choice([2, 3])  # random strafe direction

        return 4  # fallback: ATTACK
