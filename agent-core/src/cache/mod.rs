//! Level 1 cache: DuckDB in-process action cache.
//!
//! Caches L2 OpenSearch results for fast repeated lookups.
//! Target latency: < 10ms P99.

use duckdb::{Connection, params};
use crate::game::{Action, Decision, GameState};

/// Discretize game state into a cache key.
/// Groups states into ~1100 unique buckets:
/// - health: bucket by 10 (0-10 bins)
/// - ammo: bucket by 5 (0-20 bins, capped at 100)
/// - enemies_visible: raw (0-5 range)
pub fn state_hash(state: &GameState) -> i64 {
    let h = (state.health / 10).min(10) as i64;
    let a = (state.ammo / 5).min(20) as i64;
    let e = state.enemies_visible.min(5) as i64;
    h * 200 + a * 6 + e  // max: 10*200 + 20*6 + 5 = 2125
}

pub struct CacheClient {
    conn: Connection,
    enabled: bool,
}

impl CacheClient {
    /// Create a new cache client with DuckDB at the given path.
    /// If path is ":memory:", uses in-memory database.
    pub fn new(enabled: bool, db_path: &str) -> Result<Self, duckdb::Error> {
        let conn = if db_path == ":memory:" {
            Connection::open_in_memory()?
        } else {
            Connection::open(db_path)?
        };

        // Create schema if not exists
        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS action_cache (
                state_hash BIGINT PRIMARY KEY,
                action_index INTEGER NOT NULL,
                confidence FLOAT NOT NULL,
                source_doc_id TEXT NOT NULL,
                hit_count INTEGER NOT NULL DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_accessed TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )"
        )?;

        Ok(Self { conn, enabled })
    }

    pub fn is_enabled(&self) -> bool {
        self.enabled
    }

    /// Look up cached action for a game state. Returns Decision with level=1 if found.
    pub fn lookup(&self, state: &GameState) -> Option<Decision> {
        if !self.enabled {
            return None;
        }

        let hash = state_hash(state);

        let result = self.conn.query_row(
            "SELECT action_index, confidence, source_doc_id FROM action_cache WHERE state_hash = ?",
            params![hash],
            |row| {
                let action_index: i32 = row.get(0)?;
                let confidence: f32 = row.get(1)?;
                let source_doc_id: String = row.get(2)?;
                Ok((action_index, confidence, source_doc_id))
            },
        );

        match result {
            Ok((action_index, confidence, source_doc_id)) => {
                // Update hit count and last_accessed
                let _ = self.conn.execute(
                    "UPDATE action_cache SET hit_count = hit_count + 1, last_accessed = CURRENT_TIMESTAMP WHERE state_hash = ?",
                    params![hash],
                );

                let action = Action::from_index(action_index).unwrap_or(Action::Attack);
                Some(Decision {
                    action,
                    decision_level: 1,
                    confidence,
                    latency_ns: 0, // Will be filled by cascade
                    rule_matched: Some(format!("L1:{}", source_doc_id)),
                })
            }
            Err(_) => None,
        }
    }

    /// Insert an L2 result into the cache for future L1 lookups.
    pub fn insert(&self, state: &GameState, decision: &Decision) {
        if !self.enabled {
            return;
        }

        let hash = state_hash(state);
        let action_index = decision.action.to_index();
        let source = decision.rule_matched.as_deref().unwrap_or("unknown");

        // INSERT OR REPLACE (upsert)
        let _ = self.conn.execute(
            "INSERT OR REPLACE INTO action_cache (state_hash, action_index, confidence, source_doc_id, hit_count) VALUES (?, ?, ?, ?, 0)",
            params![hash, action_index, decision.confidence, source],
        );
    }

    /// Get cache statistics.
    pub fn stats(&self) -> CacheStats {
        let total: i64 = self.conn
            .query_row("SELECT COUNT(*) FROM action_cache", [], |row| row.get(0))
            .unwrap_or(0);
        let total_hits: i64 = self.conn
            .query_row("SELECT COALESCE(SUM(hit_count), 0) FROM action_cache", [], |row| row.get(0))
            .unwrap_or(0);
        CacheStats {
            entries: total as usize,
            total_hits: total_hits as usize,
        }
    }
}

