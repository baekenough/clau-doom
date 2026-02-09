# clau-doom

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Rust](https://img.shields.io/badge/Rust-stable-orange.svg)](https://www.rust-lang.org/)
[![Go](https://img.shields.io/badge/Go-1.21+-00ADD8.svg)](https://golang.org/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB.svg)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://docs.docker.com/compose/)
[![Status](https://img.shields.io/badge/Status-Phase%202-green.svg)]()

> [English README](README.md)

LLM 오케스트레이션 기반 멀티에이전트 DOOM AI 연구 프로젝트.
RAG 경험 축적, 실험계획법(DOE) 최적화, 세대 진화를 통한 체계적 게임 AI 개선.

**핵심 원칙: 게임플레이 중 실시간 LLM 호출 없음.**

---

## 목차

- [개요](#개요)
- [아키텍처](#아키텍처)
- [의사결정 계층](#의사결정-계층)
- [연구 방법론](#연구-방법론)
- [연구 현황](#연구-현황)
- [빠른 시작](#빠른-시작)
- [프로젝트 구조](#프로젝트-구조)
- [기술 스택](#기술-스택)
- [컨테이너 스택](#컨테이너-스택)
- [주요 명령어](#주요-명령어)
- [연구 워크플로우](#연구-워크플로우)
- [발표 목표](#발표-목표)
- [기여하기](#기여하기)
- [인용](#인용)
- [라이선스](#라이선스)

---

## 개요

clau-doom은 LLM 오케스트레이션 멀티에이전트 시스템이 게임 AI를 **체계적으로** 최적화할 수 있는지 검증하는 연구 프로젝트다. 에이전트는 VizDoom 시나리오를 플레이하며, 의사결정은 다단계 캐스케이드로 처리한다.

기존 게임 AI 연구가 강화학습이나 ad-hoc 튜닝에 의존하는 것과 달리, 본 프로젝트는 산업 품질공학 방법론(DOE, SPC, FMEA)을 게임 AI 최적화에 적용한다. 모든 실험은 고정 시드셋으로 재현 가능하며, 통계적 증거 없이는 어떤 주장도 채택하지 않는다.

```
에이전트 역량 = OpenSearch 문서 품질 x Rust 스코어링 정확도
```

개선 경로:
1. **문서 품질** -- 에피소드 회고를 통한 전략 문서 정제
2. **스코어링 정확도** -- DOE 최적화를 통한 Rust 의사결정 가중치 조정

---

## 아키텍처

```
+------------------+     gRPC      +------------------+
|                  |<------------->|                   |
|   Orchestrator   |               |    Agent Core     |
|   (Go)           |               |    (Rust)         |
|                  |               |    < 100ms P99    |
+--------+---------+               +--------+----------+
         |                                  |
         |  lifecycle                       |  kNN query
         |  management                      |
         v                                  v
+------------------+               +------------------+
|                  |               |                   |
|   Game Glue      |               |   OpenSearch      |
|   (Python)       |               |   RAG Search      |
|   VizDoom API    |               |                   |
+--------+---------+               +------------------+
         |
         |  VizDoom
         |  frames
         v
+------------------+               +------------------+
|                  |               |                   |
|   VizDoom        |               |   Claude Code     |
|   + Xvfb + noVNC |               |   CLI (host)      |
|   (Docker)       |               |   episode 분석    |
|                  |               |   진화/실험 설계   |
+------------------+               +------------------+
         |
    +---------+---------+---------+
    |         |         |         |
    v         v         v         v
  DuckDB   MongoDB    NATS    Dashboard
  (로그)   (지식DB)  (메시징)  (Next.js)
```

| 계층 | 기술 | 역할 |
|------|------|------|
| Game Environment | VizDoom + Xvfb + noVNC | DOOM 엔진 + 화면 스트리밍 |
| Agent Core | Rust | 의사결정 엔진, RAG 클라이언트, 스코어링 |
| Game Glue | Python | VizDoom API 바인딩, DOE 실행 |
| Orchestrator | Go | 에이전트 생명주기, gRPC 서버, CLI |
| Dashboard | Next.js + WebSocket | 실시간 관전 (계획) |
| AI Reasoning | Claude Code CLI | 에피소드 회고, 진화, 실험 설계 |
| RAG Search | OpenSearch | 전략 문서 kNN 벡터 검색 |
| Knowledge Store | MongoDB | 노하우/전략 카탈로그 |
| Messaging | NATS | 에이전트 pub/sub 브로드캐스트 |
| Local DB | DuckDB | 실험별 플레이 로그 |
| Infra | Docker Compose | 전체 오케스트레이션 |

---

## 의사결정 계층

게임플레이 중에는 LLM을 호출하지 않는다. 모든 의사결정은 아래 4단계 캐스케이드로 처리한다.

```
Level 0: MD 하드코딩 규칙 (Rust, < 1ms)
  - 기본 반사 행동, 긴급 대응
  - 에이전트 바이너리에 직접 코딩

Level 1: DuckDB 로컬 캐시 (SQL, < 10ms)
  - 에이전트별 플레이 히스토리
  - 자주 사용하는 패턴

Level 2: OpenSearch kNN (벡터 검색, < 100ms)
  - 전략 문서 검색
  - 에이전트 간 노하우 검색

Level 3: Claude Code CLI (비동기, 초 단위)
  - 에피소드 회고 (게임 종료 후)
  - 세대 진화 (세대 간)
  - 실험 분석 (DOE 실행 완료 후)
```

**Level 3은 절대로 게임플레이 루프 안에서 실행하지 않는다.**

---

## 연구 방법론

### DOE (Design of Experiments) 기반 최적화

ad-hoc 파라미터 튜닝 대신, 산업 품질공학의 실험계획법을 적용한다.

| Phase | 설계 | 적용 시점 |
|-------|------|-----------|
| 0 | OFAT (한 번에 한 인자) | 초기 탐색, 인자 수 적을 때 |
| 1 | Factorial / Fractional | 복수 인자, 교호작용 탐색 |
| 2 | RSM-CCD (반응표면법) | 유의 인자 발견 후 미세 조정 |
| 3 | Split-Plot / Sequential | 복합 제약, 적응형 설계 |

### 통계적 엄격성

- 모든 실험은 **고정 시드셋**으로 재현 가능
- 유의성 주장에는 반드시 **ANOVA + 잔차 진단** 수행
- **효과 크기** (partial eta-squared, Cohen's d) 계산 필수
- 증거 마커 체계: `[STAT:p=0.003]`, `[STAT:ci=95%: 2.3-4.7]`

### 신뢰도 프레임워크

| 신뢰도 | 기준 | 조치 |
|--------|------|------|
| HIGH | p < 0.01, n >= 50/조건, 잔차 진단 통과 | 발견사항 채택 |
| MEDIUM | p < 0.05, n >= 30/조건, 잔차 대체로 양호 | 잠정 채택, 후속 실험 계획 |
| LOW | p < 0.10, n < 30, 잔차 위반 | 탐색적 결과만, 채택 불가 |
| UNTRUSTED | 통계 검정 없음, 일화적, p >= 0.10 | 기각 |

### 감사 추적 (Audit Trail)

모든 발견사항은 완전한 추적 경로를 가진다:

```
HYPOTHESIS_BACKLOG.md    가설 수립
        |
EXPERIMENT_ORDER_{ID}.md   실험 설계 (인자, 수준, 시드셋)
        |
EXPERIMENT_REPORT_{ID}.md  통계 분석 (ANOVA, 잔차 진단)
        |
FINDINGS.md              채택된 발견사항
```

### 품질공학 도구

- **SPC** (통계적 공정 관리): 세대별 성능 이상 탐지
- **FMEA** (고장 모드 영향 분석): 실험 우선순위 결정
- **TOPSIS** (다기준 의사결정): 트레이드오프 상황에서 최적 세대 선택

---

## 연구 현황

**20개 실험 완료 / 3,420 에피소드 수집 / 45개 연구 발견사항**

### Phase 1: 전략 지형 매핑 (완료)

| 실험 | 내용 | 결과 |
|------|------|------|
| DOE-001~004 | 인프라 검증 | KILLCOUNT 매핑 버그 발견, 데이터 무효 |
| DOE-005~006 | Memory/Strength 파라미터 효과 | 모의 데이터의 허위 신호, 효과 없음 |
| DOE-007 | 시나리오 비교 | defend_the_center는 아키텍처 구분 불가 (kills 0-3) |
| DOE-008 | 아키텍처 비교 | **최초 유의미 결과**: defend_the_line에서 p=0.000555 |
| DOE-009 | 개별 파라미터 변동 | Memory/Strength 파라미터 무효 확인 (p=0.736) |
| DOE-010 | 구조적 이동 패턴 | 3-action 공간에서 랜덤과 차이 없음 |
| DOE-011 | 확장 행동 공간 | 5-action 공간에서 효율-총량 트레이드오프 발생 |
| DOE-012~020 | 체계적 전략 탐색 | burst_3가 kills 최적(15.40), adaptive_kill이 kill rate 최적(46.18) |

### Phase 2: 다기준 최적화 (진행 중)

- TOPSIS 분석 완료: 다차원 성능 지표 종합 평가
- 정보이론 분석 완료: 전략 간 정보량 비교
- 세대 진화 설계 중: DOE-021~023

### 주요 발견사항

- **F-010**: L0-only 에이전트는 모든 다른 아키텍처보다 유의하게 낮은 성능
- **F-011**: Full agent(모든 레벨 활성)가 단일 휴리스틱 에이전트보다 낮은 성능 (간섭 효과)
- **F-012**: defend_the_line은 아키텍처를 효과적으로 구분, defend_the_center는 구분 불가
- 7개 발견사항은 모의 데이터 아티팩트로 무효화, 38개가 실제 데이터에서 채택

---

## 빠른 시작

### 사전 요구사항

| 도구 | 버전 | 용도 |
|------|------|------|
| Docker + Docker Compose | 최신 | 전체 스택 오케스트레이션 |
| Rust (stable) | 최신 | Agent Core 빌드 |
| Go | 1.21+ | Orchestrator 빌드 |
| Python | 3.11+ | VizDoom Glue |
| Node.js | 18+ | Dashboard (계획) |

### 설치 및 실행

```bash
# 저장소 클론
git clone https://github.com/baekenough/clau-doom.git
cd clau-doom

# Docker 이미지 빌드
make docker-build

# 전체 스택 시작
make docker-up

# noVNC로 게임 화면 확인
open http://localhost:6901

# 전체 스택 중지
make docker-down
```

### 개발 환경 빌드

```bash
# Rust Agent Core 빌드
make build

# 테스트 실행
make test

# Rust 벤치마크
make bench
```

---

## 프로젝트 구조

```
clau-doom/
├── agent-core/              # Rust 의사결정 엔진
│   ├── src/
│   │   ├── cache/           # 캐시 시스템
│   │   ├── cascade.rs       # 의사결정 캐스케이드
│   │   ├── game/            # 게임 상태 관리
│   │   ├── grpc/            # gRPC 서버
│   │   ├── rag/             # OpenSearch RAG 클라이언트
│   │   ├── strategy/        # 전략 로직
│   │   ├── lib.rs
│   │   └── main.rs
│   ├── Cargo.toml
│   └── Cargo.lock
├── cmd/                     # Go CLI 및 오케스트레이터
│   └── orchestrator/
├── glue/                    # Python VizDoom 글루
│   ├── vizdoom_bridge.py    # VizDoom API 래퍼
│   ├── doe_executor.py      # DOE 실행기
│   ├── episode_runner.py    # 에피소드 러너
│   └── requirements.txt
├── infra/                   # Docker 설정
│   ├── docker-compose.yml
│   └── doom-player/
├── research/                # 연구 문서
│   ├── experiments/         # 23개 실험 지시서, 16개 보고서
│   ├── analyses/            # TOPSIS, 정보이론 분석
│   ├── FINDINGS.md          # 45개 연구 발견사항
│   ├── HYPOTHESIS_BACKLOG.md
│   ├── RESEARCH_LOG.md
│   └── DOE_CATALOG.md
├── docs/                    # 문헌 리뷰, 설계 문서
│   ├── 01_clau-doom-docs/
│   ├── 02_literature/
│   └── 03_clau-doom-research/
├── guides/                  # 참조 문서 (18개 주제)
│   ├── rust/
│   ├── golang/
│   ├── python/
│   ├── doe/
│   ├── vizdoom/
│   └── ...
├── proto/                   # gRPC 프로토콜 정의
├── Makefile
└── README.md
```

---

## 기술 스택

### 언어 및 프레임워크

| 언어 | 역할 | 선택 이유 |
|------|------|-----------|
| Rust | Agent Core | < 100ms 의사결정 지연시간 보장 |
| Go | Orchestrator | gRPC 서버, 동시성 처리, CLI |
| Python | VizDoom Glue | VizDoom API 호환, DOE 실행 |
| TypeScript | Dashboard (계획) | Next.js 실시간 관전 |

### 인프라

| 서비스 | 이미지 | 역할 |
|--------|--------|------|
| OpenSearch | opensearchproject/opensearch:2.x | RAG 벡터 검색 |
| MongoDB | mongo:7.x | 지식 카탈로그 (계획) |
| NATS | nats:latest | 에이전트 메시징 |
| DuckDB | (임베디드) | 실험별 플레이 로그 |
| VizDoom | Custom | DOOM 엔진 + Xvfb + noVNC |

### AI/ML 도구

| 도구 | 용도 |
|------|------|
| Claude Code CLI | 에피소드 회고, 진화, 실험 설계 |
| 18개 서브에이전트 | 연구, 개발, 관리 전담 에이전트 |
| 32개 스킬 | 에이전트 역량 정의 |
| 20개 규칙 | 실험 무결성, 에이전트 설계, 워크플로우 규약 |

---

## 컨테이너 스택

```bash
# docker-compose.yml로 관리
make docker-up
```

| 컨테이너 | 포트 | 역할 |
|----------|------|------|
| doom-player | 6901 (noVNC) | VizDoom + Xvfb + noVNC |
| agent-core | 50052 (gRPC) | Rust 의사결정 엔진 |
| opensearch | 9200 | RAG 벡터 검색 |
| nats | 4222 | 에이전트 메시징 |

---

## 주요 명령어

```bash
# 빌드
make build              # 전체 빌드 (Rust + Go)
make docker-build       # Docker 이미지 빌드

# 테스트
make test               # 전체 테스트
make bench              # Rust 벤치마크

# Docker
make docker-up          # 스택 시작
make docker-down        # 스택 중지

# 연구 (Claude Code CLI 환경)
# 실험 설계: research-pi 에이전트가 DOE 설계
# 실험 실행: research-doe-runner 에이전트가 에피소드 실행
# 통계 분석: research-analyst 에이전트가 ANOVA 수행
# 진화 관리: research-evolution-mgr 에이전트가 세대 진화
```

---

## 연구 워크플로우

```
1. 가설 수립 (research-pi)
   H-042: Memory와 Strength가 kill efficiency에 교호작용이 있다
       |
2. DOE 설계 (research-pi)
   2x3 factorial, n=180 episodes, seed set 고정
       |
3. 병렬 실행 (research-doe-runner)
   16개 Run, 에이전트 컨테이너에 인자 주입 후 에피소드 실행
       |
4. 통계 분석 (research-analyst)
   ANOVA + 잔차 진단 + 효과 크기 + 검정력 분석
       |
5. 지식 축적 (research-rag-curator)
   전략 문서 생성, OpenSearch에 인덱싱
       |
6. 세대 진화 (research-evolution-mgr)
   Generation N의 결과로 Generation N+1 유전체 생성
       |
7. 결과 종합 및 발표 (research-paper-writer)
```

### DOE Phase 전환 기준

```
Phase 0 -> 1: 3개 이상 흥미로운 인자 식별
Phase 1 -> 2: 유의한 주효과 + 교호작용 발견
Phase 2 -> 3: 최적 영역 근접, 정밀 제어 필요
Phase 3 -> Meta: 복수 실험 간 교차 종합 필요
```

---

## 발표 목표

### 학회

| 우선순위 | 학회 |
|----------|------|
| 1순위 | NeurIPS (Conference on Neural Information Processing Systems) |
| 2순위 | ICML (International Conference on Machine Learning) |
| 대안 | AAAI, AAMAS |

### 기여 주장

1. **RAG 기반 에이전트 스킬 축적**: 실시간 LLM 호출 없이 경험 기반 의사결정
2. **DOE 기반 체계적 최적화**: ad-hoc 튜닝 대신 통계적 실험 설계
3. **품질공학 기반 세대 진화**: SPC/FMEA/TOPSIS를 통한 체계적 진화
4. **재현 가능한 멀티에이전트 프레임워크**: 고정 시드, 완전한 감사 추적

### 평가 기준

- ANOVA를 통한 개선의 통계적 유의성
- 여러 DOOM 시나리오에서의 일반화 능력
- 의사결정 지연시간 < 100ms (계산 효율성)
- 에이전트 간 지식 전이 효과

---

## 기여하기

기여를 환영합니다. 아래 절차를 따라 주세요.

### 브랜치 전략

```
main           안정 릴리스
develop        메인 개발 브랜치
feature/*      새 기능 -> develop PR
experiment/*   연구 실험 -> develop PR
docs/*         문서 업데이트 -> develop PR
```

### 커밋 컨벤션

```
type(scope): subject

Types:
  feat:     새 기능
  fix:      버그 수정
  docs:     문서
  exp:      실험 (새 DOE 실행, 분석)
  refactor: 리팩토링
  test:     테스트
  chore:    빌드/도구
```

### 기여 절차

1. 저장소를 Fork합니다.
2. Feature 브랜치를 생성합니다: `git checkout -b feature/my-feature`
3. 변경사항을 커밋합니다: `git commit -m "feat(scope): add my feature"`
4. 브랜치에 Push합니다: `git push origin feature/my-feature`
5. Pull Request를 생성합니다.

### 연구 기여 시 주의사항

- 모든 실험에는 고정 시드셋을 사용해 주세요
- 통계적 주장에는 반드시 증거 마커를 포함해 주세요
- 원본 데이터(data/raw/)는 절대 수정하지 마세요
- EXPERIMENT_ORDER -> EXPERIMENT_REPORT -> FINDINGS 감사 추적을 유지해 주세요

---

## 인용

이 프로젝트를 연구에 활용하실 경우, 아래 형식으로 인용해 주세요.

```bibtex
@misc{clau-doom2026,
  title     = {clau-doom: Systematic Game AI Optimization via
               LLM-Orchestrated Multi-Agent DOE and RAG},
  author    = {Yi, Sang},
  year      = {2026},
  publisher = {GitHub},
  url       = {https://github.com/baekenough/clau-doom}
}
```

---

## 라이선스

이 프로젝트는 [MIT 라이선스](LICENSE)를 따릅니다.

---

*이 프로젝트는 Claude Code CLI를 활용한 멀티에이전트 연구 오케스트레이션 프레임워크입니다. 18개 전문 서브에이전트가 실험 설계, 통계 분석, 코드 개발, 시스템 관리를 분담합니다.*
