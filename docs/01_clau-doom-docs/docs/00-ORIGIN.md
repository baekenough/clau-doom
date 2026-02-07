# 00 — 기원과 개요

← [인덱스](../DOOM_ARENA_CLAUDE.md) · 다음 → [01-ARCHITECTURE](01-ARCHITECTURE.md)

---

## 프로젝트 기원

"Can it run DOOM?"은 컴퓨팅 역사에서 반복되는 밈이다. 계산기, ATM, 임신 테스트기에서 DOOM을 돌리는 건 하드웨어 능력의 과시였고, GPT-4로 DOOM을 돌리는 건(de Wynter, IEEE 2024) LLM 능력의 과시였다.

clau-doom은 "Claude Code, GPT Codex 같은 LLM CLI 코딩 에이전트에서 DOOM을 돌릴 수 있을까?"라는 밈적 호기심에서 출발했다. 그런데 이를 진지하게 수행하려면 실시간 제약 속 의사결정, 경험 축적과 전이, 체계적 실험 설계라는 실제 연구 문제들을 풀어야 했고, 그 과정에서 RAG 기반 행동 개선, 산업공학 DOE 적용, LLM-as-PI 프레임워크라는 고유한 연구 방향이 형성되었다.

밈에서 출발했지만 연구로 착지한 이 경로 자체가 프로젝트의 정체성이다.

## 핵심 컨셉

- 각 서브 에이전트(DOOM_PLAYER_{SEQ}.MD)가 독립적으로 Doom을 플레이
- 에이전트마다 개별 DuckDB에 경험을 축적
- 주기적으로 노하우를 공개(publish)하여 집단 지식 형성
- 세대 진화를 통해 전략의 자연선택
- Opus 4.6(Cowork)가 PI로서 실험을 설계/제어, Claude Code가 실행
- 산업공학 DOE 기법으로 다변수 동시 최적화 및 교호작용 분석

## 핵심 설계 결정

### 확정된 사항

- **실시간 판단에 LLM 호출 없음** — RAG(OpenSearch kNN) + Rust 룰엔진으로 100ms 이내 처리
- **LLM = 코치** — 비동기 정제, 에피소드 회고, 세대 진화에만 사용
- **Python은 글루만** — VizDoom 바인딩 전용. 핵심 로직은 Rust(에이전트) + Go(오케스트레이터)
- **로컬 전용** — AWS 의존성 없음. Docker Compose + 바인드 마운트
- **크로스플랫폼** — OS 의존성을 컨테이너에 격리. Ubuntu 24, Windows 11, macOS 지원
- **Cowork(연구) + Claude Code(실행) 이분화** — MD 파일로 비동기 소통
- **Nova/Titan 제거** — Bedrock 의존성 없음. 로컬은 Claude Code + Ollama
- **산업공학 DOE 통합** — OFAT에서 요인배치/타구치/RSM으로 단계적 전환
- **품질공학 기반 진화** — SPC 관리도, Cpk, FMEA, TOPSIS로 다기준 평가

### 에이전트 실력 공식

에이전트 실력 = OpenSearch 문서 품질 × Rust 스코어링 정확도. LLM이 더 좋은 전략 문서를 만들수록 실시간 RAG 검색 결과가 개선되는 피드백 루프.
