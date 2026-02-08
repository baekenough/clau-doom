"""Episode runner: executes episodes with injected action selection."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Callable, Optional

from glue.vizdoom_bridge import (
    EpisodeMetrics,
    GameState,
    NUM_ACTIONS,
    VizDoomBridge,
)

logger = logging.getLogger(__name__)

# Type for action selection function
# Takes GameState, returns action index [0, NUM_ACTIONS)
ActionFn = Callable[[GameState], int]


@dataclass
class EpisodeResult:
    """Complete result from a single episode."""

    seed: int
    condition: str
    episode_number: int
    metrics: EpisodeMetrics
    decision_latencies: list[float]  # per-tick latency in ms
    decision_levels: list[int]  # per-tick decision level

    @property
    def decision_latency_p99(self) -> float:
        if not self.decision_latencies:
            return 0.0
        sorted_lats = sorted(self.decision_latencies)
        idx = int(len(sorted_lats) * 0.99)
        return sorted_lats[min(idx, len(sorted_lats) - 1)]

    @property
    def rule_match_rate(self) -> float:
        if not self.decision_levels:
            return 0.0
        return sum(1 for d in self.decision_levels if d == 0) / len(
            self.decision_levels
        )


class EpisodeRunner:
    """Runs episodes with pluggable action selection."""

    def __init__(self, bridge: VizDoomBridge):
        self._bridge = bridge

    def run_episode(
        self,
        seed: int,
        condition: str,
        episode_number: int,
        action_fn: ActionFn,
        decision_level: int = -1,  # -1 for random, 0 for rule-only
    ) -> EpisodeResult:
        """Run a single episode."""
        self._bridge.start_episode(seed)

        decision_latencies: list[float] = []
        decision_levels: list[int] = []

        while not self._bridge.is_episode_finished():
            state = self._bridge.get_game_state()
            if state.is_dead:
                break

            t0 = time.perf_counter_ns()
            action = action_fn(state)
            t1 = time.perf_counter_ns()

            latency_ms = (t1 - t0) / 1e6
            decision_latencies.append(latency_ms)
            # Use dynamic decision level from gRPC if available
            if hasattr(action_fn, 'last_decision_level'):
                decision_levels.append(action_fn.last_decision_level)
            else:
                decision_levels.append(decision_level)

            self._bridge.make_action(action)

        metrics = self._bridge.get_episode_metrics()

        return EpisodeResult(
            seed=seed,
            condition=condition,
            episode_number=episode_number,
            metrics=metrics,
            decision_latencies=decision_latencies,
            decision_levels=decision_levels,
        )

    def run_condition(
        self,
        seeds: list[int],
        condition: str,
        experiment_id: str,
        action_fn: ActionFn,
        decision_level: int = -1,
        on_episode_complete: Optional[Callable[[EpisodeResult], None]] = None,
    ) -> list[EpisodeResult]:
        """Run all episodes for a condition."""
        results: list[EpisodeResult] = []

        for i, seed in enumerate(seeds):
            episode_number = i + 1
            logger.info(
                f"[{condition}] Episode {episode_number}/{len(seeds)} "
                f"(seed={seed})"
            )

            result = self.run_episode(
                seed, condition, episode_number, action_fn, decision_level
            )
            results.append(result)

            if on_episode_complete:
                on_episode_complete(result)

            logger.info(
                f"  kills={result.metrics.kills} "
                f"survival={result.metrics.survival_time:.1f}s "
                f"kill_rate={result.metrics.kill_rate:.2f}/min"
            )

        return results