pub struct CacheStats {
    pub entries: usize,
    pub total_hits: usize,
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_state(health: i32, ammo: i32, enemies: i32) -> GameState {
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
    fn test_state_hash_buckets() {
        // Different states should produce different hashes
        let s1 = make_state(50, 25, 2);
        let s2 = make_state(60, 30, 3);
        let s3 = make_state(20, 10, 1);

        let h1 = state_hash(&s1);
        let h2 = state_hash(&s2);
        let h3 = state_hash(&s3);

        assert_ne!(h1, h2);
        assert_ne!(h2, h3);
        assert_ne!(h1, h3);
    }

    #[test]
    fn test_state_hash_same_bucket() {
        // Similar states within same bucket should produce same hash
        let s1 = make_state(51, 25, 2);
        let s2 = make_state(59, 27, 2);  // Same bucket (50-59 health, 25-29 ammo, 2 enemies)

        assert_eq!(state_hash(&s1), state_hash(&s2));
    }

    #[test]
    fn test_cache_insert_and_lookup() {
        let cache = CacheClient::new(true, ":memory:").unwrap();
        let state = make_state(50, 30, 2);

        let decision = Decision {
            action: Action::Attack,
            decision_level: 2,
            confidence: 0.85,
            latency_ns: 0,
            rule_matched: Some("test_doc".to_string()),
        };

        cache.insert(&state, &decision);

        let retrieved = cache.lookup(&state).unwrap();
        assert_eq!(retrieved.action, Action::Attack);
        assert_eq!(retrieved.decision_level, 1);  // L1 cache level
        assert!((retrieved.confidence - 0.85).abs() < f32::EPSILON);
        assert_eq!(retrieved.rule_matched, Some("L1:test_doc".to_string()));
    }

    #[test]
    fn test_cache_miss() {
        let cache = CacheClient::new(true, ":memory:").unwrap();
        let state = make_state(50, 30, 2);

        assert!(cache.lookup(&state).is_none());
    }

    #[test]
    fn test_cache_disabled() {
        let cache = CacheClient::new(false, ":memory:").unwrap();
        let state = make_state(50, 30, 2);

        let decision = Decision {
            action: Action::MoveLeft,
            decision_level: 2,
            confidence: 0.9,
            latency_ns: 0,
            rule_matched: Some("doc".to_string()),
        };

        cache.insert(&state, &decision);
        assert!(cache.lookup(&state).is_none());  // Disabled, no lookup
    }

    #[test]
    fn test_cache_hit_count_increment() {
        let cache = CacheClient::new(true, ":memory:").unwrap();
        let state = make_state(50, 30, 2);

        let decision = Decision {
            action: Action::MoveRight,
            decision_level: 2,
            confidence: 0.75,
            latency_ns: 0,
            rule_matched: Some("doc2".to_string()),
        };

        cache.insert(&state, &decision);

        // First lookup
        cache.lookup(&state);
        // Second lookup
        cache.lookup(&state);

        // Check hit count
        let hash = state_hash(&state);
        let hit_count: i32 = cache.conn
            .query_row(
                "SELECT hit_count FROM action_cache WHERE state_hash = ?",
                params![hash],
                |row| row.get(0),
            )
            .unwrap();

        assert_eq!(hit_count, 2);
    }

    #[test]
    fn test_cache_stats() {
        let cache = CacheClient::new(true, ":memory:").unwrap();

        // Insert 3 different states
        for i in 0..3 {
            let state = make_state(50 + i * 10, 30, 2);
            let decision = Decision {
                action: Action::Attack,
                decision_level: 2,
                confidence: 0.8,
                latency_ns: 0,
                rule_matched: Some(format!("doc{}", i)),
            };
            cache.insert(&state, &decision);
        }

        // Lookup first state twice
        let state0 = make_state(50, 30, 2);
        cache.lookup(&state0);
        cache.lookup(&state0);

        let stats = cache.stats();
        assert_eq!(stats.entries, 3);
        assert_eq!(stats.total_hits, 2);
    }
}
