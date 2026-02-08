//! Level 2 RAG client: OpenSearch kNN vector search.
//!
//! Target latency: < 100ms P99.

use std::time::Duration;
use crate::game::{Action, Decision, GameState};
use serde_json::{json, Value};

/// Strategy document retrieved from OpenSearch.
#[derive(Debug, Clone)]
pub struct StrategyDoc {
    pub doc_id: String,
    pub situation_tags: Vec<String>,
    pub tactic: String,
    pub weapon: String,
    pub similarity: f32,
    pub confidence: f32,
    pub recency: f32,
}

impl StrategyDoc {
    /// Weighted score using configurable weights.
    pub fn score_with(&self, weights: &ScoringWeights) -> f32 {
        weights.similarity * self.similarity
            + weights.confidence * self.confidence
            + weights.recency * self.recency
    }

    /// Weighted score with default weights: similarity(0.4) + confidence(0.4) + recency(0.2)
    pub fn score(&self) -> f32 {
        self.score_with(&ScoringWeights::default())
    }
}

/// Scoring weights for strategy document ranking.
#[derive(Debug, Clone)]
pub struct ScoringWeights {
    pub similarity: f32,
    pub confidence: f32,
    pub recency: f32,
}

impl Default for ScoringWeights {
    fn default() -> Self {
        Self {
            similarity: 0.4,
            confidence: 0.4,
            recency: 0.2,
        }
    }
}

/// Derive situation tags from game state for OpenSearch term matching.
fn derive_situation_tags(state: &GameState) -> Vec<String> {
    let mut tags = Vec::new();

    // Health-based tags
    if state.health < 30 {
        tags.push("low_health".to_string());
    } else if state.health >= 80 {
        tags.push("full_health".to_string());
    }

    // Ammo-based tags
    if state.ammo < 10 {
        tags.push("low_ammo".to_string());
    } else if state.ammo >= 50 {
        tags.push("ammo_abundant".to_string());
    }

    // Enemy-based tags
    if state.enemies_visible >= 3 {
        tags.push("multi_enemy".to_string());
    } else if state.enemies_visible == 1 {
        tags.push("single_enemy".to_string());
    }

    tags
}

/// Map tactic string to Action.
fn tactic_to_action(tactic: &str) -> Action {
    if tactic.starts_with("retreat") || tactic.starts_with("kite") {
        Action::MoveLeft
    } else if tactic.starts_with("flank") {
        Action::MoveRight
    } else {
        // Default: aggressive, charge, attack, hold, cover, dodge, etc.
        Action::Attack
    }
}

/// RAG client configuration.
pub struct RagClient {
    enabled: bool,
    opensearch_url: String,
    index_name: String,
    k: usize,
    weights: ScoringWeights,
    http_client: reqwest::Client,
}

impl RagClient {
    pub fn new(enabled: bool, opensearch_url: String) -> Self {
        let http_client = reqwest::Client::builder()
            .timeout(Duration::from_millis(80))
            .pool_max_idle_per_host(5)
            .build()
            .unwrap_or_else(|_| reqwest::Client::new());

        Self {
            enabled,
            opensearch_url,
            index_name: "strategies".to_string(),
            k: 5,
            weights: ScoringWeights::default(),
            http_client,
        }
    }

    pub fn is_enabled(&self) -> bool {
        self.enabled
    }

    pub fn opensearch_url(&self) -> &str {
        &self.opensearch_url
    }

