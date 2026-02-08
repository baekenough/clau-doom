//! Level 0 rule engine: hardcoded reflexes from agent MD definitions.
//!
//! Rules are condition-action pairs compiled at startup from the agent's
//! MD file. Decisions at this level complete in < 1ms.

use std::time::Instant;

use crate::game::{Action, Decision, GameState};

/// A single rule: condition predicate -> action.
#[derive(Debug, Clone)]
pub struct Rule {
    pub name: String,
    pub condition: RuleCondition,
    pub action: Action,
    pub priority: u8, // higher = checked first
}

/// Rule conditions that can be evaluated against game state.
#[derive(Debug, Clone)]
pub enum RuleCondition {
    /// Health below threshold (fraction 0.0-1.0)
    HealthBelow(f32),
    /// Health above threshold
    HealthAbove(f32),
    /// Enemies visible count >= N
    EnemiesAtLeast(i32),
    /// No enemies visible
    NoEnemies,
    /// Ammo below threshold
    AmmoBelow(i32),
    /// Compound: all conditions must be true
    And(Vec<RuleCondition>),
    /// Compound: any condition must be true
    Or(Vec<RuleCondition>),
}

impl RuleCondition {
    pub fn evaluate(&self, state: &GameState) -> bool {
        match self {
            RuleCondition::HealthBelow(threshold) => state.health_fraction() < *threshold,
            RuleCondition::HealthAbove(threshold) => state.health_fraction() > *threshold,
            RuleCondition::EnemiesAtLeast(n) => state.enemies_visible >= *n,
            RuleCondition::NoEnemies => state.enemies_visible == 0,
            RuleCondition::AmmoBelow(n) => state.ammo < *n,
            RuleCondition::And(conditions) => conditions.iter().all(|c| c.evaluate(state)),
            RuleCondition::Or(conditions) => conditions.iter().any(|c| c.evaluate(state)),
        }
    }
}

/// Level 0 rule engine. Compiled rules sorted by priority.
pub struct RuleEngine {
    rules: Vec<Rule>,
    enabled: bool,
}

impl RuleEngine {
    pub fn new(enabled: bool) -> Self {
        Self {
            rules: Vec::new(),
            enabled,
        }
    }

    /// Create with default defend_the_center rules.
    pub fn with_default_rules(enabled: bool, health_threshold: f32) -> Self {
        let mut engine = Self::new(enabled);

        // Emergency retreat: low health -> dodge
        engine.add_rule(Rule {
            name: "emergency_retreat".to_string(),
            condition: RuleCondition::HealthBelow(health_threshold),
            action: Action::MoveLeft, // Dodge to avoid damage
            priority: 100,
        });

        // Attack when enemies visible
        engine.add_rule(Rule {
            name: "attack_visible_enemy".to_string(),
            condition: RuleCondition::EnemiesAtLeast(1),
            action: Action::Attack,
            priority: 50,
        });

        // Move when no enemies (explore/reposition)
        engine.add_rule(Rule {
            name: "reposition_no_enemies".to_string(),
            condition: RuleCondition::NoEnemies,
            action: Action::MoveLeft, // Rotate to find enemies
            priority: 10,
        });

        engine
    }

    pub fn add_rule(&mut self, rule: Rule) {
        self.rules.push(rule);
        self.rules.sort_by(|a, b| b.priority.cmp(&a.priority));
    }

    /// Evaluate rules against game state. Returns first matching rule's action.
    pub fn evaluate(&self, state: &GameState) -> Option<Decision> {
        if !self.enabled {
            return None;
        }

        let start = Instant::now();

        for rule in &self.rules {
            if rule.condition.evaluate(state) {
                let elapsed = start.elapsed();
                return Some(Decision {
                    action: rule.action,
                    decision_level: 0,
                    confidence: 1.0, // Rules are deterministic
                    latency_ns: elapsed.as_nanos() as u64,
                    rule_matched: Some(rule.name.clone()),
                });
            }
        }

        None
    }

    pub fn is_enabled(&self) -> bool {
        self.enabled
    }

    pub fn set_enabled(&mut self, enabled: bool) {
        self.enabled = enabled;
    }

