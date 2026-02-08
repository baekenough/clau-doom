//! agent-core: Rust decision engine for DOOM arena agents.
//!
//! Handles real-time decision-making through a multi-level cascade:
//! - Level 0: Hardcoded MD rules (< 1ms)
//! - Level 1: DuckDB local cache lookup (< 10ms)
//! - Level 2: OpenSearch kNN vector search (< 100ms)
//!
//! No LLM calls occur during gameplay. All reasoning is offline.

pub mod cache;
pub mod cascade;
pub mod game;
pub mod grpc;
pub mod rag;
pub mod strategy;
