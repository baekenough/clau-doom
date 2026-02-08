//! Level 2 RAG client: OpenSearch kNN vector search.
//!
//! Target latency: < 100ms P99.

use crate::game::{Decision, GameState};

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

/// RAG client configuration.
pub struct RagClient {
    enabled: bool,
    opensearch_url: String,
    _index_name: String,
    _k: usize,
    _weights: ScoringWeights,
}

impl RagClient {
    pub fn new(enabled: bool, opensearch_url: String) -> Self {
        Self {
            enabled,
            opensearch_url,
            _index_name: "strategies".to_string(),
            _k: 5,
            _weights: ScoringWeights::default(),
        }
    }

    pub fn is_enabled(&self) -> bool {
        self.enabled
    }

    pub fn opensearch_url(&self) -> &str {
        &self.opensearch_url
    }

    /// Query OpenSearch for similar strategies. Returns None if disabled.
    /// TODO: Implement actual kNN query in Phase 3.
    pub async fn query(&self, _state: &GameState) -> Option<Decision> {
        if !self.enabled {
            return None;
        }
        // Placeholder - will be implemented with actual HTTP client
        None
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
}
