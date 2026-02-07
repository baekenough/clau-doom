# 01 — 아키텍처

← [00-ORIGIN](00-ORIGIN.md) · [인덱스](../DOOM_ARENA_CLAUDE.md) · 다음 → [02-AGENT](02-AGENT.md)

---

## 전체 구조

```
┌─ Opus 4.6 (PI, Cowork) ──────────────────────────┐
│  연구 설계 / 가설 수립 / 결과 분석 / 세대 진화 결정  │
│  DOE 매트릭스 설계 / SPC 이상 감지 / FMEA 우선순위  │
└──────────────┬────────────────────────────────────┘
               │ EXPERIMENT_ORDER.MD
               ▼
┌─ Claude Code (실행자, Sub-agents 병렬) ──────────┐
│  실험 실행 / MD 수정 / DuckDB 쿼리 / 컨테이너 제어  │
│  DOE 매트릭스의 조건별 병렬 배분 실행                │
└──────────────┬────────────────────────────────────┘
               │
    ┌──────────▼──────────────────────┐
    │        Docker Compose            │
    │                                  │
    │  ┌──────────┐  ┌──────────┐     │
    │  │Player_001│  │Player_002│ ... │
    │  │VizDoom   │  │VizDoom   │     │
    │  │Rust Agent│  │Rust Agent│     │
    │  │DuckDB    │  │DuckDB    │     │
    │  └────┬─────┘  └────┬─────┘     │
    │       │              │           │
    │  ┌────▼──────────────▼────┐      │
    │  │   NATS (pub/sub)       │      │
    │  └────────────────────────┘      │
    │                                  │
    │  ┌────────────┐ ┌────────────┐   │
    │  │ OpenSearch  │ │  MongoDB   │   │
    │  │ (RAG 검색)  │ │ (노하우)   │   │
    │  └────────────┘ └────────────┘   │
    │                                  │
    │  ┌────────────┐ ┌────────────┐   │
    │  │  Ollama    │ │ Dashboard  │   │
    │  │ (임베딩)    │ │ (Next.js)  │   │
    │  └────────────┘ └────────────┘   │
    └──────────────────────────────────┘
```

## 기술 스택

| 레이어 | 기술 | 역할 |
|--------|------|------|
| 게임 환경 | VizDoom + Xvfb + noVNC | Doom 엔진 + 실제 화면 스트리밍 |
| 에이전트 코어 | Rust | 의사결정 엔진, RAG 클라이언트, 스코어링 |
| 게임 글루 | Python | VizDoom API 바인딩만 |
| 오케스트레이터 | Go | 에이전트 생명주기, 세대 관리, CLI |
| 대시보드 | Next.js + WebSocket + noVNC | 실시간 관전, 연구 과정 시각화 |
| AI 추론 (연구) | Claude Code CLI (호스트) | 에피소드 회고, 세대 진화, 실험 분석 |
| AI 추론 (비동기 정제) | Ollama | 경량 임베딩, 간단한 문서 정제 |
| RAG 검색 | OpenSearch 컨테이너 | 전략 문서 kNN 벡터 검색 |
| 지식 저장 | MongoDB 컨테이너 | 노하우/전략 카탈로그 |
| 메시징 | NATS 컨테이너 | 에이전트 간 노하우 pub/sub |
| 로컬 DB | DuckDB (파일) | 에이전트별 플레이 로그 |
| 저장소 | 바인드 마운트 볼륨 | S3 대체, 로컬 파일 시스템 |
| 인프라 | Docker Compose | 전체 오케스트레이션 |

## 프로토콜

| 통신 경로 | 프로토콜 | 이유 |
|-----------|----------|------|
| 에이전트 ↔ 오케스트레이터 | gRPC | 양방향 스트리밍, 상태 보고 |
| 에이전트 ↔ 에이전트 | NATS pub/sub | 노하우 브로드캐스트 |
| 대시보드 ↔ 오케스트레이터 | WebSocket | 실시간 관전 |
| 분석 ↔ DuckDB | 로컬 파일 | 직접 접근 |

## 크로스플랫폼

### 핵심 원칙: OS 의존성을 컨테이너 안에 가둔다

호스트에 필요한 것은 Docker만. VizDoom, Xvfb 등 모든 OS 의존성은 컨테이너 내부에서 해결.

| | Ubuntu 24 | Windows 11 | macOS |
|---|---|---|---|
| Docker | native | WSL2 backend | Docker Desktop / OrbStack |
| VizDoom | 컨테이너 안 | 컨테이너 안 | 컨테이너 안 |
| noVNC 접속 | localhost:6901 | localhost:6901 | localhost:6901 |
| GPU (선택적) | nvidia-docker | WSL2 + CUDA | 없음 (CPU) |

### 크로스컴파일

- Rust 에이전트: 컨테이너용 linux 타겟 + 로컬 디버깅용 네이티브 타겟
- Go 오케스트레이터: GOOS/GOARCH로 3플랫폼 빌드
- 대시보드: 웹 기반이라 OS 무관

## 로컬 실행 환경

전체 AWS 의존성 없이 Docker Compose + 바인드 마운트 볼륨으로 로컬 실행:

| AWS 서비스 | 로컬 대체 |
|-----------|----------|
| S3 | 바인드 마운트 볼륨 |
| Bedrock Claude | Claude Code CLI (호스트) |
| Bedrock Nova/Titan | Ollama |
| OpenSearch Service | OpenSearch 컨테이너 |
| DocumentDB | MongoDB 컨테이너 |
| ECS Fargate | Docker Compose |