    pub fn rule_count(&self) -> usize {
        self.rules.len()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_state(health: i32, enemies: i32, ammo: i32) -> GameState {
        GameState {
            health,
            ammo,
            kills: 0,
            enemies_visible: enemies,
            position_x: 0.0,
            position_y: 0.0,
            position_z: 0.0,
            angle: 0.0,
            episode_time: 0.0,
            is_dead: false,
            tick: 0,
        }
    }

    #[test]
    fn test_emergency_retreat() {
        let engine = RuleEngine::with_default_rules(true, 0.3);
        let state = make_state(20, 3, 50); // health 20% < 30% threshold
        let decision = engine.evaluate(&state).expect("Should match");
        assert_eq!(decision.decision_level, 0);
        assert_eq!(
            decision.rule_matched,
            Some("emergency_retreat".to_string())
        );
    }

    #[test]
    fn test_attack_visible_enemy() {
        let engine = RuleEngine::with_default_rules(true, 0.3);
        let state = make_state(80, 2, 50); // healthy, enemies visible
        let decision = engine.evaluate(&state).expect("Should match");
        assert_eq!(decision.action, Action::Attack);
        assert_eq!(
            decision.rule_matched,
            Some("attack_visible_enemy".to_string())
        );
    }

    #[test]
    fn test_reposition_no_enemies() {
        let engine = RuleEngine::with_default_rules(true, 0.3);
        let state = make_state(80, 0, 50); // healthy, no enemies
        let decision = engine.evaluate(&state).expect("Should match");
        assert_eq!(
            decision.rule_matched,
            Some("reposition_no_enemies".to_string())
        );
    }

    #[test]
    fn test_disabled_engine() {
        let engine = RuleEngine::with_default_rules(false, 0.3);
        let state = make_state(20, 3, 50);
        assert!(engine.evaluate(&state).is_none());
    }

    #[test]
    fn test_latency_under_1ms() {
        let engine = RuleEngine::with_default_rules(true, 0.3);
        let state = make_state(50, 2, 30);
        let decision = engine.evaluate(&state).expect("Should match");
        // L0 must be < 1ms = 1_000_000 ns
        assert!(
            decision.latency_ns < 1_000_000,
            "L0 latency too high: {}ns",
            decision.latency_ns
        );
    }

    #[test]
    fn test_compound_and_condition() {
        let mut engine = RuleEngine::new(true);
        engine.add_rule(Rule {
            name: "low_health_and_enemies".to_string(),
            condition: RuleCondition::And(vec![
                RuleCondition::HealthBelow(0.5),
                RuleCondition::EnemiesAtLeast(2),
            ]),
            action: Action::MoveRight,
            priority: 90,
        });

        // Both conditions met
        let state = make_state(30, 3, 50);
        let decision = engine.evaluate(&state).expect("Should match");
        assert_eq!(decision.action, Action::MoveRight);

        // Only one condition met (health OK)
        let state = make_state(80, 3, 50);
        assert!(engine.evaluate(&state).is_none());
    }

    #[test]
    fn test_compound_or_condition() {
        let mut engine = RuleEngine::new(true);
        engine.add_rule(Rule {
            name: "danger_any".to_string(),
            condition: RuleCondition::Or(vec![
                RuleCondition::HealthBelow(0.2),
                RuleCondition::AmmoBelow(5),
            ]),
            action: Action::MoveLeft,
            priority: 80,
        });

        // Low health triggers
        let state = make_state(10, 0, 50);
        assert!(engine.evaluate(&state).is_some());

        // Low ammo triggers
        let state = make_state(80, 0, 3);
        assert!(engine.evaluate(&state).is_some());

        // Neither triggers
        let state = make_state(80, 0, 50);
        assert!(engine.evaluate(&state).is_none());
    }

    #[test]
    fn test_priority_ordering() {
        let mut engine = RuleEngine::new(true);

        engine.add_rule(Rule {
            name: "low_priority".to_string(),
            condition: RuleCondition::EnemiesAtLeast(1),
            action: Action::MoveRight,
            priority: 10,
        });
        engine.add_rule(Rule {
            name: "high_priority".to_string(),
            condition: RuleCondition::EnemiesAtLeast(1),
            action: Action::Attack,
            priority: 90,
        });

        let state = make_state(50, 2, 50);
        let decision = engine.evaluate(&state).expect("Should match");
        assert_eq!(decision.action, Action::Attack);
        assert_eq!(decision.rule_matched, Some("high_priority".to_string()));
    }

    #[test]
    fn test_rule_count() {
        let engine = RuleEngine::with_default_rules(true, 0.3);
        assert_eq!(engine.rule_count(), 3);
    }

    #[test]
    fn test_set_enabled() {
        let mut engine = RuleEngine::with_default_rules(true, 0.3);
        assert!(engine.is_enabled());
        engine.set_enabled(false);
        assert!(!engine.is_enabled());
        let state = make_state(20, 3, 50);
        assert!(engine.evaluate(&state).is_none());
    }
}
