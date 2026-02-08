//! gRPC server implementing the AgentService from agent.proto.
//!
//! Wraps the DecisionCascade behind a tokio Mutex for safe
//! concurrent access from tonic's async handlers.

use std::sync::Arc;
use tokio::sync::Mutex;

use tonic::{Request, Response, Status};

use crate::cascade::{CascadeConfig, DecisionCascade};
use crate::game;

pub mod proto {
    tonic::include_proto!("clau_doom.agent");
}

use proto::agent_service_server::AgentService;
use proto::{Action as ProtoAction, GameState as ProtoGameState};

/// Convert internal Action -> proto ActionType.
fn action_to_proto(action: game::Action) -> i32 {
    match action {
        game::Action::MoveLeft => proto::ActionType::MoveLeft as i32,
        game::Action::MoveRight => proto::ActionType::MoveRight as i32,
        game::Action::Attack => proto::ActionType::Attack as i32,
    }
}

/// Convert proto GameState -> internal GameState.
fn proto_to_game_state(proto: &ProtoGameState) -> game::GameState {
    game::GameState {
        health: proto.health,
        ammo: proto.ammo,
        kills: proto.kills,
        enemies_visible: proto.enemies_visible,
        position_x: proto.position_x,
        position_y: proto.position_y,
        position_z: proto.position_z,
        angle: proto.angle,
        episode_time: proto.episode_time,
        is_dead: proto.is_dead,
        tick: proto.tick,
    }
}

/// Parse cascade_mode string into CascadeConfig.
/// Returns None if the string is empty (use server default).
fn parse_cascade_mode(mode: &str) -> Option<CascadeConfig> {
    match mode {
        "random" => Some(CascadeConfig::random()),
        "rule_only" => Some(CascadeConfig::rule_only()),
        "full_agent" => Some(CascadeConfig::full_agent()),
        _ => None,
    }
}

/// gRPC server wrapping the DecisionCascade engine.
pub struct AgentServer {
    cascade: Arc<Mutex<DecisionCascade>>,
    /// Default config used when per-request override is not provided.
    default_config: CascadeConfig,
    health_threshold: f32,
    opensearch_url: String,
    seed: u64,
}

impl AgentServer {
    pub fn new(
        cascade: DecisionCascade,
        default_config: CascadeConfig,
        health_threshold: f32,
        opensearch_url: String,
        seed: u64,
    ) -> Self {
        Self {
            cascade: Arc::new(Mutex::new(cascade)),
            default_config,
            health_threshold,
            opensearch_url,
            seed,
        }
    }
}

#[tonic::async_trait]
impl AgentService for AgentServer {
    async fn tick(
        &self,
        request: Request<ProtoGameState>,
    ) -> Result<Response<ProtoAction>, Status> {
        let proto_state = request.into_inner();
        let game_state = proto_to_game_state(&proto_state);

        // Per-request cascade_mode override for DOE flexibility.
        let decision = if !proto_state.cascade_mode.is_empty() {
            if let Some(override_config) = parse_cascade_mode(&proto_state.cascade_mode) {
                let mut temp_cascade = DecisionCascade::new(
                    override_config,
                    self.health_threshold,
                    self.opensearch_url.clone(),
                    self.seed,
                    ":memory:",  // Per-request override uses in-memory cache
                );
                temp_cascade.decide(&game_state).await
            } else {
                return Err(Status::invalid_argument(format!(
                    "unknown cascade_mode: '{}'. expected: random, rule_only, full_agent",
                    proto_state.cascade_mode
                )));
            }
        } else {
            let mut cascade = self.cascade.lock().await;
            cascade.decide(&game_state).await
        };

        let action = ProtoAction {
            action_type: action_to_proto(decision.action),
            decision_level: decision.decision_level as i32,
            latency_ms: decision.latency_ns as f32 / 1_000_000.0,
            confidence: decision.confidence,
            rule_matched: decision.rule_matched.unwrap_or_default(),
        };

        Ok(Response::new(action))
    }

    type StreamTickStream = futures_core::stream::BoxStream<
        'static,
        Result<ProtoAction, Status>,
    >;

    async fn stream_tick(
        &self,
        _request: Request<tonic::Streaming<ProtoGameState>>,
    ) -> Result<Response<Self::StreamTickStream>, Status> {
        Err(Status::unimplemented(
            "StreamTick not yet implemented; use unary Tick RPC",
        ))
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_action_to_proto_mapping() {
        assert_eq!(
            action_to_proto(game::Action::MoveLeft),
            proto::ActionType::MoveLeft as i32
        );
        assert_eq!(
            action_to_proto(game::Action::MoveRight),
            proto::ActionType::MoveRight as i32
        );
        assert_eq!(
            action_to_proto(game::Action::Attack),
            proto::ActionType::Attack as i32
        );
    }

    #[test]
    fn test_proto_to_game_state_conversion() {
        let proto = ProtoGameState {
            health: 75,
            ammo: 20,
            kills: 3,
            enemies_visible: 2,
            position_x: 1.0,
            position_y: 2.0,
            position_z: 3.0,
            angle: 90.0,
            episode_time: 45.5,
            is_dead: false,
            tick: 100,
            cascade_mode: String::new(),
        };
        let gs = proto_to_game_state(&proto);
        assert_eq!(gs.health, 75);
        assert_eq!(gs.ammo, 20);
        assert_eq!(gs.kills, 3);
        assert_eq!(gs.enemies_visible, 2);
        assert!((gs.position_x - 1.0).abs() < f32::EPSILON);
        assert!((gs.angle - 90.0).abs() < f32::EPSILON);
        assert!(!gs.is_dead);
        assert_eq!(gs.tick, 100);
    }

    #[test]
    fn test_parse_cascade_mode() {
        let random = parse_cascade_mode("random").unwrap();
        assert!(random.random_mode);

        let rule_only = parse_cascade_mode("rule_only").unwrap();
        assert!(rule_only.l0_enabled);
        assert!(!rule_only.l1_enabled);

        let full = parse_cascade_mode("full_agent").unwrap();
        assert!(full.l0_enabled);
        assert!(full.l1_enabled);
        assert!(full.l2_enabled);

        assert!(parse_cascade_mode("").is_none());
        assert!(parse_cascade_mode("invalid").is_none());
    }
}
