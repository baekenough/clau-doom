# clau-doom — 프로젝트 지식 파일 (CLAUDE.md)

## 프로젝트 한 줄 요약
LLM 기반 멀티 에이전트가 Doom을 플레이하며 RAG로 경험을 축적하고, 산업공학 DOE와 품질공학으로 체계적 최적화를 수행하며, 세대 진화를 통해 집단적으로 강해지는 실험 프로젝트. 밈에서 출발, 논문으로 착지.

## 문서 인덱스

| # | 문서 | 내용 | 경로 |
|---|------|------|------|
| 0 | 기원과 개요 | 프로젝트 기원, 핵심 컨셉, 설계 결정 | [docs/00-ORIGIN.md](docs/00-ORIGIN.md) |
| 1 | 아키텍처 | 전체 구조, 기술 스택, 프로토콜, 크로스플랫폼 | [docs/01-ARCHITECTURE.md](docs/01-ARCHITECTURE.md) |
| 2 | 에이전트 | 에이전트 정의(MD DNA), 의사결정 계층, RAG 파이프라인 | [docs/02-AGENT.md](docs/02-AGENT.md) |
| 3 | 실험 구조 | 실험 사이클, 실행 정책, 측정 체계, PI 구조 | [docs/03-EXPERIMENT.md](docs/03-EXPERIMENT.md) |
| 4 | DOE 프레임워크 | 실험계획법 단계별 도입, 요인배치/타구치/RSM/분할구/순차적 설계 | [docs/04-DOE.md](docs/04-DOE.md) |
| 5 | 품질공학 | SPC, Cp/Cpk, FMEA, TOPSIS/AHP | [docs/05-QUALITY.md](docs/05-QUALITY.md) |
| 6 | 데이터 분석 | PCA, 회귀 모델링, 학습 곡선, 시뮬레이션 최적화 | [docs/06-ANALYTICS.md](docs/06-ANALYTICS.md) |
| 7 | 진화 메커니즘 | 세대 진화 흐름, 부모 선택, 교차/변이/엘리트 | [docs/07-EVOLUTION.md](docs/07-EVOLUTION.md) |
| 8 | 대시보드 | 탭 구성, 시각화 요소, noVNC 스트리밍 | [docs/08-DASHBOARD.md](docs/08-DASHBOARD.md) |
| 9 | 논문 구조 | 타겟 학회, 기여점, RQ, Ablation, 관련 연구 | [docs/09-PAPER.md](docs/09-PAPER.md) |
| 10 | 인프라 | 레포 구조, 파일 경로, 로컬 실행 환경, CLI | [docs/10-INFRA.md](docs/10-INFRA.md) |
| 11 | 미결 사항 | 탐색 필요 항목, 의사결정 대기 목록 | [docs/11-TODO.md](docs/11-TODO.md) |

## 빠른 참조

### 핵심 설계 결정
- 실시간 판단에 LLM 호출 없음 → RAG + Rust 룰엔진 (< 100ms)
- LLM = 코치 (비동기만)
- Rust(에이전트) + Go(오케스트레이터) + Python(글루만)
- 로컬 전용, Docker Compose
- DOE 단계적 도입: OFAT → 요인배치 → 타구치 → RSM
- 품질공학 기반 진화: SPC + Cpk + FMEA + TOPSIS

### 의사결정 계층
```
Level 0: MD 하드코딩 규칙 (Rust, < 1ms)
Level 1: DuckDB 로컬 캐시 (SQL, < 10ms)
Level 2: OpenSearch kNN (벡터 검색, < 100ms)
Level 3: Claude Code CLI (비동기, 수초)
```

### 에이전트 실력 공식
에이전트 실력 = OpenSearch 문서 품질 × Rust 스코어링 정확도
