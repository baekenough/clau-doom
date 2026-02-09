"""Action selection functions for VizDoom defend_the_center/defend_the_line scenarios.

Provides action strategies for DOE-007 through DOE-024 ablation levels:
1.  random_action -- uniform random choice (3-action space)
2.  rule_only_action -- L0 hardcoded reflex rules (from Rust agent-core)
3.  L0MemoryAction -- L0 rules + memory dodge heuristic (no strength modulation)
4.  L0StrengthAction -- L0 rules + strength attack probability (no memory dodge)
5.  FullAgentAction -- callable class with memory + strength heuristics
6.  SweepLRAction -- deterministic sweep-fire: attack-left-attack-right cycle
7.  Burst3Action -- burst-fire with repositioning: 3 attacks then 1 random move
8.  Burst5Action -- burst-fire with repositioning: 5 attacks then 1 random move
9.  Random5Action -- uniform random over 5-action space (DOE-011)
10. StrafeBurst3Action -- 3 attacks then 1 random strafe (DOE-011, 5-action)
11. Smart5Action -- coordinated aim-attack-dodge for 5-action space (DOE-011)
12. CompoundAttackTurnAction -- attack + random turn simultaneously (DOE-012)
13. CompoundBurst3Action -- 3-tick compound burst then reposition (DOE-012)
14. Burst1Action -- 1 attack then 1 move, 50% attack rate (DOE-013)
15. Burst7Action -- 7 attacks then 1 move, 87.5% attack rate (DOE-013)
16. AttackOnlyAction -- 100% attack, never moves (DOE-013)
17. Burst3ThresholdAction -- burst_3 with configurable L0 threshold (DOE-014)
18. Random7Action -- uniform random over 7-action space (DOE-016)
19. ForwardAttackAction -- move forward while attacking (DOE-016)
20. AdaptiveKillAction -- state-dependent adaptive strategy (DOE-018)
21. AggressiveAdaptiveAction -- aggressive adaptive, dodge only at critical health (DOE-018)
22. GenomeAction -- parameterized genome action for evolutionary experiments (DOE-021)
23. L2RagAction -- L2 RAG strategy retrieval with OpenSearch kNN (DOE-022)
24. L2MetaStrategyAction -- L2 meta-strategy selector, delegates to L1 strategies (DOE-024)
25. RandomSelectAction -- random strategy selector baseline (DOE-024)
26. Adaptive5Action -- health-responsive adaptive strategy for 5-action space (DOE-025)
27. DodgeBurst3Action -- 3 attacks + 2 strafes cycle for 5-action space (DOE-025)
28. SurvivalBurstAction -- 2 attacks + 2 strafes + 1 turn cycle for 5-action space (DOE-025)
29. L2MetaStrategy5Action -- L2 meta-strategy selector for 5-action space (DOE-026)
30. RandomRotation5Action -- random rotation among 5-action strategies (DOE-026)
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


class Adaptive5Action:
    """Health-responsive adaptive strategy for 5-action space.

    For DOE-025: Tests value of state-dependent behavior in 5-action space.
    Actions: 0=TURN_LEFT, 1=TURN_RIGHT, 2=MOVE_LEFT, 3=MOVE_RIGHT, 4=ATTACK

    Behavior:
    - Track health over last 10 ticks
    - If health dropped >10 in last 10 ticks: strafe mode (strafe 60%, attack 40%)
    - If health stable: attack mode (burst_3 pattern: 3 attacks + 1 turn)
    - After kill: 1 tick strafe dodge then resume
    L0 emergency: low health (<20) or no ammo -> full strafe
    """

    def __init__(self):
        self._rng = None
        self._health_history = None  # deque(maxlen=10)
        self._last_kills = 0
        self._burst_pos = 0
        self._dodge_after_kill = False

    def reset(self, seed: int) -> None:
        import random as _random
        from collections import deque
        self._rng = _random.Random(seed)
        self._health_history = deque(maxlen=10)
        self._last_kills = 0
        self._burst_pos = 0
        self._dodge_after_kill = False

    def __call__(self, state) -> int:
        if self._rng is None:
            import random as _random
            from collections import deque
            self._rng = _random.Random(42)
            self._health_history = deque(maxlen=10)

        self._health_history.append(state.health)

        # L0 emergency
        if state.health < 20:
            return self._rng.choice([2, 3])  # random strafe
        if state.ammo == 0:
            return self._rng.choice([2, 3])

        # Post-kill dodge
        if state.kills > self._last_kills:
            self._last_kills = state.kills
            self._dodge_after_kill = True

        if self._dodge_after_kill:
            self._dodge_after_kill = False
            return self._rng.choice([2, 3])  # strafe dodge

        # Check if health is declining
        health_declining = False
        if len(self._health_history) >= 10:
            health_delta = self._health_history[-1] - self._health_history[0]
            if health_delta < -10:
                health_declining = True

        if health_declining:
            # Strafe mode: 60% strafe, 40% attack
            if self._rng.random() < 0.6:
                return self._rng.choice([2, 3])  # strafe
            else:
                return 4  # ATTACK
        else:
            # Attack mode: burst_3 pattern with turns
            pos = self._burst_pos % 4
            self._burst_pos += 1
            if pos < 3:
                return 4  # ATTACK
            else:
                return self._rng.choice([0, 1])  # random turn to scan


class DodgeBurst3Action:
    """3 attacks + 2 strafes cycle for 5-action space.

    For DOE-025: Intermediate point on attack/strafe gradient (60% attack).
    Actions: 0=TURN_LEFT, 1=TURN_RIGHT, 2=MOVE_LEFT, 3=MOVE_RIGHT, 4=ATTACK
    Cycle: ATTACK, ATTACK, ATTACK, STRAFE, STRAFE (period = 5)
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

        # L0 emergency
        if state.health < 20:
            return self._rng.choice([2, 3])
        if state.ammo == 0:
            return self._rng.choice([2, 3])

        pos = self._cycle_pos % 5
        self._cycle_pos += 1

        if pos < 3:
            return 4  # ATTACK
        else:
            return self._rng.choice([2, 3])  # random strafe


