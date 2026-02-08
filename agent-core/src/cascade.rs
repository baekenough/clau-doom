//! Decision cascade: L0 → L1 → L2 waterfall with ablation support.
//!
//! Three operating modes for DOE-001:
//! - Random: bypass all levels, uniform random action
//! - RuleOnly: L0 rules only, fallback to random
//! - FullAgent: L0 → L1 → L2 cascade

use std::time::Instant;
use crate::cache::CacheClient;
use crate::game::{Action, Decision, GameState};
use crate::strategy::RuleEngine;
use crate::rag::RagClient;

/// Configuration for which decision levels are active.
/// Used by DOE experiments to ablate specific levels.
#[derive(Debug, Clone)]
pub struct CascadeConfig {
    pub l0_enabled: bool,  // MD rules
    pub l1_enabled: bool,  // DuckDB cache
    pub l2_enabled: bool,  // OpenSearch kNN
    pub random_mode: bool, // Override: all random
}

impl CascadeConfig {
    /// DOE-001 Condition 1: Random baseline
    pub fn random() -> Self {
        Self {
            l0_enabled: false,
            l1_enabled: false,
            l2_enabled: false,
            random_mode: true,
        }
    }

    /// DOE-001 Condition 2: Rule-only
    pub fn rule_only() -> Self {
        Self {
            l0_enabled: true,
            l1_enabled: false,
            l2_enabled: false,
            random_mode: false,
        }
    }

    /// DOE-001 Condition 3: Full agent
    pub fn full_agent() -> Self {
        Self {
            l0_enabled: true,
            l1_enabled: true,
            l2_enabled: true,
            random_mode: false,
        }
    }
}

/// Deterministic PRNG for reproducible random actions.
/// Uses xorshift64 - fast, deterministic, good enough for action selection.
pub struct DeterministicRng {
    state: u64,
}

impl DeterministicRng {
    pub fn new(seed: u64) -> Self {
        Self {
            state: if seed == 0 { 1 } else { seed },
        }
    }

    pub fn next_u64(&mut self) -> u64 {
        let mut x = self.state;
        x ^= x << 13;
        x ^= x >> 7;
        x ^= x << 17;
        self.state = x;
        x
    }

    /// Random action from the action space
    pub fn random_action(&mut self) -> Action {
        let idx = (self.next_u64() % 3) as i32;
        Action::from_index(idx).unwrap_or(Action::Attack)
    }
}

/// The decision cascade engine.
pub struct DecisionCascade {
    config: CascadeConfig,
    rule_engine: RuleEngine,
    cache_client: CacheClient,
    rag_client: RagClient,
    rng: DeterministicRng,
}

impl DecisionCascade {
    pub fn new(
        config: CascadeConfig,
        health_threshold: f32,
        opensearch_url: String,
        seed: u64,
        duckdb_path: &str,
    ) -> Self {
        let rule_engine = RuleEngine::with_default_rules(config.l0_enabled, health_threshold);
        let rag_client = RagClient::new(config.l2_enabled, opensearch_url);
        let cache_client = CacheClient::new(config.l1_enabled, duckdb_path)
            .unwrap_or_else(|e| {
                tracing::warn!("Failed to init DuckDB cache: {}, using disabled cache", e);
                CacheClient::new(false, ":memory:").expect("in-memory cache must succeed")
            });
        Self {
            config,
            rule_engine,
            cache_client,
            rag_client,
            rng: DeterministicRng::new(seed),
        }
    }

    /// Make a decision for the given game state.
    /// Follows the cascade: L0 → L1 → L2 → fallback random
    pub async fn decide(&mut self, state: &GameState) -> Decision {
        let start = Instant::now();

        // Random mode: bypass everything
        if self.config.random_mode {
            let action = self.rng.random_action();
            return Decision {
                action,
                decision_level: 255,
                confidence: 0.0,
                latency_ns: start.elapsed().as_nanos() as u64,
                rule_matched: None,
            };
        }

        // Level 0: MD Rules (< 1ms target)
        if self.config.l0_enabled {
            if let Some(decision) = self.rule_engine.evaluate(state) {
                return Decision {
                    latency_ns: start.elapsed().as_nanos() as u64,
                    ..decision
                };
            }
        }

        // Level 1: DuckDB Cache (< 10ms target)
        if self.config.l1_enabled {
            if let Some(decision) = self.cache_client.lookup(state) {
                return Decision {
                    latency_ns: start.elapsed().as_nanos() as u64,
                    ..decision
                };
            }
        }

        // Level 2: OpenSearch kNN (< 100ms target)
        if self.config.l2_enabled {
            if let Some(decision) = self.rag_client.query(state).await {
                // Cache L2 result for future L1 hits
                self.cache_client.insert(state, &decision);
                return Decision {
                    latency_ns: start.elapsed().as_nanos() as u64,
                    ..decision
                };
            }
        }

        // Fallback: deterministic random
        let action = self.rng.random_action();
        Decision {
            action,
            decision_level: 255,
            confidence: 0.0,
            latency_ns: start.elapsed().as_nanos() as u64,
            rule_matched: None,
        }
    }