    /// Query OpenSearch for similar strategies. Returns None if disabled.
    pub async fn query(&self, state: &GameState) -> Option<Decision> {
        if !self.enabled {
            return None;
        }

        let tags = derive_situation_tags(state);
        if tags.is_empty() {
            return None;
        }

        // Build OpenSearch query
        let query_body = json!({
            "size": self.k,
            "query": {
                "bool": {
                    "should": tags.iter().map(|tag| {
                        json!({"term": {"situation_tags": tag}})
                    }).collect::<Vec<_>>(),
                    "minimum_should_match": 1,
                    "filter": [
                        {"term": {"metadata.retired": false}},
                        {"range": {"quality.trust_score": {"gte": 0.3}}}
                    ]
                }
            }
        });

        // Execute query
        let url = format!("{}/{}/_search", self.opensearch_url, self.index_name);
        let response = match self.http_client
            .post(&url)
            .json(&query_body)
            .send()
            .await
        {
            Ok(resp) => resp,
            Err(e) => {
                tracing::warn!("OpenSearch request failed: {}", e);
                return None;
            }
        };

        let body: Value = match response.json().await {
            Ok(b) => b,
            Err(e) => {
                tracing::warn!("Failed to parse OpenSearch response: {}", e);
                return None;
            }
        };

        // Parse hits
        let hits = match body["hits"]["hits"].as_array() {
            Some(h) => h,
            None => {
                tracing::warn!("No hits in OpenSearch response");
                return None;
            }
        };

        if hits.is_empty() {
            return None;
        }

        // Parse documents
        let mut docs = Vec::new();
        for hit in hits {
            let source = &hit["_source"];
            let score = hit["_score"].as_f64().unwrap_or(0.0) as f32;

            let doc = StrategyDoc {
                doc_id: source["doc_id"].as_str().unwrap_or("").to_string(),
                situation_tags: source["situation_tags"]
                    .as_array()
                    .map(|arr| {
                        arr.iter()
                            .filter_map(|v| v.as_str().map(|s| s.to_string()))
                            .collect()
                    })
                    .unwrap_or_default(),
                tactic: source["decision"]["tactic"]
                    .as_str()
                    .unwrap_or("attack")
                    .to_string(),
                weapon: source["decision"]["weapon"]
                    .as_str()
                    .unwrap_or("shotgun")
                    .to_string(),
                similarity: (score / self.k as f32).min(1.0),
                confidence: source["quality"]["trust_score"].as_f64().unwrap_or(0.5) as f32,
                recency: 0.8, // Fixed recency for seed documents
            };
            docs.push(doc);
        }

        // Score and pick best
        let best = docs
            .iter()
            .max_by(|a, b| {
                a.score_with(&self.weights)
                    .partial_cmp(&b.score_with(&self.weights))
                    .unwrap_or(std::cmp::Ordering::Equal)
            })?;

        let action = tactic_to_action(&best.tactic);

        Some(Decision {
            action,
            decision_level: 2,
            confidence: best.score_with(&self.weights),
            latency_ns: 0, // Will be filled by cascade
            rule_matched: Some(format!("RAG:{}", best.doc_id)),
        })
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_strategy_doc_score_default_weights() {
        let doc = StrategyDoc {
            doc_id: "test".to_string(),
            situation_tags: vec!["low_health".to_string()],
            tactic: "retreat".to_string(),
            weapon: "shotgun".to_string(),
            similarity: 0.9,
            confidence: 0.8,
            recency: 0.7,
        };
        // 0.4*0.9 + 0.4*0.8 + 0.2*0.7 = 0.36 + 0.32 + 0.14 = 0.82
        assert!((doc.score() - 0.82).abs() < 0.001);
    }

    #[test]
    fn test_strategy_doc_score_custom_weights() {
        let doc = StrategyDoc {
            doc_id: "test".to_string(),
            situation_tags: vec![],
            tactic: "attack".to_string(),
            weapon: "pistol".to_string(),
            similarity: 1.0,
            confidence: 0.5,
            recency: 0.0,
        };
        let weights = ScoringWeights {
            similarity: 0.6,
            confidence: 0.3,
            recency: 0.1,
        };
        // 0.6*1.0 + 0.3*0.5 + 0.1*0.0 = 0.6 + 0.15 + 0.0 = 0.75
        assert!((doc.score_with(&weights) - 0.75).abs() < 0.001);
    }

    #[test]
    fn test_disabled_client() {
        let client = RagClient::new(false, "http://localhost:9200".to_string());
        assert!(!client.is_enabled());
    }

    #[test]
    fn test_enabled_client() {
        let client = RagClient::new(true, "http://opensearch:9200".to_string());
        assert!(client.is_enabled());
        assert_eq!(client.opensearch_url(), "http://opensearch:9200");
    }

    #[test]
    fn test_derive_situation_tags_low_health() {
        let state = GameState {
            health: 20,
            ammo: 50,
            kills: 0,
            enemies_visible: 1,
            position_x: 0.0,
            position_y: 0.0,
            position_z: 0.0,
            angle: 0.0,
            episode_time: 0.0,
            is_dead: false,
            tick: 0,
        };
        let tags = derive_situation_tags(&state);
        assert!(tags.contains(&"low_health".to_string()));
        assert!(tags.contains(&"single_enemy".to_string()));
        assert!(tags.contains(&"ammo_abundant".to_string()));
    }

    #[test]
    fn test_derive_situation_tags_multi_enemy() {
        let state = GameState {
            health: 90,
            ammo: 5,
            kills: 0,
            enemies_visible: 4,
            position_x: 0.0,
            position_y: 0.0,
            position_z: 0.0,
            angle: 0.0,
            episode_time: 0.0,
            is_dead: false,
            tick: 0,
        };
        let tags = derive_situation_tags(&state);
        assert!(tags.contains(&"full_health".to_string()));
        assert!(tags.contains(&"low_ammo".to_string()));
        assert!(tags.contains(&"multi_enemy".to_string()));
    }

    #[test]
    fn test_derive_situation_tags_combined() {
        let state = GameState {
            health: 50,
            ammo: 30,
            kills: 0,
            enemies_visible: 0,
            position_x: 0.0,
            position_y: 0.0,
            position_z: 0.0,
            angle: 0.0,
            episode_time: 0.0,
            is_dead: false,
            tick: 0,
        };
        let tags = derive_situation_tags(&state);
        // Mid health, mid ammo, no enemies -> no tags
        assert!(tags.is_empty());
    }

    #[test]
    fn test_tactic_to_action_mapping() {
        assert_eq!(tactic_to_action("retreat_and_funnel"), Action::MoveLeft);
        assert_eq!(tactic_to_action("kite_backwards"), Action::MoveLeft);
        assert_eq!(tactic_to_action("flank_right"), Action::MoveRight);
        assert_eq!(tactic_to_action("aggressive_charge"), Action::Attack);
        assert_eq!(tactic_to_action("attack_visible_enemy"), Action::Attack);
        assert_eq!(tactic_to_action("hold_position"), Action::Attack);
    }
}
