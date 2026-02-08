"""VizDoom bridge: Python glue between VizDoom engine and Rust agent-core.

Responsibilities:
1. Initialize and manage VizDoom game instances
2. Extract GameState from each frame
3. Apply actions to the game engine
4. Compute episode-level metrics
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


@dataclass
class GameState:
    """Current game frame observation."""

    health: int = 100
    ammo: int = 26  # defend_the_center starting AMMO2 (cell ammo)
    kills: int = 0
    enemies_visible: int = 0
    position_x: float = 0.0
    position_y: float = 0.0
    position_z: float = 0.0
    angle: float = 0.0
    episode_time: float = 0.0
    is_dead: bool = False
    tick: int = 0


@dataclass
class EpisodeMetrics:
    """Computed metrics for a completed episode."""

    kills: int = 0
    survival_time: float = 0.0  # seconds (ticks / 35)
    damage_dealt: float = 0.0
    damage_taken: float = 0.0
    ammo_efficiency: float = 0.0  # hits / shots_fired
    exploration_coverage: float = 0.0
    kill_rate: float = 0.0  # kills per minute
    total_ticks: int = 0
    shots_fired: int = 0
    hits: int = 0
    cells_visited: int = 0


# Action indices for defend_the_center scenario
ACTION_MOVE_LEFT = 0
ACTION_MOVE_RIGHT = 1
ACTION_ATTACK = 2
NUM_ACTIONS = 3


class VizDoomBridge:
    """Wraps VizDoom for controlled experiment execution."""

    def __init__(self, scenario: str = "defend_the_center.cfg", episode_timeout: int = 2100, num_actions: int = 3):
        try:
            import vizdoom
        except ImportError:
            raise RuntimeError(
                "VizDoom not installed. Run: pip install vizdoom"
            )

        self._vizdoom = vizdoom
        self._game = vizdoom.DoomGame()
        self._episode_timeout = episode_timeout
        self._num_actions = num_actions

        # Find scenario path
        scenario_path = Path(vizdoom.scenarios_path) / scenario
        if not scenario_path.exists():
            raise FileNotFoundError(f"Scenario not found: {scenario_path}")

        self._game.load_config(str(scenario_path))
        self._configure_game()

        # Tracking state
        self._initial_health = 100
        self._prev_health = 100
        self._prev_kills = 0
        self._prev_ammo = 26  # fallback, overridden dynamically in start_episode
        self._shots_fired = 0
        self._hits = 0
        self._damage_dealt = 0.0
        self._damage_taken = 0.0
        self._visited_positions: set[tuple[int, int]] = set()
        self._tick = 0

        # NOTE on AMMO2 tracking limitations:
        # - Pistol scenarios use AMMO5 (clips), not AMMO2 (cells), so shots_fired
        #   via AMMO2 delta won't work for pistol-only scenarios.
        # - defend_the_line: enemies drop ammo pickups, so AMMO2 can *increase*
        #   mid-episode. The ammo_used = pre - post delta only counts decreases,
        #   so shots_fired will undercount when pickups occur on the same tick.
        #   ammo_efficiency and shots_fired are unreliable for this scenario.

    def _configure_game(self) -> None:
        """Configure VizDoom for headless experiment execution."""
        self._game.set_window_visible(False)
        self._game.set_sound_enabled(False)
        self._game.set_screen_resolution(
            self._vizdoom.ScreenResolution.RES_320X240
        )
        self._game.set_screen_format(self._vizdoom.ScreenFormat.GRAY8)
        self._game.set_mode(self._vizdoom.Mode.PLAYER)

        # defend_the_center uses: MOVE_LEFT, MOVE_RIGHT, ATTACK
        # These are already defined in the .cfg file

        # CRITICAL FIX: Override game variables to ensure correct index mapping
        # The defend_the_center.cfg defines: available_game_variables = { AMMO2 HEALTH }
        # which would give us only [AMMO2, HEALTH] (2 elements, missing KILLCOUNT!)
        # We MUST explicitly set the correct order BEFORE init()
        self._game.clear_available_game_variables()
        self._game.add_available_game_variable(self._vizdoom.GameVariable.KILLCOUNT)  # index 0
        self._game.add_available_game_variable(self._vizdoom.GameVariable.HEALTH)     # index 1
        self._game.add_available_game_variable(self._vizdoom.GameVariable.AMMO2)      # index 2

        self._game.set_episode_timeout(self._episode_timeout)
        self._game.init()

    def start_episode(self, seed: int) -> None:
        """Start new episode with fixed seed for reproducibility."""
        self._game.set_seed(seed)
        self._game.new_episode()

        # Reset tracking
        self._prev_health = 100
        self._prev_kills = 0
        self._shots_fired = 0
        self._hits = 0
        self._damage_dealt = 0.0
        self._damage_taken = 0.0
        self._visited_positions = set()
        self._tick = 0

        # Detect starting ammo dynamically from first frame
        state = self._game.get_state()
        if state and state.game_variables is not None:
            self._prev_ammo = int(state.game_variables[2])  # AMMO2 at index 2
        else:
            self._prev_ammo = 26  # fallback

    def get_game_state(self) -> GameState:
        """Extract current game state."""
        state = self._game.get_state()
        if state is None:
            return GameState(is_dead=True, tick=self._tick)

        game_vars = state.game_variables  # [KILLCOUNT, HEALTH, AMMO2]
        kills = int(game_vars[0]) if len(game_vars) > 0 else 0
        health = int(game_vars[1]) if len(game_vars) > 1 else 0
        ammo = int(game_vars[2]) if len(game_vars) > 2 else 0

        return GameState(
            health=health,
            ammo=ammo,
            kills=kills,
            episode_time=self._tick / 35.0,  # VizDoom runs at 35 fps
            is_dead=self._game.is_player_dead(),
            tick=self._tick,
        )

    def make_action(self, action_index: int) -> float:
        """Execute action. Returns step reward."""
        # Encode as 1-hot vector for VizDoom
        action = [0] * self._num_actions
        if 0 <= action_index < self._num_actions:
            action[action_index] = 1

        # Track pre-action state for delta computation
        pre_state = self._game.get_state()
        pre_kills = 0
        pre_ammo = 26
        pre_health = 100
        if pre_state and pre_state.game_variables is not None:
            gv = pre_state.game_variables
            pre_kills = int(gv[0]) if len(gv) > 0 else 0
            pre_health = int(gv[1]) if len(gv) > 1 else 100
            pre_ammo = int(gv[2]) if len(gv) > 2 else 26

        reward = self._game.make_action(action)
        self._tick += 1

        # Track deltas
        post_state = self._game.get_state()
        if post_state and post_state.game_variables is not None:
            gv = post_state.game_variables
            post_kills = int(gv[0]) if len(gv) > 0 else 0
            post_health = int(gv[1]) if len(gv) > 1 else 100
            post_ammo = int(gv[2]) if len(gv) > 2 else 26

            # Track kills
            new_kills = post_kills - pre_kills
            if new_kills > 0:
                self._hits += new_kills
                self._damage_dealt += new_kills * 100  # approximate

            # Track damage taken
            health_lost = pre_health - post_health
            if health_lost > 0:
                self._damage_taken += health_lost

            # Track ammo usage
            ammo_used = pre_ammo - post_ammo
            if ammo_used > 0:
                self._shots_fired += ammo_used

            self._prev_kills = post_kills
            self._prev_health = post_health
            self._prev_ammo = post_ammo

        return reward

    def is_episode_finished(self) -> bool:
        return self._game.is_episode_finished()

    def get_episode_metrics(self) -> EpisodeMetrics:
        """Compute final episode metrics."""
        survival_time = self._tick / 35.0  # seconds
        kill_rate = (
            (self._prev_kills / (survival_time / 60.0))
            if survival_time > 0
            else 0.0
        )
        ammo_eff = (
            (self._hits / self._shots_fired)
            if self._shots_fired > 0
            else 0.0
        )

        return EpisodeMetrics(
            kills=self._prev_kills,
            survival_time=survival_time,
            damage_dealt=self._damage_dealt,
            damage_taken=self._damage_taken,
            ammo_efficiency=ammo_eff,
            exploration_coverage=0.0,  # TODO: implement cell tracking
            kill_rate=kill_rate,
            total_ticks=self._tick,
            shots_fired=self._shots_fired,
            hits=self._hits,
            cells_visited=len(self._visited_positions),
        )

    def close(self) -> None:
        self._game.close()
