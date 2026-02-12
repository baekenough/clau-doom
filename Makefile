.PHONY: build test test-python proto-gen docker-build docker-up docker-down bench clean verify doe

# Build all components
build:
	cd agent-core && cargo build
	go build ./cmd/clau-doom/...
	go build ./cmd/orchestrator/...

# Run all tests
test:
	cd agent-core && cargo test
	go test ./...
	cd glue && python3 -m pytest tests/ -v

# Generate code from proto definitions
proto-gen:
	protoc --go_out=. --go-grpc_out=. proto/agent.proto proto/orchestrator.proto
	python3 -m grpc_tools.protoc -Iproto --python_out=glue --grpc_python_out=glue proto/agent.proto proto/orchestrator.proto
	cd agent-core && cargo build --features proto-gen 2>/dev/null || true

# Build docker images
docker-build:
	docker compose -f infra/docker-compose.yml build

# Start docker compose stack
docker-up:
	docker compose -f infra/docker-compose.yml up -d

# Stop docker compose stack
docker-down:
	docker compose -f infra/docker-compose.yml down

# Run Rust benchmarks (decision cascade latency)
bench:
	cd agent-core && cargo bench

# Run Python tests only (no Rust/Go needed)
test-python:
	python3 -m pytest glue/tests/ -v --ignore=glue/tests/test_integration.py --ignore=glue/tests/test_grpc_integration.py

# Verify research findings from CSV data (no VizDoom/DuckDB needed)
verify:
	python3 scripts/verify_reproducibility.py

# Run a specific DOE experiment (requires Docker stack)
# Usage: make doe DOE=DOE-020
doe:
	python3 -m glue.doe_executor --experiment $(DOE)

# Clean build artifacts
clean:
	cd agent-core && cargo clean
	rm -f cmd/clau-doom/clau-doom cmd/orchestrator/orchestrator
	find glue -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	find glue -name '*.pyc' -delete 2>/dev/null || true
