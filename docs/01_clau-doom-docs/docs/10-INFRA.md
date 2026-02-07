# 10 — 인프라

← [09-PAPER](09-PAPER.md) · [인덱스](../DOOM_ARENA_CLAUDE.md) · 다음 → [11-TODO](11-TODO.md)

---

## 프로젝트 레포 구조

```
clau-doom/
├── cmd/                        # Go — CLI + 오케스트레이터
│   ├── clau-doom/              # CLI 진입점
│   └── orchestrator/           # 오케스트레이터 서버
├── agent-core/                 # Rust — 에이전트 의사결정
│   ├── src/
│   │   ├── strategy/           # 전략 엔진
│   │   ├── rag/                # RAG 클라이언트
│   │   └── game/               # VizDoom 상태 파싱
│   └── Cargo.toml
├── glue/                       # Python — VizDoom 글루만
│   ├── vizdoom_bridge.py
│   └── requirements.txt
├── dashboard/                  # TypeScript — Next.js
│   └── app/
│       ├── arena/              # 멀티 에이전트 관전
│       ├── player/[id]/        # 개별 에이전트 상세
│       ├── evolution/          # 세대별 진화 추이 + SPC + 학습 곡선
│       └── research/           # 연구 과정 시각화 + DOE + FMEA
├── infra/
│   ├── docker/
│   │   ├── doom-player/Dockerfile
│   │   ├── orchestrator/Dockerfile
│   │   └── dashboard/Dockerfile
│   └── docker-compose.yml
├── volumes/
│   ├── agents/                 # MD 파일
│   │   ├── templates/BASE_PLAYER.MD
│   │   └── active/DOOM_PLAYER_*.MD
│   ├── data/                   # DuckDB 파일 (에이전트별)
│   ├── research/               # Opus PI 연구 문서
│   │   ├── RESEARCH_LOG.MD
│   │   ├── HYPOTHESIS_BACKLOG.MD
│   │   ├── FINDINGS.MD
│   │   ├── DOE_CATALOG.MD
│   │   ├── SPC_STATUS.MD
│   │   ├── FMEA_REGISTRY.MD
│   │   ├── orders/
│   │   └── reports/
│   ├── opensearch/
│   ├── mongo/
│   └── nats/
├── proto/                      # gRPC 정의
│   ├── agent.proto
│   └── orchestrator.proto
├── scripts/
│   ├── setup.sh                # Linux/macOS
│   └── setup.ps1               # Windows
├── docs/                       # 설계 문서 (본 문서들)
│   ├── 00-ORIGIN.md
│   ├── 01-ARCHITECTURE.md
│   ├── 02-AGENT.md
│   ├── 03-EXPERIMENT.md
│   ├── 04-DOE.md
│   ├── 05-QUALITY.md
│   ├── 06-ANALYTICS.md
│   ├── 07-EVOLUTION.md
│   ├── 08-DASHBOARD.md
│   ├── 09-PAPER.md
│   ├── 10-INFRA.md
│   └── 11-TODO.md
├── CLAUDE.md                   # 프로젝트 컨텍스트 (인덱스)
├── Makefile
└── README.md
```

## 파일 경로 규칙

```
volumes/agents/active/DOOM_PLAYER_{SEQ}.MD  — 에이전트 정의
volumes/data/player-{SEQ}/game.duckdb       — 에이전트별 플레이 로그
volumes/research/RESEARCH_LOG.MD            — PI 연구 일지
volumes/research/DOE_CATALOG.MD             — DOE 설계 카탈로그
volumes/research/SPC_STATUS.MD              — SPC 관리도 현황
volumes/research/FMEA_REGISTRY.MD           — FMEA 실패 모드 등록부
volumes/research/orders/                    — 실험 지시서 (DOE 매트릭스 포함)
volumes/research/reports/                   — 실험 결과 리포트 (ANOVA 포함)
```

## CLI 도구 (Go)

```bash
$ clau-doom init          # 프로젝트 초기화
$ clau-doom spawn 5       # 에이전트 5개 생성
$ clau-doom watch 003     # Player 003 관전
$ clau-doom generation    # 현재 세대 상태
$ clau-doom evolve        # 다음 세대로 진화 트리거
$ clau-doom doe status    # 현재 DOE 실험 진행 상황
$ clau-doom spc           # SPC 관리도 요약
$ clau-doom fmea          # FMEA 상위 RPN 목록
```
