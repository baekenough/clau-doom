//! Game state types and VizDoom integration layer.
//!
//! Defines the core types shared between the Rust decision engine
//! and the Python VizDoom bridge via gRPC:
//! - `GameState`: current frame observation (health, ammo, enemies, position)
//! - `Action`: agent response for defend_the_center scenario
//! - `Decision`: action with metadata for tracking and DOE measurement

use serde::{Deserialize, Serialize};

/// Available actions in defend_the_center scenario.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Hash, Serialize, Deserialize)]
pub enum Action {
    MoveLeft,
    MoveRight,
    Attack,
}

impl Action {
    pub fn to_index(self) -> i32 {
        match self {
            Action::MoveLeft => 0,
            Action::MoveRight => 1,
            Action::Attack => 2,
        }
    }

    pub fn from_index(idx: i32) -> Option<Self> {
        match idx {
            0 => Some(Action::MoveLeft),
            1 => Some(Action::MoveRight),
            2 => Some(Action::Attack),
            _ => None,
        }
    }

    pub fn all() -> &'static [Action] {
        &[Action::MoveLeft, Action::MoveRight, Action::Attack]
    }
}

/// Current game frame observation from VizDoom.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct GameState {
    pub health: i32,
    pub ammo: i32,
    pub kills: i32,
    pub enemies_visible: i32,
    pub position_x: f32,
    pub position_y: f32,
    pub position_z: f32,
    pub angle: f32,
    pub episode_time: f32,
    pub is_dead: bool,
    pub tick: u32,
}

impl GameState {
    /// Health as fraction [0.0, 1.0]
    pub fn health_fraction(&self) -> f32 {
        (self.health as f32 / 100.0).clamp(0.0, 1.0)
    }

    /// Whether agent is in danger (low health)
    pub fn is_low_health(&self, threshold: f32) -> bool {
        self.health_fraction() < threshold
    }

    /// Whether ammo is low
    pub fn is_low_ammo(&self, threshold: i32) -> bool {
        self.ammo < threshold
    }
}

/// Decision result with metadata for tracking.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Decision {
    pub action: Action,
    pub decision_level: u8, // 0=L0 rules, 1=L1 cache, 2=L2 RAG, 255=random/fallback
    pub confidence: f32,
    pub latency_ns: u64,
    pub rule_matched: Option<String>,
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_action_round_trip() {
        for action in Action::all() {
            let idx = action.to_index();
            assert_eq!(Action::from_index(idx), Some(*action));
        }
    }

    #[test]
    fn test_action_from_invalid_index() {
        assert_eq!(Action::from_index(-1), None);
        assert_eq!(Action::from_index(3), None);
        assert_eq!(Action::from_index(100), None);
    }

    #[test]
    fn test_health_fraction() {
        let state = GameState {
            health: 50, ammo: 10, kills: 0, enemies_visible: 0,
            position_x: 0.0, position_y: 0.0, position_z: 0.0,
            angle: 0.0, episode_time: 0.0, is_dead: false, tick: 0,
        };
        assert!((state.health_fraction() - 0.5).abs() < f32::EPSILON);
    }

    #[test]
    fn test_health_fraction_clamped() {
        let over = GameState {
            health: 200, ammo: 10, kills: 0, enemies_visible: 0,
            position_x: 0.0, position_y: 0.0, position_z: 0.0,
            angle: 0.0, episode_time: 0.0, is_dead: false, tick: 0,
        };
        assert!((over.health_fraction() - 1.0).abs() < f32::EPSILON);

        let under = GameState {
            health: -10, ammo: 10, kills: 0, enemies_visible: 0,
            position_x: 0.0, position_y: 0.0, position_z: 0.0,
            angle: 0.0, episode_time: 0.0, is_dead: false, tick: 0,
        };
        assert!((under.health_fraction() - 0.0).abs() < f32::EPSILON);
    }

    #[test]
    fn test_is_low_health() {
        let state = GameState {
            health: 20, ammo: 10, kills: 0, enemies_visible: 0,
            position_x: 0.0, position_y: 0.0, position_z: 0.0,
            angle: 0.0, episode_time: 0.0, is_dead: false, tick: 0,
        };
        assert!(state.is_low_health(0.3));
        assert!(!state.is_low_health(0.1));
    }

    #[test]
    fn test_is_low_ammo() {
        let state = GameState {
            health: 100, ammo: 5, kills: 0, enemies_visible: 0,
            position_x: 0.0, position_y: 0.0, position_z: 0.0,
            angle: 0.0, episode_time: 0.0, is_dead: false, tick: 0,
        };
        assert!(state.is_low_ammo(10));
        assert!(!state.is_low_ammo(3));
    }
}
