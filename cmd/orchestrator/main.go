// Package main provides the orchestrator gRPC server.
//
// The orchestrator manages agent lifecycle, experiment execution,
// and generation evolution. It communicates with:
// - Rust agent-core via gRPC (GameTick stream)
// - Python VizDoom bridge via gRPC (game environment control)
// - DuckDB for experiment data recording
// - OpenSearch for strategy document management
package main

import (
	"fmt"
	"os"
)

func main() {
	fmt.Println("clau-doom orchestrator — not yet implemented")
	os.Exit(0)
}
