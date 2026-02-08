#!/usr/bin/env bash
# setup.sh -- verify dependencies and create runtime directories for clau-doom.
set -euo pipefail

echo "=== clau-doom setup ==="

# Check required tools
missing=()
command -v rustc   >/dev/null 2>&1 || missing+=("rustc (Rust compiler)")
command -v cargo   >/dev/null 2>&1 || missing+=("cargo (Rust package manager)")
command -v go      >/dev/null 2>&1 || missing+=("go (Go compiler)")
command -v python3 >/dev/null 2>&1 || missing+=("python3")
command -v docker  >/dev/null 2>&1 || missing+=("docker")
command -v protoc  >/dev/null 2>&1 || missing+=("protoc (protobuf compiler)")

if [ ${#missing[@]} -gt 0 ]; then
    echo ""
    echo "Missing dependencies:"
    for dep in "${missing[@]}"; do
        echo "  - $dep"
    done
    echo ""
    echo "Install missing dependencies before continuing."
    exit 1
fi

echo "All required tools found."

# Create runtime directories (not tracked by git)
echo "Creating runtime directories..."
mkdir -p volumes/agents/templates
mkdir -p volumes/agents/active
mkdir -p volumes/data
mkdir -p volumes/opensearch
mkdir -p volumes/mongo
mkdir -p volumes/nats
mkdir -p scripts/benchmarks/results

# Create research symlink if it doesn't exist
if [ ! -e volumes/research ]; then
    ln -s ../../research volumes/research
    echo "Created symlink: volumes/research -> ../../research"
fi

echo ""
echo "Setup complete. Next steps:"
echo "  make build       -- build all components"
echo "  make test        -- run all tests"
echo "  make docker-up   -- start docker compose stack"