class SurvivalBurstAction:
    """2 attacks + 2 strafes + 1 turn cycle for 5-action space.

    For DOE-025: Maximum survival with minimal offense (40% attack).
    Actions: 0=TURN_LEFT, 1=TURN_RIGHT, 2=MOVE_LEFT, 3=MOVE_RIGHT, 4=ATTACK
    Cycle: ATTACK, ATTACK, STRAFE, STRAFE, TURN (period = 5)
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

        # L0 emergency
        if state.health < 20:
            return self._rng.choice([2, 3])
        if state.ammo == 0:
            return self._rng.choice([2, 3])

        pos = self._cycle_pos % 5
        self._cycle_pos += 1

        if pos < 2:
            return 4  # ATTACK
        elif pos < 4:
            return self._rng.choice([2, 3])  # random strafe
        else:
            return self._rng.choice([0, 1])  # random turn to scan


class CompoundAttackTurnAction:
    """Compound action: attack + random turn simultaneously every tick.

    For DOE-012: Tests simultaneous button presses.
    Returns a LIST [int, ...] instead of single int.
    The VizDoomBridge must handle list returns as multi-hot vectors.

    In 3-button space (TURN_LEFT, TURN_RIGHT, ATTACK):
    - [1, 0, 1] = turn left + attack
    - [0, 1, 1] = turn right + attack
    """

    def __init__(self):
        self._rng = None

    def reset(self, seed: int) -> None:
        import random as _random
        self._rng = _random.Random(seed)

    def __call__(self, state) -> list:
        if self._rng is None:
            import random as _random
            self._rng = _random.Random(42)

        if state.health < 20:
            return [1, 0, 0]  # turn left only (dodge)
        if state.ammo == 0:
            return [1, 0, 0]

        # Attack + random turn direction
        if self._rng.random() < 0.5:
            return [1, 0, 1]  # turn_left + attack
        else:
            return [0, 1, 1]  # turn_right + attack


class CompoundBurst3Action:
    """3 ticks of attack+turn compound, then 1 tick of turn-only to reposition.

    For DOE-012: Compound burst pattern.
    Returns LIST for multi-hot encoding.
    """

    def __init__(self):
        self._rng = None
        self._tick = 0

    def reset(self, seed: int) -> None:
        import random as _random
        self._rng = _random.Random(seed)
        self._tick = 0

    def __call__(self, state) -> list:
        if self._rng is None:
            import random as _random
            self._rng = _random.Random(42)

        if state.health < 20:
            return [1, 0, 0]
        if state.ammo == 0:
            return [1, 0, 0]

        pos = self._tick % 4
        self._tick += 1

        turn = [1, 0] if self._rng.random() < 0.5 else [0, 1]

        if pos < 3:
            return turn + [1]  # turn + attack
        else:
            return turn + [0]  # turn only (reposition)


class Burst1Action:
    """1 attack then 1 random move (50% attack rate).

    For DOE-013: Attack ratio sweep.
    """

    def __init__(self):
        self._rng = None
        self._tick = 0

    def reset(self, seed: int) -> None:
        import random as _random
        self._rng = _random.Random(seed)
        self._tick = 0

    def __call__(self, state) -> int:
        if self._rng is None:
            import random as _random
            self._rng = _random.Random(42)
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT
        pos = self._tick % 2
        self._tick += 1
        if pos == 0:
            return ACTION_ATTACK
        else:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])


class Burst7Action:
    """7 attacks then 1 random move (87.5% attack rate).

    For DOE-013: Attack ratio sweep.
    """

    def __init__(self):
        self._rng = None
        self._tick = 0

    def reset(self, seed: int) -> None:
        import random as _random
        self._rng = _random.Random(seed)
        self._tick = 0

    def __call__(self, state) -> int:
        if self._rng is None:
            import random as _random
            self._rng = _random.Random(42)
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT
        pos = self._tick % 8
        self._tick += 1
        if pos < 7:
            return ACTION_ATTACK
        else:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])


class AttackOnlyAction:
    """100% attack -- never moves.

    For DOE-013: Attack ratio sweep.
    """

    def __init__(self):
        pass

    def reset(self, seed: int) -> None:
        pass

    def __call__(self, state) -> int:
        return ACTION_ATTACK


class Burst3ThresholdAction:
    """Burst3 with configurable L0 health threshold.

    For DOE-014: L0 emergency threshold tuning.
    """

    def __init__(self, health_threshold: int = 20):
        self._rng = None
        self._tick = 0
        self._health_threshold = health_threshold

    def reset(self, seed: int) -> None:
        import random as _random
        self._rng = _random.Random(seed)
        self._tick = 0

    def __call__(self, state) -> int:
        if self._rng is None:
            import random as _random
            self._rng = _random.Random(42)
        if state.health < self._health_threshold:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])
        if state.ammo == 0:
            return ACTION_MOVE_LEFT
        pos = self._tick % 4
        self._tick += 1
        if pos < 3:
            return ACTION_ATTACK
        else:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])


class Random7Action:
    """Uniform random over 7-action space (deadly_corridor).

    Actions: 0-6 mapping to MOVE_LEFT, MOVE_RIGHT, ATTACK, MOVE_FORWARD,
    MOVE_BACKWARD, TURN_LEFT, TURN_RIGHT.
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
        return self._rng.randint(0, 6)


