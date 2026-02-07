---
name: dev-lead-routing
description: Routes development tasks to language/framework expert agents
user-invocable: false
---

# Dev Lead Routing Skill

## Purpose

Routes development tasks to appropriate language and framework expert agents. This skill contains the coordination logic for orchestrating sw-engineer agents across language, infrastructure, and architecture specializations.

## Engineers Under Management

| Type | Agents | Purpose |
|------|--------|---------|
| sw-engineer/language | lang-rust-expert, lang-golang-expert, lang-python-expert, lang-typescript-expert | Language expertise |
| sw-engineer/infra | infra-docker-expert, infra-grpc-expert | Infrastructure and communication |
| sw-architect | arch-documenter | Architecture documentation |

## Language/Framework Detection

### File Extension Mapping

| Extension | Agent | Language/Framework |
|-----------|-------|-------------------|
| `.rs` | lang-rust-expert | Rust |
| `.go` | lang-golang-expert | Go |
| `.py` | lang-python-expert | Python |
| `.ts`, `.tsx` | lang-typescript-expert | TypeScript |
| `Dockerfile`, `docker-compose.yml` | infra-docker-expert | Docker |
| `.proto` | infra-grpc-expert | gRPC/Protocol Buffers |

### Keyword Mapping

| Keyword | Agent |
|---------|-------|
| "rust", "cargo", "crate" | lang-rust-expert |
| "go", "golang" | lang-golang-expert |
| "python", "py", "pip" | lang-python-expert |
| "typescript", "ts", "react", "next.js", "node" | lang-typescript-expert |
| "docker", "compose", "container", "dockerfile" | infra-docker-expert |
| "grpc", "proto", "protobuf", "nats", "messaging" | infra-grpc-expert |
| "architecture", "ADR", "design doc", "API spec" | arch-documenter |

## Command Routing

```
Development Request -> Detection -> Expert Agent

Rust code       -> lang-rust-expert
Go code         -> lang-golang-expert
Python code     -> lang-python-expert
TypeScript code -> lang-typescript-expert
Docker/compose  -> infra-docker-expert
gRPC/NATS       -> infra-grpc-expert
Architecture    -> arch-documenter
Multi-lang      -> Multiple experts (parallel)
```

## Routing Rules

### 1. Code Review Workflow

```
1. Receive review request
2. Identify file types and languages:
   - Use Glob to find files
   - Parse file extensions
   - Detect framework (Cargo.toml, go.mod, pyproject.toml, package.json)
3. Select appropriate experts
4. Distribute files to experts (parallel if 2+ languages)
5. Aggregate review findings
6. Present unified report
```

Example:
```
User: "Review src/agent/*.rs src/orchestrator/*.go"

Detection:
  - src/agent/*.rs -> lang-rust-expert
  - src/orchestrator/*.go -> lang-golang-expert

Route (parallel):
  Task(lang-rust-expert role -> review src/agent/*.rs, model: "sonnet")
  Task(lang-golang-expert role -> review src/orchestrator/*.go, model: "sonnet")

Aggregate:
  Rust: 3 issues found
  Go: Clean
```

### 2. Feature Implementation Workflow

```
1. Analyze feature requirements
2. Identify affected components:
   - Rust agent core -> lang-rust-expert
   - Go orchestrator -> lang-golang-expert
   - Python VizDoom glue -> lang-python-expert
   - Dashboard frontend -> lang-typescript-expert
   - Docker infra -> infra-docker-expert
3. Select required experts
4. Coordinate implementation (sequential if dependent, parallel if independent)
5. Ensure consistency across languages
6. Report completion status
```

### 3. Multi-Language Projects

For tasks spanning multiple languages:

```
1. Detect all languages affected
2. Identify primary language (most files/core logic)
3. Route to appropriate experts:
   - If task spans multiple languages -> parallel experts
   - If task is language-specific -> single expert
4. Coordinate cross-language consistency (API contracts, protobuf schemas)
```

## Sub-agent Model Selection

### Model Mapping by Task Type

| Task Type | Recommended Model | Reason |
|-----------|-------------------|--------|
| Architecture analysis | `opus` | Deep reasoning required |
| Code review | `sonnet` | Balanced quality judgment |
| Code implementation | `sonnet` | Standard code generation |
| Refactoring | `sonnet` | Balanced transformation |
| Quick validation | `haiku` | Fast response |
| File search | `haiku` | Simple operation |

### Model Mapping by Agent

| Agent | Default Model | Alternative |
|-------|---------------|-------------|
| lang-rust-expert | `sonnet` | `opus` for unsafe/lifetime analysis |
| lang-golang-expert | `sonnet` | `opus` for concurrency design |
| lang-python-expert | `sonnet` | `haiku` for simple scripts |
| lang-typescript-expert | `sonnet` | `haiku` for quick checks |
| infra-docker-expert | `sonnet` | `haiku` for Dockerfile review |
| infra-grpc-expert | `sonnet` | `opus` for schema design |
| arch-documenter | `sonnet` | `opus` for ADR decisions |

### Task Call Examples

```
# Complex Rust lifetime analysis
Task(
  subagent_type: "general-purpose",
  prompt: "Analyze lifetime issues in src/agent/decision.rs following lang-rust-expert guidelines",
  model: "opus"
)

# Standard Go code review
Task(
  subagent_type: "general-purpose",
  prompt: "Review Go code in src/orchestrator/ following lang-golang-expert guidelines",
  model: "sonnet"
)

# Quick file search
Task(
  subagent_type: "Explore",
  prompt: "Find all files importing the scoring module",
  model: "haiku"
)
```

## Parallel Execution

Following R009:
- Maximum 4 parallel instances
- Only worker agents (sw-engineer/*)
- Independent file/module reviews
- Coordinate cross-expert consistency

Example:
```
User: "Review all source code"

Detection:
  - src/agent/*.rs -> lang-rust-expert
  - src/orchestrator/*.go -> lang-golang-expert
  - src/glue/*.py -> lang-python-expert
  - src/dashboard/*.ts -> lang-typescript-expert

Route (parallel, max 4):
  Task(lang-rust-expert role -> review src/agent/, model: "sonnet")
  Task(lang-golang-expert role -> review src/orchestrator/, model: "sonnet")
  Task(lang-python-expert role -> review src/glue/, model: "sonnet")
  Task(lang-typescript-expert role -> review src/dashboard/, model: "sonnet")
```

## Display Format

```
[Analyzing] Detected: Rust, Go
[Routing] lang-rust-expert:sonnet -> 12 Rust files
[Routing] lang-golang-expert:sonnet -> 8 Go files

[Delegating] lang-rust-expert:sonnet -> src/agent/
[Delegating] lang-golang-expert:sonnet -> src/orchestrator/

[Progress] 1/2 experts completed

[Summary]
  Rust: 3 issues found
  Go: Clean

Review completed.
```

## Integration with Other Agents

- Receives architecture specs from arch-documenter
- Coordinates with infra-docker-expert for containerization
- Coordinates with infra-grpc-expert for service communication

## Usage

This skill is NOT user-invocable. It should be automatically triggered when the main conversation detects development intent.

Detection criteria:
- User requests code review
- User mentions language/framework name
- User provides file paths for review
- User requests refactoring/implementation
- User references build/deploy operations
