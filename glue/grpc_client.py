"""gRPC client for Rust agent-core decision service."""

from __future__ import annotations

import logging

import grpc

from glue.proto import agent_pb2
from glue.proto.agent_pb2_grpc import AgentServiceStub
from glue.vizdoom_bridge import GameState

logger = logging.getLogger(__name__)

# Proto ActionType enum -> VizDoom action index
_ACTION_TYPE_TO_INDEX = {
    1: 0,  # MOVE_LEFT  -> ACTION_MOVE_LEFT
    2: 1,  # MOVE_RIGHT -> ACTION_MOVE_RIGHT
    7: 2,  # ATTACK     -> ACTION_ATTACK
}


class GrpcActionClient:
    """gRPC-based action selection via Rust agent-core.

    Implements ActionFn protocol (callable: GameState -> int).
    """

    def __init__(
        self,
        host: str = "localhost",
        port: int = 50051,
        cascade_mode: str = "full_agent",
    ):
        self._channel = grpc.insecure_channel(f"{host}:{port}")
        self._stub = AgentServiceStub(self._channel)
        self._cascade_mode = cascade_mode

        # Last response metadata (for episode_runner to read)
        self.last_decision_level: int = -1
        self.last_latency_ms: float = 0.0
        self.last_confidence: float = 0.0
        self.last_rule_matched: str = ""

    def __call__(self, state: GameState) -> int:
        """ActionFn protocol: convert state to gRPC call, return action index."""
        proto_state = agent_pb2.GameState(
            health=state.health,
            ammo=state.ammo,
            kills=state.kills,
            enemies_visible=state.enemies_visible,
            position_x=state.position_x,
            position_y=state.position_y,
            position_z=state.position_z,
            angle=state.angle,
            episode_time=state.episode_time,
            is_dead=state.is_dead,
            tick=state.tick,
            cascade_mode=self._cascade_mode,
        )

        response = self._stub.Tick(proto_state)

        # Store metadata for episode_runner
        self.last_decision_level = response.decision_level
        self.last_latency_ms = response.latency_ms
        self.last_confidence = response.confidence
        self.last_rule_matched = response.rule_matched

        return _ACTION_TYPE_TO_INDEX.get(response.action_type, 2)

    def close(self) -> None:
        """Close the gRPC channel."""
        self._channel.close()


def check_grpc_health(
    host: str = "localhost", port: int = 50051, timeout: float = 5.0
) -> bool:
    """Check if gRPC server is reachable."""
    try:
        channel = grpc.insecure_channel(f"{host}:{port}")
        grpc.channel_ready_future(channel).result(timeout=timeout)
        channel.close()
        return True
    except grpc.FutureTimeoutError:
        return False
