//! agent-server: gRPC entry point for the DOOM agent decision engine.
//!
//! Parses configuration from environment variables, builds the
//! DecisionCascade, and starts a tonic gRPC server.

use std::env;
use std::net::SocketAddr;

use agent_core::cascade::{CascadeConfig, DecisionCascade};
use agent_core::grpc::proto::agent_service_server::AgentServiceServer;
use agent_core::grpc::AgentServer;

use tonic::transport::Server;
use tracing::info;

fn env_or(key: &str, default: &str) -> String {
    env::var(key).unwrap_or_else(|_| default.to_string())
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    tracing_subscriber::fmt::init();

    let opensearch_url = env_or("OPENSEARCH_URL", "http://opensearch:9200");
    let grpc_port: u16 = env_or("GRPC_PORT", "50051").parse()?;
    let cascade_mode = env_or("CASCADE_MODE", "full_agent");
    let seed: u64 = env_or("SEED", "42").parse()?;
    let health_threshold: f32 = env_or("HEALTH_THRESHOLD", "0.3").parse()?;
    let duckdb_path = env_or("DUCKDB_PATH", "/app/data/agent_cache.duckdb");

    let config = match cascade_mode.as_str() {
        "random" => CascadeConfig::random(),
        "rule_only" => CascadeConfig::rule_only(),
        _ => CascadeConfig::full_agent(),
    };

    let cascade = DecisionCascade::new(
        config.clone(),
        health_threshold,
        opensearch_url.clone(),
        seed,
        &duckdb_path,
    );

    let agent_server = AgentServer::new(
        cascade,
        config,
        health_threshold,
        opensearch_url,
        seed,
    );

    let addr: SocketAddr = format!("0.0.0.0:{grpc_port}").parse()?;
    info!(%addr, %cascade_mode, seed, health_threshold, "starting agent-server");

    Server::builder()
        .add_service(AgentServiceServer::new(agent_server))
        .serve(addr)
        .await?;

    Ok(())
}