class ForwardAttackAction:
    """Move forward while attacking. For deadly_corridor: advance through corridor.

    Cycle: 3 attack, 1 move_forward, repeat.
    Uses action indices for deadly_corridor cfg: ATTACK=2, MOVE_FORWARD=3.
    """

    def __init__(self):
        self._tick = 0

    def reset(self, seed: int) -> None:
        self._tick = 0

    def __call__(self, state) -> int:
        pos = self._tick % 4
        self._tick += 1
        if pos < 3:
            return 2  # ATTACK
        else:
            return 3  # MOVE_FORWARD


class AdaptiveKillAction:
    """State-dependent adaptive strategy.

    For DOE-018: Adaptive strategy test.
    - High health (>60): pure attack (maximize kills)
    - Medium health (30-60): burst_3 pattern (balanced)
    - Low health (<30): mostly dodge with occasional attacks
    Tracks kills to detect stagnation -> increase turning.
    """

    def __init__(self):
        self._rng = None
        self._tick = 0
        self._last_kills = 0
        self._stagnant_ticks = 0

    def reset(self, seed: int) -> None:
        import random as _random
        self._rng = _random.Random(seed)
        self._tick = 0
        self._last_kills = 0
        self._stagnant_ticks = 0

    def __call__(self, state) -> int:
        if self._rng is None:
            import random as _random
            self._rng = _random.Random(42)

        # Track kill stagnation
        if state.kills > self._last_kills:
            self._last_kills = state.kills
            self._stagnant_ticks = 0
        else:
            self._stagnant_ticks += 1

        self._tick += 1

        # If stagnant for 20+ ticks, turn to find enemies
        if self._stagnant_ticks > 20:
            self._stagnant_ticks = 0
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])

        # Health-based behavior
        if state.health > 60:
            # Aggressive: pure attack
            return ACTION_ATTACK
        elif state.health > 30:
            # Balanced: burst_3 pattern
            pos = self._tick % 4
            if pos < 3:
                return ACTION_ATTACK
            else:
                return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])
        else:
            # Defensive: mostly dodge
            if self._rng.random() < 0.3:
                return ACTION_ATTACK
            else:
                return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])


