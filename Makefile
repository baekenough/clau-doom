.PHONY: build test proto-gen docker-build docker-up clean

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

# Clean build artifacts
clean:
	cd agent-core && cargo clean
	rm -f cmd/clau-doom/clau-doom cmd/orchestrator/orchestrator
	find glue -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	find glue -name '*.pyc' -delete 2>/dev/null || true