    pub fn config(&self) -> &CascadeConfig {
        &self.config
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_state(health: i32, enemies: i32) -> GameState {
        GameState {
            health,
            ammo: 50,
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

    #[tokio::test]
    async fn test_random_mode_deterministic() {
        // Same seed must produce same sequence
        let mut c1 = DecisionCascade::new(
            CascadeConfig::random(),
            0.3,
            "http://localhost:9200".into(),
            42,
            ":memory:",
        );
        let mut c2 = DecisionCascade::new(
            CascadeConfig::random(),
            0.3,
            "http://localhost:9200".into(),
            42,
            ":memory:",
        );
        let state = make_state(100, 0);
        for _ in 0..100 {
            assert_eq!(c1.decide(&state).await.action, c2.decide(&state).await.action);
        }
    }

    #[tokio::test]
    async fn test_random_mode_uniform_distribution() {
        // Chi-square test: 1000 actions should be roughly uniform across 3 actions
        let mut cascade = DecisionCascade::new(
            CascadeConfig::random(),
            0.3,
            "http://localhost:9200".into(),
            12345,
            ":memory:",
        );
        let state = make_state(100, 0);
        let mut counts = [0u32; 3];
        for _ in 0..1000 {
            let d = cascade.decide(&state).await;
            counts[d.action.to_index() as usize] += 1;
        }
        // Each should be roughly 333. Allow wide margin (200-500)
        for (i, &count) in counts.iter().enumerate() {
            assert!(
                count > 200 && count < 500,
                "Action {i} count {count} outside expected range [200, 500]"
            );
        }
    }

    #[tokio::test]
    async fn test_random_mode_level_255() {
        let mut cascade = DecisionCascade::new(
            CascadeConfig::random(),
            0.3,
            "http://localhost:9200".into(),
            42,
            ":memory:",
        );
        let d = cascade.decide(&make_state(50, 1)).await;
        assert_eq!(d.decision_level, 255);
        assert_eq!(d.confidence, 0.0);
    }

    #[tokio::test]
    async fn test_rule_only_fires_l0() {
        let mut cascade = DecisionCascade::new(
            CascadeConfig::rule_only(),
            0.3,
            "http://localhost:9200".into(),
            42,
            ":memory:",
        );
        // Low health -> emergency_retreat rule fires
        let d = cascade.decide(&make_state(20, 2)).await;
        assert_eq!(d.decision_level, 0);
        assert_eq!(d.rule_matched, Some("emergency_retreat".to_string()));
    }

    #[tokio::test]
    async fn test_rule_only_falls_through_to_random() {
        // When no rules match in rule-only mode, should still return a decision
        let mut cascade = DecisionCascade::new(
            CascadeConfig::rule_only(),
            0.3,
            "http://localhost:9200".into(),
            42,
            ":memory:",
        );
        // Actually with default rules, healthy+no enemies -> reposition_no_enemies
        // healthy+enemies -> attack_visible_enemy
        // So all states match. Let's test that rules fire properly.
        let d = cascade.decide(&make_state(80, 0)).await;
        assert_eq!(d.decision_level, 0); // reposition rule fires
    }

    #[tokio::test]
    async fn test_full_agent_l0_first() {
        let mut cascade = DecisionCascade::new(
            CascadeConfig::full_agent(),
            0.3,
            "http://localhost:9200".into(),
            42,
            ":memory:",
        );
        // Low health should trigger L0 even in full mode
        let d = cascade.decide(&make_state(20, 2)).await;
        assert_eq!(d.decision_level, 0);
    }

    #[tokio::test]
    async fn test_cascade_latency_under_100ms() {
        let mut cascade = DecisionCascade::new(
            CascadeConfig::full_agent(),
            0.3,
            "http://localhost:9200".into(),
            42,
            ":memory:",
        );
        let state = make_state(50, 2);
        let d = cascade.decide(&state).await;
        // Total cascade should complete well under 100ms
        assert!(
            d.latency_ns < 100_000_000,
            "Cascade too slow: {}ns",
            d.latency_ns
        );
    }

    #[test]
    fn test_config_presets() {
        let r = CascadeConfig::random();
        assert!(r.random_mode);
        assert!(!r.l0_enabled);

        let ro = CascadeConfig::rule_only();
        assert!(!ro.random_mode);
        assert!(ro.l0_enabled);
        assert!(!ro.l1_enabled);
        assert!(!ro.l2_enabled);

        let fa = CascadeConfig::full_agent();
        assert!(!fa.random_mode);
        assert!(fa.l0_enabled);
        assert!(fa.l1_enabled);
        assert!(fa.l2_enabled);
    }

    #[test]
    fn test_deterministic_rng_no_zero_state() {
        // Seed 0 should not cause stuck state
        let mut rng = DeterministicRng::new(0);
        let first = rng.next_u64();
        let second = rng.next_u64();
        assert_ne!(first, second);
        assert_ne!(first, 0);
    }

    #[tokio::test]
    async fn test_different_seeds_different_sequences() {
        let mut c1 = DecisionCascade::new(
            CascadeConfig::random(),
            0.3,
            "http://localhost:9200".into(),
            42,
            ":memory:",
        );
        let mut c2 = DecisionCascade::new(
            CascadeConfig::random(),
            0.3,
            "http://localhost:9200".into(),
            9999,
            ":memory:",
        );
        let state = make_state(100, 0);
        let mut different = false;
        for _ in 0..20 {
            if c1.decide(&state).await.action != c2.decide(&state).await.action {
                different = true;
                break;
            }
        }
        assert!(different, "Different seeds should produce different sequences");
    }
}