class AggressiveAdaptiveAction:
    """Aggressive adaptive: always attack unless health critically low.

    For DOE-018. Simpler adaptive that only dodges at health < 15.
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
        if state.health < 15:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])
        return ACTION_ATTACK


class GenomeAction:
    """Parameterized genome action for evolutionary experiments (DOE-021+).

    8-parameter genome controlling burst/turn cycle with optional adaptive switching.

    Genome parameters:
        burst_length: Number of consecutive ATTACK actions [1..7]
        turn_direction: "random", "alternate", "sweep_left", "sweep_right"
        turn_count: Number of consecutive TURN actions [1..3]
        health_threshold_high: Above this health → defensive mode [0..100]
        health_threshold_low: Below this health → aggressive mode [0..100]
        stagnation_window: Ticks without kill → force turn [0..10], 0=disabled
        attack_probability: Base probability of ATTACK vs TURN [0.5..1.0]
        adaptive_enabled: Use state-dependent switching

    Behavior when adaptive_enabled = False:
        repeat forever:
          for i in 1..burst_length:
            action = ATTACK
          for i in 1..turn_count:
            action = TURN_{turn_direction}

    Behavior when adaptive_enabled = True:
        if health > health_threshold_high:
          # Defensive: more turning for survivability
          action = TURN with p = 1 - attack_probability
          action = ATTACK with p = attack_probability
        elif health < health_threshold_low:
          # Aggressive: always ATTACK
          action = ATTACK
        else:
          # Normal: burst cycle (same as non-adaptive)
          for i in 1..burst_length: ATTACK
          for i in 1..turn_count: TURN

        if stagnation_window > 0 and ticks_since_last_kill >= stagnation_window:
          action = TURN  # Force reorientation
    """

    def __init__(
        self,
        burst_length: int = 3,
        turn_direction: str = "random",
        turn_count: int = 1,
        health_threshold_high: int = 0,
        health_threshold_low: int = 0,
        stagnation_window: int = 0,
        attack_probability: float = 0.75,
        adaptive_enabled: bool = False,
    ) -> None:
        # Genome parameters
        self.burst_length = burst_length
        self.turn_direction = turn_direction
        self.turn_count = turn_count
        self.health_threshold_high = health_threshold_high
        self.health_threshold_low = health_threshold_low
        self.stagnation_window = stagnation_window
        self.attack_probability = attack_probability
        self.adaptive_enabled = adaptive_enabled

        # Internal state (cleared by reset())
        self._rng: random.Random = random.Random(0)
        self._tick: int = 0
        self._last_kills: int = 0
        self._stagnant_ticks: int = 0
        self._turn_alternator: int = 0  # For "alternate" turn direction

    def reset(self, seed: int = 0) -> None:
        """Reset state between episodes.

        Seeds the internal RNG with a hash of (seed, all genome params)
        so that different genomes produce different action sequences.

        Args:
            seed: Episode seed (from DOE seed set).
        """
        # CRITICAL: hash includes all genome parameters so that different
        # genomes get different RNG streams even with the same episode seed.
        combined = hash((
            seed,
            self.burst_length,
            self.turn_direction,
            self.turn_count,
            self.health_threshold_high,
            self.health_threshold_low,
            self.stagnation_window,
            round(self.attack_probability, 4),
            self.adaptive_enabled,
        ))
        self._rng = random.Random(combined)
        self._tick = 0
        self._last_kills = 0
        self._stagnant_ticks = 0
        self._turn_alternator = 0

    def __call__(self, state: GameState) -> int:
        # Track ticks and kills for stagnation detection
        if self.adaptive_enabled and self.stagnation_window > 0:
            if state.kills > self._last_kills:
                self._last_kills = state.kills
                self._stagnant_ticks = 0
            else:
                self._stagnant_ticks += 1

        # --- L0 emergency rules (highest priority, deterministic) ---
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT

        # --- Stagnation override (adaptive mode only) ---
        if (self.adaptive_enabled
            and self.stagnation_window > 0
            and self._stagnant_ticks >= self.stagnation_window):
            self._stagnant_ticks = 0  # Reset counter
            return self._get_turn_action()

        # --- Adaptive switching logic ---
        if self.adaptive_enabled:
            if state.health > self.health_threshold_high:
                # Defensive mode: mostly turning
                if self._rng.random() < (1.0 - self.attack_probability):
                    return self._get_turn_action()
                else:
                    return ACTION_ATTACK
            elif state.health < self.health_threshold_low:
                # Aggressive mode: always attack
                return ACTION_ATTACK
            # else: fall through to normal burst cycle

        # --- Normal burst/turn cycle ---
        cycle_length = self.burst_length + self.turn_count
        cycle_pos = self._tick % cycle_length

        self._tick += 1

        if cycle_pos < self.burst_length:
            return ACTION_ATTACK
        else:
            return self._get_turn_action()

    def _get_turn_action(self) -> int:
        """Get turn action based on turn_direction parameter."""
        if self.turn_direction == "random":
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])
        elif self.turn_direction == "alternate":
            # Alternate between left and right
            self._turn_alternator = 1 - self._turn_alternator
            return ACTION_MOVE_LEFT if self._turn_alternator == 0 else ACTION_MOVE_RIGHT
        elif self.turn_direction == "sweep_left":
            return ACTION_MOVE_LEFT
        elif self.turn_direction == "sweep_right":
            return ACTION_MOVE_RIGHT
        else:
            # Fallback: random
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])


class L2RagAction:
    """L2 strategy document retrieval action function for DOE-022.

    Mirrors agent-core/src/rag/mod.rs logic in Python.
    Queries OpenSearch for matching strategy documents via term matching
    on situation_tags, scores them, and selects the best action.

    Fallback: burst_3 pattern (best known L0+L1 strategy from DOE-020).
    """

    def __init__(self, opensearch_url="http://opensearch:9200", index_name="strategies_high", k=5):
        self.opensearch_url = opensearch_url
        self.index_name = index_name
        self.k = k
        self.weights = {"similarity": 0.4, "confidence": 0.4, "recency": 0.2}

        # Burst3 fallback state
        self._rng = random.Random(0)
        self._tick = 0

        # L2 metrics tracking
        self.l2_decisions = 0
        self.l2_total_decisions = 0
        self.l2_latencies = []

        # HTTP session for connection pooling
        import urllib.request
        self._session = None

    def reset(self, seed=0):
        """Reset state between episodes."""
        self._rng = random.Random(hash(seed))
        self._tick = 0
        self.l2_decisions = 0
        self.l2_total_decisions = 0
        self.l2_latencies = []

    def derive_situation_tags(self, state):
        """Mirror derive_situation_tags() from rag/mod.rs lines 54-79."""
        tags = []
        if state.health < 30:
            tags.append("low_health")
        elif state.health >= 80:
            tags.append("full_health")
        if state.ammo < 10:
            tags.append("low_ammo")
        elif state.ammo >= 50:
            tags.append("ammo_abundant")
        if state.enemies_visible >= 3:
            tags.append("multi_enemy")
        elif state.enemies_visible == 1:
            tags.append("single_enemy")
        return tags

    def query_opensearch(self, tags):
        """Execute OpenSearch term-match query. Returns list of docs or empty list."""
        import json
        import time
        import urllib.request
        import urllib.error

        query_body = {
            "size": self.k,
            "query": {
                "bool": {
                    "should": [{"term": {"situation_tags": tag}} for tag in tags],
                    "minimum_should_match": 1,
                    "filter": [
                        {"term": {"metadata.retired": False}},
                        {"range": {"quality.trust_score": {"gte": 0.3}}}
                    ]
                }
            }
        }

        url = f"{self.opensearch_url}/{self.index_name}/_search"
        data = json.dumps(query_body).encode("utf-8")

        start = time.monotonic()
        try:
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=0.08) as resp:
                result = json.loads(resp.read())
        except Exception:
            return []
        finally:
            elapsed_ms = (time.monotonic() - start) * 1000
            self.l2_latencies.append(elapsed_ms)

        hits = result.get("hits", {}).get("hits", [])
        docs = []
        for hit in hits:
            source = hit.get("_source", {})
            score = hit.get("_score", 0.0)
            docs.append({
                "doc_id": source.get("doc_id", ""),
                "situation_tags": source.get("situation_tags", []),
                "decision": source.get("decision", {}),
                "quality": source.get("quality", {}),
                "similarity": min(score / self.k, 1.0),
                "confidence": source.get("quality", {}).get("trust_score", 0.5),
                "recency": 0.8,
            })
        return docs

    def score_document(self, doc):
        """Score document: similarity*0.4 + confidence*0.4 + recency*0.2"""
        return (
            self.weights["similarity"] * doc.get("similarity", 0)
            + self.weights["confidence"] * doc.get("confidence", 0)
            + self.weights["recency"] * doc.get("recency", 0)
        )

    def tactic_to_action(self, tactic):
        """Map tactic string to action index (mirrors rag/mod.rs lines 82-91)."""
        if tactic.startswith("retreat") or tactic.startswith("kite"):
            return ACTION_MOVE_LEFT
        elif tactic.startswith("flank"):
            return ACTION_MOVE_RIGHT
        else:
            return ACTION_ATTACK

    def _burst3_fallback(self, state):
        """Burst3 pattern as L1 fallback."""
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT
        cycle_pos = self._tick % 4
        self._tick += 1
        if cycle_pos < 3:
            return ACTION_ATTACK
        else:
            return self._rng.choice([ACTION_MOVE_LEFT, ACTION_MOVE_RIGHT])

    def __call__(self, state):
        """Full L0 + L2 + L1-fallback cascade in Python."""
        self.l2_total_decisions += 1

        # L0: Emergency rules (highest priority)
        if state.health < 20:
            return ACTION_MOVE_LEFT
        if state.ammo == 0:
            return ACTION_MOVE_LEFT

        # L2: Query OpenSearch for strategy document
        tags = self.derive_situation_tags(state)
        if tags:
            docs = self.query_opensearch(tags)
            if docs:
                best = max(docs, key=self.score_document)
                tactic = best.get("decision", {}).get("tactic", "attack")
                self.l2_decisions += 1
                return self.tactic_to_action(tactic)

        # L1 Fallback: burst_3 pattern (best known L0+L1 strategy)
        return self._burst3_fallback(state)


class L2MetaStrategyAction:
    """L2 meta-strategy selector for DOE-024.

    Queries OpenSearch for meta-strategy documents.
    Top document's decision.strategy field specifies which L1 STRATEGY
    to delegate to (burst_3 or adaptive_kill).

    Key difference from L2RagAction (DOE-022):
    - L2RagAction: query -> tactic name -> tactic_to_action() -> single action (REPLACES L1)
    - L2MetaStrategyAction: query -> strategy name -> delegate to L1 function (PRESERVES L1)

    Query caching: re-evaluates strategy every QUERY_INTERVAL ticks (default 35 = 1/sec).
    Fallback: burst_3 when no documents match or OpenSearch unavailable.
    """
    QUERY_INTERVAL = 35  # Re-evaluate strategy once per second (35 fps)

    def __init__(self, opensearch_url="http://opensearch:9200", index_name="strategies_meta", k=5):
        self.opensearch_url = opensearch_url
        self.index_name = index_name
        self.k = k
        self.weights = {"similarity": 0.4, "confidence": 0.4, "recency": 0.2}

        # L1 strategy delegates
        self.strategies = {
            "burst_3": Burst3Action(),
            "adaptive_kill": AdaptiveKillAction(),
        }
        self.current_strategy = "burst_3"  # default fallback
        self._tick = 0

        # Metrics tracking
        self.l2_query_count = 0
        self.l2_strategy_switches = 0
        self.strategy_ticks = {"burst_3": 0, "adaptive_kill": 0}
        self.l2_latencies = []

    def reset(self, seed=0):
        """Reset state between episodes."""
        self._tick = 0
        self.current_strategy = "burst_3"
        self.l2_query_count = 0
        self.l2_strategy_switches = 0
        self.strategy_ticks = {"burst_3": 0, "adaptive_kill": 0}
        self.l2_latencies = []
        # Reset L1 strategies
        for s in self.strategies.values():
            s.reset(seed)

    def derive_situation_tags(self, state):
        """Derive situation tags from game state. Extended from DOE-022 with kill-based tags."""
        tags = []
        if state.health < 30:
            tags.append("low_health")
        elif state.health >= 80:
            tags.append("full_health")
        if state.ammo < 10:
            tags.append("low_ammo")
        elif state.ammo >= 50:
            tags.append("ammo_abundant")
        if state.enemies_visible >= 3:
            tags.append("multi_enemy")
        elif state.enemies_visible == 1:
            tags.append("single_enemy")
        # NEW for DOE-024: kill-based context
        if state.kills >= 10:
            tags.append("high_kills")
        elif state.kills < 5:
            tags.append("low_kills")
        return tags

    def query_opensearch(self, tags):
        """Execute OpenSearch term-match query. Returns list of docs or empty list."""
        import json
        import time
        import urllib.request
        import urllib.error

        query_body = {
            "size": self.k,
            "query": {
                "bool": {
                    "should": [{"term": {"situation_tags": tag}} for tag in tags],
                    "minimum_should_match": 1,
                    "filter": [
                        {"term": {"metadata.retired": False}},
                        {"range": {"quality.trust_score": {"gte": 0.3}}}
                    ]
                }
            }
        }

        url = f"{self.opensearch_url}/{self.index_name}/_search"
        data = json.dumps(query_body).encode("utf-8")

        start = time.monotonic()
        try:
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=0.08) as resp:
                result = json.loads(resp.read())
        except Exception:
            return []
        finally:
            elapsed_ms = (time.monotonic() - start) * 1000
            self.l2_latencies.append(elapsed_ms)

        hits = result.get("hits", {}).get("hits", [])
        docs = []
        for hit in hits:
            source = hit.get("_source", {})
            score = hit.get("_score", 0.0)
            docs.append({
                "doc_id": source.get("doc_id", ""),
                "situation_tags": source.get("situation_tags", []),
                "decision": source.get("decision", {}),
                "quality": source.get("quality", {}),
                "similarity": min(score / self.k, 1.0),
                "confidence": source.get("quality", {}).get("trust_score", 0.5),
                "recency": 0.8,
            })
        return docs

    def score_document(self, doc):
        """Score document: similarity*0.4 + confidence*0.4 + recency*0.2"""
        return (
            self.weights["similarity"] * doc.get("similarity", 0)
            + self.weights["confidence"] * doc.get("confidence", 0)
            + self.weights["recency"] * doc.get("recency", 0)
        )

    def _update_strategy(self, state):
        """Query OpenSearch and update current strategy selection."""
        tags = self.derive_situation_tags(state)
        if not tags:
            return

        docs = self.query_opensearch(tags)
        self.l2_query_count += 1

        if docs:
            best = max(docs, key=self.score_document)
            strategy_name = best.get("decision", {}).get("strategy", "burst_3")
            if strategy_name in self.strategies and strategy_name != self.current_strategy:
                self.l2_strategy_switches += 1
                self.current_strategy = strategy_name

    def __call__(self, state):
        """Full L0 + L2-meta + L1-delegate cascade."""
        self._tick += 1

        # Track strategy distribution
        self.strategy_ticks[self.current_strategy] = self.strategy_ticks.get(self.current_strategy, 0) + 1

        # L2: Re-evaluate strategy every QUERY_INTERVAL ticks
        if self._tick % self.QUERY_INTERVAL == 0:
            self._update_strategy(state)

        # Delegate to selected L1 strategy (preserves full L1 pattern)
        return self.strategies[self.current_strategy](state)


class RandomSelectAction:
    """Random strategy selector (noise baseline) for DOE-024.

    Each tick, randomly selects burst_3 or adaptive_kill
    with equal probability. No game-state awareness.
    """

    def __init__(self):
        self._rng = None
        self.strategies = {
            "burst_3": Burst3Action(),
            "adaptive_kill": AdaptiveKillAction(),
        }
        self.strategy_ticks = {"burst_3": 0, "adaptive_kill": 0}

    def reset(self, seed=0):
        self._rng = random.Random(hash(seed))
        self.strategy_ticks = {"burst_3": 0, "adaptive_kill": 0}
        for s in self.strategies.values():
            s.reset(seed)

    def __call__(self, state):
        if self._rng is None:
            self._rng = random.Random(42)
        choice = self._rng.choice(["burst_3", "adaptive_kill"])
        self.strategy_ticks[choice] = self.strategy_ticks.get(choice, 0) + 1
        return self.strategies[choice](state)


class L2MetaStrategy5Action:
    """L2 meta-strategy selector for 5-action space (DOE-026).

    Queries OpenSearch strategies_meta_5action index for situation-aware
    strategy selection among top 5-action strategies from DOE-025.

    Delegates to: survival_burst, random_5, dodge_burst_3.
    Query interval: 35 ticks (1 second) — re-evaluates periodically.
    Fallback: survival_burst (best from DOE-025).
    """
    QUERY_INTERVAL = 35

    def __init__(self, opensearch_url="http://opensearch:9200", index_name="strategies_meta_5action", k=5):
        self.opensearch_url = opensearch_url
        self.index_name = index_name
        self.k = k
        self.weights = {"similarity": 0.4, "confidence": 0.4, "recency": 0.2}

        self.strategies = {
            "survival_burst": SurvivalBurstAction(),
            "random_5": Random5Action(),
            "dodge_burst_3": DodgeBurst3Action(),
        }
        self.current_strategy = "survival_burst"
        self._tick = 0

        self.l2_query_count = 0
        self.l2_strategy_switches = 0
        self.strategy_ticks = {"survival_burst": 0, "random_5": 0, "dodge_burst_3": 0}
        self.l2_latencies = []

    def reset(self, seed=0):
        """Reset state between episodes."""
        self._tick = 0
        self.current_strategy = "survival_burst"
        self.l2_query_count = 0
        self.l2_strategy_switches = 0
        self.strategy_ticks = {"survival_burst": 0, "random_5": 0, "dodge_burst_3": 0}
        self.l2_latencies = []
        for s in self.strategies.values():
            s.reset(seed)

    def derive_situation_tags(self, state):
        """Derive situation tags from game state."""
        tags = []
        if state.health < 30:
            tags.append("low_health")
        elif state.health >= 80:
            tags.append("full_health")
        if state.ammo < 10:
            tags.append("low_ammo")
        elif state.ammo >= 50:
            tags.append("ammo_abundant")
        if state.enemies_visible >= 3:
            tags.append("multi_enemy")
        elif state.enemies_visible == 1:
            tags.append("single_enemy")
        return tags

    def query_opensearch(self, tags):
        """Execute OpenSearch term-match query."""
        import json
        import time
        import urllib.request

        query_body = {
            "size": self.k,
            "query": {
                "bool": {
                    "should": [{"term": {"situation_tags": tag}} for tag in tags],
                    "minimum_should_match": 1,
                    "filter": [
                        {"term": {"metadata.retired": False}},
                        {"range": {"quality.trust_score": {"gte": 0.3}}}
                    ]
                }
            }
        }

        url = f"{self.opensearch_url}/{self.index_name}/_search"
        data = json.dumps(query_body).encode("utf-8")

        start = time.monotonic()
        try:
            req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=0.08) as resp:
                result = json.loads(resp.read())
        except Exception:
            return []
        finally:
            elapsed_ms = (time.monotonic() - start) * 1000
            self.l2_latencies.append(elapsed_ms)

        hits = result.get("hits", {}).get("hits", [])
        docs = []
        for hit in hits:
            source = hit.get("_source", {})
            score = hit.get("_score", 0.0)
            docs.append({
                "doc_id": source.get("doc_id", ""),
                "decision": source.get("decision", {}),
                "similarity": min(score / self.k, 1.0),
                "confidence": source.get("quality", {}).get("trust_score", 0.5),
                "recency": 0.8,
            })
        return docs

    def score_document(self, doc):
        """Score document: similarity*0.4 + confidence*0.4 + recency*0.2"""
        return (
            self.weights["similarity"] * doc.get("similarity", 0)
            + self.weights["confidence"] * doc.get("confidence", 0)
            + self.weights["recency"] * doc.get("recency", 0)
        )

    def _update_strategy(self, state):
        """Query OpenSearch and update current strategy selection."""
        tags = self.derive_situation_tags(state)
        if not tags:
            return

        docs = self.query_opensearch(tags)
        self.l2_query_count += 1

        if docs:
            best = max(docs, key=self.score_document)
            strategy_name = best.get("decision", {}).get("strategy", "survival_burst")
            if strategy_name in self.strategies and strategy_name != self.current_strategy:
                self.l2_strategy_switches += 1
                self.current_strategy = strategy_name

    def __call__(self, state):
        """Full L2-meta + L1-delegate cascade for 5-action space."""
        self._tick += 1
        self.strategy_ticks[self.current_strategy] = self.strategy_ticks.get(self.current_strategy, 0) + 1

        if self._tick % self.QUERY_INTERVAL == 0:
            self._update_strategy(state)

        return self.strategies[self.current_strategy](state)


class RandomRotation5Action:
    """Random rotation among 5-action strategies (DOE-026).

    Randomly selects from {survival_burst, random_5, dodge_burst_3}
    every ROTATION_INTERVAL ticks. No game-state awareness.
    Controls for strategy-switching benefit vs RAG-informed switching.
    """
    ROTATION_INTERVAL = 35

    def __init__(self):
        self._rng = None
        self._tick = 0
        self.strategies = {
            "survival_burst": SurvivalBurstAction(),
            "random_5": Random5Action(),
            "dodge_burst_3": DodgeBurst3Action(),
        }
        self.current_strategy = "survival_burst"
        self.strategy_ticks = {"survival_burst": 0, "random_5": 0, "dodge_burst_3": 0}
        self.l2_strategy_switches = 0

    def reset(self, seed=0):
        self._rng = random.Random(hash(seed))
        self._tick = 0
        self.current_strategy = self._rng.choice(["survival_burst", "random_5", "dodge_burst_3"])
        self.strategy_ticks = {"survival_burst": 0, "random_5": 0, "dodge_burst_3": 0}
        self.l2_strategy_switches = 0
        for s in self.strategies.values():
            s.reset(seed)

    def __call__(self, state):
        self._tick += 1
        self.strategy_ticks[self.current_strategy] = self.strategy_ticks.get(self.current_strategy, 0) + 1

        if self._tick % self.ROTATION_INTERVAL == 0:
            choices = ["survival_burst", "random_5", "dodge_burst_3"]
            new_choice = self._rng.choice(choices)
            if new_choice != self.current_strategy:
                self.l2_strategy_switches += 1
                self.current_strategy = new_choice

        return self.strategies[self.current_strategy](state)
